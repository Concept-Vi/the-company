"""runtime/mark_types.py — the file-discovered MARK-TYPE registry (Cognition Engine NEWMOD · M1 · P1).

A MARK is the disposition a mark-pass writes over a corpus unit (Group M): the finding store IS the
marks layer (same shape: `target / mark_type / value / confidence / source_pass / evidence / status`).
A MARK-TYPE is the declared VOCABULARY of `mark_type` — one named KIND of disposition a pass may
write (gold-likelihood · ai-fingerprint · contradiction · corroboration · …). A mark-pass = a
`run_role`/`run_reduce` pass that `append_finding`s with a `mark_type` DRAWN FROM this registry.

## Why a FILE-DISCOVERED registry, not a python dict (the adversary-verified BAR — PART 4.3)
**add-a-row = a FILE, no code edit.** The mark-type vocabulary must be directory-discovered,
file-per-entry + create_*-authorable, EXACTLY like roles/skills/projections — NOT `MARK_TYPES={...}`.
Dropping a `mark_types/<id>.py` makes that disposition kind available to a mark-pass with ZERO code
change. The registry path IS the rule: create the file, never edit a literal.

## Why SELF-CONTAINED (mirrors projections.py — NOT a shared base)
Mirrors the MECHANISM of `runtime/projections.py:ProjectionRegistry` / `runtime/roles.py:RoleRegistry`
/ `runtime/registry.py:NodeRegistry` (`os.listdir`→`importlib`, fail-loud, id==filename, dict-like,
`rediscover`). A STANDALONE copy of that pattern (as projections.py is). The MARK-TYPE row shape is its
own (value-shape + direction), so the validator is mark-type-specific (`_build_mark_type`). (A shared
base for the corpus registries is a FUTURE NEWMOD reuse pass — surfaced, not built.)

## The mark-type schema
Each `mark_types/<id>.py` declares a module-level `MARK_TYPE` dict — a registry ROW:
  - `id`          — required; MUST equal the module name (addressable by file — fail-loud otherwise).
                    The `mark_type` value a mark-pass stamps (e.g. `gold-likelihood`, `ai-fingerprint`).
  - `value_shape` — required; the SHAPE of the mark's `value` field — open vocab string
                    ("score" · "label" · "bool" · "span" · "free"). Lets the render/reduce interpret
                    a mark's value without a hardcoded per-kind branch. DATA, not an enum-in-code.
  - `direction`   — optional; "surface" (this mark SURFACES a unit as gold/signal — positive) |
                    "subtract" (this mark marks NOISE to subtract — the inversion, e.g. ai-fingerprint).
                    The fingerprint-subtraction discipline made DATA (denoising = surfacing, opposite
                    direction). Defaults to "surface". Open vocab.
  - `desc`        — optional; operator-facing one-liner — what this disposition MEANS (render-facing).
Every field except `id`+`value_shape` is OPTIONAL. A malformed entry (no string id / id≠filename /
empty value_shape / unknown field) FAILS LOUD at discovery — never a silent skip (a non-MARK_TYPE /
`_`-file is the one that skips).

## The floor + render-not-judge
A mark-type is DECLARED DATA — a vocabulary, not an action. Reading the registry is a READ (no
resolve/dispatch/approve). The gold-likelihood PROFILE is a READ over findings composed with evidence
(never a stored score the operator can't see-why); a mark DESCRIBES a disposition, the operator can
overrule. A mark-PASS appends a finding (telemetry/index), never a resolve — the floor holds.

## Drift home (SD2 — mirrors projections/AGENTS.md)
`mark_types/AGENTS.md` is the drift home. `tests/mark_types_acceptance.py` asserts every discovered
mark-type is reflected there. A new acceptance suite reflects into STATE.md SUITES via
`Suite.refresh_self_description()`.

## create_*-authorable + the WIRING seam
The `_build_mark_type` gate + clean `discover` make this create_*-authorable: a future
`create_mark_type` (long-term home `runtime/authoring.py` + `Suite.create_mark_type`, mirroring
`create_projection`) reuses THIS gate in a tempdir. That wiring is a SEPARATE coordinated pass.

LAWS honoured: no-hardcoding (mark-types FILE-DISCOVERED, never a literal) · reuse-don't-parallel (mirrors
ProjectionRegistry/RoleRegistry/NodeRegistry) · fail loud (malformed RAISES at discovery; unknown id RAISES
on lookup) · the floor (reading a mark-type is a READ; a mark-pass appends a finding, never resolves).
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass


MARK_TYPE_FIELDS = ("id", "value_shape", "direction", "desc")
DIRECTIONS = ("surface", "subtract")  # OPEN vocab in spirit; these are the two seeded directions.


@dataclass
class MarkType:
    """A discovered mark-type — the declared dict (`spec`) verbatim + typed accessors. `value_shape`
    tells the render/reduce how to read a mark's value; `direction` is surface (positive) vs subtract
    (the inversion/denoising — fingerprint-subtraction)."""
    id: str
    value_shape: str
    spec: dict

    @property
    def direction(self) -> str:
        return self.spec.get("direction") or "surface"

    @property
    def desc(self) -> str | None:
        return self.spec.get("desc")


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_mt_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


def _build_mark_type(name: str, decl: dict) -> MarkType:
    """Validate + build a MarkType. FAIL LOUD on a malformed entry (mirrors _build_projection)."""
    if not isinstance(decl, dict):
        raise TypeError(
            f"mark-type module {name!r}: MARK_TYPE must be a dict, got {type(decl).__name__} — "
            f"fail loud, never a silent malformed mark-type.")
    mid = decl.get("id")
    if not mid or not isinstance(mid, str):
        raise ValueError(
            f"mark-type module {name!r}: MARK_TYPE declares no string `id` — fail loud (never an "
            f"unnamed mark-type).")
    if mid != name:
        raise ValueError(
            f"mark-type module {name!r}: id {mid!r} != module name {name!r} — the id must equal the "
            f"file name (addressable by file, mirroring lenses/roles). Fail loud.")
    unknown = [k for k in decl if k not in MARK_TYPE_FIELDS]
    if unknown:
        raise ValueError(
            f"mark-type {mid!r}: unknown field(s) {unknown} — the schema is {list(MARK_TYPE_FIELDS)}. "
            f"Fail loud (never a silent typo'd field).")
    vs = decl.get("value_shape")
    if not isinstance(vs, str) or not vs:
        raise ValueError(
            f"mark-type {mid!r}: `value_shape` must be a non-empty string (score/label/bool/span/free) "
            f"— how the mark's value is read. Got {vs!r} — fail loud.")
    direction = decl.get("direction")
    if direction is not None and (not isinstance(direction, str) or not direction):
        raise ValueError(
            f"mark-type {mid!r}: `direction` (when present) must be a non-empty string "
            f"(surface=positive | subtract=the inversion). Got {direction!r} — fail loud.")
    return MarkType(id=mid, value_shape=vs, spec=dict(decl))


class MarkTypeRegistry:
    """The file-discovered MARK-TYPE registry — mirrors ProjectionRegistry/RoleRegistry/NodeRegistry
    (the ONE registry mechanism). Dict-like. Adding a mark-type = dropping a `mark_types/<id>.py`
    declaring `MARK_TYPE = {...}`. A mark-pass draws its `mark_type` from `as_records()` (registry-is-
    truth — never fabricate a mark_type)."""

    def __init__(self):
        self.mark_types: dict[str, MarkType] = {}

    def discover(self, dirs: list[str]) -> "MarkTypeRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "MARK_TYPE", None)
                if decl is None:
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "MarkTypeRegistry":
        self.mark_types.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> None:
        self.mark_types[name] = _build_mark_type(name, decl)

    # --- the consumer reads (pure reads — the floor) ---
    def subtractive(self) -> list[MarkType]:
        """The mark-types whose `direction == "subtract"` — the inversion/denoising set
        (fingerprint-subtraction). Sorted by id."""
        return [self.mark_types[k] for k in sorted(self.mark_types)
                if self.mark_types[k].direction == "subtract"]

    def as_records(self) -> list[dict]:
        """The whole mark-type set as plain dicts (the declared spec verbatim) — for cognition_info
        (the mark-pass draws a `mark_type` from here; registry-is-truth)."""
        return [dict(self.mark_types[k].spec) for k in sorted(self.mark_types)]

    # --- dict-like ---
    def __getitem__(self, mid: str) -> MarkType:
        return self.mark_types[mid]

    def __contains__(self, mid: str) -> bool:
        return mid in self.mark_types

    def __iter__(self):
        return iter(self.mark_types)

    def __len__(self) -> int:
        return len(self.mark_types)

    def get(self, mid: str, default=None):
        return self.mark_types.get(mid, default)
