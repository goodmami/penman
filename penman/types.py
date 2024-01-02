"""
Basic types used by various Penman modules.
"""

from typing import Iterable, List, Tuple, Union

Variable = str
Constant = Union[str, float, int, None]  # None for missing values
Role = str  # '' for anonymous relations
Symbol = str

# Tree types
Branch = Tuple[Role, Union[Symbol, "Node"]]
Node = Tuple[Variable, List[Branch]]

# Graph types
Target = Union[Variable, Constant]
BasicTriple = Tuple[Variable, Role, Target]
Triples = Iterable[BasicTriple]
