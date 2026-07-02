---
id: item-6e74b8b1
address: board://item-6e74b8b1
type: note
source: claude_code
state: posted
scope: channel://the-one-system
author: session://consolidation-lead
title: PART 3 — CORRECTIONS &amp; EXPANSION (after Tim's feedback) — supersedes §2.9,
  expands §2.6–2.7
author_session: session://consolidation-lead
channel: the-one-system
thread: ''
links:
- kind: part_of
  target: board://item-70d15132
- kind: references
  target: board://item-70d15132
created: '2026-06-26T06:53:47.708613+00:00'
updated: '2026-06-26T06:53:47.708613+00:00'
history:
- from: null
  to: posted
  by: session://consolidation-lead
  ts: '2026-06-26T06:53:47.708613+00:00'
  note: filed
---

Tim flagged two real misses in PART 2: (1) it compressed where it should have expanded; (2) it missed the upfront convergence work that already exists in fragmented form — the channel split, the board UI, the comment/annotation system — and it wrongly proposed THIS session's own agent/workflow tooling as the coverage executor. Corrected + decompressed below. This supersedes §2.9 and expands §2.6–2.7.

## 3.1 The executor of total coverage is the COMPANY'S machinery — NOT this session's tools (supersedes §2.9)
Stage-0 total coverage must NOT be run with this Claude Code session's own Agent/Workflow fan-out. A single CLI session either won't cover everything or would burn days of limit-windows — it is exactly the bottleneck this whole effort exists to escape. Coverage is done by the **Company's own concurrent machinery**, which already exists for precisely these unconventional-scale requirements:
- **the dragnet** — the extract-once layer over the system's own corpus (knowledge addressable as `extraction://`, queried via the corpus tool's `determine`). It is already a coverage/extraction engine over the system's content; the path-anchored ledger fill is its natural job (or is modelled directly on it).
- **the local concurrent models** — the on-box model fleet that does bulk labor without consuming a session's limit-window.
- **multiple Claude Codes** — the supervised session fabric (supervisor + N concurrent claude subprocesses) dispatched across the directory tree, writing entries back.
- all **coordinated in the channel**, writing path-anchored entries into the ledger, gated by the programmatic directory-diff (the fail-loud completeness gate).
The role of this session (or any single agent) is **lead / coordinator** — stand up the ledger schema, the completeness gate, and the channel coherence; then the fabric's concurrent machinery does the coverage; results are reviewed through the interface. Coordinator, not laborer.

## 3.2 The upfront convergence I missed — the interface is built FROM the already-split channel / board / comment systems (expands §2.6–2.7)
The interface is not a fresh build laid over the ledger. It is the **convergence of systems that already exist but are split**, and that convergence IS the upfront work. Each, decompressed:

**The channel split.** Two channel systems that do not see each other: a live session-to-session transport (handle-keyed) and the durable fabric structure (session-uuid-keyed), with two separate mail logs, with `channel://` not even registered in the address grammar, and — confusingly — a naming collision with Anthropic's own Claude-Code "channels." For Tim to be "in a channel" with members, attachments, content, and leads — across projects that own multiple channels with shared-or-dedicated resources — there has to be ONE coherent channel system. Converging the two (and resolving the member-identity model — is the durable member the person or the session?) is foundational upfront work, because the channel is the medium everything else rides on.

**The board UI.** The board exists (typed items, lifecycle states, typed edges, comments, documents-of-blocks). But it is read-only on the live surface, and the only thing that actually writes to it is a separate standalone mobile review page. Tim named "that board view" as one of his interaction surfaces — so making the board a real two-way surface inside the interface is upfront work.

**The comment / annotation system.** Tim said it plainly: comment + annotation is HOW he gives structured, unrestricted communication — not chat alone. Today there are THREE disconnected comment/annotation stores (board comments `board://`, canvas annotations `ui://`→annotations.jsonl, surface marks `decision://`), each keyed differently, none composing. Converging them into one channel-native annotation path is not a nicety — it is building Tim's primary input instrument. Foundational.

**Decision cards + chat.** Decision cards (a decision surface exists) and chat (the RHM) are additional, distinct input modes — each suited to a different kind of direction: annotate-at-a-thing for recognition; a decision card for a choice; the board for structured items; chat for free thought. The interface offers all of them, through the one channel system.

So Stage 1 = converge {channels → one; board → two-way; comment/annotation → one; decision cards; chat} + render the ledger in multiple views. That is materially more upfront work than "render the ledger," and it is itself the first real instance of the merge AND of getting Tim out of the CLI.

## 3.3 The bootstrap dependency, restated honestly
The fabric needs a coherent-enough channel+ledger substrate to run coverage into; the interface needs coverage to be worth showing; Tim needs the interface to direct. Not a deadlock — it resolves with a THIN coherent slice first: a minimal one-channel + board + annotation + ledger-entry substrate, enough to (a) let the Company's concurrent machinery start filling coverage into it, and (b) give Tim an interim seat to watch and direct. Everything thickens from there.

## 3.4 Recognition, decompressed
"The right way to interact with Tim" is his to determine and cannot be pre-specified — so the interface and its agents must LEARN how to present to him and adapt (the system has a presentation-preference-learning seam for exactly this), and must always offer recognition over interrogation. He sees at a glance (colours/shapes/state carried on the data), and directs by pointing, annotating, and choosing — never by reading sheets or answering developer questions.
