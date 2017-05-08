
# API documentation for Penman

**Contents**

Module functions:

* [decode()](#decode)
* [encode()](#encode)
* [load()](#load)
* [loads()](#loads)
* [dump()](#dump)
* [dumps()](#dumps)
* [original_order()](#original_order)
* [out_first_order()](#out_first_order)
* [alphanum_order()](#alphanum_order)

Classes and methods:

* [Triple](#Triple)
  - [Triple.source](#Triple-source)
  - [Triple.relation](#Triple-relation)
  - [Triple.target](#Triple-target)
  - [Triple.inverted](#Triple-inverted)
* [Graph](#Graph)
  - [Graph.top](#Graph-top)
  - [Graph.variables()](#Graph-variables)
  - [Graph.triples()](#Graph-triples)
  - [Graph.edges()](#Graph-edges)
  - [Graph.attributes()](#Graph-attributes)
  - [Graph.reentrancies()](#Graph-reentrancies)
* [PENMANCodec](#PENMANCodec)
  - [PENMANCodec.decode()](#PENMANCodec-decode)
  - [PENMANCodec.iterdecode()](#PENMANCodec-iterdecode)
  - [PENMANCodec.encode()](#PENMANCodec-encode)
  - [PENMANCodec.is_relation_inverted()](#PENMANCodec-is_relation_inverted)
  - [PENMANCodec.invert_relation()](#PENMANCodec-invert_relation)
  - [PENMANCodec.handle_triple()](#PENMANCodec-handle_triple)
  - [PENMANCodec.triples_to_graph()](#PENMANCodec-triples_to_graph)
* [AMRCodec](#AMRCodec)

# Serialization Functions

## decode

<a name="decode" href="#decode">▣</a>
penman.**decode**(_s, cls=PENMANCodec, \*\*kwargs_)

Deserialize PENMAN-serialized *s* into its Graph object

Arguments:

* `s` - a string containing a single PENMAN-serialized graph
* `cls` - serialization codec class
* `kwargs` - keyword arguments passed to the constructor of *cls*

Returns:

* the Graph object described by *s*

Example:

```python
>>> decode('(b / bark :ARG1 (d / dog))')
<Graph object (top=b) at ...>
```


## encode

<a name="encode" href="#encode">▣</a>
penman.**encode**(_g, top=None, cls=PENMANCodec, \*\*kwargs_)

Serialize the graph *g* from *top* to PENMAN notation.

Arguments:

* `g` - the Graph object
* `top` - the node identifier for the top of the serialized graph; if
          unset, the original top of *g* is used
* `cls` - serialization codec class
* `kwargs` - keyword arguments passed to the constructor of *cls*

Returns:

* the PENMAN-serialized string of the Graph *g*

Example:

```python
>>> encode(Graph([('h', 'instance', 'hi')]))
(h / hi)
```


## load

<a name="load" href="#load">▣</a>
penman.**load**(_source, triples=False, cls=PENMANCodec, \*\*kwargs_)

Deserialize a list of PENMAN-encoded graphs from *source*.

Arguments:

* `source` - a filename or file-like object to read from
* `triples` - if True, read graphs as triples instead of as PENMAN
* `cls` - serialization codec class
* `kwargs` - keyword arguments passed to the constructor of *cls*

Returns:

* a list of Graph objects


## loads

<a name="loads" href="#loads">▣</a>
penman.**loads**(_string, triples=False, cls=PENMANCodec, \*\*kwargs_)

Deserialize a list of PENMAN-encoded graphs from *string*.

Arguments:

* `string` - a string containing graph data
* `triples` - if True, read graphs as triples instead of as PENMAN
* `cls` - serialization codec class
* `kwargs` - keyword arguments passed to the constructor of *cls*

Returns:

* a list of Graph objects


## dump

<a name="dump" href="#dump">▣</a>
penman.**dump**(_graphs, file, triples=False, cls=PENMANCodec, \*\*kwargs_)

Serialize each graph in *graphs* to PENMAN and write to *file*.

Arguments:

* `graphs` - an iterable of Graph objects
* `file` - a filename or file-like object to write to
* `triples` - if True, write graphs as triples instead of as PENMAN
* `cls` - serialization codec class
* `kwargs` - keyword arguments passed to the constructor of *cls*


## dumps

<a name="dumps" href="#dumps">▣</a>
penman.**dumps**(_graphs, triples=False, cls=PENMANCodec, \*\*kwargs_)

Serialize each graph in *graphs* to the PENMAN format.

Arguments:

* `graphs` - an iterable of Graph objects
* `triples` - if True, write graphs as triples instead of as PENMAN

Returns:

* the string of serialized graphs


# Helper Functions

The [original_order()](#original_order),
[out_first_order()](#out_first_order), and
[alphanum_order()](#alphanum_order) functions are used during
serialization to sort the relations on a node. By default, the observed
order during decoding or graph construction is used, but if a particular
order is to be used an appropriate function may be passed as the
`relation_sort` parameter to a `PENMANCodec` instantiation.

## original_order
<a name="original_order" href="#original_order">▣</a>
penman.**original_order**(_triples_)

Return a list of *triples* in the original order.


## out_first_order
<a name="out_first_order" href="#out_first_order">▣</a>
penman.**out_first_order**(_triples_)

Sort a list of *triples* so outward (true) edges appear first.


## alphanum_order
<a name="alphanum_order" href="#alphanum_order">▣</a>
penman.**alphanum_order**(_triples_)

Sort a list of *triples* by relation name.

Embedded integers are sorted numerically, but otherwise the sorting
is alphabetic.


#  Classes


## Triple

Container for Graph edges and node attributes.

<a name="Triple" href="#Triple">▣</a>
penman.**Triple**(_source, relation, target, inverted=None_)

The final parameter, `inverted`, is optional, and when set it exists as
an attribute of the Triple object, but not as part of the 3-tuple data.
It is used to store the intended or original orientation of the triple
(i.e. whether it was true or inverted). If unset, preference during
serialization is for a true orientation.

Properties:

* <a name="Triple-source" href="#Triple-source">▣</a>
  penman.Triple.**source**

  The source node of the triple. Only get-access is supported. It can
  also be accessed by index: `triple[0]`.

* <a name="Triple-relation" href="#Triple-relation">▣</a>
  penman.Triple.**relation**

  The relation name of the triple. Only get-access is supported. It can
  also be accessed by index: `triple[1]`.

* <a name="Triple-target" href="#Triple-target">▣</a>
  penman.Triple.**target**

  The target node of the triple. Only get-access is supported. It can
  also be accessed by index: `triple[2]`.

* <a name="Triple-inverted" href="#Triple-inverted">▣</a>
  penman.Triple.**inverted**

  The intended or observed orientation of the triple. If `True`, the
  triple was or should be inverted (e.g., `(a :rel b)` was or should be
  serialized as `(b :rel-of a)`). Both get and set of this property are
  supported, and valid values are `True`, `False`, and `None`. This
  property cannot be accessed by an index.


## Graph

A basic class for modeling a rooted, directed acyclic graph.

A Graph is defined by a list of triples, which can be divided into
two parts: a list of graph edges where both the source and target
are node identifiers, and a list of node attributes where only the
source is a node identifier and the target is a constant. These
lists can be obtained via the Graph.triples(), Graph.edges(), and
Graph.attributes() methods.

<a name="Graph" href="#Graph">▣</a>
penman.**Graph**(_data=None, top=None, codec=PENMANCodec_)

Create a Graph from an iterable of triples.

Arguments:

* `data` - an iterable of triples (Triple objects or 3-tuples)
* `top` - the node identifier of the top node; if unspecified,
          the source of the first triple is used
* `codec` - the serialization codec used to interpret values

Example:

```python
>>> Graph([
...     ('b', 'instance', 'bark'),
...     ('d', 'instance', 'dog'),
...     ('b', 'ARG1', 'd')
... ])
```

Properties:

* <a name="Graph-top" href="#Graph-top">▣</a>
  penman.Graph.**top**

  The top variable.

  Both get and set actions are supported. During set (e.g.
  `g.top = 'a'`), the value is checked to ensure it is a valid node in
  the graph.

Methods:

* <a name="Graph-variables" href="#Graph-variables">▣</a>
  penman.Graph.**variables**()

  Return the list of variables (nonterminal node identifiers).

* <a name="Graph-triples" href="#Graph-triples">▣</a>
  penman.Graph.**triples**(_source=None, relation=None, target=None_)
  
  Return triples filtered by their *source*, *relation*, or *target*.

* <a name="Graph-edges" href="#Graph-edges">▣</a>
  penman.Graph.**edges**(_source=None, relation=None, target=None_)
  
  Return edges filtered by their *source*, *relation*, or *target*.
  
  Edges don't include terminal triples (node types or attributes).

* <a name="Graph-attributes" href="#Graph-attributes">▣</a>
  penman.Graph.**attributes**(_source=None, relation=None, target=None_)
  
  Return attributes filtered by their *source*, *relation*, or *target*.
  
  Attributes don't include triples where the target is a nonterminal.

* <a name="Graph-reentrancies" href="#Graph-reentrancies">▣</a>
  penman.Graph.**reentrancies**()
  
  Return a mapping of variables to their re-entrancy count.

  A re-entrancy is when more than one edge selects a node as its target.
  These graphs are rooted, so the top node always has an implicit
  entrancy. Only nodes with re-entrancies are reported, and the count is
  only for the entrant edges beyond the first. Also note that these
  counts are for the interpreted graph, not for the linearized form, so
  inverted edges are always re-entrant.


## PENMANCodec

A parameterized encoder/decoder for graphs in PENMAN notation.

<a name="PENMANCodec" href="#PENMANCodec">▣</a>
penman.**PENMANCodec**(_indent=True, relation_sort=original_order_)

Initialize a new codec.

Arguments:

* `indent` - if True, adaptively indent; if False or None, don't
             indent; if a non-negative integer, indent that many
             spaces per nesting level
* `relation_sort` - the function used to sort relations on a node

Methods:

* <a name="PENMANCodec-decode" href="#PENMANCodec-decode">▣</a>
  penman.PENMANCodec.**decode**(_s, triples=False_)
  
  Deserialize PENMAN-notation string *s* into its Graph object.
  
  Arguments:
  
  * `s` - a string containing a single PENMAN-serialized graph
  * `triples` - if True, treat *s* as a conjunction of logical triples
  
  Returns:
  
  * the Graph object described by *s*
  
  Example:
  
  ```python
  >>> codec = PENMANCodec()
  >>> codec.decode('(b / bark :ARG1 (d / dog))')
  <Graph object (top=b) at ...>
  >>> codec.decode(
  ...     'instance(b, bark) ^ instance(d, dog) ^ ARG1(b, d)'
  ... )
  <Graph object (top=b) at ...>
  ```

* <a name="PENMANCodec-iterdecode" href="#PENMANCodec-iterdecode">▣</a>
  penman.PENMANCodec.**iterdecode**(_s, triples=False_)
  
  Deserialize PENMAN-notation string *s* into its Graph objects.
  
  Arguments:
  
  * `s` - a string containing zero or more PENMAN-serialized graphs
  * `triples` - if True, treat *s* as a conjunction of logical triples
  
  Yields:
  
  * valid Graph objects described by *s*
  
  Example:
  
  ```python
  >>> codec = PENMANCodec()
  >>> list(codec.iterdecode('(h / hello)(g / goodbye)'))
  [<Graph object (top=h) at ...>, <Graph object (top=g) at ...>]
  >>> list(codec.iterdecode(
  ...     'instance(h, hello)\n'
  ...     'instance(g, goodbye)'
  ... ))
  [<Graph object (top=h) at ...>, <Graph object (top=g) at ...>]
  ```

* <a name="PENMANCodec-encode" href="#PENMANCodec-encode">▣</a>
  penman.PENMANCodec.**encode**(_g, top=None, triples=False_)
  
  Serialize the graph *g* from *top* to PENMAN notation.
  
  Arguments:
  
  * `g` - the Graph object
  * `top` - the node identifier for the top of the serialized
            graph; if unset, the original top of *g* is used
  * `triples` - if True, serialize as a conjunction of logical triples
  
  Returns:
  
  * the PENMAN-serialized string of the Graph *g*
  
  Example:
  
  ```python
  >>> codec = PENMANCodec()
  >>> codec.encode(Graph([('h', 'instance', 'hi')]))
  (h / hi)
  >>> codec.encode(Graph([('h', 'instance', 'hi')]),
  ...                    triples=True)
  instance(h, hi)
  ```

* <a name="PENMANCodec-is_relation_inverted" href="#PENMANCodec-is_relation_inverted">▣</a>
  penman.PENMANCodec.**is_relation_inverted**(_relation_)

  Return True if *relation* is inverted.

* <a name="PENMANCodec-invert_relation" href="#PENMANCodec-invert_relation">▣</a>
  penman.PENMANCodec.**invert_relation**(_relation_)

  Invert or deinvert *relation*.

* <a name="PENMANCodec-handle_triple" href="#PENMANCodec-handle_triple">▣</a>
  penman.PENMANCodec.**handle_triple**(_lhs, relation, rhs_)

  Process triples before they are added to the graph.

  Note that *lhs* and *rhs* are as they originally appeared, and
  may be inverted. Inversions are detected by
  is_relation_inverted() and de-inverted by invert_relation().

  By default, this function:
   * removes initial colons on relations
   * de-inverts all inverted relations
   * sets empty relations to `None`
   * casts numeric string sources and targets to their numeric
     types (e.g. float, int)

  Arguments:
  
  * `lhs` - the left hand side of an observed triple
  * `relation` - the triple relation (possibly inverted)
  * `rhs` - the right hand side of an observed triple
  
  Returns:
  
  * The processed (source, relation, target) triple. By default,
    it is returned as a Triple object.

* <a name="PENMANCodec-triples_to_graph" href="#PENMANCodec-triples_to_graph">▣</a>
  penman.PENMANCodec.**triples_to_graph**(_triples, top=None_)

  Create a Graph from *triples* considering codec configuration.

  The Graph class does not know about information in the codec,
  so if Graph instantiation depends on special `TYPE_REL` or
  `TOP_VAR` values, use this function instead of instantiating
  a Graph object directly. This is also where edge
  normalization (de-inversion) and value type conversion occur
  (via handle_triple()).

  Arguments:
 
  * `triples` - an iterable of (lhs, relation, rhs) triples
  * `top` - node identifier of the top node

  Returns:

  * a Graph object
  
## AMRCodec

An AMR-specific subclass of [PENMANCodec](#PENMANCodec).

This subclass redefines some patterns used for decoding so that only
AMR-style graphs are allowed. It also redefines how certain relations
get inverted (e.g. that the inverse of `:domain` is `:mod`, and
vice-versa).

<a name="AMRCodec" href="#AMRCodec">▣</a>
penman.**AMRCodec**(_indent=True, relation_sort=original_order_)

Instantiation options and methods are the same.

Example:

```python
>>> import penman
>>> amr = penman.AMRCodec()
>>> print(amr.encode(
...     penman.Graph([('s', 'instance', 'small'), ('s', 'domain', 'm'),
...                   ('m', 'instance', 'marble')])))
(s / small
   :domain (m / marble))
>>> print(amr.encode(
...     penman.Graph([('s', 'instance', 'small'), ('s', 'domain', 'm'),
...                   ('m', 'instance', 'marble')]),
...     top='m'))
(m / marble
   :mod (s / small))

```
