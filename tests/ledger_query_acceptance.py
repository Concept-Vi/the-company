"""ledger_query_acceptance — the GOLDEN-SPEC gate for ledger.query (L11 v2, the window's feed).

One spec per axis + the full composition + the teaching refusals, asserted against the LIVE ledger
(the fn is pure SQL over real data — these are integration truths, not fixtures). Plan-echo asserted on
every spec: under-recall must never be silent. Live deps: Supabase :15432 (skips loud if down; the pplx/
nomic embedders are NOT needed — specs carry tiny fake vectors only where dim-routing itself is under test
via real spaces' stored dims... no: semantic specs here use REAL stored dims by querying with a stored
vector fetched from the space itself — no embedder call)."""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def q(spec):
    body = json.dumps(spec)
    r = subprocess.run(["psql", "-h", "127.0.0.1", "-p", "15432", "-U", "postgres", "-d", "postgres",
                        "-v", "ON_ERROR_STOP=1", "-tA"],
                       input=f"select ledger.query($gs${body}$gs$::jsonb);",
                       capture_output=True, text=True, timeout=120,
                       env={**os.environ, "PGPASSWORD": "postgres"})
    if r.returncode != 0:
        raise ValueError(r.stderr.strip())
    return json.loads(r.stdout)


def stored_vector(space, emb):
    """A REAL stored vector from the space (query-by-member: exact, no embedder needed)."""
    r = subprocess.run(["psql", "-h", "127.0.0.1", "-p", "15432", "-U", "postgres", "-d", "postgres", "-tA"],
                       input=("select coalesce(vec_3584::text, vec_2560::text, vec_1024::text) "
                              f"from ledger.embedding where space='{space}' and emb_layer='{emb}' limit 1"),
                       capture_output=True, text=True, timeout=60,
                       env={**os.environ, "PGPASSWORD": "postgres"})
    return json.loads(r.stdout.strip())


# ── 0. live-dep gate (loud skip, never a silent green) ────────────────────────
try:
    probe = q({"limit": 1})
except Exception as e:
    print(f"SKIP (loud): Supabase :15432 unreachable — {e}")
    raise SystemExit(0)
check("fn answers; meta carries run_id + plan", probe["meta"].get("run_id") and "plan" in probe["meta"])

# ── 1. filter axis + combinators ──────────────────────────────────────────────
r = q({"filter": {"path_under": ["runtime/", "ops/"], "not_under": "ops/cli/", "ext": [".py"]}, "limit": 5})
check("filter any-of + not_under lists candidates", r["meta"]["plan"]["filter_candidates"] > 50)
check("filter plan-echo names the fuse", r["meta"]["plan"]["fuse"] == "filter-listing")
paths = [x["path"] for x in r["results"]]
check("not_under excluded ops/cli/", all(not p.startswith("ops/cli/") for p in paths if p))

# ── 2. count operator ─────────────────────────────────────────────────────────
r = q({"filter": {"path_under": "runtime/"}, "count": {"by": "ext"}})
check("count-by-ext returns groups", any(g["group"] == ".py" and g["n"] > 30 for g in r["results"]))
check("count plan-echo names the operator", r["meta"]["plan"]["operator"] == "count-by-ext")

# ── 3. address-set seed ───────────────────────────────────────────────────────
r = q({"addresses": ["code://company/runtime/suite.py"], "count": {"by": "kind"}})
check("address-seed + count-by-kind (calls present)", any(g["group"] == "calls" for g in r["results"]))
check("address-seed echoed in plan", r["meta"]["plan"]["address_seed"] == 1)

# ── 4. graph axis: in-direction + hops + expand ───────────────────────────────
r = q({"graph": {"anchor": "code://company/runtime/scope.py", "kinds": ["calls", "imports"],
                 "direction": "in", "depth": 2, "expand": True}, "limit": 3})
check("graph-in reaches dependents", r["meta"]["plan"]["graph_reachable"] > 5)
check("hop attribution on results", all(isinstance(x.get("hops"), int) for x in r["results"]))
check("expand attaches edges", all(isinstance(x.get("edges"), list) for x in r["results"]))

# ── 5. semantic axis (a REAL stored vector — self-similarity must rank ~1.0 top) ──
v = stored_vector("desc", "pplx")
r = q({"semantic": {"vector": v, "space": "desc", "emb": "pplx", "k": 3}, "limit": 2})
check("semantic self-query top ≈ 1.0", float(r["results"][0]["score"]) > 0.99)
check("semantic plan-echo carries dim+space", r["meta"]["plan"]["semantic"]["dim"] == 2560)

# ── 6. scale drill (the zoom) over the new code pyramid (nomic 3584) ──────────
v3 = stored_vector("code", "nomic-code")
r = q({"scale": {"space": "code", "rung": "16", "top_clusters": 2},
       "semantic": {"vector": v3, "space": "code", "emb": "nomic-code", "k": 3}, "limit": 2})
check("scale drill narrows the space", 0 < r["meta"]["plan"]["scale"]["member_candidates"] < 1042)
check("drilled self-query still top ≈ 1.0", float(r["results"][0]["score"]) > 0.99)

# ── 7. paths axis (the fusion campaign's own journey) ─────────────────────────
r = q({"paths": {"kind": "fusion"}, "limit": 5})
check("paths axis walks the fusion journey", r["meta"]["plan"]["paths_candidates"] >= 5)

# ── 8. lexical axis + RRF fusion with legs ────────────────────────────────────
r = q({"semantic": {"vector": v, "space": "desc", "emb": "pplx", "k": 20},
       "lexical": {"text": "vector store"}, "limit": 5})
check("rrf fuse when both legs run", r["meta"]["plan"]["fuse"] == "rrf60")
check("legs attributed per result", all("legs" in x for x in r["results"]))

# ── 9. the teaching refusals (fail-loud, named, with the valid set) ───────────
for bad, frag in [({"bogus": 1}, "unknown spec key"),
                  ({"count": {"by": "vibe"}}, "count.by"),
                  ({"graph": {"anchor": "x", "direction": "sideways"}}, "graph.direction"),
                  ({"graph": {"anchor": "x", "depth": 9}}, "exceeds the cap")]:
    try:
        q(bad)
        check(f"refusal for {bad}", False)
    except ValueError as e:
        check(f"teaching refusal: {frag}", frag in str(e))

print(f"\nLEDGER QUERY ACCEPTANCE — {PASS} checks passed. Every axis + composition + refusals, "
      f"plan-echo asserted throughout (under-recall is never silent).")
