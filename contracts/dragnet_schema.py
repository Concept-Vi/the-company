"""contracts/dragnet_schema.py — the FROZEN dragnet extraction superset (D1 LOCKED) + the D3 neutrality
fragment. Lives in contracts/ (the zero-dependency spine) so it is NON-AUTHORABLE: the dragnet role
registry rows (roles/dragnet_{coarse,fine,design}.py) and the safety door (runtime/roles._build_role)
both import these SAME class objects by import-path. A registry row can SELECT a grain (which of the three
roles fires) but can NEVER author a different schema shape — the door rejects any dragnet-family
output_schema that is not one of these exact classes, and rejects schema_slot (grain is role-identity,
not an authorable slot). This is what makes D1 (one superset) + the schema half of D3/D4 frozen
by-construction, not by-convention.

ONE superset: coarse ⊂ fine; design is the visual-dna-only additive extension. NOT a per-space fork —
the stored record is the one superset, design fields null/absent for non-DNA spaces (D1 / D2 near-lock).
"""
from __future__ import annotations
from typing import List
from pydantic import BaseModel


class Coarse(BaseModel):
    about: str                  # one phrase: what this content IS
    kind: str                   # decision | spec | discussion | digest | log | reference | other
    touches: List[str]          # topic/domain tags


class Fine(BaseModel):
    summary: str                # 1-2 sentence neutral summary
    entities: List[str]         # named things: systems, files, concepts, people
    claims: List[str]           # assertions/decisions stated
    relations: List[str]        # "X depends on Y" / "X supersedes Y"
    open_questions: List[str]   # unresolved threads ([] if none)


class Design(BaseModel):
    # visual-dna ONLY — the 2 additive/optional superset fields (DNA criteria 2+5, lead-settled 2026-06-22).
    # null/absent for full/theorem/transcript; NOT a per-space fork (the stored record is the one superset).
    resolves_into: List[str]    # match-key lookup: the design element(s)/component(s)/token(s) this maps to
    resolution: List[str]       # DIM-KEYED context-points: "<dim>:<context> -> <value>", dim ∈
                                # {line, opacity, colour_role, shape}


# The D3 NEUTRALITY FRAGMENT — non-authorable code. A dragnet_coarse registry row MUST carry this verbatim
# in its prompt (the safety door enforces presence); the author may add wording around it but can NEVER
# remove it. No static door can prove a free-text prompt is neutral, so this is the irreducible-tension
# guard (OPEN-1): the fragment is frozen, the rest of the prompt is authorable.
NEUTRAL_FRAGMENT = "describe it NEUTRALLY (only what it says — do not judge relevance)"

# The dragnet role FAMILY → its frozen output_schema. The single source the safety door checks identity
# against. A role id in this map is held to the freeze; any other role is unaffected (additive).
DRAGNET_FAMILY = {"dragnet_coarse": Coarse, "dragnet_fine": Fine, "dragnet_design": Design}
