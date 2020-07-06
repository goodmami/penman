# -*- coding: utf-8 -*-

"""
Semantic models for interpreting graphs.
"""

from typing import (
    cast, Optional, Tuple, List, Dict, Set, Iterable, Mapping, Any)
import re
from collections import defaultdict
import random

from penman.exceptions import ModelError
from penman.types import (
    Variable,
    Role,
    Constant,
    Target,
    BasicTriple
)
from penman.graph import CONCEPT_ROLE, Graph


_ReificationSpec = Tuple[Role, Constant, Role, Role]
_Reified = Tuple[Constant, Role, Role]
_Dereified = Tuple[Role, Role, Role]
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
        deifs: Dict[Constant, List[_Dereified]] = defaultdict(list)
        if reifications:
            for role, concept, source, target in reifications:
                reifs[role].append((concept, source, target))
                deifs[concept].append((role, source, target))
        self.reifications = dict(reifs)
        self.dereifications = dict(deifs)

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
        Return ``True`` if *role* is defined by the model.

        If *role* is not in the model but a single deinversion of
        *role* is in the model, then ``True`` is returned. Otherwise
        ``False`` is returned, even if something like
        :meth:`canonicalize_role` could return a valid role.
        """
        return (self._has_role(role)
                or (role.endswith('-of') and self._has_role(role[:-3])))

    def _has_role(self, role: Role) -> bool:
        return self._role_re.match(role) is not None

    def is_role_inverted(self, role: Role) -> bool:
        """Return ``True`` if *role* is inverted."""
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

        * Normalize multiple inversions (e.g., ``ARG0-of-of`` becomes
          ``ARG0``), but it does *not* change the direction of the role

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

    def is_role_reifiable(self, role: Role) -> bool:
        """Return ``True`` if *role* can be reified."""
        return role in self.reifications

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
        :exc:`~penman.exceptions.ModelError` is raised.

        Args:
            triple: the triple to reify
            variables: a set of variables that should not be used for
                the reified node's variable
        Returns:
            The 3-tuple of triples that reify *triple*.
        """
        source, role, target = triple
        if role not in self.reifications:
            raise ModelError(f"'{role}' cannot be reified")
        concept, source_role, target_role = next(iter(self.reifications[role]))

        var = '_'
        if variables:
            i = 2
            while var in variables:
                var = f'_{i}'
                i += 1

        return ((var, source_role, source),
                (var, CONCEPT_ROLE, concept),
                (var, target_role, target))

    def is_concept_dereifiable(self, concept: Target) -> bool:
        """Return ``True`` if *concept* can be dereified."""
        return concept in self.dereifications

    def dereify(self,
                instance_triple: BasicTriple,
                source_triple: BasicTriple,
                target_triple: BasicTriple) -> BasicTriple:
        """
        Return the triple that dereifies the three argument triples.

        If the target of *instance_triple* does not have a defined
        dereification, or if the roles of *source_triple* and
        *target_triple* do not match those for the dereification of
        the concept, a :exc:`~penman.exceptions.ModelError` is
        raised. A :exc:`ValueError` is raised if *instance_triple* is
        not an instance triple or any triple does not have the same
        source variable as the others.

        Args:
            instance_triple: the triple containing the node's concept
            source_triple: the source triple from the node
            target_triple: the target triple from the node
        Returns:
            The triple that dereifies the three argument triples.
        """
        if instance_triple[1] != CONCEPT_ROLE:
            raise ValueError('second argument is not an instance triple')
        if not (instance_triple[0] == source_triple[0] == target_triple[0]):
            raise ValueError('triples do not share the same source')

        concept = instance_triple[2]
        source_role = source_triple[1]
        target_role = target_triple[1]

        if concept not in self.dereifications:
            raise ModelError(f"{concept!r} cannot be dereified")
        for role, source, target in self.dereifications[concept]:
            if source == source_role and target == target_role:
                return (cast(Variable, source_triple[2]),
                        role,
                        target_triple[2])
            elif target == source_role and source == target_role:
                return (cast(Variable, target_triple[2]),
                        role,
                        source_triple[2])

        raise ModelError(f'{source_role!r} and {target_role!r} '
                         f'are not valid roles to dereify {concept!r}')

    def original_order(self, role: Role):
        """Role sorting key that does not change the order."""
        return True

    def alphanumeric_order(self, role: Role):
        """Role sorting key for alphanumeric order."""
        m = re.match(r'(.*\D)(\d+)$', role)
        if m:
            rolename = m.group(1)
            roleno = int(m.group(2))
        else:
            rolename, roleno = role, 0
        return rolename, roleno

    def canonical_order(self, role: Role):
        """Role sorting key that finds a canonical order."""
        return (self.is_role_inverted(role), self.alphanumeric_order(role))

    def random_order(self, role: Role):
        """Role sorting key that randomizes the order."""
        return random.random()

    def errors(self, graph: Graph) -> Dict[Optional[BasicTriple], List[str]]:
        """
        Return a description of model errors detected in *graph*.

        The description is a dictionary mapping a context to a list of
        errors. A context is a triple if the error is relevant for the
        triple, or ``None`` for general graph errors.

        Example:

            >>> from penman.models.amr import model
            >>> from penman.graph import Graph
            >>> g = Graph([('a', ':instance', 'alpha'),
            ...            ('a', ':foo', 'bar'),
            ...            ('b', ':instance', 'beta')])
            >>> for context, errors in model.errors(g).items():
            ...     print(context, errors)
            ...
            ('a', ':foo', 'bar') ['invalid role']
            ('b', ':instance', 'beta') ['unreachable']
        """
        err: Dict[Optional[BasicTriple], List[str]] = defaultdict(list)
        if len(graph.triples) == 0:
            err[None].append('graph is empty')
        else:
            g: Dict[Variable, List[BasicTriple]] = {}
            for triple in graph.triples:
                var, role, tgt = triple
                if not self.has_role(role):
                    err[triple].append('invalid role')
                if var not in g:
                    g[var] = []
                g[var].append(triple)
            if not graph.top:
                err[None].append('top is not set')
            elif graph.top not in g:
                err[None].append('top is not a variable in the graph')
            else:
                reachable = _dfs(g, graph.top)
                unreachable = set(g).difference(reachable)
                for uvar in sorted(unreachable):
                    for triple in g[uvar]:
                        err[triple].append('unreachable')
        return dict(err)


def _dfs(g, top):
    # just keep source and target of edge relations
    q = {var: {tgt for _, _, tgt in triples if tgt in g}
         for var, triples in g.items()}
    # make edges bidirectional
    for var, tgts in q.items():
        for tgt in tgts:
            if tgt not in q:
                q[tgt] = set()
            q[tgt].add(var)

    visited = set()
    agenda = [top]
    while agenda:
        cur = agenda.pop()
        if cur not in visited:
            visited.add(cur)
            agenda.extend(t for t in q.get(cur, []) if t not in visited)
    return visited
