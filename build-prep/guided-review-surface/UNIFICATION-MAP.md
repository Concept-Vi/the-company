# UNIFICATION MAP — the grown picture after Coverage Round 1

> **What this is.** The synthesized output of the full-directory COVERAGE ROUND (8 territories: runtime,
> canvas, substrate, cognition, voice, design, ops, design-corpus) over the guided-review-surface. It
> grounds the convergent thesis against current `main`, verifies the two big claims, names the genuine
> net-new remainder, and surfaces the decisions for Tim. The grown criteria live in
> `Completion Criteria.md` (the "ADDED BY COVERAGE ROUND 1" section, Groups J–N); this map is the picture
> behind them.
>
> **Evidence convention (Tim's standing law).** *Observed(file:line)* = read directly on `main`.
> *Inferred* = pattern-matched, NOT execution-verified. *Verified* = confirmed by a run. Nothing here is
> painted green; the appended criteria are status-marked honestly in the criteria doc.

---

## 1 · The organ-realization (Claim 1 — VERIFIED Y)

**This surface IS the Company's one human-interaction organ — the vault's *RHM Walkthrough & Review
Organ*. The guided build-review studio is its FIRST consumer, not its definition.**

**How it verified.** The vault doc `RHM Walkthrough Organ — Completion Criteria.md` opens with Tim's own
thesis, verbatim: *"The right-hand-man is the one organ through which Tim and the system meet … the
system surfaces anything that needs Tim (build-review items, decisions, verifications, ideas), the RHM
presents it in the interface (driving any part of the UI, voice-first), records Tim's response, and feeds
it back so the system acts — no Claude-Code-in-a-terminal middleman. Build-review is its first consumer;
the project→product pipeline's stages are future consumers. So it is built general, not as build-review's
UI."* That IS the convergent thesis, stated by Tim months before this surface was scoped. The two
documents are the same design expressed twice — vault (vantage: the general organ) and repo
(vantage: grounded-code proof). **Claim 1 = Y.**

**But the merge is a UNION, not a congruence.** The two criteria sets do NOT overlay letter-for-letter.
Each contributes load-bearing criteria the other lacks:

| The vault organ uniquely carries | The GRS criteria uniquely carry |
|---|---|
| The review QUEUE + `origin` polarity (A1/A2) → **J1** | Comprehension-at-altitude, the original-failure killer (C1–C4) |
| The `status` lifecycle field, never-on-`resolved` (A3) → **J2** (bug-guard) | GENERATE-FOR-MOCKUPS — the make-or-break spine (F1/F2) |
| The human go-gate (B2) → **J3** | Scoped temporal deixis / locus-trail (G1/G2) |
| Branching walks (B5) → **J4** | The mockup-aware stop + mockup-scheme path |
| Actionable-WHY (D4) + record/skip (D2) → **J5** | The streamed text talk-back, reusing voice (B1) |
| The three-part derived-from bind (E2) → **J6** | The RHM-annotate verb posture (I4) |
| `guard()`/POLICY actually wired (G1) → **J7** | The FE show-me lane (H2) |
| Modes-drive-the-engine behaviour (G2–G4) → **J8** | |
| The S1–S7 by-use acceptance scenarios → **J9** | |

**The grown criteria = the union of both** (Groups A–I from the GRS round + Groups J–N added this round).
The merged document IS the organ scope. The two share the SAME engine (`start_session`/`present_current`/
`next`/`start_walkthrough`/`start_guide`, all Observed present in suite.py) and the SAME governance, so
the union is additive, not a reconciliation of conflicts — with ONE noted framing tension (see §3, I1).

---

## 2 · The additive-composition architecture (per-subsystem: activated / wired / net-new)

The thesis is right that the genuinely-net-new shrinks dramatically. Per subsystem, what the surface
*activates* (already built, flip a switch), *wires* (a seam), and *builds net-new*:

| Subsystem | ACTIVATED (built, switch) | WIRED (a seam) | NET-NEW (real build) |
|---|---|---|---|
| **Runtime / engine** | walkthrough engine (`start_session`/`present_current`/`next`/`start_walkthrough`/`start_guide` — Observed suite.py:6099–6492); `walkthrough` mode (suite.py:1278); the singular wire (verified by prior build) | modes drive present-vs-act (J8) | branching via per-port + `gate` node (J4); `guard()`/POLICY wired into apply paths (J7 — Observed `guard()` never called today) |
| **Cognition** | the swarm executor + injection edge (G0–G1 proven); `chat_parts()` streaming generator (suite.py:5264) | add `"walkthrough"` to 6 roles' `mode_scope` (K1 — **6 one-liners, Tim-decision**); recall/ground inject via canonical rule on day one | `screen_reader` role (K2); connect/check/voice injection awaits G3/G4 |
| **Voice** | Kokoro TTS + whisper.cpp STT + VAD/barge-in (Observed ready) | focus-passthrough at bridge.py:848 (N·H1, one line) | — (text-stream cancel reuses the `gone[0]` primitive, N·B3) |
| **Canvas / FE** | the studio room (Review.tsx + StudioKit + RhmPanel); SSE dispatch; generic renderers; **F0 modularity DONE** | text-stream consumer N·B1 (`api.chatStream`); walkthrough↔chat `indicate` N·I3; journey-store navigate-emit N·G2; mount CognitionView beside RhmPanel | the FE show-me overlay + pace controls (H2) |
| **Substrate** | the address grammar (`ui`/`code` schemes, `addresses.json`, `tokens.json`); R2 context auto-resolution (running) | — | register `mockup://` in SCHEMES (L1, one line — Observed absent contracts/address.py:32) |
| **Design / coherence** | `check.py` + `refcheck.py` + `symbols.py` + `codeedges.py` (all Observed present); the mockup corpus (23 files) + `design-system.css`/`tokens.json` | run the mechanisms on-demand in the walk | the live coherence-oracle + finding→queue path (M1) |
| **Ops / gates** | the standing all-green gate (`suite_health_acceptance.py`, shelled via `company suites`) | — | `verify_guide_output` verify-by-use gate over generated builds (M2 — Observed does NOT exist); pre-guide capability/reachability/resident lints (ops U2–U4) |

**The net-new remainder (the honest small list):** generate-for-mockups (F2, the existing spine) +
the FE show-me lane (H2) + the batch one-approve (E2) + the binds the thesis named (R2/I4/F1/L1) +
**from this round:** the `screen_reader` role (K2), the `mockup://` scheme (L1), the coherence-oracle
(M1), the verify-gate (M2), and the vault outer-circuit criteria the GRS set lacked (J1–J9 — queue,
lifecycle, go-gate, branching, derived-from bind, `guard()`-wired, modes-drive, scenarios). Everything
else is activate-or-wire.

---

## 3 · The dependency reality (Claim 2 — OVER-INFERRED)

**The agent's "IAS Phase 0 MUST land first" is over-inferred. Most of it is already on `main`.**

Verified against current `main`:

| Agent's claimed Phase-0 prerequisite | Reality on main |
|---|---|
| **F0 — FE restructure (componentize, state container, layout shell)** | **ALREADY DONE.** App.tsx is **338 lines** (not the claimed 1660-line monolith); the FE is split into `regions/` (Review, RhmChat, CognitionView, Inbox, AddressHelp, …) + `components/` (StudioKit, ContextBundle, …); Review.tsx is 62 lines; `app.css` carries the F0/F1 carve comments as completed work. |
| **S0–S5 — address floor (grammar, registry, event-stamp, resolver, safety)** | **MOSTLY THERE.** `design/_system/addresses.json`, `tokens.json`, `design-system.css` (imported via main.tsx); `indicate`/`address_help`/`route_click`/`ui_info` all Observed present in suite.py. |
| **I1–I6 — interaction model (click=indicate+consent)** | Present — `route_click` never blurs operate-vs-annotate (per existing criterion D1); `indicate` exists. |
| **C0 — corpus-import (design-system.css, tokens.json, check.py)** | The files exist + the import is asserted in `app.css` comments. **STILL-NEEDED:** a real end-to-end render TRACE to CONFIRM the FORM gate is wired (not just assert from comments). |
| **Grammar: `mockup://` in SCHEMES** | **GENUINELY MISSING** (Observed contracts/address.py:32 — `mockup` absent). This is the one real grammar prerequisite → **L1**, a one-liner, lands before F1/F2. |

**The honest split:**
- **Already there (not a blocker):** F0 FE-modularity, the address floor, the interaction verbs, the
  design-system files.
- **Still-needed-first (small, real):** (a) **L1** — register `mockup://` in SCHEMES (one line, before
  F1/F2 dispatch); (b) **confirm** the corpus-import/FORM-gate is wired end-to-end by an actual render
  trace (vs assumed from comments).
- **Over-inferred:** "a heavy IAS Phase 0 (F0 restructure + S0–S5 floor) is a hard gate before any
  parallel build." It is not — the agent appears to have read a stale snapshot (the 1660-line monolith
  is no longer the FE on unified main).

**The DESIGN-CORPUS-INTEGRATION.md cross-roll-up over-reached.** It is one agent's synthesis and was
explicitly to be verified, not adopted: it asserts the F0 monolith prerequisite (stale), and lists a
"T1-EMIT exactly-once fix BEFORE Bucket C dispatch" that the GRS-grounded criteria treat as covered by
the verified singular wire (E1) + the new verify-gate (M2). Treated as INPUT, corrected here.

---

## 4 · The framing tension to record honestly (the runtime companion vs the grounded view)

The runtime companion (coverage/runtime.md:194) frames the surface as **"WALKTHROUGH IS A ROLE UNDER A
NON-TURN ACTIVATION CONTEXT"** and proposes building `roles/guided_review.py` + a `guided-review` row in
`ACTIVATION_CONTEXTS`. **Verified-against-main, this partly conflicts with the grounded GRS view:**

- The walkthrough engine ALREADY exists (suite.py — not a role to be written); `walkthrough` is ALREADY
  a MODE (suite.py:1278) bound via `start_walkthrough` (suite.py:6287).
- The guided dialogue's Q&A already fires under the **existing `per-turn` activation context**
  (`chat_parts`, Observed activation.py — per-turn is "ALREADY LIVE, owned by chat()/chat_parts()"), NOT
  a missing non-turn context.
- So "add a new activation context + a new role file" would **re-build an engine that exists** — an I5
  (anti-parallel) violation at the architecture level.

**The reconciliation (recorded as N·I1, not adopted as a build-a-new-role criterion):** NO new activation
context is needed for the guided dialogue's per-turn chat. What's actually missing is (a) the walkthrough
CAST (Group K — the 6 mode_scope edits) and (b) the FE show-me lane (H2). A non-turn activation context
would only be warranted if the RHM is to walk **autonomously** (system-initiated, between turns) — that
is a **forward decision**, not this build's prerequisite.

---

## 5 · The named DECISIONS for Tim

### D-I · The full-organ scope (do we merge the vault A–G in as Groups J?)
**Recommendation: YES — and the criteria doc already does it (Groups J).** Claim 1 verified; the vault
criteria are the outer circuit (queue → present → respond → act → lifecycle) the GRS set lacked, and they
are Tim's own thesis. The merged `Completion Criteria.md` IS "THE unifying human-interaction organ" rather
than "a review surface." *The only sub-question:* build-order — the vault puts `guard()`-wiring (J7)
first; the GRS round leads with text-streaming (B1). Both can run file-disjoint in parallel
(governance/queue lane vs FE lane).

### D-II · The cognition-cast posture (Group K1) — **lean vs enriched guided turn**
**This is a genuine Tim-decision, NOT a foregone criterion.** Does the guided dialogue want the enrichment
swarm (memory-recall + live-state grounding) firing on every conversational turn at a stop — giving the
RHM memory of past decisions about the same screen — or stay deliberately lean ("show me, guide me," which
the code comments at suite.py:3140-3141 lean toward)? If enriched: 6 one-line `mode_scope` edits, and
recall/ground inject immediately. **Recommendation:** lean toward enriched (a right-hand-man reviewing a
screen SHOULD remember past decisions about it), but it is Tim's call and it is cheap to flip either way.

### D-III · The IAS dependency (Claim 2) — **is anything gating?**
**Recommendation: treat IAS Phase 0 as NOT gating.** The real prerequisites are tiny: L1 (`mockup://`
scheme) + a render-trace confirmation of the FORM gate. Do NOT block the build on a "Phase 0" that is
largely already on main.

### D-IV · The non-turn activation context — autonomous walk AND/OR arrival-enrichment (forward fork)
**A forward decision, surfaced not pressed.** A non-turn activation context (the runtime companion's
`guided-review` row, §4) becomes real in EITHER of two cases — both are non-turn, both optional, neither
gates this build:
1. **Autonomous walk** — the RHM walks Tim through things *system-initiated* (between turns, not in
   response to his chat).
2. **Arrival-enrichment (the K2 fork)** — the `screen_reader` brief is computed the moment Tim LANDS on a
   stop (navigation-triggered), so the brief is ready before he asks anything — vs the lean default where
   `screen_reader` fires within-the-turn (a concurrent Part-0 when he asks, riding per-turn, no new
   context). The lean default needs NO new context; arrival-enrichment is the only K2 variant that does.

So the per-turn correction in §4 holds for the *reactive* guided dialogue (Q&A at a stop) — no new
context needed there. A non-turn context is warranted ONLY for autonomous walks (case 1) or if Tim picks
arrival-enrichment for the screen_reader brief (case 2). Recommendation: keep the lean within-turn default
unless the arrival-ready brief feels materially better in use (a 🔴 needs-tim feel judgement).

### D-V · Whether a 2nd coverage round is warranted (and on what)
**Recommendation: a SMALL, targeted 2nd round — NOT a full re-sweep.** Round 1 achieved full-territory
coverage; the open threads are narrow and specific:
1. **Verify-trace the corpus-import/FORM gate** end-to-end (the one un-traced Phase-0 item — §3).
2. **The decisions/verifications/ideas consumers** — Round 1 confirmed build-review is the first consumer
   and the pipeline stages are future consumers (vault thesis), but did NOT scope what riding the organ
   AS a new mode actually requires for those (the mode-row + resolution-lens per consumer — Group I's
   join). A targeted round on "the second consumer" would test the organ's generality concretely.
3. **The G3/G4 injection completion** for connect/check/voice (the cognition cast's deferred half — K1's
   payoff is partial until then; worth scoping against the Concurrent Cognition criteria).

These are bounded follow-ups, not a reason to re-run the broad sweep.

---

## 6 · The build sequence (grown)

```
PREREQUISITE (small, real — NOT a heavy Phase 0):
  └─ L1: register mockup:// in SCHEMES (one line)
  └─ CONFIRM corpus-import/FORM gate wired (a render trace, not a re-build)

OUTER CIRCUIT (vault organ, file-disjoint from FE — can parallel the inner lane):
  └─ J7 (guard()/POLICY wired) → J1/J2 (queue + origin + status lifecycle, the A3 bug-guard)
     → J5 (record + actionable WHY) → J6 (derived-from three-part bind)
  └─ J3 (go-gate) + J8 (modes-drive) fold into H2 + I1
  └─ J4 (branching) after the linear walk works

INNER LANE (the felt experience — GRS §5 order, refinements folded in):
  1. B1 (text streaming)        ← N·B1 exact FE wiring
  2. I3 + H1 (chat re-ground + voice focus)  ← N·I3, N·H1 one-liners
  3. H2 (FE show-me lane)       ← carries J3/J8 FORM
  4. E2 (batch one-approve)     ← M2 verify-gate wraps it
  5. F1 (mockup-aware stop) + L1 prerequisite met
  6. F2 (GENERATE-FOR-MOCKUPS — the spine) ← M2 verify-gate wraps it
  7. G2 (locus-trail)           ← N·G2 journey-store seed
  8. I4 (RHM-annotate verb)
  9. D3 (group roll-up); C4 (cap/pre-digest — or fold into K2)

ENRICHMENT / QUALITY (Tim-gated or low-urgency):
  └─ K1 (cast posture — DECISION) → K2 (screen_reader role)
  └─ M1 (coherence oracle, on-demand in walk)

STANDING ACCEPTANCE:
  └─ J9 (S1–S7 scenarios) — every criterion is green only inside a passing scenario
     (browser + voice + adversarial S6)
```

---

**Coverage Round 1 synthesized 2026-06-08.** Claims verified against `main`. The grown criteria are in
`Completion Criteria.md` (Groups J–N under "ADDED BY COVERAGE ROUND 1"). Lead commits.
