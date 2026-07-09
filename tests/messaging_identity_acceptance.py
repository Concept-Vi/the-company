"""tests/messaging_identity_acceptance.py — the identity resolver's ladder + self-healing capture (L1/L5).

Deterministic (the process-start/transcript rung is monkeypatched — the LIVE proof of that rung is
ops/messaging_live_check.py). PROVES:
  - recover_uuid ladder order: reg.session_id → reg.transcript_path → (deep) proc-starttime match; the
    deep rung fires ONLY with deep=True.
  - _strip_scheme resolves session://X, clone://sid/at, agent://slug, and a bare id (R5).
  - reconcile_registry backfills a CONFIDENT recovery into the reg (with provenance), SKIPS an
    unrecoverable one (no wrong guess), and never touches a reg that already has a session_id.

Exit 0 = PASS · 1 = FAIL.
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from runtime import identity      # noqa: E402
from runtime import cc_channels as cc  # noqa: E402

FAIL = []


def check(name, cond):
    print(("  ok  " if cond else "  XX  ") + name)
    if not cond:
        FAIL.append(name)


def main():
    # deterministic leaf rungs (no live /proc, no markers)
    identity._uuid_from_environ = lambda cp: None
    identity._uuid_from_fd = lambda cp: None
    identity._uuid_from_starttime = lambda reg, tolerance=10.0: ("uuid-A" if reg.get("claude_pid") == 111 else None)
    identity.session_scan.SELF_MARKER_DIR = tempfile.mkdtemp(prefix="mu-nomarker-")  # empty → marker misses

    # ── recover_uuid ladder ──
    check("rung1 reg.session_id", identity.recover_uuid({"session_id": "sid-1"}) == ("sid-1", "reg.session_id"))
    check("rung2 reg.transcript_path",
          identity.recover_uuid({"transcript_path": "/x/abc-uuid.jsonl"}) == ("abc-uuid", "reg.transcript_path"))
    check("deep rung6 proc-starttime match (deep=True)",
          identity.recover_uuid({"claude_pid": 111}, deep=True) == ("uuid-A", "proc-starttime-match"))
    check("deep rung does NOT fire without deep=True",
          identity.recover_uuid({"claude_pid": 111}, deep=False) == (None, "unrecovered"))
    check("unrecoverable stays unrecovered (no guess)",
          identity.recover_uuid({"claude_pid": 222}, deep=True) == (None, "unrecovered"))

    # ── _strip_scheme (R5) ──
    check("strip session://", identity._strip_scheme("session://u-1") == "u-1")
    check("strip clone://sid/at -> sid", identity._strip_scheme("clone://src-9/compact:2") == "src-9")
    check("strip agent://slug", identity._strip_scheme("agent://ledger-session-fable") == "ledger-session-fable")
    check("bare id passes through", identity._strip_scheme("ch-h8xvlf6i") == "ch-h8xvlf6i")

    # ── reconcile_registry ──
    d = tempfile.mkdtemp(prefix="mu-reconcile-")
    json.dump({"handle": "ch-A", "session_id": "", "claude_pid": 111}, open(os.path.join(d, "ch-A.json"), "w"))
    json.dump({"handle": "ch-B", "session_id": "", "claude_pid": 222}, open(os.path.join(d, "ch-B.json"), "w"))
    json.dump({"handle": "ch-C", "session_id": "already-1"}, open(os.path.join(d, "ch-C.json"), "w"))
    rep = identity.reconcile_registry(chan_dir=d)
    check("reconcile scanned only the empty regs (2)", rep["scanned"] == 2)
    check("reconcile backfilled the confident one (ch-A)",
          [b["uuid"] for b in rep["backfilled"]] == ["uuid-A"])
    check("reconcile skipped the unrecoverable one (ch-B)", rep["skipped"] == 1)
    a = json.load(open(os.path.join(d, "ch-A.json")))
    check("ch-A reg now carries session_id", a.get("session_id") == "uuid-A")
    check("ch-A backfill stamps provenance", a.get("session_id_recovered_by") == "proc-starttime-match")
    b = json.load(open(os.path.join(d, "ch-B.json")))
    check("ch-B stays empty (never guessed)", (b.get("session_id") or "") == "")
    c = json.load(open(os.path.join(d, "ch-C.json")))
    check("ch-C (already had id) untouched", c.get("session_id") == "already-1" and "session_id_recovered_by" not in c)

    if FAIL:
        print(f"\nFAIL — {len(FAIL)} failed")
        sys.exit(1)
    print("\nmessaging_identity_acceptance: PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
