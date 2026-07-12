#!/usr/bin/env python3
"""ops/hooks/pending_mentions_nag.py — the FORCED-REPLY half of the board mention loop (Tim, 2026-06-29:
"use hooks and context resolution to force a reply for typed messages").

A UserPromptSubmit hook: on every prompt in a ~/company session, resolve SELF (the fabric registration,
via the claude-ancestor PID) → fold the board for PENDING mentions (mentions of me with no reply BY me)
→ if any, INJECT them into the session's context (stdout of a UserPromptSubmit hook is added as context).
Push (cc.send at mention time) is best-effort; THIS is the guarantee: a typed mention re-surfaces in the
mentioned session's context on every turn until its reply lands on the board — it cannot silently rot.

Fail-soft ALWAYS (exit 0, no output on any error): a hook must never break a session. An unregistered
session (self doesn't resolve) simply gets no nag — registration is the membership bar (cc_channels.
register_self). Speed: one board scan; skipped entirely when self doesn't resolve.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
os.environ.setdefault("COMPANY_STORE", os.path.join(REPO, ".data", "store"))

try:
    from runtime.session_scan import resolve_self_member
    me = resolve_self_member()
    if not me or not me.get("handle"):
        sys.exit(0)                                   # not a registered member — no nag, no error
    from runtime import cc_board as cb
    pend = cb.pending_obligations(me["handle"])
    if not pend:
        sys.exit(0)
    multi = len(pend) > 1
    lines = [f"<board-obligations pending={len(pend)} for=\"{me['handle']}\">",
             "You have unmet TYPED messages on the company board — each carries an obligation "
             "(reply/verdict/ack) that must land ON THE BOARD, not only in this chat. Reply with:",
             ("  cd ~/company && .venv/bin/python -c \"import sys;sys.path.insert(0,'.');"
              "from runtime.cc_board import reply_to_mention;"
              "print(reply_to_mention('YOUR REPLY'" + (", comment_addr='<ID>'" if multi else "") + ")['address'])\""),
             ("  (several are open — you MUST pass the ID of the one you're answering)" if multi else ""),
             ""]
    for p in pend[:5]:
        frm = p.get("author_session", "?")
        ob = p.get("_obligation", "reply")
        tgt = next((l.get("target") for l in (p.get("links") or []) if l.get("kind") == "commented_on"), "")
        body = (p.get("body") or "").strip().replace("\n", " ")[:240]
        lines.append(f"- ID {p['id']} · owe: {ob} · from {frm} · on {tgt}: {body}")
    if len(pend) > 5:
        lines.append(f"- … and {len(pend)-5} more (cc_board.pending_obligations)")
    lines.append("</board-obligations>")
    print("\n".join([l for l in lines if l != ""] if not multi else lines))
except Exception:  # noqa: BLE001 — fail-soft: a hook must never break the session
    pass
sys.exit(0)
