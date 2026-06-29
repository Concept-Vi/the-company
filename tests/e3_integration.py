"""E3 integration smoke — a REAL model call through the guarded fabric.

Proves the acceptance live: an AI node calls the ollama-cloud brain; output is
non-empty; a structured request validates; and the guards are real. Requires the
ollama service up (fails LOUD if not — no silent skip).

Run: .venv/bin/python tests/e3_integration.py
"""
import os
import shutil
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic import BaseModel
from contracts.node_record import NodeInstance, Edge, Graph
from store.fs_store import FsStore
from runtime import scheduler
from fabric import client, transport, config as fcfg
from nodes import constant, llm

NT = {"constant": constant, "llm": llm}
STORE = "/tmp/company-e3-int-store"
ok = True

# No hardcoded default brain on the fabric (cognition-is-role-resolved; no-silent-fallback) — a live test
# MUST resolve a real model explicitly. Prefer COMPANY_BRAIN; else the documented clone-model default.
TEST_MODEL = fcfg.DEFAULT_BRAIN or os.environ.get("COMPANY_BRAIN") or "kimi-k2.7-code:cloud"


def check(label, cond):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


def ollama_up() -> bool:
    try:
        urllib.request.urlopen(fcfg.OLLAMA_DIRECT.replace("/v1", "") + "/v1/models", timeout=4)
        return True
    except Exception:
        return False


class Answer(BaseModel):
    capital: str


def main():
    if not ollama_up():
        print("  [FAIL] ollama service not reachable — cannot run the live E3 acceptance")
        return 1

    t = transport.openai_transport()   # defaults to ollama /v1

    # 1: guarded structured call against the real cloud brain — validates or fails loud
    ans = client.complete(
        t, [{"role": "user", "content": 'Return ONLY JSON: {"capital": "<capital of France>"}'}],
        model=TEST_MODEL, schema=Answer, json=True)
    check("live structured call -> validated schema (capital=Paris)",
          isinstance(ans, Answer) and "paris" in ans.capital.lower())

    # 2: the AI NODE runs end-to-end through the scheduler (constant prompt -> llm -> text)
    shutil.rmtree(STORE, ignore_errors=True); store = FsStore(STORE)
    g = Graph(id="ai", nodes=[
        NodeInstance(id="p", type="constant",
                     config={"value": "In one word, the opposite of 'up'?"}),
        NodeInstance(id="m", type="llm", config={"model": TEST_MODEL}),
    ], edges=[Edge(from_node="p", from_port="value", to_node="m", to_port="prompt")])
    r = scheduler.run(g, store, NT)
    output = store.get_content(store.head("run://ai/m")) if store.head("run://ai/m") else None
    check("AI node ran via scheduler; non-empty model output",
          "m" in r["ran"] and isinstance(output, str) and output.strip() != "")
    print(f"      (model said: {str(output)[:80]!r})")

    # 3: memo — re-run does NOT re-hit the model (cached)
    r2 = scheduler.run(g, store, NT)
    check("memo: re-run reuses the cached model call (no re-hit)",
          "m" in r2["skipped"] and "m" not in r2["ran"])

    print("\n" + ("✅ E3 INTEGRATION PASSED — live model call, guarded + memoised"
                  if ok else "❌ E3 INTEGRATION FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
