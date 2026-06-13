"""C-CAP — capability entry contract (Pydantic). LANE-CONTRACTS — Mirror-Registry System.

One row per discovered capability of an external platform. Binary-discovered, not hand-authored.
The SINGLE source all faces project from (MCP tool / bridge route / cap:// resolver).

Conforms to the registry-type convention (contracts/node_type.py):
  - `version: int = 1` (NOT schema_ver — see contracts/AGENTS.md: "version on NodeType/registry-types")
  - schema-additive: add optional fields + bump version; never break an existing one
  - typed Literal for kind (the type axis) — a novel kind FAILS LOUD, never silently ignored

F-FIX-3 (Build Plan): use `version` (NOT `schema_ver`) — registry-type half of the documented split.
F-FIX-5 (Build Plan): add `assembler_kind` + `locked_reason` for supervisor SpawnFlagAssembler.
F-FIX-14 (Build Plan): id = f'{kind}/{name}' where name for flags INCLUDES the '--' prefix.
  e.g. CapabilityEntry(id='flag/--debug', kind='flag', name='--debug')

General system: gained `platform_id` FK to PlatformEntry (Mirror-Registry Spec §2.10).
"""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


EntryKind = Literal[
    "flag",           # --flag / -f CLI launch arg
    "slash_command",  # /command
    "subcommand",     # claude <sub>  (auth, mcp, doctor, install, plugin, ...)
    "tool",           # built-in tool (Bash, Read, ...) from system/init
    "mcp_tool",       # mcp__<server>__<tool> with input schema
    "setting",        # ~/.claude/settings.json field
    "permission",     # permission string
    "hook_event",     # PreToolUse ... WorktreeRemove
    "sdk_event",      # system/init, result, stream_event, ...
    "enum_value",     # a permissionMode / apiKeySource / status value
    "mcp_server",     # an MCP server the session declares (init mcp_servers) — distinct from mcp_tool
    "skill",          # a skill the session declares (init skills)
    "plugin",         # a plugin the session declares (init plugins)
    "agent",          # a subagent the session declares (init agents)
]   # extended 2026-06-13: the live init self-declaration carries kinds the vocabulary lacked (gap-pressure on the kind registry itself — surfaced, not coerced)


class CapabilityVerbs(BaseModel):
    """The verb-edge layer — what operations are valid over this entry.

    Modelled on contracts/node_type.py's fractal shape: type → fields → verb-edges.
    All default True (expose-not-gate); set False explicitly to restrict.
    """
    readable: bool = True       # fetchable via capability(op="get")
    searchable: bool = True     # appears in capability(op="search")
    projectable: bool = True    # auto-projected to MCP/bridge faces
    configurable: bool = False  # settable (settings only)


class CapabilityEntry(BaseModel):
    """One discovered capability of an external platform.

    id construction rule (F-FIX-14): id = f'{kind}/{name}'
    For flags, name INCLUDES the '--' prefix: id='flag/--debug', name='--debug'.
    The discoverer constructs ids this way from help-parse output.
    cap://flag/--debug → rest='flag/--debug' → CapabilityRegistry.get('flag/--debug').

    platform_id: FK to PlatformEntry (Mirror-Registry Spec §2.10). Defaults to
    'claude-code' so the Claude Code instance works without always stating it.

    assembler_kind (F-FIX-5): the SpawnFlagAssembler closed adapter kind
    (bool/value/csv/repeat/swap) — needed by the supervisor to translate the
    registry posture into an actual flag assembly. Empty = not a supervisor-managed flag.

    locked_reason (F-FIX-5): the 'why' teaching-refusal text for LOCKED / HAZARD
    entries — what the supervisor emits when an agent tries to override a locked flag.
    Empty = no teaching text.
    """
    id: str                              # "flag/--debug", "slash/doctor", "mcp_tool/Bash"
    kind: EntryKind
    name: str
    aliases: list[str] = []
    description: str = ""

    # flag fields
    takes_value: bool = False
    value_type: str = ""                 # string|int|bool|path|csv|json
    choices: list[str] = []
    default_value: str | None = None
    visible: bool = True                 # false = hidden flag (design-time seeded from live docs)

    # classification (DERIVED — never stored as an opinion; posture_rule records which rule fired)
    posture: Literal["locked", "hazard", "consent", "safe", "unmatched"] = "unmatched"
    posture_rule: str = ""               # which rule fired: "R1".."R5" — auditable
    axis: str = ""                       # the capability axis for R3 entries

    # supervisor assembly fields (F-FIX-5)
    assembler_kind: str = ""             # bool|value|csv|repeat|swap — SpawnFlagAssembler kind
    locked_reason: str = ""              # teaching-refusal text for locked/hazard entries

    # command/tool fields
    args_schema: dict = {}
    input_schema: dict = {}
    server_name: str = ""

    # setting fields
    setting_path: str = ""
    setting_type: str = ""

    # hook fields
    hook_trigger: str = ""

    # cross-cutting / provenance
    platform_id: str = "claude-code"    # FK into Platform Registry (Mirror-Registry Spec §2.10)
    source: str = ""                     # help-parse | init-event | live-docs
    source_url: str = ""                 # live-docs-seeded entries: the doc URL
    fetched_at: str = ""                 # live-docs-seeded entries: ISO date of design-time fetch
    status: Literal["active", "retired"] = "active"
    retired_in_version: str = ""
    discovered_at: str = ""             # ISO ts of last live-surface discovery
    raw_extra: dict = {}                 # init-event fields not in known set (fail-loud captured)

    version: int = 1                     # registry-type convention (node_type.py) — NOT schema_ver
    verbs: CapabilityVerbs = CapabilityVerbs()
