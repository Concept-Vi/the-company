---
type: map
area: runtime-core
status: descriptive
coverage:
  files_read: 8
  files_total: 85
  last_read: 2026-06-28
---

# Runtime Core Engine — Complete Inventory

The central spine of the Company fabric: the orchestration layer that owns session lifecycle, coordinates cross-session messaging, routes supervisor actions, and provides the read-side view of the live fabric state.

---

## Core Modules (8/8)

### 1. **suite.py** (12,168 lines) — The Shared Brain
**Path**: `/home/tim/company/runtime/suite.py`

**What it is**: The stateless application layer — a Suite instance owns the store + registry and exposes 50+ generic verb methods for graph operations, session lifecycle reads, cascades, voice, and the UI capabilities surface. NOT per-session; operates on the addressed repository.

**Public Surface (partial high-value list)**:
- `class Suite(store, registry, nodes_dir, role_registry)` — initialization with three registries (node, role, projection)
- **Graph/Canvas ops**: `node_info()`, `edges()`, `connect()`, `delete_node()`, `move()`, `run()` (execute a graph)
- **State/Queries**: `state()` (node status), `project()`, `layers()`, `capabilities()` (introspection)
- **Session lifecycle**: `list_agent_sessions()`, `get_agent_session()`, `agent_session_timeline()` — reads the fold over agent_sessions events (NO spawn/resume — that's the supervisor)
- **Cascade system**: `save_cascade()`, `list_cascades()`, `get_cascade()`, `run_cascade()` (templated multi-step)
- **Voice logging**: `voice_log(event, **data)` — durable voice events
- **Chat models**: `available_models()`, `refresh_models()`, `models_at()`, `chat_models_detailed()`
- **Model context**: `chat()` (unified turn-runner via fabric.client)
- **Data materialization**: `discover_capabilities()` (scan for executable nodes)
- **Doc drift**: `refresh_self_description()`, `doc_drift()` (self-model coherence checks)

**Key constants**:
- `CONTENT_KINDS = ("constant", "document", "code", "file", "image", "source", "portal")`
- `NODE_STATES` — registry of 7 state types (idle, ran, cached, stuck, failed, live, empty) with render/icon/token metadata
- `RHM_VERB_SPECS`, `MODE_SPECS` — typed verb/mode registries (dataclass-based, not dicts)

**Notable/Surprising**:
- **Does NOT spawn/resume sessions** — Suite is read+model-run only; the supervisor service is the sole spawner (session_supervisor.py)
- **Model is the TIM-RULE pick** — `_model_answer()` uses `pick_ollama_model_for_context()` to resolve the brain model dynamically (kimi default, deepseek-flash for large context), not a hardcoded DEFAULT_BRAIN
- **No hardcoded state→verb mappings** — verb/mode specs are dataclass registries, not parallel dicts (single source to prevent drift)
- **150+ /api routes** registered here and dispatched in bridge.py; BRIDGE_ROUTES is the single source
- **Imports render_declaration** (session_supervisor.py reuses it) — the render-layer that every claude emit declares
- **SIZE**: 12K lines — the largest single module; includes full session_supervisor.py doc in its module docstring

**Connected to**:
- `store.fs_store.FsStore` — the addressed store (reads only here)
- `runtime.registry.NodeRegistry` — the graph registry  
- `runtime.roles.RoleRegistry` — the role/persona registry
- `runtime.projections.ProjectionRegistry` — the lens/projection registry
- `runtime.scheduler` — graph execution engine
- `runtime.governance` — the inbox + action-class guards
- `runtime.cognition` — the brain's language-model layer
- Bridge (bridge.py) — the HTTP face calls 50+ Suite methods
- MCP face (mcp_face/server.py) — calls the same methods

**Live/Dormant**: LIVE — core application logic

---

### 2. **bridge.py** (3,663 lines) — The Operator Console & HTTP Face
**Path**: `/home/tim/company/runtime/bridge.py`

**What it is**: The UI face — a ThreadingHTTPServer that dispatches 150+ HTTP routes, each calling Suite methods or cognition functions. Built on stdlib http.server (no Flask/FastAPI). Serves the operator console (canvas/studio), mockup gallery, design-system CSS, and all `/api/*` endpoints.

**Public Surface (HTTP Routes)**:
- **Static pages**: `/studio` (the canvas designer), `/design-system.css`, `/mockups/<name>.html`
- **Read-only info routes** (60+):
  - `/api/graph`, `/api/graphs`, `/api/capabilities`, `/api/cognition_info`
  - `/api/sessions`, `/api/channels`, `/api/timeline`, `/api/board`, `/api/flows`, `/api/cascades`, `/api/routines`
  - `/api/transcript-search`, `/api/session-recall`, `/api/channel-history`, `/api/session-describe`
  - `/api/brain/ask` — the supervisor-brain source router
  - `/api/models`, `/api/chat-models`, `/api/voice`, `/api/personas`, `/api/tools`
- **Canvas/graph mutations** (40+):
  - `/api/node` (POST to create/update), `/api/connect`, `/api/delete-node`, `/api/move`
  - `/api/run` (execute a graph), `/api/set`, `/api/apply`, `/api/checkpoint`, `/api/pin`
- **Mockup & design**:
  - `/api/corpus`, `/api/mockup-feedback`, `/api/mockup-feedback/status`, `/api/mockup-generate`
- **Voice & audio**:
  - `/api/tts`, `/api/stt`, `/api/voice/stream`, `/api/voice/turn`, `/api/voice/engine-knobs`, `/api/voice/log`
  - Multi-engine routing via `ENGINE_PORTS` map (kokoro/chatterbox/orpheus/cosyvoice/xtts/qwen3tts)
- **Cognition/role runs** (model-execution layer):
  - `/api/cognition/run_role`, `/api/cognition/run_items`, `/api/cognition/run_reduce`
  - `/api/cognition/create_role`, `/api/cognition/role/edit`, `/api/cognition/role/dry_run`
- **Streaming routes** (via `split("?")[0]`):
  - `/api/chat/stream`, `/api/voice/stream` (not in BRIDGE_ROUTES literal until the drift-gate learned the form)
- **Proposal/decision flow**:
  - `/api/decision`, `/api/propose`, `/api/decision/explain`, `/api/decision/decided-signals`
  - `/api/decision/update`, `/api/decision/propose`, `/api/decision/proposals`
- **Operator session** (overnight lane):
  - `/api/operator-session`, `/api/claude/turn` (embedded Claude Code session for the builder side-panel)

**Key functions**:
- `class H(BaseHTTPRequestHandler)` — request dispatcher
  - `do_GET()` — 60+ path branches
  - `do_POST()` — 40+ path branches
  - `_send(code, body, ctype)` — response writer
  - `_stream(q)` — streaming generator loop (tools, chat, voice)
- `_safe_mockup_path(name)` — path-traversal guard (two-gate: regex + realpath check)
- `_corpus_index()` — gallery discovery (disk-based, not hardcoded)
- `_tts_base_url(engine)` — route TTS requests to per-engine ports
- `_tool_gate(name, args, confirm, operator_token)` — FAIL-CLOSED tool permissioning
- Streaming helpers: `_stream_parts()` (sentence splitting), `_warm_vector_cache()`, `_freshness_loop()`

**Notable/Surprising**:
- **No Flask/FastAPI** — stdlib http.server only (the 3K lines include full route table)
- **Tool posture is call-time** — `_tool_posture(name, exposure, overlay)` computes live from tool manager (tools can be locked/consent/safe/open)
- **Operator token generation** — `_mint_operator_token()` creates one-time tokens; `_is_genuine_operator(token)` validates against a server-side secret
- **Voice multi-engine** — ENGINE_PORTS map is the routing table; unknown engine = fail loud (no silent fallback)
- **Mockup meta is data, not code** — reads `design/_system/corpus-meta.json` at startup (registry-is-truth)
- **Streaming contract is SINGLE** — all streaming (chat/voice/tools) uses the same `_stream(q)` generator pattern
- **Path is NOT derived from Suite** — bridge defines its own BRIDGE_ROUTES constant; Suite lazy-reads it at capabilities() call time
- **Imports cognition as _cog** — the brain language-model layer (run_role/run_items/run_reduce)

**Connected to**:
- `runtime.suite.Suite` — the application logic
- `runtime.cognition` — the language-model runner
- `runtime.generate_mockup` — the committed generate-for-mockups engine
- `runtime.activation_driver` — the always-on activation caller (Group H/I)
- `fabric.config` — the store dir + model/TTS URLs

**Live/Dormant**: LIVE — primary operator interface

---

### 3. **session_supervisor.py** (1,711 lines) — The Session Fleet Owner
**Path**: `/home/tim/company/runtime/session_supervisor.py`

**What it is**: A long-running SERVICE (not imported by MCP face; runs separately) that OWNS N concurrent Claude Code subprocesses. Spawns, resumes, injects user turns, streams events, tears down. Transport: held-open stdin + `--input-format stream-json`. Writes the ONLY agent_sessions.* events (single-writer law, audit C6).

**Public Surface (HTTP API, 127.0.0.1:8771)**:
- `GET /health` — {ok, service, sessions, cap, turn_timeout_s, bind}
- `GET /sessions` — every owned session's record (state machine: starting → idle ⇄ busy → closed)
- `GET /watch?session=<id>` — ndjson stream of that session's events (replay + live)
- `POST /spawn` — {cwd, resume, fork, name, prompt, source?} → new/resumed session
- `POST /inject` — {session, message, source?} → inject a turn into a live session
- `POST /interrupt` — {session} → send control_request to stdin
- `POST /teardown` — {session} → terminate a session
- `POST /bridge-session` — {operator_consent, capabilities, extra_tools, ...} → consent-gated wider-allowlist spawn (R1-prime)

**Key classes/functions**:
- `class Supervised` — one owned subprocess + supervisor-side state (state machine: starting → idle ⇄ busy → closed)
- `class SessionSupervisor` — owns the fleet under a threading.RLock
  - `spawn()` — new/resume/fork (validates flags via registry, checks cap, starts reader/stderr drains, waits_init)
  - `spawn_bridge_session()` — R1-prime wider-allowlist spawn with operator consent gate
  - `inject()` — deliver a message to a live session via stdin (queued in supervisor's own mailbox)
  - `interrupt()` — send control_request (the --input-format stream-json injection contract)
  - `_reader()` — daemon thread that parses stdout stream-json events (captures claude_session_id at system/init)
  - `_drain_stderr()` — daemon thread that drains the OS pipe (prevents child from blocking) + keeps a 50-line tail
  - `_live()` — [Supervised] list of non-closed sessions
  - `_cap_check(adding)` — COMPANY_FABRIC_CONCURRENCY enforcement (teach-loud on overflow)
  - `emit(kind, summary, durable=...)` — single-writer events onto agent_sessions.jsonl
- `_apply_spawn_flags(cmd, flags, consent=bool)` — R1.3 registry-declared flag validation
  - Validates against SPAWN_FLAG_ASSEMBLY (unknown key → TeachingRefusal)
  - Derives posture from Mirror-Registry rules (_registry_posture) — locked/hazard/consent/safe
  - Refuses consent-posture flags without operator_consent
  - Swaps allowedTools/mcp-config when kind='swap'
- `_build_spawn_cmd()` — PURE cmd builder (byte-identical to old when no params, unit-testable)
  - Locked head: --input-format stream-json (the T2 injection contract)
  - Handles provider='ollama' → `ollama launch claude --model <tag> -- ...` (not env)
  - Handles --model, --effort, --fallback-model, --permission-mode, --settings, --add-dir, --debug, --safe-mode, --bare
- `_build_bridge_session_cmd()` — R1-prime builder (wider allowlist, acceptEdits permission default)
- `_resolve_bridge_tools()` — maps capabilities (git/lsp/web/edit) to --allowedTools
  - REFUSES LOUD on computer/browser (host/rail boundaries, never silent)

**Constants/Laws**:
- `SUPERVISOR_ROUTES` — (method, path) registry (tests/supervisor_routes_acceptance.py drifts against it)
- `SPAWN_FLAG_ASSEMBLY` — {body_key: {flag, kind, teach}} — registry-declared, no hand-posture column (posture is DERIVED)
- `BRIDGE_SESSION_TOOLS` — ("mcp__company", "Bash", "Edit", "Read", "Glob", "Grep", "WebFetch", "WebSearch")
- `BRIDGE_SESSION_PERMISSION` — default "acceptEdits" (not plan = would defeat the profile)
- `fabric_concurrency()` — call-time env read (COMPANY_FABRIC_CONCURRENCY, default 3)
- `fabric_permission()` — call-time env read (COMPANY_FABRIC_PERMISSION, default "plan")
- `turn_timeout_s()` — call-time env read (COMPANY_FABRIC_TURN_TIMEOUT_S, default 900 = implement.py DEFAULT_TIMEOUT_S)

**Notable/Surprising**:
- **NOT imported by MCP face** — the supervisor is a separate service (synthesis §6.3 split); MCP writes intents to mailbox, supervisor is the only spawner
- **Held-open stdin injection** — T2-proven (~/xsession-tests/RESULTS.md): one claude subprocess per session, holds stdin open under --input-format stream-json, accepts injected turns
- **Single writer to events.jsonl** — audit C6 law: supervisor is the ONLY process emitting agent_sessions.* events
- **Registry-derived posture** — F-FIX-5 step 5: spawn flags' posture (locked/consent/safe) is NO LONGER a hand-column; it's DERIVED from Mirror-Registry rules at call time
- **Provider routing via launcher** — provider='ollama' runs `ollama launch claude --model <tag> --` NOT env overlay (env overlay fails with logged-in Claude)
- **Self-ID injection** — resume spawns inject COMPANY_SESSION_ID env so child's resolve_own_session("self") works unambiguously
- **Concurrency cap enforced + taught** — TeachingRefusal names the limit, live sessions, env var, how to free a slot
- **Computer-use refused-loud** — never green-painted as a silentn-never-bind allowlist entry (§5.4 honesty)
- **Consent gate, not lockout** — R1-prime wider spawn requires operator_consent signal; the profile is ALWAYS available (consent-not-lockdown)

**Reads from**:
- `.data/agent_sessions/mail.jsonl` — the mailbox (intents to spawn/inject/consult)
- `.data/agent_sessions/cursor:supervisor` — the cursor (consumed byte offset)
- Mirror-Registry (platforms/claude_code.py) — flag posture + body-key map

**Writes to**:
- `.data/events.jsonl` with kind=agent_sessions.spawned/agent_sessions.turn/agent_sessions.closed
- `.data/agent_sessions/cursor:supervisor` — cursor after consuming intents

**Live/Dormant**: LIVE — the session fleet backbone

**Run command**: `.venv/bin/python runtime/session_supervisor.py [port]` or `company up session-supervisor`

---

### 4. **brain_router.py** (203 lines) — The Supervisor-as-Brain Source Router
**Path**: `/home/tim/company/runtime/brain_router.py`

**What it is**: The backend half of the RHM (Right-Hand Mind) — routes questions to the right source (fleet/recall/model) and composes answers. The FRONTEND half is window.forkVBrain (DOM module in surface/.../RightHand.tsx).

**Public Surface**:
- `route_source(question: str) -> str` — deterministic pick: 'fleet' | 'recall' | 'model'
  - Keywords: _FLEET_HINTS ("fleet", "session", "wake", "consult", "supervisor", "what is running", …)
  - Keywords: _RECALL_HINTS ("remember", "recall", "history", "transcript", "what happened", …)
  - Else: 'model' (default fallback)
- `recent_channel_context(suite, channel=None, limit=12)` — L4 brain read tool
  - Returns {recent: [{channel, from, message, ts, seq}], n}
  - Composed from session_channels.channel_events_since (same read /api/channel-history serves)
- `ask(question, suite, aim=None, graph_id="codebase") -> dict` — THE BRAIN
  - Resolves source, composes answer
  - FAIL-SOFT: down source → degrade to 'model' with note
  - Returns {source, answer, ...} (+ routed_from on degrade)
  - Handlers:
    - `_fleet_answer()` — supervisor source (read fleet + propose gated action)
    - `_model_answer()` — conversational brain (Suite.chat + TIM-RULE model pick)
    - recall source — DECLARED HOOK (recollection owns the backend)

**Key functions**:
- `_fleet_answer(question, suite)` → {source, answer, fleet, proposal?}
  - Reads session_channels.fold_channels (live channel roster)
  - Reads Suite.list_agent_sessions (live session list)
  - May fold recent channel traffic + run a model turn for answer-depth (L4 discussion, not counting)
  - PROPOSE (never fire): surfaces gated actions for the operator/lead
- `_model_answer(question, aim, suite, graph_id)` → {source, answer, raw, brain_model, brain_pick}
  - Uses pick_ollama_model_for_context (_BRAIN_CTX_ESTIMATE ~12-16K)
  - Resolves to kimi (default, fits 256K window) or deepseek-flash (only if context > kimi)
  - Folds aim-grounded territory_prose if aim is set
  - Calls Suite.chat (the grounded RHM mind)

**Notable/Surprising**:
- **Tiny module** (203 lines) — a discrete source-selection primitive, not a parallel brain engine
- **READ + PROPOSE only** — never spawns/wakes (floor: brain proposes, lead/operator fires)
- **Fleet answer includes proposal** — suggests the operator can wake/consult; the answer doesn't fire
- **Model is TIM-RULE, not hardcoded** — the brain resolves its model dynamically per context size
- **Fail-soft degradation** — a down source doesn't crash; it degrades to 'model' with a note
- **Recall is a seam** — v1 routes recall questions to the model (which is itself grounded); recollection's richer lane is flagged to wire

**Connected to**:
- `runtime.session_channels` — fold_channels (channel roster)
- `runtime.suite.Suite` — list_agent_sessions, chat (the model)
- `runtime.cc_clone` — (implicit: clones appear in session list)
- `runtime.territory` — territory_prose (aim-grounded context)

**Live/Dormant**: LIVE — the /api/brain/ask endpoint calls this

---

### 5. **cc_channels.py** (563 lines) — Cross-Session Live Messaging Transport
**Path**: `/home/tim/company/runtime/cc_channels.py`

**What it is**: The live-injection TRANSPORT for cross-session messaging. Registers channel-member session ports, dispatches messages via HTTP POST (channel transport) or supervisor /inject (supervised transport), logs mail, manages threads/replies.

**Public Surface**:
- `live_sessions() -> list` — every live channel MEMBER (per-transport presence)
  - "channel" transport (default): alive = pid alive + has a port; pruned on dead pid
  - "supervised" transport (fork-owned): alive = supervisor shows it non-closed; pruned only when supervisor reachable + session closed
- `find(target: str) -> dict` — resolve target (handle, cwd, session_id) to ONE live session (fail loud if none/ambiguous)
- `push(handle_or_reg, content, meta=None, base_timeout=10)` → {ok, handle, transport, ...}
  - Dispatches on transport:
    - "channel" → HTTP POST to port (original)
    - "supervised" → POST to supervisor /inject + lazy-start /watch tail (R3.5 refactor)
  - Returns immediately; dispatch is fire-and-forget or queued in supervisor
- Functions:
  - `_alive(pid)` — os.kill(pid, 0) presence check
  - `_read_reg(path)` — JSON load with error tolerance
  - `_transport_of(reg)` — resolve "channel" vs "supervised" (back-compat: absent → "channel")
  - `supervisor_base(reg)` — the supervisor a supervised member reaches through
  - `_sup_sessions(base, timeout=5)` → (reachable, [session records])

**Constants**:
- `CHAN_DIR` — .data/channels/ (member registrations + mail log + thread index)
- `MAIL_LOG` — .data/channels/_mail.jsonl (durable record of every message/reply)
- `THREADS` — .data/channels/_threads.json (thread_id → {originator_handle, topic, members})
- `CHANNELS_DIR` — .data/channels/_channels/ (named-channel records)
- `DEFAULT_SUPERVISOR_BASE` — http://127.0.0.1:8771 (mirrors cc_clone.SUPERVISOR)

**Notable/Surprising**:
- **Two transports, one interface** — push() abstracts over HTTP-to-port (live channel-session) and supervisor /inject (supervised fork session)
- **Supervised transport is NEW** (R3.5 refactor) — fork-owned sessions are reached via supervisor, not direct HTTP
- **Back-compat detection** — a reg without `transport` field is "channel" (original behaviour)
- **Transient-tolerant pruning** — supervised regs are NEVER deleted just because supervisor is unreachable (that could destroy a fork-owned registration)
- **Supervisor batching** — one GET /sessions per distinct supervisor base (groups members by supervisor_base, caches the response)
- **Thread routing** — the mailbox + thread index (THREADS JSON) map replies back to the originator

**Writes to**:
- `.data/channels/<handle>.json` — member registration (by cc_clone.register_supervised_member)
- `.data/channels/_mail.jsonl` — durable mail log (via store.append_agent_mail)
- `.data/channels/_threads.json` — thread index

**Connected to**:
- `runtime.session_channels` — fold_channels reads the channel registry
- `runtime.cc_clone` — register_supervised_member writes supervised regs here
- `store.fs_store` — (implicit in mail log appends)

**Live/Dormant**: LIVE — the channel dispatch backbone

---

### 6. **session_channels.py** (690 lines) — Cross-Session Fabric Organs
**Path**: `/home/tim/company/runtime/session_channels.py`

**What it is**: The structure AROUND sessions — channels (persistent work-centric groups), gatherings (momentary grabs, promotable), connection edges (durable who-talked-to-whom on the session), and coordination modes (direct router vs conducted coordinator).

**Public Surface**:
- `class fold_channels(store) -> dict[str, dict]` — project channel/gathering registry rows
  - Row shape: {id, kind, name, purpose, mode, coordinator, status, members:{sid→{participation, added}}, origin, created, last_activity, posts, seq}
  - Read-time fold from channels.jsonl (log-is-the-index pattern)
- `append_channel_event(store, rec: dict) -> dict` — persist one channel-lifecycle event
  - Validates kind in CHANNEL_OPS (fail loud)
  - Validates channel non-empty (fail loud: no unfoldable records)
  - Owns seq/ts (monotonic graph-locked cross-process append)
  - Fsync'd before return
- `channel_events_since(store, seq=-1, channel=None, limit=None) -> list[dict]`
  - Returns events with seq > passed seq, oldest-first
  - Filters by channel if set
  - Reads disk every call (sees sibling appends)
- Functions:
  - `_apply_channel_event(rows, e)` — fold one event into the row dict (not public)
  - `_addr(sid)`, `_bare(ref)` — session:// prefix normalization
  - `_chan_addr(cid)`, `_chan_bare(ref)` — channel:// prefix normalization

**Constants (Closed Vocabularies — registry-is-truth)**:
- `CHANNEL_OPS` — (channel.created, channel.member_added, channel.member_removed, channel.member_status, channel.posted, channel.mode_set, channel.archived, gathering.dispersed, gathering.promoted)
- `KINDS` — ("channel", "gathering")
- `MODES` — ("direct", "conducted") [R2.5: router vs conductor]
- `PARTICIPATION` — ("awake", "listening") [declared posture; busy/closed derived from registry+supervisor]
- `ROW_STATUS` — ("active", "archived", "dispersed", "promoted") [row lifecycle]

**Notable/Surprising**:
- **Registry-shaped by design** — everything is append-only leaf + read-time fold (log-is-the-index)
- **Single mail leaf** — channels ride their own leaf (agent_sessions/channels.jsonl, the mail.jsonl twin) with cross-process seq + fsync
- **No per-target queue yet** — F1 simplification: intents consumed strictly in order (head-of-line blocking if target mid-turn, retried next poll)
- **Connection edges are a PROJECTION** — derived at read-time from mail.jsonl (who-talked-to-whom), not stored separately
- **Conducted mode (R2.5)** — whole post routes to coordinator as ONE intent; the coordinator's session_posts are the exchange
- **Supervisor liveness refinement** — member_statuses() may probe supervisor /sessions to refine awake/listening into "busy" (optional, reported in result)
- **FLOOR: no spawn/resume** — this module never spawns claude or resumes; writes are store appends only
- **Single-writer law preserved** — channel events live on their OWN leaf; supervisor remains only events.jsonl writer (audit C6)

**Reads from**:
- `<store>/agent_sessions/channels.jsonl` — the channel-lifecycle leaf
- `<store>/agent_sessions/mail.jsonl` — the mail leaf (for connection-edge projection)

**Writes to**:
- `<store>/agent_sessions/channels.jsonl` — append_channel_event writes with graph_lock

**Connected to**:
- `mcp_face/tools/channels.py` — the MCP agent face (CQRS pair channels/channel_act)
- `cc_channels.py` — live-session roster (SUPERVISOR_URL probe for member_statuses)
- `session_supervisor.py` — (implicit: sessions appear in member lists)

**Live/Dormant**: LIVE — the channel fabric engine

---

### 7. **channel_boundary.py** (320 lines) — Shared Channel Publish/Read Boundary
**Path**: `/home/tim/company/runtime/channel_boundary.py`

**What it is**: The company's edge onto Supabase for SHARED channels (single-source design, §2026-06-18). Company sessions publish directly to Supabase channel_posts; an OUTBOUND Realtime subscription injects new rows into live member-sessions (skip-by-origin, BOTH 'session' and 'client' kinds).

**Public Surface**:
- `build_post_row(channel_id, from_session, text, to_session=None, thread=None, kind="message", sender_kind="session") -> dict`
  - PURE: builds the channel_posts row the company publishes
  - Fail loud on missing required fields (channel_id, from_session, text)
  - Auto-generates thread if unset
- `publish_shared_post(row, principal=None, poster=None) -> dict`
  - Publishes to Supabase channel_posts (authenticated as least-privilege principal, NOT service-role)
  - Returns {ok, status, id?, error?}
  - Fail-loud-with-reason: ok:False + reason on any non-2xx/transport error
  - `poster(row)->resp` injection for offline tests
- `route_inject(post_row, member_sessions) -> list[str]`
  - PURE: which live company member-sessions to inject into
  - Skips by origin (from_session), NOT by sender_kind
  - BOTH 'session' and 'client' rows inject (single-source correctness)
- `class ChannelInjectSubscriber` — Realtime subscriber → live-session injector (DAEMON)
  - `on_insert(post_row)` — handle one new channel_posts row
  - `start(reconnect=True, backoff=3.0)` — connect + subscribe in daemon thread
- Helper functions:
  - `parse_realtime_message(raw) -> (event, record|None)` — parse Realtime WS frame
  - `build_join_msg(topic, access_token, table, schema, event, ref)` — phx_join frame
  - `_ws_url(http_url, anon)` — convert REST URL to Realtime WS endpoint

**Constants**:
- `BOUNDARY_PREFIX` — "COMPANY_CHANNEL" (env prefix for principal creds)
- `_REST_TABLE` — "channel_posts" (the PostgREST table)
- `_POST_REQUIRED` — ("channel_id", "from_session", "text")

**Notable/Surprising**:
- **Single-source, not mirror** — Supabase is the one store; company does NOT inject locally (delivery via Realtime sub)
- **Skip-by-origin, not by sender_kind** — BOTH company sessions and Claude Design inject to all-but-author
- **Least-privilege principal, NOT service-role** — authenticated as a dedicated RLS-scoped principal (runtime/supabase_principal.py)
- **RLS-gated Realtime** — the principal JWT rides as payload.access_token in phx_join; Realtime applies RLS and streams only what the JWT can SELECT
- **Realtime transport is STUBBED** — builder owns the Realtime mechanism (postgres_changes vs broadcast), topic, payload shape, RLS handshake
- **Fallback seam** — if Phoenix rabbits-hole, start() can swap to urllib SELECT-since-last-seen POLL

**Depends on**:
- `runtime.supabase_principal.SupabasePrincipal` — the least-privilege principal (RLS-gated)
- Supabase REST API (PostgREST) — for PUBLISH
- Supabase Realtime WS — for INJECT (stubbed/pending builder)

**Live/Dormant**: LIVE but INCOMPLETE — publish path is solid; Realtime subscriber transport pending builder's live tables + wiring

**Build state** (advisor-scoped 2026-06-18):
- PUBLISH (write) + pure INJECT-ROUTING: built + offline-tested (locked schema, clear auth)
- Realtime SUBSCRIBER TRANSPORT: stubbed (clean interface; builder owns mechanism, topic, payload, RLS handshake)
- cc_channels.py HOOK (route shared post here): pending shared-vs-internal DISCRIMINATOR (Tim/lead product call)
- DONE = live round-trip verified with builder's live tables + Claude Design end, NOT offline green

---

### 8. **render_declaration.py** — The R1.2 Render-Declaration Layer (imported by session_supervisor)
**Path**: `/home/tim/company/runtime/render_declaration.py`

**What it is**: The layer that every Claude Code emit is declared through. Each turn's events are declared (placement/component/fields) and fanned as a `declared` event; an undeclared or family-fallback emit fires the drop hook (gap-pressure sensor for the registry).

**Why here**: session_supervisor.py imports it (R1.2 law); the supervisor funs events through this layer before emitting.

**Live/Dormant**: LIVE — required by session_supervisor event flow

---

## Dependency Graph

```
suite.py (the brain)
├── calls: cognition (language-model runner)
├── calls: scheduler (graph execution)
├── calls: governance (inbox + action-class guards)
├── reads: registry, roles, projections (3 registries)
└── reads: store (addressed repository)

bridge.py (the UI face, 127.0.0.1:8770)
├── calls: suite (all app logic)
├── calls: cognition (role/items/reduce runners)
├── calls: generate_mockup (committed engine)
├── calls: activation_driver (always-on caller, Group H/I)
└── serves: 150+ /api routes

session_supervisor.py (the session fleet owner, 127.0.0.1:8771)
├── owns: N claude subprocess instances
├── imports: ui_claude_session._find_claude (binary resolution)
├── imports: ui_claude_session._MCP_CONFIG (strict company MCP)
├── imports: render_declaration (R1.2 event layer)
├── reads: Mirror-Registry (flag posture + body-key map)
├── writes: agent_sessions.* events (single writer)
├── consumes: agent_sessions/mail.jsonl (the mailbox)
└── reads: agent_sessions/cursor:supervisor (cursor state)

brain_router.py (the supervisor-as-brain source router)
├── calls: session_channels.fold_channels (channel roster)
├── calls: Suite.list_agent_sessions (session list)
├── calls: Suite.chat (the model)
├── reads: territory_prose (aim-grounded context)
└── route-to: /api/brain/ask

cc_channels.py (live-injection transport)
├── dispatches: HTTP POST (channel transport) OR supervisor /inject (supervised)
├── writes: .data/channels/_mail.jsonl (durable mail)
├── writes: .data/channels/<handle>.json (member regs)
└── reads: supervisor /sessions (for supervised presence)

session_channels.py (cross-session fabric organs)
├── reads/writes: agent_sessions/channels.jsonl (append-only leaf)
├── projects: agent_sessions/mail.jsonl (connection edges)
├── calls: channel_boundary (shared-channel dispatch hook, pending)
└── exports: fold_channels (read-time fold), append_channel_event

channel_boundary.py (shared-channel boundary)
├── publishes: Supabase channel_posts (least-privilege principal)
├── subscribes: Supabase Realtime WS (stubbed, pending builder)
├── injects: via cc_channels.push (skip-by-origin routing)
└── calls: runtime.supabase_principal (RLS-gated JWT)
```

---

## Live vs. Dormant

| Module | Live? | Notes |
|--------|-------|-------|
| **suite.py** | ✓ LIVE | Core application layer; 50+ methods called by bridge + MCP |
| **bridge.py** | ✓ LIVE | Primary operator console; 150+ /api routes active |
| **session_supervisor.py** | ✓ LIVE | Session fleet backbone; runs as separate service |
| **brain_router.py** | ✓ LIVE | /api/brain/ask calls this; source router active |
| **cc_channels.py** | ✓ LIVE | Live-message dispatch; HTTP POST + supervisor /inject |
| **session_channels.py** | ✓ LIVE | Channel/gathering fabric engine; append-only registry |
| **channel_boundary.py** | ⚠ PARTIAL | PUBLISH (write) live; Realtime SUBSCRIBER pending builder |
| **render_declaration.py** | ✓ LIVE | Imported by session_supervisor; R1.2 event layer |

---

## Notable & Surprising Findings

1. **Suite is stateless, NOT per-session** (suite.py:1)
   - Huge application engine (12K lines) but operates on the addressed store, not a session object
   - Graph mutations, runs, cascades, voice logging all go through the same generic verb API
   - Does NOT spawn/resume sessions (that's session_supervisor.py)

2. **Supervisor is a SEPARATE SERVICE** (session_supervisor.py:1)
   - NOT imported by MCP face; runs on own port (8771)
   - Sole spawner of claude processes (T2-proven transport: held-open stdin + stream-json)
   - Single-writer law (audit C6): only process emitting agent_sessions.* events

3. **Flags posture is DERIVED, not stored** (session_supervisor.py:400-410)
   - F-FIX-5 step 5: posture (locked/consent/safe) comes from Mirror-Registry rules at call time
   - No hand-column in SPAWN_FLAG_ASSEMBLY; every flag's posture is recomputed (single source of truth)

4. **Two transports for channel dispatch** (cc_channels.py:59-66, 173-198)
   - "channel" (original): HTTP POST to live session's port
   - "supervised" (R3.5 refactor): POST to supervisor /inject (fork-owned sessions)
   - Same push() interface; dispatch logic is transport-aware

5. **Channel registry is append-only log** (session_channels.py:121-160)
   - agent_sessions/channels.jsonl is the single source (log-is-the-index)
   - Cross-process unique seq under graph_lock (same append discipline as mail.jsonl)
   - Connection edges are a READ-TIME PROJECTION from mail.jsonl (not stored separately)

6. **Shared channels are single-source on Supabase** (channel_boundary.py:1-30)
   - Company publishes directly to Supabase channel_posts (authenticated as least-privilege principal)
   - Realtime sub injects into live company member-sessions (skip-by-origin)
   - Realtime transport is STUBBED; builder owns the mechanism, topic, payload, RLS handshake

7. **Brain model is TIM-RULE dynamic, not hardcoded** (brain_router.py:136-169, suite.py:145)
   - pick_ollama_model_for_context() resolves brain model per context size (kimi default, deepseek-flash for large context)
   - No DEFAULT_BRAIN constant; the model is SWAPPABLE per mode-loadout-registry

8. **Bridge has 150+ routes on ONE ThreadingHTTPServer** (bridge.py:45-135)
   - No Flask/FastAPI; pure stdlib http.server (dispatcher with 100+ path literals)
   - Single source: BRIDGE_ROUTES constant (tests/bridge_routes_acceptance.py drifts against it)
   - Tool posture is call-time (lives in tool manager, not a static list)

9. **Consent gate is "signal, not lockout"** (session_supervisor.py:174-238)
   - R1-prime wider-spawn profile is ALWAYS AVAILABLE to operator
   - operator_consent=True is required by AGENT spawn paths (consent-not-lockdown)
   - git revert is the irreversibility backstop; the gate is a marker

10. **Computer-use is REFUSED LOUD** (session_supervisor.py:229-238)
    - Not green-painted as an allowlist entry that never binds
    - "computer use in the CLI is macOS-only AND requires an interactive session"
    - Same for browser (beta, WSL/Windows unsupported)
    - The boundary is explicit, never silent (§5.4 honesty)

11. **Ollama launcher redirects despite stored login** (session_supervisor.py:641-854)
    - provider='ollama' → `ollama launch claude --model <tag> -- ...` (not env overlay)
    - A logged-in Claude Code ignores env API-key/base-url overlays (hits real Anthropic → rejects ollama model)
    - The launcher properly redirects despite stored login (fork's clone-proof verified this)

12. **Concurrency cap is taught, not silent** (session_supervisor.py:600-610)
    - COMPANY_FABRIC_CONCURRENCY enforcement returns TeachingRefusal
    - Names the cap, the live state, the env var, how to free a slot
    - Never a bare "limit exceeded" error

13. **Session state machine is truthful** (session_supervisor.py:471-509)
    - starting → idle ⇄ busy → closed (Supervised class)
    - Transitions are explicit; state is read from supervisor /sessions
    - CONSULT fans count against the same cap as live sessions

14. **Mail log is the ONE source for intents** (session_supervisor.py:44-56)
    - Intents ride in agent_sessions/mail.jsonl (one json per line)
    - Consumption is cursor-based (cheaper-than-RMW design per §2.3)
    - Replies/acks ride back via store's append_agent_mail (same leaf)

15. **Session Fabric R1-R2.5 laws are hardcoded as comments** (session_supervisor.py:10-88, session_channels.py:1-59)
    - Audit references (B3, C3, C6, C9, N4, N7)
    - Synthesis section references (§3, §6.3, etc.)
    - Every law has a citation and explicit statement (never silent assumptions)

---

## Files Analyzed (Coverage: 8 core modules, 19,318 lines total)

| File | Lines | Status |
|------|-------|--------|
| suite.py | 12,168 | READ (partial via offset/limit) |
| bridge.py | 3,663 | READ (head + route table) |
| session_supervisor.py | 1,711 | READ (full) |
| brain_router.py | 203 | READ (full) |
| cc_channels.py | 563 | READ (head + key functions) |
| session_channels.py | 690 | READ (head + fold pattern) |
| channel_boundary.py | 320 | READ (full) |
| render_declaration.py | — | REFERENCED (imported by session_supervisor) |

---

## What's NOT Included (Peripheral/Dependent Modules)

- **ui_claude_session.py** — session_supervisor imports _find_claude + _MCP_CONFIG (reuse, not reimplementation)
- **cc_clone.py** — materializes clones at point-in-time, registers as supervised members
- **cc_retire.py** — member/channel retirement with harvest crystallization
- **session_pointintime.py** — materialize session at past point (used by cc_clone)
- **session_recall.py** — recollect-own-past (the verified backbone of member harvest)
- **cc_board.py** — linked board records + typed edges
- **cc_attachments.py** — image/doc manifest for channel retirement
- **session_lens.py**, **session_lineage.py**, **session_search.py**, **session_scan.py** — session introspection layers
- **cognition.py** — the language-model runner (called by bridge, not defined in suite)
- **governance.py**, **scheduler.py**, **registry.py**, **roles.py** — foundational registries
- **corpus.py** — structured corpus write (used by cc_retire)

---

## Definitions of Terms Used

- **Registry-is-truth**: A constant/vocabular defined ONCE in code, never duplicated; additions are ONE place
- **Log-is-the-index**: An append-only leaf (JSONL) is the source; state is derived by folding from seq=0
- **Graph-lock**: Cross-process atomic append using store's graph_lock (§2.3 pattern)
- **Audit**: A specific audit report (e.g., audit C6) cited in AGENTS.md or build-prep docs
- **Synthesis**: The system-wide architecture document (build-prep/the-one-application/)
- **R1-R2.5**: Operational requirements (Session Fabric version numbers)
- **T2, T4, F-FIX-5**: Feature versions (T2=stream-json injection; T4=fork/consult; F-FIX-5=flag refactor)
- **Consent-not-lockdown**: The sole-operator security model (Tim's explicit steer: wider capabilities always available, gated by operator consent signal)
- **FLOOR**: The baseline posture/contract (e.g., floor=mcp__company-only spawn, floor=read+propose for brain)

