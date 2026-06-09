"""roles/judge_drift.py — the DRIFT-RADAR confirm role (COMPOSITION ② · built-twice / overlap judge).

② drift-radar clusters the repo corpus (run_reduce mode='cluster' over space='repo' digests) → groups of
SEMANTICALLY-NEAR files. A near-cluster is a CANDIDATE built-twice / overlap, NOT a confirmed one (two files
can be near because they're the same logic in two places — OR legitimately-distinct siblings, e.g. two role
files that share a shape but do different jobs). judge_drift is the CONFIRM gate: given a cluster of near
file-digests, it judges whether they are GENUINELY duplicated/overlapping (one-should-be-the-source) or
legitimately distinct — so the drift map FLAGS real unification targets, not every near-neighbour (the
false-positive guard; variance-not-error → a low-confidence call FLAGS for review, never auto-asserts).

A SINGLE-GENERATE validator (mirrors roles/verify_lens.py — NOT a draws-jury; the cluster IS the evidence,
the judgement is one structured read). NO confidence score (the no-confidence law): the verdict is a closed
vocabulary + a short ground; the strength signal is the cluster's cosine + the verdict token, not a float.
op:generate; in the 'drift' cast (cast-beyond-listening; listening untouched). The FLOOR: it judges, it does
NOT fix — a confirmed drift becomes a MARK (mark_type=built-twice/overlap) for review, never an auto-edit.
"""
from pydantic import BaseModel
from typing import Literal


class JudgeDriftOut(BaseModel):
    verdict: Literal["built-twice", "overlap", "distinct"]   # the closed call (no confidence float)
    # built-twice = the SAME logic/vocabulary in 2+ places (should be one-sourced);
    # overlap     = significant shared responsibility (a unification candidate, softer than built-twice);
    # distinct    = legitimately separate despite semantic nearness (NOT a drift finding — the FP guard).
    shared: str            # what they share (the logic/vocabulary/responsibility) — grounded in the digests
    the_source: str        # if built-twice/overlap: which should be the single source (or "" if unclear/distinct)
    note: str              # one short clause grounding the call


ROLE = {
    "id": "judge_drift",
    "label": "drift judge (built-twice / overlap confirm)",
    "description": "Given a cluster of semantically-near repo files, judges genuine built-twice/overlap vs "
                   "legitimately-distinct — the drift-radar's false-positive guard (② · COMPOSITION).",
    "prompt_template": (
        "You are the JUDGE_DRIFT role of the drift-radar. You are given a CLUSTER of repo files that are "
        "SEMANTICALLY NEAR (their purpose-digests cluster together). Judge whether they are genuinely "
        "DUPLICATED — the SAME logic, vocabulary, or responsibility implemented in more than one place "
        "(a unification target) — or legitimately DISTINCT (near because they're the same KIND of thing, "
        "but doing different jobs — e.g. two role files share a shape but serve different roles).\n"
        "Return JSON: {\n"
        '  "verdict": "built-twice" (same logic/vocabulary in 2+ places, should be ONE source) | '
        '"overlap" (significant shared responsibility, a softer unification candidate) | '
        '"distinct" (legitimately separate despite nearness — NOT a drift finding),\n'
        '  "shared": what they actually share (grounded in the digests — name the logic/vocabulary), or "" if distinct,\n'
        '  "the_source": for built-twice/overlap, which file SHOULD be the single source (else ""),\n'
        '  "note": one short clause grounding the call.\n'
        "}\n"
        "Be CONSERVATIVE: only built-twice/overlap when there is a REAL shared thing one source could hold; "
        "when in doubt, 'distinct' (the drift map must flag real targets, not noise). NO confidence score — "
        "the verdict token + the cluster's nearness carry the signal.\n\n"
        "THE CLUSTER:\n{utterance}"
    ),
    "output_schema": JudgeDriftOut,
    "input_addresses": ("utterance",),
    "op": "generate",
    "mode_scope": ["drift"],
}
