"""tests/registry_authoring_marks_acceptance.py — Cognition Engine WIRING (P2 create_* + M1 marks API).

Proves BY USE, in an ISOLATED throwaway git repo (mirrors authoring_acceptance / selfmod_acceptance —
never touches the real registry dirs or git history):

  P2.1  Suite.create_<kind> for the 4 PURE-DATA corpus/cognition registries (mark_type/generation_policy/
        relation_type/ai_tic) writes a `<name>/<id>.py`, git-commits, and the entry is LIVE in its
        registry (discover sees it) — NO operator approval (declarative-direct, #58). [lifter/form carry a
        CALLABLE → code-authoring, GATED, flagged for the operator — NOT a data-create here.]
  P2.2  a MALFORMED spec is REFUSED fail-loud (the registry's OWN gate-in-tempdir bites; never written).
  P2.3  an EXISTING id is REFUSED (create_* is for a NEW entry; registry-is-truth).
  P2.4  the selects (available_inputs) ADVERTISE the live registries (a created entry appears there).
  M1.1  Suite.mark(target, mark_type) round-trips via marks_for / marks_by_type (the two retrieval keys).
  M1.2  mark with an UNKNOWN mark_type FAILS LOUD (the Suite gate; store stays dumb).
  FLOOR a create_* / mark is a DATA write (commit / store-append) — never resolve/approve/dispatch
        (asserted standing in cognition_governance_acceptance; here proven by the [self-apply]/data commit).
"""
import os
import sys
import tempfile
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.roles import RoleRegistry
from runtime.suite import Suite

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


def git(root, *args):
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, check=True).stdout.strip()


# A well-formed spec per DATA registry kind (the create_* input), and the registry-instance attr to check
# live. The 4 create_*-authorable kinds (mark_type/generation_policy/relation_type/ai_tic) — lifter/form
# are code-authoring (a callable), excluded from data-create + asserted-refused below.
GOOD = {
    "mark_type":         ({"id": "novelty", "value_shape": "float", "direction": "surface",
                           "desc": "how novel the claim is"}, "mark_type_registry"),
    "generation_policy": ({"id": "strict_caps", "rep_penalty_ladder": [1.05, 1.15, 1.3],
                           "diff_against_source": True, "temperature": 0.0,
                           "desc": "a stricter caps regime"}, "generation_policy_registry"),
    "relation_type":     ({"id": "echoes", "directed": True, "inverse": "echoed_by",
                           "label": "echoes", "desc": "a is a lossy echo of b"}, "relation_type_registry"),
    "ai_tic":            ({"id": "hedging", "markers": ["likely", "probably", "perhaps"],
                           "label": "hedging", "desc": "speculative hedging language"}, "ai_tic_registry"),
}
# the dir name per kind (the `<name>/` sibling of nodes/ the Suite writes into)
DIRS = {"mark_type": "mark_types", "generation_policy": "generation_policies",
        "relation_type": "relation_types", "ai_tic": "ai_tics"}
# a seed module per registry (so discovery has content + the dir exists in the throwaway repo). lifter/form
# carry a CALLABLE (real `def`) — confirming they are CODE, not a data row (hence not data-create-able).
SEEDS = {
    "lifters":             ("seedlift", "def _x(text, *, meta=None):\n    return {}\nLIFTER = {'id':'seedlift','extract':_x,'produces':'y'}\n"),
    "mark_types":          ("seedmark", "MARK_TYPE = {'id':'seedmark','value_shape':'float','direction':'surface'}\n"),
    "generation_policies": ("seedpol", "GENERATION_POLICY = {'id':'seedpol','rep_penalty_ladder':[1.1],'diff_against_source':False}\n"),
    "relation_types":      ("seedrel", "RELATION_TYPE = {'id':'seedrel','directed':True}\n"),
    "ai_tics":             ("seedtic", "AI_TIC = {'id':'seedtic','markers':['x'],'label':'x'}\n"),
    "forms":               ("seedform", "def _m(text, *, meta=None):\n    return True\nFORM = {'id':'seedform','match':_m,'stage':'legibility'}\n"),
}

work = tempfile.mkdtemp(prefix="reg-author-marks-")
try:
    repo = os.path.join(work, "company")
    nodes = os.path.join(repo, "nodes")
    roles = os.path.join(repo, "roles")
    os.makedirs(nodes); os.makedirs(roles)
    # the 6 registry dirs + a seed each (so the Suite discovers a non-empty registry)
    for dname, (sid, ssrc) in SEEDS.items():
        d = os.path.join(repo, dname)
        os.makedirs(d)
        open(os.path.join(d, f"{sid}.py"), "w").write(ssrc)
    subprocess.run(["git", "init", repo], capture_output=True, check=True)
    git(repo, "config", "user.email", "t@t"); git(repo, "config", "user.name", "t")
    open(os.path.join(nodes, "seed.py"), "w").write(
        "VERSION='1'\nKIND='process'\nPORTS_IN={}\nPORTS_OUT={}\ndef run(i,c): return 1\n")
    git(repo, "add", "-A"); git(repo, "commit", "-m", "baseline")
    base_head = git(repo, "rev-parse", "HEAD")

    store = FsStore(os.path.join(work, "store"))
    reg = NodeRegistry().discover([nodes])
    rreg = RoleRegistry().discover([roles])
    suite = Suite(store, reg, nodes_dir=nodes, role_registry=rreg)

    print("\n[setup] the 6 registries discovered in the throwaway repo (incl. lifter/form code-seeds)")
    ALL_REG_ATTRS = {"lifters": "lifter_registry", "mark_types": "mark_type_registry",
                     "generation_policies": "generation_policy_registry",
                     "relation_types": "relation_type_registry", "ai_tics": "ai_tic_registry",
                     "forms": "form_registry"}
    for dname, reg_attr in ALL_REG_ATTRS.items():
        seed = SEEDS[dname][0]
        check(f"setup: {dname} registry discovered the seed ({seed})", seed in getattr(suite, reg_attr))

    # ── P2.1 — create_<kind> for ALL 6 → live, committed, no approval ─────────────────────────────
    print("\n[P2.1] create_<kind> writes <name>/<id>.py + commits + LIVE (declarative-direct, no approval)")
    for kind, (spec, reg_attr) in GOOD.items():
        method = getattr(suite, f"create_{kind}")
        before = git(repo, "rev-parse", "HEAD")
        out = method(dict(spec))
        rid = spec["id"]
        # the file was written into the right dir
        expect_path = os.path.join(repo, DIRS[kind], f"{rid}.py")
        check(f"P2.1 create_{kind}: wrote {DIRS[kind]}/{rid}.py", os.path.exists(expect_path))
        # it is LIVE in the registry (discover sees it) — no surfaced item, no approval
        check(f"P2.1 create_{kind}: {rid!r} is LIVE in the registry (discover sees it, no approval)",
              out.get("live") is True and rid in getattr(suite, reg_attr))
        # it git-committed (the revertible safety net)
        after = git(repo, "rev-parse", "HEAD")
        check(f"P2.1 create_{kind}: made a git commit (revertible)", after != before)
        check(f"P2.1 create_{kind}: NOT a surfaced/approval item (returns live, not a decision id)",
              "id" in out and out.get("kind") == kind)

    # ── P2.2 — a malformed spec is REFUSED fail-loud (the registry's own gate) ────────────────────
    print("\n[P2.2] a malformed spec is REFUSED fail-loud (the registry's own gate-in-tempdir bites)")
    # each BAD spec fails the registry's OWN gate (a REQUIRED field missing / a bad value the gate checks —
    # NOT an unknown field, which _write_registry_file filters to the known FIELDS before the gate sees it).
    BAD = {
        "mark_type":         {"id": "bad_mt", "value_shape": 123, "direction": "surface"},  # value_shape not a string
        "generation_policy": {"id": "bad_pol", "rep_penalty_ladder": [1.3, 1.1], "diff_against_source": True},  # non-ascending ladder
        "relation_type":     {"id": "bad_rel"},                              # missing required directed
        "ai_tic":            {"id": "bad_tic"},                              # missing required markers/label
    }
    for kind, bad in BAD.items():
        method = getattr(suite, f"create_{kind}")
        before = git(repo, "rev-parse", "HEAD")
        raised = False
        try:
            method(dict(bad))
        except Exception:
            raised = True
        check(f"P2.2 create_{kind}: a malformed spec RAISED (refused, never written)", raised)
        # NOT written + NOT committed
        check(f"P2.2 create_{kind}: the bad file was NOT written to the live dir",
              not os.path.exists(os.path.join(repo, DIRS[kind], f"{bad['id']}.py")))
        check(f"P2.2 create_{kind}: no commit was made for the refused spec",
              git(repo, "rev-parse", "HEAD") == before)

    # ── P2.3 — an EXISTING id is refused ──────────────────────────────────────────────────────────
    print("\n[P2.3] an EXISTING id is refused (create_* is for a NEW entry; registry-is-truth)")
    raised = False
    try:
        suite.create_mark_type({"id": "novelty", "value_shape": "label"})   # created in P2.1
    except ValueError:
        raised = True
    check("P2.3 create_mark_type on an existing id RAISES (a NEW entry only)", raised)

    # ── P2.4 — the selects ADVERTISE all 6 live registries (incl. lifter/form, which only data-create skips)
    print("\n[P2.4] available_inputs advertises ALL 6 registries (a created entry appears there)")
    ai = suite.available_inputs()
    for kind, (spec, reg_attr) in GOOD.items():
        sel_key = DIRS[kind]
        check(f"P2.4 available_inputs carries '{sel_key}' and lists the created entry {spec['id']!r}",
              sel_key in ai and spec["id"] in ai[sel_key])
    # lifter/form are LISTED (governed/usable) even though they are NOT data-create-able
    check("P2.4 lifters select present (listable/usable even though not data-create-able)",
          "lifters" in ai and "seedlift" in ai["lifters"])
    check("P2.4 forms select present (listable/usable even though not data-create-able)",
          "forms" in ai and "seedform" in ai["forms"])

    # ── P2.5 — lifter/form are EXCLUDED from data-create (code-authoring, flagged) ─────────────────
    print("\n[P2.5] lifter/form are NOT data-create-able (callable row → code-authoring, flagged)")
    check("P2.5 Suite has NO create_lifter (lifter.extract is a callable — code-authoring, gated)",
          not hasattr(suite, "create_lifter"))
    check("P2.5 Suite has NO create_form (form.match is a callable — code-authoring, gated)",
          not hasattr(suite, "create_form"))
    check("P2.5 _CORPUS_REGISTRIES (the create table) scopes to the 4 data kinds only",
          set(suite._CORPUS_REGISTRIES) == {"mark_type", "generation_policy", "relation_type", "ai_tic"})
    # defense-in-depth: the shared helper fail-louds if ever handed a callable-bearing row
    raised = False
    try:
        suite._write_registry_file("mark_type", {"id": "cbtest", "value_shape": lambda x: x, "direction": "surface"})
    except ValueError:
        raised = True
    check("P2.5 _write_registry_file fail-louds on a CALLABLE field (data-create can't author code)", raised)

    # ── M1 — the marks API (mark / marks_for / marks_by_type) ─────────────────────────────────────
    print("\n[M1] the marks API: mark → marks_for / marks_by_type round-trip (the two retrieval keys)")
    # use a REGISTERED mark_type — the seed 'seedmark' (and the created 'novelty')
    rec = suite.mark("claim://doc1#span3", "seedmark", value=0.7, evidence="coined vocab", source_pass="p1")
    check("M1.1 mark() persisted a record carrying target + mark_type",
          rec.get("target") == "claim://doc1#span3" and rec.get("mark_type") == "seedmark")
    check("M1.1 marks_for(target) round-trips the mark (retrieval key #1: target)",
          len(suite.marks_for("claim://doc1#span3")) == 1)
    check("M1.1 marks_by_type(mark_type) round-trips the mark (retrieval key #2: mark_type)",
          len(suite.marks_by_type("seedmark")) == 1)
    # a SECOND mark of a DIFFERENT type on the SAME target — by-type doesn't cross
    suite.mark("claim://doc1#span3", "novelty", value=0.9)
    check("M1.1 by-type doesn't cross: marks_by_type('seedmark') still 1 (not 2)",
          len(suite.marks_by_type("seedmark")) == 1)
    check("M1.1 the target now has a 2-mark THREAD (append-only accrual)",
          len(suite.marks_for("claim://doc1#span3")) == 2)
    check("M1.1 an unmarked target → honest empty list", suite.marks_for("claim://never") == [])

    # ── M1.2 — an unknown mark_type fails loud (the Suite gate; store stays dumb) ──────────────────
    print("\n[M1.2] an unknown mark_type FAILS LOUD (the Suite gate — store.append_mark stays dumb)")
    raised = False
    try:
        suite.mark("claim://x", "not_a_registered_type")
    except ValueError:
        raised = True
    check("M1.2 mark() with an unregistered mark_type RAISES (registry-is-truth; no fabricated type)", raised)
    raised = False
    try:
        suite.marks_by_type("also_not_registered")
    except ValueError:
        raised = True
    check("M1.2 marks_by_type() with an unregistered type RAISES (a typo'd type would silently look empty)",
          raised)
    # the refused mark was NOT persisted
    check("M1.2 the refused mark was NOT written", suite.marks_for("claim://x") == [])

    # ── FLOOR — the commits are DATA/self-apply, never a build-dispatch ───────────────────────────
    print("\n[FLOOR] every create_* commit is a declarative DATA write, never a claude -p / resolve")
    log = git(repo, "log", "--format=%s", f"{base_head}..HEAD")
    check("FLOOR: all create_* commits are 'create <kind> ...' DATA commits (no [self-build] dispatch)",
          all(("create " in l) for l in log.splitlines() if l.strip()) and "[self-build]" not in log)

    print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} — {PASS} checks passed — the 4 PURE-DATA corpus/"
          "cognition registries are create_*-authorable (declarative-direct, gated, committed, LIVE); all 6 "
          "are advertised in the selects (lifter/form listable but code-authoring, flagged); the marks API "
          "round-trips by target AND mark_type with the Suite mark_type gate fail-loud. Floor held (DATA "
          "writes, never a build-dispatch).")
finally:
    import shutil
    shutil.rmtree(work, ignore_errors=True)

sys.exit(0 if ok else 1)
