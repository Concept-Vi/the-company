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
import argparse, html, json, os, re, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
os.environ.setdefault("COMPANY_STORE", os.path.join(REPO, ".data", "store"))
ASSETS = os.path.join(REPO, "ops", "assets")

from runtime import cc_board as cb  # noqa: E402

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
        if st.startswith("# "):
            out.append(f"<h3>{_inline(st[2:])}</h3>"); i += 1; continue
        if st.startswith("## "):
            out.append(f"<h4>{_inline(st[3:])}</h4>"); i += 1; continue
        if re.match(r"^-{3,}$", st):
            out.append("<hr>"); i += 1; continue
        if st.startswith("> "):
            buf = []
            while i < n and lines[i].strip().startswith("> "):
                buf.append(_inline(lines[i].strip()[2:])); i += 1
            out.append("<blockquote>" + "<br>".join(buf) + "</blockquote>"); continue
        if re.match(r"^[-*] ", st):
            buf = []
            while i < n and re.match(r"^[-*] ", lines[i].strip()):
                buf.append(f"<li>{_inline(lines[i].strip()[2:])}</li>"); i += 1
            out.append("<ul>" + "".join(buf) + "</ul>"); continue
        if re.match(r"^\d+\. ", st):
            buf = []
            while i < n and re.match(r"^\d+\. ", lines[i].strip()):
                buf.append(f"<li>{_inline(re.sub(r'^\\d+\\. ', '', lines[i].strip()))}</li>"); i += 1
            out.append("<ol>" + "".join(buf) + "</ol>"); continue
        buf = []
        while i < n and lines[i].strip() and not re.match(r"^(#{1,3} |[-*] |\d+\. |> |-{3,}$)", lines[i].strip()):
            buf.append(_inline(lines[i].strip())); i += 1
        out.append("<p>" + " ".join(buf) + "</p>")
    return "\n".join(out)


def _thread_html(thread: list) -> str:
    if not thread:
        return ""
    parts = ['<div class="comments">']
    for t in thread:
        c = t["comment"]; who = c.get("author_session", "?")
        cls = "c-tim" if who == AUTHOR else "c-lead"
        parts.append(f'<div class="comment {cls}"><div class="c-who">{html.escape(who)}</div>'
                     f'<div class="c-body">{html.escape(c.get("body", ""))}</div>')
        if t.get("replies"):
            parts.append(_thread_html(t["replies"]))
        parts.append("</div>")
    parts.append("</div>")
    return "".join(parts)


def list_docs() -> list:
    docs = [i for i in cb.list_items(type="document") if i.get("channel") == CHANNEL]
    docs.sort(key=lambda d: d.get("created", ""))
    return docs


def short_label(title: str) -> str:
    return (title.split("—")[0].strip() or title)[:32]


def _docnav_html(current_id: str) -> str:
    out = ['<div class="drawer-title">Documents</div>']
    for d in list_docs():
        cur = " current" if d.get("id") == current_id else ""
        out.append(f'<a class="doc-link{cur}" href="/doc/{html.escape(d["id"])}">{html.escape(d.get("title", "(untitled)"))}</a>')
    return "".join(out)


def render_page(doc_id: str) -> str:
    asm = cb.assemble_document(doc_id)
    doc = asm["document"]; doc_addr = doc["address"]
    blocks_html = []
    for b in asm["blocks"]:
        key = (b["title"].split(" · ")[0]) if " · " in b["title"] else b["title"]
        title = b["title"].split(" · ", 1)[-1]
        blocks_html.append(f'''
        <section class="block" data-addr="{html.escape(b["address"])}" data-key="{html.escape(key)}">
          <div class="block-head">
            <span class="block-key">{html.escape(key)}</span>
            <span class="sec-actions">
              <button class="sec-comment iconbtn xs" data-addr="{html.escape(b["address"])}" data-key="{html.escape(key)}" aria-label="comment on {html.escape(key)}">{IC["bubble"]}</button>
            </span>
          </div>
          <h2 class="block-title">{_inline(title)}</h2>
          <div class="block-body">{md_to_html(b["body"])}</div>
          {_thread_html(b["thread"])}
        </section>''')
    return (PAGE
            .replace("{{TITLE}}", html.escape(doc.get("title", "Document")))
            .replace("{{SHORT}}", html.escape(short_label(doc.get("title", "Document"))))
            .replace("{{DOC_ADDR}}", html.escape(doc_addr))
            .replace("{{DOC_THREAD}}", _thread_html(asm.get("doc_thread", [])))
            .replace("{{DOCNAV}}", _docnav_html(doc_id))
            .replace("{{BLOCKS}}", "\n".join(blocks_html))
            .replace("{{COUNT}}", str(asm["block_count"])))


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
  #drawer{position:fixed;top:0;left:0;bottom:0;width:82%;max-width:330px;z-index:28;background:var(--paper);
        border-right:1px solid var(--line);box-shadow:4px 0 24px rgba(0,0,0,.16);transform:translateX(-105%);
        transition:transform .22s ease;padding:calc(18px + env(safe-area-inset-top)) 14px 18px;overflow:auto}
  #drawer.open{transform:translateX(0)}
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
  .comments{margin:12px 0 0;display:flex;flex-direction:column;gap:8px}
  .comment{border-radius:10px;padding:10px 12px;font-size:14.5px;line-height:1.5}
  .comment.c-tim{background:#eef5f0;border:1px solid #cfe3d6}
  .comment.c-lead{background:#eef1f7;border:1px solid #d2dbeb}
  .comment .comments{margin-left:12px;border-left:2px solid var(--line);padding-left:10px}
  .c-who{font:600 11px/1 ui-monospace,monospace;color:var(--muted);margin-bottom:4px}
  .c-body{white-space:pre-wrap}
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
  #cancel{margin-right:auto}
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
  <div class="crow">
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
  // tap empty bar area -> expand/collapse the "more" panel
  bar.addEventListener('click',function(e){ if(e.target===bar||e.target.classList.contains('barrow')) bar.classList.toggle('collapsed'); });
})();
(function(){ // commenting
  var pending=null,lastSel=null;
  var sheet=document.getElementById('sheet'),scope=document.getElementById('scope'),
      ctext=document.getElementById('ctext'),toast=document.getElementById('toast');
  function showToast(m,bad){toast.textContent=m;toast.style.background=bad?'#9a3b2b':'#2f6f4f';toast.style.display='block';setTimeout(function(){toast.style.display='none';},2200);}
  function clearSel(){ if(lastSel){lastSel.classList.remove('sel');lastSel=null;} }
  function grow(){ ctext.style.height='auto'; ctext.style.height=Math.min(ctext.scrollHeight,window.innerHeight*0.4)+'px'; }
  ctext.addEventListener('input',grow);
  function openSheet(p){pending=p;scope.textContent=p.scale+' · '+(p.key||'document');ctext.value='';sheet.classList.add('open');setTimeout(function(){grow();ctext.focus();},250);}
  function closeSheet(){sheet.classList.remove('open');pending=null;clearSel();}
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
    if(!pending)return; var body=ctext.value.trim(); if(!body){showToast('Write a comment first',true);return;}
    fetch('/comment',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({addr:pending.addr,key:pending.key,scale:pending.scale,quote:pending.quote,body:body,send_now:!!sendNow})})
     .then(function(r){return r.json();}).then(function(j){
        if(j.ok){closeSheet();showToast(sendNow?'Sent ✓':'Saved ✓');setTimeout(function(){location.reload();},650);}
        else{showToast(j.error||'Failed',true);}
     }).catch(function(){showToast('Network error',true);});
  }
  document.getElementById('post').addEventListener('click',function(){submit(false);});
  document.getElementById('send').addEventListener('click',function(){submit(true);});
})();
</script></body></html>"""
for _k, _v in IC.items():
    PAGE = PAGE.replace("__" + _k.upper() + "__", _v)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

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
        if p == "/manifest.webmanifest":
            man = {"name": "Vi — Review", "short_name": "Vi Review", "display": "standalone",
                   "background_color": BG, "theme_color": BG, "start_url": "/",
                   "icons": [{"src": "/icon-180.png", "sizes": "180x180", "type": "image/png"},
                             {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}]}
            return self._send(200, json.dumps(man), "application/manifest+json")
        did = DEFAULT_DOC if p in ("/",) else (p[len("/doc/"):].strip("/") if p.startswith("/doc/") else None)
        if did:
            try:
                cb.reset_registries()
                self._send(200, render_page(did))
            except Exception as e:  # noqa: BLE001
                self._send(500, f"<pre>{html.escape(str(e))}</pre>")
        else:
            self._send(404, "not found")

    def do_POST(self):
        if self.path != "/comment":
            self._send(404, "not found"); return
        try:
            n = int(self.headers.get("Content-Length", 0))
            d = json.loads(self.rfile.read(n) or b"{}")
            addr, scale = d.get("addr", ""), d.get("scale", "highlight")
            quote = (d.get("quote", "") or "").strip(); body = (d.get("body", "") or "").strip()
            send_now = bool(d.get("send_now"))
            if not addr or not body:
                self._send(400, json.dumps({"ok": False, "error": "missing addr or body"}), "application/json"); return
            anchor = f"[{scale}{' · SEND-NOW' if send_now else ''}]" + (f' re: «{quote}»' if quote else "")
            cb.reset_registries()
            rec = cb.comment(addr, f"{anchor}\n\n{body}", AUTHOR, title=f"Tim · {scale}", channel=CHANNEL)
            self._send(200, json.dumps({"ok": True, "comment": rec["address"]}), "application/json")
        except Exception as e:  # noqa: BLE001
            self._send(500, json.dumps({"ok": False, "error": str(e)}), "application/json")


def main():
    global AUTHOR
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8781)
    ap.add_argument("--author", default=AUTHOR)
    args = ap.parse_args()
    AUTHOR = args.author
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"doc-review server on http://127.0.0.1:{args.port}  (channel={CHANNEL}, author={AUTHOR})", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
