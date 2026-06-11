"""agent_sessions_exporter_acceptance — the FILTER LAW has teeth (Session Fabric F1.4, guide §E).

Proves by execution, on synthetic fixtures (the real catalog is READ-ONLY and never a test
dependency), that ops/agent_sessions_exporter.py:
  • KEEPS user+assistant text, the ai-title, one-line tool TRACES;
  • STRIPS tool_result bodies AND the duplicated top-level toolUseResult field, tool_use
    input bodies, attachment lines, bookkeeping line types, noise-prefix user texts
    (<system-reminder, Caveat:, <command-*, [Request interrupted, …), isMeta lines,
    thinking blocks (default OFF);
  • REDACTS secret patterns in everything kept (api keys, JWTs, AWS, GitHub, assignments)
    — including the subagent-rollup heading (a real leak vector found in review);
  • resolves the title via the fallback chain ai-title → last-prompt → first-user-turn →
    untitled (last ai-title occurrence wins — they are tail-heavy in the real corpus);
  • honours the QUIESCE law (fresh-mtime sessions skipped) and is IDEMPOTENT
    (same jsonl → no rewrite on the second run);
  • never writes under the source catalog (read-only law).

Run: ./.venv/bin/python tests/agent_sessions_exporter_acceptance.py
"""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ops"))

import agent_sessions_exporter as ex

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}{detail}")


def _line(**kw):
    return json.dumps(kw) + "\n"


def build_fixture(root):
    """One project dir with one rich main session + a subagent + a stub."""
    proj = root / "-home-tim-testproj"
    proj.mkdir(parents=True)
    sid = "11111111-2222-3333-4444-555555555555"
    main = proj / f"{sid}.jsonl"
    env = dict(sessionId=sid, cwd="/home/tim/testproj", gitBranch="main",
               version="2.1.170", timestamp="2026-06-11T10:00:00Z")
    lines = []
    # noise / bookkeeping
    lines.append(_line(type="queue-operation", op="enqueue"))
    lines.append(_line(type="file-history-snapshot", snapshot="HUGE_SNAPSHOT_NOISE"))
    lines.append(_line(type="permission-mode", mode="default"))
    lines.append(_line(type="attachment", content="ATTACHMENT_NOISE_BODY"))
    # noise-prefix user texts + isMeta
    lines.append(_line(type="user", message={"content": "<system-reminder>SR_NOISE</system-reminder>"}, **env))
    lines.append(_line(type="user", message={"content": "Caveat: CAVEAT_NOISE"}, **env))
    lines.append(_line(type="user", message={"content": "<command-name>/foo</command-name>"}, **env))
    lines.append(_line(type="user", message={"content": "[Request interrupted by user]"}, **env))
    lines.append(_line(type="user", isMeta=True, message={"content": "META_NOISE"}, **env))
    # real user turn with a pasted secret (conversation-text redaction)
    lines.append(_line(type="user", uuid="u-1",
                       message={"content": "Deploy with key sk-ABCDEFGHIJKLMNOPQRSTUVWX please"}, **env))
    # assistant: thinking + text + tool_use (body must die, trace must live)
    lines.append(_line(type="assistant", message={"content": [
        {"type": "thinking", "thinking": "THOUGHT_PRIVATE_NOISE"},
        {"type": "text", "text": "Deploying now with AKIAABCDEFGHIJKLMNOP inside."},
        {"type": "tool_use", "name": "Bash",
         "input": {"command": "git push origin main",
                   "huge_body": "TOOL_USE_BODY_NOISE " * 50}},
    ]}, **env)
    )
    # user line carrying tool_result block + duplicated top-level toolUseResult (secret carriers)
    lines.append(_line(type="user",
                       toolUseResult={"stdout": "TOPLEVEL_TOOLUSERESULT_SECRET"},
                       message={"content": [
                           {"type": "tool_result", "content": "TOOL_RESULT_BODY_SECRET"}]},
                       **env))
    # closing assistant text + assignment-style secret + a JWT
    lines.append(_line(type="assistant", message={"content": [
        {"type": "text",
         "text": "Done. api_key = abcdefghijklmnop1234 and token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload"}]},
        **env))
    # titles: two ai-title lines — LAST occurrence must win
    lines.append(_line(type="ai-title", aiTitle="Early Title", sessionId=sid))
    lines.append(_line(type="ai-title", aiTitle="Final Winning Title", sessionId=sid))
    lines.append(_line(type="last-prompt", lastPrompt="the last prompt text", sessionId=sid))
    main.write_text("".join(lines), encoding="utf-8")

    # subagent: > 2KB, first line carries parent sessionId; prompt holds a secret (heading redaction)
    agent = proj / "agent-deadbeef.jsonl"
    pad = "x" * 2200
    agent.write_text(
        _line(type="user", sessionId=sid,
              message={"content": f"Sub task with sk-SUBPROMPTSECRETKEY12345 {pad}"})
        + _line(type="assistant", sessionId=sid,
                message={"content": [{"type": "text", "text": "SUBAGENT_FINAL_ANSWER"}]}),
        encoding="utf-8")
    # stub subagent: < 2KB → skipped
    stub = proj / "agent-cafebabe.jsonl"
    stub.write_text(_line(type="user", sessionId=sid, message={"content": "warmup"}), encoding="utf-8")

    # second session: NO titles at all → first-user-turn fallback
    sid2 = "66666666-7777-8888-9999-000000000000"
    (proj / f"{sid2}.jsonl").write_text(
        _line(type="user", sessionId=sid2, cwd="/home/tim/testproj",
              timestamp="2026-06-11T11:00:00Z",
              message={"content": "fix the flaky watcher debounce in scanner"})
        + _line(type="assistant", sessionId=sid2, timestamp="2026-06-11T11:00:05Z",
                message={"content": [{"type": "text", "text": "On it."}]}),
        encoding="utf-8")
    return proj, sid, sid2


def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        source = root / "projects"
        dest = root / "out"
        proj, sid, sid2 = build_fixture(source)

        # age every source file past the quiesce window
        old = time.time() - 3600
        src_snapshot = {}
        for p in sorted(proj.iterdir()):
            os.utime(p, (old, old))
            src_snapshot[p.name] = (p.stat().st_size, p.stat().st_mtime)

        print("\n— run 1 (real quiesce window) —")
        rc = ex.main(["--source", str(source), "--dest", str(dest)])
        check("run 1 exits 0 (no failures)", rc == 0, f" rc={rc}")

        md_path = dest / proj.name / f"{sid}.md"
        check("one md per session exists", md_path.exists(), f" missing {md_path}")
        md = md_path.read_text(encoding="utf-8") if md_path.exists() else ""

        # ---- KEEP side
        check("user text kept", "Deploy with key" in md)
        check("assistant text kept", "Deploying now" in md)
        check("tool TRACE kept (name + key arg, one line)",
              "> tools: Bash(git push origin main)" in md, f"\n{md[:400]}")
        check("title = LAST ai-title occurrence", 'title: "Final Winning Title"' in md)
        check("frontmatter carries id/cwd/dates", f"session_id: {sid}" in md
              and 'cwd: "/home/tim/testproj"' in md and "started: 2026-06-11T10:00:00Z" in md)
        check("subagent final text rolled up", "SUBAGENT_FINAL_ANSWER" in md)

        # ---- STRIP side (the law, exact)
        for marker in ["TOOL_RESULT_BODY_SECRET", "TOPLEVEL_TOOLUSERESULT_SECRET",
                       "TOOL_USE_BODY_NOISE", "THOUGHT_PRIVATE_NOISE",
                       "ATTACHMENT_NOISE_BODY", "HUGE_SNAPSHOT_NOISE",
                       "SR_NOISE", "CAVEAT_NOISE", "META_NOISE",
                       "<system-reminder", "Caveat:", "<command-name",
                       "[Request interrupted"]:
            check(f"stripped: {marker}", marker not in md)

        # ---- redaction pass over everything kept
        check("pasted sk- key redacted in user text", "sk-ABCDEFGHIJKLMNOPQRSTUVWX" not in md
              and "[redacted:api-key]" in md)
        check("AWS key redacted in assistant text", "AKIAABCDEFGHIJKLMNOP" not in md
              and "[redacted:aws-key]" in md)
        check("JWT redacted", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in md
              and "[redacted:jwt]" in md)
        check("assignment-form secret redacted", "abcdefghijklmnop1234" not in md
              and "[redacted:assignment]" in md)
        check("subagent HEADING redacted (the reviewed leak vector)",
              "sk-SUBPROMPTSECRETKEY12345" not in md)
        check("stub subagent (<2KB) skipped", "warmup" not in md)

        # ---- title fallback chain
        md2_path = dest / proj.name / f"{sid2}.md"
        md2 = md2_path.read_text(encoding="utf-8") if md2_path.exists() else ""
        check("no-title session falls back to first user turn",
              "fix the flaky watcher debounce" in md2 and "title_source: first-user-turn" in md2)

        # ---- read-only on the catalog
        post = {p.name: (p.stat().st_size, p.stat().st_mtime) for p in sorted(proj.iterdir())}
        check("source catalog untouched (read-only law)", post == src_snapshot)
        check("no files added under source", set(post) == set(src_snapshot))

        # ---- idempotence: second run rewrites nothing
        before = md_path.stat().st_mtime_ns
        print("\n— run 2 (idempotence) —")
        rc2 = ex.main(["--source", str(source), "--dest", str(dest)])
        check("run 2 exits 0", rc2 == 0)
        check("second run does not rewrite the md", md_path.stat().st_mtime_ns == before)

        # ---- quiesce law: a fresh-mtime session is skipped
        live = proj / "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee.jsonl"
        live.write_text(_line(type="user", sessionId="live",
                              message={"content": "still typing"}), encoding="utf-8")
        print("\n— run 3 (quiesce) —")
        rc3 = ex.main(["--source", str(source), "--dest", str(dest)])
        check("run 3 exits 0", rc3 == 0)
        check("live (fresh-mtime) session NOT exported",
              not (dest / proj.name / "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee.md").exists())

        # ---- thinking flag honoured (config toggle, default OFF proven above)
        print("\n— run 4 (--include-thinking) —")
        rc4 = ex.main(["--source", str(source), "--dest", str(dest),
                       "--force", "--include-thinking"])
        md_t = md_path.read_text(encoding="utf-8")
        check("run 4 exits 0", rc4 == 0)
        check("--include-thinking keeps thinking blocks", "THOUGHT_PRIVATE_NOISE" in md_t)

    print(f"\n{'PASS' if FAIL == 0 else 'FAIL'} — {PASS} passed, {FAIL} failed")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
