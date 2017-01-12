# Change Log

## [Unreleased][unreleased]

## [v0.5.0][]

## Fixed

* Properly trim off ^ in triple-conjunction parsing.

## Added

* `TOP_VAR` and `TOP_REL` are added to `PENMANCodec` (these were
  module-level variables prior to v0.4.0); they are only used for
  triple-conjunctions. If left as `None`, they will not be printed or
  interpreted.
* `PENMANCodec.triples_to_graph` to instantiate a Graph with awareness
  of codec configuration (e.g. `TOP_VAR`, `TYPE_REL`, etc.)

## Removed

* `PENMANCodec.handle_value()` - value conversion is now done in
  `PENMANCodec.handle_triple()`, which has access to relation name, etc.

## Changed

* Decoupled `Graph` from the codec by removing the `codec` parameter and
  its usage in the class methods. Graphs can be instantiated with
  awareness of the codec via the codec's `triples_to_graph()`  method.
* `PENMANCodec` returns all node type triples before other edge triples.
* `PENMANCodec` reads/writes TOP nodes in triple conjunctions if
  `TOP_VAR` and `TOP_REL` are set (see above).
* Default node types are no longer stored as triples. This means a graph
  like `(a / a :ARG b)` cannot say if `b` is a node or just a symbol.
  Let's see how far this gets us before re-adding such support.
* `PENMANCodec.handle_triple()` now manages value conversion
* PENMAN serialization now sorts relations like `sort -V`


## [v0.4.0][]

This release is a major rewrite of the serialization mechanism. Now a
serialization codec manages the interface between graphs and PENMAN or
triple conjunctions, and it can be instantiated with parameters or
subclassed to customize behavior.

### Added

* `PENMANCodec` class for managing serialization to/from PENMAN and
   triple conjunctions
* `Graph.attributes()` returns terminal relations

### Removed

* Module-level `TOP` and `TOP_RELATION` are no longer used for
  customizing serialization behavior (see `PENMANCodec`)
* `Graph.concepts()`
* `Graph.constants()`
* `Triple.is_inverted()` (use `PENMANCodec.is_relation_inverted()`)

### Changed

* `Graph.to_triples()` is now `Graph.triples()` and no longer has a
  `normalize` parameter, but can now be filtered by `source`,
  `relation`, and `target`, as with `Graph.edges()` and
  `Graph.attributes()`
* `Graph.edges()` only returns triples between nonterminal nodes
* Default relation for node types is `instance`, since `instance-of`
  seems to not be used, documented, or intuitive.
* `load()`, `loads()`, `dump()`, and `dumps()` now take a `cls`
  parameter for a serialization codec, and any additional `**kwargs`
  are passed to its constructor.

## [v0.3.0][]

### Added

* `TOP` and `TOP_RELATION` as module-level variables
* `is_relation_inverted()`
* `invert_relation()`
* `Graph.top`
* `Graph.variables()`
* `Graph.concepts()`
* `Graph.constants()`
* `Graph.edges()`

### Changed

* `Graph.from_triples()` can take an explicit `top=...` parameter
* The `indent` parameter to `Graph.to_penman()` now takes a range of values:
  - `indent=True` is the default with adaptive indentation
  - `indent=False` and `indent=None` do not insert newlines and use a
    single space to delimit fields
  - `indent=N`, where `N` is an integer, indents N spaces after a newline
* `load()`, `loads()`, `dump()`, and `dumps()` can now take a `triples=...`
  parameter (default: False); if True, read/write as triples

## [v0.2.0][]

### Changed

* PENMAN serialization uses slightly more sophisticated default weights
  for choosing when to invert edges, which prevents some ugly graphs.
* `Graph.to_triples()` takes a `normalize=True` parameter (default `False`)
  to uninvert inverted edges.
* Running the script with `--triples` now prints the logical conjunction
  of triples (e.g. `instance-of(b, bark-01) ^ ARG0(b, d) ^
  instance-of(d, dog)`).

## [v0.1.0][]

First release with very basic functionality.

### Added

* `Triple` namedtuple for edge information (source, relation, target)
* `Graph` stores graph data and provides methods for access
* `load()`/`loads()` reads Penman files/strings
* `dump()`/`dumps()` writes Penman files/strings

[unreleased]: ../../tree/develop
[v0.1.0]: ../../releases/tag/v0.1.0
[v0.2.0]: ../../releases/tag/v0.2.0
[v0.3.0]: ../../releases/tag/v0.3.0
[v0.4.0]: ../../releases/tag/v0.4.0
[v0.5.0]: ../../releases/tag/v0.5.0
[README]: README.md
