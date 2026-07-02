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
ROOT = REPO  # the scan root; override with --root to scan another repo into the SAME ledger (multi-project)
_SCHEME_RE = re.compile(r"\b([a-z][a-z0-9+.\-]*)://")
_TODO_RE = re.compile(r"\b(TODO|FIXME|XXX|HACK)\b")
_STUB_RE = re.compile(r"\b(skeleton|not wired|not-wired|stub|placeholder|not implemented|unimplemented)\b", re.I)
_EMIT_FNS = {"emit", "_emit", "_emit_durable", "append_event", "emit_event"}
_ROUTE_VERBS = {"get", "post", "put", "delete", "patch", "route", "add_api_route", "add_url_rule", "websocket"}
_SUBSCRIBE_FNS = {"subscribe", "on", "on_event", "add_listener", "addEventListener", "listen", "handle"}


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
            names = [a.name for a in n.names if a.name != "*"]     # the symbols this file pulls from mod
            imports.append({"target": mod, "kind": "from", "internal": _is_internal(mod),
                            "line": n.lineno, "lazy": n.col_offset > 0, "names": names})
            # carry the imported names on the edge so the resolver can bind call `foo()` -> mod::foo
            edges.append({"from": file_addr, "kind": "imports", "to_raw": mod, "line": n.lineno,
                          "extra": {"names": names} if names else {}})

    # module-level constructs (constants + uppercase-dict declarations — top-level only, correctly)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    nm = t.id
                    def _const_sym(kind, sig):                    # F3/R2: module constants ARE symbols (nodes)
                        symbols.append({"code_id": code_id(nm), "stem_id": f"code://{_stem(rel)}/{nm}",
                                        "name": nm, "qual": nm, "symbol_kind": kind, "signature": sig[:160],
                                        "params": [], "returns": None, "decorators": [], "bases": [],
                                        "line_start": node.lineno, "line_end": getattr(node, "end_lineno", node.lineno),
                                        "is_async": False, "is_exported": not nm.startswith("_")})
                    if nm.isupper() and isinstance(node.value, ast.Dict):
                        keys = [k.value for k in node.value.keys if isinstance(k, ast.Constant)]
                        registry_rows.append({"name": nm, "keys": keys[:60], "line": node.lineno})
                        constants.append({"name": nm, "value": _unparse(node.value)[:200], "line": node.lineno})
                        _const_sym("registry-dict", f"{nm} = {{…{len(keys)} keys}}")
                    elif nm.isupper() or re.match(r"^_[A-Z]", nm):
                        constants.append({"name": nm, "value": _unparse(node.value)[:200], "line": node.lineno})
                        _const_sym("constant", f"{nm} = {_unparse(node.value)[:120]}")

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
            # ROUTE DEFINITION — reusable: @app.get("/x")/@router.post/app.route/add_url_rule (FastAPI/Flask/
            # express-py) with a string path starting "/". Server SERVES this endpoint (the seam's far side).
            if fname in _ROUTE_VERBS and n.args and isinstance(n.args[0], ast.Constant) \
                    and isinstance(n.args[0].value, str) and n.args[0].value.startswith("/"):
                routes.add(n.args[0].value)
                edges.append({"from": file_addr, "kind": "serves-endpoint", "to_raw": n.args[0].value,
                              "line": getattr(n, "lineno", None)})
        elif isinstance(n, ast.Compare) and len(n.comparators) == 1:
            # DISPATCHER pattern (stdlib-http): `self.path == "/api/x"` / `path == "/api/x"` — the company
            # bridge's route table. Either side may hold the literal. Server SERVES it.
            for side in (n.left, n.comparators[0]):
                if isinstance(side, ast.Constant) and isinstance(side.value, str) and side.value.startswith("/api/"):
                    routes.add(side.value)
                    edges.append({"from": file_addr, "kind": "serves-endpoint", "to_raw": side.value,
                                  "line": getattr(n, "lineno", None)})
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

    # SUBSCRIBES-EVENT — the consumer side of the event graph (matches the file-level emits-event edges).
    # Consumers pull the log and filter by kind: `x.get("kind") == "lit"` (inline) or bind `k = x.get("kind")`
    # then `k == "lit"` / `k in TUPLE` (dispatch). Two passes: collect the kind-bound vars, then harvest.
    def _is_kind_access(node):                                    # x.get("kind"|"type") or x["kind"|"type"]
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get" \
                and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value in ("kind", "type"):
            return True
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant) and node.slice.value in ("kind", "type"):
            return True
        return False
    kind_vars, tuple_consts = set(), {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and _is_kind_access(n.value):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    kind_vars.add(t.id)
        if isinstance(n, ast.Assign) and isinstance(n.value, (ast.Tuple, ast.List)):  # named string-tuple consts
            lits = [e.value for e in n.value.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
            if lits and len(lits) == len(n.value.elts):
                for t in n.targets:
                    if isinstance(t, ast.Name):
                        tuple_consts[t.id] = lits
    subs = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Compare) and len(n.comparators) == 1 and isinstance(n.ops[0], (ast.Eq, ast.In)):
            left, right, op = n.left, n.comparators[0], n.ops[0]
            kind_side = (isinstance(left, ast.Name) and left.id in kind_vars) or _is_kind_access(left)
            if isinstance(op, ast.Eq) and kind_side and isinstance(right, ast.Constant) and isinstance(right.value, str):
                subs.add(right.value)
            elif isinstance(op, ast.In) and kind_side:            # k in ("a","b") / k in NAMED_TUPLE
                if isinstance(right, (ast.Tuple, ast.List)):
                    subs.update(e.value for e in right.elts if isinstance(e, ast.Constant) and isinstance(e.value, str))
                elif isinstance(right, ast.Name) and right.id in tuple_consts:
                    subs.update(tuple_consts[right.id])
    for ev in sorted(subs):
        edges.append({"from": file_addr, "kind": "subscribes-event", "to_raw": ev, "line": None})

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


_INTERNAL_TOPS = None


def _internal_tops() -> set:
    # REUSABLE: internal top-level packages = the scanned repo's own top dirs (derived from ROOT), not a
    # company-specific literal. Cached; recomputed per process (ROOT is set once from --root in main()).
    global _INTERNAL_TOPS
    if _INTERNAL_TOPS is None:
        try:
            _INTERNAL_TOPS = {d for d in os.listdir(ROOT)
                              if os.path.isdir(os.path.join(ROOT, d)) and not d.startswith(".")}
        except Exception:
            _INTERNAL_TOPS = set()
    return _INTERNAL_TOPS


def _is_internal(mod: str) -> bool:
    top = mod.split(".")[0].lstrip(".")
    return top in _internal_tops() or mod.startswith(".")


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


_TS_LIB = None


def _resolve_ts_lib() -> str:
    """Find the SCANNED repo's OWN `typescript` (node_modules dir), wherever it lives — root or a sub-app
    (open-webui: root; this repo: canvas/app/node_modules). Reusable, no cross-repo dependency. Env override
    wins. Absent -> JS/TS recorded shallow with reason (loud). Bounded-depth glob so it's cheap."""
    global _TS_LIB
    if _TS_LIB is not None:
        return _TS_LIB
    import glob
    env = os.environ.get("COMPANY_TS_LIB", "")
    if env and os.path.isdir(os.path.join(env, "typescript")):
        _TS_LIB = env
        return env
    for pat in ("node_modules/typescript", "*/node_modules/typescript", "*/*/node_modules/typescript"):
        hits = glob.glob(os.path.join(ROOT, pat))
        if hits:
            _TS_LIB = os.path.dirname(sorted(hits)[0])            # the node_modules dir (ts_extract.js requires it)
            return _TS_LIB
    _TS_LIB = ""
    return ""


def extract_ts(rel: str, src: str, raw: bytes = b"") -> dict:
    """Real-AST extractor for JS/JSX/TS/TSX via the TypeScript compiler (ops/ts_extract.js over node) —
    replaces the line-regex that was blind to expression-embedded definitions (object-literal methods,
    window.* assigns, HOC/anonymous components). Captures functions/components/classes/methods/interfaces/
    types/enums/module-constants + imports + the JS call-graph + endpoints + events. Same return contract."""
    file_addr = f"code://{PROJECT}/{rel}"

    def shallow(reason):
        return {"imports": [], "declares": [], "address_schemes_used": _schemes(src), "env_vars": [],
                "markers": _scan_markers(src), "symbols": [], "edges": [],
                "signals": {"js_extract_skipped": reason, "has_entry_point": False},
                "extra_fields": {"js_extract_skipped": reason}}

    lib = _resolve_ts_lib()
    if not lib:
        return shallow("typescript not resolvable - `npm i typescript` or set COMPANY_TS_LIB for JS/TS extraction")
    try:
        proc = subprocess.run(["node", os.path.join(REPO, "ops", "ts_extract.js"), rel, lib],
                              input=src, capture_output=True, text=True, timeout=90)
        data = json.loads(proc.stdout) if proc.stdout.strip() else {"error": (proc.stderr or "no output")[:200]}
    except Exception as e:
        return shallow(f"node/ts_extract failed: {str(e)[:150]}")
    if "error" in data:
        return shallow(f"parse error: {str(data['error'])[:150]}")

    symbols, edges, imports = [], [], []
    components, exports, types, consts = [], [], [], []
    for s in data.get("symbols", []):
        nm, kind = s.get("name", ""), s.get("kind", "")
        if not nm:
            continue
        symbols.append({"code_id": f"code://{PROJECT}/{rel}::{nm}", "stem_id": f"code://{_stem(rel)}/{nm}",
                        "name": nm, "qual": nm, "symbol_kind": kind, "signature": nm,
                        "params": [], "returns": None, "decorators": [], "bases": [],
                        "line_start": s.get("line", 0), "line_end": s.get("line", 0),
                        "is_async": s.get("async", False), "is_exported": s.get("exported", False)})
        if kind == "component": components.append(nm)
        if kind in ("type", "interface", "enum"): types.append(nm)
        if kind == "constant": consts.append(nm)
        if s.get("exported"): exports.append(nm)
    for im in data.get("imports", []):
        imports.append({"target": im["target"], "kind": "import", "internal": im.get("relative", False),
                        "line": im.get("line", 0)})
        edges.append({"from": file_addr, "kind": "imports", "to_raw": im["target"], "line": im.get("line", 0)})
    for c in data.get("calls", []):
        edges.append({"from": file_addr, "kind": "calls", "to_raw": c["name"], "line": c.get("line", 0)})
    api_calls = data.get("endpoints", [])
    for e in api_calls:
        edges.append({"from": file_addr, "kind": "calls-endpoint", "to_raw": e["url"], "line": e.get("line", 0)})
    # UI BINDINGS — the DERIVED ui://→code join (Tim 2026-07-02: a universal mechanism recomputed every
    # extraction, never a curated registry). A FE file that carries a ui:// address is bound to it; the
    # resolver then materializes powered-by from these + the endpoint seam. extra.src = attr|literal|template.
    for u in data.get("ui_binds", []):
        edges.append({"from": file_addr, "kind": "binds-ui", "to_raw": u["addr"], "line": u.get("line", 0),
                      "extra": {"src": u.get("src", "")}})
    events = sorted(set(data.get("events", [])))
    seen, uedges = set(), []
    for g in edges:
        k = (g["kind"], g["to_raw"], g["line"])
        if k not in seen:
            seen.add(k); uedges.append(g)
    signals = {"n_imports": len(imports), "n_symbols": len(symbols), "n_components": len(set(components)),
               "n_exports": len(set(exports)), "n_types": len(types), "n_constants": len(set(consts)),
               "n_calls": sum(1 for g in uedges if g["kind"] == "calls"),
               "n_api_calls": len(api_calls), "n_edges": len(uedges), "has_entry_point": False}
    return {"imports": imports, "declares": [{"name": s["name"], "kind": s["symbol_kind"], "line": s["line_start"]}
                                             for s in symbols if s["is_exported"]],
            "address_schemes_used": _schemes(src), "env_vars": [], "markers": _scan_markers(src),
            "signals": signals, "symbols": symbols, "edges": uedges,
            "extra_fields": {"components": sorted(set(components)), "exports": sorted(set(exports)),
                             "api_calls": api_calls, "types": types, "constants": sorted(set(consts)),
                             "events": events}}


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
    {"id": "python",   "version": "py-ast-v2",   "parse_safe": True, "match": lambda ext, lang: lang == "python",
     "fn": lambda rel, src, raw: _python_norm(rel, src, raw)},
    {"id": "ts",       "version": "ts-tsc-v1", "parse_safe": True, "match": lambda ext, lang: ext in _TS_EXTS,
     "fn": lambda rel, src, raw: extract_ts(rel, src, raw)},
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


# deep-extraction guards (production-grade): a generated/minified/oversized file is recorded as a SHALLOW
# node (shape + reason) — NOT deep-regex'd. Reasons: (a) minified bundles are one giant line → catastrophic
# regex backtracking; (b) they're DERIVED artifacts (rebuild from source), so deep facts belong to the source.
_MAX_TEXT_DEEP = 800_000     # bytes — above this, deep extraction is skipped (record shape)
_MAX_LINE_DEEP = 5_000       # chars — a max line longer than this signals minified/generated → skip deep


def _too_big_to_deep_parse(src: str, raw: bytes, parse_safe: bool = False) -> str | None:
    # parse_safe extractors (real AST/tree-sitter parsers — python, tree-sitter) handle large files fine;
    # the byte cap only ever protected the REGEX path from catastrophic backtracking. So skip it for them.
    # The minified-single-line guard still applies to ALL: a one-line generated bundle is a DERIVED artifact
    # (rebuild from source), recorded shallow — not a parse limitation, a relevance decision.
    if not parse_safe and len(raw) > _MAX_TEXT_DEEP:
        return f"oversized:{len(raw)//1024}KB"
    # max line length without materializing all lines hugely: scan once
    maxln = 0
    for ln in src.splitlines():
        if len(ln) > maxln:
            maxln = len(ln)
            if maxln > _MAX_LINE_DEEP:
                return f"minified:max-line>{_MAX_LINE_DEEP}"
    return None


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
    big = _too_big_to_deep_parse(src, raw, parse_safe=bool(chosen and chosen.get("parse_safe")))
    if big:
        base["extractor"], base["extractor_version"] = "shallow", "shallow-v1"
        base.update({"imports": [], "declares": [], "address_schemes_used": [], "env_vars": [],
                     "markers": [], "symbols": [], "edges": [],
                     "signals": {"shallow": True, "has_entry_point": False},
                     "extra_fields": {"shallow_reason": big, "note": "generated/minified/oversized — recorded as a node, not deep-parsed (derived artifact; deep facts live in its source)"}})
        return base
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
        return subprocess.check_output(["git", "-C", ROOT, "rev-parse", "HEAD"], text=True).strip()
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
    files, _ = enumerate_files(ROOT)
    h = {}
    for rec in files:
        rel = rec["rel_path"]
        if any(rel.startswith(p) for p in SCRATCH_PREFIXES):     # same exclusion extract_folder applies
            h[rel] = ""
            continue
        src, raw = _read(rec["abs_path"], rel)
        h[rel] = "" if src is None else hashlib.sha256(raw).hexdigest()
    return h


import builtins as _builtins, sys as _sys
_PY_BUILTINS = set(dir(_builtins))
_STDLIB = set(getattr(_sys, "stdlib_module_names", ()))
_JS_GLOBALS = {"console", "window", "document", "Math", "JSON", "Object", "Array", "Promise", "String",
               "Number", "Boolean", "Date", "RegExp", "Map", "Set", "WeakMap", "Symbol", "Error", "parseInt",
               "parseFloat", "isNaN", "setTimeout", "setInterval", "clearTimeout", "fetch", "require", "process",
               "module", "exports", "global", "globalThis", "localStorage", "navigator", "location", "alert"}
_JS_RES_EXT = ("", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".d.ts")


def resolve_edges(ex: dict) -> dict:
    """Resolution pass — fill each edge's `to_resolved` (the real node id) from in-memory facts, and CLASSIFY
    every far-end that can't resolve (builtin | stdlib | external) so 'unresolved' is honest, not conflated
    with 'broken wiring'. Handles: contains (child id); imports (python module-map + JS/TS relative/path
    module-resolution); calls/extends/references (same-file > import-scoped > unambiguous-global). Far-end
    class lands in edge.extra.far. No DB round-trip. Reusable — all facts come from the scanned tree."""
    file_set = set(e["path"] for e in ex["entries"] if e["node_type"] == "file")
    all_nodes = set(f"code://{PROJECT}/{p}" for p in file_set)
    mod_map = {p[:-3].replace("/", "."): p for p in file_set if p.endswith(".py")}
    global_name, per_file = {}, {}
    per_file_qual = {}                                           # file -> {qual (e.g. 'ClassName.method'): code_id}
    class_files = {}                                             # ClassName -> set of files defining it
    for s in ex["symbols"]:
        global_name.setdefault(s["name"], set()).add(s["code_id"])
        per_file.setdefault(s["_parent_path"], {}).setdefault(s["name"], s["code_id"])
        qual = s["code_id"].split("::", 1)[1] if "::" in s["code_id"] else s["name"]
        per_file_qual.setdefault(s["_parent_path"], {})[qual] = s["code_id"]
        if s["symbol_kind"] == "class":
            class_files.setdefault(s["name"], set()).add(s["_parent_path"])

    def file_of(ref):
        pre = f"code://{PROJECT}/"
        return ref[len(pre):].split("::")[0] if ref.startswith(pre) else None

    def enclosing_class(ref):                                    # from 'file.py::ClassName.method' -> 'ClassName'
        if "::" not in ref:
            return None
        q = ref.split("::", 1)[1]
        return q.rsplit(".", 1)[0] if "." in q else None

    def resolve_js_import(from_file, target):                    # relative/path → a real file in the tree
        cand = os.path.normpath(os.path.join(os.path.dirname(from_file), target))
        for e in _JS_RES_EXT:
            if cand + e in file_set:
                return cand + e
        for idx in ("index.ts", "index.tsx", "index.js", "index.jsx"):
            p = os.path.normpath(os.path.join(cand, idx))
            if p in file_set:
                return p
        return None

    def classify(raw):
        head, leaf = raw.split(".")[0], raw.split(".")[-1]
        if head in _PY_BUILTINS or leaf in _PY_BUILTINS or head in _JS_GLOBALS:
            return "builtin"
        if head in _STDLIB:
            return "stdlib"
        return "external"                                        # a library / dynamic / method-on-value

    # endpoint index: normalized server URL -> serving node(s). Built from serves-endpoint edges so the
    # client seam (calls-endpoint) can resolve to the backend that answers it. Reusable (both sides are data).
    def norm_url(u):
        u = u.split("?")[0].split("#")[0]                        # drop query/fragment
        return u.rstrip("/") or "/"
    endpoint_serves = {}
    for g in ex["edges"]:
        if g["kind"] == "serves-endpoint":
            endpoint_serves.setdefault(norm_url(g["to_raw"]), set()).add(g["from"])
    # event index: name -> emitter file(s). subscribes-event resolves to the emitter (symmetric to endpoints).
    event_emits = {}
    for g in ex["edges"]:
        if g["kind"] == "emits-event":
            event_emits.setdefault(g["to_raw"], set()).add(g["from"])


    def resolve_endpoint(url):
        u = norm_url(url)
        if u in endpoint_serves:
            hit = endpoint_serves[u]
            return next(iter(hit)) if len(hit) == 1 else None    # unambiguous exact
        # prefix routes: server "/api/image" serves client "/api/image/123"
        best = None
        for su, servers in endpoint_serves.items():
            if u.startswith(su + "/") and len(servers) == 1 and (best is None or len(su) > len(best[0])):
                best = (su, next(iter(servers)))
        return best[1] if best else None

    # PASS A — imports (builds: per-file imported-FILE set + per-file imported-NAME→file map, both used
    # for import-scoped call resolution — `from x import foo; foo()` binds foo -> x's file, then x::foo).
    per_file_imp, per_file_name, resolved_n = {}, {}, 0
    for g in ex["edges"]:
        if g["kind"] != "imports":
            continue
        raw, ff, res = g["to_raw"], file_of(g["from"]), None
        if raw in mod_map:
            res = f"code://{PROJECT}/{mod_map[raw]}"
        elif ff and (raw.startswith(".") or "/" in raw):
            rf = resolve_js_import(ff, raw)
            res = f"code://{PROJECT}/{rf}" if rf else None
        g["to_resolved"] = res
        if res:
            resolved_n += 1
            resf = res.split("::")[0]
            per_file_imp.setdefault(ff, set()).add(resf)
            for nm in (g.get("extra") or {}).get("names", []):     # bind each imported name to its file
                per_file_name.setdefault(ff, {})[nm] = resf
        else:
            g.setdefault("extra", {})["far"] = "stdlib" if raw.split(".")[0] in _STDLIB else "external"

    # PASS B — contains / calls / extends / references (import-scoped, then classify the misses)
    for g in ex["edges"]:
        k, raw = g["kind"], g["to_raw"]
        if k in ("imports", "binds-ui", "powered-by"):           # already resolved in their own passes above
            continue
        res = None
        if k == "contains":
            res = raw if raw in all_nodes else None
        elif k == "calls-endpoint":
            res = resolve_endpoint(raw)                          # client seam -> the backend that serves it
            if not res:
                g.setdefault("extra", {})["far"] = "external"    # a URL no server in this tree serves
        elif k == "subscribes-event":
            hit = event_emits.get(raw) or set()                  # consumer -> the emitter of that event
            res = next(iter(hit)) if len(hit) == 1 else None
            if not res and not hit:
                g.setdefault("extra", {})["far"] = "external"    # subscribed to an event nothing in-tree emits
        elif k in ("calls", "extends", "references"):
            ff, nm = file_of(g["from"]), raw.split(".")[-1]
            recv = raw.split(".")[0] if "." in raw else None
            # RECEIVER-AWARE dotted resolution — resolve what the code LOCALLY states, no type inference:
            if recv in ("self", "cls") and ff:                   # self.m -> the enclosing class's m (same file)
                ec = enclosing_class(g["from"])                  # exact Class.method only (base-class m -> stays
                if ec:                                           # unresolved+classified; a guess would mis-link)
                    res = per_file_qual.get(ff, {}).get(f"{ec}.{nm}")
            elif recv and recv[:1].isupper() and recv in class_files:  # ClassName.m -> that class's m
                for cf in class_files[recv]:
                    hit = per_file_qual.get(cf, {}).get(f"{recv}.{nm}")
                    if hit:
                        res = hit
                        break
            if res is None and ff and ff in per_file and nm in per_file[ff]:
                res = per_file[ff][nm]                           # same-file
            elif res is None and ff and nm in per_file_name.get(ff, {}):  # `from x import nm` -> x::nm
                tgt_file = per_file_name[ff][nm]
                cand = per_file.get(tgt_file[len(f"code://{PROJECT}/"):], {}).get(nm)
                res = cand or None
            elif res is None:
                ids = global_name.get(nm) or set()
                if len(ids) == 1:
                    res = next(iter(ids))                        # unambiguous global
                elif len(ids) > 1 and ff in per_file_imp:        # import-scoped: unique candidate in an imported file
                    cands = [i for i in ids if i.split("::")[0] in per_file_imp[ff]]
                    if len(cands) == 1:
                        res = cands[0]
        g["to_resolved"] = res
        if res:
            resolved_n += 1
        elif k in ("calls", "extends", "references"):
            g.setdefault("extra", {})["far"] = classify(raw)     # honest: builtin | stdlib | external

    # PASS C — THE ui://→code JOIN, MATERIALIZED (Tim 2026-07-02: a universal mechanism recomputed every
    # build, never a curated registry — today's FE is its first input; the future real UI is born joined by
    # this same pass). Runs AFTER pass B so calls-endpoint→serves-endpoint resolutions exist. For every
    # ui:// address any FE file binds: mint a ui ENTRY (node_type='ui', address = the ui:// itself) +
    # powered-by edges to (a) each binding file and (b) the backend files serving the endpoints those
    # binding files call. Deterministic; anything underivable stays unjoined (empty scope = DENY-ALL holds).
    ui_bound_by = {}                                             # ui addr -> {binding file addrs}
    for g in ex["edges"]:
        if g["kind"] == "binds-ui":
            g["to_resolved"] = g["to_raw"]                       # the ui node exists by construction (below)
            resolved_n += 1
            ui_bound_by.setdefault(g["to_raw"], set()).add(g["from"])

    # HAND-SEED fold (legacy, read-if-present): the pre-ledger registry's 104 hand-curated `code` links
    # (design/_system/addresses.json — e.g. "ui://inbox/build-review powers runtime/suite.py:review_verdicts")
    # carry human knowledge the mechanical chain can't derive (WHICH backend symbol is the meaningful one).
    # Folded as powered-by seeds tagged src='hand-seed'; malformed refs (bare filenames) repaired by
    # unambiguous basename match against the tree; unrepairable ones counted, never guessed. This block
    # auto-retires when addresses.json is deleted (the registry is scaffolding; the mechanism is the product).
    _addr_json = os.path.join(ROOT, "design", "_system", "addresses.json")
    if os.path.isfile(_addr_json):
        try:
            _areg = json.load(open(_addr_json, encoding="utf-8")).get("addresses", {})
        except Exception:
            _areg = {}
        _by_base = {}
        for p in file_set:
            _by_base.setdefault(os.path.basename(p), []).append(p)
        seeded = skipped_refs = 0
        for _ua, _rec in _areg.items():
            _code = (_rec or {}).get("code")
            if not _code or not _ua.startswith("ui://"):
                continue
            for _ref in str(_code).split(" / "):
                _ref = _ref.split(" (")[0].strip()               # drop the trailing annotation
                _p = _ref.split(":")[0].strip().rstrip("/")
                if not _p:
                    continue
                if _p not in file_set:                           # repair bare/malformed by unambiguous basename
                    c = _by_base.get(os.path.basename(_p), [])
                    if len(c) == 1:
                        _p = c[0]
                    else:
                        skipped_refs += 1                        # ambiguous/dead — counted, not guessed
                        continue
                ui_bound_by.setdefault(_ua, set())               # ensure the ui node gets minted
                ex["edges"].append({"from": _ua, "kind": "powered-by",
                                    "to_raw": f"code://{PROJECT}/{_p}", "to_resolved": f"code://{PROJECT}/{_p}",
                                    "line": None, "extra": {"src": "hand-seed"}})
                resolved_n += 1
                seeded += 1
        ex["stats"]["ui_hand_seeded"] = seeded
        ex["stats"]["ui_hand_skipped"] = skipped_refs            # visible, never silent
    if ui_bound_by:
        file_endpoint_targets = {}                               # binding file -> {resolved backend file addrs}
        for g in ex["edges"]:
            if g["kind"] == "calls-endpoint" and g.get("to_resolved"):
                file_endpoint_targets.setdefault(g["from"].split("::")[0], set()).add(g["to_resolved"].split("::")[0])
        existing_ui = set(e["path"] for e in ex["entries"] if e.get("node_type") == "ui")
        for ui_addr, binders in sorted(ui_bound_by.items()):
            if ui_addr not in existing_ui:
                ex["entries"].append({"node_type": "ui", "path": ui_addr, "parent": None,
                                      "depth": 0, "ext": "", "language": "ui", "size_bytes": 0, "line_count": 0,
                                      "source_hash": "", "coverage_state": "derived",
                                      "imports": [], "declares": [], "address_schemes_used": [], "env_vars": [],
                                      "markers": [], "signals": {"n_binders": len(binders)}, "extra_fields": {}})
            powered = set()
            for bf in binders:
                bfile = bf.split("::")[0]
                powered.add(bfile)                               # the component file itself powers the element
                powered |= file_endpoint_targets.get(bfile, set())  # + the backend answering its calls
            for tgt in sorted(powered):
                ex["edges"].append({"from": ui_addr, "kind": "powered-by", "to_raw": tgt,
                                    "to_resolved": tgt, "line": None})
                resolved_n += 1
    ex["stats"]["edges_resolved"] = resolved_n
    return ex


# excluded from the ledger (recorded with a reason, never silently dropped — coverage stays honest):
#   discovery scratch (this effort's own outputs) + bulk DATA archives (recall transcripts — memory data,
#   not system code/structure). The ledger is of the SYSTEM, not its data dumps.
EXCLUDE_PREFIXES = [
    ("build-prep/the-one-system/discovery/", "discovery-scratch"),
    (".recollection/", "recall-data-archive"),
    # claude-ds is a SEPARATE project synced INTO ~/company/design/ — scanned as its own project
    # `claude-ds`; exclude from the `company` project so it isn't double-counted. (Its own scan uses
    # root=.../design/claude-ds, where these files are top-level, so this prefix won't self-exclude it.)
    ("design/claude-ds/", "separate-project:claude-ds"),
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
    all_files, _excl_dirs = enumerate_files(ROOT)
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
                      e.get("source_hash") or "",
                      # a ui node's path IS its address (ui://…); files/folders get code://<project>/<path>
                      e["path"] if e.get("node_type") == "ui" else f"code://{project}/{e['path']}",
                      e["coverage_state"],
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

    gcols = ["run_id", "from_ref", "kind", "to_raw", "to_resolved", "line", "produced_by_session", "pass", "extra"]
    grows = [[run_id, g["from"], g["kind"], g["to_raw"], g.get("to_resolved") or "", g.get("line") or "",
              session, "deterministic-v1", json.dumps(g.get("extra") or {})] for g in ex["edges"]]
    # ④ L4 (GRAPH-PATH §3.1) — FAIL-LOUD kind validation against the ONE edge-kind registry BEFORE the
    # COPY (rule 4; C4.1). An unregistered kind names edge_kinds/ + the absorb path (ABSORB-never-reject:
    # register the kind, never drop the edge). No hard FK on the shared table — the gate is here on the
    # write path. Skipped only if the registry table isn't present yet (a pre-0018 scratch DB) — never a
    # silent pass on a LIVE registry.
    try:
        from runtime.edge_kinds import validate_kinds as _validate_edge_kinds
        _validate_edge_kinds({g["kind"] for g in ex["edges"]})
    except ImportError:
        pass
    except RuntimeError as _e:
        if "unreachable" not in str(_e) and "does not exist" not in str(_e):
            raise
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
    # L9 SUPERSESSION (2026-07-02): after each load, refresh the run-INDEPENDENT durable tables
    # (ledger.interpretation / ledger.assertion) so a rebuild can never strand enrichment below the *_latest
    # views (unit_latest/edge_unified read the durable tables — proven cured). Idempotent + freshness-guarded;
    # best-effort so a durable-sync hiccup never fails a committed structural load. The heartbeat job (L10)
    # runs this same sync on change; here it keeps every manual/CLI build self-maintaining.
    try:
        from ops.sync_durability import sync_durability
        _dur = sync_durability()
        if _dur.get("interpretation_added") or _dur.get("assertion_added"):
            print(f"  durable sync: +{_dur}")
    except Exception as _e:                                    # loud on stderr, never fails the load
        print(f"  ⚠ durable sync skipped ({type(_e).__name__}: {_e}) — run ops/sync_durability.py manually")
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
    ap.add_argument("--root", default="", help="scan a DIFFERENT repo root into the same ledger (default: this repo)")
    a = ap.parse_args()
    global PROJECT, ROOT
    PROJECT = a.project
    if a.root:
        ROOT = os.path.abspath(os.path.expanduser(a.root))

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
        abs_path = os.path.join(ROOT, a.show)
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
