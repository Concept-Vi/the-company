"""skills/inversion_query.py — AK3 composition SKILL (Cognition Engine · per-workflow recipe).

The inversion-query as a reader-composable recipe: find_relations(near∩¬far cross-space) — WHEN to
reach for it and HOW to use it to find what is MISSING / what shares a principle but diverges in
subject. Audience: an agent/operator-facing composition playbook (same registry format as
skill://summarize). FLOOR: find_relations is READ-only (no model call) — this skill describes a READ
composition; it never emits resolve/approve/dispatch.
"""

SKILL = {
    "id": "inversion_query",
    "label": "The inversion-query (find_relations)",
    "description": "Recipe: find_relations(item, near_space, far_space) returns items NEAR `item` in one space but NOT near it in another (near∩¬far). When + how to use it to find what's MISSING or what shares a principle yet diverges in subject.",
    "content": (
        "THE INVERSION-QUERY — find_relations(item, near_space, far_space, k=10, min_score=0.5).\n"
        "It returns the items NEAR `item` in `near_space` but NOT near it in `far_space` (a near∩¬far\n"
        "set difference). This is the discovery move a flat similarity search cannot make: 'same\n"
        "PRINCIPLE, different SUBJECT' (near_space='principles', far_space='topics'), or 'same SHAPE,\n"
        "different DOMAIN'. The inversion is what surfaces the non-obvious relation — and, used in\n"
        "reverse, what is MISSING.\n"
        "\n"
        "PREREQUISITE (or it fails loud): `item` must already have a PERSISTED vector in BOTH named\n"
        "spaces. Those vectors come from the corpus capture+embed pass over EMBEDDABLE lenses (see\n"
        "skill://corpus_pipeline LAYER 2) — the embedder must have been UP at build. If `item` has no\n"
        "vector in either space, find_relations RAISES (the inversion is undefined without both anchors;\n"
        "never a silent empty that reads as 'no relations'). Fix: run the capture+embed for `item` in\n"
        "both spaces first.\n"
        "\n"
        "GET THE SPACE IDS FROM THE REGISTRY (never invent one):\n"
        "  cognition_info().spaces lists the EMBEDDABLE projection ids (the live vector spaces). Pass\n"
        "  near_space / far_space ONLY from that set. A made-up space id is a failure (rule 8).\n"
        "\n"
        "HOW TO USE IT — three modes:\n"
        "\n"
        "  A · FIND THE RELATION (the default 'same principle, different subject'):\n"
        "     find_relations(item=<a corpus unit id/address>, near_space='principles',\n"
        "                    far_space='topics')\n"
        "     → relations = units that share `item`'s PRINCIPLE yet diverge in TOPIC. RETURNS\n"
        "       {relations:[ids], near:[{id,score}], far:[{id,score}], min_score, ...}. `relations` is\n"
        "       the inversion result; near/far carry the THRESHOLDED neighbour rows so you can render the\n"
        "       WHY (which scores put each item in/out).\n"
        "\n"
        "  B · FIND WHAT IS MISSING (the inversion read — the unique value):\n"
        "     Pick a known FINGERPRINT as `item` (a generic-AI tic, a cliché, an over-used shape). Run it\n"
        "     as near in the space that captures that fingerprint, far in the space of genuine substance.\n"
        "     The `relations` are units that LOOK like the fingerprint but lack the substance — i.e. what\n"
        "     is MISSING / what is generic. Subtraction by inversion: the same tool that finds a relation\n"
        "     finds an absence, by flipping which space anchors 'near'.\n"
        "\n"
        "  C · TUNE THE NEIGHBOUR THRESHOLD:\n"
        "     min_score (default 0.5) is the cosine floor for 'is a NEIGHBOUR'. query_index ranks EVERY\n"
        "     indexed item (including score≈0), so WITHOUT the threshold `far` would contain everything\n"
        "     and the difference would always be empty. Raise min_score to demand a tighter relation;\n"
        "     lower it to widen. `k` caps the per-space k-NN.\n"
        "\n"
        "WHEN TO REACH FOR IT (vs the pipeline):\n"
        "  • Use the 3-layer pipeline (skill://corpus_pipeline) to PRODUCE the corpus + its spaces.\n"
        "  • Use find_relations AFTER the embed pass, inside the patterned-visibility LOOK step\n"
        "    (skill://patterned_visibility step 2) — when you want a cross-space relation or a missing-ness\n"
        "    read that no single-space ranking or record-by-record read can give you.\n"
        "  • It is READ-only, no model call — cheap to run repeatedly as you vary item / spaces / min_score."
    ),
}
