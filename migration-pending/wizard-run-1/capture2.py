import json, os, time, concurrent.futures as cf
import db, lift, fleet
ROOT="/mnt/c/Users/Workstation001/Documents/Claude/Projects/Visual Designer"
PROJ=json.load(open("registries/projections.json"))["projections"]
PROMPTS=json.load(open("registries/prompts.json"))
STAGE="legibility"
MODEL_PROJ=[p for p in PROJ if p["produced_by"]=="model" and p.get("stage",STAGE)==STAGE]
CHUNK_CHARS=85000; OVERLAP=10000

def build_schema():
    props={}
    for p in MODEL_PROJ:
        f=p["field"]
        if f=="array": props[p["name"]]={"type":"array","items":{"type":"string"}}
        elif f=="enum": props[p["name"]]={"type":"string","enum":p["enum"]}
        else: props[p["name"]]={"type":"string"}
    return {"type":"object","properties":props,"required":[p["name"] for p in MODEL_PROJ]}
SCHEMA=build_schema()
SYS=PROMPTS["capture.render.v1"]["text"] + "\nProjections to render: " + "; ".join(p["name"]+"="+p["desc"] for p in MODEL_PROJ)

def survey_forms():
    m={}
    for l in open("form_survey.jsonl"):
        try:
            r=json.loads(l)
            if "error" not in r: m[r["rel"]]=r.get("content_form","")
        except: pass
    return m
FORMS=survey_forms()
def is_light(form):
    f=(form or "").lower()
    return ("log" in f or "status" in f or "chronicle" in f or "index" in f or "moc" in f)

def model_render(rel, body, fm_ctx, tag):
    r=fleet.local4b([{"role":"system","content":SYS},
                     {"role":"user","content":f"PATH: {rel}\nFRONTMATTER(context): {fm_ctx}\n\nBODY:\n{body}"}],
                    json_schema=SCHEMA, max_tokens=4000, tag=tag)
    if "error" in r: return None, r["error"]
    try: return json.loads(r["text"]), None
    except Exception as e: return None, f"parse:{e}"

def merge(parts):
    out={}
    for p in MODEL_PROJ:
        n=p["name"]
        if p["field"]=="array":
            seen=[]; 
            for pr in parts:
                for x in (pr.get(n) or []):
                    if x and x not in seen: seen.append(x)
            out[n]=seen
        else:
            vals=[pr.get(n) for pr in parts if pr.get(n)]
            out[n]=max(vals,key=len) if vals else ""
    return out

def capture_one(rel):
    path=ROOT+"/"+rel
    code=lift.lift(path)
    st=os.stat(path)
    rec={"rel":rel,"form":FORMS.get(rel,""),"frontmatter":code["frontmatter"],"has_fm":code["has_fm"],
         "links":code["links"],"blocks":code["blocks"],"size":st.st_size,"mtime":st.st_mtime,"chunked":0,
         "substance":0 if is_light(FORMS.get(rel,"")) else 1}
    if rec["substance"]==0:
        rec["proj"]={}; return rec   # light: code-only (format/lineage/links); no model render
    full=open(path,encoding='utf-8',errors='ignore').read()
    fm_ctx=json.dumps(code["frontmatter"])[:1500]
    if len(full)<=CHUNK_CHARS:
        proj,err=model_render(rel, full, fm_ctx, tag=rel)
        if err: rec["_err"]=err; rec["proj"]={}; return rec
        rec["proj"]=proj
    else:
        rec["chunked"]=1; parts=[]; i=0; ci=0
        while i < len(full):
            chunk=full[i:i+CHUNK_CHARS]
            proj,err=model_render(rel, chunk, fm_ctx, tag=f"{rel}#chunk{ci}")
            if proj: parts.append(proj)
            i += CHUNK_CHARS-OVERLAP; ci+=1
        if not parts: rec["_err"]="all-chunks-failed"; rec["proj"]={}; return rec
        rec["proj"]=merge(parts); rec["_nchunks"]=ci
    return rec

def write_one(c, rec, run_id):
    prin=(rec.get("proj",{}).get("principles") or [""])[0]
    c.execute("""INSERT INTO files(rel,form,frontmatter,has_fm,principle,framing,reach,surface_claims,form_specific,substance,run_id,ts,size,mtime,chunked)
      VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(rel) DO UPDATE SET form=excluded.form,frontmatter=excluded.frontmatter,
      has_fm=excluded.has_fm,principle=excluded.principle,framing=excluded.framing,substance=excluded.substance,run_id=excluded.run_id,
      ts=excluded.ts,size=excluded.size,mtime=excluded.mtime,chunked=excluded.chunked""",
      (rec["rel"],rec["form"],json.dumps(rec["frontmatter"]),int(rec["has_fm"]),prin,
       rec.get("proj",{}).get("framing",""),"", "[]","{}",rec["substance"],run_id,time.time(),
       rec["size"],rec["mtime"],rec["chunked"]))
    for n,v in (rec.get("proj") or {}).items():
        c.execute("INSERT OR REPLACE INTO projections(rel,projection,value,produced_by,run_id) VALUES(?,?,?,?,?)",
                  (rec["rel"],n,json.dumps(v,ensure_ascii=False),"model",run_id))
    c.execute("INSERT OR REPLACE INTO projections(rel,projection,value,produced_by,run_id) VALUES(?,?,?,?,?)",
              (rec["rel"],"format",json.dumps({"has_fm":rec["has_fm"],"fm_keys":list(rec["frontmatter"]),"block_kinds":[b["kind"] for b in rec["blocks"]]}),"code",run_id))
    c.execute("INSERT OR REPLACE INTO projections(rel,projection,value,produced_by,run_id) VALUES(?,?,?,?,?)",
              (rec["rel"],"lineage",json.dumps({"size":rec["size"],"mtime":rec["mtime"]}),"code",run_id))
    for d in rec["links"]: db.add_link(c, rec["rel"], d)
    for b in rec["blocks"]: db.add_block(c, rec["rel"], b["kind"], b["content"])

def run(rels, run_id, workers=6):
    """Resume-safe, write-as-you-go, single-writer. NEVER wipes. Skips already-captured rels."""
    c=db.conn(); db.log_run(c,run_id,"capture2","4b-jsonschema+code",{})
    done={r[0] for r in c.execute("SELECT rel FROM files WHERE substance=0 OR (principle IS NOT NULL AND principle!='')").fetchall()}
    todo=[r for r in rels if r not in done]
    print(f"run {run_id}: {len(todo)} to capture ({len(done)} already done, resume-safe)", flush=True)
    import concurrent.futures as cf
    n=0; t0=time.time()
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs={ex.submit(capture_one, rel): rel for rel in todo}
        for fut in cf.as_completed(futs):
            rec=fut.result()
            write_one(c, rec, run_id)            # WRITE AS EACH COMPLETES (single writer = this thread)
            for e in fleet.CALL_LOG:
                c.execute("INSERT INTO call_log(rel,tag,status,dt,len,empty,err,ts,finish) VALUES(?,?,?,?,?,?,?,?,?)",
                          (e.get("tag",""),e.get("tag",""),e.get("status",""),e.get("dt"),e.get("len"),int(e.get("empty",0)),e.get("err"),time.time(),e.get("finish")))
            fleet.CALL_LOG.clear()
            c.commit()                           # durable per file
            n+=1
            if n%20==0: print(f"  {n}/{len(todo)} ({time.time()-t0:.0f}s)", flush=True)
    c.close()
    return n

def _old_write(recs, run_id):
    c=db.conn(); db.log_run(c,run_id,"capture2","4b-jsonschema+code",{})
    for rec in recs:
        # files row (primary 'principle' col gets first principle for convenience; full set in projections table)
        prin=(rec.get("proj",{}).get("principles") or [""])[0]
        c.execute("""INSERT INTO files(rel,form,frontmatter,has_fm,principle,framing,reach,surface_claims,form_specific,substance,run_id,ts,size,mtime,chunked)
          VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(rel) DO UPDATE SET form=excluded.form,frontmatter=excluded.frontmatter,
          has_fm=excluded.has_fm,principle=excluded.principle,framing=excluded.framing,substance=excluded.substance,run_id=excluded.run_id,
          ts=excluded.ts,size=excluded.size,mtime=excluded.mtime,chunked=excluded.chunked""",
          (rec["rel"],rec["form"],json.dumps(rec["frontmatter"]),int(rec["has_fm"]),prin,
           rec.get("proj",{}).get("framing",""),"", "[]","{}",rec["substance"],run_id,time.time(),
           rec["size"],rec["mtime"],rec["chunked"]))
        for n,v in (rec.get("proj") or {}).items():
            if isinstance(v,list):   # dedup (model repeats items — observed)
                seen=[]; [seen.append(x) for x in v if x not in seen]; v=seen
            c.execute("INSERT OR REPLACE INTO projections(rel,projection,value,produced_by,run_id) VALUES(?,?,?,?,?)",
                      (rec["rel"],n,json.dumps(v,ensure_ascii=False),"model",run_id))
        # code projections
        c.execute("INSERT OR REPLACE INTO projections(rel,projection,value,produced_by,run_id) VALUES(?,?,?,?,?)",
                  (rec["rel"],"format",json.dumps({"has_fm":rec["has_fm"],"fm_keys":list(rec["frontmatter"]),"block_kinds":[b["kind"] for b in rec["blocks"]]}),"code",run_id))
        c.execute("INSERT OR REPLACE INTO projections(rel,projection,value,produced_by,run_id) VALUES(?,?,?,?,?)",
                  (rec["rel"],"lineage",json.dumps({"size":rec["size"],"mtime":rec["mtime"]}),"code",run_id))
        for d in rec["links"]: db.add_link(c, rec["rel"], d)
        for b in rec["blocks"]: db.add_block(c, rec["rel"], b["kind"], b["content"])
    # flush call_log
    for e in fleet.CALL_LOG:
        c.execute("INSERT INTO call_log(rel,tag,status,dt,len,empty,err,ts) VALUES(?,?,?,?,?,?,?,?)",
                  ("", e.get("tag",""), e.get("status",""), e.get("dt"), e.get("len"), int(e.get("empty",0)), e.get("err"), time.time()))
    fleet.CALL_LOG.clear()
    c.commit(); c.close()

if __name__=="__main__":
    import sys, random
    if "--sample" in sys.argv or "--full" in sys.argv:
        db.init()  # idempotent CREATE IF NOT EXISTS — never wipes
        c=db.conn(); c.executescript(open("/dev/stdin").read() if False else "")
        # re-apply migration
        c.executescript("""CREATE TABLE IF NOT EXISTS projections(rel TEXT,projection TEXT,value TEXT,produced_by TEXT,run_id TEXT,UNIQUE(rel,projection));
        CREATE TABLE IF NOT EXISTS call_log(rel TEXT,tag TEXT,status TEXT,dt REAL,len INTEGER,empty INTEGER,err TEXT,ts REAL);""")
        for col,typ in [("size","INTEGER"),("mtime","REAL"),("chunked","INTEGER")]:
            try: c.execute(f"ALTER TABLE files ADD COLUMN {col} {typ}")
            except: pass
        c.commit(); c.close()
        reps=[]
        for cl in json.load(open("carve.json")):
            for m in cl["member_rels"]: reps.append(m)
        random.seed(2); by={}
        for rel in reps: by.setdefault(FORMS.get(rel,"?"),[]).append(rel)
        sample=[]
        for f,rl in by.items(): sample += random.sample(rl, min(2,len(rl)))
        full = "--full" in sys.argv
        target = reps if full else sample
        rid = "full-1" if full else "sample-3"
        print(f"{'FULL' if full else 'SAMPLE'}: {len(target)} files; schema fields: {len(MODEL_PROJ)}", flush=True)
        t0=time.time(); n=run(target, rid, workers=6)
        c=db.conn()
        fail=c.execute("SELECT count(*) FROM files WHERE run_id=? AND substance=1 AND (principle='' OR principle IS NULL)",(rid,)).fetchone()[0]
        sub=c.execute("SELECT count(*) FROM files WHERE run_id=? AND substance=1",(rid,)).fetchone()[0]
        c.close()
        print(f"done {n} in {time.time()-t0:.0f}s; substance={sub} failed={fail} -> {100*(sub-fail)//max(sub,1)}% success")
