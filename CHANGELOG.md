# Change Log

## [Unreleased][unreleased]

### Added
### Removed
### Fixed
### Changed
### Deprecated

## [v0.6.2][v0.6.2]

### Fixed

* Value-cast patterns terminated with `$` to invalid casts (#9)
* Raise EncodeError when attempting to encode empty graphs (#14)
* Redefine NODETYPE_RE for AMRCodec (#17)
* Remove specific float and int parsing in variables/nodetypes for the
  default parser (the numeric values are still parses as atoms) (#17)

## [v0.6.1][v0.6.1]

### Added

* Some additional regular expressions on `PENMANCodec` to influence
  parsing behavior
* `CONTRIBUTING.md`

### Fixed

* Allow numeric and string variables and node types

### Changed

* Grammar in README now more accurately reflect parsing behavior (and
  vice versa)

## [v0.6.0][]

### Fixed

* By default, always preserve relation order when given (fixes #6)
* `__version_info__` now gives integers for numeric parts

### Added

* `PenmanError` as a exception base class
* `EncodeError` for errors during encoding; derived from `PenmanError`
* Functions for ordering relations (these behave like `sorted()`, in
  that they take and return a list). Note that the type relation (given
  by `codec.TYPE_REL`), if present, always appears first, regardless of
  the sorting method.
  - `original_order` - the default; return the list as-is
  - `out_first_order` - sort all true orientations before inverted
    orientations; otherwise order is retained
  - `alphanum_order` - former default; sort relations alphabetically
    with embedded integers sorted numerically (like `sort -V`)
* Added disclaimer to `README.md` saying that this module is not
  affiliated with ISI, the PENMAN project, or the AMR project
* `Triple` objects can now have an `inverted` attribute that can be
  given as a fourth instantiation parameter. The object is still treated
  as a 3-tuple, so `src, rel, tgt = triple` still works (and `triple[3]`
  will not get the inversion status; use `triple.inverted`). Valid
  values are `False` (true orientation), `True` (inverted orientation),
  and `None` (no orientation specified).
* `--indent` option for commandline usage
* `AMRCodec` with a more restrictive grammar and special inversions

### Changed

* `DecodeError` now derives from `PenmanError`
* `PENMANCodec` now takes a `relation_sort` parameter whose value is a
  function that sorts `Triple` objects (see **Added** above)
* Updated the PEG definition in `README.md`, and accompanying prose.


## [v0.5.1][]

### Fixed

* Numeric conversion in `PENMANCodec.handle_triple()` now happens to
  both sources and targets, and `handle_triple()` is now run on the top,
  as well. Fixes #4
* `Graph.__str__()` now initializes a default codec for serialization.
* Incorrect script usage fixed in README.md and from `penman.py --help`
* Updated documentation


## [v0.5.0][]

### Fixed

* Properly trim off ^ in triple-conjunction parsing.

### Added

* `TOP_VAR` and `TOP_REL` are added to `PENMANCodec` (these were
  module-level variables prior to v0.4.0); they are only used for
  triple-conjunctions. If left as `None`, they will not be printed or
  interpreted.
* `PENMANCodec.triples_to_graph` to instantiate a Graph with awareness
  of codec configuration (e.g. `TOP_VAR`, `TYPE_REL`, etc.)

### Removed

* `PENMANCodec.handle_value()` - value conversion is now done in
  `PENMANCodec.handle_triple()`, which has access to relation name, etc.

### Changed

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
[v0.5.1]: ../../releases/tag/v0.5.1
[v0.6.0]: ../../releases/tag/v0.6.0
[v0.6.1]: ../../releases/tag/v0.6.1
[v0.6.2]: ../../releases/tag/v0.6.2
[README]: README.md
