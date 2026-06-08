# Cognition Engine — Completion Criteria (product-grade · corpus-capable · composable · self-extending)

> **What this is.** The truth-table of what must be TRUE for the cognition engine to be *done* — not "the code exists" but "an agent (and the operator) can USE it for real, conveniently, at scale." Every criterion is **verifiable by use** and carries **honest status** (✅ proven-by-use · 🟡 built-not-proven / designed · 🔴 gap / not-built). Form is half of done where there's a surface.
>
> **How this doc was built — and the method it encodes.** These criteria were not guessed up front. They were *discovered by using the engine*: dogfooding the MCP across 8 varied uses, running the concurrent map on the repo's own 427 files, and critically assessing why it ran below ceiling / where the output went / what the surface exposes. **That loop — use → critically assess → reason → improve → write it into the criteria — IS the method.** It's how the bar stays real (found by use) instead of green-painted (asserted). Every future finding of this kind lands here. (Aligns with loop-prep's two-faced verifiable-by-use criteria + the open-future / verify-before-claiming / no-green-paint laws.)

---

## GROUP A — Direct authoring (the agent composes its own cognition, no approval)
- **A1 · create direct, no approval** — `create_role`/`create_skill`/`create_context` apply LIVE (render→write→commit→rediscover) with NO operator-approval step. ✅ proven-by-use (repo_digest created via MCP → live, no surfaced item, 5fcc47b).
- **A2 · full capability schema** — a created role can set EVERY capability: structured-outputs · op(generate|embed) · thinking(on/off) · tools · knobs · model · input_addresses(incl skill://context://run://cas://) · mode_scope · rules · context. ✅ fields land + project (verified) · 🟡 FORM: the *convenience* of setting them (see B) not yet product-grade.
- **A3 · correctness gate bites (kept)** — a malformed spec is REFUSED fail-loud, never written (a bad role can't brick discovery). ✅ proven (AuthoringError on bad id/type).
- **A4 · build-dispatch floor holds (kept, by Tim's standing call)** — NO cognition/engine/MCP path emits `dispatch_decision` or launches `claude -p`; the build-function autonomy stays as set. ✅ governance 30/30 (AST scan).

## GROUP B — Composition surface (registry-is-truth; the product/convenience layer) 🔴 the active gap
*The single layer both faces (MCP agent + FE human) read — reflects-never-owns. The tools must be a generic renderer over the registries, NOT hardcoded.*
- **B1 · every select/param/spec PROJECTS from a registry (zero hardcoding)** — adding a skill/model/type/mode makes it settable everywhere with no tool edit. 🟡 most registries exist + are projected (roles/skills/contexts/runs/models/modes/node-types/rule-ops/destinations/schemes); 🔴 not all selects wired to them.
- **B2 · `field_types` is a TYPE REGISTRY, richer** — the ONLY hardcoded select today (flat scalars). Make it a registry + support nested objects / list[dict] / enum / optional / defaults — real product schemas. 🔴 gap (net-new: the type registry).
- **B3 · `cognition_inputs` advertises the full input space** — skill://·context://·live-runs·context-vars·schemes, projected from the registries (today it OMITS skill://+context:// — discoverability broken). 🔴 gap.
- **B4 · create-spec is discoverable + validating** — the agent learns the spec shape (fields, required/optional, per-field types) + gets fail-loud feedback, not infer-from-example. 🔴 gap.
- **B5 · op/thinking/tools project from the MODEL-CAPABILITY registry** — what's settable = what the model actually supports. 🔴 gap.
- **B6 · FORM** — the surface reads as a navigable, discoverable composition surface on both faces (MCP schema + FE), not a flat hardcoded list. 🔴 needs the FE (Group G).

## GROUP C — Concurrency / loadout (run at the REAL ceiling, mode-driven)
- **C1 · the swarm runs at its real ceiling (~32), not 14** — FOUND: `max_num_seqs:16 − R:2 = 14` is the binding cap; KV supports 44; other services already run 32. 🔴 the make: chat-4b swarm `max_num_seqs`→34. (Proven-by-measurement when set + re-run.)
- **C2 · concurrency is MODE-DRIVEN** — swarm-mode declares its loadout (max_num_seqs + util) via `brain_config`; the launch capability (#50) provisions it; the budget derives from the LIVE config (already registry-read — the VALUE was wrong-regime). 🔴 gap (wires B-loadout + #50 + brain_config).
- **C3 · proven by measurement** — re-run the whole-repo map at the swarm loadout, measure the realized knee ≈ 32 + the throughput gain. 🔴 the confirming experiment.

## GROUP D — Corpus / output (the SINK — output lands, embeds, is used)
*The scale test digested 427 files and DISCARDED them. The engine produces at scale with no place for output to live + be reused. This is the production half that's missing.*
- **D1 · map output becomes a corpus-record** — `{source_address, output, kind, model, ts}` persisted (cas://) + indexed (run-index). 🔴 gap.
- **D2 · embed-on-write** — each corpus-record → op=embed → put_vector (the existing vector index). 🔴 wiring (primitives exist).
- **D3 · retrieve-as-input (RAG over the corpus)** — a retrieve over the corpus → context:// a role reads; outputs→inputs by semantic match. 🔴 wiring (query_index exists).
- **D4 · cluster = built-twice discovery** — run_reduce(cluster) over the corpus surfaces near-duplicates. 🟡 cluster built (seeded); 🔴 not pointed at the live corpus.
- **D5 · queryable, ingest-once-query-many** — the corpus is a durable, addressed, queryable artifact (selective invalidation). 🔴 gap.
- **D6 · purposeful chains** — map→reduce→artifact toward a GOAL (repo index · find duplicates · cross-repo Q&A · coherence scan), SAVED + re-runnable. 🔴 gap (the corpus-chain).

## GROUP E — Run discovery + chaining (outputs→inputs natural)
- **E1 · every run returns its addressable handle** — run://address + turn_id in the response. ✅ proven-by-use.
- **E2 · runs are discoverable** — list_runs/find_runs over the run-index. ✅ built (a823f90) · 🟡 the index reparses O(events) — needs an efficient index, not a full scan (caught at scale).
- **E3 · outputs→inputs by discovery** — a discovered run:// fed as an input (not hand-copied). ✅ the loop proven · 🔴 a "feed-last-output" chain handle for convenience (the manual-threading friction).
- **E4 · chain persistence + re-run + output-destination** — save a chain config to re-run; direct a run's output to a named destination/lane. 🔴 gap.

## GROUP F — Robustness at scale (caught by the whole-repo test)
- **F1 · run_items :// classification correct** — a unit is an address only if it STARTS with a registered scheme, not merely contains "://" (16% of repo files broke the map). 🔴 gap (verified bug).
- **F2 · batch per-unit resilient** — one bad unit goes to skipped/failed; the good units' outputs still return (today one poison unit discards the whole batch). 🔴 gap (verified).
- **F3 · chunk-and-compose for over-context files** — split→map→compose for files > the model context (today: loud 400). 🔴 gap.
- **F4 · errors are clear, not generic** — context-overflow says "context length exceeded"; run_reduce role-mismatch gives a contract error not a bare KeyError. 🟡 fails loud (healthy) but messages generic.
- **F5 · scale baseline (healthy, keep)** — 427 files, linear, saturates the budget, 0 fail-silent, overflow loud. ✅ proven.

## GROUP G — The two faces (one surface, reflects-never-owns)
- **G1 · MCP agent face** — configure/run/inspect/create/embed/discover via MCP, reusing the engine. ✅ proven (15+ tools, by use).
- **G2 · FE human face** — the operator sees + does the same (resident models/GPU/runs + create/run/configure/re-run), reading the SAME registries the MCP reads. 🔴 gap (#55).
- **G3 · one composition surface** — both faces project from the same registries (Group B); declare once, both get it. 🔴 depends on B.

---

## Priority (foundations → features)
1. **F1/F2** robustness (the engine must not break on real corpus content) — cheapest, unblocks real use.
2. **C1/C2** the loadout ceiling (run at 32, mode-driven) — the throughput foundation.
3. **B** the composition surface from registries (B2 type-registry is the net-new keystone) — the product/convenience layer both faces need.
4. **D** the corpus sink + embed/retrieve + purposeful chains — turns "runs" into "a used corpus."
5. **E4** chain persistence · **G2** the FE human face — compose on the now-product-grade surface.

## Verification bar (every criterion)
By USE, never code-reading. FUNCTION: the real behaviour moves, at scale where relevant, no stub. FORM (where a surface exists): registry-projected (no hardcoding), discoverable, navigable — graded separately. Honest status only — a needs-tim/gap stays a gap; nothing green-painted. New findings from the use→assess→reason loop land here as new criteria.
