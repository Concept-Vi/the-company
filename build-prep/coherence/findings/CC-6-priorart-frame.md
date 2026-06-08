# CC-6 — External prior art (the CORPUS-CHAIN primitive) + the bigger frame + recursion/what-ifs

> Companion to `../CORPUS-CHAIN-ANCHOR.md`. The **sibling** of the semantic round's
> `findings/SEM-6-priorart-frame.md` — same two-thread shape, one layer up: SEM-6 mapped prior art for the
> *semantic detector* (LLM-as-judge, doc-drift, semantic search, GraphRAG); my lane is prior art for the
> **map-reduce-over-a-corpus primitive itself** (hierarchical summarization, NL→pipeline compilers, model
> cascades, declarative LLM-data pipelines) — each mapped to **its delta**, not summarized — plus the bigger
> frame and the anchor §9 what-ifs grounded in this repo's real code.
>
> **Marking convention:** **[OBS]** observed in real code (file:line) · **[INF]** inferred ·
> **[PRIOR-ART]** external, cited · **[IDEA]** my own proposal.
>
> **I deliberately do NOT re-cover SEM-6's lane** — LLM-as-judge bias set, the `run_jury`-is-N-draws-not-N-roles
> correction, doc-comment drift, Cody/Greptile semantic search, GraphRAG, the cheap-small-model-swarm
> thinness. I reference those and build *past* them onto the primitive's prior art. My lane is the *pipeline /
> compiler / cascade* side, and the deepest frame question (is `run_swarm` the universal substrate).

---

## Headline (stated once, so the rest reads against it)

**The corpus-chain primitive's *mechanics* are largely prior art — and that is a strength, not a wound, because
the round was told the "yes-but-actually" is the gold.** Three independent research lines from 2024–2025
(**LOTUS** semantic operators, **DocETL** agentic-rewrite document pipelines, **DSPy** declarative LM programs)
already build "a declared, typed pipeline of LLM operators over a corpus, optimized/compiled by a model." The
anchor's §5 coverage-certainty argument — *a single big-context call skims; decomposition gives per-unit
attention* — is not the anchor's insight: **it is DocETL's entire stated motivation, cited to the
lost-in-the-middle literature.** So the honest verdict on the four claimed novelties (anchor §0) is:
**declared-chain-as-typed-object = anticipated (LOTUS/DocETL); coverage-certainty = corroborated, not novel;
NL-compiler = narrowly novel (DocETL *optimizes a user-authored* pipeline, it does not compile one from
*freeform intent* with an inspect-approve gate — and text-to-SQL already does NL→declarative-query, so the
delta is precise and small); one-primitive-many-faces = partial (they generalize over document tasks too).**

**The defensible novelty is NOT the mechanics — it is the composition and the context:** one **resident,
local, massively-concurrent small-model** swarm (`run_swarm`) serving cognition + coherence + research-wave +
corpus-query as *configs of one engine*, whose output is **held as a dispositioned coherence substrate feeding
an autonomous no-humans loop** (push, not pull), local-first by construction. SEM-6 independently found
cheap-small-model-bulk semantic passes are a "thin/unoccupied external point" — that finding corroborates *this*
as the unoccupied design point, and the reason is economic (almost nobody has a resident concurrent small model
+ a VRAM resource-manager, so the bulk-cheap pass isn't on their menu).

**And the single sharpest contribution this companion lands — a correction to both the anchor §6 and SEM-6's
"it's all `run_swarm`":** **`run_swarm` is the MAP half *only*.** I grounded it: the engine is fan-out to
distinct addresses with a per-wave barrier, then each role's value resolved back *individually*
**[OBS cognition.py:585-621]** — there is **no cross-unit reduce/join in the engine** (grep for
reduce/join/aggregate-across-unit returns nothing in `cognition.py`/`activation.py`). `run_jury` is N draws of
*one* role, not a cross-unit reduce **[OBS cognition.py:637]**; the only "join" that exists is `run_role`'s
two-named-input injection rule (`recall ∧ ground`) **[OBS cognition.py:127]**, not arbitrary cross-unit
reasoning. So the answer to anchor §9's deepest question — *is `run_swarm` the universal substrate?* — is:
**the cheap-concurrent MAP, yes; the smart REDUCE the anchor needs (cross-unit join + decide-next loop +
hierarchical staging for an over-context digest), no — and that reduce is the real, net-new build.**

---

## THREAD 1 — External prior art for the CORPUS-CHAIN primitive (each → its delta)

### 1.1 LLM map-reduce / refine / hierarchical summarization — the MAP→REDUCE shape, named and shipped years ago [PRIOR-ART]

The anchor's `MAP (cheap ‖) → REDUCE (smart)` is, structurally, **LangChain's `map_reduce` and `refine`
summarization chains**, which have existed since the earliest LangChain — split a corpus into pieces, summarize
each (map), combine the summaries (reduce); or fold them in sequentially (refine).

- **The shape and its named limits** ([LangChain summarize docs](https://lagnchain.readthedocs.io/en/stable/modules/chains/index_examples/summarize.html);
  [Scaling Document Summarization — Medium](https://medium.com/@sonimegha1602/scaling-document-summarization-with-llms-stuffing-map-reduce-and-refine-a8a468d479c3)):
  the limitation cited verbatim is *"cross-document context is lost during the map step; final summary quality
  depends heavily on the quality of intermediate summaries."* **That is exactly anchor §7.2 (the contained-unit
  constraint) and §7.3 (the reduce's staging threshold), already a known failure mode in the wild.**
- **RAPTOR** ([arXiv 2401.18059](https://arxiv.org/html/2401.18059v1)) — *recursive* clustering + abstractive
  summarization building a **hierarchical tree** of summaries, retrieved at multiple levels. This is precisely
  the anchor §7.3 "hierarchical reduce" (reduce clusters → reduce the summaries) the anchor flags as needed when
  a 400-file digest overflows context — **RAPTOR is the published algorithm for that exact staging problem.**

**Delta the anchor adds — and the honest accounting:**
1. **Per-unit is *structured extraction*, not summarization.** map_reduce/refine emit *prose summaries*; the
   anchor's map emits **schema-enforced typed records** (`json_schema` transport **[OBS transport.py:47-48]**) —
   a finding *by construction*, not prose to re-parse. That is a real shape difference (it composes; prose
   doesn't), but it is small.
2. **Conditional decide-next loop.** map_reduce is one-shot (map → reduce → done). The anchor's reduce can
   **decide-next** (conclude it needs another targeted map pass — anchor §2, the query-engine loop). RAPTOR is
   recursive but *fixed* (cluster-summarize until one root); it does not branch on the *content* of the reduce.
   The intent-driven conditional re-map is a genuine delta — **and it is unbuilt here (see Thread 2).**
3. **Net:** the anchor is **not inventing map-reduce-over-a-corpus** — that is a settled pattern with a known
   hierarchical extension (RAPTOR) and known failure modes (cross-unit context loss). It is **re-deriving it on
   a local small-model swarm with typed outputs and a conditional loop.** Claiming the shape as novel would be
   the over-claim; claiming the *substrate it runs on* as the unoccupied point is correct (§1.5, Thread-2).

### 1.2 LOTUS + DocETL — declarative LLM-data pipelines: the CLOSEST prior art, anticipating the declared-chain [PRIOR-ART, the one to take most seriously]

This is the prior art that most directly anticipates the anchor's load-bearing structural idea (§3, *"the chain
itself is a declared, typed object"*). Two Stanford/Berkeley systems, both 2024:

- **LOTUS** ([arXiv 2407.11418](https://arxiv.org/html/2407.11418v1); [VLDB p4171-patel.pdf](https://www.vldb.org/pvldb/vol18/p4171-patel.pdf))
  — *"semantic operators, a declarative programming interface that extends the relational model with composable
  AI-based operations for semantic queries"*: `sem_map`, `sem_filter`, `sem_agg`, `sem_join`, `sem_topk` — a
  Pandas-like API where each operator is an LLM call with a NL instruction, **with an optimizer** that picks
  cheap approximations under accuracy guarantees. **This is the anchor's `Chain = {map, reduce, …}` as a
  shipped, optimized algebra.** `sem_agg` *is* the reduce; `sem_map` *is* the map.
- **DocETL** ([arXiv 2410.12189](https://arxiv.org/html/2410.12189v2); [VLDB p3035-shankar.pdf](https://www.vldb.org/pvldb/vol18/p3035-shankar.pdf))
  — a **declarative YAML pipeline** of LLM operators (map, reduce, **resolve** = entity-dedup, **gather**) over
  complex documents, **plus an agent that automatically rewrites/optimizes the pipeline** using "rewrite
  directives" and an "agent-guided plan evaluation mechanism that synthesizes task-specific validation prompts."
  DocETL's own abstract **[PRIOR-ART, quoted verbatim from the paper]:** prior declarative frameworks *"focus on
  reducing cost when executing user-specified operations… rather than improving accuracy, executing most
  operations as-is (in a single LLM call). This is problematic for complex tasks… requiring decomposition of the
  data, the task, or both."*

**This last quote is the most important external finding in the whole companion, because it means the anchor's
§5 coverage-certainty argument is corroborated prior art, not a novel insight.** DocETL's *entire motivation* is
the anchor §5 claim — that a single big LLM call over a long document *skims*: *"LLM performance degrades
considerably as length increases… they can be distracted or selectively pay attention to certain portions,
failing to gain a holistic understanding"* (DocETL §1, citing Levy 2024, Shi 2023, Liu 2024a, the
lost-in-the-middle line). DocETL's answer is the same as the anchor's: **decompose into per-unit operations.**
The anchor and DocETL reached the same insight independently; honesty requires saying so — it strengthens the
*soundness* of §5 (a peer-reviewed VLDB system is built on it) while removing it from the *novelty* column.

**The deltas the anchor genuinely adds over LOTUS/DocETL (these are real, and small/precise — state them
exactly):**
1. **Compile from *freeform intent*, not optimize a *user-authored* pipeline.** DocETL's agent **rewrites a
   pipeline the user already wrote** in YAML (abstract: *"a declarative interface for users to define such
   pipelines and uses an agent-based approach to automatically optimize them"*). LOTUS pipelines are
   hand-written in Python. **Neither compiles a multi-pass map-reduce-over-corpus chain from a one-line
   freeform intent.** *That* is the anchor's COMPILE stage (§2) and it is the narrow, defensible novelty — with
   the caveat that **text-to-SQL** ([the whole NL→declarative-query line]) already does NL→declarative-query, so
   the delta is "NL → a *multi-pass corpus-chain config* with an inspect-approve gate," not "NL → a query" in
   general. Do not claim "nobody does NL→pipeline."
2. **Local-first resident small-model swarm.** LOTUS/DocETL assume *frontier API* models (GPT-4-class) per
   operator; their cost model is dollars-per-run and their optimizers exist *because* those calls are expensive.
   The anchor's map runs on the **resident on-box 4B at ~2,241 tok/s @ conc-32** (SEM-1/SEM-6 corrected number)
   — a regime where the map is *nearly free*, which inverts the optimization problem (LOTUS optimizes to make
   the LLM-calls *fewer*; the anchor can afford *full coverage* because each call is cheap).
3. **Output is a *held, dispositioned coherence finding feeding an autonomous loop*, not a query result handed
   to a human.** LOTUS/DocETL are *analytics tools* — you run a query, you read the answer, it's gone. The
   anchor's reduce output (for the coherence-scan face) becomes a typed finding with a disposition and a
   burn-down (the structural+semantic rounds' substrate). Push, not pull (this is the §1.4 / Thread-2 frame).
4. **DocETL's `resolve` operator is the anchor's missing pairing pass [IDEA].** DocETL ships a `resolve`
   operator (entity dedup — "are these two records the same entity?") precisely because pure map can't see
   cross-unit identity. **That is the anchor §7.2 / SEM-2 "candidate-pairing pass" the swarm can't do alone, as
   a named, shipped operator.** The anchor should *steal this shape*: a corpus-chain needs a `resolve`/`pair`
   operator type alongside map and reduce — and DocETL proves it's a distinct operator, not a special case of
   reduce.

### 1.3 DSPy / LMQL — the "LLM compiler" / structured-generation line [PRIOR-ART]

- **DSPy** ([arXiv 2310.03714](https://arxiv.org/abs/2310.03714); [dspy.ai](https://dspy.ai/)) — *"a programming
  model that abstracts LM pipelines as text transformation graphs… imperative computational graphs where LMs are
  invoked through declarative modules,"* with a **compiler** that optimizes the prompts/weights of those modules
  to a metric. DSPy's "compile" is the word the anchor borrows — but DSPy compiles a **programmer-declared
  signature/module graph** into *optimized prompts*; it does **not** compile *freeform NL intent* into the graph
  structure itself.
- **LMQL** ([github.com/eth-sri/lmql](https://github.com/eth-sri/lmql); [lmql.ai](https://lmql.ai/)) — a
  query *language* for LLMs: constraint-guided decoding, typed templates, an optimizing runtime. It is the
  *per-call* structured-generation layer — the anchor's `json_schema`-enforced map output is the same idea at
  the transport layer (vLLM guided decoding, **[OBS transport.py:33-48]** server-side json_schema).

**Delta:** DSPy/LMQL are the **structured-call** and **prompt-optimization** layers; the anchor reuses their
*spirit* (typed I/O, a "compiler") but operates at the **orchestration/corpus** layer above them. The honest
framing: the anchor's "compiler" is closer to **DocETL's pipeline-synthesis agent** than to DSPy's
prompt-optimizer — DSPy optimizes a *given* graph; the anchor (like a more ambitious DocETL) wants to *generate*
the graph from intent. **The anchor's COMPILE = DocETL-agent-rewrite + a from-scratch-from-intent step DocETL
doesn't have.** That is the precise composite.

### 1.4 RAG vs full-corpus-map — the tradeoff is live and the anchor lands on the right side [PRIOR-ART]

A direct, current debate maps onto anchor §9's "RAG vs full-corpus-map":

- **The exhaustive-vs-retrieval tension, named** ([r/Rag: "is RAG right for exhaustive searches"](https://www.reddit.com/r/Rag/comments/1qc5qua/is_rag_the_right_approach_for_exhaustive_searches/):
  *"the typical RAG setup optimizes for finding the most relevant handful of chunks, not exhaustive recall across
  a corpus"*; [OpenAI community: "Full-Scan MapReduce Rather Than RAG for rigorous analysis"](https://community.openai.com/t/a-proposal-for-full-scan-mapreduce-rather-than-rag-for-rigorous-document-analysis/1375934):
  *"RAG is vulnerable to retrieval miss… by using MapReduce we may reduce the response time required for the
  deep reasoning demanded"*). This is **the exact anchor §5 coverage-certainty argument restated by practitioners
  as "when exhaustive map beats retrieval."**

**Delta + the sharp framing [IDEA]:** the world has *both* (RAG for relevance, map-reduce for exhaustiveness)
and treats them as a **choice per task**. The anchor's contribution is to make **exhaustive map the default for
coherence/onboarding** — because the question *"is anything in this whole repo incoherent?"* is definitionally
an exhaustive-recall question RAG structurally cannot answer (RAG retrieves what's *relevant to a query*; a
coherence sweep has no query, it must read *everything*). **This is the cleanest argument for why the corpus-
chain is the right primitive for coherence specifically: coherence is the canonical full-recall task, the one
case where retrieval is provably wrong.** The anchor should lead with this — it's a *grounded* reason, not a
preference.

### 1.5 Model cascades / routing — the "small-map + big-reduce" cost pattern, formalized [PRIOR-ART]

The anchor §4 cost shape (cheap map touches every byte; smart synth only ever reads small things) is a known,
formalized pattern:

- **FrugalGPT** ([arXiv 2305.05176](https://arxiv.org/abs/2305.05176)) — **LLM cascade**: call a cheap model
  first, escalate to an expensive one only on low-confidence; *"match GPT-4 with up to 98% cost reduction."*
- **RouteLLM / model cascades** ([tianpan.co](https://tianpan.co/blog/2025-11-03-llm-routing-model-cascades):
  *"maintain 95% of frontier quality while routing 85% of queries to cheaper"*; [Unified Routing+Cascading,
  OpenReview](https://openreview.net/forum?id=AAl89VNNy1); [Dynamic Model Routing, arXiv 2603.04445](https://arxiv.org/html/2603.04445v1)).

**Delta — and a precise distinction [IDEA]:** cascades route *the same task* to a cheap-or-expensive model by
confidence (sequential, escalate-on-doubt). **The anchor does NOT do that — it does a *task split*, not a
*model cascade*:** the cheap model gets the *map task* (contained extraction) and the expensive model gets a
*different task* (the reduce — join/adjudicate/compose). They never compete on the same task; they do different
jobs. This is a **stronger** cost argument than a cascade: a cascade still sometimes pays the expensive model
for the *whole* input; the anchor's expensive model **never reads the raw corpus at all** (§4), so its input is
*always* small regardless of corpus size. **The confirm-tier from SEM-3 (cheap-2nd-model → Claude-Code) IS a
cascade** — so the system has *both*: a task-split (map vs reduce) and a cascade (the adjudication confirm
tier). Naming both precisely is the delta over the literature, which conflates them.

### 1.6 Agentic query planning / plan-then-execute — the corpus-chain is its bounded, declarative cousin [PRIOR-ART]

The COMPILE→MAP→decide-next shape maps directly onto the **plan-then-execute** agent pattern:

- **Plan-and-execute agents** ([LangChain, Plan-and-Execute](https://www.langchain.com/blog/planning-agents);
  [Plan-and-Act, arXiv 2503.09572](https://arxiv.org/html/2503.09572v3)) — an explicit *planner* lays out a
  sequence of steps, an *executor* runs them, then *re-plans*. LangChain's stated selling point is exactly the
  anchor's §2 logic: **plan first because the plan is cheap to check and the execution is expensive** (and
  planning up-front beats step-by-step ReAct on long-horizon tasks for cost + coherence).

**The delta — and it reinforces §2.0, doesn't compete with it [IDEA]:** the corpus-chain is the **declarative,
bounded** version of plan-then-execute. The mapping is one-to-one: **COMPILE = plan** (and its inspect-approve
gate, anchor §7.1, *is* the "check the cheap plan before the expensive run"); **MAP = execute** (over corpus
units, full-coverage); **the reduce's decide-next = re-plan**. The distinction is the action space:
plan-and-execute plans over an **unbounded tool/action space** (agentic — and hits the convergence/coordination
problem SEM-6 §1.5 cited via AgentField); the corpus-chain plans over a **fixed unit space** (declarative,
full-recall, fan-out-pure — no convergence problem by construction). So the corpus-chain is "plan-then-execute
with the agency removed and replaced by full-coverage map" — which is precisely the
not-agent-architecture-by-default law (dataflow over corpus units, not an agent deciding to act). This is a
clean corroboration of the anchor's compile-and-decide-next design from the agent-planning literature.

### Thread-1 source list
- [LangChain summarization (map_reduce/refine) docs](https://lagnchain.readthedocs.io/en/stable/modules/chains/index_examples/summarize.html) · [Scaling Document Summarization — Medium](https://medium.com/@sonimegha1602/scaling-document-summarization-with-llms-stuffing-map-reduce-and-refine-a8a468d479c3)
- [RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval — arXiv 2401.18059](https://arxiv.org/html/2401.18059v1)
- [LOTUS: Semantic Operators — arXiv 2407.11418](https://arxiv.org/html/2407.11418v1) · [VLDB p4171-patel.pdf](https://www.vldb.org/pvldb/vol18/p4171-patel.pdf)
- [DocETL: Agentic Query Rewriting and Evaluation — arXiv 2410.12189](https://arxiv.org/html/2410.12189v2) · [VLDB p3035-shankar.pdf](https://www.vldb.org/pvldb/vol18/p3035-shankar.pdf)
- [DSPy: Compiling Declarative Language Model Calls — arXiv 2310.03714](https://arxiv.org/abs/2310.03714) · [dspy.ai](https://dspy.ai/)
- [LMQL — github.com/eth-sri/lmql](https://github.com/eth-sri/lmql) · [lmql.ai](https://lmql.ai/)
- [Is RAG right for exhaustive searches — r/Rag](https://www.reddit.com/r/Rag/comments/1qc5qua/is_rag_the_right_approach_for_exhaustive_searches/) · [Full-Scan MapReduce vs RAG — OpenAI community](https://community.openai.com/t/a-proposal-for-full-scan-mapreduce-rather-than-rag-for-rigorous-document-analysis/1375934)
- [FrugalGPT — arXiv 2305.05176](https://arxiv.org/abs/2305.05176) · [LLM Routing & Model Cascades — tianpan.co](https://tianpan.co/blog/2025-11-03-llm-routing-model-cascades) · [Unified Routing+Cascading — OpenReview](https://openreview.net/forum?id=AAl89VNNy1)
- [Plan-and-Execute Agents — LangChain](https://www.langchain.com/blog/planning-agents) · [Plan-and-Act — arXiv 2503.09572](https://arxiv.org/html/2503.09572v3)

---

## THREAD 2 — The bigger frame + the §9 what-ifs, grounded in this repo

### 2.0 The frame, sharpened: `run_swarm` is the MAP, not the whole primitive — and the REDUCE is the real build [OBS → IDEA]

The anchor §6 says *"it IS `run_swarm`, a third application,"* and SEM-6 §2.0 went further (*"the same engine,
not just the same pattern"*) for the semantic *detector*. **Both are right about the MAP and silent about the
REDUCE — and the corpus-chain's whole point is the REDUCE.** Grounded:

**What `run_swarm` actually is [OBS cognition.py:582-621]:** a `ThreadPoolExecutor` sized to `swarm_slots`
fans out one role-run per unit; an `as_completed` **barrier** joins them; each role's output is written to its
*own distinct `run://` address*; a single batched `cognition.wave` rollup is emitted; then **each role's value
is resolved back individually** (`result.resolved[rid] = resolve_run_ref(store, addr)`). That is **pure
fan-out-and-collect — a MAP**. There is **no cross-unit reasoning step** in it.

**What is NOT there [OBS, grepped]:** a search for `reduce`/`join`/cross-unit/`aggregate.*finding` across
`cognition.py` + `activation.py` returns **nothing**. The only "join" in the engine is `run_role`'s injection
rule **[OBS cognition.py:127, RULE_INPUTS=("recall","ground")]** — a rule over *exactly two named role outputs*,
hard-wired, not arbitrary cross-unit reasoning. `run_jury` **[OBS cognition.py:637]** is N draws of *one* role
with a deterministic verdict over the draws — it is the anchor's *adjudicate-one-candidate* leg, **not** a
cross-unit reduce (SEM-2 said this from the semantic side: *"`run_swarm` is a map over independent units, not a
join"* — I confirm it structurally).

**So the precise answer to anchor §9's deepest question — "is `run_swarm` already the universal substrate, and
cognition/coherence/corpus-query all faces?" [IDEA]:**
- **The cheap-concurrent MAP half: YES, literally.** Cognition's per-turn swarm, the semantic-coherence sweep,
  and the corpus-chain's map are the *same fan-out engine* over different units (roles / repo-artifacts /
  corpus-units). The one net-new seam is the SEM-1 one: `run_role` hardcodes `ctx["utterance"]`
  **[OBS cognition.py:109]** → a unit-reading worker needs a generalized ctx→messages mapping (the
  `input_addresses` schema field exists but is descriptive-only **[OBS roles.py:20,67]**).
- **The smart REDUCE half: NO — it does not exist, and it is the real build.** The corpus-chain needs three
  things the engine has *no* construct for: **(a) a cross-unit join** (read the *whole digest*, reason across
  units — pairs/clusters/cross-refs); **(b) a decide-next loop** (the reduce concludes "I need another targeted
  map pass" — anchor §2/§9 conditional query engine); **(c) hierarchical reduce staging** (anchor §7.3 — when
  the digest overflows the smart model's context, reduce-clusters → reduce-the-summaries, i.e. RAPTOR §1.1).
  None of these is `run_swarm`, `run_role`, or `run_jury`. **This is the contradiction-with-grounding the anchor
  asked for: the unification claim is half-true, and the unbuilt half is the hard, valuable half.**

**Why this matters for the roadmap [IDEA]:** anchor §9 asks "does building the primitive first collapse three
roadmap items into one?" The grounded answer: **the MAP is already built and shared (so cognition + coherence +
corpus-query *do* share a substrate today), but the REDUCE is net-new and is what turns a swarm into a
*chain*.** The highest-leverage build is therefore **not** "the whole primitive" (half exists) — it is
**specifically the reduce engine: a `run_reduce` that reads N addresses, stages hierarchically if needed, and
can emit a decide-next directive back into a targeted `run_swarm`.** That is the seam; that is the lane.

### 2.1 The COMPILE stage — net-new *in this repo*; `compile.py` is a sibling but NOT the same compile [OBS]

The anchor's COMPILE (freeform intent → declared chain config) has a tempting near-namesake in the repo, and the
distinction is load-bearing:

- **What exists [OBS compile.py:1-50]:** `runtime/compile.py` `compile(graph, branch, node_types)` compiles a
  **workflow `Graph` of `NodeInstance`s** (the editable face, with pixels/wires) into **`ExecNode`s with
  `run://` addresses** (the runnable face). It is a *structural* graph→execution lowering — *"the runtime
  recompiles each run, so the editable face and the runnable face never drift."* It is **deterministic and
  generic over node-type**; it takes *no NL, makes no model call.*
- **The anchor's COMPILE is different in kind:** freeform NL intent → *a valid instance of the Chain schema*
  (map_schema, map_prompt, unit_selector, passes, reduce_prompt). That is a **smart-model generation** step
  (DocETL's pipeline-synthesis agent, §1.2), not a structural lowering.

**The delta + the build implication [IDEA]:** the repo *already has* the "two-face, recompile-each-run,
never-drift" discipline (`compile.py`) AND the typed-graph object (`contracts/node_record.py` `Graph`/`ExecNode`
**[OBS compile.py:21 import]**). **So a corpus-chain is well-modeled as a `Graph` of typed nodes
(map-node / reduce-node / resolve-node / drill-node), and `compile.py` already lowers a `Graph` to runnable
`ExecNode`s.** The anchor's "declared chain as typed object" is therefore *not net-new* — it's a *node-type
family* on the existing graph substrate. **What IS net-new is the NL→Graph step** (the smart compiler) and the
**reduce/resolve node-types** (§2.0). This is the single most useful grounding for the build: *the chain config
is a graph; the graph compiler exists; the missing pieces are the NL-front-door and the reduce/resolve nodes.*

### 2.2 Ingest-once-query-many — the digest as a cached substrate: CAS exists, digest-as-artifact is net-new [OBS → INF]

Anchor §9: *the structured digest is a reusable substrate — one map pass feeds many reduces/followups; is it a
first-class `cas://`/`vec://`-addressed artifact, re-derived on corpus change?*

- **What exists [OBS]:** the system has a **content-addressed store** — rollups are *"PERSISTED at a `run://`
  address (content-addressed; durable)"* **[OBS activation.py:255,303]**; `put_content`/`set_ref`/`get_content`
  is the resolver pattern (`resolve_run_ref` reads head→content **[OBS cognition.py:618]**). So the *mechanism*
  to address-and-cache a digest **already exists** — a map pass's per-unit outputs are *already* persisted at
  distinct `run://` addresses **[OBS cognition.py:607]**.
- **What is net-new [INF]:** there is **no first-class "digest" artifact** — a named, queryable bundle of "all
  per-unit map outputs for corpus C at version V" that a later reduce/followup binds to without re-mapping. The
  per-unit `run://` addresses exist but are scattered per-wave; nothing collects them into a re-usable,
  invalidatable digest object. **The own/reflect law (introspective-data-building) says re-derive on corpus
  change** — so the digest is a *reflected cache* (cheap to rebuild, owned only by its addressing), and the
  invalidation story is "corpus-version changed → re-map the changed units, reuse the rest." That selective
  re-map is itself a small smart judgment (anchor §7.4 followup-cost) — **and it's unbuilt.** Honest status:
  **CAS substrate = built; digest-as-first-class-artifact + selective-invalidation = net-new.**

### 2.3 The compiler-is-itself-a-chain recursion — grounded, and it terminates [OBS → IDEA]

Anchor §9: *the compiler is itself a smart read; could it use a cheap map over the dir first ("what areas/units
exist") to inform the plan? (auto-allocation as a mini corpus-chain — the recursion.)*

This is **grounded and clean [IDEA]:** the COMPILE stage, to write a good `unit_selector` + `map_prompt`, needs
to know *what's in the corpus* — which is itself a cheap map ("classify each top-level dir/file by kind"). So
**compile = a mini corpus-chain (cheap map over the dir → reduce into a plan) feeding the real corpus-chain.**
The recursion is real but **bounded**, for the same reason SEM-6 §2.6 found the semantic meta-detector
terminates: the inner "survey map" is a *fixed-depth* pass (one cheap map, one plan-reduce), not a self-invoking
loop — it does not compile-a-compiler-to-compile. **Termination = fixed recursion depth, not self-exclusion**
(the structural round's mechanism); here it's simpler — the compiler calls *map+reduce once* to inform itself,
then runs the real chain. This is also DocETL's "agent synthesizes validation prompts by looking at sample data"
(§1.2) — the same move (sample the corpus to write the plan), which **corroborates the recursion is sound and
shipped elsewhere.**

### 2.4 Continuous-background mode — already covered by SEM-6 §2.1; I cite, not redo [OBS, cross-ref]

Anchor §9's continuous-mode what-if (a low-priority chain keeps a digest warm). **SEM-6 §2.1 already grounded
this fully** — the `background` activation context (trigger `idle-loop`, `fires_swarm: True`,
**[OBS activation.py:77-85]**) and the `rollup` context (timer, read-half, **[OBS activation.py:96-105]**) exist
and work by use; the **always-on drivers** that *call* them are explicitly **needs-tim** (*"do NOT stand up an
always-on GPU-consuming daemon"* **[OBS activation.py:79]**). The corpus-chain inherits this verbatim: an
on-demand `company ask`/`company research` needs **no** new driver; a continuous warm-digest needs the
needs-tim driver. **I add only one corpus-chain-specific note [IDEA]:** the warm digest (§2.2) is exactly what a
background chain would maintain — so the continuous-mode what-if and the digest-as-artifact what-if are *the same
build* viewed twice (the background chain's job *is* keeping the digest fresh). Build the digest artifact and the
continuous mode is "point the existing `background` driver at it."

### 2.5 The reduce feeds the RHM — the corpus-chain is the RHM's whole-repo grounding read [OBS-anchor + IDEA]

Anchor §9: *the reduce feeds the RHM (the up_translate organ over a real whole-repo digest).* SEM-6 §2.3 found
the hook (`up_translate('finding', …)` coded and waiting at `suite.py:5828`). **My corpus-chain-specific
addition [IDEA]:** the RHM's "answer about any element at Tim's altitude" is *literally a repo-QA chain*
(anchor §3: `repo-QA = compile(question) → map → reduce`). So **the RHM is not a consumer of the corpus-chain —
the RHM's answer-generation *is* a corpus-chain face.** When Tim asks the RHM "what does X do / is X coherent,"
the right implementation is: compile his question → map over the relevant units → reduce into an
altitude-matched answer. The warm digest (§2.2) makes this fast (the map is already done; it's a cheap
re-reduce). **This collapses "the RHM" and "repo-QA" into one face of the primitive** — the strongest version of
the anchor §0 "more types, not more tools" claim, and it ties to the altitude-transformation-layer memory (the
RHM up-translates; the corpus-chain is the engine that produces the thing to up-translate).

### 2.6 The introspective-data law + self-hosting — the chain instruments itself, like the swarm [OBS → INF]

SEM-6 §2.5 grounded that a swarm wave already emits a `cognition.wave` run-record and `consolidate_rollup`
aggregates them **[OBS cognition.py:600-611, activation.py:247-323]** — the full law-cycle (operation →
run-records → substrate → rollups → knowledge) is wired for the swarm. **The corpus-chain inherits this for the
MAP half automatically** (the map *is* a swarm wave → emits `cognition.wave`). **The net-new instrumentation
[INF]:** the *reduce* and *compile* stages are not swarm waves, so they don't auto-emit — a corpus-chain run
should emit its *own* run-record (which chain config, which units, how many passes, did decide-next fire, what
did the reduce cost). That run-record is the introspective-data substrate for *improving the compiler* (the
introspective-data law's own first instance was model telemetry; the corpus-chain's is **compiler-quality
telemetry** — "this compiled config under-covered / over-mapped"). **Self-hosting tie:** a corpus-chain pointed
at `~/company` that produces grounded understanding on demand *is* the institutional-memory-that-replaces-the-
developer made a verb (`company onboard`, anchor §6) — and SEM-6 §2.7 already showed the corrected economics
make it a per-session on-demand faculty (no daemon). **The corpus-chain is the read-organ of the self-hosting
spine; the introspective-data law is how it gets better at reading.**

### 2.7 The one universal-substrate picture (the join of both rounds' frames) [IDEA]

Putting §2.0 against SEM-6 §2.0 and the structural round's "sibling-not-merge":

```
                          THE ONE FAN-OUT ENGINE  (run_swarm — the MAP, BUILT)
                                        │  cheap · concurrent · structured · per-unit attention · fan-out-pure
        ┌───────────────────────────────┼───────────────────────────────┬──────────────────────────┐
   COGNITION turn              SEMANTIC-COHERENCE sweep            RESEARCH-WAVE              CORPUS-QA / ONBOARD
   units = roles               units = repo artifacts             units = areas              units = corpus units
   (built, by use)             (= run_swarm, SEM-6)               (strong workers)           (compile→map→…)
        └───────────────────────────────┴───────────────────────────────┴──────────────────────────┘
                                        │
                          ════════════ THE MISSING REDUCE ════════════  (NET-NEW — the real build)
                          cross-unit JOIN · DECIDE-NEXT loop · HIERARCHICAL staging
                          (run_swarm/run_jury do NOT provide this — §2.0, grounded)
                                        │
                          the COMPILE front-door (NL→Graph; net-new in repo — §2.1)
                          the DIGEST artifact (CAS exists, artifact net-new — §2.2)
                          feeds → the COHERENCE substrate (push) · the RHM (pull, = a QA face — §2.5)
                          instruments → the introspective-data law (compiler telemetry — §2.6)
```

**The honest unification:** the project keeps re-deriving the *map* (cognition, coherence, research-wave all
fan out cheap structured units — that part *is* one substrate, already shared). It keeps *imagining* the reduce
(every round wants cross-unit reasoning) but **has never built a general reduce** — each round hand-rolls its
synthesis (the research-wave's reduce is *me, by hand*; the coherence loop's reduce is a Claude Code agent; the
cognition turn's "reduce" is the two-input injection rule). **So the deepest finding is: the universal substrate
is real but *half-built* — the map is the shared engine, the reduce is the universal gap.** Building one general
reduce (cross-unit join + decide-next + hierarchical staging, configurable model tier) is what would actually
turn "three tools" into "one primitive, many faces" — and it is the same build whether the units are roles,
files, areas, or corpus-chunks.

---

## Summary — the expansion-ratio-greater-than-one residue (what I'd put in front of Tim)

1. **The mechanics are mostly prior art — own it, it's a strength (§1.1–1.2).** Map-reduce/refine
   (LangChain), the hierarchical reduce (RAPTOR), and *especially* declarative LLM-data pipelines with an
   optimizing/rewriting agent (**LOTUS**, **DocETL**) already build "a declared typed pipeline of LLM operators
   over a corpus, compiled/optimized by a model." **DocETL's published motivation IS the anchor's §5
   coverage-certainty argument** (LLM skims long inputs → decompose), citing the lost-in-the-middle literature —
   so §5 is *corroborated*, not novel. **[PRIOR-ART]**
2. **The defensible novelty is the composition + context, not the mechanics:** one **resident local
   small-model** swarm serving cognition + coherence + research + corpus-QA as configs of *one* engine, output
   **held as a dispositioned substrate feeding an autonomous no-humans loop** (push, not pull), local-first.
   The narrow per-pillar deltas: NL-compile-from-*freeform-intent* (DocETL only *optimizes a user-authored*
   pipeline; text-to-SQL already does NL→query, so the delta is "NL→multi-pass-corpus-chain-config + inspect-
   approve gate"); cheap-full-coverage instead of cost-optimized-frontier-calls; finding-feeding-a-loop instead
   of query-result-to-human. **[PRIOR-ART → IDEA]**
3. **The sharpest correction, grounded — `run_swarm` is the MAP only; the REDUCE is net-new and is the real
   build (§2.0):** the engine is fan-out-to-distinct-addresses + barrier + resolve-each-back-individually
   **[OBS cognition.py:585-621]**; there is **no cross-unit reduce/join** (grep-confirmed); `run_jury` is
   N-draws-one-role **[OBS cognition.py:637]**, the only join is `run_role`'s two-named-input rule
   **[OBS cognition.py:127]**. So "is `run_swarm` the universal substrate?" → **the cheap MAP yes (shared
   today), the smart REDUCE no.** The reduce needs three unbuilt constructs: **cross-unit join + decide-next
   loop + hierarchical staging** (the last = RAPTOR §1.1). **Build the general `run_reduce`, not "the whole
   primitive" (half exists).** **[OBS → IDEA]**
4. **The chain-config is a graph; the graph compiler already exists (§2.1).** `runtime/compile.py` lowers a
   typed `Graph`→`ExecNode`s deterministically **[OBS]** — but that is graph→exec, NOT intent→config. So the
   "declared chain as typed object" is a *node-type family on the existing graph substrate* (not net-new); the
   **NL→Graph compiler** (= DocETL's synthesis agent) and the **reduce/resolve node-types** are net-new. DocETL
   even ships the `resolve` operator that is exactly the anchor §7.2/SEM-2 **pairing pass** — steal it as a
   distinct node-type. **[OBS + PRIOR-ART → IDEA]**
5. **Cascade vs task-split — name them apart (§1.5).** FrugalGPT/RouteLLM cascades route *one task* cheap-or-
   expensive by confidence; the anchor does a **task split** (cheap=map, smart=reduce, never the same task) — a
   *stronger* cost claim (the smart model *never* reads the raw corpus). SEM-3's confirm-tier *is* a cascade, so
   the system has **both**; conflating them loses the argument. **[PRIOR-ART → IDEA]**
6. **Coherence is the canonical full-recall task — the grounded reason map beats RAG here (§1.4).** "Is anything
   in the whole repo incoherent?" has no query for RAG to retrieve against; it must read *everything*. This is
   the strongest, non-preference argument for the corpus-chain as coherence's primitive. **[PRIOR-ART → IDEA]**
7. **The §9 what-ifs, grounded as built-vs-not:** ingest-once-query-many → **CAS store built
   [OBS activation.py:255,303], digest-as-first-class-artifact + selective-invalidation net-new** (§2.2);
   compiler-is-a-chain recursion → **sound + bounded** (fixed depth; DocETL does the same sample-to-plan move)
   (§2.3); continuous-mode → **already SEM-6 §2.1, ready-but-driver-gated needs-tim**, and it's the *same build*
   as the warm digest (§2.4); reduce-feeds-RHM → **the RHM's answer-gen IS a repo-QA chain face**, not a
   consumer (§2.5); introspective-data → **map half auto-instruments; reduce/compile telemetry is net-new and is
   how the compiler improves** (§2.6). **[OBS + INF]**
8. **The roadmap implication (§2.7):** the project keeps re-deriving the map (shared today) and hand-rolling
   the reduce every round (research-wave's reduce = me by hand; coherence's = a Claude Code agent; cognition's =
   a two-input rule). **One general configurable reduce — cross-unit join + decide-next + hierarchical staging —
   is what actually collapses three tools into one primitive**, and it's the same build whether units are roles,
   files, areas, or corpus-chunks. That, plus the NL-front-door and the reduce/resolve node-types on the
   existing graph substrate, is the real, grounded build list — not "build the primitive," which over-claims a
   greenfield that is in fact half-existing. **[IDEA]**
