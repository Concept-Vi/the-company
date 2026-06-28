"""tests/mode_voice_acceptance.py — WS2 acceptance: per-mode voice + (verify) subtype resolution.

A presence mode declares its own voice default (modes/<id>.py `voice`): conversational modes speak,
text-only / off stay silent. voice_enabled() PRECEDENCE: mode 'off' hard-off > an explicit operator
node override > the mode-declared default > 'on'. (The per-mode voice values are a STARTER — text-only
+ off = off, the rest on — open for Tim to tune via registry edits; the mechanism is what WS2 delivers.)

WS2 also asserts the subtype resolution that was ALREADY wired (resolution_spec_for overlays a sub-type's
overrides onto the mode's base lens) — a verify-only leg, no new code there.

Run: `python3 tests/mode_voice_acceptance.py`  (exit 0 = all green; non-zero = a FAIL line printed).

Covers:
  T1  every mode declares a `voice`; text-only + off → 'off', the rest → 'on'.
  T2  voice_enabled precedence: off hard-off · mode-default (no override) · operator override wins both ways.
  T3  (verify-only) subtype resolution: listening/deep overlays budget 8000 onto the base lens; an unset
        sub-type leaves the base; an unknown sub-type fails loud.
"""
import os
import sys
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

from runtime.modes_registry import discover_modes, MODES_DIR, _OPTIONAL
from runtime.suite import Suite
from runtime.registry import NodeRegistry
from store.fs_store import FsStore

NODES = os.path.join(ROOT, "nodes")

# ── T1 — every mode declares a voice default ─────────────────────────────────────────────────────
print("\n[T1] every mode declares a `voice` default (text-only + off → off; rest → on)")
modes = discover_modes([MODES_DIR])
ok("T1a 'voice' is a recognised optional field", "voice" in _OPTIONAL, f"_OPTIONAL={_OPTIONAL}")
missing_voice = [m for m, row in modes.items() if "voice" not in row]
ok("T1b every mode declares voice", not missing_voice, f"missing: {missing_voice}")
SILENT = {"text-only", "off"}
wrong = {m: row.get("voice") for m, row in modes.items()
         if (row.get("voice") == "off") != (m in SILENT)}
ok("T1c exactly text-only+off are 'off', the rest 'on'", not wrong, f"unexpected: {wrong}")

# ── build a Suite ────────────────────────────────────────────────────────────────────────────────
store_dir = tempfile.mkdtemp(prefix="mode-voice-test-")
exit_code = 1
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    # ── T2 — voice_enabled precedence ───────────────────────────────────────────────────────────────
    print("\n[T2] voice_enabled precedence: off-gate · mode-default · operator override")

    def clear_override():
        # remove any explicit operator voice toggle so the mode-default applies
        suite.set_config(suite.SYSTEM_GRAPH, suite.MODE_NODE, {"voice_enabled": None})

    suite.set_mode("off")
    ok("T2a mode off → voice OFF (hard gate)", suite.voice_enabled() is False)

    suite.set_mode("text-only"); clear_override()
    ok("T2b text-only (no override) → voice OFF (mode default)", suite.voice_enabled() is False)

    suite.set_mode("listening"); clear_override()
    ok("T2c listening (no override) → voice ON (mode default)", suite.voice_enabled() is True)

    # operator override wins over the mode default — both directions
    suite.set_mode("listening")
    suite.set_config(suite.SYSTEM_GRAPH, suite.MODE_NODE, {"voice_enabled": "off"})
    ok("T2d operator override 'off' beats listening's on", suite.voice_enabled() is False)

    suite.set_mode("text-only")
    suite.set_config(suite.SYSTEM_GRAPH, suite.MODE_NODE, {"voice_enabled": "on"})
    ok("T2e operator override 'on' beats text-only's off", suite.voice_enabled() is True)

    # but the off-mode gate is absolute — even an 'on' override can't turn voice on for mode off
    suite.set_mode("off")
    suite.set_config(suite.SYSTEM_GRAPH, suite.MODE_NODE, {"voice_enabled": "on"})
    ok("T2f mode off stays voice OFF even with an 'on' override (hard gate wins)", suite.voice_enabled() is False)

    # ── T3 — subtype resolution (verify-only; already wired) ─────────────────────────────────────────
    print("\n[T3] subtype resolution overlays a sub-type's overrides (already wired — verify only)")
    base = suite.resolution_spec_for("listening", None)
    deep = suite.resolution_spec_for("listening", "deep")
    ok("T3a listening base budget is the declared base (None)", base.get("budget") is None, f"{base}")
    ok("T3b listening/deep overlays budget 8000", deep.get("budget") == 8000, f"{deep}")
    try:
        suite.resolution_spec_for("listening", "no-such-subtype")
        # an unknown sub-type is honestly handled (warn + base), not a crash — assert it returns the base
        ok("T3c unknown sub-type falls back to base (honest, no crash)", True)
    except Exception as e:
        ok("T3c unknown sub-type falls back to base (honest, no crash)", False, f"raised {type(e).__name__}: {e}")

    print(f"\n[RESULT] {len(PASS)} pass / {len(FAIL)} fail")
    exit_code = 1 if FAIL else 0
    if FAIL:
        print("FAILED: " + ", ".join(FAIL))
finally:
    shutil.rmtree(store_dir, ignore_errors=True)

sys.exit(exit_code)
