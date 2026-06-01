"""tests/rhm_action_acceptance.py — RHM action-through-the-gate (slice 1, C1).

The decision-compiler DOWN: the RHM can act from conversation, but ONLY through whitelisted,
governed verbs — propose (→ surfaces for operator approval, CONFIRM) and run (→ AUTO,
recomputable). It has NO path to apply / delete / file-write (E6 invariant). The LLM signals
intent with a trailing `ACTION:` line; the dispatcher enforces the whitelist.

This test proves the SECURITY invariant deterministically (crafted apply/delete actions do
NOTHING) + the action-line parsing. The propose→surface→approve→live loop is proven by use.
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


store_dir = tempfile.mkdtemp(prefix="rhm-act-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)
    g = "rhm-act"
    suite.create_node(g, "constant", config={"value": "hello"}, node_id="c")
    suite.create_node(g, "uppercase", node_id="u")
    suite.connect(g, "c", "value", "u", "text")

    # --- ACTION-line parsing ---
    clean, act = suite._parse_rhm_action("Sure, running it now.\nACTION: run")
    check("parses an ACTION: run line", act == {"verb": "run"})
    check("strips the ACTION line from the shown reply", "ACTION:" not in clean and "running it now" in clean)
    clean, act = suite._parse_rhm_action("I'll draft that.\nACTION: propose reverse :: reverse the input text")
    check("parses ACTION: propose <name> :: <spec>",
          act["verb"] == "propose" and act["name"] == "reverse" and "reverse the input" in act["spec"])
    clean, act = suite._parse_rhm_action("Just a normal grounded answer about the system.")
    check("no ACTION line → no action", act is None)

    # --- THE SECURITY INVARIANT: whitelist {run, propose}; everything else does NOTHING ---
    snapshot_files = set(os.listdir(NODES))
    r = suite._dispatch_rhm_action({"verb": "apply", "id": "anything"}, g)
    check("RHM 'apply' action is REFUSED (cannot self-approve/apply)", r["did"] == "none")
    check("no node file was written by a refused apply", set(os.listdir(NODES)) == snapshot_files)

    r = suite._dispatch_rhm_action({"verb": "delete", "node": "c"}, g)
    check("RHM 'delete' action is REFUSED", r["did"] == "none")
    check("the node was NOT deleted by a refused delete", any(n.id == "c" for n in suite._load(g).nodes))

    r = suite._dispatch_rhm_action({"verb": "write_file", "path": "/etc/x"}, g)
    check("an arbitrary verb is REFUSED (whitelist, not blacklist)", r["did"] == "none")

    # --- the ALLOWED verbs work ---
    r = suite._dispatch_rhm_action({"verb": "run"}, g)
    check("RHM 'run' executes (AUTO, recomputable)", r["did"] == "run" and "u" in r["ran"])

    print(f"\nALL {PASS} CHECKS PASS — RHM acts only through the gate; apply/delete/write are unreachable")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
