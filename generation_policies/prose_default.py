"""generation_policies/prose_default.py — SEED generation-policy: the free-prose regime.

A second regime to EXERCISE the registry's per-content variation (a regime is DATA, selectable per
content — not one global constant). Free prose (a reduce/consult summary) is NOT grammar-constrained,
so it is far less loop-prone: a single-rung ladder `[1.1]` (a fixed light penalty, no escalation step),
no diff-against-source (prose is not enumerative), no json_schema, a small warmth (temp 0.3). Proves the
ladder need not be multi-rung and the flags vary per regime. See runtime/generation_policies.py +
generation_policies/AGENTS.md. Its `id` MUST equal the file stem (`prose_default`).
"""

GENERATION_POLICY = {
    "id": "prose_default",
    "rep_penalty_ladder": [1.1],        # single rung — free prose is not the grammar-constrained loop surface
    "diff_against_source": False,       # prose is not enumerative — the diff guard does not apply
    "json_schema": False,
    "temperature": 0.3,
    "desc": "the free-prose regime (reduce/consult): a fixed light rep_penalty, no enumeration diff",
}
