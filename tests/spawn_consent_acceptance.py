"""tests/spawn_consent_acceptance.py — RT2: spawn open to agents; the consent beat is a TUNABLE default.

Tim's ruling (2026-06-29): agents CAN spawn agents — runaway-safety is a tunable guard (the concurrency
cap), never a wall. Proves the gate logic WITHOUT spawning anything real: (1) default posture — no
consent + no env → the TeachingRefusal (the beat still required); (2) COMPANY_FABRIC_AGENT_CONSENT=1 →
the same call passes the GATE (it then fails later on cmd-building in this test env — we assert the
refusal is GONE, not that a session spawned); (3) explicit operator_consent=True always passes the gate;
(4) the env parser accepts 1/true/yes/on and rejects junk; (5) the concurrency cap stays live + tunable.
"""
import os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime import session_supervisor as sv

PASS = 0
def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")

# 4 — the env parser
os.environ.pop("COMPANY_FABRIC_AGENT_CONSENT", None)
check("default: agent consent OFF", sv.agent_consent_default() is False)
for v in ("1", "true", "YES", "on"):
    os.environ["COMPANY_FABRIC_AGENT_CONSENT"] = v
    check(f"env {v!r} → consent ON", sv.agent_consent_default() is True)
os.environ["COMPANY_FABRIC_AGENT_CONSENT"] = "banana"
check("junk env → OFF (never a silent yes)", sv.agent_consent_default() is False)

sup = sv.SessionSupervisor(FsStore(os.path.join(tempfile.mkdtemp(prefix="rt2-"), "store")))

# 1 — default posture: the consent beat refuses loud
os.environ.pop("COMPANY_FABRIC_AGENT_CONSENT", None)
try:
    sup.spawn_bridge_session(operator_consent=False)
    check("no consent + no env → TeachingRefusal", False)
except sv.TeachingRefusal as e:
    check("no consent + no env → TeachingRefusal (the beat still required by default)",
          "COMPANY_FABRIC_AGENT_CONSENT" in str(e))
except Exception:
    check("no consent + no env → TeachingRefusal (the beat still required by default)", False)

# 2 — the tunable default opens the gate for agents
os.environ["COMPANY_FABRIC_AGENT_CONSENT"] = "1"
try:
    sup.spawn_bridge_session(operator_consent=False)
    gate_passed = True          # (unlikely in a test env, but if it spawns the gate certainly passed)
except sv.TeachingRefusal:
    gate_passed = False         # the gate refused — the tunable did NOT open it
except Exception:
    gate_passed = True          # refusal GONE; failed later (cmd build/registry) — the gate passed
check("COMPANY_FABRIC_AGENT_CONSENT=1 → the consent GATE passes for an agent call", gate_passed)

# 3 — explicit consent always passes the gate (either env posture)
os.environ.pop("COMPANY_FABRIC_AGENT_CONSENT", None)
try:
    sup.spawn_bridge_session(operator_consent=True)
    gate_passed = True
except sv.TeachingRefusal:
    gate_passed = False
except Exception:
    gate_passed = True
check("explicit operator_consent=True always passes the gate", gate_passed)

# 5 — the runaway guard stays live + tunable
os.environ["COMPANY_FABRIC_CONCURRENCY"] = "7"
check("the concurrency cap is live + tunable (the guard, not a wall)", sv.fabric_concurrency() == 7)
os.environ.pop("COMPANY_FABRIC_CONCURRENCY", None)

print(f"\nALL {PASS} CHECKS PASS — spawn open to agents via a tunable consent default; the cap remains the guard (RT2)")
