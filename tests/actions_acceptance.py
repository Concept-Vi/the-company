"""tests/actions_acceptance.py — E: chains/graphs as configurable saveable ACTIONS (the saving side).

A saved chain/graph promoted to a declared, named, LLM-configurable, fireable ACTION. Coherence owns
DECLARE + VALIDATE + SAVE + REGISTER (this) + the calibration that proves a config (D); the RUNNER is
cognition's engine + the existing run_graph (E3 — not built here). Proven by use:
  · build_action validates a declaration through ONE door (mirrors _build_role) — registry-is-truth: a
    step's model must be a REGISTRY ref, not a hardcoded literal (the no-hardcoding law, enforced);
  · the action registry saves/loads declared rows (registry-is-truth; persistence-survives-reload);
  · an action carries its CALIBRATED config (D4 — experiment→calibrate→SAVE the winning config);
  · build_coherence_info projects the coherence model (the read-face sibling of build_cognition_info;
    reflects-never-owns — a projection, no writes).
E5 (compose + RUN across models AND embeddings, swappable) is the end-state — gated on cognition's engine;
here we build + validate + save the declaration, the run is the convergence-round seam.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime import coherence_actions as act
from runtime import coherence_detect as cd

PASS = 0
def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")

MODELS = {"qwen3.5-4b", "bge-m3"}   # the available registry models (chat + embed) — registry-is-truth

# ── E1 · build_action validates through one door; registry-is-truth enforced ─────────────────────────
good = {"name": "doc-staleness-scan",
        "steps": [{"op": "generate", "model": "qwen3.5-4b", "inputs": ["code://doc"]},
                  {"op": "embed", "model": "bge-m3", "inputs": ["code://doc"]}],
        "output_schema": {"contradicts": "bool", "note": "str"}}
a = act.build_action(good, models=MODELS)
check("build_action accepts a valid declaration (registry-model steps)", a["ok"] and a["action"]["name"] == "doc-staleness-scan")

bad_model = {"name": "x", "steps": [{"op": "generate", "model": "gpt-4-hardcoded", "inputs": ["code://d"]}]}
r_bad = act.build_action(bad_model, models=MODELS)
check("build_action REJECTS a step naming a non-registry model (the hardcoding violation, fail-loud)",
      not r_bad["ok"] and "registry" in r_bad["error"].lower())

r_empty = act.build_action({"name": "x", "steps": []}, models=MODELS)
check("build_action REJECTS a declaration with no steps (fail-loud)", not r_empty["ok"])

# ── E2 · the action registry — save/get/list, persistence-survives-reload (registry-is-truth) ───────
regpath = os.path.join(tempfile.mkdtemp(prefix="actions-"), "actions.json")
reg = act.ActionRegistry(regpath)
reg.save(a["action"])
check("the action registry saves + gets the action back", reg.get("doc-staleness-scan")["name"] == "doc-staleness-scan")
check("list includes it", "doc-staleness-scan" in [x["name"] for x in reg.all()])
reg2 = act.ActionRegistry(regpath)   # reload
check("persistence survives reload (registry-is-truth, one declared source)", reg2.get("doc-staleness-scan") is not None)

# ── D4 · the action carries its CALIBRATED config (experiment → calibrate → SAVE the winner) ─────────
reg.save_calibration("doc-staleness-scan", {"config": "qwen3.5-4b", "precision": 0.91, "recall": 0.88})
got = reg.get("doc-staleness-scan")
check("an action carries its saved calibration (the winning config — D4)",
      got.get("calibration", {}).get("config") == "qwen3.5-4b" and got["calibration"]["precision"] == 0.91)

# ── E4 · build_coherence_info projects the model (read-face sibling; reflects-never-owns) ────────────
root = os.path.join(tempfile.mkdtemp(prefix="cinfo-"), "store")
store = FsStore(root)
cd.record_structural_findings(store, ROOT)
info = act.build_coherence_info(store)
check("build_coherence_info projects burn_down + finding_kinds + dispositions (the read-face)",
      "burn_down" in info and "finding_kinds" in info and "dispositions" in info)
check("finding_kinds is DERIVED from real findings (not a hardcoded list)", "unwired-route" in info["finding_kinds"])
check("dispositions exposes the vocabulary (so a surface reads it from here — registry-is-truth)",
      "by-design" in info["dispositions"] and "to_wire" in info["dispositions"])
# reflects-never-owns: projecting does not write
before = len(store.all_findings())
act.build_coherence_info(store)
check("build_coherence_info is reflects-never-owns (a projection — no writes)", len(store.all_findings()) == before)

print(f"\nALL {PASS} CHECKS PASS — chains-as-actions (the saving side): build_action validates through one "
      f"door (registry-is-truth enforced), the action registry saves/loads declared rows + the calibrated "
      f"config (D4), build_coherence_info projects the model (reflects-never-owns). The runner is cognition's; "
      f"E5 compose-run-across-models+embeddings is the convergence-round seam.")
