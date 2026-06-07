"""roles/check.py — the CHECK role (Concurrent Cognition G2 · C2.3 listening cast).

The CONTRADICTION sentinel: a forming answer vs the grounded facts → does the answer contradict
ground? NEW in G2 (locked `listening` cast — DECISIONS Batch 3 Q1).

CHAINS AFTER a part starts: unlike focus/recall/ground/connect (which fire from the utterance), `check`
reads the FORMING ANSWER (a run:// address produced once a reply part begins) AGAINST `ground`'s
resolved output. Its DEPENDENCY is declared as DATA here (input_addresses includes the forming-answer
ref); the staged-part CHAINING executor that fires check after part-1 emits is G3 (rule engine) / G4
(staged-response queue) — flagged downstream. This file declares the role; it does not build the chainer.
Fireable; part of the `listening` cast.
"""
from pydantic import BaseModel


class CheckOut(BaseModel):
    """`check` reads the forming answer vs ground → whether the answer contradicts the grounded facts."""
    contradicts: bool
    note: str


ROLE = {
    "id": "check",
    "label": "Check (contradiction)",
    "description": "Forming answer vs grounded facts → does the answer contradict ground? (chains after a part starts)",
    "prompt_template": (
        "You are the CHECK role — you verify a FORMING answer against the grounded facts and flag any "
        "contradiction. You are given the forming answer and a grounding note. Return ONLY JSON with "
        "two fields:\n"
        '  "contradicts": a boolean — true if the forming answer contradicts the grounded facts,\n'
        '  "note": a one-line explanation of the contradiction (or "" if none).\n'
        'Example: {"contradicts": false, "note": ""}'
    ),
    "output_schema": CheckOut,
    # DECLARED inputs: a run:// ref to the forming answer (produced once part-1 starts) + ground's
    # resolved output. The CHAINING (fire check after part-1 emits) is G3/G4 — declared, not built here.
    "input_addresses": ("run://<turn>/part-1", "ground"),
    "trigger": "CHAINS after a reply part starts: reads the forming answer vs ground (G3/G4 chainer).",
    "model_binding": {"requires": ["chat", "json"], "default_model": None, "default_base_url": None},
    "mode_scope": {"listening"},
    "rules": [
        {"id": "check-flags-contradiction", "reads": "check.contradicts",
         "effect": "flag/correct the forming answer in a later part", "kind": "route",
         "chains_after": "part-1"},
    ],
    "render_hint": {"shape": "check", "lane": "check", "chained": True},
}
