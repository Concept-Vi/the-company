"""roles/verify_jury.py — a JURY role (Concurrent Cognition G2 · C2.4 + C1.5).

Jury/ensemble is FIRST-CLASS: ANY role may declare `draws: N` + a verdict rule (quorum/vote). This is
the canonical example — a `verify` jury that runs N VARIED draws of a boolean classification and takes
a deterministic MAJORITY-VOTE verdict OVER them. The N varied draws come from C1.5's per-draw cache-key
(distinct run://<turn>/<role>#i addresses + temperature>0), so they don't collapse at the memo gate.

L2 — the verdict rule is a PURE deterministic function over the resolved draws (no eval, no model call;
a model runs only INSIDE a draw). C0.2/R2-FOLD H7 scope: the DRAWS are intentionally varied; the
VERDICT over them is deterministic — no contradiction with replay-identical routing.

⚠ E4 EPISTEMIC-MONOCULTURE CAVEAT (C2.4, the binding caveat): N draws on ONE model are N CORRELATED
samples — they measure the model's VARIANCE, not INDEPENDENT error. A jury whose CORRECTNESS truly
matters needs MODEL DIVERSITY (a 2nd small model / a cloud tiebreak), not just more draws of the same
model. v1 is single-model WITH this limit documented (Tim-fork F-a). The verdict_rule signature below is
designed so a 2nd-model / cloud tiebreak can SLOT IN later: it receives the list of draws (each a dict);
a future build can tag each draw with its `provider` and weight/tiebreak across providers WITHOUT
changing this rule's call shape. Until then the rule is an honest majority-vote over correlated draws.

NOT in any mode_scope (a demonstrative jury fired explicitly via run_jury, not part of a listening
cast) — so adding it does NOT change the listening cast. draws=3.
"""
from pydantic import BaseModel


class VerifyOut(BaseModel):
    """One draw of the verify jury: a boolean claim + a one-line reason."""
    holds: bool
    reason: str


def majority_vote(draws: list[dict]) -> dict:
    """The VERDICT rule — a PURE deterministic majority vote over the N draws (L2). Each draw is a
    resolved VerifyOut dict ({holds, reason}). Returns {verdict: bool, votes_true, votes_false, n,
    unanimous}. Deterministic: the SAME set of draws always yields the SAME verdict regardless of the
    order they finished in (it counts, it does not depend on arrival order).

    E4 slot-in point: `draws` could later carry a per-draw `provider` so a future verdict weights /
    tiebreaks across MODELS (independent error) rather than counting correlated same-model samples.
    The call shape (a list of draw dicts → a verdict dict) does not change."""
    votes_true = sum(1 for d in draws if d.get("holds") is True)
    votes_false = len(draws) - votes_true
    return {"verdict": votes_true > votes_false, "votes_true": votes_true,
            "votes_false": votes_false, "n": len(draws),
            "unanimous": votes_true == len(draws) or votes_false == len(draws)}


ROLE = {
    "id": "verify_jury",
    "label": "Verify (jury)",
    "description": "Runs N varied draws of a boolean claim → a deterministic majority-vote verdict (C2.4).",
    "prompt_template": (
        "You are a member of a VERIFY JURY. You are given a claim. Decide whether it HOLDS, and give a "
        "one-line reason. Return ONLY JSON with two fields:\n"
        '  "holds": a boolean — true if the claim holds, false otherwise,\n'
        '  "reason": a one-line reason.\n'
        'Example: {"holds": true, "reason": "the storage layer is content-addressed on ext4 by design."}'
    ),
    "output_schema": VerifyOut,
    "input_addresses": ("claim",),
    "trigger": "fired explicitly as a jury (run_jury) when a boolean must be verified by a quorum.",
    "model_binding": {"requires": ["chat", "json"], "default_model": None, "default_base_url": None},
    # NO mode_scope → in no cast (a demonstrative jury fired explicitly, not part of listening).
    "draws": 3,                        # C2.4 / C1.5 — N varied draws (per-draw key → distinct addresses)
    "verdict_rule": majority_vote,     # PURE deterministic verdict over the draws (L2 — no model call)
    "rules": [
        {"id": "verify-verdict", "reads": "verify_jury.draws",
         "effect": "majority_vote over the N draws → a deterministic verdict", "kind": "verdict"},
    ],
    "render_hint": {"shape": "jury", "lane": "verify", "draws": 3},
}
