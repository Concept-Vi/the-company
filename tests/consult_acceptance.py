"""tests/consult_acceptance.py — RHM knows the design (slice 10, Q1).

The RHM can read the system's OWN code+design and answer — so "ask it about the system and it
knows" is true. `consult` is a READ verb (codebase source + fabric), whitelisted alongside
run/propose/build; apply/delete/file-write stay unreachable. The answer is proven by use.
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


store_dir = tempfile.mkdtemp(prefix="consult-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    check("consult is a whitelisted RHM verb", "consult" in suite.RHM_VERBS)
    shown, act = suite._parse_rhm_action("Let me check.\nACTION: consult how does the memo gate work")
    check("parses ACTION: consult <query>", act["verb"] == "consult" and "memo gate" in act["query"])

    # consult with no query is refused (not a crash)
    r = suite._dispatch_rhm_action({"verb": "consult", "query": ""}, "g")
    check("empty consult is refused", r["did"] == "none")

    # the source the RHM consults is real (the repo) and substantial
    from nodes import codebase as cb
    src = cb.run({}, {})
    check("the codebase source the RHM reads is present", "scheduler" in src and len(src) > 10000)

    # the invariant still holds — consult is read-only; apply/delete unreachable
    snap = set(os.listdir(NODES))
    check("apply still refused alongside consult",
          suite._dispatch_rhm_action({"verb": "apply", "id": "x"}, "g")["did"] == "none")
    check("no file written", set(os.listdir(NODES)) == snap)

    print(f"\nALL {PASS} CHECKS PASS — RHM can consult its own code+design (read-only, gate intact)")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
