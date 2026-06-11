# Total-Processing Pipelines — knowing without questions (2026-06-11, conversation capture)

**Tim's constraints (axioms, his words):** "The only assumption that can be relied on is that no
assumptions can be relied on." Nobody — Tim, the lead, any agent — can enumerate what's built; no
spec/plan exists or can ever be given ("I am not a developer... I can never provide specifications");
every session believed it was right so everything reads as-if-correct; conflicts are UNENUMERATED;
question-asking mechanisms are disqualified (you can't ask about what you don't know to ask);
building is parallel multi-agent, no shared context. His test case: merging other sessions' UI work
needs the full connection-surface inventory nobody can produce.

**THE CORE MECHANICAL INSIGHT: questions are selective reads; embeddings + cheap local models make
TOTAL reads affordable. Process everything unconditionally; unknown-unknowns surface as RESIDUE of
total processing, never as answers to questions.** Proven once already: RG10 (940 mockup extractions
→ 483 registry entries, conflicts as byproduct) IS this machine; these pipelines point it at the
whole estate.

**Two corrected framings (Tim's pushback, both rounds):**
- Round 1 error: boot-by-similarity etc. assume an agent that knows its task. Disqualified for the
  nobody-knows class. → Questionless sweeps (contradiction mining · expectation mining · censuses ·
  derivation-divergence · boundary probes · gap-pressure) writing a LIVING MAP into the substrate;
  correctness standard = COHERENCE (truth-by-convergence; no oracle exists).
- Round 2 error: utterances-as-specs assumes spec-content in his messages. → Utterances are a
  GRADIENT FIELD (directions, corrections, values, recognitions — never destinations). Verification:
  wrongness-avoidance learned from the correction corpus + the twin as scalable reaction-predictor +
  recognition-based A/B/C gates (never specific questions — he cannot answer them).

## The pipelines (models from embedding-research-2026-06.md)

**P1 · TOTAL EXTRACTION (the inventory emitter).** Every code unit (parser-chunked: routes, handlers,
functions, state mutations, event emissions) → 4B extraction role (~12-14 concurrent) emits
{EXPOSES · EXPECTS · state touched · events · inputs/outputs} + code-embedding (LateOn-130M /
quantized nomic) + row-embedding (text model). Output: the CONNECTION-SURFACE REGISTRY with
provenance. KEY PROPERTY: knows its own coverage (% chunks processed — "no way of knowing" becomes a
number). Idempotent per-chunk (skip-lists) = parallel/resumable native.

**P2 · FUSION → conflicts as BYPRODUCT.** Cluster all rows (embedding, total N×N); within-cluster 4B
pairwise "same? agree?" + reranker precision. Outputs: unified concepts (N names → 1 mechanism) +
THE CONTRADICTION LEDGER (clusters-but-disagrees = a failed merge IS a conflict; nobody asked).

**P3 · EXPECTATION JOIN.** All EXPECTS embedded against all EXPOSES — a join, not a search.
Outputs: broken-assumptions list (expectations matching nothing) + orphan list (exposures no one
expects = stranded work found exhaustively).

**P4 · THE MERGE (the FE case).** Other sessions' work through the SAME P1 transform/models → same
coordinate space → cross-match (embed → rerank → 4B verdict). Three lists fall out: MATCHED (the
wiring list) · PRINCIPLE-WITHOUT-SURFACE (the build list) · SURFACE-WITHOUT-PRINCIPLE (design debt).
The integration plan is JOINED into existence, not written.

**P5 · VISUAL JOIN.** Qwen3-VL-2B (open, ~4-5GB, screenshot-native) embeds mockup REGIONS + live-UI
screenshots into the same space as P1 rows + the 483 addresses. Outputs: unbuilt visual expectations ·
measured visual drift · both-faces (desktop/mobile) rule checkable as unmatched clusters.

**P6 · THE RESIDUE = the unknown-unknowns.** After P1-P5: orphan clusters, providerless expectations,
extraction failures, zero-coverage zones — THE SET NOBODY KNEW TO ASK ABOUT, as leftovers.

**P7 · STAYING TRUE.** Commit-triggered re-extraction of touched chunks (content-hash refresh
pattern, already live in the corpus). Agents BOOT FROM ROWS, not code — bounded context, the
substrate is the shared memory.

**Economics (this card, today):** embeddings = total coverage for cents; 4B @ ~2700 tok/s = estate
extraction in hours; reranker = free CPU precision; Claude-class = synthesis only. The pyramid spends
intelligence exactly where cheapness runs out.

**Open tests Tim should push on (named by the lead, unanswered):** can coherence-convergence be gamed
by consistently-confident nonsense across sessions? How does the map prioritize 10,000 simultaneous
findings? (Candidate: gap-pressure + his gradient-field as the priority signal.)
