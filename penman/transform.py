
"""
Tree and graph transformations.
"""

from typing import Union, List, Tuple

from penman.types import BasicTriple
from penman.epigraph import (Epidatum, Epidata)
from penman.surface import (Alignment, RoleAlignment)
from penman.tree import (Tree, Node, is_atomic)
from penman.graph import Graph
from penman.model import Model
from penman.layout import (Push, POP)


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
            node_epis, out_epis = _edge_markers(new_epidata.pop(triple))
            new_epidata[node_triple] = node_epis
            new_epidata[out_triple] = out_epis
            # we don't know where to put the final POP without configuring
            # the tree; maybe this should be a tree operation?
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


def reify_attributes(g: Graph, model: Model) -> Graph:
    """
    Reify all attributes in *g* that have reifications in *model*.
    """
    variables = g.variables()
    if model is None:
        model = Model()
    new_epidata = dict(g.epidata)
    new_triples: List[BasicTriple] = []
    i = 2
    for triple in g.triples:
        source, role, target = triple
        if (model.nodetype_role not in (role, ':' + role)
                and target not in variables):
            # get unique id for new node
            var = '_'
            while var in variables:
                var = '_{}'.format(i)
                i += 1
            variables.add(var)
            role_triple = (source, role, var)
            node_triple = (var, model.nodetype_role, target)
            new_triples.extend((role_triple, node_triple))
            # manage epigraphical markers
            role_epis, node_epis = _attr_markers(new_epidata.pop(triple))
            new_epidata[role_triple] = role_epis + [Push(var)]
            new_epidata[node_triple] = node_epis + [POP]
        else:
            new_triples.append(triple)
    return Graph(new_triples,
                 epidata=new_epidata,
                 metadata=g.metadata)


def indicate_branches(g: Graph, model: Model) -> None:
    """
    Insert TOP triples in *g* indicating the tree structure.

    Note:
        This depends on *g* containing the epigraphical data from
        parsing; it will not work with programmatically constructed
        Graph objects or those whose epigraphical data were removed.
    """
    pass


_SplitMarkers = Tuple[Union[Epidatum, None], Epidata, Epidata, Epidata]


def _reified_markers(epidata: Epidata) -> _SplitMarkers:
    """
    Return epigraphical markers broken down by function.

    When a relation is reified the original triple disappears so its
    epigraphical data needs to be moved and sometimes altered.
    Consider the following, which has surface alignment markers::

        (a :role~1 b~2)

    Under edge reification, the desired outcome is::

        (a :ARG1-of (_ / role-label~1 :ARG2 b~2))

    Under attribute reification, it is::

        (a :role~1 (_ / b~2))
    """
    push = None
    pops = []
    role_epis = []
    other_epis = []
    for epi in epidata:
        if isinstance(epi, Push):
            push = epi
        elif epi is POP:
            pops.append(epi)
        elif epi.mode == 1:
            role_epis.append(epi)
        else:
            other_epis.append(epi)
    return push, pops, role_epis, other_epis


def _edge_markers(epidata: Epidata) -> Tuple[Epidata, Epidata]:
    push, pops, role_epis, other_epis = _reified_markers(epidata)
    # role markers on the original triple need to be converted to
    # target markers, if possible
    node_epis: List[Epidatum] = []
    for epi in role_epis:
        if isinstance(epi, RoleAlignment):
            node_epis.append(Alignment(epi.indices, prefix=epi.prefix))
        else:
            pass  # discard things we can't convert
    # other markers on the original triple get grouped for the
    # new outgoing triple
    out_epis = other_epis
    if push:
        out_epis.append(push)
    out_epis.extend(pops)

    return node_epis, out_epis


def _attr_markers(epidata: Epidata) -> Tuple[Epidata, Epidata]:
    _, pops, role_epis, other_epis = _reified_markers(epidata)
    node_epis = other_epis
    node_epis.extend(pops)
    return role_epis, node_epis
