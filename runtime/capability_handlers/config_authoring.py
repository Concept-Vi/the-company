"""runtime/capability_handlers/config_authoring.py — the ③ CONFIG-AUTHORING handlers (Capability
Fabric §3.2 / §4 ③). Pure functions over `Suite` (socket-free, mcp-free): EACH builds a validated
request and routes it through the R3 config_writer SERVICE (`r3` client) — the face NEVER opens
`.claude` or shells `claude mcp`/`plugin` itself (the floor, §1.2). The SAME fn backs two faces (the
MCP op + the bridge route, drift-tested byte-identical — §3.3 DRY teeth).

THE OP MODEL (CONVENTIONS uniform verbs): every resource here takes `op ∈ {list, get, act}` —
  · list/get → a DECLARATIVE-DIRECT read (face-direct via r3.read; touches no floor — §3.1);
  · act      → an `act:` discriminator names the F4-registered named act (CONVENTIONS §F4); the write
               routes to the R3 config_writer (consent-gated for dangerous payloads — §5.2).
`config.patterns` is the exception: `direct-read`, ops `resolve|describe` (a pure chooser resolver —
documentation-as-data, no file, no R3).

THE REOPENED BOUNDARIES (Tim's steer — buildable config-face capabilities, IN scope): CC-04
keybindings (config.keybindings), CC-32 telemetry/data-posture (config.telemetry), CC-29 cloud-provider
(config.provider) — all R3 settings/host-config writes, non-executable, reversible. The genuinely-inert
classes (CC-01/02 TUI, CC-28 org-admin, CC-31 monorepo) stay out (absence-of-row = boundary).

SOLE-OPERATOR FLOOR (Tim's steer): dangerous capabilities (hook command, skill body, slash-command
body, mcp stdio spec, plugin install) are ENABLED, gated by the consent BEAT the config_writer enforces
(per-call consent= or a standing /consent marker) + git-revert backstop — never locked out, never a
multi-user wall. An unconsented dangerous act returns a PENDING-PROPOSAL receipt, not a denial.
"""
from __future__ import annotations

from runtime.capability_handlers import register_handler
from runtime.capability_handlers import r3
from runtime.capability_handlers.reduction import config_targets as CT
from runtime.capability_handlers.reduction import cli_allowlist as CL


# ── shared helpers ────────────────────────────────────────────────────────────────────────────────

def _bad_op(key: str, op, valid) -> ValueError:
    return ValueError(
        f"{key}: unknown op {op!r} — valid ops are {list(valid)}. list/get READ the current config "
        f"(no consent); act WRITES via the R3 config_writer (act= names the operation; dangerous "
        f"payloads ride the consent beat — a proposal, never a wall).")


def _require(p: dict, *names) -> None:
    for n in names:
        if not p.get(n):
            raise ValueError(f"missing required parameter {n!r}.")


def _read(key: str, scope: str, name, project_dir) -> dict:
    """A DECLARATIVE-DIRECT read through the R3 client (face-direct; touches no floor — §3.1)."""
    payload = {"key": key, "scope": scope}
    if name:
        payload["name"] = name
    if project_dir:
        payload["project_dir"] = project_dir
    return r3.read(**payload)


# ── CC-12 · hooks ────────────────────────────────────────────────────────────────────────────────

def hooks(suite, op="list", *, scope="user", name=None, project_dir=None,
          act=None, block=None, consent=False, **_x) -> dict:
    """hooks (CC-12): read settings.json hook blocks; act adds/updates/removes a hook handler or flips
    the disableAllHooks flag. A hook `command` is a shell command Claude Code EXECUTES on a lifecycle
    trigger — DANGEROUS payload → consent beat."""
    if op in ("list", "get"):
        return _read("config.hooks", scope, None, project_dir)
    if op == "act":
        valid_acts = ("add-hook", "update-hook", "remove-hook", "set-flag")
        if act not in valid_acts:
            raise ValueError(f"hooks act must be one of {list(valid_acts)} (CONVENTIONS §F4); got {act!r}.")
        # add/update/remove-hook merge a `hooks` sub-block; set-flag merges disableAllHooks into hooks.
        _require({"block": block}, "block")
        return r3.write(key="config.hooks", scope=scope, block=block, consent=consent,
                        project_dir=project_dir)
    raise _bad_op("config.hooks", op, ("list", "get", "act"))


# ── CC-11 · mcp-servers ──────────────────────────────────────────────────────────────────────────

def mcp_servers(suite, op="list", *, scope="user", name=None, project_dir=None,
                act=None, transport=None, url_or_cmd=None, json_spec=None, consent=False, **_x) -> dict:
    """mcp-servers (CC-11): read the registered MCP servers; act runs the native `claude mcp …` CLI
    (add/add-json/remove/get/list/reset-project-choices) via the R3 config_writer. A stdio `command`
    is an EXEC target → exec-tier consent beat (§5.2 C1). Registration is the sanctioned argv-array
    path; raw ~/.claude.json edits are refused upstream."""
    if op == "list":
        return r3.cli(act="config.mcp_servers:list")
    if op == "get":
        _require({"name": name}, "name")
        return r3.cli(act="config.mcp_servers:get", name=name)
    if op == "act":
        valid_acts = ("add", "add-json", "remove", "get", "list", "reset-project-choices")
        if act not in valid_acts:
            raise ValueError(f"mcp-servers act must be one of {list(valid_acts)} (CONVENTIONS §F4); got {act!r}.")
        slots = {}
        if act == "add":
            _require({"name": name, "transport": transport, "url_or_cmd": url_or_cmd},
                     "name", "transport", "url_or_cmd")
            slots = {"name": name, "transport": transport, "scope": _mcp_scope(scope), "url_or_cmd": url_or_cmd}
        elif act == "add-json":
            _require({"name": name, "json_spec": json_spec}, "name", "json_spec")
            slots = {"name": name, "json": json_spec}
        elif act == "remove":
            _require({"name": name}, "name")
            slots = {"name": name, "scope": _mcp_scope(scope)}
        elif act == "get":
            _require({"name": name}, "name")
            slots = {"name": name}
        return r3.cli(act=f"config.mcp_servers:{act}", consent=consent, **slots)
    raise _bad_op("config.mcp_servers", op, ("list", "get", "act"))


def _mcp_scope(scope: str) -> str:
    """claude mcp scopes are local|user|project (NOT the settings.local file naming). Map the corpus
    scope words to the CLI's; default to local (the claude mcp default)."""
    return {"local": "local", "user": "user", "project": "project"}.get(scope, "local")


# ── CC-26 · output-style ─────────────────────────────────────────────────────────────────────────

def output_style(suite, op="list", *, scope="user", name=None, project_dir=None,
                 act=None, body=None, block=None, consent=False, **_x) -> dict:
    """output-style (CC-26): read an output-style file / the outputStyle+statusLine settings pointers;
    act creates/deletes a style markdown file or sets the outputStyle/statusLine pointer. Presentation
    strings — NON-dangerous (no exec), so no consent beat (the tier distinction is real)."""
    if op in ("list", "get"):
        return _read("config.output_style", scope, name, project_dir)
    if op == "act":
        valid_acts = ("set-style", "create-style", "delete-style", "set-statusline", "clear-statusline")
        if act not in valid_acts:
            raise ValueError(f"output-style act must be one of {list(valid_acts)} (CONVENTIONS §F4); got {act!r}.")
        if act in ("create-style",):
            _require({"name": name, "body": body}, "name", "body")
            return r3.write(key="config.output_style", scope=scope, name=name, body=body,
                            consent=consent, project_dir=project_dir)
        if act in ("set-style", "set-statusline", "clear-statusline"):
            # these are settings.json POINTER writes (outputStyle / statusLine) — modelled via the
            # settings primitive. NOTE (honest): config.output_style targets the style FILE; the
            # outputStyle/statusLine settings POINTER is a settings.json env-adjacent write — surfaced
            # as a building gap (the pointer write is not yet a config_targets row). Fail loud, named.
            return {"ok": False, "status": "building",
                    "teach": f"output-style act={act!r} sets a settings.json POINTER "
                             f"(outputStyle/statusLine). That pointer write is a settings-key write not "
                             f"yet rowed in config_targets — building, live-verify pending. The style "
                             f"FILE authoring (create-style/delete-style) is wired now.",
                    "act": act, "scope": scope}
        if act == "delete-style":
            return {"ok": False, "status": "building",
                    "teach": "output-style delete-style removes a style file; file DELETION is a "
                             "config_writer op not yet exposed (writes create/overwrite; delete is the "
                             "next R3 op). Building, live-verify pending — named, not silent.",
                    "act": act, "name": name, "scope": scope}
    raise _bad_op("config.output_style", op, ("list", "get", "act"))


# ── CC-03 · slash-commands ───────────────────────────────────────────────────────────────────────

def slash_commands(suite, op="list", *, scope="user", name=None, project_dir=None,
                   act=None, body=None, consent=False, **_x) -> dict:
    """slash-commands (CC-03): read a command markdown file under .claude/commands/; act creates/updates
    a command .md (delete is a building gap). A command body becomes a PROMPT Claude runs on invocation
    (can carry !`bash` + tool directives) — DANGEROUS → consent beat."""
    if op in ("list", "get"):
        return _read("config.slash_commands", scope, name, project_dir)
    if op == "act":
        valid_acts = ("create", "update", "delete")
        if act not in valid_acts:
            raise ValueError(f"slash-commands act must be one of {list(valid_acts)} (CONVENTIONS §F4); got {act!r}.")
        if act in ("create", "update"):
            _require({"name": name, "body": body}, "name", "body")
            return r3.write(key="config.slash_commands", scope=scope, name=name, body=body,
                            consent=consent, project_dir=project_dir)
        return {"ok": False, "status": "building",
                "teach": "slash-command delete removes a command .md; file DELETION is the next R3 op "
                         "(writes create/overwrite). Building, live-verify pending — named, not silent.",
                "act": act, "name": name, "scope": scope}
    raise _bad_op("config.slash_commands", op, ("list", "get", "act"))


# ── CC-13 / CC-34 · extensions (skills authoring + plugin install) ─────────────────────────────────

def extensions(suite, op="list", *, scope="user", name=None, project_dir=None,
               act=None, body=None, plugin=None, url=None, path=None, consent=False, **_x) -> dict:
    """extensions (CC-13 / CC-34): read a SKILL.md / plugin state; act either AUTHORS a skill file
    (create/update-skill → SKILL.md under .claude/skills/<name>/) or runs `claude plugin …`
    (install/update/uninstall/validate, marketplace add) via the R3 config_writer. A SKILL.md body is a
    prompt Claude loads; plugin install fetches+RUNS third-party code (exec-tier) — both DANGEROUS →
    consent beat (plugin install re-tiered to operator-consent, §5.2)."""
    file_acts = ("create-skill", "update-skill", "delete-skill")
    cli_acts = ("install-plugin", "update-plugin", "uninstall-plugin", "validate-plugin",
                "add-marketplace", "update-native", "install-native")
    if op in ("list", "get"):
        return _read("config.extensions", scope, name, project_dir)
    if op == "act":
        if act in ("create-skill", "update-skill"):
            _require({"name": name, "body": body}, "name", "body")
            return r3.write(key="config.extensions", scope=scope, name=name, body=body,
                            consent=consent, project_dir=project_dir)
        if act == "delete-skill":
            return {"ok": False, "status": "building",
                    "teach": "delete-skill removes a SKILL.md dir; DELETION is the next R3 op (writes "
                             "create/overwrite). Building, live-verify pending — named, not silent.",
                    "act": act, "name": name, "scope": scope}
        if act in ("install-plugin", "update-plugin", "uninstall-plugin"):
            _require({"plugin": plugin}, "plugin")
            slot = "config.extensions:" + {"install-plugin": "install-plugin",
                                           "update-plugin": "update-plugin",
                                           "uninstall-plugin": "uninstall-plugin"}[act]
            return r3.cli(act=slot, consent=consent, plugin=plugin, scope=_plugin_scope(scope))
        if act == "validate-plugin":
            _require({"path": path}, "path")
            return r3.cli(act="config.extensions:validate-plugin", path=path)
        if act == "add-marketplace":
            _require({"url": url}, "url")
            return r3.cli(act="config.extensions:add-marketplace", consent=consent, url=url)
        if act in ("update-native", "install-native"):
            # CC-34 (reopened — Tim's steer): the native Claude Code binary updater as a dev-bridge.
            # `claude update` / `claude install` are exec-tier (they fetch+run an installer) → the
            # consent beat. The cli rows were added by the L-④-dev lane under config.extensions.
            return r3.cli(act=f"config.extensions:{act}", consent=consent)
        raise ValueError(
            f"extensions act must be one of {list(file_acts + cli_acts)} (CONVENTIONS §F4); got {act!r}.")
    raise _bad_op("config.extensions", op, ("list", "get", "act"))


def _plugin_scope(scope: str) -> str:
    return {"user": "user", "project": "project", "local": "local"}.get(scope, "user")


# ── CC-27 · patterns (the pure chooser resolver — direct-read, no R3) ──────────────────────────────

# the chooser table (the extensibility-patterns corpus entry's routing map, as data — §4 / the corpus
# entry). resolve(intent) → the mechanism + its entry; describe() → the whole table. Documentation-as-
# data: NO file, NO R3, NO consent — a pure read on every face incl. a cold agent.
_CHOOSER = [
    dict(intent="different role/tone/format every turn", mechanism="output-style",
         activation="always", entry="output-style", changes="the system prompt directly"),
    dict(intent="claude should always know project conventions/facts", mechanism="claude-md",
         activation="always", entry="claude-memory", changes="adds facts after the system prompt"),
    dict(intent="one-off system-prompt addition for a single run", mechanism="append-system-prompt",
         activation="at-launch", entry="output-style", changes="appends without removing the default"),
    dict(intent="a separately-scoped helper with its own prompt/model/tools", mechanism="subagent",
         activation="per-task", entry="extensions", changes="runs an isolated subagent"),
    dict(intent="a reusable workflow / multi-step procedure / checklist", mechanism="skill",
         activation="on-relevant", entry="extensions", changes="loads task instructions on demand"),
    dict(intent="the same as a skill but with a short /name", mechanism="custom-command",
         activation="on-invoke", entry="extensions", changes="legacy flat command form"),
    dict(intent="run code automatically at a lifecycle point", mechanism="hook",
         activation="on-event", entry="hooks", changes="fires on PreToolUse/PostToolUse/Stop/…"),
    dict(intent="hard allow/deny of a tool (enforcement)", mechanism="permission",
         activation="always", entry="permission", changes="the permission system enforces"),
    dict(intent="give claude access to an external tool/db/api", mechanism="mcp-server",
         activation="on-relevant", entry="mcp-servers", changes="connects a stdio/http/sse server"),
    dict(intent="package + share/version any of the above", mechanism="plugin",
         activation="at-launch", entry="extensions", changes="bundles + a manifest"),
]
# the shared path placeholders + precedence (the corpus entry's other two halves).
_PLACEHOLDERS = {
    "${CLAUDE_PROJECT_DIR}": "the project root (absolute)",
    "${CLAUDE_PLUGIN_ROOT}": "the installed plugin's root dir",
    "${CLAUDE_PLUGIN_DATA}": "the plugin's per-install data dir",
}
_PRECEDENCE = ["enterprise (managed) — outranks all", "command-line args", "local (.claude/settings.local.json)",
               "project (.claude/settings.json)", "user (~/.claude/settings.json)"]


def patterns(suite, op="resolve", *, intent=None, mechanism=None, **_x) -> dict:
    """patterns (CC-27): the CHOOSER resolver — route a customization intent to the right Claude Code
    mechanism (pure, no file, no R3). op='resolve' (intent= → best-match rows); op='describe' (the whole
    chooser + placeholders + precedence laws). Documentation-as-data — the company exposes no
    customization face; this resolves WHICH mechanism, each mechanism's own entry carries its bridge."""
    if op == "describe":
        return {"ok": True, "op": "describe", "chooser": _CHOOSER,
                "placeholders": _PLACEHOLDERS, "precedence": _PRECEDENCE,
                "note": "the chooser is documentation-as-data; pick a mechanism row, then its `entry` "
                        "names the resource that contracts the actual write."}
    if op == "resolve":
        if not intent and not mechanism:
            raise ValueError("patterns(op='resolve') needs intent= (a customization goal) or mechanism= "
                             "(a mechanism name to look up). Use op='describe' to see the whole chooser.")
        rows = _CHOOSER
        if mechanism:
            rows = [r for r in _CHOOSER if r["mechanism"] == mechanism]
        if intent:
            q = intent.lower()
            scored = sorted(_CHOOSER, key=lambda r: -_overlap(q, r["intent"]))
            top = [r for r in scored if _overlap(q, r["intent"]) > 0][:3] or scored[:1]
            rows = top if not mechanism else rows
        return {"ok": True, "op": "resolve", "intent": intent, "mechanism": mechanism,
                "matches": rows,
                "note": "the top chooser rows for this intent; each row's `entry` names the resource "
                        "that contracts the write. No file touched (pure resolver)."}
    raise ValueError(f"config.patterns: unknown op {op!r} — resolve | describe.")


def _overlap(q: str, text: str) -> int:
    qs = set(w for w in q.replace("/", " ").split() if len(w) > 2)
    ts = set(w for w in text.replace("/", " ").split() if len(w) > 2)
    return len(qs & ts)


# ── CC-04 · keybindings (reopened — R3 host-config write) ──────────────────────────────────────────

def keybindings(suite, op="get", *, scope="user", project_dir=None,
                act=None, context=None, bindings=None, block=None, consent=False, **_x) -> dict:
    """keybindings (CC-04, reopened): read ~/.claude/keybindings.json; act sets/unbinds a context's
    keymap. A binding is namespace:action (or null to UNBIND); USER-SCOPE ONLY (per-project keybindings
    are not a Claude Code surface — a non-user scope is REFUSED LOUD, never silently redirected to user);
    auto-detected (no restart); NON-executable, reversible (no consent beat — git-revert is the undo)."""
    if scope not in ("user",):
        raise ValueError(
            f"keybindings is USER-scope only (~/.claude/keybindings.json) — scope={scope!r} is not a "
            f"Claude Code keybindings location. Refused loud (never silently redirected to user). "
            f"Per-project keybindings are not a surface; the operator's TUI shortcuts are user-level.")
    if op in ("list", "get"):
        return _read("config.keybindings", "user", None, project_dir)
    if op == "act":
        valid_acts = ("set-binding", "unbind", "set-context")
        if act not in valid_acts:
            raise ValueError(f"keybindings act must be one of {list(valid_acts)}; got {act!r}.")
        # the write `block` is {context, bindings:{keystroke: action|null}}; accept either an explicit
        # block= OR (context= + bindings=) for the convenience shape.
        if block is None:
            _require({"context": context, "bindings": bindings}, "context", "bindings")
            block = {"context": context, "bindings": bindings}
        return r3.write(key="config.keybindings", scope="user", block=block, consent=consent,
                        project_dir=project_dir)
    raise _bad_op("config.keybindings", op, ("list", "get", "act"))


# ── CC-32 · telemetry (reopened — settings env flags) ──────────────────────────────────────────────

# the data-posture env flags (Atlas: settings env). NON-executable policy strings, reversible.
_TELEMETRY_FLAGS = (
    "DISABLE_TELEMETRY", "DISABLE_ERROR_REPORTING", "DISABLE_NON_ESSENTIAL_MODEL_CALLS",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC", "DISABLE_AUTOUPDATER", "DISABLE_BUG_COMMAND",
)


def telemetry(suite, op="get", *, scope="user", project_dir=None,
              act=None, flags=None, consent=False, **_x) -> dict:
    """telemetry (CC-32, reopened): read / set the data-posture env flags in settings.json `env`
    (DISABLE_TELEMETRY/DISABLE_ERROR_REPORTING/…). The operator's OWN data-posture choice — a policy
    string, reversible, NON-dangerous (no exec → no consent beat)."""
    if op in ("list", "get"):
        return _read("config.telemetry", scope, None, project_dir)
    if op == "act":
        if act not in ("set-flag",):
            raise ValueError(f"telemetry act must be 'set-flag'; got {act!r}.")
        _require({"flags": flags}, "flags")
        if not isinstance(flags, dict) or not flags:
            raise ValueError("telemetry set-flag needs flags= a non-empty object {ENV_FLAG: '1'|'0'}.")
        bad = [k for k in flags if k not in _TELEMETRY_FLAGS]
        if bad:
            raise ValueError(f"telemetry: unknown data-posture flag(s) {bad} — one of "
                             f"{list(_TELEMETRY_FLAGS)} (grounded in the Atlas; fail loud, never write "
                             f"an env key Claude Code won't read as a data-posture toggle).")
        return r3.write(key="config.telemetry", scope=scope, block=flags, consent=consent,
                        project_dir=project_dir)
    raise _bad_op("config.telemetry", op, ("list", "get", "act"))


# ── CC-29 · provider (reopened — settings env, same primitive as telemetry) ────────────────────────

_PROVIDER_KEYS = (
    "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX", "ANTHROPIC_BASE_URL", "ANTHROPIC_MODEL",
    "ANTHROPIC_SMALL_FAST_MODEL", "AWS_REGION", "CLOUD_ML_REGION", "ANTHROPIC_VERTEX_PROJECT_ID",
)


def provider(suite, op="get", *, scope="user", project_dir=None,
             act=None, env=None, consent=False, **_x) -> dict:
    """provider (CC-29, reopened): read / set the cloud-provider routing env in settings.json `env`
    (CLAUDE_CODE_USE_BEDROCK/VERTEX, ANTHROPIC_BASE_URL/MODEL). The operator's inference-routing choice
    — a host-env edit, same primitive as telemetry, reversible, NON-dangerous (no exec → no consent
    beat). Takes effect on the NEXT session start (the fabric inherits it transparently)."""
    if op in ("list", "get"):
        return _read("config.provider", scope, None, project_dir)
    if op == "act":
        if act not in ("set-provider",):
            raise ValueError(f"provider act must be 'set-provider'; got {act!r}.")
        _require({"env": env}, "env")
        if not isinstance(env, dict) or not env:
            raise ValueError("provider set-provider needs env= a non-empty object {ENV_KEY: value}.")
        bad = [k for k in env if k not in _PROVIDER_KEYS]
        if bad:
            raise ValueError(f"provider: unknown provider env key(s) {bad} — one of {list(_PROVIDER_KEYS)} "
                             f"(grounded in the Atlas; fail loud, never write an env key Claude Code "
                             f"won't read as a provider toggle).")
        return r3.write(key="config.provider", scope=scope, block=env, consent=consent,
                        project_dir=project_dir)
    raise _bad_op("config.provider", op, ("list", "get", "act"))


# ── wire the real fns onto the pre-declared HANDLERS (register_handler swaps stub→real, flips built) ──
register_handler("config.hooks", hooks)
register_handler("config.mcp_servers", mcp_servers)
register_handler("config.output_style", output_style)
register_handler("config.slash_commands", slash_commands)
register_handler("config.extensions", extensions)
register_handler("config.patterns", patterns)
register_handler("config.keybindings", keybindings)
register_handler("config.telemetry", telemetry)
register_handler("config.provider", provider)
