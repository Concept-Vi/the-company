"""tests/circuit_confirm_release_acceptance.py — C5.5: a CONFIRM gate is released ONLY by the operator's
resolve — the executor's lane never writes the resolved field (the WRITE-PATH test).

THE BAR (COMPLETION-CRITERIA §L5 C5.5): a CONFIRM-class action from an agent principal raises + surfaces
to the inbox; the operator's resolve (and ONLY that) releases it; the executor's lane never writes the
resolved field. (CIRCUIT.md §4: "two-lane safe — executor writes claim/heartbeat/terminal; only the
operator's channel writes takes/resolves.")

By USE, on a temp-root store + the ONE inbox (runtime/governance.Inbox — reuse-never-fork):
  1 · guard('external', …) from a delegated agent (ceiling L2) RAISES GovernanceError AND surfaces an
      item with resolved=None (the live escalation).
  2 · the executor's lane CANNOT release: circuit.release() refuses while resolved is None; the
      executor-reachable write (Inbox.set_status — the lifecycle lane) advances status WITHOUT touching
      resolved (verified field-for-field); release STILL refuses after it.
  3 · only Inbox.resolve (the operator channel — kept OFF the MCP face) writes resolved; after it,
      release returns the item and the guarded action runs confirmed.
  4 · the write-path SPLIT is also proven structurally: set_status refuses to write 'approve' (an unknown
      lifecycle status), and the source of the executor lane (set_status) contains no resolved-write.
  5 · LIVE posture (runtime/access.py may() — the ONE effective-access decision): the agent principal's
      'approve' verb on a real container is DENIED while the operator's is ALLOWED — the two lanes are
      two different answers from the same function.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("COMPANY_TEST_RUN", "1")

from store.fs_store import FsStore                                    # noqa: E402
from runtime.governance import guard, Inbox, GovernanceError          # noqa: E402
from runtime.circuit import release, CircuitError                     # noqa: E402

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


store = FsStore(os.path.join(tempfile.mkdtemp(prefix="confirm-"), "store"))
inbox = Inbox(store)
ran = {"n": 0}


def do():
    ran["n"] += 1
    return "effect"


# ── 1 · the CONFIRM raise + surface (an agent principal under a delegation ceiling) ─────────────────
try:
    guard("external", do, inbox=inbox,
          payload={"who": "agent://executor", "what": "send the thing outward"}, ceiling="L2")
    raise AssertionError("FAIL: CONFIRM-class action from an agent did not raise")
except GovernanceError as e:
    check(f"CONFIRM-class ('external', LOCKED) from an agent principal RAISES [{str(e)[:60]}…]", True)
check("…and the action did NOT run (raise means refuse, not warn)", ran["n"] == 0)
items = [d for d in inbox.list() if d.get("action") == "external"]
check("…and it SURFACED to the ONE inbox with resolved=None (a live escalation)",
      len(items) == 1 and items[0]["resolved"] is None and items[0]["default"] == "reject")
SID = items[0]["id"]

# ── 2 · the executor's lane cannot release ───────────────────────────────────────────────────────────
try:
    release(inbox, SID)
    raise AssertionError("FAIL: release with resolved=None did not refuse")
except CircuitError as e:
    check(f"circuit.release refuses while unresolved [{str(e)[:60]}…]",
          "only the operator's resolve releases" in str(e))
inbox.set_status(SID, "presented")                      # the executor-reachable lifecycle write
d = inbox.get(SID)
check("the executor's lifecycle write (set_status) advanced status WITHOUT touching resolved "
      "(the two-lane split, field-for-field)", d["status"] == "presented" and d["resolved"] is None)
try:
    release(inbox, SID)
    raise AssertionError("FAIL: release after set_status did not refuse")
except CircuitError:
    check("release STILL refuses after the lifecycle write — status is not a release", True)
try:
    inbox.set_status(SID, "approve")
    raise AssertionError("FAIL: set_status accepted 'approve'")
except ValueError:
    check("set_status REFUSES 'approve' (not a lifecycle status) — the executor lane has no spelling "
          "of a release at all", True)
import inspect                                          # noqa: E402
src_status = inspect.getsource(Inbox.set_status)
src_resolve = inspect.getsource(Inbox.resolve)
check("WRITE-PATH, structurally: Inbox.set_status's source contains NO assignment to d['resolved'] — "
      "the resolve write exists only in Inbox.resolve (the operator channel)",
      'd["resolved"] =' not in src_status and 'd["resolved"] =' in src_resolve)

# ── 3 · only the operator's resolve releases ─────────────────────────────────────────────────────────
inbox.resolve(SID, "approve", reason="operator's eyes on it — approved")
d = inbox.get(SID)
check("Inbox.resolve (the operator channel) wrote resolved='approve' + the reason",
      d["resolved"] == "approve" and d["reason"].startswith("operator"))
got = release(inbox, SID)
check("circuit.release now RETURNS the item — the gate is open (read, never written, by the executor)",
      got["id"] == SID)
out = guard("external", do, confirmed=inbox.is_approved(SID), inbox=inbox)
check("the guarded action now RUNS, confirmed by the inbox's resolve (authorization READ from the "
      "inbox, never a caller flag invented)", out == "effect" and ran["n"] == 1)

# ── 4 · reject path: a rejected resolve NEVER releases ──────────────────────────────────────────────
sid2 = inbox.surface("external", {"who": "agent://executor", "what": "second ask"}, default="reject")
inbox.resolve(sid2, "reject", reason="not this one")
try:
    release(inbox, sid2)
    raise AssertionError("FAIL: release of a REJECTED item did not refuse")
except CircuitError:
    check("release of a REJECTED item refuses (resolve='reject' is a real answer, not a release)", True)

# ── 5 · LIVE posture: the ONE access decision splits the two lanes ──────────────────────────────────
from runtime.access import may                          # noqa: E402
agent = may("agent://vi", "approve", "project://company")
oper = may("operator://tim", "approve", "project://company")
check("may(agent://vi, 'approve', project://company) → DENY "
      f"[{agent['reason'][:60]}…] — the executor lane holds no approve verb", agent["allow"] is False)
check("may(operator://tim, 'approve', project://company) → ALLOW — identity IS the boundary",
      oper["allow"] is True and oper["via"] == "operator")

print(f"\nPASS ({PASS} checks) — C5.5: CONFIRM raises + surfaces; only the operator's resolve releases; "
      "the executor's lane has no write-path to `resolved` (behavioral + structural + live-posture proof).")
