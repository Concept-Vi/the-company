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
PIECE: RG3 — the register_element ROLE [C]. (SHARPENED by cognition — engine depth.) Create roles/register_element.py — MIRROR roles/screen_reader.py EXACTLY: a module defining a Pydantic output class + a self-registering ROLE = {...} dict (id·label·description·prompt_template·output_schema·input_addresses·op·mode_scope[·context]). It maps a candidate element → a proposed registry dossier.

★ UNIFICATION FIRST (LAW 0 — before you write anything): grep design/_system/addresses.json for an entry already covering this selector/element; read roles/AGENTS.md for an existing registration role. If register_element-ish already exists, EXTEND it, don't fork. The role itself must DEFER (not re-propose) a candidate whose selector is already a registered ui:// — recognise + skip, never duplicate an address.

OUTPUT_SCHEMA — use the RICHER field-type grammar (B2, now renders nested/enum/optional — this is the engine-depth the draft lacked), NOT flat scalars:
  - address: str (proposed ui://, nested under the parent's address)
  - represents: str (short, like addresses.json's "RUN-run" voice)
  - howto: a NESTED OBJECT (a sub-model, kind:object) { what: str, what_you_can_do: str, how_to_change: str } — at the 82 entries' altitude
  - capabilities: list[str] (from the REAL capability vocabulary — see cognition_inputs / the Feature & Function Inventory — NEVER invented)
  - maps_to_feature: str (a Feature & Function Inventory id, or the literal "proposed" if un-built)
  - confidence: float (0..1)
Define it as a real Pydantic class (mirror screen_reader's ScreenReaderOut); nested howto = a sub-BaseModel. The richer renderer is in runtime/authoring.py if you create via create_role, but here you WRITE the module directly (mirror screen_reader) — so just author the Pydantic class with the nested sub-model.

THE SEAM (input_addresses — the run:// output→input wiring, the input-address intent I own): register_element READS (a) the candidate unit (the per-unit ctx run_items passes — element snippet/text/tag/selector/ancestor_address), (b) the screen_reader mockup-summary for THIS mockup via its run:// address (the GROUND step's output feeds the MAP step — declare it in input_addresses), (c) the parent registered address + ITS dossier (resolved from addresses.json so the child nests + inherits framing). Declare input_addresses to reflect (a)+(b)+(c).

CONTEXT EFFICIENCY (engine depth — avoid N× token bloat): the few-shot exemplars (3-5 addresses.json entries) + the Feature & Function Inventory are SHARED across all N units (identical every fire) → put them in the role's 'context' field (addressed, resolved ONCE), NOT re-inlined per-unit in prompt_template. Only the per-unit-varying context (the element, the parent dossier, the mockup summary) goes through prompt_template/input_addresses. op:generate; mode_scope including a registration context (so cast-beyond-listening can fire it).

DO NOT update roles/AGENTS.md (the Commit phase does it) — just report new_role_ids:["register_element"]. VERIFY BY USE: fire the role on one real candidate element. The fire needs the chat brain resident — FIRST check \`company gpu\`, then \`company up chat-4b --wait\` if it's down (the resource-manager handles the load async/with-swap-latency — Tim's correction; never assume it's up, gated-evict, never stomp a co-resident session). Expect a well-formed dossier GROUNDED in the element. ADVERSARIAL: an un-built element → maps_to_feature:"proposed" + low confidence, NOT a fabricated capability. Report the schema + the by-use result + whether you had to bring the brain up.`,
    { label: 'RG3-register-role', phase: 'Build', schema: BUILD_SCHEMA }),

  () => agent(`${LAWS}
PIECE: RG6 — the CONFIRM [C]. (SHARPENED by cognition — jury/refcheck depth.) Gate the reconciled dossier set for accuracy + no-fiction before it's proposed to Tim. ★ THE KEY DESIGN (engine depth): the confirm is TWO LAYERS, because a single-4B jury measures VARIANCE, not ERROR (the E4 epistemic-monoculture caveat) — so the no-fiction guarantee MUST NOT rest on the model:

  LAYER 1 — the DETERMINISTIC no-fiction FLOOR (the real ERROR gate, model-independent): design/_system/refcheck.py. ★ UNIFICATION (LAW 0): refcheck.py ALREADY EXISTS — read it, REUSE it, extend only if a check is missing; do NOT write a second checker. It verifies, per dossier: (a) every capability ∈ the Feature & Function Inventory (un-listed → FAIL); (b) any code ref resolves to a real file/symbol. This is deterministic — it catches fabrication regardless of model strength. A dossier that fails refcheck is FLAGGED (not dropped, not proposed-as-confirmed).

  LAYER 2 — the ACCURACY jury (the SOFT judgment on top): a new roles/confirm_registration.py — a JURY role (draws:N>1 + a verdict_rule), MIRROR an existing jury role's shape (find one in roles/ — e.g. a verify_*/judge_* role; reuse the draws+verdict_rule pattern, do NOT invent a new jury mechanism). It judges: is \`represents\` accurate to the element? is \`howto\` grounded in what the element actually is? The N draws measure agreement; the verdict_rule is a DECLARED deterministic rule (runtime/rules.py RULE_OPS — a pure AST over the resolved draw values, NO model in the rule): quorum-agree on grounded==true AND refcheck.passed==true → confirmed; else → FLAGGED. The jury role MAY bind a stronger model from the widened catalog (C2.5 / models_for_role) when a GPU window permits — as an ENHANCEMENT, never a requirement (Layer 1 already guarantees no-fiction on the 4B alone).

Low-confidence / unverifiable → FLAGGED, never dropped (variance-not-error → flag). File-disjoint: NEW roles/confirm_registration.py + REUSE design/_system/refcheck.py; do NOT edit cognition.py/suite.py (read only). Report new_role_ids:["confirm_registration"].

VERIFY BY USE (adversarial — the jury draws need the chat brain: check \`company gpu\` → \`company up chat-4b --wait\` if down, the resource-manager loads it async/with-swap, gated, no stomp): feed a dossier with a FABRICATED capability → refcheck (Layer 1) FAILS it → FLAGGED (prove the deterministic floor bites even if the jury wavered); feed a real grounded dossier → passes both layers. Report the two-layer mechanism + the adversarial result + whether refcheck needed extending.`,
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
