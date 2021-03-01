
penman.models.amr
=================

.. automodule:: penman.models.amr

.. autodata:: model

Roles
-----

.. code:: json

   {
       ":ARG[0-9]":            {"type": "frame"},
       ":accompanier":         {"type": "general"},
       ":age":                 {"type": "general"},
       ":beneficiary":         {"type": "general"},
       ":cause":               {"type": "general", "shortcut": true},
       ":concession":          {"type": "general"},
       ":condition":           {"type": "general"},
       ":consist-of":          {"type": "general"},
       ":cost":                {"type": "general", "shortcut": true},
       ":degree":              {"type": "general"},
       ":destination":         {"type": "general"},
       ":direction":           {"type": "general"},
       ":domain":              {"type": "general"},
       ":duration":            {"type": "general"},
       ":employed-by":         {"type": "general", "shortcut": true},
       ":example":             {"type": "general"},
       ":extent":              {"type": "general"},
       ":frequency":           {"type": "general"},
       ":instrument":          {"type": "general"},
       ":li":                  {"type": "general"},
       ":location":            {"type": "general"},
       ":manner":              {"type": "general"},
       ":meaning":             {"type": "general", "shortcut": true},
       ":medium":              {"type": "general"},
       ":mod":                 {"type": "general"},
       ":mode":                {"type": "general"},
       ":name":                {"type": "general"},
       ":ord":                 {"type": "general"},
       ":part":                {"type": "general"},
       ":path":                {"type": "general"},
       ":polarity":            {"type": "general"},
       ":polite":              {"type": "general"},
       ":poss":                {"type": "general"},
       ":purpose":             {"type": "general"},
       ":role":                {"type": "general", "shortcut": true},
       ":source":              {"type": "general"},
       ":subevent":            {"type": "general"},
       ":subset":              {"type": "general", "shortcut": true},
       ":superset":            {"type": "general", "shortcut": true},
       ":time":                {"type": "general"},
       ":topic":               {"type": "general"},
       ":value":               {"type": "general"},
       ":quant":               {"type": "quantity"},
       ":unit":                {"type": "quantity"},
       ":scale":               {"type": "quantity"},
       ":day":                 {"type": "date"},
       ":month":               {"type": "date"},
       ":year":                {"type": "date"},
       ":weekday":             {"type": "date"},
       ":timezone":            {"type": "date"},
       ":quarter":             {"type": "date"},
       ":dayperiod":           {"type": "date"},
       ":season":              {"type": "date"},
       ":year2":               {"type": "date"},
       ":decade":              {"type": "date"},
       ":century":             {"type": "date"},
       ":calendar":            {"type": "date"},
       ":era":                 {"type": "date"},
       ":op[0-9]+":            {"type": "op"},
       ":snt[0-9]+":           {"type": "snt"},
       ":prep-against":        {"type": "preposition"},
       ":prep-along-with":     {"type": "preposition"},
       ":prep-amid":           {"type": "preposition"},
       ":prep-among":          {"type": "preposition"},
       ":prep-as":             {"type": "preposition"},
       ":prep-at":             {"type": "preposition"},
       ":prep-by":             {"type": "preposition"},
       ":prep-for":            {"type": "preposition"},
       ":prep-from":           {"type": "preposition"},
       ":prep-in":             {"type": "preposition"},
       ":prep-in-addition-to": {"type": "preposition"},
       ":prep-into":           {"type": "preposition"},
       ":prep-on":             {"type": "preposition"},
       ":prep-on-behalf-of":   {"type": "preposition"},
       ":prep-out-of":         {"type": "preposition"},
       ":prep-to":             {"type": "preposition"},
       ":prep-toward":         {"type": "preposition"},
       ":prep-under":          {"type": "preposition"},
       ":prep-with":           {"type": "preposition"},
       ":prep-without":        {"type": "preposition"},
       ":conj-as-if":          {"type": "conjunction"}
       ":wiki":                {"type": "wiki"},
       ":range":               {"type": "ordinal"},
   }


Role Normalizations
-------------------

.. code:: json

   {
       ":mod-of":    ":domain",
       ":domain-of": ":mod"
   }


Reifications
------------

.. code:: json

   [
       [":accompanier", "accompany-01",        ":ARG0", ":ARG1"],
       [":age",         "age-01",              ":ARG1", ":ARG2"],
       [":beneficiary", "benefit-01",          ":ARG0", ":ARG1"],
       [":beneficiary", "receive-01",          ":ARG2", ":ARG0"],
       [":cause",       "cause-01",            ":ARG1", ":ARG0"],
       [":concession",  "have-concession-91",  ":ARG1", ":ARG2"],
       [":condition",   "have-condition-91",   ":ARG1", ":ARG2"],
       [":cost",        "cost-01",             ":ARG1", ":ARG2"],
       [":degree",      "have-degree-92",      ":ARG1", ":ARG2"],
       [":destination", "be-destined-for-91",  ":ARG1", ":ARG2"],
       [":duration",    "last-01",             ":ARG1", ":ARG2"],
       [":employed-by", "have-org-role-91",    ":ARG0", ":ARG1"],
       [":example",     "exemplify-01",        ":ARG0", ":ARG1"],
       [":extent",      "have-extent-91",      ":ARG1", ":ARG2"],
       [":frequency",   "have-frequency-91",   ":ARG1", ":ARG2"],
       [":instrument",  "have-instrument-91",  ":ARG1", ":ARG2"],
       [":li",          "have-li-91",          ":ARG1", ":ARG2"],
       [":location",    "be-located-at-91",    ":ARG1", ":ARG2"],
       [":manner",      "have-manner-91",      ":ARG1", ":ARG2"],
       [":meaning",     "mean-01",             ":ARG1", ":ARG2"],
       [":mod",         "have-mod-91",         ":ARG1", ":ARG2"],
       [":name",        "have-name-91",        ":ARG1", ":ARG2"],
       [":ord",         "have-ord-91",         ":ARG1", ":ARG2"],
       [":part",        "have-part-91",        ":ARG1", ":ARG2"],
       [":polarity",    "have-polarity-91",    ":ARG1", ":ARG2"],
       [":poss",        "own-01",              ":ARG0", ":ARG1"],
       [":poss",        "have-03",             ":ARG0", ":ARG1"],
       [":purpose",     "have-purpose-91",     ":ARG1", ":ARG2"],
       [":role",        "have-org-role-91",    ":ARG0", ":ARG2"],
       [":source",      "be-from-91",          ":ARG1", ":ARG2"],
       [":subevent",    "have-subevent-91",    ":ARG1", ":ARG2"],
       [":subset",      "include-91",          ":ARG2", ":ARG1"],
       [":superset",    "include-91",          ":ARG1", ":ARG2"],
       [":time",        "be-temporally-at-91", ":ARG1", ":ARG2"],
       [":topic",       "concern-02",          ":ARG0", ":ARG1"],
       [":value",       "have-value-91",       ":ARG1", ":ARG2"],
       [":quant",       "have-quant-91",       ":ARG1", ":ARG2"]
   ]
