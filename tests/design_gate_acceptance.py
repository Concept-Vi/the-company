"""tests/design_gate_acceptance.py — F9 · the FORM gate is LIVE (the stub graduated).

Proves, BY USE, that `Suite._design_critic` is a REAL in-repo FORM gate, not the old stub that
hard-returned (False, "FORM unverifiable…") for ANY surface-touching build. The machine half of FORM
is now the corpus design-lint (`design/_system/check.py --target <changed file> --fail-on`) run over
the surface files a build CHANGED:

  • a CLEAN, token-only surface change (uses var(--x), no raw hex/rgba) → lint exits 0 → (True, …):
    a UI self-build may AUTO-CLOSE (no second manual gate — approval already happened at the
    build-intent guard);
  • an OFF-TOKEN surface change (a raw #hex / rgba(...) literal instead of var(--x)) → lint exits
    non-zero → (False, reason): the build is GATED, surfaces back, never auto-closes;
  • FAIL-SAFE: a surface change the lint cannot run on (no real file, missing corpus, any error) →
    (False, reason): unverifiable is NOT-passed; it NEVER silently returns True (rule 4).

A pure-backend build (no canvas/ change) has no form to grade → (True, …); it proceeds.

The HUMAN-JUDGMENT design-critic AGENT (browser + screenshots) is a SEPARATE stage the loop
dispatches at verify time — it is NOT run in-process here (a headless dispatch can't drive a browser,
and the implementer can't grade its own form). This suite covers the in-repo MACHINE half.

Self-contained: every surface file is planted in a TEMP tree (never the real repo's canvas/), so the
wholesale `tests/*.py` run is not poisoned. The corpus lint itself is the REAL one shipped in-repo at
design/_system/check.py (located off suite.py, not the temp _repo_root) — so this proves the gate end
to end, not against a mock.

Run: .venv/bin/python tests/design_gate_acceptance.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# Token-only surface — references corpus tokens via var(--x); NO raw colour literal. Lint-clean.
CLEAN_TSX = (
    "import './app.css';\n"
    "export const Card = () =>\n"
    "  <div className=\"card\" style={{ color: 'var(--fg)', background: 'var(--bg)' }}>\n"
    "    <span style={{ padding: 'var(--space-2)' }}>clean</span>\n"
    "  </div>;\n"
)

# Off-token surface — a raw hex literal (#abc123) AND a raw rgba(...) where a token (var(--x)) is
# required. A SINGLE occurrence trips the design-lint (gate semantics, not the recurrence finder).
DIRTY_TSX = (
    "export const Card = () =>\n"
    "  <div style={{ color: '#abc123', boxShadow: '0 0 4px rgba(0,0,0,0.4)' }}>off-token</div>;\n"
)


def fresh_suite():
    """A throwaway repo root (sandbox) so _repo_root → temp, never the real repo. The corpus lint is
    still the REAL one (located off suite.py)."""
    base = tempfile.mkdtemp(prefix="design-gate-")
    nodes = os.path.join(base, "nodes")
    os.makedirs(nodes)
    s = Suite(FsStore(os.path.join(base, "store")), NodeRegistry(), nodes_dir=nodes)
    return s, base


def plant(base, rel, body):
    """Write a surface file into the sandbox at <repo_root>/<rel> (mirrors a build's side effect)."""
    full = os.path.join(base, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(body)
    return rel


# --- 0 · the corpus lint the gate depends on exists in-repo (else every case below is fail-safe) ---
s, base = fresh_suite()
script = s._design_lint_corpus()
check(f"the in-repo corpus design-lint exists at {os.path.relpath(script, ROOT)} (F9 depends on C0)",
      os.path.exists(script))


# --- 1 · BACKEND build (no surface) → no form to grade → PASS (proceeds) ---
ok_be, why_be = s._design_critic(["runtime/suite.py", "store/fs_store.py"])
check("a pure-backend build (no canvas/ change) PASSES the FORM gate (no form to grade)", ok_be is True)


# --- 2 · CLEAN token-only surface change → lint exits 0 → PASS (may auto-close) ---
s, base = fresh_suite()
rel = plant(base, "canvas/app/src/Card.tsx", CLEAN_TSX)
ok_clean, why_clean = s._design_critic([rel])
check("a CLEAN token-only surface change PASSES the live FORM gate (design-lint clean → may auto-close)",
      ok_clean is True)
check("the pass reason names the design-lint as the satisfied machine half",
      "design-lint" in why_clean.lower() and "pass" in why_clean.lower())


# --- 3 · OFF-TOKEN surface change → lint exits non-zero → FAIL (gated, surfaces) ---
s, base = fresh_suite()
rel = plant(base, "canvas/app/src/Card.tsx", DIRTY_TSX)
ok_dirty, why_dirty = s._design_critic([rel])
check("an OFF-TOKEN surface change FAILS the live FORM gate (raw hex/rgba → design-lint non-zero)",
      ok_dirty is False)
check("the fail reason names the FORM gate + the off-token finding (legible, rule 4)",
      "form gate failed" in why_dirty.lower() and "off-token" in why_dirty.lower())


# --- 4 · a CLEAN change is NOT gated by pre-existing dirt elsewhere (lints only the CHANGED files) ---
s, base = fresh_suite()
plant(base, "canvas/app/src/Dirty.tsx", DIRTY_TSX)          # pre-existing dirt, NOT in this change-set
rel_clean = plant(base, "canvas/app/src/Clean.tsx", CLEAN_TSX)
ok_isolated, _ = s._design_critic([rel_clean])              # only the clean file is the changed surface
check("the gate lints only the CHANGED surface files — a clean change passes despite dirt elsewhere",
      ok_isolated is True)


# --- 5 · FAIL-SAFE · a surface change resolving to NO real file (lint can't run) → FALSE ---
s, base = fresh_suite()
ok_missing, why_missing = s._design_critic(["canvas/app/src/DoesNotExist.tsx"])
check("FAIL-SAFE: a surface change with no real file on disk returns False (unverifiable = not-passed)",
      ok_missing is False)
check("the fail-safe reason is labelled fail-safe (never a silent True, rule 4)",
      "fail-safe" in why_missing.lower())


# --- 6 · FAIL-SAFE · the corpus lint script missing → FALSE (never silent True) ---
# Subclass to simulate a vanished corpus (we never delete the real one). Surface still touched.
class _NoCorpus(Suite):
    def _design_lint_corpus(self):
        return os.path.join(tempfile.gettempdir(), "f9-no-such-corpus", "check.py")

s, base = fresh_suite()
ns = _NoCorpus(s.store, s.registry, nodes_dir=s.nodes_dir)
rel = plant(base, "canvas/app/src/Card.tsx", CLEAN_TSX)
ok_nocorpus, why_nocorpus = ns._design_critic([rel])
check("FAIL-SAFE: a missing corpus lint returns False even for an otherwise-clean surface",
      ok_nocorpus is False and "fail-safe" in why_nocorpus.lower())


print(f"\nALL {PASS} CHECKS PASS — F9 FORM gate LIVE: clean→pass · off-token→fail · unrunnable→fail-safe")
