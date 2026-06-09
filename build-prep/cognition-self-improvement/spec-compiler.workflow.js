// SPEC-COMPILER — COMPOSITIONS ⑦, BUILD-ONLY (no commit phase — next loop beat commits).
// The faculty that drafts a loop-prep triad from a dense seed. 4 roles, 2 file-disjoint lanes
// (the MAP half ∥ the ground+synth half) sharing ONE criterion-schema contract.
// Run: Workflow({scriptPath: "build-prep/cognition-self-improvement/spec-compiler.workflow.js"})

export const meta = {
  name: 'spec-compiler-7',
  description: 'COMPOSITIONS ⑦ spec-compiler — decompose_seed + expand_criterion (MAP half) ∥ ground_criterion + triad_synth (ground+synth half). Build+self-verify BY USE on a sample seed, NO commit.',
  phases: [
    { title: 'Build', detail: 'decompose_seed + expand_criterion (roles/) ∥ ground_criterion + triad_synth (roles/) — parallel, file-disjoint, self-verify, NO commit' },
  ],
}

// THE SHARED CRITERION CONTRACT (both lanes align to this — expand emits it, ground reads it, synth assembles):
const CRITERION = `the two-faced CRITERION shape (the loop-prep bar — FUNCTION and FORM both):
  {id: str, function: str (the behaviour, verifiable BY USE — no stub), form: str (the design-system/product
   bar where a surface exists, else "n/a"), files_touched: list[str], reuse_or_netnew: str ('reuse:<file>' |
   'net-new'), preserves: str (what still works through the change)}`

const LAWS = `
BINDING LAWS: read /home/tim/company/AGENTS.md → MAP.md → STATE.md → roles/AGENTS.md FIRST, + build-prep/cognition-self-improvement/COMPOSITIONS.md (section ⑦) + skim ONE existing loop-prep triad (build-prep/cognition-engine/COMPLETION-CRITERIA.md) as the house-style few-shot.
- LAW-0 UNIFICATION: full picture first (read roles/verify_lens.py for the ROLE-dict+Pydantic shape; roles/reduce_synth.py for the reduce-role shape). REUSE-DON'T-PARALLEL.
- THE FLOOR STAYS: a role is declarative; emit NO resolve/approve/dispatch, launch NO claude -p.
- registry-is-truth (file-discovered roles/<id>.py) · NOTHING static · fail-loud · additive · NO-FICTION (a drafted criterion's reuse-claim must cite a REAL file; un-built → 'net-new', never an invented reuse).
- Work ONLY your lane's files. Do NOT edit the other lane's files, runtime/*, mcp_face/*, or roles/AGENTS.md (next beat reflects new roles). Do NOT commit.
- GPU: verify-fire needs chat-4b — check \`company gpu\`; \`company up chat-4b --wait\` if down (async, gated, no stomp). NO Gemini · NO green-paint.
- On finish: write build-prep/cognition-self-improvement/seam-lanes/<lane>.report.json {lane, files_written, new_role_ids, how_verified, status, needs_tim, notes}.
`

const SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['lane', 'files_written', 'how_verified', 'status'],
  properties: {
    lane: { type: 'string' }, files_written: { type: 'array', items: { type: 'string' } },
    new_role_ids: { type: 'array', items: { type: 'string' } },
    how_verified: { type: 'string' }, status: { type: 'string', enum: ['built-verified', 'built-untested', 'blocked'] },
    needs_tim: { type: 'string' }, notes: { type: 'string' },
  },
}

phase('Build')
const built = await parallel([
  // ---- LANE MAP: decompose_seed (seed→groups) + expand_criterion (group→criterion) ----
  () => agent(`${LAWS}
LANE MAP — the spec-compiler's seed→criteria half (COMPOSITIONS ⑦). Build TWO new roles, MIRROR roles/verify_lens.py's shape (self-registering ROLE dict + Pydantic out class; the input rides in the unit at ctx['utterance']). mode_scope a 'spec' context (cast-beyond-listening; listening untouched). op:generate.
(1) roles/decompose_seed.py — 1×1: reads a dense SEED (Tim's terse idea) → candidate criteria-GROUPS. output_schema: {groups: list[ {group_id:str, what:str, systems_touched:str} ]}. prompt_template: decompose the seed into the natural system/feature boundaries (the loop-prep "group by system, not implementation-order").
(2) roles/expand_criterion.py — MAP (fanned via run_items over the groups): reads ONE group → a full TWO-FACED criterion. output_schema = ${CRITERION}. prompt_template: write BOTH faces (you may NOT write a function-only criterion — FORM is half of done where a surface exists), grounded in the group; mark reuse_or_netnew honestly (cite a real file for reuse, else 'net-new').
FILE-DISJOINT: ONLY roles/decompose_seed.py + roles/expand_criterion.py (+ READ verify_lens.py). Do NOT edit the ground+synth lane's files or roles/AGENTS.md.
VERIFY BY USE (chat-4b resident): both discover live; fire decompose_seed on a real sample seed (e.g. "a registry of the system's named vocabularies, browsable + addable") → groups; then run_items(expand_criterion, those groups) → full two-faced criteria. Floor (cognition_governance_acceptance) passes; roles_acceptance reds ONLY on 'drift: [decompose_seed, expand_criterion]' (EXPECTED, next beat reflects). Report new_role_ids + the by-use result. Do NOT commit.`,
    { label: 'spec-map', phase: 'Build', schema: SCHEMA }),

  // ---- LANE GROUND: ground_criterion (no-fiction reuse-check) + triad_synth (→ the 3 docs) ----
  () => agent(`${LAWS}
LANE GROUND — the spec-compiler's ground+synth half (COMPOSITIONS ⑦). Build TWO new roles. mode_scope 'spec'. op:generate.
(1) roles/ground_criterion.py — MAP: reads ONE criterion (the shared shape below) → the NO-FICTION reuse-check. output_schema: {criterion_id:str, grounded:str ('reuse'|'net-new'), cite:str (a real file:symbol if reuse, else ''), note:str}. prompt_template: check whether the thing the criterion builds-ON actually exists — cite the real file (the agent should be told it can name files it's confident exist from the repo; the corpus-grounded retrieve is a future embedder-window enhancement, NOT required now — degrade to "name the file you believe + mark confidence in note"). The criterion shape it reads: ${CRITERION}
(2) roles/triad_synth.py — REDUCE (mode=role, MIRROR roles/reduce_synth.py): reads the N grounded criteria → the loop-prep TRIAD. output_schema: {completion_criteria:str, implementation_guide:str, research_synthesis:str} (each a markdown body). prompt_template: assemble the criteria into the three docs in the house style (two-faced criteria; the synthesis = the reuse-map from the ground step; honest status).
FILE-DISJOINT: ONLY roles/ground_criterion.py + roles/triad_synth.py (+ READ reduce_synth.py/verify_lens.py). Do NOT edit the MAP lane's files or roles/AGENTS.md.
VERIFY BY USE (chat-4b resident): both discover live; fire ground_criterion via run_items on 2 mock criteria (one reuse, one net-new) → grounded verdicts with a cite for the reuse; then run_reduce(mode='role', role='triad_synth') over them → a {completion_criteria, implementation_guide, research_synthesis}. Floor passes; roles_acceptance reds ONLY on 'drift: [ground_criterion, triad_synth]' (EXPECTED). Report new_role_ids + the by-use result. Do NOT commit.`,
    { label: 'spec-ground', phase: 'Build', schema: SCHEMA }),
])

const ok = built.filter(Boolean)
log(`Build: ${ok.length}/2 · new roles: ${ok.flatMap(b=>b.new_role_ids||[]).join(',')||'-'}`)
return { built: ok }
