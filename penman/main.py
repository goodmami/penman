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


def process(f, model, out, normalize_options, format_options, triples):
    """Read graphs from *f* and write to *out*."""

    def _process(t):
        """Encode tree *t* and return the string."""
        # tree transformations
        if normalize_options['make_variables']:
            t.reset_variables(normalize_options['make_variables'])
        if normalize_options['canonicalize_roles']:
            t = transform.canonicalize_roles(t, model)
        if normalize_options['rearrange'] == 'canonical':
            layout.rearrange(t, key=model.canonical_order)
        elif normalize_options['rearrange'] == 'random':
            layout.rearrange(t, key=model.random_order)

        g = layout.interpret(t, model)

        # reconfiguration (by round-tripping; a bit inefficient, but
        # oh well)
        if normalize_options['reconfigure']:
            key = model.original_order
            if normalize_options['reconfigure'] == 'canonical':
                key = model.canonical_order
            elif normalize_options['reconfigure'] == 'random':
                key = model.random_order
            t = layout.reconfigure(g, key=key)
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

        if triples:
            return codec.format_triples(
                g.triples,
                indent=bool(format_options.get('indent', True)))
        else:
            return codec.encode(g, **format_options)

    codec = PENMANCodec(model=model)
    trees = codec.iterparse(f)

    # the try... block is to do an incremental '\n\n'.join(graphs)
    try:
        t = next(trees)
        print(_process(t), file=out)
    except StopIteration:
        return
    for t in trees:
        print(file=out)
        print(_process(t), file=out)


def main():
    parser = argparse.ArgumentParser(
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
        '--rearrange', metavar='KEY', choices=('random', 'canonical'),
        help='reorder the branches of the tree')
    norm.add_argument(
        '--reconfigure', metavar='KEY',
        choices=('original', 'random', 'canonical'),
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

    logger = logging.getLogger('penman')
    logger.setLevel(logging.ERROR - (args.verbosity * 10))

    if args.amr:
        from penman.models.amr import model
    elif args.model:
        model = Model(**json.load(args.model))
    else:
        model = Model()

    indent = -1
    if args.indent:
        if args.indent.lower() in ("no", "none", "false"):
            indent = None
        else:
            try:
                indent = int(args.indent)
                if indent < -1:
                    raise ValueError
            except ValueError:
                sys.exit('error: --indent value must be "no" or an '
                         'integer >= -1')

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
                process(f, model, sys.stdout,
                        normalize_options, format_options, args.triples)
    else:
        process(sys.stdin, model, sys.stdout,
                normalize_options, format_options, args.triples)


if __name__ == '__main__':
    main()
