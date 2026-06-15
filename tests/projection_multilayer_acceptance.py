"""projection_multilayer_acceptance — THE TEETH for the MULTI-LAYER embedding model + the MRL RESOLUTION
axis + the ONE-ENGINE projection door (bridge.build_projection ↔ Suite.project — both faces, no parallel
projector). LIVE-STORE integration (tests/AGENTS.md: "prove by USE — operate the live system"), guarding the
regressions this capability is prone to — each one a real bug this fire either fixed or could re-introduce:

  · CWD-INDEPENDENCE [fix 3b57981]: build_projection must discover bindings by an ABSOLUTE path. A cwd-relative
    default silently fell back to the 'raw' lens for EVERY binding in the MCP server process (its cwd ≠ repo
    root) — the door looked alive but returned raw kinds for every lens. This is the headline guard.
  · MULTI-LAYER read: emb= selects a real embedder LAYER (binding.emb echoed; a named layer is a real, distinct
    vector set — registry-true via the store self-scan), never silently ignored.
  · MRL ?dim= APPLIED on the vector lenses semantic + separator (added this fire — was nucleation-only):
    truncating to N dims actually MOVES the radii / leans (never a silent no-op); binding.res echoed.
  · ONE ENGINE: Suite.project / Suite.layers / Suite.layer_dims (the MCP door's call path) route to the SAME
    resolver / store self-scan the bridge HTTP face uses — reuse-don't-parallel.

Data-presence GUARDED: the layer/MRL checks SKIP (noted) when the named layer or enough embedded items aren't
present, so the suite fails on a CODE regression, never on absent optional data. The full FE drive + the visible
re-projection are verified BY USE in the browser (the design-critic record); this is the permanent backstop.

Run:  ./.venv/bin/python tests/projection_multilayer_acceptance.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = 0
FAIL = 0
SKIP = 0
EPS = 1e-6


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}  {detail}")


def skip(name, why):
    global SKIP
    SKIP += 1
    print(f"  ⊘ {name}  (skipped: {why})")


from store.fs_store import FsStore
from runtime.suite import Suite
from runtime.registry import NodeRegistry
from fabric import config as fcfg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE = FsStore(fcfg.STORE_DIR)
SUITE = Suite(STORE, NodeRegistry().discover([os.path.join(ROOT, "nodes")]))


def by_src(body):
    out = {}
    for p in body.get("points", []):
        k = p.get("source") or p.get("address")
        if k:
            out[k] = p
    return out


# ════════════════════════════════════════════════════════════════════════════════════════════════════
# 1 · CWD-INDEPENDENCE — build_projection discovers ALL bindings by absolute path (regression 3b57981)
#     Emulate the MCP server: chdir away from the repo root, then every binding must resolve to its OWN id,
#     never the synthesized 'raw' fallback (the silent break that made the MCP door return raw for everything).
# ════════════════════════════════════════════════════════════════════════════════════════════════════
print("\n1 · cwd-independence (the MCP-door regression guard)")
_cwd = os.getcwd()
ids = []
try:
    os.chdir(tempdir := "/tmp")
    from runtime import bridge  # constructs the bridge's Suite over the ABSOLUTE store — safe from any cwd

    _, b_raw = bridge.build_projection({"binding": "raw", "limit": "1"})
    ids = [x["id"] for x in b_raw.get("bindings", [])]
    check("from a wrong cwd, >1 binding is discovered (NOT the raw-only fallback)", len(ids) > 1, f"got {ids}")
    bad = [bid for bid in ids
           if bridge.build_projection({"binding": bid, "limit": "5"})[1].get("binding", {}).get("id") != bid]
    check("from a wrong cwd, EVERY discovered binding resolves to its own id (no silent raw fallback)",
          not bad, f"fell back to raw: {bad}")
finally:
    os.chdir(_cwd)

# ════════════════════════════════════════════════════════════════════════════════════════════════════
# 2 · layer_dims contract + ONE-engine self-scan (Suite == store)
# ════════════════════════════════════════════════════════════════════════════════════════════════════
print("\n2 · the layer self-description (layers + dims), via both the store and the Suite")
layers = STORE.layers_by_space()
dims = STORE.layer_dims()
check("layers_by_space() = {space:[emb,…]} non-empty", isinstance(layers, dict) and len(layers) > 0, str(list(layers)[:3]))
check("layer_dims() = {space:{emb:dim}} with positive int dims",
      isinstance(dims, dict) and len(dims) > 0
      and all(isinstance(d, int) and d > 0 for grp in dims.values() for d in grp.values()))
check("layer_dims spaces/layers ⊆ layers_by_space (one self-scan, two views)",
      all(sp in layers and set(dims[sp]).issubset(set(layers[sp])) for sp in dims))
check("Suite.layers() == store.layers_by_space() (the MCP door reads the SAME self-scan)", SUITE.layers() == layers)
check("Suite.layer_dims() == store.layer_dims() (the MCP door reads the SAME self-scan)", SUITE.layer_dims() == dims)

# ════════════════════════════════════════════════════════════════════════════════════════════════════
# 3 · ONE ENGINE — Suite.project routes to bridge.build_projection (reuse-don't-parallel, both faces)
# ════════════════════════════════════════════════════════════════════════════════════════════════════
print("\n3 · one engine, two faces (Suite.project ↔ bridge.build_projection)")
_, sp_body = SUITE.project({"binding": "raw", "limit": "5"})
_, bp_body = bridge.build_projection({"binding": "raw", "limit": "5"})
check("Suite.project == bridge.build_projection on raw (same binding id + count — the SAME resolver)",
      sp_body.get("binding", {}).get("id") == bp_body.get("binding", {}).get("id")
      and sp_body.get("count") == bp_body.get("count"))

# ════════════════════════════════════════════════════════════════════════════════════════════════════
# 4 · MULTI-LAYER read + 5 · MRL applied on semantic + separator (guarded by data presence)
# ════════════════════════════════════════════════════════════════════════════════════════════════════
print("\n4–5 · the multi-layer read + the MRL resolution axis (semantic + separator)")
# a space carrying BOTH the default layer AND a named layer (e.g. pplx) — the multi-layer condition
dual = next(((sp, sorted(e for e in es if e != "default")[0]) for sp, es in layers.items()
             if "default" in es and any(e != "default" for e in es)), None)
if not dual:
    skip("multi-layer + MRL (semantic/separator)", "no space carries both 'default' and a named layer")
else:
    sp, named = dual
    print(f"    (dual-layer space: {sp!r}, named layer: {named!r})")
    # candidate item addresses in this space@layer (semantic no-centre → rim points carrying their source)
    _, seed = bridge.build_projection({"binding": "semantic", "space": sp, "emb": named, "limit": "40"})
    cands = list(by_src(seed).keys())
    check(f"semantic@{named} on {sp!r}: binding.emb echoes the requested layer (the layer is not ignored)",
          seed.get("binding", {}).get("emb") == named, f"emb={seed.get('binding', {}).get('emb')!r}")
    if len(cands) < 2:
        skip("MRL semantic + separator", f"need ≥2 embedded items in {sp}@{named}; got {len(cands)}")
    else:
        centre = cands[0]
        # ---- SEMANTIC: radii (meaning-distance from the centre) must MOVE between full and dim=128 ----
        _, sf = bridge.build_projection({"binding": "semantic", "space": sp, "emb": named, "center": centre, "limit": "40"})
        _, s1 = bridge.build_projection({"binding": "semantic", "space": sp, "emb": named, "center": centre, "dim": "128", "limit": "40"})
        pf, p1 = by_src(sf), by_src(s1)
        common = [k for k in pf if k in p1 and k != centre]
        moved = sum(1 for k in common if abs((pf[k].get("r") or 0) - (p1[k].get("r") or 0)) > EPS)
        check("MRL semantic: res echoed (full→None, dim=128→128)",
              sf["binding"].get("res") in (None, "") and s1["binding"].get("res") == 128)
        check("MRL semantic: dim=128 MOVES the meaning-radii (truncation applied, not a no-op)",
              common and moved >= max(1, len(common) // 3), f"{moved}/{len(common)} radii moved")
        # ---- SEPARATOR: the signed lean must MOVE between full and dim=128 ----
        pa, pb = cands[0], cands[1]
        _, ff = bridge.build_projection({"binding": "by_separator", "space": sp, "emb": named, "pole_a": pa, "pole_b": pb, "limit": "40"})
        _, f1 = bridge.build_projection({"binding": "by_separator", "space": sp, "emb": named, "pole_a": pa, "pole_b": pb, "dim": "128", "limit": "40"})
        af, a1 = by_src(ff), by_src(f1)
        commons = [k for k in af if k in a1]
        lean = lambda p: p.get("lean") if p.get("lean") is not None else p.get("r")
        lmoved = sum(1 for k in commons if abs((lean(af[k]) or 0) - (lean(a1[k]) or 0)) > EPS)
        check("MRL separator: res echoed (full→None, dim=128→128)",
              ff["binding"].get("res") in (None, "") and f1["binding"].get("res") == 128)
        check("MRL separator: dim=128 MOVES the signed leans (truncation applied, not a no-op)",
              commons and lmoved >= max(1, len(commons) // 3), f"{lmoved}/{len(commons)} leans moved")

        # ════════════════════════════════════════════════════════════════════════════════════════════════
        # 6 · BINARY QUANTIZATION (the REPRESENTATION axis) — sign(±1)-through-cosine = Hamming similarity.
        #     quant=binary must: be echoed; MOVE the projection (not a no-op); COMPOSE with dim; full=None.
        #     (Fidelity — that binary preserves neighborhood structure — is proven separately: NN@10 0.81/0.70.)
        # ════════════════════════════════════════════════════════════════════════════════════════════════
        print("\n6 · binary quantization (the representation axis)")
        _, sq = bridge.build_projection({"binding": "semantic", "space": sp, "emb": named, "center": centre, "quant": "binary", "limit": "40"})
        pq = by_src(sq)
        commonq = [k for k in pf if k in pq and k != centre]
        qmoved = sum(1 for k in commonq if abs((pf[k].get("r") or 0) - (pq[k].get("r") or 0)) > EPS)
        check("BQ semantic: quant echoed (full→None, binary→'binary')",
              sf["binding"].get("quant") in (None, "") and sq["binding"].get("quant") == "binary")
        check("BQ semantic: quant=binary MOVES the meaning-radii (sign-bit Hamming applied, not a no-op)",
              commonq and qmoved >= max(1, len(commonq) // 3), f"{qmoved}/{len(commonq)} radii moved")
        # all ±1 → cos(sign a, sign b) ∈ [-1,1] → the normalized radius stays in the valid band (never NaN/blowup)
        check("BQ semantic: binary radii stay in the valid [0,1.2] band (the ±1 cosine is well-formed)",
              all(0.0 <= (pq[k].get("r") or 0) <= 1.2 for k in commonq))
        # COMPOSES with dim: binary + dim=128 is a distinct read (binarize the first 128 dims), both echoed
        _, sqd = bridge.build_projection({"binding": "semantic", "space": sp, "emb": named, "center": centre, "quant": "binary", "dim": "128", "limit": "40"})
        check("BQ semantic: composes with MRL (quant=binary & dim=128 → both echoed)",
              sqd["binding"].get("quant") == "binary" and sqd["binding"].get("res") == 128)
        # NUCLEATION: binary is a real alternate read (quant echoed; report present) — registry-true on a layer
        _, nq = bridge.build_projection({"binding": "by_nucleation", "types_space": "operators", "space": "repo", "emb": "pplx", "rung": "8", "quant": "binary", "limit": "10"})
        check("BQ nucleation: quant=binary echoed + the report still resolves (Hamming admission radii)",
              nq["binding"].get("quant") == "binary" and "nucleation" in nq and "candidates" in nq["nucleation"])

print(f"\n{'PASS' if FAIL == 0 else 'FAIL'} — {PASS} passed, {FAIL} failed, {SKIP} skipped")
sys.exit(0 if FAIL == 0 else 1)
