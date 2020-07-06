
"""
Tree and graph transformations.
"""

from typing import Optional, Dict, Set, List, Tuple
import logging

from penman.types import (Variable, Target, BasicTriple, Node)
from penman.exceptions import ModelError
from penman.epigraph import (Epidatum, Epidata)
from penman.surface import (Alignment, RoleAlignment, alignments)
from penman.tree import (Tree, is_atomic)
from penman.graph import (Graph, CONCEPT_ROLE)
from penman.model import Model
from penman.layout import (
    Push,
    Pop,
    POP,
    appears_inverted,
    get_pushed_variable,
)


logger = logging.getLogger(__name__)


def canonicalize_roles(t: Tree, model: Model) -> Tree:
    """
    Normalize roles in *t* so they are canonical according to *model*.

    This is a tree transformation instead of a graph transformation
    because the orientation of the pure graph's triples is not decided
    until the graph is configured into a tree.

    Args:
        t: a :class:`~penman.tree.Tree` object
        model: a model defining role normalizations
    Returns:
        A new :class:`~penman.tree.Tree` object with canonicalized
        roles.
    Example:
        >>> from penman.codec import PENMANCodec
        >>> from penman.models.amr import model
        >>> from penman.transform import canonicalize_roles
        >>> codec = PENMANCodec()
        >>> t = codec.parse('(c / chapter :domain-of 7)')
        >>> t = canonicalize_roles(t, model)
        >>> print(codec.format(t))
        (c / chapter
           :mod 7)
    """
    if model is None:
        model = Model()
    tree = Tree(_canonicalize_node(t.node, model), metadata=t.metadata)
    logger.info('Canonicalized roles: %s', tree)
    return tree


def _canonicalize_node(node: Node, model: Model) -> Node:
    var, edges = node
    canonical_edges = []
    for i, edge in enumerate(edges):
        role, tgt = edge
        # alignments aren't parsed off yet, so handle them superficially
        role, tilde, alignment = role.partition('~')
        if not is_atomic(tgt):
            tgt = _canonicalize_node(tgt, model)
        canonical_role = model.canonicalize_role(role) + tilde + alignment
        canonical_edges.append((canonical_role, tgt))
    return (var, canonical_edges)


def reify_edges(g: Graph, model: Model) -> Graph:
    """
    Reify all edges in *g* that have reifications in *model*.

    Args:
        g: a :class:`~penman.graph.Graph` object
        model: a model defining reifications
    Returns:
        A new :class:`~penman.graph.Graph` object with reified edges.
    Example:
        >>> from penman.codec import PENMANCodec
        >>> from penman.models.amr import model
        >>> from penman.transform import reify_edges
        >>> codec = PENMANCodec(model=model)
        >>> g = codec.decode('(c / chapter :mod 7)')
        >>> g = reify_edges(g, model)
        >>> print(codec.encode(g))
        (c / chapter
           :ARG1-of (_ / have-mod-91
                       :ARG2 7))
    """
    vars = g.variables()
    if model is None:
        model = Model()
    new_epidata = dict(g.epidata)
    new_triples: List[BasicTriple] = []
    for triple in g.triples:
        if model.is_role_reifiable(triple[1]):
            in_triple, node_triple, out_triple = model.reify(triple, vars)
            if appears_inverted(g, triple):
                in_triple, out_triple = out_triple, in_triple
            new_triples.extend((in_triple, node_triple, out_triple))
            var = node_triple[0]
            vars.add(var)
            # manage epigraphical markers
            new_epidata[in_triple] = [Push(var)]
            old_epis = new_epidata.pop(triple) if triple in new_epidata else []
            node_epis, out_epis = _edge_markers(old_epis)
            new_epidata[node_triple] = node_epis
            new_epidata[out_triple] = out_epis
            # we don't know where to put the final POP without configuring
            # the tree; maybe this should be a tree operation?
        else:
            new_triples.append(triple)
    g = Graph(new_triples,
              epidata=new_epidata,
              metadata=g.metadata)
    logger.info('Reified edges: %s', g)
    return g


def dereify_edges(g: Graph, model: Model) -> Graph:
    """
    Dereify edges in *g* that have reifications in *model*.

    Args:
        g: a :class:`~penman.graph.Graph` object
    Returns:
        A new :class:`~penman.graph.Graph` object with dereified
        edges.
    Example:
        >>> from penman.codec import PENMANCodec
        >>> from penman.models.amr import model
        >>> from penman.transform import dereify_edges
        >>> codec = PENMANCodec(model=model)
        >>> g = codec.decode(
        ...   '(c / chapter'
        ...   '   :ARG1-of (_ / have-mod-91'
        ...   '               :ARG2 7))')
        >>> g = dereify_edges(g, model)
        >>> print(codec.encode(g))
        (c / chapter
           :mod 7)
    """
    if model is None:
        model = Model()
    agenda = _dereify_agenda(g, model)
    new_epidata = dict(g.epidata)
    new_triples: List[BasicTriple] = []
    for triple in g.triples:
        var = triple[0]
        if var in agenda:
            first, dereified, epidata = agenda[var]
            # only insert at the first triple so the dereification
            # appears in the correct location
            if triple == first:
                new_triples.append(dereified)
                new_epidata[dereified] = epidata
            if triple in new_epidata:
                del new_epidata[triple]
        else:
            new_triples.append(triple)
    g = Graph(new_triples,
              epidata=new_epidata,
              metadata=g.metadata)
    logger.info('Dereified edges: %s', g)
    return g


def reify_attributes(g: Graph) -> Graph:
    """
    Reify all attributes in *g*.

    Args:
        g: a :class:`~penman.graph.Graph` object
    Returns:
        A new :class:`~penman.graph.Graph` object with reified
        attributes.
    Example:
        >>> from penman.codec import PENMANCodec
        >>> from penman.models.amr import model
        >>> from penman.transform import reify_attributes
        >>> codec = PENMANCodec(model=model)
        >>> g = codec.decode('(c / chapter :mod 7)')
        >>> g = reify_attributes(g)
        >>> print(codec.encode(g))
        (c / chapter
           :mod (_ / 7))
    """
    variables = g.variables()
    new_epidata = dict(g.epidata)
    new_triples: List[BasicTriple] = []
    i = 2
    for triple in g.triples:
        source, role, target = triple
        if role != CONCEPT_ROLE and target not in variables:
            # get unique var for new node
            var = '_'
            while var in variables:
                var = f'_{i}'
                i += 1
            variables.add(var)
            role_triple = (source, role, var)
            node_triple = (var, CONCEPT_ROLE, target)
            new_triples.extend((role_triple, node_triple))
            # manage epigraphical markers
            old_epis = new_epidata.pop(triple) if triple in new_epidata else []
            role_epis, node_epis = _attr_markers(old_epis)
            new_epidata[role_triple] = role_epis + [Push(var)]
            new_epidata[node_triple] = node_epis + [POP]
        else:
            new_triples.append(triple)
    g = Graph(new_triples,
              epidata=new_epidata,
              metadata=g.metadata)
    logger.info('Reified attributes: %s', g)
    return g


def indicate_branches(g: Graph, model: Model) -> Graph:
    """
    Insert TOP triples in *g* indicating the tree structure.

    Note:
        This depends on *g* containing the epigraphical layout markers
        from parsing; it will not work with programmatically
        constructed Graph objects or those whose epigraphical data
        were removed.

    Args:
        g: a :class:`~penman.graph.Graph` object
        model: a model defining the TOP role
    Returns:
        A new :class:`~penman.graph.Graph` object with TOP roles
        indicating tree branches.
    Example:
        >>> from penman.codec import PENMANCodec
        >>> from penman.models.amr import model
        >>> from penman.transform import indicate_branches
        >>> codec = PENMANCodec(model=model)
        >>> g = codec.decode('''
        ... (w / want-01
        ...    :ARG0 (b / boy)
        ...    :ARG1 (g / go-02
        ...             :ARG0 b))''')
        >>> g = indicate_branches(g, model)
        >>> print(codec.encode(g))
        (w / want-01
           :TOP b
           :ARG0 (b / boy)
           :TOP g
           :ARG1 (g / go-02
                    :ARG0 b))
    """
    new_triples: List[BasicTriple] = []
    for t in g.triples:
        push = next((epi for epi in g.epidata.get(t, [])
                     if isinstance(epi, Push)),
                    None)
        if push is not None:
            if push.variable == t[2]:
                new_triples.append((t[0], model.top_role, t[2]))
            elif push.variable == t[0]:
                assert isinstance(t[2], str)
                new_triples.append((t[2], model.top_role, t[0]))
        new_triples.append(t)
    g = Graph(new_triples,
              epidata=g.epidata,
              metadata=g.metadata)
    logger.info('Indicated branches: %s', g)
    return g


_SplitMarkers = Tuple[Optional[Push], List[Pop], Epidata, Epidata]


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
        elif isinstance(epi, Pop):
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


_Dereification = Dict[Variable,
                      Tuple[BasicTriple,  # inverted triple of reification
                            BasicTriple,  # dereified triple
                            List[Epidatum]]]  # computed epidata


def _dereify_agenda(g: Graph, model: Model) -> _Dereification:

    alns = alignments(g)
    agenda: _Dereification = {}
    fixed: Set[Target] = set([g.top])
    inst: Dict[Variable, BasicTriple] = {}
    other: Dict[Variable, List[BasicTriple]] = {}

    for triple in g.triples:
        var, role, tgt = triple
        if role == CONCEPT_ROLE:
            inst[var] = triple
        else:
            fixed.add(tgt)
            if var not in other:
                other[var] = [triple]
            else:
                other[var].append(triple)

    for var, instance in inst.items():
        if (var not in fixed
                and len(other.get(var, [])) == 2
                and model.is_concept_dereifiable(instance[2])):
            # passed initial checks
            # now figure out which other edge is the first one
            first, second = other[var]
            if get_pushed_variable(g, second) == var:
                first, second = second, first
            try:
                dereified = model.dereify(instance, first, second)
            except ModelError:
                pass
            else:
                # migrate epidata
                epidata: List[Epidatum] = []
                if instance in alns:
                    aln = alns[instance]
                    epidata.append(
                        RoleAlignment(aln.indices, prefix=aln.prefix))
                epidata.extend(epi for epi in g.epidata[second]
                               if not isinstance(epi, RoleAlignment))
                agenda[var] = (first, dereified, epidata)

    return agenda


def _attr_markers(epidata: Epidata) -> Tuple[Epidata, Epidata]:
    _, pops, role_epis, other_epis = _reified_markers(epidata)
    node_epis = other_epis
    node_epis.extend(pops)
    return role_epis, node_epis
