import json, os, concurrent.futures as cf, urllib.request, urllib.error, time, subprocess
ROOT="/mnt/c/Users/Workstation001/Documents/Claude/Projects/Visual Designer"
OUT=os.path.expanduser("~/wizard-run-1/code_extract.jsonl")
URL="http://localhost:8000/v1/chat/completions"; MODEL="cyankiwi/Qwen3.5-4B-AWQ-4bit"
SYS=("Read ONE source-code file from a scattered AI-generated project. Judge what is ACTUALLY IMPLEMENTED vs "
"stubbed/aspirational. STRICT JSON only:\n{\"what\":\"<=15-word what this file does\","
"\"real_or_stub\":\"real-working|partial|stub|scaffold\",\"implements\":[\"concrete capabilities/functions it really provides\"],"
"\"connects_to\":[\"external services/modules/APIs it calls (supabase, elevenlabs, twilio, mcp, etc.)\"],"
"\"notable\":[\"anything notable: TODO, broken, missing, or genuinely solid\"]}\nBe honest: AI-written code often LOOKS done but is stub.")
def call(payload, guided):
    d={"model":MODEL,"messages":[{"role":"system","content":SYS},{"role":"user","content":payload}],"max_tokens":1000,"temperature":0}
    if guided: d["response_format"]={"type":"json_object"}
    req=urllib.request.Request(URL,data=json.dumps(d).encode(),headers={"Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(req,timeout=180).read())["choices"][0]["message"]["content"]
def ex1(path):
    rel=path.replace(ROOT+"/","")
    try:
        with open(path,'r',encoding='utf-8',errors='ignore') as f: txt=f.read(60000)
    except Exception as e: return {"rel":rel,"error":str(e)[:60]}
    if len(txt.strip())<20: return {"rel":rel,"what":"(empty)","real_or_stub":"stub","implements":[],"connects_to":[],"notable":[]}
    for a in range(4):
        try:
            rec=json.loads(call(f"PATH: {rel}\n\n{txt}", a<2)); rec["rel"]=rel; return rec
        except urllib.error.HTTPError as e:
            if a<3: time.sleep(2); continue
            return {"rel":rel,"error":f"HTTP {e.code}"}
        except Exception as e:
            if a==3: return {"rel":rel,"error":str(e)[:60]}
            time.sleep(2)
# real code, exclude node_modules/dist/generated/snapshots/.obsidian
code=subprocess.run(["bash","-c",f"find '{ROOT}' -type f 2>/dev/null | grep -vE '/node_modules/|/\\.git/|/dist/|/build/|/_system/snapshots/|/\\.obsidian/' | grep -iE '\\.(ts|tsx|py|js|mjs|sql)$'"],capture_output=True,text=True).stdout.splitlines()
done=set(); keep=[]
if os.path.exists(OUT):
    for l in open(OUT):
        try:
            r=json.loads(l)
            if "error" not in r: done.add(r["rel"]); keep.append(l)
        except: pass
    open(OUT,"w").writelines(keep)
files=[p for p in code if p.replace(ROOT+"/","") not in done]
print(f"code to-extract: {len(files)} (done {len(done)})",flush=True)
t0=time.time(); n=0
with open(OUT,"a") as out, cf.ThreadPoolExecutor(max_workers=6) as exr:
    for rec in exr.map(ex1, files):
        out.write(json.dumps(rec)+"\n"); out.flush(); n+=1
        if n%50==0: print(f"  {n}/{len(files)} ({time.time()-t0:.0f}s)",flush=True)
print(f"DONE {n} in {time.time()-t0:.0f}s",flush=True)
