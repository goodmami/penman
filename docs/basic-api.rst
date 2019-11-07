
API Documentation
=================

.. automodule:: penman

   .. contents:: Contents
      :local:

   Trees, Graphs and Triples
   -------------------------

   .. autoclass:: Tree
      :members:

   .. autoclass:: Graph
      :members:

   .. autoclass:: Triple

      .. autoattribute:: source
      .. autoattribute:: role
      .. autoattribute:: target


   Codec Classes
   -------------

   .. autoclass:: PENMANCodec
      :members:


   Serialization Functions
   -----------------------

   .. autofunction:: decode
   .. autofunction:: encode
   .. autofunction:: load
   .. autofunction:: loads
   .. autofunction:: dump
   .. autofunction:: dumps

   Utilities
   ---------

   .. autofunction:: lex

   Exceptions
   ----------

   .. autoexception:: PenmanError

   .. autoexception:: GraphError
      :show-inheritance:

   .. autoexception:: LayoutError
      :show-inheritance:

   .. autoexception:: DecodeError
      :show-inheritance:

   .. autoexception:: SurfaceError
      :show-inheritance:

   .. autoexception:: ModelError
      :show-inheritance:
