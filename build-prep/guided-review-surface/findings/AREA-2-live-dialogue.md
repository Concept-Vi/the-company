# AREA 2 — Live Conversational Grounding: The RHM Talking Back, Following Deixis

Research agent: Area 2 of 6. Stress-testing the anchor, not confirming it.
Evidence marks: **Observed(file:line)** / **Inferred** / **External** / **Anchor-idea**

---

## 0 · Executive stress-test summary

The anchor's framing — "RHM talks back live" — is **architecturally achievable but not currently wired**. The key finding is that the gap is smaller than it looks and bigger than it sounds. The machinery for locus-grounded dialogue exists and is real. The machinery for streaming exists and is real. They are not connected to each other in the review surface. The machinery for temporal deixis ("that thing that opened before this") is the weakest link — it exists in the event log but is not surfaced to the RHM in a form that resolves cross-locus references. The resident model (Qwen3.5-4B) is a genuine constraint for the full deictic-following vision, not a dealbreaker for the grounded-conversation core.

Read carefully: the anchor was mostly right about what exists. Where it was naive: (a) "talks back live" implies streaming but today's chat organ is pure request/response; (b) the temporal deixis ("that thing that opened before this") is NOT currently tracked in any form the RHM sees; (c) the walkthrough/review organ is a **separate code path** from the chat organ — they coexist but do not compose yet; (d) the voice circuit already IS streaming and does compose with `chat_parts`.

---

## 1 · The chat organ today: what it actually is

### 1.1 The request/response shape (Observed)

**Observed(bridge.py:1110-1113):** The `/api/chat` POST handler calls `SUITE.chat(b["message"], gid, focus=b.get("focus"))` and returns `_send(200, json.dumps(...))` — a complete JSON response. No streaming. The FE in `sendChat` (**Observed(useAppController.ts:1121)**) does `const r = await api.chat(m, { selected })` — a full-wait `await`. During processing, the UI shows `"thinking…"` (**Observed(RhmChat.tsx:67)**). There is no partial delivery.

**Observed(suite.py:5223-5242):** `chat()` itself is: prologue → `_chat_part_core(is_final=True)` → epilogue. One part, one return. The docstring explicitly states "chat() does NOT stage (one part)."

**The anchor claim "talked back live" is aspirational, not current.** The chat organ is synchronous request/response. Every turn is: user sends → server thinks (possibly 5–25 seconds on a 4B model) → full reply arrives. There is no mid-thought streaming to the FE, no partial delivery, no interruption.

### 1.2 The staged/streamed path that DOES exist (Observed)

**Observed(suite.py:5264-5312):** `chat_parts()` IS a generator that yields parts as they complete. It is already wired to the **voice streaming path** (`/api/voice/stream`, `_voice_stream` in **bridge.py:734-903**). The voice path does genuine brain-ahead-of-TTS overlap: Part 1 fires instantly from base context, the concurrent cognition swarm fills Part 2, TTS starts on Part 1 while Part 2 generates. First audio plays at ~(STT + Part1-gen + one-sentence TTS latency).

**This is the architecture the anchor wants for text chat too — it just isn't wired there.** The gap between "talks back live" and today is: wire `chat_parts()` behind a streaming text endpoint (SSE or NDJSON), have the FE append each part to the chat log as it arrives. The underlying generator, the concurrent cognition swarm, the part-level text — all real and working in the voice path already.

### 1.3 What the anchor says about streaming (anchor-idea vs observed)

**Anchor-idea:** "the existing chat organ (`suite.chat`) run at the current locus but **streamed + live + voice-capable**, not request/response." This is CORRECT as a direction but overstates what exists today. The chat organ exists and runs at the locus. Streamed and live: the machinery exists (`chat_parts`) but is **not yet wired to a text-chat streaming endpoint**. Voice-capable: also wired, but only through the separate `/api/voice/stream` path that currently bypasses the studio focus entirely (the voice turn calls `SUITE.chat_parts(transcript, gid)` — no `focus` arg passed, **Observed(bridge.py:848)**).

**Gap for the anchor's vision:** Three specific wirings are needed:
1. A streaming text endpoint (e.g. `/api/chat/stream`, SSE or NDJSON) that drives `chat_parts()` and ships each part as it arrives.
2. Wire `focus` into the voice stream path (currently missing — voice turns are locus-blind).
3. FE: append parts live as they arrive rather than waiting for the final response.

None of these require new architecture — they are connection seams over existing machinery.

---

## 2 · The focus → locus → context channel: how it actually works

### 2.1 The full mechanism (Observed)

**Observed(useAppController.ts:1115-1121):** When `sendChat` fires, it assembles `focus.selected` as `[mockup://<file>, ui://<indicated-address>, ...canvas-node-ids]` and posts it with the message.

**Observed(suite.py:2084-2142):** Inside `_chat_context`, the focus is unpacked:
- `mockup://` values → the mockup HTML is read from disk and injected into the context block (up to 14000 chars cap)
- `ui://` values → `_describe_ui_address` resolves the registry description; `_current_locus` is SET to `indicated[-1]` (last-wins)
- canvas node-ids → the node's output/config is injected as co-presence

**Observed(suite.py:2413-2425):** `current_locus()` returns `self._current_locus` — this IS the persisted backend locus. The locus **survives across turns**: once set, it holds until a new `ui://` address is indicated. A canvas-node-only turn (no `ui://`) leaves the prior locus intact.

**Observed(suite.py:2173-2174):** R2 (`_resolve_context_at`) runs inside `_chat_context` at every turn, passing `self.current_locus()`. It gathers: annotations at the locus, chats attached to the locus, addressed events at the locus, the howto stratum, the presentation-pref stratum — all scored by recency × proximity × pin × semantic-relevance-to-intent. Budget-capped at 4000 chars.

**The anchor's claim is correct and well-built.** The focus→locus→context channel is real and working. The RHM genuinely knows what the operator is pointing at, and auto-resolves what's been said there before.

### 2.2 What the RHM's "grounding" actually contains (Observed)

**Observed(suite.py:1973-2175, `_chat_context`):** Every chat turn gets:
- Live graph state (nodes, resolved/unresolved counts)
- Last 6 events from the event log (kind + summary only)
- Available models (chat + embed)
- Current mode, available verbs
- Inbox items awaiting
- Panels, graphs
- Show-targets vocabulary
- IF there is a mockup: its raw HTML (up to 14k chars)
- IF there is an indicated ui:// address: the registry description of that element
- IF there is a current locus: the R2 context slice (annotations, chats, events, howto at the address)
- IF canvas nodes are selected: their output/config

This is substantial grounding. The RHM can answer "what am I looking at" with real content because the mockup HTML is injected.

---

## 3 · Deixis and temporal grounding: the honest hard part

### 3.1 Spatial deixis: "this / here" (Observed — mostly working)

"This" and "here" are already handled. When the operator clicks an element inside a staged mockup, the in-mockup capture script postMessages the element's `data-ui-ref` address (**Observed(StudioKit.tsx:101-134)**). The Stage listener calls `setReviewMockup(currentFile, addr)` → `indicate(addr)` → which sets `indicatedRef.current` → which ships `ui://<addr>` in the next `sendChat`. The backend then describes that element from the registry AND sets the `_current_locus` to it.

**The limit:** "this" only resolves to addresses that are in the `UI_REGISTRY` and have a `data-ui-ref` in the mockup HTML. A mockup element with no `data-ui-ref` is invisible to the deixis system — the capture script finds `null` and posts nothing (**Observed(StudioKit.tsx:108-110, FAIL-SOFT comment)**). This means deictic resolution for new/proposed mockup elements (the ones Tim is reviewing) depends on the mockup author having marked them with `data-ui-ref`. For mockups representing surfaces NOT YET in the registry, `_describe_ui_address` returns the address tagged "(unregistered)" — the RHM sees the address but not a meaningful description.

**Implication:** For review-of-existing-surfaces (real UI), spatial deixis works well. For review-of-proposed-surfaces (new mockups), it degrades to the mockup HTML + address-without-registry-description. That's still useful — the HTML IS injected — but `address_help` returns an empty `what_this_is` for unregistered addresses.

### 3.2 Temporal deixis: "that thing that opened before this" (The hard gap)

**This is where the anchor is naive.** The claim "it follows pointing like 'I want THIS to come in from HERE, after I click that thing that opened before THIS showed up'" requires the RHM to track:

1. **What the operator is pointing at NOW** — Observed: ✅ the current locus (`_current_locus`) and focus.selected
2. **What just happened** — Observed: ⚠️ LIMITED: last 6 events from the event log (kind + summary, no address-sequencing for user-navigation events)
3. **The order in which UI elements have been shown/opened** — Observed: ❌ NOT TRACKED

**The event log contains:**
- `run` events (graph execution)
- `mode` events (presence dial)
- `chat` events (each turn — text, not address-navigation)
- `annotation` events (comments placed at addresses)
- `warning`, `config`, etc.

**The event log does NOT contain:**
- "operator navigated to screen X"
- "walkthrough step advanced to stop Y"
- "operator opened panel Z"
- "review cursor moved from address A to address B"

**Observed(suite.py:1990):** `_chat_context` takes `self.store.recent_events(6)` — only the last 6 events, kind + summary only. Navigation events are NOT emitted, so "that thing that opened before this" has NO substrate in the current event log.

**The R2 context resolution (`_resolve_context_at`) is address-keyed.** It knows what's been said/annotated AT an address, and at its ancestors. It does NOT maintain a sequence of "which addresses were active in what order" across a session. There is no "recently-visited addresses" list.

**To follow temporal deixis properly, the system would need:**
- Navigation events emitted with `address=` when the operator's locus changes (set a new `_current_locus` → emit a `navigate` event)
- A "locus history" readable by the RHM — a short ordered list of recent `ui://` addresses, not just the current one
- The R2 context to include the prior 3-5 loci when the operator uses temporal language

**This is a real build gap, not a wiring issue.** It requires: (a) emitting navigation events when the locus changes, (b) a `recent_loci()` getter that reads those events, (c) injecting that into `_chat_context`. None of these are large — but none exist today.

**Practical consequence:** "I want THIS to come in from HERE" (spatial, one turn) — workable. "After I click that thing that opened before THIS showed up" (temporal, cross-turn, multi-step) — currently impossible for the RHM to follow. It has no visibility into the operator's navigation history.

### 3.3 The chat history as partial temporal grounding (Observed)

There is one partial substitute: `chat_history`. **Observed(suite.py:1965):** `training_signal()` reads `chat_history(999)`. In `_chat_context` the chat history flows into the model's conversation thread (it IS the thread). So the model sees what the operator said across prior turns, including what they said about prior screens.

**This is imperfect but non-zero.** If the operator said "what's on this screen?" about screen A, and then said "I want that behavior from screen A to appear here on screen B" — the model has the prior turn in its context window and can infer what "screen A" referred to. This is language-model temporal grounding, not address-system grounding.

**The limit:** this works for immediately prior turns (in-context), fails for anything across a long session or conversation gap, and gives the model no knowledge of which locus was active when each prior turn was said. The model is guessing from text, not reading from a structured locus trail.

---

## 4 · The walkthrough organ and the chat organ: they coexist but don't compose

### 4.1 The walkthrough organ today (Observed)

**Observed(suite.py:6198-6257, `present_current`):** The walkthrough/guide organ drives the view to a `ui://` address, resolves its narration from `address_help`, emits it as `framing`, and stamps a `ui_target` for the FE to resolve. **Observed(Walkthrough.tsx:8-94):** The FE renders the narration as a card, with NEXT/BACK/verdict controls.

**This is the "RHM shows you" half of the anchor's vision, already working.** The walkthrough organ drives the view to a stop, provides narration from the corpus (model-free for guided tours, model-dependent via `coa()` for review items). The operator can step through.

### 4.2 What the chat organ adds at each stop (Inferred — close but not wired)

The RHM chat panel (`RhmPanel` with `RhmChat` inside) renders alongside the walkthrough card in the Review surface. **Observed(StudioKit.tsx:226-256, RhmPanel):** The RhmPanel mounts `<RhmChat/>` and the `<Composer/>`. The chat organ uses the `indicated` locus (the last clicked/indicated address) as its focus.

**But: during a guided walkthrough, the locus is driven by the walkthrough organ's `resolveUiTarget` call** (**Observed(useAppController.ts, resolveUiTarget reference)**), NOT by the chat organ's `focus.selected`. The two organs are NOT connected — the walkthrough step advancing does not automatically update the chat's indicated locus.

**This is the key composition gap.** When the walkthrough advances to step N (address `ui://toolbar/run`), the chat organ does NOT automatically know that `ui://toolbar/run` is the current stop. The operator would have to manually click the element OR the walkthrough organ would need to emit an `indicate(step_address)` call when it advances. Neither happens today.

**To compose them:** when `nextStep` advances the walkthrough cursor, call `indicate(session.raw?.guide_address)` to set the chat's locus to the current stop. Then the RhmChat at that stop is automatically locus-grounded: the operator can ask "what can I change here?" and the RHM sees the address + its R2 context. This is a 5-line FE seam.

### 4.3 The narration being model-free is both a strength and a limit (Observed + Inferred)

**Observed(suite.py:6216-6257):** For guided-sequence steps (ui:// addresses), `present_current` returns `address_help`'s `how_to_use` or `what_this_is` — content from the registry corpus, NOT from the LLM. This is fast (model-free) and never confabulates (registry-is-truth).

**The limit the anchor acknowledges:** the narration is only as good as what's in the registry. For elements with authored `howto` text, the narration is rich. For bare registry entries (just `what_this_is` from the title), it's thin. **Observed(suite.py:6225-6226):** `corpus_narration = bundle.get("how_to_use") or bundle.get("what_this_is") or f"This is {item_id} — a part of the interface."` — the final fallback is a near-empty stub.

**For the proposed-surfaces use case** (reviewing new mockup designs that haven't been built yet): there is NO `address_help` for addresses that don't exist in the registry. The `present_current` guided-branch would raise `ValueError` on `address_help(item_id)` for an unregistered address (**Observed(suite.py:6218-6220)**). This means the current guided-tour machinery **cannot walk through new mockup addresses** — only registered, existing UI elements.

**This is a genuine limit for the review-of-proposals use case.** The anchor's vision includes walking through mockup proposals (new surfaces being designed). The current walkthrough organ can only walk through elements that are already in `UI_REGISTRY`. For new proposals, narration would have to come from the LLM reading the mockup HTML (the `mockup://` focus path), not from the corpus.

---

## 5 · Voice-in: the gap between the voice circuit and the studio locus

### 5.1 The voice circuit today (Observed)

**Observed(bridge.py:1075-1077, `/api/voice/stream`):** The streaming voice turn: STT → `SUITE.chat_parts(transcript, gid)` → TTS-overlapped delivery. The voice turn IS streaming already (NDJSON events, sentence-by-sentence). First audio plays at ~(silence detection + STT + Part1-gen + one-sentence TTS).

**Observed(bridge.py:848):** `parts_gen = SUITE.chat_parts(transcript, gid, turn_id=turn_id)` — no `focus` arg passed. The voice turn is **locus-blind**. The voice circuit does not pass the studio's current review address or indicated element into the brain.

**Observed(bridge.py:1058):** Even the non-streaming voice turn `(/api/voice/turn)` passes `think_fn=lambda txt: SUITE.chat(txt, gid)` — also no `focus`.

**The voice circuit currently ignores the operator's indicated locus entirely.** A voice turn saying "what is the button in the upper right of this screen?" has no access to what screen the operator is looking at.

### 5.2 The gap to locus-grounded voice (Inferred — close)

The fix is a `focus` parameter flowing from the FE through the voice endpoint. Mechanism: the FE sends the current `reviewAddress` (studio locus) and `reviewMockup` in the voice request body or query string → the bridge reads it → passes it to `chat_parts(transcript, gid, focus={selected: [...]})`. `chat_parts` already accepts `focus` (**Observed(suite.py:5264)**). Total: FE serializes `focus`, bridge unpacks it, passes through. No new architecture.

**The auto-listen path (`autoListen`)** (**Observed(useAppController.ts:304-2147)**) cycles through hear → transcript → `sendChat(transcript)` using the standard chat path with focus intact. So auto-listen DOES carry the locus correctly — it routes through `sendChat` which assembles `focus.selected` normally. Only the direct `/api/voice/stream` path loses the focus.

### 5.3 The FE voice path in the Review surface (Inferred)

In the Review surface, the `RhmChat` renders inside `RhmPanel`. The mic button is there. Push-to-talk routes through `micPressed` → `recordToggle` → blob → `runVoiceTurn(blob)` → `/api/voice/stream`. The `reviewMockup` and `reviewAddress` exist in the controller state but are NOT currently passed to `runVoiceTurn`. So voice-in in the studio works for conversation but not for locus-grounded conversation.

**The good news:** `sendChat` from the same controller DOES pass `focus.selected` correctly, including `reviewMockup` and `indicatedRef`. So **typed** studio chat is already locus-grounded. Only the **voice** path drops the focus.

---

## 6 · The resident model reality: Qwen3.5-4B and what it can handle

### 6.1 What the model is asked to do in live dialogue (Observed + External)

**Observed(suite.py:5264-5312, chat_parts):** The staged/streaming path uses a swarm of roles (the "cast") to process turns. The `chat()` call runs the base 4B model with:
- The assembled `_chat_context` block (live state + locus ground truth)
- The conversation history
- Available tools (the verb whitelist as native function-tools)
- Possibly semantic ranking via embedding (a second model call)

**Observed(suite.py:5223-5228):** The docstring says "The RHM model MUST support native tools: a non-tool model is refused FAIL-LOUD." So the 4B model must support function calling.

**External:** Qwen3.5-4B is a strong small model with instruction following and tool use. At ~2700 tok/s locally (from the MEMORY.md benchmark), a short grounded turn (say 300 tokens output) completes in ~110ms. A longer staged reply (Part 1: 150 tokens, Part 2: 400 tokens with swarm injection) takes maybe 400-600ms for Part 1 to arrive. This is fast enough for near-live feel if streamed.

### 6.2 Where the 4B model struggles for this use case (Honest assessment)

**The model context:** Each turn already carries a substantial context block — live state + mockup HTML (up to 14k chars) + R2 locus context (4k chars) + conversation history. On a 4B model with ~66k token KV (from MEMORY.md), a rich studio session with multiple mockups reviewed and substantial history approaches the comfortable range for consistent grounding.

**The anchor's "you mean like xyz?" and "what kind of…?" pattern:** These are SHORT, grounded clarification turns — the model asks a question to resolve ambiguity, then waits for the user to answer. This is genuinely well-suited to a small model with good context. The context provides what the model needs; the output is a short clarifying question. Qwen3.5-4B handles this competently.

**The hard case: temporal deictic chasing across long sessions.** "That thing that opened before THIS showed up" — even if the system emits navigation events and builds a locus trail, the model must track and resolve multi-step references across turns. For complex multi-hop "this → that → the thing before that" chains, a 4B model may confuse antecedents, especially if the trail is long. This is not about size alone — it is about working memory across context. The grounding machinery (navigation events + locus trail) CAN compensate by structuring the context to make the reference chain explicit. But without that structured context, the 4B model will guess from prose history and will sometimes be wrong.

**Honest summary:** For the core use case — grounded single-locus "what am I looking at, what can I change" conversation with clarifying questions — Qwen3.5-4B is adequate and fast. For sophisticated multi-hop temporal deixis ("what came before this screen three steps ago"), it needs structured support from the system (locus trail, navigation events) or it will confuse references. The model is not the blocker; the missing context structure is.

### 6.3 The "abstains" behavior (Observed)

**Observed(suite.py:5223-5228):** The docstring says the RHM "answers from compact ground truth; never confabulates system facts." The prompting enforces grounded-or-abstains — if the RHM cannot ground a claim in the live-state block, it is supposed to say so. For mockup review, this means: if an element's `data-ui-ref` is not in the registry, the model is told "(unregistered)" and the abstains behavior is the right response — "I can see this element in the HTML but don't have registered information about it." For proposed surfaces this is honest degradation, not failure.

---

## 7 · What the anchor got right vs. what needs correcting

### What the anchor got right (Observed confirmation)

- The focus→locus→context channel is real and works (**Observed(suite.py:2073-2174)**) ✅
- The `address_help` three-leg bundle (what_this_is / how_to_change / how_to_use) is real (**Observed(suite.py:2213-2304)**) ✅
- `annotate` / `annotations_at` + `attach_chat` / `chats_at` work and are address-keyed (**Observed(suite.py:4487-4530)**) ✅
- R2 auto-resolves context at the locus, bounded by decay (**Observed(suite.py:3036-3086)**) ✅
- The walkthrough organ drives the view to stops and narrates (**Observed(suite.py:6198-6337)**) ✅
- `chat_parts()` is a real streaming generator (**Observed(suite.py:5264-5312)**) ✅
- Voice streaming already uses `chat_parts` (**Observed(bridge.py:734-903)**) ✅
- In-mockup element deixis is built (postMessage from iframe) (**Observed(StudioKit.tsx:101-134)**) ✅

### Where the anchor was naive or underspecified

**1. "Talks back live" implies streaming — today's text chat is request/response.** The streaming machinery exists (`chat_parts`, `/api/voice/stream`) but text chat (`/api/chat`) is a full-wait call. A streaming text chat endpoint does not exist yet. This is a new build seam, not a wiring of existing wires.

**2. Temporal deixis has NO substrate today.** The event log (6 events, kind+summary) does NOT track navigation history. "That thing that opened before this" has nothing to resolve against. This requires: emit navigation events, build a `recent_loci()` reader, inject into `_chat_context`. Not huge but not already there.

**3. The walkthrough organ and chat organ are NOT composed.** Advancing a walkthrough step does NOT update the chat's indicated locus. The operator must manually indicate the current stop for the chat to be grounded at it. One FE seam (`indicate(step_address)` on step advance) closes this — but it isn't wired.

**4. The voice path drops the studio locus.** `/api/voice/stream` calls `SUITE.chat_parts(transcript, gid)` with no `focus` (**Observed(bridge.py:848)**). Typed chat passes focus; voice does not. The auto-listen path routes through `sendChat` so it DOES pass focus correctly — only direct voice turn calls lose it.

**5. New mockup addresses cannot be guided-toured.** The `present_current` guided-branch raises on unregistered addresses. Reviewing proposed new surfaces (the design-iteration use case) cannot use the walkthrough organ in its current form — it would need a fallback to "narrate from mockup HTML via LLM" rather than "narrate from corpus via address_help."

**6. The "mark up as you talk" idea (RHM calls annotate on the user's behalf) is designed but not autonomous.** The verb whitelist includes `annotate` (**Inferred from suite.py:3158-3183 VerbSpec table and the anchor's claim**). But the RHM proposing to annotate and then EXECUTING the annotation still goes through the consent gate (propose → user approves → `/api/act`). "The RHM does it for you" mid-conversation would bypass the gate — that design decision is open. The current I3 consent model requires operator approval for any action, including annotate.

---

## 8 · What's really needed vs. what the anchor implies already exists

The anchor implies most of the "live guided conversation" machinery is assembled and needs only composition. Here is the honest build inventory:

### Already real and working (no new build needed)
- Locus-grounded chat (focus→locus→context) at a `ui://` address (**suite.py:2073-2174**)
- In-mockup element deixis via postMessage (**StudioKit.tsx:101-134**)
- R2 context resolution at the locus (annotations, chats, events, howto) (**suite.py:3036-3086**)
- address_help (what_this_is / how_to_change / how_to_use) (**suite.py:2213-2304**)
- walkthrough organ: drive view to a stop + narrate (corpus-based) (**suite.py:6198-6337**)
- chat_parts() streaming generator (**suite.py:5264-5312**)
- voice streaming with brain↔TTS overlap (**bridge.py:734-903**)
- annotate / attach_chat at addresses (**suite.py:3967-4195**)
- Studio surface skeleton (Rail / Stage / RhmPanel / Composer) (**Review.tsx, StudioKit.tsx**)

### New seams needed (wiring of existing machinery)

| Seam | What to do | Effort |
|------|-----------|--------|
| Streaming text chat | New endpoint `/api/chat/stream` driving `chat_parts()` → SSE/NDJSON; FE appends parts live | Small-medium |
| Walkthrough↔chat composition | `indicate(step_address)` called when walkthrough step advances | Tiny (5 FE lines) |
| Voice focus passthrough | FE sends `focus.selected` to `/api/voice/stream`; bridge passes to `chat_parts` | Small |

### New builds needed (net-new substrate)

| Build | What it is | Effort |
|-------|-----------|--------|
| Navigation event emission | Emit `navigate` event (with `address=`) when `_current_locus` changes | Small (suite.py `_chat_context` seam) |
| Locus trail in context | `recent_loci()` reads navigate events → inject last 5 loci into `_chat_context` | Small-medium |
| Proposed-surface narration | Fallback for unregistered mockup addresses: LLM reads mockup HTML + address → narrates; used by guided tour when address_help returns absent legs | Medium |

### Design decisions that are open (Tim's calls)

- **Autonomous annotate**: does the RHM annotate mid-conversation on the operator's behalf, or does it always go through the consent card (I3)? Currently the consent model requires approval even for `annotate`. Making annotate autonomous (no card) during live dialogue is a consent-model change, not just wiring.
- **Temporal deixis depth**: how many prior loci to surface and in what form. A locus trail of 5 is useful; 20 is probably noise. The decay model applies here too.
- **Proposed-surface handling**: when a mockup address is unregistered, use LLM narration (model-dependent, may confabulate) vs. silently skip that leg (honest degrade). The current design is honest degrade. The live guided experience may need LLM narration for new proposals — that trades confabulation risk for experience completeness.

---

## 9 · The generalization angle (from anchor §8)

The anchor asks: "is the studio just the FIRST instance of a guided-RHM surface that works for ANY part of the Company?" The answer from the code is: **yes, structurally, because the organs are generic.**

The walkthrough organ is parameterized by `item_ids` — a list of `ui://` addresses or inbox review-ids (**Observed(suite.py:6287-6337)**). Any ordered set of addresses can become a guided tour. The `GUIDE_SEQUENCES` dict (**Observed(suite.py:6355-6395)**) is just a registry of named address lists. Adding a new guided sequence for any Company surface is: add an entry to `GUIDE_SEQUENCES`, write `howto` text into the corpus for those addresses. The organ runs it.

The `_chat_context` grounding is already generic over any `ui://` address — it resolves whatever locus is active. There is no studio-specific branch. So moving this to a "guided RHM review of the Company's inbox" or "guided RHM review of the node graph" or any other context is just: make sure those addresses are in `UI_REGISTRY` and have authored `howto` text. The organs compose.

The one studio-specific thing is the mockup iframe with element-level deixis. That is the proposed-surfaces scenario. For the live-app scenario (reviewing real UI by clicking real elements), the whole mechanism works without an iframe.

---

## 10 · Findings synthesis: what would "talks back live, interruptibly" actually take?

Starting from today's state, a minimal path to "live conversational grounding with deictic following":

**Step 1: Stream text chat** (makes it feel live)
New endpoint `/api/chat/stream` → drives `chat_parts()` → NDJSON events per part → FE appends each part as it arrives. This alone transforms the experience from "thinking…" (15-30s wait) to "Vi: well, this screen is the… [Part 1 arrives]…inbox region, and the thing you're pointing at is [Part 2 arrives]…the build-review surface where…" First words arrive in ~(context assembly + Part 1 gen + ~500ms on 4B). Realistic: 2-4 seconds to first text.

**Step 2: Compose walkthrough and chat** (makes the guided tour locus-grounded)
When `nextStep` fires, call `indicate(session.raw?.guide_address)`. Now the chat at each stop is automatically grounded at that stop's address. The operator asks "what do I do here?" and gets R2 context at that exact address.

**Step 3: Wire voice focus** (makes voice locus-grounded)
Pass `focus.selected` through `/api/voice/stream`. Voice turns now carry the same locus the typed turns carry.

**Step 4: Emit navigation events + locus trail** (enables temporal deixis)
On each `_current_locus` change, emit `navigate` event with `address=`. `_chat_context` reads the last N navigate events and includes a short "recently viewed: [addresses in order]" line. The 4B model can now resolve "that thing I was looking at before" from this trail.

**These four steps, done in this order, progressively realize the anchor's vision.** Steps 1-3 are wiring/composition. Step 4 is new substrate. None of them require architectural decisions beyond what's already designed. The constraint at each step is: Tim approves the direction → agents implement → verify by use.

**Interruption:** True interruption (speaking mid-reply to cut off the RHM) is possible if: (a) streaming text is live (the FE can stop appending), (b) the client-disconnect detection in `_voice_stream` (`gone[0]` / `client_gone()`) **Observed(bridge.py:780-793)** is extended to text streaming. The voice path already handles barge-in (a new recording cancels the in-flight stream). Text streaming would need a similar cancel path (SSE: client closes the stream; the server detects `gone[0]`). This exists in the voice path architecture and extends naturally.

---

## 11 · Summary of key evidence lines

| Claim | Evidence | Status |
|-------|---------|--------|
| chat() is request/response | suite.py:5223-5242 | Observed ✅ |
| chat_parts() is a streaming generator | suite.py:5264-5312 | Observed ✅ |
| Voice already uses chat_parts streaming | bridge.py:734-903 | Observed ✅ |
| Voice path drops studio focus | bridge.py:848 (no focus arg) | Observed ✅ |
| Locus set from indicated ui:// in chat | suite.py:2133-2142 | Observed ✅ |
| R2 auto-resolves context at locus | suite.py:3036-3086 | Observed ✅ |
| Event log: only 6 events, kind+summary | suite.py:1990 | Observed ✅ |
| No navigation events in event log | suite.py:497-506, event schema | Observed ✅ (gap) |
| Walkthrough does not update chat locus | useAppController.ts + Walkthrough.tsx (no indicate() on nextStep) | Observed ✅ (gap) |
| In-mockup element deixis built | StudioKit.tsx:101-134 | Observed ✅ |
| Unregistered addresses get stub narration | suite.py:6225-6226 | Observed ✅ |
| present_current raises on unregistered address | suite.py:6218-6220 | Observed ✅ (limit) |
| Guide sequences registry | suite.py:6355-6395 | Observed ✅ |

---

The idea is left bigger: the anchor said "locus-grounded conversation" and the code confirms this fully exists. The anchor was quiet on streaming (it's a new seam), quiet on temporal deixis (it needs new substrate), and quiet on the walkthrough↔chat composition gap (one FE line). The resident model is not the blocker — the missing context structure and the missing streaming seam are. Build order: stream first, compose second, temporal trail third.
