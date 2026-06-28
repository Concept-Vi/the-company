# Ledger Enrichment Plan — edges, proximity, coverage

> **Operations-reflection (Tim, 2026-06-29).** This whole process — the ledger build, the first-run audit, and the enrichment passes below — is a **prototype of standing Company operations**, not a one-off cleanup. After we've worked it all out, each pass here reflects *into* Company operations as a flow / routine / capability the Company runs on itself (the way the registry, flows, and routines already do). So this is written to be **reflectable**: the durable core is the *principles* and the *shape of each operation*, not throwaway scripts. Provisional working-out is marked as such. The reflection-into-operations happens later — this note just holds the design so it survives.

## Principles (the durable core — this is what reflects into operations)
- **No mined opinions.** Every edge is either *evidenced* (fact / grounded) or *measured* (proximity). Judgment stays with Tim's recognition, or with the decision system — never asserted by a model.
- **Evidence-gated.** No edge is written unless it can cite the evidence that grounds it. No citation → not an edge. *(Enforce, don't convention — the twin of the no-confidence law.)*
- **Tags + counts, never confidence/scores** (G16). Strength = how-derived (tag) + how-many-corroborate (count). Even proximity stores adjacency + counts, not a float.
- **Verify, don't trust.** The deterministic layer's *completeness* is independently audited, not assumed — because it fails silently (a missed symbol leaves no trace).
- **Embeddings give objective relatedness.** "What's related to what" becomes a *measurement* (position in text-space / code-space), not an opinion. The machine finds candidates; the human (or a later process) recognises the relationship.
- **Descriptive vs prescriptive** (vault law). Descriptive edges may be *discovered*; prescriptive acts (`supersedes`, `governs`, `blocks`, `decides`) are *declared* via the decision system, never mined.

## The passes — each a future standing operation

### 1. Coverage-audit harness — *verify the structure is COMPLETE*
The 4B as **auditor-against-ground-truth** (the file is the answer key) — NOT as opinion-maker. Give it the file + what was extracted (symbols / signatures / imports) and ask what's missing. Aggregate flags → a **blind-spot map by language** (we expect JS/TS to light up red, Python clean — this would have auto-caught F2).
- **Two passes while we work it out:** *with-contract* (conformance — did we extract what we intended?) and *without-contract* (discovery — what's worth extracting that we never specified?). The **diff** (without-flags the with-pass doesn't raise) = candidate new contract items; the without-pass is *how the contract grows*. Read the without-pass at the **aggregate/pattern level** (noisier — no constraint).
- Output stored as a **tags+counts coverage signal** per file ("cross-check: clean" / "N candidates flagged"). Run **sampled-per-language first** (cheap, fast). Triage for patterns — never auto-apply a flag (would trade silent under-extraction for noisy over-extraction).
- **Sweet spot:** within-file completeness. **Blind spot:** cross-file edge correctness (needs a different check).
- **Depends on** the carry-forward fix (F6) for the cheap fix→rerun-only-affected-files loop.

### 2. Fact-edge harvest — *the document graph, free & deterministic*
Frontmatter/structural edges: `attached_to`, `in_channel`, `stored_as`, `authored_by`, `references` (literal). No model. Always evidenced.

### 3. Grounded-edge harvest — *evidenced inference, auditable*
Detect in code + cite the line: `verifies` (test calls/asserts on target), `uses` (import/token), `quotes` (the span), `depends_on`. *(Kept for now; deletable after Tim reviews — confirmed 2026-06-29.)*

### 4. Proximity layer — *measured relatedness, the objective substitute for judgment edges*
Embed every file in **text-space and code-space** (Tim's text + code embedders). Store nearest-neighbour **adjacency** + **clusters** as tags+counts (no floats stored). This is what replaces the deferred lineage/variant/mirror edges: the graph shows neighbourhoods; Tim (or a later process) recognises the relationship.

## Deferred — not built now (sequenced, not deleted)
- **Judgment edges** (`supersedes`, `variant_of`, `derived_from`, `contradicts`, `corrects`, `mirrors`…) — surfaced for recognition over the proximity neighbourhoods, never asserted by a model.
- **Prescriptive edges** (`governs`, `blocks`, `decides`) — decision-system territory; recorded only when declared.

## Curated core vocabulary
The 25-kind core (8 families) is in [FIRST-RUN-QUALITY-REPORT.md] / the channel table (2026-06-29). The long tail (~8,400 kinds) stays as free-text tags on edges; only the core is rendered as graph structure.

## Sequence
**A — truncation fix (never-truncate)** → **coverage-audit harness** (harden the structure everything stands on) → **fact + grounded edges** → **proximity layer**.
