
"""
Tree and graph transformations.
"""

from penman.tree import (Tree, Node, is_atomic)
from penman.graph import Graph
from penman.model import Model


def canonicalize_roles(t: Tree, model: Model) -> None:
    """
    Normalize roles in *t* so they are canonical according to *model*.

    This is a tree transformation instead of a graph transformation
    because the orientation of the pure graph's triples is not decided
    until the graph is configured into a tree.
    """
    if model is None:
        model = Model()
    _canonicalize_node(t.node, model)


def _canonicalize_node(node: Node, model: Model) -> None:
    _, edges = node
    for i, edge in enumerate(edges):
        role, tgt, epidata = edge
        if not is_atomic(tgt):
            _canonicalize_node(tgt, model)
        edges[i] = (model.canonicalize_role(role), tgt, epidata)


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
