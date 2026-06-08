"""tests/dispose_policy_acceptance.py — C4: findings are agent-disposable; by-design ESCALATES.

The disposition lane is already SEPARATE from the operator inbox (dispositions.jsonl, not the surfaced
queue — AREA-1: the inbox is operator-only + already-drowned, so findings must NOT flood it). C4 adds the
one consent rule on top: most dispositions (to_wire/to_build_ui/defer/voice_owned/backend_only/resolved) are
AGENT-disposable (the loop burns them down) — but `by-design` (permanently ACCEPTING a gap as fine) is a
consequential operator decision, so it ESCALATES through the consent floor (an agent cannot self-accept a
gap). dispose_finding enforces exactly that, by use.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime import coherence_detect as cd

PASS = 0
def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")

root = os.path.join(tempfile.mkdtemp(prefix="dispose-"), "store")
store = FsStore(root)
store.append_finding({"kind": "unwired-route", "address": "/api/x", "source": "structural"})

# agent-disposable: the loop sets a finish/defer disposition directly
r1 = cd.dispose_finding(store, "unwired-route", "/api/x", "to_wire", by="loop", reason="needs FE caller")
check("agent CAN set an agent-disposable disposition (to_wire)", r1["ok"] and r1["applied"])
check("it persisted", store.disposition_for("unwired-route", "/api/x")["disposition"] == "to_wire")

r2 = cd.dispose_finding(store, "unwired-route", "/api/x", "resolved", by="loop")
check("agent CAN set resolved (the detector confirmed it closed)", r2["ok"] and r2["applied"])

# by-design ESCALATES: an agent canNOT self-accept a gap — it surfaces for the operator, not applied
r3 = cd.dispose_finding(store, "unwired-route", "/api/x", "by-design", by="loop", reason="looks internal")
check("agent canNOT self-set by-design (escalates — not applied)", r3["ok"] and not r3["applied"] and r3["escalated"])
check("the by-design did NOT persist (operator-only floor held)",
      store.disposition_for("unwired-route", "/api/x")["disposition"] == "resolved")

# by-design WITH operator confirmation applies (the consent gate satisfied)
r4 = cd.dispose_finding(store, "unwired-route", "/api/x", "by-design", by="tim", reason="internal entry point", confirmed=True)
check("by-design WITH operator confirmation applies", r4["ok"] and r4["applied"])
check("now it persisted (operator accepted the gap — the micro-ADR)",
      store.disposition_for("unwired-route", "/api/x")["disposition"] == "by-design")

# an unknown disposition is refused fail-loud (no silent bad state)
r5 = cd.dispose_finding(store, "unwired-route", "/api/x", "bogus", by="loop")
check("an unknown disposition is refused (fail-loud, not applied)", not r5["ok"] and not r5["applied"])

print(f"\nALL {PASS} CHECKS PASS — findings are agent-disposable in their own lane; by-design escalates "
      f"through the consent floor (operator-only); unknown dispositions fail loud.")
