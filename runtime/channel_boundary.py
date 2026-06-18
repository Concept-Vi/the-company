"""runtime/channel_boundary.py — the company-side PUBLISH/READ boundary for SHARED channels (the external edge).

Tim's frame (2026-06-18, via the lead): the internal channel fabric stays the ONE source of truth and keeps
evolving; SHARED channels are SINGLE-SOURCE on Supabase (so Claude Design + the company sessions sit in the
SAME live channel — no internal mirror). This module is the company's edge onto that shared store:
  • PUBLISH  — a company session's post to a SHARED channel is written DIRECTLY to Supabase channel_posts
               (authenticated as a least-privilege principal, NOT service-role). It is NOT also injected
               locally (single-source: Supabase is the one store; delivery happens via the Realtime sub).
  • INJECT   — an OUTBOUND Realtime subscription receives every new channel_posts row and injects it into the
               live company member-sessions, SKIPPING THE ORIGIN session. BOTH 'session' and 'client' rows
               inject (skip-by-ORIGIN, not by sender_kind) — so company sessions see each other AND see Claude
               Design on a shared channel. (The earlier sender_kind='client'-only filter was a MIRROR-design
               artifact and is WRONG for single-source — it would hide company sessions from each other.)

INTERNAL-only channels are untouched — they stay on the local fabric (cc_channels live-injection). This module
governs ONLY shared channels (an ADDITIVE path); the working coordination fabric is not disturbed.

SECURITY (the lead's rule): authenticate AS a dedicated, RLS-scoped principal (runtime/supabase_principal.py;
the boundary is a company-internal client-registry row, like Claude Design + the factory SA) — NEVER the
service-role master key in this process's env. RLS gates the principal to channel_posts (+ the collab tables).

BUILD STATE (advisor-scoped 2026-06-18): the PUBLISH (write) + the pure INJECT-ROUTING are built + offline-
tested now (locked schema, clear auth). The Realtime SUBSCRIBER TRANSPORT is STUBBED behind a clean interface
— builder owns the Realtime mechanism (postgres_changes vs broadcast-from-DB), the topic, the payload shape,
and the RLS-Realtime auth handshake; wiring the live WS waits on builder posting those (no guessed protocol).
The cc_channels.py HOOK (route a shared-channel post here) waits on the shared-vs-internal DISCRIMINATOR
(which channels are shared = a Tim/lead product call) + builder's live tables. "Done" = the live round-trip
(company writes → Supabase → CD reads; CD writes → Realtime → injected into a live session), verified with
builder's live tables + the CD end — NOT offline green (this boundary is the named gate; offline ≠ works).
"""
from __future__ import annotations

import json
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

from runtime.supabase_principal import SupabasePrincipal

# The least-privilege principal env-prefix (the lead provisions COMPANY_CHANNEL_SA_* + the shared SUPABASE_URL/
# ANON into the boundary env out-of-channel). REST URL is public (gctunhsuwpaxeatwlmuv.supabase.co).
BOUNDARY_PREFIX = "COMPANY_CHANNEL"
_REST_TABLE = "channel_posts"

# the company message fields → channel_posts columns (the locked 0003 map; to_cwd is a box-side routing hint,
# resolved from the live registry by handle, deliberately NOT published).
_POST_REQUIRED = ("channel_id", "from_session", "text")


def build_post_row(channel_id: str, from_session: str, text: str, *, to_session: str | None = None,
                   thread: str | None = None, kind: str = "message", sender_kind: str = "session") -> dict:
    """PURE: the channel_posts row the company publishes for a SHARED-channel post (unit-testable, no backend).
    sender_kind='session' (a company session) — the Edge Function writes 'client' for Claude Design. RAISES on
    a missing required field (channel_id/from_session/text) — never publish an unfindable/unroutable row."""
    row = {"channel_id": channel_id, "from_session": from_session, "to_session": to_session,
           "thread": thread, "text": text, "kind": kind, "sender_kind": sender_kind}
    missing = [k for k in _POST_REQUIRED if not row.get(k)]
    if missing:
        raise ValueError(f"build_post_row: missing required field(s) {missing} — a shared post needs "
                         f"channel_id + from_session + text. Fail loud, never publish an unroutable row.")
    return row


def publish_shared_post(row: dict, *, principal: SupabasePrincipal | None = None, poster=None) -> dict:
    """PUBLISH one shared-channel post to Supabase channel_posts, authenticated as the least-privilege
    principal (Bearer its JWT — NOT service-role). Returns {ok, status, id?, error?}. FAIL-LOUD-WITH-REASON
    (returns ok:False + the reason on any non-2xx / transport error) — the CALLER MUST surface !ok to the
    operator (a Notice) + record a Gap: a SHARED post is single-source on Supabase, so a failed publish means
    the message did NOT send (never a silent drop, the no-silent-failures law). `poster(row)->resp` injects
    the write for offline tests; default does the authenticated PostgREST POST as the principal."""
    if poster is not None:
        return poster(row)
    principal = principal or SupabasePrincipal(BOUNDARY_PREFIX)
    try:
        url = principal.url()
        if not url:
            return {"ok": False, "status": 0, "error": f"{BOUNDARY_PREFIX}: no SUPABASE_URL — cannot publish."}
        endpoint = f"{url.rstrip('/')}/rest/v1/{_REST_TABLE}"
        headers = {**principal.auth_headers(), "Content-Type": "application/json",
                   "Prefer": "return=representation"}
        req = Request(endpoint, data=json.dumps(row).encode("utf-8"), method="POST", headers=headers)
        try:
            with urlopen(req, timeout=10) as r:  # noqa: S310
                status, raw = r.status, r.read().decode("utf-8")
        except HTTPError as e:
            return {"ok": False, "status": e.code, "error": e.read().decode("utf-8", "replace")[:300]}
        except (URLError, TimeoutError) as e:
            return {"ok": False, "status": 0, "error": f"transport: {e}"}
        if status >= 300:
            return {"ok": False, "status": status, "error": raw[:300]}
        out = json.loads(raw or "[]")
        rec = out[0] if isinstance(out, list) and out else (out if isinstance(out, dict) else {})
        return {"ok": True, "status": status, "id": rec.get("id")}
    except Exception as e:  # auth failure etc. — surface, never silently drop a shared post
        return {"ok": False, "status": 0, "error": f"{type(e).__name__}: {e}"}


def route_inject(post_row: dict, member_sessions: list[str]) -> list[str]:
    """PURE: which live company member-sessions a new shared-channel post should be injected into — ALL members
    EXCEPT the ORIGIN (from_session). Skip-by-ORIGIN, NOT by sender_kind: BOTH 'session' (another company
    session) and 'client' (Claude Design) rows inject, so company sessions see each other AND see CD on a
    shared channel. The origin is skipped (it authored the post — never echo to self). Unit-testable.

    THE SINGLE-SOURCE CORRECTNESS RULE (advisor-caught, the mirror→single-source pivot): a 'client' row injects
    to every member; a 'session' row injects to every member but the author. NEVER filter to client-only (that
    would hide company↔company on shared channels). The publish path writes to Supabase and does NOT also inject
    locally — so this Realtime path is the SOLE delivery, no double-deliver."""
    origin = post_row.get("from_session")
    return [s for s in (member_sessions or []) if s and s != origin]


class ChannelInjectSubscriber:
    """The OUTBOUND Realtime subscriber → live-session injector for SHARED channels. The ROUTING (`on_insert`)
    is built + tested now; the WS TRANSPORT (`start`) is STUBBED pending builder's Realtime topic + payload
    shape + the RLS-Realtime auth handshake (no guessed protocol). Wire `members_of` (channel_id → live company
    member-session handles) + `inject` (deliver into a live session — the supervisor /channel-send → cc_channels
    .send path) at construction; the live WS connect lands when builder posts the mechanism."""

    def __init__(self, *, members_of, inject, principal: SupabasePrincipal | None = None):
        self._members_of = members_of       # (channel_id) -> [session handle, ...]
        self._inject = inject               # (session_handle, post_row) -> None (deliver into a live session)
        self._principal = principal

    def on_insert(self, post_row: dict) -> list[str]:
        """Handle one new channel_posts row (called by the Realtime transport per INSERT): route skip-by-origin
        to the channel's live company member-sessions + inject each. Returns the handles injected (for the log).
        BUILT + TESTABLE NOW — the transport feeds it real rows once wired."""
        targets = route_inject(post_row, self._members_of(post_row.get("channel_id")))
        for handle in targets:
            self._inject(handle, post_row)
        return targets

    def start(self):  # pragma: no cover - transport stub
        """STUB — connect the outbound WS to Supabase Realtime + subscribe channel_posts INSERTs, calling
        on_insert per row. NOT IMPLEMENTED until builder posts: the Realtime mechanism (postgres_changes vs
        broadcast-from-DB), the topic, the new_record payload shape, and the Bearer/RLS-Realtime handshake.
        Fail-loud so it is never mistaken for live."""
        raise NotImplementedError(
            "ChannelInjectSubscriber.start: the Realtime WS transport is pending builder's Realtime topic + "
            "payload shape + RLS-Realtime auth handshake (no guessed protocol). on_insert/route_inject are "
            "built + tested; wire start() against builder's posted mechanism, then verify the live round-trip.")


if __name__ == "__main__":
    # OFFLINE self-test — the parts that DON'T need the backend: row construction, publish via injected poster
    # (ok + fail-loud-with-reason), the skip-by-origin BOTH-KINDS routing, the subscriber's on_insert fan-out.
    # NOT a verification of CD participation — that is the LIVE round-trip (builder's tables + the CD end).
    r = build_post_row("design", "ch-8djrpmsl", "hello shared world", thread="t-1", kind="message")
    assert r["sender_kind"] == "session" and r["channel_id"] == "design" and r["to_session"] is None, r
    for bad in (("", "s", "t"), ("c", "", "t"), ("c", "s", "")):
        try:
            build_post_row(*bad); raise SystemExit(f"FAIL: missing-field not raised: {bad}")
        except ValueError:
            pass

    # publish via injected poster — ok path + fail path (the caller surfaces !ok).
    ok = publish_shared_post(r, poster=lambda row: {"ok": True, "status": 201, "id": "uuid-1"})
    assert ok["ok"] and ok["id"] == "uuid-1", ok
    bad = publish_shared_post(r, poster=lambda row: {"ok": False, "status": 401, "error": "RLS denied"})
    assert not bad["ok"] and bad["status"] == 401, bad

    # ★ the single-source routing fix: skip-by-ORIGIN, BOTH kinds inject.
    members = ["ch-8djrpmsl", "ch-ovxwz8k8", "ch-2mnxl9j0"]
    # a 'session' row from ch-8djrpmsl → injects to the OTHER two (not the author)
    sess_row = build_post_row("design", "ch-8djrpmsl", "from a company session")
    assert route_inject(sess_row, members) == ["ch-ovxwz8k8", "ch-2mnxl9j0"], route_inject(sess_row, members)
    # a 'client' (Claude Design) row → injects to ALL company members (CD is not in member_sessions)
    cd_row = build_post_row("design", "claude-design", "from Claude Design", sender_kind="client")
    assert route_inject(cd_row, members) == members, route_inject(cd_row, members)
    # NEVER client-only: a session row is NOT filtered out — company sessions see each other
    assert route_inject(sess_row, members) != [], "single-source: company↔company must inject (not client-only)"

    # subscriber on_insert fan-out via fake inject
    delivered = []
    sub = ChannelInjectSubscriber(members_of=lambda cid: members,
                                  inject=lambda h, row: delivered.append((h, row["text"])))
    injected = sub.on_insert(cd_row)
    assert injected == members and len(delivered) == 3, (injected, delivered)
    # start() is a fail-loud stub (never mistaken for live)
    try:
        sub.start(); raise SystemExit("FAIL: start() should be a NotImplementedError stub")
    except NotImplementedError:
        pass
    print("channel_boundary OFFLINE self-test: ALL PASS (build_row·publish[ok+fail-loud]·skip-by-origin-both-kinds"
          "·on_insert-fanout·start-stub). LIVE round-trip pending builder's tables + Realtime payload + CD end.")
