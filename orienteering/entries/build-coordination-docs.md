---
type: terrain-entry
name: build-coordination-docs
register: descriptive
aliases: ["build-coordination-docs"]
path: /home/tim
relation: external
kind: work
status: unconfirmed
created: 2026-06-01
last_active: 2026-06-08
size: 76K (6 files)
coverage: { files_read: 6, files_total: 6, last_read: 2026-06-26 }
git_remote: none
relates-to: ["[[company]]", "[[foundation]]"]
secrets: false
move_intent: none
provenance_of: how the engine / voice / STT / UI / wire / cognition work got built and merged onto main
doc_kind: cross-session build handoff & merge-coordination notes
loose_in: /home/tim (not a folder)
tags: [voice, fabric]
---

# build-coordination-docs

## What it is
**Six loose Markdown files sitting directly in `/home/tim/`** (not a folder) that together are the **historical provenance** of how the Company's engine, voice/STT, UI surface, decision-wire, and concurrent-cognition work got built across parallel Claude Code sessions and merged onto `main`. They are cross-session handoff and merge-coordination notes — written by one session *to* another (Tim physically relayed file paths between sessions that didn't know the other existed), each documenting what was built, the exact conflict/seam surface, and a proposed division of labour so neither side's work was silently lost.

The six files (absolute paths):

1. **`/home/tim/company-bridge.md`** (17.8K, 2026-06-02) — spec/research session ⇄ build session bridge. The spec session reports a **foundational vocabulary mismatch** it found between its "AI-Driven Build-and-Operate System" blueprint (record vocabulary: capability/scenario/gap/contract/evidence/decision/deployment-recipe/constitution) and the actual engine (which has none of those as record types). Has an append-only REPLY section for the build session.
2. **`/home/tim/MERGE-COORD-cognition.md`** (6.0K, 2026-06-08) — from the `concurrent-cognition` worktree (`/home/tim/company-cognition`, branch `concurrent-cognition`, 29 commits ahead). Lists its net-new file territory, the **7-file conflict surface** vs `main` (the hard ones: `runtime/suite.py`'s `chat()` refactor and `canvas/app/src/useAppController.ts`), and a proposed merge division.
3. **`/home/tim/ui-handoff.md`** (18.4K, 2026-06-05) — from the Interactive Addressed Surface session (`/home/tim/company-interactive`). Warns that all 14 region components / voice API / config forms live **only on its branch, not `main`** (`main` HEAD `ca84ddc`), so building on `main` would duplicate work. Hands off to the voice + config-lab session.
4. **`/home/tim/voice-frontend-handoff.md`** (11.4K, 2026-06-05/06) — backend → frontend voice seam. Documents the streaming protocol `POST /api/voice/stream` (newline-delimited JSON: transcript/reply/per-sentence wav chunks) — the ~5s→~3s low-latency win by playing chunk idx=0 while idx=1 synthesises.
5. **`/home/tim/voice-stt-handoff.md`** (13.9K, 2026-06-05) — STT-side handoff. Documents `voice/stt.py` as a **swappable ear registry** of 6 STT providers (whispercpp, whisper_local/faster-whisper, parakeet, canary, granite, assemblyai), config-slot selection, fail-loud no-fallback. Updated to note PR #1 **merged to `main` at `ca84ddc`**.
6. **`/home/tim/round3-grounding-report.md`** (8.6K, 2026-06-01) — a grounding/verification pass answering open design questions (§D #4–#7) with OBSERVED/INFERRED/VERIFIED-labelled evidence: type grammar (JSON-Schema-in-data canonical for declared types), on-write philosophy (reject-loud at contracts, succeed-permissive + classify-on-read for content), `supersedes` mechanism vs open instance-migration.

## How it works
Nothing runs — these are prose coordination artifacts. Their mechanism *was* the relay protocol itself: a file written by session A, carried by Tim to session B, sometimes appended-to (the bridge's REPLY section) and carried back. They encode branch names, worktree paths, merge-base commits, conflict tables, and the streaming/registry contracts that the actual merges onto `main` were executed against.

## What it connects to
- **[[company]]** — directly: every file describes work that landed (or was being landed) on `~/company` `main` — the voice circuit, STT ear-registry, RHM tool-calling, the interactive surface, the decision-wire, concurrent-cognition. They are the merge-history narrative for the current engine.
- **[[foundation]]** — kin as provenance/origin material (these record *how the build happened*, foundation records *why/what it is*).
- Named worktrees referenced (now likely consolidated or stale): `/home/tim/company-cognition`, `/home/tim/company-interactive`.

## When / where
Earliest 2026-06-01 (round3-grounding-report), latest 2026-06-08 (MERGE-COORD-cognition). Loose in `/home/tim/` — **not a folder**, six sibling files totalling ~76K. No git. Read 6 of 6 (heads read; the voice-stt and round3 files read in substantial depth).

## Notes / evidence
- State **dormant / historical**: the merges these coordinated are done; the docs survive as the record of how the engine/voice/ui/wire/cognition work converged onto `main`. Several reference branch states and HEAD commits (`ca84ddc`) that are now history.
- Grouped as **one entry** by the user's instruction — they share a single nature (cross-session build provenance) and a single (loose-in-`~`) location.
- Coverage caveat: heads of all six read; full bodies of voice-stt-handoff and round3-grounding-report read closely, the others skimmed past their opening sections.
