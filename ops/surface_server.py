#!/usr/bin/env python3
"""ops/surface_server.py — THE SURFACE (v2): a multi-channel, phone-reachable review + chat surface.

The next version of ops/doc_review_server.py. It keeps every capability of that prototype — granular
commenting on board documents, two-way live chat with the channel's lead (SSE push, no polling), image
attachments, PWA install, per-deploy auto-reload — and generalises it three ways:

  1. MULTI-CHANNEL / MULTI-PROJECT. No hardcoded channel. The home lists every project (channel) that has
     content; each project shows its documents, its artefacts, and its chat. Routes are `/c/<channel>/…`.
  2. ARTEFACTS. A new board item type (`artefact`) = a self-contained rich HTML page (a designed page, a
     visual map, a tool). The surface serves its body verbatim into a sandboxed iframe and wraps it with the
     channel chrome + a comment rail + the chat — so a rich page is commentable and discussable like any doc.
  3. ONE FACE. The dark-teal + gold "upward engine" visual language is the surface chrome, so a hosted
     artefact in that language sits natively inside it.

All the fabric wiring is preserved: it registers as the pushable channel member `tim`; the lead injects
replies via the channel transport → SSE → the browser; the operator's comments + chat post back onto the
board via cc_board. Bind 127.0.0.1; expose tailnet-only via `tailscale serve`.
Run: python3 ops/surface_server.py [--port 8782] [--author tim]
"""
from __future__ import annotations
import argparse, base64, html, json, os, queue, re, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
os.environ.setdefault("COMPANY_STORE", os.path.join(REPO, ".data", "store"))
ASSETS = os.path.join(REPO, "ops", "assets")

from runtime import cc_board as cb  # noqa: E402
from runtime import cc_images as ci  # noqa: E402
from runtime import cc_channels as cc  # noqa: E402
from store.fs_store import FsStore  # noqa: E402
STORE = FsStore(os.environ["COMPANY_STORE"])

OPERATOR_HANDLE = "tim"
AUTHOR = "tim"
CHANNELS_DIR = os.path.join(REPO, ".data", "channels")
VERSION = str(int(time.time()))   # per-process build id — clients auto-reload when it changes (deploy)
BG = "#0b1417"

# ── realtime: SSE clients (each tagged with the channel it's watching) + channel-scoped broadcast ──
SSE_CLIENTS: list = []            # list of (queue, channel|None)  — None = home (all channels)
SSE_LOCK = threading.Lock()


def broadcast(payload: dict, channel: str | None = None) -> None:
    """Push to every SSE client watching `channel` (and to home clients, channel=None, which see all)."""
    with SSE_LOCK:
        for q, ch in list(SSE_CLIENTS):
            if ch is None or channel is None or ch == channel:
                q.put(payload)


def _msg_payload(rec: dict) -> dict:
    who = "You" if rec.get("author_session") == OPERATOR_HANDLE else "Vi"
    imgs = ["/img/" + l["target"].split("://", 1)[-1]
            for l in (rec.get("links") or []) if l.get("kind") == "attachment"]
    return {"kind": "msg", "who": who, "body": rec.get("body", ""), "imgs": imgs,
            "channel": rec.get("channel", "")}


def register_operator(port: int) -> None:
    """Register the APP as the pushable channel member 'tim' so the fabric PUSHES replies straight into it
    (route_reply/send to 'tim' → POST to this server → SSE to the browser). The app's channel presence is
    what makes this two-way, not a drop-box."""
    reg = {"handle": OPERATOR_HANDLE, "session_id": "", "cwd": REPO,
           "description": "operator surface (multi-channel review / chat)", "pid": os.getpid(),
           "port": port, "transport": "channel", "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    os.makedirs(CHANNELS_DIR, exist_ok=True)
    with open(os.path.join(CHANNELS_DIR, OPERATOR_HANDLE + ".json"), "w", encoding="utf-8") as f:
        json.dump(reg, f, indent=2)


def lead_target_for(channel: str) -> str:
    """The lead session handle to inject this channel's chat into — per-channel file, falling back to the
    global `_chat_lead.txt`. So each project's chat reaches that project's lead."""
    for name in (f"_chat_lead_{channel}.txt", "_chat_lead.txt"):
        p = os.path.join(CHANNELS_DIR, name)
        if os.path.exists(p):
            t = open(p).read().strip()
            if t:
                return t
    return ""


# ───────────────────────── markdown → html (proven renderer, carried verbatim) ─────────────────────────
def _inline(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?!\w)", r"<em>\1</em>", s)
    return s


def md_to_html(text: str) -> str:
    out, i = [], 0
    lines = text.split("\n"); n = len(lines)
    while i < n:
        st = lines[i].strip()
        if not st:
            i += 1; continue
        mh = re.match(r"^(#{1,6})\s+(.*)$", st)
        if mh:
            lvl = len(mh.group(1)); tag = "h3" if lvl <= 1 else ("h4" if lvl == 2 else "h5")
            out.append(f"<{tag}>{_inline(mh.group(2))}</{tag}>"); i += 1; continue
        if re.match(r"^-{3,}$", st):
            out.append("<hr>"); i += 1; continue
        if st.startswith("> "):
            buf = []
            while i < n and lines[i].strip().startswith("> "):
                buf.append(_inline(lines[i].strip()[2:])); i += 1
            out.append("<blockquote>" + "<br>".join(buf) + "</blockquote>"); continue
        _NEXTBLOCK = r"^([-*] |\d+\. |#{1,6} |> |-{3,}$)"
        if re.match(r"^[-*] ", st):
            items = []
            while i < n and re.match(r"^[-*] ", lines[i].strip()):
                text = [lines[i].strip()[2:]]; i += 1
                while i < n and lines[i].strip() and not re.match(_NEXTBLOCK, lines[i].strip()):
                    text.append(lines[i].strip()); i += 1
                items.append(" ".join(text))
                save = i
                while i < n and not lines[i].strip():
                    i += 1
                if not (i < n and re.match(r"^[-*] ", lines[i].strip())):
                    i = save; break
            out.append("<ul>" + "".join(f"<li>{_inline(t)}</li>" for t in items) + "</ul>"); continue
        mo = re.match(r"^(\d+)\. ", st)
        if mo:
            start = mo.group(1); items = []
            while i < n:
                m = re.match(r"^(\d+)\.\s+(.*)$", lines[i].strip())
                if not m:
                    break
                text = [m.group(2)]; i += 1
                while i < n and lines[i].strip() and not re.match(_NEXTBLOCK, lines[i].strip()):
                    text.append(lines[i].strip()); i += 1
                items.append(" ".join(text))
                save = i
                while i < n and not lines[i].strip():
                    i += 1
                if not (i < n and re.match(r"^\d+\. ", lines[i].strip())):
                    i = save; break
            out.append(f'<ol start="{start}">' + "".join(f"<li>{_inline(t)}</li>" for t in items) + "</ol>"); continue
        buf = []; start = i
        while i < n and lines[i].strip() and not re.match(r"^(#{1,6} |[-*] |\d+\. |> |-{3,}$)", lines[i].strip()):
            buf.append(_inline(lines[i].strip())); i += 1
        if i == start:
            buf.append(_inline(lines[i].strip())); i += 1
        out.append("<p>" + " ".join(buf) + "</p>")
    return "\n".join(out)


def parse_comment(body: str):
    """(scale, quote, text) from the stored `[scale] re: «quote»\\n\\ntext` envelope — raw syntax never shown.
    The scale token is the part before any `·` (so `· SEND-NOW` / `· loc:…` extras don't leak into the chip)."""
    m = re.match(r'^\[([^\]]+)\](?:\s*re:\s*«(.*?)»)?\s*\n*(.*)$', body, re.S)
    if m:
        return m.group(1).split("·")[0].strip(), (m.group(2) or ""), (m.group(3) or "").strip()
    return "", "", body


def anchor_loc(body: str) -> str:
    """The element locator baked into an artefact comment's anchor (`[highlight · loc:<css-path>]`), or ""
    for a whole-artefact / document-block comment. Lets the surface pin a sub-element comment back in place."""
    m = re.match(r'^\[([^\]]+)\]', body)
    if not m:
        return ""
    for tok in m.group(1).split("·"):
        tok = tok.strip()
        if tok.startswith("loc:"):
            return tok[4:].strip()
    return ""


# ───────────────────────── board index + comment threads ─────────────────────────
def _build_index():
    """ONE scan → (items_by_addr, reverse_edge_map, items). Reverse map keyed by (target, kind)."""
    items = cb.list_items()
    by_addr = {i.get("address"): i for i in items}
    rev: dict = {}
    for i in items:
        for ln in (i.get("links") or []):
            rev.setdefault((ln.get("target"), ln.get("kind")), []).append(i)
    return by_addr, rev, items


def _thread(addr, rev):
    def nest(a):
        return [{"comment": e, "replies": nest(e.get("address"))} for e in rev.get((a, "reply_to"), [])]
    return [{"comment": e, "replies": nest(e.get("address"))} for e in rev.get((addr, "commented_on"), [])]


def _count(th):
    return sum(1 + _count(t["replies"]) for t in th)


def _thread_html(thread: list) -> str:
    if not thread:
        return ""
    parts = ['<div class="comments">']
    for t in thread:
        c = t["comment"]
        who = "You" if c.get("author_session") == AUTHOR else "Vi"
        cls = "c-tim" if c.get("author_session") == AUTHOR else "c-lead"
        scale, _q, text = parse_comment(c.get("body", ""))
        chip = f'<span class="cscale">{html.escape(scale)}</span>' if scale and scale != "whole" else ""
        quote = f'<div class="c-quote">{html.escape(_q)}</div>' if _q else ""
        parts.append(
            f'<div class="comment {cls}" data-id="{html.escape(c.get("id",""))}">'
            f'<div class="c-head"><span class="c-who">{who}</span>{chip}'
            f'<span class="c-actions"><button class="c-edit">edit</button><button class="c-del">delete</button></span></div>'
            f'{quote}<div class="c-body">{html.escape(text)}</div>')
        for ln in (c.get("links") or []):
            if ln.get("kind") == "attachment":
                rest = html.escape(ln.get("target", "").split("://", 1)[-1])
                parts.append(f'<img class="c-img" src="/img/{rest}" loading="lazy">')
        if t.get("replies"):
            parts.append(_thread_html(t["replies"]))
        parts.append("</div>")
    parts.append("</div>")
    return "".join(parts)


def channels_with_content():
    """Every channel that has a document or artefact, with its counts — the projects the home lists."""
    _, _, items = _build_index()
    chans: dict = {}
    for it in items:
        ch = it.get("channel")
        if not ch:
            continue
        t = it.get("type")
        if t in ("document", "artefact"):
            d = chans.setdefault(ch, {"channel": ch, "documents": 0, "artefacts": 0})
            d["documents" if t == "document" else "artefacts"] += 1
    return sorted(chans.values(), key=lambda c: (-(c["documents"] + c["artefacts"]), c["channel"]))


def _channel_contents(channel: str):
    by_addr, rev, items = _build_index()
    docs, arts = [], []
    for it in items:
        if it.get("channel") != channel:
            continue
        if it.get("type") == "document":
            docs.append(it)
        elif it.get("type") == "artefact":
            arts.append(it)
    docs.sort(key=lambda d: d.get("created", ""))
    arts.sort(key=lambda d: d.get("created", ""))
    return by_addr, rev, docs, arts


# ───────────────────────── pages ─────────────────────────
def render_home() -> str:
    cards = []
    for c in channels_with_content():
        ch = c["channel"]
        bits = []
        if c["documents"]:
            bits.append(f'{c["documents"]} doc' + ("s" if c["documents"] != 1 else ""))
        if c["artefacts"]:
            bits.append(f'{c["artefacts"]} artefact' + ("s" if c["artefacts"] != 1 else ""))
        cards.append(
            f'<a class="proj" href="/c/{html.escape(ch)}">'
            f'<div class="proj-name">{html.escape(ch)}</div>'
            f'<div class="proj-meta">{" · ".join(bits)}</div></a>')
    return (HOME.replace("{{CARDS}}", "\n".join(cards) or '<div class="empty">No projects with content yet.</div>')
                .replace("{{VERSION}}", VERSION))


def render_channel(channel: str) -> str:
    by_addr, rev, docs, arts = _channel_contents(channel)

    def tile(it, kind):
        addr = it.get("address", "")
        nc = _count(_thread(addr, rev))
        dot = f'<span class="tile-dot">{nc}</span>' if nc else ""
        href = f'/c/{html.escape(channel)}/{kind}/{html.escape(it.get("id",""))}'
        ic = IC["artefact"] if kind == "artefact" else IC["doc"]
        return (f'<a class="tile" href="{href}">'
                f'<span class="tile-ic">{ic}</span>'
                f'<span class="tile-body"><span class="tile-title">{html.escape(it.get("title","(untitled)"))}</span>'
                f'<span class="tile-kind">{kind}</span></span>{dot}</a>')

    sections = []
    if arts:
        sections.append('<div class="grp-h">Artefacts</div>' + "".join(tile(a, "artefact") for a in arts))
    if docs:
        sections.append('<div class="grp-h">Documents</div>' + "".join(tile(d, "doc") for d in docs))
    body = "\n".join(sections) or '<div class="empty">Nothing in this project yet.</div>'
    return (CHANNEL_PAGE.replace("{{CHANNEL}}", html.escape(channel))
                        .replace("{{BODY}}", body)
                        .replace("{{VERSION}}", VERSION))


def render_doc(channel: str, doc_id: str) -> str:
    by_addr, rev, _, _ = _channel_contents(channel)
    doc = by_addr.get(f"board://{doc_id}") or cb.get_item(doc_id)
    doc_addr = doc.get("address", f"board://{doc_id}")
    order = doc.get("order") or [d.get("address") for d in
                                 sorted(rev.get((doc_addr, "part_of"), []), key=lambda x: x.get("title", ""))]
    blocks_html = []
    for addr in order:
        b = by_addr.get(addr)
        if not b:
            continue
        bt = b.get("title", "")
        key = bt.split(" · ")[0] if " · " in bt else bt
        title = bt.split(" · ", 1)[-1]
        th = _thread(addr, rev); nc = _count(th)
        dot = f'<button class="cmt-dot" aria-label="{nc} comments">{nc}</button>' if nc else ""
        blocks_html.append(f'''
        <section class="block" data-addr="{html.escape(addr)}" data-key="{html.escape(key)}">
          <div class="block-head"><span class="block-key">{html.escape(key)}</span>
            <span class="sec-actions">{dot}
              <button class="sec-comment iconbtn xs" data-addr="{html.escape(addr)}" data-key="{html.escape(key)}" aria-label="comment">{IC["bubble"]}</button>
            </span></div>
          <h2 class="block-title">{_inline(title)}</h2>
          <div class="block-body">{md_to_html(b.get("body", ""))}</div>
          {_thread_html(th)}
        </section>''')
    return (DOC_PAGE.replace("{{TITLE}}", html.escape(doc.get("title", "Document")))
                    .replace("{{CHANNEL}}", html.escape(channel))
                    .replace("{{DOC_ADDR}}", html.escape(doc_addr))
                    .replace("{{DOC_THREAD}}", _thread_html(_thread(doc_addr, rev)))
                    .replace("{{BLOCKS}}", "\n".join(blocks_html))
                    .replace("{{COUNT}}", str(len(blocks_html)))
                    .replace("{{VERSION}}", VERSION))


def render_artefact(channel: str, art_id: str) -> str:
    by_addr, rev, _, _ = _channel_contents(channel)
    art = by_addr.get(f"board://{art_id}") or cb.get_item(art_id)
    art_addr = art.get("address", f"board://{art_id}")
    th = _thread(art_addr, rev)
    # the sub-element-anchored comments → pinned back into the artefact at their locator
    anchors = []
    for t in th:
        c = t["comment"]
        loc = anchor_loc(c.get("body", ""))
        if not loc:
            continue
        _s, q, text = parse_comment(c.get("body", ""))
        who = "You" if c.get("author_session") == AUTHOR else "Vi"
        anchors.append({"id": c.get("id", ""), "loc": loc, "quote": q,
                        "snippet": text[:80], "who": who, "n": 1 + _count(t["replies"])})
    return (ARTEFACT_PAGE.replace("{{TITLE}}", html.escape(art.get("title", "Artefact")))
                         .replace("{{CHANNEL}}", html.escape(channel))
                         .replace("{{ART_ID}}", html.escape(art_id))
                         .replace("{{ART_ADDR}}", html.escape(art_addr))
                         .replace("{{THREAD}}", _thread_html(th))
                         .replace("{{NC}}", str(_count(th)))
                         .replace("{{ANCHORS}}", json.dumps(anchors))
                         .replace("{{VERSION}}", VERSION))


def render_chat(channel: str) -> str:
    by_addr, rev, items = _build_index()
    msgs = sorted([i for i in items if i.get("type") == "message" and i.get("channel") == channel],
                  key=lambda m: m.get("created", ""))
    rows = []
    for m in msgs[-200:]:
        who = "You" if m.get("author_session") == AUTHOR else "Vi"
        cls = "m-tim" if m.get("author_session") == AUTHOR else "m-lead"
        imgs = "".join(f'<img class="m-img" src="/img/{html.escape(l["target"].split("://",1)[-1])}" loading="lazy">'
                       for l in (m.get("links") or []) if l.get("kind") == "attachment")
        rows.append(f'<div class="m {cls}"><div class="m-who">{who}</div>'
                    f'<div class="m-body">{html.escape(m.get("body",""))}</div>{imgs}</div>')
    return (CHAT_PAGE.replace("{{CHANNEL}}", html.escape(channel))
                     .replace("{{MSGS}}", "\n".join(rows))
                     .replace("{{VERSION}}", VERSION))


# ───────────────────────── DNA-ish iconography (stroke SVG, no emoji) ─────────────────────────
IC = {
 "menu":   '<svg viewBox="0 0 24 24" class="ic"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
 "bubble": '<svg viewBox="0 0 24 24" class="ic"><path d="M4 5h16a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H10l-4 3v-3H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1z"/></svg>',
 "x":      '<svg viewBox="0 0 24 24" class="ic"><path d="M6 6l12 12M18 6L6 18"/></svg>',
 "send":   '<svg viewBox="0 0 24 24" class="ic"><path d="M4 11l16-7-7 16-2.6-6.4z"/></svg>',
 "back":   '<svg viewBox="0 0 24 24" class="ic"><path d="M15 5l-7 7 7 7"/></svg>',
 "img":    '<svg viewBox="0 0 24 24" class="ic"><rect x="4" y="5" width="16" height="14" rx="2"/><path d="M4 16l4.5-4.5 3 3 3.5-3.5 5 5"/><circle cx="9" cy="9" r="1.4"/></svg>',
 "doc":    '<svg viewBox="0 0 24 24" class="ic"><path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/></svg>',
 "artefact":'<svg viewBox="0 0 24 24" class="ic"><path d="M12 2l9 5v10l-9 5-9-5V7z"/><path d="M12 22V12M21 7l-9 5-9-5"/></svg>',
 "chat":   '<svg viewBox="0 0 24 24" class="ic"><path d="M4 5h16v11H9l-4 3v-3H4z"/></svg>',
}

# ───────────────────────── shared chrome (head + face CSS) ─────────────────────────
HEAD = r"""<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<title>{{TITLE}}</title>
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Surface"><meta name="theme-color" content="#0b1417">
<link rel="manifest" href="/manifest.webmanifest">
<style>
  :root{--bg:#0b1417;--panel:#111f24;--panel2:#16282e;--line:#244149;--line2:#1a3138;
    --ink:#e7eef0;--mute:#9fb4b8;--faint:#678287;--acc:#e9b24a;--you:#4cba93;
    --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
    --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
  html,body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);
    line-height:1.55;-webkit-font-smoothing:antialiased;font-size:16px}
  a{color:inherit;text-decoration:none}
  .ic{width:1.25em;height:1.25em;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round;display:block}
  .topbar{position:sticky;top:0;z-index:30;display:flex;align-items:center;gap:12px;padding:max(10px,env(safe-area-inset-top)) 16px 10px;
    background:rgba(11,20,23,.92);backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
  .topbar .iconbtn{flex:none}
  .topbar .tt{flex:1;min-width:0;font-weight:650;font-size:16px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .topbar .sub{font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--faint)}
  .iconbtn{appearance:none;border:1px solid var(--line);background:var(--panel);color:var(--acc);
    width:38px;height:38px;border-radius:50%;display:grid;place-items:center;cursor:pointer;font-size:17px}
  .iconbtn.xs{width:30px;height:30px;font-size:13px}
  .iconbtn:active{background:var(--panel2)}
  .wrap{max-width:780px;margin:0 auto;padding:18px 16px 120px}
  .empty{color:var(--faint);text-align:center;padding:60px 20px;font-size:15px}
  .toast{position:fixed;left:50%;bottom:88px;transform:translateX(-50%);background:#16323a;color:var(--ink);
    border:1px solid var(--line);padding:10px 16px;border-radius:10px;font-size:14px;opacity:0;transition:opacity .2s;z-index:60;pointer-events:none}
  .toast.show{opacity:1}.toast.err{border-color:#7c3b3b;background:#3a1c1c}
  @media(prefers-reduced-motion:no-preference){.fade{animation:f .3s ease}@keyframes f{from{opacity:0;transform:translateY(4px)}}}
</style>
</head><body>"""

MANIFEST = {"name": "Surface", "short_name": "Surface", "display": "standalone",
            "background_color": BG, "theme_color": BG, "start_url": "/",
            "icons": [{"src": "/icon-180.png", "sizes": "180x180", "type": "image/png"},
                      {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}]}

# ── home: project list ──
HOME = HEAD.replace("{{TITLE}}", "Surface — projects") + r"""
<div class="topbar"><span class="iconbtn" style="cursor:default">{{LOGO}}</span>
  <div class="tt">Surface<div class="sub">your projects</div></div></div>
<div class="wrap">
  <style>
   .proj{display:block;background:var(--panel);border:1px solid var(--line);border-radius:13px;padding:18px 20px;margin-bottom:12px}
   .proj:active{background:var(--panel2)}
   .proj-name{font-size:18px;font-weight:680;letter-spacing:-.01em}
   .proj-meta{font-family:var(--mono);font-size:12px;color:var(--faint);margin-top:5px;letter-spacing:.04em}
  </style>
  {{CARDS}}
</div>
""".replace("{{LOGO}}", IC["artefact"]) + r"""<script>
(function(){var es=new EventSource('/chat-stream');es.onmessage=function(e){try{var d=JSON.parse(e.data);
 if(d.kind==='version'&&window.__v&&window.__v!==d.v)location.reload();if(d.kind==='version')window.__v=d.v;}catch(_){}};})();
</script>{{VERSIONSCRIPT}}</body></html>""".replace("{{VERSIONSCRIPT}}", "")

# ── channel: documents + artefacts ──
CHANNEL_PAGE = HEAD.replace("{{TITLE}}", "{{CHANNEL}}") + r"""
<div class="topbar"><a class="iconbtn" href="/" aria-label="home">{{BACK}}</a>
  <div class="tt">{{CHANNEL}}<div class="sub">project</div></div>
  <a class="iconbtn" href="/c/{{CHANNEL}}/chat" aria-label="chat">{{CHAT}}</a></div>
<div class="wrap">
  <style>
   .grp-h{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--acc);margin:18px 2px 10px}
   .tile{display:flex;align-items:center;gap:13px;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin-bottom:10px}
   .tile:active{background:var(--panel2)}
   .tile-ic{color:var(--acc);flex:none;font-size:18px;display:grid;place-items:center}
   .tile-body{flex:1;min-width:0;display:flex;flex-direction:column;gap:2px}
   .tile-title{font-size:15.5px;font-weight:600;line-height:1.3}
   .tile-kind{font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--faint)}
   .tile-dot{flex:none;font-family:var(--mono);font-size:12px;font-weight:700;color:var(--bg);background:var(--acc);min-width:22px;height:22px;border-radius:11px;display:grid;place-items:center;padding:0 6px}
  </style>
  {{BODY}}
</div>
""".replace("{{BACK}}", IC["back"]).replace("{{CHAT}}", IC["chat"]) + r"""<script>
(function(){var es=new EventSource('/chat-stream?channel={{CHANNEL}}');es.onmessage=function(e){try{var d=JSON.parse(e.data);
 if(d.kind==='version'&&window.__v&&window.__v!==d.v)location.reload();if(d.kind==='version')window.__v=d.v;}catch(_){}};})();
</script></body></html>"""

# ── the comment composer (a bottom sheet) + comment-management JS — shared by doc & artefact pages ──
COMMENT_CSS = r"""
  .comments{margin:12px 0 0;display:flex;flex-direction:column;gap:8px}
  .comment{border-radius:10px;padding:9px 12px;font-size:14.5px;line-height:1.5;border:1px solid var(--line)}
  .comment.c-tim{background:rgba(76,186,147,.09);border-color:rgba(76,186,147,.3)}
  .comment.c-lead{background:rgba(95,155,196,.08);border-color:rgba(95,155,196,.28)}
  .comment .comments{margin-left:12px;border-left:2px solid var(--line);padding-left:10px}
  .c-head{display:flex;align-items:center;gap:8px;margin-bottom:3px}
  .c-who{font-weight:680;font-size:12px;color:var(--acc)}.c-lead .c-who{color:#8fc0e0}
  .cscale{font-family:var(--mono);font-size:9.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--faint);border:1px solid var(--line);border-radius:10px;padding:1px 7px}
  .c-actions{margin-left:auto;display:flex;gap:8px}.c-actions button{appearance:none;background:none;border:none;color:var(--faint);font-size:11px;cursor:pointer;font-family:var(--mono)}
  .c-quote{border-left:2px solid var(--acc);padding-left:8px;color:var(--mute);font-size:13px;font-style:italic;margin:3px 0 5px}
  .c-img{max-width:100%;border-radius:8px;margin-top:6px}
  .sheet{position:fixed;inset:0;z-index:50;background:rgba(0,0,0,.5);display:none;align-items:flex-end}
  .sheet.open{display:flex}
  .sheet-card{background:var(--panel);border-top:1px solid var(--line);border-radius:16px 16px 0 0;width:100%;max-width:780px;margin:0 auto;padding:16px 16px max(16px,env(safe-area-inset-bottom))}
  .sheet-head{display:flex;align-items:center;gap:10px;margin-bottom:10px}
  .sheet-head .sk{font-family:var(--mono);font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--acc);border:1px solid var(--line);border-radius:10px;padding:2px 8px}
  .sheet-head .sq{flex:1;min-width:0;color:var(--mute);font-size:13px;font-style:italic;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  #ctext,.composer textarea{width:100%;background:var(--panel2);border:1px solid var(--line);border-radius:10px;color:var(--ink);font:inherit;padding:11px 12px;resize:none;max-height:40vh}
  .sheet-actions{display:flex;align-items:center;gap:10px;margin-top:10px}
  .sheet-actions .grow{flex:1}
  .btn{appearance:none;border:1px solid var(--acc);background:var(--acc);color:var(--bg);font-weight:650;border-radius:10px;padding:10px 16px;font-size:14.5px;cursor:pointer}
  .btn.ghost{background:none;color:var(--acc)}
  .sendnow{display:flex;align-items:center;gap:6px;font-size:12.5px;color:var(--mute)}
"""

COMMENT_JS = r"""
<div class="sheet" id="sheet"><div class="sheet-card">
  <div class="sheet-head"><span class="sk" id="sk">section</span><span class="sq" id="sq"></span>
    <button class="iconbtn xs" id="sclose" aria-label="close">{{X}}</button></div>
  <textarea id="ctext" rows="2" placeholder="Your comment…"></textarea>
  <div class="sheet-actions">
    <label class="sendnow"><input type="checkbox" id="snow"> send to Vi now</label>
    <span class="grow"></span>
    <button class="btn ghost" id="cimg" aria-label="attach">{{IMG}}</button>
    <button class="btn" id="csend">Comment</button></div>
  <input type="file" id="cfile" accept="image/*" style="display:none">
</div></div>
<div class="toast" id="toast"></div>
<script>
var CH="{{CHANNEL}}";
function toast(m,e){var t=document.getElementById('toast');t.textContent=m;t.className='toast show'+(e?' err':'');setTimeout(function(){t.className='toast';},2200);}
(function(){
 var sheet=document.getElementById('sheet'),sk=document.getElementById('sk'),sq=document.getElementById('sq'),ct=document.getElementById('ctext');
 var cur={},pendingImg=null;
 function open(o){cur=o;sk.textContent=o.scale;sq.textContent=o.quote||'';ct.value='';pendingImg=null;sheet.classList.add('open');setTimeout(function(){ct.focus();},80);}
 function close(){sheet.classList.remove('open');}
 window.__openSheet=open;
 document.getElementById('sclose').onclick=close;
 sheet.addEventListener('click',function(e){if(e.target===sheet)close();});
 function scaleFor(tag){if(/^H/.test(tag))return 'section';if(tag==='LI')return 'point';return 'highlight';}
 document.querySelectorAll('.block-body p,.block-body li,.block-title').forEach(function(el){
   el.addEventListener('click',function(e){e.stopPropagation();var b=el.closest('.block');if(!b)return;
     open({addr:b.dataset.addr,scale:scaleFor(el.tagName),quote:el.innerText.trim().slice(0,140)});});});
 document.querySelectorAll('.sec-comment').forEach(function(b){b.addEventListener('click',function(e){e.stopPropagation();
   open({addr:b.dataset.addr,scale:'section',quote:''});});});
 var db=document.getElementById('docbtn');if(db)db.addEventListener('click',function(){open({addr:this.dataset.addr,scale:'whole',quote:''});});
 var cimg=document.getElementById('cimg'),cfile=document.getElementById('cfile');
 if(cimg){cimg.onclick=function(){cfile.click();};cfile.onchange=function(){var f=cfile.files[0];if(!f)return;var r=new FileReader();r.onload=function(){pendingImg={b64:r.result,mime:f.type};toast('image attached');};r.readAsDataURL(f);};}
 document.getElementById('csend').onclick=function(){
   var body=ct.value.trim();if(!body&&!pendingImg){toast('write a comment or attach an image',true);return;}
   var payload={addr:cur.addr,scale:cur.scale,quote:cur.quote||'',loc:cur.loc||'',body:body,channel:CH,send_now:document.getElementById('snow').checked};
   if(pendingImg){payload.image_b64=pendingImg.b64;payload.image_mime=pendingImg.mime;}
   fetch('/c/'+CH+'/comment',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})
    .then(function(r){return r.json();}).then(function(j){if(j.ok){close();location.reload();}else toast(j.error||'failed',true);})
    .catch(function(){toast('network error',true);});};
})();
(function(){ // edit / delete
 function api(path,payload,done){fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}).then(function(r){return r.json();}).then(done).catch(function(){toast('network error',true);});}
 document.querySelectorAll('.comment').forEach(function(c){
   var id=c.dataset.id;var ed=c.querySelector('.c-edit'),dl=c.querySelector('.c-del');
   if(ed)ed.onclick=function(e){e.stopPropagation();var b=c.querySelector('.c-body');var old=b.textContent;
     var t=prompt('Edit comment:',old);if(t==null||t.trim()===old)return;api('/c/'+CH+'/comment-edit',{id:id,body:t.trim()},function(j){if(j.ok)location.reload();else toast('failed',true);});};
   if(dl)dl.onclick=function(e){e.stopPropagation();if(!confirm('Delete this comment?'))return;api('/c/'+CH+'/comment-delete',{id:id},function(j){if(j.ok)location.reload();else toast('failed',true);});};});
})();
(function(){var es=new EventSource('/chat-stream?channel='+CH);es.onmessage=function(e){try{var d=JSON.parse(e.data);
 if(d.kind==='version'&&window.__v&&window.__v!==d.v)location.reload();if(d.kind==='version')window.__v=d.v;
 if(d.kind==='status')toast(d.body);}catch(_){}};})();
</script>
""".replace("{{X}}", IC["x"]).replace("{{IMG}}", IC["img"])

# ── document page ──
DOC_PAGE = HEAD.replace("{{TITLE}}", "{{TITLE}}") + r"""
<div class="topbar"><a class="iconbtn" href="/c/{{CHANNEL}}" aria-label="back">{{BACK}}</a>
  <div class="tt">{{TITLE}}<div class="sub">{{COUNT}} blocks · tap any line to comment</div></div>
  <button class="iconbtn" id="docbtn" data-addr="{{DOC_ADDR}}" aria-label="comment on whole document">{{BUBBLE}}</button></div>
<div class="wrap">
  <style>
   .block{margin:0 0 22px;padding-bottom:18px;border-bottom:1px solid var(--line2)}
   .block-head{display:flex;align-items:center;gap:8px;margin-bottom:4px}
   .block-key{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--faint);flex:1}
   .sec-actions{display:flex;align-items:center;gap:7px}
   .cmt-dot{appearance:none;border:none;font-family:var(--mono);font-size:12px;font-weight:700;color:var(--bg);background:var(--acc);min-width:22px;height:22px;border-radius:11px;padding:0 6px;cursor:pointer}
   .block-title{font-size:19px;font-weight:700;letter-spacing:-.01em;margin:2px 0 8px;cursor:pointer}
   .block-body{color:var(--mute)}.block-body p,.block-body li{cursor:pointer}
   .block-body h3,.block-body h4,.block-body h5{color:var(--ink);margin:14px 0 6px}
   .block-body code{font-family:var(--mono);font-size:.85em;background:rgba(233,178,74,.1);color:var(--acc);padding:1px 5px;border-radius:4px}
   .block-body strong{color:var(--ink)}.block-body blockquote{border-left:2px solid var(--acc);padding-left:12px;color:var(--mute);margin:8px 0}
   .doc-thread{margin-top:8px}
  """ + COMMENT_CSS + r"""
  </style>
  <div class="doc-thread">{{DOC_THREAD}}</div>
  {{BLOCKS}}
</div>
""".replace("{{BACK}}", IC["back"]).replace("{{BUBBLE}}", IC["bubble"]) + COMMENT_JS + "</body></html>"

# ── artefact page: the hosted HTML in a sandboxed iframe + a comment rail + chat-in ──
ARTEFACT_PAGE = HEAD.replace("{{TITLE}}", "{{TITLE}}") + r"""
<div class="topbar"><a class="iconbtn" href="/c/{{CHANNEL}}" aria-label="back">{{BACK}}</a>
  <div class="tt">{{TITLE}}<div class="sub">artefact</div></div>
  <button class="iconbtn" id="docbtn" data-addr="{{ART_ADDR}}" aria-label="comment">{{BUBBLE}}<span class="nc" id="ncbadge"></span></button></div>
<style>
  .stage{position:fixed;top:58px;left:0;right:0;bottom:0;display:flex;flex-direction:column}
  .frame-wrap{flex:1;min-height:0;position:relative}
  iframe.art{width:100%;height:100%;border:0;background:#0b1417;display:block}
  .rail{background:var(--panel);border-top:1px solid var(--line);max-height:42vh;overflow:auto;padding:12px 16px max(12px,env(safe-area-inset-bottom));transform:translateY(calc(100% - 46px));transition:transform .26s ease}
  .rail.open{transform:translateY(0)}
  .rail-handle{display:flex;align-items:center;gap:10px;cursor:pointer;height:34px;margin:-4px 0 2px}
  .rail-handle .rh-t{font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--acc)}
  .rail-handle .rh-n{margin-left:auto;font-family:var(--mono);font-size:12px;color:var(--faint)}
  .rail-hint{font-size:12.5px;color:var(--faint);margin-top:10px;line-height:1.5}
  .comment.flash{animation:flash 1.4s ease}@keyframes flash{0%,100%{background:rgba(76,186,147,.09)}30%{background:rgba(233,178,74,.28)}}
""" + COMMENT_CSS + r"""
</style>
<div class="stage">
  <div class="frame-wrap"><iframe class="art" id="artframe" src="/c/{{CHANNEL}}/artefact/{{ART_ID}}/raw" sandbox="allow-scripts allow-popups allow-same-origin" title="{{TITLE}}"></iframe></div>
  <div class="rail" id="rail">
    <div class="rail-handle" id="railh"><span class="rh-t">Comments &amp; discussion</span><span class="rh-n" id="railn">{{NC}}</span></div>
    <div id="railbody">{{THREAD}}
      <div style="margin-top:12px"><button class="btn" id="addcmt" style="width:100%">Comment on the whole artefact</button></div>
      <div class="rail-hint">Tip: tap any paragraph, heading or card inside the page to comment on that exact spot.</div>
    </div>
  </div>
</div>
""".replace("{{BACK}}", IC["back"]).replace("{{BUBBLE}}", IC["bubble"]) + COMMENT_JS + r"""
<script>
(function(){
 var ART="{{ART_ADDR}}", ANCH={{ANCHORS}};
 var rail=document.getElementById('rail'),h=document.getElementById('railh'),frame=document.getElementById('artframe');
 h.onclick=function(){rail.classList.toggle('open');};
 var add=document.getElementById('addcmt');if(add)add.onclick=function(){window.__openSheet({addr:ART,scale:'whole',quote:''});};
 var db=document.getElementById('docbtn');if(db)db.onclick=function(){window.__openSheet({addr:ART,scale:'whole',quote:''});};

 // open the rail and flash a specific comment (called from a pin inside the iframe)
 window.__focusComment=function(id){rail.classList.add('open');
   var el=document.querySelector('.comment[data-id="'+id+'"]');
   if(el){el.scrollIntoView({block:'center'});el.classList.add('flash');setTimeout(function(){el.classList.remove('flash');},1400);}};

 // a stable CSS locator for an element inside the artefact (tag + :nth-of-type chain up to body)
 function cssPath(el,doc){
   if(!el||el===doc.body)return 'BODY';
   var segs=[];
   while(el&&el.nodeType===1&&el!==doc.body){
     var tag=el.tagName, p=el.parentNode, k=1, s=p?p.firstElementChild:null;
     while(s){if(s!==el&&s.tagName===tag)k++;if(s===el)break;s=s.nextElementSibling;}
     // recompute index properly (count same-tag siblings before el)
     k=1;s=p?p.firstElementChild:null;while(s&&s!==el){if(s.tagName===tag)k++;s=s.nextElementSibling;}
     segs.unshift(tag+':nth-of-type('+k+')');
     el=p;
   }
   return 'BODY>'+segs.join('>');
 }
 var BLOCK={P:1,LI:1,H1:1,H2:1,H3:1,H4:1,H5:1,H6:1,BLOCKQUOTE:1,TD:1,TH:1,DT:1,DD:1,FIGCAPTION:1,PRE:1,SUMMARY:1};
 function blockOf(el,doc){var n=el;while(n&&n!==doc.body){if(BLOCK[n.tagName])return n;n=n.parentElement;}return el;}

 frame.addEventListener('load',function(){
   var doc;try{doc=frame.contentDocument;}catch(e){return;}
   if(!doc||!doc.body)return;
   // inject annotation styles INTO the artefact document
   var st=doc.createElement('style');
   st.textContent='.__cm_on{outline:2px solid rgba(233,178,74,.5)!important;outline-offset:2px;border-radius:3px}'+
     '.__cm_hi{cursor:pointer}.__cm_hi:hover{outline:2px dashed rgba(233,178,74,.55)!important;outline-offset:2px}'+
     '.__cm_badge{position:absolute;transform:translate(-50%,-50%);background:#e9b24a;color:#0b1417;font:700 11px ui-monospace,Menlo,monospace;min-width:18px;height:18px;border-radius:9px;display:inline-grid;place-items:center;padding:0 5px;cursor:pointer;z-index:9999;box-shadow:0 1px 4px rgba(0,0,0,.4)}';
   doc.head.appendChild(st);
   // make every block clickable → comment on that exact spot
   doc.body.addEventListener('click',function(e){
     var b=blockOf(e.target,doc);
     if(!b)return;
     var txt=(b.innerText||b.textContent||'').trim();
     if(!txt)return;
     e.preventDefault();e.stopPropagation();
     window.__openSheet({addr:ART,scale:(/^H[1-6]$/.test(b.tagName)?'section':(b.tagName==='LI'?'point':'highlight')),
       quote:txt.slice(0,160),loc:cssPath(b,doc)});
   },true);
   // hover affordance on text blocks
   ['p','li','h1','h2','h3','h4','h5','h6','blockquote','td','figcaption','summary'].forEach(function(t){
     doc.querySelectorAll(t).forEach(function(el){el.classList.add('__cm_hi');});});
   // pin existing anchored comments back in place
   ANCH.forEach(function(a){
     var el;try{el=doc.querySelector(a.loc);}catch(_){el=null;}
     if(!el){ // fallback: match by quote text
       if(a.quote){var all=doc.querySelectorAll('p,li,h1,h2,h3,h4,h5,h6,blockquote,td,figcaption,summary');
         for(var i=0;i<all.length;i++){if((all[i].innerText||'').trim().slice(0,160)===a.quote){el=all[i];break;}}}
     }
     if(!el)return;
     el.classList.add('__cm_on');
     var rect=el.getBoundingClientRect();var sx=frame.contentWindow.scrollX||0,sy=frame.contentWindow.scrollY||0;
     var bd=doc.createElement('div');bd.className='__cm_badge';bd.textContent=a.n;
     bd.style.left=(rect.left+sx)+'px';bd.style.top=(rect.top+sy)+'px';
     bd.title=(a.who+': '+(a.snippet||''));
     bd.addEventListener('click',function(ev){ev.preventDefault();ev.stopPropagation();parent.__focusComment(a.id);});
     doc.body.appendChild(bd);
   });
 });
})();
</script></body></html>"""

# ── chat page ──
CHAT_PAGE = HEAD.replace("{{TITLE}}", "Chat — {{CHANNEL}}") + r"""
<div class="topbar"><a class="iconbtn" href="/c/{{CHANNEL}}" aria-label="back">{{BACK}}</a>
  <div class="tt">Chat<div class="sub">{{CHANNEL}}</div></div></div>
<style>
  .chatwrap{max-width:780px;margin:0 auto;padding:14px 16px 96px;display:flex;flex-direction:column;gap:10px}
  .m{max-width:84%;padding:10px 13px;border-radius:13px;font-size:15px;line-height:1.5}
  .m-who{font-family:var(--mono);font-size:9.5px;letter-spacing:.08em;text-transform:uppercase;margin-bottom:3px;opacity:.7}
  .m-tim{align-self:flex-end;background:rgba(76,186,147,.14);border:1px solid rgba(76,186,147,.32)}
  .m-lead{align-self:flex-start;background:var(--panel);border:1px solid var(--line)}
  .m-body{white-space:pre-wrap;word-wrap:break-word}.m-img{max-width:100%;border-radius:9px;margin-top:6px;display:block}
  .composer{position:fixed;left:0;right:0;bottom:0;background:rgba(11,20,23,.95);backdrop-filter:blur(12px);border-top:1px solid var(--line);
    padding:10px 12px max(10px,env(safe-area-inset-bottom));display:flex;gap:8px;align-items:flex-end}
  .composer textarea{flex:1;rows:1;min-height:42px}
""" + COMMENT_CSS.split(".sheet{")[0] + r"""
</style>
<div class="chatwrap" id="chatwrap">{{MSGS}}</div>
<div class="composer">
  <button class="iconbtn" id="cimg" aria-label="attach">{{IMG}}</button>
  <textarea id="msg" rows="1" placeholder="Message Vi…"></textarea>
  <button class="iconbtn" id="send" aria-label="send">{{SEND}}</button>
  <input type="file" id="cfile" accept="image/*" style="display:none">
</div>
<div class="toast" id="toast"></div>
""".replace("{{BACK}}", IC["back"]).replace("{{IMG}}", IC["img"]).replace("{{SEND}}", IC["send"]) + r"""<script>
var CH="{{CHANNEL}}";
function toast(m,e){var t=document.getElementById('toast');t.textContent=m;t.className='toast show'+(e?' err':'');setTimeout(function(){t.className='toast';},2200);}
var wrap=document.getElementById('chatwrap');function scroll(){window.scrollTo(0,document.body.scrollHeight);}scroll();
function addMsg(who,body,imgs){var d=document.createElement('div');d.className='m '+(who==='You'?'m-tim':'m-lead')+' fade';
 var h='<div class="m-who">'+who+'</div><div class="m-body"></div>';d.innerHTML=h;d.querySelector('.m-body').textContent=body;
 (imgs||[]).forEach(function(s){var im=document.createElement('img');im.className='m-img';im.src=s;d.appendChild(im);});
 wrap.appendChild(d);scroll();}
var pendingImg=null,cimg=document.getElementById('cimg'),cfile=document.getElementById('cfile');
cimg.onclick=function(){cfile.click();};cfile.onchange=function(){var f=cfile.files[0];if(!f)return;var r=new FileReader();r.onload=function(){pendingImg={b64:r.result,mime:f.type};toast('image attached');};r.readAsDataURL(f);};
var ta=document.getElementById('msg');ta.addEventListener('input',function(){ta.style.height='auto';ta.style.height=Math.min(ta.scrollHeight,160)+'px';});
function send(){var body=ta.value.trim();if(!body&&!pendingImg)return;var payload={body:body,channel:CH};
 if(pendingImg){payload.image_b64=pendingImg.b64;payload.image_mime=pendingImg.mime;}
 ta.value='';ta.style.height='auto';var hadImg=!!pendingImg;pendingImg=null;
 fetch('/c/'+CH+'/chat-send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})
  .then(function(r){return r.json();}).then(function(j){if(!j.ok)toast(j.error||'failed',true);else if(!j.delivered)toast('saved — no live lead session attached',false);})
  .catch(function(){toast('network error',true);});}
document.getElementById('send').onclick=send;
ta.addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}});
(function(){var es=new EventSource('/chat-stream?channel='+CH);es.onmessage=function(e){try{var d=JSON.parse(e.data);
 if(d.kind==='version'&&window.__v&&window.__v!==d.v)location.reload();if(d.kind==='version'){window.__v=d.v;return;}
 if(d.kind==='status'){toast(d.body);return;}
 if(d.kind==='msg'&&(!d.channel||d.channel===CH))addMsg(d.who,d.body,d.imgs);}catch(_){}};})();
</script></body></html>"""


# ───────────────────────── HTTP handler ─────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _file(self, path, ctype):
        try:
            with open(path, "rb") as f:
                self._send(200, f.read(), ctype)
        except OSError:
            self._send(404, "not found")

    def do_GET(self):
        p = self.path.split("?", 1)[0]
        qs = dict(re.findall(r"([^=&?]+)=([^&]*)", self.path.split("?", 1)[1])) if "?" in self.path else {}
        # assets
        if p in ("/icon-180.png", "/apple-touch-icon.png", "/apple-touch-icon-precomposed.png"):
            return self._file(os.path.join(ASSETS, "dragdev-icon-180.png"), "image/png")
        if p == "/icon-512.png":
            return self._file(os.path.join(ASSETS, "dragdev-icon-512.png"), "image/png")
        if p == "/manifest.webmanifest":
            return self._send(200, json.dumps(MANIFEST), "application/manifest+json")
        if p.startswith("/img/"):
            try:
                data, mime = ci.image_bytes(STORE, "image://" + p[len("/img/"):])
                return self._send(200, data, mime or "image/jpeg")
            except Exception:  # noqa: BLE001
                return self._send(404, "not found")
        # SSE
        if p == "/chat-stream":
            ch = qs.get("channel") or None
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            q: queue.Queue = queue.Queue()
            with SSE_LOCK:
                SSE_CLIENTS.append((q, ch))
            try:
                self.wfile.write(b": connected\n\n")
                self.wfile.write(("data: " + json.dumps({"kind": "version", "v": VERSION}) + "\n\n").encode())
                self.wfile.flush()
                while True:
                    try:
                        payload = q.get(timeout=20)
                    except queue.Empty:
                        self.wfile.write(b": ping\n\n"); self.wfile.flush(); continue
                    self.wfile.write(("data: " + json.dumps(payload) + "\n\n").encode()); self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass
            finally:
                with SSE_LOCK:
                    SSE_CLIENTS[:] = [(qq, cc_) for (qq, cc_) in SSE_CLIENTS if qq is not q]
            return
        # pages
        try:
            if p == "/":
                return self._send(200, render_home())
            m = re.match(r"^/c/([^/]+)/artefact/([^/]+)/raw$", p)
            if m:
                art = cb.get_item(m.group(2))
                return self._send(200, art.get("body", "<p>empty artefact</p>"))
            m = re.match(r"^/c/([^/]+)/artefact/([^/]+)$", p)
            if m:
                return self._send(200, render_artefact(m.group(1), m.group(2)))
            m = re.match(r"^/c/([^/]+)/doc/([^/]+)$", p)
            if m:
                return self._send(200, render_doc(m.group(1), m.group(2)))
            m = re.match(r"^/c/([^/]+)/chat$", p)
            if m:
                return self._send(200, render_chat(m.group(1)))
            m = re.match(r"^/c/([^/]+)/?$", p)
            if m:
                return self._send(200, render_channel(m.group(1)))
        except Exception as e:  # noqa: BLE001
            return self._send(500, f"<pre>{html.escape(str(e))}</pre>")
        self._send(404, "not found")

    def do_POST(self):
        p = self.path.split("?", 1)[0]
        try:
            n = int(self.headers.get("Content-Length", 0))
            d = json.loads(self.rfile.read(n) or b"{}")
        except Exception:  # noqa: BLE001
            return self._send(400, json.dumps({"ok": False, "error": "bad body"}), "application/json")
        try:
            # channel INJECT RECEIVER — the fabric pushed to 'tim' (this app). Body = {content, meta}.
            if p == "/":
                meta = d.get("meta", {}) or {}
                content = d.get("content", "") or ""
                frm = meta.get("from", "Vi")
                channel = meta.get("channel", "") or ""
                if meta.get("kind") == "status":
                    broadcast({"kind": "status", "who": ("You" if frm == OPERATOR_HANDLE else "Vi"), "body": content},
                              channel or None)
                    return self._send(200, json.dumps({"ok": True}), "application/json")
                rec = cb.file_item("message", (content[:54] or "reply"), content, frm,
                                   channel=channel or "fabric")
                broadcast(_msg_payload(rec), channel or None)
                return self._send(200, json.dumps({"ok": True}), "application/json")

            mc = re.match(r"^/c/([^/]+)/(comment|comment-edit|comment-delete|chat-send)$", p)
            if not mc:
                return self._send(404, "not found")
            channel, action = mc.group(1), mc.group(2)

            if action == "chat-send":
                body = (d.get("body", "") or "").strip()
                if not body and not d.get("image_b64"):
                    return self._send(400, json.dumps({"ok": False, "error": "empty"}), "application/json")
                rec = cb.file_item("message", (body[:54] or "image"), body or "(image)", AUTHOR, channel=channel)
                if d.get("image_b64"):
                    raw = base64.b64decode(d["image_b64"].split(",")[-1])
                    irec = ci.save_image(STORE, raw, channel=channel, path=f"chat/{rec['id']}",
                                         mime=d.get("image_mime", "image/jpeg"), author_session=AUTHOR)
                    rec = cb.edit_item(rec["id"], add_links=[{"kind": "attachment", "target": irec["address"]}])
                broadcast(_msg_payload(rec), channel)
                delivered = False
                target = lead_target_for(channel)
                if target:
                    try:
                        r = cc.send(target, f"[Tim — via the app chat · {channel}]\n\n{body or '(image attached)'}",
                                    frm="tim", thread=f"{channel}-chat")
                        delivered = bool(r.get("ok"))
                    except Exception:  # noqa: BLE001
                        delivered = False
                return self._send(200, json.dumps({"ok": True, "delivered": delivered}), "application/json")

            if action == "comment":
                addr, scale = d.get("addr", ""), d.get("scale", "highlight")
                quote = (d.get("quote", "") or "").strip(); body = (d.get("body", "") or "").strip()
                loc = (d.get("loc", "") or "").strip()
                send_now = bool(d.get("send_now"))
                if not addr or not body:
                    return self._send(400, json.dumps({"ok": False, "error": "missing addr or body"}), "application/json")
                anchor = (f"[{scale}{' · SEND-NOW' if send_now else ''}{(' · loc:' + loc) if loc else ''}]"
                          + (f' re: «{quote}»' if quote else ""))
                rec = cb.comment(addr, f"{anchor}\n\n{body}", AUTHOR, title=f"Tim · {scale}", channel=channel)
                if d.get("image_b64"):
                    raw = base64.b64decode(d["image_b64"].split(",")[-1])
                    irec = ci.save_image(STORE, raw, channel=channel, path=f"comment/{rec['id']}",
                                         mime=d.get("image_mime", "image/jpeg"), author_session=AUTHOR)
                    cb.edit_item(rec["id"], add_links=[{"kind": "attachment", "target": irec["address"]}])
                if send_now:
                    target = lead_target_for(channel)
                    if target:
                        try:
                            cc.send(target, f"[Tim — comment · {scale}" + (f' re: «{quote}»' if quote else "") +
                                    f" · {channel}]\n\n{body}", frm="tim", thread=f"{channel}-chat")
                        except Exception:  # noqa: BLE001
                            pass
                return self._send(200, json.dumps({"ok": True, "comment": rec["address"]}), "application/json")

            if action == "comment-edit":
                cid = d.get("id", ""); newtext = (d.get("body", "") or "").strip()
                if not cid or not newtext:
                    return self._send(400, json.dumps({"ok": False, "error": "missing id or body"}), "application/json")
                rec = cb.get_item(cid)
                scale, quote, _ = parse_comment(rec.get("body", ""))
                anchor = f"[{scale}]" + (f' re: «{quote}»' if quote else "")
                cb.edit_item(cid, body=f"{anchor}\n\n{newtext}", by=AUTHOR, note="edit comment")
                return self._send(200, json.dumps({"ok": True}), "application/json")

            if action == "comment-delete":
                cid = d.get("id", "")
                fp = os.path.join(cb.NOTICEBOARD_DIR, f"{cid}.md")
                if cid and os.path.exists(fp):
                    os.remove(fp)
                    return self._send(200, json.dumps({"ok": True}), "application/json")
                return self._send(400, json.dumps({"ok": False, "error": "comment not found"}), "application/json")
        except Exception as e:  # noqa: BLE001
            return self._send(500, json.dumps({"ok": False, "error": str(e)}), "application/json")


def main():
    global AUTHOR
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8782)
    ap.add_argument("--author", default=AUTHOR)
    args = ap.parse_args()
    AUTHOR = args.author
    register_operator(args.port)
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"surface server on http://127.0.0.1:{args.port}  (multi-channel, operator=tim@{args.port})", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
