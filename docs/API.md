
# API documentation for Penman

**Contents**

Module functions:

* [decode()](#decode)
* [encode()](#encode)
* [load()](#load)
* [loads()](#loads)
* [dump()](#dump)
* [dumps()](#dumps)

Classes and methods:

* [Triple](#Triple)
* [Graph](#Graph)
  - [Graph.top](#Graph-top)
  - [Graph.variables()](#Graph-variables)
  - [Graph.triples()](#Graph-triples)
  - [Graph.edges()](#Graph-edges)
  - [Graph.attributes()](#Graph-attributes)
* [PENMANCodec](#PENMANCodec)
  - [PENMANCodec.decode()](#PENMANCodec-decode)
  - [PENMANCodec.iterdecode()](#PENMANCodec-iterdecode)
  - [PENMANCodec.encode()](#PENMANCodec-encode)
  - [PENMANCodec.is_relation_inverted()](#PENMANCodec-is_relation_inverted)
  - [PENMANCodec.invert_relation()](#PENMANCodec-invert_relation)
  - [PENMANCodec.handle_triple()](#PENMANCodec-handle_triple)
  - [PENMANCodec.triples_to_graph()](#PENMANCodec-triples_to_graph)

# Functions

## decode

<a name="decode" href="API.md#decode">▣</a>
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

<a name="encode" href="API.md#encode">▣</a>
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
>>> PENMANCodec.encode(Graph([('h', 'instance', 'hi')]))
(h / hi)
```


## load

<a name="load" href="API.md#load">▣</a>
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

<a name="loads" href="API.md#loads">▣</a>
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

<a name="dump" href="API.md#dump">▣</a>
penman.**dump**(_graphs, file, triples=False, cls=PENMANCodec, \*\*kwargs_)

Serialize each graph in *graphs* to PENMAN and write to *file*.

Arguments:

* `graphs` - an iterable of Graph objects
* `file` - a filename or file-like object to write to
* `triples` - if True, write graphs as triples instead of as PENMAN
* `cls` - serialization codec class
* `kwargs` - keyword arguments passed to the constructor of *cls*


## dumps

<a name="dumps" href="API.md#dumps">▣</a>
penman.**dumps**(_graphs, triples=False, cls=PENMANCodec, \*\*kwargs_)

Serialize each graph in *graphs* to the PENMAN format.

Arguments:

* `graphs` - an iterable of Graph objects
* `triples` - if True, write graphs as triples instead of as PENMAN

Returns:

* the string of serialized graphs



#  Classes


## Triple

Container for Graph edges and node attributes.

<a name="Triple" href="API.md#Triple">▣</a>
penman.**Triple**(_source, relation, target_)


## Graph

A basic class for modeling a rooted, directed acyclic graph.

A Graph is defined by a list of triples, which can be divided into
two parts: a list of graph edges where both the source and target
are node identifiers, and a list of node attributes where only the
source is a node identifier and the target is a constant. These
lists can be obtained via the Graph.triples(), Graph.edges(), and
Graph.attributes() methods.

<a name="Graph" href="API.md#Graph">▣</a>
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

* <a name="Graph-top" href="API.md#Graph-top">▣</a>
  penman.Graph.**top**

  The top variable.

Methods:

* <a name="Graph-variables" href="API.md#Graph-variables">▣</a>
  penman.Graph.**variables**()

  Return the list of variables (nonterminal node identifiers).

* <a name="Graph-triples" href="API.md#Graph-triples">▣</a>
  penman.Graph.**triples**(_source=None, relation=None, target=None_)
  
  Return triples filtered by their *source*, *relation*, or *target*.

* <a name="Graph-edges" href="API.md#Graph-edges">▣</a>
  penman.Graph.**edges**(_source=None, relation=None, target=None_)
  
  Return edges filtered by their *source*, *relation*, or *target*.
  
  Edges don't include terminal triples (node types or attributes).

* <a name="Graph-attributes" href="API.md#Graph-attributes">▣</a>
  penman.Graph.**attributes**(_source=None, relation=None, target=None_)
  
  Return attributes filtered by their *source*, *relation*, or *target*.
  
  Attributes don't include triples where the target is a nonterminal.


## PENMANCodec

A parameterized encoder/decoder for graphs in PENMAN notation.

<a name="PENMANCodec" href="API.md#PENMANCodec">▣</a>
penman.**PENMANCodec**(_indent=True_)

Initialize a new codec.

Arguments:

* `indent` - if True, adaptively indent; if False or None, don't
             indent; if a non-negative integer, indent that many
             spaces per nesting level

Methods:

* <a name="PENMANCodec-decode" href="API.md#PENMANCodec-decode">▣</a>
  penman.PENMANCodec.**decode**(_s, triples=False_)
  
  Deserialize PENMAN-notation string *s* into its Graph object.
  
  Arguments:
  
  * `s` - a string containing a single PENMAN-serialized graph
  * `triples` - if True, treat *s* as a conjunction of logical triples
  
  Returns:
  
  * the Graph object described by *s*
  
  Example:
  
  ```python
  >>> PENMANCodec.decode('(b / bark :ARG1 (d / dog))')
  <Graph object (top=b) at ...>
  >>> PENMANCodec.decode(
  ...     'instance(b, bark) ^ instance(d, dog) ^ ARG1(b, d)'
  ... )
  <Graph object (top=b) at ...>
  ```

* <a name="PENMANCodec-iterdecode" href="API.md#PENMANCodec-iterdecode">▣</a>
  penman.PENMANCodec.**iterdecode**(_s, triples=False_)
  
  Deserialize PENMAN-notation string *s* into its Graph objects.
  
  Arguments:
  
  * `s` - a string containing zero or more PENMAN-serialized graphs
  * `triples` - if True, treat *s* as a conjunction of logical triples
  
  Yields:
  
  * valid Graph objects described by *s*
  
  Example:
  
  ```python
  >>> list(PENMANCodec.iterdecode('(h / hello)(g / goodbye)'))
  [<Graph object (top=h) at ...>, <Graph object (top=g) at ...>]
  >>> list(PENMANCodec.iterdecode(
  ...     'instance(h, hello)\n'
  ...     'instance(g, goodbye)'
  ... ))
  [<Graph object (top=h) at ...>, <Graph object (top=g) at ...>]
  ```

* <a name="PENMANCodec-encode" href="API.md#PENMANCodec-encode">▣</a>
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
  >>> PENMANCodec.encode(Graph([('h', 'instance', 'hi')]))
  (h / hi)
  >>> PENMANCodec.encode(Graph([('h', 'instance', 'hi')]),
  ...                    triples=True)
  instance(h, hi)
  ```

* <a name="PENMANCodec-is_relation_inverted" href="API.md#PENMANCodec-is_relation_inverted">▣</a>
  penman.PENMANCodec.**is_relation_inverted**(_relation_)

  Return True if *relation* is inverted.

* <a name="PENMANCodec-invert_relation" href="API.md#PENMANCodec-invert_relation">▣</a>
  penman.PENMANCodec.**invert_relation**(_relation_)

  Invert or deinvert *relation*.

* <a name="PENMANCodec-handle_triple" href="API.md#PENMANCodec-handle_triple">▣</a>
  penman.PENMANCodec.**handle_triple**(_lhs, relation, rhs_)

  Process triples before they are added to the graph.

  Note that *lhs* and *rhs* are as they originally appeared, and
  may be inverted. Inversions are detected by
  is_relation_inverted() and de-inverted by invert_relation().

  By default, this function:
   * removes initial colons on relations
   * de-inverts all inverted relations
   * sets empty relations to `None`
   * casts numeric string targets (post-de-inversion) to their
     numeric types (e.g. float, int)

  Arguments:
  
  * `lhs` - the left hand side of an observed triple
  * `relation` - the triple relation (possibly inverted)
  * `rhs` - the right hand side of an observed triple
  
  Returns:
  
  * The processed (source, relation, target) triple. By default,
    it is returned as a Triple object.

* <a name="PENMANCodec-triples_to_graph" href="API.md#PENMANCodec-triples_to_graph">▣</a>
  penman.PENMANCodec.**triples_to_graph**(_triples, top=None_)

  Create a Graph from *triples* considering codec configuration.

  The Graph class does not know about information in the codec,
  so if Graph instantiation depends on special `TYPE_REL` or
  `TOP_VAR` values, use this function instead of instantiating
  a Graph object directly. This is also where edge
  normalization (de-inversion) and value type conversion occur.

  Arguments:
 
  * `triples` - an iterable of (lhs, relation, rhs) triples
  * `top` - node identifier of the top node

  Returns:

  * a Graph object
  
