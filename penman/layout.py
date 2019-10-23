# -*- coding: utf-8 -*-

"""
Embedding tree structure in basic graphs.

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

This module introduces two :class:`Marker <graph.Marker>` sentinel
instances: :data:`PUSH` and :data:`POP`. :data:`PUSH` indicates that
the current branch descends to another node context, while :data:`POP`
returns to a previous node context. This method only works if the
triples in the graph's data are ordered. For instance, the first graph
above (repeated here) has the following data::

  PENMAN graph         Graph data                      Epigraph data
  (b / bark-01         [('b', 'instance', 'bark-01'),
     :ARG0 (d / dog)    ('b', 'ARG0', 'd'),            : Push('d')
     :mod (l / loud))   ('d', 'instance', 'dog'),      : Pop()
                        ('b', 'mod', 'l'),             : Push('l')
                        ('l', 'instance', 'loud')]     : Pop()

"""

from typing import Any, Iterable, List, NamedTuple
import re

from penman.exceptions import LayoutError
from penman import (
    graph,
    model as _model,
)

_Identifier = graph._Identifier


# Epigraphical markers

class LayoutMarker(graph.Epidatum):
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


POP = _Pop()


_TripleIter = Iterable[graph.Triple]
_TripleList = List[graph.Triple]


def original_order(triples: _TripleIter) -> _TripleList:
    """
    Return a list of triples in the original order.
    """
    return list(triples)


def out_first_order(triples: _TripleIter) -> _TripleList:
    """
    Sort a list of triples so outward (true) edges appear first.
    """
    return sorted(triples, key=lambda t: t.inverted)


def alphanum_order(triples: _TripleIter) -> _TripleList:
    """
    Sort a list of triples by relation name.

    Embedded integers are sorted numerically, but otherwise the
    sorting is alphabetic.
    """
    return sorted(
        triples,
        key=lambda t: [
            int(t) if t.isdigit() else t
            for t in re.split(r'([0-9]+)', t.relation or '')
        ]
    )


# Tree to graph interpretation ################################################

def interpret(t: graph.Tree, model: _model.Model):
    """
    Interpret tree *t* as a graph using *model*.
    """
    top, triples, epidata = _interpret_node(t, model)
    return graph.Graph(triples, top=top, epidata=epidata)


def _interpret_node(t: graph.Tree, model: _model.Model):
    triples = []
    epidata = {}
    id, edges = t
    has_nodetype = False
    for role, target, epis in edges:
        if role == '/':
            role = model.nodetype_role
            has_nodetype = True
        # atomic targets
        if is_atomic(target):
            child = ()
            target_id = target
        # nested nodes
        else:
            child = target
            target_id = target[0]
        triple = model.normalize((id, role, target_id))
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

def configure(g: graph.Graph, model: _model.Model, top=None, strict=False):
    """
    Create a tree from a graph by making as few decisions as possible.
    """
    if top is None:
        top = g.top
    data = list(reversed(_preconfigure(g, strict)))
    variables = g.variables()
    nodemap = {top: (top, [])}
    tree = _configure_node(top, data, variables, nodemap, model)
    # if any data remain, the graph was not properly annotated for a tree
    while data:
        skipped, id, data = _find_next(data, nodemap)
        data_count = len(data)
        if id is None or data_count == 0:
            raise LayoutError('possibly disconnected graph')
        _configure_node(id, data, variables, nodemap, model)
        if len(data) >= data_count:
            raise LayoutError('cycle in configuration')
        data = skipped + data
    return tree


def _preconfigure(g, strict):
    """
    Arrange the triples and epidata for ordered traversal.

    Also perform some basic validation.
    """
    data = []
    epidata = g.epidata
    pushed = set()
    for triple in g.triples():
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

def _configure_node(id, data, variables, nodemap, model):
    """
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
                push.id, data, variables, nodemap, model)
        elif target in variables and target not in nodemap:
            # site of potential node context
            nodemap[target] = node

        if role == model.nodetype_role:
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
    for i in range(len(data)-1, -1, -1):
        datum = data[i]
        if datum is POP:
            continue
        source, _, target = datum[0]
        if _get_or_establish_site(source, nodemap):
            id = source
            break
        elif _get_or_establish_site(target, nodemap):
            id = target
            break
    return data[:i], id, data[i:]


def _get_or_establish_site(id, nodemap):
    """
    Turn a node identifier target into a node context.
    """
    # first check if the id is available at all
    if id in nodemap:
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


def reconfigure(g: graph.Graph, model: _model.Model, top=None, strict=False):
    """
    Create a tree from a graph after any discarding layout markers.
    """
    graph.clear_epidata(g, LayoutMarker)
    return configure(g, model, top=top, strict=strict)


def has_valid_layout(g: graph.Graph):
    """
    Return True if *g* contains the information for a valid layout.

    Having a valid layout means that the graph data allows a
    depth-first traversal that reconstructs a spanning tree used for
    serialization.
    """
    data = list(reversed(_preconfigure(g, strict)))
    variables = g.variables()
    nodemap = {top: (top, [])}
    tree = _configure_node(g.top, data, variables, nodemap, model)
    return len(data) == 0


def is_atomic(x):
    """
    Return `True` if *x* is a valid atomic value.
    """
    return x is None or isinstance(x, (str, int, float))


def tree_node_identifiers(t: graph.Tree):
    """
    Return the list of node identifiers in the tree.
    """
    id, edges = t
    ids = [id]
    for _, target, _ in edges:
        # if target is not atomic, assume it's a valid tree node
        if not is_atomic(target):
            ids.extend(tree_node_identifiers(target))
    return ids


def inspect(g: graph.Graph):
    stack = []
    for t in g._data:
        if t is POP:
            stack.pop()
        else:
            # a properly laid-out graph should not need to pop any
            # more ids off the stack, but otherwise keep popping until
            # a suitable id is found or the stack is empty
            while stack and stack[-1] not in (t.source, t.target):
                stack.pop()
            if stack and t.target == stack[-1]:
                print('{3:>{0}} :{2} :{1}'.format(len(stack) * 3, *t))
                stack.append(t.source)
            else:
                print('{1:>{0}} :{2} :{3}'.format(len(stack) * 3, *t))
                stack.append(t.target)
