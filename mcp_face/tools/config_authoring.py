"""mcp_face/tools/config_authoring.py — the ③ CONFIG-AUTHORING agent face (Capability Fabric §3.3).

RESOURCE-KEYED MCP tools (matching the CONVENTIONS named-act grain), glob-auto-registered by
mcp_face/server.py (ZERO server.py edit — §1.3). EACH tool is thin: validate op ∈ OPS → delegate to
the SAME handler the bridge route calls (DRY: one handler, two faces, drift-tested byte-identical —
tests/capability_handlers_acceptance.py). The handler routes writes to the R3 config_writer service
(the floor — this face NEVER opens .claude or shells claude mcp/plugin; a sanctioned service acts).

THE LAW (sessions.py precedent): a new need is a new `op`, never a new flat tool. ToolAnnotations
carry readonly/destructive from the HANDLERS readonly flag (the honest contracts model — readonly∧
destructive refused at construction). Reads are readOnly; the consequential WRITE tools are not.

SOLE-OPERATOR FLOOR: dangerous config writes (hook command, skill body, command body, mcp stdio spec,
plugin install) are ENABLED, gated by the consent BEAT the config_writer enforces. A cold agent calling
a dangerous act without consent gets a PENDING-PROPOSAL receipt (consent-not-lockdown), NEVER a wall.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from contracts.tools import ToolAnnotations as CompanyToolAnnotations
from mcp.types import ToolAnnotations as SDKToolAnnotations
from runtime import capability_handlers as ch

# EXPORTED closed op set for this module's tools (CONTRACT-FORMAT §9.2: extract_reality.py fails loud
# on a tool module without an OPS constant). The ③ resources share the {list,get,act} verb set; patterns
# is the pure resolver {resolve,describe}. This is the UNION across the module's tools.
OPS = ("list", "get", "act", "resolve", "describe")
_CRUD_OPS = ("list", "get", "act")
_PATTERN_OPS = ("resolve", "describe")


def _sdk(readonly: bool, destructive: bool, title: str) -> SDKToolAnnotations:
    """contracts.ToolAnnotations → SDK hints (the sessions.py F10.1 wiring). The contracts ctor's gate
    (readonly∧destructive raises) bites before registration."""
    ann = CompanyToolAnnotations(readonly=readonly, destructive=destructive,
                                 idempotent=readonly)
    return SDKToolAnnotations(title=title, readOnlyHint=ann.readonly, destructiveHint=ann.destructive,
                              idempotentHint=ann.idempotent, openWorldHint=False)


def _call(key: str, op: str, **p) -> dict:
    """Load the WIRED registry and delegate to the SAME handler the bridge calls (DRY). load_all is
    idempotent; this guarantees the family modules' register_handler ran regardless of import order."""
    ch.load_all()
    return ch.get(key).fn(None, op, **p)


def register(mcp, suite):
    # NOTE: handlers are pure over Suite but the ③ family is suite-independent (config files / native
    # CLI via R3) — they accept `suite` as the first positional for the uniform DRY signature and ignore
    # it. The bridge passes its Suite; the face passes None. The RESULT dict is identical either way.

    @mcp.tool(annotations=_sdk(False, False, "Config — hooks (read/author settings.json hook blocks)"))
    def config_hooks(op: str = "list", scope: str = "user", name: str = "", project_dir: str = "",
                     act: str = "", block: dict | None = None, consent: bool = False) -> dict:
        """CC-12 · HOOKS — the settings.json hook handlers Claude Code runs on lifecycle triggers.
          op='list'|'get' — READ the hook blocks in a settings scope (user|project|local). No consent.
          op='act'        — WRITE: act='add-hook'|'update-hook'|'remove-hook'|'set-flag'; block= the
                            hooks sub-block (or {"disableAllHooks": true} for set-flag). A hook
                            `command` is a SHELL COMMAND Claude Code EXECUTES on the trigger — DANGEROUS:
                            without consent=true (or a standing /consent grant) you get a PENDING
                            PROPOSAL naming the danger (consent-not-lockdown), not a wall.
        Writes route to the R3 config_writer (the sole .claude writer); the face never edits the file."""
        return _call("config.hooks", op, scope=scope, name=name or None, project_dir=project_dir or None,
                     act=act or None, block=block, consent=consent)

    @mcp.tool(annotations=_sdk(False, False, "Config — MCP servers (claude mcp add/remove/list)"))
    def config_mcp_servers(op: str = "list", scope: str = "local", name: str = "", project_dir: str = "",
                           act: str = "", transport: str = "", url_or_cmd: str = "",
                           json_spec: str = "", consent: bool = False) -> dict:
        """CC-11 · MCP SERVERS — the external tool/DB/API servers Claude Code connects.
          op='list'        — the registered servers (`claude mcp list`).
          op='get'         — one server (`claude mcp get`, name= required).
          op='act'         — act='add' (transport+url_or_cmd+name) | 'add-json' (name+json_spec) |
                            'remove' (name) | 'reset-project-choices'. A stdio `command` is an EXEC
                            target — exec-tier: unconsented → PENDING PROPOSAL (consent-not-lockdown).
        Runs the native `claude mcp …` argv (injection-resistant) via the R3 config_writer."""
        return _call("config.mcp_servers", op, scope=scope, name=name or None,
                     project_dir=project_dir or None, act=act or None, transport=transport or None,
                     url_or_cmd=url_or_cmd or None, json_spec=json_spec or None, consent=consent)

    @mcp.tool(annotations=_sdk(False, False, "Config — output style (presentation files/pointers)"))
    def config_output_style(op: str = "list", scope: str = "user", name: str = "", project_dir: str = "",
                            act: str = "", body: str = "", consent: bool = False) -> dict:
        """CC-26 · OUTPUT STYLE — the presentation/role styling (output-styles/*.md + outputStyle/
        statusLine pointers).
          op='list'|'get' — READ a style file / the pointers.
          op='act'        — act='create-style' (name+body) authors the style markdown (NON-dangerous —
                            presentation strings, no consent); set-style/set-statusline/clear-statusline
                            (settings pointer) + delete-style are named building gaps (honest, not silent)."""
        return _call("config.output_style", op, scope=scope, name=name or None,
                     project_dir=project_dir or None, act=act or None, body=body or None, consent=consent)

    @mcp.tool(annotations=_sdk(False, False, "Config — slash commands (.claude/commands/*.md)"))
    def config_slash_commands(op: str = "list", scope: str = "user", name: str = "", project_dir: str = "",
                              act: str = "", body: str = "", consent: bool = False) -> dict:
        """CC-03 · SLASH COMMANDS — the custom /command prompts under .claude/commands/.
          op='list'|'get' — READ a command .md.
          op='act'        — act='create'|'update' (name+body) authors the command markdown. A command
                            body becomes a PROMPT Claude runs on invocation (can carry !`bash` + tool
                            directives) — DANGEROUS: unconsented → PENDING PROPOSAL. delete is a named
                            building gap."""
        return _call("config.slash_commands", op, scope=scope, name=name or None,
                     project_dir=project_dir or None, act=act or None, body=body or None, consent=consent)

    @mcp.tool(annotations=_sdk(False, False, "Config — extensions (skill authoring + plugin install)"))
    def config_extensions(op: str = "list", scope: str = "user", name: str = "", project_dir: str = "",
                          act: str = "", body: str = "", plugin: str = "", url: str = "", path: str = "",
                          consent: bool = False) -> dict:
        """CC-13 / CC-34 · EXTENSIONS — skill authoring + the `claude plugin` surface.
          op='list'|'get' — READ a SKILL.md / plugin state.
          op='act'        — act='create-skill'|'update-skill' (name+body → SKILL.md, DANGEROUS prompt
                            body) | 'install-plugin'|'update-plugin'|'uninstall-plugin' (plugin=,
                            install/update FETCH+RUN third-party code — EXEC-tier) |
                            'validate-plugin' (path=, read) | 'add-marketplace' (url=, exec).
        Dangerous acts unconsented → PENDING PROPOSAL (consent-not-lockdown). Runs via the R3 config_writer."""
        return _call("config.extensions", op, scope=scope, name=name or None,
                     project_dir=project_dir or None, act=act or None, body=body or None,
                     plugin=plugin or None, url=url or None, path=path or None, consent=consent)

    @mcp.tool(annotations=_sdk(True, False, "Config — extensibility patterns (the chooser resolver)"))
    def config_patterns(op: str = "resolve", intent: str = "", mechanism: str = "") -> dict:
        """CC-27 · PATTERNS — the CHOOSER: route a customization intent to the right Claude Code
        mechanism (skill/command/hook/MCP/output-style/subagent/CLAUDE.md/plugin/settings). PURE READ
        (documentation-as-data — no file, no R3, no consent).
          op='resolve'  — intent= (a goal) or mechanism= (a name) → best-match chooser rows + each
                          row's `entry` (the resource that contracts the write).
          op='describe' — the whole chooser + the shared path placeholders + the scope/precedence laws."""
        return _call("config.patterns", op, intent=intent or None, mechanism=mechanism or None)

    @mcp.tool(annotations=_sdk(False, False, "Config — keybindings (~/.claude/keybindings.json)"))
    def config_keybindings(op: str = "get", scope: str = "user", project_dir: str = "",
                           act: str = "", context: str = "", bindings: dict | None = None,
                           block: dict | None = None, consent: bool = False) -> dict:
        """CC-04 (reopened) · KEYBINDINGS — the operator's ~/.claude/keybindings.json (the TUI shortcuts;
        inert against headless, but the operator owns it — buildable, reversible).
          op='list'|'get' — READ the current keybindings.
          op='act'        — act='set-binding'|'unbind'|'set-context'; either block= {context, bindings:
                            {keystroke: action|null}} OR context= + bindings=. action is namespace:action
                            (null UNBINDS); user-scope only; auto-detected (no restart). NON-executable →
                            no consent beat; git-revert is the undo."""
        return _call("config.keybindings", op, scope="user", project_dir=project_dir or None,
                     act=act or None, context=context or None, bindings=bindings, block=block,
                     consent=consent)

    @mcp.tool(annotations=_sdk(False, False, "Config — telemetry / data-posture (settings env flags)"))
    def config_telemetry(op: str = "get", scope: str = "user", project_dir: str = "",
                         act: str = "", flags: dict | None = None, consent: bool = False) -> dict:
        """CC-32 (reopened) · TELEMETRY — the data-posture env flags in settings.json `env`
        (DISABLE_TELEMETRY / DISABLE_ERROR_REPORTING / …). The operator's OWN data choice (a policy
        string, reversible, NON-dangerous → no consent beat).
          op='list'|'get' — READ the current env block.
          op='act'        — act='set-flag', flags= {ENV_FLAG: '1'|'0'} (validated against the closed
                            data-posture flag set; unknown flag → fail loud)."""
        return _call("config.telemetry", op, scope=scope, project_dir=project_dir or None,
                     act=act or None, flags=flags, consent=consent)

    @mcp.tool(annotations=_sdk(False, False, "Config — cloud provider (settings env routing)"))
    def config_provider(op: str = "get", scope: str = "user", project_dir: str = "",
                        act: str = "", env: dict | None = None, consent: bool = False) -> dict:
        """CC-29 (reopened) · PROVIDER — the cloud-provider routing env in settings.json `env`
        (CLAUDE_CODE_USE_BEDROCK/VERTEX, ANTHROPIC_BASE_URL/MODEL). Same primitive as telemetry — a
        host-env edit, reversible, NON-dangerous → no consent beat. Takes effect on the NEXT session.
          op='list'|'get' — READ the current provider env.
          op='act'        — act='set-provider', env= {ENV_KEY: value} (validated against the closed
                            provider-key set; unknown key → fail loud)."""
        return _call("config.provider", op, scope=scope, project_dir=project_dir or None,
                     act=act or None, env=env, consent=consent)

    return (config_hooks, config_mcp_servers, config_output_style, config_slash_commands,
            config_extensions, config_patterns, config_keybindings, config_telemetry, config_provider)
