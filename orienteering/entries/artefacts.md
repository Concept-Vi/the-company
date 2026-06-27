---
type: terrain-entry
name: artefacts
register: descriptive
aliases: ["artefacts"]
path: /home/tim/artefacts
relation: external
kind: work
status: unconfirmed
created: 2026-05-26
last_active: 2026-05-28
size: 108K
coverage: { files_read: 2, files_total: 2, last_read: 2026-06-26 }
git_remote: none
relates-to: ["[[corpora]]", "[[foundation]]"]
secrets: false
move_intent: none
contents: ["Vi.md (vision narrative)", "model-survey-2026-05-26.md (RTX 4080 model survey)"]
tags: [model, voice]
---

# artefacts

## What it is
A small two-file folder holding two standalone documents from the Company's founding-arc week:

1. **`Vi.md`** (81K) — a *"what Vi is"* vision narrative: a standalone account of what is being built and why it is unlike what others are building. Written for two readers at once — *"the origin"* (Tim, as a mirror of years of work) and a *"someone he might choose to show it to"* (collaborator/backer/participant). It is explicitly **a partial view of something larger**, AI-written over a brief window, and honest about reaching the edge of what it knows. Covers the whole organism, the invariant spine, the origin, and the origin↔system coupling.

2. **`model-survey-2026-05-26.md`** (23K) — the verbatim transcript of a 2026-05-26 model-survey exchange: a comprehensive walk-through of image, video, 3D, voice (TTS / STT / full-duplex / orchestration), music, and other generative-AI models — local-runnable and commercial — assessed for **Tim's RTX 4080 16 GB rig**. Synthesis produced by four parallel research subagents, then consolidated. Carries full provenance (session ID `12c59b4e-…`, line numbers, timestamps) back into the transcript.

## How it works
Nothing runs here — these are documents, not code. `model-survey` is itself a pointer back to source transcripts (`~/.claude/projects/-home-tim/12c59b4e-….jsonl` and a superpowers archive snapshot), citing exact lines/timestamps for the exchange.

## What it connects to
- **[[foundation]]** — the model-survey notes it landed *"about 10 minutes before the first foundational identity message"* (same session as the foundation arc); it sits at the doorstep of the founding conversations now held in foundation.
- **[[corpora]]** — both files are anchored to / recoverable from the session-transcript corpus.
- The **model survey** is upstream context for the Company's later native-model-layer / model-loadout work (what local+cloud models the rig can run); **`Vi.md`** is a vision-narrative cousin of the doctrine in foundation.

## When / where
`Vi.md` mtime 2026-05-28 02:36; `model-survey` mtime 2026-05-28 13:58, content dated 2026-05-26. Path `/home/tim/artefacts`, 108K, 2 files. No git. Read 2 of 2 (both heads; bodies skimmed).

## Notes / evidence
- State **dormant**: static reference documents, not a running thing.
- The model survey is a snapshot of the **RTX 4080 16 GB** rig's options as of 2026-05-26 — useful as historical context but potentially stale against the current stack.
- Coverage caveat: I read the opening sections of both files; I did not read the full 81K `Vi.md` body end-to-end.
