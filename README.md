
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
- [x] Check graphs for model compliance
- [x] Tested (but not yet 100% coverage)
- [x] Documented (see the [documentation][])


### Library Usage

```python-console
>>> import penman
>>> g = penman.decode('(b / bark-01 :ARG0 (d / dog))')
>>> g.triples
[('b', ':instance', 'bark-01'), ('b', ':ARG0', 'd'), ('d', ':instance', 'dog')]
>>> g.edges()
[Edge(source='b', role=':ARG0', target='d')]
>>> print(penman.encode(g, indent=3))
(b / bark-01
   :ARG0 (d / dog))
>>> print(penman.encode(g, indent=None))
(b / bark-01 :ARG0 (d / dog))

```

([more information](https://penman.readthedocs.io/en/latest/library.html))


### Script Usage

```console
$ echo "(w / want-01 :ARG0 (b / boy) :ARG1 (g / go :ARG0 b))" | penman
(w / want-01
   :ARG0 (b / boy)
   :ARG1 (g / go
            :ARG0 b))
$ echo "(w / want-01 :ARG0 (b / boy) :ARG1 (g / go :ARG0 b))" | penman --make-variables="a{i}"
(a0 / want-01
    :ARG0 (a1 / boy)
    :ARG1 (a2 / go
              :ARG0 a1))

```

([more information](https://penman.readthedocs.io/en/latest/command.html))


### Demo

For a demonstration of the API usage, see the included
[Jupyter](https://jupyter.org/) notebook:

- View it on GitHub: [docs/api-demo.ipynb](docs/api-demo.ipynb)
- Run it on [mybinder.org](https://mybinder.org/):
  [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/goodmami/penman/master?filepath=docs%2Fapi-demo.ipynb)

  (Note: clear the output before running: *Cell* > *All Output* >
  *Clear*):


### PENMAN Notation

A description of the PENMAN notation can be found in the
[documentation](https://penman.readthedocs.io/en/latest/notation.html).
This module expands the original notation slightly to allow for
untyped nodes (e.g., `(x)`) and anonymous relations (e.g., `(x :
(y))`). It also accommodates slightly malformed graphs as well as
surface alignments.

### Citation

The canonical citation for the Penman library will soon be a system
demo paper for [ACL 2020]. Until the proceedings are published, simply
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

[ACL 2020]: https://acl2020.org/

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
