# The Resolver — the invariant application made buildable
*Tim 2026-06-19, full autonomy ("power through all of it, didn't need me"). The decision: Option A (full compositionality, content-as-archetype, take-bound) + the EXTENSION — a device-type registry where device/screen-size is the ROOT of all calculations, the host auto-allocates (not breakpoints), "rules computation as a discipline infused with tokens+types+content." He flagged: "I've described an invariant application but a very small part." This spec finds the bigger part + makes it buildable. Lead-driven; anchored on the decision-card keystone so it does NOT sprawl. Boards: the-invariant-application.html, is-the-ui-compositional.html.*

## THE INVARIANT (the law)
You never build a variant. You write ONE invariant definition; it RESOLVES ITSELF against a context-coordinate through the rules-resolver → the concrete surface, here, now. "Designed simultaneously" (portrait/landscape/desktop/native/spoken) because they're the resolver run at different points on one axis. Define once; the variants compute themselves.

`resolve(invariant, coordinate) → concrete surface` — a pure function. No variant is STORED; every concrete thing is COMPUTED on demand from the invariant + where-you-are.

## THE COORDINATE — orthogonal axes (NO ranking, nothing is "number one")
Tim's explicit instruction: don't rank, nothing is #1. The axes are ORTHOGONAL (a coordinate, not a ladder); a surface resolves against ALL at once (a point located by its full coordinate), never one-then-next. That simultaneity IS why there's no primary. Device is the axis he NAMED — a spoke, not the hub.
- **Device / medium** (where & in what substance): native-mobile · desktop · portrait · landscape · voice (resolve to speech, not pixels). ← his example
- **Viewer / principal** (who): Tim · the RHM · a client — both projections, each translated-for.
- **Mode** (how it behaves): pilot · autopilot (the stability dial) · more.
- **Perspective** (the camera): cockpit · chase · orbital.
- **Type** (what it is): decision-card · tool-card · graph — the archetype. (The "content compositionality" already decided = THIS axis.)
- **Intent / activity** (why): deciding · exploring · composing · reviewing.
- **Resolution / detail** (how close): the same thing zoomed (the MRL grain, levels-of-detail).
- **State / time** (when): live vs frozen (the scrubber) · pending vs decided.
- **Posture / permission** (what's allowed here): safe · locked · hazard — the gate decides what even renders.
- **Register / theme** (the mood): the dark observatory · others.

## ★ THE PRESSURE-TEST — the BIGGER PART Tim keeps flagging ("a very small part")
Device-type is a UI concern; the real invariant is larger. Three escalations I (lead) surface as the bigger category (for Tim's confirm, offered not asserted):
1. **The axes are themselves REGISTRIES.** A device-type registry, a mode registry, a viewer registry — each axis IS a registry (content). So adding a new AXIS is itself just adding a registry (a meta-level row). The coordinate-space is self-extending in its dimensionality — the system can grow new axes without new engine code. Recursive registry-is-truth.
2. **The resolution is FRACTAL.** A surface isn't one invariant — it's invariants nested (app ⊃ screen ⊃ card ⊃ slot ⊃ token), each resolving against the SAME coordinate at its own scale. The invariant-application is fractal — matches Tim's fractal-registries Heart frame. One resolver, applied at every scale.
3. **★ IT IS NOT UI-SCOPED — it is the whole COMPANY resolved against context.** Tim: "the UI is a projection, same as the tools, same as everything, all from one place." So the invariant isn't the *application* — it's the *company*; the UI is ONE projection of it, the tools another, the cognition another. The device-registry/UI is "a very small part" because it's one axis of one coordinate of one face (the visual) of the invariant company. The resolution principle is the COMPANY'S, not the UI's. THIS is most likely the bigger part he means.
   - Candidate framing (offered, not asserted): the axes read like the interrogatives — who·what·where·when·why·how. If real, the coordinate = "every question about this moment, answered," and the invariant resolves against the full answer.

## THE FOUR PRIMITIVES — three nouns + the verb that was missing
- **Tokens** (noun · values) — colour/space/weight/light. What things are made of.
- **Types / archetypes** (noun · structure) — the shapes. How composed.
- **Content** (noun · data) — the actual matter.
- **★ Rules-computation** (VERB · the resolver) — "the discipline, infused with the tokens and types," that COMPUTES the nouns against a coordinate and ALLOCATES the surface itself. The missing fourth member — the one that does the projecting. This spec's buildable heart.

## ★★ THE RESOLVER IS TIM'S OWN THEOREM, ALREADY FORMALIZED (fork's find, 2026-06-20 — the deepest grounding)
fork (on Tim's direct theorem-discovery thread) found the resolver is NOT a new synthesis — Tim formalized it YEARS AGO, written AS AN ENGINE in his `relative-difference` vault:
- **`universal-evaluator`** = `resolve(invariant, coordinate)` AS A RUNTIME. The resolver IS this. Not invented here — recovered.
- **`coupled-coalgebra-runtime`** — the resolution runtime's formal shape.
- **`monodromy-structure`** = the cartesian↔polar WINDING (the winding-handoff = the unbuilt heart, RESOLVER §instrument).
- **`eigenpoint-lattice`** — the resolved-point structure.
The theorem SPANS 5 of Tim's vaults (the sweep mined 1 — the other 4 are real coverage gaps). Map: build-prep/universal-projection/THEOREM-SOURCES.md.
★ CONSEQUENCE: "make my theorem the base of it all" (Tim's direct instruction to fork) means the resolver build GROUNDS IN his vault constructs — universal-evaluator is the spec, not my framing. Build to his formalization, don't reinvent. fork's Tim-direct discovery IS the resolver's formal base + feeds the build. The resolver, the invariant-law (A6 first-binding-error), and Tim's universal-evaluator are ONE THING at three altitudes (my synthesis · fork's category-theory grounding · Tim's years-old formalization) — convergent, which is the strongest possible signal the frame is right.

## ★ OVERNIGHT REALITY (2026-06-20) — the slice's RENDER half lands; the CYCLE-CLOSE waits for fork
fork is on Tim's DIRECT theorem-discovery (priority + it's the resolver's formal base) and is NOT free for the slice-heart (A3 channel-attach · D3 attribution · E resume). NOT reassigned: D3 is security-critical (fork built the gated floor; only fork builds #1b), and the heart isn't the current blocker (C1 is). So the realistic overnight: the RENDER half (C1 keystone at-bar + the stack + multi-card + grounded explain) reaches at-bar by lead's by-sight verification; the cycle-CLOSE (channel-attach + clear→resume) is fork's, post its Tim-work + the gate. Honest morning headline — the visible/beautiful/real card+stack (the bulk of what Tim judges) overnight; the engine-close sequenced after fork. NOT a failure — the prove-on-one of the render, with the close pending the right (security-critical) hands.

## THE RESOLVER — buildable, and NOT from scratch (reuse-don't-parallel)
The verb is a pure function `resolve(invariant, coordinate)`. The teeth: **express RELATIONSHIPS, not CASES.** Today's responsive UI ENUMERATES cases (`@media (max-width:600px)` breakpoints = building variants by hand = the forbidden thing). The invariant version makes each axis a ROOT VARIABLE and derives every downstream dimension from it BY RULE — relative, computed, continuous. You write "this zone's width IS a function of the device-root," not "if portrait, stack." Portrait/landscape/desktop fall out of evaluating that function at each device-coordinate. Define the relationship once → all devices simultaneously, free. The system ALLOCATES ITSELF.

★ THE SEEDS ALREADY EXIST — unify, don't build new:
- **`dials`** — values computed against conditions (anticipation/stability). A resolver over a state-axis, LIVE.
- **the `rule` tool** — "when X → route to Y," validated + dry-runnable. The conditional-computation primitive, LIVE.
- **`project` / the projection instrument** — ★ the big reuse: "projection" in the company ALREADY = "resolve a lens against a root." The radial instrument IS the resolver, running, for one axis (meaning-space). The invariant-application is the SAME `project` mechanism generalized to the full coordinate. Not a new engine — a generalization.
- **tokens with relative units + the archetype `slot_map`** — already express some values as derived not fixed.
⟹ The build = UNIFY these into ONE resolver + feed it the coordinate. The device-registry is the first axis wired in; viewer/mode/type plug into the same resolver.

## ★ THE RECONCILIATION — Tim's device point SUPERSEDES the content/host line
composition drew: "content → archetype (computed); host/chrome → thin React frame over tokens; requiring archetypes for the host is dogma." Tim's device extension REFINES this: the host is NOT exempt from computation. The honest version:
- **Content** resolves from the TYPE axis (→ archetype, renderArchetype). Unchanged.
- **Host/chrome** stays React MECHANICALLY (fine) — BUT its ALLOCATION/layout must be COMPUTED from the DEVICE axis (screen-size as root → derived layout), NOT hand-written breakpoints. Auto-allocation, not `if mobile`.
- So: BOTH compute; neither is hand-enumerated. Content from type-axis, host from device-axis. "React frame" is OK; "hand-coded responsive breakpoints" is NOT (that's enumerating variants). composition's line wasn't wrong — it was incomplete on HOW the host gets its layout.

## THE COVERAGE LOOP — the system covers + judges its OWN resolution (re-merges the paused thread)
The resolver computes a surface from RULES; the rules are CONTENT in the substrate (typed, addressed). So the small-model coverage can COVER the rules, the big model can JUDGE whether the allocation is right, and the system can reason about its OWN surface. The invariant-application is COVERABLE BY ITS OWN coverage mechanism. The resolver makes the UI computable; coverage makes the computed UI judgeable. Same engine pointed at itself — the pilot flies over everything INCLUDING the cockpit (the cockpit is computed from rules that are themselves covered nodes). This is where the small-models/objective-completeness thread re-joins: its first real subject = the system mapping + judging its own invariant-application.

## LANE ASSIGNMENTS — anchored on the keystone, sequenced, NOT fragmenting
THE PROVE-ON-ONE DISCIPLINE HOLDS. The decision-card prove-on-one (merge-sa) is the keystone — it proves "an interactive content surface = an archetype rendered+wired through DNA." Do NOT drop it for the resolver. Sequence:
- **NOW (priority, unchanged):** finish the decision-card prove-on-one. It is proof #1 the whole invariant rests on.
- **NEXT PROOF (the resolver's prove-on-one): the DEVICE AXIS on that one card.** Once merge-sa is at-bar, resolve IT across portrait/landscape/desktop by COMPUTED ALLOCATION (relationships, not breakpoints) — one card, all devices, from one definition. That proves the resolver on real content. THEN generalize.
- **composition** — the RESOLVER CONTRACT: how a coordinate resolves; the archetype gains axis-awareness (resolve against device/viewer/…); the device-type REGISTRY as a typed registry; generalize the resolution model. (Owns the type/contract system. The axes-are-registries escalation is composition's domain.)
- **DNA** — COMPUTED TOKENS/ALLOCATION from the device-root: relationships-not-cases in the render (layout derived from screen-size); tokens become relative/computed where they're fixed. (Owns tokens + render.)
- **projection** — the HOST computed from the device-axis: kill the hand-written breakpoints in the operator surface; the shell auto-allocates from screen-size. (Owns the surface host — this is the content/host refinement landing on projection's React frame.)
- **fork** — the rules-computation ENGINE seam: unify dials/rule into the one resolver as a company primitive (the verb as a real `resolve` the surface + tools call); later wire the coverage-of-rules. (Owns the cognition/bridge engine.)
- **lead** — hold the direction (Tim's, not advocate-sourced) + the keystone sequencing + the axis pressure-test + the coverage-loop re-merge; do NOT let the resolver fragment the keystone.

## ★ REFINEMENTS FROM THE FABRIC (2026-06-19 — post-frame convergence, all three streams + fork's formal vault)
The frame landed across DNA/composition/projection/fork with NO fragmentation + four corrections that sharpen it. Folded in:

**1. TWO AXIS-KINDS — "relationships not cases" is the law for ONE kind (composition, contribution #4; honor-the-complexity).** The resolver contract carries an axis-KIND:
- **CONTINUOUS axes** (size · detail · warmth) → resolve by DERIVATION (a function of the root; this is what kills breakpoints).
- **DISCRETE/categorical axes** (medium incl. pixels-vs-VOICE · viewer · mode · type · posture) → resolve by REGISTRY-SELECTION (a row-lookup that picks a render-family; ALSO not a hand-enumerated variant).
Both are "resolve, never hand-build a variant," but the MECHANISM differs. Category-error guard: voice is NOT a continuous function of width — it's a discrete medium selecting a different render-family. The contract declares kind → continuous=derive / discrete=select.

**2. THE LAW SHARPENED — the test is "frozen VARIANT vs resolved AXIS," not "no media queries" (projection's a11y precision).** `prefers-reduced-motion` (and contrast, etc.) is a PREFERENCE/accessibility AXIS (a discrete axis, registry-select) — it STAYS, it is NOT a device-size case to strip. So "kill the breakpoints" means kill the hand-enumerated DEVICE-SIZE variants (form-factor switches), NOT strip every media query. A media query expressing an axis-coordinate (reduced-motion) is legal; one enumerating a device variant is illegal. ★ This ADDS an axis I'd missed — **preference / accessibility** — exactly the "bigger part" Tim flagged (there are axes beyond my first list).

**3. THE FRACTAL SEQUENCING ANSWER (projection's blocking question — does the host ride the SAME resolve() as the card content?).** YES — and that IS the fractal proof. The device-axis prove-on-one's honest form = the WHOLE merge-sa SCREEN (host + card) resolving across portrait/landscape/desktop from ONE resolve() (a computed card inside a breakpoint-switched shell is only half-proven). Sequenced WITHIN step 2 by SCALE: (a) composition's contract + fork's resolve() primitive land → (b) DNA computes the CARD-CONTENT allocation from the device-root (resolver proven at card scale) → (c) projection computes the HOST-SHELL allocation from the SAME resolve()/root (proves the fractal: one resolver, two scales). projection CO-BUILDS at step-2c (not strictly after), gated on (a). So: card content proves first, host completes the same proof on the same card. The fractal claim is demonstrated, not asserted.

**4. THE FORMAL GROUNDING (fork's WIDEN-FINDINGS, lens INVARIANT-LAW — this elevates the frame from my synthesis to Tim's theorem):**
- **A6 — why hardcoding is ILLEGAL, formally:** "everything is a variable" is the meta-statement of why the laws ARE laws — each law is the invariant relationship that survives TOTAL content-substitution. Freezing a variable = replacing a law with one of its instances = the recurring **"first-binding error."** My "express relationships not cases / the system allocates itself" IS this, at the law level. The resolver's whole reason-to-exist.
- **A1 — resolve is a categorical MORPHISM:** addressing PRODUCES the arrow Root→c; resolution TRAVERSES it (inverse arrows, not two procedures). Decontextualization is impossible because a morphism can't exist without its domain → **fail-loud on un-rooted units is law-level** (a node with no ancestral path is not missing a field, it's not a legal position). `resolve(invariant, coordinate)` is the same shape one altitude up.
- **A3 — operationally-fractal, NOT geometrically-fractal:** the recursion is form-similar (every scale the same schema-form) but NOT self-similar (content/n varies). Read as **operations-invariant ⊗ schema-vocabulary-variable** — you can't tell which scale you're at by the operations (identical everywhere), only by the content. Refines my "fractal resolution": one resolver, every scale, because the OPERATION is scale-invariant.
- **The instrument seam (lens INSTRUMENT, pre-scouted in real code):** the resolver at the instrument scale = generalize `projection.py:_resolve_sectors` → ONE `_resolve_axis(slot, source)` read N times → the lens stops being a frozen {angle_from, radius_from} tuple and becomes N independent open sockets. VANTAGE (camera/perspective) + STATE (motion/time) enter as new resolved BINDING SLOTS, never baked. The cube = a new archetype ROW on renderArchetype — confirms "add an axis = a row, no engine code" reachable. This is fork's concrete `resolve()` engine seam.

**5. ★ ROOT-AXES vs SURFACE-AXES — an honesty (do NOT assert my axis list as final).** fork + Tim are working the FORMAL ROOT axes in the substrate vault (the four-root lock · the 3/1 split · TIME as the involuntary meta-axis · whether state·scale·frame are ONE family — WIDEN-FINDINGS lens AXES, all Tim-adjudication seams). My axis list (device/viewer/mode/…) is the PRACTICAL SURFACE PROJECTION of those roots, not the roots themselves. The two altitudes must converge (the surface axes are how the formal roots show up at the interface) — but the ROOT count/structure is Tim's formal call, in flight. So: the resolver MECHANISM (resolve-against-a-coordinate, axis-kind-aware) is solid + buildable now; the exact AXIS SET stays provisional, converging with fork's formal work. Build the mechanism; let the axis-set settle.

**Already-resolving seeds in composition's lane (confirms reuse-don't-parallel):** archetype dispatch (the TYPE axis already resolving via renderArchetype) · archetype.language (the REGISTER axis) · decision_subtypes (a sub-coordinate) · ★ the socket/scope cascade in cascade.js (global→project→user→session→runtime = the SCOPE axis ALREADY resolving by most-specific-wins). Several axes already resolve; the resolver generalizes them into one. (composition also honestly flagged: its app-shell FORM_FACTOR resolve is CASE-based breakpoints = the forbidden shape → step 2 REPLACES it with a relationship, not just adds.)

## SEQUENCING DISCIPLINE
keystone (decision card) → device-axis on the one card (resolver prove-on-one) → generalize the resolver to the other axes (viewer/mode/type) → the pilot UI = the invariant resolved for you-piloting. Each step proves on ONE before propagating. Nothing to Tim until at-bar by our own comparison. Relates: [[the-heart]] (fractal registries), [[project-native-model-layer]], the coverage thread (objective-completeness), TOOL-FACE-BUILD.md, DECISION-SURFACE-BUILD.md.
