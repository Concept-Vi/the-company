#!/usr/bin/env bash
# ops/ledger_interpret_drive.sh — unattended driver for the kimi interpretive sweep.
# Loops: ingest ALL existing waves (idempotent — catches any partials) → gate → if files remain, queue a new
# wave and run the kimi producer → repeat. Stops when the gate reads 0 remaining across all projects.
# Zero Claude tokens (kimi via ollama). Crash-safe: every wave checkpoints to the ledger; a rerun resumes.
set -u
cd /home/tim/company
PY=.venv/bin/python
WAVE_FILES=${WAVE_FILES:-6}
MAX_BATCHES=${MAX_BATCHES:-120}     # ~ files per wave = MAX_BATCHES (small batches → ~120-360 files/wave)
CONC=${CONC:-5}
LOG=build-prep/the-one-system/interpret/drive.log
echo "[drive] start $(date -u +%H:%M:%S)" >> "$LOG"

for iter in $(seq 1 60); do
  # 1. ingest every existing wave (idempotent; absorbs partials incl. the retired wave-007)
  for d in build-prep/the-one-system/interpret/wave-*/; do
    [ -d "$d/out" ] && $PY ops/ledger_interpret.py ingest --wave "${d%/}" >/dev/null 2>>"$LOG"
  done
  # 2. gate — remaining across all projects
  REM=$($PY ops/ledger_interpret.py gate 2>>"$LOG" | $PY -c "import json,sys;d=json.load(sys.stdin);print(sum(v['remaining'] for v in d.values()))")
  echo "[drive] iter $iter: remaining=$REM $(date -u +%H:%M:%S)" >> "$LOG"
  if [ "$REM" = "0" ]; then echo "[drive] DONE — gate empty" >> "$LOG"; break; fi
  # 3. queue a new wave over the remainder
  WD=$($PY ops/ledger_interpret.py queue --wave-files "$WAVE_FILES" --max-batches "$MAX_BATCHES" 2>>"$LOG" | $PY -c "import json,sys;print(json.load(sys.stdin)['wave_dir'])")
  [ -z "$WD" ] && { echo "[drive] no wave queued, stop" >> "$LOG"; break; }
  echo "[drive] producing $WD" >> "$LOG"
  # 4. run the kimi producer over it (blocks until the wave is done)
  $PY ops/ledger_interpret_ollama.py --wave "$WD" --concurrency "$CONC" >> "$LOG" 2>&1
done
# final ingest + gate
for d in build-prep/the-one-system/interpret/wave-*/; do [ -d "$d/out" ] && $PY ops/ledger_interpret.py ingest --wave "${d%/}" >/dev/null 2>>"$LOG"; done
$PY ops/ledger_interpret.py gate >> "$LOG" 2>&1
echo "[drive] end $(date -u +%H:%M:%S)" >> "$LOG"
