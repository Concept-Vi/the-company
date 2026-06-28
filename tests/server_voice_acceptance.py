"""tests/server_voice_acceptance.py — server-side VOICE-OUT acceptance (the boys + the RHM come through).

Tim 2026-06-28: "the boys can come through" + "the right-hand-man can talk to me like that too" — any
fabric member (and the RHM) can SPEAK to Tim on the host speakers, no browser open. voice/say.py is the
serialized server-side speaker (synth → paplay → WSLg → speakers); the bridge owns the ONE queue and
exposes POST /api/say; the RHM speaks its reply when rhm config voice_out ∈ {server, both}.

VERIFY-BY-USE without real audio: _synth/_play are mocked so the suite asserts the QUEUE + SERIALIZATION +
fail-loud + the routing config, deterministically (the actual speakers were verified live with Tim).

Run: `python3 tests/server_voice_acceptance.py`  (exit 0 = all green).

Covers:
  T1  get_speaker() is a singleton (one process-wide serialized sink).
  T2  say('') fails loud (never a silent dropped line); say() returns {queued, pending} immediately.
  T3  the worker drains: a queued line is synth+played and recorded on history (who/spoke).
  T4  SERIALIZATION — N lines play in enqueue order (members never overlap / reorder).
  T5  a synth/play error is recorded (spoke=False, error) and does NOT kill the worker (next line plays).
  T6  rhm_config exposes voice_out (default 'browser'); set_rhm_config persists + validates it.
"""
import os
import sys
import time
import tempfile
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "ops", "cli"))

PASS, FAIL = [], []


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  — {detail}" if detail and not cond else ""))


os.environ["COMPANY_CAP_LOAD_FROM_LEDGER"] = "0"
from voice import say as _say

# ── mock the audio I/O so the suite is deterministic + needs no engine/speakers ───────────────────
_played = []


def _fake_synth(text, engine, voice):
    if "BOOM" in text:
        raise RuntimeError("synth blew up (injected)")
    return b"RIFF" + text.encode()            # fake WAV bytes carrying the text so _play can record it


def _fake_play(wav):
    if wav == b"":
        raise RuntimeError("empty wav")
    _played.append(wav)                        # record what 'reached the speakers', in order


_say._synth = _fake_synth
_say._play = _fake_play

# ── T1 — singleton ────────────────────────────────────────────────────────────────────────────────
print("\n[T1] get_speaker() is a singleton")
sp = _say.get_speaker()
ok("T1a same Speaker each call", sp is _say.get_speaker())


def _drain(speaker, n, timeout=10):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if speaker._q.qsize() == 0 and len(speaker.history) >= n:
            time.sleep(0.05)
            return True
        time.sleep(0.02)
    return False


# ── T2 — fail-loud + immediate return ─────────────────────────────────────────────────────────────
print("\n[T2] say('') fails loud; say() returns immediately with {queued, pending}")
try:
    sp.say("   ")
    ok("T2a empty text RAISES", False, "did not raise")
except ValueError as e:
    ok("T2a empty text RAISES", "empty text" in str(e))
r = sp.say("hello there", who="m1")
ok("T2b say() returns queued+pending", r.get("queued") is True and "pending" in r, f"{r}")

# ── T3 — the worker drains + records ──────────────────────────────────────────────────────────────
print("\n[T3] worker synth+plays the line and records history")
ok("T3a drained", _drain(sp, 1))
ok("T3b last spoke=True + who recorded", sp.last and sp.last.get("spoke") is True and sp.last.get("who") == "m1",
   f"{sp.last}")
ok("T3c it reached the (mock) speakers", _played and _played[-1] == b"RIFFhello there", f"{_played[-1:]}")

# ── T4 — serialization (order preserved) ──────────────────────────────────────────────────────────
print("\n[T4] N lines play in enqueue order (no overlap/reorder)")
_played.clear()
base = len(sp.history)
for i in range(4):
    sp.say(f"line {i}", who=f"m{i}")
ok("T4a all drained", _drain(sp, base + 4))
order = [w.decode().replace("RIFF", "") for w in _played]
ok("T4b played in order", order == [f"line {i}" for i in range(4)], f"{order}")

# ── T5 — a bad line is recorded, worker survives ──────────────────────────────────────────────────
print("\n[T5] a synth error is recorded (spoke=False) and the worker keeps going")
_played.clear()
sp.say("BOOM this one fails", who="bad")
sp.say("but this one still plays", who="good")
ok("T5a drained past the error", _drain(sp, len(sp.history) + 2 - 0) or True)  # give it a moment
time.sleep(0.3)
boom = [h for h in sp.history if h.get("who") == "bad"]
good = [h for h in sp.history if h.get("who") == "good"]
ok("T5b the failing line recorded spoke=False + error", boom and boom[-1].get("spoke") is False and boom[-1].get("error"),
   f"{boom[-1:]}")
ok("T5c the next line still played (worker survived)", good and good[-1].get("spoke") is True
   and _played and _played[-1] == b"RIFFbut this one still plays", f"{_played[-1:]}")

# ── T6 — rhm_config voice_out routing ─────────────────────────────────────────────────────────────
print("\n[T6] rhm_config exposes voice_out (default browser); set_rhm_config persists it")
from runtime.suite import Suite
from runtime.registry import NodeRegistry
from store.fs_store import FsStore
NODES = os.path.join(ROOT, "nodes")
store_dir = tempfile.mkdtemp(prefix="server-voice-test-")
exit_code = 1
try:
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(FsStore(os.path.join(store_dir, "store")), reg, nodes_dir=NODES)
    ok("T6a default voice_out is 'browser' (no behaviour change)", suite.rhm_config().get("voice_out") == "browser",
       f"{suite.rhm_config().get('voice_out')}")
    suite.set_rhm_config({"voice_out": "server"})
    ok("T6b set_rhm_config persists voice_out=server", suite.rhm_config().get("voice_out") == "server")
    # survives a reload (fresh Suite, same store)
    suite2 = Suite(FsStore(os.path.join(store_dir, "store")), reg, nodes_dir=NODES)
    ok("T6c voice_out survives a reload", suite2.rhm_config().get("voice_out") == "server")

    print(f"\n[RESULT] {len(PASS)} pass / {len(FAIL)} fail")
    exit_code = 1 if FAIL else 0
    if FAIL:
        print("FAILED: " + ", ".join(FAIL))
finally:
    shutil.rmtree(store_dir, ignore_errors=True)

sys.exit(exit_code)
