#!/usr/bin/env python3
"""substrate-graph.py — project the claude-ds address registry into registry/graph.json,
the EXACT shape counterpart's Graph instrument renders (DNA.mountGraph — "this same
component takes ANY project's graph.json"). The graph is not a new truth: it is
registry/address-registry.json seen geometrically. Re-run after substrate-map.py.

claude-ds additions the instrument already tolerates as extra node fields:
  ghost: true        on unresolved-reference nodes (clustered under "(ghosts)")
  zone: "<leaf>"     media/archive zones (partitioned in GAPS judgement)
"""
import json, os, time
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
reg = json.load(open("registry/address-registry.json"))
addr = reg["addresses"]

TYPEMAP = {
    "js":   ("browser", "Browser logic (JavaScript)"), "jsx": ("browser", "React component (JSX)"),
    "mjs":  ("browser", "Browser module (JavaScript)"), "ts": ("browser", "Typed interface (TS)"),
    "py":   ("workstation", "Engine script (Python)"), "sh": ("workstation", "Shell script"),
    "css":  ("palette-swatches", "Styles — the look (CSS)"), "html": ("window", "Page (HTML)"),
    "json": ("database", "Structured data (JSON)"), "md": ("file-doc", "Written document (Markdown)"),
    "txt":  ("file-text", "Text note"), "svg": ("image", "Vector graphic (SVG)"),
    "png":  ("image", "Image (PNG)"), "jpg": ("image", "Image (JPG)"), "jpeg": ("image", "Image (JPG)"),
    "webp": ("image", "Image (WebP)"), "gif": ("image", "Image (GIF)"), "pdf": ("file-pdf", "Document (PDF)"),
    "woff": ("file-text", "Font"), "woff2": ("file-text", "Font"), "thumbnail": ("image", "Thumbnail"),
    "dir":  ("folder", "Folder"), "ghost": ("no-symbol", "Unresolved reference"),
}
def icon_label(t):
    return TYPEMAP.get((t or "").lower(), ("file", t or "File"))
def typ(e):
    if e.get("kind") == "directory": return "dir"
    if e.get("kind") == "ghost": return "ghost"
    return e.get("extension") or "file"
def top(a): return a.split("/")[0] if "/" in a else "(root)"
def refs(e): return len(e.get("edges_in", []))
def mtime(a):
    try: return int(os.path.getmtime(a))
    except OSError: return None

files = {a: e for a, e in addr.items() if e.get("kind") == "file"}
ghosts = {a: e for a, e in addr.items() if e.get("kind") == "ghost"}

spine = [a for a, e in sorted(files.items(), key=lambda kv: -refs(kv[1]))[:18] if refs(e) > 0]
spine_set = set(spine)

fold = defaultdict(list)
for a, e in files.items():
    fold[top(a)].append((a, e))

clusters = []
for f in sorted(fold, key=lambda f: -len(fold[f])):
    members = sorted(fold[f], key=lambda kv: -refs(kv[1]))
    order_map = {a: i for i, (a, _) in enumerate(sorted(fold[f], key=lambda kv: kv[0]))}
    nodes = []
    for a, e in members:
        ic, lab = icon_label(typ(e))
        nodes.append({"id": a, "label": e.get("name") or a.split("/")[-1],
                      "type": typ(e), "type_label": lab, "icon": ic,
                      "refs": refs(e), "bytes": e.get("bytes", 0), "lines": e.get("lines"),
                      "depth": a.count("/"), "order": order_map[a], "mtime": mtime(a),
                      "summary": e.get("description", ""), "spine": a in spine_set, "zone": e.get("zone"),
                      "out": len([x for x in e.get("edges", []) if x.get("resolved") in addr])})
    mts = [n["mtime"] for n in nodes if n["mtime"]]
    clusters.append({"id": f, "label": f, "file_count": len(members),
                     "refs": sum(refs(e) for _, e in members),
                     "bytes": sum(e.get("bytes", 0) for _, e in members),
                     "mtime": max(mts) if mts else None, "nodes": nodes})

# the GHOSTS cluster — the gap made visible: every unresolved reference as a node
if ghosts:
    gnodes = []
    for i, (a, e) in enumerate(sorted(ghosts.items(), key=lambda kv: -refs(kv[1]))):
        ic, lab = icon_label("ghost")
        gnodes.append({"id": a, "label": a.split("/")[-1], "type": "ghost", "type_label": lab,
                       "icon": ic, "refs": refs(e), "bytes": 0, "lines": None, "depth": a.count("/"),
                       "order": i, "mtime": None, "summary": "referenced but does not exist",
                       "spine": False, "ghost": True, "out": 0})
    clusters.append({"id": "(ghosts)", "label": "(ghosts)", "file_count": len(gnodes),
                     "refs": sum(n["refs"] for n in gnodes), "bytes": 0, "mtime": None,
                     "nodes": gnodes})

# the SYMBOL LEVEL as clusters — (icons)/(tokens)/(axes)/(actions), parenthesised so the
# cluster ids can't collide with real folders (the (ghosts) convention). Node ids are
# projection-safe ("(icons)/sparkles"); the canonical company address rides in `address`.
# Ghost symbols sit IN their registry cluster, flagged — a missing icon glows among icons.
sym = json.load(open("registry/symbol-registry.json"))
SYMSETS = [("(icons)", "icons", "icon", "image", "Icon (CV_ICONS)"),
           ("(tokens)", "tokens", "token", "palette-swatches", "Design token (CSS custom property)"),
           ("(axes)", "axes", "axis", "database", "Axis (CV_AXES)"),
           ("(actions)", "actions", "action", "file", "Action verb (CV_ACTIONS)")]
sym_edges = []
for clabel, key, tname, ticon, tlabel in SYMSETS:
    snodes = []
    entries = sym.get(key, {})
    for i, (caddr, v) in enumerate(sorted(entries.items())):
        short = caddr.split("/")[-1]
        nid = clabel + "/" + short
        ghost = bool(v.get("ghost"))
        orphan = bool(v.get("orphan"))
        definers = v.get("defined_in") or v.get("registered_in") or ([v["registered_in"]] if isinstance(v.get("registered_in"), str) and v.get("registered_in") else [])
        consumers = v.get("consumed_in") or v.get("invoked_in") or []
        snodes.append({"id": nid, "label": short, "type": tname, "type_label": tlabel,
                       "icon": "no-symbol" if ghost else ticon,
                       "refs": len(consumers), "bytes": 0, "lines": None,
                       "depth": 1, "order": i, "mtime": None, "address": caddr,
                       "summary": ("GHOST — used, never defined/registered" if ghost else
                                   "orphan — defined, no live consumer" if orphan else ""),
                       "spine": False, "ghost": ghost, "orphan": orphan,
                       "out": len(definers)})
        for d in definers:
            if d in files:
                sym_edges.append({"from": d, "to": nid, "kind": "defines"})
        if ghost:                       # who wants the missing thing (bounded: ghosts only)
            for cfile in consumers:
                if cfile in files:
                    sym_edges.append({"from": cfile, "to": nid, "kind": "wants"})
    if snodes:
        clusters.append({"id": clabel, "label": clabel, "file_count": len(snodes),
                         "refs": sum(n["refs"] for n in snodes), "bytes": 0, "mtime": None,
                         "nodes": snodes})

corder = {lab: i for i, lab in enumerate(sorted(c["label"] for c in clusters))}
for c in clusters:
    c["order"] = corder[c["label"]]

node_ids = set(files) | set(ghosts)
edges, seen = [], set()
for a, e in files.items():
    for x in e.get("edges", []):
        t = x.get("resolved")
        if t in node_ids and t != a and (a, t, x.get("kind")) not in seen:
            seen.add((a, t, x.get("kind")))
            edges.append({"from": a, "to": t, "kind": x.get("kind")})
edges.extend(sym_edges)

type_counts = defaultdict(int)
for a, e in files.items(): type_counts[typ(e)] += 1
if ghosts: type_counts["ghost"] = len(ghosts)
types = {}
for t, c in sorted(type_counts.items(), key=lambda kv: -kv[1]):
    ic, lab = icon_label(t)
    types[t] = {"icon": ic, "label": lab, "count": c}
for clabel, key, tname, ticon, tlabel in SYMSETS:
    n = len(sym.get(key, {}))
    if n:
        types[tname] = {"icon": ticon, "label": tlabel, "count": n}

stamp = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
m = reg.get("_meta", {})
data = {
    "meta": {"project": "claude-ds", "generated": stamp,
             "addresses": m.get("entries"), "files": len(files), "folders": len(clusters),
             "edges": len(edges), "ghosts": len(ghosts), "spine_count": len(spine),
             "company_address_prefix": "project://claude-ds/"},
    "root": {"id": ".", "label": "claude-ds", "icon": "v-mark", "type": "root",
             "type_label": "The ConceptV Design System"},
    "types": types,
    "clusters": clusters,
    "edges": edges,
    "spine": spine,
}
json.dump(data, open("registry/graph.json", "w"), indent=1)
print(f"wrote registry/graph.json | clusters:{len(clusters)} files:{len(files)} "
      f"edges:{len(edges)} types:{len(types)} spine:{len(spine)} ghosts:{len(ghosts)}")
