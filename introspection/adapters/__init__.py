"""introspection/adapters/ — the closed-set instance-#1 discovery + invocation adapters (Level 1).
Mirror-Registry System, LANE-INTROSPECTION-CORE.

The engine (introspection/engine.py) selects an adapter by a STABLE selector that arrives as DATA on
a PlatformEntry — DiscoverySource.type for discoverers, InvocationBinding.invocation_kind for
invocation. NO platform-name literals live in any adapter (F-FIX-10 / PG2). The CLI-type instance-#1
adapters built here:

  cli_help.CliHelpDiscoverer        — DiscoverySource.type == "cli-help"   (Commander --help parse)
  stream_init.StreamInitDiscoverer  — DiscoverySource.type == "stream-init" (running-session init event)
  version_probe.VersionProbe        — the freshness-key reader (VersionSource)
  subprocess_invoke.SubprocessAdapter — InvocationKind == "subprocess" (the DISCOVER-side run primitive)

REST / GraphQL / MCP / library / grpc / sdk adapters are NAMED-but-UNBUILT (Build Plan §7
R-ADAPTERS): a PlatformEntry whose discovery_sources[].type selects an unbuilt adapter must FAIL
LOUD naming the missing class (engine.select_discoverer), NEVER a silent empty registry. The closed
DISCOVERERS / INVOKERS maps below are the single registration point — adding a kind is adding a row.
"""
from __future__ import annotations

from introspection.adapters.cli_help import CliHelpDiscoverer
from introspection.adapters.stream_init import StreamInitDiscoverer
from introspection.adapters.version_probe import VersionProbe
from introspection.adapters.subprocess_invoke import SubprocessAdapter

# The CLOSED discovery-adapter set (the built members). The engine keys on DiscoverySource.type.
# A type that is a valid DiscoverySourceType Literal but absent here = a DECLARED-but-UNBUILT adapter
# → the engine FAILS LOUD naming the missing class (the §8.3 gap boundary), never a silent empty read.
DISCOVERERS = {
    CliHelpDiscoverer.source_type: CliHelpDiscoverer,        # "cli-help"
    StreamInitDiscoverer.source_type: StreamInitDiscoverer,  # "stream-init"
}

# The CLOSED invocation-adapter set. The engine keys on InvocationBinding.invocation_kind.
INVOKERS = {
    SubprocessAdapter.invocation_kind: SubprocessAdapter,    # "subprocess"
}

__all__ = ["CliHelpDiscoverer", "StreamInitDiscoverer", "VersionProbe", "SubprocessAdapter",
           "DISCOVERERS", "INVOKERS"]
