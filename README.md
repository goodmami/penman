
[![PyPI Version](https://img.shields.io/pypi/v/penman.svg)](https://pypi.org/project/Penman/)
![Python Support](https://img.shields.io/pypi/pyversions/penman.svg)
[![Build Status](https://travis-ci.org/goodmami/penman.svg?branch=develop)](https://travis-ci.org/goodmami/penman)

This module models graphs encoded in the [PENMAN notation](#penman-notation)
(e.g., [AMR][]). It may be used as a Python library or as a script.
It does not include any of the concept inventory or text-generation
capabilities of the [PENMAN][] project.

### Features

Serialization between graphs and either PENMAN notation or triple
conjunctions is provided by the [PENMANCodec][] class's `encode()`,
`decode()`, and `iterdecode()` methods. Module-level functions
provide a convenient interface to this class:

* [encode(g)][] - serialized graph *g* and return the string
* [decode(s)][] - deserialize *s* and return the graph
* [load(f)][] - return all graphs in file *f*
* [loads(s)][] - return all graphs in string *s*
* [dump(gs, f)][] - serialize all graphs in *gs* and write to file *f*
* [dumps(gs)][] - serialize all graphs in *gs* and return the string

Passing `triples=True` to the above functions does (de)serialization
to/from conjunctions of triples. The `indent` parameter of `encode()`,
`dump()`, and `dumps()` changes how PENMAN-serialized graphs are
indented (by default, they are adaptively indented to line up with
their containing node). Deserialized [Graph][] objects may be inspected
and queried for their variables (nonterminal node identifiers), triples,
etc. For more information, please consult the [documentation][], and see
the example [below](#library-usage).

### Library Usage

```python
>>> import penman
>>> g = penman.decode('(b / bark :ARG0 (d / dog))')
>>> g.triples()
[Attribute(source='b', role=':instance', target='bark'), Edge(source='b', role=':ARG0', target='d'), Attribute(source='d', role=':instance', target='dog')]
>>> print(penman.encode(g))
(b / bark
   :ARG0 (d / dog))
>>> print(penman.encode(g, top='d', indent=6))
(d / dog
      :ARG0-of (b / bark))
>>> print(penman.encode(g, indent=False))
(b / bark :ARG0 (d / dog))
```

### Script Usage

```console
$ penman --help
usage: penman [-h] [-V] [--model FILE | --amr] [--indent N] [--compact]
              [--triples]
              [FILE [FILE ...]]

Read and write graphs in the PENMAN notation.

positional arguments:
  FILE           read graphs from FILEs instead of stdin

optional arguments:
  -h, --help     show this help message and exit
  -V, --version  show program's version number and exit
  --model FILE   JSON model file describing the semantic model
  --amr          use the AMR model
  --indent N     indent N spaces per level ("no" for no newlines)
  --compact      compactly print node attributes on one line
  --triples      print graphs as triple conjunctions

$ penman <<< "(w / want-01 :ARG0 (b / boy) :ARG1 (g / go :ARG0 b))"
(w / want-01
   :ARG0 (b / boy)
   :ARG1 (g / go
            :ARG0 b))
```

### Requirements

- Python 3.6+

### PENMAN Notation

The [PENMAN][] project was a large effort at natural language generation,
and what I'm calling "PENMAN notation" is more accurately "Sentence Plan
Language" (SPL; [Kaspar 1989]), but I'll stick with "PENMAN notation"
because it may be a more familiar name to modern users and it also sounds
less specific to sentence representations, e.g., in case someone wants to
use the format to encode arbitrary graphs.

This module expands the notation slightly to allow for untyped nodes
(e.g., `(x)`) and anonymous relations (e.g., `(x : (y))`). A [PEG][]\*
definition for the notation is given below (for simplicity, whitespace
is not explicitly included; assume all nonterminals can be surrounded
by `/\s+/`):

```ruby
Start     <- Node
Node      <- '(' Variable NodeLabel? Edge* ')'
NodeLabel <- '/' Atom Alignment?
Edge      <- Role Alignment? Target
Target    <- Node | Atom Alignment?
Atom      <- String | Float | Integer | Variable | Constant
Variable  <- Symbol
Constant  <- Symbol
Role      <- /:[^\s()\/,:~]*/
String    <- /"[^"\\]*(?:\\.[^"\\]*)*"/
Float     <- /[-+]?(((\d+\.\d*|\.\d+)([eE][-+]?\d+)?)|\d+[eE][-+]?\d+)/
Integer   <- /[-+]?\d+(?=[ )\/:])/
Symbol    <- /[^\s()\/,:~]+/
Alignment <- /~([a-zA-Z]\.?)?\d+(,\d+)*/
```

\* *Note: I use `|` above for ordered-choice instead of `/` so that `/`
can be used to surround regular expressions.*

Both `Variable` and `Constant` above resolve as `Symbol`, making their
use in the `Atom` production redundant, but they are shown like this
for their semantic contribution. A `Variable` is distinguished from a
`Constant` simply by its use as the identifier of a node.

A more restricted variant of the grammar for AMR might further
restrict this grammar by making the `NodeLabel` nonterminal required
on `Node`, changing `Atom` to `Symbol` on `NodeLabel`, changing `Role`
to disallow relations without labels, and changing `Variable` to a
form like `/[a-z]+\d*/`. See also [Nathan Schneider's PEG for
AMR](https://github.com/nschneid/amr-hackathon/blob/master/src/amr.peg).

### Disclaimer

This project is not affiliated with [ISI], the [PENMAN] project, or the
[AMR] project.

[PENMAN]: http://www.isi.edu/natural-language/penman/penman.html
[AMR]: http://amr.isi.edu/
[Kasper 1989]: http://www.aclweb.org/anthology/H89-1022
[PEG]: https://en.wikipedia.org/wiki/Parsing_expression_grammar
[ISI]: http://isi.edu/

[documentation]: docs/API.md
[PENMANCodec]: docs/API.md#penmancodec
[AMRCodec]: docs/API.md#amrcodec
[encode(g)]: docs/API.md#encode
[decode(s)]: docs/API.md#decode
[load(f)]: docs/API.md#load
[loads(s)]: docs/API.md#loads
[dump(gs, f)]: docs/API.md#dump
[dumps(gs)]: docs/API.md#dumps
[Graph]: docs/API.md#graph
