
PENMAN Notation
===============

PENMAN notation, originally called *Sentence Plan Notation* in the
`PENMAN project`_ ([KAS1989]_), is a serialization format for the
directed, rooted graphs used to encode semantic dependencies, most
notably in the `Abstract Meaning Representation`_ (AMR) framework. It
looks similar to Lisp's `S-Expressions`_ in using parentheses to
indicate nested structures. For example, here is an AMR for "He drives
carelessly.":

.. code-block:: text

   (d / drive-01
      :ARG0 (h / he)
      :manner (c / care-04
                 :polarity -))

Described below are a breakdown of the parts of the PENMAN graph above
as well as a formal grammar description of PENMAN graphs in general.


Graph Anatomy
-------------

The following diagram explains what each part of the graph above is:

.. code-block:: lisp

   ;    ┌────────────────────────── Variable (this one is the graph's top)
   ;    │     ┌──────────────────── Instance relation
   ;    ┴ ────┴─────
       (d / drive-01
   ;      ┬ ───┬────
   ;      |    └─────────────────── Concept (node label)
   ;      └──────────────────────── Indicates the node's concept
   ;            ┌────────────────── Edge relation
   ;      ──────┴───────
          :ARG0 (h / he)
   ;      ──┬──
   ;        └────────────────────── Role (edge label)
          :manner (c / care-04
   ;                      ┌──────── Attribute relation
   ;                 ─────┴─────
                     :polarity -))
   ;                           ┬
   ;                           └─── Atom (or "constant")

The linearized form can only describe projective structures such as
trees, so in order to capture non-projective graphs, nodes get
identifiers (called *variables*; e.g., ``d``, ``h``, and ``c`` above)
which can be referred to later to establish a reentrancy.

.. _`PENMAN project`: https://www.isi.edu/natural-language/penman/penman.html
.. _`Abstract Meaning Representation`: https://amr.isi.edu/
.. _`S-Expressions`: https://en.wikipedia.org/wiki/S-expression


Formal Grammar
--------------

PENMAN notation can be very roughly described with the following `BNF
<https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form>`_ grammar
(from [GOO2019]_):

.. code-block:: bnf

   <node> ::= '(' <id> '/' <node-label> <edge>* ')'
   <edge> ::= ':'<edge-label> (<const>|<id>|<node>)

A more complete description is given by the following `PEG
<https://en.wikipedia.org/wiki/Parsing_expression_grammar>`_
grammar. In addition to being more complete, it also extends the
grammar to allow for surface alignments.

.. code-block:: peg

   # Syntactic productions (whitespace is allowed around non-terminals)
   Start     <- Node
   Node      <- '(' Variable NodeLabel? Relation* ')'
   NodeLabel <- '/' Concept Alignment?
   Concept   <- Constant
   Relation  <- Role Alignment? (Node / Atom Alignment?)
   Atom      <- Variable / Constant
   Constant  <- String / Symbol
   Variable  <- Symbol

   # Lexical productions (whitespace is not allowed)
   Symbol    <- NameChar+
   Role      <- ':' NameChar*
   Alignment <- '~' ([a-zA-Z] '.'?)? Digit+ (',' Digit+)*
   String    <- '"' (!'"' (StrEscape / StrChar))* '"'
   StrEscape <- '\\' StrChar
   StrChar   <- ![\n\r\f\v] .
   NameChar  <- ![ \n\t\r\f\v"()/:~] .
   Digit     <- [0-9]

This grammar has some seemingly unnecessary ambiguity in that both the
``Variable`` and ``Constant`` alternatives for ``Atom`` can resolve to
``Symbol``, but it is written this way to accommodate syntax variants
that further restrict the form of variables. Also, the distinction
between edge relations and attribute relations is semantic: if the
target of a relation is the variable of some other node, then it is an
edge, otherwise it is an attribute.

Note that the implementation in the Penman package deviates from this
grammar in that the ``Alignment`` production is not parsed together
with the rest of the structure. Instead, the ``~`` character is
allowed on ``NameChar`` and alignments are thus part of the ``Role``
or ``Atom`` tokens. They are later detected and extracted during
graph interpretation (see :func:`penman.layout.interpret`).

.. [KAS1989] Robert T. Kaspar. A Flexible Interface for Linking
             Applications to Penman's Sentence Generator. Speech and
             Natural Language: Proceedings of a Workshop Held at
             Philadelphia, Pennsylvania.
	     http://www.aclweb.org/anthology/H89-1022.
	     February 21-23, 1989.

.. [GOO2019] Michael Wayne Goodman. AMR Normalization for Fairer
	     Evaluation.  Proceedings of the 33rd Pacific Asia
	     Conference on Language, Information, and Computation
	     (PACLIC 33). https://arxiv.org/pdf/1909.01568.pdf. 2019.
