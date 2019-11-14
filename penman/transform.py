
"""
Tree and graph transformations.
"""

from typing import List

from penman.types import BasicTriple
from penman.tree import (Tree, Node, is_atomic)
from penman.graph import Graph
from penman.model import Model
from penman.layout import (LayoutMarker, Push, POP)


def canonicalize_roles(t: Tree, model: Model) -> Tree:
    """
    Normalize roles in *t* so they are canonical according to *model*.

    This is a tree transformation instead of a graph transformation
    because the orientation of the pure graph's triples is not decided
    until the graph is configured into a tree.
    """
    if model is None:
        model = Model()
    return Tree(_canonicalize_node(t.node, model), metadata=t.metadata)


def _canonicalize_node(node: Node, model: Model) -> Node:
    id, edges = node
    canonical_edges = []
    for i, edge in enumerate(edges):
        role, tgt, epidata = edge
        if not is_atomic(tgt):
            tgt = _canonicalize_node(tgt, model)
        canonical_edges.append(
            (model.canonicalize_role(role), tgt, list(epidata)))
    return (id, canonical_edges)


def reify_edges(g: Graph, model: Model) -> Graph:
    """
    Reify all edges in *g* that have reifications in *model*.
    """
    vars = g.variables()
    if model is None:
        model = Model()
    new_epidata = dict(g.epidata)
    new_triples: List[BasicTriple] = []
    for triple in g.triples:
        if model.is_reifiable(triple):
            in_triple, node_triple, out_triple = model.reify(triple, vars)
            new_triples.extend((in_triple, node_triple, out_triple))
            var = node_triple[0]
            vars.add(var)
            # manage epigraphical markers
            new_epidata[in_triple] = [Push(var)]
            new_epidata[node_triple] = [
                epi for epi in new_epidata.pop(triple)
                if not isinstance(epi, LayoutMarker)]
            new_epidata[out_triple] = [POP]
        else:
            new_triples.append(triple)
    return Graph(new_triples,
                 epidata=new_epidata,
                 metadata=g.metadata)


def contract_edges(g: Graph, model: Model) -> None:
    """
    Contract all edges in *g* that have reifications in *model*.
    """
    if model is None:
        model = Model()
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
