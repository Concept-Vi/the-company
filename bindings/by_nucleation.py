"""TYPE-NUCLEATION lens — the 20/80 water-law (Tim Geldard's growth law; all derived work attributed to him).

radius_from='nucleation' types the items of a content store against a REGISTRY OF TYPES (the scale-pyramid
centroids of `types_space` at `rung`) and reads where the registry under-covers its content: what FITS sits
INSIDE the square (within a type's own empirical extent), what does NOT fit piles up OUTSIDE, and a DISTINCT
coherent pile that accumulates past the birth threshold is a CANDIDATE NEW TYPE born outside the box. The
inverse — a registered type whose membership thins — is a (context-dependent) dissolution candidate. There is
NO objective and NO purpose: it is a pure read of the registry↔content fit. The laws underneath
(accumulate→birth, thin→candidacy) are the invariant; the thresholds bend to the situation.

Every axis is a VARIABLE, registry-true and drivable per request, so the law works on ANY registry/store and
keeps working as the Company grows new types/stores (universal law, not a fixed wiring):
  ?types_space=  the registry of types        ?rung=  how fine that registry is
  ?space=        the content store typed       ?dial=  the 20/80 BIRTH threshold (moves born/forming, not the
                                                       inside/outside membership split)

The default is a CROSS-INSTANCE pair (types from `topics`, items from `repo`) so the misfit is genuine and
NON-circular (the type centroids are not means of the items being typed) and more than one data store is
exercised — cross-store content mostly does NOT fit the registry, so the honest live picture is an empty-ish
square + the candidate new types forming outside it ("none of this fits your registry — here are the types it
wants"). Same-store (?space=topics) is the other honest regime: a populated square + the natural outliers.

HONEST BOUNDARY: this is SEMANTIC nucleation over the EMBEDDED data stores; the symbolic pile-outside for a
code-declared type-registry (events naming no registered row) is Group 10's '—' remainder — distinct-type
clustering is scoped to where vectors exist."""

BINDING = {
    "id": "by_nucleation",
    "label": "Type-nucleation — where new types are born",
    "angle_from": "nucleation",      # sectors = the registry's types + one outer ZONE per candidate (resolved)
    "radius_from": "nucleation",
    "order_by": "count",
    "types_space": "topics",         # the REGISTRY OF TYPES (scale-pyramid centroids at the rung)
    "rung": 8,                       # how fine the registry of types is (drivable ?rung=)
    "space": "repo",                 # the CONTENT store typed against the registry (cross-instance: non-circular)
    "dial": 0.2,                     # the 20/80 BIRTH threshold (surfaced + drivable ?dial=)
}
