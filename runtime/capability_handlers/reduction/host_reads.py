"""host_reads.py — DECLARATIVE-DIRECT reduction registry: the redacted host READS (safe on every face,
incl. a cold external agent — they shell nothing dangerous, write nothing, spawn nothing).

  · auto.auth (CC-24.1, reopened) — the credential METHOD, REDACTED. `claude auth status` outputs JSON
    (Atlas cli-reference: "Show authentication status as JSON … Exits 0 if logged in, 1 if not").
    redaction_for() lists the fields that MUST be stripped (the secret NEVER transits — §5.2 C3).
    NO setup-token/relogin/logout ROW (those are host acts — absence IS the boundary, §1.8/§5.2).
  · auto.cost (CC-20) — a FOLD over the agent_sessions.turn `usage` field ALREADY stamped by
    session_supervisor._extract_usage (verified built, §1.5 — NOT net-new). source="turn-usage-fold".
  · auto.routines (CC-21) — cloud routines are Anthropic-resident; a thin native `schedule list` read.
"""
from __future__ import annotations

HOST_READS = {
    "auto.auth": dict(
        source="claude-auth-status", argv=["auth", "status"],
        redact=("token", "api_key", "apiKey", "secret", "CLAUDE_CODE_OAUTH_TOKEN",
                "oauth", "accessToken", "refreshToken"),
        schema="auth.status",
        teach="auth.get returns the credential METHOD (subscription/console-api/token) + account label, "
              "REDACTED — never the secret. setup-token/relogin/logout are HOST acts (no company op)."),
    "auto.cost": dict(
        source="turn-usage-fold", event_kind="agent_sessions.turn", field="usage",
        schema="cost-usage.fold",
        teach="cost.read folds the `usage` block already stamped on agent_sessions.turn events "
              "(session_supervisor._extract_usage). costUSD is a CLIENT-SIDE ESTIMATE, not the bill."),
    "auto.routines": dict(
        source="claude-schedule-list", argv=["schedule", "list"], redact=(),
        schema="routines.list",
        teach="routines.list reads cloud routines (Anthropic-resident) via the native schedule surface "
              "— a thin host read, not a company datastore."),
}


def read_for(key: str) -> dict:
    """The direct-read row for a key. FAILS LOUD (KeyError) on unknown."""
    if key not in HOST_READS:
        raise KeyError(f"host_reads: no read for {key!r} — known: {sorted(HOST_READS)}")
    return HOST_READS[key]


def redaction_for(key: str) -> tuple:
    """The fields that MUST be stripped from this read's output (the secret never transits, §5.2 C3)."""
    return tuple(read_for(key).get("redact", ()))
