"""runtime/session_supervisor.py — the SESSION SUPERVISOR service (Session Fabric F1.1, guide §A).

The fabric's engine spine: ONE long-running service that OWNS N concurrent Claude Code
subprocesses — spawn (new | --resume | --resume --fork-session) · inject (a user turn pushed
into a live session) · interrupt · teardown — and fans each session's events to subscribers
as ndjson. It is the push tier the T2 harness proved (~/xsession-tests/RESULTS.md): a claude
process held open under `--input-format stream-json` accepts injected turns while idle, with
full memory and the same session_id.

THE LAWS THIS SERVICE CARRIES (each cites its ruling):
  · EXPOSURE (audit B3): binds 127.0.0.1 ONLY. There is deliberately no env var to widen the
    bind — any wider exposure (tailnet/authed) is an explicit recorded decision + a code change
    here, never a quiet env flip.
  · SINGLE WRITER (audit C6 / synthesis §3 landmine): this service is the ONLY process that
    emits `agent_sessions.*` events onto the shared events.jsonl — the bridge and the MCP face
    route fabric intents here via the mailbox and emit nothing fabric-shaped themselves. One
    writer → the in-process seq lock suffices → no cross-process duplicate-seq hazard.
  · ONE OWNER PER SESSION (T1): the supervisor is the only process that resumes a session it
    has live — concurrent resume elsewhere talks to a disk-loaded copy, never the live mind.
  · ENFORCED WALL-CLOCK (audit C3): a per-turn watchdog REAPS a session whose turn exceeds
    COMPANY_FABRIC_TURN_TIMEOUT_S (default 900 — implement.py DEFAULT_TIMEOUT_S precedent,
    the constant that actually enforces; ui_claude_session.TURN_TIMEOUT_S was a dead constant
    and this module does not repeat that mistake). A silently-hung no-output subprocess is
    reaped, never blocks forever.
  · CONCURRENCY CAP (audit C9): COMPANY_FABRIC_CONCURRENCY (call-time env read, default 3 —
    the implement.py CONCURRENCY_CAP precedent) caps live sessions AND consult fan copies;
    above it the service refuses LOUD with a teaching error that names the cap, the env var,
    what is live, and how to free a slot.
  · PERMISSION POSTURE: COMPANY_FABRIC_PERMISSION (call-time read, default "plan" — read-only;
    the COMPANY_WIRE_PERMISSION / COMPANY_PANEL_PERMISSION twin). acceptEdits is opt-in only.
  · THE FLOOR: this is a SERVICE (an operator-sanctioned process like the bridge), NOT the MCP
    face. mcp_face NEVER imports this module; the face writes *intents* to the mailbox and this
    service is the only thing that launches/resumes claude processes (synthesis §6.3 split).
  · NO ORPHANS: every owned subprocess is terminated on teardown/SIGTERM/exit (atexit +
    signal handlers); under systemd the cgroup is the second net.

TRANSPORT (NET-NEW, T2-proven — audit N4 honesty): held-open stdin + `--input-format
stream-json` + `--output-format stream-json`. `ui_claude_session.run_turn` is NOT reused for
the loop (it has no stdin-injection mode — one subprocess per turn, prompt as argv); what IS
reused from it: binary resolution (_find_claude), the strict company MCP config, and the
stream-event parsing shapes. Per-turn `--resume` re-spawn remains the documented fallback if
the held-open loop misbehaves under real load.

MAILBOX (coordinate-by-contract, guide §C — this module CONSUMES the leaf, it does not build
§C's tools): intents ride `<store>/agent_sessions/mail.jsonl`, one json object per line:
  {id, to: "session://<id>", from, verb: deliver|wake|consult, cas, [copies]}
Body text lives in cas (store.get_content) — messages stay small (<4KB single O_APPEND write,
the fs_store ref-history atomicity argument). Consumption is a per-consumer CURSOR (a ref —
`agent_sessions/cursor:supervisor` — holding the consumed byte offset; synthesis §2.3's
cheaper-than-RMW design). Replies/acks are appended to the SAME leaf via the store's own
`append_agent_mail` (verb: reply | error, `re` = the intent id, `thread` = the intent's thread
— seq-stamped + inbox-visible; the first commit's raw-append seam is closed), and the completed turn is claimed
durably as an `agent_sessions.turn` event (the _emit_durable class — its loss would change
behavior). F1 SIMPLIFICATION (stated, not hidden): intents are consumed strictly in order; an
intent whose target is mid-turn HOLDS the cursor (head-of-line blocking, retried next poll) so
a crash never skips an unhandled intent. A per-target queue is a later refinement.

VERBS = ROUTING DECISIONS (guide prime principle 2):
  DELIVER → inject into a session this supervisor holds live.
  WAKE    → spawn a supervisor-owned process on a non-live session id (`--resume`), then inject.
  CONSULT → spawn on a FORKED copy (`--resume --fork-session`, T4-proven non-destructive),
            N-fan ≤ cap, never touches the original.

HTTP API (127.0.0.1:<port>, default 8771 — the services.json row cites this same number):
  GET  /health                 → {ok, service, sessions, cap, turn_timeout_s, bind}
  GET  /sessions               → every owned session's record (state machine:
                                 starting → idle ⇄ busy → closed)
  GET  /watch?session=<id>     → ndjson stream of that session's events (replay + live)
  POST /spawn                  {cwd?, resume?, fork?, name?, prompt?, source?}
  POST /inject                 {session, message, source?}
  POST /interrupt              {session}   (control_request on stdin — see _interrupt note)
  POST /teardown               {session}
  POST /bridge-session         {operator_consent, capabilities?, extra_tools?, cwd?, resume?,
                                fork?, name?, prompt?, permission_mode?, model?, …}
                               RAIL R1-prime (Capability Fabric ④): a CONSENT-GATED spawn with a
                               WIDER --allowedTools (Bash/git/LSP-family/web + mcp__company) and an
                               in-session write posture, for ④'s in-session git/LSP/web ops. The
                               floor mcp__company-only spawn cannot carry those. operator_consent
                               (the /api/resolve operator-vantage gate) is REQUIRED — refused-loud
                               (403) without it: consent-not-lockdown, the profile is always
                               available, git-revert backstops. computer/browser are macOS+
                               interactive-only host boundaries (Atlas computer-use.md) — never
                               bindable on this -p/Linux rail, refused-loud. Results ride back as
                               PROSE on the turn stream (liveness:stream, NO typed return_shape).

Run: .venv/bin/python runtime/session_supervisor.py [port]   ·   service: company up session-supervisor
Proven by: tests/session_supervisor_acceptance.py (stub-binary service-level checks; real-claude
end-to-end verification is the build lead's, per the lane split)."""
from __future__ import annotations

import atexit
import json
import os
import signal
import subprocess
import sys
import threading
import time
import uuid
from collections import deque
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from store.fs_store import FsStore
from fabric import config as fcfg
from runtime import ui_claude_session as _panel   # reuse: _find_claude + _MCP_CONFIG (one source
                                                  # of the binary + the strict company-MCP config).
                                                  # This import is service→runtime, NOT the MCP face —
                                                  # the panel module's floor note covers it explicitly.
from runtime import render_declaration as _rd     # R1.2 — the render-declaration layer: every claude
                                                  # emit is declared (placement/component/fields) and
                                                  # fanned as a `declared` event; an undeclared or
                                                  # family-fallback emit fires the drop hook below
                                                  # (gap-pressure: the registry's sensor).

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PORT = 8771                    # next free beside the bridge's 8770 (audit N7 — the ONE number
                                       # services.json + the unit + the contract entries all cite)

# THE INVENTORY SOURCE for the supervisor-http transport (CONTRACT-FORMAT §9.3 / V21: a transport
# without a machine-readable registry fails contract validation — the BRIDGE_ROUTES law applied here,
# (method, path) structured from birth per §9.1). tests/supervisor_routes_acceptance.py is the drift
# teeth: this tuple and the do_GET/do_POST dispatch literals must match, BOTH directions.
SUPERVISOR_ROUTES = (
    ("GET", "/health"),
    ("GET", "/sessions"),
    ("GET", "/watch"),
    ("POST", "/spawn"),
    ("POST", "/inject"),
    ("POST", "/interrupt"),
    ("POST", "/teardown"),
    ("POST", "/bridge-session"),   # RAIL R1-prime: consent-gated wider-allowlist spawn (④ in-session git/LSP/web)
)
MAIL_LEAF = "agent_sessions"           # naming law: agent_sessions everywhere (never fabric/, never sessions/)
CURSOR_REF = "agent_sessions/cursor:supervisor"   # per-consumer mailbox cursor (a ref, §2.3 pattern)
INIT_WAIT_S = float(os.environ.get("COMPANY_FABRIC_INIT_WAIT_S", "15"))  # max crash-watch window at spawn
SPAWN_SETTLE_S = float(os.environ.get("COMPANY_FABRIC_SPAWN_SETTLE_S", "1.0"))  # brief instant-crash settle before a live stream-json process is promoted idle (init is post-first-message; see _spawn wait_init)
MAIL_POLL_S = 0.5
WATCHDOG_POLL_S = 0.5


def fabric_concurrency() -> int:
    """The live concurrency cap — CALL-TIME env read (the implement.py permission_mode() pattern:
    a deliberately-set env flips the posture without a restart; tests monkeypatch it). Default 3
    (the COMPANY_WIRE_CONCURRENCY precedent). Registry-served default is the F-tier follow-up —
    the env var stays the override either way."""
    return int(os.environ.get("COMPANY_FABRIC_CONCURRENCY", "3"))


def fabric_permission() -> str:
    """Live permission posture for supervised sessions (call-time read; default plan = read-only)."""
    return os.environ.get("COMPANY_FABRIC_PERMISSION", "plan")


def turn_timeout_s() -> float:
    """The ENFORCED per-turn wall-clock ceiling (audit C3). Call-time read so the acceptance test
    runs the reap in seconds; default 900 = implement.py DEFAULT_TIMEOUT_S, the precedent that
    actually enforces (never the dead-constant pattern)."""
    return float(os.environ.get("COMPANY_FABRIC_TURN_TIMEOUT_S", "900"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TeachingRefusal(Exception):
    """A refusal that TEACHES (audit C9): the message names the limit, the live state, and the
    way forward. Mapped to HTTP 429/409 — never a bare error."""


# ─────────────────────────── RAIL R1-prime · the `bridge-session` spawn PROFILE ───────────────────
# (Capability Fabric ③④⑤ — L-FOUND-R1prime; arch doc §3.1/§5.1/§5.4). The supervised sessions this
# service normally owns are spawned `--allowedTools mcp__company` (the FLOOR — no Bash/Edit/LSP/web;
# session_supervisor module-docstring + sessions.py floor note). That floor is correct for the
# fabric's read/route work, but it makes ④'s IN-SESSION capabilities (git via Bash, LSP nav via the
# Read/Edit family, web fetch/search) physically impossible: a session that "wants Bash and cannot
# call it" is a silent no-op (violates no-silent-failures). R1-prime is the NAMED, deliberate spawn
# POSTURE that opens a WIDER allowlist for exactly those ops — it is NOT "an intent kind", it is a new
# security decision (arch doc §1.1 / Critique-A finding).
#
# SOLE-OPERATOR SECURITY MODEL (Tim's explicit steer — consent-not-lockdown): Tim is the only user and
# is trusted. The wider profile is ALWAYS AVAILABLE — never locked out, never an auth wall. The gate is
# a CONSENT BEAT: a dangerous wider spawn must carry an explicit `operator_consent` signal (the
# /api/resolve operator-vantage precedent), and `git revert` is the backstop. An AGENT must not trigger
# an irreversible wider spawn without that signal; the OPERATOR can always consent. The gate is a
# marker, not a denial (build the gates as consent-flags, not lockouts).
#
# THE ALLOWLIST IS ATLAS-GROUNDED, NEVER INVENTED (verified 2026-06-12 via the Claude Code Atlas):
#   · `--allowedTools` takes a comma-separated list of tool specifiers — bare names (`Bash`, `Read`,
#     `Edit`, `WebFetch`, `WebSearch`) or parenthesized patterns (`Bash(git *)`, `Edit(/src/**)`)
#     (Atlas Docs/claude-code/headless.md#auto-approve-tools · tools-reference.md). Example shipped in
#     the docs: `--allowedTools "Bash,Read,Edit"`.
#   · GIT is "native Bash-tool git" (corpus git.md:46) → granted by `Bash` (or the tighter `Bash(git *)`
#     when git_only is asked). `gh pr create` likewise rides Bash.
#   · LSP code-intel: the LSP tool is governed by the Read/Edit permission family (Atlas tools-reference:
#     a `Read(...)` rule "Applies to Read, Grep, Glob, LSP") → granted by `Read`+`Edit` here.
#   · WebFetch/WebSearch are ordinary session tools, grantable to a `-p` run by name.
# COMPUTER-USE IS A HARD HOST/RAIL BOUNDARY, NOT A GRANT (the decisive Atlas correction to the arch
# doc's §5.4 optimism): the built-in `computer-use` MCP server "is not available in non-interactive
# mode with the -p flag" AND "Computer use in the CLI is not available on Linux or Windows" — it is
# macOS + interactive-session ONLY (Atlas computer-use.md:29,:223). This R1-prime rail is a headless
# `claude -p` session on a WSL2/Linux host, so the `computer` tool can NEVER resolve here. Asking for it
# is REFUSED-LOUD (never an allowlist entry that would silently never bind — that is exactly the
# requires_tool_grant failure §5.4 forbids being opaque). `browser` (Claude-in-Chrome) is beta + not-WSL
# (corpus computer-use.md / chrome.md) — also refused-loud on this host, NEVER green-painted.

# The wider tool set the profile grants by default (Atlas tool names; mcp__company stays so the session
# keeps every company tool too). git rides Bash; LSP rides the Read/Edit family.
BRIDGE_SESSION_TOOLS = ("mcp__company", "Bash", "Edit", "Read", "Glob", "Grep", "WebFetch", "WebSearch")
# The default in-session write posture for the profile. `plan` would DEFEAT the profile (no writes);
# `bypassPermissions` is over-broad. `acceptEdits` is the honest middle: file writes + common fs
# commands auto-approve, other shell/network still ride the allowlist above (Atlas headless.md). The
# spawn body may override via permission_mode (still consent-gated).
BRIDGE_SESSION_PERMISSION = os.environ.get("COMPANY_BRIDGE_SESSION_PERMISSION", "acceptEdits")
# The capabilities a caller may NAME on a bridge-session, → the tools each needs (the requires_tool_grant
# registry surface, §5.4). `git`/`lsp`/`web` are grantable on this rail; `computer`/`browser` are the
# host/rail boundaries that REFUSE LOUD (so the boundary is explicit, never an opaque failure).
BRIDGE_SESSION_CAPABILITIES = {
    "git": ("Bash",),                  # native Bash-tool git + gh (corpus git.md)
    "lsp": ("Read", "Edit"),           # the LSP tool's permission family (Atlas tools-reference)
    "web": ("WebFetch", "WebSearch"),  # ordinary -p-grantable session tools
    "edit": ("Edit", "Read"),          # in-session file authoring (e.g. ci scaffold write)
}
# capabilities that CANNOT run on this rail (headless -p / Linux host) — naming one is a teaching refusal,
# the value is the reason (surfaced, never silent — §5.4 requires_tool_grant honesty).
BRIDGE_SESSION_UNAVAILABLE = {
    "computer": ("computer use in the CLI is macOS-only AND requires an interactive session — it is "
                 "explicitly NOT available in non-interactive `-p` mode (Atlas computer-use.md:29,:223). "
                 "This R1-prime rail is a headless `-p` session on a WSL2/Linux host, so the `computer` "
                 "tool can never bind here. There is no flag that changes this; it is a host+rail "
                 "boundary, not a missing grant."),
    "browser": ("Claude-in-Chrome browser automation is beta and NOT available on WSL/Windows "
                "(corpus computer-use.md / chrome.md). On this host the browser tool cannot bind; this "
                "stays needs-tim / planned, never green-painted to live."),
}


# ─────────────────── R1.3 · the SPAWN-FLAG ASSEMBLY TABLE (registry-is-truth for POSTURE) ──────────
# LANE-SUPERVISOR-REFACTOR (2026-06-14, F-FIX-5 steps 5-6): the hand-written SPAWN_FLAGS dict that
# carried a `posture` column PER FLAG has been DELETED. Posture is now DERIVED from the Mirror-Registry
# rules (introspection.rules.classify over the claude-code PlatformEntry's signal_sets), swap-aware via
# R6 — the registry is the SOLE source of truth for a flag's posture (locked/consent/safe). This table
# carries ONLY the CONSUMER-EMISSION data the SpawnFlagAssembler needs and the registry does not hold:
#   flag    — the real `--flag` name the body-key emits (the FK; also in platforms/claude_code.py's
#             SPAWN_FLAG_BODY_KEY_MAP, the registry-side single source — kept consistent by the
#             crosscheck which derives posture by THAT map).
#   kind    — the assembler kind: bool (token only, when truthy) · value (flag + str) · csv (flag +
#             comma-join) · repeat (flag per list item) · swap (replace a head flag's value in place).
#   teach   — the teaching-refusal / summary text emitted on a locked/consent refusal.
# The body-keys here are the SAME keys the prior SPAWN_FLAGS declared (a new flag is still a new row).
# Posture is NEVER stored here — _registry_posture(flag) derives it live. The crosscheck fixture
# (tests/spawn_flags_crosscheck_acceptance.py) is now a SELF-CONSISTENCY gate: every assembly key's
# derived posture must classify cleanly (no R4 unmatched, no missing flag-name). Every flag is grounded
# in the Claude Code Atlas cli-reference (research lane 03-start-flags.md) — NEVER invented.
SPAWN_FLAG_ASSEMBLY: dict[str, dict] = {
    # ── assemblable rows (registry derives safe / consent; the assembler emits the flag) ──
    "session_id":            {"flag": "--session-id", "kind": "value",
                              "teach": "pre-assign the session UUID (the fabric's correlation handle)"},
    "name":                  {"flag": "--name", "kind": "value",
                              "teach": "human display name (the /resume picker + registry label)"},
    "continue":              {"flag": "--continue", "kind": "bool",
                              "teach": "resume the cwd's most recent conversation instead of starting new"},
    "append_system_prompt":  {"flag": "--append-system-prompt", "kind": "value",
                              "teach": "append to the default system prompt (keeps the coding-assistant identity)"},
    "append_system_prompt_file": {"flag": "--append-system-prompt-file", "kind": "value",
                              "teach": "append a file's contents to the default system prompt"},
    "system_prompt":         {"flag": "--system-prompt", "kind": "value",
                              "teach": "REPLACE the entire system prompt (persona sessions; drops default guidance)"},
    "system_prompt_file":    {"flag": "--system-prompt-file", "kind": "value",
                              "teach": "replace the system prompt from a file"},
    "max_turns":             {"flag": "--max-turns", "kind": "value",
                              "teach": "agentic-turn ceiling (safety governor; exceeds → error result)"},
    "max_budget_usd":        {"flag": "--max-budget-usd", "kind": "value",
                              "teach": "dollar ceiling for the session's API spend"},
    "json_schema":           {"flag": "--json-schema", "kind": "value",
                              "teach": "schema-validated structured output (result.structured_output)"},
    "agent":                 {"flag": "--agent", "kind": "value",
                              "teach": "run as a named subagent definition (persona)"},
    "agents":                {"flag": "--agents", "kind": "value",
                              "teach": "inline JSON agent definitions (ephemeral personas, no files)"},
    "setting_sources":       {"flag": "--setting-sources", "kind": "csv",
                              "teach": "which settings layers load (user/project/local) — isolation control"},
    "no_session_persistence": {"flag": "--no-session-persistence", "kind": "bool",
                              "teach": "ephemeral session — no transcript on disk, not resumable"},
    "include_hook_events":   {"flag": "--include-hook-events", "kind": "bool",
                              "teach": "hook lifecycle events on the stream (the R1.2 hook declarations)"},
    "prompt_suggestions":    {"flag": "--prompt-suggestions", "kind": "bool",
                              "teach": "emit prompt_suggestion after each turn (declared: input-suggestion)"},
    "replay_user_messages":  {"flag": "--replay-user-messages", "kind": "bool",
                              "teach": "ack injected user turns back on stdout (stream-json both ways)"},
    "advisor":               {"flag": "--advisor", "kind": "value",
                              "teach": "enable the server-side advisor model for this session"},
    "betas":                 {"flag": "--betas", "kind": "csv",
                              "teach": "beta API headers (API-key auth only)"},
    "exclude_dynamic_system_prompt_sections": {"flag": "--exclude-dynamic-system-prompt-sections",
                              "kind": "bool",
                              "teach": "move per-machine prompt sections into the first user message (cache reuse)"},
    "teammate_mode":         {"flag": "--teammate-mode", "kind": "value",
                              "teach": "agent-team teammate display mode (auto|in-process|tmux)"},
    "disable_slash_commands": {"flag": "--disable-slash-commands", "kind": "bool",
                              "teach": "disable all skills/commands for this session"},
    "debug_file":            {"flag": "--debug-file", "kind": "value",
                              "teach": "write debug logs to a specific path (implies debug mode)"},
    # ── rows the registry derives CONSENT for (widen the surface → the R1-prime consent beat) ──
    "tools":                 {"flag": "--tools", "kind": "value",
                              "teach": "restrict/widen which BUILT-IN tools exist ('' none · 'default' all · csv)"},
    "allowed_tools":         {"flag": "--allowedTools", "kind": "swap",
                              "teach": "REPLACE the floor allowlist (mcp__company-only) — the wider-surface decision"},
    "disallowed_tools":      {"flag": "--disallowedTools", "kind": "value",
                              "teach": "deny rules (bare name removes the tool; scoped rule denies matches)"},
    "mcp_config":            {"flag": "--mcp-config", "kind": "swap",
                              "teach": "REPLACE the strict company MCP config — different servers, different ground"},
    "permission_prompt_tool": {"flag": "--permission-prompt-tool", "kind": "value",
                              "teach": "route permission prompts to an MCP tool (approval plumbing)"},
    "plugin_dir":            {"flag": "--plugin-dir", "kind": "repeat",
                              "teach": "load local plugin(s) for this session"},
    "plugin_url":            {"flag": "--plugin-url", "kind": "repeat",
                              "teach": "fetch plugin zip(s) by URL for this session"},
    "add_dir":               {"flag": "--add-dir", "kind": "repeat",
                              "teach": "widen the session's filesystem reach to extra dir(s) — the "
                              "`dirs` capability axis, rides the operator-consent beat"},
    # ── rows the registry derives LOCKED for (transport invariants / dedicated body keys) ──
    # These carry the `why` teaching text the supervisor emits on the locked refusal. Their LOCKED
    # posture is NOT declared here — it is derived (R1 transport-invariant / body-key-override lock).
    "input_format":          {"flag": "--input-format", "kind": "value",
                              "teach": "--input-format stream-json IS the held-open injection contract "
                              "(T2) — the fabric cannot drive a session without it."},
    "print":                 {"flag": "-p", "kind": "bool",
                              "teach": "-p is the supervised transport's mode; it is always on."},
    "verbose":               {"flag": "--verbose", "kind": "bool",
                              "teach": "--verbose is required for the stream-json event surface the "
                              "reader parses; always on."},
    "output_format":         {"flag": "--output-format", "kind": "value",
                              "teach": "use the dedicated body key `output_format` (defaults to stream-"
                              "json — the reader's parse contract)."},
    "include_partial":       {"flag": "--include-partial-messages", "kind": "bool",
                              "teach": "use the dedicated body key `include_partial` (the R5 voice "
                              "seam's delta stream)."},
    "resume":                {"flag": "--resume", "kind": "value",
                              "teach": "use the dedicated body key `resume` (wake) — verbs are routing "
                              "decisions, not raw flags."},
    "fork_session":          {"flag": "--fork-session", "kind": "bool",
                              "teach": "use the dedicated body keys `resume`+`fork` (consult) — T4's "
                              "non-destructive copy path."},
    "model":                 {"flag": "--model", "kind": "value",
                              "teach": "use the dedicated body key `model`."},
    "effort":                {"flag": "--effort", "kind": "value",
                              "teach": "use the dedicated body key `effort`."},
    "fallback_model":        {"flag": "--fallback-model", "kind": "csv",
                              "teach": "use the dedicated body key `fallback`."},
    "permission_mode":       {"flag": "--permission-mode", "kind": "value",
                              "teach": "use the dedicated body key `permission_mode` (the fabric's "
                              "posture law: default plan, acceptEdits opt-in)."},
    "settings":              {"flag": "--settings", "kind": "value",
                              "teach": "use the dedicated body key `settings`."},
    "debug":                 {"flag": "--debug", "kind": "value",
                              "teach": "use the dedicated body key `debug`."},
    "safe_mode":             {"flag": "--safe-mode", "kind": "bool",
                              "teach": "use the dedicated body key `safe_mode`."},
    "bare":                  {"flag": "--bare", "kind": "bool",
                              "teach": "use the dedicated body key `bare`."},
    "dangerously_skip_permissions": {"flag": "--dangerously-skip-permissions", "kind": "bool",
                              "teach": "permission posture rides the dedicated `permission_mode` key "
                              "(bypassPermissions must be an explicit, visible posture choice — never "
                              "a side-door flag)."},
    "strict_mcp_config":     {"flag": "--strict-mcp-config", "kind": "bool",
                              "teach": "strictness is the grounding contract; to run different MCP "
                              "servers swap `mcp_config` (consent) — strict stays on so the session's "
                              "tool ground is always explicit."},
}


# ── the registry posture source (F-FIX-5 step 5 — the SOLE truth, swap-aware via R6) ────────────────
_PLATFORM_SIGNAL_SETS = None    # cached PlatformEntry.signal_sets (a file read, NO spawn) — loaded once


def _signal_sets():
    """Resolve the claude-code PlatformEntry's signal_sets ONCE (cached). This is a FILE read +
    head_builder derivation (the registry load), NOT a binary spawn — the transport_invariants are
    R6-corrected at load. FAIL LOUD if the platform row is missing (the registry is the sole posture
    truth now; a missing row is not a silent fall-back to a hand-list — there is no hand-list)."""
    global _PLATFORM_SIGNAL_SETS
    if _PLATFORM_SIGNAL_SETS is None:
        from introspection.platforms import platform_registry
        reg = platform_registry()
        entry = reg.get("claude-code")
        if entry is None:
            raise RuntimeError(
                "session_supervisor: no 'claude-code' PlatformEntry in the PlatformRegistry — the "
                "spawn-flag posture source (Mirror-Registry rules) cannot be resolved. The hand "
                "SPAWN_FLAGS dict was deleted (F-FIX-5 step 6); the registry is the sole truth. Fail "
                "loud, never spawn a session with an unclassifiable flag surface.")
        _PLATFORM_SIGNAL_SETS = entry.signal_sets
    return _PLATFORM_SIGNAL_SETS


def _registry_posture(flag_name: str) -> str:
    """DERIVE a flag's posture from the Mirror-Registry rules (introspection.rules.classify over the
    claude-code signal_sets) — the SOLE truth (F-FIX-5 step 5). Returns one of locked|hazard|consent|
    safe|unmatched. R1 LOCKED (transport invariant / body-key lock, R6-corrected) > R2 HAZARD (self-
    named danger) > R3 CONSENT (capability-axis widening, incl. --add-dir on `dirs` and the swap-kind
    head-defaults --allowedTools/--mcp-config) > R5 SAFE (expose default). The crosscheck fixture
    proves this reproduces every prior hand-posture (48/48, zero divergence)."""
    from introspection import rules
    posture, _rule, _axis = rules.classify(flag_name, _signal_sets())
    return posture


def _apply_spawn_flags(cmd: list, flags: dict | None, *, consent: bool) -> list:
    """R1.3 — apply registry-declared start-flags onto a built cmd (PURE; unit-testable without a
    spawn). Validates every key against SPAWN_FLAG_ASSEMBLY: unknown → TeachingRefusal listing the
    table; the POSTURE is DERIVED from the Mirror-Registry rules (_registry_posture — the sole truth,
    swap-aware via R6), NOT a hand-stored column: locked → TeachingRefusal carrying the row's `teach`;
    consent-posture without the operator-consent beat → TeachingRefusal naming the bridge-session
    path; a hazard posture (R2 self-named danger) is treated as locked (refused). `swap` rows replace
    the value of a flag already present in the transport head (--allowedTools / --mcp-config). Returns
    cmd (mutated in place for swap, appended otherwise). No flags → cmd unchanged (byte-identical
    guarantee holds)."""
    if not flags:
        return cmd
    if not isinstance(flags, dict):
        raise TeachingRefusal(f"REFUSED — `flags` must be an object of registry keys, got "
                              f"{type(flags).__name__}. Declared keys: {sorted(SPAWN_FLAG_ASSEMBLY)}.")
    for key, val in flags.items():
        spec = SPAWN_FLAG_ASSEMBLY.get(key)
        if spec is None:
            raise TeachingRefusal(
                f"REFUSED — unknown spawn flag {key!r}. The flag surface is REGISTRY-DECLARED "
                f"(the Mirror-Registry derives posture; session_supervisor.SPAWN_FLAG_ASSEMBLY holds "
                f"the consumer-emission data; a new flag is a new row, Atlas-grounded). "
                f"Declared: {sorted(SPAWN_FLAG_ASSEMBLY)}.")
        flag = spec["flag"]
        posture = _registry_posture(flag)          # DERIVED — the registry is the sole truth (F-FIX-5)
        if posture in ("locked", "hazard"):
            raise TeachingRefusal(f"REFUSED — spawn flag {key!r} is LOCKED: {spec['teach']}")
        if posture == "consent" and not consent:
            raise TeachingRefusal(
                f"REFUSED — spawn flag {key!r} ({spec['teach']}) WIDENS the session's surface and "
                f"rides the operator-consent beat. Spawn it via POST /bridge-session with "
                f"operator_consent=true (consent-not-lockdown — available the moment consent rides "
                f"the call; git revert backstops).")
        kind = spec["kind"]
        if kind == "bool":
            if val:
                cmd.append(flag)
        elif kind == "value":
            if val is not None and str(val) != "":
                cmd += [flag, str(val)]
        elif kind == "csv":
            s = val if isinstance(val, str) else ",".join(str(x) for x in (val or []))
            if s:
                cmd += [flag, s]
        elif kind == "repeat":
            items = [val] if isinstance(val, str) else list(val or [])
            for it in items:
                if it:
                    cmd += [flag, str(it)]
        elif kind == "swap":
            if val is None or str(val) == "":
                continue
            if flag in cmd:
                cmd[cmd.index(flag) + 1] = str(val)
            else:
                cmd += [flag, str(val)]
    return cmd


class Supervised:
    """One owned claude subprocess + its supervisor-side state. The state machine is
    starting → idle ⇄ busy → closed (truthful transitions — F1.2's bar; `closed` is terminal)."""

    def __init__(self, *, name: str | None, cwd: str, resume: str | None, fork: bool, source: str):
        self.id = "as-" + uuid.uuid4().hex[:8]      # local handle until init names the claude session id
        self.claude_session_id: str | None = resume if (resume and not fork) else None
        self.name = name or self.id
        self.cwd = cwd
        self.resume = resume
        self.fork = fork
        self.source = source
        self.profile = "default"      # "default" = mcp__company-only floor; "bridge-session" = R1-prime wider posture
        self.state = "starting"
        self.created = time.time()
        self.created_iso = _now()
        self.last_activity = time.time()
        self.turn_started: float | None = None
        self.turn_source: str | None = None
        self.turn_intent: dict | None = None        # the mailbox intent this turn answers (for the reply)
        self.turn_text: list[str] = []              # assistant text of the in-flight turn (reply body)
        self.stderr_tail: list[str] = []            # last ~50 stderr lines (drained for life; close diagnostic)
        self.turns = 0
        self.proc: subprocess.Popen | None = None
        self.stdin_lock = threading.Lock()
        self.events: deque = deque(maxlen=500)
        self.subscribers: list = []                 # queue.Queue per /watch client
        self.ev_seq = 0
        self.close_reason: str | None = None

    def record(self) -> dict:
        return {
            "id": self.id, "claude_session_id": self.claude_session_id, "name": self.name,
            "cwd": self.cwd, "state": self.state, "resume": self.resume, "fork": self.fork,
            "created": self.created_iso, "last_activity": datetime.fromtimestamp(
                self.last_activity, timezone.utc).isoformat(),
            "turns": self.turns, "pid": self.proc.pid if self.proc else None,
            "close_reason": self.close_reason, "profile": self.profile,
        }

    def matches(self, key: str) -> bool:
        return key in (self.id, self.claude_session_id)


def _extract_usage(ev: dict) -> dict | None:
    """CC-20 (cost/usage capture): the claude `result` event carries cost + token usage that the
    supervisor previously DISCARDED. Pull the standard fields off the result event into a flat
    `usage` block stamped onto the durable agent_sessions.turn (read over [[events]] — zero new
    transport). Grounded in the Claude Code Atlas (Docs/claude-code/agent-sdk/cost-tracking.md +
    .../typescript.md#modelusage + .../python.md ResultMessage): BOTH success and error result
    messages carry `usage` (snake_case token fields) and `total_cost_usd`; `modelUsage`/`model_usage`
    is the per-model camelCase passthrough carrying per-model costUSD/contextWindow. costUSD is a
    CLIENT-SIDE ESTIMATE, never the authoritative bill (cost-usage.md Errors). Returns None when the
    event carries no usage AND no cost AND no model_usage — so a turn with nothing to report stamps
    no empty noise. NO live spawn needed: verifiable by reading a turn record's event (the stub's
    result event can carry these fields)."""
    usage = ev.get("usage") if isinstance(ev.get("usage"), dict) else None
    model_usage = ev.get("modelUsage")
    if not isinstance(model_usage, dict):
        model_usage = ev.get("model_usage") if isinstance(ev.get("model_usage"), dict) else None
    cost = ev.get("total_cost_usd")
    if cost is None:
        cost = ev.get("cost_usd")        # tolerate the alternate spelling some result shapes use
    if usage is None and model_usage is None and cost is None:
        return None
    out: dict = {}
    # the model that ran the turn (result events carry it on some shapes; honest-absent otherwise)
    model = ev.get("model")
    if model is None and isinstance(model_usage, dict) and model_usage:
        model = next(iter(model_usage))  # the single model key, the common case
    if model is not None:
        out["model"] = model
    if isinstance(usage, dict):
        # snake_case token fields per the result-message ResultMessage shape (Atlas python.md)
        for k in ("input_tokens", "output_tokens",
                  "cache_read_input_tokens", "cache_creation_input_tokens"):
            if usage.get(k) is not None:
                out[k] = usage[k]
    if cost is not None:
        out["cost_usd"] = cost
    if isinstance(model_usage, dict) and model_usage:
        out["model_usage"] = model_usage   # per-model camelCase passthrough (costUSD/contextWindow/…)
    return out or None


class SessionSupervisor:
    """Owns the fleet. All mutations to the fleet dict happen under self.lock; per-session
    stdin writes under the session's stdin_lock; events.jsonl writes ride FsStore's own lock
    (single process → the in-process seq lock is sufficient, by construction)."""

    def __init__(self, store: FsStore):
        self.store = store
        self.sessions: dict[str, Supervised] = {}
        self.lock = threading.RLock()
        self.mail_path = store.root / MAIL_LEAF / "mail.jsonl"
        self._stop = threading.Event()

    # ---------- events (single writer — agent_sessions.* originate ONLY here) ----------

    def emit(self, kind: str, summary: str, *, durable: bool, **meta) -> None:
        """`durable=True` = a claim whose loss changes behavior (spawned/turn/closed): the
        failure is printed LOUDLY and RE-RAISED (the _emit_durable posture — never swallow a
        claim write). Callers that must outlive a bad write (the watchdog loop — killing it
        over one write would silently unguard every other session) wrap their call sites.
        `durable=False` = narration (idle): logged-and-continue, the _emit posture."""
        try:
            self.store.append_event({"kind": kind, "summary": summary, **meta})
        except Exception as e:
            print(f"[session-supervisor] EVENT WRITE FAILED kind={kind}: {e}", file=sys.stderr, flush=True)
            if durable:
                raise

    # ---------- fan ----------

    def _fan(self, s: Supervised, ev: dict) -> None:
        s.ev_seq += 1
        ev = {"seq": s.ev_seq, "ts": _now(), "session": s.id, **ev}
        s.events.append(ev)
        for q in list(s.subscribers):
            try:
                q.put_nowait(ev)
            except Exception:
                pass

    # ---------- spawn ----------

    def _live(self) -> list[Supervised]:
        return [s for s in self.sessions.values() if s.state != "closed"]

    def _cap_check(self, adding: int) -> None:
        cap = fabric_concurrency()
        live = self._live()
        if len(live) + adding > cap:
            names = ", ".join(f"{s.name}({s.state})" for s in live) or "none"
            raise TeachingRefusal(
                f"REFUSED — this would put {len(live) + adding} sessions live, over the cap of {cap} "
                f"(COMPANY_FABRIC_CONCURRENCY, call-time env). Live now: {names}. "
                f"Free a slot first (POST /teardown {{\"session\": \"<id>\"}}) or raise the cap "
                f"deliberately by restarting the service with COMPANY_FABRIC_CONCURRENCY=<n>. "
                f"CONSULT fans count against the same cap (copies ≤ cap).")

    @staticmethod
    def _build_spawn_cmd(*, claude_bin: str, resume: str | None, fork: bool,
                         model: str | None = None, effort: str | None = None,
                         fallback: "list[str] | str | None" = None,
                         permission_mode: str | None = None,
                         settings: str | None = None,
                         add_dir: "list[str] | str | None" = None,
                         output_format: str | None = None,
                         include_partial: bool = False,
                         debug: "str | bool | None" = None,
                         safe_mode: bool = False, bare: bool = False) -> list[str]:
        """The PURE claude-command builder (FAMILY 2: CC-10/07.2/25.2/.3/18.7/33.4). Every new param
        is OPTIONAL and defaults to today's behaviour, so the built cmd is BYTE-IDENTICAL to the old
        inline construction when none is passed (the unit test asserts exactly this). Unit-testable
        WITHOUT spawning a real claude — assert on the returned list (lead-only law: this lane never
        fires a real turn). Every flag is grounded in the Claude Code Atlas cli-reference (verified
        2026-06-12 via knowledge-corpus, vault claude-code-atlas), NEVER invented:
          --model (alias|name) · --effort low|medium|high|xhigh|max · --fallback-model <csv>  [CC-10]
          --permission-mode <mode> overriding the fabric-wide fabric_permission()              [CC-07.2]
          --settings <json|path> · --add-dir <d> (repeatable)                                  [CC-25.2/.3]
          --output-format <fmt> (default stream-json) · --include-partial-messages             [CC-18.7]
          --debug [categories] · --safe-mode · --bare                                          [CC-33.4]
        The held-open transport invariants are PRESERVED: --input-format stream-json is fixed (the
        T2 injection contract depends on it), --output-format defaults to stream-json (the reader
        parses that shape), and --include-partial-messages / --debug-as-stream all require the
        stream-json output the supervisor already runs under (Atlas: --include-partial-messages
        requires --print + --output-format stream-json — both present)."""
        # transport-fixed head: --input-format stream-json is NON-negotiable (the injection contract).
        out_fmt = output_format or "stream-json"   # default preserves the reader's parse contract
        cmd = [claude_bin, "-p",
               "--input-format", "stream-json", "--output-format", out_fmt, "--verbose",
               "--permission-mode", permission_mode or fabric_permission(),
               "--mcp-config", _panel._MCP_CONFIG, "--strict-mcp-config",
               "--allowedTools", "mcp__company"]
        if model:
            cmd += ["--model", model]
        if effort:
            cmd += ["--effort", effort]
        if fallback:
            # Atlas: --fallback-model accepts a comma-separated list tried in order.
            fb = fallback if isinstance(fallback, str) else ",".join(str(x) for x in fallback)
            if fb:
                cmd += ["--fallback-model", fb]
        if settings:
            cmd += ["--settings", settings]   # path OR inline JSON string (Atlas cli-reference)
        if add_dir:
            dirs = [add_dir] if isinstance(add_dir, str) else list(add_dir)
            for d in dirs:
                if d:
                    cmd += ["--add-dir", str(d)]   # repeatable: one flag per dir
        if include_partial:
            cmd += ["--include-partial-messages"]   # requires --output-format stream-json (held above)
        if debug:
            # --debug takes OPTIONAL category filtering (e.g. "api,hooks"); bare True = enable, no filter
            if isinstance(debug, str) and debug.strip():
                cmd += ["--debug", debug]
            else:
                cmd += ["--debug"]
        if safe_mode:
            cmd += ["--safe-mode"]
        if bare:
            cmd += ["--bare"]
        if resume:
            cmd += ["--resume", resume]
        if fork:
            cmd += ["--fork-session"]
        return cmd

    @staticmethod
    def _resolve_bridge_tools(capabilities: "list[str] | str | None",
                              extra_tools: "list[str] | str | None") -> "tuple[list[str], list[str]]":
        """Resolve a bridge-session's requested CAPABILITIES (git/lsp/web/edit) + any explicit
        extra_tools into the concrete `--allowedTools` list, REFUSING LOUD on host/rail-boundary
        capabilities (computer/browser). Pure + unit-testable (no spawn). Returns (tools, refusals):
        `refusals` is the list of teaching reasons for any unavailable capability the caller named —
        the caller (spawn_bridge_session) turns a non-empty refusals list into a TeachingRefusal so the
        boundary is EXPLICIT, never an allowlist entry that silently never binds (§5.4 honesty)."""
        refusals: list[str] = []
        if capabilities is None:
            caps: list[str] = []
        elif isinstance(capabilities, str):
            caps = [c.strip() for c in capabilities.replace(",", " ").split() if c.strip()]
        else:
            caps = [str(c).strip() for c in capabilities if str(c).strip()]
        # start from the default wider set (every bridge-session is at least git+lsp+web+edit capable —
        # the profile's whole purpose); naming caps NARROWS only when the caller asks for a subset.
        if caps:
            tools: list[str] = ["mcp__company"]
            for c in caps:
                if c in BRIDGE_SESSION_UNAVAILABLE:
                    refusals.append(f"capability '{c}': {BRIDGE_SESSION_UNAVAILABLE[c]}")
                    continue
                grant = BRIDGE_SESSION_CAPABILITIES.get(c)
                if grant is None:
                    refusals.append(
                        f"capability '{c}' is unknown — bridge-session capabilities are "
                        f"{sorted(BRIDGE_SESSION_CAPABILITIES)} (grantable on this -p/Linux rail) and "
                        f"{sorted(BRIDGE_SESSION_UNAVAILABLE)} (host/rail boundaries, refused-loud).")
                    continue
                for t in grant:
                    if t not in tools:
                        tools.append(t)
        else:
            tools = list(BRIDGE_SESSION_TOOLS)
        # explicit extra tool NAMES (Atlas specifier strings) the caller appends verbatim — but a
        # `computer`/`Computer`/`browser` specifier is STILL refused (the boundary holds regardless of
        # how it is asked for; never let it slip in as a raw tool string).
        if extra_tools:
            extras = ([extra_tools] if isinstance(extra_tools, str) else list(extra_tools))
            for t in extras:
                t = str(t).strip()
                if not t:
                    continue
                low = t.split("(")[0].strip().lower()
                if low in BRIDGE_SESSION_UNAVAILABLE:
                    refusals.append(f"tool '{t}': {BRIDGE_SESSION_UNAVAILABLE[low]}")
                    continue
                if t not in tools:
                    tools.append(t)
        return tools, refusals

    @classmethod
    def _build_bridge_session_cmd(cls, *, claude_bin: str, resume: str | None = None,
                                  fork: bool = False,
                                  capabilities: "list[str] | str | None" = None,
                                  extra_tools: "list[str] | str | None" = None,
                                  permission_mode: str | None = None,
                                  model: str | None = None, effort: str | None = None,
                                  fallback: "list[str] | str | None" = None,
                                  settings: str | None = None,
                                  add_dir: "list[str] | str | None" = None) -> list[str]:
        """The PURE bridge-session (R1-prime) command builder. Identical transport head to
        _build_spawn_cmd (held-open `--input-format stream-json` + stream-json output — the T2
        injection contract), but the `--allowedTools` is the WIDER profile set (NOT `mcp__company`
        only) and the permission posture defaults to BRIDGE_SESSION_PERMISSION (acceptEdits) so
        in-session writes are possible (a `plan` posture would defeat the profile). Unit-testable
        WITHOUT spawning a real claude (the lead-only law: assert on the returned list). RAISES
        TeachingRefusal if a host/rail-boundary capability (computer/browser) is requested — the
        boundary is loud, never an allowlist entry that never binds.

        This delegates the non-tool/non-permission flags to _build_spawn_cmd, then SWAPS the
        `--allowedTools` value — one source for the model/effort/settings/add-dir flag shapes."""
        tools, refusals = cls._resolve_bridge_tools(capabilities, extra_tools)
        if refusals:
            raise TeachingRefusal(
                "REFUSED — bridge-session requested a capability this R1-prime rail cannot grant:\n  "
                + "\n  ".join(refusals)
                + "\nDrop it from `capabilities`/`extra_tools`. The grantable set on this headless "
                  "`-p`/Linux rail is git · lsp · web · edit (computer-use and the Chrome browser are "
                  "macOS/interactive-only host boundaries — they cannot bind to a `-p` session and are "
                  "never silently allowed).")
        # build the base cmd with the profile's permission posture, then replace the allowedTools value.
        base = cls._build_spawn_cmd(
            claude_bin=claude_bin, resume=resume, fork=fork,
            model=model, effort=effort, fallback=fallback,
            permission_mode=permission_mode or BRIDGE_SESSION_PERMISSION,
            settings=settings, add_dir=add_dir)
        # _build_spawn_cmd emits `--allowedTools mcp__company` as a fixed pair; swap that single value
        # for the wider comma-joined profile set (Atlas: --allowedTools is one comma-separated value).
        i = base.index("--allowedTools")
        base[i + 1] = ",".join(tools)
        return base

    def spawn(self, *, cwd: str | None = None, resume: str | None = None, fork: bool = False,
              name: str | None = None, source: str = "http", wait_init: bool = True,
              model: str | None = None, effort: str | None = None,
              fallback: "list[str] | str | None" = None, permission_mode: str | None = None,
              settings: str | None = None, add_dir: "list[str] | str | None" = None,
              output_format: str | None = None, include_partial: bool = False,
              debug: "str | bool | None" = None, safe_mode: bool = False,
              bare: bool = False, flags: dict | None = None) -> Supervised:
        # R1.3: registry-declared flags VALIDATE BEFORE the session registers (no half-built record);
        # a plain spawn carries NO consent — consent-posture rows refuse loud here, teaching the
        # bridge-session path.
        if flags:
            _apply_spawn_flags([], flags, consent=False)        # validate-only pass (refuse pre-record)
        # the fork-requires-resume guard stays BEFORE we register the session (no half-built record)
        if fork and not resume:
            raise TeachingRefusal("REFUSED — fork=true requires resume=<session id>: a CONSULT is "
                                  "a fork OF an existing session (--resume <id> --fork-session). "
                                  "For a fresh session, spawn without fork.")
        with self.lock:
            self._cap_check(1)
            s = Supervised(name=name, cwd=cwd or REPO_ROOT, resume=resume, fork=fork, source=source)
            self.sessions[s.id] = s
        claude_bin = _panel._find_claude()           # call-time (env-overridable — the stub harness path)
        cmd = self._build_spawn_cmd(
            claude_bin=claude_bin, resume=resume, fork=fork,
            model=model, effort=effort, fallback=fallback, permission_mode=permission_mode,
            settings=settings, add_dir=add_dir, output_format=output_format,
            include_partial=include_partial, debug=debug, safe_mode=safe_mode, bare=bare)
        _apply_spawn_flags(cmd, flags, consent=False)   # R1.3 — the registry-declared remainder
        # SELF-ID INJECTION (fork's patch 21bcd77, pairs with resolve_own_session safe-consumer c66f392):
        # a RESUME (non-fork) spawn continues under the resumed sid, so that sid IS the child's own session
        # id → inject COMPANY_SESSION_ID so the child's resolve_own_session("self") resolves UNAMBIGUOUSLY
        # instead of failing-loud on a multi-transcript project dir. fork/fresh spawns mint a NEW id unknown
        # here (claude-assigned at launch) → left to the SessionStart hook; NEVER inject a wrong id (a
        # confident wrong-self is worse than a loud no-self). dict(os.environ) is byte-identical to inherit
        # for every non-resume-non-fork spawn — only a resume-clone gains the one var. [self-serve memory]
        child_env = dict(os.environ)
        if resume and not fork:
            child_env["COMPANY_SESSION_ID"] = resume
        s.proc = subprocess.Popen(cmd, cwd=s.cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, bufsize=1, env=child_env)
        threading.Thread(target=self._reader, args=(s,), daemon=True,
                         name=f"reader-{s.id}").start()
        # DRAIN stderr for the LIFE of the process. The OS pipe buffer (~64KB) MUST be emptied or a
        # chatty child blocks writing to it and dies — observed as rc=1 on RESUME spawns only: a
        # resume fires the SessionStart:resume hook AND replays the full conversation, overflowing
        # what a fresh spawn never reaches (a fresh session's thin stderr masked this in the lane's
        # stub-binary acceptance test, which never resumed a real claude). The drain IS the fix; the
        # retained tail is kept only for the close diagnostic.
        threading.Thread(target=self._drain_stderr, args=(s,), daemon=True,
                         name=f"stderr-{s.id}").start()
        self.emit("agent_sessions.spawned",
                  f"{s.name} · {'fork of ' + resume if fork else ('resume ' + resume if resume else 'new')}",
                  durable=True, session=s.id, name=s.name, cwd=s.cwd, resume=resume, fork=fork,
                  source=source, pid=s.proc.pid)
        if wait_init:
            # ROOT-CAUSE (lead-proven 2026-06-14): a real claude under --input-format stream-json
            # emits `system/init` only AFTER its first injected message — the SessionStart hooks
            # fire at spawn, but init waits for stdin input. Blocking for init here deadlocked the
            # spawn -> wait-for-idle -> inject pattern (the session sat in 'starting' forever; the
            # R1 live-probe hang). Readiness = "the process didn't instant-crash on bad flags":
            # after a brief settle a still-alive process IS ready to receive its first turn, so
            # promote 'starting' -> 'idle'. init then arrives on that first turn and the reader
            # captures claude_session_id (~L965). A stub that prints init eagerly flips to idle
            # inside the settle (the reader sets it), so the stub acceptance path is unchanged.
            deadline = time.time() + min(INIT_WAIT_S, SPAWN_SETTLE_S)
            while time.time() < deadline and s.state == "starting" and s.proc.poll() is None:
                time.sleep(0.05)
            if s.state == "starting" and s.proc.poll() is None:
                s.state = "idle"   # live stream-json process = ready for its first turn
        return s

    # ---------- RAIL R1-prime: the consent-gated bridge-session spawn ----------

    def spawn_bridge_session(self, *, operator_consent: bool = False,
                             capabilities: "list[str] | str | None" = None,
                             extra_tools: "list[str] | str | None" = None,
                             cwd: str | None = None, resume: str | None = None,
                             fork: bool = False, name: str | None = None,
                             source: str = "bridge-session", wait_init: bool = True,
                             permission_mode: str | None = None,
                             model: str | None = None, effort: str | None = None,
                             fallback: "list[str] | str | None" = None,
                             settings: str | None = None,
                             add_dir: "list[str] | str | None" = None,
                             prompt: str | None = None,
                             flags: dict | None = None) -> Supervised:
        """Spawn a session under the R1-prime PROFILE: a supervised `claude -p` with a WIDER
        `--allowedTools` (Bash/git/LSP-family/web + mcp__company) and an in-session write posture
        (acceptEdits by default), cwd defaulting to the repo root — the posture ④'s in-session
        git/LSP/web ops need (the floor `mcp__company`-only spawn cannot carry them).

        THE CONSENT GATE (sole-operator security model — consent-not-lockdown): the profile is ALWAYS
        AVAILABLE; a wider spawn is REFUSED-LOUD unless `operator_consent=True` rides the call. This is
        a CONSENT BEAT, not a lockout — the trusted operator can always consent (the /api/resolve
        operator-vantage precedent), an AGENT cannot open the wider surface without the signal, and
        `git revert` is the irreversibility backstop. The gate is a marker, never an auth wall.

        RESULT SHAPE (arch doc's correction): a bridge-session's work rides back as PROSE on the turn
        (turn_text → the mailbox reply / the watch stream) — `liveness: stream`, NO typed return_shape.
        The supervisor does not synthesize a structured git-sha/LSP-symbol object; the corpus entries
        for these ④ ops are contracted `liveness: stream` with no return_shape (honest — the prose IS
        the carrier). git's STRUCTURED-sha path is a DIFFERENT rail (R3 plain-`git` argv), not this one.

        LEAD-ONLY / live-verify pending: this method spawns a REAL claude when called by the running
        service. The cmd-BUILDER (_build_bridge_session_cmd) is unit-tested without spawning; the live
        round-trip (a real wider session committing via Bash-git, an LSP nav returning prose) is the
        build lead's to verify — NEVER claimed live here, NEVER green-painted."""
        if not operator_consent:
            raise TeachingRefusal(
                "REFUSED — a bridge-session opens a WIDER tool surface (Bash/git/LSP/web + file writes) "
                "than the fabric floor (mcp__company-only). This rail is consent-gated, not locked: pass "
                "operator_consent=true (the operator-vantage consent beat — the same gate /api/resolve "
                "uses) to open it. The capability is available the moment consent rides the call; without "
                "it an agent cannot widen the surface. `git revert` backstops anything irreversible.")
        # resolve+validate the wider toolset BEFORE registering a session (no half-built record, the
        # spawn() guard pattern). A host/rail-boundary capability (computer/browser) refuses here, loud.
        claude_bin = _panel._find_claude()
        cmd = self._build_bridge_session_cmd(
            claude_bin=claude_bin, resume=resume, fork=fork,
            capabilities=capabilities, extra_tools=extra_tools,
            permission_mode=permission_mode, model=model, effort=effort,
            fallback=fallback, settings=settings, add_dir=add_dir)
        # R1.3: the registry-declared remainder — the consent beat already rode this call, so
        # consent-posture rows (tools/allowed_tools/mcp_config/plugins/…) are appliable here.
        _apply_spawn_flags(cmd, flags, consent=True)
        if fork and not resume:
            raise TeachingRefusal("REFUSED — fork=true requires resume=<session id> (a fork is OF an "
                                  "existing session). For a fresh bridge-session, spawn without fork.")
        with self.lock:
            self._cap_check(1)
            s = Supervised(name=name or "bridge-session", cwd=cwd or REPO_ROOT,
                           resume=resume, fork=fork, source=source)
            s.profile = "bridge-session"                       # marks the wider posture on the record
            self.sessions[s.id] = s
        s.proc = subprocess.Popen(cmd, cwd=s.cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, bufsize=1)
        threading.Thread(target=self._reader, args=(s,), daemon=True,
                         name=f"reader-{s.id}").start()
        threading.Thread(target=self._drain_stderr, args=(s,), daemon=True,
                         name=f"stderr-{s.id}").start()
        # the spawn event records the PROFILE + consent so the run-record carries the security decision
        # (Introspective-Data-Building / §5.6: every R1-prime act writes who+consent+args — the misuse/
        # refusal signal is gap-pressure). The allowlist is recorded so an audit can see the surface.
        i = cmd.index("--allowedTools")
        self.emit("agent_sessions.spawned",
                  f"{s.name} · R1-prime bridge-session "
                  f"({'fork of ' + resume if fork else ('resume ' + resume if resume else 'new')})",
                  durable=True, session=s.id, name=s.name, cwd=s.cwd, resume=resume, fork=fork,
                  source=source, pid=s.proc.pid, profile="bridge-session", operator_consent=True,
                  allowed_tools=cmd[i + 1])
        if prompt:
            self.inject(s, str(prompt), source=source)
        if wait_init:
            # ROOT-CAUSE (lead-proven 2026-06-14): a real claude under --input-format stream-json
            # emits `system/init` only AFTER its first injected message — the SessionStart hooks
            # fire at spawn, but init waits for stdin input. Blocking for init here deadlocked the
            # spawn -> wait-for-idle -> inject pattern (the session sat in 'starting' forever; the
            # R1 live-probe hang). Readiness = "the process didn't instant-crash on bad flags":
            # after a brief settle a still-alive process IS ready to receive its first turn, so
            # promote 'starting' -> 'idle'. init then arrives on that first turn and the reader
            # captures claude_session_id (~L965). A stub that prints init eagerly flips to idle
            # inside the settle (the reader sets it), so the stub acceptance path is unchanged.
            deadline = time.time() + min(INIT_WAIT_S, SPAWN_SETTLE_S)
            while time.time() < deadline and s.state == "starting" and s.proc.poll() is None:
                time.sleep(0.05)
            if s.state == "starting" and s.proc.poll() is None:
                s.state = "idle"   # live stream-json process = ready for its first turn
        return s

    # ---------- the per-session stderr drain (the rc=1-on-resume fix) ----------

    def _drain_stderr(self, s: Supervised) -> None:
        """Empty the child's stderr pipe for the life of the process so it can never block on a full
        buffer. Keeps only the last 50 lines for the close diagnostic — the point is the DRAIN, not
        capture."""
        try:
            for line in s.proc.stderr:
                s.stderr_tail.append(line.rstrip("\n"))
                if len(s.stderr_tail) > 50:
                    del s.stderr_tail[0]
        except Exception:
            pass

    # ---------- the per-session stdout reader ----------

    def _declare_and_fan(self, s: Supervised, ev: dict) -> None:
        """R1.2 — fan the DECLARED form of every claude emit alongside the legacy condensed
        events (schema-additive: existing /watch consumers see exactly what they saw; a UI
        consumes the `declared` events and renders from the declaration alone). The declarer
        NEVER raises on unknown content (unknown → loud UnknownEvent + a drop) — a failure
        here is a registry/code bug, printed loud, and must not kill the reader thread."""
        try:
            dec = _rd.declare(ev)
        except Exception as e:
            print(f"[session-supervisor] DECLARE FAILED for {s.id} type={ev.get('type')}: {e}",
                  file=sys.stderr, flush=True)
            return
        self._fan(s, {"type": "declared", **dec})
        if dec.get("undeclared") or dec.get("family_fallback"):
            # the registry-gap sensor (gap-pressure): a drop is RECORDED, never swallowed.
            self.emit("agent_sessions.render_drop",
                      f"{s.name} · {'undeclared' if dec.get('undeclared') else 'family-fallback'} "
                      f"emit {dec.get('render_key')}",
                      durable=False, session=s.id, render_key=dec.get("render_key"),
                      raw_type=ev.get("type"), raw_subtype=ev.get("subtype"))

    def _reader(self, s: Supervised) -> None:
        """Parses the claude stream (the run_turn event shapes) for the LIFE of the process —
        not one turn. EOF = the process ended → closed."""
        try:
            for line in s.proc.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue                          # non-JSON chatter — the result event is the contract
                self._declare_and_fan(s, ev)          # R1.2: EVERY emit declared, nothing silently dropped
                et = ev.get("type")
                if et == "system" and ev.get("subtype") == "init":
                    first = s.claude_session_id is None
                    s.claude_session_id = ev.get("session_id") or s.claude_session_id
                    if s.state == "starting":
                        s.state = "idle"
                    s.last_activity = time.time()
                    self._fan(s, {"type": "init", "claude_session_id": s.claude_session_id})
                    # Persist the claude_session_id ↔ cwd link on first init (durable): the registry
                    # fold's canonical-id mapping wants it, AND wake/consult resolve a target's cwd
                    # from it — a session born in dir X must RESUME in dir X (claude --resume scopes
                    # to the cwd's project dir; wrong cwd = "No conversation found"). Cross-directory
                    # is the fabric's whole point (F1 cross-cwd gap, found in lead live-verification).
                    if first and s.claude_session_id:
                        self.emit("agent_sessions.registered",
                                  f"{s.name} · {s.claude_session_id[:8]} @ {s.cwd}",
                                  durable=True, session=s.id,
                                  claude_session_id=s.claude_session_id, cwd=s.cwd, name=s.name)
                elif et == "assistant":
                    for block in (ev.get("message") or {}).get("content") or []:
                        if block.get("type") == "text" and block.get("text"):
                            s.turn_text.append(block["text"])
                            self._fan(s, {"type": "text", "text": block["text"]})
                        elif block.get("type") == "tool_use":
                            inp = block.get("input") or {}
                            detail = (inp.get("file_path") or inp.get("path") or inp.get("pattern")
                                      or inp.get("command") or inp.get("description") or "")
                            self._fan(s, {"type": "tool", "name": block.get("name", "?"),
                                          "detail": str(detail)[:160]})
                elif et == "result":
                    self._turn_done(s, ev)
        except Exception as e:
            print(f"[session-supervisor] reader {s.id} died: {e}", file=sys.stderr, flush=True)
        finally:
            rc = s.proc.poll()
            if s.state != "closed":
                try:
                    # Non-zero exits carry the drained stderr tail so the cause is never a mystery
                    # (the rc=1 hunt is exactly why this is here — fail loud WITH evidence).
                    tail = (" :: " + " | ".join(s.stderr_tail[-5:])) if (rc and s.stderr_tail) else ""
                    self._close(s, reason=f"exited rc={rc}{tail}", kill=False)
                except Exception as e:
                    print(f"[session-supervisor] close event write failed for {s.id}: {e}",
                          file=sys.stderr, flush=True)

    def _turn_done(self, s: Supervised, ev: dict) -> None:
        dur_ms = int((time.time() - s.turn_started) * 1000) if s.turn_started else None
        result_text = (ev.get("result") or "") or "\n".join(s.turn_text)
        s.turns += 1
        s.state = "idle"
        s.last_activity = time.time()
        intent = s.turn_intent
        s.turn_started, s.turn_intent = None, None
        s.turn_text = []
        self._fan(s, {"type": "done", "result": result_text[:4000],
                      "claude_session_id": ev.get("session_id") or s.claude_session_id,
                      "num_turns": ev.get("num_turns"), "is_error": bool(ev.get("is_error"))})
        # DELIVER ack/reply is a CLAIM (durable class): the turn event + the mailbox reply.
        usage = _extract_usage(ev)   # CC-20: capture the result event's cost+token usage (was discarded)
        turn_meta = dict(session=s.id, claude_session_id=s.claude_session_id,
                         name=s.name, duration_ms=dur_ms, is_error=bool(ev.get("is_error")),
                         source=s.turn_source, intent_id=(intent or {}).get("id"))
        if usage is not None:
            turn_meta["usage"] = usage   # {model?, input/output/cache tokens, cost_usd?, model_usage?}
        self.emit("agent_sessions.turn", f"{s.name} · turn {s.turns} done",
                  durable=True, **turn_meta)
        if intent:
            self._mail_reply(s, intent, result_text, is_error=bool(ev.get("is_error")))
        self.emit("agent_sessions.idle", f"{s.name} idle", durable=False,
                  session=s.id, claude_session_id=s.claude_session_id, name=s.name)

    # ---------- inject / interrupt / teardown ----------

    def find(self, key: str) -> Supervised | None:
        with self.lock:
            for s in self.sessions.values():
                if s.matches(key):
                    return s
        return None

    def inject(self, s: Supervised, message: str, *, source: str = "http",
               intent: dict | None = None) -> None:
        if s.state == "closed":
            raise TeachingRefusal(f"REFUSED — session {s.id} ({s.name}) is closed "
                                  f"({s.close_reason}). WAKE it instead: spawn with "
                                  f"resume=\"{s.claude_session_id or s.id}\".")
        if s.state == "busy":
            raise TeachingRefusal(f"REFUSED — session {s.id} ({s.name}) is mid-turn. Wait for idle "
                                  f"(GET /sessions), POST /interrupt to stop the turn, or queue via "
                                  f"the mailbox (the supervisor retries deliver intents until idle).")
        line = json.dumps({"type": "user",
                           "message": {"role": "user",
                                       "content": [{"type": "text", "text": message}]}})
        with s.stdin_lock:
            s.state = "busy"
            s.turn_started = time.time()
            s.turn_source = source
            s.turn_intent = intent
            s.turn_text = []
            try:
                s.proc.stdin.write(line + "\n")
                s.proc.stdin.flush()
            except Exception as e:
                s.state = "closed"
                s.close_reason = f"stdin write failed: {e}"
                raise
        self._fan(s, {"type": "injected", "source": source, "chars": len(message)})

    def interrupt(self, s: Supervised) -> None:
        """Write a control_request interrupt onto the same stdin stream (the SDK transport's
        control wrapper shape — {type: control_request, request_id, request:{subtype: interrupt}}).
        HONEST STATUS: built-untested against a real claude turn (this lane runs only stub
        subprocesses); the watchdog remains the enforcement backstop either way."""
        if s.state != "busy":
            raise TeachingRefusal(f"REFUSED — session {s.id} ({s.name}) is {s.state}, not mid-turn; "
                                  f"there is nothing to interrupt.")
        line = json.dumps({"type": "control_request", "request_id": uuid.uuid4().hex,
                           "request": {"subtype": "interrupt"}})
        with s.stdin_lock:
            s.proc.stdin.write(line + "\n")
            s.proc.stdin.flush()
        self._fan(s, {"type": "interrupt_sent"})

    def _close(self, s: Supervised, *, reason: str, kill: bool) -> None:
        s.state = "closed"
        s.close_reason = reason
        if kill and s.proc and s.proc.poll() is None:
            try:
                s.proc.stdin.close()
            except Exception:
                pass
            s.proc.terminate()
            try:
                s.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                s.proc.kill()
        self._fan(s, {"type": "closed", "reason": reason})
        self.emit("agent_sessions.closed", f"{s.name} · {reason}", durable=True,
                  session=s.id, claude_session_id=s.claude_session_id, name=s.name, reason=reason)

    def teardown(self, s: Supervised) -> None:
        if s.state == "closed":
            return
        self._close(s, reason="teardown", kill=True)

    def teardown_all(self) -> None:
        with self.lock:
            live = self._live()
        for s in live:
            try:
                self.teardown(s)
            except Exception as e:
                print(f"[session-supervisor] teardown {s.id} failed: {e}", file=sys.stderr, flush=True)

    # ---------- the watchdog (the ENFORCED per-turn wall-clock — audit C3) ----------

    def watchdog_loop(self) -> None:
        while not self._stop.is_set():
            limit = turn_timeout_s()
            now = time.time()
            for s in list(self.sessions.values()):
                try:
                    if s.state == "busy" and s.turn_started and now - s.turn_started > limit:
                        self._close(s, reason=f"watchdog-timeout after {int(now - s.turn_started)}s "
                                              f"(COMPANY_FABRIC_TURN_TIMEOUT_S={int(limit)})", kill=True)
                    elif s.state == "starting" and now - s.created > limit:
                        # the silent-hang spawn: no init ever arrived — same enforcement
                        self._close(s, reason=f"watchdog-timeout: no init after {int(now - s.created)}s",
                                    kill=True)
                except Exception as e:
                    # the reap HAPPENED (kill precedes the event write in _close); a failed event
                    # write is loud, and the watchdog survives to guard the rest of the fleet.
                    print(f"[session-supervisor] watchdog event write failed for {s.id}: {e}",
                          file=sys.stderr, flush=True)
            self._stop.wait(WATCHDOG_POLL_S)

    # ---------- the mailbox consumer (guide §C contract — consume-only here) ----------

    def _cursor(self) -> int:
        v = self.store.head(CURSOR_REF)
        if v is None:
            # First boot: start at the CURRENT end of the leaf — never replay history written
            # before this supervisor existed (stated F1 choice; the importer/backfill is §B's).
            return self.mail_path.stat().st_size if self.mail_path.exists() else 0
        return int(v)

    def _reply_thread(self, intent: dict) -> str:
        """The reply's aggregation key: the intent's own thread (store-minted on every session_post),
        falling back to the intent id for hand-appended intents that bypassed append_agent_mail —
        a consult fan's N replies all join the ONE intent's thread either way."""
        t = intent.get("thread")
        return t if (isinstance(t, str) and t.strip()) else str(intent.get("id") or "")

    def _mail_reply(self, s: Supervised, intent: dict, text: str, *, is_error: bool) -> None:
        """Append the durable reply via the store's OWN mailbox API (the seam the first commit
        flagged, now closed: append_agent_mail stamps cross-process-unique `seq` + defaults `thread`,
        so replies are VISIBLE to sessions(op='inbox') reads and aggregate under the intent's thread
        — the raw no-seq append made them invisible to every seq-cursor read)."""
        cas = self.store.put_content({"text": text, "session": s.claude_session_id or s.id})
        self.store.append_agent_mail({
            "to": intent.get("from"), "from": f"session://{s.claude_session_id or s.id}",
            "verb": "error" if is_error else "reply", "re": intent.get("id"),
            "thread": self._reply_thread(intent), "cas": cas})

    def _mail_error(self, intent: dict, why: str) -> None:
        print(f"[session-supervisor] intent {intent.get('id')} refused: {why}", file=sys.stderr, flush=True)
        cas = self.store.put_content({"text": why})
        self.store.append_agent_mail({
            "to": intent.get("from"), "from": "session://supervisor",
            "verb": "error", "re": intent.get("id"),
            "thread": self._reply_thread(intent), "cas": cas})

    def _intent_body(self, rec: dict) -> str:
        if rec.get("cas"):
            body = self.store.get_content(rec["cas"])
            if isinstance(body, dict):
                return str(body.get("text") or body)
            return str(body)
        if rec.get("message"):
            return str(rec["message"])
        raise ValueError("intent carries neither cas nor message")

    def mailbox_loop(self) -> None:
        offset = self._cursor()
        while not self._stop.is_set():
            try:
                offset = self._mail_pass(offset)
            except Exception as e:
                print(f"[session-supervisor] mailbox pass failed: {e}", file=sys.stderr, flush=True)
            self._stop.wait(MAIL_POLL_S)

    def _mail_pass(self, offset: int) -> int:
        if not self.mail_path.exists():
            return offset
        with self.mail_path.open("r", encoding="utf-8") as f:
            f.seek(offset)
            while True:
                pos = f.tell()
                line = f.readline()
                if not line:
                    break
                if not line.endswith("\n"):
                    break                              # torn tail of a concurrent append — retry next poll
                rec_offset_after = f.tell()
                line = line.strip()
                if not line:
                    offset = rec_offset_after
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    print(f"[session-supervisor] unparseable mail line at {pos} — skipped LOUDLY",
                          file=sys.stderr, flush=True)
                    offset = rec_offset_after
                    continue
                if rec.get("verb") not in ("deliver", "wake", "consult"):
                    offset = rec_offset_after          # replies/acks/foreign verbs — not ours to act on
                    continue
                handled = self._handle_intent(rec)
                if not handled:
                    break                              # head-of-line hold (target busy) — cursor stays put
                offset = rec_offset_after
                self.store.set_ref(CURSOR_REF, str(offset))
        return offset

    def _resume_safe_cwd(self, target: str, rec: dict) -> str | None:
        """Plain wake/consult cwd, VALIDATED: per-event cwd drifts as a session cd's around
        (measured: record says /home/tim/vllm-tests, project dir encodes /home/tim), and a
        --resume in the wrong cwd = 'No conversation found'. Where the registry record carries the
        transcript path, validate candidates by re-encoding (resume_cwd_for — the same guard the
        at-launch path already uses, ledger flagged-adoption 2026-06-13); only a record-less target
        falls back to the unvalidated _cwd_for chain."""
        src_rec = self.store.load_agent_session(target)
        jp = (src_rec or {}).get("jsonl_path")
        if isinstance(jp, str) and jp:
            from runtime.session_pointintime import PointError, resume_cwd_for
            try:
                return resume_cwd_for(jp, rec.get("cwd"), (src_rec or {}).get("cwd"),
                                      self._cwd_for(target, rec))
            except PointError:
                pass                                   # fall through — teaching happens at spawn failure
        return self._cwd_for(target, rec)

    def _cwd_for(self, target: str, rec: dict) -> str | None:
        """The directory a wake/consult must resume in. A claude session is scoped to the project
        dir of the cwd it was born in; resuming elsewhere → 'No conversation found'. Resolution
        order: an explicit cwd on the intent (the sender's registry hint) → the durable
        agent_sessions.registered event for this claude_session_id → a live record → None (spawn
        falls back to REPO_ROOT, which only works for sessions born here). Newest event wins."""
        hint = rec.get("cwd")
        if isinstance(hint, str) and hint.strip():
            return hint
        found = None
        try:
            for ev in self.store.events_since(-1):     # oldest→newest; last match wins
                if (ev.get("kind") == "agent_sessions.registered"
                        and ev.get("claude_session_id") == target and ev.get("cwd")):
                    found = ev["cwd"]
        except Exception as e:
            print(f"[session-supervisor] cwd lookup for {target[:8]} failed: {e}",
                  file=sys.stderr, flush=True)
        if found:
            return found
        live = self.find(target)
        return live.cwd if live else None

    def _handle_intent(self, rec: dict) -> bool:
        """True = consumed (acted or terminally refused-loud); False = hold the cursor and retry
        (the one non-terminal case: deliver to a session that is mid-turn)."""
        target = (rec.get("to") or "").removeprefix("session://")
        verb = rec.get("verb")
        frm = rec.get("from")
        if not (isinstance(frm, str) and frm.strip()):
            # No reply path: neither the answer nor a refusal is mailable (append_agent_mail
            # refuses a from-less record by the store's own law). Consume it LOUDLY — holding
            # the cursor here would deadlock the whole mailbox behind one unroutable line.
            print(f"[session-supervisor] intent {rec.get('id')} has no `from` — unroutable, "
                  f"consumed without action (the reply path is mandatory)", file=sys.stderr, flush=True)
            return True
        try:
            body = self._intent_body(rec)
        except Exception as e:
            self._mail_error(rec, f"unreadable intent body: {e}")
            return True
        try:
            at = str(rec.get("at") or "").strip()
            if at:
                # POINT-IN-TIME LAUNCH (Session Fabric R3.4): wake/consult the target AS IT WAS at
                # a chosen moment. The target session itself is NEVER opened for writing, whatever
                # its liveness — a NEW session file is materialized (the native-fork transform on
                # the transcript's prefix at the point) and THAT copy is launched via the existing
                # spawn(--resume) path. No T1 second-writer hazard exists on this path.
                if verb not in ("wake", "consult"):
                    self._mail_error(rec, f"at={at} rides verb=wake|consult only — a deliver is a "
                                          f"tip-injection and cannot time-travel.")
                    return True
                return self._at_launch(rec, verb, target, body, at)
            if verb == "deliver":
                s = self.find(target)
                if s is None or s.state == "closed":
                    self._mail_error(rec, f"deliver target session://{target} is not live under this "
                                          f"supervisor — route as wake (it will be resumed) or consult.")
                    return True
                if s.state == "busy":
                    return False                       # retried next poll — durable, in order
                self.inject(s, body, source=rec.get("from") or "mailbox", intent=rec)
                return True
            if verb == "wake":
                live = self.find(target)
                if live and live.state == "busy":
                    return False                       # already live + mid-turn → hold, deliver next poll
                if live and live.state in ("idle", "starting"):
                    # already supervised-live → a wake degrades to deliver (truthful routing)
                    self.inject(live, body, source=rec.get("from") or "mailbox", intent=rec)
                    return True
                s = self.spawn(resume=target, cwd=self._resume_safe_cwd(target, rec),
                               source=f"mailbox:{rec.get('from')}",
                               name=rec.get("name") or f"wake-{target[:8]}")
                self.inject(s, body, source=rec.get("from") or "mailbox", intent=rec)
                return True
            if verb == "consult":
                copies = int(rec.get("copies") or 1)
                cap = fabric_concurrency()
                if copies > cap:
                    self._mail_error(rec, f"consult copies={copies} exceeds the concurrency cap {cap} "
                                          f"(COMPANY_FABRIC_CONCURRENCY) — fan ≤ cap, or raise the cap "
                                          f"deliberately on the service.")
                    return True
                with self.lock:
                    self._cap_check(copies)
                cwd = self._resume_safe_cwd(target, rec)  # validated — the fork must resume where the transcript lives
                for i in range(copies):
                    s = self.spawn(resume=target, fork=True, cwd=cwd,
                                   source=f"mailbox:{rec.get('from')}",
                                   name=(rec.get("name") or f"consult-{target[:8]}") + f"-{i + 1}")
                    self.inject(s, body, source=rec.get("from") or "mailbox", intent=rec)
                return True
        except TeachingRefusal as e:
            self._mail_error(rec, str(e))
            return True
        except Exception as e:
            self._mail_error(rec, f"{verb} failed: {e}")
            return True
        return True

    def _at_launch(self, rec: dict, verb: str, target: str, body: str, at: str) -> bool:
        """R3.4 — execute a wake/consult intent carrying `at=` (a point-in-time launch).

        MATERIALIZE (runtime/session_pointintime.materialize_at_point — the native-fork transform
        on the transcript's append-only prefix; source byte-untouched by the library's own law)
        → REGISTER the copy (a durable agent_sessions/ record with materialized_from/at provenance
        — registry-shaped, the R11 heart frame; state=closed until the spawn below flips it)
        → LAUNCH the COPY through the existing spawn path (`claude --resume <new-sid>` in the
        source session's cwd — same project dir, the materializer writes the file beside the
        source) → INJECT the message. consult fans copies=N as N INDEPENDENT materializations
        (each its own file+record — no shared mutable state between consultants).

        Always returns True (consumed): every failure is a terminal teaching reply to the sender,
        never a head-of-line hold (the target's liveness cannot unblock a bad point spec)."""
        from runtime.session_pointintime import PointError, materialize_at_point, \
            materialized_registry_record, resume_cwd_for
        src_rec = self.store.load_agent_session(target)
        if not src_rec or not (isinstance(src_rec.get("jsonl_path"), str) and src_rec.get("jsonl_path")):
            self._mail_error(rec, f"at-launch needs the target's transcript: session://{target} has "
                                  f"no registry record with a jsonl_path. The importer "
                                  f"(ops/agent_sessions_importer.py) backfills the catalog.")
            return True
        copies = int(rec.get("copies") or 1) if verb == "consult" else 1
        cap = fabric_concurrency()
        if copies > cap:
            self._mail_error(rec, f"consult copies={copies} exceeds the concurrency cap {cap} "
                                  f"(COMPANY_FABRIC_CONCURRENCY) — fan ≤ cap, or raise the cap "
                                  f"deliberately on the service.")
            return True
        with self.lock:
            self._cap_check(copies)
        # The resume cwd is the one that ENCODES to the transcript's project dir — NEVER trusted
        # from the record alone: per-event cwd DRIFTS as a session cd's around (measured on the
        # 41-boundary session: record says /home/tim/vllm-tests, project dir is -home-tim), and a
        # --resume in the wrong cwd cannot find the session. resume_cwd_for validates candidates
        # by re-encoding and refuses-teaching if none fit (rule 4 — no silent wrong-dir spawn).
        try:
            cwd = resume_cwd_for(src_rec["jsonl_path"], rec.get("cwd"), src_rec.get("cwd"),
                                 self._cwd_for(target, rec))
        except PointError as e:
            self._mail_error(rec, str(e))
            return True
        for i in range(copies):
            try:
                report = materialize_at_point(src_rec["jsonl_path"], at, source_sid=target)
            except PointError as e:
                self._mail_error(rec, f"at-launch {at} refused: {e}")
                return True
            reg = materialized_registry_record(
                report, src_rec, registered_by=f"supervisor:{rec.get('from')}")
            if not reg.get("cwd"):
                reg["cwd"] = cwd
            self.store.save_agent_session(reg)          # durable identity BEFORE the spawn (no orphan file)
            name = ((rec.get("name") or f"{verb}@{at}·{target[:8]}")
                    + (f"-{i + 1}" if copies > 1 else ""))
            # provenance lives on the REGISTRY RECORD (materialized_from/at/cut_uuid — saved
            # above) + the spawned event's resume field. No invented event kind: the
            # AGENT_SESSION_OPS vocabulary is closed (registry-is-truth), and the record
            # already carries the why.
            s = self.spawn(resume=report["new_sid"], cwd=cwd,
                           source=f"mailbox:{rec.get('from')}", name=name)
            self.inject(s, body, source=rec.get("from") or "mailbox", intent=rec)
        return True


# ───────────────────────────── HTTP face ─────────────────────────────

SUP: SessionSupervisor | None = None


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):                 # journald gets our own lines; not every GET
        pass

    def _send(self, code: int, obj: dict) -> None:
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/health":
            with SUP.lock:
                by_state: dict = {}
                for s in SUP.sessions.values():
                    by_state[s.state] = by_state.get(s.state, 0) + 1
            self._send(200, {"ok": True, "service": "session-supervisor", "bind": "127.0.0.1",
                             "sessions": {"total": len(SUP.sessions), "by_state": by_state},
                             "cap": fabric_concurrency(), "turn_timeout_s": turn_timeout_s(),
                             "permission": fabric_permission()})
            return
        if u.path == "/sessions":
            with SUP.lock:
                recs = [s.record() for s in SUP.sessions.values()]
            self._send(200, {"sessions": recs})
            return
        if u.path == "/watch":
            self._watch(parse_qs(u.query))
            return
        self._send(404, {"error": f"unknown path {u.path} — GET /health · /sessions · "
                                  f"/watch?session=<id>; POST /spawn · /inject · /interrupt · /teardown"})

    def _watch(self, q: dict) -> None:
        key = (q.get("session") or [""])[0]
        s = SUP.find(key)
        if s is None:
            self._send(404, {"error": f"unknown session {key!r} — GET /sessions for the live set"})
            return
        import queue as _q
        sub: _q.Queue = _q.Queue()
        replay = list(s.events)
        s.subscribers.append(sub)
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson")
        self.send_header("Connection", "close")
        self.end_headers()
        try:
            for ev in replay:
                self.wfile.write((json.dumps(ev) + "\n").encode())
            self.wfile.flush()
            while True:
                try:
                    ev = sub.get(timeout=15)
                except _q.Empty:
                    if s.state == "closed":
                        break
                    self.wfile.write(b'{"type":"keepalive"}\n')
                    self.wfile.flush()
                    continue
                self.wfile.write((json.dumps(ev) + "\n").encode())
                self.wfile.flush()
                if ev.get("type") == "closed":
                    break
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            try:
                s.subscribers.remove(sub)
            except ValueError:
                pass

    def do_POST(self):
        self.close_connection = True                   # the bridge's POST socket-reuse lesson
        u = urlparse(self.path)
        try:
            length = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(length) or b"{}") if length else {}
        except ValueError:
            self._send(400, {"error": "body must be JSON"})
            return
        try:
            if u.path == "/spawn":
                # FAMILY 2: thread the optional launch params from the body. Each is omitted (None/
                # falsy) when absent → spawn() reproduces today's byte-identical cmd. A nested
                # "permission":{"mode":...} block (the contracted permission.act shape) maps to
                # permission_mode; a top-level permission_mode is also honoured.
                perm = body.get("permission")
                perm_mode = body.get("permission_mode")
                if perm_mode is None and isinstance(perm, dict):
                    perm_mode = perm.get("mode")
                s = SUP.spawn(cwd=body.get("cwd"), resume=body.get("resume"),
                              fork=bool(body.get("fork")), name=body.get("name"),
                              source=body.get("source") or "http",
                              model=body.get("model"), effort=body.get("effort"),
                              fallback=body.get("fallback"), permission_mode=perm_mode,
                              settings=body.get("settings"), add_dir=body.get("add_dir"),
                              output_format=body.get("output_format"),
                              include_partial=bool(body.get("include_partial")
                                                   or body.get("include_partial_messages")),
                              debug=body.get("debug"), safe_mode=bool(body.get("safe_mode")),
                              bare=bool(body.get("bare")), flags=body.get("flags"))
                if body.get("prompt"):
                    SUP.inject(s, str(body["prompt"]), source=body.get("source") or "http")
                self._send(200, {"ok": True, "session": s.record()})
                return
            if u.path == "/bridge-session":
                # RAIL R1-prime — the consent-gated WIDER-allowlist spawn (arch doc §3.1/§5.1). The
                # operator-consent BEAT rides the body (`operator_consent: true`) — the same
                # operator-vantage gate /api/resolve uses; without it spawn_bridge_session refuses LOUD
                # (consent-not-lockdown: available, gated by a signal, git-revert backstopped). A
                # host/rail-boundary capability (computer/browser) refuses loud too (macOS/interactive
                # only — never bindable on this -p/Linux rail). Results ride back as PROSE on the
                # session's turn stream (liveness:stream, NO typed return_shape) — watch via GET /watch.
                perm = body.get("permission")
                perm_mode = body.get("permission_mode")
                if perm_mode is None and isinstance(perm, dict):
                    perm_mode = perm.get("mode")
                s = SUP.spawn_bridge_session(
                    operator_consent=bool(body.get("operator_consent")),
                    capabilities=body.get("capabilities"),
                    extra_tools=body.get("extra_tools"),
                    cwd=body.get("cwd"), resume=body.get("resume"),
                    fork=bool(body.get("fork")), name=body.get("name"),
                    source=body.get("source") or "bridge-session",
                    permission_mode=perm_mode,
                    model=body.get("model"), effort=body.get("effort"),
                    fallback=body.get("fallback"), settings=body.get("settings"),
                    add_dir=body.get("add_dir"), prompt=body.get("prompt"),
                    flags=body.get("flags"))
                self._send(200, {"ok": True, "session": s.record(),
                                 "liveness": "stream", "watch": f"/watch?session={s.id}",
                                 "note": "R1-prime results ride back as PROSE on the turn stream — "
                                         "watch the session; there is no typed return_shape."})
                return
            if u.path == "/channel-reply":
                # A Claude Code CHANNEL session's `reply` tool calls back here: record the reply in the
                # channel mail log AND push it back into the asking session (the thread's originator) —
                # the no-polling delivery loop (Tim's design 2026-06-14). Routes via runtime.cc_channels.
                from runtime import cc_channels as _cc
                res = _cc.route_reply(str(body.get("from") or ""), str(body.get("thread") or ""),
                                      str(body.get("text") or ""))
                self._send(200, {"ok": True, **res})
                return
            if u.path == "/channel-send":
                # HTTP twin of cc_channels.send — message INTO a live channel session (record + push).
                from runtime import cc_channels as _cc
                res = _cc.send(str(body.get("to") or ""), str(body.get("message") or ""),
                               frm=str(body.get("from") or "fabric"), thread=str(body.get("thread") or ""),
                               topic=str(body.get("topic") or ""))
                self._send(200, {"ok": True, **res})
                return
            if u.path in ("/inject", "/interrupt", "/teardown"):
                s = SUP.find(str(body.get("session") or ""))
                if s is None:
                    self._send(404, {"error": f"unknown session {body.get('session')!r} — "
                                              f"GET /sessions for the live set"})
                    return
                if u.path == "/inject":
                    if not body.get("message"):
                        self._send(400, {"error": "inject needs {session, message}"})
                        return
                    SUP.inject(s, str(body["message"]), source=body.get("source") or "http")
                    self._send(200, {"ok": True, "session": s.record()})
                elif u.path == "/interrupt":
                    SUP.interrupt(s)
                    self._send(200, {"ok": True, "session": s.record()})
                else:
                    SUP.teardown(s)
                    self._send(200, {"ok": True, "session": s.record()})
                return
        except TeachingRefusal as e:
            msg = str(e)
            # consent-gate refusal → 403 (forbidden until consent rides the call); cap → 429; else 409.
            code = (403 if "consent-gated" in msg          # consent gate: forbidden until consent rides
                    else 429 if "over the cap of" in msg  # concurrency cap (precise phrase — NOT bare
                                                          # "cap", which matched "capability" in a
                                                          # bridge-session boundary refusal)
                    else 409)                  # state/boundary conflict (busy/closed/rail-boundary)
            self._send(code, {"error": msg})
            return
        except Exception as e:
            self._send(500, {"error": f"INTERNAL: {e}"})
            return
        self._send(404, {"error": f"unknown path {u.path}"})


def main() -> None:
    global SUP
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    store = FsStore(fcfg.STORE_DIR)
    SUP = SessionSupervisor(store)
    threading.Thread(target=SUP.watchdog_loop, daemon=True, name="watchdog").start()
    threading.Thread(target=SUP.mailbox_loop, daemon=True, name="mailbox").start()

    def _bye(*_a):
        SUP._stop.set()
        SUP.teardown_all()                             # no orphans — the lane's hard guarantee
        os._exit(0)

    signal.signal(signal.SIGTERM, _bye)
    signal.signal(signal.SIGINT, _bye)
    atexit.register(SUP.teardown_all)
    print(f"[session-supervisor] owning sessions at http://127.0.0.1:{port} "
          f"(cap={fabric_concurrency()} · turn_timeout={int(turn_timeout_s())}s · "
          f"permission={fabric_permission()} · store={fcfg.STORE_DIR})", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()


if __name__ == "__main__":
    main()
