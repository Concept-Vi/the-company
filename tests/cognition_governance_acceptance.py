"""tests/cognition_governance_acceptance.py — Concurrent Cognition G9 (governance & safety, binds all).

The STANDING regression that keeps the cognition layer's safety floor true as the system grows.
Mirrors e6_governance (the app face) for the cognition face. Proves, by use + adversarially:

  C9.1  roles act only within the governance posture — a model runs ONLY inside a role (run_role);
        a role/rule cannot reach a gate-bypassing action. (The cognition layer has NO apply/dispatch
        verb of its own — its only effects are the 5 DESTINATION_KINDS, none consequential.)
  C9.2  THE unforgeable-resolve INVARIANT (R1-FOLD F6): no role / rule / _run_swarm path may emit a
        `resolve`/`approve`/`dispatch` event (the sole build-dispatch trigger — operator-only via
        resolve_surfaced). Enforced BY CONSTRUCTION (FORBIDDEN_DESTINATION_VERBS + DESTINATION_KINDS)
        AND asserted as a STANDING source-invariant so a future role-reachable verb can't open it.
  C9.3  fail loud everywhere — missing ref, missing rule input, malformed role output, bad rule all RAISE.
  C9.4  every net-new cognition registry declares a drift home + a drift assertion (so drift has teeth).
"""
import os
import sys
import re

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


from runtime import rules as _rules

# ── C9.2 — the unforgeable-resolve invariant ────────────────────────────────────────────────────
print("\n[C9.2] the claude -p / build-dispatch floor is unforgeable from the cognition layer")
check("C9.2 DESTINATION_KINDS contains NONE of resolve/approve/dispatch",
      not ({"resolve", "approve", "dispatch"} & set(_rules.DESTINATION_KINDS)))
check("C9.2 FORBIDDEN_DESTINATION_VERBS names the three dispatch triggers",
      set(_rules.FORBIDDEN_DESTINATION_VERBS) == {"resolve", "approve", "dispatch"})

# a rule that DECLARES a forbidden destination must RAISE at construction (structural, not runtime)
for verb in ("resolve", "approve", "dispatch"):
    raised = False
    try:
        _rules.Rule(id="adv", when={"op": "lit", "value": True}, destination=verb, target="x")
    except Exception:
        raised = True
    check(f"C9.2 adversarial: a rule declaring destination={verb!r} is REJECTED at construction", raised)

# STANDING SOURCE-INVARIANT: no cognition execution path emits/calls the resolve trigger. The only
# legitimate token occurrences are run_ref RESOLUTION (resolve_run_ref / resolved values), the
# FORBIDDEN list itself, and comments/docstrings. A bare resolve_surfaced/governance.resolve CALL,
# or emitting a {"kind":"resolve"} event, from cognition code would open the floor.
# Extended (2026-06-09, #51 round-1 finding): COVER the NEW cognition-reachable surfaces — the MCP
# AGENT face (`mcp_face/server.py`) and the skills/contexts registry (`runtime/skills.py`) — so a
# FUTURE edit emitting a forbidden verb on either fails loud, not just the original engine. (The floor
# already HELD on both; this guards it standing — defense-in-depth for "a future edit opens the floor".)
# Extended again (Cognition Engine NEWMOD): the CORPUS pillar surfaces — the file-discovered projections
# registry (`runtime/projections.py`) and the lineage-bearing corpus-record (`runtime/corpus.py`) — are
# cognition-reachable (a capture role produces corpus records, routed by the same engine). They are
# enrolled here for the SAME reason skills.py was (its docstring): a corpus write must stay a READ/INDEX
# (append_event telemetry), never a resolve/dispatch — so a future edit emitting a forbidden verb on
# either fails loud. (The floor already HOLDS: corpus.record is telemetry; this guards it standing.)
# Extended again (Cognition Engine WIRING, 2026-06-09): the 6 OTHER file-discovered corpus/cognition
# registries (lifters/mark_types/generation_policies/relation_types/ai_tics/forms — 719f82d) are now
# CONSUMED (create_* tools + run_role's rep_penalty ladder + the authoring selects). They are
# cognition-reachable DATA registries, enrolled here for the SAME reason projections/corpus were: reading
# a registry must stay a READ, a create_* must stay a declarative-DATA write (commit, never resolve/
# dispatch) — so a future edit emitting a forbidden verb on any of them fails loud. (They are floor-clean
# by construction; this guards them STANDING.)
COG_SOURCES = ["runtime/cognition.py", "runtime/rules.py", "runtime/roles.py",
               "mcp_face/server.py", "runtime/skills.py",
               "runtime/projections.py", "runtime/corpus.py",
               "runtime/lifters.py", "runtime/mark_types.py", "runtime/generation_policies.py",
               "runtime/relation_types.py", "runtime/ai_tics.py", "runtime/forms.py",
               # Group I — the mode-detection-rule registry: a cognition-layer registry that PRODUCES a
               # candidate mode + feeds the toggle; the floor must cover it (it emits no resolve/dispatch).
               "runtime/mode_detection_rules.py",
               # CALLER — the always-on activation tick: an executable cognition path that FIRES the H/I
               # drivers+detector; the floor must cover it (the tick is computation — no resolve/dispatch).
               "runtime/activation_driver.py",
               # GC1 — the FLOW registry: committed production lines, MCP-invoked. Executable
               # cognition paths → the floor must cover the loader AND every row (flows/*.py below).
               "runtime/flows.py",
               # GC7 — the VERDICT-PANEL registry: declared lens-seats + deterministic quorum
               # (run_panel). Dir is verdict_panels/ — panels/ is the (JSON-only) UI-panels module.
               "runtime/verdict_panels.py",
               # G3·S3a — the CHECK registry: deterministic gates as declared data (loader + rows).
               "runtime/checks.py",
               # GC15 — the OPERATOR-MEMORY registry: the system's evidence-backed memory of Tim
               # (pure data rows; loader scanned + every row below).
               "runtime/operator_memory.py",
               # Track-1 — the DIALS registry: adjustable character traits (pure data rows; values
               # persist via Suite.set_dial on the system graph).
               "runtime/dials.py"] + \
    [f"roles/{f}" for f in os.listdir("roles") if f.endswith(".py")] + \
    [f"flows/{f}" for f in os.listdir("flows") if f.endswith(".py")] + \
    [f"verdict_panels/{f}" for f in os.listdir("verdict_panels") if f.endswith(".py")] + \
    [f"operator_memory/{f}" for f in os.listdir("operator_memory") if f.endswith(".py")] + \
    [f"checks/{f}" for f in os.listdir("checks") if f.endswith(".py")] + \
    [f"dials/{f}" for f in os.listdir("dials") if f.endswith(".py")]
# coverage-regression guard: the new surfaces MUST stay scanned (so the guard can't silently shrink).
check("C9.2 the floor source-invariant COVERS the MCP agent face + the skills registry (new surfaces)",
      "mcp_face/server.py" in COG_SOURCES and "runtime/skills.py" in COG_SOURCES)
check("C9.2 the floor source-invariant COVERS the corpus pillar (projections + corpus-record)",
      "runtime/projections.py" in COG_SOURCES and "runtime/corpus.py" in COG_SOURCES)
check("C9.2 the floor source-invariant COVERS the 6 wired corpus/cognition registries "
      "(lifters/mark_types/generation_policies/relation_types/ai_tics/forms)",
      all(f"runtime/{m}.py" in COG_SOURCES for m in
          ("lifters", "mark_types", "generation_policies", "relation_types", "ai_tics", "forms")))
check("C9.2 the floor source-invariant COVERS the mode-detection-rule registry (Group I — it produces a "
      "candidate + feeds the toggle, never a resolve/dispatch)",
      "runtime/mode_detection_rules.py" in COG_SOURCES)
check("C9.2 the floor source-invariant COVERS the always-on activation caller (CALLER — the tick fires "
      "the H/I drivers+detector; computation only, never a resolve/dispatch/claude -p)",
      "runtime/activation_driver.py" in COG_SOURCES)
check("C9.2 the floor source-invariant COVERS the FLOW registry (GC1 — loader + every flows/<id>.py row; "
      "flows are repo-authored, MCP-invoked, proposes-only)",
      "runtime/flows.py" in COG_SOURCES and any(s.startswith("flows/") for s in COG_SOURCES))
floor_breach = []
for src in COG_SOURCES:
    with open(src) as fh:
        for i, line in enumerate(fh, 1):
            code = line.split("#", 1)[0]  # strip end-of-line comments
            if "resolve_surfaced" in code or "governance.resolve" in code \
               or re.search(r'["\']kind["\']\s*:\s*["\']resolve["\']', code) \
               or re.search(r'\.resolve\s*\(', code):
                floor_breach.append(f"{src}:{i}: {line.strip()[:80]}")
check("C9.2 STANDING source-invariant: NO cognition path calls resolve_surfaced/governance.resolve "
      "or emits a resolve event (only operator-only resolve_surfaced does)", not floor_breach)
if floor_breach:
    for b in floor_breach:
        print("      breach:", b)

# #58 FLOOR RECONCILE — the BUILD-DISPATCH floor, made EXPLICIT (was implicit via the resolve proxy).
# Tim's reframe (2026-06-09): AUTHORING-apply (create_role/create_skill/create_context applying a
# role/skill/context LIVE) is now ALLOWED from the agent/cognition face — the create-approval gate was
# the AI's default, NOT Tim's constraint. What MAINTAINS UNCHANGED (Tim CONFIRMED) is the wire's
# autonomous repo-mutation: NO cognition/engine/MCP path may emit `dispatch_decision` or launch the
# `claude -p` build-dispatch. We assert it as a STANDING explicit token-scan over COG_SOURCES (AST for
# CALLs — robust to docstrings/comments that legitimately DESCRIBE the floor; a code-only string-scan
# for the `claude -p` launch). The wire's own files (runtime/implement.py, the suite.py dispatch path)
# are NOT in COG_SOURCES — the build-dispatch lives there, operator-gated, never on a cognition path.
import ast as _ast
dispatch_breach = []
for src in COG_SOURCES:
    code = open(src).read()
    # AST: any CALL named dispatch_decision (the wire's autonomous dispatch) is forbidden on a cog path.
    try:
        tree = _ast.parse(code)
    except SyntaxError:
        continue
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Call):
            fn = node.func
            nm = fn.attr if isinstance(fn, _ast.Attribute) else (fn.id if isinstance(fn, _ast.Name) else None)
            if nm == "dispatch_decision":
                dispatch_breach.append(f"{src}: CALL dispatch_decision")
    # code-only string scan (strip end-of-line comments) for a `claude -p` / implement.py launch.
    code_no_comments = "\n".join(l.split("#", 1)[0] for l in code.splitlines())
    # docstrings still survive the comment-strip; but a real LAUNCH would be a subprocess/run call with
    # the string as an arg — scan for the launch invocation pattern, not the bare mention.
    if "implement.py" in code_no_comments and ("subprocess" in code_no_comments or "Popen" in code_no_comments):
        dispatch_breach.append(f"{src}: launches implement.py (the claude -p build-dispatch)")
check("C9.2/#58 the BUILD-DISPATCH floor MAINTAINS: NO cognition/engine/MCP path emits dispatch_decision "
      "or launches the claude -p build-dispatch (the wire's autonomous repo-mutation stays operator-gated)",
      not dispatch_breach)
if dispatch_breach:
    for b in dispatch_breach:
        print("      dispatch-breach:", b)

# #58 the CORRECTNESS GATE is KEPT (a malformed role/skill/context is REFUSED fail-loud, never written).
# Assert the gate functions exist + that a malformed spec is refused (not silently written) — the
# non-negotiable correctness floor that survives the authoring-apply reframe.
print("\n[C9.2/#58] authoring-apply ALLOWED + the CORRECTNESS gate KEPT (malformed refused, never written)")
from runtime import authoring as _auth
check("#58 the role correctness gate exists (gate_role_source — validate-in-tempdir)",
      callable(getattr(_auth, "gate_role_source", None)))
check("#58 the skill/context correctness gate exists (gate_entry_source — validate-in-tempdir)",
      callable(getattr(_auth, "gate_entry_source", None)))
# a malformed rendered role module → the gate RETURNS an error (so the write-half REFUSES it).
_bad_role = "ROLE = {'id': 'x', 'output_schema': 'not a basemodel'}\n"  # bad: output_schema not a BaseModel
check("#58 the gate BITES: a malformed role module is REFUSED (gate returns an error, never written)",
      _auth.gate_role_source("x", _bad_role) is not None)
_bad_skill = "SKILL = {'id': 'y'}\n"  # bad: no content
check("#58 the gate BITES: a malformed skill module is REFUSED (gate returns an error, never written)",
      _auth.gate_entry_source("y", _bad_skill, kind="skill") is not None)
# a WELL-FORMED entry passes the gate (the gate refuses MALFORMED, not all — it's correctness, not approval).
_good_skill = "SKILL = {'id': 'z', 'content': 'do the thing'}\n"
check("#58 the gate PASSES a well-formed skill (correctness gate, not an approval gate)",
      _auth.gate_entry_source("z", _good_skill, kind="skill") is None)
# the DIRECT create methods exist on the Suite (authoring-apply is reachable — the reframe).
from runtime.suite import Suite as _Suite
for m in ("create_role", "create_skill", "create_context", "_write_role_file", "_write_entry_file"):
    check(f"#58 authoring-apply reachable: Suite.{m} exists (direct create, no approval)",
          callable(getattr(_Suite, m, None)))

# CAPTURE-EMBED ONE-SOURCE floor home — Suite.capture_corpus is the shared capture+embed-on-write seam BOTH
# faces call. It LIVES in suite.py, which CANNOT be added to COG_SOURCES (the wire's dispatch_decision /
# claude -p launch legitimately lives in the same file — a whole-file scan would false-breach). So the floor
# teeth for this method live HERE as a TARGETED method-source scan (the permanent home — not just the lane
# tests that a refactor could drop): capture_corpus is computation (a corpus.record write + a put_vector
# write via embed_corpus_to_spaces) and MUST NOT emit/launch any consequential verb. Same for _embed_text
# (a pure derivation). AST-for-calls would be ideal, but a code-only string scan (comments stripped) matches
# the COG_SOURCES discipline above and is robust to the docstrings that legitimately DESCRIBE the floor.
import inspect as _ins_floor
for _mname in ("capture_corpus", "_embed_text"):
    _msrc = _ins_floor.getsource(getattr(_Suite, _mname))
    _mbody = _msrc.split('"""', 2)[-1] if _msrc.count('"""') >= 2 else _msrc
    _mcode = "\n".join(l.split("#", 1)[0] for l in _mbody.splitlines())  # strip end-of-line comments
    _breach = [tok for tok in ("resolve_surfaced", "dispatch_decision", ".approve(", "drive_dispatchable",
                               ".resolve(")
               if tok in _mcode]
    check(f"C9.2 the floor COVERS Suite.{_mname} (the shared capture+embed seam — computation, never an "
          f"action): no resolve/approve/dispatch in its body", not _breach)

# ── C9.1 — a model runs only inside a role; the cognition layer has no consequential verb ─────────
print("\n[C9.1] roles act only within posture — no gate-bypassing action reachable from cognition")
# the rule engine routes; the ONLY effects are the declared destination kinds (all non-consequential:
# inject/chain/address are run:// writes/role-fires; surface SURFACES for the operator; lane = an event).
check("C9.1 the rule layer's effects are exactly the 5 non-consequential DESTINATION_KINDS",
      set(_rules.DESTINATION_KINDS) == {"inject", "chain", "address", "surface", "lane"})
# the surface destination routes to the operator inbox as an ASK (resolved=None) — it cannot self-resolve.
# Real structural assertion: rules.py's route() for the surface kind goes through surface_review and emits
# an `ask` (resolved=None), and NO route effect emits/calls a resolve. Find the route() body + scan its calls.
src_rules = open("runtime/rules.py").read()
_route_body = src_rules.split("def route", 1)[1] if "def route" in src_rules else ""
_route_code = "\n".join(l.split("#", 1)[0] for l in _route_body.splitlines())  # strip comments
check("C9.1 route()'s surface destination uses surface_review (the operator ASK path), not a resolve",
      "surface_review" in _route_code and not re.search(r'\.resolve\s*\(|["\']kind["\']\s*:\s*["\']resolve["\']', _route_code))

# ── C9.3 — fail loud everywhere ──────────────────────────────────────────────────────────────────
print("\n[C9.3] fail loud — missing/bad inputs RAISE, never a silent truthy/skip")
from runtime.cognition import injection_rule, resolve_run_ref
import tempfile
from store.fs_store import FsStore

# missing declared rule input → raise (not implicit-truthy)
for bad in ({}, {"recall": {"relevant": True, "snippet": "x"}}, {"ground": {"in_scope": True, "note": "n"}}):
    raised = False
    try:
        injection_rule(bad)
    except Exception:
        raised = True
    check(f"C9.3 injection_rule raises on missing declared input (keys={list(bad)})", raised)

# unresolved run:// ref → raise
store = FsStore(tempfile.mkdtemp(prefix="g9-"))
raised = False
try:
    resolve_run_ref("run://nope/missing", store)
except Exception:
    raised = True
check("C9.3 resolve_run_ref raises on an unresolved ref (never route on a missing value)", raised)

# a non-run:// scheme → raise
raised = False
try:
    resolve_run_ref("swarm://x/y", store)
except Exception:
    raised = True
check("C9.3 resolve_run_ref rejects a non-run:// address (swarm:// is not a scheme)", raised)

# ── C9.4 — every net-new cognition registry has a drift home + a drift assertion ──────────────────
print("\n[C9.4] drift homes: every net-new cognition registry is self-described + drift-asserted")
HOMES = {
    "EDGE_KINDS (G1.3)":            ("contracts/node_record.py", "contracts/AGENTS.md", "tests/edge_kinds_acceptance.py"),
    "roles registry (G2)":         ("runtime/roles.py",        "roles/AGENTS.md",      "tests/roles_acceptance.py"),
    "RULE_OPS+DESTINATION (G3)":    ("runtime/rules.py",        "runtime/AGENTS.md",    "tests/rules_acceptance.py"),
    "MODEL_CAPABILITIES (G8)":      ("ops/cli/capabilities.py", "ops/AGENTS.md",        "tests/model_capabilities_acceptance.py"),
    "THOUGHT_SHAPES+GRAIN (G4)":    ("runtime/suite.py",        "runtime/AGENTS.md",    "tests/chat_parts_acceptance.py"),
    # The 6 file-discovered corpus/cognition registries (719f82d) — now CONSUMED (WIRING). Each declares
    # its OWN drift home (`<name>/AGENTS.md`) + acceptance suite (mirrors the projections registry's home).
    "lifters registry (K2)":            ("runtime/lifters.py",            "lifters/AGENTS.md",            "tests/lifters_acceptance.py"),
    "mark_types registry (M1)":         ("runtime/mark_types.py",         "mark_types/AGENTS.md",         "tests/mark_types_acceptance.py"),
    "generation_policies registry (O2)":("runtime/generation_policies.py","generation_policies/AGENTS.md","tests/generation_policies_acceptance.py"),
    "relation_types registry (L3)":     ("runtime/relation_types.py",     "relation_types/AGENTS.md",     "tests/relation_types_acceptance.py"),
    "ai_tics registry (M4)":            ("runtime/ai_tics.py",            "ai_tics/AGENTS.md",            "tests/ai_tics_acceptance.py"),
    "forms registry (effort-routing)":  ("runtime/forms.py",              "forms/AGENTS.md",              "tests/forms_acceptance.py"),
}
for name, (regfile, home, test) in HOMES.items():
    check(f"C9.4 {name}: registry file + drift home ({home}) + acceptance test all present",
          os.path.exists(regfile) and os.path.exists(home) and os.path.exists(test))

print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} — {PASS} checks passed — G9 cognition governance: "
      "the resolve/dispatch floor is unforgeable from the cognition layer (by construction + standing "
      "source-invariant); roles run only inside run_role with non-consequential effects; fail-loud holds; "
      "every net-new registry has a drift home.")
sys.exit(0 if ok else 1)
