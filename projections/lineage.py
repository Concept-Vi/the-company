"""projections/lineage.py — the SEED `lineage` lens (Cognition Engine K1 · a CODE projection).

The first `produced_by:"code"` seed (vs the model lenses): a STRUCTURAL lens a deterministic EXTRACTOR
produces, NOT a capture-role description — so it is EXCLUDED from the capture-schema (only `model` lenses
are described by the 4B) and OWNED by the lifters registry (a later NEWMOD pass: frontmatter/links/blocks
extractors). It proves the `produced_by` two-way split is exercised by a real discovered seed, not just
asserted. Does not embed (a structural fact, not a meaning space).

NOTE — distinct from the corpus-RECORD lineage: this lens is the file's OWN structural lineage (where the
file sits / what it derives from, extracted from its content). The corpus-record's session/round/project
lineage (runtime/corpus.py) is a DIFFERENT axis — the CAPTURE provenance (which run produced the record),
carried IN the cas record for cross-session corroboration. Same word, two axes; do not conflate.

See runtime/projections.py + projections/AGENTS.md. Its `id` MUST equal the file stem (`lineage`).
"""

PROJECTION = {
    "id": "lineage",
    "level": "structural",
    "produced_by": "code",
    "embeds": False,
    "stage": "legibility",
}
