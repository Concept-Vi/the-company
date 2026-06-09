# The Substrate Exploration — the Wizard lineage · the axes · the convergences (2026-06-10)

> The G17-REDIRECT exploration, run live against the substrate-mcp (8 vaults · 5,486 files · 65k embedded
> chunks · 1,413 types — self-indexed on its own ollama/nomic embedder, healthy). Three findings + the
> merge-vs-reference recommendation. Per the recency-supersedes law: the old corpus is read as LOSSY
> UNVERIFIED EVIDENCE of Tim's intent (the AI-augmentation baked in misreadings) — intent is
> RECONSTRUCTED, never copied as authority; where old and recent diverge, recent wins.

## FINDING 1 — THE WIZARD LINEAGE (the Surface's family tree, three generations)
The semantic trail runs, oldest → newest:
1. **"Virtual Intelligence — the adaptive wizard pattern"** (a canvas node, elevenlabs-mcp/outbox):
   *"A user arrives with a vague goal. The system discovers what's possible, guides them through steps,
   captures typed decisions, and dispatches action."* — *the Surface's one-line definition, years early,
   and it's literally named Vi.* The Live Intent Resolution Surface IS Project Vi's founding pattern.
2. **The ElevenLabs-Wizard build** (115 files — the first serious attempt): "the wizard is the AGENT'S
   OUTPUT, not a static form" · "a conversation that GENERATES SURFACES" (vs linear human-mapped steps) ·
   the agent-as-PRIMARY-INTERFACE doctrine · generative UI research.
3. **The Live Intent Resolution Surface docs** (2026-06, the recent crystallization) — the same pattern,
   matured: progressive type resolution, tags/counts, the decision ledger, execution handoff.

**What the OLD corpus carries that the recent Surface doc does NOT fully — candidate lifts (reconstructed
intent, for Tim's confirmation, not authority):**
- **Capability-check BEFORE flow-generation:** the old wizard *first checks what the platform supports,
  THEN generates a flow sized to context* ("2 steps vs 5"). The Surface doc generates options from intent;
  the old doctrine grounds them in LIVE CAPABILITIES first — for the Company: the Surface should read
  `capabilities`/`cognition_info` before proposing (registry-is-truth applied to option-generation).
- **User-owned vs agent-owned steps:** the old wizard distinguishes steps the USER must do (external
  setup, accounts, approvals) from steps the AGENT can do — surfaced as different step types. The Surface
  doc's decision-closure has this implicitly; the old corpus makes it a first-class step axis.
- **Tool-design-as-doctrine:** the old standing directive says verbatim *"Tool design is not only
  technical function"* — **Tim's 2026-06 MCP-design priority was ALREADY DOCTRINE in the oldest build.**
  The substrate's own tools prove it (enrichment='lean' knobs, size-guards, teaching descriptions — it
  independently follows our MCP-DESIGN-PRINCIPLE).

## FINDING 2 — THE AXES, ANSWERED (G17: how the substrate models what the Company describes thinly)
The substrate models the axes as PER-VAULT REGISTRY DATA (schema, not prose) — the reference model:
- **axes** — typed frontmatter fields, incl. EPISTEMIC ones (`certainty`, `truth_class`) the Company lacks.
- **state_axis** — ONE named lifecycle axis per vault (+ `open_seam_count` derived from openness tokens —
  a standing "what's unresolved" READ, like our inbox but data-derived).
- **temporal_fields** — declared (created/updated/decided_on/…) = G16's temporal axis as schema.
- **relation_kinds** — the structural axes as TYPED RELATIONS: SEQUENCE (`precedes/follows/next/prev/
  stages_traversed`), HIERARCHY (`parent/part_of/siblings/components`), DEPENDENCY (`depends_on/gates/
  unlocks/reads_from/writes_to`), even `ripples_back_to`. The Company's relation_types registry (4 kinds:
  contradicts/fragment_of/principle_beneath/sibling) is the SAME mechanism, thinly populated.
- **the type-graph** — 1,413 types ON axes (autopoietic: the vocabulary grew from use).
**THE MOVE (concrete, small):** extend the Company's relation_types registry with the sequence/hierarchy/
dependency vocabularies (file-per-kind, create(kind='relation_type') — minutes of work) + add `certainty`
as a projection lens. The axes question is answered by data we already have the machinery for.

## FINDING 3 — THE CONVERGENCES (EM-739's own law, applied to itself)
The unification vault's EMERGENT notes and the Company converged INDEPENDENTLY on:
| The old corpus (unification-vault) | The Company (built blind to it) |
|---|---|
| EM-431 Decision Readiness as Build Gate ("no build before the governing decisions") | the FLOOR + the decision→build wire |
| EM-610 Founder Decision as a Distinct Information Class | operator-only resolve; Tim's gates |
| EM-557 Human-in-the-Loop as Architectural Invariant ("AI processes, human directs, AI records") | the whole loop's shape |
| EM-1252 Prose-Without-Action ("decisions need validation gates") | verify-by-USE / no green-paint |
| XP-010 Temporal Convergence "enables the most capabilities" | G16 (Tim: "the temporal axis plays a real role") |
| EM-939 Structure-Behavior (schema-enforced first, behavior later) | registry-is-truth / schema-additive |
Per EM-739 itself: **independent convergence = the principle is necessary, not optional.** These are now
doubly-proven load-bearing laws — the strongest possible evidence class for the Company's constitution.

## THE RECOMMENDATION — reference + selective lifts, NOT a merge
- **Reference (the standing mode):** the substrate stays a separate, self-indexed corpus on its own
  embedder (healthy, working); the Company queries it live via substrate-mcp whenever lineage/axes/
  precedent is needed. No re-embedding of 65k chunks into the company corpus (reuse-don't-parallel;
  a merge duplicates working infrastructure for near-zero gain and entangles two embedding models).
- **Selective content lifts (per-need, with provenance):** today's three (the capability-check-first
  doctrine · user-owned-vs-agent-owned steps · the axes vocabularies) lift into Company docs/registries
  as RECONSTRUCTED INTENT marked for Tim's confirmation. Future lifts follow the same pattern.
- **The connective tissue already exists:** the substrate-mcp is just another MCP the crew can call.

## HEALTH (filed via the substrate's own issue system)
ulm-inventory: chunks_embedded=1,415 but chroma_count=0 — a broken/empty collection, the likely cause of
the all-vault ('*') semantic-search compactor error (single-/multi-vault searches excluding it work).
