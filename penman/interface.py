# -*- coding: utf-8 -*-

from penman import PENMANCodec


def decode(s, cls=PENMANCodec, **kwargs):
    """
    Deserialize PENMAN-serialized *s* into its Graph object

    Args:
        s: a string containing a single PENMAN-serialized graph
        cls: serialization codec class
        kwargs: keyword arguments passed to the constructor of *cls*
    Returns:
        the Graph object described by *s*
    Example:

        >>> decode('(b / bark :ARG1 (d / dog))')
        <Graph object (top=b) at ...>

    """
    codec = cls(**kwargs)
    return codec.decode(s)


def encode(g, top=None, cls=PENMANCodec, **kwargs):
    """
    Serialize the graph *g* from *top* to PENMAN notation.

    Args:
        g: the Graph object
        top: the node identifier for the top of the serialized graph;
            if unset, the original top of *g* is used
        cls: serialization codec class
        kwargs: keyword arguments passed to the constructor of *cls*
    Returns:
        the PENMAN-serialized string of the Graph *g*
    Example:
        >>> encode(Graph([('h', 'instance', 'hi')]))
        (h / hi)
    """
    codec = cls(**kwargs)
    return codec.encode(g, top=top)


def load(source, triples=False, cls=PENMANCodec, **kwargs):
    """
    Deserialize a list of PENMAN-encoded graphs from *source*.

    Args:
        source: a filename or file-like object to read from
        triples: if True, read graphs as triples instead of as PENMAN
        cls: serialization codec class
        kwargs: keyword arguments passed to the constructor of *cls*
    Returns:
        a list of Graph objects
    """
    decode = cls(**kwargs).iterdecode
    if hasattr(source, 'read'):
        return list(decode(source.read()))
    else:
        with open(source) as fh:
            return list(decode(fh.read()))


def loads(string, triples=False, cls=PENMANCodec, **kwargs):
    """
    Deserialize a list of PENMAN-encoded graphs from *string*.

    Args:
        string: a string containing graph data
        triples: if True, read graphs as triples instead of as PENMAN
        cls: serialization codec class
        kwargs: keyword arguments passed to the constructor of *cls*
    Returns:
        a list of Graph objects
    """
    codec = cls(**kwargs)
    return list(codec.iterdecode(string, triples=triples))


def dump(graphs, file, triples=False, cls=PENMANCodec, **kwargs):
    """
    Serialize each graph in *graphs* to PENMAN and write to *file*.

    Args:
        graphs: an iterable of Graph objects
        file: a filename or file-like object to write to
        triples: if True, write graphs as triples instead of as PENMAN
        cls: serialization codec class
        kwargs: keyword arguments passed to the constructor of *cls*
    """
    if hasattr(file, 'write'):
        _dump(file, graphs, triples, cls, **kwargs)
    else:
        with open(file, 'w') as fh:
            _dump(fh, graphs, triples, cls, **kwargs)


def _dump(fh, gs, triples, cls, **kwargs):
    """Helper method for dump() for incremental printing."""
    codec = cls(**kwargs)
    ss = (codec.encode(g, triples=triples) for g in gs)
    try:
        print(next(ss), file=fh)
    except StopIteration:
        return
    for s in ss:
        print(file=fh)
        print(s, file=fh)


def dumps(graphs, triples=False, cls=PENMANCodec, **kwargs):
    """
    Serialize each graph in *graphs* to the PENMAN format.

    Args:
        graphs: an iterable of Graph objects
        triples: if True, write graphs as triples instead of as PENMAN
    Returns:
        the string of serialized graphs
    """
    codec = cls(**kwargs)
    strings = [codec.encode(g, triples=triples) for g in graphs]
    return '\n\n'.join(strings)
