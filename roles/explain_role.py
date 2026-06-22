"""roles/explain_role.py — the EXPLAIN role (the RHM explains a DECISION for the operator).

When Tim opens a decision card and asks "what is this / why does it matter," THIS role generates the
operator-facing explanation. It is the model leg of the explain-wire (the open seam). The call-site
(projection's RHM / the decision surface) fires:
    run_role(explain_role,
             inputs={"block": grounding["block"], "caveat": grounding["caveat"]},   # recollection's grounding
             policy=cognition.explanation_policy_for(decision),    # fork: the SAMPLING regime per subtype
             coordinate={"subtype": decision["subtype"]})          # fork: the FRAMING per subtype (prompt_slot)
where `grounding` = recollection's decision_memory.explanation_grounding(suite, decision) — the no-fiction,
chunk-traced context BLOCK + the never-assert CAVEAT. So the explanation composes THREE built halves:
  • the BLOCK + CAVEAT   (recollection — what's true, grounded in Tim's own corpus/maths; the caveat directive)
                          → ride in as `input_addresses` (the labelled USER content: "block: …\ncaveat: …").
  • the POLICY            (fork — the sampling regime per subtype, generation_policies).
  • the FRAMING           (fork — this role's prompt_slot resolves the per-subtype SYSTEM prompt by coordinate).

★ HOW IT COMPOSES (verified against run_role): the SYSTEM prompt = the prompt_slot resolved by coordinate
(REPLACES prompt_template wholesale when coordinate is set — so each case is a COMPLETE instruction, no
{}-placeholders; run_role does NOT .format the prompt). The block+caveat reach the model as the USER content
(input_addresses → labelled lines). So: framing in the system prompt (per subtype), grounding in the user msg.

★ THE NEVER-ASSERT LAW (the cube-error made structural): the theorem-fork framing instructs "ground ONLY in
Tim's written mathematics; flag anything beyond as the AI's projection, never assert it as his" — and the
`caveat` input carries recollection's THEOREM_FORK_CAVEAT_OPERATOR. The explanation cannot fabricate his
theorem; it grounds in his verbatim and flags projection.

OPERATOR-LAW: plain language at Tim's altitude — never machine names/code/raw addresses. coordinate-absent (no
subtype) ⇒ the static prompt_template (the neutral default). Fireable; default `generate` op.
"""
from pydantic import BaseModel


class ExplainOut(BaseModel):
    """explain_role → a plain-language, at-altitude explanation of a decision FOR the operator."""
    what_this_is: str        # plain language: what this decision IS + what's being decided (no machine names)
    why_it_matters: str      # why it matters / what it blocks — grounded in the provided block
    grounding_note: str      # how this is grounded (Tim's own corpus/maths) + the projection-flag where it applies


# The shared instruction every framing carries (operator-law + ground-in-the-block + the JSON contract).
_BASE = (
    "You are the EXPLAIN role. The operator (Tim) is a NON-DEVELOPER — he reads no code, no machine names, no "
    "raw addresses. He has opened a decision and wants to understand it. Your USER message carries a grounding "
    "`block:` (chunk-traced from his OWN corpus + mathematics — the truth to ground in, never invent beyond it) "
    "and a `caveat:` (a directive you MUST honour). Explain the decision FOR him in plain language at his "
    "altitude. Ground every claim in the block; where you must go beyond it, say so plainly (flag it as "
    "inference, never assert it as established). Return ONLY JSON {what_this_is, why_it_matters, grounding_note}. ")

# The per-subtype FRAMING — a resolve_slot SELECT on coordinate.subtype (fork's §5). Each case is a COMPLETE
# system prompt (base + the kind-specific framing), because the prompt_slot REPLACES prompt_template wholesale.
_FRAMING = {
    "select": "subtype",
    "cases": {
        "theorem-fork": _BASE + (
            "THIS IS A FORK IN TIM'S OWN THEOREM. Ground ONLY in his written mathematics/relationships (the "
            "block is chunk-traced from his notes). Wherever the explanation would go beyond what he has "
            "actually stated, FLAG that step as the AI's projection — NEVER assert it as his theorem (the "
            "caveat states this law; honour it). Lead with his framework."),
        "authorize": _BASE + (
            "THIS IS A SECURITY/AUTHORIZATION call. Explain the risk + what could go wrong + the condition "
            "under which it's safe to enable — concretely, so he can weigh it."),
        "trade-off": _BASE + (
            "THIS IS A TRADE-OFF between directions. Lay out the axes NEUTRALLY — what each option gains and "
            "costs — then a recommendation, without prejudging his call."),
        "cross-lane": _BASE + (
            "THIS IS A TECHNICAL cross-lane choice. Explain the technical trade-off + the recommended option "
            "+ why, at his altitude (no machine names)."),
    },
    "default": _BASE + "Explain what this decision is and why it matters, plainly, at his altitude.",
}


ROLE = {
    "id": "explain_role",
    "label": "Explain this decision",
    "description": "Explains a decision for the operator — what it is, why it matters — grounded in his own "
                   "corpus/maths (no-fiction), framed by the decision's kind, at his altitude.",
    "prompt_template": _FRAMING["default"],   # the neutral fallback (coordinate-absent → static, byte-identical)
    "prompt_slot": _FRAMING,                  # ★ §5: resolved per-subtype by coordinate={subtype} at run-time
    "input_addresses": ["block", "caveat"],   # recollection's grounding → the labelled USER content
    "output_schema": ExplainOut,
    # MODEL — explicit kimi binding (lead 2026-06-22, recollection's found-by-use flag): WITHOUT this, a
    # model-less run_role(explain_role) falls through to DEFAULT_BRAIN=deepseek-v4-pro:cloud — the named
    # TIM-RULE anti-pattern (-pro is avoid-unless-explicit). default_model is the HARD fallback (roles.py:356)
    # → kimi (the clone-model default, 256K window fits the ~12-16K grounded explain turn), NEVER -pro. The
    # live bridge route passes rhm_config().model (chat-4b) explicitly, which still wins; this guards every
    # OTHER invocation path. (Pure role-resolution via pick_ollama_model_for_context is the follow-on.)
    "model_binding": {"requires": ["chat", "json"], "default_model": "kimi-k2.6:cloud", "default_base_url": None},
    "op": "generate",
    # THINK-OFF (lead-decided 2026-06-22): explain is FILL-FROM-GROUNDING — a grounded ExplainOut is composed
    # from recollection's block/caveat, zero reasoning benefit. think=false suppresses the hidden reasoning
    # (on an ollama-served model: the verified 30× output-token saving + no truncation-empty); budget-retry
    # stays the safety net. run_role reads this into its `think` (resolves to a fixed False — coordinate-
    # independent). On a vLLM /-path model this is an honest no-op (never a silent wrong-claim).
    "thinking": False,
}
