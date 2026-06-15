#!/usr/bin/env bash
# claude-fabric.sh — auto-join the Company cross-session channel fabric on every interactive launch.
#
# Tim-authorized 2026-06-15 ("yes you have permission to make it automatically for each session").
# The connect-time self-registration ALREADY existed (company_channel.mjs writeReg on load); what was
# missing was attaching the channel server + the inbound-push flag to every launch. This wrapper adds
# exactly the verified-working incantation (observed on the live members):
#   claude --mcp-config <channel.mcp.json> --dangerously-load-development-channels server:company-channel
# then execs the REAL claude binary by FULL PATH (never the `claude` alias → no recursion), passing ALL
# args through ("$@" — so --resume / prompts / flags survive). Falls through to a plain launch if the
# channel config is missing, so it NEVER blocks a launch (fail-safe, not fail-closed).
#
# Wired as `alias claude=...this script...` in ~/.bashrc (interactive shells only — so Tim's sessions
# auto-join the fabric, while non-interactive `claude -p` worker calls get the plain binary, which keeps
# the autonomous-spawn boundary intact). Reversible: remove the alias line / restore ~/.bashrc.bak-fabric.
set -uo pipefail
REAL_CLAUDE="/home/tim/.local/bin/claude"
CH="/home/tim/company/channels/channel.mcp.json"
if [ -x "$REAL_CLAUDE" ] && [ -f "$CH" ]; then
  exec "$REAL_CLAUDE" --mcp-config "$CH" --dangerously-load-development-channels server:company-channel "$@"
else
  # Fail-safe: if the real binary or the channel config is missing, launch plainly (never block Tim).
  exec "${REAL_CLAUDE:-claude}" "$@"
fi
