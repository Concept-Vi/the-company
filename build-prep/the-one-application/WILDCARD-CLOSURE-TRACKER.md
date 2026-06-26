# WILDCARD CLOSURE-TRACKER — the completion-refuter's living checklist

*Standing role (lead-assigned 2026-06-21): the live popcorn-B adversarial kernel / completion-refuter. Hold the holes + the L1–L5 closure-sequence; as each frontend-wire + Tim-use lands, RE-CHECK by-use AT EVERY LAYER (default-to-wrong) — flag any that report closed-but-aren't. The bar (the closure-test): does the capability hold at EVERY layer THROUGH to Tim's use, or just one?*

**THE DIAGNOSTIC (the unifying pattern — apply to every "done" claim):** a hole = a capability real+verified at ONE layer, the claim silently generalizing to the WHOLE loop. So "done" is never "the backend works" or "the wire exists" — it is "verified at backend AND surface-call-site AND Tim's actual use." Re-check each layer; default-to-wrong on the inches between them.

---

## HOLES (re-check until Tim-closed)

### HOLE-1 — decision-take canonicalization at the chokepoint
- **State: FIXED + COMMITTED (5b7acbb), by-use verified.** Re-verified in committed tree 2026-06-21 (3 markers present in runtime/territory.py). bare decision://d-42 → canonical; canonical unchanged; comment untouched.
- **Re-check trigger:** if territory_write is refactored, OR a non-canonical decision address ever reaches it live → re-curl POST /api/territory/write with a bare address, confirm the mark lands canonical + the signal emits canonical.
- **Layer status:** backend ✅ · resolver-sees-it ✅ · signal-canonical ✅ · Tim-use: N/A (defensive, fires on any take). CLOSED at its layers; rides next bounce to live.

### HOLE-3 — grounded-backend ≠ surface-calls-grounded (L2)
- **State: OPEN (verified 2026-06-21).** RightHand.tsx calls `.ask()` (generic /api/claude/turn) at lines 201, 562; `.groundedAsk()` (grounded /api/brain/ask) call-count = 0. Backend /api/brain/ask live (400). Owner: projection/fork (their lane — call-site switch).
- **Re-check trigger:** when projection switches the call-site → re-grep RightHand for `.groundedAsk(`, AND curl POST /api/brain/ask with a real question to confirm grounded answer, AND (Tim-use) the V answers grounded by-sight (not self-caveating generic).
- **Layer status:** backend ✅ · groundedAsk-method-exists ✅ · surface-call-site ❌ (uses .ask) · Tim-use ❌. NOT closed.

### HOLE-2 — grounding-trace vs origin-FIELD (L1)
- **State: ROUTED (recollection+composition), unverified by me.** Does "retrieves the decision's ACTUAL origin" trace to the real channel/gap, or read a stored origin-field an agent wrote (claim-grounded-in-a-claim)?
- **Re-check trigger:** when recollection lands the per-decision retrieval-keying fix → verify the explanation cites a REAL source (channel msg / gap / Tim's words), not a re-statement of the card or a claimed field. The doc's own discriminating check: "does the explanation ADD what's NOT on the card?"
- **Layer status:** retrieval-internals: unverified-from-here. NOT closed.

---

## L1–L5 CLOSURE-SEQUENCE (the Tim-use bar — re-check each as it lands)

| Link | Tim-use bar | Current (default-to-wrong) | Re-check |
|---|---|---|---|
| L1 | RHM walks Tim through each decision, GROUNDED | backend route live; CONTENT gated on HOLE-2 (recollection) + theorem rebake; projection holds the user-facing flip | when projection flips: by-sight the 13 cards explain w/ real source (HOLE-2 closed) — does the explanation ADD beyond the card? |
| L2 | Tim asks the V, gets a GROUNDED answer | HOLE-3 OPEN (call-site uses generic .ask) + V-overlay mount (DNA) | groundedAsk wired (HOLE-3) + V answers grounded by-use |
| L3 | Tim decides → a gated lane RESUMES | wire live + chokepoint canonical-safe (HOLE-1); decide-rung single-source ✓; awaits Tim's ACTUAL decide + noticeboard signal-write | Tim decides a real card → a gated lane resumes with the chosen option, end-to-end |
| L4 | RHM reads/proposes to the channel | SCOPED (builds on L2) | brain reads channel by-use + proposes a post Tim approves (NO autonomous post) |
| L5 | RHM updates a decision card | SCOPED (cross-lane) | RHM proposes card-update → lands on the address → re-renders, by Tim's use |

**Floor:** NONE closed by the Tim-use bar yet. Backends largely real; residual = frontend call-sites (HOLE-3) + content-grounding (HOLE-2) + Tim's actual click (L3). Re-check on each landing; report closed-but-isn't to the lead.

*Updated 2026-06-21 by wildcard (ch-869a5yzl / work-id ch-piffgfxv). Re-check on every frontend-wire + Tim-use event.*
