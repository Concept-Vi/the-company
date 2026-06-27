---
type: terrain-entry
name: recollection
register: descriptive
aliases: ["recollection"]
path: /home/tim/company/recollection
relation: external
kind: engine
status: unconfirmed
created: 2026-06-16
last_active: 2026-06-16
size: 1.1G
coverage: { files_read: 6, files_total: 10430, last_read: 2026-06-26 }
git_remote: own git (separate repo; NOT a registered MCP)
purpose: refit clone of episodic-memory v1.4.2 → the Company recall tool (board:// / clone:// units, served lens)
version: 1.4.2 (forked from obra/episodic-memory)
language: typescript
embedding_model: served via :8007 (pplx-embed-context-v1-4b lens — consumed, not served, here)
ports: [8007]
data-of: ["[[dot-recollection]]"]
depends-on: ["[[company]]"]
relates-to: ["[[cache-company]]"]
secrets: false
move_intent: done
tags: [memory]
---

# recollection

## What it is
A refit clone of the open-source `episodic-memory` tool (v1.4.2, originally `obra/episodic-memory`), reworked into the Company's recall tool. It provides MEANING-based recall over conversation archives and exposes scheme-addressed units (`board://`, `clone://`).

Evidence (Observed): `package.json` `"version": "1.4.2"`; README still references the upstream `episodic-memory` install. The refit is in `src/`: `recall.ts`, `recall-cli.ts`, `clone-cli.ts` (docstring: "clone:// FLEET-RECALL capture (recollection side)"), `indexer.ts`, `distill/` (docstring: "embed-cluster (group by MEANING, bge-m3/:8007)"), `backfill.ts`. It has its OWN git and is NOT a registered MCP server.

## How it works
Node/TypeScript CLI + library (`cli/episodic-memory.js`, `dist/`, `node_modules`). Recall/clone/backfill embed via "the served :8007 lens (fails loud if down)" (Observed in `recall-cli.ts`/`clone-cli.ts`/`backfill.ts` docstrings) — i.e. recollection is a CLIENT of the :8007 embedding service, not its owner. It reads/writes its conversation archive + index, which live separately at `[[dot-recollection]]`.

## What it connects to
- `[[dot-recollection]]` — its live data store (`conversation-archive/`, `conversation-index/`, `logs/`, `self/`).
- `[[cache-company]]` / `[[company]]` — consumes the Company-served `:8007` embed lens (direction: recollection → embed service, which is served by `company-embed-pplx`). `dot-recollection/self/` is written by Company code in `company/ops/`.

## When / where
Path `/home/tim/company/recollection`, 1.1G (mostly `node_modules`/`dist`). Latest git commit `2026-06-16 11:27:53 +1000` → created/last_active recorded as 2026-06-16. `move_intent: done

## Notes / evidence
Read: `package.json`, `README.md`, top-level + `src/` listing; grepped src docstrings for `:8007`/`board://`/`clone://`. NOT read: full source, `dist`, `node_modules`. `kind: engine` chosen over `data` (per advisor): this folder is CODE that consumes the Company's embed lens; the DATA is `[[dot-recollection]]`. The brief's ":8007 served lens" refers to the embed service it calls, not one recollection serves.
