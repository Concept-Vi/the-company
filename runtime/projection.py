"""runtime/projection.py — THE UNIVERSAL PROJECTION (Tim Geldard's equation).

The instrument is a VARIABLE engine: nothing about it is hardcoded — it RESOLVES a frame from a
declared BINDING against the live registries and store. "There is no static value for this
instrument; nothing hardcoded or fixed is valid, only what occupies that variable at that point."
(Tim, 2026-06-13.) So there are no fixed sectors — the angular divisions resolve from whatever
source a binding names, and the DEFAULT is data-driven (the distinct kinds present in the store),
never a privileged hand-written configuration.

The equation's slots, each filled by the binding (a row, swappable):
  · centre  = the origin / object of attention  (default: NOW)
  · angle θ = a categorical/cyclic division     (binding.angle_from → resolves n sectors)
  · radius r= distance from the centre          (binding.radius_from → default: time-from-now)
  · k       = recursive depth                    (nesting; default address depth)
The lock x = 2π/n (unit-wrap) keeps the divisions even: n resolves from the binding's source, and
the wheel re-divides evenly whenever n changes. Pure read (the floor)."""
import fnmatch
import hashlib
import importlib.util
import math
import os
from datetime import datetime, timezone

TAU = 2 * math.pi
BINDING_FIELDS = ("id", "label", "angle_from", "radius_from")


class BindingRegistry:
    """File-discovered BINDINGS (bindings/<id>.py) — the lenses. A binding is a declared filling of
    the equation's slots; it is NOT the sectors themselves (those resolve from angle_from). Adding a
    lens = adding a row. Same registry pattern as dials/roles/relation_types (fail-loud)."""

    def __init__(self):
        self._rows: dict = {}

    def discover(self, dirs=("bindings",)) -> "BindingRegistry":
        rows = {}
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                stem = fn[:-3]
                spec = importlib.util.spec_from_file_location(f"binding_{stem}", os.path.join(d, fn))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                row = getattr(mod, "BINDING", None)
                if not isinstance(row, dict):
                    raise ValueError(f"binding row {fn}: no BINDING dict (fail loud)")
                missing = [f for f in BINDING_FIELDS if f not in row]
                if missing or row["id"] != stem:
                    raise ValueError(f"binding {fn}: missing {missing} or id!=stem (fail loud)")
                rows[stem] = row
        self._rows = rows
        return self

    def get(self, binding_id: str | None) -> dict:
        if binding_id and binding_id in self._rows:
            return self._rows[binding_id]
        # NO privileged hardcode: the default is the data-driven raw-kinds binding, synthesized if
        # no rows are declared at all — the instrument always opens by resolving what's THERE.
        if "raw" in self._rows:
            return self._rows["raw"]
        if self._rows:
            return sorted(self._rows.values(), key=lambda r: r["id"])[0]
        return {"id": "raw", "label": "Kinds (raw)", "angle_from": "kind",
                "radius_from": "time", "order_by": "count"}

    def list(self) -> list:
        return sorted(self._rows.values(), key=lambda r: r["id"])


def _stable_unit(s: str) -> float:
    return int(hashlib.sha256(s.encode("utf-8", "replace")).hexdigest()[:8], 16) / 0xFFFFFFFF


def _parse_ts(ts: str):
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def parse_now(at):
    """Parse the ?at= scrubber value (epoch seconds OR ISO) → an aware datetime, or None (→ real now).
    The scrubber moves the temporal centre into the past; the instrument then projects only ts≤now."""
    if not at:
        return None
    try:
        s = str(at)
        return datetime.fromtimestamp(int(s), tz=timezone.utc) if s.isdigit() else datetime.fromisoformat(s)
    except Exception:
        return None


def _addr_of(e: dict) -> str:
    return e.get("address") or e.get("source_address") or ""


def _tree_distance(a: str, b: str) -> int:
    """ui:// address tree-distance (mirrors suite.address_tree_distance — replicated here so the
    pure-read floor carries NO dependency on the suite). Strip ui://, split on '/', common-prefix
    length, then distance = (len(a)-common)+(len(b)-common): exact 0, parent/child 1, sibling 2."""
    def segs(x: str) -> list:
        x = x or ""
        if x.startswith("ui://"):
            x = x[len("ui://"):]
        return [s for s in x.split("/") if s != ""]
    sa, sb = segs(a), segs(b)
    common = 0
    for x, y in zip(sa, sb):
        if x == y:
            common += 1
        else:
            break
    return (len(sa) - common) + (len(sb) - common)


def _resolve_sectors(binding: dict, events: list) -> tuple[list, dict]:
    """Resolve the angular divisions (sectors) from the binding's angle_from — NOT from a hardcoded
    list. Returns (ordered_sector_ids, kind→sector map). n = len(sectors); the wheel divides evenly.

    angle_from:
      · 'kind'       — one sector per DISTINCT kind in the data (fully data-driven; the true default).
      · 'kind-group' — sectors = binding['groups'] {sector_id: [kind-glob,...]} (a DECLARED lens —
                       one instance, never the default; grouping is a choice, stated as such).
    (Resolving sectors from an arbitrary registry's rows, e.g. roles/operator_memory, needs the
    event→row edge — the relation_types resolution not yet formalized; flagged, not faked. When that
    edge exists, angle_from = a registry name resolves here with no other change.)"""
    af = binding.get("angle_from", "kind")
    order_by = binding.get("order_by", "count")
    if af == "kind-group":
        groups = binding.get("groups") or {}
        order = list(groups.keys())  # declared order
        kmap = {}
        return order, {"__groups__": groups, "__order__": order}
    # 'kind' — data-driven
    counts = {}
    for e in events:
        k = e.get("kind") or "?"
        counts[k] = counts.get(k, 0) + 1
    kinds = list(counts.keys())
    if order_by == "count":
        kinds.sort(key=lambda k: (-counts[k], k))
    else:
        kinds.sort()
    return kinds, {k: k for k in kinds}  # each kind is its own sector


def _sector_index(kind: str, sectors: list, kmap: dict) -> int:
    if "__groups__" in kmap:  # kind-group binding
        groups, order = kmap["__groups__"], kmap["__order__"]
        for i, sid in enumerate(order):
            for pat in groups[sid]:
                if fnmatch.fnmatch(kind or "?", pat):
                    return i
        return len(order) - 1  # the declared remainder (a group must gather '*' to be honest)
    sid = kmap.get(kind, kind)
    return sectors.index(sid) if sid in sectors else len(sectors) - 1


def project(events: list, *, binding: dict | None = None, now: datetime | None = None,
            center: str | None = None, limit: int = 0, registry: BindingRegistry | None = None) -> dict:
    """Events → points, resolved from a BINDING. Pure read; every coordinate read from data the
    event already carries, the divisions resolved from the binding's named source. The CENTRE is a
    variable: default the temporal NOW (radius = age); pass `now=` (the scrubber) to move it into the
    past, or `center=<ui:// address>` to re-centre in space (radius = tree-distance from that address)."""
    reg = registry or BindingRegistry().discover()
    binding = binding or reg.get(None)
    now = now or datetime.now(timezone.utc)

    stamped = [(e, _parse_ts(e.get("ts") or "")) for e in events]
    stamped = [(e, t) for (e, t) in stamped if t is not None]
    # the time scrubber: the centre is NOW (possibly moved into the past via ?at=); only what existed
    # at-or-before that present is projected (events stamped after `now` are the future — not yet real).
    stamped = [(e, t) for (e, t) in stamped if t <= now]
    if limit:
        stamped = stamped[-limit:]

    sectors, kmap = _resolve_sectors(binding, [e for e, _ in stamped])
    n = max(len(sectors), 1)

    max_age = max((max((now - t).total_seconds(), 1.0) for _, t in stamped), default=1.0)
    log_max = math.log1p(max_age) or 1.0
    radius_from = binding.get("radius_from", "time")  # 'time' today; semantic radius = the ability phase
    # the centre freed (Tim: "the axes are variables"): a non-'now' center is an ADDRESS — radius becomes
    # STRUCTURAL tree-distance from it (near in the tree = near the centre). The cosine/semantic relevance
    # ring is the embedder-gated ability phase (Group 6) — stubbed here, never faked.
    addr_center = center if (center and center not in ("now", "")) else None
    if addr_center is not None:
        max_dist = max((_tree_distance(addr_center, _addr_of(e)) for e, _ in stamped), default=1) or 1
    else:
        max_dist = 1

    points = []
    for e, t in stamped:
        kind = e.get("kind") or "?"
        i = _sector_index(kind, sectors, kmap)
        ref = str(_addr_of(e) or e.get("summary") or e.get("seq"))
        theta = TAU * (i + 0.08 + 0.84 * _stable_unit(ref)) / n
        age = max((now - t).total_seconds(), 1.0)
        if addr_center is not None:
            r = _tree_distance(addr_center, _addr_of(e)) / max_dist   # structural distance-from-address
        else:
            r = math.log1p(age) / log_max                              # time-from-now (semantic = Group 6)
        depth = max(len([s for s in (e.get("address") or "").split("/") if s]) - 1, 0)
        phases = {"day": (t.hour * 3600 + t.minute * 60 + t.second) / 86400.0,
                  "week": (t.weekday() + (t.hour / 24.0)) / 7.0}
        sid = sectors[i] if i < len(sectors) else "?"
        points.append({
            "seq": e.get("seq"), "kind": kind, "sector": sid,
            "theta": round(theta, 5), "r": round(r, 5), "depth": depth,
            "address": e.get("address") or e.get("source_address") or "",
            "summary": str(e.get("summary") or "")[:140], "ts": e.get("ts"),
            "phases": {k: round(v, 4) for k, v in phases.items()},
        })

    return {
        "center": addr_center or "now", "now": now.isoformat(), "n": n,
        "binding": {"id": binding["id"], "label": binding["label"],
                    "angle_from": binding.get("angle_from"),
                    "radius_from": "address" if addr_center else radius_from,
                    "order_by": binding.get("order_by", "count")},
        "bindings": [{"id": b["id"], "label": b["label"]} for b in reg.list()] or
                    [{"id": "raw", "label": "Kinds (raw)"}],
        "sectors": [{"id": s, "label": s, "from": round(TAU * i / n, 5), "to": round(TAU * (i + 1) / n, 5)}
                    for i, s in enumerate(sectors)],
        "rings": 4,
        "lock": "x = 2*pi/n; n resolves from the binding's source — no hardcoded sectors",
        "points": points, "count": len(points),
    }
