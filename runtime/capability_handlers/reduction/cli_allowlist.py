"""cli_allowlist.py — R3 reduction registry: native config/VCS CLI invocations as ARGV-ARRAY templates,
keyed by HANDLER-KEY:act (so every row's resource-prefix is a declared HANDLERS key — the cross-grain
bridge the foundation test enforces), with a per-row TIER (read/write/exec) driving the consent class.

THE INJECTION FLOOR (arch §5.2): every render is an argv ARRAY built from a fixed template + validated
value SLOTS — NEVER a shell string. A value with shell metachars lands as ONE argv element (shell=False
downstream). This stops injection INTO the call; the tier gates the dangerous VALUE.

Grounded in the Claude Code Atlas (verified 2026-06-12 — never invented):
  · `claude mcp add [--transport stdio|http|sse] [--scope local|user|project] <name> <cmd-or-url>` /
    `mcp add-json <name> <json>` / `mcp remove` / `mcp list|get` / `mcp reset-project-choices`  (mcp.md)
  · `claude plugin install/update/uninstall <plugin> [-s scope]` / `plugin validate <dir>` /
    `plugin marketplace add <url>`  (plugins-reference.md)
  · `claude update` (apply an update now — no args) / `claude install [latest|stable|<version>]`
    (the NATIVE-UPDATER / installer; channel|version arg — CC-34 reopened, setup.md)
  · `git status/log/worktree …` / `git commit` / `gh pr create`  (common-workflows.md / git.md)
  · `claude auth login` (re-authenticate / switch account — OAuth, reads pasted code from stdin
    on WSL/SSH/containers) / `claude auth logout` (clear / switch the stored credential) /
    `claude setup-token` (mint a one-year inference-only token — PRINTS the secret to stdout,
    saves nothing) — CC-24 REOPENED host-config acts (authentication.md / troubleshoot-install.md)

TIERS: read (ungated) · write (config-mutating, gated) · exec (registers/fetches+runs code: mcp add
stdio spec §5.2 C1, plugin install — gated, highest).

SOLE-OPERATOR FLOOR (Tim's steer — overrides the arch's original CC-24 'absence-of-row' boundary):
the CC-24 host-config acts (relogin/logout/setup-token) are ENABLED, consent-gated, NEVER locked
out. `auto.auth:setup-token` is exec-tier AND carries returns_secret=True — the config_writer
MUST surface its stdout to the CONSENTING OPERATOR only and the handler NEVER folds the printed
token into a wire result (the redaction floor, §5.2 C3 honoured by NOT returning the secret).
"""
from __future__ import annotations
import re

_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._@-]*$")
_MCP_SCOPES = ("local", "user", "project")
_PLUGIN_SCOPES = ("user", "project", "local")
_TRANSPORTS = ("stdio", "http", "sse")

# CLI_ALLOWLIST: "<handler-key>:<act>" -> row. The prefix before ':' is a declared HANDLERS key
# (config.mcp_servers / config.extensions / dev.git) — the cross-grain bridge.
#   tool  : "claude" | "git" | "gh"   tier : read|write|exec
#   sub   : the value-free subcommand argv head
#   slots : ordered value slots (see render_argv)
CLI_ALLOWLIST = {
    # ── config.mcp_servers (CC-11) → claude mcp ──
    "config.mcp_servers:add": dict(tool="claude", tier="exec", sub=["mcp", "add"], slots=[
        ("flag", "--transport", _TRANSPORTS, "transport"),
        ("flag", "--scope", _MCP_SCOPES, "scope"), ("name", "name"), ("pos", "url_or_cmd")]),
    "config.mcp_servers:add-json": dict(tool="claude", tier="exec", sub=["mcp", "add-json"], slots=[
        ("name", "name"), ("pos", "json")]),
    "config.mcp_servers:remove": dict(tool="claude", tier="write", sub=["mcp", "remove"], slots=[
        ("flag", "--scope", _MCP_SCOPES, "scope"), ("name", "name")]),
    "config.mcp_servers:list": dict(tool="claude", tier="read", sub=["mcp", "list"], slots=[]),
    "config.mcp_servers:get": dict(tool="claude", tier="read", sub=["mcp", "get"], slots=[("name", "name")]),
    "config.mcp_servers:reset-project-choices": dict(tool="claude", tier="write",
                                                     sub=["mcp", "reset-project-choices"], slots=[]),
    # ── config.extensions (CC-13 / CC-34) → claude plugin ──
    "config.extensions:install-plugin": dict(tool="claude", tier="exec", sub=["plugin", "install"], slots=[
        ("flag", "--scope", _PLUGIN_SCOPES, "scope"), ("name", "plugin")]),
    "config.extensions:update-plugin": dict(tool="claude", tier="exec", sub=["plugin", "update"], slots=[
        ("flag", "--scope", _PLUGIN_SCOPES, "scope"), ("name", "plugin")]),
    "config.extensions:uninstall-plugin": dict(tool="claude", tier="write", sub=["plugin", "uninstall"], slots=[
        ("flag", "--scope", _PLUGIN_SCOPES, "scope"), ("name", "plugin")]),
    "config.extensions:validate-plugin": dict(tool="claude", tier="read", sub=["plugin", "validate"],
                                              slots=[("pos", "path")]),
    "config.extensions:add-marketplace": dict(tool="claude", tier="exec",
                                              sub=["plugin", "marketplace", "add"], slots=[("pos", "url")]),
    # ── config.extensions (CC-34 reopened — the NATIVE-UPDATER / installer; a host dev-bridge) ──
    # `claude update` applies an update immediately (no args; Atlas setup.md). `claude install`
    # takes a release CHANNEL or version (`latest`|`stable`|<version>) — that arg becomes the
    # auto-update default. exec-tier (it fetches+runs a new binary → highest consent class).
    "config.extensions:update-native": dict(tool="claude", tier="exec", sub=["update"], slots=[]),
    "config.extensions:install-native": dict(tool="claude", tier="exec", sub=["install"], slots=[
        ("pos", "channel")]),   # channel|version: "latest"|"stable"|"1.2.3"
    # ── dev.git (CC-06) → git / gh — the structured path ──
    "dev.git:status": dict(tool="git", tier="read", sub=["status", "--porcelain=v1", "-b"], slots=[]),
    "dev.git:log": dict(tool="git", tier="read", sub=["log", "--no-color"], slots=[("rest", "args")]),
    "dev.git:worktrees": dict(tool="git", tier="read", sub=["worktree", "list", "--porcelain"], slots=[]),
    "dev.git:commit": dict(tool="git", tier="write", sub=["commit"], slots=[("rest", "args")]),
    "dev.git:worktree-add": dict(tool="git", tier="write", sub=["worktree", "add"], slots=[("rest", "args")]),
    "dev.git:worktree-remove": dict(tool="git", tier="write", sub=["worktree", "remove"], slots=[("rest", "args")]),
    "dev.git:open-pr": dict(tool="gh", tier="write", sub=["pr", "create"], slots=[("rest", "args")]),
    # ── auto.auth (CC-24 REOPENED — host-config credential acts; consent-gated, NEVER locked out) ──
    # relogin = `claude auth login` (OAuth re-auth / account switch; reads the pasted code from stdin
    # on WSL/SSH/containers — the operator's path). exec-tier (establishes a credential). No slots.
    "auto.auth:relogin": dict(tool="claude", tier="exec", sub=["auth", "login"], slots=[]),
    # logout = `claude auth logout` (clear / switch the stored credential). write-tier (reversible by
    # re-login). No slots.
    "auto.auth:logout": dict(tool="claude", tier="write", sub=["auth", "logout"], slots=[]),
    # setup-token = `claude setup-token` (mint a one-year inference-only token — PRINTS the secret to
    # stdout, saves nothing). exec-tier + returns_secret: the config_writer surfaces stdout to the
    # consenting OPERATOR only; the handler NEVER returns the token (redaction floor, §5.2 C3).
    "auto.auth:setup-token": dict(tool="claude", tier="exec", sub=["setup-token"], slots=[],
                                  returns_secret=True),
}


def cli_for(act_key: str) -> dict:
    """The allowlist row for a 'handler-key:act'. FAILS LOUD (KeyError) on unknown."""
    if act_key not in CLI_ALLOWLIST:
        raise KeyError(f"cli_allowlist: no entry for {act_key!r} — allowlisted: {sorted(CLI_ALLOWLIST)} "
                       f"(the allowlist is the exec boundary; fail loud).")
    return CLI_ALLOWLIST[act_key]


def tier_of(act_key: str) -> str:
    return cli_for(act_key)["tier"]


def returns_secret(act_key: str) -> bool:
    """True iff this act prints a SECRET to stdout (e.g. `claude setup-token`). The config_writer
    surfaces such stdout to the consenting operator only; the handler NEVER folds it into a wire
    result (the redaction floor, §5.2 C3 — achieved by NOT returning the secret)."""
    return bool(cli_for(act_key).get("returns_secret", False))


def acts_for(handler_key: str) -> list[str]:
    """The acts available on a handler key (the part after ':') — used by faces to enumerate."""
    pre = handler_key + ":"
    return [k.split(":", 1)[1] for k in CLI_ALLOWLIST if k.startswith(pre)]


def _name(v, what):
    if not isinstance(v, str) or not _NAME_RE.match(v):
        raise ValueError(f"{what} {v!r} invalid — letters/digits then [._@-], no leading dash, no shell "
                         f"metacharacters (the second wall on top of argv-array; fail loud).")
    return v


def render_argv(act_key: str, **kw) -> list[str]:
    """Render a 'handler-key:act' + value kwargs into an argv ARRAY (leading binary first). FAILS LOUD
    (ValueError) on a missing slot — never a half-rendered literal reaching subprocess. Values land as
    discrete argv items (the injection floor)."""
    row = cli_for(act_key)
    argv = [row["tool"], *row["sub"]]
    for slot in row["slots"]:
        kind = slot[0]
        if kind == "flag":
            _, flag, choices, key = slot
            v = kw.get(key)
            if v is None:
                raise ValueError(f"render_argv({act_key!r}): missing required slot {key!r} (fail loud).")
            if choices and v not in choices:
                raise ValueError(f"render_argv({act_key!r}): {key}={v!r} not one of {choices} (fail loud).")
            argv += [flag, str(v)]
        elif kind == "name":
            v = kw.get(slot[1])
            if v is None:
                raise ValueError(f"render_argv({act_key!r}): missing required slot {slot[1]!r} (fail loud).")
            argv.append(_name(v, slot[1]))
        elif kind == "pos":
            v = kw.get(slot[1])
            if v is None:
                raise ValueError(f"render_argv({act_key!r}): missing required positional {slot[1]!r} (fail loud).")
            argv.append(str(v))
        elif kind == "rest":
            rest = kw.get(slot[1]) or []
            if not isinstance(rest, (list, tuple)):
                raise ValueError(f"render_argv({act_key!r}): slot {slot[1]!r} must be a list of argv items.")
            argv += [str(a) for a in rest]
    return argv
