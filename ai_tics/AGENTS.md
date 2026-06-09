---
type: constitution
module: ai_tics
aliases: ["ai-tics — constitution", "ai_tics — constitution"]
tags: [company, constitution, ai-tics, registry, cognition, corpus, fingerprint]
governs: [P1, M4]
relates-to: ["[[Company Map]]", "[[runtime — constitution]]", "[[projections — constitution]]", "[[mark-types — constitution]]"]
status: living
---

# ai_tics/ — module constitution

**Is:** the **file-discovered AI-TIC registry** (Cognition Engine NEWMOD · M4 · P1). An **AI-tic** is a
declared, CATALOGUED generic-AI fingerprint — a recurring tell of machine-generated (not Tim-meaning)
content. The fingerprint pass (M4, the inversion) matches the coined-vocab projection against THIS
registry → `ai-fingerprint` marks (`mark_types/ai_fingerprint`, direction `subtract`):
generic+recurring = a tic to SUBTRACT (denoising = surfacing, opposite direction); idiosyncratic+
recurring = gold. The catalogue is EXTENSIBLE — Tim's own NAMED frustrations seed it. AI-tics are a
registry **like anything else**: an `ai_tics/` dir, one self-registering `ai_tics/<id>.py` per tic —
**exactly mirroring roles/skills/projections/node-types**. Adding a tic = adding a FILE; a removed file
un-registers on `rediscover`.

**Why file-discovered, not a python dict (PART 4.3):** **add-a-row = a FILE, no code edit.** The tic
catalogue MUST be directory-discovered, file-per-entry + create_*-authorable, NOT `AI_TICS = {...}`.

**Guarantees:** an AI-tic is **one self-contained declaration** — a module-level `AI_TIC` dict over the
schema `{id · markers · label · desc}`. Required: `id` (MUST equal the file stem) · `markers` (a
NON-EMPTY list of non-empty strings — the cues the fingerprint pass matches; the catalogue, not a code
branch). `label`/`desc` optional. A malformed entry FAILS LOUD at discovery; a non-`AI_TIC`/`_`-file is
skipped.

**The AI-tics (the live set — the drift home; `tests/ai_tics_acceptance.py` asserts each is reflected here):**
*(seeded from Tim's NAMED frustrations — the generic-AI tells to subtract)*
- **`framework_imposition`** (framework-imposition) — imposing a generic framework/terminology over the
  content's native shape (Tim ACTIVELY rejects standard frameworks).
- **`versioning`** — v2/round-N/dated copies instead of updating canonical in place (named frustration: no-versioning).
- **`false_finality`** — declaring done/fixed/complete without proof (named frustration: verify-before-claiming).
- **`silent_fallback`** — routing around a problem / swallowing an error instead of failing loud
  (named frustration: no-silent-failures, make-each-thing-work).
- **`agent_arch`** — defaulting to agent-architecture where the work is content/dataflow (named distinction:
  not-agent-architecture-by-default).
- **`closure_form`** — closure-form writing (summarized/finished, expansion-ratio<1) that kills institutional
  memory (named frustration: open-future-writing).
- **`mvp`** (MVP) — MVP/impact-prioritization/scope-cutting (named frustration: no-MVP, all-or-nothing).

**The floor:** an AI-tic is DECLARED DATA — a catalogue entry, not an action. Reading is a READ
(`all_markers`/`as_records`, never `resolve`). The fingerprint pass appends a finding (a mark), never
resolves — the floor holds.

**Where new things go:** a new tic = a new file `ai_tics/<id>.py` declaring its `AI_TIC` dict. **Update
THIS file** when you add one — the acceptance fails loud otherwise.

**To extend:** drop an `ai_tics/<id>.py` → it self-registers → the fingerprint mark-pass reads it via
`as_records()` / `all_markers()` (registry-is-truth). To author one from the agent face: a future
`create_ai_tic` (declarative-direct) reuses THIS registry's `_build_tic` gate; long-term home
`runtime/authoring.py` + `Suite.create_ai_tic` — **flagged as a seam (the WIRING — incl. the fingerprint
mark-pass reading the catalogue — is a SEPARATE coordinated pass, NOT built in this lane)**.

**Seam:** discovered by `runtime/ai_tics.py:AiTicRegistry` (mirrors `ProjectionRegistry`/`RoleRegistry`/
`NodeRegistry`). Consumers: `all_markers()` (the flat cue set) · `as_records()` (cognition_info + the
fingerprint pass catalogue). All pure READS — the floor.

**Never:** hardcode a tic in a literal · fork a second registry pattern · let a tic RESOLVE/DISPATCH ·
ship one without reflecting it here.

## Relates to
- **Discovered by** [[runtime — constitution]] (`runtime/ai_tics.py`, mirroring `runtime/projections.py`).
- **Feeds** the fingerprint pass (M4) with [[mark-types — constitution]]'s `ai_fingerprint` (direction subtract).

## Read next
[[Company Map]] · [[mark-types — constitution]] · `build-prep/cognition-engine/COMPLETION-CRITERIA.md` (GROUP M/P).
