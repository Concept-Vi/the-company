#!/usr/bin/env python3
"""ops/owui_to_fork_watch.py — wake THIS fork session on Tim's OpenWebUI channel messages.

The "talk to fork through the channel" connection (2026-06-27). Polls the OpenWebUI channel; every new
TIM message (user-authored — no webhook meta) is INJECTED into the live fork session via its company-channel
port (verified: POST :<port>/ {content, meta} → renders as a <channel> tag in fork's conversation → wakes it).
fork then replies OUT via the fork webhook (separate). Together = a two-way Tim↔fork chat in the channel.

Seeds to NOW on first run (no replay of old messages). Skips webhook-origin messages (fork's own replies /
mirrored members → no loop). Reply-aware: a reply to a member's message carries that member as context.
Tied to this session's port — restart the watcher with the new port if the session changes.
"""
from __future__ import annotations
import os, json, time, requests

OWUI = os.environ.get("OWUI_BASE", "http://127.0.0.1:8081")
CH = os.environ.get("OWUI_CHANNEL", "a9a338cc-ede3-4268-a43a-94857e2ad4e6")
EMAIL = os.environ.get("OWUI_EMAIL", "v.i@conceptv.com.au")
PASSWORD = os.environ.get("OWUI_PASSWORD", "")
FORK_PORT = os.environ.get("FORK_PORT", "41939")              # this session's company-channel inject port
INTERVAL = int(os.environ.get("WATCH_INTERVAL", "3"))
STATE = os.environ.get("WATCH_STATE", "/home/tim/company/.data/owui_fork_watch_state.json")


def signin() -> str:
    if not PASSWORD:
        raise SystemExit("set OWUI_PASSWORD")
    r = requests.post(f"{OWUI}/api/v1/auths/signin", json={"email": EMAIL, "password": PASSWORD}, timeout=15)
    r.raise_for_status()
    return r.json()["token"]


def load_state():
    try:
        return json.load(open(STATE))
    except Exception:
        return {}


def save_state(s):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(s, open(STATE + ".tmp", "w"))
    os.replace(STATE + ".tmp", STATE)


def inject(content: str, meta: dict) -> bool:
    try:
        r = requests.post(f"http://127.0.0.1:{FORK_PORT}/", json={"content": content, "meta": meta}, timeout=8)
        return r.status_code == 200
    except Exception as e:
        print(f"  inject failed: {e}", flush=True)
        return False


def poll(token: str, state: dict) -> int:
    r = requests.get(f"{OWUI}/api/v1/channels/{CH}/messages", params={"limit": 30},
                     headers={"Authorization": f"Bearer {token}"}, timeout=15)
    r.raise_for_status()
    msgs = list(reversed(r.json() or []))                     # oldest-first
    seen = set(state.setdefault("seen", []))
    if not state.get("seeded"):                               # first run — only NEW messages after start
        seen.update(m["id"] for m in msgs)
        state["seeded"] = True
        state["seen"] = list(seen)[-500:]
        return 0
    n = 0
    for m in msgs:
        if m["id"] in seen:
            continue
        if m.get("meta"):                                     # webhook-origin (fork's reply / a mirrored member) — skip
            seen.add(m["id"]); continue
        text = (m.get("content") or "").strip()
        if not text:
            seen.add(m["id"]); continue
        rt = m.get("reply_to_message") or {}
        target = ((rt.get("user") or {}).get("name")) or (((rt.get("meta") or {}).get("webhook") or {}).get("name"))
        ctx = f" (replying to {target})" if target else ""
        content = f"[Tim, in the OpenWebUI channel{ctx} — reply to him by posting to the fork webhook] {text}"
        if inject(content, {"from": "tim", "thread": "owui-channel", "owui_msg_id": m["id"], "reply_target": target}):
            n += 1
            seen.add(m["id"])
        # if inject fails, leave unseen → retry next poll
    state["seen"] = list(seen)[-500:]
    return n


def main():
    print(f"fork-watch: owui[{CH}] → inject :{FORK_PORT}  interval={INTERVAL}s", flush=True)
    token = signin()
    state = load_state()
    while True:
        try:
            n = poll(token, state)
            save_state(state)
            if n:
                print(f"  injected {n} Tim message(s) → fork", flush=True)
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 401:
                token = signin()
            else:
                print(f"  http error: {e}", flush=True)
        except Exception as e:
            print(f"  error: {e}", flush=True)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    raise SystemExit(main())
