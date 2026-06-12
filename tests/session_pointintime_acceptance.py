"""tests/session_pointintime_acceptance.py — R3.3/R3.4 unit + structural guarantees, WITHOUT
spawning a real claude (lead-only law — the live "context is that-point's" probe is the lead's).

What these prove (the everything-testable-without-claude set):
  R3.3 — build_timeline: real distinct compactions found · payload boundary-copies deduped ·
         BOTH measured post-compact-head styles cut correctly (re-append era + reference era) ·
         segments carry where-along-its-life stats.
  R3.4 — materialize_at_point: the prefix file is structurally LAUNCH-SHAPED — every line parses,
         the tip IS the cut event (remapped), the parentUuid chain walks to a root, ZERO stale
         sessionId/uuid full-field values outside the deliberate forkedFrom provenance, the
         source is byte-untouched, re-materializing with the same new_sid is content-identical
         (deterministic uuid5 remap), and every refusal teaches.

The synthetic fixture mirrors the MEASURED shapes from the real 41-boundary-line session
(7c2c1b74, inspected 2026-06-12): fork-head boundary at line 0 with a re-appended preserved run ·
a later reference-style compaction whose summary is the whole post-compact head · a payload COPY
of the first boundary riding inside the second's preserved run · attachments chained into the
DAG · metadata lines (custom-title, last-prompt, file-history-snapshot) interleaved.

Exit 0 = pass, 1 = a failed check. Run: ./.venv/bin/python tests/session_pointintime_acceptance.py
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from runtime.session_pointintime import (PointError, build_timeline, materialize_at_point,
                                         materialized_registry_record, parse_point, resolve_cut,
                                         verify_materialized)

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


SRC_SID = "aaaaaaaa-1111-2222-3333-444444444444"


def _ev(uuid, parent, type_, ts, **kw):
    e = {"uuid": uuid, "parentUuid": parent, "sessionId": SRC_SID, "type": type_,
         "timestamp": ts, "isSidechain": False}
    e.update(kw)
    return e


def make_fixture(dirpath: str) -> str:
    """The synthetic transcript — line numbers are load-bearing for the checks below."""
    U = [f"00000000-0000-4000-8000-{i:012d}" for i in range(40)]
    B1, S1, P1, P2 = U[1], U[2], U[3], U[4]      # fork-head boundary + summary + 2 preserved
    T1u, T1a, ATT = U[5], U[6], U[7]             # a new turn + attachment
    B2, S2 = U[8], U[9]                          # reference-style compaction
    T2u, T2a = U[10], U[11]                      # post-B2 turn
    lines = [
        # 0: fork-head boundary (re-append era) — preserved = [P1, P2], anchor = S1
        _ev(B1, None, "system", "2026-06-01T10:00:00.000Z", subtype="compact_boundary",
            content="Conversation compacted", compactMetadata={
                "trigger": "manual", "preTokens": 50000, "postTokens": 9000,
                "messagesSummarized": 12,
                "preservedSegment": {"headUuid": P1, "anchorUuid": S1, "tailUuid": P2},
                "preservedMessages": {"anchorUuid": S1, "uuids": [P1, P2]}}),
        # 1: the summary head
        _ev(S1, B1, "user", "2026-06-01T10:00:00.100Z", isCompactSummary=True,
            message={"role": "user", "content": "This session is being continued — summary."}),
        # 2-3: the re-appended preserved run
        _ev(P1, S1, "user", "2026-06-01T09:50:00.000Z",
            message={"role": "user", "content": "preserved user turn"}),
        _ev(P2, P1, "assistant", "2026-06-01T09:50:05.000Z",
            message={"role": "assistant", "content": [{"type": "text", "text": "preserved reply"}]}),
        # 4: metadata line (no uuid)
        {"type": "custom-title", "sessionId": SRC_SID, "title": "fixture session"},
        # 5-7: a genuinely-new turn (closes B1's head) + attachment chained into the DAG
        _ev(T1u, P2, "user", "2026-06-01T10:05:00.000Z",
            message={"role": "user", "content": f"new turn; quoting uuid {P1} in prose"}),
        _ev(T1a, T1u, "assistant", "2026-06-01T10:05:10.000Z",
            message={"role": "assistant", "content": [{"type": "text", "text": "reply"}]}),
        _ev(ATT, T1a, "attachment", "2026-06-01T10:05:11.000Z",
            attachment={"type": "context", "content": [{"id": "ctx1"}]}),
        # 8: file-history-snapshot referencing a message uuid
        {"type": "file-history-snapshot", "messageId": T1u,
         "snapshot": {"messageId": T1u, "trackedFileBackups": {}}},
        # 9: reference-style compaction — preserved REFERENCES earlier lines (T1u/T1a), no re-append
        _ev(B2, ATT, "system", "2026-06-01T11:00:00.000Z", subtype="compact_boundary",
            content="Conversation compacted", compactMetadata={
                "trigger": "auto", "preTokens": 60000, "postTokens": 8000,
                "messagesSummarized": 3,
                "preservedSegment": {"headUuid": T1u, "anchorUuid": S2, "tailUuid": T1a},
                "preservedMessages": {"anchorUuid": S2, "uuids": [T1u, T1a, B1]}}),
        # 10: B2's summary head (NOT in its own preserved list — the measured eee33789 shape)
        _ev(S2, B2, "user", "2026-06-01T11:00:00.100Z", isCompactSummary=True,
            message={"role": "user", "content": "second summary."}),
        # 11: a PAYLOAD COPY of boundary B1 (same uuid, inside B2's preserved run — line-2096 shape)
        _ev(B1, S2, "system", "2026-06-01T10:00:00.000Z", subtype="compact_boundary",
            content="Conversation compacted", compactMetadata={
                "trigger": "manual", "preTokens": 50000, "postTokens": 9000,
                "messagesSummarized": 12,
                "preservedSegment": {"headUuid": P1, "anchorUuid": S1, "tailUuid": P2},
                "preservedMessages": {"anchorUuid": S1, "uuids": [P1, P2]}}),
        # 12-13: re-appended preserved refs (T1u under its B2-era rebase)
        _ev(T1u, B1, "user", "2026-06-01T10:05:00.000Z",
            message={"role": "user", "content": f"new turn; quoting uuid {P1} in prose"}),
        _ev(T1a, T1u, "assistant", "2026-06-01T10:05:10.000Z",
            message={"role": "assistant", "content": [{"type": "text", "text": "reply"}]}),
        # 14: last-prompt metadata with a leafUuid reference
        {"type": "last-prompt", "sessionId": SRC_SID, "leafUuid": T1a, "prompt": "new turn"},
        # 15-16: the post-B2 genuinely-new turn (closes B2's head)
        _ev(T2u, T1a, "user", "2026-06-01T11:10:00.000Z",
            message={"role": "user", "content": "after second compaction"}),
        _ev(T2a, T2u, "assistant", "2026-06-01T11:10:05.000Z",
            message={"role": "assistant", "content": [{"type": "text", "text": "tip reply"}]}),
    ]
    path = os.path.join(dirpath, f"{SRC_SID}.jsonl")
    with open(path, "w") as f:
        for e in lines:
            f.write(json.dumps(e, separators=(",", ":")) + "\n")
    return path


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    tmp = tempfile.mkdtemp(prefix="pointintime-")
    try:
        src = make_fixture(tmp)
        src_sha = sha(src)

        # ── R3.3 — the timeline ──
        tl = build_timeline(src)
        check("timeline finds the 2 REAL compactions (3 boundary lines − 1 payload copy)",
              len(tl["boundaries"]) == 2)
        b1, b2 = tl["boundaries"]
        check("payload boundary-copy (line 11) created NO timeline entry",
              b1["line"] == 0 and b2["line"] == 9)
        check("re-append era cut = end of the preserved run (line 3, P2)",
              b1["resume_cut_line"] == 3 and b1["resume_cut_uuid"].endswith("000000000004"))
        check("reference era cut extends through the re-appended payload (line 13, T1a copy)",
              b2["resume_cut_line"] == 13 and b2["resume_cut_uuid"].endswith("000000000006"))
        check("boundary carries the spec's fields (ts, pre/post tokens, summarized, preserved)",
              b2["ts"] == "2026-06-01T11:00:00.000Z" and b2["pre_tokens"] == 60000
              and b2["post_tokens"] == 8000 and b2["messages_summarized"] == 3
              and b2["preserved_count"] == 4)
        check("segments carry where-along-its-life stats (3 segments, middle has the new turn)",
              len(tl["segments"]) == 3 and tl["segments"][1]["user_msgs"] >= 1)
        check("points are launch-grammar strings", b1["point"] == "compact:1" and b2["point"] == "compact:2")

        # ── the point grammar teaches ──
        for bad, why in (("", "empty"), ("compact:zero", "non-int N"), ("compact:0", "0-based"),
                         ("uuid:nope", "non-uuid"), ("ts:yesterday", "non-iso"), ("banana", "no kind")):
            try:
                parse_point(bad)
                raise AssertionError(f"FAIL: parse_point({bad!r}) should refuse ({why})")
            except PointError:
                pass
        check("parse_point refuses every malformed point with a teaching error", True)
        try:
            resolve_cut(src, parse_point("compact:9"))
            raise AssertionError("FAIL: compact:9 on a 2-compaction session should refuse")
        except PointError as e:
            check("compact:N beyond the timeline refuses, naming what exists", "2" in str(e))
        try:
            resolve_cut(src, parse_point("ts:2020-01-01T00:00:00Z"))
            raise AssertionError("FAIL: ts before session start should refuse")
        except PointError:
            check("ts before the session's first message refuses", True)

        # ── R3.4 — materialize at compact:1 (the re-append era point) ──
        dest = os.path.join(tmp, "dest")
        rep1 = materialize_at_point(src, "compact:1", dest_dir=dest)
        check("materialized file exists, is a NEW file, source dir untouched",
              os.path.exists(rep1["new_path"]) and rep1["new_path"] != src)
        check("cut at compact:1 wrote exactly lines 0..3 (boundary+summary+preserved run)",
              rep1["lines_written"] == 4 and rep1["cut_line"] == 3)
        v1 = verify_materialized(rep1)
        check(f"compact:1 file verifies launch-shaped (tip=cut, chain→root, no stale ids) "
              f"[{v1['checks']}]", v1["ok"])
        check("source byte-untouched after materialization (sha identical)", sha(src) == src_sha)

        # ── materialize at a uuid point (the tip turn) ──
        tip_uuid = "00000000-0000-4000-8000-000000000011"   # T2a (the file tip, line 16)
        rep2 = materialize_at_point(src, f"uuid:{tip_uuid}", dest_dir=dest)
        check("uuid-point cut includes the whole prefix (17 lines)", rep2["lines_written"] == 17)
        v2 = verify_materialized(rep2)
        check(f"uuid-point file verifies launch-shaped [{v2['checks']}]", v2["ok"])
        new_lines = [json.loads(l) for l in open(rep2["new_path"])]
        check("every sessionId field rewritten to the new sid (native-fork transform)",
              all(l.get("sessionId") in (rep2["new_sid"], None) for l in new_lines))
        check("every event carries forkedFrom provenance {source sid, original cut uuid}",
              all(l.get("forkedFrom") == {"sessionId": SRC_SID, "messageUuid": tip_uuid}
                  for l in new_lines if l.get("uuid")))
        prose = next(l for l in new_lines
                     if l.get("type") == "user" and "quoting uuid" in str(l.get("message", {}).get("content")))
        check("a uuid QUOTED IN PROSE is NOT mutated (full-field remap only — fidelity holds)",
              "00000000-0000-4000-8000-000000000003" in prose["message"]["content"])
        fhs = next(l for l in new_lines if l.get("type") == "file-history-snapshot")
        check("file-history-snapshot messageId remapped (full-field value remap reaches metadata)",
              fhs["messageId"] != "00000000-0000-4000-8000-000000000005"
              and fhs["messageId"] == fhs["snapshot"]["messageId"])
        lp = next(l for l in new_lines if l.get("type") == "last-prompt")
        check("last-prompt leafUuid remapped", lp["leafUuid"] != "00000000-0000-4000-8000-000000000006")

        # ── ts point ──
        rep3 = materialize_at_point(src, "ts:2026-06-01T10:06:00Z", dest_dir=dest)
        check("ts-point cuts at the LAST user/assistant at-or-before the moment (line 13 — the "
              "re-appended T1a copy is the latest file position carrying that ts, the richer prefix)",
              rep3["cut_line"] == 13 and rep3["cut_uuid"].endswith("000000000006"))

        # ── determinism + overwrite refusal ──
        fixed = "bbbbbbbb-1111-2222-3333-444444444444"
        d2 = os.path.join(tmp, "det1")
        d3 = os.path.join(tmp, "det2")
        ra = materialize_at_point(src, "compact:2", dest_dir=d2, new_sid=fixed)
        rb = materialize_at_point(src, "compact:2", dest_dir=d3, new_sid=fixed)
        check("same new_sid ⇒ content-identical files (deterministic uuid5 remap)",
              sha(ra["new_path"]) == sha(rb["new_path"]))
        try:
            materialize_at_point(src, "compact:2", dest_dir=d2, new_sid=fixed)
            raise AssertionError("FAIL: overwrite should refuse")
        except PointError:
            check("an existing materialized path REFUSES to be overwritten", True)

        # ── the registry record ──
        rec = materialized_registry_record(
            rep1, {"cwd": "/home/tim", "title": "fixture session", "started": "2026-06-01T09:00:00Z",
                   "project": "-home-tim"}, registered_by="test")
        check("registry record: id=new sid · state=closed · provenance fields present",
              rec["id"] == rep1["new_sid"] and rec["state"] == "closed"
              and rec["materialized_from"] == SRC_SID
              and rec["materialized_at_point"] == "compact:1"
              and rec["jsonl_path"] == rep1["new_path"] and rec["cwd"] == "/home/tim")

        # ── the resume-cwd resolver (the measured drifted-cwd hazard) ──
        from runtime.session_pointintime import encode_project_dir, resume_cwd_for
        realish = os.path.join(tmp, "-home-tim")
        os.makedirs(realish, exist_ok=True)
        fake_jsonl = os.path.join(realish, "x.jsonl")
        open(fake_jsonl, "w").close()
        check("resume_cwd_for picks the candidate that ENCODES to the project dir (drifted "
              "record cwd rejected)",
              resume_cwd_for(fake_jsonl, "/home/tim/vllm-tests", "/home/tim") == "/home/tim")
        check("resume_cwd_for falls back to the naive decode when no candidate fits "
              "(/home/tim exists + re-encodes)",
              resume_cwd_for(fake_jsonl, "/somewhere/else") == "/home/tim")
        unresolvable = os.path.join(tmp, "proj-that-encodes-nothing")
        os.makedirs(unresolvable, exist_ok=True)
        bad_jsonl = os.path.join(unresolvable, "y.jsonl")
        open(bad_jsonl, "w").close()
        try:
            resume_cwd_for(bad_jsonl, "/somewhere/else")
            raise AssertionError("FAIL: unresolvable project dir should refuse")
        except PointError as e:
            check("resume_cwd_for REFUSES-teaching when no cwd can encode to the project dir "
                  "(never a silent wrong-dir spawn)", "cannot resolve" in str(e))
        check("encode_project_dir: '/' and '.' both encode to '-' (measured rule)",
              encode_project_dir("/home/tim/.claude") == "-home-tim--claude")

        # ── adversarial: verify_materialized actually BITES (not a rubber stamp) ──
        bad_path = os.path.join(tmp, "cccccccc-1111-2222-3333-444444444444.jsonl")
        shutil.copyfile(rep1["new_path"], bad_path)
        with open(bad_path, "a") as f:                      # a stale-sid line appended
            f.write(json.dumps({"uuid": "dddddddd-0000-4000-8000-000000000000",
                                "parentUuid": None, "sessionId": SRC_SID, "type": "user",
                                "message": {"role": "user", "content": "x"}}) + "\n")
        vbad = verify_materialized({**rep1, "new_path": bad_path,
                                    "lines_written": rep1["lines_written"] + 1})
        check("verifier FAILS a file carrying a stale source sessionId (teeth, not rubber stamp)",
              not vbad["ok"] and any("stale source sessionId" in p for p in vbad["problems"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ════ FAMILY 2 — the SUPERVISOR at-launch flow, end-to-end through the real service, against
    # a STUB claude (NO real claude — lead-only law; the stub records its argv + answers turns).
    # Proves: wake intent carrying at= → materialize beside the source → registry record with
    # provenance → spawn `--resume <materialized-sid>` in the source's cwd → message injected →
    # reply mail routes back. consult+at fans N INDEPENDENT materializations. ════
    import signal
    import subprocess
    import time
    import urllib.request

    STUB = r'''#!/usr/bin/env python3
import json, os, sys
argv_dir = os.environ.get("STUB_ARGV_DIR")
sid = None
if "--resume" in sys.argv:
    sid = sys.argv[sys.argv.index("--resume") + 1]
if argv_dir:
    with open(os.path.join(argv_dir, f"argv-{os.getpid()}.json"), "w") as f:
        json.dump({"argv": sys.argv, "cwd": os.getcwd()}, f)
print(json.dumps({"type": "system", "subtype": "init", "session_id": sid or "stub-fresh"}), flush=True)
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        ev = json.loads(line)
    except ValueError:
        continue
    if ev.get("type") != "user":
        continue
    print(json.dumps({"type": "assistant", "message": {"content": [
        {"type": "text", "text": "answered from the materialized point"}]}}), flush=True)
    print(json.dumps({"type": "result", "result": "answered from the materialized point",
                      "session_id": sid or "stub-fresh", "num_turns": 1,
                      "is_error": False}), flush=True)
'''
    tmp2 = tempfile.mkdtemp(prefix="pointintime-e2e-")
    PORT = 8786
    BASE = f"http://127.0.0.1:{PORT}"
    sup = None
    try:
        store_dir = os.path.join(tmp2, "store")
        argv_dir = os.path.join(tmp2, "argv")
        os.makedirs(argv_dir)
        # the project dir is NAMED AS THE REAL CATALOG NAMES IT — the encoded cwd ('/' and '.'
        # → '-'): the supervisor's resume_cwd_for VALIDATES candidates by re-encoding against
        # this name, so the fixture must mirror the real layout or the (correct) refusal fires.
        from runtime.session_pointintime import encode_project_dir
        proj = os.path.join(tmp2, encode_project_dir(tmp2))
        os.makedirs(proj)
        src2 = make_fixture(proj)
        src2_sha = sha(src2)

        from store.fs_store import FsStore
        st = FsStore(store_dir)
        st.save_agent_session({"id": SRC_SID, "name": None, "cwd": tmp2, "state": "closed",
                               "title": "fixture session", "jsonl_path": src2,
                               "project": "proj", "schema_ver": 1})

        stub = os.path.join(tmp2, "stub-claude")
        with open(stub, "w") as f:
            f.write(STUB)
        os.chmod(stub, 0o755)
        PY_BIN = os.path.join(ROOT, ".venv", "bin", "python")
        if not os.path.exists(PY_BIN):
            PY_BIN = sys.executable
        env = dict(os.environ, COMPANY_STORE=store_dir, COMPANY_CLAUDE_BIN=stub,
                   STUB_ARGV_DIR=argv_dir, COMPANY_FABRIC_CONCURRENCY="3",
                   COMPANY_FABRIC_TURN_TIMEOUT_S="30", COMPANY_FABRIC_INIT_WAIT_S="5")
        sup = subprocess.Popen(
            [PY_BIN, os.path.join(ROOT, "runtime", "session_supervisor.py"), str(PORT)],
            env=env, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        t0 = time.time()
        while time.time() - t0 < 15:
            try:
                with urllib.request.urlopen(BASE + "/health", timeout=2) as r:
                    if r.status == 200:
                        break
            except Exception:
                pass
            time.sleep(0.1)
        else:
            raise AssertionError("FAIL: at-launch e2e supervisor did not answer /health")

        def _mail(verb_, at_, copies_=1):
            cas = st.put_content("what was the state of the plan at this point?")
            return st.append_agent_mail({"to": f"session://{SRC_SID}",
                                         "from": "session://r3-test-lane", "verb": verb_,
                                         "cas": cas, "at": at_, "copies": copies_})

        def _wait_replies(thread, n, timeout=20):
            t0 = time.time()
            while time.time() - t0 < timeout:
                rows = [r for r in st.agent_mail_since(-1, to="session://r3-test-lane")
                        if r.get("thread") == thread]
                if len(rows) >= n:
                    return rows
                time.sleep(0.2)
            return [r for r in st.agent_mail_since(-1, to="session://r3-test-lane")
                    if r.get("thread") == thread]

        posted = _mail("wake", "compact:1")
        replies = _wait_replies(posted["thread"], 1)
        check("e2e wake@compact:1 → a reply (not an error) routes back to the sender",
              len(replies) >= 1 and replies[0].get("verb") == "reply",
              )
        body0 = st.get_content(replies[0]["cas"]) if replies else {}
        body0 = body0.get("text", "") if isinstance(body0, dict) else str(body0)
        check("e2e the reply carries the stub session's turn text",
              "answered from the materialized point" in body0)
        mats = [r for r in (st.load_agent_session(x) for x in st.list_agent_sessions())
                if r and r.get("materialized_from") == SRC_SID]
        check("e2e a registry record exists with materialized_from + at + cut provenance",
              len(mats) == 1 and mats[0]["materialized_at_point"] == "compact:1"
              and mats[0].get("materialized_cut_uuid"))
        new_sid_1 = mats[0]["id"]
        check("e2e the materialized file sits BESIDE the source (same project dir)",
              os.path.dirname(mats[0]["jsonl_path"]) == proj
              and os.path.exists(mats[0]["jsonl_path"]))
        argvs = []
        for fn in os.listdir(argv_dir):
            argvs.append(json.load(open(os.path.join(argv_dir, fn))))
        check("e2e the stub was spawned with --resume <MATERIALIZED sid> (never the source sid)",
              any("--resume" in a["argv"] and new_sid_1 in a["argv"] for a in argvs)
              and not any(SRC_SID in a["argv"] for a in argvs))
        check("e2e the spawn ran in the source session's cwd", any(a["cwd"] == tmp2 for a in argvs))
        check("e2e the SOURCE transcript is byte-untouched after the whole flow",
              sha(src2) == src2_sha)

        posted2 = _mail("consult", "compact:2", copies_=2)
        replies2 = _wait_replies(posted2["thread"], 2)
        check("e2e consult@compact:2 copies=2 → TWO replies aggregate under one thread",
              len(replies2) >= 2)
        mats2 = [r for r in (st.load_agent_session(x) for x in st.list_agent_sessions())
                 if r and r.get("materialized_from") == SRC_SID
                 and r.get("materialized_at_point") == "compact:2"]
        check("e2e consult fan = 2 INDEPENDENT materializations (2 files, 2 records)",
              len(mats2) == 2
              and len({m["jsonl_path"] for m in mats2}) == 2
              and all(os.path.exists(m["jsonl_path"]) for m in mats2))

        bad = _mail("wake", "compact:99")
        badr = _wait_replies(bad["thread"], 1)
        badbody = st.get_content(badr[0]["cas"]) if badr else {}
        badbody = badbody.get("text", "") if isinstance(badbody, dict) else str(badbody)
        check("e2e a bad point (compact:99) returns a TEACHING error reply, never silence",
              len(badr) >= 1 and badr[0].get("verb") == "error" and "compact" in badbody)
    finally:
        if sup is not None:
            try:
                sup.send_signal(signal.SIGTERM)
                sup.wait(timeout=10)
            except Exception:
                sup.kill()
        shutil.rmtree(tmp2, ignore_errors=True)

    print(f"\nPASS — {PASS} checks green (R3.3 timeline + R3.4 materializer + the supervisor "
          f"at-launch flow vs the stub binary; no real claude spawned — the live resume-at-point "
          f"probe is the lead's, marked 🟡 in the ops doc).")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"\n{e}")
        sys.exit(1)
