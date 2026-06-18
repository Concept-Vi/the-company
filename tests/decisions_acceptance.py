"""tests/decisions_acceptance.py — the decision-surface RESOLVER acceptance (fork's lane, 2026-06-18).

The decision:// scheme is the resolution-first decision-surface's first content type + the Face-Pipeline's
reconcile vessel (composition's contract). fork's piece = the resolver + parse + registry + render. Proves,
by use + adversarially:

  D1  decision:// is a registered scheme; the grammar parses (frame / bare) + the canonical normalizer holds.
  D2  the file-discovered DecisionRegistry discovers the bootstrap row + validates it.
  D3  the `decision_take` mark-type is REGISTERED under that EXACT string (the take-writer's id; a hyphen-form
      "decision-take" is NOT registered — would fail loud at suite.mark).
  D4  resolve_address(store, decision://…) → the row COMPOSED with state; pending with no take.
  D5  THE NORMALIZATION (adversarial): a take written to the canonical of the BARE form is SEEN when resolving
      via the GLOBAL form AND the bare form — ONE mark key, never a silently-pending decided decision.
  D6  fail-loud: unknown decision · malformed address · missing store (state can't be guessed/silent).
  D7  territory_prose renders the decision HUMANLY (meaning + options + state) with NO address/machine leak.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

PASS = 0
ok = True


def check(label, cond):
    global PASS, ok
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        ok = False
        print(f"  FAIL  {label}")


from contracts.address import SCHEMES, scheme, parse_decision_address, decision_address
from runtime.cognition import resolve_address, decision_registry
from runtime.decision_registry import DecisionRegistry, compose_state, DecisionError
from runtime.mark_types import MarkTypeRegistry
from runtime.territory import territory_prose, territory_label, DIRECTION_MARK_TYPES
from store.fs_store import FsStore

BID = "merge-sa-authorize"
A_BARE = f"decision://{BID}"
A_GLOB = f"decision://global/{BID}"
CANON = "decision://global/merge-sa-authorize"

# ── D1 — scheme + grammar + canonical normalizer ──────────────────────────────────────────────────
print("\n[D1] decision:// scheme registered + grammar + canonical normalizer")
check("D1 'decision' is in contracts.address.SCHEMES", "decision" in SCHEMES)
check("D1 scheme() classifies a decision:// address", scheme(A_GLOB) == "decision")
check("D1 bare decision://<id> parses to global frame", parse_decision_address(A_BARE)["scope_kind"] == "global")
check("D1 bare ≡ global canonical (the ONE mark key)",
      decision_address(parse_decision_address(A_BARE)) == decision_address(parse_decision_address(A_GLOB)) == CANON)
check("D1 project frame canonical preserved",
      decision_address(parse_decision_address("decision://project/p7/x")) == "decision://project/p7/x")
for bad in ("vi-vision://x", "decision://", "decision://project", "decision://global", "decision://global/a/b"):
    raised = False
    try:
        parse_decision_address(bad)
    except ValueError:
        raised = True
    check(f"D1 malformed {bad!r} RAISES (fail-loud parse)", raised)

# ── D2 — the file-discovered registry discovers + validates the bootstrap ───────────────────────────
print("\n[D2] the DecisionRegistry discovers the bootstrap row + validates")
reg = decision_registry()
check("D2 the bootstrap decision is discovered (registry-is-truth: a decision is a file)", BID in reg)
row = reg.get(BID)
check("D2 the row carries human meaning + ≥2 options + a recommended one",
      bool(row["meaning"]) and len(row["options"]) >= 2 and any(o.get("recommended") for o in row["options"]))
# a malformed row fails loud at build (the gate bites)
raised = False
try:
    DecisionRegistry().register("x", {"id": "x", "options": [{"label": "a"}]})  # no meaning
except DecisionError:
    raised = True
check("D2 a malformed decision (no meaning) is REFUSED at build (DecisionError)", raised)

# ── D3 — the decision_take mark-type is registered under the EXACT id ───────────────────────────────
print("\n[D3] decision_take mark-type registered (the take-writer's exact string)")
mreg = MarkTypeRegistry().discover([os.path.join(ROOT, "mark_types")])
check("D3 'decision_take' (underscore) IS a registered mark-type", "decision_take" in mreg)
check("D3 'decision-take' (hyphen) is NOT registered (a hyphen-form take would fail loud)",
      "decision-take" not in mreg)
check("D3 territory's route-back set names decision_take", "decision_take" in DIRECTION_MARK_TYPES)

# ── D4 — resolve → row + composed state; pending with no take ───────────────────────────────────────
print("\n[D4] resolve_address composes the decision (pending with no take)")
store = FsStore(tempfile.mkdtemp(prefix="dec-"))
r = resolve_address(store, A_GLOB)
check("D4 resolve returns the row's meaning + options", isinstance(r, dict) and r.get("meaning") and r.get("options"))
check("D4 with NO take the state is pending", r.get("state") == "pending" and r.get("decided_value") is None)

# ── D5 — THE NORMALIZATION (adversarial): take on the bare-canonical seen via global + bare ──────────
print("\n[D5] adversarial normalization — one mark key across bare/global forms")
canon_from_bare = decision_address(parse_decision_address(A_BARE))      # what the take-writer keys off
store.append_mark({"target": canon_from_bare, "mark_type": "decision_take",
                   "value": "Give it save-back access", "by": "operator",
                   "ts": "2026-06-18T12:00:00+00:00"})
r_glob = resolve_address(store, A_GLOB)        # resolve via GLOBAL form
r_bare = resolve_address(store, A_BARE)        # resolve via BARE form
check("D5 the take (written to the bare-canonical) is SEEN resolving via the GLOBAL form → decided",
      r_glob.get("state") == "decided" and r_glob.get("decided_value") == "Give it save-back access")
check("D5 …and SEEN resolving via the BARE form too (one key, no silent-pending)",
      r_bare.get("state") == "decided" and r_bare.get("decided_value") == "Give it save-back access"
      and r_bare.get("decided_by") == "operator")
# latest-by-ts: a later take overrides
store.append_mark({"target": canon_from_bare, "mark_type": "decision_take",
                   "value": "Stay read-only for now", "ts": "2026-06-18T18:00:00+00:00"})
check("D5 the LATEST take by ts wins",
      resolve_address(store, A_GLOB).get("decided_value") == "Stay read-only for now")

# ── D6 — fail-loud ──────────────────────────────────────────────────────────────────────────────────
print("\n[D6] fail-loud: unknown · malformed · missing-store")
for addr, why in ((f"decision://global/no-such-decision-xyz", "unknown decision"),
                  ("decision://project", "malformed address")):
    raised = False
    try:
        resolve_address(store, addr)
    except ValueError:
        raised = True
    check(f"D6 {why} RAISES (fail-loud, never silent-empty)", raised)
raised = False
try:
    resolve_address(None, A_GLOB)        # no store → state can't be composed
except ValueError:
    raised = True
check("D6 a missing store RAISES (state can't be guessed — no-silent-fallback)", raised)

# ── D7 — territory_prose renders the decision HUMANLY, no leak ──────────────────────────────────────
print("\n[D7] territory_prose renders the decision humanly (no address/machine leak)")
# fresh store so it renders the PENDING form (no take) — the operator-first case
pstore = FsStore(tempfile.mkdtemp(prefix="dec-p-"))
prose = territory_prose(A_GLOB, store=pstore)
label = territory_label(A_GLOB, store=pstore)
check("D7 the human label is the decision's legibility name (not 'this'/an address)",
      label == "Turn on save-back to the design library")
check("D7 the prose carries the decision question (meaning) + an option label",
      "save designs back" in prose and "Stay read-only for now" in prose)
check("D7 the prose names the suggested option + the open state",
      "(suggested)" in prose and "still open" in prose)
check("D7 NO raw address / scheme leak in the operator prose (operator-law)",
      "://" not in prose and "decision_take" not in prose and BID not in prose)

print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} — {PASS} checks passed — the decision:// resolver: "
      "scheme+grammar+canonical normalizer, file-discovered registry, decision_take mark-type, resolve→row+state, "
      "the adversarial one-key normalization, fail-loud, and a human (no-leak) render.")
sys.exit(0 if ok else 1)
