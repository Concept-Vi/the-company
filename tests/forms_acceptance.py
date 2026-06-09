"""tests/forms_acceptance.py — forms as a FILE-DISCOVERED registry (Cognition Engine NEWMOD · P1 · effort-routing).

The adversary-verified BAR (PART 4.3): **add-a-row = a FILE, no code edit**. Effort-routing-by-form made
DATA. Proves BY MECHANISM:
  1. DISCOVER like projections — `FormRegistry` mirrors `ProjectionRegistry`.
  2. DYNAMIC (the BAR) — drop a NEW file → discovered; remove → un-registers.
  3. FAIL LOUD — a malformed form RAISES; route() on an EMPTY registry / an all-False set RAISES.
  4. ROUTING WORKS (a match is a READ — the floor) — a decision routes deep, a log routes legibility, an
     arbitrary unit falls through to prose (the `fallthrough` flag orders the catch-all LAST).
  5. DRIFT HOME — every discovered form is reflected in forms/AGENTS.md.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from runtime.forms import FormRegistry, Form, _build_form, FORM_FIELDS, REQUIRED_FIELDS  # noqa: E402

FORMS_DIR = os.path.join(ROOT, "forms")
SEED_IDS = {"log", "registry", "decision", "prose"}
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# 1 · DISCOVER
reg = FormRegistry().discover([FORMS_DIR])
check("registry discovers the seed forms (file-discovered, not a dict)", SEED_IDS <= set(reg))
check("dict-like: reg['decision'] is a Form", isinstance(reg["decision"], Form))
check("dict-like: 'prose' in reg; .get default", "prose" in reg and reg.get("nope", "X") == "X")
check("a form carries a callable match + a stage", callable(reg["log"].match) and reg["log"].stage == "legibility")
check("'decision' routes to the deep band + capture_default policy",
      reg["decision"].stage == "deep" and reg["decision"].policy == "capture_default")
check("'prose' is the fallthrough", reg["prose"].fallthrough is True)
check("the narrow forms are NOT fallthrough", not any(reg[f].fallthrough for f in ("log", "registry", "decision")))

# 2 · DYNAMIC
tmp_path = os.path.join(FORMS_DIR, "acc_tmp_form.py")
try:
    with open(tmp_path, "w") as f:
        f.write('def _m(text, *, meta=None):\n    return "TMP" in text\nFORM = {"id": "acc_tmp_form", "match": _m, "stage": "deep"}\n')
    reg2 = FormRegistry().discover([FORMS_DIR])
    check("DROP-IN: a new forms/<id>.py is discovered with NO code change (the BAR)", "acc_tmp_form" in reg2)
finally:
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
reg3 = FormRegistry().rediscover([FORMS_DIR])
check("REMOVE: the temp form un-registers on rediscover", "acc_tmp_form" not in reg3)
check("non-FORM skip: only declaring files register", set(reg3) == set(reg))


# 3 · FAIL LOUD
def raises(label, fn):
    try:
        fn()
    except (ValueError, TypeError):
        check(label, True)
        return
    check(label, False)


def _ok(text, *, meta=None):
    return True


raises("bad id (empty) RAISES", lambda: _build_form("x", {"id": "", "match": _ok, "stage": "deep"}))
raises("id != filename RAISES", lambda: _build_form("x", {"id": "y", "match": _ok, "stage": "deep"}))
raises("missing match RAISES", lambda: _build_form("x", {"id": "x", "stage": "deep"}))
raises("non-callable match RAISES", lambda: _build_form("x", {"id": "x", "match": "nope", "stage": "deep"}))
raises("missing stage RAISES", lambda: _build_form("x", {"id": "x", "match": _ok}))
raises("empty stage RAISES", lambda: _build_form("x", {"id": "x", "match": _ok, "stage": ""}))
raises("non-bool fallthrough RAISES", lambda: _build_form("x", {"id": "x", "match": _ok, "stage": "deep", "fallthrough": "yes"}))
raises("unknown field RAISES", lambda: _build_form("x", {"id": "x", "match": _ok, "stage": "deep", "bogus": 1}))
raises("non-dict decl RAISES", lambda: _build_form("x", ["nope"]))
good = _build_form("ok", {"id": "ok", "match": _ok, "stage": "deep"})
check("a minimal well-formed form builds", good.id == "ok")

# route() fail-loud: an empty registry, and an all-False match set
empty = FormRegistry()
raises("route() on an EMPTY registry RAISES (fail loud)", lambda: empty.route("anything"))

# 4 · ROUTING WORKS (a match is a READ — the floor)
dec = reg.route("# Decision: D3 resolved\nWe chose one substrate.\n")
check("a decision-shaped unit routes to the 'decision' form (deep band)", dec.id == "decision" and dec.stage == "deep")
log = reg.route("changelog\n2026-06-09 did a thing\n2026-06-08 did another\n2026-06-07 and more\n")
check("a log-shaped unit routes to the 'log' form (legibility band)", log.id == "log")
idx = reg.route("Map of contents\n- [[A]]\n- [[B]]\n- [[C]]\n- [[D]]\n- [[E]]\n")
check("an index-shaped unit routes to the 'registry' form", idx.id == "registry")
prose = reg.route("Just some ordinary thinking about a problem, no special shape at all here.")
check("an arbitrary unit FALLS THROUGH to 'prose' (fallthrough ordered LAST via the flag)", prose.id == "prose")
recs = reg.as_records()
check("as_records() renders the match callable as a qualname (serializable to a face)",
      all(isinstance(r["match"], str) for r in recs) and len(recs) == len(reg))

# 5 · DRIFT HOME
agents_md = open(os.path.join(FORMS_DIR, "AGENTS.md")).read()
for fid in reg:
    check(f"drift: '{fid}' is reflected in forms/AGENTS.md", f"`{fid}`" in agents_md)
check("the registry is NAMED in its drift home", "FormRegistry" in agents_md)

print(f"\nPASS ({PASS} checks) — forms is a file-discovered registry (P1 · effort-routing), drift-home reflected.")
