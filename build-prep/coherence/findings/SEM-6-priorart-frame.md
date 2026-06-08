# SEM-6 — External prior art (the SEMANTIC half) + the bigger frame + cross-stream/recursion what-ifs

> Companion to `../SEMANTIC-LAYER-ANCHOR.md`. The **semantic sibling** of the structural round's
> `AREA-6-crossstream-priorart.md`. My allocated area is two threads:
> **(1)** External prior art for the *semantic* detector class — LLM-as-judge, doc/comment-code drift,
> semantic code search / LLM codebase understanding, LLM-built knowledge-graphs-from-code, cheap-model
> swarms for bulk passes — each mapped to **its delta** (what the anchor adds), not summarized.
> **(2)** The bigger frame + the anchor §8 what-ifs, grounded in this repo's real code: the continuous
> background watch, semantic finding-types as declared roles, the swarm feeding the RHM, the recursion,
> the introspective-data law — and the load-bearing question: **is the semantic-coherence swarm the same
> KIND of thing as the cognition swarm — another lens on the one swarm engine?**
>
> **Marking convention** (same as the structural sibling): **[OBS]** observed in real code (file:line) ·
> **[INF]** inferred · **[PRIOR-ART]** external, cited · **[IDEA]** my own proposal.
>
> **I deliberately do NOT re-cover what the structural AREA-6 already claimed** — fitness functions,
> code-property-graphs (Joern/CodeQL), ADRs, the AgentField "200-agent convergence problem." Those are its
> territory; I reference them and build past them. My lane is the *meaning* side.

---

## Headline (stated once, so the rest reads against it)

**For the SEMANTIC detector class the cross-stream convergence is not an analogy — it is nearly literal.**
The structural sibling concluded that structural-Coherence and cognition *share the pattern* (registry →
projection → SSE → reflects-never-owns) but the structural detector itself rides AST/registry/string
machinery that is *not* the swarm. For the **semantic** detector the engine **is `run_swarm` itself**
**[OBS cognition.py:523]**: a repo artifact becomes the "utterance," a declared role reads it, and the role
emits a **schema-enforced finding-JSON** to a `run://` address — the exact "fan out cheap structured
judgments" engine, pointed at the repo instead of a chat turn. So the anchor §8's question — *"is this
ANOTHER lens on the one swarm engine?"* — answers **yes, for semantic detection it is the same engine, not
just the same pattern.** That is the single most important frame this companion lands, and everything below
is in service of it: the prior art shows the world has the *pieces* (LLM judges, doc-drift detectors,
semantic search, code knowledge-graphs) but **nobody composes them into a cheap-concurrent-small-model
detector swarm whose output is a *held, dispositioned coherence finding* feeding an autonomous build loop** —
and this system already owns that engine.

---

## Pre-flight correction: the capability numbers (verify the anchor's claim against the real factsheet)

The anchor §2 cites "**~32 concurrent inferences at ~3000 tok/s** … the entire repo and all documentation
read in seconds." Two of those numbers are loose and one denominator was badly wrong in my first pass. The
honest, measured version — **which still supports "free in seconds," so this refines, it does not refute:**

**Corpus denominator (corrected) [OBS].** A naive `find` over `~/company` returns 14,825 `.py` files /
5.4M LOC — but that **includes `.venv`/site-packages/node_modules**. Excluding dependencies, the
**first-party corpus is ~234 Python files / ~48,035 LOC + ~124 markdown files + ~39 TS/TSX**. That is the
real denominator the "whole repo in a minute" claim must be measured against. (`suite.py` alone is 9,776
lines **[OBS]** — it is ~20% of all first-party Python; the unit-of-read question in §6.2 of the anchor is
real precisely because of files like this.)

**Throughput (corrected) [OBS, `~/vllm-tests/BENCHMARK_FACTSHEET.md`].** The resident model is
`Qwen3.5-4B-AWQ-4bit`. The measured numbers:
- Concurrency 32, 4K ctx → **2,241 tok/s aggregate** (not 3,000), ~153ms TTFT. Aggregate **plateaus at 32** —
  beyond that the scheduler queues, throughput stays flat. Max safe = 64 (2–4s latency); never above 128.
- Per-request **decode is rock-steady ~100 tok/s** regardless of output length.
- **The number that actually matters for this use, and that the anchor undersold:** *reading* a repo artifact
  is **PREFILL**, not decode — and prefill **scales sublinearly with length**: 30K input tokens prefilled in
  **~1.07s**, "no quality dropoff," which the factsheet calls *"the model's biggest win for RAG / document-QA
  workloads."* **Emitting a finding** is a small schema-constrained JSON decode (tens of tokens).

**So the real cost model [INF, computed from the above]:** a semantic sweep is `n_units` reads where each
read = (prefill the unit + its self-description) + (decode a small finding JSON). The expensive axis people
fear (decode at 100 tok/s) barely applies — findings are tiny. The cheap axis (prefill, sublinear, ~28K
tok/s effective at 30K) is exactly the axis bulk reading lives on. Rough order: ~234 files, even at
~one-module-plus-its-AGENTS.md per read and a ~50-token finding each, is a few hundred reads × tiny decode,
fanned 32-wide → **a whole-first-party-repo semantic pass is genuinely a small number of minutes, plausibly
under one.** The anchor's *spirit* ("free in seconds/minutes") survives; its *figures* (3,000 tok/s, "the
whole repo" over 5.4M LOC) do not — and the honest version is the one to build on.

---

## THREAD 1 — External prior art for the SEMANTIC detector class (each → its delta)

### 1.1 LLM-as-judge — the trust mechanism, and the place it's weakest is exactly the anchor's §6.1 [PRIOR-ART]

This is the most load-bearing body of prior art for the anchor, because the *entire* semantic layer rests on
"can you trust a 4B judgment enough to treat it as a candidate?" (anchor §6.1, the make-or-break).

- **LLM-as-judge is a mature, surveyed method** — using one LLM to score/evaluate another's output across
  open-ended tasks ([A Survey on LLM-as-a-Judge, arXiv 2411.15594](https://arxiv.org/html/2411.15594v6);
  [ScienceDirect survey](https://www.sciencedirect.com/science/article/pii/S2666675825004564)). The survey's
  own framing is telling: it devotes its core to *"strategies to enhance reliability, including improving
  consistency, mitigating biases."* The reliability problem is the headline, not a footnote.
- **The documented bias set** ([G-Eval guide, confident-ai](https://www.confident-ai.com/blog/g-eval-the-definitive-guide);
  [Comet LLM-as-judge guide](https://www.comet.com/site/blog/llm-as-a-judge/)): **position bias** (favoring
  the first/last option), **verbosity bias** (favoring longer answers), and **self-preference** — research
  shows GPT-4/Claude-class models **favor their own outputs 10–25% more** during evaluation. And smaller
  judges are *less* reliable than the frontier judges these studies use.

**The delta the anchor adds — and a SHARPENING that contradicts the anchor's own §6.1 optimism [IDEA]:**
1. **The anchor never asks the 4B to *score* or *rank*** — that is where position/verbosity bias bites. It
   asks for a **binary/typed structural judgment** ("does this module contradict its docstring?", schema-
   enforced). `roles/check.py` is the live template **[OBS]**: `CheckOut(contradicts: bool, note: str)` — a
   yes/no contradiction flag, not a 1–10 quality score. That sidesteps the *ranking* biases entirely. Good.
2. **But the anchor's proposed trust backstop is weaker than it claims — and the anchor mischaracterized
   its own mechanism.** Anchor §6.1 offers *"multi-role agreement (the cognition stream's `run_jury` — **N
   roles** must concur)."* **That is not what `run_jury` does.** The built mechanism is **N *draws* of the
   SAME role** at temperature>0 **[OBS cognition.py:645]**, and the jury's own docstring refutes its use as a
   correctness signal **[OBS cognition.py:649-651]:** *"N draws on ONE model are CORRELATED — variance, not
   independent error."* So there are three distinct things, and only one exists:
   - **`run_jury` as built** = N correlated draws of one prompt → measures *the model's self-agreement* —
     buys **stability/determinism** (a finding doesn't flicker, anchor §6.6), **not correctness**. The
     LLM-as-judge literature names self-agreement as a *failure* mode (self-preference, shared blind spots),
     not corroboration.
   - **A true multi-ROLE jury** (N *different* detector prompts reading the same artifact — focus/check/
     ground-style diversity) — what the anchor's *words* gestured at — would be *less* correlated and a
     *partial* correctness signal. **It does not exist today**; it is buildable as a set of declared roles
     (§2.4), but it is still single-model, so still not independent error.
   - **The real correctness backstop** is therefore neither: it is the **candidate-only floor + a stronger
     second model.**
   So the anchor's §6.1 jury answer is, by its own code's admission, a *consistency* check (does the model say
   the same thing twice?), **not** a *correctness* check — and the precise correction is sharper than "the
   jury is weak": *the anchor named "N roles" but the built mechanism is "N draws of one role"; the built one
   buys only stability; a true multi-role jury would buy more but doesn't exist yet; either way the
   consequential-finding backstop is the stronger second model.* The honest trust stack:
   - jury → buys **determinism/stability** (a finding doesn't flicker), addressing anchor §6.6 — *not*
     correctness;
   - the **positive-only / candidate-only floor** (anchor §3, your patterned-visibility law) is the *real*
     backstop — a 4B "looks wrong" is a lead a *stronger model confirms* before it reaches Tim; a 4B "looks
     fine" proves nothing;
   - the `verify_jury` role docstring **already anticipates the fix [OBS]**: its verdict-rule shape accepts a
     *"future 2nd-model / cloud tiebreak slotting in."* That is the genuine independent-error judge — a Claude
     Code agent (the loop's own agent) is exactly that stronger second model.
3. **Net delta:** the world has LLM-as-judge as a *stateless scoring* tool for *eval pipelines*. The anchor
   makes it a **typed, schema-constrained, candidate-only detector feeding a held coherence model**, with the
   correctness burden explicitly deferred to a stronger confirmer — and the repo's own jury caveat is the
   evidence that this deferral is *necessary*, not optional. **This is the most important correction to the
   anchor in this companion: a single-4B jury is a stability mechanism, not a trust mechanism.**

### 1.2 Doc/comment-code drift detection — the anchor's "intent-vs-implementation" check, at a higher altitude [PRIOR-ART]

There is a real, active research line on detecting when code and its natural-language description diverge:

- **Just-In-Time inconsistency detection** ([AAAI, Panthaplackel et al.](https://ojs.aaai.org/index.php/AAAI/article/view/16119/15926))
  — detect whether a *comment* becomes inconsistent *as a result of a code change*, to catch the staleness at
  edit time.
- **Code-comment inconsistency → bug introduction** ([arXiv 2409.10781](https://arxiv.org/html/2409.10781v1))
  — uses GPT-3.5 to study how comment-code inconsistency correlates with bugs; LLMs *can* judge consistency.
- **Detection + rectification** ([UMass CS692P survey PDF](https://people.cs.umass.edu/~brun/class/2024Fall/CS692P/idllm.pdf);
  [ASE 2025, "Detecting and Mitigating Inconsistencies Between Code and Documentation"](https://dl.acm.org/doi/pdf/10.1109/ASE63991.2025.00397))
  — learning-based and LLM-based methods to both flag and *fix* doc-code mismatch; static-analysis baselines
  exist for code-documentation inconsistency.

**The delta the anchor adds:**
1. **Altitude.** All of this is **comment-level / docstring-level** — a function vs the sentence above it.
   The anchor's intent-vs-implementation check (§4①) is **module-vs-`AGENTS.md`** and **module-vs-the-design-
   doc-that-spawned-it** — *architectural intent*, not line-comments. This codebase has the per-module
   constitution layer (`AGENTS.md` files, drift-homes) that makes that altitude *checkable*: the structural
   drift-home pattern **already asserts declarations stay reflected in `AGENTS.md`** **[OBS rules.py:43-46,
   activation.py:36]** — the *semantic* version is "does the module still *do* what its AGENTS.md *says*," the
   complement the structural check structurally cannot see (anchor §1).
2. **Held, not just flagged.** The prior art emits a warning at review time and forgets it. The anchor makes
   each inconsistency a **typed finding with a disposition and a burn-down** — and crucially, the structural
   sibling's own/reflect split applies *a fortiori* here: a doc-drift finding's *detection* is re-derivable
   (re-read the pair) and its *disposition* ("this AGENTS.md is aspirational, accepted") is the owned ADR.
3. **No-human framing.** The JIT-detection literature assumes a developer reads the flag and decides. Here
   the flag feeds an autonomous loop's worklist; "the prose is the institutional memory" (anchor §1) makes
   *intent drift* the highest-stakes finding, because no human re-reads the docs.

### 1.3 Semantic code search / LLM codebase understanding — answers queries; the anchor *watches* [PRIOR-ART]

Sourcegraph **Cody**, **Greptile** (literally in this agent's MCP toolset), GitHub Copilot indexing, DeepWiki:

- Semantic code search "finds code by intent, using AI and vector embeddings to understand what the code
  *does* rather than relying on exact [matches]"
  ([Sourcegraph](https://sourcegraph.com/blog/semantic-code-search-what-it-is-and-how-it-works);
  [How Cody understands your codebase](https://sourcegraph.com/blog/how-cody-understands-your-codebase)).
- Greptile builds a graph/embedding index of a repo to power **AI code review and codebase Q&A**
  ([Greptile](https://www.greptile.com/blog/semantic-codebase-search)).
- A comparison notes most of these (Cody, Greptile, DeepWiki) have **cloud components** — your data leaves the
  box ([Ry Walker, Code Intelligence Tools](https://rywalker.com/research/code-intelligence-tools)).

**The delta the anchor adds:**
1. **Pull → push.** These tools are *reactive query engines*: you ask "where does X happen," they answer. The
   anchor is a **proactive standing watch** — it asks the questions *nobody asked*, on a cadence, and **holds
   the answers as findings** until disposed. Semantic search retrieves; the coherence swarm *adjudicates and
   remembers*. (The anchor §8's "feed the RHM" what-if is where the two *meet* — see §2.3 below: the RHM is
   the pull-face, the swarm is the push-engine that keeps its index warm.)
2. **Local-first, by construction.** Cody/Greptile/DeepWiki are cloud or cloud-component; the anchor's swarm
   is the **resident on-box 4B** — no code leaves the machine, which matters for a system whose whole premise
   is self-hosting (the no-devs / self-hosting-spine law in the project memory). That is not a feature these
   tools can match for a private self-modifying repo.
3. **Output shape.** Their output is *prose for a human* (a chat answer, a review comment). The anchor's is a
   **schema-validated typed record** **[OBS fabric/transport.py:47-48]** — a finding *by construction*, not
   prose to parse. This is the difference between "a tool you ask" and "a substrate that accretes."

### 1.4 LLM-built knowledge-graphs-from-code (GraphRAG) — the *meaning*-graph vs the structural CPG [PRIOR-ART]

This is the precise point where the semantic round diverges from the structural round's prior art.

- **GraphRAG** (Microsoft) uses an **LLM to *extract* a knowledge graph from raw text/data** — entities,
  relations, then a community hierarchy + LLM-generated community summaries — and retrieves over that graph
  ([microsoft/graphrag](https://github.com/microsoft/graphrag);
  [Project GraphRAG, MS Research](https://www.microsoft.com/en-us/research/project/graphrag/);
  [GraphRAG docs](https://microsoft.github.io/graphrag/)). The structural round cited **CodeGraph/Joern/CodeQL**
  — graphs built by **AST parsing** (deterministic, structural).

**The delta — and it IS the structural-vs-semantic distinction the task asks me to draw:**
1. **Two different graphs of the same repo.** The structural CPG (last round, Joern/Area C) is built by
   *parsing* — nodes are symbols, edges are call/data/control, exact and deterministic. The GraphRAG-style
   graph is built by an *LLM reading for meaning* — nodes are *concepts*, edges are *semantic relations the
   model inferred*. The anchor's "concept/vocabulary coherence" detector (§4①, the *built-twice* detector) is
   **a GraphRAG-style meaning-graph used for a purpose GraphRAG doesn't serve**: not retrieval, but **finding
   where one concept wears two names** (the mode-dial-built-twice incident — clustering by *concept*, flagging
   divergent names for one idea). GraphRAG clusters to *summarize*; the anchor clusters to *detect incoherence*.
2. **The disagreement what-if (anchor §8) is exactly the two-graph join [IDEA].** The structural sibling's
   own/reflect frame + this: the structural CPG says "wired" (an edge exists); the semantic meaning-graph says
   "this is dead — only an obsolete test references it." **The highest-value finding is their *disagreement*** —
   neither graph catches it alone. This is the literal composition of the two rounds: structural = the
   skeleton (trustworthy, auto-actable), semantic = the flesh (candidate-only), and *the seam between them*
   (structural-says-wired ∧ semantic-says-meaningless) is a finding-type no single tool in the prior art emits.
3. **Cost/locality delta:** GraphRAG's graph-build is famously *expensive* (frontier-model extraction over a
   whole corpus). The anchor's is the **resident 4B**, prefill-dominated, on-box — and **re-derivable, not
   maintained** (the own/reflect split): you don't *keep* a stale meaning-graph, you *re-read* meaning cheaply.
   GraphRAG builds an index to keep; the anchor reflects a view it can recompute.

### 1.5 Cheap/small-model swarms for bulk passes — thin external work, and the thinness IS a finding [PRIOR-ART + IDEA]

I searched specifically for *small/cheap-model swarms doing bulk semantic codebase passes*, and the honest
result is: **the external work here is thin, and concentrated on multi-agent *orchestration*, not cheap-bulk
*detection*.**

- The hits are **orchestration frameworks** (`kyegomez/swarms`: "production-ready multi-agent architectures —
  sequential, concurrent, hierarchical" — [GitHub](https://github.com/kyegomez/swarms)) and **practitioner
  reports** ([Zach Wills, "I managed a swarm of 20 AI agents"](https://zachwills.net/i-managed-a-swarm-of-20-ai-agents-for-a-week-here-are-the-8-rules-i-learned/);
  [hamy.xyz, "9 parallel AI agents that review my code (Claude Code)"](https://hamy.xyz/blog/2026-02_code-reviews-claude-subagents)).
- The pattern in *all* of these: a small number of **frontier-model agents** (Claude/GPT subagents), each
  doing a *focused* review pass, orchestrated for higher-signal review. The "9 parallel agents" piece is the
  closest analog — specialized reviewers (test-runner, linter, security) running concurrently.

**The delta — and the candid finding [IDEA]:**
1. **Nobody is doing cheap-*small*-model *bulk* semantic detection at the corpus scale the anchor proposes.**
   The external swarms are ~9–20 *frontier* agents on *focused* tasks (cost ~dollars/run, latency ~minutes).
   The anchor is **32+ concurrent *4B* reads over the *whole* repo, essentially free, re-runnable on demand**.
   That combination — *small model × massive concurrency × whole-corpus × schema-typed findings × held in a
   coherence substrate* — **I did not find in the external work.** The thinness is itself the finding: this is
   a relatively unoccupied design point, and the reason is economic — most people don't *have* a resident
   massively-concurrent small model with a VRAM resource-manager, so the bulk-cheap pass isn't on their menu.
   **This system does** (`ops/cli/gpu.py`, `services.json`, the 2,241 tok/s @ 32 measured) — which is exactly
   the "capability that changes the economics" the anchor §2 names. The prior-art gap *validates* anchor §2.
2. **The orchestration prior art is a hazard map, not a competitor.** The practitioner swarms repeatedly hit
   the **convergence/coordination problem** (the structural sibling's AgentField cite is the canonical
   version). The anchor's swarm sidesteps it by construction: the roles are **stateless, declared, read-only
   detectors** emitting to **distinct `run://` addresses** **[OBS cognition.py:668, run_swarm:582-585]** with
   a **per-wave barrier then serialized store writes** — there is no inter-agent coordination to converge,
   because each detector is a pure function of its input unit. The thing that makes the external swarms hard
   (agents stepping on each other) **doesn't exist here** because detection is fan-out-pure, not collaborative.

### Thread-1 source list
- [A Survey on LLM-as-a-Judge — arXiv 2411.15594](https://arxiv.org/html/2411.15594v6)
- [A survey on LLM-as-a-judge — ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2666675825004564)
- [G-Eval: LLM-as-a-Judge — confident-ai (self-preference 10–25%)](https://www.confident-ai.com/blog/g-eval-the-definitive-guide)
- [LLM-as-a-Judge guide — Comet](https://www.comet.com/site/blog/llm-as-a-judge/)
- [Deep Just-In-Time Inconsistency Detection Between Comments and Code — AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/16119/15926)
- [Impact of Code-Comment Inconsistency on Bug Introduction (LLM) — arXiv 2409.10781](https://arxiv.org/html/2409.10781v1)
- [Code Comment Inconsistency Detection & Rectification — UMass CS692P PDF](https://people.cs.umass.edu/~brun/class/2024Fall/CS692P/idllm.pdf)
- [Detecting and Mitigating Inconsistencies Between Code and Documentation — ASE 2025](https://dl.acm.org/doi/pdf/10.1109/ASE63991.2025.00397)
- [Semantic Code Search — Sourcegraph](https://sourcegraph.com/blog/semantic-code-search-what-it-is-and-how-it-works)
- [How Cody understands your codebase — Sourcegraph](https://sourcegraph.com/blog/how-cody-understands-your-codebase)
- [AI Code Generators vs. Semantic Search — Greptile](https://www.greptile.com/blog/semantic-codebase-search)
- [Code Intelligence Tools for AI Agents Compared — Ry Walker](https://rywalker.com/research/code-intelligence-tools)
- [microsoft/graphrag — GitHub](https://github.com/microsoft/graphrag) · [Project GraphRAG — MS Research](https://www.microsoft.com/en-us/research/project/graphrag/) · [GraphRAG docs](https://microsoft.github.io/graphrag/)
- [kyegomez/swarms — GitHub](https://github.com/kyegomez/swarms)
- [Managing a swarm of 20 AI agents — Zach Wills](https://zachwills.net/i-managed-a-swarm-of-20-ai-agents-for-a-week-here-are-the-8-rules-i-learned/)
- [9 Parallel AI Agents That Review My Code (Claude Code) — hamy.xyz](https://hamy.xyz/blog/2026-02_code-reviews-claude-subagents)

---

## THREAD 2 — The bigger frame + the §8 what-ifs, grounded in this repo

### 2.0 The frame: the semantic-coherence swarm IS another lens on the one swarm engine [OBS → IDEA]

The task's central question — *is the semantic-coherence swarm the same KIND of thing as the cognition
swarm?* The structural sibling answered "sibling, not merge" for *structural* Coherence (shared pattern,
different machinery). **For the semantic layer the answer is tighter, and it is grounded, not analogical:**

Both are **cheap-concurrent-4B-reads-emitting-structured-judgments.** Concretely, side by side **[OBS]**:

| | Cognition swarm (per-turn) | Semantic-coherence swarm (this anchor) |
|---|---|---|
| Engine | `run_swarm` (cognition.py:523) | **the same `run_swarm`** |
| "Utterance" | the operator's chat turn | **a repo artifact** (module + its AGENTS.md / design doc) |
| Roles | `roles/*.py` (focus/recall/ground/check…) | **`roles/*.py` semantic detectors** (half-migration, intent-drift…) |
| Output | schema-enforced JSON to `run://<turn>/<role>` | **schema-enforced finding-JSON to `run://`** |
| Concurrency | ThreadPool sized to `swarm_slots` (cognition.py:582-585) | the same pool, same VRAM gate |
| Determinism | identical resolved inputs → identical routing (C0.2) | identical code → identical findings (anchor §6.6) |

`roles/check.py` is the proof that a *detector role already exists in spirit* **[OBS]**: it reads a forming
answer **against grounded facts** and emits `{contradicts: bool, note: str}` — that is *already a coherence
judgment*, just pointed at a chat answer instead of at a module-vs-its-docstring. **A semantic coherence
detector is `check.py` with the inputs swapped from `(forming-answer, ground)` to `(module, AGENTS.md)`.**

**So the frame [IDEA]:** there is **one swarm engine**; cognition and semantic-coherence are **two activation
contexts of it** (literally — see §2.1), reading two different things for two different lenses. This is a
*stronger* unification than the structural round could claim, and it is the precise answer to anchor §8's
"another lens on the one swarm engine?" — **yes, the same engine, the same roles-mechanism, the same
addressing, the same determinism property; only the utterance and the role-set differ.** I still recommend
the *finding model* be a sibling lens (own/reflect, persistent — per the structural round), but the
*detector* is not a sibling of the swarm — **it is the swarm.**

### 2.1 The continuous background watch — the mechanism is OBS-ready; only the driver is needs-tim [OBS]

Anchor §8's first what-if: *not just on-demand, but a continuous low-priority background watch keeping the
meaning-graph warm so drift is caught as it happens.* This is **not speculative — the substrate is built**:

- The `background` activation context **already exists** **[OBS activation.py:77-85]**: trigger = `idle-loop`,
  `reply: False`, `fires_swarm: True`, destinations `["surface", "address", "lane"]` — *"between-turn
  consolidation/preparation under the mode's budget."* A background swarm landing findings at `surface`/`lane`
  is **exactly** the continuous watch. The entry point `fire_activation(suite, "background", …)` **is
  built and works by use** **[OBS activation.py:141-244]**.
- The `rollup` context **already exists** **[OBS activation.py:96-105, consolidate_rollup:247]**: timer trigger,
  read-half, consolidates the swarm's own run-records into one distribution — the introspective-data rollup a
  coherence burn-down would reuse (§2.5).
- **The honest gating [OBS activation.py:15-20, 79]:** the *mechanism* is ready, but the **always-on DRIVERS**
  that *call* these entry points (the idle-loop daemon, the timer/`.timer` scheduler) are **explicitly flagged
  needs-tim** — *"do NOT stand up an always-on GPU-consuming daemon; that is Tim's call."* So the accurate
  status of the continuous-watch what-if is: **ready-but-driver-gated.** Invoking the entry point fires a
  semantic sweep today; making it *continuous* is a deliberate Tim decision about an always-on GPU consumer,
  not a build gap.

This answers the anchor §6.4 cost/cadence worry with a real position: on-demand (a CLI verb) needs **no**
new driver; continuous needs a driver Tim must consciously authorize. The economics differ accordingly.

### 2.2 VRAM contention (anchor §6.4) — already answered by construction [OBS]

The anchor §6.4 worries a whole-repo sweep "contends for the same VRAM the live cognition + chat use … 'free'
is only free if it doesn't starve the live system." **This is solved in code, not a risk to research:**

- `FLOOR_RESERVE_R` **[OBS activation.py:50-52]** = the floor on reserved slots for the live per-turn stream;
  `fire_activation` **fails loud** if a mode declares `reserve_r` below it **[OBS activation.py:176-180]**.
- The swarm sub-pool is **capped at `swarm_slots = max_num_seqs − R`** **[OBS cognition.py:443, 548-551]** —
  *"the swarm can hold at most swarm_slots gate permits, so R permits ALWAYS remain free for a concurrent
  main-stream/judge call to acquire immediately (it never queues behind the swarm)."*
- The whole thing runs under one **process-wide VRAM gate** (`global_vram_gate`) **[OBS cognition.py:453, 667]**.

**[INF]** A semantic sweep is just another `fire_activation`/`run_swarm` caller — it inherits the sacred
reserve automatically. A background coherence sweep **cannot** starve the live voice/chat reply, *by
construction*, because it runs in the capped swarm sub-pool while R permits stay free for the per-turn call.
The anchor's §6.4 is therefore **already a solved problem the moment the sweep is a swarm caller** — which
(§2.0) it is.

### 2.3 The swarm feeds the RHM — push-engine meets pull-face [OBS-anchor + IDEA]

Anchor §8: *the swarm's reading feeds the RHM, so the right-hand-man's answers are grounded in a fresh
whole-repo semantic read.* The structural sibling already found the hook: `up_translate('finding', …)` is
**coded and waiting at `suite.py:5828`** (per the structural COHERENCE-SUBSTRATE §1.3, *"the shape G2 will
feed — NOT wired here, that's a later lane"*). The semantic addition **[IDEA]**:

- §1.3 above named the prior-art split: semantic *search* (Cody/Greptile) is **pull** (you ask, it answers);
  the coherence swarm is **push** (it watches and holds). **The RHM is where they compose:** when Tim asks the
  RHM about any element, the answer should be grounded in (a) the structural registry [OBS exists] **and** (b)
  **the latest semantic finding-set for that address** — the swarm's held reading is the RHM's warm
  semantic index. The swarm keeps the index fresh (push); the RHM serves it at Tim's altitude (pull).
- This also realizes the anchor §4② "auto-explain every finding at Tim's altitude" — pre-generate the
  plain-language explanation **in bulk** during the sweep (cheap, prefill-dominated), so the coherence view
  opens fully populated with no per-click big-model latency. The swarm doing `up_translate` in bulk ahead of
  time is the same engine doing one more role.

### 2.4 Semantic finding-types as declared roles — `roles/check.py` is the literal template [OBS]

Anchor §8: *a semantic finding-type is a declared role + a schema + a prompt — a file, not code.* The
structural sibling argued finding-types should be a self-registering registry like roles/rules. For the
**semantic** layer this is even more direct — **a semantic finding-type is already shaped exactly like an
existing role file** **[OBS roles/check.py]**:

```
ROLE = {
  "id": "...",                       # the finding-kind
  "prompt_template": "...",          # what to judge (read X against Y, flag contradiction)
  "output_schema": SomeOut,          # pydantic → schema-enforced finding JSON (transport.py:47-48)
  "input_addresses": (...),          # what it reads (for semantic: a module + its AGENTS.md)
  "rules": [...],                    # what routes the finding (candidate-only: surface, never resolve)
  "render_hint": {...},              # how it shows in the view
}
```

Adding "check that every mode has a consistent name across the repo" = **dropping a `roles/concept_coherence.py`
file** that the `RoleRegistry.discover` **already picks up** **[OBS roles.py:70-73]** (the structural sibling
cited this). The detector is the only "code," and it's a *prompt + a schema*, not a function. **The three
structural gates become the first rows; the semantic detectors are new role-files in the same registry** —
"more types, not more tools," applied to semantic integrity, with the role file as the unit. This is the
cleanest grounding in the whole companion: the thing the anchor *imagines* declaring already has a working
file-shaped precedent the engine discovers.

### 2.5 The introspective-data law, pointed at semantic integrity [OBS → INF]

The structural sibling tied Coherence to the introspective-data law via the `rollup` context. The semantic
layer **closes the loop more tightly [INF]**: a semantic sweep is an *operation that self-instruments* — each
`run_swarm` wave already emits a batched `cognition.wave` telemetry record **[OBS cognition.py:600-611
referenced; consolidate_rollup reads `cognition.wave`, activation.py:271]**, and `consolidate_rollup` already
aggregates those run-records into a distribution **[OBS activation.py:247-323]**. So the full law-cycle
*operation → run-records → substrate → rollups → knowledge* is **already wired for the swarm** — a semantic
coherence sweep inherits it for free: the findings are the run-records (re-derivable telemetry), the
dispositions are the kept knowledge (the structural sibling's owned ADRs), and the burn-down is a read-time
rollup over them. **The own/reflect split holds *a fortiori* for semantic detection**: structural detection's
"re-derivable" needed an argument (re-run the AST); semantic detection's is self-evident — *re-running the
swarm is literally re-reading the meaning.* Nothing about a finding's detection is worth keeping; only the
disposition is.

### 2.6 The recursion — semantic checks on the semantic checks [OBS + IDEA]

Anchor §8: *the semantic layer checks the coherence of the semantic checks (do the role prompts still match
what they're supposed to detect?).* This is grounded twice over:

- **The drift-home pattern already does the structural half** **[OBS]**: `RULE_OPS`/`DESTINATION_KINDS` must
  stay reflected in `runtime/AGENTS.md`, asserted by `tests/rules_acceptance.py` **[OBS rules.py:43-46]**;
  the same guards `ACTIVATION_CONTEXTS` **[OBS activation.py:36-38]**. The system *already* checks that the
  declarations describing its mechanisms stay true.
- **The semantic recursion [IDEA]:** a *semantic* meta-detector reads each detector role's `prompt_template`
  against its stated `description`/`trigger` and judges "does this prompt still detect what it claims?" — the
  exact recursion, expressible as **one more role file** (§2.4). It reads role files the way other roles read
  modules. **Termination is the same self-exclusion the structural round found** [OBS the structural meta-gates
  self-exclude — COHERENCE-SUBSTRATE §6/AREA-6 §2.5]: the meta-detector excludes itself from its own scan, so
  "the swarm watching the coherence of the swarm's detectors" terminates rather than spiraling. The recursion
  isn't a hazard — it's just another role under the one self-exclusion rule.

### 2.7 `company onboard` — the institutional-memory faculty, with the corrected economics [OBS-anchor + INF]

Anchor §8's keystone what-if: a new session starts every run by regenerating a true orientation map, so no
session starts blind or drifts. The structural round established *why this matters in this very build*
(main drifted under the lead; the mode dial built twice — COHERENCE-SUBSTRATE §3.5 **[OBS]**). The semantic
contribution **[INF]**: with the corrected economics (§ pre-flight), a fresh whole-first-party-corpus semantic
read (~234 files, prefill-dominated, 32-wide) is genuinely a **small-minutes, on-demand CLI faculty** — cheap
enough to run *at the start of every Claude Code session* without a standing daemon (so it sidesteps the
needs-tim driver question of §2.1 entirely). `company onboard` is the on-demand face of the same swarm; the
continuous background watch (§2.1) is the always-on face Tim must separately authorize. Same engine, two
faces — exactly the project's established `up`/on-demand pattern.

---

## Summary — the expansion-ratio-greater-than-one residue (what I'd put in front of Tim)

1. **The frame, stronger than the structural round's (§2.0):** for the *semantic* layer the detector **IS
   `run_swarm`** — not a sibling of the swarm, the swarm itself, with the utterance = a repo artifact and the
   role-set = semantic detectors. `roles/check.py` is the live template (`{contradicts, note}` is already a
   coherence judgment). The answer to "another lens on the one swarm engine?" is **yes, literally, the same
   engine.** **[OBS → IDEA]**
2. **The numbers, corrected, still supporting "free in seconds" (pre-flight §):** not 3,000 tok/s but **2,241
   @ 32, plateau at 32, ~100 tok/s decode** — but *reading is prefill* (30K tokens in ~1.07s, sublinear) and
   *findings are tiny decodes*, so the cost lives on the cheap axis. And the corpus is **~234 first-party py
   files / 48K LOC**, not 14,825 / 5.4M. The spirit survives; the figures are honest now. **[OBS]**
3. **The sharpest correction to the anchor (§1.1):** anchor §6.1 named its trust mechanism *"multi-role
   agreement (`run_jury` — N roles must concur)"* — **but `run_jury` is N *draws* of the SAME role
   [OBS cognition.py:645], and its own docstring calls those draws CORRELATED — a stability check, not a
   correctness check.** A true multi-*role* jury (less correlated, partial correctness) is buildable but
   doesn't exist yet, and is still single-model. The real trust backstop is the **candidate-only floor + a
   stronger second model** (the `verify_jury` docstring already reserves the cloud-tiebreak slot; the loop's
   Claude Code agent *is* that model). A single-4B "looks fine" must never clear a finding. **[OBS → IDEA]**
4. **Prior-art deltas (Thread 1):** LLM-as-judge but *typed binary judgment + candidate-only, not scoring*
   (§1.1); doc-drift detection but *module-vs-AGENTS.md intent at corpus scale, held* (§1.2); semantic search
   but *proactive watch, not reactive query, local-first* (§1.3); GraphRAG but *meaning-graph for incoherence-
   detection, and the structural∧semantic disagreement is the novel finding-type* (§1.4); and **cheap-small-
   model bulk swarms are a thin/unoccupied external point — the thinness validates anchor §2's "capability
   that changes the economics."** (§1.5) **[PRIOR-ART → IDEA]**
5. **The §8 what-ifs are mostly already-built mechanism, not speculation:** continuous watch = the
   `background`/`rollup` contexts, **ready-but-driver-gated** needs-tim (§2.1); VRAM contention = **solved by
   `FLOOR_RESERVE_R` + `swarm_slots` by construction** (§2.2); finding-type = **a role file the registry
   already discovers** (§2.4); the introspective-data cycle is **already wired for the swarm** and own/reflect
   holds *a fortiori* for meaning (§2.5); the recursion terminates via the **existing self-exclusion rule**
   (§2.6); `company onboard` is the **on-demand face** the corrected economics make a per-session faculty
   (§2.7). **[OBS + INF]**
6. **The composition that is no one else's (the seam between the two rounds):** structural = the trustworthy
   auto-actable skeleton; semantic = the candidate-only flesh; **and structural-says-wired ∧ semantic-says-
   meaningless is a finding-type neither round catches alone** — the anchor §8 disagreement what-if, which is
   the literal join of the two graphs and the highest-value thing in the whole design. **[IDEA]**
