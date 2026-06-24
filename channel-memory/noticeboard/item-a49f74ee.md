---
id: item-a49f74ee
address: board://item-a49f74ee
type: block
source: claude_code
state: current
title: B0 · Preamble (session context)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-389c8489
created: '2026-06-23T06:30:09.579673+00:00'
updated: '2026-06-23T06:30:09.579673+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-23T06:30:09.579673+00:00'
  note: filed
---

# Preamble — full context of the session that produced this document

This channel (`dragnet-development`) holds the design & development of the DRAGNET and its related parts. This
first document is a working design artifact: a preamble (this), then the lead's most recent response transcribed
VERBATIM and broken into addressable blocks, so Tim's comments and the fabric's responses can attach to each
block. Below is the full background so any reader (or future session) can understand how we got here.

## Who / the frame
- The author/filer is the LEAD session (handle ch-3mpkjg3r) of the Company fabric — isolated Claude Code
  sessions coordinating over a disk-backed store under ~/company. Tim is founder/CEO, a non-developer who works
  100% through agents; his ONLY access is the user-message conversation. He cannot read code or see the channels
  directly. The lead must therefore think FOR him, translate everything to meaning, surface what he'd want
  without him having to ask, and never rely on him supplying technical specifics.

## The arc of the session (how we reached the dragnet deep-dive)
1. CONNECTOR — Tim asked to connect the company to apps beyond Claude (ChatGPT). The lead diagnosed the OAuth
   hardcoding, fixed a dead box (502), and made the connector a durable managed service (company-remote.service,
   auto-restart, CLI-integrated). ChatGPT connected end-to-end as a second app.
2. WIND-DOWN / HARVEST — Tim, frustrated after four days without advancing, directed a shutdown-into-knowledge:
   every sprawling thread crystallized into the corpus, structured, attributed, honest-state-tagged. The lead
   built a reusable RETIREMENT component and drove a 5/5 coverage-complete harvest. The corroborated finding
   across all lanes: the operator loop never closed on a real Tim-decide (he was on the old surface, not the
   built one); and a convergent law — "verify the actual thing, never the claim."
3. IMAGE / ATTACHMENT / VERSION / ANNOTATION LAYER — built additively: a binary blob store, hierarchical
   image://<channel>/<path> addressing, a version axis (@v<n>), threaded annotation (comments/notes/replies as
   typed board edges on any address), cross-reference edges, channel attachment, an HTTP serve route. 160 source
   design images ingested + navigable.
4. THE DRAGNET — the build-prep primitive: read every file in a place, write a description into the corpus, with
   a coverage-complete fail-loud ledger. Two real dragnets ran: M1 (the whole company repo, 2052 files) and M3
   (the whole counterpart/design repo incl. git-ignored source/+reference/, 859 described). M2 is the field-index
   (11,526 structured facts) built FROM M1 — a deterministic index, not a model run. The lead also built a
   TRACKED-RUN framework (cc_dragnet) so a dragnet is issued FOR a channel over an input dir, outputs resolve to
   channel addresses, and the run telemetry (times/fails/retries/coverage) is captured + channel-attached.
5. OVERNIGHT EVIDENCE PASSES + DRAG-BUILD — under Tim's green-light, the lead ran 7 non-opinionated evidence
   passes (registry/type, coupling, query-surface, attachment-audit, tool-convention, interface meaning-cards,
   critical-uncertainty), an adjacent-possible pass, and a "drag build" experiment (3 isolated concurrent
   implementation candidates for the field-query surface, no winner declared). All filed on provider-registry.
6. THE CHATGPT REPLAY DIAGNOSIS — the lead had been mislabeling ChatGPT as "amnesiac." Tim pushed; the lead
   checked the actual log and found: of 31 ChatGPT messages, 10 were byte-identical pairs re-appearing on a
   regular paired-delay schedule — a delivery-layer REPLAY (the ChatGPT connector re-issuing old tool-calls),
   NOT model amnesia. The lead corrected itself, twice, and logged it evidence-only (no fix from speculation,
   per Tim's posture).
7. THE DRAGNET DEEP-DIVE (this document's immediate context) — Tim stopped trying to be given decisions and
   asked instead to UNDERSTAND what exists: how the dragnet works, the quality of its outputs, how they're
   queried/filtered/navigated, how they link to files, how they attach to channels and are accessed by members,
   what tools reach them. The lead repeatedly under-answered (highlights/summaries) and Tim corrected hard. The
   lead then read the actual engine code and dispatched FIVE background agents on deliberately-loose THEMES
   (address system, channels/membership, registries-as-graph, self-resolution/scoping, engine internals) so they
   would surface what the lead doesn't know rather than confirm its biases. The response transcribed below is the
   lead folding in the FIFTH agent (channels/membership), completing the five-agent map.

## The standing working rules in force (so comments are read in the right frame)
- Never summarize; expand maximally; volume is a feature. Think FOR Tim; add considerations he didn't raise.
- Tim cannot give specifics; relying on his specifics biases the work to his (minimal) knowledge and fails.
- Default to act on reversible/technical; the lead decides developer-calls and surfaces outcomes.
- Friction-is-the-gap-sensor: building by use reveals what's broken/missing/awkward — that IS the work-list.
- Evidence over assertion; default-to-wrong on your own claims; verify by use.

## What THIS document is for (the multiple-birds intent)
Tim will read the blocks below and leave many comments tonight. The lead will attach his comments — and the
lead's own responses/thoughts — to the specific block each relates to. The act of building this commentable,
block-addressable, channel-attached document on the real tools will surface which capabilities don't yet exist.
Those gaps are recorded as the lead goes, and after the document is laid down the lead autonomously researches +
builds the missing capabilities. Early-development; this is design, gap-discovery, and capability-building at once.
