# E2 · The Live Cognition View + Steering — UX exploration (generative)

> **Status: open / generative / design surface (open-future).** This is the **UX/interaction exploration** that extends [[06-rendering.md]] and Completion-Criteria **G7**. 06 settled the *plumbing* (reuse spine: `cognition.*` SSE → `openStream` branch → `NodeShape`/`Edges` siblings, reflects-never-owns, registry-projected). This doc does NOT restate that. It attacks the four things 06 only gestured at:
> 1. **Swarm → glanceable shape** (the wall-of-N problem — 06's "frames accumulate fast" open Q, *solved* here).
> 2. **Motion as content** (it animates per turn — the temporal read is the information).
> 3. **The steering vocabulary** (mute/boost a role, change the cast live, "why did this part say that" — genuinely new).
> 4. **The RHM reading its OWN cognition as an interaction** (view + voice are one act).
>
> **Epistemic tags:** **Observed** (read in code/06, file:line), **Designed** (intended, not built — generative), **Open** (decide with Tim). **Constraints honoured:** addressing is **`run://`** throughout (R1-FOLD settled; `swarm://` dead; `cog://` CONFIRM-level — never assumed). The visual is **shape-not-count** — never N discrete dots as a hard number (R1-FOLD: co-resident cap is well below 32 at usable context). **Aesthetics/feel on-device = `needs-tim`** (Criteria lists "the cognition view's aesthetics" as never-self-certified).
>
> **The one sentence:** the per-turn swarm is not a list of N model-calls — it is a **river of thought converging into one spoken reply**, and the cognition view renders it as a *terrain* whose **shape carries the meaning** (how much thinking · how parallel · what fed the words · what failed · how fast it converged), up-translated to Tim's altitude by default, with the 32-node technical depth living one drill-down beneath.

---

## A · The core problem stated honestly: N concurrent roles is a WALL by default

A turn fires a swarm of role-runs (the landscape's "~32", really *well below 32 at usable context*, R1-FOLD). The naive render — one card per role, all firing at once — is **exactly the text-wall AGENTS.md rule 9 forbids**, just in node form. Thirty-ish cards lighting simultaneously is not a glanceable shape; it is visual noise that Tim must *read*, which is the failure mode [[feedback-render-for-cognition]] names ("his brain is the algorithm" only works when the **shape** carries the information, not when he has to parse 30 boxes).

**So the design problem is not "draw the roles." It is: what single SHAPE does the swarm collapse into, such that Tim recognises the turn's cognition in one look — and can descend into the 30 nodes only when he chooses?** That is the altitude-transformation layer ([[feedback-altitude-transformation-layer]]) applied to cognition: **the default view is NOT 32 technical nodes; it is the up-translated shape; the depth is drill-down.**

This doc answers it with **three nested altitudes** (§B), the **shape vocabulary** that makes each altitude readable-by-sight (§C), the **motion design** (§D), the **steering vocabulary** (§E), and the **RHM-reads-itself interaction** (§F).

---

## B · Three altitudes (the up-translation, default → drill-down)

06 proposed two zoom altitudes (Glance / Inspect). That is one too few. The swarm needs a **higher** altitude than "one turn = one band" — because Tim's *default* should not even be the turn's internals; it should be the **felt shape of the thinking**, in his words. Three nested altitudes, each a deliberate up-translation:

### B.1 · Altitude 0 — THE PULSE (default, ambient, lives WITH the conversation)
**What Tim sees by default:** not a graph at all. A **small living glyph beside the reply** (or breathing at the edge of the chat lane) — the conversation's **heartbeat of cognition**. It is the up-translated answer to "is it thinking, how hard, did it know already."

- **Designed — the glyph is a shape, not a number.** Think a **breathing iris / aperture**: it *dilates* with how much cognition this turn took (more roles fired + more injected = wider open), *brightens* on convergence (the parts resolved cleanly into the reply), goes **calm-blue** when it "already knew" (background/sense-triggered run answered before Tim finished — C5.2/C5.3, the "it already knew" feel, spine §9#1), flashes a **loud notch** if a role failed/abstained (fail-loud at altitude, rule 4). Tim reads *one glyph* and knows the character of the turn without opening anything.
- **Why an iris/aperture:** it maps the swarm to a *single continuous perceptual quantity* (openness = depth-of-thought, colour = warmth/calm, a notch = a wound). Tim recognises "that was a deep, clean, parallel turn" vs "that was shallow but something snagged" **pre-verbally**. (Exact form = `needs-tim` aesthetic; the *principle* — one continuous glyph, not a count — is the design.)
- **Reuse anchor (Observed):** this is a sibling of the existing `now` summary in `Activity.tsx:11–12` (`graph · nodes_resolved/total · awaiting`) — but rendered as **shape, not text**. The glyph subscribes to the same stream; a `cognition.turn.*` event sets its state. Where `Activity` writes "8/12 resolved", the pulse *opens to 8/12*.

### B.2 · Altitude 1 — THE RIVER (one click on the pulse: the turn as a converging flow)
**What Tim sees:** the turn as a **left-to-right (or radial-inward) river** — roles enter as **tributaries on the left**, the cascade flows rightward through its hops, and **everything converges into the BRAIN node** (the one coherent voice, spine §8) which empties into the **reply / chat lane on the right**. This is 06's "one picture" — but reframed as *flow/terrain*, not a static node diagram, because flow is what Tim reads.

- **The shape IS the information (tread-marks applied to cognition — [[feedback-render-for-cognition]]):**
  - **Worn vs faint tributary** = how much that role *contributed* (a recall that returned 8 strong hits is a wide bright channel; a role that abstained is a faint dry trace). Contribution ≈ injection `cost`/weight (spine §5, budget=attention) + whether its output was actually injected.
  - **Convergent vs branching** = did the cascade flow cleanly into the brain, or did it fan/stall? A clean turn is a tight delta; a tangled turn braids.
  - **Gaps = unaccounted** = a role that was *supposed* to fire (its trigger matched) but didn't resolve in budget → a visible **dry gap** in the riverbed (not hidden — the missing tributary is drawn as an absence). This is the cognitive analogue of the `stuck` node-state (Observed: `NodeShape.tsx:69,76` "stuck — an input never resolved").
  - **Dead-ends = broken** = a role that fired but **failed/abstained** ends in a red **silted stub** that doesn't reach the brain. Loud by sight (rule 4).
- **Density-not-count handles the cap honestly:** the river's **width/turbulence** encodes "how parallel / how much," so whether 9 or 26 roles fired, Tim reads *magnitude as shape*, never counts dots — which sidesteps the R1-FOLD "don't pin to literal 32" constraint *by design*, not by caveat.
- **Reuse anchor (Observed):** the brain + roles are tldraw shapes; the tributary wires are the `Edges` screen-space SVG overlay (`NodeShape.tsx:243–278`) — injections terminate **on the brain shape** (shape→shape, the genuine `Edges` mechanism, per 06 §C/§D). The river is `Edges` with **variable stroke-weight/opacity driven by injection `cost`** and a flow-direction animation (§D). Net-new = the weight/opacity mapping + the "dry gap" / "silted stub" treatments (Designed).

### B.3 · Altitude 2 — THE NODES (zoom in / expand a tributary: the literal swarm)
**What Tim sees:** the full role cards — exactly 06 §D's "Inspect" — effective model, JSON output, per-stage timings (`emit_run_record`, Observed `suite.py` think_ms/etc.), the config form. This is where the **30 technical nodes finally live** — *underneath two layers of up-translation*, reached only when Tim drills. Semantic zoom is already the substrate (Observed: `NodeShape.tsx:47–49` `expanded = zoom > 0.5`); expanding a river tributary = zooming that channel into its role card(s).

> **The altitude law for cognition:** Pulse (felt character) → River (converging shape) → Nodes (the literal swarm). Default = Pulse. Each click/zoom descends one level. Tim never *starts* at 32 nodes; he ends there only if he wants to. **This is the altitude-transformation layer made concrete for the swarm.**

---

## C · The shape vocabulary (what reads by sight at each altitude)

A table of the **perceptual encodings** — each is a render-rule projecting cognition-data to a shape Tim recognises without reading. (Tokens/exact look = `needs-tim`; the *mapping* is the design.)

| Cognition fact (data) | Perceptual encoding (the shape Tim reads) | Reuse / net-new |
|---|---|---|
| How much thinking this turn took | Pulse **dilation** / river **width** | net-new mapping over `cognition.turn.*` count + cost-sum |
| How parallel | river **turbulence / number of live tributaries** at peak | net-new |
| What FED the reply (the injections) | **bright worn channels** into the brain; weight = `cost` (thin=cheap, thick=loads-corpus) | `Edges` weight (06 §C) + net-new cost→weight scale |
| What was offered but didn't land | **faint / dry** tributary | net-new (the "abstained"/low-contribution treatment) |
| A role that should've fired but stalled | **dry gap** in the bed (visible absence) | analogue of `stuck` state (Observed `NODE_STATES`) |
| A role that failed/abstained | **red silted stub**, doesn't reach brain; loud | fail-loud (rule 4) + a `failed`/`abstained` render-token (06 §C node-states) |
| Convergence quality | tight **delta** (clean) vs **braid** (tangled) | net-new geometry |
| "It already knew" (background/sense run) | **calm-blue ambient ripple** with no operator turn | net-new; reads the active mode (06 §B.7, spine §2.5) |
| Speed | the **rate** the river fills (fast turn = quick flood; slow = trickle) | drives off `emit_run_record` ms (Observed) |
| Which words came from which thought | reply-part **back-lit** in the brain's colour-of-its-feeder (see §E.3) | net-new — the explanation affordance |

**Status-by-sight is already the substrate** (Observed): register a cognition node-state engine-side (`latent/firing/ran/injected/failed/abstained`) with a `render.token` and the dot paints with **zero FE edit** (`NodeShape.tsx:64,83–87`; 06 §C). So the river's per-role states inherit the proven mechanism; net-new is only the *river-scale* encodings (width/dry-gap/silt), which live on the cognition-`Edges` sibling.

---

## D · Motion as content (it animates per turn — the temporal read IS the information)

A turn is an **event over time**, and Tim reads time. Motion here is not decoration; the *trajectory* of the animation is a datum.

- **D.1 · The cascade traces.** As `cognition.role.fire → ran → inject` events arrive on the stream (06 §F emit-contract), the river **fills in real time, in dependency order**: focus→embed→recall→rerank→digest→compose→inject (spine §2#5). Tim *watches the thought happen*. A hop **brightens while firing** (06 §D), then the channel **thickens as it injects**. The shape isn't pre-drawn and revealed — it **grows the way the thought grew**. (Reuse: the SSE stream already drives live repaint per-event, Observed `useAppController.ts:366–410`; a `cognition.*` branch mirrors `decision.*` at `:390`.)
- **D.2 · Parts light as they're SPOKEN (the voice coupling, G6).** The staged reply is parts; each part is the TTS unit (landscape §1, voice coupling). When a part begins speaking, its **segment of the reply lane illuminates**, and — crucially — its **feeder tributaries pulse in sync** (the injections that fed *that part* glow as the words are voiced). So Tim *sees the sentence being spoken light up the thoughts behind it*. This is the view⟷voice unity made visual (extends §F). Net-new; depends on the part→TTS coupling (landscape §1) emitting a `cognition.part.spoken {part, feeders[]}` event. **Geometry seam (honest reuse/net-new line):** this coupling lands on the **chat lane**, which is a **DOM region (`ui://chrome/chat`), NOT a tldraw shape** — so 06 §C/§D was explicit it is **net-new geometry, not the `Edges` page-bounds mechanism**. The brain→reply illumination is a **terminal glow/cue across the DOM↔tldraw boundary** (a coordinated DOM highlight + canvas-edge pulse keyed by `into`/`part` address), not a shape-to-shape edge. A build agent must NOT under-scope this as "reuse `Edges`."
- **D.3 · The ambient "it already knew" pulse (C5.2/C5.3).** When a cascade fires with **no operator turn** (background consolidation, or a sense-trigger on a screen/app/state change), the view does NOT pop the full river — it shows a **calm ambient ripple** in the pulse glyph / at the canvas edge ("something stirred"). If it produced something Tim should see (the RHM decided to contact him — spine §2.5 outbound), the ripple **warms and reaches toward the chat lane**. Distinguishing *autonomic* cognition (calm) from *answering-you* cognition (full river) by **motion temperature** is the non-obvious move — it stops background thinking from being noise while keeping it *present*. (Open in 06 §H "background/proactive runs"; resolved here as a motion-temperature distinction.)
- **D.4 · Replay (the temporal view, [[feedback-render-for-cognition]] "watch it trace / replay").** Any past turn re-runs its animation on demand — scrub a turn and **watch the river fill again**. Reuse (Observed): the **walkthrough session organ** (`Walkthrough.tsx`, `/api/review/*`) is the proven server-authoritative step-by-step walk; a cascade-replay reuses that shape (06 §B.7/§E). The event log is durable + seq-ordered (`fs_store.append_event`, Observed 06 §B.5), so replay is just re-streaming `cognition.*` events for `run://<turn>/*` in seq order.

---

## E · The steering vocabulary (how Tim STEERS it live — genuinely new)

06 stopped at "click a role → Inspector; click config → re-bind." That is *inspection*, not *steering*. Steering = Tim **changing the cognition while it runs / for next turn**. Three verbs, each grounded in a reuse anchor, each **operator-gated** (rule: verdicts/config are operator-only, Observed `Walkthrough.tsx` operator-gated `/api/resolve`).

### E.1 · BOOST / MUTE a role = direct manipulation of attention (budget = attention, literally)
- **The gesture:** on any role tributary (River) or card (Nodes), Tim can **boost** (drag wider / a "↑" affordance) or **mute** (drag to faint / an "✕" affordance). **Boost → more working-memory/slot budget** for that role (it gets more of the swarm's reserved slots, a larger context allowance, higher injection priority). **Mute → drop it from the cast** (don't fire it; reclaim its slots for the others).
- **Why this is the RIGHT primitive:** the spine's law is **budget = attention** (§5). So the literal act of *making a tributary wider* **IS** giving that thought more attention. The shape Tim manipulates and the resource he's steering are **the same thing** — the interface collapses the metaphor and the mechanism. He's not editing a config field; he's **widening a river**.
- **Reuse anchor (Observed):** role config + binding already self-describe (`roles()`/`resolve_role()`/`knobs_for()`, 06 §B.3/§E) and the live re-bind path is `set_rhm_config`/role-binding (06 §D, Criteria G8). The boost/mute writes a per-role **slot-weight** into that same config slot. **Net-new:** the slot-scheduler must *read* a per-role weight when allocating the swarm budget (landscape §3 item 2, the VRAM-bounded slot scheduler — the make-or-break) — so boost/mute is only real if the scheduler honours weights. *(This is the load-bearing net-new dependency for steering; flagged.)*

### E.2 · CHANGE THE CAST live (the mode picks it; Tim overrides per-turn)
- **Observed/Designed:** **mode is the one dial** (landscape §1; Observed `MODES`/`MODE_DIRECTIVES`) — it selects *which* role set fires + the slot budget. So the **primary** cast-control is **picking the mode** (the existing presence dial, Observed 06 §B.7). 
- **The steering extension (Designed):** a **per-turn cast override** — Tim opens the cast (a roster of available roles from the registry, Observed `roles()` self-describe), and **toggles roles in/out for the next turn(s)** without changing the mode. "For this question, also fire the contradiction-checker." This is muting/un-muting at the *cast* grain rather than the *budget* grain. Reuse: the same config-write path as E.1; net-new = a per-turn cast scope vs the persistent mode scope.
- **The non-obvious affordance:** because the cast is **registry data** and roles self-describe their *trigger*, the view can show Tim **why each role is (or isn't) in the cast this turn** ("recall fired because your message addressed memory; screen-reader is muted because nothing changed on screen"). The cast roster is *explained*, not just listed (up-translation of the trigger logic).

### E.3 · "WHY did this part say that" = the injections ARE the explanation
- **The gesture:** Tim clicks a **part of the reply** (a sentence/beat in the chat lane) → the view **back-lights the tributaries that fed it**: the injection edges that resolved into *that part's* context light up, and the source role cards surface their contributed slice. He literally **sees which thoughts produced those words**.
- **Why this is the deepest affordance:** the explanation is not a *generated* "here's why I said that" (which could confabulate) — it is the **actual addressed data that was injected** (06 §F: `cognition.inject {turn, source, cost, chars, into}` carries the locus). The injection edges, drawn from real resolved-context events, **constitute** the explanation. The view doesn't *explain* the reply; it *shows the reply's provenance*. (Net-new: the part↔feeder mapping must be carried on the `cognition.part.*` / `cognition.inject` events' `into` field — landscape §1 + 06 §F emit-contract.)
- **Reuse anchor (Observed):** click-to-inspect a role's full JSON + config is the Inspector (`Inspector.tsx`, 06 §B.7/§E); this extends it from "inspect a node" to "inspect a *word's lineage*."

### E.4 · Steering altitudes (the gestures up-translate too)
Tim steers at **whatever altitude he's at**: at the Pulse he can only set the *mode* (coarse, "think harder / stay calm"); at the River he boosts/mutes *tributaries*; at the Nodes he edits a role's *config*. The **down-translation** (CLAUDE/[[feedback-altitude-transformation-layer]]) turns each altitude's gesture into the technical record-edit it implies — "make this thought wider" → a slot-weight write; "stay calm" → a mode set. He expresses the *want* at his level; the interface builds the mechanism.

---

## F · The RHM reads its OWN cognition — as an INTERACTION, not a second screen

06 noted (§D) that the RHM can read `ui://cognition/<turn>` because it's addressed data. This doc makes that an **interaction**, which is the non-obvious payoff:

- **The act:** Tim says aloud — *"why did you say that?"* / *"what were you thinking on that last turn?"* — and the RHM **does two things at once from ONE substrate**: it **speaks** the answer (resolving `ui://cognition/<turn>` like any context, the `_chat_context` path, Observed 06 §D) **AND lights the frame** (the river for that turn animates, the feeder tributaries for the part-in-question back-light per §E.3). **View and voice are one act.** He hears it *and sees it* explain itself, pointing at its own thoughts.
- **Why it's one substrate, not two:** the thought-graph is the same addressed `run://<turn>/<role>` data the RHM resolves to *answer*. So "render it for Tim" and "the RHM reads it to explain itself" are the **same read** projected two ways (voice + canvas) — exactly rule 3 (one source), and exactly the view⟷voice unity D.2 builds toward. There is no separate "explainability module"; self-reading is the **same machinery** as ordinary context resolution. (Same geometry caveat as D.2: the "light the frame" part lands on tldraw shapes via `Edges`; any highlight on the chat-lane part is the DOM↔tldraw cross-boundary cue, not `Edges`.)
- **The reciprocal — the RHM narrates its OWN steering:** when Tim boosts/mutes (§E), the RHM can confirm in voice *and* the river reshapes — "I'll give memory more room next time" + the tributary widens. The steering gesture, the spoken confirmation, and the shape change are **one event** down the stream.
- **Net-new:** a `cognition.explain {turn, part?}` resolve that returns BOTH a spoken summary (up-translated) and the `run://<turn>/*` frame address, so a voice question and a canvas-light are one round-trip. Depends on the `cognition.*` emit-contract (06 §F) + the part↔feeder mapping (§E.3).

---

## G · How this extends G7 (the criteria, concretely)

G7 today: *C7.1 per-turn thought-graph renders (roles/chains/injections), `cognition.*` SSE, reflects-never-owns; C7.2 RHM reads its own cognition via `ui://cognition/<turn>`.* This doc adds the **UX layer that makes G7 pass the FORM bar (CF.1: navigable-not-text, legible on 390px mobile, design-critic graded)**:

- **C7.1 is not done as 30 cards.** It is done as **Pulse → River → Nodes** (§B). Proposed criteria extension: *the per-turn cognition reads as a glanceable shape at the default altitude (no count to parse); drill-down reaches the literal role nodes.* (by use + design-rubric/needs-tim)
- **C7.2 becomes an interaction** (§F): *Tim asks "why did you say that" → the RHM speaks AND the frame lights from one `run://<turn>` read.* (by use)
- **New C7.3 (steering, Designed):** *Tim can boost/mute a role and change the cast live (operator-gated); the slot-scheduler honours the weight; the river reshapes.* — this is the one with a **hard backend dependency** (the weighted slot-scheduler, landscape §3#2). (by use)
- **Mobile (CF.1):** the Pulse glyph is *built for 390px* — a shape needs no width to read; the River collapses to a vertical converging flow; the Nodes are the existing semantic-zoom cards. Shape-first survives small screens where 30 cards never could.

---

## H · Open forks — decide WITH Tim

1. **The Pulse glyph form.** Iris/aperture (continuous openness) vs a small constellation vs a waveform vs a single warming dot? (All shape-not-count; the *which* is `needs-tim` aesthetic — but it sets the whole default-altitude feel.)
2. **River direction.** Left-to-right flow into the chat lane (reads like reading), or **radial** (roles orbit the brain, inject inward — more "cognition," less "pipeline")? Radial may map "the swarm surrounds the one voice" (spine §8) better; L-to-R maps "flow into the words" better.
3. **Does the River live ON the conversation or on its own board?** (06 §H "own surface vs overlay" — but here re-asked at *each altitude*: Pulse lives WITH chat for sure; does the River overlay the chat lane, or is it a board you flick to?) Lean: Pulse with chat, River as an expand-in-place panel, Nodes as the full canvas.
4. **Boost/mute persistence.** Does a boost last one turn, the session, or become a learned preference the presentation-layer remembers ([[feedback-altitude-transformation-layer]] "HOW it presents is LEARNED")? Could feed the predictive layer — the system learns Tim *always* boosts contradiction-checking on strategy questions and pre-widens it.
5. **The cast-override grain.** Per-turn only, or "for this topic/activity" (tie to mode/activity-context, G5)?
6. **"Already knew" loudness.** How present should background cognition be — a calm edge-ripple (lean), or does Tim want to see the autonomic river too (a faint always-on terrain)? Risk: ambient cognition becoming wallpaper noise.
7. **Faculty vs role node kinds** (carried from 06 §H). At the River altitude, do faculties (recall/selection/trajectory/model_of_tim) and roles (judge/brevity/…) draw as visually distinct tributary *kinds* (sense-fed vs reasoning), or one channel kind? The 5-layer spine (conscious/pre-conscious/subconscious/senses/world) could map to **river depth-bands**.
8. **Address scheme** (carried, CONFIRM-level): `run://<turn>/<role>` reuse (lean, no new contract) vs mint `cog://` (rule-8 contract-widening — confirm before).
9. **Steering's hard dependency:** boost/mute is only real if the **weighted slot-scheduler** (landscape §3#2) reads per-role weights. Confirm this is in-scope for the first build, else E.1 is `needs-backend` and the first cut ships mute-only (drop-from-cast, which the cast-toggle already gives) without graded boost.

---

## I · Sources
- **This series:** [[06-rendering.md]] (the reuse spine + data-model→render-rules + the static view this doc animates), `00-LANDSCAPE.md` (architecture §1, net-new §3, forks §5), `Concurrent Cognition — Completion Criteria.md` (G7, CF.1, the R1-FOLD constraints: `run://` not `swarm://`, sub-32 cap, aesthetics=needs-tim).
- **Code read (Observed), this session:** `canvas/app/src/useAppController.ts:363–415` (SSE `openStream`/dispatch-by-kind/`decision.*` branch — the cognition branch's pattern), `NodeShape.tsx:30–184` (the generic shape, ports/status-by-sight from registry, `Edges` screen-space overlay :243–278, semantic-zoom :47–49), `regions/Activity.tsx` (the `now` summary the Pulse up-translates), `regions/Inspector.tsx` (the inspect/config/force path §E.3 extends).
- **Principles:** [[feedback-render-for-cognition]] ("his brain is the algorithm"; tread-marks: worn/faint, convergent/branching, gaps=unaccounted, dead-ends=broken — applied to the river §B.2/§C), [[feedback-altitude-transformation-layer]] (two-way translation; default-translated-up; drill-down on demand; presentation learned — the three-altitude spine §B + steering down-translation §E.4), [[project-collective-cognition]] (budget=attention §E.1; the 5 layers §H#7; commander's bridge), [[project-company-one-entity]] (the one coherent voice = the brain node).
- **Governing rules:** AGENTS.md rule 3 (one source — §F), rule 4 (fail loud — §C dead-ends/dry-gaps), rule 9 (navigable visual surface not a text wall — the whole doc; FORM is half of done; design-critic + design-lint gated → aesthetics `needs-tim`).
