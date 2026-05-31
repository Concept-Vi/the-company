"""E3 — the fabric's reliability guards + VRAM semaphore (transport-agnostic).

TDD, written before fabric/ exists. The guards are the fabric.py lessons made into
real, tested logic — independent of LiteLLM/ollama (a fake transport is INJECTED, so
this is dependency injection, not mocking-the-thing-under-test). The live LiteLLM →
ollama-cloud transport + a real call are a separate integration smoke test.

Guards proven here:
  - empty content -> retry, then FAIL LOUD (never return empty silently)  [kimi/glm lesson]
  - valid JSON matching schema -> validated object
  - truncated JSON -> bracket-repaired -> validated
  - schema mismatch -> FAIL LOUD
  - plain text (no schema) -> returned
  - VRAM semaphore -> bounds concurrent LOCAL calls (16 GB card can't OOM)

Run: .venv/bin/python tests/e3_fabric.py
"""
import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic import BaseModel
from fabric import client, vram

ok = True


def check(label, cond):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


def transport_of(*responses):
    """A fake transport: returns/raises the queued responses in order."""
    it = iter(responses)

    def t(model, messages, **opts):
        r = next(it)
        if isinstance(r, BaseException):
            raise r
        return r
    return t


class Person(BaseModel):
    name: str


def main():
    no_sleep = lambda s: None

    # plain text, no schema
    check("plain text returned",
          client.complete(transport_of("hello there"), [], model="m") == "hello there")

    # empty -> retry -> valid
    check("empty then valid: retries past empty",
          client.complete(transport_of("", "  ", "recovered"), [], model="m", sleep=no_sleep) == "recovered")

    # all empty -> FAIL LOUD
    try:
        client.complete(transport_of("", "", "", ""), [], model="m", retries=3, sleep=no_sleep)
        check("all-empty raises (fail loud)", False)
    except client.FabricError:
        check("all-empty raises (fail loud)", True)

    # valid JSON + schema
    p = client.complete(transport_of('{"name": "vi"}'), [], model="m", schema=Person)
    check("schema: valid JSON -> validated object", isinstance(p, Person) and p.name == "vi")

    # truncated JSON -> repaired -> validated
    p2 = client.complete(transport_of('{"name": "vi"'), [], model="m", schema=Person, sleep=no_sleep)
    check("schema: truncated JSON bracket-repaired -> validated", isinstance(p2, Person) and p2.name == "vi")

    # schema mismatch -> FAIL LOUD
    try:
        client.complete(transport_of('{"wrong": 1}', '{"wrong": 1}', '{"wrong": 1}'),
                        [], model="m", schema=Person, retries=3, sleep=no_sleep)
        check("schema mismatch raises (fail loud)", False)
    except client.FabricError:
        check("schema mismatch raises (fail loud)", True)

    # VRAM semaphore bounds concurrent LOCAL calls
    sem = vram.VramGate(limit=1)
    live, peak, lock = 0, 0, threading.Lock()

    def local_call():
        nonlocal live, peak
        with sem.slot():
            with lock:
                live += 1; peak = max(peak, live)
            time.sleep(0.05)
            with lock:
                live -= 1

    threads = [threading.Thread(target=local_call) for _ in range(4)]
    [t.start() for t in threads]; [t.join() for t in threads]
    check("VRAM semaphore bounds concurrency (limit=1 -> peak 1)", peak == 1)

    print("\n" + ("✅ E3 FABRIC GUARDS PASSED" if ok else "❌ RED (fabric not built yet)"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
