# The Remaining-Work Board (canonical, update-in-place — the two-track arrangement)

**Written 2026-06-10 at Tim's direction: the memory/brain system goes to a DESIGN CONVERSATION track
(no implementation until talked through — it ties into the UI work); everything else from the loop
program keeps moving via workflows/beats under my management, so the board is clear (or close) when
the design is implementation-ready. This file is the management substrate for that arrangement.**

## Track 1 — THE CONVERSATION (Tim + me; no building until talked through)

- **The memory & brain system** (GC15-deep): what the growing memory of Tim feels like from his side
  (visibility/curation), what belongs in it, per-agent projections — PLUS the mechanisms it rides:
  GC14 conditional/time-addressed self-injection, GC3 address-accumulation (fields by context),
  GC13 acceptance→build lifecycle. These four are ONE design conversation — the system's brain.
- **Ties into the UI/front-end** (the [M] lane): the walk surface, how memory presents, the
  deferred-27's return condition. The conversation's output feeds the eventual loop-prep triad for
  the implementation pass.
- **His pending one-word items:** the 3 proposed memory rows (verify_by_use ·
  verify_before_claiming · expand_dont_echo).

## Track 2 — THE BUILD BOARD (workflows/beats, managed by me, runs while we talk)

### B1 · G3 build (the data-chains seams) — the biggest remaining build
From G3-CASCADE-MULTIVAR-DESIGN.md, in its build order:
  a. `checks/` registry + the `check` step kind (deterministic gates as declared data) — NEW dir +
     loader (mirror pattern, parallel-safe) + run_cascade integration (serial, mine).
  b. `panel`/`jury` step kinds (executors exist) — run_cascade integration (serial, mine).
  c. S1 per-unit ctx in run_items ({field} templates) — additive engine change (serial, mine).
  d. S2 shared resolve-once block — AFTER the resolver-vocabulary decision (small design point;
     may fold into Track 1's edges).
  e. Re-express registry_generation as a saved cascade (the proof by use).
Workflow-ability: (a) lane-able (new files); (b)(c) serial on cognition.py — mine directly; (e) after.

### B2 · GC10 propose_flow — the gated path for agents to PROPOSE new code-chains
Mirrors propose_role: an agent submits a flow draft → surfaces → operator approve → lands. Single
lane, buildable by one worker with the flows/AGENTS.md + authoring.py context.

### B3 · The rolling programs (already one-call flows; fired in idle beats)
  - transcript_mine: ~14 in-band candidates + sessions as they settle (today's walk content included).
  - repo_ingest: hash-aware freshness as the repo changes.
  - drift_radar: re-sweep after significant growth.
  - pattern_cluster + memory_proposals: the grow-circuit, re-run after mining batches.

### B4 · The consolidation marks (the radar's 6 confirmed) — PROPOSE-NOT-APPLY
The methodology-docs triplet · MERGE-COORDINATION vs WORK-SPLIT · the live-resolution-surface
draft-pair (blocked on the chown) · the consent-test overlap · the briefs pair. These are CROSS-LANE
docs — the rule for workers: produce a consolidated DRAFT + a diff for the owning session's review,
never rewrite shared docs in place. Workflow-able with that rule baked in.

### B5 · The harness→system memory migration (batched, gated)
My ~80 harness memory entries → status='proposed' operator-memory rows where they're Tim-rules
(not project state), batched ≤5/run through the grow-circuit's conservatism, his confirms gating.
NOTE: project/state notes stay harness-side; only working-with-Tim knowledge migrates.

### B6 · Small bounded items
  - P8b: ingest-side path normalization (repo-basename prefix; relative-vs-root ambiguity refuses loud).
  - The G24-edge: ONE deterministic trailing-comma unit (fire with transport logging once, bounded).
  - Inbox litter: ~38 stale items flagged to owners (not mine to bulk-retire).
  - Standing Tim-reminders (outside the loop): key rotation · vhdx compaction · the
    live-resolution-surface chown.

### B7 · Eval #4 — after G3+GC10 land (the next capability wave), measuring the whole face again.

## The management protocol (how I run Track 2 while Track 1 talks)

Each loop beat: RUNNING-CHECK → ingest finished workers/flows → pick from B1→B7 in order (B3 fills
idle) → dispatch ONE workflow (file-disjoint lanes, workers carry the laws + the operator-memory
rules as context, workers never commit) or build directly when serial → verify by USE → commit →
record. Track 1 turns PREEMPT build talk: when Tim is in the conversation, beats hold to prep-only
(the established mid-walk discipline). [M]'s FE lane stays theirs; coordination via MESSAGES.md.

## Honest constraints
- cognition.py/suite.py work is SERIAL (no parallel workers on the hot engine files) — B1's core is
  my direct work across beats, not a big fan-out.
- The consolidations touch other sessions' docs — propose-not-apply, always.
- The board being "done or closer" by implementation-time depends mostly on B1; everything else is
  small or rolling.
