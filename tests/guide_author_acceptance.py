"""tests/guide_author_acceptance.py — the GUIDE-author (Spec 3 reshaped) + its gates.

Proves, BY MECHANISM (a STUB composer — no live model, no git writes), that the author:
  1. FRESHNESS — compute_source_hash is deterministic over content-resolvable sources, and matches the
     seed guide's recorded source_hash (so the seed is NOT stale); a wrong hash IS stale.
  2. ABORT-ON-COLD — grounding that resolves to no content RAISES (never an invented guide).
  3. PROPOSE-NOT-CLOBBER — re-authoring an EXISTING guide returns action='proposed' and writes NOTHING.
  4. EMPTY-NARRATIVE fail-loud — a compose that returns empty RAISES (never an empty guide).
  5. DRY-RUN — returns the rendered source + spec without writing; the source GATES clean.
  6. GROUNDED-BY-CONSTRUCTION — the authored spec carries a real source_hash + the target + grounding.

The model-compose step (model_composer) is INJECTED here as a stub; composing on a real model is the
lead-verify slice (not exercised here — never green-painted).

LAWS proven: grounding-mandatory · no silent failures (cold/empty RAISE) · propose-not-clobber default ·
the floor (a guide is read, never executed) · reuse (author rides create_guide/render — no parallel path).
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from store.fs_store import FsStore                                          # noqa: E402
from runtime.suite import Suite                                            # noqa: E402
from runtime.registry import NodeRegistry                                  # noqa: E402
from runtime.guides import GuideRegistry                                   # noqa: E402
from runtime import guide_author as ga                                     # noqa: E402

SEED = "using_skills"
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def raises(label, exc, fn):
    try:
        fn()
    except exc:
        check(label, True)
        return
    check(label, False)


# A Suite over the REAL repo dirs, but a TEMP store (skill:// resolves via the file-discovered registry,
# not the store — so no store data needed; create paths are NOT exercised, so the repo stays clean).
suite = Suite(FsStore(tempfile.mkdtemp(prefix="ga-store-")),
              NodeRegistry().discover([os.path.join(ROOT, "nodes")]), nodes_dir=os.path.join(ROOT, "nodes"))
store = suite.store
seed = GuideRegistry().discover([os.path.join(ROOT, "guides")])[SEED]

# 1 · FRESHNESS
h1 = ga.compute_source_hash(store, ["skill://summarize"])
h2 = ga.compute_source_hash(store, ["skill://summarize"])
check("compute_source_hash is deterministic (same sources → same hash)", h1 == h2)
check("compute_source_hash(['skill://summarize']) matches the seed guide's recorded source_hash",
      h1 == seed.source_hash)
check("the seed guide is NOT stale (recorded hash == recomputed)", ga.is_stale(store, seed) is False)
# provenance-only addresses in grounded_from don't change the hash (only content-resolvable do)
check("file:// provenance addresses are skipped — hash unchanged vs skill:// alone",
      ga.compute_source_hash(store, ["skill://summarize", "file://skills/AGENTS.md"]) == h1)


class _FakeStale:
    source_hash = "0000deadbeef0000"
    grounded_from = ["skill://summarize"]


check("a guide whose recorded hash != recomputed IS stale", ga.is_stale(store, _FakeStale()) is True)


class _NoHash:
    source_hash = None
    grounded_from = ["skill://summarize"]


check("a guide with NO recorded source_hash is treated as stale (can't prove fresh)",
      ga.is_stale(store, _NoHash()) is True)

# 2 · ABORT-ON-COLD
raises("compute_source_hash RAISES when nothing resolves to content (abort-on-cold)",
       ga.GuideAuthorError, lambda: ga.compute_source_hash(store, ["file://nope", "project://nope"]))
raises("author_guide RAISES on cold grounding (no content source)",
       ga.GuideAuthorError,
       lambda: ga.author_guide(suite, "skill://summarize", ["file://nope"],
                               compose=lambda t, s: "x", dry_run=True))

# 3 · PROPOSE-NOT-CLOBBER (re-author the EXISTING seed → proposed, no write)
res = ga.author_guide(suite, "skill://summarize", ["skill://summarize"],
                      guide_id=SEED, compose=lambda t, s: "# Re-authored body\nnew narrative.",
                      on_existing="propose")
check("re-authoring an EXISTING guide returns action='proposed' (no write)", res["action"] == "proposed")
check("the proposal carries the would-write source + the current content (a diff to review)",
      "would_write" in res and "current_content" in res and res["current_content"] == seed.content)
check("propose did NOT change the live guide file (still the original content on disk)",
      GuideRegistry().discover([os.path.join(ROOT, "guides")])[SEED].content == seed.content)

# 4 · EMPTY-NARRATIVE fail-loud
raises("author_guide RAISES when compose returns an empty narrative (never an empty guide)",
       ga.GuideAuthorError,
       lambda: ga.author_guide(suite, "skill://summarize", ["skill://summarize"],
                               compose=lambda t, s: "   ", dry_run=True))

# 5 · DRY-RUN (returns a gated source, writes nothing)
dry = ga.author_guide(suite, "skill://summarize", ["skill://summarize"],
                      guide_id="using_summarize_probe",
                      compose=lambda t, s: "# Probe guide\nGrounded narrative for " + t + ".",
                      dry_run=True)
check("dry_run returns action='dry_run' with a rendered source + spec", dry["action"] == "dry_run" and "GUIDE = {" in dry["source"])
from runtime import authoring as _auth                                      # noqa: E402
check("the dry_run source GATES clean (would discover as a real guide)",
      _auth.gate_entry_source("using_summarize_probe", dry["source"], kind="guide") is None)

# 6 · GROUNDED-BY-CONSTRUCTION (the authored spec carries hash + target + grounding)
check("the authored spec carries a real source_hash, the target, and the grounding",
      dry["spec"]["source_hash"] == h1 and dry["spec"]["target"] == "skill://summarize"
      and dry["spec"]["grounded_from"] == ["skill://summarize"])

# staleness_report scans the live guides
rep = ga.staleness_report(suite)
check("staleness_report returns a row per live guide (incl. the seed, not stale)",
      any(r["guide_id"] == SEED and r["stale"] is False for r in rep))

print(f"\nPASS — {PASS} checks")
