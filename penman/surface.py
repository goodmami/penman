# -*- coding: utf-8 -*-

"""
Surface strings, tokens, and alignments.
"""

from typing import TypeVar, Type, Mapping, Tuple

from penman.types import BasicTriple
from penman.graph import Graph
from penman.epigraph import Epidatum
from penman.exceptions import SurfaceError


T = TypeVar('T', bound='AlignmentMarker')  # for classmethods


class AlignmentMarker(Epidatum):

    __slots__ = 'indices', 'prefix',

    def __init__(self, indices: Tuple[int, ...], prefix: str = None):
        super().__init__()
        self.indices = indices
        self.prefix = prefix

    @classmethod
    def from_string(cls: Type[T], s: str) -> T:
        """
        Instantiate the alignment marker from its string *s*.

        Examples:
            >>> from penman import surface
            >>> surface.Alignment.from_string('1')
            Alignment((1,))
            >>> surface.RoleAlignment.from_string('e.2,3')
            RoleAlignment((2, 3), prefix='e.')
        """

        _s = s.lstrip('~')
        prefix = None
        try:
            if _s[0].isalpha():  # ...~e
                i = 1
                if _s[1] == '.':  # ...~e.
                    i = 2
                prefix = _s[0:i]
                _s = _s[i:]
        except IndexError as exc:
            raise SurfaceError(
                f'invalid alignment marker: {s!r}'
            ) from exc

        try:
            indices = tuple(map(int, _s.split(',')))
        except ValueError as exc:
            raise SurfaceError(
                f'invalid alignments: {s!r}'
            ) from exc

        return cls(indices, prefix=prefix)

    def __repr__(self):
        args = repr(self.indices)
        if self.prefix:
            args += f', prefix={self.prefix!r}'
        name = type(self).__name__
        return f'{name}({args})'

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


_Alignments = Mapping[BasicTriple, AlignmentMarker]


def alignments(g: Graph) -> _Alignments:
    """
    Return a mapping of triples to alignments in graph *g*.

    Args:
        g: a :class:`~penman.graph.Graph` containing alignment data
    Returns:
        A :class:`dict` mapping :class:`~penman.graph.Triple` objects
        to their corresponding :class:`Alignment` objects, if any.
    Example:
        >>> from penman import decode
        >>> from penman import surface
        >>> g = decode(
        ...   '(c / chase-01~4'
        ...   '   :ARG0~5 (d / dog~7)'
        ...   '   :ARG0~3 (c / cat~2))')
        >>> surface.alignments(g)  # doctest: +NORMALIZE_WHITESPACE
        {('c', ':instance', 'chase-01'): Alignment((4,)),
         ('d', ':instance', 'dog'): Alignment((7,)),
         ('c', ':instance', 'cat'): Alignment((2,))}
    """
    return _get_alignments(g, Alignment)


def role_alignments(g: Graph) -> _Alignments:
    """
    Return a mapping of triples to role alignments in graph *g*.

    Args:
        g: a :class:`~penman.graph.Graph` containing role alignment
        data
    Returns:
        A :class:`dict` mapping :class:`~penman.graph.Triple` objects
        to their corresponding :class:`RoleAlignment` objects, if any.
    Example:
        >>> from penman import decode
        >>> from penman import surface
        >>> g = decode(
        ...   '(c / chase-01~4'
        ...   '   :ARG0~5 (d / dog~7)'
        ...   '   :ARG0~3 (c / cat~2))')
        >>> surface.role_alignments(g)  # doctest: +NORMALIZE_WHITESPACE
        {('c', ':ARG0', 'd'): RoleAlignment((5,)),
         ('c', ':ARG0', 'c'): RoleAlignment((3,))}
    """
    return _get_alignments(g, RoleAlignment)


def _get_alignments(g: Graph,
                    alignment_type: Type[AlignmentMarker]) -> _Alignments:
    alns = {}
    triple = None
    for triple, epidata in g.epidata.items():
        for epidatum in epidata:
            if isinstance(epidatum, alignment_type):
                alns[triple] = epidatum
    return alns
