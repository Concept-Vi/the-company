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
  ride the dispatcher — each fabric path is dispatched by BOTH a GET arm and a POST arm, see
  the method table below). Drift teeth: `tests/bridge_routes_acceptance.py` (literal `path ==`
  grep, both directions). The §9.1 structured `(path, method)` upgrade stays an open obligation
  for the OLDER routes; the ③④⑤ fabric routes carry their methods in the table here.
- **F1 status:** carries the EVENT surface (`GET /api/stream` SSE + `GET /api/events` snapshot)
  AND — as of the Capability Fabric L-Wire lane — the ③④⑤ CONFIG-AUTHORING / DEV-BRIDGES /
  AUTOMATION routes. session/session-message bridge bindings remain `planned`.
- **③④⑤ Capability Fabric routes + methods** (each route is ONE path dispatched by a GET read
  arm AND a POST write arm, both LITERAL `path ==`/`self.path ==`, both delegating to the SAME
  `runtime.capability_handlers.HANDLERS[key].fn` the MCP face calls — DRY, drift-tested
  byte-identical by `tests/capability_handlers_acceptance.py` §4). GET carries the READ ops
  (`?op=list|get|read|resolve|describe`); POST carries the consequential WRITE `act` (body
  `{op:"act", act:…, consent?:…}`). The handler declares its RAIL and a sanctioned SERVICE
  executes — the bridge NEVER shells/spawns (the floor):

  | route | methods | handler key | rail | CC |
  |---|---|---|---|---|
  | `/api/config/hooks` | GET·POST | `config.hooks` | R3 | CC-12 |
  | `/api/config/mcp-servers` | GET·POST | `config.mcp_servers` | R3 | CC-11 |
  | `/api/config/output-style` | GET·POST | `config.output_style` | R3 | CC-26 |
  | `/api/config/commands` | GET·POST | `config.slash_commands` | R3 | CC-03 |
  | `/api/config/plugins` | GET·POST | `config.extensions` | R3 | CC-13/CC-34 |
  | `/api/config/patterns` | GET·POST | `config.patterns` | direct-read | CC-27 |
  | `/api/config/keybindings` | GET·POST | `config.keybindings` | R3 | CC-04 (reopened) |
  | `/api/config/telemetry` | GET·POST | `config.telemetry` | R3 | CC-32 (reopened) |
  | `/api/config/provider` | GET·POST | `config.provider` | R3 | CC-29 (reopened) |
  | `/api/dev/git` | GET·POST | `dev.git` | R3 | CC-06 |
  | `/api/dev/code-intel` | GET·POST | `dev.code_intel` | R1-prime → `supervisor-http` | CC-16 |
  | `/api/dev/computer-use` | GET·POST | `dev.computer_use` | R1-prime → `supervisor-http` | CC-17 |
  | `/api/dev/code-review` | GET·POST | `dev.code_review` | R2 → `wire-job` | CC-19 |
  | `/api/dev/ci` | GET·POST | `dev.ci` | R3 | CC-30 |
  | `/api/auto/routines` | GET·POST | `auto.routines` | R3 | CC-21 |
  | `/api/auto/workflows` | GET·POST | `auto.workflows` | R1 → `supervisor-http` / R2 → `wire-job` (loop) | CC-22 |
  | `/api/auto/cost` | GET·POST | `auto.cost` | direct-read | CC-20 |
  | `/api/auto/auth` | GET·POST | `auto.auth` | R3 | CC-24.1 read / CC-24.2·.3·.4 acts (reopened) |

  CALLER IDENTITY for the consequential ③④⑤ writes (R3 / R1-prime / R2): the operator-vantage
  posture (the `/api/resolve` operator-only precedent, §5.3). A cold MCP agent reaches the READ
  surface and may build a write intent/job, but the consequential write rides the operator
  consent beat (sole-operator: consent-not-lockdown — never a multi-user wall, never a denial;
  an unconsented dangerous act returns a pending-proposal). R3 writes route to the
  `config_writer` service; R1-prime to `supervisor-http` (a wider-allowlist `bridge-session`
  spawn); R2 to `wire-job` (below). The async ④⑤ acts return a job/intent receipt + a watch
  cursor — the consequence rides the event stream, never the response body (§3.3/§8 async proof).

## `wire-job` — the headless `claude -p` wire (R2: the Capability Fabric async executor)
- **Protocol:** a HEADLESS `claude -p "<instruction>" --output-format json` run-and-capture job,
  NOT an interactive session and NOT the supervisor mailbox (only deliver/wake/consult ride
  `supervisor-http`'s R1). `runtime/implement.py` `launch()` (cmd at `:320`,
  `--output-format json`) is the executor; jobs are dispatched off the operator-only
  `POST /api/resolve` seam on `bridge-http` (the build-intent → claude -p wire). Permission
  posture defaults to PLAN (`COMPANY_WIRE_PERMISSION`, `implement.PERMISSION_MODE` `:42` —
  read-only: a plan-mode run changes/commits nothing) and concurrency is capped
  (`COMPANY_WIRE_CONCURRENCY`, `implement.CONCURRENCY_CAP` `:43`).
- **Exposure:** `process-local` — `launch()` spawns the `claude` binary as a child process on
  this host; there is NO socket of its own. It is reached only INDIRECTLY, through the
  operator-only `/api/resolve` seam on `bridge-http` (so its network exposure is `bridge-http`'s,
  localhost-only). A cold consumer cannot reach it directly.
- **Caller identity:** the operator, via the `/api/resolve` operator-vantage seam (§5.3). The
  Capability Fabric ④ `dev.code_review` (review-local / security-review-local / review-pr) and
  ⑤ `auto.workflows` act=loop write a WIRE-JOB INTENT through their handlers and return a job-id
  + watch cursor; the operator's `/api/resolve` approval + the wire-loop dispatch the run. The
  handler NEVER calls `implement.launch` itself (the floor — it builds the intent; the sanctioned
  wire acts).
- **Inventory source:** `runtime/implement.py` `launch()` + the `/api/resolve` dispatch chain on
  `bridge-http` (`BRIDGE_ROUTES` carries `/api/resolve`). HONEST GAP: there is no exported
  machine-readable wire-job command registry constant yet (same obligation class as §9.2/the
  `cli-local` gap); recorded here so V21 has its target, never silently passed. The job's
  CONSEQUENCE rides the existing dispatch events on the event stream (`GET /api/stream`), not a
  response body — the async proof shape (§8): `building → live` only when a REAL review job
  round-trips by use (the build lead's `live-verify pending` slice — no `claude -p` is fired in
  the build itself, lead-only law).

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

## `substrate-mcp` — the knowledge-vault search face (F6) — EXTERNAL, wired in
- **Protocol:** MCP over stdio. NOT company-owned code — it is a SEPARATE repo
  (`/home/tim/repos/obsidian-overlord`, run as `…/.venv/bin/python -m substrate_mcp.server`,
  state dir `…/.state`), wired into every Claude Code session via the user-scoped MCP config
  (verified in `~/.claude.json` mcpServers, 2026-06-12). The company DEPENDS on it for the
  knowledge-search capability; it does not own it (found-elsewhere ≠ company-owned — the
  binding cites this external transport honestly rather than claiming a company face).
- **Exposure:** `process-local` (stdio; no socket).
- **Caller identity:** none — search needs no identity; the vaults are read-only reference.
- **Inventory source:** the substrate server's OWN tool registry (its FastMCP tool set:
  `search_semantic`, `list_vaults`, `get_status`, `get_by_address`, …). It has NO company-side
  `OPS` constant (it is not company code) — for V21/V22 its inventory source is the external
  server's tool list, recorded as an external dependency, never a phantom company route.
- **F6 status:** `building` and VERIFIED-BY-USE — `list_vaults` + `get_status` + `search_semantic`
  over `claude-code-atlas` (287f/6958c) and `claude-platform-docs` (811f/23274c) all ran live
  2026-06-12; every cited fact in the F6 entries traces to a returned chunk's source address.

## `anthropic-admin-api` — the Anthropic org Usage & Cost API (F6) — EXTERNAL, not proxied
- **Protocol:** HTTPS to `api.anthropic.com` (`/v1/organizations/usage_report/messages`,
  `/v1/organizations/me`, the Claude Code Analytics API). NOT a company face.
- **Exposure:** `authed` — requires an Anthropic ADMIN key (`x-api-key: $ANTHROPIC_ADMIN_KEY`,
  `anthropic-version` header); org-scoped data.
- **Caller identity:** the org Admin key.
- **Inventory source:** the Anthropic API reference (external). The company does NOT proxy this
  today — `cost-usage.get`'s binding on it is `planned`, and the endpoint belongs in
  INVENTORY-EXCLUSIONS.md as "external Anthropic API, not a company face" so the reality join
  never phantom-fails on a route the company was never going to own.

## `claude-cli` — the Claude Code CLI binary's management subcommands (F4: a NON-fabric surface, declared for honesty)
- **Protocol:** the `claude` binary's non-interactive management subcommands and launch flags —
  `claude mcp add|add-json|add-from-claude-desktop|remove|list|get|reset-project-choices`,
  `claude plugin init|validate`, `claude mcp serve`, and the `--plugin-dir`/`--plugin-url` launch
  flags. NOT a programmatic transport: it is a local CLI of the `claude` binary (distinct from
  `cli-local`, which is the COMPANY `company` console). No socket, no API, no machine-readable
  request shape the Company exposes.
- **Exposure:** `process-local` — a local binary on this host. NOT reachable by any fabric consumer;
  the Company supervisor spawns headless `claude -p` and does not drive these management subcommands.
- **Caller identity:** the operator at the shell. There is no fabric caller.
- **Inventory source:** NONE that the Company exposes — this is precisely the F4 gap. The
  authoritative inventory is the Claude Code docs (vault `claude-code-atlas`: mcp.md, plugins.md,
  plugins-reference.md, skills.md, discover-plugins.md, plugin-marketplaces.md), cited per-op. V21
  would FAIL a fabric binding on this transport because no machine-readable Company inventory exists;
  every F4 `kind: cli`/`kind: tui` binding is therefore `status: planned` and carries no exposure
  registry key (`exposure: "n/a — claude CLI"` / `"n/a — interactive"`). Recorded loudly, never
  silently passed — when these management surfaces are bridged (a future settings/config-writer +
  install bridge), they migrate to `bridge-http`.

## `claude-tui` — the Claude Code interactive management menus (F4: a NON-fabric surface, declared for honesty)
- **Protocol:** the interactive `claude` TUI's management surfaces — `/hooks` (read-only hook
  browser), `/mcp` (MCP server panel + OAuth flow), `/plugin` (plugin/marketplace manager), `/config`
  (output-style picker + settings), `/statusline` (NL status-line generator), `/help`/`/skills`/
  `/agents` (extension listings), `/reload-plugins`. NOT a programmatic transport: no socket, no API,
  no machine-readable request shape. (Distinct from F2's `tui-interactive`, which covers the
  session/context slash commands; this id covers the EXTENSION-FABRIC management menus. A lane may
  fold these two ids together later via a recorded decision; kept separate here so F4's gap is
  legible without rewriting F2's transport.)
- **Exposure:** `process-local` — human-driven terminal, not reachable by any fabric consumer. The
  Company supervisor spawns headless `claude -p` (no interactive TUI), so it cannot drive these menus.
- **Caller identity:** the human at the terminal. No fabric caller.
- **Inventory source:** NONE that the Company exposes (the F4 gap). Authoritative inventory = the
  Claude Code docs (vault `claude-code-atlas`: hooks.md, mcp.md, plugins.md, output-styles.md,
  statusline.md, skills.md), cited per-op. V21 FAILS a fabric binding here for want of a
  machine-readable Company inventory; F4 `kind: tui` bindings are `status: planned`,
  `exposure: "n/a — interactive"`. Migrates to `bridge-http` when bridged.
