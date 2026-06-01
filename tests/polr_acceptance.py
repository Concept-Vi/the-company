"""tests/polr_acceptance.py — AI-path-of-least-resistance: registry as source of truth + ask-don't-fabricate.

Tim: "the registry should be leveraged; making things up is as bad as failing; if info it needs
isn't registered, it should ASK." So: registered-target options come from the REGISTRY (never the
brain's guess — fixes the gpt-4 hallucination), and a NEEDS escape turns missing-info into a
surfaced question instead of a fabrication. The model-call paths are proven by use; here the
deterministic core: registry-fill, the NEEDS detector, and the ask-surfacing.
"""
import os, sys, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


store_dir = tempfile.mkdtemp(prefix="polr-test-")
try:
    import subprocess
    repo = os.path.join(store_dir, "repo")                      # a git temp repo so apply_panel can commit (F2)
    nd = os.path.join(repo, "nodes"); os.makedirs(nd)
    subprocess.run(["git", "init", repo], capture_output=True, check=True)
    subprocess.run(["git", "-C", repo, "config", "user.email", "t@t"], capture_output=True)
    subprocess.run(["git", "-C", repo, "config", "user.name", "t"], capture_output=True)
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=nd)   # repo_root = the git temp repo; panels_dir = repo/panels

    # capability registry — the source of truth fed to the brain
    cap = suite.capabilities()
    check("capabilities lists real node-types", "constant" in cap["node_types"] and "portal" in cap["node_types"])
    check("capabilities lists the modes", len(cap["modes"]) == 8)
    check("capabilities lists models (real or fallback, never empty)", len(cap["models"]) >= 1)

    # registered-target options come from the REGISTRY, not a guess
    check("mode options = the 8 registered modes", suite._registered_options("mode") == list(suite.MODES))
    check("model options = available_models (the registry)", suite._registered_options("model") == suite.available_models())

    # apply_panel OVERRIDES the brain's guessed options with the registry — fixes the gpt-4 hallucination
    bad = {"title": "S", "fields": [{"key": "m", "label": "Model", "type": "select", "target": "model",
                                     "options": ["gpt-4", "claude-3-opus"]}]}     # the hallucinated guess
    sid = suite.inbox.surface("ui_panel", {"name": "polr_models", "panel": bad}, default="reject", resolved=None)
    suite.resolve_surfaced(sid, "approve")
    path = suite.apply_panel(sid)                            # writes to repo/panels + git-commits
    import json
    applied = json.loads(open(path).read())
    model_opts = applied["fields"][0]["options"]
    check("the hallucinated gpt-4/claude options were REPLACED by the registry",
          "gpt-4" not in model_opts and model_opts == suite.available_models())

    # ask-don't-fabricate: the NEEDS detector + surfacing
    check("NEEDS: is detected", suite._needs("NEEDS: a list of the user's projects") == "a list of the user's projects")
    check("normal output is not a NEEDS", suite._needs("export default function X(){}") is None)
    qid = suite._ask_operator("what are your projects?", "ctx")
    q = suite.inbox.get(qid)
    check("an ask surfaces a 'question' decision for the operator", q and q["action"] == "question")
    check("the question is unresolved (awaiting the operator)", q.get("resolved") is None)

    print(f"\nALL {PASS} CHECKS PASS — registry is the source of truth; missing info → ask, never fabricate")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
