# Change Log

## [Unreleased][unreleased]

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
[README]: README.md

