"""roles/decompose_seed.py — the DECOMPOSE_SEED role (COMPOSITIONS ⑦ · the SPEC-COMPILER, step 2a).

The 1×1 head of composition ⑦ (the SPEC-COMPILER — Tim's dense SEED → a loop-prep triad drafted from the
project corpus). This is the FIRST role of the compiler's seed→criteria half: it reads ONE dense SEED
(Tim's terse, multi-dimensional idea — see CLAUDE.md "Dense Messages") and DECOMPOSES it into the natural
candidate criteria-GROUPS, each a system/feature boundary. The loop-prep discipline made a model-call:
**group by SYSTEM, not by implementation-order** (the loop-prep triads — `build-prep/cognition-engine/
COMPLETION-CRITERIA.md`'s GROUP A/B/C/D… are system/feature boundaries, never a build sequence). One group
per natural seam the seed touches; the downstream `expand_criterion` MAP (step 2b) then fans over THESE
groups, one full two-faced criterion per group.

★ THE SEED RIDES IN THE INPUT — this is a 1×1 role (`run_role(decompose_seed, utterance="${seed}")`, the
   composition's step 2a), NOT a fanned MAP. `run_role` places the supplied `utterance` at `ctx["utterance"]`
   (the role's primary input → the DEFAULT byte-identical path, framed `f"Utterance: {ctx['utterance']}"` —
   `runtime/cognition.py:295`). So the seed is the whole input; `input_addresses` stays the DEFAULT
   `("utterance",)`. Mirrors `verify_lens.py`'s self-registering ROLE-dict + Pydantic-out shape, fired 1×1
   like the `repo_digest` direct-create fixture rather than fanned.

★ NESTED OUTPUT (the richer field-type grammar — register_element.py's `HowTo` pattern). The output is a
   LIST of group sub-models (`DecomposeSeedOut.groups: list[Group]`), each `{group_id, what,
   systems_touched}`. `systems_touched` is PROSE (a `str`, e.g. "runtime/suite.py + the canvas chrome"),
   NOT a list — it names which parts of the system the group implicates in the seed-author's own framing,
   so the EXPAND step can ground the criterion. `complete()` validates/retries against this schema (C1.4),
   so a malformed decomposition fails loud, never silently passes.

★ THE FLOOR (AGENTS.md rule 9 · C9.2 · COMPOSITIONS ⑦ step 5). Advisory only — this role DRAFTS candidate
   groups; it never builds, never auto-mutates the repo, never self-approves. The downstream ACT (the triad
   is PROPOSED → me → Tim steers — "a draft, never a build off an unconfirmed compiled spec") is operator/
   me-gated and lives downstream. This file is a pure ROLE dict + a Pydantic output class: it emits no
   resolve/approve/dispatch, launches no `claude -p`. The decomposition is a JUDGEMENT of the seed, not an
   action. (roles/* is in the floor source-invariant scan COG_SOURCES — kept pure data + prompt.)

★ NO-FICTION (the COMPOSITIONS invariant law 2). The grouping is a DECOMPOSITION of what the seed itself
   says — it stays at the seed's own grain (do not invent systems the seed gives no signal for; do not
   collapse distinct seams the seed clearly distinguishes). The per-criterion reuse-vs-net-new grounding
   (does a real file exist to build on?) is NOT this role's job — it is the OTHER lane's `ground_criterion`
   (COMPOSITIONS ⑦ step 2c) on the expanded criteria. This role only carves the boundaries.

`op:generate` (default), `mode_scope:{"spec"}` (the cast-beyond-listening seam — a SPEC-compiler context,
mirroring verify_lens's `{"verification"}` + register_element's `{"registration"}` + mine_exchange's
`{"mining"}`; an UNKNOWN mode yields an EMPTY cast, so adding this does NOT touch the listening cast).
Fired 1×1 by `run_role` as the compiler's step 2a; its output feeds the `expand_criterion` MAP (step 2b).
Model: the resident 4B swarm (`requires:["chat","json"]`, `default_model:None` — no GPU window needed).
"""
from pydantic import BaseModel


class Group(BaseModel):
    """ONE candidate criteria-GROUP — a natural system/feature boundary the seed touches (the loop-prep
    "group by system, not implementation-order"). A real nested sub-model (kind:object in the richer
    field-type grammar — the `HowTo`/register_element nested pattern), NOT a flat dict."""
    group_id: str           # a short kebab/slug id for the group (e.g. "vocab-registry", "browse-surface")
    what: str               # plain language: what this group IS — the feature/system boundary it names
    systems_touched: str    # PROSE (a str, not a list): which parts of the system this group implicates,
    #                         in the seed-author's framing (e.g. "runtime/suite.py registry + the canvas chrome")


class DecomposeSeedOut(BaseModel):
    """decompose_seed reads ONE dense seed → the candidate criteria-GROUPS (one per natural seam). The
    LIST is the decomposition; each `Group` is a system/feature boundary the downstream expand_criterion
    MAP fans over (one full two-faced criterion per group)."""
    groups: list[Group]


ROLE = {
    "id": "decompose_seed",
    "label": "Decompose seed (→ candidate criteria-groups)",
    "description": (
        "Reads ONE dense SEED (Tim's terse, multi-dimensional idea) and decomposes it into candidate "
        "criteria-GROUPS — natural system/feature boundaries (the loop-prep 'group by system, not "
        "implementation-order'). The head (step 2a) of the SPEC-COMPILER (COMPOSITIONS ⑦): one group per "
        "seam the seed touches; the downstream expand_criterion MAP fans over these groups into full "
        "two-faced criteria. Fired 1×1 via run_role(utterance=seed). Advisory: it drafts groups; the triad "
        "is PROPOSED → me → Tim — never a build off an unconfirmed spec."
    ),
    "prompt_template": (
        "You are the DECOMPOSE step of a SPEC-COMPILER. You read ONE dense SEED — a founder's terse, "
        "compressed statement of something to build (it may pack several dimensions into a few words) — and "
        "you DECOMPOSE it into the candidate CRITERIA-GROUPS that a loop-prep Completion-Criteria document "
        "would be organised by.\n"
        "\n"
        "Your input is the SEED itself (the utterance).\n"
        "\n"
        "How to group (this is the whole job):\n"
        "  - Group by SYSTEM / FEATURE BOUNDARY, NOT by implementation order. A group is a natural seam of "
        "the thing being built — a coherent area of behaviour (e.g. 'the registry itself', 'the browse "
        "surface', 'the add/author path', 'the addressing'), the way a Completion-Criteria doc has GROUP A, "
        "GROUP B, GROUP C — each a system/feature area, never a step in a sequence.\n"
        "  - Stay at the SEED'S OWN GRAIN. Carve the boundaries the seed actually implies — do NOT invent a "
        "system the seed gives no signal for, and do NOT collapse two seams the seed clearly distinguishes. "
        "If the seed is small, a few groups is right; if it spans several systems, more.\n"
        "  - For each group, name (a) a short slug id, (b) plain-language what it IS, and (c) which parts of "
        "the system it implicates, as prose (e.g. the modules/surfaces it would touch).\n"
        "\n"
        "Do NOT write the criteria themselves and do NOT decide reuse-vs-net-new — that is a later step. "
        "You only carve the GROUPS.\n"
        "\n"
        "Return ONLY JSON with exactly one field:\n"
        '  "groups": a list of objects, each { "group_id": a short kebab/slug id, '
        '"what": plain language what this group is (the feature/system boundary), '
        '"systems_touched": a prose string naming which parts of the system this group implicates }.\n'
        "\n"
        'Example — seed "a registry of the system\'s named vocabularies, browsable + addable": '
        '{"groups": ['
        '{"group_id": "vocab-registry", "what": "The registry itself — the single source of the system\'s '
        'named vocabularies (modes, verbs, mark-types, …), file-discovered and queryable.", '
        '"systems_touched": "a new file-discovered registry beside the existing role/node registries in '
        'runtime/, surfaced through the Suite capabilities() umbrella"}, '
        '{"group_id": "browse-surface", "what": "The operator-facing surface to BROWSE the vocabularies — a '
        'navigable view of what exists, by category.", '
        '"systems_touched": "the canvas chrome (a new panel/region) reading the registry over /api"}, '
        '{"group_id": "add-vocab", "what": "The path to ADD a new named vocabulary entry (author a row), '
        'governed and additive.", '
        '"systems_touched": "an authoring verb on the Suite + the declarative-authoring (create_*) seam"}, '
        '{"group_id": "vocab-addressing", "what": "Each vocabulary + entry is addressable so it can be '
        'pointed at and explained at altitude.", '
        '"systems_touched": "the ui:// / address registry + the chat co-presence indicate path"}]}'
    ),
    "output_schema": DecomposeSeedOut,
    # DEFAULT input axis — ("utterance",) ONLY. The seed IS the utterance (run_role places the supplied
    # utterance at ctx["utterance"], the byte-identical default framing). A 1×1 role, NOT fanned — there are
    # no per-unit KEYS and no declared extra inputs (declaring extras would trip the net-new compose path).
    "input_addresses": ("utterance",),
    "trigger": (
        "fired 1×1 via run_role(role='decompose_seed', utterance='${seed}') as step 2a of the SPEC-COMPILER "
        "(COMPOSITIONS ⑦); its output groups feed the expand_criterion MAP (step 2b, run_items over the "
        "groups) → full two-faced criteria, then ground_criterion (2c, the OTHER lane) + triad_synth (3)."
    ),
    # C2.5 capability-query: the decomposer wants a chat/json model. default_model None keeps the safe floor
    # = the resident swarm brain (the 4B) — runs on it today, NO GPU window needed. A STRONGER model MAY
    # bind via models_for_role as an ENHANCEMENT (a wider seed benefits from a stronger decomposer), never a
    # requirement.
    "model_binding": {"requires": ["chat", "json"], "default_model": None, "default_base_url": None},
    # A SPEC-COMPILER CONTEXT cast (the cast-beyond-listening seam) — NOT the listening cast. An unknown
    # mode yields an EMPTY cast, so declaring this does not change listening; it is fired explicitly via
    # run_role in the composition. Mirrors verify_lens's {"verification"} / register_element's {"registration"}.
    "mode_scope": {"spec"},
    "rules": [],
    "render_hint": {"shape": "groups", "lane": "decompose_seed"},
}
