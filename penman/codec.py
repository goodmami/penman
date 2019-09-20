# -*- coding: utf-8 -*-

"""
Serialization of PENMAN graphs.
"""

from typing import Type, Union, Iterable, Iterator, Tuple
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
    # The top id and role are implicit except in serialized triple
    # conjunctions
    TOP_ID = 'top'
    TOP_ROLE = 'TOP'
    # IDENTIFIERS are the valid tokens for node identifers
    IDENTIFIERS = 'SYMBOL', 'INTEGER'
    # ATOMS are the valid non-node targets of edges
    ATOMS = set(['SYMBOL', 'STRING', 'INTEGER', 'FLOAT'])
    # The special role / specifies a node's type/label/concept
    NODETYPE_ROLE = 'instance'

    def __init__(self, model: _model.Model = None):
        if model is None:
            model = _model.Model()
        self.model = model

    def decode(self, s: str, triples: bool = False) -> graph.Graph:
        """
        Deserialize PENMAN-notation string *s* into its Graph object.

        Args:
            s: a string containing a single PENMAN-serialized grap
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
        lines = s.splitlines()
        if triples:
            tokens = lexer.lex(lines, pattern=lexer.TRIPLE_RE)
            top, data = self.parse_triples(tokens)
        else:
            tokens = lexer.lex(lines, pattern=lexer.PENMAN_RE)
            top, data = self.parse_node(tokens)

        normalize = self.model.normalize
        data = [t if isinstance(t, graph.Epidatum) else normalize(t)
                for t in data]

        return graph.Graph(data, top=top)

    def parse_node(self, tokens: lexer.TokenIterator):
        """
        Parse a PENMAN node from *tokens*.

        The grammar rule for Nodes is::

            Node <- '(' Identifier Label? Edge* ')'

        Returns:
            A 2-tuple containing a node identifier and a list of graph
            data.
        """
        tokens.expect('LPAREN')
        token = tokens.expect(*self.IDENTIFIERS)
        id = token.value

        data = [layout.Push(id)]

        data.extend(self.parse_node_label(tokens, id))

        while tokens.peek_type() != 'RPAREN':
            data.extend(self.parse_edge(tokens, id))

        tokens.expect('RPAREN')
        data.append(layout.POP)

        return id, data

    def parse_node_label(self,
                         tokens: lexer.TokenIterator,
                         source: _Identifier):
        """
        Parse a PENMAN node label from *tokens*.

        The grammar rule for a Role is::

            Label <- '/' Atom

        Returns:
            A 2-tuple containing a role and a :class:`RoleAlignment`
        """
        data = []
        label = prefix = indices = None
        if tokens.accept('SLASH') is not None:
            if tokens.peek_type() in self.ATOMS:
                label = tokens.next().value
                data.extend(self.parse_alignment(tokens, surface.Alignment))
            else:
                pass  # return default label of None

        edge = (source, self.NODETYPE_ROLE, label)

        return [edge] + data

    def parse_edge(self,
                   tokens: lexer.TokenIterator,
                   source: _Identifier):
        """
        Parse a PENMAN edge originating at *source* from *tokens*.

        The grammar rule for an Edge is::

            Edge <- Role RoleAlignment? ( Atom Alignment? | Node )

        Valid Atoms are defined by the codec class. By default they
        include: `SYMBOL`, `STRING`, `INTEGER`, and `FLOAT`. If the
        Value is an Atom, the value itself is the target of an
        edge. If the Value is a Node, the Node's identifier is the
        target. Only Atoms may have Alignments. For robustness, a
        missing value (a role followed by another role or `')'`) is
        interpreted as a value of `None` rather than raising an error.

        Returns:
            A list of graph data.
        """
        data = []
        role = tokens.expect('ROLE').text[1:]  # strip :
        data.extend(self.parse_alignment(tokens, surface.RoleAlignment))

        _next = tokens.peek()
        next_type = _next.type
        if next_type in self.ATOMS:
            target = tokens.next().value
            data.extend(self.parse_alignment(tokens, surface.Alignment))
        elif next_type == 'LPAREN':
            target, _data = self.parse_node(tokens)
            data.extend(_data)
        # for robustness in parsing, allow edges with no target:
        #    (x :ROLE :ROLE2...  <- followed by another role
        #    (x :ROLE /...       <- followed by a node type
        #    (x :ROLE )          <- end of node
        elif next_type in ('ROLE', 'RPAREN'):
            target = None
        else:
            tokens.raise_error('Expected: ATOM, LPAREN', token=_next)

        edge = (source, role, target)

        return [edge] + data

    def parse_alignment(self,
                        tokens: lexer.TokenIterator,
                        cls: Type[surface.Alignment]):
        """
        Parse a PENMAN surface alignment from *tokens*.
        """
        token = tokens.accept('ALIGNMENT')
        if token is not None:
            m = re.match((r'~(?:(?P<prefix>[a-zA-Z])\.?)?'
                          r'(?P<indices>\d+(?:,\d+)*)'),
                         token.text)
            prefix = m.group('prefix')
            indices = list(map(int, m.group('indices').split(',')))
            return [cls(indices, prefix=prefix)]
        else:
            return []

    def parse_triples(self, tokens: lexer.TokenIterator):
        data = []
        while True:
            role = tokens.expect('SYMBOL').text
            tokens.expect('LPAREN')
            source = tokens.expect('SYMBOL', 'INTEGER').text
            tokens.expect('COMMA')
            _next = tokens.peek_type()
            if _next in self.ATOMS:
                target = tokens.next().text
            elif _next == 'RPAREN':  # special case for robustness
                target = None
            tokens.expect('RPAREN')

            data.append((source, role, target))

            # continue only if triple is followed by ^
            if tokens.peek_type() == 'CARET':
                tokens.next()
            else:
                break

        return graph.Graph(data)

    def encode(self,
               g: graph.Graph,
               triples: bool = False,
               indent: Union[int, bool] = None) -> str:
        """
        Serialize the graph *g* into PENMAN notation.

        Args:
            g: the Graph object
            triples: if True, serialize as a conjunction of logical triples
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
            return self.format_triples(g, indent=indent)
        else:
            tree = layout.assemble(g, top=top, model=self.model)
            return self.format_node(tree, indent=indent)

    def format_node(self,
                    tree: layout.Tree,
                    indent: Union[int, bool] = None) -> str:
        pass

    def format_triples(self,
                       g: graph.Graph,
                       indent: bool = True):
        delim = ' ^\n' if indent else ' ^ '
        return delim.join(
            map('{0[1]}({0[0]}, {0[2]})'.format, g.triples())
        )
