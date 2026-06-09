"""roles/judge_mining.py — the JUDGE_MINING role (COMPOSITIONS ③ · the transcript-miner's no-fiction CONFIRM gate).

The CONFIRM half of composition ③ (the TRANSCRIPT MINER): ③ MAPs `mine_exchange` over conversation
exchanges → structured self-improvement extracts (decision/rationale/tim_correction/my_error/bug_fix/
needs_tim/frustration/pattern_tag). Before any of those extracts is clustered into failure-patterns or
DRAFTED into a `feedback-*.md` memory file (the ⑤-step), the no-fiction law (the second invariant of the
whole COMPOSITIONS circuit) must bite: **did the miner fabricate a claim — a decision, a correction, a
frustration — that is NOT actually in the raw exchange?** THIS role is that gate: it validates ONE
`mine_exchange` extract against its RAW source exchange and answers whether every CLAIMED (non-empty)
field is genuinely supported by the source text.

★ THE PAIR RIDES IN THE INPUT — the axis-inversion (C 3/4), exactly as verify_lens.py does for its lens.
   The unit is a small dict carrying the extract AND the raw exchange it claims to describe:
       {"extract": {<a mine_exchange output>}, "raw_exchange": "<the Tim-message + my-response source text>"}
   `run_items`/`run_role` places that unit at `ctx["utterance"]` (the role's primary input → run_role's
   DEFAULT byte-identical framing, `f"Utterance: {unit}"`). So `input_addresses` stays the DEFAULT
   `("utterance",)`: `extract`/`raw_exchange` are KEYS INSIDE the unit dict, NOT separate declared inputs
   (declaring them would trip the net-new compose path / leave dead declared-extras). Mirrors
   verify_lens.py's single-generate, unit-carries-the-payload shape (and screen_reader.py before it).

★ NOT A DRAWS-JURY (deliberate, and distinct from this composition's siblings). confirm_registration.py
   and verify_jury.py declare `draws:N` + a pure `verdict_rule` (N varied draws of ONE classification →
   an in-role quorum). This role does NOT — it is a SINGLE-GENERATE validator, ONE judgement of ONE
   extract, exactly the spec'd shape. It declares NO `draws` and NO `verdict_rule` (adding a verdict_rule
   here would, like verify_lens warns, collide with any downstream tally and ship an unrequested
   mechanism). The composition fires it over a SAMPLE of extracts via `run_items` (③ step 4), one
   judgement per extract; any cross-sample rollup is a downstream deterministic reduce, not this role.

★ THE NO-FICTION POSTURE — bias toward FAIL (the dangerous error here is the false NEGATIVE: passing a
   fabrication). A non-empty claimed field is `grounded` ONLY if the judge can point to actual text in
   `raw_exchange` that supports it; if it cannot LOCATE that support, the verdict is `grounded:false` and
   the offending field is NAMED in `unsupported`. This mirrors verify_lens's adversarial-disprove
   default-to-fail. EMPTY fields claim NOTHING — the `mine_exchange` schema defaults most fields to ""
   (no bug_fix this exchange, no frustration, etc.), so an empty `""` is vacuously grounded and is NEVER
   counted as unsupported (else every faithful extract would spuriously fail).

★ THE FLOOR (AGENTS.md rule 9 · the COMPOSITIONS invariant 1). Advisory only — a judge NEVER commits,
   NEVER drafts the memory file, NEVER writes. This file is a pure ROLE dict + a Pydantic output class:
   it emits no resolve/approve/dispatch, launches no `claude -p`. The verdict is a JUDGEMENT; the act on
   it (FLAG, never drop — variance-not-error) lives downstream, and the memory write is the agent's, after
   confirm (③ step 5: "drafts, I confirm before writing"). E4 caveat applies: this is a SINGLE-4B SOFT
   judgement (variance, not independent error) — it strengthens the verdict + flags, it is not a hard proof; a
   stronger model from the widened catalog (C2.5 / models_for_role) MAY bind it as an enhancement when a
   GPU window permits, never a requirement.

`op:generate` (default), `mode_scope:{"mining"}` (the cast-beyond-listening seam — a MINING context,
mirroring verify_lens's `{"verification"}` and register_element's `{"registration"}`; an UNKNOWN mode
yields an EMPTY cast, so declaring this does NOT touch the listening cast). Fired over a sample of extracts
by `run_items` (③'s CONFIRM step).
"""
from pydantic import BaseModel


class JudgeMiningOut(BaseModel):
    """One judgement of ONE mine_exchange extract against its raw source exchange — the no-fiction verdict.

    The verdict is the boolean `grounded` (is every NON-EMPTY claimed field actually supported by the raw
    exchange?), the `unsupported` field NAMES the first/worst claim that has no basis in the source (the
    "why" for a fail — empty "" when grounded). The fields are TIED: grounded==false ⟹ unsupported is non-empty (names the
    ungrounded field); grounded==true ⟹ unsupported == "". NO confidence float (G16, the no-confidence
    law) — the boolean verdict + the named unsupported field ARE the evidence, not a self-rated certainty.
    complete() validates/retries against this schema (fail-loud, C1.4)."""
    grounded: bool       # is EVERY non-empty claimed field genuinely supported by the raw exchange?
    unsupported: str = ""  # the claim/field that is NOT grounded (which one + why), or "" when grounded


ROLE = {
    "id": "judge_mining",
    "label": "Judge mining (no-fiction)",
    "description": (
        "Validates ONE mine_exchange extract against its RAW source exchange — the transcript-miner's "
        "no-fiction gate (COMPOSITIONS ③ CONFIRM). Answers whether every NON-EMPTY claimed field "
        "(decision/rationale/tim_correction/my_error/bug_fix/needs_tim/frustration/pattern_tag) is "
        "genuinely supported by the source text; biases toward fail (the dangerous error is passing a "
        "fabrication). Advisory: a judge never commits or drafts; FLAG, never drop (variance-not-error)."
    ),
    "prompt_template": (
        "You are the NO-FICTION JUDGE of a transcript-mining pipeline. A miner read ONE conversation "
        "exchange (a message from Tim + my response) and produced a structured EXTRACT of it. Your one "
        "job: decide whether the extract is GROUNDED — whether every claim it makes is actually supported "
        "by the raw exchange, with NO fabrication.\n"
        "\n"
        "Your input is a unit containing two things:\n"
        "  - `extract`      — the miner's structured output, an object with these fields (each is a string, "
        "and any field MAY be the empty string \"\" meaning 'nothing of this kind this exchange'): "
        "decision, rationale, tim_correction, my_error, bug_fix, needs_tim, frustration, pattern_tag;\n"
        "  - `raw_exchange` — the source text of the exchange the extract claims to describe.\n"
        "\n"
        "How to judge (this is a NO-FICTION gate — be strict, and bias toward FAIL):\n"
        "  1. Consider ONLY the NON-EMPTY fields of `extract`. An empty field (\"\") claims NOTHING — it is "
        "automatically fine and is NEVER a reason to fail. Do not penalise empty fields.\n"
        "  2. For each NON-EMPTY field, look for ACTUAL TEXT in `raw_exchange` that supports the claim. A "
        "claimed `tim_correction` must be something Tim actually corrected in the raw exchange; a claimed "
        "`bug_fix` must be a bug actually found+fixed in it; a claimed `decision` must be a move actually "
        "made; `pattern_tag` must reflect a theme genuinely present. If you can point to supporting text, "
        "that field is grounded.\n"
        "  3. If you CANNOT locate support in `raw_exchange` for a non-empty field — if it appears "
        "invented, contradicted, or read-in — that field is UNGROUNDED. When in doubt about whether the "
        "source supports a claim, treat it as UNGROUNDED (false negatives are the safe error here).\n"
        "\n"
        "Verdict (the fields are TIED — keep them consistent):\n"
        "  - `grounded` is true ONLY if EVERY non-empty field is supported; if ANY non-empty field is "
        "ungrounded, `grounded` is false.\n"
        "  - if `grounded` is false, `unsupported` MUST name the ungrounded field and say briefly why it "
        "is not supported by the raw exchange; if `grounded` is true, `unsupported` MUST be the empty "
        "string \"\".\n"
        "\n"
        "Return ONLY JSON with exactly these fields:\n"
        '  "grounded": boolean,\n'
        '  "unsupported": the ungrounded field + why (a short phrase), or "" when grounded.\n'
        "\n"
        'Example (faithful — Tim did correct me, the extract reflects it): {"grounded": true, '
        '"unsupported": ""}\n'
        'Example (fabricated — extract claims a tim_correction with no basis in the raw exchange): '
        '{"grounded": false, "unsupported": "tim_correction: the raw exchange contains no correction from '
        'Tim — he asked a question and I answered; nothing was corrected"}'
    ),
    "output_schema": JudgeMiningOut,
    # DEFAULT input axis — ("utterance",) ONLY. `extract`/`raw_exchange` are KEYS inside the unit dict that
    # run_items/run_role places at ctx["utterance"] (byte-identical default run_role framing), NOT declared
    # inputs (declaring them would trip the net-new compose path / leave dead declared-extras).
    "input_addresses": ("utterance",),
    "trigger": (
        "fired over a SAMPLE of mine_exchange extracts by run_items (the CONFIRM step of COMPOSITIONS ③, "
        "the transcript miner) — one unit per sampled extract, each {extract, raw_exchange}; an ungrounded "
        "verdict FLAGS the extract (never dropped — variance-not-error), gating the cluster→draft step."
    ),
    # C2.5 capability-query: a judge wants a chat/json model. default_model None keeps the safe floor =
    # the resident swarm brain (the 4B) — the composition runs on it today, no GPU window needed. A
    # STRONGER model from the widened catalog (models_for_role) MAY bind this no-fiction gate as an
    # ENHANCEMENT toward independent error when a GPU window permits — never a requirement (E4 caveat).
    "model_binding": {"requires": ["chat", "json"], "default_model": None, "default_base_url": None},
    # A MINING context cast (the cast-beyond-listening seam) — NOT the listening cast. An unknown mode
    # yields an EMPTY cast, so declaring this does not change listening; it is fired explicitly via
    # run_items in the composition. Mirrors verify_lens's {"verification"} and the mine lane's {"mining"}.
    "mode_scope": {"mining"},
    "rules": [],
    "render_hint": {"shape": "verdict", "lane": "judge_mining"},
}
