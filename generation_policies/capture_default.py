"""generation_policies/capture_default.py — SEED generation-policy: the capture regime (O2).

THE entry that proves "NOTHING static": the repetition_penalty regime as DATA. The capture pass
(grammar-constrained long arrays, greedy temp0) is the surface that hits the degenerate-loop
pathology (~20% of real files). So this regime declares the LADDER as data — `1.1` default → `1.2`
on `finish=length` → (ladder exhausted) fail-loud `degenerate-loop`. `diff_against_source: True` —
the Tim-decision lean: rep_penalty can silently under-capture LEGITIMATE enumeration, so diff the
output against the source on enumerative content, NEVER a silent penalty. `json_schema: True`
(structured-outputs, not json_object), greedy temp 0.0. See runtime/generation_policies.py +
generation_policies/AGENTS.md. Its `id` MUST equal the file stem (`capture_default`).
"""

GENERATION_POLICY = {
    "id": "capture_default",
    "rep_penalty_ladder": [1.1, 1.2],   # default → escalate-on-length → exhausted = fail-loud degenerate-loop
    "diff_against_source": True,        # never a silent penalty on legitimate enumeration (Tim-decision lean)
    "json_schema": True,                # structured-outputs (NOT json_object) for the capture path
    "temperature": 0.0,                 # greedy — the loop-trigger surface this ladder cures
    "desc": "the corpus-capture regime: rep_penalty ladder 1.1→1.2→fail-loud, diff-against-source on enumeration",
}
