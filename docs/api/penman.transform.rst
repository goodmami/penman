
penman.transform
================

.. automodule:: penman.transform

   .. seealso::

      The transformation functions in this module alter the content of
      the graph. Other functions may change the shape or form of the
      graph without altering its content, such as:

      - :func:`penman.layout.rearrange`
      - :func:`penman.layout.reconfigure`
      - :meth:`penman.tree.Tree.reset_variables()`

   .. autofunction:: canonicalize_roles
   .. autofunction:: reify_edges
   .. autofunction:: dereify_edges
   .. autofunction:: reify_attributes
   .. autofunction:: indicate_branches
