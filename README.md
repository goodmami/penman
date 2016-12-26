# Penman

This module models graphs encoded in the [PENMAN notation](#penman-notation)
(e.g., [AMR][]). It may be used as a Python library or as a script.
It does not include any of the concept inventory or text-generation
capabilities of the [PENMAN][] project.

### Features

* PENMAN notation
  - [x] reading
  - [x] writing
    - [x] select new top
    - [x] re-indent
* Triples
  - [x] graph instantiation
  - [x] inspecting list of triples
  - [x] reading
  - [x] writing
    - [x] print list of triples
    - [x] format as conjunction of logical triples
    - [x] normalize inverse edges
* Graphs
  - [x] node and edge inspection
  - [ ] graph metrics
  - [ ] graph manipulation

### Library Usage

```python
>>> from penman import Graph
>>> g = Graph.from_penman('(b / bark :ARG0 (d / dog))')
>>> g.triples()
[Triple(source='b', relation='instance-of', target='bark'), Triple(source='b', relation='ARG0', target='d'), Triple(source='d', relation='instance-of', target='dog')]
>>> print(g.to_penman())
(b / bark
   :ARG0 (d / dog))
>>> print(g.to_penman(top='d'))
(d / dog
   :ARG0-of (b / bark))
```

### Script Usage

```bash
$ python penman.py --help
Penman

An API and utility for working with graphs in the PENMAN format.

Usage: penman.py [-h|--help] [-V|--version] [options]

Arguments:
  FILE                      the input file

Options:
  -h, --help                display this help and exit
  -V, --version             display the version and exit
  -v, --verbose             verbose mode (may be repeated: -vv, -vvv)
  -i FILE, --input FILE     read graphs from FILE instanced of stdin
  -o FILE, --output FILE    write output to FILE instead of stdout
  -t, --triples             print graphs as triples

$ python penman.py <<< "(w / want-01 :ARG0 (b / boy) :ARG1 (g / go :ARG0 b))"
(w / want-01
   :ARG0 (b / boy)
   :ARG1 (g / go
            :ARG0 b))
```

### Requirements

- Python 2.7 or 3.3+
- [docopt](https://pypi.python.org/pypi/docopt)

### PENMAN Notation

The [PENMAN][] project was a large effort at natural language generation,
and what I'm calling "PENMAN notation" is in fact "Sentence Plan
Language" (SPL; [Kaspar 1989]), but I'll stick with "PENMAN notation"
because it may be a more familiar name to modern users and it also sounds
less specific to sentence representations, e.g., in case someone wants to
use the format to encode arbitrary graphs. A [PEG][] definition for the
notation is given below (for clarity, whitespace is not explicitly
included; assume all nonterminals can be surrounded by `/\s+/`):

```ruby
Graph    <- Node
Node     <- '(' NodeData ')'
NodeData <- Variable ('/' Type)? Relation*
Type     <- String / Symbol
Variable <- Symbol
Relation <- Role Value
Role     <- /:[^\s(]+/
Value    <- Node / Float / Integer / String / Symbol
String   <- /"[^"\\]*(?:\\.[^"\\]*)*"/
Symbol   <- /[^\s)\/]+/
Float    <- /-?(0|[1-9]\d*)(\.\d+[eE][-+]?|\.|[eE][-+]?)\d+/
Integer  <- /-?\d+/
```

[PENMAN]: http://www.isi.edu/natural-language/penman/penman.html
[AMR]: http://amr.isi.edu/
[Kasper 1989]: http://www.aclweb.org/anthology/H89-1022
[PEG]: https://en.wikipedia.org/wiki/Parsing_expression_grammar
