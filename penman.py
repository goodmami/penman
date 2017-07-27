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

Options:
  -h, --help                display this help and exit
  -V, --version             display the version and exit
  -i FILE, --input FILE     read graphs from FILE instead of stdin
  -o FILE, --output FILE    write output to FILE instead of stdout
  -t, --triples             print graphs as triple conjunctions
  --indent N                indent N spaces per level ("no" for no newlines)
  --amr                     use AMR codec instead of generic PENMAN one
'''

# API overview:
#
# Classes:
#  * PENMANCodec(indent=True, relation_sort=original_order)
#    - PENMANCodec.decode(s)
#    - PENMANCodec.iterdecode(s)
#    - PENMANCodec.encode(g, top=None)
#    - PENMANCodec.is_relation_inverted(relation)
#    - PENMANCodec.invert_relation(relation)
#    - PENMANCodec.handle_triple(source, relation, target)
#    - PENMANCodec.triples_to_graph(triples, top=None)
#  * AMRCodec(indent=True, relation_sort=original_order)
#    - (methods are the same as PENMANCodec)
#  * Triple(source, relation, target)
#  * Graph(data=None, top=None)
#    - Graph.top
#    - Graph.variables()
#    - Graph.triples(source=None, relation=None, target=None)
#    - Graph.edges(source=None, relation=None, target=None)
#    - Graph.attributes(source=None, relation=None, target=None)
#    - Graph.reentrancies()
#
# Module Functions:
#  * decode(s, cls=PENMANCodec, **kwargs)
#  * encode(g, cls=PENMANCodec, **kwargs)
#  * load(source, triples=False, cls=PENMANCodec, **kwargs)
#  * loads(string, triples=False, cls=PENMANCodec, **kwargs)
#  * dump(graphs, file, triples=False, cls=PENMANCodec, **kwargs)
#  * dumps(graphs, triples=False, cls=PENMANCodec, **kwargs)
#  * original_order(triples)
#  * out_first_order(triples)
#  * alphanum_order(triples)

import re
from collections import namedtuple, defaultdict
try:
    basestring
except NameError:
    basestring = str

__version__ = '0.6.2'
__version_info__ = [
    int(x) if x.isdigit() else x
    for x in re.findall(r'[0-9]+|[^0-9\.-]+', __version__)
]


def original_order(triples):
    """
    Return a list of triples in the original order.
    """
    return triples


def out_first_order(triples):
    """
    Sort a list of triples so outward (true) edges appear first.
    """
    return sorted(triples, key=lambda t: t.inverted)


def alphanum_order(triples):
    """
    Sort a list of triples by relation name.

    Embedded integers are sorted numerically, but otherwise the sorting
    is alphabetic.
    """
    return sorted(
        triples,
        key=lambda t: [
            int(t) if t.isdigit() else t
            for t in re.split(r'([0-9]+)', t.relation or '')
        ]
    )


class PENMANCodec(object):
    """
    A parameterized encoder/decoder for graphs in PENMAN notation.
    """

    TYPE_REL = 'instance'
    TOP_VAR = None
    TOP_REL = 'top'
    NODE_ENTER_RE = re.compile(r'\s*(\()\s*')
    NODE_EXIT_RE = re.compile(r'\s*(\))\s*')
    RELATION_RE = re.compile(r'(:[^\s(),]*)\s*')
    INT_RE = re.compile(r'[+-]?\d+')
    FLOAT_RE = re.compile(
        r'[-+]?(((\d+\.\d*|\.\d+)([eE][-+]?\d+)?)|\d+[eE][-+]?\d+)'
    )
    ATOM_RE = re.compile(r'([^\s()\/,]+)')
    STRING_RE = re.compile(r'("[^"\\]*(?:\\.[^"\\]*)*")')
    VAR_RE = re.compile('({}|{})'.format(STRING_RE.pattern, ATOM_RE.pattern))
    NODETYPE_RE = VAR_RE  # default; allow strings, numbers, and symbols
    COMMA_RE = re.compile(r'\s*,\s*')
    SPACING_RE = re.compile(r'\s*')

    def __init__(self, indent=True, relation_sort=original_order):
        """
        Initialize a new codec.

        Args:
            indent: if True, adaptively indent; if False or None, don't
                indent; if a non-negative integer, indent that many
                spaces per nesting level
            relation_sort: when encoding, sort the relations on each
                node according to this function; by default, the
                original order is maintained
        """
        self.indent = indent
        self.relation_sort = relation_sort

    def decode(self, s, triples=False):
        """
        Deserialize PENMAN-notation string *s* into its Graph object.

        Args:
            s: a string containing a single PENMAN-serialized graph
            triples: if True, treat *s* as a conjunction of logical triples
        Returns:
            the Graph object described by *s*
        Example:

            >>> codec = PENMANCodec()
            >>> codec.decode('(b / bark :ARG1 (d / dog))')
            <Graph object (top=b) at ...>
            >>> codec.decode(
            ...     'instance(b, bark) ^ instance(d, dog) ^ ARG1(b, d)',
            ...     triples=True
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
        top, nodes, edges = data
        return self.triples_to_graph(nodes + edges, top=top)

    def iterdecode(self, s, triples=False):
        """
        Deserialize PENMAN-notation string *s* into its Graph objects.

        Args:
            s: a string containing zero or more PENMAN-serialized graphs
            triples: if True, treat *s* as a conjunction of logical triples
        Yields:
            valid Graph objects described by *s*
        Example:

            >>> codec = PENMANCodec()
            >>> list(codec.iterdecode('(h / hello)(g / goodbye)'))
            [<Graph object (top=h) at ...>, <Graph object (top=g) at ...>]
            >>> list(codec.iterdecode(
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
                    top, nodes, edges = data
                    yield self.triples_to_graph(nodes + edges, top=top)
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

            >>> codec = PENMANCodec()
            >>> codec.encode(Graph([('h', 'instance', 'hi')]))
            (h / hi)
            >>> codec.encode(Graph([('h', 'instance', 'hi')]),
            ...                      triples=True)
            instance(h, hi)
        """
        if len(g.triples()) == 0:
            raise EncodeError('Cannot encode empty graph.')
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

    def handle_triple(self, lhs, relation, rhs):
        """
        Process triples before they are added to the graph.

        Note that *lhs* and *rhs* are as they originally appeared, and
        may be inverted. Inversions are detected by
        is_relation_inverted() and de-inverted by invert_relation().

        By default, this function:
         * removes initial colons on relations
         * de-inverts all inverted relations
         * sets empty relations to `None`
         * casts numeric string sources and targets to their numeric
           types (e.g. float, int)

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
            source, target, inverted = rhs, lhs, True
            relation = self.invert_relation(relation)
        else:
            source, target, inverted = lhs, rhs, False

        source = _default_cast(source)
        target = _default_cast(target)

        if relation == '':  # set empty relations to None
            relation = None

        return Triple(source, relation, target, inverted)

    def triples_to_graph(self, triples, top=None):
        """
        Create a Graph from *triples* considering codec configuration.

        The Graph class does not know about information in the codec,
        so if Graph instantiation depends on special `TYPE_REL` or
        `TOP_VAR` values, use this function instead of instantiating
        a Graph object directly. This is also where edge
        normalization (de-inversion) and value type conversion occur
        (via handle_triple()).

        Args:
            triples: an iterable of (lhs, relation, rhs) triples
            top: node identifier of the top node
        Returns:
            a Graph object
        """
        inferred_top = triples[0][0] if triples else None
        ts = []
        for triple in triples:
            if triple[0] == self.TOP_VAR and triple[1] == self.TOP_REL:
                inferred_top = triple[2]
            else:
                ts.append(self.handle_triple(*triple))
        top = self.handle_triple(self.TOP_VAR, self.TOP_REL, top).target
        return Graph(ts, top=top or inferred_top)


    def _decode_triple_conjunction(self, s, pos=0):
        top, nodes, edges = None, [], []
        start = None
        while True:
            m = _regex(self.ATOM_RE, s, pos, "a relation/predicate")
            if start is None:
                start = m.start(1)
            pos, rel = m.end(0), m.group(1)

            m = _regex(self.NODE_ENTER_RE, s, pos, '"("')
            pos = m.end(0)
            
            m = _regex(self.VAR_RE, s, pos, "a variable (node identifier)")
            pos, var = m.end(0), m.group(1).strip()

            m = _regex(self.COMMA_RE, s, pos, '","')
            pos = m.end(0)

            if rel == self.TYPE_REL:
                m = _regex(self.NODETYPE_RE, s, pos, 'a node type')
            else:
                if s[pos] == '"':
                    m = _regex(self.STRING_RE, s, pos, 'a quoted string')
                else:
                    m = _regex(self.ATOM_RE, s, pos, 'a float/int/symbol')
            pos, tgt = m.end(0), m.group(1)
            
            if var == self.TOP_VAR and rel == self.TOP_REL:
                top = tgt
            elif rel == self.TYPE_REL:
                nodes.append((var, rel, tgt))
            else:
                edges.append((var, rel, tgt))
            
            m = _regex(self.NODE_EXIT_RE, s, pos, '")"')
            pos = m.end(1)
            
            if m.end(0) < len(s) and s[m.end(0)] == '^':
                pos = m.end(0) + 1
            else:
                break
        if top is None and nodes:
            top = nodes[0][0]
        return (start, pos), (top, nodes, edges)

    def _decode_penman_node(self, s, pos=0):
        nodes, edges = [], []

        strlen = len(s)
        m = _regex(self.NODE_ENTER_RE, s, pos, '"("')
        start, pos = m.start(1), m.end(0)

        m = _regex(self.VAR_RE, s, pos, "a variable (node identifier)")
        pos, var = m.end(0), m.group(1).strip()

        nodetype = None
        while pos < strlen and s[pos] != ')':

            # node type
            if s[pos] == '/':
                pos = self.SPACING_RE.match(s, pos=pos+1).end()
                m = _regex(self.NODETYPE_RE, s, pos, 'a node type')
                pos, nodetype = m.end(0), m.group(1)

            # relation
            elif s[pos] == ':':
                m = _regex(self.RELATION_RE, s, pos, 'a relation')
                pos, rel = m.end(0), m.group(1)

                # node value
                if s[pos] == '(':
                    span, data = self._decode_penman_node(s, pos=pos)
                    pos = span[1]
                    subtop, subnodes, subedges = data
                    nodes.extend(subnodes)
                    edges.append((var, rel, subtop))
                    edges.extend(subedges)

                # string or other atom value
                else:
                    if s[pos] == '"':
                        m = _regex(self.STRING_RE, s, pos, 'a quoted string')
                        pos, value = m.end(0), m.group(1)
                    else:
                        m = _regex(self.ATOM_RE, s, pos, 'a float/int/symbol')
                        pos, value = m.end(0), m.group(1)
                    edges.append((var, rel, value))

            elif s[pos].isspace():
                pos += 1

            # error
            else:
                raise DecodeError('Expected ":" or "/"', string=s, pos=pos)

        m = _regex(self.NODE_EXIT_RE, s, pos, '")"')
        pos = m.end(1)

        nodes = [(var, self.TYPE_REL, nodetype)] + nodes

        return (start, pos), (var, nodes, edges)

    def _encode_penman(self, g, top=None):
        """
        Walk graph g and find a spanning dag, then serialize the result.

        First, depth-first traversal of preferred orientations (whether
        true or inverted) to create graph p.

        If any triples remain, select the first remaining triple whose
        source in the dispreferred orientation exists in p, where
        'first' is determined by the order of inserted nodes (i.e. a
        topological sort). Add this triple, then repeat the depth-first
        traversal of preferred orientations from its target. Repeat
        until no triples remain, or raise an error if there are no
        candidates in the dispreferred orientation (which likely means
        the graph is disconnected).
        """
        if top is None:
            top = g.top
        remaining = set(g.triples())
        variables = g.variables()
        store = defaultdict(lambda: ([], []))  # (preferred, dispreferred)
        for t in g.triples():
            if t.inverted:
                store[t.target][0].append(t)
                store[t.source][1].append(Triple(*t, inverted=False))
            else:
                store[t.source][0].append(t)
                store[t.target][1].append(Triple(*t, inverted=True))

        p = defaultdict(list)
        topolist = [top]

        def _update(t):
            src, tgt = (t[2], t[0]) if t.inverted else (t[0], t[2])
            p[src].append(t)
            remaining.remove(t)
            if tgt in variables and t.relation != self.TYPE_REL:
                topolist.append(tgt)
                return tgt
            return None

        def _explore_preferred(src):
            ts = store.get(src, ([], []))[0]
            for t in ts:
                if t in remaining:
                    tgt = _update(t)
                    if tgt is not None:
                        _explore_preferred(tgt)
            ts[:] = []  # clear explored list

        _explore_preferred(top)

        while remaining:
            flip_candidates = [store.get(v, ([],[]))[1] for v in topolist]
            for fc in flip_candidates:
                fc[:] = [c for c in fc if c in remaining]  # clear superfluous
            if not any(len(fc) > 0 for fc in flip_candidates):
                raise EncodeError('Invalid graph; possibly disconnected.')
            c = next(c for fc in flip_candidates for c in fc)
            tgt = _update(c)
            if tgt is not None:
                _explore_preferred(tgt)

        return self._layout(p, top, 0, set())

    def _layout(self, g, src, offset, seen):
        indent = self.indent
        if src not in g or len(g.get(src, [])) == 0 or src in seen:
            return src
        seen.add(src)
        branches = []
        outedges = self.relation_sort(g[src])
        head = '({}'.format(src)
        if indent is True:
            offset += len(head) + 1  # + 1 for space after src (added later)
        elif indent is not None and indent is not False:
            offset += indent
        for t in outedges:
            if t.relation == self.TYPE_REL:
                if t.target is not None:
                    # node types always come first
                    branches = ['/ {}'.format(t.target)] + branches
            else:
                if t.inverted:
                    tgt = t.source
                    rel = self.invert_relation(t.relation)
                else:
                    tgt = t.target
                    rel = t.relation or ''
                inner_offset = (len(rel) + 2) if indent is True else 0
                branch = self._layout(g, tgt, offset + inner_offset, seen)
                branches.append(':{} {}'.format(rel, branch))
        if branches:
            head += ' '
        delim = ' ' if (indent is None or indent is False) else '\n'
        tail = (delim + (' ' * offset)).join(branches) + ')'
        return head + tail

    def _encode_triple_conjunction(self, g, top=None):
        if top is None:
            top = g.top
        if self.TOP_VAR is not None and top is not None:
            top_triple = [(self.TOP_VAR, self.TOP_REL, top)]
        else:
            top_triple = []
        return ' ^\n'.join(
            map('{0[1]}({0[0]}, {0[2]})'.format, top_triple + g.triples())
        )


class AMRCodec(PENMANCodec):
    """
    An AMR codec for graphs in PENMAN notation.
    """
    TYPE_REL = 'instance'
    TOP_VAR = None
    TOP_REL = 'top'
    # vars: [a-z]+\d* ; first relation must be node type
    NODE_ENTER_RE = re.compile(r'\s*(\()\s*(?=[a-z]+\d*\s*\/)')
    NODETYPE_RE = PENMANCodec.ATOM_RE
    VAR_RE = re.compile(r'([a-z]+\d*)')
    # only non-anonymous relations
    RELATION_RE = re.compile(r'(:[^\s(),]+)\s*')

    _inversions = {
        TYPE_REL: None,  # don't allow inverted types
        'domain': 'mod',
        'consist-of': 'consist-of-of',
        'prep-on-behalf-of': 'prep-on-behalf-of-of',
        'prep-out-of': 'prep-out-of-of',
    }
    _deinversions = {
        'mod': 'domain',
    }

    def is_relation_inverted(self, relation):
        """
        Return True if *relation* is inverted.
        """
        return (
            relation in self._deinversions or
            (relation.endswith('-of') and relation not in self._inversions)
        )

    def invert_relation(self, relation):
        """
        Invert or deinvert *relation*.
        """
        if self.is_relation_inverted(relation):
            rel = self._deinversions.get(relation, relation[:-3])
        else:
            rel = self._inversions.get(relation, relation + '-of')
        if rel is None:
             raise PenmanError(
                'Cannot (de)invert {}; not allowed'.format(relation)
            )
        return rel


class Triple(namedtuple('Triple', ('source', 'relation', 'target'))):
    """Container for Graph edges and node attributes."""
    def __new__(cls, source, relation, target, inverted=None):
        t = super(Triple, cls).__new__(
            cls, source, relation, target
        )
        t.inverted = inverted
        return t


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

    def __init__(self, data=None, top=None):
        """
        Create a Graph from an iterable of triples.

        Args:
            data: an iterable of triples (Triple objects or 3-tuples)
            top: the node identifier of the top node; if unspecified,
                the source of the first triple is used
        Example:

            >>> Graph([
            ...     ('b', 'instance', 'bark'),
            ...     ('d', 'instance', 'dog'),
            ...     ('b', 'ARG1', 'd')
            ... ])
        """
        self._triples = []
        self._top = None

        if data is None:
            data = []
        else:
            data = list(data)  # make list (e.g., if its a generator)

        if data:
            self._triples.extend(
                Triple(*t, inverted=getattr(t, 'inverted', None))
                for t in data
            )
            # implicit top: source of first triple
            if top is None:
                top = data[0][0]
            self.top = top

    def __repr__(self):
        return '<{} object (top={}) at {}>'.format(
            self.__class__.__name__,
            self.top,
            id(self)
        )

    def __str__(self):
        return PENMANCodec().encode(self)  # just use the default encoder

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
        return set(v for v, _, _ in self._triples)

    def triples(self, source=None, relation=None, target=None):
        """
        Return triples filtered by their *source*, *relation*, or *target*.
        """
        triplematch = lambda t: (
            (source is None or source == t.source) and
            (relation is None or relation == t.relation) and
            (target is None or target == t.target)
        )
        return list(filter(triplematch, self._triples))

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

    def reentrancies(self):
        """
        Return a mapping of variables to their re-entrancy count.

        A re-entrancy is when more than one edge selects a node as its
        target. These graphs are rooted, so the top node always has an
        implicit entrancy. Only nodes with re-entrancies are reported,
        and the count is only for the entrant edges beyond the first.
        Also note that these counts are for the interpreted graph, not
        for the linearized form, so inverted edges are always
        re-entrant.
        """
        entrancies = defaultdict(int)
        entrancies[self.top] += 1  # implicit entrancy to top
        for t in self.edges():
            entrancies[t.target] += 1
        return dict((v, cnt - 1) for v, cnt in entrancies.items() if cnt >= 2)


def _regex(x, s, pos, msg):
    m = x.match(s, pos=pos)
    if m is None:
        raise DecodeError('Expected {}'.format(msg), string=s, pos=pos)
    return m


def _default_cast(x):
    if isinstance(x, basestring):
        if x.startswith('"'):
            x = x  # strip quotes?
        elif re.match(
                r'-?(0|[1-9]\d*)(\.\d+[eE][-+]?|\.|[eE][-+]?)\d+$', x):
            x = float(x)
        elif re.match(r'-?\d+$', x):
            x = int(x)
    return x


class PenmanError(Exception):
    """Base class for errors in the Penman package."""


class EncodeError(PenmanError):
    """Raises when encoding PENMAN-notation fails."""


class DecodeError(PenmanError):
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

        >>> encode(Graph([('h', 'instance', 'hi')]))
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


def _main():
    import sys
    from docopt import docopt
    args = docopt(USAGE, version='Penman {}'.format(__version__))

    infile = args['--input'] or sys.stdin
    outfile = args['--output'] or sys.stdout

    codec = AMRCodec if args['--amr'] else PENMANCodec

    indent = True
    if args['--indent']:
        if args['--indent'].lower() in ("no", "none", "false"):
            indent = False
        else:
            try:
                indent = int(args['--indent'])
                if indent < 0:
                    raise ValueError
            except ValueError:
                sys.exit('error: --indent value must be "no" or a '
                         ' positive integer')

    data = load(infile, cls=codec)
    dump(data, outfile, triples=args['--triples'], cls=codec, indent=indent)


if __name__ == '__main__':
    _main()
