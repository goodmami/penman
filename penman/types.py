
"""
Basic types used by various Penman modules.
"""

from typing import (Union, Iterable, Tuple, IO)
from pathlib import Path


Variable = str
Constant = Union[str, float, int]
Role = str  # '' for anonymous relations

Target = Union[Variable, Constant, None]  # None for untyped nodes
BasicTriple = Tuple[Variable, Role, Target]
Triples = Iterable[BasicTriple]


# "Utility" types; not Penman-specific

file_or_filename = Union[str, Path, IO[str]]
