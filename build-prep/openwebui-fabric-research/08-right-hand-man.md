# 08 — The Right-Hand-Man (RHM): what it is, what's built, and the RHM-as-conversational-layer angle

**Question (lead):** research the RHM — the Company's conversational assistant/guide (the "V-icon
overlay/guide", a *layered collective cognition*, not a single-model agent). What it IS (design intent),
what's BUILT vs DESIGNED-only, and ★ **could the RHM be the conversational layer Tim chats with through
OpenWebUI** — i.e. the RHM as a model+tools that already holds the SUPERVISOR's operations (list/route/wake
members) + the Company's knowledge, so "chatting with the supervisor" is really "chatting with the RHM"?

**Method:** read-only over `/home/tim/company`. Core files read in full or in the load-bearing parts:
`runtime/brain_router.py` (the supervisor-as-brain backend, read fully), `runtime/bridge.py`
(the `/api/brain/ask`, `/api/chat`, `/api/decision/explain` handlers), `runtime/suite.py`
(`rhm_config`, `chat`/`chat_parts`, `address_help`, `up_translate`), `surface/app/src/rhm/RightHand.tsx`,
`build-prep/front-interface/fork-v-brain.js` + `fork-brain-core.js`,
`canvas/app/src/regions/{RhmChat,AddressHelp,CognitionView}.tsx`. Design docs:
`build-prep/the-one-application/{SUPERVISOR-AS-BRAIN,RHM-BRAIN-DISCUSSION}.md`,
`build-prep/coherence/findings/AREA-5-interface-rhm.md`, the `rhm-build` skill, and the sibling research
docs `01-supervisor-cli-fabric.md` / `07-openwebui-fabric-connection.md`. Two explorer sub-agents covered
the backend-mind and the frontend in parallel.

Evidence is tagged **[OBS file:line]** (read directly), **[INF]** (pattern-matched, not executed),
**[IDEA]** (my proposal/extension, not in the code). Nothing here was run end-to-end (no **[VER]**).

---

## 0. THE ONE-PARAGRAPH ANSWER (the angle, settled)

**Yes — and the architecture is already explicitly named and half-built for it.** The RHM's "mind" is not
a single model: `runtime/brain_router.py` is a **source-router** that resolves a question to one of three
cognition sources — `fleet` (the supervisor's live roster + sessions + recent channel traffic), `recall`
(grounded memory, a declared hook), and `model` (the default conversational mind). The `fleet` source
**already reads the supervisor's fabric-sight and surfaces wake/consult as a PROPOSAL it never fires**
[OBS brain_router.py:79-126]. So "chat with the supervisor" ≡ "ask the RHM a fleet question" is **the
designed identity, not a stretch** (`SUPERVISOR-AS-BRAIN.md`). The gap to "Tim chats through OpenWebUI" is
**not the mind** — it's a thin protocol seam: the bridge exposes the RHM at `POST /api/brain/ask` and
`POST /api/chat` in the **Company's own JSON shape**, but OpenWebUI speaks the **OpenAI
`/v1/chat/completions` protocol**, and **no OpenAI-compatible face exists yet** [OBS bridge.py:2918-2921;
grep for `chat/completions` in `bridge.py`/`ops/` returns nothing]. Closing that one adapter is the whole
build (§5).

---

## 1. WHAT THE RHM *IS* — the design intent (layered collective cognition)

The RHM is the **one persistent, loadable "mind" behind the V-icon** that the operator talks to and clicks
to direct the whole system. It is, by design, **a composed cognition, not one model**. Four design strands,
all grounded:

1. **The conscious-perceives-a-resolved-view model.** The operator never sees code, files, or machine
   names — only human MEANING; the technical address rides server-side as the brain's context handle. The
   `PANEL_BRIEFING` law forbids raw addresses/`scheme://` in replies; the operator gets a human aim-label,
   never the address [OBS AREA-5 §2 / RHM-BRAIN-DISCUSSION.md:50,75,78]. This is the "altitude transformation
   layer" — Tim's intent up-translated, the depths kept hidden but reachable.

2. **The two-way altitude transformation.** `up_translate(kind, ref)` is the generalized "present at Tim's
   altitude" resolver [OBS suite.py F1 / AREA-5 §1.1] — and it **already has a `kind=="finding"` branch**
   that frames a coherence/drift finding at altitude and enriches it with blast-radius (the "what would
   change touch" leg). `address_help(ui_addr)` composes three legs at one address —
   `what_this_is · how_to_change(scope+blast_radius) · how_to_use` — degrading cleanly per leg
   [OBS suite.py:2174-2265 per AREA-5]. The down-direction (Tim's words → action) is the verb fan + the
   write-back wire (§3).

3. **The mind RESOLVES which cognition-source answers** (the "loadable brain"). This is
   `resolve(invariant, coordinate)` at the cognition-source scale — the SAME resolver primitive a surface
   uses to pick an allocation by device-coordinate, lifted one altitude to pick a *source* by question-shape
   [OBS brain_router.py:10-12, 43-54; SUPERVISOR-AS-BRAIN.md §★]. Which sources are mounted is itself a
   registry/loadout (axes-are-registries) — a given RHM instance composes the sources its context needs.

4. **The brain is a ROLE that resolves to a model, never a pinned model.** The conversational source picks
   its model by the TIM-RULE context-size pick (`pick_ollama_model_for_context` — kimi for a normal ~12-16K
   interactive turn, the cheap 1M deepseek-flash only when context exceeds kimi's window, never `-pro` unless
   explicit) [OBS brain_router.py:133-169]. The brain = one row in the role→model resolution
   (the native-model-layer's first real instance).

**Tim's verbatim framing** (mined, RHM-BRAIN-DISCUSSION.md:14, line 5307): *"every capability through the UI
is also accessible through the right hand man… it can change everything about the screen… a follow-me mode
and another where I follow it… I wonder if and how claude could 'plug in' to the company, pilot the right
hand man… most of it hasn't been built and it's not in any use… but it has such high value potential."* The
N+1 / "so many minds but possible for one" passage (line 5418) is the multi-source/mind-swap intent.

> **Vocabulary caution (advisor-caught in the source mine):** "loadable brain" is the *fabric's* working
> term, faithfully derived from Tim's intent — NOT a verbatim Tim quote. Tim's actual coinages are
> *"plug in / pilot the right-hand-man"* and the *N+1* passage [RHM-BRAIN-DISCUSSION.md:16].

---

## 2. WHAT'S BUILT vs DESIGNED-ONLY (honest, file-grounded)

### 2a. The conversational mind — BUILT and reachable

| Piece | State | Evidence |
|---|---|---|
| **Source-router** (`route_source` → fleet/recall/model; `ask()` composes, fail-soft to model) | ✅ BUILT | `brain_router.py:43-54, 172-203` |
| **`fleet` source** — reads live roster (`fold_channels`) + sessions (`list_agent_sessions`) + recent channel traffic, DISCUSSES it via a folded model turn, surfaces wake/consult as a **proposal** | ✅ BUILT (read+propose) | `brain_router.py:79-126`; `recent_channel_context` `:57-76` |
| **`model` source** — `Suite.chat`, role-resolved model (kimi), aim-grounded via `territory_prose` | ✅ BUILT | `brain_router.py:136-169`; `suite.chat` returns `{reply, action, proposal, mode, model, thread_id}` |
| **`recall` source** — grounded memory | 🟡 DECLARED HOOK | `brain_router.py:184-191` — v1 routes to the tool-grounded model + flags recollection's `session_search`/`recall_for_decision` as the richer source to wire |
| **HTTP face** `POST /api/brain/ask {question, aim?, graph_id?}` | ✅ BUILT | `bridge.py:2460-2473` — "NOT a consequential-write door (no gate)" |
| **HTTP face** `POST /api/chat {message, focus?}` (the grounded RHM conversation) + `POST /api/chat/stream` (incremental parts) | ✅ BUILT | `bridge.py:2918-2921`, `:2863` |
| **`/api/decision/explain`** — composes recollection grounding + per-subtype policy + `explain_role` framing at altitude; defaults to the live `rhm_config().model` | ✅ BUILT | `bridge.py:2474-2514` |
| **`rhm_config()`** — 14-key config (mode, model, persona, voice, brain_knobs); `model` defaults to `DEFAULT_BRAIN` = `deepseek-v4-pro:cloud` (env `COMPANY_BRAIN`); mode default `listening`; persisted to the system graph node `rhm` | ✅ BUILT | `suite.py:2768-2808`; `fabric/config.py:21` |
| **Learned-twin / presentation-pref (F1)** — `set_presentation_pref`→annotation, `presentation_pref_at` latest-wins, `_apply_presentation_pref` reorders/words; gathered as a non-decaying stratum by `_r2_gather`; twin output never re-trains (echo-guard) | ✅ BUILT | `suite.py:5584-5678`, `:2928-2972` |

> **Config note (slight tension to flag):** `DEFAULT_BRAIN = deepseek-v4-pro:cloud` [OBS fabric/config.py:21]
> is the `rhm_config().model` / `/api/decision/explain` default, but `brain_router._model_answer`
> deliberately **overrides** it with the kimi context-size pick [OBS brain_router.py:145-147] — honoring
> the cognition-is-role-resolved rule and the "never -pro unless explicit" rule. So which model actually
> answers depends on the path: `/api/brain/ask` → kimi (role-resolved); `/api/chat` → `SUITE.chat`'s own
> pick; `/api/decision/explain` → `-pro` unless overridden. Worth a single resolution so the RHM's mind is
> one consistent role, not three path-dependent picks. **[INF, grounded in the two cited lines]**

### 2b. The V-overlay surface (the operator-facing organ) — mostly BUILT

The V-icon overlay is `surface/app/src/rhm/RightHand.tsx` — a persistent, draggable bottom-right overlay on
every page with a 6-verb radial fan. The host holds NO model knowledge; it mounts whatever brain
`window.forkVBrain.attach({panelEl, getAimAddress, getAimLabel})` returns (the **swap-seam**: a new brain
satisfying the `Brain` contract drops in with zero host change) [OBS RightHand.tsx:106-127;
SUPERVISOR-AS-BRAIN.md §seam].

| Verb / leg | State | Evidence |
|---|---|---|
| `navigate` (Go to), `open-source` (See the record) | ✅ wired (dispatch `gallery:verb`) | RightHand.tsx:25-32, 444-446 |
| `ask` (Ask) — **the TALK leg** | ✅ BUILT + verified-by-use | opens panel → `groundedAsk()` → `POST /api/brain/ask` → self-renders (fork-v-brain.js:89-106); the streaming sibling `talk()` → `POST /api/claude/turn` NDJSON with **per-address session continuity** (`_sessions[address]` + `--resume`) (fork-brain-core.js:43-104) |
| `annotate` (Note) — **CLICK-ASK record half** | ✅ BUILT | `direct()` → `writeDirections()` → `POST /api/territory/write` → `suite.mark` → `gallery:rerender` (fork-v-brain.js:156, fork-brain-core.js:137-182) |
| `drive` (Drive), `generate` (Make) | 🔴 STUB (`live:false`, shown dimmed "soon") | RightHand.tsx:30-31 |
| **CLICK-ASK change/generate half** (the KEYSTONE — read direction → GENERATE → write output) | 🔴 DESIGNED-ONLY | `SPEC-direction-to-generate-wire.md` — "the ONE unbuilt rung"; same wire retargeted by address IS composition's factory |
| `postToChannel()` — V posts to a channel | ✅ BUILT, **ungated** | fork-v-brain.js:133-145 → `POST /api/channel/post` (Tim's choice: open) |
| 3-question proactive starters / guided tour | ✅ BUILT | RightHand.tsx:43, 251, 578-622 |
| In-canvas siblings: `AddressHelp.tsx` (3-leg explain, altitude drill-down, F1 pref marker), `CognitionView.tsx` (Pulse/River/Nodes, reflects-never-owns, `cognition.*` SSE), `RhmChat.tsx` (canvas chat + record/debrief loop) | ✅ BUILT | the three regions; `cognition.*` SSE fold in `useAppController.ts` |

### 2c. DESIGNED-ONLY (named, not built)
- **Mind-swap MODES** (Claude Code ↔ other models ↔ N+1 concurrent sessions, swap per use, "as an extension
  to the mode system") — Tim 5418; the brain seam is one interchangeable composition, but the swap-the-mind
  UI is unbuilt [RHM-BRAIN-DISCUSSION.md:33, 105].
- **Follow-me / piggy-back modes** (bidirectional drive; "follow me" vs "I follow it") — Tim 5307/5418;
  piggy-back explicitly "not described or designed anywhere yet".
- **The keystone GENERATE-write** (§2b) — the single unbuilt router step; also the composition seam.
- **The real V *organism*** (vs the gold-icon placeholder) — swap-seam open, renders into the RightHand
  container.
- **The RHM Walkthrough Organ** — a whole separate planned build (the `rhm-build` skill + `RHM Walkthrough
  Organ — Completion Criteria.md` with S1–S7 scenarios): the RHM *walks the operator through* the surface,
  per-step voice, a review/verdict loop. Branch `rhm-walkthrough-organ`, off `operable-surface`. This is the
  "RHM as guide/tutorial" facet — designed in depth, build-loop defined, status separate from main.

---

## 3. THE SUPERVISOR OPERATIONS THE RHM CAN ALREADY REACH (the angle's foundation)

The session supervisor (`runtime/session_supervisor.py`, HTTP on `:8771`) owns the fleet lifecycle. Its
op-set, split by consequence [OBS session_supervisor.py, cross-checked with 01-supervisor-cli-fabric.md]:

- **READ (safe — the brain consumes these freely):** the `agent_sessions` event log (single-writer:
  `spawned/turn/idle/closed/registered`), `list_agent_sessions` (every CC session, newest-first,
  filterable), `fold_channels` (the named-channel roster), recent channel traffic, recall by meaning. These
  are exactly what the `fleet` source reads [OBS brain_router.py:83-86, 104].
- **CONSEQUENTIAL (lead-only, GATED — the brain PROPOSES, never fires):** `POST /spawn` (`claude -p` / fork
  a point-in-time session), `POST /inject` (push text into a live session), `POST /channel-send`,
  `/interrupt`, `/teardown` [OBS session_supervisor.py:1572-1665, the route table :131-132]. Per-turn
  watchdog (reaps turns >900s), concurrency cap (3 live, env-tunable).

**The floor (non-negotiable, and already honored):** the supervisor-as-brain exposes only READ + PROPOSE.
A fleet answer that implies an action returns it as a `{kind:"supervisor_action", is_gated:true,
suggestion, note:"floor: brain proposes, never dispatches"}` proposal [OBS brain_router.py:92-98] — the mind
*reaches* the gated verb (it can say "I could wake session X") but the operator/lead fires it
(`autonomous-spawn-lead-only`). This is the institutional safety that makes a chat-with-the-supervisor face
safe to expose.

---

## 4. THE ANGLE, IN FULL — RHM as the conversational layer over the supervisor through OpenWebUI

**Restated:** instead of OpenWebUI being a dumb chat box that hand-calls a pile of fabric tools, OpenWebUI
chats with the **RHM as its model**. The RHM already (a) routes fleet questions to the supervisor's
read+propose sight, (b) up-translates everything to Tim's altitude, (c) is role-resolved (kimi), (d) grounds
on the corpus + aim. So "chatting with the supervisor" = "chatting with the RHM" is **the existing design,
exposed over one more protocol.** Two complementary shapes, which can BOTH be built (they layer):

### Shape A — RHM-as-the-MODEL (the headline; the RHM *is* who Tim talks to)
OpenWebUI points its "model" at a Company endpoint that wraps `brain_router.ask`. Every Tim message goes
through the source-router: fleet questions → the supervisor's sight (with proposals), recall questions →
memory, everything else → the grounded conversational mind. **This is the truest read of "chatting with the
supervisor is really chatting with the RHM"** — the supervisor is one *source inside the one mind*, not a
separate tool the user must invoke.

- **What's there:** the whole mind + `POST /api/brain/ask` [OBS bridge.py:2460-2473].
- **The one real gap — protocol:** OpenWebUI talks to a "model" via the **OpenAI `/v1/chat/completions`
  protocol** (`{model, messages:[…]}` → `{choices:[{message:{content}}]}`, optional SSE deltas). The bridge
  returns the **Company shape** (`/api/brain/ask` → `{ok, source, answer, proposal?, …}`; `/api/chat` →
  `SUITE.chat(...)` = `{reply, action, proposal, …}`) [OBS bridge.py:2918-2921]. **No `/v1/chat/completions`
  face exists** (grep confirms). So the build is a **thin OpenAI-protocol adapter** in front of
  `brain_router.ask` — map `messages[-1].content` → `question`, the prior turn / a session header → `aim`,
  and the `answer` → `choices[0].message.content`. Streaming maps onto `/api/chat/stream`'s parts
  [OBS bridge.py:2863]. **[IDEA, grounded]**
- **Where the proposal goes:** a fleet answer's `proposal` (a gated wake/consult) can't be a silent tool
  call in this shape — render it **in the reply text** as "I could wake session X — say the word" (the
  propose-floor, made conversational), and/or surface it on the existing decision/stack surface. The actual
  fire stays a separate gated action (§3). **[IDEA]**

### Shape B — RHM-mind + supervisor-TOOLS via mcpo (model-driven agency)
Per `07-openwebui-fabric-connection.md §4`, **mcpo** republishes the `company` / `company-channel` MCP tools
as OpenAPI so an OpenWebUI model calls `sessions`, `channels`, `cc_channel`, `inbox`, `session_recall`,
`channel_act` as native tools. Use a **curated subset** (a thin re-export MCP) so the model isn't flooded
[OBS 07 §4, INF the flood risk]. This gives the chat model *agency* over the read fabric. **B complements
A:** A makes the RHM the *voice and the router*; B gives that voice *live tool reach* into the supervisor's
read surface. The propose-floor still binds — the consequential verbs (`/spawn`, `/inject`) are NOT in the
curated set, or are exposed as propose-only.

### How inbound/outbound resolve (cross-ref doc 07)
- **Outbound** (Tim → fabric) is the easy direction and needs **no fabric change**: an OpenWebUI Tool calls
  the already-live bridge routes (`/api/channel/post`, `/api/sessions`, `/api/channels`) server-side
  [OBS 07 §3]. With Shape A the RHM mediates; with Shape B the model calls them directly.
- **Inbound** (fabric → Tim's OpenWebUI chat) is the genuinely-missing transport. OpenWebUI *can* receive
  injected messages (`POST /api/v1/chats/{id}/messages/{mid}/event` with an admin key), but the fabric won't
  push for free — cheapest-today is OpenWebUI **polling** `/api/channel-history`; cleanest first-class is a
  new `transport:"webhook"` branch + a labelled `openwebui` member [OBS 07 §1, §5]. This matters for "the
  fleet messages Tim", less for "Tim asks the RHM and it answers" (that's request/response, already there).

### Auth / topology constraints (carry, don't trip on)
- The bridge has **no CORS / no `do_OPTIONS`** and a process-scoped operator-token gate on a few
  consequential routes [OBS 07 §2a / bridge.py:503-534]. So OpenWebUI must reach the bridge **server-side**
  (an OpenWebUI Tool/Pipe from the OpenWebUI backend), not via browser fetch — which is the recommended
  pattern anyway. The OpenAI-adapter (Shape A) is likewise a server-side endpoint.
- Reachability to Tim's phone rides the existing Tailscale tailnet (doc 06) — no new exposure needed.

### Feasibility verdict
**High, and small.** Shape A is one OpenAI-protocol adapter (~one endpoint mapping
`messages↔question/aim↔choices`, + an SSE map onto `/api/chat/stream`). Shape B is mcpo + a curated tool
re-export (mostly config). The mind, the supervisor-source, the propose-floor, the role-resolved model, and
the read routes **already exist**. The only true new code is the protocol adapter; everything else is
compose-don't-parallel. **Risk to name:** resolving the 3-path model inconsistency (§2a config note) so the
RHM Tim meets in OpenWebUI is the *same* role-resolved mind he meets behind the V-icon — otherwise OpenWebUI
could silently talk to `-pro` while the V talks to kimi.

---

## 5. RECOMMENDATION + NEXT-STEP OPTIONS

**Recommended framing for Tim:** treat OpenWebUI not as a new brain but as **a second face on the one RHM
mind** — Shape A (RHM-as-model via an OpenAI adapter) as the spine, Shape B (mcpo tool reach) layered for
agency. This keeps "one entity, not many agents": the supervisor is a *source inside the RHM*, the V-icon
and the OpenWebUI chat are two faces of the *same* mind, and the propose-floor holds on both.

- **Option A (depth):** Trace one real fleet question end-to-end — `brain_router.ask("what's running right
  now? could you wake the projection session?")` → the `fleet` source → roster+traffic fold → the proposal
  shape — and confirm by USE what the `answer` + `proposal` actually look like, so the OpenAI-adapter maps a
  *real* payload, not an inferred one. (My router claims are [OBS]; the end-to-end shape is [INF].)
- **Option B (dealer's choice):** Pin the OpenAI-protocol adapter contract jointly with doc 07's transport
  decision — one short spec: the `/v1/chat/completions` request/response/stream mapping, where the
  `proposal` renders, and the curated mcpo tool subset. The cross-stream artifact the two docs share.
- **Option C (artifact):** I draft the thin OpenAI-adapter endpoint (`/v1/chat/completions` →
  `brain_router.ask`, non-stream first) as a tentative, clearly-provisional patch against `bridge.py`, plus
  the model-resolution unification (§2a), so Tim can SEE the RHM answer through an OpenAI client and react to
  the real thing. *(My lean: C — it's small, it makes the headline angle tangible immediately, and it forces
  the one real decision (model unification) into the open.)*
- **Option D:** Resolve the §2a config tension first (one role-resolved model across all three paths) as a
  standalone hygiene pass, independent of OpenWebUI — it's correct regardless and de-risks A.
