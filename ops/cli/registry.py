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


def ram_of(svc):
    """Approx SYSTEM-RAM cost (MB) of a service — top-level ram_mb, else load.ram_mb, else 0.
    The host-memory twin of vram_of: a CPU-resident model (e.g. stt-granite fp32 ~9 GB, the ONNX ears,
    whisper.cpp) costs system RAM and ZERO VRAM, so it is invisible to the VRAM budget — yet host-RAM
    overcommit is what triggers the kernel OOM-killer. 0 means 'no material resident host footprint'
    (a timer with no process, ollama idle). Estimates, like vram_mb — the live actuation gate
    (gpu.ram_fit) reads real /proc/meminfo MemAvailable, so an imperfect estimate can't cause an OOM."""
    return svc.get("ram_mb") or svc.get("load", {}).get("ram_mb") or 0


def serve_script(svc):
    """Absolute path to the service's serve script (for `swap`), or None."""
    s = svc.get("serve")
    return os.path.expanduser(s) if s else None


def combos(reg):
    """Named service-sets meant to run together (the `_doc` key is not a combo).

    LOADOUT VARIANTS — the "class with configurations" mechanism (2026-06-28). A combo is normally a
    bare `{services:[...], note}`. A VARIANT instead declares `extends: <base-combo>` and inherits the
    base's resolved service list, then overrides just what differs:
      • swap: {old-service: new-service}   — replace one slot in place (e.g. the ear)
      • remove: [services] / add: [services]
    so a "class" is a base loadout (e.g. `interaction`) and its variants (e.g. `interaction-parakeet`)
    state only the difference. This resolver returns each combo with a concrete `services` list (plus a
    `variant_of` marker), so BOTH consumers — the `combos` listing and `resolve()`'s `up @combo` — see
    the final set with no second resolution. Fail-loud on a missing base, a swap target not in the base,
    a service that isn't registered, or an extends-cycle (registry-is-truth: never start a fabricated set).
    """
    raw = {k: v for k, v in reg.get("combos", {}).items() if k != "_doc"}
    svcs = reg.get("services", {})
    resolved: dict = {}

    def resolve_one(name, seen):
        if name in resolved:
            return resolved[name]
        if name not in raw:
            raise KeyError(f"combo {name!r} (referenced via extends) does not exist")
        if name in seen:
            raise ValueError(f"combo extends-cycle through {name!r}")
        c = dict(raw[name])
        base_name = c.get("extends")
        if base_name:
            base = resolve_one(base_name, seen | {name})
            services = list(base["services"])
            for old, new in (c.get("swap") or {}).items():
                if old not in services:
                    raise ValueError(f"combo {name!r}: swap source {old!r} not in base {base_name!r} ({services})")
                services[services.index(old)] = new
            for rm in (c.get("remove") or []):
                if rm in services:
                    services.remove(rm)
            for ad in (c.get("add") or []):
                if ad not in services:
                    services.append(ad)
            c["services"] = services
            c["variant_of"] = base_name
        # registry-is-truth guard: every service in the (possibly variant-built) set must be registered
        for s in c.get("services", []):
            if s not in svcs:
                raise ValueError(f"combo {name!r}: unknown service {s!r} (not in services.json)")
        resolved[name] = c
        return c

    for name in raw:
        resolve_one(name, set())
    return resolved


def save(reg):
    """Persist the registry back to services.json (pretty JSON). Used by `config`/`swap`."""
    with open(REG_PATH, "w") as f:
        json.dump(reg, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _coerce(s):
    if not isinstance(s, str):
        return s                       # already a real value (int/float/bool from a JSON body) — keep as-is
    low = s.lower()
    if low in ("true", "false"):
        return low == "true"
    for cast in (int, float):
        try:
            return cast(s)
        except ValueError:
            pass
    return s


def set_config(reg, key, field, value):
    """Set one field in a service's `config` block and save. Requires an existing
    config block (so we never create a half-formed one from the CLI)."""
    svc = reg["services"].get(key)
    if svc is None:
        raise KeyError(key)
    c = svc.get("config")
    if c is None:
        raise ValueError(f"{key} has no `config` block to edit "
                         f"(legacy script service — see cli/UPDATING.md to migrate it).")
    c[field] = _coerce(value)
    save(reg)
    return c[field]


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
    if isinstance(target, str) and target.startswith("@"):
        name = target[1:]
        cs = combos(reg)
        if name in cs:
            return list(cs[name]["services"])
        raise KeyError(target)
    if target in reg["groups"]:
        return [k for k, v in svcs.items() if v["group"] == target]
    if target in svcs:
        return [target]
    raise KeyError(target)
