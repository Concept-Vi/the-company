# projections/common_knowledge.py — the COMMON-KNOWLEDGE INDEX space (the recollection↔projection seam, Option A).
#
# WHY THIS EXISTS: the front-interface brief (2026-06-16) makes the projection Instrument the overlord's
# render surface over the fabric's common-knowledge index. recollection (Index Chief) comprehends the
# built-things across the fabric (the .discovery pipeline: structural extract → 4B interpret → validate) and
# PUBLISHES each comprehended unit into THIS company FsStore space — keyed by its contracts.address
# source_address (board:// · session:// · exchange:// · project:// · code:// …). Then the Instrument renders
# them natively: project(space=common_knowledge, center=<address>) → the meaning-field of the comprehended
# corpus. This is the agreed seam (recollection chose Option A — publish into a company space, reuse-don't-
# parallel — over my project() reading substrate-mcp chroma). The id IS the contract: recollection embeds with
# projection="common_knowledge"; project() reads vec://<source>#space=common_knowledge#emb=pplx.
#
# THE EMBED CONTRACT (recollection's publish path — the same one the layer model uses):
#   embed_corpus_to_spaces(store, records=[{source_address:<addr>, text:<comprehension>, projection:"common_knowledge"}],
#                          embeddable, base_url="http://localhost:8007/v1",
#                          model="perplexity-ai/pplx-embed-context-v1-4b", dim=2560, emb="pplx")
# pplx layer (2560-d) matches the operators/keystone layer, so nucleation can type the index against operators.
#
# HONEST STATE: the SPACE is declared + projectable NOW; it is EMPTY until recollection's pilot publishes (a
# declared home awaiting its data — not a toy slice, not green-paint). The per-unit VERIFICATION-STATE
# (recollection's render-for-cognition: shimmer=built-unverified/suspect, solid=verified-by-use) rides as
# point metadata on the published unit — the cleanest fill for the four-root STATE/PHASE axis. The level/
# stage metadata here is a sensible default; the Index Chief owns the index's semantics and may adjust this
# one file. See build-prep/front-interface/INTERFACE_BRIEF.md + build-prep/embedder-pplx/HOWTO-AND-REFERENCE.md.
PROJECTION = {
    "id": "common_knowledge",
    "level": "meaning",          # the comprehended corpus embedded as a semantic field (the band the lens reads at)
    "produced_by": "code",       # recollection's comprehension pipeline produces it (not a capture-model role)
    "embeds": True,              # it IS a vector space — the overlord field's content
    "field": "text",             # each unit's comprehension text is what gets embedded
    "desc": "the fabric's COMMON-KNOWLEDGE index — recollection's comprehended built-things (sessions/projects/"
            "board/exchanges, addressed in contracts.address), embedded as the overlord render-field; each unit "
            "carries its verification-state (the state/phase axis). The interface's query/render surface reads this.",
    "stage": "deep",             # the heavy comprehension pass (4B interpret), not the cheap broad legibility scan
}
