
.. highlight:: console

Installation and Setup
======================

Penman releases are available on `PyPI`_ and the source code is on
`GitHub`_.


Requirements
------------

The Penman package runs with `Python 3.8`_ and higher versions, but
otherwise it has no dependencies beyond Python's standard library.

Installation
------------

Install the latest version from `PyPI`_ with :command:`pip`::

  $ pip install penman

This command makes the ``penman`` module available in your Python
environment and as well as the :command:`penman` command at the
command line.


For Contributors
----------------

Developers and contributors of Penman can clone the source code and use `Hatch`_ to interact with the project::

  $ git clone https://github.com/goodmami/penman.git
  $ cd penman/
  $ hatch version
  1.2.3

The ``dev`` environment contains scripts for linting, type-checking,
and testing the code::

  $ hatch run dev:lint
  $ hatch run dev:typecheck
  $ hatch run dev:test

The ``docs`` environment contains scripts for building the
documentation and for cleaning the build files::

  $ hatch run docs:build
  $ hatch run docs:clean


.. _PyPI: https://pypi.org/project/Penman/
.. _GitHub: https://github.com/goodmami/penman/
.. _Python 3.8: https://www.python.org/
.. _Hatch: https://hatch.pypa.io/
