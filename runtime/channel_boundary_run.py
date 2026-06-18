"""runtime/channel_boundary_run.py — the BOUNDARY ENTRYPOINT: bring the shared-channel edge LIVE.

This is the runnable that makes runtime/channel_boundary.py's pieces live (the lead's lane assignment,
2026-06-18): load the least-privilege principal cred, authenticate, open the OUTBOUND Supabase Realtime
subscription, and inject each new SHARED-channel post into the live company member-sessions (skip-by-origin,
MODEL-1 single-source — confirmed by the lead). Nothing connects INTO the box; the box reaches OUT (WS + the
publish POST). The internal coordination fabric is UNTOUCHED — this entrypoint only READS it (push/find/
channel_members), it does not alter send/push/route (the lifeline stays byte-identical; shared channels are an
ADDITIVE path).

ENV (the lead's loader spec): load `.boundary.env` HERE (the entrypoint), default path
`build-prep/claude-design/supabase/.boundary.env`, overridable via `COMPANY_CHANNEL_ENV_FILE`, with EXISTING
os.environ taking PRECEDENCE — so local reads the file, and PROD sets COMPANY_CHANNEL_* directly (Edge Function
secrets / deploy env) and the file is a no-op. supabase_principal stays os.environ-clean (no file-loading in it).
Canonical keys (the lead aligned .boundary.env to these): COMPANY_CHANNEL_SA_EMAIL + COMPANY_CHANNEL_SA_PASSWORD
+ COMPANY_CHANNEL_ANON_KEY + COMPANY_CHANNEL_SUPABASE_URL.

INJECT primitive = cc_channels.push (PUSH-only — delivers into a live session, NO local _mail.jsonl record:
single-source, Supabase is the store). A dead member → ChannelError → on_insert logs + continues (one dead
session never blocks the rest). members_of = cc_channels.channel_members (the channel's membership).

VERIFY (by use, NOT offline green — fork is the named gate): `verify_my_half()` does the live my-side round-trip
on a THROWAWAY channel (advisor's guardrail — never the real coordination channels): auth → WS connect + join
(JWT-in-join) → publish a 'session' post → the sub RECEIVES the INSERT (proves RLS streams it because the JWT is
in the join). The inject-to-a-second-live-session is the lead's gate B (needs real sessions); this proves the
pipe (auth→publish→Supabase→Realtime-with-RLS→receive) is live end-to-end on my half.
"""
from __future__ import annotations

import os
import sys
import time

_DEFAULT_ENV_FILE = "build-prep/claude-design/supabase/.boundary.env"
_REALTIME_TOPIC = "public.channel_posts"   # builder's (b): topic `realtime:public.channel_posts` (build_join_msg prepends realtime:)


def load_env_file(path: str | None = None, *, repo_root: str | None = None) -> list[str]:
    """Load KEY=VALUE lines from the boundary env file into os.environ — EXISTING os.environ WINS (so prod's
    directly-set vars are never clobbered; local reads the file). Default path (repo-relative)
    build-prep/claude-design/supabase/.boundary.env, override via COMPANY_CHANNEL_ENV_FILE. Returns the KEY
    names set (never values — the file holds a live secret). A missing file is NOT an error (prod sets vars
    directly → the file is a legitimate no-op); returns []."""
    root = repo_root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    p = path or os.environ.get("COMPANY_CHANNEL_ENV_FILE") or os.path.join(root, _DEFAULT_ENV_FILE)
    if not os.path.isfile(p):
        return []
    set_keys = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if not key:
                continue
            if key in os.environ and os.environ[key]:
                continue                         # EXISTING wins (prod-set vars never clobbered)
            os.environ[key] = val
            set_keys.append(key)
    return set_keys


def _format_inject(row: dict) -> tuple[str, dict]:
    """A channel_posts row → (content, meta) for cc_channels.push. meta keys become <channel ...> attributes
    (from/thread/channel) so the member sees the post as a channel message from its real author."""
    content = str(row.get("text") or "")
    meta = {"from": row.get("from_session") or "?", "thread": row.get("thread") or "",
            "channel": row.get("channel_id") or ""}
    return content, meta


def make_inject():
    """inject(handle, row) → deliver into a live session via cc_channels.push (PUSH-only, no local record).
    Raises propagate to on_insert (which logs + continues past a dead session)."""
    from runtime import cc_channels

    def inject(handle: str, row: dict):
        content, meta = _format_inject(row)
        cc_channels.push(handle, content, meta=meta)   # PUSH-only: delivery, no _mail.jsonl (single-source)
    return inject


def make_members_of():
    """members_of(channel_id) → the channel's member handles (push skips dead ones via the on_insert guard)."""
    from runtime import cc_channels

    def members_of(channel_id: str) -> list:
        try:
            return cc_channels.channel_members(channel_id)
        except Exception:                              # an unknown/absent channel → no members (clean)
            return []
    return members_of


def build_subscriber(*, on_status=None):
    """Construct the live ChannelInjectSubscriber (principal + inject + members_of + builder's topic). Assumes
    the env is loaded (call load_env_file first). Does NOT start it — caller .start()s."""
    from runtime.supabase_principal import SupabasePrincipal
    from runtime.channel_boundary import ChannelInjectSubscriber
    principal = SupabasePrincipal("COMPANY_CHANNEL")
    return ChannelInjectSubscriber(members_of=make_members_of(), inject=make_inject(), principal=principal,
                                   topic=_REALTIME_TOPIC, on_status=on_status or _log_status), principal


def _log_status(kind: str, detail: str):
    print(f"[boundary] {kind}: {detail}", flush=True)


def post_to_channel(principal, channel: str, content: str, from_session: str, *,
                    thread: str | None = None, to_session: str | None = None,
                    sender_kind: str = "session") -> dict:
    """The shared-aware POST (the publish hook): a company session posting to `channel` →
      • SHARED (cc_channels.is_shared) → publish to Supabase channel_posts (single-source; the boundary sub
        delivers to members + CD). Returns publish_shared_post's {ok, status, id?, error?}.
      • INTERNAL → the existing LOCAL path (broadcast to channel_members via cc_channels.send) — UNCHANGED;
        internal posts never leave the box. Returns {ok, internal:True, delivered:[...]}.
    The gate of single-source: only shared=true publishes outward (fail-closed — is_shared False ⇒ internal)."""
    from runtime import cc_channels
    from runtime.channel_boundary import build_post_row, publish_shared_post
    if cc_channels.is_shared(channel):
        row = build_post_row(channel, from_session, content, thread=thread, to_session=to_session,
                             sender_kind=sender_kind)
        res = publish_shared_post(row, principal=principal)
        if not res.get("ok"):
            _log_status("publish_failed", f"{channel}: [{res.get('status')}] {res.get('error')}")
        return res
    # INTERNAL: the existing local broadcast (unchanged fabric) — never leaves the box.
    delivered = []
    for handle in cc_channels.channel_members(channel):
        try:
            cc_channels.send(handle, content, frm=from_session, topic=channel)
            delivered.append(handle)
        except Exception as e:  # noqa: BLE001 — a dead member never blocks the rest
            _log_status("internal_send_error", f"{channel}→{handle}: {e}")
    return {"ok": True, "internal": True, "delivered": delivered}


def ensure_design_channel(*, members: list | None = None) -> dict:
    """Seed the `design` SHARED channel (CD's home) if absent — shared=True so its posts publish outward +
    CD can participate. Idempotent (returns the existing record if present). `members` = the company session
    handles to seat in it (the inject targets); the operator/lead adds the real participants. The per-CLIENT
    grant (clients.channels) is builder's Supabase side — this is the company-side record (membership + the
    shared flag for the publish-hook routing + members_of)."""
    from runtime import cc_channels
    rec = cc_channels._read_channel("design")
    if not rec:
        rec = cc_channels.create_channel("design", purpose="Claude Design ⨯ company — shared design channel",
                                         shared=True)
    elif not rec.get("shared"):
        rec["shared"] = True
        cc_channels._write_channel(rec)
    for h in (members or []):
        if h not in rec.get("members", []):
            try:
                cc_channels.add_member("design", h)
            except Exception:  # noqa: BLE001 — already a member / archived; idempotent
                pass
    return cc_channels._read_channel("design")


def run_boundary(*, env_file: str | None = None, block: bool = True):
    """Load env → build → start the Realtime sub (daemon). Returns (subscriber, principal, thread). If block,
    keeps the process alive (the boundary is a long-running service)."""
    keys = load_env_file(env_file)
    print(f"[boundary] env loaded: {len(keys)} key(s) {sorted(keys) or '(file absent — prod sets vars directly)'}",
          flush=True)
    sub, principal = build_subscriber()
    thread = sub.start()
    print(f"[boundary] Realtime sub started → {_REALTIME_TOPIC} (skip-by-origin, MODEL-1 single-source)", flush=True)
    if block:
        try:
            while thread.is_alive():
                thread.join(timeout=1.0)
        except KeyboardInterrupt:
            sub.stop()
    return sub, principal, thread


def verify_my_half(*, env_file: str | None = None, channel: str = "design",
                   timeout_s: float = 20.0) -> dict:
    """LIVE my-half round-trip BY USE (advisor's bar — not offline green). Proves: auth → WS connect + JOIN
    (JWT-in-join) → publish a 'session' SELFTEST post → the sub RECEIVES the INSERT (⇒ RLS streamed it because
    the JWT was in the join — the load-bearing path). Posts to the SEED `design` channel (channel_posts.channel_id
    is a FK→channels, so the channel must EXIST; `design` is the seeded shared channel). The verify's sub uses an
    EMPTY members_of + no-op inject (it does NOT touch live sessions — it only confirms RECEIVE), so the only
    artifact is one marked SELFTEST row in the LOCAL `design` channel_posts (harmless, local, cleanable). The
    inject-to-a-second-live-session is the lead's gate B (real sessions); this proves my pipe is live end-to-end."""
    from runtime.supabase_principal import SupabasePrincipal, SupabaseAuthError
    from runtime.channel_boundary import (ChannelInjectSubscriber, build_post_row, publish_shared_post)

    load_env_file(env_file)
    out = {"auth": False, "joined": False, "published": False, "received": False, "marker": None, "notes": []}
    principal = SupabasePrincipal("COMPANY_CHANNEL")
    try:
        tok = principal.access_token()
        out["auth"] = bool(tok)
    except SupabaseAuthError as e:
        out["notes"].append(f"auth failed: {e}")
        return out

    marker = f"selftest-{int(time.time())}"
    out["marker"] = marker
    seen = {"hit": False}

    def _on_status(kind, detail):
        if kind == "joined":
            out["joined"] = True
        out["notes"].append(f"{kind}: {detail}")

    # a no-op inject (verify proves RECEIVE; inject-to-live-session is gate B) that flags OUR marker row
    def _inject(handle, row):
        pass

    sub = ChannelInjectSubscriber(members_of=lambda _c: [], inject=_inject, principal=principal,
                                  topic=_REALTIME_TOPIC, on_status=_on_status)
    # wrap on_insert to flag when OUR published marker row arrives
    _orig_on_insert = sub.on_insert

    def _watch(row):
        if isinstance(row, dict) and marker in str(row.get("text") or ""):
            seen["hit"] = True
        return _orig_on_insert(row)
    sub.on_insert = _watch
    sub.start()

    # give the join a moment, then publish a 'session' post to the throwaway channel
    deadline = time.time() + timeout_s
    while not out["joined"] and time.time() < deadline:
        time.sleep(0.3)
    row = build_post_row(channel, "ch-8djrpmsl", f"[BOUNDARY SELFTEST — ignore] {marker}", kind="message")
    res = publish_shared_post(row, principal=principal)
    out["published"] = bool(res.get("ok"))
    if not res.get("ok"):
        out["notes"].append(f"publish failed [{res.get('status')}]: {res.get('error')}")
    # wait for the sub to receive our marker row back through Realtime (RLS-gated)
    while not seen["hit"] and time.time() < deadline:
        time.sleep(0.3)
    out["received"] = seen["hit"]
    sub.stop()
    return out


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        r = verify_my_half()
        print("\n[boundary verify_my_half]", {k: r[k] for k in ("auth", "joined", "published", "received")})
        for n in r["notes"]:
            print("   ", n)
        ok = r["auth"] and r["joined"] and r["published"] and r["received"]
        print("RESULT:", "ALL GREEN — my half is LIVE (auth→join→publish→receive, RLS-streamed)" if ok
              else "NOT fully green — see notes (this is the by-use bar, not offline)")
        sys.exit(0 if ok else 1)
    run_boundary()
