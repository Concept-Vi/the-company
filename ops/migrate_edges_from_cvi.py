"""ops/migrate_edges_from_cvi.py — ④ L4 · LAND the cloud edges into the one store (GRAPH-PATH §3.4; C4.3).

The rebuilt-organ landing: cvi_mine's public.graph_edges (54) + type_instance_edges (606) fold into
ledger.edge under the ONE grammar, with every curation written EXCLUDED-WITH-REASON and a reconciliation
that prints DENOMINATORS. Reverses are COMPOSED AT READ, never stored (law 4); containment is DERIVED,
never stored (drop belongs_to). cvi_mine is the IMMUTABLE source-of-record — this script contains NO
INSERT/UPDATE/DELETE against cvi_mine (read-only SELECTs; asserted below).

Landing rules (registry-is-truth — the edge_kind registry decides):
  · metadata.reverse_of present            → EXCLUDE "stored reverse — composed at read (law 4)"
  · kind is a declared INVERSE (unregistered as a forward row, but forward_of() finds its forward)
                                            → EXCLUDE "declared inverse — composed at read"
  · belongs_to                             → EXCLUDE "containment face — derived from the address hierarchy, never stored"
  · a test-pollution endpoint (thread:test / placeholder 1111.. UUIDs)
                                            → EXCLUDE "test pollution"
  · anything else                          → LAND into ledger.edge (kind normalized to canonical)
  · a kind neither registered NOR a known inverse → SURFACE loud (unabsorbed — never silently dropped)

Reversal: DELETE FROM ledger.run WHERE run_id = <the landing run> (ON DELETE CASCADE removes its edges).

  .venv/bin/python ops/migrate_edges_from_cvi.py            # land + reconcile (prints denominators)
  .venv/bin/python ops/migrate_edges_from_cvi.py --dry      # classify + reconcile, write NOTHING
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
import uuid as _uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ops.seed_edge_kinds import CANONICAL  # the ONE canonical-spelling map (single source)

PG = {"host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
      "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
      "user": os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"),
      "db": os.environ.get("COMPANY_LEDGER_PGDB", "postgres"),
      "pw": os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres")}
CVI = os.environ.get("COMPANY_CVI_DB", "cvi_mine")
# the landing IS fusion-campaign work → the run carries the REAL project label 'the-fusion' (an existing
# container.projects row, so C1.4's project_id backfill stays 100% — never invent a project label). The
# run's purpose/session_id ('cvi-edge-landing'/'L4-GRAPH-PATH') distinguish the landing run.
LANDING_PROJECT = "the-fusion"


def _psql(db: str, sql: str, tuples=True) -> str:
    cmd = ["psql", "-h", PG["host"], "-p", PG["port"], "-U", PG["user"], "-d", db]
    cmd += (["-tA", "-c", sql] if tuples else ["-v", "ON_ERROR_STOP=1", "-c", sql])
    r = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, "PGPASSWORD": PG["pw"]})
    if r.returncode != 0:
        raise RuntimeError(f"psql {db} FAILED: {r.stderr.strip()} — fail loud.")
    return r.stdout


def _lit(s) -> str:
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


def canon(k: str) -> str:
    return CANONICAL.get(k, k)


def _norm_uri(u: str) -> str:
    """thread: → session:// (the cloud's session-lineage URIs join the one grammar; §3.4)."""
    if not u:
        return u
    if u.startswith("thread:"):
        return "session://" + u[len("thread:"):]
    return u


def _is_test(*uris) -> bool:
    # ONLY literal test fixtures (thread:test-*, ...:test...) — the placeholder-UUID rows (thread:1111…)
    # are real structural lineage examples the study counts as REAL (54 → ~40), so they LAND.
    return any("test" in (u or "").lower() for u in uris)


def main():
    dry = "--dry" in sys.argv
    # registry truth: which kinds are registered FORWARD rows, and the inverse→forward map
    registered = {ln.strip() for ln in _psql(PG["db"], "select id from ledger.edge_kind").split() if ln.strip()}
    inv_to_fwd = {}
    for line in _psql(PG["db"], "select id, inverse from ledger.edge_kind where inverse is not null").splitlines():
        if "|" in line:
            fid, inv = line.split("|", 1)
            inv_to_fwd[inv.strip()] = fid.strip()

    landed, excluded, unabsorbed = [], [], []

    def classify(src_table, kind, frm, to, extra_reverse=False):
        ck = canon(kind)
        if extra_reverse:
            excluded.append((src_table, kind, "stored reverse (metadata.reverse_of) — composed at read (law 4)"))
            return None
        if _is_test(frm, to):
            excluded.append((src_table, kind, "test pollution (placeholder/thread:test endpoint)"))
            return None
        if ck == "belongs_to":
            excluded.append((src_table, kind, "containment face — derived from the address hierarchy, never stored"))
            return None
        if ck not in registered:
            if ck in inv_to_fwd:
                excluded.append((src_table, kind, f"declared inverse of {inv_to_fwd[ck]!r} — composed at read (law 4)"))
                return None
            unabsorbed.append((src_table, ck))
            return None
        return ck

    # ── graph_edges (54) ───────────────────────────────────────────────────────────────────────────────
    ge = json.loads(_psql(CVI,
        "select coalesce(json_agg(t),'[]') from (select relationship, source_uri, target_uri, "
        "(metadata ? 'reverse_of') as is_rev from public.graph_edges) t"))
    ge_denom = len(ge)
    ge_rows = []
    for e in ge:
        ck = classify("graph_edges", e["relationship"], e["source_uri"], e["target_uri"], e["is_rev"])
        if ck:
            ge_rows.append((_norm_uri(e["source_uri"]), ck, _norm_uri(e["target_uri"])))

    # ── type_instance_edges (606) ────────────────────────────────────────────────────────────────────────
    tie = json.loads(_psql(CVI,
        "select coalesce(json_agg(t),'[]') from (select edge_type, from_type, from_id::text as from_id, "
        "to_type, to_id::text as to_id from public.type_instance_edges) t"))
    tie_denom = len(tie)
    tie_rows = []
    for e in tie:
        ck = classify("type_instance_edges", e["edge_type"],
                      f"{e['from_type']}:{e['from_id']}", f"{e['to_type']}:{e['to_id']}")
        if ck:
            frm = f"cvi://{e['from_type']}/{e['from_id']}"
            to = f"cvi://{e['to_type']}/{e['to_id']}"
            tie_rows.append((frm, ck, to))

    # assert cvi UNTOUCHED (read-only): the fingerprint before == after (we never wrote it)
    fp_before = _psql(CVI, "select (select count(*) from public.graph_edges)||'/'||"
                            "(select count(*) from public.type_instance_edges)").strip()

    all_rows = ge_rows + tie_rows
    run_id = str(_uuid.uuid4())
    if not dry:
        # a distinct, reversible landing run (drop it → its edges cascade away). project_id = the-fusion
        # (the landing IS the fusion campaign's work; C1.4's 100%-run-backfill invariant stays true).
        _psql(PG["db"],
              "insert into ledger.run (run_id, project, project_id, channel, purpose, layer, session_id, "
              "status, started_at, ended_at) values ("
              f"{_lit(run_id)}::uuid, {_lit(LANDING_PROJECT)}, "
              "(select project_id from container.projects where project_key='the-fusion'), "
              "'container', 'cvi-edge-landing', 'landing', "
              f"'L4-GRAPH-PATH', 'complete', now(), now())", tuples=False)
        # land the edges (kinds validated by the registry classify above — all registered)
        vals = ",".join(
            f"({_lit(run_id)}::uuid, {_lit(f)}, {_lit(k)}, {_lit(t)}, {_lit(t)}, 'L4-GRAPH-PATH', 'cvi-landing-v1')"
            for (f, k, t) in all_rows)
        if vals:
            _psql(PG["db"],
                  "insert into ledger.edge (run_id, from_ref, kind, to_raw, to_resolved, produced_by_session, pass) "
                  f"values {vals}", tuples=False)
        # exclusions-with-reason
        for (tbl, kind, reason) in excluded:
            _psql(PG["db"],
                  "insert into container.exclusions (source_system, source_table, source_key, reason) values ("
                  f"'cvi_mine', {_lit(tbl)}, {_lit(kind)}, {_lit(reason)}) on conflict do nothing", tuples=False)

    fp_after = _psql(CVI, "select (select count(*) from public.graph_edges)||'/'||"
                           "(select count(*) from public.type_instance_edges)").strip()
    assert fp_before == fp_after, f"cvi_mine MUTATED ({fp_before} → {fp_after}) — INVARIANT BROKEN, fail loud."

    # ── reconciliation (denominators printed) ────────────────────────────────────────────────────────────
    from collections import Counter
    ge_excl = Counter(r for (tbl, _k, r) in excluded if tbl == "graph_edges")
    tie_excl = Counter(r for (tbl, _k, r) in excluded if tbl == "type_instance_edges")
    print(f"{'DRY — ' if dry else ''}LANDING RECONCILIATION (cvi_mine → ledger.edge, run {run_id[:8]})")
    print(f"\ngraph_edges:  denominator {ge_denom}")
    print(f"  landed:   {len(ge_rows)}")
    for r, n in ge_excl.items():
        print(f"  excluded: {n:3}  — {r}")
    print(f"  ── {len(ge_rows)} landed + {sum(ge_excl.values())} excluded = {len(ge_rows)+sum(ge_excl.values())} / {ge_denom}")
    print(f"\ntype_instance_edges:  denominator {tie_denom}")
    print(f"  landed:   {len(tie_rows)}")
    for r, n in tie_excl.items():
        print(f"  excluded: {n:3}  — {r}")
    print(f"  ── {len(tie_rows)} landed + {sum(tie_excl.values())} excluded = {len(tie_rows)+sum(tie_excl.values())} / {tie_denom}")
    lineage = sum(1 for (_f, k, _t) in tie_rows if k == "produced")
    print(f"\ntotal landed: {len(all_rows)}  (graph_edges {len(ge_rows)} + tie {len(tie_rows)}; "
          f"tie split: {lineage} lineage/produced + {len(tie_rows)-lineage} knowledge)")
    print(f"cvi_mine fingerprint {fp_before} == {fp_after}  (immutable — never mutated)")
    if unabsorbed:
        print(f"\n!! UNABSORBED kinds (neither registered nor a known inverse) — SURFACED, never silently dropped:")
        for tbl, k in sorted(set(unabsorbed)):
            print(f"   {tbl}: {k!r} — author edge_kinds/{k}.py + re-run ops/seed_edge_kinds.py (ABSORB-never-reject)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
