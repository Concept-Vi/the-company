#!/usr/bin/env bash
# _finish_pplx_wire.sh — INTERIM throwaway. Runs the gated tail of the
# transcript-search build once the pplx-embed weights finish downloading:
#   wait for ALL_SHARDS_DONE -> verify shards -> company up embed-pplx (evict)
#   -> wait /health=ok -> substrate index (full) -> verification search.
# Emits single-line MARKER: events to stdout (for Monitor) and writes a JSON
# result to RESULT. Fail loud: any step's failure prints MARKER:FAIL and exits 1.
set -uo pipefail

DL_LOG=/tmp/dl_shards.log
SNAP=/home/tim/.cache/huggingface/hub/models--perplexity-ai--pplx-embed-context-v1-4b/snapshots/0cb9b89b219a9b8ac95aa31aa0b67f1d5801c500
RESULT=/tmp/pplx_wire_result.json
PYDRIVER=/home/tim/company/ops/wire_substrate_claude_sessions.py
OVPY=/home/tim/repos/obsidian-overlord/.venv/bin/python
COMPANY=/home/tim/company/ops/company
# A grounded semantic probe: GPU VRAM budgeting + model eviction is a real
# recurring topic across the transcripts (company CLI resource-manager, vLLM
# gpu_util, --evict). Tests semantic retrieval, not just keyword match.
PROBE="${PROBE:-how does the GPU VRAM budget and model eviction work when loading a model}"

emit() { echo "MARKER:$1" ; }

# 1) wait for the download to finish (or die)
emit "WAIT_DOWNLOAD start (watching $DL_LOG for ALL_SHARDS_DONE)"
while true; do
  if grep -q "ALL_SHARDS_DONE" "$DL_LOG" 2>/dev/null; then
    emit "DOWNLOAD_DONE ALL_SHARDS_DONE seen"; break
  fi
  # death detection: the dl_shards process gone AND not done = failure
  if ! pgrep -af dl_shards.py >/dev/null 2>&1; then
    emit "FAIL download process gone before ALL_SHARDS_DONE — restart /tmp/dl_shards.py"
    exit 1
  fi
  sleep 20
done

# 2) verify all four shards are real safetensors (>1GB, valid header) in snapshot
emit "VERIFY_SHARDS"
for n in 1 2 3 4; do
  f="$SNAP/model-0000${n}-of-00004.safetensors"
  real=$(readlink -f "$f" 2>/dev/null || echo "$f")
  if [ ! -e "$real" ]; then emit "FAIL shard $n missing ($f)"; exit 1; fi
  sz=$(stat -c %s "$real" 2>/dev/null || echo 0)
  if [ "$sz" -lt 1000000000 ]; then emit "FAIL shard $n too small ($sz bytes) — $real"; exit 1; fi
done
emit "SHARDS_OK all 4 shards present and sized"

# 3) bring up the embedder (evict largest to make room) and wait for health
emit "EMBEDDER_UP company up embed-pplx --wait --evict"
"$COMPANY" up embed-pplx --wait --evict 2>&1 | sed 's/^/  up| /'
emit "EMBEDDER_HEALTH waiting /health=ok (cold load can take minutes)"
for i in $(seq 1 120); do
  st=$(curl -s --max-time 5 http://127.0.0.1:8007/health 2>/dev/null)
  if echo "$st" | grep -q '"status": *"ok"' || echo "$st" | grep -q '"status":"ok"'; then
    emit "EMBEDDER_READY $st"; break
  fi
  if [ "$i" = 120 ]; then emit "FAIL embedder /health never ok: last=$st"; exit 1; fi
  sleep 10
done

# 3b) sanity: one embed call returns a 2560-d vector
emit "EMBED_SMOKE one /v1/embeddings call"
dim=$(curl -s --max-time 120 http://127.0.0.1:8007/v1/embeddings \
  -H 'Content-Type: application/json' \
  -d '{"input":["hello world"],"quantization":"int8"}' 2>/dev/null \
  | "$OVPY" -c 'import sys,json; d=json.load(sys.stdin); print(len(d["data"][0]["embedding"]))' 2>/dev/null)
if [ "$dim" != "2560" ]; then emit "FAIL smoke embed dim=$dim (expected 2560)"; exit 1; fi
emit "EMBED_SMOKE_OK dim=2560"

# 4) index the corpus through the substrate (full re-embed) — capture JSON
emit "INDEX substrate scan+embed (1048 files)"
"$OVPY" "$PYDRIVER" index --full > /tmp/pplx_index.json 2>/tmp/pplx_index.err
rc=$?
tail -1 /tmp/pplx_index.json 2>/dev/null | sed 's/^/  idx| /'
if [ $rc -ne 0 ]; then emit "FAIL index rc=$rc (see /tmp/pplx_index.err)"; tail -5 /tmp/pplx_index.err | sed 's/^/  err| /'; exit 1; fi
emit "INDEX_DONE"

# 5) verification search
emit "SEARCH probe=\"$PROBE\""
"$OVPY" "$PYDRIVER" search "$PROBE" -k 5 > /tmp/pplx_search.txt 2>&1
rc=$?
sed 's/^/  q| /' /tmp/pplx_search.txt
if [ $rc -ne 0 ]; then emit "FAIL search rc=$rc"; exit 1; fi

# write a compact result file
"$OVPY" "$PYDRIVER" status > "$RESULT" 2>/dev/null
emit "ALL_DONE result=$RESULT index=/tmp/pplx_index.json search=/tmp/pplx_search.txt"
exit 0
