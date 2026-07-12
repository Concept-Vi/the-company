"""tests/receipt_contract_acceptance.py — the RECEIPT SHAPE as a RENDERING CONTRACT (lead↔fabric,
thread lead-fabric-collab, 2026-07-13).

The operator app renders per-target delivery states to Tim as UI chips CONSUMING THESE SHAPES VERBATIM
(delivered/queued/transport). This test freezes them as drift-teeth under the ADDITIVE-ONLY LAW:
new keys may be added; the keys below are never renamed, removed, or re-typed. Breaking a chip is a
contract change — negotiated on the board first, this file edited in the same reviewed commit.

THE THREE SHAPES:
  1. router receipt (send→session; every entry of send→group results[]):
     {target, resolved_uuid, handle, as_id, delivered: bool, queued: bool,
      transport: 'channel'|'supervised'|'queue'|'none', verb, state, reason} (+ recorded when a store
      was in play; + kind:'session' through the send tool).
  2. channel-fan entry (send→channel / channel_act(post) fan[]):
     {session, verb, transport, delivered, mail_seq}.
  3. mention outcome (board comments, persists on the record):
     {handle, delivered, queued, transport} (+ error when unreachable).

Exit 0 = PASS · 1 = FAIL.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

FAIL = []


def check(name, cond, detail=""):
    print(("  ok  " if cond else "  XX  ") + name + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAIL.append(name)


def main():
    from runtime import identity, router

    # ── 1. the router receipt (all four rungs produce the same frozen key-set) ──
    RECEIPT_KEYS = {"target", "resolved_uuid", "handle", "as_id", "delivered", "queued",
                    "transport", "verb", "state", "reason"}
    live_row = {"uuid": "u-1", "handle": "ch-x", "as_id": None, "agent_id": None, "cwd": "/t",
                "description": "", "model": "", "kind": "agent", "state": "unsupervised-live",
                "transports": ["channel"], "reachable": True, "port": 1, "pid": 1, "claude_pid": 1,
                "forked_from": None, "reg": {"handle": "ch-x", "port": 1}, "sources": []}

    class Store:
        def put_content(self, c): return "cas://x"
        def append_agent_mail(self, rec): return {"seq": 1, **rec}

    identity.resolve = lambda t, **kw: dict(live_row) if t == "u-1" else None
    import runtime.cc_channels as cc
    cc.push = lambda reg, content, meta=None: {"ok": True, "transport": "channel"}

    r_live = router.route("u-1", "x", store=Store())
    check("live receipt carries every contract key", RECEIPT_KEYS <= set(r_live),
          f"missing: {RECEIPT_KEYS - set(r_live)}")
    check("live receipt types honest", r_live["delivered"] is True and r_live["queued"] is False
          and r_live["transport"] == "channel" and r_live.get("recorded") is True)

    identity.resolve = lambda t, **kw: {**live_row, "transports": [], "reachable": False} if t == "u-1" else None
    r_q = router.route("u-1", "x", store=Store())
    check("queued receipt carries every contract key", RECEIPT_KEYS <= set(r_q))
    check("queued receipt types honest", r_q["queued"] is True and r_q["transport"] == "queue")

    identity.resolve = lambda t, **kw: None
    r_un = router.route("ghost", "x", store=Store())
    check("unreachable receipt carries every contract key", RECEIPT_KEYS <= set(r_un))
    check("unreachable is loud (transport none, verb unreachable, reason non-empty)",
          r_un["transport"] == "none" and r_un["verb"] == "unreachable" and r_un["reason"])

    # ── 2. the channel-fan entry ──
    FAN_KEYS = {"session", "verb", "transport", "delivered", "mail_seq"}
    import tempfile
    from store.fs_store import FsStore
    from runtime import session_channels as sc
    identity.cc.live_sessions = lambda: []
    s = FsStore(tempfile.mkdtemp(prefix="rc-"))
    ch = sc.create_channel(s, name="rc", members=["mA", "mB"], registry=None)
    fan = sc.post_to_channel(s, ch["id"], "x", "session://me", registry=None)["fan"]
    check("fan entries carry every contract key", all(FAN_KEYS <= set(f) for f in fan),
          f"first entry keys: {sorted(fan[0]) if fan else 'EMPTY'}")

    # ── 3. the mention outcome ──
    MENTION_KEYS = {"handle", "delivered", "queued", "transport"}
    from runtime import cc_board as cb
    from runtime import router as rt
    rt.route = lambda *a, **kw: {"delivered": False, "queued": True, "transport": "queue", "verb": "queue"}
    rec = cb.comment("board://item-y", "hi @ch-someone", "session://me",
                     board_dir=tempfile.mkdtemp(prefix="rc-b-"))
    m = rec.get("mentions", [])
    check("mention outcomes carry every contract key", m and MENTION_KEYS <= set(m[0]),
          f"got: {sorted(m[0]) if m else 'EMPTY'}")

    if FAIL:
        print(f"\nFAIL — {len(FAIL)} failed")
        sys.exit(1)
    print("\nreceipt_contract_acceptance: PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
