"""tests/board_reply_resolution_acceptance.py — `reply` + pending mentions resolve for everyone (D-wire 2).

Proves by use: (1) pending_mentions folds from the BOARD itself (own/reflect — a mention with no reply by
the mentioned member is pending; delivery failure doesn't matter, the board is the ledger); (2) a reply BY
the mentioned member CLOSES it (drops out of pending); (3) reply_to_mention with an explicit handle files a
threaded reply on the oldest pending mention with no address needed; (4) reply_to_mention names a specific
comment when asked; (5) fail-loud when nothing is pending; (6) a reply by someone ELSE does NOT close it.
Self-resolution (handle=None → the fabric registration) is exercised live in the fabric (needs a claude
ancestor); the explicit-handle path proves the resolution mechanics.
"""
import os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_STORE"] = os.path.join(tempfile.mkdtemp(prefix="board-reply-"), "store")

from runtime import cc_board as cb

PASS = 0
def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")

bd = os.path.join(tempfile.mkdtemp(prefix="board-reply-bd-"), "noticeboard")
os.makedirs(bd, exist_ok=True)

target = cb.file_item("note", "design block", "the block under discussion", "author-a", board_dir=bd)

# two mentions of member-x, oldest first
c1 = cb.comment(target["address"], "hey @member-x thoughts on this?", "author-a", board_dir=bd)
c2 = cb.comment(target["address"], "@member-x also see this second one", "author-b", board_dir=bd)

pend = cb.pending_mentions("member-x", board_dir=bd)
check("both mentions PENDING (folded from the board, delivery-independent)",
      [p["id"] for p in pend] == [c1["id"], c2["id"]])

# a reply by someone ELSE does not close it
cb.reply(c1["address"], "butting in", "author-b", board_dir=bd)
check("a reply by someone ELSE does not close the mention",
      [p["id"] for p in cb.pending_mentions("member-x", board_dir=bd)] == [c1["id"], c2["id"]])

# reply_to_mention resolves the OLDEST pending, no address needed
r = cb.reply_to_mention("here are my thoughts", handle="member-x", board_dir=bd)
check("reply_to_mention filed a threaded reply on the OLDEST pending mention",
      any(l.get("kind") == "reply_to" and l.get("target") == c1["address"] for l in (r.get("links") or [])))
check("the replied mention CLOSED (dropped from pending)",
      [p["id"] for p in cb.pending_mentions("member-x", board_dir=bd)] == [c2["id"]])

# reply to a NAMED comment
r2 = cb.reply_to_mention("answering the second directly", handle="member-x", comment_addr=c2["address"], board_dir=bd)
check("reply_to_mention answers a NAMED comment when asked",
      any(l.get("target") == c2["address"] for l in (r2.get("links") or []) if l.get("kind") == "reply_to"))
check("all pending cleared", cb.pending_mentions("member-x", board_dir=bd) == [])

# fail-loud on nothing pending
try:
    cb.reply_to_mention("nothing to answer", handle="member-x", board_dir=bd)
    check("fail-loud when nothing pending", False)
except cb.BoardError:
    check("fail-loud when nothing pending (BoardError, never a silent no-op)", True)

print(f"\nALL {PASS} CHECKS PASS — pending fold + `reply` resolution close the mention loop on the board (D-wire 2)")
