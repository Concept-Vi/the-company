#!/usr/bin/env bash
# Drain the archaeology re-mine to completion: fire batches until one adds no new captures (dry),
# bounded at 40 iterations. Idempotent/resumable — each batch deepens, never duplicates.
cd /home/tim/company
prev=-1
for i in $(seq 1 40); do
  out=$(.venv/bin/python build-prep/memory-archaeology/archaeology_mine.py 2400 60 2>&1)
  total=$(echo "$out" | grep -oE '"design_intent_total": [0-9]+' | grep -oE '[0-9]+' | tail -1)
  echo "[$(date +%H:%M)] iter $i → design_intent_total=$total"
  # FAIL-LOUD dry-check (2026-07-08): an EMPTY total is a FAILED iteration, never "dry" —
  # the first drain exited on two consecutive crashes matching ""=="" (a dishonest DRY).
  if [ -z "$total" ]; then
    echo "  iter $i FAILED (no total) — tail of output:"; echo "$out" | tail -5
    fails=$((${fails:-0}+1)); [ "$fails" -ge 3 ] && { echo "3 consecutive FAILURES — aborting loud"; exit 1; }
    continue
  fi
  fails=0
  [ "$total" = "$prev" ] && { echo "DRY at $total — re-mine complete"; break; }
  prev=$total
done
echo "REMINE_DRAIN_DONE total=$prev"
