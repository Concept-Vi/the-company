import json, os, concurrent.futures as cf, urllib.request, urllib.error, time
ROOT="/mnt/c/Users/Workstation001/Documents/Claude/Projects/Visual Designer"
OUT=os.path.expanduser("~/wizard-run-1/target_extract.jsonl")
URL="http://localhost:8000/v1/chat/completions"; MODEL="cyankiwi/Qwen3.5-4B-AWQ-4bit"
SYS=("You are reconstructing a UNIVERSAL AGENT-DRIVEN INTERFACE SYSTEM (a 'wizard-of-wizards' — agent-generates-the-UI, "
"provider-agnostic; ElevenLabs outbound-voice is ONE application of it) toward a FINISHED, DEPLOYED product, from "
"scattered AI-written design docs. Read the WHOLE file. Extract STRICT JSON only:\n"
"{\"system_role\":\"<=25-word how THIS file contributes to the universal agent-interface system\","
"\"purpose\":\"<=25-word what it's for\","
"\"mechanisms\":[\"concrete mechanisms/how-it-works it defines\"],"
"\"capabilities_or_domains\":[\"product capabilities/domains it covers\"],"
"\"contracts_or_datamodels\":[\"schemas, contracts, data models, registries it defines\"],"
"\"ui_or_interaction\":[\"UI/interaction/surface model it describes\"],"
"\"product_requirements\":[\"what a SHIPPED product needs that this implies (auth, telephony, consent, billing, deploy, etc.)\"],"
"\"unresolved_or_undocumented\":[\"things needed but missing/undefined/half-done\"]}\n"
"Faithful; capture the REACH; flag what's missing. Detail can't be trusted but the design intent is the signal.")
def call(p,g):
    d={"model":MODEL,"messages":[{"role":"system","content":SYS},{"role":"user","content":p}],"max_tokens":1600,"temperature":0}
    if g: d["response_format"]={"type":"json_object"}
    return json.loads(urllib.request.urlopen(urllib.request.Request(URL,data=json.dumps(d).encode(),headers={"Content-Type":"application/json"}),timeout=200).read())["choices"][0]["message"]["content"]
def ex(path):
    rel=path.replace(ROOT+"/","")
    try:
        with open(path,encoding='utf-8',errors='ignore') as f: txt=f.read(110000)
    except Exception as e: return {"rel":rel,"error":str(e)[:60]}
    if len(txt.strip())<40: return {"rel":rel,"skip":1}
    for a in range(4):
        try:
            r=json.loads(call(f"PATH: {rel}\n\n{txt}",a<2)); r["rel"]=rel; return r
        except urllib.error.HTTPError as e:
            if a<3: time.sleep(2); continue
            return {"rel":rel,"error":f"HTTP {e.code}"}
        except Exception as e:
            if a==3: return {"rel":rel,"error":str(e)[:60]}
            time.sleep(2)
# target-defining files (dedup by basename to skip mirrored copies)
import json as J
hi={'architecture','intent-vision','vision','synthesis'}
seen_base=set(); files=[]
for l in open(os.path.expanduser("~/wizard-run-1/scan.jsonl")):
    try:
        r=J.loads(l); rel=r['rel']
        kw=any(k in rel.lower() for k in ['architecture','universal','agent-interface','wizard-system','vision','complete','operating-model','system-map','hub-','universalization','strategic','convai','schema','data-model','contract','operational-method'])
        if (r.get('kind') in hi or kw) and rel.endswith('.md'):
            b=rel.split('/')[-1]
            if b not in seen_base: seen_base.add(b); files.append(ROOT+"/"+rel)
    except: pass
done=set()
if os.path.exists(OUT):
    for l in open(OUT):
        try:
            r=J.loads(l)
            if 'error' not in r: done.add(r['rel'])
        except: pass
files=[p for p in files if p.replace(ROOT+"/","") not in done]
print(f"target files to deep-extract: {len(files)} (done {len(done)})",flush=True)
t0=time.time(); n=0
with open(OUT,"a") as out, cf.ThreadPoolExecutor(max_workers=8) as exr:
    for rec in exr.map(ex, files):
        out.write(json.dumps(rec)+"\n"); out.flush(); n+=1
        if n%40==0: print(f"  {n}/{len(files)} ({time.time()-t0:.0f}s)",flush=True)
print(f"DONE {n} in {time.time()-t0:.0f}s",flush=True)
