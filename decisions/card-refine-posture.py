"""decisions/card-refine-posture.py — authorize: may the assistant REFINE decision cards, propose-then-accept (L5).

The recursive one — a decision ABOUT the decision-surface, decided THROUGH it. Born from the L5 card-update
contract (composition + fork, 2026-06-22): the assistant can refine a card (sharpen wording, adjust options,
improve visuals) but the safe floor is PROPOSE-then-accept — it never changes what Tim decides ON without his
accept, and never touches the structural fields that route a decision to him (content-only whitelist). This
surfaces that posture as Tim's call. authorize subtype → owner=tim. explanation_source → the L5 contract doc
(the genuine origin, single-topic, traced). Worded at Tim's altitude — no "RHM / mark / decision_update".
"""

DECISION = {
    "id": "card-refine-posture",
    "meaning": (
        "Should the assistant be able to refine your decision cards — sharpen the wording, adjust the options, "
        "improve the visuals — by PROPOSING changes you accept, never changing them on its own?"
    ),
    "options": [
        {
            "label": "Let it propose refinements — you accept each",
            "implication": (
                "The assistant can suggest improvements to a card — clearer wording, a missing option, a sharper "
                "visual — and each suggestion waits for your one-tap accept before anything changes; you can undo "
                "any of it. It can only ever touch what you READ on a card, never the parts that route the "
                "decision to you. If a suggestion changes the options of a card you'd already decided, that card "
                "re-opens so you decide again — never a silent change underneath your answer."
            ),
            "recommended": True,
        },
        {
            "label": "Keep cards exactly as written",
            "implication": (
                "The assistant can't change your decision cards; they stay as authored until you or the team "
                "edit them directly. Simplest and entirely under your hand — but it can't help sharpen a card "
                "even when it sees a clearer way."
            ),
        },
    ],
    "scope": "global",
    "subtype": "authorize",
    "explanation_source": "code://build-prep/the-one-application/L5-CARD-UPDATE-CONTRACT.md",  # provenance: the L5 contract this decision is about (single-topic, traced)
    "legibility": {
        "name": "Let the assistant refine your decision cards",
        "is": "Reversible · it proposes, you accept · your latest answer wins",
        "why": (
            "The assistant can often see ways to sharpen a decision card — clearer wording, a missing option, a "
            "better visual. This decides whether it may suggest those refinements (each waiting for your accept "
            "before it changes anything, fully reversible) or whether cards stay exactly as authored. The safe "
            "shape, and the recommended one, is propose-then-accept: it can never change what you're deciding on "
            "without your say, and it can only touch the content you read — never the parts that route a "
            "decision to your queue. If it ever refines the options of a card you'd already settled, that card "
            "comes back to you to decide again, so an answer never sits on top of changed options."
        ),
    },
}
