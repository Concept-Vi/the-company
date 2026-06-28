"""introspection/registry.py — the CapabilityRegistry (Level 2 — the per-platform capability leaf table).
Mirror-Registry System, LANE-REGISTRIES.

ONE row per discovered capability of a platform (CapabilityEntry, contracts/capability_entry.py) —
the flags/slash-commands/tools/settings the live binary self-reports. Binary-discovered, NOT
hand-authored files: "you cannot create(kind='capability_entry') a flag into existence; it is
binary-discovered" (Mirror-Registry Spec §4.3). The SINGLE source all faces (MCP tool / bridge route
/ cap:// resolver) project from.

## F-FIX-1 / PG-D2 — A CACHED MODULE-LEVEL SINGLETON, a NEW pattern, NOT a sibling-registry copy
**This is a deliberate divergence from the sibling registries; a build agent who greps the code WILL
find a contradiction unless it reads this and introspection/AGENTS.md.** The sibling resolver-reached
registries (`skill_registry()`, `context_registry()` at runtime/cognition.py:86,92) are
FRESH-DISCOVER-ON-EACH-CALL factories (their docstrings literally say "fresh each call"); there is NO
`_registry_singleton`, NO `set_skill_registry` anywhere in runtime/. CapabilityRegistry does NOT copy
that pattern. It is a CACHED module-level singleton:

  - `set_capability_registry(reg)` — `Suite.__init__` calls this ONCE, after building the registry.
  - `capability_registry()` — the cap:// resolver (LANE-CAP-WIRE) reaches the registry via this
    accessor; it RAISES fail-loud if unset ("Suite init must call set_capability_registry").

**Why the divergence (the justification — registry-is-truth does not mean re-pay an expensive read):**
binary discovery is EXPENSIVE — it spawns a `claude` subprocess (`--help`) AND a `system/init` scratch
session. Fresh-discover-on-each-call (the sibling pattern) would spawn a process on EVERY cap://
resolution — forbidden here. So the registry is discovered ONCE (at Suite init) and CACHED. The
accessor's SHAPE mirrors `skill_registry()` (a module-level zero-arg function returning the registry),
but the lifetime is cached-singleton, not fresh. **State the divergence; never "fix" the singleton to
match the siblings.**

## What `discover()` does (the read half — LEAD-only live, unit-verified with a stub)
`CapabilityRegistry().discover(platform, ...)` runs the engine's DISCOVER → CLASSIFY over the platform
(introspection.engine.classify_platform) and holds the resulting classified CapabilityEntry rows keyed
by id. The LIVE path spawns the binary (LEAD-only) — `discover(..., discover_fn=stub)` injects fixture
rows for a no-spawn unit verification (C-REG-2 exercises the singleton mechanism with a stub-discovered
registry; C-REG-1 — the live ≥30-flag discovery — is LEAD-verify-queued).

## F-FIX-15 / PG-D3 — store write convention (the cache/stamp) is owned by LANE-REFRESH
The version-stamped projection cache (store/introspection_cache.json) + per-platform
store/<id>.version_stamp are written via direct open() (flat operational files, NOT FsStore CAS).
This registry holds the IN-MEMORY rows; the on-disk cache write is the refresh flow's job (LANE-REFRESH).

## CapabilityEntry id construction (F-FIX-14) — how .get() keys resolve
`entry.id = f"{kind}/{name}"`; for flags `name` INCLUDES the `--` prefix:
`cap://flag/--debug` → rest `"flag/--debug"` → `CapabilityRegistry.get("flag/--debug")`. The
discoverers build ids this way; this registry keys on `entry.id` verbatim.
"""
from __future__ import annotations

from typing import Callable, Optional

from contracts.capability_entry import CapabilityEntry
from contracts.platform_entry import PlatformEntry


class CapabilityRegistry:
    """The in-memory table of one platform's discovered + classified capabilities. Dict-like
    (`reg[id] -> CapabilityEntry`, `id in reg`, `.get(id)`). Built by `discover(platform)` (LEAD-only
    live spawn) or by `discover(platform, discover_fn=stub)` (no-spawn unit verification).

    MULTI-PLATFORM (2026-06-28 — the downstream extension, now built): entries are keyed by the FULL
    NESTED id `<platform_id>/<kind>/<name>` so many platforms coexist with NO collision (codex AND claude
    both having `flag/--model` are distinct keys). `discover(platform)` MERGES a platform's rows in (it no
    longer replaces), so a Suite can discover all registered platforms into ONE registry. `get`/`in`/`[]`
    accept BOTH the full nested id AND the legacy leaf id `<kind>/<name>` (→ resolved against the default
    platform `claude-code`, the transition alias) so existing `cap://flag/--debug` lookups keep working."""

    def __init__(self):
        self.entries: dict[str, CapabilityEntry] = {}   # keyed by FULL nested id: <platform>/<kind>/<name>
        self.platform_id: str = ""                       # the LAST platform discovered (back-compat)
        self.platforms: set[str] = set()                 # all platforms whose rows are held
        self.version: str = ""        # the binary version the rows were discovered from (freshness key)

    def discover(self, platform: PlatformEntry, *, executable: str | None = None,
                 version: str | None = None,
                 discover_fn: Callable[..., list[CapabilityEntry]] | None = None,
                 novel_ids: Optional[set[str]] = None) -> "CapabilityRegistry":
        """DISCOVER + CLASSIFY the platform and hold the rows. LEAD-only when discover_fn is the live
        engine discover (it spawns the binary). A unit verification injects discover_fn=stub returning
        fixture rows + an executable/version override so the classify+hold path runs with NO live
        subprocess. Fails loud on an empty discovery / a sub-floor parse (the engine raises) — never a
        silent empty registry. Mutates + returns self (so `CapabilityRegistry().discover(p)` is a
        one-liner, mirroring `RoleRegistry().discover(dirs)`)."""
        # lazy import: the engine imports the adapters (which import contracts) — keep this module's
        # import side-effect-free (no adapter import at module load), mirroring introspection/__init__.
        from introspection import engine as _engine
        classified = _engine.classify_platform(
            platform, executable=executable, version=version,
            discover_fn=discover_fn, novel_ids=novel_ids)
        self.platform_id = platform.id
        self.platforms.add(platform.id)
        self.version = version if version is not None else ""
        # MERGE (not replace) + key by the FULL nested id; stamp platform_id so attribution is never the
        # default-guess (the any-source correctness fix — entries carry the platform they were discovered from).
        for e in classified:
            e.platform_id = platform.id
            self.entries[f"{platform.id}/{e.id}"] = e
        return self

    def snapshot(self) -> dict:
        """The face-neutral projection (counts by kind + by posture + the rows) — the single shaped
        view the MCP tool / bridge route / cap:// resolver read (engine.project over the held rows)."""
        from introspection import engine as _engine
        snap = _engine.project(list(self.entries.values()))
        snap["platform_id"] = self.platform_id
        snap["version"] = self.version
        return snap

    def by_kind(self, kind: str) -> list[CapabilityEntry]:
        return [e for e in self.entries.values() if e.kind == kind]

    def search(self, query: str) -> list[CapabilityEntry]:
        """Substring match over id/name/description (the MCP capability(op='search') backing). Honours
        the verb-edge layer: only `searchable` entries appear (expose-not-gate default = all searchable)."""
        q = (query or "").lower()
        return [e for e in self.entries.values()
                if e.verbs.searchable and (q in e.id.lower() or q in e.name.lower()
                                           or q in (e.description or "").lower())]

    # --- dict-like (so it IS the capability table for the cap:// resolver + the faces) ---
    # Keys are FULL nested ids (<platform>/<kind>/<name>). _key() resolves an incoming id to the stored
    # key, accepting the legacy leaf id (<kind>/<name>) → default-platform alias, so old lookups still hit.
    _DEFAULT_PLATFORM = "claude-code"

    def _key(self, entry_id: str) -> str | None:
        if entry_id in self.entries:
            return entry_id                                   # already a full nested id
        cand = f"{self._DEFAULT_PLATFORM}/{entry_id}"          # legacy leaf id → default platform alias
        if cand in self.entries:
            return cand
        return None

    def __getitem__(self, entry_id: str) -> CapabilityEntry:
        k = self._key(entry_id)
        if k is None:
            raise KeyError(entry_id)
        return self.entries[k]

    def __contains__(self, entry_id: str) -> bool:
        return self._key(entry_id) is not None

    def __iter__(self):
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self.entries)

    def get(self, entry_id: str, default=None):
        k = self._key(entry_id)
        return self.entries[k] if k is not None else default


# ── F-FIX-1 / PG-D2 — the cached module-level singleton accessor (NEW pattern; SHAPE mirrors ──────────
#    skill_registry(), but the lifetime is cached-singleton, NOT fresh-discover-each-call) ────────────

_registry_singleton: CapabilityRegistry | None = None


def set_capability_registry(reg: CapabilityRegistry) -> None:
    """Install the process-wide CapabilityRegistry. `Suite.__init__` calls this ONCE after building +
    discovering the registry (LANE-CAP-WIRE). Idempotent re-set is allowed (a Suite rebuild replaces
    it); the point is the discover-once-cache lifetime, never a per-call fresh spawn."""
    global _registry_singleton
    _registry_singleton = reg


def capability_registry() -> CapabilityRegistry:
    """Reach the cached CapabilityRegistry (the cap:// resolver's accessor, LANE-CAP-WIRE). FAIL LOUD
    if unset — an unset registry at resolve time means Suite init did not call set_capability_registry,
    a wiring bug, never a silent empty result (registry-is-truth / no-silent-failures law)."""
    if _registry_singleton is None:
        raise RuntimeError(
            "capability_registry not set — Suite init must call set_capability_registry(reg) once "
            "after building the CapabilityRegistry (the cap:// resolver reaches it via this cached "
            "singleton; F-FIX-1 / PG-D2). This is a NEW cached-singleton pattern, NOT the fresh-"
            "discover sibling pattern (skill/context) — binary discovery is too expensive to repeat "
            "per resolution. Fail loud.")
    return _registry_singleton
