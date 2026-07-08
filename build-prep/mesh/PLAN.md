# THE MESH — build plan (banked 2026-07-08; Tim: "do every part of this")
*Companion to THE-ONE-IDEA.md (the statement) and ANCHOR.md (the seed). This is the working plan —
UPDATED as the census lands (Tim: "bank it, do something similar to a dragnet so that you have a
full inventory, a top logical map of everything, and you update your plan wherever needed to
integrate... some parts have already been partly built; you will likely find more opportunities
just by looking"). Every phase lands something alone-useful. Status column is live.*

## Phase C — THE CENSUS ✅ DONE 2026-07-08 (THE-CENSUS.md · mesh://census/1 + /batch/1-10)
77 territories · 42-item dormant register · top map: "a federation of self-registering modules
(constitution + row-files + runtime loader + acceptance test) — load-bearing but SYSTEMATICALLY
INCOMPLETE: constitutions enumerate smaller live sets than directories contain."
**C.3 integrations (census → this plan):**
- **Phase 0 fragment confirmed:** `ops/hooks/registry_freshness.py` IS the existing SessionStart
  context-injection pattern (the boot-brief composer extends this seam; its "Python generalization"
  was already parked — we're the return-condition).
- **A1 fragments found:** `runtime/activation_driver.py` (an "always-on caller", dormant) +
  supabase `realtime` container = the data-driven-trigger residents Phase 6 builds on. Also
  `routines/dragnet_freshness.py` + `routines/guide_freshness.py` (dormant freshness beats —
  the heartbeat absorbs them, not re-invents).
- **Phase 6 gains a check:** constitution-vs-directory drift (the census's systematic finding —
  e.g. mark_types 14 undocumented rows) becomes a standing heartbeat query.
- **Real defect leads to verify:** the claimed chat-history regression (runtime/suite.py ~3756,
  two sessions locate it differently) · edge_kinds inverse-law contradictions (authored_by declares
  inverse authored; no authored.py exists) · 21 uncommitted files on main · 3 fully-merged
  worktrees lingering (~/company-interactive, -night, -overnight).
- **Known false-positive class (recorded, don't chase):** "truncated mid-dict" findings = my
  gatherer's 900-char file heads (truncation-honesty gap in the MATERIAL, fix in gather());
  "README says nothing implemented" = a stale README, itself a doc-drift find.

## Phase 0 — THE SURFACING LAYER (the storage≠memory gap Tim named)
| # | What | Known existing fragments (census to complete) | Status |
|---|------|------|--------|
| 0.1 | Boot-brief composer: laws (operator rules) + current-work anchors (mesh://doc, .state, git) + latest mesh://round + open escalations — resolved from addresses AT COMPOSE TIME, bounded ~1-2K tokens, every item address-carrying | `capabilities`/`now`/`context` verbs; HANDOFF.md/STATE.md (hand-kept — become generated faces) | todo |
| 0.2 | Three doors: SessionStart hook (Claude Code in ~/company) · session-supervisor spawn context · a `brief` verb (MCP/in-universe) — ONE composer | SessionStart hook infra EXISTS (fires today: cleanup-mcp + registry-freshness); supervisor `_provider_env` spawn path; agent-boot-sequence + context-continuity skills (become thin wrappers over the brief) | todo |
| 0.3 | Verify by use: fresh session wakes already knowing THE-ONE-IDEA | — | todo |
Phase 0 is deliberately the FIRST A1 PROTOTYPE: dynamic context-resolution-from-variables — the
same composer later feeds in-universe residents' turns.

## Phases 1–8 — the pyramid proper
1. **Ledger recon** — read the pre-formed address tree in the supabase docker; attachment contract
   from Tim's structure (reuse-don't-parallel).
2. **L0 deterministic pass** — absolutes (size/time/position/reply-to/ext=type/name=id/git) over
   every exchange + file → attach to tree. No model.
3. **L1 0.8B open-universal tagger** — chat-08b warm; open vocab (domain-specific tags INVALID);
   A/B on one session before scale (the measured-gates law).
4. **First cluster→kimi-canonicalize** — run_reduce(cluster) over L1 tags; kimi-2.7 resolves;
   tags become addressed, lifecycled nodes (proposed→clustered→canonical|escalated; faces law).
   THE LOOP EXISTS HERE.
5. **4B rule-routed layer** — AWQ beside embedder (measure co-residence; verify Tim's 32-concurrent
   by use, record real numbers); allocations COMPUTED from L0+L1 state.
6. **Heartbeat** — re-observe only what changed (git-diff / new transcript tails); boot-brief
   freshness rides it; survey → living. First native in-universe inhabitant (A1).
7. **Escalation queue + laws circuit** — persisted addressed queue for Fable-court; mined laws →
   operator propose→confirm gate.
8. **Dormancy view + completion proposals** — standing query (parked-vs-forgotten mechanical via
   condition-addresses); forgotten + reaching-for + code:// ⇒ addressed build-candidates → Tim's
   gate → the cron build organs.

## Continuous (already running underneath)
- Archaeology batches (mine_design_intent, kimi) → design_intent space (600+ records).
- Mesh triangulation rounds (self-steering territories).
- Laws found anywhere → the operator propose circuit (Tim: "yes to all the laws").

## Standing disciplines (from the session's measured lessons)
Measured gates before scale (A/B every new layer) · deterministic-work-to-code · no cloud token
budgets · native structured output for ollama · declared bindings honoured · truncation always
declared · faces never flattened · counts-not-confidence (G16) · extract-the-law-before-retiring.

## THE TRUNCATION LAW (Tim, 2026-07-08 — standing, self-indicting)
"Any time you find truncation you should remove it — that's just lazy design." Truncation caps were
cost-era economics; the cost era is over (free local tiers, uncapped cloud). Sampling-by-truncation
is the same disease as sampling-by-curation. WHERE A REAL LIMIT EXISTS (a context window), chunk
COMPLETELY (late-chunking / reduce-tree — coverage-preserving), never cut. Known sites to purge:
transcript_extract MAX_TIM=1200/MAX_REPLY=2000 (**the archaeology has been mining truncated
exchanges — re-mine after fix**) · mesh gather() 900-char file-heads + 7KB cap (chunk→multiple
units instead) · triangulator notes[:60000] (deepen the reduce tree instead) · session_recall's
600-char rerank slice (reranker window permitting) · any [:N] on model-bound material anywhere.

## THE SPIRAL LAW (Tim, 2026-07-08 — the posture for everything found)
"0 of it is trustworthy as the intent — it's all that spiral. Enough has become coherent that parts
function, and I've been getting enough parts functioning so that it can be involuted." EVERYTHING any
agent finds (tools, schemas, designs, docs) was made by other agents in conversations from Tim —
attempts toward the same centre from multiple angles (deliberate: mitigates single-agent + Tim limits;
plan-a-jobs/ + plan-b-coordinates/ are literally two named angles). Therefore: NOTHING found is spec;
nothing on its own is right; ATTACK what you find (gaps, opportunities, what should be there that
isn't); FOLD your own strengths/designs/laws over the existing work to smooth its edges — never defer
to it, never replace it. THE REAL THING IS BETWEEN THE ATTEMPTS. No agent has the whole picture. The
goal state: cross the involution threshold — enough functioning parts, turned inward, self-referencing.
Directive: keep going with the tools → then design/pin-out/lay out capabilities, goals, requirements,
tools, dependencies + strategy for the whole.

## THE OPEN-VOCABULARY LAW (Tim, 2026-07-08 — "how come there's an allow list?")
Schema constrains SHAPE, never MEANING. A closed enum on a judgment-word is predetermination — and
under schema-constrained decoding it is CENSORSHIP AT THE DECODER (the model cannot say what it saw;
the census + kind retry-burns were the ENUMS failing, not the models). Coercion-onto-my-list is the
same sin twice (it destroys the pile-up signal nucleation feeds on — the operators-space keystone:
content no type covers piles up → a candidate new type). The lifecycle is the road between the two
ditches (closed enum ↔ the 88%-noise ungoverned strings): OPEN word at the decoder → embed → cluster
(pattern_cluster / run_reduce(cluster)) → a kimi seat names/canonicalizes → outliers escalate →
canonical vocab lives as COUNTS + addressed registry rows (G16), cited in prompts as guidance-with-
invitation-to-coin, NEVER as a decode constraint. A closed set is legitimate ONLY where CODE branches
deterministically on it (an ordinal dial like design_weight) — and even then the raw word should
survive. Shape-adapters (string→{claim}) that preserve the model's words are fine; word-mappers are
not. Applied: mine_design_intent.kind · triangulate_mesh.verdict · observe_territory.state all opened.
Corpus note: v2 kinds (pre-open) were decoder-constrained — an artifact distribution; statements/
reaching_for/gist are open text and untouched, so the cluster layer canonicalizes from CONTENT (no
re-mine needed); new captures carry the model's own words.
