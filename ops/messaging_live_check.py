"""ops/messaging_live_check.py — the OPERATOR-GATED live verification of the unified messaging layer.

An autonomous agent may NOT auto-launch interactive channel sessions (the documented autonomy
boundary), so the brief's "verify by use" tail — inject to a hand-started session, survive a handle
churn, fail loud on the unreachable — is staged HERE as one deliberate command for Tim. It exercises
the REAL runtime (runtime.identity + runtime.router) against live .data + the live supervisor; the
only side effect is the probe message it injects into a session YOU launched for the test.

──────────────────────────── RUNBOOK ────────────────────────────
1. Launch a throwaway hand-started channel session (a normal interactive session, in ~/company so its
   UUID is captured):
       cd ~/company && claude --mcp-config channels/channel.mcp.json \
            --dangerously-load-development-channels server:company-channel
   In it, announce a recognisable description:  (call the `announce` tool)  "LIVE-CHECK TARGET".
2. See who is reachable and by which transport:
       .venv/bin/python ops/messaging_live_check.py --list
   Find your target's row; note its handle AND its uuid.
3. Send it a live probe and read the receipt (it should say delivered via transport=channel):
       .venv/bin/python ops/messaging_live_check.py --to <handle-or-uuid>
   → the probe appears LIVE in the target session's conversation; the receipt prints delivered=True.
4. CHURN test: fully quit + relaunch that session (its handle changes). Then address it by its DURABLE
   uuid — it must still land:
       .venv/bin/python ops/messaging_live_check.py --to <uuid>
   (If --list now shows uuid empty for it, that is the open capture gap for non-~/company cwds.)
5. FAIL-LOUD test: address a nonexistent target — it must fail loud, not phantom-OK:
       .venv/bin/python ops/messaging_live_check.py --to session://does-not-exist
──────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime import identity, router     # noqa: E402


def cmd_list() -> None:
    fleet = identity.presence_all()
    rows = [{k: r.get(k) for k in ("state", "transports", "handle", "uuid", "as_id", "cwd",
                                   "reachable", "uuid_how")} for r in fleet]
    print(json.dumps({"live_fleet": len(fleet), "rows": rows}, indent=2))
    print("\nTip: a row with transports=['channel'] is a hand-started session reachable via its .mjs "
          "port; ['supervised'] is supervisor-owned. Address --to by uuid to survive a handle churn.")


def cmd_send(to: str, message: str) -> int:
    receipt = router.route(to, message, frm="ops.messaging_live_check")
    print(json.dumps(receipt, indent=2))
    if receipt.get("delivered"):
        print(f"\n✓ delivered LIVE via transport={receipt.get('transport')} — check the target's conversation.")
        return 0
    if receipt.get("queued"):
        print(f"\n• not live; QUEUED to the durable mailbox ({receipt.get('reason')}).")
        return 0
    print(f"\n✗ UNREACHABLE (failed loud, no phantom-OK): {receipt.get('reason')}")
    return 3


def main() -> None:
    ap = argparse.ArgumentParser(description="Operator-gated live check of the unified messaging layer.")
    ap.add_argument("--list", action="store_true", help="print the live fleet + reachable transports")
    ap.add_argument("--to", default="", help="target: handle | uuid | as-id | agent-id | cwd | session://X")
    ap.add_argument("--message", default="", help="probe text (default names a live-check + timestamp-free nonce)")
    args = ap.parse_args()
    if args.list or not args.to:
        cmd_list()
        if not args.to:
            return
    msg = args.message or "LIVE-CHECK from the unified messaging layer — if you see this injected live, " \
                          "reply 'LIVE-CHECK OK'. (ops/messaging_live_check.py)"
    sys.exit(cmd_send(args.to, msg))


if __name__ == "__main__":
    main()
