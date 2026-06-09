"""roles/expand_criterion.py — the EXPAND_CRITERION role (COMPOSITIONS ⑦ · the SPEC-COMPILER, step 2b · MAP).

The MAP half of composition ⑦ (the SPEC-COMPILER): each candidate criteria-GROUP (emitted by the 1×1
`decompose_seed`, step 2a) → a full TWO-FACED loop-prep CRITERION. THIS file is the ONE role that expands a
SINGLE group; the expansion is the COMPOSITION — `run_items(expand_criterion, [..N group-units..])` fires
the SAME role N times, once per group, concurrent on the resident 4B swarm. The loop-prep I keep building
by hand, compiled (COMPOSITIONS ⑦ "the loop-prep I keep building by hand, compiled").

★ THE GROUP RIDES IN THE INPUT — that is what lets ONE role expand N groups (the axis-inversion, C 3/4).
   `run_items` places each unit at `ctx["utterance"]` (the role's primary input → run_role's DEFAULT
   byte-identical path, framed `f"Utterance: {unit}"` — `runtime/cognition.py:1200,295`). So a unit is the
   group dict the decompose step emitted — `{group_id, what, systems_touched}` — and the role expands THAT
   one group into one criterion. `input_addresses` stays the DEFAULT `("utterance",)`: `group_id`/`what`/
   `systems_touched` are KEYS INSIDE the unit dict, NOT separate declared inputs (declaring them would trip
   the net-new compose path / leave dead declared-extras). Mirrors `verify_lens.py`'s `{lens, change, bar}`
   unit + `mine_exchange.py`'s `{tim_message, my_response}` unit + `register_element.py`'s run_items-fanned
   MAP shape. (The per-unit corpus-slice + few-shot that COMPOSITIONS ⑦ step 1 names as richer grounding
   ride INTO the same unit when the cascade supplies them — the unit IS the per-unit-varying context; the
   corpus-grounded retrieve is the embedder-window enhancement, NOT required for this beat.)

★ BOTH FACES ARE MANDATORY — FORM is half of done (AGENTS.md rule 9). The two-faced criterion is the
   loop-prep BAR: every criterion carries a FUNCTION (the behaviour, verifiable BY USE — no stub) AND a
   FORM (the design-system/product bar where an operator-facing surface exists). You may NOT write a
   function-only criterion: where a surface exists, FORM is required; where the change is purely backend
   (no operator-facing surface), FORM is the literal "n/a" (honest, not omitted). This mirrors how the
   real loop-prep triads (`build-prep/cognition-engine/COMPLETION-CRITERIA.md`) carry FUNCTION + a separate
   FORM note per criterion.

★ NO-FICTION on the reuse-claim (the COMPOSITIONS invariant law 2 · the brief's make-or-break). The
   `reuse_or_netnew` field is `reuse:<file>` ONLY when a real file to build on is confidently known; else
   the literal `net-new`. NEVER invent a reuse path — an un-built thing is `net-new`, never a fabricated
   `reuse:`. CRUCIAL: this role's reuse-claim is PRELIMINARY/proposed — the AUTHORITATIVE no-fiction
   reuse-check (does the cited file actually exist + actually provide the build-on?) is the OTHER lane's
   `ground_criterion` (COMPOSITIONS ⑦ step 2c), which re-reads each expanded criterion against the corpus
   and confirms `reuse`(cite) vs `net-new`(honest). So this role PROPOSES the reuse-claim at the seed-
   author's grain and defers the grounding downstream — exactly as `register_element.py` proposes a dossier
   and defers the refcheck/jury to RG6. Do NOT absorb ground_criterion's job; when unsure, `net-new` is the
   safe, honest default.

★ THE FLOOR (AGENTS.md rule 9 · C9.2 · COMPOSITIONS ⑦ step 5). Advisory only — this role DRAFTS a
   criterion; it never builds, never auto-mutates the repo, never self-approves. The triad is PROPOSED → me
   → Tim steers ("a draft, never a build off an unconfirmed compiled spec"). This file is a pure ROLE dict
   + a Pydantic output class: it emits no resolve/approve/dispatch, launches no `claude -p`. The criterion
   is a JUDGEMENT, not an action. (roles/* is in the floor source-invariant scan COG_SOURCES — pure data +
   prompt.)

`op:generate` (default), `mode_scope:{"spec"}` (the cast-beyond-listening seam — a SPEC-compiler context,
same as decompose_seed; an UNKNOWN mode yields an EMPTY cast, so adding this does NOT touch the listening
cast). Fired over N group-units by `run_items` (the composition's MAP, step 2b). Its output criteria feed
`ground_criterion` (2c, the OTHER lane) + `triad_synth` (3). Model: the resident 4B swarm
(`requires:["chat","json"]`, `default_model:None` — no GPU window needed).
"""
from pydantic import BaseModel


class ExpandCriterionOut(BaseModel):
    """ONE candidate group → one full TWO-FACED loop-prep criterion (COMPOSITIONS ⑦ MAP). The loop-prep
    bar made a schema: FUNCTION and FORM are BOTH first-class fields (FORM is half of done — `"n/a"` only
    where no operator-facing surface exists); `reuse_or_netnew` is the no-fiction reuse-claim (`reuse:<file>`
    only when a real file is confidently known, else `net-new` — preliminary, ground-checked downstream by
    the OTHER lane's ground_criterion); `preserves` is the no-regression face (what still works through the
    change). `complete()` validates/retries against this schema (C1.4), so a malformed criterion fails loud,
    never silently passes."""
    id: str                     # a short id for the criterion (the group's id or a refinement of it)
    function: str               # the BEHAVIOUR — verifiable BY USE, no stub (the FUNCTION face)
    form: str                   # the design-system/product bar where a surface exists, else the literal "n/a"
    files_touched: list[str]    # the real files/modules the criterion would touch (paths)
    reuse_or_netnew: str        # 'reuse:<file>' (a real file to build on) | 'net-new' — NO fabricated reuse
    preserves: str              # what still works through the change (the no-regression face)


ROLE = {
    "id": "expand_criterion",
    "label": "Expand criterion (group → two-faced criterion)",
    "description": (
        "Expands ONE candidate criteria-GROUP (from decompose_seed) into a full TWO-FACED loop-prep "
        "CRITERION — FUNCTION (behaviour, verifiable by use, no stub) AND FORM (the product/design-system "
        "bar where a surface exists, else 'n/a'), plus files_touched · reuse_or_netnew (honest, no fabricated "
        "reuse) · preserves. The MAP half (step 2b) of the SPEC-COMPILER (COMPOSITIONS ⑦): the group rides "
        "in the per-unit input, so run_items fans the SAME role over N groups. Advisory: it drafts criteria; "
        "the reuse-claim is preliminary (ground-checked by the OTHER lane's ground_criterion); the triad is "
        "PROPOSED → me → Tim — never a build off an unconfirmed spec."
    ),
    "prompt_template": (
        "You are the EXPAND step of a SPEC-COMPILER. You read ONE candidate criteria-GROUP (a system/feature "
        "boundary) and you write ONE full, two-faced loop-prep COMPLETION CRITERION for it — the kind of "
        "criterion a loop-prep Completion-Criteria document is made of.\n"
        "\n"
        "Your input is a unit containing the group:\n"
        "  - `group_id`        — the group's short id;\n"
        "  - `what`            — plain language what the group is (its feature/system boundary);\n"
        "  - `systems_touched` — which parts of the system the group implicates (prose).\n"
        "\n"
        "Write the criterion with BOTH faces (this is the bar — a function-only criterion is NOT acceptable):\n"
        "  - FUNCTION: the BEHAVIOUR that must be true, stated so it is verifiable BY USE — a real thing that "
        "moves, no stub, no 'the code exists'. What can the operator/agent actually DO when this is done?\n"
        "  - FORM: where this group has an OPERATOR-FACING SURFACE, the product/design-system bar it must "
        "meet (built on the design system + tokens, navigable/visual not a text-wall, responsive, "
        "consolidated). If the group is PURELY backend with NO operator-facing surface, set FORM to the "
        "literal \"n/a\" — do not invent a surface that the group does not have.\n"
        "\n"
        "Also give:\n"
        "  - files_touched: the real files/modules this criterion would touch (your best honest reading of "
        "where it lives, as paths).\n"
        "  - reuse_or_netnew: write \"reuse:<file>\" ONLY when you are confident a REAL existing file "
        "provides something to build on (name that file). If you are not confident such a file exists, or "
        "the thing is genuinely new, write the literal \"net-new\". NEVER invent a reuse path — a wrong "
        "reuse-claim is worse than an honest \"net-new\". (Your reuse-claim is preliminary; a later "
        "grounding step re-checks it against the actual repo.)\n"
        "  - preserves: what must still WORK through this change (the no-regression face — the existing "
        "behaviour the change must not break).\n"
        "\n"
        "Return ONLY JSON with exactly these fields:\n"
        '  "id": a short id for the criterion (the group_id or a refinement of it),\n'
        '  "function": the behaviour, verifiable by use,\n'
        '  "form": the design-system/product bar where a surface exists, else the literal "n/a",\n'
        '  "files_touched": a list of real file/module paths,\n'
        '  "reuse_or_netnew": "reuse:<file>" (a real file) or the literal "net-new",\n'
        '  "preserves": what still works through the change.\n'
        "\n"
        'Example A (a group WITH an operator-facing surface, building on a real file): '
        '{"id": "browse-surface", "function": "the operator can open a browse view that lists every named '
        'vocabulary by category, read live from the registry — adding a vocabulary makes it appear with no '
        'code edit", "form": "a navigable panel on the canvas chrome, built on the design system + tokens '
        '(no bespoke one-offs), categories as a visual grid not a text-wall, responsive, design-lint clean", '
        '"files_touched": ["canvas/app/src/App.tsx", "runtime/bridge.py"], '
        '"reuse_or_netnew": "reuse:runtime/bridge.py", '
        '"preserves": "the existing canvas chrome + the other panels keep rendering unchanged"}\n'
        'Example B (a purely BACKEND group, no surface, genuinely new — FORM is "n/a", net-new): '
        '{"id": "vocab-registry", "function": "a file-discovered vocab registry where dropping a file adds a '
        'named vocabulary that is then queryable through capabilities(); a malformed entry fails loud, never '
        'silently registers", "form": "n/a", '
        '"files_touched": ["runtime/vocab_registry.py", "runtime/suite.py"], '
        '"reuse_or_netnew": "net-new", '
        '"preserves": "the existing role/node registries and their discovery keep working unchanged"}'
    ),
    "output_schema": ExpandCriterionOut,
    # DEFAULT input axis — ("utterance",) ONLY. group_id/what/systems_touched are KEYS inside the unit dict
    # that run_items places at ctx["utterance"] (byte-identical default run_role framing), NOT declared
    # inputs (declaring them would trip the net-new compose path / leave dead declared-extras). The per-unit
    # corpus-slice + few-shot (COMPOSITIONS ⑦ step 1) ride into the same unit when the cascade supplies them.
    "input_addresses": ("utterance",),
    "trigger": (
        "fired over N group-units by run_items (the MAP half of COMPOSITIONS ⑦, step 2b) — one unit per "
        "group from decompose_seed, each {group_id, what, systems_touched}; its output criteria feed the "
        "no-fiction reuse-check ground_criterion (2c, the OTHER lane) then the triad_synth REDUCE (3) that "
        "assembles the loop-prep triad. PROPOSED → me → Tim (a draft, never a build off it)."
    ),
    # C2.5 capability-query: the expander wants a chat/json model. default_model None keeps the safe floor =
    # the resident swarm brain (the 4B) — the MAP runs on it today, NO GPU window needed. A STRONGER model
    # MAY bind via models_for_role as an ENHANCEMENT (a correctness-sensitive criterion benefits), never a
    # requirement.
    "model_binding": {"requires": ["chat", "json"], "default_model": None, "default_base_url": None},
    # A SPEC-COMPILER CONTEXT cast (the cast-beyond-listening seam) — NOT the listening cast. An unknown
    # mode yields an EMPTY cast, so declaring this does not change listening; it is fired explicitly via
    # run_items in the composition. Mirrors decompose_seed's {"spec"} / verify_lens's {"verification"}.
    "mode_scope": {"spec"},
    "rules": [],
    "render_hint": {"shape": "criterion", "lane": "expand_criterion"},
}
