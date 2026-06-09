"""app — the `company` command dispatcher.

ONE console for the whole Company system: see/operate services, manage the local
models, and read+budget+schedule the GPU (the resource manager). Reads services.json;
drives systemd. Nothing auto-starts at boot — everything is on-demand from here.
stdlib-only. See README.md (use) and UPDATING.md (extend). Constitution: ../AGENTS.md.

  company                  see everything + state + VRAM budget (= status)
  company status
  company up [TARGET] [--wait] [--evict] [--force]
  company down TARGET
  company restart TARGET [--wait] [--evict] [--force]
  company logs SERVICE [-f]

  company gpu              measured GPU VRAM + what's holding it
  company health           ping every service's port
  company suites           the ALL-GREEN GATE: run every acceptance suite standalone,
                           require green (live-dep skips classified) — pre-merge/pre-deploy
  company models           what's on disk (HF cache + Ollama)
  company swap SERVICE MODEL_ID   point a model service at another model + restart
  company ensure MODEL|SERVICE [--evict] [--no-wait]
                           the GATED launch/select actuator: make a model resident on demand
                           (already-up → no-op; fits → load; over-budget + --evict → evict
                           largest-first then load; can't-fit-after-evict → fail loud). The ONE
                           mechanism the engine + CLI share — reuses the up/--evict resource-manager.
  company config SERVICE [KEY VAL] show / edit a model's serve config (gpu_util, model, ctx…)
  company combos           list runnable combinations (`company up @<name>` to start one)
  company bench KIND [args]       chat|embed|suite|long-ctx
  company telemetry        learned model load times + measured VRAM (vs estimates)
  company help

TARGET = a service key, a group (core|brain|voice|models|reach), `@combo`, or `all`.
RESOURCE MANAGER (the models/VRAM type-view): `company up` REFUSES a start that would
exceed GPU capacity and shows what's holding the card.
  --evict   make room first: stop running GPU services (models→brain→voice, largest
            first) until the start fits, then start. Default is refuse.
  --force   start anyway over budget (loudly; expect OOM/offload).
  --wait    block until the model is serving, then record its REAL load time + measured
            VRAM to telemetry (so estimates become measured — see `company telemetry`)."""
import sys, time
import registry, systemd, gpu, models, bench, render, telemetry
from registry import vram_of


def _gpu_keys(reg, keys):
    """The to-start keys that occupy the GPU and expose a port (telemetry-trackable)."""
    return [k for k in keys if vram_of(reg["services"][k]) and reg["services"][k].get("port")]


def _wait_and_record(reg, keys, free_before, timeout=420):
    """After starting, block until each GPU service is serving. Record telemetry ONLY
    for a single GPU load — concurrent loads (a combo) can't be VRAM-attributed per
    service from one measurement, so we confirm serving but don't record garbage."""
    gks = _gpu_keys(reg, keys)
    solo = len(gks) == 1
    for k in gks:
        svc = reg["services"][k]
        port = svc["port"]
        t0 = time.time()
        print(f"  …waiting for {k} (:{port}) to serve (up to {timeout}s)…")
        while time.time() - t0 < timeout:
            if systemd.port_open(port) is True:
                break
            if systemd.is_active(svc) == "failed":
                print(f"  ✗ {k} unit failed while loading — see `company logs {k}`")
                break
            time.sleep(3)
        served = systemd.port_open(port) is True
        elapsed = time.time() - t0
        if not served:
            print(f"  ✗ {k} did not come up within {timeout}s")
            continue
        if solo:
            after = gpu.read_gpu()
            resident = max(0, free_before - after["free"]) if after else 0
            telemetry.record(k, elapsed, resident, vram_of(svc))
            print(f"  ✓ {k} serving in {elapsed:.0f}s · measured ~{resident/1000:.1f} GB "
                  f"(est ~{vram_of(svc)/1000:.1f} GB) · recorded")
        else:
            print(f"  ✓ {k} serving in {elapsed:.0f}s (concurrent start — VRAM not "
                  f"per-service-attributable, telemetry skipped)")


def _act(reg, action, keys, force=False, evict=False, wait=False):
    svcs = reg["services"]
    if action in ("up", "restart"):
        print(gpu.format_state(reg))
        ok, need, free, measured = gpu.check_fit(reg, keys)
        if need:
            src = "measured free" if measured else "estimated free (nvidia-smi unreadable)"
            print(f"  request needs ~{need/1000:.1f} GB; {free/1000:.1f} GB {src}.")
        if not ok:
            if evict:
                plan, projected = gpu.plan_eviction(reg, keys, need, free)
                if not plan or projected < need:
                    print(f"  ✖ REFUSED — even evicting {plan or 'nothing evictable'} frees only "
                          f"~{projected/1000:.1f} GB, need ~{need/1000:.1f} GB.")
                    sys.exit(2)
                print(f"  --evict: making room by stopping {', '.join(plan)} "
                      f"(→ ~{projected/1000:.1f} GB free)")
                for k in plan:
                    okk, msg = systemd.control(svcs[k], "stop")
                    print(f"    {'✓' if okk else '✗'} stop {k}" + ("" if okk else f"  [{msg}]"))
                time.sleep(2)  # let VRAM release
            elif force:
                print(f"  ⚠ --force: starting anyway over budget by ~{(need-free)/1000:.1f} GB "
                      f"(expect OOM or CPU-offload).")
            else:
                print(f"  ✖ REFUSED — would exceed GPU capacity by ~{(need-free)/1000:.1f} GB.")
                print(f"    Free space first (`company down <service>`), re-run with --evict to "
                      f"auto-make-room, or --force to override.")
                sys.exit(2)
    free_before = (gpu.read_gpu() or {}).get("free", 0) if wait else 0
    word = {"up": "start", "down": "stop", "restart": "restart"}[action]
    for k in keys:
        if action == "down":
            ok, msg = gpu.teardown(svcs[k])        # orphan-safe (cgroup for units; pgroup for manual)
        else:
            ok, msg = systemd.control(svcs[k], word)
        print(f"  {'✓' if ok else '✗'} {word} {k}" + ("" if ok else f"  [{msg}]"))
    if wait and action in ("up", "restart"):
        _wait_and_record(reg, keys, free_before)


def main():
    reg = registry.load()
    args = sys.argv[1:]
    cmd = args[0] if args else "status"

    if cmd in ("help", "-h", "--help"):
        print(__doc__); return
    if cmd == "status":
        print(render.status(reg)); return
    if cmd == "gpu":
        print(gpu.format_state(reg)); return
    if cmd == "health":
        print(render.health(reg)); return
    if cmd == "suites":
        # THE ALL-GREEN GATE (on-demand, option C). Runs the standing suite-health check — every
        # acceptance suite STANDALONE, green-or-documented-live-dep-skip-or-red (Suite.suite_health). The
        # repo's single source of truth for "is the whole suite green"; this console is the one place to
        # run it by hand (pre-merge / pre-deploy / whenever). SLOW — it spawns every suite (a few minutes).
        # Thin wiring: shells the gate suite (no logic duplicated) under a TEMP store so it never touches
        # the live data, and propagates its exit code (0 = all green, non-zero = a real red, named).
        import os as _os, subprocess as _sp, tempfile as _tf
        repo = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
        venv_py = _os.path.join(repo, ".venv", "bin", "python")
        py = venv_py if _os.path.exists(venv_py) else sys.executable
        gate = _os.path.join(repo, "tests", "suite_health_acceptance.py")
        if not _os.path.exists(gate):
            sys.exit(f"  ✗ the all-green gate is missing: {gate}")
        env = dict(_os.environ, COMPANY_STORE=_tf.mkdtemp(prefix="company-suites-"))
        print("running the all-green gate — every acceptance suite, standalone. This takes a few minutes…\n")
        sys.exit(_sp.run([py, gate], cwd=repo, env=env).returncode)
    if cmd == "coherence":
        # THE COHERENCE READ (on-demand). Re-derives the coherence model fresh (own/reflect — no maintained
        # graph): runs the structural detectors over the repo, folds the burn-down, and prints the real
        # backlog + the positive-only candidates. Fast (no subprocess swarm — pure AST/registry reads).
        # Thin: the logic lives in runtime/coherence_detect (scan/format_scan); this is its operator face.
        import os as _os
        repo = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
        sys.path.insert(0, repo)
        from runtime import coherence_detect as _cd
        print(_cd.format_scan(_cd.scan(repo)))
        return
    if cmd == "models":
        print(models.inventory()); return
    if cmd == "telemetry":
        print(telemetry.rollups()); return
    if cmd == "combos":
        cs = registry.combos(reg)
        if not cs:
            print("  no combos defined."); return
        for name, c in cs.items():
            note = f"   — {c['note']}" if c.get("note") else ""
            print(f"  @{name:<14} {', '.join(c['services'])}{note}")
        return
    if cmd == "config":
        if len(args) < 2:
            sys.exit("usage: company config SERVICE [KEY VALUE]")
        key = args[1]
        if key not in reg["services"]:
            sys.exit(f"unknown service {key!r}")
        if len(args) == 2:
            import json as _json
            c = reg["services"][key].get("config")
            print(_json.dumps(c, indent=2) if c else f"  {key} has no config block (legacy/script service).")
            return
        if len(args) >= 4:
            try:
                newv = registry.set_config(reg, key, args[2], args[3])
            except ValueError as e:
                sys.exit(f"  {e}")
            print(f"  ✓ {key}.config.{args[2]} = {newv!r} (saved). Apply with: company restart {key}")
            return
        sys.exit("usage: company config SERVICE [KEY VALUE]")
    if cmd == "swap":
        rest = [a for a in args[1:] if not a.startswith("-")]
        if len(rest) < 2:
            sys.exit("usage: company swap SERVICE MODEL_ID")
        ok, msg = models.swap(reg, rest[0], rest[1])
        print(("  ✓ " if ok else "  ✗ ") + msg)
        sys.exit(0 if ok else 1)
    if cmd == "ensure":
        # #50 — the GATED launch/select actuator from the CLI (the engine calls the same
        # capabilities.ensure_resident; this is its operator face). Reuses the resource-manager
        # (gpu.check_fit/plan_eviction) — NOT a second start path. --evict = authorize largest-first
        # room-making; default refuses an over-budget load (fail-loud), matching `company up`'s policy.
        import capabilities as _cap
        flags = {a for a in args[1:] if a.startswith("--")}
        rest = [a for a in args[1:] if not a.startswith("--")]
        if not rest:
            sys.exit("usage: company ensure MODEL|SERVICE [--evict] [--no-wait]")
        print(gpu.format_state(reg))   # always show what's holding the card (the up/refuse ritual)
        try:
            res = _cap.ensure_resident(rest[0], evict="--evict" in flags, reg=reg,
                                       wait="--no-wait" not in flags)
        except _cap.EnsureResidentError as e:
            print(f"  ✖ {e}")
            sys.exit(2)
        if res.get("swap_needed"):
            # G14: the swap-approval ASK — NOT a success (no ✓, exit 3 so scripts can't mistake it).
            print(f"  ⇄ {res['message']}")
            print(f"    would evict (largest-first): {', '.join(res.get('would_evict', []))} — "
                  f"approve: re-run with --evict")
            sys.exit(3)
        print(f"  ✓ {res['message']}")
        if res.get("evicted"):
            print(f"    (evicted, largest-first: {', '.join(res['evicted'])})")
        sys.exit(0)
    if cmd == "bench":
        ok, msg = bench.run([a for a in args[1:] if not a.startswith("-")])
        if msg:
            print(msg)
        sys.exit(0 if ok else 1)
    if cmd in ("up", "down", "restart"):
        flags = {a for a in args[1:] if a.startswith("--")}
        rest = [a for a in args[1:] if not a.startswith("--")]
        target = rest[0] if rest else None
        if cmd != "up" and target is None:
            sys.exit(f"`company {cmd}` needs a target (a service, a group, or `all`).")
        try:
            keys = registry.resolve(reg, target)
        except KeyError:
            sys.exit(f"unknown target {target!r}. Try a service, a group "
                     f"({'|'.join(reg['groups'])}), or `all`.")
        _act(reg, cmd, keys, force="--force" in flags, evict="--evict" in flags, wait="--wait" in flags)
        return
    if cmd == "logs":
        if len(args) < 2:
            sys.exit("usage: company logs SERVICE [-f]")
        if args[1] not in reg["services"]:
            sys.exit(f"unknown service {args[1]!r}")
        systemd.journal(reg["services"][args[1]], "-f" in args)
        return
    sys.exit(f"unknown command {cmd!r}. Try `company help`.")


if __name__ == "__main__":
    main()
