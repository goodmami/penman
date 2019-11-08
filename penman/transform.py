
"""
Graph transformations.
"""

from penman.graph import Graph
from penman.model import Model


def canonicalize_roles(g: Graph, model: Model) -> None:
    """
    Normalize roles in *g* so they are canonical according to *model*.
    """
    pass


def reify_edges(g: Graph, model: Model) -> None:
    """
    Reify all edges in *g* that have reifications in *model*.
    """
    pass


def contract_edges(g: Graph, model: Model) -> None:
    """
    Contract all edges in *g* that have reifications in *model*.
    """
    pass


def reify_attributes(g: Graph, model: Model) -> None:
    """
    Reify all attributes in *g* that have reifications in *model*.
    """
    pass


def indicate_branches(g: Graph, model: Model) -> None:
    """
    Insert TOP triples in *g* indicating the tree structure.

    Note:
        This depends on *g* containing the epigraphical data from
        parsing; it will not work with programmatically constructed
        Graph objects or those whose epigraphical data were removed.
    """
    pass
