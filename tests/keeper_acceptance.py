"""tests/keeper_acceptance.py — ④ THE CONTAINER, L7-KEEPER (C7.1–C7.5): the keeper as a COMPOSITION, BY USE.

The tending AI is NOT a new primitive — it is the composition of a member edge (L1) + cast_for_mode('keeper')
+ config rungs resolved through the ONE ladder + a persona record, anchored at project://<key> (KEEPER.md §4).
Every check is a real call / real query / real model fire — never code-existence.

  C7.1  the ONE ladder slot-kind in runtime/resolver.py: longest-prefix-on-address, walk-up on absence,
        fail-loud legible-absent below (a 3-rung universal→project→scope case). PURE.
  C7.2  the 4 cloud config rows are rungs (init/nav/creation at root '', domain_expertise at project://ci-processing)
        that resolve at their depths; keeper capability flags GATE the governed verb whitelist — a keeper is
        DENIED a rung-excluded verb via a LIVE keeper_guard()/governance.guard() call.
  C7.3  cast_for_mode('keeper') is non-empty + fires; per-project rung specialization changes ONE role's
        resolved framing WITHOUT touching a file (write a response_style rung → a different resolved prompt).
  C7.4  keeper_answer('project://counterpart-design', question, token) returns a real answer from the LIVE
        ledger (1743 entries), the envelope enriched with a trail; the SAME function serves the MCP face and
        an HTTP face — both AGREE on the deterministic envelope (a real bridge process, one curl).
  C7.5  the persona record resolves into the prompt; a project persona rung OVERRIDES it; removal RESTORES
        the global one.

Needs the local Postgres (127.0.0.1:15432) with 0013 (L1) + 0017 (L2) + 0023 (L7) applied and the container
migrated, AND the resident model up (127.0.0.1:8000) for the C7.4 fire. cvi_mine READ-ONLY.
  psql -f build-prep/claude-design/supabase/supabase/migrations/0023_keeper.sql
"""
import json, os, subprocess, sys, tempfile, shutil, time, urllib.request
from urllib.parse import quote

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


def psql(sql):
    env = {**os.environ, "PGPASSWORD": PG["pw"]}
    r = subprocess.run(["psql", "-h", PG["host"], "-p", PG["port"], "-U", PG["user"], "-d", PG["db"],
                        "-v", "ON_ERROR_STOP=1", "-tA", "-c", sql], capture_output=True, text=True, env=env)
    return r.returncode == 0, (r.stdout if r.returncode == 0 else r.stderr.strip())


CP = "project://counterpart-design"
CI = "project://ci-processing"

# ══════════════════════════════════════════════════════════════════════════════════════════════════
print("[C7.1] the ladder slot-kind in runtime/resolver.py — longest-prefix, walk-up, fail-loud-below")
from runtime.resolver import resolve, resolve_slot, ResolverError, _rung_matches

LADDER = {"tier": {"ladder": "address",
                   "rungs": {"": "universal", CP: "project", CP + "#mockups": "scope"}}}
check("3-rung: deepest rung wins (scope)", resolve(LADDER, {"address": CP + "#mockups"})["tier"] == "scope")
check("walk-up: no scope rung → project", resolve(LADDER, {"address": CP})["tier"] == "project")
check("walk-up past an absent scope → project", resolve(LADDER, {"address": CP + "#other"})["tier"] == "project")
check("walk all the way up → universal", resolve(LADDER, {"address": "project://elsewhere"})["tier"] == "universal")
check("no address on the coordinate → universal only", resolve(LADDER, {})["tier"] == "universal")
check("boundary guard: 'project://x' does NOT cover 'project://xy'", not _rung_matches("project://x", "project://xy"))
check("boundary match: 'project://x' covers 'project://x#s' and '/y'",
      _rung_matches("project://x", "project://x#s") and _rung_matches("project://x", "project://x/y"))
_raised = False
try:
    resolve_slot({"ladder": "address", "rungs": {CP + "/y": 2}}, {"address": "project://z"})
except ResolverError:
    _raised = True
check("fail-loud legible-absent BELOW the shallowest rung (no universal, no default) RAISES", _raised)
check("a 'default' catches the below-shallowest case (legible fallback, not a crash)",
      resolve_slot({"ladder": "address", "rungs": {CP + "/y": 2}, "default": 0}, {"address": "project://z"}) == 0)
check("PURE: identical inputs → identical output",
      resolve(LADDER, {"address": CP}) == resolve(LADDER, {"address": CP}))

# ══════════════════════════════════════════════════════════════════════════════════════════════════
print("[C7.2] the 4 cloud rows land as rungs at their depths; capability flags gate the verb whitelist")
from runtime import keeper, governance

ok, out = psql("select config_key || '@' || coalesce(nullif(address_prefix,''),'<universal>') "
               "from container.config_rung where source_meta->>'source' = 'cvi_mine.keeper_agent_config' "
               "order by config_key")
landed = set(out.split()) if ok else set()
check("initialization_procedure landed at the universal rung", "initialization_procedure@<universal>" in landed)
check("navigation_capabilities landed at the universal rung", "navigation_capabilities@<universal>" in landed)
check("creation_capabilities landed at the universal rung", "creation_capabilities@<universal>" in landed)
check("domain_expertise landed at the project://ci-processing rung (cloud override_level 2)",
      "domain_expertise@" + CI in landed)

coord_cp = {"address": CP, "mode": "keeper"}
coord_ci = {"address": CI, "mode": "keeper"}
check("navigation_capabilities resolves at CP by walk-up to the universal rung",
      keeper.resolve_config("navigation_capabilities", coord_cp).get("search_resources") is True)
check("domain_expertise resolves ONLY at its project rung (CI has it, CP walks up to legible-absent)",
      "pipeline_composition" in keeper.resolve_config("domain_expertise", coord_ci).get("specializations", [])
      and keeper.resolve_config("domain_expertise", coord_cp).get("_not_configured") is True)

# THE FLAGS GATE THE WHITELIST — write a project rung that EXCLUDES create_resources at CP, then a live
# guard() denies the mapped verb ('build'); a still-permitted verb ('consult') passes. Clean up after.
psql("insert into container.config_rung(address_prefix,config_key,config_value,source_meta) values "
     "('%s','creation_capabilities','{\"create_projects\":true,\"create_resources\":false,"
     "\"create_workflows\":true,\"annotate_entities\":true}'::jsonb,'{\"source\":\"C7.2 test\"}'::jsonb) "
     "on conflict (address_prefix,config_key) do update set config_value=excluded.config_value" % CP)
try:
    v = keeper.keeper_verbs(coord_cp)
    check("with the project rung, 'build' is EXCLUDED from the keeper's whitelist", "build" not in v["allowed"])
    check("the denial names the excluding capability flag (legible)",
          "create_resources" in v["denied"].get("build", ""))
    _denied = False
    try:
        keeper.keeper_guard("build", coord_cp, lambda: "BUILT")
    except governance.GovernanceError:
        _denied = True
    check("a LIVE keeper_guard('build') call DENIES the rung-excluded verb (fail loud)", _denied)
    check("a still-permitted verb passes the gate (keeper_guard('consult') → runs, inspect=AUTO)",
          keeper.keeper_guard("consult", coord_cp, lambda: "READ-OK") == "READ-OK")
finally:
    psql("delete from container.config_rung where address_prefix='%s' and config_key='creation_capabilities'" % CP)
check("cleanup: the C7.2 test rung is gone (creation_capabilities walks back up to universal-all-true)",
      keeper.keeper_verbs(coord_cp)["denied"] == {})

# ══════════════════════════════════════════════════════════════════════════════════════════════════
print("[C7.3] the keeper cast fires for mode='keeper'; a per-project rung changes a role's framing (no file edit)")
from runtime.cognition import role_registry
from runtime.resolver import resolve_slot as _rslot

cast = role_registry().cast_for_mode("keeper")
cast_ids = {r.id for r in cast}
check("cast_for_mode('keeper') is NON-EMPTY and includes the answering role keeper_reader", "keeper_reader" in cast_ids)
check("the cast is a real cast (>1 role: keeper_reader + an existing read role scoped to keeper)", len(cast_ids) >= 2)
kr = role_registry()["keeper_reader"]

def resolved_keeper_prompt(address):
    c = keeper._coordinate(address, None)          # sets c['response_style'] from the ladder (default 'standard')
    return _rslot(kr.prompt_slot, c)

psql("delete from container.config_rung where config_key='response_style'")   # clean slate
p_before = resolved_keeper_prompt(CP)
psql("insert into container.config_rung(address_prefix,config_key,config_value,source_meta) values "
     "('%s','response_style','\"thorough\"'::jsonb,'{\"source\":\"C7.3 test\"}'::jsonb) "
     "on conflict (address_prefix,config_key) do update set config_value=excluded.config_value" % CP)
try:
    p_after = resolved_keeper_prompt(CP)
    p_other = resolved_keeper_prompt("project://elsewhere")   # no rung there → walks up → 'standard'
    check("writing a project response_style rung CHANGES keeper_reader's resolved prompt (no file touched)",
          p_after != p_before and "THOROUGHLY" in p_after)
    check("the change is PER-PROJECT: another address (no rung) resolves the standard framing",
          p_other == p_before and "THOROUGHLY" not in p_other)
finally:
    psql("delete from container.config_rung where config_key='response_style'")
check("removal restores the standard framing (walk-up, no file edit)",
      resolved_keeper_prompt(CP) == p_before)

# ══════════════════════════════════════════════════════════════════════════════════════════════════
print("[C7.5] the persona resolves into the prompt; a project rung overrides; removal restores the global one")
glob = keeper.resolve_persona(coord_cp)
check("the global persona resolves at CP (universal rung)", glob is not None and glob.get("name") == "Keeper")
env0 = keeper.compose_envelope(CP, "test", None)
check("the persona resolves INTO the prompt block (## Persona present)",
      "## Persona" in keeper.keeper_context_block(env0) and "Keeper" in keeper.keeper_context_block(env0))
psql("insert into container.config_rung(address_prefix,config_key,config_value,source_meta) values "
     "('%s','persona','{\"name\":\"CP-Keeper\",\"voice\":\"design-substrate specialist\",\"stance\":\"I tend the DNA.\"}'::jsonb,"
     "'{\"source\":\"C7.5 test\"}'::jsonb) on conflict (address_prefix,config_key) do update set config_value=excluded.config_value" % CP)
try:
    over = keeper.resolve_persona(coord_cp)
    check("a project persona rung OVERRIDES the global persona (deeper rung wins)", over.get("name") == "CP-Keeper")
    check("the override is per-project (ci-processing still resolves the global persona)",
          (keeper.resolve_persona(coord_ci) or {}).get("name") == "Keeper")
    env1 = keeper.compose_envelope(CP, "test", None)
    check("the overriding persona resolves into the prompt block", "CP-Keeper" in keeper.keeper_context_block(env1))
finally:
    psql("delete from container.config_rung where address_prefix='%s' and config_key='persona'" % CP)
check("removal RESTORES the global persona (walk-up to the universal rung)",
      (keeper.resolve_persona(coord_cp) or {}).get("name") == "Keeper")

# ══════════════════════════════════════════════════════════════════════════════════════════════════
print("[C7.4] keeper_answer over the LIVE ledger; the SAME function serves MCP + HTTP (both agree)")
from runtime.suite import Suite
from runtime.registry import NodeRegistry
from store.fs_store import FsStore

work = tempfile.mkdtemp(prefix="keeper-acc-")
NODES = os.path.join(ROOT, "nodes")
_reg = NodeRegistry(); _reg.discover([NODES])
suite = Suite(FsStore(os.path.join(work, "store")), _reg, nodes_dir=NODES)

det = suite.keeper_answer(CP, "What does this project hold?", {"user_id": "operator://tim"}, fire=False)
env = det["envelope"]
check("the envelope carries the coordinate anchored at the address (the accreting half)",
      env["coordinate"]["address"] == CP and env["coordinate"]["mode"] == "keeper")
check("territory composed the LIVE ledger leg (counterpart-design = 1743 entries)",
      (env["territory"].get("project") or {}).get("ledger", {}).get("entries") == 1743)
check("the trail accreted through the stages (arrive→compose→parametrize→fire)",
      [t["stage"] for t in env["trail"]][:4] == ["arrive", "compose", "parametrize", "fire"])
check("the governed-verb whitelist is on the envelope (the flags that execute)",
      "consult" in env["verbs"]["allowed"])

import mcp_face.tools.keeper as _ktool
_captured = {}
class _FakeMCP:
    def tool(self, *a, **k):
        def deco(fn):
            _captured[fn.__name__] = fn
            return fn
        return deco
_ktool.register(_FakeMCP(), suite)
check("the `keeper` MCP tool file-drop registers (register(mcp, suite) exposes the tool)", "keeper" in _captured)
mcp_det = _captured["keeper"](address=CP, question="What does this project hold?", user_id="operator://tim", fire=False)
check("the MCP tool routes to the SAME Suite.keeper_answer (envelope identical to the direct call)",
      mcp_det["envelope"]["coordinate"] == env["coordinate"]
      and mcp_det["envelope"]["config"] == env["config"]
      and mcp_det["envelope"]["verbs"]["allowed"] == env["verbs"]["allowed"])

TEST_PORT = 8794
bproc = subprocess.Popen([os.path.join(ROOT, ".venv", "bin", "python"), "runtime/bridge.py", str(TEST_PORT)],
                         cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         env={**os.environ, "COMPANY_TEST_RUN": "1"})
try:
    deadline = time.time() + 60
    up = False
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{TEST_PORT}/api/now", timeout=2); up = True; break
        except Exception:
            time.sleep(1.5)
    check(f"the bridge face serves on :{TEST_PORT} (real runtime/bridge.py process)", up)
    url = (f"http://127.0.0.1:{TEST_PORT}/api/keeper?address={quote(CP)}"
           f"&question={quote('What does this project hold?')}&user_id={quote('operator://tim')}&fire=0")
    bd = json.loads(urllib.request.urlopen(url, timeout=60).read())
    check("the HTTP face returns the SAME deterministic envelope as the Suite/MCP faces (law 9)",
          bd["envelope"]["coordinate"] == env["coordinate"]
          and bd["envelope"]["config"] == env["config"]
          and (bd["envelope"]["territory"].get("project") or {}).get("ledger", {}).get("entries") == 1743)
finally:
    bproc.terminate()
    try:
        bproc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        bproc.kill()

# the REAL ANSWER (fire=True) — a live model fire grounded in the ledger. Skipped-with-note if the resident
# model is down (never a false green).
model_up = False
try:
    urllib.request.urlopen("http://127.0.0.1:8000/v1/models", timeout=3); model_up = True
except Exception:
    model_up = False
if model_up:
    live = suite.keeper_answer(CP, "In one line, what does this project hold and what is its standing?",
                               {"user_id": "operator://tim"}, fire=True)
    ans = live.get("answer") or {}
    check("keeper_answer FIRES the cast and returns a real grounded answer from the live ledger",
          isinstance(ans, dict) and isinstance(ans.get("answer"), str) and len(ans["answer"]) > 0)
    check("the answer is grounded in THIS project's data (its 1743 entries / active standing / design)",
          ("1743" in ans["answer"]) or ("active" in ans["answer"].lower()) or ("design" in ans["answer"].lower()))
    check("the trail closes with an 'answer' stage naming the fired cast",
          live["envelope"]["trail"][-1]["stage"] == "answer" and "keeper_reader" in live["envelope"]["trail"][-1]["fired"])
else:
    print("  ..  [C7.4 live fire] resident model (127.0.0.1:8000) DOWN — the fire=True answer is UNVERIFIED "
          "here (NOT green; the deterministic envelope + both faces are proven above). Bring the model up + re-run.")

shutil.rmtree(work, ignore_errors=True)

print(f"\nkeeper_acceptance: ALL {PASS} CHECKS PASSED"
      + ("" if model_up else "  (+ the live-fire answer needs the resident model up — noted, not green)"))
