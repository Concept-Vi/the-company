// ENGINE-SEAMS — G24 (guided decoding) ∥ G14 (swap-approval response). BUILD-ONLY, no commit (the
// loop's next beat verifies + commits). File-disjoint from the lead's serial N-series work (fabric/ +
// ops/cli/ vs mcp_face/ + suite.py). Run: Workflow({scriptPath: ".../engine-seams.workflow.js"})

export const meta = {
  name: 'engine-seams-g24-g14',
  description: 'G24 schema-guided decoding (fabric/transport.py — make malformed role-JSON impossible) ∥ G14 swap-approval response (ops/cli/capabilities.py — a needed-eviction returns approve-able info, never hard-block/silent-evict). Build + verify BY USE, no commit.',
  phases: [{ title: 'Build', detail: 'G24 fabric guided-json ∥ G14 swap-approval — parallel, file-disjoint, self-verify, NO commit' }],
}

const LAWS = `
BINDING LAWS: read /home/tim/company/AGENTS.md → MAP.md → STATE.md → the module AGENTS.md FIRST + build-prep/cognition-self-improvement/SYSTEM-GAPS.md (your G's entry). LAW-0 UNIFICATION (find what exists FIRST — these seams may be half-built; finish, don't fork) · reuse-don't-parallel · fail-loud · registry-is-truth · additive/schema-compatible (do NOT break existing callers — every current test must still pass) · FLOOR STAYS · GPU-aware (chat-4b+embed-bge co-resident; check \`company gpu\`; never stomp). Work ONLY your lane's files. Do NOT commit. Do NOT edit mcp_face/* or runtime/suite.py (the lead's serial territory RIGHT NOW). On finish write build-prep/cognition-self-improvement/seam-lanes/<lane>.report.json {lane, files_written, how_verified, status, needs_tim, notes}. NO Gemini. NO green-paint.
`

const SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['lane', 'files_written', 'how_verified', 'status'],
  properties: {
    lane: { type: 'string' }, files_written: { type: 'array', items: { type: 'string' } },
    how_verified: { type: 'string' }, status: { type: 'string', enum: ['built-verified', 'built-untested', 'blocked'] },
    needs_tim: { type: 'string' }, notes: { type: 'string' },
  },
}

phase('Build')
const built = await parallel([
  () => agent(`${LAWS}
LANE G24 — SCHEMA-GUIDED DECODING (make malformed role-JSON IMPOSSIBLE). EVIDENCE: 3 files deterministically fail the 4B digest with unparseable JSON (runtime/bridge.py · roles/check.py · nodes/portal.py — fire roles/repo_digest.py on their content to reproduce; the error rises from fabric/client.py complete() retries). THE FIX: the role's output_schema ALREADY travels to fabric (client.complete(schema=...)) — wire it through fabric/transport.py to vLLM's GUIDED DECODING (OpenAI-compatible: extra_body={"guided_json": <json-schema>} or response_format json_schema — check the transport's existing json/json_schema handling FIRST; something may be half-built [the L-transport lane built json_schema support — FIND it, finish/wire it, don't fork]). The decode then CANNOT emit invalid JSON for ANY role.
FILES: fabric/transport.py (+ fabric/client.py ONLY if the schema isn't already passed through). Do NOT touch runtime/* or mcp_face/*.
VERIFY BY USE (the regression set): fire repo_digest over the 3 known-failing files' content (chat-4b resident — company gpu first) → ALL THREE must now return valid digests; plus one normal role fire (verify_lens or a classify) still works byte-compatibly; plus an embed op unaffected. Run tests/mcp_engine_acceptance.py + any fabric/transport tests. If vLLM rejects guided_json (version/flag), report EXACTLY what it said — do not fake it.`,
    { label: 'G24-guided-decode', phase: 'Build', schema: SCHEMA }),

  () => agent(`${LAWS}
LANE G14 — THE SWAP-APPROVAL RESPONSE (Tim's design, 2026-06-09): today ensure_resident either fits→loads, or needs-eviction→fails/auto-evicts(evict=True). REQUIRED: when a load NEEDS eviction and eviction wasn't pre-authorized, the actuator RETURNS a structured swap-approval ASK — {swap_needed: true, would_load: <svc>, would_evict: [<svcs>], free_gb, needed_gb, approve: "re-call with ensure_evict=true"} — never a hard-block, never a silent evict. The agent (or operator) then decides.
FILES: ops/cli/capabilities.py (find ensure_resident / the #50 actuator + the eviction-decision point). If the run_role(ensure=) seam in runtime/cognition.py needs a TINY pass-through change to surface the structured response instead of raising, report it as a NEEDED-SEAM in your report (do NOT edit runtime/* yourself — the lead applies it).
VERIFY BY USE: simulate/exercise the needs-eviction branch (the card currently holds chat-4b+embed-bge ~13GB; a hypothetical big-model load would need eviction — drive ensure_resident with a service whose size cannot fit, or unit-drive the decision function with a mocked free-VRAM reading if a real load is unsafe — do NOT actually evict or load anything heavy; never stomp the resident models). Confirm: fits→loads unchanged · needs-evict+no-auth→the structured ASK (not an exception, not an evict) · needs-evict+ensure_evict=True→the existing authorized path. Run the capabilities/ops tests that exist.`,
    { label: 'G14-swap-approval', phase: 'Build', schema: SCHEMA }),
])

const ok = built.filter(Boolean)
log(`Engine seams: ${ok.length}/2 · ${ok.map(b=>b.lane+'='+b.status).join(' · ')}`)
return { built: ok }
