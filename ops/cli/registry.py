"""registry — load + query the self-describing service registry (services.json).

The registry is the single source of truth (see ops/AGENTS.md). This module owns
no state; it only reads and answers questions about services.json. stdlib-only.
"""
import json, os

OPS = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))  # .../ops  (cli/ is under ops/)
REG_PATH = os.path.join(OPS, "services.json")


def load():
    with open(REG_PATH) as f:
        return json.load(f)


def services(reg):
    return reg["services"]


def groups(reg):
    return reg["groups"]


def ceiling_mb(reg):
    """The VRAM budget the resource manager enforces against."""
    return reg.get("vram_ceiling_mb", 16376)


def vram_of(svc):
    """Approx VRAM cost (MB) of a service — top-level vram_mb, else load.vram_mb, else 0.
    0 means 'does not occupy the GPU' (e.g. the canvas, the bridge, ollama-idle)."""
    return svc.get("vram_mb") or svc.get("load", {}).get("vram_mb") or 0


def serve_script(svc):
    """Absolute path to the service's serve script (for `swap`), or None."""
    s = svc.get("serve")
    return os.path.expanduser(s) if s else None


def shared_ports(reg):
    """Ports used by more than one service (e.g. chat-2b + chat-08b both :8003).
    On these, port-open does NOT tell you WHICH service is up — only the per-unit
    is-active does. Callers use this to avoid false 'running' reads on a sibling's port."""
    from collections import Counter
    c = Counter(v["port"] for v in reg["services"].values() if v.get("port"))
    return {p for p, n in c.items() if n > 1}


def resolve(reg, target):
    """target → list of service keys.
    None/'default' → the bare-`company up` set (autostart flag = surface).
    'all' → everything. A group name → its members. A service key → just it."""
    svcs = reg["services"]
    if target in (None, "default"):
        return [k for k, v in svcs.items() if v.get("autostart")]
    if target == "all":
        return list(svcs)
    if target in reg["groups"]:
        return [k for k, v in svcs.items() if v["group"] == target]
    if target in svcs:
        return [target]
    raise KeyError(target)
