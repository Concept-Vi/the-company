# Implementation Guide — The Live, Guided, Right-Hand-Man Review Surface

> **HOW to build each criterion.** Loop-prep companion to `Completion Criteria.md` (the bar) and the
> grounded Research Synthesis `GUIDED-REVIEW-SURFACE.md` (the evidence). Read all three together. This
> doc gives, per build area: **Principles** (the why / design reasoning) · **Sequence of operations**
> (runtime order) · **Do's / Don'ts** (with the *because*) · **File paths with roles** · **what it
> PRESERVES** (every other system that keeps working). Pseudocode only where the logic isn't obvious.

> **File-path role legend:** **NEW** = create · **MODIFY** = edit in place (no v2/parallel) · **REUSE-import**
> = call/consume unchanged · **REFERENCE** = read-source / context, do not edit.

---

## Standing principles (apply to every area)

- **One-source / no parallel systems (the join law).** Reuse the existing organ; never build a second
  stepper, a second intent path, a second scoring source, a second mode table. *Because* the Company's
  whole design is relational composition — a parallel system strands work and breaks the circuit. The
  MODE_REGISTRY (suite.py:1220) is the canonical example: 3 old tables are now DERIVED VIEWS of one
  source. Every change here follows that pattern.
- **Registry-is-truth; the shape is DATA, never a mode-name branch.** R2 already consumes the mode's
  `resolution` spec as data (Observed suite.py:3055-3061, the E1 criterion). New behaviour is declared in
  the registry row, not `if mode == "walkthrough"`. *Because* a branch can't be extended by a new
  consumer; a data declaration can.
- **Fail-loud-legible, never silent.** Every gather/dispatch either succeeds or warns + degrades
  legibly (the operator/model is TOLD). *Because* a silent no-op or a fabricated scope lies, and Tim's
  no-silent-failure law forbids it. The 14KB truncation already does this (suite.py:2118 tells the model
  it was truncated); preserve that posture everywhere.
- **Consent stays simple.** ONE approve on GENERATE + git revert. Never re-introduce per-comment
  classification or per-address consent tiers (the anchor's standing correction). `approve_reach` is
  DROPPED — do not wire it into any flow. *Because* elaborate consent was training-derived caution, not
  Tim's need, and it killed the live feel.
- **FORM on the design system.** Every operator-facing surface renders on the corpus tokens
  (`canvas/app/src/components/design-system.css` ← `tokens.json`, aliased by `canvas/app/src/app.css` —
  e.g. `var(--panel)`, `var(--ink)`, `var(--sig)`, `var(--font-display)`/`var(--font-mono)`). Never
  hardcode a hex or a font. *Because* the surface assembles FROM the registry (law 2), and a non-developer
  recognises it by SHAPE — consistency IS comprehension. Verify with design-critic + design-lint + chrome.
- **Comprehension before action; never green-paint a feel.** Device/feel legs (streamed feel, real
  voice, the walked-through feel, did-the-mockup-edit-do-what-I-meant) are surfaced to Tim, never marked
  done by the loop.

---

## Area A — The guided show-me sequence (criteria A1-A4)

**Principles.** The walk is MODEL-FREE by construction for narration: it reads `address_help`'s corpus
how-to, not a model — so it never confabulates and never lags (Observed suite.py:6207-6257). The organ is
parameterized by a list of addresses, so the SAME engine walks live elements today and decisions/ideas
tomorrow — the studio is the first consumer, not the purpose.

**Sequence of operations (runtime).**
1. Operator picks walkthrough (the dial, or a "show me" affordance) → FE calls `start_walkthrough`.
2. `start_walkthrough` (suite.py:6287) sets the dial to `walkthrough` (pure `set_mode`) AND starts the
   organ over the item set (given, or all pending) → `start_session` → `present_current(0)`.
3. `present_current` returns `{item, framing (narration), raw.ui_target, guide:True}`. For a `ui://`
   stop it frames from the corpus (the C1 guided branch, suite.py:6216); for a `mockup://` stop it must
   tolerate + narrate from injected HTML (Area F).
4. FE drives the view: `resolveUiTarget(raw.ui_target)` → `spotlightUiRef` (scroll + 2.4s ring), renders
   the narration card, shows pace controls.
5. next/back → `next`/cursor move → repeat from step 3. dwell = no call (stay).

**Do.** Reuse `start_session`/`present_current`/`next` as-is (A1-A3). Frame narration from the corpus.
**Do** compose the flow-level `teach` side-channel WITH the corpus how-to (teach leads, element how-to
follows) — Observed suite.py:6227-6241.
**Don't** build a parallel stepper or narrate from a model — *because* the corpus path is fast,
non-confabulating, and the one-source law forbids a second engine. **Don't** call `speakReply` from the
guide path — the existing voice-narration effect reads `session.framing` for free (Observed
suite.py:6222-6224); touching voice functions risks G-8.

**Files.**
- `runtime/suite.py` — REUSE-import `start_walkthrough`:6287, `present_current`:6198, `next`:6492,
  `start_session`, `_registry_ui_target`:6161. MODIFY only for Area F (mockup tolerance).
- `canvas/app/src/components/StudioKit.tsx` — MODIFY: the guide overlay + narration card + spotlight call
  (Rail/Stage/RhmPanel/Composer already exist).
- `canvas/app/src/regions/Review.tsx` — MODIFY: host the guided mode in the studio room.
- `canvas/app/src/useAppController.ts` — MODIFY: the per-step view-drive effect (`resolveUiTarget`).
- `canvas/app/src/app.css` + `components/design-system.css` — REFERENCE (token source for the overlay).

**Preserves.** The review-card path (non-guide stops still call `coa` and present review items — the
guide branch is a `startswith("ui://")` sniff, suite.py:6216, that returns BEFORE the coa call, leaving
the review path byte-for-byte). The voice narration effect. `set_mode`'s pure contract (start_walkthrough
composes it, never changes it). The canvas region (the guide overlay is additive in the studio room).

---

## Area B — The live talk-back (criteria B1-B4)

**Principles.** "Talks back" = the existing chat organ run at the locus, STREAMED — not a new brain. The
streaming generator already exists and is PROVEN on voice; the only gap is a text endpoint that consumes
it. Reuse, not net-new cognition.

**Sequence of operations (runtime).**
1. Operator clicks an element (sets focus/locus) + types/speaks.
2. FE POSTs to a NEW text-stream endpoint (`/api/chat-stream`) with `{message, focus, graph_id}`.
3. The endpoint drives `chat_parts(message, gid, focus=...)` (suite.py:5264) and emits each part as an
   SSE/NDJSON frame as it arrives (mirror the voice driver's part-loop, bridge.py:737-744; do NOT
   re-implement staging — consume the generator).
4. FE EventSource appends each part to the chat panel live; on a new turn mid-stream, close the
   EventSource → server detects client-gone → closes the generator (B3, extend voice's `gone[0]` path,
   bridge.py:780-793).
5. R2 grounds the reply at the locus (the `focus` arg flows to `_chat_context` → `_resolve_context_at`).

**Do.** Wrap `chat_parts` in the text endpoint (B1). Pass `focus.selected` THROUGH on every path,
including voice (`/api/voice/stream` calls `chat_parts` with NO focus today — bridge.py:848 — add the
focus arg; `chat_parts` already accepts it).
**Don't** add a "bigger model" or a second chat path — *because* the streaming half is already built on
voice and the text chat is just full-wait (suite.py:5223-5242); the gap is wiring, not cognition.
**Don't** let the streamed path bypass the grounding rule — the reply must still answer w.r.t. the locus.

**Files.**
- `runtime/bridge.py` — NEW: `/api/chat-stream` (mirror `_voice_stream`:734 / `_stream_parts`:231).
  MODIFY: bridge.py:848 — pass `focus` into the voice `chat_parts` call (H1 + B2).
- `runtime/suite.py` — REUSE-import `chat_parts`:5264 (accepts `focus`), `_chat_context`:1902,
  `_resolve_context_at`:3036. Do not modify.
- `canvas/app/src/useAppController.ts` — MODIFY: the SSE fold for the chat panel (model the event-log SSE
  fold at :602; this is a SECOND, distinct SSE for reply text).
- `canvas/app/src/components/StudioKit.tsx` — MODIFY: append-parts-live in the chat panel; the locus chip.

**Preserves.** The full-wait `/api/chat` (kept as the fallback — the stream is additive). The voice
circuit (we ADD a focus arg to its `chat_parts` call; the part-loop, VAD, finished-thought judge, TTS
overlap, iOS playback all untouched). The event-log SSE at :602 (the new chat SSE is a separate stream,
no collision). Concurrent Cognition's staging (we consume `chat_parts`, never re-stage).

---

## Area C — Comprehension at altitude (criteria C1-C4)

**Principles.** The screen explains ITSELF. Two paths: registered live elements → `address_help` (3
legs); proposed mockups → raw-HTML injection (the ONLY path for unregistered mockups, and the one that's
VERIFIED working — synthesis §0). The original failure was that NEITHER path was active; the fix is to
keep the mockup in focus at every stop so the injection path is always live.

**Sequence of operations (runtime).**
1. `mockup://<file>` in `focus.selected` → `_chat_context` reads `design/mockups/<file>.html` (path-safe,
   realpath-contained, bare basename), injects under the `MOCKUP UNDER REVIEW` header with the explicit
   "read this FOR them, explain at plain-language altitude" instruction (Observed suite.py:2086-2125).
2. Over the 14KB cap → truncate WITH a fail-loud "[truncated — N chars]" marker (suite.py:2118).
3. The reply is shaped to altitude via `up_translate`/`coa` (C3 — confirm this is FE-wired; flagged
   possibly declared-not-wired).
4. C4 refinement: pre-digest HTML→text (extract structure/sections) so the 14KB carries more signal for
   >14KB mockups (IA-mobile 73KB → ~19% today).

**Do.** Keep the comprehension instruction + the fail-loud truncation marker (C1). For C4, lean
**pre-digest** over raw cap-raise — *because* the verified result was ALREADY truncated and good, so
signal-density beats raw size, and pre-digest avoids paying multi-thousand-token prefill on every turn
(synthesis D2-B).
**Don't** pre-build the extraction pipeline before measuring (the code comment at suite.py:2113 is an
explicit advisor bet: "only add cleaning IF a real test comes back junk") — *because* the 4B handled raw
truncated HTML fine, so premature cleaning is wasted build. **Don't** present raw HTML to the operator —
only the at-altitude prose.

**Files.**
- `runtime/suite.py` — MODIFY (C4 only): the injection block at :2086-2125 (add an optional pre-digest
  before the CAP). REUSE-import `address_help`:2213 (C2), `up_translate`/`coa` (C3).
- `canvas/app/src/regions/AddressHelp.tsx` — MODIFY/REFERENCE: the 3-leg comprehension card (C2 FORM,
  already token-based).
- `design/mockups/*.html` — REFERENCE (the corpus the injection reads).

**Preserves.** The grounding rule (REFUSES to answer about anything not in the live-state block — the
injection is what makes the mockup legible without breaking that rule, suite.py:2090-2092). The path-safe
realpath containment (a junk value can never read outside `design/mockups/`). The fail-loud truncation
(never silently feeds a partial as whole). C2's clean per-leg degrade + "(unregistered)" honesty.

---

## Area D — The addressed markup (criteria D1-D3)

**Principles.** Marks are append-only at `ui://` addresses; the address tree gives group semantics. R2
resolves them back at the locus + ancestors. The operate-vs-annotate boundary is never blurred.

**Sequence of operations (runtime).**
1. A mark (`annotate`/`ingest_comment`/`attach_chat`/`set_presentation_pref`) records at a `ui://`
   address (append-only; address validated by `parse_ui_address` — malformed RAISES).
2. On the next turn at that locus, R2 gathers it (annotations + chats + events + howto + prefs across the
   address AND ancestors), scores recency×proximity×pin×semantic, caps to budget, injects (suite.py:3036).
3. D3 (group roll-up): standing at a parent, a NEW descendant-gather collects marks on ALL descendants
   (today `_r2_ancestors` walks UPWARD only — a parent comment flows DOWN to children, but the reverse
   isn't built, Observed suite.py:2556).

**Do.** Reuse the four mark verbs + R2 as-is (D1, D2). For D3, add a descendant-gather that mirrors the
ancestor-walk's address-tree traversal in reverse — *because* the address grammar already encodes the
hierarchy; reuse it, don't invent a group model.
**Don't** blur operate-vs-annotate — `route_click` (suite.py:4204) keeps them distinct; preserve it.
**Don't** make D3 unbounded — apply the SAME R2 budget cap so a deep group can't flood the window.

**Files.**
- `runtime/suite.py` — MODIFY (D3): a descendant-gather alongside `_r2_ancestors`:2556. REUSE-import
  `annotate`:4263, `ingest_comment`:4291, `attach_chat`:4487, `set_presentation_pref`:4391,
  `route_click`:4204, `context_at`:3088 (the read-face, D2 FORM).
- `canvas/app/src/components/ContextBundle.tsx` — MODIFY/REFERENCE: the "what's resolved here" read-face
  (D2 FORM, token-based).
- `canvas/app/src/components/StudioKit.tsx` — MODIFY: the visible mark badge/pin at an address (D1 FORM).

**Preserves.** The append-only invariant (marks never overwrite). The ancestor-walk (D3 ADDS a reverse
gather; the existing downward inheritance is untouched). R2's single scoring source (D3 reuses the same
score+cap, no second source). `parse_ui_address` S0 gate.

---

## Area E — The accumulate → compose → one-approve BATCH (criteria E1-E2)

**Principles.** Every existing producer/approve/dispatch is SINGULAR (grep-confirmed airtight). The
governance + git + revert machinery is reusable AS-IS; the build is a WRAPPER: accumulate → compose →
one-approve → loop-dispatch. The unit is the marked-up address; the batch is the sequence's marks.

**Sequence of operations (runtime).**
1. Across the walk, marks accrue at addresses (Area D).
2. Operator clicks GENERATE → a compose-only pass: for each marked address, compose a build-intent
   reusing `resolve_scope` (ui→code scope), R2 (the attached context), `build_instruction`,
   `blast_radius` — the SAME pieces `surface_intent_at` uses per-address (suite.py:6816), just batched.
3. The batch is SHOWN (the batch-review surface) → operator approves ONCE.
4. Dispatch: loop `dispatch_decision` over the approved members; the dispatcher already handles
   concurrency (CONCURRENCY_CAP via `drive_dispatchable`, implement.py:473-545). Each member: `claude -p`
   → git checkpoint → revertible. Empty-scope members still DENY-ALL per member (no fabricated scope).

**Do.** Build a compose-only mode over the singular wire (E2) + the GENERATE button + the batch-review
surface. **Do** keep empty/orphan scope = DENY-ALL per member — *because* fabricating a broad scope to
"make it buildable" is the same failure as not acting (confabulation), suite.py:6835-6842.
**Don't** re-introduce per-comment gating in the batch UX — *because* consent is simple: ONE approve on
the batch, git is the net. **Don't** build a parallel dispatcher — *because* `dispatch_decision` +
`drive_dispatchable` already do concurrency, exactly-once, operator-only approve.

**Files.**
- `runtime/suite.py` — NEW: a `compose_batch(addresses)` that maps each address through the existing
  per-address pieces and mints a batch (reusing `surface_intent_at`:6816 / `surface_build_intent`:2962
  per member; NEW only the accumulation + batch envelope). REUSE-import `resolve_scope`:6929,
  `blast_radius`:6889, `dispatch_decision`:7360.
- `runtime/implement.py` — REUSE-import `dispatch_decision`/`drive_dispatchable`:473-545 (loop, don't
  rebuild).
- `runtime/bridge.py` — NEW: `/api/generate-batch` (compose) + the batch-approve route (operator-only,
  off the MCP face — mirror `/api/resolve`'s operator-only posture).
- `canvas/app/src/components/WireRequest.tsx` + `BlastRadiusReach.tsx` — MODIFY/REFERENCE: the
  single-intent card → extend to the batch-review board (E2 FORM, token-based). **Note:** do NOT wire
  `approve_reach` (dropped); `BlastRadiusReach.tsx` is REFERENCE for the scope display only.
- `canvas/app/src/regions/Review.tsx` — MODIFY: host the GENERATE button + the batch board.

**Preserves.** The singular wire end-to-end (the batch composes FROM it; the singular path stays a valid
entry). DENY-ALL on empty scope. Exactly-once + operator-only approve. Git checkpoint + `revert_self_change`.
The dispatcher's concurrency cap.

---

## Area F — GENERATE-FOR-MOCKUPS + the mockup-aware stop (criteria F1-F2) — THE MAKE-OR-BREAK

**Principles.** The autonomous loop edits the LIVE app; nothing edits the redesign MOCKUPS — which are
what the Commander reviews. Two net-new pieces, the same frontier: (F1) the tour must tolerate a mockup
stop; (F2) generate on a mockup must dispatch an edit to the mockup HTML. Treat as TWO loops sharing one
room: the LIVE loop is ready; the MOCKUP loop is the build.

**Sequence of operations (runtime — F2).**
1. Operator finishes a guided walk through `mockup://<file>`, talks through changes (marks accrue).
2. Clicks generate ON the mockup locus → the mockup-vs-live ROUTER (NEW) sees the locus is a `mockup://`
   address → routes to the mockup-scope resolver (NOT `resolve_scope`, which returns empty for a proposed
   surface → DENY-ALL, suite.py:7895 — correct for code, wrong for mockups).
3. The mockup-scope resolver returns `scope = ["design/mockups/<file>.html"]` (the file IS the artifact).
4. Dispatch a `claude -p` scoped to that file (reuse the wire's launch/git machinery) with the
   talked-through changes as the instruction.
5. VERIFY by re-render/screenshot (the mockup is HTML — render + capture; mirror the mockup-build skill's
   render path). Commit. Revertible via the same git path.

**Sequence (F1 — mockup-aware stop).** `present_current` currently RAISES on an unregistered address
(suite.py:6218-6220). MODIFY: if the stop is a `mockup://`/unregistered address, narrate from the injected
HTML (Area C path) instead of raising — OR add lightweight per-mockup registration.

```
# F1 (present_current, pseudocode for the new branch)
if item.startswith("mockup://") or not is_registered(item):
    narration = narrate_from_injected_html(item)   # reuse the Area-C comprehension path, model-free-where-possible
    return {framing: narration, raw: {kind: "mockup-guide", ...}, guide: True}
# else: existing ui:// branch (unchanged) / coa review branch (unchanged)
```

**Do.** Build the mockup-scope resolver + the mockup-vs-live router as the NET-NEW pieces (F2). **Do**
verify by re-render/screenshot — *because* a mockup edit that doesn't render is a silent break. **Do**
make F1 tolerate the stop, not crash — *because* the tour exists to review the proposals.
**Don't** route a mockup edit through `resolve_scope` — *because* it correctly returns empty (no code
behind a proposal) → DENY-ALL → nothing builds; the mockup needs its own file-scoped resolver.
**Don't** edit the live app from a mockup locus (or vice-versa) — the router keeps the two loops distinct
(the operator's own mockup-vs-live distinction).

**Files.**
- `runtime/suite.py` — MODIFY: `present_current`:6198 (F1 mockup tolerance). NEW: the mockup-scope
  resolver + the mockup-vs-live router (F2).
- `runtime/implement.py` — REUSE-import the launch/verify/git machinery; F2 adds a render/screenshot
  verify step for HTML artifacts (mirror the mockup-build skill's render path).
- `runtime/bridge.py` — MODIFY/REFERENCE: the retiring `/api/mockup-feedback` JSONL note path
  (bridge.py:1533/1564) is REPLACED by F2; remove only after F2 is proven (no silent gap).
- `canvas/app/src/regions/Review.tsx` — MODIFY: the mockup loop is retired here (Review.tsx:14) for the
  in-app surface; F2 is its built replacement.
- `design/mockups/*.html` — the dispatch TARGET (F2 writes here, git-tracked, revertible).

**Preserves.** The live-app loop (untouched — F2 is a SECOND scope-resolution branch, the live branch via
`resolve_scope` is byte-for-byte). DENY-ALL on genuinely empty scope (the mockup resolver only fires for
real mockup files; a junk address still DENY-ALLs). The git checkpoint/revert. The existing `present_current`
ui:// + review branches (F1 is an ADDITIONAL branch before the raise). The comprehension injection (F1
reuses it for narration).

---

## Area G — Temporal deixis, scoped (criteria G1-G2)

**Principles.** "this/here" is built (the current locus). "that-before-this" has NO substrate today —
scope it to "the last few you touched" (a short locus-trail), NOT full multi-hop ordered deixis (the 4B
confuses antecedents; HCI research says it's hard and unproductized).

**Sequence of operations (runtime — G2).**
1. On every locus change (`_current_locus` set, suite.py:2142), emit a `navigate` event
   (address-stamped) — today the event log carries no navigation events.
2. A NEW `recent_loci()` reader returns the last-few touched addresses in order (from the navigate
   events).
3. Inject the trail into context (alongside R2) so "the one before this" resolves over the recent set.

**Do.** Scope to the last-few (G2). **Do** emit navigate events address-stamped (event_address_acceptance:
every emit is stamped or a documented exclusion).
**Don't** promise full ordered multi-hop deixis — *because* it's a research-stage capability the resident
model can't hold reliably; over-promising re-creates the original failure (a surface that doesn't do what
it implies).

**Files.**
- `runtime/suite.py` — MODIFY: emit a `navigate` event at the `_current_locus` set-point (:2142). NEW:
  `recent_loci()` reader + inject the trail (alongside `_resolve_context_at`:3036).
- `canvas/app/src/components/StudioSeams.ts` — REFERENCE/MODIFY: StudioSeams.ts:86 flags standing locus ☐
  (the FE breadcrumb surface, G2 FORM). **(Real path: `canvas/app/src/components/StudioSeams.ts`.)**
- `canvas/app/src/components/StudioKit.tsx` — MODIFY: the visual breadcrumb strip (G2 FORM, token-based).

**Preserves.** `_current_locus` last-wins semantics (G1 — the navigate emit is additive). The last-6
events that reach context (the trail is a SEPARATE, scoped reader, not a change to the event budget). R2's
budget cap (the trail injection is bounded).

---

## Area H — Voice-in + the FE show-me lane (criteria H1-H2)

**Principles.** Voice-in is one of the STRONGEST legs (whisper.cpp local STT + the full live VAD/
finished-thought loop are built); the only gap is focus-passthrough. The FE show-me lane is the
net-new FE that makes the Commander SEE himself walked through, riding the already-built backend
view-driving.

**Sequence of operations.**
- **H1:** `/api/voice/stream` calls `chat_parts(transcript, gid)` with NO `focus` (bridge.py:848) → pass
  `focus.selected` through so voice is locus-aware (auto-listen via `sendChat` already carries focus).
- **H2:** dial-select walkthrough → FE calls `start_walkthrough`; per step the FE drives
  `resolveUiTarget(raw.ui_target)` → spotlight + renders the guide overlay + next/back/dwell controls;
  on advance it calls `indicate(step_address)` so the chat at the stop auto-grounds (I3 — Observed gap:
  advancing does NOT update the chat locus, ~5 FE lines).

**Do.** Add the one focus arg (H1) — *because* the capability is built; deferring leaves the most-ready
leg on the table (synthesis D3-A). **Do** ride the existing view-drive (`resolveUiTarget`/`spotlightUiRef`,
suite.py:6161 → FE :1469/:1570) for H2.
**Don't** touch the VAD / finished-thought judge / TTS overlap / iOS playback (G-8) — *because* the voice
circuit is proven; only ADD the focus arg. **Don't** green-paint the auto-listen / real-mic feel — it's
device-only (needs-tim).

**Files.**
- `runtime/bridge.py` — MODIFY: bridge.py:848 (pass `focus`). REUSE-import `/api/voice/stream`:734.
- `runtime/suite.py` — REUSE-import `chat_parts`:5264 (accepts focus), `start_walkthrough`:6287,
  `_registry_ui_target`:6161.
- `canvas/app/src/useAppController.ts` — MODIFY: the per-step view-drive effect + the dial-select trigger
  + the advance→`indicate` call (I3).
- `canvas/app/src/components/StudioKit.tsx` — MODIFY: the guided overlay + next/back/dwell controls (H2
  FORM). REFERENCE: `App.tsx` (the canvas↔review view-switch).

**Preserves.** The whole voice circuit (only the focus arg is added). Auto-listen's existing focus carry.
The backend view-drive (H2 is the FE half; backend is untouched). The canvas region (the overlay is
additive in the studio room).

---

## Area I — The unifying connections (criteria I1-I5) — THE UNIFICATION CENTERPIECE

**Principles.** This surface IS the `walkthrough` mode — NOT a new mode to create. The mode already
exists in MODE_REGISTRY (suite.py:1278) with `guided`/`show-me` subtypes, and `start_walkthrough`
(suite.py:6287) already binds dial→organ. The unification is: bind the FE to it, declare the faculties it
fires via the axes the registry already carries, and capture the improvements the reuse forces — never as
"create," always as "bind/declare/refine." The MODE_REGISTRY is the canonical one-source join (3 old
tables are DERIVED VIEWS of it, suite.py:1329-1342) — extend it the SAME way: add to the row, not a branch.

**Sequence of operations.**
- **I1:** FE dial-select walkthrough → `start_walkthrough` (sets dial + starts organ). The mode's
  `resolution` lens (`strata=None`, `howto_detail=full`, `budget=6000`/`8000` for show-me, suite.py:1283)
  flows into R2 via `resolution_spec_for(mode)` → `_resolve_context_at(..., resolution=_res)` (Observed
  suite.py:2172-2174) — so entering the mode AUTOMATICALLY widens context to the affordance leg. The
  faculties it fires are the registry axes: resolution lens · `live=["per-turn"]` · `grain="paragraph"`
  · `brain_config="voice-64k"`.
- **I2:** the improvement the reuse forces — ensure the walkthrough mode's resolution lens + `present_current`'s
  mockup tolerance (F1) admit the `mockup://` comprehension injection so the comprehension faculty fires
  on proposal stops. If the injection has no home in the existing axes, declare it as a faculty the
  walkthrough mode fires (NET-NEW, marked honestly).
- **I3:** advance → `indicate(step_address)` (the ~5-line FE seam; H2).
- **I4:** add `annotate` to `RHM_VERBS` (suite.py:3158-3206) with `current_locus()` as default address;
  autonomous mid-dialogue annotate (non-destructive → no card; git/visibility is the net; the one-approve
  gate stays on GENERATE).
- **I5:** the standing anti-parallel guard — every area reuses, never parallels (grep-checked at build).

**Do.** Treat I1 as bind/declare/refine. **Do** declare new behaviour in the registry row as data —
*because* registry-is-truth lets a future consumer (decisions/ideas/verifications) ride the SAME organ by
adding its own mode-row + lens, no parallel stepper. **Do** capture I2/I4 as the improvements the
unification forces (the synthesis flagged them — don't drop them).
**Don't** branch on `mode == "walkthrough"` in R2 or the engine — *because* it can't be extended; the
lens is consumed as data (suite.py:3055-3061). **Don't** put `annotate` behind the approval card (I4) —
*because* marks are non-destructive and gating them kills the live "it does it for you" feel; the gate
belongs on generate.

**Files.**
- `runtime/suite.py` — REFERENCE: MODE_REGISTRY:1220 / the `walkthrough` row:1278 / `mode_registry()`:1538
  / `resolution_spec_for` / `MODE_SPECS`:1333 (DERIVED view). MODIFY: I2 (lens admits comprehension), I4
  (`RHM_VERBS`:3158-3206 + default address). REUSE-import `start_walkthrough`:6287.
- `canvas/app/src/useAppController.ts` + `components/StudioKit.tsx` — MODIFY: the dial-select trigger (I1
  FORM) + the advance→indicate seam (I3).
- `canvas/app/src/components/StudioSeams.ts` — REFERENCE: the FE seam declarations.

**Preserves.** The 8-mode contract (modes_acceptance asserts len==8 + exact order — I1/I2 do NOT add or
reorder modes; they bind + refine the EXISTING `walkthrough` row). The 3 DERIVED views (MODE_SPECS /
PART_GRAIN / ACTIVATION_ALLOCATION stay value-for-value — any registry edit re-derives them, no parallel
table). The default R2 path (resolution=None → byte-for-byte today; the `listening` seed lens is
unchanged). `set_mode`'s pure contract. The RHM verb whitelist's safety (I4 adds ONE non-destructive verb;
`run`/`build`/`dispatch` gating is untouched).

---

## Cross-cutting verification (how the loop proves each criterion)

- **FUNCTION** — a real run with provenance: backend curl / a suite test exercising the path / a chrome
  drive of the FE. Code-reading is NOT verification (Tim's law).
- **FORM** — design-critic + design-lint + a chrome render/screenshot against the corpus tokens. A
  text-wall or raw model output FAILS the form face regardless of function.
- **needs-tim legs** — the streamed feel, real voice, the walked-through feel, did-the-mockup-edit-do-
  what-I-meant — surfaced to Tim, NEVER green-painted.
- **The anti-parallel guard (I5)** — re-grep for a second stepper / intent path / scoring source / mode
  table per criterion; any duplicate is a FAIL.
