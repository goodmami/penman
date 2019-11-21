# -*- coding: utf-8 -*-

"""
Serialization of PENMAN graphs.
"""

from typing import Optional, Union, Type, Iterable, Iterator, List
import re

from penman.types import (
    Variable,
    Target,
    BasicTriple,
)
from penman.tree import (Tree, is_atomic)
from penman.graph import Graph
from penman.model import Model
from penman.surface import (
    AlignmentMarker,
    Alignment,
    RoleAlignment,
)
from penman.lexer import (
    PENMAN_RE,
    TRIPLE_RE,
    lex,
    TokenIterator,
)
from penman import layout


class PENMANCodec(object):
    """
    An encoder/decoder for PENMAN-serialized graphs.
    """
    # The valid tokens for node identifiers (variables).
    IDENTIFIERS = 'SYMBOL',
    #: The valid non-node targets of edges.
    ATOMS = set(['SYMBOL', 'STRING', 'INTEGER', 'FLOAT'])

    def __init__(self, model: Model = None):
        if model is None:
            model = Model()
        self.model = model

    def decode(self, s: str, triples: bool = False) -> Graph:
        """
        Deserialize PENMAN-notation string *s* into its Graph object.

        Args:
            s: a string containing a single PENMAN-serialized graph
            triples: if `True`, parse *s* as a triple conjunction
        Returns:
            The :class:`Graph` object described by *s*.
        Example:
            >>> codec = PENMANCodec()
            >>> codec.decode('(b / bark :ARG1 (d / dog))')
            <Graph object (top=b) at ...>
            >>> codec.decode(
            ...     'instance(b, bark) ^ instance(d, dog) ^ ARG1(b, d)',
            ...     triples=True
            ... )
            <Graph object (top=b) at ...>
        """
        if triples:
            _triples = self.parse_triples(s)
            g = Graph(_triples)
        else:
            tree = self.parse(s)
            g = layout.interpret(tree, self.model)
        return g

    def iterdecode(self,
                   lines: Union[Iterable[str], str],
                   triples: bool = False) -> Iterator[Graph]:
        """
        Yield graphs parsed from *lines*.

        Args:
            lines: a string or open file with PENMAN-serialized graphs
            triples: if `True`, parse *s* as a triple conjunction
        Returns:
            The :class:`Graph` objects described in *lines*.
        """
        if triples:
            tokens = lex(lines, pattern=TRIPLE_RE)
            while tokens:
                _triples = self._parse_triples(tokens)
                yield Graph(_triples)
        else:
            for tree in self.iterparse(lines):
                yield layout.interpret(tree, self.model)

    def iterparse(self, lines: Union[Iterable[str], str]) -> Iterator[Tree]:
        """
        Yield trees parsed from *lines*.

        Args:
            lines: a string or open file with PENMAN-serialized graphs
        Returns:
            The :class:`Tree` object described in *lines*.
        """
        tokens = lex(lines, pattern=PENMAN_RE)
        while tokens and tokens.peek().type in ('COMMENT', 'LPAREN'):
            metadata = self._parse_comments(tokens)
            node = self._parse_node(tokens)
            yield Tree(node, metadata=metadata)

    def parse(self, s: str) -> Tree:
        """
        Parse PENMAN-notation string *s* into its tree structure.

        Args:
            s: a string containing a single PENMAN-serialized graph
        Returns:
            The tree structure described by *s*.
        Example:
            >>> codec = PENMANCodec()
            >>> codec.parse('(b / bark :ARG1 (d / dog))')  # noqa
            Tree(('b', [('/', 'bark', []), ('ARG1', ('d', [('/', 'dog', [])]), [])]))
        """
        tokens = lex(s, pattern=PENMAN_RE)
        metadata = self._parse_comments(tokens)
        node = self._parse_node(tokens)
        return Tree(node, metadata=metadata)

    def _parse_comments(self, tokens: TokenIterator):
        """
        Parse PENMAN comments from *tokens* and return any metadata.
        """
        metadata = {}
        while tokens.peek().type == 'COMMENT':
            comment = tokens.next().text
            while comment:
                comment, found, meta = comment.rpartition('::')
                if found:
                    key, _, value = meta.partition(' ')
                    metadata[key] = value
        return metadata

    def _parse_node(self, tokens: TokenIterator):
        """
        Parse a PENMAN node from *tokens*.

        Nodes have the following pattern::

            Node := '(' ID ('/' Concept)? Edge* ')'
        """
        tokens.expect('LPAREN')

        var = None
        edges = []

        if tokens.peek().type != 'RPAREN':
            var = tokens.expect(*self.IDENTIFIERS).value
            if tokens.peek().type == 'SLASH':
                edges.append(self._parse_node_label(tokens))
            while tokens.peek().type != 'RPAREN':
                edges.append(self._parse_edge(tokens))

        tokens.expect('RPAREN')

        return (var, edges)

    def _parse_node_label(self, tokens: TokenIterator):
        tokens.expect('SLASH')
        concept = None
        epis = []
        # for robustness, don't assume next token is the concept
        if tokens.peek().type in self.ATOMS:
            concept = tokens.next().value
            if tokens.peek().type == 'ALIGNMENT':
                epis.append(
                    self._parse_alignment(tokens, Alignment))
        return ('/', concept, epis)

    def _parse_edge(self, tokens: TokenIterator):
        """
        Parse a PENMAN edge from *tokens*.

        Edges have the following pattern::

            Edge := Role (Constant | Node)
        """
        epidata = []
        role = tokens.expect('ROLE').text
        if tokens.peek().type == 'ALIGNMENT':
            epidata.append(
                self._parse_alignment(tokens, RoleAlignment))
        target = None

        _next = tokens.peek()
        next_type = _next.type
        if next_type in self.ATOMS:
            target = tokens.next().value
            if tokens.peek().type == 'ALIGNMENT':
                epidata.append(
                    self._parse_alignment(tokens, Alignment))
        elif next_type == 'LPAREN':
            target = self._parse_node(tokens)
        # for robustness in parsing, allow edges with no target:
        #    (x :ROLE :ROLE2...  <- followed by another role
        #    (x :ROLE )          <- end of node
        elif next_type not in ('ROLE', 'RPAREN'):
            raise tokens.error('Expected: ATOM, LPAREN', token=_next)

        return (role, target, epidata)

    def _parse_alignment(self,
                         tokens: TokenIterator,
                         cls: Type[AlignmentMarker]):
        """
        Parse a PENMAN surface alignment from *tokens*.
        """
        token = tokens.expect('ALIGNMENT')
        m = re.match((r'~(?P<prefix>[a-zA-Z]\.?)?'
                      r'(?P<indices>\d+(?:,\d+)*)'),
                     token.text)
        if m is not None:
            prefix = m.group('prefix')
            indices = tuple(map(int, m.group('indices').split(',')))
        else:
            prefix, indices = None, ()
        return cls(indices, prefix=prefix)

    def parse_triples(self, s: str) -> List[BasicTriple]:
        """ Parse a triple conjunction from *s*."""
        tokens = lex(s, pattern=TRIPLE_RE)
        return self._parse_triples(tokens)

    def _parse_triples(self,
                       tokens: TokenIterator) -> List[BasicTriple]:
        target: Target
        triples = []
        while True:
            role = tokens.expect('SYMBOL').text
            tokens.expect('LPAREN')
            source = tokens.expect(*self.IDENTIFIERS).text
            tokens.expect('COMMA')
            _next = tokens.peek().type
            if _next in self.ATOMS:
                target = tokens.next().value
            elif _next == 'RPAREN':  # special case for robustness
                target = None
            tokens.expect('RPAREN')

            triples.append((source, role, target))

            # continue only if triple is followed by ^
            if tokens.peek().type == 'CARET':
                tokens.next()
            else:
                break
        return triples

    def encode(self,
               g: Graph,
               top: Variable = None,
               triples: bool = False,
               indent: Union[int, None] = -1,
               compact: bool = False) -> str:
        """
        Serialize the graph *g* into PENMAN notation.

        Args:
            g: the Graph object
            top: if given, the node to use as the top in serialization
            triples: if `True`, serialize as a conjunction of triples
            indent: how to indent formatted strings
            compact: if `True`, put initial attributes on the first line
        Returns:
            the PENMAN-serialized string of the Graph *g*
        Example:

            >>> codec = PENMANCodec()
            >>> codec.encode(Graph([('h', 'instance', 'hi')]))
            (h / hi)
            >>> codec.encode(Graph([('h', 'instance', 'hi')]),
            ...                      triples=True)
            instance(h, hi)

        """
        if triples:
            return self.format_triples(
                g.triples,
                indent=(indent is not None))
        else:
            tree = layout.configure(g, top=top, model=self.model)
            return self.format(tree, indent=indent, compact=compact)

    def format(self,
               tree: Tree,
               indent: Union[int, None] = -1,
               compact: bool = False) -> str:
        """
        Format *tree* into a PENMAN string.
        """
        if not isinstance(tree, Tree):
            tree = Tree(tree)
        vars = [var for var, _ in tree.nodes()] if compact else []
        parts = ['# ::{} {}'.format(key, value)
                 for key, value in tree.metadata.items()]
        parts.append(self._format_node(tree.node, indent, 0, set(vars)))
        return '\n'.join(parts)

    def _format_node(self,
                     node,
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
            return '({!s})'.format(var)  # var-only node

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
            parts.append(self._format_edge(edge, indent, column, vars))
        # check if all edges can be compactly written
        if compact:
            parts = [' '.join(parts)]

        return '({!s} {})'.format(var, joiner.join(parts))

    def _format_edge(self, edge, indent, column, vars):
        """
        Format tree *edge* into a PENMAN string.
        """
        role, target, epidata = edge

        if role != '/' and not role.startswith(':'):
            role = ':' + role

        role_epi = ''.join(str(epi) for epi in epidata if epi.mode == 1)
        target_epi = ''.join(str(epi) for epi in epidata if epi.mode == 2)

        if indent == -1:
            column += len(role) + len(role_epi) + 1  # +1 for :

        if target is None:
            target = ''
        elif not is_atomic(target):
            target = self._format_node(target, indent, column, vars)

        return '{}{} {!s}{}'.format(
            role,
            role_epi,
            target,
            target_epi)

    def format_triples(self,
                       triples: Iterable[BasicTriple],
                       indent: bool = True):
        """
        Return the formatted triple conjunction of *triples*.

        Args:
            triples: an iterable of triples
            indent: how to indent formatted strings
        Returns:
            the serialized triple conjunction of *triples*
        Example:
            >>> codec = PENMANCodec()
            >>> codec.format_triples([('a', ':instance', 'alpha'),
            ...                       ('a', ':ARG0', 'b'),
            ...                       ('b', ':instance', 'beta')])
            ...
            'instance(a, alpha) ^\\nARG0(a, b) ^\\ninstance(b, beta)'

        """
        delim = ' ^\n' if indent else ' ^ '
        # need to remove initial : on roles for triples
        conjunction = ['{}({}, {})'.format(role.lstrip(':'), source, target)
                       for source, role, target in triples]
        return delim.join(conjunction)
