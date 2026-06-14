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
c = cc_clone.clone_at(src, "compact:1", description="d")
ok("clone_at DOES spawn a supervised clone (the autonomous path)",
   spawned["called"] and c["supervisor_session"] == "as-new" and c["source_untouched"])
ok("clone_at returns the operator command alongside the supervised clone",
   "operator_launch_cmd" in c and "--dangerously-load-development-channels" in c["operator_launch_cmd"])

import shutil
shutil.rmtree(tmp, ignore_errors=True)

print(f"\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", ", ".join(FAIL))
    sys.exit(1)
print("ALL GREEN — cc_clone wrapper + safety-boundary guarantees (prepare=materialize-only, "
      "clone=spawns) hold. Real claude path: ops/fabric_clone_probe.py.")
