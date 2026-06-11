"""session_capabilities.py — R1-prime reduction registry: ④'s IN-SESSION capabilities (code-intel,
computer-use). The structural truth (arch §1.1): a supervised session is `--allowedTools mcp__company`
(session_supervisor.py:328) — NO Bash/Edit/LSP/WebFetch. So these need the WIDER R1-prime spawn, and
the reply rides back as PROSE over turn_text — physically NO typed return_shape. Every capability here
is therefore `liveness: stream`, `return_shape: None` (honest; the grounded-chain law forbids binding a
UI to model narration as if it were data).

requires_tool_grant surfaces the REAL sandbox boundary (§5.4) — the wider tools the R1-prime spawn must
grant beyond mcp__company (Atlas tool names verified 2026-06-12: LSP rides the Read/Edit family;
WebFetch/WebSearch are -p-grantable). act_caveats surfaces the host boundaries LOUD: computer-use
`browser` is beta AND not-WSL; `computer` is macOS+interactive-only (NEVER on a headless -p Linux rail).
"""
from __future__ import annotations

# capability key -> the R1-prime row.
SESSION_CAPABILITIES = {
    "dev.code_intel": dict(
        liveness="stream", return_shape=None,
        requires_tool_grant=("LSP", "Read", "Edit", "Grep", "Glob"),
        acts={
            "definition": {}, "references": {}, "hover": {}, "document-symbols": {},
            "workspace-symbol": {}, "implementations": {}, "call-hierarchy": {}, "diagnostics": {},
        },
        teach="code-intel runs the native LSP tool IN-SESSION (R1-prime wider spawn); the result is "
              "assistant PROSE on the turn stream — liveness:stream, NO typed return_shape (§1.1)."),
    "dev.computer_use": dict(
        liveness="stream", return_shape=None,
        requires_tool_grant=("WebFetch", "WebSearch"),
        acts={
            "web-fetch":  {"beta": False, "not_wsl": False},
            "web-search": {"beta": False, "not_wsl": False},
            "browser":    {"beta": True,  "not_wsl": True},   # Claude-in-Chrome: beta + NOT WSL
            "computer":   {"beta": True,  "not_wsl": True},   # API computer-use: macOS+interactive only
        },
        teach="computer-use: web-fetch/web-search are -p-grantable session tools; browser (Claude-in-"
              "Chrome) is beta + NOT-WSL; computer is macOS+interactive-only — both refused LOUD on this "
              "headless WSL host, never green-painted (§5.4). Result is prose — liveness:stream, no return_shape."),
}


def capability_for(key: str) -> dict:
    """The R1-prime row for a capability key. FAILS LOUD (KeyError) on unknown."""
    if key not in SESSION_CAPABILITIES:
        raise KeyError(f"session_capabilities: no capability for {key!r} — known: "
                       f"{sorted(SESSION_CAPABILITIES)}")
    return SESSION_CAPABILITIES[key]


def requires_tool_grant(key: str) -> tuple:
    """The tools the R1-prime spawn must grant beyond mcp__company for this capability (§5.4)."""
    return tuple(capability_for(key)["requires_tool_grant"])


def act_caveats(key: str, act: str) -> dict:
    """The host-boundary caveats for one act ({beta, not_wsl}). FAILS LOUD (ValueError) on an act this
    capability does not model — never a silent 'no caveats' for an unknown act (§5.4 honesty)."""
    acts = capability_for(key)["acts"]
    if act not in acts:
        raise ValueError(f"session_capabilities.act_caveats({key!r}, {act!r}): act not modelled — "
                         f"known acts: {sorted(acts)} (fail loud, never a silent default).")
    c = acts[act]
    return {"beta": bool(c.get("beta", False)), "not_wsl": bool(c.get("not_wsl", False))}
