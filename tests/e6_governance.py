"""E6 — the act-unwatched policy + surfaced-decision inbox (S7/D4/D7). Deterministic.

Run: .venv/bin/python tests/e6_governance.py
"""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime import governance as gov
from store.fs_store import FsStore

ok = True


def check(label, cond):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


def main():
    # posture per class
    check("AUTO for cheap/reversible/internal (run, inspect, configure)",
          gov.posture("run") == gov.AUTO and gov.posture("inspect") == gov.AUTO)
    check("CONFIRM for code_build / destructive / external",
          all(gov.posture(c) == gov.CONFIRM for c in ("code_build", "destructive", "external")))
    check("unknown class defaults to CONFIRM (safest)", gov.posture("???") == gov.CONFIRM)
    check("source_data + external are locked-to-confirm forever", gov.LOCKED == {"source_data", "external"})

    store = FsStore(tempfile.mkdtemp())
    inbox = gov.Inbox(store)

    # AUTO runs immediately
    check("guard AUTO runs", gov.guard("run", lambda: "did", inbox=inbox) == "did")

    # CONFIRM without confirmation -> raises + surfaces; with confirmation -> runs
    raised = False
    try:
        gov.guard("code_build", lambda: "wrote", inbox=inbox, payload={"x": 1})
    except gov.GovernanceError:
        raised = True
    check("guard CONFIRM without confirmation fails loud + surfaces",
          raised and len(inbox.list()) == 1 and inbox.list()[0]["resolved"] is None)
    check("guard CONFIRM with confirmation runs",
          gov.guard("code_build", lambda: "wrote", confirmed=True, inbox=inbox) == "wrote")

    # inbox resolve
    sid = inbox.list()[0]["id"]
    inbox.resolve(sid, "approved")
    check("inbox decision resolvable", store.get_surfaced(sid)["resolved"] == "approved")

    print("\n" + ("✅ E6 GOVERNANCE PASSED" if ok else "❌ E6 FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
