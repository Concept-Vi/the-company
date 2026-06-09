// V-A REGISTRY-GENERATION — the UNIFIED build workflow (BOTH lanes: guided-review [M] + cognition [C]).
// Tim-directed (2026-06-09): ONE workflow builds the whole chain so convergence is inside one run, not
// negotiated across two session-loops. Run with: Workflow({scriptPath: "build-prep/registry-generation/registry-generation.workflow.js"})
//
// cognition: this is the handoff. SHARPEN the two [C] agent briefs below (RG3 register_element role + RG6
// confirm) with your engine depth — edit them in place, they're drafted from guided-review's loop-prep. Then
// RUN this. The [M] briefs (RG1/RG7/RG8/RG9) are guided-review's; leave them. Safe to run as-is if you don't
// refine (git-revertible) — don't let it stall.
//
// The chain it builds: extract(RG1) → ground(screen_reader, exists) → MAP(register_element RG3, run_items) →
// REDUCE(run_reduce cluster-dedup RG5) → CONFIRM(RG6) → PROPOSE(governance) → Tim approves → WRITE-BACK(RG9).
// The cascade spec (RG7) declares it as data. RG2/4/5 are engine RUNS (happen when the cascade fires = RG10,
// after this build). This workflow builds the buildable pieces: RG1, RG3, RG6, RG7, RG8, RG9.

export const meta = {
  name: 'registry-generation-unified',
  description: 'Build the whole V-A registry-generation chain — both lanes (guided-review extract/cascade-spec/surface/write-back + cognition register_element role/confirm) — parallel, file-disjoint, then gate+commit',
  phases: [
    { title: 'Build', detail: 'RG1/RG3/RG6/RG7/RG8/RG9 in parallel — each builds + self-verifies its own file(s), does NOT commit' },
    { title: 'Commit', detail: 'one agent: gate (company suites) + reflect new roles in roles/AGENTS.md + commit each file-disjoint piece with explicit pathspec + record' },
  ],
}

const LAWS = `
BINDING LAWS (every agent): Read FIRST (bounded): build-prep/registry-generation/IMPLEMENTATION-GUIDE.md + COMPLETION-CRITERIA.md + RESEARCH-SYNTHESIS.md + COORDINATION.md (the spec + the [M]/[C] split). Then:
- Work ONLY your own file(s). Do NOT touch another piece's files. Do NOT write runtime/cognition.py or runtime/suite.py (you may READ them targeted for shape). Do NOT touch coherence's gate files.
- DO NOT git commit (the Commit phase commits, to avoid the concurrent-index race). Write your file(s) + self-verify by USE + report.
- Laws: registry-is-truth/no-hardcoding (the chain is DECLARED data, not hand-orchestration) · no-fiction (ground every registration in the Feature & Function Inventory; un-built element → marked "proposed", NEVER an invented capability) · operator-only floor (NEVER auto-mutate the REAL design/_system/addresses.json or the real mockups — test on a TEMP copy) · additive · fail-loud · reuse-not-parallel (extend parse.py; mirror roles/screen_reader.py; use the existing cascade/run_items machinery — no second registry/parser/runner) · verify-by-USE · NO green-paint (not headlessly confirmable → say needs-tim).
- setsid for any long server; NEVER the live :8770 or its store; close any chrome page you open (a chrome process-leak bit this build session — keep it tidy).
`

const BUILD_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['piece', 'lane', 'files_written', 'how_verified', 'status'],
  properties: {
    piece: { type: 'string' }, lane: { type: 'string', enum: ['M', 'C', 'J'] },
    files_written: { type: 'array', items: { type: 'string' } },
    new_role_ids: { type: 'array', items: { type: 'string' }, description: 'role ids added under roles/ (need roles/AGENTS.md reflection by the Commit phase)' },
    how_verified: { type: 'string' }, status: { type: 'string', enum: ['built-verified', 'built-untested', 'blocked'] },
    needs_tim: { type: 'string' }, notes: { type: 'string' },
  },
}

phase('Build')
const built = await parallel([
  // ---- guided-review [M] ----
  () => agent(`${LAWS}
PIECE: RG1 — EXTRACT [M]. Extend design/_system/parse.py with a candidate-element pass → design/_system/candidates.json: the MEANINGFUL elements across the 23 design/mockups/ (buttons, named sections, controls, semantic headings — SKIP layout-only / no-text wrappers). Each unit: {mockup_file, selector, outerHTML(~700 chars), visible_text, tag, ancestor_address (nearest data-ui-ref ui:// ancestor, else the mockup base from design/_system/corpus-meta.json), base_address}. ★ This candidates.json schema is the SEAM CONTRACT register_element (RG3) reads — document it precisely at the top. KEEP existing parse.py behaviour (additive). VERIFY BY USE: run the pass → candidates.json has a sane count (hundreds, << ~3000 raw, noise filtered), all fields on a sample. Report the schema + count.`,
    { label: 'RG1-extract', phase: 'Build', schema: BUILD_SCHEMA }),

  () => agent(`${LAWS}
PIECE: RG7 — the CASCADE SPEC [J, M-authored]. Author design/_system/registry-generation.cascade.json declaring the 5-step chain as DATA: extract → ground(role:screen_reader) → map(role:register_element via run_items over candidates.json) → reduce(run_reduce mode:cluster — dedup across mockups + nest into the address tree) → confirm(RG6). Reference roles by id (screen_reader EXISTS; register_element is RG3 in THIS build; the confirm is RG6). Include the run:// output→input wiring between steps. READ (targeted, read-only) runtime/suite.py save_cascade/build_action + any existing cascade to match the exact shape. VERIFY: the json is well-formed + matches the save_cascade/build_action shape (validate against the real validator if reachable WITHOUT mutating state; else document the shape-match precisely). Report the spec + how validated.`,
    { label: 'RG7-cascade', phase: 'Build', schema: BUILD_SCHEMA }),

  () => agent(`${LAWS}
PIECE: RG8 — the PROPOSAL-BATCH SURFACE [M]. Build a new component/region in canvas/app/src/ (e.g. components/RegistryProposals.tsx) that renders a batch of PROPOSED registry dossiers for operator review: each shows represents + howto{what/what_you_can_do/how_to_change} in plain language (NOT raw JSON), grouped, on the studio's corpus tokens (--studio-* / design-system), with ONE approve gate for the batch + per-entry skip + a "proposed vs maps-to-feature" tag. Dossier shape = register_element output_schema in IMPLEMENTATION-GUIDE.md. Wire to read proposals from a controller hook + an approve handler that calls /api/registry/approve (stub the route call; note the backend route is a follow-on). VERIFY BY USE WITHOUT chrome (leak risk in parallel): npx tsc --noEmit clean (no NEW error at your file) + npm run build clean. Chrome render → needs-tim (flag, do NOT open chrome). Report the file + tsc/build result.`,
    { label: 'RG8-surface', phase: 'Build', schema: BUILD_SCHEMA }),

  () => agent(`${LAWS}
PIECE: RG9 — the WRITE-BACK module [M]. Build design/_system/registry_writeback.py: a callable function taking a CONFIRMED set of dossier entries (register_element output_schema) → (a) merges them additively + dedup-safe into design/_system/addresses.json, (b) stamps the data-ui-ref attribute into the mockup HTML at the recorded selector, (c) re-runs design/_system/parse.py so element-map regenerates. Provenance per entry (run://, model, confidence). FAIL LOUD. ★ OPERATOR-ONLY FLOOR: a FUNCTION, NEVER auto-run — it runs only after Tim approves. VERIFY BY USE on a TEMP COPY ONLY: copy addresses.json + one mockup to a tmp dir, run merge/stamp against the temp, confirm the temp gains the entry + the temp mockup gains the data-ui-ref. NEVER mutate the real design/_system/addresses.json or real mockups. Report the temp round-trip.`,
    { label: 'RG9-writeback', phase: 'Build', schema: BUILD_SCHEMA }),

  // ---- cognition [C] — DRAFTED by guided-review; cognition: sharpen with engine depth ----
  () => agent(`${LAWS}
PIECE: RG3 — the register_element ROLE [C]. (cognition: sharpen this brief.) Create roles/register_element.py — MIRROR roles/screen_reader.py's exact shape (the ROLE dict, self-registering). It maps a candidate element → a proposed registry dossier. input: the candidate fields from design/_system/candidates.json (RG1's contract — read it). output_schema: {address (proposed ui://, nested under the parent), represents (short, like addresses.json's "RUN-run"), howto:{what, what_you_can_do, how_to_change} (at-altitude, matching the 82 existing entries' voice), capabilities (from the REAL capability vocabulary, not invented), maps_to_feature (a Feature & Function Inventory id, or "proposed" if un-built), confidence}. prompt_template assembles the CONTEXT: the element snippet+text+tag · the parent registered address + ITS dossier (so the child nests + inherits framing) · the mockup summary (from screen_reader) · 3-5 existing addresses.json entries as few-shot · the feature inventory (NO-FICTION — never invent a capability). op:generate; mode_scope including a registration context. DO update roles/AGENTS.md is the Commit phase's job — just report new_role_ids:["register_element"]. VERIFY BY USE: fire the role on one real candidate element → a well-formed dossier grounded in the element (adversarial: an un-built element → maps_to_feature:"proposed", NOT a fabricated capability). Report the schema + the by-use result.`,
    { label: 'RG3-register-role', phase: 'Build', schema: BUILD_SCHEMA }),

  () => agent(`${LAWS}
PIECE: RG6 — the CONFIRM [C]. (cognition: sharpen this brief — it's your jury/refcheck expertise.) Build the confirm step that gates the reconciled dossier set for accuracy + no-fiction before it's proposed to Tim. Reuse the engine's jury (run_jury) and/or a confirm role in roles/, PLUS design/_system/refcheck.py to verify each dossier's code ref resolves + its capability is in the Feature & Function Inventory. Low-confidence / unverifiable → FLAGGED (not dropped). Keep it file-disjoint: a new roles/<confirm>.py and/or a pure rule — do NOT edit cognition.py/suite.py (read only). If a confirm role is added, report new_role_ids. VERIFY BY USE (adversarial): feed a dossier with a FABRICATED capability → it's flagged/rejected; a real grounded one → passes. Report the mechanism + the adversarial result.`,
    { label: 'RG6-confirm', phase: 'Build', schema: BUILD_SCHEMA }),
])

const ok = built.filter(Boolean)
const newRoles = ok.flatMap(b => b.new_role_ids || [])
log(`Build: ${ok.length}/6 returned · ${ok.filter(b=>b.status!=='blocked').length} built · new roles: ${newRoles.join(', ')||'none'}`)

phase('Commit')
const manifest = ok.map(b => `- ${b.piece} [${b.lane}/${b.status}] files: ${(b.files_written||[]).join(', ')}${b.new_role_ids?.length?(' | new roles: '+b.new_role_ids.join(',')):''} | verified: ${b.how_verified}${b.needs_tim?(' | needs-tim: '+b.needs_tim):''}`).join('\n')
const commit = await agent(`${LAWS}
You are the COMMIT + RECORD step for the UNIFIED V-A registry-generation build. The build agents wrote these file-disjoint pieces (already in the working tree — do NOT rebuild):
${manifest}

New role ids needing drift-home reflection: ${newRoles.join(', ') || '(none)'}

DO, in order:
1. cd /home/tim/company. HEAD-check (note current HEAD — a concurrent session may have committed).
2. ★ If new roles were added, UPDATE roles/AGENTS.md (the drift-home) to reflect each new role (mirror how screen_reader is listed) — ONE edit covering all new roles (avoids the collision of two build agents editing it). This is required or roles_acceptance reds.
3. Run the gate: ./.venv/bin/python ops/cli/app.py suites — capture GREEN/RED. A pre-existing cross-session red NOT caused by these files (e.g. cognition's run_index) does not block; note it. A red CAUSED by a piece blocks THAT piece.
4. Commit each built piece whose files are present + don't break the gate: git add ONLY that piece's exact files (+ roles/AGENTS.md with the role pieces) → git commit -m "..." -- <explicit paths> (NEVER bare commit). One commit per piece (or group the role + its AGENTS.md reflection). Messages: "V-A RGn: <what> (unified-workflow, <M|C>, <verified|untested>)". NEVER commit another piece's files.
5. A blocked/missing/broken piece → do NOT commit; record why.
6. Append a status block to build-prep/coordination/MESSAGES.md (from:the-runner) + build-prep/guided-review-surface/AUTONOMOUS-STATE.md: which RG pieces landed (shas), needs-tim, the two seam contracts now frozen (candidates.json RG1 + register_element output_schema RG3), and that RG10 (whole-by-use: run the cascade → a once-dead element resolves after Tim approves) is the remaining proof. Commit those docs (explicit pathspec).
VERIFY your commits: git log --oneline for the new shas + git show --name-only to confirm each commit captured ONLY its piece's files. Report the shas + the honest per-piece status.`,
  { label: 'commit+record', phase: 'Commit', schema: {
    type: 'object', additionalProperties: false, required: ['committed', 'gate', 'summary'],
    properties: {
      committed: { type: 'array', items: { type: 'string' } }, gate: { type: 'string' },
      not_committed: { type: 'array', items: { type: 'string' } }, needs_tim: { type: 'string' }, summary: { type: 'string' },
    } } })

return { build: ok, commit }
