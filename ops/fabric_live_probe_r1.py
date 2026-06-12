"""ops/fabric_live_probe_r1.py — the R1 LIVE PROBE (lead-only: this spawns REAL claude sessions).

Session Fabric R1's real-operation proofs, runnable in one command against the LIVE supervisor:

  R1.1 — drive a real session through genuine CLI actions and OBSERVE each happen:
         (a) a slash command sent as the prompt string (Atlas agent-sdk/slash-commands.md:
             "Send slash commands by including them in your prompt string"; only
             non-interactive-capable commands dispatch — system/init lists them),
         (b) a tool use (the floor session's mcp__company tools),
         (c) /rewind — RECORDED HONESTLY: the Atlas (checkpointing.md:42) says /rewind opens an
             interactive MENU; the headless path for file-rewind is the SDK's rewindFiles()
             (typescript.md:510) which this -p transport does not carry. The probe sends it and
             records verbatim what the stream returns — the result is EVIDENCE, not a pre-claim.
  R1.2 (live half) — the full raw stream of a REAL session is captured to a file; every emit
         rides back as a `declared` event on /watch; any agent_sessions.render_drop = a registry
         gap surfaced (the service-level half is already proven by stub in
         tests/render_declaration_acceptance.py — this is the real-claude capture).
  R1.3 (live half) — spawn with registry flags and OBSERVE the real effect:
         session_id pre-assigned → the declared system/init must echo that exact session_id;
         append_system_prompt → the session can state the appended rule when asked.

Usage (the lead):
    company up session-supervisor            # if not already up
    .venv/bin/python ops/fabric_live_probe_r1.py [--port 8771] [--keep]

It prints a PROOF SUMMARY block to paste beside the R-lines in the spec doc. Sessions are torn
down at the end unless --keep. The probe NEVER green-paints: each leg reports OBSERVED/NOT-OBSERVED
with the captured evidence path.

Plumbing self-test (no real claude — what this build lane may run): point COMPANY_CLAUDE_BIN at a
stub and run with --port <test>; the probe's spawn/inject/watch/report mechanics are then exercised
end-to-end (the slash/rewind legs will report NOT-OBSERVED against a stub — honest).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPTURE_DIR = os.path.join(REPO, ".build", "fabric-probe")


class ProbeFail(Exception):
    pass


def req(base: str, method: str, path: str, body: dict | None = None, timeout: float = 30):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(base + path, data=data, method=method,
                               headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


class Watcher(threading.Thread):
    """Tee the session's /watch ndjson into memory + a capture file for the LIFE of the probe."""

    def __init__(self, base: str, session: str, capture_path: str):
        super().__init__(daemon=True)
        self.base, self.session, self.path = base, session, capture_path
        self.events: list[dict] = []
        self.lock = threading.Lock()
        self._stop = threading.Event()

    def run(self):
        try:
            r = urllib.request.Request(f"{self.base}/watch?session={self.session}")
            with urllib.request.urlopen(r, timeout=300) as resp, open(self.path, "a") as f:
                for raw in resp:
                    if self._stop.is_set():
                        break
                    f.write(raw.decode("utf-8", "replace"))
                    f.flush()
                    try:
                        ev = json.loads(raw)
                    except ValueError:
                        continue
                    with self.lock:
                        self.events.append(ev)
        except Exception as e:
            print(f"  [watcher {self.session}] ended: {e}")

    def stop(self):
        self._stop.set()

    def mark(self) -> int:
        """A cursor over the event tape — wait_for(since=mark()) only sees NEWER events, so a
        leg can never match a previous turn's done/output (the stale-event bug the stub
        self-test caught)."""
        with self.lock:
            return len(self.events)

    def wait_for(self, pred, timeout: float, what: str, since: int = 0):
        t0 = time.time()
        while time.time() - t0 < timeout:
            with self.lock:
                for ev in self.events[since:]:
                    if pred(ev):
                        return ev
            time.sleep(0.25)
        return None

    def declared_keys(self) -> list:
        with self.lock:
            return [e.get("render_key") for e in self.events if e.get("type") == "declared"]


def wait_idle(base: str, sid: str, timeout: float = 240) -> dict:
    t0 = time.time()
    while time.time() - t0 < timeout:
        _, r = req(base, "GET", "/sessions")
        rec = next((s for s in r.get("sessions", []) if s["id"] == sid), None)
        if rec and rec["state"] == "idle":
            return rec
        if rec and rec["state"] == "closed":
            raise ProbeFail(f"session {sid} closed mid-probe: {rec.get('close_reason')}")
        time.sleep(0.5)
    raise ProbeFail(f"session {sid} not idle within {timeout}s")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8771)
    ap.add_argument("--keep", action="store_true", help="leave the probe sessions alive")
    args = ap.parse_args()
    base = f"http://127.0.0.1:{args.port}"
    os.makedirs(CAPTURE_DIR, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    proof: dict[str, str] = {}

    try:
        _, h = req(base, "GET", "/health")
    except Exception as e:
        print(f"BLOCKED — supervisor not reachable on {base} ({e}).\n"
              f"Bring it up first: company up session-supervisor")
        return 2
    print(f"supervisor up: {h.get('sessions')}")

    # ── leg 1 (R1.3 live): spawn with registry flags; init must echo the pre-assigned id ──
    import uuid as _uuid
    want_sid = str(_uuid.uuid4())
    rule = f"When asked 'what extra rule were you given', answer exactly: PROBE-RULE-{stamp}"
    code, r = req(base, "POST", "/spawn", {
        "cwd": REPO, "name": f"r1-probe-{stamp}",
        "include_partial": True,
        "flags": {"session_id": want_sid, "append_system_prompt": rule}})
    if code != 200:
        print(f"FAIL spawn: {r}")
        return 1
    sid = r["session"]["id"]
    cap = os.path.join(CAPTURE_DIR, f"probe-{stamp}-{sid}.ndjson")
    w = Watcher(base, sid, cap)
    w.start()
    init = w.wait_for(lambda e: e.get("type") == "declared"
                      and e.get("render_key") == "system/init", 60, "declared init")
    got_sid = (init or {}).get("fields", {}).get("session_id")
    proof["R1.3 session_id"] = (
        f"OBSERVED — pre-assigned {want_sid} == init's session_id" if got_sid == want_sid
        else f"NOT-OBSERVED — wanted {want_sid}, init carried {got_sid}")
    print(f"  {proof['R1.3 session_id']}")

    # the appended-system-prompt effect, observed through behaviour
    wait_idle(base, sid)
    m = w.mark()
    req(base, "POST", "/inject", {"session": sid,
        "message": "What extra rule were you given? Answer with the rule's exact text only."})
    done = w.wait_for(lambda e: e.get("type") == "done", 240, "turn done", since=m)
    txt = (done or {}).get("result", "")
    proof["R1.3 append_system_prompt"] = (
        f"OBSERVED — the session stated PROBE-RULE-{stamp}" if f"PROBE-RULE-{stamp}" in txt
        else f"NOT-OBSERVED — reply was: {txt[:200]!r}")
    print(f"  {proof['R1.3 append_system_prompt']}")

    # ── leg 2 (R1.1a): a slash command as the prompt string ──
    wait_idle(base, sid)
    slash = "/context"
    avail = (init or {}).get("fields", {}).get("slash_commands") or []
    if avail and "context" not in avail and "usage" in avail:
        slash = "/usage"
    m = w.mark()
    req(base, "POST", "/inject", {"session": sid, "message": slash})
    lco = w.wait_for(lambda e: e.get("type") == "declared" and e.get("render_key")
                     in ("system/local_command_output", "system/local_command"), 120,
                     "slash output", since=m)
    done = w.wait_for(lambda e: e.get("type") == "done", 240, "slash turn done", since=m)
    if lco:
        proof["R1.1 slash command"] = (f"OBSERVED — {slash} produced declared "
                                       f"{lco['render_key']} on the stream")
    elif done and done.get("result"):
        proof["R1.1 slash command"] = (f"OBSERVED (result-carried) — {slash} returned: "
                                       f"{done['result'][:160]!r}")
    else:
        proof["R1.1 slash command"] = f"NOT-OBSERVED — {slash} produced no output event"
    print(f"  {proof['R1.1 slash command']}")

    # ── leg 3 (R1.1b): a genuine tool use, observed as a declared tool_use block ──
    wait_idle(base, sid)
    m = w.mark()
    req(base, "POST", "/inject", {"session": sid,
        "message": "Use the capabilities tool (mcp__company) and tell me how many node types exist."})
    tu = w.wait_for(
        lambda e: e.get("type") == "declared" and any(
            b.get("render_key", "").startswith("assistant.content.tool_use")
            for b in e.get("blocks") or []), 240, "tool use", since=m)
    proof["R1.1 tool use"] = (
        "OBSERVED — a declared assistant.content.tool_use block on the stream"
        if tu else "NOT-OBSERVED — no tool_use block (floor session may have declined)")
    print(f"  {proof['R1.1 tool use']}")
    w.wait_for(lambda e: e.get("type") == "done", 240, "tool turn done", since=m)

    # ── leg 4 (R1.1c): /rewind — recorded verbatim, never pre-claimed ──
    wait_idle(base, sid)
    m = w.mark()
    req(base, "POST", "/inject", {"session": sid, "message": "/rewind"})
    done = w.wait_for(lambda e: e.get("type") == "done", 240, "rewind turn done", since=m)
    proof["R1.1 rewind"] = (
        f"RECORDED — /rewind returned: {(done or {}).get('result', '')[:200]!r} "
        f"(Atlas: /rewind is an interactive menu; headless rewind = SDK rewindFiles(), not this "
        f"transport — the fabric's own time-travel is R3.4's adapter)")
    print(f"  {proof['R1.1 rewind']}")

    # ── leg 5 (R1.2 live): capture + declaration coverage of THIS real stream ──
    keys = w.declared_keys()
    _, evs = req(base, "GET", "/sessions")
    drops = [k for k in keys if k and k.startswith("undeclared/")]
    proof["R1.2 live capture"] = (
        f"{'OBSERVED' if keys else 'NOT-OBSERVED'} — {len(keys)} declared events on the live "
        f"stream ({len(set(keys))} distinct render_keys), {len(drops)} undeclared"
        + (f" ({sorted(set(drops))})" if drops else "") + f"; raw capture: {cap}")
    print(f"  {proof['R1.2 live capture']}")

    if not args.keep:
        req(base, "POST", "/teardown", {"session": sid})
    w.stop()

    print("\n══ PROOF SUMMARY (paste beside the R-lines) ══")
    for k, v in proof.items():
        print(f"  {k}: {v}")
    ok = sum(1 for v in proof.values() if v.startswith("OBSERVED") or v.startswith("RECORDED"))
    print(f"\n{ok}/{len(proof)} legs observed/recorded. Capture: {cap}")
    return 0 if ok == len(proof) else 1


if __name__ == "__main__":
    sys.exit(main())
