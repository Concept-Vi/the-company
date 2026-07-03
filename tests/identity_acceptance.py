"""tests/identity_acceptance.py — ④ THE CONTAINER, L2-IDENTITY (C2.1–C2.5): the one principal model, verified BY USE.

Covers, with real calls against real databases (never code-existence):
  C2.1  0017_identity.sql applies idempotently TWICE on a SCRATCH DB with an identical resulting schema;
        the prereq guard FAILS LOUD without schema container; the seed mints exactly ONE operator (Tim,
        t.geldard@ primary), the vi AGENT principal (v.i@ + vi@system.local attached), and the standing
        acts-for delegation Tim→vi.
  C2.2  the OPERATOR_USER_ID shadow: the principal-table read runs BESIDE the env default; the live
        operator subject (ebe5f9c7) is IDENTICAL under the shadow (via the acts-for delegation); the
        t.geldard subject's divergence (live CLIENT, shadow OPERATOR — the flip's effect) is RECORDED
        loud; the env default is STILL the live authority (needs-tim: the flip).
  C2.3  the 15 cloud users land per the map (1 operator login + 2 vi-agent logins + 4 humans + 8
        archived-with-reason — the live count is 8, not the doc's 7; measured, reconciled honestly);
        the uuid rewrite map spot-verified on 10 rows against cvi_mine; sums close with denominators.
  C2.4  may(principal, verb, address)/access_of(address) is ONE function answering both faces — the
        Suite method and a REAL bridge HTTP read return the same answer for 5 principal×address pairs.
  C2.5  the 13 duplicate L3 delegations collapse to ONE confirmed grant with 13 evidence entries; the
        L5 grant lands with its window; the delegation ceiling BOUNDS A LIVE guard() call (a test
        principal denied above its ceiling).
  +     cvi_mine is never mutated (fingerprint identical across a full migration re-run — which also
        proves the migration idempotent).

Needs the local Postgres (127.0.0.1:15432) with 0013 + 0017 applied and both slices landed:
  psql -f build-prep/claude-design/supabase/supabase/migrations/0017_identity.sql
  .venv/bin/python ops/migrate_identity_from_cvi.py --slice identity
"""
import importlib.util, json, os, subprocess, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("COMPANY_TEST_RUN", "1")

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
SCRATCH = "identity_acceptance_scratch"


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


# ══ C2.1 — 0017 idempotent double-apply on a SCRATCH DB + the prereq guard + the seed ═══════════════════
print("[C2.1] 0017_identity.sql — prereq guard + idempotent double-apply + the operator seed")
psql("postgres", f'drop database if exists "{SCRATCH}"')
ok, err = psql("postgres", f'create database "{SCRATCH}"')
check("scratch DB created", ok)

# prereq guard: applying 0017 WITHOUT schema container must FAIL LOUD with the breadcrumb.
ok, err = psql_file(SCRATCH, os.path.join(MIGRATIONS, "0017_identity.sql"))
check("prereq guard: 0017 without container schema FAILS LOUD",
      not ok and "expected schema container" in err and "fix:" in err)

ok, err = psql_file(SCRATCH, os.path.join(MIGRATIONS, "0011_ledger.sql"))
check(f"0011_ledger.sql applies on scratch ({err[:60] if not ok else 'clean'})", ok)
ok, err = psql_file(SCRATCH, os.path.join(MIGRATIONS, "0013_container.sql"))
check(f"0013_container.sql applies on scratch ({err[:60] if not ok else 'clean'})", ok)


def schema_signature():
    ok, out = psql(SCRATCH,
                   "select table_name||'|'||column_name||'|'||data_type||'|'||coalesce(is_nullable,'') "
                   "from information_schema.columns where table_schema='container' "
                   "order by table_name, column_name")
    assert ok, out
    return out


ok1, e1 = psql_file(SCRATCH, os.path.join(MIGRATIONS, "0017_identity.sql"))
check(f"first apply clean ({e1[:80] if not ok1 else 'ok'})", ok1)
sig1 = schema_signature()
ok2, e2 = psql_file(SCRATCH, os.path.join(MIGRATIONS, "0017_identity.sql"))
check(f"second apply clean — idempotent ({e2[:80] if not ok2 else 'ok'})", ok2)
sig2 = schema_signature()
check("schema signature IDENTICAL across the two applies", sig1 == sig2)
check("the 5 identity tables exist (principal/principal_auth/delegation/delegation_evidence/uuid_rewrite_map)",
      all(t in sig1 for t in ("principal|", "principal_auth|", "delegation|", "delegation_evidence|",
                              "uuid_rewrite_map|")))
# seed shape ON THE SCRATCH (the migration alone mints it — registry-authored, never an env default)
ok, out = psql(SCRATCH, "select count(*) from container.principal where kind='operator' and status='active'")
check("exactly ONE active operator principal (Tim)", ok and out.strip() == "1")
ok, out = psql(SCRATCH, "select p.address||'|'||a.auth_user_id::text||'|'||a.is_primary "
                        "from container.principal_auth a join container.principal p using(principal_id) "
                        "order by a.auth_user_id")
check("t.geldard@ (554e223d) attached PRIMARY to operator://tim",
      ok and "operator://tim|554e223d-e431-41ce-8913-1a7d8d81d321|t" in out)
check("v.i@ (ebe5f9c7) attached to agent://vi (VI's OWN email — Tim's correction, NOT the operator)",
      "agent://vi|ebe5f9c7-4d66-4717-835f-afc96088facb|t" in out)
check("vi@system.local (…0001) attached to the SAME agent://vi (vi:global ≡ vi@system.local, one row)",
      "agent://vi|00000000-0000-0000-0000-000000000001|f" in out)
ok, out = psql(SCRATCH, "select od.address||'>'||gr.address||'|'||d.max_autonomy||'|'||d.kind "
                        "from container.delegation d "
                        "join container.principal od on od.principal_id=d.delegator "
                        "join container.principal gr on gr.principal_id=d.grantee")
check("the standing acts-for delegation Tim→vi seeded (L5, kind=acts_for)",
      ok and "operator://tim>agent://vi|L5|acts_for" in out)
ok, out = psql(SCRATCH, "select column_name from information_schema.columns where table_schema='container' "
                        "and table_name='members' and column_name in ('principal_id','scopes','revoked_at')")
check("container.members gained the ADDITIVE identity columns (L1 shape untouched)",
      ok and len(out.split()) == 3)
psql("postgres", f'drop database if exists "{SCRATCH}"')

# ══ C2.3 — the 15 cloud users per the map + the uuid rewrite spot-check + reconciliation ════════════════
print("[C2.3] the 15 cloud users — landed per the map, denominators printed")
mig = _load("ops/migrate_identity_from_cvi.py", "mig_identity_for_test")


def cvi_fingerprint():
    ok, out = psql("cvi_mine", "select (select count(*) from auth.users)||'|'||(select count(*) from delegations)"
                               "||'|'||(select count(*) from space_members)")
    assert ok, out
    return out.strip()


def identity_fingerprint():
    ok, out = psql(PG["db"], "select (select count(*) from container.principal)||'|'"
                             "||(select count(*) from container.principal_auth)||'|'"
                             "||(select count(*) from container.delegation)||'|'"
                             "||(select count(*) from container.delegation_evidence)||'|'"
                             "||(select count(*) from container.uuid_rewrite_map)")
    assert ok, out
    return out.strip()


cvi_before, ident_before = cvi_fingerprint(), identity_fingerprint()
rep = mig.migrate_identity()                    # a FULL re-run (idempotency + immutability in one move)
check("re-run: cvi_mine fingerprint IDENTICAL (the source-of-record was never mutated)",
      cvi_fingerprint() == cvi_before)
check("re-run: identity row counts IDENTICAL (run twice = same result)",
      identity_fingerprint() == ident_before)

u = rep["sections"]["users"]
print(f"        {rep['denominators']['users']}")
check("users reconciliation sums close (15 = 1 + 2 + 4 + 8)",
      u["sums_match"] and u["source"] == 15 and u["operator_login"] == 1
      and u["vi_agent_logins"] == 2 and u["humans_landed"] == 4 and u["archived"] == 8)
ok, out = psql(PG["db"], "select count(*) from container.principal where kind='human'")
check("4 human principals landed (grant + nick + phil + scott)", ok and out.strip() == "4")
# RETIRED 2026-07-03 (Tim: retire the @example.com family-test accounts). Reversible: the principal
# rows are PRESERVED with status='archived' + prev_status stamped; nick/phil/scott archived, grant stays active.
ok, out = psql(PG["db"], "select status, count(*) from container.principal where kind='human' group by status order by status")
check("the 3 @example.com family-test humans are RETIRED (1 active [grant] + 3 archived), reversibly",
      ok and out.strip().replace(" ", "") == "active|1\narchived|3")
ok, out = psql(PG["db"], "select count(*) from container.principal where kind='human' "
                         "and metadata->>'family_test'='true' and status='archived' and metadata->>'retired' is not null")
check("each retired family-test human carries its retire stamp (status=archived + retired date)", ok and out.strip() == "3")
ok, out = psql(PG["db"], "select count(*) from container.exclusions where source_table='auth.users' "
                         "and (reason is null or reason='')")
check("every archived user carries a REASON (excluded-with-reason, no blanks)", ok and out.strip() == "0")
ok, out = psql(PG["db"], "select count(*) from container.uuid_rewrite_map")
check("the uuid rewrite map covers ALL 15 cloud uuids", ok and out.strip() == "15")
spot = rep["sections"]["uuid_rewrite_spotcheck"]
check("uuid rewrite SPOT-VERIFIED on 10 sampled rows against cvi_mine (all verified)",
      spot["sampled"] == 10 and spot["all_verified"])
# the map's application is live: L1's members rows now resolve principal_id through the model.
ok, out = psql(PG["db"], "select count(*) filter (where principal_id is not null)||'/'||count(*) "
                         "from container.members")
check(f"container.members principal_id backfill = 100% ({out.strip() if ok else '?'})",
      ok and len(set(out.strip().split("/"))) == 1)

# ══ C2.5 — the delegation collapse + the L5 window + the ceiling bounding a LIVE guard() ════════════════
print("[C2.5] delegations — 13-duplicate collapse + L5 window + the ceiling enforced")
d = rep["sections"]["delegations"]
print(f"        {rep['denominators']['delegations']}")
check("delegations reconciliation sums close (14 = 13 + 1 + 0)",
      d["sums_match"] and d["source"] == 14 and d["l3_collapsed_to_evidence"] == 13 and d["l5_landed"] == 1)
ok, out = psql(PG["db"], "select count(*) from container.delegation_evidence de "
                         "join container.delegation dd using(delegation_id) where dd.confirmed and dd.kind='acts_for'")
check("ONE confirmed acts-for grant carries exactly 13 evidence entries", ok and out.strip() == "13")
ok, out = psql(PG["db"], "select count(distinct de.source_uuid) from container.delegation_evidence de "
                         "join container.delegation dd using(delegation_id) where dd.kind='acts_for'")
check("…each evidence entry preserves a DISTINCT source cvi delegation uuid", ok and out.strip() == "13")
ok, out = psql(PG["db"], "select d.max_autonomy||'|'||d.valid_from::text||'|'||coalesce(d.valid_to::text,'open') "
                         "from container.delegation d where d.kind='historical' and d.source_system='cvi_mine'")
check("the L5 grant landed with its WINDOW (valid_from carried; open-ended as in source)",
      ok and out.strip().startswith("L5|2025-12-22") and out.strip().endswith("|open"))
ok, out = psql(PG["db"], "select de.note from container.delegation_evidence de "
                         "join container.delegation dd using(delegation_id) where dd.kind='historical'")
check("the L5 source `constraints` jsonb is PRESERVED verbatim (dead-stuff-carries-intention)",
      ok and "can_deploy_to_langgraph" in out)

# the ceiling BOUNDS A LIVE guard() call: mint a test principal with an L1 ceiling, resolve it via
# may(), and prove guard() denies it above its ceiling — then clean up (test rows never persist).
from runtime import governance as gov
from runtime.access import may as _may

psql(PG["db"], """
begin;
insert into container.principal (kind, handle, display, status, source_system)
values ('agent', 'test-lowceil', 'acceptance low-ceiling agent', 'active', 'identity_acceptance')
on conflict (kind, handle) do nothing;
insert into container.delegation (delegator, grantee, container_address, scopes, max_autonomy, status, kind, source_system)
select o.principal_id, t.principal_id, null, array['read','write']::text[], 'L1', 'active', 'acts_for', 'identity_acceptance'
  from container.principal o, container.principal t
 where o.address='operator://tim' and t.address='agent://test-lowceil'
on conflict (delegator, grantee, coalesce(container_address,'')) do nothing;
commit;""", script=True)
try:
    dec = _may("agent://test-lowceil", "write", "project://the-fusion")
    check("may() resolves the test principal via its delegation, carrying ceiling=L1",
          dec["allow"] and dec["via"] == "delegation" and dec.get("ceiling") == "L1")
    ceiling = dec["ceiling"]
    try:
        gov.guard("code_build", lambda: "built", ceiling=ceiling)
        check("LIVE guard(): L1 principal DENIED code_build (above its ceiling)", False)
    except gov.GovernanceError as e:
        check("LIVE guard(): L1 principal DENIED code_build (above its ceiling), naming the breach",
              "ceiling is L1" in str(e) and "requires autonomy" in str(e))
    try:
        gov.guard("spend", lambda: "spent", ceiling=ceiling)   # SURFACE class, requires L3 > L1
        check("LIVE guard(): L1 ceiling bumps a SURFACE class to CONFIRM (denied unconfirmed)", False)
    except gov.GovernanceError:
        check("LIVE guard(): L1 ceiling bumps a SURFACE class to CONFIRM (denied unconfirmed)", True)
    check("…while an L5 ceiling (the vi acts-for) leaves an AUTO class free",
          gov.guard("run", lambda: "ran", ceiling="L5") == "ran")
    check("…and a ceilingless call is BYTE-IDENTICAL to before (additive law)",
          gov.guard("run", lambda: "ran") == "ran")
finally:
    psql(PG["db"], """
begin;
delete from container.delegation d using container.principal t
  where d.grantee=t.principal_id and t.address='agent://test-lowceil';
delete from container.principal where address='agent://test-lowceil';
commit;""", script=True)
ok, out = psql(PG["db"], "select count(*) from container.principal where address='agent://test-lowceil'")
check("test principal cleaned up (no acceptance debris)", ok and out.strip() == "0")

# ══ C2.4 — may()/access_of(): ONE function, BOTH faces agree on 5 pairs ═════════════════════════════════
print("[C2.4] may()/access_of() — the Suite method and a REAL bridge HTTP read agree (5 pairs)")
from runtime.suite import Suite
from runtime.registry import NodeRegistry
from store.fs_store import FsStore
import tempfile, shutil, threading

PAIRS = [
    ("operator://tim", "write", "project://the-fusion"),
    ("agent://vi", "create:intent", "project://the-fusion"),
    ("agent://vi", "write", "project://counterpart-design"),
    ("agent://ci-keeper-agent", "write", "project://the-fusion"),
    ("human://nick-godfrey", "read", "project://the-fusion"),
]
work = tempfile.mkdtemp(prefix="identity-acc-")
NODES = os.path.join(ROOT, "nodes")
_reg = NodeRegistry(); _reg.discover([NODES])
suite = Suite(FsStore(os.path.join(work, "store")), _reg, nodes_dir=NODES)
suite_answers = [suite.may(p, v, a) for (p, v, a) in PAIRS]
check("Suite.may answers all 5 pairs with fail-closed verdicts",
      [d["allow"] for d in suite_answers] == [True, True, True, False, False])

# the REAL bridge face: serve runtime/bridge.py's own handler on a private test port and curl it.
# (8770 may be owned by another lane's verifier — we bring up our OWN instance of the same code.)
TEST_PORT = 8793
env = {**os.environ, "COMPANY_TEST_RUN": "1"}
proc = subprocess.Popen([os.path.join(ROOT, ".venv", "bin", "python"), "runtime/bridge.py", str(TEST_PORT)],
                        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
try:
    deadline = time.time() + 60
    up = False
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{TEST_PORT}/api/now", timeout=2)
            up = True
            break
        except Exception:
            time.sleep(1.5)
    check(f"the bridge face serves on :{TEST_PORT} (real runtime/bridge.py process)", up)
    agree = True
    for (p, v, a), sd in zip(PAIRS, suite_answers):
        from urllib.parse import quote
        url = (f"http://127.0.0.1:{TEST_PORT}/api/may?principal={quote(p)}&verb={quote(v)}"
               f"&address={quote(a)}")
        bd = json.loads(urllib.request.urlopen(url, timeout=20).read())
        same = (bd["allow"] == sd["allow"] and bd["via"] == sd["via"]
                and bd.get("ceiling") == sd.get("ceiling"))
        print(f"        {p:26} {v:14} {a:30} suite={sd['allow']}/{sd['via']} bridge={bd['allow']}/{bd['via']} {'==' if same else '!='}")
        agree = agree and same
    check("BOTH faces return the SAME answer on all 5 pairs (one function — law 9)", agree)
    # access_of parity on the roster read
    from urllib.parse import quote
    ro_b = json.loads(urllib.request.urlopen(
        f"http://127.0.0.1:{TEST_PORT}/api/access-of?address={quote('project://the-fusion')}", timeout=20).read())
    ro_s = suite.access_of("project://the-fusion")
    check("access_of: the bridge roster == the Suite roster (same principals, same verbs)",
          ro_b["principals"] == ro_s["principals"])
    check("access_of shows the permission may() enforces (operator row carries all 5 verbs)",
          any(r["principal"] == "operator://tim" and set(r["may"]) >= {"read", "write", "execute", "admin", "approve"}
              for r in ro_s["principals"]))
finally:
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
    shutil.rmtree(work, ignore_errors=True)

# ══ C2.2 — the operator gate, FLIPPED (2026-07-03): the PRINCIPAL TABLE is the live authority ═══════════
print("[C2.2] the operator gate — principal-table authority (FLIPPED; env default retired inert)")
src = open(os.path.join(ROOT, "mcp_face", "remote.py"), encoding="utf-8").read()
check("the live decision is the principal-table read (`_operator_tier_via_principals(subject) is True`)",
      "if _operator_tier_via_principals(subject) is True:" in src)
check("the env-default read is NO LONGER the live authority (no UNCOMMENTED `if subject == "
      "OPERATOR_USER_ID:` decision — surviving mentions are revert-comments only)",
      not any(ln.strip().startswith("if subject == OPERATOR_USER_ID:") for ln in src.splitlines()))
check("the OPERATOR_USER_ID env default is retained inert + breadcrumbed for revert",
      "now inert for the gate" in src and "FLIPPED 2026-07-03" in src)
from mcp_face import remote as _remote
check("live: t.geldard@ (554e223d/operator) resolves OPERATOR through the principal table",
      _remote._operator_tier_via_principals("554e223d-e431-41ce-8913-1a7d8d81d321") is True)
check("live: v.i@/vi (ebe5f9c7) STAYS OPERATOR — via the active Tim→vi acts-for delegation, not identity",
      _remote._operator_tier_via_principals("ebe5f9c7-4d66-4717-835f-afc96088facb") is True)
check("live: an ordinary human subject resolves CLIENT (least privilege)",
      _remote._operator_tier_via_principals("26d4500d-9d93-4531-88b7-f0609e066d60") is False)
check("live: an archived no-email subject resolves CLIENT",
      _remote._operator_tier_via_principals("28848d4e-07eb-4d71-a2e5-12c140d35400") is False)
# fail-closed: None (DB unreachable / model absent) must degrade to CLIENT, never operator
import mcp_face.remote as _rmod
_saved_cache = dict(_rmod._OP_SHADOW_CACHE)
_rmod._OP_SHADOW_CACHE.clear()
try:
    from unittest import mock as _mock
    with _mock.patch("runtime.scope._q", side_effect=Exception("DB down")):
        _fc = _remote._operator_tier_via_principals("554e223d-e431-41ce-8913-1a7d8d81d321")
    check("fail-closed: when the principal table cannot be read, the verdict is None → the gate gives CLIENT",
          _fc is None)
finally:
    _rmod._OP_SHADOW_CACHE.clear()
    _rmod._OP_SHADOW_CACHE.update(_saved_cache)
# the residual divergence vs the OLD env default is still RECORDED loud (a witness, never the decider)
import fabric.config as fcfg
audit_path = os.path.join(fcfg.STORE_DIR, "remote_mcp_audit.jsonl")
before_n = sum(1 for _ in open(audit_path)) if os.path.exists(audit_path) else 0
# t.geldard@ (now OPERATOR live) diverges from the OLD env default (which was CLIENT for it) → recorded
_remote._operator_shadow_audit("554e223d-e431-41ce-8913-1a7d8d81d321", _remote.TIER_OPERATOR)
after_lines = open(audit_path).readlines() if os.path.exists(audit_path) else []
check("the residual divergence vs the OLD env default is RECORDED (OPERATOR_SHADOW_DIVERGENCE, never silent)",
      len(after_lines) == before_n + 1
      and json.loads(after_lines[-1])["event"] == "OPERATOR_SHADOW_DIVERGENCE")
# ebe5f9c7 (v.i@) matched the old env default (both operator) → no divergence → nothing recorded
_remote._operator_shadow_audit("ebe5f9c7-4d66-4717-835f-afc96088facb", _remote.TIER_OPERATOR)
check("a decision that AGREES with the old env default records NOTHING (divergence-only convention)",
      sum(1 for _ in open(audit_path)) == before_n + 1)

# ══ the scope grammar registry (the C2.1 vocabulary leg) ════════════════════════════════════════════════
print("[GRAMMAR] scope_grammar/ — one registered grammar, three dialects parse into it")
from contracts.scope_grammar import parse_scope, normalize, registered_verbs
check("the verb registry discovers from files (A's five + create/deploy/manage)",
      set(registered_verbs()) == {"read", "write", "execute", "admin", "approve", "create", "deploy", "manage"})
check("A's verb-first dialect parses (write:leads → verb=write, object=leads)",
      parse_scope("write:leads") == {"verb": "write", "domain": None, "resource": None,
                                     "object": "leads", "raw": "write:leads"})
check("C's verb-last dialect parses (company:design:write → verb=write, domain=company, resource=design)",
      parse_scope("company:design:write")["verb"] == "write"
      and parse_scope("company:design:write")["domain"] == "company")
check("normalization is canonical + idempotent", normalize("company:design:write") == "write"
      and normalize(normalize("write:leads")) == "write:leads")
for bad in ("frobnicate:thing", "read:write", ""):
    try:
        parse_scope(bad)
        check(f"ghost/ambiguous scope {bad!r} rejected", False)
    except ValueError:
        check(f"ghost/ambiguous scope {bad!r} rejected fail-loud (registry-is-truth)", True)

print(f"\nALL {PASS} CHECKS PASSED — L2-IDENTITY C2.1–C2.5 verified by use "
      f"(C2.2 FLIPPED 2026-07-03 — principal-table authority, fail-closed, verified by use).")
