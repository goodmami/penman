# -*- coding: utf-8 -*-

"""
Penman graph library.
"""

# the following is to retain parts of the original API

__all__ = [
    '__version__',
    '__version_info__',
    'PenmanError',
    'DecodeError',
    'Tree',
    'Triple',
    'Graph',
    'PENMANCodec',
    'parse',
    'iterparse',
    'parse_triples',
    'format',
    'format_triples',
    'interpret',
    'configure',
    'decode',
    'iterdecode',
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
from penman._format import (
    format,
    format_triples,
)
from penman._parse import (
    iterparse,
    parse,
    parse_triples,
)
from penman.codec import (
    PENMANCodec,
    _decode as decode,
    _dump as dump,
    _dumps as dumps,
    _encode as encode,
    _iterdecode as iterdecode,
    _load as load,
    _loads as loads,
)
from penman.exceptions import (
    DecodeError,
    PenmanError,
)
from penman.graph import (
    Graph,
    Triple,
)
from penman.layout import (
    configure,
    interpret,
)
from penman.tree import Tree
