# -*- coding: utf-8 -*-

import re


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
