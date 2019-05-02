# -*- coding: utf-8 -*-

import sys
import argparse
import json

from penman import __version__, PENMANCodec, AMRCodec, Model, dump


def main():
    parser = argparse.ArgumentParser(
        description='An API and utility for working with graphs in the '
                    'PENMAN notation.'
    )
    add = parser.add_argument
    add('-V', '--version', action='version',
        version='Penman v{}'.format(__version__))
    add('-i', '--input', metavar='FILE',
        type=argparse.FileType('r'), default=sys.stdin,
        help='read graphs from FILE instead of stdin')
    add('-o', '--output', metavar='FILE',
        type=argparse.FileType('w'), default=sys.stdout,
        help='write output to FILE instead of stdout')
    add('-m', '--model', metavar='FILE',
        type=argparse.FileType('r'),
        help='JSON model file describing valid structures')
    add('-t', '--triples', action='store_true',
        help='print graphs as triple conjunctions')
    add('--indent', metavar='N',
        help='indent N spaces per level ("no" for no newlines)')
    add('--amr', action='store_true',
        help='use AMR codec instead of generic PENMAN one')

    args = parser.parse_args()

    codec = AMRCodec if args.amr else PENMANCodec

    indent = True
    if args.indent:
        if args.indent.lower() in ("no", "none", "false"):
            indent = False
        else:
            try:
                indent = int(args.indent)
                if indent < 0:
                    raise ValueError
            except ValueError:
                sys.exit('error: --indent value must be "no" or a '
                         ' positive integer')

    if args.model:
        model = Model(**json.load(args.model))
    else:
        model = None

    data = codec(model=model).iterdecode(args.input.read())
    dump(
        data,
        args.output,
        triples=args.triples,
        cls=codec,
        indent=indent
    )


if __name__ == '__main__':
    main()
