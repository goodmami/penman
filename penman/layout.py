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

class Push(graph.Epidatum):
    """Epigraph marker to indicate a new node context."""

    __slots__ = 'id',

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return 'Push({})'.format(self.id)


class _Pop(graph.Epidatum):
    """Epigraph marker to indicate the end of a node context."""

    __slots__ = ()

    def __repr__(self):
        return 'POP'


POP = _Pop()


# Layout structures

class Branch(NamedTuple):
    triple: graph.BasicTriple
    branches: List[Any]  # should be recursive: List[Branch]

    @property
    def top(self) -> _Identifier:
        return self.triple[0]


class Tree(object):
    def __init__(self, top, branches: Iterable[Branch]):
        self.top = top
        self.branches = branches


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

def branches(g: graph.Graph) -> List[Branch]:
    """
    (b / buy-01
       :ARG0 (k / Kim)
       :ARG1 (a / apple :quant 3))

    [((None, 'TOP', 'b'), [
       (('b', 'instance', 'buy-01'), []),
       (('b', 'ARG0', 'k'), [
          (('k', 'instance', 'Kim'), [])
        ])
       (('b', 'ARG1', 'a'), [
          (('a', 'instance', 'apple'), []),
          (('a', 'quant', 3), [])
        ])
      ])
    ]
    """
    variables = g.variables()
    data = reversed(g.data)
    bs = []
    try:
        while data:
            bs.append(_branches(None, data, variables, strict))
    except IndexError:
        pass
    return bs


def interpret(t: graph.Tree, model: _model.Model):
    """
    Interpret tree *t* as a graph using *model*.
    """
    data = _interpret_node(t, model)
    return graph.Graph(data)


def _interpret_node(t: graph.Tree, model: _model.Model):
    data = []
    id, edges = t
    has_nodetype = False
    for edge in edges:
        if len(edge) == 2:
            role, target, epidata = *edge, []
        else:
            role, target, epidata = edge
        if role == '/':
            role = model.nodetype_role
            has_nodetype = True
        # atomic targets
        if is_atomic(target):
            nested = ()
        # nested nodes
        else:
            nested = target
            target = nested[0]
        data.append(model.normalize((id, role, target)))
        data.extend(epidata)
        # recurse to nested nodes
        if nested:
            data.append(Push(target))
            data.extend(_interpret_node(nested, model))
            data.append(POP)

    # ensure there is a triple for the node label
    if not has_nodetype:
        data.insert(0, (id, model.nodetype_role, None))

    return data

def configure(g: graph.Graph, model: _model.Model, strict=False):
    """
    Create a tree from a graph by making as few decisions as possible.
    """
    nodemap = {}
    data = list(reversed(_preconfigure(g, strict)))
    tree = _configure(g.top, data, g.variables(), nodemap, model, strict)
    # if any data remain, the graph was not properly annotated for a tree
    if data:
        _reconfigure(tree, data, nodemap, model)
    return tree

def _preconfigure(g, strict):
    """
    Arrange the triples and epidata for ordered traversal.

    Also perform some basic validation.
    """
    data = []
    epidata = g.epidata()
    pushed = set()
    for triple in g.triples():
        push, pops, others = None, [], []
        for epi in epidata.get(triple, []):
            if isinstance(epi, Push):
                if strict:
                    if push is not None:
                        raise LayoutError(
                            'multiple node contexts for the same triple: {}'
                            .format(triple))
                    if epi.id not in (triple[0], triple[1]):
                        raise LayoutError(
                            "node context '{}' invalid for triple: {}"
                            .format(epi.id, triple))
                    if epi.id in pushed:
                        raise LayoutError(
                            'multiple node contexts for the same node: {}'
                            .format(epi.id))
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
        # insert in this (reversed) order
        data.append((triple, others, push))
        data.extend(pops)
    return data

def _configure(id, data, variables, nodemap, model, strict):
    """
    Side-effects:
      * *data* is modified
      * nodemap is modified
    """
    edges = []
    node = (id, edges)
    nodemap[id] = node

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
            data.append((triple, epidata))
            break

        if push and push.id not in nodemap:
            target = _configure(
                push.id, data, variables, nodemap, model, strict)

        if role == model.nodetype_role:
            role = '/'

        # simplify structure if no epidata
        if epidata:
            edge = (role, target, epidata)
        else:
            edge = (role, target)

        edges.append(edge)

    return node


def has_valid_layout(g: graph.Graph):
    """
    Return True if *g* contains the information for a valid layout.

    Having a valid layout means that the graph data allows a
    depth-first traversal that reconstructs a spanning tree used for
    serialization.
    """
    tree, nodemap, remaining = _configure(data, model)
    return len(remaining) == 0


def reconfigure(g: graph.Graph, top=None):
    pass

def is_atomic(x):
    """
    Return `True` if *x* is a valid atomic value.
    """
    return x is None or isinstance(x, (str, int, float))

def _reconfigure(tree, data, nodemap, model):
    pass

def rearrange(g: graph.Graph):
    pass
def tree_node_identifiers(t: graph.Tree):
    """
    Return the list of node identifiers in the tree.
    """
    id, edges = t
    ids = [id]
    for _, target, *_ in edges:
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
