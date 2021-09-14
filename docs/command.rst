
.. highlight:: console

Using the penman Command
========================

The :command:`penman` command allows users to perform most
reformatting tasks and predefined transformations without having to
write any code. For example, the following reformats a graph in one
line to a more conventional presentation::

  $ penman --indent 3 --compact <<< '(s / sleep-01 :polarity - :ARG0 (i / i))'
  (s / sleep-01 :polarity -
     :ARG0 (i / i))

The command becomes available at the command-line after installing
Penman (see :doc:`setup`). This guide will explain how to use the
command for several use cases.


Command Usage
-------------

The :command:`penman` command reads in data from stdin or from one or
more files then prints the results to stdout. By default, the command
will do nothing but apply the default formatting to the graphs, but
any input content that is not a graph or a metadata comment will be
discarded. To see what features are available for the current version
and how to call the command, run :command:`penman --help`::

  usage: penman [-h] [-V] [-v] [-q] [--model FILE | --amr | --noop] [--check]
                [--indent N] [--compact] [--triples] [--make-variables FMT]
                [--rearrange KEY] [--reconfigure KEY] [--canonicalize-roles]
                [--reify-edges] [--dereify-edges] [--reify-attributes]
                [--indicate-branches]
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
    --noop                use the no-op model
    --check               check graphs for compliance with the model

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


Reformatting
------------

There are two options for reformatting graphs that use newlines and
indentation to make them more friendly to human eyes. The
:command:`--indent` option controls how much each nesting level
indents and the :command:`--compact` option determines whether
attributes immediately following a concept appear on the same line as
the concept or on their own lines. For this section, consider the
following graph::

  $ x="(w / want-01 :polarity - :ARG0 (c / child) :ARG1 (g / go :ARG0 c))"


Default Formatting
''''''''''''''''''

By default, compact mode is off and :command:`--indent` has the
special value ``-1``, which performs "adaptive indenting". This
appears as follows::

  $ echo "$x" | penman
  (w / want-01
     :polarity -
     :ARG0 (c / child)
     :ARG1 (g / go
              :ARG0 c))


Changing the Indentation
''''''''''''''''''''''''

Giving a specific indent number makes Penman always indent that number
of spaces::

  $ echo "$x" | penman --indent 3
  (w / want-01
     :polarity -
     :ARG0 (c / child)
     :ARG1 (g / go
        :ARG0 c))


Compact Attributes
''''''''''''''''''

Compact mode puts attributes on the same line as the concept of their
node, but only if they appear in that position in the tree::

  $ echo "$x" | penman --compact
  (w / want-01 :polarity -
     :ARG0 (c / child)
     :ARG1 (g / go
              :ARG0 c))


Single-Line Graphs
''''''''''''''''''

With :command:`--indent=no`, Penman outputs a full graph on one
line. This can be useful for programs that read data line-by-line or
for creating bilingually aligned files::

  $ echo "$x" | penman
  (w / want-01
     :polarity -
     :ARG0 (c / child)
     :ARG1 (g / go
              :ARG0 c))
  $ echo "$x" | penman | penman --indent=no
  (w / want-01 :polarity - :ARG0 (c / child) :ARG1 (g / go :ARG0 c))

Note that :command:`--indent=0` is not the same as
:command:`--indent=no`. The former delimits parts with a single
newline but no leading space whereas the latter delimits parts with a
single space and no newlines. Also, the :command:`--compact` option is
relevant when :command:`--indent` has a numeric value but not for
:command:`--indent=no`.


Specifying a Model
------------------

While the formatting options do not require knowledge of the semantic
model, others, such as :command:`--check` and many transformations, do
require it. For Abstract Meaning Representation (AMR) graphs, the
:command:`--amr` option uses the built-in AMR model::

  $ penman --amr [...]

This model contains information about AMR's valid roles, canonical
role inversions (such as ``:domain`` to ``:mod``), and relation
reifications. Also available is the no-op model via :command:`--noop`,
which does not deinvert tree edges when interpreting the graph so that
a role like ``:ARG0-of`` is the role used in the graph triples.

Other models can be given by using the :command:`--model` option with
a path to a JSON file containing the model information::

  $ penman --model=xyz.json [...]

Custom models can be used for variations of AMR (e.g., different
versions or task-specific definitions) or even for different semantic
frameworks altogether.


Checking for Model Compliance
-----------------------------

With a model specified, a graph can be checked for compliance with
respect to the model using the :command:`--check` option. For graphs
already in PENMAN notation, the only relevant test is whether a role
is defined by the model. When graphs are constructed programatically,
there are additional checks for graphical well-formedness, such as for
an appropriate graph-top being set and for graph connectedness. When
used as a command, the exit code of the command will be ``0`` when
there are no errors or ``1`` when any errors are found. This helps
make the check be scriptable. Also, the individual errors are inserted
as metadata comments on each graph to help users resolve errors::

  $ good="(s / swim-01 :ARG0 (i / i))"                          # I swim.
  $ bad="(s / swim-01 :ARG0 (i / i) :stroke (b / backstroke))"  # I swim backstroke.
  $ if ( echo "$good" | penman --amr --check ); then
  >   echo "valid"
  > else
  >   echo "invalid"
  > fi
  (s / swim-01
     :ARG0 (i / i))
  valid
  $ if ( echo "$bad" | penman --amr --check ); then
  >   echo "valid"
  > else
  >   echo "invalid"
  > fi
  # ::error-1 (s :stroke b) invalid role
  (s / swim-01
     :ARG0 (i / i)
     :stroke (b / backstroke))
  invalid


Transforming Graphs
-------------------

Penman's transformations work either on the tree or the graph representation.


Relabeling Nodes
''''''''''''''''

The simplest transformation maps variables to a new form with the
:command:`--make-variables` option. In English AMR the variables use
the first letter of the concept and, if it is not unique, the 1-based
index starting from the second when traversing the tree in depth-first
order. AMR's primary evaluation tool smatch relabels all nodes
internally so one side uses ``a0``, ``a1``, etc. and the other side
uses ``b0``, ``b1``, etc. Penman allows users to specify the variable
format with three template variables:

  - ``{prefix}`` uses the first character of a node's concept
  - ``{i}`` is the 0-based index of a node's occurrence
  - ``{j}`` is the 1-based index of a node's occurrence, where index 1 is blank

Unlike the other transformations, :command:`--make-variables` does not
require a model::

  $ original="(x0 / chase-01 :ARG0 (x1 / cat) :ARG1 (x2 / mouse))"
  $ echo "$original" | penman --make-variables='a{i}'
  (a0 / chase-01
      :ARG0 (a1 / cat)
      :ARG1 (a2 / mouse))
  $ echo "$original" | penman --make-variables='{prefix}{j}'
  (c / chase-01
     :ARG0 (c2 / cat)
     :ARG1 (m / mouse))


Rearranging Branches
''''''''''''''''''''

Tree branches can be rearranged without changing the overall tree
structure using the :command:`--rearrange` option. It takes the name
of a method for sorting the branches on a node::

  $ original="(c / chase-01 :ARG1 (m / mouse) :polarity - :ARG0 (c2 / cat))"
  $ echo "$original" | penman --rearrange=attributes-first
  (c / chase-01
     :polarity -
     :ARG1 (m / mouse)
     :ARG0 (c2 / cat))
  $ echo "$original" | penman --rearrange=alphanumeric
  (c / chase-01
     :ARG0 (c2 / cat)
     :ARG1 (m / mouse)
     :polarity -)

The sorting methods can be combined in prioritized order::

  $ echo "$original" | penman --rearrange=attributes-first,alphanumeric
  (c / chase-01
     :polarity -
     :ARG0 (c2 / cat)
     :ARG1 (m / mouse))


Reconfiguring the Tree
''''''''''''''''''''''

In Penman, the *epigraph* is a side-channel of information that allows
it to configure (reconstruct) the original tree that led to a graph
representation. The :command:`--reconfigure` option first discards
this epigraphical information then configures the tree afresh, which
may lead to more drastic restructuring than just rearranging tree
branches. Like :command:`--rearrange`, it takes a sorting method as
its argument. Often it is helpful to use :command:`--rearrange` with
:command:`--reconfigure`, so the reconfigured tree still follows an
expected branch order::

  $ original="(s / sell-01 :ARG0 (i / i) :ARG1 (b / book :ARG1-of (r / read :ARG0 i)))"
  $ echo "$original" | penman
  (s / sell-01
   :ARG0 (i / i)
   :ARG1 (b / book
            :ARG1-of (r / read
                        :ARG0 i)))
  $ echo "$original" | penman --reconfigure=random --rearrange=alphanumeric
  (s / sell-01
     :ARG0 (i / i
              :ARG0-of (r / read
                          :ARG1 (b / book)))
     :ARG1 b)

Note that :command:`--reconfigure` does not change which variable is
the graph's top. This is because the resulting graph should encode the
same information, and the top node is treated specially. For example,
in AMR it is considered the *focused* node. A reconfigured graph will
return a perfect score with the original using a metric like smatch.


Normalizations
''''''''''''''

The remaining options are normalizations that may alter the content of
the graph. The :command:`--canonicalize-roles` option will replace
roles that the model defines as equivalent, such as ``:domain-of`` and
``:mod`` in AMR::

  $ echo "(c / chapter :domain-of 7)" | penman --amr --canonicalize-roles
  (c / chapter
     :mod 7)

Penman can handle relations that are over-inverted one time, but does
not check further than that. The :command:`--canonicalize-roles`
option will try harder to resolve over-inversions. For this
functionality, a model is not strictly necessary unless the
over-inverted role itself needs to be canonicalized::

  $ echo "(b / bark-01 :ARG0-of-of (d / dog))" | penman
  (b / bark-01
     :ARG0 (d / dog))
  $ echo "(b / bark-01 :ARG0-of-of-of-of (d / dog))" | penman
  (b / bark-01
     :ARG0-of-of (d / dog))
  $ echo "(b / bark-01 :ARG0-of-of-of-of (d / dog))" | penman --canonicalize-roles
  (b / bark-01
     :ARG0 (d / dog))

The :command:`--reify-edges` option converts edges into nodes for
edges that have a reification defined in the model::

  $ echo "(c / chapter :mod 7)" | penman --amr --reify-edges
  (c / chapter
     :ARG1-of (_ / have-mod-91
                 :ARG2 7))

The ``_`` (``_2``, etc.) variables indicate which have been
reified. Combine with :command:`--make-variables` to use standard
variable names (e.g., ``h`` in this example). The
:command:`--dereify-edges` is the reverse of
:command:`--reify-edges`::

  $ echo "(c / chapter :mod 7)" | penman --amr --reify-edges | penman --amr --dereify-edges
  (c / chapter
     :mod 7)


The :command:`--reify-attributes` option reifies attribute relations
(those where the value is a constant) so the constant value becomes
the concept of a new node::

  $ echo "(c / chapter :mod 7)" | penman --amr --reify-attributes
  (c / chapter
     :mod (_ / 7))


Finally, the :command:`--indicate-branches` option inserts relations
that hint at the original tree structure. This can be useful if a tool
that produces PENMAN graphs, like an AMR parser, wants to use a tool
like smatch to compare its output to gold trees and not just gold
graphs.
