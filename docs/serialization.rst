Notes on Serialization
======================

A PENMAN-serialized graph takes the form of a tree with labeled
reentrancies, so in deserialization it is first parsed directly into a
tree and then the pure graph is interpreted from it.

.. code-block:: lisp

   (b / bark-01
      :ARG0 (d / dog))

The above PENMAN string is parsed to the following tree:

.. code-block:: python

   Tree(('b', [(':instance', 'bark-01'),
               (':ARG0', ('d', [(':instance', 'dog')]))]))

The structure of a tree node is ``(var, branches)`` while the
structure of a branch is ``(role, target)``. The target of a branch
can be an atomic value or a tree node. This tree is then interpreted
to the following graph (triples and associated layout markers):

.. code-block:: python

   Graph(triples=[
          ('b', ':instance', 'bark-01'),
          ('b', ':ARG0', 'd'),
          ('d', ':instance', 'dog')
	 ],
	 epidata={
	  ('b', ':ARG0', 'd'): [Push('d')],
	  ('d', ':instance', 'dog'): [POP]
	 })

Serialization goes in the reverse order: from a pure graph to a tree
to a string.

Allowed Graphs
--------------

The Penman library robustly allows some kinds of invalid and
unconventional graphs.

**Unproblematic:**

.. code-block:: bash

   # Normal
   (a / a-label :ROLE (b / b-label))

   # Unlabeled nodes, edges
   (a :ROLE (b))
   (a / a-label : (b / b-label))
   (a : (b))

   # Cycles
   (a :ROLE (b :ROLE a))

   # Distributed nodes
   (a :ROLE (b :ROLE (c / c-label)) :ROLE2 (c :ATTR val))

**Allowed but Unconventional**

.. code-block:: bash

   # Empty
   ()

   # Missing edge target
   (a / a-label :ROLE )

   # Missing node label
   (a / :ROLE (b / b-label))

   # Inverted attributes
   (a / a-label :ARG0-of 2)

**Disallowed**

.. code-block:: bash

   # Disconnected (parseable as two separate graphs)
   (a / a-label)(b / b-label)

   # Missing identifiers
   (a :ROLE ( / b-label))

   # Misplaced label
   (a :ROLE (b) / a-label)

   # Multiple labels
   (a / a-label / another-label)


..
  Rules for Serialization
  -----------------------

  Node instatiation
  '''''''''''''''''


  The order of triples matters
  ''''''''''''''''''''''''''''

  Limitations
  '''''''''''
