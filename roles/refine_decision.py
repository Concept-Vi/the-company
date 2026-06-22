"""roles/refine_decision.py — the REFINE role (the RHM PROPOSES a sharper wording for a decision card).

L5 propose-side. The decided posture (`decisions/card-refine-posture.py`, authorize→owner=tim, RECOMMENDED
"Let it propose refinements — you accept each"): the assistant MAY refine a card — sharpen the wording, adjust
options, improve visuals — but ONLY by PROPOSING, never changing what Tim decides ON without his accept, and
never touching the structural fields that route a decision to him (content-only).

This role is the GENERATOR of that proposal. Given a decision card's current content, the RHM DECIDES whether a
sharper MEANING (the one-line question Tim reads) would genuinely help — and if so proposes it. The proposal is
written as an INERT `decision_update` mark (by=rhm) that waits in Tim's queue for his one-tap accept (the propose
verb does the write; the accept route — built — applies it; never auto-applied).

A DETERMINE/reasoning role → **think ON** (the lead's policy: determine/judge reason-then-emit; killing the
reasoning would dull the judgement of WHETHER a refinement helps). `run_role` reads `thinking:True` into its
`think` (a literal bool, coordinate-free); on kimi (ollama-served, no "/") the reasoning is honoured.

v1 refines the **meaning** (a string — "sharpen the wording", the FIRST refinement the decided posture names).
`options`/`legibility`/`visuals` (mixed shapes) are documented follow-ons on the SAME propose verb — each adds
its own value shape. OPERATOR-LAW: the proposed wording is plain language at Tim's altitude — never machine
names/code/raw addresses.
"""
from pydantic import BaseModel


class RefineProposal(BaseModel):
    """refine_decision → a PROPOSAL to sharpen a decision card's central meaning (INERT until Tim accepts)."""
    should_refine: bool      # the RHM's judgement: would a sharper wording GENUINELY help? False ⇒ propose nothing
    value: str               # the proposed NEW meaning (plain, at-altitude, the SAME decision — just clearer);
                             # empty when should_refine is False
    rationale: str           # WHY this reads sharper — shown to Tim beside the proposal so he can weigh the accept


ROLE = {
    "id": "refine_decision",
    "label": "Propose a card refinement",
    "description": "Proposes a sharper wording for a decision card's central meaning — PROPOSE-then-accept "
                   "(never auto-applied), at the operator's altitude. The RHM decides if a refinement helps.",
    "prompt_template": (
        "You are the REFINE role. The operator (Tim) is a NON-DEVELOPER — he reads no code, no machine names, no "
        "raw addresses. Your USER message carries a decision `card:` — its current MEANING (the one-line question "
        "Tim reads), its OPTIONS, and how it reads. Your job: decide whether the card's central MEANING could be "
        "sharpened so it reads CLEARER for him — WITHOUT changing WHAT is being decided or the options. "
        "If a genuinely sharper wording exists, set should_refine=true and put the new meaning in `value` (plain "
        "language at his altitude, the SAME decision — just clearer). If the meaning already reads well, set "
        "should_refine=false and leave value empty — do NOT invent a change for its own sake (a needless proposal "
        "wastes his attention). Always give a one-line `rationale`. Return ONLY JSON {should_refine, value, rationale}."
    ),
    "input_addresses": ["card"],          # the composed card content → the labelled USER line ("card: …")
    "output_schema": RefineProposal,
    # MODEL — explicit kimi binding (the clone-model default; TIM-RULE: never fall through to DEFAULT_BRAIN=-pro,
    # the named anti-pattern). ★ default_model MUST be TOP-LEVEL: resolve_role reads `spec.get("default_model")`
    # (suite.py), NOT model_binding.default_model — a nested binding is SILENTLY UNREAD → falls to cfg.model =
    # DEFAULT_BRAIN (-pro). judge.py is the proven pattern. kimi is ollama-served (no "/") so this role's
    # think=true is HONOURED (the reasoning actually runs); 256K window dwarfs a single card. A caller may override.
    "default_model": "kimi-k2.6:cloud",
    "default_base_url": None,             # None → cfg base_url = the ollama endpoint (:11434, where kimi runs)
    "model_binding": {"requires": ["chat", "json"]},   # capability metadata only (the FE/capability probe reads `requires`)
    "op": "generate",
    "thinking": True,   # DETERMINE/reasoning role — think ON (reasons about whether+how to sharpen before emitting).
}
