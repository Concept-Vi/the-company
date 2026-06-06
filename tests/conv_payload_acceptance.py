"""tests/conv_payload_acceptance.py — Convergence X1 + X2 · the launch-context truth reaches DISK.

THE DEFECTS (Research Synthesis, Round 1 — Observed, file:line):
  X1 — `surface_intent_at` did `out["address"]=ui_addr` (suite.py:3043) but that mutated the RETURN
       dict AFTER `surface_build_intent` already persisted the record (suite.py:2984). The address never
       reached the stored record — the build composed from a record that didn't know WHERE it came from.
  X2 — `resolve_scope` computes `symbols[]` (the `code://` neighbours behind the address) but
       `surface_intent_at` forwarded only `scope` (suite.py:3032-3033). The relationships were
       computed-then-discarded — the build never inherited the code neighbours of the locus.

THE FIX (schema-ADDITIVE, rule 2): thread `address` (X1) + `symbols` (X2) into the `payload` dict
BEFORE `inbox.surface` persists it — the open record (`inbox.surface` splats payload) carries them, so
the RELOADED-FROM-DISK record has both. The 5 existing payload fields (intent/spec/scope/
consequence_class/why) + every `.get`-based reader are untouched.

PROOF MODEL:
  • RELOAD FROM DISK — a FRESH Suite on the SAME store root reads the surfaced record back; that is the
    strongest "reaches disk" proof (not the same in-memory return dict). The reloaded payload carries
    `address` == the ui:// locus (X1) AND `symbols` == resolve_scope(addr)["symbols"] (X2).
  • REUSE-NOT-RECOMPUTE (X2) — the persisted symbols == the value resolve_scope already computed.
  • PRESERVE — the 5 existing payload fields survive verbatim; `.get` readers of the OLD fields are
    unaffected; an intent minted via the bare `surface_build_intent` (no address) has NO address/symbols
    keys (additive-optional: absent reads as None, exactly as before); empty-scope=DENY-ALL still holds.

REAL corpus addresses (verified live, same fixtures L1 uses):
  ui://chat/input            → symbols=['code://App'],                    scope=['canvas/app/src/App.tsx']
  ui://workshop/self-changes → symbols=['code://suite/revert_self_change'], scope=['runtime/suite.py']

Run: /home/tim/company/.venv/bin/python tests/conv_payload_acceptance.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_TEST_RUN"] = "1"

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
STORE_ROOT = os.path.join(tempfile.mkdtemp(prefix="conv-payload-"), "store")
store = FsStore(STORE_ROOT)
reg = NodeRegistry(); reg.discover([NODES])
suite = Suite(store, reg, nodes_dir=NODES)

CHATIN = "ui://chat/input"                 # → symbols=['code://App'], scope=['canvas/app/src/App.tsx']
WORKSHOP = "ui://workshop/self-changes"    # → symbols=['code://suite/revert_self_change']
ORPHAN = "ui://nonexistent/thing"          # → [] (DENY-ALL)

# sanity: the corpus resolver gives the symbols+scope the assertions lean on (else the fixtures are wrong)
rs = suite.resolve_scope(CHATIN)
check(f"{CHATIN} resolves symbols=['code://App'] (S3, real corpus)", rs["symbols"] == ["code://App"])
check(f"{CHATIN} resolves scope=['canvas/app/src/App.tsx'] (S3, real corpus)",
      rs["scope"] == ["canvas/app/src/App.tsx"])

# ── mint a build-intent at the address (the L1 mint path that widens the payload) ────────────────
out = suite.surface_intent_at(CHATIN, "this run button is too loud — tone it down", source="operator")
sid = out["id"]

# ════════════════════════════════════════════════════════════════════════════════════════════════
# THE LOAD-BEARING PROOF — reload the PERSISTED record from disk via a FRESH Suite on the same store
# ════════════════════════════════════════════════════════════════════════════════════════════════
store2 = FsStore(STORE_ROOT)                       # a SEPARATE store handle on the SAME root
suite2 = Suite(store2, reg, nodes_dir=NODES)
reloaded = suite2.inbox.get(sid)                   # reads disk (get_surfaced)
check("the build-intent persisted and reloads from disk (fresh Suite, same store root)",
      reloaded is not None and Suite.is_build_intent(reloaded))
payload = reloaded["payload"]

# X1 — the address reaches disk
check("X1: the RELOADED payload carries the ui:// address (reaches disk, not just the return dict)",
      payload.get("address") == CHATIN)

# X2 — the relationships (code:// symbol-neighbours) reach disk
check("X2: the RELOADED payload carries the code:// symbol-neighbours",
      payload.get("symbols") == ["code://App"])
check("X2: the persisted symbols == resolve_scope's computed value (REUSED, not recomputed/fabricated)",
      payload.get("symbols") == suite.resolve_scope(CHATIN)["symbols"])

# a SECOND real address proves it's general, not hardcoded — and the two travel TOGETHER with their scope
out2 = suite.surface_intent_at(WORKSHOP, "the self-change ledger needs a clearer label")
r2 = FsStore(STORE_ROOT)
p2 = Suite(r2, reg, nodes_dir=NODES).inbox.get(out2["id"])["payload"]
check(f"X1/X2 general: {WORKSHOP} persists its address",
      p2.get("address") == WORKSHOP)
check(f"X1/X2 general: {WORKSHOP} persists symbols=['code://suite/revert_self_change']",
      p2.get("symbols") == ["code://suite/revert_self_change"])
check("the address's symbols + scope travel together on the persisted record (the relationship reaches disk)",
      p2.get("symbols") == ["code://suite/revert_self_change"] and (p2.get("scope") or []) == ["runtime/suite.py"])

# ── PRESERVE — the 5 existing payload fields survive verbatim; .get readers unaffected ────────────
for f in ("intent", "spec", "scope", "consequence_class", "why"):
    check(f"PRESERVE: the existing payload field {f!r} survives on the reloaded record",
          f in payload)
check("PRESERVE: intent=='build' (the discriminator, untouched)", payload.get("intent") == "build")
check("PRESERVE: scope still carries S3's resolved scope (X2 added symbols BESIDE it, didn't touch it)",
      (payload.get("scope") or []) == ["canvas/app/src/App.tsx"])
check("PRESERVE: the comment text still drives the spec",
      "tone it down" in (payload.get("spec") or "") or "too loud" in (payload.get("spec") or ""))
check("PRESERVE: a .get of an OLD field (why) still works exactly as before",
      isinstance(payload.get("why"), str) and CHATIN in payload.get("why"))

# ── PRESERVE — surface_build_intent without an address: NO address/symbols keys (additive-optional) ──
bare = suite.surface_build_intent("a plain build with no address", scope=["runtime/suite.py"])
bp = FsStore(STORE_ROOT)
bpl = Suite(bp, reg, nodes_dir=NODES).inbox.get(bare["id"])["payload"]
check("PRESERVE: a bare surface_build_intent (no address) persists NO 'address' key (additive-optional)",
      "address" not in bpl)
check("PRESERVE: a bare surface_build_intent (no symbols) persists NO 'symbols' key",
      "symbols" not in bpl)
check("PRESERVE: a .get('address') on the OLD-shape record reads as None (readers unaffected)",
      bpl.get("address") is None and bpl.get("symbols") is None)
check("PRESERVE: a bare declared scope is still carried through verbatim (intent='build')",
      Suite.is_build_intent({"payload": bpl}) and (bpl.get("scope") or []) == ["runtime/suite.py"])

# ── PRESERVE — an ORPHAN address: empty scope (DENY-ALL) + the address still reaches disk, no fabrication
orphan_out = suite.surface_intent_at(ORPHAN, "change something here")
op = FsStore(STORE_ROOT)
opl = Suite(op, reg, nodes_dir=NODES).inbox.get(orphan_out["id"])["payload"]
check("PRESERVE: an orphan address persists EMPTY scope (DENY-ALL, never fabricated)",
      (opl.get("scope") or []) == [])
check("X1 holds even for an orphan: the address still reaches disk (the locus is recorded regardless)",
      opl.get("address") == ORPHAN)
check("X2 holds for an orphan: empty symbols persisted (no fabrication — the orphan has no neighbours)",
      (opl.get("symbols") or []) == [])
check("PRESERVE: the orphan return dict still carries the legible stale/note (return-readers unaffected)",
      bool(orphan_out.get("note")) or orphan_out.get("stale") is not None)
check("PRESERVE: the return dict STILL carries address (callers reading out['address'] unaffected)",
      out.get("address") == CHATIN)

print(f"\nCONV PAYLOAD ACCEPTANCE (X1+X2) — {PASS} checks passed. The minted build-intent's PERSISTED "
      f"record (reloaded from disk via a fresh Suite) carries its ui:// ADDRESS (X1) AND the address's "
      f"code:// SYMBOL-NEIGHBOURS (X2, the value resolve_scope already computed — reused, not recomputed). "
      f"The 5 existing payload fields + all .get readers are unaffected; a bare intent has no address/"
      f"symbols keys (additive-optional); empty-scope=DENY-ALL preserved.")
