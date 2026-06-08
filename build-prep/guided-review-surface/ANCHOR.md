# ANCHOR — The Live, Guided, Right-Hand-Man Review Surface

## 0 · How to read this (research-wave anchor)

This is the **shared anchor** for a research wave. Read it IN FULL first. We are **NOT confirming it** —
stress-test it, contradict it where it's naive, and ground it in what's actually there. **Expansion ratio > 1:**
leave the idea bigger and more real than you found it. The "yes, but actually…" is the gold.

This describes a surface that was **already designed and discussed across prior sessions** (the Interactive
Addressed Surface + the RHM Walkthrough Organ) but **only half-built** — the current studio is a detached
scaffold that FAILED its user. Your job per area: find what was designed (in the vault, the code, the chat
history), find what exists, and ground the full thing. Mark evidence: **Observed (file:line) / Inferred /
External-prior-art / Anchor-idea.**

**One correction baked in up front (do not re-introduce it):** an earlier session over-engineered "consent"
into per-comment classification + per-address governance tiers. **That was wrong — training-derived caution,
not the user's need.** The real consent model is DEAD SIMPLE (see §3, the generate→approve→dispatch→git loop).
Do not re-impose elaborate gating. The hard part is the LIVE GUIDED EXPERIENCE, not the consent.

## 1 · The problem (concrete, from the user verbatim)

The user is **the commander, NOT a developer.** He has read no code, written no files, given no specs, and has
**no idea what to specifically expect.** When he opened the detached studio (the standalone mockup gallery), in
his words:

> "I had no idea what the hell I was looking at. I didn't know what anything was or what I was supposed to do
> or how to think about it… the interface just expected me to open every mockup and somehow know what the hell
> it was."

That is the failure this surface exists to kill. A gallery that dumps mockups on a non-developer and expects him
to already understand them is backwards. **The whole point is that he should NOT have to know — the right-hand-man
makes it comprehensible, live, at his altitude.**

## 2 · The insight / the big what-if

**What if the review surface is not a gallery you browse, but a LIVE GUIDED CONVERSATION the right-hand-man leads
you through?** Specifically:

- The RHM **walks you through a SEQUENCE** of screens/elements, and at each stop **tells you, at your altitude,
  what this is and what you can do here** — because you don't know, and shouldn't have to.
- You **set the pace** — NEXT / BACK, dwell on one as long as you want.
- It is **live and conversational**: you click and talk; **the RHM talks BACK** — "you mean like xyz?", "what
  kind of…?". It's intuitive, not a box that reads what you already typed.
- You **point deictically, across time**: *"I want THIS to come in from HERE, after I click that thing that
  opened before THIS showed up"* — and it follows you (what you're pointing at, what just happened, the order).
- As you talk, things get **marked up** — comments / tags on elements OR groups (the RHM does it for you, or
  you do, or it proposes). Context **auto-resolves** at each address so it always knows where you are and
  what's been said here.
- Then, when YOU decide, you click **generate** — the RHM turns everything you worked through into the
  plans/requests for the autonomous Claude builds, **shows you through them**, you **approve the batch to send
  off**, it's dispatched + committed to git. **If it breaks, git reverts it.** Done.

## 3 · The shape, held loosely

```
ENTER a sequence (a journey through screens, in directories, a pattern)
  └─ RHM SHOWS-ME: drives the view to a stop, explains at-altitude what this IS + what you can do
        ├─ you NEXT / BACK / dwell  (you set the pace)
        ├─ you CLICK + TALK  →  RHM TALKS BACK (live dialogue, follows your deixis: this/here/that-before-this)
        ├─ MARK-UP accrues: comments / tags on elements OR groups, at their ui:// addresses
        └─ CONTEXT auto-resolves at each locus (the RHM always knows where you are + what's been said)
  └─ … repeat across the sequence, as long as you want …
GENERATE (you click): RHM composes the plans/requests from everything discussed → SHOWS you through →
  you APPROVE the batch → dispatched to autonomous Claude → committed to git → revert if it breaks
```

**The consent model, in full (it's simple — do not complicate it):** the ONE approval is "I approve this batch
to be sent off." Git is the safety net. There is no per-comment classification, no per-element consent tier.
You talk, you click generate, you review what it shows, you approve, it builds + commits, you revert if wrong.

**The mockup-vs-live distinction (the user's own):** edits/comments can attach to **real UI** (a change to the
running app); **new-UI mockups are their own** (proposals for surfaces not yet built — the design-iteration
loop, where "generate" updates the mockup, not the live app). The surface handles both; they're distinct.

## 4 · Anchor-ideas (mine, marked as ideas — verify or replace)

- *Idea:* the "sequence" is the **RHM Walkthrough Organ's "walkthrough is a graph"** — a journey is an ordered
  set of stops (`ui://` addresses); NEXT/BACK steps the graph; the RHM narrates each stop. (Fork #3, prior session.)
- *Idea:* "the RHM talks back" = the existing **chat organ** (`suite.chat`) run **at the current locus** (the
  focus→locus→context channel), but **streamed + live + voice-capable**, not request/response.
- *Idea:* "tells you what this is, at your altitude" = **`address_help`** (what_this_is / how_to_change /
  how_to_use) passed through **`up_translate`** (present-at-Tim's-altitude).
- *Idea:* "mark up as you talk" = the RHM calling **`annotate` / tag** on the locus on the user's behalf during
  the conversation (it has the verb whitelist; annotate is in it).
- *Idea:* "generate" = accumulate the conversation's marked-up addresses → the RHM composes **build-intents /
  plans** (`surface_intent_at` / a batch) → shows them → one approve → the **wire dispatches** (`claude -p`) →
  git. The wire already exists end-to-end.
- *Idea:* voice — he says "I might be talking" — voice-in (STT) feeding the live dialogue is likely in-scope.

## 5 · Why it belongs here — the existing machinery it builds ON (verify reuse, don't reinvent)

- **The address/context system** — `ui://` addresses on every element; `annotate`/`annotations_at` (comment at
  an address); `attach_chat`/`chats_at`; `address_help`; `resolve_scope` (address→code); `up_translate`;
  `_resolve_context_at` / R2 (context auto-resolves at a locus); the `ui_info` registry; `data-ui-ref` →
  `addresses.json`. (All Observed in the deep-reads — see §7.)
- **The RHM organ** — `suite.chat` with `focus={selected:[ui://…]}` setting the locus; the verb whitelist
  (run/propose/build/consult/show/panel/extend); grounded-or-abstains.
- **The walkthrough/review/guide backend** — `/api/review/start|next|current|status`, `/api/walkthrough/start`,
  `/api/guide/start` (the system-initiated tour). These ARE the sequence-driver routes — verify what they do.
- **The wire** — `surface_intent_at` → `dispatch_decision` → `claude -p` → git checkpoint/commit; revertible.
- **The studio scaffold (half-built)** — `canvas/app/src/regions/Review.tsx`, `components/StudioKit.tsx`
  (Rail/Stage/RhmPanel/Composer), the `/api/corpus` gallery, in-frame deixis (click an element in a mockup →
  locus), the `mockup://` chat focus (RHM reads the mockup). This is the ROOM; the guided RHM is the missing guide.
- **The vault design** — `Interactive Addressed Surface — {Completion Criteria, Implementation Guide, Research
  Synthesis}.md` (S0/F4/I1–I7/R1/R2/L1/L3/L4 + "click INDICATES + CONSENTS"); `RHM Walkthrough Organ —
  Architecture-session reply.md` (Fork #1 the UI-component registry, Fork #3 walkthrough-is-a-graph); the RHM
  Deep Scan / show-me / how-to-on-addresses docs; the S1–S7 RHM scenarios. (In the VAULT build-prep:
  `/mnt/c/Users/Workstation001/Documents/Claude/Projects/counterpart/the Company/build-prep/`.)

## 6 · The honest hard parts (where it's fragile — the rigor area lives here)

- **Live conversational grounding under deixis.** Following "THIS from HERE after that thing that opened before
  THIS showed up" needs the RHM to track: what's pointed-at now, what just happened, and the order. Is that
  achievable with the current focus/locus + event log + the resident model? Where does it break?
- **Comprehension at the user's altitude.** The RHM must actually KNOW what each screen/element is to explain it
  — `address_help` only returns what's registered. For redesign mockups (proposed surfaces), is there enough to
  explain, or does it confabulate? This is the crux of the original failure.
- **Live + streamed + voice.** The chat organ is request/response today; "talks back" intuitively implies
  streaming + interruption + voice-in. What's the gap to live?
- **The RHM driving the view.** Does the walkthrough/review backend actually MOVE the surface (spotlight a stop,
  advance) — and does the FE follow it? (`ui_target` / `resolveUiTarget`.) Or is that aspirational?
- **Generate = composing good plans from a messy conversation.** Turning a dwelt, marked-up, talked-through
  sequence into coherent build-intents the user approves in one batch — how reliable, and what's the unit?
- **Mockup-vs-live routing.** A comment on a mockup element → a mockup edit; on real UI → a live build-intent.
  How does the surface know which, and does the generate-loop route correctly?

## 7 · What I can already see (real anchors — verify + extend, don't trust blind)

- `runtime/suite.py`: `chat`:4471 · `_chat_context`:1902 · `annotate`:3967 · `annotations_at`:4030 ·
  `ingest_comment`:3995/4138 · `attach_chat`:4191 · `set_presentation_pref`:4095 · `address_help`:1959 ·
  `resolve_scope`:6929 · `up_translate`:5100 · `_registry_ui_target`:5405 · `_resolve_context_at`/`_r2_gather`/
  `_r2_score` (R2) · `current_locus` · `context_at` (new, R2 route) · `surface_intent_at`:1025/6642.
- `runtime/bridge.py`: `/api/review/start|next|current|status` (~6318/6360) · `/api/walkthrough/start` ·
  `/api/guide/start` · `/api/chat` · `/api/act` · `/api/annotate` · `/api/annotations` · `/api/context` ·
  `/api/intent-at` · `/api/stream` (SSE).
- FE: `canvas/app/src/regions/Review.tsx` · `components/StudioKit.tsx` (Rail/Stage/RhmPanel/Composer) ·
  `StudioSeams.ts` · `useAppController.ts` (the SSE fold, foldCognition mirror) · `App.tsx` (the canvas↔review
  view-switch).
- The wire: `runtime/implement.py` (`dispatch_decision`, launch/verify/git-checkpoint).
- Vault design docs (read-source): the Interactive Addressed Surface triad + the RHM Walkthrough Organ reply +
  the RHM Deep Scan, in the vault build-prep path above. Chat genesis: 2026-06-02 (address+registry), 2026-06-04
  (click indicates+consents), the walkthrough-organ session.
- The Claude Design prep already on main: `build-prep/claude-design/{APPLICATION-STRUCTURE-PACK,BACKEND-SEAM-PACK,
  AUTHORING-FE-HANDOFF}.md` + `research/deep/{surface-intent,fe-structure,seams}.md` (the deep-reads of this surface).

## 8 · Open what-ifs (threads to pull)

- How does the RHM actually DRIVE a guided sequence today (review/walkthrough/guide) — and how far from
  "narrate each stop at-altitude + NEXT/BACK + dwell" is it?
- What's the smallest real path from request/response chat to **live, streamed, talk-back** dialogue at a locus?
- How does deictic + temporal grounding work — can the RHM resolve "this / here / that-before-this" from the
  locus + the event log + what's on screen?
- How does the RHM mark up on the user's behalf mid-conversation (annotate/tag at the locus), and how do tags on
  GROUPS (not just single elements) work?
- What does "generate" compose, concretely — one build-intent per marked-up address? a plan spanning the
  sequence? — and how does the one-approval batch + dispatch + git actually run?
- How does voice-in fold into the live dialogue (he's talking)?
- How does this generalize — is the studio just the FIRST instance of a guided-RHM surface that works for ANY
  part of the Company (the broader frame)?

## Closing — spirit note to the agents

Bring **what's actually there** — the prior design is real; find it in the vault, the code, and the chat
history, and ground it. **Contradict this anchor where it's naive** (especially: do NOT re-introduce elaborate
consent — find the simple model). The make-or-break question is whether the LIVE GUIDED experience is achievable
with the existing machinery + the resident model, or where it genuinely needs new building — answer that with
evidence, honestly, even if it's less rosy than this anchor hopes. Write FULLY; leave the idea bigger and more
real. This is the surface the commander reviews his whole Company through — it has to make sense to someone who
has never read a line of the code.
