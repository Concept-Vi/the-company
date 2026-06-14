"""tests/ci_scaffold_acceptance.py — S-R9.1 CI scaffolder (CC-30): generates GitHub/GitLab workflow
files from a routine, maps cadence→cron, falls back to on-demand, fail-loud on bad provider.
Pure generation — no network, no install."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from runtime.routines import Routine, routine_registry
from runtime.ci_scaffold import github_workflow, gitlab_job, scaffold_from_routine, _cadence_to_cron

PASS, FAIL = [], []
def check(n, c, d=""):
    (PASS if c else FAIL).append(n); print(f"  {'PASS' if c else 'FAIL'}  {n}" + (f"  — {d}" if d and not c else ""))

# cadence → cron
check("1 daily OnCalendar → cron HH:MM", _cadence_to_cron("OnCalendar=*-*-* 09:00:00") == "0 9 * * *")
check("2 every:7200 (2h) → cron every 2 hours", _cadence_to_cron("every:7200") == "0 */2 * * *")
check("3 unmappable cadence → None (on-demand, not fabricated)", _cadence_to_cron("OnCalendar=Mon *-*-* 09:00:00") is None)

# github workflow
wf = github_workflow("daily-report", 'Summarize "yesterday"', cron="0 9 * * *", model="opus")
check("4 github workflow uses claude-code-action@v1 + the api-key secret",
      "anthropics/claude-code-action@v1" in wf and "secrets.ANTHROPIC_API_KEY" in wf)
check("5 github workflow embeds the prompt (quotes neutralised) + schedule cron",
      "Summarize 'yesterday'" in wf and 'cron: "0 9 * * *"' in wf)
# on-demand fallback (no cron) → issue_comment trigger
wf2 = github_workflow("mention", "do x", cron=None)
check("6 no cron → on-demand @claude (issue_comment) trigger", "issue_comment" in wf2 and "schedule" not in wf2)

# gitlab job
gj = gitlab_job("Review this MR", model="opus")
check("7 gitlab job runs headless claude -p with mcp__gitlab in allowedTools",
      "claude -p" in gj and "mcp__gitlab" in gj and "--model opus" in gj)

# scaffold_from_routine
g = scaffold_from_routine(routine_registry()["self_status"], provider="github")
check("8 scaffold_from_routine(github) targets .github/workflows and is scheduled (self_status has a cadence)",
      g["target_path"].startswith(".github/workflows/") and g["scheduled"] is True)
gl = scaffold_from_routine(Routine("r", {"id": "r", "prompt": "p"}), provider="gitlab")
check("9 scaffold_from_routine(gitlab) targets .gitlab-ci.yml", ".gitlab-ci.yml" in gl["target_path"])
check("10 GENERATES-NOT-INSTALLS note present (run is off-machine)",
      "off-machine" in g["note"].lower() and "not the Company" in g["note"])
try:
    scaffold_from_routine(routine_registry()["self_status"], provider="bitbucket"); check("11 bad provider fails loud", False)
except ValueError as e:
    check("11 bad provider fails loud", "unknown provider" in str(e))

print(f"\n{'='*56}\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL: print("FAILED:", ", ".join(FAIL)); sys.exit(1)
print("ALL GREEN — S-R9.1 CI scaffolder: github/gitlab workflow generation, cadence→cron, generates-not-installs.")
