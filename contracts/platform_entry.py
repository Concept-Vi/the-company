"""C-PLAT — platform entry contract (Pydantic). LANE-CONTRACTS — Mirror-Registry System.

One row per external platform the Company exposes. Carries the platform-level type taxonomy
(Mirror-Registry Spec §2.1–§2.9). Discovered by PlatformRegistry via a PLATFORM = {...} dict
in platforms/*.py (importlib pattern — mirrors roles/*.py:ROLE).

Conforms to the registry-type convention (contracts/node_type.py):
  - `version: int = 1` (NOT schema_ver — registry-type half of the documented split; F-FIX-3)
  - schema-additive: add optional fields + bump version; never break an existing one
  - typed Literals for adapter-selector fields (F-FIX-12): a novel value FAILS LOUD at
    PlatformEntry load — never silently configures an unrunnable adapter.

F-FIX-12 (Build Plan): InjectTransport, OutputProtocolFormat, DiscoverySourceFormat are
  CLOSED typed Literals. New members added only when their adapter is built.
  A novel value → Pydantic validation fails loud → gap-surface path fires.

Nested sub-models (PG-D5): PlatformRegistry loads via PlatformEntry.model_validate(dict).
Deeply-nested sub-models require validation, not positional construction.

All `schema_ver` references on nested sub-models are REPLACED by `version: int = 1`
per F-FIX-3 (registry-type convention, not wire-message convention).
"""
from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field


# ── Typed Literals (F-FIX-12) — closed sets; novel values FAIL LOUD ──────────────────────

InjectTransport = Literal[
    "stdin-ndjson",      # inject user turns via stdin NDJSON (the subprocess/Claude adapter)
    # ADD new members here when their adapter is built — NOT before
]

OutputProtocolFormat = Literal[
    "stream-json",       # read output as newline-delimited JSON stream events
    # ADD new members here when their adapter is built — NOT before
]

DiscoverySourceFormat = Literal[
    "commander-options-text",  # Commander.js --help option-row text (CliHelpDiscoverer)
    "json-init",               # stream-json system/init event (StreamInitDiscoverer)
    # ADD new members here when their adapter is built — NOT before
]

DiscoverySourceType = Literal[
    "cli-help",              # parse `<bin> --help` → CliHelpDiscoverer
    "stream-init",           # capture running session system/init → StreamInitDiscoverer
    "rest-openapi",          # GET OpenAPI/Swagger doc → RestOpenApiDiscoverer (unbuilt)
    "mcp-list-tools",        # MCP tools/list → McpListToolsDiscoverer (unbuilt)
    "graphql-introspect",    # GraphQL __schema → GraphqlIntrospectionDiscoverer (unbuilt)
]

InvocationKind = Literal[
    "subprocess",   # Popen with stdin/stdout PIPE (SubprocessAdapter — the only built adapter)
    "rest",         # HTTP REST calls (unbuilt — gap-surface when platform #2 registers)
    "graphql",      # GraphQL (unbuilt)
    "mcp",          # MCP protocol (unbuilt)
    "library",      # SDK/library native (unbuilt)
]


# ── Nested sub-models (Mirror-Registry Spec §2.1a, §2.3, §2.4, §2.5, §2.7, §2.8) ────────

class ExecutableLocator(BaseModel):
    """How to FIND the platform's entry-point. §2.1a.

    Engine fn _find_executable(locator) resolves: env_override → PATH (which_fallback)
    → known_paths. FAIL LOUD if none found (never silently absent).
    """
    name: str                        # "claude" | base URL for REST | endpoint for GraphQL
    env_override: str = ""           # e.g. "COMPANY_CLAUDE_BIN" — env var that overrides resolution
    which_fallback: bool = True      # probe PATH via shutil.which
    known_paths: list[str] = []      # e.g. ["~/.local/bin/claude"]
    version: int = 1


class DiscoverySource(BaseModel):
    """How the platform describes itself. §2.3.

    `type` selects the engine adapter from the CLOSED adapter set. A value not in
    DiscoverySourceType → Pydantic validation fails loud → gap-surface fires (F-FIX-12).

    `format` is DiscoverySourceFormat when provided — also typed-Literal guarded.
    The {binary} token in `command` is substituted from the ExecutableLocator at runtime.

    `floor_guard`: if the parse yields fewer than this many entries, RAISE (§2.6).
    """
    type: DiscoverySourceType
    command: list[str] = []          # e.g. ["{binary}", "--help"]; {binary} substituted at runtime
    stderr_merge: bool = False
    format: DiscoverySourceFormat | Literal[""] = ""  # typed-guarded (F-FIX-12): novel format FAILS LOUD
    parse_rule: str = ""             # "option-row" | "init-field" ...
    event_filter: dict = {}          # {"type":"system","subtype":"init"} for stream-init
    timeout_s: int = 15
    floor_guard: int = 0             # min viable parse output (§2.6); 30 for Claude --help
    fail_loud: bool = True
    version: int = 1


class SignalSets(BaseModel):
    """The classify inputs: hazard vocabulary + capability axes + transport invariants. §2.4.

    These are the ONLY membership lists the rules carry (R1/R2/R3). The rule LOGIC is
    engine-code; the signal VALUES are platform data. This is 'rules, not rows' conformance.

    transport_invariants: cached derivation result from derive_transport_invariants()
    (introspection/rules.py). NEVER hand-typed in the platform row — populated by the
    derive function at PlatformRegistry load time (F-FIX-2).

    hazard_scope MUST be "flag_name_only" — NEVER description text (R2 constraint).
    """
    # R1 signal — transport invariants, DERIVED from the consumer's spawn template
    transport_invariants_derived_from: str = ""   # "_build_spawn_cmd + body_key_handlers"
    transport_invariants: list[str] = []          # cached derivation result; refreshes with template

    # R2 signal — the platform's OWN hazard naming convention (flag-NAME scope only)
    hazard_name_vocabulary: list[str] = []        # ["dangerously","skip","bypass","unsafe"]
    hazard_scope: str = "flag_name_only"          # NEVER description text — mandatory constraint

    # R3 signal — capability axes: where a flag widens the session surface
    capability_axes: dict[str, list[str]] = {}    # {"tools-builtin":[...],"mcp":[...],...}
    version: int = 1


class ConsumerReservedInvariants(BaseModel):
    """Flags the consumer (the fabric) ALWAYS owns or locks. §2.5.

    This is a property of the CONSUMER, not of the platform's flag list.
    The R1 input. body_key_overrides: locked flags that own a dedicated body-key handler.
    The `kind` on each override is the SpawnFlagAssembler closed adapter set (engine-code).
    """
    session_mode_flag: str = ""         # "-p" — activates headless mode
    injection_protocol: dict = {}       # {flag:"--input-format", value:"stream-json"}
    output_protocol: dict = {}          # {flag:"--output-format", value:"stream-json"}
    verbosity_flag: str = ""            # "--verbose", required for output_protocol
    strict_tool_server_config: bool = False  # always emit --strict-mcp-config
    body_key_overrides: dict[str, dict] = {}  # {"model":{flag:"--model",kind:"value"}, ...}
    version: int = 1


class VersionSource(BaseModel):
    """How to read the running platform version. §2.7.

    Engine unit VersionProbe runs the command, strips suffix, compares to stamp.
    """
    command: list[str] = []      # ["{binary}", "--version"]
    strip_suffix: str = ""       # " (Claude Code)"
    format: str = "semver-stripped"
    version: int = 1


class InvocationBinding(BaseModel):
    """The held-open-session contract: inject/output protocol, envelopes, state machine. §2.8.

    inject_transport: InjectTransport typed Literal (F-FIX-12) — a novel value FAILS LOUD
    at PlatformEntry load. The Literal | Literal[""] union allows empty-string (unset) but
    rejects any other free string, forcing the gap-surface path for unbuilt adapters.
    output_protocol_format: OutputProtocolFormat typed Literal (F-FIX-12) — same guard.

    session_state_machine + local_handle_prefix carry subprocess-shaped debt (R-OVERFIT).
    A REST platform sets session_state_machine: {} — these fields are Optional for that reason.
    """
    invocation_kind: str = "subprocess"
    # message injection
    inject_transport: InjectTransport | Literal[""] = ""  # typed-guarded (F-FIX-12): novel value FAILS LOUD
    user_message_envelope: dict = {}
    interrupt_envelope: dict = {}
    # output reading
    output_protocol_format: OutputProtocolFormat | Literal[""] = ""  # typed-guarded (F-FIX-12)
    session_init_event: dict = {}
    assistant_turn_event: dict = {}
    content_blocks: list[dict] = []
    turn_result_event: dict = {}
    usage_telemetry_block: dict = {}
    event_render_registry_ref: str = ""    # path to event→render mapping
    # lifecycle
    init_signal: dict = {}
    session_state_machine: dict = {}       # subprocess-shaped; {} for stateless platforms
    platform_session_id_path: str = ""     # "session_id"
    local_handle_prefix: str = ""          # "as-" — supervisor ephemeral pre-id handle
    resume_flag: str = ""                  # "--resume"
    fork_flag: str = ""                    # "--fork-session"
    version: int = 1


class PermissionModel(BaseModel):
    """The posture vocabulary + values + profiles. §2.x (Groups 3/10).

    profiles: list of named permission profiles (default / bridge-session / etc).
    """
    flag: str = ""                     # "--permission-mode"
    env_override: str = ""             # "COMPANY_FABRIC_PERMISSION"
    default: str = ""                  # "plan"
    values: list[dict] = []            # [{name,is_read_only,...}, ...]
    hazard_flag: dict = {}             # {flag:"--dangerously-skip-permissions",posture:"locked",...}
    profiles: list[dict] = []          # [{name,tool_set,permission_mode,consent_required,...}]
    version: int = 1


class ToolSurface(BaseModel):
    """Tool-specifiers, floor-set, capability→tool grants, rail-boundary set. §2.x (Group 4)."""
    allow_flag: str = ""               # "--allowedTools"
    deny_flag: str = ""                # "--disallowedTools"
    builtin_flag: str = ""             # "--tools"
    allowlist_separator: str = ","
    floor_tool_set: list[str] = []     # ["mcp__company"]
    tool_specifiers: list[str] = []
    tool_namespace_convention: dict = {}
    capability_to_tool_grant: dict = {}   # {"git":["Bash"],"lsp":["Read","Edit"],...}
    rail_boundary_set: dict = {}          # {"computer":{"rail":"headless-p-linux"},...}
    version: int = 1


class ToolServerWiring(BaseModel):
    """How external tool-servers attach to this platform. §2.x (Group 5)."""
    config_flag: str = ""              # "--mcp-config"
    config_format: str = ""           # "json-inline"
    server_entry_shape: dict = {}     # {protocol,command,args}
    plugin_loader_flags: dict = {}    # {dir_flag,url_flag,kind}
    version: int = 1


class ResourceGovernance(BaseModel):
    """Concurrency cap + timeouts. §2.x (Group 12)."""
    concurrency_cap: dict = {}         # {env_var,default}
    turn_timeout: dict = {}            # {env_var,default_s}
    init_wait: dict = {}               # {env_var,default_s}
    version: int = 1


# ── Top-level PlatformEntry ───────────────────────────────────────────────────────────────

class PlatformEntry(BaseModel):
    """One external platform the Company exposes. One row = one platform.

    Loaded by PlatformRegistry (introspection/platforms.py) via importlib discovery of
    platforms/*.py files, each carrying a module-level PLATFORM = {...} dict.
    Loaded via PlatformEntry.model_validate(dict) (PG-D5: deeply-nested sub-models
    require validation, not positional construction).

    invocation_kind: typed InvocationKind Literal (F-FIX-12) — a novel value FAILS LOUD.

    projection_targets: the faces this platform projects to (§2.9).
    The closed set today: mcp_tool | bridge_route | capabilities_key | resolver | supervisor_posture.

    transport_invariants in signal_sets are populated by derive_transport_invariants()
    (introspection/rules.py) at PlatformRegistry load time — NEVER hand-typed (F-FIX-2).
    """
    id: str                                    # "claude-code" — Platform Registry key
    display_name: str = ""
    executable_locator: ExecutableLocator = Field(default_factory=ExecutableLocator)
    invocation_kind: InvocationKind = "subprocess"
    discovery_sources: list[DiscoverySource] = []
    version_source: VersionSource = Field(default_factory=VersionSource)
    signal_sets: SignalSets = Field(default_factory=SignalSets)
    consumer_reserved_invariants: ConsumerReservedInvariants = Field(
        default_factory=ConsumerReservedInvariants)
    invocation_binding: InvocationBinding = Field(default_factory=InvocationBinding)
    permission_model: PermissionModel = Field(default_factory=PermissionModel)
    tool_surface: ToolSurface = Field(default_factory=ToolSurface)
    tool_server_wiring: ToolServerWiring = Field(default_factory=ToolServerWiring)
    projection_targets: list[str] = []
    resource_governance: ResourceGovernance = Field(default_factory=ResourceGovernance)

    version: int = 1                           # registry-type convention (node_type.py) — NOT schema_ver
