"""tests/activation_caller_acceptance.py — Concurrent Cognition Group H/I · THE ALWAYS-ON CALLER.

Proves the NET-NEW CALLER mechanism (runtime/activation_driver.py) that fires the DUE Group H/I drivers
on ONE tick + runs the mode detector — built DORMANT + opt-in (the wire_armed() / policy=None posture):

  • DORMANT BY DEFAULT — activation_loop_enabled() is False with the env unset; maybe_start_activation_loop
    spawns NOTHING; importing bridge.py / constructing the caller stands up NO thread, NO autonomous tick.
  • THE MANUAL TICK IS LIVE — activation_tick(suite) fires the due clock drivers (background idle-gate +
    held-cursor rollup + mode-detector→toggle) and routes their outputs over the non-consequential
    DESTINATION_KINDS (the floor holds by construction).
  • THE HELD CURSOR (H3) — the caller holds ONE RollupDriver, so tick→inject-wave→tick consolidates ONCE,
    and a third tick is a no-op (a fresh driver per tick would re-consolidate every wave — the H3 bug).
  • CLOCK vs EVENT — a clock tick fires background+rollup+mode-detect; SENSE fires ONLY when a real
    sense_event is SUPPLIED (a periodic tick fabricates none — sense_tick's own fail-loud contract).
  • ENABLING THE FLAG → the loop ticks — with the env armed, _loop_iteration drives one real tick; the
    guarded spawn returns a live thread; disarming stops it.

VERIFY BY USE: drives activation_tick / _loop_iteration DIRECTLY against a hermetic suite (the H/I
drivers stubbed/observed via a recorder over fire_activation/consolidate_rollup — the DECISION is proven
deterministically, no GPU, no ThreadingHTTPServer, no real sleep), mirroring how the wire suites call
the dispatch driver directly rather than spawning the daemon.
"""
import os, sys, tempfile, time, threading
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from runtime import activation as act
from runtime import activation_driver as drv

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def fresh_suite():
    store = FsStore(os.path.join(tempfile.mkdtemp(prefix="actcaller-"), "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    return Suite(store, reg, nodes_dir=NODES)


class _Recorder:
    """Recording stub over fire_activation/consolidate_rollup — proves the CALLER's ORCHESTRATION
    deterministically WITHOUT firing the live 4B cast (the entry points are reused + proven live by
    activation_contexts_acceptance). Mirrors the recorder in activation_drivers_acceptance."""
    def __init__(self):
        self.fired = []          # [(context, mode, sense_event)]
        self.rollups = []        # [(since, mode, gc)]

    def fire_activation(self, context, *, mode=None, sense_event=None, turn_id=None, **kw):
        self.fired.append((context, mode, sense_event))
        return act.ActivationResult(context=context, mode=mode or "listening", turn_id="stub",
                                    trigger="stub", reply=False, fired_roles=["focus"],
                                    routed=[{"destination": "address", "address": "run://stub/x",
                                             "acted": True}])

    def consolidate_rollup(self, *, since=-1, mode=None, turn_id=None, gc=False):
        self.rollups.append((since, mode, gc))
        return act.ActivationResult(context="rollup", mode=mode or "listening", turn_id="stub",
                                    trigger="timer", reply=False, address="run://rollup/stub",
                                    rollup={"n_waves": 1, "n_role_runs": 2})


def _install_recorder(suite):
    rec = _Recorder()
    suite.fire_activation = rec.fire_activation
    suite.consolidate_rollup = rec.consolidate_rollup
    return rec


now = time.time()


def _stale_chat(suite, age_s):
    """Seed one stale operator-activity event `age_s` ago as the LAST event (a controlled idle signal)."""
    suite.store.append_event({"kind": "chat", "summary": "old",
                              "ts": datetime.fromtimestamp(now - age_s, timezone.utc).isoformat()})


# ===================================================================================================
# DORMANCY GATE (the wire_armed() analog) — OFF by default; importing/constructing spawns nothing.
# ===================================================================================================
os.environ.pop("COMPANY_ACTIVATION_LOOP", None)
check("DORMANT · activation_loop_enabled() is False with the env unset (off by default)",
      drv.activation_loop_enabled() is False)
for tok in ("0", "false", "no", "off", "", "  "):
    os.environ["COMPANY_ACTIVATION_LOOP"] = tok
    check(f"DORMANT · the env value {tok!r} does NOT arm the loop", drv.activation_loop_enabled() is False)
for tok in ("1", "true", "yes", "on", "enabled", "TRUE", "On"):
    os.environ["COMPANY_ACTIVATION_LOOP"] = tok
    check(f"ARM · the env value {tok!r} arms the loop (call-time read)", drv.activation_loop_enabled() is True)
os.environ.pop("COMPANY_ACTIVATION_LOOP", None)

# maybe_start_activation_loop spawns NOTHING when dormant (the default) — no thread.
s = fresh_suite()
caller = drv.ActivationCaller(suite=s)
threads_before = threading.active_count()
th = drv.maybe_start_activation_loop(caller)
check("DORMANT · maybe_start_activation_loop returns None when the env is unset (no daemon spawned)",
      th is None and threading.active_count() == threads_before)

# bridge.py must NOT auto-start the loop on import (the caller is constructed dormant).
import importlib
bridge = importlib.import_module("runtime.bridge")
check("DORMANT · importing bridge.py constructed the caller but the loop thread is None (no auto-start)",
      bridge._ACTIVATION_LOOP_THREAD is None and isinstance(bridge.ACTIVATION_CALLER, drv.ActivationCaller))


# ===================================================================================================
# THE MANUAL TICK IS LIVE — fires the DUE clock drivers; floor-clean by construction.
# ===================================================================================================
# a tick with the operator IDLE past the threshold → background fires (delegating to the reused entry point).
s = fresh_suite(); s.set_mode("listening")                 # listening allocates background + rollup live
rec = _install_recorder(s)
_stale_chat(s, 200)
caller = drv.ActivationCaller(suite=s, idle_seconds=90.0)
res = caller.activation_tick()
check("MANUAL · activation_tick fired background (idle gate open) via the reused entry point",
      res.background["fired"] is True and ("background", "listening", None) in rec.fired)
check("MANUAL · the tick records it ACTED + the background result LANDS at a non-consequential dest",
      res.acted is True and res.background["result"].routed[0]["destination"] in ("surface", "address", "lane"))
check("MANUAL · activation_tick returns a legible per-driver reason list (rule 4 — no silent no-op)",
      any("background:" in r for r in res.reasons) and any("rollup:" in r for r in res.reasons)
      and any("mode:" in r for r in res.reasons))
check("MANUAL · a clock tick passes NO sense_event → sense did NOT fire (never fabricated)",
      res.sense is None and not any(f[0] == "sense" for f in rec.fired))

# a tick with the operator ACTIVE → background does NOT fire (we go THROUGH the gate, never bypass it).
s2 = fresh_suite(); s2.set_mode("listening"); rec2 = _install_recorder(s2)
_stale_chat(s2, 5)
caller2 = drv.ActivationCaller(suite=s2, idle_seconds=90.0)
res2 = caller2.activation_tick()
check("MANUAL · activation_tick does NOT fire background while the operator is active (idle gate closed)",
      res2.background["fired"] is False and not any(f[0] == "background" for f in rec2.fired))


# ===================================================================================================
# THE HELD CURSOR (H3) — one RollupDriver across ticks; no re-consolidation.
# ===================================================================================================
s = fresh_suite(); s.set_mode("listening")
rec = _install_recorder(s)
_stale_chat(s, 5)                                          # operator active → background never fires (isolate rollup)
caller = drv.ActivationCaller(suite=s, idle_seconds=90.0)
# tick 1 — no cognition.wave records yet → rollup is a legible no-op.
r1 = caller.activation_tick()
check("HELD · tick 1 with no waves → rollup no-op (no consolidation)",
      r1.rollup["consolidated"] is False and len(rec.rollups) == 0)
since_after_t1 = caller._rollup.since
# inject a wave AFTER the cursor → tick 2 consolidates exactly that wave from the HELD cursor.
s.store.append_event({"kind": "cognition.wave",
                      "summary": {"turn_id": "t1", "n_roles": 1,
                                  "roles": [{"role": "focus", "address": "run://t1/focus", "ok": True, "ms": 42}]}})
r2 = caller.activation_tick()
check("HELD · tick 2 consolidated the NEW wave from the HELD cursor (not from -1)",
      r2.rollup["consolidated"] is True and rec.rollups[-1][0] == since_after_t1)
check("HELD · the held cursor ADVANCED past the consolidated wave", caller._rollup.since > since_after_t1)
# tick 3 — no further waves → no-op (the prior wave is NOT re-consolidated; the cursor is held across ticks).
r3 = caller.activation_tick()
check("HELD · tick 3 does NOT re-consolidate the already-consolidated wave (the H3 bug is prevented)",
      r3.rollup["consolidated"] is False and len(rec.rollups) == 1)


# ===================================================================================================
# CLOCK vs EVENT — sense fires ONLY on a real supplied event; the detector→toggle runs every tick.
# ===================================================================================================
s = fresh_suite(); s.set_mode("watch-and-react")           # allocates sense live
rec = _install_recorder(s)
_stale_chat(s, 5)                                          # operator active → background gate closed (isolate sense)
caller = drv.ActivationCaller(suite=s, idle_seconds=90.0)
# a clock tick with NO sense_event → sense does not run.
res = caller.activation_tick()
check("CLOCK · with no supplied event sense is not run (event-only — never fabricated on a clock)",
      res.sense is None and not any(f[0] == "sense" for f in rec.fired))
# a tick WITH a real sense_event → sense_tick shapes it + fires the reused entry point.
res = caller.activation_tick(sense_event={"kind": "window-focus", "detail": "VS Code opened"})
check("EVENT · a supplied sense_event makes the tick fire sense (the shaped event reaches the entry point)",
      res.sense["fired"] is True and any(f[0] == "sense" for f in rec.fired)
      and "window-focus" in res.sense["sense_event"]["summary"])
check("EVENT · firing sense marks the tick acted + carries a legible sense reason",
      res.acted is True and any("sense:" in r for r in res.reasons))
# a non-dict supplied event still fails loud (sense_tick's contract — the caller does NOT swallow it).
raised = False
try:
    caller.activation_tick(sense_event="not a dict")
except ValueError as e:
    raised = "raw_event must be a dict" in str(e)
check("EVENT · a non-dict supplied sense_event FAILS LOUD through the caller (never swallowed)", raised)


# ===================================================================================================
# THE MODE DETECTOR runs every tick + feeds the toggle (off/suggest/auto) — never set_mode directly.
# ===================================================================================================
# under 'auto', a long-idle tick detects 'background' and SWITCHES via the toggle (the detector's path).
s = fresh_suite(); s.set_mode("listening"); s.set_rhm_config({"MODE_AUTODETECT": "auto"})
rec = _install_recorder(s)
_stale_chat(s, 10000)
caller = drv.ActivationCaller(suite=s, idle_seconds=90.0)
res = caller.activation_tick()
check("MODE · a long-idle tick under 'auto' SWITCHES the mode via the toggle (detector→propose_mode)",
      res.mode["toggle_result"] is not None and res.mode["toggle_result"]["action"] == "switched"
      and s.get_mode() == res.mode["toggle_result"]["candidate"] and res.acted is True)
# under 'suggest' it SURFACES, never switches.
s = fresh_suite(); s.set_mode("listening"); s.set_rhm_config({"MODE_AUTODETECT": "suggest"})
_install_recorder(s); _stale_chat(s, 10000)
caller = drv.ActivationCaller(suite=s, idle_seconds=90.0)
res = caller.activation_tick()
check("MODE · under 'suggest' the tick SURFACES the candidate and does NOT switch",
      res.mode["toggle_result"]["action"] == "suggested" and s.get_mode() == "listening")
# under 'off' it NO-OPs.
s = fresh_suite(); s.set_mode("listening"); s.set_rhm_config({"MODE_AUTODETECT": "off"})
_install_recorder(s); _stale_chat(s, 10000)
caller = drv.ActivationCaller(suite=s, idle_seconds=90.0)
res = caller.activation_tick()
check("MODE · under 'off' the tick NO-OPs the mode (toggle posture honoured; no silent switch)",
      res.mode["toggle_result"]["action"] == "noop" and s.get_mode() == "listening")


# ===================================================================================================
# ENABLING THE FLAG → the loop ticks; the guarded spawn returns a live thread; disarming stops it.
# ===================================================================================================
# _loop_iteration drives ONE real tick directly (no thread, no sleep) — the testable unit.
s = fresh_suite(); s.set_mode("listening"); rec = _install_recorder(s)
_stale_chat(s, 200)
caller = drv.ActivationCaller(suite=s, idle_seconds=90.0)
seen = []
it = drv._loop_iteration(caller, on_tick=lambda r: seen.append(r))
check("LOOP · _loop_iteration drives ONE real tick (the testable unit — no thread, no sleep)",
      isinstance(it, drv.TickResult) and len(seen) == 1 and it.background["fired"] is True)
check("LOOP · the loop iteration passes NO sense_event (sense stays event-only on the autonomous clock)",
      it.sense is None)

# with the env ARMED, maybe_start_activation_loop spawns a live daemon thread that ticks; then disarm to stop.
os.environ["COMPANY_ACTIVATION_LOOP"] = "1"
s = fresh_suite(); s.set_mode("listening"); _install_recorder(s)
_stale_chat(s, 5)                                          # active → background won't fire; ticks still run (rollup/mode)
caller = drv.ActivationCaller(suite=s)
ticks = []
th = drv.maybe_start_activation_loop(caller, on_tick=lambda r: ticks.append(r))
check("ARM · maybe_start_activation_loop returns a live daemon thread when armed",
      th is not None and th.is_alive() and th.daemon is True)
# the loop must actually tick — wait briefly for at least one iteration (cadence floored, but we set it fast).
os.environ["COMPANY_ACTIVATION_TICK_S"] = "1"
deadline = time.time() + 8.0
while not ticks and time.time() < deadline:
    time.sleep(0.05)
check("ARM · the armed loop ACTUALLY TICKS (at least one iteration ran)", len(ticks) >= 1)
# disarm → the loop stops on its next iteration boundary (call-time re-check inside run_activation_loop).
os.environ.pop("COMPANY_ACTIVATION_LOOP", None)
os.environ.pop("COMPANY_ACTIVATION_TICK_S", None)
th.join(timeout=5.0)
check("DISARM · clearing the env STOPS the loop (the daemon exits — call-time re-check)", not th.is_alive())


# ===================================================================================================
# THE FLOOR — the caller orchestrates ONLY the non-consequential H/I drivers (no forbidden verb).
# ===================================================================================================
import inspect, ast
src = inspect.getsource(drv)
# AST scan for CALLS (robust to docstrings/comments that legitimately DESCRIBE the floor — mirrors
# cognition_governance_acceptance's AST-for-calls approach). The forbidden CALLS are the build-dispatch
# trigger (dispatch_decision) + the operator-only resolve (resolve_surfaced/.resolve/.approve). The caller
# must ALSO not call the RAW entry points directly (fire_activation/consolidate_rollup) — it goes through
# the H/I drivers (background_tick/sense_tick/RollupDriver.tick/propose_mode), which keep the gate+budget.
tree = ast.parse(src)
called_names = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        fn = node.func
        nm = fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else None)
        if nm:
            called_names.add(nm)
forbidden_calls = {"dispatch_decision", "resolve_surfaced", "approve", "resolve"} & called_names
check("FLOOR · activation_driver.py CALLS no resolve/approve/dispatch verb (AST — the build-dispatch floor)",
      not forbidden_calls)
check("FLOOR · the caller does NOT call the RAW entry points (fire_activation/consolidate_rollup) directly "
      "— it orchestrates the H/I drivers, which keep the idle-gate + budget + reserve",
      "fire_activation" not in called_names and "consolidate_rollup" not in called_names)
check("FLOOR · the caller fires only through the reused H/I drivers (background_tick/sense_tick/"
      "RollupDriver.tick/propose_mode)",
      {"background_tick", "sense_tick", "propose_mode"} <= called_names and "tick" in called_names)


print(f"\nactivation_caller_acceptance: {PASS} checks passed")
