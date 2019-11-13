
.. highlight:: console

Installation and Setup
======================

Penman releases are available on `PyPI`_ and the source code is on
`GitHub`_. Users of Penman will probably want to install from `PyPI`_
using :command:`pip` as it is the easiest method and it makes the
:command:`penman` command available at the command line. Developers
and contributors of Penman will probably want to install from the
source code.


Requirements
------------

The Penman package runs with `Python 3.6`_ and higher versions, but
otherwise it has no dependencies beyond Python's standard library.

Some development tasks, such as unit testing, building the
documentation, or making releases, have additional dependencies. See
`Installing from Source`_ for more information.


Installation
------------

Installing from PyPI
''''''''''''''''''''

Install the latest version from `PyPI`_ using :command:`pip` (using a
`virtual environment`_ is recommended)::

  $ pip install penman

After running the above command, the ``penman`` module will be
available in Python and the :command:`penman` command will be
available at the command line.


Installing from Source
''''''''''''''''''''''

Developers and contributors of the Penman project may wish to install
from the source code using one of several "extras", which are given in
brackets after the package name. The available extras are:

- ``test`` -- install dependencies for unit testing
- ``doc`` -- install dependencies for building the documentation
- ``dev`` -- install dependencies for both of the above plus those
  needed for publishing releases

When installing from source code, the ``-e`` option is also useful as
any changes made to the source code after the install will be
reflected at runtime (otherwise one needs to reinstall after any
changes). The following is how one might clone the source code, create
and activate a virtual environment, and install for development::

  $ git clone https://github.com/goodmami/penman.git
  [...]
  $ cd penman/
  $ python3 -m venv env
  $ source env/bin/activate
  (env) $ pip install -e .[dev]


Testing
-------

Unit Testing with pytest
''''''''''''''''''''''''

The unit tests can be run with `pytest`_ from the project directory of
the source code::

  (env) $ pytest

For testing multiple Python versions, a tool like `tox`_ can automate
the creation and activation of multiple virtual environments.


Type-checking with Mypy
'''''''''''''''''''''''

The Penman project heavily uses :pep:`484` and :pep:`526` type
annotations for static type checking. The code can be type-checked
using `Mypy`_::

  (env) $ mypy penman


Style-checking with Flake8
''''''''''''''''''''''''''

`Flake8`_ is used for style checking with the following checks disabled:

* `E241`_ -- large data descriptions are easier to read with whitespace
* `W503`_ -- binary operators should appear after a line break

::

  (env) $ flake8 --ignore=E241,W503 penman


.. _PyPI: https://pypi.org/project/Penman/
.. _GitHub: https://github.com/goodmami/penman/
.. _Python 3.6: https://www.python.org/
.. _virtual environment: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
.. _pytest: http://pytest.org/
.. _tox: https://tox.readthedocs.io/en/latest/
.. _Mypy: http://mypy-lang.org/
.. _Flake8: http://flake8.pycqa.org/
.. _E241: https://lintlyci.github.io/Flake8Rules/rules/E241.html
.. _W503: https://lintlyci.github.io/Flake8Rules/rules/W503.html
