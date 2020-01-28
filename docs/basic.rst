
Basic Usage
===========

This document will give an overview of how to use Penman as a tool and
as a library. For motivation, here's an example of its tool usage:

.. code-block:: console

   $ penman --indent 3 --compact <<< '(s / sleep-01 :polarity - :ARG0 (i / i))'
   (s / sleep-01 :polarity -
      :ARG0 (i / i))

And here's an example of its library usage:

.. code-block:: python

   >>> from penman import PENMANCodec
   >>> codec = PENMANCodec()
   >>> g = codec.decode('(s / sleep-01 :polarity - :ARG0 (i / i))')
   >>> g.triples.remove(('s', ':polarity', '-'))
   >>> print(PENMANCodec().encode(g))
   (s / sleep-01
      :ARG0 (i / i))


Using Penman as a Tool
----------------------

Once installed (see :doc:`setup`), the :command:`penman` command
becomes available. It allows you to perform some basic tasks with
PENMAN graphs without having to write any Python code. Run
:command:`penman --help` to get a synposis of its usage:

.. code-block:: console

   usage: penman [-h] [-V] [-v] [-q] [--model FILE | --amr] [--check]
                 [--indent N] [--compact] [--triples] [--make-variables FMT]
                 [--rearrange KEY] [--reconfigure KEY] [--canonicalize-roles]
                 [--reify-edges] [--dereify-edges] [--reify-attributes]
                 [--indicate-branches]
                 [FILE [FILE ...]]

   Read and write graphs in the PENMAN notation.

   positional arguments:
     FILE                  read graphs from FILEs instead of stdin

   optional arguments:
     -h, --help            show this help message and exit
     -V, --version         show program's version number and exit
     -v, --verbose         increase verbosity
     -q, --quiet           suppress output on <stdout> and <stderr>
     --model FILE          JSON model file describing the semantic model
     --amr                 use the AMR model
     --check               check graphs for compliance with the model

   formatting options:
     --indent N            indent N spaces per level ("no" for no newlines)
     --compact             compactly print node attributes on one line
     --triples             print graphs as triple conjunctions

   normalization options:
     --make-variables FMT  recreate node variables with FMT (e.g.: '{prefix}{j}')
     --rearrange KEY       reorder the branches of the tree
     --reconfigure KEY     reconfigure the graph layout with reordered triples
     --canonicalize-roles  canonicalize role forms
     --reify-edges         reify all eligible edges
     --dereify-edges       dereify all eligible edges
     --reify-attributes    reify all attributes
     --indicate-branches   insert triples to indicate tree structure

The :command:`penman` command can read input from stdin or from one or
more files. Output is printed to stdout. Options are available to
customize the formatting of the output, such as for controlling
indentation. Normalization options allow one to transform the graph in
predefined ways prior to serialization. For example:

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

   >>> from penman import PENMANCodec
   >>> codec = PENMANCodec()
   >>> g = codec.decode('(b / bark-01 :ARG0 (d / dog))')
   >>> g.instances()
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

Importing directly from the :mod:`penman` module allows for basic
usage of the library, but anything more advanced can take advantage of
the full API. See the :ref:`API documentation <submodules>` for more
information.
