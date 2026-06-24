#!/usr/bin/env python3
"""ops/doc_review_server.py — a local, phone-reachable REVIEW SURFACE for board documents.

Renders cc_board `document`s (ordered blocks) as a mobile-first web app where the operator comments at any
granularity (tap a paragraph/heading/bullet; per-section icon button; whole-document icon button). Each
submission POSTs back onto the right block via cc_board.comment (the selected text is preserved as the anchor
in the envelope, even though it's not shown in the composer). A hamburger drawer switches between documents.
PWA-capable (add to Home Screen → full-screen, seamless theme color, V icon). DNA iconography (no emojis).

Reusable: serves any document in the channel. Bind 127.0.0.1; exposed tailnet-only via `tailscale serve`.
Run: python3 ops/doc_review_server.py [--port 8781] [--author tim]
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
LEAD_TARGET_FILE = os.path.join(REPO, ".data", "channels", "_chat_lead.txt")
OPERATOR_HANDLE = "tim"
VERSION = str(int(time.time()))   # per-process build id — changes on every restart (deploy) → clients auto-reload

# ── realtime: SSE clients + broadcast (the browser holds one connection; the server pushes — no polling) ──
SSE_CLIENTS: list = []
SSE_LOCK = threading.Lock()


def broadcast(payload: dict) -> None:
    with SSE_LOCK:
        for q in list(SSE_CLIENTS):
            q.put(payload)


def _msg_payload(rec: dict) -> dict:
    who = "You" if rec.get("author_session") == OPERATOR_HANDLE else "Vi"
    imgs = ["/img/" + l["target"].split("://", 1)[-1]
            for l in (rec.get("links") or []) if l.get("kind") == "attachment"]
    return {"kind": "msg", "who": who, "body": rec.get("body", ""), "imgs": imgs}


def register_operator(port: int) -> None:
    """Register the APP as a pushable channel member ('tim') so the fabric can PUSH replies straight into
    it (route_reply/send to 'tim' → POST to this server's port → SSE to the browser). The operator's
    channel presence IS this app — the symmetric half that makes it a real two-way chat, not a drop-box."""
    reg = {"handle": OPERATOR_HANDLE, "session_id": "", "cwd": REPO,
           "description": "operator app (doc-review / chat surface)", "pid": os.getpid(),
           "port": port, "transport": "channel", "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    d = os.path.join(REPO, ".data", "channels")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, OPERATOR_HANDLE + ".json"), "w", encoding="utf-8") as f:
        json.dump(reg, f, indent=2)

CHANNEL = "dragnet-development"
DEFAULT_DOC = "item-389c8489"
AUTHOR = "tim"
BG = "#FBF9F4"

# ── DNA iconography: a brown (bronze) icon, stroke-only, sits in a goldwash circle (.iconbtn). No emojis. ──
IC = {
 "menu":   '<svg viewBox="0 0 24 24" class="ic"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
 "bubble": '<svg viewBox="0 0 24 24" class="ic"><path d="M4 5h16a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H10l-4 3v-3H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1z"/></svg>',
 "x":      '<svg viewBox="0 0 24 24" class="ic"><path d="M6 6l12 12M18 6L6 18"/></svg>',
 "check":  '<svg viewBox="0 0 24 24" class="ic"><path d="M5 13l4 4L19 6"/></svg>',
 "send":   '<svg viewBox="0 0 24 24" class="ic"><path d="M4 11l16-7-7 16-2.6-6.4z"/></svg>',
 "img":    '<svg viewBox="0 0 24 24" class="ic"><path d="M4 5h16v14H4z"/><path d="M4 16l4.5-4.5 3 3 3.5-3.5 5 5"/><circle cx="9" cy="9" r="1.4"/></svg>',
 "back":   '<svg viewBox="0 0 24 24" class="ic"><path d="M15 5l-7 7 7 7"/></svg>',
 "mic":    '<svg viewBox="0 0 24 24" class="ic"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/></svg>',
}


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
                    text.append(lines[i].strip()); i += 1            # fold continuation lines
                items.append(" ".join(text))
                save = i
                while i < n and not lines[i].strip():
                    i += 1
                if not (i < n and re.match(r"^[-*] ", lines[i].strip())):
                    i = save; break                                  # tolerate blank lines between items
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
                    text.append(lines[i].strip()); i += 1            # fold continuation lines into the item
                items.append(" ".join(text))
                save = i
                while i < n and not lines[i].strip():
                    i += 1
                if not (i < n and re.match(r"^\d+\. ", lines[i].strip())):
                    i = save; break                                  # keep blank-separated items in ONE list
            out.append(f'<ol start="{start}">' + "".join(f"<li>{_inline(t)}</li>" for t in items) + "</ol>"); continue
        buf = []; start = i
        while i < n and lines[i].strip() and not re.match(r"^(#{1,6} |[-*] |\d+\. |> |-{3,}$)", lines[i].strip()):
            buf.append(_inline(lines[i].strip())); i += 1
        if i == start:                      # SAFETY: never fail to advance (no infinite loop, ever)
            buf.append(_inline(lines[i].strip())); i += 1
        out.append("<p>" + " ".join(buf) + "</p>")
    return "\n".join(out)


def parse_comment(body: str):
    """Split the stored envelope body into (scale, quote, text) — so the raw [scale] re: «quote» syntax is
    NEVER shown; only the human text + a clean scale chip render."""
    m = re.match(r'^\[([^\]]+)\](?:\s*re:\s*«(.*?)»)?\s*\n*(.*)$', body, re.S)
    if m:
        return m.group(1).split("·")[0].strip(), (m.group(2) or ""), (m.group(3) or "").strip()
    return "", "", body


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
        parts.append(
            f'<div class="comment {cls}" data-id="{html.escape(c.get("id",""))}">'
            f'<div class="c-head"><span class="c-who">{who}</span>{chip}'
            f'<span class="c-actions"><button class="c-edit">Edit</button><button class="c-del">Delete</button></span></div>'
            f'<div class="c-body">{html.escape(text)}</div>')
        for ln in (c.get("links") or []):
            if ln.get("kind") == "attachment":
                rest = html.escape(ln.get("target", "").split("://", 1)[-1])
                parts.append(f'<img class="c-img" src="/img/{rest}" loading="lazy">')
        if t.get("replies"):
            parts.append(_thread_html(t["replies"]))
        parts.append("</div>")
    parts.append("</div>")
    return "".join(parts)


def short_label(title: str) -> str:
    return (title.split("—")[0].strip() or title)[:32]


def _build_index():
    """ONE scan of the board → (items_by_addr, reverse_edge_map, docs). Replaces the O(blocks×files)
    reverse_traverse-per-block that made big pages time out as the board grew."""
    items = cb.list_items()
    by_addr = {i.get("address"): i for i in items}
    rev = {}
    for i in items:
        for ln in (i.get("links") or []):
            rev.setdefault((ln.get("target"), ln.get("kind")), []).append(i)
    docs = sorted([i for i in items if i.get("type") == "document" and i.get("channel") == CHANNEL],
                  key=lambda d: d.get("created", ""))
    return by_addr, rev, docs


def _thread(addr, rev):
    def nest(a):
        return [{"comment": e, "replies": nest(e.get("address"))} for e in rev.get((a, "reply_to"), [])]
    return [{"comment": e, "replies": nest(e.get("address"))} for e in rev.get((addr, "commented_on"), [])]


def _docnav_html(current_id, docs):
    out = ['<div class="drawer-title">Conversation</div>',
           '<a class="doc-link chat-link" href="/chat">💬 Chat with Vi</a>'.replace("💬 ", ""),
           '<div class="drawer-title">Documents</div>']
    for d in docs:
        cur = " current" if d.get("id") == current_id else ""
        out.append(f'<a class="doc-link{cur}" href="/doc/{html.escape(d["id"])}">{html.escape(d.get("title", "(untitled)"))}</a>')
    return "".join(out)


def render_page(doc_id: str) -> str:
    by_addr, rev, docs = _build_index()
    doc = by_addr.get(f"board://{doc_id}") or cb.get_item(doc_id)
    doc_addr = doc.get("address", f"board://{doc_id}")
    order = doc.get("order") or [d.get("address") for d in
                                 sorted(rev.get((doc_addr, "part_of"), []), key=lambda x: x.get("title", ""))]
    def _count(th):
        return sum(1 + _count(t["replies"]) for t in th)
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
          <div class="block-head">
            <span class="block-key">{html.escape(key)}</span>
            <span class="sec-actions">
              {dot}
              <button class="sec-comment iconbtn xs" data-addr="{html.escape(addr)}" data-key="{html.escape(key)}" aria-label="comment on {html.escape(key)}">{IC["bubble"]}</button>
            </span>
          </div>
          <h2 class="block-title">{_inline(title)}</h2>
          <div class="block-body">{md_to_html(b.get("body", ""))}</div>
          {_thread_html(th)}
        </section>''')
    return (PAGE
            .replace("{{TITLE}}", html.escape(doc.get("title", "Document")))
            .replace("{{SHORT}}", html.escape(short_label(doc.get("title", "Document"))))
            .replace("{{DOC_ADDR}}", html.escape(doc_addr))
            .replace("{{DOC_THREAD}}", _thread_html(_thread(doc_addr, rev)))
            .replace("{{DOCNAV}}", _docnav_html(doc_id, docs))
            .replace("{{BLOCKS}}", "\n".join(blocks_html))
            .replace("{{COUNT}}", str(len(blocks_html))))


PAGE = r"""<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<title>{{TITLE}}</title>
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Vi Review">
<meta name="theme-color" content="#FBF9F4">
<link rel="apple-touch-icon" href="/icon-180.png">
<link rel="icon" href="/icon-180.png">
<link rel="manifest" href="/manifest.webmanifest">
<style>
  :root{ --ink:#1C1A19; --paper:#FBF9F4; --muted:#7C7770; --line:#E7E2D6; --gold:#B29135;
         --ochre:#BD922B; --bronze:#836C52; --goldwash:#FEFCEC; --tim:#2f6f4f; --lead:#3a4a6b; }
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
  html,body{margin:0}
  body{background:var(--paper);color:var(--ink);
       font:17px/1.62 -apple-system,BlinkMacSystemFont,"Segoe UI",Georgia,serif;
       padding:0 0 80px;padding-bottom:calc(80px + env(safe-area-inset-bottom))}
  /* DNA icon buttons */
  .iconbtn{display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;flex:0 0 auto;
        background:var(--goldwash);border:1px solid var(--line);border-radius:50%;padding:0}
  .iconbtn:active{background:#f6eccf}
  .iconbtn.xs{width:30px;height:30px}
  .ic{width:19px;height:19px;fill:none;stroke:var(--bronze);stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
  .iconbtn.xs .ic{width:16px;height:16px}
  /* one-line top bar */
  #bar{position:sticky;top:0;z-index:10;background:rgba(251,249,244,.96);backdrop-filter:blur(8px);
       border-bottom:1px solid var(--line);padding-top:env(safe-area-inset-top)}
  .barrow{display:flex;align-items:center;gap:10px;padding:7px 12px;height:50px}
  #title{flex:1 1 auto;margin:0;font-size:15.5px;font-weight:650;white-space:nowrap;overflow:hidden;text-align:center}
  #barmore{max-height:0;overflow:hidden;transition:max-height .22s ease}
  #bar:not(.collapsed) #barmore{max-height:60vh;overflow:auto}
  #barmore .inner{padding:4px 16px 14px}
  .sub{color:var(--muted);font-size:12.5px;line-height:1.4}
  /* drawer */
  #scrim{position:fixed;inset:0;background:rgba(0,0,0,.28);z-index:27;opacity:0;pointer-events:none;transition:opacity .2s}
  #scrim.open{opacity:1;pointer-events:auto}
  #drawer{position:fixed;top:0;left:-110%;bottom:0;width:82%;max-width:330px;z-index:28;background:var(--paper);
        border-right:1px solid var(--line);box-shadow:4px 0 24px rgba(0,0,0,.16);
        transition:left .22s ease;padding:calc(18px + env(safe-area-inset-top)) 14px 18px;overflow:auto;-webkit-overflow-scrolling:touch}
  #drawer.open{left:0}
  .drawer-title{font:600 11px/1 ui-monospace,monospace;color:var(--gold);text-transform:uppercase;letter-spacing:.08em;margin:6px 6px 12px}
  .doc-link{display:block;padding:12px;border-radius:10px;color:var(--ink);text-decoration:none;font-size:15px;line-height:1.35;margin-bottom:4px;border:1px solid transparent}
  .doc-link.current{background:var(--goldwash);border-color:var(--gold);font-weight:600}
  .doc-link:active{background:#f1ece1}
  /* content */
  main{max-width:720px;margin:0 auto;padding:6px 18px}
  .block{padding:18px 0;border-bottom:1px solid var(--line)}
  .block-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:4px}
  .block-key{font:600 11px/1 ui-monospace,monospace;color:var(--gold);letter-spacing:.08em;text-transform:uppercase}
  .sec-actions{display:flex;gap:6px}
  .block-title{font-size:20px;line-height:1.3;margin:0 0 10px;font-weight:660}
  .block-body h3{font-size:18px;margin:16px 0 8px;font-weight:640}
  .block-body h4{font-size:14px;margin:13px 0 6px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
  .block-body p{margin:9px 0}
  .block-body ul,.block-body ol{margin:9px 0;padding-left:22px}
  .block-body li{margin:5px 0}
  .block-body code{background:#f0ece3;padding:1px 5px;border-radius:4px;font-size:14px}
  .block-body blockquote{margin:9px 0;padding:6px 14px;border-left:3px solid var(--gold);color:var(--muted)}
  .block-body hr{border:none;border-top:1px solid var(--line);margin:14px 0}
  .block-body .tap{cursor:pointer;border-radius:7px;padding:3px 7px;margin:1px -7px;transition:background .12s}
  .block-body .tap:active{background:#f1ece1}
  .block-body .tap.sel{background:#fbf1d8;box-shadow:inset 0 0 0 1.5px var(--gold)}
  .comments{margin:12px 0 0;display:none;flex-direction:column;gap:8px}
  .block.show-comments > .comments, #barmore .comments{display:flex}
  .cmt-dot{min-width:24px;height:24px;border-radius:12px;border:1px solid var(--gold);background:var(--goldwash);
        color:var(--ochre);font:600 12px/1 ui-monospace,monospace;padding:0 7px}
  .comment{border-radius:10px;padding:9px 12px;font-size:14.5px;line-height:1.5}
  .comment.c-tim{background:#eef5f0;border:1px solid #cfe3d6}
  .comment.c-lead{background:#eef1f7;border:1px solid #d2dbeb}
  .comment .comments{margin-left:12px;border-left:2px solid var(--line);padding-left:10px;display:flex}
  .c-head{display:flex;align-items:center;gap:8px;margin-bottom:5px}
  .c-who{font:600 11px/1 ui-monospace,monospace;color:var(--muted)}
  .cscale{font:600 9.5px/1 ui-monospace,monospace;color:var(--gold);text-transform:uppercase;letter-spacing:.05em}
  .c-actions{margin-left:auto;display:flex;gap:12px}
  .c-edit,.c-del{background:none;border:none;font:600 11px/1 -apple-system,sans-serif;color:var(--muted);padding:2px 2px}
  .c-del{color:#9a3b2b}
  .c-body{white-space:pre-wrap}
  .c-editbox{width:100%;font:15px/1.5 -apple-system,sans-serif;border:1px solid var(--line);border-radius:8px;padding:8px;min-height:58px}
  .c-editbar{display:flex;gap:8px;margin-top:6px}
  .c-editbar button{font:600 12px/1 -apple-system,sans-serif;border:none;border-radius:8px;padding:7px 13px}
  .c-save{background:var(--ink);color:#fff}.c-cancel{background:#f0ece3}
  /* composer sheet */
  #sheet{position:fixed;inset:auto 0 0 0;z-index:30;background:#fff;border-top:1px solid var(--line);
        box-shadow:0 -8px 30px rgba(0,0,0,.16);padding:14px 16px calc(16px + env(safe-area-inset-bottom));
        transform:translateY(115%);transition:transform .22s ease;max-width:720px;margin:0 auto;border-radius:16px 16px 0 0}
  #sheet.open{transform:translateY(0)}
  #scope{font:600 11px/1.3 ui-monospace,monospace;color:var(--gold);text-transform:uppercase;letter-spacing:.06em;margin-bottom:9px}
  #ctext{width:100%;font:16px/1.5 -apple-system,sans-serif;border:1px solid var(--line);border-radius:10px;
        padding:11px 12px;resize:none;min-height:46px;max-height:40vh}
  .crow{display:flex;gap:10px;margin-top:12px;justify-content:flex-end;align-items:center}
  .cbtn{display:flex;flex-direction:column;align-items:center;gap:3px;background:none;border:none;padding:4px 6px}
  .cbtn .iconbtn{pointer-events:none}
  .cbtn span{font:600 10px/1 -apple-system,sans-serif;color:var(--muted)}
  .cbtn.primary .iconbtn{background:#efe7d2;border-color:var(--gold)}
  .cbtn.send .iconbtn{background:var(--ink);border-color:var(--ink)} .cbtn.send .ic{stroke:#fff}
  .cbtn.send span{color:var(--ink)}
  #attach{margin-right:auto}
  #thumb{margin-top:10px}
  #thumb img{max-width:100%;max-height:180px;border-radius:10px;border:1px solid var(--line)}
  .c-img{display:block;max-width:100%;max-height:300px;border-radius:10px;border:1px solid var(--line);margin-top:8px}
  #toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:var(--tim);color:#fff;
        padding:11px 18px;border-radius:24px;font:600 14px/1 -apple-system,sans-serif;z-index:40;display:none}
</style></head><body>
<div id="scrim"></div>
<nav id="drawer">{{DOCNAV}}</nav>

<header id="bar" class="collapsed">
  <div class="barrow">
    <button id="ham" class="iconbtn" aria-label="documents">__MENU__</button>
    <h1 id="title">{{SHORT}}</h1>
    <button id="docbtn" class="iconbtn" data-addr="{{DOC_ADDR}}" aria-label="comment on whole document">__BUBBLE__</button>
  </div>
  <div id="barmore"><div class="inner">
    <div class="sub">{{COUNT}} blocks · tap any paragraph, heading or bullet to comment · tap the title or the menu (top-left) for other documents</div>
    {{DOC_THREAD}}
  </div></div>
</header>
<main>{{BLOCKS}}</main>

<div id="sheet">
  <div id="scope"></div>
  <textarea id="ctext" rows="1" placeholder="Your comment…"></textarea>
  <div id="thumb"></div>
  <input id="file" type="file" accept="image/*" style="display:none">
  <div class="crow">
    <button id="attach" class="cbtn"><span class="iconbtn">__IMG__</span><span>Image</span></button>
    <button id="cancel" class="cbtn"><span class="iconbtn">__X__</span><span>Cancel</span></button>
    <button id="post" class="cbtn primary"><span class="iconbtn">__CHECK__</span><span>Save</span></button>
    <button id="send" class="cbtn send"><span class="iconbtn">__SEND__</span><span>Send now</span></button>
  </div>
</div>
<div id="toast"></div>
<script>
(function(){ // drawer
  var ham=document.getElementById('ham'),drawer=document.getElementById('drawer'),scrim=document.getElementById('scrim'),
      title=document.getElementById('title'),bar=document.getElementById('bar');
  function dr(o){drawer.classList.toggle('open',o);scrim.classList.toggle('open',o);}
  ham.addEventListener('click',function(e){e.stopPropagation();dr(!drawer.classList.contains('open'));});
  title.addEventListener('click',function(e){e.stopPropagation();dr(!drawer.classList.contains('open'));});
  scrim.addEventListener('click',function(){dr(false);});
  // doc-link navigation (explicit JS nav — robust on iOS regardless of anchor hit-testing)
  document.querySelectorAll('.doc-link').forEach(function(a){
    a.addEventListener('click',function(e){var h=a.getAttribute('href');if(h){e.preventDefault();window.location.assign(h);}});
  });
  // tap empty bar area -> expand/collapse the "more" panel
  bar.addEventListener('click',function(e){ if(e.target===bar||e.target.classList.contains('barrow')) bar.classList.toggle('collapsed'); });
})();
(function(){ // commenting
  var pending=null,lastSel=null,pendingImg=null;
  var sheet=document.getElementById('sheet'),scope=document.getElementById('scope'),
      ctext=document.getElementById('ctext'),toast=document.getElementById('toast'),
      thumb=document.getElementById('thumb'),fileInput=document.getElementById('file');
  function showToast(m,bad){toast.textContent=m;toast.style.background=bad?'#9a3b2b':'#2f6f4f';toast.style.display='block';setTimeout(function(){toast.style.display='none';},2200);}
  function clearSel(){ if(lastSel){lastSel.classList.remove('sel');lastSel=null;} }
  function grow(){ ctext.style.height='auto'; ctext.style.height=Math.min(ctext.scrollHeight,window.innerHeight*0.4)+'px'; }
  ctext.addEventListener('input',grow);
  function clearImg(){pendingImg=null;thumb.innerHTML='';fileInput.value='';}
  document.getElementById('attach').addEventListener('click',function(){fileInput.click();});
  fileInput.addEventListener('change',function(){var f=fileInput.files&&fileInput.files[0];if(!f)return;var r=new FileReader();r.onload=function(){var u=String(r.result);pendingImg={b64:u.split(',')[1],mime:f.type||'image/jpeg'};thumb.innerHTML='<img src="'+u+'">';};r.readAsDataURL(f);});
  function openSheet(p){pending=p;clearImg();scope.textContent=p.scale+' · '+(p.key||'document');ctext.value='';sheet.classList.add('open');setTimeout(function(){grow();ctext.focus();},250);}
  function closeSheet(){sheet.classList.remove('open');pending=null;clearImg();clearSel();}
  function scaleFor(t){return t==='P'?'paragraph':t==='LI'?'point':(t==='H3'||t==='H4')?'heading':t==='BLOCKQUOTE'?'quote':'text';}

  document.querySelectorAll('.block-body p, .block-body li, .block-body h3, .block-body h4, .block-body blockquote').forEach(function(el){
    if(!el.innerText.trim())return;
    el.classList.add('tap');
    el.addEventListener('click',function(e){e.stopPropagation();var b=el.closest('.block');if(!b)return;clearSel();el.classList.add('sel');lastSel=el;openSheet({addr:b.dataset.addr,key:b.dataset.key,scale:scaleFor(el.tagName),quote:el.innerText.trim()});});
  });
  document.querySelectorAll('.sec-comment').forEach(function(b){b.addEventListener('click',function(e){e.stopPropagation();clearSel();openSheet({addr:b.dataset.addr,key:b.dataset.key,scale:'section',quote:''});});});
  document.getElementById('docbtn').addEventListener('click',function(e){e.stopPropagation();clearSel();openSheet({addr:this.dataset.addr,key:'whole document',scale:'whole',quote:''});});
  document.getElementById('cancel').addEventListener('click',closeSheet);

  function submit(sendNow){
    if(!pending)return; var body=ctext.value.trim();
    if(!body && !pendingImg){showToast('Write a comment or attach an image',true);return;}
    var payload={addr:pending.addr,key:pending.key,scale:pending.scale,quote:pending.quote,body:body||'(image)',send_now:!!sendNow};
    if(pendingImg){payload.image_b64=pendingImg.b64;payload.image_mime=pendingImg.mime;}
    fetch('/comment',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})
     .then(function(r){return r.json();}).then(function(j){
        if(j.ok){closeSheet();showToast(sendNow?'Sent':'Saved');setTimeout(function(){location.reload();},650);}
        else{showToast(j.error||'Failed',true);}
     }).catch(function(){showToast('Network error',true);});
  }
  document.getElementById('post').addEventListener('click',function(){submit(false);});
  document.getElementById('send').addEventListener('click',function(){submit(true);});
})();
(function(){ // comment management: dot-toggle, edit, delete
  function api(path,payload,done){fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}).then(function(r){return r.json();}).then(done).catch(function(){alert('network error');});}
  document.querySelectorAll('.cmt-dot').forEach(function(d){
    d.addEventListener('click',function(e){e.stopPropagation();var b=d.closest('.block');if(b)b.classList.toggle('show-comments');});
  });
  document.querySelectorAll('.c-del').forEach(function(btn){
    btn.addEventListener('click',function(e){e.stopPropagation();var c=btn.closest('.comment');if(!c)return;if(!confirm('Delete this comment?'))return;api('/comment-delete',{id:c.dataset.id},function(j){if(j.ok)location.reload();else alert(j.error||'failed');});});
  });
  document.querySelectorAll('.c-edit').forEach(function(btn){
    btn.addEventListener('click',function(e){e.stopPropagation();var c=btn.closest('.comment');if(!c)return;
      var bodyEl=c.querySelector('.c-body');if(!bodyEl||c.querySelector('.c-editbox'))return;var cur=bodyEl.textContent;
      var ta=document.createElement('textarea');ta.className='c-editbox';ta.value=cur;
      var bar=document.createElement('div');bar.className='c-editbar';
      bar.innerHTML='<button class="c-save">Save</button><button class="c-cancel">Cancel</button>';
      bodyEl.style.display='none';bodyEl.after(bar);bodyEl.after(ta);ta.focus();
      bar.querySelector('.c-cancel').addEventListener('click',function(){location.reload();});
      bar.querySelector('.c-save').addEventListener('click',function(){var v=ta.value.trim();if(!v)return;api('/comment-edit',{id:c.dataset.id,body:v},function(j){if(j.ok)location.reload();else alert(j.error||'failed');});});
    });
  });
})();
// auto-reload the doc view when the app is redeployed (server restart -> new version on SSE reconnect)
(function(){
  function appVer(v){ if(window.__appver==null){window.__appver=v;return;} if(window.__appver!==v){var a=document.activeElement; if(a&&(a.tagName==='TEXTAREA'||a.tagName==='INPUT')){a.addEventListener('blur',function(){location.reload();},{once:true});} else {location.reload();} } }
  try{var es=new EventSource('/chat-stream');es.onmessage=function(e){var m;try{m=JSON.parse(e.data);}catch(_){return;} if(m.kind==='version')appVer(m.v);};}catch(_){}
})();
</script></body></html>"""
for _k, _v in IC.items():
    PAGE = PAGE.replace("__" + _k.upper() + "__", _v)


CHAT_PAGE = r"""<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<title>Chat with Vi</title>
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="theme-color" content="#FBF9F4">
<link rel="apple-touch-icon" href="/icon-180.png"><link rel="manifest" href="/manifest.webmanifest">
<style>
  :root{--ink:#1C1A19;--paper:#FBF9F4;--muted:#7C7770;--line:#E7E2D6;--gold:#B29135;--ochre:#BD922B;--bronze:#836C52;--goldwash:#FEFCEC;}
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
  html,body{margin:0}
  body{background:var(--paper);color:var(--ink);font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
       padding-bottom:calc(96px + env(safe-area-inset-bottom))}
  .iconbtn{display:inline-flex;align-items:center;justify-content:center;width:38px;height:38px;flex:0 0 auto;background:var(--goldwash);border:1px solid var(--line);border-radius:50%;padding:0;text-decoration:none}
  .iconbtn.send{background:var(--ink);border-color:var(--ink)} .iconbtn.send .ic{stroke:#fff}
  .ic{width:19px;height:19px;fill:none;stroke:var(--bronze);stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
  #bar{position:sticky;top:0;z-index:10;background:rgba(251,249,244,.96);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);padding-top:env(safe-area-inset-top)}
  .barrow{display:flex;align-items:center;gap:10px;padding:7px 12px;height:50px}
  #title{flex:1;margin:0;font-size:15.5px;font-weight:650;text-align:center}
  main{max-width:720px;margin:0 auto;padding:14px 16px;display:flex;flex-direction:column;gap:10px}
  .msg{display:flex}
  .msg-you{justify-content:flex-end} .msg-vi{justify-content:flex-start}
  .msg-b{max-width:82%;border-radius:14px;padding:10px 13px;white-space:pre-wrap;line-height:1.5;font-size:15px}
  .msg-you .msg-b{background:#eef5f0;border:1px solid #cfe3d6}
  .msg-vi .msg-b{background:#fff;border:1px solid var(--line)}
  .msg-b img{display:block;max-width:100%;border-radius:10px;margin-top:8px;border:1px solid var(--line)}
  .msg-empty{color:var(--muted);text-align:center;margin-top:40px}
  .resp-b{color:var(--muted);font-style:italic}
  .dots{display:inline-block;margin-left:6px;vertical-align:middle}
  .dots i{display:inline-block;width:5px;height:5px;border-radius:50%;background:var(--bronze);margin:0 1.5px;animation:bl 1s infinite}
  .dots i:nth-child(2){animation-delay:.2s}.dots i:nth-child(3){animation-delay:.4s}
  @keyframes bl{0%,80%,100%{opacity:.3}40%{opacity:1}}
  #composer{position:fixed;inset:auto 0 0 0;z-index:20;background:rgba(251,249,244,.97);backdrop-filter:blur(8px);
        border-top:1px solid var(--line);padding:10px 14px calc(10px + env(safe-area-inset-bottom));max-width:720px;margin:0 auto}
  #thumb img{max-height:120px;border-radius:10px;border:1px solid var(--line);margin-bottom:8px}
  .crow{display:flex;align-items:flex-end;gap:9px}
  #ctext{flex:1;font:16px/1.4 -apple-system,sans-serif;border:1px solid var(--line);border-radius:18px;padding:10px 14px;resize:none;min-height:42px;max-height:38vh}
  .iconbtn.listening{background:#9a3b2b;border-color:#9a3b2b;animation:pulse 1.1s infinite}
  .iconbtn.listening .ic{stroke:#fff}
  @keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(154,59,43,.5)}50%{box-shadow:0 0 0 6px rgba(154,59,43,0)}}
  #toast{position:fixed;bottom:90px;left:50%;transform:translateX(-50%);background:#9a3b2b;color:#fff;padding:10px 16px;border-radius:22px;font:600 14px/1 -apple-system,sans-serif;z-index:30;display:none}
</style></head><body>
<header id="bar"><div class="barrow">
  <a href="/" class="iconbtn" aria-label="back to documents">__BACK__</a>
  <h1 id="title">Chat with Vi</h1>
  <span style="width:38px"></span>
</div></header>
<main id="chat">{{MSGS}}</main>
<div id="composer">
  <div id="thumb"></div>
  <input id="file" type="file" accept="image/*" style="display:none">
  <div class="crow">
    <button id="attach" class="iconbtn" aria-label="attach image">__IMG__</button>
    <button id="mic" class="iconbtn" aria-label="dictate">__MIC__</button>
    <textarea id="ctext" rows="1" placeholder="Message Vi…"></textarea>
    <button id="send" class="iconbtn send" aria-label="send">__SEND__</button>
  </div>
</div>
<div id="toast"></div>
<script>
(function(){
  var ctext=document.getElementById('ctext'),thumb=document.getElementById('thumb'),fileInput=document.getElementById('file'),toast=document.getElementById('toast'),chat=document.getElementById('chat'),pendingImg=null;
  function esc(s){return (s||'').replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c];});}
  function atBottom(){return window.innerHeight+window.scrollY>=document.body.scrollHeight-90;}
  function scroll(){window.scrollTo(0,document.body.scrollHeight);}
  scroll();
  function append(m){var stick=atBottom();var d=document.createElement('div');d.className='msg '+(m.who==='You'?'msg-you':'msg-vi');
    var imgs=(m.imgs||[]).map(function(u){return '<img src="'+u+'">';}).join('');
    d.innerHTML='<div class="msg-b">'+esc(m.body)+imgs+'</div>';chat.appendChild(d);if(stick)scroll();}
  function err(m){toast.textContent=m;toast.style.display='block';setTimeout(function(){toast.style.display='none';},2200);}
  function grow(){ctext.style.height='auto';ctext.style.height=Math.min(ctext.scrollHeight,window.innerHeight*0.38)+'px';}
  ctext.addEventListener('input',grow);
  function clearImg(){pendingImg=null;thumb.innerHTML='';fileInput.value='';}
  document.getElementById('attach').addEventListener('click',function(){fileInput.click();});
  fileInput.addEventListener('change',function(){var f=fileInput.files&&fileInput.files[0];if(!f)return;var r=new FileReader();r.onload=function(){var u=String(r.result);pendingImg={b64:u.split(',')[1],mime:f.type||'image/jpeg'};thumb.innerHTML='<img src="'+u+'">';};r.readAsDataURL(f);});
  // microphone — browser speech recognition (web transcription; works on iOS Safari), dictates into the box
  (function(){var mic=document.getElementById('mic');var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
    if(!SR){mic.style.display='none';return;}
    var rec=null,listening=false,base='';
    mic.addEventListener('click',function(){
      if(listening){try{rec.stop();}catch(_){}return;}
      try{rec=new SR();}catch(_){return;}
      rec.lang='en-US';rec.interimResults=true;rec.continuous=true;base=ctext.value;
      rec.onstart=function(){listening=true;mic.classList.add('listening');};
      rec.onend=function(){listening=false;mic.classList.remove('listening');};
      rec.onerror=function(){listening=false;mic.classList.remove('listening');};
      rec.onresult=function(e){var interim='';for(var i=e.resultIndex;i<e.results.length;i++){var t=e.results[i][0].transcript;if(e.results[i].isFinal){base=(base?base+' ':'')+t.trim();}else{interim+=t;}}ctext.value=base+(interim?((base?' ':'')+interim):'');grow();};
      try{rec.start();}catch(_){}
    });
  })();
  var indicator=null;
  function showResp(t){if(!indicator){indicator=document.createElement('div');indicator.className='msg msg-vi';chat.appendChild(indicator);}indicator.innerHTML='<div class="msg-b resp-b">'+esc(t||'Vi is responding')+'<span class="dots"><i></i><i></i><i></i></span></div>';if(atBottom())scroll();}
  function clearResp(){if(indicator){indicator.remove();indicator=null;}}
  function send(){var body=ctext.value.trim();if(!body&&!pendingImg)return;
    var payload={body:body};if(pendingImg){payload.image_b64=pendingImg.b64;payload.image_mime=pendingImg.mime;}
    ctext.value='';grow();clearImg();
    fetch('/chat-send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})
     .then(function(r){return r.json();}).then(function(j){if(!j.ok){err(j.error||'failed');}else if(j.delivered){showResp('Vi is responding');}})
     .catch(function(){err('network error');});}
  document.getElementById('send').addEventListener('click',send);
  // realtime inbound — hold an SSE connection; the server PUSHES messages + ephemeral status (no polling, no reload)
  try{var es=new EventSource('/chat-stream');es.onmessage=function(e){var m;try{m=JSON.parse(e.data);}catch(_){return;}
      if(m.kind==='version'){appVer(m.v);return;}
      if(m.kind==='status'){showResp(m.body);return;} if(m.who==='Vi')clearResp(); append(m);};}catch(_){}
})();
// auto-reload when the APP is redeployed (server restart -> new version on SSE reconnect) — never mid-typing
function appVer(v){ if(window.__appver==null){window.__appver=v;return;} if(window.__appver!==v){
  var a=document.activeElement; if(a&&(a.tagName==='TEXTAREA'||a.tagName==='INPUT')){a.addEventListener('blur',function(){location.reload();},{once:true});} else {location.reload();} } }
</script></body></html>"""
for _k, _v in IC.items():
    CHAT_PAGE = CHAT_PAGE.replace("__" + _k.upper() + "__", _v)


def render_chat():
    msgs = sorted([i for i in cb.list_items(type="message") if i.get("channel") == CHANNEL],
                  key=lambda x: x.get("created", ""))
    rows = []
    for m in msgs:
        cls = "msg-you" if m.get("author_session") == AUTHOR else "msg-vi"
        imgs = "".join(f'<img src="/img/{html.escape(l["target"].split("://",1)[-1])}">'
                       for l in (m.get("links") or []) if l.get("kind") == "attachment")
        rows.append(f'<div class="msg {cls}"><div class="msg-b">{html.escape(m.get("body",""))}{imgs}</div></div>')
    return CHAT_PAGE.replace("{{MSGS}}", "".join(rows) or '<div class="msg-empty">No messages yet — say hello.</div>')


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        try:
            self.end_headers()
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass  # client navigated away / gave up — not an error

    def _file(self, path, ctype):
        try:
            with open(path, "rb") as f:
                self._send(200, f.read(), ctype)
        except OSError:
            self._send(404, "not found")

    def do_GET(self):
        p = self.path.split("?", 1)[0]
        if p in ("/icon-180.png", "/apple-touch-icon.png", "/apple-touch-icon-precomposed.png"):
            return self._file(os.path.join(ASSETS, "dragdev-icon-180.png"), "image/png")
        if p == "/icon-512.png":
            return self._file(os.path.join(ASSETS, "dragdev-icon-512.png"), "image/png")
        if p.startswith("/img/"):
            try:
                data, mime = ci.image_bytes(STORE, "image://" + p[len("/img/"):])
                return self._send(200, data, mime or "image/jpeg")
            except Exception:  # noqa: BLE001
                return self._send(404, "not found")
        if p == "/manifest.webmanifest":
            man = {"name": "Vi — Review", "short_name": "Vi Review", "display": "standalone",
                   "background_color": BG, "theme_color": BG, "start_url": "/",
                   "icons": [{"src": "/icon-180.png", "sizes": "180x180", "type": "image/png"},
                             {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}]}
            return self._send(200, json.dumps(man), "application/manifest+json")
        if p == "/chat-stream":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            q: queue.Queue = queue.Queue()
            with SSE_LOCK:
                SSE_CLIENTS.append(q)
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
                    if q in SSE_CLIENTS:
                        SSE_CLIENTS.remove(q)
            return
        if p == "/chat":
            try:
                return self._send(200, render_chat())
            except Exception as e:  # noqa: BLE001
                return self._send(500, f"<pre>{html.escape(str(e))}</pre>")
        did = DEFAULT_DOC if p in ("/",) else (p[len("/doc/"):].strip("/") if p.startswith("/doc/") else None)
        if did:
            try:
                self._send(200, render_page(did))
            except Exception as e:  # noqa: BLE001
                self._send(500, f"<pre>{html.escape(str(e))}</pre>")
        else:
            self._send(404, "not found")

    def do_POST(self):
        if self.path not in ("/", "/comment", "/comment-edit", "/comment-delete", "/chat-send"):
            self._send(404, "not found"); return
        try:
            n = int(self.headers.get("Content-Length", 0))
            d = json.loads(self.rfile.read(n) or b"{}")
            if self.path == "/":
                # channel INJECT RECEIVER — the fabric pushed to 'tim' (this app). Body = {content, meta}.
                meta = d.get("meta", {}) or {}
                content = d.get("content", "") or ""
                frm = meta.get("from", "Vi")
                if meta.get("kind") == "status":   # ephemeral status (e.g. "reading your comments…") — not stored
                    broadcast({"kind": "status", "who": ("You" if frm == OPERATOR_HANDLE else "Vi"), "body": content})
                    self._send(200, json.dumps({"ok": True}), "application/json"); return
                rec = cb.file_item("message", (content[:54] or "reply"), content, frm, channel=CHANNEL)
                broadcast(_msg_payload(rec))
                self._send(200, json.dumps({"ok": True}), "application/json"); return
            if self.path == "/chat-send":
                body = (d.get("body", "") or "").strip()
                if not body and not d.get("image_b64"):
                    self._send(400, json.dumps({"ok": False, "error": "empty"}), "application/json"); return
                rec = cb.file_item("message", (body[:54] or "image"), body or "(image)", AUTHOR, channel=CHANNEL)
                if d.get("image_b64"):
                    raw = base64.b64decode(d["image_b64"].split(",")[-1])
                    irec = ci.save_image(STORE, raw, channel=CHANNEL, path=f"chat/{rec['id']}",
                                         mime=d.get("image_mime", "image/jpeg"), author_session=AUTHOR)
                    rec = cb.edit_item(rec["id"], add_links=[{"kind": "attachment", "target": irec["address"]}])
                broadcast(_msg_payload(rec))   # live-echo your own message to all open chat views
                # inject into the lead's LIVE session via the channel transport (no polling, no sit)
                delivered = False
                try:
                    target = open(LEAD_TARGET_FILE).read().strip() if os.path.exists(LEAD_TARGET_FILE) else ""
                    if target:
                        r = cc.send(target, f"[Tim — via the app chat]\n\n{body or '(image attached)'}",
                                    frm="tim", thread="dragdev-chat")
                        delivered = bool(r.get("ok"))
                except Exception:  # noqa: BLE001 — message is saved regardless; delivery is best-effort
                    delivered = False
                self._send(200, json.dumps({"ok": True, "delivered": delivered}), "application/json"); return
            if self.path == "/comment":
                addr, scale = d.get("addr", ""), d.get("scale", "highlight")
                quote = (d.get("quote", "") or "").strip(); body = (d.get("body", "") or "").strip()
                send_now = bool(d.get("send_now"))
                if not addr or not body:
                    self._send(400, json.dumps({"ok": False, "error": "missing addr or body"}), "application/json"); return
                anchor = f"[{scale}{' · SEND-NOW' if send_now else ''}]" + (f' re: «{quote}»' if quote else "")
                rec = cb.comment(addr, f"{anchor}\n\n{body}", AUTHOR, title=f"Tim · {scale}", channel=CHANNEL)
                img_b64 = d.get("image_b64")
                if img_b64:
                    raw = base64.b64decode(img_b64.split(",")[-1])
                    irec = ci.save_image(STORE, raw, channel=CHANNEL, path=f"comment/{rec['id']}",
                                         mime=d.get("image_mime", "image/jpeg"), author_session=AUTHOR)
                    cb.edit_item(rec["id"], add_links=[{"kind": "attachment", "target": irec["address"]}])
                self._send(200, json.dumps({"ok": True, "comment": rec["address"]}), "application/json"); return
            if self.path == "/comment-edit":
                cid = d.get("id", ""); newtext = (d.get("body", "") or "").strip()
                if not cid or not newtext:
                    self._send(400, json.dumps({"ok": False, "error": "missing id or body"}), "application/json"); return
                rec = cb.get_item(cid)
                scale, quote, _ = parse_comment(rec.get("body", ""))
                anchor = f"[{scale}]" + (f' re: «{quote}»' if quote else "")
                cb.edit_item(cid, body=f"{anchor}\n\n{newtext}", by=AUTHOR, note="edit comment")
                self._send(200, json.dumps({"ok": True}), "application/json"); return
            if self.path == "/comment-delete":
                cid = d.get("id", "")
                p = os.path.join(cb.NOTICEBOARD_DIR, f"{cid}.md")
                if cid and os.path.exists(p):
                    os.remove(p)
                    self._send(200, json.dumps({"ok": True}), "application/json"); return
                self._send(400, json.dumps({"ok": False, "error": "comment not found"}), "application/json"); return
        except Exception as e:  # noqa: BLE001
            self._send(500, json.dumps({"ok": False, "error": str(e)}), "application/json")


def main():
    global AUTHOR
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8781)
    ap.add_argument("--author", default=AUTHOR)
    args = ap.parse_args()
    AUTHOR = args.author
    register_operator(args.port)   # register the app as a pushable channel member ('tim')
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"doc-review server on http://127.0.0.1:{args.port}  (channel={CHANNEL}, author={AUTHOR}, operator=tim@{args.port})", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
