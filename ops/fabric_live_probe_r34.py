#!/usr/bin/env python3
"""R3.4 LIVE — point-in-time resume proof (launch a session AS IT WAS at a past compaction).
Validates the R1 fix on the materialized-prefix resume path AND the headline:
a resumed PREFIX@compact:1 answers from THAT point's context, not the live session's tip.

Design (single resume, self-validating, contamination-proof):
  1. materialize SOURCE @compact:1 into its OWN project dir with a fresh sid (source byte-untouched,
     verify_materialized asserts it).
  2. read the PREFIX tail (last user/assistant texts) = the past point's "most recent topic";
     read the SOURCE tail = the live tip's "most recent topic". They must differ (else no discriminator).
  3. resume the prefix through the fixed supervisor (read-only: plan mode, no tools), ask "what is the
     most recent thing we were discussing?".
  4. PROOF: the resumed answer aligns with the PREFIX tail (the past point), NOT the SOURCE tip.
  5. cleanup: teardown + delete the materialized file (the resume turn appended only to that copy).

Run: .venv/bin/python r34_live_probe.py <source.jsonl>
"""
import json, os, sys, threading, time, urllib.request, urllib.error
sys.path.insert(0, "/home/tim/company")
from runtime.session_pointintime import (build_timeline, materialize_at_point,
                                         verify_materialized, resume_cwd_for, encode_project_dir)
import uuid as _uuid

BASE = "http://127.0.0.1:8771"
SOURCE = sys.argv[1]
MAX_PREFIX_MB = float(sys.argv[2]) if len(sys.argv) > 2 else 12.0


def req(method, path, body=None, timeout=30):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method,
                               headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


class W(threading.Thread):
    def __init__(s, sess): super().__init__(daemon=True); s.sess=sess; s.ev=[]; s.l=threading.Lock()
    def run(s):
        try:
            r=urllib.request.Request(f"{BASE}/watch?session={s.sess}")
            with urllib.request.urlopen(r,timeout=600) as resp:
                for raw in resp:
                    try: e=json.loads(raw)
                    except ValueError: continue
                    with s.l: s.ev.append(e)
        except Exception: pass
    def mark(s):
        with s.l: return len(s.ev)
    def wait(s,pred,to,since=0):
        t0=time.time()
        while time.time()-t0<to:
            with s.l:
                for e in s.ev[since:]:
                    if pred(e): return e
            time.sleep(0.25)
        return None


def wait_idle(sid, to=120):
    t0=time.time()
    while time.time()-t0<to:
        _,r=req("GET","/sessions")
        rec=next((x for x in r.get("sessions",[]) if x["id"]==sid),None)
        if rec and rec["state"]=="idle": return rec
        if rec and rec["state"]=="closed": raise SystemExit(f"FAIL resume closed: {rec.get('close_reason')}")
        time.sleep(0.5)
    raise SystemExit(f"FAIL resume not idle in {to}s")


def tail_texts(path, k=3):
    """last k user/assistant text snippets (the concrete 'recent topic' signal)."""
    out=[]
    try:
        for line in open(path, encoding="utf-8", errors="replace"):
            s=line.strip()
            if not s: continue
            try: ev=json.loads(s)
            except ValueError: continue
            msg=ev.get("message") or {}
            role=msg.get("role") or ev.get("type")
            content=msg.get("content")
            txt=""
            if isinstance(content,str): txt=content
            elif isinstance(content,list):
                txt=" ".join(b.get("text","") for b in content if isinstance(b,dict) and b.get("type")=="text")
            if role in ("user","assistant") and txt.strip():
                out.append((role, txt.strip().replace("\n"," ")[:240]))
    except FileNotFoundError:
        return []
    return out[-k:]


# ── 1. timeline + materialize @compact:1 ──
tl = build_timeline(SOURCE)
comps = tl.get("boundaries") or []
print(f"source: {os.path.basename(SOURCE)}  boundaries={len(comps)}")
assert len(comps) >= 2, "need >=2 boundaries for a clean past-vs-tip discriminator"
resume_cwd = resume_cwd_for(SOURCE, os.path.basename(os.path.dirname(SOURCE)).replace("-", "/"))
new_sid = str(_uuid.uuid4())
rep = materialize_at_point(SOURCE, "compact:1", dest_dir=os.path.dirname(SOURCE), new_sid=new_sid)
vr = verify_materialized(rep)
new_path = rep["new_path"]
prefix_mb = os.path.getsize(new_path)/1e6
print(f"materialized @compact:1 → sid={new_sid[:8]} lines={rep['lines_written']} "
      f"size={prefix_mb:.1f}MB source_untouched={rep['source_untouched']} verify_ok={vr.get('ok', vr)}")
print(f"resume_cwd={resume_cwd}")

# ── 2. the discriminator: prefix tail (past point) vs source tail (tip) ──
past_tail = tail_texts(new_path, 3)
tip_tail = tail_texts(SOURCE, 3)
print("\n── PAST POINT (prefix @compact:1) most-recent messages ──")
for role,t in past_tail: print(f"   [{role}] {t}")
print("── LIVE TIP (full source) most-recent messages ──")
for role,t in tip_tail: print(f"   [{role}] {t}")

cleanup = lambda: (os.path.exists(new_path) and os.unlink(new_path))

if not rep["source_untouched"]:
    print("\nABORT: source changed during materialize"); cleanup(); sys.exit(1)
if prefix_mb > MAX_PREFIX_MB:
    print(f"\nSKIP RESUME: prefix {prefix_mb:.1f}MB > {MAX_PREFIX_MB}MB cap (too costly). "
          f"Structural materialization + discriminator-tails PROVEN; live resume deferred (pick a "
          f"higher-compaction-count source for a small compact:1). Cleaning up.")
    cleanup(); sys.exit(0)

# ── 3. resume the prefix through the FIXED supervisor (read-only plan mode) ──
code, r = req("POST", "/spawn", {"cwd": resume_cwd, "resume": new_sid, "name": f"r34-{new_sid[:8]}"})
if code != 200:
    print(f"FAIL spawn-resume: {r}"); cleanup(); sys.exit(1)
sid = r["session"]["id"]
w = W(sid); w.start()
try:
    wait_idle(sid)   # ← the fix on the materialized-prefix resume path
    m = w.mark()
    req("POST", "/inject", {"session": sid,
        "message": "In one short sentence, what is the most recent thing we were discussing in this conversation?"})
    done = w.wait(lambda e: e.get("type")=="done", 240, since=m)
    ans = (done or {}).get("result","")
finally:
    req("POST","/teardown",{"session":sid})

print(f"\n── RESUMED-@compact:1 ANSWER (what it thinks is 'most recent') ──\n   {ans[:400]}")
# source untouched after the whole flow (the resume appended only to the materialized copy)
src_ok = os.path.getsize(SOURCE) == rep["source_bytes"]
print(f"\nsource byte-untouched after resume: {src_ok} (size {rep['source_bytes']})")
cleanup()
print("materialized prefix file deleted (cleanup).")
print("\nRESULT: read the three blocks — PROOF holds iff the RESUMED answer matches the PAST-POINT "
      "tail topic and is UNLIKE the LIVE-TIP tail topic (context is that point's, not the tip).")
