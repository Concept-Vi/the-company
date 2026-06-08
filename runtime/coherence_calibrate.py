"""coherence_calibrate — the calibration harness (Group D).

Turns a detector's trust from assertion into a measured NUMBER, against a labelled eval set drawn from the
system's own named incidents (SEM-3's "3 of 82" made systematic). Config-GENERIC: the same scorer measures a
structural detector single-config now, and a semantic detector under N model/embedding configs when
cognition's engine lands (the experiment axis Tim named — run an action under N configs, measure per config,
save the winner). Pure + model-free here; the only net-new is the eval set + the score.
"""
from __future__ import annotations

import json
import os


def load_fixtures(path: str) -> list[dict]:
    """Load captured-incident fixtures — controlled inputs with STABLE ground truth (the `fixtures` block).
    Each fixture is a detector-specific input + an `orphan`/positive label. Stable because it tests the
    detector's LOGIC against a fixed captured case, NOT the live tree (which churns as lanes build — that
    churn is the burn-down's domain, not calibration's). This is how SEM-3's named incidents become a
    measured number: the incident is pinned as a fixture, scored forever."""
    return json.load(open(path, encoding="utf-8"))["fixtures"]


def score_reachability(fixtures: list[dict], classify) -> dict:
    """Build {fixture-id: predicted_orphan} by running a consumer `classify(route, fe, tests) -> wired_bool`
    over each fixture's controlled (fe, tests), and the truth {fixture-id: expected_orphan}. Returns
    (predictions, truth) ready for calibrate()."""
    predictions, truth = {}, {}
    for fx in fixtures:
        wired = classify(fx["route"], fx.get("fe", ""), fx.get("tests", ""))
        predictions[fx["id"]] = not wired          # positive class = ORPHAN
        truth[fx["id"]] = bool(fx["orphan"])
    return predictions, truth


def calibrate(predictions: dict, truth: dict, *, config: str = "default") -> dict:
    """Score a detector's predictions against ground truth, for the positive (detected) class. Generic over
    any detector/config. `predictions[item]` = predicted-positive bool; `truth[item]` = actual-positive bool.
      tp = truly-positive AND predicted-positive          (a real finding, caught)
      fn = truly-positive BUT predicted-negative          (a MISS — for orphan-detection this is the
                                                            dangerous false-WIRE: a dead thing read as whole)
      fp = truly-negative BUT predicted-positive          (a false alarm — a real thing called dead)
      tn = truly-negative AND predicted-negative
      precision = tp/(tp+fp)   recall = tp/(tp+fn)   (empty denom → 1.0, vacuously perfect)
    Returns {config, precision, recall, f1, tp, fp, fn, tn, n}."""
    tp = fp = fn = tn = 0
    for item, actual in truth.items():
        pred = bool(predictions.get(item, False))
        if actual and pred:
            tp += 1
        elif actual and not pred:
            fn += 1
        elif (not actual) and pred:
            fp += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return {"config": config, "precision": round(precision, 4), "recall": round(recall, 4),
            "f1": round(f1, 4), "tp": tp, "fp": fp, "fn": fn, "tn": tn, "n": len(truth)}


def format_calibration(scores: list[dict]) -> str:
    """Render per-config scores as a scannable table (the experiment output — the FORM bar; never a dict
    dump). One row per config, so the N-config experiment reads at a glance which config is trustworthy."""
    lines = ["CALIBRATION — precision/recall per config (positive class = the detected finding):",
             f"  {'config':<18} {'prec':>6} {'recall':>7} {'f1':>6}   {'tp':>3} {'fp':>3} {'fn':>3} {'tn':>3}  (n)"]
    for s in scores:
        lines.append(f"  {s['config']:<18} {s['precision']:>6} {s['recall']:>7} {s['f1']:>6}   "
                     f"{s['tp']:>3} {s['fp']:>3} {s['fn']:>3} {s['tn']:>3}  ({s['n']})")
    return "\n".join(lines)
