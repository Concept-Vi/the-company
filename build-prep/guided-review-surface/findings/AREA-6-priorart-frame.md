# AREA 6 — Prior Art (external) + the Bigger Frame (internal)

> Research-wave finding for the Live, Guided, Right-Hand-Man Review Surface.
> Two halves: **(a)** how real tools do the things this surface needs — so we build on known
> patterns, not from scratch; **(b)** whether the studio is just the FIRST instance of a
> guided-RHM surface that generalizes to ANY part of the Company.
>
> Evidence tags used throughout: **Observed (file:line)** · **Inferred** · **External-prior-art (URL)**
> · **External-prior-art (marketing-claim)** = a vendor's own page, NOT independently verified ·
> **Anchor-idea** = from ANCHOR.md, repeated for grounding.

---

## TL;DR — the one finding that matters

The surface decomposes into a **mechanism layer** and an **intelligence layer**, and the split IS
the finding:

- **The mechanism is a solved, commodity problem.** Spotlight + attach-to-element + next/back/dwell
  is shipped by four mature open-source libraries (Driver.js, Intro.js, Shepherd.js, Reactour). We
  steal the *mechanism* (and its well-documented pitfalls), never build it from scratch.
- **The intelligence is unsolved end-to-end by anyone.** "AI composes the sequence live, narrates
  each stop at YOUR altitude, follows your cross-time deixis ('this from here after that opened'),
  marks up as you talk, and turns it into build-requests" — **no shipping product does the whole
  thing.** The closest confirmed precedent is **Microsoft Copilot Vision** (voice responses + visual
  highlights to guide). Figma's "AI design review" is **async batch** (select → ask → get insights),
  NOT live narrate-each-stop.
- **The deep crux — comprehension-at-altitude — is where external prior art and the internal gap
  CONVERGE.** A VLM can describe *pixels*; it cannot explain *intent/affordances* for a mockup whose
  semantics the system never registered. That is the EXACT root of the original failure ("I had no
  idea what the hell I was looking at", ANCHOR §1) and the exact internal limit (`address_help` only
  returns what's registered, ANCHOR §6). External and internal hit the same wall. **This is the
  make-or-break, not the consent model, not the sequencer.**
- **Internal frame: designed-general, built-partial, live-join-unproven.** The vault is unambiguous —
  this was designed as THE one human-interaction organ (build-review is its *first* consumer, not its
  purpose). But the RHM Deep Scan is equally unambiguous that the live conversational seam is "the
  single biggest unverified surface", most modes are inert prompt-strings, and the up-translation
  organ (`coa`) may not even be wired to the FE. So the honest status is: the GENERAL faculty is
  *designed*; the *live join* that makes it real is *unproven* — the same wall the prior art hits.

---

# PART A — EXTERNAL PRIOR ART

## A0 · The framing: mechanism vs intelligence (why nobody ships the whole thing)

Pull the surface apart along one axis — **who authored the sequence and the narration?**

| Layer | What it is | Who solved it | What to steal |
|---|---|---|---|
| **Mechanism** | spotlight an element · step next/back · dwell · attach a tooltip/card · survive route changes | **Fully solved** (4 OSS libs) | the spotlight + step engine + the SPA-reliability discipline |
| **Live composition** | AI builds the sequence on the fly for a thing it wasn't pre-scripted for | **~nobody, end-to-end** | — (this is net-new everywhere) |
| **Narration-at-altitude** | tells YOU what this is, at YOUR level, because you don't know | **Partial** (Copilot Vision describes; nobody explains *intent* for un-registered UI) | the voice+highlight loop shape (Copilot Vision) |
| **Cross-time deixis** | follows "this / here / that-before-this" live | **Research-stage, not productized** (Bolt 1980 → 2026 HCI papers) | the disambiguation model (proximity semantics) |
| **Markup-as-you-talk** | comments/tags accrue on elements as you speak | **Partial** (Figma comments are manual; AnnotateAI turns voice→stickies) | the address-anchored comment as a first-class object |
| **Generate→dispatch** | turn the talked-through session into build-requests | **Not in design tools** (Figma/Make do design→code, not review→build-intent) | — (the Company's own wire) |

**The synthesis:** every product owns ONE or TWO of these rows. The Company surface needs **all
six, fused, live.** The reason "nobody built it" (ANCHOR §intro) is real — it's not that it's
impossible, it's that the *fusion* (live composition + altitude narration + deixis, over one shared
addressed surface) is genuinely novel. The novelty is in the seams, not the parts.

---

## A1 · Guided product tours / interactive walkthroughs — the MECHANISM (fully solved)

**External-prior-art (URL):**
- `https://inlinemanual.com/blog/driverjs-vs-introjs-vs-shepherdjs-vs-reactour/` (2026 comparison)
- `https://userorbit.com/blog/best-open-source-product-tour-libraries` (2026)
- `https://github.com/kamranahmedse/driver.js` · Hacker News `id=36846520`

**The four canonical libraries (CONFIRMED via the comparison article):**

| Library | License | Note |
|---|---|---|
| **Driver.js** | permissive (MIT-style) | lightweight, vanilla JS, "move the user's focus around a webpage"; spotlight is its signature |
| **Reactour** | permissive | React-native tour |
| **Intro.js** | **AGPL** unless commercial license bought | the original feature-tour lib |
| **Shepherd.js** | **AGPL** unless commercial license | richer step/UI control |

**The next/back/dwell pattern, confirmed:** these libs ARE the "drives the view to a stop, NEXT /
BACK, dwell" mechanic (ANCHOR §2). A tour = an ordered list of steps; each step = `{ selector,
text, position }`; the engine spotlights the element, shows a card, and Next/Back/Skip step the
list. This is **exactly** the studio's needed step-engine — and it's a commodity.

**The known-hard parts (CONFIRMED — these are the implementation pitfalls the article calls out):**
1. **Selector reliability** — "the step attaches to the right UI element *every time* (even after UI
   changes)." A tour breaks when the DOM moves. → **Maps directly onto why the Company uses `ui://`
   addresses + a UI-component registry (ANCHOR §5, Observed `data-ui-ref`→`addresses.json`): a
   stable address survives DOM churn where a CSS selector does not.** This is the Company's existing
   design *solving the #1 documented tour-library failure mode.* Strong reuse-validation.
2. **SPA-friendliness** — "steps survive route changes and async rendering." The studio's stops live
   in a single-page canvas that mutates live → this pitfall is in-scope.
3. **z-index wars** — the spotlight overlay fighting app chrome. The Company's portal/present-in-place
   (ANCHOR §5, Observed `portalSelected` App.tsx:657-665) is the canvas-native answer; DOM overlay is
   the named fallback (matches the vault's R1 correction).
4. **Measurement** — completion rate, drop-off step. Less relevant for a single-commander surface,
   but the *resumable cursor* (server-authoritative session, vault B4) is the analogue.

**What to steal vs leave:** steal the **step+spotlight mechanic** and the **selector-reliability
discipline** (which the `ui://` registry already answers better than a selector). **Do NOT** adopt
a tour library wholesale — they are *authored-in-advance, zero-AI, non-conversational*. The studio's
sequence is **AI-composed live** and **two-way** (you talk, it talks back). A tour lib is the dumb
substrate; the RHM is the intelligence the libs deliberately don't have.

---

## A2 · Live conversational design-review + AI design assistants

**External-prior-art (marketing-claim — Figma's own solutions page, NOT independently verified):**
- `https://www.figma.com/solutions/ai-design-review-assistant/`

What Figma's page *claims* the interaction shape is (described, not verified by use):
> "Step 1: Select a frame or flow · Step 2: Ask for targeted feedback · Step 3: Review insights
> and recommendations · Step 4: Iterate and refine." "Scan frames, flows, and components in
> seconds… flags visual and structural mismatches." "Validate UX decisions… surface usability
> risks." "Ask for critique… without switching tools."

**The critical distinction (do not let this blur):** this is **async, batch, system-initiated
critique** — you select, you ask, it returns a list of insights. It is **NOT** a *live, paced,
narrate-each-stop walkthrough that the assistant LEADS while you set the pace and point deictically.*
Figma's AI reviews the design *for* you (a critic); the Company's RHM walks you *through* the design
*with* you (a guide, at your altitude, because you don't know what you're looking at). **Different
interaction shape, different user model.** Figma assumes a designer who already understands frames;
the Company's commander explicitly does not (ANCHOR §1). Steal the idea that *an AI can hold a
view in context and talk about it*; reject the assumption that the user can drive.

**External-prior-art (marketing-claim — Figma community plugin page):**
- `https://www.figma.com/community/plugin/1611550338941766411/annotateai-voice-typed-design-notes`
> "AnnotateAI helps designers turn feedback, documentation and handoff notes into structured assets
> directly on the Figma canvas. Create annotations, stickies, section headers, links and checklists
> that live alongside your designs."

This is the closest external echo of **"mark-up accrues as you talk"** (ANCHOR §2): **voice/typed →
structured annotations anchored to the canvas.** CONFIRMED-as-described that voice-driven annotation
onto a design surface is a shipping pattern. But it is *capture*, not *conversation* — it doesn't
talk back, doesn't follow deixis, doesn't compose a build-request. Steal the **annotation-as-a-
first-class-object-anchored-to-an-address** shape (the Company's `annotate`/`annotations_at` at a
`ui://`, Observed in ANCHOR §7, is the same primitive done better — addressed, not coordinate-pinned).

**External-prior-art (URL — secondary, community discussion):**
- `https://www.facebook.com/groups/.../` — "Figma's comment system… Designers can leave comments
  directly on a specific element." Confirms the *baseline* expectation: review tools attach comments
  to specific elements. The Company generalizes "element" to "any `ui://` address incl. groups."

**Honest gap:** I found **no shipping product** that does *live conversational design-review where
the AI leads a paced walkthrough and the human points deictically across time.* The pieces exist
(Figma critique; AnnotateAI capture; tour-lib pacing) — the **fusion does not.** This is consistent
with the anchor's claim that the live guided experience is the hard, unbuilt part.

---

## A3 · Voice-driven UI / live agents / "explain this screen" — the strongest confirmed precedent

**External-prior-art (URL — Microsoft official):**
- `https://support.microsoft.com/en-us/accessibility/copilot/basic-tasks-using-a-screen-reader-with-copilot-vision`
- `https://primer.style/accessibility/patterns/copilot-accessibility-practices/`

**CONFIRMED (Microsoft's own accessibility docs, quoted):**
> "Copilot Vision lets you use your voice to interact with content in apps and browser windows.
> Copilot Vision uses **voice responses and visual highlights to guide**…"

**This is the single strongest real precedent for the core loop** (ANCHOR §2): a live agent that
(a) sees the shared screen, (b) responds by **voice**, and (c) **highlights the thing on screen**
to direct your attention. That is *narrate + spotlight, voice-first, on a live surface* — the
studio's RHM loop, shipped, by a major vendor. **Name it as the proof the loop is buildable.**

**But mark the limit precisely (Inferred, from what Copilot Vision is):** Copilot Vision works by
**VLM over pixels** — it describes what it *sees*. It does NOT have a registered model of *what each
element is FOR* (its intent/affordance), because it operates over arbitrary third-party apps it has
no schema for. So it can say "there's a blue button here" but not "this is the model-picker; changing
it re-routes every node's compute." **The altitude-narration the commander needs — what this IS and
what you can DO here — requires registered semantics Copilot Vision structurally lacks.** (See A4.)

**Secondary confirmed shape:** the Copilot accessibility *practices* page documents the inverse —
making an AI surface itself navigable by screen-reader (announce regions, move focus, explore
settings). Relevant because the Company surface must ALSO be legible to a non-developer; the
"announce where you are + what's here" discipline is the same one the RHM needs for altitude.

---

## A4 · The deixis problem — old, deep, and NOT productized (the academic anchor)

**External-prior-art (URL — peer-reviewed / arXiv):**
- `https://arxiv.org/pdf/2605.02261` — *From 'Here' to 'There': Exploring Proximity Semantics in
  Multimodal Data Exploration* (Bromley, Wang, Setlur — Tableau Research, 2026)
- `https://dl.acm.org/doi/10.1145/3772318.3790938` (same paper, ACM)
- `https://www.researchgate.net/publication/2474859_Automatic_Referent_Resolution_of_Deictic_and_Anaphoric_Expressions`

**The canonical anchor — Bolt's "Put-That-There" (MIT, 1980)** *(title from prior knowledge; the
paper snippet only says "Bolt's 1980 system" — but this is the canonical Bolt MIT reference)*. The
Tableau paper cites it directly:
> "The indicator 'this' is a common example of **spatial deixis**, a linguistic feature that refers
> to a place relative to the use context. **Bolt's 1980 system** [first combined pointing + speech]…"

**Why this matters for the anchor:** ANCHOR §6 calls "live conversational grounding under deixis"
the honest hard part ("THIS from HERE after that thing that opened before THIS showed up"). The
prior art says: **pointing + speaking to resolve "this/here" is a 45-year-old research problem, not
a novel one — and it is STILL research-stage, not a shipped, robust capability.** That is a
sobering, honest signal: the deixis the anchor wants is *achievable in principle* (decades of work)
but *not a solved component you can drop in.*

**The usable model the 2026 paper gives us — "Proximity Semantics" (PS):** CONFIRMED finding:
> "participants relied on their **relative placement** to disambiguate meaning… meaning is shaped by
> the **closeness of multimodal elements** within a shared interaction space… participants frequently
> combined proximity with **explicit marks: arrows were commonly used.**"

And from the related AgentHands work in the same result set:
> "When it said here/this, the point should **land right then**" — i.e. **deixis is TEMPORAL** —
> the referent is whatever was focal *at the moment of utterance.*

**Translation to the Company's machinery (Inferred, mapping the paper onto Observed primitives):**
- "this/here" resolves against the **current locus** (Observed `current_locus`, `_resolve_context_at`,
  ANCHOR §7) — the spatially-/temporally-closest focal address.
- "that thing that opened *before* this" resolves against the **event log ordering** (Observed
  `events_since(seq)`) — the temporal trail of what became focal when.
- The paper's "explicit marks (arrows)" → the Company's **annotations at addresses** as the durable
  anchor when proximity alone is ambiguous.
- **So the Company already has the three substrates the research says you need** (current focal
  address + temporal event order + explicit address-anchored marks). The research validates the
  *shape* of the existing primitives. What's unproven is whether the **resident model**, given that
  field, actually resolves the reference correctly live (see B-half / RHM Deep Scan: the live join is
  the unverified surface). **The substrate exists; the live resolution is the open question — exactly
  what ANCHOR §6 flags.**

**Steal:** proximity-semantics + temporal-binding as the *grounding model* the RHM uses to resolve
deixis from `current_locus` + the event trail. **Don't assume:** that a resident model does this
robustly out of the box — the research's 45-year arc says it's hard, and the Company's own tests
defer the live conversational seam to "by use" (RHM Deep Scan, Observed).

---

## A5 · Onboarding-copilot / "explain to a non-expert" patterns

**External-prior-art (URL):** the Copilot Vision + Copilot Studio screen-reader docs (A3) double as
the onboarding-copilot precedent — "open X, move through the homepage, navigate between areas, explore
settings." Also the broad **GenAI copilot** pattern (HR copilot, coding copilots like Codex's "explain
this function") confirms the commodity verb **"explain this"** is everywhere.

**The honest read:** "explain this code/function" is ubiquitous and works *because code has registered
structure* (the AST, the symbol, the docstring). "Explain this *screen element to a non-developer at
his altitude*" is **much rarer and weaker**, because (a) the element's *intent* is usually not
registered anywhere, and (b) "at his altitude" requires a model of *who he is and what he already
knows* — the up-translation problem. This is the seam to A4's deixis and the bridge to the internal
crux (next section).

---

## A6 · The convergence crux — comprehension-at-altitude (centerpiece)

**This is the highest-value synthesis. External prior art and the internal gap hit the SAME wall.**

- **Externally:** Copilot Vision (A3) proves the *loop* (voice + highlight on a live screen) but is
  limited to *describing pixels* — it has no registered model of intent/affordance, so it can't
  explain *what a thing is FOR* or *what you can do here* for a UI it has no schema for. Figma's AI
  (A2) explains designs *to a designer who already understands frames* — it does not solve "the user
  doesn't know what he's looking at."
- **Internally (Observed, ANCHOR §6 + RHM Deep Scan):** `address_help` returns `what_this_is /
  how_to_change / how_to_use` **only for what is registered.** For a **redesign mockup** — a proposed
  surface that doesn't exist yet and has no registered semantics — there is *nothing to explain from*,
  so the RHM **confabulates** (and the grounding is prompt-enforced, not code-enforced: RHM Deep Scan
  Part 4 #2, "nothing structurally prevents confabulation").

**Both failures are the same failure:** *the explainer has no grounded model of intent for an
un-registered artifact, so it either describes-pixels-shallowly or invents.* And **this is precisely
the root of the original studio failure** (ANCHOR §1: "I had no idea what the hell I was looking at…
the interface just expected me to open every mockup and somehow know what the hell it was"). The
gallery dumped un-narrated, un-registered mockups; the RHM, asked to narrate them, has the same hole
the mockups had.

**The implication for the build (within this area's scope — not prescribing the build):** the
make-or-break is not the sequencer (commodity, A1), not the consent model (DEAD SIMPLE per ANCHOR
§3 — do not re-complicate), and not even the voice loop (precedented, A3). **It is: does the RHM
actually KNOW what each stop IS, well enough to explain it at altitude without confabulating —
especially for redesign mockups with no registered semantics?** Where the answer is "no", the
options the prior art suggests are: (a) **register the mockup's intent at author-time** (the mockup
arrives *annotated with what each surface is for* — context-13's "agent documents as it composes",
literate-programming precedent); (b) **VLM-describe + flag-as-inferred** (honest "this looks like X,
I haven't verified" rather than confident confabulation); (c) **abstain loudly** ("I don't have a
registered description of this — here's the raw spec"). The anchor's no-silent-failure law points at
(b)/(c) as the floor; (a) is the real fix and is already a designed Company principle.

---

# PART B — THE INTERNAL FRAME (the bigger picture)

## B1 · Was the surface designed as a GENERAL faculty? — YES, unambiguously (3 independent sources)

The studio/review surface is **not** a mockup-review tool that might later generalize. It was
**designed from the start as THE single human-interaction organ of the whole Company**, with
build-review as merely its *first consumer*. Three independent vault sources, all Observed:

**Source 1 — RHM Walkthrough Organ — Completion Criteria (Observed):**
> "The right-hand-man is **the one organ through which Tim and the system meet.**… the system
> surfaces *anything that needs Tim* (build-review items, decisions, verifications, ideas)… So it is
> built **general**, not as build-review's UI. **Build-review is its first consumer**; the
> project→product pipeline's stages are future consumers."

And Tim's own bar (quoted in that doc):
> "It was designed to be able to **interact with any part of the UI** so that it could present
> things to me and show things to me."

**Source 2 — RHM Walkthrough Organ — Architecture-session reply (Observed):**
> "**Build it as the single human-interaction primitive**, not 'build-review's UI.' *Every* part of
> the system that ever needs Tim surfaces through this one organ."
> "the whole system is one fractal loop — `resolve → present → persist → next` — running at every
> scale, and the human loop and the machine loop are the **same loop**… This organ is that loop made
> operable for the human side."

**Source 3 — Collective Cognition + context-13 (Observed):**
> (context-13) "everything is **addressed**, and the same address can be rendered at any granularity.
> A portal, a full-screen workshop, a search-result card are the *same artefact, many faces*."
> (Collective Cognition) "**looking = an address** → the substrate relations auto-resolve → the
> result cascades up and down through cognitive layers → arrives, already-processed, in conscious
> awareness." The guided-review locus-resolution is **one instance of** this general looking→resolve
> mechanic — it generalizes to ANY locus, not just mockups.

**Conclusion (B1):** the answer to ANCHOR §8's open what-if — *"is the studio just the FIRST instance
of a guided-RHM surface that works for ANY part of the Company?"* — is a **documented, designed YES.**
The studio is the first *consumer* of a general organ. The relational primitive is **one organ →
many surfaces**: the same `surface → present → respond → act` circuit, pointed at review-items today,
pointed at decisions / verifications / ideas / the project→product pipeline tomorrow.

## B2 · How the guided-review surface relates to the broader operable/cognition surfaces (one organ, many surfaces)

The Company has several named surfaces in the vault. They are **not parallel apps** — they are
**view-modes / consumers of one substrate** (Tim's explicit "one substrate, per-type view-modes",
Observed in Collective Cognition §7: "do **not** build a separate 'model command center'… the
console/registry **generalizes over types**… view-modes of one substrate"). Mapping them:

```
                         THE ONE ORGAN (RHM) over THE ONE SUBSTRATE (addresses + context + governance)
                                                    │
        ┌───────────────────────┬───────────────────┼───────────────────┬──────────────────────┐
        ▼                       ▼                   ▼                   ▼                      ▼
 OPERABLE COMPOSITION     INTERACTIVE ADDRESSED   GUIDED REVIEW       COLLECTIVE COGNITION    DECISION→IMPL
 SURFACE                  SURFACE                 SURFACE (this)      (the resolution spine)  WIRE
 configure/run/rerun      ui:// on every element  RHM LEADS a paced   looking=address→        generate→approve→
 chains; live SSE;        + click INDICATES       walkthrough,        auto-resolve→cascade    dispatch claude -p
 act-on-outputs           +CONSENTS; annotate;    narrates at         up into awareness       → git (revert
 (the workbench)          context auto-resolves    altitude; deixis;   (HOW the RHM perceives  if breaks)
                          at a locus (R1/R2)       mark-up; generate   each locus)             (the ACT half)
        └───────────────────────┴───────────────────┴───────────────────┴──────────────────────┘
              shared: ui:// addresses · the UI-component registry · annotate/annotations_at ·
              attach_chat/chats_at · address_help · up_translate · current_locus · the governance
              POLICY · the resolve→event substrate · the dispatch wire
```

**The relationship, stated relationally:**
- **The Interactive Addressed Surface** is the *substrate layer* — it makes every element addressable,
  pointable, annotatable, and context-resolving (R1/R2). It is the **floor** the guided surface
  stands on. (Observed: the Interactive Addressed Surface Completion Criteria defines S0–S5, I1–I7,
  R1/R2 — exactly the `ui://` + annotate + locus + context machinery the guided surface consumes.)
- **The Operable Composition Surface** is the *workbench* — configure/run/act on nodes. It's the
  *content* the commander often reviews *through* the guided surface. (Operable = where work is done;
  Guided = where the commander is led through work he didn't do.)
- **Collective Cognition** is *how the RHM perceives* each locus — looking=address→auto-resolve. The
  guided surface's "context auto-resolves at each stop so the RHM always knows where you are"
  (ANCHOR §2) **is** the cognition spine applied to the walkthrough's cursor. They are the same
  mechanic; the guided surface is the cognition spine made *paced and narrated for the human.*
- **The Decision→Implementation Wire** is the ACT half — the guided surface's "generate → approve →
  dispatch → git" (ANCHOR §3) **is** this wire, triggered from a reviewed session. (Observed: the
  wire exists end-to-end, `surface_intent_at`→`dispatch_decision`→`claude -p`→git; ANCHOR §5/§7.)

**So the guided-review surface is the human-facing FACE that composes the other surfaces:** it
*leads* the commander across the operable workbench and the addressed substrate, *perceives* each
stop via the cognition spine, *records* his responses, and *acts* via the wire. It is not a peer
app — it is **the organ that makes the others legible and operable to a non-developer.** This is the
Commander's-bridge principle (context-05) made into one surface.

### B2.1 · The code-side confirmation — the "Sequences Primitive" + the ~17-surface map (Observed, on main)

The on-main `build-prep/claude-design/` pack — the deep-reads written *about this exact surface* —
confirms B1/B2 from the code side and names the general primitive precisely. **Observed:**

- **APPLICATION-STRUCTURE-PACK.md:504-541 names "The Sequences Primitive — the one relational loop":**
  *"The Sequences primitive is one relational loop — `resolve → present/work → persist → next/trigger`
  — that the Company runs at every scale, pointed at different content. It is not a feature; it is the
  **mechanic**. A new capability is a new station on the loop, not a new pipeline."* It cites three
  recurring instances of the SAME loop — **the engine** (graph nodes), **the walkthrough/review organ**
  (review-items = nodes, cursor = operator-paced readiness, Next = fire), and **the collective
  cognition** (the context cascade). This is the relational primitive the whole Company composes from,
  and the guided surface is one expression of it.
- **APPLICATION-STRUCTURE-PACK.md:556-586 lays out ~17 surfaces** that *all* "compose the same
  primitives… carry `ui://` addresses, thread the RHM, and run on the Sequences primitive" — including
  Mockup Studio (2.1), Information Architecture (2.2, "the parent that places every other surface"),
  Canvas (2.3), Portals (2.4), Walkthrough (2.7), Inbox (2.10), Build Review (2.11), Replay (2.12), the
  Wire (2.13). **This is the literal "one organ, many surfaces" map** — and it confirms the studio is
  ONE consumer (§2.1), the Walkthrough is its own surface (§2.7), and the IA surface (§2.2) is the
  container that threads one locus across board + inspector + RHM pane simultaneously.
- **The walkthrough's built/net-new cut, Observed (STRUCTURE-PACK §2.7):** "BUILT-forward-drive
  (`present_current` / `resolveUiTarget`); **net-new: sequencer/pacing, element-level show, reverse
  journey (L9)**." So the RHM-drives-the-camera half exists; the *paced sequencer* and *element-level*
  pointing the anchor's guided experience needs are the net-new. This matches A1 (the step engine is
  the missing pacing layer) and is the precise code-side gap.
- **The studio is now real on main, not a detached mockup (Observed, CONVERGENCE-WALKTHROUGH.md):**
  the standalone HTML gallery (the one that FAILED the commander) is *superseded* by a real in-app
  `Review.tsx` surface — `[ Rail | Stage | RhmPanel(+Composer) ]`, gallery from `/api/corpus`, the
  RhmPanel IS the real RHM organ chatting at the pointed `mockup://`/`ui://` locus and "reads the
  mockup's content FOR Tim", comments → `/api/annotate` into the shared address-keyed store. **Verified
  by use, both widths (1440 + 390), 6/6** — but **deliberately UNSTYLED** (neutral `--studio-*`
  token-slots) and with **5 net-new binds still open**: R2 `/api/context?address=`, per-address tier
  data (I4), persistent server-side locus (R1), auto comment→build-intent promotion (L1), and
  **in-frame element deixis**. *So the studio ROOM exists and is real; the guided RHM + the deixis +
  the auto-resolution are the documented remaining work — exactly the anchor's framing, confirmed in
  code.*

## B3 · The honest contradiction the anchor asked for — designed-general, built-partial, live-unproven

The anchor (§intro) says: *"only half-built — the current studio is a detached scaffold that FAILED
its user."* Grounding that honestly against the RHM Deep Scan (Observed, 2026-06-06, the most
non-optimistic source):

- **The general organ is DESIGNED, not BUILT-general.** The Walkthrough-as-graph, the operator-paced
  go-gate, the `ui://`-aware `show` keystone, branching, the derived-from autonomy gate — all are
  ☐ not-started in the Completion Criteria (Observed: the inventory tables are nearly all ☐). The
  *general faculty* lives in the design docs; the *code* is build-review-shaped scaffold.
- **The live conversational seam is the single biggest unverified surface** (RHM Deep Scan Part 4 #1,
  Observed): "a real model, given the real context, emits a shape the parser catches and the
  dispatcher routes correctly, and the operator sees the right thing — has **only** the 'by use in
  browser' claim behind it… that browser proof may never have happened." **This is the same wall the
  external prior art hits (A4 deixis, A6 comprehension): the substrate is real, the live join is
  unproven.**
- **Most modes are inert** (RHM Deep Scan, Observed): 3 of 8 have real backend behaviour;
  `walkthrough`-the-mode is "directive-prose only" — *"there is no stepping engine."* The
  walkthrough *organ* (`Walkthrough.tsx`, `reviewStart`) exists as a separate subsystem but is itself
  substrate-tested-only, not proven-by-use.
- **`coa` — the up-translation organ, the literal "explain at your altitude" engine — may not even be
  FE-wired** (RHM Deep Scan Part 4 #7, Observed): "the backend method exists; it is **not** in the 94
  acceptance suites and I could not trace a FE caller for /api/coa. Likely **declared-not-wired-to-
  surface.**" Since altitude-narration is the *crux* (A6), an unwired `coa` is a high-value gap.
- **`address_help` only explains what's registered** (ANCHOR §6, Observed) — the redesign-mockup
  confabulation hole (A6) is real and unaddressed.

**The honest finding, stated plainly:** the surface was **designed as a general faculty** (B1/B2 —
solid, three sources), but it is **built as a partial, build-review-shaped scaffold**, and the **one
join that makes it a live guided organ — model + real context → correct narration + correct deixis
resolution + correct dispatch, perceived by the commander — is unproven.** This is not a reason to
re-scope smaller; it is the precise locus where the build's verification effort must concentrate.
And it converges exactly with the external finding: **the mechanism is cheap and known; the live
intelligence at altitude is where the work and the risk are.**

## B4 · Contradicting the anchor where it's naive

- **ANCHOR §4 anchor-idea: "the RHM talks back = the existing chat organ run at the current locus,
  but streamed + live + voice-capable."** *Partly naive.* The chat organ is **request/response and
  one-verb-per-turn** (Observed, RHM Deep Scan: `chat()` parses *at most one* trailing action; the
  live seam is unverified). "Streamed + live + voice + interruptible + multi-mark-up-per-turn" is
  **not a thin wrapper** — it's a real gap (ANCHOR §6 admits this for "live + streamed + voice"). The
  prior art (Copilot Vision, A3) shows it's *achievable* but is a vendor-scale build, not a config
  flag. Mark "talks back live" as **net-new behavior over the existing request/response substrate**,
  not "the existing chat organ, streamed."
- **ANCHOR §4 anchor-idea: "tells you what this is at your altitude = `address_help` through
  `up_translate`."** *Mechanically right, but the naive part is assuming the content EXISTS to
  up-translate.* For registered elements, yes. For redesign mockups, `address_help` has nothing
  registered → `up_translate` of nothing = confabulation (A6). The naive read treats altitude as a
  *translation* problem; it is first a *grounding/registration* problem. Translation is the easy
  half; having something true to translate is the hard half.
- **ANCHOR §2: "things get marked up… context auto-resolves at each address so it always knows where
  you are."** *The substrate is real (R1/R2, Observed), but "always knows" overclaims.* R2 is
  net-new and unbuilt (Observed, Interactive Addressed Surface: R2 ☐); the cognition cascade that
  would make it *feel* like "it already knew" (Collective Cognition §9) is largely Designed/UNBUILT.
  "Auto-resolves" is a designed mechanism with a built seed, not a working faculty. Don't present it
  as done.
- **What the anchor gets RIGHT and should NOT be second-guessed:** the **DEAD-SIMPLE consent model**
  (ANCHOR §intro/§3). The prior art *supports* this — no review/design tool gates per-comment; the
  governance is "approve the batch, git is the safety net." Re-introducing per-comment classification
  would be re-importing the exact training-derived caution the anchor warns against, and nothing in
  the external prior art justifies it. Hold the simple model.

---

## Sources (for re-verification)

**External — CONFIRMED (independent / official):**
- Tour libs: `https://inlinemanual.com/blog/driverjs-vs-introjs-vs-shepherdjs-vs-reactour/` ·
  `https://userorbit.com/blog/best-open-source-product-tour-libraries` ·
  `https://github.com/kamranahmedse/driver.js`
- Copilot Vision (voice + highlight to guide): `https://support.microsoft.com/en-us/accessibility/copilot/basic-tasks-using-a-screen-reader-with-copilot-vision`
  · `https://primer.style/accessibility/patterns/copilot-accessibility-practices/`
- Deixis (academic): `https://arxiv.org/pdf/2605.02261` (Tableau Research, 2026, Proximity Semantics;
  cites Bolt 1980 "Put-That-There") · `https://dl.acm.org/doi/10.1145/3772318.3790938` ·
  `https://www.researchgate.net/publication/2474859_Automatic_Referent_Resolution_of_Deictic_and_Anaphoric_Expressions`

**External — marketing-claim (vendor page, described not verified):**
- `https://www.figma.com/solutions/ai-design-review-assistant/` (async batch critique, NOT live guided)
- `https://www.figma.com/community/plugin/1611550338941766411/annotateai-voice-typed-design-notes` (voice→annotation capture)

**Internal — Observed (vault build-prep + the deep-reads):**
- `RHM Walkthrough Organ — {Completion Criteria, Architecture-session reply, Research Synthesis,
  Sequenced Systems}.md` (the general-organ thesis + the design)
- `Interactive Addressed Surface — Completion Criteria.md` (the addressed-substrate floor: S0–S5,
  I1–I7, R1/R2; "click INDICATES + CONSENTS")
- `RHM Deep Scan — Right-Hand-Man Capabilities (ground truth).md` (the non-optimistic build-status:
  live seam unverified, modes mostly inert, `coa` likely unwired)
- `Collective Cognition — the context-resolution spine.md` (looking=address→auto-resolve; one
  substrate, per-type view-modes)
- `context-13-the-surface.md` (one artefact many faces; portals; literate-programming / annotate-as-
  you-compose precedent)
- ANCHOR.md (the wave anchor; §§1–8)
- **`build-prep/claude-design/` (on main, the deep-reads OF this surface):**
  `APPLICATION-STRUCTURE-PACK.md:504-586` (the Sequences Primitive + the ~17-surface map — the
  code-side "one organ, many surfaces" confirmation) · `CONVERGENCE-WALKTHROUGH.md` (the studio is now
  a real in-app `Review.tsx` on main, verified 6/6, unstyled, 5 net-new binds open incl. in-frame
  deixis) · `README.md` (doc ownership) · `research/deep/surface-intent.md` (per-surface designed
  intent; the studio as first consumer; the click-INDICATES+CONSENTS model) · `BACKEND-SEAM-PACK.md`
  (the backend contract: 102 routes, SSE, the `ui://`/`run://`/`code://` substrate)
