# The Chain Designs — what the 4B-swarm actually extracts, and what runs on its outputs

> The concrete chains the coherence lane would build on the corpus-chain primitive, once the engine
> (run_items/run_reduce + the embed op) lands. Design captured now so we build toward it. The organizing
> law, the one Tim keeps pressing: **the 4B does bounded structured EXTRACTION, never judgment.** Each chain
> = (1) a MAP — 32-wide, one cheap call per file/unit, a fixed output SCHEMA, whole repo in ~seconds; then
> (2) a REDUCE — the judgment, run ON the structured outputs by EXACT code (trustworthy, can gate) or
> EMBEDDINGS (cluster/nearest-neighbour) or a STRONGER MODEL on only the few candidates the exact pass
> surfaced. The cheap layer touches every byte; the expensive judgment only ever touches small structured
> digests. All of these WRITE findings into the store (C1-C6), get calibrated by the harness (D), are
> dispositioned by the policy (C4), surfaced by `company coherence` — they are the SCALE-UP of the structural
> detector layer from "exact, one language, one shape" to "extract-anything, every file, every language, in
> seconds, judgment-in-the-reduce."

## The shape of every chain
```
MAP (4B · 32-wide · ~seconds)         REDUCE (the judgment — never the 4B's)
  one call per file/unit                EXACT (code over the structured facts) → trustworthy, can gate
  a FIXED extraction schema             EMBEDDINGS (cluster / nearest-neighbour) → candidate
  bounded: "extract X", not "judge X"   STRONGER MODEL (only the few candidates) → confirm, positive-only
  output = a structured fact-sheet      → writes FINDINGS into the store
```
The MAP output is a reusable **repo fact-base** (a digest — cached, `cas://`-addressable, re-derived when a
file's content-hash changes — own/reflect). Many reduces run over one map pass; a followup that needs no new
extraction is a cheap re-reduce over the warm digest, not a re-map.

---

## Category A — CONNECTION chains (reduce = exact graph-join over extracted refs)
*The 4B reads any language; the reduce is exact set-algebra. This dwarfs my AST detector — which is
Python-only and route-only — because the 4B extracts the same fact-shape from Python, TS, markdown, JSON, CSS.*

**A1 · The universal connection graph.**
- MAP per file → `{defines:[symbols], calls:[symbols], serves:[routes], consumes:[routes], emits:[events],
  listens:[events], reads_registry:[keys], writes_registry:[keys], imports:[modules]}`.
- REDUCE (exact): join `defines ↔ calls`, `serves ↔ consumes`, `emits ↔ listens` across all files → the real
  cross-language connection graph. Findings: **unwired-anything** (a capability/route/event/component
  defined-but-never-consumed), **dangling** (consumed-but-never-defined). The HTTP Python↔TS boundary (the
  one no off-the-shelf tool spans) is just a string-join on the route literal here.
- Trust: EXACT reduce → trustworthy, can gate. (The 4B's extraction is per-file bounded — its strong mode.)

**A2 · The address-reference graph.**
- MAP per file → `{addresses_defined:[ui://|code://|run://], addresses_referenced:[…]}`.
- REDUCE (exact): defined-but-unreferenced (orphan address) · referenced-but-undefined (dangling address).
- Feeds the address-registry coherence; the semantic complement to registry-vs-live.

## Category B — CLAIM chains (reduce = check extracted claims against extracted facts)
*The institutional-memory honesty layer — what the system SAYS about itself vs what's TRUE.*

**B1 · Doc-drift (semantic).**
- MAP: per doc/docstring/AGENTS.md → `{claims:[{subject, asserts}]}`; per source → `{actual:[capabilities]}`.
- REDUCE (exact then stronger-model): cross-check each claim's subject against the actual-capability facts;
  the exact pass flags mismatches; a stronger model adjudicates only those (few). Finding: **intent-drift**
  (the prose says X, the code does Y). The semantic complement to my structural drift gate ("is it listed").

**B2 · Self-description truth.**
- MAP: extract what MAP.md/STATE.md assert vs the live extracted reality. REDUCE: stale self-description
  beyond the structural "is it listed" — "is the description still TRUE."

## Category C — SHAPE chains (reduce = structured diff over extracted shapes)
*The half-migration class — the /status bug — that the research said connectivity can't catch.*

**C1 · Half-migration.**
- MAP per data-handling file → `{record_shapes:[{name, fields, lifecycle_states}], storage_mechanism}`.
- REDUCE (exact diff + stronger-model adjudicate): find two mechanisms handling "the same" record (by
  field-overlap) where the new one DROPPED a lifecycle the old one had (the /status pending→applied→dismissed
  drop). The exact diff finds the candidate pair; the stronger model adjudicates "is the drop a defect or
  intentional retirement." Exactly the bounded class SEM-3 said needs a schema diff — the MAP extracts the
  schema, the REDUCE diffs it.

**C2 · Producer↔consumer schema agreement.**
- MAP: `{schema each endpoint/node EMITS}` + `{schema each consumer EXPECTS}`. REDUCE (exact): mismatches →
  a contract-break finding (the surface calls the engine with the wrong shape — the semantic seam SEM-4 named).

## Category D — CONCEPT chains (reduce = embedding cluster over extracted concepts)
*The "built twice" class — the mode-dial incident. Uses the embed op (cognition's), which is why E5 needs it.*

**D1 · Built-twice / concept-coherence.**
- MAP per file → `{concepts:[{name, what_it_refers_to}]}`. REDUCE (EMBED + cluster): embed each concept's
  meaning, cluster; a cluster spanning divergent NAMES = one concept built twice (the mode dial); one NAME
  spanning divergent clusters = an overloaded term. Candidate-only (cluster proximity proposes; a stronger
  model confirms). **This is the chain that would have caught the mode-dial-built-twice before the merge.**

**D2 · Semantic duplication.** Embed every function/block; nearest-neighbour above a threshold → "these two
do the same thing, written twice" — the redundancy the structural graph can't see.

## Category E — COVERAGE chains (reduce = join test-touches against capability-provides)
**E1 · Semantic coverage** (cracks the Tier-3 "unsolvable").
- MAP: per test → `{exercises:[capabilities/behaviours]}`; per source → `{provides:[capabilities]}`.
- REDUCE (exact join): capabilities NO test exercises → a coverage-gap finding. The 4B extracts "what this
  test touches" (bounded); the join is exact.

## Category F — ENRICHMENT chains (the output IS the per-unit transform; reduce = assemble)
*Here the 4B's output isn't checked — it IS the product. Bulk transform, assembled.*

**F1 · `company onboard` — institutional memory in seconds.**
- MAP per file → `{one_line_purpose, kind, key_symbols, depends_on}`. REDUCE: assemble → a fresh, TRUE
  orientation map for a starting session. The fix for "main drifted under me" — a new session starts oriented,
  re-derived in seconds, never stale. The institutional-memory-that-replaces-the-developer, as a verb.

**F2 · Auto-explain every finding (bulk).**
- MAP per open finding → a plain-language, at-altitude "what this gap is, what finishing it means, what
  depends on it." REDUCE: attach to the burn-down → `company coherence` / the coherence view opens fully
  explained, no per-click latency, no big-model cost. (The RHM `up_translate('finding')` hook, pre-filled in
  bulk.)

**F3 · Candidate-disposition (bulk).**
- MAP per open finding → propose `{disposition, reason}`. REDUCE: surface as candidates (positive-only — the
  operator confirms the consequential ones via C4's escalation). Burns down the dispositioning labour the
  human would otherwise carry one-by-one.

## Category G — MULTI-PASS / recursive chains (the reduce decides the next map)
**G1 · Claim → symbol → exists.** MAP1 extract claims; the reduce picks the referenced symbols; MAP2 extract
where each symbol is defined; REDUCE check existence. The conditional loop — the reduce decides the next map.

**G2 · The compiler chain (recursive).** A cheap MAP over the dir ("what units/areas exist, what kind") informs
the NL→chain-config compiler — so the plan is grounded in a real scan, not guessed. Auto-allocation as a
mini-chain (the corpus-chain compiling itself).

---

## The trust spine (carried from SEM-3, applied per reduce-type)
- **Exact reduces** (A, C-diff, E-join) — code over the structured facts → **trustworthy, can gate** (the
  4B's bounded extraction is its strong mode; the join is deterministic).
- **Embedding reduces** (D) — cluster/NN → **candidate-only**, a stronger model confirms.
- **Stronger-model reduces** (B, C-adjudicate) — only the FEW candidates the exact pass flagged reach the
  stronger model → cheap + the only systematic-error gate. Never the 4B judging itself; never a same-model
  jury (variance≠error).
- **Calibrated** (D harness): each chain ships to the panel only if its measured precision-after-confirm
  clears the threshold on the captured-incident fixtures. The number moves if a chain regresses.

## Why this is the scale-up, not a parallel system
Every chain writes `append_finding` into the store I built; gets a disposition via `dispose_finding`; is
measured by `calibrate`; is declared + saved as an `Action` (build_action); is surfaced by `company
coherence` / `build_coherence_info`. The structural AST detectors (built, exact, one-language) and these
4B-extraction chains (universal, every file, judgment-in-the-reduce) are **two sources into one model** — the
structural∧semantic disagreement (wired-but-meaningless) is still the prize. The 4B doesn't replace the exact
detectors; it extends coverage to every language, every shape, every file, in seconds — with the judgment
always in the reduce, never in the cheap model.

## Build order when the engine lands
1. **A1 the universal connection graph** — highest leverage (subsumes + universalises reachability/
   capability-no-consumer across all languages), exact reduce, immediately trustworthy + gateable.
2. **F1 onboard + F2 auto-explain** — pure-transform, no judgment risk, immediate daily value (orient a
   session; populate the view).
3. **C1 half-migration + B1 doc-drift** — the bounded semantic classes, exact-flag + stronger-model-adjudicate.
4. **D1 built-twice** — needs the embed op; the mode-dial-class detector.
5. **E1 coverage + G the multi-pass/compiler** — last; the harder reduces.
Each is a saved Action, calibrated before it gates, dispositioned in the store, surfaced in `company coherence`.
