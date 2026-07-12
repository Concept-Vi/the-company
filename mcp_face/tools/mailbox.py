"""mcp_face/tools/mailbox.py — the ONE "what's waiting for me" read (design v2 door: MAILBOX).

THE THREE INBOX NOUNS, named distinctly at last (the review's naming ruling): this door is the FABRIC
MAILBOX (messages waiting for a session); the operator's `inbox()` stays the chief-of-staff TRIAGE
LANES; `decisions()` stays the pending DECISION CARDS. This tool does not touch either.

One call, three sections — the local leaves MERGED-IN-VIEW (each keeps its own honest cursor; two
independent seq spaces are never faked into one number), the external substrate FEDERATED fail-soft:

  mail          — the durable session mailbox (agent_sessions/mail.jsonl): FIFO oldest-first past
                  `since` (mail seq), bodies resolved, CLIENT-HELD cursor (`next_since`) — re-reading
                  the same cursor is always safe, nothing is marked/consumed server-side.
  channel_mail  — the live-transport log (.data/channels/_mail.jsonl) addressed to ANY of this
                  session's handles (current + prior churns, joined by the reg files' session_id):
                  its own line-index cursor `chan_since` → `next_chan_since`.
  allocations   — FEDERATED (the agent_mcp substrate lives in a SEPARATE server + Postgres): read
                  best-effort with a tight timeout when `agent_id` is given. Unreachable → an honest
                  {"unreachable": reason} — the local sections above are NEVER blocked by the external
                  store being down (the review's hard-dependency risk, answered). READ-ONLY: this
                  never marks picked_up — draining stays my_allocations' own act.

PURE READ, posture="safe" (the session mailbox read was already client-tier). File-drop tool.
"""
from __future__ import annotations

import os
import re
import subprocess

from contracts.tools import ToolAnnotations as CompanyToolAnnotations
from mcp.types import ToolAnnotations as SDKToolAnnotations

_AGENT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$")   # the substrate's own grammar


def _to_sdk_annotations(ann: CompanyToolAnnotations, title: str,
                        posture: str = "") -> SDKToolAnnotations:
    extra = {"posture": posture} if posture else {}
    return SDKToolAnnotations(
        title=title, readOnlyHint=ann.readonly, destructiveHint=ann.destructive,
        idempotentHint=ann.idempotent, openWorldHint=False, **extra)


def _handles_of(sid: str) -> set:
    """Every .mjs handle this session has registered under (current + prior churns still on disk) —
    the join is the reg files' session_id (P0.1 captures it at birth now). Non-destructive read."""
    from runtime import cc_channels as cc
    out = set()
    try:
        for fn in os.listdir(cc.CHAN_DIR):
            if not fn.endswith(".json") or fn.startswith("_"):
                continue
            reg = cc._read_reg(os.path.join(cc.CHAN_DIR, fn))
            if reg and reg.get("session_id") == sid and reg.get("handle"):
                out.add(reg["handle"])
    except OSError:
        pass
    return out


def _allocations_readonly(agent_id: str, timeout: float = 4.0) -> dict:
    """FEDERATED, FAIL-SOFT, READ-ONLY view of pending agent_mcp allocations for `agent_id`. Any
    failure (docker down, container absent, psql error, timeout) → {"unreachable": reason} — never an
    exception, never blocks the local mail. Never marks picked_up (read ≠ drain)."""
    if not _AGENT_ID_RE.match(agent_id):
        return {"unreachable": f"invalid agent_id {agent_id!r} — must match the substrate grammar "
                               f"[A-Za-z0-9][A-Za-z0-9._/-]{{0,127}} (refused, not queried)."}
    try:
        ps = subprocess.run(["docker", "ps", "--filter", "name=supabase_db",
                             "--format", "{{.Names}}"],
                            capture_output=True, text=True, timeout=timeout)
        container = (ps.stdout.strip().splitlines() or [""])[0]
        if not container:
            return {"unreachable": "no supabase_db container running (the agent_mcp substrate is down "
                                   "or not on this machine) — local mail above is unaffected."}
        sql = ("select id, kind, ref, note, status, created_by, created_at "
               "from agent_mcp.allocations "
               f"where to_agent = '{agent_id}' and status <> 'done' order by created_at")
        r = subprocess.run(["docker", "exec", "-i", container, "psql", "-U", "postgres",
                            "-d", "postgres", "-tA", "-F", "\t", "-c", sql],
                           capture_output=True, text=True, timeout=timeout)
        if r.returncode != 0:
            return {"unreachable": f"psql read failed: {(r.stderr or '').strip()[:200]}"}
        rows = []
        for line in r.stdout.strip().splitlines():
            parts = line.split("\t")
            if len(parts) >= 7:
                rows.append({"id": parts[0], "kind": parts[1], "ref": parts[2] or None,
                             "note": parts[3], "status": parts[4], "created_by": parts[5] or None,
                             "created_at": parts[6]})
        return {"agent_id": agent_id, "pending": rows, "total": len(rows),
                "note": "READ-ONLY view — nothing marked picked_up; drain via "
                        "supabase_admin_mcp my_allocations."}
    except (subprocess.TimeoutExpired, OSError) as e:
        return {"unreachable": f"{type(e).__name__}: {e} — local mail above is unaffected."}


def register(mcp, suite):
    @mcp.tool(annotations=_to_sdk_annotations(
        CompanyToolAnnotations(readonly=True, destructive=False, idempotent=True),
        "Fabric mailbox — what's waiting for me (read)", posture="safe"))
    def mailbox(session: str, since: int = -1, chan_since: int = -1, thread: str = "",
                verb: str = "", limit: int = 50, agent_id: str = "") -> dict:
        """Everything WAITING for a session, one call: the durable mailbox (queued messages, FIFO past
        `since`, client-held cursor — nothing consumed server-side) + the live-transport mail addressed
        to any of its handles (past `chan_since`) + (when `agent_id` is given) a fail-soft READ-ONLY
        view of its pending substrate allocations. `session` = the durable id (session://<uuid> or
        bare). Filters: `thread`/`verb` (mail section). This is the FABRIC mailbox — the operator's
        `inbox()` (triage lanes) and `decisions()` (decision cards) are different nouns, untouched."""
        from runtime import cc_channels as cc
        sid = (session or "").strip()
        if sid.startswith("session://"):
            sid = sid[len("session://"):]
        if not sid:
            raise ValueError("mailbox: `session` is required — the durable session id "
                             "(session://<uuid> or bare uuid).")

        # 1 — the durable session mailbox (same leaf + semantics as sessions(op='inbox'))
        recs = suite.store.agent_mail_since(since, to=f"session://{sid}",
                                            verb=verb or None, thread=thread or None, limit=limit)
        mail_rows = []
        for r in recs:
            body = None
            try:
                body = suite.store.get_content(r["cas"]) if r.get("cas") else r.get("text")
            except Exception:  # noqa: BLE001 — a missing blob never breaks the inbox read
                body = f"(unresolvable cas {r.get('cas')})"
            mail_rows.append({"seq": r.get("seq"), "from": r.get("from"), "verb": r.get("verb"),
                              "delivered": r.get("delivered"), "transport": r.get("transport"),
                              "thread": r.get("thread"), "channel": r.get("channel"),
                              "ts": r.get("ts"), "message": body})
        next_since = mail_rows[-1]["seq"] if mail_rows else since

        # 2 — the live-transport mail, across every handle this session has worn
        handles = _handles_of(sid)
        chan = cc.mail_since(chan_since, to_any=handles, limit=limit) if handles else \
            {"rows": [], "next_idx": chan_since}

        # 3 — federated allocations (only when asked; fail-soft; read-only)
        allocations = _allocations_readonly(agent_id) if agent_id else None

        return {"session": f"session://{sid}",
                "mail": {"rows": mail_rows, "next_since": next_since,
                         "consumption": "client-held cursor — pass next_since back; nothing is "
                                        "marked/consumed server-side; delivered:true rows are audit "
                                        "copies of messages that already landed live"},
                "channel_mail": {"handles": sorted(handles), "rows": chan["rows"],
                                 "next_chan_since": chan["next_idx"]},
                "allocations": allocations}
