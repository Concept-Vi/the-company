"""roles/ground_criterion.py — the GROUND_CRITERION role (COMPOSITIONS ⑦ · the spec-compiler's GROUND-CHECK).

The MAP half of the spec-compiler's GROUND half (composition ⑦, step 2c): on each candidate loop-prep
CRITERION, instead of trusting the EXPAND step's reuse-claim, fan a NO-FICTION reuse-CHECK over the
criteria. THIS file is the ONE role that grounds a SINGLE criterion; the "ground-check" is the
COMPOSITION — `run_items(ground_criterion, [..N criterion-units..])` fires the SAME role N times, once
per criterion, concurrent on the resident 4B swarm. The honest reuse-map of the whole drafted spec at
≈zero token-cost to me — the thing that keeps a compiled spec from claiming a reuse that doesn't exist.

★ THE CRITERION RIDES IN THE INPUT — that is what lets ONE role be N grounders (the axis-inversion, C 3/4).
   `run_items` places each unit at `ctx["utterance"]` (the role's primary input → run_role's DEFAULT
   byte-identical path, framed `f"Utterance: {unit}"`). So a unit is the two-faced CRITERION dict the
   spec-compiler's EXPAND step (`expand_criterion`, the OTHER lane) emits, exactly as COMPOSITIONS ⑦
   specifies the GROUND-CHECK input — `run_items(role="ground_criterion", items=<[{criterion, corpus_slice}, ...]>)`:
       {"id": "G3",
        "function": "<the behaviour the criterion builds, verifiable BY USE — no stub>",
        "form":     "<the design-system/product bar where a surface exists, else 'n/a'>",
        "files_touched":   ["<paths the criterion touches>"],
        "reuse_or_netnew": "reuse:<file>"  |  "net-new",     # the EXPAND step's CLAIM — what we CHECK
        "preserves":       "<what still works through the change>",
        "corpus_slice":    "<OPTIONAL retrieved slice of the project corpus on the criterion's concepts>"}
   The `corpus_slice` is OPTIONAL on purpose (the degrade the lane spec calls for): the corpus-grounded
   retrieve is a FUTURE embedder-window enhancement (① the repo exocortex, GPU window) — NOT required
   now. When it is absent, the role degrades to NAMING the file it is confident exists from the repo +
   marking its confidence in `note` (honest, never invented). `input_addresses` stays the DEFAULT
   `("utterance",)`: `id`/`function`/`form`/`files_touched`/`reuse_or_netnew`/`preserves`/`corpus_slice`
   are KEYS INSIDE the unit dict, NOT separate declared inputs (declaring them would trip the net-new
   compose path / leave dead declared-extras). Mirrors `roles/verify_lens.py`'s single-generate shape +
   `roles/register_element.py`'s run_items-fanned MAP shape.

★ NO-FICTION IS THE MAKE-OR-BREAK (the spec's one truth must not be corrupted). A drafted criterion's
   reuse-claim must cite a REAL file (AGENTS.md rule 8 — author from the registry, never invent; the
   build-loop's NO-FICTION law). So the role's whole job is: does the thing the criterion BUILDS-ON
   actually EXIST? If it does → `grounded:"reuse"` + the real `cite` (a `file:symbol`, e.g.
   `runtime/cognition.py:run_items`). If it does NOT (un-built, would-be net-new) → `grounded:"net-new"`
   + an EMPTY cite — NEVER an invented reuse to make the spec look more reuse-heavy than it is. The
   `note` carries the confidence + the reasoning so I (Opus) + Tim can steer a low-confidence call.

★ NOT A DRAWS-JURY (deliberate, file-disjoint). The CONFIRM jury of ⑦ ("covers the seed? any reuse-claim
   unverifiable?") is a SEPARATE downstream step (a `draws:N`+`verdict_rule` jury, like `verify_jury`),
   NOT this role. This role is a single-generate MAP grounder (one draw per criterion). So: NO `draws`,
   NO `verdict_rule` (declaring either would make it a jury + trip the jury-must-have-verdict_rule gate
   `runtime/roles.py:_build_role`). Mirrors `verify_lens`'s "NOT a draws-jury" stance.

★ THE FLOOR (AGENTS.md rule 9 · the COMPOSITIONS two invariant laws · cognition_governance). Advisory
   only — a grounder NEVER builds; it PROPOSES a reuse-verdict, and the spec-compiler's floor is "a
   draft, never a build off an unconfirmed compiled spec." This file is a pure ROLE dict + a Pydantic
   output class: it emits no resolve/approve/dispatch, launches no `claude -p`. The verdict is a
   JUDGEMENT about the spec, not an action.

`op:generate` (default), `mode_scope:{"spec"}` (the cast-beyond-listening seam — a spec-compiler context,
mirroring `verify_lens`'s `{"verification"}` + `register_element`'s `{"registration"}`; an UNKNOWN mode
yields an EMPTY cast, so adding this does NOT touch the listening cast). Fired over N criterion-units by
`run_items` (the composition's MAP, COMPOSITIONS ⑦ step 2c).
"""
from typing import Literal

from pydantic import BaseModel


class GroundCriterionOut(BaseModel):
    """One criterion's grounding verdict — does the thing it builds-ON actually exist? The `grounded`
    vocabulary is CLOSED (reuse | net-new) so the downstream triad_synth reduce reads an exact token
    (the reuse-map is assembled from these); enforcing it client-side is the fail-loud house style
    (complete() validates/retries against this schema, C1.4). NO-FICTION: a `reuse` MUST carry a real
    `cite`; a `net-new` carries an EMPTY cite — never an invented reuse."""
    criterion_id: str                       # ECHO the criterion's id (from the unit) — keys the reuse-map
    grounded: Literal["reuse", "net-new"]   # the closed verdict: build-on EXISTS (reuse) | un-built (net-new)
    cite: str = ""                          # if reuse: a REAL file:symbol (e.g. runtime/cognition.py:run_items); else ""
    note: str = ""                          # the confidence + reasoning (which file you believe + how sure)


ROLE = {
    "id": "ground_criterion",
    "label": "Ground criterion (reuse-check)",
    "description": (
        "Grounds ONE loop-prep criterion — does the thing it builds-ON actually EXIST? Returns "
        "grounded:'reuse' + a REAL file:symbol cite, or grounded:'net-new' + an empty cite (NEVER an "
        "invented reuse). The criterion rides in the per-unit input, so run_items fans the SAME role over "
        "N criteria — the MAP half of the spec-compiler's NO-FICTION ground-check (COMPOSITIONS ⑦, 2c). "
        "Advisory: a grounder proposes a verdict about the spec; it never builds."
    ),
    "prompt_template": (
        "You are the GROUND-CHECK of a SPEC-COMPILER. You ground ONE loop-prep CRITERION: you check "
        "whether the thing this criterion BUILDS-ON actually EXISTS in the project, so the compiled spec "
        "never claims a reuse that isn't real (NO FICTION).\n"
        "\n"
        "Your input is ONE criterion — a unit with these keys:\n"
        "  - `id`               — the criterion's id (echo it back in `criterion_id`);\n"
        "  - `function`         — the behaviour the criterion builds (what it must DO, verifiable by use);\n"
        "  - `form`             — the product/design-system bar where a surface exists (else 'n/a');\n"
        "  - `files_touched`    — the files the criterion would touch;\n"
        "  - `reuse_or_netnew`  — the EXPAND step's CLAIM ('reuse:<file>' or 'net-new') — this is the "
        "claim you are CHECKING, not something to trust;\n"
        "  - `preserves`        — what still works through the change;\n"
        "  - `corpus_slice`     — OPTIONAL: a retrieved slice of the project corpus on this criterion's "
        "concepts. It MAY be absent. When present, ground your verdict in it. When ABSENT, name the file "
        "you are CONFIDENT exists from your knowledge of the repo, and state your confidence in `note` — "
        "do NOT invent a file you are unsure of.\n"
        "\n"
        "Decide ONE thing: does the thing this criterion builds-ON already EXIST?\n"
        "  - If it EXISTS (the criterion extends/reuses real code already in the repo) → grounded = "
        "\"reuse\", and put the REAL file (a 'file:symbol', e.g. runtime/cognition.py:run_items, or a "
        "bare file path if you cannot name the symbol) in `cite`.\n"
        "  - If it does NOT exist yet (the criterion would build something un-built) → grounded = "
        "\"net-new\", and leave `cite` an empty string \"\".\n"
        "\n"
        "NO FICTION (the make-or-break): NEVER invent a reuse to make the spec look more reuse-heavy. If "
        "you are not confident a file exists, mark it net-new (or reuse with a LOW confidence stated in "
        "`note`) — an honest net-new is correct; a fabricated cite is a failure. Put your confidence and "
        "reasoning (which file you believe + how sure you are) in `note`.\n"
        "\n"
        "Return ONLY JSON with exactly these fields:\n"
        '  "criterion_id": echo the criterion\'s id,\n'
        '  "grounded": EXACTLY one of the two lowercase tokens "reuse" | "net-new",\n'
        '  "cite": a REAL file:symbol if reuse (empty string "" if net-new),\n'
        '  "note": your confidence + reasoning (which file, how sure).\n'
        "\n"
        'Example (reuse): {"criterion_id": "G3", "grounded": "reuse", "cite": '
        '"runtime/cognition.py:run_items", "note": "high confidence — the MAP fan-over-N-units engine '
        'already exists and this criterion extends it"}\n'
        'Example (net-new): {"criterion_id": "G7", "grounded": "net-new", "cite": "", "note": "no '
        'embedder-window retrieve path is built yet; this would be net-new (medium confidence)"}'
    ),
    "output_schema": GroundCriterionOut,
    # DEFAULT input axis — ("utterance",) ONLY. `id`/`function`/`form`/`files_touched`/`reuse_or_netnew`/
    # `preserves`/`corpus_slice` are KEYS inside the unit dict that run_items places at ctx["utterance"]
    # (byte-identical default run_role framing), NOT declared inputs (declaring them would trip the
    # net-new compose path / leave dead declared-extras). Mirrors verify_lens's default axis.
    "input_addresses": ("utterance",),
    "trigger": (
        "fired over N criterion-units by run_items (the MAP half of COMPOSITIONS ⑦ step 2c, the spec-"
        "compiler's ground-check) — one unit per candidate criterion; the grounded verdicts are then "
        "assembled by run_reduce(mode='role', role='triad_synth') into the loop-prep triad (the reuse-map "
        "is the reduce of these), and a downstream CONFIRM jury checks coverage vs the seed."
    ),
    # C2.5 capability-query: a grounder wants a chat/json model. default_model None keeps the safe floor =
    # the resident swarm brain (the 4B) — the composition runs on it today, no GPU window needed (⑦ is one
    # of the non-embed compositions). A STRONGER model from the widened catalog (models_for_role) MAY bind
    # the ground-check as an ENHANCEMENT toward fewer fabricated cites when a GPU window permits — never a
    # requirement.
    "model_binding": {"requires": ["chat", "json"], "default_model": None, "default_base_url": None},
    # A spec-compiler CONTEXT cast (the cast-beyond-listening seam) — NOT the listening cast. An unknown
    # mode yields an EMPTY cast, so declaring this does not change listening; it is fired explicitly via
    # run_items in the composition. Mirrors verify_lens's {"verification"} + register_element's {"registration"}.
    "mode_scope": {"spec"},
    "rules": [],
    "render_hint": {"shape": "grounded", "lane": "ground_criterion"},
}
