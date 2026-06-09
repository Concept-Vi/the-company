// SEAM-BUILD-2 — BUILD-ONLY (no commit phase — G8 fix; the next loop beat commits).
// G9 (complete ⑥: the verify-jury verdict-tally reduce-rule + the saved verify-jury cascade, mcp_face)
// ∥ ⑩ option-panels (a no-dependency faculty: develop_option + score_options roles, new roles/ files).
// Run: Workflow({scriptPath: "build-prep/cognition-self-improvement/seam-build-2.workflow.js"})

export const meta = {
  name: 'seam-build-2-g9-panels',
  description: 'G9 verify-jury tally+cascade (mcp_face) ∥ ⑩ option-panels roles (roles/) — file-disjoint, build+self-verify BY USE, NO commit (next loop beat commits)',
  phases: [
    { title: 'Build', detail: 'G9 verdict-tally reduce-rule + verify-jury cascade (mcp_face/server.py) ∥ ⑩ develop_option + score_options roles (roles/) — parallel, self-verify, NO commit' },
  ],
}

const LAWS = `
BINDING LAWS: read /home/tim/company/AGENTS.md → MAP.md → STATE.md → the module AGENTS.md FIRST, + build-prep/cognition-self-improvement/{COMPOSITIONS,SYSTEM-GAPS}.md.
- LAW-0 UNIFICATION: full code picture FIRST (grep/read the real fns you reuse); take any duplicate/adjacent thing INTO scope. REUSE-DON'T-PARALLEL.
- THE FLOOR STAYS: emit NO resolve/approve/dispatch, launch NO claude -p. A reduce-rule is a pure deterministic function (no model). A role is declarative-direct.
- registry-is-truth/no-hardcoding (the reduce-rule DERIVES from sorted(_REDUCE_RULES); a role is a file-discovered roles/<id>.py) · NOTHING static · fail-loud · additive (don't break existing callers/rules).
- Work ONLY your lane's file(s). Do NOT edit another lane's file. Do NOT edit runtime/cognition.py|suite.py|roles.py (READ for the reuse seam). Do NOT edit roles/AGENTS.md (next beat reflects new roles). Do NOT commit.
- GPU: a verify fire needs chat-4b — \`company gpu\`; \`company up chat-4b --wait\` if down (async load, gated-evict, never stomp). NO Gemini · NO green-paint.
- On finish: write build-prep/cognition-self-improvement/seam-lanes/<lane>.report.json {lane, files_written, new_role_ids, new_reduce_rules, how_verified, status, needs_tim, notes}.
`

const SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['lane', 'files_written', 'how_verified', 'status'],
  properties: {
    lane: { type: 'string' }, files_written: { type: 'array', items: { type: 'string' } },
    new_role_ids: { type: 'array', items: { type: 'string' } },
    new_reduce_rules: { type: 'array', items: { type: 'string' } },
    saved_cascades: { type: 'array', items: { type: 'string' } },
    how_verified: { type: 'string' }, status: { type: 'string', enum: ['built-verified', 'built-untested', 'blocked'] },
    needs_tim: { type: 'string' }, notes: { type: 'string' },
  },
}

phase('Build')
const built = await parallel([
  // ---- LANE G9: complete ⑥ — the verdict-tally reduce-rule + the saved verify-jury cascade ----
  () => agent(`${LAWS}
LANE G9 — COMPLETE THE VERIFY-JURY (SYSTEM-GAPS G9). verify_lens (roles/verify_lens.py) is BUILT + live; it judges ONE change through ONE lens → {lens, verdict: pass|fail|uncertain, evidence, breaking_case}. MISSING: the deterministic verdict-TALLY over the cross-lens verdicts.
(1) ADD a verdict-tally reduce-rule to mcp_face/server.py's _REDUCE_RULES (find it ~line 484; the rules DERIVE — adding here makes it appear in reduce_rule_names() + the run_reduce description + the error, no 2nd list). The rule is a PURE DETERMINISTIC function over the resolved verify_lens outputs: collect each output's \`verdict\` field → return {tally: 'green'|'fail'|'flag', ...} where green IFF every verdict=='pass'; 'fail' if ANY=='fail'; else 'flag' (any 'uncertain'). NO model in the rule (the floor). Mirror the existing count|concat|first rules' shape exactly.
(2) SAVE the verify-jury CASCADE via save_cascade so it's a reusable run_cascade: steps = [run_items(role=verify_lens, kind=items) → run_reduce(mode=rule, reduce_rule=<your new tally name>)]. The unit contract is {lens, change, bar} (verify_lens reads 'change', NOT 'diff' — confirm against roles/verify_lens.py). Name it e.g. 'verify-jury'.
FILE-DISJOINT: ONLY mcp_face/server.py (+ the save_cascade call). REUSE run_reduce(mode='rule') read-only; do NOT edit cognition.py/suite.py/roles.py or the verify_lens role.
VERIFY BY USE: (a) run_reduce(mode='rule', reduce_rule=<tally>) over a MOCK verdict-set of 3 cases → all-pass→green, one-fail→fail, one-uncertain→flag (assert each). (b) the full chain on a real mock change (chat-4b resident): run_items(verify_lens, [{lens:'correctness',change:<buggy>,bar:<>},{lens:'adversarial-disprove',...}]) → run_reduce(rule, tally) → a tally verdict. (c) reduce_rule_names() now lists your rule. (d) mcp_engine_acceptance + cognition_governance_acceptance (floor — _REDUCE_RULES is computation, no forbidden verb) still pass. Use a TEMP store for any save_cascade verify if the live cascades registry is shared; if you save the canonical cascade, note it. Report new_reduce_rules + saved_cascades + the by-use. Do NOT commit.`,
    { label: 'G9-verify-jury', phase: 'Build', schema: SCHEMA }),

  // ---- LANE PANEL: ⑩ option-panels — develop_option + score_options roles ----
  () => agent(`${LAWS}
LANE PANEL — ⑩ OPTION-PANELS (COMPOSITIONS section 10; a no-dependency faculty that serves Tim's A/B/C forks). Build TWO new roles. MIRROR the shape: roles/screen_reader.py (a self-registering ROLE dict + a Pydantic output class) + roles/reduce_synth.py (the reduce-role pattern, for score_options).
(1) roles/develop_option.py — a MAP role: develops ONE approach to a decision through ONE biasing LENS (the lens rides in the unit: 'mvp-first'|'risk-first'|'reuse-first'|'framework-first'|'radical-recompose'). input unit: {lens, question, constraints}. output_schema: {lens:str, approach:str, buys:str, costs:str, touches:str, risk:str}. prompt_template: hold the model to develop a FULL approach from ITS lens's bias, grounded in the constraints. op:generate; mode_scope a 'panel' context (cast-beyond-listening; listening untouched).
(2) roles/score_options.py — a REDUCE role (mode=role): takes the N per-lens approaches → scores each + synthesizes a RECOMMENDATION that may graft runner-up strengths. output_schema: {scored:list (per-option {lens, score, why}), recommendation:str, grafts:str}. Mirror reduce_synth's reduce-role shape. op:generate.
FILE-DISJOINT: ONLY roles/develop_option.py + roles/score_options.py (NEW files). Do NOT edit mcp_face/server.py (the other lane), cognition.py/suite.py/roles.py, or roles/AGENTS.md (next beat reflects them).
VERIFY BY USE (chat-4b resident): RoleRegistry().discover(['roles']) shows BOTH live; fire develop_option via run_items over 2 lenses ({lens:'mvp-first',question:'<a real small decision>',constraints:'<>'}, {lens:'risk-first',...}) → 2 well-formed approaches; then run_reduce(mode='role', role='score_options') over those 2 → a scored recommendation. roles_acceptance will red ONLY on 'drift: [develop_option, score_options]' (un-reflected in AGENTS.md — EXPECTED, next beat fixes; cannot edit AGENTS.md here) — confirm NOTHING earlier fails. Floor (cognition_governance) must pass. Report new_role_ids + the by-use result. Do NOT commit.`,
    { label: 'PANEL-options', phase: 'Build', schema: SCHEMA }),
])

const ok = built.filter(Boolean)
log(`Build: ${ok.length}/2 · new rules: ${ok.flatMap(b=>b.new_reduce_rules||[]).join(',')||'-'} · new roles: ${ok.flatMap(b=>b.new_role_ids||[]).join(',')||'-'} · cascades: ${ok.flatMap(b=>b.saved_cascades||[]).join(',')||'-'}`)
return { built: ok }
