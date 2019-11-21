# -*- coding: utf-8 -*-

"""
Semantic models for interpreting graphs.
"""

from typing import (cast, Tuple, List, Dict, Set, Iterable, Mapping, Any)
import re
from collections import defaultdict

from penman.exceptions import ModelError
from penman.types import (
    Variable,
    Role,
    Constant,
    BasicTriple
)
from penman.graph import CONCEPT_ROLE


_ReificationSpec = Tuple[Role, Constant, Role, Role]
_Reified = Tuple[Constant, Role, Role]
_Reification = Tuple[BasicTriple, BasicTriple, BasicTriple]


class Model(object):
    """
    A semantic model for Penman graphs.

    The model defines things like valid roles and transformations.

    Args:
        top_variable: the variable of the graph's top
        top_role: the role linking the graph's top to the top node
        concept_role: the role associated with node concepts
        roles: a mapping of roles to associated data
        normalizations: a mapping of roles to normalized roles
        reifications: a list of 4-tuples used to define reifications
    """
    def __init__(self,
                 top_variable: Variable = 'top',
                 top_role: Role = ':TOP',
                 concept_role: Role = CONCEPT_ROLE,
                 roles: Mapping[Role, Any] = None,
                 normalizations: Mapping[Role, Role] = None,
                 reifications: Iterable[_ReificationSpec] = None):
        self.top_variable = top_variable
        self.top_role = top_role
        self.concept_role = concept_role

        if roles:
            roles = dict(roles)
        self.roles = roles or {}
        self._role_re = re.compile(
            '^({})$'.format(
                '|'.join(list(self.roles) + [top_role, concept_role])))

        if normalizations:
            normalizations = dict(normalizations)
        self.normalizations = normalizations or {}

        reifs: Dict[Role, List[_Reified]] = defaultdict(list)
        if reifications:
            for role, concept, source, target in reifications:
                reifs[role].append((concept, source, target))
        self.reifications = dict(reifs)

    def __eq__(self, other):
        if not isinstance(other, Model):
            return NotImplemented
        return (self.top_variable == other.top_variable
                and self.top_role == other.top_role
                and self.concept_role == other.concept_role
                and self.roles == other.roles
                and self.normalizations == other.normalizations
                and self.reifications == other.reifications)

    @classmethod
    def from_dict(cls, d):
        """Instantiate a model from a dictionary."""
        return cls(**d)

    def has_role(self, role: Role) -> bool:
        """
        Return `True` if *role* is defined by the model.

        If *role* is not in the model but a single deinversion of
        *role* is in the model, then `True` is returned. Otherwise
        `False` is returned, even if something like
        :meth:`canonicalize_role` could return a valid role.
        """
        return (self._has_role(role)
                or (role.endswith('-of') and self._has_role(role[:-3])))

    def _has_role(self, role: Role) -> bool:
        return self._role_re.match(role) is not None

    def is_role_inverted(self, role: Role) -> bool:
        """Return `True` if *role* is inverted."""
        return not self._has_role(role) and role.endswith('-of')

    def invert_role(self, role: Role) -> Role:
        """Invert *role*."""
        if not self._has_role(role) and role.endswith('-of'):
            inverse = role[:-3]
        else:
            inverse = role + '-of'
        return inverse

    def invert(self, triple: BasicTriple) -> BasicTriple:
        """
        Invert *triple*.

        This will invert or deinvert a triple regardless of its
        current state. :meth:`deinvert` will deinvert a triple only if
        it is already inverted. Unlike :meth:`canonicalize`, this will
        not perform multiple inversions or replace the role with a
        normalized form.
        """
        source, role, target = triple
        inverse = self.invert_role(role)
        # casting is just for the benefit of the type checker; it does
        # not actually check that target is a valid variable type
        target = cast(Variable, target)
        return (target, inverse, source)

    def deinvert(self, triple: BasicTriple) -> BasicTriple:
        """
        De-invert *triple* if it is inverted.

        Unlike :meth:`invert`, this only inverts a triple if the model
        considers it to be already inverted, otherwise it is left
        alone. Unlike :meth:`canonicalize`, this will not normalize
        multiple inversions or replace the role with a normalized
        form.
        """
        if self.is_role_inverted(triple[1]):
            triple = self.invert(triple)
        return triple

    def canonicalize_role(self, role: Role) -> Role:
        """
        Canonicalize *role*.

        Role canonicalization will do the following:

        * Ensure the role starts with `':'`

        * Normalize multiple inversions (e.g., `ARG0-of-of` becomes
          `ARG0`), but it does *not* change the direction of the role

        * Replace the resulting role with a normalized form if one is
          defined in the model
        """
        if role != '/' and not role.startswith(':'):
            role = ':' + role
        role = self._canonicalize_inversion(role)
        role = self.normalizations.get(role, role)
        return role

    def _canonicalize_inversion(self, role: Role) -> Role:
        invert = self.invert_role
        if not self._has_role(role):
            while True:
                prev = role
                inverse = invert(role)
                role = invert(inverse)
                if prev == role:
                    break
        return role

    def canonicalize(self, triple: BasicTriple) -> BasicTriple:
        """
        Canonicalize *triple*.

        See :meth:`canonicalize_role` for a description of how the
        role is canonicalized. Unlike :meth:`invert`, this does not
        swap the source and target of *triple*.
        """
        source, role, target = triple
        canonical = self.canonicalize_role(role)
        return (source, canonical, target)

    def is_reifiable(self, triple: BasicTriple) -> bool:
        """Return `True` if the role of *triple* can be reified."""
        return triple[1] in self.reifications

    def reify(self,
              triple: BasicTriple,
              variables: Set[Variable] = None) -> _Reification:
        """
        Return the three triples that reify *triple*.

        Note that, unless *variables* is given, the node variable
        for the reified node is not necessarily valid for the target
        graph. When incorporating the reified triples, this variable
        should then be replaced.

        If the role of *triple* does not have a defined reification, a
        :exc:`ModelError` is raised.

        Args:
            triple: the triple to reify
            variables: a set of variables that should not be used for
                the reified node's variable
        Returns:
            The 3-tuple of triples that reify *triple*.
        """
        source, role, target = triple
        if role not in self.reifications:
            raise ModelError("'{}' cannot be reified".format(role))
        concept, source_role, target_role = next(iter(self.reifications[role]))

        var = '_'
        if variables:
            i = 2
            while var in variables:
                var = '_{}'.format(i)
                i += 1

        return ((source, self.invert_role(source_role), var),
                (var, CONCEPT_ROLE, concept),
                (var, target_role, target))
