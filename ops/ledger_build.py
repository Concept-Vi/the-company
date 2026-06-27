#!/usr/bin/env python3
"""ops/ledger_build.py — the GROWN deterministic extractor for THE LEDGER (the-one-system).

Grows the thin first-experiments (ops/code_archaeology.py · design/_system/{codeedges,symbols,refcheck}.py)
into a deep, whole-tree, all-language structural extractor that writes the NON-FLAT Supabase ledger
(schema in build-prep/the-one-system/ledger_schema.sql). REUSE-don't-fork:
  • coverage denominator      → code_archaeology.enumerate_files (the real-tree walk, Tim's law)
  • file read + exclusions    → code_archaeology.parse_file's read/secret/binary gates (re-implemented thin here,
                                same rules) — kept local so this module has no behavioural coupling to that file's
                                LLM cascade.
  • edge resolution precedence→ design/_system/codeedges (same-file > import > unambiguous-global) — applied in
                                the SEPARATE resolution pass (to_raw -> to_resolved), not here.
This module does ONLY deterministic facts (no model). The Opus interpretive layer fills the model fields later.

Decisions (lead, 2026-06-27): entries keyed by full rel-path (address=code://<project>/<path>); symbols by a
PATH-BASED unique id code://<project>/<path>::<symbol> (the stem-based code://<stem>/<symbol> collides across a
whole tree — kept as `stem_id` alias so the existing codeedges/symbols graph still joins). Registry-row detection
is OPEN (any module-level UPPERCASE dict assignment), not a hardcoded sentinel list (the bias fix).

Run:
  python3 ops/ledger_build.py --show runtime/cc_board.py     # prove the rich extraction on ONE file (no DB)
  python3 ops/ledger_build.py --folder runtime --load        # extract a folder -> load into the ledger (a run)
"""
from __future__ import annotations
import argparse, ast, hashlib, json, os, re, sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
from ops.code_archaeology import enumerate_files, _LANG_BY_EXT, _SENSITIVE_EXT, _SENSITIVE_HINT, _BINARY_EXT  # reuse
try:                                                       # integrate with the address spine — registered-scheme set
    from contracts.address import SCHEMES as _COMPANY_SCHEMES
except Exception:
    _COMPANY_SCHEMES = ()

PROJECT = "company"
_SCHEME_RE = re.compile(r"\b([a-z][a-z0-9+.\-]*)://")
_TODO_RE = re.compile(r"\b(TODO|FIXME|XXX|HACK)\b")
_STUB_RE = re.compile(r"\b(skeleton|not wired|not-wired|stub|placeholder|not implemented|unimplemented)\b", re.I)
_EMIT_FNS = {"emit", "_emit", "_emit_durable", "append_event", "emit_event"}


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read(abs_path: str, rel: str):
    """Read a file as text, applying the same exclusion gates as code_archaeology.parse_file. Returns
    (src, raw_bytes) or ('', None) with a reason on exclusion: returns (None, reason)."""
    ext = os.path.splitext(rel)[1].lower()
    base = os.path.basename(rel).lower()
    if ext in _SENSITIVE_EXT or base.startswith(".env") or base == ".secrets" or any(h in base for h in _SENSITIVE_HINT):
        return None, "sensitive"
    if ext in _BINARY_EXT:
        return None, "binary-ext"
    if ext == ".log":
        return None, "log-noise"
    try:
        with open(abs_path, "rb") as fh:
            raw = fh.read()
        if b"\x00" in raw[:4096]:
            return None, "binary-content"
        return raw.decode("utf-8", errors="replace"), raw
    except (OSError, UnicodeDecodeError) as e:
        return None, f"unreadable:{type(e).__name__}"


# ── deep Python AST extraction ───────────────────────────────────────────────────────────────
def _unparse(node) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def _decorators(node) -> list:
    return [_unparse(d) for d in getattr(node, "decorator_list", [])]


def _signature(fn: ast.AST) -> dict:
    a = fn.args
    params = []
    def add(arg, default=None, kind="arg"):
        params.append({"name": arg.arg, "annotation": _unparse(arg.annotation) if arg.annotation else None,
                       "default": _unparse(default) if default is not None else None, "kind": kind})
    posonly = list(getattr(a, "posonlyargs", []))
    args = list(a.args)
    defaults = list(a.defaults)
    allpos = posonly + args
    pad = len(allpos) - len(defaults)
    for i, arg in enumerate(allpos):
        d = defaults[i - pad] if i >= pad else None
        add(arg, d, "posonly" if i < len(posonly) else "arg")
    if a.vararg: add(a.vararg, None, "vararg")
    for arg, d in zip(a.kwonlyargs, a.kw_defaults):
        add(arg, d, "kwonly")
    if a.kwarg: add(a.kwarg, None, "kwarg")
    return {"params": params, "returns": _unparse(fn.returns) if fn.returns else None}


class _Depth(ast.NodeVisitor):
    """Max nesting depth + branch count over a body."""
    BRANCH = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith)
    def __init__(self):
        self.maxd = 0; self.cur = 0; self.branches = 0
    def generic_visit(self, node):
        nest = isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith,
                                 ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        if isinstance(node, self.BRANCH):
            self.branches += 1
        if nest:
            self.cur += 1; self.maxd = max(self.maxd, self.cur)
            super().generic_visit(node); self.cur -= 1
        else:
            super().generic_visit(node)


def _calls_in(node) -> list:
    """Raw call targets within a node body → [(raw_target, line)]. Name() → 'name'; obj.attr() → 'obj.attr'."""
    out = []
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name):
                out.append((f.id, getattr(n, "lineno", None)))
            elif isinstance(f, ast.Attribute):
                base = f.value.id if isinstance(f.value, ast.Name) else _unparse(f.value)
                out.append((f"{base}.{f.attr}" if base else f.attr, getattr(n, "lineno", None)))
    return out


def extract_python(rel: str, src: str) -> dict:
    """Deep deterministic facts for ONE python file → {entry_facts, symbols[], edges[]}."""
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError) as e:
        return {"parse_error": f"{type(e).__name__}: {e}", "symbols": [], "edges": [],
                "imports": [], "declares": [], "constants": [], "module_dicts": [],
                "env_vars": [], "routes": [], "events": [], "exceptions": {"defined": [], "raised": []},
                "signals": {}, "markers": _scan_markers(src)}
    imports, declares, constants, registry_rows = [], [], [], []
    env_vars, routes, events = set(), set(), set()
    exc_defined, exc_raised = [], set()
    symbols, edges = [], []
    n_func = n_class = 0

    def code_id(symbol):
        return f"code://{PROJECT}/{rel}::{symbol}"

    file_addr = f"code://{PROJECT}/{rel}"

    # imports — walk ALL levels (lazy imports inside functions are pervasive here, to avoid cycles;
    # top-level-only would badly undercount the dependency graph). `lazy` = nested (col_offset>0).
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                imports.append({"target": a.name, "kind": "import", "internal": _is_internal(a.name),
                                "line": n.lineno, "lazy": n.col_offset > 0})
                edges.append({"from": file_addr, "kind": "imports", "to_raw": a.name, "line": n.lineno})
        elif isinstance(n, ast.ImportFrom):
            mod = n.module or "."
            imports.append({"target": mod, "kind": "from", "internal": _is_internal(mod),
                            "line": n.lineno, "lazy": n.col_offset > 0})
            edges.append({"from": file_addr, "kind": "imports", "to_raw": mod, "line": n.lineno})

    # module-level constructs (constants + uppercase-dict declarations — top-level only, correctly)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    nm = t.id
                    if isinstance(node.value, ast.Dict) and nm.isupper() or (nm.isupper() and isinstance(node.value, ast.Dict)):
                        keys = [k.value for k in node.value.keys if isinstance(k, ast.Constant)]
                        registry_rows.append({"name": nm, "keys": keys[:60], "line": node.lineno})
                    if nm.isupper() or re.match(r"^_[A-Z]", nm):
                        constants.append({"name": nm, "value": _unparse(node.value)[:200], "line": node.lineno})

    # symbols (all defs, incl nested + methods) + per-symbol edges
    def walk_defs(node, parent_qual="", parent_is_class=False):
        nonlocal n_func, n_class
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                n_func += 1
                qual = f"{parent_qual}.{child.name}" if parent_qual else child.name
                sig = _signature(child)
                kind = "method" if parent_is_class else "function"
                symbols.append({
                    "code_id": code_id(qual), "stem_id": f"code://{_stem(rel)}/{child.name}",
                    "name": child.name, "qual": qual, "symbol_kind": kind,
                    "signature": _sig_str(child.name, sig), "params": sig["params"], "returns": sig["returns"],
                    "decorators": _decorators(child), "bases": [],
                    "line_start": child.lineno, "line_end": getattr(child, "end_lineno", child.lineno),
                    "is_async": isinstance(child, ast.AsyncFunctionDef),
                    "is_exported": not child.name.startswith("_"),
                })
                # calls within this function -> edges from the symbol
                for tgt, ln in _calls_in(child):
                    edges.append({"from": code_id(qual), "kind": "calls", "to_raw": tgt, "line": ln})
                    base = tgt.split(".")[0]
                    if base == "os" and (".getenv" in tgt or ".environ" in tgt):
                        pass
                # nested defs
                walk_defs(child, qual, parent_is_class=False)
            elif isinstance(child, ast.ClassDef):
                n_class += 1
                qual = f"{parent_qual}.{child.name}" if parent_qual else child.name
                bases = [_unparse(b) for b in child.bases]
                symbols.append({
                    "code_id": code_id(qual), "stem_id": f"code://{_stem(rel)}/{child.name}",
                    "name": child.name, "qual": qual, "symbol_kind": "class",
                    "signature": f"class {child.name}({', '.join(bases)})" if bases else f"class {child.name}",
                    "params": [], "returns": None, "decorators": _decorators(child), "bases": bases,
                    "line_start": child.lineno, "line_end": getattr(child, "end_lineno", child.lineno),
                    "is_async": False, "is_exported": not child.name.startswith("_"),
                })
                for b in bases:
                    edges.append({"from": code_id(qual), "kind": "extends", "to_raw": b, "line": child.lineno})
                    if b.endswith("Error") or b in ("Exception", "RuntimeError", "ValueError"):
                        exc_defined.append(child.name)
                walk_defs(child, qual, parent_is_class=True)
            else:
                # descend into control-flow / other nodes too (conditional + try/with-nested defs are real
                # symbols — the bug bridge.py exposed); scope (qual + class-ness) is unchanged by a block.
                walk_defs(child, parent_qual, parent_is_class)
    walk_defs(tree)

    # whole-tree scans: env vars, routes, events, raises, schemes
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            fn = n.func
            fname = fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else "")
            # os.getenv("X") / os.environ.get("X")
            if fname in ("getenv", "get") and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
                src_obj = _unparse(fn.value) if isinstance(fn, ast.Attribute) else ""
                if "environ" in src_obj or fname == "getenv":
                    if re.match(r"^[A-Z][A-Z0-9_]+$", n.args[0].value):
                        env_vars.add(n.args[0].value)
            # emit/append_event("kind", ...)
            if fname in _EMIT_FNS and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
                events.add(n.args[0].value)
                edges.append({"from": file_addr, "kind": "emits-event", "to_raw": n.args[0].value, "line": getattr(n, "lineno", None)})
        elif isinstance(n, ast.Subscript):  # os.environ["X"]
            if isinstance(n.value, ast.Attribute) and n.value.attr == "environ":
                key = n.slice
                if isinstance(key, ast.Constant) and isinstance(key.value, str) and re.match(r"^[A-Z][A-Z0-9_]+$", key.value):
                    env_vars.add(key.value)
        elif isinstance(n, ast.Raise) and n.exc is not None:
            e = n.exc.func if isinstance(n.exc, ast.Call) else n.exc
            if isinstance(e, ast.Name):
                exc_raised.add(e.id)
        elif isinstance(n, ast.Constant) and isinstance(n.value, str):
            if n.value.startswith("/api/"):
                routes.add(n.value.split()[0])

    # scheme refs (regex over source — OPEN, not a fixed list) with first line
    schemes = {}
    for m in _SCHEME_RE.finditer(src):
        s = m.group(1)
        if s in ("http", "https", "ws", "wss", "ftp", "file"):  # keep file (a real scheme) — but skip noisy urls? keep all, honest
            pass
        if s not in schemes:
            schemes[s] = src.count("\n", 0, m.start()) + 1
    for s in schemes:
        edges.append({"from": file_addr, "kind": "references", "to_raw": f"{s}://", "line": schemes[s]})

    dv = _Depth(); dv.visit(tree)
    has_main = bool(re.search(r'if\s+__name__\s*==\s*[\'"]__main__[\'"]', src))
    signals = {"n_functions": n_func, "n_classes": n_class, "n_imports": len(imports),
               "n_constants": len(constants), "n_module_dicts": len(registry_rows),
               "max_nesting_depth": dv.maxd, "n_branches": dv.branches,
               "n_symbols": len(symbols), "n_edges": len(edges), "has_entry_point": has_main}
    # folder containment edge handled at folder level by the caller.
    return {
        "imports": imports, "declares": [{"name": s["name"], "kind": s["symbol_kind"], "line": s["line_start"]}
                                         for s in symbols if "." not in s["qual"]],
        "constants": constants, "module_dicts": registry_rows,
        "address_schemes_used": [{"scheme": s, "line": l} for s, l in schemes.items()],
        "env_vars": sorted(env_vars), "routes": sorted(routes), "events": sorted(events),
        "exceptions": {"defined": sorted(set(exc_defined)), "raised": sorted(exc_raised)},
        "markers": _scan_markers(src), "signals": signals, "symbols": symbols, "edges": edges,
    }


def _scan_markers(src: str) -> list:
    out = []
    for m in _TODO_RE.finditer(src):
        ln = src.count("\n", 0, m.start()) + 1
        line_txt = src.splitlines()[ln - 1].strip()[:160] if ln - 1 < len(src.splitlines()) else ""
        out.append({"marker": m.group(1), "line": ln, "text": line_txt})
    if re.search(r'if\s+__name__\s*==\s*[\'"]__main__[\'"]', src):
        out.append({"marker": "__main__", "line": None, "text": "has entry point / self-test"})
    for m in _STUB_RE.finditer(src):
        ln = src.count("\n", 0, m.start()) + 1
        out.append({"marker": "stub-word", "line": ln, "text": m.group(0)})
    return out[:50]


def _is_internal(mod: str) -> bool:
    top = mod.split(".")[0].lstrip(".")
    return top in {"runtime", "contracts", "store", "nodes", "fabric", "mcp_face", "ops", "voice", "introspection",
                   "design", "roles", "flows", "routines"} or mod.startswith(".")


def _stem(rel: str) -> str:
    return os.path.splitext(os.path.basename(rel))[0]


def _sig_str(name: str, sig: dict) -> str:
    parts = []
    for p in sig["params"]:
        s = p["name"]
        if p["annotation"]: s += f": {p['annotation']}"
        if p["default"] is not None: s += f"={p['default']}"
        parts.append(s)
    r = f" -> {sig['returns']}" if sig["returns"] else ""
    return f"{name}({', '.join(parts)}){r}"


# ── shared scan helpers (line-aware) ───────────────────────────────────────────────────────────
def _lineno(src: str, pos: int) -> int:
    return src.count("\n", 0, pos) + 1


def _schemes(src: str) -> list:
    """Open list of scheme:// strings, each flagged whether it's a REGISTERED Company scheme (contracts/
    address.SCHEMES) — so `registered:true` queries are clean (channel/board/decision…) and http/https noise
    is distinguishable, without capping discovery to a hardcoded list."""
    seen = {}
    for m in _SCHEME_RE.finditer(src):
        s = m.group(1)
        if s not in seen:
            seen[s] = _lineno(src, m.start())
    return [{"scheme": s, "line": l, "registered": s in _COMPANY_SCHEMES} for s, l in seen.items()]


# ── TS / TSX / JS deterministic extractor (regex; a node+typescript AST is the future upgrade — MODEL-NOTES) ──
_TS_IMPORT = re.compile(r"""(?:^|\s)import\b[^;]*?from\s+['"]([^'"]+)['"]|(?:^|\s)import\s+['"]([^'"]+)['"]|require\(\s*['"]([^'"]+)['"]\s*\)|import\(\s*['"]([^'"]+)['"]\s*\)""")
_TS_DECL = re.compile(r"^\s*(export\s+)?(default\s+)?(async\s+)?(function|class)\s+([A-Za-z0-9_$]+)")
_TS_ARROW = re.compile(r"^\s*(export\s+)?(default\s+)?(?:const|let|var)\s+([A-Za-z0-9_$]+)\s*(?::[^=]+)?=\s*(async\s*)?(?:<[^>]*>)?\([^)]*\)\s*(?::[^=>]+)?=>")
_TS_TYPE = re.compile(r"^\s*(export\s+)?(?:interface|type)\s+([A-Za-z0-9_$]+)")
_TS_EXPORTS = re.compile(r"^\s*export\s*\{([^}]+)\}")
_TS_API = re.compile(r"""fetch\(\s*[`'"]([^`'"]+)|\.(get|post|put|delete|patch)\(\s*[`'"]([^`'"]+)""")
_TS_EVENT = re.compile(r"""(?:addEventListener|dispatchEvent|new\s+CustomEvent)\(\s*['"]([^'"]+)['"]""")


def extract_ts(rel: str, src: str) -> dict:
    file_addr = f"code://{PROJECT}/{rel}"
    is_tsx = rel.endswith(".tsx") or rel.endswith(".jsx")
    imports, symbols, edges = [], [], []
    components, exports, api_calls, types = [], [], [], []
    events = set()
    def sym(name, kind, line, **extra):
        symbols.append({"code_id": f"code://{PROJECT}/{rel}::{name}", "stem_id": f"code://{_stem(rel)}/{name}",
                        "name": name, "qual": name, "symbol_kind": kind, "signature": extra.get("sig", name),
                        "params": [], "returns": None, "decorators": [], "bases": extra.get("bases", []),
                        "line_start": line, "line_end": line, "is_async": extra.get("async", False),
                        "is_exported": extra.get("exported", False)})
    for i, ln in enumerate(src.splitlines(), 1):
        for m in _TS_IMPORT.finditer(ln):
            tgt = next((g for g in m.groups() if g), None)
            if tgt:
                imports.append({"target": tgt, "kind": "import", "internal": tgt.startswith("."), "line": i})
                edges.append({"from": file_addr, "kind": "imports", "to_raw": tgt, "line": i})
        m = _TS_DECL.match(ln)
        if m:
            exported = bool(m.group(1) or m.group(2)); kw = m.group(4); name = m.group(5)
            kind = "class" if kw == "class" else ("component" if (is_tsx and name[:1].isupper()) else "function")
            sym(name, kind, i, exported=exported, async_=bool(m.group(3)), sig=ln.strip()[:160])
            if kind == "component": components.append(name)
            if exported: exports.append(name)
        m = _TS_ARROW.match(ln)
        if m:
            exported = bool(m.group(1) or m.group(2)); name = m.group(3)
            kind = "component" if (is_tsx and name[:1].isupper()) else "function"
            sym(name, kind, i, exported=exported, sig=ln.strip()[:160])
            if kind == "component": components.append(name)
            if exported: exports.append(name)
        m = _TS_TYPE.match(ln)
        if m:
            sym(m.group(2), "type", i, exported=bool(m.group(1)))
            types.append(m.group(2))
        m = _TS_EXPORTS.match(ln)
        if m:
            for nm in m.group(1).split(","):
                nm = nm.strip().split(" as ")[0].strip()
                if nm: exports.append(nm)
        for am in _TS_API.finditer(ln):
            url = am.group(1) or am.group(3)
            if url:
                api_calls.append({"method": (am.group(2) or "fetch").upper(), "url": url, "line": i})
                edges.append({"from": file_addr, "kind": "calls-endpoint", "to_raw": url, "line": i})
        for em in _TS_EVENT.finditer(ln):
            events.add(em.group(1))
    signals = {"n_imports": len(imports), "n_symbols": len(symbols), "n_components": len(components),
               "n_exports": len(set(exports)), "n_types": len(types), "n_api_calls": len(api_calls),
               "n_edges": len(edges), "has_entry_point": False}
    return {"imports": imports, "declares": [{"name": s["name"], "kind": s["symbol_kind"], "line": s["line_start"]}
                                             for s in symbols if s["is_exported"]],
            "address_schemes_used": _schemes(src), "env_vars": [], "markers": _scan_markers(src),
            "signals": signals, "symbols": symbols, "edges": edges,
            "extra_fields": {"components": sorted(set(components)), "exports": sorted(set(exports)),
                             "api_calls": api_calls, "types": types, "events": sorted(events)}}


# ── SQL extractor ──
_SQL_TABLE = re.compile(r"create\s+table\s+(?:if\s+not\s+exists\s+)?([.\w\"]+)\s*\(", re.I)
_SQL_INDEX = re.compile(r"create\s+(?:unique\s+)?index\s+(?:if\s+not\s+exists\s+)?[\w\"]*\s*on\s+([.\w\"]+)", re.I)
_SQL_POLICY = re.compile(r"create\s+policy\s+\"?([^\"\s]+)\"?\s+on\s+([.\w\"]+)", re.I)
_SQL_FUNC = re.compile(r"create\s+(?:or\s+replace\s+)?function\s+([.\w\"]+)\s*\(", re.I)
_SQL_TRIGGER = re.compile(r"create\s+trigger\s+([.\w\"]+)", re.I)
_SQL_EXT = re.compile(r"create\s+extension\s+(?:if\s+not\s+exists\s+)?\"?([\w]+)\"?", re.I)


def extract_sql(rel: str, src: str) -> dict:
    tables, indexes, policies, funcs, triggers, exts = [], [], [], [], [], []
    symbols, edges = [], []
    file_addr = f"code://{PROJECT}/{rel}"
    for m in _SQL_TABLE.finditer(src):
        name = m.group(1).strip('"'); line = _lineno(src, m.start())
        # columns: text from after '(' to the matching close — rough top-level comma split
        rest = src[m.end():]; depth = 1; buf = ""
        for ch in rest:
            if ch == "(": depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0: break
            buf += ch
        cols = []
        for part in re.split(r",(?![^(]*\))", buf):
            t = part.strip().split("\n")[0].strip()
            if t and not re.match(r"(?i)(primary|foreign|unique|constraint|check)\b", t):
                cn = t.split()[0].strip('"') if t.split() else ""
                if cn: cols.append({"name": cn, "type": " ".join(t.split()[1:3])})
        tables.append({"name": name, "columns": cols, "line": line})
        symbols.append({"code_id": f"code://{PROJECT}/{rel}::{name}", "stem_id": f"code://{_stem(rel)}/{name}",
                        "name": name, "qual": name, "symbol_kind": "table", "signature": f"table {name}",
                        "params": [], "returns": None, "decorators": [], "bases": [], "line_start": line,
                        "line_end": line, "is_async": False, "is_exported": True})
    for m in _SQL_INDEX.finditer(src):
        indexes.append({"on": m.group(1).strip('"'), "line": _lineno(src, m.start())})
    for m in _SQL_POLICY.finditer(src):
        policies.append({"name": m.group(1), "on": m.group(2).strip('"'), "line": _lineno(src, m.start())})
        edges.append({"from": file_addr, "kind": "references", "to_raw": m.group(2).strip('"'), "line": _lineno(src, m.start())})
    for m in _SQL_FUNC.finditer(src):
        funcs.append(m.group(1).strip('"'))
    for m in _SQL_TRIGGER.finditer(src):
        triggers.append(m.group(1).strip('"'))
    for m in _SQL_EXT.finditer(src):
        exts.append(m.group(1))
    signals = {"n_tables": len(tables), "n_indexes": len(indexes), "n_policies": len(policies),
               "n_functions": len(funcs), "n_symbols": len(symbols), "n_edges": len(edges), "has_entry_point": False}
    return {"imports": [], "declares": [{"name": t["name"], "kind": "table", "line": t["line"]} for t in tables],
            "address_schemes_used": _schemes(src), "env_vars": [], "markers": _scan_markers(src),
            "signals": signals, "symbols": symbols, "edges": edges,
            "extra_fields": {"tables": tables, "indexes": indexes, "policies": policies, "functions": funcs,
                             "triggers": triggers, "extensions": exts,
                             "migration_order": (re.match(r"(\d+)", os.path.basename(rel)) or [None]) and
                             (re.match(r"(\d+)", os.path.basename(rel)).group(1) if re.match(r"(\d+)", os.path.basename(rel)) else None)}}


# ── systemd .service/.timer extractor ──
def extract_systemd(rel: str, src: str) -> dict:
    sections, cur = {}, None
    for ln in src.splitlines():
        s = ln.strip()
        if s.startswith("[") and s.endswith("]"):
            cur = s[1:-1]; sections[cur] = {}
        elif "=" in s and cur and not s.startswith("#"):
            k, _, v = s.partition("=")
            sections.setdefault(cur, {}).setdefault(k.strip(), []).append(v.strip())
    def first(sec, key):
        return (sections.get(sec, {}).get(key) or [None])[0]
    edges = []
    wanted = first("Install", "WantedBy")
    if wanted:
        edges.append({"from": f"code://{PROJECT}/{rel}", "kind": "references", "to_raw": wanted, "line": None})
    extra = {"unit": os.path.basename(rel), "description": first("Unit", "Description"),
             "exec_start": first("Service", "ExecStart"), "type": first("Service", "Type"),
             "wanted_by": wanted, "after": first("Unit", "After"), "requires": first("Unit", "Requires"),
             "on_calendar": first("Timer", "OnCalendar"), "sections": {k: list(v.keys()) for k, v in sections.items()}}
    return {"imports": [], "declares": [], "address_schemes_used": _schemes(src), "env_vars": [],
            "markers": _scan_markers(src), "symbols": [], "edges": edges,
            "signals": {"n_sections": len(sections), "n_edges": len(edges), "has_entry_point": bool(extra["exec_start"])},
            "extra_fields": extra}


# ── shell extractor ──
_SH_FUNC = re.compile(r"^\s*(?:function\s+)?([A-Za-z_][\w]*)\s*\(\)\s*\{")
_SH_EXPORT = re.compile(r"^\s*export\s+([A-Z_][A-Z0-9_]*)=")
_SH_BINS = {"systemctl", "python", "python3", "curl", "wget", "node", "npm", "npx", "git", "psql", "docker",
            "supabase", "claude", "pip", "pip3", "bash", "sh", "make", "ollama", "vllm"}


def extract_shell(rel: str, src: str) -> dict:
    file_addr = f"code://{PROJECT}/{rel}"
    symbols, edges, env_vars, runs = [], [], set(), set()
    for i, ln in enumerate(src.splitlines(), 1):
        m = _SH_FUNC.match(ln)
        if m:
            symbols.append({"code_id": f"code://{PROJECT}/{rel}::{m.group(1)}", "stem_id": f"code://{_stem(rel)}/{m.group(1)}",
                            "name": m.group(1), "qual": m.group(1), "symbol_kind": "function", "signature": f"{m.group(1)}()",
                            "params": [], "returns": None, "decorators": [], "bases": [], "line_start": i, "line_end": i,
                            "is_async": False, "is_exported": True})
        m = _SH_EXPORT.match(ln)
        if m: env_vars.add(m.group(1))
        toks = ln.strip().split() if ln.strip() and not ln.strip().startswith("#") else []
        while toks and toks[0] in ("exec", "nohup", "sudo", "time", "env"):  # unwrap command prefixes
            toks = toks[1:]
        first = os.path.basename(toks[0]) if toks else ""
        if first in _SH_BINS:
            runs.add(first)
            edges.append({"from": file_addr, "kind": "calls", "to_raw": first, "line": i})
    return {"imports": [], "declares": [], "address_schemes_used": _schemes(src), "env_vars": sorted(env_vars),
            "markers": _scan_markers(src), "symbols": symbols, "edges": edges,
            "signals": {"n_functions": len(symbols), "runs": len(runs), "n_edges": len(edges),
                        "has_entry_point": bool(re.match(r"#!", src))},
            "extra_fields": {"runs": sorted(runs), "shebang": src.splitlines()[0] if src.startswith("#!") else None}}


# ── JSON extractor (shape + role + refs; large/generated → shape only) ──
def extract_json(rel: str, src: str, size: int) -> dict:
    extra = {}; refs = []
    try:
        obj = json.loads(src)
    except (json.JSONDecodeError, ValueError) as e:
        return {"imports": [], "declares": [], "address_schemes_used": _schemes(src), "env_vars": [],
                "markers": _scan_markers(src), "symbols": [], "edges": [],
                "signals": {"parse_error": True}, "extra_fields": {"parse_error": str(e)[:160]}}
    if isinstance(obj, dict):
        keys = list(obj.keys())
        extra["top_level_keys"] = keys[:80]
        for meta in ("_schema", "_note", "_what"):
            if meta in obj and isinstance(obj[meta], str):
                extra[meta] = obj[meta][:300]
        extra["generated"] = any("generat" in str(obj.get(k, "")).lower() for k in ("_note", "_what", "_schema")) \
            or "generated" in os.path.basename(rel).lower()
        low = os.path.basename(rel).lower()
        extra["json_role"] = ("config" if re.search(r"config|tsconfig|package|\.toml", low) else
                              "registry" if any(k in keys for k in ("symbols", "edges", "addresses", "features", "tools")) else
                              "data")
        if size < 120_000:  # only scan values of modest files for refs
            for m in _SCHEME_RE.finditer(src):
                refs.append(m.group(1) + "://")
    elif isinstance(obj, list):
        extra["json_role"] = "data-array"; extra["length"] = len(obj)
        extra["item_keys"] = list(obj[0].keys())[:40] if obj and isinstance(obj[0], dict) else []
    return {"imports": [], "declares": [], "address_schemes_used": _schemes(src) if size < 120_000 else [],
            "env_vars": [], "markers": [], "symbols": [], "edges": [],
            "signals": {"n_keys": len(extra.get("top_level_keys", [])), "has_entry_point": False},
            "extra_fields": extra}


# ── Markdown extractor (structure → the docs/AGENTS web; prose MEANING is the model layer — MODEL-NOTES) ──
_MD_H = re.compile(r"^(#{1,6})\s+(.*)", re.M)
_MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_MD_WIKI = re.compile(r"\[\[([^\]]+)\]\]")


def extract_markdown(rel: str, src: str) -> dict:
    file_addr = f"code://{PROJECT}/{rel}"
    fm_keys = []
    if src.startswith("---"):
        end = src.find("\n---", 3)
        if end != -1:
            try:
                fm = yaml.safe_load(src[3:end])
                if isinstance(fm, dict): fm_keys = list(fm.keys())
            except Exception:
                pass
    headings = [{"level": len(m.group(1)), "text": m.group(2).strip()[:120], "line": _lineno(src, m.start())}
                for m in _MD_H.finditer(src)]
    links = sorted({m.group(1) for m in _MD_LINK.finditer(src)})
    wikilinks = sorted({m.group(1).split("|")[0].strip() for m in _MD_WIKI.finditer(src)})
    edges = []
    for w in wikilinks:
        edges.append({"from": file_addr, "kind": "references", "to_raw": f"[[{w}]]", "line": None})
    for l in links:
        if not l.startswith("http"):
            edges.append({"from": file_addr, "kind": "references", "to_raw": l, "line": None})
    return {"imports": [], "declares": [], "address_schemes_used": _schemes(src), "env_vars": [],
            "markers": _scan_markers(src), "symbols": [], "edges": edges,
            "signals": {"n_headings": len(headings), "n_links": len(links), "n_wikilinks": len(wikilinks),
                        "has_frontmatter": bool(fm_keys), "n_edges": len(edges), "has_entry_point": False},
            "extra_fields": {"frontmatter_keys": fm_keys, "headings": headings[:80],
                             "links": links[:80], "wikilinks": wikilinks[:80]}}


import yaml  # noqa: E402  (stdlib-adjacent; available in venv)


# ── CSS / HTML (light) ──
def extract_css(rel: str, src: str) -> dict:
    props = sorted({m.group(1) for m in re.finditer(r"--([\w-]+)\s*:", src)})
    n_sel = len(re.findall(r"\}", src))
    return {"imports": [], "declares": [], "address_schemes_used": _schemes(src), "env_vars": [],
            "markers": _scan_markers(src), "symbols": [], "edges": [],
            "signals": {"n_custom_props": len(props), "n_rules": n_sel, "has_entry_point": False},
            "extra_fields": {"custom_properties": props[:120], "has_root": ":root" in src}}


def extract_html(rel: str, src: str) -> dict:
    file_addr = f"code://{PROJECT}/{rel}"
    ui_refs = sorted({m.group(1) for m in re.finditer(r'data-ui-ref=["\']([^"\']+)["\']', src)})
    title = (re.search(r"<title>([^<]*)</title>", src) or [None, None])[1] if "<title>" in src else None
    scripts = sorted({m.group(1) for m in re.finditer(r'<script[^>]*src=["\']([^"\']+)["\']', src)})
    edges = [{"from": file_addr, "kind": "references", "to_raw": u, "line": None} for u in ui_refs]
    return {"imports": [], "declares": [], "address_schemes_used": _schemes(src), "env_vars": [],
            "markers": _scan_markers(src), "symbols": [], "edges": edges,
            "signals": {"n_ui_refs": len(ui_refs), "has_entry_point": False},
            "extra_fields": {"ui_refs": ui_refs[:120], "title": title, "scripts": scripts[:40]}}


def extract_jsonl(rel: str, src: str) -> dict:
    """A .jsonl is DATA (many json lines, not one doc) — record shape, not content: line count + first-line keys."""
    lines = [l for l in src.splitlines() if l.strip()]
    keys = []
    if lines:
        try:
            first = json.loads(lines[0])
            if isinstance(first, dict): keys = list(first.keys())[:40]
        except (json.JSONDecodeError, ValueError):
            pass
    return {"imports": [], "declares": [], "address_schemes_used": [], "env_vars": [], "markers": [],
            "symbols": [], "edges": [],
            "signals": {"n_records": len(lines), "has_entry_point": False},
            "extra_fields": {"json_role": "data-jsonl", "records": len(lines), "record_keys": keys}}


# ── the EXTRACTOR REGISTRY — add a language = add a ROW (not an if/elif), in a registry-philosophy codebase.
#    Each carries a VERSION stamped per entry/symbol, so improving an extractor makes old vs new rows
#    distinguishable + selectively re-runnable. ──
_TS_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts"}


def _python_norm(rel, src, raw):
    r = extract_python(rel, src)
    r["extra_fields"] = {"module_dicts": r.pop("module_dicts", []), "constants": r.pop("constants", []),
                         "routes": r.pop("routes", []), "events": r.pop("events", []),
                         "exceptions": r.pop("exceptions", {})}
    if r.get("parse_error"):
        r["extra_fields"]["parse_error"] = r.pop("parse_error")
    return r


EXTRACTORS = [
    {"id": "python",   "version": "py-ast-v2",   "match": lambda ext, lang: lang == "python",
     "fn": lambda rel, src, raw: _python_norm(rel, src, raw)},
    {"id": "ts",       "version": "ts-regex-v1", "match": lambda ext, lang: ext in _TS_EXTS,
     "fn": lambda rel, src, raw: extract_ts(rel, src)},
    {"id": "sql",      "version": "sql-regex-v1", "match": lambda ext, lang: lang == "sql",
     "fn": lambda rel, src, raw: extract_sql(rel, src)},
    {"id": "systemd",  "version": "systemd-v1",  "match": lambda ext, lang: ext in (".service", ".timer", ".target"),
     "fn": lambda rel, src, raw: extract_systemd(rel, src)},
    {"id": "shell",    "version": "shell-v1",    "match": lambda ext, lang: lang == "shell",
     "fn": lambda rel, src, raw: extract_shell(rel, src)},
    {"id": "json",     "version": "json-v1",     "match": lambda ext, lang: lang == "json",
     "fn": lambda rel, src, raw: extract_json(rel, src, len(raw))},
    {"id": "jsonl",    "version": "jsonl-v1",    "match": lambda ext, lang: ext == ".jsonl",
     "fn": lambda rel, src, raw: extract_jsonl(rel, src)},
    {"id": "markdown", "version": "md-v1",       "match": lambda ext, lang: lang == "markdown" or ext in (".md", ".txt"),
     "fn": lambda rel, src, raw: extract_markdown(rel, src)},
    {"id": "css",      "version": "css-v1",      "match": lambda ext, lang: lang == "css",
     "fn": lambda rel, src, raw: extract_css(rel, src)},
    {"id": "html",     "version": "html-v1",     "match": lambda ext, lang: lang == "html",
     "fn": lambda rel, src, raw: extract_html(rel, src)},
]


def extract_file(rec: dict) -> dict:
    rel, abs_path = rec["rel_path"], rec["abs_path"]
    src, raw = _read(abs_path, rel)
    if src is None:
        return {"rel_path": rel, "excluded": raw}  # raw holds the reason here
    ext = os.path.splitext(rel)[1].lower()
    language = _LANG_BY_EXT.get(ext, "other")
    base = {"rel_path": rel, "language": language, "ext": ext, "size_bytes": len(raw),
            "line_count": src.count("\n") + 1, "source_hash": hashlib.sha256(raw).hexdigest()}
    chosen = next((s for s in EXTRACTORS if s["match"](ext, language)), None)
    if chosen:
        r = chosen["fn"](rel, src, raw)
        base["extractor"], base["extractor_version"] = chosen["id"], chosen["version"]
    else:
        r = {"imports": [], "declares": [], "address_schemes_used": _schemes(src), "env_vars": [],
             "markers": _scan_markers(src), "symbols": [], "edges": [],
             "signals": {"has_entry_point": False}, "extra_fields": {"deep_pending": f"no extractor for {ext}"}}
        base["extractor"], base["extractor_version"] = "none", "none-v1"
    base.update(r)
    base.setdefault("extra_fields", {})
    return base


# ── the Supabase ledger load (psql COPY; no psycopg dependency) ────────────────────────────────
import subprocess, csv, uuid, tempfile

# ── connection config — ONE home, env-overridable. Direct-DB superuser is the DELIBERATE choice for a
#    bulk build tool (fast, transactional); the RLS SupabasePrincipal is for runtime app components. ──
PGCONF = {
    "host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
    "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
    "user": os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"),
    "db":   os.environ.get("COMPANY_LEDGER_PGDB", "postgres"),
    "password": os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres"),
}
SCHEMA_VERSION = 1
TOOL_VERSION = "ledger_build.py@v2"
DEFAULT_SESSION = os.environ.get("COMPANY_SESSION_ID", "session://consolidation-lead")


def _pgenv():
    return {**os.environ, "PGPASSWORD": PGCONF["password"]}


def _psql_base():
    return ["psql", "-h", PGCONF["host"], "-p", PGCONF["port"], "-U", PGCONF["user"],
            "-d", PGCONF["db"], "-v", "ON_ERROR_STOP=1"]


def _psql(sql: str) -> str:
    r = subprocess.run(_psql_base() + ["-tAc", sql], capture_output=True, text=True, env=_pgenv())
    if r.returncode != 0:
        raise RuntimeError(f"psql failed: {r.stderr.strip()}")
    return r.stdout.strip()


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "-C", REPO, "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def _j(v) -> str:
    return json.dumps(v, default=str)


def _write_csv(path: str, rows: list):
    with open(path, "w", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        for row in rows:
            w.writerow(row)


def latest_hashes(project: str, purpose: str) -> dict | None:
    """{path: source_hash} for the latest run's files, or None if no prior run (the staleness baseline)."""
    rid = _psql(f"select run_id from ledger.latest_run where project=$${project}$$ and purpose=$${purpose}$$")
    m = re.search(r"[0-9a-f-]{36}", rid)
    if not m:
        return None
    out = _psql(f"select path||'|'||coalesce(source_hash,'') from ledger.entry "
                f"where run_id='{m.group(0)}' and node_type='file'")
    d = {}
    for line in out.splitlines():
        if "|" in line:
            p, h = line.rsplit("|", 1)
            d[p] = h
    return d


def current_hashes() -> dict:
    """{path: source_hash} over the real tree NOW. Excluded files (binary/secret/scratch) → '' to match the
    ledger's excluded entries exactly (else they'd read as perpetually 'changed')."""
    files, _ = enumerate_files(REPO)
    h = {}
    for rec in files:
        rel = rec["rel_path"]
        if any(rel.startswith(p) for p in SCRATCH_PREFIXES):     # same exclusion extract_folder applies
            h[rel] = ""
            continue
        src, raw = _read(rec["abs_path"], rel)
        h[rel] = "" if src is None else hashlib.sha256(raw).hexdigest()
    return h


def resolve_edges(ex: dict) -> dict:
    """Resolution pass — fill each edge's `to_resolved` (the real node id) from the in-memory facts, making
    the graph traversable. Precedence mirrors codeedges: same-file > unambiguous-global for calls/extends;
    module→file for imports; child node-id for contains. Unresolvable (external import, ambiguous name,
    dynamic dispatch) → null, honestly. No DB round-trip (computed before load)."""
    file_paths = set(e["path"] for e in ex["entries"] if e["node_type"] == "file")
    all_nodes = set(f"code://{PROJECT}/{e['path']}" for e in ex["entries"])
    mod_map = {}
    for p in file_paths:
        if p.endswith(".py"):
            mod_map[p[:-3].replace("/", ".")] = p
    global_name, per_file = {}, {}
    for s in ex["symbols"]:
        global_name.setdefault(s["name"], set()).add(s["code_id"])
        per_file.setdefault(s["_parent_path"], {}).setdefault(s["name"], s["code_id"])

    def file_of(ref):
        pre = f"code://{PROJECT}/"
        return ref[len(pre):].split("::")[0] if ref.startswith(pre) else None

    resolved_n = 0
    for g in ex["edges"]:
        k, raw, res = g["kind"], g["to_raw"], None
        if k == "contains":
            res = raw if raw in all_nodes else None
        elif k == "imports":
            res = f"code://{PROJECT}/{mod_map[raw]}" if raw in mod_map else None
        elif k in ("calls", "extends"):
            fp = file_of(g["from"])
            nm = raw.split(".")[-1]
            if fp and fp in per_file and nm in per_file[fp]:
                res = per_file[fp][nm]                           # same-file
            else:
                ids = global_name.get(nm)
                if ids and len(ids) == 1:
                    res = next(iter(ids))                        # unambiguous global
        g["to_resolved"] = res
        if res:
            resolved_n += 1
    ex["stats"]["edges_resolved"] = resolved_n
    return ex


# excluded from the ledger (recorded with a reason, never silently dropped — coverage stays honest):
#   discovery scratch (this effort's own outputs) + bulk DATA archives (recall transcripts — memory data,
#   not system code/structure). The ledger is of the SYSTEM, not its data dumps.
EXCLUDE_PREFIXES = [
    ("build-prep/the-one-system/discovery/", "discovery-scratch"),
    (".recollection/", "recall-data-archive"),
]
SCRATCH_PREFIXES = tuple(p for p, _ in EXCLUDE_PREFIXES)  # path-only alias (used by current_hashes)


def _exclude_reason(rel: str):
    for p, reason in EXCLUDE_PREFIXES:
        if rel.startswith(p):
            return reason
    return None


def extract_folder(folder: str) -> dict:
    """Extract every file under `folder` (rel to repo root), or the WHOLE tree if folder=''. Plus folder
    nodes + contains edges. Returns {entries, symbols, edges, stats}. Deterministic; no DB, no model."""
    all_files, _excl_dirs = enumerate_files(REPO)
    if folder:
        in_folder = [f for f in all_files if f["rel_path"] == folder or f["rel_path"].startswith(folder.rstrip("/") + "/")]
    else:
        in_folder = all_files
    entries, symbols, edges = [], [], []
    folders_seen = set()
    n_excluded = 0
    for rec in in_folder:
        rel = rec["rel_path"]
        _er = _exclude_reason(rel)
        if _er:
            entries.append({"node_type": "file", "path": rel, "parent": os.path.dirname(rel) or None,
                            "depth": rel.count("/"), "ext": os.path.splitext(rel)[1].lower(), "language": "",
                            "coverage_state": "excluded", "exclude_reason": _er})
            n_excluded += 1
            continue
        # ancestor folder nodes + contains edges
        parts = rel.split("/")
        for i in range(1, len(parts)):
            fdir = "/".join(parts[:i])
            if fdir and fdir not in folders_seen:
                folders_seen.add(fdir)
                fparent = "/".join(parts[:i - 1]) or None
                entries.append({"node_type": "folder", "path": fdir, "parent": fparent,
                                "depth": fdir.count("/"), "ext": "", "language": "", "coverage_state": "deterministic"})
                if fparent:
                    edges.append({"from": f"code://{PROJECT}/{fparent}", "kind": "contains",
                                  "to_raw": f"code://{PROJECT}/{fdir}", "line": None})
        facts = extract_file(rec)
        parent = os.path.dirname(rel) or None
        if facts.get("excluded"):
            entries.append({"node_type": "file", "path": rel, "parent": parent, "depth": rel.count("/"),
                            "ext": os.path.splitext(rel)[1].lower(), "language": "",
                            "coverage_state": "excluded", "exclude_reason": facts["excluded"]})
            n_excluded += 1
            if parent:
                edges.append({"from": f"code://{PROJECT}/{parent}", "kind": "contains",
                              "to_raw": f"code://{PROJECT}/{rel}", "line": None})
            continue
        e = {"node_type": "file", "path": rel, "parent": parent, "depth": rel.count("/"),
             "ext": facts["ext"], "language": facts["language"], "size_bytes": facts["size_bytes"],
             "line_count": facts["line_count"], "source_hash": facts["source_hash"],
             "coverage_state": "deterministic",
             "imports": facts.get("imports", []), "declares": facts.get("declares", []),
             "address_schemes_used": facts.get("address_schemes_used", []),
             "env_vars": facts.get("env_vars", []), "markers": facts.get("markers", []),
             "signals": facts.get("signals", {}),
             "extra": facts.get("extra_fields", {}),
             "extractor": facts.get("extractor", ""), "extractor_version": facts.get("extractor_version", "")}
        entries.append(e)
        if parent:
            edges.append({"from": f"code://{PROJECT}/{parent}", "kind": "contains",
                          "to_raw": f"code://{PROJECT}/{rel}", "line": None})
        for s in facts.get("symbols", []):
            s["_parent_path"] = rel
            s["extractor"] = facts.get("extractor", "")
            s["extractor_version"] = facts.get("extractor_version", "")
            symbols.append(s)
        edges.extend(facts.get("edges", []))
    ex = {"entries": entries, "symbols": symbols, "edges": edges,
          "stats": {"files": len(in_folder), "excluded": n_excluded, "folders": len(folders_seen),
                    "entries": len(entries), "symbols": len(symbols), "edges": len(edges)}}
    resolve_edges(ex)                                          # fill to_resolved (traversable graph)
    return ex


def load_run(scope_label: str, ex: dict, *, project: str, channel: str, purpose: str, session: str) -> str:
    """Create a run + COPY entries/symbols/edges in ONE transaction (accumulating; never truncates). A
    mid-load failure rolls back entirely (ON_ERROR_STOP + BEGIN/COMMIT) — no half-populated 'running' run.
    Run-identity (project/channel/purpose/session) + metadata (git sha, tool/schema version) are stamped."""
    run_id = str(uuid.uuid4())
    stats = {**ex["stats"], "schema_version": SCHEMA_VERSION}
    tmp = tempfile.mkdtemp(prefix="ledger-load-")
    epath, spath, gpath = (os.path.join(tmp, n) for n in ("entry.csv", "symbol.csv", "edge.csv"))

    ecols = ["run_id", "project", "path", "node_type", "parent", "depth", "ext", "language", "size_bytes",
             "line_count", "source_hash", "address", "coverage_state", "exclude_reason", "imports", "declares",
             "address_schemes_used", "env_vars", "markers", "signals", "extra", "extractor", "extractor_version",
             "produced_by_session", "pass"]
    erows = []
    for e in ex["entries"]:
        erows.append([run_id, project, e["path"], e["node_type"], e.get("parent") or "", e.get("depth", 0),
                      e.get("ext", ""), e.get("language", ""), e.get("size_bytes") or "", e.get("line_count") or "",
                      e.get("source_hash") or "", f"code://{project}/{e['path']}", e["coverage_state"],
                      e.get("exclude_reason") or "", _j(e.get("imports", [])), _j(e.get("declares", [])),
                      _j(e.get("address_schemes_used", [])), _j(e.get("env_vars", [])), _j(e.get("markers", [])),
                      _j(e.get("signals", {})), _j(e.get("extra", {})), e.get("extractor", ""),
                      e.get("extractor_version", ""), session, "deterministic-v1"])
    _write_csv(epath, erows)

    scols = ["run_id", "code_id", "parent_path", "name", "symbol_kind", "signature", "params", "returns",
             "decorators", "bases", "line_start", "line_end", "is_exported", "is_async", "extra",
             "extractor", "extractor_version", "produced_by_session", "pass"]
    srows, seen_cid = [], set()
    for s in ex["symbols"]:
        cid = s["code_id"]
        if cid in seen_cid:                                  # same-named symbol in one file → disambiguate by line
            cid = f"{cid}#L{s.get('line_start') or 0}"
            while cid in seen_cid:
                cid = f"{cid}."
        seen_cid.add(cid)
        srows.append([run_id, cid, s["_parent_path"], s["name"], s["symbol_kind"], s.get("signature", ""),
                      _j(s.get("params", [])), s.get("returns") or "", _j(s.get("decorators", [])),
                      _j(s.get("bases", [])), s.get("line_start") or "", s.get("line_end") or "",
                      str(s.get("is_exported", False)).lower(), str(s.get("is_async", False)).lower(),
                      _j({"stem_id": s.get("stem_id"), "qual": s.get("qual")}),
                      s.get("extractor", ""), s.get("extractor_version", ""), session, "deterministic-v1"])
    _write_csv(spath, srows)

    gcols = ["run_id", "from_ref", "kind", "to_raw", "to_resolved", "line", "produced_by_session", "pass"]
    grows = [[run_id, g["from"], g["kind"], g["to_raw"], g.get("to_resolved") or "", g.get("line") or "",
              session, "deterministic-v1"] for g in ex["edges"]]
    _write_csv(gpath, grows)

    scope = _j({"roots": [scope_label], "denominator": "real-tree"})
    script = (
        "BEGIN;\n"
        "INSERT INTO ledger.run (run_id, project, channel, purpose, layer, session_id, scope, tool_git_sha, "
        "tool_version, schema_version, status, stats, started_at) VALUES "
        f"('{run_id}', $${project}$$, $${channel}$$, $${purpose}$$, 'deterministic', $${session}$$, "
        f"$${scope}$$::jsonb, $${_git_sha()}$$, $${TOOL_VERSION}$$, {SCHEMA_VERSION}, 'running', "
        f"$${_j(stats)}$$::jsonb, now());\n"
        f"\\copy ledger.entry ({','.join(ecols)}) FROM '{epath}' WITH (FORMAT csv)\n"
        f"\\copy ledger.symbol ({','.join(scols)}) FROM '{spath}' WITH (FORMAT csv)\n"
        f"\\copy ledger.edge ({','.join(gcols)}) FROM '{gpath}' WITH (FORMAT csv)\n"
        f"UPDATE ledger.run SET status='complete', ended_at=now() WHERE run_id='{run_id}';\n"
        "COMMIT;\n")
    scriptf = os.path.join(tmp, "load.sql")
    with open(scriptf, "w") as f:
        f.write(script)
    r = subprocess.run(_psql_base() + ["-f", scriptf], capture_output=True, text=True, env=_pgenv())
    if r.returncode != 0:
        raise RuntimeError(f"ledger load FAILED — transaction rolled back, nothing committed:\n{r.stderr.strip()}")
    return run_id


def emit_legacy(project: str, purpose: str) -> dict:
    """Repoint the design analysis outputs onto the LEDGER as the source (the advisor's 'regenerate from
    the ledger' — one store, not parallels). Regenerates design/_system/code-edges.json (symbol→symbol
    structural graph) FROM the ledger's resolved edges, in the SAME consumed shape — so blast_radius +
    refcheck + the acceptance tests keep working unchanged, but the data is now the ledger's (whole-tree,
    resolved) instead of codeedges.py's narrow subset build. codeedges.py's standalone build is retired."""
    path2stem = {}
    for line in _psql("select code_id||chr(9)||coalesce(extra->>'stem_id','') from ledger.symbol_latest").splitlines():
        if chr(9) in line:
            cid, stem = line.split(chr(9), 1)
            if stem:
                path2stem[cid] = stem
    edges = {}
    def ens(s):
        edges.setdefault(s, {"depends_on": set(), "depended_by": set(), "resolves": True})
    for s in path2stem.values():
        ens(s)
    q = ("select from_ref||chr(9)||to_resolved from ledger.edge_latest "
         "where kind in ('calls','extends') and to_resolved is not null and to_resolved<>''")
    for line in _psql(q).splitlines():
        if chr(9) not in line:
            continue
        fr, to = line.split(chr(9), 1)
        fs, ts = path2stem.get(fr), path2stem.get(to)
        if fs and ts and fs != ts:
            ens(fs); ens(ts)
            edges[fs]["depends_on"].add(ts); edges[ts]["depended_by"].add(fs)
    doc = {"_what": "GENERATED FROM THE LEDGER (ops/ledger_build.py --emit-legacy) — supersedes the "
                    "standalone codeedges.py AST build. Whole-tree + resolved; keyed code://<file-stem>/"
                    "<symbol>. depends_on/depended_by/resolves preserved for existing consumers.",
           "edges": {k: {"depends_on": sorted(v["depends_on"]), "depended_by": sorted(v["depended_by"]),
                         "resolves": True} for k, v in edges.items()},
           "stale": [],
           "summary": {"symbols": len(edges), "with_depends_on": sum(1 for v in edges.values() if v["depends_on"]),
                       "with_depended_by": sum(1 for v in edges.values() if v["depended_by"]), "source": "ledger"},
           "shared": sorted(k for k, v in edges.items() if len(v["depended_by"]) >= 2)}
    p = os.path.join(REPO, "design", "_system", "code-edges.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
    return {"symbols": len(edges), "edges_path": p, "shared": len(doc["shared"])}


def health_check(project: str, purpose: str) -> bool:
    """The SECOND gate — extraction QUALITY (coverage proves file PRESENCE; this proves the facts aren't
    silently DEGRADED). Over the latest run for (project,purpose): HARD-FAIL on any code parse-error, and on
    a SYSTEMIC empty rate (>50% of an extractor's files with 0 symbols/headings → the extractor broke, e.g.
    the markdown-headings bug). Isolated empties (a legit script/config) are loud WARNINGS, not failures."""
    sel = (f"(select run_id from ledger.latest_run where project=$${project}$$ and purpose=$${purpose}$$)")
    base = f"from ledger.entry e where e.run_id = {sel}"
    def n(sql):
        v = _psql(sql); return int(v) if v.strip().isdigit() else 0
    parse_err = n(f"select count(*) {base} and e.extra ? 'parse_error'")
    checks = []  # (label, empty_count, total, sample_sql)
    checks.append(("python files with 0 symbols",
                   n(f"select count(*) {base} and e.extractor='python' and e.line_count>30 and (e.signals->>'n_symbols')::int=0 and e.path not like '%__init__.py' and e.path not like '%conftest.py'"),
                   n(f"select count(*) {base} and e.extractor='python' and e.line_count>30"),
                   "python"))
    checks.append(("ts/tsx files with 0 symbols",
                   n(f"select count(*) {base} and e.extractor='ts' and e.line_count>30 and (e.signals->>'n_symbols')::int=0"),
                   n(f"select count(*) {base} and e.extractor='ts' and e.line_count>30"), "ts"))
    checks.append(("markdown >50 lines with 0 headings & no frontmatter",
                   n(f"select count(*) {base} and e.extractor='markdown' and e.line_count>50 and (e.signals->>'n_headings')::int=0 and coalesce((e.signals->>'has_frontmatter')::bool,false)=false"),
                   n(f"select count(*) {base} and e.extractor='markdown' and e.line_count>50"), "markdown"))
    deep_pending = n(f"select count(*) {base} and e.extra ? 'deep_pending'")
    hard_fail = parse_err > 0
    print("HEALTH GATE (latest run):")
    print(f"  code parse-errors: {parse_err}" + ("  ❌ HARD-FAIL" if parse_err else "  ✓"))
    for label, empty, total, _ in checks:
        frac = (empty / total) if total else 0.0
        systemic = total >= 5 and frac > 0.5
        flag = "❌ SYSTEMIC (extractor likely broke)" if systemic else ("⚠ warn" if empty else "✓")
        if systemic: hard_fail = True
        print(f"  {label}: {empty}/{total} ({frac:.0%})  {flag}")
    print(f"  deep_pending (no extractor — informational): {deep_pending}")
    if parse_err:
        for p in _psql(f"select e.path {base} and e.extra ? 'parse_error' limit 8").splitlines():
            print(f"     parse-error: {p}")
    print("  ✅ HEALTHY" if not hard_fail else "  ❌ UNHEALTHY — fix the extractor before trusting this run")
    return not hard_fail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", default="", help="prove the rich extraction on ONE file (prints the record, no DB)")
    ap.add_argument("--folder", default="", help="extract every file under a folder (rel to repo root)")
    ap.add_argument("--all", action="store_true", help="extract the WHOLE tree")
    ap.add_argument("--load", action="store_true", help="load the extracted run into the Supabase ledger")
    ap.add_argument("--project", default="company", help="run identity: project (the address project)")
    ap.add_argument("--channel", default="channel://ch-9", help="run identity: the effort's channel")
    ap.add_argument("--purpose", default="one-system-ledger", help="run identity: purpose")
    ap.add_argument("--session", default=DEFAULT_SESSION, help="run identity: the session that ran it")
    ap.add_argument("--health", action="store_true", help="run the extraction-quality health gate on the latest run")
    ap.add_argument("--incremental", action="store_true",
                    help="diff source_hash vs the latest run; skip if unchanged, else snapshot + delta report")
    ap.add_argument("--emit-legacy", dest="emit_legacy", action="store_true",
                    help="regenerate design/_system/code-edges.json FROM the ledger (ledger = canonical source)")
    a = ap.parse_args()
    global PROJECT
    PROJECT = a.project

    if a.health:
        return 0 if health_check(a.project, a.purpose) else 1

    if a.emit_legacy:
        print("EMIT-LEGACY (code-edges.json from the ledger):", json.dumps(emit_legacy(a.project, a.purpose), indent=2))
        return 0

    if a.incremental:
        prev = latest_hashes(a.project, a.purpose)
        if prev is None:
            print("INCREMENTAL: no prior run — doing a full snapshot.")
        else:
            cur = current_hashes()
            changed = [p for p in cur if p in prev and cur[p] != prev[p]]
            new = [p for p in cur if p not in prev]
            deleted = [p for p in prev if p not in cur]
            print(f"DELTA vs latest run: changed={len(changed)} new={len(new)} deleted={len(deleted)}")
            for p in (changed + new)[:12]:
                print(f"   ~ {p}")
            for p in deleted[:6]:
                print(f"   - {p} (deleted)")
            if not (changed or new or deleted):
                print("✅ ledger up to date — nothing changed, no new run written.")
                return 0
            # The deterministic re-extract is ~14s, so a changed tree → a full accumulating SNAPSHOT (correct
            # across the resolution graph). Per-file-skip incremental is reserved for the EXPENSIVE model layer
            # (section 2), where it actually pays — see MODEL-NOTES. The delta above is the change record.
            print("changes detected → writing a full snapshot run (accumulating).")
        ex = extract_folder("")
        print("EXTRACTED:", json.dumps(ex["stats"], indent=2))
        run_id = load_run("(incremental-snapshot)", ex, project=a.project, channel=a.channel,
                          purpose=a.purpose, session=a.session)
        print(f"LOADED run {run_id} into the ledger.")
        return 0 if health_check(a.project, a.purpose) else 1

    if a.show:
        abs_path = os.path.join(REPO, a.show)
        rec = extract_file({"rel_path": a.show, "abs_path": abs_path})
        out = dict(rec)
        if out.get("symbols"):
            out["symbols"] = out["symbols"][:6] + ([f"... +{len(rec['symbols'])-6} more"] if len(rec["symbols"]) > 6 else [])
        if out.get("edges"):
            out["edges_sample"] = out["edges"][:12]; out["edges_total"] = len(rec["edges"]); del out["edges"]
        print(json.dumps(out, indent=2, default=str))
        return 0

    if a.folder or a.all:
        ex = extract_folder("" if a.all else a.folder)
        print("EXTRACTED:", json.dumps(ex["stats"], indent=2))
        if a.load:
            run_id = load_run("(whole-tree)" if a.all else a.folder, ex,
                              project=a.project, channel=a.channel, purpose=a.purpose, session=a.session)
            print(f"LOADED run {run_id} into the ledger.")
            ok = health_check(a.project, a.purpose)  # gate every load
            if not ok:
                return 1
        return 0

    print("use --show <file> to prove extraction; --folder <dir> [--load] to extract + load.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
