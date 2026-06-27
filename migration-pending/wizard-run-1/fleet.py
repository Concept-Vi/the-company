"""The cascade call-layer — a multi-hop 'query engine': local4b (free map), embed (structure), kimi (cloud reduce,
256K, multi-turn, different reasoning). Concurrency caps, retry, structured output, provenance stamping."""
import json, urllib.request, urllib.error, time, concurrent.futures as cf
LOCAL="http://localhost:8000/v1/chat/completions"; LOCAL_M="cyankiwi/Qwen3.5-4B-AWQ-4bit"
EMB="http://localhost:8001/v1/embeddings"; EMB_M="BAAI/bge-m3"
OLL="http://localhost:11434/v1/chat/completions"; KIMI_M="kimi-k2.6:cloud"

def _post(url, payload, timeout):
    req=urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())

CALL_LOG=[]   # instrumentation: every call appended (raw, status, timing, len)
def local4b(messages, json_schema=None, max_tokens=8000, temperature=0, retries=3, tag="", rep_penalty=1.1):
    """json_schema: a JSON-Schema dict -> ENFORCED structured output (grammar-constrained). None -> free text."""
    last=None
    for a in range(retries):
        t0=time.time()
        try:
            p={"model":LOCAL_M,"messages":messages,"max_tokens":max_tokens,"temperature":temperature,"repetition_penalty":rep_penalty}
            if json_schema is not None:
                p["response_format"]={"type":"json_schema","json_schema":{"name":"cap","schema":json_schema}}
            resp=_post(LOCAL,p,200)["choices"][0]
            out=resp["message"]["content"]; fin=resp.get("finish_reason")
            dt=time.time()-t0
            CALL_LOG.append({"tag":tag,"attempt":a,"status":"ok","dt":round(dt,1),"len":len(out or ""),"empty":not (out or "").strip(),"finish":fin})
            if not (out or "").strip():
                last="empty-200"; time.sleep(1.0); continue
            if fin=="length" and a<retries-1:
                last="length"; max_tokens=int(max_tokens*1.8); continue   # truncated mid-JSON -> retry bigger
            return {"text":out, "prov":{"tier":"local","model":LOCAL_M}, "finish":fin}
        except urllib.error.HTTPError as e:
            CALL_LOG.append({"tag":tag,"attempt":a,"status":f"http{e.code}","dt":round(time.time()-t0,1)})
            last=f"HTTP {e.code}"
            if a<retries-1: time.sleep(2); continue
        except Exception as e:
            CALL_LOG.append({"tag":tag,"attempt":a,"status":"exc","err":str(e)[:80],"dt":round(time.time()-t0,1)})
            last=str(e)[:80]
            if a==retries-1: break
            time.sleep(2)
    return {"error":last or "fail","prov":{"tier":"local"}}

def kimi(messages, max_tokens=8000, temperature=0.2, retries=3):
    """Cloud REASONING model (kimi-k2.6) — reasons in a separate field, so it needs token headroom.
    256K window (use judiciously), multi-turn ok (pass full messages list)."""
    for a in range(retries):
        try:
            msg=_post(OLL,{"model":KIMI_M,"messages":messages,"max_tokens":max_tokens,"temperature":temperature},900)["choices"][0]["message"]
            out=msg.get("content") or ""
            return {"text":out, "reasoning":msg.get("reasoning",""), "prov":{"tier":"cloud","model":KIMI_M}}
        except Exception as e:
            if a==retries-1: return {"error":str(e)[:100],"prov":{"tier":"cloud"}}
            time.sleep(4)

def embed(texts):
    if isinstance(texts,str): texts=[texts]
    try:
        d=_post(EMB,{"model":EMB_M,"input":texts},120)["data"]
        return [r["embedding"] for r in d]
    except Exception as e:
        return [{"error":str(e)[:60]}]

def map_local(items, fn, workers=8):
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items))
def map_kimi(items, fn, workers=6):   # subscription allows ~6-10 concurrent
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items))

if __name__=="__main__":
    print("probe local4b:", local4b([{"role":"user","content":"reply READY"}],max_tokens=8).get("text","?")[:20])
    e=embed("hello world"); print("probe embed: dim", len(e[0]) if isinstance(e[0],list) else e[0])
    t0=time.time(); k=kimi([{"role":"user","content":"Reply with exactly: KIMI-READY"}],max_tokens=12)
    print(f"probe kimi ({time.time()-t0:.1f}s):", k.get("text", k.get("error"))[:40])
