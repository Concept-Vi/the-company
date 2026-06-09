// SEAM-BUILD — two file-disjoint cognition seams, BUILD-ONLY (no commit phase — the G8 fix: the
// next loop beat commits, avoiding the index race + the mega-commit-agent timeout).
// G1 (the MCP draft/one-off run path that blocked the registry-coverage classify) ∥ ⑥ verify_lens role.
// Run: Workflow({scriptPath: "build-prep/cognition-self-improvement/seam-build.workflow.js"})

export const meta = {
  name: 'seam-build-g1-jury',
  description: 'Build two file-disjoint cognition seams — G1 (MCP draft/one-off run path, mcp_face) + verify_lens role (roles/) — each builds + self-verifies BY USE, does NOT commit (next loop beat commits)',
  phases: [
    { title: 'Build', detail: 'G1 draft-run path (mcp_face/server.py) ∥ verify_lens role (roles/verify_lens.py) — parallel, file-disjoint, self-verify, NO commit' },
  ],
}

const LAWS = `
BINDING LAWS: read /home/tim/company/AGENTS.md → MAP.md → STATE.md → the module AGENTS.md FIRST, + build-prep/cognition-self-improvement/{COMPOSITIONS,SYSTEM-GAPS}.md for the program.
- LAW-0 UNIFICATION: get the full relevant code picture FIRST (grep/read the real engine fns you reuse); take any duplicate/adjacent/stranded thing you find INTO scope — never route around. REUSE-DON'T-PARALLEL (no second engine/registry/path).
- THE FLOOR STAYS: emit NO resolve/approve/dispatch, launch NO claude -p. A draft RUN is run:// COMPUTATION (never an authoring-apply — the draft role is NEVER written to roles/ or committed). Declarative authoring (a real role file) is DIRECT but is NOT what G1 does — G1 runs an EPHEMERAL spec.
- registry-is-truth/no-hardcoding · NOTHING static · fail-loud no-silent-fallback · additive (don't break existing callers).
- Work ONLY your lane's file(s). Do NOT edit another lane's file. Do NOT edit runtime/cognition.py or runtime/suite.py or runtime/roles.py (READ them targeted for the reuse seam). Do NOT commit (the next loop beat commits). Do NOT edit roles/AGENTS.md (next beat reflects new roles).
- GPU: a verify-by-use fire needs the chat brain — check \`company gpu\`; \`company up chat-4b --wait\` if down (the resource-manager loads it async; gated-evict; never stomp a co-resident session). NO Gemini · NO green-paint (not headlessly confirmable → say needs-tim).
- On finish: write build-prep/cognition-self-improvement/seam-lanes/<lane>.report.json {lane, files_written, new_role_ids, how_verified, status, needs_tim, notes}.
`

const SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['lane', 'files_written', 'how_verified', 'status'],
  properties: {
    lane: { type: 'string' },
    files_written: { type: 'array', items: { type: 'string' } },
    new_role_ids: { type: 'array', items: { type: 'string' } },
    new_mcp_tools: { type: 'array', items: { type: 'string' } },
    how_verified: { type: 'string' },
    status: { type: 'string', enum: ['built-verified', 'built-untested', 'blocked'] },
    needs_tim: { type: 'string' }, notes: { type: 'string' },
  },
}

phase('Build')
const built = await parallel([
  // ---- LANE G1: the ephemeral/draft-role run path on the MCP face ----
  () => agent(`${LAWS}
LANE G1 — the MCP DRAFT/ONE-OFF RUN PATH (SYSTEM-GAPS G1). PROBLEM (felt by use): run_role/run_items take a registered role id (string); a one-off bounded classify (e.g. "classify these 39 candidates once") forces create_role — which COMMITS a throwaway role (registry pollution + an index race) or drops below the MCP. This blocked the registry-coverage classify from running via the MCP.
THE FIX (reuse, don't build new engine): add a NEW MCP tool in mcp_face/server.py — e.g. \`run_draft\` (one unit) and/or \`run_draft_items\` (N units, the MAP) — that fires an INLINE draft role spec WITHOUT registering/committing. REUSE the EXISTING engine: runtime/roles.py:_build_role (dict→Role, line 139) builds a Role from a draft dict; runtime/suite.py:dry_run_role (line 9363) ALREADY accepts role_or_fields as a dict and runs it; runtime/cognition.run_items fans a Role over N units. So the tool = {draft_spec: {id, prompt_template, output_schema (field-spec dict like create_role's), op}, units|utterance} → _build_role(draft) → run_items/run_role → return per-unit outputs. The draft role is NEVER written to roles/, NEVER committed.
FLOOR: this is run:// computation — emits NO resolve/approve/dispatch. Assert in your verify that NO file appears under roles/ after a draft run.
FILE-DISJOINT: ONLY mcp_face/server.py. REUSE _build_role/dry_run_role/run_items read-only (do NOT edit roles.py/suite.py/cognition.py).
VERIFY BY USE: call your new tool with a draft spec (a tiny classify: output_schema {kind:"str"}) over 2-3 literal string units, chat-4b resident → per-unit outputs returned; \`git status roles/\` shows NO new file; the floor scan (cognition_governance_acceptance) still passes (run it). Report new_mcp_tools + the by-use result + that roles/ stayed clean. Do NOT commit.`,
    { label: 'G1-draft-run', phase: 'Build', schema: SCHEMA }),

  // ---- LANE JURY: the verify_lens role (⑥, the reusable verification composition) ----
  () => agent(`${LAWS}
LANE JURY — the verify_lens ROLE (COMPOSITIONS ⑥, the reusable verification jury; no GPU to build). Build NEW roles/verify_lens.py: a role that judges ONE change-under-test through ONE LENS (the lens rides in the per-unit input, so run_items can fan the SAME role over N lenses). MIRROR an existing role's exact shape — READ roles/screen_reader.py (the ROLE dict + a Pydantic output class, self-registering) and roles/verify_jury.py if it exists (the jury/verdict pattern).
input: the change-under-test (a diff/criterion/claim) + the lens id (one of: correctness · floor · drift · matches-criterion · registry-is-truth · adversarial-disprove). output_schema: {lens:str, verdict:str (pass|fail|uncertain), evidence:str, breaking_case:str (the input that breaks it, for adversarial-disprove; else "")}. prompt_template: hold the model to ITS lens only + the bar; the adversarial-disprove lens is told to DEFAULT to fail/uncertain if it can construct any breaking case. op:generate; mode_scope a verification context.
THE TALLY (do NOT build this beat — flag it): the deterministic green-iff-all-pass / any-fail→fail / any-uncertain→flag verdict-tally is a reduce-rule that lives in mcp_face's _REDUCE_RULES (the OTHER lane's file this beat) — so do NOT add it here (it would collide). Just NOTE in your report that the tally reduce-rule is the next-beat follow-on (a small additive _REDUCE_RULES entry), and that verify_lens is usable now via run_items + an existing reduce or manual tally.
FILE-DISJOINT: ONLY roles/verify_lens.py (+ READ screen_reader.py/verify_jury.py for the pattern). Do NOT edit mcp_face/server.py (the other lane) or roles/AGENTS.md (next beat reflects it).
VERIFY BY USE: RoleRegistry().discover(['roles']) shows verify_lens live; fire it (chat-4b resident) on ONE mock change through 2 lenses (e.g. correctness + adversarial-disprove) → well-formed {lens,verdict,evidence,breaking_case}; the floor (cognition_governance_acceptance) + roles_acceptance still pass (run them — a new role must not break drift/floor; but you can't edit AGENTS.md, so roles_acceptance may red on the un-reflected role — that's EXPECTED + the next beat's commit fixes it; note it, don't treat as your failure). Report new_role_ids:["verify_lens"] + the by-use result. Do NOT commit.`,
    { label: 'verify-lens', phase: 'Build', schema: SCHEMA }),
])

const ok = built.filter(Boolean)
log(`Build: ${ok.length}/2 returned · ${ok.filter(b=>b.status!=='blocked').length} built · new tools: ${ok.flatMap(b=>b.new_mcp_tools||[]).join(',')||'-'} · new roles: ${ok.flatMap(b=>b.new_role_ids||[]).join(',')||'-'}`)
return { built: ok }
