"""tests/automation_acceptance.py — the L-⑤-auto lane's TEETH (Capability Fabric §4 ⑤).

Proves the ⑤ AUTOMATION family BY USE against STUBS (lead-only law — this worker fires NO real claude /
schedule / CronDelete / `claude auth status`, loads NO model; the REAL round-trips are the lead's
'live-verify pending (lead)' slice, NEVER green-painted). It exercises the handler cmd-builders +
intent-builders + the cost fold + redaction + the rail routing + every fail-loud path, plus the
one-handler-two-faces delegation (the MCP face returns the byte-identical handler dict).

Checks (all fail-loud, exit 0 = pass / 1 = a failed check):
  1. WIRING — the four ⑤ handlers wire onto HANDLERS on the specced rails (registry-is-truth);
  2. auto.cost — the usage FOLD over agent_sessions.turn sums tokens+cost, the session filter scopes,
     a turn without usage is ignored, an empty store is an HONEST zero (never fabricated), a broken
     store FAILS LOUD (not a zero total);
  3. auto.auth — direct-read returns the credential METHOD read row + the REDACTION contract; _redact
     actually strips the secret fields (the secret NEVER transits); the host-act boundary is named;
  4. auto.routines — list/get is a direct-read; act builds the PROPOSED native argv (run-now/pause/
     one-off=cloud `claude schedule …`, cancel-session-task=native CronDelete) on rail R3 and NEVER
     shells; cancel-session-task without task_id, an unknown act, and an unknown op all fail loud;
  5. auto.workflows — list catalogs goal(R1)/loop(R2)/parallel(consult, the LIVE primitive, NOT here);
     set-goal builds a /goal deliver intent on R1 (the EXACT native command, session-scoped), goal-
     status/clear-goal map to `/goal`/`/goal clear`, loop builds a /loop wire JOB on R2; the fail-loud
     paths (set-goal w/o session, w/o condition, loop w/o interval, unknown act) refuse;
  6. ASYNC HONESTY — every R1/R2/R3 act returns a RECEIPT (intent/job + watch/consent), NEVER a
     pretended typed result;
  7. DRY DELEGATION — the MCP face tool returns the byte-identical dict the handler returns (one
     handler, two faces — the §3.3 teeth, scoped to ⑤).

Run: ./.venv/bin/python tests/automation_acceptance.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from runtime import capability_handlers as ch
from runtime.capability_handlers import automation as A
from runtime.capability_handlers.automation import _redact

PASS = 0
FAIL = 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f"  XX  {label}  {detail}")


def raises(fn, exc=Exception):
    try:
        fn()
        return False
    except exc:
        return True
    except Exception:
        return False


# ── stub suite + store (the cost fold's source; NO real supervisor) ──
class StubStore:
    def __init__(self, evs, broken=False):
        self._evs = evs
        self._broken = broken

    def events_since(self, seq):
        if self._broken:
            raise OSError("events.jsonl unreadable (simulated)")
        return [e for e in self._evs if e.get("seq", -1) > seq]


class StubSuite:
    def __init__(self, evs=None, broken=False):
        self.store = StubStore(evs or [], broken=broken)


TURNS = [
    {"seq": 1, "kind": "agent_sessions.turn", "session": "a1",
     "usage": {"input_tokens": 100, "output_tokens": 50, "cost_usd": 0.002, "model": "sonnet"}},
    {"seq": 2, "kind": "agent_sessions.turn", "session": "a2",
     "usage": {"input_tokens": 10, "output_tokens": 5, "cost_usd": 0.0001, "model": "haiku"}},
    {"seq": 3, "kind": "agent_sessions.idle", "session": "a1"},       # no usage — ignored by the fold
    {"seq": 4, "kind": "agent_sessions.turn", "session": "a1"},        # turn WITHOUT usage — ignored
]


print("=== automation_acceptance — the ⑤ AUTOMATION family (L-⑤-auto, stubs only) ===")

# ── 1 · wiring ──
print("\n[1] the four ⑤ handlers wire onto HANDLERS on the specced rails")
# auto.auth flipped to R3 once it gained the REOPENED CC-24 host-config acts (its READ op is still a
# direct-read served by the SAME fn; the declared rail is the WRITE rail — the routines/workflows
# convention). Only auto.cost stays a pure direct-read (readonly).
EXPECT_RAIL = {"auto.routines": "R3", "auto.workflows": "R1",
               "auto.cost": "direct-read", "auto.auth": "R3"}
for k, r in EXPECT_RAIL.items():
    h = ch.HANDLERS[k]
    check(f"{k}: built + rail {r}", h.built and h.rail == r, f"built={h.built} rail={h.rail}")
check("auto.cost is readonly (the one pure direct-read in ⑤)",
      ch.HANDLERS["auto.cost"].readonly)
check("auto.routines/auto.workflows/auto.auth are NOT readonly (write rails — R3/R1)",
      not ch.HANDLERS["auto.routines"].readonly and not ch.HANDLERS["auto.workflows"].readonly
      and not ch.HANDLERS["auto.auth"].readonly)

# ── 2 · auto.cost — the usage fold ──
print("\n[2] auto.cost — the fold over agent_sessions.turn `usage`")
suite = StubSuite(TURNS)
r = A.cost(suite, "read")
check("rail=direct-read", r["rail"] == "direct-read")
check("sums input_tokens across the 2 usage-bearing turns (100+10)", r["total"]["input_tokens"] == 110)
check("sums output_tokens (50+5)", r["total"]["output_tokens"] == 55)
check("sums cost_usd (0.002+0.0001)", abs(r["total"]["cost_usd"] - 0.0021) < 1e-9)
check("counts only usage-bearing turns (idle + no-usage ignored)", r["turns_counted"] == 2)
check("by_model_turn_count has sonnet+haiku", set(r["by_model_turn_count"]) == {"sonnet", "haiku"})
r1 = A.cost(suite, "read", session="session://a1")
check("session filter scopes to a1 (input=100)", r1["total"]["input_tokens"] == 100)
check("session filter strips the session:// prefix in echo", r1["session"] == "session://a1")
empty = A.cost(StubSuite([]), "read")
check("empty store → HONEST zero (not fabricated)",
      empty["total"]["input_tokens"] == 0 and empty["turns_counted"] == 0)
check("empty fold names the estimate caveat", "ESTIMATE" in empty["estimate"].upper())
check("broken store FAILS LOUD (not a zero total)",
      raises(lambda: A.cost(StubSuite(broken=True), "read"), RuntimeError))
check("auto.cost unknown op fails loud", raises(lambda: A.cost(suite, "list"), ValueError))

# ── 3 · auto.auth — redacted direct-read READ + the REOPENED CC-24 host-config ACTS ──
print("\n[3] auto.auth — credential method READ (redacted) + reopened acts (CC-24, Tim's steer)")
a = A.auth(suite, "get")
check("get rail=direct-read", a["rail"] == "direct-read")
check("get names the `claude auth status` read source", a["read"]["argv"] == ["auth", "status"])
check("get redaction lists the secret fields", "token" in a["redaction"]["fields_stripped"]
      and "CLAUDE_CODE_OAUTH_TOKEN" in a["redaction"]["fields_stripped"])
check("get advertises the reopened acts (relogin/logout/setup-token AVAILABLE, not boundary)",
      set(a["acts_available"]) == {"relogin", "logout", "setup-token"})
check("get carries NO 'boundary'/'Absence-of-row' field (CC-24 acts are reopened, NOT locked out)",
      "boundary" not in a and "Absence-of-row" not in str(a))
# _redact actually strips a secret-bearing payload (the secret NEVER transits)
raw = {"method": "subscription", "account": "tim@x", "token": "sk-SECRET", "nested": {"oauth": "zzz"}}
red = _redact(raw, tuple(a["redaction"]["fields_stripped"]))
check("_redact strips top-level secret", red["token"] == "[REDACTED]")
check("_redact strips nested secret", red["nested"]["oauth"] == "[REDACTED]")
check("_redact keeps the non-secret method", red["method"] == "subscription")
# the REOPENED acts (consent-not-lockdown, R3, NEVER shelled here — the floor)
relogin = A.auth(suite, "act", act="relogin")
check("relogin rail=R3 (host-config act, NOT direct-read)", relogin["rail"] == "R3")
check("relogin builds `claude auth login` argv (grounded, Atlas)",
      relogin["proposed"]["argv"] == ["claude", "auth", "login"] and relogin["proposed"]["tier"] == "exec")
check("relogin is intent-built, NEVER shelled here (the floor)", relogin["status"] == "intent-built")
check("relogin names the R3 config-writer executor", "config-writer" in relogin["executor"])
check("relogin consent-not-lockdown (consent path, never a denial)",
      "consent" in relogin["consent"].lower() and "never a denial" in relogin["consent"])
check("relogin flags live-verify pending (lead) — never green-painted",
      "live-verify pending (lead)" in relogin["note"])
logout = A.auth(suite, "act", act="logout")
check("logout builds `claude auth logout` argv (write tier)",
      logout["proposed"]["argv"] == ["claude", "auth", "logout"] and logout["proposed"]["tier"] == "write")
check("logout reversibility names relogin (git-revert-equivalent backstop)",
      "relogin" in logout["reversible"])
st = A.auth(suite, "act", act="setup-token")
check("setup-token builds `claude setup-token` argv (exec tier)",
      st["proposed"]["argv"] == ["claude", "setup-token"] and st["proposed"]["tier"] == "exec")
check("setup-token flags returns_secret=True (the printed-token danger named loud)",
      st.get("returns_secret") is True and "secret_handling" in st)
check("setup-token NEVER folds a token into the result (the redaction floor — by NOT returning it)",
      all(k not in st for k in ("secret", "oauth_token", "claude_code_oauth_token", "token_value")))
check("setup-token consent path present (consent-not-lockdown)",
      "consent" in st and st["consent"])
check("auto.auth act=consent=True echoes 'consented'",
      A.auth(suite, "act", act="relogin", consent=True)["consent"] == "consented")
check("auto.auth unknown ACT fails loud (names the reopened acts)",
      raises(lambda: A.auth(suite, "act", act="nope"), ValueError))
check("auto.auth unknown op fails loud", raises(lambda: A.auth(suite, "list"), ValueError))

# ── 4 · auto.routines — read + R3 intent-builders ──
print("\n[4] auto.routines — direct-read + R3 native-CLI intent (NEVER shells)")
lr = A.routines(suite, "list")
check("list rail=direct-read", lr["rail"] == "direct-read")
check("list names the cloud-schedule read source", lr["read"]["argv"] == ["schedule", "list"])
rn = A.routines(suite, "act", act="run-now", routine_id="r1")
check("run-now rail=R3", rn["rail"] == "R3")
check("run-now builds the cloud `claude schedule run` argv head",
      rn["proposed"]["argv_head"] == ["claude", "schedule", "run"])
check("run-now is intent-built, NOT executed (status)", rn["status"] == "intent-built")
check("run-now names the R3 config-writer executor", "config-writer" in rn["executor"])
check("run-now carries the consent path (consent-not-lockdown)", "consent" in rn["consent"].lower())
cst = A.routines(suite, "act", act="cancel-session-task", task_id="ab12cd34")
check("cancel-session-task uses native CronDelete (not claude)",
      cst["proposed"]["tool"] == "CronDelete" and cst["proposed"]["task_id"] == "ab12cd34")
oo = A.routines(suite, "act", act="one-off", cron="0 9 * * *", prompt="check ci")
check("one-off threads cron+prompt", oo["proposed"]["cron"] == "0 9 * * *" and oo["proposed"]["prompt"] == "check ci")
check("cancel-session-task WITHOUT task_id fails loud",
      raises(lambda: A.routines(suite, "act", act="cancel-session-task"), ValueError))
check("unknown routines act fails loud",
      raises(lambda: A.routines(suite, "act", act="nuke"), ValueError))
check("unknown routines op fails loud",
      raises(lambda: A.routines(suite, "delete"), ValueError))
# the handler NEVER shells: no subprocess import path is exercised; the proposed argv is DATA
check("run-now proposed argv is data (no exit/sha keys — nothing was run)",
      "exit" not in rn and "sha" not in rn)

# ── 5 · auto.workflows — goal (R1) / loop (R2) / parallel (consult, NOT here) ──
print("\n[5] auto.workflows — /goal R1 · /loop R2 · parallel=consult (live, linked)")
wl = A.workflows(suite, "list")
check("list catalogs goal/loop/parallel", set(wl["modes"]) == {"goal", "loop", "parallel"})
check("goal mode is R1", wl["modes"]["goal"]["rail"] == "R1")
check("loop mode is R2", wl["modes"]["loop"]["rail"] == "R2")
check("parallel points at session.post consult (not rebuilt)",
      "consult" in wl["modes"]["parallel"]["what"])
sg = A.workflows(suite, "act", act="set-goal", session="session://a1", condition="all tests pass")
check("set-goal rail=R1", sg["rail"] == "R1")
check("set-goal builds the EXACT native /goal command",
      sg["native_command"] == "/goal all tests pass")
check("set-goal intent is a supervisor DELIVER (the supervisor injects, not the handler)",
      sg["intent"]["verb"] == "deliver" and "supervisor" in sg["executor"])
check("set-goal intent targets the session (strips session://)", sg["intent"]["session"] == "a1")
check("set-goal names the hooks requirement (Atlas goal.md)", "hooks" in sg["requires"].lower())
gs = A.workflows(suite, "act", act="goal-status", session="a1")
check("goal-status maps to bare `/goal`", gs["native_command"] == "/goal")
cg = A.workflows(suite, "act", act="clear-goal", session="a1")
check("clear-goal maps to `/goal clear`", cg["native_command"] == "/goal clear")
lp = A.workflows(suite, "act", act="loop", interval="5m", prompt="check deploy")
check("loop rail=R2", lp["rail"] == "R2")
check("loop builds a wire JOB (not a supervisor intent)",
      lp["status"] == "job-built" and lp["job"]["kind"] == "wire-loop")
check("loop builds the native /loop command", lp["job"]["native_command"] == "/loop 5m check deploy")
check("loop names the operator gate (/api/resolve)", "/api/resolve" in lp["operator_gate"])
check("set-goal WITHOUT session fails loud (session-scoped)",
      raises(lambda: A.workflows(suite, "act", act="set-goal", condition="x"), ValueError))
check("set-goal WITHOUT condition fails loud",
      raises(lambda: A.workflows(suite, "act", act="set-goal", session="a1"), ValueError))
check("loop WITHOUT interval fails loud (cron cadence required)",
      raises(lambda: A.workflows(suite, "act", act="loop"), ValueError))
check("unknown workflows act fails loud",
      raises(lambda: A.workflows(suite, "act", act="dance"), ValueError))

# ── 6 · async honesty — every act returns a receipt, never a pretended result ──
print("\n[6] async honesty — acts return a receipt (intent/job + watch), never a typed result")
for label, res in (("routines run-now", rn), ("workflows set-goal", sg), ("workflows loop", lp)):
    check(f"{label} carries a `watch` cursor / consequence path", "watch" in res)
    check(f"{label} carries a build status (intent/job-built)", res.get("status", "").endswith("-built"))
    check(f"{label} flags live-verify pending (lead) — never green-painted", "live-verify pending" in res["note"])

# ── 7 · DRY delegation — the MCP face returns the byte-identical handler dict ──
print("\n[7] DRY — the MCP face tool == the handler dict (one handler, two faces, scoped to ⑤)")


class StubMCP:
    def __init__(self):
        self.tools = {}

    def tool(self, annotations=None):
        def deco(fn):
            self.tools[fn.__name__] = fn
            return fn
        return deco


from mcp_face.tools import automation as face
m = StubMCP()
f_routines, f_workflows, f_cost, f_auth = face.register(m, suite)
check("face registers all four ⑤ tools", set(m.tools) == {"routines", "workflows", "cost", "auth"})
check("face exports an OPS inventory for the 4 resources",
      set(face.OPS) == {"auto.routines", "auto.workflows", "auto.cost", "auto.auth"})
# byte-identical: face(...) JSON == handler(...) JSON for the same args
pairs = [
    ("cost", json.dumps(f_cost(op="read"), sort_keys=True, default=str),
     json.dumps(A.cost(suite, "read"), sort_keys=True, default=str)),
    ("auth get", json.dumps(f_auth(op="get"), sort_keys=True, default=str),
     json.dumps(A.auth(suite, "get"), sort_keys=True, default=str)),
    ("auth act=relogin", json.dumps(f_auth(op="act", act="relogin"), sort_keys=True, default=str),
     json.dumps(A.auth(suite, "act", act="relogin"), sort_keys=True, default=str)),
    ("auth act=setup-token", json.dumps(f_auth(op="act", act="setup-token", consent=True), sort_keys=True, default=str),
     json.dumps(A.auth(suite, "act", act="setup-token", consent=True), sort_keys=True, default=str)),
    ("routines.list", json.dumps(f_routines(op="list"), sort_keys=True, default=str),
     json.dumps(A.routines(suite, "list"), sort_keys=True, default=str)),
    ("workflows set-goal", json.dumps(f_workflows(op="act", act="set-goal", session="a1", condition="x"), sort_keys=True, default=str),
     json.dumps(A.workflows(suite, "act", act="set-goal", session="a1", condition="x"), sort_keys=True, default=str)),
]
for label, face_json, hdl_json in pairs:
    check(f"DRY {label}: face dict == handler dict (byte-identical)", face_json == hdl_json,
          f"face={face_json[:120]} hdl={hdl_json[:120]}")

print(f"\n=== {PASS} passed, {FAIL} failed ===")
sys.exit(0 if FAIL == 0 else 1)
