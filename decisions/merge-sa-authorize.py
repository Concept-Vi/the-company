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
        "The company can read the shared design library to build from, but can't save into it — should it "
        "get its own key to write finished designs back on its own, or stay read-only?"
    ),
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
        # C5 GROUNDED explain (recollection, e93aa85): drawn from common memory — recall_for_decision
        # surfaced the real situation (the design library is a read-only synced copy; the save-back gap was
        # documented + left waiting), not invented. fork's live-gen explain leg MAY override this from the
        # recall bundle (resolved-not-stored per C5); until then this grounded text carries the C1 render.
        "why": (
            "Today the shared design library is a read-only copy the company builds from: it can read every "
            "design but can't write back, so saving finished work has been a separate, deliberate step (a "
            "known, documented gap). This decides whether to close that gap — give the company its own write "
            "key, scoped to only its own entries and revocable anytime, so it saves designs back on its own — "
            "or keep the read-only posture for now. Not choosing changes nothing: it stays read-only and pending."
        ),
    },
}
