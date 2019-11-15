# -*- coding: utf-8 -*-

import sys
import argparse
import json

from penman.__about__ import __version__
from penman.model import Model
from penman import layout
from penman.codec import PENMANCodec
from penman import transform


def process(f, model, out, transform_options, format_options):
    """Read graphs from *f* and write to *out*."""

    def _process(t):
        """Encode tree *t* and return the string."""
        # tree transformations
        if transform_options['canonicalize_roles']:
            t = transform.canonicalize_roles(t, model)

        g = layout.interpret(t, model)

        # graph transformations
        if transform_options['reify_edges']:
            g = transform.reify_edges(g, model)
        if transform_options['reify_attributes']:
            g = transform.reify_attributes(g)
        if transform_options['indicate_branches']:
            g = transform.indicate_branches(g, model)

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
        description='Read and write graphs in the PENMAN notation.'
    )
    parser.add_argument(
        '-V', '--version', action='version',
        version='Penman v{}'.format(__version__))
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
        '--canonicalize-roles', action='store_true',
        help='canonicalize role forms')
    norm.add_argument(
        '--reify-edges', action='store_true',
        help='reify all eligible edges')
    norm.add_argument(
        '--reify-attributes', action='store_true',
        help='reify all attributes')
    norm.add_argument(
        '--indicate-branches', action='store_true',
        help='insert triples to indicate tree structure')

    args = parser.parse_args()

    if args.amr:
        from penman.models.amr import model
    elif args.model:
        model = Model(**json.load(args.model))
    else:
        model = None

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

    transform_options = {
        'canonicalize_roles': args.canonicalize_roles,
        'reify_edges': args.reify_edges,
        'reify_attributes': args.reify_attributes,
        'indicate_branches': args.indicate_branches,
    }
    format_options = {
        'indent': indent,
        'compact': args.compact,
        'triples': args.triples,
    }

    if args.FILE:
        for file in args.FILE:
            with open(file) as f:
                process(f, model, sys.stdout,
                        transform_options, format_options)
    else:
        process(sys.stdin, model, sys.stdout,
                transform_options, format_options)


if __name__ == '__main__':
    main()
