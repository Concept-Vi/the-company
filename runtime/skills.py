"""runtime/skills.py — the file-discovered SKILL + CONTEXT registries (Concurrent Cognition C 3b).

Tim's scope expansion (2026-06-08): "skills/contexts are registries like anything else
(registry-is-truth)." A role's `input_addresses` can be `skill://<id>` (a reusable unit of
instructions the role reads) or `context://<id>` (a reusable context blob) — set by ADDRESS,
resolved through `runtime/cognition.py:resolve_address` (the C 3/4 extensible seam). This module
is that seam's FIRST real extension: the two registries the resolver dispatches to.

## Why a registry, not a literal (embodies ~/.vi/rules/no-hardcoding.md)
A skill / a context is the same KIND of thing roles, node-types, and edge-kinds are: a declared,
discoverable unit of vocabulary. So it is NOT a literal list in code — it is a FILE-DISCOVERED
registry, EXACTLY mirroring `runtime/roles.py:RoleRegistry` (which itself mirrors
`runtime/registry.py:NodeRegistry`). Adding a skill = dropping a `skills/<id>.py` file; it
self-registers + is addressable as `skill://<id>`. The registry path IS the rule: create it,
never drop the literal. (reuse-don't-parallel: this is the SAME importlib discovery mechanism
RoleRegistry uses — not a new globbing/markdown mechanism, which would be a forked registry.)

## The schemas (minimal + registry-shaped — id + content + a label/description like roles)
Each `skills/<id>.py` declares a module-level `SKILL` dict; each `contexts/<id>.py` a `CONTEXT`
dict. Both share the same minimal shape — a registry ROW:
  - `id`          — required; MUST equal the module name (so it is addressable by file, exactly
                    like a role/node-type — fail-loud otherwise).
  - `content`     — required; the resolvable VALUE. For a skill: the instructions text a role reads
                    as its input. For a context: the reusable context blob. This is what
                    `skill://<id>` / `context://<id>` resolves TO (a read — the floor: no
                    resolve/dispatch, just return the declared content).
  - `label`       — operator-facing short name (optional; like roles have).
  - `description` — operator-facing one-liner (optional; like roles have).
Every field except `id` + `content` is OPTIONAL. A malformed entry (no string id / id≠filename /
no content / unknown field) FAILS LOUD at discovery — never a silent skip (a non-entry/`_`-file is
the one that skips, mirroring RoleRegistry's non-role-module skip).

## Drift home (mirrors roles/AGENTS.md)
`skills/AGENTS.md` + `contexts/AGENTS.md` are the constitutions (drift homes).
`tests/skills_contexts_acceptance.py` asserts every discovered entry is reflected in its drift
home (mirrors how `tests/roles_acceptance.py` guards roles against `roles/AGENTS.md`).

LAWS honoured: no-hardcoding (skills/contexts are FILE-DISCOVERED DATA, never a literal list/dict) ·
reuse-don't-parallel (ONE registry pattern — mirrors RoleRegistry/NodeRegistry EXACTLY, not a fork) ·
fail loud (a malformed entry RAISES at discovery; an unknown id RAISES on lookup — registry-is-truth,
never fabricate) · the floor (resolving an entry is a READ — return its content, no resolve/dispatch).
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass


# the schema field names a skill/context entry MAY declare. `id` + `content` required; rest optional.
# (Both registries share ONE row shape — a registry ROW: an addressable id + its resolvable content.)
ENTRY_FIELDS = ("id", "content", "label", "description")


@dataclass
class Entry:
    """A discovered registry entry — a skill OR a context (they share the row shape). Carries the
    declared dict (`spec`) verbatim + the typed accessors the resolver reads. `content` is what the
    address resolves TO (a read — the floor)."""
    id: str
    content: str
    spec: dict
    kind: str                                    # "skill" | "context" — the scheme this row answers

    @property
    def label(self) -> str:
        return self.spec.get("label") or self.id

    @property
    def description(self) -> str | None:
        return self.spec.get("description")


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_sc_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


def _build_entry(name: str, decl: dict, *, kind: str, attr: str) -> Entry:
    """Validate + build an Entry from a module's declared dict. FAIL LOUD on a malformed entry
    (mirrors RoleRegistry._build_role's TypeError/ValueError-on-declared-but-malformed): a declared
    entry with a bad shape RAISES — it is NOT silently skipped (a non-entry file is the one that
    skips). registry-is-truth: never register a fabricated/unnamed/empty row."""
    if not isinstance(decl, dict):
        raise TypeError(
            f"{kind} module {name!r}: {attr} must be a dict (the declared {kind} schema), got "
            f"{type(decl).__name__} — fail loud, never a silent malformed {kind}.")
    eid = decl.get("id")
    if not eid or not isinstance(eid, str):
        raise ValueError(
            f"{kind} module {name!r}: {attr} declares no string `id` — every {kind} declares its id "
            f"(fail loud; author from the registry, never an unnamed {kind}).")
    if eid != name:
        raise ValueError(
            f"{kind} module {name!r}: {attr} id {eid!r} != module name {name!r} — the id must equal "
            f"the file name (so a {kind} is addressable by file, mirroring roles/node-types). Fail loud.")
    unknown = [k for k in decl if k not in ENTRY_FIELDS]
    if unknown:
        raise ValueError(
            f"{kind} {eid!r}: unknown {kind}-schema field(s) {unknown} — the C 3b schema is "
            f"{list(ENTRY_FIELDS)}. Fail loud (never a silent typo'd field that no consumer reads).")
    content = decl.get("content")
    if not isinstance(content, str) or not content:
        raise ValueError(
            f"{kind} {eid!r}: must declare non-empty string `content` (what {kind}://{eid} resolves "
            f"TO — the instructions/blob a role reads). Got {content!r} — fail loud (never resolve a "
            f"{kind} to an empty/None value).")
    return Entry(id=eid, content=content, spec=dict(decl), kind=kind)


class _BaseEntryRegistry:
    """The file-discovered registry base — mirrors `runtime/roles.py:RoleRegistry` /
    `runtime/registry.py:NodeRegistry` EXACTLY (the ONE registry pattern; not a fork). Dict-like
    (`reg[id] -> Entry`, `id in reg`, `.get(id)`). Adding an entry = dropping a `<dir>/<id>.py` file.

    Subclasses set `KIND` ("skill"|"context") + `ATTR` (the module-level dict name, "SKILL"|"CONTEXT")
    — the ONLY difference between the two registries (same mechanism, two vocabularies)."""
    KIND: str = ""
    ATTR: str = ""

    def __init__(self):
        self.entries: dict[str, Entry] = {}

    def discover(self, dirs: list[str]) -> "_BaseEntryRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, self.ATTR, None)
                if decl is None:                  # not an entry module (mirrors NodeRegistry's `run` check)
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "_BaseEntryRegistry":
        """Rebuild from the filesystem (clear + discover) — so a REMOVED entry file actually
        un-registers (discover() only adds). Mirrors RoleRegistry/NodeRegistry.rediscover."""
        self.entries.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> None:
        self.entries[name] = _build_entry(name, decl, kind=self.KIND, attr=self.ATTR)

    def read(self, entry_id: str) -> str:
        """Read an id → its declared `content` (the READ the address scheme answers — the floor:
        no resolve/dispatch, just return the declared value). NAMED `read` (not `resolve`) on purpose:
        reading a skill/context IS a read, and the cognition layer keeps a dotted-resolve call a
        forbidden-only token (the C9.2 source-invariant — `resolve_run_ref` is a plain function, never
        a dotted-resolve method, for the same reason). So this file is now COVERED by that standing
        source-invariant scan (cognition_governance_acceptance COG_SOURCES) — a future edit here that
        emitted a forbidden verb would fail loud. FAIL LOUD on an unknown id (registry-is-truth —
        NEVER fabricate a missing skill/context)."""
        if entry_id not in self.entries:
            raise ValueError(
                f"unknown {self.KIND} {entry_id!r} — registered {self.KIND}s: {sorted(self.entries)} "
                f"(registry-is-truth: a {self.KIND}://{entry_id} that is not a discovered file does not "
                f"resolve — fail loud, never fabricate).")
        return self.entries[entry_id].content

    # --- dict-like (mirrors RoleRegistry) ---
    def __getitem__(self, entry_id: str) -> Entry:
        return self.entries[entry_id]

    def __contains__(self, entry_id: str) -> bool:
        return entry_id in self.entries

    def __iter__(self):
        return iter(self.entries)

    def get(self, entry_id: str, default=None):
        return self.entries.get(entry_id, default)


class SkillRegistry(_BaseEntryRegistry):
    """The file-discovered SKILL registry — a `skills/<id>.py` declares a module-level `SKILL` dict;
    `skill://<id>` resolves to its `content` (the reusable instructions a role reads as its input)."""
    KIND = "skill"
    ATTR = "SKILL"


class ContextRegistry(_BaseEntryRegistry):
    """The file-discovered CONTEXT registry — a `contexts/<id>.py` declares a module-level `CONTEXT`
    dict; `context://<id>` resolves to its `content` (the reusable context blob a role reads)."""
    KIND = "context"
    ATTR = "CONTEXT"
