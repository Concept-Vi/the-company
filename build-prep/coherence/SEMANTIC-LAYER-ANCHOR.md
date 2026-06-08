# The Semantic Layer — an anchor exploration (the 4B-swarm half of the Coherence Substrate)

> **How to read this.** Same as the coherence round: this is NOT a plan or a spec — it is the *shape of an
> idea* caught early, in its "what if…?" tone, to be the **shared anchor** for a wave of research agents.
> Everyone reads THIS first so we hold the same partial picture, then each agent explores one allocated
> area across everything available and writes a companion file beside this one. We are NOT confirming this
> doc — stress-test it, contradict it, ground it in what actually exists. Expansion ratio > 1: leave the
> idea bigger and more real than you found it. The "yes, but actually…" is the gold.
>
> **Required context.** Read `build-prep/coherence/COHERENCE-SUBSTRATE.md` first — this idea is the
> *semantic detector layer* of that substrate. That document established: a live, typed, addressed,
> dispositioned model of the system's own connectedness, fed by detectors, read by a Claude Code agent as
> its worklist, burned down toward zero. Its detectors so far are all **structural** (AST / registry /
> string / call-graph) — they see *wiring*. This anchor is about the other half.
>
> **The no-humans rule still holds.** No developer fills gaps, no human review holds the picture together
> across sessions. That is the whole reason any of this matters. Keep it in mind as you research.

---

## 1 · The gap this fills (and why structural detection alone is not enough)

The coherence substrate's detectors, today and in the near plan, are **structural**: they parse the AST,
read the registry, match route strings, trace the call-graph. They are exact, cheap, deterministic — and
**blind to meaning**. The detection-rigor research (`findings/AREA-3-detection-rigor.md`) proved this is a
hard ceiling, not a temporary limitation: the genuinely dangerous coherence failures are **not connectivity
properties** and static analysis *structurally cannot see them*:

- **half-migration** — mechanism X half-replaced by Y, with a dropped lifecycle (the `/api/mockup-feedback`
  `/status` incident: the feedback store moved to annotations but the pending→applied→dismissed lifecycle
  was silently lost). The research's verdict: "not a connectivity property… cannot prove a dropped lifecycle
  without a schema/semantic diff." A graph flags the *candidate*; it cannot adjudicate the *meaning*.
- **suite-covers-capability** — does any test actually *exercise* this capability? "No clean machine signal…
  not a spec-able detector" (Area 2 Tier-3). There is no structural edge from a test to the meaning of what
  it covers.
- **intent-vs-implementation drift** — does the code still do what its docstring / `AGENTS.md` / design doc
  *claims*? The structural drift check only asks "is the suite *listed* in STATE." It cannot ask "is the
  *prose still true*." And the prose is the institutional memory — so when meaning drifts while wiring holds,
  the self-description goes quietly false and **nothing watches**.
- **concept / vocabulary coherence** — the same concept wearing divergent names across sessions (the
  *literal* "mode dial built twice" incident — two sessions independently built two halves of one mode
  declaration). Structural analysis sees two valid symbols; it cannot see they are *the same idea built
  twice*.

So there is a whole class of incoherence — the *semantic* class — that the structural substrate is
constitutionally unable to detect. In a human team, a person catches these (code review, "wait, didn't we
already build that?", "the docs say X but the code does Y"). **In a no-humans build, nobody does.** That is
the gap.

## 2 · The capability that changes the economics (Tim's prompt)

There is a resident small model — a **4B** (the cognition stream runs its roles on it). Tim's figures, to
be verified by the research: it can run on the order of **~32 concurrent inferences at ~3000 tokens/second**
— effectively free, and fast enough that **the entire repo and all documentation could be read in seconds,
or at most a minute or two**. That is the unlock. A semantic check that would be absurd to run with a large
model on every file — "read this module and its docstring and judge whether they still agree" — becomes
*trivially affordable* when you can fan out 32 cheap concurrent judgments and re-run the whole corpus on
demand.

> **The big what-if:** *What if the coherence substrate has a second detector class — **semantic** detectors
> powered by a cheap, massively-concurrent 4B swarm — that reads the repo for **meaning, not wiring**, and
> finds the entire class of incoherence the structural detectors structurally cannot see? On demand in the
> CLI, whole-repo in seconds, essentially free.*

And the engine for it **already exists** — it is the cognition stream's swarm (`run_swarm`, the roles/rules,
the schema-enforced JSON output, the `run://` addressing). This is not net-new machinery; it is the cognition
swarm pointed at *the repo* instead of at *a chat turn*. Build-on-not-beside, cross-stream, again.

## 3 · The organizing insight — two detector classes, one model, one discipline

This is the spine to hold:

```
STRUCTURAL detectors  (built / near-plan)        SEMANTIC detectors  (this anchor)
  AST · registry · call-graph · string             a 4B swarm reading for MEANING
  sees WIRING                                       sees INTENT / CONCEPT / CONSISTENCY
  exact · deterministic · cheap                     fuzzy · probabilistic · cheap-at-scale
  trustworthy enough to AUTO-ACT                    CANDIDATE-ONLY — never auto-acted
        \                                          /
         \                                        /
          ──────▶  ONE coherence finding model  ◀──────
                   (typed · addressed · dispositioned)
                   read by a Claude Code agent as its worklist
```

The **discipline** is the load-bearing constraint, and it is already two of the project's laws:
- **Positive-only / candidate-only** (your patterned-visibility law: "semantic corroboration is positive-only
  signal; rare ≠ wrong"; and Area 3's demote-only rule). A semantic finding may **propose** ("this looks like
  a half-migration") but never **declare** ("this IS dead"). A 4B "looks fine" proves nothing; a 4B "looks
  wrong" is a candidate for a stronger judge to confirm. **No semantic finding auto-acts.** It feeds the
  model as a candidate; the big model (a Claude Code agent) or Tim confirms the consequential ones.
- **Own/reflect** (from the coherence round): the *detection* (the meaning-graph) is re-derivable — re-run
  the swarm, get the reading again — so it is reflected, never owned, never maintained. Only the *disposition*
  (a human/agent's confirmation or "by-design") is owned. So you can re-read the whole repo's meaning every
  time, cheaply, and keep only the decisions.

This composition is the whole design: structural findings are the trustworthy skeleton; semantic findings are
the candidate flesh; one model holds both; nothing semantic acts without confirmation.

## 4 · What it could build in — my ideas (the generative core, held loosely)

Grouped. Each is a *what-if*, not a commitment. Research should ground feasibility, false-positive risk, and
the confirm-path for each.

### ① Semantic DETECTORS (find what static can't)
- **Half-migration detector.** A run reads the old mechanism + the new and judges "does the new carry the
  old's full lifecycle / behaviour?" Closes the bounded class the structural research couldn't. *(The
  `/status` incident is the test case: would a 4B reading both the JSONL feedback path and the annotation
  store have flagged the dropped status lifecycle? If yes, this is proven by the very bug that motivated it.)*
- **Intent-vs-implementation drift.** Read each module + its declared self-description (`AGENTS.md`,
  docstrings, the design doc that spawned it) and judge "does the implementation still match the claim?"
  Semantic drift, the complement to the structural drift check. The highest-value one, because it keeps the
  *self-understanding* honest — the institutional memory the whole no-humans premise rests on.
- **Concept / vocabulary coherence (the "built-twice" detector).** Cluster the repo by *concept*; flag where
  one concept wears divergent names, or one name spans divergent concepts. Would have caught the mode dial
  semantically, before the merge.
- **Documentation contradiction + staleness sweep.** Fan the swarm across all the markdown (hundreds of
  files) in seconds: docs describing things that no longer exist; two docs contradicting each other; a memory
  note naming a deleted file or a renamed symbol.
- **Semantic coverage mapping.** A run per (suite, capability) judges "does this suite actually exercise this
  capability?" 32-concurrent × cheap = the whole coverage matrix in a minute. Cracks the Tier-3 the
  structural research called "not spec-able."

### ② Semantic ENRICHMENT (make the model legible + actionable, instantly, in bulk)
- **Auto-explain every finding at Tim's altitude.** Pre-generate the plain-language "what is this gap, what
  would finishing it mean, what depends on it" for *every* finding at once — so the coherence view opens fully
  populated, no per-click latency, no big-model cost. (The RHM `up_translate('finding')` organ is the shape;
  the swarm does it in bulk ahead of time.)
- **Candidate disposition + reason for every finding.** The swarm proposes, for *all* findings, "this looks
  by-design (internal entry point)" / "this looks like a real to-wire (an FE caller is missing)" with a
  reason. Candidate-only — Tim/the lead confirms the consequential ones. Burns down the dispositioning labour
  that otherwise falls on the human.
- **Cross-session semantic dedup.** Two sessions wording "the same gap" differently → clustered into one
  finding, so the model doesn't double-count drift.

### ③ Whole-corpus ON-DEMAND faculties (new CLI verbs — the "free in seconds" payoff)
- **`company onboard` — regenerate true institutional memory on demand.** The swarm reads everything and
  produces a *fresh, true* orientation map for a starting Claude Code session — directly fixing the
  drift-under-me problem (a new session starts oriented, not blind, not re-discovering by grep). This is the
  institutional-memory-as-substrate idea made into a faculty.
- **Repo-wide semantic QA.** "Where does X actually happen / what would break if I change Y / where is the
  consent floor enforced" — answered from the whole corpus in seconds.
- **Pre-commit semantic review.** Before a commit lands, a run judges "does this diff match its stated intent,
  does it touch things it shouldn't, does it violate any `AGENTS.md` law?" A cheap semantic reviewer *in front
  of* the structural gates. (Note the relationship to the wire's existing adversarial critic — this is the
  bulk/semantic complement.)

## 5 · Why it belongs in THIS system (what's already built to support it)

The bet — as with the coherence substrate — is that this is mostly *naming and pointing existing machinery
at a new target*, not building beside it. The pieces an agent must understand:

- **The cognition swarm engine.** `runtime/cognition.py` (`run_swarm`, `SlotBudget` from `services.json` +
  `gpu.py`, `run_role`/`run_jury`, `resolve_run_ref`), `runtime/roles.py` + `roles/*` (the file-discovered
  role registry), `runtime/rules.py` (the declared-AST rule engine — a closed grammar, never eval/exec),
  `runtime/activation.py` (per-turn / background / rollup contexts), `contracts/cognition_info.py` (the
  projection). *This is the swarm. Pointing it at "read a repo artifact → emit a schema-enforced structured
  judgment" instead of at a chat turn is the core move.*
- **Schema-enforced JSON output.** The `json_schema` decode branch in `fabric/transport.py` — the swarm
  already emits *structured, schema-validated* output, not free text. So a semantic finding can be a typed
  record by construction (it doesn't need parsing out of prose). This is huge for trust: the 4B is constrained
  to a finding *schema*, not asked to write an essay.
- **The resident 4B + the resource manager.** `ops/cli/` (`gpu.py` the VRAM resource manager, `services.json`
  the model registry, `models.py`, `bench.py`), and the benchmark sheet (`~/vllm-tests/`) — the real
  measured throughput / concurrency / VRAM the "32 concurrent / 3000 tok/s" claim must be checked against.
- **The coherence substrate** it feeds — the finding model, the own/reflect split, the Claude-Code-agent loop,
  the `company coherence` CLI face (the structural round's artefact + companions).
- **The CLI / single-console pattern** (`ops/cli/app.py`) — where a `company onboard` / `company coherence
  scan --semantic` verb slots in, exactly like `company suites`.
- **The introspective-data-building law** — operation self-instruments → run-records → substrate → rollups →
  knowledge. A semantic detection run is another instrumented operation; the cognition stream already runs
  this exact cycle (`cognition.wave` rollups). Semantic coherence is the same cycle with *meaning* as the
  instrumented thing.

## 6 · The hard parts (where this is fragile — research these hardest)

The semantic analog of "detection rigor was the make-or-break." Be skeptical here:

1. **Can you trust a 4B judgment enough to act on — even as a candidate?** A 4B half-understands code; it will
   hallucinate, miss context, over-flag. The whole value collapses if the semantic findings are noise that
   trains Tim to ignore them (the cry-wolf failure). **How is a semantic finding verified?** Options to
   research: multi-role agreement (the cognition stream's `run_jury` — N roles must concur); the determinism
   property (identical inputs → identical judgment); a stronger model (a Claude Code agent) confirms before it
   reaches Tim; calibration / confidence; the positive-only discipline as the backstop (never act, only
   propose). This is the make-or-break — if semantic findings can't clear a trust bar, the layer is a
   curiosity, not a tool.
2. **Context windows vs whole-repo.** A 4B has a bounded context. "Read the whole repo" really means many
   bounded reads + a composition. What's the right unit (a file? a symbol? a module + its self-description)?
   How do cross-file judgments (half-migration spans two mechanisms; concept-coherence spans the whole repo)
   work when no single run sees everything? This is a real architecture question, not a detail.
3. **Positive-only is a strong constraint — is it enough, and is it honored?** A semantic finding must never
   auto-act. But the loop *wants* to burn down. How do semantic candidates get promoted to actionable without
   a human per-item — does a stronger model confirm, and is *that* trustworthy? Where exactly is the line
   between "the swarm proposes" and "something acts"?
4. **Cost / cadence / VRAM contention.** The 4B is also the cognition stream's resident model. Running a
   whole-repo semantic sweep contends for the same VRAM the live cognition + chat use. When does a sweep run
   (on-demand only? a tick? pre-commit?), and how does it coexist with the resource manager's budget without
   evicting the things in use? "Free" is only free if it doesn't starve the live system.
5. **The 4B's real ceiling on code.** The throughput claim may be real; the *quality* on genuine code
   reasoning is the question. What can a 4B actually judge reliably (consistency, naming, doc-match — likely
   yes) vs not (deep logic, subtle dataflow — likely no)? The honest tiering of *which semantic checks a 4B is
   good enough for* is as important as the structural Tier-1/2/3 split was.
6. **Determinism / reproducibility.** The coherence model's trust rested partly on "identical code → identical
   findings." A sampling LLM is not deterministic by default. Can the swarm be made reproducible enough
   (temperature 0, schema-constrained, jury-voted) that a semantic finding is stable across runs, not a
   flickering ghost?

## 7 · What I can already see (anchors in the real code, to verify + extend)

- The cognition swarm is real and substantial — `run_swarm` fans rule-routed roles on the resident 4B, each
  emitting schema-enforced JSON to `run://<turn>/<role>`; this is the exact "fan out cheap structured
  judgments" engine the semantic layer needs.
- `fabric/transport.py` has the `json_schema` branch — structured output is already a solved primitive.
- The resource manager (`ops/cli/gpu.py`, `services.json`, `company up/down/swap`) governs the 4B's VRAM —
  the contention question (§6.4) lives here.
- The coherence substrate's finding model + `company coherence` face is the consumer (the structural round).
- The benchmark sheet (`~/vllm-tests/BENCHMARK_FACTSHEET.md` per the project memory) is where the real
  throughput/concurrency numbers live — verify the "32 concurrent / 3000 tok/s" against it.
- The cognition stream's `run_jury` + determinism (C0.2) are the candidate trust mechanisms for §6.1.

## 8 · Open what-ifs (pull on these freely)

- What if the semantic layer is not just on-demand but a **continuous background watch** — the cognition
  stream's `background`/`rollup` activation contexts already exist; a low-priority swarm could keep the
  meaning-graph warm so semantic drift is caught as it happens, not only when someone runs a scan?
- What if **finding-types are declared** (the structural round's idea) and a *semantic* finding-type is just a
  declared role + a schema + a prompt — so adding "check that every mode has a consistent name across the
  repo" is a file, not code? (More types, not more tools — for semantic checks too.)
- What if the swarm's reading **feeds the RHM** — so when Tim asks the right-hand-man about any element, the
  answer is grounded in a fresh whole-repo semantic read, not just the structural registry?
- What if the **recursion applies**: the semantic layer checks the coherence of the semantic checks (do the
  role prompts still match what they're supposed to detect)?
- What if this is the thing that finally makes **`company onboard` real** — a new Claude Code session (or the
  in-app `claude -p` loop) starts every run by regenerating a true map, so no session ever starts blind or
  drifts from what other sessions did? The institutional-memory-that-replaces-the-developer, generated fresh
  in seconds each time.
- What if the structural and semantic findings **disagree** — structural says "wired," semantic says "this is
  dead code that's only referenced by an obsolete test" — and the *disagreement itself* is the highest-value
  finding (the thing neither class catches alone)?

---

## For the research agents — the spirit of this

You've read the shape, and the coherence substrate it extends. Go to your allocated area and explore it
**across everything available** — the real cognition-swarm code, the resource manager + benchmarks, the
coherence substrate, external prior art, your own reasoning. You were given an *area*, not a list of findings,
on purpose: bring what's actually there, contradict this doc where it's naive, prove the hard parts harder
than it admits. Verify the capability claims against real numbers. Write a **full** companion (your area was
sized to have real content; cover it). Anchor to evidence (`file:line`, real measured numbers) and mark
**observed / inferred / external-prior-art / your-idea** clearly. Write it beside this anchor so the outputs
of this round — together with the coherence-substrate round — become the basis to build something really
useful.

Leave the idea bigger and more real than you found it.
