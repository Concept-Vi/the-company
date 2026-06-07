"""roles/judge.py — ROLE #0: the finished-thought judge (Concurrent Cognition G2 · C2.2).

The judge is the FIRST role (role #0) — it pre-dates the cognition build (it is the voice circuit's
finished-thought endpoint, `Suite.is_finished_thought`). G2 moves its declaration OUT of suite.py's
hardcoded one-entry `ROLE_REGISTRY` class constant INTO this file-discovered role — UNCHANGED IN
BEHAVIOUR (C2.2). `suite.py:resolve_role`/`roles()` read the SAME dict, only from the discovered
registry instead of a class constant, so `resolve_role('judge')` returns a BYTE-IDENTICAL effective
binding before/after this move.

FACET: config-only. The judge declares NO `prompt_template`, NO `mode_scope`, NO `draws` → it does NOT
fire via the swarm, it is in NO listening cast, and it is not a jury. It is a CONFIG slot, triggered by
the voice circuit (POST /api/voice/finished-thought) and run by `is_finished_thought`. It is NOT forced
to fake a prompt — the absence of those fields IS its (correct) facet.

The dict below is the verbatim copy of the prior suite.py `ROLE_REGISTRY["judge"]` (so the move is
byte-identical), PLUS two ADDITIVE G2 fields (schema-additive, rule 2): `model_binding` (the C2.5
capability-query shape — its `requires` declares what a judge model must provide; `default_model` None
keeps the safe floor = the brain) and `render_hint` (G7 data). These additive keys are not read by
`resolve_role`, so the effective resolution is unchanged.
"""

ROLE = {
    "id": "judge",
    "label": "Finished-thought judge",
    "description": "Decides whether a spoken utterance is a COMPLETE thought (fire the turn) or "
                   "mid-ramble (keep listening) — the voice circuit's semantic endpoint.",
    "trigger": "voice circuit: a VAD pause during always-listen (POST /api/voice/finished-thought)",
    "default_model": None,            # None → falls to the RHM brain (rhm_config.model) — always
                                      # available. The hard default stays safe; the data-driven
                                      # PREFERENCE is `recommended_*` below (binding it live needs
                                      # the 4B resident → the resource manager owns that).
    "default_base_url": None,         # None → the brain's base_url
    "recommended_model": "cyankiwi/Qwen3.5-4B-AWQ-4bit",      # MEASURED day-one pick (Tim 2026-06-05)
    "recommended_base_url": "http://localhost:8000/v1",
    "recommended_reason": ("local 4B no-think judged FINISHED in 463ms / a fragment in 49ms vs "
                           "deepseek-cloud 2113–6500ms (measured) — a reasoning cloud model is the "
                           "wrong tool on the always-listen hot path. Bind when the 4B is resident."),
    "thinking": False,                # WANTS a fast non-reasoning model (a reasoner stalls the hot path)
    "output": "one word: FINISHED | MORE",
    "tools": [],                      # no tools — a pure classifier
    "context": "the utterance text only (no system grounding)",
    # max_tokens 2048: the DEFAULT judge falls to the RHM brain, which today is a THINKING model
    # (qwen3.5) — at 256 it gets cut off mid-reasoning and emits EMPTY content (FabricError). 2048
    # lets it finish thinking + emit the FINISHED|MORE word (verified). A no-think model (the
    # recommended 4B) uses <50 tokens, so this ceiling never hurts it — it only unblocks the
    # thinking default. (Snappy always-listen still WANTS the no-think 4B bound — see recommended_*.)
    "knobs": {"max_tokens": 2048, "temperature": 0},
    "env_model": "COMPANY_JUDGE_MODEL", "env_url": "COMPANY_JUDGE_URL",
    "env_knobs": {"max_tokens": "COMPANY_JUDGE_MAX_TOKENS"},

    # --- ADDITIVE G2 fields (schema-additive; NOT read by resolve_role → effective binding unchanged) ---
    # C2.5: the capability-QUERY shape. A judge model must `provide` fast no-think classification on the
    # always-listen hot path. `requires` is the QUERY (role.requires ⊆ model.provides), not prose; the
    # None default_model keeps the always-available floor (the brain) when no live provider matches.
    # SINGLE-SOURCE NOTE (for the next agent): `model_binding` is the CANONICAL G2 binding shape (the
    # capability query). The FLAT top-level fields above (default_model/recommended_model/env_*) are the
    # LEGACY inputs `suite.py:resolve_role` reads directly (preserved for byte-identical C2.2). They
    # mirror values inside model_binding; when G8 lands, resolve_role should migrate to read model_binding
    # so the two copies can't drift — flagged, not refactored now (it would change resolve_role behaviour).
    "model_binding": {
        "requires": ["chat", "fast", "no-think"],
        "default_model": None, "default_base_url": None,
        "recommended_model": "cyankiwi/Qwen3.5-4B-AWQ-4bit",
        "env_model": "COMPANY_JUDGE_MODEL", "env_url": "COMPANY_JUDGE_URL",
    },
    "render_hint": {"shape": "verdict", "lane": "voice-circuit"},  # G7 data (the live view is G7)
}
