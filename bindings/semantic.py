# THE CIRCLE — semantic radius (Group 6). radius_from='semantic' → r = meaning-distance from the
# centre (1 - cosine, normalized for legibility), read off the persisted per-space vectors. The centre
# is an item with a vector in `space`; the bridge resolves the vectors (store.get_vector) and passes
# them to the pure project(). angle stays 'kind' (Group 6 owns the CIRCLE; the ANGLE — order-from-edges
# — is Group 10). `space` names which embeddable lens space the cosine reads (topics/principles/
# worldview/repo — registry-is-truth; a space with no vectors yet just yields an empty meaning-ring).
BINDING = {
    "id": "semantic",
    "label": "Meaning — how close in meaning to the centre",
    # human meaning (registry-true, declared-first; TENTATIVE draft — Tim/DNA ratify; never machine names)
    "meta": {
        "name": "Meaning",
        "is": "Everything arranged by how close in meaning it is to one thing you choose.",
        "fills": "You pick a centre; everything else sits near or far by how related in meaning it is — near means close in meaning, far means unrelated.",
        "why": "To find what's most related in meaning to something you care about.",
    },
    "angle_from": "kind",
    "radius_from": "semantic",
    "space": "topics",
    "order_by": "count",
}
