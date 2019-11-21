
[![PyPI Version](https://img.shields.io/pypi/v/penman.svg)](https://pypi.org/project/Penman/)
![Python Support](https://img.shields.io/pypi/pyversions/penman.svg)
[![Build Status](https://travis-ci.org/goodmami/penman.svg?branch=develop)](https://travis-ci.org/goodmami/penman)
[![Documentation Status](https://readthedocs.org/projects/penman/badge/?version=latest)](https://penman.readthedocs.io/en/latest/?badge=latest)


This package models graphs encoded in [PENMAN
notation](#penman-notation) (e.g., [AMR][]), such as the following for
*the boy wants to go*:

```
(w / want-01
   :ARG0 (b / boy)
   :ARG1 (g / go
            :ARG0 b))
```

The Penman package may be used as a Python [library](#library-usage)
or as a [script](#script-usage).


### Features

- [x] Read and write PENMAN-serialized graphs or triple conjunctions
- [x] Read metadata in comments (e.g., `# ::id 1234`)
- [x] Read surface alignments (e.g., `foo~e.1,2`)
- [x] Inspect and manipulate the [graph][] or [tree][] structures
- [x] Customize graphs for writing:
  - [x] adjust indentation and compactness
  - [x] select a new top node
  - [x] rearrange edges (partially implemented)
  - [x] restructure the tree shape
- [x] [Transform][transform] the graph
  - [x] Canonicalize roles
  - [x] Reify edges
  - [x] Reify attributes
  - [x] Embed the tree structure with additional `TOP` triples
- [x] [AMR model][]: role inventory and transformations
- [x] Tested (but not yet 100% coverage)
- [x] Documented (see the [documentation][])


### Library Usage

```python
>>> import penman
>>> g = penman.decode('(b / bark :ARG0 (d / dog))')
>>> g.triples
[('b', ':instance', 'bark'), ('b', ':ARG0', 'd'), ('d', ':instance', 'dog')]
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
              [--triples] [--canonicalize-roles] [--reify-edges]
              [--reify-attributes] [--indicate-branches]
              [FILE [FILE ...]]

Read and write graphs in the PENMAN notation.

positional arguments:
  FILE                  read graphs from FILEs instead of stdin

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  --model FILE          JSON model file describing the semantic model
  --amr                 use the AMR model

formatting options:
  --indent N            indent N spaces per level ("no" for no newlines)
  --compact             compactly print node attributes on one line
  --triples             print graphs as triple conjunctions

normalization options:
  --canonicalize-roles  canonicalize role forms
  --reify-edges         reify all eligible edges
  --reify-attributes    reify all attributes
  --indicate-branches   insert triples to indicate tree structure

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
Language" (SPL; [Kaspar 1989][]), but I'll stick with "PENMAN notation"
because it may be a more familiar name to modern users and it also sounds
less specific to sentence representations, e.g., in case someone wants to
use the format to encode arbitrary graphs.

This module expands the notation slightly to allow for untyped nodes
(e.g., `(x)`) and anonymous relations (e.g., `(x : (y))`). A [PEG][]\*
definition for the notation is given below (for simplicity, whitespace
is not explicitly included; assume all nonterminals can be surrounded
by `/\s+/`):

```ruby
# Syntactic productions
Start     <- Node
Node      <- '(' Variable NodeLabel? Relation* ')'
NodeLabel <- '/' Concept Alignment?
Concept   <- Atom
Relation  <- Role Alignment? (Edge | Attribute)
Edge      <- Variable Alignment?
           | Node
Attribute <- Atom Alignment?
Atom      <- String | Float | Integer | Symbol
Variable  <- Symbol
# Lexical productions
Role      <- /:[^\s()\/,:~]*/
String    <- /"[^"\\]*(?:\\.[^"\\]*)*"/
Float     <- /[-+]?(((\d+\.\d*|\.\d+)([eE][-+]?\d+)?)|\d+[eE][-+]?\d+)/
Integer   <- /[-+]?\d+(?=[ )\/:])/
Symbol    <- /[^\s()\/,:~]+/
Alignment <- /~([a-zA-Z]\.?)?\d+(,\d+)*/
```

\* *Note: I use `|` above for ordered-choice instead of `/` so that `/`
can be used to surround regular expressions.*

There is ambiguity in that both `Edge` and `Attribute` can resolve
their first token to `Symbol` (via the `Variable` and `Atom`
productions, respectively), but they are shown like this for their
semantic contribution. A `Variable` is distinguished from other
`Symbol` tokens simply by its use as the identifier of a node.
Examples of non-variable `Symbol` tokens in AMR are concepts (e.g.,
`want-01`), `-` in `:polarity -`, `expressive` in `:mode expressive`,
etc.

The above grammar is for the PENMAN graphs that this library supports,
but AMR is more restrictive.  A variant for AMR might make the
`NodeLabel` nonterminal required on `Node`, change `Atom` to `Symbol`
on `Concept`, change `Role` to require at least one character after
`:` or even spell out all valid roles, and change `Variable` to a form
like `/[a-z]+[0-9]*/`. See also [Nathan Schneider's PEG for
AMR](https://github.com/nschneid/amr-hackathon/blob/master/src/amr.peg).


### Disclaimer

This project is not affiliated with [ISI], the [PENMAN] project, or the
[AMR] project.

[PENMAN]: http://www.isi.edu/natural-language/penman/penman.html
[AMR]: http://amr.isi.edu/
[Kasper 1989]: http://www.aclweb.org/anthology/H89-1022
[PEG]: https://en.wikipedia.org/wiki/Parsing_expression_grammar
[ISI]: http://isi.edu/

[documentation]: https://penman.readthedocs.io/
[graph]: https://penman.readthedocs.io/en/latest/api/penman.graph.html
[tree]: https://penman.readthedocs.io/en/latest/api/penman.tree.html
[transform]: https://penman.readthedocs.io/en/latest/api/penman.transform.html
[AMR model]: https://penman.readthedocs.io/en/latest/api/penman.models.amr.html
