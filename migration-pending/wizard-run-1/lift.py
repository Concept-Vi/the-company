"""Registry-driven, exact code extraction. Add a lifter = add a registry row (no code change for new regex/fence kinds)."""
import re, json, os
REG = json.load(open(os.path.expanduser("~/wizard-run-1/registries/markdown_lifters.json")))

def _frontmatter(txt):
    if not txt.startswith("---"): return {}, False
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", txt, re.S)
    if not m: return {}, False
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.strip().startswith("#"):
            k, _, v = line.partition(":"); k = k.strip(); v = v.strip().strip('"\'')
            if k:
                if v.startswith("[") and v.endswith("]"):
                    v = [x.strip().strip('"\'') for x in v[1:-1].split(",") if x.strip()]
                fm[k] = v
    return fm, True

def _fenced(txt):
    blocks = []
    for m in re.finditer(r"```([a-zA-Z0-9_-]*)\n(.*?)```", txt, re.S):
        lang = (m.group(1) or "").lower(); body = m.group(2)
        kind = lang or ("json" if body.strip()[:1] in "{[" else ("sql" if re.search(r"\b(create table|select|insert)\b", body, re.I) else "code"))
        blocks.append({"kind": kind, "content": body.strip()[:8000]})
    return blocks

def _tables(txt):
    out = []
    for m in re.finditer(r"((?:^\|.*\|\s*\n){2,})", txt, re.M):
        out.append({"kind": "table", "content": m.group(1).strip()[:4000]})
    return out

def lift(path, file_type="markdown"):
    with open(path, encoding="utf-8", errors="ignore") as f: txt = f.read()
    fm, has_fm = {}, False; links = []; blocks = []
    for row in REG.get(file_type, []):
        meth = row["method"]
        if meth == "yaml_frontmatter": fm, has_fm = _frontmatter(txt)
        elif meth == "regex": links += [x.strip() for x in re.findall(row["pattern"], txt)]
        elif meth == "fenced_blocks": blocks += _fenced(txt)
        elif meth == "md_tables": blocks += _tables(txt)
    return {"frontmatter": fm, "has_fm": has_fm, "links": sorted(set(links)), "blocks": blocks}

if __name__ == "__main__":
    import sys, glob
    ROOT="/mnt/c/Users/Workstation001/Documents/Claude/Projects/Visual Designer"
    # test on a few varied reps from the carve
    reps=[]
    for c in json.load(open(os.path.expanduser("~/wizard-run-1/carve.json"))):
        reps += c["member_rels"][:1]
    import random; random.seed(1)
    sample = [ROOT+"/"+r for r in random.sample(reps, min(8, len(reps)))]
    for p in sample:
        r = lift(p)
        rel = p.replace(ROOT+"/","")
        print(f"\n{rel[:80]}")
        print(f"  has_fm={r['has_fm']} fm_keys={list(r['frontmatter'])[:6]} links={len(r['links'])} blocks={[b['kind'] for b in r['blocks']][:6]}")
