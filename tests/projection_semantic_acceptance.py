"""projection_semantic_acceptance — THE TEETH for Group 6 (THE CIRCLE / semantic radius) of THE
UNIVERSAL PROJECTION. Guards `runtime/projection.py:project(..., vectors=)` with radius_from='semantic'.

WHY (read before changing):
  · Group 6 makes radius = MEANING-distance from the centre (1 - cosine), read off the per-space vectors
    the caller passes in (project stays PURE — vectors ride in like events; the store I/O is the bridge's).
  · The CENTRE's own cosine is 1.0 — an OUTLIER. The first build normalized over ALL cosines incl. the
    centre, so sem_cmax=1.0 compressed every real neighbour into the OUTER band and left the inner radius
    EMPTY (verified in-browser: nearest real neighbour at r≈0.39, inner 39% dead). THE FIX: exclude the
    centre from the normalization band → the nearest neighbour maps near the origin, the field uses the
    FULL radius. The empty-core regression guard (§2) is the whole point of this suite — do not weaken it.
  · HERMETIC: synthetic vectors, no live :8001, no store. The live model+embed path is verified BY USE in
    the Group-6 beat (center=suite.py over the topics space: 162 points, centre at 0, full spread).

Run:  ./.venv/bin/python tests/projection_semantic_acceptance.py
"""
import math
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime.projection import BindingRegistry, project

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


NOW = datetime(2026, 6, 14, 12, 0, 0, tzinfo=timezone.utc)
SEM = {"id": "semantic", "label": "Meaning", "angle_from": "kind", "radius_from": "semantic", "space": "topics"}


def vec_at(cos):
    """A 2D unit vector whose cosine with [1,0] is `cos` (so I can dial exact cosines)."""
    return [cos, math.sqrt(max(1.0 - cos * cos, 0.0))]


def corpus_ev(seq, src, age_s=100):
    """A corpus.record-shaped event: address is the run:// record, source_address the embeddable item."""
    t = NOW - timedelta(seconds=age_s)
    return {"seq": seq, "kind": "corpus.record", "ts": t.isoformat(),
            "address": f"run://corpus/company/{src}/topics", "source_address": src,
            "summary": f"rec-{seq}"}


# Centre = code://C (cos 1.0). Neighbours clustered in [0.59, 0.84] (the real-corpus shape: a tight band
# well below 1.0). One point (X) has NO vector. The centre is also a projected point (its own record).
CENTER = "code://C"
events = [corpus_ev(0, "code://C"), corpus_ev(1, "code://N1"), corpus_ev(2, "code://N2"),
          corpus_ev(3, "code://N3"), corpus_ev(4, "code://X")]
COS = {"code://C": 1.0, "code://N1": 0.84, "code://N2": 0.70, "code://N3": 0.59}   # X absent (no vector)
# vectors keyed by _addr_of(e) (= the run:// address) for the points, PLUS the centre keyed by `center`.
vectors = {f"run://corpus/company/{src}/topics": vec_at(c) for src, c in COS.items()}
vectors[CENTER] = vec_at(1.0)

res = project(events, binding=SEM, center=CENTER, vectors=vectors, now=NOW, registry=BindingRegistry())
by_src = {p["address"]: p for p in res["points"]}
rC = by_src["run://corpus/company/code://C/topics"]["r"]
rN1 = by_src["run://corpus/company/code://N1/topics"]["r"]
rN2 = by_src["run://corpus/company/code://N2/topics"]["r"]
rN3 = by_src["run://corpus/company/code://N3/topics"]["r"]
pX = by_src["run://corpus/company/code://X/topics"]

print("=== 1 · the semantic floor: centre at origin, monotone, full radius, surfaced ===")
check("binding.radius_from reports 'semantic'", res["binding"]["radius_from"] == "semantic")
check("radius_normalized is surfaced True (honest about the min-max stretch)",
      res["binding"].get("radius_normalized") is True)
check("the CENTRE item is at the origin (r == 0)", abs(rC - 0.0) < 1e-9, f"rC={rC}")
check("radius is MONOTONE in meaning-distance (nearer cosine → smaller r): N1<N2<N3",
      rN1 < rN2 < rN3, f"N1={rN1} N2={rN2} N3={rN3}")
check("the FARTHEST neighbour reaches the rim (r == 1.0)", abs(rN3 - 1.0) < 1e-9, f"rN3={rN3}")
check("every r ∈ [0,1]", all(0.0 <= p["r"] <= 1.0 for p in res["points"]))

print("=== 2 · THE EMPTY-CORE REGRESSION GUARD: the centre 1.0 outlier is EXCLUDED from the band ===")
# With the centre in the band, sem_cmax=1.0 → nearest neighbour r = 1-(0.84-0.59)/(1.0-0.59) ≈ 0.39 (the
# bug: inner 39% empty). Excluding it → nearest maps to the 0.06 floor. Assert the FIX, not the bug.
check("nearest neighbour sits NEAR the origin (≈0.06), NOT compressed to ≈0.39 (the empty-core bug)",
      rN1 < 0.15, f"rN1={rN1} (must be ~0.06; ≥0.15 means the centre outlier is back in the band)")
check("the inner half of the radius is POPULATED (a neighbour with r < 0.5 exists)",
      any(0.0 < p["r"] < 0.5 for p in res["points"]), "inner core empty → the compression failure")

print("=== 3 · a point with NO vector → rim + FLAGGED (never silent-dropped) ===")
check("the vectorless point X is at the rim (r == 1.0)", abs(pX["r"] - 1.0) < 1e-9, f"rX={pX['r']}")
check("X carries r_unknown=True (honest: meaning-distance unknown)", pX.get("r_unknown") is True)
check("a point WITH a vector does NOT carry r_unknown", "r_unknown" not in by_src["run://corpus/company/code://N1/topics"])

print("=== 4 · FAIL-LOUD: semantic with no centre vector RAISES (no silent fallback to time) ===")
def _no_centre():
    project(events, binding=SEM, center=None, vectors=vectors, now=NOW, registry=BindingRegistry())
def _centre_missing_vec():
    project(events, binding=SEM, center="code://NOT-EMBEDDED", vectors=vectors, now=NOW, registry=BindingRegistry())
raised1 = raised2 = False
try: _no_centre()
except ValueError: raised1 = True
try: _centre_missing_vec()
except ValueError: raised2 = True
check("center=None RAISES (semantic needs a centre to measure FROM)", raised1)
check("a centre with no vector in the space RAISES (never a faked radius)", raised2)

print("=== 5 · ADDITIVE: a non-semantic binding ignores `vectors` (raw still time-based) ===")
raw = BindingRegistry().discover().get("raw")
res_raw = project(events, binding=raw, now=NOW, vectors=vectors, registry=BindingRegistry())
check("raw binding (vectors passed) still reports radius_from='time' (semantic path is gated)",
      res_raw["binding"]["radius_from"] == "time")
check("raw binding carries NO radius_normalized key (semantic-only field)",
      "radius_normalized" not in res_raw["binding"])

print("=== 6 · STRAIN (Group 7, SEED §111): |r_struct - r_semantic| — coincidence=coherent, gap=strain ===")
# A fixture with VARIED tree-distance from the centre (the prior fixture's items are all siblings, so it
# can't show a structural gradient). C = centre. COH = same subtree + near in MEANING (coherent). DIV =
# same subtree but FAR in meaning (the divergence §111 is about). FAR = far in tree AND far in meaning
# (coherent — they AGREE it's far). The dispositive check: the centre — the MOST coherent point — is 0,
# not max (the bug the 2D cell↔wheel form would have produced).
sC, sCOH, sDIV, sFAR = "code://a/b/c/C", "code://a/b/c/COH", "code://a/b/c/DIV", "code://z/FAR"
sevents = [corpus_ev(0, sC), corpus_ev(1, sCOH), corpus_ev(2, sDIV), corpus_ev(3, sFAR)]
SCOS = {sC: 1.0, sCOH: 0.84, sDIV: 0.60, sFAR: 0.59}
svec = {f"run://corpus/company/{s}/topics": vec_at(c) for s, c in SCOS.items()}
svec[sC] = vec_at(1.0)
sres = project(sevents, binding=SEM, center=sC, vectors=svec, now=NOW, registry=BindingRegistry())
sp = {p["address"].split("/company/")[1].rsplit("/topics", 1)[0]: p for p in sres["points"]}
strain = {k: sp[k].get("strain") for k in (sC, sCOH, sDIV, sFAR)}
rstruct = {k: sp[k].get("r_struct") for k in (sC, sCOH, sDIV, sFAR)}
check("the CENTRE — the most coherent point — has strain ≈ 0 (NOT max: the 2D-noise bug is gone)",
      strain[sC] is not None and strain[sC] < 1e-6, f"centre strain={strain[sC]}")
check("a COHERENT point (same subtree + near in meaning) has strain ≈ 0",
      strain[sCOH] is not None and strain[sCOH] < 0.1, f"COH strain={strain[sCOH]} (r={sp[sCOH]['r']} r_struct={rstruct[sCOH]})")
check("a DIVERGENT point (near in TREE, far in MEANING) has HIGH strain",
      strain[sDIV] is not None and strain[sDIV] > 0.5, f"DIV strain={strain[sDIV]}")
check("strain is about DISAGREEMENT, not distance: far-in-tree + far-in-meaning is COHERENT (low strain)",
      strain[sFAR] is not None and strain[sFAR] < 0.1, f"FAR strain={strain[sFAR]}")
check("every strain ∈ [0,1]", all(0.0 <= s <= 1.0 for s in strain.values() if s is not None))
check("a point carries BOTH r (where it means) and r_struct (where it's filed)",
      all(sp[k].get("r") is not None and sp[k].get("r_struct") is not None for k in (sCOH, sDIV)))
# strain is semantic-only + vector-gated (a vectorless point has no meaning-position → no strain)
res_x = by_src["run://corpus/company/code://X/topics"]
check("a vectorless point carries NO strain (no fabricated coherence)", "strain" not in res_x)
res_raw2 = project(events, binding=raw, now=NOW, vectors=vectors, registry=BindingRegistry())
check("a non-semantic binding emits NO strain (the circle must be MEANING)",
      all("strain" not in p for p in res_raw2["points"]))

print(f"\n{'PASS' if FAIL == 0 else 'FAIL'} — {PASS} passed, {FAIL} failed "
      f"(Group 6 semantic radius + Group 7 strain: origin-centred, monotone, full-radius, centre-outlier "
      f"excluded, vectorless→rim+flag, fail-loud, additive; strain = |filed - means|, centre/coherent≈0, "
      f"divergence high, semantic-gated. Live path verified by use.)")
sys.exit(1 if FAIL else 0)
