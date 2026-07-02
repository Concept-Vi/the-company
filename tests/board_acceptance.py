"""tests/board_acceptance.py — ④ THE CONTAINER, L6-BOARD (C6.1–C6.7): the rebuilt board, verified BY USE.

Covers, with real calls against the REAL board store (channel-memory/noticeboard/, 1000+ items), the real
local Postgres projection, and read-only checks against cvi_mine (never mutated):

  C6.1  scope + author land as ADDRESSES on the item shape; list(scope=project://…) filters (real store:
        block-composition = 279); the DERIVED authored_by index answers the reverse lookup WITHOUT an
        O(n) scan — TIMED against the full-scan equivalent on the real store.
  C6.2  the 8 new item_type rows (observation, milestone, design, task, blocker, cognitive_guide,
        research, diagnostic) registered with states honoring the legacy open/resolved/closed; an illegal
        transition is REFUSED fail-loud.
  C6.3  the 319 pour reconciliation closes vs cvi_mine (denominators printed); uuid ids KEPT; 5 sampled
        posts keep their long-tail content keys byte-true vs cvi_mine; resolver-names → history entries;
        project_id → scope; the stale JSONB NOT migrated + the one provenance note present.
  C6.4  the Postgres projection derives from the files; DELETING every row and re-deriving reproduces
        IDENTICAL counts (files stay truth).
  C6.5  item.filed / item.transitioned emit on the channel layer; a SUBSCRIBED test agent (a capturing
        emitter) wakes on both; the MCP register() seam wires the emitter to suite.emit_run_record.
  C6.6  a pin is a VIEW-record edge: pinning an item on one board-view does NOT pin it on another.
  C6.7  the board is NOT the inbox: a filed board item does NOT appear in inbox_lanes; an EXPLICIT
        escalation (surface_review) does; inbox_lanes' source carries no board read.

Run:  .venv/bin/python tests/board_acceptance.py     (exit 0 = all green)
Needs: local Postgres 127.0.0.1:15432 with 0020_board_projection.sql applied + the L6 migration run
       (.venv/bin/python ops/migrate_board_from_cvi.py --slice all).
"""
import inspect
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from runtime import cc_board as cb                       # noqa: E402
import ops.migrate_board_from_cvi as mig                 # noqa: E402

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


PG = ["psql", "-h", os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
      "-p", os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
      "-U", os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"), "-v", "ON_ERROR_STOP=1", "-tA", "-c"]
ENV = {**os.environ, "PGPASSWORD": os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres")}


def q(db, sql):
    r = subprocess.run(PG[:-1] + ["-d", db, "-c", sql], capture_output=True, text=True, env=ENV)
    if r.returncode != 0:
        raise RuntimeError(f"psql({db}) failed: {r.stderr.strip()[:400]}")
    return r.stdout.strip()


tmp = tempfile.mkdtemp(prefix="board-accept-")
try:
    cb.set_board_emitter(None)                            # a clean slate for the emitter checks

    # ── C6.2 — the 8 new item_type rows + legacy states + fail-loud illegal transition ────────────────
    reg_types = cb.item_types()
    new8 = ["observation", "milestone", "design", "task", "blocker", "cognitive_guide", "research", "diagnostic"]
    check("C6.2 all 8 new item_types registered", all(t in reg_types for t in new8))
    for t in new8:
        st = cb._items_reg()[t].states
        check(f"C6.2 {t} honours legacy open/resolved/closed", all(s in st for s in ("open", "resolved", "closed")))
    check("C6.2 issue gained additive `closed` (12 cloud posts land in it)",
          "closed" in cb._items_reg()["issue"].states)
    it = cb.file_item("observation", "obs", "b", "tester", board_dir=tmp)
    try:
        cb.transition(it["id"], "nonsense-state", board_dir=tmp)
        check("C6.2 illegal transition refused fail-loud", False)
    except cb.BoardError as e:
        check("C6.2 illegal transition refused fail-loud", "illegal transition" in str(e))

    # ── C6.1 — scope/author as ADDRESSES + list(scope=…) + the derived reverse, timed ─────────────────
    rec = cb.file_item("note", "fusion check", "b", "tim",
                       scope="project://the-fusion", author="operator://tim", board_dir=tmp)
    check("C6.1 scope lands as an address on the item shape", rec["scope"] == "project://the-fusion")
    check("C6.1 author lands as an address on the item shape", rec["author"] == "operator://tim")
    got = cb.list_items(scope="project://the-fusion", board_dir=tmp)
    check("C6.1 list(scope=project://the-fusion) returns it", [r["id"] for r in got] == [rec["id"]])
    check("C6.1 author derives from a legacy handle (ch-… → session://)",
          cb.file_item("note", "x", "", "ch-abc99", board_dir=tmp)["author"] == "session://ch-abc99")
    # the REAL store: the poured 319 are scope-addressed; list(scope=…) is the board projection
    bc = cb.list_items(scope="project://block-composition")
    print(f"  [real store] list(scope=project://block-composition) -> {len(bc)} items")
    check("C6.1 real-store scope filter returns block-composition's 279", len(bc) == 279)
    all_real = cb.list_items()
    print(f"  [real store] total items: {len(all_real)}")
    check("C6.1 real store carries 1000+ items (the 690-era engine items + the 319 + the note)",
          len(all_real) >= 1009)
    # the derived reverse vs the O(n) scan — TIMED on the real store
    author_addr = "session://ch-3mpkjg3r"                  # the heaviest real author (291 legacy items)
    t0 = time.perf_counter()
    scan = [r["id"] for r in cb.list_items() if r.get("author") == author_addr]
    t_scan = time.perf_counter() - t0
    cb.authored_by_index()                                 # warm (load/derive once, like any process would)
    t0 = time.perf_counter()
    idx = cb.items_by_author(author_addr)
    t_idx = time.perf_counter() - t0
    print(f"  [timing] O(n) scan {t_scan*1000:.1f}ms vs derived index {t_idx*1000:.3f}ms "
          f"on {len(all_real)} items ({len(idx)} hits)")
    check("C6.1 derived index and O(n) scan agree", sorted(idx) == sorted(scan))
    check("C6.1 reverse lookup via the index beats the O(n) scan", t_idx < t_scan)
    check("C6.1 index is regenerable (rebuild reproduces identical counts)",
          cb.rebuild_authored_by_index()["count"] == len(all_real))

    # ── C6.3 — the 319 pour: reconciliation + uuid ids + long-tail + history + scope ──────────────────
    posts = json.loads(q("cvi_mine",
        "select coalesce(json_agg(t),'[]') from (select post_id, project_id, post_type, status, content "
        "from notice_board_posts) t"))
    pmap = dict(r.split("|") for r in q("cvi_mine",
        "select project_id || '|' || project_key from projects").splitlines())
    check("C6.3 cvi_mine still carries exactly 319 posts (immutable source)", len(posts) == 319)
    landed = missing = 0
    for p in posts:
        if os.path.exists(os.path.join(cb.NOTICEBOARD_DIR, f"{p['post_id']}.md")):
            landed += 1
        else:
            missing += 1
    print(f"  [reconciliation] 319 = {landed} landed + 0 excluded + {missing} missing")
    check("C6.3 reconciliation closes: 319 = 319 landed + 0 excluded", landed == 319 and missing == 0)
    # 5 sampled posts: every long-tail content key preserved byte-true; state honoured; scope from project_id
    samples = sorted(posts, key=lambda p: -len(p.get("content") or {}))[:5]
    for p in samples:
        r = cb.get_item(p["post_id"])
        content = p.get("content") or {}
        for k, v in content.items():
            if k == "title":       # a null cloud title lands as the synthesized "(… untitled)" fallback
                ok = r.get("title") == v or (v in (None, "") and "untitled" in (r.get("title") or ""))
            elif k == "description":   # a null description lands as the empty body ('' ≡ null)
                ok = (r.get("body") or "") == (v or "")
            else:
                ok = r.get(k) == v
            assert ok, f"FAIL: C6.3 long-tail key {k!r} drifted on {p['post_id']}: {r.get(k)!r} != {v!r}"
        check(f"C6.3 sampled {p['post_id'][:8]}… keeps all {len(content)} content keys + state + scope",
              r["state"] == p["status"] and r["scope"] == f"project://{pmap[p['project_id']]}")
    # resolver-names → synthesized history (a resolved post carries {to:resolved, by:resolved_by})
    rb = next(p for p in posts if (p.get("content") or {}).get("resolved_by") and p["status"] == "resolved")
    hist = cb.get_item(rb["post_id"])["history"]
    check("C6.3 resolver-name became a history entry ({to:'resolved', by:resolved_by})",
          any(h.get("to") == "resolved" and h.get("by") == rb["content"]["resolved_by"] for h in hist))
    # the stale JSONB: NOT migrated (exactly the 319 + the ONE provenance note carry source=cvi_mine)
    cvi_sourced = cb.list_items(source="cvi_mine")
    check("C6.3 stale JSONB NOT migrated (exactly 319 posts + 1 provenance note carry source=cvi_mine)",
          len(cvi_sourced) == 320)
    prov = cb.get_item(mig.PROVENANCE_NOTE_ID)
    check("C6.3 the one provenance note is filed and names the stale JSONB",
          "notice_board JSONB" in prov["title"] and "NOT migrated" in prov["title"])

    # ── C6.4 — the DERIVED Postgres projection: delete + re-derive = identical counts ─────────────────
    rep1 = mig.derive_projection()
    counts1 = q("postgres", "select type || '|' || state || '|' || count(*) from container.board_items "
                            "group by type, state order by 1")
    q("postgres", "delete from container.board_items")
    check("C6.4 projection rows deleted (the derived side is disposable)",
          q("postgres", "select count(*) from container.board_items") == "0")
    rep2 = mig.derive_projection()
    counts2 = q("postgres", "select type || '|' || state || '|' || count(*) from container.board_items "
                            "group by type, state order by 1")
    print(f"  [projection] derive #1: {rep1['files']} files -> {rep1['rows']} rows; "
          f"derive #2 after delete: {rep2['rows']} rows")
    check("C6.4 delete + re-derive reproduces identical row count", rep1["rows"] == rep2["rows"])
    check("C6.4 delete + re-derive reproduces identical (type,state) counts", counts1 == counts2)
    check("C6.4 projection row count == file count (files stay truth)",
          rep2["files"] == rep2["rows"] == len(cb.list_items()))

    # ── C6.5 — item.filed / item.transitioned wake a subscribed test agent ────────────────────────────
    woken = []
    cb.set_board_emitter(lambda ev, fields: woken.append((ev, fields)))
    ev_item = cb.file_item("task", "wake test", "b", "tester", board_dir=tmp)
    check("C6.5 item.filed emitted on the channel layer (subscriber woke)",
          woken and woken[-1][0] == "item.filed" and woken[-1][1]["id"] == ev_item["id"])
    check("C6.5 the event carries scope + author (addresses ride the wire)",
          woken[-1][1]["scope"] == "global" and "author" in woken[-1][1])
    cb.transition(ev_item["id"], "resolved", by="tester", board_dir=tmp)
    check("C6.5 item.transitioned emitted (subscriber woke on the move)",
          woken[-1][0] == "item.transitioned" and woken[-1][1]["to"] == "resolved")
    # emit failure is SURFACED, never breaks the write
    cb.set_board_emitter(lambda ev, fields: (_ for _ in ()).throw(RuntimeError("subscriber down")))
    broken = cb.file_item("note", "emit-fail", "", "tester", board_dir=tmp)
    check("C6.5 a failing emitter is surfaced as emit_error, the write still lands",
          "RuntimeError" in broken.get("emit_error", "") and
          os.path.exists(os.path.join(tmp, f"{broken['id']}.md")))
    cb.set_board_emitter(None)
    # the MCP register() seam wires the emitter to suite.emit_run_record
    calls = []

    class _StubMCP:
        def tool(self):
            return lambda fn: fn

    class _StubSuite:
        def emit_run_record(self, op, duration_ms, **fields):
            calls.append((op, fields))

    import mcp_face.tools.cc_board as mcp_board
    mcp_board.register(_StubMCP(), _StubSuite())
    wired = cb.file_item("note", "mcp-wire", "", "tester", board_dir=tmp)
    check("C6.5 register() wires the board emitter to suite.emit_run_record",
          calls and calls[-1][0] == "item.filed" and calls[-1][1]["id"] == wired["id"])
    cb.set_board_emitter(None)

    # ── C6.6 — a pin is a VIEW-record edge (pin on one view absent on another) ────────────────────────
    check("C6.6 the `pinned` edge kind is registered (a row-add, no code)", "pinned" in cb.edge_kinds())
    target = cb.file_item("idea", "pin me", "", "tester", board_dir=tmp)
    v_mine = cb.create_view("My board", "tim", board_dir=tmp)
    v_yours = cb.create_view("Your board", "lead", board_dir=tmp)
    cb.pin(v_mine["id"], target["id"], by="tim", board_dir=tmp)
    check("C6.6 pinned on MY view", cb.is_pinned(target["id"], v_mine["id"], board_dir=tmp))
    check("C6.6 NOT pinned on YOUR view (salience belongs to the view)",
          not cb.is_pinned(target["id"], v_yours["id"], board_dir=tmp))
    ins = cb.reverse_traverse(target["address"], "pinned", board_dir=tmp)
    check("C6.6 the pin is a typed edge FROM the view TO the item (reverse finds exactly one view)",
          [e["item"]["id"] for e in ins] == [v_mine["id"]])
    try:
        cb.pin(target["id"], v_mine["id"], board_dir=tmp)
        check("C6.6 pinning ON a non-view refused fail-loud", False)
    except cb.BoardError:
        check("C6.6 pinning ON a non-view refused fail-loud", True)

    # ── C6.7 — the board is NOT the inbox ─────────────────────────────────────────────────────────────
    from store.fs_store import FsStore
    from runtime.registry import NodeRegistry
    from runtime.suite import Suite
    store = FsStore(os.path.join(tmp, "store"))
    nreg = NodeRegistry(); nreg.discover([os.path.join(ROOT, "nodes")])
    suite = Suite(store, nreg, nodes_dir=os.path.join(ROOT, "nodes"))
    board_item = cb.file_item("issue", "a board issue — discourse, not escalation", "", "tester",
                              board_dir=tmp)
    lanes = suite.inbox_lanes()
    everything = json.dumps(lanes)
    check("C6.7 a filed board item does NOT appear in inbox_lanes (board=discourse)",
          board_item["id"] not in everything and lanes["counts"]["escalations"] == 0)
    esc = suite.surface_review({"title": "escalated: a board item needs the operator",
                                "board_item": board_item["address"], "kind": "board_escalation"})
    lanes2 = suite.inbox_lanes()
    check("C6.7 an EXPLICIT escalation (surface_review) DOES appear in inbox_lanes",
          any(d["id"] == esc["id"] for d in lanes2["live_escalations"]))
    src = inspect.getsource(Suite.inbox_lanes)
    check("C6.7 inbox_lanes carries no board read (grep-verified: the traffic never runs board→inbox)",
          "board" not in src and "cc_board" not in src)

    print(f"\nALL {PASS} CHECKS PASS — L6-BOARD: scope/author addressed, the 319 landed losslessly, "
          f"the projection derives, events wake, pins are view-records, the board is not the inbox")
finally:
    cb.set_board_emitter(None)
    shutil.rmtree(tmp, ignore_errors=True)
