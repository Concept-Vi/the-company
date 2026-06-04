"""symbols.py — the CODE-SYMBOL REGISTRY: the `code://` branch of the universal coordinate
(Block 17-18). Run:
    python3 symbols.py
Where refcheck.py is the FORWARD pass (a ref → does it still resolve?), this is the REVERSE
index (a symbol → WHO references it). It reads EVERY `code` value from register.json
(features[].code) AND addresses.json (addresses.*.code) — the same source set refcheck reads
— resolves each ref against the real source under ~/company (READ-ONLY), and turns every code
symbol the corpus references into an ADDRESSABLE ENTITY keyed by a stable id
(code://<resolved-file-stem>/<symbol>, e.g. code://suite/resolve_surfaced). Each entry records
the file, the symbol, its kind (def | class | route | const | file-only), whether it currently
resolves, and — the NEW information beyond refcheck — `referenced_by`: every feature-id and
ui:// address that points at that one symbol. Shared symbols (referenced by 2+ corpus things)
fall straight out of the reverse merge. A symbol named in a `path:symbol` ref that is ABSENT
from the file resolves:false — that IS a drift signal.

Built ON refcheck (reuse, not reimplement): collect_refs (+ its LOUD malformed-registry
checks), split_refs, parse_ref, _resolve, _all_defs, _nearest_def. The resolver is an injectable
seam (resolve=refcheck._resolve) so the test stays hermetic (inline fixtures, no ~/company).

The model layer extends this later (see mechanisms.json · code-symbol-registry): a model
annotates each symbol with what it ACTUALLY does, and flags where a symbol is referenced by a
feature whose represents-claim it doesn't match (semantic, on top of this structural reverse map).

ref FORMS handled (none silently dropped):
  • path:symbol  (runtime/suite.py:run)        → the named symbol; kind from its def line; resolves = present in file.
  • path:line    (scheduler.py:37)             → the ENCLOSING def (nearest preceding); kind from that def line.
  • path only    (nodes/embed.py)              → kind=file-only, no symbol; resolves = file found.
  • Suite.verb   (Suite.run)                    → grep bridge.py for the verb; kind=route (api face).
  • /api/...                                    → route literal in bridge.py; kind=route.
  • glob / dir   (nodes/*.py, voice/)          → NOT a symbol entry → index_ref returns None (counted in the
                                                  summary as 'not indexable as a symbol', never silently skipped).
Compound refs (' / ' and ' + ' separated) are split (refcheck.split_refs); each sub-ref is indexed independently."""
import os, re, json
import refcheck

COMPANY = refcheck.COMPANY

# classify the def/class/declaration KIND from the source line that DECLARES the symbol.
# refcheck's _PYDEF/_TSXDEF capture the NAME only; we read the keyword here to assign kind.
_KW = re.compile(
    r'^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?(?P<kw>def|class|function|const|let|var)\b')

# code file extensions — a ref to one of these that does NOT resolve is genuine drift (the file
# churned away). A non-code extension (.css/.html) was never a code symbol → not_indexable.
_CODE_EXTS = (".py", ".ts", ".tsx", ".js", ".jsx")


def _find_decl(lines: list, symbol: str):
    """Find the 1-based line that DECLARES `symbol`, including forms refcheck's _all_defs misses
    (notably tsx `export default function App()`). Returns the lineno or None. This is symbols.py
    owning the EXACT per-symbol resolution its reverse-index purpose needs (refcheck is forward/
    approximate 'near a def'; the reverse index needs precise 'is this named symbol defined here')."""
    pat = re.compile(
        r'^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?'
        r'(?:def|class|function|const|let|var)\s+' + re.escape(symbol) + r'\b')
    for i, ln in enumerate(lines):
        if pat.match(ln):
            return i + 1
    return None


def _kind_from_line(line: str) -> str:
    """The line that declares a symbol → its kind in the CLOSED set def|class|const.
    py 'def'/'async def' → def · 'class' → class · tsx 'function' → def ·
    tsx 'const'/'let'/'var' → const. Unknown (no recognised keyword) → def (a captured
    declaration we can't otherwise classify is treated as a definition site)."""
    m = _KW.match(line or "")
    if not m:
        return "def"
    kw = m.group("kw")
    if kw == "class":
        return "class"
    if kw in ("const", "let", "var"):
        return "const"
    return "def"  # def / async def / function


def _stem(repo_path: str) -> str:
    """Repo-relative file → stable stem for the id (basename without extension).
    'runtime/suite.py' → 'suite'; 'canvas/app/src/App.tsx' → 'App'; 'nodes/embed.py' → 'embed'.
    Both 'suite.py' and 'runtime/suite.py' resolve to the SAME repo file, so refs in either
    form collapse to one stem → one symbol id (the unification the reverse index needs)."""
    return os.path.splitext(os.path.basename(repo_path))[0]


def symbol_id(repo_path: str, symbol) -> str:
    """The stable code:// id. code://<file-stem>/<symbol>, or code://<file-stem> when there
    is no symbol (a file-only ref)."""
    stem = _stem(repo_path)
    return f"code://{stem}/{symbol}" if symbol else f"code://{stem}"


def index_ref(ref: str, resolve=refcheck._resolve, bridge_lines=None):
    """Index ONE sub-ref → {id, file, symbol, kind, resolves} or None if the form is not a
    symbol (glob/dir/unresolvable form — counted in the summary, never silently dropped).
    `file` is the RESOLVED repo-relative path when the ref resolves (so the id is stable across
    bare/qualified forms); the raw path's stem is the fallback id when it does NOT resolve."""
    ref = ref.strip()

    # /api/... → a route literal; resolves iff present in bridge.py.
    if ref.startswith("/api/"):
        bl = bridge_lines if bridge_lines is not None else (resolve("bridge.py") or (None, []))[1]
        hit = any(ref in ln for ln in bl)
        bres = resolve("bridge.py")
        bfile = bres[0] if bres else "runtime/bridge.py"
        return {"id": f"code://{_stem(bfile)}/{ref}", "file": bfile, "symbol": ref,
                "kind": "route", "resolves": bool(hit)}

    head = ref.split()[0] if ref.split() else ref

    # Suite.verb form (Capitalised.method, NO path, single token) — grep bridge.py for the verb.
    # fullmatch on the WHOLE ref (as refcheck does) so 'App.tsx NodeShapeUtil:124' (has a space →
    # it's a file:line ref, not a Suite.verb) does NOT get mis-read as verb 'tsx'. Checked BEFORE
    # file-parsing so 'Suite.do_POST' is NOT read as a file named 'Suite.do_POST'.
    if re.fullmatch(r'[A-Z]\w*\.\w+', ref):
        verb = head.split(".")[-1]
        bl = bridge_lines if bridge_lines is not None else (resolve("bridge.py") or (None, []))[1]
        pat = re.compile(r'\b(?:def|class)\s+' + re.escape(verb) + r'\b')
        bare = re.compile(r'\b' + re.escape(verb) + r'\b')
        hit = any(pat.search(ln) for ln in bl) or any(bare.search(ln) for ln in bl)
        bres = resolve("bridge.py")
        bfile = bres[0] if bres else "runtime/bridge.py"
        return {"id": f"code://{_stem(bfile)}/{verb}", "file": bfile, "symbol": verb,
                "kind": "route", "resolves": bool(hit)}

    # glob / bare directory / no-file token → NOT a symbol entry (refcheck's unverifiable form).
    if "*" in ref or ref.endswith("/") or "." not in head:
        return None  # glob (nodes/*.py) / dir (voice/) — reported by the caller, not indexed.

    f, line, hint = refcheck.parse_ref(ref)
    if not f:
        return None  # no resolvable file head (already handled the api/Suite.verb cases above).

    res = resolve(f)
    if res is None:
        # file not found under ~/company code dirs. Discriminate by extension (mirrors refcheck's
        # 'non-code file → unverifiable, not drift'): a NON-code ext (.css/.html — e.g. a CSS
        # selector) was never a code symbol → return None so the caller lists it under
        # not_indexable. A CODE ext that doesn't resolve is genuine drift (file churned away).
        ext = os.path.splitext(f)[1].lower()
        if ext not in _CODE_EXTS:
            return None
        symbol = None
        if hint.startswith(":") and not hint[1:].lstrip().isdigit():
            symbol = hint[1:].strip() or None
        kind = "file-only" if symbol is None else "def"
        return {"id": symbol_id(f, symbol), "file": f, "symbol": symbol,
                "kind": kind, "resolves": False}

    repo_path, lines = res
    defs = refcheck._all_defs(lines)

    # path:symbol — the symbol name is the remainder hint ':<name>' (a non-numeric tail).
    if hint.startswith(":") and not hint[1:].lstrip().isdigit():
        symbol = hint[1:].strip()
        declline = defs.get(symbol) or _find_decl(lines, symbol)  # _all_defs first, then the
        if declline:                                              # forms it misses (export default).
            kind = _kind_from_line(lines[declline - 1])
            return {"id": symbol_id(repo_path, symbol), "file": repo_path, "symbol": symbol,
                    "kind": kind, "resolves": True}
        # named symbol genuinely ABSENT from the file → drift signal.
        return {"id": symbol_id(repo_path, symbol), "file": repo_path, "symbol": symbol,
                "kind": "def", "resolves": False}

    # path:line — the symbol is the ENCLOSING def (nearest preceding); kind from that def line.
    if line is not None:
        if line < 1 or line > len(lines):
            return {"id": symbol_id(repo_path, None), "file": repo_path, "symbol": None,
                    "kind": "file-only", "resolves": False}
        sym, defline, dist = refcheck._nearest_def(lines, line - 1)
        if sym is None:
            return {"id": symbol_id(repo_path, None), "file": repo_path, "symbol": None,
                    "kind": "file-only", "resolves": False}
        kind = _kind_from_line(lines[defline - 1])
        return {"id": symbol_id(repo_path, sym), "file": repo_path, "symbol": sym,
                "kind": kind, "resolves": True}

    # path only — file-only ref; resolves because the file was found.
    return {"id": symbol_id(repo_path, None), "file": repo_path, "symbol": None,
            "kind": "file-only", "resolves": True}


def build_index(items: list, resolve=refcheck._resolve) -> dict:
    """The REVERSE index. Given collect_refs-shaped items ({raw, source, owner, label}),
    split each raw into sub-refs, index each, and COLLAPSE every ref that lands on the same
    id into ONE entry whose `referenced_by` is the de-duped, sorted list of owners pointing at
    it. Returns {id: {file, symbol, kind, resolves, referenced_by[]}}.
    Collision guard: if two refs hit the same id but DIFFERENT resolved files, that's a real
    id collision — recorded under entry['_collision'] (surfaced, never silently merged)."""
    bres = resolve("bridge.py")
    bridge_lines = bres[1] if bres else []
    reg = {}
    for it in items:
        for sub in refcheck.split_refs(it["raw"]):
            ent = index_ref(sub, resolve=resolve, bridge_lines=bridge_lines)
            if ent is None:
                continue  # glob/dir — not a symbol; the caller tallies these separately.
            sid = ent["id"]
            if sid not in reg:
                reg[sid] = {"file": ent["file"], "symbol": ent["symbol"], "kind": ent["kind"],
                            "resolves": ent["resolves"], "referenced_by": []}
            else:
                prev = reg[sid]
                if prev["file"] != ent["file"]:
                    prev.setdefault("_collision", []).append(ent["file"])
                # a resolving sighting wins (prefer the form that actually landed a symbol).
                if ent["resolves"] and not prev["resolves"]:
                    prev.update({"file": ent["file"], "symbol": ent["symbol"],
                                 "kind": ent["kind"], "resolves": True})
            if it["owner"] not in reg[sid]["referenced_by"]:
                reg[sid]["referenced_by"].append(it["owner"])
    for ent in reg.values():
        ent["referenced_by"].sort()
    return reg


def shared_symbols(reg: dict) -> list:
    """The ids referenced by 2+ corpus things — the shared symbols (a change there ripples to
    multiple features/addresses). Falls straight out of the reverse merge."""
    return sorted(sid for sid, e in reg.items() if len(e["referenced_by"]) >= 2)


def build_registry(register: dict, addresses: dict, resolve=refcheck._resolve) -> dict:
    """Assemble the emitted doc. Reuses refcheck.collect_refs (which fails LOUD on a malformed
    registry). Returns the full code-symbols.json shape (with _what + summary)."""
    items = refcheck.collect_refs(register, addresses)  # raises ValueError on malformed input.
    # tally the non-symbol forms (glob/dir) honestly, so nothing is silently dropped.
    not_indexable = []
    bres = resolve("bridge.py")
    bridge_lines = bres[1] if bres else []
    for it in items:
        for sub in refcheck.split_refs(it["raw"]):
            if index_ref(sub, resolve=resolve, bridge_lines=bridge_lines) is None:
                not_indexable.append({"owner": it["owner"], "ref": sub})

    reg = build_index(items, resolve=resolve)
    shared = shared_symbols(reg)
    unresolved = sorted(sid for sid, e in reg.items() if not e["resolves"])
    collisions = sorted(sid for sid, e in reg.items() if e.get("_collision"))
    return {
        "_what": "THE CODE-SYMBOL REGISTRY — the `code://` branch of the universal coordinate "
                 "(Block 17-18): every code symbol the corpus references, as an addressable "
                 "entity. REVERSE index (symbol → WHO references it), complementing refcheck's "
                 "FORWARD pass (ref → does it resolve). Keyed by a stable id "
                 "code://<resolved-file-stem>/<symbol> (e.g. code://suite/resolve_surfaced). Each "
                 "entry: file · symbol · kind(def|class|route|const|file-only) · resolves(bool) · "
                 "referenced_by[] (the feature-ids + ui:// addresses pointing at it). resolves:false "
                 "is a DRIFT signal (a named symbol no longer in the file). GENERATED by "
                 "_system/symbols.py reading register.json (features[].code) + addresses.json "
                 "(addresses.*.code) against ~/company (READ-ONLY) — REGENERATE after any code: ref "
                 "change. glob/dir refs (nodes/*.py, voice/) are not symbols → listed under "
                 "not_indexable (counted, never silently dropped). The future local-AI layer "
                 "(mechanisms.json · code-symbol-registry) annotates each symbol with what it actually "
                 "does + flags symbols referenced by features whose represents-claim they don't match.",
        "symbols": reg,
        "not_indexable": not_indexable,
        "summary": {
            "symbols_indexed": len(reg),
            "resolve": sum(1 for e in reg.values() if e["resolves"]),
            "do_not_resolve": len(unresolved),
            "shared_2plus": len(shared),
            "not_indexable": len(not_indexable),
            "id_collisions": len(collisions),
        },
        "unresolved": unresolved,
        "shared": shared,
        "collisions": collisions,
    }


def _validate(doc: dict):
    """Fail LOUD on a malformed registry we just built (a self-check before it's trusted)."""
    if not isinstance(doc.get("symbols"), dict):
        raise ValueError("code-symbols.json malformed: 'symbols' is not a dict")
    for sid, e in doc["symbols"].items():
        if not sid.startswith("code://"):
            raise ValueError(f"code-symbols.json malformed: id {sid!r} is not a code:// id")
        for k in ("file", "kind", "resolves", "referenced_by"):
            if k not in e:
                raise ValueError(f"code-symbols.json malformed: {sid} missing {k!r}")
        if not e["referenced_by"]:
            raise ValueError(f"code-symbols.json malformed: {sid} has no referenced_by")


def run_corpus():
    """Build the reverse index over the real corpus; write code-symbols.json; print a summary."""
    here = os.path.dirname(os.path.abspath(__file__))
    design = os.path.dirname(here)
    register = json.load(open(os.path.join(design, "register.json"), encoding="utf-8"))
    addr_doc = json.load(open(os.path.join(here, "addresses.json"), encoding="utf-8"))
    addresses = addr_doc.get("addresses", addr_doc)

    doc = build_registry(register, addresses)
    _validate(doc)

    out = os.path.join(here, "code-symbols.json")
    json.dump(doc, open(out, "w", encoding="utf-8"), indent=2)
    s = doc["summary"]
    print("symbols (code:// reverse index) — summary:")
    for k, v in s.items():
        print(f"  {k}: {v}")
    if doc["shared"]:
        print("  → SHARED symbols (referenced by 2+ corpus things):")
        for sid in doc["shared"]:
            e = doc["symbols"][sid]
            print(f"    {sid}  ←  {', '.join(e['referenced_by'])}")
    if doc["unresolved"]:
        print("  → DOES NOT RESOLVE (drift signal — a named symbol no longer in the file):")
        for sid in doc["unresolved"]:
            e = doc["symbols"][sid]
            print(f"    {sid}  ({e['file']})  ←  {', '.join(e['referenced_by'])}")
    if doc["collisions"]:
        print("  → id COLLISIONS (same id, different resolved files):", ", ".join(doc["collisions"]))
    if doc["not_indexable"]:
        print("  → not indexable as a symbol (glob/dir — reported, not dropped):",
              ", ".join(f"{n['owner']}:{n['ref']}" for n in doc["not_indexable"]))
    return doc


def main():
    run_corpus()


if __name__ == "__main__":
    main()
