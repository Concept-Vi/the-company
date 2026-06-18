"""decisions/merge-sa-authorize.py — BOOTSTRAP decision (the decision-surface's first real instance).

The lead's smallest-path verify row for the decision:// resolver. A REAL pending decision: whether to give
the Company its own private write-credentials to the shared visual design library (the vi-vision service-account
write path), so finished designs can be saved back automatically — or keep it read-only for now. Worded at the
OPERATOR's altitude (no machine names — "the design library", "save-back", never "vi-vision SA / RLS").

Resolved as decision://global/merge-sa-authorize. id MUST equal the file stem (merge-sa-authorize). STATE is
NOT here — it resolves from the LATEST `decision_take` mark on the canonical address (pending until the operator
chooses). explanation_source points the RHM at the Face-Pipeline board item (why save-back matters: the
pipeline's REGISTER step writes finished designs back into the library).
"""

DECISION = {
    "id": "merge-sa-authorize",
    "meaning": (
        "Should the Company get its own private way to save designs back into the shared design library — "
        "so finished and changed designs are written back automatically — or stay read-only for now, where it "
        "can use the library but can't save anything into it yet?"
    ),
    "options": [
        {
            "label": "Give it save-back access",
            "implication": (
                "The Company gets its own private sign-in to the design library and can save designs back on "
                "its own. It only ever touches its own entries — never anyone else's — and you can switch the "
                "sign-in off again at any time."
            ),
            "recommended": True,
        },
        {
            "label": "Stay read-only for now",
            "implication": (
                "The Company keeps reading the shared library to build from it, but can't save anything back "
                "yet. Saving stays a separate, deliberate step until you decide to turn it on."
            ),
        },
    ],
    "scope": "global",
    "explanation_source": "board://item-c0a2d591",
    "legibility": {
        "name": "Turn on save-back to the design library",
        "is": "a decision to make",
        "why": (
            "It decides whether the Company can write finished designs back into the shared library on its own, "
            "or stays read-only until you say otherwise."
        ),
    },
}
