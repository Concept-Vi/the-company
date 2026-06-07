"""voice/speakable.py — the SPEAKABLE LAYER: a brain reply → clean, expressive SPEECH.

ONE universal function — `speakable(reply, engine)` — that every voice path calls before text
reaches a TTS engine. It does two jobs Tim named (2026-06-07):

  V-C  STRIP NON-SPOKEN TEXT.  The brain replies like a TEXT model — markdown headings, **bold**,
       lists, `inline code`, ``` code fences ```, [links](url), blockquotes, tables, bare URLs,
       raw emoji, decorative symbol-runs. A TTS engine reads ALL of that aloud literally ("asterisk
       asterisk bold asterisk asterisk", "hash hash heading"). This layer normalises a reply to
       natural spoken prose BEFORE it hits the engine.

  V-D  EXPRESSION (engine-aware).  Some engines understand inline paralinguistic markup; most do
       not. We carry a SINGLE canonical tag vocabulary in the reply (engine-agnostic), and at synth
       time MAP each canonical tag to the SELECTED engine's real syntax — or STRIP it if that engine
       can't speak it (so an unsupported tag is never read aloud as the literal characters).

       Confirmed engine expression support (researched 2026-06-07, sources in the lane report):
         • orpheus    — angle-bracket paralinguistic tags: <laugh> <chuckle> <sigh> <cough>
                        <sniffle> <groan> <yawn> <gasp>   (canopyai/Orpheus-TTS README)
         • chatterbox — square-bracket tags: [laugh] [sigh] [gasp] [cough]  (Resemble AI)
         • cosyvoice  — fine-grained markers [laughter] [breath] + wrap <laughter>..</laughter>,
                        emphasis <strong>..</strong>  (CosyVoice2 paper / repo)
         • qwen3tts   — NO inline tags (instruction/description-driven only) → strip
         • xtts       — NO inline tags (reference-clip-driven) → strip
         • kokoro     — NO emotion tags (plain text) → strip

WHY a canonical set (not literal-preserve): the brain stays engine-agnostic — it can emit one
vocabulary and ANY engine renders or drops it correctly. Registry-is-truth (AGENTS rule 8): the
engine→syntax map is the single source; adding an engine adds a row, not a code path.

WHY here (stdlib only, no markdown lib): `voice/loop.py` runs in the .voice-venv (Python 3.12) and
the bridge runs the 3.14 runtime — this module is imported in BOTH, so it must stay stdlib-only
(regex), exactly like `loop.py`. No third-party markdown dependency.

WHERE it is applied (the pre-TTS seam, never the visible text):
  • bridge `/api/voice/stream` — clean the WHOLE reply, THEN sentence-split (cleaning per-chunk
    would split markdown across chunks). The `{type:reply}` event + trial recording stay RAW.
  • bridge `/api/voice/turn` (via loop.loop_turn) — clean before `speak()`; the returned `reply`
    stays RAW (the visible transcript).
  • bridge `/api/tts` — the generic text→wav path (speakReply text-replies, walkthrough narration);
    cleaning clean text is idempotent, so this is safe + complete.

FAIL LOUD (AGENTS rule 4): a non-string input raises; a reply that is NON-EMPTY but becomes EMPTY
after cleaning (e.g. a pure code-fence) raises — we never hand the engine silence and pretend a
turn spoke. An UNKNOWN engine does NOT hard-raise (that would make this a break-point for every
future engine) — it strips ALL expression markup (the worst outcome is reading "[sigh]" aloud) and
records a warning marker; markdown is still stripped. The fail-loud contract is about silent DROP
of the whole reply, not about being brittle to a new engine id.

This is a UNIVERSAL capability: any reply→speech path (the five-character voice trial, the debrief
host's narration, walkthrough narration, and any future read-back channel — phone, notification)
calls this ONE function. Reply→clean-expressive-speech, in one place.
"""
from __future__ import annotations

import re

# --- the canonical expression vocabulary (engine-agnostic) -------------------------------------
# The brain (or a persona) emits these in ONE syntax we pick as canonical: angle-bracket, matching
# the most expressive engine (Orpheus). At synth we map to the selected engine. A tag the engine
# can't speak is DROPPED (never read aloud).
CANONICAL_TAGS = ("laugh", "chuckle", "sigh", "cough", "sniffle", "groan", "yawn", "gasp", "breath")

# Per-engine expression capability — the SINGLE SOURCE (registry-is-truth). Adding an engine adds a
# row here, not a branch in code.
#   supports : the canonical tags this engine can actually voice (others are dropped for it).
#   render   : how to turn a canonical tag into THIS engine's real inline syntax.
# Engines absent from this map = no inline expression support → all tags stripped (e.g. qwen3tts,
# xtts, kokoro, and any unknown engine).
ENGINE_EXPRESSION: dict[str, dict] = {
    "orpheus": {
        "supports": ("laugh", "chuckle", "sigh", "cough", "sniffle", "groan", "yawn", "gasp"),
        "render": lambda t: f"<{t}>",                       # Orpheus: <laugh>
    },
    "chatterbox": {
        "supports": ("laugh", "sigh", "gasp", "cough"),
        "render": lambda t: f"[{t}]",                       # Chatterbox: [sigh]
    },
    "cosyvoice": {
        # CosyVoice2 uses [laughter]/[breath] markers; map 'laugh'→'laughter' to its token.
        "supports": ("laugh", "breath"),
        "render": lambda t: "[laughter]" if t == "laugh" else f"[{t}]",
    },
}

# A canonical tag in the reply text: <laugh> ... case-insensitive, the canonical bracket form.
_CANON_TAG_RE = re.compile(r"<(" + "|".join(CANONICAL_TAGS) + r")>", re.IGNORECASE)

# Emoji + pictographic symbol unicode ranges (surgical — does NOT strip accented letters, em-dashes,
# curly quotes, or other spoken punctuation). Covers the common emoji/symbol/dingbat/flag blocks.
_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"   # symbols & pictographs, emoticons, transport, supplemental, extended-A
    "\U00002600-\U000027BF"   # misc symbols + dingbats
    "\U0001F1E6-\U0001F1FF"   # regional indicators (flags)
    "\U00002190-\U000021FF"   # arrows
    "\U00002B00-\U00002BFF"   # misc symbols & arrows
    "\U0000FE00-\U0000FE0F"   # variation selectors
    "\U00002000-\U0000206F"   # general punctuation block? NO — handled below; keep dashes/quotes
    "]",
)
# (General-punctuation is intentionally NOT in the emoji strip — em/en dashes, ellipsis, curly
#  quotes belong to spoken prose. The block above re-narrowed: rebuild without it.)
_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0001F1E6-\U0001F1FF"
    "\U00002B00-\U00002BFF"
    "\U0000FE00-\U0000FE0F"
    "]",
)


def _strip_markdown(text: str) -> str:
    """Remove markdown control characters / structure, leaving the spoken content. Order matters:
    fenced code first (multi-line), then inline code, links/images, headings, emphasis, lists,
    blockquotes, tables, rules, then URLs + emoji + symbol runs. Each step explained inline."""
    t = text

    # ``` fenced code blocks ``` (and ~~~): drop ENTIRELY — code is not speech. Multi-line, so this
    # must run on the whole reply (the architectural reason cleaning is whole-reply, not per-chunk).
    t = re.sub(r"```.*?```", " ", t, flags=re.DOTALL)
    t = re.sub(r"~~~.*?~~~", " ", t, flags=re.DOTALL)
    # any dangling/unclosed fence marker → gone
    t = re.sub(r"`{3,}", " ", t)

    # `inline code` → keep the inner text, drop the backticks (e.g. `chat()` → chat())
    t = re.sub(r"`([^`]*)`", r"\1", t)

    # images ![alt](url) → the alt text (or nothing). Do BEFORE links (same bracket shape).
    t = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", t)
    # links [text](url) → just the visible text
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    # reference links [text][ref] → the text
    t = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", t)

    # headings: leading #'s on a line → drop the markers, keep the heading words (they ARE spoken)
    t = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", t)

    # blockquotes: leading > on a line → drop
    t = re.sub(r"(?m)^\s{0,3}>+\s?", "", t)

    # horizontal rules (--- *** ___ on their own line) → drop the whole line
    t = re.sub(r"(?m)^\s{0,3}([-*_])(\s*\1){2,}\s*$", "", t)

    # tables: a row that is mostly pipes/dashes (separator) → drop; data rows → pipes to commas
    t = re.sub(r"(?m)^\s*\|?[\s:\-\|]+\|[\s:\-\|]*$", "", t)   # |---|---| separator rows
    t = re.sub(r"(?m)^\s*\|(.+)\|\s*$",
               lambda m: ", ".join(c.strip() for c in m.group(1).split("|") if c.strip()), t)

    # list markers: leading -, *, + or 1. / 1) → drop the marker, keep the item text
    t = re.sub(r"(?m)^\s{0,8}[-*+]\s+", "", t)
    t = re.sub(r"(?m)^\s{0,8}\d+[.)]\s+", "", t)

    # emphasis: **bold** __bold__ *italic* _italic_ ~~strike~~ → keep the inner words
    t = re.sub(r"\*\*\*([^*]+)\*\*\*", r"\1", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"\*([^*]+)\*", r"\1", t)
    t = re.sub(r"___([^_]+)___", r"\1", t)
    t = re.sub(r"__([^_]+)__", r"\1", t)
    # single _italic_ — only when underscores hug a word (don't touch snake_case mid-word)
    t = re.sub(r"(?<![A-Za-z0-9_])_([^_]+)_(?![A-Za-z0-9_])", r"\1", t)
    t = re.sub(r"~~([^~]+)~~", r"\1", t)

    # bare URLs → drop (an engine reading "h t t p colon slash slash" is the bug). Keep surrounding
    # words. http(s):// and www. forms.
    t = re.sub(r"https?://\S+", " ", t)
    t = re.sub(r"(?<!\S)www\.\S+", " ", t)

    # emoji + pictographic symbols → drop (surgical ranges; accented letters/dashes/quotes survive)
    t = _EMOJI_RE.sub("", t)

    return t


def _normalise_whitespace_punct(text: str) -> str:
    """Collapse the gaps + stray symbol runs left by stripping into natural spoken spacing."""
    t = text
    # decorative symbol RUNS that aren't sentence punctuation (e.g. "==>", "***", "##", "•••")
    t = re.sub(r"[•◦▪‣·]+", " ", t)                          # bullet glyphs that leaked through
    t = re.sub(r"(?<!\d)[#*_~^|]{1,}(?!\w)", " ", t)         # leftover lone control chars
    # collapse 3+ repeated punctuation (keep up to "...") to avoid the engine over-pausing
    t = re.sub(r"([!?.,;:])\1{2,}", r"\1\1\1", t)
    # multiple blank lines / runs of whitespace → single space; trim line edges
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\s*\n\s*", " ", t)                          # newlines become spaces (one utterance)
    t = re.sub(r" {2,}", " ", t)
    # space before sentence punctuation left by removals: "word ." → "word."
    t = re.sub(r"\s+([,.!?;:])", r"\1", t)
    return t.strip()


def _apply_expression(text: str, engine: str | None) -> tuple[str, list[str]]:
    """Map every canonical <tag> to the SELECTED engine's real syntax, or DROP it if the engine
    can't speak it. Returns (text, warnings). This runs AFTER markdown stripping but is protected
    from it: the canonical tags are angle-bracket and the markdown pass does not touch <...> that
    aren't links/html-of-interest, so they survive to here intact (the test asserts this)."""
    caps = ENGINE_EXPRESSION.get((engine or "").strip().lower())
    warnings: list[str] = []

    def repl(m: re.Match) -> str:
        tag = m.group(1).lower()
        if caps and tag in caps["supports"]:
            return caps["render"](tag)                      # render in the engine's native syntax
        return ""                                           # unsupported here → DROP (never read aloud)

    out = _CANON_TAG_RE.sub(repl, text)
    if caps is None and _CANON_TAG_RE.search(text):
        # an unknown engine carried tags we stripped — surface it (not silent), but don't raise.
        warnings.append(f"engine {engine!r} unknown to the expression registry — all expression "
                        f"markup stripped (it would otherwise be read aloud literally)")
    return out, warnings


def speakable(reply: str, engine: str | None = None, *, warn=None) -> str:
    """THE universal transform: a brain reply → clean, engine-aware, speakable prose.

    reply  : the brain's reply text (may contain markdown + canonical <tag> expression markup).
    engine : the TTS engine the cleaned text is bound for (orpheus/chatterbox/cosyvoice/qwen3tts/
             xtts/kokoro/…). Decides which expression tags survive (in that engine's syntax) and
             which are dropped. None / unknown → all expression markup stripped (markdown still
             stripped); a warning is surfaced via `warn`.
    warn   : optional callable(str) the caller passes to receive non-fatal warnings (e.g. unknown
             engine). The bridge can emit these as a {type:note}/log line — fail-loud-LEGIBLE
             without breaking the turn.

    FAIL LOUD: non-string `reply` raises TypeError; a non-empty reply that cleans to EMPTY raises
    ValueError (we never hand the engine silence + pretend a turn spoke). Whitespace-only input is
    a degenerate already-empty case → returns "" (nothing was said to begin with)."""
    if not isinstance(reply, str):
        raise TypeError(f"speakable() needs a str reply, got {type(reply).__name__} (fail loud — "
                        f"a malformed reply must surface, never be coerced to silence)")

    if not reply.strip():
        return ""                                           # nothing to speak (and nothing was)

    stripped = _strip_markdown(reply)
    expressed, warnings = _apply_expression(stripped, engine)
    spoken = _normalise_whitespace_punct(expressed)

    # A NON-EMPTY reply that became EMPTY after cleaning = we'd hand the engine silence. That is a
    # real problem (e.g. the brain replied with ONLY a code fence) — fail loud, never a silent drop
    # of the whole reply.
    if not spoken:
        raise ValueError(
            f"speakable(): reply was non-empty but cleaned to nothing — refusing to synth silence "
            f"(the reply was all non-spoken content, e.g. a code fence or symbols). "
            f"Original (first 200 chars): {reply[:200]!r}")

    for w in warnings:
        if warn:
            try:
                warn(w)
            except Exception:
                pass                                        # a broken warn-sink must not break speech

    return spoken
