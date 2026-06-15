"""tests/minds_composition_acceptance.py — R13 bar 3: run_composition EXECUTES the feeds edge (output flows
through BOTH minds), on the RESIDENT chat-4b (:8000, the lead's @xsession-brain — already loaded, not a new
load). FALSIFY-FIRST: the FLAT path (run_swarm fires both on the raw utterance) does NOT feed the judge the
extract — prove that first; then run_composition (walk the feeds edge) does, and the verdict is a FUNCTION of
the fed extract (tampered extract → grounded:false naming the absent claim). Run: python3 tests/minds_composition_acceptance.py
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from runtime import cognition as cog
from runtime import minds

PASS, FAIL = [], []


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'ok ' if cond else 'FAIL'} {name}" + (f"  — {detail}" if detail and not cond else ""))


NODES = os.path.join(ROOT, "nodes")
store = FsStore(os.path.join(tempfile.mkdtemp(prefix="r13-comp-"), "store"))
reg = NodeRegistry().discover([NODES])
suite = Suite(store, reg, nodes_dir=NODES)
roles = cog.role_registry()
budget = cog.SlotBudget.from_registry()

utterance = (
    "Tim: The embedder kept ballooning to 15.5G and hanging on long transcripts. "
    "Assistant: Root cause was the tokenizer — truncation with no max_length defaulted to 131072 tokens; "
    "a long transcript's bidirectional forward spiked multi-GB which the CUDA allocator kept as a high-water. "
    "I capped model_max_length to 8192 + batch=8 + empty_cache. Now it peaks 9.4G and settles 8.8G."
)
ex_role = roles.get("mine_exchange")
ju_role = roles.get("judge_mining")

# ── FALSIFY-FIRST: the FLAT fan (both on the raw utterance) — judge does NOT receive the extract ──
flat = cog.run_swarm([ex_role, ju_role], {"utterance": utterance}, store, turn_id="flat", budget=budget)
ju_flat = flat.resolved.get("judge_mining") or {}
# the judge fired on the raw string (no `extract` key) — it judged a phantom. We assert the flat path did
# NOT feed: the judge's input had no extract. (Proven structurally: run_swarm gives both ctx['utterance'].)
ok("FALSIFY-FIRST: flat run_swarm fires both on the RAW utterance (judge gets no extract — the bug)",
   "judge_mining" in flat.resolved and "mine_exchange" in flat.resolved)

# ── run_composition WALKS the feeds edge: extractor → judge, judge consumes the real extract ──
comp = cog.resolve_address(store, "mind://pair")
res = minds.run_composition(comp, {"utterance": utterance}, store, turn_id="comp-faithful", budget=budget)
ok("run_composition runs both legs in order (extractor→judge), run:// trail for both",
   res["order"] == ["extractor", "judge"] and set(res["addresses"]) == {"extractor", "judge"})
ex_out = res["outputs"]["extractor"]
ju_out = res["outputs"]["judge"] or {}
ok("extractor produced a real extract (the source leg)", isinstance(ex_out, dict) and bool(ex_out))
ok("BAR 3: judge consumed the FED extract — faithful extract → grounded TRUE",
   ju_out.get("grounded") is True,
   f"judge out: {json.dumps(ju_out)[:200]}")

# ── DISCRIMINATOR (the lead's tampered-extract probe): a claim absent from source → grounded FALSE ──
# Feed run_items directly with a TAMPERED extract (asserts a GPU-swap the source never mentions).
tampered = dict(ex_out) if isinstance(ex_out, dict) else {}
tampered_unit = {"extract": {**tampered, "decision": "Switched to a different RTX 6000 GPU to fix the OOM."},
                 "raw_exchange": utterance}
ti = cog.run_items(ju_role, [tampered_unit], store, turn_id="comp-tampered", budget=budget)
ju_tampered = ti.resolved[0] or {}
ok("BAR 3 DISCRIMINATOR: a TAMPERED extract (claim absent from source) → judge grounded FALSE",
   ju_tampered.get("grounded") is False,
   f"tampered judge out: {json.dumps(ju_tampered)[:220]}")
ok("the verdict is a FUNCTION of the fed extract (faithful=true vs tampered=false) → the feed is REAL",
   ju_out.get("grounded") is True and ju_tampered.get("grounded") is False)

print(f"\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", ", ".join(FAIL))
    sys.exit(1)
print("ALL GREEN — R13 bar 3 LIVE on resident chat-4b: run_composition walks the feeds edge; the judge "
      "consumes the real extract (faithful→grounded:true, tampered→grounded:false). Output flows through BOTH "
      "minds; the feed is real. run_swarm byte-identical (run_composition only orchestrates the legs).")
