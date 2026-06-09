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

---
# PART 2 — NO-REGRESSION: the foundation + all carried-forward + the mode-reach groups
> Tim's mandate (2026-06-09): this is NOT a pivot — it's the continuation of what was always meant to happen, so **everything from before must be present, nothing dropped.** This part makes that explicit: the original build is the proven base (by reference), and every still-open prior item is carried forward as a criterion here.

## FOUNDATION — the original Concurrent Cognition build (G0–G9), PROVEN by use
**Source (the proven base, persists, no regression):** `build-prep/concurrent-cognition/Concurrent Cognition — Completion Criteria.md` (+ its Guide/Synthesis) + the engine commits `[cognition]` + `.build/OVERNIGHT-WALKTHROUGH.md`. Status there: G0 spike · G1 substrate · G2 roles · G3 rule-engine · G4 staged-reply · G5 per-turn · G6 voice-coupling · G7 view · G9 governance — **✅ by use** (verified across this session: the engine quartet, the floor, the suites). This triad **supersedes by reference + extends** — it does not re-derive the done base; it carries the OPEN items below + adds the product/corpus/surface layer (Part 1).

## CARRIED-FORWARD (the original's still-open items — folded into this triad, NOT dropped)
- **C1.7-deep · the deep-main concurrency knee at util 0.63** — proven at 0.49 (knee=14); the 0.63 swarm-brain deep-64K-main knee is computed-not-measured. → folds into **GROUP C** (the loadout — the 16→32 work proves this too; needs the GPU reconfig + a real deep-main wave). needs-tim on the live measure.
- **C2.5 · the model CATALOG (the original G8/L-model)** — the role↔model query is built, but the provider set is resident-chat-4b-only; the capability catalog needs widening (the original G8). → **new criterion (Group B5 extends to the catalog):** MODEL_CAPABILITIES projects the full live catalog (chat·embed·vision·...), so role-binding + the op/thinking/tools selects project real model capabilities. 🔴.
- **C0.3 (fusing-quality) · C4.4 (one-voice feel) · staged-stream feel · on-device voice audio · the view's aesthetics** — perceptual needs-tim, carried (never loop-green; yours to judge). Listed in Part-1 needs-tim.

## GROUP H — Activation drivers (the original G5 background/sense/rollup — built-but-UNDRIVEN)
*Verified outstanding: `fire_activation`/`consolidate_rollup` exist but have NO route/timer driver — the between-turns cognition the modes allocate never fires.*
- **H1 · background driver** — an idle-loop tick fires the mode's cast → destinations (surface/address/lane), no reply, under the mode's budget. 🔴 (the substrate exists in `activation.py`; the driver is net-new — a timer/idle-loop). FORM: the surfaced output is navigable, not noise.
- **H2 · sense driver** — an event-hook fires the cast on a screen/app/state-change (the cast sees the event as its utterance). 🔴.
- **H3 · rollup driver** — a timer tick runs the introspective-data consolidation of the swarm's run-records → a rollup. 🔴. (The activation contexts are declared registry-data; the DRIVERS are the gap. Connect: a scheduler/timer + the resource budget — never a parallel loop.)

## GROUP I — Mode auto-detector (the toggle exists, no detector)
- **I1 · a detector PRODUCES a mode candidate** — `autodetect_mode` honors off/suggest/auto over a SUPPLIED candidate; nothing produces one. Build the detector (reads the live signal → a candidate mode), feeding the existing toggle. 🔴. Connect: the mode registry + the signal source; deterministic where possible. FORM: the suggestion surfaces legibly (suggest-mode), never silently auto-switches without the declared posture.

## GROUP J — Cognition↔resolution feedback loop (the system sees its own thinking)
- **J1 · the swarm's run:// outputs feed R2's next-turn resolution** — today R2 resolves operator-notebook strata; the swarm's thinking (run://<turn>/<role>) is a parallel edge that never converges back. Wire the prior turn's cognition into what the next turn resolves (the system's own thinking becomes context). 🔴. Connect: R2 (`_r2_gather`) + the run-index (#54) + resolve_address. (The cleanest "the system sees itself" wire; relates to the corpus D — cognition output as retrievable context.)

## NO-REGRESSION COVERAGE STATEMENT
Every prior item is accounted for: the original G0–G9 (✅ proven, by reference) · C1.7-deep + C2.5-catalog (carried → C + B5-catalog) · the perceptual feels (carried → needs-tim) · G5 background/sense/rollup (→ Group H) · the mode-map lost-opportunities #5/#6/#8 (→ H/I/J) · #3 brain_config (→ C) · #2/#4/#7 (✅ done: A served 13 axes + consent-routing; cast-beyond-listening). The NEW layer (Part 1, Groups A–G) is the product/corpus/composition/robustness extension. **Nothing from before is dropped; this triad is the single complete bar.**

---
# PART 3 — THE CORPUS/DISCOVERY PILLAR (rides the cognition spine; registry-driven; from run-1 + the inspection)
> Built-ready criteria. See IMPLEMENTATION-GUIDE Part 3 for the run-1→real-code mapping. Everything dynamic/contextual/compositional/registry-loaded — NO static values.

## GROUP K — Multi-projection capture
- **K1** a `projections` registry (file-discovered, add-a-row) declares the lens set; a `capture` role's output_schema is built FROM it. 🔴
- **K2** `run_items(role=capture, items=corpus)` renders each unit at many lenses → per-projection records on the store (cas://) + code projections (lifters registry). 🔴 (reuses run_items)
- **K3** render-NOT-judge (the prompt); a unit is DESCRIBED (map), judged later (reduce) — the 4B is a describer not a judge. 🔴

## GROUP L — Multi-space embedding + the inversion-finder
- **L1** each embeddable projection → op=embed → put_vector space-keyed (vec://<item>#space=<proj>). 🔴 (reuses op=embed)
- **L2** query_index gains a space filter; `find_relations(item, near_space, far_space)` = near∩¬far = the inversion-finder (same principle, different subject). 🔴
- **L3** composed/typed/directional relations via a relation-type registry (principle-beneath/fragment-of/contradicts/sibling). 🔴

## GROUP M — The marks layer (= the finding/disposition store, REUSED) + corroboration + fingerprint
- **M1** marks = `append_finding` (coherence's store; mark_type from a registry); a mark-pass = a run_role/run_reduce pass. 🔴 (reuses the finding store)
- **M2** the gold-likelihood PROFILE = findings_for(item) composed with evidence (a read, never a stored score; Tim sees-why, overrules). 🔴
- **M3** corroboration = run_reduce(cluster) over principle-space, cross-SESSION (lineage); positive-only (rare→flag, NEVER discard; frequency only promotes). 🔴
- **M4** fingerprint = coined-vocab vs an AI-tics registry → ai-fingerprint marks; denoising = surfacing, opposite direction. 🔴

## GROUP N — The tiered cascade (REUSE the ActionRegistry)
- **N1** a cascade = a saved Action (coherence_actions.build_action/ActionRegistry — EXISTS); multi-hop, per-step model/tier, looping. 🔴 (wire the runner)
- **N2** MODEL_CAPABILITIES += cloud-reasoner models; run_role(model=cloud) routes via the fabric (reasoning-field + headroom + multi-turn). 🔴
- **N3** `run_cascade(action_id, inputs)` executes the declared Action; the engine routes each sub-question to the tier that fits. 🔴

## GROUP O — Generation robustness (cognition.py; the engine's reliability — could fold into F)
- **O1** json_schema (grammar-constrained), NOT json_object. 🔴 (CHANGE run_role)
- **O2** repetition_penalty ladder (1.1→1.2→fail-loud degenerate-loop), per-content via the generation-policy registry; frequency_penalty is wrong. 🔴 · **OPEN: rep_penalty can censor legitimate enumeration → diff-against-source, never silent (Tim-decision).**
- **O3** persist finish_reason + tokens (op.run); the adaptive large-file handler (raise/split/chunk-overlap/route), never an arbitrary cap. 🔴

## GROUP P — Everything-registry (the dynamic/compositional law made concrete)
- **P1** new registries file-discovered + projecting (cognition_info pattern): projections·lifters·mark-types·AI-tics·relation-types·generation-policies·forms — add-a-row, no code. 🔴
- **P2** the agent authors them (create_projection/create_mark_type/...) like create_role; the system composes its own discovery passes. 🔴
- **P3** the B inspection fixes: _REDUCE_RULES/api_verbs/ENGINE_RUN_OPS/PROTECTED_ROLES → projected not hardcoded; selects hang off the capabilities umbrella; guard-consistency pass. 🔴

## GROUP Q — Patterned-visibility render (the interactive renderer; = #55/G2)
- **Q1** the FE renders the network (nodes=items+projections+marks, typed edges, clusters, gold-profiles, rare-flags, inversions) from the projections over /api, on kit.tsx. 🔴
- **Q2** the loop: render→grab→annotate(write a disposition/mark)→steers the next run_items. Patterned-visibility, rendered. 🔴 FORM: navigable-not-text, design-system, design-lint.

## OPEN DECISIONS (Tim's — captured for him + the adversaries)
1. rep_penalty vs legitimate enumeration (O2) · 2. node-authoring line: declarative-direct/code-gated (the inspection) · 3. pillar-relationship: distinct pillar on the spine (lean) vs deeper GROUP D.

---
# PART 4 — ADVERSARIAL-FOLD corrections (see GUIDE Part 4; these supersede the over-claims)
## RESTORED (no-regression violations adversary-foundations caught — were DROPPED/mis-stated)
- **C7.3 · the live ANIMATED per-turn thought-visualization (the CRAFT SURFACE, Tim-flagged 2026-06-07)** — distinct from the corpus-network render (Q); carried. 🔴 FORM: animation, watch-the-wave; needs-tim on feel.
- **G8 (cloud-decoupled · swarm-always-resident · residency-fail-loud)** — added to the proven FOUNDATION; the cloud-routing rides these, never breaks them. ✅ base + the cloud-additive rule.
- **C7.4 · canvas authoring of roles/rules** (the FE create surface, beside the agent create). 🔴
## RE-SIZED / CORRECTED (verified)
- the **cascade RUNNER is NET-NEW** (N1-N3; the ActionRegistry only validates/saves) · **cloud routing net-new transport** (run_role is resident-only) · **marks = a GENERALIZATION of the finding store** (not same-shape; needs claim/span + mark-type retrieval) · **field_types is widen-the-grammar, NOT a registry** (K/B2 contradiction fixed) · **the model layer goes file-discovered** (Native Model Layer; supersedes N2) · **registries must be file-discovered + create_*-authorable** (P1: not "projects").
- **LANES added:** LANE-FABRIC (transport/client) · LANE-STORE (fs_store+vector_index — ban OFF, abide the store constitution).
- **LINEAGE is a sequencing GATE** (session/round/project in the corpus-record before the first run). Restored disciplines: map-vs-reduce enforcement · effort-routing by form · resume-safety. Ingestion path (/mnt/c→ext4). Thresholds per-context. json_schema VERIFY.
## DECISIONS resolved (Tim's posture + the laws) · 1 open
- fs_store: **edit/upgrade, abide portability (address-stable+Protocol)+constitution** ✓ · render: **EXTENDS the RHM organ** (reuse-don't-parallel) ✓ · model layer: **file-discovered** (Native Model Layer) ✓ · node-type authoring: **gated (code=the floor)**, declarative direct ✓ · **OPEN: rep_penalty robust-vs-lossy (lean: ladder + diff-against-source, never silent).**

---
# PART 5 — TWO STANDING BARS (cross-cutting; EVERY lane/tool/module held to BOTH, like Form)
> Tim 2026-06-09: the agent-knowledge layer + self-describing-for-update are MAJOR parts of the implementation, not polish. They're the two halves of AI-operable-with-no-human-devs: agents know how to USE it, and how to EVOLVE it. Verified by USE (a FRESH agent/session, no hand-holding).

## BAR 1 — AGENT-KNOWLEDGE (how an agent knows to call any of this)
Every capability ships its knowledge-path, on four layers:
- **AK1 · Discovery** — `cognition_info` (+ the registry projections) is the entry-point: a call returns the complete live capability surface (roles, projections, models, tools, the new registries). The agent learns "what can I compose" from ONE call, never from hardcoded knowledge. 🔴/✅(exists, extend to new registries)
- **AK2 · Per-tool descriptions** — EVERY MCP tool ships a rich description: what it does · when to use it · each param · what it RETURNS (the response shape) · how it composes with others. A capable agent can use any single tool from its schema alone. 🔴 (audit + bring all tools — incl. the old node-graph ones — to this bar)
- **AK3 · Per-workflow SKILLS** — every MULTI-STEP workflow (the 3-layer corpus pipeline · the patterned-visibility loop · the inversion-query · map-vs-reduce composition) ships a SKILL (the composition recipe — order, wiring output→input, when to use which tier), like the existing build-loop skills. Single tool-descs do NOT encode multi-step composition; the skill does. ✅ verified-by-use (d85f9f6 — 4 file-discovered recipe-skills: corpus_pipeline·patterned_visibility·inversion_query·map_reduce_composition; discover+read+registry-grounded; floor 31/31)
- **AK4 · Saved cascades** — a saved Action IS a frozen recipe; `run_cascade(action)` runs the encoded workflow. The agent reuses proven pipelines without re-deriving them. 🔴
- **VERIFY (the bar):** a FRESH agent, given ONLY `cognition_info` + the tool descriptions + the skills (no hand-holding, no pre-knowledge of the steps), can drive the 3-layer corpus pipeline + the follow-up queries by use. If it can't, the knowledge-layer is incomplete. *(This is the "agent-usability is half of done" analog of the Form bar — assessed, not assumed.)*

## BAR 2 — SELF-DESCRIBING FOR UPDATE (how an agent knows to evolve it; no human devs)
Every module/tool/registry/criterion is documented so the NEXT AI session/agent can update + extend it easily — the AI-path-of-least-resistance: the *correct* update is the *easiest* one.
- **SD1 · Module self-description** — each module carries its constitution (`AGENTS.md`: Is / Guarantees / Where-new-things-go / To-extend / Never), kept TRUE as part of every change (drift-acceptance passes — the standing gate). 🔴/✅(pattern exists, hold the new modules to it)
- **SD2 · Registry drift-homes** — every registry (incl. the 7 new ones) declares its drift-home + the "add-a-row = a FILE" recipe in-place, so extending it is obvious + can't silently drift. 🔴
- **SD3 · Inline WHY + seams** — the code explains its reasoning (not just what), names its seams ("where X plugs in"), and its "never" list — so an agent reading it cold can change it without re-deriving or breaking an invariant. 🔴
- **SD4 · Tool↔code traceability** — each tool's description names its delegate (tool → Suite/engine fn → what it touches), so an agent updating behaviour knows where it actually lives (the inspection-map, made standing). 🔴
- **VERIFY (the bar):** a FRESH session, given only the self-description (the constitutions + drift-homes + inline-why), can correctly EXTEND a registry / change a tool / add a projection without reading the whole codebase or breaking an invariant. The drift gate fails loud if a change doesn't update its self-description.

## Why these are load-bearing (the connection)
The system is AI-operated with NO human developers. BAR 1 = agents know how to USE it; BAR 2 = agents know how to EVOLVE it. Without BAR 1, the tools exist but agents can't compose them. Without BAR 2, the code works but the next session can't safely change it → drift, the thing the whole Company fights. Together they ARE the self-hosting spine: the system describes itself well enough to be used AND grown by AI alone.
