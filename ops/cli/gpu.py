"""gpu — the ONE VRAM resource manager (shared core).

The models/VRAM type-view of the one console (ops/AGENTS.md): "the operable face of
'it's all resource management'." Reads measured VRAM (nvidia-smi) + per-service budget
from the registry, decides whether a start fits, and tears services down orphan-safely.

POLICY (Tim, 2026-06-06): `company up` REFUSES a start that would blow past the GPU
capacity, and ALWAYS shows what is already holding the card. `--force` overrides.

SHARED CORE (2026-06-06, with the voice-stack session): this is the single VRAM
authority for BOTH the `company` CLI and `voice/lifecycle.py` — voice imports it
instead of keeping a second budget/teardown. stdlib-only so it loads in the 3.14
bridge. Public API: read_gpu, budget_of, is_gpu_service, check_fit, plan_eviction,
teardown, format_state. (Named `gpu` not `resource` — `resource` shadows a stdlib module.)
"""
import os, subprocess, signal, time
from registry import vram_of, ram_of, ceiling_mb
from systemd import port_open, is_active, control as _unit_control
from telemetry import learned_vram

NVSMI = "/usr/lib/wsl/lib/nvidia-smi"

# Evict GPU holders in this group order when making room (last = evicted last).
_EVICT_PRIORITY = {"models": 0, "brain": 1, "voice": 2}


def is_gpu_service(svc):
    """Does this service occupy the GPU? (has a vram_mb estimate OR a config gpu_util OR a config
    `_profile` it can auto-allocate from — a profiled model with no static gpu_util still pins VRAM)."""
    c = svc.get("config") or {}
    return bool(vram_of(svc) or c.get("gpu_util") or c.get("_profile"))


# The activation/CUDA-graph/fragmentation headroom (MB) auto-allocation adds ON TOP of measured weights
# + KV, before dividing by the ceiling. NOT a hardcoded literal: read from the registry
# (registry-is-truth, mirrors vram_ceiling_mb / ram_headroom_mb); this default applies only if unset.
# Rationale (build-log 01-serving §D4): bare weights+KV omits the CUDA context, activation peaks, and
# allocator fragmentation that live INSIDE vLLM's gpu_util fraction; ~512 MB lands the computed util
# just above the old hand-tuned literals (chat-4b: 0.419 vs the hand-tuned 0.40), so a model is never
# starved and never over-grabs.
_VRAM_OVERHEAD_DEFAULT_MB = 512


def _vram_overhead_mb(reg):
    return reg.get("vram_overhead_mb", _VRAM_OVERHEAD_DEFAULT_MB)


def auto_gpu_util(reg, key):
    """COMPUTE the gpu_util fraction a model NEEDS, from its MEASURED footprint — the dissolution of the
    static-memory-allocation class (CAPABILITY-WIRING-MAP.md ⚑; build-log 01-serving §D3/D4). Returns the
    fraction in (0,1], or None when the model has no `_profile` to size from (then a static gpu_util is the
    explicit override, or the caller fails loud).

    The card already exposes every input (no estimate, no guess):
      weights  = config._profile.fixed_mb       (measured resident weights, KV separated out)
      KV       = _profile.kv_kb_per_token × max_model_len / 1024  (KV for the TARGET context)
      overhead = reg.vram_overhead_mb            (activation/CUDA-graph/fragmentation margin)
      gpu_util = (weights + KV + overhead) / vram_ceiling_mb
    Size each model to its NEED (never starved), taking only that slice (co-residence preserved). vLLM has
    no '--gpu-memory-utilization auto'; the auto-ness lives HERE, in the resource manager that owns VRAM."""
    svc = reg["services"].get(key)
    if not svc:
        return None
    c = svc.get("config") or {}
    prof = c.get("_profile") or {}
    fixed = prof.get("fixed_mb")
    kv_per_tok = prof.get("kv_kb_per_token")
    mml = c.get("max_model_len")
    if fixed is None or kv_per_tok is None or not mml:
        return None
    kv_mb = kv_per_tok * mml / 1024.0
    need_mb = fixed + kv_mb + _vram_overhead_mb(reg)
    ceiling = ceiling_mb(reg)
    if ceiling <= 0:
        return None
    return min(1.0, need_mb / ceiling)


def budget_vram(reg, key):
    """VRAM to budget for a service, in priority order:
      1. config.gpu_util × ceiling  — the EXPLICIT OVERRIDE: a hand-set static gpu_util is the slice vLLM
         pins, authoritative (and immune to stale telemetry from a previous gpu_util);
      2. auto_gpu_util × ceiling     — COMPUTED from the measured _profile footprint (the dissolution of
         the static-allocation class) for a config model with a profile and NO static override;
      3. learned (measured) telemetry — for non-config services we've actually loaded;
      4. the registry vram_mb estimate."""
    svc = reg["services"][key]
    c = svc.get("config")
    if c and c.get("gpu_util"):
        return int(round(c["gpu_util"] * ceiling_mb(reg)))
    auto = auto_gpu_util(reg, key)
    if auto is not None:
        return int(round(auto * ceiling_mb(reg)))
    return learned_vram(key) or vram_of(svc)


# Public API name for the shared core (voice/lifecycle.py imports this). Same signature.
budget_of = budget_vram


def _vram_source(reg, key):
    """Where a per-service VRAM figure came from — so the view is HONEST about live vs guessed
    (per-process VRAM is unreadable on this WSL box, so the figure is never a direct measurement
    of the process; it's one of three derivations):
      reserved — config.gpu_util × ceiling, the slice vLLM actually pins (authoritative);
      measured — a recorded load-delta from telemetry (the live mechanism: total-GPU jump on load);
      est      — the static registry vram_mb (no load ever measured for it)."""
    svc = reg["services"][key]
    c = svc.get("config")
    if c and c.get("gpu_util"):
        return "reserved"
    if auto_gpu_util(reg, key) is not None:
        return "computed"          # auto-allocated from the measured _profile footprint + KV + overhead
    return "measured" if learned_vram(key) else "est"


def _is_running(svc):
    """True if the service is up. Use the PER-UNIT signal for managed services —
    NOT the port — because model services share ports (chat-* all :8000, the two
    embedders :8004); a port check would mark every same-port sibling as running and
    let the budget gate be bypassed. Manual services have no unit, so fall back to
    their (unique) port."""
    if svc["manage"]["type"] == "manual":
        return port_open(svc.get("port")) is True
    return is_active(svc) == "active"


def _nvsmi_path():
    if os.path.exists(NVSMI):
        return NVSMI
    from shutil import which
    return which("nvidia-smi")


def read_gpu():
    """Measured GPU memory in MB → dict(used, free, total, util) or None if unreadable."""
    smi = _nvsmi_path()
    if not smi:
        return None
    r = subprocess.run([smi, "--query-gpu=memory.used,memory.free,memory.total,utilization.gpu",
                        "--format=csv,noheader,nounits"], capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return None
    used, free, total, util = [int(x.strip()) for x in r.stdout.strip().split(",")]
    return {"used": used, "free": free, "total": total, "util": util}


# The system-RAM headroom (MB) the actuation gate keeps free — never gate down to literally 0 MemAvailable.
# Read from the registry (registry-is-truth, not hardcoded); this default applies only if unset.
_RAM_HEADROOM_DEFAULT_MB = 2048


def _ram_headroom_mb(reg):
    return reg.get("ram_headroom_mb", _RAM_HEADROOM_DEFAULT_MB)


def read_system_ram():
    """Measured SYSTEM RAM in MB → dict(total, available, used) or None if /proc/meminfo is unreadable.
    The RAM analog of read_gpu(). `available` is the kernel's MemAvailable — its own estimate of how much
    can be allocated WITHOUT swapping — which counts ALL processes on the box (Chrome, background evals,
    anything), not just registered services. That is the truth the actuation gate must read: an OOM is
    caused by TOTAL memory pressure, never by the Company's own services in isolation (the 2026-06-28
    cascade was Granite + an embedder + ~44 Chrome procs — none individually over budget)."""
    try:
        with open("/proc/meminfo") as f:
            mi = {}
            for line in f:
                k, _, rest = line.partition(":")
                parts = rest.split()
                if parts:
                    mi[k.strip()] = int(parts[0])           # kB (first field)
    except (OSError, ValueError):
        return None
    if "MemTotal" not in mi or "MemAvailable" not in mi:
        return None
    total = mi["MemTotal"] // 1024
    avail = mi["MemAvailable"] // 1024
    return {"total": total, "available": avail, "used": total - avail}


def running_gpu_services(reg):
    """[(key, vram_mb)] for services that are up (port open) AND occupy the GPU."""
    out = []
    for k, v in reg["services"].items():
        if is_gpu_service(v) and _is_running(v):
            out.append((k, budget_vram(reg, k)))
    return out


def committed_mb(reg):
    """Sum of estimated VRAM across running GPU services."""
    return sum(mb for _, mb in running_gpu_services(reg))


def committed_ram_mb(reg):
    """Sum of ESTIMATED system-RAM across running services (config-time view — 'what we think we hold').
    The actuation gate does NOT use this; it reads live MemAvailable (which also sees non-service
    pressure). This sum is for telemetry / the 'holding memory' display only."""
    return sum(ram_of(v) for v in reg["services"].values() if _is_running(v))


def ram_fit(reg, to_start):
    """The system-RAM leg of the capacity decision for starting `to_start` (service keys).

    need = sum of estimated ram_mb for the NOT-yet-running services in the set (a running one already
    holds its RAM). free = LIVE /proc/meminfo MemAvailable − headroom (read fresh, so all memory pressure
    on the box is counted — the property that makes overcommit impossible-by-code, not just impossible
    among Company services). Returns {ok, need, free, present}. present=False when /proc/meminfo is
    unreadable → ok=True (don't block on an unmeasurable resource; mirrors check_fit's nvidia-smi-absent
    fallback) but the caller is told to warn."""
    svcs = reg["services"]
    need = sum(ram_of(svcs[k]) for k in to_start if not _is_running(svcs[k]))
    sysram = read_system_ram()
    if sysram is None:
        return {"ok": True, "need": need, "free": None, "present": False}
    free = sysram["available"] - _ram_headroom_mb(reg)
    return {"ok": need <= free, "need": need, "free": free, "present": True}


def check_fit_unified(reg, to_start):
    """The FULL capacity decision — BOTH legs: GPU VRAM (check_fit, reused byte-for-byte) AND system RAM
    (ram_fit, live MemAvailable). Returns {vram:{ok,need,free,present}, ram:{ok,need,free,present}, ok}
    where top-level ok = both legs ok. Non-mutating; does NOT touch check_fit or its three existing
    callers — it COMPOSES them, so the VRAM path stays identical and this is the one call that knows about
    both resources (used by the combo-capacity surface and any programmatic actuator)."""
    vok, vneed, vfree, vpresent = check_fit(reg, to_start)
    vram = {"ok": vok, "need": vneed, "free": vfree, "present": vpresent}
    ram = ram_fit(reg, to_start)
    return {"vram": vram, "ram": ram, "ok": vram["ok"] and ram["ok"]}


def validate_combo_capacity(reg, services):
    """CONFIG-TIME 'can this set EVER fit the hardware at all?' check — independent of what is running.
    A loadout/combo whose ESTIMATED totals exceed the hardware is impossible by construction and must
    fail LOUD when configured, not at a 3am OOM. Two ceilings:
      • VRAM: sum of the set's budgeted VRAM  vs  the card ceiling (vram_ceiling_mb).
      • RAM:  sum of the set's estimated ram_mb  vs  MemTotal − headroom.
    Returns a dict the caller renders. ram_cap=None (ram_ok=True) when /proc/meminfo is unreadable —
    config-time can't judge an unmeasurable ceiling, but the live actuation gate still will."""
    svcs = reg["services"]
    for k in services:
        if k not in svcs:
            raise KeyError(f"validate_combo_capacity: unknown service {k!r}")
    vram_need = sum(budget_vram(reg, k) for k in services if is_gpu_service(svcs[k]))
    vram_cap = ceiling_mb(reg)
    ram_need = sum(ram_of(svcs[k]) for k in services)
    sysram = read_system_ram()
    ram_cap = (sysram["total"] - _ram_headroom_mb(reg)) if sysram else None
    vram_ok = vram_need <= vram_cap
    ram_ok = (ram_cap is None) or (ram_need <= ram_cap)
    return {"ok": vram_ok and ram_ok, "vram_ok": vram_ok, "ram_ok": ram_ok,
            "vram_need": vram_need, "vram_cap": vram_cap,
            "ram_need": ram_need, "ram_cap": ram_cap, "ram_present": sysram is not None}


def _running_units(reg):
    """[(key, unit)] for running systemd-UNIT services — the ones systemd accounts (cgroup RAM + CPU).
    Manual/hosted services have no unit and are skipped here (their per-service usage isn't cgroup-measured)."""
    out = []
    for k, v in reg["services"].items():
        m = v.get("manage", {})
        if m.get("type", "").endswith("unit") and m.get("unit") and _is_running(v):
            out.append((k, m["unit"]))
    return out


def _num_or_none(s):
    """Parse a systemd numeric property; '[not set]' / uint64-max (accounting off) → None."""
    try:
        n = int(s)
    except (TypeError, ValueError):
        return None
    return n if 0 <= n < (1 << 63) else None


def _systemd_sample(units):
    """ONE `systemctl --user show` pass over `units` → {unit: (mem_bytes|None, cpu_nsec|None)} from the
    cgroup accounting (MemoryCurrent counts child processes too — e.g. vLLM's EngineCore — so it is the
    TRUE per-service RAM, not just the main PID's RSS). Empty on any failure (caller falls back to est)."""
    if not units:
        return {}
    try:
        r = subprocess.run(["systemctl", "--user", "show", *units, "-p", "Id,MemoryCurrent,CPUUsageNSec"],
                           capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return {}
    out, cur, uid = {}, {}, None
    for line in r.stdout.splitlines():
        if not line.strip():
            if uid:
                out[uid] = (cur.get("mem"), cur.get("cpu"))
            cur, uid = {}, None
            continue
        k, _, val = line.partition("=")
        if k == "Id":
            uid = val
        elif k == "MemoryCurrent":
            cur["mem"] = _num_or_none(val)
        elif k == "CPUUsageNSec":
            cur["cpu"] = _num_or_none(val)
    if uid:
        out[uid] = (cur.get("mem"), cur.get("cpu"))
    return out


def _proc_stat_snapshot():
    """(total_jiffies, idle_jiffies) from /proc/stat's aggregate cpu line, or None."""
    try:
        with open("/proc/stat") as f:
            v = [int(x) for x in f.readline().split()[1:]]
        return sum(v), v[3] + (v[4] if len(v) > 4 else 0)   # idle + iowait
    except (OSError, ValueError, IndexError):
        return None


def measure_now(reg, interval=0.15):
    """ONE shared sample window → (system_cpu, {key: {ram_mb, cpu_pct}}) — ALL of it MEASURED, nothing
    from registry files. System CPU from /proc/stat (busy% = 1 − idle-delta/total-delta) + /proc/loadavg.
    Per-service RAM/CPU from systemd cgroup accounting (MemoryCurrent / CPUUsageNSec) sampled before+after
    a single `interval` sleep, so the whole measured view costs one interval. cpu_pct is top-style
    (100% = one full core; a service can exceed 100% across cores — the system line gives the core count).
    Per-service map is empty for services systemd can't account (manual/hosted/accounting-off) — the caller
    shows those honestly, never a guess-as-reading. The short sleep is fine: format_state is an
    operator-command render (refuse/up/gpu/ensure), never a hot path."""
    units = _running_units(reg)
    unit_to_key = {u: k for k, u in units}
    unit_list = [u for _, u in units]
    st1 = _proc_stat_snapshot()
    sd1 = _systemd_sample(unit_list)
    time.sleep(interval)
    st2 = _proc_stat_snapshot()
    sd2 = _systemd_sample(unit_list)
    sys_cpu = None
    if st1 and st2 and st2[0] > st1[0]:
        dt = st2[0] - st1[0]
        pct = max(0.0, min(100.0, 100.0 * (1.0 - (st2[1] - st1[1]) / dt)))
        cores = os.cpu_count() or 1
        try:
            with open("/proc/loadavg") as f:
                la = f.read().split()
            sys_cpu = {"pct": pct, "load1": float(la[0]), "load5": float(la[1]),
                       "load15": float(la[2]), "cores": cores}
        except (OSError, ValueError, IndexError):
            sys_cpu = {"pct": pct, "load1": 0.0, "load5": 0.0, "load15": 0.0, "cores": cores}
    per = {}
    for u, key in unit_to_key.items():
        mem2, cpu2 = sd2.get(u, (None, None))
        _, cpu1 = sd1.get(u, (None, None))
        rec = {}
        if mem2 is not None:
            rec["ram_mb"] = mem2 / 1024 / 1024
        if cpu1 is not None and cpu2 is not None:
            rec["cpu_pct"] = max(0.0, (cpu2 - cpu1) / 1e9 / interval * 100.0)
        if rec:
            per[key] = rec
    return sys_cpu, per


def format_state(reg):
    """The MEASURED resource picture — shown on refuse and on every `up`, so agents always know the real
    state without a second call. Everything here is measured from the machine, never a registry guess
    presented as a reading (Tim 2026-06-28): GPU from nvidia-smi, RAM from /proc/meminfo, CPU from
    /proc/stat, per-service RAM+CPU from systemd cgroup accounting. Per-service VRAM is the one figure
    this WSL box cannot measure live (nvidia-smi returns per-process used_memory=N/A) — so it shows the
    telemetry-MEASURED load-delta when one exists, else 0 for a CPU-only service, else the gpu_util
    RESERVATION (the slice vLLM actually pins — authoritative, not a guess) or the registry estimate,
    each HONESTLY labelled."""
    gpu = read_gpu()
    ram = read_system_ram()
    sys_cpu, per = measure_now(reg)
    lines = []
    if gpu:
        lines.append(f"  GPU (measured): {gpu['used']/1024:.1f} GB used / "
                     f"{gpu['free']/1024:.1f} GB free / {gpu['total']/1024:.1f} GB  ({gpu['util']}% util)")
    if ram:
        lines.append(f"  RAM (measured): {ram['used']/1024:.1f} GB used / "
                     f"{ram['available']/1024:.1f} GB available / {ram['total']/1024:.1f} GB")
    if sys_cpu:
        lines.append(f"  CPU (measured): {sys_cpu['pct']:.0f}% busy · load "
                     f"{sys_cpu['load1']:.1f}/{sys_cpu['load5']:.1f}/{sys_cpu['load15']:.1f} · "
                     f"{sys_cpu['cores']} cores")
    running = [(k, v) for k, v in reg["services"].items() if _is_running(v)]
    if running:
        lines.append("  resident services (measured · cgroup RAM/CPU; VRAM measured where the card allows):")
        for k, v in sorted(running, key=lambda kv: -per.get(kv[0], {}).get("ram_mb", 0)):
            meas = per.get(k, {})
            if is_gpu_service(v):
                lv = learned_vram(k)
                vram = (f"VRAM ~{lv/1000:.1f} GB (measured)" if lv
                        else f"VRAM ~{budget_vram(reg, k)/1000:.1f} GB ({_vram_source(reg, k)})")
            else:
                vram = "VRAM 0 (CPU-only)"
            ramc = (f"RAM ~{meas['ram_mb']/1000:.1f} GB" if "ram_mb" in meas
                    else f"RAM ~{ram_of(v)/1000:.1f} GB (est)")
            cpuc = f"CPU {meas['cpu_pct']:.0f}%" if "cpu_pct" in meas else "CPU —"
            lines.append(f"    • {k:<16} {vram:<30} {ramc:<14} {cpuc}")
    else:
        lines.append("  resident services: none (GPU clear)")
    return "\n".join(lines)


def check_fit(reg, to_start):
    """Decide whether starting `to_start` (service keys) fits the budget.

    Uses MEASURED free VRAM (truth) vs the SUM of registry estimates for the
    not-yet-running GPU services in the set. Returns (ok, need_mb, free_mb, gpu_present)."""
    svcs = reg["services"]
    need = sum(budget_vram(reg, k) for k in to_start
               if is_gpu_service(svcs[k]) and not _is_running(svcs[k]))
    gpu = read_gpu()
    if gpu is None:
        # Can't measure — fall back to the registry budget (estimate vs ceiling).
        free = ceiling_mb(reg) - committed_mb(reg)
        return need <= free, need, free, False
    return need <= gpu["free"], need, gpu["free"], True


def fit_report(reg, keys):
    """The 'will THIS SELECTION fit?' picture for the settings fit-surface (Tim, 2026-06-07):
    'if things don't fit from what I've selected then it would be able to tell me.'

    Answers TWO distinct questions for a chosen set of GPU services (e.g. a brain + a voice):
      • fits_card  — does the SUM of their config-derived budgets fit the card CEILING? This is the
        capacity question, independent of what's loaded now, and it's what changes when you resize a
        model (brain @ 256K vs @ 64K) — because budget_vram = config.gpu_util × ceiling.
      • fits_now   — do the not-yet-running ones fit the MEASURED free VRAM right now? (reuses check_fit's
        truth: measured free, not estimates.)
    Returns a dict the surface renders directly. Each item carries its budget, group, and running state.
    No silent rounding-away: when it won't fit, `evict` names what to unload and `reason` says why."""
    svcs = reg["services"]
    ceiling = ceiling_mb(reg)
    items = []
    for k in keys:
        if k not in svcs:
            raise KeyError(f"fit_report: unknown service {k!r}")
        s = svcs[k]
        items.append({"key": k, "mb": budget_vram(reg, k) if is_gpu_service(s) else 0,
                      "group": s.get("group"), "gpu": is_gpu_service(s), "running": _is_running(s)})
    need_total = sum(i["mb"] for i in items)
    fits_card = need_total <= ceiling
    gpu = read_gpu()
    free = gpu["free"] if gpu else (ceiling - committed_mb(reg))
    # the live question: only the not-yet-running selected services need NEW room
    need_now = sum(i["mb"] for i in items if i["gpu"] and not i["running"])
    fits_now = need_now <= free
    evict, projected = ([], free)
    if not fits_now:
        evict, projected = plan_eviction(reg, keys, need_now, free)
    return {
        "selection": list(keys),
        "items": items,
        "need_mb": need_total,
        "ceiling_mb": ceiling,
        "fits_card": fits_card,
        "headroom_mb": ceiling - need_total,
        "free_mb": free,
        "need_now_mb": need_now,
        "fits_now": fits_now,
        "evict": evict,
        "projected_free_mb": projected,
        "gpu_present": gpu is not None,
    }


def plan_eviction(reg, to_start, need, free):
    """Choose which running GPU services to stop to fit `need`, sparing the to-start
    set. Evicts models→brain→voice, largest first, only as many as required.
    Returns (evict_keys, projected_free). projected_free may still be < need if even
    evicting every candidate isn't enough (caller must check)."""
    svcs = reg["services"]
    skip = set(to_start)
    cands = [(k, mb) for k, mb in running_gpu_services(reg) if k not in skip]
    cands.sort(key=lambda km: (_EVICT_PRIORITY.get(svcs[km[0]]["group"], 9), -km[1]))
    evict, projected = [], free
    for k, mb in cands:
        if projected >= need:
            break
        evict.append(k)
        projected += mb
    return evict, projected


def _script_token(run):
    """The identifying script path in a manual service's run cmd (for pgrep)."""
    for t in run.split():
        if t.endswith(".py") or t.endswith(".sh"):
            return os.path.expanduser(t)
    return None


def teardown(svc):
    """Orphan-SAFE stop. Returns (ok, message).

    Unit services → `systemctl stop`, which kills the whole systemd CGROUP — this reaps
    vLLM's EngineCore + its spawn helpers, which a plain SIGTERM/SIGKILL on the parent
    does NOT (EngineCore has no OS death-link; it reparents to init and squats ~10 GB —
    upstream #19849, found by the voice-stack session 2026-06-06). So units are the
    orphan-safe path; prefer them.

    Manual/Popen services → process-GROUP teardown: SIGTERM the pgroup, poll, then SIGKILL,
    so child workers die with the parent. (After the 2026-06-06 ear→unit flip there should
    be no manual GPU services left; kept as the robust fallback.)"""
    m = svc["manage"]
    if m.get("type") != "manual":
        return _unit_control(svc, "stop")          # cgroup teardown — reaps EngineCore
    target = _script_token(m.get("run", ""))
    if not target:
        return False, "manual service: cannot identify process (no script in run cmd)"
    pids = subprocess.run(["pgrep", "-f", target], capture_output=True, text=True).stdout.split()
    if not pids:
        return True, "already stopped"
    pgids = set()
    for p in pids:
        try:
            pgids.add(os.getpgid(int(p)))
        except (ProcessLookupError, ValueError):
            pass
    for g in pgids:
        try:
            os.killpg(g, signal.SIGTERM)
        except ProcessLookupError:
            pass
    for _ in range(8):                              # poll up to ~8s for graceful exit
        time.sleep(1)
        if not subprocess.run(["pgrep", "-f", target], capture_output=True, text=True).stdout.strip():
            return True, f"stopped (process-group SIGTERM, {len(pids)} pid(s))"
    for g in pgids:                                 # still alive → force
        try:
            os.killpg(g, signal.SIGKILL)
        except ProcessLookupError:
            pass
    return True, f"stopped (process-group SIGKILL after timeout, {len(pids)} pid(s))"
