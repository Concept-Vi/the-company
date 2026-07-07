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
  company query "Q" [SPACE] [N]  ask the COORDINATE SPACE from the terminal (the same one
                           function the MCP tool + /api/query call; lens-routed embed)
  company jobs             THE HEARTBEAT, visible: every registered job + trigger posture
                           (proposed/armed) + live change/quiet-window state + recent fires
                           composed through the circuit clock-fold (a dead fire shows LAPSED)
  company session [SUB]    the supervised Claude Code fleet (Session Fabric): list ·
                           new [--cwd D] [--resume ID] [--fork] [--name L] [--prompt "…"] ·
                           send <id> <msg…> · stop <id>. Talks to the session-supervisor
                           service (127.0.0.1:8771) — `company up session-supervisor` first.
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


def _confirm_started(svc, k, word, window=8):
    """LOUD-FAIL: a returncode-0 start/restart of a Type=simple unit only means systemd FORKED the
    process — NOT that it serves (the stale-bridge no-op class: `✓ restart` printed for a service that
    launched then died). So never claim success on the bare returncode. Briefly confirm liveness without
    forcing a full --wait: port up → serving; unit failed → crashed (loud ✗); neither within `window`s →
    say HONESTLY that liveness is unconfirmed (◐, not a silent ✓). A genuinely slow model → use --wait."""
    port = svc.get("port")
    if svc["manage"]["type"] == "manual" or not port:
        return f"✓ {word} {k}"                               # no managed port to probe
    t0 = time.time()
    while time.time() - t0 < window:
        if systemd.port_open(port) is True:
            return f"✓ {word} {k} — serving on :{port}"
        if systemd.is_active(svc) == "failed":
            return f"✗ {word} {k} FAILED on startup — see `company logs {k}`"
        time.sleep(1)
    return (f"◐ {word} {k} launched — liveness UNCONFIRMED in {window}s (Type=simple returns on fork; "
            f"slow model → use --wait, else check `company status`)")


def _repoint_loadout_brain(reg, keys, brain_key):
    """After `company up @loadout` brings a brain-carrying loadout up, ask the bridge to repoint the RHM at
    that loadout's brain (the bridge owns the live Suite/RHM-config + the ONE verify+revert repoint logic —
    no parallel repoint here). Bridge DOWN is handled LOUD, never silent: the RHM pointer is persisted + read
    at the next bridge start, so a missed repoint would break the brain THEN — so we print the exact manual
    fix instead of pretending it's done."""
    import json as _json, urllib.request as _ur, urllib.error as _ue
    cfg = reg["services"][brain_key].get("config") or {}
    model, port = cfg.get("model"), cfg.get("port")
    endpoint = f"http://127.0.0.1:{port}/v1" if port else None
    body = _json.dumps({"services": keys}).encode()
    req = _ur.Request("http://127.0.0.1:8770/api/loadout/repoint", data=body,
                      headers={"Content-Type": "application/json"})
    try:
        out = _json.loads(_ur.urlopen(req, timeout=30).read())
        if out.get("repointed"):
            print(f"  ✓ RHM brain → {out.get('model')} @ {out.get('base_url')} (loadout switch complete)")
        else:
            print(f"  · RHM pointer unchanged ({out.get('reason', 'no brain in loadout')})")
    except _ue.HTTPError as e:
        # the bridge answered but the repoint FAILED (e.g. the new brain didn't pass the verify probe) — loud.
        detail = e.read().decode(errors="replace")[:300]
        print(f"  ✖ RHM repoint FAILED ({e.code}): {detail}")
        print(f"    The brain may be mid-load; retry the `company up @loadout`, or set it manually once it serves:")
        print(f"    curl -s :8770/api/rhm-config -d '{{\"model\":\"{model}\",\"base_url\":\"{endpoint}\"}}'")
    except (_ue.URLError, OSError) as e:
        # bridge DOWN — do NOT pretend the switch is complete. The pointer is stale until repointed.
        print(f"  ⚠ bridge not reachable ({e}) — the RHM brain was NOT repointed.")
        print(f"    The RHM is still pointed at the PRIOR (now-evicted) brain; fix when the bridge is up:")
        print(f"    curl -s :8770/api/rhm-config -d '{{\"model\":\"{model}\",\"base_url\":\"{endpoint}\"}}'")


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
        # WS-R: the SYSTEM-RAM leg of the capacity invariant (the block above is the GPU/VRAM leg).
        # ram_fit reads LIVE /proc/meminfo MemAvailable, so ALL memory pressure on the box (Chrome,
        # background evals, anything) is counted — overcommit is impossible by code, not just impossible
        # among Company services (the real OOM cause was non-service pressure). RAM overflow is
        # kernel-fatal (the OOM-killer); --force does NOT override it (force is VRAM-only by design).
        ram = gpu.ram_fit(reg, keys)
        if not ram["present"]:
            print("  ⚠ system RAM unreadable (/proc/meminfo) — RAM leg skipped (VRAM-only, like nvidia-smi absent).")
        else:
            if ram["need"]:
                print(f"  request needs ~{ram['need']/1000:.1f} GB RAM; ~{ram['free']/1000:.1f} GB available "
                      f"now (live MemAvailable − headroom).")
            if not ram["ok"]:
                print(f"  ✖ REFUSED — would exceed system RAM by ~{(ram['need']-ram['free'])/1000:.1f} GB. "
                      f"RAM overflow is kernel-fatal; --force does NOT override it.")
                print(f"    Free memory first (close other RAM users / `company down <service>`), then retry.")
                sys.exit(2)
    word = {"up": "start", "down": "stop", "restart": "restart"}[action]
    # MEASURED-RESTART FIX (2026-06-28): on a restart the old instance is still resident here, so a
    # free_before snapshot would count it — and free_after (old freed, new loaded) ends up HIGHER,
    # making the load-delta read ~0. Tear the service down FIRST when we're going to measure, so
    # free_before reflects the card WITHOUT it. (`up` of a not-running service is already correct.)
    if wait and action == "restart":
        for k in keys:
            gpu.teardown(svcs[k])
        time.sleep(2)                              # let VRAM actually release before the snapshot
    free_before = (gpu.read_gpu() or {}).get("free", 0) if wait else 0
    for k in keys:
        if action == "down":
            ok, msg = gpu.teardown(svcs[k])        # orphan-safe (cgroup for units; pgroup for manual)
            print(f"  {'✓' if ok else '✗'} {word} {k}" + ("" if ok else f"  [{msg}]"))
            continue
        ok, msg = systemd.control(svcs[k], word)   # restart on an already-stopped unit just starts it
        if not ok:
            print(f"  ✗ {word} {k}  [{msg}]")      # systemctl itself refused (loud)
        elif wait and vram_of(svcs[k]) and svcs[k].get("port"):
            print(f"  ✓ {word} {k}")               # GPU service + --wait: _wait_and_record confirms liveness below
        else:                                      # no silent ✓ on a bare fork — probe liveness (covers the CPU bridge too)
            print(f"  {_confirm_started(svcs[k], k, word)}")
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
        # the terrain-ledger drift detector — declared INTO the same substrate (same finding model),
        # surfaced in the same read (orienteering/ path-existence gate + positive-only orbit-coverage).
        from runtime import orienteering_drift as _od
        print("\n" + _od.format_scan(_od.scan(repo)))
        return
    if cmd == "query":
        # THE COORDINATE QUERY's CLI face (one implementation — mcp_face.tools.coordinate.run_query, the
        # same entry the MCP tool + the bridge /api/query call). `company query "text" [SPACE] [LIMIT]`
        # for quick asks; SPACE routes the embed lens (code/symbol→nomic, else pplx).
        import subprocess, os as _os, json as _json
        if len(args) < 2:
            print('usage: company query "your question" [SPACE=desc] [LIMIT=8]\n'
                  '  spaces: desc·docs·code·symbol·history·exchange·extractions·repo·topics…\n'
                  '  (full multi-axis specs: the coordinate MCP tool or POST /api/query)')
            return 1
        _text, _space = args[1], (args[2] if len(args) > 2 else "desc")
        _lim = int(args[3]) if len(args) > 3 else 8
        _repo = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
        _code = ("import sys, json; sys.path.insert(0, '.'); "
                 "from mcp_face.tools.coordinate import run_query; "
                 f"r = run_query({{'semantic': {{'text': {_text!r}, 'space': {_space!r}}}, 'limit': {_lim}}}); "
                 "print(json.dumps(r))")
        r = subprocess.run([_os.path.join(_repo, ".venv", "bin", "python"), "-c", _code],
                           cwd=_repo, capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            print(r.stderr.strip()[:600]); return 1
        out = _json.loads(r.stdout)
        plan = out.get("meta", {}).get("plan", {})
        print(f"QUERY over {_space!r} — plan: {_json.dumps(plan)}")
        for x in out.get("results", []):
            sc = x.get("score"); sc = f"{float(sc):.3f}" if sc is not None else "  ·  "
            print(f"  {sc}  {x.get('address','')[:76]}")
            if x.get("what_it_does"):
                print(f"         {x['what_it_does'][:100]}")
        return 0

    if cmd == "jobs":
        # THE HEARTBEAT'S CLI FACE (one implementation — runtime/jobs.jobs_status_render; this verb is a
        # thin invoker so the status logic lives ONCE and the CLI stays stdlib-only).
        import subprocess, os as _os
        _repo = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
        _code = ("import sys, os; sys.path.insert(0, '.'); "
                 "from store.fs_store import FsStore; from runtime.registry import NodeRegistry; "
                 "from runtime.suite import Suite; from fabric import config as fcfg; "
                 "from runtime.jobs import jobs_status_render; "
                 "s = Suite(FsStore(fcfg.STORE_DIR), NodeRegistry().discover([os.path.join('.', 'nodes')])); "
                 "print(jobs_status_render(s))")
        r = subprocess.run([_os.path.join(_repo, ".venv", "bin", "python"), "-c", _code],
                           cwd=_repo, capture_output=True, text=True, timeout=120)
        print(r.stdout.strip() or r.stderr.strip()[:800])
        return 0 if r.returncode == 0 else 1

    if cmd == "models":
        print(models.inventory()); return
    if cmd == "telemetry":
        print(telemetry.rollups()); return
    if cmd == "session":
        # Session Fabric F1.1 — the supervised-fleet type-view (the constitution's "more TYPES"
        # growth shape). Thin: all logic in sessions.py; the supervisor service does the owning.
        import sessions as _sessions
        _sessions.run(args[1:])
        return
    if cmd == "board":
        # The Company NOTICEBOARD (inward-facing half) — file/list/pick-up/transition typed items
        # (request/issue/tip/guide/idea) about the Company itself. Thin: all logic in board.py;
        # runtime/cc_board.py owns it (pure file I/O — no service). A different session running
        # `company board file ...` + the lead `company board list/transition ...` IS the request loop.
        import board as _board
        _board.run(args[1:])
        return
    if cmd == "clone":
        # The clone-FLEET read surface (distributed-memory addressed rows) — a stable + PORTABLE read of a
        # clone:// record + its persisted reflection (mirrors `company board get`), so an external process
        # (recollection's fleet-recall ingest) reads without coupling to .data/clones/. cc_clone owns it.
        import clone as _clone
        _clone.run(args[1:])
        return
    if cmd == "combos":
        cs = registry.combos(reg)
        if not cs:
            print("  no combos defined."); return
        for name, c in cs.items():
            note = f"   — {c['note']}" if c.get("note") else ""
            cap = gpu.validate_combo_capacity(reg, c["services"])
            print(f"  @{name:<14} {', '.join(c['services'])}{'' if cap['ok'] else '   ⚠ EXCEEDS HARDWARE'}{note}")
            if not cap["ok"]:
                if not cap["vram_ok"]:
                    print(f"      ⚠ VRAM ~{cap['vram_need']/1000:.1f} GB > ~{cap['vram_cap']/1000:.1f} GB card")
                if not cap["ram_ok"]:
                    print(f"      ⚠ RAM ~{cap['ram_need']/1000:.1f} GB > ~{cap['ram_cap']/1000:.1f} GB usable")
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
        # forward args[1:] VERBATIM (kind + the bench script's own flags like --url/--model/
        # --concurrency/--requests/--max-tokens). The old `if not a.startswith("-")` filter stripped
        # EVERY flag, so a bench could only ever run the script defaults (:8000, the 4B-AWQ) — it
        # could not target another endpoint/model/concurrency. bench.run() takes args[0]=kind and
        # forwards the rest to the bench script (which does its own argparse).
        ok, msg = bench.run(args[1:])
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
        # WS-R: config-time hardware-fit guard for a loadout/combo. If the SET can never fit this hardware
        # (sum of estimates > card VRAM, or > usable system RAM) it's a capacity IMPOSSIBILITY — fail loud
        # here, before the live gate, so configuring a too-big loadout tells you immediately (Tim's bar).
        if cmd in ("up", "restart") and isinstance(target, str) and target.startswith("@"):
            cap = gpu.validate_combo_capacity(reg, keys)
            if not cap["ok"]:
                why = []
                if not cap["vram_ok"]:
                    why.append(f"VRAM ~{cap['vram_need']/1000:.1f} GB > ~{cap['vram_cap']/1000:.1f} GB card")
                if not cap["ram_ok"]:
                    why.append(f"RAM ~{cap['ram_need']/1000:.1f} GB > ~{cap['ram_cap']/1000:.1f} GB usable")
                sys.exit(f"  ✖ loadout {target} cannot fit this hardware: {'; '.join(why)}. "
                         f"Edit the combo in services.json — this is a capacity impossibility, not a "
                         f"live-state refusal (no --force/--evict can satisfy it).")
        _act(reg, cmd, keys, force="--force" in flags, evict="--evict" in flags, wait="--wait" in flags)
        # LOADOUT DOOR — after a @loadout comes up, the RHM brain must FOLLOW it (else it stays pointed at the
        # just-evicted brain = the broken-brain class). Only for an @loadout that carries a brain (a tool-only
        # loadout, or a bare-service start, repoints nothing). The repoint logic (verify+revert) lives in the
        # bridge's Suite — ONE logic, two callers — so the CLI POSTs to it (the store/RHM is the bridge's).
        if cmd in ("up", "restart") and isinstance(target, str) and target.startswith("@"):
            brains = [k for k in keys if (reg["services"].get(k) or {}).get("group") == "brain"]
            if brains:
                _repoint_loadout_brain(reg, keys, brains[0])
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
