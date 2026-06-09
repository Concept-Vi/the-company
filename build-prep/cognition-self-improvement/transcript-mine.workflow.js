// TRANSCRIPT-MINE — COMPOSITIONS ③, BUILD-ONLY (no commit phase — next loop beat commits).
// Two file-disjoint new roles + a BOUNDED real mining run (the value: findings about how-I-work-with-Tim).
// Run: Workflow({scriptPath: "build-prep/cognition-self-improvement/transcript-mine.workflow.js"})

export const meta = {
  name: 'transcript-mine-3',
  description: 'COMPOSITIONS ③ transcript-miner — build mine_exchange + judge_mining roles (file-disjoint) + RUN a bounded mining over real exchanges (the self-improvement findings). BUILD-ONLY, no commit.',
  phases: [
    { title: 'Build', detail: 'mine_exchange role + bounded mining run (roles/mine_exchange.py) ∥ judge_mining role (roles/judge_mining.py) — parallel, self-verify BY USE, NO commit' },
  ],
}

// The SHARED output contract (both lanes use it — mine emits it, judge validates it):
const MINE_SCHEMA = `mine_exchange output_schema (use the RICHER field-types — strings + optionals):
  {decision: str (the decision/move made this exchange, or ""), rationale: str (why, or ""),
   tim_correction: str (what Tim corrected, or ""), my_error: str (what I did wrong that prompted it, or ""),
   bug_fix: str (a bug found+fixed, or ""), needs_tim: str (a needs-tim/flag raised, or ""),
   frustration: str (a frustration Tim named, or ""), pattern_tag: str (a short kebab tag for the
   recurring theme — e.g. 'green-painting', 'summaries-not-detail', 'dismissed-stranded-work',
   'over-cautious-gating')}`

const LAWS = `
BINDING LAWS: read /home/tim/company/AGENTS.md → MAP.md → STATE.md → roles/AGENTS.md FIRST, + build-prep/cognition-self-improvement/COMPOSITIONS.md (section ③).
- LAW-0 UNIFICATION: full picture first (read roles/screen_reader.py + roles/verify_lens.py for the self-registering ROLE-dict + Pydantic shape to MIRROR). REUSE-DON'T-PARALLEL.
- THE FLOOR STAYS: a role is declarative; emit NO resolve/approve/dispatch, launch NO claude -p.
- registry-is-truth (file-discovered roles/<id>.py) · NOTHING static · fail-loud · additive.
- Work ONLY your lane's file. Do NOT edit the other lane's file, runtime/*, mcp_face/*, or roles/AGENTS.md (next beat reflects new roles). Do NOT commit.
- GPU: the mining fire needs chat-4b — check \`company gpu\`; \`company up chat-4b --wait\` if down (async, gated, no stomp). NO Gemini · NO green-paint.
- On finish: write build-prep/cognition-self-improvement/seam-lanes/<lane>.report.json {lane, files_written, new_role_ids, how_verified, status, needs_tim, notes, findings}.
`

const SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['lane', 'files_written', 'how_verified', 'status'],
  properties: {
    lane: { type: 'string' }, files_written: { type: 'array', items: { type: 'string' } },
    new_role_ids: { type: 'array', items: { type: 'string' } },
    how_verified: { type: 'string' }, status: { type: 'string', enum: ['built-verified', 'built-untested', 'blocked'] },
    findings: { type: 'string', description: 'the actual mining findings (pattern_tags + notable decisions/corrections) — the value' },
    needs_tim: { type: 'string' }, notes: { type: 'string' },
  },
}

phase('Build')
const built = await parallel([
  // ---- LANE MINE: build mine_exchange + RUN a bounded real mining (the findings) ----
  () => agent(`${LAWS}
LANE MINE — COMPOSITIONS ③ the transcript-MINER role + a BOUNDED real mining run. Build NEW roles/mine_exchange.py: a MAP role that reads ONE conversation exchange (a Tim-message + my-response pair) → structured self-improvement extract. MIRROR roles/verify_lens.py (self-registering ROLE dict + Pydantic out class; the exchange rides in the unit/utterance). op:generate; mode_scope a 'mining' context (cast-beyond-listening; listening untouched).
${MINE_SCHEMA}

THEN RUN A BOUNDED MINING (the value, BY USE): the transcripts are /home/tim/.claude/projects/-home-tim/*.jsonl. EXTRACT (deterministic, your code) ~12-15 exchange-units from ONE or two recent jsonl files (parse the jsonl: a 'user' message followed by the 'assistant' response = one exchange; take the text content; bound to ~12-15 to keep it one beat). Fire run_items(mine_exchange, those units) on the resident chat-4b → per-exchange extracts. REPORT THE FINDINGS: the pattern_tags that recurred + any notable decisions/corrections/needs-tim the mining surfaced (this is the actual self-improvement signal — real findings about how-I-work-with-Tim). The full all-transcripts mining + the embed-CLUSTER of pattern_tags into failure-pattern groups is the FOLLOW-ON (needs the embedder window — flag it).
FILE-DISJOINT: ONLY roles/mine_exchange.py (+ READ verify_lens.py/screen_reader.py). Do NOT edit judge_mining (other lane) or roles/AGENTS.md.
VERIFY BY USE: RoleRegistry().discover(['roles']) shows mine_exchange live; the bounded run returns well-formed extracts; floor (cognition_governance_acceptance) passes (roles_acceptance will red ONLY on 'drift: [mine_exchange]' un-reflected — EXPECTED, next beat). Report new_role_ids:["mine_exchange"] + the FINDINGS + the by-use result. Do NOT commit.`,
    { label: 'mine', phase: 'Build', schema: SCHEMA }),

  // ---- LANE JUDGE: build judge_mining (the no-fiction validator) ----
  () => agent(`${LAWS}
LANE JUDGE — COMPOSITIONS ③ the mining CONFIRM role. Build NEW roles/judge_mining.py: a role that validates ONE mine_exchange extract against its RAW exchange — the no-fiction gate (did the miner fabricate a decision/correction not actually in the exchange?). MIRROR roles/verify_lens.py's shape. input unit: {extract (a mine_exchange output), raw_exchange (the source text)}. output_schema: {grounded: bool (is every claimed field actually supported by the raw exchange?), unsupported: str (which claim isn't grounded, or ""), confidence: float}. op:generate; mode_scope 'mining'. The mine_exchange contract it validates:
${MINE_SCHEMA}
FILE-DISJOINT: ONLY roles/judge_mining.py (+ READ verify_lens.py). Do NOT edit mine_exchange (other lane) or roles/AGENTS.md.
VERIFY BY USE: discover live; fire judge_mining (chat-4b) on ONE mock {extract, raw_exchange} pair where the extract FABRICATES a correction not in the raw → grounded:false + unsupported names it; and a faithful pair → grounded:true. Floor passes. Report new_role_ids:["judge_mining"] + the adversarial by-use result. Do NOT commit.`,
    { label: 'judge', phase: 'Build', schema: SCHEMA }),
])

const ok = built.filter(Boolean)
log(`Build: ${ok.length}/2 · new roles: ${ok.flatMap(b=>b.new_role_ids||[]).join(',')||'-'}`)
return { built: ok }
