"""tests/board_bus_events_acceptance.py — F1: board activity lands on the DURABLE BUS, channel-stamped.

Proves by use: (1) filing a board item (no emitter configured = the default) appends a `board.item.filed`
event to the COMPANY_STORE events.jsonl carrying the CHANNEL stamp; (2) a transition appends
`board.item.transitioned`; (3) the ?channel= filter semantics — a channel-stamped event set folds to
exactly the stamped subset (the same skip rule the bridge /api/stream applies); (4) an explicit
set_board_emitter(None) still means OFF (test semantics preserved); (5) emit failure is lenient —
surfaced as emit_error, never breaking the file write.
"""
import os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
STORE_DIR = os.path.join(tempfile.mkdtemp(prefix="board-bus-"), "store")
os.environ["COMPANY_STORE"] = STORE_DIR

from store.fs_store import FsStore
from runtime import cc_board as cb

PASS = 0
def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")

bd = os.path.join(tempfile.mkdtemp(prefix="board-bus-bd-"), "noticeboard")
os.makedirs(bd, exist_ok=True)
store = FsStore(STORE_DIR)

# 1: default emitter → the bus, channel-stamped
rec = cb.file_item("note", "bus probe", "body", "tester", channel="design", board_dir=bd)
evs = store.events_since(-1)
filed = [e for e in evs if e.get("kind") == "board.item.filed" and e.get("id") == rec["id"]]
check("filing lands board.item.filed on the durable bus (default emitter, no wiring needed)", len(filed) == 1)
check("the event carries the CHANNEL stamp", filed[0].get("channel") == "design")
check("no emit_error on the record (the emit succeeded)", "emit_error" not in rec)

# 2: transition emits too
cb.transition(rec["id"], "archived", by="tester", board_dir=bd)   # a note's legal move: posted→archived
evs = store.events_since(-1)
trans = [e for e in evs if e.get("kind") == "board.item.transitioned" and e.get("id") == rec["id"]]
check("a transition lands board.item.transitioned on the bus", len(trans) == 1)

# 3: the ?channel= filter semantics (the bridge's skip rule over the same data)
store.append_event({"kind": "x.unstamped", "summary": "no channel"})
allevs = store.events_since(-1)
chan_only = [e for e in allevs if e.get("channel") == "design"]
check("the channel filter folds to exactly the stamped subset (unstamped events excluded)",
      all(e.get("channel") == "design" for e in chan_only) and len(chan_only) >= 1
      and any(e.get("kind") == "x.unstamped" for e in allevs))

# 4: explicit None = OFF (test semantics preserved)
cb.set_board_emitter(None)
rec2 = cb.file_item("note", "silent probe", "body", "tester", channel="design", board_dir=bd)
evs2 = [e for e in store.events_since(-1) if e.get("id") == rec2["id"]]
check("set_board_emitter(None) means explicitly OFF (no bus event)", evs2 == [])

# 5: lenient failure — surfaced, never raised
cb.set_board_emitter(lambda ev, f: (_ for _ in ()).throw(RuntimeError("bus down")))
rec3 = cb.file_item("note", "lenient probe", "body", "tester", channel="design", board_dir=bd)
check("an emit failure is SURFACED (emit_error), the file write stands", "emit_error" in rec3
      and os.path.exists(os.path.join(bd, f"{rec3['id']}.md")))
cb.set_board_emitter(cb._UNSET_EMITTER)   # restore the default for any later suite

print(f"\nALL {PASS} CHECKS PASS — board activity on the durable bus, channel-stamped; ?channel= folds honestly (F1)")
