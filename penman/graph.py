# -*- coding: utf-8 -*-

"""
Data structures for Penman graphs and triples.
"""

from typing import (
    Union, Iterable, Optional, Mapping, Any,
    List, Tuple, Dict, Set, NamedTuple)

from collections import defaultdict


_Identifier = str
_Constant = Union[str, float, int]
_Role = str                                    # '' for anonymous relations
_Target = Union[_Identifier, _Constant, None]  # None for untyped nodes

# This type-checks with basic tuples, unlike Triple below
BasicTriple = Tuple[_Identifier, _Role, _Target]

# These are the main data containers on graphs
# _Data = Iterable[BasicTriple]
_Metadata = Mapping[str, str]


class Epidatum(object):
    __slots__ = ()

    #: The `mode` attribute specifies what the Epidatum annotates:
    #:
    #:  * `mode=0` -- unspecified
    #:  * `mode=1` -- role epidata
    #:  * `mode=2` -- target epidata
    mode = 0

Datum = Union[BasicTriple, Epidatum]
_Data = Iterable[Datum]
_Epidata = Mapping[BasicTriple, List[Epidatum]]


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
        data: an iterable of triples (:class:`Triple` or 3-tuples)
        top: the node identifier of the top node; if unspecified,
            the source of the first triple is used
        alignments: a mapping of ISI-style surface alignments (triples
            to token indices) for nodes
        role_alignments: a mapping of ISI-style surface alignments
            (triples to token indices) for roles
    Example:
        >>> Graph([('b', 'instance', 'bark'),
        ...        ('d', 'instance', 'dog'),
        ...        ('b', 'ARG1', 'd')])
    """

    def __init__(self,
                 data: _Data,
                 top: _Identifier = None,
                 epidata: _Epidata = None,
                 metadata: _Metadata = None):
        # split triples and epidata
        if not epidata:
            epidata = {}
        triples = []
        current = None
        for datum in data:
            if isinstance(datum, Epidatum):
                if current not in epidata:
                    epidata[current] = []
                epidata[current].append(datum)
            else:
                triples.append(datum)
                current = datum

        if not triples and not top:
            raise ValueError('Cannot instantiate an empty Graph')

        ids = [t[0] for t in triples]
        if top is None:
            top = ids[0]  # implicit top: source of first triple
        elif len(ids) == 0:
            ids = [top]
        if not metadata:
            metadata = {}

        self._triples = triples
        self._variables = set(ids)
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
    def data(self) -> List[Datum]:
        data = []
        for triple in self._triples:
            data.append(triple)
            data.extend(self.epidata.get(triple, []))
        return data

    @property
    def top(self) -> _Identifier:
        """
        The top variable.
        """
        return self._top

    @top.setter
    def top(self, top: _Identifier):
        if top not in self._variables:
            raise ValueError('top must be a valid node')
        self._top = top  # check if top is valid variable?

    def variables(self) -> Set[_Identifier]:
        """
        Return the set of variables (nonterminal node identifiers).
        """
        return set(self._variables)

    def triples(self,
                source: _Identifier = None,
                role: _Role = None,
                target: _Target = None) -> List[Triple]:
        """
        Return triples filtered by their *source*, *role*, or *target*.
        """
        variables = self._variables
        triples = [Edge(*t) if t[2] in variables else Attribute(*t)
                   for t in self._filter_triples(None, source, role, target)]
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
                        target: Optional[_Target]) -> List[BasicTriple]:
        """
        Filter triples based on their source, role, and/or target.
        """
        if is_edge is source is role is target is None:
            triples = list(self._triples)
        else:
            variables = self._variables

            def triplematch(t: BasicTriple) -> bool:
                return ((is_edge is None or (t[2] in variables) == is_edge)
                        and (source is None or source == t[0])
                        and (role is None or role == t[1])
                        and (target is None or target == t[2]))

            triples = list(filter(triplematch, self._triples))

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
        entrancies[self.top] += 1  # implicit entrancy to top
        for t in self.edges():
            entrancies[t.target] += 1
        return dict((v, cnt - 1) for v, cnt in entrancies.items() if cnt >= 2)


Branch = Tuple[_Role, Optional[Epidatum],
               Union[_Target, 'Tree'], Optional[Epidatum]]
Tree = Tuple[_Identifier, List[Branch], List[Branch]]


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
