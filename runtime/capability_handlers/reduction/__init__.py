"""runtime/capability_handlers/reduction/ — the SERVICE-SIDE reduction registries (arch §3.2).

Proposal B's idea relocated to where it's TRUE: the per-capability "what each act actually
writes/runs" lives here as DATA, not in the resource-shaped faces. Four registries, by rail:
  config_targets        — R3 .claude file/json-pointer + danger flag + per-scope path each ③ write targets.
  cli_allowlist         — R3 native-CLI argv templates (claude mcp/plugin, git/gh) — argv-array, tiered.
  session_capabilities  — R1-prime in-session rows (liveness:stream, NO typed return_shape; tool grants).
  host_reads            — DECLARATIVE-DIRECT reads (auth redacted, cost fold, routines list).
"""
from runtime.capability_handlers.reduction import config_targets
from runtime.capability_handlers.reduction import cli_allowlist
from runtime.capability_handlers.reduction import session_capabilities
from runtime.capability_handlers.reduction import host_reads

__all__ = ["config_targets", "cli_allowlist", "session_capabilities", "host_reads"]
