"""roles/guide_author.py — the guide-author's BRAIN role (cognition-is-role-resolved).

The guide-author (`runtime/guide_author.py`) composes a narrative how-to FROM resolved sources. Its
MODEL is a ROLE, never pinned — this role resolves to a model via the registry/cfg (default_model
None → the cfg brain, exactly like reduce_synth). `model_composer(role='guide_author')` uses this
binding; the guide-writing framing is supplied by the composer (the judge precedent: resolve a role
for its binding, then supply task-specific messages). The prompt_template documents the intent AND
makes the role usable directly via run_role. op=generate. In NO mode_scope (fired explicitly by the
guide-author, never part of a listening cast — mirrors reduce_synth/verify_jury).
"""
from pydantic import BaseModel


class GuideAuthorOut(BaseModel):
    """One narrative guide body (markdown), grounded only in the supplied sources."""
    guide: str


ROLE = {
    "id": "guide_author",
    "label": "Guide author",
    "description": "Composes a narrative how-to guide for a target, grounded ONLY in the supplied sources.",
    "prompt_template": (
        "You write a concise NARRATIVE how-to guide for the given target, for a human/agent learning to "
        "use it. Ground it ONLY in the supplied sources — add nothing they do not support. Sections: "
        "what it is · when to reach for it · how (the steps) · a worked example · gotchas. Return ONLY "
        'JSON with one field:\n  "guide": the markdown guide body (no preamble).'
    ),
    "output_schema": GuideAuthorOut,
    "input_addresses": ("utterance",),
    "model_binding": {"requires": ["chat", "reasoning"], "default_model": None, "default_base_url": None},
    "op": "generate",
    "trigger": "fired by runtime/guide_author.py (model_composer) to compose a guide narrative from resolved sources.",
}
