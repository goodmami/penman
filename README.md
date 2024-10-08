<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="/docs/_static/logo-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="/docs/_static/logo-light.svg">
    <img alt="Shows the Penman logo: a slash character between two parentheses." src="/docs/_static/logo-light.svg">
  </picture>
</div>
<h1 align="center">Penman &ndash; a library for PENMAN graph notation</h1>
<div align="center">

[![PyPI Version](https://img.shields.io/pypi/v/penman.svg)](https://pypi.org/project/Penman/)
![Python Support](https://img.shields.io/pypi/pyversions/penman.svg)
[![.github/workflows/checks.yml](https://github.com/goodmami/penman/actions/workflows/checks.yml/badge.svg?branch=main)](https://github.com/goodmami/penman/actions/workflows/checks.yml)
[![Documentation Status](https://readthedocs.org/projects/penman/badge/?version=latest)](https://penman.readthedocs.io/en/latest/?badge=latest)

</div>

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

For Javascript, see [chanind/penman-js](https://github.com/chanind/penman-js).


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

If you make use of Penman in your work, please cite [Goodman, 2020].
The BibTeX is below:

[Goodman, 2020]: https://www.aclweb.org/anthology/2020.acl-demos.35/

```bibtex
@inproceedings{goodman-2020-penman,
    title = "{P}enman: An Open-Source Library and Tool for {AMR} Graphs",
    author = "Goodman, Michael Wayne",
    booktitle = "Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics: System Demonstrations",
    month = jul,
    year = "2020",
    address = "Online",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/2020.acl-demos.35",
    pages = "312--319",
    abstract = "Abstract Meaning Representation (AMR) (Banarescu et al., 2013) is a framework for semantic dependencies that encodes its rooted and directed acyclic graphs in a format called PENMAN notation. The format is simple enough that users of AMR data often write small scripts or libraries for parsing it into an internal graph representation, but there is enough complexity that these users could benefit from a more sophisticated and well-tested solution. The open-source Python library Penman provides a robust parser, functions for graph inspection and manipulation, and functions for formatting graphs into PENMAN notation. Many functions are also available in a command-line tool, thus extending its utility to non-Python setups.",
}
```

For the graph transformation/normalization work, please cite [Goodman, 2019].
The BibTeX is below:

[Goodman, 2019]: https://jaslli.org/files/proceedings/05_paclic33_postconf.pdf

``` bibtex
@inproceedings{Goodman:2019,
  title     = "{AMR} Normalization for Fairer Evaluation",
  author    = "Goodman, Michael Wayne",
  booktitle = "Proceedings of the 33rd Pacific Asia Conference on Language, Information, and Computation",
  year      = "2019",
  pages     = "47--56",
  address   = "Hakodate",
  publisher = "Japanese Association for the Study of Logic, Language and Information",
  url       = "https://jaslli.org/files/proceedings/05_paclic33_postconf.pdf",
  abstract  = "Abstract Meaning Representation (AMR; Banarescu et al., 2013) encodes the meaning of sentences as a directed graph and Smatch (Cai and Knight, 2013) is the primary metric for evaluating AMR graphs. Smatch, however, is unaware of some meaning-equivalent variations in graph structure allowed by the AMR Specification and gives different scores for AMRs exhibiting these variations. In this paper I propose four normalization methods for helping to ensure that conceptually equivalent AMRs are evaluated as equivalent. Equivalent AMRs with and without normalization can look quite different—comparing a gold corpus to itself with relation reification alone yields a difference of 25 Smatch points, suggesting that the outputs of two systems may not be directly comparable without normalization. The algorithms described in this paper are implemented on top of an existing open-source Python toolkit for AMR and will be released under the same license."
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
