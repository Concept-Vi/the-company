"""runtime/item_types.py — the file-discovered ITEM-TYPE registry for the Company NOTICEBOARD / board.

An ITEM-TYPE is a declared KIND of board record (Tim's "story things": request · issue · tip · guide ·
idea) WITH its own lifecycle (the legal state-machine). Mirrors the ONE registry mechanism
(ProjectionRegistry / RoleRegistry / RelationTypeRegistry): os.listdir -> importlib, fail-loud,
id == filename, dict-like, rediscover. A STANDALONE copy — the ITEM-TYPE row shape is its own (a
per-type lifecycle), so the validator is item-type-specific (`_build_item_type`).

## Why a FILE-DISCOVERED registry, not an inline enum (the locked decision, 2026-06-15)
`type` and `state` are REGISTRY REFERENCES, never `[request|issue|...]` baked into code. Adding a
story-type = dropping an `item_types/<id>.py` declaring `ITEM_TYPE = {...}`. Zero code change. The
per-type LIFECYCLE (legal transitions) lives ON the row — a board item just carries its current
`state`; the legal moves are a property of its type (fields-in-types-referencing-types — the Heart).

## The item-type schema — each `item_types/<id>.py` declares a module-level `ITEM_TYPE` dict (a ROW):
  - id          — required; MUST equal the module name (addressable by file — fail-loud otherwise).
  - initial     — required; the state a freshly-filed item starts in (MUST be in `states`).
  - states      — required; non-empty list of legal state strings.
  - transitions — required; dict {from_state: [allowed to_state, ...]}; every key + every target in `states`.
  - label       — optional; human label.
  - desc        — optional; operator-facing one-liner.
A malformed entry (bad id / id != filename / unknown field / bad states/initial/transitions) FAILS LOUD
at discovery — never a silent skip.

LAWS honoured: no-hardcoding (item-types FILE-DISCOVERED) · reuse-don't-parallel (mirrors
RelationTypeRegistry) · fail loud (malformed RAISES; unknown id RAISES on lookup) · the floor (reading
an item-type is a READ).
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass


ITEM_TYPE_FIELDS = ("id", "initial", "states", "transitions", "label", "desc")
REQUIRED_FIELDS = ("id", "initial", "states", "transitions")


@dataclass
class ItemType:
    """A discovered story-type — the declared dict (`spec`) verbatim + typed accessors. `transitions`
    is the per-type lifecycle (the only truth for what state a board item may move to next)."""
    id: str
    initial: str
    states: list
    transitions: dict
    spec: dict

    @property
    def label(self) -> str:
        return self.spec.get("label") or self.id

    @property
    def desc(self):
        return self.spec.get("desc")

    def legal_from(self, state: str) -> list:
        """The states an item of this type may move to FROM `state` (registry-declared — never hardcoded)."""
        return list(self.transitions.get(state, []))


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_it_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


def _build_item_type(name: str, decl: dict) -> ItemType:
    """Validate + build an ItemType. FAIL LOUD on a malformed entry (mirrors _build_relation_type)."""
    if not isinstance(decl, dict):
        raise TypeError(
            f"item-type module {name!r}: ITEM_TYPE must be a dict, got {type(decl).__name__} — fail loud.")
    rid = decl.get("id")
    if not rid or not isinstance(rid, str):
        raise ValueError(f"item-type module {name!r}: declares no string `id` — fail loud (never unnamed).")
    if rid != name:
        raise ValueError(
            f"item-type module {name!r}: id {rid!r} != module name {name!r} — the id must equal the file "
            f"name (addressable by file). Fail loud.")
    unknown = [k for k in decl if k not in ITEM_TYPE_FIELDS]
    if unknown:
        raise ValueError(
            f"item-type {rid!r}: unknown field(s) {unknown} — the schema is {list(ITEM_TYPE_FIELDS)}. Fail loud.")
    missing = [k for k in REQUIRED_FIELDS if k not in decl]
    if missing:
        raise ValueError(
            f"item-type {rid!r}: missing required field(s) {missing} — a story-type MUST declare "
            f"{list(REQUIRED_FIELDS)} (a lifecycle on the row). Fail loud.")
    states = decl["states"]
    if not isinstance(states, list) or not states or not all(isinstance(s, str) for s in states):
        raise ValueError(f"item-type {rid!r}: `states` must be a non-empty list of strings. Got {states!r} — fail loud.")
    initial = decl["initial"]
    if initial not in states:
        raise ValueError(f"item-type {rid!r}: `initial` {initial!r} is not in `states` {states}. Fail loud.")
    transitions = decl["transitions"]
    if not isinstance(transitions, dict):
        raise ValueError(
            f"item-type {rid!r}: `transitions` must be a dict {{from: [to,...]}}. "
            f"Got {type(transitions).__name__} — fail loud.")
    for frm, tos in transitions.items():
        if frm not in states:
            raise ValueError(f"item-type {rid!r}: transition from unknown state {frm!r} (not in {states}). Fail loud.")
        if not isinstance(tos, list) or not all(isinstance(t, str) for t in tos):
            raise ValueError(f"item-type {rid!r}: transitions[{frm!r}] must be a list of state strings. Got {tos!r} — fail loud.")
        for t in tos:
            if t not in states:
                raise ValueError(
                    f"item-type {rid!r}: transition {frm!r}->{t!r} targets unknown state {t!r} (not in {states}). Fail loud.")
    return ItemType(id=rid, initial=initial, states=list(states), transitions=dict(transitions), spec=dict(decl))


class ItemTypeRegistry:
    """The file-discovered ITEM-TYPE registry — mirrors RelationTypeRegistry (the ONE registry mechanism).
    Dict-like. Adding a story-type = dropping an `item_types/<id>.py` declaring `ITEM_TYPE = {...}`."""

    def __init__(self):
        self.item_types: dict[str, ItemType] = {}

    def discover(self, dirs: list[str]) -> "ItemTypeRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "ITEM_TYPE", None)
                if decl is None:
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "ItemTypeRegistry":
        self.item_types.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> None:
        self.item_types[name] = _build_item_type(name, decl)

    def as_records(self) -> list[dict]:
        return [dict(self.item_types[k].spec) for k in sorted(self.item_types)]

    # --- dict-like ---
    def __getitem__(self, rid: str) -> ItemType:
        return self.item_types[rid]

    def __contains__(self, rid: str) -> bool:
        return rid in self.item_types

    def __iter__(self):
        return iter(self.item_types)

    def __len__(self) -> int:
        return len(self.item_types)

    def get(self, rid: str, default=None):
        return self.item_types.get(rid, default)
