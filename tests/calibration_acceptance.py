"""tests/calibration_acceptance.py — D: the calibration harness (experiment → measure → save).

Turns a detector's trust from assertion into a measured NUMBER per config (SEM-3's "3 of 82" made
systematic), against captured-incident FIXTURES with STABLE ground truth. The fixtures pin the false-wire
incident as a permanent regression case (comment-mention / existence-assertion / prose-in-string must read
ORPHAN; real fetch/EventSource/HTTP must read WIRED) — so the score tests the detector's LOGIC, immune to the
live tree changing (live churn is the burn-down's domain, not calibration's). The framework is config-generic:
the same scorer measures this structural detector single-config now, and a semantic detector under N
model/embedding configs when cognition's engine lands (the experiment axis). Proven:
  · the current AST/call-marker logic scores precision=1.0, recall=1.0 on the fixtures;
  · the harness CATCHES the false-wire regression — the OLD substring logic scores recall=0.0 on the
    orphan class (every comment/assertion/prose mention false-wired). The number moves when the detector
    regresses — that discriminating power is the whole point.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from runtime import coherence_detect as cd
from runtime import coherence_calibrate as cal

PASS = 0
def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")

fixtures = cal.load_fixtures(os.path.join(ROOT, "build-prep", "coherence", "eval-set", "reachability.json"))
check("fixtures load (captured-incident, stable ground truth)", len(fixtures) >= 6)
check("the 3 false-wire incident classes are present (comment/assertion/prose → orphan)",
      sum(1 for f in fixtures if f["orphan"]) >= 3)

# ── the CURRENT AST/call-marker logic — score its LOGIC over the fixtures ─────────────────────────────
def classify_current(route, fe, tests):
    return cd.route_is_wired(route, cd._strip_comments(fe), cd._strip_comments(tests))
pred, truth = cal.score_reachability(fixtures, classify_current)
score = cal.calibrate(pred, truth, config="ast-current")
check("current detector recall=1.0 (catches every captured orphan — no false-WIRE)", score["recall"] == 1.0)
check("current detector precision=1.0 (no real consumer false-orphaned)", score["precision"] == 1.0)

# ── the harness CATCHES the regression: the OLD substring logic (route in text) false-wires the mentions ─
def classify_old(route, fe, tests):
    return (route in fe) or (route in tests)     # the original substring-anywhere bug
pred_old, _ = cal.score_reachability(fixtures, classify_old)
score_old = cal.calibrate(pred_old, truth, config="old-substring")
check("OLD substring detector recall < 1.0 (the false-wires MISSED — harness catches the regression)",
      score_old["recall"] < 1.0)
check("the false-WIRE is quantified as false-negatives (the dangerous direction)", score_old["fn"] >= 3)

# ── the per-config comparison table (the experiment output — scannable, not a dict dump) ──────────────
table = cal.format_calibration([score, score_old])
check("format_calibration renders a scannable per-config table",
      "ast-current" in table and "old-substring" in table and "{" not in table)

print(f"\nALL {PASS} CHECKS PASS — the calibration harness: captured-incident fixtures (stable) + a "
      f"config-generic scorer → precision/recall per config. Current logic 1.0/1.0; the OLD substring logic "
      f"recall={score_old['recall']} (the harness CATCHES the false-wire regression). The trust number, "
      f"measured — ready for the N-config LLM/embedding experiment when the engine lands.")
