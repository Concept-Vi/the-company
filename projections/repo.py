"""projections/repo.py — the `repo` lens (Cognition Engine K1 · render-not-judge · COMPOSITION ① repo-exocortex).

The repo-exocortex content lens that DOES embed (`embeds:true`) → it becomes a vector SPACE (Group L:
op=embed → put_vector(vec://<item>#space=repo)), so `find_relations`/retrieve can range over the REPO
space. This is the G15 unblock: ① assumed a `repo` embeddable space but only principles/topics/worldview
existed, so a capture(projection='repo') failed loud. This declares it. The repo_digest role (roles/
repo_digest.py) produces the per-file digest; this lens names the embeddable space those digests land in.
produced_by a model; a text field (the file's purpose/summary, what grounds retrieval). render-NOT-judge.

See runtime/projections.py + projections/AGENTS.md. Its `id` MUST equal the file stem (`repo`).
"""

PROJECTION = {
    "id": "repo",
    "level": "content",
    "produced_by": "model",
    "embeds": True,
    "field": "text",
    "desc": "what this repo file IS — its purpose + the concepts it covers (describe, do not judge)",
    "stage": "legibility",
}
