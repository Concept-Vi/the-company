"""coherence_detect — structural coherence detectors (AST-grounded, model-free).

The trustworthy STRUCTURAL half of the coherence substrate (round 1). Everything here is exact,
deterministic, cheap, and needs no model — it reads the AST + the registries, never guesses. The fuzzy
SEMANTIC half (the 4B swarm) is a separate layer that ADJUDICATES candidates these detectors find; nothing
here calls a model.

Discipline (from the detection-rigor research): static analysis may OVER-call dead (the safe direction —
a false orphan is caught downstream); it must never silently DECLARE something wired that is dead (the
dangerous false-wire direction — a dead thing reading as whole). So the consumer check below removes the two
measured false-wire sources (comments + existence-assertions) without introducing false-orphans: it only
ever EXCLUDES comment/assertion mentions, never invents a consumer.
"""
from __future__ import annotations

import ast
import glob
import os
import re


# ── route extraction (the MAP side: what /api routes the bridge actually serves) ─────────────────────
def extract_routes(bridge_src: str) -> set[str]:
    """AST-extract every `/api/...` route literal that is actually IN A ROUTING DECISION — a string that is
    an operand of a `self.path == "..."` comparison or a `self.path in ("...", ...)` membership. This is
    structurally immune to the regex's latent bug (a route mentioned in a comment/docstring is NOT in a
    comparison node, so it is never counted). Falls back to the regex set ONLY to UNION (never to shrink),
    so we can't miss a route the AST walk doesn't recognise."""
    routes: set[str] = set()
    try:
        tree = ast.parse(bridge_src)
    except SyntaxError:
        tree = None
    if tree is not None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                # self.path == "/api/..."  OR  self.path in ("/api/...", ...)
                for comp in node.comparators:
                    for lit in _string_consts(comp):
                        if lit.startswith("/api/"):
                            routes.add(lit)
    # UNION the regex routes (never shrink) — so an unusual routing form the AST misses is still counted.
    routes |= set(re.findall(r'"(/api/[a-zA-Z0-9_\-/]+)"', bridge_src))
    return routes


def _string_consts(node: ast.AST) -> list[str]:
    """Every string constant inside an expression node (a bare Constant, or the elts of a tuple/list/set)."""
    out: list[str] = []
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        out.append(node.value)
    elif isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        for e in node.elts:
            out.extend(_string_consts(e))
    return out


# ── consumer detection (is a route REALLY called, vs merely mentioned?) ──────────────────────────────
_CALL_MARKERS = ("fetch(", "eventsource(", "requests", ".post(", ".get(", ".put(", ".delete(",
                 "urlopen", "axios", "http")
_EXISTENCE_RE = re.compile(r"\bin\s+\w*(bridge|src|source|routes?)\w*", re.I)


def _strip_comments(text: str) -> str:
    """Remove the two measured false-wire sources so a route MENTIONED in a comment is not read as a caller:
    JS/TS `//…` + `/*…*/`, and Python `#…` line comments. Conservative (line-level): strips a `//`/`#`
    comment from the point it starts to end-of-line. Block comments removed whole. A route literal sitting
    BEFORE a trailing comment survives (it's real code); one INSIDE a comment is removed (it's a mention)."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)        # JS/TS block comments
    out_lines = []
    for line in text.splitlines():
        # cut a // or # comment (best-effort; a route is in "/api/…" double-quotes, rarely after a # in a string)
        for marker in ("//", "#"):
            idx = line.find(marker)
            if idx != -1:
                line = line[:idx]
        out_lines.append(line)
    return "\n".join(out_lines)


def route_is_wired(route: str, fe_text: str, test_text: str) -> bool:
    """A route is WIRED iff, in the COMMENT-STRIPPED corpus, it appears on a line that ALSO carries a real
    CALL marker (fetch( / EventSource( / requests / .post( / .get( …) and is not an existence-assertion.
    This is the positive signal that separates a real CONSUMER (a line that actually calls the route) from a
    MENTION (a comment, a docstring, a check()-label, a print string, or a `"/api/x" in bridge_src`
    existence test). The three measured false-wires were all mentions: a comment (mockup-feedback), an
    existence-assertion (scope), and prose-in-a-string (voice/turn). Requiring a call marker removes all
    three. The residual risk is the OTHER direction (a real consumer whose call the marker-scan misses → a
    false ORPHAN) — but a false orphan is the SAFE direction (it surfaces for cataloguing, never silently
    declares a dead route whole), and the live reclassification (verified by use) shows no real consumer is
    lost: every genuine fetch/EventSource/HTTP call carries a marker on its line."""
    for corpus in (fe_text, test_text):
        for line in corpus.splitlines():
            if route not in line or _EXISTENCE_RE.search(line):
                continue
            low = line.lower()
            if any(m in low for m in _CALL_MARKERS):
                return True
    return False


def route_reachability(repo_root: str) -> tuple[set[str], dict[str, bool]]:
    """Returns (all_routes, {route: wired_bool}) — AST-extracted routes, comment-stripped consumer check."""
    bridge = open(os.path.join(repo_root, "runtime", "bridge.py"), encoding="utf-8").read()
    routes = extract_routes(bridge)
    fe = "\n".join(open(f, errors="ignore").read()
                   for f in glob.glob(os.path.join(repo_root, "canvas/app/src/**/*.ts*"), recursive=True))
    _meta = ("reachability_acceptance.py", "suite_health_acceptance.py")
    tests = "\n".join(open(f, errors="ignore").read()
                      for f in glob.glob(os.path.join(repo_root, "tests", "*.py"))
                      if os.path.basename(f) not in _meta)
    fe, tests = _strip_comments(fe), _strip_comments(tests)
    return routes, {r: route_is_wired(r, fe, tests) for r in routes}


# ── #4a registry-vs-live (TRUSTWORTHY — gate-able): node files on disk vs the live registry ──────────
def registry_vs_live(repo_root: str, live_types: set[str]) -> dict:
    """Set-difference of the node-types DISCOVERABLE on disk (nodes/*.py declaring KIND + run()) vs the LIVE
    registry (`live_types`, from capabilities().node_types). A file on disk not live, or a live type with no
    file, is a real drift. Trustworthy (no model, no heuristic — two declared sets). Returns
    {on_disk, live, disk_not_live, live_not_disk, ok}."""
    # A node-type's identity is the MODULE FILENAME STEM (registry.discover registers `name`=stem for any
    # nodes/*.py with a run() attr — KIND is a category process|content, NOT the type name). So the disk set
    # is {stem : nodes/<stem>.py (non-_) defines run()}.
    on_disk: set[str] = set()
    nodes_dir = os.path.join(repo_root, "nodes")
    for f in glob.glob(os.path.join(nodes_dir, "*.py")):
        stem = os.path.basename(f)[:-3]
        if stem.startswith("_"):
            continue
        try:
            tree = ast.parse(open(f, errors="ignore").read())
        except SyntaxError:
            continue
        if any(isinstance(n, ast.FunctionDef) and n.name == "run" for n in ast.walk(tree)):
            on_disk.add(stem)
    disk_not_live = sorted(on_disk - live_types)
    live_not_disk = sorted(live_types - on_disk)
    return {"on_disk": sorted(on_disk), "live": sorted(live_types),
            "disk_not_live": disk_not_live, "live_not_disk": live_not_disk,
            "ok": not disk_not_live and not live_not_disk}


# ── #4b capability-with-no-consumer (CANDIDATE-only — positive-only, never auto-acted) ───────────────
def capability_no_consumer(repo_root: str) -> list[str]:
    """Public Suite methods reachable from NO face (bridge/MCP `SUITE.<m>(`) or test, even transitively via
    internal `self.<m>(` edges. CANDIDATE-only: dynamic dispatch (the RHM verb whitelist, the rules engine,
    getattr) is invisible to AST, so an unreached method may still be live — this PROPOSES, never declares.
    Returns the candidate method names (sorted)."""
    suite_src = open(os.path.join(repo_root, "runtime", "suite.py"), errors="ignore").read()
    tree = ast.parse(suite_src)
    # the Suite class + its method defs
    methods: dict[str, ast.FunctionDef] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Suite":
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods[item.name] = item
    public = {m for m in methods if not m.startswith("_")}
    # internal edges: method -> {self.<m> it calls}
    edges: dict[str, set[str]] = {}
    for name, fn in methods.items():
        called = set()
        for n in ast.walk(fn):
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and isinstance(n.func.value, ast.Name) and n.func.value.id == "self"):
                called.add(n.func.attr)
        edges[name] = called
    # entry points: methods named as SUITE.<m>( in the faces, or s.<m>(/.<m>( in tests
    # faces = the things that consume Suite methods: the HTTP bridge, the MCP face, AND the wire/loop
    # (implement.py) + cognition driver — all real callers. (Still CANDIDATE-only: dynamic dispatch via the
    # RHM verb whitelist / the rules engine / getattr is invisible to AST, so an unreached method may be live.)
    faces = ""
    for rel in ("runtime/bridge.py", "mcp_face/server.py", "runtime/implement.py", "runtime/cognition.py"):
        p = os.path.join(repo_root, rel)
        if os.path.exists(p):
            faces += open(p, errors="ignore").read()
    tests = "\n".join(open(f, errors="ignore").read()
                      for f in glob.glob(os.path.join(repo_root, "tests", "*.py")))
    # broad `.method(` over faces+tests (the faces call via SUITE./suite./self.; tests via s./instance.) —
    # inclusive on purpose: a method called any of those ways is a consumer; over-inclusion only SHRINKS the
    # candidate set, the safe direction for a positive-only detector that must not over-claim "unconsumed".
    called = set(re.findall(r"\.([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", faces + "\n" + tests))
    entry = called & set(methods)
    # reachability over internal edges from the entry set
    reached, stack = set(entry), list(entry)
    while stack:
        m = stack.pop()
        for nxt in edges.get(m, ()):
            if nxt in methods and nxt not in reached:
                reached.add(nxt); stack.append(nxt)
    return sorted(public - reached)


# ── C3 the reconcile + C5 the burn-down rollup (the finding MODEL — read-time folds over the store) ──
_ACCEPTED_DISPOSITIONS = ("by-design", "backend_only", "voice_owned")   # dispositioned-accepted ≠ open
_FINISH_DISPOSITIONS = ("to_wire", "to_build_ui")                       # open-finish (still the backlog)
_CLOSED_DISPOSITIONS = ("resolved",)


def _handle(f: dict) -> tuple:
    """The stable finding handle = (kind, address). Structural findings dedup on this; the reconcile and the
    rollup both key on it (own/reflect: a re-detection re-appends, the read folds to the distinct handle)."""
    return (f.get("kind"), f.get("address"))


def reconcile(current: list[dict], prior: list[dict]) -> dict:
    """The universal (kind,address) upsert — generalizes reachability's documented/new/stale to ANY detector.
    Given THIS run's findings (`current`) vs the PRIOR set (`prior`):
      known    = current ∩ prior   (the gap still stands — carry its disposition forward)
      new      = current − prior   (a fresh disconnection — surfaces, default-open)
      resolved = prior − current   (the detector no longer emits it — the gap closed; auto-close)
    Returns the three handle-lists (sorted) + net_change (|new|−|resolved|, the burn-down direction; a
    sustained net_change>0 over a window is the thrash signal). Pure — no store, no model."""
    cur = {_handle(f) for f in current}
    pri = {_handle(f) for f in prior}
    known = sorted(cur & pri)
    new = sorted(cur - pri)
    resolved = sorted(pri - cur)
    return {"known": known, "new": new, "resolved": resolved,
            "net_change": len(new) - len(resolved),
            "counts": {"known": len(known), "new": len(new), "resolved": len(resolved)}}


# C4 — the disposition policy: which dispositions an AGENT may set vs which ESCALATE to the operator.
_VALID_DISPOSITIONS = ("to_wire", "to_build_ui", "voice_owned", "backend_only", "defer", "resolved", "by-design")
_OPERATOR_ONLY_DISPOSITIONS = ("by-design",)   # permanently ACCEPTING a gap = a consequential operator decision


def dispose_finding(store, kind: str, address: str, disposition: str, *,
                    by: str = "", reason: str = "", confirmed: bool = False) -> dict:
    """C4 — set a finding's disposition under the consent policy. Findings live in their OWN agent-disposable
    lane (the dispositions overlay, NOT the operator inbox). Most dispositions are agent-settable (the loop
    burns the backlog down). `by-design` (permanently accepting a gap as fine) ESCALATES: an agent cannot
    self-accept a gap — without operator `confirmed`, it is NOT applied; it surfaces for the operator (the
    operator-only floor). Unknown dispositions fail loud. Returns {ok, applied, escalated, disposition}."""
    if disposition not in _VALID_DISPOSITIONS:
        return {"ok": False, "applied": False, "escalated": False,
                "error": f"unknown disposition {disposition!r} (valid: {_VALID_DISPOSITIONS})"}
    if disposition in _OPERATOR_ONLY_DISPOSITIONS and not confirmed:
        # escalate — surface for the operator, do NOT apply (the consent floor; never silently dropped)
        return {"ok": True, "applied": False, "escalated": True, "disposition": disposition,
                "note": "by-design accepts a gap permanently — operator confirmation required (escalated)"}
    store.append_disposition(kind, address, disposition, reason=reason, by=by)
    return {"ok": True, "applied": True, "escalated": False, "disposition": disposition}


def scan(repo_root: str, store=None) -> dict:
    """The on-demand coherence READ (the `company coherence` face). RE-DERIVES the model fresh (own/reflect:
    no maintained graph — detection is recomputed each call), recording the structural findings into `store`
    (a fresh temp store if none given) + folding the burn_down, and running the CANDIDATE detectors as a
    separate report (positive-only — proposed, never in the burn-down must-fix count). Returns
    {burn_down, candidates:{capability_no_consumer, hardcoding}}."""
    if store is None:
        import tempfile, os as _os
        from store.fs_store import FsStore
        store = FsStore(_os.path.join(tempfile.mkdtemp(prefix="coherence-scan-"), "store"))
    record_structural_findings(store, repo_root)
    return {"burn_down": burn_down(store),
            "candidates": {"capability_no_consumer": capability_no_consumer(repo_root),
                           "hardcoding": [d["name"] + f" ({d['file']}:{d['line']})" for d in hardcoding_candidates(repo_root)]}}


def format_scan(result: dict) -> str:
    """Render a scan scannably for the CLI (the FORM bar for this lane: a navigable surface, not a dict dump).
    The burn-down up top (the headline), the open backlog by disposition, then the candidates (adjudicate),
    clearly separated so the trustworthy must-fix set is never confused with the propose-only candidates."""
    b = result["burn_down"]
    c = result["candidates"]
    lines = []
    lines.append(f"COHERENCE — {b['total']} findings :: {b['open']} open · {b['accepted']} accepted · {b['closed']} closed")
    # the open backlog, grouped by disposition (the burn-down-to-zero target)
    byd = b["by_disposition"]
    open_disp = {k: v for k, v in byd.items() if k in (*_FINISH_DISPOSITIONS, "(open)")}
    if open_disp:
        lines.append("  OPEN (the burn-down target):")
        for disp, n in sorted(open_disp.items(), key=lambda kv: -kv[1]):
            lines.append(f"    [{disp}] {n}")
    acc_disp = {k: v for k, v in byd.items() if k in _ACCEPTED_DISPOSITIONS}
    if acc_disp:
        lines.append("  accepted (dispositioned — not a defect): "
                     + " · ".join(f"{disp} {n}" for disp, n in sorted(acc_disp.items())))
    lines.append(f"  by kind: " + " · ".join(f"{k} {v}" for k, v in sorted(b["by_kind"].items())))
    # the candidate detectors — positive-only, ADJUDICATE (never in the must-fix count)
    cnc, hc = c["capability_no_consumer"], c["hardcoding"]
    lines.append(f"\n  candidates (positive-only — adjudicate, never auto-acted):")
    lines.append(f"    capability-no-consumer ({len(cnc)}): {', '.join(cnc) if cnc else '—'}")
    lines.append(f"    hardcoding ({len(hc)}): {', '.join(hc[:8])}{' …' if len(hc) > 8 else ''}")
    return "\n".join(lines)


def record_structural_findings(store, repo_root: str) -> dict:
    """C6 — run the trustworthy structural detector (reachability) and WRITE its findings into the store, so
    the substrate flows end-to-end (detector → finding-store → disposition overlay → burn_down) on REAL data.
    Each orphan route lands as an `unwired-route` finding; a catalogued orphan's disposition is SEEDED from the
    declared orphan-routes catalogue tag (the _ORPHAN_ROUTES→records migration) — BUT only if undispositioned,
    so an operator's later decision is never clobbered by the catalogue default on re-detection (own/reflect:
    the decision persists, detection re-runs). A NEW (uncatalogued) orphan lands undispositioned → open (the
    burn-down target). Only the EXACT detector writes burn-down findings; the candidate detectors
    (capability-no-consumer/hardcoding) stay report-only (positive-only — they don't inflate the must-fix
    count). Returns {recorded}."""
    import json
    routes, wired = route_reachability(repo_root)
    cat_path = os.path.join(repo_root, "design", "_system", "orphan-routes.json")
    catalogue = json.load(open(cat_path, encoding="utf-8"))["routes"]
    recorded = 0
    for route in sorted(routes):
        if wired.get(route):
            continue                                     # wired — not a finding
        store.append_finding({"kind": "unwired-route", "address": route, "route": route,
                              "state": "built-no-caller", "source": "structural", "owner": "interface"})
        recorded += 1
        if route in catalogue and store.disposition_for("unwired-route", route) is None:
            store.append_disposition("unwired-route", route, catalogue[route]["tag"],
                                     reason=catalogue[route].get("note", ""), by="catalogue")
    return {"recorded": recorded}


def burn_down(store) -> dict:
    """C5 — the burn-down model: a READ-TIME fold over the finding store ⨝ the disposition overlay (the
    run_stats pattern — no maintained graph; own/reflect). Dedups the append-only findings by (kind,address)
    (a re-detection does not inflate the model), then classifies each distinct finding by its resolved
    disposition:
      open     = undispositioned OR a finish-disposition (to_wire/to_build_ui) — the burn-down-toward-zero set
      accepted = a dispositioned-accepted (by-design/backend_only/voice_owned) — acknowledged, not a defect
      closed   = resolved
    Returns {total, open, accepted, closed, by_kind, by_disposition, open_findings}. `(open)` is the
    by_disposition key for undispositioned findings (the honest default — never silently dropped)."""
    findings = store.all_findings()
    distinct: dict = {}
    for f in findings:
        distinct[_handle(f)] = f            # last record per handle (re-detection folds away)
    by_kind: dict = {}
    by_disposition: dict = {}
    open_count = accepted = closed = 0
    open_findings = []
    for (kind, address), f in distinct.items():
        by_kind[kind] = by_kind.get(kind, 0) + 1
        d = store.disposition_for(kind, address)
        disp = d["disposition"] if d else "(open)"
        by_disposition[disp] = by_disposition.get(disp, 0) + 1
        if disp in _ACCEPTED_DISPOSITIONS:
            accepted += 1
        elif disp in _CLOSED_DISPOSITIONS:
            closed += 1
        else:                                # undispositioned or a finish-disposition → open
            open_count += 1
            open_findings.append({"kind": kind, "address": address, "disposition": disp})
    return {"total": len(distinct), "open": open_count, "accepted": accepted, "closed": closed,
            "by_kind": by_kind, "by_disposition": by_disposition,
            "open_findings": sorted(open_findings, key=lambda x: (x["kind"], x["address"]))}


# ── #3 hardcoding candidates (CANDIDATE-only) — literals that mirror a registry ──────────────────────
def hardcoding_candidates(repo_root: str, min_entries: int = 6) -> list[dict]:
    """Module/class-level literal dict/list/tuple/set assigned to an UPPER_CASE name in runtime/*.py, with
    >= min_entries — a candidate hardcoded vocabulary that may belong in a registry (the pattern the
    no-hardcoding rule forbids; the _ORPHAN_ROUTES dict was exactly this until 2026-06-08). CANDIDATE-only:
    a big literal can be a legitimate constant (a grammar, an enum the registry derives FROM) — this
    PROPOSES for review, never declares. Returns [{file, name, kind, n, line}]."""
    out = []
    for f in glob.glob(os.path.join(repo_root, "runtime", "*.py")):
        src = open(f, errors="ignore").read()
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            up = [n for n in names if n.isupper() or (n[:1].isupper() and "_" in n)]
            if not up:
                continue
            v = node.value
            n_entries = (len(v.keys) if isinstance(v, ast.Dict)
                         else len(v.elts) if isinstance(v, (ast.List, ast.Tuple, ast.Set)) else 0)
            if n_entries >= min_entries:
                out.append({"file": os.path.relpath(f, repo_root), "name": up[0],
                            "kind": type(v).__name__, "n": n_entries, "line": node.lineno})
    return sorted(out, key=lambda d: (-d["n"], d["file"]))

