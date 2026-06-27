#!/usr/bin/env python3
"""ops/owui_fabric_bridge.py — the bidirectional sync bridge between a Company FABRIC channel and an
OpenWebUI channel. Makes the room TWO-WAY (build B, Stage 1+3, 2026-06-27):

  fabric → OpenWebUI : every member post mirrors into the OWUI channel via that member's OWN webhook
                       (identity = the member handle). A member seen for the first time SELF-REGISTERS
                       its webhook on the spot (Tim's model: registration is what creates the webhook).
  OpenWebUI → fabric : every message Tim types in the OWUI channel (user-authored, no webhook meta) is
                       forwarded into the fabric channel. If it's a REPLY to a member's message, the
                       member he's answering is read off `reply_to_message.meta.webhook` and prefixed
                       (@member) — the reply/reply-in-thread precision Tim noticed.

Standalone: rides the HTTP surfaces both sides already expose (fabric :8770 /api/channel-history +
/api/channel/post ; OWUI :8081 channels API + the auth-free webhook post). NO fabric-core edit — the
push-transport (cc_channels P2) can replace the fabric→OWUI poll later for lower latency. Crash-safe via
a durable json cursor. Verify-by-use: run --once first (no flood), inspect, then --loop.
"""
from __future__ import annotations
import argparse, json, os, time
import requests

OWUI = os.environ.get("OWUI_BASE", "http://127.0.0.1:8081")
FAB = os.environ.get("FABRIC_BASE", "http://127.0.0.1:8770")
OWUI_CHANNEL = os.environ.get("OWUI_CHANNEL", "a9a338cc-ede3-4268-a43a-94857e2ad4e6")  # the fabric-test OWUI channel
FABRIC_CHANNEL = os.environ.get("FABRIC_CHANNEL", "ch-0")          # an active fabric channel (3 members) for the verify; repoint to a real room
OWUI_EMAIL = os.environ.get("OWUI_EMAIL", "v.i@conceptv.com.au")
OWUI_PASSWORD = os.environ.get("OWUI_PASSWORD", "")               # SECRET — provide via env, never hardcode (committed clean)
STATE = os.environ.get("BRIDGE_STATE", "/home/tim/company/.data/owui_bridge_state.json")
MAX_BACKFILL = int(os.environ.get("MAX_BACKFILL", "8"))            # cap the first-run replay each way (no flood)


def _load_state() -> dict:
    try:
        with open(STATE) as f:
            return json.load(f)
    except Exception:
        return {}


def _save_state(s: dict) -> None:
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    tmp = STATE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(s, f, indent=2)
    os.replace(tmp, STATE)


def owui_signin() -> str:
    if not OWUI_PASSWORD:
        raise SystemExit("set OWUI_PASSWORD in the env (the OpenWebUI admin password) — not hardcoded.")
    r = requests.post(f"{OWUI}/api/v1/auths/signin", json={"email": OWUI_EMAIL, "password": OWUI_PASSWORD}, timeout=15)
    r.raise_for_status()
    return r.json()["token"]


def ensure_member_webhook(token: str, member: str, state: dict) -> dict:
    """Self-registration: a fabric member seen for the first time gets its OWN OWUI webhook (identity baked
    in). Cached in state so it's created once. Returns {id, token}."""
    hooks = state.setdefault("member_webhooks", {})
    if member in hooks:
        return hooks[member]
    r = requests.post(f"{OWUI}/api/v1/channels/{OWUI_CHANNEL}/webhooks/create",
                      headers={"Authorization": f"Bearer {token}"}, json={"name": member}, timeout=15)
    r.raise_for_status()
    wh = r.json()
    hooks[member] = {"id": wh["id"], "token": wh["token"]}
    return hooks[member]


def fabric_to_owui(token: str, state: dict) -> int:
    """Mirror new fabric-channel posts → OWUI via each member's webhook. Returns count mirrored."""
    r = requests.get(f"{FAB}/api/channel-history", params={"channel": FABRIC_CHANNEL}, timeout=15)
    r.raise_for_status()
    posts = (r.json() or {}).get("posts", [])
    last_seq = state.get("fabric_last_seq")
    if last_seq is None:                                          # first run — seed to LATEST (mirror only NEW posts; no old-chatter flood)
        state["fabric_last_seq"] = posts[-1]["seq"] if posts else 0
        last_seq = state["fabric_last_seq"]
    bridge_seqs = set(state.get("bridge_posted_seqs", []))
    n = 0
    for p in posts:
        if p.get("seq", 0) <= last_seq:
            continue
        if p.get("seq") in bridge_seqs:                          # the bridge itself forwarded this (Tim's msg) — don't echo back
            state["fabric_last_seq"] = p["seq"]; continue
        member = p.get("from") or "fabric"
        wh = ensure_member_webhook(token, member, state)
        body = p.get("message") or ""
        try:
            pr = requests.post(f"{OWUI}/api/v1/channels/webhooks/{wh['id']}/{wh['token']}",
                               json={"content": body}, timeout=15)
            if pr.status_code == 200:
                n += 1
        except Exception as e:
            print(f"  [f→o] webhook post failed for {member}: {e}")
        state["fabric_last_seq"] = p["seq"]
    return n


def owui_to_fabric(token: str, state: dict) -> int:
    """Forward Tim's OWUI messages (user-authored, no webhook meta) → the fabric channel. Reply-aware:
    a reply to a member's message is prefixed @member. Returns count forwarded."""
    r = requests.get(f"{OWUI}/api/v1/channels/{OWUI_CHANNEL}/messages", params={"limit": 50},
                     headers={"Authorization": f"Bearer {token}"}, timeout=15)
    r.raise_for_status()
    msgs = list(reversed(r.json() or []))                         # oldest-first
    seen = set(state.setdefault("owui_seen_ids", []))
    if not state.get("owui_seeded"):                             # first run — only forward the last MAX_BACKFILL
        old = [m["id"] for m in msgs[:-MAX_BACKFILL]] if len(msgs) > MAX_BACKFILL else []
        seen.update(old)
        state["owui_seeded"] = True
    n = 0
    for m in msgs:
        if m["id"] in seen:
            continue
        if m.get("meta"):                                        # webhook-origin (came FROM the fabric) — never echo back
            seen.add(m["id"]); continue
        text = (m.get("content") or "").strip()
        if not text:
            seen.add(m["id"]); continue
        # reply-awareness: which member is Tim answering?
        rt = m.get("reply_to_message") or {}
        target = ((rt.get("meta") or {}).get("webhook") or {}).get("name") if rt else None
        if not target and rt:                                    # webhook name may live on the joined user
            target = (rt.get("user") or {}).get("name")
        msg = (f"@{target} {text}" if target else f"Tim: {text}")
        try:
            pr = requests.post(f"{FAB}/api/channel/post", json={"channel": FABRIC_CHANNEL, "message": msg}, timeout=15)
            if pr.status_code == 200:
                n += 1
                seen.add(m["id"])                                # only mark seen on SUCCESS — a failed forward retries next pass
                try:                                             # record the fabric seq we created → fabric→owui skips it (no echo)
                    pj = pr.json(); sq = pj.get("seq") or (pj.get("posted") or {}).get("posted")
                    if sq is not None:
                        state.setdefault("bridge_posted_seqs", []).append(sq)
                        state["bridge_posted_seqs"] = state["bridge_posted_seqs"][-500:]
                except Exception:
                    pass
            else:
                print(f"  [o→f] fabric post non-200 ({pr.status_code}): {pr.text[:120]} — will retry")
        except Exception as e:
            print(f"  [o→f] fabric post failed (will retry): {e}")
    state["owui_seen_ids"] = list(seen)[-500:]                   # bound the cursor
    return n


def one_pass(token: str, state: dict) -> tuple[int, int]:
    f2o = fabric_to_owui(token, state)
    o2f = owui_to_fabric(token, state)
    _save_state(state)
    return f2o, o2f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="a single sync pass (verify, no flood)")
    ap.add_argument("--loop", action="store_true", help="continuous bidirectional sync")
    ap.add_argument("--interval", type=int, default=5)
    a = ap.parse_args()
    print(f"bridge: fabric[{FABRIC_CHANNEL}] ↔ owui[{OWUI_CHANNEL}]  state={STATE}")
    token = owui_signin()
    state = _load_state()
    if a.loop:
        print("loop (Ctrl-C to stop)")
        while True:
            try:
                f2o, o2f = one_pass(token, state)
                if f2o or o2f:
                    print(f"  synced: fabric→owui {f2o} · owui→fabric {o2f}", flush=True)
            except requests.HTTPError as e:
                if e.response is not None and e.response.status_code == 401:
                    token = owui_signin()                        # re-auth on token expiry
                else:
                    print(f"  http error: {e}", flush=True)
            except Exception as e:
                print(f"  pass error: {e}", flush=True)
            time.sleep(a.interval)
    else:
        f2o, o2f = one_pass(token, state)
        print(f"ONE PASS: fabric→owui mirrored {f2o} · owui→fabric forwarded {o2f}")
        print(f"  member webhooks: {list(state.get('member_webhooks',{}).keys())}")


if __name__ == "__main__":
    raise SystemExit(main())
