# Episodic Memory Upgrade — Living Plan & Decisions

> The management doc for the episodic-memory refit. Built section-by-section with Tim via a question sequence (2026-06-12). Each section: the proposal menu (3 options × effort) → Tim's decision → the concrete plan for that part. When every section is decided, the full design + implementation plan assembles from the DECISIONS LOG below.
>
> Companion docs in this folder: `MERGE-INTENTION.md` (the full collective-memory frame this feeds), `INVENTORY.md`, `LANDSCAPE.md`, `UPSTREAM-DOCS.md`, `reads/1-5` (code-grounded). This upgrade is the **first concrete instance** of the collective merge; it targets Tim's Claude Code workflow specifically.

## Why it sucks today (the diagnosis every upgrade targets)
`MiniLM-384 · one flat vector per raw exchange · vector-OR-LIKE (never fused) · no reranker · returns raw truncated text · only when explicitly asked.`
Five compounding failures (weak embedder, undistilled atom, no hybrid, no precision re-order, must-ask) + two that bite Tim's workflow specifically: **skips agent sidechains** (where his fan-out work happens) and **no parallel-session timeline** sense. Net effect: he barely uses it.

## The unconventional-workflow priorities (what's uniquely Tim's, not generic)
- intent-constellation atom + agent-sidechain capture (others discard exactly the work he does)
- proactive auto-recall (he doesn't ask, so it must not need asking)
- topic-threading-over-time rollups (he builds in dispersed fragments revisited across months)

---

## THE MENU (section by section — 3 proposals each, effort-tagged)

**Base strategy** — Fork-in-place [Low] · Clone-as-sibling-plugin [Med] · Clone-as-Company-seed [High]
**P1 Atom** — un-truncate/chunk [Low] · turn-context atom [Med] · intent-constellation atom [High]
**P2 Placement** — bge-m3 swap [Low] · dual-lens prose+code [Med] · multi-coordinate (instruction-directed) [High]
**P3 Retrieval** — hybrid RRF [Low] · query-expansion/HyDE [Med] · routed multi-space gather [High]
**P4 Precision** — ms-marco reranker [Low] · listwise jina-v3 [Med] · retrieve→rerank→swarm-judge [High]
**P5 Distillation** — swarm-backfill summaries [Low] · per-exchange G23 extract [Med] · hierarchical rollups [High]
**P6 Provenance** — index file_path [Low] · parse tool_result [Med] · artefact-provenance graph [High]
**P7 Query interface** — progressive disclosure [Low] · parametric tools [Med] · axis-addressed API [High]
**P8 Agent skill** — rewrite skill prompts [Low] · proactive auto-recall hook [Med] · memory sub-agent [High]
**P9 Modality** — code-block-aware [Low] · ColGrep/LateOn sidecar [Med] · visual memory VL [High]
**P10 Capture** — unify lanes [Low] · voice ingestion [Med] · live/streaming capture [High]

---

## QUESTION-SEQUENCE METHOD (how to run this — Tim's instruction, 2026-06-12)
- The section MESSAGE must be the *full explanation required to make the decision* — deep, not a recap of labels.
- Explain every option by **what it actually does and what it enables**, in effect-terms. NOT developer jargon. Tim does not implicitly know the difference between mechanism-labels and shouldn't have to.
- Tim is NOT the user — agents are. Frame choices around what the agent gains/can-do, not implementation mechanics.
- Bring expert INSIGHT + a real recommendation AND my own first-person thoughts (the tool strips them — they must go in the MESSAGE). Tim wants the view of the agent who'll USE this.
- One section at a time. Record his answer + the concrete plan + my reasoning.
- **EVERYTHING IN THE MESSAGE — and NEVER use the AskUserQuestion tool.** Tim only sees what is written in the message body. The full layout (every option, consequences, reasoning, recommendation) AND the questions themselves go in the MESSAGE as plain text; Tim answers in his own words. No option-picker UI, ever.
- **DESIGN THE FULL BEST VERSION — never pick what to build first.** Tim defines build-order AFTER the complete design exists. Stop phasing / "start with these 3" — that's his call, not mine.

## DURABLE DESIGN PRINCIPLES (set by Tim during the sequence — apply to every section)
- **Non-developer interpretation, everywhere.** Don't default to developer/generic framings (auth, decisions, clean code). Tim's content is conceptual/relational/his-own-language; his steering vocab, his queries, his concepts are HIS. Mine them from his corpus; never assume dev defaults.
- **Code is a lossy AI projection of conversation.** Every file in every project is AI-generated from Tim's conversations, NEVER reviewed, never will be. So: no project is complete or fully designed; duplicates, gaps, divergence, inconsistency are GUARANTEED. → The conversation is the source of truth; code is *evidence of an attempt*. The conversation/concept layer is primary; code is derived. The **code→conversation provenance hop** is the key link (what-was-meant vs what-got-generated; the gap = the incompleteness). Embeddings' "similar-but-not-identical" strength + clustering SURFACE the duplicates/gaps/divergence as structure — a FEATURE for "merge/unify projects," not noise to smooth.
- **Resource reality:** ~15.5 GB GPU available (Company unloaded). The everyday lenses co-reside (Qwen3-Embedding-0.6B ~1.5G + bge-m3 ~1.7G + nomic-code ~6.5G + ColGrep CPU ≈ ~10G, +VL-2B ~4.5G fits). The 8B (~16G solo) is a periodic DEEP-PASS, not an always-on lens. Everything is a swappable registry slot.

## DECISIONS LOG
*(filled one section at a time as Tim answers; each entry = his choice + notes + the concrete plan for that part)*

### Section 0 — Base strategy & success criteria — DECIDED
**Name:** `recollection` (a clone-as-sibling plugin; gets its OWN skills and its OWN custom sub-agents — distinct from the original episodic-memory's `remembering-conversations`/`search-conversations`).
**Base strategy:** Clone-as-sibling-plugin [Med]. Standalone now, built absorbable into the Company later. Own data dir (survives plugin updates). NOT wired into the Company pgvector backend yet (that waits on the merge).

**★ THE NORTH STAR (success criterion — overrides the four checkboxes):**
recollection exists to give Tim **stable identity + non-repetition**. Its primary job is NOT search — it is to make an agent **already understand what Tim means and what he probably wants**, carrying his *described principles and concepts* forward across all projects and sessions so he never has to re-explain himself. "What I was talking about" (concepts, meaning, principles) matters more than "something I said" (verbatim). Specific-instruction recall is the exception, not the default. This is an **identity-continuity layer** that should feed the same target as `model_of_tim` / `foundation/TIM.md` / the principles — not a transcript search box.

Tim selected all four sub-criteria as true (understands-what-happened, recalls-across-all-history, precision-when-asked, proactive-just-remembers) but framed them as **in service of** the north star.

**★★ SECOND PILLAR (surfaced during P1, 2026-06-12) — CROSS-PROJECT OMNISCIENCE:**
recollection must also be the **reconstructable total history of everything Tim has ever built**. Because Tim is the single origin and *literally everything in every project was generated through the transcripts* (he never wrote/reviewed/edited any of it directly), the transcripts contain — recoverably — every project's WHAT, WHEN, structure, and code-level detail. Requirements stated:
- The agent **already knows what was built in other projects and when** (timestamps + provenance).
- Knows what each project *was*, its **structure**, down to **code level** — all scales.
- Enables **broad operations**: "unify this feature," "merge these two projects" — and the agents it manages can know too.
- **Pools and reasons across all the dispersed times** Tim talked about / worked on a concept.
- Gets better at **predicting what Tim wanted to do** (the model-of-Tim / intent-prediction edge).

**The two pillars share ONE mechanism** (the single-origin transcript spine): distill (meaning/concepts) + provenance (what/when built, via tool_call→artefact) + scale axis (concept↔structure↔code) + temporal axis + pool-across-time → reason → act. 

Prioritization implication, carried forward to every section:
- **Distillation** (P5: concept/principle statements AND project structure/code rollups) and **Provenance** (P6: what-built-when, the artefact graph) are now BOTH central — they jointly serve both pillars.
- **Proactive injection** (P8) serves Pillar 1 (identity) AND Pillar 2 (project awareness loaded before work).
- **Temporal + scale axes** are load-bearing (when-built, concept↔code).
- Retrieval (P2-P4) must support **pooling a concept/project across all its dispersed occurrences in time** — not single-hit lookup (the topic-threading-over-time pattern, now confirmed essential).
- Connects to: one-entity, model-of-Tim, common-memory-temporal, the foundation principles, the repo-exocortex (current code on disk) which recollection's build-history complements.

### P1 — Atom — DECIDED: a typed REGISTRY of multi-scale units, each ADDRESS-LINKED
**Not one atom.** A **registry of unit types** at different scales, chosen by the kind of query (compositional — matches the typed-registry pattern). Option-1 meaning-units (distilled work-model outputs) are ONE type; others: principle/concept statement, conversation-level, project-level, topic/concept-level. Raw bedrock still underneath; distilled units link back to raw (nothing lost).

**★ The defining property — every unit carries its addresses (links), two directions:**
1. **UP to its container (hierarchical address):** `unit ∈ session ∈ project`. CRITICAL STRUCTURAL FACT Tim surfaced: every session physically runs in a **working directory = the project folder**, so project membership is *already true in the transcript* (the cwd — confirmed present on the exchange in reads/1), NOT inferred. The scale/spatial hierarchy is solid ground, free.
2. **ACROSS to what it's about:** the topic / concept / artefact it relates to.

**This makes recollection answer RELATIONAL/ADDRESS queries, not just content search:**
- "What projects include X?" → concept X → linked project addresses.
- "When has X been a problem?" → units about X → their timestamps.
- "Where has X been described?" → all units about X across their addresses.
- "When was this part worked on in this project?" → filter by project + part + time.
These are answered by traversing links + filtering on scale/time axes — the addresses-as-junctions model. Couples tightly to P6 (the link/provenance graph), P5 (distillation makes the units), P7 (axis-addressed query interface exposes these query shapes).

**Implication for later sections:** the data model is *units (typed, multi-scale) + links (to container + to topic/artefact)*. P6 must build the links. P7 must expose by-project / by-topic / by-time / by-scale queries. P2 must fingerprint units so the topic/concept links are findable by meaning.
### P2 — Placement — DECIDED (full best design; all lens roles belong)
**Meaning layer:** steerable dense (**Qwen3-Embedding** — instruction-steered, "same memory, different question-shape") **+** sparse (**bge-m3**, for exact terms: Tim's coined language, error strings, file paths). Answers "what did I mean" (dense) AND "when has this exact thing come up" (sparse).
**Code layer:** **nomic-embed-code** in-store (semantic "find code that does X") **+ LateOn-Code/ColGrep** organ (token-precise agent grep) **+** every code unit carries the **code→conversation provenance link**.
**Visual:** **Qwen3-VL-2B** + matched **VL-Reranker-2B** (mockups/screenshots → the conversation that designed them).
**Context-aware:** **pplx-embed-context-4b** for project-level/long rollup units (meaning needs whole arc → "merge these projects").
**Scale/economy machinery:** **pplx-embed-0.6b** (4–32× fingerprint compression → fingerprint the ENTIRE history affordably); **Granite-97M** (CPU background bulk); **Qwen3-Embedding-8B** (periodic max-fidelity DEEP-PASS, solo).
**★ Steering vocabulary = MINED from Tim's corpus + refined by use** (NOT a fixed dev ontology). The swarm extracts his recurring concepts/principles/framings → the steering instructions ("represent this for the principle being expressed / the concept being defined / a correction / what was built & in which project" + his concept-axes: altitude, gap-pressure, relational-systems, the Company…). Improves from retrieval performance + his corrections. Shares the concept registry with `model_of_tim`. (This is the "you'd need to work that out" piece — a living registry, the standing open refinement.)
**All roles confirmed to belong; build-order deferred to Tim.**
### P3 — Retrieval/Gather — DECIDED (designed by Tim's convergence transmission, 2026-06-12)
**Primary sources:** `~/foundation/exchanges/20-the-convergence-object.md` (verbatim) · `~/company/build-prep/brain/CONVERGENCE-OBJECT.md` (canonical doctrine: the two laws, the barrier protocol, the ten derivations).

**The querier is the AGENT, not Tim** — gather triggers from Tim's rich input (or an agent's working need), never a search box. The pipeline:
- **Pass 0 — structural, programmatic, free:** size, timestamps, session depth, channel/dictation flags. *Measure structurally first because it's free.*
- **Pass 1 — message-type classification (tiny model):** density axis + act axis (directive / co-thinking / transmission / invitation-to-generate…). Message types & conditions are **registry-declared** — one type declaration updates classification, decomposition, and routing everywhere.
- **Pass 2 — decomposition to sentence-grain blocks** (Tim's writing packs per-sentence), unless small/isolated.
- **Pass 3 — per-block typed classification** at extreme concurrency (0.8B-class, ~120 concurrent), governed by **THE CLASSIFICATION LAW** (one axis, two extremes, evenly spaced low-integer divisions, ~3–5 per call; over-capacity discriminations run as **progressive chains** — 3×3 over 1×9, adaptive path, each step's resolved content feeding the next).
- **Pass 4 — typed lookups:** the block-type selects the space — laws / concepts / projects / provenance / operator-memory / model_of_tim; chains deepen conditionally on what comes back.
- **Pass 5 — aggregate per thread → inject** into the responding agent's context.
- **Two gather modes, both required:** top-k (precise) AND **gather-all-and-aggregate** (pooling a concept/project across all its occurrences in time — Pillar 2's mode; surfacing near-duplicates/divergence across projects is the answer, not noise).
- Fusion by rank (RRF); **agreement-across-lenses = the relevance signal** (Tim's corroboration instinct as the rule). Routing resolved structurally: block-type → space (supersedes the abstract routing question Tim skipped).
**★ THE OBJECT'S PRE-SEEDS for the remaining sections** (from CONVERGENCE-OBJECT.md — the derivations make P4–P10 part-derivable; each still gets its Tim-pass in the sequence):
- **P4 Precision** = resistance measured at query time (judge = does this candidate's meaning sit at the question's coordinates). Rerank stages + swarm juries are tiers of the resistance-routed compute pyramid (derivation 6).
- **P5 Distillation** = the coarse-graining flow; **principles = what survives rollup across scales** (derivation 5 gives the mining criterion for the steering vocabulary / model_of_tim). Consolidation = **annealing**, one objective: minimize total corpus resistance (derivation 3). Ontology growth = watch the deep holes (derivation 4, awaiting Tim's fit-test).
- **P6 Provenance** = **the ledger of crossings** (derivation 9): every Write/Edit tool-call is a timestamped thought→artefact crossing; Pillar 2 = replay the crossings; identity = the provenance-linked connected component. Plus **self-anchored artefacts** (derivation 8): generated files embed verbatim quotes from their causal conversation.
- **P7 Query interface** = classification-is-addressing (derivation 1): retrieval tools replay the address-computing chains; axis-addressed queries.
- **P8 Agent skill/injection** = the codebook (Pillar 1 in channel terms) + **wave-timing** (derivation 10): floor-injection at session start, dense transfer at peaks, pre-compaction waveform snapshots. Trained on `tim_correction` as the error signal (derivation 7). **NOTE (2026-06-13): P8's "memory sub-agent" = P4's looping judgment layer — ONE organ. The active, self-directed recall→read→recall-again→assemble loop decided in P4-D2 IS the sub-agent. P8 will specify its triggering/injection behaviour; P4 specified its judgment machinery.**
- **Corpus health** (new, cross-section): the **temperature scan** (derivation 2) — per-unit resistance computable with the P2 lenses; the dream phase = convergence restoration.

### P4 — Precision → THE JUDGMENT LAYER — DECIDED (2026-06-13)
P4 was reframed by Tim from "a precision/rerank stage" into the memory's general **judgment layer**. Search (P3) returns a dirty pile (the real answer + duplicates + a superseded older position + word-coincidence junk); the judgment layer is what happens to that pile before it reaches the agent. Today: nothing — which is half of why the current memory is useless.

**D1 — the stack & when deep reading fires:** Option A (full stack, routed), with Tim's two additions:
- **Three cleaners.** (1) *Proofreader* — a tiny CPU model that reads the question + ONE candidate together and scores the match; always runs, ~free; fixes "right answer buried at rank 15." Can't see across candidates. (2) *Set-reader* — a small model that reads the whole shortlist AT ONCE, so it can fold duplicates and FLAG disagreements (it can't resolve them). (3) *Jury* — several copies of the resident 4B (32-wide), each actually reading a candidate and answering a few fixed 1-axis/3-option questions (per the Classification Law); the only cleaner that can read in time-order and rule "this was true once, you changed your mind."
- **Routing is RULE-DRIVEN and keys on BOTH the question AND the result** (registry-declared triggers, changeable without code). The jury wakes when the question-type is high-stakes/identity-bearing OR the result pile is scattered/conflict-flagged; trivial clean lookups stay instant. (GPU-by-load: deep reading only where there's something to figure out.)
- **★ The jury is a GENERAL machine, not a relevance-cleaner** (Tim): "several small readers → structured verdicts," pointable at ANY judgment — relevance, but also "what questions should the calling agent be asking?", "which direction does this point?", any number of things. Judging is a **reasoning operation over recall**, not an end-of-pipeline cleanup.

**D2 — judgments are an OPEN TYPED REGISTRY** (the real decision, not "which abilities"): all four seed-judgments exist AND MORE; new judgment types are *declared in the registry, not coded*. Seeds:
1. **Junk-kill / answers-vs-mentions** — does this bear on the question or just share vocabulary (every recall).
2. **Changed-mind / supersession** — when 2+ of Tim's statements disagree: resolve on the **time axis** (directional: which is later supersedes; trivially schema-able for small models per the directional-edge law) or surface the disagreement AS the finding. Without it = averaged fiction, silently. Guaranteed-divergence corpus makes this essential.
3. **Everything-about-X stories (set-curation)** — pooled queries return a curated ARC (first appearance → development → current, duplicates folded, divergence visible), not a top-10 of the most-repeated line. What "merge these two projects" needs.
4. **Visual matched judging** — the VL-reranker paired to the VL lens, fires only when images are in play.
- **★ The memory is ACTIVE, not one-shot** (the live wire Tim caught in #3): it can run **its own follow-up retrievals + AI processing** — recall → read → notice a gap → recall again → process → assemble. **This is the same organ as P8's "memory sub-agent": the judgment layer that loops IS the agent. P4 and P8 are one organ** — recorded here, expanded in P8.

**D3 — verdicts are SELF-EXPLAINING and TYPED (multiple per result):** a result carries a small stack of typed verdict-records (relevance: "answers"; currency: "current — replaced Dec-2025"; confidence: "two routes agreed"), each a typed record, several per result, agent reads what it needs. Grounded-chain law applied to the memory's own output: nothing returned without its structured reasoning attached.

**Net identity:** P4 = the memory's judgment layer — general, registry-typed/extensible, run by the reusable jury machine, routed by question+result, able to loop on its own (= the sub-agent), returning typed self-explaining verdicts.
### P5 — Distillation — DECIDED (2026-06-13)
P5 = the machinery that MANUFACTURES memories from raw transcripts (reads each piece, writes down what it actually was). Pillar 1's core. Three stacked layers, all chosen.

**D1 — depth: ALL THREE layers, none hardcoded (grown).**
- **L1 Summary** — per-conversation "what was this about" (wayfinding); finish it on all 13,270 via the 32-wide swarm (current system stalled at 1,267).
- **L2 Structured extraction** — the swarm reads each piece and pulls out the meaningful things as separate TYPED records (decision · rationale · tim-correction · my-error · bug-fix · needs-tim · frustration · pattern + principle · concept-definition · what-was-built), each linked to its source moment and embedded. "What's Tim's principle about X" returns the PRINCIPLE, not a transcript. This is the search-box→understanding jump = Pillar 1, mechanically.
- **L3 Rollups** — compose L2 records UP across scale: conversation → session → project-arc (down to what got built) → "Tim's settled view on concept X, pooled from everywhere." **What survives the rollup at every scale IS a principle** (convergence object, derivation 5) → this is where model_of_tim + the steering vocabulary come from. Pillar 1 (who Tim is) and Pillar 2 (everything built, every zoom) are the SAME rollup flow read at different heights. L3 is where the active follow-up-retrieval loop (P4) and the annealing/consolidation dream-phase run.
- **★ NO HARDCODING (P5 build-law, Tim emphasised twice):** extraction types AND rollup levels are registry/living-vocabulary (mined from Tim's corpus, same registry as P2 steering), NEVER coded — "so they can be grown." The whole layer must stay extensible.

**D2 — triggers: backfill + live + deep-pass + INTERACTIVE, and the trigger set itself extensible.**
- *backfill* (one pass over all existing history to bootstrap) · *live* (distill new conversations as they land) · *deep-pass* (periodic higher-fidelity re-distill on the 8B + dream-phase consolidation that re-rolls-up and folds duplicates).
- **★ INTERACTIVE distillation** (Tim's addition): during interactions with Tim, through the **Company's interface (not fully built)**, in **directed / co modes** — distillation happens IN the collaboration, not only in the background. Mode-gated (the modes registry).
- "Avoid hardcoding in all builds so this is viable after the first three" → the trigger set is an open registry; interactive is the 4th, more can be added.

**D3 — what becomes a PRINCIPLE: candidate-staging → powerful-model ratification with Tim.**
- Candidate principles go to a **candidate location** (staging, not committed).
- A **POWERFUL model** (Claude-class, NOT the small swarm) conducts the gate WITH Tim: propose → talk → refine → commit. This is the foundation-exchanges pattern, mechanized.
- **The powerful-model slot is swappable:** it can be ME (external Claude Code, via the Company MCP) OR a powerful model inside the application. Either fills the role.
- **★ UNIFICATION:** D2's interactive trigger + D3's ratification are ONE co-mode loop — converse → distill in-flight → surface candidates → refine → commit. (Recursion: THIS design session IS that loop — co-mode distillation, me-as-powerful-model proposing, foundation/exchanges + this plan file = the commit. The system models the activity producing it.)
- **✓ CONFIRMED (Tim, 2026-06-13):** the ratification gate is ONLY for **principle / identity-level declarations** (the model_of_tim layer — load-bearing, propagates to every agent). Non-principle L2 records (decisions, build-facts, project-arcs — recall material) **self-assemble without the gate.**
### P6 — Provenance / the link graph — DECIDED (2026-06-13)
P6 = the connections between memories/artefacts; Pillar 2's spine. **Provenance is ONE continuous linking process** (Tim) — recovering links from history and linking new artefacts as they're made are the SAME mechanism, not two jobs; the new-artefact case is just the live edge of the graph that reaches back through everything.
**Identity = the connected graph** (convergence obj der.9): thought/transcript/artefact are one body held together by links; maintain them = maintain the entity; no-versioning derives (a v2 copy forks the body).

**D1 — richness: FULL+.** containment (unit∈session∈project, free from cwd) + file↔conversation **crossings** (every Write/Edit tool-call = a timestamped thought→artefact crossing; Pillar 2 = replay the crossings) + directional **cause-edges** (produced-by/produces, precedes/succeeds — the edge law) + **cross-project concept links** (same concept connected everywhere it appears — required for "what projects include X", "merge two projects", pooling).
- **tool_result (Tim refinement): kept but LAZY.** NOT distilled into memory (low value; don't spend the swarm on 6.7M action-outputs). The crossing record **KEYS** to the raw result → an agent that specifically needs "what came back" fetches it on demand from the raw source. Reachable, not dumped. (Same on-demand pattern as P7 progressive disclosure / raw-bedrock-always-one-hop-down.)

**D2 — link trust-grades (consequence of full+): BOTH, kept distinct.** Mechanical skeleton (containment + crossings — extracted exactly from the transcript, certain, free, asserted as fact) + semantic enrichment (cause-edges + cross-project concept-sameness — can't be mechanical; model-made, so TYPED + confidence-graded per the grounded-chain law; high-stakes links run through the P4 judgment layer; never an inferred link masquerading as certain).

**D3 — forward anchoring: LINK, don't embed (Tim correction).** Embedding a verbatim quote inside an artefact is REDUNDANT — a copy that can drift + duplicates content (violates convergence/no-divergence). Instead the **continuous live link IS the anchor** (same provenance mechanism): every generated artefact links to its causal conversation, traversable, drift-checkable against the LIVE source. One source, everything points to it. (Refines convergence-object derivation 8: anchor = live link, NOT embedded copy.)
### P7 — Query interface — DECIDED (2026-06-13)
The surface an agent calls. Must be usable by ME + other Claude Code agents (MCP/skill), not just internal. The current 2 blunt tools (search/read → raw flood) are why the existing memory goes unused even with the data.

**D1 — tool shape: parametric core + AXIS-ADDRESSED front doors, REGISTRY-DRIVEN.** Named, question-shaped tools (`whats_my_position_on(x)`, `the_arc_of(concept)`, `what_projects_include(x)`, `when_was_worked_on(thing, project)`, `what_touched(file)`…) over one parametric machine. The named set is a **registry** — new query-shapes are declared, not coded ("so more can be added"). Why it matters: this is the **grounded-chain law AS the interface** — the easy/obvious tool returns the judged, current, grounded answer; the shape of the tools decides which path is the path of least resistance, so we make the grounded questions the easy front doors.

**D2 — progressive disclosure: HANDLES-FIRST + optional return-override.** Default returns compact handles (id + one-line gist + the P4 typed verdicts: relevant/current/confidence), a few hundred tokens; the agent expands only what it wants. A **return-format override** parameter (on the parametric core) lets a caller change what comes back (full content / the arc / raw). Raw always one hop down — where P6's lazy tool_results live. Makes the memory cheap enough to use CONSTANTLY (the point).

**D3 — surfaces: ALL THREE.** MCP tools (the axis-addressed tools over the Company MCP — for me + any CC agent, the primitive surface) · recollection's **skill** (wraps the common "recall what's relevant" flow) · the **sub-agent** (the active loop from P4/P8 for deep pool/arc jobs). All obey the grounded default: easy path = judged + provenance-carrying; raw drill-down = a deliberate extra hop.
### P8 — Agent skill
_pending_
### P9 — Modality
_pending_
### P10 — Capture
_pending_

---

## IMPLEMENTATION PLAN
*(assembled from the decisions once all sections are decided — sequencing, dependencies, model bindings, verification)*
_pending_
