# -*- coding: utf-8 -*-

"""
PENMAN graph library for AMR, DMRS, etc.

Penman is a module to assist in working with graphs encoded in PENMAN
notation, such as those for Abstract Meaning Representation (AMR) or
Dependency Minimal Recursion Semantics (DMRS). It allows for conversion
between PENMAN and triples, inspection of the graphs, and
reserialization (e.g. for selecting a new top node). Some features,
such as conversion or reserialization, can be done by calling the
module as a script.
"""

__all__ = [
    '__version__',
    '__version_info__',
    '__title__',
    '__summary__',
    '__uri__',
    '__author__',
    '__email__',
    '__license__',
    '__copyright__',
    'PenmanError',
    'GraphError',
    'LayoutError',
    'DecodeError',
    'SurfaceError',
    'ModelError',
    'lex',
    'Triple',
    'Edge',
    'Attribute',
    'Graph',
    'Tree',
    'Model',
    'PENMANCodec',
    'decode',
    'encode',
    'load',
    'loads',
    'dump',
    'dumps',
]


from penman.__about__ import (
    __version__,
    __version_info__,
    __title__,
    __summary__,
    __uri__,
    __author__,
    __email__,
    __license__,
    __copyright__,
)

from penman.exceptions import (
    PenmanError,
    GraphError,
    LayoutError,
    DecodeError,
    SurfaceError,
    ModelError,
)
from penman.lexer import lex
from penman.graph import (
    Triple,
    Edge,
    Attribute,
    Graph,
)
from penman.tree import Tree
from penman.model import Model
from penman.codec import PENMANCodec

from penman.interface import (
    decode,
    encode,
    load,
    loads,
    dump,
    dumps,
)
