# Full-coverage dragnet recall — PROVEN by-use at small scale (the #65 engine)

*Tim's reframe (lead t-1781961622): #65 isn't a search (top-k sampled) — it's a DRAGNET: push ALL corpus+transcript through local concurrent models, each judging relates?/how?. The 99%-no is the COVERAGE PROOF. Local=free → wasteful IS the feature. This is the MAP in map-reduce (dragnet=MAP → synthesize survivors=REDUCE). Critical-comparison FIRST: prove the engine by-use small before scaling. Done — with a key finding.*

## PROVEN (by-use, local-4b, 2026-06-20)
- **Engine**: `cognition.run_items(role, [N chunks], store, turn_id=…)` fans 1 role × N units concurrently on chat-4b (:8000, RESIDENT default). 20 real corpus chunks → **2.1s, 20/20 clean structured JSON, 0 failed, ~10 chunks/sec concurrent.** Structured output (`relates: bool, how: str`) returns clean per-unit. The 32-concurrent structured dragnet on local is REAL + runnable today (chat-4b verified serving — real completion, not just /health).
- **Correctness**: with a neutral topical-overlap prompt + topic "memory/recall/searching past conversations", it correctly flagged 12/20 with accurate `how` phrases (chunk[0]→"searching historical conversation memory"; chunk[1]→"searching past conversations/history"). Genuine separation, accurate connections — not noise.

## ★ THE CRITICAL FINDING (default-to-wrong caught it in my OWN proof)
The dragnet's never-miss property is **PROMPT-SENSITIVE**. My v1 prompt said *"judge strictly — most content will NOT relate; that is expected."* Result: **0/20 relates — FALSE NEGATIVES** (it missed chunk[0] "search historical memory" + chunk[1] "episodic memory tools", which plainly relate to recall). That 0/20 would have been mis-reported as *"works! the 99%-no coverage shape!"* — but it was JUDGE BIAS, not coverage. v2 (neutral prompt, same chunks, broader-but-fair topic) → 12/20 correct.
**LESSON (the design depth for #65):** "be wasteful / expect 99% no" is an OBSERVATION of the aggregate output, **NEVER an instruction to the per-chunk judge.** The judge prompt must ask only genuine topical overlap, with NO prior on the answer rate. A prejudging prompt turns the never-miss dragnet into a miss-machine — the exact "comes back saying it's right when it isn't" failure, inside the tool. This is why the dragnet ≠ embedding-floor: it reads the CONTENT, but only if the judge is unbiased.

## DRAGNET vs EMBEDDING-FLOOR (both kept, different jobs)
- Embedding search RANKS (fast first-cut, top-k) — needs the relevance floor (the no-floor bug: off-corpus "souffle" → confident hits; real 0.47-0.49 vs noise 0.31). For SAMPLING.
- Dragnet NEVER-MISSES (reads every chunk's content) — for COVERAGE/certainty. Wasteful by design; local=free pays for it.
- map-reduce: dragnet=MAP (every chunk→relates?/how?, structured, concurrent) → REDUCE (synthesize survivors, central judgment). [[extraction-vs-judgment]] — small models extract, central judges.

## NEXT (before the full self-referential run)
1. ★ NEUTRAL JUDGE PROMPT — bake the finding in (no answer-rate prior). The one design decision that makes-or-breaks coverage.
2. Coordinate fork (engine owner): run_items 32-concurrent at full corpus scale (35,904 transcript chunks + corpus) — batching, throughput, cloud-open via fork's think-fix for big-ctx.
3. SELF-REFERENTIAL first run (Tim): dragnet the session history to RECOVER the discussed design depth (structured-outputs / allocation / what-prompts / feeding) — the pattern proves itself by recovering its own design.
4. Author the `theorem-mine` / `dragnet` skill (the recipe) + wire as a Workflow (my first real one — pipeline: dragnet-MAP → reduce-survivors).

## ★ THE RELIABLE + GENERALIZABLE RECIPE (Tim 2026-06-20: "continue till it works useful, reliable, generalizable" — got it)
Critical-comparison vs a keyword ground-truth exposed the real reliability flaw + the fix:
- **The flaw:** a BINARY-relates worker (even with a neutral prompt) has a local-4b **NO-LEAN** → it's conservative → it MISSES borderline-relevant content (vs keyword ground-truth: 21 keyword-hits not flagged; most were keyword-false-positives the dragnet rightly rejected, BUT the NO-lean is real + defeats never-miss). A filtering worker can miss.
- **THE FIX (Tim's design, proven):** split MAP into EXTRACT (worker) + DETERMINE (central):
  - **WORKER = neutral EXTRACTION** — `{about: phrase, touches: [topic tags]}`. NO topic, NO relevance call, NO "judge strictly", NO aggregate prior. The worker DESCRIBES, never filters — so it CANNOT miss (Tim: "they shouldn't have that kind of context"). Local, free, ~7 chunks/s.
  - **DETERMINE = central** — reads the cheap extractions (not the full chunks) to decide relevance to the topic (Tim: "output that gets looked at to then determine"). Consistent because it's one judge over uniform extractions.
  - RESULT: misses 21→8 (residual = keyword-false-positives, e.g. "wait for D2", "discovery-first stance" — not real design content); caught 45 vs keyword's 25 (20 semantic catches keyword missed). Never-miss restored.
- **★ THE GENERALIZABILITY WIN:** the worker extraction carries NO topic → EXTRACT THE CORPUS ONCE, DETERMINE FOR ANY TOPIC against the stored extractions. Dragnet-once, query-many — not re-reading the corpus per question. The extraction layer is a reusable asset (embed/store it → every future question is a cheap central determination over it).
- map-reduce final shape: **EXTRACT (worker, neutral, once)** → **DETERMINE (central, per-topic)** → **REDUCE (synthesize survivors)**. Verified useful (topic-1: 39 accurate survivors + correct synthesis), reliable (misses closed via extract-not-filter), generalizable (extract-once/query-many, topic-agnostic worker).

## ★ THROUGHPUT MEASURED (gate 1, 2026-06-21 — corrects the "32-concurrent / batching cuts it hard" assumption)
Measured the REAL saturated rate before committing the full run (default-to-wrong: measure, don't assume batching helps):
- **Real concurrency = 14 slots**, NOT 32. chat-4b is `max_num_seqs: 16` (hybrid-Mamba CUDA-graph cap — >23 fails); SlotBudget = 16 − reserve_r 2 = **swarm_slots 14**. The "32-concurrent" was a wrong assumption.
- **Coarse SATURATES at ~8.4 chunks/s** — N=16→7.3/s, N=48→8.1, N=96→8.4 (plateau). It's ALREADY at the 14-slot ceiling at small N → **batching does NOT cut it further** (the bottleneck is 14-concurrent × per-request latency, not batch size).
- **Full-run estimate (honest, measured)**: coarse all 35,904 @ 8.4/s ≈ **71min** + fine on ~70% (~25k) @ ~2.4/s ≈ **2.9h** = **~4h total** single-model. Acceptable for a ONE-TIME overnight never-re-extract bake ("wasteful is the feature") — but NOT the sub-hour "batching cuts it hard" implied.
- **SPEED LEVERS if ~4h is too long** (none needed if overnight is fine): (a) run COARSE on chat-2b/chat-08b (`max_num_seqs: 32` → ~2× concurrency, smaller=faster) reserving 4b for fine — needs the lead's loadout. (b) ~~cloud-fan coarse~~ — QUALIFIED by fork's finding (377a533): cloud reasoning models can't do think-off + STRUCTURED-output cleanly (kimi returned prose to `format`), so a cloud-coarse stage would need to be FREE-TEXT (not the structured Coarse schema) or pay the reasoning-budget cost. ⟹ structured extraction is a LOCAL-vLLM job (chat-4b does think-off + structured both) — cloud is for big-ctx NON-structured agents. So the real lever is (a) smaller LOCAL models, not cloud. LEAN: accept the local run overnight — one-time, permanent asset.
- (NOTE: the ACTUAL filtered run is 18,858 chunks not 35,904 — Tim's 9-project scope ~halved it — measured effective rate ~3.1 chunks/s coarse+fine combined → **~1.7h**, not 4h.)

## STATUS
Engine PROVEN + the RELIABLE/GENERALIZABLE recipe figured out by-use (extract→determine→reduce; the worker NEVER filters → never-miss; extract-once/query-many). ~18/s binary, ~7/s extract; full 35,904 ≈ 30-85min, feasible overnight ("wasteful is the feature"). NOT yet run at full scale. Render-independent; keystone-first holds. NEXT: store the extraction layer (the reusable asset) + the self-referential run (dragnet-extract the session history → determine "structured-outputs/allocation/feeding design depth" → recover it). Coordinate fork on full-scale run_items.
