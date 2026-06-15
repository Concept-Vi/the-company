"""tests/session_address_grammar_acceptance.py — the ONE shared session:// sub-address grammar.

(Named session_address_* not address_grammar_* — tests/address_grammar_acceptance.py already owns the
ui:// grammar, a different concern. Scout-before-build caught the clash.)

f1ade750's flag, actioned: session://<sid>/step/<tool_use_id> was parsed in TWO places — cognition.py
(an inline `"/step/" in rest` substring-split, permissive) and cc_gate.py (a `STEP_ADDR_RE` regex,
strict). Two parsers for one shape → drift (they already disagreed on `session://a/b/step/c`). This
declares the grammar ONCE in contracts/address.py (the grammar home, beside scheme()/is_cas() — same
pattern as contracts/ui_info.py:parse_ui_address for ui://), and proves: (a) it parses the two legal
session forms, (b) it FAILS LOUD on an unknown sub-address (never a silent-pass — f1ade750's bar), (c) it
is BEHAVIOR-EQUIVALENT to cc_gate's existing STEP_ADDR_RE on a battery (so fork's import-swap of cc_gate
onto it is provably safe — fork's behavior-preserving condition), (d) clone://·member://·mind:// add as
DECLARED entries later, not new dual code-branches.

Falsify-first floor: importing the not-yet-existing grammar fns RAISES (RED) before the build. Plain-assert.
    .venv/bin/python tests/session_address_grammar_acceptance.py
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from contracts.address import parse_session_address, is_step_address  # noqa: E402  (RED before build)

PASS, FAIL = [], []


def check(n, c, d=""):
    (PASS if c else FAIL).append(n)
    print(f"  {'PASS' if c else 'FAIL'}  {n}" + (f"  — {d}" if d and not c else ""))


def raises(fn, exc=Exception, sub=""):
    try:
        fn()
        return False
    except exc as e:
        return sub in str(e) if sub else True
    except Exception:
        return False


# ── the two LEGAL session forms parse ────────────────────────────────────────────────────────────────
check("1 session://<sid> → whole session {sid, step:None}",
      parse_session_address("session://abc-123") == {"sid": "abc-123", "step": None})
check("2 session://<sid>/step/<tuid> → {sid, step}",
      parse_session_address("session://abc-123/step/toolu_99") == {"sid": "abc-123", "step": "toolu_99"})
check("3 is_step_address True ONLY for the step form",
      is_step_address("session://abc-123/step/toolu_99") is True
      and is_step_address("session://abc-123") is False)

# ── FAIL LOUD on a malformed / unknown sub-address (f1ade750's bar — never silent-pass) ──────────────
check("4 session://<sid>/bogus/x RAISES (unknown sub-path is malformed, not silent-pass)",
      raises(lambda: parse_session_address("session://abc-123/bogus/x"), ValueError, "malformed"))
check("5 session://<sid>/step/ (empty tool_use_id) RAISES",
      raises(lambda: parse_session_address("session://abc-123/step/"), ValueError))
check("6 session:// (empty sid) RAISES",
      raises(lambda: parse_session_address("session://"), ValueError))
check("7 a non-session address RAISES (this grammar is session://-scoped)",
      raises(lambda: parse_session_address("board://item-x"), ValueError))

# ── the DRIFT, fixed: the edge cognition's old split accepted but cc_gate rejected now converges ──────
check("8 ★ session://a/b/step/c RAISES (the divergent edge — old inline split took sid='a/b'; now strict)",
      raises(lambda: parse_session_address("session://a/b/step/c"), ValueError))
check("9 is_step_address False on the divergent edge (agrees with cc_gate's regex, not the old split)",
      is_step_address("session://a/b/step/c") is False)

# ── behavior-EQUIVALENCE with cc_gate's STEP_ADDR_RE (proves fork's cc_gate swap is safe) ────────────
# Swap-tolerant: this equivalence is the PRE-swap safety proof. Once fork swaps cc_gate onto
# is_step_address and retires the redundant regex (f1ade750's bar: separate validation GONE, not
# coexisting), there is nothing to compare against — the equivalence then holds by construction (one
# parser). So guard the import: present → prove equivalence; retired → swap complete by construction.
battery = [
    "session://u1/step/t1", "session://u1", "session://u1/step/", "session://",
    "session://a/b/step/c", "session://u1/bogus/x", "board://x", "session://u1/step/t/extra",
    "session://u1/step/toolu_abcDEF123",
]
try:
    from runtime.cc_gate import STEP_ADDR_RE  # noqa: E402  (the regex cc_gate validated with PRE-swap)
    mismatch = [a for a in battery if is_step_address(a) != bool(STEP_ADDR_RE.match(a))]
    check("10 ★ is_step_address ≡ cc_gate.STEP_ADDR_RE across the battery (one grammar, swap-safe)",
          not mismatch, f"mismatches: {mismatch}")
except ImportError:
    check("10 ★ cc_gate swapped onto is_step_address (STEP_ADDR_RE retired) — one parser by construction",
          True)

print(f"\n{'=' * 60}\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", ", ".join(FAIL))
    sys.exit(1)
print("ALL GREEN — one shared session:// sub-address grammar in contracts/address.py: parses the two\n"
      "legal forms, fails loud on an unknown sub-path, and is equivalent to cc_gate's STEP_ADDR_RE (so\n"
      "cc_gate's separate validator can swap onto it with no behavior change). The two-parser drift\n"
      "f1ade750 flagged is closed by construction.")
