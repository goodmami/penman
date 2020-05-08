.. Penman documentation master file, created by
   sphinx-quickstart on Tue Apr 23 22:53:04 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Penman's documentation!
==================================

.. sidebar:: Quick Links

  - `Project page <https://github.com/goodmami/penman>`_
  - `How to contribute <https://github.com/goodmami/penman/blob/master/CONTRIBUTING.md>`_
  - `Report a bug <https://github.com/goodmami/penman/issues>`_
  - `Changelog <https://github.com/goodmami/penman/blob/master/CHANGELOG.md>`_
  - `License (MIT) <https://github.com/goodmami/penman/blob/master/LICENSE>`_

The Penman package is a library for working with graphs in the PENMAN
format. Its primary job is thus parsing the serialized form into an
internal :class:`graph <penman.graph.Graph>` representation and format
graphs into the serialized form again. Once parsed, the graphs can be
inspected and manipulated, depending on one's needs.

The interpretation of PENMAN into the internal graph depends on a
semantic model. The default :class:`model <penman.model.Model>` works
in most cases, but for people working with `Abstract Meaning
Representation <https://amr.isi.edu/>`_ (AMR) data, the :mod:`AMR
model <penman.models.amr>` will allow them to perform operations in a
way that follows the principles of AMR. Users may also define custom
models if they need more control.

.. toctree::
   :maxdepth: 2
   :caption: Guides

   setup
   command
   library
   notation
   structures
   serialization

.. toctree::
   :maxdepth: 1
   :caption: API Reference:

   api/penman
   api/penman.codec
   api/penman.constant
   api/penman.epigraph
   api/penman.exceptions
   api/penman.graph
   api/penman.layout
   api/penman.model
   api/penman.models
   api/penman.surface
   api/penman.transform
   api/penman.tree


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
