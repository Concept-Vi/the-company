"""runtime/activation_driver.py — Concurrent Cognition Group H/I · THE ALWAYS-ON CALLER (DORMANT).

WHAT THIS CLOSES. Group G5 built the activation-context substrate + the entry points
(`fire_activation`/`consolidate_rollup`); Group H built the DECISION layer (`background_tick`,
`sense_tick`, `RollupDriver`, the `activity_signal` reader); Group I built the mode AUTO-DETECTOR
(`detect_mode_candidate`/`propose_mode`). All of it is TICKABLE — but NOTHING calls it on a clock or
an event, so the always-on cognition the modes ALLOCATE never actually fires live. This module is the
missing CALLER: ONE tick that fires the DUE clock-driven drivers + runs the mode detector, in one place,
reusing the H/I drivers byte-for-byte (it NEVER reimplements them, NEVER calls the raw entry points).

THE CRITICAL DISCIPLINE — DORMANT + OPT-IN (the same posture as the wire's `wire_armed()` and the
scheduler's `policy=None` byte-identical default):

  • The MANUAL/EXTERNAL drive seam (`activation_tick` + `POST /api/activation/tick`) is LIVE — it is the
    explicit-drive door (an external caller, a test, the operator, an ops cadence). Firing it fires roles
    = COMPUTATION (the G9/C9.2 floor: the drivers route only over the five non-consequential
    DESTINATION_KINDS; NO resolve/approve/dispatch, NO `claude -p`). A manual tick is safe by construction.
  • The AUTONOMOUS BACKGROUND LOOP (the cadence that ticks on its own forever) is OFF BY DEFAULT, behind a
    CALL-TIME env gate `activation_loop_enabled()` (`COMPANY_ACTIVATION_LOOP`, default disabled). Importing
    this module + constructing the bridge SUITE spawns NOTHING. Enabling the live always-on cadence is a
    BEHAVIOR CHANGE the operator greenlights → NEEDS-TIM, never auto-started by this build (exactly like
    arming the wire is `COMPANY_WIRE_PERMISSION=acceptEdits` / NOT the default).

WHAT FIRES ON A CLOCK TICK vs WHAT IS EVENT-ONLY:
  A periodic tick has NO real sense event — and `sense_tick` FAILS LOUD on a fabricated one (its own
  contract: "never fire on a fabricated event"). So a clock `activation_tick`:
    • ALWAYS runs `background_tick` (its idle gate decides whether to fire — we never bypass the gate),
    • ALWAYS runs `RollupDriver.tick()` (the HELD cursor consolidates only new waves),
    • ALWAYS runs `propose_mode` (the detector → the off/suggest/auto toggle),
    • runs `sense_tick` ONLY when a REAL `sense_event` is SUPPLIED to the tick (the endpoint may pass one
      in its POST body; the autonomous loop passes none, so sense stays event-only — never fabricated).

THE STATE THE CALLER HOLDS (why this is an OBJECT, not a free function): the rollup driver's `since`
cursor MUST persist across ticks, or every tick re-consolidates every wave (the exact bug H3 exists to
prevent). So `ActivationCaller` holds ONE long-lived `RollupDriver`; bridge.py constructs ONE module-level
instance that BOTH the endpoint and the loop drive — the cursor is held across manual AND loop ticks alike.

REUSE-DON'T-PARALLEL (binding): no second scheduler, no second loop, no second budget. The caller
ORCHESTRATES the existing H/I drivers; each driver still enforces the mode budget + the sacred per-turn
reserve (inside the reused entry points it delegates to) + routes over the non-consequential destinations.
The dormant/live split mirrors the wire's PROVEN shape — the wire's dispatch driver is called DIRECTLY by
the suites (the testable iteration) while its background variant is the daemon thread; here
`activation_tick` / `_loop_iteration` are the directly-testable units and `run_activation_loop` is the daemon.

FAIL-LOUD: a driver's LEGIBLE non-fire (idle gate closed, mode doesn't allocate, no new waves, no
candidate) is aggregated as a reason in the tick result (rule 4 — never a silent no-op). A driver that
RAISES a real error is NOT swallowed — `activation_tick` re-raises it loud (a real fault must surface;
only the legible "didn't fire because X" outcomes are collected). The autonomous loop's per-iteration
try/except exists ONLY so one bad iteration can't kill the daemon, and it EMITS a loud warning event +
keeps the reason — it never pretends success.

DRIFT HOME: this caller is reflected in runtime/AGENTS.md (the Group H/I section — the always-on caller
seam); tests/activation_caller_acceptance.py proves the dormant-by-default + the held-cursor + the
clock-vs-event split by USE.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from runtime import activation as _act


# =====================================================================================================
# THE DORMANCY GATE (the wire_armed() analog) — call-time read, default OFF.
#
# COMPANY_ACTIVATION_LOOP gates ONLY the autonomous background CADENCE (the daemon that ticks forever).
# The manual `activation_tick` / the POST endpoint are ALWAYS available (the external-drive seam) — a
# manual tick fires roles = computation, floor-clean, safe by construction. What this env arms is the
# self-running clock. Read at CALL time (not import) so the operator can flip it without a process
# restart, and a test can set/clear it, and the SAFE default (no autonomous loop) holds for every process
# that does not deliberately opt in. The accepted "on" tokens mirror common bool-env conventions.
# =====================================================================================================
_TRUE_TOKENS = frozenset({"1", "true", "yes", "on", "enabled"})

# The default cadence (seconds) the autonomous loop waits between ticks WHEN ARMED. A DECLARED knob (not a
# magic literal buried in the loop), env-overridable. Generous by design — the between-turns cognition is
# not a hot path, and the idle gate / held cursor make a slow cadence correct (no missed work, no flood).
DEFAULT_TICK_SECONDS = 60.0


def activation_loop_enabled() -> bool:
    """Is the AUTONOMOUS background activation loop deliberately armed? (the wire_armed() analog.)

    True ONLY when the operator has opted in via COMPANY_ACTIVATION_LOOP ∈ {1,true,yes,on,enabled}.
    DEFAULT FALSE — so importing this module + constructing the bridge SUITE spawns NO loop, NO thread,
    NO autonomous tick. This is the gate that keeps the always-on cognition INERT BY DEFAULT (🔒 built-
    not-armed, exactly like the wire's resolve→dispatch trigger). Enabling the live cadence is a behavior
    change the operator greenlights → NEEDS-TIM; this build NEVER auto-starts it.

    Call-time read (not an import-time snapshot) so a deliberately-set env flips the posture WITHOUT a
    process restart and a by-use test can toggle it."""
    return os.environ.get("COMPANY_ACTIVATION_LOOP", "").strip().lower() in _TRUE_TOKENS


def loop_tick_seconds() -> float:
    """The live cadence (seconds between autonomous ticks), call-time read of COMPANY_ACTIVATION_TICK_S
    (default DEFAULT_TICK_SECONDS). Floored at 1.0s so a misconfig can never busy-spin the daemon."""
    try:
        return max(1.0, float(os.environ.get("COMPANY_ACTIVATION_TICK_S", DEFAULT_TICK_SECONDS)))
    except (TypeError, ValueError):
        return DEFAULT_TICK_SECONDS


@dataclass
class TickResult:
    """The captured artifact of ONE activation tick — every driver's legible outcome in one place (the
    proof, read by use). `acted` is True iff SOMETHING fired/consolidated this tick (a non-fire tick is a
    legible no-op, never an error). Each sub-result is the driver's own return dict / ActivationResult so
    the caller adds NO new shape — it ORCHESTRATES, it doesn't reinterpret."""
    background: dict | None = None          # background_tick(...) → {fired, reason, signal, result?}
    rollup: dict | None = None              # RollupDriver.tick(...) → {consolidated, reason, ...}
    mode: dict | None = None                # propose_mode(...) → {detected, toggle_result?, reason?}
    sense: dict | None = None               # sense_tick(...) → {fired, reason, sense_event, result?} (event-only)
    reasons: list = field(default_factory=list)   # the aggregated legible non-fire/outcome reasons (rule 4)
    acted: bool = False                     # did any driver actually fire/consolidate/switch this tick?
    wall_s: float = 0.0

    def as_dict(self) -> dict:
        """A JSON-SAFE projection of the tick (the endpoint serializes this). The driver sub-results nest
        an `ActivationResult` dataclass (e.g. background['result']) — coerce ANY dataclass to a dict
        recursively so the bridge can `json.dumps` it without a 'not JSON serializable' fault (the live
        endpoint's reality; the in-process test never serialized). Reuse-don't-reshape: we COERCE the
        existing driver dicts, we do NOT invent a new shape."""
        import dataclasses
        def _coerce(v):
            if dataclasses.is_dataclass(v) and not isinstance(v, type):
                return {k: _coerce(val) for k, val in dataclasses.asdict(v).items()}
            if isinstance(v, dict):
                return {k: _coerce(val) for k, val in v.items()}
            if isinstance(v, (list, tuple)):
                return [_coerce(x) for x in v]
            return v
        return {"background": _coerce(self.background), "rollup": _coerce(self.rollup),
                "mode": _coerce(self.mode), "sense": _coerce(self.sense),
                "reasons": list(self.reasons), "acted": self.acted, "wall_s": self.wall_s}


@dataclass
class ActivationCaller:
    """THE STATEFUL CALLER — the one place the H/I drivers are orchestrated on a tick.

    Holds the ONE long-lived `RollupDriver` whose `since` cursor MUST persist across ticks (a fresh driver
    per tick would re-consolidate every wave — the H3 bug). bridge.py constructs ONE module-level instance
    that BOTH the manual endpoint AND the autonomous loop drive, so the cursor is held across both.

    The caller is REUSE-ONLY: it never reimplements a driver, never calls a raw entry point, never names a
    forbidden verb. Every effect flows through `background_tick`/`sense_tick`/`RollupDriver.tick`/
    `propose_mode`, which keep the budget + reserve + the non-consequential-destinations floor.
    """
    suite: Any
    idle_seconds: float | None = None       # override the background idle threshold (None = the driver default)
    _rollup: _act.RollupDriver = field(init=False, repr=False)

    def __post_init__(self):
        # ONE held-cursor rollup driver for the whole caller lifetime (the H3 discipline). since=-1 → the
        # first tick reads from the log start; thereafter the cursor advances and is HELD across ticks.
        self._rollup = _act.RollupDriver(suite=self.suite)

    def activation_tick(self, *, sense_event: dict | None = None,
                        mode: str | None = None) -> TickResult:
        """FIRE THE DUE DRIVERS + RUN THE DETECTOR — ONE orchestrated tick (the CALLER mechanism).

        ALWAYS (clock-driven):
          • background_tick — its IDLE GATE decides whether to fire (we go THROUGH the gate, never call
            fire_activation('background') directly — that would bypass the gate).
          • RollupDriver.tick — the HELD cursor consolidates only NEW cognition.wave records since the
            last tick (no re-consolidation; an empty interval is a legible no-op).
          • propose_mode — the detector PRODUCES a candidate and feeds the off/suggest/auto toggle (never
            set_mode directly; off no-ops, suggest surfaces, auto switches).

        EVENT-ONLY:
          • sense_tick — runs ONLY when a REAL `sense_event` is supplied (the endpoint may pass one; the
            autonomous loop passes None). A periodic tick has no sense event, and sense_tick fails loud on
            a fabricated one — so we NEVER manufacture one. (A non-dict supplied event still fails loud
            inside sense_tick — that is its contract; we do not catch it here, it surfaces.)

        Returns a TickResult with each driver's legible outcome + the aggregated reasons. A real driver
        ERROR is NOT swallowed (it re-raises loud — rule 4); only the drivers' OWN legible non-fire
        outcomes ('idle gate closed', 'mode does not allocate', 'no new waves', 'no candidate') are
        collected. `acted` is True iff something actually fired/consolidated/switched."""
        t0 = time.monotonic()
        res = TickResult()

        # ── background (clock) — go THROUGH the idle gate; never bypass it ──────────────────────────
        bg = _act.background_tick(self.suite, mode=mode,
                                  **({"idle_seconds": self.idle_seconds} if self.idle_seconds is not None else {}))
        res.background = bg
        if bg.get("fired"):
            res.acted = True
            res.reasons.append(f"background: fired ({bg.get('reason')})")
        else:
            res.reasons.append(f"background: no-fire ({bg.get('reason')})")

        # ── rollup (clock) — the HELD cursor (no re-consolidation across ticks) ─────────────────────
        ru = self._rollup.tick(mode=mode)
        res.rollup = ru
        if ru.get("consolidated"):
            res.acted = True
            res.reasons.append(f"rollup: consolidated ({ru.get('reason')})")
        else:
            res.reasons.append(f"rollup: no-op ({ru.get('reason')})")

        # ── mode auto-detect (clock) — the detector → the off/suggest/auto toggle (never set_mode) ──
        md = _act.propose_mode(self.suite)
        res.mode = md
        tr = md.get("toggle_result")
        if tr is not None:
            # 'switched' under auto is the only one that CHANGES the live mode; suggest surfaces an event.
            if tr.get("action") in ("switched", "suggested"):
                res.acted = True
            res.reasons.append(f"mode: {tr.get('action')} → {tr.get('candidate')}")
        else:
            res.reasons.append(f"mode: {md.get('reason', 'no candidate')}")

        # ── standing job triggers (clock) — the L10 trigger walk (runtime/jobs.trigger_tick): fires
        # ARMED schedule/change triggers only (proposed ones skip legibly; arming = the operator door
        # arm_job). No second scheduler — this tick IS the scheduler pass. A corrupt trigger-state file
        # raises loud through here (rule 4); per-trigger errors are recorded inside the walk result.
        from runtime import jobs as _jobs
        tw = _jobs.trigger_tick(self.suite)
        res.reasons.append(
            f"triggers: walked {tw['walked']}, fired {len(tw['fired'])}"
            + (f" {[f['job'] for f in tw['fired']]}" if tw["fired"] else "")
            + (f", errors {tw['errors']}" if tw["errors"] else ""))
        if tw["fired"]:
            res.acted = True

        # ── sense (EVENT-ONLY) — fire ONLY on a real supplied event; never fabricate one ────────────
        if sense_event is not None:
            sn = _act.sense_tick(self.suite, sense_event, mode=mode)
            res.sense = sn
            if sn.get("fired"):
                res.acted = True
                res.reasons.append(f"sense: fired ({sn.get('reason')})")
            else:
                res.reasons.append(f"sense: no-fire ({sn.get('reason')})")

        res.wall_s = round(time.monotonic() - t0, 3)
        return res


# =====================================================================================================
# THE AUTONOMOUS LOOP (OFF BY DEFAULT) — the daemon that ticks the caller on a cadence WHEN ARMED.
#
# This is the ONLY part that is dormant-by-default. The split mirrors the wire's proven shape: the
# TESTABLE unit (`_loop_iteration`) is called directly by the suite/test; `run_activation_loop` is the
# daemon thread that calls it forever. Standing up the daemon at all is gated on activation_loop_enabled()
# → NEEDS-TIM. A clock tick passes NO sense_event (sense stays event-only — never fabricated on a clock).
# =====================================================================================================

def _loop_iteration(caller: ActivationCaller, *, on_tick: Callable[[TickResult], None] | None = None) -> TickResult:
    """ONE autonomous-loop iteration: a clock tick (NO sense_event — sense is event-only). The daemon
    calls this in `while enabled: _loop_iteration(...); sleep(cadence)`. Factored out so a by-use test
    drives the iteration DIRECTLY (no ThreadingHTTPServer, no real sleep) — exactly how the wire suites
    call the dispatch driver directly rather than spawning the daemon. `on_tick` is an optional observer
    (telemetry/test) called with the result."""
    res = caller.activation_tick()
    if on_tick is not None:
        on_tick(res)
    return res


def run_activation_loop(caller: ActivationCaller, *, stop: Callable[[], bool] | None = None,
                        tick_seconds: float | None = None,
                        on_tick: Callable[[TickResult], None] | None = None) -> None:
    """THE AUTONOMOUS DAEMON BODY — tick the caller on a cadence, ONLY while armed. This is what a
    background thread runs; it is NEVER started unless activation_loop_enabled() is True (the dormancy
    gate, checked by the spawn site in bridge.py AND re-checked here each iteration so disarming the env
    stops the loop). A real per-iteration error is caught ONLY so one bad tick can't kill the daemon — it
    emits a LOUD warning event + keeps going; it never pretends success (rule 4). `stop` is an optional
    extra predicate (ops/test) to break the loop; `tick_seconds`/cadence is the live env read.

    NOT auto-started by this build. The spawn (a thread/`.start()`) is bridge.py's, gated dormant; arming
    the live cadence is the operator's greenlight (needs-tim)."""
    suite = caller.suite
    while activation_loop_enabled() and not (stop is not None and stop()):
        try:
            _loop_iteration(caller, on_tick=on_tick)
        except Exception as e:   # noqa: BLE001 — one bad tick must not kill the daemon, but it FAILS LOUD
            try:
                suite._emit("warning", f"activation loop iteration errored (loop continues): {e}",
                            address="ui://chrome/toolbar")
            except Exception:
                pass
        time.sleep(tick_seconds if tick_seconds is not None else loop_tick_seconds())


def maybe_start_activation_loop(caller: ActivationCaller, *, on_tick: Callable[[TickResult], None] | None = None):
    """THE GUARDED SPAWN SEAM — start the autonomous daemon IFF deliberately armed; otherwise spawn
    NOTHING and return None. bridge.py calls this once at startup: by default (env unset) it is a pure
    no-op — no thread, no tick — keeping the always-on cognition INERT BY DEFAULT. Only when the operator
    has set COMPANY_ACTIVATION_LOOP does it stand up the daemon thread (daemon=True so it never blocks
    process shutdown). Enabling the env is the needs-tim behavior change; THIS build defaults it OFF.

    Returns the spawned threading.Thread (armed) or None (dormant — the default)."""
    if not activation_loop_enabled():
        return None
    import threading
    th = threading.Thread(target=run_activation_loop, args=(caller,),
                          kwargs={"on_tick": on_tick}, name="activation-caller-loop", daemon=True)
    th.start()
    return th
