
penman.layout
=============

.. automodule:: penman.layout

Epigraphical Markers
--------------------

.. autoclass:: LayoutMarker
   :show-inheritance:

.. autoclass:: Push
   :show-inheritance:

.. autoclass:: Pop
   :show-inheritance:

.. autodata:: POP

   Using the :data:`POP` singleton can help reduce memory usage and
   processing time when working with many graphs, but it should
   **not** be checked for object identity, such as ``if x is POP``,
   when working with multiple processes because each process gets its
   own instance. Instead, use a type check such as ``isinstance(x,
   Pop)``.


Tree Functions
--------------

.. autofunction:: interpret
.. autofunction:: rearrange

Graph Functions
---------------

.. autofunction:: configure
.. autofunction:: reconfigure

Diagnostic Functions
--------------------

.. autofunction:: get_pushed_variable
.. autofunction:: appears_inverted
.. autofunction:: node_contexts
