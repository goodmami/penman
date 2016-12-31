
# API documentation for Penman

## Contents

* [decode()](#decode)
* [encode()](#encode)
* [load()](#load)
* [loads()](#loads)
* [dump()](#dump)
* [dumps()](#dumps)

* [Triple](#triple)

* [Graph](#graph)
* [Graph.top](#graph)
* [Graph.variables()](#graph-variables)
* [Graph.triples()](#graph-triples)
* [Graph.edges()](#graph-edges)
* [Graph.attributes()](#graph-attributes)

* [PENMANCodec](#penmancodec)
* [PENMANCodec.decode()](#penmancodec-decode)
* [PENMANCodec.iterdecode()](#penmancodec-iterdecode)
* [PENMANCodec.encode()](#penmancodec-encode)
* [PENMANCodec.is_relation_inverted()](#penmancodec-is_relation_inverted)
* [PENMANCodec.invert_relation()](#penmancodec-invert_relation)
* [PENMANCodec.handle_value()](#penmancodec-handle_value)
* [PENMANCodec.handle_triple()](#penmancodec-handle_triple)

## Functions

### decode

penman.**decode**(*s, cls=PENMANCodec, \*\*kwargs*)

Deserialize PENMAN-serialized *s* into its Graph object

##### Arguments

* `s` - a string containing a single PENMAN-serialized graph
* `cls` - serialization codec class
* `kwargs` - keyword arguments passed to the constructor of *cls*

##### Returns

the Graph object described by *s*

##### Example

```python
>>> decode('(b / bark :ARG1 (d / dog))')
<Graph object (top=b) at ...>
```


### encode

penman.**encode**(*g, top=None, cls=PENMANCodec, \*\*kwargs*)

Serialize the graph *g* from *top* to PENMAN notation.

##### Arguments

* `g` - the Graph object
* `top` - the node identifier for the top of the serialized graph; if
          unset, the original top of *g* is used
* `cls` - serialization codec class
* `kwargs` - keyword arguments passed to the constructor of *cls*

##### Returns

the PENMAN-serialized string of the Graph *g*

#### Example

```python
>>> PENMANCodec.encode(Graph([('h', 'instance', 'hi')]))
(h / hi)
```


### load

penman.**load**(*source, triples=False, cls=PENMANCodec, \*\*kwargs*)

Deserialize a list of PENMAN-encoded graphs from *source*.

##### Arguments

* `source` - a filename or file-like object to read from
* `triples` - if True, read graphs as triples instead of as PENMAN
* `cls` - serialization codec class
* `kwargs` - keyword arguments passed to the constructor of *cls*

##### Returns

a list of Graph objects


### loads

penman.**loads**(*string, triples=False, cls=PENMANCodec, \*\*kwargs*)

Deserialize a list of PENMAN-encoded graphs from *string*.

##### Arguments

* `string` - a string containing graph data
* `triples` - if True, read graphs as triples instead of as PENMAN
* `cls` - serialization codec class
* `kwargs` - keyword arguments passed to the constructor of *cls*

##### Returns

a list of Graph objects


### dump

penman.**dump**(*graphs, file, triples=False, cls=PENMANCodec, \*\*kwargs*)

Serialize each graph in *graphs* to PENMAN and write to *file*.

##### Arguments

* `graphs` - an iterable of Graph objects
* `file` - a filename or file-like object to write to
* `triples` - if True, write graphs as triples instead of as PENMAN
* `cls` - serialization codec class
* `kwargs` - keyword arguments passed to the constructor of *cls*


### dumps

penman.**dumps**(*graphs, triples=False, cls=PENMANCodec, \*\*kwargs*)

Serialize each graph in *graphs* to the PENMAN format.

##### Arguments

* `graphs` - an iterable of Graph objects
* `triples` - if True, write graphs as triples instead of as PENMAN

##### Returns

the string of serialized graphs



##  Classes


### Triple

Container for Graph edges and node attributes.

penman.**Triple**(*source, relation, target*)


### Graph

A basic class for modeling a rooted, directed acyclic graph.

A Graph is defined by a list of triples, which can be divided into
two parts: a list of graph edges where both the source and target
are node identifiers, and a list of node attributes where only the
source is a node identifier and the target is a constant. These
lists can be obtained via the Graph.triples(), Graph.edges(), and
Graph.attributes() methods.

penman.**Graph**(*data=None, top=None, codec=PENMANCodec*)

Create a Graph from an iterable of triples.

##### Arguments

* `data` - an iterable of triples (Triple objects or 3-tuples)
* `top` - the node identifier of the top node; if unspecified,
          the source of the first triple is used
* `codec` - the serialization codec used to interpret values

##### Example

```python
>>> Graph([
...     ('b', 'instance', 'bark'),
...     ('d', 'instance', 'dog'),
...     ('b', 'ARG1', 'd')
... ])
```

#### Graph.top

penman.Graph.**top**

The top variable.

#### Graph.variables

penman.Graph.**variables**()

Return the list of variables (nonterminal node identifiers).

#### Graph.triples

penman.Graph.**triples**(*source=None, relation=None, target=None*)

Return triples filtered by their *source*, *relation*, or *target*.

#### Graph.edges

penman.Graph.**edges**(*source=None, relation=None, target=None*)

Return edges filtered by their *source*, *relation*, or *target*.

Edges don't include terminal triples (node types or attributes).

#### Graph.attributes

penman.Graph.**attributes**(*source=None, relation=None, target=None*)

Return attributes filtered by their *source*, *relation*, or *target*.

Attributes don't include triples where the target is a nonterminal.


### PENMANCodec

A parameterized encoder/decoder for graphs in PENMAN notation.

penman.**PENMANCodec**(*indent=True*)

Initialize a new codec.

##### Arguments

* `indent` - if True, adaptively indent; if False or None, don't
             indent; if a non-negative integer, indent that many
             spaces per nesting level

#### PENMANCodec.decode

penman.PENMANCodec.**decode**(*s, triples=False*)

Deserialize PENMAN-notation string *s* into its Graph object.

##### Arguments

* `s` - a string containing a single PENMAN-serialized graph
* `triples` - if True, treat *s* as a conjunction of logical triples

##### Returns

the Graph object described by *s*

##### Example

```python
>>> PENMANCodec.decode('(b / bark :ARG1 (d / dog))')
<Graph object (top=b) at ...>
>>> PENMANCodec.decode(
...     'instance(b, bark) ^ instance(d, dog) ^ ARG1(b, d)'
... )
<Graph object (top=b) at ...>
```

#### PENMANCodec.iterdecode

penman.PENMANCodec.**iterdecode**(*s, triples=False*)

Deserialize PENMAN-notation string *s* into its Graph objects.

##### Arguments

* `s` - a string containing zero or more PENMAN-serialized graphs
* `triples` - if True, treat *s* as a conjunction of logical triples

##### Yields

valid Graph objects described by *s*

##### Example

```python
>>> list(PENMANCodec.iterdecode('(h / hello)(g / goodbye)'))
[<Graph object (top=h) at ...>, <Graph object (top=g) at ...>]
>>> list(PENMANCodec.iterdecode(
...     'instance(h, hello)\n'
...     'instance(g, goodbye)'
... ))
[<Graph object (top=h) at ...>, <Graph object (top=g) at ...>]
```

#### PENMANCodec.encode

penman.PENMANCodec.**encode**(*g, top=None, triples=False*)

Serialize the graph *g* from *top* to PENMAN notation.

##### Args

* `g` - the Graph object
* `top` - the node identifier for the top of the serialized
          graph; if unset, the original top of *g* is used
* `triples` - if True, serialize as a conjunction of logical triples

##### Returns

the PENMAN-serialized string of the Graph *g*

##### Example

```python
>>> PENMANCodec.encode(Graph([('h', 'instance', 'hi')]))
(h / hi)
>>> PENMANCodec.encode(Graph([('h', 'instance', 'hi')]),
...                    triples=True)
instance(h, hi)
```

#### PENMANCodec.is_relation_inverted

penman.PENMANCodec.**is_relation_inverted**(*relation*)

Return True if *relation* is inverted.

#### PENMANCodec.invert_relation

penman.PENMANCodec.**invert_relation**(*relation*)

Invert or deinvert *relation*.

#### PENMANCodec.handle_value

penman.PENMANCodec.**handle_value**(*s*)

Process relation value *s* before it is used in a triple.

##### Arguments

* `s` - the string value of a non-nodetype relation

##### Returns

the value, converted to float or int if applicable,
otherwise the unchanged string

#### PENMANCodec.handle_triple

penman.PENMANCodec.**handle_triple**(*lhs, relation, rhs*)

Process triples before they are added to the graph.

Note that *lhs* and *rhs* are as they originally appeared, and
may be inverted. By default, this function normalizes all such
inversions, and also removes initial colons in relations and
sets empty relations to None.

##### Arguments

* `lhs` - the left hand side of an observed triple
* `relation` - the triple relation (possibly inverted)
* `rhs` - the right hand side of an observed triple

##### Returns

The processed (source, relation, target) triple. By default,
it is returned as a Triple object.

