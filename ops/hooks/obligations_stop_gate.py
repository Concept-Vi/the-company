#!/usr/bin/env python3
"""ops/hooks/obligations_stop_gate.py — the STOP-BOUNDARY obligation gate (Tim, 2026-07-13).

Live injection is the default for reaching a member; THIS covers the actively-working case: when a
session finishes a turn (the Stop hook), it is told how many typed messages are outstanding — and the
stop is BLOCKED ONCE with the list, so the agent replies before going idle. stop_hook_active guards the
loop (a second stop passes through — never an infinite block). Fail-soft on every error.
"""
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
os.environ.setdefault("COMPANY_STORE", os.path.join(REPO, ".data", "store"))

try:
    payload = json.load(sys.stdin)
except Exception:  # noqa: BLE001
    payload = {}

try:
    if payload.get("stop_hook_active"):        # we already blocked once this stop — let it through
        sys.exit(0)
    from runtime.session_scan import resolve_self_member
    me = resolve_self_member()
    if not me or not me.get("handle"):
        sys.exit(0)
    from runtime import cc_board as cb
    pend = cb.pending_obligations(me["handle"])
    if not pend:
        sys.exit(0)
    ids = [f"{p['id']} (owe: {p.get('_obligation','reply')}, from {p.get('author_session','?')})" for p in pend[:5]]
    print(json.dumps({"decision": "block",
                      "reason": (f"You have {len(pend)} unmet typed message(s) on the company board — "
                                 f"reply BEFORE stopping (obligations are enforced): {ids}. Reply with "
                                 f"cc_board.reply_to_mention('text'"
                                 + (", comment_addr='<ID>'" if len(pend) > 1 else "") + ").")}))
except Exception:  # noqa: BLE001 — a hook must never break the session
    pass
sys.exit(0)
