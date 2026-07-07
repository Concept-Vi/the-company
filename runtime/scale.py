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
def _member_hash(store, source_addresses: list, hashes: dict | None = None) -> str:
    """The incremental key for a centroid: the content_hash of its members' SORTED (source, content_hash)
    pairs — re-persist ONLY when membership changes OR a member re-embeds. PERF+CORRECTNESS fix
    (2026-07-07): `hashes` = a per-build PREFETCH ({source: content_hash} via pg_vectors.content_hashes,
    ONE query for the whole space) replacing a per-member get_vector round-trip that ALSO read the wrong
    key (the default space — named-space units aren't there, so content read '∅' and incrementality
    silently keyed on membership only). Reuses vector_index.content_hash (not reimplemented)."""
    from store import vector_index as vx
    hashes = hashes or {}
    parts = [f"{src}:{hashes.get(src, '∅')}" for src in sorted(source_addresses)]
    return vx.content_hash("\n".join(parts))


def build_scale_pyramid(store, *, space: str, rungs: list | None = None, linkage: str = "ward",
                        force: bool = False, emb: str | None = None) -> dict:
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

    SCALE: above _WARD_MAX_UNITS the O(n²) ward dendrogram is infeasible → DELEGATE to the kmeans-hybrid
    (build_scale_pyramid_kmeans) which is identical in output shape + nesting (recollection 2026-06-27, the
    harvested rollup-scalability gap — extractions 51k / common_knowledge). linkage='ward' explicit still
    forces the dendrogram path (a caller that KNOWS the space is small + wants exact ward can demand it)."""
    from store import vector_index as vx

    corpus = store.index_corpus(space=space, emb=emb)   # [{id: <unit source address>, vector}] at the embedder LAYER
    n = len(corpus)
    # SCALABLE DELEGATION: a large space can't be warded whole → the kmeans-hybrid (same structure/nesting).
    # Only when the caller didn't pin a specific non-default linkage (ward is the default → eligible to scale).
    if n > _WARD_MAX_UNITS and linkage == "ward":
        return build_scale_pyramid_kmeans(store, space=space, rungs=rungs, force=force, emb=emb)
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
    model = (store.get_vector(store.space_address(ids[0], space, emb)) or {}).get("model")

    from store import pg_vectors as _pgv
    _hashes = _pgv.content_hashes(getattr(store, "_pg_ns", "") + space, emb or "pplx")   # ONE query — the incrementality prefetch
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
            store_key = store.space_address(cluster_addr, f"scale:{space}:k{k}", emb)
            h = _member_hash(store, member_srcs, _hashes)
            prior = store.get_vector(store_key)
            if force or prior is None or prior.get("content_hash") != h:
                store.put_vector(store_key, cvec, h, dim=dim, model=model,
                                 space=f"scale:{space}:k{k}", source=cluster_addr, emb=emb)
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
    rows = emit_cluster_member_rows(store, pyramid, emb)     # the structure's SQL home (0022; reconciled)
    # store.save_scale_pyramid(space, pyramid, emb)  # RETIRED 2026-07-03 (rows-forward): the JSON sidecar
    #   write — structure now lives in ledger.cluster_member (the 7 legacy sidecars were loaded there once;
    #   readers reconstruct from rows). Restore by uncommenting if the rows path must be rolled back.
    return {"space": space, "rungs": rungs, "n_units": n, "built": built, "skipped": skipped,
            "member_rows": rows["rows"],
            "pyramid_rungs": [{"k": r["k"], "clusters": len(r["clusters"])} for r in rung_records]}


# Above this unit count, the O(n²) ward dendrogram is infeasible (its own docstring: "never agglomerate the
# whole corpus blindly") → build_scale_pyramid delegates to the SCALABLE kmeans-hybrid path. The 51,600
# extractions space + common_knowledge are the spaces that need it (recollection 2026-06-27, the harvested
# rollup-scalability gap). Below it, ward over all units stays (its nesting is exact + cheap at small n).
_WARD_MAX_UNITS = 4000


def build_scale_pyramid_kmeans(store, *, space: str, rungs: list | None = None, force: bool = False,
                               emb: str | None = None) -> dict:
    """SCALABLE multi-scale pyramid for a LARGE space (the kmeans-hybrid — recollection 2026-06-27). Ward is
    O(n²) mem / O(n³) time → infeasible over 50k+ units. Instead:
      1. MiniBatchKMeans the FINEST rung (max K) over all n units → the base clustering (sklearn, minibatch =
         designed for exactly this scale).
      2. WARD-agglomerate the ~K FINE CENTROIDS up to the coarse rungs (reuse `agglomerate` — now O(K²) on the
         centroids, not O(n²) on units). A coarse cluster's members = the EXACT UNION of the fine clusters that
         fold into it → the nesting invariant (coarse ⊃ fine) holds BY CONSTRUCTION, the same property the
         single-dendrogram ward path guarantees.
    Persists the IDENTICAL structure as build_scale_pyramid (cluster://<space>/k<K>/<label> centroids as
    queryable `scale:<space>:k<K>` vectors + the pyramid sidecar) — a drop-in for any rung_points/resolve_at_rung
    reader. Incremental (member-hash skip). PURE READ of the embedder (centroids are means of on-disk vectors)."""
    import numpy as _np
    from sklearn.cluster import MiniBatchKMeans

    corpus = store.index_corpus(space=space, emb=emb)
    from store import pg_vectors as _pgv
    _hashes = _pgv.content_hashes(getattr(store, "_pg_ns", "") + space, emb or "pplx")   # ONE query (perf+correctness fix, same as the ward path)
    n = len(corpus)
    if n == 0:
        raise ValueError(f"scale.build_scale_pyramid_kmeans: space {space!r} has NO unit vectors.")
    if rungs is None:
        rungs = default_rungs(n)
    rungs = sorted({int(k) for k in (rungs or []) if 1 < int(k) < n}, reverse=True)
    if not rungs:
        raise ValueError(f"scale.build_scale_pyramid_kmeans: space {space!r} ({n} units) too thin to coarsen.")

    # MEMORY-NATIVE (recollection 2026-06-27 fix): build ONE numpy array + free the Python corpus immediately.
    # The naive path held corpus(list) + nv(list) + X(numpy) = ~3× the vector data (~8GB for 51k×2560 → OOM/
    # thrash). Here: vectors → float32 array, normalize in-place, drop the source lists; centroids/exemplars are
    # numpy (X[idxs].mean / X[idxs]@c), never a Python list-of-lists copy.
    ids = [c["id"] for c in corpus]
    model = (store.get_vector(store.space_address(ids[0], space, emb)) or {}).get("model")
    X = _np.asarray([c["vector"] for c in corpus], dtype=_np.float32)
    del corpus                                                   # free the Python dicts/lists (the heavy half)
    dim = int(X.shape[1])
    _nrm = _np.linalg.norm(X, axis=1, keepdims=True); _nrm[_nrm == 0] = 1.0
    X /= _nrm                                                    # unit-normalize in place → cosine == dot

    def _cen(idxs):                                              # normalized mean of member rows (numpy)
        m = X[idxs].mean(axis=0); nn = float(_np.linalg.norm(m))
        return m / nn if nn else m

    finest = rungs[0]
    km = MiniBatchKMeans(n_clusters=finest, random_state=0, batch_size=4096,
                         n_init=3, max_iter=100).fit(X)
    labels = km.labels_.tolist()

    # FINE rung — kmeans clusters, in stable order (by smallest member index → reproducible labels)
    fine_groups = clusters_of(labels)                            # {km_label: [unit_idx, ...]}
    fine = []                                                    # ordered [(source, [unit_idxs], centroid_np)]
    for label, (_kl, idxs) in enumerate(sorted(fine_groups.items(), key=lambda kv: min(kv[1]))):
        fine.append((f"cluster://{space}/k{finest}/{label}", idxs, _cen(idxs)))

    built = skipped = 0
    rung_records: list = []

    def _persist_rung(k, clusters):
        """clusters = ordered [(source, [unit_idxs], centroid_np, children_finer|None)] → persist + record."""
        nonlocal built, skipped
        recs = []
        for label, (src, idxs, cvec, child) in enumerate(clusters):
            member_srcs = [ids[i] for i in idxs]
            exemplar = int(idxs[int((X[idxs] @ cvec).argmax())])  # member nearest the centroid (numpy)
            store_key = store.space_address(src, f"scale:{space}:k{k}", emb)
            h = _member_hash(store, member_srcs, _hashes)
            prior = store.get_vector(store_key)
            if force or prior is None or prior.get("content_hash") != h:
                store.put_vector(store_key, cvec.tolist(), h, dim=dim, model=model,
                                 space=f"scale:{space}:k{k}", source=src, emb=emb)
                built += 1
            else:
                skipped += 1
            recs.append({"label": label, "source": src, "size": len(idxs), "exemplar": ids[exemplar],
                         "members": member_srcs, **({"children_finer": child} if child is not None else {})})
        rung_records.append({"k": k, "space": f"scale:{space}:k{k}", "clusters": recs})

    # COARSER rungs — ward the FINE CENTROIDS (O(K²)), cut at each coarse rung; a coarse cluster's units =
    # union of its fine clusters' units (nesting exact). Build COARSEST→FINEST among the coarse set so each
    # records the finer clusters folding into it; the FINE rung itself is persisted last (children=None).
    coarse_rungs = [k for k in rungs if k != finest]
    if coarse_rungs:
        fine_centroids = [fc[2].tolist() for fc in fine]         # ~K centroids → lists for the pure-python ward
        _nv2, cuts2 = agglomerate(fine_centroids, linkage="ward")
        # map each fine-cluster position → its coarse-cluster source, rung by rung (descending K) for children
        prev_assign = {p: fine[p][0] for p in range(len(fine))}   # finest rung: a fine pos maps to its own source
        for k in coarse_rungs:                                    # descending (rungs sorted desc; finest excluded)
            part = cut(cuts2, k)                                  # label per FINE-cluster position
            groups = clusters_of(part)                           # {coarse_label: [fine_position, ...]}
            clusters = []
            assign = {}
            for label, (_cl, fpos) in enumerate(sorted(groups.items(), key=lambda kv: min(kv[1]))):
                src = f"cluster://{space}/k{k}/{label}"
                unit_idxs = sorted(i for p in fpos for i in fine[p][1])    # UNION of the fine clusters' units
                cvec = _cen(unit_idxs)
                child = sorted({prev_assign[p] for p in fpos})            # finer clusters folding in
                clusters.append((src, unit_idxs, cvec, child))
                for p in fpos:
                    assign[p] = src
            _persist_rung(k, clusters)
            prev_assign = assign
    # the FINE rung (persisted after, so the coarse children_finer above point at THIS rung's sources)
    _persist_rung(finest, [(src, idxs, cvec, None) for (src, idxs, cvec) in fine])

    pyramid = {"space": space, "linkage": "kmeans+ward", "n_units": n, "dim": dim,
               "rungs": sorted(rung_records, key=lambda r: r["k"]), "unit_space": space}
    rows = emit_cluster_member_rows(store, pyramid, emb)     # the structure's SQL home (0022; reconciled)
    # store.save_scale_pyramid(space, pyramid, emb)  # RETIRED 2026-07-03 — see build_scale_pyramid's note.
    return {"space": space, "rungs": rungs, "n_units": n, "built": built, "skipped": skipped, "method": "kmeans+ward",
            "member_rows": rows["rows"],
            "pyramid_rungs": [{"k": r["k"], "clusters": len(r["clusters"])} for r in rung_records]}


def emit_cluster_member_rows(store, pyramid: dict, emb: str | None = None) -> dict:
    """L-scale rows-forward (2026-07-03): persist the pyramid's MEMBERSHIP/NESTING as ledger.cluster_member
    rows — the SQL home the coordinate query's scale-drill joins (migration 0022). Replaces the JSON sidecar
    as the structure's home (vocabulary stays: vectors in ledger.embedding, structure in cluster_member).
    Fresh-rebuild semantics: DELETE this (space, emb, ns)'s rows then insert the new set, count-reconciled
    (RAISE on mismatch — never a silently-partial pyramid). Respects the store root's namespace (a test/tmp
    store writes ns-prefixed space values — the same __root_ isolation law as vectors/marks)."""
    from store.pg_marks import _psql, _dq                 # the shared psql runner (generic, param-quoted)
    ns = getattr(store, "_pg_ns", "")
    space = ns + pyramid["space"]
    embv = emb or "pplx"
    # invert children_finer -> parent_cluster (the coarser cluster each finer one folds into)
    parent_of = {}
    for rung in pyramid["rungs"]:
        for c in rung["clusters"]:
            for child in c.get("children_finer") or []:
                parent_of[child] = c["source"]
    lines = ["BEGIN;",
             f"delete from ledger.cluster_member where space={_dq(space)} and emb={_dq(embv)};"]
    want = 0
    for rung in pyramid["rungs"]:
        k = rung["k"]
        for c in rung["clusters"]:
            ca, ex, par = c["source"], c.get("exemplar"), parent_of.get(c["source"])
            for m in c["members"]:
                lines.append(
                    f"insert into ledger.cluster_member (cluster_address,member_address,space,k,emb,is_exemplar,parent_cluster) "
                    f"values ({_dq(ca)},{_dq(m)},{_dq(space)},{k},{_dq(embv)},{'true' if m == ex else 'false'},"
                    f"{_dq(par) if par else 'null'});")
                want += 1
    lines.append("COMMIT;")
    _psql("\n".join(lines))
    got = int(_psql(f"select count(*) from ledger.cluster_member where space={_dq(space)} and emb={_dq(embv)}").strip())
    if got != want:
        raise RuntimeError(f"emit_cluster_member_rows: {pyramid['space']} landed {got} rows, expected {want} "
                           f"— a partial pyramid is worse than none (investigate before trusting the drill).")
    return {"space": pyramid["space"], "rows": got}


def load_pyramid(store, space: str, emb: str | None = None) -> dict | None:
    """The persisted pyramid structure for `space` (at the embedder LAYER `emb`), or None if never built
    (an HONEST None — never a fabricated pyramid). RECONSTRUCTED from ledger.cluster_member rows (the
    structure's SQL home since 2026-07-03; the 7 legacy sidecars were loaded there once) — same dict shape
    the sidecar carried: {space, n_units, rungs:[{k, space, clusters:[{label, source, size, exemplar,
    members, children_finer}]}]}. Respects the store root's namespace (test stores see only their rows)."""
    from store.pg_marks import _psql, _dq
    ns = getattr(store, "_pg_ns", "")
    sp = ns + space
    embv = emb or "pplx"
    out = _psql("select k, cluster_address, member_address, is_exemplar, coalesce(parent_cluster,'') "
                f"from ledger.cluster_member where space={_dq(sp)} and emb={_dq(embv)} "
                "order by k desc, cluster_address")
    rows = [l.split("|") for l in out.splitlines() if l.count("|") >= 4]
    if not rows:
        return None
        # return store.load_scale_pyramid(space, emb)  # RETIRED 2026-07-03 (rows are the home; the sidecar
        #   read — restore by uncommenting only if the rows path must be rolled back)
    by_k: dict = {}
    parents: dict = {}
    for k, ca, m, ex, par in rows:
        c = by_k.setdefault(int(k), {}).setdefault(ca, {"source": ca, "members": [], "exemplar": None})
        c["members"].append(m)
        if ex == "t":
            c["exemplar"] = m
        if par:
            parents[ca] = par
    children: dict = {}
    for child, par in parents.items():
        children.setdefault(par, []).append(child)
    rungs = []
    n_units = 0
    for k in sorted(by_k):
        clusters = []
        for label, (ca, c) in enumerate(sorted(by_k[k].items())):
            rec = {"label": label, "source": ca, "size": len(c["members"]),
                   "exemplar": c["exemplar"], "members": c["members"]}
            if ca in children:
                rec["children_finer"] = sorted(children[ca])
            clusters.append(rec)
        rungs.append({"k": k, "space": f"scale:{space}:k{k}", "clusters": clusters})
        n_units = max(n_units, sum(len(c["members"]) for c in by_k[k].values()))
    return {"space": space, "n_units": n_units, "rungs": rungs, "unit_space": space}


def rung_points(store, space: str, k: int, emb: str | None = None) -> list:
    """The coarse POINTS at rung K — one per cluster: {source (cluster address), vector (centroid), size,
    exemplar, members}. The bridge feeds these to project() as pseudo-events so the SAME instrument
    (semantic radius, angle, centre) draws a coarse rung exactly as it draws units — zoom changes which rung
    RESOLVES, not which renderer runs. Reads the persisted centroids (no recompute). Fail-loud if the rung
    was never built (so a caller cannot silently render an empty coarse rung)."""
    pyr = load_pyramid(store, space, emb)
    if not pyr:
        raise ValueError(f"scale.rung_points: no pyramid built for space {space!r} (build_scale_pyramid first)")
    rec = next((r for r in pyr["rungs"] if r["k"] == k), None)
    if rec is None:
        raise ValueError(f"scale.rung_points: rung k={k} not in pyramid for {space!r} "
                         f"(rungs: {[r['k'] for r in pyr['rungs']]})")
    out = []
    for c in rec["clusters"]:
        v = store.get_vector(store.space_address(c["source"], rec["space"], emb))
        if v is None:
            raise ValueError(f"scale.rung_points: centroid vector missing for {c['source']!r} — pyramid "
                             f"structure and vector substrate disagree (rebuild build_scale_pyramid)")
        out.append({"source": c["source"], "vector": v["vector"], "size": c["size"],
                    "exemplar": c["exemplar"], "members": c["members"],
                    **({"children_finer": c["children_finer"]} if "children_finer" in c else {})})
    return out


def resolve_at_rung(store, query_vector: list, *, space: str, k: int | None = None, n: int = 5,
                    emb: str | None = None) -> dict:
    """RESOLVE a query at a rung — the zoom-by-rung query layer. k=None (or k>=n_units) → the UNIT rung
    (query_index over `space`: returns individual units). A coarse k → query_index over `scale:<space>:k<K>`:
    returns the nearest THEME(S) (cluster centroids, by their cluster `source`). SAME cosine, SAME
    query_index — only the space (the rung) changes. Returns {rung, ranked:[{id, score}], note}.

    `emb` = the embedder LAYER, threaded EXPLICITLY to query_index so the rung is queried at the SAME layer
    its pyramid was BUILT at (build_scale_pyramid's `emb`; default None = the bare layer). This must be passed
    — relying on query_index's default is a layer-consistency bug: query_index's omit-default is the system's
    DEFAULT_EMB_LAYER (pplx), which would query a different layer than a bare-built pyramid → empty ranked."""
    from store import vector_index as vx
    rung_space = space if (k is None) else f"scale:{space}:k{k}"
    res = vx.query_index(store, query_vector, k=n, space=rung_space, with_note=True, emb=emb)
    return {"rung": ("unit" if k is None else f"k{k}"), "space": rung_space, **res}


def rebuild_scale_pyramids(spaces: str = "docs,desc,code,symbol", emb_map: str = "") -> dict:
    """The PYRAMID-REBUILD job body (jobs HANDLERS registry): rebuild the named spaces' pyramids through
    the rows-forward path (incremental — unchanged centroids skip by content-hash). `spaces` = comma list;
    `emb_map` optional overrides "space:emb,…" (default: code/symbol→nomic-code, else pplx). Returns per-
    space results; a failed space is recorded + raised at the end (never silent)."""
    import os
    from store.fs_store import FsStore
    from fabric import config as fcfg
    st = FsStore(fcfg.STORE_DIR)
    emb_default = {"code": "nomic-code", "symbol": "nomic-code"}
    overrides = dict(p.split(":", 1) for p in emb_map.split(",") if ":" in p)
    out, errors = {}, []
    for sp in [s.strip() for s in spaces.split(",") if s.strip()]:
        emb = overrides.get(sp) or emb_default.get(sp, "pplx")
        try:
            r = build_scale_pyramid(st, space=sp, emb=emb)
            out[sp] = {"built": r["built"], "skipped": r["skipped"], "rows": r["member_rows"]}
        except Exception as e:
            errors.append(f"{sp}: {type(e).__name__}: {e}")
            out[sp] = {"error": str(e)[:160]}
    if errors:
        raise RuntimeError(f"rebuild_scale_pyramids: {len(errors)} space(s) failed — {errors} "
                           f"(the others' results: { {k: v for k, v in out.items() if 'error' not in v} })")
    return out
