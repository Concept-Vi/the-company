"""tests/fabric_retry_acceptance.py — the model layer is robust to ollama-cloud's high-variance latency.

ollama-cloud is cheap but high-variance: sometimes very slow, sometimes quick. The dominant failure
was a slow-but-PROGRESSING generation getting KILLED at the old bare `timeout=120` literal and
re-queued into the same slow path. The fix SPLITS two levers (worst-case wall-clock = retries × timeout,
so you don't bump both globally):
  - a longer, CONFIG-DRIVEN TIMEOUT (fabric/config.py: DEFAULT_TIMEOUT / DEFAULT_CLOUD_TIMEOUT) fixes
    the slow-but-succeeding case (the main one);
  - EXPONENTIAL + JITTERED retry backoff (fabric/client._backoff), with NO sleep after the final
    attempt, fixes transient HARD failures (refused/502/empty) — fail-loud contract intact.

Proven here (TDD, headless — no live endpoint needed; transports are INJECTED fakes):
  1. timeout defaults read from CONFIG, not a bare literal (signature default == config constant);
     and an env override is picked up by the transport (proven in a SUBPROCESS so the import-time
     env read is real, not a no-op after-the-fact mutation).
  2. _backoff is exponential + jittered + bounded (per-attempt bounds: 2**i <= s < 2**i + base, capped).
  3. _retry_sleep SKIPS the final-attempt sleep (all-fail with N retries → exactly N-1 sleeps;
     a success on attempt 2 of 4 sleeps only ONCE, not 3×).
  4. a transient transport error retries then SUCCEEDS.
  5. an always-empty response raises FabricError after the BUMPED default retries (4) — fail loud.
  6. embed dim-mismatch raises FabricError via the NODE (embed.run passes dim=) — no silent pass.

Run: ./.venv/bin/python tests/fabric_retry_acceptance.py
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from fabric import client, transport, config as fcfg
from fabric.client import _backoff, _retry_sleep, FabricError

ok = True


def check(label, cond):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


def recording_sleep():
    """A fake sleep that records each delay it is asked to wait (the clock injection)."""
    calls = []
    return calls, (lambda s: calls.append(s))


def transport_of(*responses):
    """A fake transport returning/raising queued responses in order (dependency injection)."""
    it = iter(responses)

    def t(model, messages, **opts):
        r = next(it)
        if isinstance(r, BaseException):
            raise r
        return r
    return t


def embeddings_transport_of(*responses):
    """A fake EMBEDDINGS transport: (model, inputs) -> list[list[float]] (or raises)."""
    it = iter(responses)

    def t(model, inputs):
        r = next(it)
        if isinstance(r, BaseException):
            raise r
        return r
    return t


def main():
    # === 1a. timeout defaults are CONFIG-DRIVEN, not bare literals ===
    import inspect
    sig_chat = inspect.signature(transport.openai_transport).parameters["timeout"].default
    sig_embed = inspect.signature(transport.openai_embeddings_transport).parameters["timeout"].default
    check("openai_transport timeout default == fcfg.DEFAULT_TIMEOUT (not a bare literal)",
          sig_chat == fcfg.DEFAULT_TIMEOUT)
    check("embeddings transport timeout default == fcfg.DEFAULT_TIMEOUT (config-driven, MODERATE — not cloud-inflated)",
          sig_embed == fcfg.DEFAULT_TIMEOUT and fcfg.DEFAULT_TIMEOUT < fcfg.DEFAULT_CLOUD_TIMEOUT)
    check("config split: DEFAULT_TIMEOUT (180) < DEFAULT_CLOUD_TIMEOUT (300)",
          fcfg.DEFAULT_TIMEOUT == 180 and fcfg.DEFAULT_CLOUD_TIMEOUT == 300)

    # === 1b. an ENV OVERRIDE is picked up — in a SUBPROCESS (config reads env at IMPORT time;
    #         mutating os.environ after import would prove nothing). The child sets the env,
    #         imports fresh, and prints the transport's effective default timeout. ===
    child = (
        "import inspect;"
        "from fabric import transport, config as fcfg;"
        "d=inspect.signature(transport.openai_transport).parameters['timeout'].default;"
        "print(f'{fcfg.DEFAULT_TIMEOUT}|{d}')"
    )
    env = dict(os.environ, COMPANY_FABRIC_TIMEOUT="999")
    out = subprocess.run([sys.executable, "-c", child], cwd=ROOT, env=env,
                         capture_output=True, text=True)
    got = (out.stdout.strip().splitlines() or [""])[-1]
    check(f"env override COMPANY_FABRIC_TIMEOUT=999 → config==999 AND transport default==999 (got {got!r})",
          got == "999|999")

    # === 2. _backoff is exponential + jittered + bounded ===
    base, cap = 1.0, 30.0
    backoff_in_bounds = True
    for i in range(6):
        samples = [_backoff(i, base=base, cap=cap) for _ in range(50)]
        expected = min(cap, base * (2 ** i))
        lo, hi = expected, expected + base       # jitter adds [0, base)
        if not all(lo <= s < hi + 1e-9 for s in samples):
            backoff_in_bounds = False
        if len(set(samples)) <= 1:               # jitter must actually vary the value
            backoff_in_bounds = False
    check("_backoff is exponential (2**i), jittered (varies within [exp, exp+base)), capped at 30",
          backoff_in_bounds)
    check("_backoff grows: backoff(0) region < backoff(3) region (1 vs 8)",
          _backoff(0, base=base) < _backoff(3, base=base))

    # === 3. _retry_sleep SKIPS the final attempt ===
    calls, sleep = recording_sleep()
    for attempt in range(4):                     # retries=4
        _retry_sleep(sleep, attempt, retries=4)
    check("_retry_sleep over 4 attempts sleeps exactly 3× (skips the final attempt)",
          len(calls) == 3)

    # all-empty, retries=4 → exactly 3 sleeps then raise (no useless final-attempt sleep before raising)
    calls2, sleep2 = recording_sleep()
    try:
        client.complete(transport_of("", "", "", ""), [], model="m", retries=4, sleep=sleep2)
        check("all-empty raises after 4 attempts (fail loud)", False)
    except FabricError:
        check("all-empty raises after the BUMPED default retries (fail loud)", True)
    check("all-empty over 4 retries sleeps exactly 3× (no dead final-attempt sleep)",
          len(calls2) == 3)

    # a SUCCESS on attempt 2 of 4 sleeps only ONCE (one failure → one backoff), not 3×
    calls3, sleep3 = recording_sleep()
    res = client.complete(transport_of(RuntimeError("502"), "recovered"), [], model="m",
                          retries=4, sleep=sleep3)
    check("transient transport error retries then SUCCEEDS", res == "recovered")
    check("a success on attempt 2 sleeps exactly ONCE (not 3×)", len(calls3) == 1)

    # the backoff sequence is increasing+jittered, not the old flat 0.5*(attempt+1)
    calls4, sleep4 = recording_sleep()
    try:
        client.complete(transport_of("", "", "", "", ""), [], model="m", retries=5, sleep=sleep4)
    except FabricError:
        pass
    check("recorded backoff sequence is strictly increasing (exponential, not linear-flat)",
          len(calls4) == 4 and all(calls4[i] < calls4[i + 1] for i in range(len(calls4) - 1)))

    # === 4. default retries is now 4 (cloud queues) ===
    no_sleep = lambda s: None
    attempts_seen = {"n": 0}

    def counting_empty(model, messages, **opts):
        attempts_seen["n"] += 1
        return ""
    try:
        client.complete(counting_empty, [], model="m", sleep=no_sleep)   # default retries
    except FabricError:
        pass
    check("complete() default retries == 4 (made 4 attempts before failing loud)",
          attempts_seen["n"] == 4)

    # === 5. embeddings: dim-mismatch raises through complete_embeddings (fail loud) ===
    bad = embeddings_transport_of([[0.0, 0.0]])      # 2-dim, but we will assert dim=1024
    try:
        client.complete_embeddings(bad, ["x"], model="m", dim=1024, retries=2, sleep=no_sleep)
        check("complete_embeddings dim-mismatch raises (fail loud)", False)
    except FabricError:
        check("complete_embeddings dim-mismatch raises (fail loud)", True)

    # === 6. the NODE (embed.run) PASSES dim → a wrong-length vector FAILS LOUD via the node ===
    from nodes import embed
    orig = transport.openai_embeddings_transport
    transport.openai_embeddings_transport = lambda **kw: (lambda model, inputs: [[0.1, 0.2, 0.3]])
    try:
        embed.run({"text": "anything"}, {})          # default dim = DEFAULT_EMBED_DIM (1024) ≠ 3
        check("embed.run with a wrong-length vector FAILS LOUD (node passes dim=)", False)
    except FabricError:
        check("embed.run enforces the dim contract — wrong-length vector raises FabricError", True)
    finally:
        transport.openai_embeddings_transport = orig

    # and a CORRECT-dim vector flows through (the node doesn't over-reject)
    transport.openai_embeddings_transport = lambda **kw: (lambda model, inputs: [[0.5] * fcfg.DEFAULT_EMBED_DIM])
    try:
        v = embed.run({"text": "anything"}, {})
        check("embed.run with a correct-dim vector returns it (no over-rejection)",
              isinstance(v, list) and len(v) == fcfg.DEFAULT_EMBED_DIM)
    finally:
        transport.openai_embeddings_transport = orig

    print("\n" + ("✅ FABRIC RETRY/TIMEOUT ACCEPTANCE PASSED"
                  if ok else "❌ FABRIC RETRY/TIMEOUT ACCEPTANCE FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
