# WILDCARD ADVERSARIAL PASS — L1–L5 default-to-wrong hole-list

*Role: fresh-eyes adversarial on OPERATOR-LOOP-CLOSURE.md (lead-assigned). Method: read the code + curl live, default-to-wrong, hunt conflations (committed≠live · mechanism-verified≠Tim-closed · route-exists≠surface-uses-it · backend-live≠frontend-calls-it). Verification-state on every line. NOT contrarian — where a claim HOLDS under live check, I say so (no manufactured holes).*

## LIVE CURL RESULTS (committed≠live test — method-correct)
- `POST /api/brain/ask` → **400** (live; needs {question} — matches the doc's "VERIFIED LIVE 400-not-404"). ✅ backend real.
- `POST /api/territory/write` → **200** (live; the decide chokepoint, now canonicalizing post-5b7acbb). ✅
- `GET /api/decision/decided-signals?since=0` → **200** (live; L3 read-half). ✅
- `POST /api/decision/list` → **404**, `GET` → 404 (no such route — but the doc never claims it; NOT a hole, my probe was speculative).
→ The backend endpoints the doc claims live ARE live under correct-method curl. No committed≠live hole at the backend. (Ports listening: 8770 bridge, 8771, 4100 litellm, 11434 ollama, 8000/8007/8008.)

## ★ HOLE-3 (L2, REAL — verified in code): backend-grounded-and-live ≠ the-surface-calls-grounded
- **The claim (doc L2):** "Backend /api/brain/ask VERIFIED LIVE… Today forkVBrain → generic /api/claude/turn (self-caveats, NOT grounded). projection wires forkVBrain → /api/brain/ask (the L2 root-fix)." Marked DISPATCHED/wait-fill (honestly NOT-done).
- **What I verified:** `fork-v-brain.js` exposes BOTH `ask()` → `/api/claude/turn` (generic, panel) AND `groundedAsk()` → `/api/brain/ask` (grounded, kimi). BUT `RightHand.tsx` (the RHM panel) calls **`.ask()` at BOTH call sites (lines 201 tour-starter, 562 user-question) — never `.groundedAsk()`.**
- **THE CONFLATION (confirmed, not speculative):** "the grounded backend is live + verified" is TRUE and "forkVBrain CAN ground (groundedAsk exists)" is TRUE — but the SURFACE Tim actually uses calls the GENERIC path. So a user asking the V today gets the self-caveating generic turn, NOT the grounded mind. The grounded capability is built on both ends (backend + a groundedAsk method) and simply **not connected at the call site.** This is the precise wait-fill: ~2 call sites (201, 562) `.ask(` → `.groundedAsk(` (or a grounded-by-default in forkVBrain.ask). The doc's L2 honesty HOLDS; this pinpoints the exact one-edit gap + confirms it's call-site, not backend.
- **VERIFICATION-STATE:** Observed in code (the two call sites use .ask; groundedAsk exists unused-by-the-panel). NOT my lane to fix (projection/fork own RightHand + forkVBrain) — flagged for the wait-fill.

## CLAIMS THAT HOLD (no hole — said honestly, per default-to-wrong-but-not-contrarian)
- **L3 wire** (decide→signal→resume): real + now canonical-safe (HOLE-1 fix 5b7acbb committed+verified). Mechanism verified; the doc correctly says "NOT closed-by-Tim" (awaits his click). HOLDS as "mechanism-live, Tim-use-pending" — that's honest, not a hole.
- **forkVBrain / groundedExplain wires are NOT wire-illusions:** `window.forkVBrain` IS defined (fork-v-brain.js:122) + loaded (index.html script) + attached (RightHand). `groundedExplain` IS imported into GalleryMount + mounted in App.tsx. Both real. (Checked specifically for the wire-illusion class — not present here.)
- **Decide chokepoint single-source:** confirmed one function (territory_write); onVerb reuses writeDirections. ✅

## ★ HOLE-2 (L1, routed): grounding-trace vs origin-FIELD — does "retrieves the decision's ACTUAL origin" trace to the real channel/gap, or read a stored origin field an agent wrote (claim-grounded-in-a-claim)? Lead routed to recollection+composition. Verification-state: flagged-to-verify (I can't confirm recollection's retrieval internals from here).

## THE PATTERN ACROSS THE HOLES (for the lead's "is it finished" bar)
Every hole is the SAME shape: **a capability is real and verified at ONE layer, and the claim silently generalizes to the WHOLE loop.** HOLE-1 = chokepoint-fires-signal verified for canonical-input, generalized to all-input. HOLE-3 = grounded-backend-live, generalized to surface-is-grounded (but the call site uses generic). HOLE-2 = origin-retrieved, generalized to origin-traced-to-source. The doc is unusually honest (it caught two itself); the residual risk is the LAST inch of each link — backend-live vs Tim-uses-the-grounded-path vs the-loop-closes-by-his-hand. **None of L1–L5 is "done" by the Tim-use bar; the backends are largely real; the gaps are frontend call-sites + Tim's actual click.** That matches the doc's own closure-sequence — so the doc's HONESTY holds; my pass confirms it + pinpoints HOLE-3's exact call-site.
