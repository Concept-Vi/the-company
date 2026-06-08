"""tests/autodetect_setter_acceptance.py — GC6 / E2-live: MODE_AUTODETECT is a runtime-settable slot.

E2-backend built MODE_AUTODETECT as an env-resolved class constant (read-only in composition_config).
GC6 makes it SETTABLE end to end through the EXISTING config path (set_rhm_config) — the same pattern
the model/persona/voice slots use. This proves BY USE:

  • set_rhm_config('MODE_AUTODETECT', v) PERSISTS (under the lowercase node-config slot `mode_autodetect`)
    and RE-RESOLVES self.MODE_AUTODETECT (the X17 re-resolve) so autodetect_mode honours it THIS turn.
  • autodetect_mode now honours the live value: 'auto' SWITCHES, 'suggest' PROPOSES (no switch), 'off' NO-OP.
  • an off-options value is REJECTED fail-loud (rule 4/8 — never a silent wrong value).
  • a RELOAD (a fresh Suite on the same store) reads the PERSISTED value (reload-survival).
  • the existing config slots (model/persona/mode/voice) still round-trip — nothing clobbered.
  • capabilities().composition_config.MODE_AUTODETECT reflects the live value (the surface reads it there).
  • set_mode's pure contract + autodetect_mode's off/suggest/auto branches are preserved.
"""
import os, sys, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from fabric import config as fcfg

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


store_dir = tempfile.mkdtemp(prefix="autodetect-test-")
try:
    # ensure the env doesn't shadow the default (a clean default-floor baseline)
    os.environ.pop("COMPANY_MODE_AUTODETECT", None)
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    # --- the default floor (byte-for-byte today) ---
    check("default MODE_AUTODETECT is 'off' (the manual-only default)", suite.MODE_AUTODETECT == "off")
    caps = suite.capabilities()
    check("capabilities().composition_config exposes the live MODE_AUTODETECT",
          caps["composition_config"]["MODE_AUTODETECT"] == "off")
    check("autodetect_mode honours 'off' — NO-OP (no switch)",
          suite.autodetect_mode("focus")["action"] == "noop" and suite.get_mode() == suite.DEFAULT_MODE)

    # --- SET → 'suggest' through the existing config path ---
    suite.set_rhm_config({"MODE_AUTODETECT": "suggest"})
    check("set_rhm_config re-resolves the LIVE self.MODE_AUTODETECT → 'suggest' (X17 re-resolve)",
          suite.MODE_AUTODETECT == "suggest")
    check("persisted under the lowercase node-config slot `mode_autodetect`",
          suite._rhm_cfg().get("mode_autodetect") == "suggest")
    check("capabilities reflects the live value 'suggest'",
          suite.capabilities()["composition_config"]["MODE_AUTODETECT"] == "suggest")
    r = suite.autodetect_mode("focus")
    check("autodetect_mode honours 'suggest' — PROPOSES, does NOT switch",
          r["action"] == "suggested" and r["applied"] is None and suite.get_mode() == suite.DEFAULT_MODE)

    # --- SET → 'auto' → autodetect_mode SWITCHES ---
    suite.set_rhm_config({"MODE_AUTODETECT": "auto"})
    check("set_rhm_config re-resolves the live value → 'auto'", suite.MODE_AUTODETECT == "auto")
    r = suite.autodetect_mode("focus")
    check("autodetect_mode honours 'auto' — SWITCHES via the one set_mode",
          r["action"] == "switched" and r["applied"] == "focus" and suite.get_mode() == "focus")

    # --- back to 'off' → NO-OP again (the toggle round-trips) ---
    suite.set_rhm_config({"MODE_AUTODETECT": "off"})
    check("set back to 'off' re-resolves", suite.MODE_AUTODETECT == "off")
    check("autodetect_mode honours 'off' again — NO-OP (mode stays 'focus', untouched)",
          suite.autodetect_mode("listening")["action"] == "noop" and suite.get_mode() == "focus")

    # --- FAIL LOUD: an off-options value is REJECTED (rule 4/8) ---
    suite.set_rhm_config({"MODE_AUTODETECT": "auto"})   # set a known-good value first
    rejected = False
    try:
        suite.set_rhm_config({"MODE_AUTODETECT": "bananas"})
    except ValueError as e:
        rejected = "bananas" in str(e) and "MODE_AUTODETECT" in str(e)
    check("an off-options MODE_AUTODETECT value is REJECTED fail-loud", rejected)
    check("the rejected write did NOT change the persisted/live value (still 'auto')",
          suite.MODE_AUTODETECT == "auto" and suite._rhm_cfg().get("mode_autodetect") == "auto")

    # --- the OTHER config slots still round-trip (nothing clobbered) ---
    suite.set_rhm_config({"model": "deepseek-v4-flash:cloud", "persona": "a terse naval officer"})
    suite.set_mode("watch-and-react")
    c = suite.rhm_config()
    check("the existing slots still round-trip alongside MODE_AUTODETECT",
          c["model"] == "deepseek-v4-flash:cloud" and c["persona"] == "a terse naval officer"
          and c["mode"] == "watch-and-react")
    check("MODE_AUTODETECT survived the other-slot writes (coexist on the one node)",
          suite._rhm_cfg().get("mode_autodetect") == "auto" and suite.MODE_AUTODETECT == "auto")

    # --- RELOAD: a fresh Suite on the SAME store reads the persisted value (reload-survival) ---
    s2 = Suite(FsStore(os.path.join(store_dir, "store")), reg, nodes_dir=NODES)
    check("a fresh Suite reads the PERSISTED MODE_AUTODETECT ('auto') — reload-survival",
          s2.MODE_AUTODETECT == "auto")
    check("the fresh Suite's autodetect_mode honours the persisted 'auto' (switches)",
          s2.autodetect_mode("background")["action"] == "switched" and s2.get_mode() == "background")
    check("the fresh Suite's capabilities reflects the persisted value",
          s2.capabilities()["composition_config"]["MODE_AUTODETECT"] == "auto")
    check("the other slots also survived the reload (no regression)",
          s2.rhm_config()["model"] == "deepseek-v4-flash:cloud")

    # --- autodetect_mode still FAILS LOUD on a fabricated candidate (preserved contract) ---
    fabricated_rejected = False
    try:
        s2.autodetect_mode("not-a-mode")
    except ValueError:
        fabricated_rejected = True
    check("autodetect_mode still rejects a fabricated candidate mode (preserved)", fabricated_rejected)

    print(f"\nALL {PASS} CHECKS PASS — MODE_AUTODETECT is runtime-settable, persistent, re-resolved (GC6/E2-live)")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
