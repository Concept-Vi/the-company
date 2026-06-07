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
from registry import vram_of, ceiling_mb
from systemd import port_open, is_active, control as _unit_control
from telemetry import learned_vram

NVSMI = "/usr/lib/wsl/lib/nvidia-smi"

# Evict GPU holders in this group order when making room (last = evicted last).
_EVICT_PRIORITY = {"models": 0, "brain": 1, "voice": 2}


def is_gpu_service(svc):
    """Does this service occupy the GPU? (has a vram_mb estimate OR a config gpu_util)."""
    return bool(vram_of(svc) or svc.get("config", {}).get("gpu_util"))


def budget_vram(reg, key):
    """VRAM to budget for a service, in priority order:
      1. config.gpu_util × ceiling  — for config-driven models this IS the reservation
         vLLM takes from the card, so it's authoritative (and immune to stale telemetry
         from a previous gpu_util);
      2. learned (measured) telemetry — for non-config services we've actually loaded;
      3. the registry vram_mb estimate."""
    svc = reg["services"][key]
    c = svc.get("config")
    if c and c.get("gpu_util"):
        return int(round(c["gpu_util"] * ceiling_mb(reg)))
    return learned_vram(key) or vram_of(svc)


# Public API name for the shared core (voice/lifecycle.py imports this). Same signature.
budget_of = budget_vram


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


def format_state(reg):
    """The 'what's holding the card' block — shown on refuse and on every `up`,
    so agents always know the state without a second call."""
    gpu = read_gpu()
    lines = []
    if gpu:
        lines.append(f"  GPU (measured): {gpu['used']/1024:.1f} GB used / "
                     f"{gpu['free']/1024:.1f} GB free / {gpu['total']/1024:.1f} GB  ({gpu['util']}% util)")
    running = running_gpu_services(reg)
    if running:
        lines.append("  holding the card:")
        for k, mb in sorted(running, key=lambda x: -x[1]):
            lines.append(f"    • {k:<15} ~{mb/1000:.1f} GB")
    else:
        lines.append("  holding the card: nothing (GPU is clear)")
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
