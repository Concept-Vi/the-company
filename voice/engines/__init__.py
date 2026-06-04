"""voice/engines/ — one HTTP TTS service per trial voice, each MIRRORING voice/tts_service.py's contract.

The contract (identical to the Kokoro service the bridge already proxies):
  POST /tts  {text, voice?, speed?}  -> audio/wav bytes
  GET  /voices                       -> {"voices": [...], "default": ...}
  GET  /health (and /)               -> {"ok": true}
  fail loud: any error -> 500 {"error": "<Type>: <msg>"} (never a silent empty wav)

Port map (the SHARED contract the runtime-backend builder relies on; bridge routes by `engine`):
  kokoro:4123 (existing) · chatterbox:4124 · orpheus:4125 · cosyvoice:4126 · xtts:4127 · qwen3tts:4128

Each engine runs in its OWN venv/process (their deps conflict — vLLM, torch pins, a git-clone repo) on
its own port; see voice/engines/REQUIREMENTS.md for the exact per-engine install + run command. Heavy
model imports are GUARDED inside a lazy _engine() so importing the wrapper module never crashes — a
missing lib fails loud with a precise "pip install X" message only when /tts is actually called.
"""
