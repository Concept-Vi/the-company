---
type: constitution
module: projections
aliases: ["projections — constitution"]
tags: [company, constitution, projections, registry, cognition, corpus]
governs: [K1, P1]
relates-to: ["[[Company Map]]", "[[runtime — constitution]]", "[[roles — constitution]]", "[[skills — constitution]]"]
status: living
---

# projections/ — module constitution

**Is:** the **file-discovered PROJECTION registry** (Cognition Engine K1 / P1). A **projection** is a
declared **LENS** over a corpus unit — one named way to DESCRIBE a file/unit (what it IS, the topics it
covers, the principles it expresses, its claimed status, …). The lens set is the discovery vocabulary of
the corpus pillar: a `capture` role's `output_schema` is built FROM the `model` lenses; each `embeds:true`
lens becomes a vector SPACE (Group L); `find_relations(near_space, far_space)` set-operates over those
spaces (the inversion-finder). Projections are a registry **like anything else** (registry-is-truth): a
`projections/` dir, one self-registering `projections/<id>.py` per lens — **exactly mirroring how
roles + skills + node-types self-register** (`roles/`+`runtime/roles.py`; `skills/`+`runtime/skills.py`;
`nodes/`+`runtime/registry.py`). Adding a lens = adding a FILE; it self-registers and is queryable; a
removed file un-registers on `rediscover`.

**Why file-discovered, not a python dict (the adversary-verified BAR — COMPLETION-CRITERIA PART 4.3):**
the real test of "registry-is-truth" is **add-a-row = a FILE, no code edit.** `cognition_info` already
PROJECTS code-dicts (RULE_OPS/THOUGHT_SHAPES) — but projection ≠ dynamic; a dict still needs a source
edit to grow. So a projection registry MUST be directory-discovered, file-per-entry + create_*-authorable,
NOT `PROJECTIONS = {...}`. Dropping a `projections/<id>.py` makes that lens appear everywhere (the
capture-schema, the spaces, the selects) with ZERO code change.

**Guarantees:** a projection is **one self-contained declaration** — a module-level `PROJECTION` dict over
the schema `{id · level · produced_by · embeds · field · enum · desc · stage}`. Required:
`id` (MUST equal the file stem) · `level` (the abstraction band — open vocab) · `produced_by`
(`model`=a capture-role describes it | `code`=a lifter extracts it) · `embeds` (bool — does it become a
space). `field`/`enum`/`desc`/`stage` are optional. A malformed entry FAILS LOUD at discovery (never a
silent skip); a non-`PROJECTION`/`_`-file is skipped (mirroring the role/skill non-entry skip).

**The projections (the live set — the drift home; `tests/projections_acceptance.py` asserts each is reflected here):**
- **`what`** — content · model · no-embed · string. A <=15-word statement of what the file IS. The seed lens.
- **`topics`** — content · model · **embeds** · array. The subjects/areas it covers → the topics SPACE.
- **`repo`** — content · model · **embeds** · text. What a repo file IS (purpose + concepts) → the repo SPACE (COMPOSITION ① repo-exocortex; the repo_digest role produces it). The G15 unblock — ① needs an embeddable `repo` space to ingest into.
- **`principles`** — meaning · model · **embeds** · array. The underlying principles/intents it expresses
  (may be several) → the principle SPACE (the space M3 corroboration runs over cross-SESSION — which is
  why the corpus-record carries session/round/project lineage from the start).
- **`worldview`** — meaning · model · **embeds** · array. The stances/values it ASSUMES (often unstated)
  → the worldview SPACE.
- **`claimed_status`** — epistemic · model · no-embed · enum {decided·draft·aspirational·stub·unknown}.
  The file's OWN claimed state — the clearest **render-NOT-judge** lens (K3: render the claim, do NOT
  judge whether it is true; judgement is a later reduce pass).
- **`lineage`** — structural · **code** · no-embed. The first `produced_by:"code"` seed: a deterministic
  EXTRACTOR (the lifters registry, a later NEWMOD pass) produces it — EXCLUDED from the capture-schema
  (only `model` lenses are described by the 4B). Proves the `produced_by` split is exercised by a real
  seed. *(Distinct from the corpus-RECORD lineage: this is the file's own structural lineage; the record's
  session/round/project is the capture provenance — same word, two axes; see runtime/corpus.py.)*

**Render-NOT-judge (K3):** a lens DESCRIBES (`desc` is a render instruction) — it does NOT judge. The 4B
is a describer; judgement of truth/quality is a LATER reduce pass, never the capture lens itself.

**Where new things go:** a new lens = a new file `projections/<id>.py` declaring its `PROJECTION` dict
(its `id` MUST equal the file name). **Update THIS file** (the drift home) when you add one —
`tests/projections_acceptance.py` fails loud if a discovered projection isn't reflected here (mirrors how
`roles_acceptance` guards roles against `roles/AGENTS.md`).

**To extend:** drop a `projections/<id>.py` (model OR code lens) → it self-registers → it appears in the
capture-schema (if `model`) / the space set (if `embeds`) / `cognition_info` with NO code change. To
author one from the agent face: `create_projection` (the MCP/agent-face tool — the declarative-direct
create, like `create_skill`: renders `PROJECTION = {...}`, runs THIS registry's own discover() gate
in a tempdir, writes `projections/<id>.py`, git-commits (`[self-apply]`, path-scoped → revertible), and
rediscovers so the lens is LIVE in `cognition_info` immediately; node-type / executable-code create stays
GATED). The author path currently lives in `mcp_face/server.py` reusing this registry's gate +
`Suite._commit_or_rollback`; its long-term home is `render_projection_source` in `runtime/authoring.py`
+ a `Suite.create_projection` method (mirroring `create_skill`/`create_context`) — flagged as a seam.

**Seam:** discovered by `runtime/projections.py:ProjectionRegistry` (mirrors `runtime/roles.py:RoleRegistry`
/ `runtime/skills.py:_BaseEntryRegistry`, which mirror `runtime/registry.py:NodeRegistry` —
reuse-don't-parallel, the ONE registry mechanism). The consumers read over the discovered set:
`model_projections()` (the capture-schema) · `embeddable()` (the space set, Group L) · `as_records()`
(the cognition_info projection, SURFACE lane). All pure READS — the floor (no resolve/dispatch/approve).

**Never:** hardcode a lens in a literal list/dict (this module IS the no-hardcoding rule — the registry
path, never the literal; PART 4.3) · fork a second registry pattern (mirror `RoleRegistry`/`NodeRegistry`) ·
let a capture lens JUDGE (render-not-judge — K3) · ship a lens without reflecting it in this drift home.

## Relates to
- **Discovered by** [[runtime — constitution]] (`runtime/projections.py`, mirroring `runtime/roles.py`/`runtime/skills.py`).
- **Mirrors** [[roles — constitution]] + [[skills — constitution]] — the same self-registering, file-discovered shape.
- **Feeds** the corpus pillar: the capture-schema (K2), the multi-space embedding (Group L), the
  corpus-record (`runtime/corpus.py`, D1).

## Read next
[[Company Map]] · [[roles — constitution]] (the sibling registry this mirrors) · `skills/AGENTS.md`
(the skill registry — same shape) · `build-prep/cognition-engine/COMPLETION-CRITERIA.md` (GROUP K/P).
