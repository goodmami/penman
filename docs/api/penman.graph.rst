
penman.graph
============

.. automodule:: penman.graph

   .. autoclass:: Graph

      .. attribute:: top

	 The top variable.

      .. attribute:: triples

	 The list of triples that make up the graph.

      .. attribute:: epidata

	 Epigraphical data that describe how a graph is to be
	 expressed when serialized.

      .. attribute:: metadata

	 Metadata for the graph.

      .. automethod:: instances
      .. automethod:: edges
      .. automethod:: attributes
      .. automethod:: variables
      .. automethod:: reentrancies

   .. autoclass:: Triple

      .. autoattribute:: source
      .. autoattribute:: role
      .. autoattribute:: target

   .. autoclass:: Instance
      :show-inheritance:

   .. autoclass:: Edge
      :show-inheritance:

   .. autoclass:: Attribute
      :show-inheritance:
