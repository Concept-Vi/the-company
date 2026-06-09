---
type: constitution
module: forms
aliases: ["forms — constitution"]
tags: [company, constitution, forms, registry, cognition, corpus, effort-routing]
governs: [P1]
relates-to: ["[[Company Map]]", "[[runtime — constitution]]", "[[projections — constitution]]", "[[generation-policies — constitution]]"]
status: living
---

# forms/ — module constitution

**Is:** the **file-discovered FORM registry** (Cognition Engine NEWMOD · P1 · effort-routing). A **form**
is a declared FILE-SHAPE → ROUTING rule: it recognises a kind of corpus unit by its shape (a log · a
registry/index · a decision note · free prose) and routes it to an EFFORT BAND — the restored
**effort-routing-by-form** discipline: ~half a corpus is bookkeeping, DON'T burn full capture depth on
logs. The capture pass reads a unit's form to TIER the work (`legibility` the cheap broad pass · `deep`
the heavier pass · `skip`) and may pick a generation-policy by form. "Effort-routing by form" made DATA,
not a hardcoded if-ladder. Forms are a registry **like anything else**: a `forms/` dir, one
self-registering `forms/<id>.py` per shape — **exactly mirroring roles/skills/projections/node-types**.
Adding a form = adding a FILE; a removed file un-registers on `rediscover`.

**Why file-discovered, not a python dict (PART 4.3):** **add-a-row = a FILE, no code edit.** The
form→routing vocabulary MUST be directory-discovered, file-per-entry + create_*-authorable, NOT
`FORMS = {...}`.

**Guarantees:** a form is **one self-contained declaration** — a module-level `FORM` dict over the
schema `{id · match · stage · policy · fallthrough · desc}`. Required: `id` (MUST equal the file stem) ·
`match` (a callable `(text, *, meta=None) -> bool` — the deterministic shape recogniser; a match is a
READ) · `stage` (the effort band — open vocab DATA). `policy` (a generation-policy id this form selects)
/ `fallthrough` (bool — the catch-all, checked LAST) / `desc` optional. A malformed entry FAILS LOUD at
discovery; a non-`FORM`/`_`-file is skipped. `route()` FAILS LOUD if NO form matches (never a silently
un-routed unit) — so a `fallthrough` form is declared.

**The forms (the live set — the drift home; `tests/forms_acceptance.py` asserts each is reflected here):**
- **`log`** — match: timestamped lines / changelog|handoff|status header. stage `legibility`, policy
  `prose_default`. Bookkeeping — the cheap broad pass.
- **`registry`** — match: MoC/index/registry header or mostly-link lines. stage `legibility`, policy
  `prose_default`. Structure, not substance.
- **`decision`** — match: decision|decided|resolved|Dn header. stage `deep`, policy `capture_default`.
  High-substance (the spine) — the heavier deep pass. Exercises the `deep` band.
- **`prose`** — `fallthrough: True`, matches any non-empty unit. stage `deep`, policy `capture_default`.
  The catch-all (checked LAST via the `fallthrough` flag — DATA-driven ordering, no hardcoded form name).

**The floor:** a form is DECLARED DATA + a deterministic recogniser (a READ). Reading the registry /
running a `match` is a READ (the method is `route`/`as_records`, never `resolve`). The router PICKS an
effort band; it never resolves/dispatches — the floor holds.

**Where new things go:** a new shape→routing rule = a new file `forms/<id>.py` declaring its `FORM`
dict. **Update THIS file** when you add one — the acceptance fails loud otherwise.

**To extend:** drop a `forms/<id>.py` → it self-registers → the capture lane reads `route()` to tier the
work by shape. To author one from the agent face: a future `create_form` (declarative-direct) reuses THIS
registry's `_build_form` gate; long-term home `runtime/authoring.py` + `Suite.create_form` — **flagged as
a seam (the WIRING — incl. the capture lane reading `route()` — is a SEPARATE coordinated pass, NOT built
in this lane)**. A `match` callable author path is correctly GATED (like node-types — it is code).

**Seam:** discovered by `runtime/forms.py:FormRegistry` (mirrors `ProjectionRegistry`/`RoleRegistry`/
`NodeRegistry`). Consumers: `route(text, meta=)` (the effort-routing read — narrow forms first, fallthrough
last) · `as_records()` (cognition_info — the callable rendered as its qualname). All pure READS — the floor.

**Never:** hardcode a shape→routing rule in a literal if-ladder (this module IS the no-static rule for
effort-routing) · fork a second registry pattern · let a form RESOLVE/DISPATCH (it recognises — a READ) ·
ship a form without reflecting it here · leave no fallthrough (route() fails loud on an un-routed unit).

## Relates to
- **Discovered by** [[runtime — constitution]] (`runtime/forms.py`, mirroring `runtime/projections.py`).
- **Selects** [[generation-policies — constitution]] regimes by shape (the `policy` field).
- **Read by** the corpus capture lane (K2) to tier the work — a SEPARATE coordinated wiring pass.

## Read next
[[Company Map]] · [[generation-policies — constitution]] · `build-prep/cognition-engine/COMPLETION-CRITERIA.md` (PART 3/4).
