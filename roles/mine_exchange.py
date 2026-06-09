"""roles/mine_exchange.py — the MINE_EXCHANGE role (COMPOSITIONS ③ · the TRANSCRIPT MINER, MAP half).

The MAP half of composition ③ (the TRANSCRIPT MINER): mine the previous-session transcripts into
structured self-improvement knowledge — every decision+rationale, every Tim-correction+what-I-did-wrong,
every bug+fix, every needs-tim, every named frustration, tagged with the recurring failure-PATTERN.
Self-improvement *from the record* (the incomplete-work / green-painting / dismissed-stranded-work lessons
Tim has given would self-surface here). THIS file is the ONE role that mines a SINGLE exchange; the "mine"
is the COMPOSITION — `run_items(mine_exchange, [..N exchange-units..])` fires the SAME role N times, once
per exchange, concurrent on the resident 4B swarm. The cross-exchange CLUSTER of the `pattern_tag`s into
recurring failure-pattern GROUPS is the REDUCE half (`run_reduce(mode="cluster")`) — that needs the
embedder window (bge-m3 @ :8001) and is the flagged FOLLOW-ON, not this beat.

★ THE EXCHANGE RIDES IN THE INPUT — that is what lets ONE role mine N exchanges (the axis-inversion, C 3/4).
   `run_items` places each unit at `ctx["utterance"]` (the role's primary input → run_role's DEFAULT
   byte-identical path, framed `f"Utterance: {unit}"`). So a unit is a small dict carrying ONE exchange:
   a Tim-message + my-response pair (+ optional session_id/ts for orientation), exactly as COMPOSITIONS ③
   specifies the exchange-unit `{session_id, ts, tim_message, my_response}`:
       {"tim_message": "<what Tim typed>", "my_response": "<what I replied>", "session_id": "...", "ts": "..."}
   The prompt holds the model to EXTRACTING the self-improvement signal from THAT one exchange.
   `input_addresses` stays the DEFAULT `("utterance",)`: `tim_message`/`my_response`/… are KEYS INSIDE the
   unit dict, NOT separate declared inputs (declaring them would trip the net-new compose path / leave dead
   declared-extras). Mirrors `verify_lens.py`'s `{lens, change, bar}` unit + `screen_reader.py`'s single-
   generate shape + `register_element.py`'s run_items-fanned MAP shape.

★ NOT A DRAWS-JURY (deliberate, file-disjoint). `verify_jury.py`/`confirm_registration.py`/the OTHER lane's
   `judge_mining.py` (the ③ CONFIRM jury — NOT this file) declare `draws:N` + a pure `verdict_rule`. This
   role does NOT — it is the MAP role (one extract per exchange), not the validation jury. Putting a
   `verdict_rule`/`draws` here would ship an unrequested mechanism. So: NO `draws`, NO `verdict_rule`.

★ THE FLOOR (AGENTS.md rule 9 · C9.2 · COMPOSITIONS ③ step 5). Advisory only — the miner EXTRACTS; it does
   NOT write memory files, never auto-mutates the repo, never self-approves. The downstream ACT (draft a
   `feedback-*.md` → I review + write — the memory write is MINE) is operator/me-gated and lives downstream.
   This file is a pure ROLE dict + a Pydantic output class: it emits no resolve/approve/dispatch, launches
   no `claude -p`. The extract is a JUDGEMENT of the record, not an action.

★ NO-FICTION / grounding-is-everything (the COMPOSITIONS invariant law 2). The model extracts ONLY what is
   IN the exchange — most exchanges have NO correction/bug/frustration, and those fields are then the empty
   string `""` (the richer-types optional default), NOT a fabricated one. The CONFIRM step (`judge_mining`,
   the OTHER lane) re-checks a sampled extract against the raw exchange; a fabricated extract is FLAGGED.

`op:generate` (default), `mode_scope:{"mining"}` (the cast-beyond-listening seam — a MINING context,
mirroring verify_lens's `{"verification"}` + register_element's `{"registration"}`; an UNKNOWN mode yields
an EMPTY cast, so adding this does NOT touch the listening cast). Fired over N exchange-units by `run_items`
(the composition's MAP). Model: the resident 4B swarm (`requires:["chat","json"]`, `default_model:None`).
"""
from pydantic import BaseModel


class MineExchangeOut(BaseModel):
    """ONE exchange's self-improvement extract (COMPOSITIONS ③ MAP). The RICHER field-types: strings +
    OPTIONALS — every signal field defaults to the empty string `""` (most exchanges carry only some of
    them; absence is `""`, NEVER a fabricated value — the no-fiction floor). `pattern_tag` is the ONE
    always-emitted field: a short kebab tag for the recurring theme, the key the downstream embed-CLUSTER
    reduce (the flagged follow-on) groups over. `complete()` validates/retries against this schema (C1.4),
    so a malformed extract fails loud, never silently passes."""
    decision: str = ""        # the decision / move made this exchange (or "" if none)
    rationale: str = ""       # WHY that decision (or "")
    tim_correction: str = ""  # what Tim corrected / pushed back on (or "")
    my_error: str = ""        # what I did wrong that prompted the correction (or "")
    bug_fix: str = ""         # a bug found + fixed this exchange (or "")
    needs_tim: str = ""        # a needs-tim / flag raised for the operator (or "")
    frustration: str = ""     # a frustration Tim named (or "")
    pattern_tag: str          # REQUIRED — a short kebab tag for the recurring theme (the cluster key)


ROLE = {
    "id": "mine_exchange",
    "label": "Mine exchange (self-improvement extract)",
    "description": (
        "Mines ONE conversation exchange (a Tim-message + my-response pair) into a structured "
        "self-improvement extract: the decision+rationale, any Tim-correction+my-error, any bug+fix, any "
        "needs-tim, any named frustration, tagged with the recurring failure-PATTERN. The exchange rides "
        "in the per-unit input, so run_items fans the SAME role over N exchanges — the MAP half of the "
        "transcript miner (COMPOSITIONS ③). Advisory: the miner extracts; the memory-write is mine; the "
        "cross-exchange pattern_tag CLUSTER is the downstream embed-reduce (the flagged follow-on)."
    ),
    "prompt_template": (
        "You are the TRANSCRIPT MINER. You read ONE conversation EXCHANGE between Tim (the founder/"
        "operator) and an AI agent (the assistant) and extract the SELF-IMPROVEMENT SIGNAL — what can be "
        "learned about how to work better with Tim from THIS one exchange.\n"
        "\n"
        "Your input is a unit containing the exchange:\n"
        "  - `tim_message`  — what Tim said/typed;\n"
        "  - `my_response`  — what the assistant replied;\n"
        "  - `session_id`/`ts` — orientation only (may be absent).\n"
        "\n"
        "Extract ONLY what is ACTUALLY IN the exchange. Most exchanges have NO correction, NO bug, and NO "
        "frustration — when a signal is absent, return the EMPTY STRING \"\" for that field. NEVER invent "
        "or guess a value to fill a field (a fabricated extract is worse than an empty one).\n"
        "\n"
        "The fields to extract (every one is the empty string \"\" unless the exchange clearly contains it, "
        "EXCEPT pattern_tag which you ALWAYS give):\n"
        "  - decision: the decision or move made this exchange (what was chosen/done), or \"\".\n"
        "  - rationale: WHY that decision was made (the reasoning), or \"\".\n"
        "  - tim_correction: what Tim corrected, pushed back on, or redirected, or \"\".\n"
        "  - my_error: what the assistant did wrong that prompted Tim's correction, or \"\".\n"
        "  - bug_fix: a concrete bug found AND fixed in this exchange, or \"\".\n"
        "  - needs_tim: a needs-tim / flag raised for the operator to decide or look at, or \"\".\n"
        "  - frustration: a frustration Tim explicitly named (something that annoyed or blocked him), or \"\".\n"
        "  - pattern_tag: ALWAYS give this — a short kebab-case tag naming the recurring theme of this "
        "exchange (the thing that, repeated across exchanges, is a pattern). Examples: "
        "'green-painting', 'summaries-not-detail', 'dismissed-stranded-work', 'over-cautious-gating', "
        "'verify-before-claiming', 'reuse-dont-parallel', 'build-on-existing', 'expand-dont-echo'. "
        "Coin a fitting kebab tag if none fits — keep it short and reusable.\n"
        "\n"
        "Be concrete and specific — quote or paraphrase the actual content, do not generalize into "
        "platitudes. Return ONLY JSON with exactly these eight fields.\n"
        "\n"
        'Example (a correction): {"decision": "switched to building on the existing registry instead of a '
        'new file", "rationale": "Tim flagged the parallel system", "tim_correction": "stop building a '
        'parallel store, extend the one that exists", "my_error": "started a second store rather than '
        'reusing the registry", "bug_fix": "", "needs_tim": "", "frustration": "AI keeps re-solving solved '
        'problems", "pattern_tag": "reuse-dont-parallel"}\n'
        'Example (a plain build move, no correction): {"decision": "fired the bounded mining run on the '
        'resident 4B", "rationale": "prove the role by use before reporting", "tim_correction": "", '
        '"my_error": "", "bug_fix": "", "needs_tim": "the embed-cluster of pattern_tags needs the embedder '
        'window", "frustration": "", "pattern_tag": "verify-by-use"}'
    ),
    "output_schema": MineExchangeOut,
    # DEFAULT input axis — ("utterance",) ONLY. tim_message/my_response/session_id/ts are KEYS inside the
    # unit dict that run_items places at ctx["utterance"] (byte-identical default run_role framing), NOT
    # declared inputs (declaring them would trip the net-new compose path / leave dead declared-extras).
    "input_addresses": ("utterance",),
    "trigger": (
        "fired over N exchange-units by run_items (the MAP half of COMPOSITIONS ③, the transcript miner) — "
        "one unit per exchange, each {tim_message, my_response, session_id?, ts?}; the cross-exchange "
        "pattern_tag CLUSTER into recurring failure-pattern groups is the downstream embed-reduce "
        "(run_reduce mode='cluster', needs the bge-m3 embedder window — the flagged follow-on)."
    ),
    # C2.5 capability-query: the miner wants a chat/json model. default_model None keeps the safe floor =
    # the resident swarm brain (the 4B) — the MAP runs on it today, NO GPU window needed (only the
    # downstream embed-cluster reduce needs the embedder). A STRONGER model MAY bind via models_for_role as
    # an ENHANCEMENT, never a requirement.
    "model_binding": {"requires": ["chat", "json"], "default_model": None, "default_base_url": None},
    # A MINING CONTEXT cast (the cast-beyond-listening seam) — NOT the listening cast. An unknown mode
    # yields an EMPTY cast, so declaring this does not change listening; it is fired explicitly via
    # run_items in the composition. Mirrors verify_lens's {"verification"} / register_element's {"registration"}.
    "mode_scope": {"mining"},
    "rules": [],
    "render_hint": {"shape": "extract", "lane": "mine_exchange"},
}
