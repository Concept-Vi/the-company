import json, os, concurrent.futures as cf, urllib.request, urllib.error, time, subprocess
ROOT="/mnt/c/Users/Workstation001/Documents/Claude/Projects/Visual Designer"
OUT=os.path.expanduser("~/wizard-run-1/extract.jsonl")
URL="http://localhost:8000/v1/chat/completions"; MODEL="cyankiwi/Qwen3.5-4B-AWQ-4bit"
SYS=("Read ONE markdown file from a SCATTERED, AI-GENERATED, never-reviewed project corpus. "
"Much was never built; expect gaps, contradictions, half-ideas. Read the WHOLE file. Extract STRICT JSON only:\n"
"{\"what\":\"<=15-word what this file is\",\"intent\":\"<=30-word what it's REACHING FOR (goal/vision behind it)\","
"\"components\":[\"named things/capabilities it introduces\"],\"decisions\":[\"choices it states as made\"],"
"\"open_questions\":[\"things it flags as unresolved\"],"
"\"gaps_or_contradictions\":[\"things missing, conflicting, or that don't add up\"],"
"\"latent_or_abandoned\":[\"ideas it gestures at but never designs/finishes — half-thoughts worth surfacing\"]}\n"
"Faithful: if sparse, few items; if rich, capture it ALL. Do NOT invent coherence. Capture the REACH even when detail can't be trusted.")
def call(payload, guided):
    d={"model":MODEL,"messages":[{"role":"system","content":SYS},{"role":"user","content":payload}],"max_tokens":2000,"temperature":0}
    if guided: d["response_format"]={"type":"json_object"}
    req=urllib.request.Request(URL,data=json.dumps(d).encode(),headers={"Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(req,timeout=240).read())["choices"][0]["message"]["content"]
def extract(path):
    rel=path.replace(ROOT+"/","")
    try:
        with open(path,'r',encoding='utf-8',errors='ignore') as f: txt=f.read(115000)
    except Exception as e: return {"rel":rel,"error":f"read:{e}"}
    if len(txt.strip())<40: return {"rel":rel,"what":"(near-empty)","intent":"","components":[],"decisions":[],"open_questions":[],"gaps_or_contradictions":[],"latent_or_abandoned":[]}
    payload=f"PATH: {rel}\n\n{txt}"
    for attempt in range(4):
        try:
            rec=json.loads(call(payload, attempt<2)); rec["rel"]=rel; return rec
        except urllib.error.HTTPError as e:
            if attempt<3: time.sleep(2); continue
            return {"rel":rel,"error":f"HTTP {e.code}"}
        except Exception as e:
            if attempt==3: return {"rel":rel,"error":str(e)[:80]}
            time.sleep(2)
allmd=subprocess.run(["bash","-c",f"find '{ROOT}' -type f -iname '*.md' 2>/dev/null | grep -vE '/node_modules/|/\\.git/'"],capture_output=True,text=True).stdout.splitlines()
done=set(); keep=[]
if os.path.exists(OUT):
    for line in open(OUT):
        try:
            r=json.loads(line)
            if "error" not in r and r.get("what")!="(near-empty)": done.add(r["rel"]); keep.append(line)
        except: pass
    open(OUT,"w").writelines(keep)
files=[p for p in allmd if p.replace(ROOT+"/","") not in done]
print(f"to-extract: {len(files)} (good-done: {len(done)})",flush=True)
t0=time.time(); n=0
with open(OUT,"a") as out, cf.ThreadPoolExecutor(max_workers=8) as ex:
    for rec in ex.map(extract, files):
        out.write(json.dumps(rec)+"\n"); out.flush(); n+=1
        if n%100==0: print(f"  {n}/{len(files)} ({time.time()-t0:.0f}s)",flush=True)
print(f"DONE {n} in {time.time()-t0:.0f}s",flush=True)
