# -*- coding: utf-8 -*-

"""
PENMAN graph library for AMR, DMRS, etc.

Penman is a project to assist in working with graphs encoded in PENMAN
notation, such as those for Abstract Meaning Representation (AMR) or
Dependency Minimal Recursion Semantics (DMRS). It allows for
conversion between PENMAN and triples, inspection of the graphs, and
reserialization (e.g. for selecting a new top node). Some features,
such as conversion or reserialization, can be done by calling the
script interface (e.g., `python3 -m penman.main`, or just `penman` if
Penman is installed via `pip`).
"""

# the following is to retain parts of the original API

__all__ = [
    '__version__',
    '__version_info__',
    'PenmanError',
    'DecodeError',
    'Triple',
    'Graph',
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
)

from penman.exceptions import (
    PenmanError,
    DecodeError,
)
from penman.graph import (
    Triple,
    Graph,
)
from penman.codec import PENMANCodec

from penman.interface import (
    decode,
    encode,
    load,
    loads,
    dump,
    dumps,
)
