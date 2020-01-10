
"""
Functions for basic reading and writing of PENMAN graphs.
"""

from typing import Union, Iterable, List
from pathlib import Path

from penman.codec import PENMANCodec
from penman.model import Model
from penman.graph import Graph
from penman.types import (Variable, file_or_filename)


def decode(s: str,
           model: Model = None) -> Graph:
    """
    Deserialize PENMAN-serialized *s* into its Graph object

    Args:
        s: a string containing a single PENMAN-serialized graph
        model: the model used for interpreting the graph
    Returns:
        the Graph object described by *s*
    Example:

        >>> decode('(b / bark-01 :ARG0 (d / dog))')
        <Graph object (top=b) at ...>

    """
    codec = PENMANCodec(model=model)
    return codec.decode(s)


def encode(g: Graph,
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

        >>> encode(Graph([('h', 'instance', 'hi')]))
        (h / hi)

    """
    codec = PENMANCodec(model=model)
    return codec.encode(g,
                        top=top,
                        indent=indent,
                        compact=compact)


def load(source: file_or_filename,
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


def loads(string: str,
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


def dump(graphs: Iterable[Graph],
         file: file_or_filename,
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
            _dump(fh, graphs, codec, indent, compact)
    else:
        assert hasattr(file, 'write')
        _dump(file, graphs, codec, indent, compact)


def _dump(fh, gs, codec, indent, compact):
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


def dumps(graphs: Iterable[Graph],
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
