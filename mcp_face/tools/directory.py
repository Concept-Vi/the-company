"""mcp_face/tools/directory.py — the ONE faceted "who/what exists" read (design v2 door: DIRECTORY).

Replaces four partial, differently-shaped list surfaces with one door (they keep working — adapters,
no flag-day): sessions(op=list) [the durable registry] · cc_channel(op=list) [live .mjs presence] ·
cc_clone(op=list) [the clone fleet — previously structurally INVISIBLE to every general list] ·
channels(op=list) [the rooms]. Two facets, two honest row shapes (the boundary review's ruling —
actors and rooms are different nouns, never forced into one row):

  facet="principals" — ACTORS (sessions + clones), one row shape:
      {address, uuid, kind: session|clone, name, state, transports, reachable, handle, cwd,
       description, title, last_activity, at?, source_sid?}
    The durable registry (filters + summarizer-exclusion + fold_errors PRESERVED) enriched with live
    presence (transports/reachable/handle by probe), plus live-only rows the registry doesn't know,
    plus CLONES as kind=clone actors (the hidden-fleet fix) carrying their provenance address
    (clone://<source_sid>/<at>) — but NOT their filesystem paths (materialized/source paths stay on
    the operator-only cc_clone detail; existence+state here matches what sessions(list) already
    exposes at posture=safe).
  facet="channels" — ROOMS, their own shape (id, kind, name, purpose, mode, coordinator, status,
    member_count, posts, created, last_activity). `state` filters status; `q` substring.

Params: q (substring) · state · cwd (principals) · since (registry seq cursor, principals) ·
limit · include_summarizers (default False — the human lane; ~77% of the catalog is CC-internal
summarizer one-shots) · live_only (principals: only the probed-live fleet + live clones) ·
detail ("concise"|"full"). PURE READ, posture="safe" (both source lists were already client-tier).
File-drop tool (pkgutil auto-register).
"""
from __future__ import annotations

from typing import Literal

from contracts.tools import ToolAnnotations as CompanyToolAnnotations
from mcp.types import ToolAnnotations as SDKToolAnnotations

FACETS = ("principals", "channels")


def _to_sdk_annotations(ann: CompanyToolAnnotations, title: str,
                        posture: str = "") -> SDKToolAnnotations:
    extra = {"posture": posture} if posture else {}
    return SDKToolAnnotations(
        title=title, readOnlyHint=ann.readonly, destructiveHint=ann.destructive,
        idempotentHint=ann.idempotent, openWorldHint=False, **extra)


def _actor_row(*, address=None, uuid=None, kind="session", name=None, state=None,
               transports=None, reachable=None, handle=None, cwd=None, description=None,
               title=None, last_activity=None, **extra) -> dict:
    row = {"address": address or (f"session://{uuid}" if uuid else None), "uuid": uuid,
           "kind": kind, "name": name, "state": state, "transports": transports or [],
           "reachable": bool(reachable), "handle": handle, "cwd": cwd,
           "description": description, "title": title, "last_activity": last_activity}
    row.update(extra)
    return row


def register(mcp, suite):
    @mcp.tool(annotations=_to_sdk_annotations(
        CompanyToolAnnotations(readonly=True, destructive=False, idempotent=True),
        "Fabric directory — who/what exists (read)", posture="safe"))
    def directory(facet: Literal["principals", "channels"], q: str = "", state: str = "",
                  cwd: str = "", since: int = -1, limit: int = 50,
                  include_summarizers: bool = False, live_only: bool = False,
                  detail: str = "concise") -> dict:
        """ONE faceted "who/what exists RIGHT NOW" — the fabric's directory. Pick `facet`:

          facet="principals" — the ACTORS: every session (durable registry + probed-live presence,
                joined) plus the clone fleet as kind=clone rows (previously invisible to every list).
                Each row says who they are (durable address), whether they're reachable and by which
                transport, and where they sit. Filters: q/state/cwd/since/limit;
                include_summarizers=False by default (the human lane); live_only=True for just the
                probed-live fleet.
          facet="channels" — the ROOMS: channels + gatherings with membership counts and activity
                (their own row shape — a room is not an actor). `state` filters status; `q` substring.

        PURE READ (the writes stay on their own doors: send/channel_act/principal registration)."""
        if facet == "principals":
            from runtime import identity as _identity
            fold_errors = 0
            rows_by_key: dict = {}
            order: list = []

            def _put(key, row):
                if key in rows_by_key:
                    # enrich, never duplicate: live/clone facts land on the existing row
                    cur = rows_by_key[key]
                    for k, v in row.items():
                        if v not in (None, [], False) or k == "reachable":
                            if cur.get(k) in (None, [], False) or k in ("transports", "reachable",
                                                                        "handle", "kind", "at",
                                                                        "source_sid", "address"):
                                cur[k] = v
                else:
                    rows_by_key[key] = row
                    order.append(key)

            if not live_only:
                res = suite.list_agent_sessions(state=state or None, cwd=cwd or None,
                                                q=q or None, since=since, limit=limit,
                                                include_summarizers=include_summarizers)
                fold_errors = res.get("fold_errors", 0)
                for r in res["sessions"]:
                    _put(r.get("id"), _actor_row(
                        uuid=r.get("id"), kind="session", name=r.get("name"), state=r.get("state"),
                        cwd=r.get("cwd"), title=r.get("title"), last_activity=r.get("last_activity")))

            # live presence (probe) — enrich registry rows / add live-only rows the registry misses
            for pr in _identity.presence_all():
                key = pr.get("uuid") or f"handle:{pr.get('handle')}"
                if live_only or key in rows_by_key or _match(pr, q, state, cwd):
                    _put(key, _actor_row(
                        uuid=pr.get("uuid"), kind="session", state=pr.get("state"),
                        transports=pr.get("transports"), reachable=pr.get("reachable"),
                        handle=pr.get("handle"), cwd=pr.get("cwd"),
                        description=pr.get("description"),
                        address=(f"session://{pr['uuid']}" if pr.get("uuid") else None)))

            # clones — the hidden fleet, as kind=clone actors (safe fields only: no filesystem paths)
            try:
                from runtime import cc_clone as _cc_clone
                for c in _cc_clone.list_clones(prune=True):
                    key = c.get("session_id") or f"clone:{c.get('handle')}"
                    _put(key, _actor_row(
                        uuid=c.get("session_id"), kind="clone", name=c.get("handle"),
                        state="supervised-live", transports=["supervised"], reachable=True,
                        handle=c.get("handle"), cwd=c.get("cwd"),
                        description=c.get("description"),
                        address=c.get("address") or (
                            f"clone://{c.get('source_sid')}/{c.get('at')}"
                            if c.get("source_sid") else None),
                        at=c.get("at"), source_sid=c.get("source_sid")))
            except Exception:  # noqa: BLE001 — the clone registry absent/unreadable never hides sessions
                pass

            rows = [rows_by_key[k] for k in order][:limit if live_only else None]
            return {"facet": facet, "total": len(rows), "fold_errors": fold_errors,
                    "live_only": live_only, "detail": detail, "principals": rows}

        if facet == "channels":
            from runtime import session_channels as _sc
            out = []
            for cid, row in (_sc.fold_channels(suite.store) or {}).items():
                if state and row.get("status") != state:
                    continue
                if q and q.lower() not in f"{row.get('name','')} {row.get('purpose','')} {cid}".lower():
                    continue
                out.append({"id": cid, "kind": row.get("kind"), "name": row.get("name"),
                            "purpose": row.get("purpose"), "mode": row.get("mode"),
                            "coordinator": row.get("coordinator"), "status": row.get("status"),
                            "member_count": len(row.get("members") or {}),
                            "posts": row.get("posts", 0), "created": row.get("created"),
                            "last_activity": row.get("last_activity")})
            out.sort(key=lambda r: r.get("last_activity") or "", reverse=True)
            return {"facet": facet, "total": len(out), "channels": out[:limit]}

        raise ValueError(f"directory: unknown facet {facet!r} — one of {FACETS}.")


def _match(pr: dict, q: str, state: str, cwd: str) -> bool:
    """Apply the principals filters to a LIVE-ONLY presence row (registry rows are pre-filtered by
    list_agent_sessions; this keeps the two paths consistent)."""
    if state and pr.get("state") != state:
        return False
    if cwd and pr.get("cwd") != cwd:
        return False
    if q:
        hay = f"{pr.get('handle','')} {pr.get('cwd','')} {pr.get('description','')}".lower()
        if q.lower() not in hay:
            return False
    return True
