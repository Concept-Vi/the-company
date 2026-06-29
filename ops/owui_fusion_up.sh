#!/usr/bin/env bash
# ops/owui_fusion_up.sh — bring up the OpenWebUI↔company FUSION GLUE after a (re)start.
# The durable substrate (committed code + company services via `company up` + the fork repo) survives a
# WSL restart; these 5 glue processes were launched by hand and don't. Idempotent: skips a piece already up.
# Run AFTER `company up` (needs the bridge :8770 + vLLM + voice engines) and after OpenWebUI (:8081) is up.
set -u
cd /home/tim/company
OVENV=/home/tim/openwebui-venv/bin/python      # the shims/adapter/room run on the OWUI venv
CVENV=/home/tim/company/.venv/bin/python        # the MCP gateway runs on the company venv
# secrets (gitignored)
TOK=$(grep -m1 "^COMPANY_REMOTE_DEV_TOKEN=" .secrets | cut -d= -f2-)
PW=$(grep -m1 "^OWUI_PASSWORD=" .secrets | cut -d= -f2-)
up(){ curl -s -m2 -o /dev/null "http://127.0.0.1:$1/" 2>/dev/null; }   # crude liveness
start(){ # name port "cmd..."
  local name=$1 port=$2; shift 2
  if (exec 3<>/dev/tcp/127.0.0.1/$port) 2>/dev/null; then echo "  ✓ $name already up (:$port)"; exec 3>&- 2>/dev/null; return; fi
  setsid "$@" >"/tmp/fusion_${name}.out" 2>&1 & disown
  sleep 1; echo "  → started $name (:$port) → /tmp/fusion_${name}.out"
}
echo "Bringing up OpenWebUI↔company fusion glue…"
start tts_shim   4200 $OVENV ops/tts_openai_shim.py
start stt_shim   4201 $OVENV ops/stt_openai_shim.py
start operator   4300 $OVENV ops/fabric_openai_adapter.py
start mcp_gateway 8773 env COMPANY_REMOTE_DEV_TOKEN="$TOK" $CVENV mcp_face/remote.py 8773
start owui_room 8782 env OWUI_PASSWORD="$PW" $OVENV ops/owui_room.py
echo "Done. (Verify: voice in OWUI, the 'operator' model, and 70 fabric tools via the gateway.)"
