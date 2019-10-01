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



def has_valid_layout(g: graph.Graph):
    """
    Return True if *g* contains the information for a valid layout.

    Having a valid layout means that the graph data allows a
    depth-first traversal that reconstructs a spanning tree used for
    serialization.
    """
    ## NEW
    return len(branches(g)) == 1
    ## OLD
    variables = g.variables()
    stack = []
    for datum in g._data:

        try:
            if datum is POP:
                stack.pop()
            # some other epidatum; ignore
            elif not isinstance(graph.Triple):
                continue
            # regular edge or attribute
            elif datum.source == stack[-1]:
                if isinstance(datum, graph.Edge):
                    stack.append(datum.target)
            # inverted edge
            elif datum.target == stack[-1]:
                assert isinstance(datum, graph.Edge)
                stack.append(datum.source)
            else:
                # neither the triple's source nor target connect to
                # the current branch
                return False

        except IndexError:
            # stack is empty but there are more triples to consider
            return False

        except AttributeError:
            raise LayoutError('Unexpected graph datum: {!r}'.format(datum))

    # full traversal complete
    return True


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

def _branches(node_id, data, variables, strict):
    children = []
    push_candidate = None
    while data:
        datum = data.pop()

        if datum is POP:
            break

        elif datum is PUSH:
            if push_candidate is None:
                if strict:
                    raise LayoutError('invalid layout')
            else:
                children.append(
                    _branches(push_candidate, data, variables, strict))

        elif not isinstance(datum, graph.Marker):
            source, role, target = datum
            # regular edge
            if source == node_id and target in variables:
                push_candidate = target
            # inverted edge
            elif target == node_id and source in variables:
                push_candidate = source
            # attribute
            elif node_id in (source, target):
                continue
            # misplaced triple
            else:
                data.append((source, role, target))
                break

    return node_id, children

    # source,
    # id, children = None, []
    # stack = []
    # for datum in g.data:

    #     try:
    #         if datum is POP:
    #             children = stack.pop()
    #         # some other marker; ignore
    #         elif isinstance(graph.Marker):
    #             continue
    #         # regular edge or attribute
    #         elif datum.source == stack[-1]:
    #             if isinstance(datum, graph.Edge):
    #                 stack.append(datum.target)
    #         # inverted edge
    #         elif datum.target == stack[-1]:
    #             assert isinstance(datum, graph.Edge)
    #             stack.append(datum.source)
    #         else:
    #             # neither the triple's source nor target connect to
    #             # the current branch
    #             return False

    #     except IndexError:
    #         # stack is empty but there are more triples to consider
    #         return False

    #     except AttributeError:
    #         raise LayoutError('Unexpected graph datum: {!r}'.format(datum))

    # # full traversal complete
    # return True

def interpret(t: graph.Tree, model: _model.Model):
    data = []
    _interpret(t, model, data)
    return graph.Graph(data)


def _interpret(t: graph.Tree, model: _model.Model, data):
    start_index = len(data)
    id, attrs, edges = t
    has_nodetype = False
    for edge in (attrs + edges):
        if len(edge) == 2:
            role, target, role_epi, target_epi = *edge, None, None
        else:
            role, role_epi, target, target_epi = edge
        if role == '/':
            role = model.nodetype_role
            has_nodetype = True
        # atomic targets
        if target is None or isinstance(target, (str, int, float)):
            nested = ()
        # nested nodes
        else:
            nested = target
            target = nested[0]
        data.append(model.normalize((id, role, target)))
        if role_epi:
            data.append(role_epi)
        if target_epi:
            data.append(target_epi)
        # recurse to nested nodes
        if nested:
            _interpret(nested, model, data)

    # ensure there is a triple for the node label
    if not has_nodetype:
        data.insert(start_index, (id, model.nodetype_role, None))


def configure(g: graph.Graph, model: _model.Model):
    """
    Create a tree from a graph by making as few decisions as possible.
    """
    pass


def reconfigure(g: graph.Graph, top=None):
    pass


def rearrange(g: graph.Graph):
    pass


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
