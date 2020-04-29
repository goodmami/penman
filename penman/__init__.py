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
    'Triple',
    'Graph',
    'PENMANCodec',
    'parse',
    'format',
    'interpret',
    'configure',
    'decode',
    'encode',
    'load',
    'loads',
    'dump',
    'dumps',
]

import logging

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
from penman.layout import (
    interpret,
    configure,
)
from penman._parse import parse
from penman._format import format
from penman.codec import PENMANCodec
from penman.interface import (
    decode,
    encode,
    load,
    loads,
    dump,
    dumps,
)

logging.basicConfig()
