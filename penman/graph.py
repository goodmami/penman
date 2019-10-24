# -*- coding: utf-8 -*-

"""
Data structures for Penman graphs and triples.
"""

from typing import (
    Union, Iterable, Optional, Mapping, Any,
    List, Tuple, Dict, Set, NamedTuple)
from collections import defaultdict

from penman.exceptions import GraphError


_Identifier = str
_Constant = Union[str, float, int]
_Role = str                                    # '' for anonymous relations
_Target = Union[_Identifier, _Constant, None]  # None for untyped nodes
_Variables = Set[_Identifier]

# This type-checks with basic tuples, unlike Triple below
BasicTriple = Tuple[_Identifier, _Role, _Target]
_Triples = Iterable[BasicTriple]

# These are the main data containers on graphs
_Metadata = Mapping[str, str]


class Epidatum(object):
    __slots__ = ()

    #: The `mode` attribute specifies what the Epidatum annotates:
    #:
    #:  * `mode=0` -- unspecified
    #:  * `mode=1` -- role epidata
    #:  * `mode=2` -- target epidata
    mode = 0


_Epidata = Mapping[BasicTriple, List[Epidatum]]

# Tree types
Branch = Tuple[_Role, Any, List[Epidatum]]
Tree = Tuple[_Identifier, List[Branch]]


class Triple(NamedTuple):
    """
    A relation between nodes or between a node and an constant.

    Args:
        source: the source node identifier of the triple
        role: the relation between the source and target
        target: the target node identifier or constant
    """

    source: _Identifier
    """The source node identifier of the triple."""

    role: _Role
    """The relation (edge label) between the source and target."""

    target: _Target
    """The target node identifier or constant."""


class Edge(Triple):
    """A relation between nodes."""

    target: _Identifier
    """The target node identifier."""


class Attribute(Triple):
    """A relation between a node and a constant."""

    target: _Constant
    """The target constant."""


class Graph(object):
    """
    A basic class for modeling a rooted, directed acyclic graph.

    A Graph is defined by a list of triples, which can be divided into
    two parts: a list of graph edges where both the source and target
    are node identifiers, and a list of node attributes where only the
    source is a node identifier and the target is a constant. These
    lists can be obtained via the :meth:`triples`, :meth:`edges`, and
    :meth:`attributes` methods.

    Args:
        triples: an iterable of triples (:class:`Triple` or 3-tuples)
        top: the node identifier of the top node; if unspecified,
            the source of the first triple is used
        epidata: a mapping of triples to epigraphical markers
        metadata: a mapping of metadata types to descriptions
    Example:
        >>> Graph([('b', 'instance', 'bark'),
        ...        ('d', 'instance', 'dog'),
        ...        ('b', 'ARG1', 'd')])
    """

    def __init__(self,
                 triples: _Triples = None,
                 top: _Identifier = None,
                 epidata: _Epidata = None,
                 metadata: _Metadata = None):
        if not triples:
            triples = []
        if not epidata:
            epidata = {}
        if not metadata:
            metadata = {}

        # the following (a) creates a new list and (b) validates that
        # they are triples
        self._triples = [(src, role, tgt) for src, role, tgt in triples]
        self._top = top
        self.epidata = epidata
        self.metadata = metadata

    def __repr__(self):
        return '<{} object (top={}) at {}>'.format(
            self.__class__.__name__,
            self.top,
            id(self)
        )


    @property
    def top(self) -> Union[_Identifier, None]:
        """
        The top variable.
        """
        top = self._top
        if top is None and len(self._triples) > 0:
            top = self._triples[0][0]  # implicit top
        return top

    @top.setter
    def top(self, top: Union[_Identifier, None]):
        if top is not None and top not in self.variables():
            raise GraphError('top must be a valid node')
        self._top = top  # check if top is valid variable?

    def variables(self) -> _Variables:
        """
        Return the set of variables (nonterminal node identifiers).
        """
        return set(src for src, _, _ in self._triples)

    def triples(self,
                source: _Identifier = None,
                role: _Role = None,
                target: _Target = None) -> List[Triple]:
        """
        Return triples filtered by their *source*, *role*, or *target*.
        """
        variables = self.variables()
        triples = [Edge(*t) if t[2] in variables else Attribute(*t)
                   for t in self._filter_triples(
                           None, source, role, target, variables)]
        return triples

    def edges(self,
              source: Optional[_Identifier] = None,
              role: _Role = None,
              target: _Identifier = None) -> List[Edge]:
        """
        Return edges filtered by their *source*, *role*, or *target*.

        Edges don't include terminal triples (node types or attributes).
        """
        triples = [Edge(*t)
                   for t in self._filter_triples(True, source, role, target)]
        return triples

    def attributes(self,
                   source: Optional[_Identifier] = None,
                   role: _Role = None,
                   target: _Constant = None) -> List[Attribute]:
        """
        Return attributes filtered by their *source*, *role*, or *target*.

        Attributes don't include triples where the target is a nonterminal.
        """
        triples = [Attribute(*t)
                   for t in self._filter_triples(False, source, role, target)]
        return triples

    def _filter_triples(self,
                        is_edge: Union[bool, None],
                        source: Optional[_Identifier],
                        role: Optional[_Role],
                        target: Optional[_Target],
                        variables: _Variables = None) -> List[BasicTriple]:
        """
        Filter triples based on their source, role, and/or target.
        """
        if is_edge is source is role is target is None:
            triples = list(self._triples)
        else:
            if variables is None:
                variables = self.variables()
            triples = [
                t for t in self._triples
                if ((is_edge is None or (t[2] in variables) == is_edge)
                    and (source is None or source == t[0])
                    and (role is None or role == t[1])
                    and (target is None or target == t[2]))
            ]

        return triples

    def reentrancies(self) -> Dict[_Identifier, int]:
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
        entrancies: Dict[_Identifier, int] = defaultdict(int)
        if self.top is not None:
            entrancies[self.top] += 1  # implicit entrancy to top
        for t in self.edges():
            entrancies[t.target] += 1
        return dict((v, cnt - 1) for v, cnt in entrancies.items() if cnt >= 2)


def clear_epidata(g, epidata_class=None):
    """
    Remove all epigraphical data in *g*.

    If *epidata_class* is given and is not `None`, only subtypes of
    *epidata_class* will be removed.
    """
    for epilist in g.epidata.values():
        if epidata_class is not None:
            epilist[:] = [epi for epi in epilist
                          if not isinstance(epi, epidata_class)]
        else:
            epilist[:] = []
