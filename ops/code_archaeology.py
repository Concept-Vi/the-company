#!/usr/bin/env python3
"""ops/code_archaeology.py — the code-archaeology DRAGNET (the reusable build-prep PRIMITIVE).

board://item-d1a7bf75 + build-prep/the-one-application/CODE-ARCHAEOLOGY-DRAGNET-DESIGN.md. A coverage-complete,
queryable MAP of a repo — run/refresh it BEFORE a significant build, then synthesize from it. The fix for
"agents sample → get confident → build from partial info" (the recurring failure). DESCRIPTIVE-ONLY.

REUSE (don't-fork): cog.run_items (the shared 32-concurrent runner) for the LLM prose; Suite.capture_corpus
for the write+embed into the registered `code_archaeology` space; contracts/address for code:// addressing.
NOT a touch of recollection's dragnet_extract.py (the sibling-isolation seam, lead-settled).

PARSER-FIRST (the quality call): structural facts (symbols/imports/declares) are DETERMINISTIC (Python ast;
regex for JS/TS/sh/sql; keys for JSON) — an LLM hallucinates them, and the synthesis maps the registry/provider
landscape FROM them. The LLM does ONLY the prose (what_it_is coarse · summary/touchpoints fine). This also
resolves the chunk-native-engine vs file-native-spec mismatch: the parser gives whole-file structure, so the
LLM unit is the FILE (one record per file), never a byte window.

★ COVERAGE-CORRECTNESS (DNA's catch): the denominator is the REAL FILESYSTEM TREE, NOT git-ls-files —
git-ignored content dirs (e.g. a design system in reference/) would be silently omitted (the exact failure the
dragnet kills). enumerate() walks the real tree; excludes only TRUE junk (loud per-exclusion reason).

M1 = the COVERAGE PROOF: enumerate → parse → cascade → merge → capture+embed → LEDGER at 100%
(denominator == Σ states, fail-loud on a gap). M2 (field-index / registry-discoverability) fast-follows.

Run: python3 ops/code_archaeology.py --sample 25   (PROVE the pipeline; does not write the asset)
     python3 ops/code_archaeology.py --all --confirm   (the full M1 coverage run + ledger)
"""
from __future__ import annotations
import argparse, ast, hashlib, json, os, re, sys, time
from datetime import datetime, timezone
from typing import List
from pydantic import BaseModel

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
OUT_DIR = os.path.join(REPO, ".data", "store", "code_archaeology")

# ── coverage: walk the REAL tree, exclude only TRUE junk (DNA coverage-correctness — NOT git-ls-files) ──
_JUNK_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
             ".data", ".cache", ".venv", "venv", "dist", "build", ".build", ".next", ".turbo", "coverage"}
# ★ SECURITY: the real-tree walk re-includes git-ignored files — git-ignore protects BOTH junk AND SECRETS.
# A secrets/credentials/key file must NEVER be described/embedded into the corpus. Exclude by name/ext/substring.
_SENSITIVE_EXT = {".key", ".pem", ".p12", ".pfx", ".keystore", ".crt"}
_SENSITIVE_HINT = ("secret", "credential", "password", "id_rsa", "id_ed25519", ".htpasswd", ".npmrc")
_BINARY_EXT = {".pyc", ".so", ".o", ".a", ".dylib", ".dll", ".bin", ".wav", ".mp3", ".mp4", ".png", ".jpg",
              ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz", ".tar", ".whl", ".db", ".sqlite",
              ".lock", ".woff", ".woff2", ".ttf", ".eot", ".parquet", ".npy", ".pt", ".bin", ".onnx"}
_CODE_BEARING = {"module", "script"}              # the step-gate: these continue to FINE


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_junk_dir(name: str, abspath: str) -> bool:
    """TRUE junk = vendored/generated/cache (NOT content). Robust to project-specific venv names (.voice-venv,
    .litellm-venv) via name-pattern + the definitive pyvenv.cfg signature — NOT a hardcoded venv-name list."""
    if name in _JUNK_DIRS:
        return True
    if name == "site-packages" or name.endswith("venv") or name.endswith("-venv"):
        return True
    try:
        if os.path.exists(os.path.join(abspath, "pyvenv.cfg")):    # a virtualenv by signature, any name
            return True
    except OSError:
        pass
    return False


def enumerate_files(repo: str, *, include_gitignored=()) -> list[dict]:
    """The DENOMINATOR — the REAL filesystem tree (os.walk), TRUE-junk pruned. `include_gitignored` is an
    explicit allow-list of git-ignored content dirs to force-include (the design source/+reference/ case —
    empty for the company repo, where the git-ignored set is junk). Returns [{rel_path, abs_path}]."""
    out = []
    incl = set(include_gitignored)
    for dirpath, dirnames, filenames in os.walk(repo):
        rel_dir = os.path.relpath(dirpath, repo)
        top = (rel_dir.split(os.sep)[0]) if rel_dir != "." else ""
        # prune junk dirs IN PLACE (os.walk honours dirnames mutation) — but never prune a force-included dir
        dirnames[:] = [d for d in dirnames
                       if not _is_junk_dir(d, os.path.join(dirpath, d)) or (os.path.join(rel_dir, d) in incl)]
        for fn in filenames:
            rel = os.path.normpath(os.path.join(rel_dir, fn)) if rel_dir != "." else fn
            out.append({"rel_path": rel, "abs_path": os.path.join(dirpath, fn)})
    return sorted(out, key=lambda r: r["rel_path"])


# ── STAGE 0 — the PARSER (deterministic structural facts) ──
_LANG_BY_EXT = {".py": "python", ".js": "javascript", ".mjs": "javascript", ".ts": "typescript",
               ".tsx": "typescript", ".jsx": "javascript", ".md": "markdown", ".json": "json",
               ".html": "html", ".css": "css", ".sh": "shell", ".sql": "sql", ".yaml": "yaml",
               ".yml": "yaml", ".toml": "toml"}
_REGISTRY_SENTINELS = {"ROLE": "role", "PROJECTION": "projection", "MARK_TYPE": "mark_type",
                      "NODE_TYPE": "node_type", "DECISION": "decision", "PANEL": "panel", "FLOW": "flow",
                      "SKILL": "skill", "CONTEXT": "context", "ITEM_TYPE": "item_type"}
_TEST_RE = re.compile(r"(^|/)(tests?|test_|.*_test)\b", re.I)
_JS_IMPORT_RE = re.compile(r"""^\s*import\b.*?from\s+['"]([^'"]+)['"]|^\s*(?:const|let|var)\s+.*=\s*require\(['"]([^'"]+)['"]\)""", re.M)
_JS_EXPORT_RE = re.compile(r"^\s*export\s+(?:default\s+)?(?:async\s+)?(?:function|class|const|let|var)\s+([A-Za-z0-9_$]+)", re.M)


def _kind(rel_path: str, language: str, has_symbols: bool) -> str:
    if _TEST_RE.search(rel_path):
        return "test"
    if language == "markdown":
        return "doc"
    if language == "json" or language in ("yaml", "toml"):
        return "config" if re.search(r"config|manifest|package|tsconfig|\.json$", rel_path, re.I) else "data"
    if language == "shell":
        return "script"
    if language in ("python", "javascript", "typescript"):
        return "module" if has_symbols else "script"
    if language in ("html", "css"):
        return "asset"
    return "other"


def parse_python(src: str) -> dict:
    """Exact structural facts via the ast — defs/classes (top_symbols), imports, declares (registry-rows)."""
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return {"top_symbols": [], "imports": [], "declares": [], "parse_error": "python ast parse failed"}
    syms, imps, decls = [], [], []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            syms.append({"name": node.name, "kind": "function"})
        elif isinstance(node, ast.ClassDef):
            syms.append({"name": node.name, "kind": "class"})
        elif isinstance(node, ast.Import):
            imps += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            imps.append(node.module or ".")
        elif isinstance(node, ast.Assign):                          # module-level registry-row sentinel?
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in _REGISTRY_SENTINELS:
                    decls.append({"sentinel": t.id, "registry": _REGISTRY_SENTINELS[t.id]})
    return {"top_symbols": syms, "imports": sorted(set(imps)), "declares": decls}


def parse_generic(language: str, src: str) -> dict:
    """Best-effort structural facts for non-python: regex imports/exports (JS/TS), keys (JSON)."""
    syms, imps, decls = [], [], []
    if language in ("javascript", "typescript"):
        for m in _JS_IMPORT_RE.finditer(src):
            imps.append(m.group(1) or m.group(2))
        syms = [{"name": n, "kind": "export"} for n in _JS_EXPORT_RE.findall(src)]
    elif language == "json":
        try:
            obj = json.loads(src)
            if isinstance(obj, dict):
                syms = [{"name": k, "kind": "key"} for k in list(obj.keys())[:60]]
        except (json.JSONDecodeError, ValueError):
            pass
    return {"top_symbols": syms, "imports": sorted(set(i for i in imps if i)), "declares": decls}


def parse_file(rec: dict) -> dict | None:
    """STAGE 0 — read + structurally parse ONE file. Returns the skeleton, or None if unreadable (binary)."""
    abs_path, rel = rec["abs_path"], rec["rel_path"]
    ext = os.path.splitext(rel)[1].lower()
    base = os.path.basename(rel).lower()
    # ★ SECURITY exclusion FIRST — never describe/embed a secret/credential/key (the git-ignored-include edge)
    if ext in _SENSITIVE_EXT or base.startswith(".env") or base == ".secrets" \
            or any(h in base for h in _SENSITIVE_HINT):
        return {"_excluded": "sensitive"}
    if ext in _BINARY_EXT:
        return {"_excluded": "binary-ext"}
    if ext == ".log":
        return {"_excluded": "log-noise"}
    try:
        with open(abs_path, "rb") as fh:
            raw = fh.read()
        if b"\x00" in raw[:4096]:                                   # NUL byte → binary
            return {"_excluded": "binary-content"}
        src = raw.decode("utf-8", errors="replace")
    except (OSError, UnicodeDecodeError) as e:
        return {"_excluded": f"unreadable:{type(e).__name__}"}
    language = _LANG_BY_EXT.get(ext, "other")
    fp = hashlib.sha256(raw).hexdigest()
    loc = src.count("\n") + 1
    if language == "python":
        st = parse_python(src)
    elif language in ("javascript", "typescript", "json"):
        st = parse_generic(language, src)
    else:
        st = {"top_symbols": [], "imports": [], "declares": []}
    kind = _kind(rel, language, bool(st.get("top_symbols")))
    return {"rel_path": rel, "language": language, "kind": kind, "loc": loc, "fingerprint": fp,
            "top_symbols": st["top_symbols"], "imports": st["imports"], "declares": st["declares"],
            "_src_head": src[:2600], "_parse_error": st.get("parse_error"),
            "_n_symbols": len(st["top_symbols"])}


# ── the LLM legs (parser-first: the LLM does ONLY prose) — reuse cog.run_items ──
class CoarseOut(BaseModel):
    what_it_is: str            # one neutral phrase: what this file IS (describe, don't judge)

class FineOut(BaseModel):
    summary: str               # 1-2 sentence neutral summary of what the file does
    registry_touchpoints: List[str]   # "registers a role via ROLE" / "writes FsStore" — descriptive, [] if none
    cross_refs: List[str]      # other files/modules it depends on or is depended on by (from imports), [] if none


def _coarse_role():
    from runtime.roles import Role
    return Role(id="code_coarse", spec={}, prompt_template=(
        "You describe a source file NEUTRALLY (what it IS — do NOT judge quality or relevance). You are given "
        "its path, language, and a head excerpt.\n{utterance}\n\n"
        "Return ONLY JSON: {\"what_it_is\": \"what this file is, in one plain phrase\"}"
    ), output_schema=CoarseOut)


def _fine_role():
    from runtime.roles import Role
    return Role(id="code_fine", spec={}, prompt_template=(
        "Describe this code-bearing file's role NEUTRALLY (only what it does). You are given its path, its "
        "PARSED symbols/imports, and a head excerpt.\n{utterance}\n\n"
        "Return ONLY JSON: {\"summary\": \"1-2 sentence neutral summary\", "
        "\"registry_touchpoints\": [\"descriptive, e.g. 'registers a role' / 'writes the store' — [] if none\"], "
        "\"cross_refs\": [\"key modules/files it depends on — [] if none\"]}"
    ), output_schema=FineOut)


def _coarse_unit(sk: dict) -> str:
    sym = ", ".join(s["name"] for s in sk["top_symbols"][:30])
    return (f"path: {sk['rel_path']}\nlanguage: {sk['language']}  kind: {sk['kind']}  loc: {sk['loc']}\n"
            f"symbols: {sym or '(none)'}\nhead:\n{sk['_src_head']}")


def _fine_unit(sk: dict) -> str:
    sym = ", ".join(f"{s['name']}({s['kind']})" for s in sk["top_symbols"][:40])
    imp = ", ".join(sk["imports"][:30])
    decl = ", ".join(d["registry"] for d in sk["declares"])
    return (f"path: {sk['rel_path']}\nlanguage: {sk['language']}\nsymbols: {sym or '(none)'}\n"
            f"imports: {imp or '(none)'}\ndeclares: {decl or '(none)'}\nhead:\n{sk['_src_head']}")


def run_cascade(skeletons: list[dict], *, store, coarse_max=120, fine_max=400, label="m1"):
    """STAGE 1 coarse (all) → step-gate (code-bearing) → STAGE 2 fine (gated). Returns (records, stats).
    Reuses cog.run_items on the resident 4b @ :8000 (vLLM /v1 — non-reasoning, the lead's think=false-free)."""
    from runtime import cognition as cog
    t0 = time.time()
    c_res = cog.run_items(_coarse_role(), [_coarse_unit(s) for s in skeletons], store,
                          turn_id=f"codearch-coarse-{label}", max_tokens=coarse_max)
    coarse = {i: (v if isinstance(v, dict) else v.dict()) for i, v in c_res.resolved.items()}
    t_coarse = time.time() - t0
    gated = [i for i, s in enumerate(skeletons) if s["kind"] in _CODE_BEARING and s.get("_n_symbols")]
    t1 = time.time()
    fine = {}
    if gated:
        f_res = cog.run_items(_fine_role(), [_fine_unit(skeletons[i]) for i in gated], store,
                              turn_id=f"codearch-fine-{label}", max_tokens=fine_max)
        for pos, i in enumerate(gated):
            v = f_res.resolved.get(pos)
            if v is not None:
                fine[i] = v if isinstance(v, dict) else v.dict()
    t_fine = time.time() - t1
    records, failed_coarse = [], []
    for i, sk in enumerate(skeletons):
        cv = coarse.get(i)
        if cv is None:
            failed_coarse.append(sk["rel_path"]); continue
        rec = {k: sk[k] for k in ("rel_path", "language", "kind", "loc", "fingerprint",
                                  "top_symbols", "imports", "declares")}
        rec["what_it_is"] = cv.get("what_it_is", "")
        rec["grain"] = "fine" if i in fine else "coarse"
        if sk.get("_parse_error"):
            rec["parse_error"] = sk["_parse_error"]
        if i in fine:
            rec.update({k: fine[i].get(k) for k in ("summary", "registry_touchpoints", "cross_refs")})
        # the embeddable text (leads the serialized record — prose first for a meaningful vector)
        rec["text"] = (f"{sk['rel_path']} — {rec['what_it_is']} "
                       + (rec.get("summary", "") or "")).strip()
        records.append(rec)
    stats = {"n": len(skeletons), "coarse_ok": len(coarse), "coarse_failed": len(c_res.failed) + len(failed_coarse),
             "gated_to_fine": len(gated), "fine_ok": len(fine),
             "t_coarse_s": round(t_coarse, 1), "t_fine_s": round(t_fine, 1),
             "throughput_per_s": round(len(coarse) / t_coarse, 1) if t_coarse else 0,
             "failed_coarse_paths": failed_coarse}
    return records, stats


def code_address(project: str, rel_path: str) -> str:
    return f"code://{project}/{rel_path}"


# ── M2 — the FIELD-INDEX (registry/type DISCOVERABILITY): a SIBLING store (the marks-layer PATTERN — append-only
# jsonl + read-time linear scan — in its OWN namespace, NOT the shared marks.jsonl). Built from the DETERMINISTIC
# parser fields (declares/imports/kind/language/symbol), so it's a fast no-model pass (no cc_dragnet run-telemetry
# needed — it's an index, not an extraction). Answers the queries semantic search CAN'T: "all files declaring a
# role" · "all projections" · "all files importing fs_store" · "all modules". The elevation's core. ──
FIELD_INDEX = os.path.join(OUT_DIR, "field_index.jsonl")


def build_field_index(repo: str, project: str, *, include_gitignored=()) -> dict:
    """Enumerate + PARSE (deterministic, no model) → emit typed field-rows {target, field, value} → the sibling
    index. field ∈ {declares, imports, kind, language, symbol}. Returns counts."""
    files = enumerate_files(repo, include_gitignored=include_gitignored)
    rows, n_files, by_field = [], 0, {}
    for rec in files:
        sk = parse_file(rec)
        if sk is None or sk.get("_excluded"):
            continue
        n_files += 1
        target = code_address(project, sk["rel_path"])
        emit = [("kind", sk["kind"]), ("language", sk["language"])]
        emit += [("declares", d["registry"]) for d in sk["declares"]]
        emit += [("imports", im) for im in sk["imports"]]
        emit += [("symbol", s["name"]) for s in sk["top_symbols"][:40]]
        for field, value in emit:
            if value:
                rows.append({"target": target, "field": field, "value": value})
                by_field[field] = by_field.get(field, 0) + 1
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(FIELD_INDEX, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return {"files_indexed": n_files, "rows": len(rows), "by_field": by_field, "path": FIELD_INDEX}


def query_field_index(field: str, value: str, *, contains=False) -> list[str]:
    """Read-time linear scan (the marks-layer pattern) → the targets matching field==value (or value-substring
    if contains). registry-is-truth: scans the index file (no maintained secondary index — same as marks_by_type)."""
    if not os.path.exists(FIELD_INDEX):
        raise FileNotFoundError(f"no field index at {FIELD_INDEX} — run --field-index first")
    out = []
    for line in open(FIELD_INDEX):
        try:
            r = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        if r.get("field") != field:
            continue
        v = str(r.get("value") or "")
        if (value.lower() in v.lower()) if contains else (v == value):
            out.append(r["target"])
    return sorted(set(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=0, help="PROVE/MEASURE on N files (does NOT write the asset)")
    ap.add_argument("--all", action="store_true", help="the FULL M1 coverage run (needs --confirm)")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--project", default="company")
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--include-gitignored", default="", help="comma-sep git-ignored content dirs to force-include (design source/,reference/)")
    ap.add_argument("--coarse-max", type=int, default=120)
    ap.add_argument("--fine-max", type=int, default=400)
    ap.add_argument("--field-index", action="store_true", help="M2: build the registry-discoverability field-index (deterministic, no model)")
    ap.add_argument("--query", default="", help="M2: query the field-index FIELD=VALUE (declares=role · imports=fs_store · kind=module); ~VALUE = substring")
    a = ap.parse_args()

    if a.query:                                                   # M2 read — no Suite/model needed
        field, _, value = a.query.partition("=")
        contains = value.startswith("~")
        hits = query_field_index(field.strip(), value.lstrip("~").strip(), contains=contains)
        print(f"FIELD-QUERY [{a.query}] → {len(hits)} hits:")
        for h in hits[:60]:
            print(" ", h)
        if len(hits) > 60:
            print(f"  … +{len(hits)-60} more")
        return 0
    if a.field_index:                                            # M2 build — deterministic, no model
        incl = [p.strip() for p in a.include_gitignored.split(",") if p.strip()]
        res = build_field_index(a.repo, a.project, include_gitignored=incl)
        print("FIELD-INDEX BUILT:", json.dumps(res, indent=2))
        return 0

    if a.all and not a.confirm:
        print("FULL M1 is GATED. Run --sample N first to PROVE the pipeline, then --all --confirm.")
        return 2

    incl = [p.strip() for p in a.include_gitignored.split(",") if p.strip()]
    files = enumerate_files(a.repo, include_gitignored=incl)
    print(f"DENOMINATOR (real filesystem tree, junk-pruned): {len(files)} files  (force-included gitignored: {incl or 'none'})")
    if a.sample:
        files = files[:: max(1, len(files) // a.sample)][:a.sample]
        print(f"  → sampling {len(files)} for the proof")

    from store.fs_store import FsStore
    from fabric import config as fcfg
    from runtime.registry import NodeRegistry
    from runtime.suite import Suite
    store = FsStore(fcfg.STORE_DIR)
    suite = Suite(store, NodeRegistry().discover([os.path.join(REPO, "nodes")]), nodes_dir=os.path.join(REPO, "nodes"))
    # fail-loud: the space must be registered (embed_corpus_to_spaces raises otherwise)
    spaces = [p.id for p in suite.projection_registry.embeddable()]
    assert "code_archaeology" in spaces, f"code_archaeology not a registered embeddable space — got {spaces}"

    # STAGE 0 — parse all; partition excluded
    skeletons, ledger, excluded = [], [], []
    for rec in files:
        sk = parse_file(rec)
        if sk is None or sk.get("_excluded"):
            reason = (sk or {}).get("_excluded", "unreadable")
            excluded.append(rec["rel_path"])
            ledger.append({"rel_path": rec["rel_path"], "state": "excluded", "reason": reason,
                           "record_address": None, "fingerprint": None, "ts": _ts()})
        else:
            skeletons.append(sk)
    print(f"STAGE 0 parser: {len(skeletons)} readable · {len(excluded)} excluded")

    # STAGE 1+2 — the cascade
    records, stats = run_cascade(skeletons, store=store, coarse_max=a.coarse_max, fine_max=a.fine_max,
                                 label=("sample" if a.sample else "m1"))
    print("CASCADE STATS:", json.dumps({k: v for k, v in stats.items() if k != "failed_coarse_paths"}, indent=2))

    if a.sample and not a.all:
        print(f"\nSAMPLE PROOF: {len(records)} records (grain fine={sum(1 for r in records if r['grain']=='fine')}). "
              f"NOT written (sample). Example record:")
        if records:
            ex = dict(records[0]); ex["top_symbols"] = ex["top_symbols"][:5]
            print(json.dumps(ex, indent=2)[:1400])
        return 0

    # CAPTURE + EMBED — write each record at code://<project>/<rel_path> into the code_archaeology space
    # the serialized output IS the embed text (_embed_text key-sorts the whole dict) → carry ONLY semantic
    # content. Drop the 64-char `fingerprint` (pure hex noise in a semantic space; the LEDGER keeps it for the
    # incremental sha-diff) and the redundant `text` scratch field (its prose is already in what_it_is/summary).
    cap_recs = [{"source_address": code_address(a.project, r["rel_path"]),
                 "output": {k: v for k, v in r.items() if k not in ("fingerprint", "text")},
                 "projection": "code_archaeology"} for r in records]
    by_path = {r["rel_path"]: r for r in records}
    done_addrs = {}
    BATCH = 200
    for bi in range(0, len(cap_recs), BATCH):
        res = suite.capture_corpus(cap_recs[bi:bi + BATCH], project=a.project, session="code-archaeology", round="m1")
        for c in res["captured"]:
            done_addrs[c["source_address"]] = c["address"]
        print(f"  captured {bi}-{bi+len(cap_recs[bi:bi+BATCH])} (embedded: {bool(res.get('embedded'))})", flush=True)

    # LEDGER — per-file state; FAIL-LOUD: denominator == Σ states
    for r in records:
        addr = code_address(a.project, r["rel_path"])
        ledger.append({"rel_path": r["rel_path"], "state": "done", "reason": r["grain"],
                       "record_address": done_addrs.get(addr, addr), "fingerprint": r["fingerprint"], "ts": _ts()})
    for p in stats["failed_coarse_paths"]:
        ledger.append({"rel_path": p, "state": "failed", "reason": "coarse-llm-failed",
                       "record_address": None, "fingerprint": by_path.get(p, {}).get("fingerprint"), "ts": _ts()})

    denominator = len(files)
    states = {}
    for row in ledger:
        states[row["state"]] = states.get(row["state"], 0) + 1
    accounted = sum(states.values())
    excluded_n = states.get("excluded", 0)
    done_n = states.get("done", 0)
    coverage = round(100.0 * done_n / (denominator - excluded_n), 2) if (denominator - excluded_n) else 0.0

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "ledger.jsonl"), "w") as f:
        for row in ledger:
            f.write(json.dumps(row) + "\n")

    summary = {"denominator": denominator, "accounted": accounted, "states": states,
               "coverage_pct": coverage, "project": a.project, "ts": _ts(),
               "fail_loud_ok": (accounted == denominator)}
    # the ledger as an addressable corpus record (capture-only, readable via corpus op=read)
    suite.capture_corpus([{"source_address": code_address(a.project, "_ledger"), "output": summary}],
                         project=a.project, session="code-archaeology", round="m1")
    print("\nLEDGER SUMMARY:", json.dumps(summary, indent=2))
    if accounted != denominator:
        raise SystemExit(f"FAIL-LOUD: denominator {denominator} != Σ states {accounted} — {denominator-accounted} files unaccounted!")
    print(f"\n✅ M1 COVERAGE PROOF: {done_n} done + {excluded_n} excluded = {accounted}/{denominator} accounted "
          f"({coverage}% of non-excluded). Ledger: {os.path.join(OUT_DIR,'ledger.jsonl')} + code://{a.project}/_ledger")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
