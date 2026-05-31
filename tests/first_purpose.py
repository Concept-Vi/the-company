"""FIRST PURPOSE — the system answers a question about its OWN codebase, grounded.

The application doing what it's for: a composition reads the repo's own code into context
and the brain answers a question about it, citing the code. Live (real model). Requires ollama up.
Run: .venv/bin/python tests/first_purpose.py
"""
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from fabric import config as fcfg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GID = "first-purpose-test"
ok = True


def check(label, cond):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


def main():
    try:
        urllib.request.urlopen(fcfg.OLLAMA_DIRECT.replace("/v1", "") + "/v1/models", timeout=4)
    except Exception:
        print("  [FAIL] ollama not reachable — cannot run the live first-purpose test")
        return 1

    gpath = os.path.join(fcfg.STORE_DIR, "graphs", GID + ".json")
    if os.path.exists(gpath):
        os.remove(gpath)

    suite = Suite(FsStore(fcfg.STORE_DIR), NodeRegistry().discover([os.path.join(ROOT, "nodes")]))

    # the codebase node alone reads real source
    suite.create_node(GID, "codebase", node_id="code")
    suite.create_node(GID, "constant",
                      {"value": "What does the scheduler's memo gate do, and which file is it in?"},
                      node_id="q")
    suite.create_node(GID, "ask", {"model": fcfg.DEFAULT_BRAIN}, node_id="answer")
    suite.connect(GID, "q", "value", "answer", "question")
    suite.connect(GID, "code", "context", "answer", "context")

    r = suite.run(GID)
    res = suite.results(GID)
    ctx = res.get("code") or ""
    ans = (res.get("answer") or "")
    check("codebase node read real source (incl scheduler.py)",
          isinstance(ctx, str) and "scheduler.py" in ctx and len(ctx) > 5000)
    check("the system answered about ITS OWN code (grounded: memo + scheduler)",
          isinstance(ans, str) and "memo" in ans.lower() and "scheduler" in ans.lower())
    print(f"\n  Q: What does the scheduler's memo gate do, and which file is it in?\n  A: {ans[:400]}")

    print("\n" + ("✅ FIRST PURPOSE WORKS — the system answered about its own codebase"
                  if ok else "❌ FIRST PURPOSE FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
