"""runtime/projection.py — THE UNIVERSAL PROJECTION (Tim Geldard's equation; built 2026-06-13).

"Free universal rendering of exactly the same points" — every store event ALREADY carries its full
screen position; this module only READS it out (no model calls, no layout engine, no learned
flattening — the floor: pure computation):

  · θ (angle)  = KIND → its sector in the file-discovered projection/ registry (types are ANGULAR
                 divisions; n rows ⇒ sectors of 2π/n each; adding a row REDISTRIBUTES all sectors
                 evenly — the water law). Within-sector spread by a stable content hash.
  · r (radius) = TIME → distance from NOW (the centre — "everything you and I do is relative to
                 the same point of time"). Log-scaled: recent = inner rings; the rings are the
                 inscribed circles.
  · depth      = NESTING → address path-segment count (recursive subdivision; descend = the dual
                 sites legalize).
  · phases     = the timestamp's nested cycles (hour-of-day, day-of-week — "jampacked with cycles")
                 — S4's seed, carried per point from day one.

The lock x = 2π/n (the unit-wrap circle, r = 1/(2π)) keeps angular and radial division commensurate
at every n — congruent cells at every scale. The registry IS the angular geometry: declare a sector
row and the whole screen re-divides. Registry-is-truth, extended to the renderer."""
import fnmatch
import hashlib
import importlib.util
import math
import os
from datetime import datetime, timezone

ROW_FIELDS = ("id", "label", "gathers", "meaning")
TAU = 2 * math.pi


class SectorRegistry:
    """File-discovered sector rows (projection/<id>.py) — the dial-registry pattern, fail-loud."""

    def __init__(self):
        self._rows: list = []

    def discover(self, dirs=("projection",)) -> "SectorRegistry":
        rows = {}
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                stem = fn[:-3]
                spec = importlib.util.spec_from_file_location(f"sector_{stem}", os.path.join(d, fn))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                row = getattr(mod, "SECTOR", None)
                if not isinstance(row, dict):
                    raise ValueError(f"projection row {fn}: no SECTOR dict (fail loud)")
                missing = [f for f in ROW_FIELDS if f not in row]
                if missing or row["id"] != stem:
                    raise ValueError(f"projection row {fn}: missing {missing} or id!=stem (fail loud)")
                rows[stem] = row
        # Deterministic order: catch-all 'field' LAST (it gathers '*'), the rest sorted by id —
        # so specific sectors always claim their kinds before the declared remainder does.
        ordered = sorted([r for r in rows.values() if r["id"] != "field"], key=lambda r: r["id"])
        if "field" in rows:
            ordered.append(rows["field"])
        self._rows = ordered
        return self

    @property
    def rows(self) -> list:
        return list(self._rows)

    def sector_of(self, kind: str) -> int:
        """Index of the first sector whose gathers-patterns match this kind (registry order)."""
        for i, row in enumerate(self._rows):
            for pat in row["gathers"]:
                if fnmatch.fnmatch(kind or "?", pat):
                    return i
        return len(self._rows) - 1  # the declared remainder (field gathers '*' so normally unreached)


def _stable_unit(s: str) -> float:
    """Deterministic 0..1 from content — the within-sector angular spread (no randomness: the
    same point lands at the same angle forever; stability is structural, never engineered)."""
    return int(hashlib.sha256(s.encode("utf-8", "replace")).hexdigest()[:8], 16) / 0xFFFFFFFF


def _parse_ts(ts: str):
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def project(events: list, *, now: datetime | None = None, registry: SectorRegistry | None = None,
            limit: int = 0) -> dict:
    """Events → points. Pure read; every coordinate comes from data the event already carries."""
    reg = registry or SectorRegistry().discover()
    rows = reg.rows
    n = len(rows)
    now = now or datetime.now(timezone.utc)

    # Radius normalization needs the oldest age (log scale, recent = inner).
    stamped = [(e, _parse_ts(e.get("ts") or "")) for e in events]
    stamped = [(e, t) for (e, t) in stamped if t is not None]
    if limit:
        stamped = stamped[-limit:]
    max_age = max((max((now - t).total_seconds(), 1.0) for _, t in stamped), default=1.0)
    log_max = math.log1p(max_age)

    points = []
    for e, t in stamped:
        kind = e.get("kind") or "?"
        i = reg.sector_of(kind)
        ref = str(e.get("address") or e.get("source_address") or e.get("summary") or e.get("seq"))
        # θ: the sector's wedge [i, i+1)·2π/n, spread inside by stable hash (edges left clear: 8%).
        theta = TAU * (i + 0.08 + 0.84 * _stable_unit(ref)) / n
        # r: log-scaled age, 0 = the centre (NOW) … 1 = the oldest ring.
        age = max((now - t).total_seconds(), 1.0)
        r = math.log1p(age) / log_max
        # depth: nesting from the address path (recursive subdivision).
        depth = max(len([s for s in (e.get("address") or "").split("/") if s]) - 1, 0)
        # phases: the timestamp's nested cycles (S4 seed — hour-of-day, day-of-week as 0..1 wraps).
        phases = {"day": (t.hour * 3600 + t.minute * 60 + t.second) / 86400.0,
                  "week": (t.weekday() + (t.hour / 24.0)) / 7.0}
        points.append({
            "seq": e.get("seq"), "kind": kind, "sector": rows[i]["id"],
            "theta": round(theta, 5), "r": round(r, 5), "depth": depth,
            "address": e.get("address") or e.get("source_address") or "",
            "summary": str(e.get("summary") or "")[:140], "ts": e.get("ts"),
            "phases": {k: round(v, 4) for k, v in phases.items()},
        })

    return {
        "center": "now", "now": now.isoformat(), "n": n,
        "sectors": [{"id": r["id"], "label": r["label"], "meaning": r["meaning"],
                     "from": round(TAU * i / n, 5), "to": round(TAU * (i + 1) / n, 5)}
                    for i, r in enumerate(rows)],
        "rings": 4,  # the inscribed circles at the first divisions (the FE may re-divide on zoom)
        "lock": "x = 2*pi/n (unit-wrap circle r = 1/(2*pi)); sectors redistribute evenly with n",
        "points": points, "count": len(points),
    }
