"""routines/launch-surfaces.py — the LAUNCHER routine (SAFE: approval gates stay ON).

Hands back Tim's two review-surface URLs and their up/down status, so launching is a remembered,
registry-backed thing instead of a command anyone has to recall. It does NOT auto-restart with
disabled approvals — if a server is down it says so; restarting (engine/serve.sh) is a gated action a
person/agent confirms. Fire via the `routines` MCP tool op=fire, or routine_runner.fire('launch-surfaces')."""
from __future__ import annotations

ROUTINE = {
    "id": "launch-surfaces",
    "label": "Launch Tim's surfaces",
    "description": "Report the DNA gallery + live-surface phone URLs and whether each is up; flag if a restart is needed.",
    "prompt": (
        "Report Tim's two review-surface URLs and their status. "
        "Check the gallery with  curl -s -o /dev/null -w '%{http_code}' http://localhost:8090/  and the surface with "
        "curl -s -o /dev/null -w '%{http_code}' http://localhost:5174/  (read-only). "
        "If the gallery is NOT 200, say it's DOWN and that an agent should run "
        "/home/tim/repos/counterpart/design/engine/serve.sh to restart it (a person/agent confirms that — do not force it). "
        "Reply with EXACTLY:\n"
        "  Gallery:  https://workstation001.tail777bc2.ts.net          (up/down)\n"
        "  Surface:  https://workstation001.tail777bc2.ts.net:8443     (up/down)"
    ),
    "cwd": "/home/tim/repos/counterpart/design",
    "permission_mode": "default",
    "cadence": "manual (op=fire)",
    "repeats": False,
    "max_turns": 4,
    "trigger": "manual — fire when Tim wants his surface URLs + their status",
}
