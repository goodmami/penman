#!/usr/bin/env python3

"""
PENMAN graph library for AMR, DMRS, etc.

Penman is a module to assist in working with graphs encoded in the
PENMAN format, such as those for Abstract Meaning Representation (AMR)
or Dependency Minimal Recursion Semantics (DMRS). It allows for
conversion between PENMAN and triples, inspection of the graphs, and
reserialization (e.g. for selecting a new top node). Some features,
such as conversion or reserialization, can be done by calling the
module as a script.
"""

from __future__ import print_function

USAGE = '''
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
#  * PENMANCodec(nodetype_relation='instance', indent=True)
#    - PENMANCodec.decode(s)
#    - PENMANCodec.encode(g, top=None)
#    - is_relation_inverted(relation)
#    - invert_relation(relation)
#  * Triple(source, relation, target)
#  * Graph(data=None, top=None, codec=PENMANCodec)
#    - Graph.triples()
#    - Graph.top
#    - Graph.variables()
#    - Graph.concepts()
#    - Graph.constants()
#    - Graph.edges(source=None, relation=None, target=None)
#
# Module Functions:
#  * decode(s, cls=PENMANCodec, **kwargs)
#  * encode(g, cls=PENMANCodec, **kwargs)
#

import re
from collections import namedtuple, defaultdict

__version__ = '0.4.0-alpha'
__version_info__ = __version__.replace('.', ' ').replace('-', ' ').split()

_float_re = re.compile(r'-?(0|[1-9]\d*)(\.\d+[eE][-+]?|\.|[eE][-+]?)\d+$')
_int_re = re.compile(r'-?\d+$')


class PENMANCodec(object):
    """
    A parameterized encoder/decoder for graphs in PENMAN notation.
    """

    def __init__(self, nodetype_relation='instance', indent=True):
        """
        Initialize a new codec.

        Args:
            nodetype_relation: the triple relation used for '/'
            indent: if True, adaptively indent; if False or None, don't
                indent; if a non-negative integer, indent that many
                spaces per nesting level
        """
        self.nodetype_relation = nodetype_relation
        self.indent = indent
    
    def decode(self, s):
        """
        Deserialize PENMAN-notation string *s* into its Graph object.
       
        Args:
            s: a string containing a single PENMAN-serialized graph
        Returns:
            the Graph object described by *s*
        Example:

            >>> PENMANCodec.decode('(b / bark :ARG1 (d / dog))')
            <Graph object (top=b) at ...>
        """
        toks, _, depth = _lex_penman(s)
        if depth > 0:
            raise ValueError('incomplete graph: {}'.format(s))
        top, triples = self._parse_penman_node(list(reversed(toks)))
        g = Graph(triples, top=top)
        return g

    def encode(self, g, top=None):
        """
        Serialize the graph *g* from *top* to PENMAN notation.

        Args:
            g: the Graph object
            top: the node identifier for the top of the serialized
                graph; if unset, the original top of *g* is used
        Returns:
            the PENMAN-serialized string of the Graph *g*
        Example:

            >>> PENMANCodec.encode(Graph([('h', 'instance', 'hi')]))
            (h / hi)
        """
        return self._serialize_penman(g, top=top)

    def is_relation_inverted(self, relation):
        """
        Return True if *relation* is inverted.
        """
        return relation and relation.endswith('-of')

    def invert_relation(self, relation):
        """
        Invert or deinvert *relation*.
        """
        if self.is_relation_inverted(relation):
            return relation[:-3] or None
        else:
            return (relation or '') + '-of'

    def _parse_penman_node(self, toks):
        triples = []
        assert toks.pop() == '('
        var = toks.pop()
        nodetype = None
        while toks[-1] != ')':
            if toks[-1] == '/':
                toks.pop()
                nodetype = toks.pop()
            elif toks[-1][0] == ':':
                reln = toks.pop()[1:] or None
                if toks[-1] == '(':
                    tgt, ts = self._parse_penman_node(toks)
                else:
                    tgt, ts = toks.pop(), []
                    if _float_re.match(tgt):
                        tgt = float(tgt)
                    elif _int_re.match(tgt):
                        tgt = int(tgt)
                if self.is_relation_inverted(reln):
                    triples.append(Triple(tgt, self.invert_relation(reln), var))
                else:
                    triples.append(Triple(var, reln, tgt))
                triples.extend(ts)
        assert toks.pop() == ')'
        return var, [Triple(var, self.nodetype_relation, nodetype)] + triples

    def _serialize_penman(self, g, top=None):
        if top is None:
            top = g.top
        ts = defaultdict(list)
        remaining = set()
        for idx, t in enumerate(g.triples()):
            ts[t.source].append((t, t, 0.0, idx))
            if t.target in g._vars:
                invrel = self.invert_relation(t.relation)
                ts[t.target].append(
                    (Triple(t.target, invrel, t.source), t, 1.0, idx)
                )
            remaining.add(t)
        p = _walk(ts, top, remaining)
        return _layout(p, top, self, 0, set())


def encode(g, top=None, cls=PENMANCodec, **kwargs):
    """
    Serialize the graph *g* from *top* to PENMAN notation.

    Args:
        g: the Graph object
        top: the node identifier for the top of the serialized graph; if
            unset, the original top of *g* is used
        cls: serialization codec class
        kwargs: keyword arguments passed to the constructor of *cls*
    Returns:
        the PENMAN-serialized string of the Graph *g*
    Example:

        >>> PENMANCodec.encode(Graph([('h', 'instance', 'hi')]))
        (h / hi)
    """
    codec = cls(**kwargs)
    return codec.encode(g, top=top)


def decode(s, cls=PENMANCodec, **kwargs):
    """
    Deserialize PENMAN-serialized *s* into its Graph object

    Args:
        s: a string containing a single PENMAN-serialized graph
        cls: serialization codec class
        kwargs: keyword arguments passed to the constructor of *cls*
    Returns:
        the Graph object described by *s*
    Example:

        >>> PENMANCodec.decode('(b / bark :ARG1 (d / dog))')
        <Graph object (top=b) at ...>
    """
    codec = cls(**kwargs)
    return codec.decode(s)


class Triple(namedtuple('Triple', ('source', 'relation', 'target'))):
    """Container for Graph edges and node attributes."""

class Graph(object):
    """
    A basic class for modeling a directed acyclic graph.

    A Graph is defined by a list of triples, which can be divided into
    two parts: a list of graph edges where both the source and target
    are node identifiers, and a list of node attributes where only the
    source is a node identifier and the target is a constant. These
    lists can be obtained via the Graph.triples(), Graph.edges(), and
    Graph.attributes() methods.
    """

    def __init__(self, data=None, top=None, codec=PENMANCodec()):
        """
        Create a Graph from an iterable of triples.

        Args:
            data: an iterable of triples (Triple objects or 3-tuples)
            top: the node identifier of the top node; if unspecified,
                the source of the first triple is used
        Example:

            >>> Graph([
            ...     ('b', 'instance-of', 'bark'),
            ...     ('b', 'ARG1', 'd'),
            ...     ('d', 'instance-of', 'dog')]
            ... ])
        """
        if data is None:
            data = []
        self._triples = [Triple(src, rel, tgt) for src, rel, tgt in data]
        self._vars = set(t.source for t in self._triples)

        if top is None and self._triples:
            top = self._triples[0].source  # implicit top
        self.top = top

        self._codec = codec

    def __repr__(self):
        return '<{} object (top={}) at {}>'.format(
            self.__class__.__name__,
            self.top,
            id(self)
        )

    def __str__(self):
        return self._codec.encode(self)

    @property
    def top(self):
        """
        The top variable.
        """
        return self._top

    @top.setter
    def top(self, top):
        if top not in self._vars:
            raise Exception('top must be a valid node')
        self._top = top  # check if top is valid variable?

    def variables(self):
        """
        Return the list of variables (nonterminal node identifiers).
        """
        return self._vars

    def concepts(self):
        """
        Return the set of concepts in the graph.

        A concept is the target of an `instance` relation.
        """
        return set(tgt for _, rel, tgt in self._triples if rel=='instance')

    def constants(self):
        """
        Return the non-instance terminal nodes.
        """
        constants = []
        variables = self.variables()
        for triple in self._triples:
            if triple.relation == 'instance':
                continue
            if self._codec.is_relation_inverted(triple.relation):
                if triple.source not in variables:
                    constants.append(triple.source)
            elif triple.target not in variables:
                constants.append(triple.target)
        return constants

    def edges(self, source=None, relation=None, target=None):
        """
        Return edges filtered by their *source*, *relation*, or *target*.

        Edges don't include terminal triples (node types or attributes).
        """
        edges = []
        for triple in self._triples:
            if (triple.target in self._vars and
                    (source is None or source == triple.source) and
                    (relation is None or relation == triple.relation) and
                    (target is None or target == triple.target)):
                edges.append(triple)
        return edges

    def triples(self):
        """
        Return the list of triples.
        """
        return list(self._triples)

# def load(source, cls=PENMANCodec, triples=False, **kwargs):
#     """
#     Deserialize a list of PENMAN-encoded graphs from *source*.

#     Args:
#         source: a filename or file-like object to read from
#         triples: if True, read graphs as triples instead of as PENMAN
#     Returns:
#         a list of Graph objects
#     """
#     reader = cls(**kwargs)
#     if hasattr(source, 'read'):
#         return reader.decode() # not done here
#             # read(source, **kwargs))
#     else:
#         with open(source) as fh:
#             return list(read(fh, **kwargs))


# def loads(string, triples=False, **kwargs):
#     """
#     Deserialize a list of PENMAN-encoded graphs from *string*.

#     Args:
#         string: a string containing graph data
#         triples: if True, read graphs as triples instead of as PENMAN
#     Returns:
#         a list of Graph objects
#     """
#     lines = string.splitlines()
#     if triples:
#         graphs = _read_triples(lines, **kwargs)
#     else:
#         graphs = _read_penman(lines, **kwargs)
#     return list(graphs)


# def dump(file, graphs, triples=False, **kwargs):
#     """
#     Serialize each graph in *graphs* to PENMAN and write to *file*.

#     Args:
#         file: a filename or file-like object to write to
#         graphs: an iterable of Graph objects
#         triples: if True, write graphs as triples instead of as PENMAN
#     """
#     text = dumps(graphs, triples=triples, **kwargs)

#     if hasattr(file, 'write'):
#         print(text, file=file)
#     else:
#         with open(file, 'w') as fh:
#             print(text, file=fh)


# def dumps(graphs, triples=False, **kwargs):
#     """
#     Serialize each graph in *graphs* to the PENMAN format.

#     Args:
#         graphs: an iterable of Graph objects
#         triples: if True, write graphs as triples instead of as PENMAN
#     Returns:
#         the string of serialized graphs
#     """
#     if triples:
#         strings = [
#             _serialize_triples(
#                 g.triples()
#             )
#             for g in graphs
#         ]
#     else:
#         strings = [
#             g.to_penman(top=kwargs.get('top'), indent=kwargs.get('indent', True))
#             for g in graphs
#         ]
#     return '\n\n'.join(strings) + '\n'


def _read_penman(line_iterator, **kwargs):
    toks, depth = [], 0
    for line in line_iterator:
        if depth > 0 or line.lstrip().startswith('('):
            new_toks, _, depth = _lex_penman(line, depth=depth)
            toks.extend(new_toks)
            if depth == 0:
                yield _parse_penman(toks)
                toks = []


def _lex_penman(s, depth=0):
    start, i, end = 0, 0, len(s)
    toks = []
    while i < end:
        c = s[i]
        if c in ' (,)"/\n\t\r\v\f':  # breaking characters ("," for triples)
            if start < i:
                toks.append(s[start:i])
            if c in '()/,':  # basic punctuation
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


def _walk(graph, top, remaining):
    path = defaultdict(list)
    candidates = [
        # e, t, w, o = edge, triple, weight, original-order
        (e, t, w, o) for e, t, w, o in graph.get(top, []) if t in remaining
    ]
    candidates.sort(key=lambda c: (c[2], c[3]), reverse=True)
    while candidates:
        edge, triple, _, _ = candidates.pop()
        if triple in remaining:
            path[edge.source].append(edge)
            remaining.remove(triple)
            candidates.extend(graph.get(edge.target, []))
            candidates.sort(key=lambda c: c[2], reverse=True)
    return path


def _layout(g, v, codec, offset, seen):
    indent = codec.indent
    if v not in g or len(g.get(v, [])) == 0 or v in seen:
        return v
    seen.add(v)
    branches = []
    outedges = sorted(
        g[v],
        key=lambda e: (-(e.relation == codec.nodetype_relation),
                       codec.is_relation_inverted(e.relation))
    )
    head = '({}'.format(v)
    if indent is True:
        offset += len(head) + 1  # + 1 for space after v (added later)
    elif indent is not None and indent is not False:
        offset += indent
    for edge in outedges:
        if edge.relation == 'instance':
            if edge.target is None:
                continue
            rel = '/'
        else:
            rel = ':' + (edge.relation or '')
        inner_offset = (len(rel) + 1) if indent is True else 0
        branch = _layout(g, edge.target, codec, offset + inner_offset, seen)
        branches.append('{} {}'.format(rel, branch))
    if branches:
        head += ' '
    delim = ' ' if (indent is None or indent is False) else '\n'
    tail = (delim + (' ' * offset)).join(branches) + ')'
    return head + tail


def _read_triples(line_iterator, **kwargs):
    triples = []
    for line in line_iterator:
        while line:
            toks, pos, _ = _lex_penman(line)
            if len(toks) == 6 and toks[1::2] == ['(', ',', ')']:
                relation, lhs, rhs = toks[::2]
                triples.append(Triple(lhs, relation, rhs))
                line = line[pos:].lstrip()
                if line and line[0] == '^':
                    line = line[1:]
                else:
                    yield Graph(triples)
                    triples = []
                    line = ''
            line = line.lstrip()


def _serialize_triples(triples):
    return ' ^\n'.join(
        map('{0[1]}({0[0]}, {0[2]})'.format, triples)
    )


def _main():
    import sys
    from docopt import docopt
    args = docopt(USAGE, version='Penman {}'.format(__version__))

    infile = args['--input'] or sys.stdin
    data = load(infile)

    outfile = args['--output'] or sys.stdout
    dump(outfile, data, triples=args['--triples'])


if __name__ == '__main__':
    _main()
