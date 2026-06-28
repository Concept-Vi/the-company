"""introspection/invoke.py — the UNIVERSAL, posture-gated INVOCATION layer (run any capability of any
registered source). Level 1, platform-agnostic — Mirror-Registry System, LANE-INVOKE (2026-06-28).

The registry was a passive CATALOG (discover/classify/address). This is the active half: INVOKE a
registered source's capability through ONE mechanism, gated by the DISCOVERED posture. It mirrors the
DISCOVER design exactly — an INVOKERS map selected by the platform's `invocation_kind` (subprocess built;
rest/mcp/grpc/sdk/library NAMED-but-UNBUILT → MissingInvokerError naming the class, the §8.3 gap-surface,
never a silent no-op). ZERO platform-name literals (the lift holds — it dispatches on invocation_kind, a
stable selector, never on a platform's identity).

POSTURE GATE (the safety floor, registry-is-truth): every flag/subcommand in the request is looked up in
the live CapabilityRegistry; the HIGHEST posture decides. `locked` (a fabric transport-invariant) and
`hazard` (a danger-named capability, e.g. --dangerously-bypass-*) REFUSE unless `confirm=True` (operator
consent) — with the teaching, never a silent run. `consent` (widens the session surface) is ALLOWED but
RECORDED (auditable). `safe`/`unmatched` run. A novel/unknown flag is `unmatched` (runs, recorded) — the
gate fails OPEN for unknowns (expose-not-gate, Tim Ruling 1) but LOUD for the known-dangerous.

This is general for ANY source: a new platforms/<id>.py row with invocation_kind='subprocess' is invokable
here for free; a new invocation_kind needs one INVOKER (gap-surfaced), exactly like a new discoverer.
"""
from __future__ import annotations

_SEVERITY = {"locked": 4, "hazard": 3, "consent": 2, "safe": 1, "unmatched": 0}
_BLOCK = {"locked", "hazard"}          # refuse without confirm


class MissingInvokerError(RuntimeError):
    """An invocation_kind whose adapter is not built (the gap-surface, never a silent no-op)."""


def _select_invoker(invocation_kind: str):
    from introspection.adapters import INVOKERS
    inv = INVOKERS.get(invocation_kind)
    if inv is None:
        raise MissingInvokerError(
            f"invoke: no invoker built for invocation_kind={invocation_kind!r} — built: {sorted(INVOKERS)}. "
            f"A platform selecting an unbuilt kind fails loud naming the gap (§8.3); build the adapter when "
            f"a 2nd platform of this kind registers. Never a silent no-op.")
    return inv()


def _registry():
    from introspection.registry import capability_registry
    return capability_registry()


def gate(platform, argv: list[str], *, registry=None) -> dict:
    """Look up each flag/subcommand token in argv against the capability registry and compute the gate.
    Returns {posture, blocked, used:[{token,kind,posture,axis}], unknown:[...]}. PURE (no side effects)."""
    reg = registry if registry is not None else _registry()
    used, unknown, worst = [], [], "unmatched"
    for tok in argv:
        if not tok or tok.startswith("-") is False and "=" in tok:
            continue
        kind = "flag" if tok.startswith("-") else "subcommand"
        # flag may be --name=value → match the --name part
        name = tok.split("=", 1)[0] if tok.startswith("-") else tok
        entry = reg.get(f"{platform.id}/{kind}/{name}") or reg.get(f"{kind}/{name}")
        if entry is None:
            if tok.startswith("-"):
                unknown.append(name)
            continue
        used.append({"token": name, "kind": entry.kind, "posture": entry.posture, "axis": entry.axis})
        if _SEVERITY.get(entry.posture, 0) > _SEVERITY.get(worst, 0):
            worst = entry.posture
    return {"posture": worst, "blocked": worst in _BLOCK, "used": used, "unknown": unknown}


def invoke(platform, argv: list[str], *, confirm: bool = False, timeout_s: int = 60,
           registry=None, stdin: str | None = None) -> dict:
    """Run a registered source's capability through its invocation adapter, posture-gated. `argv` is the
    command AFTER the binary (subcommand + flags + args), e.g. ['pr','create','--draft'] for gh, or
    ['exec','--output-last-message','/tmp/x','-'] for codex. Returns a structured result. REFUSES a
    locked/hazard capability unless confirm=True (with the teaching). Never a silent dangerous run."""
    g = gate(platform, argv, registry=registry)
    if g["blocked"] and not confirm:
        return {"ok": False, "refused": True, "gate": g, "platform": platform.id,
                "reason": (f"refused: this invocation uses a {g['posture'].upper()} capability "
                           f"({', '.join(u['token'] for u in g['used'] if u['posture'] in _BLOCK)}). "
                           f"locked = a fabric transport-invariant; hazard = danger-named. Pass confirm=True "
                           f"(operator consent) to proceed. registry-is-truth, never a silent dangerous run.")}
    invoker = _select_invoker(getattr(platform, "invocation_kind", "subprocess"))
    exe = invoker.find_executable(platform.executable_locator)
    try:
        cp = invoker.run_capture([exe] + list(argv), timeout_s=timeout_s, stdin=stdin)
    except Exception as e:  # noqa: BLE001 — surface the invocation failure, never swallow
        return {"ok": False, "refused": False, "gate": g, "platform": platform.id,
                "error": f"{type(e).__name__}: {str(e)[:200]}"}
    return {"ok": cp.returncode == 0, "refused": False, "gate": g, "platform": platform.id,
            "exit_code": cp.returncode, "stdout": (cp.stdout or "")[:8000],
            "stderr": (cp.stderr or "")[:4000] if cp.stderr else ""}
