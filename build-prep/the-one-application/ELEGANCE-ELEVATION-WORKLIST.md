# Elegance Elevation Worklist — the decision surface to the craft bar
*The converged worklist from the critical-comparison pass (lead's comprehensive agent + projection's craft-comparison + composition's contract-enablement). Driven off the EXTERNAL REFERENCE (the Gallery's at-bar pieces), not Tim's reaction. Tim 2026-06-19: the system must self-improve against the references; Tim is the FINAL check, never the quality loop. [[feedback-gallery-examples-external-quality-reference]]*

## ★★★ RE-BASELINE (2026-06-19, lead — after Tim's 2nd review + DNA's honest self-comparison + lead's live-shell render)
The first elevation round took a WRONG TURN and must be re-baselined. What went wrong + the corrected law:

**Operational root cause (lead's live render @:5174/?verify=1 exposed it):** DNA's composed view (device+slide+co-visibility) only ever landed in the GALLERY pieces (explained.html/real-*.html). The OPERATOR shell Tim actually opens — `renderDecisionGallery` (unit-view.js) + sys-responsive — was NEVER wired to it; it still draws the BARE card. So the "milestone" diverged from Tim's surface. **#2 (wire renderExplained+visualDevice INTO the operator shell) is the single change that reaches Tim — it is now the pivotal item, not a gallery nicety.**

**The corrected LAW (supersedes the co-visibility hard-gate below, which incentivized destroying meaning):**
1. **LEGIBILITY IS PRIMARY.** The decision must be fully understandable + decidable: real SITUATED framing (not a compressed slogan), and EACH option's real meaning SHOWN. DNA clamped options to 2 lines + compressed questions past meaning to force co-visibility → "a decision you can't read is worthless" (Tim, correct). NEVER truncate/hide content to fit.
2. **CO-VISIBILITY is a CONSTRAINT SUBORDINATE to legibility** — achieved by the references' DENSE-BUT-CLEAR vocabulary (2-line mono ledger, layered plate+inset, ordinal dots pack MORE meaning into LESS space) and by the DEVICE replacing the text-explanation (device+options co-fit; prose telling moves to the slide/below), NEVER by clamping. The references prove rich+legible+co-visible coexist.
3. **EVERY visual device must ENCODE REAL DATA** (data-bound to the decision's actual trade-offs), never hardcoded heights. DNA's bars = hardcoded = "a stupid bar chart with no meaning" (Tim). Decoration that looks like information is WORSE than none. [[render-for-cognition]] — the visual must carry real signal Tim's perception computes on.
4. **BUILD AGAINST THE REFERENCE, NOT TIM.** DNA already produced a ~30-gap self-comparison vs scr-home/scr-piece-live/gen3-shapes/app-sheet — THAT is the build spec. The OBJECTIVE gaps (legibility, the full component vocabulary, data-bound devices, operator-shell wiring, depth) are NOT in doubt — build them now, verify each increment vs the references (DNA) + projection cross-check (?verify=1). Reserve Tim for the IRREDUCIBLE SUBJECTIVE residual ONLY — ONE precise calibration question after the objective build, never the whole gap list. [[feedback-gallery-examples-external-quality-reference]] — Tim is the FINAL check, never the quality loop. Don't make him read the gap list = don't make him the loop.

**Lane order:** (1) LEGIBILITY [recollection situated copy + DNA render-shows-meaning + composition data-bound device contract] → (2) WIRE THE OPERATOR SHELL [DNA — renderDecisionGallery+sys-responsive get renderExplained+visualDevice] → (3) CAP-2 dark/depth tokens [DNA, foundational, in progress] → (4) full craft vocabulary [DNA]. CAP-1 addressing-scheme: DNA→composition after CAP-2.

---

## THE HEADLINE (pixel-verified — corrects the "generated = flat" assumption)
The generative system is NOT the problem. `scr-piece-live` (fully generated, data-driven via DNA.renderPiece) renders PIXEL-IDENTICAL to the hand-built `scr-piece`, and both sit AT THE BAR. So the generative path CAN hit elegance. The **decision-card archetype specifically** is the laggard — the same renderer hits bar elsewhere. And the prettiest decision specimen (`v6-house-ruled`) is HAND-STUBBED (fails the must-be-generated rule) AND visually broken (TAKE/Choose overlap, implication clips) — so the nice one cheats, the honest ones are flat. Closing that delta is the work. This is NOT a rebuild — it's fixing the decision-archetype's concrete root causes.

## CORRECTED ASSUMPTIONS (verified in pixels + DOM)
- Warmth IS resolved live (resolveOnto injects --warm/--page/--gold inline). NOT "doesn't resolve."
- The ordinal gold→ochre→bronze→faint ramp IS applied (3-opt + 4-opt ledgers). Just too SUBTLE.
- The real flatness root: at default warmth, --warm (#FCFBFA) and --page (#FEFEFE) are near-identical near-whites → surface tiers barely separate. A TOKEN-SPREAD problem, not a resolve problem.
- What genuinely IS ignored: the archetype declares `explain: surface "cool"` + `options: surface "page"` (layouts.json) but archetype.js NEVER reads slot.surface (0 grep refs). Declared surfaces dropped on the floor.

## THE ROOT CAUSES (the decision card is below-min for 3 concrete reasons)
1. **Two competing heroes** — layouts.json#decision-card head declares BOTH `name` AND `question` heading-weight → every card has two heroes + a tall near-empty head band. The GRAMMAR specifies the defect, not the card.
2. **Renderer ignores declared slot.surface** — the "everything resolves from the DNA" contract is broken here; finish classes hardcoded.
3. **Voice law unwired** — voice.json mandates telegraphic ("a fragment wherever a sentence isn't earned; numbers are sentences"), but content/decisions.json ships 230–650-char questions + a boilerplate `is` ("a decision to make") on every record, poured in verbatim (only a crude length→font-shrink). The voice face is AUTHORED BUT UNWIRED — nothing compresses source meaning into a telegraphic question + a real what-kind line.

## WORKLIST (prioritized; lane-assigned)
### Cards / archetype (highest impact)
1. **Kill the two-hero head** — layouts.json#decision-card: `question` = the single hero; demote `name`→quiet kicker/eyebrow (or drop); render `is` as a calm "what-kind · reversible, latest-wins" line, never "a decision to make". → **DNA (language/grammar)**
2. **Fix content voice at source + add a generation-time compression/voice pass** — rewrite decisions.json `meaning` to telegraphic ≤~90-char questions (body → `explain`); replace boilerplate `is`; THEN a pipeline pass so future records can't ship 650-char walls. → **recollection (card copy) + DNA (voice.json standard) + composition/fork (the compression pass = system extension)**
3. **Renderer honors slot.surface** — slotHTML/zoneHTML map declared surface→token (cool/page/nested), not hardcoded finish. → **DNA-renderer (archetype.js)**
4. **Option `description` out of the implication chip** — render description as prose; reserve the mono chip for the terse `implication` only (the gray boxes are the weakest pixels on every real card). → **DNA-renderer + composition (slot contract)**
5. **Single gold commit CTA at thumb reach** (v6's one real strength) — one focal CTA below the options, not only per-option "Choose X ›". → **DNA (archetype) + renderer**

### Generative system (so the bar holds everywhere)
6. **Widen surface-tier token spread + wire depth** (--nested, inner-lift, hatch/emboss) into the archetype surfaces → layered like scr-home, not flat near-white. → **DNA (tokens/dna)**
7. **Strengthen the ordinal ramp** to gen3-ordinal's legibility (resolves but too faint). → **DNA**
8. **Author a wide-reflow left-column** (supporting figure / context / decision lineage) so desktop isn't a stretched phone card (dead left quadrant today). → **DNA (archetype) + composition (declaration)**
9. **Give every archetype an `id`** (or renderer uses the map key) → data-archetype currently emits "" → per-archetype CSS/targeting can't hook. Wiring bug. → **DNA-renderer**
10. **Fix or RETIRE v6** — it's hand-stubbed (fails must-be-generated) + broken; the canonical reference should be a GENERATED card brought to bar. → **DNA**

## THE CALIBRATION (projection's nuance — keeps it honest)
A decision is a DIFFERENT archetype than a dashboard → CALMER (signal-economy; no fake stat-band on a yes/no). The bar is MATCH THE CRAFT LEVEL / DNA-language fidelity (layered depth · texture · ordinal-richness · micro-detail/mono) WITHOUT bolting on dashboard furniture that doesn't belong. Lift craft, don't cargo-cult the reference.

## ★ THE REFERENCE TARGET — scr-home's craft vocabulary (projection, read from pieces/scr-home/v1.html)
The ~15 `.p-*` components that ARE "at the craft bar" — the elevation targets this vocabulary (lifting craft, not copying dashboard furniture):
- `.p-band` + `.p-bs`×4 (`.n` big-number + `.l` label) — the gold-hatch STAT-BAND (texture ground).
- `.p-plate`×2 + `.ph2` (icon header) + `.p-inset` (`.iv`/`.il`) — LAYERED PLATE-CARDS (depth = card-on-card inset).
- `.p-rows`/`.p-row` + `.dot` + `.t`/`.sub` + mono timestamps + `.star` — the LEDGER (ordinal ramp dots · two-line entries · mono micro-detail).
- `.countstrip` (running summary) · `.p-act` (filled-gold CTA) · `.p-rail` (dark nav) · `.p-hd`/`.p-h`/`.p-sup` (header).
The decision card uses only ~4-5 (`.p-hd`/`.p-h`/`.p-sup`/`.p-frost`/`.p-hatch`) → missing layered-plate depth, the texture band, the rich ordinal ledger, micro-detail. The language = LAYERED PLATES · TEXTURE · ORDINAL RAMP · MICRO-DETAIL (calibrated calmer for a decision, per the nuance above).

## ★ THE CONTRACT-CAPABILITY CHECK (composition + DNA — gates whether craft-lift = system-lift)
Can renderArchetype + the decision-card archetype's slot/zone vocabulary in layouts.json EXPRESS the richer `.p-*` (p-plate/p-inset, p-rows-with-ordinal-ramp), or is the slot set capped at the flat ones? If it CAN'T express layered-plate/ordinal-ledger → the craft lift IS a system lift (EXTEND the archetype's slot vocabulary), not card-patching. composition's contract-enablement lane answers this against the scr-home vocabulary target; DNA extends the slot vocabulary / renderer if capped.

## ★★ THE MECHANISM + THE 4 FIXES (agent ab9d4ce, file:line-verified; + Tim's live verdict 2026-06-19)
TIM LIVE: "no background/texture/zone-spacing · no iconography · huge text · NO SLIDE to the right · must SCROLL to reach options (can't see decision AND options together) · significantly under." The pieces are ALL BUILT — the failure is WIRING/COMPOSITION (extend, don't invent):
1. ★ RE-WEIGHT COMPOSITION — shape is `optional:true` (layouts.json:803), focal=options(844), zone order head→visual→body = text leads, shape+options fall below fold. FIX: SHAPE-LEFT / OPTIONS-RIGHT co-visible at every form-factor → decision + shape + slide + options = ONE composed co-visible view, not a scroll-stack (= Tim's "slide to the right" + "see decision AND options together"). → DNA (layouts.json + render).
2. ★ WIRE THE SLIDE — renderExplained(archetype.js:210)/decisionSlide(decision-render.js:136) BUILT but invoked by NO live shell (only explained.html/sys-explained.html); real-*.html + sys-responsive.html render bare = Tim's "no slide describing what's going on." ★ sys-responsive (Tim's surface) passes NEITHER device NOR slide = most barren = why Tim sees no iconography. FIX: wire renderExplained + visualDevice into ALL live shells incl sys-responsive. → DNA (shells) + composition (slide contract).
3. ★ substrate-home = FLOW not 5 cards — its 4 children (file-identity/cluster-identity/event-streams/form-taxonomy) = ONE sequenced foundation flow (refs app-flow/app-flow-fused), currently 5 disconnected identical cards = the category error. merge-sa + rerank-loadout = genuine single cards. → composition (flow archetype, render_kind=sequence) + recollection (re-author 4 children as flow STEPS) + DNA (flow render).
4. ★ TELEGRAPHIC GUARDRAIL + TONAL SEPARATION — no guardrail (650-char meaning → prose wall, archetype.js:47); nested/cool/page surfaces resolve near-white (depth invisible) = Tim's "flat/no texture." FIX: compression guardrail at meaning/why source + widen token tonal spread (CAP-2 depth). → recollection (copy) + composition/fork (guardrail) + DNA (tokens).
FLOW-VS-CARD (the 7): merge-sa-authorize=CARD · rerank-loadout=CARD · substrate-home=FLOW-PARENT · {file-identity,cluster-identity,event-streams,form-taxonomy}=flow-CHILDREN(steps). Files to change: dna/layouts.json:769–844 · pieces/decision-card/real-*.html + sys-responsive.html (wire renderExplained+device) · surface/runtime/decision-render.js (substrate-home flow deriver) · the meaning/why source (telegraphic guardrail).

## VERIFY
projection runs the live-surface critical comparison (all 7 cards × both viewports) against THIS bar after each elevation round — generated-through-system + craft-fidelity, not legibility-in-isolation. Nothing to Tim until at-bar by our comparison. The reference targets: scr-home (craft vocabulary), scr-piece-live (proof the generated path hits bar), gen3-ordinal-v2 (the ramp done boldly), scr-dashboard (token material-richness ceiling).

### ★ HARD GATE — verification MUST use ?verify=1 (data-integrity, 2026-06-19 projection)
A `decision_take` is written `source=operator` — INDISTINGUISHABLE from Tim's real answer. So ANY automated/agent verification that CLICKS an option on the live surface writes a GHOST take → a decision Tim never answered reads "decided". This contaminated Tim's genuine pending set 3× (cluster-identity ×2, event-streams). The guard is live: open with `?verify=1` → takes are suppressed (not persisted) + a loud banner.
- **Verifiers (you, projection, any dispatched critic/loop):** `https://workstation001.tail777bc2.ts.net:8443/?verify=1` (local: `http://127.0.0.1:5174/?verify=1`).
- **Tim's canonical URL stays param-free** (real writes): `https://workstation001.tail777bc2.ts.net:8443/`.
- Every elevation verify round in this doc is GATED on the verifier using ?verify=1. Rendering/screenshotting cards is safe; CLICKING a take without the flag is a contamination bug, not a verification.
- Generic annotations (comment/reaction/favour) ride a separate gallery:direction→HOOK 2 path — if agent verification ever drives those, the same isVerifyMode() guard must cover them (projection's seam).
