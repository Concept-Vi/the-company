# The Operator Cycle — Completion Criteria (the overnight spine)
*Tim 2026-06-20, running the fabric overnight. His ask, decompressed: a DECISION is a TYPE that is a particular kind of SEQUENCE (≥1 cards — presentation + explanation + choice, multi-card to aid explanation) ATTACHED TO A CHANNEL; the channel STACKS operator-directed things (presentations · explanations · decisions); the fabric works autonomously UNTIL BLOCKED ("no more work can be done without clearing them") → Tim CLEARS the stack → the fabric RESUMES → the cycle REPEATS. Everything to do it perfectly: visual + use verification, FUNCTION and FORM.*

## ★★★ THE OVERNIGHT TARGET — ONE VERTICAL SLICE (advisor-sharpened; this overrides "build the six groups")
The overnight's worth is decided by FOCUS, not breadth. The provable unit of Tim's whole ask = **ONE COMPLETE CYCLE ON ONE REAL DECISION**: a multi-card decision-sequence · attached to a channel · stacked · rendered AT-BAR (function+form) · that Tim can actually CLEAR · with the downstream RESUMING. That single slice exercises A+B+C+D+E on one instance — it IS the prove-on-one discipline applied to the cycle.
- **THE FAILURE MODE TO ACTIVELY PREVENT: fan-out.** NOT "composition builds the whole type system + projection builds the whole stack + someone specs the engine" → five unproven layers by morning and still no single working, beautiful, cleared decision. The target is the VERTICAL slice, not each group's breadth. Every stream builds only the thin slice through its group that the ONE decision needs.
- **THE GATING MILESTONE: C1 (the keystone card, merge-sa) AT-BAR, verified by LEAD'S OWN EYES** (chrome-devtools, both viewports, the live surface). It's been in-flight all session, Tim's been disappointed twice, and the whole cycle inherits its engine. Stream "it's at-bar" reports are NOT the verification (the bare-card-in-the-shell miss was caught by lead's render, not the stream's claim). If C1 doesn't land, THAT is the morning headline — not the layers built around it.
- **DEFER E2 (the automated BLOCKED-detector).** It's the novel, ungrounded part and the slice doesn't need it: LEAD plays the blocked-detector role MANUALLY for the prove-on-one (stack one decision → declare blocked → Tim clears → observe resume). Prove the MECHANISM (stack→render→clear→resume) on one instance; the auto-detector is a later generalization needing its own investigation, not speculative overnight code.
- **SEQUENCE TO fork's OFFLINE WINDOW (~down till 1am Brisbane).** fork owns the slice's heart (A3 channel-attachment · D3 attribution · E resume). So the slice cannot CLOSE before ~1am. PRE-1am realistic: DNA→C1 (keystone at-bar), composition→A (type + card-kinds, thin), projection→B (stack render against the EXISTING DecisionsInbox). POST-1am: fork wires the binding + attribution + resume. THEN lead verifies the whole slice.
- **HELD LIGHTLY (both/and, await Tim's confirm):** "presentations · explanations · decisions" could be standalone stack-items OR cards-within-a-decision. The design carries BOTH (card-kinds A2 + item-types A4) — sound, but do NOT build deep on the standalone-presentation path until Tim's reaction confirms it. The slice uses cards-within-a-decision (the certain reading).

### ★ RULING — co-visible vs stepped, and the TWO levels of "card" (lead, 2026-06-20; composition's reconciliation 354ac94)
Tim named TWO distinct levels — both honored, kept distinct:
- **"each decision can have more than one card to help with explanation"** = the card-KINDS (present · explain · choose) — the PARTS of ONE decision (composition's `card_kinds`, a grouping over the composed-view slots: present=question/kicker/kind/shape · explain=the slide · choose=options/state/decided).
- **"decisions = a particular kind of SEQUENCE attached to channels"** = decision.steps (many child decisions) + the channel-stack — the sequence of MANY decisions. `card_kinds ≠ decision.steps`.
★ **CO-VISIBLE vs STEPPED is a RESOLVER OUTPUT, not a stored variant** — the invariant is the three kinds; whether they render co-visible (kinds as zones of one view) or stepped (separate cards) COMPUTES against the device × COMPLEXITY coordinate (the invariant-application law, applied to the card itself).
- **merge-sa (the gate) = CO-VISIBLE** — the three kinds are the zones of one composed view; the hard gate holds (decision+options together @390, no scroll). merge-sa does NOT step (stepping reintroduces Tim's "can't see decision AND options together"). NON-NEGOTIABLE for C1.
- the multi-card-STEPPED capacity is real but proves on a COMPLEX decision LATER (explanation rich enough that the resolver steps it). Do NOT force merge-sa to step to "show multiple cards" — that breaks the gate. Simple→co-visible, complex→stepped, resolver decides.
- **Tim's confirm (held lightly):** merge-sa as ONE co-visible view (not stepped cards) is the simple-binary reading that honors BOTH his "more than one card" (capacity, resolved by complexity) AND his co-visibility gate. His to confirm, not assumed.
- **LEAD's OWN HOURS: weight toward making the live surface REAL + verifying it by sight — NOT more boards.** (~6 artifacts shipped today; Tim judges the surface, not the spec.)

## THE CYCLE (the thing being built, one diagram)
```
fabric works autonomously  ──produces──▶  CHANNEL-STACK (ordered operator-items: presentation | explanation | decision-sequence | verify-request)
        ▲                                          │
        │                                          ▼
     RESUME  ◀──unblocks──  Tim CLEARS the stack (decide-in-surface · verify-by-sight · approve)  ◀── BLOCKED-detector fires
        │                                          ▲                                                  (no work proceeds without a clear)
        └──────────────────── the cycle repeats ──┘
```
One channel = one operator work-queue. A decision is one kind of stacked item (a channel-attached card-sequence). Tim clears in batches when the fabric saturates.

## VERIFICATION RULES (the bar — read before checking anything)
EVERY criterion is **two-faced: FUNCTION and FORM. Both, or it is not done.** A line is green ONLY when BOTH are verified BY USE (not by reading code, not by a DOM query):
- **FUNCTION** — the real behaviour moves real state; verified by USE (drive it on the live surface). No stub, no placeholder, no fake result.
- **FORM** — built from the design system (DNA archetype + tokens, via the resolver; NO bespoke values, NO hand breakpoints); coherent + responsive by COMPUTED allocation; a navigable visual surface, not a text-wall; at-bar by the reference comparison (scr-home / scr-piece-live / gen3-shapes / app-flow) AND Tim's 5 (background/texture/zone-spacing · iconography · not-text-heavy · co-visible decision+options · legible).
- **VISUAL VERIFICATION** — chrome-devtools, the WHOLE screen, both viewports (390 + 1440), via the live operator surface (:8443 / :5174). ★ Drivers use `?verify=1` (no ghost takes).
- **USE VERIFICATION** — the cycle actually runs: an item stacks → renders → Tim clears it → the fabric observes the clear → resumes. End-to-end, by use.
- Status honesty: **VERIFIED** (ran + looked) · **DESIGNED** (specced, not built) · **BROKEN** (exists, wrong result). Never mark green on code-reading.

---

## GROUP A — THE DECISION-SEQUENCE TYPE (foundation; everything depends on it)
*A decision = a channel-attached sequence of ≥1 cards. Extends the SHIPPED decision.steps (composition a3bbe94/c50de96, render_kind=sequence) + decision:// + the decision-card archetype; adds the channel binding + multi-card-kinds.*

- **A1 · decision-as-sequence type** — a `decision` resolves to an ORDERED sequence of ≥1 cards (not 1:1 card). render_kind=sequence carries it.
  - FUNCTION ☐ a decision with N cards advances card→card; state (which card, the pending choice) is real, addressed (decision://), resolved through the ONE resolver. by use.
  - FORM ☐ the sequence reads as a navigable progression (not a scroll-wall); each card at-bar; the advance is a real transition. by sight, both viewports.
- **A2 · multi-card KINDS** — a card carries a `kind`: `presentation` (show the thing) · `explanation` (why / what's at stake — the RHM's leg) · `choice` (the options + the take). A decision-sequence = ≥1 presentation/explanation cards THEN the choice card(s). A decision MAY have >1 choice card.
  - FUNCTION ☐ each kind renders its role; the choice card's take writes the decision_take (exact contract: mark_type=`decision_take`, target=canonical decision_address, value=option LABEL); presentation/explanation cards carry no take. by use.
  - FORM ☐ each kind is a distinct archetype-variant (resolved from the card's kind — the TYPE axis), at-bar; the explanation card shows real situated meaning + a real data-bound device (no decorative chart). by sight.
- **A3 · channel-ATTACHMENT** — a decision-sequence is bound to a channel (the channel carries it). The binding is data (registry-true), not code.
  - FUNCTION ☐ a decision-sequence created against a channel appears in that channel's stack; resolving the channel yields its ordered items incl. this sequence. by use.
  - FORM ☐ n/a at the data layer (verified at the stack render, B-group).
- **A4 · the item-TYPE registry** — a channel-stack item is a TYPE: `presentation | explanation | decision-sequence | verify-request | …` (a registry, so adding an item-kind = a row, no engine code — the axes-are-registries law). 
  - FUNCTION ☐ each item-type resolves to its render + its clear-semantics (a decision clears by a take; a verify-request clears by a verdict; a presentation clears by acknowledge). by use.
  - FORM ☐ each item-type is at-bar in the stack (B-group).

## GROUP B — THE CHANNEL-STACK (the operator work-queue)
*The channel becomes Tim's stack of things-to-clear. Generalizes the existing surfaced-queue (list_surfaced / "N decisions waiting" / DecisionsInbox) from decisions-only to the full item-type set; rides the channel fabric (channels/channel_act/channel_posts/cc_board).*

- **B1 · the stack accumulates** — the fabric PUSHES operator-items onto a channel as it works (a decision it needs made, a thing to verify, an explanation it prepared). Ordered, durable, addressed.
  - FUNCTION ☐ a session pushes an item to the channel-stack; it persists + is ordered; the surface reads the live stack. by use (a real push from a fabric session → appears).
  - FORM ☐ the stack renders as a navigable, legible queue (not a log dump) — each item a card-preview with its kind + state; at-bar; computed allocation across devices. by sight, both viewports.
- **B2 · the stack is the surface's spine** — the operator surface shows the channel-stack as the primary "what needs you" view (the DecisionsInbox, generalized). Items open into their card-sequence.
  - FUNCTION ☐ tapping a stacked item opens its sequence (A1); clearing returns to the stack with that item resolved/removed. by use.
  - FORM ☐ the stack→item→stack flow is a coherent navigable surface; the V/RHM present; at-bar. by sight.
- **B3 · clear-state per item** — each item has a clear-state (pending → cleared) + how-it-clears (decide/verify/acknowledge). The verify=1 guard applies (a verifier clears nothing real).
  - FUNCTION ☐ clearing an item flips its state durably (real write, attributed); ?verify=1 suppresses the write (no ghost clear). by use, BOTH (real clear persists · verify-mode does not).
  - FORM ☐ pending vs cleared is visually unmistakable; the cleared item leaves the active stack. by sight.

## GROUP C — THE RENDER (function + form, via the resolver — the elegance bar)
*Every card (all kinds) renders through the ONE renderArchetype + the resolver (RESOLVER-BUILD.md), at-bar. This is the keystone work, generalized from the single decision-card to the multi-card sequence.*

- **C1 · the keystone card at-bar (merge-sa)** — the single decision-card (choice kind) is at-bar: legible (un-clamped options, real situated meaning), real data-bound device, the explaining content, CAP-2 depth, WIRED IN THE OPERATOR SHELL (renderDecisionGallery/sys-responsive). [IN FLIGHT — DNA re-attacking with critics; proof #1.]
  - FUNCTION ☐ merge-sa resolves + the take writes, in the operator shell, by use.
  - FORM ☐ at-bar by the reference comparison + Tim's 5, both viewports, ?verify=1. proof #1.
- **C2 · the device-axis on the card (the resolver's prove-on-one)** — merge-sa resolves across portrait/landscape/desktop by COMPUTED ALLOCATION (relationships, not breakpoints), card-content @ card-scale.
  - FUNCTION ☐ one definition → all device-coordinates; no hand-written form-factor switch. by use.
  - FORM ☐ at-bar on each device-coordinate; the layout is derived, not enumerated. by sight, all three.
- **C3 · the whole-screen fractal** — the HOST shell resolves from the SAME resolve()/device-root as the card content (one resolver, two scales). Kills App.tsx classify(w,h)→3 modules + surface.css/source.css size @media; KEEPS preference axes (prefers-reduced-motion — a resolved axis, not a stripped breakpoint).
  - FUNCTION ☐ the whole merge-sa screen (host+card) resolves across devices from one resolve(); reduced-motion still honored. by use.
  - FORM ☐ host + card co-allocate cleanly on every device-coordinate; at-bar. by sight, both viewports.
- **C4 · the multi-card sequence at-bar** — presentation + explanation + choice cards each at-bar, and the SEQUENCE (advance/back) is a real navigable transition. The card KIND resolves its variant (type-axis).
  - FUNCTION ☐ a real multi-card decision advances through its cards; the choice card's take works. by use.
  - FORM ☐ each card kind at-bar; the sequence reads as progression; at-bar both viewports. by sight.
- **C5 · the explanation leg (RHM)** — the explanation card's content resolves through the RHM (run_turn / the explain leg) + common memory (recollection), not stored prose; situated, telegraphic-but-meaningful.
  - FUNCTION ☐ the explanation is generated/resolved live for the real decision, grounded. by use.
  - FORM ☐ legible, situated, at-bar (not a wall, not a slogan). by sight.

## GROUP D — THE CLEAR MECHANISM (how Tim works the stack)
*Tim clears items in-surface: decide (the take), verify (a verdict), acknowledge. Rides the gated floor + operator-attribution.*

- **D1 · decide-in-surface** — Tim makes a decision by acting on the choice card; the take IS the write-back (decision becomes a resolved artifact). [decision:// take wired — fork 97be816.]
  - FUNCTION ☐ a real take on the live surface writes the decision_take, attributed to Tim (operator-token #1b), the decision re-resolves to decided. by use.
  - FORM ☐ the take is a single clear gold-commit action at thumb-reach; the decided state is unmistakable. by sight.
- **D2 · verify-in-surface** — a verify-request item lets Tim confirm a thing by SIGHT/USE; clearing it records the verdict + unblocks whatever depended on it.
  - FUNCTION ☐ Tim's verdict on a verify-request writes durably + unblocks the dependent work. by use.
  - FORM ☐ the thing-to-verify is shown as a navigable visual surface (function AND form visible), not a description. by sight.
- **D3 · attribution floor (#1b)** — every consequential clear (take/verdict/approve) carries genuine-operator attribution (the per-session operator token); a verifier/agent CANNOT forge a clear (the unified gated floor — same seam as the tool-face invoke + territory-write).
  - FUNCTION ☐ a real operator clear persists; an unattributed/agent clear is refused (403/suppressed). by use, BOTH.
  - FORM ☐ n/a (security floor).
- **D4 · batch clearing** — Tim can work the whole stack in a sitting (clear item → next surfaces → repeat) without leaving the surface.
  - FUNCTION ☐ clearing one item advances to the next pending; the stack drains by use. by use.
  - FORM ☐ the batch flow is a coherent, low-friction surface (no dead-ends, no scroll-hunting). by sight.

## GROUP E — THE CYCLE ENGINE (autonomous-until-blocked → clear → resume → repeat)
*The producer/consumer loop. The fabric works, stacks operator-items, DETECTS when it's blocked (everything left needs Tim), signals the stack is ready, observes Tim's clears, RESUMES. This is the operator-loop heart.*

- **E1 · the fabric produces operator-items** — as sessions work, work that NEEDS Tim is pushed to the channel-stack (not held in a session, not lost) — a decision, a verify-request, a presentation. (Connects gap-pressure + no-silent-failures: a blocker becomes a stacked item, never a silent stall.)
  - FUNCTION ☐ a session hitting a needs-Tim point stacks an item (vs stalling silently); by use (induce a needs-Tim → it appears on the stack).
  - FORM ☐ the stacked item is legible + at-bar (B1).
- **E2 · the BLOCKED detector** — the fabric detects "no more work can be done without clearing" (all remaining work is gated on a stacked operator-item) and marks the cycle BLOCKED-on-Tim.
  - FUNCTION ☐ when every live lane is gated on a stacked item, the cycle reports BLOCKED + the ready stack; verified by use (drive lanes to saturation → blocked fires, not a false-idle). by use.
  - FORM ☐ "the fabric is waiting on you, here's the stack" is a clear surface state (not a guess). by sight.
- **E3 · resume-on-clear** — when Tim clears an item, the fabric observes it and the dependent work RESUMES (the decision's downstream unblocks).
  - FUNCTION ☐ clearing a blocking item resumes the dependent lane (the decided value flows to what was waiting). by use (clear → downstream proceeds).
  - FORM ☐ n/a (engine) — surfaced as the item leaving the stack (B3).
- **E4 · the cycle repeats** — resume → more autonomous work → more items stacked → blocked again → Tim clears → … the loop sustains across sittings.
  - FUNCTION ☐ at least TWO full cycles run end-to-end by use (work→stack→blocked→clear→resume→work→stack→…). by use.
  - FORM ☐ the operator always has one coherent "what's mine to do / what's the system doing" surface across the cycle. by sight.
- **E5 · notify-when-ready (optional, the wake)** — when the cycle goes BLOCKED, Tim is notified the stack is ready (the channel is the carrier; a notice/PWA signal). [DESIGNED — confirm the channel can signal; mobile/Tailscale per the established access.]

## GROUP F — STANDING PRODUCT-FACE + INTEGRITY (held across all surfaces)
- **F1 · everything generated-through-the-system** — no hand-stubbed cards/screens; the system is EXTENDED to generate what it needs (the must-be-generated rule). by inspection + use.
- **F2 · the design system is the source** — all render via DNA archetype + tokens + the resolver; no bespoke values, no hand breakpoints; one-change-propagates (verified: a DNA change reaches the cards without UI-code edit). by use.
- **F3 · no ghost-contamination** — the verify=1 guard + the server attribution floor cover every clear-path (take/verdict/approve); proven a driver clears nothing real. by use.
- **F4 · no silent failure** — a needs-Tim or a failed clear surfaces (a stacked item / a Notice + a Gap), never a silent stall or a fake success. by use.
- **F5 · self-coverage (the loop's reflexive end)** — the cycle's own pieces are typed/addressed nodes the coverage mechanism can map + judge (the system reasons about its own operator-loop). [DESIGNED — the coverage-thread re-join; later.]

---

## PRIORITY ORDER (dependency — foundations first)
1. **C1** — the keystone card at-bar (merge-sa). Proof #1; everything visual rests on it. [IN FLIGHT.]
2. **A1·A2·A4** — the decision-sequence type + card-kinds + item-type registry (the data foundation).
3. **A3·B1·B2** — channel-attachment + the stack accumulates + the stack is the surface spine.
4. **C4·C5** — the multi-card sequence at-bar + the RHM explanation leg.
5. **D1·D3·D4** — decide-in-surface + the attribution floor + batch clearing.
6. **E1·E2·E3·E4** — the cycle engine (produce → blocked → resume → repeat).
7. **C2·C3** — the device-axis + whole-screen fractal (the resolver prove-on-one; rides on C1, generalizes the render).
8. **D2·B3** — verify-in-surface + per-item clear-state.
9. **F1–F4** — standing product-face + integrity (held throughout; F5 + E5 later).

## OWNERS (anchored on the keystone; the fabric builds — no fragmentation)
- **DNA** — C1 (keystone) → C4 card-kind variants + C2/C3 computed render; F2.
- **composition** — A (decision-sequence type, card-kinds, item-type registry) + the resolver contract (C2/C3) + A4 registries; D1 take-generalization.
- **projection** — B (the channel-stack as the surface spine) + C3 host fractal + the stack render; D4 batch flow.
- **fork** — A3 channel-attachment (the binding) + E (the cycle engine: produce/blocked/resume) + D3 attribution floor (#1b) + C5 RHM explain leg.
- **recollection** — C5 common-memory into the explanation + E1 (what-needs-Tim surfacing).
- **lead** — hold the bar + the sequence + the gate (D3 review) + the cycle's integrity (F) + visual/use verification before anything reaches Tim.

## VERIFY (the loop's exit test)
DONE = TWO full operator-cycles run end-to-end on the live surface, by use AND by sight, both viewports, ?verify=1 for drivers: the fabric works → stacks a multi-card decision-sequence + a verify-request on a channel → goes BLOCKED with a legible at-bar stack → Tim clears (decides + verifies, attributed) → the fabric resumes the downstream → stacks again → repeat. Function AND form green on every item. Nothing to Tim until at-bar by our own comparison. Relates: [[the-invariant-application]] (the resolver), DECISION-SURFACE-BUILD.md, RESOLVER-BUILD.md, TOOL-FACE-BUILD.md (the shared gated floor), [[project-operator-surface-rhm]].
