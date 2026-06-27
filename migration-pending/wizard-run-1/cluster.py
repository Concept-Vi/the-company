import json, numpy as np, collections, os
from sklearn.cluster import KMeans
W=os.path.expanduser("~/wizard-run-1/")
rels=[]; vecs=[]
for line in open(W+"embed.jsonl"):
    r=json.loads(line)
    if "v" in r: rels.append(r["rel"]); vecs.append(r["v"])
X=np.array(vecs,dtype=np.float32); X/=np.linalg.norm(X,axis=1,keepdims=True)+1e-9
print(f"vectors: {X.shape}")
# scan metadata
meta={}
for line in open(W+"scan.jsonl"):
    try:
        r=json.loads(line); meta[r["rel"]]={"kind":r.get("kind"),"domain":r.get("domain"),"built":r.get("built")}
    except: pass
def area(rel): return rel.split("/")[0]
K=40
km=KMeans(n_clusters=K,n_init=4,random_state=0).fit(X)
lab=km.labels_
# nearest to centroid for representatives
out=open(W+"clusters.txt","w")
for c in range(K):
    idx=np.where(lab==c)[0]
    if len(idx)==0: continue
    cen=km.cluster_centers_[c]; cen/=np.linalg.norm(cen)+1e-9
    sims=X[idx]@cen; order=idx[np.argsort(-sims)]
    ar=collections.Counter(area(rels[i]) for i in idx).most_common(2)
    dm=collections.Counter(meta.get(rels[i],{}).get("domain") for i in idx).most_common(3)
    kd=collections.Counter(meta.get(rels[i],{}).get("kind") for i in idx).most_common(3)
    reps=[rels[i] for i in order[:5]]
    line=f"\n### C{c}  (n={len(idx)})  area={ar}  domain={dm}  kind={kd}\n" + "\n".join("   "+r for r in reps)
    out.write(line+"\n"); 
    if len(idx)>=20: print(line)
out.close()
# near-duplicate density
sample=X if len(X)<=2500 else X[np.random.choice(len(X),2500,replace=False)]
S=sample@sample.T; np.fill_diagonal(S,0)
dups=int((S>0.95).sum()//2); high=int((S>0.90).sum()//2)
print(f"\n=== redundancy: pairs>0.95={dups}  pairs>0.90={high}  (of {len(sample)} files) ===")
print(f"cluster sizes: {sorted(collections.Counter(lab).values(),reverse=True)}")
