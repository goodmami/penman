
Basic Usage
===========

This document will give an overview of how to use Penman as a tool and
as a library.


Penman Fundamentals
-------------------

The Penman package is a library for working with graphs in the PENMAN
format. Its primary job is thus parsing the serialized form into an
internal graph representation and format graphs into the serialized
form again. Once parsed, the graphs can be inspected and manipulated,
depending on one's needs.

The interpretation of PENMAN into the internal graph depends on a
semantic model. The default model works in most cases, but for people
working with Abstract Meaning Representation (AMR) data, the AMR model
will allow them to perform operations in a way that follows the
principles of AMR. Users may also define custom models if they need
more control.


Using Penman as a Tool
----------------------

Once installed (see :doc:`setup`), the :command:`penman` command
becomes available. It allows you to perform some basic tasks with
PENMAN graphs without having to write any Python code. Run
:command:`penman --help` to get a synposis of its usage:

.. code-block:: console

   $ penman --help
   usage: penman [-h] [-V] [--model FILE | --amr] [--indent N] [--compact]
                 [--triples] [--canonicalize-roles] [--reify-edges]
                 [--reify-attributes] [--indicate-branches]
                 [FILE [FILE ...]]

   Read and write graphs in the PENMAN notation.

   positional arguments:
     FILE                  read graphs from FILEs instead of stdin

   optional arguments:
     -h, --help            show this help message and exit
     -V, --version         show program's version number and exit
     --model FILE          JSON model file describing the semantic model
     --amr                 use the AMR model

   formatting options:
     --indent N            indent N spaces per level ("no" for no newlines)
     --compact             compactly print node attributes on one line
     --triples             print graphs as triple conjunctions

   normalization options:
     --canonicalize-roles  canonicalize role forms
     --reify-edges         reify all eligible edges
     --reify-attributes    reify all attributes
     --indicate-branches   insert triples to indicate tree structure

The :command:`penman` command can read input from stdin or from one or
more files. Currently it always outputs to stdout. Options are
available to customize the formatting of the output, such as for
controlling indentation. Normalization options allow one to transform
the graph in predefined ways prior to serialization. For example:

.. code-block:: console

   $ penman --amr --indent=3 --reify-edges <<< '(a / apple :quant 3)'
   (a / apple
      :ARG1-of (_ / have-quant-91
         :ARG2 3))


Using Penman as a Library
-------------------------

While the command-line utility is convenient, it does not expose all
the functionality that the Penman package has. For more sophisticated
uses, the API allows one to directly inspect trees and graphs,
construct and manipulate trees and graphs, further customize
serialization, interface with other systems, etc.

For example:

.. code-block:: python

   >>> from penman.codec import PENMANCodec
   >>> codec = PENMANCodec()
   >>> g = codec.decode('(b / bark-01 :ARG0 (d / dog))')
   >>> g.attributes()
   [Attribute(source='b', role=':instance', target='bark-01'), Attribute(source='d', role=':instance', target='dog')]
   >>> g.edges()
   [Edge(source='b', role=':ARG0', target='d')]
   >>> g.variables()
   {'d', 'b'}
   >>> print(codec.encode(g, top='d'))
   (d / dog
      :ARG0-of (b / bark-01))
   >>> g.triples.append(('b', ':polarity', '-'))
   >>> print(codec.encode(g))
   (b / bark-01
      :ARG0 (d / dog)
      :polarity -)

See the API documentation for more information.
