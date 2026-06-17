# Substrate Unification — Implementation Guide (the HOW for the loop)

> Loop-prep doc 2 of 3. **These docs live at `/home/tim/company/build-prep/the-one-application/`.** Pairs with the
> **Research Synthesis** (`UNION-RESEARCH-SYNTHESIS.md` — the master; PARTS 1–6, the verified anchors, the
> feasible/blocks arbitration) + the **CANONICAL trigger-system pillar designs**
> (`../trigger-system/DESIGN-forms-built.md`, `DESIGN-lifters.md`, `DESIGN-trigger-registry.md` — these are the
> source set; `../trigger-system/DESIGN-SYNTHESIS.md`'s lifter=predicate crux is **PARTLY SUPERSEDED** by the
> verified lifter≠predicate correction in B-0.5/B-1.4b — cite the pillars, not DESIGN-SYNTHESIS, for the
> recogniser split) + the orientation set (`THE-ONE-SYSTEM.md` · `FORMS-ARE-PLACEHOLDER.md` ·
> `SUBSTRATE-IN-THE-COMPANY-REFLECTION.md`). The criteria doc (`COMPLETION-CRITERIA.md`) uses an identical source
> set. This doc is the build sequence, the dos/don'ts, and the file map. **It references the synthesis for the
> WHY + the file:line evidence — it does not duplicate it.**
>
> **Streams reconciled before this build (the SCAN-BEFORE-BUILD law).** This build does not decide the union
> alone. The sibling streams that are facets of the one application — `instrument-surface/`,
> `universal-projection/`, `self-build-surface/`, `live-resolution-surface/`, `front-interface/`,
> `guided-review-surface/`, `registry-generation/`, `model-routing-unification/` (#71), `trigger-system/` (#73),
> `coherence/`, **`coverage/` (#74 — the COMPLETED `guided-review-surface/findings/coverage/` sweep)** — are
> reconciled in the **RECONCILE-GATES (R-*)** section + Group RECONCILE (criteria PART 0, RCN1–RCN7).
> The reconciles are **lead/fabric-owned, coordinated via the channel, each backed by a DURABLE artifact** —
> never routed to Tim. The build is gated on them, with a coordination-window return-condition so a missing
> sibling synthesis → a provisional decision from this build's own scan (fail-loud Gap), never an indefinite stall.
>
> **Epistemic posture (Tim's bar, carried from the synthesis).** Every claim below is labelled **Observed**
> (seen in code, no execution) · **Inferred** (pattern-match, unverified) · **Verified** (confirmed by
> execution/test). Where the synthesis labelled something Inferred or uncited, this guide preserves the label —
> it does **not** launder it into present-tense fact. **A source-line that *states* a thing (a docstring/comment/
> shared call-site) is a code-read → Observed, never a by-use Verified.**

---

## THE ONE LAW THAT GOVERNS THIS WHOLE BUILD — unions-not-bridges (ABSORB, don't connect)

The synthesis's corrected thesis is **not** "everything collapses by adding a row." It is:
*one address **syntax** is the right spine + a **FEASIBLE set** of grammar-as-data / registry-base /
storage-seam / forms-via-RULE_OPS / one-projection-engine moves — bounded by a set of **BLOCKS that are
decisions, not bridges** (none dissolves by adding a row).*

So this guide splits **hard** into three tiers, and a build-worker treats them as different things:

- **BUILD-CRITERIA (B-*)** — the feasible set. These get built, verified by use, committed. **This includes
  every developer/architecture call the lead has DECIDED** (the lead picked it, coordinating via the fabric;
  the criterion records the decision and is built — see the next bullet).
- **TIM-DECISIONS (T-*)** — the small set of genuine **direction/meaning** choices only Tim can make,
  translated to his altitude. These live in the criteria's **DECISIONS-FOR-TIM** section. A T-* criterion stays
  🔴 until Tim records the meaning; a row-add/migration-size through it must **fail loud**.
- **RECONCILE-GATES (R-*)** — the sibling-stream reconciles. **Lead/fabric-owned, NOT Tim.** Each is resolved
  ancestor/live/distinct-seam via the channel before the FORM/interface build proceeds.

**WHO decides is the cut (not-a-developer + coordinate-via-fabric).** A code-pattern / architecture choice is
NEVER routed to Tim (he is not a developer; asking him is forbidden AND it parks decidable work behind a false
gate — a double violation). The lead decides those NOW (coordinating with the ~10 channel members) and surfaces
only the OUTCOME for Tim in human terms. Only direction/meaning reaches Tim. **This is the correction of the
prior draft, which mislabeled ~7 developer calls as "needs-Tim gates."**

**Absorb, don't connect** is the concrete reading of every Don't here: ride the ONE event log (don't bolt a
second bus), read-time-fold (don't fork a parallel store), one scope base (don't copy the filter into six
registries — and MIGRATE `roles.mode_scope` onto it in-scope, don't leave it on a copy), one disposition system
(don't invent a third), one projection engine (don't adopt DNA's instance — generalize it), one `ui://` source
(DERIVE the other, don't diff-gate two authorities), **one `SCHEMES` source — DERIVE the importable tuple from a
file-discovered `scheme/` registry (`SCHEMES = tuple(scheme_registry)`), don't keep a hand-edited literal as the
authority** (the same derive-discipline; the prior draft's "keep the literal, add a side-table" left a two-place
hand-edit), one trigger registry mechanism (reuse the shared base, don't clone a bespoke class). When two
mechanisms exist in embryo, the union is to **unify them into one**, never to wire a bridge between two survivors.

---

## Standing laws (bind every build step)

Registry-is-truth / **no-hardcoding** (a new form/lifter/trigger/scheme is a FILE or a row, never a code
edit — including `SCHEMES`, now DERIVED from a `scheme/` registry, B-0.2) · **additive** (optional fields default
to the current behaviour; bump schema_ver; never break the contract spine — Rule 1; the importable name shape is
preserved by DERIVATION, not by keeping a literal) · **fail-loud** (no silent no-op, **no silent runtime
fallback**, **no silent under-extraction** — a lifter that cannot extract a construct emits a Gap, never silently
omits — surface a Notice + record a Gap) · **reuse-don't-parallel** (extend the ONE mechanism / the shared
registry base; never stand up a second fan/store/bus or clone a bespoke registry class) · **the floor** (a
parse/lift is a pure in-process READ — no resolve/dispatch) · **storage-on-ext4 (AGENTS.md Rule 5)** — any DB
data dir (PGDATA / container volume) lives on ext4 (`~/...`), NEVER `/mnt/c` (WSL fsync corrupts DBs); a
`/mnt/c` data dir fails loud at stand-up · **Rule-7 confirm-on-real-source-data (AGENTS.md Rule 7)** — anything
irreversible touching real source data (the migration, a second-project census, the fs-source disposition) is
SURFACED + operator-CONFIRMED BEFORE the mutation; rollback is recovery-after, not the confirm-before gate · **the
operator-gated build wire (C9.2)** — no role/rule/trigger/driver/cc_launch/MCP path may emit
`resolve`/`approve`/`dispatch` or launch `claude -p` by construction; a build-dispatch routes
`decision.surfaced_for_review` → operator `resolve_surfaced` → `dispatch_decision` (which enforces its gates +
refuses a double-launch); the structural gate holds INDEPENDENT of arming (prove by use, not by "the driver is
dormant"); **built-not-armed (env-gated dormant) is a TIMING gate ON TOP of this, never a substitute** · **C9.4
three-anchor + self-description** (every net-new registry ships `runtime/<reg>.py` + a `<reg>/AGENTS.md` (or
module AGENTS.md) drift home + `tests/<reg>_acceptance.py`, AND every change updates `MAP.md`/`STATE.md`/the
module AGENTS.md via `refresh_self_description`; `drift_acceptance.py` + `cognition_governance_acceptance.py` fail
loud if missing — a registry without its anchors cannot reach green `company suites`) · **FORM is half of done
(Rule 9) — FIVE clauses** — any operator-facing surface passes (a) a SEPARATE design-critic, (b) a fail-loud
design-lint, on (c) BOTH faces (native desktop AND native mobile), (d) is surfaced for review
(`decision.surfaced_for_review`), AND (e) is **rendered-for-cognition (rule 13)** — SHAPE carries the information
(density/convergence/gaps read at a glance), not a wall-of-text/flat-list that passes a generic critic; the
implementer never self-grades FORM. **A FORM owned by a separate session is handed off as an ENFORCED
system-memory Gap row** (`return-when` = the owning session's FORM is ✅), never a prose pointer; overall-done's
machine check asserts those Gaps closed · **a "LEAD DECISION recorded" must EXIST as a durable artifact** (a
channel-posted synthesis + /or a decision/registry row) — a prose tag in this doc is NOT a recorded decision
(verify-by-use + channel-relayed-is-proposal); a build-worker that finds the tag but no artifact treats it as
not-yet-decided · **honest status — FOUR buckets** (✅ Verified · 🟡 Designed [no code] · 🟠 Built-unexercised
[code exists, never run by use] · 🔴 Gap/Broken); never collapse 🟡 and 🟠 (assume-more-work) · **verify-by-use**
(a criterion is done when the END-TO-END path runs against real data, not when "no error"; a code-read is never a
green) · claim a shared file in `WORK-SPLIT.md § CLAIMS` before editing it · `company suites` green (incl.
`drift_acceptance`) before any shared-file commit.

**Evidence labels are load-bearing.** Carry these into the build, never present them as fact:
- SEAM C "3-line fix" = **Inferred** (the *drop* is Verified; the *fix scope* is not). Verify before sizing.
- SEAM D DNA census (621 addrs / 1,050 edges / 14 ghost nodes) = **DNA-self-reported, uncited to any live
  Company file**, in a **separate repo** (`/home/tim/repos/counterpart/design/`). Re-verify before relying;
  the cross-repo READ is itself an **open cross-boundary decision** (found-elsewhere ≠ replacement — R-DNA).
- `resolve_model` (`model_routing.py:105`) = **defined, imported NOWHERE** (the "3 callers" are comments
  reading *"does NOT change today's firing"*). The "unwired" reading stands.
- **`_RESOLVABLE` is NOT out of sync (Verified this session).** `SCHEMES`=16; `resolve_address` has dispatch
  branches for exactly 9 (`run·cas·skill·context·session·cap·board·clone·mind`); `_RESOLVABLE`=those 9. It is
  the deliberate, correct mirror of which schemes have a resolver. The 7 absent RAISE **by design** (the
  documented extensible seam). **There is no drift and no bug** — the prior draft's "verified 7-out-of-sync"
  claim is the error; see B-0.1.

---

## File territory — parallelism for the loop

**File-disjoint → PARALLEL lanes (new files, each self-registers by drop):**
`scheme/*.py` rows (the new file-discovered scheme registry SCHEMES derives from, B-0.2) · `forms/*.py` ·
`lifters/*.py` · `trigger/*.py` rows · `board_edges/responds_to.py` · `nodes/cc_launch.py` ·
`runtime/triggers.py` · `runtime/trigger_driver.py` (or the activation-tick extension, B-2.5) ·
`mcp_face/tools/triggers.py` · the new `tests/*_acceptance.py` · each new registry's `<reg>/AGENTS.md` drift home.
(Event-kind validation = A2-in-place — a lead decision, see B-2.3; no `event_kinds/*.py` lane. Effort bands
ride `GenerationPolicy` additively — see B-1.3; no `effort_bands/*.py` lane unless a field genuinely cannot
live on a policy row.)

**Hot files → SERIALIZE + claim the window in `WORK-SPLIT.md`:**
`runtime/suite.py` (the capture wrappers, the discover lines, **`_CORPUS_REGISTRIES` — Task #59 is editing this
table concurrently (adding `minds`); ADOPT its row, don't clobber it; coordinate via the channel**, `create_*`) ·
`runtime/cognition.py` (`run_items`/`run_role` passthrough, `resolve_address`→`SCHEME_HANDLERS`) ·
`runtime/forms.py` · `runtime/lifters.py` · `runtime/rules.py` (RULE_OPS shape-ops) · `contracts/address.py`
(`SCHEMES = tuple(scheme_registry)` derivation + the `set==set` drift-guard, parsers — grep-first for any
existing mind/vec parser, incl. Task #59's minds work) · `runtime/territory.py` (`_RESOLVABLE` drift-guard) ·
`contracts/resolver.py` (Protocol widening to the live distinct-method surface) ·
`runtime/generation_policies.py` (the effort-band field, if it rides a policy row) ·
`runtime/session_supervisor.py` + `runtime/cc_clone.py` + `runtime/routine_runner.py` (the structured_output
capture — three coordinated files, one claim).

**NEVER touched by this loop:** `runtime/projection.py`/`bridge.py` engine internals (strongly-Observed-good,
reuse as slot — the FORM/render is owned by `instrument-surface/`+`universal-projection/`, R-INST) ·
`canvas/app/src/*` token/render (FORM/front-end — owned by the separate FE session, R-INST, **with a named
return-condition, not an unconditional park**). DNA's `/home/tim/repos/counterpart/design/*` is **read-only
reference** — never build into it (and the READ itself is an open decision, R-DNA).

---

# PHASE 0 — FOUNDATIONS (grammar-as-data + registry-base + storage-seam) — build FIRST

These unblock everything downstream. Nothing in Phase 1–3 ships until the foundations it depends on are green.
**Order correction (vs the prior draft):** the storage SEAM (B-0.7) is the uncontested lead deliverable.
**★ B-0.5b (the recursive vec grammar) lands BEFORE B-0.2 (SCHEMES-derive)** — synthesis line 66: the recursive
`vec://cluster://…#space=scale:…` grammar is "the single load-bearing thing the union design must model BEFORE
flattening SCHEMES"; the prior draft inverted this. Then B-0.2 (SCHEMES DERIVED from a file-discovered `scheme/`
registry) precedes B-0.3 (table dispatch) which precedes the B-0.1 drift-guard (which DERIVES from B-0.3's
`SCHEME_HANDLERS`). The vec/cluster `nesting`/`fragment_grammar` rows in B-0.2's registry are
fail-loud-unwritable until B-0.5b is green. The prior "derive `_RESOLVABLE` first, lead with it" was wrong on two
counts (it's a non-bug, and it can't derive from a field that doesn't exist until the registry lands).

### B-0.1 · `_RESOLVABLE` is a DRIFT-GUARD over the live dispatch set — NOT a bug fix (CORRECTED)
- **Lands:** `runtime/territory.py:32` (the 9-tuple) ← derives from the live `resolve_address` dispatch set
  (cleanly `tuple(SCHEME_HANDLERS)` once B-0.3 lands).
- **★ THE CORRECTION (Verified this session, the prior draft is wrong):** the prior draft called this a
  "verified 7-out-of-sync drift, the highest-value/lowest-risk move in the whole build." **It is a non-bug.**
  `SCHEMES`=16; `resolve_address` (`runtime/cognition.py`) has dispatch branches for **exactly 9**
  (`run·cas·skill·context·session·cap·board·clone·mind`); `_RESOLVABLE`=those 9. The comment at `territory.py:32`
  says so explicitly. The 7 absent (blob/vec/ui/code/exchange/file/project) **RAISE fail-loud BY DESIGN** — the
  documented extensible seam ("this RAISE is the extensible seam; add a branch when a resolver exists"). So
  `_RESOLVABLE` is the deliberate, correct mirror, not drift.
- **Do:** make `_RESOLVABLE` a DERIVATION from the **actual dispatch capability** — the schemes that have a live
  `resolve_address` branch (`tuple(SCHEME_HANDLERS)` after B-0.3) — and keep it as a **drift-guard**. *Because*
  the real invariant is "resolvable == has-a-dispatch-branch", and deriving it removes the chance a future hand
  edit diverges.
- **Don't:** derive from a settable `resolution_path` field — *because* setting that field on a deferred scheme
  ahead of its branch would make it appear resolvable and **convert a by-design fail-loud into a silent-success**
  (the exact risk). Don't call it a bug, don't lead with it.
- **Verify-by-use (falsify-first, GREEN-on-unmodified):** write `set(_RESOLVABLE) == {schemes with a live
  dispatch branch}` against UNMODIFIED code — it must come up **GREEN** (that green is the proof there is no bug
  today). Then keep it as the drift-guard: add a 10th scheme's dispatch branch → it auto-appears; remove a
  branch → it drops; a `_RESOLVABLE` hand-edit that diverges fails the guard loud.

### B-0.2 · `SCHEMES` is DERIVED from a file-discovered `scheme/` registry — `SCHEMES = tuple(scheme_registry)` (LEAD DECISION FLIPPED)
- **Lands:** a new file-discovered `scheme/<id>.py` registry (the AUTHORITY) + `contracts/address.py:116` where
  the importable name becomes `SCHEMES = tuple(scheme_registry)` (a DERIVATION, not a hand-edited literal) + a
  `set(scheme_registry) == set(SCHEMES)` fail-loud drift-guard.
- **★ LEAD DECISION FLIPPED (recorded — derive-SCHEMES-from-a-file-discovered-registry; the prior draft's
  "keep-the-literal, add-a-side-table" is REVERSED):** the prior draft kept the 16-scheme literal authoritative
  and added metadata that merely REFERENCES it, justified by "Rule 1 / import shape." **That is a FALSE
  DICHOTOMY — refuted by REG5 and by the live repo.** VERIFIED: `SCHEMES` is an OPEN, GROWING vocabulary
  EXTENDED IN PLACE — `contracts/address.py` carries **7 `"Adding X to SCHEMES is purely additive"` comments**
  (the manual-edit ritual; `grep -c 'purely additive' contracts/address.py` = 7) — the textbook flag-hardcoding
  anti-pattern. And the repo ALREADY derives a tuple-shape from a file authority: **`suite.py:33` projects
  `design/_system/addresses.json` INTO `UI_REGISTRY` rows** (derive-don't-mirror, in production). So a tuple can
  stay importable while DERIVED. The discriminator the floor states — "does adding a scheme require a code
  edit?" — was YES under the prior draft (edit the `contracts/` tuple); under the flip it is NO (drop a
  `scheme/<id>.py` row). The per-scheme fields `identity_class · resolution_path · nesting · fragment_grammar ·
  parse_fn · resolver_fn · granularity · status · desc` live NATIVELY on the rows (not a side-table); the
  prose-comment status becomes the row's `status` field. (This is a developer/architecture call the lead owns,
  not Tim's; the decision must EXIST as a durable artifact per the standing-laws floor. If derivation proves
  genuinely impossible it is argued AGAINST the REG5/`suite.py:33` precedent and recorded — never asserted via
  "import shape.")
- **Reuse seam:** the shared file-discovered registry mechanism (the `board_edges`-reuses-`relation_types`-class
  pattern) for the `scheme/` dir; the `suite.py:33` `addresses.json→UI_REGISTRY` projection as the derivation
  precedent. **C9.4: the `scheme/` registry ships its three anchors** (`runtime/<reg>.py` + `scheme/AGENTS.md` +
  `tests/scheme_acceptance.py`) + the self-description update, or `drift_acceptance` fails.
- **Preserves (by DERIVATION, earned by regression-diff not assertion):** the importable `SCHEMES` is
  byte-identical in CONTENTS to today (every `import SCHEMES` site unchanged) — capture every `SCHEMES` consumer's
  behaviour on UNMODIFIED code, apply the derivation, re-run, diff identical; the 16 schemes + their parse
  behaviour are unchanged; Rule-1 import shape held, Rule-2 additive.
- **★ ORDER GATE:** B-0.5b (the recursive vec grammar) lands FIRST; the vec/cluster rows' `nesting`/
  `fragment_grammar` fields are STRUCTURALLY un-writable (fail-loud) until B-0.5b is green (the row-add-ahead-of-
  the-proven-grammar RAISES, mirroring the row-add-before-Tim-decision fail-loud).
- **Verify-by-use:** a `scheme/<id>.py` row-drop makes a new scheme legal with NO `contracts/` edit, by use; the
  `set(scheme_registry)==set(SCHEMES)` guard green; `parse_address` of one address per scheme returns today's
  parse; `drift_acceptance` + `cognition_governance_acceptance` green with the `scheme/` anchors present.
- **Do:** carry `identity_class` + `resolution_path` as first-class row fields — *because* those decide unify-vs-block.
- **Don't:** add `channel`/`cluster` rows here yet — *because* they are T-* / lead-dual-face decisions
  (DECISIONS-FOR-TIM #2/#3, ID2 is a lead reconcile). The registry must be able to *hold* them; they are admitted
  only after the meaning/dual-face is recorded. And don't keep a hand-edited literal alongside the registry —
  that re-creates the two-place edit the flip removes.

### B-0.3 · `resolve_address` if/elif → `SCHEME_HANDLERS[scheme]` table dispatch — the 9 RESOLVABLE schemes
- **Lands:** `runtime/cognition.py` (`resolve_address` if/elif chain → a `SCHEME_HANDLERS` table).
- **★ LEAD DECISION (recorded, artifact-backed — table-dispatch-for-the-resolvable-9):** the per-scheme resolver
  functions already exist behind the if/elif; build the table ON them. `_RESOLVABLE` then = `tuple(SCHEME_HANDLERS)` (B-0.1).
- **Preserves (earned by REGRESSION-DIFF, not assertion — a "Preserves" prose line is a code-read, never green):**
  capture each of the 9 schemes' resolution on UNMODIFIED code, apply the table, re-run, diff identical;
  fail-loud on a non-resolvable/unknown scheme is unchanged (verify that path too).
- **★ HARD BOUND (unions-not-bridges):** the table is keyed on the **leading `scheme://`** and **cannot** parse
  the nested `vec://cluster://…#space=scale:…` key (**Verified**: `scale.py:34,282` produces it; `fs_store.py:920`
  is flat-concat). `vec`/`cluster`/`ui`/`code`/`file`/`project`/`channel` do **not** go in this table — they are
  handled by the recursive grammar (B-0.5b), the resolver collapse (B-0.4b), or the T-* identity decisions.
- **Verify-by-use:** resolve one address per resolvable scheme through the table == through the old chain, by use.
- **Don't:** "just split on the first `://`" to cover `vec://cluster://` — *because* that mis-keys it; the
  nested grammar is a declared recursive parser (B-0.5b, a lead decision), not a parse trick.

### B-0.4 · Consolidate sub-address parsers in `address.py` — GREP-FIRST (no second parser for one shape)
- **Lands:** `contracts/address.py` (alongside `parse_session_address`/`parse_clone_address`).
- **★ Grep-first (required):** BEFORE adding `parse_vec_address`/`parse_mind_address`, **grep
  `contracts/address.py` + Task #59's in-flight minds work for any existing mind/vec parser** — the file warns
  against two parsers for one shape (f1ade750's flag). Extend the one declared parser; never mint a second.
  (The file's own comment already anticipates `mind://`; #59 is minds-first-classness work — coordinate.)
- **Reuse seam:** build the new parsers ON the existing shape. Move the silent `_safe()` address→filename
  transform out of `fs_store` into `address.py` as a declared contract (synthesis §1.2).
- **Preserves:** existing parses unchanged; `_safe()` produces identical filenames (a relocation).
- **Verify-by-use:** round-trip each scheme's address through its parser; `_safe()` of a known address ==
  today's filename, by use; AND the grep-first confirmed no pre-existing parser to fork.

### B-0.4b · COLLAPSE the second resolver `resolve_scope` into the one dispatch path (LEAD DECISION)
- **Lands:** `runtime/suite.py:9117` (`resolve_scope`, JSON-backed `design/_system/addresses.json`, explicitly
  *"NOT live"*) collapsed into the `resolve_address`/`SCHEME_HANDLERS` chain.
- **★ LEAD DECISION (recorded — collapse-the-second-resolver):** `ui://`/`code://` resolve through this PARALLEL
  resolver today, not a row-add. The union is to collapse it into the one dispatch path (real work — the map's
  row-add was wrong here). This is a developer/architecture call the lead owns. (Reconciled with
  `live-resolution-surface/`, R-LIVE — that stream owns the live-intent FORM; this is the resolver-collapse
  backend.)
- **Verify-by-use:** a `ui://`/`code://` address resolves through the SAME dispatch entry as a resolvable scheme.
- **Don't:** leave two resolvers with a bridge between them.

### B-0.5 · RECOGNISERS → DATA (RULE_OPS shape-ops) — **for predicates only** (lifters are producers)
- **Lands:** `runtime/rules.py:65` (`RULE_OPS`). Add bounded shape-recognition ops: **regex-on-head**,
  **line-count / line-ratio**, **extension-match** (synthesis SEAM B + DESIGN-forms PART 3).
- **Reuse seam:** `RULE_OPS` is the **ONE predicate language** (**Verified** `rules.py:65`: a closed grammar —
  field/lit, and/or/not, comparisons, arithmetic, in/contains). `mode_detection_rules` is the prior art. Build
  the shape-ops ON it.
- **★ THE CORRECTION (UNION over the pillar synthesis, authoritative):** the trigger-system DESIGN-SYNTHESIS
  asserts the crux holds for all three recognisers including lifters. It does NOT. `RULE_OPS` has **no
  produce/extract/emit op** (**Verified**). So:
  - `forms.match` = a **predicate** → fits RULE_OPS ✅ → pure data → a `_CORPUS_REGISTRIES` row authored through
    the ONE shared gate (`_write_registry_file`) — B-1.4.
  - `triggers.when` = a **predicate** → fits RULE_OPS ✅. Whether `create(kind='trigger')` rides the create-gate
    is the **R-TRIGGER-CREATE** reconcile (lead/fabric, not Tim — a counter-precedent exists: `mode_detection_rules`
    is pure-data yet kept off `_CORPUS_REGISTRIES`). The `triggers` MCP tool ships regardless (B-2.6).
  - `lifters.extract` = a **producer** → **RULE_OPS CANNOT express it** ❌. The callable-guard (**Observed**
    `suite.py:9886`) blocks lifters for the right reason: *extraction is code, not a predicate.* Lifters get a
    separate producer-authoring contract (B-1.5 selector-is-data, extract-is-code — LEAD DECISION B-1.4b).
- **Preserves:** existing `mode_detection_rules` predicates evaluate identically; adding ops is additive.
- **Verify-by-use:** a data-AST form with `regex-on-head` selects the same units the current callable matchers
  do (DESIGN-forms §3: head-of-first-8-lines regex + `linky/len(lines)>0.6` ratio + `ts_lines>=3` count).
- **Don't:** add a `produce`/`emit` op to RULE_OPS to "include lifters" — *because* that turns the closed
  predicate grammar into an open code-eval surface (breaks the floor) — exactly the bridge the union forbids.

### B-0.5b · DECLARE THE RECURSIVE GRAMMAR for the live nested `vec://cluster://…#space=scale:…` key (LEAD DECISION)
- **Lands:** `contracts/address.py` — `parse_vec_address` returns the nested structure (a `vec://` whose body
  is a whole `cluster://` address + the `scale:<space>:k<K>` fragment sub-grammar).
- **★ LEAD DECISION (recorded — the grammar IS recursive):** the prior draft routed this to Tim ("Tim decides the
  grammar is recursive"). That is a parser-architecture call the lead owns, NOT a Tim gate. The grammar is
  declared recursive and built against the **live key** (`scale.py:34,282`); the flat-table alternative is wrong
  because it mis-keys the nested body. This must land before vec's `nesting` metadata (B-0.2) is trusted.
- **Verify-by-use (falsify-first):** the flat first-`://`-split mis-keys the live key on UNMODIFIED code (red),
  then the recursive parser returns the nested structure (green). Then RES2 (vec reached via the one path,
  honouring nesting) is unblocked.

### B-0.6 · A SHARED scope base (global / project / user) — forms is the PILOT, roles MIGRATES onto it in-scope
- **Lands:** new shared registry base; **forms** as the pilot consumer (`runtime/forms.py:61` `FORM_FIELDS`,
  `route()` `:171`); **AND `roles.mode_scope` MIGRATED onto the same base** (not left on its own copy).
- **Reuse seam:** `roles.py` `mode_scope` is the exact prior art (a declared data field; the consumer filters by
  it — `roles.py:91,112-113,262-263`). Build the scope base ON that pattern. C9.4 anchors for the new base.
- **★ MIGRATE roles onto the ONE base IN-SCOPE (the prior draft's "NOTE for the lead" is the parallel-not-union
  trap):** standing up a NEW scope base while `roles.mode_scope` keeps its own copy is two mechanisms for one
  concept (scope) — the exact parallel-not-union pattern this build exists to eliminate, plus a soft-word
  deferral. So in THIS loop either migrate `roles.mode_scope` onto the shared base (incomplete-work-in-scope), OR
  record a closed-by-construction reason why roles cannot share it. Not a later "NOTE."
- **Preserves (regression-diff):** `scope` **defaults to `"global"` when absent** → the current forms + roles stay
  global, nothing changes (DESIGN-forms PART 2) — earn it by capturing the forms+roles routing on unmodified
  code, applying the base, diffing identical. `route(text, *, meta=None, project=None, user=None)` — new args default `None`.
- **Precedence:** collect ALL in-scope matches, pick by `(scope_rank, fallthrough_rank, id)` where
  `user=0<project=1<global=2`, `non-fallthrough=0<fallthrough=1` — a narrow global beats a fallthrough user
  (DESIGN-forms §2). `project` is the explicit `project` arg the capture call already names (no singleton exists).
- **Verify-by-use:** a project-scoped form matches only under its project; a role's `mode_scope` filters through
  the SAME base; fail-loud RAISES when no in-scope form matches (the global `prose` fallthrough guarantees a match).
- **Don't:** copy the scope field + filter into the other five+ registries now — *because* that forks six copies
  of the filter (reuse-don't-parallel). Forms + roles are the in-scope consumers; further promotion is per-need,
  but roles is NOT deferred to a NOTE.

### B-0.7 · STORAGE SEAM — widen Protocol 10→the live DISTINCT-method surface, re-type `Suite.store`, absorb the 2 bypasses (LEAD DELIVERABLE #1)
> **This is the FIRST storage deliverable — it ships BEFORE any Postgres/Supabase backend exists. Uncontested.**
- **Lands:** `contracts/resolver.py` (the 10-method Protocol) · `runtime/suite.py` (`Suite.store` type + the two
  bypass namespaces).
- **Reuse seam:** `FsStore` already implements the full surface; build the widened Protocol ON the real
  call-surface, then re-type `Suite.store: FsStore` → `Suite.store: Resolver`.
- **The load-bearing number (Verified — but state the METRIC precisely):** Protocol = **10**; `FsStore` = **77**
  defs. **★ The widen target is the count of DISTINCT store-method NAMES invoked on `self.store`, NOT call-SITES**
  (a reviewer grep gave ~48 distinct names vs ~61 call-sites; the prior draft's "→61" conflated them — you widen a
  Protocol by distinct methods, padding it to a call-site count mis-scopes the seam). **1a:** re-measure LIVE,
  report distinct-method-names (the widen target) AND call-sites (a separate count), then widen Protocol 10 → the
  distinct-method count. **1b:** re-type `Suite.store` (stays green on fs — makes a 2nd backend *possible*).
  **1c — absorb the 2 bypasses:** `cascades.json` via `_ActionRegistry(store.root / "cascades.json")` (**Verified**
  `suite.py:394`) and `agent_sessions/channels.jsonl` via `session_channels.py` both reach the store root
  *outside* the method surface → silently stranded by a backend swap. Absorb them into the store surface
  (unions-not-bridges: pull the bypass in, don't leave a side-channel).
- **Preserves:** the fs path stays green at every step. No hot-path read changes today.
- **Verify-by-use:** the live distinct-method re-measure recorded; `company suites` green after the re-type on fs;
  a synthetic "no-op backend" satisfies the widened Protocol surface (proves the seam is the real surface, not the
  10-method illusion).
- **Don't:** point the hot path at a cloud backend, build HNSW/IVFFlat/halfvec, or move the registries —
  *because* local-first is the stack's law (cloud is later sync/realtime/mobile, addressed identically because
  *the address never changes*), ~9k vectors exact-cosine is sub-10ms, and **Git holds every `<registry>/*.py`
  row** (`_CORPUS_REGISTRIES` is an enumerable index, not a relocation into SQL). **And: no runtime fs-fallback**
  — "reversible" means an operator-initiated ROLLBACK of a migration step, NOT a runtime path where a PG failure
  silently serves fs (a PG failure FAILS LOUD — Notice + Gap; see the migration order below). **And: the PG data
  dir is ext4 (`~/...`), NEVER `/mnt/c` — see the migration section's ext4 + Rule-7-confirm gates.**

---

# PHASE 1 — COVERAGE-USEFUL (the SEE/SHAPE half wired into capture)

Depends on Phase 0 (recognisers→data for `create_form`; scope base; storage seam green on fs). **★ B-1.0 is
PULLED ALONGSIDE the Phase-0 foundations** (not run behind GRAMMAR/IDENTITY) so the emergent kinds EXIST before
anything routes on them — the ordering risk the prior draft left open.
**★ Coverage-first gate (FORMS-ARE-PLACEHOLDER + RCN7):** the current `forms/` rows (`decision`/`log`/`registry`/
`prose`) and `skip`/`deep`/`legibility` stages are **PRIOR-AI SCAFFOLDING, not Tim's canonical taxonomy.** Before
the effort-routing treats any taxonomy as the spine, **B-1.0 CONVERGES onto the COMPLETED coverage sweep (RCN7),
then runs the OPEN-ENDED extending pass**; the emergent kinds are proposed to Tim (a T-* meaning call about HIS
taxonomy); **B-1.2/B-1.3/B-1.4 effort-routing is HARD-GATED — fail-loud — until COV2 (Tim's recorded taxonomy)
exists** (wiring routing to ANY taxonomy before COV2 mislabels the placeholders "emergent" — scaffolding-as-spec).
Mark the placeholder forms/stages PROVISIONAL everywhere.

### B-1.0 · OPEN-ENDED coverage pass — CONVERGE onto the COMPLETED sweep FIRST (RCN7), then EXTEND (no re-derive)
- **★ ANCESTOR (RCN7 — do NOT re-derive): a COMPLETED open per-unit coverage sweep already exists** —
  `build-prep/guided-review-surface/findings/coverage/` ("Full territory coverage of the design corpus, 250+
  documents, completed 2026-06-08", with `substrate.md` reading every file in `contracts/`/`store/`/`fabric/`
  in full, tagging USE/TOUCH/UNIFY/RELATE) + `trigger-system/COVERAGE-RUNBOOK.md`. B-1.0 INGESTS these, marks
  them ancestor/live (RCN7), and EXTENDS the territory map — it does NOT re-scan from zero (re-deriving completed
  work is the parallel-build the union forbids; coverage = Task #74, a co-owned stream named exactly like #73).
- **Lands:** a coverage run that EXTENDS the existing sweep, describing each NOT-yet-covered unit (what it
  actually IS) with no forced classification into the placeholder forms.
- **Reuse seam:** the existing `findings/coverage/` sweep + the capture path + a describe-only role/output_schema.
- **Verify-by-use:** the existing sweep ingested + RCN7 recorded; the extending pass runs over the real corpus;
  its emergent natural kinds are recorded and **proposed to Tim** as the seed of his real form taxonomy (T-* —
  COV2; the effort-routing is fail-loud-blocked until it lands).
- **Do:** converge-then-extend, open-ended — *because* forms come FROM the coverage, not imposed on it (Tim's
  coverage law) AND completed work is adopted, not re-run (scaffolding-not-spec / incomplete-work-in-scope).
  **Don't:** re-derive the sweep from zero; don't lock the placeholder taxonomy as the routing spine.

### B-1.1 · `policy=` passthrough `run_items → run_role`
- **Lands:** `runtime/cognition.py:1204` (add `policy: str | None = None`), forward on the `run_role` call `:1344`.
- **Reuse seam:** `run_role` **already** consumes a `policy` + runs its rep_penalty ladder (**Observed**
  `cognition.py:203-356`); `GenerationPolicy` carries `budget`/`json_schema`/`temperature`
  (`generation_policies.py:96-108`). Build the one-line bridge ON it.
- **Preserves:** default `policy=None` claims **byte-identical** to today.
- **Verify-by-use (the byte-identical claim earns its ✅ by REGRESSION-DIFF, not assertion):** capture the
  default-path output on UNMODIFIED code, apply the additive param, re-run, **diff — identical** = the additive
  guarantee holds (Rule 2 by demonstration). Then a capture with an explicit policy runs the ladder.
- **Don't:** add a second fan path in `run_items` — *because* one role × N units is the contract; effort comes
  from firing once per bucket (below), not a parallel fan.

### B-1.2 · Capture→forms BUCKET-BY-BAND wire (OFF by default) — on the EMERGENT taxonomy, not placeholders
- **Lands:** `runtime/suite.py` — `ingest_paths` (`:10474`, flat fire `:10550-10551`) + `capture_corpus_lenses`
  (`:10662`). New `by_form: bool = False` param (also MCP `ingest`, `mcp_face/tools/ingest.py:15`).
- **Reuse seam:** `route()` exists + supports `meta` (REUSE). Group units by `route()`'s `{stage, policy}`, fire
  **one `run_items` per band**. **The stages/forms it routes on are the COV2 emergent taxonomy** (B-1.0), with
  `skip`/`deep`/`legibility` treated as PROVISIONAL placeholders until Tim's taxonomy lands — NOT the canonical spine.
- **★ HARD GATE (COV2 fail-loud predecessor):** wiring `by_form` to ANY taxonomy before COV2 (Tim's recorded
  taxonomy) exists MUST FAIL LOUD (mirroring the row-add-before-Tim-decision fail-loud). Otherwise the build wires
  to the placeholders and mislabels them "emergent" — the scaffolding-as-spec failure.
- **Preserves:** `by_form=False` (default) claims the **exact current flat path** — earns its ✅ by the
  regression-diff (run flat path before/after, identical). `run_items` itself is untouched (once per bucket).
- **Verify-by-use:** `by_form=True` over a mixed dir → `skip` units **dropped and named** in `skipped_by_form`
  (no-silent-failure floor), different bands fire at different `max_tokens`; AND a falsify-first test: `by_form`
  wired before COV2 is recorded fails loud.
- **Don't:** "call `route()` and log the stage" without the buckets (relabelling, not retiering); and don't
  build the bands on the placeholder taxonomy as if it's correct, and don't wire routing before COV2.

### B-1.3 · Form CONTEXT/OUTPUT selectors + the effort-band field — RIDE `GenerationPolicy`, don't fork a registry
- **Lands:** `runtime/forms.py:61` (optional `context`, `lens` fields) · the per-unit slice hardcode
  `WALK_MAX_CHARS = 6000` (`runtime/corpus.py:255`) · **the effort band as an ADDITIVE field on
  `GenerationPolicy` / `GenerationPolicyRegistry`** (`generation_policies.py`), NOT a net-new `effort_bands/`
  registry.
- **★ LEAD DECISION (recorded — reuse `GenerationPolicy`, don't parallel a registry):** `GenerationPolicy`
  already carries `budget` (the max-tokens band), `json_schema`, `temperature` and has its own registry. The
  only genuinely-new axis is `slice_chars` (the per-unit read window) + the `stage` grouping. Add those as
  **optional additive fields on the policy row** (schema_ver bump) so stage→effort reuses the ONE policy
  registry. Stand up a separate `effort_bands/` registry ONLY if a field genuinely cannot live on a policy row —
  and argue that case (reuse-don't-parallel: don't fork a whole registry for one new field).
- **Reuse seam:** `context://` → existing `ContextRegistry`; `lens` → the existing dynamic-schema-from-lenses
  builder in `capture_corpus_lenses` (`suite.py:10731-10752`); `budget`/`json_schema`/`temperature` →
  `run_role`/`GenerationPolicy`. The form is the per-shape dossier that sizes BOTH ends (DESIGN-forms PART 4).
- **Preserves:** new fields optional/schema-additive; non-form path keeps `WALK_MAX_CHARS`. If the policy row
  gains fields, C9.4: its existing anchors are updated (it already has `generation_policies/AGENTS.md` +
  `tests/generation_policies_acceptance.py`).
- **Verify-by-use:** a `legibility` band cuts a small head-slice; a `deep` band reads the full unit; the `lens`
  field produces the same output_schema the caller-passed `lenses` does today.
- **Don't:** leave `WALK_MAX_CHARS=6000` as the universal slice on the form path; and don't fork a registry for
  a field a policy row can hold.

### B-1.4 · `create_form` — data-AST forms ride the ONE shared gate (LEAD DECISION: Option C)
- **Lands:** `runtime/suite.py` — add `form` to `_CORPUS_REGISTRIES` (`:360-371`, **adopting Task #59's `minds`
  row in the same table — do not clobber it; coordinate via the channel**); `create_form` is a one-liner like
  `create_projection` (`:9933-9939`): `return self._write_registry_file("form", spec)`. `_build_form`
  (`forms.py:98,122`) extended to accept **either** a callable **or** a RULE_OPS data-AST.
- **★ LEAD DECISION (recorded — Option C; the prior draft routed A/B/C to Tim, a forbidden developer-pick):**
  the gate **RAISES on any callable field** (**Observed** `suite.py:9886-9891`) — which is *why* `form` is
  excluded from `_CORPUS_REGISTRIES` today. So "data-create on the existing gate" is impossible while `match` is
  a callable. **Option C is the lead's call:** `create_form` accepts **only data-AST specs** (pure data → rides
  the existing gate as a new row); hand-authored **callable** forms stay developer-gated as files. This honours
  the task ("data-create on the existing gate") AND the floor (executable code stays gated) AND "everything
  authorable as data" — without rewriting the four placeholder matchers day one. (Option A net-new code-render
  path / B all-data-RULE_OPS were considered and not chosen; this is a schema-contract architecture call, not a
  Tim decision.)
- **Reuse seam:** the shared gate `_write_registry_file` (`suite.py:9840-9931`) works unchanged for pure-data
  rows. C9.4: the `form` registry already has `forms/AGENTS.md` + `tests/forms_acceptance.py` — extend them.
- **Preserves:** the placeholder callable matchers keep working (route evaluates whichever a form is); none rewritten.
- **Verify-by-use:** `create(kind='form', spec={data-AST match})` writes `forms/<id>.py`, the gate rediscovers
  it, `route()` selects it on a matching unit; `drift_acceptance` green.

### B-1.4b · LIFTERS get a producer-authoring contract — selector-is-DATA, extract-is-CODE, COMPLETE per-engine parser (LEAD DECISION)
- **★ LEAD DECISION (recorded, artifact-backed — the prior draft routed this to Tim as G-LIFTER-AUTHOR):**
  `lifters.extract` is a **producer**, not a predicate — RULE_OPS cannot author it. The producer-authoring
  contract is: lifters stay **developer-authored file-drops** in this loop; the `create` path is limited to
  predicate registries. The `extensions`/`match`-regex-string SELECTOR is DATA (B-1.5); the `extract` body stays
  CODE. (A gated code-render `propose→apply` for lifters is a possible future upgrade — flagged, not built here.)
- **★ EVERY engine gets a COMPLETE in-process parser — TS/JS via tree-sitter NOW, not a regex stand-in
  (make-each-thing-work, no-MVP):** Python uses the complete `ast` parser (B-1.7); TS/JS must match that
  completeness via **IN-PROCESS `py-tree-sitter` + `tree-sitter-typescript`** (C-extension bindings, no
  subprocess — installed exactly like the in-process `ast` at `coherence_detect.py:16` / PyYAML at
  `frontmatter.py:25`). The prior draft's "subprocess-tree-sitter (rejected) vs regex (shipped)" is a FALSE
  DICHOTOMY — the complete in-process parser is available right now, so the in-process-READ floor does NOT
  justify a deliberately-incomplete regex cut for the one engine Tim acquired to test fully. **An unextractable
  construct emits a Gap (fail-loud) — silent under-extraction is forbidden** (a partial substrate becomes ground
  truth for the union queries + ghost detection). If a genuine in-scope blocker stops tree-sitter this loop, the
  TS incompleteness is an ADOPTED in-scope gap with its return-when written as a SYSTEM-MEMORY Gap ROW, never an
  "upgrade" note. This is a developer/architecture call, not a Tim gate.
- **Verify-by-use (POSITIVE proof, not only ACT3's negative fail-loud):** drop a data-selector lifter, `applicable`
  selects it, `extract` produces real typed records by use; TS extraction completeness == the Python `ast` path
  on a real `.ts` file; an unextractable construct emits a Gap.

### B-1.5 · LIFTER selection-by-file-type + composition onto ONE record
- **Lands:** `runtime/lifters.py:69` (`LIFTER_FIELDS` + `_build_lifter` `:100` — add `extensions` list + optional
  `match` **regex STRING**) · new `applicable(path, text=None)` read (`:167` sibling of `for_projection`).
- **Reuse seam:** the `LifterRegistry` mechanism + `as_records()` (`:175`) — build the selector ON them, keep
  `produces`/`for_projection` (add the file-type axis; don't remove the projection axis — DESIGN-lifters §2).
- **Preserves (earned by regression-diff on the existing lifters):** the existing `produces`/`for_projection`
  selection is unchanged — capture the seed lifters' `as_records()` + `applicable` behaviour on UNMODIFIED code,
  apply the file-type axis, re-run, diff identical for the no-`extensions` path. `match` is a **regex STRING, not
  a callable** — *because* `as_records()` only qualname-ifies
  `extract`; a callable `match` rides raw + breaks JSON serialization + trips `tests/lifters_acceptance.py:90`.
  A string serializes cleanly, no `as_records` change. (This is the lifter *selector* serialization point — NOT
  RULE_OPS authoring; see B-0.5/B-1.4b.)
- **Seed migration (required):** add `"extensions": [".md"]` to `lifters/frontmatter.py`, `links.py`, `blocks.py`
  — *absent `extensions` = NEVER selected* (the safe reading; no silent match-everything).
- **Verify-by-use:** `applicable(".py")` returns the sorted py-lifter set; composition is `{lf.id: lf.extract(text)}`
  (collision-free; id == filename).
- **Don't:** widen `links.py`'s return type in place — `tests/lifters_acceptance.py:85` asserts `["Alpha","http://x"]`;
  add per-link context as a **sibling** `link_context.py`, not a contract change.

### B-1.6 · LIFTER → capture attach (the dead lane connected)
- **Lands:** ONE block in `ingest_paths` (`runtime/suite.py:10558`).
- **Reuse seam:** the corpus record is an **open/additive dict** — `write_record` spreads `**extra`
  (`corpus.py:172`); `capture_corpus` forwards `**extra` (`suite.py:10623`). `structure` rides **free** — no
  `corpus.py` edit.
- **Preserves (earned by regression-diff, not assertion):** `structure` is deterministic over the same `text` →
  re-capture yields the same record → same cas (write-once/idempotent-resume, `corpus.py:174`). The embedding is
  unchanged — only `output` feeds the vector (`suite.py:10635`); `structure` is durable+queryable, not embedded.
  Earn it: capture a unit's record + vector on UNMODIFIED code, apply the attach, re-capture, diff — the embedding
  (vector) byte-identical, the `structure` field additive-only.
- **Verify-by-use:** capture a `.py` → record carries `structure: {py_imports:[...], py_symbols:[...]}`; the
  embedding is the same as before (the regression-diff).
- **Don't:** ask the model to enumerate imports/symbols/links — *never ask the model to enumerate what code can
  extract exactly* (the model paraphrases; the lifter quotes).

### B-1.7 · The new lifter files (file-drop, the open set) + the inbound-link READ
- **Lands (parallel, each self-registers):** `lifters/py_symbols.py`, `py_imports.py`, `py_decorators.py`,
  `py_docstrings.py`, `py_callgraph.py`, `ts_imports.py`, `ts_exports.py`, `ts_components.py`, `json_shape.py`,
  `md_tags.py`, `link_context.py`. Plus `inbound_links(address)` as a `find_relations` sibling (`suite.py:10854`).
  (The `lifters/` registry already has its C9.4 anchors — extend `tests/lifters_acceptance.py` + `lifters/AGENTS.md`.)
- **Reuse seam:** Python = `ast` (REUSE the proven walks at `coherence_detect.py:35,127,154,164`); md/json/yaml =
  regex + the seed lifters + `json`/PyYAML (degrade-to-line-parse if PyYAML absent, as `frontmatter.py:25`).
  Inbound-links = a **read-time fold** over stored `structure.link_context`, mirroring `list_corpus`/`find_relations`.
- **TS/JS:** **IN-PROCESS tree-sitter NOW (`py-tree-sitter` + `tree-sitter-typescript`)** — C-extension bindings,
  no subprocess, installed exactly like the in-process `ast`/PyYAML the repo already uses; this matches the Python
  `ast` path's COMPLETENESS for `ts_imports`/`ts_exports`/`ts_components` (B-1.4b). node/`tsc` subprocess REJECTED
  (breaks the in-process-READ floor); **regex stand-ins REJECTED too — a deliberately-incomplete extractor for the
  one engine Tim acquired to test fully is an MVP cut (make-each-thing-work / no-MVP).** **★ "a missed symbol is
  the SAFE direction" is DELETED — any construct the lifter cannot extract emits a Gap (fail-loud); silent
  under-extraction is forbidden (it poisons the substrate the union queries + ghost detection trust as ground
  truth).** If a genuine blocker stops tree-sitter this loop, record the TS incompleteness as a system-memory Gap
  ROW with a return-when, never an "upgrade" note in `lifters/AGENTS.md`.
- **Verify-by-use:** each new lifter extracts real values; a string `match` survives `as_records()` JSON;
  `inbound_links(B)` returns the `(source, description)` pairs whose `link_context.target == B`.
- **Don't:** fork a second store/index for inbound descriptions — the fold over the stored lifts IS the mechanism.

---

# PHASE 2 — TRIGGER (the ACT half) — SEAM C precedes the structured branch of SEAM A

**Cross-feature dependency (encode in loop order):** **B-2.1 (structured_output capture) precedes B-2.5's
structured cc_launch branch.** A trigger launching a CC with `--json-schema` gets its output dropped until C is fixed.

### B-2.1 · Close the `structured_output` capture gap (SEAM C)
- **Lands:** `runtime/session_supervisor.py:1086-1097` (`_turn_done`) + `runtime/cc_clone.py:330-339`
  (`msg_clone`) + `runtime/routine_runner.py:81-91,115` (`_capture_done`/`fire`).
- **Reuse seam:** the `--json-schema` **input** side exists (`SPAWN_FLAG_ASSEMBLY["json_schema"]`,
  `session_supervisor.py:278-279`). Build the **capture** side ON the existing `done`-event readers.
- **Verified field name:** `structured_output` (**snake_case**) — `render_declarations.json:394` +
  `ui-contract/resources/headless-control.md:162,177`. `structuredOutput` is NOT it.
- **The gap (Verified):** `_turn_done` builds the fanned `done` from `ev.get("result")` + usage only, does **NOT**
  read `ev["structured_output"]` (field only in a docstring, line 279). A schema-launched CC's output is dropped.
- **Preserves:** add `"structured_output": ev.get("structured_output")` → None when no schema → byte-identical
  for non-schema spawns (earns its ✅ by regression-diff on a plain spawn's `done`).
- **★ Label discipline:** the "3-line fix" is **Inferred, not traced.** Verify the scope across all three files
  (falsify-first: a `--json-schema` CC drops its output on UNMODIFIED code → red; fix; green).
- **Don't:** rename to `structuredOutput` or assume one file.

### B-2.2 · `nodes/cc_launch.py` — the composable launch unit (runs ONLY through the operator-gated wire)
- **Lands:** new `nodes/cc_launch.py` (self-registers, `registry.py:55-90`).
- **Reuse seam:** the node contract (CLONE `nodes/ask.py`'s shape) + the supervisor `/spawn → /watch done` cycle
  (REUSE the engine) + the scheduler writing each `PORTS_OUT` port to its `run://` address (REUSE). Copy the
  `routine_runner.fire()` orchestration onto the **raw `/spawn`** route (`build_spawn_body` drops
  `provider`/`flags`/`effort`/`fallback`; the raw route reads them, `session_supervisor.py:1591-1602`).
- **★ Operator-gated by construction (C9.2):** `cc_launch` is a NODE the operator-gated wire runs — it is NEVER
  launched directly by a trigger/driver. The dispatch route is `decision.surfaced_for_review` → operator
  `resolve_surfaced` → `dispatch_decision` (which enforces its gates + refuses a double-launch). The node does
  not emit `resolve`/`approve`/`dispatch`.
- **Preserves:** `VOLATILE = True` is **MANDATORY** (a CC launch reads mutable truth; without it the memo-gate
  serves the first result forever, `nodes/AGENTS.md:15`). `keep_session=False`; the floor spawn = plan permission
  + `mcp__company` only.
- **Verify-by-use:** run a one-shot `cc_launch` node → `result` + `structured` land at their `run://` addresses;
  a `--json-schema` launch fills `structured` (proves B-2.1 wired through).
- **Don't:** route the launch through a rule verb (a CC-launch is a node the gated wire runs, not a 6th destination).

### B-2.3 · `runtime/triggers.py` + `trigger/` dir on the SHARED registry mechanism (LEAD DECISION) + event-kind A2
- **Lands:** new `runtime/triggers.py` + `trigger/<id>.py` rows; one discover line in `Suite.__init__` beside
  `mode_detection_rule_registry` (`suite.py:308-310`). C9.4: ship `trigger/AGENTS.md` + `tests/triggers_acceptance.py`.
- **★ LEAD DECISION (recorded — reuse the SHARED base, do NOT clone the bespoke class):** the prior draft said
  "CLONE `mode_detection_rules.py`." But `mode_detection_rules` has its **own bespoke `ModeDetectionRuleRegistry`
  class** (its own `discover`/`register` — `mode_detection_rules.py:202,216,236`), NOT the shared
  `_BaseEntryRegistry`/`RelationTypeRegistry` mechanism. Cloning a bespoke class propagates a parallel-class
  pattern (reuse-don't-parallel violation). **Reuse the canonical file-discovered registry mechanism** (the
  `board_edges`-reuses-`relation_types`-class-verbatim-with-its-own-dir pattern, the proven one) with a new
  `trigger/` dir. The `when` predicate-grammar reuse (`rules.RULE_OPS`) is correct and kept. If
  `mode_detection_rules` itself is a parallel-class violation, flag it for absorption into the shared mechanism
  (in-scope per unions-not-bridges/incomplete-work-in-scope) rather than replicating it.
- **★ LEAD DECISION (recorded, artifact-backed — event-kind taxonomy = A2, validate-in-place, with A1 as the
  TRIGGERED-deferred upgrade):** the prior draft routed A1/A2/A3 to Tim (a forbidden developer-pick). The lead's
  call: **A2 — validate `watch.event` against the existing `ACTIVATION_CONTEXTS`** (`activation.py:64-106`) to
  ship B-2.3 now. **A1 (a file-discovered `event_kinds/` registry — the registry-is-truth form) is a
  CONDITION-ADDRESSED deferral, NOT a bare "flagged upgrade": written as a system-memory Gap ROW with a concrete
  return-when = "a non-activation event source needs a kind not in `ACTIVATION_CONTEXTS`"** (no_unconditional_
  deferrals — the registry-is-truth form especially needs a firing condition since A2 is the non-registry path).
  No `event_kinds/` lane in this loop.
- **Reuse seam:** the `when` REUSES `rules.RULE_OPS` (validated by `validate_ast`, evaluated by `evaluate` —
  pure, no eval/exec). Cheap actions → `rules.route()` over the 5 `DESTINATION_KINDS`; build-dispatch →
  the operator-gated wire (B-2.2/B-2.5), never a launch verb.
- **Preserves:** the row carries **no Python callable** → pure data; validation is fail-loud (`id==filename`;
  `when ∈ grammar`; action destination ∉ `FORBIDDEN_DESTINATION_VERBS`, `rules.py:130`; `watch.event ∈
  ACTIVATION_CONTEXTS`).
- **Verify-by-use:** drop a `trigger/<id>.py`, discover, `op="run"` a synthetic event → the matching row fires;
  `drift_acceptance` green with `trigger/`'s anchors.
- **Don't:** add a 6th `DESTINATION_KIND` for launch — the floor holds *by construction* only while a rule cannot
  forge a launch verb; and don't clone the bespoke registry class.

### B-2.4 · `board.filed` emit + `board_edges/responds_to.py` (the first hook + the attach-back edge)
- **Lands:** the emit at the **suite/MCP boundary** (where the `cc_board` tool calls suite, which has `_emit`) —
  **NOT inside `cc_board.py`** · new `board_edges/responds_to.py` row.
- **Reuse seam:** `suite._emit` rides the **ONE append-only event log** (mirrors `activation.py`'s casts emitting
  `cognition.wave` + `RollupDriver` reading by a held `since` cursor). The typed-edge layer exists
  (`cc_board.py:157-170,318-410`); `responds_to` is a one-line row-add mirroring `promoted_from.py`, live via
  `reset_registries()`. (`board_edges` reuses the `relation_types` class — no new registry, anchors covered.)
- **Preserves:** `cc_board.file_item` stays pure functions with no suite handle (an inert write today); the emit
  is at the boundary. `relations(board://id, "in")` already surfaces the reply (**Verified read**).
- **Verify-by-use:** `file_item(type="request")` → `board.filed` on the event log → a synthetic driver tick reads
  it; a CC files back `links=[{responds_to → board://id}]` → `relations(…, "in")` surfaces it.
- **Don't:** bolt a pub/sub bus onto `cc_board.py` (parallel-channel anti-pattern); ride the one event log.

### B-2.5 · `runtime/trigger_driver.py` (BUILT-NOT-ARMED) — EXTEND activation's tick, don't fork a 2nd cursor (LEAD DECISION)
- **Lands:** new `runtime/trigger_driver.py` — built as an **extension of `activation`'s existing tick layer**,
  not a second independent driver.
- **★ LEAD DECISION (recorded — extend activation's tick / trigger-as-context, not a parallel cursor):**
  `activation.py` is ALREADY a generic event→(decide)→action tick layer over the one event log (`sense_tick`
  `:458`; `RollupDriver.tick` `:506` reading `events_since`; `ACTIVATION_CONTEXTS` `:64`; an `action` result).
  A new driver with its OWN `events_since` + its OWN held `since` cursor is a SECOND cursor ticking the SAME log
  — the parallel-not-union pattern. **Build the trigger evaluation as an EXTENSION of activation's tick** (one
  cursor, one driver that also evaluates `trigger/` rows), consistent with the A2 event-kind decision (a
  trigger's `watch.event` is an activation-context). If a genuinely separate driver proves necessary, the
  criterion must ARGUE why it is not the existing `sense_tick` and why two cursors over one log is not a second
  bus — default is EXTEND.
- **Reuse seam:** REUSE `events_since` + the held `since` cursor (the `RollupDriver.tick` shape), `rules.evaluate`
  for `matches`, `rules.route` for cheap actions; build-dispatch → the operator-gated wire (B-2.2), never a
  direct launch. C9.4: if a new module, its anchors; if an extension, update activation's drift home.
- **Preserves:** **BUILT-NOT-ARMED** — env-gated dormant (mirroring `activation_driver`'s
  `COMPANY_ACTIVATION_LOOP`-style gate). This is the **TIMING** gate ON TOP of the structural operator gate
  (B-2.2). A build-worker must NEVER arm the driver (Autonomous-Spawn-Lead-Only).
- **★ Self-trigger loop guard (non-negotiable):** the reply `file_item(...)` re-emits `board.filed` → re-read →
  same trigger fires → runaway. Wire the proven fix: `OPERATOR_ACTIVITY_KINDS` self-exclusion
  (`activation.py:359-364`) — **(a) exclude items carrying a `responds_to` edge** (structural, no new field —
  recommended), or (b) stamp the emit with an `origin` and skip trigger-authored origins.
- **Verify-by-use:** feed one synthetic `board.filed` → the (extended) driver fires the matching trigger once,
  THROUGH the operator-gated wire for any build-dispatch; a `responds_to` reply does **not** re-trigger.
- **★ Structural-gate-INDEPENDENT-of-arming by-use proof (C9.2 requires this, not the weaker dormancy code-read):**
  in a SANDBOX, ARM the driver, feed a synthetic event whose action is a build-dispatch, and confirm it routes
  through the operator gate (`decision.surfaced_for_review`) — NEVER a direct `claude -p` launch. The structural
  gate earns green by use; "the driver stays dormant" is an Observed/code-read, not the proof C9.2 demands.
- **★ Falsify-first floor test:** a trigger/driver path attempting to emit `dispatch` is **REJECTED at
  construction** (mirroring `FORBIDDEN_DESTINATION_VERBS` / `dispatch_decision`'s no-bypass) — red proves the
  forge is possible on a broken build, green proves the floor holds.
- **Don't:** stand up an always-on tick loop, arm any source, or build a second cursor over the one log.

### B-2.6 · `mcp_face/tools/triggers.py` — agents author triggers via the tools
- **Lands:** new `mcp_face/tools/triggers.py` (auto-registered by `server.py` pkgutil discovery — no `server.py`
  edit, mirrors `routines.py:27-29`).
- **Reuse seam:** CLONE the `routines.py`/`flows.py`/`node.py` tool shape — ONE parameterised tool, an `op`
  selector (`list`/`get`/`run`/`add`/`arm`). Actions resolve through the SAME routing the graph engine uses.
- **Preserves:** `op="run"` is the by-USE proof (a synthetic event, as `activation.sense_tick(raw_event)` proves
  the sense path); `op="arm"` is **needs-tim** and refuses-loud unless operator-authorized (BUILT-NOT-ARMED floor).
- **Verify-by-use:** `triggers(op="add", spec={...})` writes a `trigger/<id>.py`; `triggers(op="run", id=...)`
  fires it against a synthetic event; `op="arm"` refuses without authorization.
- **Don't:** promise `create(kind='trigger')` for free before R-TRIGGER-CREATE resolves WHY `mode_detection_rules`
  (also pure-data) was kept off `_CORPUS_REGISTRIES` — the tool ships regardless; `create_trigger` is the
  conditional add (lead/fabric reconcile, not a Tim gate).

---

# PHASE 3 — THE UNION SEAMS (the SAME substrate at different aspects) — absorb, don't add

### B-3.1 · Coherence as ONE LENS over the same substrate (SEAM E) — FORM handed to guided-review (R-COHERENCE)
- **Lands:** the three coherence gates → the first rows of a `finding-type` registry; findings ride the
  **existing** event log (`kind="coherence.finding"`, address-stamped); dispositions ride the **existing**
  pin-overlay; burn-down = read-time rollup. C9.4: `finding-type` ships its three anchors.
- **Reuse seam:** the event log + pin-overlay + `run_stats`-style read-time rollup. Build coherence ON the
  address substrate.
- **Preserves:** **no new store, no `coherence://` scheme** — consistent with the storage GO.
- **Verify-by-use:** a detector emits → a finding lands on the event log → a disposition persists → re-run
  reconciles known/new/resolved.
- **★ FORM:** the coherence burn-down is operator-meaningful → a navigable design-system surface (LEG1
  meaning-from-data) that renders so SHAPE carries the burn-down state (render-for-cognition: open vs resolved at
  a glance), **NOT a CLI burn-down, NOT a flat list**; owned by `guided-review-surface/` (R-COHERENCE) and
  **handed off as an ENFORCED system-memory Gap row** (`return-when` = guided-review's burn-down is
  design-critic-passed + render-for-cognition on both faces) — overall-done blocks on it; design-critic +
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
