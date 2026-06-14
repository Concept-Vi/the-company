"""mcp_face/tools/cc_voice.py — give text a VOICE through the company MCP (the fabric's wire to the
resident TTS engine). File-drop tool (pkgutil auto-register). Surfaces runtime/cc_voice.py, which
reuses the existing voice services — it does NOT reinvent TTS.

## Ops
  op="engines" — which TTS engines exist (registry) and which is currently UP.
  op="speak"   — render `text` to a WAV via the running engine; returns the file path (+ bytes).
                 Playback is device-side (operator/UI plays the file). Optional `voice`.
"""
from __future__ import annotations

from typing import Literal

OPS = ("engines", "speak")


def register(mcp, suite):
    @mcp.tool()
    def cc_voice(op: Literal["engines", "speak"], text: str = "", voice: str = "") -> dict:
        """Give text a VOICE through the Company's resident TTS engine (building block for voiced
        cross-session conversation). Pick `op`:

          op="engines" — list TTS engines + which is up (bring one up with `company up @xsession`).
          op="speak"   — render `text` to a WAV (returns the path; play it device-side). Optional `voice`.
        """
        from runtime import cc_voice as v
        try:
            if op == "engines":
                return {"op": "engines", **v.engines()}
            if op == "speak":
                if not text:
                    raise ValueError("cc_voice(op='speak') requires `text`.")
                return {"op": "speak", **v.speak(text, voice=voice or None)}
        except v.VoiceError as e:
            return {"op": op, "ok": False, "error": str(e)}
        raise ValueError(f"cc_voice: unknown op {op!r} — one of {OPS}.")
