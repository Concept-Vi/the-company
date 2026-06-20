# Feed Tim's theorem into COMPANY recall — the plan (#65 post-restore; recollection)

*The lead's post-restore task (g/t-1781885694): "feed Tim's theorem INTO the recall so the system can recall its OWN BASE — #65, give recollection its history." Recall substrate is restored (3475aa6). This SCOPES the ingest thin-slice-first; it does NOT mass-embed yet — that's a resource + design commitment that wants the approach confirmed (and must not contend with the slice's embedder overnight). Lead/Tim: greenlight the approach + space, then I execute.*

## THE GAP (precise)
Tim's theorem is fully indexed in the OVERLORD substrate (8,629 files / 116,712 chunks across 5 vaults — THEOREM-SOURCES.md) but the COMPANY corpus is CODE-ONLY. So the company can't recall its own base: `recall_for_decision` / `corpus(op=query)` over the company spaces (history/common_knowledge/principles/worldview/topics/repo) never sees the theorem. To make the theorem the base, it must live in the COMPANY corpus, not just the overlord vaults.

## THE MECHANICS (the path exists — reuse, don't rebuild)
- SOURCE: the theorem content lives in the overlord substrate (chroma + substrate.db, Windows-path vaults). Two ways to pull it: (a) read the vault markdown files directly via `walk_files` over the vault roots, or (b) pull the already-chunked text from the overlord substrate.db (35k+ chunks already segmented + the `tims_verbatim` catalog). (b) reuses existing chunking + the structural tags (axis/face/articulation) — richer.
- INGEST: `runtime/corpus.py:walk_files` → 4B digest-fan (cognition.run_items) → `runtime/cognition.py:embed_corpus_to_spaces(store, records, projections, embed_fn, dim)` → writes per-(item,space) vectors into the company FsStore (the SAME path the existing corpus uses; X12-FAST cache covers reads).
- RECALL: once embedded into a company space, `recall_for_decision` + `corpus(op=query, space=…)` reach it automatically (no new query path).

## ★ THIN-SLICE FIRST (the lead's own discipline applied here — prove on a small unit before 116k)
Do NOT embed all 116,712 chunks first. Prove the loop on the HIGHEST-VALUE small unit:
1. **The `tims_verbatim` catalog + the 189-chunk formal package** in `relative-difference` (THEOREM-SOURCES.md flags these as the under-mined core — Tim's own words, axis/face-tagged). ~few hundred chunks.
2. Embed that into ONE company space (proposed: a NEW `worldview` or a dedicated `theorem`/`base` space — see Decision A).
3. VERIFY BY USE: `recall_for_decision("<a decision about the axes / the invariant>")` now surfaces Tim's actual theorem words as grounding. THAT proves "the system recalls its own base."
4. THEN scale: the other 4 vaults' theorem folders (visual-dna `Theory` 25, unification `02_PRINCIPLES` 143, ulm `ALLOCATIONS/Schemas`, vi-context `07-Unarticulated` 21) — curated theorem folders, not all 116k.

## OPEN DECISIONS (need the lead/Tim before executing — why this is scoped-not-done)
- **A · WHICH SPACE.** Theorem into existing `worldview`/`principles`, or a NEW dedicated space (`theorem`/`base`)? A dedicated space makes "recall the base" addressable + keeps it from diluting the why-layer; existing spaces need no new wiring. (Lean: a dedicated `worldview`-adjacent space, but Tim's call — it shapes how the base is addressed.)
- **B · CURATE vs FULL.** The theorem FOLDERS (the curated ~500-1000 chunks of his actual articulation) vs all 116k chunks (most are downstream build-system, not the theorem). Lean: curate the theorem-bearing folders (THEOREM-SOURCES lists them); 116k would bury the base in noise + cost hours of embed.
- **C · SOURCE PULL.** Read vault .md directly (simple, re-walkable) vs pull from overlord substrate.db (reuses chunking + the axis/face tags). Lean: substrate.db for the tagged richness, but it's cross-system plumbing.
- **D · REFRESH.** One-shot, or a re-ingest beat as Tim's vaults grow? (Lean: one-shot now, a beat later — don't over-build.)

## RESOURCE / SEQUENCING
- Embedding contends with :8007 (the slice's C1 render + live recall use it). The thin-slice (~hundreds of chunks) is cheap (~minutes); the full 116k is hours + heavy contention → must NOT run during the active slice. So: thin-slice provable now on greenlight; full scale only in a quiet window.
- consult-before-model-loads: uses the running :8007 (no new load) — same as the recall restore.

## STATUS
Scoped + thin-slice plan ready. NOT executed (awaiting Decision A+B esp.). Recall substrate restored + verified, so the moment the approach is greenlit I run the thin-slice proof (tims_verbatim → one space → recall-its-own-base by use) and flag the result. Not slice-blocking; no rush per the lead.
