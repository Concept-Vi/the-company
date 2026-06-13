"""tests/session_supervisor_params_acceptance.py — FAMILY 1 (cost/usage capture) + FAMILY 2
(spawn() parameter widening) unit guarantees, WITHOUT spawning a real claude (lead-only law).

These prove the two backend builds the COVERAGE map named:
  FAMILY 1 (CC-20): the result event's cost+token usage is CAPTURED, not discarded — _extract_usage
    pulls the standard fields; a turn with nothing to report stamps no noise (returns None).
  FAMILY 2 (CC-10/07.2/25.2/.3/18.7/33.4): the cmd-builder threads each new OPTIONAL param into the
    claude command, defaulting to BYTE-IDENTICAL behaviour when unset. Asserted on the built cmd
    list directly — no subprocess, no real turn (the flag "took" requires a live spawn = lead's
    live-verify, honestly out of this lane).

Exit 0 = pass, 1 = a failed check. Run: ./.venv/bin/python tests/session_supervisor_params_acceptance.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# isolate from any operator env that could change defaults under us
os.environ.pop("COMPANY_FABRIC_PERMISSION", None)

from runtime import session_supervisor as ss

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def build(**kw):
    # claude_bin/resume/fork are the always-present args; everything else is the widened set
    base = dict(claude_bin="/stub/claude", resume=None, fork=False)
    base.update(kw)
    return ss.SessionSupervisor._build_spawn_cmd(**base)


def pair_after(cmd, flag):
    # the value token immediately following `flag` in the cmd list (None if flag absent or trailing)
    if flag in cmd:
        i = cmd.index(flag)
        return cmd[i + 1] if i + 1 < len(cmd) else None
    return None


def main():
    # ── FAMILY 2.0 — the byte-identical default (the hard invariant) ──
    default = build()
    EXPECTED_DEFAULT = ["/stub/claude", "-p",
                        "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
                        "--permission-mode", ss.fabric_permission(),
                        "--mcp-config", ss._panel._MCP_CONFIG, "--strict-mcp-config",
                        "--allowedTools", "mcp__company"]
    check("default cmd is byte-identical to the pre-widening construction", default == EXPECTED_DEFAULT)
    check("default carries NO new flags (model/effort/fallback/settings/add-dir/debug/safe/bare/partial)",
          not any(f in default for f in ("--model", "--effort", "--fallback-model", "--settings",
                                         "--add-dir", "--debug", "--safe-mode", "--bare",
                                         "--include-partial-messages")))

    # resume/fork unchanged
    r = build(resume="abc123")
    check("resume appends --resume <id> (unchanged)", pair_after(r, "--resume") == "abc123")
    rf = build(resume="abc123", fork=True)
    check("fork appends --fork-session (unchanged)", "--fork-session" in rf)

    # ── FAMILY 2 — each new param appears in the built cmd ──
    # CC-10 model / effort / fallback
    check("model → --model <v>", pair_after(build(model="opus"), "--model") == "opus")
    check("effort → --effort <v>", pair_after(build(effort="xhigh"), "--effort") == "xhigh")
    check("fallback list → --fallback-model <csv> (Atlas: comma-separated, tried in order)",
          pair_after(build(fallback=["sonnet", "haiku"]), "--fallback-model") == "sonnet,haiku")
    check("fallback string passes through verbatim",
          pair_after(build(fallback="sonnet,haiku"), "--fallback-model") == "sonnet,haiku")

    # CC-07.2 per-spawn permission_mode OVERRIDES the fabric-wide default
    pm = build(permission_mode="acceptEdits")
    check("permission_mode OVERRIDES fabric_permission() on --permission-mode",
          pair_after(pm, "--permission-mode") == "acceptEdits")
    check("unset permission_mode falls back to fabric_permission()",
          pair_after(build(), "--permission-mode") == ss.fabric_permission())

    # CC-25.2 settings  /  CC-25.3 add-dir (repeatable)
    check("settings → --settings <json|path>",
          pair_after(build(settings='{"model":"opus"}'), "--settings") == '{"model":"opus"}')
    multi = build(add_dir=["/a", "/b"])
    check("add_dir list → repeated --add-dir (one flag per dir)",
          multi.count("--add-dir") == 2 and "/a" in multi and "/b" in multi)
    check("add_dir string → one --add-dir",
          build(add_dir="/only").count("--add-dir") == 1)

    # CC-18.7 output_format / include_partial
    of = build(output_format="json")
    check("output_format replaces the stream-json value on --output-format",
          pair_after(of, "--output-format") == "json")
    check("output_format unset keeps --output-format stream-json (reader's parse contract)",
          pair_after(build(), "--output-format") == "stream-json")
    check("include_partial → --include-partial-messages (and --output-format stays stream-json)",
          "--include-partial-messages" in build(include_partial=True)
          and pair_after(build(include_partial=True), "--output-format") == "stream-json")

    # CC-33.4 debug categories / safe-mode / bare
    check("debug string → --debug <categories>",
          pair_after(build(debug="api,hooks"), "--debug") == "api,hooks")
    db = build(debug=True)
    check("debug=True → bare --debug (no category token consumes a real flag)",
          "--debug" in db and (db.index("--debug") == len(db) - 1
                               or db[db.index("--debug") + 1].startswith("--")))
    check("safe_mode → --safe-mode", "--safe-mode" in build(safe_mode=True))
    check("bare → --bare", "--bare" in build(bare=True))

    # the input-format transport invariant is NEVER overridden (injection contract)
    check("--input-format stream-json is fixed even with output_format set",
          pair_after(build(output_format="json"), "--input-format") == "stream-json")

    # ── R1.3 — the SPAWN-FLAG ASSEMBLY TABLE (registry-is-truth for POSTURE, F-FIX-5 steps 5-6) ──
    # The hand SPAWN_FLAGS dict (with its `posture` column) was DELETED; posture is DERIVED from the
    # Mirror-Registry rules (ss._registry_posture). SPAWN_FLAG_ASSEMBLY now holds ONLY the consumer-
    # emission data. Registry sanity: every row declares a flag-name (--… or -p) + a valid assembler
    # kind + teaching text; every row's DERIVED posture is a real posture (never R4 unmatched).
    for k, spec in ss.SPAWN_FLAG_ASSEMBLY.items():
        flag = spec.get("flag", "")
        assert flag.startswith("-") and spec.get("kind") in \
            ("bool", "value", "csv", "repeat", "swap"), f"{k}: bad flag/kind"
        assert spec.get("teach"), f"{k}: assembly row must carry teaching text"
        assert ss._registry_posture(flag) in ("safe", "consent", "locked", "hazard"), (
            f"{k}: derived posture is not a real posture (R4 unmatched — the supervisor would refuse "
            f"a flag it declares it can assemble)")
    check(f"SPAWN_FLAG_ASSEMBLY valid ({len(ss.SPAWN_FLAG_ASSEMBLY)} rows; every row has flag+kind+"
          f"teach + a real DERIVED posture)", True)
    check("the spec-named R1.3 flags are all assembly rows",
          all(k in ss.SPAWN_FLAG_ASSEMBLY for k in ("session_id", "continue", "append_system_prompt",
                                            "allowed_tools", "mcp_config", "tools", "max_turns",
                                            "max_budget_usd", "name", "agents", "json_schema")))
    check("posture is DERIVED from the registry (the deleted SPAWN_FLAGS hand-dict is gone)",
          not hasattr(ss, "SPAWN_FLAGS") and ss._registry_posture("--model") == "locked"
          and ss._registry_posture("--add-dir") == "consent"
          and ss._registry_posture("--session-id") == "safe")

    def apply(flags, consent=False, base=None):
        cmd = list(base) if base else build()
        return ss._apply_spawn_flags(cmd, flags, consent=consent)

    # no flags → byte-identical (the hard invariant extends to the registry path)
    check("flags=None leaves the cmd byte-identical", apply(None) == build())
    # safe value/bool/csv/repeat kinds land as argv
    c = apply({"session_id": "11111111-2222-3333-4444-555555555555", "continue": True,
               "append_system_prompt": "extra rules", "max_turns": 5,
               "setting_sources": ["user", "project"]})
    check("session_id → --session-id <uuid>",
          pair_after(c, "--session-id") == "11111111-2222-3333-4444-555555555555")
    check("continue → --continue", "--continue" in c)
    check("append_system_prompt → --append-system-prompt <text>",
          pair_after(c, "--append-system-prompt") == "extra rules")
    check("max_turns → --max-turns 5", pair_after(c, "--max-turns") == "5")
    check("setting_sources list → --setting-sources csv",
          pair_after(c, "--setting-sources") == "user,project")
    # falsy bool / empty value rows append nothing
    check("falsy bool + empty value append nothing",
          apply({"continue": False, "session_id": ""}) == build())
    # unknown key → teaching refusal naming the registry
    try:
        apply({"warp_drive": 1})
        check("unknown flag refused", False)
    except ss.TeachingRefusal as e:
        check("unknown flag → TeachingRefusal naming the registry", "SPAWN_FLAG_ASSEMBLY" in str(e))
    # locked rows refuse with the dedicated-path teaching
    for k, needle in (("input_format", "injection contract"), ("model", "dedicated body key"),
                      ("dangerously_skip_permissions", "permission_mode"),
                      ("strict_mcp_config", "grounding")):
        try:
            apply({k: "x"})
            check(f"locked {k} refused", False)
        except ss.TeachingRefusal as e:
            check(f"locked {k} → teaching refusal ({needle})", needle in str(e))
    # consent rows refuse WITHOUT consent, teaching the bridge-session path…
    try:
        apply({"allowed_tools": "mcp__company,Bash"})
        check("consent flag without consent refused", False)
    except ss.TeachingRefusal as e:
        check("consent flag w/o consent → teaches /bridge-session + operator_consent",
              "bridge-session" in str(e) and "operator_consent" in str(e))
    # …and APPLY with consent: swap kind replaces the head's value in place
    cc = apply({"allowed_tools": "mcp__company,Bash", "mcp_config": "/tmp/other-mcp.json",
                "tools": "Bash,Edit,Read", "plugin_dir": ["/p1", "/p2"]}, consent=True)
    check("consented allowed_tools SWAPS the floor value (no duplicate flag)",
          pair_after(cc, "--allowedTools") == "mcp__company,Bash"
          and cc.count("--allowedTools") == 1)
    check("consented mcp_config SWAPS the strict company config value",
          pair_after(cc, "--mcp-config") == "/tmp/other-mcp.json" and cc.count("--mcp-config") == 1)
    check("consented tools → --tools <csv>", pair_after(cc, "--tools") == "Bash,Edit,Read")
    check("plugin_dir repeats per item", cc.count("--plugin-dir") == 2)
    # spawn() validates flags BEFORE registering (no half-built record): the validate-only pass
    try:
        ss._apply_spawn_flags([], {"allowed_tools": "X"}, consent=False)
        check("validate-only pass refuses pre-record", False)
    except ss.TeachingRefusal:
        check("validate-only pass refuses pre-record (consent row, no consent)", True)

    # ── FAMILY 1 — _extract_usage captures the result event's cost+usage ──
    full = ss._extract_usage({
        "type": "result", "model": "claude-opus-4-8",
        "usage": {"input_tokens": 1200, "output_tokens": 340,
                  "cache_read_input_tokens": 800, "cache_creation_input_tokens": 64},
        "total_cost_usd": 0.0123,
        "modelUsage": {"claude-opus-4-8": {"costUSD": 0.0123, "contextWindow": 200000}},
    })
    check("usage capture pulls model", full.get("model") == "claude-opus-4-8")
    check("usage capture pulls input/output tokens",
          full.get("input_tokens") == 1200 and full.get("output_tokens") == 340)
    check("usage capture pulls cache read+creation tokens",
          full.get("cache_read_input_tokens") == 800 and full.get("cache_creation_input_tokens") == 64)
    check("usage capture pulls cost_usd from total_cost_usd", full.get("cost_usd") == 0.0123)
    check("usage capture keeps the per-model model_usage passthrough",
          full.get("model_usage", {}).get("claude-opus-4-8", {}).get("costUSD") == 0.0123)

    # cost-only result still captured; model inferred from the single model_usage key
    cost_only = ss._extract_usage({"type": "result", "is_error": False,
                                   "total_cost_usd": 0.5,
                                   "model_usage": {"claude-sonnet-4-6": {"costUSD": 0.5}}})
    check("cost-only result still captured (cost_usd present)", cost_only.get("cost_usd") == 0.5)
    check("model inferred from the lone model_usage key when no top-level model",
          cost_only.get("model") == "claude-sonnet-4-6")

    # alternate cost spelling tolerated
    alt = ss._extract_usage({"type": "result", "cost_usd": 0.9})
    check("alternate cost spelling (cost_usd) tolerated", alt.get("cost_usd") == 0.9)

    # a turn with NOTHING to report stamps no empty noise
    check("no usage/cost/model_usage → returns None (no empty-block noise)",
          ss._extract_usage({"type": "result", "result": "hi", "is_error": False,
                             "num_turns": 1, "session_id": "x"}) is None)


    # ── FAMILY 1 (end-to-end through the real service) — a usage-emitting result event lands its
    # cost+usage on the durable agent_sessions.turn on events.jsonl (the COVERAGE "read over [[events]]"
    # claim). Uses a STUB claude that speaks usage (NO real claude — lead-only law). ──
    import shutil, signal, subprocess, tempfile, time, urllib.request, urllib.error

    USAGE_STUB = r'''#!/usr/bin/env python3
import json, sys, uuid, os
sid = os.environ.get("STUB_SID") or ("stub-" + uuid.uuid4().hex[:8])
print(json.dumps({"type": "system", "subtype": "init", "session_id": sid}), flush=True)
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try: ev = json.loads(line)
    except ValueError: continue
    if ev.get("type") != "user": continue
    print(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "ok"}]}}), flush=True)
    print(json.dumps({"type": "result", "result": "ok", "session_id": sid,
                      "num_turns": 1, "is_error": False, "model": "claude-opus-4-8",
                      "usage": {"input_tokens": 11, "output_tokens": 7, "cache_read_input_tokens": 3},
                      "total_cost_usd": 0.0042,
                      "modelUsage": {"claude-opus-4-8": {"costUSD": 0.0042}}}), flush=True)
'''
    tmp = tempfile.mkdtemp(prefix="supervisor-usage-")
    PORT = 8783
    BASE = f"http://127.0.0.1:{PORT}"
    store_dir = os.path.join(tmp, "store")
    stub = os.path.join(tmp, "stub-claude")
    with open(stub, "w") as f:
        f.write(USAGE_STUB)
    os.chmod(stub, 0o755)
    PY_BIN = os.path.join(ROOT, ".venv", "bin", "python")
    if not os.path.exists(PY_BIN):
        PY_BIN = sys.executable
    env = dict(os.environ, COMPANY_STORE=store_dir, COMPANY_CLAUDE_BIN=stub,
               COMPANY_FABRIC_CONCURRENCY="3", COMPANY_FABRIC_TURN_TIMEOUT_S="30",
               COMPANY_FABRIC_INIT_WAIT_S="5")
    sup = subprocess.Popen([PY_BIN, os.path.join(ROOT, "runtime", "session_supervisor.py"), str(PORT)],
                           env=env, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    def _req(method, path, body=None, timeout=10):
        data = json.dumps(body).encode() if body is not None else None
        r = urllib.request.Request(BASE + path, data=data, method=method,
                                   headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read() or b"{}")

    try:
        t0 = time.time()
        while time.time() - t0 < 15:
            try:
                if _req("GET", "/health", timeout=2)[0] == 200:
                    break
            except Exception:
                pass
            time.sleep(0.1)
        else:
            raise AssertionError("FAIL: usage-e2e supervisor did not answer /health")
        code, r = _req("POST", "/spawn", {"cwd": tmp, "name": "usage-1"})
        assert code == 200, "spawn failed"
        sid = r["session"]["id"]
        _req("POST", "/inject", {"session": sid, "message": "go"})
        turn_ev = None
        t0 = time.time()
        while time.time() - t0 < 10 and turn_ev is None:
            ep = os.path.join(store_dir, "events.jsonl")
            if os.path.exists(ep):
                for ln in open(ep):
                    if not ln.strip():
                        continue
                    e = json.loads(ln)
                    if e.get("kind") == "agent_sessions.turn" and e.get("session") == sid:
                        turn_ev = e
                        break
            if turn_ev is None:
                time.sleep(0.1)
        check("e2e: agent_sessions.turn carries a `usage` block (cost no longer discarded)",
              isinstance(turn_ev, dict) and isinstance(turn_ev.get("usage"), dict))
        u = (turn_ev or {}).get("usage", {})
        check("e2e: turn.usage stamps tokens + cost_usd from the result event",
              u.get("input_tokens") == 11 and u.get("output_tokens") == 7 and u.get("cost_usd") == 0.0042)
        check("e2e: turn.usage stamps the model that ran the turn", u.get("model") == "claude-opus-4-8")
    finally:
        try:
            sup.send_signal(signal.SIGTERM)
            sup.wait(timeout=10)
        except Exception:
            sup.kill()
        shutil.rmtree(tmp, ignore_errors=True)


    print(f"\nPASS — {PASS} checks green (FAMILY 1 cost capture + FAMILY 2 spawn-param cmd-builder; "
          f"no real spawn — flag-took proof is the lead's live-verify).")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"\n{e}")
        sys.exit(1)
