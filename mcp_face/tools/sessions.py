"""mcp_face/tools/sessions.py — the SESSION FABRIC's agent face (Session Fabric §C; F1.3).

Sessions message sessions. TWO tools, per the standing MCP law (MCP-DESIGN-PRINCIPLE.md) + the
marks/mark CQRS precedent:

    sessions(op=list|inbox|watch|describe, …)   → the ONE consolidated READ (pure — no writes, ever)
    session_post(to, message, verb=, copies=)   → the ONE consequential WRITE (a mailbox append)

A new need is a new `op`, never a new flat tool.

THE FLOOR (synthesis §6.3 — the law that keeps WAKE/CONSULT on the right side): NOTHING here spawns
`claude -p`, resumes a session, or touches resolve/approve/dispatch. `session_post` only APPENDS AN
INTENT RECORD to the mailbox leaf (`agent_sessions/mail.jsonl` — a store append, telemetry/registry-
filling class); the SUPERVISOR SERVICE (runtime/session_supervisor.py — operator-sanctioned, its own
permission posture) is the only thing that acts on deliver/wake/consult intents, and the only writer
of `agent_sessions.*` events (single-writer law, criteria audit C6). This face also emits NO fabric
events — it writes mail, reads folds.

THE VERBS ARE ROUTING DECISIONS, NOT MECHANISMS (guide prime principle 2) — all of them reduce to
"look up the target in the registry → pick the path its state allows":
    DELIVER → an inject intent (the supervisor writes into a supervised-live session's stdin stream)
    WAKE    → a spawn intent on a non-live session (`claude -p --resume <id>` — becomes supervised-live)
    CONSULT → fork intents (`--fork-session`, T4-verified: N concurrent forks, original byte-identical)
    queue   → no supervisor involved: the target session PULLS it via sessions(op=inbox) at its next turn
`verb=auto` routes by live registry state (supervised-live→deliver · closed→wake · otherwise→queue;
unknown-state is NOT deliverable — guide §B liveness rule).

SEAMS (verified in-tree 2026-06-11, the registry lane §B):
    suite.list_agent_sessions(state=, cwd=, q=, since=, limit=)  → {sessions, total, fold_errors}
    suite.get_agent_session(sid)                                  → joined row+record (raises on unknown)
    suite.AGENT_SESSION_STATES / suite.AGENT_SESSION_OPS          → the closed vocabularies
    suite.store.append_agent_mail / agent_mail_since              → the mailbox leaf (this lane, §C)
If the registry seam is absent in a running Suite (a partial deploy), ops that need it raise a
TEACHING error naming the missing lane — never a silent empty.

ANNOTATIONS — the first honest instance (F10.1 ledger seed, audit N3): these registrations wire the
REAL `contracts.ToolAnnotations` model (readonly/destructive/idempotent, readonly∧destructive refused
at construction) through to the SDK's ToolAnnotations hints, making mcp_face/AGENTS.md:16's claim true
at the face layer for the fabric's tools.

NAMING (criteria ruling N2): tool `sessions` · store dir `agent_sessions/` · events `agent_sessions.*`.
NOT `fabric` (the model fabric), NOT the review-session store. The operator's decision `inbox` tool is
a DIFFERENT noun (Tim's triage lanes) — this module's `op="inbox"` is the session MAILBOX.
"""
from typing import Literal
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from contracts.tools import ToolAnnotations as CompanyToolAnnotations   # the honest contracts model
from mcp.types import ToolAnnotations as SDKToolAnnotations             # the SDK's hint carrier

_VERBS = ("auto", "deliver", "wake", "consult")
# EXPORTED closed op set — the contract corpus's machine inventory for this consolidated tool
# (CONTRACT-FORMAT §9.2: every consolidated MCP tool module exports OPS; extract_reality.py
# fails loud on a tool module without one). tests/supervisor_routes_acceptance.py is the teeth.
OPS = ("list", "inbox", "watch", "describe", "search")


def _fabric_concurrency() -> int:
    """The fabric concurrency cap — CONSULT copies ≤ this (criteria audit C9; refuse-loud above it).
    Call-time env read (the implement.py permission_mode precedent) so a deliberately-set
    COMPANY_FABRIC_CONCURRENCY is honoured without a restart. The literal 3 mirrors implement.py:43's
    CONCURRENCY_CAP. FLAGGED HARDCODING (registry-is-truth): the registry-served default (a supervisor
    services-row config) is the supervisor lane's seam — when it lands, this default reads from it and
    the env stays the override."""
    return int(os.environ.get("COMPANY_FABRIC_CONCURRENCY", "3"))


def _to_sdk_annotations(ann: CompanyToolAnnotations, title: str) -> SDKToolAnnotations:
    """contracts.ToolAnnotations → SDK hints (the F10.1 wiring — first honest instance). The contracts
    model's own gate (readonly∧destructive raises) bites BEFORE registration, so an incoherent
    annotation can never reach a client."""
    return SDKToolAnnotations(
        title=title, readOnlyHint=ann.readonly, destructiveHint=ann.destructive,
        idempotentHint=ann.idempotent, openWorldHint=False)


def _sid(ref: str, param: str) -> str:
    """Normalize a session reference (bare uuid OR session://<uuid>) to the bare id. Teaching on empty."""
    if not isinstance(ref, str) or not ref.strip():
        raise ValueError(
            f"`{param}` must be a session reference — a Claude session id (uuid) or its address form "
            f"session://<id>. sessions(op='list') shows the registry (ids, names, titles, states).")
    ref = ref.strip()
    return ref[len("session://"):] if ref.startswith("session://") else ref


def _addr(sid: str) -> str:
    return f"session://{sid}"


def _registry_guard(suite, what: str):
    """Fail TEACHING-loud if the registry fold (guide §B lane) is absent from this Suite build —
    never an AttributeError posing as an internal bug, never a fabricated empty registry."""
    if not callable(getattr(suite, what, None)):
        raise ValueError(
            f"the session registry fold (Suite.{what} — Session Fabric guide §B) is not present in "
            f"this running Suite. The mailbox ops still work: sessions(op='inbox') reads your mail, "
            f"sessions(op='watch') polls fabric events. Registry-backed ops (list/describe/auto-"
            f"routing) need the §B lane loaded — restart the MCP server against current main.")


def register(mcp, suite):
    # ── the consolidated READ ─────────────────────────────────────────────────────────────────────
    @mcp.tool(annotations=_to_sdk_annotations(
        CompanyToolAnnotations(readonly=True, destructive=False, idempotent=True),
        "Session fabric — read (registry · mailbox · live events)"))
    def sessions(op: Literal["list", "inbox", "watch", "describe", "search"], session: str = "",
                 q: str = "", state: str = "", cwd: str = "", since: int = -1,
                 thread: str = "", verb: str = "", limit: int = 50,
                 detail: str = "concise", mode: str = "auto") -> dict:
        """READ the agent-session fabric — every Claude Code session this machine has run (the
        backfilled catalog + live ones), their mailboxes, and the live fabric events. PURE READ
        (CQRS): posting a message is the separate `session_post` tool. Pick `op`:

          op="list"     — the FLEET: every registered session {id, name, cwd, state, title,
                           last_activity}, newest-activity first. Filters: `state`
                           (supervised-live = supervisor-owned, DELIVER reaches it ·
                           unsupervised-live = alive but pull-only · closed = wake-able),
                           `cwd` (exact), `q` (substring over title/name/id), `since` (event-seq
                           cursor), `limit`.
          op="describe" — ONE session in full (`session` required): its registry row + durable
                           record (cwd, title, envelope) + its mail traffic summary (inbound/
                           outbound counts, latest thread activity).
          op="inbox"    — `session`'s MAILBOX (required): messages addressed to it, OLDEST-first,
                           with bodies resolved to text. `since` = your consumption cursor (mail
                           seq, NOT event seq; -1 = everything); the result's `next_since` is what
                           you pass next call — consumption is CLIENT-HELD here (the SSE
                           Last-Event-ID pattern; this read never moves any cursor). Filters:
                           `thread` (one conversation, e.g. a consult fan's replies), `verb`,
                           `limit` (FIFO — pagination never skips). NOTE: deliver/wake/consult
                           records addressed to you are the SUPERVISOR's to act on (push); records
                           with verb="queue" are yours to pick up by reading this.
          op="watch"    — the live fabric trajectory: `agent_sessions.*` events (registered ·
                           spawned · turn · idle · closed · adopted) after event-seq `since`,
                           optionally for one `session`. Poll-shaped (this face is stdio; the
                           streaming twin is the bridge's SSE). THE WRITE-PROOF DISCIPLINE: after a
                           session_post, completion = the declared consequence events appearing
                           here after your posted seq — never "the response looked ok".
          op="search"   — CONTENT search over every session's TRANSCRIPT (the claude-sessions
                           corpus index) — the merged-search twin of op="list"'s q (which only
                           filters title/name/id). Each result is a LIVE HANDLE: {session_id,
                           session_address, state (joined LIVE at query time), cwd, title,
                           point (matched turn/speaker/anchor), snippet, primary_verb (what
                           verb='auto' would do NOW), commands (the exact session_post forms)}.
                           `q` (required) = the content query · `mode` = "auto" (default) |
                           "semantic" (embedding search; needs the embed-pplx service — fails
                           TEACHING-loud when down) | "lexical" (term search, zero models, always
                           on; auto picks semantic when available and DECLARES mode_used) ·
                           `state` pre-filters on live state · `limit` = max sessions. The chain:
                           search → pick a handle → session_post (the write twin) → verify via
                           op="watch"/op="inbox". One result per session, best chunk leads.

        `detail`: "concise" (default, high-signal fields) | "detailed" (full records). An empty
        result is HONEST (no sessions / no mail / no events — never fabricated). The operator's
        `inbox` tool is a DIFFERENT thing (Tim's decision-triage lanes); this op="inbox" is the
        session-to-session mailbox."""
        if op not in OPS:
            raise ValueError(
                f"sessions: unknown op={op!r}. Valid: {list(OPS)} — list=the fleet · "
                f"inbox=a session's mail (needs `session`) · watch=live fabric events · "
                f"describe=one session in full (needs `session`) · search=content search over "
                f"transcripts, results are live handles (needs `q`). To SEND, use session_post (CQRS).")
        if detail not in ("concise", "detailed"):
            raise ValueError(f"sessions: detail must be 'concise' or 'detailed', got {detail!r}.")

        if op == "search":
            # R4.2/R4.5 — the search→handle join (runtime/session_search.py): corpus hit ⨝ live
            # registry row + point + commands. Pure read (the floor — acting is session_post's).
            _registry_guard(suite, "get_agent_session")
            if not q.strip():
                raise ValueError(
                    "sessions(op='search') needs `q` — the CONTENT query over the transcripts "
                    "(meaning for mode='semantic', terms for mode='lexical'). To filter the fleet "
                    "by title/name/id instead, use sessions(op='list', q=…).")
            from runtime import session_search
            return {"op": op, **session_search.search_sessions(
                suite, q=q.strip(), k=limit, mode=mode, state=state or None, detail=detail)}

        if op == "list":
            _registry_guard(suite, "list_agent_sessions")
            res = suite.list_agent_sessions(state=state or None, cwd=cwd or None,
                                            q=q or None, since=since, limit=limit)
            rows = res["sessions"]
            if detail == "concise":
                rows = [{"id": r.get("id"), "name": r.get("name"), "state": r.get("state"),
                         "title": r.get("title"), "cwd": r.get("cwd"),
                         "last_activity": r.get("last_activity")} for r in rows]
            return {"op": op, "total": res["total"], "fold_errors": res["fold_errors"],
                    "detail": detail, "sessions": rows}

        if op == "describe":
            _registry_guard(suite, "get_agent_session")
            sid = _sid(session, "session")
            row = suite.get_agent_session(sid)              # raises its own teaching error on unknown
            inbound = suite.store.agent_mail_since(-1, to=_addr(sid))
            outbound = [r for r in suite.store.agent_mail_since(-1) if r.get("from") == _addr(sid)]
            mail = {"inbound": len(inbound), "outbound": len(outbound),
                    "latest": [{"id": r.get("id"), "from": r.get("from"), "verb": r.get("verb"),
                                "thread": r.get("thread"), "ts": r.get("ts")} for r in inbound[-5:]]}
            if detail == "concise":
                row = {k: row.get(k) for k in ("id", "name", "state", "title", "title_source",
                                               "cwd", "started", "last_activity")}
            return {"op": op, "session": _addr(sid), "record": row, "mail": mail, "detail": detail,
                    "next": "sessions(op='inbox', session=…) reads the mail bodies; "
                            "session_post sends to it."}

        if op == "inbox":
            sid = _sid(session, "session")
            rows = suite.store.agent_mail_since(since, to=_addr(sid),
                                                verb=verb or None, thread=thread or None,
                                                limit=limit)
            next_since = rows[-1]["seq"] if rows else since
            out = []
            for r in rows:
                body = suite.store.get_content(r["cas"])    # bodies always ride cas:// (fail-loud if torn)
                if detail == "concise":
                    out.append({"id": r.get("id"), "seq": r.get("seq"), "from": r.get("from"),
                                "verb": r.get("verb"), "thread": r.get("thread"),
                                "ts": r.get("ts"), "message": body})
                else:
                    out.append({**r, "message": body})
            return {"op": op, "session": _addr(sid), "total": len(out), "since": since,
                    "next_since": next_since, "detail": detail, "messages": out,
                    "consumption": "client-held cursor — pass since=next_since on your next read; "
                                   "re-reading is safe (this never consumes destructively)."}

        if op == "watch":
            if not hasattr(suite, "AGENT_SESSION_OPS"):
                raise ValueError(
                    "the fabric event vocabulary (Suite.AGENT_SESSION_OPS — Session Fabric guide §B) "
                    "is not present in this running Suite; op='watch' needs it. op='inbox' still "
                    "reads mail. Restart the MCP server against current main.")
            kinds = tuple(suite.AGENT_SESSION_OPS)
            sid = _sid(session, "session") if (session or "").strip() else None
            scanned = suite.store.events_since(since)
            matching = [e for e in scanned if e.get("kind") in kinds
                        and (sid is None or e.get("session") == sid)]
            if len(matching) > limit:                       # paginate WITHOUT skipping: cursor = last returned
                matching = matching[:limit]
                next_since = matching[-1].get("seq", since)
            else:                                           # consumed the whole tail: cursor = log tail
                next_since = scanned[-1].get("seq", since) if scanned else since
            if detail == "concise":
                matching = [{"kind": e.get("kind"), "session": e.get("session"),
                             "state": e.get("state"), "seq": e.get("seq"), "ts": e.get("ts"),
                             "summary": e.get("summary")} for e in matching]
            return {"op": op, "session": _addr(sid) if sid else None, "total": len(matching),
                    "since": since, "next_since": next_since, "detail": detail,
                    "events": matching,
                    "note": "agent_sessions.* events are emitted ONLY by the supervisor service "
                            "(single-writer law) — an empty result with the supervisor down is "
                            "honest silence, not absence of sessions (op='list' shows those)."}

    # ── the consequential WRITE ───────────────────────────────────────────────────────────────────
    @mcp.tool(annotations=_to_sdk_annotations(
        CompanyToolAnnotations(readonly=False, destructive=False, idempotent=False),
        "Session fabric — post a message/intent to a session"))
    def session_post(to: str, message: str, verb: Literal["auto", "deliver", "wake", "consult"] = "auto",
                     copies: int = 1, from_session: str = "", thread: str = "") -> dict:
        """SEND a message to another Claude Code session (the fabric's one WRITE — CQRS twin of the
        `sessions` read tool). This NEVER spawns or touches a session directly: it appends a durable
        INTENT to the mailbox; the supervisor service acts on it (the floor — this face cannot launch
        processes). Routing verbs (decisions, not mechanisms):

          verb="auto"    (default) — routed by the target's live registry state:
                          supervised-live → deliver · closed → wake · anything else → queue
                          (unknown/unsupervised is NOT deliverable — it gets next-turn pickup).
          verb="deliver" — inject into a SUPERVISED-LIVE session's conversation (push). To an
                          unsupervised-live target this becomes next-turn pickup (still delivery);
                          to a CLOSED target it is REFUSED (nothing to inject into — wake or consult).
          verb="wake"    — re-spawn a CLOSED session (`--resume`, context intact) and hand it the
                          message; it becomes supervised-live. Refused on live targets (a second
                          writer on a live session silently BRANCHES it — T1).
          verb="consult" — ask a FORKED COPY (`--fork-session`): the original is NEVER touched
                          (T4-verified byte-identical), works on live or closed targets, and fans:
                          `copies=N` forks N parallel consultants (N ≤ COMPANY_FABRIC_CONCURRENCY),
                          replies aggregating under one thread id.

        `to`: the target (session id or session://<id> — sessions(op='list') shows the fleet).
        `from_session`: REQUIRED — your reply path. Pass YOUR session id (session://<id>) so answers
        can route back; a stable label is accepted but is not reply-addressable. `thread`: join an
        existing conversation (a prior post's thread id); omitted → a fresh thread is minted.

        Returns {posted, seq, verb, routed, thread, …}. VERIFY consequences, don't assume: replies
        land in sessions(op='inbox', session=<your from_session>, thread=<thread>); supervisor
        actions show as sessions(op='watch') events after your posted seq."""
        sid = _sid(to, "to")
        if not isinstance(message, str) or not message.strip():
            raise ValueError(
                "session_post: `message` is empty — nothing to send. The message is the body the "
                "target reads (it rides the cas:// store; size is not a constraint).")
        if not isinstance(from_session, str) or not from_session.strip():
            raise ValueError(
                "session_post: `from_session` is required — it is the REPLY PATH. Pass your own "
                "session id (session://<your-id>) so the target's answer can route back to your "
                "inbox; a stable label (e.g. 'lead') is accepted but not reply-addressable.")
        if verb not in _VERBS:
            raise ValueError(
                f"session_post: unknown verb={verb!r}. Valid: {list(_VERBS)} — auto routes by the "
                f"target's registry state; deliver=inject (live), wake=re-spawn (closed), "
                f"consult=ask a forked copy (never touches the original, may fan via copies=).")
        cap = _fabric_concurrency()
        if not isinstance(copies, int) or isinstance(copies, bool) or copies < 1:
            raise ValueError(f"session_post: copies must be an int ≥ 1, got {copies!r}.")
        if copies > 1 and verb != "consult":
            raise ValueError(
                f"session_post: copies={copies} only makes sense with verb='consult' (N forked "
                f"consultants on one question). deliver/wake/auto address ONE session — send one.")
        if copies > cap:
            raise ValueError(
                f"session_post: copies={copies} exceeds the fabric concurrency cap ({cap}) — "
                f"refused loud (criteria C9), never silently truncated. The cap is "
                f"COMPANY_FABRIC_CONCURRENCY (env-tunable); fan wider in waves, or raise the cap "
                f"deliberately.")

        # ── the router (guide §C pseudocode): look up the target, pick the path its state allows ──
        _registry_guard(suite, "get_agent_session")
        row = suite.get_agent_session(sid)     # raises the registry's own teaching error on unknown
        state = row.get("state")
        if verb == "auto":
            if state == "supervised-live":
                resolved = "deliver"
            elif state == "closed":
                resolved = "wake"
            else:                               # unsupervised-live / unknown — NOT deliverable (§B)
                resolved = "queue"
        elif verb == "deliver":
            if state == "closed":
                raise ValueError(
                    f"session_post: {_addr(sid)} is CLOSED — there is no live conversation to "
                    f"deliver into. Use verb='wake' (re-spawns it via --resume, context intact, "
                    f"then hands it your message) or verb='consult' (asks a forked copy without "
                    f"reviving the original).")
            resolved = "deliver" if state == "supervised-live" else "queue"
        elif verb == "wake":
            if state == "supervised-live":
                raise ValueError(
                    f"session_post: {_addr(sid)} is already SUPERVISED-LIVE — waking it would "
                    f"double-spawn. Use verb='deliver' (injects into the live conversation).")
            if state != "closed":
                raise ValueError(
                    f"session_post: {_addr(sid)} is {state or 'of unknown liveness'} — waking a "
                    f"possibly-live session adds a SECOND WRITER, which silently BRANCHES the "
                    f"conversation (T1). Wait for it to quiesce to 'closed', post with "
                    f"verb='auto' (queues for its next turn), or verb='consult' a forked copy.")
            resolved = "wake"
        else:                                   # consult — live or closed, never the original (T4)
            resolved = "consult"

        cas = suite.store.put_content(message)
        rec = {"to": _addr(sid), "from": from_session.strip(), "verb": resolved,
               "requested_verb": verb, "cas": cas, "copies": copies,
               "state_at_post": state, "source": "mcp_face.session_post"}
        if thread.strip():
            rec["thread"] = thread.strip()
        out = suite.store.append_agent_mail(rec)

        routed, what_happens = {
            "deliver": ("supervisor-inject",
                        "the supervisor pops this intent and injects it into the live conversation; "
                        "watch for agent_sessions.turn on the target after this seq"),
            "wake": ("supervisor-wake",
                     "the supervisor pops this intent, re-spawns the session (--resume) and hands it "
                     "your message; watch for agent_sessions.spawned then .turn"),
            "consult": ("supervisor-fork",
                        f"the supervisor forks {copies} cop{'ies' if copies > 1 else 'y'} "
                        f"(--fork-session, original untouched); replies aggregate under this thread"),
            "queue": ("next-turn-pickup",
                      "no supervisor involved: the target reads it via sessions(op='inbox') at its "
                      "next turn (pull)"),
        }[resolved]
        return {"posted": out["id"], "seq": out["seq"], "to": out["to"], "verb": resolved,
                "requested_verb": verb, "state_at_post": state, "copies": copies,
                "thread": out["thread"], "routed": routed,
                "what_happens": what_happens,
                "replies": f"sessions(op='inbox', session='{from_session.strip()}', "
                           f"thread='{out['thread']}')"}

    return sessions, session_post
