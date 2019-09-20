# -*- coding: utf-8 -*-

"""
Semantic models for interpreting graphs.
"""

from penman import graph

class Model(object):
    def __init__(self, relations=None):
        if not relations:
            relations = {}
        self.relations = relations

    def is_inverted(self, triple: graph.BasicTriple) -> bool:
        role = triple[1]
        return role not in self.relations and role.endswith('-of')

    def invert(self, triple: graph.BasicTriple) -> graph.BasicTriple:
        source, role, target = triple
        if role in self.relations:
            inverse = self.relations[role].get('inverse', role + '-of')
        elif role.endswith('-of'):
            inverse = role[:-3]
        else:
            inverse = role + '-of'
        return (target, inverse, source)

    def normalize(self, triple: graph.BasicTriple) -> graph.BasicTriple:
        if self.is_inverted(triple):
            triple = self.invert(triple)
        return triple

    def is_reifiable(self, triple: graph.BasicTriple) -> bool:
        relation_data = self.relations.get(triple.role, {})
        return len(relation_data.get('reifications', [])) > 0

    def reify(self, triple:graph.BasicTriple) -> bool:
        pass
