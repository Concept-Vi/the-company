---
type: constitution
register: prescriptive
module: types
aliases: ["types — constitution"]
tags: [company, container, registry, types, L3]
status: living
---

# types/ — the generative TYPE registry (④ · L3 · organ-studies/REGISTRY.md)

**What it is.** One **file per universal TYPE** (`types/<id>.py` exporting `TYPE = {...}`), beside the
engine's other file-discovered registries. The rebuilt organ (REGISTRY.md): **B's registration act driving
A's cascade** — one `create(kind='type', spec)` mints a complete citizen (verbs · board card · address ·
routing) by fanning out through `cascades/`. A PEER dir; cascades reference INTO the existing registries,
never fork them (rule 3). Vocabulary = FILES; the generated artifacts + the DB projection are DERIVED, one
way (file → DB); a DB artifact row with no source type file is a GHOST, fails loud.

**What it must guarantee.**
- Every `TYPE.id` **equals its file stem** (addressable by file); a malformed row FAILS LOUD at discovery.
- **The hollow gate**: a TRIVIAL `data_schema` ({} / {"type":"object"} alone / no `properties`) is REFUSED
  with a teaching error naming the de-facto-schema evidence path (HOLLOW-TYPES.md / the 319 posts). This is
  the fix for A's 7 hollow rows fanned out meaning-empty.
- **Law 11**: a type declares its `states` + `initial` + `transitions` (self-consistent — initial ∈ states,
  every transition source/target ∈ states, validated at discovery). An INSTANCE transition is validated at
  the one write door; an illegal transition is refused fail-loud. `state_requirements` drives a resolver
  read that VARIES BY STATE (e.g. task `done` REQUIRES the closure/verification block).

**The TYPE row (schema — `runtime/type_registry.py:TYPE_FIELDS`).**
`id` (==stem) · `label` · `data_schema` (REQUIRED, non-trivial) · `faces` (face-key → spec; the keys ARE
cascade ids — presence = `generates[]` membership) · `states`/`initial`/`transitions`/`state_requirements`
(law 11) · `version` · `provenance` · `desc`.

**Where new things go.** A NEW KIND of project (forecast/theorem/document) = `create(kind='type', {id, label,
data_schema, faces, states…})` → verbs/card/address/routing exist + `capabilities()` gains it, so every
authoring prompt can only speak of it in registered terms (rule 8 closes). A new FACE = one new
`cascades/<name>.py`. **Types are `create()`-authorable (pure DATA); cascades are code-authored (they carry a
handler callable).**

**The landing (C3.3/C3.4).** 16 cloud universal_types: **9 SOUND** landed as files (component_spec→faces.board,
status_values→states) + their artifacts REGENERATED (never migrated). **7 HOLLOW** per HOLLOW-TYPES.md:
RECONSTRUCT 4 (task/milestone/observation/blocker — de-facto schemas + lifecycles) · FUSE 3
(decision/design_proposal/project_space — recorded in `_fusion_map.py`, NEVER silently imported). **+2 GHOST**
(research/diagnostic — registered, routing harvested from the hand-authored decorators; hand-made-powers-the-
generator). The disposition record lives in `types/_fusion_map.py`, surfaced via `Suite.type_info()`.

**Its seam.** `runtime/type_registry.py` (TypeRegistry + generate_all + completeness + law 11); `Suite`'s
`create_type` / `generate_all` / `delete_type` / `type_info` / `type_transition` / `type_state_view`;
`/api/type_info` (bridge). Generated artifacts land in `container.generated_artifact` (migration 0019 — the
INTERIM edge home PENDING L4's edge store).

**What would violate it.** A hardcoded `TYPES={...}` literal · a hollow type going live · a generated artifact
migrated instead of regenerated · a type declaring a transition to an undeclared state · a second type/cascade
store beside this one (rule 3).

## Agent-authored entries (auto-reflected)
<!-- created live by the create face; one line per entry — keeps the drift-home acceptance green. -->
<!-- NOTE: the drift-home reflection is APPEND-ONLY (matches delete_role — deleting an entry leaves its
     line for the operator to prune by integration). The acceptance test stubs git + cleans its probe file;
     if a real create→delete leaves a stale line here, prune it as part of that change. -->

