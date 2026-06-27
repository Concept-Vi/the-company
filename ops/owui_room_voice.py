#!/usr/bin/env python3
"""ops/owui_room_voice.py — VOICE & EARS for the operator room.

OpenWebUI channels are text-only (no mic/playback). This is the bridge that gives the room a voice:
a tiny served page (phone-friendly, HTTPS over Tailscale → secure context → mic works) that

  EARS  : tap-to-talk → browser mic → POST /listen → Company STT (granite/whisper) → the transcript is
          posted INTO the room as Tim → the room routes it to members exactly like a typed message.
  VOICE : the page polls /poll → new member messages → Company TTS (kokoro) → spoken aloud on the phone.

Reuses the proven Company voice stack (voice.stt + the kokoro TTS service) and the existing room daemon
(Tim's transcript is just a normal channel message, so members + member↔member + operator all still work).

Run: OWUI_PASSWORD=… .venv/bin/python ops/owui_room_voice.py    (then `tailscale serve` its port)
"""
from __future__ import annotations
import base64, json, os, sys, time, urllib.request, requests
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from voice import stt as _stt

OWUI = os.environ.get("OWUI_BASE", "http://127.0.0.1:8081")
CHANNEL = os.environ.get("ROOM_OWUI_CHANNEL", "a9a338cc-ede3-4268-a43a-94857e2ad4e6")
EMAIL = os.environ.get("OWUI_EMAIL", "v.i@conceptv.com.au")
PASSWORD = os.environ.get("OWUI_PASSWORD", "")
PORT = int(os.environ.get("ROOM_VOICE_PORT", "8785"))
TTS_PORT = int(os.environ.get("COMPANY_TTS_PORT", "4123"))
STT_PROVIDER = os.environ.get("ROOM_STT", "granite")
TTS_VOICE = os.environ.get("COMPANY_TTS_VOICE", "af_heart")

_token = ""


def signin() -> str:
    r = requests.post(f"{OWUI}/api/v1/auths/signin", json={"email": EMAIL, "password": PASSWORD}, timeout=15)
    r.raise_for_status()
    return r.json()["token"]


def post_to_room(text: str) -> None:
    requests.post(f"{OWUI}/api/v1/channels/{CHANNEL}/messages/post",
                  headers={"Authorization": f"Bearer {_token}"}, json={"content": text}, timeout=15)


def recent_member_messages(since_ms: int) -> list:
    """Member (webhook-authored) messages newer than since_ms (created_at is ns in OWUI)."""
    r = requests.get(f"{OWUI}/api/v1/channels/{CHANNEL}/messages", params={"limit": 20},
                     headers={"Authorization": f"Bearer {_token}"}, timeout=15)
    r.raise_for_status()
    out = []
    for m in (r.json() or []):
        if not m.get("meta"):                                  # skip Tim's own (text-only) messages
            continue
        ts = int(m.get("created_at", 0) // 1_000_000)          # ns → ms
        if ts <= since_ms:
            continue
        who = ((m.get("user") or {}).get("name")) or "member"
        out.append({"ts": ts, "who": who, "text": (m.get("content") or "").strip(), "id": m.get("id")})
    return sorted(out, key=lambda x: x["ts"])


def tts_wav_b64(text: str) -> str:
    body = json.dumps({"text": text[:600], "voice": TTS_VOICE, "speed": 1.0}).encode()
    req = urllib.request.Request(f"http://127.0.0.1:{TTS_PORT}/", data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    return base64.b64encode(urllib.request.urlopen(req, timeout=30).read()).decode()


PAGE = """<!doctype html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Room Voice</title><style>
body{font-family:-apple-system,system-ui,sans-serif;background:#0f1115;color:#e6e8eb;margin:0;padding:18px}
h1{font-size:18px;font-weight:600;margin:0 0 14px}
#talk{width:100%;padding:26px;font-size:20px;border:0;border-radius:16px;background:#2563eb;color:#fff;font-weight:600}
#talk.rec{background:#dc2626}
#log{margin-top:16px;font-size:15px;line-height:1.5}
.me{color:#9ec1ff}.them{color:#a7f3d0}.sys{color:#8b94a3;font-size:13px}
.row{margin:8px 0;padding:8px 12px;background:#171a21;border-radius:10px}
</style></head><body>
<h1>🎙 Room Voice <span class=sys id=status>—</span></h1>
<button id=talk>Tap & hold to talk</button>
<div id=log></div>
<script>
let mr,chunks=[],since=Date.now();
const log=document.getElementById('log'),talk=document.getElementById('talk'),status=document.getElementById('status');
function add(cls,who,t){const d=document.createElement('div');d.className='row';d.innerHTML='<b class="'+cls+'">'+who+':</b> '+t;log.prepend(d);}
async function start(){
  try{const s=await navigator.mediaDevices.getUserMedia({audio:true});
    mr=new MediaRecorder(s);chunks=[];mr.ondataavailable=e=>chunks.push(e.data);
    mr.onstop=send;mr.start();talk.classList.add('rec');talk.textContent='● listening… release to send';status.textContent='listening';
  }catch(e){status.textContent='mic blocked: '+e.message;}
}
async function send(){
  talk.classList.remove('rec');talk.textContent='Tap & hold to talk';status.textContent='transcribing…';
  const blob=new Blob(chunks,{type:'audio/webm'});const fd=new FormData();fd.append('audio',blob,'a.webm');
  const r=await fetch('/listen',{method:'POST',body:blob});const j=await r.json();
  if(j.transcript){add('me','you',j.transcript);status.textContent='sent';}else{status.textContent='no speech';}
}
talk.addEventListener('mousedown',start);talk.addEventListener('touchstart',e=>{e.preventDefault();start();});
talk.addEventListener('mouseup',()=>mr&&mr.state=='recording'&&mr.stop());
talk.addEventListener('touchend',e=>{e.preventDefault();mr&&mr.state=='recording'&&mr.stop();});
async function poll(){
  try{const r=await fetch('/poll?since='+since);const j=await r.json();
    for(const m of j.messages){since=Math.max(since,m.ts+1);add('them',m.who,m.text);
      if(m.audio){const a=new Audio('data:audio/wav;base64,'+m.audio);a.play().catch(()=>{});}}
  }catch(e){}
  setTimeout(poll,2500);
}
status.textContent='ready';poll();
</script></body></html>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/index"):
            b = PAGE.encode()
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        elif self.path.startswith("/poll"):
            try:
                since = int((self.path.split("since=", 1)[1].split("&")[0]) if "since=" in self.path else 0)
            except Exception:
                since = 0
            try:
                msgs = recent_member_messages(since)
                for m in msgs:
                    try:
                        m["audio"] = tts_wav_b64(m["text"])
                    except Exception:
                        m["audio"] = ""
                self._json(200, {"messages": msgs})
            except Exception as e:
                self._json(500, {"error": str(e)})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/listen":
            try:
                n = int(self.headers.get("Content-Length", 0))
                audio = self.rfile.read(n)
                res = _stt.transcribe(audio, provider=STT_PROVIDER)
                text = (res.get("text") or "").strip()
                if text:
                    post_to_room(text)
                self._json(200, {"transcript": text})
            except Exception as e:
                self._json(500, {"error": str(e)})
        else:
            self._json(404, {"error": "not found"})


def main():
    global _token
    if not PASSWORD:
        raise SystemExit("set OWUI_PASSWORD")
    _token = signin()
    print(f"room-voice: page+ears+voice on :{PORT}  (STT={STT_PROVIDER} TTS=:{TTS_PORT} room={CHANNEL})", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()


if __name__ == "__main__":
    raise SystemExit(main())
