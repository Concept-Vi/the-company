# Consolidation draft — methodology-docs (company-build · rhm-build · wire-build)

> **STATUS: DRAFT / PROPOSED ONLY.** Nothing here has been executed. All three source files are
> untouched. This file is the deliverable of one consolidation lane; the owning session decides.
> Origin: DRIFT-RADAR-REPORT.md, confirmed unification candidate #1 (cos .86) — "the same
> cron-loop/lanes/verify-by-use protocol written three times… a one-source methodology page with
> per-build deltas would hold it."

---

## RATIONALE

### What these files actually are (load-bearing fact)

The three sources are **byte-identical mirrors of live, runnable skills** (verified by md5sum,
2026-06-10):

| repo copy | live skill | md5 match |
|---|---|---|
| `/home/tim/company/docs/methodology/company-build.md` | `~/.claude/skills/company-build/SKILL.md` | ✅ `8eac2834…` |
| `/home/tim/company/docs/methodology/rhm-build.md` | `~/.claude/skills/rhm-build/SKILL.md` | ✅ `02f1e001…` |
| `/home/tim/company/docs/methodology/wire-build.md` | `~/.claude/skills/wire-build/SKILL.md` | ✅ `72332d27…` |

`docs/methodology/README.md` states the contract explicitly: *"The live, runnable versions remain
in `~/.claude/skills/`. These copies are the durable record + reference. When a recipe changes,
update both (or treat the live skill as source and re-copy here as part of the change)."* It also
already names the lineage: *"They descend from one another (`company-build` is the canonical
recipe; the rest are adaptations)."*

So this is not three free-floating docs — it is three **(repo-mirror ↔ live-skill) pairs** plus a
README that documents the family. Any consolidation that edits the repo copies WITHOUT the live
skills changing in the same step **breaks the mirror invariant and manufactures drift** — the
exact disease this lane exists to cure. That constraint shapes the whole verdict.

### The family is bigger than the three

Same folder, same protocol, not in this overlap: `docs/methodology/remediation-build.md` (also a
byte-identical mirror of its skill). Outside the folder, **unmirrored** sibling loop-skills that
share the same protocol skeleton: `voice-build`, `cognition-build`, `mockup-build`,
`interactive-surface-build`, `workshop-build`, `unified-build-loop`. The folder also holds the
upstream methodology pair (`loop-prep.md`, `plan-review.md`). Every new loop today is written by
**copying the latest recipe and mutating it** — fork-and-drift is the current reproduction method.
That is the strongest argument FOR extracting the shared core once.

### What is duplicated (the shared protocol skeleton, ~60–70% of each doc)

All three carry, in near-identical words:

1. **Header discipline** — "Cron-driven, parallel, crash-safe"; rhm says "Mirrors /company-build;
   same discipline", wire says "Mirrors /rhm-build + /company-build; same discipline".
2. **Files block shape** — plan triad (Completion Criteria · Implementation Guide · Research
   Synthesis) in the Windows-side counterpart vault `build-prep/`; REPO `/home/tim/company` +
   branch + never-commit-to list; venv `./.venv`; canvas `canvas/app` (:5173); bridge :8770;
   STATE = `state.json` + per-lane `lanes/<lane>.report.json` + `loop.lock` under a `.build/…` dir.
3. **Lanes concept** — file-disjoint territories → safe parallel; explicit dep graph.
4. **The 10-step fire** — lock-or-exit (<20 min) · read state+plan · ingest lane reports ·
   compute buildable (stale >25 min → reclaim) · dispatch workers in parallel with the same
   worker-prompt contract (read `AGENTS.md`→`MAP.md`→`STATE.md`→module `AGENTS.md` FIRST; ONLY its
   lane in ONLY its territory; NOT commit, NOT edit criteria; obey laws; write
   `{lane,criteria,files,how_verified,preserved,notes}` report) · verify by USE (bridge restart →
   tests + `drift_acceptance.py` → curl → chrome-devtools driving the real thing + screenshot) ·
   adversarial re-check by a SEPARATE agent · design-critic (FORM) by a SEPARATE agent against the
   same design rubric + design-lint · flag-never-green-paint · mark+commit per criterion
   (`☐`→`✅`/`◑` + by-use note, update STATE/MAP, `git add <paths>`, NO Co-Authored-By trailer,
   update state.json) · blocked-twice → `blocked`+reason, move on · release lock, exit.
5. **Stopping** — all terminal → write `WALKTHROUGH.md` + PushNotification Tim; never delete the
   cron (Tim ends it).
6. **Laws core** — build against contracts · schema-additive (bump `schema_ver`) ·
   registry-is-truth / one source / never fabricate · fail loud · ext4 · NO Gemini ·
   reflects-never-owns · update self-description (drift must pass) · **FORM is half of done**
   (verbatim-identical long clause in all three) · prove by USE never code-reading ·
   tldraw = 3.15.6.
7. **Invocation shape** — `/<name>` cron · "continue the X build" · "X build status" (read state +
   plan, report, don't run) · "stop the X build" (delete the cron).

### Observed drift BETWEEN the three copies (evidence the duplication already costs)

These are core-protocol divergences, not per-build deltas — each one is a place where an
improvement landed in one copy and not the others:

- **Bridge restart**: company uses bare `pkill -f 'bridge.py 8770'; … bridge.py 8770 &` (~3s);
  rhm/wire use the hardened `pkill -f '[b]ridge.py 8770'; … setsid … >/tmp/bridge-<x>.log 2>&1
  </dev/null &` (~4s) — pkill-self-match-safe, session-detached, logged. Strictly better; company
  never received it.
- **Worker dispatch mode**: company `mode auto`; rhm/wire `mode bypassPermissions`.
- **"Console MUST be clean"** UI gate: rhm/wire only.
- **`refresh_self_description` on verb/type/capability change** in verify: rhm/wire only.
- **Verification target**: company verifies against criteria/units; rhm/wire verify **inside
  scenarios** ("against the SCENARIOS not units") — a protocol upgrade.
- **Channel-back step 8**: absent in company; E3 substrate-verdict loop in rhm; extended with the
  unattended wire dispatch (`drive_dispatchable`) in wire.
- **Lock wording**: "write it (with timestamp)" (company) vs "write epoch" (rhm/wire).
- **Design-critic paragraph**: three near-identical variants; wire's is fullest (adds "the form
  analogue of `drift_acceptance`", "not a later polish pass", "responsive at the set widths").

This is real fork-and-drift inside what the README itself calls one recipe family.

### What each source uniquely holds (must survive any consolidation)

- **company-build.md**: lanes E/N/K/U/F with their file territories and criteria mapping (A–G);
  state at `.build/` root with the gloss "(gitignored) — the coordination substrate",
  "single-writer, no race", "overlap guard"; branch `operable-surface`; the
  `[operable-surface]` commit tag; the canvas-law phrasing "edges/positions backend-authoritative;
  drag round-trips through /api"; create_node seeding / atomic save_graph / per-port edges /
  per-kind models / events_since endpoint inventory; walkthrough content spec ("how to drive
  each"); taste examples "feel of a drag, looks right".
- **rhm-build.md**: lanes CONTRACTS/SCHED/CORE/UI/X with territories; `.build/rhm/`; branch
  `rhm-walkthrough-organ` (off `operable-surface`); `[rhm-organ]` commit tag with scenario id in
  the message; S1–S7 scenario definitions in the verify step; the full **E3 channel-back**
  (verdict_cursor · `resolve_verdicts_since` vs approve-only `review_verdicts(since)` ·
  `commit_criterion` three-part bind on `derived_from`=resolve-`seq` · `requeue_from_verdict`
  with actionable WHY · "you CANNOT edit the criteria markdown, a new criterion = requeued inbox
  item + needs-tim flag" · crash-safe cursor, commit binds to unique `seq` not `sid` ·
  operator-only resolve); the "WALKTHROUGH.md is a human SUMMARY, not the channel-back" callout;
  the recursive payoff (the organ's first live run IS the operable-surface walkthrough, S1); laws
  additions (DETERMINISTIC gates NO confidence; no-bypass via POLICY/`is_approved`/bind;
  reuse-don't-parallel: extend `coa`+`resolve`+inbox+scheduler+registry, `ui_info` is a sibling of
  object_info not an edit to it); taste examples "voice naturalness, exact spotlight aesthetics".
- **wire-build.md**: lanes UX/WIRE-BE/WIRE-LOOP (U1 RUN-latch call-site fix at App.tsx:1036);
  `.build/wire/`; branch `decision-wire-and-surface` (off `rhm-walkthrough-organ`); `[wire]` tag;
  plan provenance "plan-reviewed, 2 rounds, converged" + the launch-channel research folder
  `build-prep/research-claude-code-launch/`; S8's seven parts; the SSE navigation-"timeout" quirk
  note for chrome-devtools; the **entire W6 unattended dispatch**: `drive_dispatchable` bounded
  watcher pass · `resurface_crashed` first (dispatch claim with no terminal event → loud
  re-surface exactly once via a `decision.crashed` marker; `dispatch_decision` CORRECTLY refuses
  re-launch) · auto-dispatch iff approve AND `is_build_intent` (`payload["intent"]=="build"`, §W2)
  AND `posture(declared_class)==AUTO` (`consequence_class`, default `"decision_build"`, AUTO in
  `governance.POLICY`) · `dispatch_decision(sid, derived_from, *, launcher=None, verifier=None,
  repo=None)` semantics (per-seq lock → `decision.dispatch` event-log exactly-once → three-part
  bind → posture pre-gate → deny-all empty scope → launch → verify → `implemented` or surface
  back; `LaunchError` → loud re-queue inside the verb, returns `{requeued,…,launched:False}`,
  does not raise) · verdicts are event **dicts** (`v["seq"]`, never attribute access) · §W7
  concurrency cap (`implement.CONCURRENCY_CAP`, env `COMPANY_WIRE_CONCURRENCY`, default 3;
  `decision.deferred` event + returned `deferred` list; cursor advances only past CONSUMED
  verdicts) · exactly-once does NOT rely on the cursor (the event is the guarantee; cursor =
  coarse guard) · only `/api/resolve` writes `resolved`; code writes the `status` lane only; the
  commit-law expansion (refresh_self_description for factual blocks on apply; prose by
  integration; drift must pass BEFORE commit); laws additions (the repo's 8 rules enumerated incl.
  stage-gated SURFACE-cross-cutting/CONFIRM-irreversible and author-from-the-registry/ASK-don't-
  fabricate; exactly-once; operator-only resolve; read the module AGENTS.md before editing it);
  adversarial examples (forge a dispatch, race two fires, write `implemented` on a failed build,
  exceed declared scope); the wire's recursive payoff (first real run = a decision Tim records,
  implemented autonomously, reviewed through the RHM organ); taste examples "spotlight aesthetics,
  copy tone, icon set".

### Judgment: is consolidation right?

**Mixed — extraction yes, replacement no.**

WRONG to merge the three docs into one replacing document, because:

1. **Mirror invariant.** Each repo doc must stay byte-identical to a live skill. A cron fire
   invokes ONE skill and the loop agent executes ONE self-contained prompt. Consolidating the repo
   docs without identically restructuring the live skills creates repo↔skill drift by design.
   Restructuring the live skills (core-doc + delta-pointer) would make every autonomous fire
   depend on a two-file read inside an unattended loop — a new failure mode, against the
   AI-path-of-least-resistance law (the correct action must be the easiest path; for an unattended
   cron agent that is one complete prompt).
2. **They are historical records of an *evolving* protocol, not three copies of one frozen
   protocol.** company-build (no channel-back, unit-verify) → rhm-build (+scenarios, +E3
   channel-back) → wire-build (+unattended dispatch, +commit-law detail). All three builds have
   RUN (engine built; RHM v1 operational + proven; wire built on its branch). Normalizing the
   three onto one core would retroactively falsify what each loop actually executed.
3. **The overlap is partly by design** — the README already declares the descent relationship and
   the durable-copy purpose. A series with a declared lineage is not accidental duplication.

RIGHT to extract the shared core ONCE, because:

4. The drift listed above is real and already cost (the design-critic block was visibly
   retrofitted into all three by hand; the bridge-restart hardening reached only two of three).
5. The family keeps growing (6+ unmirrored sibling loops) by fork-and-mutate; a canonical
   **build-loop protocol** page gives future loops one place to instantiate from, and gives
   protocol improvements one place to land before propagation.
6. This is exactly the one-source / no-repeat law applied at the methodology layer, and exactly
   what the drift radar proposed: "a one-source methodology page with per-build deltas."

### Current-law overlay the owning session must rule on (NOT folded into sources)

- **Branch rules are superseded.** All three docs mandate stacked branches
  (`operable-surface` → `rhm-walkthrough-organ` → `decision-wire-and-surface`, "NEVER commit to
  main"). The standing law since 2026-06-04 (`feedback-no-branches-company`) is **commit to main;
  no branches in ~/company** — proven by the branch-consolidation cleanup, and the newer sibling
  loops (e.g. voice-build) already commit to main. The proposed protocol page below states
  commit-to-main as the current rule and preserves the historical branch facts in the deltas as
  record. The owning session should decide whether the live skills also get a superseded-banner.
- **Both-or-neither.** If any restructuring of the three repo docs is ever executed, it must land
  in the live skills in the same change, per the README contract.

### Decisions for the owning session (smallest set)

| # | Decision | This draft's recommendation |
|---|---|---|
| D-a | Add `docs/methodology/build-loop-protocol.md` (the consolidated text below) as a NEW one-source page? | Yes — pure addition, breaks nothing, gives future loops an instantiation source. |
| D-b | Thin the three docs' shared sections to pointers at the protocol page? | No for now — only ever in lockstep with the live skills (both-or-neither), and the historical-record + self-contained-prompt arguments weigh against it even then. Keep them full. |
| D-c | Backport the hardened bridge-restart / console-clean / refresh_self_description lines into company-build (doc + skill together)? | Only if company-build will ever fire again; otherwise leave the record as-ran and note in the protocol page (done below as VARIANT notes). |
| D-d | Superseded-branch banner on the three docs/skills? | Worth doing, but it is an edit to other lanes' files — owner's call, not this lane's. |
| D-e | Does `remediation-build.md` (same folder, same family, outside this overlap) join the protocol page's delta list? | Yes eventually; out of this lane's named scope, flagged only. |

---

## VERDICT: mixed

Keep all three sources intact (mirror invariant + historical record + self-contained cron
prompts). Consolidate by **adding** the one-source protocol page below; per-build deltas preserved
as clearly-marked sections. No source is retired.

---

## CONSOLIDATED TEXT — proposed `docs/methodology/build-loop-protocol.md`

> Tentative. Written as the canonical instantiation source for FUTURE loops and the single landing
> place for protocol improvements. Where the three historical recipes diverge, a **[VARIANT]**
> note records who says what, so nothing is lost and the owner can canonize. Slots a new loop must
> fill are marked `«slot»`.

# The Build-Loop Protocol (cron · lanes · verify-by-use)

The Company's autonomous build recipe: a cron-driven, **parallel**, **crash-safe** loop that reads
a plan, builds the buildable file-disjoint lanes in parallel, verifies each criterion **by USE**
(function AND form, plus an adversarial re-check), commits per criterion, flags what needs Tim,
and surfaces a walkthrough when done. The whole build runs autonomously; Tim reviews at the end.

Instantiations (per-build deltas at the end of this page): `company-build` (the canonical first
recipe) → `rhm-build` → `wire-build` (each descends from the previous; later siblings:
`remediation-build`, `voice-build`, `cognition-build`, `mockup-build`, `interactive-surface-build`,
`workshop-build`, `unified-build-loop`). Upstream methodology: `loop-prep` (produces the plan
triad) and `plan-review` (hardens it) — a loop should only run on a plan-reviewed triad.

## 1 · Files (every instantiation declares these)

- **PLAN** — the triad in the Windows-side counterpart vault:
  `/mnt/c/Users/Workstation001/Documents/Claude/Projects/counterpart/the Company/build-prep/«name» — Completion Criteria.md`
  (+ ` — Implementation Guide.md`, ` — Research Synthesis.md`). Read EACH fire, never cached.
  Criteria may carry scenarios + build order + lanes (rhm-style) and plan-review provenance
  (wire-style: "plan-reviewed, 2 rounds, converged").
- **REPO** — `/home/tim/company`. venv `./.venv`. canvas `canvas/app` (vite :5173). bridge :8770.
  **Commit target under current law (2026-06-04, feedback-no-branches-company): `main` — no
  branches; branches strand work across parallel sessions.**
  *[VARIANT — historical: the three first-generation recipes each used a dedicated stacked branch
  and a NEVER-commit-to list (see deltas). Superseded; preserved as record.]*
- **STATE** — `«.build/«dir»»/state.json` (gitignored; the coordination substrate) ·
  per-lane completion markers `«.build/«dir»»/lanes/<lane>.report.json` (single-writer, no race) ·
  `«.build/«dir»»/loop.lock` (overlap guard).

## 2 · Lanes

Decompose the plan into **file-disjoint lanes** (a lane = a set of criteria + an exclusive file
territory) with an explicit **dependency graph** (which lanes are independent, which only become
buildable after another is *verified*). File-disjointness is what makes parallel dispatch safe;
the dep graph is what sequences the rest. `«lanes + territories + deps»`

## 3 · Each fire (one bounded wave)

1. **Lock or exit.** If `loop.lock` exists and is <20 min old → exit (a wave is running). Else
   write it (epoch timestamp). Always remove on exit.
2. **Read** state.json + the PLAN (especially its scenarios/group under build) + the relevant
   GUIDE sections.
3. **Ingest finished lanes:** each `lanes/*.report.json` newer than its state entry → that lane is
   built-unverified → goes to verify (step 6).
4. **Compute buildable lanes:** lanes with status `todo` whose deps are all `verified`. Skip
   `in-progress` (unless stale >25 min → reclaim) / `verified` / `blocked` / `needs-tim`.
5. **Dispatch buildable lanes IN PARALLEL** (Agent, run_in_background;
   *[VARIANT — worker mode: `bypassPermissions` (rhm/wire, later practice) vs `auto` (company,
   first recipe)]*). Each worker prompt MUST: read `/home/tim/company/AGENTS.md` → `MAP.md` →
   `STATE.md` → its module's `AGENTS.md` FIRST; implement ONLY its lane's criteria in ONLY its
   file territory; **NOT commit, NOT edit the criteria doc**; obey the LAWS (§5); on finish write
   `lanes/<lane>.report.json` = `{lane, criteria:[...], files:[...], how_verified, preserved,
   notes}`. Mark each lane `in-progress` in state. Then exit — the next fire verifies when
   reports land.
6. **Verify built-unverified lanes (by USE — against SCENARIOS where the plan defines them, not
   units):**
   - Backend (.py) changed → **restart the bridge** (hardened form, later practice):
     `pkill -f '[b]ridge.py 8770'; cd /home/tim/company && setsid ./.venv/bin/python
     runtime/bridge.py 8770 >/tmp/bridge-«name».log 2>&1 </dev/null &` (~4s).
     *[VARIANT — company used the unhardened `pkill -f 'bridge.py 8770'; … &` (~3s), no setsid/log.]*
   - Run the named acceptance tests `./.venv/bin/python tests/<t>.py` **+
     `tests/drift_acceptance.py`**; curl the new endpoints; run `refresh_self_description` if
     node-types/verbs/capabilities changed *(rhm/wire practice; e.g. rhm's `gate` node)*.
   - UI: chrome-devtools MCP on `http://localhost:5173` — actually DO the thing the criterion
     claims (add a node, open its inspector, set a field, run, see output, drag a port, watch a
     pushed update / drive the scenario step). Screenshot. **Console MUST be clean** *(rhm/wire
     practice)*. Known quirk: a navigation "timeout" is the SSE keep-alive — the page renders;
     select the page + screenshot (wire).
   - **Run the plan's scenarios as they become possible** — a criterion is verified inside a
     passing multi-part scenario, not as an isolated unit. `«scenario list»`
   - **Adversarial re-check (FUNCTION):** dispatch a SEPARATE agent per just-verified criterion
     whose job is to DISPROVE "done" — find the case where it fails, within its scenario (e.g.
     forge a dispatch, race two fires, write a success marker on a failed run, exceed declared
     scope). A line is `verified` only if it survives.
   - **Design-critic (FORM — every operator-facing surface, mandatory, separate agent):** the
     function-verifier defaults to "does it work" and cannot judge form. Dispatch a SEPARATE
     browser-driving **design-critic** (screenshots) whose only lens is the product face, against
     the **design rubric**: built on the design system's components + tokens (NO hardcoded values,
     NO bespoke one-offs) · no overlaps · responsive at the set widths · consistent
     scale/type/spacing · settings consolidated · navigable visual/spatial surface, not a
     text-wall/list · empty/loading/error states · outcome demonstrable. The FORM face of a
     criterion is green ONLY if the critic passes it. Where machine-checkable, a **design-lint**
     fails the build on off-token / bespoke-element — the form analogue of `drift_acceptance`;
     function-only cannot be marked done. FORM is half of done (AGENTS.md rule 9), not a later
     polish pass.
   - **Flag, never green-paint:** genuinely subjective taste (feel of a drag, voice naturalness,
     exact spotlight aesthetics, copy tone, icon set, "looks right") → mark `needs-tim`, NOT
     verified. (A bespoke/overlapping/off-design-system surface is NOT a taste call — it FAILS
     form.)
7. **Mark + commit per criterion:** check the box in the CRITERIA doc (`☐`→`✅`/`◑` with a
   one-line by-use note + the scenario id where applicable); update `STATE.md`/`MAP.md` if a
   capability changed; **update the self-description as part of the change**
   (`Suite.refresh_self_description()` for factual blocks; `AGENTS.md`/`MAP.md`/`STATE.md` + the
   module `AGENTS.md` prose by integration; `tests/drift_acceptance.py` must pass BEFORE commit —
   wire's commit-law form, the fullest). Then commit ONLY the touched files by path:
   `git add <paths> && git commit -m "[«tag»] <criterion-ids>: <what> (verified by «S#/use»)"`.
   **NO Co-Authored-By / attribution trailer.** Commit per coherent criterion-unit. Update
   state.json.
8. **Channel-back (instantiations that act on operator verdicts — rhm E3, wire E3+W6):** act on
   verdicts directly from the substrate, **no markdown middleman**. Keep a `verdict_cursor` (an
   event `seq`) in state.json — loop state, NOT a suite method. After step 7:
   `suite.resolve_verdicts_since(verdict_cursor)` → process in `seq` order → approve →
   `commit_criterion(criterion_id, sid, derived_from=seq)` (the three-part-bind gate:
   kind=resolve · choice=approve · surfaced==sid); reject/needs-change → `requeue_from_verdict`
   (a NEW responsive review item through the SAME inbox, carrying the actionable WHY);
   comment/skip are not resolve events. Advance the cursor to the max `seq` consumed; persist.
   Crash-safe: a re-fire re-reads from the cursor and can never double-commit
   (`commit_criterion` binds to the unique `seq`, not the `sid`). **Operator-only stays
   operator-only:** the loop READS verdicts and WRITES derived commits/requeues/dispatches; it
   NEVER calls `resolve`/`resolve_surfaced` — only the operator resolves; the loop has no resolve
   verb. The criteria markdown is out of the loop's edit territory: "a new criterion" = the
   requeued inbox item + a `needs-tim` flag in state.json, never an edit to the criteria doc.
   (Wire extends this step with unattended dispatch — see the wire delta, §W6/W7.)
9. **Blocked:** a lane failing verify twice → `blocked` with reason; move on (never stall).
10. **Release lock. Exit.**

## 4 · Stopping → the walkthrough

When every criterion is `verified`, `blocked`, or `needs-tim` (none `todo`/`in-progress`): stop
dispatching, write `«.build/«dir»»/WALKTHROUGH.md` (what's verified — by which scenario · what
needs Tim's eyes · what's blocked + why · how to drive each) and **PushNotification** Tim. Do not
delete the cron — Tim ends it.

> **WALKTHROUGH.md is a human SUMMARY, not the channel-back** (rhm's clarification, general):
> where step 8 exists, Tim's verdicts are acted on directly in-loop from the substrate (events +
> the inbox) — there is no markdown relay where the loop waits for a file to be hand-edited.

## 5 · Laws (bind every worker — from the repo constitutions)

Core, all instantiations: **build against contracts** · **schema-additive** (optional fields,
bump `schema_ver`) · **registry is the source of truth / one source — author from the registry,
never invent/fabricate (ASK don't fabricate)** · **fail loud** (no silent fallback/cache) ·
**ext4 store** · **NO Gemini** · **reflects-never-owns** (canvas drives via addresses;
edges/positions backend-authoritative; drag round-trips through /api) · **update the
self-description as part of the change** (`drift_acceptance` must pass) · **stage-gated**
(SURFACE cross-cutting, CONFIRM irreversible) · **FORM is half of done** (any operator-facing
surface is built on the design system — components + tokens, NEVER bespoke/hardcoded;
function-only is NOT done; FORM verified by a SEPARATE design-critic + a fail-loud design-lint —
AGENTS.md rule 9) · **prove by USE — FUNCTION *and* FORM, inside a scenario where the plan has
them — never code-reading** · **read the module AGENTS.md before editing it** · tldraw installed
= **3.15.6**.

Governed-action additions (rhm/wire — any instantiation whose build touches
decision/review/dispatch machinery): **DETERMINISTIC gates, NO confidence value anywhere** (route
on declared consequence/reversibility/LOCKED via POLICY) · **no-bypass** (every consequential
action reads authorization from the substrate — POLICY, `is_approved`, the
`derived_from`=resolve-`seq` three-part bind — never a caller flag; the system
presents/surfaces, only Tim resolves) · **operator-only resolve** (code writes the `status` lane
only — e.g. `implemented` — NEVER the operator `resolved` field) · **exactly-once** (a durable
claim event keyed on the resolve `seq`, checked before launch) · **reuse don't parallel** (extend
`coa` + `resolve` + inbox + scheduler + the registry/bind/`apply` pattern — no second
decision/record/render/build/queue system; new shapes are siblings, e.g. `ui_info` beside
object_info, not edits).

## 6 · Invocation pattern

`/«name»` (the cron) · "continue the «name» build" (resume) · "«name» build status" (read
state.json + the PLAN, report, don't run) · "stop the «name» build" (delete the cron).

---

## PER-BUILD DELTAS (every unique fact preserved)

### Δ company-build — the operable composition surface (the canonical first recipe)

- **Skill description (frontmatter):** Autonomous cron-driven parallel build loop for the Company
  operable composition surface. Reads the build-prep completion criteria, builds the next
  buildable file-disjoint lanes in parallel, verifies by use + adversarially, marks/commits on
  the operable-surface branch, flags what needs Tim's eyes. Invoke via the */10 cron, or
  "continue the build" / "build status".
- **Scope:** criteria **A–G** of the operable surface; the whole build runs autonomously, Tim
  reviews at the very end.
- **PLAN:** `…/build-prep/Operable Composition Surface — {Completion Criteria, Implementation
  Guide, Research Synthesis}.md` ("the plan — Windows-side vault; read each fire").
- **Branch (historical, superseded by no-branches law):** `operable-surface` — never commit to
  `main`. Commit tag `[operable-surface]`, message form
  `"[operable-surface] <criterion>: <what> (verified by use)"`.
- **STATE dir:** `.build/` root — `state.json` · `lanes/<lane>.report.json` · `loop.lock`.
- **Lanes** (see GUIDE "Parallelization"):
  - **E — Embeddings**: `fabric/transport.py` `fabric/client.py` `fabric/config.py` + NEW
    `nodes/embed.py` `nodes/similarity.py` `nodes/retrieve.py`. (E1–E5) — independent, anytime.
  - **N — Node configs**: a `CONFIG` block per existing `nodes/*.py`
    (ask/codebase/constant/join/llm/model_of_tim/pair/portal/rhm_mode/titlecase/uppercase/
    wordcount). (A1) — independent.
  - **K — Backend surface**: `runtime/suite.py` `runtime/bridge.py` `store/fs_store.py` —
    create_node seeding(A) · atomic save_graph + set_position + position-in-state + /api/move(C5)
    · graph_id threading + /api/graphs(C4) · per-port edges in state(C2/C3) · per-kind models +
    /api/models(B) · force in /api/run(D4) · events_since + /api/stream(G) · wire /api/set(A3).
    One lane (shared hot files).
  - **U — Canvas**: `canvas/app/src/App.tsx` only — config form + api.set(A2) · model
    dropdowns(B) · port nubs + drag(C1) · graph picker(C4) · loadGraph rewrite + drag-listener +
    persistenceKey camera-only(C5) · force button(D4) · EventSource(G). Depends on K's endpoints
    → only buildable once K is verified.
  - **F — Act on outputs**: composes last (depends on C+U).
- **Protocol-variant facts (as-ran):** worker mode `auto` · unhardened bridge restart
  (`pkill -f 'bridge.py 8770'; … &`, ~3s) · no console-clean gate · no refresh_self_description
  line in verify · verify against criteria/units (no scenarios) · no channel-back step (8-step →
  9-step fire numbering; "Always remove on exit" lock wording, "write it (with timestamp)").
- **Stopping:** `.build/WALKTHROUGH.md` — what's verified · what needs Tim's eyes · what's
  blocked + why · **how to drive each**.
- **Taste examples (needs-tim):** feel of a drag, "looks right".
- **Invocation:** `/company-build` · "continue the build" · "build status" · "stop the build".

### Δ rhm-build — the RHM Walkthrough & Review Organ

- **Skill description (frontmatter):** Autonomous cron-driven parallel build loop for the RHM
  Walkthrough & Review Organ. Reads the build-prep criteria + S1-S7 scenarios, builds the next
  buildable file-disjoint lanes in parallel, verifies by USE (browser + voice + adversarial S6)
  against the scenarios, marks/commits on the rhm-walkthrough-organ branch, flags what needs Tim.
  Invoke via the cron, or "continue the rhm build" / "rhm build status".
- **Scope:** the organ; every criterion verified **inside a passing multi-part scenario (S1–S7)**.
  "Mirrors /company-build; same discipline."
- **PLAN:** `…/build-prep/RHM Walkthrough Organ — Completion Criteria.md` (the criteria doc also
  carries the S1–S7 scenarios + build order + lanes) + Guide + Synthesis.
- **Branch (historical, superseded):** `rhm-walkthrough-organ`, off `operable-surface`; NEVER
  commit to `main` or `operable-surface`. Tag `[rhm-organ]`, message form
  `"[rhm-organ] <criterion>: <what> (verified by S#)"` — scenario id in the by-use note.
- **STATE dir:** `.build/rhm/`.
- **Lanes** (see state.json + Guide "Parallelization"):
  - **CONTRACTS** — `contracts/address.py` (add `ui` scheme) + NEW `contracts/ui_info.py` (the
    ui-component-registry shape). Independent.
  - **SCHED** — `runtime/compile.py` + `runtime/scheduler.py` + NEW `nodes/gate.py`. B5
    branching: per-port addresses + selective emit + a `gate` node ("branch not taken" =
    port-address never written). Independent.
  - **CORE** — `runtime/governance.py` + `runtime/suite.py` + `runtime/bridge.py` +
    `store/fs_store.py`. The big shared-hot-file backend pass: G1 (wire `guard()`/POLICY into the
    APPLY paths + AUTO mutators — propose stays unguarded; mirror `apply_node`); A (review class +
    separate `status` field + `origin` polarity + `surface_review`); D (reuse
    `coa`+`resolve_surfaced`, session-tag, `session_view`, actionable WHY, fail-safe to raw
    payload); B-backend (session-as-graph + a human-writable `go`-gate per node + atomic
    `save_session`); E (`review_verdicts`, `commit_criterion` with the
    `derived_from`=resolve-`seq` three-part-bind gate, mirror `apply_node`); C1-backend
    (`build_ui_info`/`/api/ui_info`, sibling of object_info). Depends on CONTRACTS' `ui_info`
    shape (code against it).
  - **UI** — `canvas/app/src/App.tsx` (+`app.css`). C2 KEYSTONE (extend `show` → `ui://`
    resolver: canvas→camera reuse, chrome→DOM scroll+spotlight), C3 present-in-place (portal +
    DOM), C5 (`data-ui-ref` handles on chrome; render-from-registry opt-in — keep
    edges/node-shape/chat/grow imperative-but-pointable), B-frontend (walkthrough surface +
    "Next" + N-of-M), F (voice per-step, text-config, fail-safe), `review.advance`
    stream-dispatch. **After CONTRACTS+CORE.**
  - **X** — `runtime/suite.py` (after CORE; same file): E3 (the loop reads verdicts →
    `commit_criterion` → requeue, no middleman) + G3 (`decide-for-me` deterministic dispatcher on
    `posture(class)`, NO confidence).
- **Verify specifics:** bridge log `/tmp/bridge-rhm.log`; `refresh_self_description` if
  node-types/verbs changed (e.g. the `gate` node); UI/voice — drive the actual scenario step
  (start a walk, watch the canvas move to a `ui://` target, respond, Next, see N-of-M); Console
  MUST be clean. Scenarios: **S1** the canonical walk (the spine) · **S2** unscripted question →
  non-node target · **S4** branching · **S5** deterministic routing, run twice = identical, no
  confidence value anywhere · **S6** ADVERSARIAL: un-provenanced + mismatched verdict both refuse
  · **S7** voice→text fallback, resume-after-drop. (S3 is not enumerated in the recipe's verify
  list — the criteria doc holds the full set.)
- **Channel-back (E3) — unique details beyond the protocol's step 8:**
  `review_verdicts(since)` is the approve-only slice; `resolve_verdicts_since` is the sibling
  that also yields the negative ones the requeue path needs. Each verdict carries
  `seq · surfaced · choice · reason`; the criterion_id comes from the surfaced item's payload
  (the build need it answered). Requeues go through the SAME inbox (`surface_review`).
- **Stopping:** `.build/rhm/WALKTHROUGH.md` (what's verified by which scenario · needs-Tim ·
  blocked). **Recursive payoff:** the FIRST live run of the organ is the operable-surface
  walkthrough (S1) — surface those items and let Tim drive.
- **Taste examples:** voice naturalness, exact spotlight aesthetics.
- **Laws additions:** deterministic-gates/no-confidence · no-bypass (RHM presents/surfaces, only
  Tim resolves) · reuse-don't-parallel (extend `coa`+`resolve`+inbox+scheduler+the registry
  pattern — no second decision/record/render system; `ui_info` is a sibling of object_info, not
  an edit to it).
- **Invocation:** `/rhm-build` · "continue the rhm build" · "rhm build status" · "stop the rhm
  build".

### Δ wire-build — the Decision→Implementation Wire + Product-Level Surface

- **Skill description (frontmatter):** Autonomous cron-driven parallel build loop for the
  Decision→Implementation Wire + Product-Level Surface. Reads the plan-reviewed triad + scenario
  S8, builds the buildable file-disjoint lanes in parallel (UX ∥ WIRE-BE → WIRE-LOOP), verifies
  each criterion by USE (S8 unattended circuit + adversarial refusals for the wire; browser +
  screenshot for the surface), commits per criterion on the decision-wire-and-surface branch
  under the repo's commit law, flags what needs Tim. Invoke via the cron, or "continue the wire
  build" / "wire build status" / "stop the wire build".
- **Scope:** "Mirrors /rhm-build + /company-build; same discipline." Closes the headline
  capability — a recorded decision → autonomously implemented by Claude Code → verified → result
  fed back → item closed, **no human re-prompt** — AND brings the canvas surface to a
  complete-product bar (**RUN-fix first**).
- **PLAN:** `…/build-prep/Decision-to-Implementation Wire + Product Surface — Completion
  Criteria.md` (+ Guide, Synthesis) — **plan-reviewed, 2 rounds, converged**. Launch-channel
  detail: `…/build-prep/research-claude-code-launch/`.
- **Branch (historical, superseded):** `decision-wire-and-surface`, off `rhm-walkthrough-organ`;
  NEVER commit to `main` / `operable-surface` / `rhm-walkthrough-organ`. Tag `[wire]`, message
  form `"[wire] <criteria-ids>: <what> (verified by S8/use)"`.
- **STATE dir:** `.build/wire/`.
- **Lanes:**
  - **UX** — `canvas/app/src/App.tsx` + `app.css`. U1–U12 (Group U). **U1 first** (the RUN latch:
    call-site fix `onClick={() => doRun()}` at App.tsx:1036 + a try/catch/finally for U4 — see
    Guide §U1). Independent → wave 1.
  - **WIRE-BE** — NEW `runtime/implement.py` + `runtime/suite.py` + `runtime/governance.py` +
    `store/fs_store.py`. W1,W2,W3,W4,W5,W7. The wire backend. Independent of UX (file-disjoint) →
    wave 1.
  - **WIRE-LOOP** — this SKILL's §8 dispatch step + the watcher increment in
    `runtime/implement.py`. W6 (unattended). **After WIRE-BE verified.**
- **Verify specifics:** bridge log `/tmp/bridge-wire.log`; `refresh_self_description` if a
  verb/type/capability changed; UX via chrome-devtools on :5173 — navigation "timeout" is the SSE
  quirk, the page renders; select the page + screenshot. Drive the real flow: **U1 = click RUN,
  confirm the POST fires, no latch, recover from a failed run**; screenshot each Group-U item;
  Console MUST be clean. **S8 parts:** 1 happy unattended · 2 forged seq refuses · 3 bad
  implementation re-queues · 4 LOCKED/consequential gated BEFORE dispatch · 5 exactly-once across
  overlap/crash · 6 scope-overrun surfaces back · 7 concurrency cap + loud defer. Adversarial
  examples: forge a dispatch, race two fires, write `implemented` on a failed build, exceed
  declared scope.
- **Commit law (fullest form — promoted into the protocol's step 7):**
  `Suite.refresh_self_description()` for factual blocks (run on apply); `AGENTS.md`/`MAP.md`/
  `STATE.md` + the module `AGENTS.md` prose by integration; `tests/drift_acceptance.py` must pass
  before commit. Commit per coherent criterion-unit.
- **Channel-back (E3 + the NEW dispatch, W6 UNATTENDED) — the full mechanism:** the increment is
  **`runtime/implement.drive_dispatchable`** — ONE bounded watcher pass; the loop calls it and
  persists the returned cursor so the unattended circuit closes with no human re-prompt. Each
  fire after step 7:
  - **Crashed mid-flight first:** `implement.resurface_crashed(suite)` — a `decision.dispatch`
    claim with NO terminal event (`decision.implemented`/`decision.verify` for that same
    `derived_from`) launched then died. `dispatch_decision` CORRECTLY refuses to re-launch it
    (exactly-once — the claim event is durable), so it is RE-SURFACED loud (a new responsive
    review item + a `decision.crashed` marker keyed on the seq so it is re-surfaced exactly
    once), NEVER silently dropped (no silent dead end).
  - `verdicts = suite.resolve_verdicts_since(verdict_cursor)` — event **dicts**: use `v["seq"]`,
    `v["surfaced"]`, `v["choice"]`, NOT attribute access; process in `seq` order:
    - **Auto-dispatchable** iff (deterministic, no confidence) `v["choice"]=="approve"` AND
      `suite.is_build_intent(suite.inbox.get(v["surfaced"]))` (the §W2 discriminator —
      `payload["intent"]=="build"`) AND `posture(declared_class)==AUTO` (the ONLY class that
      auto-runs; `declared_class = payload["consequence_class"]`, default `"decision_build"`,
      which IS `AUTO` in `governance.POLICY`). Then
      `suite.dispatch_decision(v["surfaced"], v["seq"], launcher=…, verifier=…)` — signature
      `dispatch_decision(sid, derived_from, *, launcher=None, verifier=None, repo=None)`; it
      **first** takes the per-seq lock + checks the `decision.dispatch` event log (exactly-once),
      verifies the three-part bind (kind=resolve · surfaced==sid · choice=approve), enforces the
      posture==AUTO pre-gate + the deny-all empty scope, then launches → verifies → writes
      `implemented` (guarded on the verdict) or surfaces back. A `LaunchError` is turned into a
      loud re-queue INSIDE the verb (returns `{requeued,…,launched:False}`) — it does not raise
      for a crashed launch.
    - **CONFIRM/SURFACE/LOCKED** declared class (`posture(declared_class)!=AUTO`) → leave for the
      operator (surfaced; do NOT auto-dispatch). `dispatch_decision` also refuses these itself
      (no-bypass).
    - `choice==approve` AND build-criterion (not build-intent) → `commit_criterion` (the existing
      E3 path).
    - reject/needs-change → `requeue_from_verdict`.
  - **§W7 concurrency cap:** `drive_dispatchable` dispatches at most `implement.CONCURRENCY_CAP`
    (env `COMPANY_WIRE_CONCURRENCY`, default 3) per pass; the remainder is DEFERRED loud (a
    `decision.deferred` event + the returned `deferred` list) and re-offered next pass — NEVER
    silently truncated. The cursor only advances past CONSUMED verdicts (dispatched or terminally
    routed), so a deferred verdict is re-read next pass.
  - Advance `verdict_cursor` to the returned `cursor` (max `seq` consumed); persist.
    **Exactly-once does NOT rely on the cursor** (the `decision.dispatch` event is the guarantee)
    — the cursor is a coarse guard only, so a crash/re-fire can never double-launch.
  - **Operator-only:** the loop READS verdicts + WRITES derived dispatches/statuses; it NEVER
    calls `resolve`/`resolve_surfaced`. Only `/api/resolve` writes the operator `resolved` field.
    `dispatch_decision` writes the `status` lane (`implemented`) only.
- **Stopping:** `.build/wire/WALKTHROUGH.md` (verified-by-which-scenario · needs-Tim · blocked).
  **Recursive payoff:** the wire's first real run is a decision *you* record being implemented
  autonomously and shown back — and the RHM organ walks you through reviewing it.
- **Taste examples:** exact spotlight aesthetics, copy tone, icon set.
- **Laws (wire's enumeration):** the repo's 8 rules (AGENTS.md): build against contracts ·
  schema-additive (bump `schema_ver`) · one source · fail loud · ext4 storage · NO Gemini ·
  stage-gated (SURFACE cross-cutting, CONFIRM irreversible) · author from the registry, never
  invent (ASK don't fabricate). PLUS: deterministic gates/no-confidence · no-bypass
  (authorization is the substrate-read `derived_from` seq-bind, never a caller flag; **the wire
  is off the MCP face**; only the operator resolves) · operator-only resolve (code writes the
  `status` lane only — `implemented` — NEVER the `resolved` field) · exactly-once (the
  `decision.dispatch` event keyed on the resolve `seq`, checked before launch) ·
  reflects-never-owns · reuse don't parallel (extend `coa`/`resolve`/inbox/the bind/`apply`
  pattern — no second decision/build/queue system) · every change updates the self-description
  (drift must pass) · read the module AGENTS.md before editing it · FORM is half of done · prove
  by USE inside a scenario.
- **Invocation:** `/wire-build` · "continue the wire build" · "wire build status" · "stop the
  wire build".

---

## DISPOSITION TABLE (proposed, never executed)

| Source file | Disposition | Reasoning |
|---|---|---|
| `docs/methodology/company-build.md` | **keep** (full text, untouched now) → *optional* keep-as-pointer later, ONLY in lockstep with `~/.claude/skills/company-build/SKILL.md` (both-or-neither, per the README mirror contract) | Byte-mirror of a live skill + the as-ran record of the operable-surface build (its protocol variant — unit-verify, no channel-back — is historical fact, not drift to erase). |
| `docs/methodology/rhm-build.md` | **keep** (full text, untouched now) → same conditional pointer option | Byte-mirror of a live skill + as-ran record; sole holder of S1–S7 verify detail and the E3 channel-back prose. |
| `docs/methodology/wire-build.md` | **keep** (full text, untouched now) → same conditional pointer option | Byte-mirror of a live skill + as-ran record; sole holder of the W6 unattended-dispatch mechanism and the fullest commit-law/laws text (which the protocol page promotes to canonical). |
| `docs/methodology/build-loop-protocol.md` (NEW, proposed) | **fold-in target** — create from §CONSOLIDATED TEXT above; add one line to `docs/methodology/README.md` pointing at it | The one-source methodology page the drift radar asked for; the landing place for protocol improvements; the instantiation source for future loops (which today fork-and-drift). |
| `docs/methodology/remediation-build.md` + unmirrored sibling skills (voice/cognition/mockup/interactive-surface/workshop/unified) | **out of this lane's scope — flagged** | Same family; the owning session should extend the protocol page's delta list to them in a later pass. |

**Retire: nothing.** Consolidation here is additive (one new one-source page), because the
sources are simultaneously (a) mirrors of live runnable skills, (b) self-contained prompts for
unattended cron agents, and (c) historical records of an intentionally evolving protocol.

**Open flags for the owning session (restated):** branch rules in all three are superseded by the
no-branches law (2026-06-04) — protocol page states commit-to-main, deltas preserve history;
worker-mode `auto` vs `bypassPermissions` and the unhardened company bridge-restart are marked
[VARIANT] for canonization; any future thinning of the repo docs must change the live skills in
the same commit.
