-passed + render-for-cognition on both faces) — overall-done blocks on it; design-critic +
  render-for-cognition + both faces + surfaced-for-review.
- **Don't:** mint a `coherence://` scheme; don't discharge the burn-down as a CLI; don't hand the FORM off as a
  prose pointer (use the enforced Gap).

### B-3.2 · Unify the DISPOSITION system that exists TWICE in embryo (SEAM F) — with C9.4 anchors if it lands a registry
- **Lands:** `_ORPHAN_ROUTES` hardcoded dict **and** `governance.POLICY` (AUTO/SURFACE/CONFIRM/LOCKED) → **one**
  disposition mechanism.
- **Reuse seam:** pick the survivor and absorb the other (the disposition overlay + governance posture are the
  two embryos).
- **★ C9.4 anchors (the prior draft named none here, unlike B-0.2/B-2.3/B-3.1):** unifying `_ORPHAN_ROUTES`
  (a hardcoded dict) into rows almost certainly LANDS/MODIFIES a disposition-posture registry — if so it ships its
  **three anchors** (`runtime/<reg>.py` + `<reg>/AGENTS.md` drift home + `tests/<reg>_acceptance.py`) + the
  self-description update, or `drift_acceptance` fails loud. If the unification genuinely adds no registry, state
  that explicitly.
- **Preserves:** AUTO/SURFACE/CONFIRM/LOCKED preserved as the unified vocabulary; `_ORPHAN_ROUTES` migrates into
  finding-records (the catalogue becomes the first findings — the recursion).
- **Verify-by-use:** an orphan-route that was an `_ORPHAN_ROUTES` entry resolves through the one disposition path
  with the same posture; if a registry landed, its three anchors present + `drift_acceptance` green.
- **Don't:** leave both running with a bridge — the union is one, never invent a third; don't land a registry
  without its anchors.

### B-3.3 · The COMPANY substrate engine — GENERALIZE DNA's cut, never adopt it (SEAM D); the cross-repo READ is R-DNA
- **Lands:** the company's canonical substrate engine, pointable at any project (project-registry +
  global/project/user scope). DNA's proven cut is the **SEED + reference**.
- **Reuse seam:** generalize the engine pattern; the census feeds **BOTH** the structural substrate (the
  address-registry / typed graph) AND the semantic corpus (the `vec://<source>#space=<projection>` embeddings) —
  two lenses on the SAME addressed units (SEAM D).
- **★ Label + cross-repo discipline:** DNA's numbers (621 addrs / 1,050 edges / 22 types / 14 ghost nodes) are
  **DNA-self-reported, uncited to any live Company file**, in a **separate repo**
  (`/home/tim/repos/counterpart/design/`). `dna/types.json` + `substrate-assemble.py` are **PHANTOM in
  `/home/tim/company`** (**Verified**). **R-DNA (a reconcile, not a build input): the cross-repo dependency —
  this build READING counterpart/design as seed + as a second project to census — is an OPEN cross-boundary
  decision** (found-elsewhere ≠ replacement). Confirm with operator/lead whether counterpart/design is an input
  this build reads, an ancestor, or a layer the union absorbs — BEFORE relying on it as "census a second project."
- **Preserves:** DNA remains architect-of-record for her instance; her design repo becomes one project the
  company's substrate covers (once R-DNA confirms the relationship) — not superseded.
- **Verify-by-use:** the company engine censuses a project (e.g. the company repo) and produces the structural
  graph + feeds the corpus — without touching DNA's instance; the cross-repo relationship recorded (R-DNA).
- **Don't:** build the company's substrate ON DNA's instance or into the counterpart repo; and don't treat the
  cross-repo READ as a settled build input — it is a reconcile.

---

# THE ACCEPTANCE TEST FOR "THE UNION IS REAL" (a ready loop-prep criterion)

The one query that makes it a union (synthesis §3) — *board items of type `request`, with a `responds_to` edge
to project P, modified since T, ranked by cosine to query-vector Q*:

```sql
SELECT i.address, 1 - (v.vector <=> :q) AS score
FROM board_items i
JOIN edges   e ON e.source = i.address AND e.kind='responds_to' AND e.target=:project
JOIN vectors v ON v.source = i.address AND v.space='history' AND v.emb='pplx'
WHERE i.type='request' AND i.modified_at >= :t
ORDER BY score DESC;
```
If the migration serves this, the union is real. If you can't write it, the union is hollow. (Today this is the
read-time-fold over the event log + the `(space,emb)`-filtered cosine — the SQL is the *later* backend's form of
the **same** query; the address never changes.) **The migration is ORDERED + ext4-pinned + operator-CONFIRMED
before the first real-data mutation + operator-rollbackable per step, NOT runtime-fs-fallback:** 1 Seam (B-0.7) →
2 local PG+pgvector stand-up **on ext4 (`~/...`), NEVER `/mnt/c` — fail-loud if the data dir resolves under
`/mnt/c` (Rule 5)** → **[operator SURFACE + CONFIRM before any real-data mutation — Rule 7]** → 3 Shape-B
JSONL→tables → 4 Shape-A dirs→upsert → 5 vectors → 6 concurrency swap (the `append_event` monotonic-unique
seq→SERIAL, load-bearing for the SSE cursor) → 7 CAS blobs → 8 BGE-backup decision → **[post-cutover: the fs
source is decommissioned via operator CONFIRM, OR retained read-only with PG the single authority — no silent
dual-authority, no silent delete (Rule 7)]**. ✅ each step rollbackable-to-fs by use; the ext4 refusal + the
step-3 operator-CONFIRM gate present; **AND a fault-injection test: kill PG mid-read → loud failure (Notice+Gap),
NOT a silent fs read.** (Sized on STORE0's LIVE full re-census — no doc-number; the prior "1,068" had already
drifted to 1,069 live, which is why the criterion forbids trusting any written count.)

---

# RECONCILE-GATES (R-*) — sibling-stream reconciles — LEAD/FABRIC-OWNED, NOT Tim (the SCAN-BEFORE-BUILD law)

> Per THE-ONE-SYSTEM's LAW: any plan made WITHOUT the full-scope scan WILL FAIL. The scan is DISTRIBUTED across
> the fabric (each stream deep-scans its own project + posts a synthesis; the lead assembles). These are
> resolved ancestor/live/distinct-seam **via the channel**, never routed to Tim, **each backed by a DURABLE
> artifact (a channel-posted synthesis + /or a decision row), not a prose tag.** The interface/FORM build is
> GATED on them. (These mirror Group RECONCILE / RCN1–RCN7 in the criteria.)
>
> **★ REQUIRE-vs-ASSERT + coordination-window (carried from criteria PART 0).** Where a B-* criterion reads
> "CONVERGES onto X (R-…)" while the R-gate is still open, that criterion is **CONDITIONAL — GATED, not
> built-to** (build the R-independent backend half; the convergence half lands after the gate records). And if a
> sibling synthesis is not posted within the coordination window, the lead records a **PROVISIONAL decision from
> this build's own scan** (fail-loud Gap) so the FORM build proceeds — never an indefinite stall.

- **R-REGISTRY-GEN · `registry-generation/` — ONE pipeline at TWO granularities (= criteria RCN1/REG6).** `build-prep/registry-generation/COORDINATION.md` builds an address registry via two parallel loops (guided-review [M] + cognition [C]) — the SAME address registry PART 1 designs. **The synthesis frame (line 240): registry-generation (UI-element grain) + the substrate census (file grain) are TWO PASSES OF ONE PIPELINE at two granularities — not two pipelines to bridge, not merely "pick ancestor or live."** *Resolves when:* the lead/fabric records the one-pipeline-two-grain recognition (converged onto ONE engine), artifact-backed. **NEVER two forks of one registry.**
- **R-INST · `instrument-surface/` + `universal-projection/` — the instrument FORM seam, handed off as ENFORCED Gaps.** Both build the seed-equation instrument (wheel/lattice, the operator surface loop, the equation audit). *Resolves when:* recorded (artifact-backed) — PART 6 here is the BACKEND face (engine reuse + registry-driven rendering); those streams own the FORM/operator-surface face (design-critic + render-for-cognition + both faces). **The instrument FORM (INST1-4) is handed to them as ENFORCED system-memory Gap rows** (`return-when` = the owning stream's FORM is ✅ on both faces) — overall-done BLOCKS until those Gaps close; never a prose pointer, never silently dropped.
- **R-SELFBUILD · `self-build-surface/` + `front-interface/` — the keystone seam.** `self-build-surface/GROUNDED-MAP.md` already maps the click→talk→generate→writeback→re-render circuit (built legs verified across the fabric); `front-interface/SPEC-direction-to-generate-wire.md` specs the one unbuilt rung. *Resolves when:* recorded — the ACT keystone (B-2.x/LENS3) CONVERGES onto that circuit (the generate-step is the same rung, brain via #71, through the operator-gated wire), NEVER a second self-build loop.
- **R-LIVE · `live-resolution-surface/` — the resolution seam.** Designs the live intent→address resolution path the RES group designs. *Resolves when:* recorded — RES1/B-0.4b (resolver-collapse) is the backend; live-resolution-surface owns the live-intent FORM.
- **R-71 · `model-routing-unification/` (#71) — the co-owned brain.** RES3, B-2.2/B-2.5 (cc_launch model-routed), LENS3 (build-brain) depend on #71. *Resolves when:* #71's per-role model resolution is wired where these consume it, attributed to #71, never silently claimed.
- **R-COHERENCE · `guided-review-surface/` + `coherence/` — the finding/review seam.** *Resolves when:* recorded — B-3.1 emits findings to the event log; guided-review renders them (the FORM half) — one finding substrate.
- **R-TRIGGER-CREATE · `create(kind='trigger')` eligibility (was G-TRIGGER-CREATE).** A trigger row is pure data → looks Tier-B-eligible, **but** `mode_detection_rules` is also pure-data and was kept OFF `_CORPUS_REGISTRIES` (counter-precedent). *Resolves when:* the lead/fabric resolves WHY MDR was kept off the create-path. The MCP tool (B-2.6) ships regardless; `create_trigger` is the conditional add. (Lead/fabric, not Tim.)
- **R-DNA · the cross-repo READ of `counterpart/design/` (LENS2/B-3.3).** *Resolves when:* operator/lead confirms whether counterpart/design is an input this build reads, an ancestor, or a layer the union absorbs (found-elsewhere ≠ replacement) — before relying on "census a second project."
- **R-COVERAGE · `coverage/` (Task #74, = criteria RCN7).** A COMPLETED open per-unit coverage sweep already exists (`build-prep/guided-review-surface/findings/coverage/`, incl. `substrate.md`; + `trigger-system/COVERAGE-RUNBOOK.md`) — coverage was the ONE live stream the prior draft gave no reconcile, so B-1.0 was re-deriving completed work (the parallel-build the union forbids). *Resolves when:* recorded (artifact-backed) — B-1.0 ingests the existing sweep, marks it ancestor/live, and EXTENDS it (converges), never re-derives from zero. Task #74 named co-owned, exactly like #73/trigger-system.

**Reclassified OUT of the gate-pile (the prior draft's error — these were developer calls wrongly routed to
Tim; now LEAD DECISIONS, built, each artifact-backed):** G-GRAMMAR → B-0.5b (declare recursive, build it) ·
G-RESOLVER → B-0.4b (collapse `resolve_scope`) · G-FORM-MATCH → B-1.4 (Option C) · G-EVENT-TAXONOMY → B-2.3
(A2 now, A1 upgrade) · G-LIFTER-AUTHOR → B-1.4b (selector-data/extract-code + complete-per-engine parser) ·
G-EDGE-LAW → criteria EDGE1/EDGE2 (family-only + named-distinct, a wrong-abstraction correction the lead makes) ·
ui:// diff-gate → criteria REG5 (DERIVE one source, kill the diff).

**Also corrected (not a gate, a content flip): SCHEMES → DERIVED from a `scheme/` registry (B-0.2)** — the prior
draft's "keep-the-literal + side-table" left a two-place hand-edit; the REG5/`suite.py:33` derivation precedent
makes `SCHEMES = tuple(scheme_registry)` the registry-is-truth move (import shape preserved by derivation). And
**ID2 (channel member) is a LEAD dual-face reconcile, not a forced Tim binary** (multi-job-elements: a member IS
both a person-handle AND a session; declare the join; only a residual canonical-identity choice may reach Tim).

**The genuine Tim decisions (the only ones that reach Tim, in DECISIONS-FOR-TIM, at his altitude — each surfaced
ONLY after the lead has first modelled "can it be BOTH?"):** file://-vs-cas identity-meaning (after the
both-with-a-derivation model) · the RESIDUAL channel-member durable-referent (only if it survives the lead's
dual-face model — ID2 is a lead reconcile, NOT "person or session?") · cluster stable-vs-query-or-both · admit/
carve/mix the event tier (Shape-B) · the emergent form taxonomy from B-1.0's coverage (COV2). **That is the whole
Tim-gate set — ~3 + a residual + the taxonomy, refined, not ~13.**

---

# THE BUILD ORDER (one line)

**RECONCILE-FIRST for dependent parts (R-* via the fabric — gates the FORM/interface build; coordination-window
provisional if a sibling is silent)** ‖ **Phase 0 foundations + COV1 PULLED ALONGSIDE**
(B-0.7 storage seam [LEAD DELIVERABLE #1, ext4 + distinct-method widen] · **★ B-0.5b recursive vec grammar FIRST
[synthesis line 66: before flattening SCHEMES]** → B-0.2 SCHEMES DERIVED from a `scheme/` registry [LEAD FLIP,
artifact-backed; vec/cluster nesting rows fail-loud until B-0.5b green] → B-0.3 9-resolvable table dispatch
[regression-diff] → B-0.1 `_RESOLVABLE` drift-guard [GREEN-on-unmodified, a guard not a fix] → B-0.4 parsers
[grep-first] · B-0.4b collapse `resolve_scope` · B-0.5 recognisers→DATA [predicates only] · B-0.6 scope base
[forms pilot + roles MIGRATED in-scope] · **B-1.0 OPEN coverage CONVERGING onto the existing sweep (R-COVERAGE),
alongside the foundations**) → **propose taxonomy to Tim (COV2) — a fail-loud predecessor of all effort-routing**
→ **Phase 1 coverage-useful** (B-1.1 policy passthrough [regression-diff] → B-1.2 bucket-by-band [on the COV2
emergent taxonomy, fail-loud before COV2] → B-1.3 context/output selectors + effort-band ON `GenerationPolicy` →
B-1.4 create_form [data-AST, Option C, LEAD] · B-1.4b lifter producer-contract + complete-per-engine parser
[tree-sitter NOW, no silent under-extraction, LEAD] → B-1.5 lifter selector → B-1.6 lifter attach → B-1.7 lifter
files [TS via in-process tree-sitter] + inbound-links) → **Phase 2 trigger** (B-2.1 structured_output capture
**before, per-file across the 3 paths** → B-2.2 cc_launch [operator-gated] → B-2.3 triggers on the SHARED base
[LEAD] + event-kind A2 [LEAD] → B-2.4 board.filed + responds_to → B-2.5 driver [EXTEND activation's tick, dormant,
loop-guard, dispatch-forge-rejected, **structural-gate-independent-of-arming proven by use**] → B-2.6 triggers
MCP tool) → **Phase 3 union seams** (B-3.1 coherence-as-lens [FORM→guided-review as enforced Gap] → B-3.2
disposition union [C9.4 anchors if a registry] → B-3.3 generalize-DNA-engine [R-DNA reconcile first]) → **VERIFY
by use** (incl. `drift_acceptance` + the dispatch-forge-rejected + the arming-independent gate + the
regression-diffs + the ext4 refusal + the Rule-7 confirm + the kill-PG fault test) + run the converged coverage →
the union acceptance query → the map → Tim (the ~3+residual+taxonomy DECISIONS-FOR-TIM, at altitude). **★
OVERALL-DONE is BLOCKED until RCN2/R-INST (+R-COHERENCE) record AND the handed-off FORM Gaps (INST1-4, LEG1-2,
the coherence burn-down, the LEG1 listings) return design-critic + design-lint + render-for-cognition on BOTH
faces; until then the status is FUNCTION-complete / FORM-pending-external — NEVER done.**