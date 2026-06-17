# Self-Build Substrate — Unified Design Synthesis
*Lead synthesis of the 3 design-grounding investigations (DESIGN-forms-built.md · DESIGN-lifters.md · DESIGN-trigger-registry.md), 2026-06-17. The plan/design Tim asked for BEFORE launching builders. Provisional; awaits Tim's decisions (below).*

## ★★ CONVERGENCE (2026-06-17) — this IS DNA's "Substrate — Part One" (don't fork)
Tim pointed the lead at `board://item-d65629c4` + `counterpart/design/docs/command/SUBSTRATE-ARCHITECTURE.md` (DNA's session). It is Tim's VERBATIM architecture for exactly the SEE+SHAPE half designed here — and DNA has BUILT a first cut: `substrate/address-registry.json` (621 addrs, contains-edges, types, time+position) + `substrate/type-registry.json` (22 types) + the census RAN (224 files, 1,050 typed edges w/ equal-opposite `referenced_by`, 14 ghost nodes) + `docs/WAYFINDER.md` + root `CLAUDE.md` + `engine/substrate-assemble.py`/`substrate-wayfinder.py`. So:
- **DO NOT build a parallel coverage/forms/lifter system. CONVERGE onto the substrate.** (union law.)
- Reconciliation (this doc's design ↔ the substrate): "deterministic lifters" = the substrate's typed-edges + per-type **parsers**; "forms" = the substrate's **type-registry declarations** (parsers/format/fields/valid-edges/context/interpretations) + the registry's own rules (valid-types/ignore-lists/prompt-resolution); "coverage scan→ignore-list" = the **census** + the registry ignore-rules + dispatch-by-territory; "model-vs-lifter split" = Tim's **"two halves"** law (derived structure vs authored meaning); the "recognisers→data" crux = already the substrate's **derive-never-place + registry-is-truth + add-by-declaration** laws (ANSWERED — declaration-not-code is the law here); "allocate by space not search" = the substrate's **founding dispatch law**.
- **★ PLACEMENT (Tim, 2026-06-17):** do NOT build the company's substrate ON DNA's instance — her substrate is SPECIFIC/ISOLATED to the design project; the COMPANY is the MAIN. The canonical substrate engine is built INTO the company; DNA's proven cut is the SEED + reference (the proving ground, not superseded); her design repo becomes ONE PROJECT the company's substrate covers. Shape = ONE engine (home = company) + per-project REGISTRIES as instances (design repo = one, company repo = another). DNA = architect-of-record for Part One (her verbatim-from-Tim doc is canonical) + owner of her instance; lead = port+generalize the engine into the company + the act-layer + the cross-project/project-registry layer.
- **What this doc owns (EXTENDS the substrate, built INTO the company):** (1) the **ACT layer** = "Substrate Part Two" — the TRIGGER registry (event→action→CC-launch) operating OVER the addressed graph; the substrate doc is explicitly "Part One: the queryable repository" (SEE+SHAPE) and does not cover acting. (2) the **COMPANY substrate engine** — generalize DNA's per-project cut into the company's canonical engine, pointable at any project (the project-registry + global/project/user scope + SQL/Postgres + the COMPANY address-resolution the doc names), seeded by engine/substrate-*.py. (3) the **substrate↔corpus bridge** — the substrate is the STRUCTURAL typed graph; the corpus is the SEMANTIC embeddings; the census feeds BOTH (structure→substrate, meaning→corpus). Wire into the company's existing resolve_address + forms/lifters/projection registries (reuse, don't re-create in the company either).
- The "decisions for Tim" below mostly COLLAPSE (the substrate's laws already answer recognisers→data + scope + lifter/form unification). What remains is the SEAM with DNA (below) + the act-layer + the hoist.

## THE PICTURE — three faces of ONE substrate
What Tim asked for (forms-built + coverage-hardened + trigger-registry) is one introspective self-build substrate:
- **SEE itself** — COVERAGE: scan→ignore-list→read-set → deterministic lift + schema-enforced digest → chunked embed → records → layered understanding.
- **SHAPE what it sees** — FORMS (tier effort + context + output by file-type) + LIFTERS (deterministic structural facts).
- **ACT on itself** — TRIGGERS: event → driver → trigger-registry(when?) → action (a CC-launch node) → write back.

## THE BIG FINDING — it's all built, and WIRED TO NOTHING
Each of the three mechanisms is **built, tested, and surfaced — but no working path calls it**:
- FormRegistry.route() exists; no capture path calls it (uniform role+max_tokens on every unit).
- LifterRegistry.extract() exists; the only callers are the test file → the deterministic half of every corpus record is currently EMPTY.
- The trigger circuit's every link exists (rules.RULE_OPS, routines/spawn, board edges) except the binding registry + the driver.
So this build is **~80% CONNECTING + hardening, ~20% net-new.**

## ★ THE ONE CRUX (all three pillars hit it independently)
The same thing blocks all three from being **agent-authorable the way Tim's theorem wants** (declared, in registries, no hardcoding): their **recognisers are Python CALLABLES**, and the company's shared auto-authoring gate (`_write_registry_file`, suite.py:9886) **refuses callable fields** — which is exactly why forms, and the pure-data `mode_detection_rules`, are kept OFF the `create()`-authorable `_CORPUS_REGISTRIES` table.
- Forms: `match` is a callable → `create_form` impossible on the shared gate.
- Triggers: `create(kind='trigger')` conditional on the same.
- Lifters: `match` must be a regex STRING not a callable (callable breaks `as_records()` serialization) — same root.

**THE DECISION: move recognisers from code → DATA** (a `rules.RULE_OPS` data-AST + regex-strings, the `mode_detection_rules` prior art).
- If YES: forms + triggers + lifters ALL become `create()`-authorable — agents author them LIVE, registry-is-truth, zero code edit. This IS Tim's theorem (everything declared/in-registries/authorable/no-hardcoding). One shared gate for all three.
- Cost: add a few shape-recognition ops to RULE_OPS (regex-on-head, line-ratio, extension-match); convert the 3 seed lifters + the placeholder forms to data-match. Bounded.
- RECOMMENDATION: **YES, recognisers as DATA.** It resolves the forms/trigger/lifter authoring at one stroke and is the single most theorem-aligned move. (Hybrid escape hatch: a genuinely-complex recogniser can stay developer-gated code; the DATA path is the default + the authorable one.)

## DECISION 2 (small) — scope as a SHARED registry base
global / project / user scoping doesn't exist today. Add it ONCE as a shared base for the file-discovered registries (forms as pilot → triggers, lifters, eventually roles/projections), not six copies. `project` links via the explicit `project` arg the calls already carry (no active-project singleton exists). Precedence: (scope_rank, fallthrough_rank, id). RECOMMENDATION: shared base.

## DECISION 3 (small) — the TS/JS extractor
Python has `ast` (reuse), markdown/json/yaml have parsers (reuse). TS/TSX/JS/MJS have **NOTHING in-repo**. RECOMMENDATION: **regex extractors now** (zero-dep, respects the in-process-READ floor, ships for the recent TS coverage pain), with **tree-sitter-typescript flagged as the robust upgrade**. (node/tsc subprocess rejected — breaks the floor.)

## LEAD-DECIDED (recommendations; flag if you want in)
- Inbound-link descriptions: store `link_context`, fold at read-time (don't pre-emit into the vector substrate yet).
- Event-kind taxonomy: validate against the existing ACTIVATION_CONTEXTS first; first-class `event_kinds/` later if needed.
- Trigger safety: single-fire/dedup + the self-trigger-loop guard (reuse the OPERATOR_ACTIVITY_KINDS self-exclusion pattern) — non-negotiable, built in.
- The trigger DRIVER ships BUILT-NOT-ARMED (mirrors activation_driver's dormant env-gated posture) — provable by one synthetic event, no always-on daemon until Tim arms it.
- The capture→forms wire + the lifter lane ship as OPTIONAL switches (by_form=False default → byte-identical to today).

## REUSE vs BUILD (the dispatch map)
REUSE: FormRegistry.route · LifterRegistry · rules.RULE_OPS/route/DESTINATION_KINDS · routines/supervisor spawn · cc_board edges · the walk→digest→embed ledger · response_format=json_schema · the over-context chunker · ast/json/yaml parsers · the dynamic-schema-from-lenses builder.
BUILD: recognisers→data (RULE_OPS shape-ops + convert seeds) · shared global/project/user scope base · capture→forms bucket-by-stage wire (+ policy passthrough, drop skip) · lifter→capture attach (one block in ingest_paths, record.structure) · TS/JS regex lifters · pass-0 dir-scan→ignore-list step · embed-side chunking · CC-launch node (nodes/cc_launch.py) + close the structured_output capture gap (result.structured_output, snake_case) · runtime/triggers.py registry + trigger_driver.py (dormant) + board.filed emit + responds_to edge · mcp_face/tools/triggers.py.

## SEQUENCE (after Tim's decisions → builders dispatched per criterion)
1. Foundation: recognisers→data + shared scope base (unblocks all authoring).
2. Coverage-useful: pass-0 scan→ignore · lifter lane · capture→forms wire · embed chunking · schema-enforced digest.
3. Trigger: CC-launch node + structured_output fix · triggers registry + dormant driver · board.filed emit + responds_to.
4. Verify by use + run the first real coverage (form/lifter-shaped) → the map → Tim.
