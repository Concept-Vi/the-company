---
name: remediation-build
description: Use to autonomously fix the cross-layer defects in the Company repo found by the verification review — the unification/completion/connection loop. Reads the Master Remediation Spec, builds the buildable file-disjoint lanes in parallel (BACKEND ∥ TESTS ∥ DATA-HYGIENE → VERIFY), verifies each criterion by USE against the operator's END-TO-END path (the seam, not the cell), commits per criterion on the remediation branch, flags what needs Tim. FORM/front-end is a SEPARATE session, out of this loop's scope. Invoke via the cron, or "continue the remediation" / "remediation status" / "stop the remediation".
---

# Remediation Build Loop (unification · completion · connection)

Cron-driven, parallel, crash-safe. Fixes the defects the three-loop verification review found — the passes that never happened **across** the stacked builds. Descends from `company-build`; the one new spine: **verify the SEAM, not the cell.** Every Tier-0 defect was a *connection* failure that within-silo verification missed, so this loop's verify step drives the **operator's real end-to-end path across layers**, never the unit in isolation.

## Scope (and what's deliberately OUT)
IN: BACKEND correctness/connection, TESTS coverage of the unproven subsystems, DATA-HYGIENE. **OUT: the FORM / front-end rebuild** (`canvas/app/**`) — that is its own session with the spec §4 as its brief (gated on the design-system decision G0). This loop must NOT touch `canvas/app/**` except where a backend contract change requires the FE to be *informed* (note it; don't rebuild). Sidestepping `canvas/` also means this loop never trips the FORM auto-close gate.

## Files (the plan — Windows-side vault; read each fire)
- SPEC (source of truth): `/mnt/c/Users/Workstation001/Documents/Claude/Projects/counterpart/the Company/build-prep/Unification, Completion & FORM — Master Remediation Spec.md` — §3 findings ledger (the criteria, by ID), §5 per-file map, §6 completion criteria, §7 lane partition.
- REPO: `/home/tim/company` — **branch `remediation` off `main`** (create it; never commit to `main`). venv `./.venv`. bridge :8770. (canvas :5173 only for VERIFY drives, never edited here.)
- STATE: `/home/tim/company/.build/remediation/state.json` (gitignored) — coordination substrate. `.build/remediation/lanes/<lane>.report.json` — single-writer per-lane completion markers. `.build/remediation/loop.lock` — overlap guard.

## Lanes (file-disjoint → safe parallel; from spec §7)
- **BACKEND** — `runtime/suite.py` `runtime/bridge.py` `store/fs_store.py` `runtime/governance.py` `runtime/implement.py`. **(`panels/settings.json` is deliberately NOT in this territory — see the T3-SETTINGS hard guard below; seed T3-SETTINGS as `blocked` at cold-start, never in a lane.)** Criteria: T0-WIRE (a real entry seam so a build can be triggered from a face), T0-KEYSTONE (stamp a registry-valid `ui_target` into the payload), T1-EMIT (dispatch-claim fail-loud, no swallow), T1-SEQ (lock `append_event`), T1-RACE (per-graph mutation lock + atomic `save_surfaced`), T3-MODE (expose `MODE_DIRECTIVES` via capabilities), T3-STATUS (backend `stuck` status), T3-HYGIENE (tag-test-items-at-source half). One lane — these are the shared hot files; never split them across parallel workers.
- **TESTS** — new `tests/*.py` only (disjoint from everything). Criteria: T2-RHM-COVERAGE (walkthrough session lifecycle + `ui://` resolver + governance refusals), T2-EMBED-GATE (embed→similarity→retrieve against live BGE-M3 :8001; gate/branching), T3-SESSION-CHURN guard (fs_store session methods). Independent; runs anytime.
- **DATA-HYGIENE** — no source contention. Purge/namespace store test-pollution (`ADV-*`/`atk-*`/`g1-3`/`ADVERSARIAL-TEST-*`), reseed a clean demo graph, gitignore the stray `mcp_registration_debug.log`. Independent; runs anytime. **Commit model:** the ONLY committable artifact here is the one `.gitignore` line; the purge/reseed mutate gitignored `.data/store` and commit nothing — verify those by **state-inspection** (`/api/inbox` returns clean items; the demo graph loads), not by a commit.
- **VERIFY** — runs after BACKEND lands. The real end-to-end proofs (T0-WIRE + T2-WIRE-YOUNG): several real, varied, scoped wire runs from a real face, incl. one that breaks a suite (must surface-back, not close). Depends on the BACKEND entry seam existing.

Wave 1 = BACKEND ∥ TESTS ∥ DATA-HYGIENE (all file-disjoint). VERIFY last.

## Buildable vs closeable — and the split-criterion rule (READ BEFORE DISPATCHING)
A criterion being *buildable* (codeable in-scope this loop) does NOT mean it is *closeable* (can reach `verified` in-scope). Spec §3 assigns four criteria to **BACKEND + FRONTEND**, and FRONTEND is OUT of this loop. Handle them precisely:
- **T0-KEYSTONE, T3-MODE, T3-STATUS** — build ONLY the backend half (stamp the field / expose the directives / add the `stuck` status). The FE half (canvas view-drive, deleting the duplicated copy, painting status) is out of scope. These criteria can reach **at most `needs-tim`** this loop — never `verified`. Set the state status to **`needs-tim`** (the stop condition already accepts it) with the note `partial-fe-pending: backend half landed + unit-proven; FE-half pending the FORM session`. Do NOT invent a separate `partial-fe-pending` *status* — it's a note on `needs-tim`, so the stop condition and the step-4 skip-list cover it unchanged.
- **T3-SETTINGS — DO NOT TOUCH `panels/settings.json` this loop.** Its fix needs `options_from` support that lives in `App.tsx fieldsFor` (FE, out of scope). Switching the JSON to `options_from` WITHOUT the FE half **breaks the live panel** — shipping a regression, not a fix. Mark it `blocked` with reason "paired with FE — belongs to the FORM session." This is a hard guard, not a judgement call.
- **T3-HYGIENE spans two lanes** (BACKEND owns *tag-test-items-at-source*; DATA-HYGIENE owns *purge + gitignore*). **BACKEND owns the criterion ID** and only marks it done once BOTH halves report; DATA-HYGIENE writes its half as a sub-note in its own report, not a duplicate ID claim.
- **T4-SUITE / T4-HUD** — opportunistic/structural; T4-HUD is FE (out). Do not dispatch T4 as a criterion; a worker may tidy within its own territory only if it doesn't risk the lane.
- **T0-WIRE vs T2-WIRE-YOUNG (the two halves of "the wire works")** — distinct criteria, distinct owners. **T0-WIRE** = the entry seam EXISTS and reaches a result; it is owned by BACKEND and reaches **`verified`** as soon as step 6's single end-to-end seam-drive (trigger from a real face → result) + the reachability grep + the adversarial re-check pass. **T2-WIRE-YOUNG** = reliability across *several varied real runs incl. one that breaks a suite*; it is owned by the **VERIFY** lane, is a separate criterion, and does NOT gate T0-WIRE. One good drive closes T0-WIRE; the reliability battery closes T2-WIRE-YOUNG.

## Each fire (one bounded wave)
0. **Cold-start (first fire only).** If `.build/remediation/` doesn't exist: create the `remediation` branch off `main` (`git checkout main && git checkout -b remediation`), `mkdir -p .build/remediation/lanes`, and seed `state.json` with every lane `todo` + each lane's criteria (by spec ID, per §7) and file territory. `.build/` is gitignored — correct.
1. **Lock or exit.** If `.build/remediation/loop.lock` exists and is <20 min old → exit. Else write it (timestamped). Always remove on exit.
2. **Read** state.json + the SPEC (§3 criteria, §5 file map, §6/§7) + the buildable-vs-closeable rule above.
3. **Ingest finished lanes:** for each `.build/remediation/lanes/*.report.json` newer than its state entry → built-unverified; go to verify (step 6).
4. **Compute buildable lanes:** status `todo` whose deps are met (BACKEND/TESTS/DATA-HYGIENE anytime; VERIFY after BACKEND verified). Skip `in-progress` (reclaim if stale >25 min) / `verified` / `blocked` / `needs-tim`.
5. **Dispatch buildable lanes IN PARALLEL** (Agent, mode auto, run_in_background). Each worker prompt MUST: read `/home/tim/company/AGENTS.md` → `MAP.md` → `STATE.md` → its module's `AGENTS.md` FIRST; implement ONLY its lane's criteria (by spec ID) in ONLY its file territory; **NOT commit, NOT edit criteria, NOT touch `canvas/app/**`**; obey the laws (registry-is-truth, schema-additive, fail-loud, no Gemini, **preserve what holds — spec §3 "what holds"**); on finish write `.build/remediation/lanes/<lane>.report.json` = `{lane, criteria:[...], files:[...], how_verified, preserved, notes}`. Mark each `in-progress`. Then exit (next fire verifies when reports land).
6. **Verify built-unverified lanes — BY USE, AT THE SEAM:**
   - If backend (.py) changed → **restart the bridge**: `pkill -f 'bridge.py 8770'; cd /home/tim/company && ./.venv/bin/python runtime/bridge.py 8770 &` (~3s).
   - Run the named acceptance suites + `tests/drift_acceptance.py`.
   - **Seam test (the spine):** drive the OPERATOR'S END-TO-END PATH, not the function. T0-WIRE → trigger a build from a real face (chat/MCP/HTTP) and confirm it flows to a reviewable result — NOT by calling `surface_build_intent` directly. T0-KEYSTONE → confirm a real walk drives the view. A criterion that passes its unit but is unreachable from a face is **NOT done** (that is the whole bug class this loop exists to kill).
   - **Reachability check:** for any new/fixed capability, grep that a real face (`bridge.py` route or `mcp_face/server.py` tool) or a test actually calls it. Built-but-unreferenced = not done.
   - **Adversarial re-check:** dispatch a SEPARATE agent per just-verified criterion to DISPROVE "done" (find the failing case, incl. concurrency for T1-RACE/SEQ, silent-failure injection for T1-EMIT). Verified only if it survives.
   - **Flag, never green-paint:** anything not confirmable headlessly → `needs-tim` with a note, NOT verified.
7. **Mark + commit per criterion:** update the SPEC §3 (mark the ID done with a one-line by-use note), update `STATE.md`/`MAP.md` if a capability changed, then commit ONLY the touched files by path on `remediation`: `git add <paths> && git commit -m "[remediation] <ID>: <what> (verified by use at the seam)"` + the Co-Authored-By trailer. Update state.json.
8. **Blocked:** a lane failing verify twice → `blocked` with reason; move on (never stall).
9. **Release lock. Exit.**

## Stopping → the walkthrough
When every criterion is `verified`, `blocked`, or `needs-tim` (none `todo`/`in-progress`): write `/home/tim/company/.build/remediation/WALKTHROUGH.md` (what's verified at the seam · what needs Tim's eyes · what's blocked + why · how to drive each end-to-end · the FORM lane still pending its own session) and **PushNotification** Tim. Do not delete the cron (Tim ends it).

## Laws (bind every worker — from the repo constitutions + spec §8)
Build against contracts · schema-additive (optional fields, bump schema_ver) · registry is the source of truth, never fabricate · **fail loud (no silent fallback/swallow — this loop FIXES a swallow, never adds one)** · ext4 store · NO Gemini · canvas REFLECTS never owns · update self-description as part of the change (`drift_acceptance` must pass) · **prove by USE at the seam, never code-reading, never a green label** · preserve what spec §3 says holds (operator-only resolve, the wire's structural gates, registry-fed models). Do NOT touch `canvas/app/**`.

## Invocation
`/remediation-build` (the cron) · "continue the remediation" (resume) · "remediation status" (read state.json + SPEC, report, don't run) · "stop the remediation" (delete the cron).
