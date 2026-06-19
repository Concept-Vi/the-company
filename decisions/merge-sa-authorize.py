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
    "meaning": "Give the company its own key to save designs back — or stay read-only?",
    "options": [
        {
            "label": "Give it save-back access",
            "implication": (
                "The company gets its own key to the shared design library — its own, not yours or anyone's — "
                "and can save finished designs back on its own. It only ever writes its own entries, never "
                "touches anyone else's, and you can revoke that key anytime."
            ),
            "recommended": True,
        },
        {
            "label": "Stay read-only for now",
            "implication": (
                "The company keeps reading the shared library to build from it, but can't save anything back "
                "yet. Saving stays a separate, deliberate step until you decide to turn it on."
            ),
        },
    ],
    "scope": "global",
    "explanation_source": "board://item-c0a2d591",
    "legibility": {
        "name": "Turn on save-back to the design library",
        "is": "Reversible · your latest answer wins",
        "why": (
            "The company gets its own key to the shared design library — its own, not yours or anyone's — so "
            "it can save finished and changed designs back on its own. It only ever writes its own entries, "
            "never touches anyone else's, and you can revoke that key anytime. Or stay read-only: it reads the "
            "library to build from, but saving stays a separate, deliberate step. No rush — not choosing "
            "changes nothing: it stays read-only and pending, decide whenever."
        ),
    },
}
