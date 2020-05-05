
from typing import Optional, Union, List, Iterable

from penman.types import BasicTriple
from penman.tree import (Tree, is_atomic)


def format(tree: Tree,
           indent: Union[int, None] = -1,
           compact: bool = False) -> str:
    """
    Format *tree* into a PENMAN string.

    Args:
        tree: a Tree object
        indent: how to indent formatted strings
        compact: if ``True``, put initial attributes on the first line
    Returns:
        the PENMAN-serialized string of the Tree *t*
    Example:
        >>> import penman
        >>> print(penman.format(
        ...     ('b', [('/', 'bark-01'),
        ...            (':ARG0', ('d', [('/', 'dog')]))])))
        (b / bark-01
           :ARG0 (d / dog))
    """
    if not isinstance(tree, Tree):
        tree = Tree(tree)
    vars = [var for var, _ in tree.nodes()] if compact else []
    parts = ['# ::{}{}'.format(key, ' ' + value if value else value)
             for key, value in tree.metadata.items()]
    parts.append(_format_node(tree.node, indent, 0, set(vars)))
    return '\n'.join(parts)


def format_triples(triples: Iterable[BasicTriple], indent: bool = True) -> str:
    """
    Return the formatted triple conjunction of *triples*.

    Args:
        triples: an iterable of triples
        indent: how to indent formatted strings
    Returns:
        the serialized triple conjunction of *triples*
    Example:
        >>> import penman
        >>> g = penman.decode('(b / bark-01 :ARG0 (d / dog))')
        >>> print(penman.format_triples(g.triples))
        instance(b, bark-01) ^
        ARG0(b, d) ^
        instance(d, dog)

    """
    delim = ' ^\n' if indent else ' ^ '
    # need to remove initial : on roles for triples
    conjunction = [f'{role.lstrip(":")}({source}, {target})'
                   for source, role, target in triples]
    return delim.join(conjunction)


def _format_node(node,
                 indent: Optional[int],
                 column: int,
                 vars: set) -> str:
    """
    Format tree *node* into a PENMAN string.
    """
    var, edges = node
    if not var:
        return '()'  # empty node
    if not edges:
        return f'({var!s})'  # var-only node

    # determine appropriate joiner based on value of indent
    if indent is None:
        joiner = ' '
    else:
        if indent == -1:
            column += len(str(var)) + 2  # +2 for ( and a space
        else:
            column += indent
        joiner = '\n' + ' ' * column

    # format the edges and join them
    # if vars is non-empty, all initial attributes are compactly
    # joined on the same line, otherwise they use joiner
    parts: List[str] = []
    compact = bool(vars)
    for edge in edges:
        target = edge[1]
        if compact and (not is_atomic(target) or target in vars):
            compact = False
            if parts:
                parts = [' '.join(parts)]
        parts.append(_format_edge(edge, indent, column, vars))
    # check if all edges can be compactly written
    if compact:
        parts = [' '.join(parts)]

    return f'({var!s} {joiner.join(parts)})'


def _format_edge(edge, indent, column, vars):
    """
    Format tree *edge* into a PENMAN string.
    """
    role, target = edge

    if role != '/' and not role.startswith(':'):
        role = ':' + role

    if indent == -1:
        column += len(role) + 1  # +1 for :

    sep = ' '
    if not target:
        target = sep = ''
    elif not is_atomic(target):
        target = _format_node(target, indent, column, vars)

    return f'{role}{sep}{target!s}'
