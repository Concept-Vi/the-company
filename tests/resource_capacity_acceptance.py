"""tests/resource_capacity_acceptance.py — WS-R acceptance: the SYSTEM-RAM capacity invariant.

The resource manager (ops/cli/gpu.py) was VRAM-ONLY. A CPU-resident model (stt-granite fp32 ~9 GB,
the ONNX ears, whisper.cpp) costs system RAM and ZERO VRAM, so it was invisible to the budget — yet
host-RAM overcommit is exactly what triggers the kernel OOM-killer (the 2026-06-28 cascade: Granite +
an embedder + ~44 Chrome procs). WS-R adds a RAM leg that, at ACTUATION time, reads LIVE /proc/meminfo
MemAvailable (counting ALL processes on the box, not just registered services) and refuses loud — so
overcommit is impossible BY CODE, not merely impossible among Company services. A separate CONFIG-time
check refuses a loadout whose estimates can't ever fit the hardware.

VERIFY-BY-USE, no service is started: the refuse path in app._act exits BEFORE any systemd call, so we
drive it directly with a synthetic over-budget service. The PASS legs are asserted on the pure functions
against the LIVE machine readings.

Run: `python3 tests/resource_capacity_acceptance.py`  (exit 0 = all green; non-zero = a FAIL line printed).

Covers:
  T1  ram_of resolves top-level ram_mb, then load.ram_mb, then 0 (the vram_of twin).
  T2  read_system_ram() returns total/available/used from the live /proc/meminfo (this box is Linux).
  T3  ram_fit: a 0-need set is ok; an impossible set (ram_mb > MemAvailable) is NOT ok; present=True.
  T4  check_fit_unified composes both legs (ok == vram.ok AND ram.ok) and keeps the {vram,ram,ok} shape.
  T5  check_fit is UNTOUCHED — still returns its 4-tuple (the byte-identical-callers regression guard).
  T6  validate_combo_capacity: a real combo fits; an over-RAM set fails ram_ok; an over-VRAM set fails vram_ok.
  T7  THE INVARIANT — app._act REFUSES an over-RAM start with exit 2 EVEN with --force (force is VRAM-only;
        RAM overflow is kernel-fatal). Also refuses without force. This is the "can't overcook resources" bar.
  T8  COMPLETENESS — every real service in services.json carries a ram_mb (so a new CPU service can't be
        silently RAM-invisible); only timer-jobs + the hosted gateway are exempt.
"""
import os
import sys
import io
import contextlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops", "cli"))

import registry
import gpu
import app

PASS, FAIL = [], []


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  — {detail}" if detail and not cond else ""))


reg = registry.load()

# ── T1 — ram_of resolution (the vram_of twin) ────────────────────────────────────────────────────
print("\n[T1] ram_of resolves top-level → load.ram_mb → 0")
ok("T1a top-level ram_mb", registry.ram_of({"ram_mb": 1234}) == 1234)
ok("T1b load.ram_mb fallback", registry.ram_of({"load": {"ram_mb": 555}}) == 555)
ok("T1c default 0 (no estimate)", registry.ram_of({"group": "core"}) == 0)
ok("T1d top-level wins over load", registry.ram_of({"ram_mb": 10, "load": {"ram_mb": 20}}) == 10)

# ── T2 — live system-RAM probe ───────────────────────────────────────────────────────────────────
print("\n[T2] read_system_ram() reads live /proc/meminfo")
sysram = gpu.read_system_ram()
ok("T2a returns a dict on Linux", isinstance(sysram, dict), f"got {type(sysram).__name__}")
if isinstance(sysram, dict):
    ok("T2b has total/available/used", all(k in sysram for k in ("total", "available", "used")), f"{sysram}")
    ok("T2c total > available (used > 0)", sysram["total"] > sysram["available"] > 0, f"{sysram}")
    ok("T2d used == total - available", sysram["used"] == sysram["total"] - sysram["available"], f"{sysram}")

# ── T3 — ram_fit (the actuation leg, live MemAvailable) ──────────────────────────────────────────
print("\n[T3] ram_fit: fits when need=0, refuses when need > live available")
# Synthetic reg: one cheap (0) service + one impossibly-heavy service, both 'manual' on dead ports so
# _is_running() reads them as NOT running (so their need counts).
big = (sysram["available"] if isinstance(sysram, dict) else 40000) + 50000   # guaranteed > available
synth = {"services": {
    "zero-svc": {"group": "models", "ram_mb": 0, "manage": {"type": "manual"}, "port": 59990},
    "huge-svc": {"group": "models", "ram_mb": big, "manage": {"type": "manual"}, "port": 59991},
}}
fit0 = gpu.ram_fit(synth, ["zero-svc"])
fitbig = gpu.ram_fit(synth, ["huge-svc"])
ok("T3a zero-cost set fits", fit0["ok"] is True and fit0["need"] == 0, f"{fit0}")
ok("T3b present True (/proc/meminfo readable)", fit0["present"] is True, f"{fit0}")
ok("T3c impossible set REFUSED", fitbig["ok"] is False and fitbig["need"] == big, f"{fitbig}")
ok("T3d free == MemAvailable − headroom",
   isinstance(sysram, dict) and fit0["free"] == sysram["available"] - reg.get("ram_headroom_mb", 2048),
   f"free={fit0['free']}")

# ── T4 — check_fit_unified composes both legs ────────────────────────────────────────────────────
print("\n[T4] check_fit_unified = VRAM leg (check_fit) + RAM leg (ram_fit)")
uni = gpu.check_fit_unified(synth, ["huge-svc"])
ok("T4a has vram + ram + ok keys", all(k in uni for k in ("vram", "ram", "ok")), f"{list(uni)}")
ok("T4b top ok == vram.ok and ram.ok", uni["ok"] == (uni["vram"]["ok"] and uni["ram"]["ok"]), f"{uni}")
ok("T4c over-RAM → top ok False", uni["ok"] is False and uni["ram"]["ok"] is False, f"{uni}")

# ── T5 — check_fit UNTOUCHED (regression: callers unpack a 4-tuple) ──────────────────────────────
print("\n[T5] check_fit still returns its 4-tuple (byte-identical callers)")
res = gpu.check_fit(reg, [])
ok("T5a returns a 4-tuple", isinstance(res, tuple) and len(res) == 4, f"got {res!r}")
a, b, c, d = res  # must unpack exactly like app.py:92 / lifecycle:158 / capabilities:451
ok("T5b unpacks (ok, need, free, present)", isinstance(a, bool) and isinstance(b, int), f"{res!r}")

# ── T6 — validate_combo_capacity (config-time hardware fit) ───────────────────────────────────────
print("\n[T6] validate_combo_capacity: real combo fits; over-RAM/over-VRAM sets fail loud")
inter = registry.combos(reg)["interaction"]["services"]
cap_inter = gpu.validate_combo_capacity(reg, inter)
ok("T6a real 'interaction' loadout fits the hardware", cap_inter["ok"] is True, f"{cap_inter}")
# over-RAM synthetic set
memtotal = sysram["total"] if isinstance(sysram, dict) else 40000
synth2 = {"vram_ceiling_mb": reg.get("vram_ceiling_mb", 16376), "ram_headroom_mb": reg.get("ram_headroom_mb", 2048),
          "services": {
              "ramhog": {"group": "models", "ram_mb": memtotal + 100000, "manage": {"type": "manual"}, "port": 59992},
              "vramhog": {"group": "models", "vram_mb": 999999, "manage": {"type": "manual"}, "port": 59993},
          }}
cap_ram = gpu.validate_combo_capacity(synth2, ["ramhog"])
cap_vram = gpu.validate_combo_capacity(synth2, ["vramhog"])
ok("T6b over-RAM set fails ram_ok", cap_ram["ram_ok"] is False and cap_ram["ok"] is False, f"{cap_ram}")
ok("T6c over-VRAM set fails vram_ok", cap_vram["vram_ok"] is False and cap_vram["ok"] is False, f"{cap_vram}")

# ── T7 — THE INVARIANT: --force does NOT override the RAM refuse ──────────────────────────────────
print("\n[T7] app._act REFUSES an over-RAM start with exit 2 — even with --force (force is VRAM-only)")


def _act_exit(force):
    """Run app._act on the impossible synthetic service; return the SystemExit code (or None)."""
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            app._act(synth, "up", ["huge-svc"], force=force, evict=False, wait=False)
    except SystemExit as e:
        return e.code
    return None


code_force = _act_exit(force=True)
code_plain = _act_exit(force=False)
ok("T7a over-RAM start with --force STILL exits 2 (kernel-fatal, not forceable)", code_force == 2, f"exit={code_force}")
ok("T7b over-RAM start without force exits 2", code_plain == 2, f"exit={code_plain}")

# ── T8 — COMPLETENESS: every real service carries a ram_mb ────────────────────────────────────────
print("\n[T8] every real service has a ram_mb (no silent RAM-invisible service)")
EXEMPT = {"remote-gateway"}  # hosted (no local process); timer-jobs handled by group below
no_ram = [k for k, v in reg["services"].items()
          if "ram_mb" not in v and k not in EXEMPT and v.get("group") != "jobs"]
ok("T8a no real service missing ram_mb", not no_ram, f"missing: {no_ram}")
ok("T8b ram_headroom_mb is set in the registry", "ram_headroom_mb" in reg, "registry-is-truth, not hardcoded")

# ── T9 — the ACTUATOR rides the RAM gate: ensure_resident refuses an over-RAM load ───────────────
print("\n[T9] ensure_resident (the mode-loadout actuator) refuses an over-RAM, 0-VRAM service")
import capabilities
# A 0-VRAM, huge-RAM, not-running service (the granite shape): VRAM-fit passes (need 0) but RAM must catch it.
synth3 = {"vram_ceiling_mb": reg.get("vram_ceiling_mb", 16376), "ram_headroom_mb": reg.get("ram_headroom_mb", 2048),
          "services": {"ramhog-ear": {"group": "voice", "vram_mb": 0, "ram_mb": big,
                                      "manage": {"type": "manual", "run": "voice/ears/fake.py"},
                                      "port": 59994}}}
raised = False
try:
    capabilities.ensure_resident("ramhog-ear", evict=False, reg=synth3, wait=False)
except capabilities.EnsureResidentError as e:
    raised = "SYSTEM RAM" in str(e)
ok("T9a ensure_resident RAISES on an over-RAM 0-VRAM load (the granite shape)", raised,
   "VRAM-fit would pass need=0; the RAM leg must catch it")

# ── result ───────────────────────────────────────────────────────────────────────────────────────
print(f"\n[RESULT] {len(PASS)} pass / {len(FAIL)} fail")
if FAIL:
    print("FAILED: " + ", ".join(FAIL))
    sys.exit(1)
sys.exit(0)
