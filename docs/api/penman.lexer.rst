
penman.lexer
============

.. automodule:: penman.lexer

   Module Constants
   ----------------

   .. data:: PATTERNS

      A dictionary mapping token names to regular expressions. For
      instance::

	'ROLE':  r':[^\s()\/,:~^]*'

      The token names are used later by the :class:`TokenIterator` to
      help with parsing.

   .. data:: PENMAN_RE

      A compiled regular expression pattern for lexing PENMAN graphs.

   .. data:: TRIPLE_RE

      A compiled regular expression pattern for lexing triple
      conjunctions.

   Module Functions
   ----------------

   .. autofunction:: lex

   Classes
   -------

   .. autoclass:: Token
      :members:

   .. autoclass:: TokenIterator
      :members:
