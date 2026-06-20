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

## STATUS
Engine PROVEN small (mechanically + correctness), the critical prompt-bias finding captured. NOT scaled yet (per the directive: prove small first — done). Render-independent; keystone-first holds. Ready to coordinate fork + run the self-referential mine on the neutral prompt.
