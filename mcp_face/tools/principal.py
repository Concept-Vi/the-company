"""mcp_face/tools/principal.py — the ONE identity door (design v2: PRINCIPAL) — presence, NOT access.

WHO IS THIS / WHO AM I, answered once: the four resolvers the identity review mapped (identity.resolve
[live presence] · principals.resolve_kind [agent-vs-viewer] · the durable registry record ·
session_scan [self]) composed behind one read door. ACCESS (may/grant — fail-CLOSED authorization over
container.* Postgres) is DELIBERATELY a separate door: a different identity space with no join column
to sessions and the opposite failure mode (the review was unanimous — presence must never answer a
permission question).

  principal (read, posture="safe"):
    op="resolve" — any target (uuid | ch-handle | as-id | agent-id | cwd | session://X | clone://X)
                   → ONE enriched row: the live PresenceRow (transports/reachable by PROBE) + the
                   principal KIND (agent|viewer|ambiguous, with evidence) + the durable registry
                   record when known. Not-found → an honest {found: false, reason} (never fabricated).
    op="roster"  — every registered principal (the reg files, non-destructive) with kind + live state.
    op="whoami"  — THIS session's own identity (the self-resolution ladder; ambiguous → teaching).

  principal_act (write, operator-tier):
    op="describe" — self-description (name/description) onto YOUR OWN reg (idempotent per claude_pid;
                    the register_self path — works with or without a live .mjs port; an .mjs session's
                    announce/profile keep working, same file).
    op="register" — the durable ROLE-NAME + surviving-inbox capability lives in the EXTERNAL substrate
                    (mcp__supabase_admin_mcp__agent_register, a separate server + Postgres with no join
                    to sessions yet). Folding it needs the cross-repo seam designed first (the
                    addressing review: NEEDS-NEW-DATA) — until then this op TEACHES where to go rather
                    than faking a fold.

File-drop tools (pkgutil auto-register).
"""
from __future__ import annotations

from typing import Literal

from contracts.tools import ToolAnnotations as CompanyToolAnnotations
from mcp.types import ToolAnnotations as SDKToolAnnotations

READ_OPS = ("resolve", "roster", "whoami")
WRITE_OPS = ("describe", "register")


def _to_sdk_annotations(ann: CompanyToolAnnotations, title: str,
                        posture: str = "") -> SDKToolAnnotations:
    extra = {"posture": posture} if posture else {}
    return SDKToolAnnotations(
        title=title, readOnlyHint=ann.readonly, destructiveHint=ann.destructive,
        idempotentHint=ann.idempotent, openWorldHint=False, **extra)


def register(mcp, suite):
    @mcp.tool(annotations=_to_sdk_annotations(
        CompanyToolAnnotations(readonly=True, destructive=False, idempotent=True),
        "Fabric principal — who is this / who am I (read)", posture="safe"))
    def principal(op: Literal["resolve", "roster", "whoami"], target: str = "") -> dict:
        """WHO IS THIS / WHO AM I — the one identity read (presence + kind + durable record; NOT
        access/permissions, which is the separate `access` door). Pick `op`:

          op="resolve" — `target` (uuid | ch-handle | as-id | agent-id | cwd | session://X | clone://X)
                → one enriched row: live reachability by PROBE (transports/reachable), principal kind
                (agent|viewer|ambiguous + evidence), the durable registry record when known. Honest
                {found: false} when nothing matches — never fabricated, never a guess on ambiguity.
          op="roster" — every registered principal (non-destructive read of the reg files) with kind
                + live state where live.
          op="whoami" — THIS session's own identity via the self-resolution ladder (fail-loud teaching
                on ambiguity rather than mis-identifying self)."""
        from runtime import identity as _identity
        from runtime import principals as _principals

        if op == "resolve":
            if not target.strip():
                raise ValueError("principal(op='resolve') needs `target` — any identity form "
                                 "(uuid/handle/agent-id/cwd/session://X/clone://X).")
            reg_fn = getattr(suite, "get_agent_session", None)
            try:
                pr = _identity.resolve(target.strip(), registry=reg_fn)
            except _identity.AmbiguousTarget as e:
                return {"op": op, "found": False, "ambiguous": True, "reason": str(e)}
            if pr is None:
                return {"op": op, "found": False,
                        "reason": f"{target!r} is not a live session and not a known durable id — "
                                  f"directory(facet='principals') lists who exists."}
            row = {k: v for k, v in pr.items() if k != "reg"}
            if pr.get("reg") is not None:
                try:
                    row["principal_kind"] = _principals.resolve_kind(pr["reg"])
                except Exception as e:  # noqa: BLE001 — kind is enrichment, never blocks the resolve
                    row["principal_kind"] = {"kind": "ambiguous", "error": str(e)}
            if pr.get("uuid") and reg_fn is not None:
                try:
                    row["record"] = reg_fn(pr["uuid"])
                except Exception:
                    row["record"] = None            # live-but-uncatalogued is honest
            return {"op": op, "found": True, **row}

        if op == "roster":
            live_by_handle = {}
            try:
                for r in _identity.presence_all():
                    if r.get("handle"):
                        live_by_handle[r["handle"]] = {"state": r.get("state"),
                                                       "transports": r.get("transports"),
                                                       "reachable": r.get("reachable"),
                                                       "uuid": r.get("uuid")}
            except Exception:  # noqa: BLE001 — the probe failing must not hide the registry
                pass
            rows = []
            for p in _principals.list_principals():
                rows.append({**p, "live": live_by_handle.get(p.get("handle"))})
            return {"op": op, "total": len(rows), "principals": rows}

        if op == "whoami":
            from runtime.session_scan import (AmbiguousSelfError, resolve_own_session,
                                              resolve_self_member)
            out = {"op": op}
            try:
                own = resolve_own_session()
                out.update({"session_id": own.get("session_id"),
                            "address": f"session://{own.get('session_id')}",
                            "how": own.get("how"), "cwd": own.get("cwd")})
            except AmbiguousSelfError as e:
                out.update({"ambiguous": True, "teaching": str(e)})
            except Exception as e:  # noqa: BLE001
                out.update({"error": f"{type(e).__name__}: {e}"})
            try:
                member = resolve_self_member()
                if member:
                    out["member"] = {"handle": member.get("handle"), "name": member.get("name"),
                                     "description": member.get("description")}
            except Exception:  # noqa: BLE001
                pass
            return out

        raise ValueError(f"principal: unknown op {op!r} — one of {READ_OPS}.")

    @mcp.tool(annotations=_to_sdk_annotations(
        CompanyToolAnnotations(readonly=False, destructive=False, idempotent=True),
        "Fabric principal — self-description (write)"))
    def principal_act(op: Literal["describe", "register"], name: str = "",
                      description: str = "") -> dict:
        """The identity WRITE twin. Pick `op`:

          op="describe" — set YOUR OWN name/description on the fabric (idempotent per session; keeps
                an existing live port; how the roster/directory recognise you). An .mjs session's
                announce/profile tools keep working — same reg, same file.
          op="register" — a durable ROLE-NAME with a surviving pull-inbox lives in the EXTERNAL
                substrate; this op TEACHES the path rather than faking a fold (the cross-repo join
                does not exist yet — by design, not omission)."""
        if op == "describe":
            if not (name.strip() or description.strip()):
                raise ValueError("principal_act(op='describe') needs `name` and/or `description` — "
                                 "how the roster recognises you.")
            from runtime import cc_channels as cc
            reg = cc.register_self(name=name.strip(), description=description.strip())
            return {"op": op, "handle": reg.get("handle"), "session_id": reg.get("session_id"),
                    "name": reg.get("name"), "description": reg.get("description"),
                    "transport": reg.get("transport")}
        if op == "register":
            return {"op": op, "ok": False,
                    "teaching": "A durable role-name + surviving inbox is the substrate's "
                                "agent_register (mcp__supabase_admin_mcp__agent_register) — a separate "
                                "server + Postgres with NO join to session identity yet. Register "
                                "there; read pending allocations fail-soft via mailbox(agent_id=…). "
                                "Folding it into this door needs the cross-repo seam designed first "
                                "(design v2 board://item-de33cdf8 §II.1)."}
        raise ValueError(f"principal_act: unknown op {op!r} — one of {WRITE_OPS}.")
