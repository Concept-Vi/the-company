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
