# -*- coding: utf-8 -*-

"""
Serialization of PENMAN graphs.
"""

from typing import Optional, Union, Iterable, Iterator, List
import logging

from penman.types import (
    Variable,
    Target,
    BasicTriple,
)
from penman.tree import (Tree, is_atomic)
from penman.graph import Graph
from penman.model import Model
from penman.lexer import (
    PENMAN_RE,
    TRIPLE_RE,
    lex,
    TokenIterator,
)
from penman import layout


logger = logging.getLogger(__name__)


class PENMANCodec(object):
    """
    An encoder/decoder for PENMAN-serialized graphs.
    """

    def __init__(self, model: Model = None):
        if model is None:
            model = Model()
        self.model = model

    def decode(self, s: str) -> Graph:
        """
        Deserialize PENMAN-notation string *s* into its Graph object.

        Args:
            s: a string containing a single PENMAN-serialized graph
        Returns:
            The :class:`~penman.graph.Graph` object described by *s*.
        Example:
            >>> codec = PENMANCodec()
            >>> codec.decode('(b / bark-01 :ARG0 (d / dog))')
            <Graph object (top=b) at ...>
        """
        tree = self.parse(s)
        return layout.interpret(tree, self.model)

    def iterdecode(self,
                   lines: Union[Iterable[str], str]) -> Iterator[Graph]:
        """
        Yield graphs parsed from *lines*.

        Args:
            lines: a string or open file with PENMAN-serialized graphs
        Returns:
            The :class:`~penman.graph.Graph` objects described in
            *lines*.
        """
        for tree in self.iterparse(lines):
            yield layout.interpret(tree, self.model)

    def iterparse(self, lines: Union[Iterable[str], str]) -> Iterator[Tree]:
        """
        Yield trees parsed from *lines*.

        Args:
            lines: a string or open file with PENMAN-serialized graphs
        Returns:
            The :class:`~penman.tree.Tree` object described in
            *lines*.
        """
        tokens = lex(lines, pattern=PENMAN_RE)
        while tokens and tokens.peek().type in ('COMMENT', 'LPAREN'):
            yield self._parse(tokens)

    def parse(self, s: str) -> Tree:
        """
        Parse PENMAN-notation string *s* into its tree structure.

        Args:
            s: a string containing a single PENMAN-serialized graph
        Returns:
            The tree structure described by *s*.
        Example:
            >>> codec = PENMANCodec()
            >>> codec.parse('(b / bark-01 :ARG0 (d / dog))')  # noqa
            Tree(('b', [('/', 'bark-01'), ('ARG0', ('d', [('/', 'dog')]))]))
        """
        tokens = lex(s, pattern=PENMAN_RE)
        return self._parse(tokens)

    def _parse(self, tokens: TokenIterator) -> Tree:
        metadata = self._parse_comments(tokens)
        node = self._parse_node(tokens)
        tree = Tree(node, metadata=metadata)
        logger.debug('Parsed: %s', tree)
        return tree

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
                    metadata[key] = value.rstrip()
        return metadata

    def _parse_node(self, tokens: TokenIterator):
        """
        Parse a PENMAN node from *tokens*.

        Nodes have the following pattern::

            Node := '(' ID ('/' Concept)? Edge* ')'
        """
        tokens.expect('LPAREN')

        var = None
        concept: Union[str, None]
        edges = []

        if tokens.peek().type != 'RPAREN':
            var = tokens.expect('SYMBOL').text
            if tokens.peek().type == 'SLASH':
                slash = tokens.next()
                # for robustness, don't assume next token is the concept
                if tokens.peek().type in ('SYMBOL', 'STRING'):
                    concept = tokens.next().text
                    if tokens.peek().type == 'ALIGNMENT':
                        concept += tokens.next().text
                else:
                    concept = None
                    logger.warning('Missing concept: %s', slash.line)
                edges.append(('/', concept))
            while tokens.peek().type != 'RPAREN':
                edges.append(self._parse_edge(tokens))

        tokens.expect('RPAREN')

        return (var, edges)

    def _parse_edge(self, tokens: TokenIterator):
        """
        Parse a PENMAN edge from *tokens*.

        Edges have the following pattern::

            Edge := Role (Constant | Node)
        """
        role_token = tokens.expect('ROLE')
        role = role_token.text
        if tokens.peek().type == 'ALIGNMENT':
            role += tokens.next().text

        target = None
        _next = tokens.peek()
        next_type = _next.type
        if next_type in ('SYMBOL', 'STRING'):
            target = tokens.next().text
            if tokens.peek().type == 'ALIGNMENT':
                target += tokens.next().text
        elif next_type == 'LPAREN':
            target = self._parse_node(tokens)
        # for robustness in parsing, allow edges with no target:
        #    (x :ROLE :ROLE2...  <- followed by another role
        #    (x :ROLE )          <- end of node
        elif next_type not in ('ROLE', 'RPAREN'):
            raise tokens.error('Expected: SYMBOL, STRING, LPAREN', token=_next)
        else:
            logger.warning('Missing target: %s', role_token.line)

        return (role, target)

    def parse_triples(self, s: str) -> List[BasicTriple]:
        """ Parse a triple conjunction from *s*."""
        tokens = lex(s, pattern=TRIPLE_RE)
        return self._parse_triples(tokens)

    def _parse_triples(self,
                       tokens: TokenIterator) -> List[BasicTriple]:
        target: Target
        triples = []
        strip_caret = False
        while True:
            role = tokens.expect('SYMBOL').text
            if strip_caret and role.startswith('^'):
                role = role[1:]
            tokens.expect('LPAREN')
            # SYMBOL may contain commas, so handle it here. If there
            # is no space between the comma and the next SYMBOL, they
            # will be grouped as one.
            symbol = tokens.expect('SYMBOL')
            source, comma, rest = symbol.text.partition(',')
            target = None
            if rest:  # role(a,b)
                target = rest
            else:
                if comma:  # role(a, b) OR role(a,)
                    _next = tokens.accept('SYMBOL')
                    if _next:
                        target = _next.text
                else:  # role(a , b) OR role(a ,b) OR role(a ,) OR role(a)
                    _next = tokens.accept('SYMBOL')
                    if not _next:  # role(a)
                        pass
                    elif _next.text == ',':  # role(a , b) OR role(a ,)
                        _next = tokens.accept('SYMBOL')
                        if _next:  # role(a , b)
                            target = _next.text
                    elif _next.text.startswith(','):  # role(a ,b)
                        target = _next.text[1:]
                    else:  # role(a b)
                        tokens.error("Expected: ','", token=_next)
            tokens.expect('RPAREN')

            if target is None:
                logger.warning('Triple without a target: %s', symbol.line)

            triples.append((source, role, target))

            # continue only if triple is followed by ^
            if tokens:
                _next = tokens.peek()
                if _next.type != 'SYMBOL' or not _next.text.startswith('^'):
                    break
                elif _next.text == '^':
                    strip_caret = False
                    tokens.next()
                else:
                    strip_caret = True
            else:
                break
        return triples

    def encode(self,
               g: Graph,
               top: Variable = None,
               indent: Union[int, None] = -1,
               compact: bool = False) -> str:
        """
        Serialize the graph *g* into PENMAN notation.

        Args:
            g: the Graph object
            top: if given, the node to use as the top in serialization
            indent: how to indent formatted strings
            compact: if ``True``, put initial attributes on the first line
        Returns:
            the PENMAN-serialized string of the Graph *g*
        Example:

            >>> codec = PENMANCodec()
            >>> codec.encode(Graph([('h', 'instance', 'hi')]))
            (h / hi)

        """
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
        parts = ['# ::{}{}'.format(key, ' ' + value if value else value)
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
            parts.append(self._format_edge(edge, indent, column, vars))
        # check if all edges can be compactly written
        if compact:
            parts = [' '.join(parts)]

        return f'({var!s} {joiner.join(parts)})'

    def _format_edge(self, edge, indent, column, vars):
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
            target = self._format_node(target, indent, column, vars)

        return f'{role}{sep}{target!s}'

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
        conjunction = [f'{role.lstrip(":")}({source}, {target})'
                       for source, role, target in triples]
        return delim.join(conjunction)
