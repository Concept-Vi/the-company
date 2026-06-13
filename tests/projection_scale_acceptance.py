"""projection_scale_acceptance — THE TEETH for Group 11 (THE MULTI-SCALE EMBEDDING PYRAMID) of THE
UNIVERSAL PROJECTION. Guards `runtime/scale.py` (agglomerate / build_scale_pyramid / resolve_at_rung) +
the store scale sidecar.

WHY (read before changing) — the metric this suite LOCKS, the trap it guards:
  · Group 11 is the SCALE axis: zoom out → resolve at a COARSER grain (themes), zoom in → units. The
    coarse rung = fewer, larger MEANING-regions = CLUSTERS of near points; a coarse point = the cluster
    centroid. (Lineage — unit⊂session⊂project — was the first plan; the per-space probe killed it: within
    a space `session` is capture-batch provenance, `project` is one point. So the honest coarsening is over
    MEANING, the same circle Group 6 built — not provenance.)
  · THE NESTING LOCK (§1, dispositive): the rungs must NEST — every fine cluster ⊂ exactly one coarse
    cluster — or zoom is a lie (units jumping themes between rungs = a fake pyramid). ONE agglomerative
    dendrogram cut at each rung gives this; independent per-K k-means does NOT. This suite proves the cuts
    of one tree nest. DO NOT replace agglomerate with per-K clustering — §1 would (correctly) fail.
  · THE WARD LOCK (§2): AVERAGE-linkage CHAINS on high-baseline-cosine embeddings (one cluster swallows
    the space); Ward gives BALANCED, discriminative clusters. §2 demonstrates the chaining on a synthetic
    so the choice of `ward` is guarded against a "simpler average" regression.
  · THE COARSE≠FINE LOCK (§4): a coarse-rung query must resolve to a genuinely COARSER/DIFFERENT result
    than the fine rung (a theme region containing the fine top-1, not the same unit). This is the
    distinctness gate the build was held to BEFORE the render was wired.
  · HERMETIC: a tmp FsStore seeded with deterministic synthetic BLOB vectors (well-separated themes) — NO
    live :8001, NO real store. build_scale_pyramid never calls the embedder (centroids are means of on-disk
    vectors), so this runs offline. The live topics-space pyramid is verified BY USE in the Group-11 beat.

Run:  ./.venv/bin/python tests/projection_scale_acceptance.py
"""
import math
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime import scale
from store import vector_index as vx

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}  {detail}")


# ── deterministic synthetic: B well-separated blobs, P points each, dim D. Each blob is a near-orthogonal
#    one-hot direction + a tiny index-derived jitter (NO randomness — reproducible build-to-build). Blob
#    points share a dominant axis → genuinely-near; blobs are mutually far → a real coarsening exists. ──
D = 12
B = 6
P = 6


def blob_vectors():
    vecs, truth = [], []          # truth[i] = which blob point i belongs to
    for b in range(B):
        for p in range(P):
            v = [0.0] * D
            v[b] = 10.0                                   # the blob's dominant axis (well separated)
            v[(b + 1) % D] += 0.5 + 0.03 * p              # tiny shared secondary lean
            v[(b * 7 + p) % D] += 0.15                    # tiny per-point jitter (deterministic)
            vecs.append(v)
            truth.append(b)
    return vecs, truth


print("§1 ONE-DENDROGRAM NESTING (every fine cluster ⊂ exactly one coarse cluster) ─────────────")
vecs, truth = blob_vectors()
nv, cuts = scale.agglomerate(vecs, linkage="ward")
n = len(vecs)
check("a snapshot exists for every cluster-count 1..n", all(k in cuts for k in range(1, n + 1)))
part6 = scale.cut(cuts, B)
part2 = scale.cut(cuts, 2)
g6 = scale.clusters_of(part6)
g2 = scale.clusters_of(part2)
check(f"cut at K={B} recovers {B} clusters", len(g6) == B, f"got {len(g6)}")
# NESTING: each fine cluster's points all share ONE coarse label
nested = all(len({part2[i] for i in members}) == 1 for members in g6.values())
check("every K=6 (fine) cluster sits wholly inside ONE K=2 (coarse) cluster — the cuts NEST", nested)
# and the fine cut recovers the planted blobs (well-separated → ward finds them)
recovered = all(len({truth[i] for i in members}) == 1 for members in g6.values())
check("the fine cut recovers the planted blobs (each cluster is one true blob)", recovered)

print("\n§2 WARD vs AVERAGE — ward stays BALANCED where average CHAINS ──────────────────────────")
# The chaining pathology that bit the REAL data (average absorbed 129/162 & 525/644 into one giant; ward
# gave 9/19/31): a DENSE core + scattered satellites reproduces it. Average nucleates on the core and
# absorbs the satellites one-by-one (nearest-neighbour chaining) → [giant, speck]; ward resists (merging a
# far satellite into the big core spikes within-cluster variance) → the natural core-vs-satellites split.
# This is WHY build_scale_pyramid defaults to ward; a regression to average would (correctly) fail here.
DD = 16
chain = ([[8.0] + [0.0] * (DD - 1) for _ in range(18)])        # 18-point dense core (high baseline)
for _i in range(18):
    chain[_i][1 + _i % 5] += 0.05                              # tiny intra-core jitter
for _s in range(6):                                            # 6 scattered, mutually-distant satellites
    v = [1.0] + [0.0] * (DD - 1)
    v[6 + _s] += 6.0
    chain.append(v)
_, cuts_avg = scale.agglomerate(chain, linkage="average")
_, cuts_ward = scale.agglomerate(chain, linkage="ward")
avg_sizes = sorted(len(m) for m in scale.clusters_of(scale.cut(cuts_avg, 2)).values())
ward_sizes = sorted(len(m) for m in scale.clusters_of(scale.cut(cuts_ward, 2)).values())
check("average-linkage CHAINS (a giant cluster + a speck) at K=2", avg_sizes[0] <= 2, f"avg sizes={avg_sizes}")
check("ward-linkage stays BALANCED — keeps the satellite group, no speck", min(ward_sizes) >= 5, f"ward sizes={ward_sizes}")
check("ward's largest cluster is smaller than average's giant (less chaining)",
      max(ward_sizes) < max(avg_sizes), f"ward={ward_sizes} avg={avg_sizes}")
check("build_scale_pyramid's production linkage default is ward",
      (scale.build_scale_pyramid.__kwdefaults__ or {}).get("linkage") == "ward")

print("\n§3 CENTROID = normalised mean of members (lives on the unit sphere; a real member names it) ──")
members0 = g6[next(iter(g6))]
c = scale.centroid(nv, members0)
check("centroid is unit-norm (‖c‖≈1)", abs(math.sqrt(sum(x * x for x in c)) - 1.0) < 1e-9)
# the centroid is nearer its OWN members than a foreign blob's points
other = next(m for lab, ms in g6.items() for m in ms if truth[ms[0]] != truth[members0[0]])
own = sum(scale._cos(nv[i], c) for i in members0) / len(members0)
check("centroid is closer to its own members than to a foreign blob's point",
      own > scale._cos(nv[other], c), f"own={own:.3f} foreign={scale._cos(nv[other], c):.3f}")
try:
    scale.centroid(nv, [])
    check("centroid([]) fails loud (no zero-vector centroid)", False)
except ValueError:
    check("centroid([]) fails loud (no zero-vector centroid)", True)

print("\n§4 COARSE ≠ FINE RESOLUTION over a real store (the distinctness gate) ────────────────────")
tmp = tempfile.mkdtemp(prefix="scale_acc_")
try:
    from store.fs_store import FsStore
    store = FsStore(tmp)
    SP = "probe"
    # seed the UNIT vectors (space='probe') — exactly what Group 8's capture would have persisted
    for i, v in enumerate(vecs):
        src = f"unit://probe/{truth[i]}/{i}"
        store.put_vector(store.space_address(src, SP), scale._norm(v), vx.content_hash(f"u{i}"),
                         dim=D, model="synthetic", space=SP, source=src)
    res = scale.build_scale_pyramid(store, space=SP, rungs=[B, 2])
    check("build reports the 2 requested rungs", sorted(r["k"] for r in res["pyramid_rungs"]) == [2, B])
    check("the coarse vectors were persisted (scale:probe:k6 has B centroids)",
          len(store.index_addresses(space=f"scale:{SP}:k{B}")) == B,
          f"got {len(store.index_addresses(space=f'scale:{SP}:k{B}'))}")
    # ADDITIVE: building the pyramid did NOT touch the unit space
    check("the UNIT space is untouched by the build (additive)",
          len(store.index_addresses(space=SP)) == n)

    # a query planted IN blob 0
    q = scale._norm(vecs[0])
    fine = scale.resolve_at_rung(store, q, space=SP, k=None, n=5)          # the UNIT rung
    coarse = scale.resolve_at_rung(store, q, space=SP, k=B, n=1)            # the THEME rung
    fine_ids = [r["id"] for r in fine["ranked"]]
    coarse_cluster = coarse["ranked"][0]["id"]                             # a cluster:// address
    check("the FINE rung resolves to individual UNITS", all(x.startswith("unit://") for x in fine_ids))
    check("the COARSE rung resolves to a THEME (a cluster address), not a unit",
          coarse_cluster.startswith("cluster://"), coarse_cluster)
    check("fine top-1 and coarse top-1 are DIFFERENT objects (genuinely different grain)",
          fine_ids[0] != coarse_cluster)
    # the coarse theme CONTAINS the fine top-1 (the pyramid is a faithful coarsening, not a different field)
    pyr = scale.load_pyramid(store, SP)
    rung6 = next(r for r in pyr["rungs"] if r["k"] == B)
    theme = next(cl for cl in rung6["clusters"] if cl["source"] == coarse_cluster)
    check("the coarse theme is a REGION (size > 1), genuinely coarser than a unit", theme["size"] > 1)
    check("the coarse theme CONTAINS the fine top-1 unit (faithful coarsening: the theme holds the point)",
          fine_ids[0] in theme["members"], f"top1={fine_ids[0]} members={theme['members']}")

    # DISCRIMINATIVE: queries planted in DIFFERENT blobs resolve to DIFFERENT coarse themes
    resolved = set()
    for b in range(B):
        qb = scale._norm(vecs[b * P])
        rb = scale.resolve_at_rung(store, qb, space=SP, k=B, n=1)
        resolved.add(rb["ranked"][0]["id"])
    check("queries in different blobs resolve to different coarse themes (no collapse to one sink)",
          len(resolved) == B, f"{len(resolved)} distinct of {B}")

    print("\n§5 NESTING is PERSISTED (cross-rung parent links) + INCREMENTAL rebuild ──────────────")
    rung2 = next(r for r in pyr["rungs"] if r["k"] == 2)
    # every k=6 cluster names a parent at k=2 via children_finer on the coarse rung
    coarse_children = sorted({src for cl in rung2["clusters"] for src in cl.get("children_finer", [])})
    fine_sources = sorted(cl["source"] for cl in rung6["clusters"])
    check("the coarse rung records its finer children (nesting is persisted, not inferred)",
          coarse_children == fine_sources, f"children={coarse_children}\nfine={fine_sources}")
    # incremental: a second build with unchanged members re-persists NOTHING
    res2 = scale.build_scale_pyramid(store, space=SP, rungs=[B, 2])
    check("an unchanged rebuild re-persists no centroids (incremental, content-hash keyed)",
          res2["built"] == 0 and res2["skipped"] == (B + 2), f"built={res2['built']} skipped={res2['skipped']}")

    print("\n§6 FAIL LOUD + derived dyadic rungs ──────────────────────────────────────────────────")
    try:
        scale.build_scale_pyramid(store, space="does-not-exist")
        check("a pyramid over an EMPTY space fails loud", False)
    except ValueError:
        check("a pyramid over an EMPTY space fails loud", True)
    try:
        scale.rung_points(store, SP, 999)
        check("rung_points on a non-existent rung fails loud", False)
    except ValueError:
        check("rung_points on a non-existent rung fails loud", True)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

check("default_rungs is dyadic + derived (n=162 → [32, 8])", scale.default_rungs(162) == [32, 8],
      f"got {scale.default_rungs(162)}")
check("default_rungs returns [] for a space too thin to coarsen honestly", scale.default_rungs(5) == [])
check("default_rungs grows with n (every rung a power of two, descending)",
      all((k & (k - 1)) == 0 for k in scale.default_rungs(644)) and
      scale.default_rungs(644) == sorted(scale.default_rungs(644), reverse=True),
      f"got {scale.default_rungs(644)}")
try:
    scale.agglomerate([[1.0]], linkage="nope")
    check("agglomerate rejects an unknown linkage (fail loud)", False)
except ValueError:
    check("agglomerate rejects an unknown linkage (fail loud)", True)
try:
    scale._cos([1.0, 0.0], [1.0])
    check("_cos fails loud on a dim mismatch (no silent-truncate wrong cosine)", False)
except ValueError:
    check("_cos fails loud on a dim mismatch (no silent-truncate wrong cosine)", True)

print(f"\n{'PASS' if FAIL == 0 else 'FAIL'} — {PASS} passed, {FAIL} failed "
      f"(Group 11 multi-scale pyramid: ONE dendrogram → nested rungs, ward-not-chaining, centroid=normed "
      f"mean, coarse≠fine resolution over a real store, discriminative themes, persisted nesting, "
      f"incremental, fail-loud, derived dyadic rungs. Live topics pyramid verified by use.)")
sys.exit(1 if FAIL else 0)
