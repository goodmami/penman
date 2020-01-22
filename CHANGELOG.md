# Change Log

## [Unreleased][unreleased]

### Added

* `penman.layout.reconfigure()` now has a `key` parameter ([#52][])
* `--reconfigure` command-line option ([#52][])

### Changed

* `penman.model.Model.original_order()` takes a `Role` instead of a
  `Branch` argument ([#53][])
* `penman.model.Model.canonical_order()` takes a `Role` instead of a
  `Branch` argument ([#53][])
* `penman.model.Model.random_order()` takes a `Role` instead of a
  `Branch` argument ([#53][])



## [v0.9.1][]

**Release date: 2020-01-16**

Partially revert some changes regarding the parsing of surface
alignments as they caused issues, particular when strings contain `~`
characters.

### Added

* `ALIGNMENT` production in `penman.lexer.PATTERNS` (this reverts a
  change in v0.9.0) ([#50][])

### Changed

* Disallow tildes in the `ROLE` and `SYMBOL` patterns (this reverts a
  change in v0.9.0) ([#50][])
* `ALIGNMENT` tokens are joined to their previous `ROLE`, `SYMBOL`, or
  `STRING`, which means they can now be separated with a space (for
  example, `(a / alpha ~1)`)


## [v0.9.0][]

**Release date: 2020-01-07**

Added support for node relabeling and dereification, and also
optimized parsing time by simplifying the work done during parsing.

### Added

* `penman.tree.Tree.reset_variables()` ([#41][])
* `--make-variables=FMT` command-line option ([#41][])
* `penman.surface.AlignmentMarker.from_string()` ([#45][])
* `penman.model.Model.is_role_reifiable()` (was `is_reifiable()`)
* `penman.model.Model.is_concept_dereifiable()` ([#40][])
* `penman.model.Model.dereify()` ([#40][])
* `penman.layout.get_pushed_variable()` ([#39][])
* `penman.layout.node_contexts()`
* `penman.transform.dereify_edges()` ([#40][])
* `--dereify-edges` command-line option ([#40][])
* `penman.graph.Graph.instances()` ([#48][])

### Removed

* `penman.lexer.Token.value` property ([#44][])
* `FLOAT` and `INTEGER` productions in `penman.lexer.PATTERNS` ([#44][])
* `penman.codec.PENMANCodec.ATOMS` ([#44][])
* `penman.codec.PENMANCodec.IDENTIFIERS` ([#44][])
* `COMMA` and `CARET` productions in `penman.lexer.PATTERNS` ([#43][])
* `triples` parameter for the following ([#42][]):
  - `penman.interface.decode()`
  - `penman.interface.loads()`
  - `penman.interface.load()`
  - `penman.interface.encode()`
  - `penman.interface.dumps()`
  - `penman.interface.dump()`
  - `penman.codec.encode()`
  - `penman.codec.decode()`
* `ALIGNMENT` production in `penman.lexer.PATTERNS` ([#45][])
* `penman.model.Model.is_reifiable()` (now `is_role_reifiable()`)

### Changed

* Remove support for numeric data detection and casting ([#44][])
* Allow commas and carets in the `SYMBOL` pattern ([#43][])
* Allow tildes in the `ROLE` and `SYMBOL` patterns ([#45][])
* Surface alignments are extracted and formatted in `penman.layout`,
  not `penman.lexer` or `penman.codec` ([#45][])
* Tree branches are simple 2-tuples: `(role, target)` ([#45][])
* `penman.layout.appears_inverted()` better detects inverted triples
  when the target in the serialization was just a variable ([#47][])
* Nodes without concepts get a default concept of `None` (again); this
  means that `(b :ARG0-of (a))` is 3 triples instead of 1, but it will
  help distinguish node attributes from true edges.
* `penman.layout.interpret()` no longer deinverts attributes; doing so
  leads to triples with constants as a source (or treating constants
  as variables); this requires looking at the variables of tree nodes
  to determine which are attributes.
* `penman.graph.Graph.attributes()` no longer returns `:instance`
  triples ([#48][])


## [v0.8.0][]

**Release date: 2019-12-12**

This release adds a handful of minor functions and expands the
documentation.

### Added

* `penman.layout.appears_inverted()` ([#37][])
* Tree branch sorting functions ([#31][])
  - `penman.model.Model.original_order()`
  - `penman.model.Model.canonical_order()`
  - `penman.model.Model.random_order()`
* `penman.layout.rearrange()` ([#31][])
* `--rearrange=(canonical|random)` command-line option


## [v0.7.2][]

**Release date: 2019-11-25**

### Added

* `-q` / `--quiet` command line option
* `-v` / `--verbose` command line option
* Loggers that print some diagnostic information at the DEBUG and INFO
  levels

### Fixed

* Remove superfluous `POP` layout markers when graphs have duplicated
  triples ([#34][])
* Avoid `KeyError` on edge and attribute reification when graphs have
  duplicated triples ([#35][])

### Changed

* `Model.reify()` no longer inverts the incoming triple


## [v0.7.1][]

**Release date: 2019-11-21**

The [v0.7.0](#v070) release was missing a declaration for the new
`penman.models` sub-package, so it was not available for new
installs. This release fixes that.

### Fixed

* The `penman.models` package is now declared in `setup.py`
* The documentation now looks one level up when building (this is just
  "in case", as I think the missing package problem was the real
  culprit for faulty documentation builds.)


## [v0.7.0][]

**Release date: 2019-11-21**

This release comprises a major restructuring from previous
versions. No longer is there a single `penman.py` module, but the
`penman` package, which has the following modules:

- `__about__` - package meta-information
- `codec` - high-level parsing and formatting
- `epigraph` - epigraphical markers
- `exceptions` - exception classes
- `graph` - triple and graph classes
- `interface` - `load()`, `dump()`, etc.
- `layout` - interpretation and configuration of trees
- `lexer` - low-level parsing
- `main` - command-line interface
- `model` - semantic model class
- `surface` - surface alignment information
- `transform` - tree and graph transformations
- `tree` - tree class
- `types` - static type checking definitions

In addition, there is a `models` sub-package for provided semantic
models, although it currently only contains one: `models.amr`.

While some of the original API is preserved through imports in
`penman/__init__.py`, there are a number of backward-incompatible
changes in this release. Changes that affect the old API are listed
below, but otherwise the new functionality is under the added
modules.

### Python Versions

* Removed support for Python 2.7
* Removed support for Python 3.3
* Removed support for Python 3.4
* Removed support for Python 3.5
* Added support for Python 3.6
* Added support for Python 3.7
* Added support for Python 3.8

### Added

* `penman.Graph.epidata`
* `penman.Graph.metadata`
* `penman.PENMANCodec.parse()`
* `penman.PENMANCodec.parse_triples()`
* `penman.PENMANCodec.iterparse()`
* `penman.PENMANCodec.format()`
* `penman.PENMANCodec.format_triples()`
* `penman.codec`
* `penman.epigraph`
* `penman.epigraph.Epidatum`
* `penman.exceptions`
* `penman.exceptions.GraphError`
* `penman.exceptions.LayoutError`
* `penman.exceptions.SurfaceError`
* `penman.exceptions.ModelError`
* `penman.graph`
* `penman.graph.CONCEPT_ROLE`
* `penman.graph.Edge`
* `penman.graph.Attribute`
* `penman.layout`
* `penman.layout.LayoutMarker`
* `penman.layout.Push`
* `penman.layout.POP`
* `penman.layout.interpret()`
* `penman.layout.configure()`
* `penman.layout.reconfigure()`
* `penman.layout.has_valid_layout()`
* `penman.lexer`
* `penman.lexer.PATTERNS`
* `penman.lexer.PENMAN_RE`
* `penman.lexer.TRIPLE_RE`
* `penman.lexer.Token`
* `penman.lexer.TokenIterator`
* `penman.lexer.lex()`
* `penman.model`
* `penman.model.Model`
* `penman.models`
* `penman.models.amr`
* `penman.models.amr.roles`
* `penman.models.amr.normalizations`
* `penman.models.amr.reifications`
* `penman.models.amr.model`
* `penman.surface` ([#19][])
* `penman.surface.AlignmentMarker`
* `penman.surface.Alignment`
* `penman.surface.RoleAlignment`
* `penman.surface.alignments()`
* `penman.surface.role_alignments()`
* `penman.transform`
* `penman.transform.canonicalize_roles()`
* `penman.transform.reify_edges()` ([#27][])
* `penman.transform.reify_attributes()`
* `penman.transform.indicate_branches()`
* `penman.tree` ([#16][])
* `penman.tree.Tree`
* `penman.tree.is_atomic()`

### Removed

* [docopt](https://github.com/docopt/docopt) dependency ([#20][])
* `penman.EncodeError`
* `penman.AMRCodec`
* `penman.Triple.inverted`
* `penman.PENMANCodec.is_relation_inverted()`
* `penman.PENMANCodec.invert_relation()`
* `penman.PENMANCodec.handle_triple()`
* `penman.PENMANCodec.triples_to_graph()`
* `penman.original_order()`
* `penman.out_first_order()`
* `penman.alphanum_order()`

### Fixed

* Graphs can no longer be encoded with attributes as the top ([#15][])
* For AMR, both `:mod` and `:domain` are for non-inverted relations,
  although their inverses can be canonicalized to the other ([#26][])
* Epigraphical layout markers allow the tree structure to be preserved
  without modifying the pure graph's triples ([#25][])

### Changed

* Restructured project as a package
* Use Sphinx-generated documentation
* Replaced "relation" with "role" when "role" is intended.
* Replaced "node type" and "node label" with "concept"
* Replaced "node identifier" with "variable"
* Roles now include the colon (`:ARG0`, not `ARG0`), following
  convention
* `penman.PENMANCodec` no longer takes the `indent` or `relation_sort`
  parameters
* `penman.PENMANCodec.encode()` now takes `indent` and `compact`
  parameters
* `penman.PENMANCodec.iterdecode()` works on streams ([#21][])
* `penman.PENMANCodec` now reads comments with metadata ([#23][])
* `penman.PENMANCodec` no longer accepts non-symbol variables ([#13][])
* `penman.dump()` now writes iteratively to a stream ([#22][])
* The following no longer take the `cls` parameter for a codec class,
  nor `**kwargs` to configure that class, but instead a `model`
  parameter for the semantic model:
  - `penman.decode()`
  - `penman.encode()`
  - `penman.loads()`
  - `penman.dumps()`
  - `penman.load()`
  - `penman.dump()`
* The following now take the formatting parameters `indent` and
  `compact`:
  - `penman.encode()`
  - `penman.dumps()`
  - `penman.dump()`
* `penman.Graph.triples` is now a member variable instead of a method
* `penman.Graph` class is mutable ([#32][])
* Concepts (node labels) in `penman.Graph` now have a special role
  known to the `penman.graph` module, which can help avoid some
  reentrancy issues ([#29][])


## [v0.6.2][]

**Release date: 2017-10-04**

### Fixed

* Value-cast patterns terminated with `$` to invalid casts ([#9][])
* Raise EncodeError when attempting to encode empty graphs ([#14][])
* Redefine NODETYPE_RE for AMRCodec ([#17][])
* Remove specific float and int parsing in variables/nodetypes for the
  default parser (the numeric values are still parses as atoms) ([#17][])


## [v0.6.1][]

**Release date: 2017-03-14**

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

**Release date: 2017-03-04**

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

**Release date: 2017-02-20**

### Fixed

* Numeric conversion in `PENMANCodec.handle_triple()` now happens to
  both sources and targets, and `handle_triple()` is now run on the top,
  as well. Fixes #4
* `Graph.__str__()` now initializes a default codec for serialization.
* Incorrect script usage fixed in README.md and from `penman.py --help`
* Updated documentation


## [v0.5.0][]

**Release date: 2017-01-13**

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

**Release date: 2017-01-01**

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

**Release date: 2017-01-01**

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

**Release date: 2016-11-09**

### Changed

* PENMAN serialization uses slightly more sophisticated default weights
  for choosing when to invert edges, which prevents some ugly graphs.
* `Graph.to_triples()` takes a `normalize=True` parameter (default `False`)
  to uninvert inverted edges.
* Running the script with `--triples` now prints the logical conjunction
  of triples (e.g. `instance-of(b, bark-01) ^ ARG0(b, d) ^
  instance-of(d, dog)`).


## [v0.1.0][]

**Release date: 2016-11-08**

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
[v0.7.0]: ../../releases/tag/v0.7.0
[v0.7.1]: ../../releases/tag/v0.7.1
[v0.7.2]: ../../releases/tag/v0.7.2
[v0.8.0]: ../../releases/tag/v0.8.0
[v0.9.0]: ../../releases/tag/v0.9.0
[v0.9.1]: ../../releases/tag/v0.9.1
[README]: README.md

[#4]: https://github.com/goodmami/penman/issues/4
[#6]: https://github.com/goodmami/penman/issues/6
[#9]: https://github.com/goodmami/penman/issues/9
[#13]: https://github.com/goodmami/penman/issues/13
[#14]: https://github.com/goodmami/penman/issues/14
[#15]: https://github.com/goodmami/penman/issues/15
[#16]: https://github.com/goodmami/penman/issues/16
[#17]: https://github.com/goodmami/penman/issues/17
[#19]: https://github.com/goodmami/penman/issues/19
[#20]: https://github.com/goodmami/penman/issues/20
[#21]: https://github.com/goodmami/penman/issues/21
[#22]: https://github.com/goodmami/penman/issues/22
[#23]: https://github.com/goodmami/penman/issues/23
[#25]: https://github.com/goodmami/penman/issues/25
[#26]: https://github.com/goodmami/penman/issues/26
[#27]: https://github.com/goodmami/penman/issues/27
[#29]: https://github.com/goodmami/penman/issues/29
[#31]: https://github.com/goodmami/penman/issues/31
[#32]: https://github.com/goodmami/penman/issues/32
[#34]: https://github.com/goodmami/penman/issues/34
[#35]: https://github.com/goodmami/penman/issues/35
[#37]: https://github.com/goodmami/penman/issues/37
[#39]: https://github.com/goodmami/penman/issues/39
[#40]: https://github.com/goodmami/penman/issues/40
[#41]: https://github.com/goodmami/penman/issues/41
[#42]: https://github.com/goodmami/penman/issues/42
[#43]: https://github.com/goodmami/penman/issues/43
[#44]: https://github.com/goodmami/penman/issues/44
[#45]: https://github.com/goodmami/penman/issues/45
[#47]: https://github.com/goodmami/penman/issues/47
[#48]: https://github.com/goodmami/penman/issues/48
[#50]: https://github.com/goodmami/penman/issues/50
[#52]: https://github.com/goodmami/penman/issues/52
[#53]: https://github.com/goodmami/penman/issues/53
