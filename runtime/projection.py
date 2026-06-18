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

# THE KINDS REGISTRY (composition 2026-06-17: "same legibility-type, OWN registry") — human MEANING per event
# kind, read DECLARED-FIRST for the wheel's sectors and rendered by the surface; un-seeded kinds fall back to a
# humanized id so they're still legible. Meaning lives in the DATA (kinds/raw.py), never in the instrument.
# Defensive import: a missing/malformed registry degrades to humanize-only (never breaks projection — fail-soft).
try:
    from kinds.raw import KIND_META as _KIND_META
except Exception:
    _KIND_META = {}
# THE NODE-TYPE legibility registry (the Connections lens, binding=by_node_type — sectors are node TYPES, not
# kinds). SAME legibility-type shape, OWN registry (composition: "ONE legibility-type, MANY registries"). Same
# defensive import — a missing map degrades to humanize-only.
try:
    from nodes._meta import NODE_TYPE_META as _NODE_TYPE_META
except Exception:
    _NODE_TYPE_META = {}
# THE FAMILY legibility registry (the "Activity" lens, binding=grouped — sectors are the 7 declared FAMILIES,
# angle_from="kind-group"). SAME legibility-type shape, OWN registry — and it lives WITH its `groups` definition
# in bindings/grouped.py (the families' meaning beside what they gather). Same defensive import.
try:
    from bindings.grouped import GROUP_META as _GROUP_META
except Exception:
    _GROUP_META = {}
# THE PROJECTION-SPACES legibility registry (the "Ways of looking" lens, binding=by_lens — sectors are the
# corpus SPACES, angle_from="projections"). SAME legibility-type shape; kept in bindings/by_lens.py (NOT a
# projections/_meta.py) because the bridge has runtime/ on sys.path where `import projections` resolves to
# runtime/projections.py (the registry MODULE), so `projections._meta` silently fails — bindings/ has no such
# collision (bindings.grouped already imports clean). Same defensive import.
try:
    from bindings.by_lens import PROJECTION_SPACE_META as _PROJECTION_SPACE_META
except Exception:
    _PROJECTION_SPACE_META = {}

# which declared-meaning registry backs a given sector DOMAIN (binding.angle_from). Each domain maps to its own
# {id: {name, is}} registry; an unmapped domain falls through to humanize-only (still legible, never raw).
_SECTOR_META_BY_DOMAIN = {
    "kind": _KIND_META,
    "node-types": _NODE_TYPE_META,
    "node_types": _NODE_TYPE_META,
    "kind-group": _GROUP_META,
    "projections": _PROJECTION_SPACE_META,
}


def _humanize_kind(kind: str) -> str:
    """Fallback human label for an un-seeded kind/sector id: split on . _ - / and Title-Case (machine-id → words)."""
    import re
    words = re.sub(r"[._\-/]+", " ", str(kind)).strip()
    return words.title() if words else str(kind)


def _kind_name(kind: str, meta: dict = _KIND_META) -> str:
    """DECLARED-first human name (registry meta.name) → humanized-id fallback. The operator never sees a raw
    machine id (Tim's #1 law); declared names are human, the fallback at least reads as words. `meta` selects
    WHICH registry (kinds by default; node-types for the Connections lens)."""
    m = meta.get(kind)
    return (m.get("name") if isinstance(m, dict) else None) or _humanize_kind(kind)


def _kind_meaning(kind: str, meta: dict = _KIND_META):
    """DECLARED one-line meaning (meta.is) for the tapped-sector readout; None if un-seeded (no fabrication).
    `meta` selects which registry (kinds default; node-types for Connections)."""
    m = meta.get(kind)
    return m.get("is") if isinstance(m, dict) else None


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


def _spearman(xs: list, ys: list) -> float:
    """Spearman rank correlation — dependency-free (rank both lists with average-rank ties, then Pearson on
    the ranks). The two-gravity separator's ordering-divergence test reads this. Returns 0.0 for <2 points or
    a zero-variance list (no orderable signal — never a fabricated correlation)."""
    n = len(xs)
    if n < 2 or len(ys) != n:
        return 0.0

    def ranks(vs: list) -> list:
        order = sorted(range(n), key=lambda i: vs[i])
        r = [0.0] * n
        i = 0
        while i < n:                                   # average-rank ties: equal values share their mean rank
            j = i
            while j + 1 < n and vs[order[j + 1]] == vs[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0                   # 1-based average rank over the tie block [i..j]
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    rx, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    vy = math.sqrt(sum((b - my) ** 2 for b in ry))
    if vx == 0 or vy == 0:
        return 0.0
    return float(cov / (vx * vy))


def separation_report(pulls_a: list, pulls_b: list, pole_a: list, pole_b: list, *, refs: list | None = None,
                      distinctness_floor: float = 0.02, spread_floor: float = 0.004) -> dict:
    """THE FIFTH GATE (Group 9 — the two-gravity separator). The four bars (live / all-real-data / drivable /
    interactive) do NOT test whether the field actually SEPARATES: a min-max-normalized radius paints a clean
    gradient over PURE NOISE, so 'it renders and I can drive it' can be true and meaningless at once. This is
    the discriminator that decides ✅, computed on the RAW per-item cosines (BEFORE any normalization —
    normalization always manufactures spread, so it can never be the witness of real separation). Three raw
    facts, ALL required for `separates`:
      1. pole_distinctness = 1 - cos(poleA, poleB) ≥ floor — the two poles must point different ways AT ALL
         (identical poles → no field).
      2. spread_a AND spread_b both ≥ floor — each pole's per-item pull must VARY across the corpus. A pole
         whose cosine is ~constant everywhere is a DEAD pole (noise / uninformative); this catches it. A FLOOR
         to kill the degenerate, NOT a calibrated strength threshold (corpus cosines cluster in a narrow band —
         there is no honest magic 'strong-enough' number to tune against that band).
      3. ordering divergence: Spearman(pulls_a, pulls_b) NOT ≈ +1. Redundant poles rank every item the SAME
         (ρ→+1 → one gravity wearing two hats → FAILS); opposed poles rank inversely (ρ→−1 → two real
         gravities → PASSES); independent poles ρ≈0 → passes. This carries the real two-gravity signal. (An
         earlier draft gated on gap-ranking vs single-pole ranking — that has a false NEGATIVE: maximally
         opposed poles make gap≈−2·cosA, so gap-rank≈cosA-rank, wrongly flagging the BEST case as redundant.)
    Returns the raw facts + `separates` + the leaders toward each pole (spot-check material for the honest gate)."""
    n = len(pulls_a)
    distinct = 1.0 - _cosine(pole_a, pole_b)

    def _std(vs: list) -> float:
        if len(vs) < 2:
            return 0.0
        m = sum(vs) / len(vs)
        return math.sqrt(sum((v - m) ** 2 for v in vs) / len(vs))      # population std of the raw cosines

    sa, sb = _std(pulls_a), _std(pulls_b)
    rho = _spearman(pulls_a, pulls_b)
    gaps = [pulls_b[i] - pulls_a[i] for i in range(n)]                  # signed lean: >0 toward B, <0 toward A
    order = sorted(range(n), key=lambda i: gaps[i])
    lean_a = sum(1 for g in gaps if g < 0)
    lean_b = sum(1 for g in gaps if g > 0)
    # FOURTH degeneracy (alongside distinctness / dead-pole / redundancy): a pole that attracts NOBODY. If every
    # item leans the same way (min(lean_a, lean_b) == 0) the field collapses to a ONE-pole distance — the other
    # pole is not a competing gravity in THIS corpus, so it is not a two-gravity SEPARATION. This is a HARD
    # degeneracy (a count of zero), NOT a tuned threshold against the narrow band — same family as the dead pole.
    # It is what makes the lens-mismatched pair (every code item leaning to the code centroid, balance 162/0)
    # correctly report separates=False, closing the hole where a FORM gating on `separates` green-lights it.
    separates = bool(distinct >= distinctness_floor and sa >= spread_floor and sb >= spread_floor
                     and rho <= 0.9 and min(lean_a, lean_b) >= 1)
    # the BALANCE — how the corpus distributes between the two gravities. The HARD one-sided case (a pole
    # attracting NOBODY) is now a degeneracy folded into `separates` above; the balance still surfaces the
    # DEGREE of skew for the cases that DO separate (a 57/105 real field vs a 6/6 even one) WITHOUT tuning a
    # magic threshold — the operator/FORM reads minority_frac (0.5 = perfectly even, →0 = lopsided) and judges.

    def _pick(idxs: list) -> list:
        return [{"ref": (refs[i] if refs else i), "lean": round(gaps[i], 4),
                 "pull_a": round(pulls_a[i], 4), "pull_b": round(pulls_b[i], 4)} for i in idxs]

    return {
        "separates": separates, "n": n,
        "pole_distinctness": round(distinct, 4), "distinctness_floor": distinctness_floor,
        "spread_a": round(sa, 5), "spread_b": round(sb, 5), "spread_floor": spread_floor,
        "rank_corr": round(rho, 4),                                    # Spearman(pulls_a, pulls_b)
        # the balance: items leaning to A / to B / neutral, and the minority fraction (0.5 = perfectly even,
        # ~0 = one pole wins everywhere). Surfaced, NOT gated — honest legibility of a lopsided field.
        "balance": {"lean_a": lean_a, "lean_b": lean_b, "neutral": n - lean_a - lean_b,
                    "minority_frac": round(min(lean_a, lean_b) / n, 4) if n else 0.0},
        "leaders_a": _pick(order[:5]),                                 # most negative lean (toward pole A)
        "leaders_b": _pick(list(reversed(order[-5:]))),                # most positive lean (toward pole B)
    }


def _normv(v: list) -> list:
    mag = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / mag for x in v]


def _centroid(vs: list) -> list:
    """Unit-normalized mean of a set of vectors (the group's centre direction)."""
    n = len(vs[0])
    c = [0.0] * n
    for v in vs:
        for i in range(n):
            c[i] += v[i]
    return _normv(c)


def nucleation_report(item_vecs: list, item_refs: list, type_vecs: list, type_labels: list,
                      type_radii: list, type_sizes: list, *, dial: float = 0.2, cap: int = 120,
                      ncut: int = 4, perms: int = 80, seed: int = 1729) -> dict:
    """TYPE-NUCLEATION — the 20/80 water-law (Tim Geldard's growth law; all derived work attributed to him).
    Content is typed against a registry of TYPES; what FITS sits INSIDE the square (within a type's own
    empirical extent), what does NOT fit piles up OUTSIDE; where a DISTINCT, coherent pile accumulates past a
    threshold, a NEW TYPE is born. The inverse — a registered type whose membership thins — is a
    (context-dependent) dissolution candidate. No objective, no purpose: a pure read of where the registry
    under-covers its content, and the laws underneath (accumulate→birth, thin→candidacy) are the invariant
    while the specific thresholds bend to the situation (Tim: "it isn't a hard rule that applies in all
    situations but the laws underneath, those are the constant").

    The honesty discipline (mirrors the fifth gate — a normalized gradient over noise is green-paint):
      · MEMBERSHIP (inside vs outside) = the type's OWN admission extent (`type_radii`, e.g. a low percentile of
        each type's member cosines). An item is 'inside' ONLY if it is actually within some type's empirical
        reach. Cross-registry content → mostly/all OUTSIDE (honest: it does not fit) → an empty square + a pile;
        same-registry content → a populated square + the natural outliers. This is NOT a tuned global cosine
        floor and NOT a fit-percentile — either would manufacture a false 'inside' (placing an item in a type
        it does not belong to). Truthful position over a clean ratio.
      · DISTINCTNESS = an apples-to-apples silhouette MARGIN per pile-cluster = mean(member→own-centroid cos)
        − mean(member→nearest-existing-type cos): the members bind to EACH OTHER more than to any existing type
        (→ their own thing, not a sub-region of an existing type). Surfaced as STRENGTH (Tim: "not a hard
        rule"); the binary distinct-vs-noise uses a PILE-PERMUTATION NULL — the margin must beat random
        same-size groupings OF THE PILE (parameter-free, registry-derived; dissolves the margin≈0 knife-edge
        that a bare `margin>0` would flap on).
      · BIRTH (the 20/80 dial) = a DISTINCT candidate is BORN a new type once its mass passes the threshold
        (`dial` × median existing-type size); below it a distinct cluster is still FORMING. The dial is Tim's
        surfaced 20/80 — it moves the BIRTH line, it does NOT decide membership ("a type is born when a region
        fills past ~20/80").
      · DISSOLUTION = registered types whose mass sits in the low tail (< half the median type size) → surfaced
        as candidates, FLAGGED context-dependent (a sparse type may be rare-not-wrong) — never auto-applied.

    Bounded (agglomerate is O(n³) — never cluster a whole corpus blindly): clusters at most `cap` worst-fitting
    pile items; the un-clustered tail is SURFACED (`pile_tail`), never silently dropped. Deterministic (fixed
    `seed` for the null). Returns the report + `per_item` placement (sector + radius) the projection reads."""
    from runtime import scale  # lazy — the pure floor pulls the (dependency-free) clusterer only on demand
    import random as _random
    T = len(type_vecs)
    if T == 0:
        raise ValueError("nucleation needs a registry of TYPES (type_vecs is empty) — fail loud, never a "
                         "one-type or zero-type field; a registry of nothing cannot be under-covered.")
    N = len(item_vecs)
    med_type_size = sorted(type_sizes)[len(type_sizes) // 2] if type_sizes else 1
    dissolve_floor = med_type_size / 2.0                     # the low-tail dissolution band (context-dependent)
    # birth_mass (the 20/80 BIRTH threshold) is set below once the examined pile size is known — Tim's "a region
    # fills past ~20/80": a candidate is born once it holds a `dial`-fraction of the pile being examined, so the
    # dial genuinely MOVES the born/forming line (a fixed multiple of a type size barely bit — distinctness
    # dominated and the dial was inert).

    # FIT every item to its nearest registered type; MEMBERSHIP by that type's own admission extent (truthful).
    best_fit = [0.0] * N
    assigned = [0] * N
    inside = [False] * N
    for i, v in enumerate(item_vecs):
        bi, bf = 0, -2.0
        for k in range(T):
            c = _cosine(v, type_vecs[k])
            if c > bf:
                bf, bi = c, k
        best_fit[i], assigned[i] = bf, bi
        inside[i] = bf >= type_radii[bi]
    inside_idx = [i for i in range(N) if inside[i]]
    pile_idx = [i for i in range(N) if not inside[i]]

    # BOUND the clustered pile to the `cap` WORST-fitting (agglomerate is O(n³)); surface the tail.
    pile_sorted = sorted(pile_idx, key=lambda i: best_fit[i])
    clustered = pile_sorted[:cap]
    pile_tail = pile_sorted[cap:]                            # surfaced, never silently dropped
    # the 20/80 BIRTH threshold, as a FILL fraction of the examined pile (Tim: "fills past ~20/80") — the dial
    # moves the born/forming line (a distinct cluster below it is FORMING, above it is BORN a new type).
    birth_mass = max(3, round(dial * max(len(clustered), 1)))

    candidates = []
    if len(clustered) >= 6:
        pv = [item_vecs[i] for i in clustered]
        nv, cuts = scale.agglomerate(pv, linkage="ward")
        part = scale.cut(cuts, min(ncut, len(clustered)))
        groups = scale.clusters_of(part)
        rng = _random.Random(seed)

        def _margin(local_idxs: list) -> float:
            vs = [pv[j] for j in local_idxs]
            cen = _centroid(vs)
            internal = sum(_cosine(v, cen) for v in vs) / len(vs)
            external = sum(max(_cosine(v, tv) for tv in type_vecs) for v in vs) / len(vs)
            return internal - external

        for cid, local in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            if len(local) < 3:
                continue
            s = len(local)
            m = _margin(local)
            # PILE-PERMUTATION NULL: random same-size groupings of the WHOLE clustered pile (not a constant).
            null = sorted(_margin(rng.sample(range(len(pv)), s)) for _ in range(perms))
            p95 = null[min(int(perms * 0.95), perms - 1)]
            distinct = m > p95                               # beats the null → a real distinct region, not noise
            born = bool(distinct and s >= birth_mass)        # distinct AND past the 20/80 mass → a NEW TYPE
            global_members = [clustered[j] for j in local]
            ex = item_refs[global_members[0]]
            candidates.append({
                "size": s, "margin": round(m, 4), "null_p95": round(p95, 4),
                "distinct": distinct, "born": born, "birth_mass": birth_mass,
                "exemplar": ex, "members": [item_refs[g] for g in global_members],
                "member_idx": global_members,
            })

    # DISSOLUTION candidates — registered types in the low mass tail (context-dependent, never auto-applied).
    dissolution = [{"type": type_labels[k], "size": type_sizes[k],
                    "note": "below the low-tail floor — a dissolution CANDIDATE, context-dependent "
                            "(a sparse type may be rare, not wrong); never auto-applied"}
                   for k in range(T) if type_sizes[k] < dissolve_floor]

    # PER-ITEM placement (sector + radius) the projection reads. Inside → the assigned type's sector, radius =
    # fit DEPTH (strong fit deep, marginal near the box edge). Pile → OUTSIDE the box (r>1): a clustered
    # candidate member sits in that candidate's own outer ZONE (the forming new type, further out); an
    # un-clustered tail item hovers JUST outside the type it almost-fit (tried here, did not make it in).
    cand_zone = {}                                            # global item idx → candidate ordinal (its zone)
    for ci, c in enumerate(candidates):
        for gi in c["member_idx"]:
            cand_zone[gi] = ci
    # inside radius band: normalize best_fit over the inside set so the strongest fit is deep, the marginal at
    # the box edge (a small floor keeps the strongest just off the origin).
    in_fits = [best_fit[i] for i in inside_idx]
    fmin, fmax = (min(in_fits), max(in_fits)) if in_fits else (0.0, 1.0)
    fspread = (fmax - fmin) or 1.0
    # pile-tail radius band: more-unfit → farther out, in a thin ring just past the box edge.
    tail_fits = [best_fit[i] for i in pile_idx if i not in cand_zone]
    tmin, tmax = (min(tail_fits), max(tail_fits)) if tail_fits else (0.0, 1.0)
    tspread = (tmax - tmin) or 1.0

    per_item = {}
    for i in range(N):
        ref = item_refs[i]
        if inside[i]:
            r = 0.08 + 0.86 * (1.0 - (best_fit[i] - fmin) / fspread)   # strong→0.08 (deep), marginal→0.94
            per_item[ref] = {"sector": type_labels[assigned[i]], "r": round(min(max(r, 0.0), 0.96), 5),
                             "inside": True, "fit": round(best_fit[i], 4),
                             "assigned": type_labels[assigned[i]], "born": False}
        elif i in cand_zone:
            ci = cand_zone[i]
            per_item[ref] = {"sector": f"✦{ci}", "r": 1.18,        # the candidate's outer zone (forming type)
                             "inside": False, "fit": round(best_fit[i], 4),
                             "assigned": type_labels[assigned[i]], "pile_cluster": ci,
                             "born": candidates[ci]["born"]}
        else:
            r = 1.04 + 0.10 * (1.0 - (best_fit[i] - tmin) / tspread)    # the thin almost-fit ring just outside
            per_item[ref] = {"sector": type_labels[assigned[i]], "r": round(r, 5),
                             "inside": False, "fit": round(best_fit[i], 4),
                             "assigned": type_labels[assigned[i]], "tail": True, "born": False}

    return {
        "n_items": N, "n_types": T,
        "membership": {"inside": len(inside_idx), "pile": len(pile_idx)},
        "pile_total": len(pile_idx), "pile_clustered": len(clustered), "pile_tail": len(pile_tail),
        "dial": dial, "birth_mass": birth_mass, "median_type_size": med_type_size,
        "candidates": [{k: v for k, v in c.items() if k != "member_idx"} for c in candidates],
        "born_count": sum(1 for c in candidates if c["born"]),
        "distinct_count": sum(1 for c in candidates if c["distinct"]),
        "dissolution_candidates": dissolution,
        "type_labels": list(type_labels), "type_sizes": list(type_sizes),
        "per_item": per_item,
        # the candidate ZONE labels the projection appends as extra sectors (the pile forms OUTSIDE the box)
        "zones": [{"id": f"✦{ci}", "exemplar": c["exemplar"], "born": c["born"],
                   "distinct": c["distinct"], "size": c["size"]} for ci, c in enumerate(candidates)],
    }


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
            sector_edges: list | None = None, poles: dict | None = None,
            nucleation: dict | None = None) -> dict:
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

    # SEPARATOR precompute (Group 9 — the TWO-GRAVITY field). A GENERAL variable-two-pole resolution: a binding
    # with radius_from=='separator' plants TWO poles (any two vectors — pole-agnostic, registry-true, NOT a
    # hardcoded pollution oracle), and every item's radius reads its signed lean toward one pole vs the other.
    # The caller (bridge) resolves the two pole vectors and passes them in via `poles` ({'a':vecA,'b':vecB} or
    # {'a':{'vector':..,'label':..},'b':..}) — project() stays PURE, the poles ride IN like events/vectors.
    # For each point with a vector: pull_a = cos(item,A), pull_b = cos(item,B), lean = pull_b - pull_a (signed:
    # >0 → toward B, <0 → toward A, ~0 → neutral). BOTH pulls + the raw signed lean are carried on the point so
    # NO signal is thrown away (1D is lossy; the FORM picks its geometry from the raw fields). The fifth gate
    # (separation_report) runs HERE on the raw cosines and is surfaced — it is the witness that the field really
    # separates (a normalized radius alone is green-paint: it gradients over noise). Fail-loud: separator mode
    # with no poles RAISES (never a silent fallback to time). A vectorless point → r=1.0 + r_unknown (rim +
    # flagged, never silent-dropped), same honesty as the semantic mode.
    sep = (radius_from == "separator")
    sep_pa: dict = {}
    sep_pb: dict = {}
    sep_lean: dict = {}
    sep_lmin = sep_lmax = 0.0
    separation = None
    pole_a_meta = pole_b_meta = None
    if sep:
        _pa, _pb = (poles or {}).get("a"), (poles or {}).get("b")
        va = _pa.get("vector") if isinstance(_pa, dict) else _pa
        vb = _pb.get("vector") if isinstance(_pb, dict) else _pb
        if not va or not vb:
            raise ValueError(
                "separator radius needs TWO pole vectors (poles={'a':...,'b':...}) — fail loud, never a "
                "silent fallback to time. A two-gravity field with one (or no) gravity is not a field.")
        pole_a_meta = {"label": (_pa.get("label") if isinstance(_pa, dict) else None),
                       "ref": (_pa.get("ref") if isinstance(_pa, dict) else None)}
        pole_b_meta = {"label": (_pb.get("label") if isinstance(_pb, dict) else None),
                       "ref": (_pb.get("ref") if isinstance(_pb, dict) else None)}
        for _i, (_e, _t) in enumerate(stamped):
            pv = (vectors or {}).get(_addr_of(_e)) or (vectors or {}).get(_e.get("source_address") or "")
            if pv is not None and len(pv) == len(va) == len(vb):
                ca, cb = _cosine(va, pv), _cosine(vb, pv)
                sep_pa[_i], sep_pb[_i], sep_lean[_i] = ca, cb, cb - ca
        if sep_lean:
            _idxs = sorted(sep_lean.keys())
            _refs = [(stamped[i][0].get("source_address") or _addr_of(stamped[i][0])
                      or str(stamped[i][0].get("summary") or stamped[i][0].get("seq"))) for i in _idxs]
            separation = separation_report([sep_pa[i] for i in _idxs], [sep_pb[i] for i in _idxs],
                                           va, vb, refs=_refs)
            _leans = [abs(g) for g in sep_lean.values()]
            sep_lmin, sep_lmax = min(_leans), max(_leans)
    sep_norm = sep and (sep_lmax - sep_lmin) > 1e-9

    # NUCLEATION precompute (the 20/80 water-law — TYPE-BIRTH). A binding with radius_from=='nucleation' types
    # the items against a REGISTRY OF TYPES and reads where the registry under-covers its content: what fits
    # sits inside the square, what does not piles up OUTSIDE, and a distinct coherent pile past the birth
    # threshold is a CANDIDATE NEW TYPE. The heavy compute (fit → truthful membership → cluster the pile →
    # silhouette margin + permutation-null verdict → birth/dissolution) lives in `nucleation_report` (run by
    # the bridge, which resolves the type centroids + admission radii + item vectors from the store); project()
    # stays the GEOMETRY: it reads the resolved per-item placement and lays the points down. The SECTORS become
    # the registry's types PLUS one outer ZONE per candidate cluster (the pile forms OUTSIDE the box). Fail-loud:
    # nucleation mode with no resolved report RAISES (never a silent fallback to time).
    nuc = (radius_from == "nucleation")
    nuc_report = nucleation if nuc else None
    nuc_items: dict = {}
    if nuc:
        if not nuc_report or not nuc_report.get("per_item"):
            raise ValueError("nucleation radius needs a resolved report (nucleation={... per_item ...}) — fail "
                             "loud, never a silent fallback to time; type-birth has no meaning without a "
                             "registry of types to be under-covered.")
        nuc_items = nuc_report["per_item"]
        sectors = list(nuc_report.get("type_labels") or []) + [z["id"] for z in nuc_report.get("zones", [])]
        n = max(len(sectors), 1)
        kmap = {"__nuc__": True}

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

    # pick the declared-meaning registry for THIS lens's sectors (kinds default; node-types for Connections; an
    # unmapped domain → kinds map, which yields humanize-only for ids it doesn't hold — still legible, never raw).
    # Computed BEFORE the points loop so each point can carry its sector's HUMAN name (the inspector's "in" row).
    _sector_meta = _SECTOR_META_BY_DOMAIN.get(binding.get("angle_from", "kind"), _KIND_META)
    points = []
    for idx, (e, t) in enumerate(stamped):
        kind = e.get("kind") or "?"
        # the angular SECTOR key: by KIND (default/kind-group), or by the EVENT→ROW edge for an
        # angle_from=<registry/graph> binding (Group 10) — an event naming no row → the '—' remainder.
        info = None
        if nuc:                                   # NUCLEATION: sector = the resolved per-item placement (the
            # type it fits, or the candidate ZONE it piles into). An item not typed (no vector) is not a point.
            info = nuc_items.get(e.get("source_address") or "") or nuc_items.get(_addr_of(e))
            if info is None:
                continue
            skey = info["sector"]
            if skey not in sectors:
                continue
            i = sectors.index(skey)
        elif (by := kmap.get("__by__")):          # registry/graph mode: place by the EVENT→ROW edge
            row = _row_of(e, by)
            skey = row if row is not None else "—"
            if skey not in sectors:
                # the event maps to NO rendered row — drop it (don't pile it into the last sector). This is
                # the whole_set/connections case: there is no '—' remainder, so an unmapped event is simply
                # not a point of this view (the view is the registry's rows + their real edges, not a dump).
                continue
            i = sectors.index(skey)
        else:                                     # kind / kind-group: fnmatch/identity via _sector_index
            skey = kind
            i = _sector_index(skey, sectors, kmap)
        gi, gj, gd = cells[idx]
        ref = str(_addr_of(e) or e.get("summary") or e.get("seq"))
        theta = TAU * (i + 0.08 + 0.84 * _stable_unit(ref)) / n
        age = max((now - t).total_seconds(), 1.0)
        r_unknown = False
        if nuc:
            r = info["r"]                                            # resolved placement: <1 inside, >1 piled out
        elif sem:
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
        elif sep:
            g = sep_lean.get(idx)
            if g is None:
                r, r_unknown = 1.0, True                              # no vector → rim, FLAGGED (not dropped)
            elif sep_norm:
                # radius = |lean| normalized: NEUTRAL (no preference) → centre, BOTH poles → rim (the two
                # gravities render as EQUALS, not poleA→centre which would pile every strong-A item at the
                # degenerate origin — the same centre-pile failure as semantic/Group-10). The SIGN (which pole)
                # is the second channel, carried as the `lean`/`pole` fields for the FORM to render.
                r = 0.06 + 0.94 * (abs(g) - sep_lmin) / (sep_lmax - sep_lmin)
                r = min(max(r, 0.0), 1.0)
            else:
                r = abs(g)                                           # single value / no spread → raw |lean|
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
            # the kind's HUMAN words ride ON the point (registry-is-truth) so EVERY consumer — the drill-in
            # face, the inspector, a tooltip — shows MEANING, never the machine kind-id (operator-law). Read
            # declared-first from the kind registry; humanized-id fallback. `kind` stays the machine key.
            "kind_name": _kind_name(kind), "kind_meaning": _kind_meaning(kind),
            # the sector's HUMAN name (registry-true, via the lens's meta-registry) rides on the point too, so the
            # inspector's "in" row reads a human division on EVERY lens — not the machine sector-id on non-Kinds
            # lenses (operator-law). On the Kinds lens sector==kind so this equals kind_name; on Connections/graph
            # lenses it's the node-type/row human name. `sector` stays the machine key (the engine indexes by it).
            "sector_name": _kind_name(sid, _sector_meta),
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
            # SEPARATOR (Group 9) — both raw pulls + the signed lean carried so the FORM renders the two
            # gravities as equals (sign = which pole; |lean| = how strongly). 1D radius is lossy; these are not.
            **({"pull_a": round(sep_pa[idx], 4), "pull_b": round(sep_pb[idx], 4),
                "lean": round(sep_lean[idx], 4),
                "pole": ("b" if sep_lean[idx] > 0 else "a" if sep_lean[idx] < 0 else "—")}
               if (sep and idx in sep_lean) else {}),
            # NUCLEATION (the 20/80 water-law) — the typed-fit carried so the FORM shows WHERE each item landed:
            # inside (fits a type) vs piled out, its best fit + assigned type, the candidate ZONE it nucleates
            # into, and whether that candidate is BORN (a new type) vs still forming. r<1 inside, r>1 piled out.
            **({"fit": info["fit"], "assigned": info["assigned"], "inside": info["inside"],
                **({"pile_cluster": info["pile_cluster"]} if "pile_cluster" in info else {}),
                **({"tail": True} if info.get("tail") else {}),
                **({"born": True} if info.get("born") else {})}
               if (nuc and info is not None) else {}),
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
                    "radius_from": ("nucleation" if nuc else "separator" if sep else "semantic" if sem
                                    else ("address" if addr_center else radius_from)),
                    "order_by": binding.get("order_by", "count"),
                    # the binding's DECLARED human meaning (registry-true): name/is/fills/why, rendered by the
                    # Legend (declared-first; falls back to the computed mechanical lines). None until seeded.
                    "meta": binding.get("meta"),
                    # semantic only: was the meaning-distance min-max normalized for legibility? (honest —
                    # so 'near=close' is never silently a distorted absolute distance)
                    **({"radius_normalized": sem_norm, "space": binding.get("space")} if sem else {}),
                    # separator only: the two poles (label/ref) + whether the lean was min-max normalized
                    **({"poles": {"a": pole_a_meta, "b": pole_b_meta},
                        "radius_normalized": sep_norm, "space": binding.get("space")} if sep else {}),
                    # nucleation only: which registry-of-types + which item store the fit was read against
                    **({"types_space": (nuc_report or {}).get("types_space"),
                        "space": binding.get("space")} if nuc else {})},
        "bindings": [{"id": b["id"], "label": b["label"]} for b in reg.list()] or
                    [{"id": "raw", "label": "Kinds (raw)"}],
        # sector label = the row's HUMAN name (declared-first → humanized-id fallback); `meaning` = its one-line
        # "what it is" (the tap-a-sector readout). The instrument stays empty of meaning — it reads these off the
        # DATA. The meaning-registry is chosen by the sector DOMAIN (binding.angle_from): kinds for the default
        # Kinds wheel, node-types for the Connections lens, etc.; an unmapped domain → humanize-only (still
        # legible). id stays the machine key (the engine indexes/edges by it, never shown raw).
        "sectors": [{"id": s, "label": _kind_name(s, _sector_meta), "meaning": _kind_meaning(s, _sector_meta),
                     "from": round(TAU * i / n, 5), "to": round(TAU * (i + 1) / n, 5)}
                    for i, s in enumerate(sectors)],
        "edges": edges,   # the directional typed edges between sectors (directed chords; bidir = a real cycle)
        # THE FIFTH GATE (Group 9): the separation report — the witness that the two-gravity field actually
        # SEPARATES (computed on raw cosines, not the cosmetic radius). Present only in separator mode.
        **({"separation": separation} if sep else {}),
        # NUCLEATION (the 20/80 water-law): the type-birth report — membership, the candidate new types (with
        # margin-strength + the permutation-null verdict + born/forming), dissolution candidates, the bounded
        # pile + surfaced tail. The witness for type-birth (per_item is omitted here — it rides on the points).
        **({"nucleation": {k: v for k, v in nuc_report.items() if k != "per_item"}} if nuc else {}),
        "rings": rings, "grid": grid_m,   # m/2 concentric circles for the m×m dyadic grid (seed §1)
        "lock": "x = 2*pi/n; n resolves from the binding's source — no hardcoded sectors",
        "points": points, "count": len(points),
    }
