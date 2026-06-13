"""platforms/_wiring.py — the head_builder BOOTSTRAP/WIRING for the platform rows (Level-2, NOT a row).
Mirror-Registry System, LANE-SUPERVISOR-REFACTOR (ROW-PURITY, 2026-06-14).

WHY THIS FILE EXISTS (row-purity). A `platforms/<id>.py` row is PURE DATA — a `PLATFORM = {...}` dict
the registry validates via `PlatformEntry.model_validate`. A Pydantic model cannot hold a callable, so
the one non-data thing the Mirror-Registry needs from the consumer — the zero-arg `head_builder` thunk
that returns the consumer's UNCONDITIONAL spawn-head argv (the F-FIX-2 transport-invariant derivation
input) — used to be registered by a `_register_head_builder()` function INSIDE `claude_code.py`. That
made the instance row non-pure (it carried a def + a `runtime` import). The generalization-proof needs
the instance row to be the CLEAN template every future platform copies: imports + the dict, nothing
else. So the thunk registration moves HERE, the wiring module.

The `_`-prefix means the PlatformRegistry's file-discovery SKIPS this file (it is not a platform row —
`platforms.py` discover() ignores `_`-prefixed files). It is imported EXPLICITLY by the consumer that
needs the LIVE transport-invariant derivation (runtime/suite.py at registry construction; the
crosscheck acceptance test). Importing it REGISTERS every platform's head_builder thunk with the
engine.

CYCLE DISCIPLINE (PG-D6). The forbidden import edge is `introspection/ → runtime/`. This file lives in
`platforms/` and imports `runtime.session_supervisor` (platforms → runtime — ALLOWED, the same edge
`claude_code.py` used before). Its CALLERS are runtime/tests, never `introspection/` — so introspection
never transitively imports runtime. `introspection.platforms.platform_registry()` does NOT import this
module; a context that builds the registry without wiring (a contracts-only validation) simply keeps
the row's DECLARED `transport_invariants` (which is the post-R6-correct set — see claude_code.py), and
the engine validates it non-empty. Wiring ADDS live re-derivation (drift detection); it is never a
correctness pre-condition.

This module is idempotent: register_head_builders() can be called repeatedly (re-registering the same
thunk is a harmless dict overwrite). It is also invoked at import (the module-level call at the bottom)
so a bare `import platforms._wiring` is sufficient to wire the thunks.
"""
from __future__ import annotations


def register_head_builders() -> None:
    """Register every platform's head_builder thunk with the Mirror-Registry engine (F-FIX-2). The
    thunk wraps the consumer's `SessionSupervisor._build_spawn_cmd` (the function is `_build_spawn_cmd`,
    NOT `_build_cmd` — F-FIX-8) called with MINIMAL args (resume=None, fork=False, no optional body
    params), so its return is exactly the unconditional spawn head — the input the engine parses for
    the R1 transport-invariant set. Guarded so a context that cannot import the supervisor/engine (a
    contracts-only validation) is a clean no-op: the platform rows then keep their DECLARED (post-R6)
    transport_invariants, and the engine validates them non-empty."""
    try:
        from introspection.engine import register_head_builder
        from runtime.session_supervisor import SessionSupervisor
    except Exception:
        return  # supervisor/engine not importable here — the rows' declared R1 lists stand
    # claude-code (instance #1). A second platform of a known kind adds ONE more register call here
    # (or its own wiring module) — never a def back inside the pure-data row.
    register_head_builder(
        "claude-code",
        lambda: SessionSupervisor._build_spawn_cmd(claude_bin="claude", resume=None, fork=False),
    )


# Wire at import so `import platforms._wiring` is sufficient (idempotent — safe to import repeatedly).
register_head_builders()
