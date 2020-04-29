# -*- coding: utf-8 -*-

"""
Serialization of PENMAN graphs.
"""

from typing import Union, Iterable, Iterator, List

from penman.types import (
    Variable,
    BasicTriple,
)
from penman.tree import Tree
from penman.graph import Graph
from penman.model import Model
from penman._parse import (
    parse,
    iterparse,
    parse_triples,
)
from penman._format import (
    format,
    format_triples,
)
from penman import layout


class PENMANCodec(object):
    """
    An encoder/decoder for PENMAN-serialized graphs.
    """

    def __init__(self, model: Model = None):
        if model is None:
            model = Model()
        self.model = model

    def decode(self, s: str) -> Graph:
        """
        Deserialize PENMAN-notation string *s* into its Graph object.

        Args:
            s: a string containing a single PENMAN-serialized graph
        Returns:
            The :class:`~penman.graph.Graph` object described by *s*.
        Example:
            >>> from penman.codec import PENMANCodec
            >>> codec = PENMANCodec()
            >>> codec.decode('(b / bark-01 :ARG0 (d / dog))')
            <Graph object (top=b) at ...>
        """
        tree = parse(s)
        return layout.interpret(tree, self.model)

    def iterdecode(self,
                   lines: Union[Iterable[str], str]) -> Iterator[Graph]:
        """
        Yield graphs parsed from *lines*.

        Args:
            lines: a string or open file with PENMAN-serialized graphs
        Returns:
            The :class:`~penman.graph.Graph` objects described in
            *lines*.
        """
        for tree in self.iterparse(lines):
            yield layout.interpret(tree, self.model)

    def iterparse(self, lines: Union[Iterable[str], str]) -> Iterator[Tree]:
        """
        Yield trees parsed from *lines*.

        Args:
            lines: a string or open file with PENMAN-serialized graphs
        Returns:
            The :class:`~penman.tree.Tree` object described in
            *lines*.
        """
        yield from iterparse(lines)

    def parse(self, s: str) -> Tree:
        """
        Parse PENMAN-notation string *s* into its tree structure.

        Args:
            s: a string containing a single PENMAN-serialized graph
        Returns:
            The tree structure described by *s*.
        Example:
            >>> from penman.codec import PENMANCodec
            >>> codec = PENMANCodec()
            >>> codec.parse('(b / bark-01 :ARG0 (d / dog))')  # noqa
            Tree(('b', [('/', 'bark-01'), (':ARG0', ('d', [('/', 'dog')]))]))
        """
        return parse(s)

    def parse_triples(self, s: str) -> List[BasicTriple]:
        """ Parse a triple conjunction from *s*."""
        return parse_triples(s)

    def encode(self,
               g: Graph,
               top: Variable = None,
               indent: Union[int, None] = -1,
               compact: bool = False) -> str:
        """
        Serialize the graph *g* into PENMAN notation.

        Args:
            g: the Graph object
            top: if given, the node to use as the top in serialization
            indent: how to indent formatted strings
            compact: if ``True``, put initial attributes on the first line
        Returns:
            the PENMAN-serialized string of the Graph *g*
        Example:
            >>> from penman.graph import Graph
            >>> from penman.codec import PENMANCodec
            >>> codec = PENMANCodec()
            >>> codec.encode(Graph([('h', 'instance', 'hi')]))
            '(h / hi)'

        """
        tree = layout.configure(g, top=top, model=self.model)
        return self.format(tree, indent=indent, compact=compact)

    def format(self,
               tree: Tree,
               indent: Union[int, None] = -1,
               compact: bool = False) -> str:
        """
        Format *tree* into a PENMAN string.
        """
        return format(tree, indent=indent, compact=compact)

    def format_triples(self,
                       triples: Iterable[BasicTriple],
                       indent: bool = True) -> str:
        """
        Return the formatted triple conjunction of *triples*.

        Args:
            triples: an iterable of triples
            indent: how to indent formatted strings
        Returns:
            the serialized triple conjunction of *triples*
        Example:
            >>> from penman.codec import PENMANCodec
            >>> codec = PENMANCodec()
            >>> codec.format_triples([('a', ':instance', 'alpha'),
            ...                       ('a', ':ARG0', 'b'),
            ...                       ('b', ':instance', 'beta')])
            ...
            'instance(a, alpha) ^\\nARG0(a, b) ^\\ninstance(b, beta)'

        """
        return format_triples(triples, indent=indent)
