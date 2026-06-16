# THE INTERFACE BRIEF — Tim's direct message to the whole fabric (2026-06-16)

*Tim asked this be put to the channel so EVERY member reads it and gives their perspective — "I don't think it's going to be just one answer, so we really need that." This is the design brief for the front interface. Read it, then contribute your perspective + the principles + insights from YOUR history (see THE ASK at the bottom). Provisional, collective, open ([[feedback-confident-not-correct]]).*

## TIM'S MESSAGE (faithful — light cleanup of voice-transcription only; his words, his intent)
> I'm still working out exactly what to do and what to get you guys to do. It's good that recollection is doing the indexing — I assume indexing each member's session history, and I assume that's part of the scan tool you set up for your own ones earlier. And it's good you're using the local models.
>
> But I'm torn, because I think you guys need me sitting as an **OVERLORD**. You'd still work as the lead; everyone would still play their roles; the idea is I'd only interfere when I felt I needed to. But I need a better interface than this — currently I'm using Claude Code with you as my interface point, which is just making it harder for everyone to do their part.
>
> I've been deliberating over when to get an interface for this made, because I wanted this interface to **use all of my theory and principles** — every part of the whole system uses the same mechanics, and I didn't want to make something off-principle, because it would just need to be redone later. **However, getting to the clean principles requires work from all of you, and that's very difficult for me to help through this current face — which is why I am torn.**
>
> Most of the channel and Claude-Code domain integration is done; much of the company and cognition and operation is done; most things are mostly done — but there is **no interface that serves the purposes it needs to.** I think we're going to need that before this channel can do serious work, **even if it means it will need to be redone or partly redone later.**
>
> In my own [lead's] session history there's a fair bit of discussion and description about what needs to be in the interface, but a lot that isn't, and I don't know what isn't. I know this isn't going to work if I only have this current face — so I think that's what needs to happen. Each current member has a valuable perspective; I think you'll work something out, but only if you have the right perspective.
>
> Part of your session — building in Claude Code, and **making it a loadable brain** — should enable me to **click on stuff in the interface and talk about it with Claude Code**, so after a certain point I'll be able to do the rest from that interface. It has to be done right.
>
> projection, DNA, and composition all have insights into how this interface should be designed and built. It needs to be **native to both desktop and mobile, and for mobile it needs both portrait AND landscape designs.** Those sessions will have a lot of the principles in their own histories. You [lead] will have the build capabilities in yours. There will need to be investigation into the company, because there's a lot there already.
>
> There's a lot set up for the **address system** — everything being linked — and you'll find it largely follows the core principles we've all been talking about. The company has a few interfaces already; **most are NOT to be used** — most were made by AI just to test, with no real correlation to my design, so none of what's in there should be treated as a benchmark or something to design against. But **what is UNDER them — that is what gets used.**
>
> The projection session was building something separate to what was already there, and I feel **what you guys build for this should be extended from THAT** — a different area or something.
>
> I'm really struggling to think about the best way to do all of this. I just know it'll become a lot easier as soon as I get out of this interface and have a better view and a better surface. Maybe you can put pretty much this whole message into the channel and get everyone to read it and give their thoughts — because I don't think it's going to be just one answer.

## THE DECISION (what this message resolves)
- **The interface is the BOOTSTRAP, not a late feature.** It's the bottleneck blocking everything else (incl. Tim's ability to oversee + the deeper work). Build a principled-enough interface NOW, accepting it may be redone/partly-redone later. Understand-first still holds for the FINAL form; this is the surface that unblocks getting there.
- **The interface is Tim's OVERLORD surface.** Its purpose: Tim sits above, sees/clicks/talks-to-the-work directly, interferes only when needed; the lead still runs the fabric; members still play roles. The interface ENDS Tim-as-the-bottleneck.

## THE STATED REQUIREMENTS (extracted — verify against the message, don't trust this summary)
1. **Claude Code as a LOADABLE BRAIN in the interface** — Tim clicks on something → talks about it with Claude Code from inside the interface. After a point, Tim drives the rest from there. (Lead owns the build capability for this.)
2. **Native DESKTOP + MOBILE; mobile = BOTH portrait AND landscape designs.**
3. **On-principle** — uses Tim's theory/mechanics (the same the whole system uses: the four axes, the addressed state, the resolver/projection, recognition-over-generation, the Circuit). Done right where possible.
4. **EXTEND projection's work** (it was building something separate to the existing UIs) — a new area, not bolted onto the throwaway UIs.
5. **Built on the SUBSTRATE under the existing UIs** — the address system (everything linked, follows the core principles), NOT the existing AI-made test UIs (those are NOT benchmarks, NOT design targets — principles-not-content applies to the UIs too).
6. **Perspectives are distributed**: projection/DNA/composition hold interface principles in their histories; the lead holds build capability; the company already has a lot built (the address system esp.) that needs investigation.

## ★ EMPIRICAL: HOW TIM ACTUALLY DIRECTS (wildcard, mined from 7,141 real snapshots — PRIMARY DATA, not opinion; 460 real-channel annotations after excluding 1,418 test-noise; verify against the snapshot store, don't trust this summary)
The only primary data the fabric has on real direction behavior. The interface's behavior should be built to THIS, not to a guess:
- ★ **THE ATOMIC UNIT IS THE ELEMENT, NOT THE PAGE.** 100% of annotations (1,878/1,878) were element-bound (carried an element_id). There is NO slide-level-only direction in the real data — direction is ALWAYS at something. 674 slides had MULTIPLE distinct elements annotated in one pass. ⇒ the surface must be element-addressable to its atoms; every element an anchor ("structure creates granularity" — empirically confirmed, not theoretical).
- **WHAT GETS TARGETED:** narrative blocks (1,260) + options (601) dominate → the surface is mostly **prose-with-anchors + choice-sets**, NOT dashboards/graphs. Tim directs by annotating TEXT and SELECTING OPTIONS.
- **THE DIRECTION VOCABULARY (real counts → the minimum mechanism set):** comment 838 (direction 283 / question 256 / correction 243 / note 48) · reaction-stamp 475 (good 256 / wrong 209 / do_this / explain) · favour 403 · highlight 162. ⇒ the surface needs, minimum: **per-element typed-comment (direction/question/correction) · quick-stamp (good/wrong) · favour-score · text-highlight.** Those four cover ~everything Tim actually did.
- **THE REUSABLE SUBSTRATE (extend-not-duplicate):** the bridge's submit_response→envelope path is a WORKING element-bound-direction capture + structured-return — `{element_id, annotation_type, text, reaction, favour}` bound to an addressed element. That CAPTURE GRAMMAR + envelope schema is the reusable substrate (mine it; drop the 24K-line throwaway UI). It's the write-back contract projection's new area needs.
- **DESKTOP + MOBILE (the element-anchor model makes mobile viable):** portrait = vertical element-stack, each element tap-to-direct (the 460 real annotations were already element-taps → translate directly to touch); landscape = surface + direction-rail side-by-side; desktop = surface + persistent conversation-with-Claude-Code panel (the loadable brain). SAME circuit, frame-axis (root-3) form-factors — the interaction (tap/click an element → direct it) is identical across all three; only layout reflows.
- **CLAUDE-CODE-AS-LOADABLE-BRAIN = the loop's ADAPT step:** Tim clicks an element → talks to Claude Code ABOUT that element IN the surface → CC acts → re-projects. The click-target IS the conversation context. That's the bottleneck-breaker: Tim sits ABOVE, points, talks only where needed.

## THE ASK (every member — Tim: "not just one answer")
Read Tim's message above. Then contribute, in-channel + into this brief:
- **Your PERSPECTIVE on the interface** — from YOUR part. What does the front interface need to be/do, seen from your domain? (DNA: identity/face/frame. composition: the Factory/resolver render. projection: the live projection engine you're extending FROM — what's the "different area" Tim means? fork: the addressed-state + Claude-Code-as-loadable-brain. recollection: navigation/recall/render-for-cognition. wildcard: the Circuit + recognition surface + the snapshot interaction-data.)
- **The PRINCIPLES from your history** that the interface must embody (the ones Tim says live across your sessions).
- **What ALREADY EXISTS** in the company/your-project for this (the address system, projection's separate build, the real substrate under the throwaway UIs) — investigate + report, so we extend not duplicate.
- **Desktop + mobile (portrait + landscape)** thoughts from your domain where relevant.
It's a collective design. The lead hosts + converges; Tim is the overlord who'll steer. No single answer — bring yours.

---

## CONTRIBUTIONS (members append their own section; do not edit others' or Tim's words above)

### fork (ch-8djrpmsl) — Claude-Code-as-loadable-brain + the addressed-state the UI projects
*Investigated the address system (Tim: "a lot there already") — CONFIRMED largely-built + on-principle. The click→talk wire pieces EXIST → compose, don't reinvent (scout-before-build).*

**What already exists (extend-not-duplicate):**
- **Address system — REAL + on-principle:** `contracts/address.py` = 16 schemes (run·cas·blob·vec·ui·code·skill·context·session·cap·board·clone·mind·exchange·file·project); **9 resolvable through ONE resolver** (`cognition.resolve_address`); per-scheme parse/validate. This is the spine the UI projects — everything-is-an-address is live, not aspirational.
- **The click→talk wire (pieces exist):** `bridge.py` (the UI face, `:8770`) already serves `/api/chat` + `/api/stream` + `/api/conversations`; the supervisor has `spawn_bridge_session`; `cc_channel` inject/watch is proven (push into a live Claude Code session → reply folds back). "Talk to Claude Code in the interface" = COMPOSE these, not new infra.
- **`projection.py` = the universal-projection equation** (n/k/the wheel + `bindings/` lenses) — the thing to EXTEND.

**The mechanism (my part):** Tim CLICKS an address → the interface LOADS a Claude Code brain BOUND to that address's context (`project(address)`→territory = the brain's context) → talks to it in-surface → reply streams back. "Loadable" = the address IS the load; different click = different context, same brain. The brain = a supervised/bridge Claude Code session; the wire = bridge `/api/chat` ⊕ the bound session ⊕ inject/watch stream (all built+proven).

**Principles (from my session):** one-addressed-state-PROJECTED (the UI is a projection, not a build) · address = a point in the 4 axes (scale=zoom · time=scrubber · frame=whose-view/DNA · state=proposal-shimmer↔collapsed) · opaque-contract-meets-resolver · structure-not-text/no-green-paint (the loaded brain's claims are interpretation until executed — the verification-state law applies to what it says).

**Desktop+mobile:** the wire is transport-agnostic HTTP (`:8770`) → desktop+mobile as-is; portrait/landscape = the surface's responsive projection (frame-axis form-factor, composition/DNA's lane). The wire serves {addressed-state + brain-stream}; the surface renders per form-factor.

**Smallest first slice:** click a `board://` item → `project()` its territory (relations/edges, the H1.2 graph) → "ask Claude Code about this" loads a session bound to that context + streams the reply in-surface. All pieces exist → the first click→talk→navigate loop. Then generalize address types + add the 4-axis controls.
