# -*- coding: utf-8 -*-

"""
Data structures for Penman graphs and triples.
"""

from typing import (
    Type, TypeVar, Union, Optional, Mapping, List, Dict, NamedTuple)
from collections import defaultdict

from penman.exceptions import GraphError
from penman.types import (
    Identifier,
    IdSet,
    Constant,
    Role,
    Target,
    BasicTriple,
    Triples,
)
from penman.epigraph import (Epidatum, Epidata)


NODETYPE_ROLE = ':instance'


class Triple(NamedTuple):
    """
    A relation between nodes or between a node and an constant.

    Args:
        source: the source node identifier of the triple
        role: the relation between the source and target
        target: the target node identifier or constant
    """

    source: Identifier
    """The source node identifier of the triple."""

    role: Role
    """The relation (edge label) between the source and target."""

    target: Target
    """The target node identifier or constant."""


class Edge(Triple):
    """A relation between nodes."""

    target: Identifier
    """The target node identifier."""


class Attribute(Triple):
    """A relation between a node and a constant."""

    target: Constant
    """The target constant."""


T = TypeVar('T', bound='Graph')  # needed for type-checking Graph.copy()


class Graph(object):
    """
    A basic class for modeling a rooted, directed acyclic graph.

    A Graph is defined by a list of triples, which can be divided into
    two parts: a list of graph edges where both the source and target
    are node identifiers, and a list of node attributes where only the
    source is a node identifier and the target is a constant. The raw
    triples are available via the :attr:`triples` attribute, while the
    :meth:`edges` and :meth:`attributes` methods return only those
    that are edges between nodes or between a node and a constant,
    respectively.

    Args:
        triples: an iterable of triples (:class:`Triple` or 3-tuples)
        top: the node identifier of the top node; if unspecified,
            the source of the first triple is used
        epidata: a mapping of triples to epigraphical markers
        metadata: a mapping of metadata types to descriptions
    Example:
        >>> Graph([('b', ':instance', 'bark'),
        ...        ('d', ':instance', 'dog'),
        ...        ('b', ':ARG1', 'd')])
    """

    def __init__(self,
                 triples: Triples = None,
                 top: Identifier = None,
                 epidata: Mapping[BasicTriple, Epidata] = None,
                 metadata: Mapping[str, str] = None):
        if not triples:
            triples = []
        if not epidata:
            epidata = {}
        if not metadata:
            metadata = {}

        # the following (a) creates a new list (b) validates that
        # they are triples, and (c) ensures roles begin with :
        self.triples = [(src, _ensure_colon(role), tgt)
                        for src, role, tgt in triples]
        self._top = top
        self.epidata = dict(epidata)
        self.metadata = dict(metadata)

    def __repr__(self):
        return '<{} object (top={}) at {}>'.format(
            self.__class__.__name__,
            self.top,
            id(self)
        )

    def __eq__(self, other):
        if not isinstance(other, Graph):
            return NotImplemented
        return (self.top == other.top
                and len(self.triples) == len(other.triples)
                and set(self.triples) == set(other.triples))

    def __or__(self, other):
        if isinstance(other, Graph):
            g = self.copy(epidata=True, metadata=False)
            g |= other
            return g
        else:
            return NotImplemented

    def __ior__(self, other):
        if isinstance(other, Graph):
            new = set(other.triples) - set(self.triples)
            self.triples.extend(t for t in other.triples if t in new)
            for t in new:
                if t in other.epidata:
                    self.epidata[t] = list(other.epidata[t])
            self.epidata.update(other.epidata)
            return self
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Graph):
            g = self.copy(epidata=True, metadata=False)
            g -= other
            return g
        else:
            return NotImplemented

    def __isub__(self, other):
        if isinstance(other, Graph):
            removed = set(other.triples)
            self.triples[:] = [t for t in self.triples if t not in removed]
            for t in removed:
                if t in self.epidata:
                    del self.epidata[t]
            possible_variables = set(v for t in self.triples for v in t[::2])
            if self._top not in possible_variables:
                self._top = None
            return self
        else:
            return NotImplemented

    @property
    def top(self) -> Union[Identifier, None]:
        """
        The top variable.
        """
        top = self._top
        if top is None and len(self.triples) > 0:
            top = self.triples[0][0]  # implicit top
        return top

    @top.setter
    def top(self, top: Union[Identifier, None]):
        if top is not None and top not in self.variables():
            raise GraphError('top must be a valid node')
        self._top = top  # check if top is valid variable?

    def variables(self) -> IdSet:
        """
        Return the set of variables (nonterminal node identifiers).
        """
        vs = set(src for src, _, _ in self.triples)
        if self._top is not None:
            vs.add(self._top)
        return vs

    def edges(self,
              source: Optional[Identifier] = None,
              role: Role = None,
              target: Identifier = None) -> List[Edge]:
        """
        Return edges filtered by their *source*, *role*, or *target*.

        Edges don't include terminal triples (node types or attributes).
        """
        variables = self.variables()
        return [Edge(*t)
                for t in self._filter_triples(source, role, target)
                if t[2] in variables]

    def attributes(self,
                   source: Optional[Identifier] = None,
                   role: Role = None,
                   target: Constant = None) -> List[Attribute]:
        """
        Return attributes filtered by their *source*, *role*, or *target*.

        Attributes don't include triples where the target is a nonterminal.
        """
        variables = self.variables()
        return [Attribute(*t)
                for t in self._filter_triples(source, role, target)
                if t[1] == NODETYPE_ROLE or t[2] not in variables]

    def _filter_triples(self,
                        source: Optional[Identifier],
                        role: Optional[Role],
                        target: Optional[Target]) -> List[BasicTriple]:
        """
        Filter triples based on their source, role, and/or target.
        """
        if source is role is target is None:
            triples = list(self.triples)
        else:
            triples = [
                t for t in self.triples
                if ((source is None or source == t[0])
                    and (role is None or role == t[1])
                    and (target is None or target == t[2]))
            ]
        return triples

    def reentrancies(self) -> Dict[Identifier, int]:
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
        entrancies: Dict[Identifier, int] = defaultdict(int)
        if self.top is not None:
            entrancies[self.top] += 1  # implicit entrancy to top
        for t in self.edges():
            entrancies[t.target] += 1
        return dict((v, cnt - 1) for v, cnt in entrancies.items() if cnt >= 2)

    def copy(self: T, epidata: bool = True, metadata: bool = True) -> T:
        """
        Return a copy of the graph.

        This is a "deep" copy in that mutable substructures are copied
        as well, but immutable ones like individual triples use the
        original instances. Also, epidata may be mutable but copies
        are not created.

        Args:
            epidata: if `True`, include any epidata
            metadata: if `True`, include any metadata
        """
        g = self.__class__(
            list(self.triples),
            top=self.top,
            epidata=None if not epidata else {
                t: list(epis) for t, epis in self.epidata.items()},
            metadata=None if not metadata else dict(self.metadata))
        return g

    def clear(self,
              triples: bool = True,
              epidata: Union[bool, Type[Epidatum]] = True,
              metadata: bool = True) -> None:
        """
        Remove triples, epidata, and/or metadata from the graph.

        If *triples* is `True`, the graph's top will be set to `None`.

        The *epidata* parameter may be a subclass of :class:`Epidatum`,
        in which case only epidata that are subtypes of *epidata* will
        be removed.

        Args:
            triples: if `True`, remove all triples from the graph
            epidata: if `True`, remove all epidata from the graph; if
                a subclass of :class:`Epidatum`, only remove instances
                of that class and its subclasses
            metadata: if `True`, remove all metadata from the graph
        """
        if triples:
            self.triples.clear()
            self._top = None

        if epidata is True or epidata is Epidatum:
            self.epidata.clear()
        else:
            assert isinstance(epidata, Epidatum)
            for epilist in self.epidata.values():
                epilist[:] = [epi for epi in epilist
                              if not isinstance(epi, epidata)]

        if metadata:
            self.metadata.clear()


def _ensure_colon(role):
    if not role.startswith(':'):
        return ':' + role
    return role
