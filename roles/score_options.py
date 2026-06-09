"""roles/score_options.py — the SCORE_OPTIONS reduce-role (COMPOSITIONS ⑩ · the option-panel REDUCE).

The REDUCE half of composition ⑩ (OPTION-PANELS): the cross-option JOIN that takes the N per-lens
approaches developed by `roles/develop_option.py` (the MAP) and turns them into a PRE-RANKED option-space
with a reasoned RECOMMENDATION that may GRAFT runner-up strengths. This is the judge-panel pattern (a
diverse panel + a scoring judge beats one-attempt-iterated when the option-space is wide) — the
CLAUDE.md "offer options" rule, supercharged, then sharpened into a recommendation Tim can steer.

★ A REDUCE-ROLE, mirroring `roles/reduce_synth.py` EXACTLY (the C 2/4 synthesize-join template):
   `op:generate`, takes the N map-output approaches — composed by `run_reduce(mode="role")` into ONE
   labelled `"notes"` input (the N develop_option outputs are DYNAMIC, so the compose is the DRIVER's job,
   not statically declared here) — and merges them into ONE scored recommendation. Fired explicitly via
   `run_reduce(mode="role", role=score_options)`; the driver supplies `ctx={"notes": composed}` where
   `composed` renders each upstream option as "[unit_id] <json>" (so this role sees which approach came
   from which lens — and DevelopOptionOut echoes `lens`, so the lens label is carried inside each JSON too).

★ THE INPUT AXIS (C 1/4 — the one place behaviourally identical to reduce_synth):
   `input_addresses=("notes",)`. "notes" is a DECLARED non-utterance input present in the ctx that
   `run_reduce(mode="role")` supplies → run_role's `_is_default_input` is False → the labelled-compose
   path (NOT the default-utterance framing). The N upstream `run://` addresses are dynamic (the panel's
   outputs) so they are NOT statically listed here — run_reduce reads them back and composes them into
   this one "notes" input. Identical to reduce_synth's seam.

★ THE OUTPUT IS RICHER THAN reduce_synth (the one place the mirror's SHAPE differs — deliberate). Where
   reduce_synth returns a flat `{summary:str}`, the option-panel reduce must return a per-option RANK
   list + a recommendation + the grafts. So `scored` is a nested `list[ScoredOption]` (each a sub-model
   {lens, rank, why}) — the richer field-type grammar (kind:list[object]), the SAME nested-sub-model +
   list pattern `roles/register_element.py` uses (its `HowTo` sub-model). `rank` is an int ORDINAL
   (1=strongest, ties allowed) — a count/ordinal, NOT a fake-precision float (the no-confidence law, G16;
   register_element's old `confidence:float` was migrated out for the same reason). The ORDERING is what
   the recommendation + grafts need (the lead + the runner-ups), and an ordinal states it without false precision.

★ NO mode_scope → in NO cast (a reduce-role fired explicitly via run_reduce, not part of any listening/
   panel cast) — so adding it does NOT change any cast (mirrors reduce_synth's + verify_jury's "in no
   cast" stance). The MAP role (develop_option) carries mode_scope={"panel"}; the REDUCE is fired
   directly, exactly as reduce_synth is.

★ THE FLOOR (AGENTS.md rule 9 · the COMPOSITIONS two invariant laws · cognition_governance). Advisory
   only — the reduce RECOMMENDS; Tim decides the fork. This file is a pure ROLE dict + Pydantic output
   classes: it emits no resolve/approve/dispatch, launches no `claude -p`. A reduce-role is pure data +
   a model call (the join is L1 data: which role, what schema; the model runs INSIDE the role, L2). The
   `rules` entry below is a DECLARED reduce rule (DATA) — the reduce DRIVER is runtime/cognition.run_reduce;
   the role does not itself execute a verdict.
"""
from pydantic import BaseModel


class ScoredOption(BaseModel):
    """One ranked option in the panel's tally — the nested sub-model (kind:object in the richer field-type
    grammar, the SAME nested pattern register_element's HowTo uses), keyed to the lens that produced it."""
    lens: str       # which lens's approach this rank is for (echoed from the upstream develop_option output)
    rank: int       # the ORDINAL standing, 1 = strongest (ties allowed) — a count/ordinal, NOT a fake-precision
    #                 float (the no-confidence law, G16: tags+counts; the `why` carries the qualitative reason)
    why: str        # the concrete reason for the rank — what makes this approach strong or weak


class ScoreOptionsOut(BaseModel):
    """`score_options` reads the N composed develop_option approaches → a PRE-RANKED option-space + a
    reasoned recommendation that may GRAFT the best of the runners-up. Richer than ReduceSynthOut's flat
    {summary}: a nested list[ScoredOption] + the recommendation + the grafts. Advisory — Tim decides."""
    scored: list[ScoredOption]   # one {lens, rank, why} per upstream approach — the pre-ranked space
    recommendation: str          # the reasoned recommendation across the panel (advisory; Tim decides)
    grafts: str                  # how the recommendation grafts runner-up strengths onto the lead approach


ROLE = {
    "id": "score_options",
    "label": "Score options (panel reduce)",
    "description": (
        "Reduces the N per-lens approaches (developed by develop_option, composed by run_reduce) into a "
        "PRE-RANKED option-space + a reasoned recommendation that may graft runner-up strengths — the "
        "REDUCE half of the option-panel (COMPOSITIONS ⑩). Advisory: it recommends; Tim decides the fork."
    ),
    "prompt_template": (
        "You are the SCORE_OPTIONS reduce-role — the cross-option JUDGE of an OPTION PANEL. You are given "
        "several developed approaches to ONE decision, one per upstream panelist, each on its own line "
        "prefixed by its unit id in [brackets]. Each approach carries the LENS it was developed through "
        "(mvp-first · risk-first · reuse-first · framework-first · radical-recompose) plus its approach, "
        "buys, costs, touches, and risk.\n"
        "\n"
        "Do THREE things:\n"
        "  1. RANK the approaches (1 = strongest; ties allowed) against the decision — weighing what each "
        "buys vs what it costs, how grounded and complete it is, and its risk. Give the concrete reason for "
        "each rank. Use an ORDINAL rank, NOT a 0..1 score — no fake-precision number.\n"
        "  2. RECOMMEND: synthesize ONE reasoned recommendation across the whole panel — which approach (or "
        "blend) you would put forward, and WHY. This is ADVISORY; you never pick the fork, you recommend.\n"
        "  3. GRAFT: say how your recommendation grafts the STRENGTHS of the runner-up approaches onto the "
        "lead one (the best recommendation often borrows a runner-up's strength — name what you grafted "
        "and from which lens).\n"
        "\n"
        "Return ONLY JSON with exactly these fields:\n"
        '  "scored": a list, one object per approach — { "lens": the approach\'s lens, "rank": an integer '
        '(1 = strongest, ties allowed), "why": the concrete reason for the rank },\n'
        '  "recommendation": a reasoned recommendation across the panel (advisory),\n'
        '  "grafts": how the recommendation grafts runner-up strengths onto the lead (name lens + strength).\n'
        "\n"
        'Example: {"scored": [{"lens": "reuse-first", "rank": 1, "why": "least net-new, additive and '
        'reversible, but limited headroom"}, {"lens": "framework-first", "rank": 2, "why": "cleanest '
        'long-term shape but more code now"}], "recommendation": "Take the reuse-first approach now — it is '
        'the least-risk path that ships.", "grafts": "Graft framework-first\'s clean read-back seam onto it '
        'so the additive path can generalize later without a rewrite."}'
    ),
    "output_schema": ScoreOptionsOut,
    # The declared input axis (C 1/4): "notes" is the composed N-approaches input run_reduce supplies in
    # ctx. Present-in-ctx + non-utterance ⇒ run_role's labelled-compose path (NOT the default utterance
    # framing). The N upstream run:// addresses are dynamic (the panel's develop_option outputs) so they
    # are NOT statically listed here — run_reduce reads them back and composes them into this one "notes"
    # input. Identical to reduce_synth's seam.
    "input_addresses": ("notes",),
    "op": "generate",
    "trigger": (
        "fired explicitly by run_reduce(mode='role', role=score_options) as the cross-option JOIN of the "
        "option-panel (COMPOSITIONS ⑩) — over the N develop_option approaches (the panel's MAP outputs)."
    ),
    "model_binding": {"requires": ["chat", "json"], "default_model": None, "default_base_url": None},
    # NO mode_scope → in NO cast (a reduce-role fired explicitly via run_reduce). Mirrors reduce_synth.
    "rules": [
        # DECLARED reduce rule (DATA; the reduce DRIVER is runtime/cognition.run_reduce). The N per-lens
        # approaches are joined into one scored recommendation — the cross-option scoring join.
        {"id": "reduce-score-options", "reads": "score_options.notes",
         "effect": "rank the N per-lens approaches + synthesize a recommendation grafting runner-up strengths",
         "kind": "reduce"},
    ],
    "render_hint": {"shape": "scored-options", "lane": "score_options"},
}
