"""platforms/claude_code.py — Claude Code as INSTANCE #1 of the Mirror-Registry System.
Mirror-Registry System, LANE-REGISTRIES. Spec §7 (the registration rows that prove the lift).

PURE DATA — imports + ONE `PLATFORM = {...}` dict, NO def/class (ROW-PURITY, 2026-06-14). The entire
Claude Code mechanism is expressed as a PlatformEntry row (validated by PlatformRegistry via
PlatformEntry.model_validate, PG-D5). Every Claude-specific value the engine needs (binary name, flag
names, stream-json protocol, permission-mode strings, MCP config format, hazard vocabulary, capability
axes, event shapes, the state machine, timeouts, the body-key↔flag-name map) lives HERE — NOWHERE in
introspection/engine.py / rules.py / adapters/ (the PG2 / F-FIX-10 leak invariant; this is the
legitimate Level-2 home for these strings). This row is the CLEAN TEMPLATE the generalization-proof
needs: a second platform of a known kind copies this shape — imports + a dict, nothing else.

THE head_builder binding (F-FIX-2) — the engine derives the R1 transport-invariant set by CALLING a
zero-arg thunk that returns the consumer's unconditional spawn-head argv. A Pydantic model cannot hold
a callable, so the binding is a registration, not row data. It USED to live here as a
`_register_head_builder()` def, which made the row non-pure. It now lives in platforms/_wiring.py (the
`_`-prefixed bootstrap module the registry's file-discovery skips), imported by the consumer that
needs the live derivation (runtime/suite.py; the crosscheck test). This row keeps only its DECLARED
(post-R6-correct) `transport_invariants` as the engine-validated fallback when no thunk is wired.

Spec §7 cites every value to Lane A's file:line or the Dynamic Capability Registry spec; the row
below reproduces those Observed values verbatim.
"""
from __future__ import annotations

# ── F-FIX-5 step 3 — the body-key ↔ flag-name MAP (DATA) ────────────────────────────────────────────
# The supervisor's SPAWN_FLAGS keys are snake_case BODY-KEYS ("session_id", "mcp_config"); the registry
# speaks flag-NAMES ("--session-id", "--mcp-config"). LANE-SUPERVISOR-REFACTOR (deferred) translates one
# to the other to read posture from the registry instead of the hand-dict; the SPAWN_FLAGS cross-check
# fixture (F-FIX-9, tests/) uses this map to compare registry-derived posture vs the hand posture for
# every overlapping key. The 18 LOCKED SPAWN_FLAGS rows carry NO `flag` field (they route to a dedicated
# body key) — this map supplies their real Claude flag-name. Values are Atlas-grounded (the flags
# _build_spawn_cmd / the body-key routing actually emit). DATA, consumed by the fixture + the refactor.
SPAWN_FLAG_BODY_KEY_MAP: dict[str, str] = {
    # safe rows (already carry `flag` in SPAWN_FLAGS — repeated here so the map is the single FK source)
    "session_id": "--session-id", "name": "--name", "continue": "--continue",
    "append_system_prompt": "--append-system-prompt",
    "append_system_prompt_file": "--append-system-prompt-file",
    "system_prompt": "--system-prompt", "system_prompt_file": "--system-prompt-file",
    "max_turns": "--max-turns", "max_budget_usd": "--max-budget-usd", "json_schema": "--json-schema",
    "agent": "--agent", "agents": "--agents", "setting_sources": "--setting-sources",
    "no_session_persistence": "--no-session-persistence", "include_hook_events": "--include-hook-events",
    "prompt_suggestions": "--prompt-suggestions", "replay_user_messages": "--replay-user-messages",
    "advisor": "--advisor", "betas": "--betas",
    "exclude_dynamic_system_prompt_sections": "--exclude-dynamic-system-prompt-sections",
    "teammate_mode": "--teammate-mode", "disable_slash_commands": "--disable-slash-commands",
    "debug_file": "--debug-file",
    # consent rows
    "tools": "--tools", "allowed_tools": "--allowedTools", "disallowed_tools": "--disallowedTools",
    "mcp_config": "--mcp-config", "permission_prompt_tool": "--permission-prompt-tool",
    "plugin_dir": "--plugin-dir", "plugin_url": "--plugin-url",
    # locked rows — SPAWN_FLAGS carries NO `flag` for these (they route to a body key); the real flag:
    "input_format": "--input-format", "print": "-p", "verbose": "--verbose",
    "output_format": "--output-format", "include_partial": "--include-partial-messages",
    "resume": "--resume", "fork_session": "--fork-session", "model": "--model", "effort": "--effort",
    "fallback_model": "--fallback-model", "permission_mode": "--permission-mode",
    "settings": "--settings", "add_dir": "--add-dir", "debug": "--debug", "safe_mode": "--safe-mode",
    "bare": "--bare", "dangerously_skip_permissions": "--dangerously-skip-permissions",
    "strict_mcp_config": "--strict-mcp-config",
}


PLATFORM = {
    "id": "claude-code",
    "display_name": "Claude Code",

    # §2.1a executable-locator (Lane A Group 1; implement.py:44, ui_claude_session.py:34-35)
    "executable_locator": {
        "name": "claude", "env_override": "COMPANY_CLAUDE_BIN",
        "which_fallback": True, "known_paths": ["~/.local/bin/claude"],
    },

    # §2.2 invocation kind (Lane A Group 1; session_supervisor.py:741) — selects SubprocessAdapter
    "invocation_kind": "subprocess",

    # §2.3 discovery-sources (Lane A Group 8; Dynamic Capability Registry spec §2.1)
    "discovery_sources": [
        {"type": "cli-help", "command": ["{binary}", "--help"], "stderr_merge": True,
         "format": "commander-options-text", "parse_rule": "option-row", "floor_guard": 30},
        {"type": "stream-init",
         "command": ["{binary}", "-p", ".", "--output-format", "stream-json", "--verbose", "--model", "haiku", "--no-session-persistence"],  # FIX 2026-06-13: -p needs a prompt (".") + --verbose (stream-json requires it) + cheap throwaway model; init fires pre-turn. run_capture pipes no stdin, so a prompt arg is required (was rc=1: no prompt).
         "format": "json-init",
         "event_filter": {"type": "system", "subtype": "init"}, "timeout_s": 20,
         # field_kind_map + metadata_fields: how the live init self-declaration maps to capability
         # kinds (DATA — derived 2026-06-13 from the real init event the binary emitted). Collection
         # fields → one CapabilityEntry per member; metadata = context scalars (skipped). A NEW init
         # field not listed here is gap-surfaced (sdk_event/init.unmapped), never silently dropped.
         "field_kind_map": {"tools": "tool", "slash_commands": "slash_command",
                            "mcp_servers": "mcp_server", "skills": "skill",
                            "plugins": "plugin", "agents": "agent"},
         "metadata_fields": ["type", "subtype", "uuid", "session_id", "cwd", "model",
                             "permissionMode", "output_style", "apiKeySource", "claude_code_version",
                             "fast_mode_state", "analytics_disabled", "product_feedback_disabled",
                             "memory_paths"]},
    ],

    # §2.7 version-source (Lane A Group 8) — the PRIMARY & only freshness key (npm package BANNED)
    "version_source": {"command": ["{binary}", "--version"], "strip_suffix": " (Claude Code)",
                       "format": "semver-stripped"},   # → "2.1.177"

    # §2.4 signal-sets — the classify inputs (Lane A Group 9; spec §3.3, §3.5)
    # transport_invariants is POPULATED BY derive_transport_invariants() at PlatformRegistry load
    # (F-FIX-2) — the list below is the documented expected set, but the registry OVERWRITES it with
    # the LIVE derivation from the registered head_builder thunk (the cache is a projection of the
    # derivation, never the source of truth). Kept here so a row whose template is not-yet-wired still
    # declares a non-empty R1 input (the engine RAISES on an empty R1 set).
    "signal_sets": {
        "transport_invariants_derived_from": "_build_spawn_cmd + body_key_handlers",
        # NOTE: this is the DECLARED fallback set (used only if no head_builder thunk is registered);
        # the registry OVERWRITES it at load with the LIVE derivation (derive_transport_invariants,
        # which applies R6). It reflects the post-R6 truth: --mcp-config / --allowedTools are NOT here
        # (R6 swap-head-defaults → R3 consent); --add-dir is NOT here (dirs capability axis → R3
        # consent). The remaining members are the genuine head locks + body-key-override locks.
        "transport_invariants": [
            "-p", "--input-format", "--output-format", "--verbose", "--permission-mode",
            "--strict-mcp-config",                                     # the unconditional head locks
            "--include-partial-messages", "--resume", "--fork-session", "--model", "--effort",
            "--fallback-model", "--settings", "--debug", "--safe-mode", "--bare",
            "--dangerously-skip-permissions",                          # the body-key-override locks
        ],
        "hazard_name_vocabulary": ["dangerously", "skip", "bypass", "unsafe"],  # binary's OWN naming
        "hazard_scope": "flag_name_only",
        "capability_axes": {
            "tools-builtin": ["--tools", "--allowed-tools", "--allowedTools", "--disallowed-tools",
                              "--disallowedTools"],
            "mcp": ["--mcp-config", "--channels"],
            # dirs axis (FIX 2026-06-13): --add-dir WIDENS the session's filesystem reach (an R3
            # capability axis), so it rides the operator-consent beat — NOT a transport lock. It was
            # previously mis-classified `locked` because it sat in body_key_overrides (which the
            # F-FIX-2 derivation unions into the R1 set, and R1 > R3 wins). Resolution: declare it on
            # the dirs axis HERE and drop it from body_key_overrides below, so R3 CONSENT fires.
            # (Build Map F10.9 FLAG: "--add-dir posture=locked likely wrong→consent".)
            "dirs": ["--add-dir"],
            "permission": ["--permission-prompt-tool"],
            "plugins": ["--plugin-dir", "--plugin-url"],
        },
    },

    # §2.5 consumer-reserved-invariants (Lane A Groups 2, 15; session_supervisor.py:320-350, 382-404)
    "consumer_reserved_invariants": {
        "session_mode_flag": "-p",
        "injection_protocol": {"flag": "--input-format", "value": "stream-json"},
        "output_protocol": {"flag": "--output-format", "value": "stream-json"},
        "verbosity_flag": "--verbose", "strict_tool_server_config": True,
        # the locked flags that own a body key (Lane A Group 15). `kind` is the SpawnFlagAssembler
        # closed-adapter kind (engine-code); `why` is the teaching-refusal text the supervisor emits.
        # These flag-names join the DERIVED R1 set (F-FIX-2 derivation = head ∪ these). NOTE: the two
        # SWAP rows (--mcp-config / --allowedTools) are the consent-overridable head DEFAULTS — they
        # are CONSENT axis members above, not body-key locks here (so they are NOT listed in this
        # block; the cross-check fixture surfaces the head/consent tension explicitly — F-FIX-9).
        "body_key_overrides": {
            "model": {"flag": "--model", "kind": "value", "why": "use the dedicated body key `model`."},
            "effort": {"flag": "--effort", "kind": "value", "why": "use the dedicated body key `effort`."},
            "fallback": {"flag": "--fallback-model", "kind": "csv",
                         "why": "use the dedicated body key `fallback`."},
            "permission_mode": {"flag": "--permission-mode", "kind": "value",
                                "why": "use the dedicated body key `permission_mode` (the fabric's "
                                       "posture law: default plan, acceptEdits opt-in)."},
            "settings": {"flag": "--settings", "kind": "value",
                         "why": "use the dedicated body key `settings`."},
            # NOTE: --add-dir is NOT a body-key lock — it is a `dirs` CAPABILITY-AXIS member (R3
            # CONSENT). It widens the session's filesystem reach, so it rides the operator-consent
            # beat (like --allowedTools / --mcp-config), never a hard transport lock. Declared on
            # signal_sets.capability_axes["dirs"] above; removed from here so the F-FIX-2 derivation
            # does not union it into the R1 locked set (FIX 2026-06-13; Build Map F10.9).
            "resume": {"flag": "--resume", "kind": "value",
                       "why": "use the dedicated body key `resume` (wake) — verbs are routing "
                              "decisions, not raw flags."},
            "fork": {"flag": "--fork-session", "kind": "bool",
                     "why": "use the dedicated body keys `resume`+`fork` (consult) — T4's non-"
                            "destructive copy path."},
            "output_format": {"flag": "--output-format", "kind": "value",
                              "why": "use the dedicated body key `output_format` (defaults to stream-"
                                     "json — the reader's parse contract)."},
            "include_partial": {"flag": "--include-partial-messages", "kind": "bool",
                                "why": "use the dedicated body key `include_partial` (the R5 voice "
                                       "seam's delta stream)."},
            "debug": {"flag": "--debug", "kind": "value",
                      "why": "use the dedicated body key `debug`."},
            "safe_mode": {"flag": "--safe-mode", "kind": "bool",
                          "why": "use the dedicated body key `safe_mode`."},
            "bare": {"flag": "--bare", "kind": "bool", "why": "use the dedicated body key `bare`."},
            "input_format": {"flag": "--input-format", "kind": "value",
                             "why": "--input-format stream-json IS the held-open injection contract "
                                    "(T2) — the fabric cannot drive a session without it."},
            "print": {"flag": "-p", "kind": "bool",
                      "why": "-p is the supervised transport's mode; it is always on."},
            "verbose": {"flag": "--verbose", "kind": "bool",
                        "why": "--verbose is required for the stream-json event surface; always on."},
            "strict_mcp_config": {"flag": "--strict-mcp-config", "kind": "bool",
                                  "why": "strictness is the grounding contract; to run different MCP "
                                         "servers swap `mcp_config` (consent) — strict stays on."},
            "dangerously_skip_permissions": {
                "flag": "--dangerously-skip-permissions", "kind": "bool",
                "why": "permission posture rides the dedicated `permission_mode` key "
                       "(bypassPermissions must be an explicit, visible posture choice — never a "
                       "side-door flag)."},
        },
    },

    # §2.8 invocation-binding (Lane A Groups 2, 6, 7, 11; session_supervisor.py:887-1017)
    "invocation_binding": {
        "invocation_kind": "subprocess", "inject_transport": "stdin-ndjson",
        "user_message_envelope": {"type_field": "type", "type_value": "user",
                                  "role_field": "message.role", "content_path": "message.content"},
        "interrupt_envelope": {"type_field": "type", "type_value": "control_request",
                               "subtype_path": "request.subtype", "subtype_value": "interrupt",
                               "id_field": "request_id"},
        "output_protocol_format": "stream-json",
        "session_init_event": {"type_value": "system", "subtype_value": "init",
                               "session_id_path": "session_id", "version_path": "claude_code_version"},
        "assistant_turn_event": {"type_value": "assistant", "content_path": "message.content"},
        "turn_result_event": {"type_value": "result", "result_path": "result",
                              "is_error_path": "is_error", "session_id_path": "session_id",
                              "num_turns_path": "num_turns"},
        "usage_telemetry_block": {"usage_path": "usage", "cost_path": "total_cost_usd",
                                  "model_usage_path": "modelUsage",
                                  "token_fields": ["input_tokens", "output_tokens",
                                                   "cache_read_input_tokens",
                                                   "cache_creation_input_tokens"]},
        "event_render_registry_ref": "runtime/render_declarations.json",
        "init_signal": {"event_type": "system", "event_subtype": "init", "default_s": 15},
        "session_state_machine": {"states": ["starting", "idle", "busy", "closed"],
                                  "terminal": ["closed"],
                                  "transitions": {"starting->idle": "init_signal",
                                                  "idle->busy": "inject",
                                                  "busy->idle": "turn_result",
                                                  "*->closed": "error|teardown"}},
        "platform_session_id_path": "session_id", "local_handle_prefix": "as-",
        "resume_flag": "--resume", "fork_flag": "--fork-session",
    },

    # §2.x permission_model / tool_surface / tool_server_wiring / resource_governance
    # (Lane A Groups 3/10, 4, 5, 12) — fields are the Lane A instance-data columns verbatim
    "permission_model": {
        "flag": "--permission-mode", "env_override": "COMPANY_FABRIC_PERMISSION", "default": "plan",
        "values": [{"name": "plan", "is_read_only": True, "is_default": True},
                   {"name": "acceptEdits", "is_write": True, "scope": "file"},
                   {"name": "bypassPermissions", "is_write": True, "scope": "all", "hazard": True}],
        "hazard_flag": {"flag": "--dangerously-skip-permissions", "posture": "locked",
                        "hazard_signal": "dangerously-"},
        "profiles": [{"name": "default", "tool_set": "floor", "permission_mode": "plan",
                      "consent_required": False},
                     {"name": "bridge-session", "tool_set": "bridge-session-default",
                      "permission_mode": "acceptEdits", "consent_required": True,
                      "consent_key": "operator_consent"}],
    },
    "tool_surface": {
        "allow_flag": "--allowedTools", "deny_flag": "--disallowedTools", "builtin_flag": "--tools",
        "allowlist_separator": ",", "floor_tool_set": ["mcp__company"],
        "tool_specifiers": ["mcp__company", "Bash", "Read", "Edit", "Glob", "Grep", "WebFetch",
                            "WebSearch"],
        "tool_namespace_convention": {"pattern": "mcp__<server>__<tool>", "separator": "__",
                                      "hyphens": "preserved"},
        "capability_to_tool_grant": {"git": ["Bash"], "lsp": ["Read", "Edit"],
                                     "web": ["WebFetch", "WebSearch"], "edit": ["Edit", "Read"]},
        "rail_boundary_set": {"computer": {"rail": "headless-p-linux"},
                              "browser": {"rail": "headless-p-linux"}},
    },
    "tool_server_wiring": {
        "config_flag": "--mcp-config", "config_format": "json-inline",
        "server_entry_shape": {"protocol": "stdio", "command": "<venv>/python",
                               "args": ["mcp_face/server.py"]},
        "plugin_loader_flags": {"dir_flag": "--plugin-dir", "url_flag": "--plugin-url",
                                "kind": "repeat"},
    },
    "resource_governance": {
        "concurrency_cap": {"env_var": "COMPANY_FABRIC_CONCURRENCY", "default": 3},
        "turn_timeout": {"env_var": "COMPANY_FABRIC_TURN_TIMEOUT_S", "default_s": 900},
        "init_wait": {"env_var": "COMPANY_FABRIC_INIT_WAIT_S", "default_s": 15},
    },

    # §2.9 projection-targets (Dynamic Capability Registry spec §5)
    "projection_targets": ["mcp_tool", "bridge_route", "capabilities_key", "resolver",
                           "supervisor_posture"],
}

# ROW-PURITY (2026-06-14, LANE-SUPERVISOR-REFACTOR). This file is PURE DATA — imports + the one
# `PLATFORM = {...}` dict, NO def/class. The head_builder thunk binding (F-FIX-2 — the consumer's
# zero-arg spawn-head builder the engine derives the R1 transport-invariant set from) USED to live
# here as `_register_head_builder()`, which made the instance row non-pure (a def + a runtime import).
# It moved to platforms/_wiring.py (the bootstrap module, `_`-prefixed so the registry's file-
# discovery skips it). The consumer that needs the LIVE derivation imports that wiring; this row keeps
# only its DECLARED (post-R6-correct) transport_invariants as the fallback. The instance row is now
# the clean template the generalization-proof needs: a second platform copies this shape exactly.
