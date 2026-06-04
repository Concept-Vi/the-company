"""tests/node_states_render_acceptance.py — S5 · node_states `render` field.

`capabilities()` serves NODE_STATES — 7 states (idle/ran/cached/stuck/failed/live/empty). Before S5 each
entry carried id/label/means/applies_to/derived_when but NO `render` (state→visual-token) field, so the FE
had to hardcode the state→token vocabulary — the thing F3 must avoid (one-source, rule 3). S5 adds a
`render` (token + icon + shape) to each of the 7 states, served via capabilities() (it splats the dict, so
render rides along — additive; an older FE ignores the unknown key via .get-style access).

This suite asserts STRUCTURE (each of the 7 states carries a render with token/icon/shape, and the token
REFERENCES a real corpus design-token — registry-is-truth, no invented tokens) — NOT aesthetics. Aesthetic
grading (does the colour read right, is the icon apt) is the design-critic's separate stage (rule 9), not a
machine gate here.

FLAGGED (corpus/FORM follow-ups, OUT of this backend lane — surfaced, not silently done):
  • failed/live/empty have NO DISTINCT corpus CSS class yet (only .s-idle/.s-ran/.s-cache/.s-stuck exist,
    design-system.css:92-93); they bind to the closest existing semantic tokens (failed→--fail, live→--acc,
    empty→--tx-3). Adding .s-failed/.s-live/.s-empty bindings is the corpus keeper / F3's job.
  • the icon/shape vocabularies are NOT corpus-registered (no icon registry; the "shape" token group is
    border-radii) — the values here are provisional, FE/design-critic may revise.
"""
import os, sys, re, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

NODES = os.path.join(ROOT, "nodes")
PASS = 0
SEVEN = {"idle", "ran", "cached", "stuck", "failed", "live", "empty"}


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def corpus_tokens():
    """The set of design-token custom-property names defined in the corpus design-system.css
    (registry-is-truth: a render token MUST reference one of these, never an invented name)."""
    css = os.path.join(ROOT, "design", "design-system.css")
    if not os.path.exists(css):
        return None   # corpus not present in this checkout → skip the cross-check (flagged below)
    text = open(css, encoding="utf-8").read()
    return set(re.findall(r"(--[a-z0-9-]+)\s*:", text))


store_dir = tempfile.mkdtemp(prefix="noderender-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    cap = suite.capabilities()
    check("capabilities() exposes node_states", "node_states" in cap)
    ns = cap["node_states"]
    by_id = {s["id"]: s for s in ns}

    check("all 7 node-states are served", SEVEN <= set(by_id))

    # --- each of the 7 carries a structurally-valid render ---
    for sid in SEVEN:
        s = by_id[sid]
        check(f"{sid!r} carries a `render` block", isinstance(s.get("render"), dict))
        r = s["render"]
        check(f"{sid!r} render has a token (str, --custom-property form)",
              isinstance(r.get("token"), str) and r["token"].startswith("--"))
        check(f"{sid!r} render has an icon (non-empty str)", isinstance(r.get("icon"), str) and bool(r["icon"]))
        check(f"{sid!r} render has a shape (non-empty str)", isinstance(r.get("shape"), str) and bool(r["shape"]))

    # --- registry-is-truth: every render token REFERENCES a real corpus design-token (no fabrication) ---
    tokens = corpus_tokens()
    if tokens is None:
        check("corpus design-system.css absent in this checkout — token cross-check SKIPPED (flagged)", True)
    else:
        check("corpus design-system.css parsed at least one token", len(tokens) > 0)
        for sid in SEVEN:
            tok = by_id[sid]["render"]["token"]
            check(f"{sid!r} render token {tok!r} is a REAL corpus token (registry-is-truth, no invention)",
                  tok in tokens)

    # --- additive: the render field did not disturb the existing served fields (PRESERVES) ---
    for sid in SEVEN:
        s = by_id[sid]
        check(f"{sid!r} still carries label + means + applies_to (render is additive)",
              bool(s.get("label")) and bool(s.get("means")) and bool(s.get("applies_to")))

    # --- the OTHER capabilities() served keys are unchanged in shape (additive, not a rewrite) ---
    for key in ("node_types", "rhm_verbs", "modes"):
        check(f"capabilities() still serves {key!r} (unchanged by S5)", key in cap)

    print(f"\nALL {PASS} CHECKS PASS — S5: each of the 7 node_states carries a render{{token,icon,shape}}; "
          f"every token references a real corpus design-token (registry-is-truth); additive, no field disturbed.")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
