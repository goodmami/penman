# -*- coding: utf-8 -*-

"""
Serialization of PENMAN graphs.
"""

from typing import Union, Iterable, Iterator, List, IO
from pathlib import Path

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


# "Utility" types; not Penman-specific

FileOrFilename = Union[str, Path, IO[str]]


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
        for tree in iterparse(lines):
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


# The following are for the top-level API. They are renamed when they
# are imported into __init__.py. They are named with the leading
# underscore here so they are not included as part of penman.codec's
# public API.

def _decode(s: str,
            model: Model = None) -> Graph:
    """
    Deserialize PENMAN-serialized *s* into its Graph object

    Args:
        s: a string containing a single PENMAN-serialized graph
        model: the model used for interpreting the graph
    Returns:
        the Graph object described by *s*
    Example:
        >>> import penman
        >>> penman.decode('(b / bark-01 :ARG0 (d / dog))')
        <Graph object (top=b) at ...>

    """
    codec = PENMANCodec(model=model)
    return codec.decode(s)


def _iterdecode(lines: Union[Iterable[str], str],
                model: Model = None) -> Iterator[Graph]:
    """
    Yield graphs parsed from *lines*.

    Args:
        lines: a string or open file with PENMAN-serialized graphs
        model: the model used for interpreting the graph
    Returns:
        The :class:`~penman.graph.Graph` objects described in
        *lines*.
    Example:
        >>> import penman
        >>> for g in penman.iterdecode('(a / alpha) (b / beta)'):
        ...     print(repr(g))
        <Graph object (top=a) at ...>
        <Graph object (top=b) at ...>
    """
    codec = PENMANCodec(model=model)
    yield from codec.iterdecode(lines)


def _encode(g: Graph,
            top: Variable = None,
            model: Model = None,
            indent: Union[int, bool] = -1,
            compact: bool = False) -> str:
    """
    Serialize the graph *g* from *top* to PENMAN notation.

    Args:
        g: the Graph object
        top: if given, the node to use as the top in serialization
        model: the model used for interpreting the graph
        indent: how to indent formatted strings
        compact: if ``True``, put initial attributes on the first line
    Returns:
        the PENMAN-serialized string of the Graph *g*
    Example:
        >>> import penman
        >>> from penman.graph import Graph
        >>> penman.encode(Graph([('h', 'instance', 'hi')]))
        '(h / hi)'

    """
    codec = PENMANCodec(model=model)
    return codec.encode(g,
                        top=top,
                        indent=indent,
                        compact=compact)


def _load(source: FileOrFilename,
          model: Model = None) -> List[Graph]:
    """
    Deserialize a list of PENMAN-encoded graphs from *source*.

    Args:
        source: a filename or file-like object to read from
        model: the model used for interpreting the graph
    Returns:
        a list of Graph objects
    """
    codec = PENMANCodec(model=model)
    if isinstance(source, (str, Path)):
        with open(source) as fh:
            return list(codec.iterdecode(fh))
    else:
        assert hasattr(source, 'read')
        return list(codec.iterdecode(source))


def _loads(string: str,
           model: Model = None) -> List[Graph]:
    """
    Deserialize a list of PENMAN-encoded graphs from *string*.

    Args:
        string: a string containing graph data
        model: the model used for interpreting the graph
    Returns:
        a list of Graph objects
    """
    codec = PENMANCodec(model=model)
    return list(codec.iterdecode(string))


def _dump(graphs: Iterable[Graph],
          file: FileOrFilename,
          model: Model = None,
          indent: Union[int, bool] = -1,
          compact: bool = False) -> None:
    """
    Serialize each graph in *graphs* to PENMAN and write to *file*.

    Args:
        graphs: an iterable of Graph objects
        file: a filename or file-like object to write to
        model: the model used for interpreting the graph
        indent: how to indent formatted strings
        compact: if ``True``, put initial attributes on the first line
    """
    codec = PENMANCodec(model=model)
    if isinstance(file, (str, Path)):
        with open(file, 'w') as fh:
            _dump_stream(fh, graphs, codec, indent, compact)
    else:
        assert hasattr(file, 'write')
        _dump_stream(file, graphs, codec, indent, compact)


def _dump_stream(fh, gs, codec, indent, compact):
    """Helper method for dump() for incremental printing."""
    ss = (codec.encode(g, indent=indent, compact=compact)
          for g in gs)
    try:
        print(next(ss), file=fh)
    except StopIteration:
        return
    for s in ss:
        print(file=fh)
        print(s, file=fh)


def _dumps(graphs: Iterable[Graph],
           model: Model = None,
           indent: Union[int, bool] = -1,
           compact: bool = False) -> str:
    """
    Serialize each graph in *graphs* to the PENMAN format.

    Args:
        graphs: an iterable of Graph objects
        model: the model used for interpreting the graph
        indent: how to indent formatted strings
        compact: if ``True``, put initial attributes on the first line
    Returns:
        the string of serialized graphs
    """
    codec = PENMANCodec(model=model)
    strings = [codec.encode(g, indent=indent, compact=compact)
               for g in graphs]
    return '\n\n'.join(strings)
