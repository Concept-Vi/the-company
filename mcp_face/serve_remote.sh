#!/usr/bin/env bash
# Canonical launch for the remote MCP connector front (mcp_face/remote.py).
# This is the SINGLE source of the connector's run env — used both for a manual
# launch and as the ExecStart of the company-managed service (durability: a loose
# nohup died once and took the whole connector down — 2026-06-22).
#
# Chain: app -> claude-design-gateway (Supabase edge, OAuth resource) -> Tailscale
# Funnel (https://workstation001.tail777bc2.ts.net -> 127.0.0.1:8772) -> this.
# Identity IS the gate: a JWKS-verified sub == OPERATOR_USER_ID -> all tools;
# any other valid Supabase user -> client tier; no/invalid token -> 401.
set -euo pipefail
cd "$(dirname "$0")/.."   # the company root

export SUPABASE_JWKS_URL="${SUPABASE_JWKS_URL:-https://gctunhsuwpaxeatwlmuv.supabase.co/auth/v1/.well-known/jwks.json}"
export SUPABASE_JWT_AUDIENCE="${SUPABASE_JWT_AUDIENCE:-authenticated}"
export OPERATOR_USER_ID="${OPERATOR_USER_ID:-ebe5f9c7-4d66-4717-835f-afc96088facb}"
export REMOTE_PUBLIC="${REMOTE_PUBLIC:-1}"   # public-facing via the Funnel -> dev-token bypass HARD-disabled
export PUBLIC_RESOURCE_URL="${PUBLIC_RESOURCE_URL:-https://workstation001.tail777bc2.ts.net}"
export PUBLIC_AS_URL="${PUBLIC_AS_URL:-https://gctunhsuwpaxeatwlmuv.supabase.co/auth/v1}"

exec .venv/bin/python mcp_face/remote.py "${1:-8772}"
