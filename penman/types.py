
"""
Basic types used by various Penman modules.
"""

from typing import (
    Union, Iterable, Tuple, Set
)

Identifier = str
IdSet = Set[Identifier]
Constant = Union[str, float, int]
Role = str  # '' for anonymous relations

Target = Union[Identifier, Constant, None]  # None for untyped nodes
BasicTriple = Tuple[Identifier, Role, Target]
Triples = Iterable[BasicTriple]
