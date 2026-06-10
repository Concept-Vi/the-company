"""operator_memory/look_at_output_first.py — MIGRATED (B5 batch 3; awaits Tim's confirmation)."""
MEMORY = {
    "id": "look_at_output_first",
    "rule": "When generation or processing fails: DUMP and READ the raw output BEFORE theorizing. 'The content is too big' is the LAST hypothesis, not the first. Zero/clean results from a big input are suspicious — look.",
    "why": "The proven failure: 3 wrong fixes built on a theory vs 1 decoding param visible in the raw output. Failure can correlate with value — mark capture-status loudly.",
    "evidence": [{"quote": "On failure: dump+read the raw output BEFORE theorizing; 'content too big' is the last hypothesis not the first (run-1: 3 wrong fixes vs 1 decoding param).",
                  "source": "standing harness note, 2026-06-05"}],
    "scope": {"when": "any run/generation/processing fails or returns surprisingly little"},
    "status": "proposed",
}
