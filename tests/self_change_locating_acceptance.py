"""tests/self_change_locating_acceptance.py — L5 · self-change-locating (§21.7#5).

"What changed HERE?" — filter the self-change audit log by the ADDRESS the operator is at, and
revert from there. The address→code join is S3's resolver (`resolve_scope`, corpus-side); L5 adds an
address FILTER on top of the EXISTING `self_change_log` — it does NOT modify the log/revert methods.

THE JOIN (additive query, no new revert path):
    address  --S3 resolve_scope-->  scope[]  (repo-relative code files)
    self_change_log().changed_files  ∩  scope[]   →  the changes that touched THIS element.

This suite proves:
  1. A self-change whose `changed_files` touch a scope S3 maps to `ui://workshop/self-changes`
     (→ runtime/suite.py) IS returned by the address-filtered query for that address.
  2. ISOLATION — a change touching a DIFFERENT scope (canvas/app/src/App.tsx, which
     `ui://chat/input` maps to) is NOT returned for `ui://workshop/self-changes`, and vice-versa.
     Same two synthetic records prove the join BOTH ways, against the REAL corpus resolver.
  3. PRESERVE — `self_change_log` / `last_self_change` / `revert_self_change` are unchanged: the
     query is a NEW method that calls them, never an edit to them. (We assert the existing methods
     still answer, and that the new method does not shadow/replace them.)
  4. STALE TRICHOTOMY (rule 4 — fail-loud, not a silent empty):
       (a) scope resolves → filter (changes that touch it, possibly empty = legit "none here");
       (b) empty scope, NOT stale (orphan/CSS-selector/DENY-ALL address) → [] WITH the note;
       (c) corpus unreadable → stale:True propagated WITH the note — NEVER a silent [] that lies
           "nothing changed here". The query passes `stale`/`note` straight through from resolve_scope.
  5. REVERT-AT-ADDRESS composes the EXISTING `revert_self_change(sha)` — the file→ui→sha chain
     resolves, then the same operator-only revert runs (we capture the sha via a mock leaf; we do
     NOT mutate git). No new revert path; the operator-only `/api/revert` gate is untouched.
  6. The query is reachable from a real FACE (a bridge.py GET route calls it, mirroring /api/scope).

DETERMINISM: `self_change_log` reads real git history (non-deterministic), so the isolation
assertions feed SYNTHETIC records (monkeypatch `self_change_log`) while using the REAL
`resolve_scope` against the present corpus — both join directions are then provable exactly.

FRESHNESS COUPLING (seams-engine risk #4): the join depends on the regenerated
design/_system/code-symbols.json — a STALE corpus returns a STALE change list. Surfaced via
`stale`/`note`, never pretended-live (proven by check 4c).
"""
import os
import re
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


NODES = os.path.join(ROOT, "nodes")
store = FsStore(os.path.join(tempfile.mkdtemp(prefix="l5-"), "store"))
reg = NodeRegistry(); reg.discover([NODES])
suite = Suite(store, reg, nodes_dir=NODES)

# Two REAL corpus addresses with clean, non-overlapping scopes (verified live):
#   ui://workshop/self-changes → ['runtime/suite.py']
#   ui://chat/input            → ['canvas/app/src/App.tsx']
WORKSHOP = "ui://workshop/self-changes"
CHATIN = "ui://chat/input"

# sanity: the corpus resolver gives the scopes the join leans on (else the fixtures are wrong, not L5)
check(f"{WORKSHOP} resolves to runtime/suite.py (S3, real corpus)",
      suite.resolve_scope(WORKSHOP)["scope"] == ["runtime/suite.py"])
check(f"{CHATIN} resolves to canvas/app/src/App.tsx only (S3, real corpus)",
      suite.resolve_scope(CHATIN)["scope"] == ["canvas/app/src/App.tsx"])

# Two SYNTHETIC self-change records — one per scope — so the join is provable BOTH directions.
SUITE_CHANGE = {"sha": "aaaa1111", "subject": "[self-apply] add node-type 'foo'",
                "ts": "2026-06-05T10:00:00+10:00", "is_revert": False,
                "changed_files": ["runtime/suite.py", "nodes/foo.py"]}
APP_CHANGE = {"sha": "bbbb2222", "subject": "[self-apply] tweak the canvas shell",
              "ts": "2026-06-05T11:00:00+10:00", "is_revert": False,
              "changed_files": ["canvas/app/src/App.tsx"]}
_real_self_change_log = suite.self_change_log
suite.self_change_log = lambda limit=50: [APP_CHANGE, SUITE_CHANGE]   # newest-first, synthetic

# ── 1. the change touching the address's scope IS returned ────────────────────
ws = suite.self_changes_at(WORKSHOP)
shas_ws = [c["sha"] for c in ws["changes"]]
check(f"{WORKSHOP} → returns the suite.py change ({shas_ws})", "aaaa1111" in shas_ws)
check(f"{WORKSHOP} carries its address + scope", ws["address"] == WORKSHOP and ws["scope"] == ["runtime/suite.py"])
check("a returned change carries the touched files (the operator sees WHY it matched)",
      "runtime/suite.py" in (ws["changes"][0].get("matched_files") or ws["changes"][0]["changed_files"]))

# ── 2. ISOLATION — both directions, same two records ──────────────────────────
check(f"{WORKSHOP} does NOT return the App.tsx change (isolation)", "bbbb2222" not in shas_ws)
ci = suite.self_changes_at(CHATIN)
shas_ci = [c["sha"] for c in ci["changes"]]
check(f"{CHATIN} → returns ONLY the App.tsx change ({shas_ci})", shas_ci == ["bbbb2222"])
check(f"{CHATIN} does NOT return the suite.py change (isolation other way)", "aaaa1111" not in shas_ci)

# ── 4b. empty scope, NOT stale → [] WITH the note (DENY-ALL address) ──────────
orphan = suite.self_changes_at("ui://nonexistent/thing")
check("orphan address → no changes (empty scope, DENY-ALL)", orphan["changes"] == [])
check("orphan address is NOT stale", orphan["stale"] is False)
check("orphan address carries the surfaced note (the gap, not a silent empty)", bool(orphan["note"]))

# restore the real log for the preserve + stale checks below
suite.self_change_log = _real_self_change_log

# ── 3. PRESERVE — existing methods unchanged + the new method does not replace them
check("self_change_log still callable + returns a list (preserved)", isinstance(suite.self_change_log(3), list))
check("last_self_change still callable (preserved)", suite.last_self_change() is None or isinstance(suite.last_self_change(), dict))
check("revert_self_change still present + callable (preserved)", callable(suite.revert_self_change))
check("self_changes_at is a NEW method, distinct from self_change_log",
      suite.self_changes_at is not suite.self_change_log)
# source-level preserve: the existing method bodies are byte-for-byte (no edit). We assert the new
# method is additive by confirming the existing signatures still answer with the documented keys.
real = suite.self_change_log(50)
if real:
    check("self_change_log records still carry the documented keys (sha/changed_files/is_revert)",
          all(k in real[0] for k in ("sha", "subject", "ts", "is_revert", "changed_files")))
else:
    check("self_change_log returns [] on no ledger (documented degrade) — preserved", real == [])

# ── 4c. STALE TRICHOTOMY — corpus unreadable → stale propagated, NOT a silent empty
# Point the resolver at an empty corpus dir so code-symbols.json is unreadable → resolve_scope stale.
empty_corpus = tempfile.mkdtemp(prefix="l5-empty-corpus-")
os.makedirs(os.path.join(empty_corpus, "design", "_system"), exist_ok=True)
_real_corpus_dir = suite._corpus_dir
suite._corpus_dir = lambda: os.path.join(empty_corpus, "design", "_system")
suite.self_change_log = lambda limit=50: [SUITE_CHANGE]   # there IS a change touching suite.py
stale = suite.self_changes_at(WORKSHOP)
check("corpus unreadable → stale:True PROPAGATED (not a silent empty that lies 'nothing here')",
      stale["stale"] is True)
check("stale result carries the legible note (regenerate the corpus)", bool(stale["note"]))
check("stale result does NOT fabricate a change list (changes empty under DENY-ALL stale scope)",
      stale["changes"] == [])
suite._corpus_dir = _real_corpus_dir
suite.self_change_log = _real_self_change_log

# ── 5. REVERT-AT-ADDRESS composes the EXISTING revert_self_change(sha) — no new path
captured = {}
_real_revert = suite.revert_self_change
def _mock_revert(sha):
    captured["sha"] = sha
    return {"reverted": sha, "head": "deadbeef"}
suite.revert_self_change = _mock_revert
suite.self_change_log = lambda limit=50: [SUITE_CHANGE]
# the operator, at WORKSHOP, picks the change that touched here and reverts it — the chain resolves
# the sha from the address-filtered list, then composes the SAME revert.
out = suite.revert_self_change_at(WORKSHOP, "aaaa1111")
check("revert-at-address composed the EXISTING revert_self_change with the right sha",
      captured.get("sha") == "aaaa1111")
check("revert-at-address returns the existing revert's result (reverted+head)",
      out.get("reverted") == "aaaa1111")
# a sha NOT in the address's filtered list is REFUSED (you can only revert what changed HERE) — fail loud
refused = False
try:
    suite.revert_self_change_at(WORKSHOP, "bbbb2222")   # App.tsx change, not at this address
except (ValueError, KeyError):
    refused = True
check("revert-at-address REFUSES a sha that did not change at this address (fail loud, scoped)", refused)
suite.revert_self_change = _real_revert
suite.self_change_log = _real_self_change_log

# ── 6. reachable from a real FACE — a bridge GET route calls it ───────────────
with open(os.path.join(ROOT, "runtime", "bridge.py"), encoding="utf-8") as f:
    bridge_src = f.read()
check("bridge.py has a /api/self-changes-at route", "/api/self-changes-at" in bridge_src)
check("the route calls SUITE.self_changes_at", "self_changes_at" in bridge_src)
check("revert stays on the EXISTING operator-only /api/revert gate (no new revert route)",
      bridge_src.count("/api/revert") >= 1 and "/api/revert-at" not in bridge_src)

print(f"\nSELF-CHANGE LOCATING ACCEPTANCE — {PASS} checks passed. "
      f"'what changed HERE?' filters self_change_log by S3's address→code scope join; isolation holds "
      f"both ways; revert-at-address composes the EXISTING revert_self_change (operator-only gate "
      f"untouched); stale trichotomy fails loud (corpus unreadable → stale, never a silent empty). "
      f"FRESHNESS: the join depends on the regenerated code-symbols.json — surfaced via stale/note.")
