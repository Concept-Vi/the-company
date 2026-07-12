#!/usr/bin/env python3
"""substrate-map.py — the claude-ds ADDRESS MAP emitter (the two-engines join).

Engine 1 (counterpart substrate pattern): every folder/file = an address with a type
and a `contains` parent edge; per-file DETERMINISTIC edge extraction (five vocabularies);
edges resolve or become GHOST nodes; every edge records its equal-and-opposite inverse.

Engine 2 (the DS describing itself): the registries ARE the symbol level —
window.CV_* globals · CSS custom properties · CV_ICONS ids · CV_AXES axes+values ·
glyph-corpus.json (glyph:// addresses, already emitted by _system/emit_glyph_corpus.js).

The five edge vocabularies (all mechanical — no judgement):
  1. loads      html -> script src / link href / img src / use href / iframe
  2. globals    js   -> window.CV_* DEFINES vs CONSUMES
  3. tokens     css/js/html -> --prop: DEFINES vs var(--prop) CONSUMES
  4. assets     any  -> url(...) / path-string references
  5. registry   icon ids used vs registered · axis ids resolved vs made

GHOST  = consumed/referenced but defined nowhere.
ORPHAN = defined but consumed nowhere (inside the scanned tree).

Outputs (derived, never hand-maintained — rerun on change):
  registry/address-registry.json   file-level addresses + typed edges + ghosts
  registry/symbol-registry.json    symbol-level nodes (globals/tokens/icons/axes/glyphs)
  registry/GAPS.md                 the human-readable ghost/orphan gap list

Zones: _archive-v1, uploads, inspo, screenshots, _qa, _ingest are mapped as addresses but
PARTITIONED OUT of gap judgement (excluded-with-reason: archive/leaf-media zones).
"""
import os, re, json, time, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
STAMP = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

SKIP_TOP = {".git", "node_modules", "__pycache__"}
# mapped as addresses, excluded from gap judgement (reason recorded)
LEAF_ZONES = {"_archive-v1": "archived v1 — superseded, kept for provenance",
              "uploads": "raw pasted media", "inspo": "reference media",
              "screenshots": "capture media", "_qa": "QA harnesses + shots (probe-only consumers)",
              "_ingest": "source-extraction media"}
# derived artifacts whose contents duplicate their sources (would double-count every symbol)
DERIVED_FILES = {"_ds_bundle.js": "generated bundle (concatenation of app files)",
                 "_ds_manifest.json": "generated card manifest"}
TEXT_EXT = {"js", "jsx", "css", "html", "md", "json", "svg", "txt", "d.ts", "ts"}

def zone_of(rel):
    top = rel.split("/", 1)[0]
    return top if top in LEAF_ZONES else None

# ---------------------------------------------------------------- pass A: skeleton
addr = {}
for dirpath, dirs, fnames in os.walk(ROOT):
    rel = os.path.relpath(dirpath, ROOT)
    dirs[:] = [d for d in dirs if d not in SKIP_TOP]
    a = "." if rel == "." else rel.replace(os.sep, "/")
    parent = None if a == "." else (os.path.dirname(a) or ".")
    addr[a] = {"address": a, "kind": "directory" if a != "." else "root",
               "parent": parent, "zone": zone_of(a) if a != "." else None}
    for f in fnames:
        fp = f if a == "." else a + "/" + f
        ext = os.path.splitext(f)[1].lstrip(".").lower() or "(none)"
        try: b = os.path.getsize(os.path.join(dirpath, f))
        except OSError: b = None
        addr[fp] = {"address": fp, "kind": "file", "name": f, "extension": ext,
                    "parent": a, "bytes": b, "zone": zone_of(fp)}

files = {a: e for a, e in addr.items() if e["kind"] == "file"}

def read(a):
    try:
        return open(os.path.join(ROOT, a), encoding="utf-8", errors="replace").read()
    except OSError:
        return ""

RE_BLOCK_COMMENT = re.compile(r'/\*.*?\*/', re.S)
RE_LINE_COMMENT = re.compile(r'(?<!:)//[^\n]*')
RE_HTML_COMMENT = re.compile(r'<!--.*?-->', re.S)

def strip_comments(txt, ext):
    """Doc prose is not consumption: 'var(--token)' in a header comment is not an
    edge. Heuristic strip (protocol '://' preserved by the lookbehind)."""
    if ext in ("js", "jsx", "ts", "css"):
        txt = RE_BLOCK_COMMENT.sub("", txt)
        if ext != "css":
            txt = RE_LINE_COMMENT.sub("", txt)
    if ext in ("html", "htm"):
        txt = RE_HTML_COMMENT.sub("", txt)
        txt = RE_BLOCK_COMMENT.sub("", txt)
    return txt

# ---------------------------------------------------------------- pass B: edges
# suffix index for SELF-HEAL: a path that resolves nowhere re-points to the UNIQUE
# real address ending with it (counterpart assemble.py pattern; the heal IS a finding:
# the reference's path drifted from the layout). Ambiguous/none -> ghost.
suffix_index = defaultdict(list)
for _a in files:
    parts = _a.split("/")
    for i in range(len(parts)):
        suffix_index["/".join(parts[i:])].append(_a)

def resolve_path(frm, target):
    t = target.strip().split("?")[0].split("#")[0]
    if (not t or "${" in t or "%23" in t
            or t.startswith(("http:", "https:", "data:", "mailto:", "//", "blob:"))):
        return None, False, False
    base = os.path.dirname(frm)
    for cand in (os.path.normpath(os.path.join(base, t)).replace(os.sep, "/"),
                 os.path.normpath(t.lstrip("/")).replace(os.sep, "/")):
        if cand in addr:
            return cand, True, False
    hits = suffix_index.get(t.lstrip("./"), [])
    if len(hits) == 1:
        return hits[0], True, True          # healed — path drift finding
    return os.path.normpath(os.path.join(base, t)).replace(os.sep, "/"), False, False

INVERSE = {"script": "loaded_by", "stylesheet": "styled_by", "img": "embedded_by",
           "use": "embedded_by", "iframe": "framed_by", "href": "linked_by",
           "import": "imported_by", "url": "embedded_by", "pathref": "referenced_by"}

RE_HTML = [("script", re.compile(r'<script[^>]+src=["\']([^"\']+)["\']')),
           ("stylesheet", re.compile(r'<link[^>]+href=["\']([^"\']+)["\']')),
           ("img", re.compile(r'<(?:img|source|video|audio)[^>]+src=["\']([^"\']+)["\']')),
           ("use", re.compile(r'<use[^>]+href=["\']([^"\']+)["\']')),
           ("iframe", re.compile(r'<iframe[^>]+src=["\']([^"\']+)["\']')),
           ("href", re.compile(r'<a[^>]+href=["\']([^"\']+\.html?[^"\']*)["\']'))]
RE_CSS_IMPORT = re.compile(r'@import\s+(?:url\()?["\']?([^"\')\s;]+)')
RE_URL = re.compile(r'url\(\s*["\']?([^"\')\s]+?)["\']?\s*\)')
# path-like string in js/jsx/json: quoted, has a slash + known asset/code extension
RE_PATHSTR = re.compile(r'["\'`]([./A-Za-z0-9_-]*?/[A-Za-z0-9 ._()+-]+\.(?:js|jsx|css|html|svg|png|jpg|jpeg|webp|json|woff2?|mp4))["\'`]')

RE_GLOBAL_DEF = re.compile(r'(?:window|global|globalThis)\.(CV_[A-Z0-9_]+)\s*=[^=]')
RE_GLOBAL_ANY = re.compile(r'(?:window|global|globalThis)\.(CV_[A-Z0-9_]+)')
# doc-prose placeholder names that appear inside descriptive STRINGS (not real tokens)
META_TOKENS = {"--token", "--x", "--y", "--z", "--var", "--prop", "--name"}
RE_TOKEN_DEF = re.compile(r'(--[a-zA-Z][\w-]*)\s*:')
RE_TOKEN_SETP = re.compile(r"""setProperty\(\s*['"`](--[a-zA-Z][\w-]*)""")
RE_TOKEN_USE = re.compile(r'var\(\s*(--[a-zA-Z][\w-]*)\s*([,)])')
RE_ICON_USE = [re.compile(r"""icon:\s*['"]([a-z0-9-]+)['"]"""),
               re.compile(r"""iconSVG\(\s*['"]([a-z0-9-]+)['"]"""),
               re.compile(r"""svg/([a-z0-9-]+)\.svg""")]
# entry-shape discriminators: an `id:` is an ACTION if `verb:` follows in the same
# entry window, a TRIGGER if `on:` follows, a TYPE if `layer:` follows, a DECORATOR
# if `group:` follows (each registry's declared shape — the discriminator is the shape)
def ids_by_shape(txt, key):
    out = []
    for m in re.finditer(r"""\{\s*id:\s*['"]([A-Za-z0-9._-]+)['"]""", txt):
        window = txt[m.end():m.end() + 260]
        if re.match(r"[^{}]*\b" + key + r":", window):
            out.append(m.group(1))
    return out
RE_ACTION_USE = [re.compile(r"""\binvoke\(\s*['"]([a-z0-9-]+)['"]"""),
                 re.compile(r"""\bdo:\s*['"]([a-z0-9-]+)['"]"""),
                 re.compile(r"""onPick:\s*['"]([a-z0-9-]+)['"]""")]
RE_TYPE_USE = [re.compile(r"""\b(?:R|CV_REGISTRY|REG)\.(?:resolve|get)\(\s*['"]([A-Za-z0-9._-]+)['"]"""),
               re.compile(r"""occupant:\s*['"]([a-z0-9-]+)['"]""")]
RE_EVENT_USE = re.compile(r"""\bemit\(\s*['"]([a-z0-9.*-]+)['"]""")
RE_EVENT_ON = re.compile(r"""\bon:\s*['"]([a-z0-9.*-]+)['"]""")
RE_SKIN_SCOPE = re.compile(r'\[data-skin="([a-z-]+)"\]')
RE_SKIN_USE = re.compile(r"""data-skin=\\?["']([a-z-]+)|setAttribute\(\s*['"]data-skin['"],\s*['"]([a-z-]+)""")
RE_AXIS_USE = [re.compile(r"""\b(?:CV_AXES|AX(?:\(\))?)\.(?:resolve|has|css|ids|candidates|default)\(\s*['"]([a-z-]+)['"]"""),
               re.compile(r"""\b(?:ax|sub)\(\s*['"]([a-z-]+)['"]"""),
               re.compile(r"""axis:\s*['"]([a-z-]+)['"]""")]

# symbol tables (engine 2)
g_def, g_use = defaultdict(list), defaultdict(list)    # CV_* globals
t_def, t_use = defaultdict(list), defaultdict(list)    # --tokens
t_use_hard = defaultdict(list)                          # var(--x) with NO fallback
i_use = defaultdict(list)                               # icon ids
ax_use = defaultdict(list)                              # axis ids
act_def, act_use = defaultdict(list), defaultdict(list)  # action ids (verb: shape)
typ_def, typ_use = defaultdict(list), defaultdict(list)  # CV_REGISTRY type ids (layer: shape)
dec_def = defaultdict(list)                              # decorator ids (group: shape)
trig_def = defaultdict(list)                             # trigger ids (on: shape)
ev_emit, ev_on = defaultdict(list), defaultdict(list)    # event names
skin_def, skin_use = defaultdict(list), defaultdict(list)  # data-skin scopes
txt_cache = {}                                            # live js/jsx/html text (weak-use pass)
edges_total, ghosts, healed_edges = 0, {}, []

def add_edge(e, frm, kind, target):
    global edges_total
    res, exists, healed = resolve_path(frm, target)
    if res is None:  # external/dynamic — record without resolution
        e["edges"].append({"kind": kind, "target": target, "external": True})
        return
    edges_total += 1
    e["edges"].append({"kind": kind, "target": target, "resolved": res,
                       "exists": exists, "healed": healed})
    if healed:
        healed_edges.append((frm, target, res))
    inv = INVERSE.get(kind, kind + "_by")
    if exists:
        addr[res].setdefault("edges_in", []).append({"kind": inv, "from": frm})
    else:
        ghosts.setdefault(res, {"address": res, "kind": "ghost",
                                "type": "ghost.unresolved-file", "edges_in": []}
                          )["edges_in"].append({"kind": inv, "from": frm, "of_kind": kind})

for a, e in files.items():
    ext = e["extension"]
    if ext not in TEXT_EXT and not a.endswith(".d.ts"):
        continue
    if e["name"] in DERIVED_FILES or a.startswith("registry/"):
        e["derived"] = DERIVED_FILES.get(e["name"], "substrate-map output (this map)")
        continue
    raw = read(a)
    e["lines"] = raw.count("\n") + 1
    txt = strip_comments(raw, ext)
    e["edges"] = []
    if ext in ("html", "htm"):
        for kind, rx in RE_HTML:
            for m in rx.finditer(txt):
                add_edge(e, a, kind, m.group(1))
    if ext == "css" or "<style" in txt or ext in ("js", "jsx", "html"):
        for m in RE_URL.finditer(txt):
            add_edge(e, a, "url", m.group(1))
    if ext == "css":
        for m in RE_CSS_IMPORT.finditer(txt):
            add_edge(e, a, "import", m.group(1))
    if ext in ("js", "jsx", "json", "ts"):
        for m in RE_PATHSTR.finditer(txt):
            tgt = m.group(1)
            if tgt.startswith(("./", "../")) or "/" in tgt.strip("./"):
                add_edge(e, a, "pathref", tgt)
    # globals (vocab 2)
    if ext in ("js", "jsx", "html"):
        defs = set(RE_GLOBAL_DEF.findall(txt))
        for g in defs: g_def[g].append(a)
        for g in set(RE_GLOBAL_ANY.findall(txt)) - defs:
            g_use[g].append(a)
    # tokens (vocab 3) — defines from `--x:` (css/inline styles) + JS setProperty
    if ext in ("css", "html", "js", "jsx"):
        for tk in RE_TOKEN_DEF.findall(txt):
            t_def[tk].append(a)
        for tk in RE_TOKEN_SETP.findall(txt):
            t_def[tk].append(a)
        for tk, closer in RE_TOKEN_USE.findall(txt):
            t_use[tk].append(a)
            if closer == ")":                 # consumed with NO fallback — hard dependency
                t_use_hard[tk].append(a)
    # registry ids (vocab 5)
    if ext in ("js", "jsx", "html"):
        for rx in RE_ICON_USE:
            for m in rx.finditer(txt):
                i_use[m.group(1)].append(a)
        for rx in RE_AXIS_USE:
            for m in rx.finditer(txt):
                ax_use[m.group(1)].append(a)
        for i_ in ids_by_shape(txt, "verb"):    act_def[i_].append(a)
        for i_ in ids_by_shape(txt, "layer"):   typ_def[i_].append(a)
        for i_ in ids_by_shape(txt, "group"):   dec_def[i_].append(a)
        for rx in RE_ACTION_USE:
            for m in rx.finditer(txt):
                act_use[m.group(1)].append(a)
        for rx in RE_TYPE_USE:
            for m in rx.finditer(txt):
                typ_use[m.group(1)].append(a)
        # trigger/event vocabulary only where CV_EVENTS is actually in play —
        # `on:` is also the colour axis's "sits on <ground>" field (shape collision)
        if "CV_EVENTS" in txt:
            for i_ in ids_by_shape(txt, "on"):
                trig_def[i_].append(a)
            for m in RE_EVENT_ON.finditer(txt):
                ev_on[m.group(1)].append(a)
        if "CV_EVENTS" in txt or ".emit(" in txt:
            for m in RE_EVENT_USE.finditer(txt):
                ev_emit[m.group(1)].append(a)
        if ext in ("js", "jsx", "html"):
            txt_cache[a] = txt
        for m in RE_SKIN_USE.finditer(txt):
            skin_use[m.group(1) or m.group(2)].append(a)
    if ext == "css":
        for m in RE_SKIN_SCOPE.finditer(txt):
            skin_def[m.group(1)].append(a)

for ga, g in ghosts.items():
    if ga not in addr:
        addr[ga] = g
    else:
        addr[ga].setdefault("edges_in", []).extend(g["edges_in"])

# ---------------------------------------------------------------- raw colours
# "things that should use tokens but don't": raw hex/rgb colours in LIVE styling
# files, OUTSIDE var() fallbacks (a fallback documents a token; a bare literal
# bypasses the system). Token-definition files own their literals — excluded.
RE_RAWCOLOR = re.compile(r'#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|rgba?\([^)]*\)')
TOKEN_HOME = lambda a: a.startswith("tokens/") or a == "colors_and_type.css" or a == "tonal-zoning.css"
def in_fallback(txt, pos):
    # inside `var(--name, <here>)` — scan back to the nearest unmatched "var("
    start = max(0, pos - 120)
    seg = txt[start:pos]
    vi = seg.rfind("var(")
    return vi >= 0 and seg[vi:].count(")") == 0
raw_colors = {}           # file -> {value: count}
for a, e in files.items():
    ext = e["extension"]
    if ext not in ("css", "html", "jsx", "js") or e.get("zone") or e.get("derived") or TOKEN_HOME(a):
        continue
    if a.startswith(("assets/", "_system/", "preview/")):   # icon/content fills + generators, not UI styling
        continue
    txt = strip_comments(read(a), ext)
    hits = {}
    for m in RE_RAWCOLOR.finditer(txt):
        v = m.group(0)
        if v.startswith("rgb") and "var(" in v:
            continue                                  # rgba(var(--x)…) is token-fed
        if in_fallback(txt, m.start()):
            continue                                  # documented fallback, not a bypass
        hits[v.lower()] = hits.get(v.lower(), 0) + 1
    if hits:
        raw_colors[a] = hits
        e["raw_colors"] = hits

# ---------------------------------------------------------------- pass C: symbol registries
# icons registered: the CV_ICONS.data keys
icons_reg = []
ic_txt = read("assets/icons/cv-icons.js")
m = re.search(r'CV_ICONS\.data\s*=\s*\{(.*)', ic_txt, re.S)
if m:
    icons_reg = re.findall(r"^\s*'([a-z0-9-]+)':", m.group(1), re.M)

# axes registered: axes/*/*-axis.js make({ id: 'x', ... values: [{id:...}] })
axes_reg = {}
for a in files:
    if a.startswith("axes/") and a.endswith(".js") and a != "axes/axis-core.js":
        txt = read(a)
        mid = re.search(r"make\(\s*\{\s*[^}]*?id:\s*'([a-z-]+)'", txt, re.S)
        if mid:
            vals = re.findall(r"\{\s*id:\s*'([a-z0-9-]+)'", txt)
            axes_reg[mid.group(1)] = {"file": a, "values": [v for v in vals if v != mid.group(1)]}

# glyph corpus (already-addressed symbol level)
glyphs = []
try:
    glyphs = json.load(open("glyph-corpus.json"))["entries"]
except (OSError, KeyError, json.JSONDecodeError):
    pass

def live(paths):  # judgement pool = non-leaf-zone consumers/definers
    return [p for p in paths if not files.get(p, addr.get(p, {})).get("zone")]

symbols = {"_meta": {"generated": STAMP, "by": "_system/substrate-map.py",
                     # THE COMPANY SEAM: every address here is reachable as
                     # project://claude-ds/<file address> · cv://<registry>/<id> ·
                     # glyph://... — the DS-native algebra joins the company's
                     # address-resolution at this prefix.
                     "company_address_prefix": "project://claude-ds/"},
           "globals": {}, "tokens": {}, "icons": {}, "axes": {},
           "types": {}, "actions": {}, "decorators": {}, "events": {},
           "skins": {}, "glyphs": len(glyphs)}
for g in sorted(set(g_def) | set(g_use)):
    symbols["globals"]["cv://global/" + g] = {
        "defined_in": sorted(set(g_def.get(g, []))), "consumed_in": sorted(set(g_use.get(g, []))),
        "ghost": not g_def.get(g), "orphan": bool(g_def.get(g)) and not live(g_use.get(g, []))}
# token families = first two dash-segments of DEFINED tokens (--fs-, --accent-, ...)
def fam(tk):
    seg = tk.lstrip("-").split("-")
    return "--" + seg[0] + "-" if len(seg) > 1 else None
def_fams = {fam(tk) for tk in t_def if fam(tk)}
for tk in sorted(set(t_def) | set(t_use)):
    if tk.endswith("-") or tk in META_TOKENS:
        continue                                # dynamic computed / doc-placeholder name
    undef = not t_def.get(tk)
    hard = bool(live(t_use_hard.get(tk, [])))
    # ghost taxonomy: hard ghost = no-fallback consumer would break;
    # family ghost = fallback-masked but the name belongs to a DEFINED family
    # (the --fs-micro class of bug); parametric = fallback-only, no family — a
    # deliberate per-composition contract variable, NOT a defect.
    # --skin-* is the per-skin OVERRIDE CONTRACT: unset at :root BY DESIGN
    # (tokens/skins.css header: "at :root the --skin-mat-* refs are unset, so these
    # substitute to glass defaults") — fallback-consumed --skin-* is parametric, not ghost.
    skin_slot = tk.startswith("--skin-")
    kind = ("ghost-hard" if (undef and hard and not skin_slot) else
            "ghost-family" if (undef and fam(tk) in def_fams and not skin_slot) else
            "parametric" if undef else "defined")
    symbols["tokens"]["cv://token/" + tk] = {
        "defined_in": sorted(set(t_def.get(tk, []))), "consumed_in": sorted(set(t_use.get(tk, []))),
        "class": kind, "ghost": undef and kind.startswith("ghost"),
        "orphan": not undef and not t_use.get(tk)}
for ic in sorted(set(icons_reg) | set(i_use)):
    symbols["icons"]["cv://icon/" + ic] = {
        "registered": ic in icons_reg, "consumed_in": sorted(set(i_use.get(ic, []))),
        "ghost": ic not in icons_reg, "orphan": ic in icons_reg and not live(i_use.get(ic, []))}
for ax in sorted(set(axes_reg) | set(ax_use)):
    symbols["axes"]["cv://axis/" + ax] = {
        "registered_in": axes_reg.get(ax, {}).get("file"),
        "values": axes_reg.get(ax, {}).get("values", []),
        "consumed_in": sorted(set(ax_use.get(ax, []))),
        "ghost": ax not in axes_reg, "orphan": ax in axes_reg and not live(ax_use.get(ax, []))}

# actions: registered (verb-shaped entries) vs invoked/do:/onPick.
# WEAK-USE pass: verb-variable dispatch (var verb = ... 'fill-socket'; invoke(verb))
# leaves the id as a bare quoted string — count it as use when the file also
# touches the action layer. Suppresses false orphans only (never creates ghosts).
for ac in act_def:
    if live(act_use.get(ac, [])):
        continue
    needle = "'" + ac + "'"
    for fa, ftxt in txt_cache.items():
        if fa in act_def[ac] or files.get(fa, {}).get("zone"):
            continue
        if needle in ftxt and ("invoke" in ftxt or "CV_ACTIONS" in ftxt):
            act_use[ac].append(fa)
for ac in sorted(set(act_def) | set(act_use)):
    symbols["actions"]["cv://action/" + ac] = {
        "registered_in": sorted(set(act_def.get(ac, []))),
        "invoked_in": sorted(set(act_use.get(ac, []))),
        "ghost": not act_def.get(ac) and bool(live(act_use.get(ac, []))),
        "orphan": bool(act_def.get(ac)) and not live(act_use.get(ac, []))}
# types: registered (layer-shaped entries) vs resolved/occupant
for ty in sorted(set(typ_def) | set(typ_use)):
    symbols["types"]["cv://type/" + ty] = {
        "registered_in": sorted(set(typ_def.get(ty, []))),
        "consumed_in": sorted(set(typ_use.get(ty, []))),
        "ghost": not typ_def.get(ty) and bool(live(typ_use.get(ty, []))),
        "orphan": bool(typ_def.get(ty)) and not live(typ_use.get(ty, []))}
# decorators: vocabulary nodes (property-name consumption is not statically traceable —
# registered-only; no ghost/orphan judgement)
for dc in sorted(dec_def):
    symbols["decorators"]["cv://decorator/" + dc] = {"registered_in": sorted(set(dec_def[dc]))}
# events: emitted vs listened (a trigger's on:). Both directions can dangle:
# emitted-with-no-trigger = dead-letter · trigger-on-never-emitted = deaf.
for ev in sorted(set(ev_emit) | set(ev_on)):
    if ev == "*":
        continue
    symbols["events"]["cv://event/" + ev] = {
        "emitted_in": sorted(set(ev_emit.get(ev, []))), "listened_in": sorted(set(ev_on.get(ev, []))),
        "dead_letter": bool(live(ev_emit.get(ev, []))) and not live(ev_on.get(ev, [])),
        "deaf_trigger": bool(live(ev_on.get(ev, []))) and not live(ev_emit.get(ev, []))}
# skins: [data-skin=] scope defined vs applied; cross-checked against the skin axis values
skin_axis_vals = set(axes_reg.get("skin", {}).get("values", []))
for sk in sorted(set(skin_def) | set(skin_use) | skin_axis_vals):
    symbols["skins"]["cv://skin/" + sk] = {
        "scope_defined_in": sorted(set(skin_def.get(sk, []))),
        "applied_in": sorted(set(skin_use.get(sk, []))),
        "in_skin_axis": sk in skin_axis_vals,
        "ghost": (sk in skin_axis_vals or bool(skin_use.get(sk))) and not skin_def.get(sk)}

# ---------------------------------------------------------------- write
os.makedirs("registry", exist_ok=True)
reg = {"_meta": {"root": ROOT, "generated": STAMP, "by": "_system/substrate-map.py",
                 "entries": len(addr), "files": len(files), "edges_total": edges_total,
                 "ghost_files": sum(1 for e in addr.values() if e.get("kind") == "ghost"),
                 "leaf_zones": LEAF_ZONES},
       "addresses": addr}
json.dump(reg, open("registry/address-registry.json", "w"), indent=1)
json.dump(symbols, open("registry/symbol-registry.json", "w"), indent=1)

# ---------------------------------------------------------------- GAPS.md
def sect(title, rows):
    return ["## " + title + f" ({len(rows)})", ""] + rows + [""]

lines = ["# GAPS — claude-ds address-map gap list (derived; rerun _system/substrate-map.py)",
         f"_generated {STAMP} · files {len(files)} · edges {edges_total}_", ""]

gf = [(ga, len(g.get("edges_in", []))) for ga, g in addr.items() if g.get("kind") == "ghost"]
gf = [(a, n) for a, n in gf if not zone_of(a)]
lines += sect("GHOST FILES — referenced but do not exist (live zones)",
              [f"- `{a}` ← {n} refs (e.g. from `{addr[a]['edges_in'][0]['from']}`)"
               for a, n in sorted(gf, key=lambda x: -x[1])])

heal_live = [(f, t, r) for f, t, r in healed_edges if not zone_of(f)]
lines += sect("PATH DRIFT — reference healed by suffix-match (path in file ≠ layout)",
              [f"- `{f}` says `{t}` → actually `{r}`" for f, t, r in heal_live])

gt = [(k, v) for k, v in symbols["tokens"].items()
      if v.get("class") == "ghost-hard" and live(v["consumed_in"])]
lines += sect("GHOST TOKENS (hard) — var(--x) with NO fallback, --x defined nowhere",
              [f"- `{k.split('/')[-1]}` used in {len(v['consumed_in'])} file(s): " +
               ", ".join(f"`{p}`" for p in v["consumed_in"][:4]) for k, v in
               sorted(gt, key=lambda kv: -len(kv[1]["consumed_in"]))])

gtf = [(k, v) for k, v in symbols["tokens"].items()
       if v.get("class") == "ghost-family" and live(v["consumed_in"])]
lines += sect("GHOST TOKENS (family, fallback-masked) — name in a defined family, token missing (the --fs-micro class)",
              [f"- `{k.split('/')[-1]}` used in {len(v['consumed_in'])} file(s): " +
               ", ".join(f"`{p}`" for p in v["consumed_in"][:4]) for k, v in
               sorted(gtf, key=lambda kv: -len(kv[1]["consumed_in"]))])

gg = [(k, v) for k, v in symbols["globals"].items() if v["ghost"] and live(v["consumed_in"])]
lines += sect("GHOST GLOBALS — window.CV_* consumed, assigned nowhere",
              [f"- `{k.split('/')[-1]}` consumed in: " + ", ".join(f"`{p}`" for p in v["consumed_in"][:5])
               for k, v in sorted(gg, key=lambda kv: -len(kv[1]["consumed_in"]))])

gi = [(k, v) for k, v in symbols["icons"].items() if v["ghost"] and live(v["consumed_in"])]
lines += sect("GHOST ICONS — icon id used, not in CV_ICONS.data",
              [f"- `{k.split('/')[-1]}` used in: " + ", ".join(f"`{p}`" for p in v["consumed_in"][:4])
               for k, v in sorted(gi, key=lambda kv: -len(kv[1]["consumed_in"]))])

ga_ = [(k, v) for k, v in symbols["axes"].items() if v["ghost"] and live(v["consumed_in"])]
lines += sect("GHOST AXES — axis id resolved, never registered",
              [f"- `{k.split('/')[-1]}` consumed in: " + ", ".join(f"`{p}`" for p in v["consumed_in"][:4])
               for k, v in ga_])

gac = [(k, v) for k, v in symbols["actions"].items() if v["ghost"]]
lines += sect("GHOST ACTIONS — invoked / wired (do:/onPick:), never registered",
              [f"- `{k.split('/')[-1]}` invoked in: " + ", ".join(f"`{p}`" for p in v["invoked_in"][:4])
               for k, v in gac])

gty = [(k, v) for k, v in symbols["types"].items() if v["ghost"]]
lines += sect("GHOST TYPES — resolved / used as occupant, never registered",
              [f"- `{k.split('/')[-1]}` consumed in: " + ", ".join(f"`{p}`" for p in v["consumed_in"][:4])
               for k, v in gty])

gsk = [(k, v) for k, v in symbols["skins"].items() if v["ghost"]]
lines += sect("GHOST SKINS — in the skin axis / applied, but no [data-skin] scope in tokens/skins.css",
              [f"- `{k.split('/')[-1]}`" for k, v in gsk])

gdl = [(k, v) for k, v in symbols["events"].items() if v["dead_letter"]]
lines += sect("DEAD-LETTER EVENTS — emitted, no trigger listens",
              [f"- `{k.split('/')[-1]}` emitted in: " + ", ".join(f"`{p}`" for p in v["emitted_in"][:4])
               for k, v in gdl])

gdf = [(k, v) for k, v in symbols["events"].items() if v["deaf_trigger"]]
lines += sect("DEAF TRIGGERS — a trigger listens for an event nothing emits",
              [f"- `{k.split('/')[-1]}` listened in: " + ", ".join(f"`{p}`" for p in v["listened_in"][:4])
               for k, v in gdf])

ot = [k.split("/")[-1] for k, v in symbols["tokens"].items()
      if v["orphan"] and not all(zone_of(d) for d in v["defined_in"])]
lines += sect("ORPHAN TOKENS — defined, consumed nowhere", ["- `" + t + "`" for t in ot])

oi = [k.split("/")[-1] for k, v in symbols["icons"].items() if v["orphan"]]
lines += sect("ORPHAN ICONS — registered, no live consumer", ["- `" + i + "`" for i in oi])

og = [k.split("/")[-1] for k, v in symbols["globals"].items() if v["orphan"]]
lines += sect("ORPHAN GLOBALS — defined, no live consumer", ["- `" + g + "`" for g in og])

oax = [k.split("/")[-1] for k, v in symbols["axes"].items() if v["orphan"]]
lines += sect("ORPHAN AXES — registered, no live consumer", ["- `" + a + "`" for a in oax])

oac = [k.split("/")[-1] for k, v in symbols["actions"].items() if v["orphan"]]
lines += sect("ORPHAN ACTIONS — registered, never invoked/wired", ["- `" + a + "`" for a in oac])

oty = [k.split("/")[-1] for k, v in symbols["types"].items() if v["orphan"]]
lines += sect("ORPHAN TYPES — registered, never resolved (galleries render all; static named use only)",
              ["- `" + t + "`" for t in oty])

# raw colours: aggregate by VALUE, matched back to the token that already holds it
tok_by_value = {}
for tk, fs in t_def.items():
    pass
val_of_token = {}
for a in files:
    if TOKEN_HOME(a):
        for m in re.finditer(r'(--[a-zA-Z][\w-]*)\s*:\s*(#[0-9a-fA-F]{3,6})\s*;', read(a)):
            val_of_token.setdefault(m.group(2).lower(), m.group(1))
by_val = {}
for a, hits in raw_colors.items():
    for v, n in hits.items():
        by_val.setdefault(v, {"n": 0, "files": []})
        by_val[v]["n"] += n
        by_val[v]["files"].append(a)
rc_rows = []
for v, d in sorted(by_val.items(), key=lambda kv: -kv[1]["n"]):
    tok = val_of_token.get(v)
    rc_rows.append(f"- `{v}` ×{d['n']} in {len(d['files'])} file(s)" +
                   (f" — TOKEN EXISTS: `{tok}` (mechanical fix)" if tok else " — no exact token (needs a naming/design call)") +
                   " · e.g. " + ", ".join(f"`{p}`" for p in d["files"][:3]))
lines += sect("RAW COLOURS — literal colours in live styling files, outside var() fallbacks (should use tokens)", rc_rows)

open("registry/GAPS.md", "w").write("\n".join(lines))

# persist the gap scoreboard in the registry so the GATE diffs data, not prose
symbols["_meta"]["gap_counts"] = {
    "ghost_files_live": len(gf), "ghost_tokens_hard": len(gt), "ghost_tokens_family": len(gtf),
    "ghost_globals": len(gg), "ghost_icons": len(gi), "ghost_axes": len(ga_),
    "ghost_actions": len(gac), "ghost_types": len(gty), "ghost_skins": len(gsk),
    "dead_letter_events": len(gdl), "deaf_triggers": len(gdf),
    "orphan_tokens": len(ot), "orphan_icons": len(oi), "orphan_globals": len(og),
    "orphan_axes": len(oax), "orphan_actions": len(oac), "orphan_types": len(oty),
    "raw_colour_values": len(by_val), "path_drift_heals": len(heal_live),
}
symbols["_meta"]["ghost_keys"] = sorted(
    [k for k, v in symbols["tokens"].items() if v["ghost"]] +
    [k for k, v in symbols["icons"].items() if v["ghost"]] +
    [k for k, v in symbols["globals"].items() if v["ghost"]] +
    [k for k, v in symbols["axes"].items() if v["ghost"]] +
    [k for k, v in symbols["actions"].items() if v["ghost"]] +
    [k for k, v in symbols["types"].items() if v["ghost"]])
json.dump(symbols, open("registry/symbol-registry.json", "w"), indent=1)

print(f"addresses {len(addr)} · files {len(files)} · edges {edges_total} · healed {len(heal_live)}")
print(f"ghost files (live) {len(gf)} · ghost tokens hard {len(gt)} family {len(gtf)} · ghost globals {len(gg)} · ghost icons {len(gi)} · ghost axes {len(ga_)}")
print(f"orphan tokens {len(ot)} · orphan icons {len(oi)} · orphan globals {len(og)} · orphan axes {len(oax)}")
print(f"symbols: globals {len(symbols['globals'])} tokens {len(symbols['tokens'])} icons {len(symbols['icons'])} axes {len(symbols['axes'])} glyphs {symbols['glyphs']}")
print(f"  + types {len(symbols['types'])} actions {len(symbols['actions'])} decorators {len(symbols['decorators'])} events {len(symbols['events'])} skins {len(symbols['skins'])}")
print(f"ghost actions {len(gac)} · ghost types {len(gty)} · ghost skins {len(gsk)} · dead-letter events {len(gdl)} · deaf triggers {len(gdf)}")
print(f"orphan actions {len(oac)} · orphan types {len(oty)}")
parametric = sum(1 for v in symbols['tokens'].values() if v.get('class') == 'parametric')
print(f"parametric contract tokens (fallback-only, by design): {parametric}")
