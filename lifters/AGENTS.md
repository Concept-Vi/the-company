---
type: constitution
register: prescriptive
module: lifters
aliases: ["lifters — constitution"]
tags: [company, constitution, lifters, registry, cognition, corpus]
governs: [P1, K2]
relates-to: ["[[Company Map]]", "[[runtime — constitution]]", "[[projections — constitution]]"]
status: living
---

# lifters/ — module constitution

**Is:** the **file-discovered LIFTER registry** (Cognition Engine NEWMOD · P1 · K2). A **lifter** is a
declared **deterministic EXTRACTOR** — it produces a `produced_by:"code"` projection (frontmatter /
links / blocks) WITHOUT a model call. The corpus capture (K2) renders the `model` projections via a
capture-role; the `code` projections are produced by these lifters. So a lifter is the CODE half of the
projection split — a `projections/<id>.py` with `produced_by:"code"` (e.g. the seed `lineage` lens) is
EXTRACTED by a matching lifter here. Lifters are a registry **like anything else** (registry-is-truth):
a `lifters/` dir, one self-registering `lifters/<id>.py` per extractor — **exactly mirroring how
roles + skills + projections + node-types self-register**. Adding a lifter = adding a FILE; it
self-registers; a removed file un-registers on `rediscover`.

**Why file-discovered, not a python dict (PART 4.3):** the real test of "registry-is-truth" is
**add-a-row = a FILE, no code edit.** So the lifter set MUST be directory-discovered, file-per-entry +
create_*-authorable, NOT `LIFTERS = {...}`.

**Guarantees:** a lifter is **one self-contained declaration** — a module-level `LIFTER` dict over the
schema `{id · extract · produces · desc}`. Required: `id` (MUST equal the file stem) · `extract` (a
callable `(text, *, meta=None) -> value` — the deterministic extractor; a PARSE is a READ, the floor
holds). `produces`/`desc` optional. A malformed entry FAILS LOUD at discovery; a non-`LIFTER`/`_`-file
is skipped.

**The lifters (the live set — the drift home; `tests/lifters_acceptance.py` asserts each is reflected here):**
- **`frontmatter`** — extract the leading YAML frontmatter block as a dict (structural).
- **`links`** — extract the outbound links (`[[wikilinks]]` + `[md](targets)`) as a list (structural).
- **`blocks`** — extract the heading-block structure (`{level, heading}` per `#`-heading) as a list (structural).

**The floor (C9.2):** a lifter EXTRACT is a READ/parse — no resolve/dispatch. The registry reads
(`for_projection`/`as_records`) are pure reads.

**Where new things go:** a new extractor = a new file `lifters/<id>.py` declaring its `LIFTER` dict
(its `id` MUST equal the file name). **Update THIS file** (the drift home) when you add one —
`tests/lifters_acceptance.py` fails loud if a discovered lifter isn't reflected here.

**To extend:** drop a `lifters/<id>.py` → it self-registers → the corpus capture (K2) finds it via
`for_projection(<pid>)` to produce the matching `produced_by:"code"` projection. To author one from the
agent face: a future `create_lifter` (the declarative-direct create, like `create_skill`/
`create_projection`) reuses THIS registry's `_build_lifter` gate in a tempdir; its long-term home is
`render_lifter_source` in `runtime/authoring.py` + a `Suite.create_lifter` method — **flagged as a seam
(the WIRING is a SEPARATE coordinated pass, NOT built in this lane)**. An executable-code lifter author
path is correctly GATED (like node-types).

**Seam:** discovered by `runtime/lifters.py:LifterRegistry` (mirrors
`runtime/projections.py:ProjectionRegistry` / `runtime/roles.py:RoleRegistry` /
`runtime/registry.py:NodeRegistry` — reuse-don't-parallel, the ONE registry mechanism). The consumers
read over the discovered set: `for_projection(pid)` (K2 routing) · `as_records()` (the cognition_info
projection — the callable rendered as its qualname). All pure READS — the floor.

**Never:** hardcode an extractor in a literal list/dict (the registry path, never the literal) · fork a
second registry pattern · let a lifter RESOLVE/DISPATCH (it EXTRACTS — a READ) · ship a lifter without
reflecting it in this drift home.

## Relates to
- **Discovered by** [[runtime — constitution]] (`runtime/lifters.py`, mirroring `runtime/projections.py`).
- **Feeds** the corpus pillar: the `produced_by:"code"` projections (`projections/lineage.py` and future
  structural lenses), the corpus-record (`runtime/corpus.py`, K2).

## Read next
[[Company Map]] · [[projections — constitution]] (the sibling registry whose `code` lenses these feed) ·
`build-prep/cognition-engine/COMPLETION-CRITERIA.md` (GROUP K/P).
