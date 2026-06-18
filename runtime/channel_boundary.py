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
import threading
import time
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
    # thread is NOT NULL in channel_posts (live-verify caught it 2026-06-18) + the company convention always
    # carries a thread (cc_channels.send generates t-<ts>-<handle> if unset) — so default-generate a thread for
    # a fresh post (a reply/threaded post passes its thread). The post grouping; satisfies the column.
    if not thread:
        thread = f"t-{int(time.time())}-{channel_id}"
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


def _ws_url(http_url: str, anon: str) -> str:
    """The Supabase Realtime WS endpoint from the project URL: https→wss, http→ws (the local stack is http)."""
    base = http_url.rstrip("/")
    if base.startswith("https://"):
        base = "wss://" + base[len("https://"):]
    elif base.startswith("http://"):
        base = "ws://" + base[len("http://"):]
    return f"{base}/realtime/v1/websocket?apikey={anon}&vsn=1.0.0"


def build_join_msg(topic: str, access_token: str, *, table: str = "channel_posts", schema: str = "public",
                   event: str = "INSERT", ref: str = "1") -> dict:
    """The phx_join frame subscribing to `table` INSERTs. ★ LOAD-BEARING (the lead's RLS answer): the principal
    JWT rides as payload.access_token — Supabase Realtime applies RLS to postgres_changes and streams ONLY rows
    the JWT can SELECT, so NO access_token → RLS streams nothing → a silent-empty subscription (looks connected,
    delivers nothing). The 0005 authed-SELECT grant is what makes Realtime deliver these rows."""
    return {"topic": f"realtime:{topic}", "event": "phx_join",
            "payload": {"config": {"postgres_changes": [{"event": event, "schema": schema, "table": table}]},
                        "access_token": access_token},
            "ref": ref}


def parse_realtime_message(raw) -> tuple:
    """(event, record|None) from a raw Realtime WS frame. event=='postgres_changes' + type INSERT → the new
    channel_posts row; everything else (phx_reply join-ack, system, heartbeat) → record None. Defensive dig
    (payload.data.record). (None, None) on non-JSON. The pure parse — offline-testable; start() acts on it."""
    try:
        msg = json.loads(raw)
    except (ValueError, TypeError):
        return None, None
    if not isinstance(msg, dict):
        return None, None
    event = msg.get("event")
    if event == "postgres_changes":
        data = (msg.get("payload") or {}).get("data") or {}
        rec = data.get("record")
        if data.get("type") == "INSERT" and isinstance(rec, dict):
            return event, rec
    return event, None


class ChannelInjectSubscriber:
    """The OUTBOUND Realtime subscriber → live-session injector for SHARED channels. Connects the company's box
    OUT to Supabase Realtime (nothing connects IN — no box exposure), phx_joins channel_posts INSERTs WITH the
    principal JWT (RLS-gated), and injects each new row into the live company member-sessions (skip-by-origin,
    BOTH kinds). `members_of`(channel_id)→[handles], `inject`(handle, row)→deliver (the supervisor /channel-send
    → cc_channels.send path), `principal` (the COMPANY_CHANNEL least-privilege login), `topic` (builder's
    Realtime topic for channel_posts). on_status(kind, detail) is an optional log/Notice sink.

    FALLBACK SEAM (the lead's safety net): if Supabase's Phoenix protocol rabbit-holes, the start() body swaps
    to a urllib SELECT-since-last-seen POLL calling self.on_insert — transport-only; publish/parse/inject/
    skip-origin are unchanged. Target stays Realtime; flag the rabbit-hole rather than ship-laggy-then-redo."""

    def __init__(self, *, members_of, inject, principal: SupabasePrincipal, topic: str,
                 table: str = "channel_posts", on_status=None):
        self._members_of = members_of
        self._inject = inject
        self._principal = principal
        self._topic = topic
        self._table = table
        self._on_status = on_status or (lambda *_a: None)
        self._ws = None
        self._stop = threading.Event()
        self._ref = 0

    def on_insert(self, post_row: dict) -> list[str]:
        """Handle one new channel_posts row: route skip-by-origin to the channel's live company member-sessions
        + inject each (an inject failure is logged, never aborts the others). Returns the handles injected."""
        targets = route_inject(post_row, self._members_of(post_row.get("channel_id")))
        for handle in targets:
            try:
                self._inject(handle, post_row)
            except Exception as e:  # noqa: BLE001 — one dead session never blocks the rest
                self._on_status("inject_error", f"{post_row.get('channel_id')}→{handle}: {e}")
        return targets

    def _next_ref(self) -> str:
        self._ref += 1
        return str(self._ref)

    def start(self, *, reconnect: bool = True, backoff: float = 3.0):
        """Connect + subscribe in a DAEMON thread (non-blocking); reconnect with backoff on drop, fresh token
        each connect. Returns the thread. (Lazy-imports websocket so the publish half needs no WS dep.)"""
        import websocket  # lazy: publish-only callers don't need the WS dep

        def _run():
            while not self._stop.is_set():
                join = build_join_msg(self._topic, self._principal.access_token(),
                                      table=self._table, ref=self._next_ref())
                url = _ws_url(self._principal.url(), self._principal.anon_key())

                def on_open(ws):
                    ws.send(json.dumps(join))
                    self._on_status("joined", self._topic)

                def on_message(ws, raw):
                    _event, rec = parse_realtime_message(raw)
                    if rec is not None:
                        self.on_insert(rec)

                def on_error(ws, err):
                    self._on_status("error", str(err))

                def on_close(ws, *_a):
                    self._on_status("closed", self._topic)

                self._ws = websocket.WebSocketApp(url, on_open=on_open, on_message=on_message,
                                                  on_error=on_error, on_close=on_close)
                threading.Thread(target=self._heartbeat, args=(self._ws,), daemon=True).start()
                self._ws.run_forever()
                if not reconnect or self._stop.is_set():
                    break
                self._stop.wait(backoff)

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        return t

    def _heartbeat(self, ws, *, interval: float = 25.0):
        """Phoenix heartbeat + token refresh — keeps the RLS subscription alive past the JWT's expiry (re-sends
        a fresh access_token; access_token() refreshes near expiry). Exits when the socket drops (run reconnects)."""
        while not self._stop.is_set():
            self._stop.wait(interval)
            if self._stop.is_set():
                break
            try:
                ws.send(json.dumps({"topic": "phoenix", "event": "heartbeat", "payload": {}, "ref": self._next_ref()}))
                ws.send(json.dumps({"topic": f"realtime:{self._topic}", "event": "access_token",
                                    "payload": {"access_token": self._principal.access_token()},
                                    "ref": self._next_ref()}))
            except Exception:  # noqa: BLE001 — socket closed; the run loop reconnects
                break

    def stop(self):
        self._stop.set()
        if self._ws is not None:
            try:
                self._ws.close()
            except Exception:  # noqa: BLE001
                pass


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

    # subscriber on_insert fan-out via fake inject (a dummy principal — on_insert never touches it; start() does)
    dummy = SupabasePrincipal("COMPANY_CHANNEL",
                              env={"COMPANY_CHANNEL_SUPABASE_URL": "https://gctunhsuwpaxeatwlmuv.supabase.co",
                                   "COMPANY_CHANNEL_ANON_KEY": "anon"},
                              fetch=lambda *_: {"access_token": "jwt.x.y"})
    delivered = []
    sub = ChannelInjectSubscriber(members_of=lambda cid: members, principal=dummy, topic="channel_posts",
                                  inject=lambda h, row: delivered.append((h, row["text"])))
    injected = sub.on_insert(cd_row)
    assert injected == members and len(delivered) == 3, (injected, delivered)

    # ★ build_join_msg — the LOAD-BEARING JWT-in-join (no access_token → RLS silent-empty subscription)
    join = build_join_msg("channel_posts", "JWT123")
    assert join["event"] == "phx_join" and join["payload"]["access_token"] == "JWT123", join
    assert join["payload"]["config"]["postgres_changes"][0]["table"] == "channel_posts", join

    # parse_realtime_message — INSERT→record · join-ack→None · junk→(None,None)
    ev, rec = parse_realtime_message(json.dumps({"event": "postgres_changes",
                                                 "payload": {"data": {"type": "INSERT", "record": cd_row}}}))
    assert ev == "postgres_changes" and rec == cd_row, (ev, rec)
    ev2, rec2 = parse_realtime_message(json.dumps({"event": "phx_reply", "payload": {"status": "ok"}}))
    assert ev2 == "phx_reply" and rec2 is None, (ev2, rec2)
    assert parse_realtime_message("not json") == (None, None)

    # _ws_url — https→wss (prod), http→ws (local stack)
    assert _ws_url("https://gctunhsuwpaxeatwlmuv.supabase.co", "anon").startswith(
        "wss://gctunhsuwpaxeatwlmuv.supabase.co/realtime/v1/websocket?apikey=anon"), _ws_url("https://x", "a")
    assert _ws_url("http://localhost:54321", "a").startswith("ws://localhost:54321/realtime/v1/websocket"), "local"

    print("channel_boundary OFFLINE self-test: ALL PASS (build_row·publish[ok+fail-loud]·skip-by-origin-both-kinds"
          "·on_insert-fanout·build_join[JWT-load-bearing]·parse-realtime·ws-url). LIVE WS round-trip pending "
          "builder's local URL/topic + minted principal + 0005 RLS — verified at step-c, NOT offline green.")
