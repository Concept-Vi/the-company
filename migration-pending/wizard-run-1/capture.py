import json, os, time, concurrent.futures as cf
import db, lift, fleet, forms
ROOT="/mnt/c/Users/Workstation001/Documents/Claude/Projects/Visual Designer"
def survey_forms():
    m={}
    for l in open(os.path.expanduser("~/wizard-run-1/form_survey.jsonl")):
        try:
            r=json.loads(l)
            if "error" not in r: m[r["rel"]]=r.get("content_form","")
        except: pass
    return m
FORMS=survey_forms()
def capture_one(rel):
    path=ROOT+"/"+rel
    code=lift.lift(path)
    bk, light = forms.bucket(FORMS.get(rel,""))
    rec={"rel":rel,"form":bk,"frontmatter":code["frontmatter"],"has_fm":code["has_fm"],"links":code["links"],"blocks":code["blocks"],"substance":0 if light else 1}
    if light:
        # light: code metadata + one-line summary (cheap local)
        body=open(path,encoding='utf-8',errors='ignore').read(4000)
        r=fleet.local4b([{"role":"system","content":'One-line summary. JSON: {"summary":"..."}'},
                         {"role":"user","content":body}], schema=True, max_tokens=120)
        try: rec["form_specific"]={"summary":json.loads(r["text"]).get("summary","")}
        except: rec["form_specific"]={"summary":""}
        rec.update({"principle":"","framing":"","reach":"","surface_claims":[]})
        return rec
    body=open(path,encoding='utf-8',errors='ignore').read(110000)
    fm_ctx=json.dumps(code["frontmatter"])[:1500]
    sys=("Capture ONE file from a SCATTERED, AI-GENERATED, NEVER-REVIEWED corpus — the AI wrote it as-if-final but "
      "NOTHING is trustworthy at the detail level. The GOLD is the underlying PRINCIPLE/INTENT of the author's mental "
      "model (the AI rendered it imperfectly); surface claims are UNVERIFIED evidence, not fact. Return STRICT JSON: "
      + forms.schema_for(bk))
    r=fleet.local4b([{"role":"system","content":sys},
                     {"role":"user","content":f"PATH: {rel}\nFRONTMATTER(context): {fm_ctx}\n\nBODY:\n{body}"}],
                    schema=True, max_tokens=1600)
    if "error" in r: rec["_err"]=r["error"]; rec.update({"principle":"","framing":"","reach":"","surface_claims":[],"form_specific":{}}); return rec
    try:
        b=json.loads(r["text"])
        rec.update({"principle":b.get("principle",""),"framing":b.get("framing",""),"reach":b.get("reach",""),
                    "surface_claims":b.get("surface_claims",[]),
                    "form_specific":{k:v for k,v in b.items() if k not in ("what","principle","framing","reach","surface_claims")}})
        rec["form_specific"]["what"]=b.get("what","")
    except Exception as e:
        rec["_err"]=f"parse:{e}"; rec.update({"principle":"","framing":"","reach":"","surface_claims":[],"form_specific":{}})
    return rec
def write(recs, run_id):
    c=db.conn(); db.log_run(c,run_id,"capture","4b+code",{})
    for rec in recs:
        db.upsert_file(c, rec["rel"], form=rec["form"], frontmatter=rec["frontmatter"], has_fm=rec["has_fm"],
            principle=rec.get("principle"), framing=rec.get("framing"), reach=rec.get("reach"),
            surface_claims=rec.get("surface_claims",[]), form_specific=rec.get("form_specific",{}),
            substance=rec["substance"], run_id=run_id)
        for d in rec["links"]: db.add_link(c, rec["rel"], d)
        for blk in rec["blocks"]: db.add_block(c, rec["rel"], blk["kind"], blk["content"])
    c.commit(); c.close()
if __name__=="__main__":
    import sys, random
    db.init()
    reps=[]
    for cl in json.load(open("carve.json")):
        for m in cl["member_rels"]: reps.append((m, cl["tag"]))
    if "--sample" in sys.argv:
        # stratified across buckets
        random.seed(2); by={}
        for rel,_ in reps:
            bk,_l=forms.bucket(FORMS.get(rel,"")); by.setdefault(bk,[]).append(rel)
        sample=[]
        for bk,rl in by.items(): sample += random.sample(rl, min(3,len(rl)))
        print(f"sample: {len(sample)} files across {len(by)} buckets", flush=True)
        t0=time.time(); recs=fleet.map_local(sample, capture_one, workers=6)
        write(recs, "sample-1")
        print(f"captured {len(recs)} in {time.time()-t0:.0f}s; errors={sum('_err' in r for r in recs)}")
