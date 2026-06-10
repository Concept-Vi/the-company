"""operator_memory/flag_hardcoding.py — MIGRATED from the harness notes (B5 batch 1; awaits Tim's
confirmation)."""
MEMORY = {
    "id": "flag_hardcoding",
    "rule": "Always FLAG hardcoding when found (a literal list/dict/value where a registry belongs) — it must be replaced with registry architecture, never patched or extended in place.",
    "why": "Hardcoding is the root drift failure across AI sessions: a literal in one session is invisible to the next; registry-is-truth is the standing Company law.",
    "evidence": [{"quote": "registry is the source of truth, never fabricate — Tim called out run_role hardcoding ctx['utterance'] and the _ORPHAN_ROUTES dict: 'right shape, wrong form: promote to the registry'",
                  "source": "Tim, 2026-06-08 (the coherence rounds)"}],
    "scope": {"when": "reading or writing any code"},
    "status": "proposed",
}
