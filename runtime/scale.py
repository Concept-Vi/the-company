"""runtime/scale.py — GROUP 11 · THE MULTI-SCALE EMBEDDING PYRAMID (the instrument's ZOOM axis).

WHAT THIS IS (read before changing):
  The instrument resolves a frame from a binding — centre, angle θ, radius r. Group 6 made the radius
  the CIRCLE (semantic meaning-distance). Group 11 adds the missing axis: SCALE. Zooming out should not
  just magnify the same points — it should resolve at a COARSER GRAIN: the meaning-field at lower
  resolution = fewer, larger meaning-REGIONS (themes), not the individual units. Zoom IN and the theme
  dissolves back into its member units. "Zoom changes which rung RESOLVES" (COMPLETION-CRITERIA Group 11).

WHY CLUSTER-CENTROIDS, NOT LINEAGE (the reversal the evidence forced):
  The first plan was a LINEAGE pyramid (unit ⊂ session ⊂ project, from the corpus.record lineage). The
  per-space probe KILLED it: within a single embedding space the `session` axis is CAPTURE-BATCH
  provenance (ingest-flow / full-repo / g25 / smoke-test — which ingest run wrote the unit, NOT a
  semantic nest), and `project` is ONE point per space (company dominates every space). A centroid over a
  capture batch is an arbitrary slice of the repo — noise; a one-point project rung is degenerate. So the
  honest coarsening is over MEANING, not provenance: Group 11 is the EMBEDDING pyramid (Group 6 already
  fixed radius = the circle = meaning), so the coarse rung = fewer, larger meaning-regions = CLUSTERS of
  near points. The centroid of a cluster is the real coarse "point". This is a PURE READ over the unit
  vectors Group 8 already persisted — no re-embed, no re-chunk, no new metric, no new semantics.

WHY HIERARCHICAL (Ward), NOT per-K k-means (the dispositive design choice):
  The rungs must NEST — a fine cluster must sit inside exactly one coarse cluster (unit ⊂ fine ⊂ coarse),
  or zoom is a lie (units jumping themes between rungs = a fake pyramid). ONE agglomerative dendrogram cut
  at each rung gives that for free: every K-cut is a coarsening of every finer K-cut (they share one merge
  sequence). Independent k-means per K does NOT nest. LINKAGE = Ward: AVERAGE-linkage CHAINED on these
  high-baseline-cosine embeddings (one cluster swallowed 129/162, 525/644 — verified in the linkage probe);
  Ward minimises within-cluster variance → BALANCED, discriminative clusters (topics: 9/19/31 at K=8,
  queries spread across all 8 themes, containment 95-100%). Ward needs Euclidean; on L2-NORMALISED vectors
  squared-euclidean = 2(1-cosine), so Ward-on-normed ≡ cosine-Ward. DEPENDENCY-FREE (no numpy/scipy — the
  floor's _cosine is hand-rolled for exactly this reason); the Lance-Williams update keeps it O(n²) memory
  and we build only the space the FORM renders (topics, 162) — never the whole corpus blindly.

REUSE — NOT A PARALLEL VECTOR STORE: centroids persist via the SAME store.put_vector into the SAME
vectors/ substrate, keyed `vec://cluster://<space>/k<K>/<label>#space=scale:<space>:k<K>` — so the EXISTING
store/vector_index.query_index ranks them with the EXISTING cosine (resolve at a coarse rung = query that
scale space; the centroid's `source` is the cluster address it returns). No second index, no reimplemented
cosine. The NESTING/membership (which units ⊂ which cluster, the cross-rung parent links, the exemplar
label) rides a small pyramid sidecar (store.save_scale_pyramid) — vectors stay in the vector substrate,
structure in the structure sidecar, no duplication.

FAIL LOUD (rule 4): a pyramid over an EMPTY space RAISES (never a silent empty pyramid). A space too thin
to coarsen honestly (n < 2·floor) RAISES rather than fabricate degenerate rungs. The embedder is NEVER
touched here (centroids are means of vectors already on disk) — so this lane runs even with :8001 down.
"""
from __future__ import annotations
import math


# ── the dependency-free vector floor (mirrors projection.py:_cosine — the pure-read floor carries NO
#    numpy/scipy import; replicated, not shared, so a refactor of one never silently breaks the other) ──
def _norm(v: list) -> list:
    """L2-normalise — so squared-euclidean distance = 2(1-cosine) (lets Ward, a euclidean method, act on
    cosine geometry) and a centroid is comparable by cosine. A zero vector normalises to itself (guarded)."""
    n = math.sqrt(sum(x * x for x in v))
    if n == 0.0:
        return list(v)
    return [x / n for x in v]


def _cos(a: list, b: list) -> float:
    """Cosine of two ALREADY-NORMALISED vectors (= dot product). Fail loud on a dim mismatch (rule 4) —
    a silently-truncated zip would give a wrong-but-plausible similarity (the exact bug _cosine guards)."""
    if len(a) != len(b):
        raise ValueError(f"scale._cos: dim mismatch {len(a)} vs {len(b)} — a wrong cosine is worse than a crash")
    return sum(x * y for x, y in zip(a, b))


def centroid(normed_vectors: list, member_idxs: list) -> list:
    """The cluster's coarse point = the L2-NORMALISED MEAN of its members' (normalised) vectors. Mean then
    re-normalise so the centroid lives on the same unit sphere as the units → cosine to it is meaningful.
    member_idxs must be non-empty (a cluster has ≥1 member by construction)."""
    if not member_idxs:
        raise ValueError("scale.centroid: empty cluster has no centroid (fail loud — never a zero vector)")
    dim = len(normed_vectors[member_idxs[0]])
    acc = [0.0] * dim
    for i in member_idxs:
        vi = normed_vectors[i]
        for d in range(dim):
            acc[d] += vi[d]
    return _norm([x / len(member_idxs) for x in acc])


# ── ONE dendrogram, cut at every rung (the nesting guarantee) ────────────────────────────────────────
def agglomerate(vectors: list, *, linkage: str = "ward") -> tuple[list, dict]:
    """Build ONE agglomerative dendrogram over `vectors` and snapshot the partition at every cluster-count.

    Returns (normed_vectors, cuts) where cuts[K] = a partition: a list `label[i]` (the active-cluster id of
    original point i) when exactly K clusters remain. Because EVERY snapshot comes from the SAME merge
    sequence, cuts[K_coarse] is a strict COARSENING of cuts[K_fine] for K_coarse < K_fine — i.e. every fine
    cluster ⊂ exactly one coarse cluster (the nesting the pyramid stands on). This is the property that an
    independent per-K clustering would NOT have.

    LINKAGE (`ward` default — the linkage the evidence chose; see module docstring):
      · ward     — minimise within-cluster variance (Lance-Williams). On L2-normed vectors with d²=2(1-cos)
                   this is cosine-Ward: balanced, discriminative clusters (the chosen production linkage).
      · complete — max intra-pair distance (compact clusters; available for comparison).
      · average  — UPGMA (CHAINS on high-baseline cosine — kept only so the test can DEMONSTRATE why ward).
    Works in SQUARED-EUCLIDEAN on normalised vectors (d² = 2(1-cosine)); all three are monotone in cosine
    distance so a single distance store serves them. O(n²) memory, O(n³) time (full closest-pair scan per
    merge) — fine for the rendered space (topics=162); callers never agglomerate the whole corpus blindly.
    """
    if linkage not in ("ward", "complete", "average"):
        raise ValueError(f"scale.agglomerate: unknown linkage {linkage!r} (ward|complete|average)")
    n = len(vectors)
    nv = [_norm(v) for v in vectors]
    if n == 0:
        return nv, {}
    if n == 1:
        return nv, {1: [0]}

    size = {i: 1 for i in range(n)}
    members = {i: [i] for i in range(n)}
    active = list(range(n))
    # squared-euclidean on normed vectors = 2(1-cosine); upper-triangle dict keyed (min,max)
    D: dict = {}
    for i in range(n):
        for j in range(i + 1, n):
            D[(i, j)] = 2.0 * (1.0 - _cos(nv[i], nv[j]))

    def dg(a, b):
        return D[(a, b)] if a < b else D[(b, a)]

    cuts: dict = {}

    def snapshot():
        part = [0] * n
        for cid in active:
            for m in members[cid]:
                part[m] = cid
        cuts[len(active)] = part

    snapshot()                                   # K = n (every point its own cluster)
    nxt = n
    while len(active) > 1:
        # closest active pair (full scan — exact; the dendrogram correctness floor)
        best = None
        bp = None
        for ii in range(len(active)):
            a = active[ii]
            for jj in range(ii + 1, len(active)):
                d = dg(a, active[jj])
                if best is None or d < best:
                    best = d
                    bp = (a, active[jj])
        a, b = bp
        na, nb, dab = size[a], size[b], best
        newid = nxt
        nxt += 1
        # Lance-Williams update of newid↔every other active cluster
        for c in active:
            if c == a or c == b:
                continue
            nc, dac, dbc = size[c], dg(a, c), dg(b, c)
            if linkage == "ward":
                d = ((na + nc) * dac + (nb + nc) * dbc - nc * dab) / (na + nb + nc)
            elif linkage == "complete":
                d = dac if dac > dbc else dbc
            else:                                # average (UPGMA)
                d = (na * dac + nb * dbc) / (na + nb)
            D[(min(newid, c), max(newid, c))] = d
        members[newid] = members[a] + members[b]
        size[newid] = na + nb
        active.remove(a)
        active.remove(b)
        active.append(newid)
        snapshot()
    return nv, cuts


def cut(cuts: dict, k: int) -> list:
    """The partition with the available cluster-count CLOSEST to k (ties → the finer/larger count). cuts has
    a snapshot for every K in [1, n], so `cuts.get(k)` is usually exact; the closest-match keeps a caller's
    derived rung robust if a degenerate merge ever skipped a count."""
    if not cuts:
        raise ValueError("scale.cut: empty dendrogram (no points)")
    if k in cuts:
        return cuts[k]
    return cuts[min(cuts, key=lambda kk: (abs(kk - k), -kk))]


def clusters_of(partition: list) -> dict:
    """{cluster_label: [point_index, ...]} from a partition (label-per-point). Members in ascending index
    order (stable, so labels/exemplars are reproducible build-to-build)."""
    out: dict = {}
    for i, lab in enumerate(partition):
        out.setdefault(lab, []).append(i)
    return out


def default_rungs(n: int, *, floor: int = 4) -> list:
    """The DYADIC resolution ladder (SEED §1: the grid is m = 2^k; a rung is one resolution level). DERIVED
    from n — never hardcoded — so a bigger space gets coarser rungs automatically and registry-is-truth
    holds (no magic sector counts). Two rungs by default: a fine-coarse rung near a power of two of ~√n and
    a coarse rung a QUARTER of it (a sparse, clearly-separated ladder: 8 ⊂ 32, not every level). Capped so
    each coarse cluster averages ≥3 members (K ≤ n//3). Returns DESCENDING cluster-counts (coarsest last is
    handled by the caller). A space too thin to coarsen honestly → [] (the caller fail-louds)."""
    if n < floor * 2:
        return []
    # top ≈ a power of two near 2.8·√n, capped at n//3 (≥~3 members/cluster), floored at `floor`
    top = 1 << max(2, round(math.log2(max(2.0, math.sqrt(n))) + 1.0))
    cap = 1 << int(math.log2(max(2, n // 3)))
    top = min(top, cap)
    rungs = []
    k = top
    while k >= floor:
        rungs.append(k)
        k //= 4                                  # quarter-steps → a sparse, well-separated ladder
    return rungs                                 # e.g. n=162 → [32, 8];  n=644 → [32, 8]


# ── BUILD / RESOLVE over the persisted vector substrate ───────────────────────────────────────────────
def _member_hash(store, source_addresses: list) -> str:
    """The incremental key for a centroid: the content_hash of its members' SORTED (source, content_hash)
    pairs. So a centroid is re-persisted ONLY when its membership changes OR a member re-embeds (its unit
    content_hash moves) — mirrors build_index's content-hash incrementality. Reuses vector_index.content_hash
    (the same blake2b key the unit vectors were persisted under — not reimplemented)."""
    from store import vector_index as vx
    parts = []
    for src in sorted(source_addresses):
        rec = store.get_vector(store.space_address(src, None))   # unit vectors live in the bare/default key under their own source
        parts.append(f"{src}:{(rec or {}).get('content_hash', '∅')}")
    return vx.content_hash("\n".join(parts))


def build_scale_pyramid(store, *, space: str, rungs: list | None = None, linkage: str = "ward",
                        force: bool = False) -> dict:
    """BUILD the multi-scale pyramid over the UNIT vectors persisted in `space` (Group 8's topics/repo/…).

    For each rung K: cut the ONE dendrogram at K, compute each cluster's centroid (normalised mean of its
    members' vectors), persist the centroid as a QUERYABLE vector (store.put_vector, space=`scale:<space>:k<K>`,
    source=`cluster://<space>/k<K>/<label>`) and record the cluster's membership + exemplar (the member
    nearest the centroid — a REAL unit that names the theme, never a fabricated label). Persist the whole
    structure (rungs, per-rung clusters, cross-rung parent links) via store.save_scale_pyramid.

    INCREMENTAL: a centroid is re-persisted only when its `_member_hash` changed (or force=True / new) —
    an unchanged rebuild writes no vectors. PURE READ of the embedder: centroids are means of on-disk
    vectors; :8001 is never called (this lane runs with the embedder down).

    FAIL LOUD: an empty/absent space, or a space too thin to coarsen (default_rungs → []), RAISES — never a
    silent empty pyramid. Returns {space, rungs:[...], n_units, built, skipped}.
    """
    from store import vector_index as vx

    corpus = store.index_corpus(space=space)     # [{id: <unit source address>, vector}]
    n = len(corpus)
    if n == 0:
        raise ValueError(
            f"scale.build_scale_pyramid: space {space!r} has NO unit vectors — cannot build a pyramid over "
            f"an empty space (build the lens first via capture_corpus_lenses). Fail loud, never an empty pyramid.")
    if rungs is None:
        rungs = default_rungs(n)
    if not rungs:
        raise ValueError(
            f"scale.build_scale_pyramid: space {space!r} has only {n} units — too thin to coarsen honestly "
            f"(need ≥ {2 * 4}). Fail loud rather than fabricate degenerate one-member rungs.")
    rungs = sorted(set(int(k) for k in rungs if 1 < int(k) < n), reverse=True)   # valid, descending, unique

    ids = [c["id"] for c in corpus]
    vecs = [c["vector"] for c in corpus]
    dim = len(vecs[0])
    # the embed model the units were built under (a centroid inherits it — it is a mean of those vectors)
    model = (store.get_vector(store.space_address(ids[0], space)) or {}).get("model")

    nv, cuts = agglomerate(vecs, linkage=linkage)

    built = skipped = 0
    rung_records: list = []
    # FINEST→COARSEST (descending K) so each coarse cluster can record the FINER clusters that fold into it
    # (`children_finer` = the nesting made explicit + queryable; the finest rung has no finer rung → none).
    prev_assign: dict | None = None              # {unit_index: finer_cluster_source} from the rung just built
    for k in sorted(rungs, reverse=True):        # descending K = finest coarse rung first
        part = cut(cuts, k)
        groups = clusters_of(part)
        cluster_recs: list = []
        assign: dict = {}
        # stable cluster ordering by smallest member index → reproducible labels build-to-build
        for label, (_lab, idxs) in enumerate(sorted(groups.items(), key=lambda kv: min(kv[1]))):
            cvec = centroid(nv, idxs)
            # exemplar = the member NEAREST the centroid (a real unit that names the theme)
            exemplar = max(idxs, key=lambda i: _cos(nv[i], cvec))
            member_srcs = [ids[i] for i in idxs]
            cluster_addr = f"cluster://{space}/k{k}/{label}"
            store_key = store.space_address(cluster_addr, f"scale:{space}:k{k}")
            h = _member_hash(store, member_srcs)
            prior = store.get_vector(store_key)
            if force or prior is None or prior.get("content_hash") != h:
                store.put_vector(store_key, cvec, h, dim=dim, model=model,
                                 space=f"scale:{space}:k{k}", source=cluster_addr)
                built += 1
            else:
                skipped += 1
            # parent link: which FINER-rung clusters fold into this one (nesting made explicit + queryable)
            child_finer = sorted({prev_assign[i] for i in idxs}) if prev_assign else None
            cluster_recs.append({
                "label": label, "source": cluster_addr, "size": len(idxs),
                "exemplar": ids[exemplar], "members": member_srcs,
                **({"children_finer": child_finer} if child_finer is not None else {}),
            })
            for i in idxs:
                assign[i] = cluster_addr
        rung_records.append({"k": k, "space": f"scale:{space}:k{k}", "clusters": cluster_recs})
        prev_assign = assign

    pyramid = {"space": space, "linkage": linkage, "n_units": n, "dim": dim,
               # present COARSEST-FIRST (ascending K) — the order zoom walks out→in (theme → unit)
               "rungs": sorted(rung_records, key=lambda r: r["k"]), "unit_space": space}
    store.save_scale_pyramid(space, pyramid)
    return {"space": space, "rungs": rungs, "n_units": n, "built": built, "skipped": skipped,
            "pyramid_rungs": [{"k": r["k"], "clusters": len(r["clusters"])} for r in rung_records]}


def load_pyramid(store, space: str) -> dict | None:
    """The persisted pyramid structure for `space`, or None if never built (an HONEST None — never a
    fabricated pyramid). Thin reuse of store.load_scale_pyramid."""
    return store.load_scale_pyramid(space)


def rung_points(store, space: str, k: int) -> list:
    """The coarse POINTS at rung K — one per cluster: {source (cluster address), vector (centroid), size,
    exemplar, members}. The bridge feeds these to project() as pseudo-events so the SAME instrument
    (semantic radius, angle, centre) draws a coarse rung exactly as it draws units — zoom changes which rung
    RESOLVES, not which renderer runs. Reads the persisted centroids (no recompute). Fail-loud if the rung
    was never built (so a caller cannot silently render an empty coarse rung)."""
    pyr = load_pyramid(store, space)
    if not pyr:
        raise ValueError(f"scale.rung_points: no pyramid built for space {space!r} (build_scale_pyramid first)")
    rec = next((r for r in pyr["rungs"] if r["k"] == k), None)
    if rec is None:
        raise ValueError(f"scale.rung_points: rung k={k} not in pyramid for {space!r} "
                         f"(rungs: {[r['k'] for r in pyr['rungs']]})")
    out = []
    for c in rec["clusters"]:
        v = store.get_vector(store.space_address(c["source"], rec["space"]))
        if v is None:
            raise ValueError(f"scale.rung_points: centroid vector missing for {c['source']!r} — pyramid "
                             f"structure and vector substrate disagree (rebuild build_scale_pyramid)")
        out.append({"source": c["source"], "vector": v["vector"], "size": c["size"],
                    "exemplar": c["exemplar"], "members": c["members"],
                    **({"children_finer": c["children_finer"]} if "children_finer" in c else {})})
    return out


def resolve_at_rung(store, query_vector: list, *, space: str, k: int | None = None, n: int = 5) -> dict:
    """RESOLVE a query at a rung — the zoom-by-rung query layer. k=None (or k>=n_units) → the UNIT rung
    (query_index over `space`: returns individual units). A coarse k → query_index over `scale:<space>:k<K>`:
    returns the nearest THEME(S) (cluster centroids, by their cluster `source`). SAME cosine, SAME
    query_index — only the space (the rung) changes. Returns {rung, ranked:[{id, score}], note}."""
    from store import vector_index as vx
    rung_space = space if (k is None) else f"scale:{space}:k{k}"
    res = vx.query_index(store, query_vector, k=n, space=rung_space, with_note=True)
    return {"rung": ("unit" if k is None else f"k{k}"), "space": rung_space, **res}
