"""tests/container_acceptance.py — ④ THE CONTAINER, L1-SPINE (C1.1–C1.7): the rebuilt spine, verified BY USE.

Covers, with real calls against real databases (never code-existence):
  C1.1  0013_container.sql applies idempotently TWICE on a SCRATCH DB with an identical resulting schema.
  C1.2  resolve_address("project://the-fusion") returns record + containment edges through the ONE
        resolver, LIVE; unknown project / malformed address FAIL LOUD with the decided breadcrumb.
  C1.3  territory_for("project://the-fusion") composes the project leg; absent legs noted-absent;
        territory_prose renders WITHOUT raw addresses.
  C1.4  all 4 ledger labels have container.projects rows; ledger.entry.project_id backfill = 100%
        (161,835 + 1,743 + 1,028 + 331 — denominators printed).
  C1.5  PROJECT_ROOTS is read from container.projects.root_path (the `platforms` defect closed); the
        old dict is commented out with the breadcrumb, not deleted.
  C1.6  the back-write record resolves through project://the-fusion/{decisions,ore,concepts}/…,
        provenance-stamped to its source docs.
  C1.7  create_project is ONE atomic circuit on a scratch DB; a failed step rolls the WHOLE circuit back.
  +     cvi_mine is never mutated (row-count fingerprint identical across a full migration re-run —
        the re-run also proves the migration idempotent: container counts unchanged).

Needs the local Postgres (127.0.0.1:15432) with the spine slice landed:
  psql -f build-prep/claude-design/supabase/supabase/migrations/0013_container.sql
  .venv/bin/python ops/migrate_container_from_cvi.py --slice spine
  .venv/bin/python ops/backwrite_fusion_record.py
"""
import importlib.util, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


PG = {"host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
      "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
      "user": os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"),
      "db": os.environ.get("COMPANY_LEDGER_PGDB", "postgres"),
      "pw": os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres")}
MIGRATIONS = os.path.join(ROOT, "build-prep", "claude-design", "supabase", "supabase", "migrations")
SCRATCH = "container_acceptance_scratch"


def psql(db, sql, *, script=False):
    env = {**os.environ, "PGPASSWORD": PG["pw"]}
    cmd = ["psql", "-h", PG["host"], "-p", PG["port"], "-U", PG["user"], "-d", db, "-v", "ON_ERROR_STOP=1"]
    if script:
        r = subprocess.run(cmd, input=sql, capture_output=True, text=True, env=env)
    else:
        r = subprocess.run(cmd + ["-tA", "-c", sql], capture_output=True, text=True, env=env)
    return r.returncode == 0, (r.stdout if r.returncode == 0 else r.stderr.strip())


def psql_file(db, path):
    env = {**os.environ, "PGPASSWORD": PG["pw"]}
    r = subprocess.run(["psql", "-h", PG["host"], "-p", PG["port"], "-U", PG["user"], "-d", db,
                        "-v", "ON_ERROR_STOP=1", "-f", path], capture_output=True, text=True, env=env)
    return r.returncode == 0, (r.stderr or "").strip()


def _load(relpath, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, relpath))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ══ C1.1 — the migration applies idempotently TWICE on a SCRATCH DB, identical schema ═══════════════════
print("[C1.1] 0013_container.sql — idempotent double-apply on a scratch DB")
psql("postgres", f'drop database if exists "{SCRATCH}"')
ok, err = psql("postgres", f'create database "{SCRATCH}"')
check("scratch DB created", ok)
ok, err = psql_file(SCRATCH, os.path.join(MIGRATIONS, "0011_ledger.sql"))
check(f"0011_ledger.sql applies on scratch ({err[:60] if not ok else 'clean'})", ok)


def schema_signature():
    ok, out = psql(SCRATCH,
                   "select table_name||'|'||column_name||'|'||data_type||'|'||coalesce(is_nullable,'') "
                   "from information_schema.columns where table_schema='container' "
                   "order by table_name, column_name")
    assert ok, out
    return out


ok1, e1 = psql_file(SCRATCH, os.path.join(MIGRATIONS, "0013_container.sql"))
check(f"first apply clean ({e1[:80] if not ok1 else 'ok'})", ok1)
sig1 = schema_signature()
ok2, e2 = psql_file(SCRATCH, os.path.join(MIGRATIONS, "0013_container.sql"))
check(f"second apply clean — idempotent ({e2[:80] if not ok2 else 'ok'})", ok2)
sig2 = schema_signature()
check("schema signature IDENTICAL across the two applies", sig1 == sig2 and len(sig1.splitlines()) > 40)
check("all 6 container tables exist (spaces/projects/scopes/resources/members/exclusions)",
      all(t in sig1 for t in ("spaces|", "projects|", "scopes|", "resources|", "members|", "exclusions|")))
ok, out = psql(SCRATCH, "select column_name from information_schema.columns "
                        "where table_schema='ledger' and table_name='entry' and column_name='project_id'")
check("ledger.entry gained the ADDITIVE nullable project_id (schema-additive; label column untouched)",
      ok and "project_id" in out)

# ══ C1.7 — create_project: ONE ATOMIC CIRCUIT (on the scratch DB; a failed step rolls ALL back) ═════════
print("[C1.7] create_project — the atomic circuit")
mig = _load("ops/migrate_container_from_cvi.py", "mig_for_test")
live_db = mig.PGCONF["db"]
mig.PGCONF["db"] = SCRATCH                    # the circuit runs against the scratch container schema
try:
    row = mig.create_project("accept-test-proj", project_type="meta", description="acceptance circuit probe",
                             root_path="/tmp", keeper_role=None)
    check("circuit mints the project row (provenance-stamped)", row["project_key"] == "accept-test-proj")
    check("the address is DB-DERIVED (generated column — derive-never-place)",
          row["address"] == "project://accept-test-proj")
    ok, out = psql(SCRATCH, "select count(*) from container.members m join container.projects p "
                            "using(project_id) where p.project_key='accept-test-proj'")
    check("the minimal identity seed landed (operator://tim + agent://vi member rows)",
          ok and out.strip() == "2")
    ok, out = psql(SCRATCH, "select count(*) from container.spaces where space_key='tim'")
    check("space-if-needed created the one Space", ok and out.strip() == "1")
    # duplicate mint REFUSED (a circuit, not an upsert)
    try:
        mig.create_project("accept-test-proj")
        check("duplicate create_project refused", False)
    except ValueError as e:
        check("duplicate create_project refused fail-loud (never overwrites)", "already exists" in str(e))
    # a FAILED STEP rolls the WHOLE circuit back: poison the project INSERT (bad uuid cast at step 2);
    # steps that ran before it must not survive.
    ok, out = psql(SCRATCH, "select count(*) from container.members")
    before_members = out.strip()
    try:
        mig.create_project("accept-rollback-proj", source_uuid="NOT-A-UUID")
        check("poisoned circuit raised", False)
    except Exception:
        check("poisoned circuit raised (fail loud)", True)
    ok, out = psql(SCRATCH, "select count(*) from container.projects where project_key='accept-rollback-proj'")
    check("failed step rolled the WHOLE circuit back — no project row", ok and out.strip() == "0")
    ok, out = psql(SCRATCH, "select count(*) from container.members")
    check("…and no member rows leaked from the poisoned circuit", ok and out.strip() == before_members)
finally:
    mig.PGCONF["db"] = live_db
psql("postgres", f'drop database if exists "{SCRATCH}"')

# ══ C1.2 — the ONE resolver serves project:// LIVE (record + containment edges; fail-loud unknown) ══════
print("[C1.2] resolve_address(project://…) — both claimants served, live")
from runtime.cognition import resolve_address

r = resolve_address(None, "project://the-fusion")
check("project://the-fusion resolves through the ONE resolver", r.get("kind") == "project")
check("…returns the container RECORD", r["record"]["project_key"] == "the-fusion"
      and r["record"]["address"] == "project://the-fusion")
check("…returns the CONTAINMENT EDGES (authored contains: the shelves)",
      {"project://the-fusion/decisions", "project://the-fusion/ore", "project://the-fusion/concepts"}
      <= {c["address"] for c in r.get("contains", [])})
check("…returns members (the identity seed)",
      {m["principal"] for m in r.get("members", [])} >= {"operator://tim", "agent://vi"})
check("…returns the ledger label join (the derived IS-layer counts)",
      isinstance(r.get("ledger", {}).get("entries"), int))
r2 = resolve_address(None, "project://counterpart-design")
check("a ledger-label project resolves with its 1,743 entries joined",
      r2["ledger"]["entries"] == 1743 and r2["record"]["root_path"] == "/home/tim/repos/counterpart/design")
try:
    resolve_address(None, "project://no-such-project-xyz")
    check("unknown project fails loud", False)
except ValueError as e:
    msg = str(e)
    check("unknown project fails loud with the decided breadcrumb (expected/previously/fix)",
          "expected" in msg and "previously" in msg and "fix:" in msg and "never fabricate" in msg)
try:
    resolve_address(None, "project://the-fusion/decisions/")
    check("malformed (trailing slash) fails loud", False)
except ValueError:
    check("malformed project address fails loud (grammar gate)", True)
try:
    resolve_address(None, "project://the-fusion/no-such-shelf/nothing")
    check("unknown in-project path fails loud", False)
except ValueError as e:
    check("unknown in-project path fails loud, names the project as existing", "exists" in str(e))

# grammar declared once — contracts.address.parse_project_address
from contracts.address import parse_project_address
p = parse_project_address("project://the-fusion/decisions/4-the-container")
check("parse_project_address: canonical 3-level parse",
      p["project_key"] == "the-fusion" and p["path"] == "decisions/4-the-container")
check("parse_project_address: bare project node",
      parse_project_address("project://x")["path"] is None)
for bad in ("project://", "project://a//b", "session://x"):
    try:
        parse_project_address(bad)
        check(f"parse rejects {bad!r}", False)
    except ValueError:
        check(f"parse rejects {bad!r} fail-loud", True)

# ══ C1.3 — territory_for's project leg ══════════════════════════════════════════════════════════════════
print("[C1.3] territory_for(project://the-fusion) — the project leg composes")
from runtime.territory import territory_for, territory_prose, territory_label

t = territory_for("project://the-fusion")
check("identity leg present (the container record)", t["legs_present"]["identity"])
check("project leg present (status + scopes + members + ledger)", t["legs_present"]["project"]
      and t["project"]["status"] == "active" and "decisions" in t["project"]["scopes"]
      and len(t["project"]["members"]) >= 2)
prose = territory_prose(t)
check("prose renders WITHOUT raw addresses (operator-law)", prose and "://" not in prose)
check("prose carries the project's standing + holdings",
      "Standing:" in prose and "This project holds:" in prose)
check("territory_label is human (never the raw address)",
      "://" not in territory_label(t) and territory_label(t) != "this")
t_bad = territory_for("project://not-a-real-project-zzz")
check("unknown project degrades to noted-absent (never a crash)",
      t_bad["identity"] is None and any("identity leg unresolved" in n for n in t_bad["notes"]))
check("…and prose still renders (never raises)", isinstance(territory_prose(t_bad), str))

# ══ C1.4 — the 4-label backfill = 100%, denominators printed ═══════════════════════════════════════════
print("[C1.4] the ledger backfill — 100% with denominators")
DENOMS = {"company": 161835, "counterpart-design": 1743, "platforms": 1028, "claude-ds": 331}
ok, out = psql(PG["db"], "select project, count(*), count(project_id) from ledger.entry group by project order by project")
check("backfill query runs", ok)
rows = {l.split("|")[0]: (int(l.split("|")[1]), int(l.split("|")[2])) for l in out.splitlines() if l}
for label, want in sorted(DENOMS.items()):
    total, filled = rows.get(label, (0, 0))
    print(f"        {label}: {filled}/{total} (expected denominator {want})")
    check(f"{label}: total matches the stated denominator ({want})", total == want)
    check(f"{label}: backfill = 100% ({filled}/{total})", filled == total)
ok, out = psql(PG["db"], "select count(*) from container.projects where project_key in "
                         "('company','counterpart-design','platforms','claude-ds')")
check("all 4 ledger labels have container.projects rows", ok and out.strip() == "4")
ok, out = psql(PG["db"], "select count(*) from ledger.run where project_id is null")
check("ledger.run backfill total (0 nulls)", ok and out.strip() == "0")

# ══ C1.5 — PROJECT_ROOTS reads the registry; the dict is commented out with the breadcrumb ══════════════
print("[C1.5] PROJECT_ROOTS — dies as code, lives as data")
li = _load("ops/ledger_interpret.py", "li_for_test")
roots = li.project_roots()
check("project_roots() reads container.projects.root_path (all 4 labels + the-fusion)",
      set(roots) >= {"company", "counterpart-design", "platforms", "claude-ds", "the-fusion"})
check("`platforms` (the live defect) now has a real root on disk",
      os.path.isdir(roots["platforms"]) and roots["platforms"].endswith("/platforms"))
src = open(os.path.join(ROOT, "ops", "ledger_interpret.py"), encoding="utf-8").read()
check("the old dict is COMMENTED OUT, not deleted",
      '# -- PROJECT_ROOTS = {"company": REPO,' in src)
check("…with the breadcrumb (expected/previously/fix)",
      "expected container.projects.root_path" in src and "previously this" in src and "fix" in src)
check("no live assignment to the old dict remains", "\nPROJECT_ROOTS = {" not in src)

# ══ C1.6 — the back-write moment: the decided record queryable via the resolver ═════════════════════════
print("[C1.6] the back-write — the campaign's decided record, addressed + provenance-stamped")
for addr, needle in (("project://the-fusion/decisions/4-the-container", "Tim, decided"),
                     ("project://the-fusion/decisions/1-vector-cutover", "COMMENT IT OUT"),
                     ("project://the-fusion/ore/study-spine", "THE SPINE"),
                     ("project://the-fusion/concepts/law-01", "identity")):
    rec = resolve_address(None, addr)
    body = json.dumps(rec["record"]["content"])
    check(f"{addr.split('/', 3)[-1]} resolves with its real text", rec["kind"] == "resource" and needle in body)
    prov = rec["record"].get("provenance") or {}
    check("…provenance-stamped (source_doc + commit_sha)",
          prov.get("source_doc", "").startswith("build-prep/") and len(prov.get("commit_sha", "")) >= 7)
ok, out = psql(PG["db"], "select count(*) from container.resources r join container.scopes s using(scope_id) "
                         "where s.address='project://the-fusion/concepts'")
check("the 11 laws + 2 methodologies land under concepts/ (13 rows)", ok and out.strip() == "13")

# ══ the standing laws — reconciliation + cvi_mine immutability (a full idempotent re-run) ═══════════════
print("[LAW] reconciliation sums + cvi_mine never mutated + migration idempotent (full re-run)")


def cvi_fingerprint():
    ok, out = psql("cvi_mine", "select (select count(*) from spaces)||'|'||(select count(*) from projects)"
                               "||'|'||(select count(*) from project_scopes)||'|'||(select count(*) from project_resources)"
                               "||'|'||(select count(*) from project_content)||'|'||(select count(*) from project_members)")
    assert ok, out
    return out.strip()


def container_fingerprint():
    ok, out = psql(PG["db"], "select (select count(*) from container.spaces)||'|'||(select count(*) from container.projects)"
                             "||'|'||(select count(*) from container.scopes)||'|'||(select count(*) from container.resources)"
                             "||'|'||(select count(*) from container.members)||'|'||(select count(*) from container.exclusions)")
    assert ok, out
    return out.strip()


cvi_before, cont_before = cvi_fingerprint(), container_fingerprint()
rep = mig.migrate_spine()                      # the FULL slice, re-run
check("re-run: cvi_mine row counts IDENTICAL (the source-of-record was never mutated)",
      cvi_fingerprint() == cvi_before)
check("re-run: container row counts IDENTICAL (run twice = same result)",
      container_fingerprint() == cont_before)
for name, sec in rep["sections"].items():
    if isinstance(sec, dict) and "sums_match" in sec:
        absorbed_n = sec.get("absorbed", 0)   # a source row dropped by conflict is absorbed-with-reason
        math = f"{sec['source']} = {sec['landed']} + {sec['excluded']}" + (f" + {absorbed_n}" if absorbed_n else "")
        check(f"reconciliation sums match for {name} ({math})", sec["sums_match"]
              and sec["source"] == sec["landed"] + sec["excluded"] + absorbed_n)
ok, out = psql(PG["db"], "select count(*) from container.exclusions where reason is null or reason=''")
check("every exclusion carries a REASON (excluded-with-reason, no blanks)", ok and out.strip() == "0")
check("the reconciliation report is ARCHIVED at project://the-fusion/ore/reconciliation-spine (CA.1)",
      resolve_address(None, "project://the-fusion/ore/reconciliation-spine")["record"]["content"]
      ["sections"]["ledger_backfill"]["entry"])

print(f"\nALL {PASS} CHECKS PASSED — L1-SPINE C1.1–C1.7 verified by use.")
