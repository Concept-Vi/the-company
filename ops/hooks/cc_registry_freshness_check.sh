#!/usr/bin/env bash
# ops/hooks/cc_registry_freshness_check.sh — SessionStart hook: warn if the capability registry
# stamp is stale (Mirror-Registry System, LANE-REFRESH, F-FIX-13 / C-REF-1).
#
# HOW THIS WORKS:
#   Wired as a Claude Code SessionStart hook via .claude/settings.json.  Runs at the start of
#   every session.  Compares the live binary version (claude --version) against the stored stamp
#   (store/claude-code.version_stamp).  Emits a WARNING to stdout if stale — Claude Code injects
#   it as additionalContext for the session.  NON-BLOCKING: exits 0 regardless (a stale registry
#   is a warning, not a hard session block; the curator gate is in the refresh flow itself).
#
# FAIL POSTURES:
#   - binary not found                 → warn "REGISTRY FRESHNESS: binary unreachable" + exit 0
#   - stamp file missing               → warn "REGISTRY FRESHNESS: never built — run cc_registry_refresh"
#   - stamp found but stale            → warn "REGISTRY FRESHNESS: stale (stamp=X live=Y)"
#   - stamp found and current          → silent (no noise in a fresh session)
#   - any unexpected error             → warn "REGISTRY FRESHNESS: check failed (detail)" + exit 0
#
# Never writes the stamp (propose-only stance; stamp write is post-curator-approval governance).
# Never spawns a claude subprocess (only claude --version is called, which is sub-second).
#
# PATTERN NOTE: this is the FIRST file in ops/hooks/ — a NEW pattern (F-FIX-13). No existing
# ops/hooks/ template exists; the wiring model is .claude/settings.json SessionStart (live in
# the harness) with a command: path entry pointing here.

set -euo pipefail

COMPANY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAMP_FILE="$COMPANY_ROOT/store/claude-code.version_stamp"
CLAUDE_BIN="${COMPANY_CLAUDE_BIN:-claude}"

# Capture the SessionStart hook stdin (Claude Code's {session_id, transcript_path, cwd, …}) for the
# #69 self-marker write below. tty-guarded so a MANUAL run (no piped stdin) never hangs on cat.
HOOK_STDIN=""
if [ ! -t 0 ]; then HOOK_STDIN="$(cat 2>/dev/null || true)"; fi

# ── #69 SELF-MARKER (FAILURE-ISOLATED — runs fabric-wide on EVERY session-start; a failure here must
#    NEVER break anyone's session-start). The whole block is wrapped so any error → silent continue:
#    the marker-write degrades to no-marker (= today's behaviour) and the freshness check proceeds.
#    Isolation proven by use (empty/malformed/no-sid/unwritable stdin all exit 0). ──
{
    if [ -n "$HOOK_STDIN" ]; then
        printf '%s' "$HOOK_STDIN" | "${COMPANY_PYTHON:-python3}" "$COMPANY_ROOT/ops/hooks/write_self_marker.py" || true
    fi
} >/dev/null 2>&1 || true

# Suppress all output if nothing is stale (clean session, no noise)
warn() {
    echo "REGISTRY FRESHNESS: $*"
}

# ── resolve the binary ─────────────────────────────────────────────────────────────────────────
if ! command -v "$CLAUDE_BIN" >/dev/null 2>&1; then
    CLAUDE_BIN="$HOME/.local/bin/claude"
fi
if [ ! -x "$CLAUDE_BIN" ] && ! command -v claude >/dev/null 2>&1; then
    warn "binary unreachable — cannot check freshness. Run: company up"
    exit 0
fi
CLAUDE_BIN="${CLAUDE_BIN:-claude}"

# ── read live version ──────────────────────────────────────────────────────────────────────────
LIVE_VERSION="$("$CLAUDE_BIN" --version 2>/dev/null | sed 's/ (Claude Code)//' | awk '{print $1}')" || true
if [ -z "$LIVE_VERSION" ]; then
    warn "version probe returned empty — binary may not be responding. Run cc_registry_refresh when ready."
    exit 0
fi

# ── compare against the stamp ──────────────────────────────────────────────────────────────────
if [ ! -f "$STAMP_FILE" ]; then
    warn "stamp missing — registry has NEVER been built for this binary. Run flow cc_registry_refresh to build it."
    exit 0
fi

STAMPED_VERSION="$(tr -d '[:space:]' < "$STAMP_FILE")"

if [ "$STAMPED_VERSION" != "$LIVE_VERSION" ]; then
    warn "STALE — stamp=$STAMPED_VERSION live=$LIVE_VERSION. Run flow cc_registry_refresh to refresh and surface novelty."
    exit 0
fi

# ── current — no output, clean session ────────────────────────────────────────────────────────
# stamp == live version: registry is fresh, silent exit.
exit 0
