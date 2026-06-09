"""tests/mode_autodetect_acceptance.py — Concurrent Cognition Group I · the mode AUTO-DETECTOR.

The toggle (`Suite.autodetect_mode`) already honoured off/suggest/auto over a SUPPLIED candidate
(autodetect_setter_acceptance); the gap (mode-map lost-opportunity #6) was that NOTHING produced one.
Group I builds the DETECTOR that reads the live signal and PRODUCES a candidate, feeding the toggle —
and makes the detection rules a FILE-DISCOVERED REGISTRY (not a hardcoded list of lambdas).

WHAT THIS PROVES (verify-by-use):
  1. REGISTRY-IS-TRUTH — the detection rules are a file-discovered registry
     (runtime/mode_detection_rules.py + mode_detection_rules/<id>.py), mirroring roles/projections; a
     dropped FILE is discovered (add-a-row=a-FILE, no code edit); a removed file un-registers.
  2. ORDER-BEARING — first-match-wins is by the declared `priority`, NOT listdir/filename order (the
     adversarial filename test: a rule with an alphabetically-first filename but a high priority fires
     LAST).
  3. DATA-AST CONDITIONS — each rule's `when` is a rules.RULE_OPS data-AST (the ONE predicate language),
     validated at discovery + evaluated PURE; a lambda/string/eval condition is rejected.
  4. THE DETECTOR — a live signal deterministically produces the right candidate (background/focus/
     listening); the None-handling holds at startup (idle_seconds None never TypeErrors); a candidate
     unregistered in MODES FAILS LOUD (rule 8).
  5. SUGGEST-NOT-SWITCH — propose_mode feeds the toggle: off=no-op, suggest=surfaces (a 'mode' event,
     mode unchanged), auto=switches; the detector NEVER calls set_mode directly.
  6. THE FLOOR — the detector produces a candidate + feeds the toggle; it emits NO resolve/approve/
     dispatch (the suggest path is a 'mode' event, the auto path is set_mode — never a consequential verb).
  7. FAIL-LOUD at discovery — a malformed rule file RAISES at discover (never a silent skip).
  8. DRIFT HOME — every discovered rule is reflected in mode_detection_rules/AGENTS.md + the registry is
     named in runtime/AGENTS.md (mirrors projections_acceptance → projections/AGENTS.md).

No GPU dependency — the detector is a deterministic READ over a synthetic activity signal.
"""
import os, sys, tempfile, time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from runtime import activation as act
from runtime.mode_detection_rules import ModeDetectionRuleRegistry, _build_rule

NODES = os.path.join(ROOT, "nodes")
MDR_DIR = os.path.join(ROOT, "mode_detection_rules")
PASS = 0
NOW = time.time()


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def fresh_suite():
    store = FsStore(os.path.join(tempfile.mkdtemp(prefix="mdr-"), "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    return Suite(store, reg, nodes_dir=NODES)


def _seed_activity(s, age_s):
    """Seed one operator-activity event `age_s` seconds ago as the LAST event (so idle_seconds is
    deterministic regardless of any config-emit ordering)."""
    s.store.append_event({"kind": "chat", "summary": "x",
                          "ts": datetime.fromtimestamp(NOW - age_s, timezone.utc).isoformat()})


print("\n=== 1 · REGISTRY-IS-TRUTH (file-discovered, like roles/projections) ===")
s = fresh_suite()
reg = s.mode_detection_rule_registry
check("the registry is wired onto the Suite", isinstance(reg, ModeDetectionRuleRegistry))
check("the seed rules are discovered from mode_detection_rules/*.py",
      {"background", "focus", "listening"}.issubset(set(reg)))
check("dict-like access works (reg[id], id in reg, .get)",
      reg["background"].candidate == "background" and "focus" in reg and reg.get("nope") is None)
# add-a-row = a FILE (registry-is-truth): drop a file → discovered; remove → un-registered (rediscover)
adv = os.path.join(MDR_DIR, "acctestdropped.py")
open(adv, "w").write(
    'MODE_DETECTION_RULE={"id":"acctestdropped","candidate":"text-only","why":"dropped-file test",'
    '"priority":50,"when":{"op":"eq","args":[{"op":"lit","value":1},{"op":"lit","value":2}]}}')
try:
    reg2 = ModeDetectionRuleRegistry().discover([MDR_DIR])
    check("a DROPPED rule file is discovered (add-a-row=a-FILE, no code edit)", "acctestdropped" in reg2)
    reg2.rediscover([MDR_DIR])
    check("rediscover still sees it while the file exists", "acctestdropped" in reg2)
finally:
    os.remove(adv)
reg3 = ModeDetectionRuleRegistry().discover([MDR_DIR])
check("a REMOVED rule file un-registers (rediscover from the filesystem)", "acctestdropped" not in reg3)


print("\n=== 2 · ORDER-BEARING — priority wins, NOT listdir/filename order ===")
ordered = s.mode_detection_rule_registry.ordered()
check("ordered() is ascending by priority (background<focus<listening)",
      [r.id for r in ordered] == ["background", "focus", "listening"]
      and [r.priority for r in ordered] == [10, 20, 30])
# adversarial: an alphabetically-FIRST filename with a HIGH priority must fire LAST (not hijack).
adv = os.path.join(MDR_DIR, "aaa_adversarial.py")
open(adv, "w").write(
    'MODE_DETECTION_RULE={"id":"aaa_adversarial","candidate":"background","why":"adv","priority":99,'
    '"when":{"op":"eq","args":[{"op":"lit","value":1},{"op":"lit","value":1}]}}')
try:
    rega = ModeDetectionRuleRegistry().discover([MDR_DIR])
    order = [r.id for r in rega.ordered()]
    check("an alphabetically-first filename with priority 99 fires LAST (priority, not listdir)",
          order[0] == "background" and order[-1] == "aaa_adversarial")
finally:
    os.remove(adv)


print("\n=== 3 · DATA-AST CONDITIONS (rules.RULE_OPS, the ONE predicate language) ===")
check("a rule's `when` is a dict data-AST (not a lambda/callable)",
      isinstance(reg["background"].when, dict) and not callable(reg["background"].when))
# a malformed AST is rejected at build (the same validate_ast the G3 rules ride).
raised = False
try:
    _build_rule("x", {"id": "x", "candidate": "focus", "why": "w", "priority": 1,
                      "when": {"op": "NOT_AN_OP", "args": []}})
except ValueError as e:
    raised = "not a valid" in str(e)
check("a `when` outside the RULE_OPS grammar FAILS LOUD at build (reuse-don't-parallel)", raised)
# a lambda condition is rejected (it's not a dict AST).
raised = False
try:
    _build_rule("x", {"id": "x", "candidate": "focus", "why": "w", "priority": 1,
                      "when": (lambda s: True)})
except ValueError as e:
    raised = "must be a dict" in str(e)
check("a lambda condition is REJECTED (a rule is declared DATA, never code)", raised)


print("\n=== 4 · THE DETECTOR — deterministic candidate from a live signal ===")
# long-idle → background
s = fresh_suite(); _seed_activity(s, 10000)
d = act.detect_mode_candidate(s, now_epoch=NOW)
check("a long-idle signal deterministically detects 'background'",
      d["candidate"] == "background" and d["rule"] == "background" and d["why"]
      and d["signal"]["idle_seconds"] >= 900)
check("the detector is a pure READ → carries the signal + the matched rule id + priority",
      d["rule"] == "background" and d["priority"] == 10)
# active + clear inbox → focus
s = fresh_suite(); _seed_activity(s, 5)
d = act.detect_mode_candidate(s, now_epoch=NOW)
check("a recently-active signal with an empty inbox detects 'focus'",
      d["candidate"] == "focus" and d["signal"]["idle_seconds"] < 90 and d["signal"]["inbox"] == 0)
# inbox piling up → listening (active so not background, inbox>0 so not focus)
s = fresh_suite(); s.surface_review({"title": "pile up", "action": "build_result_review"}); _seed_activity(s, 5)
d = act.detect_mode_candidate(s, now_epoch=NOW)
check("a non-empty inbox detects 'listening' (the inbox signal is READ, not stuck at 0)",
      d["candidate"] == "listening" and d["signal"]["inbox"] > 0)
# NONE-HANDLING at startup: idle_seconds is None → no TypeError, clean no-candidate (none of the seeds fire)
s = fresh_suite()
d = act.detect_mode_candidate(s, now_epoch=NOW)
check("at startup (idle_seconds None, empty inbox) no rule matches → clean no-op (no TypeError)",
      d["candidate"] is None and d["signal"]["idle_seconds"] is None)
# determinism: identical signal → identical result, twice
s = fresh_suite(); _seed_activity(s, 10000)
a1 = act.detect_mode_candidate(s, now_epoch=NOW); a2 = act.detect_mode_candidate(s, now_epoch=NOW)
check("identical signal → identical candidate (deterministic — no model, no clock-in-the-rule)", a1 == a2)
# a candidate UNREGISTERED in MODES fails loud (rule 8) — drop a rule whose candidate is fabricated.
adv = os.path.join(MDR_DIR, "bogusmode.py")
open(adv, "w").write(
    'MODE_DETECTION_RULE={"id":"bogusmode","candidate":"NONSENSE_MODE","why":"x","priority":1,'
    '"when":{"op":"eq","args":[{"op":"lit","value":1},{"op":"lit","value":1}]}}')
raised = False
try:
    sb = fresh_suite()       # discovers bogusmode (a real file) → detect must fail loud
    try:
        act.detect_mode_candidate(sb, now_epoch=NOW)
    except ValueError as e:
        raised = "unregistered mode" in str(e)
finally:
    os.remove(adv)
check("a rule proposing an unregistered mode FAILS LOUD at detect (rule 8)", raised)


print("\n=== 5 · SUGGEST-NOT-SWITCH — propose_mode feeds the toggle (off/suggest/auto) ===")
def _seeded(mode_, toggle_, age_s=10000):
    su = fresh_suite(); su.set_mode(mode_); su.set_rhm_config({"MODE_AUTODETECT": toggle_})
    _seed_activity(su, age_s)
    return su
# suggest → surfaces a 'mode' event, mode UNCHANGED
s = _seeded("listening", "suggest")
ev0 = len([e for e in s.events_since(-1) if e.get("kind") == "mode"])
out = act.propose_mode(s, now_epoch=NOW)
ev1 = len([e for e in s.events_since(-1) if e.get("kind") == "mode"])
check("propose_mode under 'suggest' SURFACES the candidate (a 'mode' event) and does NOT switch",
      out["toggle_result"]["action"] == "suggested" and out["toggle_result"]["applied"] is None
      and s.get_mode() == "listening" and ev1 == ev0 + 1)
# auto → switches via the one set_mode
s = _seeded("listening", "auto")
det = act.detect_mode_candidate(s, now_epoch=NOW)
out = act.propose_mode(s, now_epoch=NOW)
check("propose_mode under 'auto' SWITCHES to the detected candidate (via the toggle, not the detector)",
      out["toggle_result"]["action"] == "switched" and s.get_mode() == det["candidate"]
      and det["candidate"] != "listening")
# off → no-op
s = _seeded("listening", "off")
out = act.propose_mode(s, now_epoch=NOW)
check("propose_mode under 'off' NO-OPs (toggle posture honoured; no silent switch)",
      out["toggle_result"]["action"] == "noop" and s.get_mode() == "listening")
# candidate == live mode → no re-propose
s = _seeded("listening", "auto")
live = act.detect_mode_candidate(s, now_epoch=NOW)["candidate"]
s.set_mode(live); _seed_activity(s, 10000)
out = act.propose_mode(s, now_epoch=NOW)
check("a candidate equal to the live mode is a no-op (no re-propose)",
      out["toggle_result"] is None and "already the live mode" in out["reason"])


print("\n=== 6 · THE FLOOR — the detector emits NO resolve/approve/dispatch ===")
s = _seeded("listening", "auto")
before = s.events_since(-1)
act.propose_mode(s, now_epoch=NOW)
new_kinds = {e.get("kind") for e in s.events_since(-1)[len(before):]}
check("propose_mode emits only mode-lifecycle kinds (no resolve/approve/dispatch — the floor)",
      not (new_kinds & {"resolve", "approve", "decision.dispatch", "decision.implemented"}))
# the detector itself is a pure read: no events at all.
s = fresh_suite(); _seed_activity(s, 10000)
n0 = len(s.events_since(-1))
act.detect_mode_candidate(s, now_epoch=NOW)
check("detect_mode_candidate is a PURE READ (emits/fires/switches nothing)", len(s.events_since(-1)) == n0)


print("\n=== 7 · FAIL-LOUD at discovery — a malformed rule file RAISES ===")
adv = os.path.join(MDR_DIR, "malformed.py")
open(adv, "w").write('MODE_DETECTION_RULE={"id":"malformed","candidate":"focus"}')  # missing why/when/priority
raised = False
try:
    try:
        ModeDetectionRuleRegistry().discover([MDR_DIR])
    except ValueError as e:
        raised = "missing required" in str(e)
finally:
    os.remove(adv)
check("a malformed rule file FAILS LOUD at discovery (never a silent skip)", raised)


print("\n=== 8 · DRIFT HOMES — discovered rules reflected in the constitutions ===")
mdr_agents = open(os.path.join(MDR_DIR, "AGENTS.md"), encoding="utf-8").read()
for rid in ("background", "focus", "listening"):
    check(f"drift: '{rid}' is reflected in mode_detection_rules/AGENTS.md", f"`{rid}`" in mdr_agents)
runtime_agents = open(os.path.join(ROOT, "runtime", "AGENTS.md"), encoding="utf-8").read()
check("drift: the registry is named in runtime/AGENTS.md (the Group-I detector section)",
      "mode_detection_rules" in runtime_agents or "ModeDetectionRuleRegistry" in runtime_agents)
check("drift: detect_mode_candidate + propose_mode named in runtime/AGENTS.md",
      "detect_mode_candidate" in runtime_agents and "propose_mode" in runtime_agents)


print(f"\nPASS ({PASS} checks) — the mode auto-detector is a file-discovered, order-bearing, data-AST "
      f"registry feeding the existing off/suggest/auto toggle (suggest-not-switch; the floor holds).")
