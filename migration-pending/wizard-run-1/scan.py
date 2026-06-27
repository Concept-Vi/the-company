import json, os, concurrent.futures as cf, urllib.request, time

ROOT="/mnt/c/Users/Workstation001/Documents/Claude/Projects/Visual Designer"
MANIFEST=os.path.expanduser("~/wizard-run-1/manifest_full.txt")
OUT=os.path.expanduser("~/wizard-run-1/scan.jsonl")
URL="http://localhost:8000/v1/chat/completions"
MODEL="cyankiwi/Qwen3.5-4B-AWQ-4bit"

KINDS="design-spec, intent-vision, architecture, decision-record, research, process-meta, build-status, glossary-ref, config-data, code, test, schema-migration, notes, other"
DOMAINS="voice-audio, telephony, agent-identity, knowledge-corpus, campaign-batch, compliance-consent, secrets-payment, ui-surface, mcp-tools, post-call-proof, workspace-infra, business-gtm, other"

SYS=("Classify ONE file of a voice-agent project by WHAT IT IS (never relevance). "
"Return STRICT JSON only: {\"kind\":\"<one of: %s>\",\"domain\":\"<one of: %s>\",\"role\":\"<≤12-word what-this-file-is>\",\"built\":\"<code-that-runs|design-only|generated|unclear>\"}. "
"Most files are markdown design/intent, not code — judge accordingly." % (KINDS,DOMAINS))

def classify(path):
    rel=path.replace(ROOT+"/","")
    try:
        with open(path,'r',encoding='utf-8',errors='ignore') as f: head=f.read(8000)
    except Exception as e: return {"rel":rel,"error":f"read:{e}"}
    body=json.dumps({"model":MODEL,"messages":[{"role":"system","content":SYS},
        {"role":"user","content":f"PATH: {rel}\n\nOPENING:\n{head}"}],
        "max_tokens":160,"temperature":0,"response_format":{"type":"json_object"}}).encode()
    for attempt in range(3):
        try:
            req=urllib.request.Request(URL,data=body,headers={"Content-Type":"application/json"})
            r=urllib.request.urlopen(req,timeout=90).read()
            txt=json.loads(r)["choices"][0]["message"]["content"]
            rec=json.loads(txt); rec["rel"]=rel; return rec
        except Exception as e:
            if attempt==2: return {"rel":rel,"error":str(e)[:120]}
            time.sleep(1)

done=set()
if os.path.exists(OUT):
    for line in open(OUT):
        try: done.add(json.loads(line)["rel"])
        except: pass
files=[l.strip() for l in open(MANIFEST) if l.strip() and l.strip().replace(ROOT+"/","") not in done]
print(f"to-scan: {len(files)} (already done: {len(done)})", flush=True)

t0=time.time(); n=0
with open(OUT,"a") as out, cf.ThreadPoolExecutor(max_workers=24) as ex:
    for rec in ex.map(classify, files):
        out.write(json.dumps(rec)+"\n"); out.flush(); n+=1
        if n%50==0: print(f"  {n}/{len(files)}  ({time.time()-t0:.0f}s)", flush=True)
print(f"DONE {n} files in {time.time()-t0:.0f}s", flush=True)
