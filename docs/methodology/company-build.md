---
name: company-build
description: Autonomous cron-driven parallel build loop for the Company operable composition surface. Reads the build-prep completion criteria, builds the next buildable file-disjoint lanes in parallel, verifies by use + adversarially, marks/commits on the operable-surface branch, flags what needs Tim's eyes. Invoke via the */10 cron, or "continue the build" / "build status".
---

# Company Build Loop (operable composition surface)

Cron-driven, parallel, crash-safe. Builds criteria **A–G** of the operable surface, verifies each by USE + an adversarial re-check, and surfaces a walkthrough when done. The whole build runs autonomously; Tim reviews at the very end.

## Files (the plan — Windows-side vault; read each fire)
- CRITERIA: `/mnt/c/Users/Workstation001/Documents/Claude/Projects/counterpart/the Company/build-prep/Operable Composition Surface — Completion Criteria.md`
- GUIDE: `…/build-prep/Operable Composition Surface — Implementation Guide.md`
- SYNTHESIS: `…/build-prep/Operable Composition Surface — Research Synthesis.md`
- REPO: `/home/tim/company` — **branch `operable-surface`** (never commit to `main`). venv `./.venv`. canvas `canvas/app` (vite :5173). bridge :8770.
- STATE: `/home/tim/company/.build/state.json` (gitignored) — the coordination substrate. `/home/tim/company/.build/lanes/<lane>.report.json` — per-lane completion markers (single-writer, no race). `/home/tim/company/.build/loop.lock` — overlap guard.

## Lanes (file-disjoint → safe parallel; see GUIDE "Parallelization")
- **E — Embeddings**: `fabric/transport.py` `fabric/client.py` `fabric/config.py` + NEW `nodes/embed.py` `nodes/similarity.py` `nodes/retrieve.py`. (E1–E5) — independent, runs anytime.
- **N — Node configs**: a `CONFIG` block per existing `nodes/*.py` (ask/codebase/constant/join/llm/model_of_tim/pair/portal/rhm_mode/titlecase/uppercase/wordcount). (A1) — independent.
- **K — Backend surface**: `runtime/suite.py` `runtime/bridge.py` `store/fs_store.py` — create_node seeding(A) · atomic save_graph + set_position + position-in-state + /api/move(C5) · graph_id threading + /api/graphs(C4) · per-port edges in state(C2/C3) · per-kind models + /api/models(B) · force in /api/run(D4) · events_since + /api/stream(G) · wire /api/set(A3). One lane (shared hot files).
- **U — Canvas**: `canvas/app/src/App.tsx` only — config form + api.set(A2) · model dropdowns(B) · port nubs + drag(C1) · graph picker(C4) · loadGraph rewrite + drag-listener + persistenceKey camera-only(C5) · force button(D4) · EventSource(G). **Depends on K's endpoints** → only buildable once K is verified.
- **F — Act on outputs**: composes last (depends on C+U).

## Each fire (one bounded wave)
1. **Lock or exit.** If `.build/loop.lock` exists and is <20 min old → exit (a wave is running). Else write it (with timestamp). Always remove on exit.
2. **Read** state.json + CRITERIA + the relevant GUIDE sections.
3. **Ingest finished lanes:** for each `.build/lanes/*.report.json` newer than its state entry → that lane's code is built-unverified; go to verify (step 6).
4. **Compute buildable lanes:** lanes with status `todo` whose deps are met (E,N,K anytime; U after K verified; F after C+U). Skip `in-progress` (unless stale >25 min → reclaim) / `verified` / `blocked` / `needs-tim`.
5. **Dispatch buildable lanes IN PARALLEL** (Agent, mode auto, run_in_background). Each worker prompt MUST: read `/home/tim/company/AGENTS.md` → `MAP.md` → `STATE.md` → its module's `AGENTS.md` FIRST; implement ONLY its lane's criteria in ONLY its file territory; **NOT commit, NOT edit criteria**; obey the laws (registry-is-truth, schema-additive, fail-loud, no Gemini); on finish write `.build/lanes/<lane>.report.json` = `{lane, criteria:[...], files:[...], how_verified, preserved, notes}`. Mark each in state `in-progress`. Then exit (next fire verifies when reports land).
6. **Verify built-unverified lanes (by USE):**
   - If backend (.py) changed → **restart the bridge**: `pkill -f 'bridge.py 8770'; cd /home/tim/company && ./.venv/bin/python runtime/bridge.py 8770 &` (give it ~3s).
   - Backend: run the named acceptance tests `./.venv/bin/python tests/<t>.py` + `tests/drift_acceptance.py`; hit the new endpoints via curl.
   - UI: chrome-devtools MCP on `http://localhost:5173` — actually DO the thing the criterion claims (add a node, open its inspector, set a field, run, see output, drag a port, watch a pushed update). Screenshot.
   - **Adversarial re-check (FUNCTION):** dispatch a SEPARATE agent per just-verified criterion whose job is to DISPROVE "done" (find the case where it fails). A line is `verified` only if it survives.
   - **Design-critic (FORM — every operator-facing surface, mandatory, separate agent):** the function-verifier defaults to "does it work" and cannot judge form. Dispatch a SEPARATE browser-driving **design-critic** judging the product face against the **design rubric** (built on the design system's components + tokens, NO hardcoded/bespoke · no overlaps · responsive · consistent scale/type/spacing · settings consolidated · navigable visual/spatial, not a text-wall · empty/loading/error states · outcome demonstrable). The FORM face of a criterion is green ONLY if it passes; a design-lint fails the build on off-token/bespoke where machine-checkable. FORM is half of done (AGENTS.md rule 9), not a later pass.
   - **Flag, never green-paint:** genuinely subjective taste (feel of a drag, "looks right") → mark `needs-tim`, NOT verified. (A bespoke/overlapping/off-design-system surface is NOT taste — it FAILS form.)
7. **Mark + commit per criterion:** check the box in CRITERIA (replace `☐`→`✅`/`◑` with a one-line by-use note), update `STATE.md`/`MAP.md` if a capability changed, then commit ONLY the touched files by path on `operable-surface`: `git add <paths> && git commit -m "[operable-surface] <criterion>: <what> (verified by use)"`. NO Co-Authored-By / attribution trailer. Update state.json.
8. **Blocked:** a lane failing verify twice → `blocked` with reason; move on (never stall).
9. **Release lock. Exit.**

## Stopping → the walkthrough
When every criterion is `verified`, `blocked`, or `needs-tim` (none `todo`/`in-progress`): stop dispatching, write `/home/tim/company/.build/WALKTHROUGH.md` (what's verified · what needs Tim's eyes · what's blocked + why · how to drive each), and **PushNotification** Tim that the build is ready for his walkthrough. Do not delete the cron (Tim ends it).

## Laws (bind every worker — from the repo constitutions)
Build against contracts · schema-additive (optional fields, bump schema_ver) · registry is the source of truth, never fabricate · fail loud (no silent fallback/cache) · ext4 store · NO Gemini · canvas REFLECTS never owns (edges/positions backend-authoritative; drag round-trips through /api) · update self-description as part of the change (`drift_acceptance` must pass) · **FORM is half of done** (any operator-facing surface is built on the design system — components + tokens, NEVER bespoke/hardcoded; function-only is NOT done; FORM verified by a SEPARATE design-critic + a fail-loud design-lint — AGENTS.md rule 9) · prove by USE — FUNCTION *and* FORM — never code-reading. tldraw installed = **3.15.6**.

## Invocation
`/company-build` (the cron) · "continue the build" (resume) · "build status" (read state.json + CRITERIA, report, don't run) · "stop the build" (delete the cron).
