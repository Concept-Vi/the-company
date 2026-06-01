"""tests/panel_acceptance.py — add a panel to the interface, through the interface (slice 14).

The honest, BOUNDED capability: the brain authors a DECLARATIVE panel definition (a generic
renderer displays it), validated to allowed field types/targets — NEVER arbitrary interface
code. Additive + git-committed (reversible). Fields edit only real config (mode/model/persona).
This is what makes "update the app through its interface" real-but-bounded, not a fake node.
"""
import os, sys, tempfile, shutil, subprocess, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def git(root, *a):
    return subprocess.run(["git", "-C", root, *a], capture_output=True, text=True, check=True).stdout.strip()


work = tempfile.mkdtemp(prefix="panel-test-")
try:
    repo = os.path.join(work, "company"); nodes = os.path.join(repo, "nodes")
    os.makedirs(nodes)
    subprocess.run(["git", "init", repo], capture_output=True, check=True)
    git(repo, "config", "user.email", "t@t"); git(repo, "config", "user.name", "t")
    open(os.path.join(nodes, "seed.py"), "w").write("VERSION='1'\nKIND='process'\nPORTS_IN={}\nPORTS_OUT={}\ndef run(i,c): return 1\n")
    git(repo, "add", "-A"); git(repo, "commit", "-m", "baseline")

    store = FsStore(os.path.join(work, "store"))
    reg = NodeRegistry(); reg.discover([nodes])
    suite = Suite(store, reg, nodes_dir=nodes)

    # a brain-authored def with VALID fields + an attempted ARBITRARY-CODE/illegal field
    deftn = {"title": "Settings", "fields": [
        {"key": "mode", "label": "Presence", "type": "select", "target": "mode",
         "options": ["listening", "off"]},
        {"key": "model", "label": "Model", "type": "text", "target": "model"},
        {"key": "evil", "label": "pwn", "type": "script", "target": "filesystem", "code": "rm -rf /"},
    ]}
    sid = suite.inbox.surface("ui_panel", {"name": "settings", "panel": deftn}, default="reject", resolved=None)
    suite.resolve_surfaced(sid, "approve")
    path = suite.apply_panel(sid)

    written = json.loads(open(path).read())
    targets = [f["target"] for f in written["fields"]]
    check("valid fields kept (mode, model)", "mode" in targets and "model" in targets)
    check("the arbitrary-code field is DROPPED (no script type / filesystem target)",
          "filesystem" not in targets and all(f["type"] in ("select", "text") for f in written["fields"]))
    check("no 'code' key survives into any field", all("code" not in f for f in written["fields"]))
    check("apply_panel git-committed the panel (reversible)", "[self-apply]" in git(repo, "log", "-1", "--format=%s"))
    check("the panel file is additive (new JSON in panels/)", os.path.basename(path) == "settings.json")
    check("list_panels surfaces it", any(p["id"] == "settings" for p in suite.list_panels()))

    # apply_surfaced dispatches by class (ui_panel → panel, not node-type)
    sid2 = suite.inbox.surface("ui_panel", {"name": "presence", "panel": {"title": "Presence",
            "fields": [{"key": "m", "label": "Mode", "type": "select", "target": "mode", "options": ["focus"]}]}},
            default="reject", resolved=None)
    suite.resolve_surfaced(sid2, "approve")
    r = suite.apply_surfaced(sid2)
    check("apply_surfaced routes ui_panel to apply_panel", r["kind"] == "ui_panel")
    check("a SECOND, different panel renders (generic renderer, not a settings-shaped hole)",
          len(suite.list_panels()) == 2)

    # a fully-malformed def doesn't crash apply (contained) — no fields, but a valid file
    sid3 = suite.inbox.surface("ui_panel", {"name": "broken", "panel": {"oops": True}}, default="reject", resolved=None)
    suite.resolve_surfaced(sid3, "approve")
    suite.apply_panel(sid3)
    check("a malformed def yields an empty-but-valid panel (no crash)",
          any(p["id"] == "broken" and p["fields"] == [] for p in suite.list_panels()))

    print(f"\nALL {PASS} CHECKS PASS — declarative panels: validated (no arbitrary code), additive, git-backed")
finally:
    shutil.rmtree(work, ignore_errors=True)
