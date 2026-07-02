"""tests/circuit_takes_acceptance.py — C5.4: the approval-retract window is BOUNDED BY THE CLAIM.

THE BAR (COMPLETION-CRITERIA §L5 C5.4): an approval take-mark is retractable BEFORE an intent_claim
references it, and REFUSED after — both cases demonstrated. (CIRCUIT.md §4: "Consequences: retractable
until an intent_claim references the take; the audit trail IS the data.")

By USE, on a temp-root store: a decision_take lands on a proposal:// address (the ONE approval vocabulary
— mark_types/decision_take, the approvals table's successor); retract = the registered decision_retract
(append-only, audit-preserving — never a delete); the moment a claim carries `references_take` naming the
proposal, the window CLOSES (execution started on the approval's strength — un-approving would orphan a
running effect). The state fold is decision_registry.compose_state — the SAME fold the decision surface
uses (reuse-never-fork).
"""
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("COMPANY_TEST_RUN", "1")

from store.fs_store import FsStore                                    # noqa: E402
from runtime.circuit import (take_on_proposal, retract_take, claims_referencing,  # noqa: E402
                             claim_intent, CircuitError)
from runtime.decision_registry import compose_state as decision_fold  # noqa: E402

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


store = FsStore(os.path.join(tempfile.mkdtemp(prefix="takes-"), "store"))
T0 = datetime(2026, 7, 2, 12, 0, 0, tzinfo=timezone.utc)
ROW = {"id": "acc", "meaning": "acceptance proposal", "options": [{"label": "approve"}]}

# ── 1 · RETRACTABLE BEFORE a claim references it ─────────────────────────────────────────────────────
P1 = "proposal://global/acc-retractable"
take_on_proposal(store, P1, value="approve", by="operator://tim")
s = decision_fold(ROW, store.marks_for(P1))
check("a take on the proposal address folds to DECIDED (the ONE decision fold — reuse, not a fork)",
      s["state"] == "decided" and s["decided_value"] == "approve" and s["decided_by"] == "operator://tim")
check("no claim references it yet (the window is open)", claims_referencing(store, P1) == [])
retract_take(store, P1, by="operator://tim", note="changed my mind before anything ran")
s = decision_fold(ROW, store.marks_for(P1))
check("retract BEFORE any claim → allowed; the fold returns to PENDING (append-only un-decide)",
      s["state"] == "pending")
check("the audit trail IS the data: take AND retract both still on the thread (nothing deleted)",
      [m["mark_type"] for m in store.marks_for(P1)] == ["decision_take", "decision_retract"])

# ── 2 · REFUSED AFTER a claim references it ──────────────────────────────────────────────────────────
P2 = "proposal://global/acc-frozen"
I2 = "intent://global/acc-approved-run"
take_on_proposal(store, P2, value="approve", by="operator://tim")
claim_intent(store, I2, by="agent://executor", session="session://s9/step/1",
             lease_until=(T0 + timedelta(hours=1)).isoformat(), now=T0,
             references_take=P2)                      # execution claims ON the approval's strength
check("the claim's references_take is found (the freeze set)",
      [c.get("target") for c in claims_referencing(store, P2)] == [I2])
try:
    retract_take(store, P2, by="operator://tim", note="too late")
    raise AssertionError("FAIL: retract after a referencing claim did NOT refuse")
except CircuitError as e:
    check("retract AFTER a referencing claim → REFUSED, naming the claiming intent "
          f"[{str(e)[:70]}…]", I2 in str(e) and "window closed" in str(e))
s = decision_fold(ROW, store.marks_for(P2))
check("the refused retract wrote NOTHING — the take still folds DECIDED",
      s["state"] == "decided"
      and [m["mark_type"] for m in store.marks_for(P2)] == ["decision_take"])

# ── 3 · grammar edges ────────────────────────────────────────────────────────────────────────────────
try:
    retract_take(store, "proposal://global/acc-nothing", by="operator://tim")
    raise AssertionError("FAIL: retract with no take did not refuse")
except CircuitError as e:
    check("retract with NO take to retract → fail-loud (never a silent no-op)", "nothing to retract" in str(e))
try:
    take_on_proposal(store, "board://item-1", by="operator://tim")
    raise AssertionError("FAIL: take on a non-proposal address did not refuse")
except CircuitError:
    check("a take on a non-proposal:// address refuses (the approval grammar lives on proposal addresses)", True)
try:
    take_on_proposal(store, P1, by="")
    raise AssertionError("FAIL: unattributed take did not refuse")
except CircuitError:
    check("an unattributed take (`by` empty) refuses — exactly the audit hole the circuit closes", True)

print(f"\nPASS ({PASS} checks) — C5.4: the take's retract window is open until an intent_claim "
      "references it, closed after; both demonstrated; audit-preserving throughout.")
