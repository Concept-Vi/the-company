"""runtime/source_types.py — the file-discovered SOURCE-TYPE registry for the board.

A SOURCE-TYPE is a declared ORIGIN of board records / correlatable history (Tim 2026-06-15: Claude Code
transcripts now; GitHub history later — "it's history/version control… they'll have the same author so
they correlate… matching the schema of each source, declared in the source-type registry"). Stamping
every item with a `source` registry-ref NOW means GitHub (and other coding apps) fold in by a JOIN on
shared keys (author/path/time), NOT a migration. Mirrors the ONE registry mechanism; a STANDALONE copy
(own row shape -> own validator, `_build_source_type`).

## The source-type schema — each `source_types/<id>.py` declares a module-level `SOURCE_TYPE` dict:
  - id        — required; MUST equal the module name.
  - label     — optional; human label.
  - join_keys — optional; the shared keys this source correlates with others on (e.g. author/path/time).
  - desc      — optional; operator-facing one-liner.
A malformed entry FAILS LOUD at discovery.

LAWS honoured: no-hardcoding · reuse-don't-parallel (mirrors RelationTypeRegistry) · fail loud · the floor.
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass


SOURCE_TYPE_FIELDS = ("id", "label", "join_keys", "desc")
REQUIRED_FIELDS = ("id",)


@dataclass
class SourceType:
    id: str
    spec: dict

    @property
    def label(self) -> str:
        return self.spec.get("label") or self.id

    @property
    def join_keys(self) -> list:
        return list(self.spec.get("join_keys") or [])

    @property
    def desc(self):
        return self.spec.get("desc")


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_st_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


def _build_source_type(name: str, decl: dict) -> SourceType:
    """Validate + build a SourceType. FAIL LOUD on a malformed entry."""
    if not isinstance(decl, dict):
        raise TypeError(
            f"source-type module {name!r}: SOURCE_TYPE must be a dict, got {type(decl).__name__} — fail loud.")
    rid = decl.get("id")
    if not rid or not isinstance(rid, str):
        raise ValueError(f"source-type module {name!r}: declares no string `id` — fail loud (never unnamed).")
    if rid != name:
        raise ValueError(
            f"source-type module {name!r}: id {rid!r} != module name {name!r} — the id must equal the "
            f"file name. Fail loud.")
    unknown = [k for k in decl if k not in SOURCE_TYPE_FIELDS]
    if unknown:
        raise ValueError(
            f"source-type {rid!r}: unknown field(s) {unknown} — the schema is {list(SOURCE_TYPE_FIELDS)}. Fail loud.")
    jk = decl.get("join_keys")
    if jk is not None and (not isinstance(jk, list) or not all(isinstance(k, str) for k in jk)):
        raise ValueError(f"source-type {rid!r}: `join_keys` must be a list of strings if present. Got {jk!r} — fail loud.")
    return SourceType(id=rid, spec=dict(decl))


class SourceTypeRegistry:
    """The file-discovered SOURCE-TYPE registry — mirrors RelationTypeRegistry. Dict-like. Adding a
    source = dropping a `source_types/<id>.py` declaring `SOURCE_TYPE = {...}` (e.g. a future github row)."""

    def __init__(self):
        self.source_types: dict[str, SourceType] = {}

    def discover(self, dirs: list[str]) -> "SourceTypeRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "SOURCE_TYPE", None)
                if decl is None:
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "SourceTypeRegistry":
        self.source_types.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> None:
        self.source_types[name] = _build_source_type(name, decl)

    def as_records(self) -> list[dict]:
        return [dict(self.source_types[k].spec) for k in sorted(self.source_types)]

    # --- dict-like ---
    def __getitem__(self, rid: str) -> SourceType:
        return self.source_types[rid]

    def __contains__(self, rid: str) -> bool:
        return rid in self.source_types

    def __iter__(self):
        return iter(self.source_types)

    def __len__(self) -> int:
        return len(self.source_types)

    def get(self, rid: str, default=None):
        return self.source_types.get(rid, default)
