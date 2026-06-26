# Coverage-First Pre-Build Runbook
*Tim's coverage methodology (2026-06-17), grounded in the actual built tools/roles. Coverage ≠ search: the directory boundary is the objective marker; every region reports what's FOUND (open-ended), not what was sought. PROVISIONAL — awaits Tim's OK on the compute run + the methodology-as-standard. Ancestral learnings (recollection) to be folded before running.*

## THE STAFF (roles) + FLOWS that already exist for this
COVERAGE roles: **repo_digest** (open-ended per-file: {digest = what it IS + its role; kind = code|doc|config|test|data}) · **interpret_file** · **screen_reader**. Synthesis: **reduce_synth**. Design: **decompose_seed → expand_criterion → ground_criterion → triad_synth** (the spec-compiler → the 3 loop-prep docs). Panels: **develop_option → score_options** (option-panel) · **verify_lens/verify_jury** (verify-jury). Grounding/judges: **ground · judge · judge_drift · judge_mining**. Mining/registry: **mine_exchange · register_element · confirm_registration · atlas_linker**. Misc: **recall · embed · connect · focus · check · element_fit_lens · voice/voice_lens · eval_classify**.

FLOWS (cascades): `ask-the-codebase` (retrieve→synth) · `eval_digest_reduce` (repo_digest MAP → reduce_synth) · `spec-compiler` (the 3 docs) · `option-panel` (options→score→recommendation+grafts) · `verify-jury` (verify_lens→verdict-tally) · + eval probes.

## PHASE 0 — BOUNDARY + HYGIENE (the objective marker)
- Directory scan (done, first pass): 125,231 files / 8,266 dirs RAW — but artifact-inflated (~14k .pyc, 9.4k .h, .so/.gz/.dat/.map) AND ~40 registry dirs each report ~2,080 files (a vendored tree buried in them). The MEANINGFUL boundary ≈ 14k .py + 3.7k ts/js/mjs + 1.2k .md + real configs.
- TODO: resolve the ~2,080-per-dir vendored anomaly → exclude it → the TRUE source boundary (the denominator).
- Cross-check coverage: corpus has 2,625 company records but the sampled ones are role/operator digests, not source-file digests → the source-file coverage in the `repo` space is unverified. Compute GAP = source-boundary − already-digested (corpus find by source_address code://).
- OUTPUT: a COVERAGE MANIFEST = {region → {file count, types, sizes, already-covered, gap}}. The objective marker everything is measured against.
- NEW TOOL (currently shell): the boundary-scanner should be an MCP tool — the coverage-orchestrator's first step (on the gaps board item-501c4188).

## PHASE 1 — FULL COVERAGE (allocate by space, open-ended digest)
- Partition the boundary by directory region.
- Fan **repo_digest** over EVERY file in each region (open-ended "what is this + its role", not "find X"). Mechanism: **ingest** (walk→digest-fan→embed; reports walked/digested/remaining/corpus_total) for the bulk; **run_items**/**capture** for finer control + a durable sink.
- ALLOCATE BY TIER (the net-new orchestration): small/simple files → the resident local 4B swarm (run_items); large/complex regions → cloud (kimi/deepseek via model=) ; the hardest/whole-file-reasoning → a Claude Code launch (routines/cc_clone). Allocation keyed to region + file size/type.
- COVERAGE MARKER: loop each region until remaining=0 → PROVABLE complete coverage (the thing my 3 search-scouts never had).
- PERSIST: each digest → a corpus record (capture: durable cas:// + run://corpus pointer + index event), embedded in `repo`/`common_knowledge`.

## PHASE 2 — LAYER UP (understanding in layers)
- Per region: run_reduce(mode=role, role=reduce_synth) over its digests → a region summary (or the eval_digest_reduce cascade).
- Cross-region: reduce the region summaries → a whole-coverage understanding (file → region → whole).
- Discovery pass: run_reduce(mode=cluster) + find_relations(near/far space) → "same principle, different place" → surfaces drift/duplication the coverage exposes.

## PHASE 3 — PROPOSED DESIGN (from complete coverage, not assumptions)
- Seed = the whole-coverage understanding. run_cascade(name='spec-compiler', inputs=seed): decompose_seed → expand_criterion(fan) → ground_criterion (reuse-vs-net-new, grounded against the now-complete corpus) → triad_synth → the 3 docs (Completion-Criteria two-faced FUNCTION/FORM, Implementation-Guide with reuse seams, Research-Synthesis = the reuse-map).

## PHASE 4 — PANELS (perspectives, additions, adversaries)
- run_cascade(name='option-panel', ...) on the design → scored options + recommendation + GRAFTS (additions/perspectives).
- run_cascade(name='verify-jury', ...) on the design's claims → adversarial verification (catches green-paint).
- HONEST GAP: the `panel` TOOL has NO registered verdict_panels in this env — so the jury comes via these cascades; named multi-seat panels would need create(kind='role') seats + a verdict_panels/<id>.py (optional upgrade).

## PHASE 5 — DESIGN → DISPATCHED BUILDERS
- The vetted triad → dispatch builders (Claude Code launches via routines/cc_clone, or the fork/streams), each owning a criterion, the Completion-Criteria as the truth-table, verify-by-use.

## REUSE vs NEW (honest)
- REUSE (built): repo_digest · ingest · capture · run_items · run_reduce · spec-compiler · option-panel · verify-jury · find_relations.
- NEW (to build): (1) the boundary-scanner MCP tool + the coverage manifest/marker; (2) the allocate-across-tiers orchestrator (ingest is local-swarm-only today; region→cloud/claude-code routing by size/type is new); (3) optional registered panels.

## ★ REFINEMENTS (Tim, 2026-06-17 #2) — hardening to his principles (grounded)
The naive flat-digest plan is REPLACED by a layered, hardened pipeline:
- **Structured output = a real mechanism, NOT prompt** (confirmed `fabric/transport.py:_apply_response_format` → `response_format=json_schema`, derived from output-fields `fabric/client.py:78`). Use the role's enforced output-schema, never prompt instructions.
- **Forms wired in but OPTIONAL** — `FormRegistry.route()` (forms.py:171) exists, unused by capture. Add an OPTIONAL capture→route switch (available, off by default). NOT always-on.
- **Forms (and registries) SCOPED global / project / user** — no scoping exists today (forms is flat). Add the three tiers; one user now; project links to the running project. Likely the general registry pattern.
- **Pass 0 = programmatic scan → IGNORE-LIST** — scan the whole tree (depth, counts, addresses, extensions) → build an ignore list (cut vendored junk inflating 125k→meaningful) → read the remainder. Ignore-driven, not add-all. (The boundary tool — currently shell.)
- **Chunk, don't truncate** — over-context MODEL chunker exists (cognition.py:1431 chunk-and-compose); the EMBED side leaves chunking to the caller + can truncate → make ingest chunk for embed (check current max first; [[reference-pplx-embed-leaks-under-load]]).
- **Deterministic structure, not model-guessed** — NO code import/export lifter exists today (lifters are markdown-only: links/blocks/frontmatter, `lifters/`). BUILD an AST-based code lifter (capture ALL imports/exports reliably); extend the markdown links lifter for relations/descriptions from referencing files. The model only does the OPEN-ENDED part.

### THE REFINED LAYERED PASS
```
Pass 0  programmatic scan → ignore-list → read-set            (boundary marker)
Pass 1  deterministic lifters (no model): imports/exports[code] · links/relations/frontmatter[md]
Pass 2  model digest, schema-enforced (response_format=json_schema), thinking OFF, chunk-not-truncate
        └ forms.route() AVAILABLE (optional tiering, off by default)
Pass 3  embed (chunked) → records {structure + description} → coverage ledger → layered summaries → Tim
```
REUSE: json-schema enforcement · over-context chunker · markdown lifters · FormRegistry.route · walk→digest→embed ledger.
BUILD: code imports/exports lifter · forms global/project/user scoping · optional capture→forms wire · pass-0 scan→ignore step · embed-side chunking · harden the digest role prompt+fields.

NOTE: the current forms taxonomy (decision/log/prose/registry) is Tim's PLACEHOLDER ([[FORMS-ARE-PLACEHOLDER]]) — forms come FROM the coverage, defined to his principles AFTER we see what's there; don't lock them.

## ★ MODEL-TIER ROUTING (grounded in the company's OWN SEM-research, Tim 2026-06-17 "use it all")
Extraction-vs-judgment, empirically validated (build-prep/coherence/SEM-1/2/3 + SEMANTIC-LAYER):
- **4B SWARM (resident :8000, ~32 concurrent) = the EXTRACTION/census tier.** Per-file digests + structural tagging + form/lifter recognition = bounded + schema'd + per-unit = its proven sweet spot. ★ Use json-SCHEMA structured output (not prompt-only) — the reliability key. It is a HIGH-RECALL PRE-FILTER, NOT an adjudicator; it can't do open cross-repo discovery.
- **JUDGMENT/CONFIRM tier (cloud kimi/deepseek, or local nemotron-30B) = confirms the swarm's output.** "Schema+jury reduce noise but can't guarantee truth → a stronger-model confirmation is the necessary keystone." The synthesis/judge steps run here.
- **EMBEDDINGS (pplx :8007) + RERANKER (jina :8008, CPU/0-VRAM)** = recall/neighbour/coverage-marker — already on, free precision.
- **OLLAMA CLOUD (kimi/deepseek-flash)** = off-card mid tier + clones + build-brain (deepseek-flash for >256K).
- ★ #71 (model-routing) is the MECHANISM that makes this automatic (resolve_model: extractor→4B, judge/synth→cloud) — the census routes through it.
- RESOURCE LAW: resident 4B + pplx-embed + CPU-reranker + cloud = FREE (no VRAM load). Loading nemotron / bge / jina-v4 / qwen3-8B contends for the card → CONSULT TIM before loading (or use cloud for judgment, no load).

## DECISIONS FOR TIM (the OKs)
1. Green-light the FULL COVERAGE compute run (Phase 1 across the swarm/tiers) — real compute.
2. Make this coverage→design→panel pipeline the STANDARD pre-build ritual (the executable form of scan-before-build)?
3. Tier policy: how far to lean on cloud/Claude-Code vs the local swarm for the hard regions.
