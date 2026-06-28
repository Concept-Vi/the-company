#!/usr/bin/env bash
# ops/ledger_interpret_codex_drive.sh — rate-limit-resilient Codex lane for counterpart-design.
# Loops the codex producer (which SKIPS already-done files) + ingests, until the project's gate is empty.
# If a pass makes NO progress (≈ hit a ChatGPT rate limit), it backs off and retries — so it resumes
# automatically when the limit resets. Crash/limit-safe: every done file is a committed scratch JSON.
set -u
cd /home/tim/company
export PATH="/home/linuxbrew/.linuxbrew/bin:$PATH"
PY=.venv/bin/python
PROJECT=${PROJECT:-counterpart-design}
CONC=${CONC:-3}
CHUNK=${CHUNK:-120}
BACKOFF=${BACKOFF:-900}          # seconds to wait after a no-progress pass (rate-limit reset window)
LOG=build-prep/the-one-system/interpret/codex-drive.log
remaining_of(){ $PY ops/ledger_interpret.py gate 2>/dev/null | $PY -c "import json,sys;print(json.load(sys.stdin).get('$PROJECT',{}).get('remaining','?'))"; }
echo "[codex-drive] start $(date -u +%H:%M:%S) project=$PROJECT" >> "$LOG"
for iter in $(seq 1 80); do
  $PY ops/ledger_interpret.py ingest --wave build-prep/the-one-system/interpret/wave-codex >/dev/null 2>>"$LOG"
  BEFORE=$(remaining_of)
  echo "[codex-drive] iter $iter remaining=$BEFORE $(date -u +%H:%M:%S)" >> "$LOG"
  [ "$BEFORE" = "0" ] && { echo "[codex-drive] DONE" >> "$LOG"; break; }
  # the ONE source-driven producer (backend=codex) — consolidates the codex lane (Tim 2026-06-28).
  $PY ops/ledger_interpret_producer.py --project "$PROJECT" --backend codex --limit "$CHUNK" --concurrency "$CONC" >> "$LOG" 2>&1
  PRC=$?
  if [ "$PRC" = "3" ]; then
    echo "[codex-drive] HELD: terminal backend error (out of credits / auth) — NOT retrying. Add ChatGPT/codex credits to resume; the kimi lane covers the whole sweep meanwhile. $(date -u +%H:%M:%S)" >> "$LOG"
    break
  fi
  $PY ops/ledger_interpret.py ingest --wave build-prep/the-one-system/interpret/wave-codex >/dev/null 2>>"$LOG"
  AFTER=$(remaining_of)
  echo "[codex-drive] iter $iter after=$AFTER" >> "$LOG"
  if [ "$AFTER" = "$BEFORE" ]; then
    echo "[codex-drive] NO PROGRESS (transient — likely rate-limited) → backoff ${BACKOFF}s $(date -u +%H:%M:%S)" >> "$LOG"
    sleep "$BACKOFF"
  fi
done
echo "[codex-drive] end $(date -u +%H:%M:%S)" >> "$LOG"
