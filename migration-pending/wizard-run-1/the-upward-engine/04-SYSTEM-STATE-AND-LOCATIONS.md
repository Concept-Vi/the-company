---
type: state
register: descriptive
aliases: ["Upward Engine — system state and locations"]
tags: [company, recollection, dragnet, wizard, locations, state]
status: descriptive
coverage: { files_read: many, files_total: many, last_read: 2026-06-27 }
relates-to: ["[[The Upward Engine — vision]]", "[[Upward Engine — UI capability map]]", "[[Upward Engine — dogfooding plan]]", "[[project-recollection-design]]", "[[project-dragnet-recall-substrate]]"]
---

# Upward Engine — system state & where everything is

The honest, grounded map (verified 2026-06-27, session d5fc8ad1) of the three chains + the company recall + the seed. Marked **VERIFIED** (read/ran this session) vs **ELSEWHERE** (lives in another session — pointer only).

---

## recollection — the OUTER cross-everything memory chain  *(the section)*

**What it is:** a refit of the open-source `episodic-memory` plugin into the company's outer, cross-session/cross-project recall **substrate**. Upstream = sync transcripts → embed → vector-search. The refit kept that and built a **typed knowledge substrate** on top (atoms → units → links + fingerprints + verdicts + candidates, with `unit_type`/`relation_type` registries), embedding through the **company's served lens** rather than a bundled model. Full mechanics: deep-read by 3 agents this session; design memory at [[project-recollection-design]].

**State — built, backfilled once, then PARKED:**
- Live skeleton: the data model, the served-lens embedding, capture (sessions + `board://` + `clone://`), the mechanical crossings graph, `recall` + `navigate`, and the distill *shape* (with a stub extractor).
- **Backfilled 2026-06-16** (1,000 conversations) — then nothing has run its sync/index since (frozen at that date). **No live caller** — not a registered MCP, no cron, no systemd, nothing invokes it. The only live write into its data dir is the company **self-marker** hook (session-identity, repointed this session).
- **Organs awaiting switch-on** (the dedicated session's agenda): (1) the real **distill extraction model** — stubbed, needs Tim's VRAM greenlight (config re-point `EXTRACT_URL`); (2) **ratify** — throws "not wired"; principles stage as candidates but can't be ratified until the judge + Tim-approval exist; (3) distilled **units aren't embedded** → recorded but not recall-queryable (this is the keystone gap for the UI's multi-space map); (4) L3 rollup, semantic links, the `:8008` reranker — scaffolded; (5) **register it as a live MCP** (its `.mcp.json` is relative/unregistered).

**Where it is (VERIFIED, moved into the company this session):**
- **Code:** `/home/tim/company/recollection` (own git, no remote; gitignored inside company).
- **Data:** `/home/tim/company/.recollection` (1.2 GB: `conversation-archive/`, `conversation-index/db.sqlite`, `logs/`, `self/`; gitignored). Pinned by `RECOLLECTION_CONFIG_DIR=/home/tim/company/.recollection` in `~/.bashrc`. Old `~/recollection` + `~/.recollection` removed; 8,218 DB paths rewritten; **recall verified working at the new path** (CLI run returned hits).
- **MCP tools it defines** (in its own unregistered `.mcp.json`): `search`, `read`, `recall`.
- **Served lens:** `http://127.0.0.1:8007/v1/embeddings` (`pplx-embed-context-v1-4b`, INT8/2560/cosine).
- **`self/` (company-owned, parked under recollection's root):** session-identity markers (#69), written by `company/ops/hooks/write_self_marker.py` + `ops/seed_self.py`, read by `runtime/session_scan.py`; all three now derive the path from `RECOLLECTION_CONFIG_DIR`.
- **ELSEWHERE:** recollection's own **design/build session** — a long transcript with its oldest session-state still active/idle (Tim runs the dedicated work there). Recallable by meaning via `session_recall`.

---

## Dragnet — the inverted catch-all chain *(one chain in the same engine)*

**What it is:** Tim's name for the method — pump huge data **up through layers of smaller models** into the company and its brain; the catch-all inversion. *One kind of chain in the same compositional system* (not a separate system). Design memory: [[project-dragnet-recall-substrate]] + [[project-dragnet-unification]].

**Where it is:**
- **Company-side (VERIFIED present):** `ops/dragnet_extract.py`, `ops/dragnet_determine.py`, `routines/dragnet_freshness.py`, and the build-prep dossier `build-prep/the-one-system/`. The session-recall substrate it feeds: `~/.cache/company/substrate-claude-sessions/` over `~/corpora/claude-sessions`.
- **Channel:** `dragnet-development` (the cross-session channel where its work is coordinated).
- **ELSEWHERE:** the **live Dragnet build runs in another session** (an agent actively on it) — that session holds the current state + its own transcript. This file does not capture that session's live detail; treat the company-side files as the durable trace and the session as the live edge.

---

## The company's INNER recall — the live tool today

**What it is:** the inner, single-session layer — distinct from recollection (outer). This is the recall that is **actually live and registered right now.**
- **MCP:** `mcp__company__session_recall` (op = find/decisions/open_loops/catch_up/timeline/directives/spin_up_points/drift), served by `mcp_face/server.py` (running).
- **Code:** `runtime/session_recall.py` + `runtime/session_scan.py` + `runtime/session_lens.py`.
- **Store:** the `.cache/company/substrate-claude-sessions` index over `~/corpora/claude-sessions` — embeds via `:8007`, reranks via `:8008` (rerank currently down — fails declared, not silent).
- **Seam:** recollection (outer/deep) is meant to **union** with this (inner/fresh) at a freshness boundary.

---

## The wizard — the seed (this folder)

**What it is:** the by-hand prototype run (2026-06-04→05) of the project→product pipeline on a real ~5,000-file corpus — the only place a real project was actually pumped through the model fleet. **NOT yet mined.** Preserve whole; it's the seed for the real chains.
- **The working outputs:** this folder — `/home/tim/company/migration-pending/wizard-run-1/` (the toolkit `capture2.py`/`fleet.py`/registries, `wizard.db`, the projection/jsonl data). Heavy data gitignored-but-on-disk; scripts/registries/docs tracked.
- **The recount/handoff:** `SESSION_FIELD_REPORT.md` (read it first — the reframes, the walls, the cascade economics, the multi-level-embedding unlock).
- **The ideated process (drafted sequence descriptions):** `/mnt/c/Users/Workstation001/Documents/Claude/Projects/counterpart/the Company/build-prep/Discovery Methodology — Patterned Visibility (from run-1).md` (VERIFIED present) — the methodology: patterned-visibility, cascade+economics, projections + multi-level embedding + cross-level queries, the large-file design space, the degenerate-loop trace.
- **Staged plan / round findings:** `BUILD_PLAN.md`, `FINDINGS.md` (this folder).
- **ELSEWHERE:** the **wizard session transcript** — the long session where it was described, discussed, and all the issues/trials/commentary ran. Recallable via `session_recall`.

---

## The seed context, in one place
The unique material to build the real systems from: **(a)** the wizard *working outputs* (this folder) · **(b)** the *ideated process* (the Patterned-Visibility methodology doc, /mnt/c) · **(c)** the wizard *session transcript* (discussions/issues/trials) · **(d)** recollection's *built substrate + its design session* · **(e)** Dragnet's *company-side files + its live session*. The UI dogfooding ([[Upward Engine — dogfooding plan]]) points the engine at the company's own corpus — which already contains (c), (d), (e) as transcripts — so the system can recall its own making.

> Honesty: the "ELSEWHERE" pointers (the recollection design session, the Dragnet session, the wizard transcript) were **not** opened this session — they're named so the dedicated sessions can find them via `session_recall`, not summarised here. Everything marked VERIFIED was read or run on 2026-06-27.
