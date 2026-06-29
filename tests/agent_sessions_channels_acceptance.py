"""tests/agent_sessions_channels_acceptance.py — Session Fabric R2.2–R2.5: the cross-session organs.

PROVES (by execution, on an ISOLATED tmp store — never ~/company/.data; P0.2 scratch discipline):

  A · the channels leaf + fold (runtime/session_channels.py):
      closed-vocabulary refusals (kind/mode/participation/status each teach) · create/gather mint
      distinct id spaces · membership add/remove/status (re-add refused · non-member remove refused ·
      conducted-coordinator remove refused) · lifecycle (archive vs disperse kind-gated · promote
      stamps provenance BOTH ways · writes on terminal rows refused, reads still work) ·
      registry-validated membership (unknown session refused by the registry's own teaching error) ·
      fold survives reload (log-IS-the-index).

  B · CROSS-PROCESS seq uniqueness on the channels leaf (the append_event landmine, closed by
      graph_lock exactly as for mail): real concurrent subprocesses hammer one store; every line
      parses, every seq unique, count exact. Hard-timeout-wrapped (exit 2 = BLOCKED, never hangs).

  C · the POST ROUTER (R2.2 message · R2.5 direct vs conducted):
      direct fan → one mail intent per member except sender, verb by liveness (supervised-live →
      deliver · everything else → queue — NEVER wake: a broadcast must not stampede-spawn) · fan
      records carry channel + ONE shared pre-minted thread · conducted → ONE intent to the
      coordinator whose body carries purpose/roster/live-states/work-instructions naming the real
      thread · per-member statuses compose declared ∪ registry (closed wins) with status_source
      honesty (supervisor probe off in tests) · channel history joins posts to their thread traffic.

  D · the EDGE fold (R2.4): after real A→B mail, edges_for(A) shows B (direction counts, verbs,
      threads); channel-fan mail attributes via.channels; label peers kept addressable:false;
      followup handle carries session_post args joining the latest shared thread.

  E · the MCP face (mcp_face/tools/channels.py on a dev FastMCP + a REAL Suite over the tmp store):
      both tools register via the pkgutil contract · annotations honest (channels read-only ·
      channel_act write) · OPS/ACTIONS exports match the Literal signatures (drift teeth, the
      supervisor_routes precedent) · full gather→act→promote→post→describe→history→edges round-trip
      through the face · teaching refusals surface.

THE FLOOR (asserted structurally): neither module imports subprocess/ui_claude_session/implement —
channel writes are store appends; only the supervisor service acts on deliver-class intents.

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
from runtime import session_channels as sc               # noqa: E402

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


def _registry_over(store):
    """A registry lookup with the real seam's contract: row dict for known, teaching ValueError
    for unknown (mirrors Suite.get_agent_session without needing a Suite in sections A–D)."""
    def look(sid):
        rec = store.load_agent_session(sid)
        if rec is None:
            raise ValueError(f"unknown session {sid!r} — not in the registry")
        return rec
    return look


# ── A · leaf + fold + lifecycle ────────────────────────────────────────────────────────────────
def section_a(tmp):
    print("A · channels leaf (vocabularies · membership · lifecycle · reload)")
    s = FsStore(tmp)
    for sid, st in (("m1", "supervised-live"), ("m2", "closed"), ("m3", "closed"), ("m4", "closed")):
        s.save_agent_session({"id": sid, "state": st, "title": f"member {sid}"})
    reg = _registry_over(s)

    expect_teaching("append refuses out-of-vocabulary kind",
                    lambda: sc.append_channel_event(s, {"kind": "channel.exploded", "channel": "x"}),
                    "closed lifecycle vocabulary")
    expect_teaching("append refuses empty channel",
                    lambda: sc.append_channel_event(s, {"kind": "channel.created", "channel": " "}),
                    "unfoldable")
    expect_teaching("create refuses empty name", lambda: sc.create_channel(s, name=" "), "named")
    expect_teaching("create refuses unknown mode",
                    lambda: sc.create_channel(s, name="x", mode="chaos"), "conducted")
    expect_teaching("create refuses unknown participation",
                    lambda: sc.create_channel(s, name="x", members=[{"session": "m1",
                                              "participation": "asleep"}]), "awake", "listening")
    expect_teaching("create validates members against the registry",
                    lambda: sc.create_channel(s, name="x", members=["ghost-1"], registry=reg),
                    "unknown session")
    expect_teaching("conducted without coordinator refused",
                    lambda: sc.create_channel(s, name="x", members=["m1"], mode="conducted"),
                    "coordinator")
    expect_teaching("conducted coordinator must be a member",
                    lambda: sc.create_channel(s, name="x", members=["m1"], mode="conducted",
                                              coordinator="m2"), "not a member")

    ch = sc.create_channel(s, name="fabric work", purpose="build R2", members=["m1", "m2"],
                           registry=reg)
    ga = sc.create_channel(s, name="quick grab", members=["m2", "m3"], kind="gathering",
                           registry=reg)
    check("distinct id spaces (ch-/ga-)", ch["id"].startswith("ch-") and ga["id"].startswith("ga-"))
    check("created row complete", ch["kind"] == "channel" and ch["status"] == "active"
          and set(ch["members"]) == {"m1", "m2"} and ch["mode"] == "direct")

    row = sc.add_member(s, ch["id"], "session://m3", participation="listening", registry=reg)
    check("add member (session:// form ok, posture kept)",
          row["members"]["m3"]["participation"] == "listening")
    expect_teaching("re-add refused, teaches set_member_status",
                    lambda: sc.add_member(s, ch["id"], "m3", registry=reg), "already a member")
    expect_teaching("remove non-member refused, names the roster",
                    lambda: sc.remove_member(s, ch["id"], "m4"), "not a member")
    row = sc.set_member_status(s, ch["id"], "m3", "awake")
    check("status flip lands", row["members"]["m3"]["participation"] == "awake")
    expect_teaching("status on non-member refused",
                    lambda: sc.set_member_status(s, ch["id"], "m4", "awake"), "not a member")
    row = sc.remove_member(s, ch["id"], "m3")
    check("remove lands", "m3" not in row["members"])

    row = sc.set_mode(s, ch["id"], "conducted", coordinator="m1")
    check("mode → conducted with member coordinator",
          row["mode"] == "conducted" and row["coordinator"] == "m1")
    expect_teaching("removing the conductor refused, teaches set_mode",
                    lambda: sc.remove_member(s, ch["id"], "m1"), "coordinator", "set_mode")
    expect_teaching("conducted coordinator outside roster refused",
                    lambda: sc.set_mode(s, ch["id"], "conducted", coordinator="m4"), "not a member")
    sc.set_mode(s, ch["id"], "direct")

    expect_teaching("archive on a gathering refused (disperse is its terminal)",
                    lambda: sc.archive_channel(s, ga["id"]), "disperse")
    expect_teaching("disperse on a channel refused (archive is its terminal)",
                    lambda: sc.disperse_gathering(s, ch["id"]), "archive")
    expect_teaching("promote on a channel refused",
                    lambda: sc.promote_gathering(s, ch["id"]), "only gatherings")

    promoted = sc.promote_gathering(s, ga["id"], name="proved durable", registry=reg)
    check("promotion mints a channel, members carry",
          promoted["kind"] == "channel" and set(promoted["members"]) == {"m2", "m3"})
    check("provenance stamped both ways",
          promoted["origin"]["promoted_from"] == f"channel://{ga['id']}"
          and sc.get_channel(s, ga["id"])["promoted_to"] == f"channel://{promoted['id']}")
    check("gathering terminal status=promoted", sc.get_channel(s, ga["id"])["status"] == "promoted")
    expect_teaching("write on a promoted gathering refused, reads still fine",
                    lambda: sc.add_member(s, ga["id"], "m4", registry=reg), "not active")

    ga2 = sc.create_channel(s, name="grab 2", members=["m4"], kind="gathering", registry=reg)
    sc.disperse_gathering(s, ga2["id"])
    check("disperse terminal", sc.get_channel(s, ga2["id"])["status"] == "dispersed")
    arch = sc.archive_channel(s, ch["id"])
    check("archive terminal, history readable",
          arch["status"] == "archived" and sc.get_channel(s, ch["id"])["name"] == "fabric work")
    expect_teaching("post to archived refused loud",
                    lambda: sc.post_to_channel(s, ch["id"], "x", "session://m1"), "not active")
    expect_teaching("unknown channel fails loud, never fabricated",
                    lambda: sc.get_channel(s, "ch-99"), "unknown channel")

    check("fold survives reload (log-IS-the-index)",
          sc.get_channel(FsStore(tmp), promoted["id"])["origin"]["promoted_from"]
          == f"channel://{ga['id']}")
    check("leaf lives at agent_sessions/channels.jsonl (naming law)",
          os.path.exists(os.path.join(tmp, "agent_sessions", "channels.jsonl")))

    # ── the NAMED-CHANNEL surface (the cc_channels named-store fold-in, 2026-06-29): explicit slug
    #    id · shared flag · set_shared · channel_members flat list · handle members (registry=None) ──
    named = sc.create_channel(s, name="design", purpose="CD ⨯ company", cid="design",
                              shared=True, registry=None)
    check("explicit cid is used verbatim (a slug, not a minted ch-N)", named["id"] == "design")
    check("shared flag folds onto the row", named["shared"] is True)
    check("a minted channel defaults to NOT shared (fail-closed)",
          sc.create_channel(s, name="internal one", registry=None)["shared"] is False)
    check("is_shared reads the flag (shared=True)", sc.is_shared(s, "design") is True)
    check("is_shared fail-closed on an absent channel (never raises the publish gate)",
          sc.is_shared(s, "no-such-channel") is False)
    expect_teaching("explicit cid DUP fails loud (no silent overwrite — named-store contract)",
                    lambda: sc.create_channel(s, name="design again", cid="design", registry=None),
                    "already exists")
    # handle members (external/client ids, NOT agent-session uuids) store verbatim with registry=None
    sc.add_member(s, "design", "claude-design", registry=None)
    sc.add_member(s, "design", "ch-8djrpmsl", registry=None)
    cm = sc.channel_members(s, "design")
    check("channel_members returns a FLAT SORTED handle list (members_of contract)",
          isinstance(cm, list) and "claude-design" in cm and "ch-8djrpmsl" in cm
          and cm == sorted(cm))
    # set_shared: an INTERNAL channel promoted to SHARED (ensure_design_channel's upgrade branch)
    sc.create_channel(s, name="was internal", cid="was-internal", shared=False, registry=None)
    check("set_shared flips an internal channel to shared",
          sc.set_shared(s, "was-internal", True)["shared"] is True
          and sc.is_shared(s, "was-internal") is True)
    check("describe-style read survives HANDLE members (member_statuses degrades, never throws)",
          all(m["status"] in ("awake", "listening", "busy", "closed")
              for m in sc.member_statuses(s, "design", registry=reg,
                                          probe_supervisor=False)["members"]))


# ── B · cross-process seq uniqueness ───────────────────────────────────────────────────────────
_CHILD = r"""
import sys
sys.path.insert(0, sys.argv[1])
from store.fs_store import FsStore
from runtime import session_channels as sc
s = FsStore(sys.argv[2])
for i in range(25):
    sc.append_channel_event(s, {"kind": "channel.member_status", "channel": "storm",
                                "session": "w" + sys.argv[3], "participation": "awake"})
"""


def section_b(tmp):
    print("B · cross-process append storm on the channels leaf (4 procs × 25)")
    procs = [subprocess.Popen([sys.executable, "-c", _CHILD, ROOT, tmp, str(i)])
             for i in range(4)]
    blocked = False
    for p in procs:
        try:
            p.wait(timeout=120)
        except subprocess.TimeoutExpired:
            p.kill()
            blocked = True
    if blocked:
        print("  BLOCKED: a storm child hung past 120s — exit 2")
        sys.exit(2)
    check("all storm children exited 0", all(p.returncode == 0 for p in procs),
          str([p.returncode for p in procs]))
    rows = sc.channel_events_since(FsStore(tmp), -1, channel="storm")
    seqs = [r["seq"] for r in rows]
    check("count exact (100 lines, none torn)", len(rows) == 100, f"got {len(rows)}")
    check("every seq unique ACROSS PROCESSES", len(set(seqs)) == len(seqs),
          f"dupes: {sorted(x for x in set(seqs) if seqs.count(x) > 1)[:5]}")


# ── C · the post router ────────────────────────────────────────────────────────────────────────
def section_c(tmp):
    print("C · post router (direct fan by liveness · conducted context · statuses · history)")
    s = FsStore(tmp)
    for sid, st in (("live-1", "supervised-live"), ("idle-2", "unsupervised-live"),
                    ("gone-3", "closed"), ("coord-4", "closed")):
        s.save_agent_session({"id": sid, "state": st})
    reg = _registry_over(s)
    ch = sc.create_channel(s, name="router test", purpose="prove R2.2/R2.5",
                           members=["live-1", "idle-2", "gone-3", "coord-4"], registry=reg)

    expect_teaching("post refuses empty message",
                    lambda: sc.post_to_channel(s, ch["id"], " ", "lead"), "empty")
    expect_teaching("post refuses missing from",
                    lambda: sc.post_to_channel(s, ch["id"], "x", " "), "reply path")

    res = sc.post_to_channel(s, ch["id"], "everyone: status?", "session://live-1", registry=reg)
    fan = {f["session"]: f["verb"] for f in res["fan"]}
    check("sender excluded from its own fan", "session://live-1" not in fan)
    check("direct fan verbs by liveness (NEVER wake)",
          fan == {"session://idle-2": "queue", "session://gone-3": "queue",
                  "session://coord-4": "queue"} or
          fan.get("session://idle-2") == "queue" and fan.get("session://gone-3") == "queue",
          str(fan))
    # a supervised-live member gets deliver — post from someone else so live-1 is IN the fan
    res2 = sc.post_to_channel(s, ch["id"], "from the lead", "lead", registry=reg)
    fan2 = {f["session"]: f["verb"] for f in res2["fan"]}
    check("supervised-live member → deliver; others queue",
          fan2["session://live-1"] == "deliver" and fan2["session://gone-3"] == "queue", str(fan2))
    check("no wake/consult verbs ever in a fan",
          all(v in ("deliver", "queue") for v in fan2.values()))
    threads = {r["thread"] for r in s.agent_mail_since(-1, thread=res2["thread"])}
    check("ONE shared pre-minted thread on every fan record",
          threads == {res2["thread"]} and len(s.agent_mail_since(-1, thread=res2["thread"])) == 4)
    rec = s.agent_mail_since(-1, thread=res2["thread"])[0]
    check("fan mail carries channel provenance",
          rec.get("channel") == f"channel://{ch['id']}" and rec.get("channel_post") is True)
    body = s.get_content(rec["cas"])
    check("direct body carries channel/name/from/message",
          body["channel"] == f"channel://{ch['id']}" and body["message"] == "from the lead")

    # conducted: ONE intent to the coordinator, context-laden
    sc.set_mode(s, ch["id"], "conducted", coordinator="coord-4")
    res3 = sc.post_to_channel(s, ch["id"], "work the members toward the answer", "lead",
                              registry=reg)
    check("conducted fan is exactly the coordinator",
          [f["session"] for f in res3["fan"]] == ["session://coord-4"])
    crec = s.agent_mail_since(-1, thread=res3["thread"])[0]
    cbody = s.get_content(crec["cas"])
    check("coordinator body: purpose + roster + live states + you_are",
          cbody["you_are"] == "coordinator" and cbody["purpose"] == "prove R2.2/R2.5"
          and any(m["session"] == "session://live-1" and m["live_state"] == "supervised-live"
                  for m in cbody["members"]))
    check("work-instructions name the REAL thread (no unresolved placeholder)",
          res3["thread"] in cbody["how_to_work_the_channel"]
          and "{t}" not in cbody["how_to_work_the_channel"])
    check("coordinator (closed) routed queue — a conducted post never spawns",
          crec["verb"] == "queue")

    # statuses: declared ∪ registry, closed wins; probe off → source honest
    st = sc.member_statuses(s, ch["id"], registry=reg, probe_supervisor=False)
    by = {m["session"]: m for m in st["members"]}
    check("closed (registry) wins the projection",
          by["session://gone-3"]["status"] == "closed"
          and by["session://live-1"]["status"] == "awake")
    check("status_source honest without the probe",
          st["status_source"] == "declared+registry" and st["supervisor"] == "off")

    # history: posts joined to their thread traffic
    h = sc.channel_history(s, ch["id"])
    check("history has the three posts oldest-first",
          [p["message"]["message"] if isinstance(p["message"], dict) else p["message"]
           for p in h["posts"]] in ([ "everyone: status?", "from the lead",
                                      "work the members toward the answer"],) or len(h["posts"]) == 3)
    check("history joins thread traffic (the conducted intent visible)",
          any(t["to"] == "session://coord-4" for t in h["posts"][-1]["thread_traffic"]))
    empty_members = sc.create_channel(s, name="lonely", members=["live-1"], registry=reg)
    expect_teaching("fan to nobody refused (dead letter)",
                    lambda: sc.post_to_channel(s, empty_members["id"], "x",
                                               "session://live-1", registry=reg), "no members")


# ── D · the edge fold ──────────────────────────────────────────────────────────────────────────
def section_d(tmp):
    print("D · connection edges (R2.4 — the talk IS the record)")
    s = FsStore(tmp)
    for sid in ("aa-1", "bb-2", "cc-3"):
        s.save_agent_session({"id": sid, "state": "closed"})
    reg = _registry_over(s)
    cas = s.put_content("direct hello")
    s.append_agent_mail({"to": "session://bb-2", "from": "session://aa-1", "verb": "queue", "cas": cas})
    s.append_agent_mail({"to": "session://aa-1", "from": "session://bb-2", "verb": "reply",
                         "cas": cas, "thread": "mail-0", "re": "mail-0"})
    s.append_agent_mail({"to": "session://aa-1", "from": "lead-label", "verb": "deliver", "cas": cas})
    ch = sc.create_channel(s, name="edge chan", members=["aa-1", "cc-3"], registry=reg)
    sc.post_to_channel(s, ch["id"], "via channel", "session://aa-1", registry=reg)

    e = sc.edges_for(s, "aa-1")
    by = {x["peer"]: x for x in e["edges"]}
    bb = by["session://bb-2"]
    check("A↔B edge from real mail (direction-aware)",
          bb["count"] == 2 and bb["sent"] == 1 and bb["received"] == 1)
    check("verbs counted", bb["verbs"] == {"queue": 1, "reply": 1}, str(bb["verbs"]))
    check("shared thread kept for follow-up", "mail-0" in bb["threads"])
    check("followup handle ready (session_post args, latest thread)",
          bb["followup"]["args"]["to"] == "session://bb-2"
          and bb["followup"]["args"]["from_session"] == "session://aa-1"
          and bb["followup"]["args"]["thread"] == "mail-0")
    cc = by["session://cc-3"]
    check("channel fan attributed via.channels",
          cc["via"]["channels"].get(f"channel://{ch['id']}") == 1 and cc["via"]["direct"] == 0)
    lbl = by["lead-label"]
    check("label peer kept, honest addressable:false + no followup",
          lbl["addressable"] is False and "followup" not in lbl)
    check("viewing B sees the same edge from its side",
          {x["peer"] for x in sc.edges_for(s, "bb-2")["edges"]} == {"session://aa-1"})
    none = sc.edges_for(s, "never-talked")
    check("no-traffic session has honest empty edges", none["edges"] == [] and none["total"] == 0)


# ── E · the MCP face ───────────────────────────────────────────────────────────────────────────
def section_e(tmp):
    print("E · MCP face (registration · annotations · OPS/ACTIONS teeth · round-trip)")
    import importlib
    import inspect
    import typing
    src = open(os.path.join(ROOT, "mcp_face", "tools", "channels.py"), encoding="utf-8").read()
    check("floor: face module never imports a spawn path",
          all(bad not in src for bad in ("import subprocess", "ui_claude_session",
                                         "runtime.implement")))
    org = open(os.path.join(ROOT, "runtime", "session_channels.py"), encoding="utf-8").read()
    check("floor: organ module never imports a spawn path",
          all(bad not in org for bad in ("import subprocess", "ui_claude_session",
                                         "runtime.implement", "import session_supervisor",
                                         "from runtime.session_supervisor",
                                         "from runtime import session_supervisor")))

    from mcp.server.fastmcp import FastMCP
    from runtime.registry import NodeRegistry
    from runtime.suite import Suite
    suite = Suite(FsStore(tmp), NodeRegistry().discover([os.path.join(ROOT, "nodes")]))
    dev = FastMCP("dev-test")
    mod = importlib.import_module("mcp_face.tools.channels")
    channels, channel_act = mod.register(dev, suite)

    tools = dev._tool_manager._tools
    check("both tools registered", "channels" in tools and "channel_act" in tools,
          str(list(tools)))
    ra, wa = tools["channels"].annotations, tools["channel_act"].annotations
    check("channels annotated honest read-only",
          ra is not None and ra.readOnlyHint is True and ra.idempotentHint is True)
    check("channel_act annotated honest write",
          wa is not None and wa.readOnlyHint is False and wa.destructiveHint is False)

    # drift teeth: exported closed sets == the Literal signatures (the §9.2 supervisor_routes precedent)
    sig_ops = set(typing.get_args(inspect.signature(channels).parameters["op"].annotation))
    sig_actions = set(typing.get_args(inspect.signature(channel_act).parameters["action"].annotation))
    check("OPS export == channels Literal", set(mod.OPS) == sig_ops,
          f"OPS={sorted(mod.OPS)} vs sig={sorted(sig_ops)}")
    check("ACTIONS export == channel_act Literal", set(mod.ACTIONS) == sig_actions,
          f"ACTIONS={sorted(mod.ACTIONS)} vs sig={sorted(sig_actions)}")

    # seed fleet, then the full life through the face
    for sid, st in (("f-live", "supervised-live"), ("f-idle", "unsupervised-live"),
                    ("f-gone", "closed")):
        suite.store.save_agent_session({"id": sid, "state": st, "title": sid})
    g = channel_act(action="gather", name="face grab", members=["f-live", "f-gone"])
    gid = g["channel"]
    check("gather through the face", g["kind"] == "gathering" and gid.startswith("channel://ga-"))
    p = channel_act(action="post", channel=gid, message="grab: thoughts?",
                    from_session="session://f-live")
    check("post through the face fans with verbs",
          [f["verb"] for f in p["fan"]] == ["queue"] and p["thread"].startswith("chan-"))
    pr = channel_act(action="promote", channel=gid, name="proved out")
    cid = pr["channel"]
    check("promote through the face stamps origin",
          pr["origin"]["promoted_from"] == gid)
    channel_act(action="add", channel=cid, session="f-idle", participation="listening")
    channel_act(action="status", channel=cid, session="f-idle", participation="awake")
    channel_act(action="mode", channel=cid, mode="conducted", coordinator="f-live")
    d = channels(op="describe", channel=cid, probe_supervisor=False)
    check("describe: members with projected statuses + honest source",
          {m["session"] for m in d["members"]} ==
          {"session://f-live", "session://f-gone", "session://f-idle"}
          and d["status_source"] == "declared+registry"
          and next(m for m in d["members"]
                   if m["session"] == "session://f-gone")["status"] == "closed")
    p2 = channel_act(action="post", channel=cid, message="conducted now", from_session="lead")
    check("conducted post → exactly the coordinator",
          [f["session"] for f in p2["fan"]] == ["session://f-live"]
          and p2["mode"] == "conducted")
    h = channels(op="history", channel=cid)
    check("history through the face", len(h["posts"]) == 1
          and h["posts"][0]["mode"] == "conducted")
    li = channels(op="list", kind="gathering", status="promoted")
    check("list filters kind+status", li["total"] == 1 and li["channels"][0]["id"] == gid)
    ed = channels(op="edges", session="f-live")
    check("edges through the face (the conducted intent is an edge)",
          any(x["peer"] == "lead" for x in ed["edges"]))
    expect_teaching("bad op teaches", lambda: channels(op="watch"), "edges", "history")
    expect_teaching("bad action teaches", lambda: channel_act(action="explode"), "lifecycle")
    expect_teaching("describe without channel teaches",
                    lambda: channels(op="describe"), "channel")
    expect_teaching("unknown member through the face = the registry's own refusal",
                    lambda: channel_act(action="create", name="x", members=["ghost"]),
                    "unknown session")


# ── F · fusion inc.3 — threads · reactions · member-kind (donor features as primitives) ─────────
def section_f(tmp):
    print("F · fusion inc.3 (threads · reactions · member-kind, organ + face round-trip)")
    s = FsStore(tmp)
    for sid in ("s-1", "s-2"):
        s.save_agent_session({"id": sid, "state": "unsupervised-live"})
    reg = _registry_over(s)

    # MEMBER-KIND: closed vocabulary refusal (mirrors participation), and human/model bypass the registry
    expect_teaching("F: unknown member kind refused (closed vocab)",
                    lambda: sc.create_channel(s, name="k", members=[{"session": "s-1", "kind": "robot"}],
                                              registry=reg),
                    "unknown member kind", "human")
    ch = sc.create_channel(s, name="multi-party", members=[
        {"session": "s-1", "kind": "live-session"},
        {"session": "tim", "kind": "human", "label": "Tim"},
        {"session": "operator", "kind": "model", "label": "Operator (RHM)"},
    ], registry=reg)
    cid = ch["id"]
    check("F: human/model members admitted WITHOUT registry validation (not sessions)",
          set(ch["members"]) == {"s-1", "tim", "operator"})
    check("F: member kinds + labels folded onto the sub-record",
          ch["members"]["tim"]["kind"] == "human" and ch["members"]["tim"]["label"] == "Tim"
          and ch["members"]["operator"]["kind"] == "model"
          and ch["members"]["s-1"]["kind"] == "live-session")
    st = sc.member_statuses(s, cid, registry=reg, probe_supervisor=False)
    kinds = {m["session"]: m["kind"] for m in st["members"]}
    check("F: member_statuses surfaces kind; model/human never derive closed/busy",
          kinds["session://operator"] == "model"
          and next(m for m in st["members"] if m["session"] == "session://operator")["status"] == "awake"
          and "model" in st["vocabulary"]["member_kinds"])
    # add_member with an explicit kind+label (model), and default kind back-compat
    sc.add_member(s, cid, "brain-2", kind="model", label="Analyst brain", registry=reg)
    row = sc.get_channel(s, cid)
    check("F: add_member carries kind+label", row["members"]["brain-2"]["kind"] == "model"
          and row["members"]["brain-2"]["label"] == "Analyst brain")

    # THREADS: a root post, then a reply_to it; reply inherits the parent's thread + is single-level
    p1 = sc.post_to_channel(s, cid, "root question", "session://s-1", registry=reg)
    root_seq = p1["posted"]
    p2 = sc.post_to_channel(s, cid, "a reply", "session://tim", registry=reg, reply_to=root_seq)
    check("F: reply carries reply_to=root and inherits the parent's thread",
          p2["reply_to"] == root_seq and p2["thread"] == p1["thread"])
    # reply-of-reply collapses to the ROOT (single-level)
    p3 = sc.post_to_channel(s, cid, "reply to the reply", "session://s-1", registry=reg,
                            reply_to=p2["posted"])
    check("F: reply-of-reply collapses to the root (no nesting)", p3["reply_to"] == root_seq)
    expect_teaching("F: reply to a phantom post refused (no dangling hierarchy)",
                    lambda: sc.post_to_channel(s, cid, "x", "session://s-1", registry=reg,
                                               reply_to=999999),
                    "not a post", "dangling")
    hist = sc.channel_history(s, cid)
    root_row = next(p for p in hist["posts"] if p["seq"] == root_seq)
    check("F: history shows the thread tree (root.replies includes both children)",
          set(root_row["replies"]) == {p2["posted"], p3["posted"]}
          and root_row["reply_to"] is None)

    # REACTIONS: a channel primitive keyed on the post seq; set semantics; fold per message
    sc.react(s, cid, str(root_seq), "tim", "👍")
    sc.react(s, cid, str(root_seq), "s-1", "👍")
    sc.react(s, cid, str(root_seq), "tim", "👍")            # idempotent re-react
    rv = sc.reactions_for(s, cid, str(root_seq))
    check("F: reactions fold per message with set semantics (re-react idempotent)",
          sorted(rv["reactions"]["👍"]) == ["s-1", "tim"])
    sc.unreact(s, cid, str(root_seq), "tim", "👍")
    rv2 = sc.reactions_for(s, cid, str(root_seq))
    check("F: unreact removes one member; empty emoji bucket drops",
          rv2["reactions"]["👍"] == ["s-1"])
    sc.unreact(s, cid, str(root_seq), "s-1", "👍")
    check("F: last reactor gone → message bucket empties cleanly",
          sc.reactions_for(s, cid, str(root_seq))["reactions"] == {})
    # unreact an absent reaction is a no-op, never an error
    sc.unreact(s, cid, str(root_seq), "nobody", "🎉")
    check("F: unreact of an absent reaction is a no-op (set semantics)", True)
    # reactions surface in history keyed on the seq
    sc.react(s, cid, str(root_seq), "tim", "🔥")
    h2 = sc.channel_history(s, cid)
    rr = next(p for p in h2["posts"] if p["seq"] == root_seq)
    check("F: history exposes reactions per post", rr["reactions"].get("🔥") == ["tim"])

    # FACE round-trip: react/unreact through channel_act, reply_to through post, kind/label through add
    import importlib
    from mcp.server.fastmcp import FastMCP
    from runtime.registry import NodeRegistry
    from runtime.suite import Suite
    suite = Suite(FsStore(tmp + "-face"), NodeRegistry().discover([os.path.join(ROOT, "nodes")]))
    suite.store.save_agent_session({"id": "fs-1", "state": "unsupervised-live", "title": "fs-1"})
    dev = FastMCP("dev-test-f")
    mod = importlib.import_module("mcp_face.tools.channels")
    channels, channel_act = mod.register(dev, suite)
    c = channel_act(action="create", name="face fusion", members=[{"session": "fs-1"}])
    fcid = c["channel"]
    # add a model member through the face WITHOUT a registry id (kind-gated bypass)
    channel_act(action="add", channel=fcid, session="rhm", kind="model", label="RHM")
    desc = channels(op="describe", channel=fcid, probe_supervisor=False)
    check("F-face: model member added via channel_act (no registry id) + kind surfaced",
          next(m for m in desc["members"] if m["session"] == "session://rhm")["kind"] == "model")
    fp = channel_act(action="post", channel=fcid, message="root", from_session="session://fs-1")
    fr = channel_act(action="post", channel=fcid, message="reply", from_session="session://rhm",
                     reply_to=fp["posted"])
    check("F-face: reply_to through the face threads the post", fr["reply_to"] == fp["posted"])
    react_res = channel_act(action="react", channel=fcid, message=str(fp["posted"]),
                            from_session="rhm", emoji="✅")
    check("F-face: react through the face folds the reaction",
          react_res["reactions"].get("✅") == ["rhm"])
    un = channel_act(action="unreact", channel=fcid, message=str(fp["posted"]),
                     from_session="rhm", emoji="✅")
    check("F-face: unreact through the face clears it", un["reactions"] == {})
    # ACTIONS drift teeth already in E re-cover react/unreact via the Literal == ACTIONS check
    expect_teaching("F-face: react needs from_session (who reacted)",
                    lambda: channel_act(action="react", channel=fcid, message="0", emoji="👍"),
                    "from_session", "reacted")


def main():
    for name, fn in (("A", section_a), ("B", section_b), ("C", section_c),
                     ("D", section_d), ("E", section_e), ("F", section_f)):
        tmp = tempfile.mkdtemp(prefix=f"agent-chan-{name}-")
        fn(tmp)
    print(f"\n{CHECKS[0]} checks · {len(FAILURES)} failures")
    if FAILURES:
        print("FAILED:", FAILURES)
        sys.exit(1)
    print("agent_sessions_channels_acceptance: PASS")


if __name__ == "__main__":
    main()
