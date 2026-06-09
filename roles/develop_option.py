"""roles/develop_option.py — the DEVELOP_OPTION role (COMPOSITIONS ⑩ · the option-panel MAP).

The MAP half of composition ⑩ (OPTION-PANELS): for a design fork (Tim's A/B/C pattern), instead of MY
single framing of the option-space, fan independent free swarm-models over the SAME question — each
developing ONE *distinct* approach through ONE biasing LENS (mvp-first · risk-first · reuse-first ·
framework-first · radical-recompose). THIS file is the ONE role that develops a SINGLE approach from a
SINGLE lens; the "panel" is the COMPOSITION — `run_items(develop_option, [..N lens-units..])` fires the
SAME role N times, once per lens, concurrent on the resident 4B swarm. The CLAUDE.md "offer options" rule,
supercharged: a diverse panel, not one framing. (The reduce that SCORES + recommends across them is the
sibling role `roles/score_options.py`, fired via `run_reduce(mode="role")`.)

★ THE LENS RIDES IN THE INPUT — that is what lets ONE role be N panelists (the axis-inversion, C 3/4),
   EXACTLY as `verify_lens.py` makes one role be N jurors. `run_items` places each unit at
   `ctx["utterance"]` (the role's primary input → run_role's DEFAULT byte-identical path, framed
   `f"Utterance: {unit}"`). So a unit is a small dict carrying the lens id + the decision question + the
   constraints, exactly as COMPOSITIONS ⑩ specifies:
       {"lens": "mvp-first",        "question": "<the decision/fork>", "constraints": "<what bounds it>"}
       {"lens": "radical-recompose","question": "<the decision/fork>", "constraints": "<what bounds it>"}
   The prompt holds the model to develop a FULL approach FROM ITS lens's bias ONLY (the one named in the
   unit) — fan the same role over N lenses and each draw develops one biased-but-complete approach.
   `input_addresses` stays the DEFAULT `("utterance",)`: `lens`/`question`/`constraints` are KEYS INSIDE
   the unit dict, NOT separate declared inputs (declaring them would trip the net-new compose path / leave
   dead declared-extras). Mirrors `verify_lens.py`'s lens-in-unit shape + `register_element.py`'s
   run_items-fanned MAP shape + `screen_reader.py`'s single-generate Pydantic-output shape.

★ THE LENS VOCABULARY (COMPOSITIONS ⑩). Declared as visible DATA (the LENSES tuple) so the set is in one
   place — the same five the composition's run_items call fans, and the drift home names. The lens is a
   BIAS, not a filter: each lens develops a FULL, real approach to the WHOLE question, slanted by its
   priority — so the panel spans the option-space rather than agreeing.

★ GROUNDED IN THE CONSTRAINTS (no-fiction). The approach must be developed against the `constraints`
   carried in the unit (what exists / what bounds the decision), not invented in a vacuum — `touches`
   names the real systems an approach would change. (Per COMPOSITIONS ⑩, the cascade can additionally
   feed a retrieved corpus-slice; here the constraints ride in the unit, mirroring how verify_lens carries
   its `bar` in-unit. Richer per-mockup/run:// grounding is the cascade/chainer's job downstream, not this
   file — same posture as verify_lens.)

★ THE FLOOR (AGENTS.md rule 9 · the COMPOSITIONS two invariant laws · cognition_governance). Advisory
   only — a panelist NEVER picks the fork; Tim decides (the reduce only RECOMMENDS). This file is a pure
   ROLE dict + a Pydantic output class: it emits no resolve/approve/dispatch, launches no `claude -p`. An
   approach is a PROPOSAL of thinking, not an action.

`op:generate` (default), `mode_scope:{"panel"}` — a panel CONTEXT cast (the cast-beyond-listening seam,
the same seam screen_reader/verify_lens/register_element ride; an UNKNOWN mode yields an EMPTY cast, so
adding this does NOT touch the listening cast). Fired over N lens-units by `run_items` (the MAP).
"""
from pydantic import BaseModel


# The closed lens vocabulary (COMPOSITIONS ⑩). Declared as visible DATA (not buried in prose) so the set
# is one place — the same five the composition's run_items call fans, and the drift home names. Each lens
# is a BIAS that develops a FULL approach to the whole question, not a partial view.
LENSES = (
    "mvp-first",         # the smallest thing that works — ship the thin slice, defer the rest
    "risk-first",        # what could go wrong — minimize blast-radius / irreversibility / unknowns first
    "reuse-first",       # LAW-0 — build on what already exists; take the duplicate/adjacent thing into scope
    "framework-first",   # the principled, complete, well-structured shape — do it properly, generalize
    "radical-recompose", # question the framing itself — a from-scratch recomposition, not an increment
)


class DevelopOptionOut(BaseModel):
    """One lens's fully-developed approach to ONE decision. Every field is a scalar string (mirrors
    ScreenReaderOut's flat-scalar shape) so a panelist's output is a clean, comparable dossier the reduce
    (`score_options`) can score side-by-side. `lens` is ECHOED back (from the unit) so the reduce can key
    each scored option to the lens that produced it (the same echo-the-input discipline as VerifyLensOut)."""
    lens: str       # ECHO the lens this approach was developed through (from the unit)
    approach: str   # the FULL approach — what to build/do, developed from this lens's bias, concretely
    buys: str       # what this approach BUYS (its upside — what you get by taking it)
    costs: str      # what it COSTS (its downside / what you give up / pay)
    touches: str    # the real systems/files/seams this approach would change (grounded in the constraints)
    risk: str       # the chief risk of this approach (what could go wrong, how reversible)


ROLE = {
    "id": "develop_option",
    "label": "Develop option (one lens)",
    "description": (
        "Develops ONE full approach to a decision through ONE biasing LENS (mvp-first · risk-first · "
        "reuse-first · framework-first · radical-recompose). The lens rides in the per-unit input, so "
        "run_items fans the SAME role over N lenses — the MAP half of the option-panel (COMPOSITIONS ⑩). "
        "Advisory: a panelist develops, it never picks the fork; the reduce (score_options) recommends."
    ),
    "prompt_template": (
        "You are ONE PANELIST of an OPTION PANEL. You develop ONE full approach to a DECISION through "
        "exactly ONE LENS, and you develop it FROM THAT LENS'S BIAS — never another angle.\n"
        "\n"
        "Your input is a unit containing three things:\n"
        "  - `lens`        — the ONE lens whose bias you must develop the approach from (one of: "
        "mvp-first, risk-first, reuse-first, framework-first, radical-recompose);\n"
        "  - `question`    — the decision / fork to develop an approach to;\n"
        "  - `constraints` — what bounds the decision (what exists, what must be preserved, the limits). "
        "Ground your approach in these — name the REAL systems it would touch; do not invent.\n"
        "\n"
        "What each lens biases you toward (develop a FULL, real approach to the WHOLE question, slanted "
        "by your lens — the lens is a PRIORITY, not a partial view):\n"
        "  - mvp-first: the smallest thing that genuinely works — ship the thin slice now, defer the rest.\n"
        "  - risk-first: minimize what could go wrong — least blast-radius, least irreversibility, "
        "fewest unknowns; de-risk before you build.\n"
        "  - reuse-first: build on what ALREADY exists — extend/compose the present pieces, take any "
        "duplicate or adjacent thing into scope; the least net-new.\n"
        "  - framework-first: the principled, complete, well-structured shape — do it PROPERLY, generalize "
        "the mechanism, leave a clean seam.\n"
        "  - radical-recompose: question the framing itself — a from-scratch recomposition that may "
        "discard the assumed shape, not an increment on it.\n"
        "\n"
        "Develop a COMPLETE approach (not a one-liner): what you would build/do, concretely. Then state "
        "honestly what it buys, what it costs, the real systems it touches, and its chief risk. Be "
        "specific and grounded in the constraints — a fabricated approach is worse than a modest honest one.\n"
        "\n"
        "Return ONLY JSON with exactly these fields:\n"
        '  "lens": echo back the lens you developed through (the `lens` from the unit),\n'
        '  "approach": the full approach — what to build/do, from your lens\'s bias, concretely,\n'
        '  "buys": what this approach buys (its upside),\n'
        '  "costs": what it costs (its downside / what you give up),\n'
        '  "touches": the real systems/files/seams it would change (grounded in the constraints),\n'
        '  "risk": its chief risk (what could go wrong, how reversible).\n'
        "\n"
        'Example (reuse-first): {"lens": "reuse-first", "approach": "Extend the existing event log with '
        'one additive field rather than a new store — append a kind marker and read it back through the '
        'present resolver.", "buys": "no new storage surface; existing callers keep working; least code", '
        '"costs": "the log row grows; a future heavy query may want its own index", "touches": '
        '"store/fs_store.py append path, the read-back in suite.py", "risk": "low — additive and '
        'git-reversible; worst case the marker is ignored by old readers"}'
    ),
    "output_schema": DevelopOptionOut,
    # DEFAULT input axis — ("utterance",) ONLY. `lens`/`question`/`constraints` are KEYS inside the unit
    # dict that run_items places at ctx["utterance"] (byte-identical default run_role framing), NOT
    # declared inputs. Mirrors verify_lens.py exactly (lens/change/bar in-unit) — declaring them as extra
    # inputs would trip the net-new compose path / leave dead declared-extras.
    "input_addresses": ("utterance",),
    "op": "generate",
    "trigger": (
        "fired over N lens-units by run_items (the MAP half of COMPOSITIONS ⑩, the option-panel) — one "
        "unit per lens, each {lens, question, constraints}; the N approaches are then scored + synthesized "
        "into a recommendation by the sibling reduce-role score_options via run_reduce(mode='role')."
    ),
    # C2.5 capability-query: a panelist wants a chat/json model. default_model None keeps the safe floor =
    # the resident swarm brain (the 4B) — the panel runs on it today, NO GPU window needed (COMPOSITIONS ⑩
    # is explicitly a no-GPU composition). A stronger model from the widened catalog (models_for_role) MAY
    # bind a lens as an ENHANCEMENT toward independence when a GPU window permits — never a requirement.
    "model_binding": {"requires": ["chat", "json"], "default_model": None, "default_base_url": None},
    # A panel CONTEXT cast (the cast-beyond-listening seam) — NOT the listening cast. An unknown mode
    # yields an EMPTY cast, so declaring this does not change listening; it is fired explicitly via
    # run_items in the composition. Mirrors register_element's {"registration"} / verify_lens's {"verification"}.
    "mode_scope": {"panel"},
    "rules": [],
    "render_hint": {"shape": "option", "lane": "develop_option"},
}
