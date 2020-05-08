# -*- coding: utf-8 -*-

"""
Data structures for Penman graphs and triples.
"""

from typing import (Union, Optional, Mapping, List, Dict, Set, NamedTuple)
from collections import defaultdict
import copy

from penman.exceptions import GraphError
from penman.types import (
    Variable,
    Constant,
    Role,
    Target,
    BasicTriple,
    Triples,
)
from penman.epigraph import Epidata


CONCEPT_ROLE = ':instance'


class Triple(NamedTuple):
    """
    A relation between nodes or between a node and an constant.

    Args:
        source: the source variable of the triple
        role: the edge label between the source and target
        target: the target variable or constant
    """

    source: Variable
    """The source variable of the triple."""

    role: Role
    """The edge label between the source and target."""

    target: Target
    """The target variable or constant."""


class Instance(Triple):
    """A relation indicating the concept of a node."""

    target: Constant
    """The node concept."""


class Edge(Triple):
    """A relation between nodes."""

    target: Variable
    """The target variable."""


class Attribute(Triple):
    """A relation between a node and a constant."""

    target: Constant
    """The target constant."""


class Graph(object):
    """
    A basic class for modeling a rooted, directed acyclic graph.

    A Graph is defined by a list of triples, which can be divided into
    two parts: a list of graph edges where both the source and target
    are variables (node identifiers), and a list of node attributes
    where only the source is a variable and the target is a
    constant. The raw triples are available via the :attr:`triples`
    attribute, while the :meth:`instances`, :meth:`edges` and
    :meth:`attributes` methods return only those that are concept
    relations, relations between nodes, or relations between a node
    and a constant, respectively.

    Args:
        triples: an iterable of triples (:class:`Triple` or 3-tuples)
        top: the variable of the top node; if unspecified, the source
            of the first triple is used
        epidata: a mapping of triples to epigraphical markers
        metadata: a mapping of metadata types to descriptions
    Example:
        >>> from penman.graph import Graph
        >>> Graph([('b', ':instance', 'bark-01'),
        ...        ('d', ':instance', 'dog'),
        ...        ('b', ':ARG0', 'd')])
        <Graph object (top=b) at ...>
    """

    def __init__(self,
                 triples: Triples = None,
                 top: Variable = None,
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
        name = self.__class__.__name__
        return f'<{name} object (top={self.top}) at {id(self)}>'

    def __str__(self):
        triples = '[{}]'.format(',\n   '.join(map(repr, self.triples)))
        epidata = '{{{}}}'.format(',\n    '.join(
            map('{0[0]!r}: {0[1]!r}'.format, self.epidata.items())))
        return f'Graph(\n  {triples},\n  epidata={epidata})'

    def __eq__(self, other):
        if not isinstance(other, Graph):
            return NotImplemented
        return (self.top == other.top
                and len(self.triples) == len(other.triples)
                and set(self.triples) == set(other.triples))

    def __or__(self, other):
        if isinstance(other, Graph):
            g = copy.deepcopy(self)
            g.metadata.clear()
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
            g = copy.deepcopy(self)
            g.metadata.clear()
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
    def top(self) -> Union[Variable, None]:
        """
        The top variable.
        """
        top = self._top
        if top is None and len(self.triples) > 0:
            top = self.triples[0][0]  # implicit top
        return top

    @top.setter
    def top(self, top: Union[Variable, None]):
        if top is not None and top not in self.variables():
            raise GraphError('top must be a valid node')
        self._top = top  # check if top is valid variable?

    def variables(self) -> Set[Variable]:
        """
        Return the set of variables (nonterminal node identifiers).
        """
        vs = set(src for src, _, _ in self.triples)
        if self._top is not None:
            vs.add(self._top)
        return vs

    def instances(self) -> List[Instance]:
        """
        Return instances (concept triples).
        """
        return [Instance(*t)
                for t in self._filter_triples(None, CONCEPT_ROLE, None)]

    def edges(self,
              source: Optional[Variable] = None,
              role: Role = None,
              target: Variable = None) -> List[Edge]:
        """
        Return edges filtered by their *source*, *role*, or *target*.

        Edges don't include terminal triples (concepts or attributes).
        """
        variables = self.variables()
        return [Edge(*t)
                for t in self._filter_triples(source, role, target)
                if t[1] != CONCEPT_ROLE and t[2] in variables]

    def attributes(self,
                   source: Optional[Variable] = None,
                   role: Role = None,
                   target: Constant = None) -> List[Attribute]:
        """
        Return attributes filtered by their *source*, *role*, or *target*.

        Attributes don't include concept triples or those where the
        target is a nonterminal.
        """
        variables = self.variables()
        return [Attribute(*t)
                for t in self._filter_triples(source, role, target)
                if t[1] != CONCEPT_ROLE and t[2] not in variables]

    def _filter_triples(self,
                        source: Optional[Variable],
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

    def reentrancies(self) -> Dict[Variable, int]:
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
        entrancies: Dict[Variable, int] = defaultdict(int)
        if self.top is not None:
            entrancies[self.top] += 1  # implicit entrancy to top
        for t in self.edges():
            entrancies[t.target] += 1
        return dict((v, cnt - 1) for v, cnt in entrancies.items() if cnt >= 2)


def _ensure_colon(role):
    if not role.startswith(':'):
        return ':' + role
    return role
