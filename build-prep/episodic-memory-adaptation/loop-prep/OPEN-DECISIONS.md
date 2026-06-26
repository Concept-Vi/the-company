# recollection — OPEN DECISIONS FOR TIM

> **Tim answers these in ONE pass at the end of loop-prep** (his call, 2026-06-14: "I'll answer all things at the end, once I've been through... probably the most important here"). Accumulated as the exploration waves surface them. Each entry: the decision · why it's open · the options · my lean. **Resolved-by-me items are at the bottom** (FYI, no action needed) so the decision list stays clean and complete.
>
> Status: WAVE 1 in progress (constraints ✓, design-truth ✓, build-map pending). More may be added by waves 2–3.

---

## ★ RESOLVED — evidence-grounded decisions (recollection-session, 2026-06-14)
> Tim (2026-06-14): "make the decisions for me, but with supporting evidence for why I'd choose it — from our conversation — and record the reasoning so I can ask questions later." These are MY calls, each with its evidence trail + a confidence mark. Tim can interrogate/override any. Trust-tag: `tim-direct` = he said it; `inferred` = grounded in his principles/prior statements. Detailed option text retained below.

- **D-1 · Address grammar → MULTI-SPACE ADDRESSING (Tim-direct, 2026-06-14).** A unit is NOT anchored in ONE canonical space — it carries a real address in EVERY relevant space at once: structural/provenance (`unit∈session∈project`, `exchange://`), semantic (embedding position, per-lens), temporal (ts/recency), **PHYSICAL** (the filesystem path, when the thing is/produced a file — "it would also have a physical location, like if it was a file"), relational (the link graph), + others as relevant. **Being multiply-located IS the value** — Tim verbatim: "having an address in more than one space is one of the valuable things, that's how you can find something in other spaces" (find via any space → cross to the others). The unified coordinate lattice is the space these are co-equal SUB-spaces of; the embedding space is ONE of them, NOT the master container. Stable identity hangs on the incorruptible provenance/id (semantic coords drift on re-embed; provenance doesn't); the other spaces are addresses attached to that identity. This REFINES the fork/lead "dissolution" (which framed it as one embedding-space with provenance as discrete axes) → genuinely co-equal multiple spaces. **THE GATE IS OPEN — both sessions unblocked to index.** `[tim-direct · CERTAIN]`
- **D-2 · Central judge → BOTH, by mode** (session model for interactive/co-mode ratification; local big model 9B/27B for the unattended lane). Why: extraction-vs-judgment law `[tim-direct]`; "do a lot more with local models" `[tim-direct]`; and he wants the unattended metabolism (introspective-data-building, dream-phase, consolidation = all `tim-direct` design laws) → which *requires* a local judge. `[inferred · HIGH]`
- **D-3 · Build isolation → recollection's own plugin repo, commit-to-main there.** Why: no-branches-company is scoped to `~/company` specifically `[tim-direct memory]`; recollection is a separate clone repo. `[inferred · HIGH]`
- **D-4 · Licensing → use the best regardless of license; non-commercial OK.** Why: Tim, verbatim 2026-06-14: "Using non-commercial stuff is fine. This is experiments." → jina-v3 stays; no commercial-safe swap needed. `[tim-direct · CERTAIN]`
- **D-5 · Lens loadout → interim served pplx-4b now; the full lens-set is the eventual OUTER recollection embedder design; everyday co-resident set ≈10G (steerable-dense + sparse + code + ColGrep), VL swapped in for images, 8B solo deep-pass — a reconfigurable registry DEFAULT, not a lock.** Why: ~15.5GB budget `[tim-direct]`; "bge is one config, not the winner / full lens-set" `[tim-direct]`; make-each-thing-work; D-4 now permits the non-commercial served stack as interim. `[inferred · HIGH]`
- **D-6 · Codex → strip the harness but KEEP/port its `tool_result` parsing onto the Claude path.** Why: immediate target is Claude Code `[tim-direct]`; tool_result is the "what came back" half of the causal story (valued in the P6 design); no-deferral / make-each-thing-work says don't drop the only working parser. `[inferred · HIGH]`
- **D-7 · Distribution → private local plugin** (install from local path; not published). Why: single-origin personal memory; no stated intent to share; absence of any publish signal. `[inferred · MED-HIGH]`
- **D-8 · Refold → build standalone now, absorb into the Company as an explicit later step; portable-by-field.** Why: the Company pgvector backend is unbuilt (reads/2) — don't block on it; the build-map shows absorption = a backend re-point. `[inferred · HIGH]`
- **D-9 · Sidechains → first-class units, pooled into the parent intent/session/project rollup arc.** Why: Tim works almost entirely through agents — "263 = agents under <10 sessions," the fan-out IS the work `[tim-direct]`; Pillar 2 ("know what was built") is unrecoverable without them. `[tim-direct evidence · HIGH]`
- **D-10 · Floor injection → precomputed cached floor, refreshed on deep-pass/ratification** (NOT live-at-SessionStart). Why: avoids re-introducing the SessionStart model-call recursion (build-readiness B-6) + per-session latency; the floor (principles + project state) changes slowly. `[inferred · HIGH, technical/low-risk]`
- **D-11 · `search`/`read` → keep the names, default to the grounded handles-first envelope; raw flood behind an explicit override.** Why: grounded-chain law — "the grounded chain must be the AI's easiest path" `[tim-direct]`; the raw flood is *why the current memory goes unused*. `[tim-direct evidence · HIGH]`
- **D-12 · Capture → (i) re-ingest from `~/.claude/projects` into the fresh schema (NOT read the live old DB); (ii) run recollection as a 4th lane until proven, then retire the 3 legacy lanes.** Why: re-ingest avoids the comingling landmine (build-readiness B-5: env-fallback to the live 11.4GB store) and keeps the old DB untouched; run-as-4th avoids disrupting Tim's live SessionEnd→Supabase sync mid-build (don't-strand-work). `[inferred · MED-HIGH]`
- **D-13 · "Merge two projects" → inventory-for-the-agent** (recollection produces the MATCHED/build-list/debt-list across the two; an agent does the merge). Why: not-agent-architecture-by-default — "LLM use defaults to dataflow/content, not agent-action" `[tim-direct]`; recollection is memory, not an actor; the questionless-sweep produces the inventory. `[inferred · HIGH]`
- **D-14 · Modalities → images NOW (already in the CC stream — buildable immediately, and Tim's design work is image-heavy); voice(STT)+documents sequenced as explicit later units; the visual lens must NOT sit as a dead registry row.** Why: build-readiness (images in-stream); no-deferral but pragmatic sequencing; "looks-covered-isn't" is the worst state. `[inferred · MED-HIGH]`
- **D-15 · Deep-hole growth law → build the SENSOR now (detect units that won't classify); SURFACE candidates for Tim to name/ratify — Tim-gated, no auto-create.** Why: it's the ontology growing = the same no-fiction-about-Tim caution as principles `[tim-direct law]`. NOTE: derivation-4 itself (the growth-law concept) was flagged as MY extrapolation awaiting Tim's fit-test — so the *sensor* is the safe, grounded build; the auto-create stays gated until he confirms the concept. `[inferred · MED — concept pending Tim's fit-test]`
- **PREF/IDENTITY OWNERSHIP → recollection owns the ONE unified layer; ALL sessions FEED it (Tim-direct, 2026-06-14).** Tim verbatim: "sure that can be the owner, but everyone needs to be looking — you all have histories with me. It's for now as well as something to be built." So: recollection (outer) owns the single unified preference/identity layer; but the signal is gathered from EVERY session — each has its own accumulated history with Tim, and that is all signal (the one-entity law: all sessions feed one identity, not just the fork). TWO timeframes: it works NOW (every session draws on its Tim-history immediately, before the full build) AND the proper unified layer is built. Gated no-misremember-Tim. `[tim-direct · CERTAIN]`

**Confidence summary:** HIGH/CERTAIN on D-1,D-2,D-3,D-4,D-5,D-6,D-8,D-9,D-10,D-11,D-13 + PREF-OWNERSHIP. MED-HIGH on D-7,D-12,D-14. MED (concept-pending) on D-15. None were pure-taste-with-zero-signal.

**★ BOTH-PLUS-OTHERS rule (Tim, 2026-06-14, now standing — [[feedback-both-plus-others]]):** any either/or should first be tested for "both + others" — the binary is usually false. Retro-sweep of the above: D-1 → multi-space (both+others). D-7 → both-across-time (private now, publishable later). D-13 → both-across-time (inventory now, assisted-merge as a later mode of the same thing). D-2/D-5/D-6/D-14/D-15 were already composed/both. Grounded in Tim's own "it's for now as well as something to be built."

**★ OPERATIVE APPROVAL STANDARD (Tim-direct to the lead via AskUserQuestion, 2026-06-14; committed `~/company/channel-memory/mega-prep/APPROVAL-STANDARD.md` 94ca745):** self-approve any CONSEQUENTIAL action that is git-revertible + cross-reviewed via **high-bar recorded-intent recovery**; ping lead→Tim only for truly-irreversible/external (external sends/pushes, non-recoverable deletes, spend past threshold, outside-repo, Tim's accounts). **HIGH-BAR CONDITION (keystone): recovery quality GATES autonomy** — must be pattern-level across time AND projects, structure-not-text, NOT shallow grep (this session's early failures = negative examples); low-confidence recovery → ping, don't self-approve. **This condition IS recollection's Pillar-1 done rigorously** — so building recollection well is what makes the fabric's self-approval safe; recovery quality is the safety mechanism. recollection's build self-approves against the loop-prep itself (the rigorous, pattern-level recorded intent).

## DECISIONS NEEDED (original option detail — retained for reference; all now resolved above)

### D-1 · Address grammar — geometric vs provenance (vs both)
**Why open:** the plan (P1) says units carry addresses "up and across" but never defines what an address IS. The sibling SEED docs supply a geometric model: a recursive box-position (quadtree/Morton path) where **radius = relevance-from-now, angle = relation-type, scale = n**. The plan's working model is provenance-based: `exchange://<sid>/<i>` + `cwd→project`.
**Options:**
- (a) **Provenance address, lattice as a projection** (my lean) — keep `exchange://`+cwd as the canonical address/identity, and treat the geometric lattice as a *render/health* projection computed from it. Lowest risk, both pillars work, the geometry is available where it helps (the health-scan, navigation) without being load-bearing for identity.
- (b) **Geometric address as canonical** — adopt the quadtree/radius/angle/scale model as the primary address grammar. More powerful/unified, bigger commitment, less proven.
- (c) **Both first-class** — maintain both grammars natively.

### D-2 · The central judge — session model vs dedicated local big model
**Why open:** extraction-vs-judgment law = workers (the 4B swarm) extract, a central layer judges relationally. What model fills the *central judge* seat for the heavy judgments (supersession, set-curation, principle-ratification)?
**⚠ THE CONSEQUENCE (Wave-3, the real question):** if D-2 = session-model-ONLY, then the entire **unattended lane cannot run when no session is active** — the dream-phase/consolidation (G9.2), the questionless sweeps (G5.3), and background ratification (G2.4) all silently can't happen. So D-2 is really: **do you want unattended memory metabolism at all?** If yes → a local big judge is *required, not optional*.
**Options:**
- (a) **The session model only** (me / the driving CC agent via MCP) — strongest reasoning, zero extra VRAM — but NO unattended metabolism (memory only improves while you're working).
- (b) **A dedicated local big model** (9B/27B/35B) — always available, runs the unattended lane on-card.
- (c) **Both, by context** (my lean) — session model for interactive/co-mode ratification; local big model for the unattended lane. Same role, model bound by mode (registry slot). This is the only option that delivers unattended metabolism AND top-tier interactive judgment.

### D-3 · Build isolation — branch+worktree vs commit-to-main
**Why open:** default is commit-to-main (no-branches law). The concurrent-cognition build took an explicit branch+worktree override. recollection is a clone-as-sibling *plugin* (its own repo/dir, mostly outside ~/company), so the no-branches-in-company law may not even apply to it.
**Options:**
- (a) **Its own plugin repo, commit-to-main there** (my lean) — recollection lives in its own dir (the clone), so it has its own git; commit to its main; the no-branches-company law is about ~/company specifically and doesn't bind a separate plugin repo.
- (b) **Branch+worktree** like concurrent-cognition — if you want the autonomous loop isolated from a working copy you're also using.

### D-4 · Licensing stance for the build (light — confirm)
**Why open:** you said "forget licensing" during model *consideration* — but the design-truth wave flagged that the **jina reranker/embedders are CC-BY-NC (non-commercial)**, and recollection is meant to be absorbable into the (commercial) Company. So "forget licensing" for exploring ≠ "ship non-commercial in the product path."
**Options:**
- (a) **Commercial-safe only in the production path** (my lean) — use jina etc. for benchmarking/comparison, but the shipped lenses/rerankers are permissively-licensed (ms-marco, bge, qwen, nomic, pplx, granite all are). Non-commercial models stay as eval reference.
- (b) **Forget licensing entirely** — use whatever is best regardless; treat licensing as a later problem.

### D-5 · Lens loadout — which embedders co-reside
**Why open:** P2 chose the full lens-SET (no winner), but ~15.5 GB means not all load at once. Which lenses are the standing co-resident everyday set vs which run only on deep-passes?
**Options:** (my lean) everyday co-resident = steerable-dense (qwen3-embed 0.6B ~1.5G) + sparse (bge-m3 ~1.7G) + code (nomic-code ~6.5G) + ColGrep (CPU) ≈ ~10G, with VL-2B (~4.5G) swapped in when images are in play; the 8B embedder is solo deep-pass only. But the exact standing set is a config/registry call — and per registry-is-truth it's reconfigurable, so this is a *default*, not a lock.

### D-6 · Codex harness — keep or drop
**Why open:** the upstream v1.4.2 the clone is based on supports Codex as a first-class harness (since 1.3.0), not just Claude Code. recollection's immediate target is Claude Code.
**⚠ Wave-3 catch:** the **Codex parser path is the ONLY one that captures `tool_result`** (the Claude path leaves it 100% NULL — a discarded TODO). So a clean Codex strip *loses the only working tool_result capture*.
**Options:** (a) **strip the Codex harness but KEEP/port its `tool_result` parsing onto the Claude path** (my lean — simpler harness, and finally fills the empty result axis) · (b) keep Codex whole · (c) strip Codex and leave tool_result NULL (only viable if tool_results stay purely lazy/keyed and we accept the Claude archive never had them).

### D-7 · Distribution — marketplace-publish vs private sibling
**Why open:** recollection is a clone-as-sibling plugin. Is it published to a marketplace (like the original) or kept a private local plugin?
**Options:** (a) **private local plugin** (my lean — it's yours, single-origin, no reason to publish; install from local path) · (b) publish (only if you ever want it shareable).

### D-8 · Standalone→absorbed MCP refold — timing
**Why open:** recollection is standalone-first but built absorbable into the Company. When does its MCP/store fold into the Company's (store backend re-point, MCP verbs merged into the company face)?
**Options:** (a) **build standalone now, refold as an explicit later step** (my lean — don't block the build on the Company's pgvector backend that doesn't exist yet; write portable-by-field so absorption is a re-point not a rewrite) · (b) build Company-seeded from day one (couples to unbuilt Company backend).

### D-9 · Sidechain placement in the graph (Pillar-2-critical) ★
**Why open:** your actual work happens in agent sidechains. They're captured+embedded, but where do sidechain exchanges sit in the unit/link graph, and **do rollups pool them into the parent session's arc?** This decides whether your real work shows up in the omniscience pillar at all. (Also: the real exclusion is a `is_sidechain=0` filter in `search.ts`, not capture — a build-fix, not a decision.)
**Options:** (a) **sidechains are first-class units linked to their parent intent, and rollups pool them into the session/project arc** (my lean — it's where the building happened) · (b) sidechains captured but kept separate (recall them only on explicit ask).

### D-10 · Floor injection — precomputed-cached vs live-at-SessionStart
**Why open:** G8.1 injects the "floor" (your principles + project state) at session start. Doing it *live* re-introduces a SessionStart model-call — the exact recursion the design just removed — plus latency on every session.
**Options:** (a) **precomputed cached floor artifact, refreshed on deep-pass/ratification** (my lean — no per-session model call, instant) · (b) live-computed each session start (fresh, but slower + recursion risk).

### D-11 · `search`/`read` — grounded default or keep the raw flood first-class
**Why open:** keeping the `search`/`read` tool names (drop-in requirement) also re-exposes the blunt, ungrounded, flood-the-context path as a first-class verb — which undercuts the grounded-chain law (the grounded path should be the *easiest* path).
**Options:** (a) **keep the names but default them to the grounded handles-first envelope; raw flood only behind an explicit override flag** (my lean) · (b) keep `search`/`read` as the literal old behaviour (drop-in fidelity, but the easy path is the ungrounded one).

### D-12 · Capture migration & legacy lanes
**Why open:** two linked choices. (i) Backfill source: re-ingest from `~/.claude/projects` into the fresh schema, or read the live 11.4 GB episodic DB? (ii) The 3 existing lanes (episodic hook · your SessionEnd→Supabase sync · lobe-importer) — retire now, or run recollection as a 4th until absorption?
**Options:** (i) **re-ingest from `~/.claude/projects`** (my lean — clean, into the new schema; the old DB stays untouched) vs read live DB (faster, but couples to the old store). (ii) **run as a 4th lane until proven, then retire the others** (my lean — don't disrupt your live Supabase sync mid-build) vs retire-now.

### D-13 · "Merge two projects" — scope
**Why open:** G10.3 promises "merge these two projects," which blurs two very different things.
**Options:** (a) **inventory-for-the-agent** — recollection produces the MATCHED/build-list/debt-list across the two projects and an agent does the merge (my lean — recollection informs, doesn't act) · (b) **assisted-merge operation** — recollection drives the merge itself (much bigger, agentic).

### D-14 · Non-CC modality sequencing
**Why open:** P9/P10 decided modalities (code/images/docs/voice) but there are no criteria and no sequence. Risk: the visual lens sits as a registry row with no use — "looks covered, isn't."
**Options:** (a) **images now** (they're already in the CC stream — buildable immediately), **voice (STT) + documents sequenced as explicit later units** (my lean) · (b) all modalities deferred until core is proven · (c) all modalities in the first build.

### D-15 · Derivation-4 (new types born at deep holes) — the growth law
**Why open:** the stated growth law (units that won't classify → a missing type). Build the *sensor* (detect deep-hole residents) now? And does it auto-create the new type or surface it for you?
**Options:** (a) **build the sensor now; surface candidates for Tim to name/ratify (Tim-gated auto-create)** (my lean — it's the ontology growing; same no-fiction caution as principles) · (b) sensor only, no auto-create · (c) defer the whole growth law.

*(Decisions D-1…D-15 are the full set for Tim's one-pass answer. Builder-level items I resolved are in the RESOLVED section.)*

---

## RESOLVED BY ME — FYI, no action needed (kept off the decision list)

- **C3 · Pre-compaction snapshot** — DROPPED. CONVERGENCE der.10 said snapshot before compaction; you explicitly dropped it in P8-D2 ("the memory IS the continuity"). Plan wins; build no snapshot.
- **C1/C2 · Stale text** — the loop-prep docs will cite the CORRECTED positions: provenance anchoring is LINK-not-embed (P6, not der.8's "embed quotes"); bge-m3 is NOT the unify-target (MERGE-INTENTION's "unify on bge-m3" is superseded; bge-m3 has zero priority).
- **Questionless-sweep lane (G2)** — ADDED as a first-class component. Pillar 2's broad ops ("merge two projects," inventory, orphan/residue sweep) need sweeps that emit findings *unasked* — a class query-time gather (P3) can't produce. Added to the design (de-risked by the other session's 940→483 overnight RG10 proof).
- **No-fiction-about-Tim / asymmetry law (G4)** — RECORDED as a hard constraint on principle records: the memory must never misremember Tim (the worst available corruption); this is the reason P5's ratification gate exists.
- **Multi-vector code lens (G5)** — RECORDED as a build constraint: LateOn/ColGrep keep their OWN index outside the single-column store (already known from P2/reads; now a hard build note).
- **nomic-code ops trap** — RECORDED: `--pooling last` + query-prefix or it fails silently (registry law).
- **Reuse the concurrent-cognition rules engine for memory return-conditions (C4)** — build P8's conditions *rules-shaped* now (standalone can't reach the Company engine yet) so they drop onto it at absorption. Recorded as a build directive.
- **Clone-base dispositions (build-map)** — KEEP the plugin chassis + capture-incrementality + exchanges/tool_calls atom tables + additive-ALTER migration + read/render + re-embed engine + the `search`/`read` tool names. MODIFY paths→`~/.recollection` (survive updates), include sidechains, demote the hardcoded FLOAT[384] to one lens, pluggable source registry. REPLACE in-process ONNX embeddings → fabric multi-lens; cloud-SDK summarizer → local resident-4B distill (also kills the SessionStart recursion); flat KNN → the gather+judge machine.
- **Three build-map corrections (baked into the map):** (a) substrate-mcp's `embeddings.py` is NOT in the repo — the harvestable `OpenAIEmbedder` survives only in CC file-history (`~/.claude/file-history/bda8ce28-.../ae22f5e848708178@v2`); (b) CI's provenance tables are `indexed_artifacts` / `artifact_provenance` (not `ci_`-prefixed); (c) CI has 5 parametric tools (20260210 migration) + `ci_issues` as the 6th (20260211).
- **Wave-3 build-readiness fixes (→ GUIDE, see wave3-build-readiness-audit.md):** sidechain exclusion is `is_sidechain=0` in `search.ts:165/188` NOT capture (fix the filter, not the sweep); the MCP server runs from committed `dist/` so the build loop MUST `npm run build` before every verify; renaming env vars REQUIRES updating `.mcp.json`'s env allowlist (else silent fallback to the live ~/.config/superpowers store — comingling); `vec_exchanges FLOAT[384]` dim is a vec0 REBUILD not an ALTER (per-lens `CREATE VIRTUAL TABLE vec_<lens>`); lazy `tool_result` = re-read source JSONL via `show.ts`, NOT query `tool_calls.tool_result` (NULL); add a `tool_input.file_path` index for the crossing join; `~120 concurrent` must be `SlotBudget.from_registry`, not hardcoded; the summarizer REPLACE must preserve the hierarchical/resume/sentinel paths; the mcp-server is a near-total rewrite despite keeping the `search`/`read` names; 38 tests need a refit policy.
- **ND-1 vec 384** → RETIRE it for a clean fabric re-embed (re-embed-refusal law: old 384 vectors aren't reusable); per-lens vec tables.
- **ND-2 G2.1 backfill** → prove on a SAMPLE + schedule the full sweep; don't block the criterion on a full-corpus 4B compute run (it's real net-new compute, ~1,286 of 13k summaries exist today).
- **Retrieval-completeness (A3/D-NEW-3)** → CRITERIA fix: pooled results carry a coverage/confidence verdict + a ground-set recall proof (no-silent-failure applied to recall). Done in COMPLETION_CRITERIA G5/G11.
- **Wave-3 criteria-hardening (→ CRITERIA, see wave3-design-audit.md):** A1 scale edge-graph criterion, A2 panel switch-flip (grounded in tim_correction), A4 grounded-is-easiest + fresh-agent-drives-task (B5), A6 tool_result round-trip, and a new G11 law-floors group (reject >5-bin classification · reject inverse-less edge · test the no-fiction ABSTENTION path · worker-can't-emit-verdict membrane · per-step context-package). Folded into COMPLETION_CRITERIA.
