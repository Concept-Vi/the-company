"""tests/render_declaration_acceptance.py — the R1.2 render-declaration layer, proven by use.

What this proves (Session Fabric R1.2 — 'every emit type mapped, declaration consumed to
actually render each, no emit type unhandled/silently dropped'):

  A. the registry is TYPED CONTENT: loads + validates against its closed vocabularies; an
     invalid entry fails LOUD at load (RegistryInvalid), never a half-valid registry;
  B. the dispatch matrix: every documented stream shape (init, compact_boundary, status,
     api_retry, thinking_tokens, hooks, tasks, permission_denied, local_command_output,
     stream_event inner family, result success+error, tool_progress, tool_use_summary,
     rate_limit_event, auth_status, prompt_suggestion, assistant blocks incl.
     AskUserQuestion, user tool_result, attachments, transcript sidecar rows, supervisor
     wire events) derives the right render_key;
  C. REAL DATA, full coverage: the three REAL T2 stream captures (~/xsession-tests — real
     claude stdout) and a real-transcript sample declare 100% — zero undeclared — and every
     declared event RENDERS through the consumer (ops/render_declared_stream.render_one),
     which dispatches on declaration content only;
  D. the LOUD undeclared path: a bogus emit type still renders (UnknownEvent), is marked
     undeclared, and fires the drop hook — never None, never an exception, never silent;
     a family-fallback hit renders AND fires the soft drop;
  E. SERVICE-LEVEL: the real supervisor service (stub claude binary — lead-only law: this
     lane never spawns real claude) fans a `declared` event for EVERY stub emit on /watch,
     including an unknown probe type, and the unknown lands as agent_sessions.render_drop
     on events.jsonl (the registry-gap sensor operating for real).

Run: ./.venv/bin/python tests/render_declaration_acceptance.py     (exit 0 pass · 1 fail)
"""
from __future__ import annotations

import glob
import json
import os
import random
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from runtime import render_declaration as rd
from ops.render_declared_stream import render_one, render_file

PY = os.path.join(ROOT, ".venv", "bin", "python")
if not os.path.exists(PY):
    PY = sys.executable
PORT = 8786                      # test-only port (supervisor acceptance uses 8779; live is 8771)
BASE = f"http://127.0.0.1:{PORT}"
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# ── A. registry validity ──────────────────────────────────────────────────────────────────
def test_registry():
    reg = rd.load_registry(force=True)
    check("registry loads + validates (typed content, closed vocab)", bool(reg["declarations"]))
    check("registry has the documented core keys",
          all(k in reg["declarations"] for k in (
              "system/init", "system/compact_boundary", "assistant", "assistant.content.text",
              "assistant.content.tool_use", "user", "user.content.tool_result",
              "stream_event/content_block_delta.text_delta", "result/success", "result/*",
              "rate_limit_event", "system/thinking_tokens", "attachment/hook_success",
              "system/*", "attachment/*")))
    # an INVALID registry fails loud
    bad = {"vocab": reg["vocab"],
           "declarations": {"x": {"surface": "stream", "placement": "NOT-A-PLACE",
                                  "component": "None", "is_terminal": False,
                                  "blocks_execution": False, "evidence": "inferred",
                                  "field_map": {}, "summary": "bad"}}}
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump(bad, tmp); tmp.close()
    try:
        rd.load_registry(tmp.name, force=True)
        check("invalid registry fails loud", False)
    except rd.RegistryInvalid as e:
        check("invalid registry fails loud (names the entry + the vocab)",
              "NOT-A-PLACE" in str(e) and "x" in str(e))
    finally:
        os.unlink(tmp.name)
        rd.load_registry(force=True)     # restore the real registry in the cache


# ── B. the dispatch matrix ───────────────────────────────────────────────────────────────
MATRIX = [
    ({"type": "system", "subtype": "init", "session_id": "s", "model": "m"}, "system/init"),
    ({"type": "system", "subtype": "compact_boundary",
      "compact_metadata": {"trigger": "auto", "pre_tokens": 5}}, "system/compact_boundary"),
    ({"type": "system", "subtype": "status", "status": "compacting"}, "system/status"),
    ({"type": "system", "subtype": "api_retry", "attempt": 2}, "system/api_retry"),
    ({"type": "system", "subtype": "thinking_tokens", "estimated_tokens": 9}, "system/thinking_tokens"),
    ({"type": "system", "subtype": "hook_started", "hook_id": "h"}, "system/hook_started"),
    ({"type": "system", "subtype": "hook_progress", "hook_id": "h"}, "system/hook_progress"),
    ({"type": "system", "subtype": "hook_response", "hook_id": "h", "outcome": "success"}, "system/hook_response"),
    ({"type": "system", "subtype": "permission_denied", "tool_name": "Bash"}, "system/permission_denied"),
    ({"type": "system", "subtype": "task_started", "task_id": "t"}, "system/task_started"),
    ({"type": "system", "subtype": "task_progress", "task_id": "t"}, "system/task_progress"),
    ({"type": "system", "subtype": "task_updated", "task_id": "t", "patch": {}}, "system/task_updated"),
    ({"type": "system", "subtype": "task_notification", "task_id": "t"}, "system/task_notification"),
    ({"type": "system", "subtype": "local_command_output", "content": "x"}, "system/local_command_output"),
    ({"type": "system", "subtype": "commands_changed", "commands": []}, "system/commands_changed"),
    ({"type": "system", "subtype": "files_persisted", "files": []}, "system/files_persisted"),
    ({"type": "system", "subtype": "plugin_install", "status": "started"}, "system/plugin_install"),
    ({"type": "system", "subtype": "away_summary", "content": "x"}, "system/away_summary"),
    ({"type": "system", "subtype": "turn_duration", "durationMs": 5}, "system/turn_duration"),
    ({"type": "system", "subtype": "some_future_subtype", "content": "x"}, "system/*"),
    ({"type": "stream_event", "event": {"type": "message_start", "message": {"id": "m"}}},
     "stream_event/message_start"),
    ({"type": "stream_event", "event": {"type": "content_block_start", "index": 0,
                                        "content_block": {"type": "text"}}},
     "stream_event/content_block_start.text"),
    ({"type": "stream_event", "event": {"type": "content_block_start", "index": 0,
                                        "content_block": {"type": "tool_use", "name": "Read"}}},
     "stream_event/content_block_start.tool_use"),
    ({"type": "stream_event", "event": {"type": "content_block_delta", "index": 1,
                                        "delta": {"type": "text_delta", "text": "hi"}}},
     "stream_event/content_block_delta.text_delta"),
    ({"type": "stream_event", "event": {"type": "content_block_delta", "index": 0,
                                        "delta": {"type": "thinking_delta", "thinking": "…"}}},
     "stream_event/content_block_delta.thinking_delta"),
    ({"type": "stream_event", "event": {"type": "content_block_delta", "index": 2,
                                        "delta": {"type": "input_json_delta", "partial_json": "{"}}},
     "stream_event/content_block_delta.input_json_delta"),
    ({"type": "stream_event", "event": {"type": "content_block_stop", "index": 2}},
     "stream_event/content_block_stop"),
    ({"type": "stream_event", "event": {"type": "message_delta", "delta": {"stop_reason": "end_turn"}}},
     "stream_event/message_delta"),
    ({"type": "stream_event", "event": {"type": "message_stop"}}, "stream_event/message_stop"),
    ({"type": "stream_event", "event": {"type": "weird_future_inner"}}, "stream_event/*"),
    ({"type": "result", "subtype": "success", "result": "ok"}, "result/success"),
    ({"type": "result", "subtype": "error_max_turns", "is_error": True, "errors": ["x"]}, "result/*"),
    ({"type": "result", "subtype": "error_during_execution", "is_error": True}, "result/*"),
    ({"type": "tool_progress", "tool_use_id": "t", "elapsed_time_seconds": 1.0}, "tool_progress"),
    ({"type": "tool_use_summary", "summary": "s", "preceding_tool_use_ids": []}, "tool_use_summary"),
    ({"type": "rate_limit_event", "rate_limit_info": {"status": "allowed"}}, "rate_limit_event"),
    ({"type": "auth_status", "isAuthenticating": True}, "auth_status"),
    ({"type": "prompt_suggestion", "suggestion": "next"}, "prompt_suggestion"),
    ({"type": "attachment", "attachment": {"type": "hook_success", "hookName": "h"}},
     "attachment/hook_success"),
    ({"type": "attachment", "attachment": {"type": "brand_new_kind"}}, "attachment/*"),
    ({"type": "ai-title", "aiTitle": "T", "sessionId": "s"}, "ai-title"),
    ({"type": "custom-title", "customTitle": "T", "sessionId": "s"}, "custom-title"),
    ({"type": "worktree-state", "worktreeSession": {"worktreePath": "/x"}}, "worktree-state"),
    ({"type": "file-history-snapshot", "messageId": "m"}, "file-history-snapshot"),
    ({"type": "queue-operation", "operation": "dequeue"}, "queue-operation"),
    ({"type": "injected", "source": "http", "chars": 4}, "injected"),
    ({"type": "keepalive"}, "keepalive"),
    ({"type": "closed", "reason": "teardown"}, "closed"),
]


def test_matrix():
    ok = True
    for ev, want in MATRIX:
        dec = rd.declare(ev)
        if dec["render_key"] != want:
            print(f"    MISMATCH: {ev.get('type')}/{ev.get('subtype')} -> "
                  f"{dec['render_key']} (wanted {want})")
            ok = False
        if not render_one(dec):
            print(f"    NO RENDER for {want}")
            ok = False
    check(f"dispatch matrix: {len(MATRIX)} documented shapes derive the right key + render", ok)
    # content-block sub-dispatch incl. the AskUserQuestion nuance (blocks_execution)
    dec = rd.declare({"type": "assistant", "message": {"model": "m", "content": [
        {"type": "text", "text": "hello"},
        {"type": "thinking", "thinking": "…", "signature": "sig"},
        {"type": "tool_use", "id": "t1", "name": "Read", "input": {"file_path": "/x"}},
        {"type": "tool_use", "id": "t2", "name": "AskUserQuestion",
         "input": {"questions": [{"question": "?", "options": []}]}},
    ]}})
    keys = [b["render_key"] for b in dec["blocks"]]
    check("assistant blocks sub-dispatch (text/thinking/tool_use + AskUserQuestion nuance)",
          keys == ["assistant.content.text", "assistant.content.thinking",
                   "assistant.content.tool_use", "assistant.content.tool_use.AskUserQuestion"]
          and dec["blocks"][3].get("blocks_execution") is True)
    dec = rd.declare({"type": "user", "message": {"content": [
        {"type": "tool_result", "tool_use_id": "t1", "content": "out"}]}})
    check("user tool_result block targets the tool card by id",
          dec["blocks"][0]["render_key"] == "user.content.tool_result"
          and dec["blocks"][0].get("update_target") == "tool-by-id")
    # honest truncation: a >64KB field is capped WITH a visible marker
    dec = rd.declare({"type": "system", "subtype": "away_summary", "content": "x" * 70000})
    check("long field capped LOUDLY (value capped + __truncated marker, never silent)",
          len(dec["fields"]["content"]) == rd.FIELD_CAP
          and dec["fields"].get("content__truncated") is True)


# ── C. real data, full coverage ──────────────────────────────────────────────────────────
def test_real_captures():
    captures = [os.path.expanduser(p) for p in (
        "~/xsession-tests/t1/out.jsonl", "~/xsession-tests/t1/out2.jsonl",
        "~/xsession-tests/channel-hello/out.jsonl")]
    captures = [p for p in captures if os.path.exists(p)]
    check("the real T2 stream captures exist (real claude stdout)", len(captures) == 3)
    for p in captures:
        t = render_file(p, quiet=True)
        check(f"REAL stream {os.path.basename(os.path.dirname(p))}/{os.path.basename(p)}: "
              f"{t['events']} events, 100% declared + rendered, 0 undeclared",
              t["events"] > 0 and t["rendered"] == t["events"] and not t["undeclared"])
    # a deterministic real-transcript sample (the full-corpus scan is ops --scan-corpus;
    # run for real 2026-06-13: 2,514 files · 705k+ events · ZERO undeclared)
    files = sorted(glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")))
    if files:
        rnd = random.Random(11)         # fixed seed — deterministic sample
        sample = rnd.sample(files, min(25, len(files)))
        und = []
        n = 0
        for fp in sample:
            t = render_file(fp, quiet=True)
            n += t["events"]
            und += t["undeclared"]
        check(f"real-transcript sample (25 files · {n} events): zero undeclared", not und)


# ── D. the loud undeclared path ──────────────────────────────────────────────────────────
def test_undeclared():
    drops = []
    rd.on_drop(drops.append)
    dec = rd.declare({"type": "completely_unknown_emit", "x": 1})
    check("unknown emit still RENDERS (UnknownEvent, undeclared=true) — never dropped",
          dec.get("undeclared") is True and dec["component"] == "UnknownEvent"
          and bool(render_one(dec)))
    check("the drop hook fired with the gap record",
          any(d.get("kind") == "undeclared" and "completely_unknown_emit" in d.get("render_key", "")
              for d in drops))
    drops.clear()
    dec = rd.declare({"type": "system", "subtype": "never_seen_before", "content": "x"})
    check("family-fallback renders as declared AND fires the soft drop (registry sensor)",
          dec["render_key"] == "system/*" and dec.get("family_fallback") is True
          and any(d.get("kind") == "family-fallback" for d in drops))
    rd._DROP_HOOKS.remove(drops.append) if drops.append in rd._DROP_HOOKS else None


# ── E. service-level: the supervisor fans declared events for real ───────────────────────
RICH_STUB = r'''#!/usr/bin/env python3
import json, sys
sid = "stub-declared-1"
print(json.dumps({"type": "system", "subtype": "init", "session_id": sid}), flush=True)
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
    # the rich emit set: partials, thinking ticks, hooks, a tool call, an UNKNOWN probe, result
    print(json.dumps({"type": "system", "subtype": "thinking_tokens", "estimated_tokens": 7}), flush=True)
    print(json.dumps({"type": "stream_event", "event": {"type": "message_start", "message": {"id": "m1"}}}), flush=True)
    print(json.dumps({"type": "stream_event", "event": {"type": "content_block_delta", "index": 0,
                      "delta": {"type": "text_delta", "text": "par"}}}), flush=True)
    print(json.dumps({"type": "system", "subtype": "hook_started", "hook_id": "h1",
                      "hook_name": "PreToolUse:Bash", "hook_event": "PreToolUse"}), flush=True)
    print(json.dumps({"type": "system", "subtype": "hook_response", "hook_id": "h1",
                      "outcome": "success", "exit_code": 0}), flush=True)
    print(json.dumps({"type": "assistant", "message": {"model": "stub", "content": [
        {"type": "text", "text": "declared!"},
        {"type": "tool_use", "id": "t1", "name": "Read", "input": {"file_path": "/x"}}]}}), flush=True)
    print(json.dumps({"type": "totally_unknown_probe", "payload": 1}), flush=True)
    print(json.dumps({"type": "rate_limit_event", "rate_limit_info": {"status": "allowed"}}), flush=True)
    print(json.dumps({"type": "result", "subtype": "success", "result": "declared!",
                      "session_id": sid, "num_turns": 1, "is_error": False}), flush=True)
'''


def _req(method, path, body=None, timeout=10):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method,
                               headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        return resp.status, json.loads(resp.read() or b"{}")


def test_service():
    tmp = tempfile.mkdtemp(prefix="render-decl-accept-")
    store_dir = os.path.join(tmp, "store")
    stub = os.path.join(tmp, "stub-claude")
    with open(stub, "w") as f:
        f.write(RICH_STUB)
    os.chmod(stub, 0o755)
    env = dict(os.environ, COMPANY_STORE=store_dir, COMPANY_CLAUDE_BIN=stub,
               COMPANY_FABRIC_CONCURRENCY="2", COMPANY_FABRIC_TURN_TIMEOUT_S="30",
               COMPANY_FABRIC_INIT_WAIT_S="5")
    sup = subprocess.Popen([PY, os.path.join(ROOT, "runtime", "session_supervisor.py"), str(PORT)],
                           env=env, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True)
    try:
        t0 = time.time()
        while time.time() - t0 < 15:
            try:
                _req("GET", "/health")
                break
            except Exception:
                time.sleep(0.2)
        code, r = _req("POST", "/spawn", {"cwd": tmp, "name": "decl"})
        sid = r["session"]["id"]
        code, r = _req("POST", "/inject", {"session": sid, "message": "go"})
        t0 = time.time()
        while time.time() - t0 < 15:
            code, r = _req("GET", "/sessions")
            rec = [s for s in r["sessions"] if s["id"] == sid][0]
            if rec["turns"] == 1:
                break
            time.sleep(0.2)
        check("service: the rich stub turn completed", rec["turns"] == 1)
        # read the watch stream's replay — the declared events must be there for EVERY emit
        req = urllib.request.Request(f"{BASE}/watch?session={sid}")
        declared = []
        with urllib.request.urlopen(req, timeout=10) as resp:
            t0 = time.time()
            for raw in resp:
                ev = json.loads(raw)
                if ev.get("type") == "declared":
                    declared.append(ev)
                if ev.get("type") == "done" or time.time() - t0 > 10:
                    break
        keys = [d.get("render_key") for d in declared]
        for want in ("system/init", "system/thinking_tokens", "stream_event/message_start",
                     "stream_event/content_block_delta.text_delta", "system/hook_started",
                     "system/hook_response", "assistant", "rate_limit_event", "result/success",
                     "undeclared/totally_unknown_probe"):
            check(f"watch stream carries declared {want}", want in keys)
        a = [d for d in declared if d.get("render_key") == "assistant"][0]
        check("declared assistant carries its sub-dispatched blocks on the wire",
              [b["render_key"] for b in a.get("blocks", [])]
              == ["assistant.content.text", "assistant.content.tool_use"])
        u = [d for d in declared if d.get("undeclared")][0]
        check("the unknown probe is RENDERED-loud on the wire (undeclared=true, UnknownEvent)",
              u["component"] == "UnknownEvent")
        # the registry-gap sensor: agent_sessions.render_drop landed on events.jsonl
        ev_path = os.path.join(store_dir, "events.jsonl")
        t0 = time.time()
        found = False
        while time.time() - t0 < 10 and not found:
            if os.path.exists(ev_path):
                with open(ev_path) as f:
                    found = any(json.loads(l).get("kind") == "agent_sessions.render_drop"
                                for l in f if l.strip())
            time.sleep(0.2)
        check("agent_sessions.render_drop recorded for the unknown emit (gap-pressure sensor)", found)
        _req("POST", "/teardown", {"session": sid})
    finally:
        sup.terminate()
        try:
            sup.wait(timeout=5)
        except subprocess.TimeoutExpired:
            sup.kill()


def main():
    test_registry()
    test_matrix()
    test_real_captures()
    test_undeclared()
    test_service()
    print(f"\nPASS — {PASS} checks green (render-declaration layer R1.2)")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(str(e))
        sys.exit(1)
