# recollection — BUILD-ORDER REFRESH & FULL-SCOPE LINE-UP (2026-06-17)

*Tim's directive (2026-06-17): "get the full scope, map it out and line it up and build through it all. Use my principles + architectures, involve the others where needed, big value. Always build in MORE of the system than you plan for, avoid repeating things, aid the union objective." This doc refreshes the sound-but-stale Jun-14/15 loop-prep (COMPLETION_CRITERIA + IMPLEMENTATION_GUIDE + RESEARCH_SYNTHESIS + OPEN-DECISIONS + seam-mapping — all still canonical; this is the current-state + lined-up build-through over them). Grounded by two read-only explorer waves (loop-prep currency + recollection codebase state) + this session's R1–R10.*

## A. CURRENT STATE — the spine is BUILT, the apex is the GAP (verified)

| Stage | What EXISTS now (verified) | State | The GAP to build |
|---|---|---|---|
| CAPTURE (P10) | parser·indexer·sync(live-hook)·backfill(~13k, sidechains)·board/clone sources; ~/.recollection sqlite-vec | ✅ built (live=SessionStart→sync) | mid-session/Stop distill-triggers; non-CC modalities |
| DISTILL (P5) | L1 summarizer ✅; L2 harness+extractor+unit-types **scaffold on a STUB**; ratify=throws | ◑ L1 built · L2 scaffold-on-stub | wire the REAL served-4B into extractor; wire-in Company forms/lifters; the ratification gate |
| EMBED (P2) | served :8007/pplx-2560 single lens, fail-loud, dim-validated; registry shaped for many | ◑ single-lens built | the multi-lens loadout (sparse/code/visual/context + MINED steering) |
| LINK (P6) | crossings MECHANICAL graph ✅ (produced_by/references/precedes/contains); links table | ◑ mechanical built · semantic absent | semantic concept-link lane; ★WIRE-IN Company find_relations + relation_types (now BUILT — reuse) |
| GATHER (P3) | search(vector/text/both, per-axis, scopes)·recall(5 wires)·navigate ✅ | ◑ top-k built | the decompose→classify@120→gather-all-aggregate (Classification-Law) |
| JUDGE (P4) | verdicts+atoms tables (schema, ZERO writers); candidate staging works; corpus_rerank exists | ○ absent/stub | THE judgment layer: proofreader→set-reader→jury, typed verdicts, the registry (reuse corpus_rerank as proofreader/set-reader) |
| RECALL (P7/P8) | MCP search/read/recall + navigate + /api/cognition/neighbours; PULL-only | ◑ on-demand built · ambient absent | P8 proactive injection (SessionStart floor — D-10 cached); the deep sub-agent |
| HEALTH | verify·doctor·stats·sync-sentinels·embedding-migration ✅ | ◑ index-health built | the temperature scan (resistance) + the annealing dream-phase |

## B. REUSE-DON'T-REPEAT — the convergences to WIRE-IN (the union objective)
*The Company grew toward what recollection planned to hand-roll standalone. Fold these in; do not parallel them.*
- **LINK** → Company `find_relations` (suite.py:10854, mcp_face:918) + `relation_types/` registry + `lifters/links.py` edge-extractor. recollection's semantic-link lane wires onto these, not a parallel graph.
- **DISTILL** → Company `forms/` (decision/log/prose) + `lifters/` (blocks/frontmatter/links) — the typed-extraction machinery, BUILT-BUT-UNWIRED (R9). recollection's L2 distill wires THROUGH forms/lifters (file-type→output-shape) instead of the flat repo_digest. This ALSO closes R9 for the Company coverage — one wire serves both (aids the union).
- **EMBED/publish** → Company `common_knowledge` space (Option A, live) + the pplx-2560 spine. recollection PUBLISHES comprehended units here (absorption already started — updates D-8).
- **JUDGE** → `corpus_rerank` (jina-v3 :8008) = the proofreader/set-reader precision pass; reuse, don't rebuild reranking.
- **RECALL primitive** → `/api/cognition/neighbours` (recall-under-a-unit, live) = a built recall arm; recollection's gather/navigate compose it.
- **ADDRESSING backbone** → DNA's SUBSTRATE-ARCHITECTURE (repo-as-addressed-typed-queryable-graph) = the per-project address layer; recollection's crossings(=typed-edges) + corpus(=attachments) + multi-space-addressing converge with it. Build recollection's addressing AS an instance of it.
- **INNER arm** → fork's `session_recall` (the per-session retrieval spine) + `resolve_address`/`territory_for`. recollection WRAPS it (outer cross-session/temporal/identity); the 4 seam-wires (seam-mapping.md) hold.

## C. THE LINED-UP BUILD-THROUGH (dependency-ordered; build MORE than the minimum at each)
*Spine is built — do NOT rebuild. Build through the apex + the wire-ins, in dependency order.*

- **BEAT 1 — DISTILL real + forms/lifters wire-in.** Replace the extractor stub with the served-4B (the path exists, model-gated); route L2 extraction THROUGH the Company forms/lifters (file-type→form→stage/policy + lifter structure). Build-more: this closes R9 for the Company too. [touches: composition (forms/lifters), lead (the served-4B / capture seam)]
- **BEAT 2 — EMBED multi-lens.** Add lens entries to the registry (sparse/code/visual/context) + the steering-vocab MINING pass. Build-more: the `#emb=` multi-layer mechanism already exists Company-side — populate the lenses there too. [touches: lead (GPU loadout sequencing)]
- **BEAT 3 — LINK semantic + find_relations wire-in.** The semantic concept-link lane (embedding near-pairs → graded `links`) onto the existing mechanical graph; wire recollection's edge layer to Company `find_relations`/`relation_types`. Build-more: cross-project concept links (Pillar-2). [touches: fork/lead (relation_types co-scope)]
- **BEAT 4 — JUDGE (the apex).** proofreader (corpus_rerank reuse) → set-reader → jury (4B, rule-driven); wire the verdicts+atoms writers; the open judgment registry; ratify the gate (with Tim). This is the keystone — recovery-quality that GATES autonomy. Build-more: the jury as a general machine (also "what should the agent ask?"). [touches: lead (core-engine co-scope), Tim (ratification seat)]
- **BEAT 5 — GATHER full.** decompose→threads→registry-typed classify@~120 concurrency→typed lookups→two modes (top-k + gather-all-aggregate / pool-across-time = Pillar-2 apex). [reuses cognition.run_items the swarm]
- **BEAT 6 — RECALL proactive (P8).** the SessionStart cached-floor (D-10) + in-session injection (mode-gated) + the deep sub-agent (gather→judge→follow-up→assemble). Build-more: usable by ALL fabric sessions, not just internal. [touches: all sessions (the floor), lead (hook policy)]
- **BEAT 7 — HEALTH.** temperature/resistance scan (structural↔semantic distance) + the annealing dream-phase (re-place drifted, split/merge, fold duplicates). [cross-cutting, runs once there's volume]
- **CROSS (every beat) — UNION seam + addressing backbone:** publish to common_knowledge; build addressing as an instance of the SUBSTRATE-ARCHITECTURE; keep the fork↔recollection 4-wires + add the recollection↔Company-corpus seam to seam-mapping.

## D. DISCIPLINES (Tim's, standing — apply every beat)
registry-is-truth / no-hardcoding (everything grown) · conversation-is-source-of-truth, code-is-lossy-projection · the four root axes (scale/time/frame/state) · verification-state on every unit (verified-by-use, no green paint) · FUNCTION+FORM both (the recall surfaces have a form face) · commit-to-main no-branches · no-versioning (update in place) · reuse-don't-parallel · build-more-than-planned · scout-before-build (the explorer waves) · involve the streams at the co-scope seams (don't collide — file-disjoint / propose-diff where it's their lane).

## E. OPEN DECISIONS: ZERO (all D-1…D-15 resolved with evidence, 2026-06-14). Build-order is the only open choice — lined up above; Tim adjusts.

---
## F. ★ INTO-THE-CENTRE REFRAME (lead/Tim law, 2026-06-17) — supersedes any island-build in §C
THE LAW: the COMPANY is the single CENTRE of all building (not frozen — it gets improved continuously); an island's GOOD PARTS are absorbed INTO the company (the centre improves to hold them), then the island drops its parallel scaffolding to ride the company spine. Direction of accumulation = always INTO the centre. recollection IS an island.

IMPACT on this build: the apex is NOT completed inside ~/recollection — it is built INTO THE COMPANY (runtime / cognition / the registries / the corpus), absorbing recollection's good design; recollection then SHEDS its parallel structure (own sqlite-vec store · own MCP server · own embed client) to ride the company spine (the corpus · :8007 · the MCP face).
- COMPANY ABSORBS (improves to hold — the apex it lacks): JUDGE layer + open judgment registry + verdict/atom writers · proactive injection (SessionStart cached-floor + deep sub-agent) · the multi-scale typed UNIT model · multi-lens + mined steering · full GATHER (pool-across-time) · HEALTH (temperature + dream-phase) · the 8-stage recall design.
- recollection RIDES (already in the centre): find_relations + relation_types · forms/lifters · common_knowledge · corpus_rerank · /api/cognition/neighbours · session_recall · SUBSTRATE-ARCHITECTURE.
- CO-SCOPE: building into the centre's core (cognition.py/suite.py/registries) = the lead's lane, R13 byte-identical discipline → propose-diff / file-disjoint, never route around. composition co-owns forms; fork co-owns relation_types.
- The §C beats still hold as the WHAT; their WHERE is now "into the company centre," co-scoped, sequenced with the lead against the active union-build/#71/legibility.
