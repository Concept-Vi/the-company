"""tests/conv_constitution_acceptance.py — Convergence X15 · build_instruction names the GOVERNING
module constitution(s) — the constitution-hop.

THE PRINCIPLE (Completion Criteria X15 / Implementation Guide X15):
  Today the launch instruction names ONLY the ROOT three — "Read AGENTS.md / MAP.md / STATE.md
  first." But every scope file sits UNDER a module dir whose own `AGENTS.md` declares (via
  `governs:`) the laws of edits there (`runtime/AGENTS.md`, `store/AGENTS.md`, `canvas/AGENTS.md`,
  …). X15 derives the GOVERNING module's `AGENTS.md` from the scope's parent dirs and NAMES them
  in the instruction ALONGSIDE the root three — so the build reads the laws of exactly where you
  pointed. Instruction-naming is the mechanism (no Claude-Code auto-load assumption).

THE FIX (PURE string-formatter, additive): from `payload["scope"]` (repo-relative files), walk each
  file's parent dirs UP to the nearest ancestor that HAS an `AGENTS.md` under the repo (read-only,
  deterministic existence check against REPO_ROOT — NOT cwd), dedupe, and APPEND a clearly-labelled
  adjacent line naming those module `AGENTS.md` paths. The existing "Read AGENTS.md / MAP.md /
  STATE.md first." sentence is PRESERVED unaltered (a NEW adjacent line is added, never an edit of
  the root sentence). `build_instruction` stays `decision: dict` in → `str` out; NO suite/embed/
  network call — only a read-only `os.path.exists` stat, which is deterministic and pure-of-IO-side-
  effects (X4's boundary + X5's consent-time property both hold).

PROOF MODEL:
  • HOP — scope=["runtime/suite.py","store/fs_store.py"] → the prompt names runtime/AGENTS.md AND
    store/AGENTS.md (the governing module constitutions), alongside the preserved root three.
  • WALK-UP — scope=["canvas/app/src/App.tsx"] (parent dirs canvas/app/src + canvas/app have NO
    AGENTS.md; canvas/ DOES) → the prompt names canvas/AGENTS.md (the NEAREST governing ancestor),
    proving the walk-up — NOT merely the immediate parent (which would name nothing here).
  • DEDUPE — two files in the same module dir → that module's AGENTS.md is named ONCE.
  • BACKWARD-COMPATIBLE — empty/no scope → JUST the root three, no module line, no crash. A scope
    file under NO module dir (no ancestor AGENTS.md) → just the root three (fail-loud-legible, no crash).
  • PRESERVE — the root "Read AGENTS.md / MAP.md / STATE.md first." line, the spec, the scope_line,
    the STANDARDS_BLOCK, and X4's rich context block (address/symbols/context) are all still present
    and unaltered (X15 ADDS the module-constitution naming; it does not replace).
  • PURE — `build_instruction(decision)` is called DIRECTLY; NO `launch`, NO subprocess, NO real
    `claude -p` (this tests the pure function, not the launcher).

Run: /home/tim/company/.venv/bin/python tests/conv_constitution_acceptance.py
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


ROOT_LINE = "Read AGENTS.md / MAP.md / STATE.md first"


# ════════════════════════════════════════════════════════════════════════════════════════════════
# HOP — two files in two DIFFERENT module dirs → BOTH governing module AGENTS.md are named.
#   runtime/suite.py  → runtime/AGENTS.md     store/fs_store.py → store/AGENTS.md
# (sanity-check the worktree really has those module constitutions, so the hop has something to name)
# ════════════════════════════════════════════════════════════════════════════════════════════════
assert os.path.exists(os.path.join(ROOT, "runtime", "AGENTS.md")), "fixture: runtime/AGENTS.md must exist"
assert os.path.exists(os.path.join(ROOT, "store", "AGENTS.md")), "fixture: store/AGENTS.md must exist"

HOP = {"payload": {"intent": "build", "spec": "touch two modules",
                   "scope": ["runtime/suite.py", "store/fs_store.py"],
                   "consequence_class": "decision_build"}}
hop = build_instruction(HOP)
check("PURE: build_instruction(decision) returns a str (decision-in → string-out)", isinstance(hop, str))
check("X15 HOP: the prompt names the GOVERNING module constitution runtime/AGENTS.md", "runtime/AGENTS.md" in hop)
check("X15 HOP: the prompt names the GOVERNING module constitution store/AGENTS.md", "store/AGENTS.md" in hop)
check("X15 HOP: the root three line is STILL present (the module naming is ALONGSIDE, not instead)",
      ROOT_LINE in hop)
# the module naming is clearly labelled as the governing module constitution(s) (legible, not a bare path dump)
check("X15 HOP: a clear label introduces the module constitution(s) (legible section)",
      "governing module" in hop.lower() and "constitution" in hop.lower())


# ════════════════════════════════════════════════════════════════════════════════════════════════
# WALK-UP — a deeply-nested scope file whose immediate parent dirs have NO AGENTS.md.
#   canvas/app/src/App.tsx → canvas/app/src (no AGENTS.md) → canvas/app (no AGENTS.md) → canvas (HAS)
# This is what discriminates walk-up from immediate-parent-only: immediate-parent would name NOTHING.
# ════════════════════════════════════════════════════════════════════════════════════════════════
assert os.path.exists(os.path.join(ROOT, "canvas", "AGENTS.md")), "fixture: canvas/AGENTS.md must exist"
assert not os.path.exists(os.path.join(ROOT, "canvas", "app", "src", "AGENTS.md")), \
    "fixture: canvas/app/src must NOT have its own AGENTS.md (else this doesn't test walk-up)"

NESTED = {"payload": {"intent": "build", "spec": "tweak the canvas surface",
                      "scope": ["canvas/app/src/App.tsx"], "consequence_class": "decision_build"}}
nested = build_instruction(NESTED)
check("X15 WALK-UP: a deeply-nested scope file names the NEAREST governing ancestor canvas/AGENTS.md",
      "canvas/AGENTS.md" in nested)
check("X15 WALK-UP: it does NOT invent a non-existent canvas/app/src/AGENTS.md (only EXISTING constitutions)",
      "canvas/app/src/AGENTS.md" not in nested and "canvas/app/AGENTS.md" not in nested)


# ════════════════════════════════════════════════════════════════════════════════════════════════
# DEDUPE — two files in the SAME module dir → that module's AGENTS.md is named exactly ONCE.
# ════════════════════════════════════════════════════════════════════════════════════════════════
DEDUP = {"payload": {"intent": "build", "spec": "two files in one module",
                     "scope": ["runtime/suite.py", "runtime/implement.py"],
                     "consequence_class": "decision_build"}}
dedup = build_instruction(DEDUP)
check("X15 DEDUPE: runtime/AGENTS.md is named (two runtime files → one constitution)", "runtime/AGENTS.md" in dedup)
check("X15 DEDUPE: runtime/AGENTS.md is named exactly ONCE (distinct dirs deduped)",
      dedup.count("runtime/AGENTS.md") == 1)


# ════════════════════════════════════════════════════════════════════════════════════════════════
# DIRECTORY SCOPE — a scope entry that is ITSELF a module dir (e.g. "runtime/") names that module's
# AGENTS.md (you pointed AT the module dir, so its own constitution governs). This is the shape the
# wire's own fixtures use (scope=["runtime/"]); naming nothing there would be a silent gap (rule 4).
# ════════════════════════════════════════════════════════════════════════════════════════════════
DIRSCOPE = {"payload": {"intent": "build", "spec": "point at a whole module dir",
                        "scope": ["runtime/"], "consequence_class": "decision_build"}}
dirscope = build_instruction(DIRSCOPE)
check("X15 DIR-SCOPE: a bare module-dir scope ('runtime/') names runtime/AGENTS.md (not nothing)",
      "runtime/AGENTS.md" in dirscope)
check("X15 DIR-SCOPE: still carries the root three line", ROOT_LINE in dirscope)


# ════════════════════════════════════════════════════════════════════════════════════════════════
# BACKWARD-COMPATIBLE — empty/no scope → JUST the root three, no module line, no crash.
# ════════════════════════════════════════════════════════════════════════════════════════════════
EMPTY_SCOPE = {"payload": {"intent": "build", "spec": "a build with no scope",
                           "consequence_class": "decision_build"}}
empty = build_instruction(EMPTY_SCOPE)
check("BACKWARD-COMPAT: an empty-scope build composes without crashing", isinstance(empty, str))
check("BACKWARD-COMPAT: the empty-scope prompt still carries the root three line", ROOT_LINE in empty)
check("BACKWARD-COMPAT: an empty-scope build names NO module constitution (no scope → no hop)",
      "/AGENTS.md" not in empty)
check("BACKWARD-COMPAT: an empty-scope build still carries spec + STANDARDS_BLOCK",
      "a build with no scope" in empty and STANDARDS_BLOCK in empty)

# a decision with NO payload at all (the oldest shape) → still composes, no module line, no crash
nopl = build_instruction({})
check("BACKWARD-COMPAT: a no-payload decision composes (no crash)", isinstance(nopl, str))
check("BACKWARD-COMPAT: a no-payload decision names NO module constitution", "/AGENTS.md" not in nopl)
check("BACKWARD-COMPAT: a no-payload decision still carries the root three line", ROOT_LINE in nopl)


# ════════════════════════════════════════════════════════════════════════════════════════════════
# FAIL-LOUD-LEGIBLE — a scope file under NO module dir (no ancestor AGENTS.md anywhere) → just the
# root three, no crash, no invented path. The root IS an AGENTS.md, so a top-level file resolves to
# the ROOT constitution which is ALREADY named by the root line — we must not double-name it as a
# "module" constitution, and we must not crash.
# ════════════════════════════════════════════════════════════════════════════════════════════════
TOPLEVEL = {"payload": {"intent": "build", "spec": "edit a top-level file",
                        "scope": ["MAP.md"], "consequence_class": "decision_build"}}
top = build_instruction(TOPLEVEL)
check("FAIL-LOUD: a top-level scope file composes without crashing", isinstance(top, str))
check("FAIL-LOUD: a top-level scope file still carries the root three line", ROOT_LINE in top)


# ════════════════════════════════════════════════════════════════════════════════════════════════
# PRESERVE — the root line, spec, scope_line, STANDARDS_BLOCK, and X4's rich context block are all
# still present and unaltered (X15 ADDS; it does not replace). Build a RICH intent (X4 fields) to
# confirm X15 coexists with X4 byte-for-byte on the parts X15 doesn't touch.
# ════════════════════════════════════════════════════════════════════════════════════════════════
RICH_ADDR = "ui://chat/input"
RICH_SYM = "code://ChatInput"
RICH_CTX = "operator: tone the run button down, it's too loud"
RICH = {"payload": {
    "intent": "build", "spec": "this run button is too loud — tone it down",
    "scope": ["canvas/app/src/App.tsx"], "consequence_class": "decision_build",
    "address": RICH_ADDR, "symbols": [RICH_SYM],
    "context": [{"kind": "chat", "address": RICH_ADDR, "ts": "2026-06-02T00:00:00Z",
                 "text": RICH_CTX, "pinned": True}],
}}
rich = build_instruction(RICH)
check("PRESERVE: the root 'Read AGENTS.md / MAP.md / STATE.md first' line is present", ROOT_LINE in rich)
check("PRESERVE: the spec text is still slotted", "this run button is too loud — tone it down" in rich)
check("PRESERVE: the scope_line ('authorized ONLY these paths') is present",
      "authorized to change ONLY these paths" in rich and "canvas/app/src/App.tsx" in rich)
check("PRESERVE: the STANDARDS_BLOCK is present verbatim", STANDARDS_BLOCK in rich)
check("PRESERVE: X4's INDICATED-ELEMENT (address) section is present", RICH_ADDR in rich and "INDICATED ELEMENT" in rich.upper())
check("PRESERVE: X4's RELATED-CODE (symbol) section is present", RICH_SYM in rich and "RELATED CODE" in rich.upper())
check("PRESERVE: X4's CONTEXT-AT-LOCUS (bundle) section is present", RICH_CTX in rich and "CONTEXT AT THIS LOCUS" in rich.upper())
# and X15 ADDS its hop on top of the rich prompt (canvas → canvas/AGENTS.md)
check("X15 + X4 coexist: the rich prompt ALSO names the governing module constitution canvas/AGENTS.md",
      "canvas/AGENTS.md" in rich)


print(f"\nCONV CONSTITUTION ACCEPTANCE (X15) — {PASS} checks passed. build_instruction stays a PURE "
      f"decision-in/str-out formatter (only a read-only os.path.exists stat; no suite/embed/subprocess) "
      f"and now NAMES the GOVERNING module constitution(s) — derived by walking each scope file's parent "
      f"dirs UP to the nearest ancestor that HAS an AGENTS.md under the repo, deduped — ALONGSIDE the "
      f"preserved root three (the 'Read AGENTS.md / MAP.md / STATE.md first' line is unaltered; a NEW "
      f"adjacent line names the module laws). Empty/no scope → just the root three (backward-compatible, "
      f"no crash); a scope under no module dir → root three (fail-loud-legible). spec/scope_line/"
      f"STANDARDS_BLOCK/X4-context-block are preserved.")
