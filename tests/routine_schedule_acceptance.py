"""tests/routine_schedule_acceptance.py — S-R9.1 schedule arm acceptance (no systemctl, no arming).
Proves the generator renders valid systemd units from a routine cadence, fail-loud on bad cadence,
and that it GENERATES-NOT-ARMS (no enable; emits the arm command + services.json entry instead)."""
import os, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from runtime.routines import Routine, routine_registry
from runtime.routine_schedule import render_units, generate_units, _timer_directive, unit_names, ScheduleError

PASS, FAIL = [], []
def check(n, c, d=""):
    (PASS if c else FAIL).append(n); print(f"  {'PASS' if c else 'FAIL'}  {n}" + (f"  — {d}" if d and not c else ""))
def raises(fn, sub=""):
    try: fn(); return False
    except ScheduleError as e: return sub in str(e) if sub else True
    except Exception: return False

# render: OnCalendar
r_cal = Routine("cal", {"id": "cal", "prompt": "p", "cadence": "OnCalendar=*-*-* 09:00:00", "label": "Cal"})
svc, tmr = render_units(r_cal)
check("1 OnCalendar cadence → [Timer] OnCalendar line", "OnCalendar=*-*-* 09:00:00" in tmr)
check("2 .service is a oneshot running routine_runner with the routine id",
      "Type=oneshot" in svc and "-m runtime.routine_runner cal" in svc)
check("3 .timer is bound to company.target (managed member, no orphan)", "WantedBy=company.target" in tmr)
check("4 .timer points at the .service unit", f"Unit={unit_names('cal')[0]}" in tmr)
# render: every:<seconds>
_, tmr_iv = render_units(Routine("iv", {"id": "iv", "prompt": "p", "cadence": "every:3600"}))
check("5 every:<seconds> → OnUnitActiveSec interval", "OnUnitActiveSec=3600s" in tmr_iv and "OnBootSec=3600s" in tmr_iv)
# fail-loud
check("6 no cadence fails loud (fire-only routine)", raises(lambda: render_units(Routine("x", {"id": "x", "prompt": "p"})), "no cadence"))
check("7 unparseable cadence fails loud", raises(lambda: _timer_directive("weekly"), "unschedulable"))
check("8 every:0 fails loud", raises(lambda: _timer_directive("every:0"), "positive integer"))
# generate writes files + emits arm command + services entry, does NOT arm
with tempfile.TemporaryDirectory() as td:
    g = generate_units(r_cal, dest_dir=td)
    check("9 generate writes the .service + .timer files", os.path.isfile(g["service_path"]) and os.path.isfile(g["timer_path"]))
    check("10 generate emits a services.json jobs entry (group=jobs)",
          g["services_json_entry"]["routine-cal"]["group"] == "jobs")
    check("11 GENERATES-NOT-ARMS: arm_command is emitted (operator-run), not executed",
          "systemctl --user enable" in g["arm_command"] and "GENERATED, NOT ARMED" in g["note"])
# the shipped sample is schedulable
check("12 the shipped self_status routine renders (has a cadence)",
      "OnCalendar" in render_units(routine_registry()["self_status"])[1])

print(f"\n{'='*56}\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL: print("FAILED:", ", ".join(FAIL)); sys.exit(1)
print("ALL GREEN — S-R9.1 schedule arm: cadence→systemd units, fail-loud, generates-not-arms.")
