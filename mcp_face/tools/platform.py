"""mcp_face/tools/platform.py — the PLATFORM tool: list registered sources + INVOKE their capabilities.
Mirror-Registry System, LANE-INVOKE (2026-06-28). File-drop (pkgutil auto-register), one consolidated
op-parameterised tool per the MCP-DESIGN-PRINCIPLE.

The capability tool READS the registry (what a source can do). THIS tool is the active half — list the
registered platforms and RUN any of their capabilities through the universal, posture-gated invocation
layer (introspection.invoke). Works for ANY registered source (a new platforms/<id>.py row is invokable
for free). `invoke` is consequential (it runs a real subprocess) so it is NOT posture='safe' — operator
door only; and the DISCOVERED posture gates it (locked/hazard REFUSE unless confirm=True).
"""
from __future__ import annotations
from typing import Literal

OPS = ("list", "describe", "invoke", "gate")


def register(mcp, suite):
    @mcp.tool()
    def platform(op: Literal["list", "describe", "invoke", "gate"], platform_id: str = "",
                 argv: list[str] | None = None, confirm: bool = False, timeout_s: int = 60) -> dict:
        """Registered SOURCES (CLIs/APIs/…) + INVOKE their capabilities (Mirror-Registry).
          op="list"     — every registered platform {id, display_name, invocation_kind}.
          op="describe" — one platform (`platform_id`) row + its capability counts from the registry.
          op="gate"     — DRY-RUN the posture gate for `platform_id` + `argv` (no run): what postures the
                          flags carry + whether it would be blocked. Use before invoke.
          op="invoke"   — RUN `platform_id` with `argv` (the command AFTER the binary, e.g.
                          ['pr','create','--draft'] for gh, ['exec','--output-last-message','/tmp/x','-']
                          for codex), posture-GATED: a locked/hazard capability REFUSES unless
                          `confirm=True`. Returns {ok, exit_code, stdout, stderr, gate}. Consequential.
        """
        from introspection.platforms import platform_registry
        from introspection import invoke as _inv
        try:
            # reach the registry via the SUITE (triggers lazy Suite construction → ledger-backed registry
            # set), NOT the bare module singleton (which is unset until the Suite is built in this process —
            # the live-use gap, 2026-06-28). Pass it explicitly to gate/invoke so they never hit an unset
            # singleton. Falls back to None (the singleton) if the suite has no registry attribute.
            _reg = getattr(suite, "capability_registry", None)
            preg = platform_registry()
            if op == "list":
                out = []
                for pid in sorted(preg.ids()):
                    p = preg[pid]
                    out.append({"id": pid, "display_name": getattr(p, "display_name", pid),
                                "invocation_kind": getattr(p, "invocation_kind", "")})
                return {"op": "list", "platforms": out, "total": len(out)}
            if not platform_id or platform_id not in preg:
                return {"op": op, "ok": False,
                        "error": f"platform_id {platform_id!r} not registered. Known: {sorted(preg.ids())}."}
            p = preg[platform_id]
            if op == "describe":
                from introspection.registry import capability_registry
                reg = capability_registry()
                kinds = {}
                for k in reg:
                    if k.startswith(f"{platform_id}/"):
                        e = reg.entries[k]
                        kinds[e.kind] = kinds.get(e.kind, 0) + 1
                return {"op": "describe", "id": platform_id,
                        "display_name": getattr(p, "display_name", platform_id),
                        "invocation_kind": getattr(p, "invocation_kind", ""), "capability_counts": kinds}
            if op == "gate":
                return {"op": "gate", "platform": platform_id, **_inv.gate(p, argv or [], registry=_reg)}
            if op == "invoke":
                return {"op": "invoke", **_inv.invoke(p, argv or [], confirm=confirm, timeout_s=timeout_s, registry=_reg)}
            return {"op": op, "ok": False, "error": f"unknown op {op!r}"}
        except Exception as e:  # noqa: BLE001 — teaching error, never a silent failure
            return {"op": op, "ok": False, "error": f"{type(e).__name__}: {e}"}

    return (platform,)
