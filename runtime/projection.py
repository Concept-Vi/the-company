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


def _singular(registry_name: str) -> str:
    """Depluralize a registry NAME → the EVENT FIELD that names its row (the event→row edge convention,
    ONE rule, not a per-registry table): projections→projection, mark_types→mark_type, relation_types→
    relation_type, generation_policies→generation_policy, ai_tics→ai_tic, roles→role, forms→form,
    bindings→binding. (-ies→-y · trailing -s dropped · else unchanged.)"""
    n = registry_name
    if n.endswith("ies"):
        return n[:-3] + "y"
    if n.endswith("s"):
        return n[:-1]
    return n


def _row_of(event: dict, angle_from: str):
    """THE EVENT→ROW EDGE (Group 10), formalized. Which row of the `angle_from` entity-set does this event
    relate to? Two conventions:
      · a GRAPH ('graph' or 'graph:<id>') — the NODE the event touches: `node` · else `from_node` (a
        connect/wire event's SOURCE — the edge itself feeds sector_edges, its source feeds membership).
      · a REGISTRY (any other name, e.g. 'roles'/'projections') — the SINGULAR-field convention: an op.run
        carries `role` (the guide's "op.run → the role that fired"), a corpus.record carries `projection`.
    Returns the row id, or None when the event names no row of that set (→ an honest remainder sector,
    never a forced/fabricated membership)."""
    if angle_from == "graph" or angle_from.startswith("graph:"):
        return event.get("node") or event.get("from_node") or event.get("to_node")
    return event.get(_singular(angle_from))


def _toposort(ids: list, edges: list, key) -> list:
    """ORDER-FROM-EDGES (Group 10 / SEED §79-82: "A precedes B → A before B around the wheel; the linear
    order WRAPPED into a circle"). Kahn topological sort over the DIRECTED edges (from→to) restricted to
    `ids`, with a STABLE deterministic tie-break (`key`) at every ready-step — so the order is reproducible
    across runs AND respects every real edge. A CYCLE's remaining nodes are appended stably (never dropped,
    never an infinite loop — render the order the edges DO determine + the rest by the tie-break). Edges
    touching ids outside the set are ignored (they don't constrain THIS wheel)."""
    from collections import defaultdict
    idset = set(ids)
    indeg = {i: 0 for i in ids}
    adj = defaultdict(list)
    for a, b in edges:
        if a in idset and b in idset and a != b:
            adj[a].append(b)
            indeg[b] += 1
    ready = sorted([i for i in ids if indeg[i] == 0], key=key)
    out = []
    seen = set()
    while ready:
        n = ready.pop(0)
        if n in seen:
            continue
        out.append(n)
        seen.add(n)
        fresh = [m for m in adj[n] if (indeg.__setitem__(m, indeg[m] - 1) or indeg[m] == 0) and m not in seen]
        if fresh:
            ready = sorted(ready + fresh, key=key)
    if len(out) < len(ids):                       # a cycle — append the rest stably (never drop a row)
        out += sorted([i for i in ids if i not in seen], key=key)
    return out


def _resolve_sectors(binding: dict, events: list, *, sector_ids=None, sector_edges=None) -> tuple[list, dict]:
    """Resolve the angular divisions (sectors) from the binding's angle_from — NOT from a hardcoded
    list. Returns (ordered_sector_ids, kmap). n = len(sectors); the wheel divides evenly.

    angle_from:
      · 'kind'       — one sector per DISTINCT kind in the data (fully data-driven; the true default).
      · 'kind-group' — sectors = binding['groups'] {sector_id: [kind-glob,...]} (a DECLARED lens).
      · <registry>/'graph:<id>' (Group 10) — sectors = that entity-set's rows (PRESENT in the data),
        each event mapped to its row via the EVENT→ROW edge (`_row_of`). `sector_ids` (the candidate row
        ids) + `sector_edges` (directed edges among them) are PASSED IN by the caller (registry-is-truth;
        project stays pure). order_by='edge' → `_toposort` over the real edges (SEED §79-82); else by count
        (the honest fallback when an entity-set has NO inter-row edges — SEED §95 growth front). An event
        naming no row → an honest '—' remainder sector (never forced)."""
    af = binding.get("angle_from", "kind")
    order_by = binding.get("order_by", "count")
    if af == "kind-group":
        groups = binding.get("groups") or {}
        order = list(groups.keys())  # declared order
        return order, {"__groups__": groups, "__order__": order}
    if af not in ("kind",):
        # angle_from = a REGISTRY / GRAPH entity-set (Group 10). Sector by the rows PRESENT in the data.
        cand = set(sector_ids or [])
        counts: dict = {}
        unmapped = False
        for e in events:
            row = _row_of(e, af)
            if row is not None and (not cand or row in cand):
                counts[row] = counts.get(row, 0) + 1
            elif row is None:
                # only events that COULD name a row of this set but don't → remainder (a connect/wire event
                # in graph mode legitimately has no single node membership — it is an edge, not a remainder).
                if not (af == "graph" or af.startswith("graph:")) or e.get("kind") != "connect":
                    unmapped = True
        # WHOLE-SET (the connections view, Group 10): a binding may ask to render the ENTIRE registry's rows
        # (the structure + its connections), not only the rows present in the event data — so "the connections
        # in the registries" shows every row + every directional typed edge, even rows no event has touched.
        # Default stays data-driven (present-only, e.g. by_lens). whole_set requires the caller's sector_ids.
        if binding.get("whole_set") and cand:
            ids = sorted(cand)
            unmapped = False                          # the set is the whole registry; nothing is "outside" it
        else:
            ids = list(counts.keys())
        tie = lambda r: (-counts.get(r, 0), str(r))
        if order_by == "edge" and sector_edges:
            ordered = _toposort(ids, list(sector_edges), key=tie)
        else:
            ordered = sorted(ids, key=tie)            # count (default) — the alphabetical sort is retired
        if unmapped:
            ordered = ordered + ["—"]
        return ordered, {"__by__": af}
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
            vectors: dict | None = None, sector_ids: list | None = None,
            sector_edges: list | None = None) -> dict:
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

    sectors, kmap = _resolve_sectors(binding, [e for e, _ in stamped],
                                     sector_ids=sector_ids, sector_edges=sector_edges)
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

    # STRAIN precompute (Group 7, SEED §111: "strain is the distance between a point's square-position and
    # its circle-position"). Compared LIKE-FOR-LIKE as RADII at a shared angle (NOT a 2D cell↔wheel distance:
    # the one-sector angle is pure jitter, so the 2D form is dominated by hash-noise and the centre — the
    # MOST coherent point — would read max-strain). r_struct = tree-distance-from-centre over the SOURCE
    # address (the repo-tree FILING — where it's filed), normalized; strain = |r_struct - r_semantic| (where
    # it's filed vs where it MEANS to be). Centre → 0/0 → strain 0 (coherent); near-in-tree + far-in-meaning
    # → high (divergence). Only in semantic mode (the circle must be MEANING). The wheel-angle registration
    # that would let a true 2D reading work is Group 10's job — not pulled forward.
    sem_struct: dict = {}
    if sem:
        def _is_c(i):
            return (stamped[i][0].get("source_address") or _addr_of(stamped[i][0])) == addr_center
        raw = {i: _tree_distance(addr_center, (e.get("source_address") or _addr_of(e)))
               for i, (e, _t) in enumerate(stamped)}
        # normalize r_struct with the SAME band shape as r_semantic (min-max over NON-centre, 0.06 floor,
        # centre→0) so the two radii are DIRECTLY comparable: a point nearest in BOTH → r==r_struct → strain
        # 0 (coherent); nearest-structural + farthest-semantic → r_struct=0.06 vs r=1.0 → strain ~0.94. Were
        # the two normalized differently, even a coherent point would carry residual strain (a false signal).
        nc_d = [d for i, d in raw.items() if not _is_c(i)]
        dmin, dmax = (min(nc_d), max(nc_d)) if nc_d else (0, 0)
        spread = dmax - dmin
        for i, d in raw.items():
            if _is_c(i):
                sem_struct[i] = 0.0
            elif spread > 1e-9:
                sem_struct[i] = 0.06 + 0.94 * (d - dmin) / spread
            else:
                sem_struct[i] = 0.06          # all non-centre equidistant in the tree → one structural ring

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
        # the angular SECTOR key: by KIND (default/kind-group), or by the EVENT→ROW edge for an
        # angle_from=<registry/graph> binding (Group 10) — an event naming no row → the '—' remainder.
        by = kmap.get("__by__")
        skey = ((_row_of(e, by) if _row_of(e, by) is not None else "—") if by else kind)
        i = _sector_index(skey, sectors, kmap)
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
        # STRAIN (Group 7): the gap between where it's FILED (r_struct, repo-tree distance) and where it
        # MEANS to be (r, semantic). Only meaningful when the circle is semantic; a vectorless point has no
        # meaning-position so it carries no strain (NOT a fabricated 0).
        r_struct = sem_struct.get(idx) if sem else None
        strain = abs(r - r_struct) if (sem and r_struct is not None and not r_unknown) else None
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
            # STRAIN (Group 7) — semantic mode only: where it's FILED (r_struct) vs where it MEANS to be (r),
            # and their gap. The FE draws the radial tension segment r_struct↔r at this angle (SEED §111).
            **({"r_struct": round(r_struct, 5), "strain": round(strain, 5)}
               if strain is not None else {}),
            # only a SEMANTIC point with no vector carries this (rim + flagged) — additive, absent otherwise
            **({"r_unknown": True} if r_unknown else {}),
        })

    # THE CONNECTIONS (Group 10 — "the connections in the registries"): surface the REAL directional typed
    # edges between sectors so the surface can DRAW them (directed chords), not just order by them. Tim's model:
    # every typed edge is DIRECTIONAL with an equal-opposite, and ONLY directional relations type — so each
    # edge is emitted ONCE in its declared direction [from→to] (the equal-opposite is the reverse reading, not
    # a second edge). Mapped to sector INDICES (the FE draws between wedge angles); only edges whose BOTH
    # endpoints are present sectors; self-loops dropped; deduped. `bidir` flags a genuine A→B AND B→A pair (a
    # real 2-cycle / mutual relation — rendered as a cycle, NOT flattened: nonsequential is valid, Tim 495).
    _sidx = {s: i for i, s in enumerate(sectors)}
    _eset = {(a, b) for (a, b) in (sector_edges or []) if a in _sidx and b in _sidx and a != b}
    edges = [{"from": _sidx[a], "to": _sidx[b], **({"bidir": True} if (b, a) in _eset else {})}
             for (a, b) in sorted(_eset)]
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
        "edges": edges,   # the directional typed edges between sectors (directed chords; bidir = a real cycle)
        "rings": rings, "grid": grid_m,   # m/2 concentric circles for the m×m dyadic grid (seed §1)
        "lock": "x = 2*pi/n; n resolves from the binding's source — no hardcoded sectors",
        "points": points, "count": len(points),
    }
