---
type: contract-journey
journey: manage-session-state
summary: Choose the right way to manage a session's state when work goes sideways or context fills — the rewind-vs-summarize-vs-compact-vs-clear-vs-fork disambiguation. Five overlapping mechanisms with five precise distinct meanings; this journey is the chooser.
status: planned
relates-to: ["[[checkpoint]]", "[[context-window]]", "[[session]]", "[[transcript]]"]
---

# Journey: manage session state

**The flow that disambiguates the five overlapping "fix/shrink/go-back" mechanisms of a session.
F2 honesty up front: four of the five are in-process Claude Code features (interactive TUI +
Agent SDK) the Company supervisor does NOT bridge — only fork is realized through a real fabric
endpoint. This journey is `planned`; it tells a UI WHICH mechanism a user intent maps to, and
where the fabric gap is.**

## The disambiguation this journey owns (V19 ambiguity class: "session state management")
Five things all sound like "go back / clean up", and they are NOT interchangeable:

- **REWIND/RESTORE** ([[checkpoint#op: checkpoint.restore]]) — REVERTS state to a past point.
  Undoes code edits, conversation, or both. Destructive to current file content (applied to disk
  immediately). Use when something BROKE and you want it gone. Bash/external/other-session edits
  are NOT covered — the documented blind spot.
- **TARGETED SUMMARIZE** ([[checkpoint#op: checkpoint.summarize]]) — COMPRESSES one side of a
  chosen point. Frees context WITHOUT touching files; original messages kept in the transcript.
  Use to drop a side-discussion while keeping early context, or compress setup while keeping
  recent work. It is `/compact` aimed at one side of a message.
- **COMPACT** ([[context-window#op: context-window.compact]]) — COMPRESSES the WHOLE
  conversation into a summary. Frees context; files untouched; auto-runs by default as the window
  fills. Use when the window is full and the whole history can be summarized. CLAUDE.md/memory
  survive (re-read from disk); conversation-only instructions may not.
- **CLEAR** ([[context-window#op: context-window.clear]]) — DISCARDS the window entirely and
  starts a fresh session. Files untouched; the old session is PARKED on disk, resumable. Use
  between UNRELATED tasks. (`/btw` is the micro-version: an aside that never enters history.)
- **FORK** ([[session#op: session.create]] fork=true — the ONE fabric-real path) — COPIES the
  conversation into a new session id, leaving the original byte-identical (probe-verified T4).
  Use to TRY A DIFFERENT APPROACH while preserving the original intact. checkpointing.md itself
  points here as the alternative to in-place rewind.

## The chooser (intent -> mechanism)
| the user's situation | mechanism | op |
|---|---|---|
| "that edit broke things, undo it" | REWIND (code) | [[checkpoint#op: checkpoint.restore]] scope=code |
| "go back to before this whole detour" | REWIND (both) | [[checkpoint#op: checkpoint.restore]] scope=both |
| "this side-thread bloated context, drop it but keep the rest" | TARGETED SUMMARIZE | [[checkpoint#op: checkpoint.summarize]] |
| "the window is full, summarize everything and continue" | COMPACT | [[context-window#op: context-window.compact]] |
| "I'm done with this, starting something unrelated" | CLEAR | [[context-window#op: context-window.clear]] |
| "I want to try another approach but keep this one" | FORK | [[session#op: session.create]] fork=true |
| "how full IS the window / what's eating it" | READ | [[context-window#op: context-window.get]] |

## The two axes that decide every choice
1. **Does it touch FILES?** Only REWIND(code/both) and FORK do. Summarize/compact/clear are
   conversation-context only — files stay on disk.
2. **Does it PRESERVE the original?** FORK and TARGETED-SUMMARIZE preserve (fork = new id,
   original intact; summarize = original messages kept in transcript). REWIND reverts (gone from
   the live thread, though the transcript keeps the messages). CLEAR parks (old session on disk,
   resumable). COMPACT compresses-in-place (summary replaces the messages).

## Ordered ops (the read-then-act shape)
1. **[[context-window#op: context-window.get]]** — read the window first when the trigger is
   "running out of context" (PLANNED — in-process /context; no fabric read). If the trigger is
   "it broke", skip to step 2.
2. **[[checkpoint#op: checkpoint.list]]** — if rewinding/targeted-summarizing, list the restore
   points to choose one (PLANNED — /rewind menu; SDK uuids).
3. **Act** via the mechanism the chooser selected. Only FORK has a real fabric endpoint
   ([[session#op: session.create]] / [[session#op: session.post]] verb=consult); the other four
   are in-process.

## Pass shape
PLANNED journey: it cannot reach `pass` through the fabric for the four in-process mechanisms —
its honest verdict for those is `blocked-by-build` (the named gap: no fabric endpoint), which a
UI records as a recorded boundary, never a dead end. The FORK branch CAN pass through the fabric:
it passes when [[session#op: session.create]] fork=true returns a new session id AND the original
session's jsonl is byte-identical (the fork invariant, probe-verified T4 2026-06-11) AND the new
session appears in [[session#op: session.list]]. The chooser table itself (intent -> mechanism)
is the deliverable a UI needs regardless of which mechanisms are bridged.
