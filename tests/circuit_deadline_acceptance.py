"""tests/circuit_deadline_acceptance.py — C5.6: deadline behavior — SURFACE proceeds-by-default with a
recorded note; CONFIRM escalates.

THE BAR (COMPLETION-CRITERIA §L5 C5.6): a SURFACE-class proposal past its deadline proceeds-by-default
with a recorded note; a CONFIRM-class one escalates — both demonstrated with short test deadlines.
(CIRCUIT.md §4: "SURFACE-class → default=proceed at deadline; CONFIRM-class → default=reject, escalate.")

By USE, on a temp-root store + the ONE inbox: items carry a `deadline` (top-level or in payload);
circuit.sweep_deadlines(store, now) applies the law —
  · SURFACE ('promote') past deadline → resolved='proceed' + a RECORDED deadline_note (the one sanctioned
    non-operator resolve: the DECLARED default acting at its declared deadline — nothing new was decided);
  · CONFIRM ('external', LOCKED) past deadline → NEVER touches resolved (C5.5's write-path law holds even
    at the deadline); stamps escalated=True + deadline_note + status='presented' (in the operator's face);
    circuit.release STILL refuses; only the operator's resolve ever releases it;
  · not-yet-due untouched · already-resolved untouched · the sweep is idempotent (a second pass skips).
"""
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("COMPANY_TEST_RUN", "1")

from store.fs_store import FsStore                                    # noqa: E402
from runtime.governance import Inbox, posture, SURFACE, CONFIRM       # noqa: E402
from runtime.circuit import sweep_deadlines, release, CircuitError    # noqa: E402

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


store = FsStore(os.path.join(tempfile.mkdtemp(prefix="deadline-"), "store"))
inbox = Inbox(store)
T0 = datetime(2026, 7, 2, 12, 0, 0, tzinfo=timezone.utc)
SHORT = timedelta(seconds=30)                            # the short test deadline

check("posture sanity: 'promote' is SURFACE, 'external' is CONFIRM (the declared policy rows)",
      posture("promote") == SURFACE and posture("external") == CONFIRM)

# ── the four items: SURFACE-due · CONFIRM-due · not-yet-due · already-resolved ──────────────────────
sid_s = inbox.surface("promote", {"what": "promote the draft", "deadline": (T0 + SHORT).isoformat()},
                      default="proceed", resolved=None)
sid_c = inbox.surface("external", {"what": "send it outward", "deadline": (T0 + SHORT).isoformat()},
                      default="reject", resolved=None)
sid_f = inbox.surface("promote", {"what": "later one", "deadline": (T0 + timedelta(days=1)).isoformat()},
                      default="proceed", resolved=None)
sid_r = inbox.surface("external", {"what": "already answered", "deadline": (T0 + SHORT).isoformat()},
                      default="reject", resolved=None)
inbox.resolve(sid_r, "reject", reason="operator said no before the deadline")

# ── the sweep, one tick past the short deadline ──────────────────────────────────────────────────────
out = sweep_deadlines(store, now=T0 + SHORT + timedelta(seconds=1))
check("sweep saw all 4 deadline-carrying items", out["checked"] == 4)

d = inbox.get(sid_s)
check("SURFACE past deadline → PROCEEDS by the declared default (resolved='proceed')",
      sid_s in out["proceeded"] and d["resolved"] == "proceed")
check("…WITH the note RECORDED on the item (why it proceeded, when, by what law)",
      "proceeded by the DECLARED default" in d.get("deadline_note", "")
      and "SURFACE-class" in d["deadline_note"])

d = inbox.get(sid_c)
check("CONFIRM past deadline → ESCALATES (escalated=True, presented to the operator)",
      sid_c in out["escalated"] and d.get("escalated") is True and d["status"] == "presented")
check("…and resolved is STILL None — the deadline never releases a CONFIRM gate (C5.5 holds at the "
      "deadline too)", d["resolved"] is None)
check("…the escalation note is recorded (legible why)", "ESCALATED to the operator" in d["deadline_note"])
try:
    release(inbox, sid_c)
    raise AssertionError("FAIL: an escalated CONFIRM item released without the operator")
except CircuitError:
    check("release of the escalated item still refuses — only the operator resolves it", True)
inbox.resolve(sid_c, "approve", reason="operator caught the escalation")
check("…until the operator's resolve — then it releases", release(inbox, sid_c)["id"] == sid_c)

d = inbox.get(sid_f)
check("a NOT-YET-DUE deadline is untouched (no resolve, no note)",
      d["resolved"] is None and "deadline_note" not in d)
d = inbox.get(sid_r)
check("an item RESOLVED before its deadline is untouched by the sweep (the answer stands)",
      d["resolved"] == "reject" and "deadline_note" not in d and sid_r not in out["escalated"])

# ── idempotency: the second sweep changes nothing ───────────────────────────────────────────────────
out2 = sweep_deadlines(store, now=T0 + SHORT + timedelta(minutes=5))
check("the sweep is IDEMPOTENT: a second pass proceeds/escalates NOTHING new (noted items skipped)",
      out2["proceeded"] == [] and out2["escalated"] == [])

print(f"\nPASS ({PASS} checks) — C5.6: past-deadline SURFACE proceeds-by-default with a recorded note; "
      "CONFIRM escalates and only the operator releases; not-due/resolved untouched; sweep idempotent.")
