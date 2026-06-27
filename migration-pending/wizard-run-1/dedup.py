import json, numpy as np, collections, os
W=os.path.expanduser("~/wizard-run-1/")
rels=[]; vecs=[]
for line in open(W+"embed.jsonl"):
    r=json.loads(line)
    if "v" in r: rels.append(r["rel"]); vecs.append(r["v"])
X=np.array(vecs,dtype=np.float32); X/=np.linalg.norm(X,axis=1,keepdims=True)+1e-9
n=len(rels); print(f"files: {n}")
# union-find on cosine>0.95 (blocked matmul to bound memory)
parent=list(range(n))
def find(a):
    while parent[a]!=a: parent[a]=parent[parent[a]]; a=parent[a]
    return a
def union(a,b):
    ra,rb=find(a),find(b)
    if ra!=rb: parent[ra]=rb
B=400
for i in range(0,n,B):
    S=X[i:i+B]@X.T
    for r in range(S.shape[0]):
        gi=i+r
        for gj in np.where(S[r]>0.95)[0]:
            if gj>gi: union(gi,int(gj))
groups=collections.defaultdict(list)
for i in range(n): groups[find(i)].append(i)
sizes=sorted((len(v) for v in groups.values()),reverse=True)
uniq=len(groups)
print(f"UNIQUE dup-groups: {uniq}  (so ~{uniq} distinct docs behind {n} files = {100*(n-uniq)//n}% redundant)")
print(f"biggest dup-groups: {sizes[:15]}")
print("singletons (unique):", sum(1 for s in sizes if s==1))
# show the most-copied content groups
big=sorted(groups.values(),key=len,reverse=True)[:8]
print("\n=== most-duplicated content (group size → sample paths) ===")
for g in big:
    print(f"\n[x{len(g)}] {rels[g[0]]}")
    for i in g[1:4]: print(f"        = {rels[i]}")
