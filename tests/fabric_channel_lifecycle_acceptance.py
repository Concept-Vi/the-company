"""tests/fabric_channel_lifecycle_acceptance.py — P5: retire folded into channel_act + the archive gate.

PROVES BY USE (tmp store; board/attachment writers mocked — no real noticeboard writes):
  · channel_act(archive) on a channel with UN-harvested members REFUSES with the coverage ledger
    (the bypass the review flagged — closed at the TOOL layer; the runtime archive_channel is
    UNCHANGED, so its 108-check suite + every programmatic caller keep their contract).
  · force=True archives anyway (explicit, on the caller's head).
  · complete coverage archives without force.
  · channel_act(retire) = the cc_retire discipline as a lifecycle verb: coverage check + corpus
    record + linked board record; archive only via force (explicit, never a side effect);
    from_session required (provenance).

Exit 0 = PASS · 1 = FAIL.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore            # noqa: E402
from runtime import session_channels as sc    # noqa: E402
from runtime import cc_retire as cr           # noqa: E402
from mcp_face.tools import channels as ch_mod  # noqa: E402

FAIL = []


def check(name, cond):
    print(("  ok  " if cond else "  XX  ") + name)
    if not cond:
        FAIL.append(name)


class _StubMCP:
    def __init__(self):
        self.tools = {}

    def tool(self, annotations=None):
        def deco(fn):
            self.tools[fn.__name__] = fn
            return fn
        return deco


class _FakeSuite:
    def __init__(self, store):
        self.store = store

    def get_agent_session(self, sid):
        raise ValueError(f"unknown session {sid}")


def main():
    tmp = tempfile.mkdtemp(prefix="fabric-lifecycle-")
    store = FsStore(os.path.join(tmp, "store"))

    # hermetic cc_retire collaborators: no real harvest files, no real board/attachments writes
    cr._harvest_files = lambda: []
    cr._board.reverse_traverse = lambda addr, kind: []
    cr._board.file_item = lambda *a, **k: {"address": "board://item-fake", "id": "item-fake"}
    cr._board.list_items = lambda **k: []
    cr._att.manifest = lambda channel: {"attachments": {}}

    ch1 = sc.create_channel(store, name="unharvested room", members=["m1", "m2"], registry=None)
    ch2 = sc.create_channel(store, name="covered room", members=["m3"], registry=None)

    mcp = _StubMCP()
    ch_mod.register(mcp, _FakeSuite(store))
    channel_act = mcp.tools["channel_act"]

    # ── the archive GATE ──
    try:
        channel_act(action="archive", channel=ch1["id"])
        check("archive with un-harvested members REFUSES", False)
    except ValueError as e:
        check("archive with un-harvested members REFUSES", "NO harvest" in str(e))
        check("the refusal TEACHES retire + force", "retire" in str(e) and "force=True" in str(e))
        check("the refusal names the missing members", "m1" in str(e) and "m2" in str(e))
    check("the channel is still ACTIVE after the refusal",
          sc.get_channel(store, ch1["id"])["status"] == "active")

    r = channel_act(action="archive", channel=ch1["id"], force=True)
    check("force=True archives anyway (explicit)", r["status"] == "archived")

    # complete coverage → no force needed
    cr._harvest_files = lambda: ["m3-harvest.md"]
    r2 = channel_act(action="archive", channel=ch2["id"])
    check("complete coverage archives WITHOUT force", r2["status"] == "archived")

    # ── retire as a lifecycle verb ──
    cr._harvest_files = lambda: []
    ch3 = sc.create_channel(store, name="to retire", members=["m9"], registry=None)
    try:
        channel_act(action="retire", channel=ch3["id"])
        check("retire without from_session raises teaching", False)
    except ValueError as e:
        check("retire without from_session raises teaching", "from_session" in str(e))

    r3 = channel_act(action="retire", channel=ch3["id"], from_session="session://me",
                     message="what this room learned")
    check("retire writes the corpus record", str(r3.get("corpus", "")).startswith("cas://")
          or r3.get("corpus"))
    check("retire files the linked board record", r3.get("board") == "board://item-fake")
    check("retire surfaces the coverage gap honestly",
          r3["coverage"]["complete"] is False and r3["coverage"]["missing"] == ["m9"])
    check("retire does NOT archive as a side effect", r3["archived"] is False
          and sc.get_channel(store, ch3["id"])["status"] == "active")

    r4 = channel_act(action="retire", channel=ch3["id"], from_session="session://me", force=True)
    check("retire + force archives (explicit opt-in)", r4["archived"] is True
          and sc.get_channel(store, ch3["id"])["status"] == "archived")

    check("ACTIONS export includes retire (drift-teeth stay true)", "retire" in ch_mod.ACTIONS)

    if FAIL:
        print(f"\nFAIL — {len(FAIL)} failed")
        sys.exit(1)
    print("\nfabric_channel_lifecycle_acceptance: PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
