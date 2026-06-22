"""projections/code_archaeology.py — the `code_archaeology` lens (the code-archaeology dragnet's SPACE).

The reusable build-prep PRIMITIVE's output space (board://item-d1a7bf75): ONE descriptive record per repo
file (coverage-complete), embedded → semantically queryable (`corpus op=query space=code_archaeology`) AND
stored structured at `code://<project>/<rel_path>` (field-queryable, M2). produced_by=`code` — a PARSER-FIRST
extractor (deterministic structural facts: symbols/imports/declares; + an LLM describe for the prose).
render-NOT-judge: describes what a file IS, never judges relevance.

The G15 precedent (projections/repo.py): a capture into an UNREGISTERED space FAILS LOUD — this declares
`code_archaeology` so the dragnet's capture_corpus populates it. id MUST equal the file stem.
See runtime/projections.py + projections/AGENTS.md.
"""

PROJECTION = {
    "id": "code_archaeology",
    "level": "content",
    "produced_by": "code",
    "embeds": True,
    "field": "text",
    "desc": "what a repo file IS — its structure (symbols/imports/declares) + a neutral description "
            "(the code-archaeology dragnet's coverage-complete map; describe, do not judge)",
    "stage": "legibility",
}
