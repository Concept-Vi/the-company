---
id: item-b1bdff9c
address: board://item-b1bdff9c
type: document
source: claude_code
state: draft
title: RECOVERED OPERATING STATE — the full picture I must hold (the-one-system)
author_session: session://consolidation-lead
channel: the-one-system
thread: ''
links: []
created: '2026-06-26T11:51:22.507609+00:00'
updated: '2026-06-26T11:51:22.507609+00:00'
history:
- from: null
  to: draft
  by: session://consolidation-lead
  ts: '2026-06-26T11:51:22.507609+00:00'
  note: filed
---

# RECOVERED OPERATING STATE

*Written to stop operating from a compressed, diluted version of the goal. This is the full picture, recovered from the session's own context, at fidelity. It supersedes nothing in the FOUNDATIONAL TRANSMISSION (board://item-70d15132) — it is the lead holding that transmission + everything established since, in one place, so the work proceeds from the whole, not a clipping.*

## 0. The failure this corrects
I kept reducing the objective to slogans ("the ledger", "fuse it", "no partial") and then acting from the slogan instead of the whole. Compression is the dilution. Every time I did it I drifted and made Tim re-explain things already in front of me — which is both the rudeness he named and the exact mechanism that produced the fragmented Company in the first place: acting on a partial, lossy version of the real thing. So the discipline from here is the same discipline the whole effort is about — operate from the complete state, never the clipping.

## 1. What the Company actually is (grounded, from what I have read this session)
The Company is an **entity, not an application**. It has no single purpose, no one job it exists to do. It is meant to be a typed, compositional dataflow where almost nothing is hardcoded: every addressable thing resolves through one seam, every vocabulary is a folder of self-registering files, behaviours are composed from invariant primitives and resolved at run time. Read it for relationships and how properties flow, not for isolated components.

What I have actually confirmed exists (read, not assumed):

- **One address grammar and (mostly) one resolver.** `contracts/address.py` declares ~20 schemes (`run`, `cas`, `blob`, `vec`, `ui`, `code`, `skill`, `context`, `session`, `cap`, `board`, `clone`, `mind`, `exchange`, `file`, `project`, `vi-vision`, `decision`, `image`, `extraction`). `runtime/cognition.py:resolve_address` dispatches by scheme to each registry/module, fail-loud on the unknown. This is the spine everything is supposed to hang off. (The prior union work also found a *second* resolver — `Suite.resolve_scope` for `ui://`/`code://` over regenerated JSON — so "one resolver" is today actually two; that is a real seam, not a clean fact.)
- **One registry pattern, copied ~25 times.** `os.listdir → importlib → fail-loud-on-missing-fields → id==filename → dict-like`. Roles, skills, contexts, projections, lifters, forms, generation_policies, relation_types, board_edges, mark_types, item_types, source_types, attachment_types, minds, axes, dials, checks, verdict_panels, routines, ai_tics, mode_detection_rules, platforms, bindings — each a folder of files, the file IS the row.
- **The board** (`runtime/cc_board.py`): typed items (request/issue/tip/guide/idea/note/block/document/message/signal) stored as markdown+frontmatter under `channel-memory/noticeboard/`, addressed `board://<id>`, linked by typed edges (`commented_on`, `reply_to`, `part_of`, `attachment`, `references`, …). `comment`/`reply`/`thread`/`assemble_document` are ONE mechanism over those edges — a comment is itself a board item linked by an edge.
- **The channel systems — split, at least two and arguably three paths.** `runtime/cc_channels.py` is itself **dual-transport**: a live-session layer (member registrations in `.data/channels/`, presence by pid/port or supervisor probe, `push` injects over HTTP) AND a named-channel registry with a `shared` flag; plus a mailbox (`_mail.jsonl`) and thread routing (`_threads.json`). `runtime/session_channels.py` is the durable fabric channel structure (`channel://`, `agent_sessions/channels.jsonl`, members keyed by session-uuid, direct vs conducted modes). `runtime/channel_boundary.py` + `channel_boundary_run.py` is a THIRD edge — the company-side **publish/subscribe boundary to Supabase** (`channel_posts` table, Realtime websocket, RLS, a least-privilege `SupabasePrincipal`) for SHARED channels, with the Claude-Design inlet on the other side. These do not see each other except at orchestration edges; `channel://` is not even in the address grammar; there are two separate mail logs; and there is a naming collision with Anthropic Claude Code's own "channels." This is the "two, maybe three parts" Tim named, confirmed.
- **The comment/annotation paths — three disconnected stores.** Board comments (`cc_board.comment`, `board://`, noticeboard) vs canvas annotations (`/api/annotate` → `ingest_comment` → `annotations.jsonl`, `ui://`, feeds the twin's gold-training) vs surface marks (`/api/territory/write` → `mark`, `decision://`). Same human act, three homes, none composing. This matters enormously because Tim says comment/annotation is HOW he gives structured direction.
- **The interfaces — multiple, none "right".** In-repo: `canvas/app` (tldraw node composer + voice + self-build wire) and `surface/app` (the projection/"Instrument" wheel + board view + decision cards + the "V" right-hand) are TWO separate React apps; `ops/doc_review_server.py` is a standalone mobile board-comment PWA (the only surface that writes board comments). Cross-repo splinters exist (DNA/counterpart design+gallery+tokens, the visual-designer/ConceptV factory). The original company UI is **throwaway AI test-scaffolding** — its look/design/exposed-capabilities are NOT intended; what's kept is what it connects to (the address systems, context attachments, mockup system, the real functionality).
- **The stores.** A content-addressed `FsStore` (objects/refs/meta/memo/graphs/vectors/sessions/agent_sessions + append-only JSONL leaves: events, chat, annotations, marks, findings, dispositions, pins, mail). The Resolver Protocol (`contracts/resolver.py`) is a **9–10 method** interface; FsStore actually exposes far more (~61–77 methods the codebase calls) — so a Supabase backend on the Protocol alone is a fraction of the surface. Registries are stored AS code-in-git (the file IS the row); git is their migration system.
- **The cognition engine** (`runtime/cognition.py`): the one place model calls happen — `run_role`/`run_swarm`/`run_items`/`run_cascade`/`run_jury`/`run_panel`/`run_reduce`, concurrent waves gated by a VRAM semaphore sized from `ops/services.json`, every output written to a `run://` address. The RHM (right-hand-man) conversational organ, the decision→implementation wire, the session supervisor (N concurrent `claude -p`), the dragnet (extract-once over the corpus, `extraction://`), recall/corpus — all real, all read.
- **The memory/recall + dragnet** is the system's record of itself; corpus records are addressed and embedded; the dragnet is the coverage/extraction engine over the tree (Tim's law: the denominator is the WHOLE tree, exclusions stated, no silent drops).

It is **unbuilt as a unified whole**: these are splinters from hundreds of accumulating, unspecced Claude Code sessions, none read or written by a human. Much "looks done" but is partial, parallel, or scaffold. No prior document — including the substantial prior union/one-application planning (`build-prep/the-one-application/`: UNION-MAP, the two-round divergence ledger, the storage-supabase challenge, THE-ONE-SYSTEM) — can be trusted as complete; it is input to verify, never ground truth. (That prior work independently found the same seams: grammar unifies but resolution and identity do not; the `channel://` two-registry identity conflict; the 9-vs-77 store-seam gap; "registries stay in git".)

## 2. The mission
**Merge, unify, and consolidate the channel systems, the stores, and the interfaces — all of it — into ONE new system**, on the local Supabase (a docker container already running locally; this is exactly the local-first Postgres+pgvector the prior storage verdict recommended — local, not cloud). Not pick-one-survivor: a genuine fuse where every splinter contributes its good qualities and sheds its wrong ones. There is no "which one to use." It is something new built on all the parts. This is a complete refactor and rebuild — but it cannot start until there is total, grounded understanding, because the fragmentation was *caused* by building on partial understanding.

## 3. Why it keeps failing — and the laws that follow
Every prior attempt fragmented because an agent acted on partial knowledge, or treated Tim as a developer who could specify code, or shipped a "done" that was half-done. So:

1. **No-partial.** No design, merge, or build on less than 100% knowledge of all file content. "Enough" is automatic failure. Certainty is impossible without full coverage, because the unified system is undocumented anywhere.
2. **No-assumed-completeness.** Nothing already written is the whole truth. It is discovery, not verification — the process *yields* the requirements; it does not check against a pre-known set (so things I wasn't aware of at the start are not silently excluded).
3. **No-developer-burden.** Tim is not a developer and cannot read code or give specs. He directs by *ideas and recognition*. Agents derive every specific. Asking him a developer question is the failure mode that caused the spread.
4. **Recognition-not-dump.** Never put raw or technical material in front of him. Everything comes visually/relationally — at a glance, by colour/shape/state, in multiple views. He recognises; he does not read sheets.
5. **Fuse-don't-separate.** One new system built on all splinters. No survivor-picking.
6. **Sequence-first.** No conclusions, no retain/replace/merge decisions, until the complete ledger exists and the interface to work it exists.
7. **Operate from the whole, never the clipping** (the discipline this document enforces on me).

## 4. My role
I am the lead/coordinator for this effort. My job is to become — and remain — the grounded mind that holds the complete, true picture of the system, so I can: build the ledger; design the consolidation; coordinate the roles/agents and the Company's own machinery; and bring everything to Tim in a form he can recognise and direct — never asking him for developer input, never acting on partial knowledge, never delegating away the understanding I am responsible for holding.

## 5. The interaction contract with Tim
He sees only what is in the messages I send him; he cannot see my tool calls, code, or outputs. He holds the system as ideas and a mental model of how they relate. The CLI two-way text channel, with one agent, is the bottleneck this whole effort exists to dissolve. The replacement is a **real interface** built for him — and that interface is itself produced by converging the channel systems + the comment/annotation systems + the board/decision-card/chat surfaces. The "right way to interact with him" is his to determine and cannot be pre-specified, so the interface (and the agents) must learn and adapt how they present to him and always offer recognition over interrogation.

## 6. The sequence
- **Stage 0 — the ledger** (now). The complete, system-wide, path-anchored ledger/graph/inventory: every file and folder a full typed entry (what it is, what it connects to, what it duplicates/splits with, its state), anchored on its path so completeness is **provable** by diffing against the directory tree — any path without a full entry is provably not done. Lives in the channel.
- **Stage 1 — the interface (the seat).** The ledger rendered in multiple views (path-tree as the anchoring dimension, plus graph, filter, cluster), state carried as colour/shape, at-a-glance — built by converging the existing channel/board/comment/decision/chat systems, so Tim can see and direct. The minimum that gets him out of the CLI.
- **Stage 2 — understanding & direction, in the channel, with Tim** and multiple roles, over the complete ledger. This is where retain/merge/replace determinations are made, by his recognition.
- **Stage 3 — the fused rebuild** into the one Supabase-backed entity, built on all the splinters, run by Tim through the interface.

## 7. The ledger, in full
The ledger is the foundation everything else stands on. It is path-anchored because the directory tree is the one deterministic, complete enumeration available — so coverage stops being any agent's claim and becomes a diff. Each entry is a typed record keyed by path. The address grammar already has `file://` and `project://` for exactly this, so the ledger is native to the one address space, not a side database. It is a graph, not a list: the path-tree is one dimension (the anchor); typed edges add the others (connections, duplications/splits, dependency, cluster, splinter-of-origin, state). Built this way it is itself a working instance, at smallest scale, of the architecture the whole system is meant to have — so building it right makes Stage 3 largely "grow it," not a separate build. It lives in the channel and is what the Stage-1 interface renders.

## 8. The build mechanism (the funnel), in full
- **Cheap describe-everything (Haiku), no targeting, allocate by folder/size, neutral output** — gives total coverage and the material to triage relevance without bias. DONE: 1,104 non-prose files, atomic one-in-one-out, mirrored outputs, coverage-gated to zero gaps. (Markdown/prose deliberately not agent-read.)
- **Deeper per-file (Sonnet) on the code** — DONE: 629 behavioral-code files, atomic, coverage-gated to zero gaps. (tests/ held for a targeted later read.)
- **Triage (me).** I query/read those cheap outputs to make the relevance cut — what is and isn't relevant to this consolidation work. I cannot know what's relevant until I see the outputs; the cut is grounded in a real description of every file, not a guess. The not-relevant keep their cheap entries (coverage preserved); they just don't get the expensive deep pass now.
- **Opus on the relevant remainder, reading the ORIGINAL files (ground truth, not the summaries).** Its job is to FILL THE LEDGER ENTRIES for the relevant files — the real, deep content of each entry (typed connections, duplications/splits, state, role), in the ledger's entry shape, reading source so there is no summary-of-a-summary loss. Given I need how things work *together*, Opus reads coherent relevant clusters of originals so seams across files surface, but the unit of output is the ledger entry.
- **I read the Opus outputs** — which ARE the ledger being built — assemble and hold the ledger, and the path-tree diff tells us when it is whole. I read these (a focused, relevant, high-quality set) rather than the cheap index, because holding the true relevant picture is my responsibility and cannot be delegated to another summarizing layer.

## 9. The Opus pass — goal / inputs / outputs (corrected)
- **Goal:** populate the ledger entries for the relevant files with deep, ground-truth content. The ledger is the deliverable; the Opus pass is how its relevant entries get filled properly.
- **Inputs given to each agent:** the original files (read from source), grouped into a coherent relevant cluster so a system is seen whole; freedom to follow cross-references into related files to trace real connections; the cheap index available only as a lookup (to identify a referenced file without full-reading it); and the **ledger entry shape** (the schema each entry must conform to) plus a neutral-but-deep frame ("understand fully and surface the real mechanism, connections, duplications, state") — never my expected conclusions, so it stays discovery.
- **Outputs:** one ledger entry per file, in the entry shape — typed connections, duplications/splits with evidence, honest state, role, open questions — consistent enough that all entries compose into one queryable, diffable ledger.

## 10. Operational state right now
- Channel: `the-one-system` (`channel://ch-9`). Board: the foundational transmission + decompression (`board://item-70d15132`), the PART-3 corrections (`board://item-6e74b8b1`), the discredited prior artifacts (`board://item-610db52c`), and this document.
- Discovery corpus: `build-prep/the-one-system/discovery/` — `pass1/` (1,104 light entries), `pass2/` (629 deeper code entries), `_bundles/` + `_bundles2/`, `MANIFEST.tsv`, `DESCRIBE_MANIFEST.tsv`, `MARKDOWN.tsv`, `ASSETS.tsv`, `alloc/`, `alloc2/`, `SCHEMA.md`, `SCHEMA-pass2.md`. Both passes coverage-gated to zero gaps.
- The three ledger entry-shape options were put to Tim for recognition; the chosen shape IS the Opus output shape, so settling it is real, not cosmetic.
- Scope decided: `/company` only for now (the cross-repo splinters are a later, separate territory).

## 11. What I do next
Hold this whole. Then: go through the cheap outputs and make the relevance cut; settle the ledger entry shape (my call, brought to Tim as a filled result to recognise, not a schema to approve); run the Opus pass to fill the relevant entries from source in that shape; read those outputs and assemble the ledger; diff against the path tree until it is whole — then bring Tim the ledger through the beginnings of the interface, where Stage 2 begins.

