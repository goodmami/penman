#!/usr/bin/env python3

"""
PENMAN graph library for AMR, DMRS, etc.

Penman is a module to assist in working with graphs encoded in PENMAN
notation, such as those for Abstract Meaning Representation (AMR) or
Dependency Minimal Recursion Semantics (DMRS). It allows for conversion
between PENMAN and triples, inspection of the graphs, and
reserialization (e.g. for selecting a new top node). Some features,
such as conversion or reserialization, can be done by calling the
module as a script.
"""

from __future__ import print_function

USAGE = '''
Penman

An API and utility for working with graphs in PENMAN notation.

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
#  * PENMANCodec(indent=True)
#    - PENMANCodec.decode(s)
#    - PENMANCodec.iterdecode(s)
#    - PENMANCodec.encode(g, top=None)
#    - PENMANCodec.is_relation_inverted(relation)
#    - PENMANCodec.invert_relation(relation)
#    - PENMANCodec.handle_value(s)
#    - PENMANCodec.handle_triple(source, relation, target)
#  * Triple(source, relation, target)
#  * Graph(data=None, top=None, codec=PENMANCodec)
#    - Graph.top
#    - Graph.variables()
#    - Graph.triples(source=None, relation=None, target=None)
#    - Graph.edges(source=None, relation=None, target=None)
#    - Graph.attributes(source=None, relation=None, target=None)
#
# Module Functions:
#  * decode(s, cls=PENMANCodec, **kwargs)
#  * encode(g, cls=PENMANCodec, **kwargs)
#  * load(source, triples=False, cls=PENMANCodec, **kwargs)
#  * loads(string, triples=False, cls=PENMANCodec, **kwargs)
#  * dump(graphs, file, triples=False, cls=PENMANCodec, **kwargs)
#  * dumps(graphs, triples=False, cls=PENMANCodec, **kwargs)

import re
from collections import namedtuple, defaultdict

__version__ = '0.4.0'
__version_info__ = __version__.replace('.', ' ').replace('-', ' ').split()

class PENMANCodec(object):
    """
    A parameterized encoder/decoder for graphs in PENMAN notation.
    """

    TYPE_REL = 'instance'
    NODE_ENTER_RE = re.compile(r'\s*(\()\s*([^\s()\/,]+)\s*')
    NODE_EXIT_RE = re.compile(r'\s*(\))\s*')
    RELATION_RE = re.compile(r'(:[^\s(),]*)\s*')
    ATOM_RE = re.compile(r'\s*([^\s()\/,]+)\s*')
    STRING_RE = re.compile(r'("[^"\\]*(?:\\.[^"\\]*)*")\s*')
    COMMA_RE = re.compile(r'\s*,\s*')

    def __init__(self, indent=True):
        """
        Initialize a new codec.

        Args:
            indent: if True, adaptively indent; if False or None, don't
                indent; if a non-negative integer, indent that many
                spaces per nesting level
        """
        self.indent = indent
    
    def decode(self, s, triples=False):
        """
        Deserialize PENMAN-notation string *s* into its Graph object.
       
        Args:
            s: a string containing a single PENMAN-serialized graph
            triples: if True, treat *s* as a conjunction of logical triples
        Returns:
            the Graph object described by *s*
        Example:

            >>> PENMANCodec.decode('(b / bark :ARG1 (d / dog))')
            <Graph object (top=b) at ...>
            >>> PENMANCodec.decode(
            ...     'instance(b, bark) ^ instance(d, dog) ^ ARG1(b, d)'
            ... )
            <Graph object (top=b) at ...>
        """
        try:
            if triples:
                span, data = self._decode_triple_conjunction(s)
            else:
                span, data = self._decode_penman_node(s)
        except IndexError:
            raise DecodeError(
                'Unexpected end of string.', string=s, pos=len(s)
            )
        top, triples = data
        g = Graph(triples, top=top)
        return g

    def iterdecode(self, s, triples=False):
        """
        Deserialize PENMAN-notation string *s* into its Graph objects.
       
        Args:
            s: a string containing zero or more PENMAN-serialized graphs
            triples: if True, treat *s* as a conjunction of logical triples
        Yields:
            valid Graph objects described by *s*
        Example:

            >>> list(PENMANCodec.iterdecode('(h / hello)(g / goodbye)'))
            [<Graph object (top=h) at ...>, <Graph object (top=g) at ...>]
            >>> list(PENMANCodec.iterdecode(
            ...     'instance(h, hello)\n'
            ...     'instance(g, goodbye)'
            ... ))
            [<Graph object (top=h) at ...>, <Graph object (top=g) at ...>]
        """
        pos, strlen = 0, len(s)
        while pos < strlen:
            if s[pos] == '#':
                while pos < strlen and s[pos] != '\n':
                    pos += 1
            elif triples or s[pos] == '(':
                try:
                    if triples:
                        span, data = self._decode_triple_conjunction(
                            s, pos=pos
                        )
                    else:
                        span, data = self._decode_penman_node(s, pos=pos)
                except (IndexError, DecodeError):
                    # don't re-raise below for more robust parsing, but
                    # for now, raising helps with debugging bad input
                    raise
                    pos += 1
                else:
                    top, ts = data
                    yield Graph(ts, top=top)
                    pos = span[1]
            else:
                pos += 1

    def encode(self, g, top=None, triples=False):
        """
        Serialize the graph *g* from *top* to PENMAN notation.

        Args:
            g: the Graph object
            top: the node identifier for the top of the serialized
                graph; if unset, the original top of *g* is used
            triples: if True, serialize as a conjunction of logical triples
        Returns:
            the PENMAN-serialized string of the Graph *g*
        Example:

            >>> PENMANCodec.encode(Graph([('h', 'instance', 'hi')]))
            (h / hi)
            >>> PENMANCodec.encode(Graph([('h', 'instance', 'hi')]),
            ...                    triples=True)
            instance(h, hi)
        """
        if triples:
            return self._encode_triple_conjunction(g, top=top)
        else:
            return self._encode_penman(g, top=top)

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

    def handle_value(self, s):
        """
        Process relation value *s* before it is used in a triple.

        Args:
            s: the string value of a non-nodetype relation
        Returns:
            the value, converted to float or int if applicable,
            otherwise the unchanged string
        """
        if s.startswith('"'):
            value = s
        elif re.match(r'-?(0|[1-9]\d*)(\.\d+[eE][-+]?|\.|[eE][-+]?)\d+', s):
            value = float(s)
        elif re.match(r'-?\d+', s):
            value = int(s)
        else:
            value = s
        return value

    def handle_triple(self, lhs, relation, rhs):
        """
        Process triples before they are added to the graph.

        Note that *lhs* and *rhs* are as they originally appeared, and
        may be inverted. By default, this function normalizes all such
        inversions, and also removes initial colons in relations and
        sets empty relations to None.

        Args:
            lhs: the left hand side of an observed triple
            relation: the triple relation (possibly inverted)
            rhs: the right hand side of an observed triple
        Returns:
            The processed (source, relation, target) triple. By default,
            it is returned as a Triple object.
        """
        relation = relation.replace(':', '', 1)  # remove leading :
        if self.is_relation_inverted(relation):  # deinvert
            source, target = rhs, lhs
            relation = self.invert_relation(relation)
        else:
            source, target = lhs, rhs
        if relation == '':  # set empty relations to None
            relation = None
        return Triple(source, relation, target)

    def _decode_triple_conjunction(self, s, pos=0):
        triples = []
        start = None
        while True:
            m = _regex(self.ATOM_RE, s, pos, "a relation/predicate")
            if start is None:
                start = m.start(1)
            pos, rel = m.end(0), m.group(1)
            m = _regex(self.NODE_ENTER_RE, s, pos, '"(" and a variable')
            pos, var = m.end(0), m.group(2)
            m = _regex(self.COMMA_RE, s, pos, '","')
            pos = m.end(0)
            if s[pos] == '"':
                m = _regex(self.STRING_RE, s, pos, 'a quoted string')
            else:
                m = _regex(self.ATOM_RE, s, pos, 'a float/int/atom')
            pos, tgt = m.end(0), m.group(1)
            # don't "handle" if its a node type (not in this version, at least)
            if rel != self.TYPE_REL:
                tgt = self.handle_value(tgt)
            triples.append(self.handle_triple(var, rel, tgt))
            m = _regex(self.NODE_EXIT_RE, s, pos, '")"')
            pos = m.end(1)
            if m.end(0) >= len(s) or s[m.end(0)] != '^':
                break
        top = triples[0][0] if triples else None
        return (start, pos), (top, triples)

    def _decode_penman_node(self, s, pos=0):
        triples = []

        strlen = len(s)
        m = _regex(self.NODE_ENTER_RE, s, pos, '"(" and a variable')
        start, pos, var = m.start(1), m.end(0), m.group(2)

        nodetype = None
        while pos < strlen and s[pos] != ')':

            # node type
            if s[pos] == '/':
                m = _regex(self.ATOM_RE, s, pos+1, 'a node type')
                pos, nodetype = m.end(0), m.group(1)

            # relation
            elif s[pos] == ':':
                m = _regex(self.RELATION_RE, s, pos, 'a relation')
                pos, rel = m.end(0), m.group(1)

                # node value
                if s[pos] == '(':
                    span, data = self._decode_penman_node(s, pos=pos)
                    pos = span[1]
                    triples.append(self.handle_triple(var, rel, data[0]))
                    triples.extend(data[1])

                # string or other atom value
                else:
                    if s[pos] == '"':
                        m = _regex(self.STRING_RE, s, pos, 'a quoted string')
                        pos, value = m.end(0), m.group(1)
                    else:
                        m = _regex(self.ATOM_RE, s, pos, 'a float/int/atom')
                        pos, value = m.end(0), m.group(1)
                    triples.append(
                        self.handle_triple(var, rel, self.handle_value(value))
                    )

            elif s[pos].isspace():
                pos += 1

            # error
            else:
                raise DecodeError('Expected ":" or "/"', string=s, pos=pos)

        m = _regex(self.NODE_EXIT_RE, s, pos, '")"')
        pos = m.end(1)

        triples = [self.handle_triple(var, self.TYPE_REL, nodetype)] + triples

        return (start, pos), (var, triples)

    def _encode_penman(self, g, top=None):
        if top is None:
            top = g.top
        ts = defaultdict(list)
        remaining = set()
        variables = g.variables()
        for idx, t in enumerate(g.triples()):
            ts[t.source].append((t, t, 0.0, idx))
            if t.target in variables:
                invrel = self.invert_relation(t.relation)
                ts[t.target].append(
                    (Triple(t.target, invrel, t.source), t, 1.0, idx)
                )
            remaining.add(t)
        p = _walk(ts, top, remaining)
        return _layout(p, top, self, 0, set())

    def _encode_triple_conjunction(self, g, top=None):
        return ' ^\n'.join(
            map('{0[1]}({0[0]}, {0[2]})'.format, g.triples())
        )


def _regex(x, s, pos, msg):
    m = x.match(s, pos=pos)
    if m is None:
        raise DecodeError('Expected {}'.format(msg), string=s, pos=pos)
    return m


class DecodeError(Exception):
    """Raised when decoding PENMAN-notation fails."""
    
    def __init__(self, *args, **kwargs):
        # Python2 doesn't allow parameters like:
        #   (*args, key=val, **kwargs)
        # so do this manaully.
        string = pos = None
        if 'string' in kwargs:
            string = kwargs['string']
            del kwargs['string']
        if 'pos' in kwargs:
            pos = kwargs['pos']
            del kwargs['pos']
        super(DecodeError, self).__init__(*args, **kwargs)
        self.string = string
        self.pos = pos

    def __str__(self):
        if isinstance(self.pos, slice):
            loc = ' in span {}:{}'.format(self.pos.start, self.pos.stop)
        else:
            loc = ' at position {}'.format(self.pos)
        return Exception.__str__(self) + loc


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

        >>> decode('(b / bark :ARG1 (d / dog))')
        <Graph object (top=b) at ...>
    """
    codec = cls(**kwargs)
    return codec.decode(s)


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


def load(source, triples=False, cls=PENMANCodec, **kwargs):
    """
    Deserialize a list of PENMAN-encoded graphs from *source*.

    Args:
        source: a filename or file-like object to read from
        triples: if True, read graphs as triples instead of as PENMAN
        cls: serialization codec class
        kwargs: keyword arguments passed to the constructor of *cls*
    Returns:
        a list of Graph objects
    """
    decode = cls(**kwargs).iterdecode
    if hasattr(source, 'read'):
        return list(decode(source.read()))
    else:
        with open(source) as fh:
            return list(decode(fh.read()))


def loads(string, triples=False, cls=PENMANCodec, **kwargs):
    """
    Deserialize a list of PENMAN-encoded graphs from *string*.

    Args:
        string: a string containing graph data
        triples: if True, read graphs as triples instead of as PENMAN
        cls: serialization codec class
        kwargs: keyword arguments passed to the constructor of *cls*
    Returns:
        a list of Graph objects
    """
    codec = cls(**kwargs)
    return list(codec.iterdecode(string, triples=triples))


def dump(graphs, file, triples=False, cls=PENMANCodec, **kwargs):
    """
    Serialize each graph in *graphs* to PENMAN and write to *file*.

    Args:
        graphs: an iterable of Graph objects
        file: a filename or file-like object to write to
        triples: if True, write graphs as triples instead of as PENMAN
        cls: serialization codec class
        kwargs: keyword arguments passed to the constructor of *cls*
    """
    text = dumps(graphs, triples=triples, cls=cls, **kwargs)

    if hasattr(file, 'write'):
        print(text, file=file)
    else:
        with open(file, 'w') as fh:
            print(text, file=fh)


def dumps(graphs, triples=False, cls=PENMANCodec, **kwargs):
    """
    Serialize each graph in *graphs* to the PENMAN format.

    Args:
        graphs: an iterable of Graph objects
        triples: if True, write graphs as triples instead of as PENMAN
    Returns:
        the string of serialized graphs
    """
    codec = cls(**kwargs)
    strings = [codec.encode(g, triples=triples) for g in graphs]
    return '\n\n'.join(strings)


class Triple(namedtuple('Triple', ('source', 'relation', 'target'))):
    """Container for Graph edges and node attributes."""

class Graph(object):
    """
    A basic class for modeling a rooted, directed acyclic graph.

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
            codec: the serialization codec used to interpret values
        Example:

            >>> Graph([
            ...     ('b', 'instance', 'bark'),
            ...     ('d', 'instance', 'dog'),
            ...     ('b', 'ARG1', 'd')
            ... ])
        """
        self._triples = []
        self._nodes = []
        self._top = None
        self._codec = codec

        ntrel = self._codec.TYPE_REL
        if data:
            if top is None:
                top = data[0][0]  # implicit top: source of first triple
            ntypes = dict((s, t) for s, r, t in data if r == ntrel)
            nodes = set(s for s, _, _ in data)
            for src, rel, tgt in data:
                # insert node types in order of node appearance
                if src in nodes:
                    self._nodes.append((src, ntypes.get(src)))
                    nodes.remove(src)
                if tgt in nodes:
                    self._nodes.append((tgt, ntypes.get(tgt)))
                    nodes.remove(tgt)
                # then add triple if not nodetype
                if rel != ntrel:
                    self._triples.append(Triple(src, rel, tgt))
            self.top = top

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
        if top not in self.variables():
            raise ValueError('top must be a valid node')
        self._top = top  # check if top is valid variable?

    def variables(self):
        """
        Return the list of variables (nonterminal node identifiers).
        """
        return set(v for v, _ in self._nodes)

    def triples(self, source=None, relation=None, target=None):
        """
        Return triples filtered by their *source*, *relation*, or *target*.
        """
        triplematch = lambda t: (
            (source is None or source == t.source) and
            (relation is None or relation == t.relation) and
            (target is None or target == t.target)
        )
        triples = [
            Triple(v, self._codec.TYPE_REL, t) for v, t in self._nodes
        ]
        triples.extend(self._triples)
        return list(filter(triplematch, triples))

    def edges(self, source=None, relation=None, target=None):
        """
        Return edges filtered by their *source*, *relation*, or *target*.

        Edges don't include terminal triples (node types or attributes).
        """
        edgematch = lambda e: (
            (source is None or source == e.source) and
            (relation is None or relation == e.relation) and
            (target is None or target == e.target)
        )
        variables = self.variables()
        edges = [t for t in self._triples if t.target in variables]
        return list(filter(edgematch, edges))

    def attributes(self, source=None, relation=None, target=None):
        """
        Return attributes filtered by their *source*, *relation*, or *target*.

        Attributes don't include triples where the target is a nonterminal.
        """
        attrmatch = lambda a: (
            (source is None or source == a.source) and
            (relation is None or relation == a.relation) and
            (target is None or target == a.target)
        )
        variables = self.variables()
        attrs = [t for t in self.triples() if t.target not in variables]
        return list(filter(attrmatch, attrs))

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
        key=lambda e: (-(e.relation == codec.TYPE_REL),
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
