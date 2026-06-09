---
type: constitution
module: mark_types
aliases: ["mark-types — constitution", "mark_types — constitution"]
tags: [company, constitution, mark-types, registry, cognition, corpus, marks]
governs: [P1, M1, M4]
relates-to: ["[[Company Map]]", "[[runtime — constitution]]", "[[projections — constitution]]"]
status: living
---

# mark_types/ — module constitution

**Is:** the **file-discovered MARK-TYPE registry** (Cognition Engine NEWMOD · M1 · M4 · P1). A **mark**
is the disposition a mark-pass writes over a corpus unit (Group M): the coherence finding store IS the
marks layer (same shape: `target / mark_type / value / confidence / source_pass / evidence / status`).
A **mark-type** is the declared VOCABULARY of `mark_type` — one named KIND of disposition a pass may
write. A mark-pass = a `run_role`/`run_reduce` pass that `append_finding`s with a `mark_type` DRAWN FROM
this registry. Mark-types are a registry **like anything else**: a `mark_types/` dir, one
self-registering `mark_types/<id>.py` per kind — **exactly mirroring roles/skills/projections/node-types**.
Adding a mark-type = adding a FILE; a removed file un-registers on `rediscover`.

**Why file-discovered, not a python dict (PART 4.3):** **add-a-row = a FILE, no code edit.** The
mark-type vocabulary MUST be directory-discovered, file-per-entry + create_*-authorable, NOT
`MARK_TYPES = {...}`.

**Guarantees:** a mark-type is **one self-contained declaration** — a module-level `MARK_TYPE` dict over
the schema `{id · value_shape · direction · desc}`. Required: `id` (MUST equal the file stem) ·
`value_shape` (how the mark's value is read — score/label/bool/span/free; open vocab DATA).
`direction` (`surface`=positive signal | `subtract`=noise to subtract, the inversion — fingerprint-
subtraction; defaults to `surface`) + `desc` optional. A malformed entry FAILS LOUD at discovery; a
non-`MARK_TYPE`/`_`-file is skipped.

**The mark-types (the live set — the drift home; `tests/mark_types_acceptance.py` asserts each is reflected here):**
- **`gold_likelihood`** — score · **surface**. Likelihood a unit is gold (MEANING, not surface artifact);
  the PROFILE is a READ over findings+evidence (never a stored opaque score — the operator sees-why, can overrule).
- **`ai_fingerprint`** — label · **subtract**. A matched AI-tic (generic+recurring) to subtract — denoising
  is surfacing, OPPOSITE direction. The seed that EXERCISES the surface-vs-subtract split.
- **`contradiction`** — span · **surface**. This unit contradicts another (a tension surfaced for review;
  render-not-judge — the operator decides).

**The floor + render-not-judge:** a mark-type is DECLARED DATA — a vocabulary, not an action. Reading is
a READ (`subtractive`/`as_records`, never `resolve`). A mark DESCRIBES a disposition; judgement of
truth/quality is a later reduce pass, and the operator can overrule. A mark-pass appends a finding
(telemetry/index), never resolves — the floor holds.

**Where new things go:** a new disposition kind = a new file `mark_types/<id>.py` declaring its
`MARK_TYPE` dict. **Update THIS file** when you add one — `tests/mark_types_acceptance.py` fails loud
if a discovered mark-type isn't reflected here.

**To extend:** drop a `mark_types/<id>.py` → it self-registers → a mark-pass may stamp it (drawn from
`as_records()` — registry-is-truth). To author one from the agent face: a future `create_mark_type`
(declarative-direct, like `create_projection`) reuses THIS registry's `_build_mark_type` gate; long-term
home `runtime/authoring.py` + `Suite.create_mark_type` — **flagged as a seam (the WIRING is a SEPARATE
coordinated pass, NOT built in this lane)**.

**Seam:** discovered by `runtime/mark_types.py:MarkTypeRegistry` (mirrors `ProjectionRegistry`/
`RoleRegistry`/`NodeRegistry` — the ONE registry mechanism). Consumers: `subtractive()` (the inversion
set) · `as_records()` (cognition_info + the mark-pass vocabulary). All pure READS — the floor.

**Never:** hardcode a mark-type in a literal · fork a second registry pattern · let a mark-type JUDGE
or a mark-pass RESOLVE (render-not-judge; the floor) · ship one without reflecting it here.

## Relates to
- **Discovered by** [[runtime — constitution]] (`runtime/mark_types.py`, mirroring `runtime/projections.py`).
- **Feeds** Group M: the marks layer (the coherence finding store), the gold-likelihood profile, the
  fingerprint pass (with the `ai_tics` registry).

## Read next
[[Company Map]] · [[projections — constitution]] · `build-prep/cognition-engine/COMPLETION-CRITERIA.md` (GROUP M/P).
