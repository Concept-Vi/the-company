# Guided-review — autonomous-loop STATE (continuity across cron fires + compaction)

> The cron loop re-reads this each fire to re-orient (crash/compaction-robust). Keep it honest + current:
> done / in-flight / blocked / needs-Tim. Update it every fire.

## Standing context
- I am the guided-review session. My build = the guided RHM walkthrough surface (the one human-interaction
  organ; build-review its first consumer). Criteria build-ready: `build-prep/guided-review-surface/Completion Criteria.md` (committed 15886ed).
- Three-session coordination is live + relay-free: `build-prep/coordination/` (AUTONOMOUS-LOOP.md protocol,
  MESSAGES.md channel, WORK-SPLIT.md § CLAIMS, CONVERGENCE-ROUND.md). My cron slot: `:05` (5,20,35,50).
- Forward-split: I mutate the operator surface + FE + wire/generate-for-mockups + my roles-on-the-C-seam;
  coherence reads/gates; cognition owns the engine.

## GATES on my build (why most of it waits)
- **Cognition's C** (run_role→input_addresses + the cast-beyond-listening seam) must land before my walkthrough
  cast + screen_reader role can be built. HOLDING runtime/cognition.py + runtime/roles.py until cognition posts
  "C released." Watch MESSAGES.md.
- The forward-split is implied by coherence (it reads, I mutate) — proceed on the FE, but post my first FE
  claims so coherence can object if it disagrees.

## UNGATED work I CAN do overnight (file-disjoint, no held files)
The FE/surface parts in `canvas/app/src/*` that don't need cognition's engine — per the Completion Criteria
priority, the ones not blocked on C/the wire. Each: claim → build → `company suites` green → verify by USE on a
TEMP store → commit → release. (Identify the next buildable one each fire from the criteria; if all ungated FE
parts are done or every remaining piece needs C → record blocked + exit, don't spin.)

## Status (update every fire)
- 2026-06-08 setup: loop + message system + cron established. Build NOT started (held at criteria-ready +
  coordinating). First fire: read MESSAGES, pick the first ungated FE criterion, claim+build+gate+verify, or
  record blocked-on-C if nothing's ungated-buildable yet.
- in-flight: —
- blocked: my roles/cast → cognition's C (waiting).
- needs-Tim: confirm the forward-split if coherence/interface object (none yet).

## 2026-06-09 — RE-SCOPE done + READINESS HOLD (Tim's catch)
Loop-prep RE-SCOPED for the 3-fork split (Completion Criteria § POST-COORDINATION RE-SCOPE): build ONLY my lane;
consume cognition's C; cross-ref coherence's gates. § PROTOCOL item 11 = the readiness gate.
**CRON: do NOT build until ALL THREE post "loop-prep re-scoped + grounded + ready" on the board.** Re-scope is
done + I've posted my readiness; now waiting on coherence to ground its criteria + all three to confirm. Until
then each fire = poll the channel + answer, NO code. When ready AND cognition's C cast lands → build my lane.

## 2026-06-09 fire — HOLD (gated, no build)
- cognition C: 3/4 run_items (ca2d3df) + 3b skills/contexts (1b89f70) landed. **Cast (4/4) NOT yet landed** → my roles gated.
- readiness gate: I'm ready+posted; coherence still grounding its criteria → not all-three-ready.
- Action this fire: HOLD, posted a status, no code. (Future no-change fires: update STATE only, do NOT spam the channel — only post on a real change/build/answer.)
- Unblocks: C's cast lands (→ build my roles) AND/OR readiness settles (→ build my disjoint FE lane, claimed+gated).

## 2026-06-09 fire — walkthrough cast EDITED + verified, HELD uncommitted (gate red, not my reds)
- DID: added "walkthrough" to mode_scope in roles/{recall,ground,voice,connect,focus,check}.py (sed; the cast).
- VERIFIED BY USE: cast_for_mode("walkthrough")={the 6}; listening cast preserved (unbroken).
- BLOCKED on the gate (company suites RED, 2 suites, NEITHER mine to fix):
  (1) cast_beyond_listening_acceptance — its assertion "walkthrough cast is EMPTY today (guided-review adds it)"
      is now correctly false → cognition flips it (its test). (2) settings_surface_acceptance — RED at clean HEAD
      (mode text-only subtypes JSON-safe), cognition's mode territory, not mine.
- HELD: the 6 roles/ edits are UNCOMMITTED (gate red). Claim kept. Flagged cognition. Committed docs only.
- NEXT FIRE: if both reds cleared → company suites green → COMMIT the 6 roles + release claim. Else keep holding.
