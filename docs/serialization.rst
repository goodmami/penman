Notes on Serialization
======================

A PENMAN-serialized graph takes the form of a tree with labeled
reentrancies, so in deserialization it is first parsed directly into a
tree and then the pure graph is interpreted from it.

.. code:: lisp

   (b / bark
      :ARG0 (d / dog))

The above PENMAN string is parsed to the following tree:

.. code:: python

   ('b', [('instance', 'bark', []),
          ('ARG0', ('d', [('instance', 'dog', [])]), [])])

The structure of a tree node is ``(id, branches)`` while the structure
of a branch is ``(role, target, epidata)``. The target of a branch can
be an atomic value or a tree node. The epidata field is a list of
epigraphical markers. This tree is then interpreted to the following
triples (which define a pure graph; the epidata is stored separately
but is not shown here as it is empty for this example):

.. code:: python

   [('b', 'instance', 'bark'),
    ('b', 'ARG0', 'd'),
    ('d', 'instance', 'dog')]

Serialization goes in the reverse order: from a pure graph to a tree
to a string.

Rules for Serialization
-----------------------

Node instatiation
'''''''''''''''''


The order of triples matters
''''''''''''''''''''''''''''

Limitations
'''''''''''
