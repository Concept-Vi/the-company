#!/usr/bin/env python3
"""rg10_run.py — RG10 at FULL SCALE: an incremental batch wrapper around the PROVEN
registry_generation_run.run_registry_generation (reuse-don't-parallel — that module already supplies
the three manual seams: resolve-once shared exemplars/inventory ctx · the bare-name `ground` role
variant (the {mockup} chaining's manual form) · the run_jury+refcheck two-layer CONFIRM. Proven by
use on C1-inbox-desktop: 43 candidates → 43 dossiers → 28 clusters → 14 confirmed / 14 flagged).

Per mockup: the full RG3–RG6 chain (GROUND → MAP → REDUCE cluster-dedup → CONFIRM) → the per-mockup
artifact build-prep/cognition-self-improvement/rg10-batch-<stem>.json (the SAME artifact __main__
writes — one canonical shape). State (.build/rg10/state.json) tracks done/failed per mockup —
resume-safe; bounded batches compose to all 23 mockups / 940 candidates.

FAIL-LOUD (the lesson from this file's first draft, which read only .resolved and silently swallowed
940 .failed units): a mockup whose chain raises OR yields 0 dossiers from >0 candidates is recorded
in state["failed"] with the reason — NEVER marked done. A failed mockup is retried on later batches
(transient model errors heal) up to MAX_ATTEMPTS, then left loud in state for the surface step.

THE FLOOR: this run PROPOSES — the artifacts surface for Tim's APPROVE; nothing writes
addresses.json or the mockups (RG9's write-back runs only after the operator approves).
"""
import json
import os
import sys
import time

os.chdir("/home/tim/company")
sys.path.insert(0, "/home/tim/company")
sys.path.insert(0, "/home/tim/company/build-prep/cognition-self-improvement")
STATE_DIR = ".build/rg10"
STATE = os.path.join(STATE_DIR, "state.json")
ART_DIR = "build-prep/cognition-self-improvement"
MAX_ATTEMPTS = 2          # the blocked-twice discipline: retried once, then left loud for the surface


def _load(path, default):
    try:
        return json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _save(state):
    json.dump(state, open(STATE, "w"), indent=1)


def _adopt_existing(state, mockups):
    """A mockup whose batch artifact ALREADY exists (e.g. C1's proven first run) is adopted as done —
    incomplete/stranded work is in-scope, never re-burned."""
    for m in mockups:
        if m in state["done"]:
            continue
        fp = os.path.join(ART_DIR, f"rg10-batch-{m.replace('.html', '')}.json")
        if os.path.exists(fp):
            d = _load(fp, None)
            if d and d.get("n_dossiers"):
                state["done"][m] = {"candidates": d["n_candidates"], "dossiers": d["n_dossiers"],
                                    "clusters": d["n_clusters"], "confirmed": len(d["confirmed"]),
                                    "flagged": len(d["flagged"]), "adopted": True}


def run_batch(time_budget_s: int = 420) -> dict:
    from registry_generation_run import _load_suite, run_registry_generation

    os.makedirs(STATE_DIR, exist_ok=True)
    state = _load(STATE, {"done": {}, "failed": {}})
    state.setdefault("done", {}); state.setdefault("failed", {})
    cands = _load("design/_system/candidates.json", {}).get("candidates", [])
    mockups = sorted({c["mockup_file"] for c in cands})
    _adopt_existing(state, mockups)
    _save(state)

    suite = _load_suite()
    t0, ran = time.time(), []
    for m in mockups:
        if m in state["done"]:
            continue
        if state["failed"].get(m, {}).get("attempts", 0) >= MAX_ATTEMPTS:
            continue                                       # left LOUD in state — surfaced, not silently retried forever
        if time.time() - t0 > time_budget_s:
            break
        stem = m.replace(".html", "")
        try:
            out = run_registry_generation(suite, mockup=m, turn=f"rg10-{stem}", verbose=True)
        except Exception as e:
            prior = state["failed"].get(m, {"attempts": 0})
            state["failed"][m] = {"attempts": prior["attempts"] + 1, "error": f"{type(e).__name__}: {e}"[:300]}
            _save(state)
            continue
        if out["n_dossiers"] == 0 and out["n_candidates"] > 0:
            prior = state["failed"].get(m, {"attempts": 0})
            state["failed"][m] = {"attempts": prior["attempts"] + 1,
                                  "error": f"0/{out['n_candidates']} dossiers — every MAP unit failed; NOT done"}
            _save(state)
            continue
        fp = os.path.join(ART_DIR, f"rg10-batch-{stem}.json")
        json.dump({"mockup": out["mockup"], "ground": out["ground"], "n_candidates": out["n_candidates"],
                   "n_dossiers": out["n_dossiers"], "n_clusters": out["n_clusters"],
                   "confirmed": out["confirmed"], "flagged": out["flagged"]},
                  open(fp, "w"), indent=2)
        state["done"][m] = {"candidates": out["n_candidates"], "dossiers": out["n_dossiers"],
                            "clusters": out["n_clusters"], "confirmed": len(out["confirmed"]),
                            "flagged": len(out["flagged"])}
        state["failed"].pop(m, None)
        _save(state)
        ran.append(m)
    return {"ran_this_batch": ran,
            "mockups_done": len(state["done"]), "mockups_total": len(mockups),
            "failed": state["failed"],
            "confirmed_total": sum(v["confirmed"] for v in state["done"].values()),
            "flagged_total": sum(v["flagged"] for v in state["done"].values())}


if __name__ == "__main__":
    print(json.dumps(run_batch(int(sys.argv[1]) if len(sys.argv) > 1 else 420), indent=1, default=str))
