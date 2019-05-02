# -*- coding: utf-8 -*-

from operator import itemgetter
from collections import defaultdict


class Triple(tuple):
    """
    Container for Graph edges and node attributes.

    The final parameter, `inverted`, is optional, and when set it
    exists as an attribute of the Triple object, but not as part of
    the 3-tuple data.  It is used to store the intended or original
    orientation of the triple (i.e. whether it was true or
    inverted). If unset, preference during serialization is for a true
    orientation.

    Args:
        source: the source node of the triple
        relation: the relation between the source and target
        target: the target node or attribute
        inverted: the preferred orientation is inverted if `True`,
            uninverted if `False`, and no preference if `None`
    Attributes:
        source: the source node of the triple
        relation: the relation between the source and target
        target: the target node or attribute
        inverted: the preferred orientation is inverted if `True`,
            uninverted if `False`, and no preference if `None`
    """

    def __new__(cls, source, relation, target, inverted=None):
        t = super().__new__(cls, (source, relation, target))
        t._inverted = inverted
        return t

    source = property(itemgetter(0))
    relation = property(itemgetter(1))
    target = property(itemgetter(2))

    @property
    def inverted(self):
        return self._inverted


class Graph(object):
    """
    A basic class for modeling a rooted, directed acyclic graph.

    A Graph is defined by a list of triples, which can be divided into
    two parts: a list of graph edges where both the source and target
    are node identifiers, and a list of node attributes where only the
    source is a node identifier and the target is a constant. These
    lists can be obtained via the Graph.triples(), Graph.edges(), and
    Graph.attributes() methods.

    Args:
        data: an iterable of triples (Triple objects or 3-tuples)
        top: the node identifier of the top node; if unspecified,
            the source of the first triple is used
        alignments: an iterable of ISI
    Example:
        >>> Graph([
        ...     ('b', 'instance', 'bark'),
        ...     ('d', 'instance', 'dog'),
        ...     ('b', 'ARG1', 'd')
        ... ])
    """

    def __init__(self, data=None, top=None,
                 alignments=None, role_alignments=None):
        if data is not None:
            data = list(data)  # make list (e.g., if its a generator)
        if alignments is None:
            alignments = {}
        if role_alignments is None:
            role_alignments = {}

        self._triples = []
        self._variables = []
        self._top = None
        self._alignments = alignments
        self._role_alignments = role_alignments

        if data:
            self._triples.extend(
                Triple(*t, inverted=getattr(t, 'inverted', None))
                for t in data
            )
            self._variables = {v for v, _, _ in self._triples}
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
        if top not in self._variables:
            raise ValueError('top must be a valid node')
        self._top = top  # check if top is valid variable?

    def variables(self):
        """
        Return the list of variables (nonterminal node identifiers).
        """
        return set(self._variables)

    def triples(self, source=None, relation=None, target=None):
        """
        Return triples filtered by their *source*, *relation*, or *target*.
        """
        triples = self._triples
        if not (source is relation is target is None):

            def triplematch(t):
                return ((source is None or source == t.source)
                        and (relation is None or relation == t.relation)
                        and (target is None or target == t.target))

            triples = filter(triplematch, triples)
        return list(triples)

    def edges(self, source=None, relation=None, target=None):
        """
        Return edges filtered by their *source*, *relation*, or *target*.

        Edges don't include terminal triples (node types or attributes).
        """

        def edgematch(e):
            return ((source is None or source == e.source)
                    and (relation is None or relation == e.relation)
                    and (target is None or target == e.target))

        variables = self._variables
        edges = [t for t in self._triples if t.target in variables]
        return list(filter(edgematch, edges))

    def attributes(self, source=None, relation=None, target=None):
        """
        Return attributes filtered by their *source*, *relation*, or *target*.

        Attributes don't include triples where the target is a nonterminal.
        """

        def attrmatch(a):
            return ((source is None or source == a.source)
                    and (relation is None or relation == a.relation)
                    and (target is None or target == a.target))

        variables = self._variables
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

    def alignments(self):
        """
        Return the surface alignments for nodes and attributes.
        """
        return dict(self._alignments)

    def role_alignments(self):
        """
        Return the surface alignments for relations.
        """
        return dict(self._role_alignments)
