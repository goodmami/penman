# -*- coding: utf-8 -*-

"""
Semantic models for interpreting graphs.
"""

from typing import cast

from penman import graph

class Model(object):

    def __init__(self,
                 top_identifier:str = 'top',
                 top_role:str = 'TOP',
                 nodetype_role:str = 'instance',
                 relations:dict = None):
        self.top_identifier = top_identifier
        self.top_role = top_role
        self.nodetype_role = nodetype_role
        self.relations = relations or {}

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def is_inverted(self, triple: graph.BasicTriple) -> bool:
        return self.is_role_inverted(triple[1])

    def is_role_inverted(self, role: str) -> bool:
        return role not in self.relations and role.endswith('-of')

    def invert(self, triple: graph.BasicTriple) -> graph.BasicTriple:
        source, role, target = triple
        if role in self.relations:
            inverse = self.relations[role].get('inverse', role + '-of')
        elif role.endswith('-of'):
            inverse = role[:-3]
        else:
            inverse = role + '-of'

        # casting is just for the benefit of the type checker; it does
        # not actually check that target is a valid identifier type
        target = cast(graph._Identifier, target)

        return (target, inverse, source)

    def normalize(self, triple: graph.BasicTriple) -> graph.BasicTriple:
        if self.is_role_inverted(triple[1]):
            triple = self.invert(triple)
        return triple

    def is_reifiable(self, triple: graph.BasicTriple) -> bool:
        relation_data = self.relations.get(triple[1], {})
        return len(relation_data.get('reifications', [])) > 0

    def reify(self, triple:graph.BasicTriple) -> bool:
        pass
