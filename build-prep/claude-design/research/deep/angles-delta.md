# Angles Delta — Branch Merge Report

> **Date read:** 2026-06-08. Source: `/home/tim/company` (read-only). Method: stat+log first, then 4 bounded diffs.
>
> **CORRECTION TO inv-E-angles.md (Angle 3):** The prior inventory described `concurrent-cognition` as "BUILT, not yet merged" and `interactive-surface-build` as "ACTIVE, has NOT been merged." Both are now wrong. Both branches have been merged. The unified main is the ground truth.

---

## Status Summary (all four branches)

| Branch | Prior status (inv-E) | Actual status |
|---|---|---|
| `concurrent-cognition` | Built, pending merge | **MERGED** at `233f34e` ("Merge branch 'concurrent-cognition'") |
| `interactive-surface-build` | Active in-build, X1–X17 staged | **MERGED** at `e1063f7` ("Merge interactive-surface-build into main") |
| `night-build` | Base case, integrated | Remote-only; all content long since folded via the above two merges |
| `overnight-20260605` | Stale historical checkpoint | Not a current ref; superseded |

**There is one unified main.** The two angles the pack cares about are both on it. The operable-interface-build worktree (`~/company-interface`) carries 3 commits NOT yet on main — the studio scaffold + mockups — addressed separately at the end.

---

## Angle 1 — concurrent-cognition (MERGED at `233f34e`)

### What it adds structurally

The concurrent cognition **organ** — a complete swarm/staging layer that runs alongside the primary RHM turn. 7 new files in `/home/tim/company/runtime/` + 8 role files in `/home/tim/company/roles/`:

| File | What it is |
|---|---|
| `runtime/cognition.py` | The proving spike + `run_role` + `run_swarm` / `SlotBudget` — fires concurrent model calls, writes results to `run://<turn>/<role>` addresses in the CAS store |
| `runtime/roles.py` | File-discovered `RoleRegistry` — scans `roles/*.py`, loads every role as a `Role` dataclass (id / prompt_template / output_schema / model_binding / mode_scope / verdict_rule); the single role notion, reused by both the swarm and authoring |
| `runtime/rules.py` | Declared-AST rule engine — a closed grammar (never eval), 5 rule destinations (inject / surface / suppress / escalate / log), deterministic: identical resolved inputs route identically regardless of concurrent role finish order |
| `runtime/activation.py` | Per-turn activation context registry — 3 trigger types (background / sense / rollup) fire non-reply roles on the reserve; the main-turn reserve is sacred (G9 floor by construction) |
| `runtime/authoring.py` | The operator-facing authoring backend — propose/apply/edit/delete role; rule validate/dry_run/attach; dry_run_role/preview_turn; the select queries (models_for_role/inputs/field_types); 12 `/api/cognition/*` endpoints |
| `contracts/cognition_info.py` | The `build_cognition_info` projection — registry-generated, reusable, dynamic; sibling of `object_info`; read by `GET /api/cognition_info` |
| `roles/*.py` (8 files) | File-discovered cast: focus / recall / ground / connect / check / voice / judge / verify_jury — each declares its output schema (Pydantic), model_binding, mode_scope, verdict_rule |

**Suite.py additions** (large hunk on the shared file — not a separate file):
- `chat_parts()` generator — the staged-chat producer; the heart of G4: shared prologue·part-core·epilogue pattern; `THOUGHT_SHAPES` + `PART_GRAIN` registries; mandatory brevity bypass; tools-on-final-only
- `THOUGHT_SHAPES` / `shape_for` — per-mode thought-shape (the cognition side of the mode dial)
- `run_swarm` integration into the chat hot-path — fan-out concurrent role calls per turn, inject via resolved `run://` addresses
- AUTH backend inline (16 `/api/cognition/*` methods)

**Bridge.py addition** (the G6 voice coupling, also shared):
- `_stream_parts()` — the brain↔TTS overlap factory: a producer thread runs `chat_parts()` ahead of synthesis so part N+1 is generated while part N is being synthesized; `clean_fn` is the V-C/V-D speakable layer (per-part, before sentence split); fail-loud on clean-to-empty; proactive disconnect probe

**CognitionView.tsx (new FE region):**
- Three altitudes: Pulse (ambient iris, dilation = depth-of-thought shape), River (SVG flow diagram, tributaries per role, width = contribution, red silted stub = failure), Nodes (role card list)
- Driven entirely by `cognition.*` SSE events + `GET /api/cognition_info` — reflects-never-owns
- Registry-driven: role list comes from the projection, not hardcoded; a new role appears here with zero FE code

**New SSE event branch — `cognition.*`:**
Events emitted into the main `/api/stream` spine on a `cognition.*` channel:
`cognition.wave.start` → `cognition.role.fire` × N → `cognition.role.ran` × N → `cognition.inject` → `cognition.wave.done`
Causal-ordered, addressable by `run://<turn>/<role>` address.

**Governance additions:**
2 new CONFIRM-class verbs in governance (the build-dispatch floor: by construction, no role / rule / authoring path can emit resolve/approve/dispatch). A standing governance regression suite (18 checks) enforces this.

**New test files:**
`activation_contexts_acceptance.py` (293), `authoring_acceptance.py` (271), `chat_parts_acceptance.py` (418), `cognition_governance_acceptance.py` (141), `cognition_info_acceptance.py` (311), `voice_parts_acceptance.py` (423), `json_schema_transport_acceptance.py` (282), `model_capabilities_acceptance.py` (175), `roles_acceptance.py` (177), `rules_acceptance.py` (421), `wire_async_dispatch_acceptance.py` (382), `wire_commit_acceptance.py` (292), `suite_health_acceptance.py` (55) — 13 new test files, all acceptance-by-use.

**Also added during the cognition session (committed before or during merge):**
- `build-prep/claude-design/BACKEND-SEAM-PACK.md` (449 lines) — the FE-facing seam contract for the full unified backend; 102 routes documented; curled-live evidence on every response shape; the cognition-authoring side cross-refs `AUTHORING-FE-HANDOFF.md`. **This is a major already-written seam doc the pack must not duplicate — reference it.**
- `build-prep/concurrent-cognition/AUTHORING-FE-HANDOFF.md` (337 lines) — the full authoring UI contract (12 endpoints, `RoleFieldSpec` / `RuleAST` / `RuleDecl` shapes, the UX surface map)

---

### How concurrent-cognition reshapes shared seams (the contract-level changes)

These are the seams that the concurrent-cognition merge changed — not additions but CHANGES to existing contracts:

**1. suite.py — the mode dial is now built twice, awaiting unification**

The interface session built `MODE_SPECS` / `resolution_spec_for` (what context resolves per mode). The cognition session built `THOUGHT_SHAPES` / `shape_for` (what thought-shape / grain / staging applies per mode). Both operate on the same 8 modes. As stated in MERGE-COORDINATION.md: "the mode dial is built twice — these are two halves of ONE declaration on the SAME 8 modes." They were merged without a collision (no textual conflict), but the semantic integration — unifying the two into a single mode declaration — is a **named pending integration** in the MERGE-COORDINATION file. The pack must document this as an open seam: the MODE declaration is split across two locations in `suite.py`; a future integration will unify them.

**2. suite.py chat-core — the thread-scoped feed**

The cognition session's G4 refactor (the `chat_parts` generator) had a pre-merge bug where `_chat_part_core` read `self.store.chat_history(20)` (global, not thread-scoped), silently reverting the interface session's fix for new conversations starting fresh. This was caught, verified, and patched at merge time: the fix is `chats_in_thread(_tid, 20) if _tid else chat_history(20)`. The merged main has the correct thread-scoped read. **This is verified; it is not an open issue.** But it tells the pack that `chat_history` vs `chats_in_thread` is a load-bearing distinction at this seam.

**3. bridge.py `_voice_stream` — speakable layer**

The cognition session's G6 voice coupling (brain↔TTS overlap, `_stream_parts`) was merged with the interface session's V-C/V-D speakable layer. The combine: raw part text flows to `on_part` (the `{type:part}` display event) and into the assembled reply UNCHANGED; `clean_fn` (bound to `voice.speakable`) is applied to the whole part BEFORE the sentence split — only the TTS-bound text is cleaned. This is the settled contract on the voice streaming seam. The pack's existing `seams.md` references `voice/speakable.py` but may not have the `clean_fn` per-part granularity detail — it should add it.

**4. The self-mod audit ledger (`_SELF_CHANGE_STREAMS` / `_change_stream`)**

The interface session restructured the audit ledger that the cognition session's `[self-apply]` commits write into. Post-merge, the `selfmod_audit_acceptance` suite (34 checks) verifies that `[self-apply]` commits classify correctly under the new `_change_stream` logic. This seam is verified green. It is a **shared write surface** — any FE surface that displays or navigates self-change records must understand both classification classes.

**5. The latent FE capabilities — `cognition.*` SSE as CognitionView inputs**

The interface session built `/api/knobs`, `/api/run-stats`, and node-states with no FE caller (verified BUILT in `seams.md` §14 as DESIGNED-NOT-BUILT for the setter, READ-ONLY for the config). These are exactly what `CognitionView` needs as inputs. The `cognition_info` projection (via `GET /api/cognition_info`) + the `cognition.*` SSE lifecycle together give CognitionView everything it renders. The pack must document this as a closed wire: the previously-latent capabilities now have a consumer.

---

## Angle 2 — interactive-surface-build (MERGED at `e1063f7`)

### What it adds structurally (X1–X17 + L-series)

The X-numbered commits are a staged delivery of the **Operable Composition Surface** — the coordinate system by which the operator points at any element and the system composes builds from that precise location. All 17 are now on main.

**The address-to-scope-to-build chain (X1–X8):**
- X1: `surface_build_intent` persists the `ui://` address into the payload before persist (the pointed build)
- X2: `resolve_scope` symbol-neighbours persisted alongside (the code scope at mint time)
- X3: `_r2_gather` + `_r2_score_and_cap` runs at mint and persists the bounded context bundle as `payload.context` (R2 gather AT MINT — consent-time property: what the operator approved is what the build composes from)
- X4: `build_instruction` composes the rich prompt from address + symbols + context bundle (pure: decision-in / str-out, no I/O)
- X5: Consent-time resolution proven by construction (mint resolves once; dispatch composes from the persisted record, no second gather)
- X6: `ui://` ↔ `run://` bridge — R2 gather at a `ui://canvas/<node>` locus also resolves the node's `run://`-keyed strata (version-history + node-instance events)
- X7: Pin override — `Suite.pin(address, target_ts)` + `POST /api/pin` + append-only `pins.jsonl` overlay
- X8: `_r2_dedup` collapses a clicked comment's annotation+chat+event echo to ONE item in the gather

**The structural graph substrate (X9–X11):**
- X9: `blast_radius(address)` — inverts `code-symbols.json`'s `referenced_by` into the co-reference sibling set
- X10: `design/_system/codeedges.py` — parses ~/company source into symbol→symbol `depends_on` / `depended_by` edges (428 symbols) keyed by the same `code://` ids; `code-edges.json`; `reach_report` bounded at DEPTH 2-3
- X11: `semantically_nearest[]` — additive sibling field in `code-symbols.json`; embeddings via the existing embed node (BGE-M3), top-5 cosine `code://` ids; degrade-with-warning if embedder down

**The semantic and configurable composition (X12–X17):**
- X12: Persisted vector index — new `vectors/` namespace in the one FsStore; `store/vector_index.py` build_index (content-hash incremental) + query_index; degrade-with-warning proven live
- X13: R2 semantic ranking term — 4th term in `_r2_score` (`R2_SEMANTIC_WEIGHT * cosine(intent, item)`); precomputed per turn; degrade to 0 if embedder down
- X14: `blast_radius` spans both edge kinds — 4 distinguished kinds returned: co_reference / structural_dependents / structural_dependencies / semantic_neighbours
- X15: Constitution-hop — `build_instruction` names the governing module `AGENTS.md` (walks each scope file's parent dirs up to the nearest ancestor with an `AGENTS.md`)
- X16: Operator-approves-the-reach — `approve_reach(sid, members)` + `POST /api/approve-reach`; blast_radius persisted at mint so the operator sees the reach before widening; safety: a member NOT in the persisted radius RAISES (no scope injection)
- X17: Configurable composition — R2 ranking knobs (`R2_LAMBDA`, `R2_PROXIMITY_WEIGHT`, `R2_PIN_WEIGHT`, `R2_SEMANTIC_WEIGHT`, `R2_BUDGET`, `R2_RUN_VERSIONS`) resolve from env (`COMPANY_R2_*`) at `Suite.__init__`; `capabilities()` exposes `composition_config` (read-only)

**The L-series (interactive addressed surface wires):**
- L1 / `POST /api/intent-at`: addressed-feedback → wire (comment at a `ui://` address → ingest_comment + resolve_scope + surface_build_intent; already documented in `seams.md` §11)
- L2: `wire_armed()` + `permission_mode()` — the resolve→dispatch production trigger (INERT BY DEFAULT, `plan` mode; `acceptEdits` opt-in only); `wire_armed()` gates all autonomous dispatch
- L4: Twin located-gold — `ingest_comment` emits one additive `append_chat` stamped with the address; routes via `_provenance_grade` as operator/gold/located (trains the twin with location)
- L5: `self_changes_at(address)` + `revert_self_change_at` + `GET /api/self-changes-at`; `SelfChanges.tsx` region
- L6: Ref-version index — `ref_versions(address)` + `GET /api/ref-versions`; `Versions.tsx` surface
- L8: Inbox items carry a `ui://` target in payload; `Inbox.tsx` "↳ go to thing" link → `resolveUiTarget`
- L9: Journey recording — `POST /api/journey/{start,step,stop}` + `GET /api/journey/replay,/api/journeys`; `JourneyBar`
- L10: `stale_at_address(address)` + `GET /api/stale-at`; Inspector freshness badge

**New test files (X/L series):**
`design_gate_acceptance.py` (185), `event_address_acceptance.py` (329), `feedback_to_wire_acceptance.py` (179), `focus_ui_address_acceptance.py` (111), `inbox_target_acceptance.py` (150), `journey_recording_acceptance.py` (113), `locus_acceptance.py` (132), `memo_stale_acceptance.py` (189), `navgraph_acceptance.py` (171), `node_states_render_acceptance.py` (99), `propose_affordance_acceptance.py` (168), `self_change_locating_acceptance.py` (179), `twin_located_gold_acceptance.py` (188), `ui_registry_acceptance.py` (166), `version_history_acceptance.py` (137) — 15 new test files.

---

### How interactive-surface-build reshapes shared seams

**1. `surface_build_intent` signature extended (X1–X3)**

`surface_build_intent` now persists `address`, `symbols[]`, and `payload.context` (the R2 bundle) at mint time. The mint is the consent-time boundary — the surfaced record IS the launched record. The pack must document that every caller of `surface_build_intent` (or `POST /api/intent-at`) gets a richer payload than before: the scope and context are now part of the persisted proposal, not derived again at dispatch.

**2. `blast_radius` return shape extended (X9 → X14)**

The `blast_radius(address)` return evolved across X9/X10/X14. Final shape has 4 distinguished keys: `co_reference[]`, `structural_dependents[]`, `structural_dependencies[]`, `semantic_neighbours[]`. Any FE surface consuming blast_radius must know this is the shape — not just a flat list. The pack must document the 4-kind contract.

**3. `capabilities()` / `composition_config` added to the capabilities contract**

`GET /api/capabilities` now includes a `composition_config` section (the R2 knobs). The pack's seams must add this to the capabilities contract. Read-only: no setter route. This is the only DESIGNED-NOT-BUILT gap confirmed in `seams.md` (§14).

**4. `approve_reach` as a net-new operator-only route (X16)**

`POST /api/approve-reach` is a new operator-only route that does NOT exist in `RHM_VERBS` and is not accessible from the MCP face. This is structurally important: it is an explicit operator gate on scope expansion. The pack must add it to the route table as a distinct governance action.

**5. The `code-edges.json` as a new registerable substrate (X10)**

`design/_system/codeedges.py` builds and maintains `code-edges.json` — structural code dependencies. This is a net-new substrate (sibling of `code-symbols.json`, same `code://` key space) that `resolve_scope` + `blast_radius` consume. It is NOT part of the graph substrate (it is design-side, read-only at runtime). The pack must note this as a distinct registry: the corpus now has THREE layers — `code-symbols.json` (UI→code mapping), `code-edges.json` (code→code structural deps), and the vector index (code→code semantic neighbours).

---

## Angle 3 — operable-interface-build worktree (NOT YET MERGED)

3 commits ahead of main. These carry the studio and redesign mockups — the visual/aesthetic layer that is held pending Tim's A/B/C decision.

**What's added beyond main:**
- `canvas/app/src/components/StudioKit.tsx` (231 lines) + `StudioSeams.ts` (106 lines) — the studio component kit: `RailNav`, `Stage`, `RhmPanel`, and the backend seam helpers
- `canvas/app/src/regions/Review.tsx` (62 lines) — the Review surface (a real in-app page of the main app, not a standalone portal)
- `design/mockups/IA-desktop.html` (838) + `IA-mobile.html` (1031) — the Interactive Architecture redesign mockups (gold-primary, living-instrument)
- `design/mockups/STUDIO.html` (739) + `SCENARIO-PLAYER.html` (750) — the studio and scenario player mockup designs
- `design/mockups/A2-rhm-mobile-elevated.html` (313) + `A3-settings-elevated.html` (263) — elevated mobile designs

**Important:** The worktree REMOVES `CognitionView.tsx` (214 lines deleted in the stat). This means the worktree predates or diverges from the cognition merge on this file. A merge of the worktree onto main will require reconciling the `CognitionView.tsx` addition (from concurrent-cognition, on main) with the worktree's deletion. This is the **primary merge risk** for the worktree → main path.

---

## Structure Implications: What the Pack Must Account For

### Surfaces / seams to ADD to the pack

1. **Cognition organ contract** — `GET /api/cognition_info` (the registry projection) + the `cognition.*` SSE event lifecycle (`wave.start` → `role.fire×N` → `role.ran×N` → `inject` → `wave.done`). The CognitionView depends on both. The pack does not currently document this.

2. **Authoring surface contract** — the 12 `/api/cognition/*` endpoints. Already written in `build-prep/concurrent-cognition/AUTHORING-FE-HANDOFF.md` (337 lines) and cross-referenced in `BACKEND-SEAM-PACK.md`. The pack should reference these docs rather than re-characterize from scratch.

3. **`blast_radius` 4-kind return shape** — the 4 distinguished keys must be in the pack's contract table. Currently `seams.md` doesn't describe blast_radius return shape.

4. **`POST /api/approve-reach`** — new operator-only route (not in `RHM_VERBS`, not on MCP face). Missing from the route table entirely.

5. **`GET /api/stale-at`** — L10 staleness check. Missing from route table.

6. **`GET /api/ref-versions`** — L6 version history at an address. Missing from route table.

7. **Journey recording routes** — `POST /api/journey/{start,step,stop}` + `GET /api/journey/replay` + `GET /api/journeys`. Missing from route table.

8. **`self_changes_at` / `GET /api/self-changes-at`** — L5. Missing from route table.

9. **The three corpus layers** — `code-symbols.json` / `code-edges.json` / `vectors/` (the persisted vector index). The pack's seams only describe the first layer.

10. **`composition_config` in capabilities** — `GET /api/capabilities` now carries `composition_config` (the R2 knobs). The pack must add this as a read-only sub-object.

### Contracts that CHANGED (not additions)

1. **`surface_build_intent` / `POST /api/intent-at` payload** — now includes `address`, `symbols[]`, `payload.context` persisted at mint time. Any description of the build-intent shape is now incomplete without these fields.

2. **The mode declaration** — `MODE_SPECS` (interface session) and `THOUGHT_SHAPES` (cognition session) are two halves of one mode contract. The pack must document both registries and name their unification as a pending integration.

3. **`chat_parts()` as the staging generator** — the staged-chat path through `voice/stream` now uses `chat_parts()` with `THOUGHT_SHAPES`/`PART_GRAIN` registries. The voice seam contract must describe this generator, not just the endpoint.

---

## The Biggest Reshape to Watch

**The mode-dial unification** is the single most structurally consequential pending work the pack must name.

`MODE_SPECS` / `resolution_spec_for` (what context R2 resolves per mode) and `THOUGHT_SHAPES` / `shape_for` (what thought-shape / grain / staging the cognition organ uses per mode) are the two halves of the same dial. They were merged without a textual conflict but their SEMANTIC unification was explicitly deferred. The MERGE-COORDINATION.md names it as "the integration (the real prize)." It is not a bug; it is the designed next convergence.

Until this unification is done:
- Any FE surface that adapts to mode (the Settings/mode UI, anything that renders mode-aware cognition behavior) is touching a seam that is about to be restructured
- The pack that documents the mode contract must document BOTH registries and flag their planned merge
- The mode dial's eventual unified form will be the single place where mode controls BOTH what context is resolved AND how the cognition organ shapes its output — that's a large surface change when it lands

The concrete risk: if Claude Design builds mode-specific rendering based on `MODE_SPECS` alone (ignoring `THOUGHT_SHAPES`), that work will be partially invalidated when the two are unified. The safe path is to document both, wire both, and treat the unification as a near-term surface change.

---

## Cross-reference map (what already exists vs. what's missing)

| Item | Exists where | Status |
|---|---|---|
| 102-route contract (all subsystems) | `build-prep/claude-design/BACKEND-SEAM-PACK.md` | Written. Reference, don't re-do. |
| Authoring contract (12 `/api/cognition/*`) | `build-prep/concurrent-cognition/AUTHORING-FE-HANDOFF.md` | Written. Reference. |
| Interface seam contracts (I2/I4/R1/R2/L1) | `claude-design/research/deep/seams.md` | Written (this pack). |
| `cognition.*` SSE + `GET /api/cognition_info` | Missing from seams.md | **NEEDS ADDITION** |
| `blast_radius` 4-kind return shape | Missing from seams.md | **NEEDS ADDITION** |
| `POST /api/approve-reach` | Missing from route table | **NEEDS ADDITION** |
| L5/L6/L8/L9/L10 routes (stale-at, ref-versions, journey, inbox-target, self-changes-at) | Missing from seams.md | **NEEDS ADDITION** |
| Three corpus layers (code-symbols / code-edges / vectors) | Only first layer described | **NEEDS EXPANSION** |
| `composition_config` in capabilities | Not in pack | **NEEDS ADDITION** |
| Mode-dial split (`MODE_SPECS` + `THOUGHT_SHAPES`) | Not in pack | **NEEDS DOCUMENTING as open seam** |
| Studio / redesign mockups (IA-desktop/mobile, STUDIO.html) | `design/mockups/` in worktree only | **NOT YET ON MAIN** |
