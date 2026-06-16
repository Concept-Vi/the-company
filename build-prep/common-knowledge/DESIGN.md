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

## SEQUENCE (Tim's)
recollection PILOTS the pattern (recall→project + self-index) → PROVEN + VERIFIED + cross-examined by a peer → PROPAGATED to every member. Common knowledge of all projects is built the same way, member by member, on the queue. ONLY THEN does the interface build begin on full scope.

## STATUS
- front-interface/BUILD_PLAN.md = PARKED (premature; resumes after common knowledge). Its design (the Circuit over one addressed state, the live projection engine) stays valid as the TARGET — but it builds on common knowledge, not before it.
- This doc = the central design base. Every member contributes/rechecks/adds here (Tim: "a central design base improves quality — everyone contributes, rechecks, puts thoughts in"). Provisional, collaborative, open.
