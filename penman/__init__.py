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
from penman.exceptions import (
    PenmanError,
    DecodeError,
)
from penman.tree import Tree
from penman.graph import (
    Triple,
    Graph,
)
from penman.layout import (
    interpret,
    configure,
)
from penman._parse import (
    parse,
    iterparse,
    parse_triples,
)
from penman._format import (
    format,
    format_triples,
)
from penman.codec import (
    PENMANCodec,
    _decode as decode,
    _iterdecode as iterdecode,
    _encode as encode,
    _load as load,
    _loads as loads,
    _dump as dump,
    _dumps as dumps,
)
