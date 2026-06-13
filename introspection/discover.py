"""introspection/discover.py - the DISCOVER verb + adapter dispatch (Level 1, platform-agnostic).
Mirror-Registry System, LANE-INTROSPECTION-CORE.

DISCOVER is the first of the four engine verbs (DISCOVER -> CLASSIFY -> PROJECT -> REFRESH). Given a
PlatformEntry, it:
  1. resolves the executable (via the InvocationKind invoker's find primitive),
  2. for EACH declared DiscoverySource, selects the adapter from the CLOSED DISCOVERERS map by
     src.type, runs it (discover -> parse), and collects the CapabilityEntry rows,
  3. fails LOUD if a declared source selects a DECLARED-but-UNBUILT adapter (the §8.3 gap boundary,
     C-GENPROOF converse) - NEVER a silent empty registry.

ZERO platform-name literals (F-FIX-10 / PG2): the executable name, the discovery commands, the
event filters, the floor guards - all arrive as DATA on the PlatformEntry. This file dispatches on
STABLE selectors (DiscoverySource.type, InvocationKind), never on a platform's identity.
"""
from __future__ import annotations

from contracts.capability_entry import CapabilityEntry
from contracts.platform_entry import PlatformEntry
from introspection.adapters import DISCOVERERS, INVOKERS, VersionProbe


class MissingAdapterError(RuntimeError):
    """A PlatformEntry declared a discovery source / invocation kind whose adapter is NOT built.
    Raised LOUD naming the missing class - never a silent empty registry (Build Plan §8.3, C-GENPROOF
    converse). This is the gap-surface for unbuilt members of the closed adapter set."""


def select_invoker(platform: PlatformEntry):
    """Return the invocation adapter for the platform's invocation_kind, or FAIL LOUD naming the
    missing invoker. The invocation_kind is a typed Literal on PlatformEntry (a novel value already
    fails at model_validate); a VALID-but-UNBUILT kind (rest/graphql/mcp/library) fails here."""
    kind = platform.invocation_kind
    invoker_cls = INVOKERS.get(kind)
    if invoker_cls is None:
        raise MissingAdapterError(
            f"platform {platform.id!r} declares invocation_kind={kind!r} but no invoker is built for "
            f"it. Built invokers: {sorted(INVOKERS)}. Build the {kind!r} invoker (a new row in "
            f"introspection/adapters/INVOKERS) - never run with a silently-absent invoker. Fail loud.")
    return invoker_cls()


def select_discoverer(source_type: str, platform_id: str = ""):
    """Return the discoverer adapter for a DiscoverySource.type, or FAIL LOUD naming the missing
    class. source_type is a typed DiscoverySourceType Literal (a novel value fails at model_validate);
    a VALID-but-UNBUILT type (rest-openapi/mcp-list-tools/graphql-introspect) fails here. This is the
    C-GENPROOF converse: a novel-type platform fails loud naming the missing adapter."""
    discoverer_cls = DISCOVERERS.get(source_type)
    if discoverer_cls is None:
        # Name the expected class so the gap-surface message is actionable (the §8.3 boundary).
        expected = {
            "rest-openapi": "RestOpenApiDiscoverer",
            "mcp-list-tools": "McpListToolsDiscoverer",
            "graphql-introspect": "GraphqlIntrospectionDiscoverer",
        }.get(source_type, f"<discoverer for {source_type!r}>")
        raise MissingAdapterError(
            f"platform {platform_id or '?'!r} declares a discovery source of type {source_type!r} but "
            f"its adapter is NOT built. Built discoverers: {sorted(DISCOVERERS)}. Build the missing "
            f"{expected} (a new row in introspection/adapters/DISCOVERERS) - the engine refuses to "
            f"return a silent empty registry for an unbuilt adapter. Fail loud.")
    return discoverer_cls()


def resolve_executable(platform: PlatformEntry) -> str:
    """Resolve the platform's entry-point via its invoker's find primitive (subprocess: env -> PATH ->
    known_paths, fail loud). Returns the resolved path/name. For invokers without a find primitive
    (future REST: the locator.name IS the base URL), falls back to the locator name."""
    invoker = select_invoker(platform)
    find = getattr(invoker, "find_executable", None)
    if callable(find):
        return find(platform.executable_locator)
    return platform.executable_locator.name


def probe_version(platform: PlatformEntry, executable: str) -> str:
    """Read the running platform version (the freshness key). DATA-driven via VersionSource."""
    return VersionProbe().probe(executable, platform.version_source)


def discover(platform: PlatformEntry, *, executable: str | None = None,
             version: str | None = None) -> list[CapabilityEntry]:
    """Run DISCOVER for a platform: resolve the executable, probe the version, then run EACH declared
    DiscoverySource through its selected adapter and collect the rows. Fails LOUD on an unbuilt adapter
    (the §8.3 boundary) and on a source that yields nothing below its floor_guard (the adapter raises).

    Returns the full CapabilityEntry list (UN-classified - CLASSIFY is a separate verb in engine.py).
    The `executable`/`version` overrides let a caller skip the live probe in a unit test (a stub feeds
    them directly); when omitted they are resolved/probed live (LEAD-only)."""
    if not platform.discovery_sources:
        raise ValueError(
            f"platform {platform.id!r} declares NO discovery_sources - a platform that cannot describe "
            f"itself has no registry. Declare at least one DiscoverySource. Fail loud.")
    exe = executable if executable is not None else resolve_executable(platform)
    ver = version if version is not None else probe_version(platform, exe)
    all_entries: list[CapabilityEntry] = []
    for src in platform.discovery_sources:
        discoverer = select_discoverer(src.type, platform.id)
        raw = discoverer.discover(exe, src)
        entries = discoverer.parse(raw, parse_rule=(src.parse_rule or "option-row"),
                                   platform_id=platform.id, version=ver) \
            if discoverer.source_type == "cli-help" \
            else discoverer.parse(raw, src, platform_id=platform.id, version=ver)
        floor = getattr(src, "floor_guard", 0) or 0
        if floor and len(entries) < floor:
            raise RuntimeError(
                f"platform {platform.id!r} source {src.type!r}: parsed {len(entries)} entries, below "
                f"floor_guard={floor} - a parse that low means a format change or a wrong executable, "
                f"never a clean result. Refusing the partial registry. Fail loud.")
        all_entries.extend(entries)
    return all_entries
