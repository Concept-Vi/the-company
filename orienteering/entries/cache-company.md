---
type: terrain-entry
name: cache-company
register: descriptive
aliases: ["cache-company"]
path: /home/tim/.cache/company/substrate-claude-sessions
relation: external
kind: data
status: unconfirmed
created: 2026-06-12
last_active: 2026-06-22
size: 1.6G
coverage: { files_read: 2, files_total: 4, last_read: 2026-06-26 }
git_remote: none
purpose: the live session-recall vector index over [[corpora]]/claude-sessions
embedding_model: perplexity-ai/pplx-embed-context-v1-4b
ports: [8007]
indexes: ["[[corpora]]"]
depends-on: ["[[company-systemd]]"]
relates-to: ["[[company]]"]
secrets: false
move_intent: none
tags: [memory, embedding]
---

# cache-company

## What it is
The live session-recall vector index: a Chroma vector store plus a `substrate.db` SQLite database that together embed `[[corpora]]/claude-sessions` so the Company can recall past sessions by MEANING.

Evidence (Observed): contents = `chroma/` (1009M), `substrate.db` (98M), `config.json` (791 bytes), and `chroma.corrupt-backup-20260620/` (a quarantined corrupt store). Total 1.6G.

## How it works
`config.json` (Observed) defines: `state_dir` = this folder; one vault `claude-sessions` → `/home/tim/corpora/claude-sessions` (`.md`); `embedding_provider: openai`-style API pointed at `ollama_base_url: http://127.0.0.1:8007/v1`; `embedding_model: perplexity-ai/pplx-embed-context-v1-4b`; chunking 600 target / 64 overlap / 1400 max tokens. So: text from `[[corpora]]` → embedded via the :8007 lens (served by `company-embed-pplx`) → stored in chroma + substrate.db. The reindex is driven by `[[company-systemd]]`'s `company-claude-sessions-reindex` timer (delta reindex after each exporter run).

## What it connects to
- `[[corpora]]` — the source vault it embeds (config-evidenced path).
- `[[company]]` / `[[company-systemd]]` — the :8007 embed service and the reindex timer that maintain it.

## When / where
Path `/home/tim/.cache/company/substrate-claude-sessions`, 1.6G. `chroma/` mtime 2026-06-22 19:26; `substrate.db` mtime 2026-06-20 03:21. created 2026-06-12 (config.json), last_active 2026-06-22 (newest store write).

## Notes / evidence
Read: `config.json` in full + directory sizing. NOT read: chroma/sqlite internals (binary index). State note (Verified): the index is STALE vs. its intended 20-min reindex cadence — `chroma` last written 2026-06-22, `substrate.db` 2026-06-20, while `systemctl --user list-timers 'company-*'` returns 0 active timers and `company-claude-sessions-reindex.timer` is `inactive`. The :8007 embed service IS active (`company-embed-pplx.service` = active), but the reindex beat that feeds this store is not currently running. The `chroma.corrupt-backup-20260620` is a quarantined prior store (matches the dragnet "35904=stale chroma" bug context).
