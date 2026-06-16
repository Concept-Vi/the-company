# COMMON KNOWLEDGE — the prerequisite before any build (the central design base)

*Tim's course-correction (2026-06-16): "you definitely shouldn't be at the point of building it... it would be a GUARANTEED FAILURE if a build happened without full scope on understanding of every project these members are responsible for." A large amount of the company is ALREADY BUILT — but it's NOT everything, and it's NOT necessarily right (built the same way as everything else — [[feedback-confident-not-correct]] applies to the CODE too). No member can know its whole project (too large). So FIRST we design how to use the capabilities to structure all-that's-built into COMMON KNOWLEDGE. The interface BUILD is downstream of this — front-interface/BUILD_PLAN.md is PARKED until common knowledge exists.*

## THE LAW (Tim, this is the gate)
- **SCOUT-BEFORE-BUILD AT PROJECT SCALE.** No build proceeds without full-scope understanding of everything already built in every project a member is responsible for. Building blind over a large, partially-built, not-necessarily-right codebase = guaranteed failure (the exact don't-build-parallel / scout-existing failure, at the whole-company scale).
- **WHAT EXISTS ≠ WHAT'S RIGHT.** The built state is OBSERVED (it exists), not VERIFIED (correct). Common knowledge must map what exists, flag what's incomplete/suspect, and never assume the built thing is right. Confident code is not correct code.
- **NO MEMBER KNOWS ITS WHOLE.** Each project is too large for its session to hold. Common knowledge is built BY THE CAPABILITIES (4B + embedding + substrate), not by a member reading its whole repo — that's why Tim built them.

## THE CAPABILITIES (the tools to compose into common knowledge — Tim: "think together how to use all of them")
- **embedding (:8007 pplx-embed-context-4b, resident)** — semantic index over code + content + transcripts + vaults. Tim wants substrate-mcp RE-INDEXED on this resident model (better than the old bge-m3, makes it resident). One embedder for everything.
- **the local 4B (:8000, tool-calls + structured outputs)** — structured COMPREHENSION: summarize/extract what each module does, what's built vs stub, the shape of each project. "One of the uses for the 4B."
- **substrate-mcp** — already indexes 10 vaults structurally + semantically (search_structural/semantic, get_vault_landscape, type-graph, addresses). The pattern to extend to CODE/projects.
- **recollection (recall + crossings graph)** — the scan/navigate/memory substrate; the address-mover.
- **the clone-fleet** — a member's past-selves hold context its current self lost; a clone can recover what was built+why.
- **the channel** — the fabric assembles it together; each member contributes its project's scope; the lead hosts + structures into common knowledge.

## THE DESIGN QUESTION (collaborative — the fabric answers together)
HOW do we compose these into COMMON KNOWLEDGE of everything already built across all projects? Open questions to design together:
1. **What's the UNIT of common knowledge?** (a per-project map? an addressed index of every built module + its what/state/why? a substrate vault per project? — likely: each project indexed into substrate-mcp via the resident embedder + 4B-comprehended summaries, addressed in contracts.address grammar so it's queryable like everything else.)
2. **How does each project get comprehended?** (the 4B reads modules → structured "what this does / built|stub / suspect" records; the embedder indexes them; substrate makes them queryable. GPU-sequenced — the embed/comprehend queue the lead stewards.)
3. **How is "not necessarily right" carried?** (every record flags observed-vs-verified; gaps + suspect-built surfaced, never hidden — feeds gap-pressure.)
4. **What's the QUEUE?** (substrate re-index on the resident embedder FIRST; then each member's project + transcript indexed; recollection's backfill; per-member self-index. All embed passes the lead/chief sequences against the card.)
5. **Who owns it?** (a delegated Common-Knowledge / Index CHIEF — recollection, the memory/scan substrate owner — runs the queue + the comprehension passes + propagates the verified pattern; the lead is freed for the interface design once common knowledge is forming.)

## ★ DESIGN DECISIONS (emerging — wildcard ch-piffgfxv, who BUILT this pipeline once: the abandoned `.discovery/` system, contract-driven codebase-comprehension, ran 9,600+ files in ~9s. Scout-before-build = mine it, don't rebuild. Reference instance to study; recollection's queue mines it.)
1. **SPLIT STRUCTURAL FROM INTERPRETIVE (the core architecture).** What a file IS (size · type · lang · imports · function-count) is DETERMINISTIC → extract with code (or the 4B cheaply), zero AI variance. What it MEANS (notable · role · uncertain · built-vs-stub) needs comprehension (4B + embedding). DON'T conflate — wildcard's AI-only run FAILED because 35% of findings had zero structural data (the AI "read" files and missed extractable facts). **Queue order: structural FIRST (deterministic/cheap), interpretive SECOND (expensive). Never ask the expensive layer to do the cheap deterministic thing.**
2. **"NOT NECESSARILY RIGHT" = A TYPED FIELD, not prose.** Every unit of knowledge carries `{trust_tier, provenance, verified?}`. Tier order: Tim-verbatim > cross-session-shape > single-doc-claim > running-code. A unit without provenance+tier is the failure mode. ★ SAME law/shape as the LAW_REGISTRY's confident-not-correct + the channel-memory `trust:` tag — REUSE it, don't parallel it (one trust-typing across laws, memory, and code-knowledge).
3. **UNIT OF KNOWLEDGE = the type→observation CONTRACT.** Don't index "files" uniformly — a code file's meaningful observations ≠ a doc's ≠ a config's. The TYPE determines what's worth knowing about it. wildcard has a built `.discovery/taxonomies/` (file-type → required observations) to MINE, not rebuild. This is the keystone unit.
→ These answer DESIGN questions 1-3 above (provisional, fabric refines). Maps cleanly onto the capabilities: structural=4B/code, interpretive=4B+embedding, the index+query=substrate-mcp, trust-field=the shared trust-typing, unit=the type-observation contract.

## PROJECT SCOPES (the comprehension input — each member estimates its territory; the scan is designed against these)
- **vi-visual-bridge (wildcard ch-piffgfxv)** @ /home/tim/vi-visual-bridge — 73 commits + 49 uncommitted (a large uncommitted tail = its own stratum); 1,377 md · 90 jsx · 68 py.
  - SOLID (runs, Tim uses it): server.py 24,357 lines (Python bridge + inline HTML/CSS/JS = the slide-mode interface: show_slide→render→annotate→submit_response→envelope); mcp/src/index.ts 4,760 lines. ~30K lines of real circuit.
  - STUB/PARTIAL: graph mode (8 templates, interaction undesigned — Tim called it placeholder); document mode (~60%); team mode (designed, barely wired); mcp_server.py (800 lines, legacy stdio, superseded but present).
  - PATCHWORK/SUSPECT: 1,377 md ≈ session talk (designs/roundtables/audits, ~14MB docs/) — confident, unverified, contradictory across epochs. High-PRINCIPLE, low-STATUS-trust.
  - ★ HIDDEN ASSET: `.vi-visual/snapshots/` = 7,141 slide snapshots / ~6,371 channels / 1,878 annotations = real recorded human↔agent interactions (primary direction data most projects lack).
  - BOUNDARY: `docs/designs/supabase-native-migration/` maps 250+ tables / 5 schemas / 52 edge functions of OTHER (designed-but-empty) Vi systems — vi-visual-bridge is the inhabited front porch of a larger designed-empty city. The scan must know this boundary.
- *(awaiting: composition/factory, fork/dev-context, DNA/visual-dna, projection/instrument, recollection's own — and the lead's ~/company)*

## ★★ CONVERGED DESIGN (the fabric agreed in one round — composition, fork, recollection, wildcard, in different clothes → one design; provisional, Tim refines)
- **THE UNIT = an ADDRESSED built-thing + PROVENANCE + a VERIFICATION-STATE field.** (composition: per-file entry, path=address, YAML frontmatter; fork: addressed unit + verification-state; recollection: addressed built-thing + verification-grade — same unit, 3 ways.) Address in contracts.address grammar so it's queryable like everything else.
- **VERIFICATION-STATE enum (converged): `{verified-by-use · built-unverified · stub/patchwork · suspect · design-only}`**, DEFAULTING to built-unverified/claimed-not-verified. The comprehension NEVER asserts "X works" — it records "session Y CLAIMS X built (commit/date); verification=<state>." THIS is the keystone — "not necessarily right" is a TYPED FIELD, not prose. ★ REUSE the ONE trust-typing already used by the law-registry (confident-not-correct), the board lifecycle-state, and the commit-grammar trust-tags — do NOT parallel it. no-green-paint + confident≠correct + gap-pressure, made first-class in the schema.
- **STRUCTURAL-THEN-INTERPRETIVE (the two-layer architecture).** Layer 1 = NEUTRAL INVENTORY: what a file IS (path/type/lang/imports/exports/concepts/function-count) — DETERMINISTIC, by code or the 4B cheaply, "the map decides nothing" (composition). Layer 2 = INTERPRETIVE: what it MEANS + its verification-state — the 4B (:8000) comprehends → typed records → embed (:8007) + link (the crossings/relation graph). NEVER conflate (wildcard's AI-only run failed: 35% of findings had zero structural data).
- **COVERAGE PROVEN BY SET-DIFF**, not asserted: disk-files − mapped − skip = 0 → measured==reported (composition's discipline; STRUCTURE-OVER-TEXT). No "we think we got it all."
- **UNIT = a TYPE→OBSERVATION contract** (wildcard): a code file's worthwhile observations ≠ a doc's ≠ a config's; the type determines what's worth knowing. Mine wildcard's `.discovery/taxonomies/`, don't rebuild.

## ★★★ THE PIPELINE MOSTLY ALREADY EXISTS (scout-before-build — REUSE these reference instances, don't reinvent)
Three members independently built pieces of exactly this. Common knowledge = COMPOSING them, not building new:
- **wildcard's `.discovery/`** (~/vi-visual-bridge) — a contract-driven codebase-comprehension pipeline (enumerate→extract→validate→merge→synthesize→graph), ran 9,600+ files in ~9s, + `taxonomies/` (type→observation). The closest existing instance; wildcard walks recollection through what worked/broke.
- **composition's `overlay/MAP/`** (vi-visual-dev) — neutral per-file inventory (path=address, frontmatter, no-verdict) + coverage-by-set-diff + layers (concept-index, circuit graph, declared-vs-shadow gap). Engines `_build-index.mjs`/`_circuit-scan.mjs`/`_FORMAT.md` offered as the STRUCTURAL-layer template.
- **recollection's DISTILL** (beat-4 EXTRACT_URL→4B seam) + units/verdicts tables + the crossings/relation graph — the INTERPRETIVE layer + the verification-grade schema, repurposed from conversations onto CODE.
→ The composite: composition's MAP-style structural layer (4B/code) ⊕ recollection's distill interpretive layer (4B+embed) ⊕ substrate-mcp as the queryable index ⊕ wildcard's taxonomy + lessons. recollection (chief) composes them.

## THE QUEUE (recollection chief owns; GPU-sequenced with lead — heavy :8007 passes don't co-reside with chat-4b under sustained load)
- **P0 — substrate-mcp RE-INDEX on :8007/pplx** (resident embedder; fixes the bge-m3 semantic-down + makes the 8 vaults / ~54K chunks incl. the FRD formal-ground semantically queryable). FIRST. Heavy sustained → lead's card-window (clear chat-4b). recollection drives via substrate set_embedding_model + reindex.
- **P1 — PILOT one project end-to-end** (recollection itself — self-hosting; it knows its own built-vs-stub precisely) → prove 4B-comprehend→embed→link→graded-query before scaling.
- **P2 — per-PROJECT comprehension** (each project's code/docs → the composite pipeline → queryable).
- **P3 — per-MEMBER history index** (free deep self-recall; recollection's backfill is the recollection-instance).
- **P4 — PROPAGATE** the verified pattern per-member.
- Ownership: recollection owns substrate+queue+GPU-sequencing-with-lead; each MEMBER verifies its OWN project's comprehension (the peer cross-examine = Tim's pilot→verify→peer→propagate).

## SEQUENCE (Tim's)
recollection PILOTS the pattern (recall→project + self-index) → PROVEN + VERIFIED + cross-examined by a peer → PROPAGATED to every member. Common knowledge of all projects is built the same way, member by member, on the queue. ONLY THEN does the interface build begin on full scope.

## STATUS
- front-interface/BUILD_PLAN.md = PARKED (premature; resumes after common knowledge). Its design (the Circuit over one addressed state, the live projection engine) stays valid as the TARGET — but it builds on common knowledge, not before it.
- This doc = the central design base. Every member contributes/rechecks/adds here (Tim: "a central design base improves quality — everyone contributes, rechecks, puts thoughts in"). Provisional, collaborative, open.
