"""flows/transcript_mine.py — the ③ transcript-miner (G23) as a registered flow row. ONE call mines a
bounded batch of conversation transcripts into the durable history memory: deterministic exchange
extraction → mine_exchange MAP (the resident 4B) → capture+embed into space='history'. Idempotent at
EXCHANGE granularity (the corpus's own exchange://<sid>/<i> keys are the skip-list — capped sessions
deepen across batches); richest-first; active sessions ripen; failures recorded loud. PROPOSES corpus
records only."""
import sys

FLOW = {
    "id": "transcript_mine",
    "label": "Transcript miner (dialogue → durable history memory, bounded batches)",
    "description": (
        "Mines past conversation transcripts into the queryable history space: each Tim-message + "
        "reply pair is distilled into {decision, rationale, tim_correction, my_error, bug_fix, "
        "needs_tim, frustration, pattern_tag} and embedded on write. Incremental by exchange (re-runs "
        "deepen, never duplicate); bounded by time budget; per-file failures recorded loud. Feeds the "
        "pattern_cluster flow."),
    "params": {
        "time_budget_s": {"desc": "wall-clock bound for this batch", "default": 420},
        "max_mb": {"desc": "upper size band in MB (raise to reach the long foundational sessions)",
                   "default": 20},
    },
    "proposes_only": True,
}


def run(time_budget_s: int = 420, max_mb: int = 20) -> dict:
    sys.path.insert(0, "/home/tim/company/build-prep/cognition-self-improvement")
    from g23_mine import run_batch
    return run_batch(int(time_budget_s), max_mb=int(max_mb))
