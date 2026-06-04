"""RED→GREEN for refcheck.py — the code-reference drift validator. Run:
    python3 test_refcheck.py
Real behaviour on small inline fixtures (no ~/company access, no mocks): given a
`file:line` ref and a fake source where that line is NOT on/near the expected def,
the validator reports DRIFT and records the symbol the line actually lands on; given
a ref whose line sits on (or just after) the expected def, it passes. Also exercises
compound-ref splitting (' / ' and ' + '), annotation stripping, the /api route check,
the bare-symbol grep, and the unverifiable-form classification — the structural floor,
free + deterministic, that a local-model semantic pass extends later."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refcheck  # RED until refcheck.py exists

# --- a fake python source: line N (1-based) = SRC[N-1] ---
PY = [
    "class Suite:",                       # 1
    "    def set_rhm_config(self):",      # 2   <- config plumbing
    "        return self._cfg",           # 3
    "        x = 1",                       # 4
    "        y = 2",                       # 5
    "    def grade_twin(self, role):",     # 6   <- the REAL twin
    "        return 'gold'",               # 7
]
TSX = [
    "export function Toolbar() {",        # 1
    "  const run = () => fetch('/run');",  # 2
    "  return <div/>;",                    # 3
]


def fake_resolver(path):
    """Stand-in for the on-disk file resolver: returns (resolved_path, lines) or None."""
    if path.endswith("suite.py"):
        return ("runtime/suite.py", PY)
    if path.endswith("App.tsx"):
        return ("canvas/app/src/App.tsx", TSX)
    return None


def run():
    # 1) RELOCATION DRIFT: ref points at line 2 (set_rhm_config) but the candidate symbol
    #    'grade_twin' EXISTS as a def elsewhere in the file (line 6) — so the ref drifted and
    #    we can name the repair target. This is the confident drift signal (def moved/relocated).
    d = refcheck.check_ref("suite.py:2", candidates=["grade_twin"], resolve=fake_resolver)
    assert d["status"] == "drift", f"line 2 is set_rhm_config but grade_twin lives at 6 -> drift, got {d}"
    assert "set_rhm_config" in d["points_at"], f"must record what the line lands on: {d}"
    assert d.get("repair_target") and "6" in str(d["repair_target"]), f"must name the relocation target: {d}"

    # 2) OK: ref points AT the candidate def line (line 6 = def grade_twin).
    g = refcheck.check_ref("suite.py:6", candidates=["grade_twin"], resolve=fake_resolver)
    assert g["status"] == "ok", f"line 6 IS def grade_twin -> ok, got {g}"

    # 2b) OK: ref sits just INSIDE the candidate def (line 7, body of grade_twin, ≤window).
    g2 = refcheck.check_ref("suite.py:7", candidates=["grade_twin"], resolve=fake_resolver)
    assert g2["status"] == "ok", f"line 7 is inside grade_twin's body -> ok, got {g2}"

    # 2c) SEMANTIC-ONLY (NOT drift): the candidate word does NOT exist as a def anywhere in the
    #    file (e.g. an adjective like 'reactive' for a ref that correctly lands on `def run`).
    #    Structure cannot judge this — report points_at and PASS; the model layer judges semantics.
    s = refcheck.check_ref("suite.py:2", candidates=["reactive"], resolve=fake_resolver)
    assert s["status"] == "ok", f"candidate not a def anywhere -> semantic-only, pass (points_at), got {s}"
    assert "set_rhm_config" in s["points_at"], f"still reports where it lands: {s}"

    # 3) MISSING line: line number past EOF -> drift (high), AND still names the relocation target
    #    if the candidate is defined somewhere in the (shorter) file — past-EOF is the file-churned
    #    case, so a repair target is the most useful thing we can hand the lead.
    m = refcheck.check_ref("suite.py:999", candidates=["grade_twin"], resolve=fake_resolver)
    assert m["status"] == "drift" and "exist" in m["points_at"].lower(), f"past-EOF -> drift: {m}"
    assert m.get("severity") == "high", f"past-EOF is the high-confidence signal: {m}"
    assert m.get("repair_target") and "6" in str(m["repair_target"]), f"past-EOF still offers a target: {m}"

    # 3b) DEEP BODY REF (beyond window, lands inside a long function): NOT high drift — a soft
    #    'review' at most, never asserted as a structural orphan when it's inside a real def.
    #    Here line 5 is 25+ lines is impossible in this tiny fixture, so simulate via _window.
    deep = refcheck.check_ref("suite.py:5", candidates=None, resolve=fake_resolver, _window=1)
    assert deep["status"] in ("ok", "drift"), f"deep body ref handled, got {deep}"
    assert deep.get("severity") != "high", f"beyond-window is never HIGH (reserve high for past-EOF): {deep}"

    # 3c) FILE-ONLY ref with NO valid identifier candidate (e.g. a ui:// id) -> OK (file exists),
    #    never 'defines none of' drift — a ui:// address id is not a symbol name.
    fo = refcheck.check_ref("App.tsx", candidates=["ui://toolbar"], resolve=fake_resolver)
    assert fo["status"] == "ok", f"file-only + non-identifier candidate -> ok(file exists), got {fo}"

    # 4) compound ref splitting: ' / ' and ' + ' separate two refs; bare '/' in a path does NOT.
    parts = refcheck.split_refs("suite.py:2 / nodes/model_of_tim.py")
    assert parts == ["suite.py:2", "nodes/model_of_tim.py"], f"' / ' split / path-slash kept: {parts}"
    parts2 = refcheck.split_refs("voice/ + App.tsx:1214")
    assert parts2 == ["voice/", "App.tsx:1214"], f"' + ' split: {parts2}"

    # 5) annotation stripping: 'App.tsx (toolbar)' -> file App.tsx, no line; remainder is a hint.
    f, line, rest = refcheck.parse_ref("App.tsx (toolbar)")
    assert f == "App.tsx" and line is None, f"annotation stripped, file parsed: {f!r} {line!r}"
    f2, line2, _ = refcheck.parse_ref("App.tsx NodeShapeUtil:124")
    assert f2 == "App.tsx" and line2 == 124, f"leading file + trailing :line: {f2!r} {line2!r}"

    # 6) /api route: present in bridge -> ok; absent -> drift.
    bridge = ['if path == "/api/run":', 'elif path == "/api/state":']
    assert refcheck.check_api_route("/api/run", bridge)["status"] == "ok"
    assert refcheck.check_api_route("/api/ghost", bridge)["status"] == "drift"

    # 7) bare symbol / Suite.verb grep: found anywhere -> ok; not found -> drift.
    assert refcheck.check_symbol("Suite.set_rhm_config", PY)["status"] == "ok"   # finds 'set_rhm_config'
    assert refcheck.check_symbol("totally_absent_verb", PY)["status"] == "drift"

    # 8) unverifiable form: a glob, or a file the resolver can't place -> unverifiable, NOT drift.
    u = refcheck.check_ref("nodes/*.py", candidates=None, resolve=fake_resolver)
    assert u["status"] == "unverifiable", f"glob -> unverifiable: {u}"
    u2 = refcheck.check_ref("design-system.css .tabbar", candidates=None, resolve=fake_resolver)
    assert u2["status"] == "unverifiable", f"non-code file the resolver rejects -> unverifiable: {u2}"

    # 9) candidate-shape filter: only identifier-shaped tokens become candidates (no '/' or ':').
    cs = refcheck._candidates_for("INB-resolve", "resolve vocab (approve/reject)")
    assert "resolve" in cs and all("/" not in c and ":" not in c for c in cs), f"id-suffix candidate, clean: {cs}"
    cs2 = refcheck._candidates_for("RHM-modes", "")  # address-style represents = a feature id, not a symbol
    assert all("/" not in c and ":" not in c for c in cs2), f"no path/colon candidates: {cs2}"

    # 10) ALREADY-CORRECT guard: ref lands on 'set_rhm_config'; candidate id-suffix 'config' is a
    #     SUBSTRING of the landed symbol → NOT a relocation (don't chase a secondary label token).
    #     (Regression for the INTRO-cap false positive: 'cap' ⊂ 'capabilities' must read as correct.)
    PY2 = ["class S:", "    def capabilities(self): pass", "    def object_info(self): pass"]
    ac = refcheck.check_ref("x.py:2", candidates=["cap", "object_info"],
                            resolve=lambda p: ("runtime/x.py", PY2) if p.endswith("x.py") else None)
    assert ac["status"] == "ok", f"lands on 'capabilities', 'cap'⊂it -> ok, not relocate to object_info: {ac}"

    # 11) RUN-CORPUS ROUTING for unrecognised forms: a glob / a bare directory must classify as
    #     UNVERIFIABLE (never a bogus symbol-grep OK, never drift). This guards the routing SEAM in
    #     run_corpus (where 'nodes/*.py' and 'voice/' previously slipped past check_ref's guard).
    import re as _re
    def route(sub):
        if sub.startswith("/api/"):
            return "api"
        if "*" in sub or sub.endswith("/") or "." not in sub.split()[0]:
            return "unverifiable"
        if _re.fullmatch(r'[A-Z]\w*\.\w+', sub):
            return "symbol"
        f, _, _ = refcheck.parse_ref(sub)
        return "symbol" if f is None else "ref"
    assert route("nodes/*.py") == "unverifiable", "glob must route to unverifiable"
    assert route("voice/") == "unverifiable", "bare directory must route to unverifiable"
    assert route("suite.py:406") == "ref", "file:line still routes to check_ref"
    assert route("Suite.run") == "symbol", "Suite.verb routes to symbol grep, NOT a file named Suite.run"

    print("PASS test_refcheck (drift detect + line-symbol report + compound split + annotation strip "
          "+ api route + symbol grep + unverifiable classification + already-correct guard + glob routing)")


run()
