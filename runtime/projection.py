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


def _cosine(a, b) -> float:
    """Cosine of two vectors — REPLICATED here (like _tree_distance) so the pure-read floor carries NO
    dependency on nodes/retrieve. Fail-loud on a dim mismatch (zip would truncate to a wrong-but-plausible
    cosine; query + corpus may be embedded by different models → different dims) and on a zero vector
    (ZeroDivisionError — never a fabricated 0). Mirrors nodes/retrieve._cosine byte-for-byte in behaviour."""
    if len(a) != len(b):
        raise ValueError(f"vector dim mismatch: {len(a)} vs {len(b)} (cannot cosine different dims)")
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return float(dot / (na * nb))


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


def _grid_cell(address: str, cap: int = 4) -> tuple:
    """The dyadic (i,j) grid cell of an address — the seed's recursive quadrant subdivision (THE-SEED §1:
    "nesting = recursive subdivision; a path IS a grid coordinate"). Each path segment picks one of 4
    sub-quadrants (stable hash → (bx,by)); d levels → a cell in a 2^d × 2^d grid, built MSB-first so a
    parent's cell CONTAINS its children's. Scheme-agnostic (events carry ui://, run://, raw) — so NOT
    parse_ui_address (that is ui://-only + fail-loud); the same scheme-strip the tree-distance uses.
    Returns (i, j, d) with 0 ≤ i,j < 2^d and d = min(segment-count, cap). Empty address → (0,0,0)."""
    s = address or ""
    if "://" in s:
        s = s.split("://", 1)[1]
    segs = [p for p in s.split("/") if p != ""][:cap]
    i = j = 0
    for seg in segs:
        q = int(hashlib.sha256(seg.encode("utf-8", "replace")).hexdigest()[:8], 16) & 3  # 0..3 quadrant
        i = (i << 1) | (q & 1)
        j = (j << 1) | ((q >> 1) & 1)
    return i, j, len(segs)


def project(events: list, *, binding: dict | None = None, now: datetime | None = None,
            center: str | None = None, limit: int = 0, registry: BindingRegistry | None = None,
            vectors: dict | None = None) -> dict:
    """Events → points, resolved from a BINDING. Pure read; every coordinate read from data the
    event already carries, the divisions resolved from the binding's named source. The CENTRE is a
    variable: default the temporal NOW (radius = age); pass `now=` (the scrubber) to move it into the
    past, or `center=<ui:// address>` to re-centre in space (radius = tree-distance from that address).

    SEMANTIC radius (Group 6 — the CIRCLE): a binding with `radius_from=='semantic'` sets radius =
    MEANING-distance from the centre = 1 - cosine(centre, point), read off the PERSISTED per-space
    vectors the caller passes in via `vectors` ({_addr_of(e) → vector}, incl. the centre's, keyed by
    `center`). project() stays PURE — vectors ride IN like events; the store I/O (store.get_vector over
    the binding's space) is the caller's (the bridge's) job. Fail-loud-legible: a semantic binding with
    no centre vector RAISES (no silent fallback to time). A point with no vector → r=1.0 + r_unknown
    (rim + flagged, never silent-dropped). The cosines are min-max NORMALIZED across the projected set
    for legibility (corpus cosines cluster in a narrow band → raw 1-cos is visually unreadable);
    `radius_normalized` is surfaced so the distortion is never silent."""
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
    radius_from = binding.get("radius_from", "time")  # 'time' | 'semantic' (Group 6) | structural-by-address
    # the centre freed (Tim: "the axes are variables"): a non-'now' center is an ADDRESS — radius becomes
    # STRUCTURAL tree-distance from it (near in the tree = near the centre), UNLESS the binding asks for
    # 'semantic' (cosine meaning-distance, Group 6 — now built, reading the passed-in per-space vectors).
    addr_center = center if (center and center not in ("now", "")) else None
    if addr_center is not None:
        max_dist = max((_tree_distance(addr_center, _addr_of(e)) for e, _ in stamped), default=1) or 1
    else:
        max_dist = 1

    # SEMANTIC precompute (Group 6): cosine(centre, point) for every point that HAS a vector; then a
    # min-max normalization band so near=close is VISIBLE (raw 1-cos clusters unreadably).
    sem = (radius_from == "semantic")
    sem_cos: dict = {}
    sem_cmin = sem_cmax = 0.0
    if sem:
        centre_vec = (vectors or {}).get(addr_center) if addr_center else None
        if centre_vec is None:
            raise ValueError(
                f"semantic radius needs a CENTRE item carrying a vector (center={center!r} has none in "
                f"the binding's space) — fail loud, never a silent fallback to time.")
        for _i, (_e, _t) in enumerate(stamped):
            pv = (vectors or {}).get(_addr_of(_e))
            if pv is not None and len(pv) == len(centre_vec):
                sem_cos[_i] = _cosine(centre_vec, pv)
        # the BAND excludes the CENTRE itself: its cosine is 1.0 (an OUTLIER) — including it makes
        # sem_cmax=1.0, which compresses every real neighbour into the OUTER band and leaves the inner
        # radius empty (the empty-core failure). Normalize over the NON-centre cosines so the nearest
        # real neighbour maps near the origin and the field uses the FULL radius.
        nc = [c for _i, c in sem_cos.items()
              if (stamped[_i][0].get("source_address") or _addr_of(stamped[_i][0])) != addr_center]
        if nc:
            sem_cmin, sem_cmax = min(nc), max(nc)
    sem_norm = sem and (sem_cmax - sem_cmin) > 1e-9

    # THE SQUARE / STRUCTURE half (the seed §1): each point's dyadic (i,j) cell from its address path
    # (recursive quadrant subdivision — a parent cell CONTAINS its children); the grid resolution
    # m = 2^(deepest path, capped); the concentric circles = m/2 ("m/2 circles for an m×m grid"). This
    # replaces the rings:4 hardcode AND the bare depth scalar with the real nested geometry.
    GRID_CAP = 4
    cells = [_grid_cell(_addr_of(e), GRID_CAP) for e, _ in stamped]
    max_d = max((c[2] for c in cells), default=0)
    grid_m = (1 << max_d) if max_d > 0 else 1          # 2^max_d (1 if no addressed events)
    rings = max(grid_m // 2, 1)

    points = []
    for idx, (e, t) in enumerate(stamped):
        kind = e.get("kind") or "?"
        i = _sector_index(kind, sectors, kmap)
        gi, gj, gd = cells[idx]
        ref = str(_addr_of(e) or e.get("summary") or e.get("seq"))
        theta = TAU * (i + 0.08 + 0.84 * _stable_unit(ref)) / n
        age = max((now - t).total_seconds(), 1.0)
        r_unknown = False
        if sem:
            c = sem_cos.get(idx)
            is_centre = (e.get("source_address") or _addr_of(e)) == addr_center
            if is_centre:
                r = 0.0                                              # the query item IS the origin of the field
            elif c is None:
                r, r_unknown = 1.0, True                              # no vector → rim, FLAGGED (not dropped)
            elif sem_norm:
                # non-centre points fill [0.06, 1.0] (a small floor keeps the nearest neighbour just OFF the
                # origin so it reads distinct from the centre dot): nearest cos → 0.06, farthest → 1.0.
                r = 0.06 + 0.94 * (1.0 - (c - sem_cmin) / (sem_cmax - sem_cmin))
                r = min(max(r, 0.0), 1.0)
            else:
                r = 1.0 - c                                          # single value / no spread → raw 1-cos
        elif addr_center is not None:
            r = _tree_distance(addr_center, _addr_of(e)) / max_dist   # structural distance-from-address
        else:
            r = math.log1p(age) / log_max                              # time-from-now
        depth = max(len([s for s in (e.get("address") or "").split("/") if s]) - 1, 0)
        phases = {"day": (t.hour * 3600 + t.minute * 60 + t.second) / 86400.0,
                  "week": (t.weekday() + (t.hour / 24.0)) / 7.0}
        sid = sectors[i] if i < len(sectors) else "?"
        points.append({
            "seq": e.get("seq"), "kind": kind, "sector": sid,
            "theta": round(theta, 5), "r": round(r, 5), "depth": depth,
            "cell": {"i": gi, "j": gj, "d": gd},   # the dyadic structural coordinate (the square half)
            "address": e.get("address") or e.get("source_address") or "",
            "summary": str(e.get("summary") or "")[:140], "ts": e.get("ts"),
            "phases": {k: round(v, 4) for k, v in phases.items()},
            # the EMBEDDABLE key (the source the per-space vector is keyed by) — present only when the event
            # carries one, so a meaning-field can re-centre on the ITEM (not its run:// record address).
            **({"source": e.get("source_address")} if e.get("source_address") else {}),
            # only a SEMANTIC point with no vector carries this (rim + flagged) — additive, absent otherwise
            **({"r_unknown": True} if r_unknown else {}),
        })

    return {
        "center": addr_center or "now", "now": now.isoformat(), "n": n,
        "binding": {"id": binding["id"], "label": binding["label"],
                    "angle_from": binding.get("angle_from"),
                    "radius_from": "semantic" if sem else ("address" if addr_center else radius_from),
                    "order_by": binding.get("order_by", "count"),
                    # semantic only: was the meaning-distance min-max normalized for legibility? (honest —
                    # so 'near=close' is never silently a distorted absolute distance)
                    **({"radius_normalized": sem_norm, "space": binding.get("space")} if sem else {})},
        "bindings": [{"id": b["id"], "label": b["label"]} for b in reg.list()] or
                    [{"id": "raw", "label": "Kinds (raw)"}],
        "sectors": [{"id": s, "label": s, "from": round(TAU * i / n, 5), "to": round(TAU * (i + 1) / n, 5)}
                    for i, s in enumerate(sectors)],
        "rings": rings, "grid": grid_m,   # m/2 concentric circles for the m×m dyadic grid (seed §1)
        "lock": "x = 2*pi/n; n resolves from the binding's source — no hardcoded sectors",
        "points": points, "count": len(points),
    }
