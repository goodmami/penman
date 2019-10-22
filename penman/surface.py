# -*- coding: utf-8 -*-

"""
Surface strings, tokens, and alignments.
"""

from typing import Type, Union, Mapping, Tuple, List

from penman import graph
from penman.exceptions import SurfaceError


class AlignmentMarker(graph.Epidatum):

    __slots__ = 'indices', 'prefix',

    def __init__(self, indices: Tuple[int, ...], prefix: str = None):
        super().__init__()
        self.indices = indices
        self.prefix = prefix

    def __repr__(self):
        args = repr(self.indices)
        if self.prefix:
            args += ', prefix={}'.format(repr(self.prefix))
        return '{}({})'.format(type(self).__name__, args)

    def __str__(self):
        return '~{}{}'.format(self.prefix or '',
                              ','.join(map(str, self.indices)))

    def __eq__(self, other):
        if not isinstance(other, AlignmentMarker):
            return False
        return (self.prefix == other.prefix
                and self.indices == other.indices)


class Alignment(AlignmentMarker):
    __slots__ = ()
    mode = 2


class RoleAlignment(AlignmentMarker):
    __slots__ = ()
    mode = 1


_Alignments = Mapping[graph.Triple, AlignmentMarker]


def alignments(g: graph.Graph) -> _Alignments:
    """
    Return a mapping of triples to alignments in graph *g*.

    Args:
        g: a :class:`Graph` containing alignment data
    Returns:
        A :class:`dict` mapping :class:`Triple` objects to their
        corresponding :class:`Alignment` objects, if any.
    """
    return _get_alignments(g, Alignment)


def role_alignments(g: graph.Graph) -> _Alignments:
    """
    Return a mapping of triples to role alignments in graph *g*.

    Args:
        g: a :class:`Graph` containing role alignment data
    Returns:
        A :class:`dict` mapping :class:`Triple` objects to their
        corresponding :class:`RoleAlignment` objects, if any.
    """
    return _get_alignments(g, RoleAlignment)


def _get_alignments(g: graph.Graph,
                    alignment_type: Type[AlignmentMarker]) -> _Alignments:
    alns = {}
    triple = None
    for triple, epidata in g.epidata.items():
        for epidatum in epidata:
            if isinstance(epidatum, alignment_type):
                alns[triple] = epidatum
    return alns
