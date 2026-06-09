// REPO-EXOCORTEX — COMPOSITION ①, BUILD-ONLY (no commit phase — next loop beat commits).
// The keystone: ingest the repo + the Surface docs into a queryable EMBEDDED corpus (space='repo'),
// then GROUND the FRAME organ-map by querying it (turn the lean "~80% built" into verified reuse-cites).
// Two file-disjoint lanes: the INGEST extractor+run (new module) ∥ the GROUND query (read-only, the value).
// Run: Workflow({scriptPath: "build-prep/cognition-self-improvement/repo-exocortex.workflow.js"})

export const meta = {
  name: 'repo-exocortex-1',
  description: 'COMPOSITION ① repo-exocortex — ingest ~/company + Surface docs into an embedded queryable corpus (space=repo) + ground the FRAME organ-map by query. BUILD-ONLY, no commit.',
  phases: [
    { title: 'Build', detail: 'INGEST extractor + a bounded embed-capture run (new module) ∥ GROUND-map query harness (read-only) — parallel, self-verify BY USE, NO commit' },
  ],
}

const LAWS = `
BINDING LAWS: read /home/tim/company/AGENTS.md → MAP.md → STATE.md → the module AGENTS.md FIRST, + build-prep/cognition-self-improvement/{COMPOSITIONS.md (section ①), FRAME-the-two-halves.md}.
- LAW-0 UNIFICATION: full code picture FIRST — REUSE the existing engine, do NOT build a 2nd corpus/embed/index path: Suite.capture_corpus (runtime/suite.py:9630 — write+embed-on-write into a space, lineage-GATED {project,session,round}), cognition.embed_corpus_to_spaces (:376), store/vector_index.build_index (:64) + index_staleness, Suite.find_relations (:9734), Suite.list_corpus (:9717), roles/repo_digest.py (the existing whole-repo digest role — REUSE it, don't fork). REUSE-DON'T-PARALLEL.
- THE EMBEDDER IS GO: load via run_role(...,ensure=True) / capture handles embed-on-write; it co-resides with chat-4b (~13GB on the 16GB card — check \`company gpu\` first, 7GB free now, NO eviction needed; if a future load WOULD need eviction, surface swap-approval [G14], never silent-evict/stomp).
- THE FLOOR STAYS: ingest/query is run:// COMPUTATION — emits NO resolve/approve/dispatch, launches NO claude -p. Lineage gate is REQUIRED in the corpus-record before the first capture (fail-loud).
- registry-is-truth/no-hardcoding · NOTHING static (chunk-size from the model context, not a constant; file-set from a deterministic walk) · fail-loud · NO green-paint (a real embed that didn't persist → say so).
- Work ONLY your lane's files. Do NOT edit runtime/cognition.py|suite.py|roles.py|mcp_face/* (READ for the reuse seam) or roles/AGENTS.md. Do NOT commit (next beat commits).
- On finish: write build-prep/cognition-self-improvement/seam-lanes/<lane>.report.json {lane, files_written, how_verified, status, findings, needs_tim, notes}.
`

const SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['lane', 'files_written', 'how_verified', 'status'],
  properties: {
    lane: { type: 'string' }, files_written: { type: 'array', items: { type: 'string' } },
    how_verified: { type: 'string' }, status: { type: 'string', enum: ['built-verified', 'built-untested', 'blocked'] },
    findings: { type: 'string', description: 'the grounded result — corpus size/spaces, and (GROUND lane) the verified organ-map cites' },
    needs_tim: { type: 'string' }, notes: { type: 'string' },
  },
}

phase('Build')
const built = await parallel([
  // ---- LANE INGEST: the deterministic extractor + a bounded embed-capture into space='repo' ----
  () => agent(`${LAWS}
LANE INGEST — COMPOSITION ① the repo-exocortex ingest. Build NEW build-prep/cognition-self-improvement/exocortex_ingest.py (a standalone module/script — NOT in runtime/, file-disjoint): a DETERMINISTIC walk of ~/company (runtime/ · store/ · mcp_face/ · ops/ · contracts/ · fabric/ · roles/ · build-prep/cognition-self-improvement/ · build-prep/live-resolution-surface/) → one unit per file {path, kind: code|doc|criteria|surface, text, sha, module_home(nearest AGENTS.md)}; skip .git/binaries/node_modules/.venv; a file > the model context → note for run_chunked (don't fail). This list is the ingest source.
THEN RUN A BOUNDED CAPTURE+EMBED (the keystone, BY USE — embedder GO): take a representative SUBSET (~25-40 files spanning code+doc+surface — enough to PROVE the pipeline + ground the map, not all thousands this beat) → Suite.capture_corpus(records, project='company', session='exocortex-1', round='1', projection='repo') reusing roles/repo_digest.py as the describe-role → each file becomes a durable corpus record in space='repo', EMBEDDED on write (real bge-m3 vectors). Lineage GATED. Confirm with Suite.list_corpus(project='company') + that the vectors persisted (a find_relations or query returns real neighbours, not empty).
FILE-DISJOINT: ONLY build-prep/cognition-self-improvement/exocortex_ingest.py (+ the bounded run, which writes to the .data store — that's runtime state, gitignored, not a code file). REUSE capture_corpus/embed_corpus_to_spaces/repo_digest read-only.
VERIFY BY USE: \`company gpu\` shows the embedder co-resident (loaded, chat-4b not stomped); list_corpus shows the captured records in space='repo'; a query returns real semantic neighbours. Report the corpus size + that embeddings PERSISTED (real vectors) + the full file-count the deterministic walk found (so the FULL ingest is a known next step). Do NOT commit.`,
    { label: 'ingest', phase: 'Build', schema: SCHEMA }),

  // ---- LANE GROUND: query the corpus to verify the FRAME organ-map (read-only; the value) ----
  () => agent(`${LAWS}
LANE GROUND — GROUND THE FRAME ORGAN-MAP (read-only query; the value of ①). Read build-prep/cognition-self-improvement/FRAME-the-two-halves.md — it has a LEAN organ-map (Surface organ ↔ downstream engine piece, marked ✅/🟡/🔴, "~80% built" UNVERIFIED). Your job: VERIFY it against the real code (deterministically + by query), and write the GROUNDED version.
Build NEW build-prep/cognition-self-improvement/organ-map-grounded.md: for EACH row of the FRAME map, find the REAL downstream code (the file:symbol that implements it — grep/read ~/company; if the INGEST lane's space='repo' corpus is queryable by the time you run, use Suite.find_relations/a query to locate it, else grep directly — degrade cleanly). Mark each: ✅ EXISTS (cite file:symbol) · 🟡 PARTIAL (cite + what's missing) · 🔴 NET-NEW (nothing found). Compute the REAL built-percentage from the cites, not the lean guess. Flag any FRAME-map row that was wrong (overclaimed ✅ that's actually 🟡, or a 🔴 that actually exists).
FILE-DISJOINT: ONLY build-prep/cognition-self-improvement/organ-map-grounded.md (a NEW doc). READ-ONLY on all code. Do NOT edit the FRAME doc (cross-reference it).
VERIFY BY USE: every ✅/🟡 cite resolves to a real file:symbol (you checked it exists); the grounded percentage is computed from actual cites. Report the grounded built-vs-netnew split + any FRAME-map corrections + the precise NET-NEW list (what the Surface still needs that the engine does NOT have — the real build backlog). Do NOT commit.`,
    { label: 'ground-map', phase: 'Build', schema: SCHEMA }),
])

const ok = built.filter(Boolean)
log(`Build: ${ok.length}/2 · ${ok.map(b=>b.lane+':'+b.status).join(' · ')}`)
return { built: ok }
