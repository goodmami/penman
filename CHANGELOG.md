# Change Log

## [Unreleased][unreleased]

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
[README]: README.md
