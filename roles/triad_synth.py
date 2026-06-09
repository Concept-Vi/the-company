"""roles/triad_synth.py — the TRIAD_SYNTH reduce-role (COMPOSITIONS ⑦ · the spec-compiler's REDUCE/SYNTH).

The REDUCE half of the spec-compiler (composition ⑦, step 3): the cross-criterion JOIN that takes the N
GROUNDED criteria (each a `ground_criterion` output — the MAP step's reuse-checked criterion) and
ASSEMBLES them into the loop-prep TRIAD — the three documents I keep building by hand, compiled:
  · Completion-Criteria  — the verifiable-by-use bar (the two-faced criteria, FUNCTION + FORM, honest status)
  · Implementation-Guide — how to build them (per criterion: where it lands, the reuse seam, the order)
  · Research-Synthesis   — the reuse-MAP (which criterion reuses what real file vs is net-new) = the reduce of 2c
"the synthesis = the reduce of 2c" (COMPOSITIONS ⑦) — the Research-Synthesis IS the assembled grounded
verdicts, so this reduce-role's third doc is built directly from the `grounded`/`cite` it reads.

★ A REDUCE-ROLE, mirroring `roles/reduce_synth.py` + `roles/score_options.py` EXACTLY (the C 2/4
   synthesize-join template): `op:generate`, takes the N map-output grounded-criteria — composed by
   `run_reduce(mode="role")` into ONE labelled `"notes"` input (the N `ground_criterion` outputs are
   DYNAMIC, so the compose is the DRIVER's job, not statically declared here) — and MERGES them into the
   three-doc triad. Fired explicitly via `run_reduce(mode="role", role="triad_synth")`; the driver
   supplies `ctx={"notes": composed}` where `composed` renders each upstream grounded-criterion as
   "[unit_id] <json>" (so this role sees each criterion's id + grounded-verdict + cite). Identical seam
   to reduce_synth + score_options.

★ THE INPUT AXIS (C 1/4 — the one place behaviourally identical to reduce_synth/score_options):
   `input_addresses=("notes",)`. "notes" is a DECLARED non-utterance input present in the ctx that
   `run_reduce(mode="role")` supplies → run_role's `_is_default_input` is False → the labelled-compose
   path (NOT the default-utterance framing). The N upstream `run://` addresses are dynamic (the
   ground-check's outputs) so they are NOT statically listed here — run_reduce reads them back and
   composes them into this one "notes" input.

★ THE OUTPUT IS THREE MARKDOWN BODIES (the one place the mirror's SHAPE differs — deliberate, like
   score_options' richer shape). Where reduce_synth returns a flat `{summary:str}`, the spec-compiler
   reduce must return the THREE loop-prep docs — so the output is three string fields, each a full
   markdown body. NOTE: because these are full documents, the by-use `run_reduce` call MUST pass a
   GENEROUS `max_tokens` (the default 512 truncates three docs → the JSON never closes → schema-retry
   exhausts → FabricError; a generous budget is required, the truncation is fail-loud, never silent).

★ NO mode_scope → in NO cast (a reduce-role fired explicitly via run_reduce, not part of any cast — the
   MAP role `ground_criterion` carries the {"spec"} scope; the REDUCE is fired directly). So adding it
   does NOT change any cast (mirrors reduce_synth's + score_options' "in no cast" stance). This matters:
   triad_synth declares input_addresses=("notes",), so if a cast ever auto-fired it as a swarm role it
   would fail-loud on the missing "notes" input — the REDUCE belongs OFF the cast, fired directly.

★ THE FLOOR (AGENTS.md rule 9 · the COMPOSITIONS two invariant laws · cognition_governance). Advisory
   only — the reduce DRAFTS the triad; I refine it, Tim steers, and the spec-compiler's floor is "a
   draft, never a build off an unconfirmed compiled spec." This file is a pure ROLE dict + a Pydantic
   output class: it emits no resolve/approve/dispatch, launches no `claude -p`. A reduce-role is pure
   data + a model call (the join is L1 data: which role, what schema; the model runs INSIDE the role,
   L2). The `rules` entry below is a DECLARED reduce rule (DATA) — the reduce DRIVER is
   runtime/cognition.run_reduce; the role does not itself execute a verdict.
"""
from pydantic import BaseModel


class TriadSynthOut(BaseModel):
    """`triad_synth` reads the N composed grounded-criteria → the loop-prep TRIAD (three markdown bodies).
    Each field is a full markdown document in the build-prep house style (two-faced criteria, honest
    status, registry-is-truth). The Research-Synthesis is the assembled reuse-map (the reduce of the
    grounded verdicts). Because these are full documents, the by-use run_reduce call passes a generous
    max_tokens (the 512 default truncates → fail-loud JSON-parse failure, never silent)."""
    completion_criteria: str    # markdown: the verifiable-by-use bar (two-faced criteria, honest status)
    implementation_guide: str   # markdown: how to build each criterion (where it lands, the reuse seam, order)
    research_synthesis: str      # markdown: the reuse-MAP (each criterion reuse:<file> vs net-new) — reduce of 2c


ROLE = {
    "id": "triad_synth",
    "label": "Synthesize triad (spec-compiler reduce)",
    "description": (
        "Assembles the N grounded criteria (from ground_criterion, composed by run_reduce) into the "
        "loop-prep TRIAD — Completion-Criteria, Implementation-Guide, Research-Synthesis — in the "
        "build-prep house style (two-faced FUNCTION/FORM criteria, honest status, registry-is-truth); "
        "the Research-Synthesis is the assembled reuse-map (the reduce of the ground-check). The REDUCE "
        "half of the spec-compiler (COMPOSITIONS ⑦, step 3). Advisory: a DRAFT — never a build off it."
    ),
    "prompt_template": (
        "You are the TRIAD_SYNTH reduce-role — the cross-criterion JOIN of a SPEC-COMPILER. You are given "
        "several GROUNDED CRITERIA, one per upstream unit, each on its own line prefixed by its unit id in "
        "[brackets]. Each grounded criterion carries: its `criterion_id`, the `grounded` verdict "
        "('reuse' or 'net-new'), the `cite` (a real file:symbol when reuse, empty when net-new), and a "
        "`note` (the grounder's confidence + reasoning). (Where the upstream criterion also carries its "
        "function/form/files_touched/preserves, use them — assemble whatever is present.)\n"
        "\n"
        "ASSEMBLE them into the THREE loop-prep documents (the build-prep house style):\n"
        "  1. completion_criteria — the truth-table of what must be TRUE for the build to be DONE. Write "
        "each criterion TWO-FACED: its FUNCTION (the behaviour, verifiable BY USE — no stub) AND its FORM "
        "(the design-system/product bar where a surface exists, else 'n/a'). Carry HONEST STATUS markers "
        "(proven-by-use / built-not-proven / gap). Registry-is-truth (no hardcoded value where a registry "
        "is the source). Group related criteria under headings for parseability.\n"
        "  2. implementation_guide — how to build each criterion: where it lands (the file/module), the "
        "REUSE SEAM (cite the real file it builds on, from the grounded verdict), what it preserves, and "
        "a sensible build ORDER (foundations before features). Be concrete — name files.\n"
        "  3. research_synthesis — the REUSE-MAP: for each criterion, whether it REUSES a real file "
        "(name the cite) or is NET-NEW (honest). This is the reduce of the ground-check — assemble the "
        "grounded verdicts into one map so the reuse-vs-net-new shape of the whole build is visible at a "
        "glance. Distinguish high- from low-confidence grounding (from the notes).\n"
        "\n"
        "Write in the house style: provisional/open (never closure-form), expansive (more not less), "
        "headings for parseability, honest status only (never green-paint a gap). Each document is a full "
        "markdown body.\n"
        "\n"
        "Return ONLY JSON with exactly these fields, each a markdown string:\n"
        '  "completion_criteria": the Completion-Criteria document (two-faced criteria, honest status),\n'
        '  "implementation_guide": the Implementation-Guide document (where each lands, the reuse seam, order),\n'
        '  "research_synthesis": the Research-Synthesis document (the reuse-map — reuse:<file> vs net-new).\n'
        "\n"
        'Example: {"completion_criteria": "## GROUP A — ...\\n- **A1 · ...** — FUNCTION: ... FORM: ... '
        '🔴 gap\\n", "implementation_guide": "## A1\\nLands in `runtime/...`; reuses '
        '`runtime/cognition.py:run_items`; preserves ...\\n", "research_synthesis": "## Reuse-map\\n- A1 '
        '→ reuse: runtime/cognition.py:run_items (high confidence)\\n- A2 → net-new\\n"}'
    ),
    "output_schema": TriadSynthOut,
    # The declared input axis (C 1/4): "notes" is the composed N-grounded-criteria input run_reduce
    # supplies in ctx. Present-in-ctx + non-utterance ⇒ run_role's labelled-compose path (NOT the default
    # utterance framing). The N upstream run:// addresses are dynamic (the ground-check's outputs) so they
    # are NOT statically listed here — run_reduce reads them back and composes them into this one "notes"
    # input. Identical to reduce_synth's + score_options' seam.
    "input_addresses": ("notes",),
    "op": "generate",
    "trigger": (
        "fired explicitly by run_reduce(mode='role', role='triad_synth') as the cross-criterion JOIN of "
        "the spec-compiler (COMPOSITIONS ⑦, step 3) — over the N ground_criterion outputs (the ground-"
        "check's MAP outputs). Pass a GENEROUS max_tokens (the three docs exceed the 512 default → the "
        "default truncates → fail-loud JSON-parse failure)."
    ),
    "model_binding": {"requires": ["chat", "json"], "default_model": None, "default_base_url": None},
    # NO mode_scope → in NO cast (a reduce-role fired explicitly via run_reduce). Mirrors reduce_synth +
    # score_options. Load-bearing: triad_synth declares input_addresses=("notes",), so it must NOT be in a
    # cast that could auto-fire it as a swarm role (it would fail-loud on the missing "notes" input).
    "rules": [
        # DECLARED reduce rule (DATA; the reduce DRIVER is runtime/cognition.run_reduce). The N grounded
        # criteria are joined into the three loop-prep docs — the cross-criterion synthesize join, with
        # the Research-Synthesis being the assembled reuse-map (the reduce of the ground-check).
        {"id": "reduce-triad-synth", "reads": "triad_synth.notes",
         "effect": "assemble the N grounded criteria into the loop-prep triad (criteria/guide/synthesis); "
                   "the research-synthesis is the assembled reuse-map",
         "kind": "reduce"},
    ],
    "render_hint": {"shape": "triad", "lane": "triad_synth"},
}
