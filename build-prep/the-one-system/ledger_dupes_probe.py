#!/usr/bin/env python3
"""Fast numpy duplication/fragmentation pass over the ledger, both CODE and DOCS, via embed-pplx.
Surfaces near-duplicate clusters (files/docs doing/saying ~the same thing) at several thresholds."""
import json, os, subprocess, urllib.request, time
import numpy as np

EMBED="http://127.0.0.1:8007/v1/embeddings"; MODEL="perplexity-ai/pplx-embed-context-v1-4b"
def P(sql):
    return subprocess.run(["psql","-h","127.0.0.1","-p","15432","-U","postgres","-d","postgres","-tAc",sql],
                          capture_output=True,text=True,env={**os.environ,"PGPASSWORD":"postgres"}).stdout
def fetch(where):
    rows=[]
    out=P("select e.project||chr(1)||e.path||chr(1)||replace(coalesce(e.what_it_does,''),chr(10),' ') "
          "from ledger.entry e join ledger.latest_run r using(run_id) "
          f"where e.node_type='file' and e.what_it_does is not null and e.what_it_does<>'' {where} order by e.project,e.path")
    for ln in out.splitlines():
        p=ln.split(chr(1))
        if len(p)>=3 and p[2].strip(): rows.append({"project":p[0],"path":p[1],"desc":p[2]})
    return rows
def embed_all(rows):
    vs=[]; B=32
    for i in range(0,len(rows),B):
        body=json.dumps({"model":MODEL,"input":[r["desc"][:2000] for r in rows[i:i+B]]}).encode()
        with urllib.request.urlopen(urllib.request.Request(EMBED,data=body,headers={"Content-Type":"application/json"}),timeout=120) as r:
            vs.extend(it["embedding"] for it in json.loads(r.read())["data"])
    M=np.array(vs,dtype=np.float32); M/=np.linalg.norm(M,axis=1,keepdims=True)+1e-9
    return M
def clusters_at(M,t):
    n=len(M); S=M@M.T; np.fill_diagonal(S,0)
    par=list(range(n))
    def f(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    ii,jj=np.where(np.triu(S>=t,1))
    npairs=len(ii)
    for a,b in zip(ii.tolist(),jj.tolist()):
        ra,rb=f(a),f(b)
        if ra!=rb: par[ra]=rb
    from collections import defaultdict
    cl=defaultdict(list)
    for i in range(n): cl[f(i)].append(i)
    return npairs,[c for c in cl.values() if len(c)>=2]

def run(label, where, ct):
    rows=fetch(where); t0=time.time()
    if not rows: print(f"[{label}] no rows"); return None,None
    M=embed_all(rows); print(f"[{label}] embedded {len(rows)} in {time.time()-t0:.0f}s",flush=True)
    out=[f"\n## {label}: near-duplicate clusters (embedded what_it_does)\n"]
    for t in [0.95,0.90,0.85,0.80]:
        npr,cls=clusters_at(M,t)
        nfiles=sum(len(c) for c in cls)
        out.append(f"- cos>={t}: {npr} pairs · {len(cls)} clusters covering {nfiles} files")
    out.append("")
    npr,cls=clusters_at(M,ct); cls.sort(key=len,reverse=True)
    cross=sum(1 for c in cls if len({rows[i]['project'] for i in c})>1)
    out.append(f"**At cos>={ct}: {len(cls)} clusters, {cross} cross-project. Top clusters:**\n")
    for ci,c in enumerate(cls[:30],1):
        projs=sorted({rows[i]['project'] for i in c})
        out.append(f"### {label} cluster {ci} — {len(c)} files{' [CROSS: '+','.join(projs)+']' if len(projs)>1 else ''}")
        for i in c[:10]: out.append(f"  - `{rows[i]['project']}/{rows[i]['path']}` — {rows[i]['desc'][:100]}")
        if len(c)>10: out.append(f"  - …+{len(c)-10} more")
        out.append("")
    return "\n".join(out), (len(cls),cross,sum(len(c) for c in cls))

codetxt,codestat=run("CODE","and e.ext in ('.py','.js','.jsx','.ts','.tsx')",0.85)
docstxt,docstat=run("DOCS","and e.ext='.md'",0.85)
open("/home/tim/.claude/jobs/7a97439e/tmp/dupe_np.md","w").write((codetxt or "")+"\n"+(docstxt or ""))
print("CODE stat (clusters,cross,files):",codestat)
print("DOCS stat (clusters,cross,files):",docstat)
print("WROTE dupe_np.md", flush=True)
