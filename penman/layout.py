# -*- coding: utf-8 -*-

"""
Interpreting trees to graphs and configuring graphs to trees.

In order to serialize graphs into the PENMAN format, a tree-like
layout of the graph must be decided. Deciding a layout includes
choosing the order of the edges from a node and the paths to get to a
node definition (the node reference that includes its label and
edges). For instance, the following graphs for "The dog barked loudly"
have different edge orders on the ``b`` node::

  (b / bark-01           (b / bark-01
     :ARG0 (d / dog)        :mod (l / loud)
     :mod (l / loud))       :ARG0 (d / dog))

With re-entrancies, there are choices about which location of a
re-entrant node gets the full definition with its node label, etc.
For instance, the following graphs for "The dog tried to bark" have
different locations for the definition of the ``d`` node::

  (t / try-01              (t / try-01
     :ARG0 (d / dog)          :ARG0 d
     :ARG1 (b / bark-01       :ARG1 (b / bark-01
        :ARG0 d))                :ARG0 (d / dog))

With inverted edges, there are even more possibilities, such as::

  (t / try-01                (t / try-01
     :ARG0 (d / dog             :ARG1 (b / bark-01
        :ARG0-of b)                :ARG0 (d / dog
     :ARG1 (b / bark-01))             :ARG0-of t)))

This module introduces two epigraphical markers so that a pure graph
parsed from PENMAN can retain information about its tree layout
without altering its graph properties. The first marker type is
:class:`Push`, which is put on a triple to indicate that the triple
introduces a new node context, while the sentinel :data:`POP`
indicates that a triple is at the end of one or more node contexts.
These markers only work if the triples in the graph's data are
ordered. For instance, one of the graphs above (repeated here) has the
following data::

  PENMAN                 Graph                            Epigraph
  (t / try-01            [('t', ':instance', 'try-01'),   :
     :ARG0 (d / dog)      ('t', ':ARG0', 'd'),            : Push('d')
     :ARG1 (b / bark-01   ('d', ':instance', 'dog'),      : POP
        :ARG0 d))         ('t', ':ARG1', 'b'),            : Push('b')
                          ('b', ':instance', 'bark-01'),  :
                          ('b', ':ARG0', 'd')]            : POP
"""

from typing import Union, Mapping
import copy

from penman.exceptions import LayoutError
from penman.types import Identifier
from penman.epigraph import Epidatum
from penman.tree import (Tree, Node, is_atomic)
from penman.graph import (Graph, NODETYPE_ROLE)
from penman.model import Model


_Nodemap = Mapping[Identifier, Union[Node, None]]


# Epigraphical markers

class LayoutMarker(Epidatum):
    """Epigraph marker for layout choices."""


class Push(LayoutMarker):
    """Epigraph marker to indicate a new node context."""

    __slots__ = 'id',

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return 'Push({})'.format(self.id)


class _Pop(LayoutMarker):
    """Epigraph marker to indicate the end of a node context."""

    __slots__ = ()

    def __repr__(self):
        return 'POP'


#: Epigraphical marker to indicate the end of a node context.
POP = _Pop()


# Tree to graph interpretation ################################################

def interpret(t: Tree, model: Model = None) -> Graph:
    """
    Interpret tree *t* as a graph using *model*.
    """
    if model is None:
        model = Model()
    top, triples, epidata = _interpret_node(t.node, model)
    return Graph(triples, top=top, epidata=epidata, metadata=t.metadata)


def _interpret_node(t: Node, model: Model):
    triples = []
    epidata = {}
    id, edges = t
    for role, target, epis in edges:
        if role == '/':
            role = NODETYPE_ROLE
        # atomic targets
        if is_atomic(target):
            child = ()
            target_id = target
        # nested nodes
        else:
            child = target
            target_id = target[0]
        triple = model.deinvert((id, role, target_id))
        triples.append(triple)
        epidata[triple] = epis
        # recurse to nested nodes
        if child:
            epidata[triple].append(Push(target_id))
            _, _triples, _epis = _interpret_node(child, model)
            triples.extend(_triples)
            epidata.update(_epis)
            epidata[triples[-1]].append(POP)

    return id, triples, epidata


# Graph to tree configuration #################################################

def configure(g: Graph,
              top: Identifier = None,
              model: Model = None,
              strict: bool = False) -> Tree:
    """
    Create a tree from a graph by making as few decisions as possible.
    """
    if model is None:
        model = Model()
    node, data, nodemap = _configure(g, top, model, strict)
    # if any data remain, the graph was not properly annotated for a tree
    while data:
        skipped, id, data = _find_next(data, nodemap)
        data_count = len(data)
        if id is None or data_count == 0:
            raise LayoutError('possibly disconnected graph')
        _configure_node(id, data, nodemap, model)
        if len(data) >= data_count:
            raise LayoutError('possible cycle in configuration')
        data = skipped + data
    return Tree(node, metadata=g.metadata)


def _configure(g, top, model, strict):
    """
    Create the tree that can be created without any improvising.
    """
    if len(g.triples) == 0:
        return (g.top, []), [], {}

    nodemap: _Nodemap = {var: None for var in g.variables()}
    if top is None:
        top = g.top
    if top not in nodemap:
        raise LayoutError('top is not a variable: {!r}'.format(top))
    nodemap[top] = (top, [])

    data = list(reversed(_preconfigure(g, strict)))
    node = _configure_node(top, data, nodemap, model)

    return node, data, nodemap


def _preconfigure(g, strict):
    """
    Arrange the triples and epidata for ordered traversal.

    Also perform some basic validation.
    """
    data = []
    epidata = g.epidata
    pushed = set()
    for triple in g.triples:
        push, pops, others = None, [], []
        for epi in epidata.get(triple, []):
            if isinstance(epi, Push):
                if push is not None or epi.id in pushed:
                    if strict:
                        raise LayoutError(
                            "multiple node contexts for '{}'"
                            .format(epi.id))
                    pass  # change to 'continue' to disallow multiple contexts
                if epi.id not in (triple[0], triple[2]):
                    if strict:
                        raise LayoutError(
                            "node context '{}' invalid for triple: {}"
                            .format(epi.id, triple))
                    continue
                pushed.add(epi.id)
                push = epi
            elif epi is POP:
                pops.append(epi)
            else:
                others.append(epi)

        if strict and push and pops:
            raise LayoutError(
                'incompatible node context changes on triple: {}'
                .format(triple))

        data.append((triple, others, push))
        data.extend(pops)

    return data


def _configure_node(id, data, nodemap, model):
    """
    Configure a node and any descendants.

    Side-effects:
      * *data* is modified
      * *nodemap* is modified
    """
    node = nodemap[id]
    edges = node[1]

    while data:
        datum = data.pop()
        if datum is POP:
            break

        triple, epidata, push = datum
        if triple[0] == id:
            source, role, target = triple
        elif triple[2] == id:
            source, role, target = model.invert(triple)
        else:
            # misplaced triple
            data.append(datum)
            break

        if push and push.id == target:
            nodemap[push.id] = (push.id, [])
            target = _configure_node(
                push.id, data, nodemap, model)
        elif target in nodemap and nodemap[target] is None:
            # site of potential node context
            nodemap[target] = node

        if role == NODETYPE_ROLE:
            role = '/'
            index = 0
        else:
            index = len(edges)

        edges.insert(index, (role, target, epidata))

    return node


def _find_next(data, nodemap):
    """
    Find the next node context; establish if necessary.
    """
    id = None
    for i in range(len(data) - 1, -1, -1):
        datum = data[i]
        if datum is POP:
            continue
        source, _, target = datum[0]
        if source in nodemap and _get_or_establish_site(source, nodemap):
            id = source
            break
        elif target in nodemap and _get_or_establish_site(target, nodemap):
            id = target
            break
    pivot = i + 1
    return data[pivot:], id, data[:pivot]


def _get_or_establish_site(id, nodemap):
    """
    Turn a node identifier target into a node context.
    """
    # first check if the id is available at all
    if nodemap[id] is not None:
        _id, edges = nodemap[id]
        # if the mapped node's id doesn't match it can be established
        if id != _id:
            node = (id, [])
            nodemap[id] = node
            for i in range(len(edges)):
                # replace the identifier in the tree with the new node
                if edges[i][1] == id:
                    edge = list(edges[i])
                    edge[1] = node
                    edges[i] = tuple(edge)
        else:
            pass  # otherwise the node already exists so we're good
        return True
    # id is not yet available
    return False


def reconfigure(g: Graph,
                top: Identifier = None,
                model: Model = None,
                strict: bool = False) -> Tree:
    """
    Create a tree from a graph after any discarding layout markers.
    """
    p = copy.deepcopy(g)
    for epilist in p.epidata.values():
        epilist[:] = [epi for epi in epilist
                      if not isinstance(epi, LayoutMarker)]
    return configure(p, top=top, model=model, strict=strict)


def has_valid_layout(g: Graph,
                     top: Identifier = None,
                     model: Model = None,
                     strict: bool = False) -> bool:
    """
    Return True if *g* contains the information for a valid layout.

    Having a valid layout means that the graph data allows a
    depth-first traversal that reconstructs a spanning tree used for
    serialization.
    """
    if model is None:
        model = Model()
    tree, data, nodemap, variables = _configure(g, top, model, strict)
    return len(data) == 0
