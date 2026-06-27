import json, os, concurrent.futures as cf, urllib.request, time, subprocess
ROOT="/mnt/c/Users/Workstation001/Documents/Claude/Projects/Visual Designer"
OUT=os.path.expanduser("~/wizard-run-1/embed.jsonl")
URL="http://localhost:8001/v1/embeddings"; MODEL="BAAI/bge-m3"
def emb(path):
    rel=path.replace(ROOT+"/","")
    try:
        with open(path,'r',encoding='utf-8',errors='ignore') as f: txt=f.read(3000)
    except Exception as e: return {"rel":rel,"error":str(e)[:80]}
    if len(txt.strip())<30: return {"rel":rel,"skip":1}
    body=json.dumps({"model":MODEL,"input":txt[:3000]}).encode()
    for a in range(3):
        try:
            req=urllib.request.Request(URL,data=body,headers={"Content-Type":"application/json"})
            v=json.loads(urllib.request.urlopen(req,timeout=60).read())["data"][0]["embedding"]
            return {"rel":rel,"v":v}
        except Exception as e:
            if a==2: return {"rel":rel,"error":str(e)[:80]}
            time.sleep(1)
allmd=subprocess.run(["bash","-c",f"find '{ROOT}' -type f -iname '*.md' 2>/dev/null | grep -vE '/node_modules/|/\\.git/'"],capture_output=True,text=True).stdout.splitlines()
done=set()
if os.path.exists(OUT):
    for line in open(OUT):
        try: done.add(json.loads(line)["rel"])
        except: pass
files=[p for p in allmd if p.replace(ROOT+"/","") not in done]
print(f"embed: {len(files)} (done {len(done)})",flush=True)
t0=time.time(); n=0
with open(OUT,"a") as out, cf.ThreadPoolExecutor(max_workers=16) as ex:
    for rec in ex.map(emb, files):
        out.write(json.dumps(rec)+"\n"); out.flush(); n+=1
        if n%200==0: print(f"  {n}/{len(files)} ({time.time()-t0:.0f}s)",flush=True)
print(f"DONE {n} in {time.time()-t0:.0f}s",flush=True)
