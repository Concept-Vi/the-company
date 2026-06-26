"""tests/cc_clone_acceptance.py — structural regression gate for runtime/cc_clone.py (the point-in-time
CLONE -> fabric extension). NO real claude, NO live supervisor: the supervisor + materialize are mocked;
the REAL claude path is proven by ops/fabric_clone_probe.py. This covers the wrapper logic + the two
guarantees that encode the safety boundary: prepare_at NEVER spawns (operator-gated) and clone_at DOES.
Run: .venv/bin/python tests/cc_clone_acceptance.py
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from runtime import cc_clone

PASS, FAIL = [], []


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'ok ' if cond else 'FAIL'} {name}" + (f"  — {detail}" if detail and not cond else ""))


# ── operator_launch_cmd: the exact interactive-channel-clone command (operator runs it) ──
cmd = cc_clone.operator_launch_cmd("SID-123", "/home/tim", "clone-ab", "a desc")
ok("operator cmd resumes the materialized sid", "--resume SID-123" in cmd)
ok("operator cmd loads the channel mcp-config", "--mcp-config" in cmd and "channel.mcp.json" in cmd)
ok("operator cmd uses the dangerously-load channel flag",
   "--dangerously-load-development-channels server:company-channel" in cmd)
ok("operator cmd carries handle + session_id env",
   "COMPANY_CHANNEL_HANDLE=clone-ab" in cmd and "COMPANY_SESSION_ID=SID-123" in cmd)
ok("operator cmd cds to the resume cwd", cmd.strip().startswith("cd /home/tim"))

# ── isolate state: temp clones dir ──
tmp = tempfile.mkdtemp(prefix="cc_clone_test_")
cc_clone.CLONES_DIR = os.path.join(tmp, "clones")
os.makedirs(cc_clone.CLONES_DIR)

# ── registry I/O + _find_clone resolution (by handle / session_id / supervisor_session) ──
mat = os.path.join(tmp, "materialized.jsonl")
open(mat, "w").write("{}\n")
reg = {"kind": "supervised-clone", "handle": "clone-xy", "supervisor_session": "as-1",
       "session_id": "SID-xy", "materialized_path": mat, "at": "compact:1"}
json.dump(reg, open(os.path.join(cc_clone.CLONES_DIR, "clone-xy.json"), "w"))
ok("_find_clone by handle", cc_clone._find_clone("clone-xy")["handle"] == "clone-xy")
ok("_find_clone by session_id", cc_clone._find_clone("SID-xy")["handle"] == "clone-xy")
ok("_find_clone by supervisor_session", cc_clone._find_clone("as-1")["handle"] == "clone-xy")
try:
    cc_clone._find_clone("nonexistent")
    ok("_find_clone fail-loud on unknown", False)
except cc_clone.CloneError:
    ok("_find_clone fail-loud on unknown", True)

# ── end_clone: teardown (supervisor mocked) + delete materialized + drop registry (non-destructive) ──
cc_clone._sup = lambda *a, **k: (200, {})
e = cc_clone.end_clone("clone-xy")
ok("end_clone deletes the materialized prefix", not os.path.exists(mat) and e["materialized_deleted"])
ok("end_clone removes the registry entry",
   not os.path.exists(os.path.join(cc_clone.CLONES_DIR, "clone-xy.json")))

# ── list_clones prunes dead supervised sessions, keeps live ones ──
for h, sup in (("clone-live", "as-alive"), ("clone-dead", "as-dead")):
    json.dump({"handle": h, "supervisor_session": sup, "session_id": h},
              open(os.path.join(cc_clone.CLONES_DIR, h + ".json"), "w"))
cc_clone._alive_supervised = lambda s: s == "as-alive"
live = cc_clone.list_clones()
ok("list_clones keeps the live clone", any(r["handle"] == "clone-live" for r in live))
ok("list_clones prunes the dead clone (+ removes its file)",
   not any(r["handle"] == "clone-dead" for r in live)
   and not os.path.exists(os.path.join(cc_clone.CLONES_DIR, "clone-dead.json")))

# ── THE SAFETY-BOUNDARY GUARANTEES: prepare_at never spawns; clone_at must spawn ──
src = os.path.join(tmp, "src.jsonl")
open(src, "w").write("{}\n")
cc_clone.materialize_at_point = lambda s, at, dest_dir=None, new_sid=None: {
    "new_path": os.path.join(dest_dir or tmp, (new_sid or "x") + ".jsonl"),
    "source_sid": "srcsid", "source_untouched": True}
cc_clone.resume_cwd_for = lambda s, *c: "/home/tim"
cc_clone.build_timeline = lambda s: {"boundaries": [{"n": 1}]}


def _forbidden_sup(*a, **k):
    raise AssertionError("prepare_at MUST NOT touch the supervisor (operator-gated, materialize-only)")


cc_clone._sup = _forbidden_sup
try:
    p = cc_clone.prepare_at(src, "compact:1", description="d")
    ok("prepare_at is materialize-only — NEVER spawns (operator-gate guarantee)",
       p.get("prepared") and "operator_launch_cmd" in p and p["source_untouched"])
except AssertionError as a:
    ok("prepare_at is materialize-only — NEVER spawns (operator-gate guarantee)", False, str(a))

spawned = {"called": False}


def _spy_sup(path, body=None, method="POST", timeout=30):
    if path == "/spawn":
        spawned["called"] = True
        return 200, {"session": {"id": "as-new"}}
    return 200, {"sessions": [{"id": "as-new", "state": "idle"}]}


cc_clone._sup = _spy_sup
cc_clone._wait_idle = lambda s, timeout=120: {"id": s, "state": "idle"}
cc_clone.CHAN_DIR = os.path.join(tmp, "channels")     # don't pollute the live channel registry
c = cc_clone.clone_at(src, "compact:1", description="d")
ok("clone_at DOES spawn a supervised clone (the autonomous path)",
   spawned["called"] and c["supervisor_session"] == "as-new" and c["source_untouched"])
ok("clone_at returns the operator command alongside the supervised clone",
   "operator_launch_cmd" in c and "--dangerously-load-development-channels" in c["operator_launch_cmd"])

# the channel WIRE (overnight lane w/ lead): clone_at registers the supervised clone as a channel member
# with EXACTLY the lead's CHANNEL-LAYER schema (the dispatch side reads these fields verbatim).
import json as _json
_memp = os.path.join(cc_clone.CHAN_DIR, c["handle"] + ".json")
_mem = _json.load(open(_memp)) if os.path.exists(_memp) else {}
ok("clone_at registers a supervised channel-member with the exact lead schema",
   set(_mem.keys()) == {"handle", "session_id", "transport", "supervisor_session",
                        "supervisor_base", "cwd", "description"}
   and _mem.get("transport") == "supervised" and _mem.get("session_id") == c["session_id"]
   and _mem.get("supervisor_session") == "as-new")
ok("end_clone deregisters the channel-member (presence=truth)",
   (lambda r: not os.path.exists(_memp))(cc_clone.end_clone(c["handle"], delete_materialized=False)))

# MODEL OVERRIDE (the Fable-era resume fix): model/fallback_model flow into the /spawn body verbatim.
spawn_body = {}
def _spy_body(path, body=None, method="POST", timeout=30):
    if path == "/spawn":
        spawn_body.update(body or {})
        return 200, {"session": {"id": "as-m"}}
    return 200, {"sessions": [{"id": "as-m", "state": "idle"}]}
cc_clone._sup = _spy_body
cm = cc_clone.clone_at(src, "compact:1", description="Fable era", model="opus", fallback_model=["sonnet", "haiku"])
ok("clone_at passes model + fallback into the /spawn body (Fable-era resume fix)",
   spawn_body.get("model") == "opus" and spawn_body.get("fallback") == ["sonnet", "haiku"]
   and cm.get("model") == "opus")

# PROVIDER PASSTHROUGH (ollama-native company-model backend, 2026-06-16): provider flows into the /spawn
# body so the supervisor's _provider_env points the child CC at ollama :11434. Threaded beside model.
spawn_body_p = {}
def _spy_body_p(path, body=None, method="POST", timeout=30):
    if path == "/spawn":
        spawn_body_p.update(body or {})
        return 200, {"session": {"id": "as-p"}}
    return 200, {"sessions": [{"id": "as-p", "state": "idle"}]}
cc_clone._sup = _spy_body_p
cp = cc_clone.clone_at(src, "compact:1", description="ollama clone", provider="ollama",
                       model="kimi-k2.7-code:cloud")
# provider threads into /spawn; the MODEL is now context-size-aware-picked (TIM RULE) — kimi for a small
# ctx, deepseek-v4-flash for a big one. (Here the mocked materialize new_path doesn't exist → estimate-fail
# → the safe big model; the real kimi-vs-flash split is tested directly below via _pick_ollama_model.)
ok("clone_at passes provider into the /spawn body + model is pick-resolved (ollama)",
   spawn_body_p.get("provider") == "ollama" and cp.get("provider") == "ollama"
   and spawn_body_p.get("model") in (cc_clone.KIMI_OLLAMA_MODEL, cc_clone.OLLAMA_BIG_CTX_MODEL))

# BYTE-IDENTICAL DEFAULT: provider omitted → NO 'provider' key in the body (the existing Anthropic path
# is preserved exactly; the env-injection seam only fires when provider is set).
spawn_body_np = {}
def _spy_body_np(path, body=None, method="POST", timeout=30):
    if path == "/spawn":
        spawn_body_np.update(body or {})
        return 200, {"session": {"id": "as-np"}}
    return 200, {"sessions": [{"id": "as-np", "state": "idle"}]}
cc_clone._sup = _spy_body_np
cc_clone.clone_at(src, "compact:1", description="no provider")
ok("clone_at omits the provider key when unset (byte-identical default)",
   "provider" not in spawn_body_np)

# CONTEXT-SIZE-AWARE OLLAMA MODEL PICK (TIM RULE 2026-06-16): kimi default → deepseek-v4-flash:cloud when
# the clone's est. context > kimi's 256K window; explicit non-kimi honored; estimate-fail → safe big model.
small = os.path.join(tmp, "small.jsonl")
with open(small, "w") as f:
    f.write(json.dumps({"message": {"content": [{"type": "text", "text": "hi there, short context"}]}}) + "\n")
m, why = cc_clone._pick_ollama_model(small, None)
ok("model-pick: small ctx → kimi default", m == cc_clone.KIMI_OLLAMA_MODEL, why)

big = os.path.join(tmp, "big.jsonl")
with open(big, "w") as f:
    f.write(json.dumps({"message": {"content": [{"type": "text", "text": "x" * (4 * cc_clone.KIMI_MAX_CTX + 10000)}]}}) + "\n")
m, why = cc_clone._pick_ollama_model(big, None)
ok("model-pick: ctx > kimi window → deepseek-v4-flash:cloud (1M)", m == cc_clone.OLLAMA_BIG_CTX_MODEL, why)

m, why = cc_clone._pick_ollama_model(big, "deepseek-v4-pro:cloud")
ok("model-pick: explicit non-kimi honored (never auto-overridden, never auto -pro)", m == "deepseek-v4-pro:cloud", why)

m, why = cc_clone._pick_ollama_model("/no/such/path.jsonl", None)
ok("model-pick: estimate-fail → safe big model (deepseek-v4-flash)", m == cc_clone.OLLAMA_BIG_CTX_MODEL, why)

import shutil
shutil.rmtree(tmp, ignore_errors=True)

print(f"\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", ", ".join(FAIL))
    sys.exit(1)
print("ALL GREEN — cc_clone wrapper + safety-boundary guarantees (prepare=materialize-only, "
      "clone=spawns) hold. Real claude path: ops/fabric_clone_probe.py.")
