"""roles/verify_lens.py — the VERIFY_LENS role (COMPOSITIONS ⑥ · the reusable verification jury).

The MAP half of composition ⑥ (the VERIFICATION JURY): on any change, instead of ONE serialized
verification pass (mine), fan a **jury of distinct LENSES** of free swarm-models over the change, then
tally them deterministically. THIS file is the ONE role that does a SINGLE lens; the "jury" is the
COMPOSITION — `run_items(verify_lens, [..N lens-units..])` fires the SAME role N times, once per lens,
concurrent on the resident 4B swarm. Six parallel angles on every commit at ≈zero token-cost to me.

★ THE LENS RIDES IN THE INPUT — that is what lets ONE role be N jurors (the axis-inversion, C 3/4).
   `run_items` places each unit at `ctx["utterance"]` (the role's primary input → run_role's DEFAULT
   byte-identical path, framed `f"Utterance: {unit}"`). So a unit is a small dict carrying the lens id +
   the change-under-test + the bar for THAT lens, exactly as COMPOSITIONS ⑥ specifies:
       {"lens": "correctness",          "change": "<diff/criterion/claim>", "bar": "<the criterion>"}
       {"lens": "adversarial-disprove", "change": "<diff/criterion/claim>", "bar": "<find a breaking input>"}
   The prompt holds the model to ITS lens ONLY (the one named in the unit) — fan the same role over N
   lenses and each draw judges through one angle. `input_addresses` stays the DEFAULT `("utterance",)`:
   `lens`/`change`/`bar` are KEYS INSIDE the unit dict, NOT separate declared inputs (declaring them
   would trip the net-new compose path / leave dead declared-extras). Mirrors `screen_reader.py`'s
   single-generate shape + `register_element.py`'s run_items-fanned MAP shape.

★ NOT A DRAWS-JURY (deliberate, file-disjoint). `verify_jury.py`/`confirm_registration.py` declare
   `draws:N` + a pure `verdict_rule` (N varied draws of ONE classification → an in-role quorum). This
   role does NOT — its "jury" is the CROSS-LENS fan (N distinct lenses, one draw each), and the VERDICT
   TALLY over the lenses (green iff every lens passes · any fail→fail · any uncertain→FLAG) is a
   DETERMINISTIC reduce-rule that lives in the OTHER lane — `mcp_face`'s `_REDUCE_RULES` (run via
   `run_reduce(mode="rule")`). Putting a verdict_rule here would COLLIDE with that tally and ship an
   unrequested mechanism. So: NO `draws`, NO `verdict_rule`. The tally reduce-rule is the next-beat
   follow-on (a small additive `_REDUCE_RULES` entry); until then verify_lens is usable now via
   `run_items` + an existing reduce, or a manual tally over the per-lens verdicts.

★ THE FLOOR (AGENTS.md rule 9 · C9.2). Advisory only — a juror NEVER commits; I commit. This file is a
   pure ROLE dict + a Pydantic output class: it emits no resolve/approve/dispatch, launches no
   `claude -p`. The verdict is a JUDGEMENT, not an action (the deterministic tally + any action on it
   live downstream, operator-gated). The adversarial-disprove lens is the variance-not-error gate built
   in: it is told to DEFAULT to fail/uncertain if it can construct ANY input that breaks the change.

`op:generate` (default), `mode_scope:{"verification"}` (the cast-beyond-listening seam — a verification
context, mirroring register_element's `{"registration"}`; an UNKNOWN mode yields an EMPTY cast, so adding
this does NOT touch the listening cast). Fired over N lens-units by `run_items` (the composition's MAP).
"""
from typing import Literal

from pydantic import BaseModel


# The closed lens vocabulary (COMPOSITIONS ⑥). Declared as visible DATA (not buried in prose) so the
# set is one place — the same six the composition's run_items call fans, and the drift home names.
LENSES = (
    "correctness",          # does the change DO what it claims — logically right against the bar?
    "floor",                # does it stay within the floor — no resolve/approve/dispatch, no claude -p?
    "drift",                # is the self-description updated (AGENTS.md/MAP.md/STATE.md/module constitution)?
    "matches-criterion",    # does it actually satisfy the stated criterion (FUNCTION + FORM), not adjacent?
    "registry-is-truth",    # no hardcoded list/value where a registry is the source of truth?
    "adversarial-disprove", # can ANY input be constructed that breaks the change? (default fail/uncertain)
)


class VerifyLensOut(BaseModel):
    """One lens's judgement of ONE change-under-test. The verdict vocabulary is CLOSED so the downstream
    deterministic tally (green-iff-all-pass / any-fail→fail / any-uncertain→FLAG, the OTHER lane's
    `_REDUCE_RULES` reduce-rule) is an exact-token reduce — enforcing it client-side is the fail-loud
    house style (complete() validates/retries against this schema, C1.4)."""
    lens: str                                       # ECHO the lens this draw judged through (from the unit)
    verdict: Literal["pass", "fail", "uncertain"]   # the closed verdict vocabulary (the tally reduces over)
    evidence: str                                   # the concrete reason for the verdict (cite the change)
    breaking_case: str = ""                         # adversarial-disprove: the input that breaks it; else ""


ROLE = {
    "id": "verify_lens",
    "label": "Verify (one lens)",
    "description": (
        "Judges ONE change-under-test through ONE LENS (correctness · floor · drift · matches-criterion · "
        "registry-is-truth · adversarial-disprove). The lens rides in the per-unit input, so run_items "
        "fans the SAME role over N lenses — the MAP half of the verification jury (COMPOSITIONS ⑥). "
        "Advisory: a juror never commits; the deterministic verdict tally is a downstream reduce-rule."
    ),
    "prompt_template": (
        "You are ONE JUROR of a VERIFICATION JURY. You judge a CHANGE-UNDER-TEST through exactly ONE "
        "LENS, and you judge through THAT LENS ONLY — never another angle.\n"
        "\n"
        "Your input is a unit containing three things:\n"
        "  - `lens`   — the ONE lens you must judge through (one of: correctness, floor, drift, "
        "matches-criterion, registry-is-truth, adversarial-disprove);\n"
        "  - `change` — the change-under-test: a diff, a criterion, or a claim;\n"
        "  - `bar`    — the bar you hold the change to for THIS lens.\n"
        "\n"
        "What each lens means (judge ONLY the one named in `lens`):\n"
        "  - correctness: does the change actually DO what it claims, logically, against the bar?\n"
        "  - floor: does it stay within the floor — emits NO resolve/approve/dispatch, launches NO "
        "claude -p, never self-approves or auto-mutates the repo?\n"
        "  - drift: is the self-description updated for this change (the relevant AGENTS.md / MAP.md / "
        "STATE.md / module constitution reflects it)?\n"
        "  - matches-criterion: does it satisfy the STATED criterion (its FUNCTION and its FORM bar), "
        "not merely something adjacent?\n"
        "  - registry-is-truth: is there NO hardcoded list/value where a registry is the source of "
        "truth (the value comes from the registry, never invented or pinned in code)?\n"
        "  - adversarial-disprove: try to DISPROVE the change — construct an input/case that BREAKS it. "
        "You DEFAULT to fail (or uncertain) if you can construct ANY breaking case; only pass if you "
        "genuinely cannot find one. When you find one, put it in `breaking_case`.\n"
        "\n"
        "Hold the change to its `bar` for your lens, strictly. Be concrete — cite what in the change "
        "made you decide.\n"
        "\n"
        "Return ONLY JSON with exactly these fields:\n"
        '  "lens": echo back the lens you judged through (the `lens` from the unit),\n'
        '  "verdict": EXACTLY one of the three lowercase tokens "pass" | "fail" | "uncertain",\n'
        '  "evidence": a concrete one- or two-line reason, citing the change,\n'
        '  "breaking_case": for the adversarial-disprove lens, the input/case that breaks the change '
        '(empty string "" if none, or for any other lens).\n'
        "\n"
        'Example (correctness): {"lens": "correctness", "verdict": "pass", "evidence": "the function '
        'returns the documented shape for every branch in the diff", "breaking_case": ""}\n'
        'Example (adversarial-disprove): {"lens": "adversarial-disprove", "verdict": "fail", "evidence": '
        '"an empty input list is not handled", "breaking_case": "items=[] → IndexError on line 12"}'
    ),
    "output_schema": VerifyLensOut,
    # DEFAULT input axis — ("utterance",) ONLY. `lens`/`change`/`bar` are KEYS inside the unit dict that
    # run_items places at ctx["utterance"] (byte-identical default run_role framing), NOT declared inputs.
    "input_addresses": ("utterance",),
    "trigger": (
        "fired over N lens-units by run_items (the MAP half of COMPOSITIONS ⑥, the verification jury) — "
        "one unit per lens, each {lens, change, bar}; the cross-lens verdicts are tallied by a "
        "downstream deterministic reduce-rule (mcp_face _REDUCE_RULES, the next-beat follow-on)."
    ),
    # C2.5 capability-query: a juror wants a chat/json model. default_model None keeps the safe floor =
    # the resident swarm brain (the 4B) — the composition runs on it today, no GPU window needed. A
    # STRONGER model from the widened catalog (models_for_role) MAY bind a correctness-critical lens as an
    # ENHANCEMENT toward independent error when a GPU window permits — never a requirement.
    "model_binding": {"requires": ["chat", "json"], "default_model": None, "default_base_url": None},
    # A verification CONTEXT cast (the cast-beyond-listening seam) — NOT the listening cast. An unknown
    # mode yields an EMPTY cast, so declaring this does not change listening; it is fired explicitly via
    # run_items in the composition. Mirrors register_element's {"registration"}.
    "mode_scope": {"verification"},
    "rules": [],
    "render_hint": {"shape": "lens", "lane": "verify_lens"},
}
