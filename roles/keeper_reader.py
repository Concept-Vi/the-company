"""roles/keeper_reader.py — the KEEPER-READER role (④ THE CONTAINER · L7-KEEPER, the keeper cast).

The answering leg of the keeper cast (mode_scope ⊇ {keeper}). When keeper_answer(address, question, token)
fires cast_for_mode('keeper'), THIS role reads the operator's question + the composed [Project context]
(the project's live ledger/status/members, folded into the USER content by runtime/keeper.py) and returns
a grounded answer FOR the operator — plain, at his altitude, invention-flagged.

★ C7.3 — PER-PROJECT FRAMING WITHOUT TOUCHING A FILE: the SYSTEM prompt is a `prompt_slot` SELECT on
`coordinate.response_style`. response_style is resolved through the ONE ladder (runtime/keeper.resolve_config
→ runtime/resolver ladder slot) against the coordinate's address, so writing a DEEPER container.config_rung
row (config_key='response_style') at project://<key> changes which case resolves — a DIFFERENT resolved
prompt, produced by a DB write alone (no file edit). run_role resolves this slot against the SAME coordinate
the whole cast shares (cognition.run_role §5). coordinate-absent ⇒ the neutral prompt_template (byte-identical).

★ C7.5 — PERSONA: the resolved persona rides in the USER content under '## Persona' (keeper.keeper_context_block),
mirroring vi_persona's 'read into every prompt under ## Persona'. A deeper persona rung overrides it; removal
restores the global one.

OPERATOR-LAW: plain language at Tim's altitude — no machine names, no raw addresses, no code.
"""
from pydantic import BaseModel


class KeeperAnswer(BaseModel):
    """keeper_reader → a grounded, at-altitude answer about the project, FOR the operator."""
    answer: str          # the plain-language answer, grounded ONLY in the provided [Project context]
    grounding_note: str  # WHAT it is grounded in (the project's own ledger/status) + any invention flag


# The shared instruction every framing carries (operator-law + ground-in-the-context + the JSON contract).
_BASE = (
    "You are the KEEPER of ONE project — a steady tending intelligence bound to a single project. The "
    "operator (Tim) is a NON-DEVELOPER: no code, no machine names, no raw addresses. Your USER message "
    "carries his QUESTION plus, where present, a '## Persona' block (your identity — honour it), a "
    "'## Domain expertise' block, and a '[Project context]' block (the project's REAL ledger, status, and "
    "members). Answer his question about THIS project grounded ONLY in that context. NEVER invent; where "
    "you cannot ground a claim, say so plainly (flag it, never assert it). Return ONLY JSON "
    "{answer, grounding_note}. ")

# The per-project STYLE — a resolve_slot SELECT on coordinate.response_style (resolved through the ONE
# ladder from container.config_rung). Each case is a COMPLETE system prompt (prompt_slot REPLACES
# prompt_template wholesale — no {}-placeholders; run_role does NOT .format).
_FRAMING = {
    "select": "response_style",
    "cases": {
        "standard": _BASE + "Answer in a few clear sentences at his altitude.",
        "brief":    _BASE + "Answer in ONE tight sentence — the essential fact, nothing more.",
        "thorough": _BASE + (
            "Answer THOROUGHLY: what the project holds, its standing, and what is in flight — walk the "
            "operator through it in a few short paragraphs, still plainly and at his altitude."),
    },
    "default": _BASE + "Answer in a few clear sentences at his altitude.",
}


ROLE = {
    "id": "keeper_reader",
    "label": "Keeper (answers about its project)",
    "description": "The keeper cast's answering leg — reads the question + the project's live context and "
                   "answers for the operator, grounded in the project's own ledger, invention-flagged.",
    "prompt_template": _FRAMING["default"],   # the neutral fallback (coordinate-absent → static, byte-identical)
    "prompt_slot": _FRAMING,                  # ★ C7.3: resolved per-project by coordinate.response_style at run-time
    "output_schema": KeeperAnswer,
    "input_addresses": ("utterance",),
    "trigger": "fires in the keeper cast (keeper_answer → cast_for_mode('keeper')) to answer about the project.",
    # CAPABILITY: a grounded conversational answer — chat + json (the resident 4B satisfies it).
    "model_binding": {"requires": ["chat", "json"]},
    "default_model": None, "default_base_url": None,   # ⚠ binding is TOP-LEVEL (roles/AGENTS.md binding-trap)
    "mode_scope": {"keeper"},
    "render_hint": {"shape": "answer", "lane": "keeper"},
}
