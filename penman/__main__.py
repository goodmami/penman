# -*- coding: utf-8 -*-

import sys
import os
import argparse
import json
import logging

from penman.__about__ import __version__
from penman.model import Model
from penman import layout
from penman.codec import PENMANCodec
from penman import transform


# Names of functions allowed for ordering triples/branches; we cannot
# resolve them to the actual functions until the model is loaded.  If
# the value of the key is not a method of the model, the value is
# passed as a keyword argument with the value `True`.
REARRANGE_KEYS = {
    'random': 'random_order',
    'canonical': 'canonical_order',
    'alphanumeric': 'alphanumeric_order',
    'inverted-last': 'is_role_inverted',
    'attributes-first': 'attributes_first',
}
RECONFIGURE_KEYS = {
    'original': 'original_order',
    'random': 'random_order',
    'canonical': 'canonical_order',
}


def process(f,
            model,
            out,
            err,
            check,
            normalize_options,
            format_options,
            triples):
    """Read graphs from *f* and write to *out*."""

    exitcode = 0
    codec = PENMANCodec(model=model)
    trees = codec.iterparse(f)

    first = True
    for t in trees:
        if first:
            first = False
        else:
            print(file=out)

        g = _process_in(t, model, normalize_options)
        if check:
            exitcode |= _check(g, model)
        if triples:
            s = codec.format_triples(
                g.triples,
                indent=bool(format_options.get('indent', True)))
        else:
            t = _process_out(g, model, normalize_options)
            s = codec.format(t, **format_options)

        print(s, file=out)

    return exitcode


def _process_in(t, model, normalize_options):
    """Encode tree *t* and return the string."""
    # tree transformations
    if normalize_options['canonicalize_roles']:
        t = transform.canonicalize_roles(t, model)

    g = layout.interpret(t, model)

    # graph transformations
    if normalize_options['reify_edges']:
        g = transform.reify_edges(g, model)
    if normalize_options['dereify_edges']:
        g = transform.dereify_edges(g, model)
    if normalize_options['reify_attributes']:
        g = transform.reify_attributes(g)
    if normalize_options['indicate_branches']:
        g = transform.indicate_branches(g, model)

    return g


def _process_out(g, model, normalize_options):
    if normalize_options['reconfigure']:
        key, kwargs = normalize_options['reconfigure']
        t = layout.reconfigure(g, key=key, **kwargs)
        g = layout.interpret(t, model)
    else:
        t = layout.configure(g, model=model)
    if normalize_options['rearrange']:
        key, kwargs = normalize_options['rearrange']
        layout.rearrange(t, key=key, **kwargs)
    if normalize_options['make_variables']:
        t.reset_variables(normalize_options['make_variables'])

    return t


def _check(g, model):
    i = 1
    errors = model.errors(g)
    if errors:
        for triple, errors in errors.items():
            if triple:
                context = '({}) '.format(' '.join(map(str, triple)))
            else:
                context = ''
            for error in errors:
                g.metadata[f'error-{i}'] = context + error
            i += 1
        return 1
    else:
        return 0


def _order_funcs(KEY_FUNCS):

    def split_arg(arg):
        values = arg.split(',')
        for value in values:
            if value not in KEY_FUNCS:
                raise argparse.ArgumentTypeError(
                    'invalid choice: {!r} (choose from {})'
                    .format(value, ', '.join(map(repr, KEY_FUNCS))))
        return values

    return split_arg


def _make_sort_key(keys, model, KEY_FUNCS):
    kwargs = {}
    funcs = []
    for key in keys:
        name = KEY_FUNCS[key]
        func = getattr(model, name, None)
        if func is None:
            kwargs[name] = True
        else:
            funcs.append(func)

    def sort_key(role, funcs=funcs):
        return [func(role) for func in funcs]

    return sort_key, kwargs


def main():
    parser = argparse.ArgumentParser(
        prog='penman',
        description='Read and write graphs in the PENMAN notation.',
    )
    parser.add_argument(
        '-V', '--version', action='version',
        version='Penman v{}'.format(__version__))
    parser.add_argument(
        '-v', '--verbose', action='count', dest='verbosity', default=0,
        help='increase verbosity')
    parser.add_argument(
        '-q', '--quiet', action='store_true',
        help='suppress output on <stdout> and <stderr>')
    parser.add_argument(
        'FILE', nargs='*',
        help='read graphs from FILEs instead of stdin')
    model_group = parser.add_mutually_exclusive_group()
    model_group.add_argument(
        '--model', metavar='FILE',
        type=argparse.FileType('r'),
        help='JSON model file describing the semantic model')
    model_group.add_argument(
        '--amr', action='store_true',
        help='use the AMR model')
    model_group.add_argument(
        '--noop', action='store_true',
        help='use the no-op model')
    parser.add_argument(
        '--check', action='store_true',
        help='check graphs for compliance with the model')
    form = parser.add_argument_group('formatting options')
    form.add_argument(
        '--indent', metavar='N',
        help='indent N spaces per level ("no" for no newlines)')
    form.add_argument(
        '--compact', action='store_true',
        help='compactly print node attributes on one line')
    form.add_argument(
        '--triples', action='store_true',
        help='print graphs as triple conjunctions')
    norm = parser.add_argument_group('normalization options')
    norm.add_argument(
        '--make-variables', metavar='FMT',
        help="recreate node variables with FMT (e.g.: '{prefix}{j}')")
    norm.add_argument(
        '--rearrange', metavar='KEY',
        type=_order_funcs(REARRANGE_KEYS),
        help='reorder the branches of the tree')
    norm.add_argument(
        '--reconfigure', metavar='KEY',
        type=_order_funcs(RECONFIGURE_KEYS),
        help='reconfigure the graph layout with reordered triples')
    norm.add_argument(
        '--canonicalize-roles', action='store_true',
        help='canonicalize role forms')
    norm.add_argument(
        '--reify-edges', action='store_true',
        help='reify all eligible edges')
    norm.add_argument(
        '--dereify-edges', action='store_true',
        help='dereify all eligible edges')
    norm.add_argument(
        '--reify-attributes', action='store_true',
        help='reify all attributes')
    norm.add_argument(
        '--indicate-branches', action='store_true',
        help='insert triples to indicate tree structure')

    args = parser.parse_args()

    if args.quiet:
        args.verbosity = 0
        sys.stdout.close()
        sys.stdout = open(os.devnull, 'w')
    else:
        args.verbosity = min(args.verbosity, 3)

    logging.basicConfig()
    logger = logging.getLogger('penman')
    logger.setLevel(logging.ERROR - (args.verbosity * 10))

    model = _get_model(args.amr, args.noop, args.model)

    if args.rearrange:
        args.rearrange = _make_sort_key(
            args.rearrange, model, REARRANGE_KEYS)

    if args.reconfigure:
        args.reconfigure = _make_sort_key(
            args.reconfigure, model, RECONFIGURE_KEYS)

    indent = _indent(args.indent)

    normalize_options = {
        'make_variables': args.make_variables,
        'rearrange': args.rearrange,
        'reconfigure': args.reconfigure,
        'canonicalize_roles': args.canonicalize_roles,
        'reify_edges': args.reify_edges,
        'dereify_edges': args.dereify_edges,
        'reify_attributes': args.reify_attributes,
        'indicate_branches': args.indicate_branches,
    }
    format_options = {
        'indent': indent,
        'compact': args.compact,
    }

    if args.FILE:
        for file in args.FILE:
            with open(file) as f:
                exitcode = process(
                    f, model, sys.stdout, sys.stderr, args.check,
                    normalize_options, format_options, args.triples)
    else:
        exitcode = process(
            sys.stdin, model, sys.stdout, sys.stderr, args.check,
            normalize_options, format_options, args.triples)

    sys.exit(exitcode)


def _get_model(amr, noop, model_file):
    if amr:
        from penman.models.amr import model
    elif noop:
        from penman.models.noop import model
    elif model_file:
        model = Model(**json.load(model_file))
    else:
        model = Model()
    return model


def _indent(indent):
    if indent:
        if indent.lower() in ("no", "none", "false"):
            indent = None
        else:
            try:
                indent = int(indent)
                if indent < -1:
                    raise ValueError
            except ValueError:
                sys.exit('error: --indent value must be "no" or an '
                         'integer >= -1')
    else:
        indent = -1
    return indent


if __name__ == '__main__':
    main()
