"""runtime/modes_registry.py — the FILE-DISCOVERED presence-MODE registry.

The presence modes (listening/text-only/background/focus/walkthrough/watch-and-react/decide-for-me/off …)
were the system's ONE remaining hardcoded dict (a `MODE_REGISTRY = {...}` literal in suite.py) — the lone
violation of the registry-is-truth law that roles/projections/mode_detection_rules all honour. This makes
modes an OPEN, file-discovered registry like the rest (Tim 2026-06-28: "modes are a starter set, open,
all in registries, adjustable"): a `modes/` dir, one `modes/<id>.py` per mode declaring a module-level
`MODE` dict, discovered → the same ordered {id: decl} the literal produced. Add a mode = drop a file;
edit a mode = edit its file; no code edit.

Mirrors the MECHANISM of runtime/mode_detection_rules.py / runtime/roles.py (os.listdir → importlib,
fail-loud on a malformed entry, id == filename stem). Modes are ORDER-BEARING (MODES = tuple(registry);
modes_acceptance asserts len + exact order; the _M_* mode-sets frozenset over it), so — like the detection
rules — each file declares an explicit integer `order` (lower first) and discovery sorts by (order, id),
NEVER by listdir/filename order. `order` is used for sequencing only and is STRIPPED from the returned
decl, so each entry is byte-for-byte the dict the literal held (no extra key leaks to MODE_SPECS /
capabilities / the FE).

The id is the filename stem VERBATIM (hyphens kept — `text-only`, `watch-and-react`, `decide-for-me` are
real mode ids the dial/set_mode validate against). The importlib spec name sanitises hyphens; the id does not.
"""
from __future__ import annotations

import importlib.util
import os

# The axis schema a mode declares (the union the literal carried). `id` is the filename; the rest are the
# fields every derived view reads. subtypes is optional (absent → None, byte-for-byte today). order is
# discovery-only (stripped from the decl). Required = everything a derived view reads unconditionally.
_REQUIRED = ("label", "directive", "resolution", "consent", "grain", "shape", "stage",
             "live", "reserve_r", "per_role_ctx", "main_ctx_tokens", "brain_config")
_OPTIONAL = ("subtypes", "loadout_class", "voice")


def _load_module(path: str):
    name = "_mode_" + os.path.splitext(os.path.basename(path))[0].replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _build_mode(mid: str, decl: dict) -> tuple[int, dict]:
    """Validate + normalise one mode declaration → (order, decl-without-order). Fail loud on a malformed
    mode (mirrors RoleRegistry._build_role / the detection-rule validator) — a declared mode with a bad
    shape RAISES, never a silent skip."""
    if not isinstance(decl, dict):
        raise TypeError(f"mode {mid!r}: MODE must be a dict, got {type(decl).__name__} — fail loud.")
    order = decl.get("order")
    if not isinstance(order, int) or isinstance(order, bool):
        raise ValueError(f"mode {mid!r}: MODE must declare an integer `order` (sequencing; modes are "
                         f"order-bearing). got {order!r} — fail loud.")
    missing = [k for k in _REQUIRED if k not in decl]
    if missing:
        raise ValueError(f"mode {mid!r}: MODE missing required field(s) {missing} — the mode schema is "
                         f"{list(_REQUIRED)} (+ optional {list(_OPTIONAL)}). Fail loud.")
    out = {k: v for k, v in decl.items() if k != "order"}    # strip order → byte-for-byte the literal entry
    return order, out


def discover_modes(dirs) -> dict:
    """Read every `modes/<id>.py` under `dirs` → an ordered {id: decl} dict (sorted by (order, id)),
    EXACTLY the shape the old MODE_REGISTRY literal produced. Fail loud on a malformed/duplicate mode.
    A non-mode file (no module-level MODE, or starting with `_`) is skipped (the constitution/AGENTS.md)."""
    if isinstance(dirs, str):
        dirs = [dirs]
    found: dict[str, tuple[int, dict]] = {}
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".py") or fn.startswith("_"):
                continue
            mid = fn[:-3]
            mod = _load_module(os.path.join(d, fn))
            decl = getattr(mod, "MODE", None)
            if decl is None:
                continue                                      # a non-mode .py (helper) — skip, never fail
            if mid in found:
                raise ValueError(f"duplicate mode id {mid!r} across {dirs} — fail loud.")
            found[mid] = _build_mode(mid, decl)
    if not found:
        raise RuntimeError(f"discover_modes: no modes found under {dirs} — the modes/ registry is empty "
                           f"(registry-is-truth: a mode is a file). Fail loud, never an empty dial.")
    ordered_ids = sorted(found, key=lambda m: (found[m][0], m))
    return {mid: found[mid][1] for mid in ordered_ids}


# The repo modes/ dir, REPO-ROOT-anchored (not cwd — a relative default returns [] silently when cwd≠root).
MODES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modes")
