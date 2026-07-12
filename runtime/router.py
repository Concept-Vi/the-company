"""runtime/router.py — the ONE presence-aware router (best live transport → fallback → truthful receipt).

The weld the map called for: the two live-inject transports that already exist —
  • the .mjs port push (cc_channels.push, "channel" transport) — reaches a hand-started / unsupervised-live
    session at its own local port;
  • the supervisor stdin inject ("supervised" transport) — reaches a session the supervisor owns;
— are COMPLEMENTARY, and were never chosen-between by presence. This router does exactly that: it
resolves a target through runtime.identity (one durable identity, its live transports by probe), then
picks the transport that ACTUALLY reaches them right now, falls back to the durable mailbox, and returns
a RECEIPT THE CALLER CAN TRUST. It NEVER silently drops and NEVER claims a delivery it cannot confirm
(the phantom-OK fix: cc_channels.push returns {ok:False} on a non-200 WITHOUT raising — this router
inspects that flag instead of assuming success).

THE LADDER (in order; the first that reaches them wins; nothing below is skipped silently):
  1. channel     — a live .mjs port → HTTP-inject; delivered iff the POST really returned 200.
  2. supervised  — the owning supervisor → /inject; delivered iff the supervisor returned 200.
  3. queue       — no live transport → append to the durable mailbox (pull via sessions op=inbox).
  4. none        — unreachable AND no durable id/mailbox → delivered=False, LOUD reason (never a phantom OK).

THE RECEIPT (every field always present — the honest answer to "what actually happened"):
  {target, resolved_uuid, handle, delivered, queued, transport, verb, state, reason}

Read-only w.r.t. the fabric's event stream (emits no agent_sessions.*); the only write it may do is a
durable mailbox append on the queue rung (given a store) — the same append session_channels/session_post
already use. dry_run=True resolves + picks the transport + builds the receipt WITHOUT sending (safe
verification against a live fleet — a real inject into another session is the operator-gated tail).
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

from runtime import cc_channels as cc
from runtime import identity


def _receipt(target, pr, *, delivered, transport, verb, reason, queued=False, state=None) -> dict:
    return {
        "target": target,
        "resolved_uuid": (pr or {}).get("uuid"),
        "handle": (pr or {}).get("handle"),
        "as_id": (pr or {}).get("as_id"),
        "delivered": bool(delivered),
        "queued": bool(queued),
        "transport": transport,               # channel | supervised | queue | none
        "verb": verb,                         # inject | queue | unreachable
        "state": state if state is not None else (pr or {}).get("state"),
        "reason": reason,
    }


def _supervisor_inject(base: str, session: str, content: str, source: str) -> "tuple[bool, str | None]":
    """POST base/inject {session, message, source} — the supervisor writes it as a live user turn into
    the owned session's held-open stdin. Returns (ok, error). Mirrors cc_channels._push_supervised's
    POST but needs no .mjs reg (a /spawn'd session has none — map gap G20)."""
    body = json.dumps({"session": session, "message": content, "source": source}).encode()
    req = urllib.request.Request(base.rstrip("/") + "/inject", data=body, method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200, None
    except (urllib.error.URLError, OSError) as e:
        return False, str(e)


def _record(store, uuid: str, content: str, frm: str, thread: str | None, *,
            delivered: bool, transport: str | None = None) -> dict:
    """The durable mail record — written for EVERY routed message, not only the queued ones (P0.5:
    record-AND-deliver, the review's data-loss fix — deliver-XOR-queue would erase live-delivered
    history the moment channel posts route through here). `verb` is ALWAYS "queue" on this leaf: the
    supervisor acts only on deliver/wake/consult, so a record for an already-live-delivered message is
    never double-injected (the proven post_to_channel backstop pattern). `delivered`/`transport` carry
    the truth for inbox/history readers: delivered:true = it already landed live, this row is the
    audit/backstop copy; delivered:false = a real queued message to pick up."""
    cas = store.put_content(content)
    rec = {"to": f"session://{uuid}", "from": frm, "verb": "queue", "cas": cas,
           "delivered": delivered, "source": "runtime.router"}
    if transport:
        rec["transport"] = transport
    if thread:
        rec["thread"] = thread
    return store.append_agent_mail(rec)


def _record_lenient(store, uuid, content, frm, thread, *, delivered: bool,
                    transport: str | None) -> "tuple[bool, str | None]":
    """Record best-effort AFTER a successful live delivery: a record failure must never turn a delivered
    message into an error — but it is SURFACED on the receipt (recorded:false + reason), never silent."""
    if store is None or not uuid:
        return False, ("no store to record to" if store is None
                       else "no durable uuid to record against (live-only member)")
    try:
        _record(store, uuid, content, frm, thread, delivered=delivered, transport=transport)
        return True, None
    except Exception as e:                       # noqa: BLE001 — audit best-effort, delivery already true
        return False, f"record failed: {type(e).__name__}: {e}"


def route(target: str, content: str, *, frm: str = "fabric", thread: str | None = None,
          base: str | None = None, registry=None, store=None, dry_run: bool = False,
          deep: bool = True) -> dict:
    """Deliver `content` to `target` by the best LIVE transport, falling back to the durable mailbox,
    returning a truthful receipt. NEVER silently drops; NEVER claims unconfirmed delivery.
      target   : any form identity.resolve accepts (uuid|handle|as-id|agent-id|cwd|session://X|substring)
      registry : optional suite.get_agent_session — lets a not-live target resolve as known-closed
      store    : optional suite.store — enables the durable queue rung (needs the target's uuid)
      dry_run  : resolve + choose transport + build receipt WITHOUT sending (safe live verification)
      deep     : False = fast recovery rungs only in resolution (hot paths, e.g. per-mention routing);
                 True (default) = the full ladder incl. the proc-starttime match (single-target sends)"""
    pr = identity.resolve(target, base=base, registry=registry, deep=deep)
    if pr is None:
        return _receipt(target, None, delivered=False, transport="none", verb="unreachable", state=None,
                        reason="unresolved: not a live session and not a known durable id — failing loud, "
                               "not dropping (address by uuid/handle, or the session is gone).")
    uuid = pr.get("uuid")
    transports = pr.get("transports") or []
    meta = {"from": frm}
    if thread:
        meta["thread"] = thread
    fail = ""

    # rung 1 — live .mjs channel transport (unsupervised-live, or a cc_clone supervised reg)
    if "channel" in transports and pr.get("reg") is not None:
        if dry_run:
            return _receipt(target, pr, delivered=True, transport="channel", verb="inject",
                            reason="dry-run: would inject via the live .mjs port")
        try:
            r = cc.push(pr["reg"], content, meta=meta)
        except cc.ChannelError as e:
            r = {"ok": False, "error": str(e)}
        if r.get("ok"):
            tr = r.get("transport", "channel")
            rec_ok, rec_err = _record_lenient(store, uuid, content, frm, thread,
                                              delivered=True, transport=tr)
            out = _receipt(target, pr, delivered=True, transport=tr, verb="inject",
                           reason="live .mjs inject confirmed (HTTP 200)"
                                  + ("" if rec_ok else f" [{rec_err}]"))
            out["recorded"] = rec_ok
            return out
        fail = f".mjs push not ok ({r.get('error') or 'non-200 from port'})"   # do NOT claim delivered

    # rung 2 — supervised-live via the owning supervisor's /inject
    if "supervised" in transports:
        session_key = pr.get("as_id") or uuid
        if dry_run:
            return _receipt(target, pr, delivered=True, transport="supervised", verb="inject",
                            reason="dry-run: would inject via the owning supervisor /inject")
        if session_key:
            ok, err = _supervisor_inject(base or cc.DEFAULT_SUPERVISOR_BASE, session_key, content, frm)
            if ok:
                rec_ok, rec_err = _record_lenient(store, uuid, content, frm, thread,
                                                  delivered=True, transport="supervised")
                out = _receipt(target, pr, delivered=True, transport="supervised", verb="inject",
                               reason="supervisor /inject confirmed (HTTP 200)"
                                      + ("" if rec_ok else f" [{rec_err}]"))
                out["recorded"] = rec_ok
                return out
            fail = (fail + "; " if fail else "") + f"supervisor inject failed ({err})"

    # rung 3 — durable queue (never a silent drop): persist for next-turn pull
    if uuid and store is not None:
        if not dry_run:
            _record(store, uuid, content, frm, thread, delivered=False)
        pre = (fail + " -> " if fail else "")
        out = _receipt(target, pr, delivered=False, queued=True, transport="queue", verb="queue",
                       reason=pre + "no live transport reached them; queued to the durable mailbox "
                              "(they pull it via sessions(op='inbox') next turn).")
        out["recorded"] = not dry_run
        return out

    # rung 4 — genuinely unreachable: LOUD, never a phantom OK
    why = fail or "no live transport and state=" + str(pr.get("state"))
    if not uuid:
        why += "; no durable uuid recovered to queue to (session is reachable-live only, or anonymous)"
    elif store is None:
        why += "; no store provided to queue to"
    return _receipt(target, pr, delivered=False, transport="none", verb="unreachable", reason=why)


if __name__ == "__main__":                       # dry-run smoke against the live fleet (no real injects)
    import sys
    fleet = identity.presence_all()
    print(f"live fleet: {len(fleet)}")
    picks = []
    for r in fleet[:8]:
        tgt = r.get("uuid") or r.get("handle") or r.get("as_id")
        rec = route(tgt, "smoke", dry_run=True)
        picks.append({"target": tgt, "transport": rec["transport"], "delivered": rec["delivered"],
                      "verb": rec["verb"], "state": rec["state"]})
    # a deliberately-unknown target must fail LOUD, not phantom-OK
    unknown = route("session://does-not-exist-000", "smoke", dry_run=True)
    json.dump({"picks": picks,
               "unknown_target": {k: unknown[k] for k in ("transport", "delivered", "verb", "reason")}},
              sys.stdout, indent=2)
    print()
