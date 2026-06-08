# Coverage: `area://canvas` — the whole front end
> Agent: coverage sweep · 2026-06-08
> Method: ls + targeted reads (~30–40 lines of signatures per file) + grep patterns.
> Evidence marks: **Observed (file:line)** = read in code · **Inferred** = pattern-matched · **Unification-opportunity** = named gap the guided-review-surface landing would activate or fix.

---

## 0 · Territory map (files read)

```
canvas/app/src/
  App.tsx              (338 lines)   — layout shell, Hud, view-switch, AnnotateBar, JourneyBar
  useAppController.ts  (2389 lines)  — ALL state + handlers + effects; the SSE fold; the keystone
  api.ts               (399 lines)   — api client + pure helpers
  AppContext.ts        (14 lines)    — context bridge
  registryStore.ts     (92 lines)    — shape-reachable external store (OINFO/UI_INFO/NODE_STATES/COGNITION_INFO)
  NodeShape.tsx        (read to :60) — generic node shape, reads NODE_STATES from registry
  regions/
    Review.tsx         (62)          — studio shell (Rail|Stage|RhmPanel composition)
    StudioKit.tsx      (256)         — Card, Rail, Stage, Composer, RhmPanel — the studio structural primitives
    StudioSeams.ts     (113)         — WIRED vs PENDING seam map (the integration contract)
    RhmChat.tsx        (94)          — the real right-hand-man chat organ
    ProposeAffordance.tsx (172)      — B1/B2 two-click consent + steer + defer
    Walkthrough.tsx    (94)          — the walkthrough card (both review + guided-tour C1 modes)
    Inbox.tsx          (181)         — chief-of-staff triage (build-intent lane, deferred-offer lane)
    CognitionView.tsx  (214)         — Pulse / River / Nodes (live cognition organ)
    AddressHelp.tsx    (278)         — D2/F1 altitude surface (what-this-is + how-to-use + drill-down)
    Workshop.tsx       (28)          — full-viewport output modal
    Toolbar.tsx        (78)          — run + mode dial + guide/teach controls + settings gear
    (and 8 others: Activity, Fleet, Grow, History, Inspector, OpPanels, Palette, SelfChanges, Settings, Versions)
  components/
    WireRequest.tsx    (155)         — G-4 self-build wire door (point→ask→see-reach→approve)
    BuildIntentCard.tsx(104)         — demonstrate-first build-intent card
    ContextBundle.tsx  (50+)         — X5 surfaced context-bundle + X7 pin
    BlastRadiusReach.tsx(301)        — X16 reach ripple
    StudioSeams.ts     (see regions) — in components/, same file
    kit.tsx            (71)          — Surface/SectionHead/Badge/EmptyState/LaneHead
    ShapeHow.tsx       (114)         — F1 feedback chips (reshape-presentation affordance)
    NodeConfigForm.tsx, PanelErrorBoundary.tsx, PanelView.tsx
```

---

## 1 · USES — existing regions/components/seams the guided-review-surface composes

### 1.1 · The studio room (Review.tsx + StudioKit.tsx) — the surface IS this room

**Observed (Review.tsx:1–62):** The studio is a real in-app region (`regions/Review.tsx`) composing three named structural primitives: `<Rail>` (the corpus gallery), `<Stage>` (sandboxed iframe with in-mockup element deixis), `<RhmPanel>` (the real RhmChat organ at the indicated locus + AddressHelp + Composer). The outer shell carries `data-ui-ref="ui://studio"`.

**Observed (StudioKit.tsx:1–257):** Each primitive declares its contract (binds / emits / token-slots) and is structure-only — no aesthetic. The `<Card>` carries `data-ui-ref={address}` so a click indicates the mockup's surface. The `<Stage>` implements the in-mockup element deixis (postMessage capture, same-origin guard, only `studio-deixis` envelope, only `ui://` addresses — Observed StudioKit.tsx:101–134; `inFrameDeixis` is WIRED in StudioSeams.ts:43–44). The `<Composer>` posts to `/api/annotate` and reads back via `/api/annotations` (NOT the retired mockup-feedback jsonl — the bespoke jsonl retirement is load-bearing).

**What it means for the build:** The studio room IS the guided-review-surface's FE home. Rail→Stage→RhmPanel is the [ gallery | show-me area | right-hand-man ] skeleton the guided overlay rides into. The structural seams are already named and typed; Claude Design designs against them.

---

### 1.2 · The locus channel: indicate() → focus.selected → context-at-address

**Observed (useAppController.ts:808–824):** `indicate(addr)` is the ONE locus sink. Sets `indicatedRef.current` (non-stale closure read), paints `.ui-indicated` on the DOM element, and — in journey-recording mode — appends the address as a journey step. All downstream consumers read the ref.

**Observed (useAppController.ts:1100–1144 `sendChat`):** When a message is sent, `focus.selected` assembles `[reviewMockup:// prefix, indicatedRef.current, ...nodeIds]`. The `mockup://` prefix rides FIRST (the "mockup under review" framing leads). The backend's `_chat_context` reads this. This IS the focus→locus→context-at-address channel.

**Observed (StudioKit.tsx:112–134 `Stage`, `setReviewMockup`):** Opening a mockup sets `reviewMockup` AND calls `indicate(address)` → the locus binds for free. In-mockup element clicks re-indicate the clicked element's `data-ui-ref` WITHOUT remounting the iframe (the `key={reviewMockup}` stays stable).

**What it means for the build:** The channel is fully built for the studio. The guided-review-surface adds the show-me overlay on top: when the walkthrough advances to a stop, the FE must call `indicate(stop_address)` so the chat at that stop is auto-grounded. This is the Bucket-B seam (synthesis §2, "walkthrough ↔ chat composition" — ~5 FE lines).

---

### 1.3 · The RhmChat organ

**Observed (RhmChat.tsx:1–94):** The real chat organ. Carries conversation threads (S2 new/reopen), the memory loop (V3 record/debrief), minimize control, voice push-to-talk (mic button → `micPressed`), and the `<ProposeAffordance />` consent card. The gear/config panel is **RETIRED** — model/persona/voice settings live in the consolidated Settings. NO streaming text: `sendChat` calls `api.chat()` (full-wait JSON, Observed api.ts:97) and sets `chatBusy` throughout.

**Unification-opportunity (U1 — TEXT STREAMING):** `api.chat()` is a full-wait POST (Observed api.ts:97). The backend `chat_parts()` streaming generator already exists (synthesis Bucket B, Observed suite.py:5264-5312). The FE chat panel shows `"thinking…"` until the whole reply lands. No SSE/NDJSON text consumer exists in `useAppController.ts` or `RhmChat.tsx`. **This is the single highest-leverage FE change for "feels live"** (synthesis §5 step 1). The guided-review surface makes this gap maximally visible because the RhmPanel inside the studio IS the same RhmChat organ — every guided stop feels frozen until the full reply lands.

---

### 1.4 · The ProposeAffordance (B1/B2 consent surface)

**Observed (ProposeAffordance.tsx:1–172):** Fully built. B1 = single/simple offer (one-click approve or steer). B2 = interactive multi-option comparison (select-then-approve, chat-until-approve, steer refines options). Both support: pick, steer (loops through `sendChat`), defer-to-inbox (B3), set-aside, dismiss. The `interactive` flag is the registry-truth marker. Nothing runs until the explicit approve commit (the B2 invariant is preserved).

**What it means for the build:** The guided-review-surface's "BATCH compose+one-approve" (synthesis Bucket C-b) extends THIS surface — the batch approve is a WRAPPER over the singular `approveProposal` path, not a replacement. The multi-option comparison card (B2) is the FE pattern for showing a composed batch and selecting from it.

---

### 1.5 · The walkthrough card (Walkthrough.tsx) — shares the session machinery

**Observed (Walkthrough.tsx:1–94):** The walkthrough card serves BOTH the review walk (verdict affordances) AND the guided-sequence tour (C1 — `isGuide = !!(session.guide || session.raw?.guide_address)`). A guide step hides verdicts and shows "step through" + "show again". Both share: the `wtBusy` concurrency guard, the per-step spotlight drive (`resolveUiTarget`), voice/text toggle, the narration effect (speaks `session.framing`). The Bucket-C-h "FE show-me lane" (the guided overlay the Commander sees) is THIS component, promoted to be the overlay riding the studio Stage.

**Observed (useAppController.ts:1677–1686):** The per-step view-drive effect calls `indicate(hint)` ONLY when `session.raw?.indicate` is explicitly set (the teach-to-self-modify tour's hard-gated doors). For a DEFAULT guide step over `guide_address`, there is **NO indicate call to bind the chat locus to the guide stop**.

**Unification-opportunity (U2 — WALKTHROUGH ↔ CHAT COMPOSITION GAP):** Confirmed. When a guide step advances, `indicate(session.raw?.guide_address)` is NOT called. The locus in `sendChat`'s `focus.selected` therefore still carries the previous step's locus (or null). The synthesis's "~5 FE lines" fix: in the per-step view-drive effect (useAppController.ts:1677), after resolving the ui_target, call `indicate(session.raw?.guide_address || session.raw?.ui_target)` so every guide stop auto-grounds the chat. This is the exact Bucket-B seam.

---

### 1.6 · The AddressHelp / altitude surface (D2/F1)

**Observed (AddressHelp.tsx:1–279):** Fully built. Renders the 3-leg address_help bundle at altitude (plain-language what + how-to-use leads; mechanism drills down). Degrades cleanly per leg (5 states, including well-formed-but-unregistered). The F1 "learned marker" and `lead_with:change` structural adapt are wired (the ShapeHow feedback chips POST `/api/presentation-pref` → re-fetch → the panel reflects the pref). Carries `data-ui-ref="ui://inspector/help"` so it is itself addressable and guidable. Renders nothing unless a `ui://` locus is indicated.

**What it means for the build:** This is the SAME panel mounted inside `RhmPanel` in the studio (`StudioKit.tsx:226–256` RhmPanel's `studio-rhm-help` block). For a guided stop on a registered address, this panel explains the stop at altitude — no net-new code needed. For an **unregistered** mockup address it returns `(unregistered)`, which is STATE-4 (surfaced honestly as "not registered yet"). For `mockup://` comprehension the help falls back to the injected-HTML path (synthesis §0 verified).

---

### 1.7 · The CognitionView (live cognition organ)

**Observed (CognitionView.tsx:1–214):** The Commander's window onto the system's OWN thinking. Three altitudes: Pulse (default ambient iris beside the reply), River (converging tributary flow), Nodes (role cards). Fully SSE-driven (`cognition.*` events fold into `cognitionTurn` via `foldCognition`, Observed useAppController.ts:395, 640–642). Registry-driven: a new role/state appears with zero FE code.

**Observed (CognitionView.tsx:34–45, `statusToken`):** The `latent / firing / injected` lifecycle states used in the River fall back to hardcoded design-system tokens (`--fail`, `--acc`, `--await`, `--tx-3`). These lifecycle states are **NOT registered as `node_states`** in the backend (Observed comment line 31–35: "06 §F#4 named them net-new"). So `statusToken` first checks the registered `nodeStates` array (the registry path), then falls back to the switch.

**Unification-opportunity (U3 — COGNITION NODE_STATES NOT WIRED for lifecycle states):** The Pulse and River read `cognitionInfo?.node_states` (loaded from `/api/cognition_info`) for registered states, but the live lifecycle states (`firing`, `injected`, `latent`) are not yet registered backend-side. This is a known gap (synthesis Bucket C: "C-h" — NODE_STATES-not-wired named as a deferred FE lane). The guided-review-surface landing is the moment to register them: when the River shows as the RHM works through a guided stop, the tributary states should paint from the registry, not hardcoded fallbacks. One backend registration pass (add to the cognition node_states) → the FE River paints correctly with zero FE edit (rule 8).

**What it means for the build:** CognitionView is the **SIBLING live-view** to the guided-review-surface. When the RHM explains a stop, the Pulse should breathe beside the reply in the RhmPanel — the operator sees cognition happening as the narration arrives. The Pulse is already mounted in the canvas (`App.tsx:205`) beside RhmChat; inside the studio's RhmPanel, it is NOT currently mounted. The guided-review-surface build should mount the Pulse beside the RhmPanel's chat lane (the studio's own RhmChat instance) so the operator can open the River while the RHM narrates a stop.

---

### 1.8 · The Inbox (the deferred-offer lane and the walk-these affordance)

**Observed (Inbox.tsx:1–181):** The chief-of-staff surface. Key seams for the guided-review-surface:

- The **"walk these"** button (`ui://inbox/walk`, Observed Inbox.tsx:63–65) calls `startWalk(item_ids)` — this is how the Inbox drives the walkthrough organ today (the review loop's entry from the Inbox side).
- The **deferred-offer lane** (B3, Observed Inbox.tsx:93–118): live offers parked by the operator (`deferOffer → /api/defer-offer`). Each renders as a RESUME card whose click re-opens the interactive ProposeAffordance card. This is the persistence mechanism for "generate later" — a composed batch offer (Bucket C-b) that the operator parks and resumes.
- The **build-intent lane** (wire-blue, Observed Inbox.tsx:79–91): renders `BuildIntentCard` for each `isBuildIntent` escalation. The demonstrate-first pattern + `BlastRadiusReach` ripple.

**What it means for the build:** The guided-review-surface's "batch compose + one-approve" ends up HERE as a deferred-offer card (if the operator parks it) or immediately as a ProposeAffordance B2 card (if they approve inline). The Inbox is the destination for any generate action that isn't approved immediately; the build inherits this for free.

---

### 1.9 · The SSE fold (openStream in useAppController.ts)

**Observed (useAppController.ts:598–668):** Single `EventSource` on `/api/stream?since=<cursor>`. Dispatches by kind: structural (`run/create/connect/delete/move`) → loadGraph; `mode/config` → poll + settings refresh; `cognition.*` → foldCognition; `decision.*`/`ask`/`reject`/etc. → inbox+poll; `chat/react` → chatHistory; `review.advance/start` → refreshSession.

**Observed (useAppController.ts:650–652):** The `chat/react` branch refreshes the chat log via `api.chatHistory()` (full array, replaces). This is the SSE path that keeps the chat log live after a streaming text response lands — but it delivers the FULL history, not parts arriving live. The streaming parts themselves are not delivered to the FE (no NDJSON/text-stream consumer in this branch).

**What it means for the build:** The SSE feed is the right channel for streaming text chat parts — a new `chat.part` event kind (or a NDJSON response channel) would slot into the `chat/react` branch as a real-time appender. This is Bucket B (wrap `chat_parts()` in a text SSE endpoint; FE appends each part as it arrives — synthesis §5 step 1).

---

### 1.10 · api.ts — the hot FE file the guided-review-surface touches

**Observed (api.ts:1–399):** All backend routes are in one client. Key routes for the build:

- `api.chat(message, focus)` → full-wait POST (no streaming, Observed :97)
- `api.walkthroughStart(item_ids?)` → POST /api/walkthrough/start (C4 FE show-me lane, Observed :296–298)
- `api.corpus()` → GET /api/corpus (studio gallery, Observed :189)
- `api.annotate` → POST /api/annotate (Composer comment path — called via `annotateLocus`)
- `api.intentAt(address, text)` → POST /api/intent-at (Composer request-change path)
- `api.addressHelp(address)` → GET /api/address-help (the 3-leg altitude bundle)
- `api.annotations(address)` → GET /api/annotations?address= (thread read-back)
- **Missing:** No `api.chatStream()` method exists (the text-SSE seam is net-new, Bucket B)
- **Missing:** No `api.walkthroughGuide()` / guide-specific start (the existing `startGuide()` calls the raw `fetch` inline in the controller, Observed useAppController.ts:1344 — not a named api method)

---

## 2 · TOUCHES — App.tsx mount, the controller, api.ts

### 2.1 · The view-switch (App.tsx:127–175)

**Observed (App.tsx:127–175):** The VIEW SWITCH is a net-new structural piece added 2026-06-08. A top-level `view` state (`'canvas' | 'review'`) toggles between the canvas shell and the Review workspace. Both render inside the SAME `AppContext.Provider` — the RHM brain, the locus channel, and all state are shared. The tldraw board keeps running underneath either view; in `'review'` the canvas shell is `display:none` (not unmounted — canvas state survives the switch). The view-switch chip carries `data-ui-ref="ui://view-switch"`.

**What it means for the build:** The guided-review-surface's studio room IS the `view === 'review'` branch. The build is assembling the guided overlay (Bucket C-h) INSIDE the studio's existing `<Review>` component. The AppContext sharing means `walkthroughStart`, `startGuide`, `indicate`, `sendChat`, `CognitionView`, and the `<ProposeAffordance>` consent surface are ALL available inside the Review workspace without a wiring pass — they are the same controller.

---

### 2.2 · The controller is the hot file

**Observed (useAppController.ts):** 2389 lines. Every capability the guided-review-surface needs passes through this file:

- `sendChat` (full-wait, the streaming seam lives here)
- `indicate` (the locus sink)
- `resolveUiTarget` / `spotlightUiRef` (the keystone)
- `changeMode` (dial→walkthrough→`walkthroughStart`)
- `startGuide` (the guided-sequence tour)
- `startWalk` / `nextStep` / `endWalk` / `respondStep`
- `annotateLocus` / `mintBuildIntent`
- `fetchAddressHelp`
- `openStream` (the SSE fold)

The **streaming text seam** (Bucket B) is a controller change: `sendChat` currently `await api.chat()` full-wait. The change is: open a `fetch()` to the new text-SSE endpoint, read `.body` in a `ReadableStream` loop, append each part to `chat` incrementally (exactly as the voice circuit reads `voiceStream`, Observed api.ts:141–143 `voiceStream` returns raw Response). The voice circuit is the pattern to reuse.

**What it means for the build:** The controller is the primary edit file for Bucket B (streaming) and the walkthrough ↔ chat composition fix. Both are additive — they add a branch or a call to existing logic, not a rewrite.

---

### 2.3 · api.ts — the guided-review-surface adds one new method

**Inferred:** The text-SSE chat path will need either a new `api.chatStream(message, focus)` method (returning raw Response like `voiceStream`) or an amended `api.chat` that accepts a streaming flag. The voice circuit pattern (`api.voiceStream` → `fetch` returning raw `Response`, caller reads `.body`) is the exact template. The guided-review-surface needs this in api.ts when the streaming seam is built.

---

## 3 · UNIFIES / IMPROVES — deferred FE lanes the synthesis named

### 3.1 · U1 — Text streaming (Bucket B + Bucket C-d) — THE FEEL

**Observed gap:** `api.chat()` is full-wait (api.ts:97). No NDJSON/SSE consumer in the controller. `chatBusy` shows "thinking…" until the whole reply arrives. The `chat_parts()` generator is built backend-side (synthesis Bucket B).

**Unification path:** Add `api.chatStream(m, focus)` → `fetch('/api/chat/stream', …)` returning raw Response. In `sendChat`, branch: if streaming is available, open the stream and `setChat(c => [...c, { role: 'assistant', text: accumulated }])` as parts arrive (mirroring the voice circuit's NDJSON reader at useAppController.ts:1900). This activates the already-built backend generator.

**What activates:** The feel-live experience that everything in the guided-review-surface rides on. Without it, every guided stop narration feels frozen. This is synthesis step 1.

---

### 3.2 · U2 — Walkthrough ↔ chat locus composition (Bucket B, ~5 lines)

**Observed gap:** The per-step view-drive effect (useAppController.ts:1677–1686) calls `indicate(hint)` only when `session.raw?.indicate` is explicitly set (the teach-to-self-modify tour special case). For a default guided-sequence step, `guide_address` is set on `session.raw` but `indicate()` is NOT called. Result: the chat at each stop is not auto-grounded at the stop's address.

**Unification path (exact location):** After line 1683 (`const tgt = session.raw?.ui_target`), add:
```
const guideAddr = session.raw?.guide_address
if (guideAddr && guideAddr.startsWith('ui://') && !hint) {
  indicate(guideAddr)
}
```
This makes every guide step indicate its address before the spotlight → sendChat's `focus.selected` leads with that address → context-at-address auto-resolves.

**What activates:** Every guided stop becomes auto-grounded (synthesis Bucket B, the "walkthrough ↔ chat composition" seam).

---

### 3.3 · U3 — CognitionView Pulse inside the studio (missing mount)

**Observed gap:** The Pulse (`CognitionView`) is mounted in `App.tsx:205` inside the canvas `.as-canvas` div. When `view === 'review'`, the canvas shell is `display:none` (App.tsx:175) — the Pulse is hidden. Inside the studio's RhmPanel (`StudioKit.tsx:226–256`), there is NO `<CognitionView>` mount.

**Unification path:** Mount `<CognitionView>` alongside `<RhmChat />` inside the RhmPanel (or as an adjacent overlay in Review.tsx), wrapped in `<PanelErrorBoundary>`. The CognitionView's SSE feed runs continuously (the `openStream` is app-global), so mounting it here is purely additive — no new data subscription needed.

**What activates:** The Commander sees the Pulse breathe beside the reply as the RHM narrates each stop. The River is available on click. The cognition organ becomes part of the review experience.

---

### 3.4 · U4 — `latent/firing/injected` lifecycle states not in NODE_STATES registry

**Observed gap (CognitionView.tsx:34–45):** The River's `statusToken()` falls back to hardcoded design-system tokens for `latent/firing/injected` because these lifecycle states are not registered in `cognitionInfo?.node_states`. The comment at line 31 names this as "net-new" in the backend spec.

**Unification path:** Backend registration (one pass in the cognition roles/states registry) → the FE fallback switch becomes dead code → the River paints from the registry (rule 8). This is a build-touchpoint the guided-review-surface landing should include.

---

### 3.5 · U5 — Workshop is a 3-stream candidate

**Observed (Workshop.tsx:1–28):** The Workshop modal shows a single node's full output (`workshop.output` as plain text). The synthesis named a "workshop 3-stream" (the three output altitudes of a node result). Workshop currently renders one Surface well with raw output text. When the guided-review-surface emits a "batch generated" result, the Workshop (or a sibling) could surface it — the Workshop's `setWorkshop(node, output, address)` call from the controller is the natural landing point for a generated-mockup result.

**Inferred:** The Workshop is the correct region for showing a generated-mockup diff/preview (a "here's what changed" after a GENERATE-FOR-MOCKUPS dispatch). The Workshop already covers the full viewport and is outside the grid. This is a UNIFY opportunity: extend Workshop to accept a `result_kind` field that renders appropriately (diff view vs raw text vs screenshot).

---

### 3.6 · U6 — Duplicated patterns: AnnotateBar / WireRequest share vocabulary, not a base

**Observed (App.tsx:58–74 AnnotateBar, components/WireRequest.tsx:1–155):** Both are indicated-ui:// affordances that float over the canvas cell, both use `.rhm-indicating` chip vocabulary, both gate on `clickMode(indicated) !== 'annotate'` being true (or not). They are NOT composed from a shared `IndicatedAffordance` wrapper — both independently implement the gate check, the vocabulary, and the subtree-exclusion from `onDocClick`.

**Unification-opportunity:** A `<IndicatedAffordance gate="annotate">` wrapper that handles the gate check + the `onDocClick` exclusion once. Both AnnotateBar and WireRequest slot inside it. The guided-review-surface will add a third affordance in this area (the "generate" button on a guide step, scoped to the guided stop's address) — the wrapper is the clean foundation.

---

### 3.7 · U7 — Inbox deferred-offer lane missing `data-ui-ref`

**Observed (Inbox.tsx:97–99 comment):** The deferred-offer lane explicitly notes it has NO `data-ui-ref` yet because `ui://inbox/deferred-offers` is not registered in `design/_system/addresses.json`. The comment flags a "corpus-registration batch" pending. This lane is load-bearing for the guided-review-surface: when the operator parks a "generate" batch offer, it lands here. The lane works without the ref, but it cannot be spotlighted by a guide tour or addressed by the RHM without registration.

**Unification path:** Register `ui://inbox/deferred-offers` in the addresses corpus. This is a one-line addition to the addresses registry + a `data-ui-ref` on the lane's `<div className="ibx-lane">`.

---

## 4 · RELATES — conceptually related regions and surfaces

### 4.1 · CognitionView as sibling live-view (the Pulse + River beside the guided dialogue)

**Observed:** CognitionView is explicitly built as "the commander's bridge" (CognitionView.tsx:2 — "the operator's window onto the system's OWN thinking"). The guided-review-surface is also described as "the Commander's-bridge made into one surface" (synthesis §1). These are the same architectural claim from two directions: CognitionView = how the system thinks; guided-review = how the system presents to the Commander. They are designed to coexist in the same room. The `data-ui-ref="ui://cognition"` address is registered (Observed CognitionView.tsx:192).

**Relates as:** A COMPOSE relationship. The guided-review-surface mounts the CognitionView alongside its RhmPanel — the Pulse is the ambient signal of RHM depth-of-thought at each guided stop.

---

### 4.2 · AddressHelp as the static comprehension face at each stop

**Observed:** The AddressHelp panel is mounted in the right-rail (`App.tsx:248–250`) and in the RhmPanel's studio block (`StudioKit.tsx:235–250 RhmPanel`). For a registered guided stop, AddressHelp pre-populates the three legs at the stop's address — this IS the "address_help 3-leg comprehension" the synthesis marks READY (synthesis Bucket A). The guided overlay can reference the AddressHelp panel directly rather than duplicating the comprehension.

**Relates as:** A REUSE relationship. At each guided stop, AddressHelp renders the "what is this + what can I do here" panel for free, no RHM call needed. The RHM narration (the framing/howto) is additional synthesis; AddressHelp is the static face.

---

### 4.3 · Inbox "walk these" → the review walk's entry from the Inbox side

**Observed (Inbox.tsx:63–65):** `ui://inbox/walk` calls `startWalk(item_ids)`. This is the bridge from the Inbox (the decision/approval surface) to the Walkthrough organ (the guided review). When the guided-review-surface builds the FE show-me lane for the Studio (a separate entry), it is a SECOND entry into the SAME `startGuide()`/`startWalk()` machinery — the Inbox's entry stays as the review-walk path; the Studio adds a guide-path entry from the mockup view. Both drive `setSession()` → the same Walkthrough card.

**Relates as:** A SHARE relationship. Two entries into one organ. The Studio's guided entry (`walkthroughStart()` or `startGuide()`) reuses the existing per-step view-drive, narration, and spotlight machinery already proven in the Inbox "walk these" path.

---

### 4.4 · JourneyBar and journey recording

**Observed (App.tsx:85–114 JourneyBar, useAppController.ts:149–154, api.ts:308–316):** The journey-recording system (L9 reverse journey) is an explicit navigation-history substrate: `journeyStart/journeyStep/journeyStop/journeyReplay` at `/api/journey/*`. This IS the temporal-deixis substrate (synthesis Bucket C-e). Every `indicate()` call appends a step while recording. The replay steps through addresses via the PRESERVED `resolveUiTarget`. This is the closest thing to "recent loci" the FE currently has — but it requires explicit recording (not automatic).

**Relates as:** A SEED relationship. The synthesis's "temporal-deixis scope-down" (Bucket C-e, D5-A) can extend the journey substrate: auto-emit `navigate` events on `indicate()` calls (not just when recording) → a `recent_loci()` reader → inject the trail into chat context. The existing `journeyStep` API call pattern is the implementation template. This is Bucket C-e's build path, and it lives entirely in the controller.

---

## 5 · Key observed gaps (synthesis confirmation or new)

| Gap | Observed location | Synthesis bucket | Severity |
|---|---|---|---|
| No text streaming — `sendChat` full-wait | api.ts:97, useAppController.ts:1121 | Bucket B (seam) + C-d (interruptible) | The feel of everything |
| Walkthrough ↔ chat locus not composed | useAppController.ts:1677–1686 | Bucket B (~5 lines) | Grounding of every guided stop |
| No guided overlay (FE show-me lane) | Review.tsx (no overlay), Walkthrough.tsx (exists but not studio-mounted) | Bucket C-h | The visible guided UX |
| No generate/batch-approve UI | Review.tsx, StudioKit.tsx, ProposeAffordance (only singular) | Bucket C-b | "generate" doesn't exist yet |
| GENERATE-FOR-MOCKUPS dispatch (no mockup scope path) | StudioSeams.ts PENDING (empty, L1_COMMENT_TO_INTENT only) | Bucket C-a | The spine |
| Mockup-aware guided stop (present_current RAISES) | No FE protection — the Walkthrough card would show whatever the backend returns | Bucket C-c | Tour can't walk mockups |
| CognitionView not mounted in studio | App.tsx:205 (canvas-only mount), StudioKit.tsx (no CognitionView) | New finding | Commander can't see cognition while reviewing |
| `latent/firing/injected` not in NODE_STATES | CognitionView.tsx:34–45 | New finding | River paints from hardcoded fallbacks |
| `ui://inbox/deferred-offers` not registered | Inbox.tsx:97–99 | Registration gap | Parked generate offers can't be spotlighted |
| No `startGuide` in api.ts | useAppController.ts:1344 (raw fetch) | Structural gap | Guide start not a named api seam |

---

## 6 · R2 context at address — PENDING seam status

**Observed (StudioSeams.ts:57–71 R2_CONTEXT_AT_ADDRESS):** The backend `GET /api/context?address=` resolver is BUILT and proven (`addr_context_acceptance.py`). What remains PENDING is the **FE CONSUMER**: no studio region calls `api.context(address)` yet. The PENDING seam entry declares this honestly and says "move to WIRED when an addressed-context inspector region binds it." The per-leg reads (annotation thread + address-help) serve the panel today as partial substitutes. This is catalogued as `to_wire` in Suite._ORPHAN_ROUTES.

**What it means for the build:** The synthesis's R2 "context bundle" view (PENDING seam R2_CONTEXT_AT_ADDRESS) is the correct next surface in the RhmPanel — a collapsible "context at this address" panel below AddressHelp, binding `api.context(address)` on indicate. This would show the operator exactly what the RHM sees at the current stop. ContextBundle.tsx (the components/ContextBundle.tsx component) already renders a context array — it could be repurposed for this seam once the FE consumer is bound.

---

## 7 · up_translate / coa altitude-shaping — FE wiring status

**Observed (StudioSeams.ts:29 `upTranslate`):** `api.upTranslate(kind, ref)` IS declared in STUDIO_WIRED (`upTranslate: { route: 'GET /api/up-translate', …, backend: 'runtime/suite.py:5100 up_translate' }`). However, the StudioSeams comment notes "the ADDRESS surface (AddressHelp) consumes `addressHelp` DIRECTLY (not this envelope) BY DESIGN" (Observed api.ts:250–256). The `up_translate` envelope is provided for the OTHER kinds (decision → coa, future finding/event consumers); it is **NOT wired into any FE render** currently.

**Observed (api.ts:255):** "provided for completeness + correctness, not wired into a FE render here (see the lane report's identified_gaps)."

**Confirms synthesis flag:** The synthesis notes "`up_translate`/`coa` altitude-shaping **may not be FE-wired** (declared-not-wired-to-surface)". **Confirmed observed.** The `up_translate` method exists in `api.ts:255` but no FE component calls it. `coa` (Observed api.ts:112 `api.coa(id)`) is called by `openCoa` in the controller — that IS wired (the Inbox's "compile ↗" action). The altitude-shaping for CHAT output (the `coa` voice for explanations) goes through the brain/chat path, not through a separate `up_translate` call to the FE. This is not a blocking gap — the chat path already shapes altitude via the brain; the `up_translate` FE endpoint is for future surfaces that need the altitude envelope as a discrete object.

---

## 8 · Summary table by relation kind

| Relation | Component/Seam | Status |
|---|---|---|
| **USE** | Rail/Stage/RhmPanel (the studio room) | READY — the FE home of the guided surface |
| **USE** | indicate() → locus channel | READY — the one locus sink |
| **USE** | sendChat (the chat path) | READY (full-wait); text-streaming MODERATE (Bucket B) |
| **USE** | ProposeAffordance (B1/B2 consent) | READY — extend for batch |
| **USE** | Walkthrough card (C1 guided-sequence) | READY (card exists); studio-mount + overlay = NET-NEW |
| **USE** | AddressHelp (D2/F1 altitude) | READY — the static comprehension face at each stop |
| **USE** | resolveUiTarget + spotlightUiRef | READY — the preserved spotlight keystone |
| **USE** | startGuide() + changeMode(walkthrough) | READY — the organ entry points |
| **USE** | api.walkthroughStart(), api.annotate(), api.intentAt() | READY — all WIRED in StudioSeams |
| **TOUCH** | App.tsx view-switch (canvas↔review) | BUILT (2026-06-08) — the guided surface IS the review branch |
| **TOUCH** | useAppController sendChat (stream seam) | Full-wait today; streaming seam lives here |
| **TOUCH** | useAppController per-step view-drive effect | The walkthrough↔chat locus fix lands here (~5 lines) |
| **TOUCH** | api.ts | One new `chatStream` method for the streaming seam |
| **TOUCH** | StudioSeams.ts PENDING → WIRED migration | When generate-for-mockups or R2 context lands |
| **UNIFY** | Text streaming (Bucket B) | Net-new endpoint + controller branch |
| **UNIFY** | Walkthrough↔chat locus composition | ~5 lines in the per-step effect |
| **UNIFY** | CognitionView Pulse mount in studio | Additive — mount CognitionView in RhmPanel/Review |
| **UNIFY** | NODE_STATES lifecycle states registration | Backend pass → River paints from registry |
| **UNIFY** | AnnotateBar/WireRequest shared base | One IndicatedAffordance wrapper (third affordance coming) |
| **UNIFY** | `ui://inbox/deferred-offers` registration | Corpus + data-ui-ref (one line each) |
| **RELATE** | CognitionView as sibling live-view | Compose into the guided-review room |
| **RELATE** | Inbox "walk these" as second entry to the organ | Share startWalk → setSession → Walkthrough |
| **RELATE** | JourneyBar / journey recording as temporal-deixis seed | Extend `indicate()` to auto-emit navigate events |
| **RELATE** | ContextBundle as R2 context-at-address view | Repurpose for the PENDING R2 FE consumer |

---

## 9 · The top unification opportunity

**U1 — Text streaming** is the single highest-leverage change in the canvas area. Every interaction the guided-review-surface delivers — narration at a stop, dialogue about a mockup, the RHM explaining a change — currently lands as a frozen "thinking…" → full-text dump. The `chat_parts()` generator is built and proven on the voice path; the FE voice circuit (`api.voiceStream` → raw Response → NDJSON reader, Observed useAppController.ts:1900) is the exact template. The change is: one new `api.chatStream()` method + a branch in `sendChat` that reads the stream and appends parts to the chat log incrementally. **Without this, the guided-review-surface's dialogue feels broken no matter how correct the backend comprehension is.** This is synthesis step 1, and it is a MODERATE seam, not net-new architecture.
