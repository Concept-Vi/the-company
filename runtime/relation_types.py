"""runtime/relation_types.py — the file-discovered RELATION-TYPE registry (Cognition Engine NEWMOD ·
L3 · P1).

A RELATION-TYPE is a declared KIND of typed/directional edge between two corpus units — the vocabulary
`find_relations` (L3) composes/labels its discovered relations with: `principle-beneath` · `fragment-of`
· `contradicts` · `sibling`. The cross-level query `find_relations(item, near_space, far_space)` =
`query_index(near)` ∩ ¬`query_index(far)` (the inversion-finder); the relation it MARKS is one of these
declared types, with a DIRECTION (some are directed — fragment-of has a parent/child; some symmetric —
sibling).

## Why a FILE-DISCOVERED registry, not a python dict (PART 4.3)
**add-a-row = a FILE, no code edit.** The relation vocabulary must be directory-discovered, file-per-
entry + create_*-authorable, EXACTLY like roles/skills/projections — NOT `RELATION_TYPES={...}`.
Dropping a `relation_types/<id>.py` makes that edge kind available to `find_relations` with ZERO code
change.

## Why SELF-CONTAINED (mirrors projections.py)
Mirrors the MECHANISM of ProjectionRegistry/RoleRegistry/NodeRegistry (`os.listdir`→`importlib`,
fail-loud, id==filename, dict-like, `rediscover`). A STANDALONE copy. The RELATION-TYPE row shape is
its own (directedness + the two space roles), so the validator is relation-type-specific
(`_build_relation_type`).

## The relation-type schema
Each `relation_types/<id>.py` declares a module-level `RELATION_TYPE` dict — a registry ROW:
  - `id`        — required; MUST equal the module name (addressable by file — fail-loud otherwise).
                  The edge kind (`principle-beneath`, `fragment-of`, `contradicts`, `sibling`).
                  *(NB: the file STEM is a python identifier, so a hyphenated edge name lives in `label`;
                  the `id`==stem uses underscores, e.g. `principle_beneath`.)*
  - `directed`  — required bool — is the edge DIRECTED (A→B has a from/to, e.g. fragment-of: child→parent)
                  or SYMMETRIC (sibling: A↔B)? Decides whether `find_relations` records one or both ends.
  - `inverse`   — optional; for a directed edge, the id of its INVERSE relation-type (e.g. fragment-of's
                  inverse "has-fragment"), if the registry declares one. Render/traverse reads it.
  - `near`      — optional; the projection SPACE this relation reads as its NEAR set (the inversion-finder's
                  `query_index(near)`). DATA — which space the edge is computed over.
  - `far`       — optional; the projection SPACE this relation reads as its FAR set (the `¬query_index(far)`).
  - `desc`      — optional; operator-facing one-liner (what the relation MEANS).
Every field except `id`+`directed` is OPTIONAL. A malformed entry (no string id / id≠filename /
non-bool directed / unknown field) FAILS LOUD at discovery — never a silent skip.

## The floor + render-not-judge
A relation-type is DECLARED DATA — a vocabulary, not an action. Reading is a READ (`get`/`as_records`,
never `resolve`). `find_relations` produces a relation (a finding/mark the operator reviews); a relation
DESCRIBES, judgement is a later pass.

## Drift home (SD2) + create_*-authorable + WIRING seam
`relation_types/AGENTS.md` is the drift home; `tests/relation_types_acceptance.py` asserts reflection.
The `_build_relation_type` gate + clean `discover` make it create_*-authorable (a future
`create_relation_type` reusing this gate — a SEPARATE coordinated wiring pass, NOT built here). The
SUITE lane wires `find_relations` to label edges from this registry; that is the next pass.

LAWS honoured: no-hardcoding (relation-types FILE-DISCOVERED, never a literal) · reuse-don't-parallel
(mirrors ProjectionRegistry/RoleRegistry) · fail loud (malformed RAISES; unknown id RAISES on lookup) ·
the floor (reading a relation-type is a READ).
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass


RELATION_TYPE_FIELDS = ("id", "directed", "inverse", "near", "far", "label", "desc")
REQUIRED_FIELDS = ("id", "directed")


@dataclass
class RelationType:
    """A discovered edge kind — the declared dict (`spec`) verbatim + typed accessors. `directed` decides
    whether find_relations records one end or both; `near`/`far` name the spaces the inversion-finder
    set-operates over."""
    id: str
    directed: bool
    spec: dict

    @property
    def inverse(self) -> str | None:
        return self.spec.get("inverse")

    @property
    def near(self) -> str | None:
        return self.spec.get("near")

    @property
    def far(self) -> str | None:
        return self.spec.get("far")

    @property
    def label(self) -> str:
        return self.spec.get("label") or self.id

    @property
    def desc(self) -> str | None:
        return self.spec.get("desc")


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_rt_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


def _build_relation_type(name: str, decl: dict) -> RelationType:
    """Validate + build a RelationType. FAIL LOUD on a malformed entry (mirrors _build_projection)."""
    if not isinstance(decl, dict):
        raise TypeError(
            f"relation-type module {name!r}: RELATION_TYPE must be a dict, got {type(decl).__name__} — "
            f"fail loud, never a silent malformed relation-type.")
    rid = decl.get("id")
    if not rid or not isinstance(rid, str):
        raise ValueError(
            f"relation-type module {name!r}: declares no string `id` — fail loud (never unnamed).")
    if rid != name:
        raise ValueError(
            f"relation-type module {name!r}: id {rid!r} != module name {name!r} — the id must equal the "
            f"file name (addressable by file). Fail loud.")
    unknown = [k for k in decl if k not in RELATION_TYPE_FIELDS]
    if unknown:
        raise ValueError(
            f"relation-type {rid!r}: unknown field(s) {unknown} — the schema is "
            f"{list(RELATION_TYPE_FIELDS)}. Fail loud (never a silent typo'd field).")
    missing = [k for k in REQUIRED_FIELDS if k not in decl]
    if missing:
        raise ValueError(
            f"relation-type {rid!r}: missing required field(s) {missing} — a relation MUST declare "
            f"{list(REQUIRED_FIELDS)} (directed=is-the-edge-directional). Fail loud.")
    directed = decl.get("directed")
    if not isinstance(directed, bool):
        raise ValueError(
            f"relation-type {rid!r}: `directed` must be a bool (directed A→B vs symmetric A↔B — decides "
            f"whether find_relations records one end or both). Got {directed!r} — fail loud.")
    return RelationType(id=rid, directed=directed, spec=dict(decl))


class RelationTypeRegistry:
    """The file-discovered RELATION-TYPE registry — mirrors ProjectionRegistry/RoleRegistry/NodeRegistry
    (the ONE registry mechanism). Dict-like. Adding an edge kind = dropping a `relation_types/<id>.py`
    declaring `RELATION_TYPE = {...}`. `find_relations` labels its discovered edges from `as_records()`
    (registry-is-truth — never fabricate an edge kind)."""

    def __init__(self):
        self.relation_types: dict[str, RelationType] = {}

    def discover(self, dirs: list[str]) -> "RelationTypeRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "RELATION_TYPE", None)
                if decl is None:
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "RelationTypeRegistry":
        self.relation_types.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> None:
        self.relation_types[name] = _build_relation_type(name, decl)

    # --- the consumer reads (pure reads — the floor) ---
    def directed(self) -> list[RelationType]:
        """The DIRECTED relation-types (find_relations records a from/to end). Sorted by id."""
        return [self.relation_types[k] for k in sorted(self.relation_types)
                if self.relation_types[k].directed]

    def symmetric(self) -> list[RelationType]:
        """The SYMMETRIC relation-types (find_relations records both ends). Sorted by id."""
        return [self.relation_types[k] for k in sorted(self.relation_types)
                if not self.relation_types[k].directed]

    def as_records(self) -> list[dict]:
        """The whole relation-type set as plain dicts (the declared spec verbatim) — for cognition_info."""
        return [dict(self.relation_types[k].spec) for k in sorted(self.relation_types)]

    # --- dict-like ---
    def __getitem__(self, rid: str) -> RelationType:
        return self.relation_types[rid]

    def __contains__(self, rid: str) -> bool:
        return rid in self.relation_types

    def __iter__(self):
        return iter(self.relation_types)

    def __len__(self) -> int:
        return len(self.relation_types)

    def get(self, rid: str, default=None):
        return self.relation_types.get(rid, default)
