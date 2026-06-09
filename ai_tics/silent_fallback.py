"""ai_tics/silent_fallback.py — SEED AI-tic: silent-fallback.

The generic-AI tell of silently routing around a problem (use a different engine/model, swallow an
error, pretend success) instead of failing loud — a NAMED Tim frustration (no-silent-failures;
make-each-thing-work). See runtime/ai_tics.py + ai_tics/AGENTS.md.
"""

AI_TIC = {
    "id": "silent_fallback",
    "label": "silent-fallback",
    "markers": ["falls back to", "as a fallback", "if that fails, use", "just use a different", "silently", "best-effort"],
    "desc": "routing around a problem / swallowing an error instead of failing loud (a named Tim frustration)",
}
