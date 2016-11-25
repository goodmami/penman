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
#    - Triple.is_inverted()
#  * Graph(triples, comment=None)
#    - Graph.from_penman(string)
#    - Graph.to_penman(top=None, indent=True)
#    - Graph.from_triples(triples, top=None)
#    - Graph.to_triples(normalize=False)
#    - Graph.top
#    - Graph.variables()
#    - Graph.concepts()
#    - Graph.constants()
#    - Graph.edges(source=None, relation=None, target=None)
#
# Module Functions:
#  * load(source, triples=False, **kwargs)
#  * loads(string, triples=False, **kwargs)
#  * dump(file, graphs, triples=False, **kwargs)
#  * dumps(graphs, triples=False, **kwargs)
#  * is_relation_inverted(relation)
#  * invert_relation(relation)
#
# Module Variables:
#  * TOP
#  * TOP_RELATION
#

from __future__ import print_function

from collections import namedtuple, defaultdict

__version__ = '0.3.0'
__version_info__ = __version__.replace('.', ' ').replace('-', ' ').split()

TOP = 'TOP'
TOP_RELATION = 'TOP'


def is_relation_inverted(relation):
    """
    Return True if *relation* is inverted.
    """
    return relation.endswith('-of')  # and relation != 'instance-of'


def invert_relation(relation):
    """
    Invert or deinvert *relation*.
    """
    return relation[:-3] if is_relation_inverted(relation) else relation+'-of'


def _invert(triple):
    return Triple(
        triple.target,
        invert_relation(triple.relation),
        triple.source
    )


class Triple(namedtuple('Triple', ('source', 'relation', 'target'))):
    """
    Basic container for triple data.
    """

    def is_inverted(self):
        """
        Return True if the triple is inverted.
        """
        return is_relation_inverted(self.relation)


class Graph(object):
    """
    A basic class for modeling a directed acyclic graph.
    """

    def __init__(self):
        self._triples = []
        self._top = None
        self._inv_weights = {}

    def __str__(self):
        return self.to_penman()

    @classmethod
    def from_penman(cls, string):
        """
        Create a Graph from a string in the PENMAN format.
        """
        toks, _, depth = _lex_penman(string)
        if depth > 0:
            raise ValueError('incomplete graph: {}'.format(string))
        return _parse_penman(toks)

    @classmethod
    def from_triples(cls, triples, top=None):
        """
        Create a Graph from an iterable of triples.
        """
        graph = cls()
        graph._top = top
        for source, relation, target in triples:
            if graph._top is None:  # implicit top (first unnormalized triple)
                graph._top = source
            if source == TOP and relation == TOP_RELATION:  # explicit top
                graph._top = target
            else:
                # if is_relation_inverted(relation):
                #     source, target = target, source
                #     relation = relation[:-3]
                #     inv_weight = 0.0
                # else:
                #     inv_weight = 1.0
                graph._triples.append(Triple(source, relation, target))
        return graph

    @property
    def top(self):
        """
        Return the top variable.
        """
        return self._top

    @top.setter
    def top(self, top):
        self._top = top  # check if top is valid variable?

    def variables(self):
        """
        Return the list of variables (nonterminal node identifiers).
        """
        variables = set()
        for source, relation, target in self._triples:
            if ((is_relation_inverted(relation) and relation != 'instance-of')
                    or relation == 'instance'):
                source = target
            variables.add(source)
        return variables

    # def instances(self, concept=None):
    #     """
    #     Return the set of variables that are instances of a concept.
    #     """
    #     instances = set()
    #     for triple in self._triples:
    #         if triple.relation == 'instance-of':
    #             if concept is None or concept == triple.target:
    #                 instances.add(triple.source)
    #         elif triple.relation == 'instance':
    #             if concept is None or concept == triple.source:
    #                 instances.add(triple.target)
    #     return instances

    def concepts(self):
        """
        Return the set of concepts in the graph.
        """
        concepts = set()
        for triple in self._triples:
            if triple.relation == 'instance-of':
                concepts.add(triple.target)
            elif triple.relation == 'instance':
                concepts.add(triple.source)
        return concepts

    def constants(self):
        """
        Return the non-instance terminal nodes.
        """
        constants = []
        variables = self.variables()
        for triple in self._triples:
            if triple.relation in ('instance-of', 'instance'):
                continue
            if triple.is_inverted():
                if triple.source not in variables:
                    constants.append(triple.source)
            elif triple.target not in variables:
                constants.append(triple.target)
        return constants

    def edges(self, source=None, relation=None, target=None):
        """
        Return edges filtered by their *source*, *relation*, or *target*.
        Edges don't include node labels (instance-of relations).
        """
        edges = []
        for triple in self._triples:
            src, rln, tgt = triple
            if triple.is_inverted():
                src, rln, tgt = tgt, invert_relation(rln), src
            if ((source is None or source == src) and
                    (relation is None or relation == rln) and
                    (target is None or target == tgt)):
                edges.append((src, rln, tgt))
        return edges

    def to_penman(self, top=None, indent=True):
        """
        Serialize the graph to PENMAN and return the string.

        Args:
          top: the node identifier of the top of the graph
          indent: if True, adaptively indent; if False or None,
                  don't indent; if a non-negative integer, indent
                  that many spaces per nesting level
        """
        if top is None:
            top = self._top
        if indent is False:
            indent = None
        return _serialize_penman(self._triples, top, indent)

    def to_triples(self, normalize=False):
        """
        Return a list of triples.

        Args:
            normalize: if True, ensure all triples are uninverted
        """
        triples = []
        # if self._top is not None:
        #     triples.append()
        for triple in self._triples:
            if normalize and triple.is_inverted():
                triple = _invert(triple)
            triples.append(triple)
        return triples


def load(source, triples=False, **kwargs):
    """
    Deserialize a list of PENMAN-encoded graphs from *source*.
    """
    read = _read_triples if triples else _read_penman
    if hasattr(source, 'read'):
        return list(read(source, **kwargs))
    else:
        with open(source) as fh:
            return list(read(fh, **kwargs))


def loads(string, triples=False, **kwargs):
    """
    Deserialize a list of PENMAN-encoded graphs from *string*.
    """
    lines = string.splitlines()
    if triples:
        graphs = _read_triples(lines, **kwargs)
    else:
        graphs = _read_penman(lines, **kwargs)
    return list(graphs)


def dump(file, graphs, triples=False, **kwargs):
    """
    Serialize each graph in *graphs* to PENMAN and write to *file*.
    """
    text = dumps(graphs, triples=triples, **kwargs)

    if hasattr(file, 'write'):
        print(text, file=file)
    else:
        with open(file, 'w') as fh:
            print(text, file=fh)


def dumps(graphs, triples=False, **kwargs):
    """
    Serialize each graph in *graphs* to the PENMAN format.
    """
    if triples:
        strings = [
            _serialize_triples(
                g.to_triples(normalize=kwargs.get('normalize', False))
            )
            for g in graphs
        ]
    else:
        strings = [
            g.to_penman(top=kwargs.get('top'), indent=kwargs.get('indent', True))
            for g in graphs
        ]
    return '\n\n'.join(strings) + '\n'


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
        if c in ' (:,)"/\n\t\r\v\f':  # breaking characters ("," for triples)
            if start < i:
                toks.append(s[start:i])
            if c in '():/,':  # basic punctuation
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
    nodestack = [TOP]
    reln = TOP_RELATION
    triples = []
    while toks:
        tok = toks.pop()
        if tok == '(':
            var = toks.pop()
            triples.append(Triple(nodestack[-1], reln, var))
            nodestack.append(var)
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


def _serialize_penman(triples, top, indent, weights=None):
    if weights is None:
        weights = _default_inversion_weights(triples)
    g = defaultdict(list)
    remaining = set()
    for idx, triple in enumerate(triples):
        g[triple.source].append((triple, triple, 0.0, idx))
        g[triple.target].append((_invert(triple), triple, weights[triple], idx))
        remaining.add(triple)
    p = _walk(g, top, remaining)
    return _layout(p, top, indent, 0, set())


def _default_inversion_weights(triples):
    """
    Default to a high weight for inverting :instance-of or any that
    never appear as a source (e.g. :polarity -, not (- :polarity-of ...)
    """
    wts = {}
    srcs = set()
    for t in triples:
        if t.relation not in ('instance-of', 'instance'):
            srcs.add(t.target if t.is_inverted() else t.source)
    for t in triples:
        if t.relation == 'instance-of':
            wts[t] = 2.0
        elif t.relation == 'instance':
            wts[t] = 0.0
        elif t.target not in srcs:
            wts[t] = 2.0
        else:
            wts[t] = 1.0
    return wts


def _walk(graph, var, remaining):
    path = defaultdict(list)
    candidates = [
        # e, t, w, o = edge, triple, weight, original-order
        (e, t, w, o) for e, t, w, o in graph.get(var, []) if t in remaining
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


def _layout(g, v, indent, offset, seen):
    if v not in g or len(g.get(v, [])) == 0 or v in seen:
        return v
    seen.add(v)
    branches = []
    outedges = sorted(
        g[v],
        key=lambda e: (-e.relation.startswith('instance'),
                       e.is_inverted())
    )
    head = '({} '.format(v)
    if indent is True:
        offset += len(head)
    elif indent is not None and indent is not False:
        offset += indent
    for edge in outedges:
        rel = '/' if edge.relation == 'instance-of' else ':' + edge.relation
        inner_offset = (len(rel) + 1) if indent is True else 0
        branch = _layout(g, edge.target, indent, offset + inner_offset, seen)
        branches.append('{} {}'.format(rel, branch))
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
                    yield Graph.from_triples(triples)
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
    args = docopt(__doc__, version='Penman {}'.format(__version__))

    infile = args['--input'] or sys.stdin
    data = load(infile)

    outfile = args['--output'] or sys.stdout
    dump(outfile, data, triples=args['--triples'])


if __name__ == '__main__':
    _main()
