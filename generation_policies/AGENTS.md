---
type: constitution
module: generation_policies
aliases: ["generation-policies — constitution", "generation_policies — constitution"]
tags: [company, constitution, generation-policies, registry, cognition, corpus]
governs: [P1, O2]
relates-to: ["[[Company Map]]", "[[runtime — constitution]]", "[[projections — constitution]]"]
status: living
---

# generation_policies/ — module constitution

**Is:** the **file-discovered GENERATION-POLICY registry** (Cognition Engine NEWMOD · O2 · P1). A
**generation-policy** is the declared, per-content GENERATION REGIME a `run_role` call uses — **NOT
static knobs in code.** This is the registry the law "NOTHING static" is made CONCRETE on: the
repetition_penalty regime is a registry ROW with a **ladder as DATA** + a **diff-against-source flag**,
**add-a-row = a FILE**. Generation-policies are a registry **like anything else**: a
`generation_policies/` dir, one self-registering `generation_policies/<id>.py` per regime — **exactly
mirroring roles/skills/projections/node-types**. Adding a regime = adding a FILE; a removed file
un-registers on `rediscover`.

**Why this registry exists (the generation pathology):** greedy temp0 + grammar-constrained long arrays
→ a degenerate repetition loop (~20% of real files; input-size does NOT predict it; `frequency_penalty`
is WRONG — it penalises JSON structure). The cure is a **repetition_penalty LADDER**: `1.1` default →
`1.2` on `finish=length` → **fail-loud `degenerate-loop`** (ladder exhausted). It is declared per-content
as DATA, NEVER a code constant. Tim-decision lean: rep_penalty can silently under-capture LEGITIMATE
enumeration → a `diff_against_source` check, NEVER a silent penalty.

**Why file-discovered, not a python dict (PART 4.3):** **add-a-row = a FILE, no code edit** — and NOT
`REP_PENALTY = 1.1` in code. The regime MUST be directory-discovered, file-per-entry + create_*-authorable.

**Guarantees:** a generation-policy is **one self-contained declaration** — a module-level
`GENERATION_POLICY` dict over the schema `{id · rep_penalty_ladder · diff_against_source · json_schema ·
temperature · budget · desc}`. Required: `id` (MUST equal the file stem) · `rep_penalty_ladder` (a
NON-EMPTY ASCENDING list of floats — default → escalate-on-length → exhausted=fail-loud) ·
`diff_against_source` (bool — the never-silently-lossy guard). `json_schema`/`temperature`/`budget`/`desc`
optional. A malformed entry FAILS LOUD at discovery; a non-`GENERATION_POLICY`/`_`-file is skipped.

**The generation-policies (the live set — the drift home; `tests/generation_policies_acceptance.py` asserts each is reflected here):**
- **`capture_default`** — the corpus-capture regime: `rep_penalty_ladder: [1.1, 1.2]` (default → escalate →
  fail-loud degenerate-loop), `diff_against_source: True` (never a silent penalty on enumeration),
  `json_schema: True`, `temperature: 0.0` (greedy — the loop-trigger surface this ladder cures). THE entry
  that proves "NOTHING static".
- **`prose_default`** — the free-prose regime (reduce/consult): `rep_penalty_ladder: [1.1]` (a single
  fixed rung — prose is not the grammar-constrained loop surface), `diff_against_source: False` (prose is
  not enumerative), `temperature: 0.3`. Proves the ladder need not be multi-rung + the flags vary per regime.

**The floor:** a generation-policy is DECLARED DATA — a regime, not an action. Reading is a READ
(`policy_for`/`next_rep_penalty`/`as_records`, **never `resolve`** — deliberately keeping this module
clean of the C9.2 forbidden `.resolve(` token so it stays floor-safe if/when enrolled in COG_SOURCES).

**Where new things go:** a new regime = a new file `generation_policies/<id>.py` declaring its
`GENERATION_POLICY` dict. **Update THIS file** when you add one — the acceptance fails loud otherwise.

**To extend:** drop a `generation_policies/<id>.py` → it self-registers → `run_role` reads the selected
regime's ladder. To author one from the agent face: a future `create_generation_policy` (declarative-
direct) reuses THIS registry's `_build_policy` gate; long-term home `runtime/authoring.py` +
`Suite.create_generation_policy` — **flagged as a seam (the WIRING — incl. `run_role` reading the ladder
— is a SEPARATE coordinated pass, NOT built in this lane)**.

**Seam:** discovered by `runtime/generation_policies.py:GenerationPolicyRegistry` (mirrors
`ProjectionRegistry`/`RoleRegistry`/`NodeRegistry`). Consumers: `policy_for(id)` / `next_rep_penalty()`
(the run_role read) · `as_records()` (cognition_info). All pure READS — the floor.

**Never:** hardcode a rep_penalty/json_schema/temperature as a code CONSTANT (this module IS the
no-static rule — the registry path, never the literal) · fork a second registry pattern · use a
`.resolve(`-named method here (floor token) · ship a regime without reflecting it here.

## Relates to
- **Discovered by** [[runtime — constitution]] (`runtime/generation_policies.py`, mirroring `runtime/projections.py`).
- **Read by** the ENGINE lane's `run_role` generation-robustness change (the rep_penalty ladder) — a
  SEPARATE coordinated wiring pass.

## Read next
[[Company Map]] · [[projections — constitution]] · `build-prep/cognition-engine/COMPLETION-CRITERIA.md` (GROUP O/P).
