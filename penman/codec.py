# -*- coding: utf-8 -*-

"""
Serialization of PENMAN graphs.
"""

from typing import Optional, Type, Iterable, Iterator, Tuple
from collections import defaultdict
import re
import logging

from penman import (
    graph,
    layout,
    surface,
    model as _model,
    lexer)


_Identifier = graph._Identifier


class PENMANCodec(object):
    """
    An encoder/decoder for PENMAN-serialized graphs.
    """
    # The valid tokens for node identifers.
    IDENTIFIERS = 'SYMBOL',
    #: The valid non-node targets of edges.
    ATOMS = set(['SYMBOL', 'STRING', 'INTEGER', 'FLOAT'])

    def __init__(self, model: _model.Model = None):
        if model is None:
            model = _model.Model()
        self.model = model

    def decode(self, s: str, triples: bool = False) -> graph.Graph:
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
            data = self.parse_triples(s)
            g = graph.Graph(data)
        else:
            tree = self.parse(s)
            g = layout.interpret(tree, self.model)
        return g

    def parse(self, s: str):
        """
        Parse PENMAN-notation string *s* into its tree structure.

        Args:
            s: a string containing a single PENMAN-serialized graph
        Returns:
            The tree structure described by *s*.
        Example:
            >>> codec = PENMANCodec()
            >>> codec.parse('(b / bark :ARG1 (d / dog))')
            ('b', [('/', 'bark')], [('ARG1', ('d', [('/', 'dog')], []))])
        """
        tokens = lexer.lex(s, pattern=lexer.PENMAN_RE)
        return self._parse_node(tokens)

    def _parse_node(self, tokens: lexer.TokenIterator):
        """
        Parse a PENMAN node from *tokens*.

        Nodes have the following pattern::

            Node := '(' ID ('/' Label)? Edge* ')'
        """
        tokens.expect('LPAREN')

        id = tokens.expect(*self.IDENTIFIERS).value
        edges = []

        if tokens.peek().type == 'SLASH':
            edges.append(self._parse_node_label(tokens))

        while tokens.peek().type != 'RPAREN':
            edges.append(self._parse_edge(tokens))

        tokens.expect('RPAREN')

        return (id, edges)

    def _parse_node_label(self, tokens: lexer.TokenIterator):
        tokens.expect('SLASH')
        label = None
        # for robustness, don't assume next token is the label
        if tokens.peek().type in self.ATOMS:
            label = tokens.next().value
            if tokens.peek().type == 'ALIGNMENT':
                aln = self._parse_alignment(tokens, surface.Alignment)
                return ('/', label, [aln])
        # no alignment or maybe no label
        return ('/', label)

    def _parse_edge(self, tokens: lexer.TokenIterator):
        """
        Parse a PENMAN edge from *tokens*.

        Edges have the following pattern::

            Edge := Role (Constant | Node)
        """
        epidata = []
        role = tokens.expect('ROLE').text[1:]  # strip the leading :
        if tokens.peek().type == 'ALIGNMENT':
            epidata.append(
                self._parse_alignment(tokens, surface.RoleAlignment))
        target = None

        _next = tokens.peek()
        next_type = _next.type
        if next_type in self.ATOMS:
            target = tokens.next().value
            if tokens.peek().type == 'ALIGNMENT':
                epidata.append(
                    self._parse_alignment(tokens, surface.Alignment))
        elif next_type == 'LPAREN':
            target = self._parse_node(tokens)
        # for robustness in parsing, allow edges with no target:
        #    (x :ROLE :ROLE2...  <- followed by another role
        #    (x :ROLE )          <- end of node
        elif next_type not in ('ROLE', 'RPAREN'):
            tokens.raise_error('Expected: ATOM, LPAREN', token=_next)

        if epidata:
            return (role, target, epidata)
        else:
            return (role, target)

    def _parse_alignment(self,
                         tokens: lexer.TokenIterator,
                         cls: Type[surface.AlignmentMarker]):
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

    def parse_triples(self, s: str):
        tokens = lexer.lex(s, pattern=lexer.TRIPLE_RE)

        data = []
        while True:
            role = tokens.expect('SYMBOL').text
            tokens.expect('LPAREN')
            source = tokens.expect(*self.IDENTIFIERS).text
            tokens.expect('COMMA')
            _next = tokens.peek().type
            if _next in self.ATOMS:
                target = tokens.next().text
            elif _next == 'RPAREN':  # special case for robustness
                target = None
            tokens.expect('RPAREN')

            data.append((source, role, target))

            # continue only if triple is followed by ^
            if tokens.peek().type == 'CARET':
                tokens.next()
            else:
                break

        return data

    def encode(self,
               g: graph.Graph,
               triples: bool = False,
               indent: Optional[int] = -1,
               compact: bool = False) -> str:
        """
        Serialize the graph *g* into PENMAN notation.

        Args:
            g: the Graph object
            triples: if True, serialize as a conjunction of logical triples
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
            return self.format_triples(g, indent=(indent is not None))
        else:
            tree = layout.configure(g, self.model)
            return self.format(tree, indent=indent, compact=compact)

    def format(self, tree, indent: Optional[int] = -1, compact: bool = False):
        """
        Format *tree* into a PENMAN string.
        """
        ids = layout.tree_node_identifiers(tree) if compact else []
        return self._format_node(tree, indent, 0, set(ids))

    def _format_node(self,
                     node,
                     indent: Optional[int],
                     column: int,
                     ids: set) -> str:
        """
        Format tree *node* into a PENMAN string.
        """
        id, edges = node
        id = str(id)  # ids can be ints

        # unlabeled nodes; just return now
        if not edges:
            return '({})'.format(id)

        # determine appropriate joiner based on value of indent
        if indent is None:
            joiner = ' '
        else:
            if indent == -1:
                column += len(id) + 2  # +2 for ( and a space
            else:
                column += indent
            joiner = '\n' + ' ' * column

        # format the edges and join them
        # if ids is non-empty, all initial attributes are compactly
        # joined on the same line, otherwise they use joiner
        parts = []
        compact = bool(ids)
        for edge in edges:
            target = edge[1]
            if compact and (not layout.is_atomic(target) or target in ids):
                compact = False
                if parts:
                    parts = [' '.join(parts)]
            parts.append(self._format_edge(edge, indent, column, ids))
        # check if all edges can be compactly written
        if compact:
            parts = [' '.join(parts)]

        return '({} {})'.format(id, joiner.join(parts))

    def _format_edge(self, edge, indent, column, ids):
        """
        Format tree *edge* into a PENMAN string.
        """
        if len(edge) == 2:
            role, target, epidata = *edge, []
        else:
            role, target, epidata = edge

        if role != '/' and not role.startswith(':'):
            role = ':' + role

        role_epi = ''.join(str(epi) for epi in epidata if epi.mode == 1)
        target_epi = ''.join(str(epi) for epi in epidata if epi.mode == 2)

        if indent == -1:
            column += len(role) + len(role_epi) + 1 # +1 for :

        if target is None:
            target = ''
        elif not layout.is_atomic(target):
            target = self._format_node(target, indent, column, ids)


        return '{}{} {!s}{}'.format(
            role,
            role_epi,
            target,
            target_epi)

    def format_triples(self,
                       g: graph.Graph,
                       indent: bool = True):
        delim = ' ^\n' if indent else ' ^ '
        return delim.join(
            map('{0[1]}({0[0]}, {0[2]})'.format, g.triples())
        )
