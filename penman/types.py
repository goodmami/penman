
"""
Basic types used by various Penman modules.
"""

from typing import (Union, Iterable, Tuple, Set, IO)
from pathlib import Path


Identifier = str
IdSet = Set[Identifier]
Constant = Union[str, float, int]
Role = str  # '' for anonymous relations

Target = Union[Identifier, Constant, None]  # None for untyped nodes
BasicTriple = Tuple[Identifier, Role, Target]
Triples = Iterable[BasicTriple]


# "Utility" types; not Penman-specific

file_or_filename = Union[str, Path, IO[str]]
