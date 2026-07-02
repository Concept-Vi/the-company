"""runtime/jobs.py — the PARAMETRIC JOB SYSTEM (the-one-system, substrate lane; walking skeleton).

A JOB is a data row (registry-is-truth, the cascades precedent): {what-to-run · params · trigger ·
allocations · outputs}. It unifies the five job-shaped mechanisms (flows/routines/cascades/graphs/
activation) that each held one piece — see build-prep/the-one-system/plan-a-jobs/DESIGN.md. THIS module
is the skeleton: the registry + the ONE validation door + params-as-data + run_job over the EXISTING
cascade executor (Suite.run_cascade — never a forked runner). Manual-fire only; triggers/heartbeat land next.

RECONCILIATION with ④ THE CONTAINER (build-prep/the-one-system/SUBSTRATE-LANES-RECONCILIATION.md): jobs are
the trigger/registry layer ABOVE ④'s CIRCUIT (L5) consequential-action floor — a job fires → runs a cascade
→ any consequential step routes through CIRCUIT's propose→resolve. The skeleton is manual-fire compute-only
(no triggers, no consequential routing), so it is independent of CIRCUIT and safe to build before L5.
No schema, no migration — pure data rows in .data/store/jobs.json (file-disjoint from every ④ lane).

FLOOR (inherited from flows/cascades): proposes_only default True; the cascade body is run:// computation
only (no resolve/approve/dispatch, no claude -p — the cascade runner already enforces this). Fail-loud with
TEACHING refusals (field path + what-was-got + expected + closest-match + a fix fragment).
"""
from __future__ import annotations
import json
import os
import time

# The closed job-row vocabulary (unknown field FAILS LOUD — the routines.py discipline). Kept flat + jsonb-
# lift-ready so the eventual Supabase move (NORTH-STAR directive 4, deliberately later) is a copy, not a redesign.
JOB_FIELDS = ("id", "label", "description", "run", "params", "allocations", "outputs",
              "trigger", "proposes_only", "enabled", "created_by", "created_at", "version")
RUN_KINDS = ("cascade", "cascade_inline")   # skeleton executor kinds; flow/graph/agent step-kinds land later
TRIGGER_KINDS = ("manual", "schedule", "change", "event", "condition")  # skeleton fires manual only


def _registry(suite):
    """The job registry — ActionRegistry over jobs.json (the SAME store class as cascades; registry-is-
    truth, mtime-fresh across processes, atomic writes). Keyed by the job's `id` (stored as the row's
    `name` so ActionRegistry's name-keying works unchanged)."""
    from runtime.coherence_actions import ActionRegistry
    return ActionRegistry(str(suite.store.root / "jobs.json"))


def _teach(at: str, got, expected: str, *, closest=None, fix=None, why: str = "") -> dict:
    """A fail-loud TEACHING refusal (never a bare error): names the field, what was got, what's expected,
    the closest valid value, and a fix fragment the caller can merge + resubmit."""
    r = {"ok": False, "refused": True, "at": at, "got": got, "expected": expected}
    if closest is not None:
        r["closest"] = closest
    if fix is not None:
        r["fix"] = fix
    if why:
        r["why"] = why
    r["resubmit"] = "jobs(op='define', check=true, job=<your row with the fix applied>)"
    return r


def _closest(word: str, pool) -> list:
    """Cheap closest-match (shared-prefix + substring) for teaching refusals — no dependency."""
    word = str(word or "")
    pool = list(pool)
    scored = sorted(pool, key=lambda c: (-len(os.path.commonprefix([word, c])), abs(len(c) - len(word))))
    return [c for c in scored if os.path.commonprefix([word, c]) or word in c or c in word][:3] or scored[:2]


def build_job(decl: dict, *, cascades: set) -> dict:
    """Validate a job declaration through the ONE door (the build_action precedent). Returns
    {ok:True, job} on success, or a teaching refusal. `cascades` = the live saved-cascade names, so a
    run.cascade referencing an unknown cascade is refused at define-time (never fires into a dangling name)."""
    if not isinstance(decl, dict):
        return _teach("(root)", type(decl).__name__, "a job object (dict)")
    unknown = [k for k in decl if k not in JOB_FIELDS]
    if unknown:
        return _teach(unknown[0], unknown[0], f"a known job field — one of {list(JOB_FIELDS)}",
                      closest=_closest(unknown[0], JOB_FIELDS),
                      why="the job row vocabulary is closed (fail-loud on drift, like routines/flows)")
    jid = decl.get("id")
    if not jid or not isinstance(jid, str):
        return _teach("id", decl.get("id"), "a non-empty string id (addressable as job://<id>)")
    for req in ("label", "description"):
        if not decl.get(req) or not isinstance(decl.get(req), str):
            return _teach(req, decl.get(req), f"a non-empty {req} string")
    run = decl.get("run")
    if not isinstance(run, dict) or not run:
        return _teach("run", run, f"a run object naming what to run: one of {RUN_KINDS}",
                      fix={"run": {"cascade": "<a saved cascade name>"}})
    rk = next((k for k in run if k in RUN_KINDS), None)
    if rk is None:
        bad = next(iter(run), None)
        return _teach("run", bad, f"a run kind — one of {RUN_KINDS}", closest=_closest(bad, RUN_KINDS))
    if rk == "cascade":
        cname = run["cascade"]
        if cname not in cascades:
            return _teach("run.cascade", cname, "a registered saved-cascade name",
                          closest=_closest(cname, cascades),
                          why="refs resolve at define-time so a job never fires into a dangling name",
                          fix={"run": {"cascade": (_closest(cname, cascades) or ['<save it first>'])[0]}})
    else:  # cascade_inline — validated at fire time by the cascade door (it may reference roles live)
        if not isinstance(run["cascade_inline"], dict) or not run["cascade_inline"].get("steps"):
            return _teach("run.cascade_inline", run.get("cascade_inline"),
                          "an inline cascade decl object with a non-empty steps[] list")
    params = decl.get("params") or {}
    if not isinstance(params, dict):
        return _teach("params", params, "a params object {name: {desc, default?}} (the flows shape)")
    for pname, pspec in params.items():
        if not isinstance(pspec, dict) or "desc" not in pspec:
            return _teach(f"params.{pname}", pspec, "a param spec {desc: str, default?: any} (flows shape)")
    trig = decl.get("trigger") or {"kind": "manual"}
    if not isinstance(trig, dict) or trig.get("kind") not in TRIGGER_KINDS:
        return _teach("trigger.kind", trig.get("kind") if isinstance(trig, dict) else trig,
                      f"a trigger kind — one of {TRIGGER_KINDS}",
                      closest=_closest(isinstance(trig, dict) and trig.get("kind") or "", TRIGGER_KINDS))
    if trig.get("kind") != "manual":
        return _teach("trigger.kind", trig.get("kind"),
                      "manual (the skeleton fires manual only; schedule/change/condition triggers land "
                      "with the TriggerDriver + the ActivationCaller tick — see plan-a-jobs/DESIGN.md)",
                      why="registering a standing trigger arms autonomous work and routes through the "
                          "operator (proposed→ask→armed); not yet built")
    job = {
        "name": jid,                                   # ActionRegistry keys on `name`; id IS the key
        "id": jid, "label": decl["label"], "description": decl["description"],
        "run": {rk: run[rk]},
        "params": params,
        "allocations": decl.get("allocations") or {},
        "outputs": decl.get("outputs") or {"address": f"run://job/{jid}"},
        "trigger": {"kind": "manual"},
        "proposes_only": bool(decl.get("proposes_only", True)),
        "enabled": bool(decl.get("enabled", True)),
        "created_by": decl.get("created_by", ""),
        "created_at": decl.get("created_at", ""),      # stamped by the caller (no clock in a pure fn)
        "version": decl.get("version", 1),
    }
    return {"ok": True, "job": job}


def save_job(suite, decl: dict) -> dict:
    """Author/update a job row (validated through build_job, persisted, survives reload)."""
    built = build_job(decl, cascades={c["name"] for c in suite.cascade_registry.all()})
    if not built.get("ok"):
        return built
    job = built["job"]
    if not job.get("created_at"):
        job["created_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    _registry(suite).save(job)
    suite._emit("job.save", f"saved job {job['id']!r} (run={list(job['run'])[0]})", job=job["id"])
    return {"ok": True, "job": job}


def list_jobs(suite) -> list:
    return _registry(suite).all()


def get_job(suite, job_id: str) -> dict | None:
    return _registry(suite).get(job_id)


def _resolve_params(job: dict, params: dict | None) -> dict:
    """Merge caller params over declared defaults (the flows Flow.run discipline): unknown param → refuse;
    a required param (default is None AND absent) → refuse; declared defaults fill the rest."""
    declared = job.get("params") or {}
    params = params or {}
    unknown = [p for p in params if p not in declared]
    if unknown:
        raise ValueError(f"jobs.run: unknown param {unknown[0]!r} for job {job['id']!r} — "
                         f"declared params are {list(declared)} (author them into the job row first).")
    out = {}
    for pname, pspec in declared.items():
        if pname in params:
            out[pname] = params[pname]
        elif pspec.get("default") is not None or "default" in pspec:
            out[pname] = pspec.get("default")
        else:
            raise ValueError(f"jobs.run: job {job['id']!r} requires param {pname!r} "
                             f"({pspec.get('desc','')}) — no default; pass it in `params`.")
    return out


def run_job(suite, *, job_id: str | None = None, job: dict | None = None, params: dict | None = None) -> dict:
    """FIRE a job: resolve it (saved by id OR an inline job dict), merge/validate params, run its cascade
    body through the EXISTING executor (Suite.run_cascade), and record ONE job.run event. Returns the run
    record {fire_id, job, state, params, result, outputs}. Fail-loud on every miss (never a silent no-op)."""
    if job is None:
        if not job_id:
            raise ValueError("run_job: pass job_id (a saved job) or job (an inline job dict).")
        job = get_job(suite, job_id)
        if job is None:
            known = [j["id"] for j in list_jobs(suite)]
            raise ValueError(f"run_job: no saved job {job_id!r} — saved jobs are {known} "
                             f"(define one via jobs(op='define') first; registry-is-truth).")
    else:                                              # inline: validate through the same door before firing
        built = build_job(job, cascades={c["name"] for c in suite.cascade_registry.all()})
        if not built.get("ok"):
            return built
        job = built["job"]

    resolved = _resolve_params(job, params)
    fire_id = job["id"] + "-" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + f"-{int(time.monotonic()*1000)%10000:04d}"
    run = job["run"]
    # the step-0 input for the cascade = the resolved params (the cascade's own contract consumes them)
    inputs = resolved if resolved else None
    if "cascade" in run:
        cname = run["cascade"]
    else:
        # inline: save an ephemeral job-owned cascade, then run it through the ONE executor (no forked runner).
        cname = f"_job:{job['id']}"
        decl = dict(run["cascade_inline"]); decl["name"] = cname
        saved = suite.save_cascade(decl)
        if not saved.get("ok"):
            return {"ok": False, "refused": True, "at": "run.cascade_inline", "error": saved.get("error"),
                    "why": "the inline cascade decl failed the cascade validation door (same door as save_cascade)"}
    suite._emit("job.run", f"fire job {job['id']!r} → cascade {cname!r} (fire {fire_id})",
                job=job["id"], fire_id=fire_id, params=resolved)
    try:
        result = suite.run_cascade(cname, inputs=inputs,
                                   max_tokens=int((job.get("allocations") or {}).get("max_tokens", 256)))
        state, err = "succeeded", None
    except Exception as e:                             # fail-loud: the run record carries the breadcrumb
        result, state, err = None, "failed", f"{type(e).__name__}: {e}"
    rec = {"ok": state == "succeeded", "fire_id": fire_id, "job": job["id"], "state": state,
           "params": resolved, "cascade": cname, "result": result, "error": err,
           "outputs": {"address": f"run://job/{job['id']}/{fire_id}"}}
    suite._emit("job.done", f"job {job['id']!r} {state} (fire {fire_id})",
                job=job["id"], fire_id=fire_id, state=state, error=err)
    return rec
