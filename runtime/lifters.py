"""runtime/lifters.py — the file-discovered LIFTER registry (Cognition Engine NEWMOD · P1 · K2).

A LIFTER is a declared **deterministic EXTRACTOR** over a corpus unit — it produces a
`produced_by:"code"` projection (frontmatter / links / blocks) WITHOUT a model call. The corpus
capture (K2) renders the `model` projections via a capture-role; the `code` projections are
produced by these lifters. So a lifter is the CODE half of the projection split: a
`projections/<id>.py` with `produced_by:"code"` (e.g. the seed `lineage` lens) is EXTRACTED by a
matching lifter here.

## Why a FILE-DISCOVERED registry, not a python dict (the adversary-verified BAR — PART 4.3)
The real test of "registry-is-truth": **add-a-row = a FILE, no code edit.** A lifter set must be
directory-discovered, file-per-entry + create_*-authorable, EXACTLY like roles/skills/projections.
So this is NOT `LIFTERS = {...}` — it is `os.listdir` → import a `lifters/<id>.py` per extractor,
each self-registering. Dropping a `lifters/<id>.py` makes that extractor available with ZERO code
change. The registry path IS the rule: create the file, never edit a literal.

## Why SELF-CONTAINED (mirrors projections.py / roles.py — NOT a shared base)
This mirrors the MECHANISM of `runtime/projections.py:ProjectionRegistry` /
`runtime/skills.py:_BaseEntryRegistry` / `runtime/roles.py:RoleRegistry` (all of which mirror
`runtime/registry.py:NodeRegistry`) — `os.listdir` → `importlib` a directory, fail-loud on a
malformed entry, id==filename, dict-like, `rediscover` for removal. A STANDALONE copy of that
pattern, EXACTLY as `projections.py` is. The LIFTER row shape differs (it declares an `extract`
CALLABLE), so the validator is lifter-specific (`_build_lifter`) — mirroring the mechanism, not
copying projection's field set. (A shared base for the eventual corpus registries is a FUTURE
NEWMOD reuse pass — surfaced, not built; roles/skills/projections each carry their own copy, the
established precedent.)

## The lifter schema
Each `lifters/<id>.py` declares a module-level `LIFTER` dict — a registry ROW:
  - `id`        — required; MUST equal the module name (addressable by file, like a role/lens —
                  fail-loud otherwise). The lifter name; matches the `produced_by:"code"`
                  projection it produces (e.g. `lineage`, `links`, `blocks`).
  - `extract`   — required; a CALLABLE `(text:str, *, meta:dict|None=None) -> Any` — the
                  deterministic extractor. It READS the unit and returns the projection value
                  (a structural fact: frontmatter dict, link list, block list). A PARSE is a
                  READ, never a resolve/dispatch — the floor (C9.2) holds.
  - `produces`  — optional; the projection id this lifter feeds (defaults to `id`). Lets a lifter
                  name differ from its target lens if ever needed; the consumer (corpus.py, K2)
                  reads it to route the extracted value to the right `produced_by:"code"` record.
  - `desc`      — optional; operator-facing one-liner (what it extracts, deterministically).
Every field except `id`+`extract` is OPTIONAL. A malformed entry (no string id / id≠filename /
non-callable extract / unknown field) FAILS LOUD at discovery — never a silent skip (a non-LIFTER
/ `_`-file is the one that skips).

## Drift home (SD2 — mirrors projections/AGENTS.md)
`lifters/AGENTS.md` is this registry's constitution (the drift home). `tests/lifters_acceptance.py`
asserts every discovered lifter is reflected in `lifters/AGENTS.md`. A new acceptance suite reflects
into STATE.md's SUITES block via `Suite.refresh_self_description()`.

## create_*-authorable + the WIRING seam
The `_build_lifter` gate + clean `discover` make this registry create_*-authorable: a future
`create_lifter` (long-term home `runtime/authoring.py` + a `Suite.create_lifter`, mirroring
`create_projection`) reuses THIS registry's gate in a tempdir. That wiring is a SEPARATE coordinated
pass — NOT built here. (An executable-code lifter author path is correctly GATED, like node-types.)

LAWS honoured: no-hardcoding (extractors are FILE-DISCOVERED, never a literal dict) · reuse-don't-parallel
(ONE registry mechanism — mirrors ProjectionRegistry/RoleRegistry/NodeRegistry, not a fork) · fail loud
(a malformed lifter RAISES at discovery; an unknown id RAISES on lookup) · the floor (a lifter EXTRACT is
a READ/parse — no resolve/dispatch).
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass


# The schema field names a lifter MAY declare. `id`+`extract` required; rest optional.
LIFTER_FIELDS = ("id", "extract", "produces", "desc")


@dataclass
class Lifter:
    """A discovered code-extractor — the declared dict (`spec`) verbatim + the typed accessors. The
    `extract` callable produces a `produced_by:"code"` projection value deterministically (a READ)."""
    id: str
    spec: dict

    @property
    def extract(self):
        return self.spec["extract"]

    @property
    def produces(self) -> str:
        return self.spec.get("produces") or self.id

    @property
    def desc(self) -> str | None:
        return self.spec.get("desc")


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_lift_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


def _build_lifter(name: str, decl: dict) -> Lifter:
    """Validate + build a Lifter from a module's declared dict. FAIL LOUD on a malformed entry
    (mirrors _build_projection's RAISE-on-declared-but-malformed): a declared LIFTER with a bad shape
    RAISES — never silently skipped (a non-LIFTER file is the one that skips). registry-is-truth."""
    if not isinstance(decl, dict):
        raise TypeError(
            f"lifter module {name!r}: LIFTER must be a dict (the declared extractor schema), got "
            f"{type(decl).__name__} — fail loud, never a silent malformed lifter.")
    lid = decl.get("id")
    if not lid or not isinstance(lid, str):
        raise ValueError(
            f"lifter module {name!r}: LIFTER declares no string `id` — every lifter declares its id "
            f"(fail loud; author from the registry, never an unnamed lifter).")
    if lid != name:
        raise ValueError(
            f"lifter module {name!r}: LIFTER id {lid!r} != module name {name!r} — the id must equal "
            f"the file name (so a lifter is addressable by file, mirroring roles/lenses). Fail loud.")
    unknown = [k for k in decl if k not in LIFTER_FIELDS]
    if unknown:
        raise ValueError(
            f"lifter {lid!r}: unknown lifter-schema field(s) {unknown} — the schema is "
            f"{list(LIFTER_FIELDS)}. Fail loud (never a silent typo'd field that no consumer reads).")
    extract = decl.get("extract")
    if not callable(extract):
        raise ValueError(
            f"lifter {lid!r}: `extract` must be a callable (text, *, meta=None) -> value — the "
            f"deterministic extractor. Got {type(extract).__name__} — fail loud (a lifter with no "
            f"extractor produces no projection).")
    return Lifter(id=lid, spec=dict(decl))


class LifterRegistry:
    """The file-discovered LIFTER registry — mirrors `runtime/projections.py:ProjectionRegistry` /
    `runtime/roles.py:RoleRegistry` / `runtime/registry.py:NodeRegistry` (the ONE registry mechanism;
    not a fork). Dict-like (`reg[id] -> Lifter`, `id in reg`, `.get(id)`, iterate). Adding an extractor
    = dropping a `lifters/<id>.py` declaring `LIFTER = {...}`; it self-registers.

    The corpus capture (K2) reads `for_projection(pid)` to find the extractor for a `produced_by:"code"`
    lens; `as_records()` projects the set (sans the non-serializable callable) for cognition_info."""

    def __init__(self):
        self.lifters: dict[str, Lifter] = {}

    def discover(self, dirs: list[str]) -> "LifterRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "LIFTER", None)
                if decl is None:               # not a lifter module (mirrors NodeRegistry's `run` check)
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "LifterRegistry":
        """Rebuild from the filesystem (clear + discover) — a REMOVED lifter file un-registers.
        Mirrors ProjectionRegistry/RoleRegistry.rediscover."""
        self.lifters.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> None:
        self.lifters[name] = _build_lifter(name, decl)

    # --- the consumer reads (all pure reads — the floor) ---
    def for_projection(self, pid: str) -> Lifter | None:
        """The lifter that produces a given `produced_by:"code"` projection id (K2 routing) — or None
        if no extractor is registered for it (the corpus capture fails loud on a missing one)."""
        for k in sorted(self.lifters):
            if self.lifters[k].produces == pid:
                return self.lifters[k]
        return None

    def as_records(self) -> list[dict]:
        """The lifter set as plain dicts for cognition_info (SURFACE lane) — the `extract` callable is
        replaced by its qualname (a callable can't serialize to a face). registry-is-truth: the
        discovered set, never a hand-listed one."""
        out = []
        for k in sorted(self.lifters):
            spec = dict(self.lifters[k].spec)
            fn = spec.get("extract")
            spec["extract"] = getattr(fn, "__qualname__", repr(fn))
            out.append(spec)
        return out

    # --- dict-like (mirrors ProjectionRegistry) ---
    def __getitem__(self, lid: str) -> Lifter:
        return self.lifters[lid]

    def __contains__(self, lid: str) -> bool:
        return lid in self.lifters

    def __iter__(self):
        return iter(self.lifters)

    def __len__(self) -> int:
        return len(self.lifters)

    def get(self, lid: str, default=None):
        return self.lifters.get(lid, default)
