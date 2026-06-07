# B1 — External Architectures: How the Outside World Builds Concurrent Cognition

*Outward research scout, 2026-06-07. READ-ONLY web survey of the BROADER design space around our [[00-LANDSCAPE|concurrent-cognition]] design — staged-stream of reply PARTS fed by a swarm of ~32 concurrent small-model ROLE-runs whose structured outputs resolve into the next part's context. Thesis under test: **quality from concurrency + composition, not model size.***

*This file maps the landscape top-down, names each pattern + its tradeoffs, places OUR design inside it, surfaces the counter-evidence (where the field says our shape may be wrong), and proposes shapes that may be BETTER than ours. Written expansively (maximal-capture). Every claim carries a source link; numbers are quoted from the fetched source, not recalled. Where I reason beyond the source I mark it **[my inference]**.*

---

## 0. The one-sentence finding (read this first)

Our design already has a **name in the literature**, an **empirical anchor**, a **40-year-old architectural ancestor**, and a **rival shape that challenges its core voice assumption**:

- **Name:** *Compound AI System* (Berkeley BAIR / Zaharia et al, Feb 2024). Our whole thesis — "results come from the SYSTEM of interacting model-calls, not the single model" — is the headline claim of that essay. We should adopt this as our umbrella vocabulary when talking outward.
- **Empirical anchor:** *Mixture-of-Agents* (Together AI, Wang et al, 2024) — open-source models composed beat GPT-4o on AlpacaEval 2.0 (65.1% vs 57.5%). This is the strongest published "composition ≥ size" evidence.
- **Counter-evidence (must not ignore):** *Self-MoA* (Li et al, ICLR 2025) — mixing *different* models often *lowers* average quality; aggregating many draws of the *single best* model beat mixed-MoA by 6.6% on AlpacaEval. **This directly tests our "32 role-runs on the ONE resident 4B" choice — and largely VINDICATES it** (we already use one model, many draws). See §4.
- **Ancestor:** the *Blackboard architecture* (Hearsay-II, 1970s) — independent "knowledge sources" post structured findings to a shared workspace, consumed opportunistically by a synthesizer. This is our `swarm://<turn>/<role>` → next-part-context, 1:1. See §6.
- **Rival shape:** *Moshi* (Kyutai, 2024) — a full-duplex speech-text model that overlaps listening/thinking/speaking *in one model with no cascade*. It challenges our "each PART is the TTS unit" coupling. See §7.

---

## 1. The taxonomy (three axes that sort the whole space)

The field doesn't have one "concurrent cognition" label, so the patterns scatter unless you sort them. Three axes do it, and **where our design lands on all three is itself the finding.**

**Axis A — what is parallelism FOR?**
- *Parallel-for-latency*: run things at once to answer faster. (Speculative decoding, Skeleton-of-Thought, parallel sampling.)
- *Parallel-for-quality*: run things at once to answer better. (MoA, multi-agent debate, self-consistency, ensembles.)

**Axis B — how many distinct models?**
- *Same model, many draws*: one model sampled/branched N times. (Self-consistency, speculative decoding, Self-MoA.)
- *Many roles / many models*: distinct prompted roles or distinct checkpoints. (MoA, debate, blackboard knowledge-sources.)

**Axis C — WHEN do the parallel runs interact?**
- *Aggregate-at-end*: runs are independent; a merge step combines them once. (Ensemble, self-consistency, branch-solve-merge.)
- *Interact-during-generation*: runs read each other / feed an ongoing process mid-stream. (Multi-agent debate, blackboard, **our injection edge**.)

> **Our design's coordinates:** *parallel-for-quality* (Axis A) · *same model, many role-draws* (Axis B) · *interact-during-generation, and the interaction feeds a STREAMING reply part-by-part* (Axis C). **No single named pattern occupies exactly that cell.** The closest neighbours: Blackboard (C) + Self-MoA (B) + Skeleton-of-Thought (the staged-stream feel) + Compound AI (the umbrella). Our contribution is the *fusion*: a blackboard swarm feeding a part-by-part stream on one resident small model, gated by a mode-dial. **That fusion is novel enough to be worth naming as our own.** [my inference]

---

## 2. Compound AI Systems — the umbrella (and the cleanest justification of our thesis)

**Source:** [The Shift from Models to Compound AI Systems — BAIR blog, Zaharia, Khattab, Stoica et al, 2024-02-18](http://bair.berkeley.edu/blog/2024/02/18/compound-ai-systems/) · formalized in [Optimizing Model Selection for Compound AI Systems (arXiv 2502.14815)](https://arxiv.org/html/2502.14815v1).

**Definition (quoted):** "a system that tackles AI tasks using multiple interacting components, including multiple calls to models, retrievers, or external tools."

**Why systems beat monolithic models (their four reasons, quoted/paraphrased):**
1. **Better returns on engineering effort** — the load-bearing number: *AlphaCode 2* reaches ~80% by generating up-to-1M solutions + filtering/scoring, where scaling the base model alone moved 30%→35%. **A system extracted what scaling could not.**
2. **Dynamic capabilities** — systems pull in real-time info (retrieval) a frozen model cannot.
3. **Control & trust** — systems can filter outputs / verify facts that an isolated model cannot guarantee.
4. **Flexible cost/latency trade-offs** — tune the system per-application.

**Named examples:** AlphaCode 2 (generate-filter-score), AlphaGeometry (LLM + symbolic engine), **Medprompt** (retrieval + CoT + ensembling on GPT-4). Framework abstractions: LangChain, LlamaIndex, **DSPy** (optimizes the whole pipeline end-to-end), LangSmith (tracing).

**Maps to us:** This IS our thesis, stated by the people who named the category. Our swarm + staged stream is a compound AI system with an *intra-turn, streaming* topology. The "better returns on engineering effort" argument is the strongest framing for Tim's "quality from concurrency + composition, not size."
**Challenges us:** Their canonical examples are *aggregate-at-end* and *latency-tolerant* (generate 1M, then filter). Our hard constraint is the opposite — *real-time, part-by-part, voice-coupled*. The compound-AI literature is light on **streaming** compound systems. **That gap is where our originality lives, and also where the risk lives** (the field hasn't de-risked low-latency composition for us). [my inference]

---

## 3. Mixture-of-Agents (MoA) — the central "small composed ≥ large" evidence

**Source:** [Mixture-of-Agents Enhances Large Language Model Capabilities (arXiv 2406.04692)](https://arxiv.org/abs/2406.04692) · [Together AI blog](https://www.together.ai/blog/together-moa) · [GitHub](https://github.com/togethercomputer/moa).

**Architecture (quoted/extracted):** a **layered** structure. "Each layer comprises multiple LLM agents"; each agent in layer *n* uses "all the outputs from agents in the previous layer as auxiliary information." Roles split into:
- **Proposers** (generate candidate responses): WizardLM-2-8x22b, Qwen1.5-110B/72B-Chat, Llama-3-70B, Mixtral-8x22B, dbrx-instruct.
- **Aggregators** (synthesize the layer's proposals into one improved response): Qwen1.5-110B (full) / Qwen1.5-72B (Lite) / GPT-4o (hybrid).
- Full config = **3 layers**; MoA-Lite = **2 layers**.

**The headline numbers (quoted):**
- **AlpacaEval 2.0 LC win rate:** Together MoA **65.1±0.6%** vs **GPT-4o 57.5%** — a **7.6-point absolute** open-source-only win over GPT-4o.
- **MT-Bench:** MoA **9.25**, MoA-Lite **9.18**, GPT-4o **9.19** (roughly tied at ceiling).
- **FLASK:** MoA wins on correctness, factuality, insightfulness, completeness, metacognition.
- **Cost:** MoA-Lite "can match GPT-4o cost while achieving higher quality."

**The tradeoff they admit (quoted):** MoA "does come at the cost of a slower time to first token; reducing this latency is an exciting future direction."

**Maps to us:** This is the empirical proof Tim's thesis needs — *composition of smaller open models surpassed the frontier monolith.* Their **proposer→aggregator** split is exactly our **swarm-roles→synthesizer(brain)** split. Their "layers" ≈ our **chains** (role→role edges).
**Challenges us:** (1) **Latency.** MoA's own admitted weakness — slow TTFT — is *the exact thing our staged-stream is designed to hide* (speak Part 1 while the swarm works in its shadow). So our architecture is a **proposed FIX for MoA's headline flaw.** That's a strong story. (2) MoA mixes *big* models (70B–110B) and aggregates with a *big* model. We run **one 4B** as both swarm and aggregator. Whether a 4B aggregator can synthesize 32 role-outputs as well as a 110B aggregator is **unproven for us** and is the single biggest empirical risk. [my inference — must be proved by the spike]

---

## 4. Self-MoA — the counter-evidence that actually VINDICATES our one-model choice

**Source:** [Rethinking Mixture-of-Agents: Is Mixing Different Large Language Models Beneficial? — Self-MoA (OpenReview ioprnwVrDH, ICLR 2025)](https://openreview.net/forum?id=ioprnwVrDH).

**Core finding (quoted):** Mixing *different* LLMs does NOT reliably help. "MoA performance is rather sensitive to the quality, and mixing different LLMs often lowers the average quality of the models." Aggregating multiple outputs from the **single best** model — *Self-MoA* — beat standard mixed-MoA by **6.6% on AlpacaEval 2.0** and **3.8% average across MMLU, CRUX, MATH**.

**The principle:** there is a **quality–diversity tradeoff.** Diversity (different models) is only worth it if it doesn't drag in weaker outputs. Past some point, **adding more, worse, different voices hurts.**

**Maps to us — this is the most important single result in this file for our design decisions:**
- Our landscape §1 already commits to **"32 concurrent requests to the ONE resident 4B, not 32 models."** Self-MoA is direct empirical support: *one strong model, many draws, aggregated* is the configuration that won. **We are on the vindicated side of the field's biggest open MoA question.** Keep it.
- BUT Self-MoA's diversity comes from **temperature sampling the same prompt.** OUR diversity comes from **different ROLE PROMPTS** (memory-recall vs contradiction-checker vs tone-shaper). These are not the same kind of diversity. Self-MoA validates "one model, many draws"; it does **not** validate "many *functionally distinct role* draws" — that's closer to blackboard knowledge-sources (§6) and is **still ours to prove.** [my inference]
- Actionable design law it implies: **gate role-outputs by quality before injection.** If a role produces a low-quality JSON, injecting it may *lower* the next part's quality, per Self-MoA's quality-sensitivity finding. This argues for the landscape's `selector/brevity judge` and an **abstain** state on roles — drop weak contributions rather than always inject. [my inference, but well-grounded in the Self-MoA result]

*See also [Attention-MoA (arXiv 2601.16596)](https://arxiv.org/html/2601.16596v1): despite the name it does NOT use learned scalar weights — instead each agent generates a **natural-language critique** ("corrective instruction") of peers' responses, highlighting discrepancies/hallucinations, and agents synthesize these critiques to revise (≈5.7% of queries get explicit error-correction, 13.3% quality enhancement). It's a cross-critique refinement, not weighted aggregation — relevant to how our roles could critique each other before the brain composes.*

---

## 5. Skeleton-of-Thought (SoT) — the closest academic analog to our STAGED STREAM

**Source:** [Skeleton-of-Thought (arXiv 2307.15337)](https://arxiv.org/html/2307.15337v3) · [Microsoft Research writeup](https://www.microsoft.com/en-us/research/blog/skeleton-of-thought-parallel-decoding-speeds-up-and-improves-llm-output/).

**Mechanism (quoted):** Two stages. (1) **Skeleton stage** — the LLM "generate[s] the skeleton of the answer" (a concise outline of points). (2) **Point-expanding stage** — "parallel API calls or batched decoding to complete the contents of each skeleton point in parallel."

**Results (quoted):** speed-ups **1.83×–2.69×** (Claude 22s→12s = 1.83×; Vicuna-33B 43s→16s = 2.69×). Quality "not worse than baseline in ~60% of cases," and *improved* on generic/common-sense/knowledge/roleplay/counterfactual questions.

**The hard limitation (quoted):** SoT "cannot accelerate questions that require step-by-step thinking, in which the latter steps require the details from the earlier steps." Hence **SoT-R (with Router)** — a router decides per-question whether to apply SoT at all, preserving quality on reasoning tasks.

**Maps to us — very strongly:**
- SoT's **skeleton→parallel-expand** is a cousin of our **plan the parts → fill parts with swarm-fed context.** SoT-R's **router** is our **mode-dial** (`shape_for(mode)` — focus/background → never stage). The field already learned that *staging must be conditional*; our mode-dial bakes that in from day one.
**Challenges / differs from us:**
- SoT expands points **independently and in parallel, then concatenates.** That makes the answer feel slightly listy/disjoint (a known SoT critique) and means **later points cannot use earlier points.** OUR parts are **sequentially dependent by design** — Part 2's context is *resolved from* Part 1 + the swarm fired in Part 1's shadow. So we are **NOT SoT** — we deliberately keep the inter-part dependency SoT throws away, accepting the SoT limitation case (sequential reasoning) as our *normal* mode. **This is a real architectural divergence to state proudly: we trade SoT's full parallelism for coherence + voice-streaming.** [my inference]
- SoT's win was *latency*; ours is *latency-hidden quality*. Same machinery, different objective.

---

## 6. The Blackboard architecture — our 40-year-old ancestor (the strongest 1:1 map)

**Source:** [Blackboard Systems — Nii, Stanford CS-TR-86-1123 (PDF)](http://i.stanford.edu/pub/cstr/reports/cs/tr/86/1123/CS-TR-86-1123.pdf) · [The Evolution of Blackboard Control Architectures (UMass)](https://web.cs.umass.edu/publication/docs/1992/UM-CS-1992-071.pdf) · [A Blackboard Architecture for Control — Hayes-Roth (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/0004370285900633).

**The classic model (Hearsay-II speech understanding, 1970s; HASP/SIAP sonar):**
- A shared **blackboard** = a global, structured workspace holding partial solutions at multiple levels of abstraction.
- Independent **knowledge sources (KSs)** = specialist modules that *watch* the blackboard, and when their trigger-condition is met, **post a contribution** (a hypothesis/finding) back to it.
- A **control/scheduler** decides which KS runs next — **opportunistic, data-driven** problem-solving, not a fixed pipeline. Hayes-Roth's BB1 even put *control reasoning itself on a blackboard*.

**Maps to us — this is the cleanest "this is a named, proven pattern" entry in the whole file:**

| Blackboard concept | Our design |
|---|---|
| Blackboard (shared structured workspace) | the `swarm://<turn>/<role>` address space |
| Knowledge source (specialist, triggered) | a **role** in the Role Registry (memory-recall, contradiction-checker…) |
| KS posts a contribution | role writes JSON to its address |
| Control/scheduler picks next KS | our reactive "fires-when-deps-resolve" scheduler + mode-selected role set |
| Solution emerges by accretion on the blackboard | each PART resolves its context from posted role-outputs |
| Multiple abstraction levels on the board | the spine's layers (conscious/auxiliary/faculty/sense) |

**Why this matters:** it tells us this architecture *worked* for real-time-ish, multi-source interpretation (speech, sonar) decades ago, and gives us a **vocabulary and a control-theory** (opportunistic scheduling, KS triggering, hypothesis confidence) we can mine directly. **Recommendation: explicitly frame the swarm as a modern neural blackboard.** It earns credibility and hands us 40 years of control-strategy literature (e.g., focus-of-attention = exactly Tim's "budget = attention").
**Challenges us:** classic blackboards struggled with **control overhead** (deciding what to run next could dominate). Our mode-dial pre-selecting the role set is the mitigation — we avoid per-step control reasoning by fixing the cast per mode. [my inference]

---

## 7. Voice — two shapes: the chunked CASCADE (what we ARE) vs Moshi full-duplex (the rival)

### 7a. The mainstream chunked-cascade — our NEAREST production analog

**Source:** [Sequential Pipeline Architecture for Voice Agents — LiveKit](https://livekit.com/blog/sequential-pipeline-architecture-voice-agents) · [LiveKit vs Pipecat (Sellerity)](https://sellerity.co/blog/livekit-pipecat-web-voice-agents) · [Building Enterprise Realtime Voice Agents (arXiv 2603.05413)](https://arxiv.org/html/2603.05413v1).

**The pattern:** the standard 2026 production voice agent is a **cascade**: `Audio In → VAD → STT → LLM → TTS → Audio Out`, each stage swappable. The trick that makes it feel realtime is **streaming at stage boundaries** — quoted: "TTS starts synthesizing audio from the first sentence while the LLM is still generating the rest." Both **Pipecat** and **LiveKit Agents** support chunked processing keyed on the first sentence (or first chunk).

**Latency (quoted):** naive blocking = 1000–2000ms+; **streaming = 400–800ms.** Components: VAD 10–50ms, STT partial <100ms, **LLM first token 300–800ms**, **TTS first audio chunk 100–200ms**. The effective time-to-first-audio = STT + LLM-first-**sentence** + TTS-first-chunk — i.e. you pay only for the *first sentence* of LLM, not the whole reply.

**Cascade vs speech-to-speech tradeoff (quoted):** cascade gives "full visibility and swappable components, better tool-calling reliability, complete audit trails"; speech-to-speech gives "lower latency (200–300ms), preserves emotional tone/prosody, fewer stages." Their verdict: for most 2026 deployments "the cascaded pipeline remains the default" for control/debuggability.

**Maps to us — this is EXACTLY our voice plan, and it's the production-default, de-risked path:**
- Our "speak Part 1 while the swarm + brain produce Part 2" is **the chunked-cascade technique generalized from sentence-grain to PART-grain.** The field already ships "TTS-on-first-sentence-while-LLM-continues"; we extend the *gap* (the time bought by speaking Part 1) into a **compute window for 32 role-runs.** **That reframe is the cleanest statement of our voice mechanism: the swarm runs inside the latency the cascade already hides.** [my inference]
- It also tells us our part-grain decision (open fork: sentence/beat/paragraph) has a production precedent: **sentence-chunking is the proven default for first-audio latency**; coarser grains buy more swarm-compute but raise time-to-first-audio. The tradeoff is *measured*, not guessed.
- And it validates keeping the cascade: tool-calling reliability + auditability + swappable TTS are real wins our compound system needs.

### 7b. Moshi full-duplex — the RIVAL SHAPE that challenges the cascade entirely

**Source:** [Moshi: a speech-text foundation model for real-time dialogue (arXiv 2410.00037)](https://arxiv.org/abs/2410.00037) · [Kyutai PDF](https://kyutai.org/Moshi.pdf) · [GitHub kyutai-labs/moshi](https://github.com/kyutai-labs/moshi).

**Mechanism (quoted):**
- **Inner Monologue:** Moshi "first predict[s] time-aligned text tokens as a prefix to audio tokens" — it *thinks in text a beat ahead of speaking it as audio*, in one model.
- **Dual-stream:** models "its own speech and that of the user into parallel streams" → no explicit turn boundaries → handles interruptions/overlap → "arbitrary conversational dynamics."
- **No cascade:** replaces the VAD→STT→LLM→TTS pipeline with one speech-to-speech model, so "non-linguistic information... such as emotion or non-speech sounds" isn't lost.
- **Latency:** "theoretical latency of 160ms, 200ms in practice" — the first real-time full-duplex spoken LLM.

**Maps to / challenges us — this is the most important "is there a better shape?" entry:**
- OUR voice plan (landscape §1): each completed *text PART* is the TTS streaming unit; voice streams as the brain produces parts; brain↔TTS overlap. This is a **cascade** (brain→TTS) — exactly what Moshi *abolishes.*
- Moshi proves the overlap can happen **inside one model** without a part-by-part text handoff, with sub-200ms latency and prosody/emotion preserved. **Moshi's Inner Monologue is itself a "think slightly before you speak" mechanism — a micro-version of our staged stream, but at the token level inside one model rather than the part level across a swarm.**
- **Honest tension:** our swarm needs a *text substrate* (roles emit JSON; parts are text; injection resolves text addresses). A pure speech-to-speech model like Moshi has **no exposed text blackboard to inject 32 role-findings into.** So Moshi's shape and our shape are, at the limit, **incompatible** — you can't easily hang a structured blackboard swarm off a fused speech-token model.
- **The reconciliation [my inference, design proposal]:** our architecture and Moshi solve *different* halves. Moshi nails **conversational realtime feel** (interruption, overlap, prosody) but is a *single small model with no compositional cognition layer.* We nail **compositional cognition** (32 roles, blackboard, injection) but bolt voice on as a cascade. A **better shape than either** may be: keep our text blackboard + swarm for cognition, but make the **final-part TTS a streaming, interruptible, Moshi-like duplex layer** rather than a fire-once cascade — so the brain can be *interrupted mid-part* and the swarm re-fired against the new user input. This makes "barge-in" a first-class event that re-triggers the swarm. Treat Moshi not as a competitor but as **the spec for our TTS/listening edge.**

---

## 8. The supporting cast (each mapped briefly)

### 8a. Self-consistency — *same model, many draws, vote* (aggregate-at-end)
**Source:** [Self-Consistency Improves Chain of Thought Reasoning (arXiv 2203.11171), Wang et al, Google](https://arxiv.org/abs/2203.11171). Sample N reasoning paths at temperature, take the **majority answer.** The original "many concurrent draws of one model beat one greedy draw" result — ancestor of Self-MoA. **Maps:** our swarm IS many concurrent draws of one model; but our roles produce *complementary* findings, not *competing* answers to vote on. **Lesson:** for any role where multiple roles answer the *same* question (e.g. relevance-scorer), majority-vote/consistency is a cheap free quality lever. [my inference]

### 8b. Multi-agent debate — *many instances, interact-during, converge* (interact-during)
**Source:** [Improving Factuality and Reasoning through Multiagent Debate (arXiv 2305.14325), Du/Tenenbaum et al — "society of mind"](https://arxiv.org/abs/2305.14325) · [project page](https://composable-models.github.io/llm_debate/). Multiple instances "propose and debate... over multiple rounds to arrive at a common final answer"; each reads + critiques others. Config: **3 agents, 2 rounds** (bounded "due to computational cost"); more agents/rounds → higher accuracy. **Maps:** our **chains** (role→role edges, role B resolves over role A's output) are a *single-pass* debate. **Challenges:** debate's gains need *rounds* (iteration), which cost latency we can't spend intra-turn. **Lesson:** reserve debate-style multi-round refinement for the *contradiction-checker / fact-grounder* roles only, single bounce, not the whole swarm. [my inference]

### 8c. Branch-Solve-Merge (BSM) — *decompose → parallel-solve → fuse* (aggregate-at-end)
**Source:** [Branch-Solve-Merge Improves LLM Evaluation and Generation (arXiv 2310.15123), Meta AI](https://arxiv.org/abs/2310.15123). Three modules: **branch** (plan a decomposition into parallel sub-tasks), **solve** (independently), **merge** (fuse). **Maps:** this is *literally our turn shape* — branch = mode picks the role cast, solve = the swarm, merge = the brain composes the part. BSM is our turn-machinery described as a generic algorithm. **Strong corroboration that the branch→parallel-solve→merge skeleton is sound.** BSM applies it to *evaluation/generation quality*; we apply it *intra-turn, streamed.*

### 8d. LLM-Blender — *ensemble by rank-then-fuse* (aggregate-at-end)
**Source:** [LLM-Blender: Ensembling LLMs with Pairwise Ranking and Generative Fusion (arXiv 2306.02561), ACL 2023](https://arxiv.org/abs/2306.02561). Two modules: **PairRanker** (rank candidate outputs pairwise) + **GenFuser** (generate a fused answer from the top-K). **Maps:** a concrete recipe for *how the brain should merge 32 role-outputs* — rank for quality first (echoes Self-MoA's quality-sensitivity), fuse the best, don't blindly concatenate. **Directly informs our synthesizer/selector-judge design.**

### 8e. Speculative decoding — *the boundary case; NOT composition* (parallel-for-latency, same-model)
**Source:** [TensorRT-LLM Speculative Sampling docs](https://nvidia.github.io/TensorRT-LLM/advanced/speculative-decoding.html) · Medusa / EAGLE-3 / [Apple Mirror Speculative Decoding](https://machinelearning.apple.com/research/mirror). A small **draft** model proposes tokens; the **target** model verifies them in parallel — pure *speedup*, identical output distribution, **no compositional quality gain.** **Why it's in this file:** to draw the boundary. Speculative decoding is *parallelism for latency on one model's single answer* — it is **NOT** our pattern, and conflating the two would be a category error. **The clean distinction:** spec-decode makes *one* answer faster; our swarm makes a *better, multi-faceted* answer feasible in the same wall-clock. *(Note: vLLM, our server, supports speculative decoding natively — it's an orthogonal lever we could ALSO turn on to make each role-run faster, compounding with concurrency. [my inference])*

### 8f. SLMs are the future of agentic AI — *the economic case for our small-model swarm*
**Source:** [Small Language Models are the Future of Agentic AI (arXiv 2506.02153), Belcak/Heinrich et al, NVIDIA](https://arxiv.org/abs/2506.02153). Three positions (quoted): SLMs are "sufficiently powerful, inherently more suitable, and necessarily more economical for many invocations in agentic systems"; they shine where models do "a small number of specialized tasks repetitively and with little variation"; and **heterogeneous systems** (agents invoking multiple different models) are "the natural choice." Includes an LLM→SLM **conversion algorithm.** **Maps:** this is NVIDIA endorsing *exactly* our bet — a swarm of small specialized model-invocations (our roles = "specialized tasks repetitively") beats one big general model on cost/latency/throughput. **The strongest external authority for the economics of "32 small role-runs instead of 1 big call."**

---

## 9. Patterns → how each maps to OUR design (master table)

| Pattern | Axis (A/B/C) | Core idea | Maps to our piece | Tradeoff / challenge to us |
|---|---|---|---|---|
| **Compound AI Systems** (BAIR) | quality · many · either | results from the system of calls, not the model | the umbrella name for our whole design | examples are latency-tolerant + aggregate-at-end; streaming is under-explored = our risk + originality |
| **Mixture-of-Agents** (Together) | quality · many models · end | layered proposer→aggregator beats GPT-4o (65.1 vs 57.5) | swarm-roles→brain synthesizer; layers = chains | slow TTFT (our stream HIDES this); used big models + big aggregator — our 4B aggregator unproven |
| **Self-MoA** (ICLR'25) | quality · **same** model · end | mixing models lowers quality; one best model many draws wins (+6.6%) | **vindicates our one-4B, many-draws choice** | our diversity is *role-prompt*, not temperature — a different (untested) diversity; **gate weak role-outputs** |
| **Skeleton-of-Thought** | latency · same · end | outline → expand points in parallel (1.83–2.69×) | skeleton≈plan-parts; SoT-R router ≈ our mode-dial | SoT points are *independent*; ours are *dependent* — we keep coherence SoT drops |
| **Blackboard** (Hearsay-II) | quality · many · **during** | KSs post to shared workspace; opportunistic control | **1:1 with `swarm://` + reactive scheduler** | classic control-overhead — mitigated by mode pre-selecting the cast |
| **Chunked-cascade voice** (LiveKit/Pipecat) | latency · n/a · during | STT→LLM→TTS, TTS starts on first sentence while LLM continues (400–800ms) | **our exact voice plan, generalized sentence→part grain**; swarm runs in the hidden gap | coarser part-grain raises time-to-first-audio; cascade is the de-risked 2026 default |
| **Moshi full-duplex** | latency · one model · during | inner-monologue + dual-stream, no cascade, 160/200ms | challenges part-as-TTS cascade; = spec for our TTS/listen edge | pure speech model has no text blackboard to inject into — shapes are incompatible at the limit; reconcile by making TTS interruptible/duplex |
| **Self-consistency** | quality · same · end | sample N paths, majority vote | cheap quality lever for same-question roles | only works for votable answers, not complementary findings |
| **Multi-agent debate** | quality · many · during | instances critique over rounds | our chains = single-pass debate | gains need *rounds* = latency we lack intra-turn; reserve for checker roles |
| **Branch-Solve-Merge** | quality · many · end | decompose→parallel-solve→fuse | **literally our turn shape** as a generic algorithm | corroboration, not challenge |
| **LLM-Blender** | quality · many · end | rank candidates → generative fusion | recipe for HOW the brain merges 32 outputs | rank-by-quality first (echoes Self-MoA) — don't concatenate |
| **Speculative decoding** | **latency · same** · n/a | draft proposes, target verifies; same output | **boundary case — NOT composition**; orthogonal speedup we can also use | category error to conflate with our swarm |
| **SLMs-for-agentic** (NVIDIA) | — | small specialized models are sufficient + economical | economic authority for our small-model swarm | endorses, doesn't challenge |

---

## 10. Shapes that may be BETTER than ours (the unknown-unknowns)

Honest scout duty — places where the outside world suggests our shape could be improved or is taking an avoidable risk:

1. **Rank-then-fuse the swarm, don't concatenate (from LLM-Blender + Self-MoA).** Our landscape injects role-outputs as resolved context. Self-MoA proves *low-quality injections actively hurt.* **Better shape:** a quality-ranking gate (the selector-judge) ranks role JSONs, the brain fuses only the top-K, weak/contradictory ones are *dropped* (the `abstain` role-state). Make the injection edge *selective*, not *all-in*. This is probably the highest-value refinement in this file.

2. **Make the TTS edge Moshi-like (interruptible duplex), not a one-way cascade.** Our part-as-TTS-unit is a cascade Moshi shows is avoidable. **Better shape:** treat the final-part TTS as a streaming, *barge-in-able* layer; a user interruption is a first-class event that re-fires the swarm against the new input mid-turn. This buys true conversational realtime feel without abandoning our cognition layer.

3. **Differential aggregator focus over flat injection.** Don't let the brain treat all 32 role-outputs as equal context. Mode already biases *which* roles fire; extend it to bias *how much each counts* — by role, by mode, by confidence. (= the blackboard "focus of attention" = Tim's "budget = attention.") *Mechanism note:* Attention-MoA (§4) does this NOT by learned scalar weights but by **natural-language cross-critique** between agents before synthesis — a lighter, prompt-level way to get the same "weigh the good, discount the contradicted" effect, and a candidate for how a contradiction-checker role could annotate the others before injection. [my inference]

4. **Conditional staging is non-negotiable (from SoT-R).** The field learned that staging *hurts* some question types (sequential reasoning, simple replies). Our mode-dial must default to **don't-stage** for focus/background and only stage when the thought-shape benefits — exactly as landscape §3 item 6 specifies. SoT-R is the external proof this gate is mandatory, not optional.

5. **Single-bounce debate for adversarial roles only.** Don't make the whole swarm iterate (latency). But contradiction-checker / fact-grounder roles measurably benefit from *one* critique bounce (debate evidence). Model these as 2-node chains, not single roles.

6. **Adopt blackboard control vocabulary wholesale.** 40 years of "opportunistic scheduling / focus-of-attention / hypothesis confidence / KS triggering" maps onto our open forks (role triggers, slot budget, GC). We're re-deriving solved control theory — mine it instead.

---

## 11. Sources (all visited)

- BAIR — Compound AI Systems: http://bair.berkeley.edu/blog/2024/02/18/compound-ai-systems/
- Optimizing Model Selection for Compound AI Systems (arXiv 2502.14815): https://arxiv.org/html/2502.14815v1
- Mixture-of-Agents (arXiv 2406.04692): https://arxiv.org/abs/2406.04692 · Together blog: https://www.together.ai/blog/together-moa · GitHub: https://github.com/togethercomputer/moa
- Self-MoA / Rethinking MoA (OpenReview ioprnwVrDH, ICLR 2025): https://openreview.net/forum?id=ioprnwVrDH
- Attention-MoA (arXiv 2601.16596): https://arxiv.org/html/2601.16596v1
- Skeleton-of-Thought (arXiv 2307.15337): https://arxiv.org/html/2307.15337v3 · MSR: https://www.microsoft.com/en-us/research/blog/skeleton-of-thought-parallel-decoding-speeds-up-and-improves-llm-output/
- Blackboard Systems, Nii (Stanford CS-TR-86-1123): http://i.stanford.edu/pub/cstr/reports/cs/tr/86/1123/CS-TR-86-1123.pdf · UMass evolution: https://web.cs.umass.edu/publication/docs/1992/UM-CS-1992-071.pdf · Hayes-Roth BB1 (ScienceDirect): https://www.sciencedirect.com/science/article/pii/0004370285900633
- Chunked-cascade voice — LiveKit Sequential Pipeline: https://livekit.com/blog/sequential-pipeline-architecture-voice-agents · LiveKit vs Pipecat (Sellerity): https://sellerity.co/blog/livekit-pipecat-web-voice-agents · Building Enterprise Realtime Voice Agents (arXiv 2603.05413): https://arxiv.org/html/2603.05413v1
- Moshi (arXiv 2410.00037): https://arxiv.org/abs/2410.00037 · Kyutai PDF: https://kyutai.org/Moshi.pdf · GitHub: https://github.com/kyutai-labs/moshi
- Self-Consistency (arXiv 2203.11171): https://arxiv.org/abs/2203.11171
- Multi-agent Debate (arXiv 2305.14325): https://arxiv.org/abs/2305.14325 · project: https://composable-models.github.io/llm_debate/
- Branch-Solve-Merge (arXiv 2310.15123): https://arxiv.org/abs/2310.15123
- LLM-Blender (arXiv 2306.02561): https://arxiv.org/abs/2306.02561
- SLMs are the Future of Agentic AI (arXiv 2506.02153, NVIDIA): https://arxiv.org/abs/2506.02153
- Speculative decoding — TensorRT-LLM: https://nvidia.github.io/TensorRT-LLM/advanced/speculative-decoding.html · Apple Mirror SD: https://machinelearning.apple.com/research/mirror

---

*Scout's closing read: our design is not a leap into the dark. It is a **streaming, intra-turn fusion of three proven patterns** — a Blackboard swarm (Hearsay-II) on one small model (Self-MoA / SLM-agentic), composed Branch-Solve-Merge style into a part-by-part stream (Skeleton-of-Thought's staging, conditioned by its router-lesson). The umbrella is Compound AI Systems; the empirical green light is MoA-beats-GPT-4o; the sharpest open risk is the 4B-as-aggregator question and the voice-cascade-vs-Moshi-duplex choice. The field has de-risked most of our pieces individually; what's genuinely ours — and unproven — is the **real-time streaming fusion** of them.*
