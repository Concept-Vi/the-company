"""tests/activation_drivers_acceptance.py — Concurrent Cognition Group H + I.

Proves the NET-NEW DECISION LAYER over the (already-built G5) activation entry points:

  H1 — background_tick: the IDLE GATE. Fires fire_activation('background') ONLY when the operator has
       been quiet >= the threshold AND the mode allocates background; a non-fire is a legible reason.
  H2 — sense_tick: the EVENT INTAKE. Shapes a RAW event → the sense_event dict + dispatches
       fire_activation('sense'); fail-loud on a non-dict raw event.
  H3 — RollupDriver: the HELD CURSOR. .tick() consolidates only the waves since the last tick (no
       re-consolidation), advancing the cursor; an empty interval is a legible no-op.
  I1 — detect_mode_candidate / propose_mode: the DETECTOR produces a candidate from the live signal
       (deterministic, registry-driven MODE_DETECTION_RULES) and FEEDS the existing off/suggest/auto
       toggle (never set_mode directly). A rule's candidate must be a registered mode (fail-loud).

VERIFY BY USE: the driver layer is exercised with SYNTHETIC idle/event/clock signals and a recording
stub over the entry point (so the DECISION is proven deterministically, no GPU dependency); the real
entry-point path is asserted by the existing activation_contexts_acceptance (it fires the live cast).
An OPTIONAL live-path check fires the real background entry point IFF the resident model is reachable.

Drift: OPERATOR_ACTIVITY_KINDS + MODE_DETECTION_RULES are reflected in runtime/AGENTS.md (asserted here,
mirroring rules_acceptance → RULE_OPS).
"""
import os, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from runtime import activation as act

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def fresh_suite():
    store = FsStore(os.path.join(tempfile.mkdtemp(prefix="actdrv-"), "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    return Suite(store, reg, nodes_dir=NODES)


class _Recorder:
    """A recording stub over fire_activation/consolidate_rollup — proves the DRIVER DECISION (gate/intake/
    cursor) deterministically WITHOUT firing the live 4B cast. The driver is the net-new; the entry point
    it delegates to is reused + already proven live by activation_contexts_acceptance."""
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


# ---------------------------------------------------------------------------------------------------
# DRIFT — the two net-new registries are reflected in their drift home.
# ---------------------------------------------------------------------------------------------------
with open(os.path.join(ROOT, "runtime", "AGENTS.md"), encoding="utf-8") as f:
    agents_md = f.read()
check("OPERATOR_ACTIVITY_KINDS is named in its drift home runtime/AGENTS.md",
      "OPERATOR_ACTIVITY_KINDS" in agents_md)
check("MODE_DETECTION_RULES is named in its drift home runtime/AGENTS.md",
      "MODE_DETECTION_RULES" in agents_md)
check("the H drivers (background_tick/sense_tick/RollupDriver) are reflected in the drift home",
      "background_tick" in agents_md and "sense_tick" in agents_md and "RollupDriver" in agents_md)
check("the I detector (detect_mode_candidate/propose_mode) is reflected in the drift home",
      "detect_mode_candidate" in agents_md and "propose_mode" in agents_md)
check("the always-on caller is documented as needs-tim (no daemon stood up)",
      "needs-tim" in agents_md and ("never a thread" in agents_md or "no always-on" in agents_md))


# ---------------------------------------------------------------------------------------------------
# THE SHARED ACTIVITY READER — deterministic READ, fires/emits nothing.
# ---------------------------------------------------------------------------------------------------
s = fresh_suite()
n0 = len(s.events_since(-1))
sig = act.activity_signal(s)
check("activity_signal reports the live mode", sig["mode"] == s.get_mode())
check("activity_signal is a pure READ — emits no event", len(s.events_since(-1)) == n0)
check("activity_signal carries the idle/inbox/recent-kinds signal shape",
      set(("idle_seconds", "last_activity", "mode", "inbox", "recent_kinds")) <= set(sig))

# seed an operator-activity event with a controlled ts, then prove idle_seconds is measured from it.
now = time.time()
from datetime import datetime, timezone
s.store.append_event({"kind": "chat", "summary": "hi",
                      "ts": datetime.fromtimestamp(now - 5, timezone.utc).isoformat()})
sig = act.activity_signal(s, now_epoch=now)
check("idle_seconds is measured from the last operator-activity event (~5s)",
      sig["last_activity"] == "chat" and 4.0 <= sig["idle_seconds"] <= 6.0)
check("OPERATOR_ACTIVITY_KINDS includes the turn signals + operator graph acts",
      {"chat", "cognition.turn.done", "create", "connect"} <= act.OPERATOR_ACTIVITY_KINDS)
check("the system's OWN background activity is EXCLUDED (can't reset its own idle clock)",
      "activation" not in act.OPERATOR_ACTIVITY_KINDS and "op.run" not in act.OPERATOR_ACTIVITY_KINDS)


# ---------------------------------------------------------------------------------------------------
# H1 — the BACKGROUND DRIVER (idle gate).
# ---------------------------------------------------------------------------------------------------
s = fresh_suite()
s.set_mode("listening")                                     # listening allocates `background` live
rec = _install_recorder(s)
# operator ACTIVE 5s ago → the gate must NOT fire (below threshold).
s.store.append_event({"kind": "chat", "summary": "active",
                      "ts": datetime.fromtimestamp(now - 5, timezone.utc).isoformat()})
r = act.background_tick(s, idle_seconds=90.0, now_epoch=now)
check("H1 · background_tick does NOT fire while the operator is active (idle gate closed)",
      r["fired"] is False and "active" in r["reason"] and len(rec.fired) == 0)
# operator quiet 200s → the gate FIRES, delegating to the (reused) entry point.
s2 = fresh_suite(); s2.set_mode("listening"); rec2 = _install_recorder(s2)
s2.store.append_event({"kind": "chat", "summary": "old",
                       "ts": datetime.fromtimestamp(now - 200, timezone.utc).isoformat()})
r = act.background_tick(s2, idle_seconds=90.0, now_epoch=now)
check("H1 · background_tick FIRES when the operator is idle past the threshold",
      r["fired"] is True and rec2.fired == [("background", "listening", None)])
check("H1 · the fired result LANDS at a non-consequential destination (not a no-op)",
      r["result"].routed and r["result"].routed[0]["destination"] in ("surface", "address", "lane")
      and r["result"].routed[0]["acted"] is True)
# a mode that does NOT allocate background → the gate refuses with a legible reason (no fire).
s3 = fresh_suite(); s3.set_mode("walkthrough"); rec3 = _install_recorder(s3)
r = act.background_tick(s3, idle_seconds=0.0, now_epoch=now)
check("H1 · background_tick refuses when the mode does not allocate background (legible, no fire)",
      r["fired"] is False and "does not allocate" in r["reason"] and len(rec3.fired) == 0)


# ---------------------------------------------------------------------------------------------------
# H2 — the SENSE DRIVER (event intake).
# ---------------------------------------------------------------------------------------------------
s = fresh_suite()
s.set_mode("watch-and-react")                              # allocates `sense` live
rec = _install_recorder(s)
r = act.sense_tick(s, {"kind": "window-focus", "detail": "VS Code opened"})
check("H2 · sense_tick shaped the raw event → a sense_event with a summary the cast reads",
      r["fired"] is True and "window-focus" in r["sense_event"]["summary"]
      and "VS Code opened" in r["sense_event"]["summary"])
check("H2 · sense_tick dispatched fire_activation('sense') with the shaped event (reused entry point)",
      rec.fired and rec.fired[-1][0] == "sense" and rec.fired[-1][2] == r["sense_event"])
check("H2 · the raw event's fields are PRESERVED through the shaping (not discarded)",
      r["sense_event"]["kind"] == "window-focus" and r["sense_event"]["detail"] == "VS Code opened")
# an explicit summary is honoured as-is.
r = act.sense_tick(s, {"summary": "the build finished"})
check("H2 · an explicit summary is used as the cast's utterance verbatim",
      r["sense_event"]["summary"] == "the build finished")
# a non-dict raw event fails loud.
raised = False
try:
    act.sense_tick(s, "not a dict")
except ValueError as e:
    raised = "raw_event must be a dict" in str(e)
check("H2 · a non-dict raw event FAILS LOUD (never a fabricated sense event)", raised)
# a mode that does NOT allocate sense → no fire, legible reason.
s4 = fresh_suite(); s4.set_mode("focus"); rec4 = _install_recorder(s4)
r = act.sense_tick(s4, {"summary": "x"})
check("H2 · sense_tick refuses when the mode does not allocate sense (legible, no fire)",
      r["fired"] is False and "does not allocate" in r["reason"] and len(rec4.fired) == 0)


# ---------------------------------------------------------------------------------------------------
# H3 — the ROLLUP DRIVER (held cursor — no re-consolidation across ticks).
# ---------------------------------------------------------------------------------------------------
s = fresh_suite()
rec = _install_recorder(s)
drv = act.RollupDriver(suite=s)
# tick 1 with NO waves → a legible no-op, cursor advances past the empty interval.
r1 = drv.tick()
check("H3 · a tick with no new cognition.wave records is a legible no-op (no consolidation)",
      r1["consolidated"] is False and len(rec.rollups) == 0)
# inject a wave AFTER the cursor → tick 2 consolidates exactly that wave, from the held cursor.
since_after_t1 = drv.since
s.store.append_event({"kind": "cognition.wave",
                      "summary": {"turn_id": "t1", "n_roles": 1,
                                  "roles": [{"role": "focus", "address": "run://t1/focus", "ok": True, "ms": 42}]}})
r2 = drv.tick()
check("H3 · tick 2 consolidated the NEW wave from the HELD cursor (not from -1)",
      r2["consolidated"] is True and rec.rollups[-1][0] == since_after_t1)
check("H3 · the cursor ADVANCED past the consolidated wave", drv.since > since_after_t1)
# tick 3 with no further waves → no-op (the prior wave is NOT re-consolidated).
r3 = drv.tick()
check("H3 · tick 3 does NOT re-consolidate the already-consolidated wave (cursor held)",
      r3["consolidated"] is False and len(rec.rollups) == 1)


# ---------------------------------------------------------------------------------------------------
# I1 — the MODE AUTO-DETECTOR (produces a candidate → feeds the existing toggle).
# ---------------------------------------------------------------------------------------------------
# every declared rule's candidate is a REGISTERED mode (no fabrication).
s = fresh_suite()
for i, rule in enumerate(act.MODE_DETECTION_RULES):
    check(f"I1 · MODE_DETECTION_RULES[{i}] candidate {rule['candidate']!r} is a registered mode",
          rule["candidate"] in s.MODES)

# DETERMINISTIC: an idle signal past 10x threshold → the 'background' candidate (first matching rule).
s = fresh_suite(); s.set_mode("listening")
s.store.append_event({"kind": "chat", "summary": "old",
                      "ts": datetime.fromtimestamp(now - 10000, timezone.utc).isoformat()})
det = act.detect_mode_candidate(s, now_epoch=now)
check("I1 · a long-idle signal deterministically detects the 'background' candidate",
      det["candidate"] == "background" and det["why"])
check("I1 · the detector is a pure READ → it carries the signal + the rule index it matched",
      det["rule_index"] is not None and det["signal"]["idle_seconds"] >= 900)

# the detector FEEDS the toggle (not set_mode). NOTE: set_mode/set_rhm_config emit operator-activity
# events, so we CONFIGURE first, then seed the stale activity event LAST (the controlled idle signal).
def _seeded(mode_, toggle_, age_s=10000):
    """A fresh suite at `mode_`, toggle `toggle_`, with one stale operator-activity event `age_s` ago as
    the LAST event — so the idle signal is deterministically large regardless of config-emit ordering."""
    su = fresh_suite(); su.set_mode(mode_); su.set_rhm_config({"MODE_AUTODETECT": toggle_})
    su.store.append_event({"kind": "chat", "summary": "old",
                           "ts": datetime.fromtimestamp(now - age_s, timezone.utc).isoformat()})
    return su

# Under 'suggest' it SURFACES, never switches.
s = _seeded("listening", "suggest")
det = act.detect_mode_candidate(s, now_epoch=now)
cand = det["candidate"]
ev0 = len([e for e in s.events_since(-1) if e.get("kind") == "mode"])
out = act.propose_mode(s, now_epoch=now)
ev1 = len([e for e in s.events_since(-1) if e.get("kind") == "mode"])
check("I1 · propose_mode under 'suggest' SURFACES the candidate (a 'mode' event) and does NOT switch",
      out["toggle_result"]["action"] == "suggested" and out["toggle_result"]["applied"] is None
      and s.get_mode() == "listening" and ev1 == ev0 + 1)

# under 'auto' it SWITCHES via the one set_mode (the toggle's path, not the detector's).
s = _seeded("listening", "auto")
det = act.detect_mode_candidate(s, now_epoch=now)
out = act.propose_mode(s, now_epoch=now)
check("I1 · propose_mode under 'auto' SWITCHES to the detected candidate (via the toggle)",
      out["toggle_result"]["action"] == "switched"
      and out["toggle_result"]["candidate"] == det["candidate"]
      and s.get_mode() == det["candidate"] and det["candidate"] != "listening")

# under 'off' it NO-OPs (the toggle owns the posture; the detector never bypasses it).
s2 = _seeded("listening", "off")
out = act.propose_mode(s2, now_epoch=now)
check("I1 · propose_mode under 'off' NO-OPs (toggle posture honoured; no silent switch)",
      out["toggle_result"]["action"] == "noop" and s2.get_mode() == "listening")

# a candidate EQUAL to the live mode is a no-op (don't re-propose the mode already on). Put the suite
# in the very mode the long-idle signal would detect, so the candidate == the live mode.
s3 = _seeded("listening", "auto")
live_cand = act.detect_mode_candidate(s3, now_epoch=now)["candidate"]
s3.set_mode(live_cand)
s3.store.append_event({"kind": "chat", "summary": "old",
                       "ts": datetime.fromtimestamp(now - 10000, timezone.utc).isoformat()})
out = act.propose_mode(s3, now_epoch=now)
check("I1 · a candidate equal to the live mode is a no-op (no re-propose)",
      out["toggle_result"] is None and "already the live mode" in out["reason"])

# a rule proposing an UNREGISTERED mode fails loud (rule 8).
_orig = act.MODE_DETECTION_RULES
try:
    act.MODE_DETECTION_RULES = [{"candidate": "nonsense", "why": "x", "when": lambda s: True}]
    raised = False
    try:
        act.detect_mode_candidate(fresh_suite())
    except ValueError as e:
        raised = "unregistered mode" in str(e)
    check("I1 · a rule proposing an unregistered mode FAILS LOUD (rule 8)", raised)
finally:
    act.MODE_DETECTION_RULES = _orig


# ---------------------------------------------------------------------------------------------------
# OPTIONAL — the REAL entry-point path through the driver (fires the live cast IFF the model is reachable).
# Not asserted hard (no GPU dependency in CI); the live cast is proven by activation_contexts_acceptance.
# ---------------------------------------------------------------------------------------------------
try:
    s = fresh_suite(); s.set_mode("listening")
    r = act.background_tick(s, idle_seconds=0.0)            # idle gate forced open → real fire_activation
    if r.get("fired") and r.get("result") and getattr(r["result"], "fired_roles", None):
        check("LIVE · background_tick fired the REAL cast through the reused entry point",
              len(r["result"].fired_roles) >= 1)
    else:
        print("  --  LIVE background fire skipped (cast empty / non-fire) — driver layer proven by stub")
except Exception as e:
    print(f"  --  LIVE background fire skipped (model unreachable: {type(e).__name__}) — proven by stub")


print(f"\nactivation_drivers_acceptance: {PASS} checks passed")
