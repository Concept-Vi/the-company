# scans/ — session scan output (DATA, projectable)

```
trust: fabric-derived
author: ch-8djrpmsl / 11e7d395 (fork)
date: 2026-06-14
verified: by-execution (runtime/session_scan.py over the live transcripts)
```
> Per [[COMMIT-GRAMMAR]] §2 §4. The SCAN is Tim's verified-direct §1.3 ask, rendered as data.

## What's here
- `<sid>.summary.json` — the committed analysis (small, stable): totals, attribution split
  (human / assistant / tool / channel / compaction / synthetic), per-model token totals, the
  system-subtype taxonomy, the boundary timeline, the `forkedFrom` inherited/own partition, the
  dense-message profile (biggest human + assistant messages), and the largest time-gaps (Tim's away/sleep signal).
- `<sid>.rows.ndjson` — **NOT committed** (regenerable + large + stale-on-write because the sources are
  LIVE and grow). One row per event, the §6 schema in `../schema/session-store-grammar.md`.

## Regenerate the rows (and refresh summaries) — deterministic
```
python3 -m runtime.session_scan <~/.claude/projects/<enc-cwd>/<sid>.jsonl> --out-dir channel-memory/scans
```
The projection (vision §1.9) consumes the tool's LIVE output, not a frozen blob — that's why only the
stable summary + the tool are committed; the fine-grained rows are produced on demand.

## Sources scanned (2026-06-14 snapshot)
- `bda8ce28-…` — the ROOT / lead (true beginning 2026-06-10T05:10:17Z).
- `11e7d395-…` — the fork (this session); branched 2026-06-13T14:21:07Z.
See `../map/lineage.md` for how they relate.
