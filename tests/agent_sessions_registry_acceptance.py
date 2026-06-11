#!/usr/bin/env python3
"""tests/agent_sessions_registry_acceptance.py — Session Fabric F1.2: the agent-session REGISTRY.

By USE over a temp store + synthetic catalog fixtures (no model, no live process — the registry is
records + log + fold; the supervisor that EMITS live events is a separate lane, its emit shape is
consumed here exactly as runtime/suite.py declares it). Proves:

  · `session://` is a registered scheme (contracts.address) and `resolve_address` resolves it to the
    agent-session registry RECORD; an unknown id RAISES fail-loud (never fabricate a session).
  · store whole-record primitives (`save_agent_session`/`load`/`list`/`agent_session_mtimes`) — the
    save_journey atomic pattern on the DISTINCT `agent_sessions/` dir (never the review-session
    `sessions/` dir); a record with no id is REFUSED (structural fail-loud, the append_mark discipline).
  · the REGISTRY FOLD (log-IS-the-index, the run-index pattern): records seed identity, the
    agent_sessions.* closed event set (AGENT_SESSION_OPS) moves state/last_activity — truthful
    transitions (spawned→supervised-live, closed→closed, adopted→supervised-live, registered→
    unsupervised-live; turn/idle move activity only); a fresh Suite over the same store CONVERGES
    (cross-process shape — derived from shared disk, never RAM); record re-writes refresh IDENTITY
    only (the log owns state once a row exists); an unknown state filter RAISES the teaching error;
    a malformed event is counted loud in fold_errors, never bricks the projection.
  · the IMPORTER (ops/agent_sessions_importer.py) on a synthetic catalog: the EXACT title fallback
    chain (ai-title LAST-occurrence-wins → last-prompt → first-user-turn truncated → untitled+envelope),
    sidechain (agent-*) skipping, summarizer marking, idempotent re-run (skip-unchanged), and the
    live-record guard (a non-closed record is NEVER stomped by backfill). The importer's run against
    the REAL catalog (≥1,000 records, coverage stats) is the lane's by-use verification, executed
    separately — this suite proves the chain's semantics deterministically.
"""
import importlib.util
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from contracts.address import SCHEMES, scheme  # noqa: E402
from store.fs_store import FsStore  # noqa: E402
from runtime.suite import Suite  # noqa: E402
from runtime.registry import NodeRegistry  # noqa: E402
from runtime.cognition import resolve_address  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "agent_sessions_importer", os.path.join(ROOT, "ops", "agent_sessions_importer.py"))
importer = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(importer)

PASS = 0


def check(label, cond):
    global PASS
    mark = "ok " if cond else "XX "
    print(f"  {mark} {label}")
    if not cond:
        raise SystemExit(f"FAIL: {label}")
    PASS += 1


def refused(label, fn, exc=ValueError):
    try:
        fn()
        check(label + " (should have raised)", False)
    except exc:
        check(label, True)


def _suite(root):
    return Suite(FsStore(root), NodeRegistry().discover([os.path.join(ROOT, "nodes")]))


def _jsonl(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        for rec in lines:
            f.write(json.dumps(rec) + "\n")


def _user(text, ts, **kw):
    return {"type": "user", "message": {"role": "user", "content": text},
            "timestamp": ts, "cwd": "/home/tim/proj", "gitBranch": "main", "version": "2.1.0", **kw}


def _asst(text, ts):
    return {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": text}]},
            "timestamp": ts, "cwd": "/home/tim/proj", "version": "2.1.0"}


with tempfile.TemporaryDirectory() as tmp:
    store_root = os.path.join(tmp, "store")
    store = FsStore(store_root)

    print("[1] session:// is a registered scheme; the store's whole-record primitives hold")
    check("1.1 'session' in contracts.address.SCHEMES", "session" in SCHEMES)
    check("1.2 scheme('session://abc') == 'session'", scheme("session://abc") == "session")
    store.save_agent_session({"id": "rec-1", "title": "T", "state": "closed", "cwd": "/x"})
    check("1.3 save→load round-trips on agent_sessions/ (distinct from review sessions/)",
          store.load_agent_session("rec-1")["title"] == "T"
          and not os.path.exists(os.path.join(store_root, "sessions", "rec-1.json"))
          and os.path.exists(os.path.join(store_root, "agent_sessions", "rec-1.json")))
    check("1.4 list + mtimes see the record", store.list_agent_sessions() == ["rec-1"]
          and "rec-1" in store.agent_session_mtimes())
    refused("1.5 a record with NO id is refused (fail-loud — unresolvable)",
            lambda: store.save_agent_session({"title": "no id"}))
    refused("1.6 a record with an EMPTY id is refused",
            lambda: store.save_agent_session({"id": "   "}))

    print("[2] resolve_address: session:// → the registry record; unknown RAISES")
    check("2.1 session://rec-1 resolves to the record",
          resolve_address(store, "session://rec-1")["title"] == "T")
    refused("2.2 an unknown session id raises (never fabricate)",
            lambda: resolve_address(store, "session://nope"))

    print("[3] the registry fold — records seed identity, the agent_sessions.* log owns the trajectory")
    suite = _suite(store_root)
    rows = suite.list_agent_sessions()
    check("3.1 a record-seeded row projects {id,name,cwd,state,last_activity,title}",
          rows["total"] == 1 and rows["sessions"][0]["state"] == "closed"
          and rows["sessions"][0]["cwd"] == "/x")
    store.append_event({"kind": "agent_sessions.spawned", "session": "rec-1", "summary": "s", "name": "builder"})
    row = suite.list_agent_sessions()["sessions"][0]
    check("3.2 spawned → supervised-live (+ identity carried on the event lands)",
          row["state"] == "supervised-live" and row["name"] == "builder")
    prev_activity = row["last_activity"]
    store.append_event({"kind": "agent_sessions.turn", "session": "rec-1", "summary": "t"})
    row = suite.list_agent_sessions()["sessions"][0]
    check("3.3 turn moves last_activity, NOT state",
          row["state"] == "supervised-live" and row["last_activity"] != prev_activity)
    # a record re-write must refresh IDENTITY only — the log owns state once the row exists
    store.save_agent_session({"id": "rec-1", "title": "T2", "state": "closed", "cwd": "/x"})
    row = suite.list_agent_sessions()["sessions"][0]
    check("3.4 record re-write refreshes identity (title) but cannot roll back log-owned state",
          row["title"] == "T2" and row["state"] == "supervised-live")
    store.append_event({"kind": "agent_sessions.closed", "session": "rec-1", "summary": "c"})
    check("3.5 closed → closed", suite.list_agent_sessions()["sessions"][0]["state"] == "closed")
    store.append_event({"kind": "agent_sessions.adopted", "session": "rec-1", "summary": "a"})
    check("3.6 adopted → supervised-live (WAKE/adopt re-owns it)",
          suite.list_agent_sessions()["sessions"][0]["state"] == "supervised-live")
    store.append_event({"kind": "agent_sessions.registered", "session": "fresh-9", "summary": "r",
                        "cwd": "/tmp", "name": "fresh"})
    check("3.7 registered (no record) creates an unsupervised-live row",
          suite.list_agent_sessions(state="unsupervised-live")["sessions"][0]["id"] == "fresh-9")
    fresh = _suite(store_root)
    check("3.8 a FRESH Suite over the same store converges (cross-process shape — disk, never RAM)",
          {r["id"]: r["state"] for r in fresh.list_agent_sessions()["sessions"]}
          == {r["id"]: r["state"] for r in suite.list_agent_sessions()["sessions"]})
    refused("3.9 an unknown state filter raises the teaching error",
            lambda: suite.list_agent_sessions(state="alive"))
    n_before = suite.list_agent_sessions()["total"]
    store.append_event({"kind": "agent_sessions.turn", "summary": "malformed — no session id"})
    r = suite.list_agent_sessions()
    check("3.10 a malformed fabric event is COUNTED (fold_errors), never bricks the projection",
          r["fold_errors"] >= 1 and r["total"] == n_before)
    desc = suite.get_agent_session("rec-1")
    check("3.11 describe joins row (log-owned state) over record (identity + envelope)",
          desc["state"] == "supervised-live" and desc["title"] == "T2")
    refused("3.12 describe of an unknown session raises", lambda: suite.get_agent_session("ghost"))

    print("[4] the importer — the EXACT title fallback chain on a synthetic catalog (read-only)")
    catalog = os.path.join(tmp, "projects", "-home-tim-proj")
    os.makedirs(catalog)
    long_prompt = "build the session fabric registry " * 8        # >100 chars → truncation
    _jsonl(os.path.join(catalog, "aaaa-ai.jsonl"), [
        {"type": "ai-title", "aiTitle": "early title (must lose)"},
        _user("real prompt", "2026-06-01T00:00:00Z"),
        _asst("reply", "2026-06-01T00:00:01Z"),
        {"type": "last-prompt", "lastPrompt": "the last prompt"},
        {"type": "ai-title", "aiTitle": "final title (last occurrence wins)"},
    ])
    _jsonl(os.path.join(catalog, "bbbb-lp.jsonl"), [
        _user("<system-reminder>noise</system-reminder>", "2026-06-02T00:00:00Z"),
        _asst("reply", "2026-06-02T00:00:01Z"),
        {"type": "last-prompt", "lastPrompt": "where it ended"},
    ])
    _jsonl(os.path.join(catalog, "cccc-fu.jsonl"), [
        _user("Caveat: noise first", "2026-06-03T00:00:00Z"),
        _user(long_prompt, "2026-06-03T00:00:01Z"),
        _asst("reply", "2026-06-03T00:00:02Z"),
    ])
    _jsonl(os.path.join(catalog, "dddd-env.jsonl"), [
        _user("Context: This summary will be shown in a list to help users…", "2026-06-04T00:00:00Z"),
        _asst("<summary>a machine summary</summary>", "2026-06-04T00:00:01Z"),
    ])
    _jsonl(os.path.join(catalog, "agent-zz.jsonl"), [_user("a sidechain — must be skipped", "2026-06-05T00:00:00Z")])

    istore = FsStore(os.path.join(tmp, "imp-store"))
    stats = importer.run_import(os.path.join(tmp, "projects"), istore)
    check("4.1 four mains imported; the agent-* sidechain skipped",
          stats["written"] == 4 and stats["main_files"] == 4)
    check("4.2 chain step 1 — ai-title, LAST occurrence wins (tail-scan semantics), beats last-prompt",
          istore.load_agent_session("aaaa-ai")["title"] == "final title (last occurrence wins)"
          and istore.load_agent_session("aaaa-ai")["title_source"] == "ai-title")
    check("4.3 chain step 2 — last-prompt when no ai-title (noise user turn not used)",
          istore.load_agent_session("bbbb-lp")["title"] == "where it ended"
          and istore.load_agent_session("bbbb-lp")["title_source"] == "last-prompt")
    fu = istore.load_agent_session("cccc-fu")
    check("4.4 chain step 3 — FIRST REAL user turn (noise-prefixed skipped), truncated ≤100",
          fu["title_source"] == "first-user-turn" and len(fu["title"]) <= 100
          and fu["title"].startswith("build the session fabric registry"))
    env = istore.load_agent_session("dddd-env")
    check("4.5 chain step 4 — untitled+envelope for the summarizer one-shot, marked summarizer:true",
          env["title_source"] == "untitled-envelope" and env["summarizer"] is True
          and "2026-06-04" in env["title"] and env["state"] == "closed")
    check("4.6 coverage stats account for every record",
          sum(stats["titles"].values()) == 4 and stats["summarizer_sessions"] == 1)
    check("4.7 envelope fields landed (cwd · started · last_activity · turns · bytes)",
          env["cwd"] == "/home/tim/proj" and env["started"] == "2026-06-04T00:00:00Z"
          and env["turns"] == 2 and env["jsonl_bytes"] > 0)
    stats2 = importer.run_import(os.path.join(tmp, "projects"), istore)
    check("4.8 idempotent re-run skips unchanged sources",
          stats2["written"] == 0 and stats2["skipped_unchanged"] == 4)
    live = istore.load_agent_session("aaaa-ai")
    live["state"] = "supervised-live"
    istore.save_agent_session(live)
    stats3 = importer.run_import(os.path.join(tmp, "projects"), istore, force=True)
    check("4.9 the LIVE-record guard — a non-closed record is never stomped by backfill",
          stats3["skipped_live"] == 1
          and istore.load_agent_session("aaaa-ai")["state"] == "supervised-live")
    isuite = _suite(os.path.join(tmp, "imp-store"))
    r = isuite.list_agent_sessions()
    check("4.10 the fold returns the imported records; summarizer filter narrows to real conversations",
          r["total"] == 4 and isuite.list_agent_sessions(include_summarizers=False)["total"] == 3)
    check("4.11 the imported records resolve as session:// addresses",
          resolve_address(istore, "session://bbbb-lp")["title"] == "where it ended")

with tempfile.TemporaryDirectory() as tmp:
    print("[5] the canonical-id rule — supervisor handle emits fold onto catalog uuid rows (fork-safe)")
    store5 = FsStore(os.path.join(tmp, "store"))
    suite5 = _suite(os.path.join(tmp, "store"))
    # a WAKE: the catalog record exists (uuid), the supervisor emits spawned under its LOCAL handle
    # with resume=<uuid> (the real emit shape, runtime/session_supervisor.py) — ONE row results.
    store5.save_agent_session({"id": "uuid-1", "title": "the original", "state": "closed", "cwd": "/p"})
    store5.append_event({"kind": "agent_sessions.spawned", "session": "as-aaa", "resume": "uuid-1",
                         "fork": False, "summary": "wake", "name": "waked"})
    r = suite5.list_agent_sessions()
    check("5.1 a WAKE spawned(handle, resume=uuid) folds onto the CATALOG row — one row, supervised-live",
          r["total"] == 1 and r["sessions"][0]["id"] == "uuid-1"
          and r["sessions"][0]["state"] == "supervised-live" and r["sessions"][0]["title"] == "the original")
    store5.append_event({"kind": "agent_sessions.turn", "session": "as-aaa",
                         "claude_session_id": "uuid-1", "summary": "t"})
    check("5.2 later handle-keyed events resolve through the alias to the same row",
          suite5.list_agent_sessions()["total"] == 1)
    # a NEW spawn: no uuid until init — folds under the handle, then MIGRATES on the first
    # uuid-carrying event (one session, one row).
    store5.append_event({"kind": "agent_sessions.spawned", "session": "as-bbb", "fork": False,
                         "summary": "new", "name": "fresh", "cwd": "/q"})
    check("5.3 a NEW spawn (uuid unknown yet) folds under the handle",
          any(r["id"] == "as-bbb" for r in suite5.list_agent_sessions()["sessions"]))
    store5.append_event({"kind": "agent_sessions.turn", "session": "as-bbb",
                         "claude_session_id": "uuid-2", "summary": "t"})
    rows = {r["id"]: r for r in suite5.list_agent_sessions()["sessions"]}
    check("5.4 the first uuid-carrying event MIGRATES the handle row onto the uuid (no handle ghost)",
          "as-bbb" not in rows and rows["uuid-2"]["name"] == "fresh"
          and rows["uuid-2"]["state"] == "supervised-live")
    # a CONSULT fork: resume names the ORIGINAL — the fold must NOT alias the fork onto it (T4:
    # the original is never touched).
    store5.append_event({"kind": "agent_sessions.spawned", "session": "as-ccc", "resume": "uuid-1",
                         "fork": True, "summary": "consult", "name": "fork-probe"})
    rows = {r["id"]: r for r in suite5.list_agent_sessions()["sessions"]}
    check("5.5 a CONSULT fork (resume=original, fork=true) does NOT fold onto the original row",
          "as-ccc" in rows and rows["uuid-1"]["name"] != "fork-probe")
    store5.append_event({"kind": "agent_sessions.turn", "session": "as-ccc",
                         "claude_session_id": "uuid-3", "summary": "t"})
    rows = {r["id"]: r for r in suite5.list_agent_sessions()["sessions"]}
    check("5.6 the fork's own uuid lands as its OWN row; the original stays untouched",
          "uuid-3" in rows and "as-ccc" not in rows and rows["uuid-1"]["title"] == "the original")

print(f"\nALL {PASS} CHECKS PASS — agent-session registry: session:// scheme + resolver, whole-record "
      f"store on agent_sessions/, the AGENT_SESSION_OPS fold (records=identity, log=trajectory, "
      f"cross-process convergent, fail-loud filters, counted-never-bricked malformed events), and the "
      f"importer's EXACT title chain (last-occurrence ai-title → last-prompt → first-user-turn → "
      f"untitled+envelope) with sidechain skipping, summarizer marking, idempotent re-runs and the "
      f"live-record guard. The supervisor (event EMITTER) + mailbox/verbs + exporter are other lanes.")
