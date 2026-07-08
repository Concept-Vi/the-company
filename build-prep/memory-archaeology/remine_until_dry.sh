#!/usr/bin/env bash
# Drain the archaeology to TRUE dry (external-reference law): dry = a full pass over the WHOLE
# derived transcript universe with zero new captures and zero failures — reported by the driver
# itself as "dry": true. Empty output = a FAILED iteration (3-strike loud abort), never dry.
cd /home/tim/company
fails=0
for i in $(seq 1 500); do
  out=$(.venv/bin/python build-prep/memory-archaeology/archaeology_mine.py 2400 60 2>&1)
  total=$(echo "$out" | grep -oE '"design_intent_total": [0-9]+' | grep -oE '[0-9]+' | tail -1)
  new=$(echo "$out" | grep -oE '"new_this_batch": [0-9]+' | grep -oE '[0-9]+' | tail -1)
  dry=$(echo "$out" | grep -c '"dry": true')
  echo "[$(date +%H:%M)] iter $i → total=$total new=$new dry=$dry"
  if [ -z "$total" ]; then
    echo "  iter $i FAILED (no total) — tail:"; echo "$out" | tail -5
    fails=$((fails+1)); [ "$fails" -ge 3 ] && { echo "3 consecutive FAILURES — aborting loud"; exit 1; }
    continue
  fi
  fails=0
  [ "$dry" -ge 1 ] && { echo "TRUE DRY at $total (full universe pass, zero new, zero failures)"; break; }
done
echo "REMINE_DRAIN_DONE total=$total"
