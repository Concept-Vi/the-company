# Completion Criteria — The Live, Guided, Right-Hand-Man Review Surface

> **The truth-table of what must be TRUE for this surface to be DONE.** This is the loop-prep
> companion to the grounded Research Synthesis (`GUIDED-REVIEW-SURFACE.md`, same folder) and the
> `Implementation Guide.md`. Read the synthesis first — it carries the evidence (Observed file:line,
> Verified-by-use, the build map). This doc carries the *bar*; the guide carries the *how*.

---

## How to read this doc (the loop-prep law, the verification rules)

**EVERY criterion is TWO-FACED.** No criterion has only a FUNCTION line. The loop is not allowed to
call a criterion done on function alone, nor on form alone.

- **FUNCTION** — the behaviour. Real state moves through the real system; verified by USE (a real run,
  provenance named — backend call / browser drive / device test), never by reading the code. Tim's
  standing law: *code-reading is not verification.*
- **FORM** — the operator-facing face. Built on the **design system + corpus tokens** (the single
  source: `canvas/app/src/components/design-system.css` ← `tokens.json`, aliased by
  `canvas/app/src/app.css`); a **navigable visual / spatial / temporal / relational surface a
  non-developer recognises BY SHAPE** — never a text-wall, never raw model output, never a
  developer console. Verified by the **design rubric** the build skills already run
  (**design-critic** + **design-lint** + a real **chrome render/screenshot**), NOT an invented one.
  The FORM face exists even for "backend-shaped" criteria: a locus-trail is *visual breadcrumbs*; an
  annotation is a *visible mark at its address*; a streamed reply is *parts landing live in the panel*.

**Status marks (honest split, never green-paint — Tim's standing law).** Each criterion is tagged:
- ✅ **verified-by-use** — watched it work end-to-end (provenance named).
- 🟡 **code-complete-untested** — built + wired, not yet run-proven.
- 🔴 **needs-tim** — a device/feel leg only Tim can judge (the *feel* of streamed talk-back, real
  mic/speaker voice, the *staged feel*, whether an explanation lands at *his* altitude). These are
  **NEVER painted green** by the loop — they are surfaced for Tim.

**Reuse status (from the synthesis buckets):** **READY** (built + wired, reuse as-is) · **MODERATE**
(exists; wire a seam) · **NET-NEW** (the real build). Carried per criterion so the loop knows the lift.

**Settled decisions baked in (do not re-open):**
- **Consent is SIMPLE** — one approve + git revert. `approve_reach` is **DROPPED** (the synthesis's own
  finding: the simple model works without it; the anchor's standing correction forbids re-introducing
  per-address consent tiers). No criterion depends on it.
- **Comprehension is VERIFIED working** — the resident 4B explained the C1-inbox mockup at a
  non-developer's altitude (synthesis §0). The 14KB-cap pre-digest is a **MODERATE refinement**, NOT
  the make-or-break, NOT net-new architecture.
- **Temporal deixis is SCOPED** to "this/here + the last-few-touched" — not full multi-hop ordered
  deixis.
- **Voice-in is IN** — it is one of the most-ready legs (the only gap is focus-passthrough).

---

## EXTENSIBILITY NOTE (this is a UNIFICATION, structured to GROW)

This surface is **not a one-off** — it is THE one human-interaction organ for the whole Company, and
the build-review studio is its **first consumer**. The criteria below are grouped so that **full
directory-area-coverage research rounds will APPEND more groups** as related threads are found (Tim's
plan). New groups slot in as `Group N` blocks with the same two-faced shape; the mode-integration
(Group I) is the join that lets a *new* consumer (decisions / verifications / ideas / the
project→product pipeline) ride the SAME organ by declaring its own mode-row + resolution lens, with no
parallel stepper. **Never filter a found thread out as "out of scope" — append it as a criterion.**

---

## Group A — The guided show-me sequence (the RHM walks you through)

The Commander is *led*, not handed a gallery. He enters a sequence (an ordered walk through
`ui://`/`mockup://` addresses); the RHM drives the view to each stop, narrates AT-ALTITUDE what this
IS + what you can do here; he sets the pace (next/back/dwell).

### A1 · Enter a sequence → the RHM drives the view to the first stop · MODERATE
- **FUNCTION:** Selecting the guided/walkthrough experience starts the organ over a real item set
  (`start_walkthrough` → `start_session` → `present_current(0)`), returns a first stop with a
  registry-valid `ui_target`, and the FE drives the live view to that element (scroll + 2.4s spotlight
  ring). Verified by a browser run: pick walkthrough → the view moves to stop 0 and rings the element.
- **FORM:** A guided overlay rendered on corpus tokens — a calm, spatial "you are here / next" frame,
  not a modal text dump. The spotlight ring + the narration card read as ONE place the eye lands.
  design-critic + chrome screenshot pass.
- *Status target:* 🟡 backend READY (`start_walkthrough` suite.py:6287 already binds dial→organ); FE
  overlay is the lift. The *led feeling* is 🔴 needs-tim.

### A2 · At each stop, narrate AT-ALTITUDE what this IS + what you can do · READY (backend)
- **FUNCTION:** Each `ui://` stop frames its narration from the **corpus** (`address_help` 3-leg
  bundle — `what_this_is` / `how_to_use`), MODEL-FREE by construction (never confabulates), composed
  with any flow-level `teach` side-channel. Verified: a guided stop returns non-empty `framing` text
  sourced from the registry, byte-for-byte the corpus narration when no teach is present.
- **FORM:** Narration presented as plain-language, at-altitude prose in the guide card (corpus tokens,
  serif display voice), not a registry dump or JSON. design-critic pass; reads as a person explaining,
  not a tooltip.
- *Status target:* 🟡 (engine Observed suite.py:6207-6257; FE card presentation is the lift). The
  *altitude landing* is 🔴 needs-tim.

### A3 · You set the pace — NEXT / BACK / dwell · MODERATE
- **FUNCTION:** next/back step the cursor through the session (`next` suite.py:6492 / `present_current`);
  dwell is "no advance" (the operator simply stays). Verified by browser: clicking next/back moves the
  spotlight + narration to the adjacent stop; dwelling holds the locus + keeps the chat grounded there.
- **FORM:** next/back/dwell controls are visible, spatial pace controls (corpus tokens) — a "你 set the
  pace" affordance, not hidden keybinds. A progress sense (stop N of M) the eye reads. design-lint +
  screenshot pass.
- *Status target:* 🟡 (backend stepper READY; FE controls + the dial-select→start trigger are the FE
  show-me lane, Group H).

### A4 · Guided walk across mockup FILES (not just live elements) · MODERATE
- **FUNCTION:** A sequence whose stops include `mockup://<file>` loads file N into the Stage and
  narrates it (the existing Stage + corpus + the mockup-comprehension injection), advancing file-to-file.
  Verified: a multi-mockup sequence renders each mockup in turn with a narration grounded in its content.
- **FORM:** The mockup renders full in the Stage (its own HTML, sandboxed), with the guide card beside
  it — a "showroom with a guide" shape, not a file list. design-critic pass.
- *Status target:* 🟡 (Stage exists; the mockup-aware stop, Group F, unblocks the narration path).

---

## Group B — The live talk-back (you click + talk, the RHM talks BACK)

It is a conversation, not a box that reads what you typed. The reply *feels live* (streamed), follows
what you point at, and the RHM asks back.

### B1 · Streamed text talk-back (the reply lands live, part by part) · MODERATE
- **FUNCTION:** A text chat at the locus streams the reply in parts as the brain produces them (wrap the
  existing `chat_parts()` generator — Observed suite.py:5264, proven on voice — in a text SSE/NDJSON
  endpoint; FE appends each part). Verified by a real call: parts arrive incrementally, not one full-wait
  blob.
- **FORM:** Parts land in the chat panel live, on corpus tokens, with a calm streaming cadence (no
  layout jump per part) — the *talks-back* feel. design-critic + a screen recording / chrome render.
- *Status target:* 🟡 backend MODERATE (engine exists, text endpoint net-new wiring). The *live feel* is
  🔴 needs-tim.

### B2 · Talk-back follows what you point at (locus-grounded dialogue) · READY → MODERATE
- **FUNCTION:** A chat turn carries the operator's focus (`focus.selected`) so R2 resolves context AT
  that locus (annotations + chats + events + howto + prefs, scored, capped) and the reply answers with
  respect to it. In-mockup element clicks (`data-ui-ref`) and `mockup://` focus both feed the locus.
  Verified: clicking element X then asking "what's this?" yields an answer grounded in X, not the page.
- **FORM:** The pointed element is visibly the locus (a persistent indication mark / "talking about: X"
  chip on corpus tokens) so the operator SEES what the RHM is grounded on. design-lint pass.
- *Status target:* ✅ in the studio (focus→locus→R2 fires live, Observed suite.py:2073-2174,
  StudioKit.tsx:219); 🟡 for the streamed path carrying focus.

### B3 · Interruptible talk-back (barge-in on text) · NET-NEW
- **FUNCTION:** The operator can interrupt a streaming text reply (start a new turn) and the in-flight
  generation stops (client-disconnect detection extended from voice's `gone[0]` barge-in path, Observed
  bridge.py:780-793). Verified: typing/sending mid-stream halts the prior stream cleanly.
- **FORM:** Interruption reads as natural — the cut reply settles, the new turn begins, no error state,
  no orphaned spinner. design-critic pass on the transition.
- *Status target:* 🟡 (extends naturally from voice; net-new for text). The *interrupt feel* is 🔴.

### B4 · The RHM asks BACK (clarifying dialogue, not echo) · READY (rides the model)
- **FUNCTION:** When the operator's intent is underspecified, the RHM responds conversationally
  ("you mean like X?", "what kind of…?") rather than only restating — this rides the resident brain +
  the grounded context, no new mechanism. Verified by a real exchange where the RHM asks a clarifying
  question grounded in the locus.
- **FORM:** The back-and-forth reads as dialogue turns in the panel (corpus tokens, clear
  operator-vs-RHM voicing). design-lint pass.
- *Status target:* 🔴 needs-tim (quality/feel is a judgement only Tim makes); mechanism READY.

---

## Group C — Comprehension at altitude (the original-failure killer)

The screen must explain ITSELF, at Tim's altitude, the moment he lands on it — because he should not
have to know what anything is. **This is VERIFIED working; the criteria here lock it in + refine it.**

### C1 · A mockup explains itself at a non-developer's altitude · READY / ✅ verified-by-use
- **FUNCTION:** With a `mockup://<file>` in focus, the RHM reads the raw HTML FOR the operator and
  explains, at plain-language altitude, what the screen IS + what he can do here (Observed injection
  suite.py:2086-2125). **Verified-by-use (synthesis §0):** the resident Qwen3.5-4B, given C1-inbox
  truncated to 14KB, named the screen, walked the zones, and told the operator what to focus on.
- **FORM:** The explanation presents as at-altitude prose in the chat/guide card (corpus tokens), NOT
  raw HTML, NOT a markup-fixated dump. design-critic pass that it reads like a person, not a parser.
- *Status target:* ✅ FUNCTION verified-by-use; FORM 🟡 until the presentation card is design-passed; the
  *his-altitude* judgement is 🔴 needs-tim.

### C2 · Registered live elements explain themselves (the 3-leg path) · READY
- **FUNCTION:** On a registered `ui://` element, `address_help` returns what_this_is / how_to_change /
  how_to_use, degrading clean per leg. Verified: a registered element returns a populated bundle; an
  unknown one returns "(unregistered)" honestly (no confabulation).
- **FORM:** The three legs present as a navigable at-altitude card (what / how-to-change / how-to-use as
  recognisable zones on corpus tokens), not a flat blob. design-lint pass.
- *Status target:* 🟡 (engine Observed suite.py:2213; presentation card is the lift).

### C3 · Comprehension passes through altitude-shaping (not raw model output) · MODERATE
- **FUNCTION:** The explanation IS routed through the altitude-shaping organ (`up_translate`/`coa`), not
  raw model output. **The synthesis flags this as possibly declared-not-wired** (Observed RHM Deep Scan
  Part 4 #7) — so the bar is to CONFIRM the FE path actually routes the explanation through
  altitude-shaping, traced end-to-end. Verified: the trace shows the shaping in the live path (not
  assumed).
- **FORM:** Output reads at-altitude (no jargon leak) — the design rubric judges the register.
- *Status target:* 🟡 (must confirm the wire; net-new if it's declared-not-wired). 🔴 needs-tim on register.

### C4 · The 14KB-cap pre-digest refinement (big mockups survive) · MODERATE / refinement
- **FUNCTION:** Mockups over the 14KB injection cap (Observed CAP=14000 suite.py:2117; IA-mobile 73KB →
  ~19% survives) are pre-digested (HTML→text structure/sections) so the cap carries far more *signal*,
  OR the cap is modestly raised. Verified: a >14KB mockup yields a complete at-altitude explanation
  covering its tail, not just its head.
- **FORM:** No operator-facing change beyond a fuller, more accurate explanation — judged by the
  explanation card reading complete (no "and then it cuts off" feel). design-critic on a big-mockup run.
- *Status target:* 🟡 NET-NEW refinement (a pre-digest pass). **NOT make-or-break** — fold in once the
  feel under real big mockups is measured (synthesis D2, lean pre-digest).

---

## Group D — The addressed markup (comments / tags accrue at addresses, incl. GROUPS)

As you talk, marks accrue at `ui://` addresses — the operator does it, or the RHM does it for him.
Context auto-resolves at each locus so the RHM always knows what's been said HERE.

### D1 · Mark-up accrues at an address (comment / tag / chat / pref) · READY
- **FUNCTION:** `annotate` / `ingest_comment` / `attach_chat` / `set_presentation_pref` record
  append-only at any `ui://` address; `route_click` never blurs operate-vs-annotate (Observed
  suite.py:4263/4291/4487/4391, route_click:4204). Verified: a comment at address X persists and
  resolves back at X (and its ancestors) on the next turn.
- **FORM:** A mark is a VISIBLE thing at its address — a badge / pin / count on the element, navigable,
  on corpus tokens — not an invisible log entry. design-lint + screenshot pass.
- *Status target:* 🟡 (operator path Observed/READY; the visible-mark FORM is the lift).

### D2 · Context auto-resolves at each locus (R2) · READY / ✅ running
- **FUNCTION:** At the locus, R2 gathers annotations + chats + events + howto + prefs across the address
  AND its ancestors, scored by recency×proximity×pin×semantic, budget-capped, injected into the turn
  (Observed suite.py:3036-3086; ancestor inheritance works). Verified-by-use: it fires live in the studio.
- **FORM:** The operator can SEE what's resolved here (the `context_at` read-face / a "what's been said
  here" panel on corpus tokens) — a relational surface, not a hidden inject-string. design-critic pass.
- *Status target:* ✅ FUNCTION running; FORM 🟡 (the visible read-face is the lift).

### D3 · GROUP roll-up — stand at a group, see members' marks · NET-NEW
- **FUNCTION:** Standing at a group/parent address, the surface gathers marks on ALL its descendants
  (a descendant-gather — today only the REVERSE works: a parent comment flows DOWN via ancestor-walk
  `_r2_ancestors`, Observed suite.py:2556 upward-only). Verified: marks on children appear when standing
  at the parent.
- **FORM:** The roll-up presents as a relational/spatial view (the group as a container showing its
  members' marks), recognisable by shape. design-critic pass.
- *Status target:* 🟡 NET-NEW (a descendant-gather). Lowest urgency — a quality-of-review addition.

---

## Group E — The accumulate → compose → one-approve BATCH ("generate")

When YOU decide, you click **generate**: the RHM composes the plans from everything discussed across the
sequence, SHOWS you through them, you approve THE BATCH, it dispatches → git → revertible.

### E1 · The singular wire holds end-to-end (the floor it composes from) · READY
- **FUNCTION:** comment → `surface_intent_at` → one operator approve → governed `dispatch_decision` →
  `claude -p` → git checkpoint → operator-revert (Observed suite.py:6816 → :7360 → implement.py:352 →
  :7611 → revert_self_change:8920). Empty/orphan scope = DENY-ALL; exactly-once; operator-only approve.
  **Evidence reconciliation:** the synthesis Bucket A marks this **Observed** (code-read, NOT re-run by
  this wave); it was **verified by the PRIOR decision→wire build** (provenance:
  `project-decision-wire-built.md` — implement → verified → closed). This wave does NOT re-run it; E2's
  batch path will exercise it.
- **FORM:** The single-intent approval card (corpus tokens) shows the scope + the change plainly; the
  revert affordance is visible. design-lint pass.
- *Status target:* ✅ FUNCTION verified by the prior wire build (not re-run here — Observed for this wave);
  FORM 🟡.

### E2 · Accumulate → compose → one-approve BATCH · NET-NEW
- **FUNCTION:** A compose-only mode accumulates the sequence's marked-up addresses into a BATCH, the RHM
  composes build-intents from them (reusing `resolve_scope`, R2, `build_instruction` per address), a
  GENERATE button mints the batch, the operator approves ONCE, and the batch dispatches by looping the
  existing `dispatch_decision` over members (the dispatcher already handles concurrency, Observed
  `drive_dispatchable` implement.py:473-545). Verified: a multi-mark sequence → one approve → all members
  dispatch + commit; refusal cases (empty scope) still DENY-ALL per member.
- **FORM:** A batch-review surface (corpus tokens) — the operator SEES the composed plans as a navigable
  list/board he walks before approving, with the ONE approve gate; not a wall of JSON. design-critic +
  screenshot pass.
- *Status target:* 🟡 NET-NEW (wrapper over the singular wire; the governance/git/revert machinery is
  reused as-is). The one-approve UX must NOT re-introduce per-comment gating (consent stays simple).

---

## Group F — GENERATE-FOR-MOCKUPS + the mockup-aware stop (THE MAKE-OR-BREAK)

The autonomous loop edits the LIVE app; **nothing edits the redesign MOCKUPS** — which are exactly what
the Commander opens and reviews. This is the spine: comprehension without actionability is half the
kill, and it's the design-iteration half that originally failed him.

### F1 · The mockup-aware guided stop (the tour can walk the proposals) · NET-NEW
- **FUNCTION:** `present_current` tolerates a `mockup://`/unregistered stop — narrating from the injected
  HTML (Group C path) instead of raising (today it RAISES on an unregistered address, Observed
  suite.py:6218-6220, so the built tour CANNOT tour the proposals it exists to review). Verified: a
  guided sequence with a mockup stop narrates that stop instead of erroring.
- **FORM:** The mockup stop renders + narrates indistinguishably from a live stop (same guide card, same
  spotlight idiom on corpus tokens) — the operator can't tell it's a "harder" stop. design-critic pass.
- *Status target:* 🟡 NET-NEW (engine tolerance OR lightweight per-mockup registration).

### F2 · GENERATE-FOR-MOCKUPS — the autonomous mockup-edit dispatch · NET-NEW · **MAKE-OR-BREAK**
- **FUNCTION:** Clicking generate on a mockup's locus dispatches a `claude -p` whose scope is
  `design/mockups/<file>.html`, verified by re-render/screenshot, committed to git, revertible — the
  mockup-scope resolver + the mockup-vs-live routing decision are the net-new pieces (today: empty scope
  on a proposed surface → DENY-ALL → nothing builds, Observed suite.py:7895; the only mockup loop is a
  manual JSONL note being retired, Observed bridge.py:1533/1564, Review.tsx:14). Verified-by-use: a
  talked-through change to a mockup → generate → the mockup HTML is edited, re-rendered, committed, and
  revertible.
- **FORM:** The operator SEES the mockup change land — a before/after render in the Stage + the change in
  the batch-review surface (corpus tokens) — not a git diff. design-critic + before/after screenshots.
- *Status target:* 🟡 NET-NEW — **THE GATE on the surface delivering its founding promise.** The
  *did-it-do-what-I-meant* judgement is 🔴 needs-tim.

---

## Group G — Temporal deixis (SCOPED to this/here + last-few-touched)

"I want THIS to come in from HERE, after that thing that opened before THIS" — followed via a short
standing locus-trail. **Scoped — not full multi-hop ordered deixis (synthesis D5-A).**

### G1 · "this / here" — the current locus is followed · READY
- **FUNCTION:** The backend-held `_current_locus` tracks what the operator points at (last-wins on
  multi-select, Observed suite.py:2142); the dialogue answers with respect to it. Verified: "this" in a
  message resolves to the pointed element.
- **FORM:** "here" is visibly indicated (the locus chip / mark, Group B2 FORM). design-lint pass.
- *Status target:* ✅ FUNCTION (current_locus runs); FORM 🟡.

### G2 · "the last few you touched" — a standing locus-trail · NET-NEW
- **FUNCTION:** Locus changes emit `navigate` events; a `recent_loci()` reader returns the last-few
  touched addresses (in order); the trail is injected into context so "that-before-this" resolves over
  the recent set (today: no navigation substrate — `_current_locus` is in-memory last-wins, only last-6
  events reach context, Observed suite.py:2142/:1990; StudioSeams.ts:86 flags standing locus ☐).
  Verified: after touching A→B→C, "the one before this" resolves to B.
- **FORM:** The trail presents as visual breadcrumbs (corpus tokens) — a temporal/spatial strip the
  operator reads, not a hidden list. design-critic pass.
- *Status target:* 🟡 NET-NEW, scoped. **Do not promise full ordered multi-hop deixis** (the 4B confuses
  antecedents without heavy support; HCI research says it's hard).

---

## Group H — Voice-in + the FE show-me lane

### H1 · Voice-in feeds the live dialogue, locus-aware · MODERATE
- **FUNCTION:** STT (whisper.cpp local default) + the live VAD/finished-thought loop feed the dialogue
  (Observed voice/AGENTS.md:16, bridge.py:734-903 `/api/voice/stream`); the ONLY gap is passing
  `focus.selected` through so voice is locus-aware (Observed bridge.py:848 calls `chat_parts` with no
  focus; `chat_parts` already accepts focus, suite.py:5264; auto-listen via `sendChat` already carries
  focus). Verified: speaking while pointing at X yields an answer grounded in X.
- **FORM:** The voice circuit's existing surface (mic state, listening indication) on corpus tokens,
  showing the pointed locus while talking. design-lint pass.
- *Status target:* 🟡 MODERATE (one focus-passthrough seam). The *real-mic / auto-listen feel* is 🔴
  needs-tim (device-only; never green-painted).

### H2 · The FE show-me lane (the Commander SEES himself walked through) · NET-NEW
- **FUNCTION:** The FE guided overlay + next/back/dwell controls + the dial-select → `start_walkthrough`
  trigger, riding the already-built backend view-driving (Observed suite.py:6313-6316 DEFERRED — backend
  binding exists, view-drive is the FE half). Per step the FE calls `resolveUiTarget(ui_target)` to drive
  + spotlight, and `indicate(step_address)` so the chat at each stop auto-grounds (Observed gap: advancing
  does NOT update the chat locus — ~5 FE lines, synthesis Bucket B). Verified by browser: picking
  walkthrough drives the view stop-by-stop, controls work, each stop's chat is grounded there.
- **FORM:** The whole show-me experience reads as ONE guided surface (overlay + spotlight + narration +
  pace controls) on corpus tokens — the experience the Commander recognises as "being walked through,"
  not a row of buttons. design-critic + chrome screenshot pass.
- *Status target:* 🟡 NET-NEW (FE). The *walked-through feel* is 🔴 needs-tim.

---

## Group I — The unifying connections (mode-integration + subsystem improvements)

**This is the UNIFICATION centerpiece.** The surface connects in AS A MODE and uses many subsystems; for
each it reuses, it may force an improvement — these are captured as criteria, never dropped.

### I1 · The surface IS the `walkthrough` mode (mode-integration) · MODERATE
- **FUNCTION:** The guided-review surface is bound to the existing `walkthrough` mode in MODE_REGISTRY
  (Observed suite.py:1278, with `guided`/`show-me` subtypes already declared). The mode declares which
  faculties fire via the axes it already carries: its **resolution lens** (`strata=None`,
  `howto_detail=full`, `budget=6000`/`8000` for show-me — the affordance leg is the POINT), its **live**
  activation contexts (`per-turn`), its **grain** (`paragraph`), its **brain_config** (`voice-64k`).
  Selecting walkthrough sets the dial AND starts the organ (`start_walkthrough` suite.py:6287 already
  binds dial→organ — this is NOT "create a mode," it is bind/declare/refine). Verified: entering
  walkthrough mode resolves context through the walkthrough lens (full howto, wide budget) AND starts the
  guided organ.
- **FORM:** The mode is selectable on the presence dial (corpus tokens), and entering it visibly shifts
  the surface into guided/show-me register. design-lint pass on the dial + the mode shift.
- *Status target:* 🟡 MODERATE (mode-row + dial→organ seam exist; FE dial-select trigger is the lift, ties
  to H2). The faculty-axes are READY in the registry.

### I2 · The walkthrough mode's resolution lens admits the mockup-comprehension path · NET-NEW
- **FUNCTION:** The improvement the unification forces: the walkthrough mode's `resolution` lens (and
  `present_current`'s mockup tolerance, F1) admit the `mockup://` HTML-comprehension injection so the
  guided/show-me mode actually fires the comprehension faculty on proposal stops. If the mockup-comprehension
  injection has no home in the registry's axes, it is declared as a faculty the walkthrough mode fires —
  marked NET-NEW honestly. Verified: in walkthrough mode, a mockup stop resolves context that INCLUDES the
  injected mockup HTML.
- **FORM:** No new operator surface — judged via C1/F1 (the mockup explains itself within the guided stop).
- *Status target:* 🟡 NET-NEW (the join between the mode lens + the comprehension injection + F1).

### I3 · Walkthrough ↔ chat composition (advancing re-grounds the chat) · MODERATE
- **FUNCTION:** When a walkthrough step advances, the chat locus updates to the new stop (call
  `indicate(step_address)` on advance — Observed gap: advancing does NOT update the chat locus, ~5 FE
  lines, synthesis Bucket B). Verified: after next, asking "what's this?" answers about the NEW stop.
- **FORM:** The locus chip (B2 FORM) updates as the walk advances — the operator SEES the grounding move
  with the spotlight. design-lint pass.
- *Status target:* 🟡 MODERATE (a small FE seam, part of H2).

### I4 · The RHM annotates as you talk (the RHM-annotate verb) · NET-NEW
- **FUNCTION:** The improvement the unification forces: `annotate` is NOT in `RHM_VERBS` (Observed
  suite.py:3158-3206 refuses); add it as ONE whitelist entry with `current_locus()` as the default
  address, so "RHM marks up as you talk" works for arbitrary annotations (today `request_change` IS
  whitelisted and routes conversation → `surface_intent_at` → `ingest_comment`, so build-intents are
  already partially reachable, Observed suite.py:3197). Annotation is NON-destructive (no code change, no
  dispatch), so it fits the "consent is simple" spirit — the RHM marks autonomously mid-dialogue; git +
  visibility is the net; the one-approve gate stays on GENERATE, not on marks (synthesis D4-B). Verified:
  during a dialogue the RHM places a mark at the locus and it persists + is visible.
- **FORM:** The RHM-placed mark appears as a visible mark at its address (D1 FORM), distinguishable as
  RHM-authored vs operator-authored. design-lint pass.
- *Status target:* 🟡 NET-NEW (one whitelist entry + default-address + the autonomous-annotate consent
  posture). The *does-it-interrupt-the-feel* judgement is 🔴 needs-tim.

### I5 · Subsystem-reuse register (the connections held, nothing reinvented) · cross-cutting
- **FUNCTION:** Each subsystem the surface touches is REUSED, never paralleled: context resolution (R2),
  the wire (`surface_intent_at`/`dispatch_decision`), the walkthrough/guide engine
  (`start_guide`/`present_current`/`next`), voice (`chat_parts`/`/api/voice/stream`), the cognition modes
  (MODE_REGISTRY), the address/registry substrate (`ui_info`, `data-ui-ref`→`addresses.json`). Verified:
  no parallel stepper, no second intent path, no duplicate scoring source is introduced (grep-confirmed at
  build time). This criterion is the **anti-parallel-system guard** — it stays TRUE across all groups.
- **FORM:** N/A as a screen; verified structurally (one-source law) — but every group's FORM rides the
  SAME design system, which is the form-level expression of the same non-duplication.
- *Status target:* 🟡 (a standing invariant the loop re-checks per criterion).

---

## Priority order (dependency order, not a schedule)

Reuses the synthesis §5 ordering — already dependency-ordered, each unblocks the next:

1. **B1 — Text streaming** (the felt-live experience everything rides on).
2. **I3 + H1-seam — Walkthrough↔chat composition + voice focus-passthrough** (every stop auto-grounds;
   voice becomes locus-aware).
3. **H2 — The FE show-me lane** (the Commander SEES himself walked through — A1/A2/A3 become real).
4. **E2 — Accumulate → compose → one-approve batch** ("generate" exists; the live loop is complete).
5. **F1 — The mockup-aware guided stop** (the tour can walk the proposals; pairs with C1's verified
   comprehension to make mockup review legible).
6. **F2 — GENERATE-FOR-MOCKUPS** (THE SPINE — the gate on the founding promise; lands into a working room
   after 1-5).
7. **G2 — Locus-trail / temporal deixis, scoped** ("the last few you touched").
8. **I4 — RHM-annotate verb** (one whitelist entry + the consent posture).
9. **D3 — Group roll-up** (a descendant-gather; lowest urgency).
10. **C4 — Cap/pre-digest refinement** (fold in once the feel under real big mockups is measured).

Threaded throughout: **I1/I2/I5** (mode-integration + the anti-parallel guard) hold across the whole
build; **C3** (confirm altitude-shaping is FE-wired) is checked early; consent stays simple (one approve
+ git, `approve_reach` dropped); steal the tour *mechanism* from commodity libraries (Driver.js /
Shepherd.js) — our `ui://` registry already solves their #1 selector-reliability failure.
