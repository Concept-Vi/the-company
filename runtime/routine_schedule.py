"""runtime/routine_schedule.py — the S-R9.1 SCHEDULE ARM: generate a per-routine systemd .timer +
.service from a routine's `cadence`, mirroring ops/systemd/company-agent-sessions-exporter.{timer,
service} (the established Company periodic-job convention, bound to company.target so it rises/falls
with the Company and shows under `company status`).

GENERATES, NEVER ARMS. This writes the unit files to ops/systemd/generated/ and emits the suggested
ops/services.json jobs entry + the enable command — it does NOT `systemctl enable` anything and does
NOT edit the live services.json. ARMING a recurring `claude -p` timer is an autonomous self-firing
spawn loop: that is the operator's deliberate one-command step (the lead-only-spawn rule), never an
auto-armed loop. So the capability is built + verifiable; arming stays Tim's call.

Cadence grammar (from the routine's `cadence` field):
  - "OnCalendar=<expr>"  → used verbatim as the [Timer] OnCalendar= directive (systemd calendar).
  - "every:<seconds>"    → OnUnitActiveSec=<seconds> + OnBootSec=<seconds> (interval timer).
"""
from __future__ import annotations

import os

from runtime.routines import Routine, routine_registry

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN_DIR = os.path.join(REPO_ROOT, "ops", "systemd", "generated")
VENV_PY = os.path.join(REPO_ROOT, ".venv", "bin", "python")


class ScheduleError(ValueError):
    """A routine cannot be scheduled (no/!malformed cadence) — raised TEACHING-loud."""


def _timer_directive(cadence: str) -> str:
    """Map a routine cadence → the systemd [Timer] line. Fail loud on an unparseable cadence."""
    c = (cadence or "").strip()
    if c.startswith("OnCalendar="):
        expr = c[len("OnCalendar="):].strip()
        if not expr:
            raise ScheduleError("cadence 'OnCalendar=' has no expression — e.g. 'OnCalendar=*-*-* 09:00:00'.")
        return f"OnCalendar={expr}"
    if c.startswith("every:"):
        sec = c[len("every:"):].strip()
        if not sec.isdigit() or int(sec) < 1:
            raise ScheduleError(f"cadence 'every:{sec}' — seconds must be a positive integer.")
        return f"OnUnitActiveSec={sec}s\nOnBootSec={sec}s"
    raise ScheduleError(
        f"unschedulable cadence {cadence!r} — grammar is 'OnCalendar=<expr>' or 'every:<seconds>'. "
        f"A routine with no cadence is fire-only (run it via the `routines` tool op=fire).")


def unit_names(routine_id: str) -> tuple:
    base = f"company-routine-{routine_id}"
    return f"{base}.service", f"{base}.timer"


def render_units(routine: Routine) -> tuple:
    """Return (service_text, timer_text) for a routine — pure (unit-testable, no file IO)."""
    if not routine.cadence:
        raise ScheduleError(
            f"routine {routine.id!r} declares no cadence — it is fire-only. Add a `cadence` "
            f"('OnCalendar=…' or 'every:<seconds>') to schedule it.")
    timer_line = _timer_directive(routine.cadence)
    svc_name, _ = unit_names(routine.id)
    service = f"""[Unit]
Description=Company routine '{routine.id}' — {routine.spec.get('label') or routine.id} (oneshot; the .timer fires it)
Documentation=file://{os.path.join(REPO_ROOT, 'runtime', 'routine_runner.py')}

[Service]
Type=oneshot
WorkingDirectory={REPO_ROOT}
ExecStart={VENV_PY} -m runtime.routine_runner {routine.id}
Nice=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=company-routine-{routine.id}
"""
    timer = f"""[Unit]
Description=Company routine '{routine.id}' timer — cadence {routine.cadence!r} (S-R9.1 schedule arm)

[Timer]
{timer_line}
Persistent=true
Unit={svc_name}

[Install]
# Bound to company.target (not bare timers.target) so it rises/falls with the Company and
# `company status` shows it as a managed member — no invisible orphan timer (Tim's requirement).
WantedBy=company.target
"""
    return service, timer


def generate_units(routine_or_id, *, dest_dir: str = GEN_DIR) -> dict:
    """Write the .service + .timer to dest_dir. Returns paths + the suggested services.json jobs
    entry + the (operator-run) enable command. Does NOT enable; does NOT touch the live services.json."""
    routine = routine_or_id if isinstance(routine_or_id, Routine) else routine_registry()[routine_or_id]
    service_text, timer_text = render_units(routine)
    os.makedirs(dest_dir, exist_ok=True)
    svc_name, timer_name = unit_names(routine.id)
    svc_path = os.path.join(dest_dir, svc_name)
    timer_path = os.path.join(dest_dir, timer_name)
    with open(svc_path, "w", encoding="utf-8") as f:
        f.write(service_text)
    with open(timer_path, "w", encoding="utf-8") as f:
        f.write(timer_text)
    services_entry = {
        f"routine-{routine.id}": {
            "group": "jobs",
            "title": f"Routine: {routine.spec.get('label') or routine.id}",
            "manage": {"type": "user-unit", "unit": timer_name},
        }
    }
    return {
        "routine_id": routine.id,
        "service_path": svc_path,
        "timer_path": timer_path,
        "services_json_entry": services_entry,
        "arm_command": (f"cp {svc_path} {timer_path} ~/.config/systemd/user/ && "
                        f"systemctl --user daemon-reload && systemctl --user enable --now {timer_name}"),
        "note": ("GENERATED, NOT ARMED — arming a recurring claude -p timer is the operator's "
                 "deliberate step (lead-only-spawn). Run arm_command to enable; add services_json_entry "
                 "to ops/services.json for `company status` visibility."),
    }


if __name__ == "__main__":
    import json, sys
    print(json.dumps(generate_units(sys.argv[1] if len(sys.argv) > 1 else "self_status"), indent=2))
