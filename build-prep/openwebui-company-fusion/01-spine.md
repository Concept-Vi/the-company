---
type: map
status: descriptive
register: descriptive
coverage:
  files_read: ["ops/services.json", "runtime/session_supervisor.py", "runtime/bridge.py", "ops/systemd/company.target", "ops/cli/app.py", "ops/cli/sessions.py"]
  files_total: ~50 (all core runtime/ops spine)
  last_read: 2026-06-28
---

# The Company Spine — OpenWebUI↔Company Fusion Design Map

## Executive Summary

The **Company** is a self-contained **Agent OS** with ~20 systemd services, a shared in-memory **Suite** (brain/embedding/cognition), and two primary HTTP faces: the **Bridge** (operator UI, port :8770) and the **Session Supervisor** (Claude Code fleet manager, port :8771). OpenWebUI is a chat/model-management interface that can integrate as a **third HTTP face** on the Bridge's Suite + tools layer, effectively becoming another "surface" talking to the same brain and embedder infrastructure. The spine is **LIVE now** — bridge, supervisor, services running; OpenWebUI would be an **additive consumer**, not a replacement.

## 1. Core Runtime Services — The Spine Inventory

### 1.1 Service Registry & Lifecycle (`ops/services.json`)
**File:** `/home/tim/company/ops/services.json`

Single source of truth for all ~25 managed services. Every service has:
- `id`: Service key (e.g., `chat-4b`, `bridge`, `stt-moonshine`)
- `title`: Human description
- `port`: HTTP port (if applicable)
- `group`: Category (core|brain|voice|models|reach|jobs)
- `manage.type`: `user-unit` | `system-unit` | `manual` | `hosted`
- `manage.unit`: systemd unit name (e.g., `company-bridge.service`)
- `health`: Health check endpoint (e.g., `/api/now` for bridge)
- `vram_mb`: GPU budget (for models)
- `autostart`: bool (only true for interactive core: canvas, bridge, remote, session-supervisor)
- `config`: Model-specific settings (gpu_util, max_model_len, model path, etc.)

**Policy (Tim, 2026-06-06):** Nothing auto-starts at boot. Every service is **on-demand** via `company up <service>`. The `autostart=true` flag means "started by bare `company up` (no target)" — keeps the interactive surface live.

**Live Status (2026-06-28):**
```
▶ RUNNING (core): bridge, remote, session-supervisor
▶ RUNNING (brain): chat-4b (~6.5 GB)
▶ RUNNING (voice): tts-kokoro, stt-moonshine
▶ RUNNING (models): embed-pplx (~5.4 GB), rerank-jina (~1.3 GB)
▶ RUNNING (reach): ollama, tailscale, remote-gateway
· STOPPED: canvas (vite dev), all other models on-demand
```

---

### 1.2 The Bridge — HTTP API + UI Face (`runtime/bridge.py`, port :8770)

**What it is:** The operator console + state/action API over a **shared Suite** (the same cognition engine the MCP face uses). Stdlib HTTP only.

**File:** `/home/tim/company/runtime/bridge.py` (lines 1–927+, truncated in reads)

**HTTP API Surface — BRIDGE_ROUTES (single source of truth):**

```python
# Lines 45–135 in bridge.py
BRIDGE_ROUTES = (
    # Served pages / static
    "/studio", "/design-system.css", "/mockups/",
    
    # GET routes (read-only, majority)
    "/api/stream",                    # Server-Sent Events (live event tail)
    "/api/now",                       # Health check (current state)
    "/api/chat",                      # RHM conversation history
    "/api/corpus", "/api/graph",      # Knowledge graph + corpus reads
    "/api/cognition_info",            # Cognition engine metadata
    "/api/models",                    # Available models
    "/api/voice",                     # Voice engine list + status
    "/api/tools",                     # MCP tool list (machine-truth + human forms)
    "/api/capabilities",              # System capabilities + API verbs
    "/api/panels",                    # UI panel layout
    "/api/projection",                # Semantic projection (the Circle, Group 6)
    "/api/session-recall",            # Cross-session memory search
    "/api/transcript-search",         # Claude session search
    # ... 40+ more GET routes
    
    # POST routes (consequential)
    "/api/chat",                      # RHM conversation (new turn)
    "/api/tts",                       # TTS synthesis request
    "/api/stt",                       # STT transcription
    "/api/voice/stream",              # Voice chat stream
    "/api/run",                       # Cognition run (role/items/reduce)
    "/api/tools/invoke",              # Generic MCP tool invocation (gated)
    "/api/resolve", "/api/revert",    # Decision resolve/revert (operator-only)
    "/api/claude/turn",               # S1: in-session Claude Code turn (operator-only, plan mode)
    "/api/channel/post",              # The open V-POST (Tim 2026-06-22)
    # ... 30+ more POST routes
)
```

**Core Design:**
- **Single Suite**: `SUITE = Suite(FsStore(fcfg.STORE_DIR), NodeRegistry()...)` (line 458)
  - Shares **brain** (cognition.py), **embedder** (embed-pplx), **memory** (store), **graph** (contracts)
  - No 2nd Suite — the MCP face + bridge both operate the SAME Suite
- **Tool Face (GAP 1–3)**: 
  - GAP 1: Lazy imports `mcp_face.server.build_mcp(SUITE)` → binds FastMCP manager to bridge's Suite
  - GAP 2: `/api/tools` GETs machine-truth from list_tools() + human forms from `mcp_face/tool_meta.json`
  - GAP 3: `/api/tools/invoke` POST is FAIL-CLOSED operator gate (mirrors `remote_exposure.json`)
- **Voice Coupling**: Chat parts generator driven by producer thread; brain generates ahead of TTS synthesis (C6.1 overlap, lines 308–456)
- **Operator Attribution**: Token-minted safety gate (lines 541–576) for accidental-runaway prevention (not adversary-proof)

**Key Daemons:**
- `_warm_vector_cache()`: Pre-warm semantic index on boot (~1.5s cold → hot)
- `_commit_queue_drain_loop()`: Serialize concurrent git commits (cross-session safe)
- `_freshness_loop()`: Auto-reindex extractions when asset files change (MTIME-gated)

**HTTP Bindings:**
- Listen: `localhost:8770` (default)
- Health: `GET /api/now` → `{ok, service, ...}`
- Serves: `/studio` (operator console), `/mockups/` (design-system)

---

### 1.3 Session Supervisor — Claude Code Fleet Manager (`runtime/session_supervisor.py`, port :8771)

**What it is:** The **ONLY process** that spawns/owns/manages live Claude Code subprocesses (Session Fabric F1.1). Each session is held open with `--input-format stream-json`, accepting injected turns while idle — full memory preserved.

**File:** `/home/tim/company/runtime/session_supervisor.py` (1712 lines total)

**Laws This Service Carries:**

1. **EXPOSURE (audit B3)**: Binds `127.0.0.1` ONLY — no env var to widen it
2. **SINGLE WRITER (audit C6)**: This service is the ONLY process emitting `agent_sessions.*` events
3. **ONE OWNER PER SESSION (T1)**: Supervisor owns the live session; nowhere else can resume it live
4. **ENFORCED WALL-CLOCK (audit C3)**: Per-turn watchdog reaps hung turns (default 900s via `COMPANY_FABRIC_TURN_TIMEOUT_S`)
5. **CONCURRENCY CAP (audit C9)**: Default 3 live sessions (`COMPANY_FABRIC_CONCURRENCY`, call-time env read)
6. **NO ORPHANS**: atexit + signal handlers ensure all subprocesses are terminated

**HTTP API (127.0.0.1:8771):**

```
GET  /health                 → {ok, service, sessions, cap, turn_timeout_s, bind}
GET  /sessions               → every owned session's record (state: starting→idle⇄busy→closed)
GET  /watch?session=<id>     → ndjson stream of session's events (replay + live)
POST /spawn                  {cwd?, resume?, fork?, name?, prompt?, source?, flags?, …}
POST /inject                 {session, message, source?}
POST /interrupt              {session}
POST /teardown               {session}
POST /bridge-session         {operator_consent, capabilities?, extra_tools?, cwd?, …}
                             RAIL R1-prime (Capability Fabric ④): consent-gated spawn with
                             WIDER --allowedTools (Bash/git/LSP/web + mcp__company)
```

**Spawn Flags (Registry-Derived Posture, R1.3):**

The `SPAWN_FLAG_ASSEMBLY` table (lines 258–373) lists every flag a caller can request. Posture (locked|hazard|consent|safe) is **derived from the Mirror-Registry** (not hand-stored here), so the transport invariants are centrally correct. Examples:

- `session_id`: value (safe) — pre-assign UUID
- `model`: value (consent) — rides the dedicated body key
- `continue`: bool (safe) — resume cwd's most recent conversation
- `allowed_tools`: swap (consent) — REPLACE the floor allowlist (the R1-prime wider-surface decision)
- `permission_mode`: value (consent) — fabric-wide default plan; acceptEdits opt-in
- `input_format`: value (locked) — `stream-json` IS the contract (no negotiation)
- `print` (`-p`): bool (locked) — held-open injection mode (always on)

**Mailbox (Coordinate-by-Contract):**

Intents ride `/store/agent_sessions/mail.jsonl` (one JSON per line):
```json
{id, to: "session://<id>", from, verb: "deliver|wake|consult", cas, copies?}
```

- `deliver` → inject into live session (supervisor owns it)
- `wake` → spawn on non-live session (`--resume`), then inject
- `consult` → spawn on FORK copy (`--resume --fork-session`), never touches original

Per-consumer cursor tracks position (`agent_sessions/cursor:supervisor`).

**Command Builder (Pure, Unit-Testable):**

- `_build_spawn_cmd()` (lines 612–695): Assembles a claude CLI command with held-open transport head:
  ```
  claude -p \
    --input-format stream-json --output-format stream-json --verbose \
    --permission-mode <mode> \
    --mcp-config <config> --strict-mcp-config \
    --allowedTools mcp__company \
    [--model <tag>] [--effort low|medium|high|xhigh|max] \
    [--settings <json|path>] [--add-dir <d>] [--debug [cats]] \
    [--resume <id>] [--fork-session]
  ```
  - Provider='ollama' → `ollama launch claude --model <tag> -- -p ...` (Tim 2026-06-16)
  - Every flag verified via registry posture (F-FIX-5 step 5)

- `_build_bridge_session_cmd()` (lines 763–802): R1-prime variant with wider tools + acceptEdits permission

**R1-prime: The Bridge-Session Profile (Capability Fabric ④)**

A **consent-gated** spawn with Bash/Edit/Read/Glob/Grep/WebFetch/WebSearch + mcp__company. Used for:
- In-session git (Bash native, via corpus git.md)
- LSP navigation (Read/Edit permission family)
- Web fetch/search (Atlas-grantable)
- **NOT** computer/browser (macOS/interactive-only host boundaries — refused-loud on this Linux `-p` rail)

Gate: `operator_consent=True` required; consent-not-lockdown — always available, git revert backstops.

---

## 2. The `company` CLI — Service Management (`ops/cli/`)

**File:** `/home/tim/company/ops/cli/app.py`

**One Console for Everything:**

```bash
company                      # status + VRAM budget
company up [TARGET]          # start service(s) (or @combo group)
company down TARGET          # stop service
company restart TARGET       # stop + start
company health               # ping every service's port
company gpu                  # measured GPU VRAM + what's holding it
company models               # inventory (HF cache + Ollama)
company swap SERVICE MODEL   # rewire model service to a different model
company ensure MODEL|SERVICE # gated load (refuse over-budget, --evict to auto-stop others)
company config SERVICE [KEY VAL]  # edit model serve config
company combos               # list runnable service combinations
company session [SUB]        # supervised fleet: list/new/send/stop (talks to supervisor :8771)
company board [SUB]          # Company noticeboard (request/issue/idea lifecycle)
company clone                # clone-fleet records (distributed memory)
```

**Constitution:** `ops/AGENTS.md` — the sole truth for how to extend the CLI.

**Target Syntax:**
- Service key: `chat-4b`, `bridge`, `stt-moonshine`
- Group: `core`, `brain`, `voice`, `models`, `reach`, `jobs`
- Combo: `@small-pair`, `@wake`, `@xsession`, `@instrument`, `@interaction`, `@interaction-parakeet`
- `all`: Every service

**Resource Manager (GPU budgeting):**

- `company up` REFUSES a start that would exceed 16.4 GB GPU ceiling
- `--evict`: Auto-stop largest GPU services (models→brain→voice) to make room
- `--force`: Start anyway over budget (expect OOM/offload)
- `--wait`: Block until serving, record real load time + measured VRAM to telemetry

---

## 3. Systemd Integration — ~20 Units

**File:** `/home/tim/company/ops/systemd/` (26 unit files)

**Master Target:**
```ini
[Unit]
Description=The Company — all local services (canvas, bridge, brain, voice)
After=network.target
WantedBy=default.target
```

**Service Groups:**

| Unit | Port | Group | Type | Autostart | Purpose |
|------|------|-------|------|-----------|---------|
| `company-bridge.service` | 8770 | core | user | ✓ | Operator UI + API |
| `company-remote.service` | 8772 | core | user | ✓ | MCP connector gateway (Funnel) |
| `company-session-supervisor.service` | 8771 | core | user | ✓ | Claude Code fleet manager |
| `company-canvas.service` | 5173 | core | user | ✓ | Vite dev server (frontend) |
| `vllm-chat.service` (chat-4b) | 8000 | brain | user | — | Local Qwen3.5-4B worker (on-demand) |
| `company-tts-kokoro.service` | 4123 | voice | user | — | TTS voice out (unmanaged) |
| `voicemode-whisper.service` (stt-whisper) | 2022 | voice | user | — | STT voice in (boot default ear) |
| `company-stt-moonshine.service` | 2034 | voice | user | — | ONNX lean STT (current ear) |
| `company-stt-parakeet.service`, `..-parakeet-onnx`, `..-canary`, `..-granite` | 2031–2035 | voice | user | — | GPU ears (on-demand trials) |
| `company-voice-*.service` (chatterbox, orpheus, cosyvoice, xtts, qwen3tts) | 4124–4128 | voice | user | — | TTS engines (trial personas) |
| `company-embed-pplx.service` | 8007 | models | user | — | pplx-embed-context-v1-4b (custom transformers) |
| `vllm-embed.service` (embed-bge) | 8001 | models | user | — | BGE-M3 embeddings |
| `vllm-jina-*.service`, `company-rerank-jina.service` | 8002, 8004, 8008 | models | user | — | Jina embeddings + reranker |
| `vllm-2b.service`, `vllm-08b.service`, `vllm-nemotron.service`, `vllm-qwen3emb.service` | 8003, 8006, 8005, 8004 | models | user | — | On-demand chat/embed models |
| `ollama.service` | 11434 | reach | system | ✓ (boot) | GGUF model runtime (supervisor backend) |
| `tailscaled.service` | — | reach | system | ✓ (boot) | Tailnet (phone access) |
| `github-runner.service` | — | reach | user | — | CI runner (on-demand) |
| `company-agent-sessions-exporter.timer` | — | jobs | user | — | Transcripts → markdown (every 20 min) |
| `company-claude-sessions-reindex.timer` | — | jobs | user | — | Reindex beat (~5 min after export) |
| `company-ledger-refresh.timer` | — | jobs | user | — | Refresh terrain ledger |

**Boot Autostart Policy:** Only `ollama.service`, `tailscaled.service`, and the system-level reach services auto-start at boot. Everything else is **on-demand** via the CLI or supervisor.

---

## 4. Live Memory & State

### 4.1 The Shared Suite (`runtime/suite.py` + `store/fs_store.py`)

**Single Source of Brain + Memory:**

```python
SUITE = Suite(
    FsStore(fcfg.STORE_DIR),           # store root: ~/.company/.data/store
    NodeRegistry().discover([...])     # nodes/ graph discovery
)
```

- **Brain**: All cognition functions (run_role, run_items, run_reduce, resolve_address, etc.)
- **Store**: File-backed event log + vector index + graph + node records
- **Registry**: Node types + skills + capabilities

**Both bridge and MCP face use the SAME Suite** (no duplication, single truth).

### 4.2 Events & Durability

Central `/store/events.jsonl` (append-only):
- `agent_sessions.spawned`: Supervisor creates a session
- `agent_sessions.turn`: Supervisor completes a turn (with cost/token usage — CC-20)
- `agent_sessions.closed`: Session torn down
- Agent-side events (from mcp_face): Router logs, intent consumption, decisions
- Bridge events: UI state changes, cognition runs

The supervisor is the **SINGLE WRITER** of `agent_sessions.*` events — audit C6 guarantees no duplicate-seq hazard.

---

## 5. What's Currently LIVE (2026-06-28)

```
✓ Bridge             :8770  — operator console + ~100 GET/POST routes
✓ Session Supervisor :8771  — Claude Code fleet, 3 max live sessions
✓ Remote Connector   :8772  — MCP tool gateway to cloud
✓ Chat-4B            :8000  — local brain (~6.5 GB, vLLM)
✓ Embed-PPLX         :8007  — transcript-search embedder (~5.4 GB)
✓ Rerank-Jina        :8008  — semantic rerank (~1.3 GB)
✓ STT-Moonshine      :2034  — CPU ear (ONNX, <1 GB, realtime)
✓ TTS-Kokoro         :4123  — voice out (unmanaged)
✓ Ollama             :11434 — GGUF runtime (supervisor backend)
✓ Tailscale          —      — phone access (via tailnet)

GPU committed: ~14.1 GB of 16.4 GB
```

---

## 6. OpenWebUI Fusion: Integration Opportunities

### 6.1 **The Natural Seam: Bridge's Suite + Routes**

**Option A: OpenWebUI as a Third HTTP Face (RECOMMENDED)**

Route: Add OpenWebUI routes to the **bridge** (:8770) directly, consuming the SAME Suite:

```python
# In bridge.py do_GET/do_POST, add:
elif self.path == "/webui/chat":          # OpenWebUI chat interface (GET)
elif self.path == "/webui/models":        # Model selector (GET)
elif self.path == "/webui/chat/stream":   # Chat streaming (POST + SSE)
```

**Why this wins:**
- **No 2nd Suite**: OpenWebUI operates the exact brain, embedder, memory suite the bridge and MCP face use
- **Shared tools**: `/api/tools` already lists every MCP tool; OpenWebUI calls them via `/api/tools/invoke` (same gated endpoint)
- **Shared events**: Voice, chat, decisions all flow to the central events.jsonl
- **Unified attribution**: Operator token slot (lines 541–576) gates writes; OpenWebUI inherits it
- **Voice loop ready**: Bridge's `_stream_parts()` (lines 327–456) already overlaps brain + TTS; OpenWebUI just consumes the same socket

**Integration Points:**
1. **Chat**: POST `/webui/chat/stream` → runs SUITE.chat_parts() + voices back via bridge's TTS loop
2. **Models**: GET `/webui/models` → reads SUITE's available models (same as `/api/models`)
3. **Tool Invoke**: POST `/webui/tools/{name}` → calls `_tool_gate()` + SUITE.run_tool() (same GAP-3 gate)
4. **History**: GET `/webui/chat/history` → reads RHM conversation from store (same as `/api/chat`)
5. **Settings**: GET `/webui/voice/engines` → bridges's TTS engine map (lines 245–246)

---

### 6.2 **Where NOT to Plug In (Don't Duplicate)**

- **Don't spawn a 2nd Suite**: The bridge's Suite (line 458) is singular by design. A 2nd Suite would split brain state.
- **Don't add a separate supervisor service**: The supervisor (:8771) owns Claude Code subprocesses; OpenWebUI isn't a session manager — it's a chat UI.
- **Don't auto-start OpenWebUI on the systemd target**: Keep it managed via the CLI (`company up openwebui`) or manual launch.

---

### 6.3 **OpenWebUI's Own Footprint**

Assume OpenWebUI as a Node process on port 3000 (or :8780 to avoid conflicts):

```ini
[Unit]
Description=OpenWebUI — chat interface (consumer of bridge Suite)
After=company.target
WantedBy=default.target    # (or on-demand: not WantedBy)

[Service]
Type=simple
ExecStart=/path/to/openwebui start
Environment="BRIDGE_URL=http://127.0.0.1:8770"
Environment="BRIDGE_SUITE_KEY=<...>"    # auth to bridge if needed
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=company.target    # rises/falls with the Company
```

**VRAM:** ~0 (Node app, no GPU). OpenWebUI is **pure UI** — the brain/embedder run on the bridge.

---

### 6.4 **Fusion-Specific Design Decisions**

#### **Issue 1: Model Selection — Who's the Brain Now?**

**Today:** Bridge has one active brain (`--rhm-config model`). OpenWebUI users might want to select a different local model (chat-2b, chat-08b, nemotron) or a cloud model (Claude API) at request time.

**Solution (Consent-Based):**
```python
POST /webui/chat/stream {prompt: "…", model?: "chat-4b|nemotron|claude-opus", voice?: "kokoro|orpheus"}
```

- If `model` is absent → use default (rhm_config.model)
- If `model` is a local service key → check it's running via `company ensure <model>`; fail loud if can't fit
- If `model` is "claude-opus" → route via the supervisor's provider='anthropic' (or the fabric's litellm proxy :4100)
- Same posture as BRIDGE_SESSION_PROFILE: **wider capability**, **operator consent** gated (the operator chooses the brain; OpenWebUI surface never auto-upgrades to a premium model)

#### **Issue 2: Voice — Multi-Engine Routing**

**Today:** Bridge has `ENGINE_PORTS` map (lines 245–246) hardcoding kokoro/chatterbox/orpheus/etc.

**OpenWebUI Alignment:**
```python
GET /webui/voices → {engines: [{name, port, health}], current: "kokoro"}
POST /webui/voice/switch {engine: "orpheus"} → `/api/voice/switch` (same underlying, bridge already handles)
```

OpenWebUI surface selects voice → bridge route handles the co-resident shrink (context-window auto-sizing, line 249).

#### **Issue 3: Tools & Capabilities — Operator Exposure**

**Today:** `/api/tools/invoke` is FAIL-CLOSED to the operator (lines 677–740). OpenWebUI should inherit the same gate.

```python
POST /webui/tools/{name} {args: {...}, confirm?: bool}
→ calls _tool_gate(name, args, confirm=confirm, operator_token=<session-token>)
→ if allowed, SUITE.run_tool(name, args)
```

**Operator-only tools** (locked posture) are available to OpenWebUI ONLY if the operator is using it (token minted on bridge load, line 564). A background Claude Code session (mcp_face) never minted a token → cannot post accidentally.

---

### 6.5 **Data Flow Diagram: OpenWebUI ↔ Company Spine**

```
┌─────────────────────────────────────────────────────────────┐
│ OpenWebUI (port :3000 or :8780, Node)                       │
│  • Chat UI (input/output streaming)                         │
│  • Model selector (local brain + cloud)                     │
│  • Voice engine switcher                                    │
│  • Tool invoker (on-demand MCP calls)                       │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP (same-host, no auth needed)
                   ↓
        ┌──────────────────────┐
        │  Bridge :8770        │ ← single HTTP face
        │  (operator console)  │   (routes unified)
        └─────────┬────────────┘
                  │ 
        ┌─────────┴──────────────────────────────────────────┐
        ↓                                                     ↓
    ┌────────────────────┐                  ┌──────────────────────┐
    │ Shared Suite       │                  │ Session Supervisor   │
    │ • Brain (cognition │                  │ :8771 (127.0.0.1)    │
    │ • Embedder (pplx)  │                  │ • Spawns Claude Code │
    │ • Memory (store)   │                  │ • Owns live sessions  │
    │ • Graph (nodes)    │                  │ (read-only from here)│
    └─────────┬──────────┘                  └──────────────────────┘
              │ 
    ┌─────────┴──────────────────────────────────────────┐
    ↓                  ↓                 ↓                ↓
 ┌──────────┐    ┌─────────┐      ┌──────────┐    ┌──────────┐
 │Chat-4B   │    │Embed-   │      │Rerank-   │    │Ollama    │
 │:8000     │    │PPLX :   │      │Jina :8008│    │:11434    │
 │(vLLM)    │    │8007     │      │(GPU)     │    │(GGUF)    │
 └──────────┘    └─────────┘      └──────────┘    └──────────┘
```

---

## 7. Fusion Uncertainties & Flagged Questions

### 7.1 **Does OpenWebUI Replace or Augment the Bridge?**

**Assumption in this map:** OpenWebUI is an **additional consumer** of the bridge's Suite, not a replacement. The bridge serves the operator (Tim). OpenWebUI might serve a different persona (e.g., a non-operator user accessing the local brain via UI). 

**Decision needed:** Is OpenWebUI operator-only (same access gate, same token), or should it offer a **public-facing** variant with restricted tools? (Affects security model + route design.)

### 7.2 **Model Selection — Implicit vs. Explicit**

**Today:** The bridge uses the active rhm_config.model. OpenWebUI users might expect to swap the brain at request time.

**Question:** Should `POST /webui/chat {model: "…"}` be:
- **Implicit** (route decides which service to use, auto-load if possible)?
- **Explicit** (caller pre-loads via `company ensure <model>`, then specifies)?
- **Gated** (operator only, consent required)?

This affects whether OpenWebUI becomes a model-loading UI or just consumes pre-running models.

### 7.3 **Long-Context Handling**

**Today:** Bridge's voice loop overlaps brain + TTS; context windows are sized per model (`max_model_len`). 

**Question:** Does OpenWebUI support the bridge's coopt chat window (which can span multiple earlier turns + attachments)? Or is each OpenWebUI chat session fresh?

### 7.4 **Unified Token & Attribution**

The operator token (lines 541–576) is minted by the **bridge** on load. If OpenWebUI is a separate frontend server, it would need its own token auth or inherit the bridge's.

**Option:** OpenWebUI runs as a **proxy reverse** to `:8770`, inheriting the token minted by the bridge (cleaner). Or OpenWebUI is a **bridge plugin**, not a separate server.

### 7.5 **Where Does the Canvas Fit?**

**Today:** `company-canvas.service` (vite, :5173) is the frontend for the bridge. OpenWebUI might replace or coexist with it.

**Question:** Is OpenWebUI meant to:
- **Replace** the vite canvas (and operators use OpenWebUI instead)?
- **Augment** it (both frontends on the bridge, different routes)?
- **Stand alone** (separate from canvas, serves different users)?

---

## 8. Recommended Next Steps for OpenWebUI Integration

### Phase 1: Foundation (No Code Changes)
1. **Understand OpenWebUI's expected API** — what endpoints does the UI expect from a chat backend?
2. **Map OpenWebUI's tool/model selection** to the bridge's `/api/tools` + `/api/models` routes.
3. **Sketch the auth/attribution model** — is OpenWebUI operator-only or public?

### Phase 2: Minimal Integration
1. **Add `/webui/*` routes to bridge.py** (pass-through to Suite methods initially).
2. **Test chat streaming** — can OpenWebUI consume `POST /webui/chat/stream` + ndjson events?
3. **Verify tool calls** — can OpenWebUI invoke MCP tools via the bridge's `_tool_gate()`?

### Phase 3: Full Fusion
1. **Model selection** — route model swaps through `company ensure` or supervisor's provider flag.
2. **Voice engine integration** — expose `/webui/voices` + switch via bridge's existing TTS loop.
3. **Session recording** — ensure OpenWebUI chats land in the store's events.jsonl for cross-session memory.

### Phase 4: Polish
1. **Operator token inheritance** or minting for OpenWebUI.
2. **Unified theme/branding** with the bridge's operator console.
3. **Monitoring** — surface OpenWebUI usage in the `company` CLI status view.

---

## 9. Appendix: File Reference

| File Path | Lines | Purpose |
|-----------|-------|---------|
| `ops/services.json` | all | Service registry (single source of truth) |
| `runtime/bridge.py` | 1–927+ | HTTP face + Suite binding + routes |
| `runtime/session_supervisor.py` | 1–1712 | Claude Code fleet manager (session Fabric F1.1) |
| `ops/cli/app.py` | all | `company` command dispatcher |
| `ops/cli/sessions.py` | all | Session Fabric operator face |
| `ops/cli/registry.py` | all | Service registry loader |
| `ops/cli/gpu.py` | all | VRAM budgeter (resource manager) |
| `ops/cli/systemd.py` | all | systemd driver (user + system units) |
| `ops/systemd/company.target` | all | Master systemd target |
| `ops/systemd/company-bridge.service` | all | Bridge unit |
| `ops/systemd/company-session-supervisor.service` | all | Supervisor unit |
| `ops/AGENTS.md` | all | CLI constitution (rules for extending) |
| `fabric/config.py` | all | Fabric configuration (litellm proxy, etc.) |
| `runtime/suite.py` | all | Cognition engine (brain, memory, graph) |
| `store/fs_store.py` | all | File-backed event store |

---

**Status:** Descriptive map of live infrastructure. Integration design ready for Phase 1 review.

