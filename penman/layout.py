# -*- coding: utf-8 -*-

import re


POP = None  # singleton for indicating where a branch ends


def original_order(triples):
    """
    Return a list of triples in the original order.
    """
    return triples


def out_first_order(triples):
    """
    Sort a list of triples so outward (true) edges appear first.
    """
    return sorted(triples, key=lambda t: t.inverted)


def alphanum_order(triples):
    """
    Sort a list of triples by relation name.

    Embedded integers are sorted numerically, but otherwise the sorting
    is alphabetic.
    """
    return sorted(
        triples,
        key=lambda t: [
            int(t) if t.isdigit() else t
            for t in re.split(r'([0-9]+)', t.relation or '')
        ]
    )


def inspect(g):
    stack = []
    for t in g._triples:
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
