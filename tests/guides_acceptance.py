"""tests/guides_acceptance.py — guides as an addressable registry (the narrative-guide face).

Tim (2026-06-28): the Company needs guides on how to USE it; he settled "one entry, two faces" — a
skill (`skill://`, the dense instruction-unit a role reads) and a guide (`guide://`, the narrative
how-to a learner reads), two projections of a target. This suite proves, BY MECHANISM (no live model
needed — purely structural), that:

  1. SCHEME additive — `guide` is in `contracts/address.py:SCHEMES` (mirrors skill/context; no
     record-shape / schema_ver change), and the older schemes are untouched.
  2. The registry DISCOVERS like skills — `GuideRegistry` mirrors `SkillRegistry`: file-discovered
     from `guides/`, dict-like, fail-loud on a malformed entry, a non-entry/`_`-file skipped; dropping
     a 2nd file registers it (the dynamic proof); removing it un-registers on rediscover.
  3. resolve_address resolves `guide://` — the seed guide resolves to its REAL declared content; an
     UNKNOWN id RAISES fail-loud (registry-is-truth, never fabricate).
  4. The GROUNDING gate — a guide with empty/absent `grounded_from` RAISES at discovery (a guide is
     authored FROM real sources or it does not exist; abort-on-cold). Same for a missing `target`.
  5. Drift — the seed guide is reflected in `guides/AGENTS.md` (the drift home).

LAWS proven: no-hardcoding (the ids live in `guides/` — discovered, never a literal) · reuse-don't-
parallel (GuideRegistry mirrors SkillRegistry, reusing _load_module; resolve_address dispatches to it,
one seam) · fail-loud (unknown id / malformed / ungrounded entry RAISES) · the floor (a guide read is a
READ — the method is `read`, not `resolve`) · grounding-mandatory.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from contracts.address import SCHEMES, scheme                               # noqa: E402
from store.fs_store import FsStore                                          # noqa: E402
from runtime.cognition import resolve_address                              # noqa: E402
from runtime.guides import GuideRegistry, GuideEntry, _build_guide          # noqa: E402

GUIDES = os.path.join(ROOT, "guides")
SEED_GUIDE = "using_skills"
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def raises(label, fn):
    try:
        fn()
    except Exception:
        check(label, True)
        return
    check(label, False)


# 1 · SCHEME additive
check("contracts.address.SCHEMES contains 'guide' (additive — mirrors skill/context)", "guide" in SCHEMES)
check("the additive precedent holds — skill/context/run/cas STILL in SCHEMES (nothing removed)",
      all(s in SCHEMES for s in ("skill", "context", "run", "cas")))
check("scheme('guide://using_skills') == 'guide' (a registered scheme, not a bare name)",
      scheme("guide://using_skills") == "guide")

# 2 · discovers like skills
reg = GuideRegistry().discover([GUIDES])
check("GuideRegistry().discover(['guides']) finds the seed guide (file-discovered, no literal)", SEED_GUIDE in reg)
check("the registry mirrors SkillRegistry (discover/rediscover/register/read present)",
      all(hasattr(reg, m) for m in ("discover", "rediscover", "register", "read")))
check("the registry is dict-like (reg[id] -> GuideEntry, id in reg, .get)",
      isinstance(reg[SEED_GUIDE], GuideEntry) and (SEED_GUIDE in reg) and reg.get("nope") is None)
seed = reg[SEED_GUIDE]
check("the seed guide carries id + content + target + grounded_from (the guide row)",
      seed.id == SEED_GUIDE and bool(seed.content) and seed.target == "skill://summarize"
      and isinstance(seed.grounded_from, list) and len(seed.grounded_from) >= 1)

# dynamic proof — drop a 2nd guide file → discovered; remove → un-registers
tmp = os.path.join(GUIDES, "_tmp_probe_guide.py")
# (use a real id == filename; '_'-prefixed files are SKIPPED, so name it without leading underscore)
probe = os.path.join(GUIDES, "tmpprobeguide.py")
try:
    with open(probe, "w") as f:
        f.write(
            "GUIDE = {'id':'tmpprobeguide','content':'probe how-to body',"
            "'target':'skill://summarize','grounded_from':['skill://summarize']}\n")
    reg2 = GuideRegistry().discover([GUIDES])
    check("dropping a 2nd guides/<id>.py FILE → it is discovered (no code change — dynamic proof)",
          "tmpprobeguide" in reg2)
    check("the dropped guide RESOLVES to its declared content (read())",
          reg2.read("tmpprobeguide") == "probe how-to body")
finally:
    os.remove(probe)
reg3 = GuideRegistry().rediscover([GUIDES])
check("removing the file → it un-registers on rediscover (mirrors SkillRegistry.rediscover)",
      "tmpprobeguide" not in reg3)

# a non-entry / _-prefixed file is SKIPPED
skipprobe = os.path.join(GUIDES, "_skipme.py")
try:
    with open(skipprobe, "w") as f:
        f.write("GUIDE = {'id':'_skipme','content':'x','target':'t','grounded_from':['g']}\n")
    reg4 = GuideRegistry().discover([GUIDES])
    check("a non-entry / _-prefixed file is SKIPPED (not registered, not raised)", "_skipme" not in reg4)
finally:
    os.remove(skipprobe)

# 3 · resolve_address resolves guide://
store = FsStore(tempfile.mkdtemp(prefix="guides-resolve-"))
check("resolve_address('guide://using_skills') resolves to the seed guide's REAL content (no raise)",
      resolve_address(store, "guide://using_skills") == seed.content)
check("the guide:// path dispatches to GuideRegistry.read (identical value — one seam, no parallel)",
      resolve_address(store, "guide://using_skills") == GuideRegistry().discover([GUIDES]).read("using_skills"))
raises("resolve_address('guide://no-such-guide') RAISES fail-loud (registry-is-truth, never fabricate)",
       lambda: resolve_address(store, "guide://no-such-guide"))

# 4 · the grounding gate + required fields (fail-loud at build)
raises("a guide with EMPTY grounded_from FAILS LOUD (the mandatory-grounding gate — abort on cold)",
       lambda: _build_guide("g", {"id": "g", "content": "x", "target": "skill://summarize", "grounded_from": []}))
raises("a guide with NO grounded_from FAILS LOUD",
       lambda: _build_guide("g", {"id": "g", "content": "x", "target": "skill://summarize"}))
raises("a guide with NO target FAILS LOUD (a guide is ABOUT something)",
       lambda: _build_guide("g", {"id": "g", "content": "x", "grounded_from": ["skill://summarize"]}))
raises("a guide with id != filename FAILS LOUD",
       lambda: _build_guide("g", {"id": "other", "content": "x", "target": "t", "grounded_from": ["s"]}))
raises("a guide with empty content FAILS LOUD",
       lambda: _build_guide("g", {"id": "g", "content": "", "target": "t", "grounded_from": ["s"]}))
raises("a guide with an UNKNOWN field FAILS LOUD (strict schema)",
       lambda: _build_guide("g", {"id": "g", "content": "x", "target": "t", "grounded_from": ["s"], "bogus": 1}))

# 5 · drift home — the seed guide is reflected in guides/AGENTS.md
with open(os.path.join(GUIDES, "AGENTS.md")) as f:
    agents = f.read()
for gid in reg:
    check(f"drift: discovered guide {gid!r} is reflected in guides/AGENTS.md (the drift home)",
          gid in agents)

# 6 · the LIVE-AUTHORING path (render + gate) — create(kind='guide') foundation, pure (no git)
from runtime import authoring as _auth                                      # noqa: E402
good = {"id": "probe_authored", "content": "A probe how-to.", "target": "skill://summarize",
        "grounded_from": ["skill://summarize"], "label": "Probe"}
src = _auth.render_entry_source(good, kind="guide")
check("render_entry_source(kind='guide') emits a module-level GUIDE dict", "GUIDE = {" in src)
check("the rendered guide GATES clean (discovers in a temp dir — reuse the real GuideRegistry)",
      _auth.gate_entry_source("probe_authored", src, kind="guide") is None)
# the rendered source actually discovers + resolves to the declared content
import tempfile as _tf, os as _os                                          # noqa: E402
_d = _tf.mkdtemp(prefix="guide-render-")
with open(_os.path.join(_d, "probe_authored.py"), "w") as f:
    f.write(src)
check("a rendered guide is discoverable + resolves to its content",
      GuideRegistry().discover([_d]).read("probe_authored") == "A probe how-to.")
# the grounding gate fires at AUTHOR time too (render refuses an ungrounded guide)
raises("render_entry_source(kind='guide') REFUSES an empty grounded_from (author-time grounding gate)",
       lambda: _auth.render_entry_source(
           {"id": "x", "content": "c", "target": "skill://summarize", "grounded_from": []}, kind="guide"))
raises("render_entry_source(kind='guide') REFUSES a missing target",
       lambda: _auth.render_entry_source(
           {"id": "x", "content": "c", "grounded_from": ["skill://summarize"]}, kind="guide"))
raises("render_entry_source(kind='guide') REFUSES an unknown field",
       lambda: _auth.render_entry_source(
           {"id": "x", "content": "c", "target": "t", "grounded_from": ["s"], "bogus": 1}, kind="guide"))

print(f"\nPASS — {PASS} checks")
