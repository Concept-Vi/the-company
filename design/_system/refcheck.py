"""refcheck.py — the code-reference drift validator (no models, free, deterministic). Run:
    python3 refcheck.py
Layer-0 of the corpus-analysis mechanisms (see _system/mechanisms.json): the traceability
refs DRIFT as the real app grows — a `code:` ref that once pointed at the right `def` now
lands in unrelated plumbing. This pass reads EVERY `code` value from register.json
(features[].code) AND addresses.json (addresses.*.code), resolves each against the real
source under ~/company (READ-ONLY), and reports where a ref no longer lands on/near the
symbol the corpus claims it represents. It does NOT repair anything — it emits the lead's
repair worklist (refcheck-report.json) + a printed summary.

Refs come in several FORMS; each is handled, none is silently skipped:
  • file:line / path/file:line  → resolve the file under ~/company, confirm the line exists,
      capture the nearest preceding `def `/`class ` (.py) and a context window; flag DRIFT
      if a sibling-derived expected symbol isn't found near the line, OR the line isn't within
      a small window after a def/class. Prefer reporting "points at <symbol>" over hard fail.
  • /api/...                     → grep bridge.py for the route literal; missing = drift.
  • Suite.verb / bare symbol     → grep the resolved/likely source for a matching def/class; missing = drift.
  • unrecognised (glob, css selector, un-resolvable file) → unverifiable-form (NOT drift).
Compound refs (' / ' and ' + ' separated) are split and each sub-ref validated independently.
Fails LOUD on a malformed registry; never silently drops a ref.

The model layer extends this later: today = "line exists + sits near a def"; LATER (free local
AI) = a model reads the code at the ref + the corpus `represents` claim and judges whether the
symbol actually IMPLEMENTS what the corpus says (semantic match, not just structural)."""
import os, re, json, subprocess

# the code dirs to search a bare/relative ref against, under ~/company (READ-ONLY).
COMPANY = os.path.expanduser("~/company")
SEARCH_DIRS = ["", "runtime", "nodes", "store", "contracts", "canvas/app/src", "voice"]
WINDOW = 25  # a ref line ≤ WINDOW lines after its def/class counts as "on" that symbol.

# python def/class extractor (captures the symbol name); used for nearest-preceding + ref-line.
_PYDEF = re.compile(r'^\s*(?:async\s+)?(?:def|class)\s+([A-Za-z_]\w*)')
# tsx-ish symbol extractor — we do NOT parse TSX, only report the nearest declaration line.
_TSXDEF = re.compile(r'^\s*(?:export\s+)?(?:async\s+)?(?:function|const|class|let|var)\s+([A-Za-z_$][\w$]*)')
# a `file[:line]` head at the start of a ref (path may contain '/'), tolerating a trailing annotation.
_HEAD = re.compile(r'^([\w./-]+\.\w+)(?::(\d+))?')


def split_refs(ref: str) -> list:
    """A `code` value may pack several refs joined by ' / ' or ' + ' (spaces required, so a bare
    '/' inside a path is NOT a split point). Returns the list of trimmed sub-refs (>=1)."""
    parts = re.split(r'\s+/\s+|\s+\+\s+', ref.strip())
    return [p.strip() for p in parts if p.strip()]


def parse_ref(ref: str):
    """Pull the leading `file[:line]` out of a sub-ref, tolerating annotations.
    'App.tsx (toolbar)'        -> ('App.tsx', None, '(toolbar)')
    'App.tsx NodeShapeUtil:124'-> ('App.tsx', 124, 'NodeShapeUtil:124')   (leading file wins; line is the LAST :N)
    'suite.py:577'             -> ('suite.py', 577, '')
    Returns (file_or_None, line_or_None, remainder_hint)."""
    m = _HEAD.match(ref.strip())
    if not m:
        return (None, None, ref.strip())
    f = m.group(1)
    line = int(m.group(2)) if m.group(2) else None
    rest = ref.strip()[m.end():].strip()
    # 'App.tsx NodeShapeUtil:124' — head matched only 'App.tsx'; recover a trailing :N from the rest.
    if line is None and rest:
        m2 = re.search(r':(\d+)\s*$', rest)
        if m2:
            line = int(m2.group(1))
    return (f, line, rest)


def _resolve(path: str):
    """Resolve a (possibly relative) source path under ~/company across SEARCH_DIRS, READ-ONLY.
    Returns (repo-relative-path, [lines]) or None if not found / not a real file."""
    cand = os.path.basename(path) if "/" not in path else path
    tried = []
    for d in SEARCH_DIRS:
        full = os.path.join(COMPANY, d, cand) if d else os.path.join(COMPANY, cand)
        tried.append(full)
        if os.path.isfile(full):
            with open(full, encoding="utf-8", errors="replace") as fh:
                return (os.path.relpath(full, COMPANY), fh.read().splitlines())
    # path may already be repo-relative (e.g. 'canvas/app/src/App.tsx')
    full = os.path.join(COMPANY, path)
    if os.path.isfile(full):
        with open(full, encoding="utf-8", errors="replace") as fh:
            return (os.path.relpath(full, COMPANY), fh.read().splitlines())
    return None


def _nearest_def(lines: list, idx0: int):
    """Walk UP from 0-based line idx0 to the nearest def/class (py) or declaration (tsx-ish).
    Returns (symbol_name, def_line_1based, distance) or (None, None, None)."""
    for i in range(idx0, -1, -1):
        m = _PYDEF.match(lines[i]) or _TSXDEF.match(lines[i])
        if m:
            return (m.group(1), i + 1, idx0 - i)
    return (None, None, None)


def _all_defs(lines: list) -> dict:
    """Every def/class (and tsx declaration) in the file → {symbol_name: 1-based line}.
    First occurrence wins (the canonical definition site)."""
    out = {}
    for i, ln in enumerate(lines):
        m = _PYDEF.match(ln) or _TSXDEF.match(ln)
        if m and m.group(1) not in out:
            out[m.group(1)] = i + 1
    return out


def _candidate_match(candidates, defs: dict, landed_symbol, ref_line=None):
    """Does any candidate name a def/class in this file that is NOT the symbol the ref landed on?
    Match is exact OR the candidate is a token within a def name (e.g. 'resolve' ⊂ 'resolve_surfaced',
    'replay' == 'replay'). Returns (matched_def_name, def_line) of the BEST elsewhere-target, or None.
    A candidate that equals/relates to the LANDED symbol is treated as 'already correct', not a target.
    Ranking, best first: (a) exact name match; then (b) — when a ref_line is given — the candidate def
    NEAREST the original ref line (a drifted ref usually moved a little, not across the file)."""
    landed = (landed_symbol or "").lower()
    # ALREADY-CORRECT guard: if the symbol the ref lands on relates to ANY candidate (exact, token,
    # or substring either way — 'cap'⊂'capabilities'), the ref is on a right-named symbol → not a
    # relocation. (Without this, a SECONDARY label-token like 'object_info' would wrongly relocate a
    # ref that already sits on its primary symbol 'capabilities'.)
    for cand in (candidates or []):
        c = cand.lower()
        if not c or len(c) < 3 or not landed:
            continue
        toks = re.split(r'[_]|(?<=[a-z])(?=[A-Z])', landed_symbol or "")
        tokset = {t.lower() for t in toks if t}
        if c == landed or c in tokset or c in landed or landed in c:
            return None
    matches = []                                              # (is_exact, name, lineno)
    for cand in (candidates or []):
        c = cand.lower()
        if not c or len(c) < 3:
            continue
        for name, lineno in defs.items():
            nl = name.lower()
            toks = re.split(r'[_]|(?<=[a-z])(?=[A-Z])', name)
            tokset = {t.lower() for t in toks if t}
            related = (c == nl) or (c in tokset)
            if not related:
                continue
            # if this def IS where the ref landed, the ref is already on its symbol — not a relocation.
            if nl == landed or c == landed or (landed and (c in landed or landed in c)):
                return None
            matches.append((c == nl, name, lineno))
    if not matches:
        return None
    # exact matches win; then nearest to the original ref line (if known); then earliest.
    def rank(m):
        is_exact, _name, lineno = m
        prox = abs(lineno - ref_line) if ref_line else lineno
        return (0 if is_exact else 1, prox)
    best = min(matches, key=rank)
    return (best[1], best[2])


def check_api_route(route: str, bridge_lines: list) -> dict:
    """/api/... → present as a literal anywhere in bridge.py text = ok; absent = drift."""
    hit = any(route in ln for ln in bridge_lines)
    return {"status": "ok" if hit else "drift",
            "points_at": (f"route literal {route!r} found in bridge.py" if hit
                          else f"route literal {route!r} NOT in bridge.py")}


def check_symbol(sym: str, lines: list) -> dict:
    """Suite.verb / bare symbol → a matching `def <verb>`/`class <verb>`/registration in the source.
    Takes the last dotted segment as the symbol; found = ok, absent = drift."""
    name = sym.split(".")[-1].strip()
    pat = re.compile(r'\b(?:def|class)\s+' + re.escape(name) + r'\b')
    bare = re.compile(r'\b' + re.escape(name) + r'\b')
    hit = any(pat.search(ln) for ln in lines) or any(bare.search(ln) for ln in lines)
    return {"status": "ok" if hit else "drift",
            "points_at": (f"symbol {name!r} present" if hit else f"symbol {name!r} not found")}


def check_ref(ref: str, candidates=None, resolve=_resolve, _window=WINDOW) -> dict:
    """Validate ONE sub-ref against the real source. Returns {status: ok|drift|unverifiable, ...}.
    `candidates` = symbol names this ref plausibly SHOULD land on (from the owner id-suffix + the
    snake/camel tokens in its label). The verdict is CONSERVATIVE — we hard-flag drift ONLY on
    confident signals and otherwise report `points_at` and PASS (semantic judgement is the model
    layer's job). Verdict order:
      1. line missing / past EOF                                  → drift (high)
      2. line not within `_window` of ANY def/class               → drift (high; structural orphan)
      3. RELOCATION: a candidate names a def/class ELSEWHERE in the file (not where the ref lands)
         → drift (review) + `repair_target` = that def's line
      4. otherwise                                                → ok (report points_at)"""
    f, line, hint = parse_ref(ref)
    # unrecognised form: a glob, a bare symbol with no file, a css selector, etc. -> not a file:line.
    if not f or "*" in ref or ("." not in (f or "")):
        return {"status": "unverifiable", "points_at": "no resolvable file:line form"}
    res = resolve(f)
    if res is None:
        # the file isn't under company's code dirs (e.g. design-system.css) -> unverifiable, NOT drift.
        return {"status": "unverifiable", "points_at": f"file {f!r} not found under ~/company code dirs"}
    resolved_path, lines = res
    defs = _all_defs(lines)
    # only identifier-shaped candidates can name a symbol (a ui:// id or feature-id like 'RHM-modes' can't).
    cands = [c for c in (candidates or []) if re.fullmatch(r'[A-Za-z_]\w*', c or "")]
    if line is None:
        # file-only ref (e.g. nodes/embed.py) — the file exists. If a real candidate is defined here,
        # point at it; otherwise just confirm the file (NEVER 'defines none of' — too aggressive: a
        # file legitimately hosts many symbols, and our candidate guess may simply be wrong).
        hit = _candidate_match(cands, defs, None)
        if hit:
            return {"status": "ok", "resolved": resolved_path,
                    "points_at": f"file {resolved_path} exists; defines {hit[0]} @ line {hit[1]}"}
        return {"status": "ok", "resolved": resolved_path,
                "points_at": f"file {resolved_path} exists (no line given)"}
    if line < 1 or line > len(lines):
        # (1) line doesn't exist — the high-confidence signal (often a file-churned/shrunk ref).
        #     Still try a relocation target so the lead has somewhere to repair TO.
        out = {"status": "drift", "severity": "high", "resolved": resolved_path,
               "points_at": f"line {line} does not exist ({len(lines)} lines)"}
        target = _candidate_match(cands, defs, None, ref_line=line)
        if target:
            out["repair_target"] = f"{target[0]} @ line {target[1]}"
        return out
    idx0 = line - 1
    sym, defline, dist = _nearest_def(lines, idx0)
    content = lines[idx0].strip()
    points_at = (f"{sym} (def @ line {defline}, +{dist})" if sym else f"line content: {content!r}")
    out = {"resolved": resolved_path, "line_content": content, "points_at": points_at, "candidates": cands}
    # (2) relocation: a candidate symbol is DEFINED elsewhere in this file, not where the ref lands.
    #     This is the second confident signal (a def moved; we can name the repair target).
    target = _candidate_match(cands, defs, sym, ref_line=line)
    if target:
        out["status"] = "drift"
        out["severity"] = "review"
        out["repair_target"] = f"{target[0]} @ line {target[1]}"
        out["points_at"] = points_at + f"  [candidate {target[0]} is defined at line {target[1]}]"
        return out
    # (3) beyond-window / no enclosing def — a SOFT review (deep in a long function is legitimate;
    #     we surface 'verify intended' rather than assert drift). Reserve HIGH for past-EOF only.
    if sym is None or dist is None or dist > _window:
        out["status"] = "drift"
        out["severity"] = "review"
        out["points_at"] = points_at + " (deep in body / beyond window — verify the ref still intends this)"
        return out
    # (4) lands on/near a def, no better-named target found → OK (semantic judgement is the model layer's job).
    out["status"] = "ok"
    return out


def _candidates_for(owner_id: str, label: str) -> list:
    """Plausible symbol names the ref should land on — for the RELOCATION check ONLY (a candidate
    only drives a drift verdict if it actually names a def elsewhere in the file, so noisy guesses
    are harmless — they simply don't match). Sources, in order:
      • the owner id-suffix after the last '-'  (INB-resolve→'resolve', WIRE-dispatch→'dispatch')
      • snake_case / camelCase identifier tokens quoted-or-bare in the label
        (label 'present_current + ui_target framing' → 'present_current', 'ui_target')."""
    cands = []
    # id-suffix: 'INB-resolve' → 'resolve'. Only if it's identifier-shaped (a 'ui://...' address id
    # or a feature-id token like 'F1' won't be a symbol — those are filtered below + in check_ref).
    if owner_id and "-" in owner_id:
        cands.append(owner_id.rsplit("-", 1)[1])
    elif owner_id:
        cands.append(owner_id)
    # snake_case / camelCase identifiers named in the label (real symbol names show up verbatim).
    for m in re.finditer(r'\b([a-z][a-z0-9]*_[a-z0-9_]+|[a-z]+[A-Z]\w+)\b', label or ""):
        cands.append(m.group(1))
    # de-dupe, keep order, drop trivially-short and non-identifier-shaped (no '/', ':', '*').
    seen, out = set(), []
    for c in cands:
        cl = c.lower()
        if len(cl) >= 3 and cl not in seen and re.fullmatch(r'[a-z_]\w*', cl):
            seen.add(cl)
            out.append(c)
    return out


def collect_refs(register: dict, addresses: dict) -> list:
    """Every code ref from features[].code (register) + addresses.*.code (addresses), each as
    {raw, source, owner, label}. Fails LOUD if either registry is malformed."""
    items = []
    feats = register.get("features")
    if not isinstance(feats, list):
        raise ValueError("register.json malformed: 'features' is not a list")
    for f in feats:
        if "code" not in f or "id" not in f:
            raise ValueError(f"register.json feature missing id/code: {f!r}")
        items.append({"raw": f["code"], "source": "register", "owner": f["id"], "label": f.get("label", "")})
    if not isinstance(addresses, dict):
        raise ValueError("addresses.json malformed: 'addresses' is not a dict")
    for addr, spec in addresses.items():
        if not isinstance(spec, dict) or "code" not in spec:
            raise ValueError(f"addresses.json entry missing code: {addr!r} -> {spec!r}")
        items.append({"raw": spec["code"], "source": "addresses", "owner": addr,
                      "label": spec.get("represents", "")})
    return items


def run_corpus():
    """Validate every ref in the real corpus; write refcheck-report.json; return the report."""
    here = os.path.dirname(os.path.abspath(__file__))
    design = os.path.dirname(here)
    register = json.load(open(os.path.join(design, "register.json"), encoding="utf-8"))
    addr_doc = json.load(open(os.path.join(here, "addresses.json"), encoding="utf-8"))
    addresses = addr_doc.get("addresses", addr_doc)

    bridge_res = _resolve("bridge.py")
    bridge_lines = bridge_res[1] if bridge_res else []

    # ~/company is under an active cron build — pin the snapshot this report was computed against,
    # so line numbers are interpretable (a ref's line N is meaningful only against a known revision).
    try:
        snapshot = subprocess.check_output(
            ["git", "-C", COMPANY, "log", "-1", "--format=%H %ci"], text=True).strip()
    except Exception as e:                                    # READ-ONLY; never fail the run on this.
        snapshot = f"unknown ({e})"

    items = collect_refs(register, addresses)
    checked = 0
    ok, drift, unverifiable = [], [], []
    for it in items:
        cands = _candidates_for(it["owner"], it["label"])
        for sub in split_refs(it["raw"]):
            checked += 1
            if sub.startswith("/api/"):
                r = check_api_route(sub, bridge_lines)
            elif "*" in sub or sub.endswith("/") or "." not in sub.split()[0]:
                # a glob (nodes/*.py), a directory (voice/), or a token with no file extension →
                # unrecognised form → unverifiable, NEVER drift, NEVER a bogus symbol grep (the task
                # forbids silently skipping; we classify it honestly instead).
                r = {"status": "unverifiable", "points_at": f"unrecognised form (glob/dir/no file:line): {sub!r}"}
            elif re.fullmatch(r'[A-Z]\w*\.\w+', sub):
                # Suite.verb form (Capitalised.method, no path) — grep the API face for the verb.
                # (Not a file: 'Suite.run' must NOT be read as a file named 'Suite.run'.)
                r = check_symbol(sub, bridge_lines)
            else:
                f, line, _ = parse_ref(sub)
                # a bare symbol (no file, but dotted) → symbol grep against bridge.py.
                if f is None:
                    r = check_symbol(sub, bridge_lines)
                else:
                    r = check_ref(sub, candidates=cands)
            rec = {"ref": sub, "full_code": it["raw"], "source": it["source"], "owner": it["owner"],
                   "represents": it["label"], "candidates": cands, "points_at": r.get("points_at"),
                   "resolved": r.get("resolved"), "line_content": r.get("line_content"),
                   "repair_target": r.get("repair_target")}
            if r["status"] == "ok":
                ok.append(rec)
            elif r["status"] == "drift":
                rec["severity"] = r.get("severity", "review")
                drift.append(rec)
            else:
                unverifiable.append(rec)

    report = {
        "_what": "Drift findings for every code: ref in register.json (features[].code) + addresses.json "
                 "(addresses.*.code). Produced by _system/refcheck.py (read ~/company READ-ONLY). "
                 "drift[] is the lead's repair worklist; the lead repairs the registries centrally. "
                 "'points_at' = what the ref now lands on; 'expected' = the symbol hint derived from the "
                 "owner's label. NOTE: represents[] in views[] are feature-ids, not code refs — code refs "
                 "live in features[].code, so THAT is what this validates (see report (d)).",
        "snapshot": f"~/company @ {snapshot} — line numbers are as-of this revision (the repo is "
                    "under an active build loop; re-run after the registries are repaired).",
        "checked": checked, "ok": ok, "drift": drift, "unverifiable": unverifiable,
        "summary": {"checked": checked, "ok": len(ok), "drift": len(drift),
                    "unverifiable": len(unverifiable)},
    }
    out = os.path.join(here, "refcheck-report.json")
    json.dump(report, open(out, "w", encoding="utf-8"), indent=2)
    s = report["summary"]
    print("refcheck (code-ref drift) — summary:")
    for k, v in s.items():
        print(f"  {k}: {v}")
    if drift:
        print("  → DRIFT (repair worklist):")
        for d in drift:
            tgt = f"  ⇒ repair to: {d['repair_target']}" if d.get("repair_target") else ""
            print(f"    [{d['source']}·{d.get('severity')}] {d['owner']} :: {d['ref']}  →  {d['points_at']}{tgt}")
    if unverifiable:
        print("  → unverifiable-form (not drift):",
              ", ".join(f"{u['owner']}:{u['ref']}" for u in unverifiable))
    return report


def main():
    run_corpus()


if __name__ == "__main__":
    main()
