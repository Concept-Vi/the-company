"""tests/voice_circuit_acceptance.py — the V-PTT (voice push-to-talk) CIRCUIT works end-to-end by USE.

Proves the whole ear→brain→mouth circuit the listening mode drives, asserting EACH HOP against the
worktree bridge (:8771 — NEVER :8770, which runs main):

    scripted audio bytes  ──/api/stt──▶  transcript
                          ──/api/chat──▶ reply (the ONE Suite brain)
                          ──/api/tts──▶  wav (spoken back)

This is the listening-mode loop's headless skeleton (voice/loop.py is the in-process twin). It does NOT
touch the mic/speaker (browser hardware — lane G); it proves the SERVER circuit those hooks ride on.

WHY :8771 + a real clip: the circuit is only proven by USE — a scripted clip is synthesized by the live
Kokoro TTS, transcribed by the SELECTED ear (rhm_config().stt, = whisper.cpp), answered by the live RHM
brain, and spoken back. No hop is mocked.

LIVE-ENDPOINT POLICY (fail-loud, never a vacuous pass): each hop needs a live service. If a prerequisite
is down we SKIP loud + return NON-ZERO — never an "ALL PASS" over an un-run hop. The chat hop RETRIES a
couple times because a cloud RHM model can transiently return empty (the suite lane's tool-gate fails
loud on that) — only an all-attempts-empty is a real failure.

PRECONDITION: the worktree bridge must be up on :8771:
    setsid ./.venv/bin/python runtime/bridge.py 8771 &
Run: ./.venv/bin/python tests/voice_circuit_acceptance.py
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

BRIDGE = os.environ.get("COMPANY_BRIDGE_URL", "http://127.0.0.1:8771")
PASS = 0
ok = True


def check(label, cond):
    global PASS, ok
    if cond:
        PASS += 1
        print(f"  PASS  {label}")
    else:
        ok = False
        print(f"  FAIL  {label}")


def _get(path, timeout=8):
    with urllib.request.urlopen(BRIDGE + path, timeout=timeout) as r:
        return json.loads(r.read() or b"{}")


def _post_json(path, payload, timeout=90):
    req = urllib.request.Request(BRIDGE + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read() or b"{}")


def _post_bytes(path, data, timeout=60):
    req = urllib.request.Request(BRIDGE + path, data=data,
                                 headers={"Content-Type": "application/octet-stream"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read() or b"{}")


def _bridge_up():
    try:
        _get("/api/now", timeout=4)
        return True
    except Exception:
        return False


print("V-PTT voice circuit — STT → chat → TTS, each hop by USE (bridge :8771)")

if not _bridge_up():
    print(f"\n  SKIP (LOUD): worktree bridge unreachable at {BRIDGE} — start it:")
    print("    setsid ./.venv/bin/python runtime/bridge.py 8771 &")
    print("\nFAILURES PRESENT — 0 checks passed")
    sys.exit(1)

# --- hop 0: scripted audio (synthesize a real clip via the live Kokoro through /api/tts) ---
print("\n[0] scripted audio — synthesize a spoken clip via /api/tts (the mouth, used as the prompt source)")
SPOKEN = "What does the scheduler memo gate do?"
wav = None
try:
    req = urllib.request.Request(BRIDGE + "/api/tts",
                                 data=json.dumps({"text": SPOKEN}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        wav = r.read()
except (urllib.error.URLError, OSError) as e:
    print(f"  SKIP (LOUD): /api/tts (Kokoro :4123) unreachable — cannot script audio ({e}).")
    ok = False
if wav:
    check("scripted clip is a non-trivial WAV", len(wav) > 1000 and wav[:4] == b"RIFF")

# --- hop 1: /api/stt — audio → transcript (through the SELECTED ear) ---
transcript = ""
if wav:
    print("\n[1] /api/stt — the EAR: scripted audio → transcript (selected ear = rhm_config().stt)")
    try:
        heard = _post_bytes("/api/stt", wav, timeout=60)
        transcript = (heard.get("text") or "").strip()
        print(f"    heard: {transcript!r}  via {heard.get('provider')!r}")
        check("transcript is non-empty", len(transcript) > 0)
        check("transcript recovers a key word (scheduler/memo/gate)",
              any(w in transcript.lower() for w in ("scheduler", "memo", "gate")))
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        print(f"  SKIP (LOUD): /api/stt hop failed — {e}")
        ok = False

# --- hop 2: /api/chat — transcript → reply (the ONE Suite brain) ---
reply = ""
if transcript:
    print("\n[2] /api/chat — the BRAIN: transcript → reply (the ONE Suite; retries transient cloud-empty)")
    last_err = None
    for attempt in range(3):                                 # a cloud RHM model can transiently return empty
        try:
            out = _post_json("/api/chat", {"message": transcript, "graph_id": "codebase"}, timeout=120)
            if out.get("error"):
                last_err = out["error"]
                time.sleep(2)
                continue
            reply = (out.get("reply") or "").strip()
            if reply:
                print(f"    reply: {reply[:90]!r}  (model {out.get('model')!r})")
                break
            last_err = "empty reply"
            time.sleep(2)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            last_err = str(e)
            time.sleep(2)
    check("brain returned a non-empty reply (after retries)", bool(reply))
    if not reply:
        print(f"    last error: {last_err}")

# --- hop 3: /api/tts — reply → wav (spoken back) ---
if reply:
    print("\n[3] /api/tts — the MOUTH: reply → wav (spoken back to the operator)")
    try:
        req = urllib.request.Request(BRIDGE + "/api/tts",
                                     data=json.dumps({"text": reply[:300]}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            spoken = r.read()
        check("reply synthesized to a non-trivial WAV", len(spoken) > 1000 and spoken[:4] == b"RIFF")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        print(f"  SKIP (LOUD): /api/tts reply hop failed — {e}")
        ok = False

print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} — {PASS} checks passed (full circuit: STT→chat→TTS)")
sys.exit(0 if ok else 1)
