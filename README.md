# Penman

This module models graphs encoded in the PENMAN (e.g., [AMR][])
notation. It is meant to be used as a Python library or as a script.

### Features

* PENMAN notation
  - [x] reading
  - [x] writing
    - [x] select new top
    - [x] re-indent
* Triples
  - [x] graph instantiation
  - [x] inspecting list of triples
  - [ ] reading
  - [x] writing
    - [x] print list of triples
    - [x] format as conjunction of logical triples
    - [x] normalize inverse edges
* Graphs
  - [ ] node and edge inspection
  - [ ] graph metrics
  - [ ] graph manipulation

### Library Usage

```python
>>> from penman import Graph
>>> g = Graph.from_penman('(b / bark :ARG0 (d / dog))')
>>> g.to_triples()
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

[AMR]: http://amr.isi.edu/
