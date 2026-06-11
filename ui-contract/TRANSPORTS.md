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
