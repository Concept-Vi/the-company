"""tests/graph_path_acceptance.py — ④ THE CONTAINER · L4 GRAPH+PATH (C4.1–C4.7), verified BY USE.

Real calls against the real ledger (127.0.0.1:15432) + a scratch DB for the migration idempotency check.
Never code-existence — every check exercises the built behaviour.

  C4.1  0018 applies idempotently TWICE on a scratch DB (identical schema); edge_kinds assembles; the
        validate seam FAILS LOUD on an unregistered kind; every live ledger.edge kind is registered;
        part-of was normalized to part_of (count-verified — 0 part-of rows remain).
  C4.2  reverses composed at read: compose_inverse('imported_by') returns the flipped 'imports' rows on a
        known pair; NO imported_by rows are stored.
  C4.3  the landing reconciles with denominators (graph_edges 54 = 43 landed + 11 excluded; tie 606 = 282
        + 324); exclusions-with-reason exist; cvi_mine is immutable.
  C4.4  a cascade envelope auto-derives a path (steps=legs, payloads=run:// addrs); path://<id>/<ordinal>
        resolves through the ONE resolver; step 0 via_kind is NULL; path_replay materializes the walk.
  C4.5  the fusion campaign is a path:// record (kind=fusion) with the build's steps as ordinals.
  C4.6  paths embed under space='paths'; a similarity query returns sane ordering (self first). Skipped
        with a loud note only if the embedder endpoint is down (degrade-with-warning, never a false fail).
  C4.7  the projection emits paths[] alongside clusters/edges/spine/ghosts; counts-including-zero.

Prereqs (the live slice landed):
  psql -f build-prep/claude-design/supabase/supabase/migrations/0018_graph_path.sql
  python ops/seed_edge_kinds.py && python -m runtime.edge_kinds assemble
  python ops/migrate_edges_from_cvi.py && python ops/backwrite_fusion_path.py
"""
import importlib.util
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
MIGRATIONS = os.path.join(ROOT, "build-prep", "claude-design", "supabase", "supabase", "migrations")
PG = {"host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
      "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
      "user": os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"),
      "db": os.environ.get("COMPANY_LEDGER_PGDB", "postgres"),
      "pw": os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres")}
SCRATCH = "graph_path_acceptance_scratch"
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def psql(db, sql, script=False):
    env = {**os.environ, "PGPASSWORD": PG["pw"]}
    cmd = ["psql", "-h", PG["host"], "-p", PG["port"], "-U", PG["user"], "-d", db, "-v", "ON_ERROR_STOP=1"]
    if script:
        r = subprocess.run(cmd + ["-f", sql], capture_output=True, text=True, env=env)
        return r.returncode == 0, (r.stderr or "").strip()
    r = subprocess.run(cmd + ["-tA", "-c", sql], capture_output=True, text=True, env=env)
    return r.returncode == 0, (r.stdout if r.returncode == 0 else r.stderr.strip())


def _schema_fingerprint(db):
    ok, out = psql(db, "select string_agg(table_name||':'||column_name||':'||data_type, ',' order by "
                       "table_name, ordinal_position) from information_schema.columns where table_schema='ledger' "
                       "and table_name in ('edge_kind','path','path_step')")
    return out.strip() if ok else None


# ══ C4.1 — migration idempotent on scratch + registry live + validate seam + normalization ══════════════
print("[C4.1] edge_kinds registry + fail-loud validation + spelling normalization")
psql("postgres", f'drop database if exists "{SCRATCH}"')
ok, _ = psql("postgres", f'create database "{SCRATCH}"')
check("scratch DB created", ok)
ok, err = psql(SCRATCH, os.path.join(MIGRATIONS, "0011_ledger.sql"), script=True)
check(f"0011_ledger applies on scratch ({err[:50] if not ok else 'clean'})", ok)
ok, err = psql(SCRATCH, os.path.join(MIGRATIONS, "0018_graph_path.sql"), script=True)
check(f"0018_graph_path applies (1st) ({err[:60] if not ok else 'clean'})", ok)
fp1 = _schema_fingerprint(SCRATCH)
ok, err = psql(SCRATCH, os.path.join(MIGRATIONS, "0018_graph_path.sql"), script=True)
check(f"0018_graph_path applies AGAIN idempotently ({err[:60] if not ok else 'clean'})", ok)
fp2 = _schema_fingerprint(SCRATCH)
check("schema identical across double-apply (idempotent)", fp1 and fp1 == fp2)
psql("postgres", f'drop database if exists "{SCRATCH}"')

# live registry
ek = importlib.util.spec_from_file_location("edge_kinds_mod", os.path.join(ROOT, "runtime", "edge_kinds.py"))
edge_kinds = importlib.util.module_from_spec(ek); ek.loader.exec_module(edge_kinds)
ids = edge_kinds.all_ids()
check(f"edge_kind registry assembled ({len(ids)} kinds)", len(ids) >= 44)
ok, out = psql(PG["db"], "select kind from (select distinct kind from ledger.edge) e where not ledger.edge_kind_exists(kind)")
check("every live ledger.edge kind is registered (0 unregistered)", ok and not out.strip())
ok, out = psql(PG["db"], "select ledger.edge_kind_exists('imports')")
check("edge_kind_exists('imports') true (non-blocking seam)", ok and out.strip() == "t")
ok, out = psql(PG["db"], "select ledger.validate_edge_kind('__bogus_kind__')")
check("validate_edge_kind fails loud on an unregistered kind", (not ok) and "unregistered edge kind" in out)
try:
    edge_kinds.validate_kinds(["__bogus_kind__"]); raise AssertionError("no raise")
except ValueError as e:
    check("runtime.validate_kinds names edge_kinds/ + absorb path", "edge_kinds/" in str(e) and "ABSORB" in str(e))
ok, out = psql(PG["db"], "select count(*) from ledger.edge where kind='part-of'")
check("part-of normalized to part_of (0 part-of rows remain)", ok and out.strip() == "0")

# ══ C4.2 — reverses composed at read, never stored ══════════════════════════════════════════════════
print("[C4.2] reverses composed at read (law 4)")
from runtime.scope import _q
ok, out = psql(PG["db"], "select count(*) from ledger.edge where kind='imported_by'")
check("NO imported_by rows stored", ok and out.strip() == "0")
check("registry: imported_by is the declared inverse of imports", edge_kinds.forward_of("imported_by") == "imports")
ok, tgt = psql(PG["db"], "select to_resolved from ledger.edge where kind='imports' and to_resolved is not null and to_resolved<>'' limit 1")
tgt = tgt.strip().splitlines()[0]
composed = edge_kinds.compose_inverse(_q, tgt, "imported_by")
check(f"compose_inverse('imported_by') composes {len(composed)} edges off stored imports", len(composed) > 0)
check("composed edge is the flipped inverse (from==target, kind==imported_by)",
      composed[0]["from"] == tgt and composed[0]["kind"] == "imported_by")

# ══ C4.3 — landing reconciles with denominators; cvi immutable ══════════════════════════════════════
print("[C4.3] landing reconciliation + excluded-with-reason + cvi immutable")
land = subprocess.run([sys.executable, os.path.join(ROOT, "ops", "migrate_edges_from_cvi.py"), "--dry"],
                      capture_output=True, text=True, cwd=ROOT)
lo = land.stdout
check("graph_edges denominators balance (54)", "= 54 / 54" in lo)
check("type_instance_edges denominators balance (606)", "= 606 / 606" in lo)
check("cvi_mine immutable (fingerprint unchanged)", "immutable — never mutated" in lo)
check("belongs_to dropped as containment (derived not stored)", "containment face" in lo)
check("stored reverses excluded (composed at read)", "stored reverse" in lo and "composed at read" in lo)
ok, out = psql(PG["db"], "select count(*) from container.exclusions where source_system='cvi_mine' and reason like '%composed at read%'")
check("exclusion-with-reason rows persisted", ok and int(out.strip() or 0) > 0)
ok, out = psql(PG["db"], "select count(*) from ledger.edge where produced_by_session='L4-GRAPH-PATH'")
check(f"cloud edges landed into ledger.edge ({out.strip()})", ok and int(out.strip() or 0) >= 300)

# ══ C4.4 — a cascade envelope auto-derives a path; steps resolve; replay ═══════════════════════════════
print("[C4.4] path derivation from a run envelope + step resolution + replay")
from runtime import paths as P
from runtime.cognition import resolve_address
from runtime.bridge import SUITE as _S
envelope = {"action": "acceptance-probe", "turn_id": "accept-" + str(os.getpid()),
            "steps": [{"step": 0, "role": "focus", "kind": "role", "address": "run://accept/0-focus", "op": "run"},
                      {"step": 1, "role": "tally", "kind": "reduce", "address": "run://accept/1-tally", "op": "run"}],
            "final_address": "run://accept/1-tally"}
derived = P.derive_path_from_cascade(envelope, project="company")
check("derive_path_from_cascade returns a path address", derived["address"].startswith("path://company/accept-"))
r = resolve_address(_S.store, derived["address"])
check("path resolves through the ONE resolver (2 steps)", r["kind"] == "path" and len(r["steps"]) == 2)
st = resolve_address(_S.store, derived["address"] + "/1")
check("path://<id>/1 resolves the step (payload = run:// addr)", st["kind"] == "path_step" and st["step"]["payload_addr"] == "run://accept/1-tally")
st0 = resolve_address(_S.store, derived["address"] + "/0")
check("step 0 via_kind is NULL (start node)", st0["step"]["via_kind"] is None)
check("step 1 via_kind='follows' (registered edge kind)", st["step"]["via_kind"] == "follows")
rp = P.path_replay(derived["address"], "materialize")
check("path_replay materializes the walk", rp["n_steps"] == 2 and rp["walk"][1]["via"] == "follows")
try:
    resolve_address(_S.store, derived["address"] + "/99"); raise AssertionError("no raise")
except ValueError:
    check("out-of-range ordinal fails loud", True)

# ══ C4.5 — the fusion campaign as a path:// record ═══════════════════════════════════════════════════
print("[C4.5] the fusion campaign path (kind=fusion)")
fr = resolve_address(_S.store, "path://the-fusion/campaign")
check("fusion path exists (kind=fusion)", fr["record"]["kind"] == "fusion")
check("fusion path carries the build's steps as ordinals", len(fr["steps"]) >= 8)
check("ordinal 0 is the start (via_kind NULL)", fr["steps"][0]["via_kind"] is None)

# ══ C4.6 — path embedding + similarity ═══════════════════════════════════════════════════════════════
print("[C4.6] path embedding under space='paths' + similarity")
emb = P.embed_paths(_S.store)
if emb.get("degraded"):
    print("  ..  embedder endpoint DOWN — embedding degraded-with-warning (NOT a fail); similarity skipped")
else:
    check(f"paths embedded under space='paths' ({emb.get('embedded',0)+emb.get('skipped',0)} paths)",
          (emb.get("embedded", 0) + emb.get("skipped", 0)) >= 1)
    hits = P.path_similarity(_S.store, "path://the-fusion/campaign", k=5)
    check("similarity query returns hits", len(hits) >= 1)
    check("self-similarity ranks first (sane ordering)", hits[0].get("id") == "path://the-fusion/campaign")

# ══ C4.7 — the projection contract emits paths[] alongside the rest, counts-including-zero ═════════════
print("[C4.7] projection contract: paths[] alongside clusters/edges/spine/ghosts")
gp = importlib.util.spec_from_file_location("graph_projection", os.path.join(ROOT, "ops", "graph_projection.py"))
graph_projection = importlib.util.module_from_spec(gp); gp.loader.exec_module(graph_projection)
proj = graph_projection.build_projection()
for key in ("meta", "types", "clusters", "edges", "spine", "ghosts", "paths"):
    check(f"projection has '{key}'", key in proj)
m = proj["meta"]
for mk in ("edges_total", "edges_resolved", "ghosts", "kinds_seen", "kinds_registered", "paths", "clusters", "spine_count", "by_face", "by_provenance"):
    check(f"meta has count '{mk}' (counts-including-zero)", mk in m)
check("paths[] carries at least the fusion campaign", any(p["id"] == "path://the-fusion/campaign" for p in proj["paths"]))
check("paths[] step shape is {at, via, ordinal}", all(set(s) >= {"at", "via", "ordinal"} for p in proj["paths"] for s in p["steps"]))
check("edges[] sourced from edge_unified include authored provenance", "authored" in m["by_provenance"])

print(f"\n✅ graph_path_acceptance — {PASS} checks passed (C4.1–C4.7)")
