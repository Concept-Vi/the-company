"""mcp_face/tools/jobs.py — the PARAMETRIC JOB SYSTEM's agent face (file-drop tool).

One noun, one tool: an agent registers a job as a data row (what-to-run · params · trigger · allocations),
lists/inspects them, and fires one — through the SAME shared functions the UI face will call (runtime/jobs.py;
one function → two faces). Skeleton scope: define / list / describe / fire (manual). Triggers + the
change-driven heartbeat land next (the TriggerDriver on the ActivationCaller tick).

Validation TEACHES: a bad row comes back with the field path, what-was-got, what's expected, the closest
valid value, and a fix fragment to merge + resubmit — never a bare error.
"""
from __future__ import annotations

from typing import Literal

OPS = ("define", "list", "describe", "fire", "vocabulary")


def register(mcp, suite):
    @mcp.tool()
    def jobs(op: Literal["define", "list", "describe", "fire", "vocabulary"],
             job: dict | None = None, id: str = "", params: dict | None = None,
             check: bool = False) -> dict:
        """Register + run PARAMETRIC JOBS (data rows: what-to-run · params · trigger · allocations · outputs).
        The job body reuses the cascade executor; jobs are the trigger/registry layer above it. Pick `op`:

          op="vocabulary" — the job-row schema + run/trigger kinds + a worked example (self-description).
          op="define"     — author/update a job row (`job`=the row). `check=true` validates WITHOUT saving.
                            A bad row returns a teaching refusal (field path + expected + closest + fix).
          op="list"       — every registered job (id · label · run kind · trigger · enabled).
          op="describe"   — one job, fully (`id`=the job id).
          op="fire"       — run a job NOW: a registered one (`id` + optional `params`), or an inline body
                            (`job`=a full job dict — ephemeral, recorded, not registered). Manual only.
        """
        from runtime import jobs as J
        if op == "vocabulary":
            return {"op": "vocabulary", "job_fields": list(J.JOB_FIELDS), "run_kinds": list(J.RUN_KINDS),
                    "trigger_kinds": list(J.TRIGGER_KINDS),
                    "note": ("skeleton: fires manual only; triggers/heartbeat land next. The run body reuses "
                             "a saved cascade (run={cascade:<name>}) or an inline decl (run={cascade_inline:{steps:[…]}})."),
                    "example": {"id": "redescribe-changed", "label": "Re-describe changed files",
                                "description": "Run the describe cascade over a passed file list.",
                                "run": {"cascade": "ask-the-codebase"},
                                "params": {"scope": {"desc": "files to process", "default": None}},
                                "allocations": {"max_tokens": 1200}, "proposes_only": True}}
        if op == "define":
            if not isinstance(job, dict):
                raise ValueError("jobs(op='define') requires `job` (the job row dict).")
            if check:
                return {"op": "define", "checked": True,
                        **J.build_job(job, cascades={c["name"] for c in suite.cascade_registry.all()})}
            return {"op": "define", **J.save_job(suite, job)}
        if op == "list":
            rows = J.list_jobs(suite)
            return {"op": "list", "count": len(rows),
                    "jobs": [{"id": r["id"], "label": r.get("label", ""), "run": list(r.get("run", {}))[:1],
                              "trigger": (r.get("trigger") or {}).get("kind", "manual"),
                              "enabled": r.get("enabled", True)} for r in rows]}
        if op == "describe":
            if not id:
                raise ValueError("jobs(op='describe') requires `id`.")
            row = J.get_job(suite, id)
            if row is None:
                return {"op": "describe", "found": False,
                        "note": f"no job {id!r} — jobs are {[j['id'] for j in J.list_jobs(suite)]}"}
            return {"op": "describe", "found": True, "job": row}
        if op == "fire":
            if job is not None:
                return {"op": "fire", **J.run_job(suite, job=job, params=params)}
            if not id:
                raise ValueError("jobs(op='fire') requires `id` (a saved job) or `job` (an inline dict).")
            return {"op": "fire", **J.run_job(suite, job_id=id, params=params)}
        raise ValueError(f"jobs: unknown op {op!r} — one of {OPS}.")
