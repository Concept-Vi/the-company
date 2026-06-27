---
type: terrain-entry
name: corpora
register: descriptive
aliases: ["corpora", "Claude Code Atlas"]
path: /home/tim/corpora
relation: external
kind: data
status: unconfirmed
created: 2026-06-10
last_active: 2026-06-12
size: 93M
coverage: { files_read: 0, files_total: 1863, last_read: 2026-06-26 }
git_remote: none
purpose: shared source library ("Claude Code Atlas") — the text that gets embedded into the session-recall index
indexed-by: ["[[cache-company]]"]
derived-from: ["[[company-systemd]]"]
relates-to: ["[[company]]"]
secrets: false
move_intent: none
tags: [memory]
---

# corpora

## What it is
A shared source library — the "Claude Code Atlas". Two parts: scraped Claude platform documentation and exported Claude Code session transcripts. It is the SOURCE TEXT that the session-recall vector index embeds.

Evidence (Observed): `ls` → two subfolders `claude-platform-docs` + `claude-sessions`. `claude-platform-docs` = 811 `.md`. `claude-sessions` = 1052 files (1051 `.md` + 1 `.json`). Total 1863 files, 93M. (These confirm the brief's "811 docs + 1,051 transcripts".)

## How it works
Static text on disk — no service of its own. It is consumed: `[[cache-company]]`'s `config.json` registers a vault `{"name":"claude-sessions","path":"/home/tim/corpora/claude-sessions","extensions":[".md"]}` (Observed) — i.e. the transcript half of corpora is the embed source for the recall substrate. The `claude-sessions` markdown is itself produced by the Company exporter (see When/where).

## What it connects to
- `[[cache-company]]` — indexes `corpora/claude-sessions` into chroma+sqlite via the :8007 embed lens (direct, config-evidenced).
- `[[company]]` — `company-agent-sessions-exporter.service` writes Claude Code jsonl → `~/corpora/claude-sessions` markdown (Observed in the unit `Description`); so corpora is both fed by and read back by the Company.

## When / where
Path `/home/tim/corpora`, 93M, 1863 files. Earliest file mtime 2026-06-10 16:33; latest 2026-06-12 19:20. last_active 2026-06-12 — note this is STALE relative to the exporter's intended 20-min cadence (see Notes); the exporter timer is not currently active.

## Notes / evidence
Read: structure + file/extension counts only — NO file bodies were read (relation: external data; catalogue depth is counts + role). The 06-12 latest-mtime is direct evidence the export loop has not run since 2026-06-12, consistent with `[[company-systemd]]`'s exporter timer being inactive (`systemctl --user list-timers 'company-*'` → 0 timers listed).
