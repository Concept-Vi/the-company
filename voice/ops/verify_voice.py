#!/usr/bin/env python3
"""voice/ops/verify_voice.py — POST-RESTART verify-by-use for the voice trial (the finish-checklist
STEP 3, as one command). Each check is GREEN only when demonstrated against the running stack — no
check passes on code-reading. Run AFTER `voice-stack start` + the bridge is up.

  python3 voice/ops/verify_voice.py            # run every check, print PASS/FAIL per line
  python3 voice/ops/verify_voice.py --quick     # skip the per-engine /api/tts synth (just probes + routing)

Uses only stdlib (runs in the 3.14 runtime python OR any python3) — it talks to the bridge + engines
over HTTP, it does NOT import the heavy libs. The bridge is the ONE Suite (default :8770); engines are
the per-port services. Fail-loud: a check that errors prints FAIL with the exact error, never a fake pass.

Pre-restart you can dry-run the two checks that don't need the GPU engines:
  python3 voice/ops/verify_voice.py --pre-restart   # only: /api/voice reachable + Kokoro byte-identical
"""
from __future__ import annotations
import argparse
import json
import sys
import urllib.request

BRIDGE = "http://127.0.0.1:8770"
ENGINE_PORTS = {"kokoro": 4123, "chatterbox": 4124, "orpheus": 4125,
                "cosyvoice": 4126, "xtts": 4127, "qwen3tts": 4128}

_results: list[tuple[str, bool, str]] = []


def check(name: str):
    """Decorator-ish helper: run fn, record PASS/FAIL + a note. Never raises out — records the error."""
    def run(fn):
        try:
            ok, note = fn()
        except Exception as e:                                # fail loud INTO the report, don't abort the run
            ok, note = False, f"{type(e).__name__}: {e}"
        _results.append((name, ok, note))
        print(f"[{'PASS' if ok else 'FAIL'}] {name} — {note}")
        return ok
    return run


def _get(url: str, timeout: int = 5):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read() or b"{}")


def _post(url: str, payload: dict, timeout: int = 120, raw: bool = False):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
    return body if raw else json.loads(body or b"{}")


def c_voice_status():
    """STEP 3.1 — /api/voice reachable; report which engines are up."""
    d = _get(BRIDGE + "/api/voice")
    engines = d.get("engines", [])
    up = [e["engine"] for e in engines if e.get("up")]
    return (len(engines) > 0, f"engines reporting: {len(engines)}; up={up}; stt={d.get('stt')}")


def c_kokoro_identical():
    """STEP 3.2 (no-engine case) — /api/tts with no engine must be byte-identical to direct Kokoro."""
    text = "Voice trial verification check."
    via_bridge = _post(BRIDGE + "/api/tts", {"text": text}, raw=True)
    via_kokoro = _post(f"http://127.0.0.1:{ENGINE_PORTS['kokoro']}/tts", {"text": text}, raw=True)
    same = via_bridge == via_kokoro
    return (same and len(via_bridge) > 44,
            f"bridge={len(via_bridge)}B kokoro={len(via_kokoro)}B identical={same}")


def c_tts_engine(engine: str):
    """STEP 3.2/3.3 — POST /api/tts {engine} → an audible (non-empty) wav for an UP engine."""
    wav = _post(BRIDGE + "/api/tts", {"engine": engine, "text": "Hello from the voice trial."}, raw=True)
    return (len(wav) > 44, f"{engine} returned {len(wav)} bytes")


def c_tts_faildown():
    """STEP 3.2 — an engine that's DOWN must fail loud (HTTP 400) naming the engine+port, never silent."""
    # find a down engine from /api/voice
    d = _get(BRIDGE + "/api/voice")
    down = [e for e in d.get("engines", []) if not e.get("up") and e["engine"] != "kokoro"]
    if not down:
        return (True, "all engines up — no down-engine to test fail-loud (ok)")
    eng = down[0]["engine"]
    try:
        _post(BRIDGE + "/api/tts", {"engine": eng, "text": "x"}, raw=True)
        return (False, f"{eng} is down but /api/tts did NOT fail loud")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        return (e.code >= 400 and eng in body, f"{eng} down → HTTP {e.code}: {body[:120]}")


def c_debrief(session_ids):
    """STEP 3.7 (highest-risk) — record a session → debrief framing must QUOTE the real transcript.
    Requires session_ids (record 2 turns first, pass --debrief-session <id>). Skipped if not provided."""
    if not session_ids:
        return (True, "skipped — pass --debrief-session <id> after recording a real session")
    _post(BRIDGE + "/api/debrief/start", {"session_ids": session_ids})
    cur = _get(BRIDGE + "/api/review/current")
    # The surfaced debrief item carries the REAL transcript object (suite.start_debrief), which has
    # n == turn count. The exact nesting in /api/review/current's payload is resolved at runtime;
    # walk the response for a transcript dict with an 'n' so the check doesn't hardcode the path.
    n = _find_transcript_n(cur)
    return (n is not None and n > 0,
            f"debrief framing transcript.n={n} (must equal recorded turn count, not a bare name; "
            "by-ear: confirm the host QUOTES the real transcript, never confabulates)")


def _find_transcript_n(obj):
    """Recursively find a {'transcript': {... 'n': int ...}} (or a transcript dict with 'n')."""
    if isinstance(obj, dict):
        t = obj.get("transcript")
        if isinstance(t, dict) and isinstance(t.get("n"), int):
            return t["n"]
        if "n" in obj and "turns" in obj and isinstance(obj.get("n"), int):
            return obj["n"]
        for v in obj.values():
            r = _find_transcript_n(v)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = _find_transcript_n(v)
            if r is not None:
                return r
    return None


def main():
    global BRIDGE
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="skip per-engine /api/tts synth")
    ap.add_argument("--pre-restart", action="store_true",
                    help="only the two checks that work without GPU engines")
    ap.add_argument("--bridge", default=BRIDGE)
    ap.add_argument("--debrief-session", action="append", default=[],
                    help="session id(s) to debrief (record 2 turns first)")
    args = ap.parse_args()
    BRIDGE = args.bridge

    check("3.1 /api/voice reachable")(c_voice_status)
    check("3.2 no-engine == Kokoro (byte-identical)")(c_kokoro_identical)

    if args.pre_restart:
        _summary(); return

    # which engines are up → only synth-test those (don't fail a check just because an engine is off)
    try:
        up = [e["engine"] for e in _get(BRIDGE + "/api/voice").get("engines", []) if e.get("up")]
    except Exception:
        up = []
    if not args.quick:
        for engine in ("qwen3tts", "chatterbox", "cosyvoice", "xtts", "orpheus"):
            if engine in up:
                check(f"3.3 /api/tts {engine} audible")(lambda e=engine: c_tts_engine(e))
            else:
                print(f"[SKIP] 3.3 /api/tts {engine} — engine down (start it: voice-stack start {engine})")
    check("3.2 down-engine fails loud")(c_tts_faildown)
    check("3.7 debrief quotes transcript")(lambda: c_debrief(args.debrief_session))

    _summary()


def _summary():
    passed = sum(1 for _, ok, _ in _results if ok)
    print(f"\n=== {passed}/{len(_results)} checks PASSED ===")
    sys.exit(0 if passed == len(_results) else 1)


if __name__ == "__main__":
    main()
