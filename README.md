
| Branch | Status |
| ------ | ------ |
| [master](https://github.com/goodmami/penman/tree/master)  | [![Build Status](https://travis-ci.org/goodmami/penman.svg?branch=master)](https://travis-ci.org/goodmami/penman) |
| [develop](https://github.com/goodmami/penman/tree/develop) | [![Build Status](https://travis-ci.org/goodmami/penman.svg?branch=develop)](https://travis-ci.org/goodmami/penman) |

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
[Triple(source='b', relation='instance', target='bark'), Triple(source='d', relation='instance', target='dog'), Triple(source='b', relation='ARG0', target='d')]
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

```
$ python penman.py --help
Penman

An API and utility for working with graphs in PENMAN notation.

Usage: penman.py [-h|--help] [-V|--version] [options]

Options:
  -h, --help                display this help and exit
  -V, --version             display the version and exit
  -i FILE, --input FILE     read graphs from FILE instead of stdin
  -o FILE, --output FILE    write output to FILE instead of stdout
  -t, --triples             print graphs as triple conjunctions
  --indent N                indent N spaces per level ("no" for no newlines)
  --amr                     use AMR codec instead of generic PENMAN one

$ python penman.py <<< "(w / want-01 :ARG0 (b / boy) :ARG1 (g / go :ARG0 b))"
(w / want-01
   :ARG0 (b / boy)
   :ARG1 (g / go
            :ARG0 b))
```

### Requirements

- Python 2.7 or 3.3+
- [docopt](https://pypi.python.org/pypi/docopt) (for script usage)

### PENMAN Notation

The [PENMAN][] project was a large effort at natural language generation,
and what I'm calling "PENMAN notation" is more accurately "Sentence Plan
Language" (SPL; [Kaspar 1989]), but I'll stick with "PENMAN notation"
because it may be a more familiar name to modern users and it also sounds
less specific to sentence representations, e.g., in case someone wants to
use the format to encode arbitrary graphs.

This module expands the notation slightly to allow for untyped nodes
(e.g., `(x)`) and anonymous relations (e.g., `(x : (y))`). It is also
very permissive for the form of node identifiers (and other atoms). A
[PEG][]\* definition for the notation is given below (for simplicity,
whitespace is not explicitly included; assume all nonterminals can be
surrounded by `/\s+/`):

```ruby
Start    <- Node
Node     <- '(' NodeData ')'
NodeData <- Variable ('/' NodeType)? Edge*
NodeType <- Atom
Variable <- Atom
Edge     <- Relation Value
Relation <- /:[^\s(),]*/
Value    <- Node | Atom
Atom     <- String | Float | Integer | Symbol
String   <- /"[^"\\]*(?:\\.[^"\\]*)*"/
Float    <- /[-+]?(((\d+\.\d*|\.\d+)([eE][-+]?\d+)?)|\d+[eE][-+]?\d+)/
Integer  <- /[-+]?\d+/
Symbol   <- /[^\s()\/,]+/
```

\* *Note: I use `|` above for ordered-choice instead of `/` so that `/`
can be used to surround regular expressions.*

A more restricted variant of the grammar for AMR might make the `('/'
NodeType)` group required, and NodeTypes (maybe renamed "Concepts")
could be given as a disjunction of allowed names. Similarly, Relations
could be a disjunction of allowed names and possible inversions, or
otherwise require at least one character after `:`. It might also
restrict Variables to a form like `/[a-z]+\d*/` and also restrict Atom
values in some way. The included [AMRCodec][] employs most of these
restrictions and raises `DecodeError`s for graphs it deems invalid. See
also [Nathan Schneider's PEG for AMR](https://github.com/nschneid/amr-hackathon/blob/master/src/amr.peg).

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
