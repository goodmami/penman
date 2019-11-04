
"""
Definitions of tree structures.
"""

from typing import Tuple, List, Any

from penman.types import (Identifier, Role)
from penman.epigraph import Epidata

# Tree types
Branch = Tuple[Role, Any, Epidata]
Tree = Tuple[Identifier, List[Branch]]
