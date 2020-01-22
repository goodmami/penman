
# Penman &mdash; a Python library for PENMAN graph notation

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
  - Adjust indentation and compactness
  - Select a new top node
  - Rearrange edges
  - Restructure the tree shape
  - Relabel node variables
- [x] [Transform][transform] the graph
  - Canonicalize roles
  - Reify and dereify edges
  - Reify attributes
  - Embed the tree structure with additional `TOP` triples
- [x] [AMR model][]: role inventory and transformations
- [x] Tested (but not yet 100% coverage)
- [x] Documented (see the [documentation][])


### Library Usage

```python-console
>>> import penman
>>> g = penman.decode('(b / bark-01 :ARG0 (d / dog))')
>>> g.triples
[('b', ':instance', 'bark-01'), ('b', ':ARG0', 'd'), ('d', ':instance', 'dog')]
>>> print(penman.encode(g))
(b / bark-01
   :ARG0 (d / dog))
>>> print(penman.encode(g, top='d', indent=6))
(d / dog
      :ARG0-of (b / bark-01))
>>> print(penman.encode(g, indent=False))
(b / bark-01 :ARG0 (d / dog))
```

([more information][as-library])

[as-library]: https://penman.readthedocs.io/en/latest/basic.html#using-penman-as-a-library


### Script Usage

```console
$ penman --help
usage: penman [-h] [-V] [-v] [-q] [--model FILE | --amr] [--indent N]
              [--compact] [--triples] [--make-variables FMT] [--rearrange KEY]
              [--reconfigure KEY] [--canonicalize-roles] [--reify-edges]
              [--dereify-edges] [--reify-attributes] [--indicate-branches]
              [FILE [FILE ...]]

Read and write graphs in the PENMAN notation.

positional arguments:
  FILE                  read graphs from FILEs instead of stdin

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -v, --verbose         increase verbosity
  -q, --quiet           suppress output on <stdout> and <stderr>
  --model FILE          JSON model file describing the semantic model
  --amr                 use the AMR model

formatting options:
  --indent N            indent N spaces per level ("no" for no newlines)
  --compact             compactly print node attributes on one line
  --triples             print graphs as triple conjunctions

normalization options:
  --make-variables FMT  recreate node variables with FMT (e.g.: '{prefix}{j}')
  --rearrange KEY       reorder the branches of the tree
  --reconfigure KEY     reconfigure the graph layout with reordered triples
  --canonicalize-roles  canonicalize role forms
  --reify-edges         reify all eligible edges
  --dereify-edges       dereify all eligible edges
  --reify-attributes    reify all attributes
  --indicate-branches   insert triples to indicate tree structure

$ penman <<< "(w / want-01 :ARG0 (b / boy) :ARG1 (g / go :ARG0 b))"
(w / want-01
   :ARG0 (b / boy)
   :ARG1 (g / go
            :ARG0 b))
```

([more information][as-tool])

[as-tool]: https://penman.readthedocs.io/en/latest/basic.html#using-penman-as-a-tool


### PENMAN Notation

A description of the PENMAN notation can be found in the
[documentation](https://penman.readthedocs.io/en/latest/notation.html).
See also [Nathan Schneider's PEG for
AMR](https://github.com/nschneid/amr-hackathon/blob/master/src/amr.peg).

This module expands the notation slightly to allow for untyped nodes
(e.g., `(x)`) and anonymous relations (e.g., `(x : (y))`). It also
accommodates slightly malformed graphs as well as surface alignments.

### Citation

There is not (yet) a canonical citation for the Penman library, so
putting https://github.com/goodmami/penman in a footnote is
sufficient. If you are referring to the graph
transformation/normalization work or prefer an academic citation,
please use the following:

``` bibtex
@inproceedings{Goodman:2019,
  title     = "{AMR} Normalization for Fairer Evaluation",
  author    = "Goodman, Michael Wayne",
  booktitle = "Proceedings of the 33rd Pacific Asia Conference on Language, Information, and Computation",
  year      = "2019",
  pages     = "47--56",
  address   = "Hakodate"
}
```

### Disclaimer

This project is not affiliated with [ISI][], the [PENMAN][] project,
or the [AMR][] project.

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
