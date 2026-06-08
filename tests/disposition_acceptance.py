"""tests/disposition_acceptance.py — the finding store + the disposition overlay (Group C1-C2).

The substrate spine, by use. Proves the own/reflect split in the store:
  · DETECTION is re-derivable + append-only — a finding record rides a dedicated address-keyed log
    (mirrors append_annotation); re-detecting re-appends (own/reflect: re-derive freely).
  · DISPOSITION is OWNED + mutable — a last-wins overlay keyed by the (kind,address) finding handle
    (mirrors the pin overlay); it is NOT a mutation of the append-only finding record, and it SURVIVES a
    re-detection (the decision persists even as detection re-runs). A disposition is a micro-ADR.

Verified by use: write → read-back → persistence-survives-reload → disposition last-wins → disposition
survives re-detection. No model, no engine — pure store primitives (store constitution: turns an address
into bytes and back; never calls a model).
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore

PASS = 0
def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")

root = os.path.join(tempfile.mkdtemp(prefix="disposition-"), "store")
store = FsStore(root)

# ── C1 · the finding record (detection — append-only, address-keyed) ─────────────────────────────────
f1 = store.append_finding({"kind": "unwired-route", "address": "code://bridge/api_knobs",
                           "state": "built-no-caller", "evidence": "no caller in FE or tests",
                           "source": "structural"})
check("append_finding returns the record with a ts stamped", "ts" in f1 and f1["kind"] == "unwired-route")
got = store.findings_for("code://bridge/api_knobs")
check("findings_for returns the finding at its address", len(got) == 1 and got[0]["kind"] == "unwired-route")
check("a different address has no findings", store.findings_for("code://other/thing") == [])

# persistence-survives-reload — a SECOND store over the same root sees the first's writes
store2 = FsStore(root)
check("persistence survives reload (2nd store sees the finding)",
      len(store2.findings_for("code://bridge/api_knobs")) == 1)

# ── C2 · the disposition overlay (OWNED — last-wins, keyed by (kind,address), separate from the record) ─
store.append_disposition("unwired-route", "code://bridge/api_knobs", "to_wire", reason="needs an FE caller", by="coherence")
d = store.disposition_for("unwired-route", "code://bridge/api_knobs")
check("disposition_for resolves the disposition", d and d["disposition"] == "to_wire" and d["reason"] == "needs an FE caller")

# last-wins: a later disposition overrides (a decision changed)
store.append_disposition("unwired-route", "code://bridge/api_knobs", "by-design", reason="internal entry point", by="tim")
d2 = store.disposition_for("unwired-route", "code://bridge/api_knobs")
check("disposition is last-wins (by-design overrides to_wire)", d2["disposition"] == "by-design" and d2["by"] == "tim")

# an undispositioned finding resolves to None (the additive default — open)
check("an undispositioned finding has no disposition (open)",
      store.disposition_for("unwired-route", "code://other/route") is None)

# ── the own/reflect property: re-DETECTION re-appends the finding, but the DISPOSITION persists ────────
store.append_finding({"kind": "unwired-route", "address": "code://bridge/api_knobs",
                      "state": "built-no-caller", "evidence": "re-detected this tick", "source": "structural"})
threads = store.findings_for("code://bridge/api_knobs")
check("re-detection appends (detection is re-derivable, append-only — 2 records now)", len(threads) == 2)
d3 = store.disposition_for("unwired-route", "code://bridge/api_knobs")
check("the DISPOSITION survives re-detection (owned, not recomputed — still by-design)",
      d3["disposition"] == "by-design")

print(f"\nALL {PASS} CHECKS PASS — finding store (detection, re-derivable) + disposition overlay (owned, "
      f"last-wins, survives re-detection). The own/reflect split, proven in the store by use.")
