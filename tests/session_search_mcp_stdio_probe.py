"""tests/session_search_mcp_stdio_probe.py — the AGENT-NATIVE chain proof (R4.4 + R4.5).

This probe IS an MCP agent: a programmatic client that spawns the REAL company MCP server
(mcp_face/server.py, the same argv Claude Code's .claude.json uses) and speaks REAL newline-delimited
JSON-RPC over stdio — initialize → tools/list → tools/call. No stubs, no in-process shortcuts: this
is the exact path any non-Tim agent walks (R4.4 "agents search-and-launch too" — not UI-only;
R4.5 "search invoked through the company MCP returns results").

THE CHAIN IT WALKS:
  1. tools/list           — the server ADVERTISES sessions with op="search" (discovery: an agent
                            finds the capability in the tool schema, never by reading source).
  2. sessions(op=search)  — a real content query over the real transcript index; results come back
                            as LIVE handles (session_id + state-now + point + commands).
  3. [--act only] session_post(verb='consult') on the top routable handle — the agent ACTS from the
                            result: the intent lands durably in the mailbox (verified by step 4).
                            The supervisor EXECUTING that intent (the fork, the reply) is the
                            supervisor service's job — when it is down, the intent queues; that
                            execution is the lead's live probe, by design (the floor: only the
                            supervisor spawns).
  4. [--act only] sessions(op='inbox', session=<target>) — the posted intent is READ BACK through
                            the same MCP face (write-proof discipline: verify the consequence,
                            never trust the response envelope).
  5. [--act only] R4.3's STRUCTURE half: the found session is GRABBED into a real gathering
                            (channel_act action='gather' — the handle's own `gather` command),
                            the gathering is messaged (closed member ⇒ the post QUEUES, never
                            wakes — floor-safe for real), the membership + post are read back
                            (channels op='describe'/'history'), then the gathering DISPERSES
                            (R2.3's momentary lifecycle — grab, act, let go; history stays).

Default run is PURE READ (steps 1–2; safe to repeat). `--act` performs the real post ONCE — it
writes real mail the supervisor WILL act on when next up. Run it deliberately.

Run:  ./.venv/bin/python tests/session_search_mcp_stdio_probe.py [--act] [-q "query"]
Exit: 0 only if every walked step proved out; non-zero + the failing frame otherwise (fail loud).
"""
import argparse
import json
import os
import select
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER = [os.path.join(ROOT, ".venv", "bin", "python"), os.path.join(ROOT, "mcp_face", "server.py")]


class StdioMCP:
    """A minimal REAL MCP client: newline-delimited JSON-RPC over the server's stdio."""

    def __init__(self, argv):
        self.p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, bufsize=1, cwd=ROOT)
        self._id = 0

    def _send(self, obj):
        self.p.stdin.write(json.dumps(obj) + "\n")
        self.p.stdin.flush()

    def _read_msg(self, timeout=120):
        deadline = time.time() + timeout
        while time.time() < deadline:
            r, _, _ = select.select([self.p.stdout], [], [], 1.0)
            if not r:
                if self.p.poll() is not None:
                    raise RuntimeError(
                        f"server exited rc={self.p.returncode}; stderr: {self.p.stderr.read()[-800:]}")
                continue
            line = self.p.stdout.readline()
            if not line:
                raise RuntimeError(
                    f"server closed stdout; stderr: {self.p.stderr.read()[-800:]}")
            line = line.strip()
            if not line:
                continue
            return json.loads(line)
        raise RuntimeError("timeout waiting for a JSON-RPC frame")

    def request(self, method, params=None, timeout=120):
        self._id += 1
        rid = self._id
        self._send({"jsonrpc": "2.0", "id": rid, "method": method, "params": params or {}})
        while True:
            msg = self._read_msg(timeout)
            if msg.get("id") == rid:
                if "error" in msg:
                    raise RuntimeError(f"{method} → JSON-RPC error: {msg['error']}")
                return msg["result"]
            # notifications/other ids: keep draining (real protocol traffic, not noise)

    def notify(self, method, params=None):
        self._send({"jsonrpc": "2.0", "method": method, "params": params or {}})

    def close(self):
        try:
            self.p.stdin.close()
        except Exception:
            pass
        try:
            self.p.terminate()
            self.p.wait(timeout=10)
        except Exception:
            self.p.kill()


def tool_result_json(res):
    """FastMCP returns dict results as content[0].text JSON (+ structuredContent on new SDKs)."""
    if isinstance(res.get("structuredContent"), dict):
        sc = res["structuredContent"]
        return sc.get("result", sc)
    for c in res.get("content", []):
        if c.get("type") == "text":
            return json.loads(c["text"])
    raise RuntimeError(f"no JSON payload in tool result: {json.dumps(res)[:400]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-q", default="transcript exporter session frontmatter",
                    help="content query to search")
    ap.add_argument("--act", action="store_true",
                    help="ALSO post a real consult intent on the top handle (writes real mail)")
    args = ap.parse_args()

    ok = True

    def check(label, cond, extra=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}" + (f" — {extra}" if extra and not cond else ""))

    print("MCP stdio probe — the agent-native search→handle→act chain (R4.4/R4.5)")
    cli = StdioMCP(SERVER)
    try:
        init = cli.request("initialize", {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "r4-search-lane-probe", "version": "0"}}, timeout=180)
        cli.notify("notifications/initialized")
        check("initialize handshake with the REAL server (server names itself)",
              (init.get("serverInfo") or {}).get("name") == "company",
              json.dumps(init)[:200])

        tools = cli.request("tools/list", {}, timeout=180)
        names = {t["name"]: t for t in tools.get("tools", [])}
        check("sessions + session_post advertised", "sessions" in names and "session_post" in names)
        sess_schema = json.dumps(names.get("sessions", {}))
        check("the sessions tool schema ADVERTISES op='search' (agent-discoverable, not source-read)",
              '"search"' in sess_schema)

        res = cli.request("tools/call", {
            "name": "sessions",
            "arguments": {"op": "search", "q": args.q, "limit": 3}}, timeout=300)
        payload = tool_result_json(res)
        check("sessions(op='search') over stdio returned the joined envelope",
              payload.get("op") == "search" and "results" in payload
              and payload.get("mode_used") in ("semantic", "lexical"))
        print(f"  · mode_used={payload.get('mode_used')} sessions_found={payload.get('sessions_found')}"
              f" chunks_matched={payload.get('chunks_matched')}")
        handles = [r for r in payload.get("results", []) if r.get("routable")]
        check("results are LIVE handles (state joined, primary_verb computed, commands present)",
              handles and all(r.get("state") and r.get("primary_verb") and r.get("commands")
                              for r in handles))
        for r in payload.get("results", []):
            print(f"  · {r['session_id'][:8]}… state={r.get('state')} verb={r.get('primary_verb')}"
                  f" point={ (r.get('point') or {}).get('anchor') }")

        if args.act and handles:
            top = handles[0]
            sid = top["session_id"]
            snippet = (top.get("snippet") or "")[:160].replace("'", "’")
            msg = (f"CONSULT from the search→handle→act chain (Session Fabric R4.3/R4.4 probe): "
                   f"your transcript matched the query {args.q!r} at {top['point']['anchor']!r} — "
                   f"“{snippet}…”. Question: in one short paragraph, what was this part of your "
                   f"conversation about, and what (if anything) did it decide?")
            post = cli.request("tools/call", {
                "name": "session_post",
                "arguments": {"to": top["session_address"], "message": msg, "verb": "consult",
                              "from_session": "r4-search-lane-probe"}}, timeout=180)
            ppay = tool_result_json(post)
            check("ACT: consult intent posted from the handle (real mailbox append)",
                  ppay.get("posted") and ppay.get("verb") == "consult" and ppay.get("thread"))
            print(f"  · posted={ppay.get('posted')} seq={ppay.get('seq')} thread={ppay.get('thread')}"
                  f" routed={ppay.get('routed')}")
            inbox = cli.request("tools/call", {
                "name": "sessions",
                "arguments": {"op": "inbox", "session": sid, "thread": ppay.get("thread")}},
                timeout=180)
            ipay = tool_result_json(inbox)
            got = [m for m in ipay.get("messages", []) if m.get("id") == ppay.get("posted")]
            check("WRITE-PROOF: the posted intent READ BACK through sessions(op='inbox')",
                  bool(got) and got[0].get("verb") == "consult")
            print(f"  · lead live-probe: bring the supervisor up (company up session-supervisor) "
                  f"and watch agent_sessions.spawned/.turn after seq {ppay.get('seq')} "
                  f"(thread {ppay.get('thread')})")

            # ── R4.3 structure half: handle → GATHERING → post → read back → disperse ──────────
            g = cli.request("tools/call", {
                "name": "channel_act",
                "arguments": {"action": "gather", "name": "r4-search-result-gathering",
                              "purpose": f"momentary: act on the session the query {args.q!r} found",
                              "members": [top["session_address"]]}}, timeout=180)
            gpay = tool_result_json(g)
            cid = gpay.get("channel") or (gpay.get("record") or {}).get("channel") or gpay.get("id")
            check("GATHER: the found session grabbed into a real gathering (from the handle's "
                  "own gather command)", bool(cid), json.dumps(gpay)[:300])
            if cid:
                cp = cli.request("tools/call", {
                    "name": "channel_act",
                    "arguments": {"action": "post", "channel": cid,
                                  "message": f"(R4.3 probe) this gathering exists because your "
                                             f"transcript matched {args.q!r} at "
                                             f"{top['point']['anchor']!r}. No action needed.",
                                  "from_session": "r4-search-lane-probe"}}, timeout=180)
                cpay = tool_result_json(cp)
                fan = cpay.get("fan") or cpay.get("posts") or []
                check("POST to the gathering fans floor-safely (closed member ⇒ queue, never wake)",
                      bool(fan) and all((f.get("verb") in ("queue", "deliver")) for f in fan),
                      json.dumps(cpay)[:300])
                desc = tool_result_json(cli.request("tools/call", {
                    "name": "channels", "arguments": {"op": "describe", "channel": cid}},
                    timeout=180))
                members = json.dumps(desc)
                check("READ-BACK: the gathering's describe shows the found session as member",
                      top["session_id"] in members, members[:300])
                hist = tool_result_json(cli.request("tools/call", {
                    "name": "channels", "arguments": {"op": "history", "channel": cid}},
                    timeout=180))
                check("READ-BACK: the post is in the channel's own history",
                      "R4.3 probe" in json.dumps(hist))
                dis = tool_result_json(cli.request("tools/call", {
                    "name": "channel_act", "arguments": {"action": "disperse", "channel": cid}},
                    timeout=180))
                check("DISPERSE: the gathering let go (R2.3's momentary lifecycle)",
                      "error" not in dis, json.dumps(dis)[:200])
                print(f"  · gathering {cid} — gathered, posted (fan: "
                      f"{[(f.get('to') or '')[-12:] + ':' + (f.get('verb') or '') for f in fan]}), "
                      f"read back, dispersed")
    finally:
        cli.close()

    print("\n" + ("PROBE PASS" if ok else "PROBE FAILURES — fail loud"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
