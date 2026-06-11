"""config_targets.py — R3 reduction registry: which .claude file / json-pointer each ③ CONFIG-AUTHORING
write targets, whether its payload is DANGEROUS (an exec target → consent tier, §5.2), and the
per-scope path resolution. SERVICE-SIDE (arch §3.2): the resource-shaped faces stay thin; this is the
"what each act writes" truth, invisible to the corpus grain.

GROUND TRUTH (Claude Code Atlas, verified 2026-06-12 — never invented):
  · Hooks: settings JSON `hooks` → EVENT → matcher-groups → handlers (type:command/…). Scope files:
    ~/.claude/settings.json (user) · .claude/settings.json (project) · .claude/settings.local.json (local).
  · MCP servers: `claude mcp add` writes ~/.claude.json (local under projects.<cwd>, OR user top-level)
    or .mcp.json (project root). project→.mcp.json, local→~/.claude.json. (mcp.md / mcp-quickstart.md)
  · Output styles: markdown+frontmatter under output-styles/; outputStyle/statusLine settings pointers.
  · Slash commands: markdown under commands/. Skills: SKILL.md under skills/<name>/.
  · Plugins enabled-state: enabledPlugins in settings; extraKnownMarketplaces for marketplaces.
  · Keybindings (CC-04, reopened): ~/.claude/keybindings.json. Telemetry/data-posture (CC-32, reopened):
    settings env flags.

DANGEROUS = the payload is something Claude Code will EXECUTE or fetch+run (§5.2): hook `command`,
skill `body`, slash-command `body`, mcp stdio `command`, plugin source. NOT dangerous: presentation
strings (outputStyle/statusLine), boolean flags, enable/disable of an already-installed plugin,
keybindings, telemetry flags. is_dangerous() drives the consent class.

NO `managed` scope (§5.5): managed policy is an ORG-ADMIN boundary the company is a SUBJECT of —
absence-of-row IS the boundary, applied evenly (no synthetic managed path).
"""
from __future__ import annotations
import os

HOME = os.path.expanduser("~")

# the three REAL settings scopes (NO managed — §5.5 boundary = absence). scope -> the settings file.
# project/local are repo-relative (joined to a project_dir at write time); user is absolute under HOME.
SCOPES = {
    "user":    os.path.join(HOME, ".claude", "settings.json"),
    "project": os.path.join(".claude", "settings.json"),
    "local":   os.path.join(".claude", "settings.local.json"),
}

# hook EVENT names — the closed Claude Code lifecycle set (Atlas hooks.md). Used by content validation.
HOOK_EVENTS = (
    "PreToolUse", "PostToolUse", "PreToolBatch", "PostToolBatch", "Notification",
    "UserPromptSubmit", "SessionStart", "SessionEnd", "Stop", "SubagentStop",
    "PreCompact", "MessageDisplay", "PermissionRequest",
)

# CONFIG_TARGETS: handler key -> reduction row.
#   kind        : "settings" | "command" | "skill" | "output-style" | "mcp-json" | "keybindings"
#                 — the config_writer /write `kind` discriminator this handler routes to.
#   dangerous   : True iff the payload is an exec/fetch target (drives consent class config-write).
#   subdir      : the dir under a scope's .claude/ for file-authoring (commands/, skills/, output-styles/)
#   ext         : file extension for the markdown-file kinds
#   scope_files : per-resource scope→file override (mcp_servers: project→.mcp.json, local→~/.claude.json)
#   schema      : the corpus contract:schema name the block validates against
CONFIG_TARGETS = {
    "config.hooks": dict(
        kind="settings", pointer="hooks", dangerous=True, schema="hooks.config",
        teach="a hook handler is a shell command / HTTP / MCP-tool / prompt Claude Code EXECUTES at a "
              "lifecycle TRIGGER — an executable payload."),
    "config.mcp_servers": dict(
        kind="mcp-json", pointer="mcpServers", dangerous=True, schema="mcp-servers.entry",
        scope_files={"project": ".mcp.json", "local": "~/.claude.json", "user": "~/.claude.json"},
        teach="an MCP server's stdio `command` is an executable Claude Code launches."),
    "config.output_style": dict(
        kind="output-style", subdir="output-styles", ext=".md", dangerous=False, schema="output-style.file",
        teach="an output-style file is prose+frontmatter — a presentation string, not executed."),
    "config.slash_commands": dict(
        kind="command", subdir="commands", ext=".md", dangerous=True, schema="slash-command.file",
        teach="a slash-command body becomes a prompt Claude Code runs on invocation (can carry "
              "!`bash` injections + tool directives)."),
    "config.extensions": dict(
        kind="skill", subdir="skills", ext=".md", skill_layout=True, dangerous=True, schema="skill.file",
        teach="a SKILL.md body is a prompt Claude loads (can carry tool directives + bundled scripts); "
              "plugin install fetches+runs third-party code."),
    # ── reopened boundaries (Tim's explicit steer — buildable R3 config-face capabilities) ──
    "config.keybindings": dict(
        # keybindings live in a DEDICATED file (~/.claude/keybindings.json — Atlas keybindings.md, NOT
        # settings.json), USER-scope only (it governs the operator's TUI; per-project keybindings are
        # not a Claude Code surface). The scope_files override pins the single real target so scope_path
        # never falls through to SCOPES (= settings.json) — that fall-through was a foundation bug this
        # lane closes (the kind="keybindings" payload would have clobbered settings.json). Object with a
        # `bindings` array; auto-detected (no restart); non-executable, reversible.
        kind="keybindings", pointer="bindings", dangerous=False, schema="keybindings.config",
        scope_files={"user": "~/.claude/keybindings.json"},
        teach="a keybinding writes ~/.claude/keybindings.json — a host-config the operator owns "
              "(governs the interactive TUI; inert against headless). Non-executable, reversible (CC-04)."),
    "config.telemetry": dict(
        kind="settings", pointer="env", dangerous=False, schema="telemetry.flags",
        teach="a telemetry/data-posture flag (DISABLE_TELEMETRY/DISABLE_ERROR_REPORTING/…) is written to "
              "settings.json `env` — the operator's own data-posture choice. A policy string, reversible (CC-32)."),
    "config.provider": dict(
        kind="settings", pointer="env", dangerous=False, schema="provider.env",
        teach="a cloud-provider selection (CLAUDE_CODE_USE_BEDROCK/VERTEX, ANTHROPIC_BASE_URL/MODEL) is a "
              "host-env edit written to settings.json `env` — same primitive as telemetry. The operator's "
              "inference-routing choice; reversible (CC-29)."),
}


def target_for(key: str) -> dict:
    """The reduction row for a handler key. FAILS LOUD (KeyError) on an unknown key — registry-is-truth,
    no silent default."""
    if key not in CONFIG_TARGETS:
        raise KeyError(f"config_targets: no target for {key!r} — known: {sorted(CONFIG_TARGETS)}")
    return CONFIG_TARGETS[key]


def is_dangerous(key: str) -> bool:
    """True iff this capability's write payload is an exec/fetch target (drives the consent tier)."""
    return bool(target_for(key).get("dangerous"))


def scope_path(key: str, scope: str, name: str | None = None) -> str:
    """Resolve the on-disk path a (key, scope[, name]) write targets. FAILS LOUD on an out-of-row scope
    (managed / unknown) — no synthetic path for a boundary scope (§5.5). For settings kinds returns the
    settings file; for per-resource scope_files returns the override (mcp_servers); for file-authoring
    kinds returns the scope's subdir file (commands/<name>.md, skills/<name>/SKILL.md, output-styles/<name>.md).
    Paths are returned in their CANONICAL form (~ for HOME user-scope, repo-relative for project/local)
    — config_writer resolves them to absolute against a project_dir + HOME."""
    row = target_for(key)
    # per-resource scope override (mcp_servers)
    sf = row.get("scope_files")
    if sf is not None:
        if scope not in sf:
            raise ValueError(f"config_targets.scope_path({key!r}): scope {scope!r} not valid here — "
                             f"one of {sorted(sf)} (no managed/synthetic scope, §5.5).")
        return sf[scope]
    if scope not in SCOPES:
        raise ValueError(f"config_targets.scope_path({key!r}): scope {scope!r} invalid — the three "
                         f"scopes are {sorted(SCOPES)} (no managed scope; boundary = absence, §5.5).")
    subdir = row.get("subdir")
    if subdir is None:
        # a settings-block write → the settings file for the scope (canonical ~/repo-relative form)
        return SCOPES[scope] if scope == "user" else SCOPES[scope]
    # a file-authoring write under the scope's .claude/<subdir>/
    base = os.path.join("~", ".claude") if scope == "user" else os.path.join(".claude")
    if row.get("skill_layout"):
        leaf = os.path.join(name or "{name}", "SKILL.md")
    else:
        leaf = (name or "{name}") + row.get("ext", ".md")
    return os.path.join(base, subdir, leaf)
