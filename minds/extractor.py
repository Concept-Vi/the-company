"""extractor — a role-mind: the fast fact-extractor leg of the N+1 composition.
Binds the existing roles/mine_exchange (extracts structured facts from an exchange/utterance) — the
EXTRACT half of extraction-vs-judgment. Reuse-don't-parallel: a mind is a named reference to a real role."""
MIND = {
    "id": "extractor",
    "kind": "role",
    "role": "mine_exchange",
    "desc": "fast fact-extractor (binds roles/mine_exchange) — emits structured facts for the judge to weigh.",
}
