
penman
======

.. automodule:: penman

For basic usage, common functionality is available from the top-level
:mod:`penman` module. For more advanced usage, please use the full API
available via the submodules.

Users wanting to interact with graphs might find the :func:`decode` and
:func:`encode` functions a good place to start::

    >>> import penman
    >>> g = penman.decode('(w / want-01 :ARG0 (b / boy) :ARG1 (g / go :ARG0 b))')
    >>> g.top
    'w'
    >>> len(g.triples)
    6
    >>> [concept for _, _, concept in g.instances()]
    ['want-01', 'boy', 'go']
    >>> print(penman.encode(g, top='b'))
    (b / boy
       :ARG0-of (w / want-01
                   :ARG1 (g / go
                            :ARG0 b)))

The :func:`decode` and :func:`encode` functions work with one PENMAN
graph. The :func:`load` and :func:`dump` functions work with
collections of graphs.

Users who want to work with trees would use :func:`parse` and
:func:`format` instead::

   >>> import penman
   >>> t =  penman.parse('(w / want-01 :ARG0 (b / boy) :ARG1 (g / go :ARG0 b))')
   >>> var, branches = t.node
   >>> var
   'w'
   >>> len(branches)
   3
   >>> role, target = branches[2]
   >>> role
   ':ARG1'
   >>> print(penman.format(target))
   (g / go
      :ARG0 b)


Module Constants
----------------

.. data:: penman.__version__

   The software version string.

.. data:: penman.__version_info__

   The software version as a tuple.


Classes
-------

.. class:: Tree

   Alias of :exc:`penman.tree.Tree`.

.. class:: Triple

   Alias of :exc:`penman.graph.Triple`.

.. class:: Graph

   Alias of :exc:`penman.graph.Graph`.

.. class:: PENMANCodec

   Alias of :exc:`penman.codec.PENMANCodec`.


Module Functions
----------------

Trees
'''''

.. autofunction:: parse

.. autofunction:: iterparse

.. autofunction:: format

.. function:: interpret(t, model=None)

   Interpret a graph from the :class:`Tree` *t*.

   Alias of :func:`penman.layout.interpret`

Graphs
''''''

.. autofunction:: decode

.. autofunction:: iterdecode

.. autofunction:: encode

.. function:: configure(g, top=None, model=None)

   Configure a tree from the :class:`Graph` *g*.

   Alias of :func:`penman.layout.configure`

Corpus Files
''''''''''''

.. autofunction:: loads

.. autofunction:: load

.. autofunction:: dumps

.. autofunction:: dump

Triple Conjunctions
'''''''''''''''''''

.. autofunction:: parse_triples

.. autofunction:: format_triples


Exceptions
----------

.. exception:: PenmanError

   Alias of :exc:`penman.exceptions.PenmanError`.

.. exception:: DecodeError

   Alias of :exc:`penman.exceptions.DecodeError`.

.. _submodules:

Submodules
----------

- :doc:`penman.codec` -- Codec class for reading and writing PENMAN data
- :doc:`penman.constant` -- For working with constant values
- :doc:`penman.epigraph` -- Base classes for epigraphical markers
- :doc:`penman.exceptions` -- Exception classes
- :doc:`penman.graph` -- Classes for pure graphs
- :doc:`penman.layout` -- Conversion between trees and graphs
- :doc:`penman.model` -- Class for defining semantic models
- :doc:`penman.models` -- Pre-defined models
- :doc:`penman.surface` -- For working with surface alignments
- :doc:`penman.transform` -- Graph and tree transformation functions
- :doc:`penman.tree` -- Classes for trees


