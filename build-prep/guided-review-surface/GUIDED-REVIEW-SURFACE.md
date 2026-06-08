# The Live, Guided, Right-Hand-Man Review Surface — Grounded

> **What this is.** The synthesis of a 6-area research wave (anchor + AREA-1…6) on the surface the
> Commander reviews his whole Company through. No longer "what if" — this is grounded in what the
> wave found in the code, the vault, and the prior art, **corrected where the research corrected the
> anchor**, with the real build map and the decisions named for Tim.
>
> **Evidence marks used throughout:** **Observed (file:line)** = read directly in code/files ·
> **Inferred** = pattern-matched, not execution-verified · **Verified-by-use** = confirmed by a real
> run (provenance named) · **External** = outside-the-repo prior art. Where a companion *corrected*
> the anchor's file:line, this artefact uses the corrected mark and flags it.

---

## 0 · The grounded headline (read this first)

The surface was **always designed-general** — it is THE one human-interaction organ for the whole
Company (the "Sequences primitive": `resolve → present/work → persist → next/trigger`, run at every
scale), with **build-review as its FIRST consumer, not its purpose** (Observed, three independent vault
sources + `build-prep/claude-design/APPLICATION-STRUCTURE-PACK.md:504-586`, the ~17-surface map). It is
**designed-general, built-partial, live-unproven.**

The wave's decisive correction to the anchor: **the make-or-break is NOT comprehension and NOT the
consent model.** Comprehension *works* (result below); consent is *dead-simple and already built for
the single case* (one approve + git revert). **The make-or-break is GENERATE-FOR-MOCKUPS** — the
autonomous build loop edits the LIVE app end-to-end, but **there is no path that edits the redesign
MOCKUPS**, which are exactly what the Commander opens and reviews. That, plus a guided tour engine that
*raises* on the unregistered mockup addresses it would need to tour, makes **the mockups the consistent
frontier across the entire wave**. The live-app paths are largely ready; the mockup paths are the build.

### The verified comprehension result (the key result of the wave)

The original studio failure was **not** that the model can't explain a screen. It was that **neither
comprehension path was active** — no RHM focus (so no HTML injection) and the mockup was unregistered
(so `address_help` returned "(unregistered)"). The Commander was handed a screen with *nothing
explaining it*.

**Verified-by-use (provenance: the comprehension test specified in AREA-5 §1 was subsequently run as
part of this wave — not by this synthesis layer; two companions explicitly could not run it because the
bridge + 4B brain were down at their write-time).** The resident **Qwen3.5-4B**, given the 21KB
**C1-inbox** mockup **truncated to the 14KB cap** (so it lost ~1/3 of the content) plus a
non-developer's "what am I looking at?" with the mockup in focus, produced an **excellent
value-altitude explanation** — it named the screen ("the Company's Inbox / chief-of-staff dashboard"),
walked the 4 zones, the awaiting-approval pill, the inbox lanes, and told the user what to focus on and
what to ignore.

**Two halves, stated honestly:**
- ✅ **Comprehension works.** A small resident model, given the raw mockup HTML, explains a screen at a
  non-developer's altitude — even truncated. This is the single most load-bearing claim of the surface,
  and it holds.
- ⚠️ **The 14KB cap is NOT cleared.** C1-inbox survived at ~67% content; **IA-mobile is 73KB → ~19%
  survives.** "Comprehension works" is verified; "the cap is fine" is not. A cap-raise or HTML→text
  pre-digest stays **net-new** (§2, §4).

---

## 1 · What this surface IS (the experience, grounded)

Not a gallery you browse — a **live guided conversation the right-hand-man leads you through**. The
Commander has read no code, written no specs, and should not have to know what anything is. The RHM
makes it comprehensible, live, at his altitude. The shape (held to what the wave grounded):

```
ENTER a sequence (an ordered walk through screens / addresses — a journey)
  └─ RHM SHOWS-ME: drives the view to a stop, explains AT-ALTITUDE what this IS + what you can do here
        ├─ you NEXT / BACK / dwell  (you set the pace)              ← engine BUILT (live), FE lane net-new
        ├─ you CLICK + TALK → RHM TALKS BACK (live dialogue, follows this/here) ← locus BUILT; streaming + temporal net-new
        ├─ MARK-UP accrues at ui:// addresses (comments / tags)      ← operator path BUILT; RHM-does-it net-new(1 verb)
        └─ CONTEXT auto-resolves at each locus (R2 — it knows where you are + what's been said)  ← BUILT + running
  └─ … repeat across the sequence, as long as you want …
GENERATE (you click): RHM composes the plans from everything discussed → SHOWS you through →
  you APPROVE THE BATCH → dispatched to autonomous claude -p → committed to git → operator-revert if it breaks
        ↑ singular wire BUILT end-to-end · BATCH compose+approve net-new · MOCKUP-edit dispatch net-new (the spine)
```

**It is designed-general (Observed, confirmed three ways).** The walkthrough organ is parameterized by
a list of `ui://` addresses (`GUIDE_SEQUENCES`, Observed suite.py:6355-6395 / corrected from AREA-3 to
suite.py:6378). The `_chat_context` grounding is generic over any locus — there is no studio-specific
branch (AREA-2 §9). So the same `surface → present → respond → act` circuit points at review-items
today and at decisions / verifications / ideas / the project→product pipeline tomorrow. **The studio is
the first consumer of a general organ — not a tool that might later generalize.** (Vault Sources 1-3,
Observed; the Sequences Primitive named on-main at APPLICATION-STRUCTURE-PACK.md:504-541.)

**Relationally, where it sits (AREA-6 B2):** the **Interactive Addressed Surface** is the substrate
floor (every element addressable + annotatable + context-resolving); **Collective Cognition** is *how*
the RHM perceives each locus (looking = address → auto-resolve); the **Decision→Implementation Wire**
is the ACT half. The guided-review surface is the **human-facing face that composes the others** — it
*leads* the Commander across them, *perceives* each stop via the cognition spine, *records* his
responses, and *acts* via the wire. It is the Commander's-bridge made into one surface.

---

## 2 · The honest build map — three buckets

> Where a companion corrected the anchor's §7 line numbers, this map uses the **corrected Observed
> mark** and says so. Corrections found: `_registry_ui_target` = suite.py:6161 (anchor said :5405);
> `surface_intent_at` = suite.py:6816 (anchor said :1025/6642); the `ui://` grammar lives in
> `contracts/ui_info.py:194` `parse_ui_address` (anchor referenced `contracts/address.py`); the
> mockup-HTML injection cap `CAP = 14000` is at suite.py:2117.

### BUCKET A — READY (built + wired; reuse as-is)

| Capability | Evidence | Note |
|---|---|---|
| Focus → locus → context channel (RHM knows what you point at) | Observed suite.py:2073-2174 · StudioKit.tsx:219-220 | In the *studio* the locus IS fed and R2 fires live; outside it, I1/F4 still ☐ |
| R2 context auto-resolution at a locus (annotations + chats + events + howto + prefs, scored by recency×proximity×pin×semantic, 4000-char cap) | Observed suite.py:3036-3086 (gather 2812; score 2522; budget 2482) | More complete than any design doc; **ancestor (parent→child) inheritance works** |
| `address_help` 3-leg comprehension (what_this_is / how_to_change / how_to_use) | Observed suite.py:2213 (AREA-1) / :2213-2304 (AREA-2) | Degrades clean per leg; returns "(unregistered)" when unknown |
| `mockup://` raw-HTML comprehension injection ("read this FOR them, explain at altitude") | Observed suite.py:2086-2125 | The ONLY comprehension path for unregistered mockups — **Verified-by-use it works** (§0) |
| Walkthrough/guide ENGINE: drive view to a stop + narrate + NEXT/BACK | Observed suite.py:6198-6337 (`present_current`, `next`); `start_guide` :6442 | Model-free narration from corpus → never confabulates; fast |
| `ui_target` spotlighting (drive the live view to a stop) | Observed `_registry_ui_target` suite.py:6161 (CORRECTED) → FE `resolveUiTarget` :1469 / `spotlightUiRef` :1570 | Validates ui:// against registry, querySelector, scrollIntoView, 2.4s ring |
| In-mockup element deixis (click inside a staged mockup → its `data-ui-ref` address) | Observed StudioKit.tsx:101-134 · bridge.py:440-459 | 18 of 23 mockups carry `data-ui-ref`; a built surprise |
| `annotate` / `ingest_comment` / `attach_chat` / `set_presentation_pref` at any ui:// | Observed suite.py:4263 / :4291 / :4487 / :4391 | Operator face; address-keyed; append-only; never blurs operate-vs-annotate (route_click :4204) |
| The SINGULAR wire end-to-end: comment → intent → one approve → governed dispatch → `claude -p` → git → operator-revert | Observed `surface_intent_at` suite.py:6816 (CORRECTED) → `dispatch_decision` :7360 → implement.py launch :352 → git checkpoint :7611 → `revert_self_change` :8920 | Empty/orphan scope = DENY-ALL (real safety); exactly-once; operator-only approve; safe-by-default `plan` posture |
| Voice circuit: STT (whisper.cpp local default) + live VAD/finished-thought loop + streamed brain↔TTS overlap | Observed voice/AGENTS.md:16 · bridge.py:734-903 `/api/voice/stream` | **Stronger than the anchor feared** — voice-in is one of the most-ready legs |
| The studio ROOM (real in-app, superseded the failed gallery) | Observed Review.tsx · StudioKit.tsx (Rail/Stage/RhmPanel/Composer) · CONVERGENCE-WALKTHROUGH.md (verified 6/6, both widths) | Real RHM organ chatting at the pointed locus; comments → shared address store |

### BUCKET B — MODERATE (exists; reuse + wire a seam — not net-new architecture)

| Seam | What to do | Evidence |
|---|---|---|
| **Streaming text chat** ("talks back" *feels* live) | `chat_parts()` streaming generator already exists + is proven on voice; wrap it in a text SSE/NDJSON endpoint; FE appends each part as it arrives | Observed `chat_parts` suite.py:5264-5312; voice uses it bridge.py:734-903; text `/api/chat` is full-wait suite.py:5223-5242 |
| **Walkthrough ↔ chat composition** | When a walkthrough step advances, call `indicate(step_address)` so the chat at each stop is auto-grounded at that stop | Observed gap: advancing does NOT update the chat locus (AREA-2 §4.2) — ~5 FE lines |
| **Voice focus passthrough** | `/api/voice/stream` calls `chat_parts(transcript, gid)` with NO `focus` → voice is locus-blind; pass `focus.selected` through | Observed bridge.py:848 (no focus arg); `chat_parts` already accepts `focus` suite.py:5264. (Auto-listen via `sendChat` already carries focus.) |
| **Guided walk across mockup FILES** | Load file N → narrate (existing Stage + corpus); achievable with what's built | Inferred (AREA-5 Seam 3) — distinct from in-mockup-element spotlight (net-new, Bucket C) |
| **Batch DISPATCH leg** | Loop the existing `dispatch_decision` over the approved batch members — the dispatcher already handles concurrency (CONCURRENCY_CAP) | Observed `drive_dispatchable` implement.py:473-545 — the LEAST-new part of "generate" |
| **`approve_reach` (already built)** | A second consent dimension (authorize how far an edit propagates), default = pointed-address-only, optional | Observed `/api/approve-reach` bridge.py:1499; blast_radius minted at suite.py:6889 — **Tim-decision §4** |

### BUCKET C — NET-NEW / HARD (the missing layer — this is the real build)

| Build | What it is | Evidence / status |
|---|---|---|
| **(a) GENERATE-FOR-MOCKUPS — the autonomous mockup-edit dispatch** | No path edits the redesign mockups. On a mockup's ui://, `resolve_scope` → empty (proposed surface, no code) → DENY-ALL → nothing builds (correctly). Today the only mockup loop is a manual JSONL note (`/api/mockup-feedback`) a human-directed agent applies by hand — and it's being RETIRED for the in-app surface with no built replacement. **Net-new: a `claude -p` whose scope is `design/mockups/<file>.html`, verified by re-render/screenshot, committed, revertible.** | Observed bridge.py:1533/1564 (notes only); suite.py:7124 (`to_wire`); Review.tsx:14 (retired); empty-scope DENY-ALL suite.py:7895. **THE MAKE-OR-BREAK (§3).** |
| **(b) ACCUMULATE → COMPOSE → ONE-APPROVE BATCH ("generate" over a sequence)** | Every producer/approve/dispatch is **singular** — grep-confirmed airtight. No accumulation buffer, no compose-step, no batch approve, no "generate" button (zero matches in Review.tsx/StudioKit.tsx for generate/batch/compose). The GOVERNANCE+GIT+REVERT machinery is reusable as-is; **the accumulate→compose→one-approve leg is the build** (a wrapper over the singular dispatch). | Observed AREA-4 §2-3 full grep; the per-address pieces (`resolve_scope`, R2, `blast_radius`, `build_instruction`) all exist to compose from |
| **(c) MOCKUP-AWARE guided stop** | `present_current` **RAISES on an unregistered address** → the built tour engine **cannot tour the proposed mockups** it exists to review. Net-new: engine tolerates `mockup://`/unregistered stops (narrate from injected HTML, not corpus) OR lightweight per-mockup registration. | Observed suite.py:6218-6220 (raises). Connects (a)+(c): mockups are the frontier for BOTH tour AND edit |
| **(d) Live TEXT streaming substrate** | (Bucket B is the wiring; the *interruptible* text-streaming cancel path — client-disconnect detection extended from voice's `gone[0]`) is the net-new piece for barge-in on text | Observed voice barge-in bridge.py:780-793 — extends naturally but doesn't exist for text |
| **(e) NAVIGATION-HISTORY / standing locus-trail (TEMPORAL deixis)** | "that-before-this" has **NO substrate today.** `_current_locus` is in-memory last-wins; the event log carries no navigation events; only last-6 events (kind+summary) reach context. Net-new: emit `navigate` events on locus change + a `recent_loci()` reader + inject the trail. **Recommend scoping to "this/here + the last few you touched"** before promising full ordered temporal deixis. | Observed suite.py:2142 (in-memory), :1990 (6 events); StudioSeams.ts:86 flags standing locus ☐. AREA-2 §3.2 + AREA-5 §2c agree |
| **(f) RHM annotates as you talk** | `annotate` is NOT in `RHM_VERBS` (Observed suite.py:3158-3206 / :4031 refuses). **BUT `request_change` IS** and routes conversation → `surface_intent_at` → `ingest_comment` — so "RHM marks up as you talk" is **partially reachable today for build-intents.** Net-new for *arbitrary* annotate = **one whitelist entry + `current_locus()` as default address + a consent-model decision** (does it bypass the approval card mid-dialogue?). | Observed AREA-3 (verb list, `request_change` :3197 → :3994-4029); AREA-2 §6. Framed as "one verb + a consent call," not a missing capability |
| **(g) GROUP roll-up (stand at a group, see members' marks)** | The address tree gives group semantics **one way only**: comment ON a parent flows DOWN to children (ancestor-walk, works). The REVERSE — stand at a group, see all marks on its descendants — is **not built** (`_r2_ancestors` walks upward only). Net-new: a descendant-gather. | Observed suite.py:2556 (upward only). AREA-3 §1 — directional contradiction of the anchor |
| **(h) The FE SHOW-ME lane** | The Commander doesn't yet *see himself* walked through. Backend view-driving exists; the FE guided overlay + next/back/dwell controls + dial-select → `start_walkthrough` trigger are deferred/unbuilt. | Observed suite.py:6313-6316 (DEFERRED); AREA-1/3/5 |

**Two unverified-but-not-blocking flags (state, don't re-run):** the resident-4B comprehension quality
is now **Verified-by-use** (§0); `up_translate`/`coa` altitude-shaping **may not be FE-wired** (Observed
RHM Deep Scan Part 4 #7 — "declared-not-wired-to-surface") — confirm the explanation passes through
altitude-shaping, not just raw model output.

---

## 3 · The make-or-break (the spine)

**The surface is buildable NOW as a live-app review-and-tweak instrument.** "Walk me through the running
Company, explain each part at my altitude, comment, generate a change, approve, it builds + commits +
reverts" is built or a MODERATE reuse (Bucket A + B). That is genuinely close.

**It is NOT yet buildable as the thing its own founding story demands** — making the redesign MOCKUPS
comprehensible *and actionable* — because two net-new pieces gate it, and they are the same frontier:

1. **GENERATE-FOR-MOCKUPS (Bucket C-a).** When the Commander finishes a guided walk through a mockup and
   clicks **generate**, *nothing edits that mockup.* Comprehension without actionability is half the kill
   — and it's the design-iteration half, the exact half that originally failed him.
2. **The MOCKUP-AWARE guided stop (Bucket C-c).** The built tour engine *raises* on the unregistered
   mockup addresses it would need to tour. The tour can walk the live app; it cannot yet walk the
   proposals.

**Treat the surface as TWO loops sharing one room (AREA-5's sharpening of the anchor's own §3
distinction):**
- **Live loop — READY now:** guided walk over live `ui://` elements → comment → `surface_intent_at` →
  approve → `dispatch_decision` → git. Add text-SSE (feel) + the batch compose-and-show UX. Ship first.
- **Mockup loop — the net-new build:** define what "generate on a mockup" *dispatches* — a `claude -p`
  scoped to `design/mockups/<file>.html`, verified by re-render/screenshot, committed, revertible. The
  wire, git, and the mockup-feedback scaffold all exist to compose from; the routing decision + the
  mockup-scope resolver + the mockup-aware tour stop are net-new, and they are the gate.

**Prior-art frame (External, AREA-6):** the **mechanism** layer (spotlight / next / back / dwell) is a
commodity (Driver.js / Shepherd.js / Intro.js / Reactour) — **steal it; do not build it.** Our `ui://`
registry already *solves their #1 documented failure mode* (selector reliability under DOM churn). The
**intelligence** layer (live AI-composed sequence + altitude narration + cross-time deixis + mark-up +
generate, fused live) **is shipped end-to-end by nobody** — Microsoft Copilot Vision (voice + highlight
on a live screen) is the closest precedent for the *loop* but describes pixels, not registered intent;
Figma's AI review is async-batch critique for designers who already understand frames. The novelty is in
the seams, not the parts — which is exactly why it's worth building and why the work concentrates on the
live join, not the mechanism.

---

## 4 · The decisions for Tim (named, with options)

These are the genuine forks the wave surfaced. Each is a Tim-decision because it's an outcome/posture
call, not an implementation choice.

**D1 · `approve_reach` — keep or drop.** A second consent dimension is *already built and live*
(authorize how far an edit propagates; default = pointed-address-only). The simple model (one approve +
git) works WITHOUT it.
- **(A) Drop** — honor the anchor's "consent is dead-simple" correction; reach defaults to pointed
  address; remove the affordance. Cleanest.
- **(B) Keep as optional** — it's already off-by-default and doesn't break the simple flow; keep it for
  the rare wide-blast change.
- *My read:* lean (B) — it's built, optional, and doesn't re-introduce per-comment gating; but if it ever
  *shows* in the one-approve UX as a second gate, that's the training-derived caution the anchor warns
  against, so keep it invisible-unless-asked.

**D2 · The 14KB mockup-comprehension cap — raise vs pre-digest.** Comprehension is verified even
truncated, but IA-mobile (73KB) survives at ~19%.
- **(A) Raise the cap** — simplest; costs prefill latency every turn (heavy mockups → multi-thousand-token
  prefill, the likely "lag").
- **(B) HTML→text pre-digest** — extract structure/sections so 14KB carries far more *signal*; more build,
  better feel, scales to the big mockups.
- **(C) Both** — modest raise + pre-digest for the over-cap files.
- *My read:* lean (B) — the verified result was *already* truncated and good, so signal-density beats raw
  size; pre-digest is the move that makes the 73KB screens work without paying prefill on every turn.

**D3 · Voice-in — this build or later.** AREA-5 found voice-in is one of the *strongest* legs (whisper.cpp
local STT default + full live loop built); the ONLY gap is focus-passthrough (Bucket B, small).
- **(A) Include now** — it's nearly free (one focus-passthrough seam) and it's how Tim said he'd actually
  use it ("I might be talking").
- **(B) Defer** — ship typed-streaming first, add voice once the text loop feels right.
- *My read:* lean (A) — the cost is a single seam and the capability is already built; deferring leaves the
  most-ready leg on the table.

**D4 · The RHM-annotate verb + autonomous-annotate consent.** Net-new is one whitelist entry; the real
question is the consent posture.
- **(A) Add `annotate` to `RHM_VERBS`, still gated** — RHM *proposes* a mark, you approve (the current I3
  card). Safe, but interrupts the live feel.
- **(B) Autonomous mid-dialogue annotate** — the RHM marks up as you talk, no card (git/visibility is the
  net). Matches the anchor's "it does it for you" — but is a consent-model change.
- *My read:* annotation is non-destructive (no code changes, no dispatch), so (B) fits the "consent is
  simple" spirit *for marks specifically* while keeping the one-approve gate where it belongs (generate).
  Surfacing as your call because it *is* a consent-model change.

**D5 · Temporal-deixis depth — scope down or go full.** "that-before-this" has no substrate today.
- **(A) Scope down** — ship "this/here" (built) + "the last few things you touched" (a short locus trail
  from new navigate events). Both AREA-2 and AREA-5 recommend this.
- **(B) Full ordered temporal deixis** — multi-hop "the thing before that three steps ago"; the 4B confuses
  antecedents without heavy structured support; 45 years of HCI research says it's hard and unproductized.
- *My read:* lean (A) — deliver the trail, prove the feel, let depth grow; don't promise the research-stage
  capability up front.

**D6 · Proposed-surface narration when nothing is registered — LLM-narrate vs abstain.** For an unregistered
mockup address (AREA-6 a/b/c):
- **(A) Register intent at author-time** — the mockup arrives annotated with what each surface is for (the
  real fix; an existing Company principle — "agent documents as it composes").
- **(B) VLM/LLM-narrate + flag-as-inferred** — "this looks like X, I haven't verified."
- **(C) Abstain loudly** — "I don't have a registered description — here's the raw spec."
- *My read:* the verified result (§0) shows the injected-HTML path *already* narrates well, so (B) is the
  working floor today; (A) is the durable fix and aligns with the no-silent-failure law. Pursue (B) now,
  build toward (A).

---

## 5 · Proposed build sequence (toward loop-prep)

Ordered by what unblocks what. This is a dependency order, not a schedule.

1. **Text streaming (Bucket B + C-d).** Wrap `chat_parts()` in a text SSE; FE appends parts live. This is
   the single highest-leverage change for "feels live" and it unblocks the whole live-dialogue feel.
   *Unblocks:* the felt-live experience everything else rides on.
2. **Walkthrough ↔ chat composition + voice focus passthrough (Bucket B).** ~5 FE lines + one focus arg.
   *Unblocks:* every guided stop becomes auto-grounded; voice becomes locus-aware (D3-A).
3. **The FE show-me lane (Bucket C-h).** The guided overlay + next/back/dwell + dial-select trigger, riding
   the already-built backend view-driving. *Unblocks:* the Commander *sees himself* walked through — the
   experience becomes real, on the live app.
4. **Accumulate → compose → one-approve batch (Bucket C-b).** A compose-only mode over the singular wire +
   the "generate" button + the batch-review surface. *Unblocks:* "generate" exists at all; the live loop is
   now complete end-to-end.
5. **Mockup-aware guided stop (Bucket C-c).** Engine tolerates `mockup://`/unregistered stops, narrating
   from injected HTML. *Unblocks:* the tour can finally walk the proposals — and pairs with §0's verified
   comprehension to make mockup review legible.
6. **GENERATE-FOR-MOCKUPS — the mockup-edit dispatch (Bucket C-a, THE SPINE).** A `claude -p` scoped to the
   mockup HTML, verified by re-render/screenshot, committed, revertible. *This is the gate on the surface
   delivering its founding promise.* Do it after 1-5 so the mockup loop lands into a working room.
7. **Locus-trail / temporal deixis, scoped (Bucket C-e, D5-A).** Navigate events + `recent_loci()` + inject.
   *Unblocks:* "the last few things you touched."
8. **RHM-annotate verb (Bucket C-f, D4).** One whitelist entry + the consent posture you pick.
9. **Group roll-up (Bucket C-g).** A descendant-gather. Lowest-urgency; a quality-of-review addition.
10. **Cap/pre-digest refinement (D2).** Fold in once the comprehension feel under real (big) mockups is
    measured.

Threaded throughout: confirm `up_translate`/`coa` altitude-shaping is FE-wired (it may be
declared-not-wired); keep the consent model simple (one approve + git); steal the tour mechanism from the
commodity libraries rather than building it.

---

## Closing

This is the grounded picture we reason over and decide. The surface is **designed-general,
built-partial, live-unproven** — and the wave located the work precisely: the **live-app loop is nearly
there**, **comprehension is verified**, **consent is simple and built**, and the **mockups are the
consistent frontier** — both to *tour* and to *generate-edit*. The make-or-break is generate-for-mockups
+ the mockup-aware stop, riding a live, streamed, locus-grounded dialogue. The decisions in §4 are
Tim's; the sequence in §5 is the order that unblocks itself. **loop-prep turns this into completion
criteria.**
