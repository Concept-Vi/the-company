"""tests/fabric_mention_routing_acceptance.py — FL2: mentions ride the unified router (loudness held).

PROVES (tmp board dir + tmp COMPANY_STORE; router mocked per scenario — the router's own ladder is
proven in its own suites):
  · a LIVE member mention → delivered:true with the true transport, board-thread preserved.
  · a QUEUED member (durable mailbox rung) → outcome {queued:true, transport:'queue'} on the comment —
    the durable leg mentions never had — AND the sender-side loudness still fires (bus event +
    delivery_warning) because queued ≠ live-delivered, with the note telling the truth per class.
  · an UNREACHABLE target → {delivered:false, queued:false, error} recorded; loudness names it
    unreachable (recorded-on-comment-only).
  · the router is called with deep=False (the hot-path guard) and the store (queue rung enabled).

Exit 0 = PASS · 1 = FAIL.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

os.environ["COMPANY_STORE"] = tempfile.mkdtemp(prefix="fl2-store-")

from runtime import cc_board as cb        # noqa: E402
from runtime import router as rt          # noqa: E402
from store.fs_store import FsStore        # noqa: E402

FAIL = []


def check(name, cond):
    print(("  ok  " if cond else "  XX  ") + name)
    if not cond:
        FAIL.append(name)


def main():
    bd = tempfile.mkdtemp(prefix="fl2-board-")
    calls = []

    def fake_route(target, content, *, frm="fabric", thread=None, base=None, registry=None,
                   store=None, dry_run=False, deep=True):
        calls.append({"target": target, "thread": thread, "deep": deep, "store": store,
                      "content": content})
        if target == "ch-live":
            return {"delivered": True, "queued": False, "transport": "channel", "verb": "inject"}
        if target == "ch-queued":
            return {"delivered": False, "queued": True, "transport": "queue", "verb": "queue"}
        return {"delivered": False, "queued": False, "transport": "none", "verb": "unreachable",
                "reason": "unresolved: not a live session and not a known durable id"}

    rt.route = fake_route

    rec = cb.comment("board://item-x", "ping @ch-live @ch-queued @ch-ghost99", "session://author",
                     board_dir=bd)
    m = {o["handle"]: o for o in rec.get("mentions", [])}

    check("live member delivered with true transport",
          m["ch-live"]["delivered"] is True and m["ch-live"]["transport"] == "channel")
    check("queued member carries the durable leg (queued:true, transport=queue)",
          m["ch-queued"]["delivered"] is False and m["ch-queued"]["queued"] is True
          and m["ch-queued"]["transport"] == "queue")
    check("unreachable recorded loud with reason",
          m["ch-ghost99"]["delivered"] is False and m["ch-ghost99"]["queued"] is False
          and "unresolved" in m["ch-ghost99"].get("error", ""))
    check("router called deep=False (hot-path guard)", all(c["deep"] is False for c in calls))
    check("router given the store (queue rung enabled)", all(c["store"] is not None for c in calls))
    check("board thread preserved (board-<id>)", all(c["thread"] == f"board-{rec['id']}" for c in calls))
    check("mention body format preserved (reply_to_mention teaching present)",
          all("Reply must land ON THE BOARD" in c["content"] for c in calls))

    # sender-side loudness: preserved + truthful per class
    check("delivery_warning present and names BOTH classes",
          "ch-queued" in rec.get("delivery_warning", "") and "ch-ghost99" in rec.get("delivery_warning", "")
          and "NOT LIVE-DELIVERED" in rec.get("delivery_warning", ""))
    store = FsStore(os.environ["COMPANY_STORE"])
    evs = [e for e in store.events_since(-1) if e.get("kind") == "board.mention.undelivered"]
    check("bus event fired for the not-live-delivered", len(evs) == 1)
    check("event splits queued vs unreachable truthfully",
          evs and evs[0].get("queued") == ["ch-queued"] and evs[0].get("unreachable") == ["ch-ghost99"])

    # persisted on the comment record (F3 open frontmatter)
    back = cb.get_item(rec["id"], board_dir=bd)
    check("outcomes persist on the comment record",
          {o["handle"] for o in back.get("mentions", [])} == {"ch-live", "ch-queued", "ch-ghost99"})

    if FAIL:
        print(f"\nFAIL — {len(FAIL)} failed")
        sys.exit(1)
    print("\nfabric_mention_routing_acceptance: PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
