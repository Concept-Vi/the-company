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

# ════════ ADDED BY COVERAGE ROUND 1 (2026-06-08) ════════

> **What this section is.** The full-directory COVERAGE ROUND swept eight territories (runtime, canvas,
> substrate, cognition, voice, design, ops, design-corpus) + verified the two big claims against current
> `main`. Every relation that surfaced is appended below as a real two-faced criterion — **never filtered
> out as "out of scope"** (the standing law). Groups continue the existing A–I lettering as **J–N**.
> Refinements that sharpen an *existing* criterion are recorded as `+refine` cross-refs (NOT new parallel
> criteria — that would violate I5 at the document level). Each appended criterion carries its honest
> status target; **none is verified-by-use, so none is ✅.**
>
> **The two verified claims (the frame this round grounds):**
> - **Claim 1 — VERIFIED Y (the organ-realization is real).** This surface IS the vault's *RHM
>   Walkthrough & Review Organ*. The vault organ's own thesis is verbatim Tim's: *"the one organ through
>   which Tim and the system meet … Build-review is its first consumer … built general, not as
>   build-review's UI."* The merge is a **UNION, not a congruence** — the vault contributes load-bearing
>   criteria the GRS set LACKS (the review-queue + origin/status lifecycle, the human go-gate, branching,
>   actionable-WHY, the three-part derived-from bind, `guard()`-actually-wired, modes-drive, and the
>   S1–S7 acceptance scenarios), while the GRS set uniquely owns comprehension-at-altitude (C),
>   generate-for-mockups (F), and scoped temporal deixis (G). The grown criteria below = the union.
> - **Claim 2 — OVER-INFERRED (IAS Phase 0 is NOT a hard prerequisite; it is mostly already-there).**
>   Verified against `main`: the FE is **already F0-modular** (`App.tsx` 338 lines; `regions/` +
>   `components/` dirs; `Review.tsx` 62 lines — NOT a 1660-line monolith; `app.css` carries the F0/F1
>   carve comments as DONE). The **address floor exists** (`design/_system/addresses.json`, `tokens.json`,
>   `design/design-system.css` imported via `main.tsx`; `indicate`/`address_help`/`route_click`/`ui_info`
>   all present in `suite.py`). The genuine still-needed-first remainder is small: **(a)** register
>   `mockup://` in `SCHEMES` (one line — Observed `contracts/address.py:32` `SCHEMES = ("run","cas",
>   "blob","vec","ui","code")`, `mockup` ABSENT), and **(b)** CONFIRM (trace, not assume) that the
>   corpus-import + FORM-gate is actually wired end-to-end (the `app.css` comments assert the import; an
>   end-to-end render trace is not yet done). Everything else the agent called "Phase 0 prerequisite" is
>   on main already.

---

## Group J — The organ-merge: the vault criteria the GRS set lacks (UNION half)

**Claim 1 verified.** These are the vault *RHM Walkthrough & Review Organ* criteria that have **no GRS
equivalent** and must come in for the merged organ to be whole. They are the OUTER CIRCUIT (queue →
present → respond → act → lifecycle); the existing A–I groups are the inner mechanics + the
mockup/comprehension extensions.

### J1 · One review queue, all sources, with `origin` polarity · NET-NEW
- **FUNCTION:** Any source needing Tim surfaces into the **one** inbox as a first-class `review`
  decision, carrying an `origin` field — `responsive` (system-awaiting-Tim) vs `generative` (Tim's
  ideas) — one queue, not two (vault A1/A2). Reuses `inbox.surface` (governance.py:68); `review` is
  added to `governance.POLICY`. Verified by use: a build-loop "needs-Tim" item and a captured idea BOTH
  land in the same queue, distinguishable by `origin`.
- **FORM:** The queue is ONE navigable lane on corpus tokens, with `origin` legible as a visible polarity
  (responsive vs generative), not two parallel inboxes. design-lint pass.
- *Status target:* 🟡 NET-NEW (additive field + POLICY row; reuses the surface primitive). The
  generative-entry (idea-capture) is its own future consumer.

### J2 · A distinct `status` lifecycle field (NEVER overloaded onto `resolved`) · NET-NEW · **bug-guard**
- **FUNCTION:** `inbox → presented → responded → resolved | requeue` is a **separate `status` field**,
  never written into `resolved` (vault A3). Observed hazard on main: `inbox_lanes`/`now`/`is_approved`
  read `resolved is None` (suite.py:777,378; governance.py:95) — so a lifecycle value placed in
  `resolved` would silently DROP the item from the queue. Verified: an item walked through all four
  states stays correctly queued/closed; a `requeue` returns it to `inbox`, never to `resolved`.
- **FORM:** The item's lifecycle state is a visible stage marker (corpus tokens) the operator reads —
  where it is in the circuit. design-lint pass.
- *Status target:* 🟡 NET-NEW (a distinct field + the read-sites updated). This is a **silent-drop guard**
  — verify the `resolved is None` readers are not confused by a lifecycle value.

### J3 · "Next" is a human go-gate (the walk cannot cascade past Tim) · MODERATE
- **FUNCTION:** Each review-node carries a **human-writable `go` input** that only resolves on Tim's
  action; **Next writes it → the node fires** (vault B2). The scheduler already waits on unresolved
  inputs (scheduler.py:49,97) — so each node MUST carry its own gate or the run cascades past the human.
  Verified: a multi-item session holds at item N until Tim advances; it never auto-runs ahead.
- **FORM:** The "Next" affordance reads as the operator's own go-control (corpus tokens), with "item N of
  M" progress visible (vault B4). design-lint pass.
- *Status target:* 🟡 MODERATE (the go-gate per node; the stepper engine + progress already exist —
  A1/A3, `start_session`/`present_current`/`next`). Cross-ref A3 (pace controls).

### J4 · Branching — a verdict routes to a different next item · NET-NEW
- **FUNCTION:** A verdict routes the walk: reject → insert a remediation sub-walk; approve → skip ahead
  (vault B5). Observed genuinely net-new on main: today it is one-address-per-node + resolution-only
  (compile.py:51-57); branching needs **per-port addresses + a `gate` node** (vault Guide). Verified
  (vault S4): the next item Tim sees depends on his verdict, not a fixed order; the not-taken branch's
  items never appear.
- **FORM:** The walk's path is legible — the operator sees the branch taken (a relational/temporal
  shape), not a hidden re-order. design-critic pass.
- *Status target:* 🟡 NET-NEW (per-port addresses + a `gate` node). The highest-lift vault addition.

### J5 · Record the verdict + WHY; the WHY is itself actionable · MODERATE
- **FUNCTION:** approve/reject/comment/skip/decide(option) + the WHY are recorded, tied to the item +
  session position (vault D2 — reuses `resolve_surfaced` suite.py:1153; **skip → back to inbox, not
  resolved**). A "needs-change" WHY becomes **directly a new criterion/edit**, not only twin-training
  (vault D4). Resolve stays operator-only (vault D3, governance.py:82-84 — invariant). Verified: a
  rejected item's WHY surfaces as a new queue item the loop can pick up.
- **FORM:** The verdict + WHY present as a recorded mark at the item (corpus tokens), replayable; the
  WHY-becomes-work is a visible new queue entry. design-lint pass.
- *Status target:* 🟡 MODERATE (`resolve_surfaced` exists; add comment/skip + session tagging + the
  WHY→criterion path). Cross-ref D1/D2/E2.

### J6 · The channel back — system acts, provably DERIVED-FROM the verdict (three-part bind) · MODERATE
- **FUNCTION:** Recorded verdicts flow to the loop from `events_since(seq)` filtered to `resolve` events
  — no human relay (vault E1). The criterion-write is a governed action REQUIRING `derived_from = the
  resolve event's seq`, and **refuses unless that event is `kind=resolve · choice=approve ·
  surfaced==this sid`** (the three-part structural bind, vault E2 — bind to `seq` not `sid`). Verified
  (vault S6, adversarial): a write with no `derived_from` refuses; a verdict for X used to authorize Y
  refuses; re-resolving (new `seq`) binds to the new event, not the stale one.
- **FORM:** The derived-from provenance is a visible chain at the dispatched change (corpus tokens) — the
  operator sees WHICH verdict authorized WHICH act. design-lint pass.
- *Status target:* 🟡 MODERATE (mirrors `apply_node`→`is_approved`→`GovernanceError` suite.py:880-882;
  the wire E1 is verified by the prior build). This is the **safety invariant** — extends E1/E2.

### J7 · `guard()`/POLICY actually WIRED into the production apply paths · NET-NEW
- **FUNCTION:** Routing goes through `guard()` by consequence/reversibility — **not** hardcoded class
  strings — wired into the apply paths + AUTO mutators (vault G1). Observed on main: `guard()` is
  **never called today** — the real CONFIRM gate is hand-rolled in `apply_*` (suite.py:880-882). The two
  load-bearing principles hold: **deterministic gates, not confidence** (the twin never decides
  permissions); **all in scope**. Verified (vault S5): the same item routes identically twice
  (deterministic), the RHM can SAY why in consequence terms, and no confidence value appears in the path.
- **FORM:** The gate's decision is explainable in plain consequence language ("acted because reversible /
  asking because irreversible") on corpus tokens — never a confidence number. design-critic pass.
- *Status target:* 🟡 NET-NEW (wire the existing `guard()`/POLICY into the hand-rolled gate sites). A
  foundation criterion (vault build-order puts G1 first).

### J8 · The walkthrough/decide-for-me MODES drive the engine · MODERATE
- **FUNCTION:** Entering `walkthrough` mode actually starts/steers the session (emitting `show ui://…`
  sequences); `decide-for-me` acts on what `posture(class)==AUTO` permits (reversible) and surfaces the
  rest — no confidence field (vault G2/G3/G4). Observed: `walkthrough` mode exists (suite.py:1278) and
  `start_walkthrough` binds dial→organ (suite.py:6287); the gap is the modes *behaviourally* driving
  present-vs-act. Verified: switching mode reconfigures present-vs-act and persists. Cross-ref I1 (the
  surface IS the walkthrough mode).
- **FORM:** The mode is the dial; entering it visibly shifts the surface (I1 FORM). design-lint pass.
- *Status target:* 🟡 MODERATE (mode rows exist; the drive-behaviour is the lift). Extends I1.

### J9 · The S1–S7 by-use acceptance scenarios are the organ's gate · cross-cutting
- **FUNCTION:** A criterion is green only inside a passing multi-part SCENARIO (the seams, not the
  units): **S1** the first real walk end-to-end (voice + look, four verdict kinds, the loop acts);
  **S2** an unscripted question resolving to a MIX of targets incl. non-node chrome (the keystone);
  **S3** a newly-grown component is walkable the instant it registers (zero new walk code); **S4**
  branching (J4); **S5** deterministic governance, no confidence (J7); **S6** the no-bypass /
  derived-from integrity, adversarial (J6); **S7** never a dead end (voice→text fallback, `coa`-error→raw
  payload, device-switch resume). Verified by USE per scenario on the live canvas, Tim-driven (browser +
  voice + the adversarial S6). 
- **FORM:** N/A as a single screen — these are the cross-circuit proofs; each scenario's FORM is the
  FORM of the criteria it exercises.
- *Status target:* 🔴 needs-tim for S1/S5/S7 feel-and-drive legs; 🟡 for the mechanically-checkable
  scenarios (S2/S3/S4/S6). This is the **acceptance suite** the merged organ checks against.

---

## Group K — Cognition-cast enrichment (the guided turn can think richer)

**The posture is now DECIDED (Round 2): enriched by default.** Verified on main: all six roles
(focus/recall/ground/connect/check/voice) carry `mode_scope: {"listening"}` ONLY — `walkthrough` is
absent (roles/*.py). So `cast_for_mode("walkthrough")` returns `[]` today: the enrichment swarm is idle
during guided turns. Round 2 decision: the guided turn SHOULD fire the swarm (a right-hand-man reviewing
a screen must have memory of past decisions about it). Posture is CONFIGURABLE — see K3. The decision
changes K1's status from a posture-gate to a mechanism criterion.

### K1 · The walkthrough-cast activation — add `"walkthrough"` to the six role mode_scopes · MODERATE
*(Round 2 refine: posture RESOLVED → mechanism criterion; 🔴 needs-tim on posture is retired.)*
- **FUNCTION:** Add `"walkthrough"` to the `mode_scope` of the six roles — focus, recall, ground,
  connect, check, voice (six one-line edits in roles/*.py). With this, `cast_for_mode("walkthrough")`
  returns the full swarm for guided turns instead of `[]`. Calibrated payoff (Observed): all six fire
  concurrently + light up the CognitionView; recall + ground INJECT into Part 2 immediately via the
  canonical `INJECTION_RULE` (suite.py:5402-5409) — this is ~80% of an enriched guided turn on day 1
  of K1, zero additional code. Connect/check/voice fire and write to `run://<turn>/<role>` but their
  outputs go dormant until K4 (their rules are descriptive, not AST-shaped — suite.py:5397-5399;
  voice's rule is `kind:"route"` — the ~20%). The `cast_posture` config axis (K3) gates whether the
  swarm fires at all — default `"enriched"` means K1 is active unless the operator flips the axis.
  Verified: a guided turn shows a populated cast in `cognition_info()` and recall/ground shape the reply.
- **FORM:** The cast's concurrent thinking is visible (the CognitionView Pulse/River beside the guided
  reply — see canvas U-thread). design-lint pass when populated.
- *Status target:* 🟡 MODERATE (six one-line edits once K3 axis exists). Cross-ref K3 (axis),
  K4 (injection completion).

### K2 · A `screen_reader` cognition role for guided/mockup stops · NET-NEW
- **FUNCTION:** Move the "read this screen FOR the operator" logic out of the ad-hoc `_chat_context` HTML
  injection (Observed suite.py:2086-2125) into a **declared role** — `screen_reader`/`locus_brief`:
  `input_addresses: (mockup_html, ui_address)`, `output_schema: {summary, zones, focus_point}`,
  `mode_scope: {"walkthrough"}`. **Trigger (a coherence choice, see UNIFICATION-MAP D-IV):** EITHER
  within-the-turn (a concurrent Part-0 when Tim asks at the stop — no new activation model, rides
  per-turn) OR on-stop-ARRIVAL (the brief is ready the moment Tim lands, before he asks — a
  navigation-triggered enrichment, which would use a non-turn activation context). Default lean:
  within-the-turn Part-0 (no new context); arrival-enrichment is the richer option Tim can pick. Verified:
  at a mockup stop the role fires, produces a structured brief, and Part 1 builds the narration from it.
- **FORM:** No new operator surface — judged via C1/F1 (the mockup explains itself); but the role is now
  visible in `cognition_info()` (the operator can SEE it firing at each stop). design-lint pass.
- *Status target:* 🟡 NET-NEW (one role file). Benefits: visible in CognitionView, re-bindable to a
  faster/embed model, and it IS the C4 14KB pre-digest done properly (html→structured brief via a model).
  Composes with `check` (check reads `screen_reader.summary` vs `ground.note`). Cross-ref C1/C4/F1.

---

# ════════ ADDED/REFINED BY ROUND 2 (2026-06-08) ════════

> **What this section is.** Round 2 was a targeted follow-up (three bounded scopes: injection-state +
> config axis; FORM-gate wiring; second-consumer generality). It adds K3, K4, M3, and Group O to the
> criteria; refines K1 in place (posture resolved → mechanism). The net-new build remainder is UNCHANGED
> by these additions — K3/K4 are config and injection-completion (both within the already-scoped cognition
> lane); M3 is a one-file pre-commit hook; Group O names the organ's general shape and deferred
> consumers, which the build was already targeting. Round 2 reframes and sharpens; it does not grow the
> scope.
>
> **Evidence convention.** Same standing law. *Observed(file:line)* = read directly on `main`.
> *Inferred* = pattern-matched, NOT execution-verified. Round 2 findings are at
> `findings/round2/{injection-and-config,form-gate,second-consumer}.md`.

---

### K3 · The `cast_posture` config axis — MODE_REGISTRY + `rhm_config` slot + `fireable` filter · MODERATE
*(Round 2 addition: the cast posture is a configurable axis, not a hardwired choice.)*
- **FUNCTION:** Declare `cast_posture` as a per-mode/per-subtype axis in MODE_REGISTRY (sibling to
  `grain`, `shape`, `stage`, `brain_config`), following the same subtype-override pattern the `budget`
  axis already uses (e.g. `show-me` overrides `budget` from 6000→8000 — Observed suite.py:1284-1286).
  Declaration:
  ```python
  "walkthrough": {
      ...
      "cast_posture": "enriched",       # "enriched" | "lean" | "off"
      "subtypes": {
          "guided":  {"cast_posture": "enriched"},
          "show-me": {"cast_posture": "lean"},   # show-me drives; lighter cast
      },
      ...
  }
  ```
  Add a `cast_posture` slot to `rhm_config()` (default `"enriched"`) and to `set_rhm_config`'s
  whitelist — following the `MODE_AUTODETECT`/`brain_knobs` precedent (Observed suite.py:1821,
  1807-1836). Read the posture once in `chat_parts()` at the `fireable` derivation (a one-place filter,
  Observed suite.py:5333-5340 — no other code changes):
  ```python
  posture = self.rhm_config().get("cast_posture", "enriched")
  if posture == "off":    fireable = []
  elif posture == "lean": fireable = [r for r in cast if r.id in ("recall", "ground") and ...]
  # "enriched" = all fireable (current behavior after K1)
  ```
  `"enriched"` = full swarm (K1 active). `"lean"` = recall + ground only. `"off"` = empty cast
  (today's default before K1). Runtime-tunable via `set_rhm_config` without a redeploy. **Net-new
  work:** (a) `cast_posture` axis in MODE_REGISTRY row + subtypes, (b) slot in
  `rhm_config()`/`set_rhm_config()`, (c) posture filter in `chat_parts()` — all small;
  (d) thread subtype resolution into `cast_for_mode()` (Observed gap: `cast_for_mode()` keys on
  top-level mode string only, Observed roles.py:210-214 — net-new/moderate, only needed if
  guided vs show-me want different casts out of the box). Verified: setting `cast_posture="lean"` via
  `set_rhm_config` results in only recall/ground firing on the next guided turn.
- **FORM:** The axis is surfaceable via the configure verb (the same path that sets brain_knobs
  today — corpus tokens, settings surface). The operator can see the current posture and change it.
  design-lint pass on the settings surface.
- *Status target:* 🟡 MODERATE (precedent clear; (a)–(c) are small; (d) is the moderate net-new if
  per-subtype posture is needed immediately). Cross-ref K1 (the mechanism this axis governs), K4
  (injection completion).

### K4 · Injection completion — promote connect/check/voice rules to AST with `destination="inject"` · NET-NEW
*(Round 2 addition: the ~20% G3/G4 follow-on, a separate bounded criterion.)*
- **FUNCTION:** Connect, check, and voice carry **descriptive** `{id, reads, effect, kind}` rule dicts,
  not AST-shaped rules (Observed from roles/connect.py, roles/check.py, roles/voice.py — confirmed
  injection-and-config §3). These are explicitly skipped at the `chat_parts()` fireable-rule loop
  (suite.py:5397-5399: *"descriptive {id,reads,effect,kind} role entries are NOT AST rules → skipped"*).
  Voice's rule additionally carries `kind:"route"` — not `destination:"inject"` — so even if promoted to
  AST it would not reach the inject path without also setting the destination.
  To make connect/check/voice OUTPUTS land in Part 2: author AST rules with `when` op-trees and
  `destination="inject"` for each role; the existing `chat_parts()` loop then picks them up with no
  further engine changes (Observed suite.py:5419-5438 — the consume leg is already general). **Bound:**
  the current `inject_text` slot is a scalar (suite.py:5419 — assigns, not appends); when 2+ roles have
  inject rules, successive fires overwrite. Accumulation logic (appending multiple injections into one
  coherent context block) is also net-new and must ship alongside the AST rule promotion — otherwise only
  the last inject-rule to fire contributes to Part 2. Verified: after authoring the AST rules, a guided
  turn's Part 2 user content contains structured outputs from connect + check (plus recall/ground from K1)
  as a single coherent injected block.
- **FORM:** The richer injected context produces Part 2 replies that visibly draw on connection and
  check outputs (references past design decisions, flags live inconsistencies) — judged via 🔴 needs-tim
  on the felt altitude improvement.
- *Status target:* 🟡 NET-NEW (three AST rule blocks + accumulation logic). Depends on K1 (swarm fires)
  and K3 (posture is enriched). Cross-ref K1, K3, and the G3/G4 designators in the Implementation Guide.

---

## Group L — Substrate + grammar one-liners (the coordinate system stays self-consistent)

### L1 · Register `mockup://` in the address SCHEMES · NET-NEW · prerequisite-ish
- **FUNCTION:** Add `mockup` to `SCHEMES` (Observed `contracts/address.py:32` — today
  `("run","cas","blob","vec","ui","code")`, `mockup` ABSENT though it is already in operational use in
  suite.py). The docstring states adding a scheme is "purely additive" (address.py:16); schema-ver stays
  unchanged. Verified: `scheme("mockup://A2-canvas-desktop.html")` returns `"mockup"` truthfully (it
  doesn't today), which the mockup-aware stop (F1) + generate-for-mockups (F2) depend on. Optionally also
  add `doc`/`area` (forward — enables RHM walking vault notes as tour stops; NOT a prerequisite).
- **FORM:** N/A (substrate) — verified structurally (the grammar is self-describing of the full build
  vocabulary). The form-level expression is that every address the surface uses parses truthfully.
- *Status target:* 🟡 NET-NEW (one line). **Lands before F1/F2 dispatch.** Cross-ref F1/F2.

---

## Group M — The live coherence oracle (drift detection becomes operator-facing) · NET-NEW

### M1 · The drift mechanisms surface as a live coherence oracle in the walk · NET-NEW
- **FUNCTION:** The existing coherence mechanisms — `design/_system/check.py` + `refcheck.py` +
  `symbols.py` + `codeedges.py` (all Observed present on main) — become a LIVE coherence oracle the
  walkthrough can run on-demand and surface as actionable findings (the RHM can SAY "this mockup uses
  ad-hoc colours / references a dead address" and SURFACE it as a queue item). Verified: running the
  oracle mid-walk on a mockup yields findings the RHM narrates + can turn into a `review` item.
- **FORM:** Findings present as a navigable coherence checklist at the locus (corpus tokens) — a
  relational view of "what's consistent / what drifted," not a raw report dump. design-critic pass.
- *Status target:* 🟡 NET-NEW (wire the existing check/refcheck/symbols/codeedges into the walk as an
  on-demand oracle + the finding→queue path). Cross-ref J5 (WHY→work), the design/ops companions.

### M2 · A verify-gate WRAPS guide-generated builds (verify-by-use before commit) · NET-NEW
- **FUNCTION:** A new gate — `verify_guide_output(generated_graph, test_suite_ref)` — asserts a
  guide-initiated build (operator clicks generate → RHM autonomously builds) produces a committed graph
  that the suite can verify was NOT fabricated, BEFORE git commit. Observed on main: the standing
  all-green gate exists (`tests/suite_health_acceptance.py`, shelled via `company suites` —
  ops/cli/app.py:135-144) but it runs acceptance suites over the WHOLE codebase, NOT the
  generated-output-only verify-by-use (`verify_build`/`verify_guide_output` do NOT exist in suite.py).
  Reuses the gate's subprocess + TEMP-store isolation pattern (app.py:133-149) over the generated graph.
  Verified: a generate-for-mockups (F2) or batch (E2) build runs through the gate and only a verified
  output reaches commit. Cross-ref ops U2/U3/U4 (pre-guide capability + address-reachability + resident
  lints) as companion gates.
- **FORM:** The gate's pass/fail presents as a visible verification mark on the generated change (corpus
  tokens) — the operator SEES it was proven, not just "built." design-lint pass.
- *Status target:* 🟡 NET-NEW (the verify-gate + the bridge↔`company` shared interface). This operationalises
  "verify before claiming" for autonomous builds. Cross-ref E2/F2/J6.

### M3 · Tracked pre-commit hook — FORM gate fires on ALL canvas commits, not only wire-routed ones · NET-NEW
*(Round 2 addition: the gate-gap finding — FE written outside dispatch_decision has no FORM check.)*
- **FUNCTION:** The existing `_design_critic` (suite.py:7515) fires UNCONDITIONALLY inside
  `dispatch_decision` for all wire-routed canvas builds — Observed. The gap: FE written by any path
  bypassing `dispatch_decision` (a raw worktree session, a direct agent edit) commits canvas files
  never checked by design-lint. Proof of gap: `.git/hooks/` contains only `.sample` files (Observed,
  none active); `canvas/app/package.json` has no lint step (Observed :5). Existing off-token debt:
  `canvas/app/src/app.css:1426` and `app.css:1515` both carry `#fff` — Verified by executing
  `python3 design/_system/check.py --target canvas/app/src` (2 off-token literals, 0 bespoke). These
  are cleanup candidates (`var(--white)` or `var(--surface)` likely correct).
  Close the gap with a **tracked** `hooks/pre-commit` (not `.git/hooks/` — tracked, version-controlled,
  ephemeral `.git/` side-stepped) that: lints only STAGED canvas `.tsx`/`.css` files per-file, not the
  whole tree (mirrors the wire's constraint at suite.py:7219 — *"Lint only the surface files THIS
  build changed — a clean change must not be gated by pre-existing dirt elsewhere"*); exits non-zero on
  any off-token literal; fails-safe if the design-lint script is missing. Wire via
  `git config core.hooksPath hooks` (persists in `.git/config`). Add one line to root `AGENTS.md`:
  *"After cloning, run `git config core.hooksPath hooks` to activate the FORM gate."* This is the
  AI-native equivalent of a CI gate: self-describing, traceable, picked up by fresh sessions that read
  `AGENTS.md`. Verified: staging a `.tsx` file with an off-token literal, committing, triggers the
  hook and the commit is refused; staging a clean file succeeds.
- **FORM:** When the hook fires, the rejection message names the offending file:line and the literal —
  actionable on corpus tokens (plain-language `FORM pre-commit: canvas/app/src/app.css:1426 #fff —
  replace with var(--…)` style). Not a silent exit-1 with no message. design-lint pass (the error
  message itself reads like the design system wants it to).
- *Status target:* 🟡 NET-NEW (hook text is proposed in round-2 finding but NOT yet written to disk,
  NOT yet `chmod +x`, NOT yet end-to-end tested by a real `git commit` with a staged off-token file —
  hook code-complete-proposed, not code-complete-tested). Cross-ref M2 (verify-gate family);
  `app.css:1426,1515` are the two named cleanup items that unblock the pre-existing-dirt constraint.

---

## Group N — Refinements to EXISTING criteria (sharpen, do NOT parallel — the I5 doc-level guard)

> These coverage threads already have a home in A–I. Recorded here as **`+refine`** so the loop sharpens
> the existing criterion with the new evidence — it must **NOT** create a second parallel criterion.

- **N·B1 (+refine text-streaming):** Canvas companion gives the EXACT FE wiring for B1 — add
  `api.chatStream(m, focus)` → `fetch('/api/chat/stream', …)` returning a raw Response; in `sendChat`
  branch to open the stream and append parts (mirror the voice NDJSON reader at
  useAppController.ts:1900). Observed: `api.chat()` is a full-wait POST (api.ts:97); no SSE/NDJSON text
  consumer exists yet. This activates the already-built backend `chat_parts()` generator. **Sharpens B1;
  no new criterion.**
- **N·G2 (+refine temporal deixis):** Canvas companion gives the journey-store SEED path for G2 —
  auto-emit `navigate` events on `indicate()` calls (not only on record) → a `recent_loci()` reader →
  inject the trail into chat context; the existing `journeyStep` API call pattern is the template, lives
  entirely in the controller. **Sharpens G2; no new criterion.**
- **N·I3 (+refine walkthrough↔chat composition):** Canvas companion confirms the exact gap + fix —
  advancing a guide step does NOT call `indicate(session.raw?.guide_address)`, so the locus stays stale;
  after useAppController.ts:1683 (`const tgt = session.raw?.ui_target`) add the `indicate(...)` call so
  every guide stop auto-grounds the chat. **Sharpens I3 (~5 FE lines); no new criterion.**
- **N·H1 (+refine voice focus-passthrough):** Voice companion confirms the one-line fix — bridge.py:848
  calls `chat_parts` with NO focus; `chat_parts` already accepts focus (suite.py:5264). Pass
  `focus.selected` through so voice is locus-aware. **Sharpens H1; lands in the same pass as N·I3.**
- **N·B3 (+refine streaming cancel):** Voice companion confirms the cancel primitive — the
  `gone[0]`/`client_gone` SELECT+MSG_PEEK barge-in pattern (bridge.py:780-793) is generic and reusable
  for the text-streaming cancel path. **Sharpens B3; reuses the voice primitive.**
### Forward-notes — surfaced threads that get a HOME (never filtered), low-urgency / explicitly-deferred

> The "never filter" law: every thread the coverage surfaced gets a criterion OR an explicit forward-note.
> These are real but tangential or low-urgency; recorded so none is silently dropped.

- **FWD·doc/area-scheme (substrate TOUCH):** Optionally add `doc`/`area` to SCHEMES (enables the RHM
  walking vault notes / directory-areas as tour stops). FORWARD design point, NOT a prerequisite —
  carried inside L1.
- **FWD·cognition-ADDRESS_KINDS (substrate UNIFY #2):** `ui://cognition/<turn>` addresses fail
  `validate_address_record`'s kind check — `cognition` is missing from `ADDRESS_KINDS`
  (contracts/cognition_info.py). Needed only IF annotations are placed at cognition loci. One-line
  additive fix; deferred until that path is exercised.
- **FWD·MCP-annotate-verbs (substrate UNIFY #5):** The agent (MCP) face has no `AnnotateAddress`/`ChatsAt`
  verb-pair — only the HTTP bridge does. If the agent face is later used for automated reasoning over
  annotations, expose the same store primitives through both faces (one source). Tangential to the human
  surface; deferred, not dropped.
- **FWD·resolver-Protocol-width (substrate TOUCH #5 / UNIFY #4):** `contracts/resolver.py`'s Protocol is
  narrower than the actual `FsStore` contract (`append_annotation`/`chats_for`/`save_session`/
  `save_journey`/`put_vector` absent). Flag for the future Supabase backend swap; not a build-blocker now.
- **FWD·NodeType-howto (substrate UNIFY #7):** D1 affordance text lives on `UnionAddressRecord` but not on
  `NodeType`, so live-app NODE narration is always LLM-generated. A corpus `howto` on NodeType would make
  node narration corpus-grounded (model-free) like element narration. Quality refinement; deferred.
- **FWD·index-auto-rebuild (substrate UNIFY #8):** The semantic-R2 index has a staleness check but no
  auto-rebuild trigger; a boot-time stale-check + async rebuild would make semantic R2 live without manual
  steps. Quality-of-life; deferred.
- **FWD·dynamic-review-FORM (design UNIFY #2/#3):** The walkthrough should read `component-inventory.json`
  + the per-view `surface-specs` to BUILD THE REVIEW FORM DYNAMICALLY — marking `run://` vs `ui://`
  addresses, absent-component gaps ("view correct, build when ready"), and orphan addresses. This extends
  M1 (the coherence oracle reads the same registries); recorded as M1's inventory/coverage dimension, not
  a separate criterion.

- **N·I1 (+refine the role+activation-context framing):** Runtime companion frames the surface as a
  COMPOSITION — a role fired under an activation context, "zero new execution model." Verified-against-main
  nuance: the guided dialogue already fires under the **existing `per-turn` activation context**
  (chat_parts), NOT a missing non-turn context; `walkthrough` is already a MODE (suite.py:1278) bound via
  `start_walkthrough` (suite.py:6287). So the runtime companion's "add a `guided-review` ACTIVATION_CONTEXTS
  row + a `roles/guided_review.py` file" is **one framing that partly conflicts with the GRS-grounded
  view** — the engine already exists; what's actually missing is the walkthrough CAST (Group K) and the FE
  show-me lane (H2). **Recorded as a +refine note on I1, NOT adopted as a build-a-new-role criterion**
  (would violate I5 — the engine is not re-built). The honest net is: NO new activation context is needed
  for the guided dialogue's per-turn chat; a non-turn context would only be needed if the RHM is to walk
  *autonomously* (system-initiated) — a forward decision, see UNIFICATION-MAP.

---

## Group O — The general human-interaction organ and its 7 consumers
*(Round 2 addition: the second-consumer analysis confirms the organ is already general. Build-review is
INSTANCE 1. The 6 other consumers are near-free framing-branches, deferred post-instance-1.)*

**The organ IS already general.** The sequencer (`start_session`, `next`, `present_current`), the
cursor + go-gate graph, the inbox queue (`inbox.list()` filtered `resolved is None`), addressed markup
(`ui_target` stamped in `raw`, `resolveUiTarget` on FE drives view), the resolve path
(`resolve_surfaced(sid, choice, reason)`), and the mode dial (`set_mode("walkthrough")`) are all
SHARED across every consumer — Observed in second-consumer §5 (suite.py). Per-consumer variation is
confined to one place: the framing branch in `present_current`. The rest needs NO change per consumer.

### O1 · The sequencer + resolve path are shared, verified as general · READY / Observed
- **FUNCTION:** The shared organ (start_session / next / present_current / go-gate graph / cursor /
  ui_target-markup / resolve_surfaced / mode-dial) works for ANY inbox item type — the `present_current`
  branch dispatches on `action` to handle each consumer differently; the stepper, cursor,
  gate-writes, and resolve path require no modification per consumer. Verified by: build-review
  (instance-1) already exercises every shared leg; adding a new consumer requires only a new branch
  case in `present_current` + a resolve handler for its specific post-approval effect (Observed
  second-consumer §7: one branch + one handler per consumer, no new organ). Cross-ref A1/A3/J3 (the
  shared mechanics already criterionised there).
- **FORM:** N/A as a discrete screen — this is structural confirmation. Its FORM-face is expressed as
  every consumer presenting through the same guided overlay, corpus tokens, spotlight idiom (the
  general organ surfaces every consumer identically to the operator's eye).
- *Status target:* 🟡 Observed for the shared legs; Inferred for the per-consumer branch generality
  (the branches do not exist in code yet — second-consumer §198-199 marks the per-consumer framing
  as Inferred/design). Cross-ref O2.

### O2 · The 7 consumers — instance-1 built, the other 6 are near-free framing-branches · cross-cutting
- **FUNCTION (the definitive consumer map):** The organ serves 7 named consumers; build-review is
  instance-1; the others are each ONE branch case in `present_current` + one resolve handler, deferred
  to post-instance-1:

  | # | Consumer | Action class | Framing in `present_current` | Resolve effect |
  |---|---|---|---|---|
  | 1 | **Build Review** (instance-1) | `"review"`, `intent="build"` | COA (model-dependent up-translate) | `dispatch_decision` fires on approve |
  | 2 | **Deferred Offers** | `"deferred_offer"` | offer name + options direct (no COA — it's already commander-altitude) | `revive_offer(sid)` → ProposeAffordance re-opens |
  | 3 | **Node Results** | `"result"` | COA or raw (COA degrades gracefully; probably fine for value-choice results) | acknowledge (approve) / dismiss (reject); no dispatch |
  | 4 | **Questions** | `"question"` | question text direct (raw) | operator's free-text answer injected back via `resolve_surfaced(sid, choice="custom", reason=<answer>)` |
  | 5 | **Authoring** | `"code_build"`,`"role_build"`,`"role_delete"`,`"ui_panel"`,`"ui_extension"` | asset content direct (code/panel/spec) | `apply_surfaced` (already class-routing, no change) |
  | 6 | **Governance Escalations** | addr-tier I4 class | COA or raw | approve/reject governance consent |
  | 7 | **System-Initiated Tour** | `ui://` element addresses (start_guide) | corpus how-to, model-free | already built and working — no delta |

  Verified (instance-1): build-review exercises the full organ end-to-end. Inferred (consumers 2–6):
  the per-consumer `present_current` branch strategy is design-level; the branches do not yet exist
  in code (second-consumer §198-199). Consumer 7 is ✅ working (start_guide already built — second-
  consumer §4). The near-free claim rests on the shared organ requiring no change; only the
  branch + handler vary.
- **FORM:** Every consumer presents through the same guided overlay on corpus tokens — the organ's
  general shape is consistent regardless of which consumer is active. The action-class label (e.g.
  "Build Intent" / "Deferred Offer" / "Question") is a legible type marker in the overlay.
  design-lint pass per consumer as built.
- *Status target:* ✅ consumer 7 (start_guide); 🟡 consumer 1 (instance-1, the current build target);
  🟡 Inferred for consumers 2–6 (design-level; post-instance-1). Cross-ref J1 (queue + origin),
  J2 (lifecycle), J3 (go-gate), J5 (record verdict + WHY).

### O3 · INSTANCE-1-ONLY machinery — NOT generalized into the organ · INVARIANT
- **FUNCTION (the anti-bleed guard):** These mechanisms are specific to the build-review consumer
  (instance-1) and MUST NOT be built into the shared organ — generalising them would introduce an
  I5-class parallel-system. Per second-consumer §6, these are instance-1-only:
  1. **`dispatch_decision` wired to resolve** — only build-intents dispatch autonomous implementation
     on approve; all other consumers use class-specific handlers (apply / answer / acknowledge / revive).
  2. **`surface_build_intent` / scope declaration** — the scope + `consequence_class` machinery is
     build-specific.
  3. **`decision_build` consequence class** — the governance class tied to the build wire.
  4. **Build-gate + scope-diff at dispatch time (DENY-ALL for empty scope)** — the safety property of
     the build wire; not a general walkthrough concern.
  5. **`surface_intent_at` as the comment→intent entry seam (L1)** — the addressed-feedback-to-wire
     path is build-specific.
  The invariant: the loop checks that no implementation of a new consumer bleeds any of these five
  into the shared sequencer/resolver path. Verified structurally at build-time (grep-confirm that
  `dispatch_decision` is never called from the shared `present_current` branch logic, only from the
  build-review resolve handler).
- **FORM:** N/A as a screen — a structural invariant held by the anti-parallel system guard (I5).
  Cross-ref I5 (the anti-parallel guard); all consumers in O2.
- *Status target:* 🟡 (standing invariant the loop re-checks when a new consumer is added).

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

### Coverage-round-1 additions slotted into the order

The J–N groups are dependency-placed (the refinements N· fold into the steps that own them):

- **L1 (`mockup://` SCHEMES one-liner)** — lands BEFORE F1/F2 dispatch (prerequisite-ish).
- **J7 (`guard()`/POLICY wired) → J1/J2 (queue + origin/status lifecycle) → J5/J6 (record + derived-from
  bind)** — the OUTER CIRCUIT foundation, vault build-order (G1 first). These can build in parallel with
  the inner B1/H2 lane (file-disjoint: governance/queue vs FE).
- **N·B1, N·G2, N·I3, N·H1, N·B3** — fold into their owners (B1, G2, I3, H1, B3) as the exact wiring; no
  separate scheduling.
- **J3 (go-gate) + J8 (modes-drive)** — fold into H2 (the FE show-me lane) + I1 (mode-integration).
- **J4 (branching)** — net-new, after the linear walk works (post-H2/E2).
- **M1 (coherence oracle) + M2 (verify-gate wraps generated builds)** — M2 lands with E2/F2 (it gates
  what they dispatch); M1 is a quality-of-review addition, low urgency.
- **K1 (cast posture)** *(Round 2: posture DECIDED enriched, K1 is now a build step)* — six one-line
  mode_scope edits; depends on K3 axis existing first. **K2 (screen_reader role)** — can build once
  K1 is active (or independently as the C4 pre-digest).
- **J9 (S1–S7 scenarios)** — the standing acceptance suite the loop checks every criterion against.

### Coverage-round-2 additions slotted into the order

Round 2 additions are dependency-placed; they do NOT reorder the existing sequence:

- **M3 (tracked pre-commit hook + `core.hooksPath`)** — lands EARLY (file-disjoint from the main build
  lanes; blocks no other criterion). The 2 existing `#fff` literals in `app.css:1426,1515` are named
  cleanup items; fix them before or alongside the hook so the whole-tree scan is clean for future
  reference (though the hook lints staged-only, so they do not gate today's commits).
- **K3 (`cast_posture` axis in MODE_REGISTRY + `rhm_config` slot + `fireable` filter)** — lands BEFORE
  K1 (the axis is the prerequisite for K1 to behave correctly). Items (a)–(c) small; (d) per-subtype
  threading moderate, needed if guided vs show-me want different cast defaults immediately.
- **K4 (injection completion: AST rules + accumulation logic)** — lands AFTER K1 + K3 are active.
  Delivers the ~20% G3/G4 payoff (connect/check/voice outputs fold into Part 2). Cross-ref the
  G3/G4 designators in the Implementation Guide.
- **O1/O2/O3 (general organ + 7 consumers)** — these are structural recognition criteria; O1/O3 are
  invariants the loop re-checks throughout; O2 consumers 2–6 land AFTER instance-1 (build-review) is
  proven working. Consumer 7 (system-tour) is already ✅.

---
## POST-COORDINATION RE-SCOPE (2026-06-09) — what's MINE vs consumed/gated, per the 3-fork split
This loop-prep was written BEFORE the three sessions coordinated. The split (WORK-SPLIT § PROTOCOL) re-owns
several criteria — the loop builds ONLY my-lane criteria and CONSUMES the rest, never rebuilds them:
- **CONSUME cognition's C (don't build the engine):** K1 walkthrough cast (+mode_scope on 6 roles), K2
  screen_reader role, K4 injection-completion → I ADD my roles ON cognition's C seam AFTER C releases (claim
  roles/ then); HOLD cognition.py/roles.py until released.
- **DECLARE only (cognition's A serves):** K3 cast_posture → I declare the MODE_REGISTRY row; A serves it.
- **HANDED to cognition's A:** L1 mockup:// scheme + the studio-suite-mockup-focus.patch → cognition's A
  window. Removed from my build.
- **UNIFIED into coherence's shared gate suite:** M3 FORM pre-commit hook → contribute the FORM-lint to the ONE
  shared suite; no separate hook.
- **COHERENCE's (cross-ref, don't build):** M1 coherence-oracle, M2 verify-gate-wraps-generated-builds, the
  system-wide gates → coherence's detectors + the convergence round.
- **MINE to build (my lane):** the operator surface + FE (show-me lane, Review/StudioKit, useAppController,
  App.tsx, api.ts), the wire/generate-for-mockups, my surface's bridge routes, the voice focus-passthrough fix,
  the cast_posture DECLARATION, + my roles-on-C-seam (after C). The FE halves of A/B/D/E/H + F.
READINESS: build only after this re-scope + a posted "loop-prep re-scoped + grounded + ready" (§ PROTOCOL item 11).

---
## RE-SCOPE (2026-06-09, Tim): generate-for-mockups is AUTONOMOUS + REGISTRY-DRIVEN
Tim: "it shouldn't need me in the loop to build it, and it should be made so that it's easy to reconfigure and update."
- **AUTONOMOUS-buildable** — REMOVE the earlier "needs Tim / focused-round-only" gate. The make-or-break builds like any lane; safety = git-revert (Tim's simple-consent model), not Tim-in-the-build-loop. (See [[feedback-no-needs-tim-gating]].)
- **REGISTRY-DRIVEN / reconfigurable** — the generate behavior is DECLARED DATA, not hardcoded: a `generate-config` registry carrying {prompt/instruction template · model/agent · plan-vs-apply default · routing (mockup-edit vs live build-intent) · scope rule}. Changing how generate works = editing the config, no code change (no-hardcoding law).
- **The engine core (file-disjoint, build now):** a generate-config registry (NEW declared data) + a dispatcher that reads config + a mockup's captured feedback (/api/mockup-feedback, already built) → builds the instruction → calls implement.py dispatch_decision (plan-safe-by-default) → on apply, commits (git-revertible). REUSE dispatch_decision (the claude -p spawner) — no parallel wire.
- **Follow-on (after B1 releases bridge.py):** the thin /api/<generate> trigger route (bridge.py) + the FE "generate" button. Sequenced behind B1's bridge.py claim — NOT behind Tim.
