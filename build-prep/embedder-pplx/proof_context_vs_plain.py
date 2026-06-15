#!/usr/bin/env python3
"""PROVE the context-as-parent-context upgrade (Tim's #4) — using the EXISTING :8007 contextual endpoint
(no server change, no restart). Embed the 29 OPERATORS two ways and compare:
  PLAIN   = each role embedded ALONE        (POST /v1/embeddings {input:[...]})
  CONTEXT = all 29 as ONE parent-group      (POST /v1/embeddings {documents:[[...29...]]}) — late chunking:
            each role's vector is informed by ALL its siblings (the registry as its parent).
Question: does embedding a thing IN THE CONTEXT OF ITS PARENT make the operator-families more coherent/
separable? If yes → Tim's fractal upgrade is real for non-document things.
"""
import os, ast, glob, json, math, urllib.request
import sys; sys.path.insert(0, "/home/tim/company")
from runtime import scale

ROLES_DIR = "/home/tim/company/roles"
URL = "http://127.0.0.1:8007/v1/embeddings"
MODEL = "perplexity-ai/pplx-embed-context-v1-4b"

def role_text(path):
    src = open(path).read(); tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "ROLE" for t in node.targets):
            d = {}
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant):
                    try: d[k.value] = ast.literal_eval(v)
                    except Exception: d[k.value] = None
            if not d.get("id"): return None, None
            parts = [f"{d.get('label') or d['id']}."]
            for key in ("description", "trigger", "output", "context"):
                if d.get(key): parts.append(str(d[key]))
            return d["id"], " ".join(p.strip() for p in parts if p)
    return None, None

ids, texts = [], []
for p in sorted(glob.glob(os.path.join(ROLES_DIR, "*.py"))):
    if os.path.basename(p).startswith("_"): continue
    rid, txt = role_text(p)
    if rid and txt: ids.append(rid); texts.append(txt)
print(f"{len(ids)} operators")

def post(body):
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())

# PLAIN — each alone
plain_resp = post({"input": texts, "model": MODEL, "quantization": "int8"})
P = [d["embedding"] for d in sorted(plain_resp["data"], key=lambda d: d["index"])]
# CONTEXT — all 29 as one parent-group (one document, 29 chunks)
ctx_resp = post({"documents": [texts], "model": MODEL, "quantization": "int8"})
# rows are (document=0, chunk=i) in order
C = [d["embedding"] for d in sorted(ctx_resp["data"], key=lambda d: (d.get("meta",{}).get("document",0), d.get("meta",{}).get("chunk", d["index"])))]
print(f"PLAIN dim={len(P[0])}  CONTEXT dim={len(C[0])}  (n={len(P)},{len(C)})")
assert len(P) == len(C) == len(ids), "row count mismatch"

def cos(a, b):
    d = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a)); nb = math.sqrt(sum(x*x for x in b))
    return d/(na*nb) if na and nb else 0.0

# 1) did context MOVE each vector? (proves late-chunking is doing something)
shifts = [(ids[i], cos(P[i], C[i])) for i in range(len(ids))]
shifts.sort(key=lambda x: x[1])
print("\n[1] CONTEXT vs PLAIN per-role cosine (lower = context moved it more):")
for rid, c in shifts[:6]: print(f"    moved most: {rid:20} cos(plain,context)={c:.3f}")
print(f"    mean cos(plain,context) = {sum(c for _,c in shifts)/len(shifts):.3f}  (1.0 = no change)")

# 2) family partition from PLAIN clustering; measure separability margin in PLAIN vs CONTEXT
def margin(vecs, groups):
    intra, inter, ni, ne = 0.0, 0.0, 0, 0
    members = [m for g in groups.values() for m in g]
    for gi, g in groups.items():
        for a in range(len(g)):
            for b in range(a+1, len(g)):
                intra += cos(vecs[g[a]], vecs[g[b]]); ni += 1
        others = [m for gj, gg in groups.items() if gj != gi for m in gg]
        for a in g:
            for o in others:
                inter += cos(vecs[a], vecs[o]); ne += 1
    mi = intra/ni if ni else 0; me = inter/ne if ne else 0
    return mi, me, mi - me

_, cuts = scale.agglomerate(P, linkage="ward")
part = scale.cut(cuts, 8)
groups = scale.clusters_of(part)
pi, pe, pm = margin(P, groups)
ci, ce, cm = margin(C, groups)
print("\n[2] operator-FAMILY separability (same partition from PLAIN clustering), intra - inter cosine:")
print(f"    PLAIN  : intra={pi:.3f} inter={pe:.3f}  margin={pm:.3f}")
print(f"    CONTEXT: intra={ci:.3f} inter={ce:.3f}  margin={cm:.3f}")
print(f"    Δmargin (context - plain) = {cm-pm:+.3f}   → {'CONTEXT MORE SEPARABLE ✓' if cm>pm else 'no improvement'}")

# 3) concrete: for each role, did context pull it TOWARD its own family centroid (vs others)?
def centroid(idxs, vecs):
    n=len(idxs); dim=len(vecs[0]); return [sum(vecs[i][k] for i in idxs)/n for k in range(dim)]
id2fam = {m: gi for gi, g in groups.items() for m in g}
toward = 0
for i in range(len(ids)):
    fam = [m for m in groups[id2fam[i]] if m != i] or [i]
    own_c = centroid(fam, P)  # own family centroid (from plain, excluding self)
    # nearest OTHER family centroid (plain)
    others = [centroid(g, P) for gi, g in groups.items() if gi != id2fam[i]]
    near_other = max((cos(P[i], oc) for oc in others), default=0)
    # plain margin to own vs nearest-other; context margin
    pm_i = cos(P[i], own_c) - near_other
    cm_i = cos(C[i], own_c) - max((cos(C[i], oc) for oc in others), default=0)
    if cm_i > pm_i: toward += 1
print(f"\n[3] {toward}/{len(ids)} roles sit MORE clearly inside their family under CONTEXT than PLAIN.")
print("\n=== READ: if Δmargin > 0 and most roles tighten, embedding-in-parent-context is a real upgrade for non-document things. ===")
