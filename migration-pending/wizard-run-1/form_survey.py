import json, os, concurrent.futures as cf, urllib.request, urllib.error, time
ROOT="/mnt/c/Users/Workstation001/Documents/Claude/Projects/Visual Designer"
OUT=os.path.expanduser("~/wizard-run-1/form_survey.jsonl")
URL="http://localhost:8000/v1/chat/completions"; MODEL="cyankiwi/Qwen3.5-4B-AWQ-4bit"
SYS=("Characterize the FORM/SHAPE of ONE file from a scattered AI-generated project (NOT what it means — what KIND "
"of thing it is and what a LOSSLESS capture of it would need). STRICT JSON only:\n"
"{\"content_form\":\"<best fit, coin a new one if needed: prose-design|schema-or-contract|decision-card|transcript-or-dialogue|status-or-log|checklist-or-criteria|math-proof|template-or-skeleton|index-or-moc|data-dump|tutorial-howto|mixed|other>\","
"\"format_features\":[\"structural features present: frontmatter, embedded-json, code-blocks, tables, mermaid, wikilinks, yaml, numbered-steps, etc.\"],"
"\"capture_needs\":[\"what fields/structure a LOSSLESS reconstruction of THIS file's value would require — be specific to what's actually in it\"]}")
def call(p,g):
    d={"model":MODEL,"messages":[{"role":"system","content":SYS},{"role":"user","content":p}],"max_tokens":500,"temperature":0}
    if g: d["response_format"]={"type":"json_object"}
    return json.loads(urllib.request.urlopen(urllib.request.Request(URL,data=json.dumps(d).encode(),headers={"Content-Type":"application/json"}),timeout=150).read())["choices"][0]["message"]["content"]
def survey(rel):
    path=ROOT+"/"+rel
    try:
        with open(path,encoding='utf-8',errors='ignore') as f: txt=f.read(40000)
    except Exception as e: return {"rel":rel,"error":str(e)[:50]}
    if len(txt.strip())<30: return {"rel":rel,"content_form":"empty","format_features":[],"capture_needs":[]}
    for a in range(4):
        try:
            r=json.loads(call(f"PATH: {rel}\n\n{txt}",a<2)); r["rel"]=rel; return r
        except urllib.error.HTTPError as e:
            if a<3: time.sleep(2); continue
            return {"rel":rel,"error":f"HTTP {e.code}"}
        except Exception as e:
            if a==3: return {"rel":rel,"error":str(e)[:50]}
            time.sleep(2)
reps=set()
for c in json.load(open("carve.json")):
    for m in c["member_rels"]: reps.add(m)
reps=sorted(reps)
done=set(); keep=[]
if os.path.exists(OUT):
    for l in open(OUT):
        try:
            r=json.loads(l)
            if "error" not in r: done.add(r["rel"]); keep.append(l)
        except: pass
    open(OUT,"w").writelines(keep)
todo=[r for r in reps if r not in done]
print(f"form-survey: {len(todo)} reps (done {len(done)})",flush=True)
t0=time.time(); n=0
with open(OUT,"a") as out, cf.ThreadPoolExecutor(max_workers=8) as ex:
    for rec in ex.map(survey, todo):
        out.write(json.dumps(rec)+"\n"); out.flush(); n+=1
        if n%100==0: print(f"  {n}/{len(todo)} ({time.time()-t0:.0f}s)",flush=True)
print(f"DONE {n} in {time.time()-t0:.0f}s",flush=True)
