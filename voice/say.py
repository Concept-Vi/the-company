"""voice/say.py — SERVER-SIDE speech-out: the Company speaks to Tim through the machine's own speakers.

The other voice paths (voice/loop.py, /api/voice/stream, the canvas speakReply) all return WAV BYTES to
a BROWSER, which plays them via Web Audio — so nothing is audible unless the canvas is open. Tim's ask
(2026-06-28): "the boys can come through" + "the right-hand-man can talk to me like that too" — i.e. any
fabric MEMBER (and the RHM) can SPEAK to him with NO browser open. This module is that sink: synth a line
on a TTS engine, then PLAY it on this host's speakers.

The audio path (verified on this WSL box): `paplay` → the WSLg PulseServer socket (unix:/mnt/wslg/PulseServer)
→ Windows speakers. ALSA finds no card; PulseAudio via WSLg is the working sink. We set PULSE_SERVER
explicitly so it works regardless of the bridge service's inherited env.

Serialized by design: one daemon worker drains a queue, synthesising + playing ONE line at a time, so two
members never talk over each other. `say()` enqueues and returns immediately (never blocks the caller).
Reuses the existing synth (voice.loop.speak) + the pre-TTS speakable cleaner (voice.speakable) — no parallel
TTS path. Runs IN the bridge process (3.14, which imports voice.loop/speakable fine + reaches PulseAudio);
other processes (the MCP face) reach it via the bridge POST /api/say, so there is ONE queue, one sink.
"""
from __future__ import annotations

import os
import queue
import subprocess
import tempfile
import threading
import time

# The WSLg PulseAudio sink — set explicitly so paplay finds it even when the bridge's systemd unit did not
# inherit PULSE_SERVER. Overridable for a non-WSL host (a normal PulseAudio/pipewire socket).
PULSE_SERVER = os.environ.get("COMPANY_PULSE_SERVER", "unix:/mnt/wslg/PulseServer")
DEFAULT_ENGINE = os.environ.get("COMPANY_SAY_ENGINE", "kokoro")
_MAX_QUEUE = 64                                     # a backstop so a runaway speaker can't grow unbounded


def _synth(text: str, engine: str, voice: str | None):
    """Text → WAV bytes via the SELECTED TTS engine. Reuses voice.loop.speak (the one engine-call +
    fail-loud), after the speakable cleaner strips markdown/emoji so the engine never reads markup aloud."""
    from voice import loop as _loop                 # lazy: keeps import-time light + venv-safe
    try:
        from voice import speakable as _speakable
        spoken = _speakable.speakable(text, engine)
    except Exception:
        spoken = text                               # best-effort clean; never lose the line over a cleaner error
    return _loop.speak(spoken, engine, voice=voice)


def _play(wav: bytes) -> None:
    """Play WAV bytes on THIS host's speakers via paplay → the WSLg PulseServer. Fail loud (no silent
    no-op) so a broken audio path surfaces instead of pretending it spoke."""
    if not wav:
        raise RuntimeError("voice.say._play: empty WAV (synth produced no audio) — refusing a silent no-op")
    env = dict(os.environ, PULSE_SERVER=PULSE_SERVER)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(wav)
        path = f.name
    try:
        r = subprocess.run(["paplay", path], env=env, capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            raise RuntimeError(f"voice.say: paplay failed (rc={r.returncode}) — {r.stderr.strip()[:200]}; "
                               f"PULSE_SERVER={PULSE_SERVER}. Is the WSLg audio socket present?")
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


class Speaker:
    """The serialized server-side voice. One daemon worker drains the queue: synth → play, ONE at a time,
    so members never overlap. Thread-safe enqueue via say(). Each spoken item records its outcome on
    `last` (the by-use evidence: what was said, by whom, did it play, any error)."""

    def __init__(self):
        self._q: queue.Queue = queue.Queue(maxsize=_MAX_QUEUE)
        self._worker: threading.Thread | None = None
        self._lock = threading.Lock()
        self.history: list = []                     # recent spoken items (capped) — the say-log
        self.last: dict | None = None

    def _ensure_worker(self):
        with self._lock:
            if self._worker is None or not self._worker.is_alive():
                self._worker = threading.Thread(target=self._run, name="company-speaker", daemon=True)
                self._worker.start()

    def _run(self):
        while True:
            item = self._q.get()
            try:
                wav = _synth(item["text"], item["engine"], item.get("voice"))
                _play(wav)
                item["spoke"] = True
            except Exception as e:                  # one bad line must not kill the speaker; record it loud
                item["spoke"] = False
                item["error"] = f"{type(e).__name__}: {e}"
            finally:
                item["done_ts"] = time.time()
                self.last = item
                self.history.append(item)
                del self.history[:-50]              # keep the last 50
                self._q.task_done()

    def say(self, text: str, *, engine: str | None = None, voice: str | None = None,
            who: str | None = None) -> dict:
        """ENQUEUE a line to be spoken on the host speakers (returns immediately — the worker plays it in
        turn). `who` is the speaker's identity (a member name / 'rhm') for the say-log. Fail loud on empty
        text or a full queue (a dropped line is a silent failure)."""
        text = (text or "").strip()
        if not text:
            raise ValueError("voice.say: empty text — nothing to speak (fail loud, never a silent no-op)")
        item = {"text": text, "engine": engine or DEFAULT_ENGINE, "voice": voice, "who": who,
                "enqueued_ts": time.time(), "spoke": None}
        self._ensure_worker()
        try:
            self._q.put_nowait(item)
        except queue.Full:
            raise RuntimeError(f"voice.say: speak queue full ({_MAX_QUEUE}) — refusing to drop {who or 'a'} "
                               f"line silently. The speaker is backed up; retry shortly.")
        return {"queued": True, "who": who, "engine": item["engine"], "pending": self._q.qsize()}


_SPEAKER: Speaker | None = None


def get_speaker() -> Speaker:
    """The ONE process-wide Speaker (the bridge owns it; everything else reaches it via POST /api/say so
    there is a single serialized sink). Constructed lazily — importing this module starts no thread."""
    global _SPEAKER
    if _SPEAKER is None:
        _SPEAKER = Speaker()
    return _SPEAKER
