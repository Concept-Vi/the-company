"""tests/l5_reground_acceptance.py — L5 updates RE-GROUND the explanation (recollection's contract).

L5 lets the RHM propose + the operator accept `decision_update` marks; compose_definition folds the
ACCEPTED updates onto the decision row → the effective DEFINITION (registry-is-truth; the row never
mutates). The explain-wire's recollection half — explanation_grounding — must then ground the UPDATED
card, not the stale declared row. The route owner (projection/fork) resolves the dict via
compose_definition BEFORE the explain re-ground; THIS proves explanation_grounding HONOURS whatever
resolved dict it is handed (the contract fork's one route-line depends on).

DEFAULT-TO-WRONG: every check fails LOUD if explanation_grounding ignored the resolved dict (e.g.
re-fetched the raw row by id) — a sentinel that does NOT reach the updated block falsifies the claim.

Headless-safe + fast: normal-subtype checks run at rerank=False (no recall/determine network); the
theorem-fork cache is SEEDED for both meanings so we prove the KEY discriminates by the updated text
WITHOUT the ~13s determine. Reads the live registry rows (registry-is-truth) — picks rows by subtype
so a rename/removal degrades to a skip, never a false pass.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from runtime.cognition import decision_registry as _dreg
from runtime.decision_registry import compose_definition
from runtime import decision_memory as dm

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def _meaning(row):
    return (row.get("meaning") or row.get("text") or row.get("decision") or row.get("question") or "").strip()


suite = Suite(FsStore(os.path.join(ROOT, ".data/store")), NodeRegistry().discover([NODES]), nodes_dir=NODES)
reg = _dreg()
rows = {did: reg.get(did) for did in reg if isinstance(reg.get(did), dict)}

# pick live rows by subtype — registry-is-truth, robust to renames
norm_id = next((d for d, r in rows.items() if r.get("subtype") != "theorem-fork" and _meaning(r)), None)
thm_id = next((d for d, r in rows.items() if r.get("subtype") == "theorem-fork" and _meaning(r)), None)
assert norm_id, "no non-theorem decision in the live registry to test against"

# ── CASE 1: normal subtype — meaning + options + legibility updates re-ground ───────
print(f"\nCASE 1  {norm_id} ({rows[norm_id].get('subtype')}): meaning/options/legibility re-ground")
row = rows[norm_id]
block_raw = dm.explanation_grounding(suite, row, rerank=False)["block"]

S_MEAN, S_OPT = "ZZ_SENTINEL_UPDATED_MEANING_q9", "ZZ_SENTINEL_UPDATED_OPTION_q9"
S_IS, S_WHY = "ZZ_SENTINEL_WHAT_IT_IS_q9", "ZZ_SENTINEL_WHY_IT_MATTERS_q9"
marks = [
    {"mark_type": "decision_update", "ts": "T1", "value": {"field": "meaning", "value": S_MEAN}},
    {"mark_type": "decision_update", "ts": "T2", "value": {"field": "options",
        "value": [{"label": S_OPT, "implication": "the updated option's implication"}]}},
    {"mark_type": "decision_update", "ts": "T3", "value": {"field": "legibility",
        "value": {"is": S_IS, "why": S_WHY}}},
    {"mark_type": "decision_update_accept", "value": "T1"},
    {"mark_type": "decision_update_accept", "value": "T2"},
    {"mark_type": "decision_update_accept", "value": "T3"},
]
updated_def, _reopened = compose_definition(row, marks)
block_upd = dm.explanation_grounding(suite, updated_def, rerank=False)["block"]

check("updated meaning reaches the updated block", S_MEAN in block_upd)
check("updated meaning ABSENT from the raw block (proves no raw re-fetch)", S_MEAN not in block_raw)
check("updated option reaches the updated block", S_OPT in block_upd)
check("updated WHAT-IT-IS reaches the updated block", S_IS in block_upd)
check("updated WHY-IT-MATTERS reaches the updated block", S_WHY in block_upd)

# ── CASE 2: theorem-fork — the framework cache RE-KEYS on the updated meaning ───────
if thm_id:
    print(f"\nCASE 2  {thm_id} (theorem-fork): the framework cache re-keys on the updated meaning")
    trow = rows[thm_id]
    try:
        suite.store._vector_records(); ver = suite.store._vec_version
    except Exception:
        ver = -1
    old_text = _meaning(trow)
    new_text = "ZZ_SENTINEL_THEOREM_NEW_MEANING about a wholly different framework axis q9"
    C_OLD, C_NEW = "ZZ_SENTINEL_OLD_THEOREM_CLAIM_q9", "ZZ_SENTINEL_NEW_THEOREM_CLAIM_q9"
    k_old, k_new = (old_text, ver), (new_text, ver)
    had_old = k_old in dm._THEOREM_CLAIMS_CACHE              # restore-after: don't pollute a live cache
    prev_old = dm._THEOREM_CLAIMS_CACHE.get(k_old)
    try:
        dm._THEOREM_CLAIMS_CACHE[k_old] = [{"claim": C_OLD, "chunk_id": "x", "theme": "t"}]
        dm._THEOREM_CLAIMS_CACHE[k_new] = [{"claim": C_NEW, "chunk_id": "y", "theme": "t"}]
        tblock_raw = dm.explanation_grounding(suite, trow, rerank=False)["block"]
        tmarks = [
            {"mark_type": "decision_update", "ts": "U1", "value": {"field": "meaning", "value": new_text}},
            {"mark_type": "decision_update_accept", "value": "U1"},
        ]
        tupdated, _ = compose_definition(trow, tmarks)
        tblock_upd = dm.explanation_grounding(suite, tupdated, rerank=False)["block"]
        check("raw theorem block uses the OLD-meaning cache key", C_OLD in tblock_raw)
        check("updated theorem block uses the NEW-meaning cache key", C_NEW in tblock_upd)
        check("old theorem claim ABSENT from the updated block (proves re-key)", C_OLD not in tblock_upd)
    finally:
        dm._THEOREM_CLAIMS_CACHE.pop(k_new, None)
        if had_old:
            dm._THEOREM_CLAIMS_CACHE[k_old] = prev_old
        else:
            dm._THEOREM_CLAIMS_CACHE.pop(k_old, None)
else:
    print("\nCASE 2  skipped — no theorem-fork decision in the live registry")

print(f"\nALL {PASS} CHECKS PASS — L5-accepted updates re-ground the explanation "
      "(explanation_grounding honours the compose_definition-resolved dict; the theorem cache re-keys).")
