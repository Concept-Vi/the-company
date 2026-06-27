"""codeedges.py — the STRUCTURAL CODE-DEPENDENCY GRAPH: symbol→symbol calls/imports
(Convergence X10).

⚠ SUPERSEDED (2026-06-27, the-one-system): `code-edges.json` is now GENERATED FROM THE LEDGER
(`ops/ledger_build.py --emit-legacy`) — whole-tree + resolved (4,900+ symbols vs this subset build's
~430), the ledger being the one canonical structural store. This standalone AST build is RETIRED;
keep it only as reference/fallback. Consumers (suite.blast_radius, refcheck, the acceptance tests)
are unchanged — they read the same `code-edges.json`, now ledger-sourced. See
build-prep/the-one-system/LEDGER-SPEC.md §8.

Run (legacy/standalone):
    python3 codeedges.py
Where symbols.py is the REVERSE index (a symbol → which CORPUS THINGS reference it — a
feature-id / ui:// address) and refcheck.py is the FORWARD pass (a ref → does it still
resolve), THIS is the third, net-new branch: which SYMBOL depends on which other SYMBOL.
That symbol→symbol code-dependency graph existed NOWHERE — the reverse-index's
`referenced_by`/`shared` is corpus-artifact→symbol, not symbol→symbol. X10 builds it: it
parses the real Python source under ~/company (READ-ONLY, stdlib `ast`), and for each
DEFINED symbol records the OTHER known symbols it calls/imports → `depends_on[]`, inverted
to `depended_by[]`, keyed by the EXISTING code://<file-stem>/<symbol> ids symbols.py uses
(one coordinate system — `symbol_id` is REUSED from symbols.py, never re-implemented). This
is the substrate that turns the address-graph from points into a RELATIONAL graph:
`depended_by` = dependents-to-VERIFY, `depends_on` = dependencies-to-RESPECT for a pointed
self-build (the blast radius, X14).

Emits `code-edges.json` = {code://id: {depends_on[], depended_by[], resolves}} + a `stale[]`
honesty list (mirrors refcheck/symbols: an unparseable source file is a stale, resolves:false
entry — fail-loud-legible, NEVER a silent skip or a crash) + a summary.

BOUNDED REACH (the explosion guard). A transitive code-dependency graph can degenerate to
all-touches-all (a core symbol — e.g. a logger — is reached from everywhere). So we store
only DIRECT edges and expose a BOUNDED transitive query (`reach` / `reach_report`) capped at
the named DEPTH constant (2–3 hops, per Tim; the depth is the X17-configurable knob — read
from env CODEEDGES_DEPTH, default 2). A reach that hits the bound is REPORTED as `capped`
(no silent truncation). We do NOT precompute the transitive closure into the file — that is
exactly where the explosion would live; the bound lives in the query.

RESOLUTION (precise, not a degenerate fan). A referenced name is resolved to a target id by
precedence, highest-confidence first — so a bare `run()` (defined in 18 node files) does NOT
fan out to all 18:
  1. SAME-FILE definition         (a method/function defined in the same file as the caller)
  2. EXPLICIT import              (`from scheduler import tick` / `import scheduler` then
                                   `scheduler.tick()` → the imported module's file)
  3. UNAMBIGUOUS global           (the name is defined in exactly ONE file across the corpus)
  4. AMBIGUOUS / unknown          (defined in 2+ files with no import/same-file signal, or not
                                   defined anywhere) → NOT an edge; tallied honestly in the
                                   summary as `unresolved_refs`, never exploded into a fan.

Built ON symbols.py (reuse, not reimplement): `symbol_id`, `_stem`, and the resolver
seam (`refcheck._resolve` / SEARCH_DIRS / COMPANY) for the on-disk READ-ONLY walk. The
`read` seam is injectable so the test stays hermetic (inline fixtures, no ~/company)."""
import os, ast, json
import refcheck
import symbols

# one coordinate system — REUSE symbols.py's id scheme, never a parallel.
symbol_id = symbols.symbol_id
_stem = symbols._stem
COMPANY = refcheck.COMPANY
SEARCH_DIRS = refcheck.SEARCH_DIRS

# X17-configurable: the bounded transitive reach (2–3 hops per Tim). Default = 2.
# A literal would violate D2 (everything configurable); read the knob, keep the default as floor.
DEPTH = int(os.environ.get("CODEEDGES_DEPTH", "2"))
if DEPTH not in (2, 3):
    # fail-loud-legible: an out-of-range knob is a config error, not a silent clamp.
    raise ValueError(f"CODEEDGES_DEPTH must be 2 or 3 (Tim's bound); got {DEPTH!r}")


def list_company_py(search_dirs=SEARCH_DIRS, company=COMPANY) -> list:
    """The repo-relative paths of every .py file under the same SEARCH_DIRS refcheck/symbols
    search, READ-ONLY. Deterministic (sorted). __pycache__ is skipped (not source)."""
    seen, out = set(), []
    for d in search_dirs:
        base = os.path.join(company, d) if d else company
        if not os.path.isdir(base):
            continue
        for f in sorted(os.listdir(base)):
            if not f.endswith(".py"):
                continue
            rel = os.path.normpath(os.path.join(d, f)) if d else f
            if rel not in seen:
                seen.add(rel)
                out.append(rel)
    return out


def _read_company(repo_path: str, company=COMPANY):
    """READ-ONLY read of a repo-relative source path under ~/company. Returns text or None.
    This is the on-disk `read` seam the test replaces with an inline fixture."""
    full = os.path.join(company, repo_path)
    if not os.path.isfile(full):
        return None
    with open(full, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _defs_in(tree: ast.AST, stem: str):
    """Every function/class DEFINED in this module → {name: code://id}. Nested defs and methods
    are included (keyed by their own name; the id is code://<file-stem>/<name>, matching
    symbols.py which keys by name within a file). First definition of a name in the file wins
    (the canonical site), mirroring symbols._all_defs."""
    out = {}
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if n.name not in out:
                out[n.name] = f"code://{stem}/{n.name}"
    return out


def _imports_in(tree: ast.AST):
    """The import map for a module → {local_name: module_stem}.
      `from scheduler import tick`        → {'tick': 'scheduler'}
      `from runtime.suite import Suite`   → {'Suite': 'suite'}   (last path segment = the stem)
      `from x import y as z`              → {'z': 'x'}
      `import scheduler`                  → {'scheduler': 'scheduler'}
      `import runtime.suite as s`         → {'s': 'suite'}
    The stem is the basename of the module path (matches symbols._stem: 'runtime/suite.py'
    and 'suite.py' collapse to stem 'suite')."""
    mod_alias, name_from = {}, {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                stem = a.module.split(".")[-1] if hasattr(a, "module") else a.name.split(".")[-1]
                local = a.asname or a.name.split(".")[0]
                mod_alias[local] = a.name.split(".")[-1]
        elif isinstance(n, ast.ImportFrom):
            mod = (n.module or "").split(".")[-1]
            for a in n.names:
                local = a.asname or a.name
                name_from[local] = mod
    return mod_alias, name_from


def _refs_in_symbol(node: ast.AST):
    """Within ONE defining symbol's body, the names + attribute-accesses it references.
    Returns (called_or_named[], attr_calls[]). `called_or_named` = plain Name targets of a
    Call AND bare Name loads (a function passed/used). `attr_calls` = the .attr part of an
    Attribute (e.g. self.resolve() → 'resolve'; scheduler.tick() → ('scheduler','tick'))."""
    names, attrs = [], []
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            fn = n.func
            if isinstance(fn, ast.Name):
                names.append(fn.id)
            elif isinstance(fn, ast.Attribute):
                # obj.attr() — record the attr; and if obj is a plain Name, the module/object too.
                base = fn.value.id if isinstance(fn.value, ast.Name) else None
                attrs.append((base, fn.attr))
        elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
            names.append(n.id)
        elif isinstance(n, ast.Attribute):
            base = n.value.id if isinstance(n.value, ast.Name) else None
            attrs.append((base, n.attr))
    return names, attrs


def build_graph(files: list, read=_read_company) -> dict:
    """Parse every file (READ-ONLY via the `read` seam), build the symbol→symbol edge graph.
    Returns the full code-edges.json doc shape ({_what, edges, stale, summary}).

    Two passes:
      PASS 1 — parse each file; collect its defs (name→id), imports, and AST. An unparseable
               file → a `stale` entry (resolves:false) — fail-loud-legible, never dropped.
      PASS 2 — for each defined symbol, resolve the names/attrs in its body to OTHER known
               symbol ids by the precedence above; record depends_on + invert to depended_by."""
    parsed = {}                  # repo_path -> {stem, defs:{name:id}, mod_alias, name_from, tree}
    stale = []                   # unparseable / unreadable files (fail-loud honesty list)
    global_name_ids = {}         # name -> set(ids) across the whole corpus (for the global pass)

    # ---- PASS 1: parse + index every file --------------------------------------------
    for rel in files:
        src = read(rel)
        if src is None:
            stale.append({"file": rel, "reason": "not found / unreadable", "resolves": False})
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError as e:
            # fail-loud-legible: an unparseable source file is recorded, never silently skipped.
            stale.append({"file": rel, "reason": f"SyntaxError: {e}", "resolves": False})
            continue
        stem = _stem(rel)
        defs = _defs_in(tree, stem)
        mod_alias, name_from = _imports_in(tree)
        parsed[rel] = {"stem": stem, "defs": defs, "mod_alias": mod_alias,
                       "name_from": name_from, "tree": tree}
        for name, sid in defs.items():
            global_name_ids.setdefault(name, set()).add(sid)

    # stem -> the set of ids defined in files of that stem (for import-resolution by module).
    stem_name_id = {}            # (stem, name) -> id
    for info in parsed.values():
        for name, sid in info["defs"].items():
            stem_name_id[(info["stem"], name)] = sid

    edges = {}                   # id -> {depends_on:set, depended_by:set, resolves:True}
    unresolved_refs = 0          # ambiguous/unknown names that did NOT become an edge (honest tally)

    def ensure(sid):
        if sid not in edges:
            edges[sid] = {"depends_on": set(), "depended_by": set(), "resolves": True}
        return edges[sid]

    # seed an entry for every defined symbol (so a leaf with no deps still appears, like
    # symbols.py lists every referenced symbol).
    for info in parsed.values():
        for sid in info["defs"].values():
            ensure(sid)

    def resolve_name(name, this_file_info):
        """A bare name → its target id by precedence (same-file > import > unambiguous-global).
        Returns an id or None (ambiguous/unknown — NOT an edge)."""
        if name in this_file_info["defs"]:                          # 1. same-file def
            return this_file_info["defs"][name]
        if name in this_file_info["name_from"]:                     # 2a. `from mod import name`
            tgt = stem_name_id.get((this_file_info["name_from"][name], name))
            if tgt:
                return tgt
        ids = global_name_ids.get(name)                             # 3. unambiguous global
        if ids and len(ids) == 1:
            return next(iter(ids))
        return None                                                 # 4. ambiguous/unknown

    def resolve_attr(base, attr, this_file_info):
        """`base.attr` → target id. `self.attr`/`cls.attr` → same-file method (precedence 1-ish);
        `module.attr` where `module` is an imported alias → that module's symbol; else fall back
        to bare-name resolution on `attr`."""
        if base in ("self", "cls"):                                 # method on the same object
            if attr in this_file_info["defs"]:
                return this_file_info["defs"][attr]
            return resolve_name(attr, this_file_info)
        if base in this_file_info["mod_alias"]:                     # imported module.attr
            tgt = stem_name_id.get((this_file_info["mod_alias"][base], attr))
            if tgt:
                return tgt
        if base in this_file_info["name_from"]:                     # rare: from x import obj; obj.attr
            tgt = stem_name_id.get((this_file_info["name_from"][base], attr))
            if tgt:
                return tgt
        return resolve_name(attr, this_file_info)                   # else resolve the attr name

    # ---- PASS 2: resolve each symbol's body refs to edges ----------------------------
    for rel, info in parsed.items():
        # map each defining node to its id, then resolve the refs in its body.
        for node in ast.walk(info["tree"]):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            src_id = info["defs"].get(node.name)
            if src_id is None:
                continue
            names, attrs = _refs_in_symbol(node)
            targets = set()
            for nm in names:
                if nm == node.name:                                 # ignore self-recursion
                    continue
                tid = resolve_name(nm, info)
                if tid and tid != src_id:
                    targets.add(tid)
                elif tid is None and nm in global_name_ids:
                    unresolved_refs += 1                            # ambiguous known name, no signal
            for base, attr in attrs:
                tid = resolve_attr(base, attr, info)
                if tid and tid != src_id:
                    targets.add(tid)
                elif tid is None and attr in global_name_ids:
                    unresolved_refs += 1
            for tid in targets:
                ensure(src_id)["depends_on"].add(tid)
                ensure(tid)["depended_by"].add(src_id)

    # freeze sets → sorted lists (deterministic, json-serialisable).
    for e in edges.values():
        e["depends_on"] = sorted(e["depends_on"])
        e["depended_by"] = sorted(e["depended_by"])

    shared = sorted(sid for sid, e in edges.items() if len(e["depended_by"]) >= 2)
    return {
        "_what": "THE STRUCTURAL CODE-DEPENDENCY GRAPH (Convergence X10) — symbol→symbol "
                 "calls/imports, the relational layer the reverse-index (symbols.py) lacks. "
                 "GENERATED by _system/codeedges.py parsing ~/company source READ-ONLY (stdlib "
                 "ast). Keyed by the SAME code://<file-stem>/<symbol> ids symbols.py uses (one "
                 "coordinate system — symbol_id is REUSED, no parallel). Each entry: depends_on[] "
                 "(dependencies-to-RESPECT) · depended_by[] (dependents-to-VERIFY) · resolves. "
                 "DIRECT edges only are stored; the transitive reach is a BOUNDED query capped at "
                 "DEPTH (2-3 hops, X17-configurable via CODEEDGES_DEPTH) — see codeedges.reach / "
                 "reach_report; a reach that hits the bound is reported `capped` (no silent "
                 "truncation; the explosion guard lives in the query, not the file). An "
                 "unparseable/unreadable source file is a stale[] entry (resolves:false) — "
                 "fail-loud-legible, never a silent skip. Resolution is precise (same-file > "
                 "import > unambiguous-global); an ambiguous bare name (e.g. run(), defined in 18 "
                 "node files) does NOT fan out — it is tallied as unresolved_refs, not exploded. "
                 "SIBLING of code-symbols.json (X10 does not modify symbols.py — that is X11, "
                 "semantic edges). REGENERATE after the ~/company source changes. The blast_radius "
                 "(X14) reads this for the structural dependents/dependencies of a pointed scope.",
        "edges": edges,
        "stale": stale,
        "summary": {
            "files_parsed": len(parsed),
            "files_stale": len(stale),
            "symbols": len(edges),
            "with_depends_on": sum(1 for e in edges.values() if e["depends_on"]),
            "with_depended_by": sum(1 for e in edges.values() if e["depended_by"]),
            "shared_2plus_dependents": len(shared),
            "unresolved_refs": unresolved_refs,
            "depth": DEPTH,
        },
        "shared": shared,
    }


def reach(start: str, edges: dict, depth=DEPTH) -> set:
    """The BOUNDED transitive set of symbols `start` depends on, within `depth` hops (the
    explosion guard — a chain longer than depth does NOT leak edges beyond the cap). BFS over
    depends_on; the start itself is excluded. depth=1 = direct deps only."""
    frontier = {start}
    reached = set()
    for _ in range(depth):
        nxt = set()
        for sid in frontier:
            for dep in edges.get(sid, {}).get("depends_on", []):
                if dep not in reached and dep != start:
                    nxt.add(dep)
        nxt -= reached
        if not nxt:
            break
        reached |= nxt
        frontier = nxt
    return reached


def reach_report(start: str, edges: dict, depth=DEPTH) -> dict:
    """Like `reach`, but reports WHETHER the bound was hit — so a capped reach is legible, not a
    silent truncation. `capped`=True means there were still un-walked deps at the depth limit
    (the graph continues past the bound; we stopped on purpose)."""
    frontier = {start}
    reached = set()
    capped = False
    for hop in range(depth):
        nxt = set()
        for sid in frontier:
            for dep in edges.get(sid, {}).get("depends_on", []):
                if dep != start:
                    nxt.add(dep)
        nxt -= reached
        nxt.discard(start)
        if not nxt:
            break
        reached |= nxt
        frontier = nxt
        if hop == depth - 1:
            # at the last allowed hop — is there anything one step further? then it's capped.
            for sid in frontier:
                further = set(edges.get(sid, {}).get("depends_on", [])) - reached - {start}
                if further:
                    capped = True
                    break
    return {"start": start, "depth": depth, "reached": sorted(reached), "capped": capped}


def _validate(doc: dict):
    """Fail LOUD on a malformed graph we just built (self-check before it's trusted)."""
    if not isinstance(doc.get("edges"), dict):
        raise ValueError("code-edges.json malformed: 'edges' is not a dict")
    for sid, e in doc["edges"].items():
        if not sid.startswith("code://"):
            raise ValueError(f"code-edges.json malformed: id {sid!r} is not a code:// id")
        for k in ("depends_on", "depended_by", "resolves"):
            if k not in e:
                raise ValueError(f"code-edges.json malformed: {sid} missing {k!r}")


def run_corpus():
    """Build the structural graph over the real ~/company source; write code-edges.json; print
    a summary. READ-ONLY on ~/company (parses it; never modifies it)."""
    here = os.path.dirname(os.path.abspath(__file__))
    files = list_company_py()
    doc = build_graph(files)
    _validate(doc)
    out = os.path.join(here, "code-edges.json")
    json.dump(doc, open(out, "w", encoding="utf-8"), indent=2)
    s = doc["summary"]
    print("codeedges (structural symbol→symbol graph, X10) — summary:")
    for k, v in s.items():
        print(f"  {k}: {v}")
    if doc["shared"]:
        print(f"  → {len(doc['shared'])} symbols depended-on by 2+ others (ripple-on-change):")
        for sid in doc["shared"][:15]:
            print(f"    {sid}  ←  {len(doc['edges'][sid]['depended_by'])} dependents")
        if len(doc["shared"]) > 15:
            print(f"    … and {len(doc['shared']) - 15} more")
    if doc["stale"]:
        print("  → STALE (unparseable/unreadable — fail-loud, not dropped):")
        for st in doc["stale"]:
            print(f"    {st['file']}: {st['reason']}")
    return doc


def main():
    run_corpus()


if __name__ == "__main__":
    main()
