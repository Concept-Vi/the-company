# The Cognition Surface — research synthesis + the thinking frame

**Status: Track-1 round 4 (2026-06-10). Four-explorer research pass (concurrent cognition · resolution
machinery · canvas scaffolding-truth · Claude Code integration assets) + the synthesis Tim asked for:
"working out how to display the cognition in a way that I can interact at my level." Companion to
THINKING-MEMORY-IDENTITY-PRESENCE.md (rounds 0–3). Tim's framing holds absolutely: the current UI is
scaffolding built by AI to test that surfaces connect — it is NOT the design; its plumbing survives,
its face does not.**

---

## 1 · Research headlines (what is actually true on disk)

### 1.1 Concurrent cognition — ON MAIN, proven by use
- `runtime/cognition.py` (2555 ln) + `runtime/rules.py` (587 ln) + `contracts/cognition_info.py`.
- One resident 4B runs concurrent rule-routed ROLES — 32 OPTIMAL (corrected; an earlier ~12–14 figure was an AI error since removed; serving max_num_seqs=34) (C0.5: knee = min(max_num_seqs−R,
  free_KV/per_role_ctx); stale per-config knee figures removed — 32 is the corrected width); structured outputs resolve at
  `run://<turn>/<role>`; a STAGED multi-part reply reads them via declared RULES.
- **Rules are renderable data-ASTs** (closed grammar: and/or/not/eq/…/field/lit; no now/random/call;
  deterministic, proven order-independent). FIVE destinations, all non-consequential: inject · chain ·
  address · surface · lane. resolve/approve/dispatch are FORBIDDEN at construction.
- **MODE_REGISTRY is the one source** uniting presence + resolution + staging + budget: each of 8
  modes declares {directive · resolution(strata/howto_detail/budget) · grain · shape · stage · cast ·
  brain_config}. No `if mode==` anywhere. Modes ARE the coarse now-vocabulary, already.
- **CognitionView.tsx EXISTS** (Pulse + River altitudes; Nodes via inspector), fed live by
  `cognition.*` SSE (turn.start/role.fire/role.ran/inject/part/turn.done), folded sync into a turn
  frame. Aesthetic gates are needs-tim. Addressable at ui://cognition/<turn> — the RHM can read its
  own thought-graph at the same address.
- **The held placeholder = the CRAFT SURFACE (C7.3–C7.5):** live thought-viz (C7.3, largely real) →
  canvas AUTHORS cognition (C7.4: create/manage roles, rules, modes FROM the surface) → point at a
  directory, declare structured outputs dynamically, watch the swarm stream results (C7.5).

### 1.2 The resolution machinery — the render-ready spine
- ui:// grammar canonical (contracts/ui_info.py S0, UnionAddressRecord, v2); 483-entry address
  registry; build_ui_info → /api/ui_info; FE resolveUiTarget (camera for canvas, DOM+spotlight for
  chrome) is the SINGLE address-navigation sink.
- `_resolve_context_at` + `_r2_gather`: per-address context resolution (annotations/chat/events/
  howto/prefs/run-trail/cognition strata), mode-parameterized, scored+capped → the inject string.
- `address_help` = the 3-leg bundle (what_this_is · how_to_change(scope+blast radius) ·
  how_to_use), degrade-clean; F1 presentation_prefs (terser/more/lead_with/shape) REAL and applied
  model-free; `/api/up-translate` exists (the altitude envelope).
- `now()` exists (mode · presence · surfaced_pending · last_event) — flat snapshot; the now-ORGAN
  (condition evaluation, dial-override firing) is the designed gap.
- Walkthrough organ: present_current frames ANY ui:// address model-free from corpus help; journeys
  (L9) record/replay address click-paths.

### 1.3 The canvas — scaffolding-truth confirmed
- ~8,267 src lines; useAppController.ts (2,567 ln) is the carved state container; 18 regions; kit.tsx
  primitives (SectionHead/Badge/Surface/EmptyState) on corpus tokens (W2 gold-instrument, no literal
  colors); grid shell + mobile sheets (<699px data-mtab).
- **PLUMBING (survives any redesign):** the 65 /api seams · EventSource /api/stream (seq-dedup,
  kind-dispatch) · resolveUiTarget + indicate (the two keystones) · chat/voice ndjson streaming ·
  NodeShape+Edges tldraw integration (3.15.6, persistenceKey company-canvas-v3) · ui:// registry ·
  review sessions · journey recording · cognition turn-fold.
- **PRESENTATION (discardable scaffold):** all region styling/copy/layout choices. The face gets
  rebuilt; the wiring diagram stays.

### 1.4 Claude Code integration — the assets are in hand
- **The WIRE is on main, complete, inert by default:** runtime/implement.py launches
  `claude -p … --output-format json --permission-mode plan` (COMPANY_WIRE_PERMISSION gates
  acceptEdits; concurrency 3; 900s cap); exactly-once via durable decision.dispatch claim + per-seq
  flock; changed-files from GIT GROUND TRUTH (baseline-hash delta, immune to self-report);
  scope-diff surfaces wandering builds; git checkpoint commit before `implemented`; review item
  surfaced, dispatcher-inert. Only the operator's approve (on a build-intent, AUTO class) dispatches.
- **The Atlas (vault: Spaces/Claude Code Atlas/Custom Apps Integration.md) gives the embed recipe:**
  the Agent SDK (`ClaudeSDKClient` + `ClaudeAgentOptions`: allowed_tools, permission_mode,
  can_use_tool callback, hooks, resume=session_id, mcp_servers) streamed over a small backend →
  ndjson to the FE — the SAME streaming pattern RhmChat already uses. Alternative: stream-json CLI
  per-turn (no session persistence). Channels.md: push-MCP notifications INTO a running session
  (phone-relay approvals; external events) — later.
- **Shortest honest path to the side-chat:** ~150-line UIClaudeSession (Agent SDK, plan-mode
  default) + `/api/claude/start|continue` ndjson routes on bridge.py + a sidebar region on kit
  primitives + INJECT the indicated ui:// address with its address_help + R2 context into the
  session's system prompt. No new substrate; reuses Suite, the address system, the streaming pattern.

---

## 2 · THE THINKING FRAME (Tim: "I don't know how to think about that but I'm hoping you might")

### 2.1 Don't display the machinery — display the RESOLUTIONS
The screen never shows "the system's internals"; it shows what the resolver produced at the position
Tim occupies: what returned here, what fired now, what's proposed, what's waiting on him. The
machinery stays below; what surfaces is always an ANSWER. (The interface is the resolver's face —
round 3 — now grounded in real parts.)

### 2.2 Every moment of the surface answers THREE QUESTIONS — and they are the only
interactions Tim needs:
1. **"What are you doing?"** → the NOW rendered (presence, turns pulsing, runs running, beats
   firing). Machinery: now() + cognition.* SSE + the event stream. Glanceable, ambient, never a log.
2. **"What do you know here?"** → POINT AT ANYTHING and the memory/knowledge AT that address
   renders (address_help's three legs + history + self-changes + what maps here). Machinery:
   indicate + address_help + R2 — all real.
3. **"Why did you do that?"** → any rendered element explains itself on tap: which rule fired
   (rules render as readable infix), which role's output injected, which memory returned, which
   verdict routed it. Machinery: renderable rule-ASTs + run:// lineage + provenance records.
Everything else is composition. Tim never learns the machinery's vocabulary; the machinery answers
in his.

### 2.3 ONE altitude grammar for everything: Pulse → River → Nodes
The cognition view's three altitudes are not a cognition-specific trick — they are THE universal
rendering grammar of the surface:
- **Pulse (glance):** shape + heat. Is it thinking? how much? anything for me? — recognition by
  sight, his native read.
- **River (inspect):** the parts, labeled in plain words — what fired, what it found, what it
  proposes.
- **Nodes (depth):** the full record — primarily for agents; available to him on demand, never
  required.
Memory, builds, the wire, voice — every subsystem renders at these same three altitudes. Default
altitude per region is a learned presentation_pref (F1), not a setting he must manage.

### 2.4 Interaction is POINT + TALK — already the system's native loop
Click an element (indicate — built) and speak/type (chat/voice — built); the address rides with the
utterance (focus/indicated — built); the answer comes back AT his altitude (prefs — built). "Interact
with cognition at my level" is not a new interaction model to invent — it is the existing loop
pointed at the right renderings, with one new conversation partner:

### 2.5 TWO chats, one surface — the entity and the builder
- **Viv (the RHM):** the entity speaking about itself. Always-on, voice-first, presence, walks,
  answers from ground truth, presents at addresses. The COMPANION.
- **Claude Code (the side-chat):** the BUILDER on call. Tim points at anything and says "change
  this / why is this / make me a…" — the session receives the address, its code scope, its
  registry entry, its context notebook, and investigates or implements. The CONTRACTOR, standing in
  the workshop, already briefed.
The WIRE connects them to consequence: a "change this" can mint a build-intent AT the address
(/api/intent-at — built), his approve dispatches it (dispatch_decision — built, gated), the result
renders back at the address for review (built). Claude Code in the sidebar = the conversational face
of the same circuit, with plan-mode (read/investigate) free-roaming and edits always behind his gate.

### 2.6 The COMMAND CIRCUIT (what "taking over my ability to command through it" means)
SEE (the now + work rendered at altitude) → POINT (indicate an address) → SAY (voice/text) →
the system ANSWERS (Viv) / PROPOSES (cards at the address) / BUILDS (Claude Code + the wire) →
the result RENDERS BACK at the address → he APPROVES/ADJUSTS (his gate, in place) → the registries
update → the surface re-resolves. Every arc of this circuit exists in the plumbing today; the build
is the ASSEMBLY plus the face.

### 2.7 The dials govern the surface (built yesterday)
stability=workshop: regions stay where he knows them; contents resolve. anticipation=warm: surfaces
pre-resolve as the now shifts. Both adjustable, both condition-scopable when the now-organ lands.

---

## 3 · SLICE 1 — the early start (Tim's explicit ask)

**The Claude Code side-chat rendered in the application, with click-context riding in.**
1. `runtime/ui_claude_session.py` — Agent SDK session wrapper (~150 ln): plan-mode default,
   allowed_tools read-oriented to start, resume= for multi-turn, system prompt = Company briefing +
   the indicated address's help bundle + R2 context.
2. Two bridge routes: `/api/claude/start`, `/api/claude/continue` — ndjson streaming (the exact
   RhmChat pattern; bridge is ThreadingHTTPServer — reuse, don't parallel).
3. A sidebar region on kit primitives — messages, tool-activity lines ("reading suite.py…"),
   the indicated-address chip (reuse .rhm-indicating), input.
4. The handoff seam: a Claude-chat "build this" mints intent-at(address) → the wire's existing
   review/approve circuit. Edits NEVER flow without his gate (the wire's posture law unchanged).
5. FORM: design-system tokens only; mobile sheet at <699px like the other panels.
Verification by use: point at a node → ask "what is this?" → watch it read the actual code → ask
for a change → see the intent card → approve → watch the wire build it → result renders back.

**Then (the order the frame implies):** the now-organ (presence + injection trigger — the keystone
both Tim's greeting and conditional memory need) → the resolved-surface composition (rules-as-layout
on the stable frame) → the craft surface (C7.4/C7.5: authoring cognition from the canvas) → the
aesthetic pass (the deferred token-single-source redesign) riding the whole way.

---

## 4 · Open threads added by this round
- The Agent SDK availability in this venv (install/version check is step 0 of slice 1).
- Claude session ↔ inbox identity: should Claude-chat conversations be addressed
  (ui://chat/claude/<session>) so THEY accumulate memory like everything else? (Instinct: yes —
  same substrate, no parallel chat store.)
- Voice into the Claude side-chat (the STT seam is shared) — later; Viv stays the voice-first face.
- The greeting resolution (round 1, thread 6) becomes buildable the moment the now-organ exists.
