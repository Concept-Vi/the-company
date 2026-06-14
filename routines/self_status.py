"""routines/self_status.py — a sample ROUTINE (S-R9.1): the Company asks a fresh session to report
its own health. Pure data (imports + one ROUTINE dict), mirroring platforms/claude_code.py.

This is the canonical first routine: it drives a real Claude Code session in the Company repo, asks
for a one-line self-status, and captures the reply — the smallest end-to-end proof that a routine
fires through the supervisor. Cadence is descriptive (the schedule arm reads it); fire it now via
the `routines` MCP tool op=fire or runtime.routine_runner.fire('self_status')."""
from __future__ import annotations

ROUTINE = {
    "id": "self_status",
    "label": "Self status",
    "description": "Fire a session that reports the Company's health in one line.",
    "prompt": ("In ONE short line, state that you are a Company routine session running, the current "
               "working directory, and that you can reach the company MCP. Reply with just that line."),
    "cwd": "/home/tim/company",
    "permission_mode": "plan",
    "cadence": "OnCalendar=*-*-* 09:00:00",
    "repeats": False,
    "max_turns": 1,
    "trigger": "daily morning health check (schedule arm) or manual op=fire",
}
