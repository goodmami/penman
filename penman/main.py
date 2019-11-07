# -*- coding: utf-8 -*-

import sys
import argparse
import json

from penman import __version__, PENMANCodec, Model, dump


def process(f, model, out, format_options):
    data = PENMANCodec(model=model).iterdecode(f)
    dump(
        data,
        out,
        model=model,
        **format_options
    )


def main():
    parser = argparse.ArgumentParser(
        description='Read and write graphs in the PENMAN notation.'
    )
    add = parser.add_argument
    add('-V', '--version', action='version',
        version='Penman v{}'.format(__version__))
    add('FILE', nargs='*',
        help='read graphs from FILEs instead of stdin')
    model_group = parser.add_mutually_exclusive_group()
    model_group.add_argument(
        '--model', metavar='FILE',
        type=argparse.FileType('r'),
        help='JSON model file describing the semantic model')
    model_group.add_argument(
        '--amr', action='store_true',
        help='use the AMR model')
    add('--indent', metavar='N',
        help='indent N spaces per level ("no" for no newlines)')
    add('--compact', action='store_true',
        help='compactly print node attributes on one line')
    add('--triples', action='store_true',
        help='print graphs as triple conjunctions')

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

    format_options = {
        'indent': indent,
        'compact': args.compact,
        'triples': args.triples,
    }

    if args.FILE:
        for file in args.FILE:
            with open(file) as f:
                process(f, model, sys.stdout, format_options)
    else:
        process(sys.stdin, model, sys.stdout, format_options)


if __name__ == '__main__':
    main()
