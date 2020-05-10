
Using Penman as a Python Library
================================

For some cases, the :command:`penman` command is not flexible enough
and it becomes necessary to write some Python code. Penman's Python
API is well-documented and well-tested and lets you dig into the
actual structures holding the data. One case where it's currently
necessary to write code is for arbitrary graph editing. For example,
perhaps you want to anonymize all attributes with numeric values. Here
is one way to do that with the API:

.. code-block:: python

   >>> import penman
   >>> from penman import constant
   >>> g = penman.decode('(b / buy-01 :ARG0 (i / i) :ARG1 (a / apple :quant 3))')
   >>> anon_map = {}
   >>> attributes = []
   >>> for src, role, tgt in g.attributes():
   ...     if constant.type(tgt) in (constant.INTEGER, constant.FLOAT):
   ...         anon_val = f'number_{len(anon_map)}'
   ...         anon_map[anon_val] = tgt
   ...         tgt = anon_val
   ...     attributes.append((src, role, tgt))
   ... 
   >>> g2 = penman.Graph(g.instances() + g.edges() + attributes)
   >>> print(penman.encode(g2))
   (b / buy-01
      :ARG0 (i / i)
      :ARG1 (a / apple
               :quant number_0))
   >>> anon_map
   {'number_0': '3'}

This could be improved, such as making the anonymization into a
function. It could also be made to work on the
:class:`~penman.tree.Tree` structure if you care about keeping the
original tree intact as this procedure loses the epigraphical markers
needed to reconstruct the tree from the graph.

The API is also useful for deeper inspection of graphs. For example:

.. code-block:: python

   >>> import penman
   >>> g = penman.decode('''
   ... # ::id ex1 ::snt The dog barked.
   ... (b / bark-01
   ...    :ARG0 (d / dog))
   ... ''')
   >>> g.top
   'b'
   >>> g.instances()
   [Instance(source='b', role=':instance', target='bark-01'), Instance(source='d', role=':instance', target='dog')]
   >>> g.edges()
   [Edge(source='b', role=':ARG0', target='d')]
   >>> sorted(g.variables())
   ['b', 'd']
   >>> g.metadata
   {'snt': 'The dog barked.', 'id': 'ex1'}
   >>> g.epidata
   {('b', ':instance', 'bark-01'): [], ('b', ':ARG0', 'd'): [Push(d)], ('d', ':instance', 'dog'): [POP]}
   >>> g.reentrancies()
   {}

Or for inserting surface alignments:

.. code-block:: python

   >>> from penman import surface
   >>> g.metadata['tok'] = 'The dog barked .'
   >>> g.epidata[('b', ':instance', 'bark-01')].append(surface.Alignment((2,), prefix='e.'))
   >>> g.epidata[('d', ':instance', 'dog')].append(surface.Alignment((1,), prefix='e.'))
   >>> print(penman.encode(g))
   # ::snt The dog barked.
   # ::id ex1
   # ::tok The dog barked .
   (b / bark-01~e.2
      :ARG0 (d / dog~e.1))

Many tasks can be accomplished with the basic API available at the
top-level :mod:`penman` module, but some more advanced usage requires
the use of specific submodules, such as the use of
:mod:`penman.constant` and :mod:`penman.surface` above. See the
:doc:`API documentation <api/penman>` for more information.
