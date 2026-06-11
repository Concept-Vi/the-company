"""tests/agent_sessions_mailbox_acceptance.py — Session Fabric §C: the MAILBOX leaf + the MCP face verbs.

PROVES (by execution, on an ISOLATED tmp store — never ~/company/.data; P0.2 scratch discipline):

  A · the store leaf (`agent_sessions/mail.jsonl`, FsStore):
      append-discipline refusals (to/from/verb/cas each required, teaching) · seq monotonic-unique ·
      thread defaults to the mail id · cas bodies round-trip · since/to/verb/thread/limit reads ·
      per-consumer cursor refs (default -1 · advance · idempotent re-ack · REGRESSION REFUSED ·
      corruption fails loud · survives reload).

  B · CROSS-PROCESS seq uniqueness (the append_event landmine, closed for mail by graph_lock):
      REAL concurrent subprocesses (threads would false-pass on the in-process lock — the
      concurrency_acceptance precedent) hammer one store; every line parses, every seq unique,
      count exact. Hard-timeout-wrapped: a deadlock marks BLOCKED (exit 2), never hangs.

  C · the MCP face (mcp_face/tools/sessions.py on a dev FastMCP + a REAL Suite over the tmp store):
      both tools register via the pkgutil contract (register(mcp, suite)) · contracts.ToolAnnotations
      wired honestly through to SDK hints (F10.1 first instance: sessions readOnly, session_post not) ·
      the ROUTER (guide §C pseudocode): auto→deliver/wake/queue by registry state · explicit-verb
      state refusals TEACH (deliver→closed · wake→live · wake→unsupervised) · unknown session refused ·
      copies>cap refused naming COMPANY_FABRIC_CONCURRENCY · copies>1 without consult refused ·
      empty message / missing from_session refused · post→inbox ROUND-TRIP (body text back, FIFO,
      next_since pagination walks without skipping) · consult fan record (copies, one thread) ·
      reply joins the thread · watch returns only agent_sessions.* events with an honest cursor ·
      describe joins registry row + mail summary.

THE FLOOR (asserted structurally): the tools module never imports subprocess/ui_claude_session/
implement — posting writes INTENTS; only the supervisor service acts on them.

Exit 0 = PASS · 1 = FAIL · 2 = BLOCKED (hang/timeout).
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore                       # noqa: E402

FAILURES = []
CHECKS = [0]


def check(name, cond, detail=""):
    CHECKS[0] += 1
    if cond:
        print(f"  ok  {name}")
    else:
        FAILURES.append(name)
        print(f"  FAIL {name} {detail}")


def expect_teaching(name, fn, *needles):
    """The call must raise ValueError whose message TEACHES (carries every needle)."""
    try:
        fn()
    except ValueError as e:
        msg = str(e)
        missing = [n for n in needles if n.lower() not in msg.lower()]
        check(name, not missing, f"teaching error missing {missing!r} in: {msg[:160]}")
        return
    except Exception as e:  # noqa: BLE001
        check(name, False, f"raised {type(e).__name__} not the teaching ValueError: {e}")
        return
    check(name, False, "did not refuse at all")


# ── A · the store leaf ────────────────────────────────────────────────────────────────────────────
def section_a(tmp):
    print("A · store leaf (append discipline · reads · cursors)")
    s = FsStore(tmp)
    for field in ("to", "from", "verb", "cas"):
        rec = {"to": "session://t", "from": "session://me", "verb": "deliver", "cas": "cas://x"}
        rec.pop(field)
        expect_teaching(f"append refuses missing `{field}`",
                        lambda r=rec: s.append_agent_mail(r), field)
    cas = s.put_content("hello fabric")
    m0 = s.append_agent_mail({"to": "session://t1", "from": "session://me", "verb": "deliver", "cas": cas})
    m1 = s.append_agent_mail({"to": "session://t1", "from": "session://me", "verb": "queue",
                              "cas": cas, "thread": m0["thread"]})
    m2 = s.append_agent_mail({"to": "session://t2", "from": "session://me", "verb": "consult",
                              "cas": cas, "copies": 2})
    check("seqs monotonic 0,1,2", [m0["seq"], m1["seq"], m2["seq"]] == [0, 1, 2])
    check("id from seq + thread defaults to id", m0["id"] == "mail-0" and m0["thread"] == "mail-0")
    check("explicit thread honoured", m1["thread"] == "mail-0" and m2["thread"] == "mail-2")
    check("body rides cas round-trip", s.get_content(m0["cas"]) == "hello fabric")
    check("since is strictly-greater", [r["seq"] for r in s.agent_mail_since(0)] == [1, 2])
    check("to-filter", len(s.agent_mail_since(-1, to="session://t1")) == 2)
    check("verb-filter", [r["id"] for r in s.agent_mail_since(-1, verb="consult")] == ["mail-2"])
    check("thread-filter", len(s.agent_mail_since(-1, thread="mail-0")) == 2)
    check("limit keeps FIRST N (FIFO)", [r["seq"] for r in s.agent_mail_since(-1, limit=2)] == [0, 1])
    check("cursor default -1 (fresh consumer)", s.agent_mail_cursor("sup") == -1)
    s.set_agent_mail_cursor("sup", 1)
    check("cursor advance", s.agent_mail_cursor("sup") == 1)
    s.set_agent_mail_cursor("sup", 1)
    check("idempotent re-ack ok", s.agent_mail_cursor("sup") == 1)
    expect_teaching("cursor regression refused", lambda: s.set_agent_mail_cursor("sup", 0),
                    "backward", "since=")
    expect_teaching("empty consumer refused", lambda: s.agent_mail_cursor(" "), "consumer")
    s.set_ref("agent-mail-cursor://junky", "not-an-int")
    expect_teaching("corrupt cursor fails loud", lambda: s.agent_mail_cursor("junky"), "corrupt")
    s2 = FsStore(tmp)
    check("cursor + mail survive reload",
          s2.agent_mail_cursor("sup") == 1 and len(s2.agent_mail_since(-1)) == 3)
    check("leaf lives at agent_sessions/mail.jsonl (naming law)",
          os.path.exists(os.path.join(tmp, "agent_sessions", "mail.jsonl")))


# ── B · cross-process seq uniqueness ─────────────────────────────────────────────────────────────
_CHILD = r"""
import sys
sys.path.insert(0, sys.argv[1])
from store.fs_store import FsStore
s = FsStore(sys.argv[2])
cas = s.put_content("storm")
for i in range(25):
    s.append_agent_mail({"to": "session://storm", "from": "session://w" + sys.argv[3],
                         "verb": "queue", "cas": cas})
"""


def section_b(tmp):
    print("B · cross-process append storm (4 procs × 25 — graph_lock teeth)")
    procs = [subprocess.Popen([sys.executable, "-c", _CHILD, ROOT, tmp, str(i)])
             for i in range(4)]
    blocked = False
    for p in procs:
        try:
            p.wait(timeout=120)                      # hard timeout: a deadlock NEVER hangs the harness
        except subprocess.TimeoutExpired:
            p.kill()
            blocked = True
    if blocked:
        print("  BLOCKED: a storm child hung past 120s (lock-ordering bug?) — exit 2")
        sys.exit(2)
    check("all storm children exited 0", all(p.returncode == 0 for p in procs),
          str([p.returncode for p in procs]))
    rows = FsStore(tmp).agent_mail_since(-1, to="session://storm")
    seqs = [r["seq"] for r in rows]
    check("count exact (100 lines, none torn)", len(rows) == 100, f"got {len(rows)}")
    check("every seq unique ACROSS PROCESSES", len(set(seqs)) == len(seqs),
          f"dupes: {sorted(s for s in set(seqs) if seqs.count(s) > 1)[:5]}")


# ── C · the MCP face ─────────────────────────────────────────────────────────────────────────────
def section_c(tmp):
    print("C · MCP face (registration · annotations · router · refusals · round-trips)")
    import importlib
    src = open(os.path.join(ROOT, "mcp_face", "tools", "sessions.py"), encoding="utf-8").read()
    check("floor: tools module never imports a spawn path",
          all(bad not in src for bad in ("import subprocess", "ui_claude_session", "runtime.implement")))

    from mcp.server.fastmcp import FastMCP
    from runtime.registry import NodeRegistry
    from runtime.suite import Suite
    suite = Suite(FsStore(tmp), NodeRegistry().discover([os.path.join(ROOT, "nodes")]))
    dev = FastMCP("dev-test")
    mod = importlib.import_module("mcp_face.tools.sessions")
    sessions, session_post = mod.register(dev, suite)

    tools = dev._tool_manager._tools
    check("both tools registered (pkgutil contract shape)",
          "sessions" in tools and "session_post" in tools, str(list(tools)))
    ra, wa = tools["sessions"].annotations, tools["session_post"].annotations
    check("F10.1: sessions annotated honest read-only",
          ra is not None and ra.readOnlyHint is True and ra.idempotentHint is True
          and ra.destructiveHint is False)
    check("F10.1: session_post annotated honest write",
          wa is not None and wa.readOnlyHint is False and wa.destructiveHint is False)

    # seed the registry (records carry state — the fold's record-seeding path; importer-shaped)
    live, idle, gone, blank = "live-1111", "idle-2222", "gone-3333", "blank-4444"
    suite.store.save_agent_session({"id": live, "state": "supervised-live", "name": "builder",
                                    "cwd": "/tmp/x", "title": "live one"})
    suite.store.save_agent_session({"id": idle, "state": "unsupervised-live", "title": "idle one"})
    suite.store.save_agent_session({"id": gone, "state": "closed", "title": "closed one"})
    suite.store.save_agent_session({"id": blank})        # state unknown (None)

    res = sessions(op="list")
    check("list shows the seeded fleet", res["total"] == 4 and len(res["sessions"]) == 4)
    check("list rows concise high-signal",
          {"id", "state", "title"} <= set(res["sessions"][0]))

    # the router — auto by state
    p = session_post(to=live, message="hi live", from_session=f"session://{gone}")
    check("auto → supervised-live = deliver/supervisor-inject",
          p["verb"] == "deliver" and p["routed"] == "supervisor-inject")
    p = session_post(to=f"session://{gone}", message="hi closed", from_session=f"session://{live}")
    check("auto → closed = wake/supervisor-wake (and session:// form accepted)",
          p["verb"] == "wake" and p["routed"] == "supervisor-wake")
    p = session_post(to=idle, message="hi idle", from_session=f"session://{live}")
    check("auto → unsupervised-live = queue/next-turn-pickup",
          p["verb"] == "queue" and p["routed"] == "next-turn-pickup")
    p = session_post(to=blank, message="hi unknown-state", from_session=f"session://{live}")
    check("auto → unknown state = NOT deliverable → queue", p["verb"] == "queue")

    # explicit-verb refusals TEACH
    expect_teaching("deliver → closed refused, teaches wake/consult",
                    lambda: session_post(to=gone, message="x", verb="deliver",
                                         from_session="lead"), "wake", "consult")
    expect_teaching("wake → supervised-live refused, teaches deliver",
                    lambda: session_post(to=live, message="x", verb="wake",
                                         from_session="lead"), "deliver")
    expect_teaching("wake → unsupervised refused, teaches the T1 branch danger",
                    lambda: session_post(to=idle, message="x", verb="wake",
                                         from_session="lead"), "second writer", "branches")
    expect_teaching("unknown session refused by the registry's own teaching error",
                    lambda: session_post(to="nope-0000", message="x", from_session="lead"),
                    "unknown session")
    expect_teaching("empty message refused", lambda: session_post(to=live, message="  ",
                    from_session="lead"), "message")
    expect_teaching("missing from_session refused, teaches the reply path",
                    lambda: session_post(to=live, message="x"), "reply path")
    expect_teaching("copies with non-consult refused",
                    lambda: session_post(to=live, message="x", verb="deliver", copies=2,
                                         from_session="lead"), "consult")
    cap = int(os.environ.get("COMPANY_FABRIC_CONCURRENCY", "3"))
    expect_teaching("copies > cap refused loud, names the env knob",
                    lambda: session_post(to=live, message="x", verb="consult", copies=cap + 1,
                                         from_session="lead"), "COMPANY_FABRIC_CONCURRENCY")

    # consult fan + thread aggregation + reply
    p = session_post(to=gone, message="three views please", verb="consult", copies=cap,
                     from_session=f"session://{live}")
    check("consult fan: one record, copies rides it, supervisor-fork",
          p["verb"] == "consult" and p["copies"] == cap and p["routed"] == "supervisor-fork")
    fan_thread = p["thread"]
    reply = session_post(to=live, message="fork-1 answer", verb="auto", thread=fan_thread,
                         from_session=f"session://{gone}")
    check("reply joins the fan thread", reply["thread"] == fan_thread)

    # post→inbox round-trip + pagination
    box = sessions(op="inbox", session=live)
    msgs = box["messages"]
    check("inbox round-trips bodies oldest-first",
          [m["message"] for m in msgs][:1] == ["hi live"] and msgs[-1]["message"] == "fork-1 answer")
    check("inbox thread filter isolates the fan",
          [m["message"] for m in sessions(op="inbox", session=live,
                                          thread=fan_thread)["messages"]] == ["fork-1 answer"])
    page1 = sessions(op="inbox", session=live, limit=1)
    page2 = sessions(op="inbox", session=live, since=page1["next_since"], limit=1)
    check("next_since pagination walks FIFO without skipping",
          page1["messages"][0]["seq"] < page2["messages"][0]["seq"]
          and page1["messages"][0]["message"] == "hi live")
    empty = sessions(op="inbox", session="never-posted-to")
    check("empty inbox is honest (no fabrication)",
          empty["total"] == 0 and empty["next_since"] == -1)

    # watch — only fabric events, honest cursor (the test plays the single-writer supervisor)
    suite.store.append_event({"kind": "agent_sessions.turn", "session": live, "summary": "turn 1"})
    suite.store.append_event({"kind": "op.run", "op": "voice.client", "summary": "noise"})
    w = sessions(op="watch", session=live)
    check("watch returns only agent_sessions.* for the session",
          w["total"] >= 1 and all(e["kind"].startswith("agent_sessions.") for e in w["events"]))
    w2 = sessions(op="watch", session=live, since=w["next_since"])
    check("watch cursor: nothing new after the tail", w2["total"] == 0)

    # describe — registry row + mail summary
    d = sessions(op="describe", session=live)
    check("describe joins record + mail counts",
          d["record"]["state"] == "supervised-live" and d["mail"]["inbound"] >= 2
          and d["mail"]["outbound"] >= 2)
    expect_teaching("describe unknown session teaches", lambda: sessions(op="describe",
                    session="nope-9999"), "unknown session")
    expect_teaching("bad op teaches the valid set", lambda: sessions(op="mailbox"), "inbox", "watch")
    expect_teaching("bad detail teaches", lambda: sessions(op="list", detail="full"), "concise")


def main():
    for name, fn in (("A", section_a), ("B", section_b), ("C", section_c)):
        tmp = tempfile.mkdtemp(prefix=f"agent-mail-{name}-")
        fn(tmp)
    print(f"\n{CHECKS[0]} checks · {len(FAILURES)} failures")
    if FAILURES:
        print("FAILED:", FAILURES)
        sys.exit(1)
    print("agent_sessions_mailbox_acceptance: PASS")


if __name__ == "__main__":
    main()
