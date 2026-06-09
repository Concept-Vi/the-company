"""roles/embed.py — the demonstrative EMBED-ROLE (the op-axis vector path · #50 first by-use proof).

The op-axis (C) made real on the embed side: a role declares `op="embed"`, so `run_role` takes the
EXISTING `complete_embeddings` vector path (reuse — zero new plumbing) instead of the generate path.
An embed role needs NO prompt_template/output_schema — it EMBEDS its input text into a vector, it does
not generate JSON. Its `can_fire` is satisfied by op=="embed" (runtime/roles.py:102), not a template.

INPUT (the C input-axis): the DEFAULT input is `("utterance",)` — `run_role`/`_embed_text_for` embeds
`ctx["utterance"]` itself (the RAW text, NOT the "Utterance: …" generate-framing — that prefix is a
chat artifact, wrong for a vector). A richer caller can declare extra inputs (composed as labelled
lines), but the demonstrative role embeds the utterance directly.

OUTPUT: `run_role` returns `{"vector", "dim", "model"}` from the LOCAL resident embedder only (no
cloud embeddings — Tim's correction; an embedder takes a small card slot, co-resides, but is NOT a
cloud escape from residency). A down/empty/dim-mismatch embedder RAISES FabricError (fail-loud).

NOT in any mode_scope (a demonstrative role fired explicitly, not part of a listening cast — mirrors
verify_jury/reduce_synth). It emits NO resolve/approve/dispatch (operator-only floor): it is pure data
+ an embed call. Its model_binding requires the embed capability (resolved to the local embedder).
"""

ROLE = {
    "id": "embed",
    "label": "Embed (vector)",
    "description": "Embeds its input text into a dense vector via the local embedder — the op=embed path.",
    "op": "embed",
    # The declared input axis (C 1/4): the DEFAULT — embed the utterance text directly.
    "input_addresses": ("utterance",),
    "trigger": "fired explicitly (run_role with op=embed) to produce a vector; not part of a listening cast.",
    "model_binding": {"requires": ["embed"], "default_model": None, "default_base_url": None},
    # NO prompt_template / output_schema (an embed role embeds, it does not generate) — can_fire via op=embed.
    # NO mode_scope → in no cast (a demonstrative embed-role fired explicitly).
    "render_hint": {"shape": "vector", "lane": "embed"},
}
