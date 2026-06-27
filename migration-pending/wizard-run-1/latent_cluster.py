import json, urllib.request, concurrent.futures as cf, numpy as np, collections, os, time
from sklearn.cluster import KMeans
W=os.path.expanduser("~/wizard-run-1/")
def load(fn):
    items=[]
    for l in open(W+fn):
        try:
            n,txt=l.rstrip("\n").split("\t",1)
            items.append(txt)
        except: pass
    return items
lat=load("clean_latent_or_abandoned.txt"); con=load("clean_gaps_or_contradictions.txt")
print(f"latent: {len(lat)}  contradictions: {len(con)}")
URL="http://localhost:8001/v1/embeddings"
def emb(t):
    try:
        body=json.dumps({"model":"BAAI/bge-m3","input":t[:500]}).encode()
        req=urllib.request.Request(URL,data=body,headers={"Content-Type":"application/json"})
        return np.array(json.loads(urllib.request.urlopen(req,timeout=40).read())["data"][0]["embedding"],dtype=np.float32)
    except: return None
def cluster_dump(items,name,K):
    with cf.ThreadPoolExecutor(max_workers=16) as ex: vs=list(ex.map(emb,items))
    pairs=[(i,v) for i,v in zip(items,vs) if v is not None]
    X=np.array([v for _,v in pairs]); X/=np.linalg.norm(X,axis=1,keepdims=True)+1e-9
    K=min(K,len(pairs)//3 or 1)
    km=KMeans(n_clusters=K,n_init=4,random_state=0).fit(X); lab=km.labels_
    print(f"\n===== {name}: {len(pairs)} items → {K} theme-clusters =====")
    sizes=collections.Counter(lab)
    for c,_ in sizes.most_common():
        idx=np.where(lab==c)[0]; cen=km.cluster_centers_[c]; cen/=np.linalg.norm(cen)+1e-9
        reps=[pairs[i][0] for i in idx[np.argsort(-(X[idx]@cen))][:5]]
        if len(idx)>=4:
            print(f"\n[{name} theme · n={len(idx)}]")
            for r in reps: print(f"   • {r}")
cluster_dump(lat,"LATENT/ABANDONED",30)
cluster_dump(con,"CONTRADICTIONS",30)
