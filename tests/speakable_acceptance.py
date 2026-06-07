"""tests/speakable_acceptance.py — the SPEAKABLE LAYER (V-C strip + V-D expression) by USE.

Proves the ONE universal transform `voice.speakable.speakable(reply, engine)` that every voice path
calls before text reaches a TTS engine:

  V-C  a brain reply full of TEXT-MODEL formatting (markdown headings/lists/**bold**/`code`/```fences```/
       [links](url)/blockquotes/tables/bare URLs/emoji/symbol runs) is cleaned to natural spoken prose —
       NO markdown control chars, NO code fences, NO raw URLs hit the engine.

  V-D  the SAME reply's canonical expression markup (<laugh>, <sigh>, …) is PRESERVED in the SELECTED
       engine's real syntax for engines that support it (orpheus <laugh>, chatterbox [sigh],
       cosyvoice [laughter]) and STRIPPED for engines that do NOT (qwen3tts / xtts / kokoro / unknown)
       so it is never read aloud as literal characters.

This is a PURE-FUNCTION test: it needs NO services (no TTS engine, no bridge, no GPU). The live
streaming circuit (audio → STT → brain → speakable → TTS → spoken WAV) needs the engines up and is the
needs-services / needs-Tim's-ear layer, flagged in the lane report — NOT faked here.

Run: /home/tim/company/.venv/bin/python tests/speakable_acceptance.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from voice.speakable import speakable, ENGINE_EXPRESSION, CANONICAL_TAGS   # noqa: E402

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


print("SPEAKABLE LAYER — V-C strip + V-D engine-aware expression, by USE (pure fn, no services)")

# A representative brain reply: every text-model formatting kind Tim named, PLUS a canonical
# expression tag (Orpheus-style <laugh>) the brain might emit.
REPLY = """# The Scheduler Memo Gate

The memo gate means **re-run only what changed**. Here's how it works <laugh>:

- A node fires when its input *addresses* resolve in the `store`.
- The gate compares the new content hash to the cached one.
- See the [contracts](https://example.com/contracts/C5) for the full spec.

```python
def memo(node):
    return cache.get(node.hash)
```

> It is reactive, not imperative.

| Field | Meaning |
|-------|---------|
| hash  | content id |

Visit https://example.com/docs for more. That's the gist! 🎉🚀"""


# ---- V-C: the cleaned text is clean prose, for an engine WITHOUT expression (kokoro) ----
print("\n[V-C] strip non-spoken text (engine=kokoro — no expression markup, pure strip)")
clean = speakable(REPLY, "kokoro")
print(f"    cleaned (first 160): {clean[:160]!r}")

check("no markdown heading hash (#) survives", "#" not in clean)
check("no bold/italic asterisks survive", "*" not in clean)
check("no code-fence backticks survive", "`" not in clean)
check("no code-fence body leaked (def memo)", "def memo" not in clean and "cache.get" not in clean)
check("no markdown link syntax [..](..) survives", "](" not in clean and "[contracts]" not in clean)
check("link visible text IS kept ('contracts')", "contracts" in clean)
check("no raw URL survives (https://)", "https://" not in clean and "example.com" not in clean)
check("no blockquote marker (>) survives", ">" not in clean)
check("no table pipe (|) survives", "|" not in clean)
check("no emoji survives", "🎉" not in clean and "🚀" not in clean)
check("heading WORDS are kept (spoken)", "Scheduler Memo Gate" in clean)
check("the actual prose survives ('re-run only what changed')", "re-run only what changed" in clean)
check("non-empty reply cleaned to non-empty prose", len(clean.strip()) > 0)
# kokoro has no expression support → the <laugh> tag must be GONE (not read aloud)
check("kokoro (no expression) DROPS the <laugh> tag", "<laugh>" not in clean and "laugh" not in clean.lower())


# ---- V-D: engine-aware expression — preserved (mapped) for supporting engines, stripped otherwise ----
print("\n[V-D] expression markup mapped per engine (supported → native syntax; unsupported → stripped)")

orph = speakable(REPLY, "orpheus")
check("orpheus PRESERVES <laugh> in its native angle-bracket syntax", "<laugh>" in orph)
check("orpheus output is still clean prose (no markdown)", "#" not in orph and "`" not in orph and "](" not in orph)

cbox = speakable(REPLY, "chatterbox")
check("chatterbox MAPS <laugh> → its [laugh] syntax", "[laugh]" in cbox)
check("chatterbox does NOT carry the angle-bracket form", "<laugh>" not in cbox)

cosy = speakable(REPLY, "cosyvoice")
check("cosyvoice MAPS 'laugh' → its [laughter] token", "[laughter]" in cosy)
check("cosyvoice does NOT carry the angle-bracket form", "<laugh>" not in cosy)

for eng in ("qwen3tts", "xtts"):
    out = speakable(REPLY, eng)
    check(f"{eng} (no inline expression) STRIPS the tag (no <laugh>/[laugh]/laughter literal)",
          "<laugh>" not in out and "[laugh]" not in out and "laughter" not in out.lower())

# the canonical tag SURVIVES the markdown pass for a supporting engine (the protect-from-strip proof)
print("\n[V-D] expression tags survive the markdown strip (not eaten as link/html syntax)")
tag_only = "Well **done**! <sigh> That `code` was rough. <gasp>"
o = speakable(tag_only, "orpheus")
check("orpheus keeps BOTH <sigh> and <gasp> through the markdown pass", "<sigh>" in o and "<gasp>" in o)
check("...while still stripping the **bold** and `code` markers around them",
      "*" not in o and "`" not in o and "done" in o and "code" in o)


# ---- unknown engine: strip-all-expression + warn, never hard-raise (a future engine isn't a break point) ----
print("\n[unknown engine] strips expression + warns (no hard-raise — markdown still stripped)")
warns = []
out_unknown = speakable("Hi **there** <laugh> friend.", "some-future-engine-v9", warn=warns.append)
check("unknown engine still strips markdown (no **)", "*" not in out_unknown and "there" in out_unknown)
check("unknown engine strips the unsupported tag (no <laugh>)", "<laugh>" not in out_unknown)
check("unknown engine SURFACES a warning (not silent)", len(warns) == 1 and "unknown" in warns[0].lower())


# ---- FAIL LOUD: bad input + empty-after-clean ----
print("\n[fail loud] bad input + empty-after-clean never silently drop the reply")
try:
    speakable(12345, "orpheus")          # type: ignore[arg-type]
    check("non-string reply raises TypeError", False)
except TypeError:
    check("non-string reply raises TypeError", True)

try:
    # a reply that is ENTIRELY a code fence → cleans to nothing → must fail loud (never synth silence)
    speakable("```\njust code, no prose\n```", "kokoro")
    check("non-empty reply that cleans to EMPTY raises ValueError (no silent silence)", False)
except ValueError:
    check("non-empty reply that cleans to EMPTY raises ValueError (no silent silence)", True)

check("truly-empty input returns '' (nothing was said to begin with)", speakable("   ", "kokoro") == "")


# ---- registry-is-truth: the expression map is the single source ----
print("\n[registry] the engine→expression map is the single source (registry-is-truth)")
check("orpheus/chatterbox/cosyvoice are registered with expression support",
      all(e in ENGINE_EXPRESSION for e in ("orpheus", "chatterbox", "cosyvoice")))
check("every supported tag is in the canonical vocabulary",
      all(t in CANONICAL_TAGS for caps in ENGINE_EXPRESSION.values() for t in caps["supports"]))


# ---- idempotence: cleaning already-clean text is a no-op (safe on the generic /api/tts path) ----
print("\n[idempotence] cleaning already-clean prose is a no-op (safe everywhere)")
plain = "Good evening. This is the company speaking. Let us begin."
check("already-clean prose passes through unchanged", speakable(plain, "kokoro") == plain)


# ---- THE WIRING by USE: loop.loop_turn (backs /api/voice/turn) actually CLEANS before speak() ----
# Service-free: monkeypatch the two service deps (listen=STT, speak=TTS) + inject the brain, so this
# exercises the REAL loop_turn code path that the bridge's /api/voice/turn uses — proving the wiring,
# not just the pure function. (No bridge, no engines, no :8771 — deterministic + isolates THIS wiring.)
print("\n[wiring] voice.loop.loop_turn cleans the reply before speak() (the /api/voice/turn path)")
import voice.loop as _L                                      # noqa: E402
_cap = {}
_orig_listen, _orig_speak = _L.listen, _L.speak
try:
    _L.listen = lambda *a, **k: {"text": "tell me about the gate", "provider": "stub"}
    # speak(text, engine, voice=None, speed=1.0) — capture the TEXT that reaches TTS (loop.py:97)
    _L.speak = lambda text, engine, voice=None, speed=1.0: (_cap.__setitem__("text", text),
                                                            _cap.__setitem__("engine", engine), b"RIFF0000")[2]
    RAW = "# Hi\n\nWelcome **there** `code` <laugh>. See [docs](https://x.io)."
    out = _L.loop_turn(b"audiobytes", "pip",                 # pip's engine is orpheus (supports <laugh>)
                       think_fn=lambda t: {"reply": RAW})
    sent_to_tts = _cap.get("text", "")
    check("loop_turn sent CLEANED text to speak() (no markdown ** ` # ](  )",
          all(x not in sent_to_tts for x in ("**", "`", "#", "](")) and "https://" not in sent_to_tts)
    check("loop_turn MAPPED the <laugh> tag for pip's orpheus engine", "<laugh>" in sent_to_tts)
    check("loop_turn engine resolved to orpheus (pip's engine)", _cap.get("engine") == "orpheus")
    check("loop_turn RETURNED reply stays RAW (the visible transcript)", out["reply"] == RAW)
finally:
    _L.listen, _L.speak = _orig_listen, _orig_speak         # restore (don't leak the monkeypatch)


print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} — {PASS} checks passed")
sys.exit(0 if ok else 1)
