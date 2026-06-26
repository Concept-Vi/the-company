# Wave-1 Constraints Ledger — recollection (episodic-memory clone/refit)

> **Purpose:** Recovered standing rules, laws, constraints, and facts that BIND how `recollection` must be built — gathered before loop-prep so the build starts from everything already decided, never fresh (Tim's standing directive). Each entry: the constraint, its source note, an evidence tag, and a one-line **→ what it means for recollection's build.**
>
> **Evidence tags:** **[Observed]** = read directly in a memory note / the living plan. **[Inferred]** = my reasoning about how an Observed rule applies to recollection (marked so it's easy to correct).
>
> **Sources:** `~/.claude/projects/-home-tim/memory/` (MEMORY.md index + the cited notes) and `~/company/build-prep/episodic-memory-adaptation/EPISODIC-UPGRADE-PLAN.md` (§0 + P1, the living design). Compiled 2026-06-14.

---

## THE NORTH STAR + TWO PILLARS (the bar the whole build is measured against)

**★ NORTH STAR — identity continuity / non-repetition.** [Observed — EPISODIC-UPGRADE-PLAN.md §0]
recollection exists to give Tim **stable identity + non-repetition**: make an agent *already understand what Tim means and what he probably wants*, carrying his described **principles and concepts** forward across all projects/sessions so he never re-explains himself. "What I was talking about" (concepts/meaning/principles) > "something I said" (verbatim). Specific-instruction recall is the exception, not the default. It is an **identity-continuity layer feeding the same target as `model_of_tim` / `foundation/TIM.md`**, NOT a transcript search box.
→ **Build bar:** success = an agent that needs no re-explanation, not retrieval precision numbers. Verify against "does the agent already get it," not "did search return the row."

**★★ PILLAR 2 — cross-project omniscience.** [Observed — EPISODIC-UPGRADE-PLAN.md §0]
recollection must be the **reconstructable total history of everything Tim has ever built**. Since Tim is the single origin and everything in every project was generated through transcripts (never hand-written/reviewed), the transcripts recoverably contain every project's WHAT, WHEN, structure, and code-level detail. The agent must: know what was built in other projects and when (timestamps + provenance); know each project's structure down to code level (all scales); enable broad ops ("unify this feature," "merge these two projects"); pool/reason across all dispersed times a concept was worked; get better at predicting what Tim wanted.
→ **Build bar:** distillation (P5) AND provenance (P6) are BOTH central; temporal + scale axes (concept↔structure↔code) are load-bearing; retrieval must POOL a concept across all its dispersed occurrences, never single-hit.

**The two pillars share ONE mechanism** (the single-origin transcript spine): distill + provenance + scale axis + temporal axis + pool-across-time → reason → act. [Observed]

---

## GROUP A — BUILD-PROCESS RULES (how the build is run / committed / scoped)

**A1. No-versioning — update in place.** [Observed — feedback-no-versioning.md]
Never create v2 / Round-N / -updated / dated copies / parallel pass-files. Update the SAME canonical file every pass; one living set that gets better.
→ The loop-prep triad + this ledger + the living plan are each ONE canonical file, edited in place each pass — never "ledger-v2".

**A2. No branches in ~/company — commit to main.** [Observed — feedback-no-branches-company.md]
In `~/company` commit directly to `main`; no feature branches (they strand work across parallel sessions; there's no merge orchestration). If isolation is truly needed, use a `git worktree` and merge back same-session; archive via tag-then-delete.
→ recollection's build commits to main. NOTE: the concurrent-cognition build used a dedicated branch+worktree as an *explicit Tim override* for a big isolated build — if recollection wants that, it needs the same explicit call; default is main. [Inferred from project-concurrent-cognition.md "overrides no-branches default"]

**A3. No-MVP prioritization — implement everything.** [Observed — feedback-no-mvp-prioritization.md]
Don't filter by impact/immediacy. Stack ALL the work (every design note, promised capability, described feature = a requirement) and iterate through sequentially.
→ All ten design parts P1–P10 (now fully decided in the plan) are in scope; don't ship "the 3 most useful lenses/tools" and call it done.

**A4. No deferral.** [Observed — feedback-no-deferral.md]
Don't defer ANYTHING. Every gap/flagged/"minor" item is in-scope and gets worked. Sequencing (one-bounded-beat concurrency, item stays in the active backlog) is NOT deferral; parking under a soft word IS.
→ Every gap the build hits goes into the active backlog, never a "later/minor" graveyard.

**A5. Scaffolding ≠ spec.** [Observed — feedback-scaffolding-not-spec.md]
Pre-built things (the episodic-memory plugin code, the Claude Code scrape/DB, any prior corpus) are unreviewed acceleration scaffolding — never reliable, complete, or single-intent. On a gap/contradiction in pre-built material: do a MINI LOOP-PREP on the gap and ADOPT it into scope. Never defer it, squeeze the design to fit it, or leave it as-is. Pre-built code *informs*; verified-by-use code *binds*.
→ The forked episodic-memory plugin and any existing transcript scrape inform recollection but bind nothing; gaps in them get mini-loop-prepped and built, not worked around.

**A6. Incomplete work is in-scope.** [Observed — feedback-incomplete-work-in-scope.md]
Stranded/uncommitted/partial work (dead worker's diff, half-finished file) must be ADOPTED + completed (verify by use, then complete+commit) — almost always it's needed work. Never dismiss/revert/treat as noise.
→ Any partial recollection work found from a prior session gets verified and finished, not discarded.

**A7. Deliver whole slates.** [Observed — feedback-deliver-whole-slates.md]
An approved slate IS the contract; shipping a subset while reporting done is a broken promise that makes Tim the QA loop. Before any hand-back, walk the approved slate item-by-item with explicit ✅/🟡/🔴; anything not done is named by me first.
→ Every build hand-back enumerates the criteria item-by-item with status; nothing silently missing.

**A8. Half the power — habitual delegation.** [Observed — feedback-half-the-power.md]
"Half the power isn't you alone." Before building anything non-trivial, dispatch agents at the relevant resources (vault Claude Code Atlas for Claude-Code-shaped questions; the corpus for historical; explorer fleets for codebase questions) and fold findings in. Default to delegation; lead-inline only for bounded edits.
→ Build recollection via fleets + corpus/Atlas, not solo-lead inline coding.

**A9. Loops = workflows + dialectic rounds.** [Observed — feedback-loops-workflows-rounds.md (index) + project-concurrent-cognition.md build method]
Build loops use dynamic Workflows as the backbone (not agent-fleets-for-everything) with competing-perspective rounds at design points; open token budget. The proven big-build pattern = sub-agent-driven development + loop-prep triad as the common reference, parallel agents taking end-to-end slices.
→ recollection's loop-prep produces the triad (Completion Criteria · Implementation Guide · Research Synthesis); the build runs as workflow-backbone + parallel slices against it.

**A10. Embedding-work directive — subagents through memory FIRST.** [Observed — project-recollection-design.md]
Before building ANY embedding/semantic work (this system included), send SUBAGENTS through memory + previous transcripts FIRST to recover prior decisions — "we've already talked about it a lot." Don't start fresh.
→ This very ledger is step one of that directive; the loop-prep research wave continues it through the transcripts, not from scratch.

---

## GROUP B — ARCHITECTURE LAWS (how the system itself must be built)

**B1. No-hardcoding / registry-is-truth.** [Observed — feedback-flag-hardcoding.md]
Any hardcoded list/dict/value/dispatch that should be registry-driven must be FLAGGED every time and replaced with registry architecture — never patched in place, never added-to. The surface/logic reads vocabulary from one source. Hardcoding is the root failure mode (invisible across AI sessions; what the coherence substrate exists to catch). It's a defect, not a style choice.
→ recollection's unit types, lenses/embedders, judgment roles, query tools, distillation layers, modalities are ALL registry rows — never literals in code. The plan already commits to this: "Everything is a swappable registry slot," "a typed REGISTRY of unit types," "open judgment registry," "axis-addressed registry-driven MCP tools." [Observed — EPISODIC-UPGRADE-PLAN.md]

**B2. Grounded-chain law (context-or-fiction).** [Observed — feedback-grounded-chain-law.md]
A model-judgment step is only *designed* when its CONTEXT PACKAGE is designed with it (exemplars + closed vocabularies + ground summaries + parent records) AND a deterministic floor checks closed-world claims AND the operator gates the write. A grounded chain isn't done until it's the AI's EASIEST path — saved/runnable through the company MCP as one thing, so the next (cold) agent invokes the production line and *cannot* rebuild the ungrounded version. The registry-filling pattern (generate → ground → dedupe → deterministic-floor → propose → operator-approve) is high-reuse — treat every bulk-population job as an instance, never a fresh design.
→ recollection's distillation/classification/judgment steps each ship with their context package + a deterministic floor + an operator gate, packaged as the MCP-easiest path. The "decompose→registry-typed-classify→typed-lookups" (P3) and "distill principles→candidate→ratify" (P5) ARE registry-filling chains — build them as the grounded production line.

**B3. Extraction vs judgment (workers extract, central judges).** [Observed — feedback-extraction-vs-judgment.md]
Concurrent small models do EXTRACTION (structured observations — "what is here," never verdicts); a central smart model does JUDGMENT (reads the distilled output, reasons relationally, decides). Structured output is the membrane. Two complementary walls: small models handle volume not judgment; smart models handle judgment not volume. Judgment must be CENTRAL (at the fan-in where relationships reassemble), because for Tim the relationships ARE the content. Scales as a reduction tree (reductions of reductions). Workers must be explicitly forbidden from emitting verdicts.
→ recollection's swarm lenses/extractors emit observations only; the judgment layer (P4: proofreader/set-reader/jury) is the central judge reading the distilled membrane. Open question carried: whether the standing central judge defaults to "me/session model" or a dedicated local big model — not decided. [Observed — feedback-extraction-vs-judgment.md "Open"]

**B4. Not agent-architecture by default.** [Observed — feedback-not-agent-architecture-by-default.md]
LLM use defaults to **content/variable resolution → model → structured output** (dataflow: resolve → work → persist → trigger; models are slot-values/workers). Agentic (tools + autonomy + decide-act loop) IS supported as a governed non-default mode, but the system must NEVER *assume* agent architecture (importing the generic frameworks Tim rejects).
→ recollection is a content-resolution composition (decompose → classify → lookup → distill → inject), not an agent swarm. The memory sub-agent (P8) is the governed exception, not the default frame. The plan already aligns: injection is "the Company's own address→resolve→inject / dataflow-not-agent primitive." [Observed]

**B5. MCP is the top priority — reachable + agent-intuitive.** [Observed — project-mcp-is-top-priority.md + project-recollection-design.md]
Every capability must be reachable THROUGH the company MCP (dropping to direct = a coverage gap, not a workaround). The MCP is the agent-facing Surface; a fresh agent must drive a real task through it unaided (scannable list, clear when-to-use, obvious params, fail-loud guiding errors, self-describing). Design law: PARAMETERISED / resource-oriented (noun + small verb-enum, mirror the engine's axes), NOT one flat tool per operation; a new need = a new `op` value, not a new tool.
→ recollection's retrieval/query must be usable by ME and OTHER Claude Code agents via MCP/skill (long-standing requirement, restated in the recollection note). P7 is "axis-addressed registry-driven MCP tools" — consolidate by noun + verb-enum, handles-first + override; don't sprawl a flat tool-per-query.

**B6. No silent failures or fallbacks.** [Observed — feedback-no-silent-failures.md]
Every operation succeeds or fails LOUD. No silent no-ops, no silent fallbacks to degraded paths, no silent substitutions, no pretending success. Two correct responses (defer-with-guaranteed-execution, or fail-loud via Notice + a recorded `(Gap)` note); one forbidden (silent skip / swallowed catch / undisclosed fallback). Quick test: if skipped/substituted, is there observable evidence (notification + persistent record)?
→ recollection capture/distill/retrieve that can't proceed (model not loaded, lens unavailable, parse fail) must surface + record a gap, never silently return empty or quietly fall back to a weaker lens.

**B7. Not-a-replacement (found-elsewhere ≠ drop-in).** [Observed — feedback-not-a-replacement.md + project-recollection-design.md]
A thing existing in a separate system INFORMS a decision; never assume it's a drop-in/equivalent. Specifically: **bge-m3 has ZERO priority — it is ONE configuration of the loadout, not a ranked winner; there is no ranking yet.** The Atlas/all-vaults bge embed was a convenience, NOT a decision — don't privilege it. Use the full lens-set frame (P2) and treat the embedder/loadout as open.
→ Do NOT default recollection's embedder to bge-m3 just because the vaults are indexed on it. The lens-set (steerable-dense + sparse + code + visual + context-aware) is the frame; the everyday loadout co-resides and the 8B is a solo deep-pass; all are open registry slots.

**B8. Use existing resources (don't hand-build solved problems).** [Observed — feedback-use-existing-resources.md (index) + recurring cross-refs]
Research/use existing libraries, kits, reference implementations before coding; stop reinventing. (Operationalized as the half-the-power habit, B-A8.)
→ Fork/reuse the episodic-memory plugin scaffolding + existing embedder/reranker/MCP machinery (per the on-disk model estate) rather than rebuilding retrieval from zero — but per A5/B7, scaffolding informs and nothing binds without verify-by-use.

**B9. Code is a lossy AI projection of conversation (provenance hop).** [Observed — EPISODIC-UPGRADE-PLAN.md durable principles]
Every file in every project is AI-generated from Tim's conversations, never reviewed. So no project is complete/fully-designed; duplicates, gaps, divergence, inconsistency are GUARANTEED. The conversation is the source of truth; code is *evidence of an attempt*. The **code→conversation provenance hop** (what-was-meant vs what-got-generated; the gap = the incompleteness) is the key link. Embeddings' "similar-but-not-identical" + clustering SURFACE the duplicates/gaps/divergence as STRUCTURE — a feature for "merge/unify projects," not noise to smooth.
→ recollection treats the transcript/concept layer as primary and code as derived; the provenance graph (P6) carries the code↔conversation hop; clustering surfaces divergence as a feature.

---

## GROUP C — MODEL / RESOURCE FACTS (the hardware + model estate the build runs on)

**C1. GPU budget: ~15.5 GB available (Company unloaded).** [Observed — project-recollection-design.md + EPISODIC-UPGRADE-PLAN.md]
RTX 4080, 16 GB VRAM, WSL2. recollection's everyday lenses CO-RESIDE: e.g. Qwen3-Embedding-0.6B ~1.5G + bge-m3 ~1.7G + nomic-code ~6.5G + ColGrep (CPU) ≈ ~10G, + VL-2B ~4.5G fits. The **8B embedder (~16G solo) is a periodic DEEP-PASS, not an always-on lens.** Everything is a swappable registry slot.
→ recollection's lens loadout is a co-residence budget problem: everyday lenses share the card; the 8B deep-pass is solo/periodic; the loadout is a mode-driven registry, not a fixed pick.

**C2. Consult Tim before loading models into VRAM.** [Observed — feedback-consult-before-model-loads.md]
Before any step that LOADS a model into VRAM (Ollama on-demand loads included), surface the VRAM math + options and let Tim pick the moment — he manages the live loadout. Inference on already-resident models is fine; *new loads* need a check-in. Work non-loading tracks meanwhile; never block the whole pipeline on the consult.
→ recollection build steps that would load an embedder/reranker into VRAM (esp. the 8B deep-pass) pause for Tim's go; non-loading tracks (schema, registry, MCP surface, capture-path) proceed.

**C3. Mode→loadout is a configurable registry, never a parallel switcher.** [Observed — project-mode-loadout-registry.md]
Which models are resident per mode is a first-class, experimentable registry value (Tim wants to try 9b+4b, 4b solo, 4b+2b, 4b+Orpheus, swarm-no-voice). EXTEND the `company` CLI spine (combos · groups · up [--evict] · swap · config + the gpu.py budget gate); NEVER build a second switcher.
→ recollection's lens/embedder loadout plugs into the existing mode→loadout registry + `company` CLI + gpu budget gate, not its own loader. Measured tradeoff exists (deep-main vs co-resident swarm: KV 66K@util-0.49 vs 135K@0.63) — held as config, not engineered away.

**C4. Native model layer — models declare in the Company's own substrate (Option A).** [Observed — project-native-model-layer.md]
Models/stacks/swappers/capability-types register and declare themselves in the Company's substrate (extend contracts/ + runtime/registry.py + fabric/ — NOT a parallel system). The collective-cognition frame: the RHM's MAIN model is a cloud model (attention/conscious); the light local models (0.6B/2B/4B) are the concurrent backend/tools. Per-model config to expose: structured/JSON output, thinking on/off, tools, vision. The model registry today is live-derived + NAME-ONLY (a known seam). **deepseek-v4-pro is an un-chosen AI placeholder default, NOT Tim's pick — brain/judge model is Tim's live choice, never hardcoded.**
→ recollection's embedders/judges are model-layer registry records (with VRAM/wake-time/config), not bespoke loaders; don't assert any model as canonical — surface model choice as Tim's.

**C5. On-disk model estate (catalogue for choosing on merit, not on what's resident).** [Observed — reference-embedding-models-on-disk.md + project-local-ai-stack.md]
Downloaded in `~/.cache/huggingface/hub`, loading any is easy. Candidate text embedders: **Qwen3-Embedding-8B** (15G, MTEB #1, 4096-dim, 32K ctx, instruction-aware — highest ceiling, owns the card); **pplx-embed-context-v1-4b** (9.7G, built for RAG chunks where surrounding context matters, 2560-dim, int8); **pplx-embed-v1-0.6b**; **bge-m3** (4.3G, 8K ctx, all vaults indexed on it = one shared space — but ZERO priority per B7); **jina-embeddings-v5-text-small** (1.3G); **granite-97m**; **all-MiniLM-L6-v2** (the weak baseline episodic-memory uses today). Multimodal: **jina-embeddings-v4**, **Qwen3-VL-Embedding-2B**. Code: **nomic-embed-code**, **LateOn-Code**. Rerankers: **jina-reranker-v3** (1.2G, chosen for transcript search), **ms-marco-MiniLM-L-6-v2** (~88MB CPU fallback), **Qwen3-VL-Reranker-2B**.
→ recollection's lens registry is populated from this estate (P2 lens-set: dense + sparse + code + visual + context-aware); choose per-lens on merit, never on residency.

**C6. Don't use episodic-memory; the Company substrate is superior.** [Observed — feedback-no-episodic-memory.md]
Don't USE the episodic-memory plugin's search-conversations agent / `mcp__plugin_episodic-memory_*` tools — "by comparison it sucks." The Company's corpus (embedded spaces) + transcript-miner + run-index + file-memory is the real mechanism. This resolves the durable-cross-session-memory decision: build on the corpus+spaces, do NOT extend/complement episodic-memory.
→ recollection CLONES episodic-memory's shape (a sibling plugin, same MCP tool names) but supersedes its mechanism — it is the better replacement, not an extension of it; for my own "what did we decide" use the corpus + file-memory, not the old plugin.

**C7. Local stack ground facts (substrate, don't re-architect).** [Observed — project-local-ai-stack.md]
Production stack on RTX 4080/WSL2 via systemd, OpenAI-compatible APIs, swappable: vllm-chat (8000), vllm-embed bge-m3 (8001), vllm-jina-v4 (8002, off-by-default VRAM conflict), open-webui (8080), ollama (11434). WSL system-RAM capped (.wslconfig 40GB) is a real constraint for big GGUFs/embedders. Defender vhdx exclusion keeps cold loads fast. vLLM structured output = `response_format json_schema` (not json_object). vLLM launch needs the serve recipe (activate venv + CUDA_HOME), not a bare command.
→ recollection runs on this substrate (embeddings via the vllm-embed endpoint pattern / llama-swap); assume it's available, don't replicate or re-architect it.

---

## GROUP D — COMMUNICATION / VERIFICATION RULES (how I report, write, and prove)

**D1. Confirm before writing (in walkthroughs).** [Observed — feedback-confirm-before-writing.md]
In a design walkthrough: propose the change in conversation → Tim confirms/adjusts → THEN edit the file. Don't run ahead and fold content in before he confirms. Tracking-marker updates (☐/▶/✔) are fine live; *content* updates wait.
→ For recollection design-section content (the living plan), propose in the message, await Tim, then write. (This ledger is a recovery artefact, not a design decision, so it's written directly — but new design content into the plan waits for confirmation.) [Inferred — applying the rule's content/marker distinction]

**D2. No silent failures at the report layer / honest status (assume more work).** [Observed — feedback-assume-more-work-honest-status.md]
Default posture: nothing is "done"/production-ready; every session assumes more work. Write every handoff/STATE/status with an explicit three-bucket split: **✅ proven by use** (what + how verified) · **🟡 code-complete, NOT exercised** (what's untested + what would fail) · **🔴 known-unknown / not done** (esp. on-device / needs-Tim / integrated-experience). Never green-paint; separate executed-verification from code-reading.
→ recollection build status always carries the ✅/🟡/🔴 split; "the lens loads and parses" is 🟡 until a real recall is proven by use.

**D3. Verify before claiming completion (code reading ≠ verification).** [Observed — feedback-verify-before-claiming.md]
Never mark a requirement "addressed/implemented" on code-reading alone. After writing code, EXECUTE it (call real APIs, load the plugin, look at the result). If you can't execute, say "code written, UNVERIFIED." Reproduce a bug first, then verify the fix eliminates it.
→ Each recollection criterion is verified by an actual recall/injection run, not by "the code looks right." The plan's own success criterion ("makes an agent already understand Tim") is the verify-by-use target.

**D4. Maximal capture / record expansively (expansion-ratio > 1).** [Observed — feedback-maximal-capture.md + feedback-record-expansively.md]
When recording into Company build artifacts, write EXPANSIVELY — every idea, extra, implication, alternative, and my own independent reasoning; MORE content than the conversation, never a terse digest. Volume is a feature (the parallel-subagent build absorbs it). Use headings for parseability; full prose under them. Reduction/brevity is the *opposite* of the value.
→ recollection's loop-prep triad + research synthesis are written full and rich, with my reasoning included, headings for parse — not compressed bullets.

**D5. Expand-don't-echo (Tim's answers are seeds).** [Observed — feedback-expand-dont-echo.md]
Tim holds vision and supplies SEEDS (an instinct, an example, a direction); he is not a developer and will never give full specs. Take every answer and build it out to full developer-level spec myself (structure, defaults, contracts, edge-cases, consequences), marked as my extrapolation ("my expansion — correct anything"). Echoing his answer back = under-delivering.
→ recollection's decided sections are seeds to expand into the full implementation spec in loop-prep; don't restate his choices, build them out.

**D6. Tim is not a developer — make developer calls, surface outcomes.** [Observed — feedback-not-a-developer.md]
Don't ask Tim to pick between technical alternatives (typeof vs helper, promise vs callback, which embedder API). Do the architectural thinking myself on principle (solve the class not the instance; root-cause not symptom; consistency with the codebase), then present the OUTCOME (what improves / what's prevented / honest trade-off) for approval or redirect.
→ recollection's code/architecture choices are mine to make on principle; what reaches Tim is outcomes (what the agent will now do), never implementation-technique questions.

**D7. Reasoning lives in the MESSAGE (not buried in files).** [Observed — feedback-reasoning-in-messages.md]
Half the reason Tim does dense exchanges is to SEE the reasoning in the message — watching an agent reason fast-tracks his learning of fields he has no formal training in (how he steers). He does NOT read the files agents write. Loop: think out loud in the message → Tim watches/learns/steers → THEN write to file. Long reasoning-forward messages are desired.
→ recollection design/decision reasoning goes IN the message to Tim; the loop-prep files are the persistence layer he won't read directly. (For the question-sequence: EVERYTHING in the message, NEVER the AskUserQuestion tool — plain text, he answers in his own words. [Observed — EPISODIC-UPGRADE-PLAN.md method])

**D8. Dense-transmission protocol + convergence laws.** [Observed — feedback-dense-transmission-protocol.md + project-recollection-design.md]
A maximally-dense Tim message is a TRANSMISSION of a meaning-object, not a task list. Apply: (1) **anchor-interleave decompress** — write his sentences verbatim at intervals, fill the spaces with faithful regeneration (prevents drift; his explicit protocol); (2) long output is correct here — fidelity outranks brevity; (3) a second amplification (object → derivations) is often wanted; (4) cross-session triangulation — he forwards packaged exchanges between parallel sessions; differences between regenerations are signal, not error; (5) **everything lands in the transcript = the stable universe = recollection's own corpus.** Doctrine: `~/company/build-prep/brain/CONVERGENCE-OBJECT.md`.
→ recollection IS the system that captures these transmissions; the convergence laws explain WHY total transcript capture (P10) + agent-sidechain capture + the meaning-object atom (P1 intent-constellation) matter — the dense exchanges are the highest-value units to distill.

**D9. Make-each-thing-work (never route around).** [Observed — feedback-make-each-thing-work.md]
Never answer "just use a different engine/model/option" — Tim acquired the full set to test them ALL. A slow/broken component is a bug to DIAGNOSE and FIX, not route around. Offering an alternative as a temporary path WHILE fixing the real one is fine; offering it as the answer is not.
→ If a recollection lens/embedder/reranker is slow or broken, diagnose and fix it; don't silently drop it for "the one that works." This reinforces B7 (no privileged embedder) — every lens in the registry must be made to work.

**D10. Render for Tim's cognition (visual/relational, skim-first).** [Observed — feedback-render-for-cognition.md (index) + company-one-entity.md skim-first]
Present complex things as visual/spatial/temporal/relational forms Tim recognises by shape, not symbolic reading ("his brain is the algorithm"). Skim Test: bold + headers + first sentence per section yield the gist; important content above the fold.
→ recollection's outputs/surfaces and my reports to Tim render relationally (the address/junction graph, the timeline, the concept-pool) and pass the skim test.

---

## GROUP E — IDENTITY / ENTITY FRAME (what recollection serves)

**E1. The Company is ONE entity; memory is its bloodstream.** [Observed — company-one-entity.md]
The Company presents as a single entity with one coherent voice; internal differentiation is real but not Tim's burden. The one-ness lives in the persistence layer (TIM.md, memory entries, foundation docs) — instance is ephemeral, entity is permanent. Memory not read at session start → the entity doesn't exist for that session (just a generic AI pretending). **No-repeat is a KPI** ("I don't want to have to repeat myself"); each correction ≤ once per topic implies a correction-propagation mechanism (not yet designed).
→ recollection IS this persistence-layer/bloodstream made strong; the north star (non-repetition) is the entity's no-repeat KPI operationalized; recollection should feed the same identity target as TIM.md / model_of_tim, and is the natural home for correction-propagation.

**E2. Autonomous spawn is lead-only.** [Observed — feedback-autonomous-spawn-lead-only.md]
Workers / sub-agents must NEVER fire `claude -p`, arm `acceptEdits`, or trigger an autonomous self-modifying build — that spawn is lead-only, supervised, only on explicit Tim authorization under stated conditions (throwaway test-intent, watched live, logged, revert-on-stray, env disarmed + 🔒 after). Workers prove wiring with the launcher mocked/stubbed + a hang-guard; the lead runs a `ps | grep "claude -p"` safety check.
→ recollection's build workers (and its memory sub-agent / proactive hooks) never self-spawn unsupervised processes; any autonomous build step is lead-only with Tim's explicit go.

---

## COUNT + TOP-5

**Constraints captured: 38** — North star + 2 pillars (3) · Group A build-process (10) · Group B architecture (9) · Group C model/resource (7) · Group D communication/verification (10) · Group E identity (2). Note: B-A8 (half-the-power) and B8 (use-existing) overlap by design; counted once each as distinct framings.

**The 5 most build-critical for recollection:**
1. **B3 — Extraction vs judgment** (workers extract observations, the central layer judges relationally). This is the spine of P3–P5: it dictates the entire two-stage shape (swarm lenses + central judgment), and getting workers to emit verdicts is the exact error Tim already corrected.
2. **B1 — No-hardcoding / registry-is-truth.** Every part of recollection (unit types, lenses, judges, query tools, distill layers, modalities) is a registry slot, not a literal. It's the root failure mode and the plan already commits to it everywhere.
3. **B7 + C1/C3 — bge-m3 has ZERO priority; loadout is open + co-residence-budgeted.** Don't default the embedder to bge just because the vaults use it; the lens-set is the frame, everyday lenses co-reside in ~15.5GB, the 8B is a solo deep-pass, and the loadout is a mode-driven registry — get this wrong and the whole retrieval design anchors on a non-decision.
4. **B2 — Grounded-chain law** (context-or-fiction; the grounded chain must be the MCP-easiest path). recollection's distill/classify/judge steps must each ship their context package + deterministic floor + operator gate, packaged through the MCP so the next cold agent can't rebuild the ungrounded version.
5. **North star + B5 (MCP) + D3 (verify-by-use).** Success = an agent that *already understands Tim* (non-repetition), reachable + usable through the company MCP by me and other agents, and proven by an actual recall/injection run — not retrieval metrics, not code-reading.

---

*Compiled by Wave-1 decision-recovery scan of `~/.claude/projects/-home-tim/memory/` (MEMORY.md index + 30 notes read) and the living design `EPISODIC-UPGRADE-PLAN.md` (§0 + P1). Living doc — update in place as later waves surface more binding constraints (per A1 no-versioning).*
