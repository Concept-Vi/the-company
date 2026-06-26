# Seam Mapping — INNER (fork session-recall) nests in OUTER (recollection)

```
trust: fabric-derived (both plans + the fork's built code, read this session)
author: mapping pass for the UNIFIED SEAM document (multi-session mega-prep)
date: 2026-06-14
purpose: make the nesting precise so all sessions build to ONE spec. The convergence is LOCKED
         (Round 7, channel-memory RESEARCH-SYNTHESIS; OPEN-DECISIONS ★ RESOLVED). This doc keys
         each fork component to its outer correspondent, defines the boundary, and resolves
         every conflict + names every gap with the change EACH side makes.
evidence: Observed = read directly in code/plan this session · Inferred = pattern-matched, labelled.
sources:
  INNER (fork): /home/tim/company/channel-memory/plan/{COMPLETION-CRITERIA,IMPLEMENTATION-GUIDE,RESEARCH-SYNTHESIS,INFERRED-PREFERENCES}.md
                + built code runtime/session_{scan,recall,lens}.py (read) + channel-memory/design/lead-lane-inputs.md
  OUTER (recollection): /home/tim/company/build-prep/episodic-memory-adaptation/loop-prep/{COMPLETION_CRITERIA,IMPLEMENTATION_GUIDE,RESEARCH_SYNTHESIS,OPEN-DECISIONS}.md
```

---

## 0. The shape of the nesting (read this first — it is ASYMMETRIC)

The fork is **NOT a miniature recollection.** It is the inner **single-session instance of recollection's RETRIEVAL SPINE only**:

```
            capture → embed → gather → judge → recall-surface
recollection: G1   →  G3   →  G5    →  G6   →  G7              ← the OUTER spine (all sessions)
fork:        scan  → recall →(lenses)→ panel → lens API        ← the INNER spine (one session)
```

recollection then **WRAPS that spine** with layers the single-session case has no instance of:
- **G2 distill / rollups** — manufacture L1/L2/L3 memories across sessions (no fork analogue; one session has nothing to roll up).
- **G4 link / provenance graph** — artefact↔conversation crossings + cross-project concept-sameness (the fork keys a single transcript path only; no cross-anything graph).
- **G8 proactive injection (Layer-2)** — SessionStart floor + in-session hooks (fork has no injection layer).
- **G9 health / annealing** — corpus temperature + dream-phase (a single session has no corpus to anneal).
- **Pillar-1 unified identity layer (G10.2)** — the fork FEEDS it (3.7) but does not own/host it.

**Stated precisely:** the fork OWNS the *working concrete instance of the retrieval spine for one session*; recollection OWNS *the data model the spine writes into, the cross-session/cross-project layers, and the identity layer*. The fork's served stack is "the concrete working instance of recollection's abstract slots" (fork RESEARCH-SYNTHESIS Round 7, Observed). Everything below makes that exact.

---

## 1. Component-by-component correspondence

Each row: fork component (+ where) ↔ recollection part it is the inner/single-session case of (+ where) · tag.

| # | FORK component (INNER) | cite | recollection part (OUTER) it is the single-session case of | cite | tag |
|---|---|---|---|---|---|
| C1 | **session_scan** — structural scan → projectable rows (`line/uuid/parent/ts/type/role/attr/model/is_boundary/boundary_point`; summary carries `source_bytes/scanned_at`); inject/tool/compaction filter, dense profile, gaps | fork CC §1.1–1.2, RS R1; code `scan_session()` returns `{summary,rows}` | **Capture → atoms** (one session's exchanges as the lowest unit `atom{type,session_id,project,ts,exchange_ref,raw_ref}`) + the **structural address** half of G0.3 | OUTER G1.1/G1.3, G0.2 (`atoms`), Guide §1–§2 | Observed (row keys + summary fields read in `session_scan.py` L182–196) |
| C2 | **dimension-aware chunking** — split a turn on its OWN structure so each dimension is a retrievable unit; parent {line,ts,attr} preserved | fork CC G1, Guide §1; code `_split()`/`session_chunks()` (today: 700-char overlap, dimension-aware = [D]) | the **unit-grain decision** feeding fingerprints — recollection's `units` + the per-block decompose in Gather Pass2 (sentence-grain) | OUTER G0.2 (`units`), Guide §6 Pass2 (sentence-grain decompose) | Observed (fork: `_split` read; recollection: Guide §6 Pass2) |
| C3 | **session_recall** — embed (:8007 pplx-4b documents-mode, 2560-d cosine) + served rerank (:8008 jina-v3 CPU), fail-loud, build-once index | fork CC G2, RS R1–R2; code `_embed_documents/_rerank_endpoint/recall()` | **Embed/lenses (one lens)** + **proofreader (the always-on CPU reranker)** | OUTER G3.1 (one fabric lens), G6.1 (proofreader CPU), Guide §4/§7 | Observed (HTTP contract + cosine + rerank read in `session_recall.py`) |
| C4 | **the lens family** — find / decisions / open_loops / catch_up / timeline / directives / spin_up_points | fork CC G3.1–3.8; code `session_lens.py` `LENSES` dict | **Gather modes + recall surfaces** — top-k precise (`find`), pooled-arc (`timeline`), axis-addressed tools (`the_arc_of`, `whats_my_position_on`); lenses = the single-session shapes of recollection's parametric tool registry | OUTER G5.2 (two modes), G7.1 (axis-addressed tools), Guide §6/§8 | Observed (lens fns read); mapping of each lens→tool is Inferred (shapes correspond; names differ) |
| C5 | **3.2 decisions + the generic-pinpoint gap** | fork CC G3.2, INFERRED Q7 | **Gather + Judge** answering "what's the decision" — the gap is closed by the panel (C6), = recollection's judge re-ordering a noisy region | OUTER G6.1 (set-reader re-orders), G6.2 (jury rules answers-vs-mentions) | Observed (gap stated fork CC G3.2); resolution = Inferred-aligned |
| C6 | **Group-4 retrieve→synthesize PANEL** — concurrent structured facet-extractors (chosen/alternatives/reason/constraints/owner) on chat-4b/08b → ONE smart-model judge; built ON `runtime/cognition.py` roles (`run_role`+concurrency+`json=True`), NOT new infra | fork CC G4, Guide §4, RS R4, lead-lane §D | **The Judge layer** (extraction-vs-judgment): fan-out workers extract observations, central judge decides; an OPEN registry of judgment-types; verdicts typed+self-explaining | OUTER G6.1–6.3, G11.4 (worker-can't-judge membrane), Guide §7, D-2 | Observed (cognition.py existence + roles split confirmed by lead-lane §D, verified-this-session); panel-as-judge-instance Inferred |
| C7 | **3.7 requirements/preferences lens (ANTI-RECENCY)** — reads `feedback-*` corpus FIRST, layers session Tim-signal, weights by repetition not recency | fork CC G3.7, Guide §3.7, INFERRED Q3, RS R6/R7 | **Pillar-1 unified identity layer** — the fork is the INNER/session contributor that FEEDS it; recollection OWNS the one layer; ALL sessions feed | OUTER G10.2/G10.2★ (switch-flip panel), PREF/IDENTITY-OWNERSHIP decision, Guide §8d floor | Observed (convergence stated verbatim fork CC G3.7 + RS R7 + recollection PREF-OWNERSHIP) |
| C8 | **Group 6 — project·session·segment addressing** (`session://<project>/<sid>` + scope selector; one embedder space; HARD GATE) | fork CC G6, lead-lane §B, INFERRED Q5 | **D-1 MULTI-SPACE addressing** — project·session·segment become the **structural/provenance axes** (one of several co-equal spaces), inside G0.3 address grammar | OUTER D-1 (★RESOLVED, tim-direct·CERTAIN), G0.3, Guide §1 | Observed (D-1 text explicitly subsumes the project·session·segment keys) |
| C9 | **Group 5 — channel context-attachment** (manifest {sessions,docs,recall_scope}; load-on-join; `cc_channel op=recall`) | fork CC G5, lead-lane §A/§C, INFERRED Q4 | **No direct outer correspondent in recollection's spine** — channels are the fork/lead's *delivery surface*; recollection's analogue is G7 recall-surfaces + G8 injection (load-on-join ≈ floor-injection). Channels CONSUME recollection's recall; they are not part of its data model | OUTER G7/G8 (consumer side only) | Inferred (channels are a fork/lead lane; recollection treats them as a recall *consumer*, not an owned layer) |
| C10 | **Group 7 — projection to The Heart** (scan/lens/brief as DATA → Company UI projects it) | fork CC G7, vision §1.9 | **Operator surfaces (FORM bar)** — recollection's health-map / ratification surface; both defer to Tim's UI pointer | OUTER FORM-bar(3), G9.1 surface | Observed (both Tim-gated/FAR) |
| C11 | **Group 8 + lens 3.8 — spin-up / fork-fleet** (rank fork-points, uuid-cut probe, fleet launch) | fork CC G8, G3.8; code `spin_up_points()` | **NO outer correspondent** — session-splicing is orthogonal to cross-session MEMORY | — | Observed (recollection has no fork-fleet component) — see §3 GAP-3 |
| C12 | **INFERRED-PREFERENCES doc** (proposed answers to fork's open Qs, get-a-feel method) | fork INFERRED-PREFERENCES Q1–Q7 | **OPEN-DECISIONS** (recollection's D-1…D-15 + RESOLVED) — same instrument, outer scope; several fork Qs are pre-answered by resolved Ds (see §4) | OUTER OPEN-DECISIONS | Observed (both are "propose→Tim reacts" ledgers) |

**Cleanest correspondences (highest confidence, both sides cited, Observed):**
- **C3** session_recall ↔ G3.1 one-lens + **G6.1 proofreader** — the fork's served :8007/:8008 *is* recollection's interim embed-lens + always-on CPU reranker.
- **C6** the panel ↔ G6 Judge — same law (extraction-vs-judgment), same engine family (cognition.py roles), confirmed by lead-lane §D this session.
- **C7** 3.7 preferences ↔ Pillar-1 — explicitly converged: the fork FEEDS, recollection OWNS, all sessions feed.
- **C8** project·session·segment ↔ D-1 structural axes — D-1's text literally absorbs the fork's keys as the provenance sub-space.

---

## 2. The nesting — ownership + the boundary interface

### What the FORK OWNS (the inner single-session retrieval spine)
- **The recall/lens lane** — `session_recall.py` (embed+cosine+rerank+index) and `session_lens.py` (the lens family), keyed to ONE transcript path. [Observed: code]
- **The served :8007 / :8008 stack as the concrete instance** — pplx-4b documents-mode embed (:8007) + jina-v3 CPU rerank (:8008), bridge-free, fail-loud. The working hardware/HTTP reality recollection's abstract slots resolve to. [Observed: RS R2 + code]
- **session_scan** — the structural scan + projectable rows + freshness-stamp fields (`source_bytes/scanned_at`). [Observed]
- **The Group-4 panel roles/chain** — NEW facet-extract + judge roles on `cognition.py` (new roles, not new infra). [Observed: lead-lane §D]
- **Group 8 fork-fleet + 3.8 spin-up ranking** — entirely fork-owned, no outer nesting (§3 GAP-3).

### What recollection OWNS (the outer cross-session container)
- **The data model** — `atoms/units/links/fingerprints/verdicts/candidates` tables, portable-by-field, fail-loud lineage. The fork's scan rows are written INTO this; the fork does not own a schema. [Observed: Guide §1, G0.2]
- **Multi-space addressing (D-1)** — the unified coordinate lattice of co-equal sub-spaces (provenance/semantic/temporal/PHYSICAL/relational); the fork's project·session·segment are the structural axes within it. [Observed: D-1]
- **Distill / rollups (G2)** — L1/L2/L3, the principle-ratification gate. No fork instance.
- **Link / provenance graph (G4)** — crossings + cross-project concept edges + lazy tool_results.
- **The unified identity/preference layer (Pillar-1)** — recollection owns the ONE layer; ALL sessions feed; gated no-fiction-about-Tim. [Observed: PREF-OWNERSHIP decision]
- **Capture of ALL sessions incl. sidechains + backfill (G1)** — the fork captures one session; recollection captures the whole archive (~13,270 convs + `agent-*.jsonl`). [Observed: G1.1/G1.2, D-9]
- **Health/annealing (G9) + proactive injection (G8).**

### THE BOUNDARY INTERFACE — exactly FOUR wires cross inner↔outer

```
  FORK (INNER)                         WIRE                          recollection (OUTER)
  ─────────────                        ────                          ────────────────────
1 session_scan rows  ───────────────►  scan rows → capture atoms  ──► G1/G0.2 atoms (one session's worth)
2 project·session·   ───────────────►  scope keys → structural    ──► D-1 multi-space addressing
  segment keys                          axes inside multi-space         (the provenance sub-space)
3 served :8007 embed ◄──────────────►  HTTP embed+rerank contract ──► G3 interim embed-lens (D-5)
  + :8008 rerank                        (EMBED_URL / RERANK_URL)        + G6.1 proofreader
4 3.7 preference     ───────────────►  session Tim-signal → feeds ──► Pillar-1 identity layer
  profile payload                       the owned identity layer        (recollection owns; all feed)
```

1. **scan rows → capture atoms.** The fork's `{line/ts/attr/model/boundary_point,…}` row contract (Observed in `session_scan.py`) is the single-session shape of recollection's `atom`/`unit` rows (Guide §1). At absorption, scan becomes one `capture_source` row writing into `atoms`. The freshness fields (`source_bytes/scanned_at`) are the stamp recollection's incremental/high-water-mark capture (G1.2 FORM) reuses.
2. **scope keys → structural axis-set.** `session://<project>/<sid>` + `{scope: project|session|segment|all}` (lead-lane §B) ARE the addresses on recollection's structural/provenance sub-space (D-1). The fork computes them per-session; recollection holds them as one axis-set of the lattice. (Project key = encoded `~/.claude/projects/<cwd>/` dir, resolve-by-re-encode — Observed lead-lane §B.)
3. **served HTTP contract.** `EMBED_URL=:8007/v1/embeddings` (documents-mode, pplx-4b, 2560-d) and `RERANK_URL=:8008/rerank` (jina-v3 CPU) — both env-configurable (Observed `session_recall.py` L33–38). This is the wire recollection plugs into as its **interim embed-lens (D-5)** and **proofreader (G6.1)**. Because the URLs are env-driven, absorption into recollection's fabric `:8001` multi-lens is a config re-point, NOT a rebuild.
4. **preference payload → Pillar-1.** The fork's 3.7 profile (feedback-* primary + session-supplement, anti-recency) is emitted as the channel-load payload (fork 5.3) AND fed into recollection's owned identity layer. recollection judges/ratifies; the fork supplies one session's signal. ALL sessions feed the same wire.

---

## 3. ALIGN / CONFLICT / GAP

### ALIGN (both plans say the same thing — build once)
- **A1 · Extraction-vs-judgment.** Fork G4/panel = recollection G6/Judge: small models extract structured facets, a central smart model judges; workers never decide (fork Guide §4 ↔ OUTER G11.4 membrane). Identical law, identical engine family (cognition.py roles). [Observed both]
- **A2 · No parallel memory system.** Fork principle-2 / RS R7 ("NO parallel memory system across forks") = recollection Guide §0 / D-12 (unify into one capture path, not a 4th lane). [Observed both]
- **A3 · Fail-loud, no silent fallback.** Fork G2.3 (teaching error + declared degradation) = recollection's no-silent-failure (G5.2★, Guide §0). [Observed both]
- **A4 · Anti-recency identity = the feedback-* corpus.** Fork 3.7/Q3 ↔ recollection Pillar-1 + no-fiction gate. Converged. [Observed both]
- **A5 · One embedder space per index / golden rule.** Fork G6.2 + lead-lane §B ("never mix spaces") = recollection G3.4 ("same model per space, no mismatch") + B-7 (per-lens vec table). [Observed both]
- **A6 · Grounded result, handles-not-flood.** Fork's lens APIs return handles (line/ts/attr/score) ↔ recollection D-11 / G7.1 handles-first envelope + grounded-chain law. [Observed both]
- **A7 · Registry-is-truth / no-hardcoding.** Fork G4.3 facet registry + lead-lane cross-cutting ↔ recollection Guide §0 + every FORM bar. [Observed both]

### CONFLICT (the two plans diverge — winner named, with the change EACH side makes)

- **K1 · Reranker license — the sharpest, and there is an internal recollection contradiction to surface.**
  - Fork **2.2** hedges: "jina-v3 = CC-BY-NC → for any commercial/production path swap to a permissive reranker (ms-marco)." [Observed fork CC G2.2]
  - recollection **Guide §7** says: "ms-marco reranker (CPU) for the proofreader. ⚠ jina reranker = non-commercial (D-4) → eval only." [Observed Guide §7]
  - **BUT recollection's own resolved D-4** (tim-direct·CERTAIN, 2026-06-14, the LATER authority): "use the best regardless of license; non-commercial OK. … jina-v3 stays; no commercial-safe swap needed." [Observed OPEN-DECISIONS D-4]
  - **WINNER: D-4.** It supersedes BOTH the fork-2.2 hedge AND recollection's own Guide §7 "ms-marco / jina eval-only" line (Guide §7 is stale relative to the resolved decision).
  - **Change the fork makes:** drop the 2.2 "swap for commercial" hedge; jina-v3 :8008 stays the production reranker. (The env-configurability stays as a *capability*, not a *mandate*.)
  - **Change recollection makes:** the seam doc must flag **Guide §7's "ms-marco for proofreader / jina eval-only" line as superseded by D-4** → **jina-v3 :8008 IS recollection's proofreader (G6.1)**, not eval-only. ms-marco becomes an optional registry alternative, not the default.

- **K2 · Address grammar — embedding-as-master vs co-equal multi-space.**
  - Fork frames it: "the embedding index IS already a 2560-d lattice → hierarchy is a DISCRETE-AXIS SLICE of the lattice … lattice-with-hierarchy-as-axes" — embedding space is the master container. [Observed fork CC G6 ★GATE + RS R7]
  - recollection **D-1** explicitly REFINES/supersedes this: "the embedding space is ONE of them, NOT the master container … genuinely co-equal multiple spaces. Stable identity hangs on the incorruptible provenance/id (semantic coords drift on re-embed; provenance doesn't)." D-1 names the fork/lead "dissolution" by name as the thing it refines. [Observed OPEN-DECISIONS D-1]
  - **WINNER: D-1** (tim-direct·CERTAIN, later authority, explicitly addresses the fork's framing).
  - **Change the fork makes:** the canonical address/identity becomes `exchange://<sid>/<i>` + cwd→project (provenance, incorruptible), NOT the embedding lattice; the embedding lattice becomes ONE co-equal sub-space among provenance/temporal/physical/relational. The fork's project·session·segment keys remain valid — but as the *structural* sub-space, not "axes of the master embedding lattice."
  - **Change recollection makes:** none — D-1 already states the resolved position; the seam doc just records that the fork's RS R7 lattice-as-master language is now superseded.

- **K3 · Embed transport — :8007 pplx-4b single-lens vs fabric :8001 multi-lens (SOFT — dissolved, not won).**
  - Fork: served :8007 pplx-4b documents-mode, 2560-d, the ONE embedder. [Observed RS R2 + code]
  - recollection Guide §4: fabric `:8001` OpenAI-compatible, registry-driven MULTI-lens (steerable-dense/sparse/code/ColGrep/VL…), no model privileged. [Observed Guide §4, G3.1]
  - **RESOLUTION (not a winner): D-5** dissolves it. D-5: "interim served pplx-4b now; the full lens-set is the eventual OUTER recollection embedder design … a reconfigurable registry DEFAULT, not a lock." The fork's :8007 pplx-4b IS the interim single-lens instance; recollection's multi-lens fabric subsumes it as ONE registry row at absorption (the env-configurable URLs make this a re-point). [Observed D-5]
  - **Change each side makes:** fork — keep pplx-4b as the working interim, do not treat it as final. recollection — register pplx-4b/:8007 as one lens row in the loadout (D-5), with the multi-lens set as the eventual superset.

### GAP (neither plan fully covers — name it so it is not assumed-covered)

- **GAP-1 · Live-session index freshness on a GROWING session.** Fork **2.4** has a concrete, specced guard: compare source `.jsonl` mtime/size vs the index's recorded stamp; rebuild-or-warn (reuses scan's `source_bytes/mtime`). [Observed fork Guide §2.4 — but status [D], unbuilt]. recollection has **live-capture G1.3** ("a new exchange appears within the session") but does NOT specify incremental **re-fingerprinting** on a live, still-growing session — its capture is incremental, its EMBED isn't stated to be. **Seam must resolve:** adopt the fork's mtime/size freshness guard as the single-session instance of recollection's live re-fingerprint policy; recollection currently leaves the embed-side freshness implicit. (Owner: shared — fork specs the single-session guard, recollection must say live-embed is incremental too.)

- **GAP-2 · The fork's lenses ≠ recollection's named axis-tools — name-mapping is unspecified.** Fork has `find/decisions/open_loops/catch_up/timeline/directives/spin_up_points`; recollection has `whats_my_position_on/the_arc_of/what_projects_include/when_was_worked_on/what_touched`. The shapes correspond (C4) but **no doc maps lens↔tool**. [Inferred]. **Seam must resolve:** declare which fork lens is the single-session instance of which recollection axis-tool (e.g. `timeline`↔`the_arc_of`; `decisions`+panel↔`whats_my_position_on` for decisions; `open_loops`/`catch_up`/`directives` are session-scoped lenses with NO cross-session tool yet → candidate new recollection tools, or session-only). This is genuinely uncovered.

- **GAP-3 · Spin-up / fork-fleet (fork Group 8 + lens 3.8) has NO outer correspondent.** Session-splicing/cloning is orthogonal to cross-session MEMORY; recollection has no component for it. [Observed]. **Seam must record:** fork-OWNED, no nesting — so it is NOT silently assumed covered by recollection. (It consumes recollection's recall to *rank* fork-points, but the splicing itself is outside the memory system.)

- **GAP-4 · Projection to The Heart (fork Group 7 / vision §1.9) — shared deferral, no owner.** Both plans defer the FORM/UI projection to Tim's UI-session pointer (fork G7 [FAR]; recollection FORM-bar (3) / G9.1). [Observed both]. **Seam must record:** the projection surface is a SHARED downstream deliverable, currently Tim-gated on both sides; the seam doc should not green-paint either side's FORM face until the UI pointer lands.

---

## 4. The resolved decisions' impact on the fork's plan

- **D-1 (MULTI-SPACE) → restructures the fork's Group 6.** The fork's `project·session·segment` keying becomes the **structural/provenance axis-set inside multi-space addressing** — co-equal with the semantic/temporal/physical/relational spaces, not "discrete axes of the master embedding lattice." Identity hangs on `exchange://<sid>/<i>` (incorruptible, re-embed-stable), not on the embedding coords. The fork's GATE language ("nothing indexes until Tim picks lattice-vs-hierarchy") is now **resolved — the gate is OPEN** (D-1: "THE GATE IS OPEN — both sessions unblocked to index"). The fork's RS R7 "lattice-as-master" framing is superseded (see K2). [Observed]

- **D-4 (license: jina-v3 fine, non-commercial OK, tim-direct) → removes the fork's 2.2 hedge AND recollection's Guide-§7 ms-marco default.** jina-v3 :8008 stays the production reranker = recollection's proofreader (G6.1). The fork's "swap to ms-marco for commercial" line is dropped; recollection's "jina eval-only" line is flagged stale (see K1). The env-configurable RERANK_URL stays as a capability, not a forced swap. [Observed]

- **PREF/IDENTITY-OWNERSHIP (recollection owns ONE layer; ALL sessions feed, tim-direct) → fixes the fork's 3.7 as a CONTRIBUTOR, not a layer.** The fork's preferences lens FEEDS recollection's owned identity layer; it is explicitly "NOT a second layer" (fork CC G3.7 verbatim). Two timeframes: it works NOW (every session draws on its Tim-history immediately) AND the unified layer is built. Critically — **ALL sessions feed it, not just the fork** (the one-entity law); the fork is one contributor among all sessions. Gated no-misremember-Tim (recollection's no-fiction gate applies to what the fork feeds). [Observed]

- **(Bonus) D-2 (BOTH-by-mode judge) → confirms the fork's panel judge-seat is mode-bound.** The fork's "chat-nemotron-30B or a cloud seat judges" maps onto D-2: session-model for interactive/co-mode, local big model for the unattended lane. The fork's panel is the interactive instance; recollection adds the unattended judge the single-session case never needs. [Observed D-2 ↔ fork CC G4.4]

- **(Bonus) D-9 (sidechains first-class) → recollection captures what the fork doesn't.** The fork keys a single foreground transcript; recollection's capture pools `agent-*.jsonl` sidechains into the parent arc (D-9). Tim's work happens in sidechains → recollection's omniscience pillar covers what a single-session foreground recall would miss. [Observed]

---

## 5. Summary for the unified seam doc

**Cleanest component correspondences (build-once, both cited, Observed):**
1. **session_recall (:8007 embed + :8008 rerank)** ↔ recollection **G3.1 one-lens + G6.1 proofreader** — the served stack IS recollection's interim embed-lens (D-5) and always-on CPU reranker.
2. **Group-4 panel** ↔ recollection **G6 Judge** — same extraction-vs-judgment law, same `cognition.py` roles engine (lead-verified §D).
3. **3.7 preferences lens** ↔ recollection **Pillar-1** — fork FEEDS, recollection OWNS, all sessions feed.
4. **project·session·segment keys** ↔ recollection **D-1 structural axis-set** — D-1 literally absorbs them as the provenance sub-space.
5. **session_scan rows** ↔ recollection **G1/G0.2 atoms** — one session's capture written into the outer data model.

**The boundary interface = FOUR wires (inner↔outer):**
1. scan rows → capture atoms (one session's G1).
2. project·session·segment keys → structural axes inside D-1 multi-space.
3. served :8007/:8008 HTTP contract (env-configurable) → recollection's interim embed-lens (D-5) + proofreader (G6.1).
4. 3.7 preference profile → Pillar-1 identity layer (recollection owns, all sessions feed).

**Conflicts/gaps the seam doc MUST resolve:**
- **K1 license (sharpest):** D-4 supersedes BOTH the fork's "swap jina→ms-marco" hedge AND recollection's own Guide-§7 "ms-marco/jina-eval-only" line → jina-v3 :8008 IS the proofreader; flag Guide §7 stale.
- **K2 address grammar:** D-1 supersedes the fork's "embedding-lattice-as-master" framing → provenance `exchange://` is canonical identity; embedding is one co-equal sub-space.
- **K3 embed transport (soft):** D-5 dissolves :8007-single vs :8001-multi → pplx-4b is one interim lens row in the multi-lens loadout.
- **GAP-1:** live-session re-fingerprint freshness — fork has the mtime/size guard, recollection leaves live-embed freshness implicit; adopt the fork's guard.
- **GAP-2:** fork-lens ↔ recollection-axis-tool name-map is unspecified — must be declared (some lenses have no cross-session tool yet).
- **GAP-3:** spin-up/fork-fleet is fork-owned with NO outer correspondent — record so it's not assumed covered.
- **GAP-4:** projection to The Heart — shared deferral, Tim-gated both sides; don't green-paint either FORM face.
```
