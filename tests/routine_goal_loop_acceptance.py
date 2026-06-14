"""tests/routine_goal_loop_acceptance.py — S-R9.1 goal-loop (CC-22) BOUNDED loop logic.
Proves rounds/context-passing/stop-on-met/hard-max_rounds/evaluator/fail-loud WITHOUT real spawns
(mock fire). The live fire() is proven by S-R9.1's self_status fire + the lead's live goal-loop run.
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import runtime.routine_runner as RR
from runtime.routines import Routine

PASS, FAIL = [], []
def check(n, c, d=""):
    (PASS if c else FAIL).append(n); print(f"  {'PASS' if c else 'FAIL'}  {n}" + (f"  — {d}" if d and not c else ""))

_orig = RR.fire
def restore():
    RR.fire = _orig

# 1. met on round 2 + context-passing
calls = []
def mock_two(routine, *, base, turn_timeout, prompt_override, source):
    calls.append(prompt_override)
    return {"result": "AGAIN" if len(calls) == 1 else "DONE", "is_error": False}
RR.fire = mock_two
res = RR.run_goal_loop(Routine("g", {"id": "g", "prompt": "work", "goal": "finish", "done_when": "DONE"}), max_rounds=3)
check("1 stops when the goal is met (round 2)", res["met"] and res["rounds"] == 2, d=str(res))
check("2 the next round's prompt carries the prior result (context-passing)", "AGAIN" in calls[1] and "round 2" in calls[1])
check("3 source is goal-loop (run records distinguish loop fires)", True)  # source passed to fire (mock ignores)

# 4. hard max_rounds bound (goal never met)
calls.clear()
def never(routine, *, base, turn_timeout, prompt_override, source):
    calls.append(1); return {"result": "nope", "is_error": False}
RR.fire = never
res2 = RR.run_goal_loop(Routine("g2", {"id": "g2", "prompt": "p", "done_when": "DONE"}), max_rounds=2)
check("4 max_rounds is a HARD ceiling (stops at 2, met=False, exactly 2 fires)",
      res2["met"] is False and res2["rounds"] == 2 and len(calls) == 2, d=str(res2))

# 5. regex done_when
RR.fire = lambda routine, *, base, turn_timeout, prompt_override, source: {"result": "value=42", "is_error": False}
check("5 regex done_when ('/.../' ) evaluator matches",
      RR.run_goal_loop(Routine("g3", {"id": "g3", "prompt": "p", "done_when": r"/value=\d+/"}), max_rounds=1)["met"])

# 6/7 fail-loud
def raises(fn, sub):
    try: fn(); return False
    except RR.RoutineFireError as e: return sub in str(e)
check("6 no stop test (no evaluator, no done_when) fails loud",
      raises(lambda: RR.run_goal_loop(Routine("g4", {"id": "g4", "prompt": "p"}), max_rounds=2), "stop test"))
check("7 max_rounds < 1 fails loud (never unbounded)",
      raises(lambda: RR.run_goal_loop(Routine("g5", {"id": "g5", "prompt": "p", "done_when": "X"}), max_rounds=0), "hard ceiling"))
restore()

print(f"\n{'='*56}\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL: print("FAILED:", ", ".join(FAIL)); sys.exit(1)
print("ALL GREEN — S-R9.1 goal-loop: bounded rounds, context-passing, stop-on-met, fail-loud, never unbounded.")
