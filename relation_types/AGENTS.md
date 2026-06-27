---
type: constitution
register: prescriptive
module: relation_types
aliases: ["relation-types — constitution", "relation_types — constitution"]
tags: [company, constitution, relation-types, registry, cognition, corpus]
governs: [P1, L3]
relates-to: ["[[Company Map]]", "[[runtime — constitution]]", "[[projections — constitution]]"]
status: living
---

# relation_types/ — module constitution

**Is:** the **file-discovered RELATION-TYPE registry** (Cognition Engine NEWMOD · L3 · P1). A
**relation-type** is a declared KIND of typed/directional edge between two corpus units — the vocabulary
`find_relations` (L3) composes/labels its discovered relations with. The cross-level query
`find_relations(item, near_space, far_space)` = `query_index(near)` ∩ ¬`query_index(far)` (the
inversion-finder); the relation it MARKS is one of these declared types, with a DIRECTION (some directed,
some symmetric). Relation-types are a registry **like anything else**: a `relation_types/` dir, one
self-registering `relation_types/<id>.py` per kind — **exactly mirroring roles/skills/projections/
node-types**. Adding an edge kind = adding a FILE; a removed file un-registers on `rediscover`.

**Why file-discovered, not a python dict (PART 4.3):** **add-a-row = a FILE, no code edit.** The edge
vocabulary MUST be directory-discovered, file-per-entry + create_*-authorable, NOT `RELATION_TYPES = {...}`.

**Guarantees:** a relation-type is **one self-contained declaration** — a module-level `RELATION_TYPE`
dict over the schema `{id · directed · inverse · near · far · label · desc}`. Required: `id` (MUST equal
the file stem — a python identifier, so a hyphenated edge name lives in `label`) · `directed` (bool —
directed A→B vs symmetric A↔B; decides whether find_relations records one end or both). `inverse`/`near`/
`far`/`label`/`desc` optional (`near`/`far` name the projection spaces the inversion-finder set-operates
over). A malformed entry FAILS LOUD at discovery; a non-`RELATION_TYPE`/`_`-file is skipped.

**The relation-types (the live set — the drift home; `tests/relation_types_acceptance.py` asserts each is reflected here):**
- **`principle_beneath`** (label `principle-beneath`) — DIRECTED · near=`principles`. A expresses the
  principle beneath B (the principle under the instance; A→B).
- **`fragment_of`** (label `fragment-of`) — DIRECTED · inverse `has_fragment` · near=`topics`. A is a
  fragment of the whole B (part→whole). Exercises the `inverse` field.
- **`contradicts`** — DIRECTED · near=`principles` · far=`principles`. A contradicts B (a tension surfaced
  for review; render-not-judge — the operator decides). The relation the `contradiction` mark-type stamps.
- **`sibling`** — SYMMETRIC (`directed: False`) · near=`topics`. A and B are siblings — same level, shared
  topic, neither beneath the other (A↔B). Exercises the symmetric branch.

**The floor + render-not-judge:** a relation-type is DECLARED DATA — a vocabulary, not an action.
Reading is a READ (`directed`/`symmetric`/`as_records`, never `resolve`). `find_relations` produces a
relation (a finding the operator reviews); a relation DESCRIBES, judgement is a later pass.

**Where new things go:** a new edge kind = a new file `relation_types/<id>.py` declaring its
`RELATION_TYPE` dict. **Update THIS file** when you add one — the acceptance fails loud otherwise.

**To extend:** drop a `relation_types/<id>.py` → it self-registers → `find_relations` labels its edges
from `as_records()` (registry-is-truth). To author one from the agent face: a future
`create_relation_type` (declarative-direct) reuses THIS registry's `_build_relation_type` gate; long-term
home `runtime/authoring.py` + `Suite.create_relation_type` — **flagged as a seam (the WIRING — incl.
`find_relations` labelling edges — is a SEPARATE coordinated pass, NOT built in this lane)**.

**Seam:** discovered by `runtime/relation_types.py:RelationTypeRegistry` (mirrors `ProjectionRegistry`/
`RoleRegistry`/`NodeRegistry`). Consumers: `directed()` / `symmetric()` (the find_relations branch) ·
`as_records()` (cognition_info). All pure READS — the floor.

**Never:** hardcode an edge kind in a literal · fork a second registry pattern · let a relation-type JUDGE
(render-not-judge) · ship one without reflecting it here.

## Relates to
- **Discovered by** [[runtime — constitution]] (`runtime/relation_types.py`, mirroring `runtime/projections.py`).
- **Read by** Group L's `find_relations` (the inversion-finder) — a SEPARATE coordinated wiring pass.
- **References** the projection SPACES (`projections/principles.py`, `topics.py`) it set-operates over.

## Read next
[[Company Map]] · [[projections — constitution]] · `build-prep/cognition-engine/COMPLETION-CRITERIA.md` (GROUP L/P).

## Agent-authored entries (auto-reflected)
- **`depends_on`** — agent-authored relation_type (created via the declarative-direct face). DEPENDENCY axis (substrate lift): this unit requires the target — a gate; the inverse reading is 'target unlocks this'
<!-- created live by the create face; one line per entry — keeps the
     drift-home acceptance green; refine the prose by integration. -->
- **`precedes`** — agent-authored relation_type (created via the declarative-direct face). SEQUENCE axis (substrate lift): this unit comes before the target in a declared order — stage/step/round; logical order, not the wall-clock 
