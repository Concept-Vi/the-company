"""tests/fabric_board_cqrs_acceptance.py — P6: the board CQRS split + the since-cursor.

PROVES: `board`/`board_act` are THIN doors over the unchanged runtime (delegation faithful, BoardError
→ {ok:false}); the read door gains the `since` cursor (oldest-first past an ISO stamp, next_since,
pagination never skips); reads refuse writes and vice versa (CQRS teaching both ways); annotations tell
the truth per door; NEITHER door carries a posture tag (cc_board is operator-tier — the split must not
silently widen the public boundary); the original cc_board tool still registers untouched.

Exit 0 = PASS · 1 = FAIL.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from runtime import cc_board as cb                 # noqa: E402
from mcp_face.tools import board as b_mod          # noqa: E402
from mcp_face.tools import cc_board as old_mod     # noqa: E402

FAIL = []


def check(name, cond):
    print(("  ok  " if cond else "  XX  ") + name)
    if not cond:
        FAIL.append(name)


class _StubMCP:
    def __init__(self):
        self.tools = {}
        self.annotations = {}

    def tool(self, annotations=None):
        def deco(fn):
            self.tools[fn.__name__] = fn
            self.annotations[fn.__name__] = annotations
            return fn
        return deco


class _FakeSuite:
    def emit_run_record(self, ev, n, **fields):
        pass


def main():
    rows = [
        {"id": "a", "updated": "2026-07-10T00:00:00", "state": "open"},
        {"id": "b", "updated": "2026-07-11T00:00:00", "state": "open"},
        {"id": "c", "updated": "2026-07-12T00:00:00", "state": "open"},
    ]
    calls = {}
    cb.list_items = lambda **kw: (calls.__setitem__("list", kw), list(rows))[1]
    cb.get_item = lambda i: {"id": i}
    cb.file_item = lambda *a, **k: (calls.__setitem__("file", (a, k)), {"id": "new", "address": "board://new"})[1]
    cb.transition = lambda item, to_state, **k: {"id": item, "state": to_state}
    cb.comment = lambda target, body, author, **k: {"id": "cmt", "on": target}
    err = cb.BoardError

    mcp = _StubMCP()
    b_mod.register(mcp, _FakeSuite())
    board, board_act = mcp.tools["board"], mcp.tools["board_act"]

    # delegation + filters pass through
    r = board(op="list", type="request", state="open")
    check("list delegates with filters", r["total"] == 3
          and calls["list"]["type"] == "request" and calls["list"]["state"] == "open")

    # the since cursor: oldest-first past the stamp, next_since, pagination never skips
    r2 = board(op="list", since="2026-07-10T00:00:00", limit=1)
    check("since filters + oldest-first + limit", [i["id"] for i in r2["items"]] == ["b"])
    check("next_since = last returned stamp", r2["next_since"] == "2026-07-11T00:00:00")
    r3 = board(op="list", since=r2["next_since"])
    check("cursor pagination never skips", [i["id"] for i in r3["items"]] == ["c"])
    r4 = board(op="list", since=r3["next_since"])
    check("caught-up: empty + cursor stable", r4["items"] == [] and r4["next_since"] == r3["next_since"])

    # CQRS teaching both ways
    try:
        board(op="file", type="note", title="x", author_session="s")
        check("read door refuses a write op", False)
    except (ValueError, TypeError):
        check("read door refuses a write op", True)
    try:
        board_act(op="list")
        check("write door refuses a read op", False)
    except (ValueError, TypeError):
        check("write door refuses a read op", True)

    # write delegation + defaults
    r5 = board_act(op="file", type="note", title="t", author_session="session://me")
    check("file delegates (source default claude_code)",
          r5["item"]["id"] == "new" and calls["file"][1].get("source") == "claude_code")
    r6 = board_act(op="comment", target="image://ch/x.png", body="nice", author_session="session://me")
    check("comment annotates ANY address (image:// too)", r6["item"]["on"] == "image://ch/x.png")

    # BoardError → {ok:false}
    def _boom(i):
        raise err("no such item")
    cb.get_item = _boom
    r7 = board(op="get", item="ghost")
    check("BoardError surfaced as ok:false", r7.get("ok") is False and "no such item" in r7["error"])

    # honest annotations + exposure preserved
    def _posture(a):
        return getattr(a, "posture", None) or (getattr(a, "model_extra", None) or {}).get("posture")
    ar, aw = mcp.annotations["board"], mcp.annotations["board_act"]
    check("read door readOnlyHint=True", getattr(ar, "readOnlyHint", None) is True)
    check("write door readOnlyHint=False", getattr(aw, "readOnlyHint", None) is False)
    check("NEITHER door widens the public boundary (no posture tag)",
          _posture(ar) is None and _posture(aw) is None)

    # the original cc_board still registers untouched
    mcp2 = _StubMCP()
    old_mod.register(mcp2, _FakeSuite())
    check("cc_board (back-compat) still registers", "cc_board" in mcp2.tools)

    if FAIL:
        print(f"\nFAIL — {len(FAIL)} failed")
        sys.exit(1)
    print("\nfabric_board_cqrs_acceptance: PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
