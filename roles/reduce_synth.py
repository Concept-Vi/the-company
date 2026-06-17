"""roles/reduce_synth.py — the demonstrative REDUCE-ROLE (Concurrent Cognition C 2/4 · the join role).

The cross-unit REDUCE's `mode="role"` synthesize join (COGNITION-REVIEW "the smart REDUCE" · CORPUS-CHAIN
§2-REDUCE compose): the `reduce-tree` THOUGHT_SHAPE's declared `join` role made REAL. It takes the N
map-output notes — composed by `run_reduce` into ONE labelled input (the N addresses are DYNAMIC, so the
compose is the driver's job, not statically declared here) — and MERGES them into ONE summary.

This is the template + the by-use proof for the reduce-role variant: a generate role whose INPUT is the
N read-back map outputs (via the C 1/4 input-axis — run_reduce supplies ctx={"notes": <composed>}, hitting
run_role's labelled-compose path because "notes" is a declared non-utterance input present in ctx), and
whose OUTPUT is one synthesized {summary} (op=generate, the default).

NOT in any mode_scope (a demonstrative reduce-role fired explicitly via run_reduce, not part of a listening
cast) — so adding it does NOT change the listening cast (mirrors verify_jury's "in no cast" stance).
Op=generate (the default). A reduce-role emits NO resolve/approve/dispatch (operator-only floor) — it is
pure data + a model call (the join is L1 data: which role, what schema; the model runs INSIDE the role, L2).
"""
from pydantic import BaseModel


class ReduceSynthOut(BaseModel):
    """`reduce_synth` reads the N composed map outputs → ONE merged summary across them."""
    summary: str


ROLE = {
    "id": "reduce_synth",
    "label": "Reduce (synthesize)",
    "description": "Merges the N map-output notes (composed by run_reduce) into ONE summary — the reduce-tree join role.",
    "prompt_template": (
        "You are the REDUCE role — the cross-unit JOIN of a map-reduce. You are given several notes, "
        "one per upstream unit, each on its own line prefixed by its unit id in [brackets]. SYNTHESIZE "
        "them into ONE merged summary that joins what they say (no per-unit list — a single combined "
        "summary). Return ONLY JSON with one field:\n"
        '  "summary": a short merged summary across all the notes.\n'
        'Example: {"summary": "All three notes agree the storage layer stays content-addressed on ext4."}'
    ),
    "output_schema": ReduceSynthOut,
    # The declared input axis (C 1/4): "notes" is the composed N-map-outputs input run_reduce supplies in
    # ctx. Present-in-ctx + non-utterance ⇒ run_role's labelled-compose path (NOT the default utterance
    # framing). The N upstream run:// addresses are dynamic (the wave's outputs) so they are NOT statically
    # listed here — run_reduce reads them back and composes them into this one "notes" input.
    "input_addresses": ("notes",),
    "op": "generate",
    "trigger": "fired explicitly by run_reduce(mode='role') as the reduce-tree join role over a wave's N outputs.",
    # CAPABILITY TIER (#71): reduce_synth is the cross-unit SYNTHESIS join — it REASONS over N upstream
    # outputs, so it requires `reasoning`. The resident 4B is no-think (provides [chat,json,tools,fast,
    # no-think], NOT reasoning) → resolve_model routes reduce_synth → a reasoner (today: the local
    # loadable:chat-nemotron, [chat,json,thinking,reasoning]) — extraction-vs-judgment: the 4B extracts, the
    # reasoner judges/synthesizes (NOT the 4B judging). DECLARES the capability the role needs (the suitability
    # read resolve_model routes on); does NOT change today's firing (RESIDENT_MODEL kwarg until Phase 2).
    "model_binding": {"requires": ["chat", "json", "reasoning"], "default_model": None, "default_base_url": None},
    # NO mode_scope → in no cast (a demonstrative reduce-role fired explicitly via run_reduce).
    "rules": [
        # DECLARED reduce rule (DATA; the reduce DRIVER is runtime/cognition.run_reduce). The N map
        # outputs are joined into one summary — the cross-unit synthesize join (reduce-tree).
        {"id": "reduce-synthesize", "reads": "reduce_synth.notes",
         "effect": "merge the N map-output notes into one summary", "kind": "reduce"},
    ],
    "render_hint": {"shape": "summary", "lane": "reduce"},
}
