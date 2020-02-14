
"""
Definitions of tree structures.
"""

from typing import Dict, List, Set, Mapping, Any

from penman.types import (Variable, Branch, Node)


class Tree:
    """
    A tree structure.

    A tree is essentially a node that contains other nodes, but this
    Tree class is useful to contain any metadata and to provide
    tree-based methods.
    """

    __slots__ = 'node', 'metadata'

    def __init__(self,
                 node: Node,
                 metadata: Mapping[str, str] = None):
        self.node = node
        self.metadata = metadata or {}

    def __eq__(self, other) -> bool:
        if isinstance(other, Tree):
            other = other.node
        return self.node == other

    def __repr__(self) -> str:
        return f'Tree({self.node!r})'

    def __str__(self) -> str:
        s = _format(self.node, 2)
        return f'Tree(\n  {s})'

    def nodes(self) -> List[Node]:
        """
        Return the nodes in the tree as a flat list.
        """
        return _nodes(self.node)

    def reset_variables(self, fmt='{prefix}{j}') -> None:
        """
        Recreate node variables formatted using *fmt*.

        The *fmt* string can be formatted with the following values:

        - ``prefix``: first alphabetic character in the node's concept
        - ``i``: 0-based index of the current occurrence of the prefix
        - ``j``: 1-based index starting from the second occurrence
        """
        varmap: Dict[Variable, Variable] = {}
        used: Set[Variable] = set()
        for var, branches in self.nodes():
            if var not in varmap:
                concept = next((tgt for role, tgt in branches if role == '/'),
                               None)
                pre = _default_variable_prefix(concept)
                i = 0
                newvar = None
                while newvar is None or newvar in used:
                    newvar = fmt.format(
                        prefix=pre,
                        i=i,
                        j='' if i == 0 else i + 1)
                    i += 1
                used.add(newvar)
                varmap[var] = newvar

        self.node = _map_vars(self.node, varmap)


def _format(node: Node, level: int) -> str:
    var, branches = node
    next_level = level + 2
    indent = '\n' + ' ' * next_level
    branch_strings = [_format_branch(branch, next_level)
                      for branch in branches]
    return '({!r}, [{}{}])'.format(
        var, indent, (',' + indent).join(branch_strings))


def _format_branch(branch: Branch, level: int) -> str:
    role, target = branch
    if is_atomic(target):
        target = repr(target)
    else:
        target = _format(target, level)
    return f'({role!r}, {target})'


def _nodes(node: Node) -> List[Node]:
    var, branches = node
    ns = [] if var is None else [node]
    for _, target in branches:
        # if target is not atomic, assume it's a valid tree node
        if not is_atomic(target):
            ns.extend(_nodes(target))
    return ns


def _default_variable_prefix(concept: Any) -> Variable:
    """
    Return the variable prefix for *concept*.

    If *concept* is a non-empty string, the prefix is the first
    alphabetic character in the string, if there are any, downcased.
    Otherwise the prefix is ``'_'``.

    Examples:
        >>> default_variable_prefix('Alphabet')
        'a'
        >>> default_variable_prefix('chase-01')
        'c'
        >>> default_variable_prefix('"string"')
        's'
        >>> default_variable_prefix('_predicate_n_1"')
        'p'
        >>> default_variable_prefix(1)
        '_'
        >>> default_variable_prefix(None)
        '_'
        >>> default_variable_prefix('')
        '_'
    """
    prefix = '_'
    if concept and isinstance(concept, str):
        for c in concept:
            if c.isalpha():
                prefix = c.lower()
                break
    return prefix


def _map_vars(node, varmap):
    var, branches = node

    newbranches: List[Branch] = []
    for role, tgt in branches:
        if not is_atomic(tgt):
            tgt = _map_vars(tgt, varmap)
        elif role != '/' and tgt in varmap:
            tgt = varmap[tgt]
        newbranches.append((role, tgt))

    return (varmap[var], newbranches)


def is_atomic(x) -> bool:
    """
    Return ``True`` if *x* is a valid atomic value.

    Examples:
        >>> from penman.tree import is_atomic
        >>> is_atomic('a')
        True
        >>> is_atomic(None)
        True
        >>> is_atomic(3.14)
        True
        >>> is_atomic(('a', [('/', 'alpha')]))
        False
    """
    return x is None or isinstance(x, (str, int, float))
