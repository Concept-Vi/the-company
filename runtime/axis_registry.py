"""runtime/axis_registry.py — the file-discovered COORDINATE-AXIS registry (the resolver's axes-are-registries).

An AXIS is one orthogonal dimension of the resolver's COORDINATE (resolve(invariant, coordinate) → surface;
RESOLVER-BUILD.md / RESOLVER-CONTRACT.md): device · viewer · mode · perspective · type · intent · resolution ·
state · posture · register. A surface resolves against ALL axes at once (a point located by its full coordinate);
no axis is #1 (orthogonal, no ranking — Tim's law).

## Why a FILE-DISCOVERED registry (Tim's "axes ARE registries" escalation — the recursive registry-is-truth)
Adding a new AXIS = dropping an `axes/<id>.py` declaring `AXIS = {...}`. ZERO engine code — the coordinate-space
is SELF-EXTENDING in its dimensionality (the system grows new dimensions with a row). The resolver MECHANISM is
list-AGNOSTIC (resolve_slot resolves against whatever coordinate it's handed; runtime/resolver.py) — so this
registry is the coordinate's VOCABULARY, not a switch the resolver branches on. ★ THE AXIS SET HERE IS THE
SURFACE PROJECTION (the device/viewer/… list); the FORMAL ROOT axes (the four-root lock · the 3/1 ·
time-as-meta-axis · whether state/scale/frame are one family) are Tim+fork's vault work — Tim-adjudicated. So
these rows are DATA (swappable); the mechanism survives any root-set Tim settles. Don't assert this list as final.

## The axis schema — each `axes/<id>.py` declares a module-level `AXIS` dict (a ROW):
  - id            — required; MUST equal the module name (addressable by file — fail-loud otherwise).
  - namespace     — required; the coordinate KEY this axis contributes (e.g. 'device' → coordinate.device.*).
  - fields        — optional; {sub_field: KIND} where KIND ∈ continuous | discrete — the resolve mechanism per
                    sub-field (continuous → DERIVE via a relationship-AST; discrete → registry-SELECT). An axis
                    may be MIXED (device: {w:continuous, h:continuous, orient:discrete}). The category-error guard
                    lives here: a discrete sub-field (voice/orient) is NOT a continuous function.
  - value_source  — optional; where the axis VALUE comes from at resolve-time ('live' · a source ref ·
                    'pending' when no value-source exists yet, e.g. viewer.expertise has no operator-mode state).
  - desc          — optional; operator-facing one-liner.
A malformed entry (bad id / id != filename / unknown field / bad fields-kind) FAILS LOUD at discovery.

## KINDS (open vocab in spirit; the two the resolver mechanism honors)
continuous → resolve_slot derives (a relationship-AST over the coordinate; kills breakpoints).
discrete   → resolve_slot registry-selects (a row-lookup by the coordinate's value; also not a hand-variant).

LAWS honoured: no-hardcoding (axes FILE-DISCOVERED, never an enum) · reuse-don't-parallel (mirrors
StackItemTypeRegistry/ItemTypeRegistry/mark_types — the ONE registry mechanism, own row shape) · fail loud ·
the floor (reading an axis is a READ).
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass


AXIS_FIELDS = ("id", "namespace", "fields", "value_source", "desc")
REQUIRED_FIELDS = ("id", "namespace")
KINDS = ("continuous", "discrete")


@dataclass
class Axis:
    """A discovered coordinate-axis — the declared dict (`spec`) verbatim + typed accessors. `fields` maps each
    resolvable sub-field to its KIND (continuous=derive | discrete=select); `value_source` is where its value
    comes from ('pending' = no source wired yet)."""
    id: str
    namespace: str
    spec: dict

    @property
    def fields(self) -> dict:
        return dict(self.spec.get("fields") or {})

    @property
    def value_source(self):
        return self.spec.get("value_source")

    @property
    def desc(self):
        return self.spec.get("desc")


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_ax_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


def _build_axis(name: str, decl: dict) -> Axis:
    """Validate + build an Axis. FAIL LOUD on a malformed entry (mirrors _build_stack_item_type)."""
    if not isinstance(decl, dict):
        raise TypeError(f"axis module {name!r}: AXIS must be a dict, got {type(decl).__name__} — fail loud.")
    aid = decl.get("id")
    if not aid or not isinstance(aid, str):
        raise ValueError(f"axis module {name!r}: declares no string `id` — fail loud (never unnamed).")
    if aid != name:
        raise ValueError(
            f"axis module {name!r}: id {aid!r} != module name {name!r} — id must equal the file name "
            f"(addressable by file). Fail loud.")
    unknown = [k for k in decl if k not in AXIS_FIELDS]
    if unknown:
        raise ValueError(f"axis {aid!r}: unknown field(s) {unknown} — the schema is {list(AXIS_FIELDS)}. Fail loud.")
    ns = decl.get("namespace")
    if not ns or not isinstance(ns, str):
        raise ValueError(f"axis {aid!r}: `namespace` must be a non-empty string (the coordinate key). Fail loud.")
    fields = decl.get("fields")
    if fields is not None:
        if not isinstance(fields, dict) or not fields:
            raise ValueError(f"axis {aid!r}: `fields` (when present) must be a non-empty dict {{sub_field: kind}}. Fail loud.")
        for f, k in fields.items():
            if not isinstance(f, str) or k not in KINDS:
                raise ValueError(
                    f"axis {aid!r}: fields[{f!r}]={k!r} — each kind must be one of {list(KINDS)} "
                    f"(continuous=derive | discrete=select). Fail loud.")
    vs = decl.get("value_source")
    if vs is not None and (not isinstance(vs, str) or not vs):
        raise ValueError(f"axis {aid!r}: `value_source` (when present) must be a non-empty string. Fail loud.")
    return Axis(id=aid, namespace=ns, spec=dict(decl))


class AxisRegistry:
    """The file-discovered coordinate-AXIS registry — mirrors StackItemTypeRegistry's mechanism (the ONE
    registry mechanism), own row shape. Dict-like. Adding an axis = dropping an `axes/<id>.py` declaring
    `AXIS = {...}` — the coordinate-space self-extends, zero engine code."""

    def __init__(self):
        self.axes: dict[str, Axis] = {}

    def discover(self, dirs: list[str]) -> "AxisRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "AXIS", None)
                if decl is None:
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "AxisRegistry":
        self.axes.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> None:
        self.axes[name] = _build_axis(name, decl)

    def as_records(self) -> list[dict]:
        """The whole coordinate vocabulary as plain dicts (the declared specs) — for the resolver/host to read
        the available axes (registry-is-truth; the coordinate's dimensions are DATA)."""
        return [dict(self.axes[k].spec) for k in sorted(self.axes)]

    # --- dict-like ---
    def __getitem__(self, aid: str) -> Axis:
        return self.axes[aid]

    def __contains__(self, aid: str) -> bool:
        return aid in self.axes

    def __iter__(self):
        return iter(self.axes)

    def __len__(self) -> int:
        return len(self.axes)

    def get(self, aid: str, default=None):
        return self.axes.get(aid, default)
