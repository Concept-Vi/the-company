"""runtime/stack_item_types.py — the file-discovered CHANNEL-STACK item-type registry (FACE-2 / A4).

A STACK-ITEM-TYPE is a declared KIND of thing the fabric STACKS on a channel for the operator to clear
(presentation · explanation · decision-sequence · verify-request). It is the operator-CYCLE's vocabulary:
the fabric works → stacks typed items → BLOCKED → Tim clears → resume. Each type declares its RENDER +
DISPATCH contract (how its row reads, when it leaves the queue, how a tap opens it) — NOT a lifecycle.

## NOT the board item_types — a DISTINCT registry (different row shape, same mechanism)
`runtime/item_types.py` is the NOTICEBOARD/board registry: rows carry a LIFECYCLE (initial/states/
transitions) — idea/issue/guide/tip/request. THIS registry is the CHANNEL-STACK: rows carry a
RENDER/DISPATCH contract (row_fields + settled-predicate + open_verb). The shapes are genuinely
different (lifecycle vs render-contract), so they are SEPARATE registries — this is the 5th STANDALONE
instance of the ONE file-discovered mechanism (mark_types · item_types · relation_types · roles ·
projections all are), reuse-don't-parallel at the MECHANISM level, each with its OWN row shape. (If a
stack item ALSO wants a board lifecycle later, it composes the two — it does not merge them.)

## Why FILE-DISCOVERED (the locked law): `type` is a REGISTRY REFERENCE, never an enum baked in code.
Adding a stack item-kind = dropping a `stack_item_types/<id>.py` declaring `STACK_ITEM_TYPE = {...}`.
ZERO code change — the operator-cycle's vocabulary self-extends (axes-are-registries). The host
(projection) renders ANY item from this declaration + fail-louds an unlanded type; it holds NO
variant-knowledge (STACK-ITEM-HOST-CONTRACT.md).

## The stack-item-type schema — each `stack_item_types/<id>.py` declares `STACK_ITEM_TYPE` (a ROW):
  - id              — required; MUST equal the module name (addressable by file — fail-loud otherwise).
  - label           — optional; the human kind-name (defaults to id).
  - desc            — optional; operator-facing one-liner (human meaning).
  - row_fields      — optional; {field_name: record_source_path} — the per-type row fields + WHERE each
                      comes from on the item's /api/territory record (STACK-ITEM-HOST-CONTRACT §2).
                      Every value is a dot-path into the record; absent → the row degrades to `name`.
  - unsettled_state — optional; the `state` value that KEEPS the item in the queue (it LEAVES when state
                      != this). Default 'pending' (STACK-ITEM-HOST-CONTRACT §1's settled-predicate).
  - open_verb       — optional; {event: <str>, payload: [<field>, ...]} — the typed open-event a tap
                      dispatches (§3). Absent → the host's generic resolve/spotlight fallback (never a
                      dead tap).
A malformed entry (bad id / id != filename / unknown field / malformed row_fields/open_verb) FAILS LOUD
at discovery — never a silent skip.

LAWS honoured: no-hardcoding (FILE-DISCOVERED) · reuse-don't-parallel (mirrors ItemTypeRegistry's
mechanism, own row shape) · fail loud (malformed RAISES; unknown id RAISES on lookup) · the floor
(reading a stack-item-type is a READ — no resolve/dispatch).
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass


STACK_ITEM_TYPE_FIELDS = ("id", "label", "desc", "row_fields", "unsettled_state", "open_verb")
REQUIRED_FIELDS = ("id",)
DEFAULT_UNSETTLED_STATE = "pending"


@dataclass
class StackItemType:
    """A discovered stack-item-type — the declared dict (`spec`) verbatim + typed accessors. The host
    renders an item of this type from `row_fields` (per-type), shows it while state==`unsettled_state`,
    and opens it via `open_verb` (or the generic fallback)."""
    id: str
    spec: dict

    @property
    def label(self) -> str:
        return self.spec.get("label") or self.id

    @property
    def desc(self):
        return self.spec.get("desc")

    @property
    def row_fields(self) -> dict:
        return dict(self.spec.get("row_fields") or {})

    @property
    def unsettled_state(self) -> str:
        v = self.spec.get("unsettled_state")
        return v if isinstance(v, str) and v else DEFAULT_UNSETTLED_STATE

    @property
    def open_verb(self):
        return self.spec.get("open_verb")


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_sit_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


def _build_stack_item_type(name: str, decl: dict) -> StackItemType:
    """Validate + build a StackItemType. FAIL LOUD on a malformed entry (mirrors _build_item_type)."""
    if not isinstance(decl, dict):
        raise TypeError(
            f"stack-item-type module {name!r}: STACK_ITEM_TYPE must be a dict, got {type(decl).__name__} — fail loud.")
    sid = decl.get("id")
    if not sid or not isinstance(sid, str):
        raise ValueError(f"stack-item-type module {name!r}: declares no string `id` — fail loud (never unnamed).")
    if sid != name:
        raise ValueError(
            f"stack-item-type module {name!r}: id {sid!r} != module name {name!r} — the id must equal the file "
            f"name (addressable by file). Fail loud.")
    unknown = [k for k in decl if k not in STACK_ITEM_TYPE_FIELDS]
    if unknown:
        raise ValueError(
            f"stack-item-type {sid!r}: unknown field(s) {unknown} — the schema is {list(STACK_ITEM_TYPE_FIELDS)}. Fail loud.")
    rf = decl.get("row_fields")
    if rf is not None:
        if not isinstance(rf, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in rf.items()):
            raise ValueError(
                f"stack-item-type {sid!r}: `row_fields` must be a dict of {{field: record_source_path}} strings. "
                f"Got {rf!r} — fail loud.")
    us = decl.get("unsettled_state")
    if us is not None and (not isinstance(us, str) or not us):
        raise ValueError(
            f"stack-item-type {sid!r}: `unsettled_state` (when present) must be a non-empty string. Got {us!r} — fail loud.")
    ov = decl.get("open_verb")
    if ov is not None:
        if not isinstance(ov, dict) or not isinstance(ov.get("event"), str) or not ov.get("event"):
            raise ValueError(
                f"stack-item-type {sid!r}: `open_verb` (when present) must be {{event:<str>, payload?:[<str>...]}}. "
                f"Got {ov!r} — fail loud.")
        pl = ov.get("payload")
        if pl is not None and (not isinstance(pl, list) or not all(isinstance(p, str) for p in pl)):
            raise ValueError(
                f"stack-item-type {sid!r}: `open_verb.payload` (when present) must be a list of field-name strings. "
                f"Got {pl!r} — fail loud.")
    return StackItemType(id=sid, spec=dict(decl))


class StackItemTypeRegistry:
    """The file-discovered CHANNEL-STACK item-type registry — mirrors ItemTypeRegistry's mechanism (the
    ONE registry mechanism), own row shape. Dict-like. Adding a stack item-kind = dropping a
    `stack_item_types/<id>.py` declaring `STACK_ITEM_TYPE = {...}`."""

    def __init__(self):
        self.stack_item_types: dict[str, StackItemType] = {}

    def discover(self, dirs: list[str]) -> "StackItemTypeRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "STACK_ITEM_TYPE", None)
                if decl is None:
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "StackItemTypeRegistry":
        self.stack_item_types.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> None:
        self.stack_item_types[name] = _build_stack_item_type(name, decl)

    def as_records(self) -> list[dict]:
        """The whole set as plain dicts (the declared spec verbatim) — for the bridge to hand the host
        the type vocabulary (registry-is-truth; the host's StackItemType union derives from here)."""
        return [dict(self.stack_item_types[k].spec) for k in sorted(self.stack_item_types)]

    # --- dict-like ---
    def __getitem__(self, sid: str) -> StackItemType:
        return self.stack_item_types[sid]

    def __contains__(self, sid: str) -> bool:
        return sid in self.stack_item_types

    def __iter__(self):
        return iter(self.stack_item_types)

    def __len__(self) -> int:
        return len(self.stack_item_types)

    def get(self, sid: str, default=None):
        return self.stack_item_types.get(sid, default)
