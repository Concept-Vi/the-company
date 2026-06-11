---
type: contract-transports
captured: 2026-06-12
status: living — F1 transports; lanes F2+ append their own
---

# TRANSPORTS — transport ids → protocol, exposure, caller identity, inventory source

Bindings in resource entries reference these ids. Exposure values are the registry keys the
entries cite (`exposure.json#<id>`); `exposure.json` itself is a GENERATED artifact of
`tools/extract_reality.py`, which is NOT YET BUILT — until it lands, the exposure values
stated here are hand-verified against the code (each cites its ground truth) and the
machine-diff (V24) is an open obligation, stated loudly per the format's fail-loud rule.

## `mcp-company` — the company MCP server (the agent face)
- **Protocol:** MCP over stdio (FastMCP, `mcp_face/server.py`); every Claude Code session on
  this machine carries it via the user-scoped MCP config — zero setup, tools discoverable by
  description alone.
- **Exposure:** `process-local` (stdio; no socket exists — ground truth: server runs per-session
  as a child process).
- **Caller identity:** the calling Claude Code session. HONEST REALITY: identity is NOT
  ambient — `session_post` REQUIRES `from_session` explicitly (your own `session://<id>`);
  there is no implicit "your session" wired through the MCP transport today. Inbox reads are
  parameterized by explicit `session=` for the same reason.
- **Inventory source:** each consolidated tool module exports a closed `OPS` constant
  (CONTRACT-FORMAT §9.2; `mcp_face/tools/sessions.py` → `OPS = ("list","inbox","watch",
  "describe")` + the split write tool `session_post`). Drift teeth:
  `tests/supervisor_routes_acceptance.py`. (Other tool modules predate the obligation; the
  extractor will fail loud on them when it lands — recorded, not hidden.)

## `supervisor-http` — the session supervisor service
- **Protocol:** HTTP/JSON on `127.0.0.1:8771` (`runtime/session_supervisor.py`; service row
  `session-supervisor` in `ops/services.json`, unit `company-session-supervisor.service`,
  started via `company up session-supervisor`).
- **Exposure:** `localhost-only` — binds 127.0.0.1 with deliberately NO env var to widen
  (audit B3: wider exposure = recorded decision + code change). One ndjson streaming GET
  (`/watch`); everything else request/response JSON.
- **Caller identity:** anonymous-local (anything on this host). Writes accept a free-text
  `source` self-label (audited into events/records, not authenticated).
- **Inventory source:** `SUPERVISOR_ROUTES` in `runtime/session_supervisor.py` — a structured
  `(method, path)` tuple (§9.3), bidirectional drift teeth in
  `tests/supervisor_routes_acceptance.py`.

## `bridge-http` — the operator bridge
- **Protocol:** HTTP/JSON + SSE on `127.0.0.1:8770` (`runtime/bridge.py`).
- **Exposure:** `localhost-only` locally; selected paths are also served over Tailscale
  (`tailscale serve` — the recorded mobile-access decision). Fabric entries that bind here
  mark exposure per the registry when the path is decided.
- **Caller identity:** anonymous-local / tailnet device. Non-session consumers name
  themselves explicitly in `from`-shaped fields (`consumer://` scheme is PLANNED, §9.7 —
  until it lands a stable self-chosen label is the convention, stated per-op).
- **Inventory source:** `BRIDGE_ROUTES` in `runtime/bridge.py` (flat path tuple; methods
  ride comments — the §9.1 structured `(path, method)` upgrade is an open obligation that
  lands with the first fabric route). Drift teeth: `tests/bridge_routes_acceptance.py`.
- **F1 status:** carries the EVENT surface today (`GET /api/stream` SSE + `GET /api/events`
  snapshot). NO fabric-specific routes yet — every bridge binding on session/session-message
  ops is `planned`.

## `cli-local` — the company console
- **Protocol:** local process exec — `company <noun> <op>` (`ops/cli/app.py` dispatcher,
  one thin module per noun per UPDATING.md; `company session …` is `ops/cli/sessions.py`,
  a pure HTTP face onto supervisor-http: the console NEVER spawns claude itself).
- **Exposure:** `process-local` (a local binary; reaches only localhost services).
- **Caller identity:** the operator at the shell (Tim). `source: "cli"` is stamped on writes.
- **Inventory source:** the `ops/cli/app.py` dispatch chain + per-noun modules. HONEST GAP:
  no exported machine-readable command registry constant yet — extract_reality will need one
  (same obligation class as §9.2); recorded here so V21 has its target, never silently passed.

## `tui-interactive` — the Claude Code interactive terminal (F2: a NON-fabric surface, declared for honesty)
- **Protocol:** the interactive `claude` TUI — slash commands (`/rewind`, `/compact`, `/context`,
  `/clear`, `/btw`, `/branch`, `/resume`) and key chords (`Esc Esc`). NOT a programmatic transport:
  no socket, no API, no machine-readable request shape.
- **Exposure:** `process-local` — it is a human-driven terminal, not reachable by any fabric
  consumer. The Company supervisor spawns headless `claude -p`, which has NO interactive TUI, so
  the supervisor cannot drive these surfaces at all.
- **Caller identity:** the human at the terminal. There is no fabric caller.
- **Inventory source:** NONE that the Company exposes — this is precisely the F2 gap. The
  authoritative inventory of these surfaces is the Claude Code docs (vault `claude-code-atlas`:
  checkpointing.md, context-window.md, interactive-mode.md, commands.md, sessions.md), cited
  per-op. V21 would FAIL a fabric binding on this transport because no machine-readable Company
  inventory exists; every F2 binding marked `kind: tui` is therefore `status: planned` and carries
  no exposure registry key (`exposure: "n/a — interactive"`). Recorded loudly, never silently
  passed — when these are bridged (Atlas CC-18, SDK-shaped), they migrate to `agent-sdk` below.

## `agent-sdk` — the Claude Agent SDK in-process API (F2: a NON-fabric surface, declared for honesty)
- **Protocol:** the `@anthropic-ai/claude-agent-sdk` (TS) / `claude_agent_sdk` (Python) in-process
  library: `ClaudeAgentOptions(enable_file_checkpointing=…)`, `rewind_files(uuid)` / `rewindFiles`,
  `/compact` sent as a prompt string, the `compact_boundary` system message, the `PreCompact` hook,
  `UserMessage.uuid` restore points (requires `extraArgs {replay-user-messages: null}`).
- **Exposure:** `process-local` — an in-process SDK call inside whatever program holds the session.
  The Company supervisor uses headless `claude -p` over stream-json but does NOT use the SDK's
  checkpointing/compaction options, so these are not wired through any Company endpoint today.
- **Caller identity:** the SDK program holding the `ClaudeSDKClient` / `query()` session. No fabric
  caller.
- **Inventory source:** the Agent SDK reference (vault `claude-code-atlas`:
  agent-sdk/file-checkpointing.md, agent-sdk/agent-loop.md, agent-sdk/typescript.md,
  agent-sdk/subagents.md), cited per-op. As with `tui-interactive`, NO machine-readable Company
  inventory exists; F2 `kind: sdk` bindings are `status: planned` with `exposure: "n/a — Agent SDK
  in-process"`. Bridging them is owned by the headless/SDK lane (Atlas CC-18); F2 records the
  capability and the absent bridge. This is the natural carrier for a future fabric checkpoint/
  context endpoint.
