# ORGAN-MAP GROUNDED — the FRAME organ-map verified against the real code

> **What this is.** The LANE-GROUND deliverable for ① (the value of the repo-exocortex): the FRAME doc's
> LEAN organ-map (`FRAME-the-two-halves.md` § "THE ORGAN-MAP") asserted "downstream ~80% built" as an
> **unverified lean reading**. This doc GROUNDS every row against the real `~/company` code — each ✅/🟡
> resolves to a real `file:symbol` I checked exists; the built-percentage is **computed from the cites,
> not guessed**; every FRAME-map row that was wrong is FLAGGED; and the precise NET-NEW backlog (what the
> Surface still needs that the engine does NOT have) is assembled from every 🔴/🟡-half.
>
> **How grounded (degrade-clean note).** The lane said: query the `space='repo'` corpus via
> `find_relations` if the INGEST lane populated it by run-time, else grep directly. At run-time the corpus
> was **empty** (`list_corpus(project='company')` → 0 records; one stray `cognition-engine` digest in the
> whole store, NOT a `repo`-space record) — the INGEST lane had not completed. So I grounded by **direct
> deterministic grep + read** of `~/company` (clean degradation), citing real `file:line:symbol`. This is
> itself a finding: **row 10's corpus/spaces code exists but has never been run on the repo** (the spaces
> are unpopulated — the ① ingest is a real net-new ACTION, not just net-new code).
>
> **Read-only.** No code touched. This doc cross-references `FRAME-the-two-halves.md`; it does not edit it.
>
> **RE-VERIFIED (a later GROUND beat, 2026-06-09 ~20:40).** This deliverable was authored by an earlier beat
> of the GROUND lane; this beat **re-verified it, it was not re-authored.** Re-checks this beat: (a) every
> ✅/🟡 `file:symbol` cite still resolves to the real line (grep over `runtime/cognition.py`,
> `runtime/suite.py`, `store/*.py`, `roles/` confirmed the row-1/2/7/9/12 spine + the row-3/8/13 corrections);
> (b) the corpus is **still empty** at this run-time — `list_corpus(project='company')` → 0, whole-store
> `list_corpus()` → 1 record (the SAME stray `cognition-engine`/`projection='what'` digest, NOT a `repo`
> record), `find_corpus(projection='repo')` → 0 — so the row-10 "the ① ingest never ran on the repo" finding
> STANDS; (c) **`embed-bge` is now RESIDENT** (`company gpu`: 4.9 GB, co-resident with `chat-4b` at 8.0 GB,
> 6.4 GB free) — the embedder is UP, so net-new #8 (RUN the ① repo-exocortex ingest) is now **unblocked to
> run**, no eviction needed. *(One isolated `run_role(op="embed")` run exists in the run-index — `list_runs`
> seq 2204, 167s. That is a standalone embed at a `run://` address, NOT a `capture_corpus` chain, so it
> produces no `corpus.record` by design — it does NOT contradict the empty-corpus finding and is NOT a
> failed-ingest. Noted to preempt a future misread.)*

---

## THE CROSS-CUTTING TRUTH (the pattern under every row)

The single pattern the evidence shows, stated plainly so it can be applied per-row and not re-derived:

> **The engine has the PRIMITIVES and the PATTERNS. Many SPECIFIC Surface organs are net-new.**

- **Primitives that exist (✅, the spine):** `run_items`/`run_reduce`/`run_role`/`run_chunked` (the
  axis-inversion swarm fan), `SlotBudget.from_registry` (registry-driven concurrency cap), the
  **lens-rides-in-input** pattern (one role = N jurors/panelists), marks + the file-discovered mark-type
  registry, the corpus capture+embed+query stack, and the decision→build wire.
- **Specific organs that DON'T exist yet (🔴/🟡):** the §20.4 extractor roles (anchor / preference /
  rejection / constraint / contradiction / missing-field), `session_memo` / ⑨ durable-memory,
  progressive-type-resolution **wiring**, schema→UI **render**, first-class Decision-Ledger /
  Assumption-Shelf / Missing-Information-Map **objects**, and — the headline — the **schema-rendered
  generative surface itself** (§19). Plus: the corpus is **empty** (the ① ingest never ran on the repo).

This is why the grounded built-% lands **meaningfully below** the FRAME's lean ~80% — and that gap IS the
grounding working (it converts "≈80% built" into a real, citeable backlog). It is **not** green-paint and
**not** a failure: the spine is real and reusable; the Surface-specific organs are the build.

---

## THE GROUNDED ORGAN-MAP (each ✅/🟡 cites a real `file:symbol` I verified)

Legend: ✅ EXISTS (cite) · 🟡 PARTIAL (cite + what's missing) · 🔴 NET-NEW (nothing found).
`FRAME →` is the status the lean FRAME map asserted; **`GROUNDED →`** is the verified status.
A ⚠️ flags a FRAME-map row I found WRONG.

| # | Surface organ (the doc) | Real downstream code (verified `file:symbol`) | FRAME → | GROUNDED → |
|---|---|---|---|---|
| 1 | Fan-out/fan-in (32×4B + 6 larger) §20.1–20.4 | `runtime/cognition.py:1085 run_items()` (1 role × N units, concurrent on the swarm) · `:1769 run_reduce()` (fan-in) · `:708 class SlotBudget` + `:725 from_registry` (the 32-knee from `max_num_seqs`, registry-driven) · service `chat-4b` @ `ops/services.json` | ✅ | ✅ |
| 2 | The Arbiter (higher model → next action) §20.5 | `runtime/cognition.py:1769 run_reduce(mode="role")` (the synthesizing join) · the jury roles: `roles/verify_lens.py` + `roles/verify_jury.py`/`roles/confirm_registration.py` (`draws`+`verdict_rule` quorum, `runtime/roles.py:36-37`) · arbiter slot = a stronger `model_binding` via `models_for_role` | ✅ | ✅ |
| 3 | Tags/counts/observations NOT confidence §12 | `store/fs_store.py:677 append_mark` + `:705 marks_for` · `runtime/suite.py:9151 mark()` (gated by the file-discovered `runtime/mark_types.py` registry) · corpus `runtime/suite.py:9630 capture_corpus` | ✅ "a LAW already" | ⚠️ **🟡** |
| 4 | Progressive type resolution §11 | the registries exist + are file-discovered (`runtime/roles.py:205 RoleRegistry.discover`, `runtime/mark_types.py`); `run_role` runs over them. **No progressive-resolution WIRING** (no foreground/supporting/rejected/resolved schema-state machine, no §11 stage driver) | 🟡 | 🟡 |
| 5 | Schema activation → schema-rendered UI §19/§18 | declarative panels: `runtime/suite.py:10229 propose_panel` / `:10265 apply_panel` → `canvas/app/src/components/PanelView.tsx` (renders **fixed JSON field-defs**, the 'others' tier). **NOT** §18→§19 schema→UI: no schema-state→component-render path | 🟡 | 🟡 |
| 6 | Anchor/preference/rejection extractors §20.4 | the run_items **tagger pattern** exists (lens-rides-in-input: `roles/verify_lens.py`, `roles/develop_option.py`) — proven shape. **The §20.4 extractor ROLES do NOT exist** (no anchor/preference/rejection/constraint/contradiction/missing-field role files in `roles/`) | ✅ pattern | 🟡 (✅ pattern · 🔴 roles) |
| 7 | Possibility generation / contrast sets §6.5 | `roles/develop_option.py` (one role = N lens-panelists: mvp/risk/reuse/framework/radical) + `roles/score_options.py` (the scoring reduce) · `run_items`+`run_reduce(mode="role")` — ⑩ option-panels, verified present | ✅ | ✅ |
| 8 | Decision ledger / assumption shelf / missing-info map §21/§8 | adjacent substrate exists: `runtime/governance.py:78 class Inbox` (+ `:153 surface_review`, `:163 set_status`, `:184 resolve`) · `runtime/suite.py:6273 inbox_lanes` · `:6320 coa` (decision-compiler). **No FIRST-CLASS Decision-Ledger / Assumption-Shelf / Missing-Information-Map OBJECTS** (grep: none) | ✅ | ⚠️ **🟡** |
| 9 | Spec compilation (state → handoff) §23/§8 | ⑦ spec-compiler chain present + complete: `roles/decompose_seed.py` · `roles/expand_criterion.py` · `roles/ground_criterion.py` · `roles/triad_synth.py` (+ `roles/judge.py`) · `runtime/suite.py:858 save_cascade` / `:885 run_cascade` (the GROUP-N runner threads step→step) | ✅ | ✅ |
| 10 | Event/graph/vector/doc store + embedding ladders §17 | code exists: `store/fs_store.py:426 append_event` (event) · `:325 save_graph`/`:340 load_graph` (graph) · `store/vector_index.py:64 build_index`/`:142 query_index`/`:175 index_staleness` (vector) · `:215 set_ref` + `objects/` CAS (doc) · `runtime/cognition.py:376 embed_corpus_to_spaces`. **BUT the `repo` space is UNPOPULATED** — `list_corpus(project='company')`→0; the ① ingest has never run on the repo | 🟡 (① embeds) | 🟡 |
| 11 | Memory (preference/rejection/project/decision) §16 | ③ transcript-miner present: `roles/mine_exchange.py` + `roles/judge_mining.py` (+ corpus spaces via `capture_corpus`). **⑨ durable cross-session memory ABSENT** — no `session_memo`/`durable`/`memo` role in `roles/` (verified: NONE) | 🟡 | 🟡 |
| 12 | Execution handoff → downstream autonomous workflow §23/§26 | THE WIRE, present + proven: `runtime/suite.py:7337 surface_build_intent` · `:7921 dispatch_decision` · `runtime/implement.py:473 drive_dispatchable` (decision→`claude -p`→verify→`implemented`+surfaced) · `:9831 _self_build_commit` (the git checkpoint) | ✅ | ✅ |
| 13 | The live generative surface itself §19/§11/§12 | the FE/RHM organ exists as **fixed React regions** (`canvas/app/src/regions/RhmChat.tsx`, `Inbox.tsx`, `Review.tsx`, `Walkthrough.tsx`, `CognitionView.tsx`) — the **EXTENSION BASE**, not the generative surface. §19 demands "**not** a static app shell with fixed pages… a live adaptive surface" rendered from project-state + schemas; grep for generative/schema-render in `canvas/app/src/` → **NONE**. The regions are the thing to EXTEND (per the FRAME's own note), not partial-build credit | 🔴 the build | 🔴 |

*(Section-number note: the FRAME map's "§8/§9/§16/§18/§20…" labels are LOOSE — e.g. it cited "§16" for
the swarm, but the swarm is §20 Worker Architecture; §16 is the Memory Model. This is a notes-line
inaccuracy in the FRAME doc, **not** a status correction — I mapped each row by its CONTENT to the real
Surface section and grounded the downstream cite. Listed here only so the next agent isn't confused.)*

---

## THE THREE FRAME-MAP ROWS THAT WERE WRONG (overclaimed ✅ → actually 🟡)

1. **Row 3 — "Tags/counts/observations NOT confidence" marked ✅ "a LAW already (no-confidence-value)."**
   ⚠️ **OVERCLAIM → 🟡.** The marks/corpus SUBSTRATE is ✅ (`store/fs_store.py:677 append_mark`,
   `runtime/suite.py:9151 mark`). But no-confidence is **NOT enforced** — `mark()` (suite.py:9151)
   takes extra `**fields` that "splat through to the open mark record," and its own docstring lists
   `confidence` as one of them (`value/confidence/source_pass/evidence/…`). So the substrate ACCEPTS a
   confidence value; no-confidence is a **convention** (code comments + the wire-tests' repeated "no
   confidence value anywhere" assertions in `tests/wire_acceptance.py`/`wire_harden_acceptance.py`,
   and the deterministic `implement.py:410` gate), **not a schema-rejected field**. Convention-not-law →
   🟡. (Also note: `tests/cognition_governance_acceptance.py` — the 42/42 floor scan — asserts the
   floor invariant, NOT a no-confidence law; grep for "confidence" in it → none.)

2. **Row 8 — "Decision ledger / assumption shelf" marked ✅.** ⚠️ **OVERCLAIM → 🟡.** The Surface names
   FIRST-CLASS objects (§8.14 Decision Ledger, §8.15 Assumption Shelf, §8.16 Missing-Information Map).
   Grep for `decision.ledger`/`assumption.shelf`/`missing.information.map` in `runtime/*.py` → **none**.
   What exists is ADJACENT substrate the objects could be built ON (the inbox + governance + coa,
   `runtime/governance.py:78`, `runtime/suite.py:6273`/`:6320`) — not the named objects themselves. 🟡.

3. **Row 6 — "Anchor/preference/rejection extractors" marked "✅ pattern."** This was HONEST about being a
   pattern not a build — but the GROUNDED status is best read as **🟡** (the lens-rides-in-input pattern
   is ✅, but the §20.4 extractor ROLES are 🔴-absent). Not strictly "wrong," but the table's split
   makes the missing half explicit so it lands in the backlog.

**No FRAME-map 🔴 was found to actually exist** (no under-claim corrections) — and critically, the FRAME's
🔴 row 13 (the generative surface) **STANDS**: the existing canvas regions are fixed React components (the
extension base), NOT the schema-rendered generative surface §19 demands. Down-grading row 13 to 🟡 on the
strength of "RhmChat/Inbox exist" would be the green-paint this lane exists to prevent — the FRAME author
already knows the RHM organ exists ("**EXTENDS** the RHM organ, not a 2nd renderer"); that is the
thing-to-extend, not evidence of a partial build.

---

## THE GROUNDED BUILT-% (computed from the cites, not a lean guess)

Method, stated transparently so it reads as derived: ✅ = 1.0 · 🟡 = 0.5 · 🔴 = 0.0, over the **13 rows**
of the grounded table (the FRAME's 12 + the generative-surface row split out, matching the FRAME's own
12-row map which already listed the generative surface as its own line — 13 grounded rows because row 6
carries both a ✅-pattern and a 🔴-roles half; I score it 🟡=0.5 to avoid double-counting).

| status | rows | weight each | subtotal |
|---|---|---|---|
| ✅ EXISTS | 1, 2, 7, 9, 12 (5 rows) | 1.0 | 5.0 |
| 🟡 PARTIAL | 3, 4, 5, 6, 8, 10, 11 (7 rows) | 0.5 | 3.5 |
| 🔴 NET-NEW | 13 (1 row) | 0.0 | 0.0 |
| **total** | **13** | | **8.5 / 13 = 65%** |

**GROUNDED built-% ≈ 65%** (8.5 of 13), versus the FRAME's lean **~80%**. The gap is the seven 🟡 rows
each carrying a real missing half + the one hard 🔴. **5 rows are genuinely ✅** (the swarm fan, the
arbiter/jury, option-panels, the spec-compiler, the wire) — the spine the COMPOSITIONS describe IS real
and reusable. The headline correction: **~65% built, not ~80%; the generative surface (§19) is the hard
🔴; the remaining gap is seven specific organs each half-built.**

---

## THE PRECISE NET-NEW LIST (the real build backlog — what the Surface needs that the engine does NOT have)

Assembled from every 🔴 row + the missing half of every 🟡 row. This is the deliverable Tim uses to steer.

**The headline (🔴):**
1. **The schema-rendered generative surface itself (§19 / §3.3 / §3.7).** The live adaptive surface that
   renders from project-state + active schemas — typing/clicking/rejecting AS the reasoning ("the screen
   is part of the conversation"). The existing canvas regions (`RhmChat`/`Inbox`/`Review`/`Walkthrough`/
   `CognitionView`) are the **extension base** to build it ON (coordinate with the guided-review FE lane),
   **not** the surface. This is the single biggest net-new — the product face.

**The missing halves of the 🟡 rows:**
2. **The §20.4 extractor ROLES** (row 6): anchor / entity / time / preference / rejection / constraint /
   contradiction / missing-field extractor roles — authored via `create_role` over the existing
   lens-rides-in-input pattern (the pattern is ✅; the roles are 🔴). These are DIRECT declarative-authoring
   builds (no operator gate), each one `create_role(spec)`.
3. **⑨ durable cross-session memory** (row 11): a `session_memo` role + the embed-into-`space="history"` +
   the boot-sequence retrieve-over-it. **Honest reuse-decision owed to Tim** (per COMPOSITIONS ⑨): this
   OVERLAPS the episodic-memory plugin + the file-memory at `~/.claude/projects/-home-tim/memory/` — the
   right build is "extend, not parallel," and WHICH it complements is Tim's call.
4. **Progressive-type-resolution WIRING** (row 4): the §11 foreground/supporting/rejected/resolved
   schema-state machine + stage driver over the file-discovered registries (the registries are ✅; the
   resolution machine is 🔴).
5. **Schema → UI render** (row 5): the §18→§19 path that turns an active schema's state into rendered
   components (the declarative-panel renderer `PanelView.tsx` is fixed-JSON-fields, NOT schema-state→UI).
6. **First-class Decision-Ledger / Assumption-Shelf / Missing-Information-Map objects** (row 8): §8.14–
   8.16 as real objects, built ON the inbox/governance/coa substrate (the substrate is ✅; the named
   objects are 🔴).
7. **no-confidence as an ENFORCED invariant** (row 3) — IF Tim wants it as a law: today `mark()` accepts a
   `confidence=` field; making no-confidence a hard schema rejection (not just a tested convention) is a
   small net-new guard. Flagged as a Tim-decision, not assumed.

**The net-new ACTION (not code — running what exists):**
8. **Run the ① repo-exocortex ingest on the actual repo** (row 10). The store/vector/embed CODE is all ✅
   (`build_index`/`embed_corpus_to_spaces`/`query_index`/`index_staleness`), but the `repo` space is
   **empty** (`list_corpus`→0) — it has never been populated. The ingest is a real net-new ACTION that
   then GROUNDS every downstream composition (②③④⑨⑫ read its corpus). Note: the existing
   `roles/repo_digest.py` is the REUSE target for the digest step (COMPOSITIONS ① names
   `digest_for_index`/`verify_digest`, neither of which exists — `repo_digest.py` is the built equivalent;
   do NOT fork it).

---

## VERIFY-BY-USE (how every cite was confirmed)

Every ✅/🟡 cite was resolved to a real `file:line:symbol` via `grep`/`Read` on `~/company` this session
(the corpus being empty, I degraded to direct grep — clean, as the lane permits). Spot-evidence of the
load-bearing checks:
- `mark()` confidence param: READ `runtime/suite.py:9151-9166` — extra `**fields` (incl. `confidence`)
  splat into the record → row 3 is 🟡 (substrate accepts it; no-confidence is convention).
- `session_memo` / durable-memory: `ls roles/ | grep` → **NONE** → row 11 ⑨ is 🔴.
- generative surface vs fixed FE: `grep -ril generativ|schema.render canvas/app/src/` → **NONE**;
  `PanelView.tsx:1` self-describes as "a brain-authored declarative panel" (fixed fields);
  `RhmChat.tsx:1` is "carved from App.tsx" (a fixed region) → row 13 🔴 stands.
- corpus empty: `mcp__company__list_corpus(project="company")` → `{total:0}` → row 10's spaces unpopulated.
- the spine ✅ rows: `grep -nE 'def (run_items|run_reduce|run_role|run_chunked)'` →
  `cognition.py:1085/1769/203/1444`; `save_cascade`/`run_cascade` → `suite.py:858/885`; the wire →
  `suite.py:7337/7921` + `implement.py:473`; SlotBudget → `cognition.py:708/725`.

**Built-% is computed from the table cites (8.5/13 = 65%), not asserted.** No code was modified. The FRAME
doc was cross-referenced, not edited.
