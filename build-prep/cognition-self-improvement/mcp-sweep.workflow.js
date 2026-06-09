// MCP-SWEEP — the consolidation sweep, PARALLEL (now that tools are file-discovered, each cluster is its
// own mcp_face/tools/<resource>.py = file-disjoint). Each lane BUILDS its consolidated module + researches
// the codebase THROUGH THE MCP (corpus op=query — dogfood ①) + verifies IN ISOLATION + REPORTS the flat
// tools to remove. It does NOT touch server.py (the shared removal is a serial pass after) or another lane.
// BUILD-ONLY, no commit. Run: Workflow({scriptPath: "build-prep/cognition-self-improvement/mcp-sweep.workflow.js"})

export const meta = {
  name: 'mcp-sweep-consolidation',
  description: 'Parallel MCP consolidation — create(kind)/marks/runs/node/rule each → a file-discovered mcp_face/tools/<r>.py module, consolidating the flat tools; research via the MCP; verify in isolation; report removals. No server.py edits, no commit (serial removal+commit after).',
  phases: [{ title: 'Build', detail: 'create · marks · runs · node · rule — parallel module builds, report the flat tools to remove' }],
}

const LAWS = `
BINDING LAWS — read build-prep/cognition-self-improvement/MCP-DESIGN-PRINCIPLE.md FIRST (the standing law: the whole mandate, the 3 consumers, the upgrade dimensions). Then:
- THE PRINCIPLE: a tool per RESOURCE + a small verb/selector param (op/by/kind) — NOT flat-per-op. registry-is-truth: enums DERIVE from the live registries (NOTHING hardcoded). detail=concise|detailed where a read can be heavy. Helpful fail-loud errors that TEACH. High-signal responses (no raw hashes/IDs). Design for the COLDEST consumer (external agents) → internal + RHM served; the FLOOR is a security boundary (declarative-direct only; NEVER resolve/approve/dispatch/claude-p).
- REUSE-DON'T-PARALLEL: your module WRAPS the existing Suite methods — research them THROUGH THE MCP (corpus(op='query', space='repo', text='...') to find the Suite method / its signature; or read server.py's existing flat-tool bodies for the exact call). NO new engine, NO 2nd path.
- FILE-DISJOINT: write ONLY your lane's file(s). Do NOT edit mcp_face/server.py (the flat-tool removal is a SERIAL pass after — you REPORT the flat tool names to remove), do NOT edit another lane's module, do NOT edit roles/AGENTS.md.
- VERIFY IN ISOLATION (NOT by importing the whole server — sibling modules may be mid-write): construct a throwaway FastMCP + a Suite, call your module's register(mcp, suite), confirm your tool registers + fire a sample op of each kind. (company gpu first if a call needs a model; the embedder/chat co-reside.)
- Do NOT commit. NO Gemini. On finish: write build-prep/cognition-self-improvement/seam-lanes/mcpsweep-<lane>.report.json {lane, module, tool, ops, flat_tools_to_remove:[...], how_verified, notes, new_suite_methods?}.
`

const SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['lane', 'module', 'flat_tools_to_remove', 'how_verified', 'status'],
  properties: {
    lane: { type: 'string' }, module: { type: 'string' }, tool: { type: 'string' },
    ops: { type: 'array', items: { type: 'string' } },
    flat_tools_to_remove: { type: 'array', items: { type: 'string' } },
    new_suite_methods: { type: 'array', items: { type: 'string' } },
    how_verified: { type: 'string' }, status: { type: 'string', enum: ['built-verified', 'built-untested', 'blocked'] },
    notes: { type: 'string' },
  },
}

phase('Build')
const built = await parallel([
  () => agent(`${LAWS}
LANE CREATE — the biggest consolidation (8→1) + a LAW-0 unify. Build mcp_face/tools/create.py: ONE tool create(kind, spec, model="") that DECLARATIVELY authors a new registry entry, dispatching to Suite.create_<kind>. The kinds DERIVE registry-is-truth from the Suite's create_<kind> methods MINUS 'node' (node is a GRAPH instance, not a declarative registry — it stays in the node lane). Pass model only to kinds whose signature accepts it (create_role).
★ FIRST close the flagged seam (the code asks for it): create_projection is currently INLINE in server.py (NOT a Suite method) — LIFT it to Suite.create_projection. The clean lift (verified by me): add a 'projection' row to runtime/suite.py:_CORPUS_REGISTRIES mapping to (projections_dir, projection_registry, ProjectionRegistry, 'PROJECTION'); then a wrapper method create_projection(self, spec) that returns self._write_registry_file('projection', spec) — the SHARED helper already does render→gate-in-tempdir→atomic-write→_commit_or_rollback→rediscover (mirrors the other corpus registries; the inline server body becomes redundant). VERIFY Suite.create_projection works in isolation (a throwaway Suite, create a test projection, confirm it discovers, then delete the test file). The 7 other kinds are already Suite.create_<kind>.
M4 (the eval finding): create_role via the MCP does NOT auto-reflect the drift-home (roles/AGENTS.md) → roles_acceptance reds. Make create's RESPONSE teach this (return a 'reflect_in' field naming the drift-home for the kind, e.g. roles/AGENTS.md) — a self-teaching response, NOT a silent gap. (Full auto-append is a follow-on; the teaching response is the M4 floor.)
FILE-DISJOINT: mcp_face/tools/create.py + runtime/suite.py (the projection lift — ONLY the create lane touches suite.py). REPORT flat_tools_to_remove = the 8 create_role/skill/context/projection/mark_type/generation_policy/relation_type/ai_tic (NOT create_node). new_suite_methods=['create_projection'].`,
    { label: 'create', phase: 'Build', schema: SCHEMA }),

  () => agent(`${LAWS}
LANE MARKS — build mcp_face/tools/marks.py. Keep WRITE separate (CQRS): the existing mark(target, mark_type, ...) write stays (report it to STAY, not remove). Consolidate the READS: marks(by, target="", mark_type="") — by='target' → marks_for(target); by='type' → marks_by_type(mark_type); + fold findings_for(target) as by='findings' (or a separate clearly-named op — your call, but research what findings_for returns vs marks_for via the MCP/server.py first). detail/limit if heavy. REPORT flat_tools_to_remove = marks_for, marks_by_type, findings_for (NOT mark — the write stays). Wrap the existing Suite methods (research their signatures).`,
    { label: 'marks', phase: 'Build', schema: SCHEMA }),

  () => agent(`${LAWS}
LANE RUNS — build mcp_face/tools/runs.py. Consolidate the run/result reads: runs(op, role="", op_filter="", address="", limit=50) — op='list' → list_runs; op='find' → find_runs(role/op); op='results' → get_results(address); op='events' → get_events; op='state' → get_state. Research each existing tool's exact signature + return via the MCP/server.py FIRST (they are distinct nouns — be honest if 'state'/'events' don't belong; group only what's genuinely the same resource, per the principle's don't-god-tool rule). detail/limit for heavy ones. REPORT flat_tools_to_remove = the ones you genuinely folded (list_runs, find_runs, + get_results/get_events/get_state IF they fit; leave any that are a distinct resource, and say why).`,
    { label: 'runs', phase: 'Build', schema: SCHEMA }),

  () => agent(`${LAWS}
LANE NODE — build mcp_face/tools/node.py. Consolidate the graph-node verbs: node(op, graph="", type="", config={}, node_id="") — op='create' → create_node; op='delete' → delete_node; op='apply' → apply_node; op='propose' → propose_node. ★ FLOOR CARE: apply_node / propose_node touch the governance posture — confirm (research server.py + governance) that node(op=apply) stays within the EXISTING posture/floor (no new escalation path; an external agent must not gain a privileged action via consolidation). Research each flat tool's signature/body via the MCP/server.py. REPORT flat_tools_to_remove = create_node, delete_node, apply_node, propose_node. Wrap the existing Suite methods.`,
    { label: 'node', phase: 'Build', schema: SCHEMA }),

  () => agent(`${LAWS}
LANE RULE — build mcp_face/tools/rule.py. Consolidate the rule ops: rule(op, ...) — op='attach' → attach_rule; op='dry_run' → dry_run_rule; op='validate' → validate_rule. Research each flat tool's signature + return via the MCP/server.py FIRST (match their params exactly). detail if heavy. REPORT flat_tools_to_remove = attach_rule, dry_run_rule, validate_rule. Wrap the existing Suite methods.`,
    { label: 'rule', phase: 'Build', schema: SCHEMA }),
])

const ok = built.filter(Boolean)
log(`Sweep build: ${ok.length}/5 · modules: ${ok.map(b=>b.module).join(', ')} · removals reported: ${ok.flatMap(b=>b.flat_tools_to_remove||[]).length}`)
return { built: ok }
