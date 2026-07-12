"""tests/fabric_reads_acceptance.py — the two Phase-2 read doors (design v2): directory + mailbox.

PROVES BY USE (isolated tmp store + tmp reg dir; never ~/company/.data):
  DIRECTORY — one faceted who/what-exists: registry rows ENRICHED with live presence (not duplicated);
    live-only rows the registry doesn't know appear; CLONES appear as kind=clone actors carrying their
    provenance address but NO filesystem paths (the hidden-fleet fix, posture-safe fields only);
    summarizers excluded by default; channels facet keeps the ROOM row shape; posture="safe" tagged.
  MAILBOX — the fabric inbox: durable mail FIFO past `since` with a client-held cursor + resolved
    bodies; channel_mail joined across ALL the session's handles (churn-spanning) with its own cursor;
    allocations FEDERATED fail-soft (invalid agent_id refused without querying; substrate down → an
    honest unreachable note, local mail unaffected) and READ-ONLY.

Exit 0 = PASS · 1 = FAIL.
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore            # noqa: E402
from runtime import cc_channels as cc         # noqa: E402
from runtime import identity                  # noqa: E402
from runtime import cc_clone                  # noqa: E402
from mcp_face.tools import directory as dir_mod   # noqa: E402
from mcp_face.tools import mailbox as mb_mod      # noqa: E402

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
    def __init__(self, store):
        self.store = store

    def list_agent_sessions(self, state=None, cwd=None, q=None, since=-1, limit=200,
                            include_summarizers=True):
        rows = [
            {"id": "u-reg-1", "name": "alpha", "state": "closed", "title": "did a thing",
             "cwd": "/w1", "last_activity": "2026-07-12T01:00:00", "summarizer": False},
            {"id": "u-live-1", "name": None, "state": "closed", "title": "went live later",
             "cwd": "/w2", "last_activity": "2026-07-12T02:00:00", "summarizer": False},
            {"id": "u-summ-1", "name": None, "state": "closed", "title": "Caveat: the messages…",
             "cwd": "/w3", "last_activity": "2026-07-12T03:00:00", "summarizer": True},
        ]
        if not include_summarizers:
            rows = [r for r in rows if not r["summarizer"]]
        if q:
            rows = [r for r in rows if q in (r.get("title") or "") or q in (r.get("id") or "")]
        return {"sessions": rows[:limit], "total": len(rows), "fold_errors": 0}


def main():
    tmp = tempfile.mkdtemp(prefix="fabric-reads-")
    store = FsStore(os.path.join(tmp, "store"))
    suite = _FakeSuite(store)

    # isolated transport-leaf state
    chan_dir = os.path.join(tmp, "channels")
    os.makedirs(chan_dir, exist_ok=True)
    cc.CHAN_DIR = chan_dir
    cc.MAIL_LOG = os.path.join(chan_dir, "_mail.jsonl")

    # live presence: one row enriching a registry session, one live-only (uuid-less)
    identity.presence_all = lambda base=None, deep=False: [
        {"uuid": "u-live-1", "handle": "ch-live1", "state": "unsupervised-live",
         "transports": ["channel"], "reachable": True, "cwd": "/w2", "description": "the live one"},
        {"uuid": None, "handle": "ch-anon", "state": "unsupervised-live",
         "transports": ["channel"], "reachable": True, "cwd": "/w9", "description": "anonymous live"},
    ]
    # the clone fleet: one clone (with fs paths that must NOT surface)
    cc_clone.list_clones = lambda prune=True: [
        {"handle": "clone-ab12", "session_id": "u-clone-1", "source_sid": "u-reg-1",
         "at": "compact:2", "cwd": "/w1", "description": "past self",
         "address": "clone://u-reg-1/compact:2",
         "materialized_path": "/SECRET/path.jsonl", "source_path": "/SECRET/src.jsonl"}]

    mcp = _StubMCP()
    dir_mod.register(mcp, suite)
    mb_mod.register(mcp, suite)
    directory, mailbox = mcp.tools["directory"], mcp.tools["mailbox"]

    # ── DIRECTORY: principals ──
    res = directory(facet="principals")
    rows = {r["uuid"] or r["handle"]: r for r in res["principals"]}
    check("registry row present", "u-reg-1" in rows)
    check("summarizer EXCLUDED by default", "u-summ-1" not in rows)
    check("live presence ENRICHES the registry row (no duplicate)",
          rows.get("u-live-1", {}).get("handle") == "ch-live1"
          and rows["u-live-1"]["transports"] == ["channel"] and rows["u-live-1"]["reachable"])
    check("live-only (anonymous) row appears", "ch-anon" in rows)
    clone_row = rows.get("u-clone-1")
    check("clone appears as kind=clone actor", clone_row and clone_row["kind"] == "clone")
    check("clone carries provenance address", clone_row and clone_row["address"] == "clone://u-reg-1/compact:2")
    check("clone filesystem paths NOT exposed",
          clone_row and "materialized_path" not in clone_row and "source_path" not in clone_row)
    check("posture=safe tagged", getattr(mcp.annotations["directory"], "posture", None) == "safe"
          or (getattr(mcp.annotations["directory"], "model_extra", None) or {}).get("posture") == "safe")
    res_summ = directory(facet="principals", include_summarizers=True)
    check("include_summarizers=True restores them",
          any(r["uuid"] == "u-summ-1" for r in res_summ["principals"]))

    # ── DIRECTORY: channels facet (room shape, own fold) ──
    from runtime import session_channels as sc
    sc.create_channel(store, name="room one", members=["m1", "m2"], registry=None)
    resc = directory(facet="channels")
    check("channels facet lists the room", resc["total"] == 1
          and resc["channels"][0]["name"] == "room one")
    check("room row is a ROOM shape (member_count, mode) not an actor",
          resc["channels"][0]["member_count"] == 2 and "transports" not in resc["channels"][0])

    # ── MAILBOX: durable mail with client-held cursor ──
    sid = "u-live-1"
    for i, txt in enumerate(("first", "second", "third")):
        cas = store.put_content(txt)
        store.append_agent_mail({"to": f"session://{sid}", "from": "session://sender", "verb": "queue",
                                 "cas": cas, "delivered": i == 0, "transport": "channel" if i == 0 else None})
    r1 = mailbox(session=f"session://{sid}", limit=2)
    check("mail FIFO oldest-first, bodies resolved",
          [m["message"] for m in r1["mail"]["rows"]] == ["first", "second"])
    check("delivered:true audit copy visible", r1["mail"]["rows"][0]["delivered"] is True)
    r2 = mailbox(session=sid, since=r1["mail"]["next_since"])
    check("cursor pagination never skips", [m["message"] for m in r2["mail"]["rows"]] == ["third"])
    check("re-reading the same cursor is safe (client-held)",
          [m["message"] for m in mailbox(session=sid, since=r1["mail"]["next_since"])["mail"]["rows"]] == ["third"])

    # ── MAILBOX: channel_mail across churned handles ──
    for h in ("ch-old1", "ch-new1"):
        json.dump({"handle": h, "session_id": sid, "cwd": "/w2", "pid": 1, "claude_pid": 1, "port": 1},
                  open(os.path.join(chan_dir, f"{h}.json"), "w"))
    with open(cc.MAIL_LOG, "w") as f:
        for to, txt in (("ch-old1", "to old handle"), ("ch-other", "not mine"), ("ch-new1", "to new handle")):
            f.write(json.dumps({"kind": "message", "frm": "ch-x", "to": to, "text": txt}) + "\n")
    r3 = mailbox(session=sid)
    check("channel_mail joins ALL the session's handles (churn-spanning)",
          [m["text"] for m in r3["channel_mail"]["rows"]] == ["to old handle", "to new handle"])
    check("channel_mail cursor advances", r3["channel_mail"]["next_chan_since"] == 2)
    r4 = mailbox(session=sid, chan_since=r3["channel_mail"]["next_chan_since"])
    check("channel cursor pagination", r4["channel_mail"]["rows"] == [])

    # ── MAILBOX: federated allocations, fail-soft + read-only ──
    bad = mb_mod._allocations_readonly("bad id with spaces")
    check("invalid agent_id REFUSED without querying", "invalid agent_id" in bad.get("unreachable", ""))
    import subprocess as _sp
    orig_run = _sp.run
    _sp.run = lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError("no docker"))
    try:
        down = mb_mod._allocations_readonly("ledger-session-fable")
        check("substrate down → honest unreachable, no exception",
              "unreachable" in down and "local mail above is unaffected" in down["unreachable"])
    finally:
        _sp.run = orig_run
    r5 = mailbox(session=sid)
    check("no agent_id → allocations None (not queried)", r5["allocations"] is None)
    check("mailbox posture=safe tagged", getattr(mcp.annotations["mailbox"], "posture", None) == "safe"
          or (getattr(mcp.annotations["mailbox"], "model_extra", None) or {}).get("posture") == "safe")

    if FAIL:
        print(f"\nFAIL — {len(FAIL)} failed")
        sys.exit(1)
    print("\nfabric_reads_acceptance: PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
