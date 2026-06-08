# The Corpus-Chain Primitive — an anchor exploration (the map-reduce substrate under the other two rounds)

> **How to read this.** Same process as the coherence + semantic-layer rounds: this is NOT a plan or spec —
> it is the *shape of an idea* in "what if" tone, the **shared anchor** for a research wave. Read it first;
> everyone holds the same partial picture, then each agent explores one allocated area across everything
> available and writes a companion beside this file. Do NOT confirm it — stress-test, contradict, ground it
> in real code + real numbers. Expansion ratio > 1: leave the idea bigger and more real. The "yes, but
> actually…" is the gold.
>
> **Required context (read these — this idea is the substrate UNDER them):**
> - `build-prep/coherence/COHERENCE-SUBSTRATE.md` — the structural coherence round.
> - `build-prep/coherence/SEMANTIC-LAYER.md` — the 4B-swarm semantic round.
> - `~/.claude/skills/research-wave/SKILL.md` — the manual methodology this would *productize*.
>
> **The recursive twist:** this round is the research-wave process applied to *building the research-wave
> (and its underlying primitive) as a real tool.* The thing we're researching is the thing we're using.
>
> **The no-humans rule still holds.** No developer fills gaps, no human review holds the picture together
> across sessions. That is why any of this matters.

---

## 0 · The headline (read first)

Three things this project keeps reaching for are **the same primitive wearing different clothes**, and we've
been treating them as separate builds:
- the **research-wave** (this round's process: anchor → fan out area-agents → synthesize) — a manual skill today;
- the **semantic coherence layer** (round 2: a 4B swarm reads the repo → structured findings → a smart layer adjudicates);
- the **`onboard` / repo-map / repo-QA faculties** (round 2 §CLI: read the whole corpus → a true map / an answer).

All three are: **take a corpus → process every unit cheaply and in parallel into structured outputs → reason
across those structured outputs with a strong model → produce a grounded, tagged result.** That is one
primitive — call it a **corpus-chain** (a map-reduce-over-a-corpus with an LLM at each stage). The big
what-if: *build that ONE primitive — declared, configurable, compilable from natural language — and the
research-wave, the coherence scan, the onboarder, and ad-hoc repo queries are all just **configs** of it, not
separate tools.* "More types, not more tools," at the orchestration layer.

And it resolves the tension the semantic round raised (a cheap model can't do deep reasoning): **the cheap
layer never gets the reasoning task.** It gets a *contained* unit + a schema + thinking-on, and emits
structured output. The depth lives in the strong *reduce* layer, which only ever reads the small structured
digest, never the raw corpus. Expensive intelligence applied only to compressed, complete, structured inputs.

---

## 1 · The problem it fills

Right now: the research-wave is a manual skill I execute by hand (I carve the areas, I dispatch, I
synthesize). The coherence semantic layer is a designed-but-unbuilt detector class. The onboarder is a
proposed CLI verb. Each is being designed/built *separately*, and **none is easy for an agent to just
*use*** — they all require hand-construction (carve areas, write per-unit prompts, write the reduce). In a
no-humans build, a faculty that's hard to invoke doesn't get invoked. The gap: there is no **single,
low-friction, composable primitive** that any agent (or Tim) can point at a directory with a freeform intent
and get back full-coverage, structured, grounded understanding — fast, cheap, and trustworthy.

## 2 · The insight — the corpus-chain, a three-stage pipeline

```
COMPILE (smart)   freeform intent  →  a declared, INSPECTABLE chain config
   ↓ (surface the plan — cheap to check, expensive to run; approve, then go)
MAP (cheap, ‖)    per-unit structured extraction over the selected units — FULL coverage, tagged, thinking-on
   ↓ (the structured digest — a reusable warm substrate)
REDUCE (smart)    join across units → adjudicate/verify → compose → tagged output
   ↺ decide-next: needs a pairing pass? a drill-down? a followup? → loop back to a targeted MAP
```

- **MAP** is the cheap parallel layer. Each worker gets a *contained* input — the instruction/schema + **one
  unit** (one file, even) — and emits **schema-enforced structured output**, thinking on. Concurrent, seconds,
  *guaranteed per-unit attention* (every file gets its own focused pass — see §coverage-certainty). The
  worker never sees "the main goal" or does cross-unit reasoning; it does bounded extraction, its proven
  strong mode (SEM-3).
- **REDUCE** is the strong layer. It reads the *structured digest* (not the raw corpus) and does the four
  jobs the map can't: **join** (cross-unit reasoning — pairs, clusters, cross-refs), **adjudicate/verify**
  (the correctness gate — catch a bad extraction, re-query; the SEM-3 stronger-model-confirm lives here),
  **compose** (produce the answer), and **decide-next** (conclude it needs another targeted map pass — the
  conditional loop that makes it a *query engine* not a one-shot).
- **COMPILE** is the on-ramp (Tim's addition): a smart run that turns freeform intent into the structured
  chain config (the map schema, the per-unit prompt, the unit selector, the reduce prompt, the passes) — so
  you express *what you want to know*, not *how to run a swarm*. The compiled plan is inspectable/approvable
  before the map spends. This is the path-of-least-resistance law: make the correct use the *easiest* use.

## 3 · The declared chain — the thing that makes it all compose

The load-bearing structural idea: **the chain itself is a declared, typed object.**
```
Chain = { unit_selector,        # which units (a dir glob, a file list, a registry slice)
          map_schema,           # the structured output shape per unit (json_schema-enforced)
          map_prompt,           # the contained per-unit instruction
          passes,               # single-map | map→pair→map | map→reduce→drill (the multi-pass plan)
          reduce_prompt,        # how the strong layer joins/composes
          worker_model,         # the MAP tier (configurable — §4)
          synth_model }         # the REDUCE/COMPILE tier (configurable — §4)
```
Then everything composes:
- the **compiler** is a smart model that emits a *valid instance* of this schema;
- the **runner** executes *any* valid instance — it doesn't care if the config was compiled or hand-written or saved;
- **common purposes are *saved* chains** (named declared configs you re-run); **novel queries *compile* fresh.**
  The compiler is the on-ramp; saved chains are the library.

**The faces, as saved chains (this is the "everywhere it connects"):**
```
research-wave    = map(per-area deep-read) → reduce(write companions + synthesize)   [workers must be STRONG — §4]
coherence-scan   = map(per-file structured findings) → reduce(adjudicate + the wired∧meaningless join)
onboard / map    = map(per-file digest) → reduce(write the true orientation)
repo-QA          = compile(question) → map(per-unit answer) → reduce(compose tagged conditional result)
doc-staleness    = map(per-doc check) → reduce(cluster + report)
```
So you don't build the research tool, the coherence layer, and the onboarder as three things — you build **one
corpus-chain primitive + a handful of declared chains.** That is the universal-composition move, at the
orchestration layer.

## 4 · The configurable model tiers + the cost shape

Both the worker (map) and the synth (compile/reduce) models are **configurable, read from the model
registry** (Tim's native-model-layer). The tiers:
```
WORKER (map)    local 4B swarm (~14 concurrent, cheapest)  ·  Ollama Cloud (~6-10 concurrent, more capable)
                ·  Claude Code subagents / cloud Opus (strongest)
SYNTH (compile+reduce)   cloud Opus / a strong model (substitutes for me)
```
**The cost shape is the elegant part:** the smart model only ever touches *small things* — the freeform
intent (compile) and the structured digest (reduce). It **never reads the raw corpus.** The cheap parallel
layer does the only thing that touches every byte. So you get *full coverage* at cheap-layer cost, and
*correctness + reasoning* at smart-layer quality, but the smart layer's input is always small → fast, never
skims.

**The worker-tier rule (the tension the map-reduce split resolves):** match worker capability to *the
per-unit task*, not to the goal. Because the map task is *contained structured extraction*, even a 4B clears
it (SEM-3: contained input → structured judgment is its strong mode). The deep reasoning is in the reduce, so
the cheap workers are fine *for the map* even when the overall question is deep. The exception: the
research-wave *face* gives its workers genuinely deep per-area reasoning (write a grounded companion) — so
*that* face configures strong workers. The knob exists per chain; the guardrail is "does this chain's
per-unit task actually fit the worker tier."

## 5 · The coverage-certainty insight (why two stages beat one big call)

A single strong model with a huge context reading the whole directory *skims* — lost-in-the-middle, silent
under-reading. The map layer gives **guaranteed per-unit attention**: every unit gets its own focused pass,
nothing skipped, every output tagged to its source. So the "certain" in "tagged, structured, certain output"
is **certainty of coverage + provenance**, not "the cheap model is right per-unit." Correctness is the
reduce's job; *completeness* is the map's. That completeness is the thing neither a lone big call nor a lone
cheap model can give — and it's the core argument for the whole shape.

## 6 · Why it belongs here / what it builds on

- **It IS `run_swarm`, a third application.** Cognition turn (round 1's stream) · semantic coherence (round 2)
  · now corpus-query. Same engine: fan structured roles/workers over units → reduce. Files-as-units instead of
  roles-as-units. The `json_schema` transport (`fabric/transport.py`) already makes the map output a typed
  record by construction. `run_jury`'s 2nd-model slot is the reduce's adjudicate leg. The one net-new seam
  (from SEM-1): `run_role` hardcodes `ctx["utterance"]` → a unit-reading worker needs a generalized
  ctx→messages mapping.
- **It's the substrate UNDER the other two rounds.** The coherence semantic layer *is* a coherence-scan chain;
  the research-wave *is* a research chain. Building this primitive is building the thing that makes both real
  — so this round may reorder the others (build the primitive first, then the faces are configs).
- **The model registry** (native model layer) feeds the configurable tiers. **The CLI** (`company …`) is where
  `company research <dir>` / `company ask <dir> "<query>"` / `company onboard` slot in (the next verbs after
  `company suites`/`company coherence`). **The coherence substrate** consumes its output (a chain run is how
  you ground a thing before it becomes a finding-to-build). **Self-hosting:** a Company faculty that generates
  grounded understanding on demand — point it at any directory, get coverage — is the institutional-memory-
  that-replaces-the-developer, made a verb.

## 7 · The hard parts (research these hardest)

1. **Compiler reliability — the make-or-break.** Can a smart model reliably turn freeform intent into a
   *valid, runnable, law-abiding* chain config? This is the new load-bearing unknown (the generalization of
   "can a model auto-allocate research areas without violating the skill's laws — area-not-question,
   sized-by-content, include-the-skeptic"). What's the failure mode of a mis-compiled chain (wrong units,
   wrong schema, a per-unit prompt that isn't unit-local)? Is the inspect-approve gate enough? When must the
   human/strong-agent see the plan vs auto-run? This is this round's Area-3 — be skeptical.
2. **The contained-unit constraint.** The per-unit task must be answerable from the one unit, or the cheap
   worker guesses. Cross-unit questions (half-migration spans 2 files; built-twice spans the repo) aren't pure
   maps — they need the reduce to join, or a *pairing pass* (the structural layer surfaces the pair → a 2nd
   map judges it — SEM-2's chain). Which questions are unit-local vs need multi-pass?
3. **The reduce's staging threshold.** A 400-file digest may not fit one smart-model context → the reduce must
   be *hierarchical* (reduce clusters → reduce the summaries) or it re-introduces lost-in-the-middle at the
   top. Where's the threshold on the real corpus? How does the reduce stage itself without losing the
   cross-unit join?
4. **Followup cost.** A followup answerable from the warm digest = a cheap re-reduce; one needing un-extracted
   data = a targeted re-map. The engine must *know which* — itself a small smart judgment. How reliable is that?
5. **Trust carries from SEM-3.** The map is candidate-generation (high-recall, not adjudication); the reduce is
   the correctness gate; positive-only is the floor; deep-reasoning classes never clear at the cheap tier.
   Don't re-litigate — inherit it. But: does the *compile* stage introduce a new trust surface (a confidently
   mis-compiled chain that looks valid)?
6. **Determinism / reuse.** Saved chains are reusable; the digest is a warm cache (own/reflect: re-derive when
   the corpus changes). What's the cache-invalidation story? Is a chain run reproducible enough to trust a
   saved chain's output across runs?

## 8 · What I can already see (real anchors to verify + extend)

- `runtime/cognition.py` `run_swarm` / `run_role` / `run_jury` — the map+reduce engine, the 2nd-model slot.
- `fabric/transport.py` `json_schema` branch — structured map output, a typed record by construction.
- `runtime/roles.py` + `roles/*` (`roles/check.py` = `{contradicts, note}`) — the declared-worker template; a
  chain/finding-type as a declared file the registry discovers.
- `ops/cli/` (`app.py` the verb chain, `models.py`/`gpu.py`/`services.json` the model registry + resource mgr) —
  where the configurable tiers + the new verbs live.
- The two prior rounds' artefacts + their 12 companions — the faces this primitive underlies, and SEM-1's real
  numbers (~2,241 tok/s @ conc-32, ~14 concurrent on real files, suite.py needs a chunk tier) + SEM-3's trust
  ladder (carry these, don't redo them).

## 9 · Open what-ifs (pull freely)

- **Ingest once, query many:** the structured digest is a reusable substrate — one map pass feeds many reduces/
  followups. Is the digest a first-class cached artifact (a `vec://`/`cas://`-addressed thing), re-derived on
  corpus change?
- **The compiler IS a chain:** compiling intent → config is itself a smart read; could it use a cheap map over
  the dir first ("what areas/units exist") to inform the plan? (Auto-allocation as a mini corpus-chain — the
  recursion.)
- **Conditional/agentic queries:** because the reduce can decide-next, you get "complex conditional question →
  full-coverage map → compose → tagged answer, with followups over the warm digest." A semantic *query engine*
  over the repo, same primitive.
- **Continuous mode:** the cognition stream's `background`/`rollup` contexts exist — a low-priority chain could
  keep a digest warm so the coherence layer / onboarder is always current, not only on-demand.
- **The reduce feeds the RHM:** a fresh corpus-chain read grounds the right-hand-man's answers (the
  up_translate organ over a real whole-repo digest).
- **It reorders the roadmap:** if research-wave + coherence + onboard are all chains, the highest-leverage
  build is the *primitive*, and the three become declared configs — does building this first collapse three
  roadmap items into one?

---

## For the research agents — the spirit

You've read the shape and the two rounds it sits under. Go to your allocated area, explore across everything
available (the real `run_swarm`/transport/CLI code, the model registry + benchmarks, the two prior rounds'
artefacts, external prior art, your own reasoning). You were given an *area*, not a list of findings — bring
what's actually there, contradict the anchor where naive, prove the hard parts harder. Verify capability
claims against real numbers. Mark **Observed (file:line) / Inferred / External-prior-art / Your-idea**. Write
a **full** companion (sized for depth, no skim). Map *everywhere it connects and what needs building* — Tim
asked for that specifically. Write beside this anchor so this round joins the other two into the basis to
build something really useful. Leave the idea bigger and more real than you found it.
