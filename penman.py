#!/usr/bin/env python3

'''
Penman

An API and utility for working with graphs in the PENMAN format.

Usage: penman.py [-h|--help] [-V|--version] [options]

Arguments:
  FILE                      the input file

Options:
  -h, --help                display this help and exit
  -V, --version             display the version and exit
  -v, --verbose             verbose mode (may be repeated: -vv, -vvv)
  -i FILE, --input FILE     read graphs from FILE instanced of stdin
  -o FILE, --output FILE    write output to FILE instead of stdout
  -t, --triples             print graphs as triples

'''

# API overview:
#
# Classes:
#  * Triple(source, relation, target)
#  * Graph(triples, comment=None)
#    - Graph.from_penman(s)
#    - Graph.to_penman(top=None, indent=2, comment=False)
#    - Graph.from_triples(ts)
#    - Graph.triples()
#
# Module Functions:
#  * load(f)
#  * loads(s)
#  * dump(f, xs)
#  * dumps(xs)
#  

from __future__ import print_function

import re
from collections import namedtuple, defaultdict

__version__ = '0.1.0'
__version_info__ = __version__.replace('.', ' ').replace('-', ' ').split()


class Triple(namedtuple('Triple', ('source', 'relation', 'target'))):
    def is_inverted(self):
        return self.relation.endswith('-of')


def _invert(t):
    return Triple(
        t.target,
        t.relation[:-3] if t.is_inverted() else t.relation+'-of',
        t.source
    )


class Graph(object):
    def __init__(self):
        self._triples = []
        self._top = None

    def __str__(self):
        return self.to_penman()

    @classmethod
    def from_penman(cls, s):
        toks, pos, depth = _lex_penman(s)
        if depth > 0:
            raise ValueError('incomplete graph: {}'.format(s))
        return _parse_penman(toks)

    @classmethod
    def from_triples(cls, ts):
        g = cls()
        for source, relation, target in ts:
            if g._top is None:  # implicit top (first triple only)
                g._top = source
            if source is None and relation is None:  # explicit top
                g._top = target
            else:
                g._triples.append(Triple(source, relation, target))
        return g

    def to_penman(self, top=None, indent=True):
        if top is None: top = self._top
        if indent is False: indent = None
        return _serialize_penman(self._triples, top, indent)

    def to_triples(self):
        ts = []
        # if self._top is not None:
        #     ts.append()
        ts.extend(self._triples)
        return ts


def load(f, **kwargs):
    if hasattr(f, 'read'):
        return list(_read_penman(f, **kwargs))
    else:
        with open(f) as fh:
            return list(_read_penman(fh, **kwargs))

# def iterload(f):
#   with open(f) as fh:
#       for g in _read_penman(fh):
#           yield g


def loads(s, **kwargs):
    return list(_read_penman(s.splitlines()))


def dump(f, xs, **kwargs):
    with open(f, 'w') as fh:
        print(dumps(xs, **kwargs), file=fh)


def dumps(xs, **kwargs):
    strings = []
    for x in xs:
        if isinstance(x, Graph):
            strings.append(x.to_penman())
        else:
            strings.append(x)
    return '\n'.join(x.to_penman() for x in xs)


def _read_penman(line_iterator, **kwargs):
    toks, depth = [], 0
    for line in line_iterator:
        if depth > 0 or line.lstrip().startswith('('):
            new_toks, pos, depth = _lex_penman(line, depth=depth)
            toks.extend(new_toks)
            if depth == 0:
                g = _parse_penman(toks)
                yield g
                toks = []


def _lex_penman(s, depth=0):
    start, i, end = 0, 0, len(s)
    toks = []
    while i < end:
        c = s[i]
        if c in ' (:)"/\n\t\r\v\f':  # breaking characters
            if start < i:
                toks.append(s[start:i])        
            if c in '():/':  # basic punctuation
                toks.append(c)
                if c == '(':
                    depth += 1
                elif c == ')':
                    depth -= 1
                    if depth == 0:
                        start = i + 1
                        break
            elif c == '"':  # start of string
                i += 1
                c = s[i]
                while c != '"':
                    i += 2 if c == '\\' else 1
                    c = s[i]
                toks.append(s[start:i+1])
            else:  # whitespace (c in ' \t\n\v\f\r')
                pass
            start = i + 1
        else:   # symbol not covered above; don't split
            pass
        i += 1
    if start < i:
        toks.append(s[start:i])
    if depth < 0:
        raise ValueError('Invalid graph at position {}'.format(i))
    return toks, i + 1, depth


def _parse_penman(toks):
    toks = list(reversed(toks))
    nodestack = [None]
    reln = None
    triples = []
    while toks:
        tok = toks.pop()
        if tok == '(':
            v = toks.pop()
            triples.append(Triple(nodestack[-1], reln, v))
            nodestack.append(v)
        elif tok == ')':
            nodestack.pop()
        elif tok == '/':
            tgt = toks.pop()
            triples.append(Triple(nodestack[-1], 'instance-of', tgt))
        elif tok == ':':
            reln = toks.pop()
        else:
            triples.append(Triple(nodestack[-1], reln, tok))
    return Graph.from_triples(triples)


def _serialize_penman(triples, top, indent):
    g = defaultdict(list)
    remaining = set()
    for triple in triples:
        g[triple.source].append((triple, triple, 0.0))
        g[triple.target].append((_invert(triple), triple, 1.0))
        remaining.add(triple)
    p = _walk(g, top, remaining)
    return _layout(p, top, indent, 0, set())


def _walk(g, v, remaining):
    p = defaultdict(list)
    candidates = [(e, t, w) for e, t, w in g.get(v, []) if t in remaining]
    candidates.sort(key=lambda e_t_w: e_t_w[2], reverse=True)
    while candidates:
        e, t, w = candidates.pop()
        if t in remaining:
            p[e.source].append(e)
            remaining.remove(t)
            candidates.extend(g.get(e.target, []))
            candidates.sort(key=lambda e_t_w: e_t_w[2], reverse=True)
    return p


def _layout(g, v, indent, offset, seen):
    if v not in g or len(g.get(v, [])) == 0 or v in seen:
        return v
    seen.add(v)
    branches = []
    outedges = sorted(
        g[v],
        key=lambda e: (-e.relation.startswith('instance'),
                       e.is_inverted(),
                       e.relation)
    )
    offset += len(v) + 2  # 2 for '(' and ' '
    for edge in outedges:
        rel = '/' if edge.relation == 'instance-of' else ':' + edge.relation
        branch = _layout(g, edge.target, indent, offset + len(rel) + 1, seen)
        branches.append('{} {}'.format(rel, branch))
    rels = ('\n' + (' ' * offset)).join(branches)
    s = '({} {})'.format(v, rels)
    return s


def _main(args):
    import sys
    infile = args['--input'] or sys.stdin
    data = load(infile)
    gformat = Graph.to_triples if args['--triples'] else Graph.to_penman
    for g in data:
        print(gformat(g))
        print()


if __name__ == '__main__':
    from docopt import docopt
    args = docopt(__doc__, version='Penman {}'.format(__version__))
    _main(args)
