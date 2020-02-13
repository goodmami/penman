
penman.constant
===============

.. automodule:: penman.constant

When a PENMAN string is parsed to a tree or a graph, constant values
are left as strings or, if the value is missing, as ``None``. Penman
nevertheless recognizes four datatypes commonly used in PENMAN data:
integers, floats, strings, and symbols. A fifth type, called a "null"
value, is used when an attribute is missing its target, but aside from
robustness measures it is not a supported datatype.


Enumerated Datatypes
--------------------

.. autodata:: SYMBOL
.. autodata:: STRING
.. autodata:: INTEGER
.. autodata:: FLOAT
.. autodata:: NULL


Module Functions
----------------

.. autofunction:: type
.. autofunction:: evaluate
.. autofunction:: quote
