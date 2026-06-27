---
type: terrain-entry
name: dot-recollection
register: descriptive
aliases: ["dot-recollection"]
path: /home/tim/company/.recollection
relation: external
kind: data
status: unconfirmed
created: 2026-06-16
last_active: 2026-06-26
size: 1.2G
coverage: { files_read: 4, files_total: many, last_read: 2026-06-26 }
git_remote: none
purpose: recollection's live data store — conversation archive/index/logs + the Company session-identity (self/) data
data-store-for: ["[[recollection]]", "[[company]]"]
secrets: false
move_intent: done
tags: [memory]
---

# dot-recollection

## What it is
`[[recollection]]`'s live data store: `conversation-archive/`, `conversation-index/`, `logs/`, and `self/`. Plain-meaning: the actual recalled conversation data plus the per-session SELF-IDENTITY markers the Company uses to know "which session am I".

Evidence (Observed): `ls` → `conversation-archive`, `conversation-index`, `logs`, `self`. `conversation-archive/` is keyed by project (`-home-tim`, `project-a`, …). `self/` holds `<pid>.json` markers (e.g. `10280.json`, `10964.json`).

## How it works
No service — it is the on-disk state that recollection reads/writes. Its `self/` subtree is Company session-identity data: `/home/tim/company/ops/hooks/write_self_marker.py` writes `~/.recollection/self/<claude-pid>.json = {session_id, transcript_path, cwd, ts}` (Observed: docstring + `SELF_MARKER_DIR = ~/.recollection/self`). `/home/tim/company/ops/seed_self.py` pre-seeds a live session's own self-id so it survives compaction (same `SELF_MARKER_DIR`). `/home/tim/company/runtime/session_scan.py` reads these markers. So `self/` is Company-owned data that happens to live under recollection's root.

## What it connects to
- `[[recollection]]` — owns the archive/index halves.
- `[[company]]` — `self/` is written by `ops/hooks/write_self_marker.py` + `ops/seed_self.py` and read by `runtime/session_scan.py` (#69/#65 self-serve-memory). The marker FILE is the whole self-id mechanism (dodges the self-mod auto-deny).

## When / where
Path `/home/tim/company/.recollection`, 1.2G. Newest file mtime 2026-06-26 14:35 (`self/` markers are written by live sessions → genuinely active). created 2026-06-16 (tracks the recollection refit). last_active 2026-06-26.

## Notes / evidence
Read: top-level + `self/` listing; traced the 3 Company code paths via grep (`write_self_marker.py`, `seed_self.py`, `session_scan.py`). NOT read: archive/index contents (bulk data; catalogue depth is role + structure). Unlike `[[corpora]]`/`[[cache-company]]`, this store IS fresh (06-26) because the `self/` markers are written on every live session, independent of the stalled export/reindex timers.
