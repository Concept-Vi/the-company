"""tests/rhm_acceptance.py — the right-hand-man chat (I2 "RHM panel"), first cut.

A grounded conversational surface: the coherent voice of the Company about ITSELF. It answers
from COMPACT GROUND TRUTH (live system state — context-05 escalation rung 1), never the 88k
codebase, and persists turns across sessions (continuity). The actual model reply is proven by
use in the browser with a ground-truth-dependent question; here we prove the substrate:
the chat log (append-only, oldest-first, persists) and the context-builder (carries ground truth).
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


store_dir = tempfile.mkdtemp(prefix="rhm-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))

    # --- chat log: append-only, oldest-first (chronological for replay), bounded ---
    store.append_chat({"role": "user", "text": "hello"})
    store.append_chat({"role": "assistant", "text": "hi — I'm the company"})
    store.append_chat({"role": "user", "text": "what can you see?"})
    hist = store.chat_history(limit=10)
    check("chat_history is oldest-first (chronological)", hist[0]["text"] == "hello")
    check("chat_history keeps roles", hist[1]["role"] == "assistant")
    check("chat_history respects the limit", len(store.chat_history(limit=2)) == 2)

    store2 = FsStore(os.path.join(store_dir, "store"))
    check("chat persists across sessions (continuity)",
          store2.chat_history(limit=10)[0]["text"] == "hello")

    # --- the context-builder carries COMPACT ground truth (not the codebase) ---
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store2, reg, nodes_dir=NODES)
    g = "rhm-graph"
    suite.create_node(g, "constant", config={"value": "x"}, node_id="c")
    suite.create_node(g, "uppercase", node_id="u")
    ctx = suite._chat_context(g)
    check("context names the graph", g in ctx)
    check("context carries the live node count (ground truth)", "2" in ctx)
    check("context lists available node-types", "uppercase" in ctx and "constant" in ctx)
    # budget raised 4000→16000 (Tim 2026-06-22: "16k min really — do not trim when there are other options");
    # still guards the no-codebase-dump invariant + the raw-ui://-dump bloat class (now capped to chrome regions).
    check("context does NOT dump the codebase source", "AGENTS.md" not in ctx and len(ctx) < 16000)

    print(f"\nALL {PASS} CHECKS PASS — RHM substrate: grounded context + persistent chat log")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
