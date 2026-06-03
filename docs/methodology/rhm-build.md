---
name: rhm-build
description: Autonomous cron-driven parallel build loop for the RHM Walkthrough & Review Organ. Reads the build-prep criteria + S1-S7 scenarios, builds the next buildable file-disjoint lanes in parallel, verifies by USE (browser + voice + adversarial S6) against the scenarios, marks/commits on the rhm-walkthrough-organ branch, flags what needs Tim. Invoke via the cron, or "continue the rhm build" / "rhm build status".
---

# RHM Walkthrough Organ — Build Loop

Cron-driven, parallel, crash-safe. Builds the organ, verifies each criterion **inside a passing multi-part scenario (S1–S7)** by USE, surfaces a walkthrough when done. Mirrors `/company-build`; same discipline.

## Files
- CRITERIA (+ S1–S7 scenarios + build order + lanes): `/mnt/c/Users/Workstation001/Documents/Claude/Projects/counterpart/the Company/build-prep/RHM Walkthrough Organ — Completion Criteria.md`
- GUIDE: `…/build-prep/RHM Walkthrough Organ — Implementation Guide.md` · SYNTHESIS: `…/build-prep/RHM Walkthrough Organ — Research Synthesis.md`
- REPO: `/home/tim/company` — **branch `rhm-walkthrough-organ`** (off `operable-surface`; NEVER commit to `main` or `operable-surface`). venv `./.venv`. canvas `canvas/app` (:5173). bridge :8770.
- STATE: `/home/tim/company/.build/rhm/state.json` · per-lane reports `.build/rhm/lanes/<lane>.report.json` · lock `.build/rhm/loop.lock`.

## Lanes (file-disjoint → safe parallel; see state.json + Guide "Parallelization")
- **CONTRACTS** — `contracts/address.py` (add `ui` scheme) + NEW `contracts/ui_info.py` (the ui-component-registry shape). Independent.
- **SCHED** — `runtime/compile.py` + `runtime/scheduler.py` + NEW `nodes/gate.py`. B5 branching: per-port addresses + selective emit + a `gate` node ("branch not taken" = port-address never written). Independent.
- **CORE** — `runtime/governance.py` + `runtime/suite.py` + `runtime/bridge.py` + `store/fs_store.py`. The big shared-hot-file backend pass: G1 (wire `guard()`/POLICY into the APPLY paths + AUTO mutators — propose stays unguarded; mirror `apply_node`); A (review class + separate `status` field + `origin` polarity + `surface_review`); D (reuse `coa`+`resolve_surfaced`, session-tag, `session_view`, actionable WHY, fail-safe to raw payload); B-backend (session-as-graph + a human-writable `go`-gate per node + atomic `save_session`); E (`review_verdicts`, `commit_criterion` with the `derived_from`=resolve-`seq` three-part-bind gate, mirror `apply_node`); C1-backend (`build_ui_info`/`/api/ui_info`, sibling of object_info). Depends on CONTRACTS' `ui_info` shape (code against it).
- **UI** — `canvas/app/src/App.tsx` (+`app.css`). C2 KEYSTONE (extend `show` → `ui://` resolver: canvas→camera reuse, chrome→DOM scroll+spotlight), C3 present-in-place (portal + DOM), C5 (`data-ui-ref` handles on chrome; render-from-registry opt-in — keep edges/node-shape/chat/grow imperative-but-pointable), B-frontend (walkthrough surface + "Next" + N-of-M), F (voice per-step, text-config, fail-safe), `review.advance` stream-dispatch. **After CONTRACTS+CORE.**
- **X** — `runtime/suite.py` (after CORE; same file): E3 (the loop reads verdicts → `commit_criterion` → requeue, no middleman) + G3 (`decide-for-me` deterministic dispatcher on `posture(class)`, NO confidence).

## Each fire (one bounded wave)
1. **Lock or exit.** `.build/rhm/loop.lock` <20min → exit. Else write epoch. Remove on exit.
2. **Read** state.json + CRITERIA (esp. S1–S7) + the relevant GUIDE sections.
3. **Ingest finished lanes:** each `.build/rhm/lanes/*.report.json` newer than its state entry → built-unverified → verify (6).
4. **Compute buildable:** `todo` lanes whose `deps` are all `verified` (CONTRACTS/SCHED/CORE anytime; UI after CONTRACTS+CORE; X after CORE). Skip in-progress (stale >25min → reclaim)/verified/blocked/needs-tim.
5. **Dispatch buildable lanes IN PARALLEL** (Agent, mode bypassPermissions, run_in_background). Each worker: read `/home/tim/company/AGENTS.md`→`MAP.md`→`STATE.md`→its module `AGENTS.md` FIRST; implement ONLY its lane in ONLY its territory; **NOT commit, NOT edit criteria**; obey the LAWS below; on finish write `.build/rhm/lanes/<lane>.report.json` `{lane,criteria,files,how_verified,preserved,notes}`. Mark in-progress. Exit.
6. **Verify built-unverified (by USE, against the SCENARIOS not units):**
   - Backend changed → restart bridge: `pkill -f '[b]ridge.py 8770'; cd /home/tim/company && setsid ./.venv/bin/python runtime/bridge.py 8770 >/tmp/bridge-rhm.log 2>&1 </dev/null & ` (~4s); run the relevant `tests/*.py` + `drift_acceptance.py`; curl new endpoints; **run refresh_self_description if node-types/verbs changed** (e.g. the `gate` node).
   - UI/voice → chrome-devtools on :5173: drive the actual scenario step (start a walk, watch the canvas move to a `ui://` target, respond, Next, see N-of-M). Screenshot. Console MUST be clean.
   - **Run the scenarios as they become possible:** S1 (the canonical walk) is the spine; S2 (unscripted question → non-node target), S4 (branching), S5 (deterministic routing, run twice = identical, no confidence value anywhere), S6 (ADVERSARIAL: un-provenanced + mismatched verdict both refuse), S7 (voice→text fallback, resume-after-drop).
   - **Adversarial re-check (FUNCTION):** a SEPARATE agent tries to DISPROVE each just-verified criterion *within its scenario*. Green only if it survives.
   - **Design-critic (FORM — every operator-facing surface, mandatory, separate agent):** a SEPARATE browser-driving critic judges the product face against the **design rubric** (built on the design system's components + tokens, NO hardcoded/bespoke · no overlaps · responsive · consistent scale/type/spacing · settings consolidated · navigable visual/spatial, not a text-wall · empty/loading/error states · outcome demonstrable). The FORM face is green ONLY if it passes; a design-lint fails the build on off-token/bespoke where machine-checkable. FORM is half of done (AGENTS.md rule 9).
   - **Flag, never green-paint:** genuinely subjective taste (voice naturalness, exact spotlight aesthetics) → `needs-tim`. (Bespoke/overlapping/off-design-system is NOT taste — it FAILS form.)
7. **Mark + commit per criterion** on `rhm-walkthrough-organ`: check the criteria box (`☐`→`✅`/`◑` + by-use note + scenario id), update `MAP`/`STATE` if a capability changed, `git add <paths> && git commit -m "[rhm-organ] <criterion>: <what> (verified by S#)"`. NO Co-Authored-By / attribution trailer. Update state.json.
8. **Channel-back — act on verdicts directly, NO markdown middleman (E3).** The loop READS the operator's recorded verdicts from the substrate and acts, instead of relaying through a markdown WALKTHROUGH file. Keep a `verdict_cursor` (an event `seq`) in `state.json` (loop state — NOT a suite method). Each fire, after step 7:
   - `verdicts = suite.resolve_verdicts_since(verdict_cursor)` — ALL resolve events (approve + reject/needs-change/decide), each carrying `seq · surfaced · choice · reason`. (`review_verdicts(since)` is the approve-only slice; `resolve_verdicts_since` is the sibling that also yields the negative ones the requeue path needs.)
   - For each verdict `v` (in `seq` order):
     - `choice == approve` → `suite.commit_criterion(criterion_id, v.surfaced, derived_from=v.seq)` — the three-part-bind gate (kind=resolve·choice=approve·surfaced==sid) turns resolved→done; the criterion_id comes from the surfaced item's payload (the build need it answered).
     - `choice` reject / needs-change / actionable-WHY → `suite.requeue_from_verdict(v.surfaced, derived_from=v.seq, note=v.reason)` — surfaces a NEW responsive `review` item through the SAME inbox (`surface_review`), carrying the actionable WHY. **You CANNOT edit the criteria markdown** (out of territory), so "a new criterion" = this requeued inbox item + (if it maps to a criterion change) a `needs-tim` flag in `state.json` — never an edit to the criteria doc.
     - `choice == comment`/`skip` are not resolve events (they don't reach this list), so nothing to do.
   - **Advance the cursor:** set `verdict_cursor` to the max `seq` consumed and persist `state.json`. Crash-safe: a re-fire re-reads from the cursor, never double-commits (commit_criterion binds to the unique `seq`, not the `sid`).
   - **Operator-only stays operator-only:** the loop READS verdicts and WRITES derived criteria/requeues. It NEVER calls `resolve`/`resolve_surfaced` — only the operator (UI channel) resolves. The loop has no resolve verb.
9. **Blocked** twice → `blocked` + reason; move on.
10. **Release lock. Exit.**

## Stopping → walkthrough
When every criterion is verified/blocked/needs-tim: write `/home/tim/company/.build/rhm/WALKTHROUGH.md` (what's verified by which scenario · needs-Tim · blocked) and **PushNotification** Tim. The recursive payoff: the FIRST live run of the organ is the operable-surface walkthrough (S1) — surface those items and let Tim drive. Don't delete the cron (Tim ends it).

> **WALKTHROUGH.md is a human SUMMARY, not the channel-back.** Tim's verdicts are acted on directly in-loop (step 8: `resolve_verdicts_since` → `commit_criterion`/`requeue_from_verdict`), reading the recorded verdict from the substrate — there is no markdown relay where the loop waits for a file to be hand-edited. The verdict→action path is the substrate (events + the inbox), not this file.

## Laws (bind every worker)
**DETERMINISTIC gates, NO confidence** (route on consequence/reversibility/LOCKED via POLICY) · **No-bypass:** every consequential action reads authorization from the substrate (POLICY, `is_approved`, `derived_from`=resolve-`seq` three-part-bind), never a caller flag; RHM presents/surfaces, only Tim resolves (operator-only) · **reflects-never-owns** (canvas drives via addresses; backend truth) · **reuse don't parallel** (extend `coa`+`resolve`+inbox+scheduler+the registry pattern — no second decision/record/render system; `ui_info` is a sibling of object_info, not an edit to it) · schema-additive · fail loud · ext4 · NO Gemini · update self-description (drift must pass) · **FORM is half of done** (any operator-facing surface is built on the design system — components + tokens, NEVER bespoke/hardcoded; function-only is NOT done; FORM verified by a SEPARATE design-critic + a fail-loud design-lint — AGENTS.md rule 9) · **prove by USE inside a scenario — FUNCTION *and* FORM — never code-reading.** tldraw = 3.15.6.

## Invocation
`/rhm-build` (cron) · "continue the rhm build" · "rhm build status" (read state.json + CRITERIA, report) · "stop the rhm build" (delete the cron).
