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
  company models           what's on disk (HF cache + Ollama)
  company swap SERVICE MODEL_ID   point a model service at another model + restart
  company bench KIND [args]       chat|embed|suite|long-ctx
  company telemetry        learned model load times + measured VRAM (vs estimates)
  company help

TARGET = a service key, a group (core|brain|voice|models|reach), or `all`.
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
    """After starting, block until each GPU service is serving, then record telemetry."""
    for k in _gpu_keys(reg, keys):
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
        after = gpu.read_gpu()
        resident = max(0, free_before - after["free"]) if after else 0
        if served:
            rec = telemetry.record(k, elapsed, resident, vram_of(svc))
            print(f"  ✓ {k} serving in {elapsed:.0f}s · measured ~{resident/1000:.1f} GB "
                  f"(est ~{vram_of(svc)/1000:.1f} GB) · recorded")
        else:
            print(f"  ✗ {k} did not come up within {timeout}s (not recorded)")


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
    if cmd == "models":
        print(models.inventory()); return
    if cmd == "telemetry":
        print(telemetry.rollups()); return
    if cmd == "swap":
        rest = [a for a in args[1:] if not a.startswith("-")]
        if len(rest) < 2:
            sys.exit("usage: company swap SERVICE MODEL_ID")
        ok, msg = models.swap(reg, rest[0], rest[1])
        print(("  ✓ " if ok else "  ✗ ") + msg)
        sys.exit(0 if ok else 1)
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
