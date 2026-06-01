"""tests/twin_acceptance.py — the twin mechanism (slice 7, B1, B3).

The twin (context-05) reasons from the EXPLICIT model of Tim (the principles) and grades
provenance: Tim's own words are GOLD (the only training signal); the twin's output is
WORKING-grade and must never masquerade as ground truth (prevents model-collapse). The
mechanism is operational cold-start; predictive strength is corpus-fed later (B4, slice 9).
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


store_dir = tempfile.mkdtemp(prefix="twin-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    check("model_of_tim is a discovered source node-type", "model_of_tim" in reg)

    # B1 — the twin's context carries the EXPLICIT model of Tim (compact digest of the principles)
    digest = suite._model_of_tim_digest()
    if digest:   # only assert content when the foundation file is present in this environment
        check("digest is compact (not the whole file)", len(digest) <= 2600)
        check("digest carries Tim's principle statements (e.g. single origin)",
              "origin" in digest.lower() or "entity" in digest.lower())
    else:
        check("digest degrades gracefully when the model file is absent", digest == "")

    # B3 — provenance grading: Tim's words gold, the twin's working
    check("Tim's turn is graded gold", suite._provenance_grade("user") == "gold")
    check("the twin's turn is graded working", suite._provenance_grade("assistant") == "working")

    # only gold is the training signal (no model-collapse from the twin's own echoes)
    store.append_chat({"role": "user", "text": "Tim said this", "grade": "gold"})
    store.append_chat({"role": "assistant", "text": "twin inferred this", "grade": "working"})
    store.append_chat({"role": "user", "text": "Tim again", "grade": "gold"})
    sig = suite.training_signal()
    check("training signal is gold-only", len(sig) == 2 and all(t["grade"] == "gold" for t in sig))
    check("the twin's own output is NOT training signal", all("inferred" not in t["text"] for t in sig))

    print(f"\nALL {PASS} CHECKS PASS — twin: explicit model-of-Tim in context + gold/working grading")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
