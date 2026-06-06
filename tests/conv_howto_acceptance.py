"""tests/conv_howto_acceptance.py — D1 · the FOUNDATIONAL HOW-TO / AFFORDANCE stratum.

WHAT D1 IS (the foundational stratum of the Operable Interface):
the "what-is-this / what-can-I-do / how-do-I-change-it" help that resolves AT a `ui://` address — the
ground every other operability affordance stands on. It is built REUSE-ONLY (no parallel store/system),
in THREE pieces:

  1. THE DATA — an optional `howto` field on the `ui://` address record. Plumbed the way the RHM scan
     identified: addresses.json record → UnionAddressRecord/from_corpus → the corpus-element union-extras
     whitelist (row[5]['howto']) → readable from the live UI_REGISTRY. A few real addresses are SEEDED
     with howto text (proof the field carries end-to-end).

  2. THE RESOLVER — `_r2_howto_at(address, now)`: a NEW R2 gather stratum mirroring `_r2_events_at`,
     wired into `_r2_gather` per-ancestor, PIN-PERSISTENT (no recency decay — emitted pinned=True with
     ts=now re-stamped EVERY gather, so recency = exp(0) = 1 through the EXISTING scorer; no scorer edit),
     FLOOD-PROOF (truncated at R2_HOWTO_MAX before scoring; the per-turn R2_BUDGET cap still applies),
     through the SAME dedup/score/cap as every other item. Architected MODE-PARAMETERIZABLE (E1 later),
     NOT hardwired per-element (Tim's correction): resolution is generic over any address via the
     registry, never a per-address branch.

  3. THE COMPOSED RESOLVER — `address_help(ui_addr)`: joins the THREE legs into one bundle —
     what-this-is (`_describe_ui_address` → the represents/feature label) + how-to-change (`resolve_scope`
     → `blast_radius`) + how-to-use (the new `howto`) — DEGRADING CLEAN when a leg is absent.

WHAT THIS PROVES (by USE — real Suite, real corpus registry, no live model):
  A. an address with `howto` resolves it (the data plumbs corpus → registry → `_registry_howto_for`).
  B. `_r2_howto_at` gathers it PIN-PERSISTENT (recency does not decay over time) and within R2_BUDGET
     (flood-proof: a huge howto is truncated AND never evicts the operator's own locus comment).
  C. `address_help(addr)` JOINS the three legs.
  D. degrade clean when a leg is absent (a bare/unauthored address — no how-to-use leg, no crash;
     a malformed address fails LOUD).

COMPANY_TEST_RUN is set for inbox-hygiene parity with the sibling suites.
"""
import os, sys, tempfile, shutil
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_TEST_RUN"] = "1"

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    if cond:
        PASS += 1
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}")
        raise SystemExit(1)


def fresh_suite():
    reg = NodeRegistry()
    reg.discover([NODES])
    return Suite(FsStore(tempfile.mkdtemp(prefix="howto-")), reg)


# A real SEEDED corpus address (design/_system/addresses.json carries `howto` on these). If the seed
# changes, pick any address whose corpus entry has a `howto` field — the test reads from the registry,
# never hardcodes the text.
SEEDED = "ui://toolbar/run"
# A real corpus address that authors NO howto (the clean how-to-use absent leg).
UNAUTHORED = "ui://toolbar/portal"

print("D1 · how-to / affordance stratum")

# ── A · THE DATA: howto plumbs corpus → registry ────────────────────────────────────────────────
su = fresh_suite()
howto = su._registry_howto_for(SEEDED)
check("A1: a SEEDED address resolves its authored howto from the registry (corpus → row[5] → read)",
      isinstance(howto, str) and len(howto) > 0)
check("A2: an UNAUTHORED address resolves None (honest absence, not a fabricated help)",
      su._registry_howto_for(UNAUTHORED) is None)
# fail-loud on a malformed address (the S0 grammar gate)
malformed_raised = False
try:
    su._registry_howto_for("not-a-ui-address")
except Exception:
    malformed_raised = True
check("A3: a MALFORMED address fails LOUD (S0 grammar gate), never a silent empty",
      malformed_raised)

# ── B · THE RESOLVER: _r2_howto_at — pin-persistent + flood-proof, through the real gather/cap ──────
now = datetime(2026, 1, 1, tzinfo=timezone.utc)
items = su._r2_howto_at(SEEDED, now=now)
check("B1: _r2_howto_at returns one item for a seeded address", len(items) == 1)
it = items[0]
check("B2: the item carries kind='howto' (NOT 'event' — so _r2_dedup pass-2 never mangles it)",
      it.get("kind") == "howto")
check("B3: the item is PINNED (pinned=True → the R2_PIN_WEIGHT bonus, the pin-persistence mechanism)",
      it.get("pinned") is True)
check("B4: the item carries NO internal '_raw' key (so _r2_dedup pass-1 keeps it unconditionally)",
      "_raw" not in it)
check("B5: the item ts == the gather `now` (re-stamped each gather → recency = exp(0) = 1, never decays)",
      it.get("ts") == now.isoformat())
check("B6: _r2_howto_at returns [] for an UNAUTHORED address (clean degrade)",
      su._r2_howto_at(UNAUTHORED, now=now) == [])

# PIN-PERSISTENT proven by USE: the howto's score does NOT decay as time advances, BECAUSE the ts is
# re-stamped to `now` on every gather. An ordinary (non-pinned, fixed-ts) item's recency would decay
# toward 0 over 30 days; the howto's stays at recency 1.
later = now + timedelta(days=30)
g_now = su._r2_gather(SEEDED, now=now)
g_later = su._r2_gather(SEEDED, now=later)
howto_now = [x for x in g_now if x.get("kind") == "howto"][0]
howto_later = [x for x in g_later if x.get("kind") == "howto"][0]
score_now = su._r2_score(howto_now, SEEDED, now)
score_later = su._r2_score(howto_later, SEEDED, later)
check("B7: PIN-PERSISTENT — the howto's score is IDENTICAL 30 days later (no recency decay)",
      abs(score_now - score_later) < 1e-9 and score_now > 0)

# FLOOD-PROOF: a giant howto is TRUNCATED at R2_HOWTO_MAX (legible marker), so it cannot blow the window;
# AND it does NOT evict the operator's own locus comment — both coexist in the bounded R2_BUDGET slice.
su2 = fresh_suite()
giant = "X" * (su2.R2_HOWTO_MAX * 5)
# monkey-seed a giant howto onto a real registry row's extras (DATA injection — proves the bound, not a
# new code path): mutate the loaded UI_REGISTRY row's union-extras for this test instance only.
patched = False
new_registry = []
for row in su2.UI_REGISTRY:
    if row[0] == SEEDED and len(row) > 5:
        extras = dict(row[5]); extras["howto"] = giant
        new_registry.append((row[0], row[1], row[2], row[3], row[4], extras))
        patched = True
    else:
        new_registry.append(row)
su2.UI_REGISTRY = new_registry
check("B8 (setup): patched a giant howto onto the seeded row", patched)
gi = su2._r2_howto_at(SEEDED, now=now)[0]
check("B9: FLOOD-PROOF — a giant howto is TRUNCATED at R2_HOWTO_MAX with a legible marker (not silent)",
      len(gi["text"]) <= su2.R2_HOWTO_MAX + 64 and "truncated" in gi["text"])

# the howto does NOT starve the operator's own comment: attach a comment at the locus, gather+cap, assert
# BOTH survive the bounded window.
su2.ingest_comment(SEEDED, "OPERATOR: remember to check the cache before this run", source="operator")
capped = su2._r2_score_and_cap(su2._r2_gather(SEEDED, now=now), SEEDED, now)
total = sum(len(x.get("text", "") or "") for x in capped)
kinds = {x.get("kind") for x in capped}
check("B10: within R2_BUDGET — the capped locus slice never exceeds the budget",
      total <= su2.R2_BUDGET)
check("B11: FLOOD-PROOF — the operator's own comment SURVIVES alongside the pin-persistent howto "
      "(the howto grounds, it does not starve the window)",
      "howto" in kinds and "annotation" in kinds)

# ── C · THE COMPOSED RESOLVER: address_help joins the three legs ─────────────────────────────────
su3 = fresh_suite()
bundle = su3.address_help(SEEDED)
check("C1: address_help returns the bundle for the address", bundle.get("address") == SEEDED)
check("C2: LEG what-this-is is present (the represents/feature label, via _describe_ui_address)",
      bool(bundle.get("what_this_is")) and "(unregistered)" not in bundle["what_this_is"])
check("C3: LEG how-to-change is present (resolve_scope → blast_radius join)",
      bundle["how_to_change"].get("blast_radius") is not None
      or bundle["how_to_change"].get("scope"))
check("C4: LEG how-to-use is present (the new howto field)",
      bundle.get("how_to_use") is not None and len(bundle["how_to_use"]) > 0)
check("C5: legs_present reports all three legs resolved for a fully-described address",
      bundle["legs_present"] == {"what_this_is": True, "how_to_change": True, "how_to_use": True})

# ── D · DEGRADE CLEAN when a leg is absent ───────────────────────────────────────────────────────
# An address with NO authored howto → the how-to-use leg is absent (None), the others still resolve, no crash.
bundle_u = su3.address_help(UNAUTHORED)
check("D1: DEGRADE — an UNAUTHORED address yields how_to_use=None (the leg cleanly absent)",
      bundle_u.get("how_to_use") is None)
check("D2: DEGRADE — the other legs still resolve (what-this-is present), no crash, a clean partial",
      bundle_u["legs_present"]["how_to_use"] is False
      and bundle_u["legs_present"]["what_this_is"] is True)
# A malformed address fails LOUD (it is a real error, not a missing leg).
help_raised = False
try:
    su3.address_help("garbage-not-ui")
except Exception:
    help_raised = True
check("D3: DEGRADE-vs-ERROR — a MALFORMED address fails LOUD (S0 gate), never a silent half-bundle",
      help_raised)

print(f"\n{PASS} checks PASSED — D1 how-to/affordance stratum proven by use.")
