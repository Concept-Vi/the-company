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

## 2026-06-09 fire — HOLD (settings cleared; only cognition's cast-flip blocks)
- settings_surface: GREEN now (was a flaky/environmental red earlier, same HEAD) → NOT a blocker. (Flagged coherence re: gate determinism.)
- cast_beyond_listening: still RED (my held edit + cognition's stale "empty walkthrough cast" assertion). cognition hasn't flipped yet (HEAD unchanged).
- ACTION: HOLD the 6-role cast edit (verified, uncommitted). No code commit (gate red on cast). Docs only. Not spinning.
- NEXT FIRE: if cognition flipped cast_beyond_listening → company suites green → COMMIT the cast + release claim. Else keep holding.

## 2026-06-09 fire (cont) — cognition cleared me (efa9dbb) but left the cast_beyond_listening assertion → STILL hard-blocked
- cognition's relay cleared me to build the cast, but did NOT flip its test's "walkthrough cast is EMPTY today" assertion → my cast edit trips it → gate red → can't commit. Won't edit cognition's test (its lane). Re-flagged POINTEDLY (exact file:line + 1-line fix).
- ESCALATION RULE: if cognition's NEXT fire still hasn't flipped it (my primary piece stays hard-blocked on a 1-liner it owns) → PushNotification Tim (a real cross-session deadlock blocking my lane). Not yet — give cognition one fire to act on the pointed flag.
- Cast edit: still held + verified. No commit. Not spinning.

## 2026-06-09 fire — STILL deadlocked on cognition's :56 (2nd fire) — SURFACED FOR TIM'S MORNING (not waking him)
- cognition d5db6ba: added MCP scope, did NOT flip cast_beyond_listening:56. My cast (verified) stays gate-blocked.
- ESCALATION RULE REVISED (conscious, not silent): I will NOT PushNotification overnight — it's not destructive/urgent (main is CLEAN, the cast lands the instant :56 flips, nothing's broken). Morning-able → recorded here as Tim's #1 call.
- ★ TIM'S MORNING DECISION (the deadlock): cognition keeps deprioritizing the 1-line flip that lands my primary piece. Options: (a) relay firmly to cognition to flip cast_beyond_listening:56; (b) authorize me to flip that ONE anticipated assertion in cognition's test (its own comment says "guided-review adds it"); (c) tell me to pivot to the FE lane (it's available — A1/A3 show-me lane, B1 streaming — but they're moderate builds I held rather than risk a half-baked autonomous commit at deadlock-depth overnight).
- Cast: held, verified, uncommitted. Did NOT churn (no revert) + did NOT risk a heavy autonomous FE build. Clean main.

## 2026-06-09 fire — ✅ WALKTHROUGH CAST LANDED (5b8c08e)
- cognition flipped cast_beyond_listening:56 (525e3c8, data-driven invariant) → unblocked.
- Committed the 6-role cast. Gate GREEN (119 suites, 0 red). cast_for_mode("walkthrough")={the 6}; listening preserved. Claim released.
- The deadlock that needed Tim's morning call → RESOLVED autonomously (cognition flipped it). No Tim action needed on it now.
- NEXT FIRE: build the screen_reader role (roles/screen_reader.py — the mockup→at-altitude-comprehension role, on the C seam, op=generate over a mockup:// input) OR the FE show-me lane (A1/A3). screen_reader is the natural next (same seam, my lane, ungated).

## 2026-06-09 fire — ✅ screen_reader role LANDED (f77e6a2)
- Built roles/screen_reader.py (walkthrough cast, at-altitude mockup comprehension, reads A's mockup:// injection). Hit the drift-home red (new role must be in roles/AGENTS.md) → fixed (added it). Gate GREEN 120/0. By-use proven (dry-run: inbox mockup → plain "what this is / what you can do"). Claim released.
- TWO pieces landed: the walkthrough cast (5b8c08e) + screen_reader. The enriched guided turn + the screen-comprehension are live.
- NEXT FIRE: the FE show-me lane (A1 guided overlay / A3 next-back-dwell controls — purely my FE in canvas/app/src, backend start_walkthrough/present_current/next READY). Bigger build (FE + chrome verify); FORM feel = needs-tim.
