"""gpu — the resource manager: read the card, enforce the VRAM budget.

This is the models/VRAM type-view of the one console (ops/AGENTS.md): "the operable
face of 'it's all resource management'." It reads measured VRAM from nvidia-smi and
the per-service estimates from the registry, and decides whether a start fits.

POLICY (Tim, 2026-06-06): `company up` REFUSES a start that would blow past the GPU
capacity, and ALWAYS shows what is already holding the card so any agent knows the
state. `--force` overrides (loudly). stdlib-only.
"""
import os, subprocess
from registry import vram_of, ceiling_mb
from systemd import port_open, is_active
from telemetry import learned_vram

NVSMI = "/usr/lib/wsl/lib/nvidia-smi"

# Evict GPU holders in this group order when making room (last = evicted last).
_EVICT_PRIORITY = {"models": 0, "brain": 1, "voice": 2}


def budget_vram(svc, key):
    """VRAM to budget for a service: the MEASURED resident from telemetry if we've
    learned it, else the registry estimate. Measured beats guessed."""
    return learned_vram(key) or vram_of(svc)


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
        if vram_of(v) and _is_running(v):
            out.append((k, vram_of(v)))
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
    need = sum(budget_vram(svcs[k], k) for k in to_start
               if vram_of(svcs[k]) and not _is_running(svcs[k]))
    gpu = read_gpu()
    if gpu is None:
        # Can't measure — fall back to the registry budget (estimate vs ceiling).
        free = ceiling_mb(reg) - committed_mb(reg)
        return need <= free, need, free, False
    return need <= gpu["free"], need, gpu["free"], True


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
