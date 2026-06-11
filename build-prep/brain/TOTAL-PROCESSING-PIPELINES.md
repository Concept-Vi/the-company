# Total-Processing Pipelines — knowing without questions

**What this document is:** the full statement of the mechanism class that resolves the Company's
deepest constraint — that NOBODY (Tim, any lead, any agent) can know what the system contains, and
no question-based mechanism can fix that. Written 2026-06-11 from a live design conversation with
Tim; expanded for COLD READERS: other sessions/agents are pointed here to READ and discuss, not to
act. Companion files: `embedding-research-2026-06.md` (the model research with URLs) ·
`UNCONVENTIONAL-EMBEDDING-USES.md` (the wider ideas round) · `CONTEXT-FORAGER-RIFF.md` (Tim's
search-canvas vision + his binding corrections of v1).

---

## 1 · The constraints, as axioms (Tim's words)

These are not problems to fix; they are the ground truth everything must be designed against:

- **"The only assumption that can be relied on is that no assumptions can be relied on."**
- The estate was built by MANY sessions, none sharing context or memory. "All of them believed they
  were doing the right thing, so everything is written as if that is the case — but it is impossible
  for that to be the case."
- The conflicts are not merely unresolved — they are **unenumerated**. No record of them exists.
- No human reads, writes, or reviews anything. Tim: "I am not a developer... I can never provide
  specifications for things that can be used to compare against. Even this message — this is how I
  talk." He also cannot verify or answer specific questions: "I will never be able to know or verify
  or answer any specific questions."
- Reading everything is impossible for any single context; even fleets of readers cannot reach 100%,
  and what they read is inconsistent anyway.
- **Question-based mechanisms are structurally disqualified for this class**: "if you don't ask the
  right questions then you can't identify things that you didn't already know or think to ask."
  (Targeted reads stay VALID as tools — they just cannot resolve THIS.)
- All building is **parallel multi-agent**; no agent maintains one context through anything. Sessions
  end, compact, and die mid-thought. The substrate is the only continuity.
- There is no spec, no accurate plan document, and there never will be. "The code base will be spread
  and messy and chaotic, because there was never a specification or a plan — it is just accumulated,
  building on what was there before, and at no point was what was before 'correct'."

**Tim's test case (apply it to every idea):** other sessions are building UI principles. Their work
must merge into this repo. Doing that "needs the full exact inventory of every feature and every
place a UI might connect to and exactly how." Nobody can produce that inventory — not from memory,
not by reading, not by asking. Any mechanism that cannot produce it MECHANICALLY fails the test.

## 2 · The core mechanical insight

**Questions are selective reads. Embeddings plus cheap local models make TOTAL reads affordable.**

A question reads a slice of the estate chosen by what the asker already suspects. Total processing
reads EVERYTHING, unconditionally, and transforms it — so what nobody suspected shows up anyway,
either as structure (clusters, joins) or as RESIDUE (the things that matched nothing). The
unknown-unknowns are not answered into existence; they are **left over** by total processing.

Why this is affordable now (the pyramid — spend intelligence exactly where cheapness runs out):
- **Vectors** (embedding models): total N×N comparison of everything against everything — cents.
- **The resident 4B swarm** (~12–14 concurrent roles, ~2,700 tok/s measured on this card): bounded
  per-unit judgments — extraction, pairwise agreement, classification. The whole estate in hours.
- **The reranker** (88M, runs on CPU): precision on close pairs — effectively free.
- **Claude-class models**: synthesis of already-judged clusters ONLY. The scarce resource never does
  coverage work.

**The proof this machine works (not speculation):** the RG10 registry pipeline. With no one asking
any question, it processed every mockup → 940 raw extractions → embedding-dedup → deterministic
floors → jury/panel judgment → 483 verified registry entries, WITH its conflicts surfacing as a
byproduct of reconciliation. That ran overnight on this hardware while Tim slept. Every pipeline
below is that same machine pointed at a different corpus.

## 3 · Two corrected framings (errors a reader must not repeat)

This design was reached through two of Tim's corrections, each killing a comfortable first
conclusion. Cold readers will be tempted by the same two errors; don't be.

**Error 1 — retrieval-shaped thinking.** First-draft ideas ("an agent declares its task and its
briefing assembles by similarity") assume an agent that KNOWS its task. For the nobody-knows class,
any mechanism taking a question or task as input is disqualified by the axioms. The corrected class
is **questionless sweeps** that EMIT findings without being asked:
- *Contradiction mining* — two things claiming the same job can't both be right; disagreement is
  detectable by comparison alone, no knowledge of intent required.
- *Expectation mining* — every artifact implies a world (code that calls a function assumes it
  exists and behaves); extract the implications, check them against reality. The artifacts ARE the
  questions.
- *Categorical censuses* — enumerate every mechanism-that-does-X by semantic sweep; conflicts appear
  as multiplicity in the census ("there are four approval mechanisms").
- *Derivation-divergence* — independent agents derive the same understanding from different corners;
  where their honest derivations DISAGREE, the system is inconsistent right there. The multi-agent
  constraint used as a measuring instrument.
- *Boundary probing* — drive the system through its own faces and record surprise (the proven
  cold-eval pattern as a standing organ). Surprise needs no spec.
- *Gap-pressure* — Tim's discovered law: constrained operation itself emits the map of what's
  missing (drops, insistence, tool-misuse = unmet needs).
These remain valid and feed the pipelines; the pipelines in §4 are their industrialized,
model-powered form.

**Error 2 — utterances-as-specs.** Comparing built artifacts against Tim's messages as if they were
acceptance criteria assumes spec-content his messages never carry. **His utterances are a GRADIENT
FIELD, not destinations**: directions ("more like this"), corrections ("not this"), recurring
values, recognitions of things shown to him. The verification consequences:
- **Wrongness is learnable even when rightness is unspecifiable.** Every correction ever recorded is
  a labeled pair (thing-as-built → his reaction). The correction corpus (mined from the full
  transcript history, hundreds deep) trains a rejection-predictor: "does this resemble things he has
  corrected before?" Verification reframed: not *matches the spec* (impossible) but *avoids known
  wrongness and moves with known direction*.
- **The twin** (the model-of-Tim lineage): conditioned on every recorded approval/rejection, it
  predicts his reaction at scale — pre-filtering volume his real gate could never process. His gate
  stays for what matters; the twin handles magnitude.
- **Recognition, not interrogation.** He cannot answer specific questions — so uncertainties must be
  transformed into SHOWN CANDIDATES (A/B/C artifacts) he reacts to. His own stated mode: he
  recognizes the right direction even when he couldn't articulate it.
- **Correctness without an oracle = COHERENCE.** Internally consistent · agreed between independent
  derivations · expectations met · behaviorally unsurprising · aligned with the gradient field.
  Across N sessions that each believed they were right, the coherent core of their overlap is the
  best approximation of the vision that exists anywhere. Truth-by-convergence, because
  truth-by-checking is impossible here.

## 4 · The pipelines

### P1 · TOTAL EXTRACTION — the inventory emitter
*The direct mechanical answer to "every place a UI might connect, and exactly how."*

- **Chunking:** every code unit in the estate — every route, handler, function, state mutation,
  event emission — produced by a PARSER (mechanical, judgment-free, complete by construction).
- **Extraction:** every chunk through a 4B extraction role emitting ONE structured row:
  `{EXPOSES · EXPECTS (what it assumes exists elsewhere) · STATE touched · EVENTS emitted/consumed ·
  INPUTS/OUTPUTS}`. Unconditional — every chunk, no selection. This is the registry-filling
  pattern's MAP step with its designed context package (the chunk + its file dossier + closed
  vocabularies), so the small model is never asked to imagine.
- **Embedding:** the chunk by a CODE embedder (LateOn-Code-130M resident-class, and/or quantized
  nomic-embed-code ~5–6GB for the deep space — both detailed in the research file, including the
  pooling/prefix traps that silently produce garbage if missed); the row by the text embedder.
- **Output:** the **connection-surface registry** — thousands of rows in the substrate, each with
  provenance to exact code. The inventory nobody could write, EMITTED.
- **The property no human inventory ever has: it knows its own coverage.** Chunks-processed over
  chunks-existing is a number. "You have no way of knowing" becomes "the map reports 94% processed,
  and here are the unprocessed 6% BY NAME." Incompleteness stops being unknowable; it becomes a
  metric with a worklist.
- **Parallel-native:** per-chunk idempotent with skip-lists (the proven mining pattern — 1,460
  exchange-extracts were built exactly this way across many bounded batches). Any number of agents
  run it, any session resumes it, nothing is redone, no context is shared.

### P2 · FUSION — conflicts emerge as a byproduct
- Cluster ALL P1 rows by embedding (total, N×N, cheap). Within each cluster the 4B swarm judges
  pairs — *"same thing? do they agree?"* — with the reranker as the precision check on close calls.
- **Output (a): unified concepts** — "these five things are one mechanism under five session-given
  names" → the synonym ledger, registry data every future agent reads so history stops confusing it.
- **Output (b): THE CONTRADICTION LEDGER** — pairs that cluster together but DISAGREE. A conflict is
  precisely A FAILED MERGE: same job, incompatible behavior. Nobody asked where the conflicts were;
  deduplication finds them, because finding them is what failing to deduplicate IS.

### P3 · THE EXPECTATION JOIN — broken assumptions, mechanically
- Every P1 row's EXPECTS field embedded against every row's EXPOSES — **a join, not a search**.
- **Outputs:** expectations matching nothing = the **broken-assumptions list** (one session's belief
  the rest of the system doesn't honor — the precise fingerprint of context-less parallel building);
  exposures matching no expectation = the **orphan list** (built and never used — the stranded-work
  class, found exhaustively instead of stumbled upon by floor walks).

### P4 · THE MERGE — Tim's FE test case, solved as a join
- The other sessions' work (UI principles, or anything else, forever) goes through THE SAME P1
  transform with THE SAME embedding models → their rows land in the SAME coordinate space as this
  estate's rows. Nobody on either side needs to know the other side.
- Cross-match: embedding shortlist → reranker precision → 4B verdict per candidate pair.
- **Three lists fall out mechanically:**
  1. **MATCHED** (principle ↔ surface): the wiring list, provenance in both directions.
  2. **PRINCIPLE-WITHOUT-SURFACE**: the build list — what the UI expects that nothing provides.
  3. **SURFACE-WITHOUT-PRINCIPLE**: the design-debt list — capabilities no principle covers.
- **The integration plan is JOINED into existence, not written.** This is the generic answer to
  merging ANY session's work into ANY estate state, permanently.

### P5 · THE VISUAL JOIN — images become citizens of the same space
- Qwen3-VL-Embedding-2B (open license, ~4–5GB plausible co-resident, screenshot-native, with a
  MATCHED open reranker — the frontier scan's headline find) embeds every mockup REGION and every
  live-UI screenshot into the same space as P1 rows and the 483-entry ui:// address registry.
- **Outputs:** mockup elements matching no surface = unbuilt visual expectations · live screens far
  from their source mockups = **visual drift, measured** (the drift-radar law extended to
  appearance) · Tim's both-faces rule (native desktop AND mobile, always) checkable as unmatched
  face-clusters · later: pitch decks, design styles, the entire visual half of the company data,
  searchable beside the words that describe them.

### P6 · THE RESIDUE — where the unknown-unknowns surface
*The direct mechanical answer to "you can't ask about what you don't know to ask."*
- After P1–P5, collect everything that matched NOTHING: orphan clusters · providerless expectations ·
  extraction failures · zero-coverage zones · census singletons.
- **That residue IS the set nobody knew to ask about** — not found by looking, but left over when
  everything else paired up. It enters the map as first-class findings.

### P7 · STAYING TRUE — the map never rots
- Commit-triggered re-extraction of touched chunks only (the content-hash refresh pattern already
  live in the corpus). The map is a STANDING ORGAN, not a report — it updates as the estate changes.
- **Agents boot from rows, not from code.** A builder lane reads its slice of the connection-surface
  registry; the contradiction ledger warns it; the expectation join scopes it; the residue feeds its
  backlog. Bounded context, parallel by construction — the substrate is the shared memory, exactly
  as the axioms require.
- Findings flow into the proposal lifecycle (propose → Tim's gate, twin-pre-filtered → build → Real),
  so **the map and the work-queue are the same circuit** — the map is made OF the work, not before it.

## 5 · What this resolves, axiom by axiom

| Axiom | Resolution |
|---|---|
| nobody can enumerate the estate | P1 emits the inventory; coverage is a measured number |
| conflicts unenumerated | P2's ledger — conflicts = failed merges, found by deduplication itself |
| sessions' beliefs disagree silently | P3 — beliefs ARE the EXPECTS fields; unmet ones surface |
| merging unknown work into unknown estate | P4 — same transform → same space → three lists |
| can't ask the right questions | P6 — unknown-unknowns are the residue of total processing |
| no spec, ever | §3 — gradient field + wrongness-learning + twin + recognition gates; coherence as the correctness standard |
| parallel agents, no shared context | every pipeline per-unit idempotent; the substrate is the blackboard |
| everything goes stale | P7 — commit-triggered freshness; a standing organ |

## 6 · Open tests (named, deliberately unanswered — push on these)

1. **Can coherence-convergence be gamed by consistently-confident nonsense?** If many sessions made
   the SAME wrong assumption, the coherent core contains it. Candidate counter: boundary probing
   outranks textual coherence (behavior beats agreement), and the gradient field (Tim's corrections)
   outranks both. Unproven.
2. **Prioritization at scale:** when the map holds 10,000 findings, what orders them? Candidates:
   gap-pressure (what operation keeps tripping on) · gradient-field proximity (what Tim's recorded
   direction says matters) · blast-radius (what blocks the most other things). Likely all three as
   declared, inspectable rules — never a confidence score (the no-confidence law).
3. **Extraction-quality drift:** P1's rows are 4B judgments; the floors arc (refcheck → prose_check →
   relation-filter, three lived instances) predicts recurring misfires that should become
   deterministic checks. Budget for that arc; don't fight it.
4. **Which embedder when:** resident-small for the standing map; deep-space (Qwen-8B / nomic-7B
   quant) re-indexes in allocated windows (Tim's approved dual-space pattern); the work-type loadout
   (Tim: "dedicate pretty much all resources to a big embedding model... like a mode at a different
   level") governs transitions. The registry of loadouts exists (combos); the policy is the open bit.
