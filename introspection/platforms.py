"""introspection/platforms.py — the PlatformRegistry (Level 2 — the platform table).
Mirror-Registry System, LANE-REGISTRIES.

The file-discovered registry of `PlatformEntry` rows — ONE row per external platform the Company
mirrors (Claude Code is row #1; a REST API / MCP server / vLLM gRPC endpoint join as more rows).
Adding a platform = dropping a `platforms/<id>.py` file declaring a module-level `PLATFORM = {...}`
dict; it self-registers + is queryable. A removed file un-registers on rediscover.

## A STANDALONE COPY of the importlib registry pattern — NOT an imported base (S3)
Per the Build Plan S3 (re-verified against runtime/projections.py:22-27): the five existing
registries (Node/Role/Skill/Context/Projection) each WRITE the importlib discovery pattern again —
there is NO shared `_BaseEntryRegistry` to import. PlatformRegistry follows the SAME discipline: it
re-writes the `os.listdir → spec_from_file_location → exec_module → read a module-level sentinel →
fail-loud on malformed` loop locally (mirroring runtime/roles.py:RoleRegistry.discover EXACTLY),
NOT by importing a base. This is reuse-of-PATTERN, not a fork and not a base-class dependency.

## PG-D5 — each PLATFORM dict is loaded via PlatformEntry.model_validate(dict)
The PlatformEntry sub-models are deeply nested (ExecutableLocator, DiscoverySource[], SignalSets,
ConsumerReservedInvariants, InvocationBinding, PermissionModel, ToolSurface, ToolServerWiring,
VersionSource, ResourceGovernance). `model_validate` validates the whole tree; a novel
discovery_sources[].type / inject_transport / invocation_kind value is a typed Literal → Pydantic
FAILS LOUD at load (F-FIX-12) — the gap-surface, never a silently-configured unrunnable adapter.

## F-FIX-2 — transport_invariants are DERIVED at load, never hand-typed (law: registry-is-truth)
When a discovered platform module registers a head_builder thunk (via
introspection.engine.register_head_builder — its Level-2 module does so at import), the registry
re-populates that platform's `signal_sets.transport_invariants` from
`engine.derived_transport_invariants(entry)` at load time. So even if the row's author hand-typed a
transport_invariants list, the DERIVED set replaces it — the cache is a projection of the derivation,
never a source of truth. If no thunk is registered, the row's declared list stands (a platform whose
consumer template is not yet wired must still declare its R1 input, or classify RAISES — see engine).

## Fail-loud discipline (the registry-family law)
A `platforms/<id>.py` that declares a `PLATFORM` dict that does NOT validate against PlatformEntry
RAISES at discovery (Pydantic ValidationError) — it is NOT silently skipped. A `_`-prefixed file
(e.g. `_probe.py`) is skipped only by the family's `startswith('_')` convention IF it is being used
as scratch; the PG-PG1 probe drops a `platforms/_probe.py` deliberately to prove a malformed field
RAISES — so the probe file is loaded EXPLICITLY by the probe (the dir-discovery skips `_` files, the
probe calls register() directly to exercise the validate path). A file with NO `PLATFORM` sentinel
is not a platform module (mirrors NodeRegistry's `hasattr(mod,'run')` / RoleRegistry's `ROLE` check).

This registry is dict-like (`reg[id] -> PlatformEntry`, `id in reg`, `.get(id)`) so it drops in
wherever a platform table is read.
"""
from __future__ import annotations

import importlib.util
import os

from contracts.platform_entry import PlatformEntry


def _normalize_id(s: str) -> str:
    """Normalize a platform id / module name for the addressable-by-file check: hyphens and
    underscores are equivalent (`claude-code` ⇔ `claude_code`), since a Python module file cannot
    contain a hyphen but the canonical Platform-Registry key is hyphenated. Lower-cased so case is
    not a spurious mismatch."""
    return s.replace("-", "_").lower()


def _load_module(path: str):
    """Load a platforms/<id>.py module by path (mirrors runtime/roles.py:_load_module +
    runtime/registry.py:_load_module — the SAME importlib mechanism, written again per S3)."""
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_platform_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


class PlatformRegistry:
    """The file-discovered platform registry — a STANDALONE copy of the importlib registry pattern
    (S3; NOT an imported base, NOT a fork). Dict-like so it IS the platform table for any reader.
    Adding a platform = dropping a `platforms/<id>.py` declaring `PLATFORM = {...}`."""

    def __init__(self):
        self.platforms: dict[str, PlatformEntry] = {}
        self._dirs: list[str] = []

    def discover(self, dirs: list[str]) -> "PlatformRegistry":
        """Discover every `platforms/<id>.py` that declares a `PLATFORM` dict, validate each via
        PlatformEntry.model_validate (PG-D5), and register it. Mirrors RoleRegistry.discover: a
        `.py` file with no `PLATFORM` sentinel is not a platform module (skipped, like a non-role
        file); a `_`-prefixed file is skipped by the family convention; a malformed `PLATFORM`
        RAISES (Pydantic ValidationError) — never a silent skip of a declared-but-broken row."""
        self._dirs = list(dirs)
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "PLATFORM", None)
                if decl is None:                 # not a platform module (no sentinel) — skip
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "PlatformRegistry":
        """Rebuild from the filesystem (clear + discover) so a REMOVED platform file actually
        un-registers (discover() only adds). Mirrors NodeRegistry/RoleRegistry.rediscover."""
        self.platforms.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> PlatformEntry:
        """Validate a `PLATFORM` dict against PlatformEntry and register it (PG-D5). FAIL LOUD on a
        malformed dict (Pydantic ValidationError propagates — never swallowed) and on an id/file
        mismatch (the row's `id` must equal the file name, so a platform is addressable by file —
        the same discipline RoleRegistry enforces on ROLE['id'] == module name).

        Id/filename normalization: a Python module file CANNOT contain a hyphen, but a platform's
        canonical Platform-Registry key IS hyphenated (`claude-code`, the §7 row id). So the rule is
        `id` must equal the module name with `_`↔`-` normalized (`claude-code` ⇔ `claude_code.py`).
        Anything beyond that hyphen/underscore difference RAISES — the addressable-by-file discipline
        holds (a file `foo.py` can only carry id `foo`/`foo`-with-dashes, never an unrelated id).

        F-FIX-2: after validation, if a head_builder thunk is registered for this platform's id,
        re-derive `signal_sets.transport_invariants` from the live spawn template and overwrite the
        cached list (the derivation is the truth; the row's typed list is a projection of it)."""
        if not isinstance(decl, dict):
            raise TypeError(
                f"platform module {name!r}: PLATFORM must be a dict (the declared PlatformEntry "
                f"shape), got {type(decl).__name__} — fail loud, never a silent malformed platform.")
        entry = PlatformEntry.model_validate(decl)   # PG-D5 — validates the whole nested tree, FAILS LOUD
        if _normalize_id(entry.id) != _normalize_id(name):
            raise ValueError(
                f"platform module {name!r}: PLATFORM id {entry.id!r} does not match module name "
                f"{name!r} (even after `_`↔`-` normalization: {_normalize_id(entry.id)!r} != "
                f"{_normalize_id(name)!r}) — the id must equal the file name (hyphens↔underscores ok), "
                f"so a platform is addressable by file, mirroring node-types / roles. Fail loud.")
        entry = self._derive_invariants(entry)
        self.platforms[entry.id] = entry
        return entry

    @staticmethod
    def _derive_invariants(entry: PlatformEntry) -> PlatformEntry:
        """F-FIX-2 — populate signal_sets.transport_invariants from the DERIVED set if a head_builder
        thunk is registered for this platform (its Level-2 module registers it at import). The engine
        owns the derivation (engine.derived_transport_invariants reads the registered thunk +
        body_key_overrides). Imported lazily so this registry has no import-time dependency on the
        engine module (and no platform-name strings leak in here — the engine binding is generic)."""
        from introspection import engine as _engine
        if entry.id not in _engine._HEAD_BUILDERS:
            return entry   # no live template wired — the row's declared transport_invariants stands
        derived = _engine.derived_transport_invariants(entry)
        new_signal = entry.signal_sets.model_copy(update={"transport_invariants": derived})
        return entry.model_copy(update={"signal_sets": new_signal})

    # --- dict-like (so it IS the platform table for any reader) ---
    def __getitem__(self, platform_id: str) -> PlatformEntry:
        return self.platforms[platform_id]

    def __contains__(self, platform_id: str) -> bool:
        return platform_id in self.platforms

    def __iter__(self):
        return iter(self.platforms)

    def __len__(self) -> int:
        return len(self.platforms)

    def get(self, platform_id: str, default=None):
        return self.platforms.get(platform_id, default)

    def ids(self) -> list[str]:
        return sorted(self.platforms)


# The default discovery dir (~/company/platforms/), resolved relative to the repo root (this file is
# at introspection/platforms.py → repo root is its parent's parent). A caller may pass its own dirs.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLATFORMS_DIR = os.path.join(_REPO_ROOT, "platforms")


def platform_registry(dirs: list[str] | None = None) -> PlatformRegistry:
    """Build + discover a PlatformRegistry over `dirs` (default: ~/company/platforms/).

    NOTE — this is a FRESH-discover factory, the SIBLING-registry shape (like skill_registry()),
    because PlatformEntry rows are CHEAP file reads (no subprocess, no model load). This is the
    OPPOSITE of CapabilityRegistry (introspection/registry.py), which is a CACHED singleton because
    its discovery is EXPENSIVE (spawns the binary). The two registries deliberately use the two
    different patterns — each justified by its discovery cost (see introspection/AGENTS.md F-FIX-1)."""
    return PlatformRegistry().discover(dirs or [PLATFORMS_DIR])
