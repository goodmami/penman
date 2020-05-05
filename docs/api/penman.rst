
penman
======

.. automodule:: penman

For basic usage, and to retain some backward compatibility with early
versions, common functionality is available from the top-level
:mod:`penman` module. For more advanced usage, please use the full API
available via the submodules.

.. _submodules:

Submodules
----------

Data Structures
'''''''''''''''

- :doc:`penman.epigraph` -- Base classes for epigraphical markers
- :doc:`penman.graph` -- Classes for pure graphs
- :doc:`penman.model` -- Class for defining semantic models
- :doc:`penman.models` -- Pre-defined models
- :doc:`penman.surface` -- Classes for surface alignments
- :doc:`penman.tree` -- Classes for trees

Serialization
'''''''''''''

- :doc:`penman.constant` -- For working with constant values
- :doc:`penman.codec` -- Codec class for reading and writing PENMAN data
- :doc:`penman.layout` -- Conversion between trees and graphs

Other
'''''

- :doc:`penman.exceptions` -- Exception classes
- :doc:`penman.transform` -- Graph and tree transformation functions


Module Constants
----------------

.. data:: penman.__version__

   The software version string.

.. data:: penman.__version_info__

   The software version as a tuple.


Classes
-------

.. class:: Triple

   Alias of :exc:`penman.graph.Triple`.

.. class:: Tree

   Alias of :exc:`penman.tree.Tree`.

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

.. function:: configure(g, top=None, model=None, strict=False)

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
