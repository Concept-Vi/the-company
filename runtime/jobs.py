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
RUN_KINDS = ("cascade", "cascade_inline", "handler")   # flow/graph/agent step-kinds land later
TRIGGER_KINDS = ("manual", "schedule", "change", "event", "condition")  # skeleton fires manual only

# THE HANDLER REGISTRY — the ONE place deterministic-python run-bodies live ("rows for everything; code
# only in the handler registry" — plan-a-jobs R2's law). A job row NAMES a handler; it can never carry
# code. Each entry: name → (import path, callable, one-line what-it-does). Closed set, fail-loud on an
# unregistered name at define-time. These are the maintenance primitives the heartbeat composes.
HANDLERS = {
    "durability_sync": ("ops.sync_durability", "sync_durability",
                        "refresh ledger.interpretation + ledger.assertion from the newest enrichment (L9)"),
    "file_meta_walk":  ("ops.build_file_meta", "load_file_meta",
                        "git-walk a project's history into ledger.file_meta (the run-independent time axis)"),
}


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
    elif rk == "handler":
        hname = run["handler"]
        if hname not in HANDLERS:
            return _teach("run.handler", hname, "a registered handler name (jobs never carry code — "
                          f"the closed registry is {sorted(HANDLERS)})",
                          closest=_closest(hname, HANDLERS),
                          why="rows for everything; code only in the handler registry",
                          fix={"run": {"handler": (_closest(hname, HANDLERS) or sorted(HANDLERS))[0]}})
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
    trig_state = "n/a"
    if trig.get("kind") != "manual":
        # STANDING TRIGGERS: accepted as data, but NEVER born armed — the floor (proposed→armed; arming is
        # the operator's, and the autonomous loop is ALSO env-gated off: a double gate). Validate the config:
        cfg = trig.get("config") or {}
        if trig["kind"] == "schedule":
            if not isinstance(cfg.get("every_s"), int) or cfg["every_s"] < 30:
                return _teach("trigger.config.every_s", cfg.get("every_s"),
                              "an int ≥ 30 (seconds between fires)", fix={"trigger": {"kind": "schedule", "config": {"every_s": 3600}}})
        elif trig["kind"] == "change":
            srcs = cfg.get("sources")
            if not isinstance(srcs, list) or not srcs or not all(isinstance(s, str) and s.startswith("git:") for s in srcs):
                return _teach("trigger.config.sources", srcs,
                              'a non-empty list of "git:<abs-repo-path>" sources (v1: git-sig change detection; '
                              '"ledger:<table>" is the reserved post-outbox kind)',
                              fix={"trigger": {"kind": "change", "config": {"sources": ["git:/home/tim/company"],
                                                                            "quiet_window_s": 120}}})
        else:
            return _teach("trigger.kind", trig["kind"],
                          "manual | schedule | change (event/condition kinds land with the event-cursor "
                          "+ rules-AST work — see plan-a-jobs/DESIGN.md)")
        trig_state = "proposed"                        # ALWAYS born proposed — arming is arm_job's transition
                                                       # only (trigger_state is not even an authorable field)
    job = {
        "name": jid,                                   # ActionRegistry keys on `name`; id IS the key
        "id": jid, "label": decl["label"], "description": decl["description"],
        "run": {rk: run[rk]},
        "params": params,
        "allocations": decl.get("allocations") or {},
        "outputs": decl.get("outputs") or {"address": f"run://job/{jid}"},
        "trigger": {**trig} if trig.get("kind") != "manual" else {"kind": "manual"},
        "trigger_state": trig_state,                   # n/a (manual) | proposed | armed — armed ONLY via arm_job
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

    # L10↔L5 BIND: every fire IS an intent — claimed with a lease, terminated on completion, composed by
    # the clock (runtime/circuit). A fire that dies mid-run composes to LAPSED with no reaper (the same
    # zombie-proofing the historical 73 got); a lapsed fire is re-claimable. The marks are the DURABLE
    # execution record (container.mark) — the trigger walk's in_flight state file is just its fast path.
    from runtime import circuit as _circ
    _intent = f"intent://job/{job['id']}/{fire_id}"
    _lease_s = int((job.get("allocations") or {}).get("time_budget_s", 600))
    _circ.claim_intent(suite.store, _intent, by=f"job://{job['id']}", session=fire_id,
                       lease_seconds=_lease_s)

    if "handler" in run:                               # deterministic-python body from the closed registry
        mod_path, fn_name, _doc = HANDLERS[run["handler"]]
        suite._emit("job.run", f"fire job {job['id']!r} → handler {run['handler']!r} (fire {fire_id})",
                    job=job["id"], fire_id=fire_id, params=resolved)
        try:
            import importlib
            fn = getattr(importlib.import_module(mod_path), fn_name)
            result = fn(**resolved) if resolved else fn()
            state, err = "succeeded", None
        except Exception as e:                         # fail-loud: the run record carries the breadcrumb
            result, state, err = None, "failed", f"{type(e).__name__}: {e}"
        _circ.terminate(suite.store, _intent, outcome=state,
                        result=f"run://job/{job['id']}/{fire_id}", error=err)
        rec = {"ok": state == "succeeded", "fire_id": fire_id, "job": job["id"], "state": state,
               "params": resolved, "handler": run["handler"], "result": result, "error": err,
               "intent": _intent,
               "outputs": {"address": f"run://job/{job['id']}/{fire_id}"}}
        suite._emit("job.done", f"job {job['id']!r} {state} (fire {fire_id})",
                    job=job["id"], fire_id=fire_id, state=state, error=err)
        return rec

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
            _circ.terminate(suite.store, _intent, outcome="cancelled",
                            error="inline cascade decl refused at the door")
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
    _circ.terminate(suite.store, _intent, outcome=state,
                    result=f"run://job/{job['id']}/{fire_id}", error=err)
    rec = {"ok": state == "succeeded", "fire_id": fire_id, "job": job["id"], "state": state,
           "params": resolved, "cascade": cname, "result": result, "error": err,
           "intent": _intent,
           "outputs": {"address": f"run://job/{job['id']}/{fire_id}"}}
    suite._emit("job.done", f"job {job['id']!r} {state} (fire {fire_id})",
                job=job["id"], fire_id=fire_id, state=state, error=err)
    return rec


# ═══════════════════════════════════════════════════════════════════════════════════════════════════
# THE TRIGGER LAYER (L10 stage 2) — standing triggers as data on the job row, fired by ONE tick driver.
# Floor: a non-manual trigger is born state='proposed'; ONLY arm_job (the operator door) arms it — and the
# autonomous loop that would tick this continuously is ITSELF env-gated off (COMPANY_ACTIVATION_LOOP), so
# nothing self-fires until Tim arms both. Change detection v1 = git-sig (HEAD + porcelain hash: sees every
# writer); quiet-window debounce + watermark semantics per plan-a-jobs/DESIGN.md (the graphile job_key
# arithmetic compressed into per-trigger state, safe because exactly ONE caller ticks).
# ═══════════════════════════════════════════════════════════════════════════════════════════════════

def arm_job(suite, job_id: str, *, by: str = "operator") -> dict:
    """ARM a proposed standing trigger — THE OPERATOR DOOR (call this only on Tim's word; agents propose,
    the operator arms). Records who armed + when; the tick only ever fires state='armed' triggers."""
    reg = _registry(suite)
    job = reg.get(job_id)
    if job is None:
        raise ValueError(f"arm_job: no job {job_id!r} — jobs: {[j['id'] for j in reg.all()]}")
    if (job.get("trigger") or {}).get("kind") in (None, "manual"):
        raise ValueError(f"arm_job: job {job_id!r} has a manual trigger — nothing to arm (fire it directly).")
    job["trigger_state"] = "armed"
    job["armed_by"], job["armed_at"] = by, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    reg.save(job)
    suite._emit("job.armed", f"standing trigger ARMED on job {job_id!r} (by {by})", job=job_id, by=by)
    return {"ok": True, "job": job_id, "trigger_state": "armed", "by": by}


def pause_job(suite, job_id: str, *, by: str = "") -> dict:
    """Disarm a standing trigger (row stays; state → proposed)."""
    reg = _registry(suite)
    job = reg.get(job_id)
    if job is None:
        raise ValueError(f"pause_job: no job {job_id!r}")
    job["trigger_state"] = "proposed"
    reg.save(job)
    suite._emit("job.paused", f"standing trigger PAUSED on job {job_id!r}", job=job_id, by=by)
    return {"ok": True, "job": job_id, "trigger_state": "proposed"}


def _git_sig(repo: str) -> str:
    """The change signature for a git: source — HEAD sha + a hash of the dirty state. One subprocess,
    sees EVERY writer (agent sessions, manual edits, other tools) — the property job-completion events
    can't have. An unreadable repo raises (fail loud, never a silent 'no change')."""
    import hashlib
    import subprocess as sp
    head = sp.run(["git", "-C", repo, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=30)
    dirty = sp.run(["git", "-C", repo, "status", "--porcelain"], capture_output=True, text=True, timeout=60)
    if head.returncode != 0 or dirty.returncode != 0:
        raise RuntimeError(f"_git_sig: {repo} unreadable as a git repo — "
                           f"{(head.stderr or dirty.stderr).strip()[:120]}")
    return head.stdout.strip() + ":" + hashlib.blake2b(dirty.stdout.encode(), digest_size=8).hexdigest()


def _trigger_state_path(suite) -> str:
    return str(suite.store.root / "trigger_state.json")


def _load_trigger_state(suite) -> dict:
    p = _trigger_state_path(suite)
    if not os.path.exists(p):
        return {}
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception as e:                             # corrupt state NEVER silently resets — raise with the path
        raise RuntimeError(f"trigger_state.json corrupt at {p} ({type(e).__name__}: {e}) — "
                           "inspect/repair it; a silent reset would re-fire or skip triggers invisibly.")


def _save_trigger_state(suite, state: dict) -> None:
    p = _trigger_state_path(suite)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=1)
    os.replace(tmp, p)


def trigger_tick(suite, *, now: float | None = None) -> dict:
    """Walk every ARMED standing trigger once; fire what's due. THE one scheduler pass (hosted as the 4th
    driver in ActivationCaller.activation_tick — no second scheduler). Per armed job:
      schedule: due ⇔ now − last_fired_at ≥ every_s.
      change:   sig ≠ state.sig → re-arm the quiet window (changed_at=now; job_key replace-mode semantics);
                due ⇔ sig ≠ last_fired_sig ∧ quiet elapsed ∧ not in-flight. Fires run_job with a
                `watermark` param when the job declares one (the run discovers its own work — events are
                only wake-ups, so coalescing is free and a missed tick self-heals).
      Single-flight: in_flight_fire_id guards a running fire; a stall past 1.5× time_budget_s surfaces
      LOUD (job.stalled event) + releases (recorded, never a silent wedge).
    Returns {walked, fired[], skipped[], errors[]} — every non-fire is legible, never silent."""
    now = now if now is not None else time.time()
    state = _load_trigger_state(suite)
    out = {"walked": 0, "fired": [], "skipped": [], "errors": []}
    for job in list_jobs(suite):
        trig = job.get("trigger") or {}
        if trig.get("kind") in (None, "manual"):
            continue
        out["walked"] += 1
        jid = job["id"]
        if job.get("trigger_state") != "armed":
            out["skipped"].append(f"{jid}: proposed (not armed — the operator door)")
            continue
        st = state.setdefault(jid, {})
        cfg = trig.get("config") or {}
        budget_s = int((job.get("allocations") or {}).get("time_budget_s", 600))
        # single-flight + loud stall
        if st.get("in_flight_fire_id"):
            if now - st.get("in_flight_since", now) > budget_s * 1.5:
                suite._emit("job.stalled", f"job {jid!r} fire {st['in_flight_fire_id']} exceeded "
                            f"{budget_s * 1.5:.0f}s — releasing single-flight (recorded, surfaced)",
                            job=jid, fire_id=st["in_flight_fire_id"])
                st["in_flight_fire_id"] = None
            else:
                out["skipped"].append(f"{jid}: in-flight ({st['in_flight_fire_id']})")
                continue
        try:
            due, fire_params = False, {}
            if trig["kind"] == "schedule":
                due = now - st.get("last_fired_at", 0) >= cfg["every_s"]
                if not due:
                    out["skipped"].append(f"{jid}: schedule not due "
                                          f"({int(cfg['every_s'] - (now - st.get('last_fired_at', 0)))}s left)")
            elif trig["kind"] == "change":
                sig = "|".join(_git_sig(s[len("git:"):]) for s in cfg["sources"])
                if sig != st.get("sig"):
                    st["sig"], st["changed_at"] = sig, now       # job_key replace-mode: re-arm the window
                quiet = cfg.get("quiet_window_s", 120)
                if sig == st.get("last_fired_sig"):
                    out["skipped"].append(f"{jid}: no change since last fire")
                elif now - st.get("changed_at", now) < quiet:
                    out["skipped"].append(f"{jid}: in quiet window "
                                          f"({int(quiet - (now - st.get('changed_at', now)))}s left)")
                else:
                    due = True
                    if "watermark" in (job.get("params") or {}):
                        fire_params["watermark"] = st.get("watermark")
            if not due:
                continue
            fire_start = now
            st["in_flight_fire_id"], st["in_flight_since"] = "pending", now
            _save_trigger_state(suite, state)                    # persist BEFORE the fire (crash-legible)
            rec = run_job(suite, job_id=jid, params=fire_params or None)
            st["in_flight_fire_id"] = None
            st["last_fired_at"] = fire_start
            if trig["kind"] == "change":
                st["last_fired_sig"] = st.get("sig")
                st["watermark"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(fire_start))
            out["fired"].append({"job": jid, "fire_id": rec.get("fire_id"), "state": rec.get("state")})
        except Exception as e:                                   # a trigger error is recorded + surfaced, never fatal to the walk
            st["in_flight_fire_id"] = None
            out["errors"].append(f"{jid}: {type(e).__name__}: {e}")
            suite._emit("job.trigger_error", f"trigger walk error on {jid!r}: {e}", job=jid)
    _save_trigger_state(suite, state)
    return out
