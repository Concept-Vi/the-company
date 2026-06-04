"""tests/address_grammar_acceptance.py — S0 · CONTRACT.0 — ONE canonical ui:// grammar.

The load-bearing seam of the Interactive Addressed Surface. Two non-interoperable grammars
existed:
  • Corpus (design/_system/addresses.json): element-level, region-keyed, list-capabilities,
    `ui://<region>/<element>` (+ region-only forms like `ui://inbox`).
  • Live app (Suite.UI_REGISTRY): region-level, KIND-keyed, bool-object capabilities,
    `ui://<kind>/<ref>` (e.g. `ui://chrome/inbox`).

S0 reconciles them into ONE grammar by making the grammar STRUCTURAL (the segment shape) and
putting the kind/region SEMANTICS in the per-address RECORD. This suite proves:
  1. The canonical grammar parses every address on BOTH sides (corpus element/region forms +
     live kind forms).
  2. Every address on BOTH sides projects to the union record and passes the record-shape teeth
     (valid kind ∈ {chrome,field,canvas,panel,ext}, non-empty region, canonical bool-capabilities).
  3. The conformance check PASSES (zero problems) for the corpus AND the live registry — each side
     validated INDIVIDUALLY (it does NOT require the two address sets to match; an address on one
     side only is an orphan to reconcile, not a fabrication — rule 8).
  4. Capabilities normalize list→bool-object, mapping the corpus `driven`/`driven-read-only` →
     `drivenReadOnly`, and an UNKNOWN capability fails LOUD (rule 4 — never silent-dropped).
  5. The existing /ui_info consumers are PRESERVED (build_ui_info still serves the v1 shape).
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from contracts.ui_info import (
    ADDRESS_KINDS,
    CAPABILITY_FIELDS,
    UnionAddressRecord,
    conform_corpus,
    conform_live,
    normalize_capabilities,
    parse_ui_address,
    validate_address_record,
)

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


NODES = os.path.join(ROOT, "nodes")
store = FsStore(os.path.join(tempfile.mkdtemp(prefix="grammar-"), "store"))
reg = NodeRegistry(); reg.discover([NODES])
suite = Suite(store, reg, nodes_dir=NODES)

# ── 1. the grammar parses every shape both sides use ──────────────────────────
for addr in ("ui://inbox/build-review",      # corpus element form
             "ui://inbox",                     # corpus region-only form
             "ui://chrome/inbox",              # live kind form
             "ui://canvas/node-7",             # live canvas instance
             "ui://inbox/build-review/@stuck", # @state form (criteria)
             "ui://inbox/build-review@stuck"): # @state form (corpus _what)
    p = parse_ui_address(addr)
    check(f"grammar parses {addr!r} → {p['segments']} state={p['state']}", p["segments"])

# malformed → fail loud (rule 4)
for bad in ("inbox/x", "ui://", "run://g/n", "ui:///"):
    raised = False
    try:
        parse_ui_address(bad)
    except (ValueError, TypeError):
        raised = True
    check(f"malformed {bad!r} raises (fail loud)", raised)

# ── 2. capabilities normalize list→bool-object; vocabulary maps; unknown fails loud ──
norm = normalize_capabilities(["pointable", "driven", "driven-read-only"])
check("corpus list normalizes to bool-object", isinstance(norm, dict))
check("every canonical capability field is present", all(f in norm for f in CAPABILITY_FIELDS))
check("`driven` maps to drivenReadOnly", norm["drivenReadOnly"] is True)
check("`pointable` is True, `openable` absent→False", norm["pointable"] and not norm["openable"])
unknown_raised = False
try:
    normalize_capabilities(["teleportable"])
except ValueError:
    unknown_raised = True
check("unknown capability fails LOUD (never silent-dropped)", unknown_raised)

# ── 3. conformance: the CORPUS validates against the one grammar+record ──────
corpus_path = os.path.join(ROOT, "design", "_system", "addresses.json")
with open(corpus_path, encoding="utf-8") as f:
    corpus_addresses = json.load(f).get("addresses", {})
check("corpus addresses.json loaded", len(corpus_addresses) > 0)
cc = conform_corpus(corpus_addresses)
check(f"CORPUS conforms — zero problems (problems: {cc['problems'][:3]})", not cc["problems"])
check(f"corpus produced {len(cc['records'])} union records",
      len(cc["records"]) == len(corpus_addresses))
# every corpus record carries kind ∈ ADDRESS_KINDS + non-empty region
for addr, r in cc["records"].items():
    assert r["kind"] in ADDRESS_KINDS, f"{addr} kind {r['kind']} not in {ADDRESS_KINDS}"
    assert r["region"], f"{addr} empty region"
check("every corpus record: kind∈ADDRESS_KINDS + non-empty region", True)

# ── 4. conformance: the LIVE UI_REGISTRY validates against the SAME grammar+record ──
cl = conform_live(suite.UI_REGISTRY)
check(f"LIVE UI_REGISTRY conforms — zero problems (problems: {cl['problems'][:3]})",
      not cl["problems"])
check(f"live produced {len(cl['records'])} union records (= {len(suite.UI_REGISTRY)} rows)",
      len(cl["records"]) == len(suite.UI_REGISTRY))
# the live kind-form address keys are present (NOT migrated to region-first — that is S1)
check("live ui://chrome/inbox present (string NOT migrated by S0)",
      "ui://chrome/inbox" in cl["records"])
check("live ui://canvas/* present", "ui://canvas/*" in cl["records"])

# ── 5. the union record is the UNION (optional join fields), validated by its teeth ──
ur = UnionAddressRecord.from_corpus("ui://inbox/build-review",
                                    corpus_addresses["ui://inbox/build-review"])
check("corpus record carries represents (the feature join)", ur.represents == "WIRE-review")
check("corpus record carries code (the code:// join, for S3)",
      ur.code == "runtime/suite.py:review_verdicts")
check("record-shape teeth pass for a good record", validate_address_record(ur) == [])
# a record with a bad kind is caught by the teeth (not the permissive string grammar)
bad = UnionAddressRecord(address="ui://x/y", kind="bogus", region="x")
check("bad kind caught by the record teeth", any("kind" in p for p in validate_address_record(bad)))

# ── 6. PRESERVES — the existing /ui_info serializer still works (v1 shape unchanged) ──
served = suite.ui_info()
check("build_ui_info still serves the 7 live entries", len(served) == len(suite.UI_REGISTRY))
check("served entries keep the v1 ref keys (inbox present)", "inbox" in served)
check("served entry keeps capabilities bool-object", served["inbox"]["capabilities"]["pointable"])

print(f"\nADDRESS GRAMMAR ACCEPTANCE — {PASS} checks passed. "
      f"ONE canonical grammar: structural string + semantic record; "
      f"corpus + live both conform; live strings NOT migrated (that is S1).")
