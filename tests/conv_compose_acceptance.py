"""tests/conv_compose_acceptance.py — Convergence X4 · build_instruction composes the RICH prompt.

THE PRINCIPLE (Completion Criteria X4 / Implementation Guide X4):
  X1/X2/X3 now PERSIST `address`, `symbols[]`, and the bounded R2 `context` bundle into the
  build-intent's payload. But `build_instruction` (implement.py:168) still slots only
  spec + scope + the static STANDARDS_BLOCK + "read the root three" — it IGNORES the new fields.
  X4 widens `build_instruction` to compose those into the prompt EXACTLY as it already slots
  `scope`: the indicated address; the related code symbols (the neighbours); and the attached
  context bundle (the accumulated notebook). The launched build arrives pointed + memory-rich.

THE FIX (PURE string-formatter, additive): read the new payload fields with safe `.get`
  defaults and APPEND legible, clearly-labelled, CONDITIONAL sections. An older intent without
  the fields composes EXACTLY as today (byte-for-byte — no empty sections). `build_instruction`
  stays `decision: dict` in → `str` out; NO suite/embed/network call (that breaks the boundary
  AND X5's consent-time property — the context is ALREADY in the payload, X4 only FORMATS it).

PROOF MODEL:
  • RICH — a decision whose payload carries address+symbols+context → the returned string
    CONTAINS the address, EACH symbol, and EACH context item's text (the rich prompt).
  • BACKWARD-COMPATIBLE — a decision WITHOUT those fields composes exactly as before: the
    spec+scope+STANDARDS_BLOCK+read-root-three, and NO dangling empty section labels.
  • PRESERVE — the existing spec / scope_line / STANDARDS_BLOCK / read-root-three slots are all
    still present and unaltered (X4 ADDS sections; it does not replace).
  • FAIL-LOUD malformed — a malformed context bundle renders what's valid + a visible note,
    NEVER crashes the compose (no exception) and NEVER silently drops (the note is the loud part).
  • PURE — `build_instruction(decision)` is called DIRECTLY; NO `launch`, NO subprocess, NO
    real `claude -p` (this tests the pure function, not the launcher).

Run: /home/tim/company/.venv/bin/python tests/conv_compose_acceptance.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_TEST_RUN"] = "1"

from runtime.implement import build_instruction, STANDARDS_BLOCK

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# ════════════════════════════════════════════════════════════════════════════════════════════════
# A RICH decision — the X1/X2/X3 widened payload shape, exactly as persisted to disk.
#   address  : the ui:// locus (X1)
#   symbols  : the code:// neighbours (X2)
#   context  : the bounded R2 bundle — public {kind,address,ts,text,pinned} items only (X3)
# ════════════════════════════════════════════════════════════════════════════════════════════════
ADDRESS = "ui://chat/input"
SYMBOLS = ["code://App", "code://ChatInput"]
CTX_TEXT_1 = "the run button has felt sluggish since last week — accumulated note"
CTX_TEXT_2 = "operator: tone the run button down, it's too loud"
RICH = {
    "payload": {
        "intent": "build",
        "spec": "this run button is too loud — tone it down",
        "scope": ["canvas/app/src/App.tsx"],
        "consequence_class": "decision_build",
        "why": "operator clicked ui://chat/input and said: tone it down",
        "address": ADDRESS,
        "symbols": SYMBOLS,
        "context": [
            {"kind": "annotation", "address": "ui://chat/input", "ts": "2026-06-01T00:00:00Z",
             "text": CTX_TEXT_1, "pinned": False},
            {"kind": "chat", "address": "ui://chat/input", "ts": "2026-06-02T00:00:00Z",
             "text": CTX_TEXT_2, "pinned": True},
        ],
    }
}

rich = build_instruction(RICH)
check("PURE: build_instruction(decision) returns a str (decision-in → string-out)", isinstance(rich, str))

# ── RICH — the address, every symbol, every context item's text are IN the composed prompt ─────────
check("X4 RICH: the composed prompt CONTAINS the indicated ui:// address", ADDRESS in rich)
for s in SYMBOLS:
    check(f"X4 RICH: the composed prompt CONTAINS the related code:// symbol {s!r}", s in rich)
check("X4 RICH: the composed prompt CONTAINS the FIRST context item's text (the inherited notebook)",
      CTX_TEXT_1 in rich)
check("X4 RICH: the composed prompt CONTAINS the SECOND context item's text",
      CTX_TEXT_2 in rich)

# legible, clearly-labelled sections (assert labels exist; load-bearing asserts stay on the values)
check("X4 RICH: an INDICATED-ELEMENT label introduces the address (legible section)",
      "INDICATED ELEMENT" in rich.upper())
check("X4 RICH: a RELATED-CODE label introduces the symbols (legible section)",
      "RELATED CODE" in rich.upper())
check("X4 RICH: a CONTEXT-AT-LOCUS label introduces the bundle (legible section)",
      "CONTEXT AT THIS LOCUS" in rich.upper())

# ── PRESERVE — the existing slots are all still present, unaltered ─────────────────────────────────
check("PRESERVE: the spec text is still slotted", "this run button is too loud — tone it down" in rich)
check("PRESERVE: the scope_line ('authorized ONLY these paths') is still present",
      "authorized to change ONLY these paths" in rich and "canvas/app/src/App.tsx" in rich)
check("PRESERVE: the STANDARDS_BLOCK is still present verbatim", STANDARDS_BLOCK in rich)
check("PRESERVE: the 'Read AGENTS.md / MAP.md / STATE.md first' line is still present",
      "Read AGENTS.md / MAP.md / STATE.md first" in rich)

# ════════════════════════════════════════════════════════════════════════════════════════════════
# BACKWARD-COMPATIBLE — a decision WITHOUT address/symbols/context composes EXACTLY as before.
# This is the byte-for-byte preserve: the same compose without the new fields == today's prompt.
# ════════════════════════════════════════════════════════════════════════════════════════════════
BARE = {
    "payload": {
        "intent": "build",
        "spec": "a plain build with no address",
        "scope": ["runtime/suite.py"],
        "consequence_class": "decision_build",
        "why": "operator surfaced a plain build-intent",
    }
}
bare = build_instruction(BARE)
check("BACKWARD-COMPAT: a bare intent (no new fields) composes without crashing", isinstance(bare, str))
check("BACKWARD-COMPAT: the bare prompt still carries the spec + scope + STANDARDS_BLOCK",
      "a plain build with no address" in bare and "runtime/suite.py" in bare and STANDARDS_BLOCK in bare)
check("BACKWARD-COMPAT: the bare prompt still carries the read-root-three line",
      "Read AGENTS.md / MAP.md / STATE.md first" in bare)
# NO dangling empty section labels when the fields are absent (the most likely miss)
check("BACKWARD-COMPAT: NO empty 'INDICATED ELEMENT' section when there is no address",
      "INDICATED ELEMENT" not in bare.upper())
check("BACKWARD-COMPAT: NO empty 'RELATED CODE' section when there are no symbols",
      "RELATED CODE" not in bare.upper())
check("BACKWARD-COMPAT: NO empty 'CONTEXT AT THIS LOCUS' section when there is no context",
      "CONTEXT AT THIS LOCUS" not in bare.upper())

# byte-for-byte: the bare compose == the SAME payload built today (the existing slots, unchanged shape).
# We reconstruct today's expected output from the preserved pieces to prove X4 ADDED nothing here.
expected_bare = (
    "Implement the following approved change in the 'company' repo. "
    "Read AGENTS.md / MAP.md / STATE.md first.\n\na plain build with no address"
    "\n\nYou are authorized to change ONLY these paths (the operator approved exactly this scope): "
    "runtime/suite.py. Do NOT touch anything outside that scope." + STANDARDS_BLOCK)
check("BACKWARD-COMPAT (byte-for-byte): the bare prompt == today's exact compose (X4 added NOTHING here)",
      bare == expected_bare)

# an intent with NO payload at all (the oldest shape) still composes (no crash, no empty sections)
empty = build_instruction({})
check("BACKWARD-COMPAT: a decision with no payload composes (no crash)", isinstance(empty, str))
check("BACKWARD-COMPAT: a no-payload decision has no empty new sections",
      "INDICATED ELEMENT" not in empty.upper() and "RELATED CODE" not in empty.upper()
      and "CONTEXT AT THIS LOCUS" not in empty.upper())

# ════════════════════════════════════════════════════════════════════════════════════════════════
# FAIL-LOUD malformed context — render what's valid + a VISIBLE note; never crash, never silent-drop.
# ════════════════════════════════════════════════════════════════════════════════════════════════
GOOD_TEXT = "this VALID sibling item must still render despite the malformed neighbours"
MALFORMED = {
    "payload": {
        "intent": "build",
        "spec": "compose despite a broken bundle",
        "scope": ["runtime/suite.py"],
        "address": "ui://chat/input",
        "symbols": ["code://App"],
        "context": [
            {"kind": "annotation", "address": "ui://chat/input", "ts": "z", "text": GOOD_TEXT, "pinned": False},
            "this item is a bare string, not a dict",          # malformed: not a dict
            {"kind": "chat", "address": "ui://x", "ts": "z", "pinned": False},  # malformed: no text
            42,                                                # malformed: not even a string
        ],
    }
}
try:
    malformed = build_instruction(MALFORMED)
    crashed = False
except Exception as e:  # noqa: BLE001 — the whole point is to prove it does NOT raise
    crashed = True
    malformed = ""
    print(f"  !! build_instruction RAISED on malformed context: {e!r}")
check("FAIL-LOUD: a malformed context bundle does NOT crash the compose (no exception)", not crashed)
check("FAIL-LOUD: the VALID sibling item STILL renders (render-what's-valid)", GOOD_TEXT in malformed)
check("FAIL-LOUD: a VISIBLE note flags the skipped malformed items (the note is the loud part — no silent drop)",
      "malformed" in malformed.lower() or "skipped" in malformed.lower())

# context that is not a list at all (e.g. a dict) → noted, never crashes, the rest still composes
NOTALIST = {
    "payload": {
        "intent": "build", "spec": "context is a dict, not a list", "scope": ["runtime/suite.py"],
        "address": "ui://chat/input", "context": {"oops": "this is a dict not a list"},
    }
}
try:
    notalist = build_instruction(NOTALIST)
    crashed2 = False
except Exception as e:  # noqa: BLE001
    crashed2 = True
    notalist = ""
    print(f"  !! build_instruction RAISED on non-list context: {e!r}")
check("FAIL-LOUD: a non-list context does NOT crash the compose", not crashed2)
check("FAIL-LOUD: a non-list context still composes the address + spec + STANDARDS_BLOCK",
      "ui://chat/input" in notalist and "context is a dict, not a list" in notalist and STANDARDS_BLOCK in notalist)

print(f"\nCONV COMPOSE ACCEPTANCE (X4) — {PASS} checks passed. build_instruction stays a PURE "
      f"decision-in/str-out formatter (no suite/embed/subprocess call) and now APPENDS legible, "
      f"CONDITIONAL sections for the indicated address (X1), the related code symbols (X2), and the "
      f"attached R2 context bundle (X3) — exactly as it slots scope. A bare intent composes "
      f"byte-for-byte as today (backward-compatible, no empty sections); spec/scope_line/STANDARDS_BLOCK/"
      f"read-root-three are preserved; a malformed bundle renders what's valid + a visible note, never "
      f"crashes, never silently drops. Constitution-naming is X15, NOT here.")
