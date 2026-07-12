"""tests/board_mentions_acceptance.py — @mention on a board comment injects toward the member + is RECORDED.

Proves by use: (1) @handle in a comment body triggers mention routing; (2) the outcome PERSISTS on the
comment record (`mentions` field — rides the opened frontmatter, F3) so undelivered is visible, never
silent; (3) a comment with no live member still FILES fine (the board is the durable half; delivery is
best-effort); (4) no self-ping; (5) the mention regex doesn't false-fire on emails/paths.
Live delivery to a real session is exercised by use in the fabric (cc.send is the proven chat path).
"""
import os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_STORE"] = os.path.join(tempfile.mkdtemp(prefix="board-mentions-"), "store")

from runtime import cc_board as cb

PASS = 0
def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")

bd = os.path.join(tempfile.mkdtemp(prefix="board-mentions-bd-"), "noticeboard")
os.makedirs(bd, exist_ok=True)

target = cb.file_item("note", "mention target", "the thing commented on", "author-a", board_dir=bd)

# 1+2+3: a mention to a NON-live handle → comment files, outcome recorded as delivered:False (loud, not silent)
rec = cb.comment(target["address"], "hey @no-such-member-xyz can you look at this?", "author-a", board_dir=bd)
back = cb.get_item(rec["id"], board_dir=bd)
check("the comment filed despite no live member (board = durable half)", back.get("id") == rec["id"])
m = back.get("mentions") or []
check("the mention outcome PERSISTED on the record", len(m) == 1 and m[0]["handle"] == "no-such-member-xyz")
check("undelivered is RECORDED (delivered False), never silent", m[0]["delivered"] is False)

# 4: no self-ping
rec2 = cb.comment(target["address"], "note to self @author-a remember this", "author-a", board_dir=bd)
back2 = cb.get_item(rec2["id"], board_dir=bd)
check("no self-ping (author mentioning self routes nothing)", not (back2.get("mentions") or []))

# 5: regex hygiene — emails and paths don't false-fire
rec3 = cb.comment(target["address"], "mail info@conceptv.com.au and see ~/company/x @real-handle", "author-b", board_dir=bd)
back3 = cb.get_item(rec3["id"], board_dir=bd)
m3 = back3.get("mentions") or []
check("an email does NOT false-fire; a real @handle does", [x["handle"] for x in m3] == ["real-handle"])

# 6: no mentions → no field
rec4 = cb.comment(target["address"], "plain comment, nothing to route", "author-b", board_dir=bd)
back4 = cb.get_item(rec4["id"], board_dir=bd)
check("a plain comment carries no mentions field", "mentions" not in back4)

# 7: SENDER-SIDE LOUDNESS (the @lead failure class): an undelivered mention EMITS a bus event
#    and the return carries an unmissable delivery_warning — recorded-but-unseen is not loud.
from store.fs_store import FsStore
_store = FsStore(os.environ["COMPANY_STORE"])
evs = [e for e in _store.events_since(-1) if e.get("kind") == "board.mention.undelivered"]
check("an undelivered mention lands board.mention.undelivered on the bus (watchers SEE it)",
      any("no-such-member-xyz" in (e.get("handles") or []) for e in evs))
check("the sender's return carries an explicit delivery_warning",
      "delivery_warning" in rec and "NOT LIVE-DELIVERED" in rec["delivery_warning"])

print(f"\nALL {PASS} CHECKS PASS — board @mentions route toward live members + outcomes persist loud (D-wire 1)")
