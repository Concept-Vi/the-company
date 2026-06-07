"""tests/rules_acceptance.py — the RULE ENGINE (Concurrent Cognition G3 · the L2 core).

Proves G3 by USE + ADVERSARIALLY (not just units): a rule is a DECLARED DATA-AST interpreted by a
RESTRICTED evaluator (NEVER eval/exec/compile), deterministic, renderable, addressable, that routes a
role's resolved output to one of five destinations — and CANNOT forge a resolve/approve/dispatch.

  C3.1  full declared logic, determinism ENFORCED not asserted:
          - a valid RICH predicate (multi-field, boolean+comparison+membership) evaluates correctly
            AND replays IDENTICALLY (deterministic regardless of input finish-order).
          - the generalized spike rule (recall.relevant AND ground.in_scope) is a DECLARED AST and
            evaluates IDENTICALLY to the old hand-written cognition.injection_rule.
          - ADVERSARIAL: a rule that tries to read time/random/order/partials/call-a-model is REJECTED
            by the static whitelist-walk at commit AND there is no eval path (whitelist by construction);
            a missing/pruned reference FAILS LOUD (never implicit truthy-on-missing).
  C3.2  a rule routes to ANY of five destinations (inject · chain · address · surface · lane), all five
        demonstrated by USE; the SURFACE destination CANNOT emit a resolve (it routes through
        surface_review → an `ask` event, resolved=None; the claude -p floor stays lead-only).
  C3.3  routing is renderable + addressable: a rule + its firing are queryable data; over-nesting fails loud.
  C3.4  new/changed rules ride the normal change path (the static AST walk is the commit gate; no special gate).

Plus: drift home — RULE_OPS + DESTINATION_KINDS reflected in runtime/AGENTS.md (C9.4 / R2-FOLD H5).

Run: PYTHONPATH=. python tests/rules_acceptance.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from runtime import rules
from runtime.rules import (
    RULE_OPS, DESTINATION_KINDS, FORBIDDEN_DESTINATION_VERBS, MAX_RULE_DEPTH,
    Rule, RuleError, build_rule, evaluate, validate_ast, route, validate_role_rules,
)
from store.fs_store import FsStore

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def expect_raise(label, fn, exc=RuleError):
    global PASS
    try:
        fn()
    except exc:
        PASS += 1
        print(f"  ok  {label}")
    else:
        raise AssertionError(f"FAIL (no raise): {label}")


store = FsStore(os.path.join(tempfile.mkdtemp(prefix="rules-"), "store"))

# =================================================================================================
# C3.1 — a valid RICH predicate evaluates correctly + replays identically
# =================================================================================================
print("\nC3.1 — declared logic, determinism ENFORCED")

# a RICH predicate: multi-field, boolean + comparison + membership over resolved values.
# "(recall.relevant AND ground.in_scope) AND recall.score >= 0.5 AND ground.topic in recall.topics"
rich = {
    "op": "and",
    "args": [
        {"op": "field", "path": "recall.relevant"},
        {"op": "field", "path": "ground.in_scope"},
        {"op": "ge", "args": [{"op": "field", "path": "recall.score"}, {"op": "lit", "value": 0.5}]},
        {"op": "in", "args": [{"op": "field", "path": "ground.topic"}, {"op": "field", "path": "recall.topics"}]},
    ],
}
validate_ast(rich)
check("a rich multi-field AST (bool+comparison+membership) validates", True)

resolved_true = {
    "recall": {"relevant": True, "score": 0.8, "snippet": "S", "topics": ["storage", "voice"]},
    "ground": {"in_scope": True, "topic": "storage"},
}
resolved_false = {
    "recall": {"relevant": True, "score": 0.3, "snippet": "S", "topics": ["storage"]},  # score < 0.5
    "ground": {"in_scope": True, "topic": "storage"},
}
check("rich predicate is TRUE when all conditions hold", evaluate(rich, resolved_true) is True)
check("rich predicate is FALSE when score < 0.5 (comparison branch)", evaluate(rich, resolved_false) is False)
check("membership branch: ground.topic NOT in recall.topics → FALSE",
      evaluate(rich, {"recall": {"relevant": True, "score": 0.9, "snippet": "S", "topics": ["voice"]},
                      "ground": {"in_scope": True, "topic": "storage"}}) is False)

# replay-identical: many evals over the SAME resolved inputs → ONE distinct result (deterministic).
results = {evaluate(rich, resolved_true) for _ in range(100)}
check("replay-identical: 100 evals over identical inputs → 1 distinct result (deterministic)", results == {True})

# determinism regardless of finish-order: the dict the driver hands in is order-independent; prove by
# building it in two different key-orders and getting the identical result.
import collections
a = collections.OrderedDict()
a["ground"] = resolved_true["ground"]; a["recall"] = resolved_true["recall"]
b = collections.OrderedDict()
b["recall"] = resolved_true["recall"]; b["ground"] = resolved_true["ground"]
check("routing is independent of which input was inserted first (finish-order invariance)",
      evaluate(rich, a) == evaluate(rich, b) == True)

# the generalized spike rule evaluates IDENTICALLY to the old hand-written cognition.injection_rule.
from runtime.cognition import injection_rule, INJECTION_RULE


def old_injection(resolved):
    rec, grd = resolved["recall"], resolved["ground"]
    relevant, in_scope = bool(rec.get("relevant")), bool(grd.get("in_scope"))
    if relevant and in_scope:
        return {"inject": True, "snippet": rec["snippet"], "reason": "recall.relevant AND ground.in_scope"}
    return {"inject": False, "snippet": None,
            "reason": f"recall.relevant={relevant} ground.in_scope={in_scope}"}


for rel in (True, False):
    for ins in (True, False):
        c = {"recall": {"relevant": rel, "snippet": "the snippet"}, "ground": {"in_scope": ins, "note": "n"}}
        check(f"declared INJECTION_RULE == old hand-written logic (relevant={rel}, in_scope={ins})",
              injection_rule(c) == old_injection(c))

# --- C3.1 ADVERSARIAL: nondeterminism / IO / model-call CANNOT be expressed (whitelist by construction) ---
print("\nC3.1 ADVERSARIAL — nondeterminism/IO/model-call is REJECTED")

# a rule that tries to read 'now' (time) — there is no such op → rejected at the static walk.
expect_raise("a rule using a 'now' op is REJECTED (no such op — whitelist by construction)",
             lambda: validate_ast({"op": "now", "args": []}))
expect_raise("a rule using a 'random' op is REJECTED",
             lambda: validate_ast({"op": "random", "args": []}))
expect_raise("a rule using a 'call' op (model/function call) is REJECTED",
             lambda: validate_ast({"op": "call", "args": [{"op": "lit", "value": "model"}]}))
expect_raise("a rule using a 'read_file'/IO op is REJECTED",
             lambda: validate_ast({"op": "read_file", "args": [{"op": "lit", "value": "/etc/passwd"}]}))
# wave-completion-order / partial-results: there is no op that reads finish-order or 'which sibling
# finished first' — the evaluator is handed ONLY the resolved-value dict, with no order/partial channel.
expect_raise("a rule using a 'finish_order' op is REJECTED (no order channel exists)",
             lambda: validate_ast({"op": "finish_order", "args": []}))
# a field path with a dunder (getattr-shaped reach) is rejected — dict-key traversal only.
expect_raise("a field path with a __dunder__ segment is REJECTED (no getattr reach)",
             lambda: validate_ast({"op": "field", "path": "recall.__class__"}))
# a 'lit' with a non-literal (e.g. a dict op masquerading) is rejected.
expect_raise("a 'lit' with a non-static value is REJECTED",
             lambda: validate_ast({"op": "lit", "value": {"op": "now"}}))
# build_rule on an adversarial rule is REJECTED at commit (rides C3.4).
expect_raise("build_rule REJECTS an adversarial (time-reading) rule at COMMIT (C3.4 gate)",
             lambda: build_rule({"id": "evil", "when": {"op": "now", "args": []}, "destination": "inject"}))

# a string is not a valid AST node (we never parse strings — no eval/ast.parse path at all).
expect_raise("a STRING is not a valid AST node (we never parse/eval strings)",
             lambda: validate_ast("recall.relevant AND ground.in_scope"))

# prove there is NO eval/exec/compile/ast.parse call in the rule engine source (structural — the
# language is DATA, never a parsed string). Strip comments AND every string-LITERAL (docstrings name the
# ban as prose — "calls compile()", "ast.parse") using the tokenizer, then assert no real call survives.
import io
import re
import tokenize
src = open(os.path.join(ROOT, "runtime", "rules.py")).read()
_code_toks = []
for tok in tokenize.generate_tokens(io.StringIO(src).readline):
    if tok.type in (tokenize.COMMENT, tokenize.STRING):
        continue                                   # drop comments + ALL string literals (docstrings)
    _code_toks.append(tok.string)
code_only = " ".join(_code_toks)
check("runtime/rules.py contains NO eval()/exec()/compile()/ast.parse() call (the language is DATA)",
      not re.search(r'(?<![A-Za-z_.])(eval|exec|compile)\s*\(', code_only)
      and not re.search(r'ast\s*\.\s*parse\s*\(', code_only)
      and "__import__" not in code_only)

# --- C3.1 missing/pruned reference FAILS LOUD (never implicit truthy-on-missing) ---
print("\nC3.1 — missing/pruned reference fails loud (never gate.py implicit-truthy)")
r = build_rule({"id": "needs-both", "when": rich, "destination": "inject",
                "params": {"value_path": "recall.snippet"}})
expect_raise("a missing declared input (no 'ground') FAILS LOUD at decide()",
             lambda: r.decide({"recall": {"relevant": True, "score": 0.9, "snippet": "S", "topics": ["x"]}}))
# ADVERSARIAL (order-independence — the short-circuit trap): a missing input sitting BEHIND a falsy
# earlier arg must STILL fail loud — `and`/`or` short-circuit must NOT silently swallow it (that would
# couple routing to which refs resolved/pruned — the implicit-on-missing F5/H2 forbid).
r_sc = build_rule({"id": "short-circuit", "destination": "inject",
                   "when": {"op": "and", "args": [{"op": "field", "path": "recall.relevant"},
                                                  {"op": "field", "path": "ground.in_scope"}]}})
expect_raise("a missing input BEHIND a falsy arg STILL fails loud (no short-circuit swallow — F5/H2)",
             lambda: r_sc.decide({"recall": {"relevant": False}}))   # ground ABSENT, behind a False
# and the same rule with on_missing='skip' is a DECLARED no-op (not a silent fire=False either way).
r_sc_skip = build_rule({"id": "sc-skip", "destination": "inject", "on_missing": "skip",
                        "when": {"op": "and", "args": [{"op": "field", "path": "recall.relevant"},
                                                       {"op": "field", "path": "ground.in_scope"}]}})
d_sc = r_sc_skip.decide({"recall": {"relevant": False}})  # ground absent behind a False
check("a missing input behind a falsy arg with on_missing='skip' is a DECLARED no-op (not silent)",
      d_sc["fire"] is False and "on_missing=skip" in d_sc["reason"] and "ground" in d_sc["reason"])
# on_missing='skip' → a DECLARED no-op (not implicit truthy): fire=False with a skip reason.
r_skip = build_rule({"id": "skip-on-missing", "when": {"op": "field", "path": "recall.relevant"},
                     "destination": "inject", "on_missing": "skip"})
d = r_skip.decide({})  # recall absent
check("on_missing='skip' yields a DECLARED no-op (fire=False), never implicit-truthy",
      d["fire"] is False and "on_missing=skip" in d["reason"])

# per-rule readiness (no global barrier, never a timeout): ready only when EVERY declared input settled.
check("readiness: NOT ready while an input is 'pending'",
      r.ready({"recall": "resolved", "ground": "pending"}) is False)
check("readiness: ready when every input is 'resolved'",
      r.ready({"recall": "resolved", "ground": "resolved"}) is True)
check("readiness: a 'pruned'/'failed' input is SETTLED (ready), driver then fails-loud/on_missing",
      r.ready({"recall": "resolved", "ground": "pruned"}) is True)

# =================================================================================================
# C3.2 — a rule routes to ANY of five destinations; surface CANNOT forge a resolve
# =================================================================================================
print("\nC3.2 — five destinations, all by USE; surface != resolve")
check("DESTINATION_KINDS has exactly the five declared kinds",
      set(DESTINATION_KINDS) == {"inject", "chain", "address", "surface", "lane"})


# a tiny fake suite that records surface_review calls + the events emitted (to prove no resolve).
class FakeSuite:
    def __init__(self):
        self.events = []          # (kind, payload)
        self.surfaced = []

    def _emit(self, kind, summary, **meta):
        self.events.append((kind, {"summary": summary, **meta}))

    def surface_review(self, item, origin="responsive"):
        # MIRRORS the real Suite.surface_review contract: it emits an `ask` event (NEVER `resolve`),
        # resolved stays None (a live escalation). We assert this is what the rule's surface path uses.
        sid = f"surf-{len(self.surfaced)}"
        self.surfaced.append({"id": sid, "item": item, "origin": origin, "resolved": None})
        self._emit("ask", f"a review item was surfaced ({origin})", surfaced=sid, origin=origin)
        return {"id": sid, "origin": origin, "status": "inbox"}


emitted = []


def emit(kind, payload):
    emitted.append((kind, payload))


TURN = "test-turn-1"
fire_resolved = resolved_true  # the rich rule fires on this

# (1) INJECT — lands the value at run://<turn>/inject/<rule>, readable back via the canonical resolver.
r_inject = build_rule({"id": "inj", "when": {"op": "field", "path": "recall.relevant"},
                       "destination": "inject", "params": {"value_path": "recall.snippet"}})
out = route(r_inject.decide(fire_resolved), store=store, turn_id=TURN)
check("destination INJECT lands the value at a run:// address", out["acted"] and out["address"].startswith("run://"))
cas = store.head(out["address"])
check("the injected value reads BACK via the canonical run:// resolver (C1.3)",
      store.get_content(cas) == "S")

# (2) CHAIN — TRIGGERS the dependent role via the driver's executor (model runs in the ROLE, not rule).
r_chain = build_rule({"id": "chn", "when": {"op": "field", "path": "ground.in_scope"},
                      "destination": "chain", "params": {"chain_role": "check"}})
# without an executor: returns the chain DECISION (the role to fire) for the driver to honor.
out = route(r_chain.decide(fire_resolved), turn_id=TURN)
check("destination CHAIN names the dependent role (no executor → decision for the driver)",
      out["acted"] and out["chain_role"] == "check")
# WITH an executor (the driver's run_role seam — the model runs in the ROLE): route FIRES it + lands
# the chained output at a run:// address. The executor here is a fake run_role (no live model needed in
# the unit; the live-4B chain firing is proven in the e2e). It MUST be the ROLE that runs a model — the
# rule never does (L2). We assert route triggered it + the output is addressable.
fired_roles = []


def fake_chain_executor(role_id):
    fired_roles.append(role_id)
    return {"contradicts": False, "note": ""}    # what a CheckOut role would emit


out = route(r_chain.decide(fire_resolved), store=store, turn_id=TURN, chain_executor=fake_chain_executor)
check("destination CHAIN TRIGGERS the dependent role via the executor (run_role; model in the ROLE, L2)",
      out["acted"] and fired_roles == ["check"])
check("the chained role's output is landed at a run:// address (addressable like any role output)",
      out["address"].startswith("run://") and store.get_content(store.head(out["address"]))["contradicts"] is False)

# (3) ADDRESS — lands the value at run://<turn>/addr/<rule> (durable, no reply impact).
r_addr = build_rule({"id": "lnd", "when": {"op": "field", "path": "recall.relevant"},
                     "destination": "address", "params": {"value_path": "ground.topic"}})
out = route(r_addr.decide(fire_resolved), store=store, turn_id=TURN)
check("destination ADDRESS lands the value durably at a run:// address",
      out["acted"] and store.get_content(store.head(out["address"])) == "storage")

# (4) SURFACE — REUSES surface_review (an `ask` event, resolved=None) — NEVER a resolve.
fake = FakeSuite()
r_surf = build_rule({"id": "srf", "when": {"op": "field", "path": "ground.in_scope"},
                     "destination": "surface", "params": {"title": "needs a look"}})
out = route(r_surf.decide(fire_resolved), suite=fake, turn_id=TURN)
check("destination SURFACE routes through surface_review (the existing inbox, no parallel queue)",
      out["acted"] and out["surfaced"] == "surf-0")
check("the surfaced item has resolved=None (a live escalation, NOT a resolve)",
      fake.surfaced[0]["resolved"] is None)

# SURFACE by USE against the REAL Suite (not just the fake): the rule's surface lands a real review
# item in the real inbox with resolved=None, and NO resolve event is emitted (the floor holds on the
# real path too). Reuse-don't-parallel: it is the SAME surface_review the build-loop/idea-capture use.
from runtime.registry import NodeRegistry
from runtime.suite import Suite
_real_store = FsStore(os.path.join(tempfile.mkdtemp(prefix="rules-suite-"), "store"))
_reg = NodeRegistry(); _reg.discover([os.path.join(ROOT, "nodes")])
real_suite = Suite(_real_store, _reg, nodes_dir=os.path.join(ROOT, "nodes"))
_before = len(_real_store.list_surfaced())
out = route(r_surf.decide(fire_resolved), suite=real_suite, turn_id=TURN)
_items = _real_store.list_surfaced()
check("SURFACE by USE on the REAL Suite: a review item lands in the real inbox",
      len(_items) == _before + 1 and out["surfaced"])
_surfaced = _real_store.get_surfaced(out["surfaced"])
check("the REAL surfaced item has resolved=None (a live escalation, never a forged resolve)",
      _surfaced.get("resolved") is None and _surfaced.get("status") == "inbox")
# no `resolve` event was emitted by the real surface path (only `ask`); the dispatch floor holds.
_evs = _real_store.events_since(-1)
check("the REAL surface path emitted NO `resolve`/`approve`/`dispatch` event (floor lead-only)",
      not any(e.get("kind") in ("resolve", "approve", "dispatch") for e in _evs))

# (5) LANE — a named typed stream on the ONE event log.
r_lane = build_rule({"id": "lan", "when": {"op": "field", "path": "recall.relevant"},
                     "destination": "lane", "params": {"lane": "contradictions", "value_path": "recall.snippet"}})
out = route(r_lane.decide(fire_resolved), turn_id=TURN, emit=emit)
check("destination LANE writes a typed cognition.lane event (a named stream, not a parallel channel)",
      out["acted"] and any(k == "cognition.lane" and p["lane"] == "contradictions" for k, p in emitted))

# --- C3.2 CRITICAL LAW: the surface path CANNOT emit a resolve/approve/dispatch ---
print("\nC3.2 ADVERSARIAL — the claude -p floor is lead-only (surface cannot forge a resolve)")
kinds_emitted = [k for k, _ in fake.events]
check("the surface path emitted ONLY an `ask` event — NEVER a `resolve`",
      "ask" in kinds_emitted and "resolve" not in kinds_emitted)
for verb in FORBIDDEN_DESTINATION_VERBS:
    check(f"no event of kind {verb!r} was emitted by ANY rule destination",
          verb not in kinds_emitted and verb not in [k for k, _ in emitted])
# a rule CANNOT even DECLARE a forbidden destination (resolve/approve/dispatch) — rejected at build.
for verb in FORBIDDEN_DESTINATION_VERBS:
    expect_raise(f"a rule declaring destination={verb!r} is REJECTED at build (floor is lead-only)",
                 lambda v=verb: build_rule({"id": "x", "when": {"op": "field", "path": "a.b"}, "destination": v}))
# structural proof: no DESTINATION_KIND is a forbidden verb, and route() has no resolve/approve/dispatch.
check("no DESTINATION_KIND is a forbidden dispatch-trigger verb (structural)",
      not (set(DESTINATION_KINDS) & set(FORBIDDEN_DESTINATION_VERBS)))
rules_src = open(os.path.join(ROOT, "runtime", "rules.py")).read()
route_body = rules_src[rules_src.index("def route("):]
import re as _re
# no emit/append of a 'resolve'/'approve'/'dispatch' event kind in route()
check("route() never emits a resolve/approve/dispatch event kind (structural — code-walk)",
      not _re.search(r'(emit|append_event)\([^)]*["\'](resolve|approve|dispatch)', route_body))

# =================================================================================================
# C3.3 — routing is renderable + addressable; over-nesting fails loud
# =================================================================================================
print("\nC3.3 — renderable + addressable; nesting cap fails loud")
rec = r.as_record()
check("a rule is addressable DATA: as_record() has id/when/destination/inputs/when_text",
      all(k in rec for k in ("id", "when", "destination", "inputs", "when_text")))
check("the rule renders to a SHORT badge string (when_text)", isinstance(rec["when_text"], str) and len(rec["when_text"]) > 0)
check("the rule's declared inputs are queryable (the readiness whitelist)",
      set(rec["inputs"]) == {"recall", "ground"})
fr = r.firing_record(r.decide(fire_resolved), turn_id=TURN)
check("a FIRING is addressable data at run://<turn>/rules/<rule> with fired/reason",
      fr["address"] == f"run://{TURN}/rules/needs-both" and fr["fired"] is True and "reason" in fr)


# over-nesting (deeper than MAX_RULE_DEPTH) FAILS LOUD — the edge-badge must stay legible.
def deep_ast(n):
    node = {"op": "field", "path": "a.b"}
    for _ in range(n):
        node = {"op": "not", "args": [node]}
    return node


validate_ast(deep_ast(MAX_RULE_DEPTH - 2))  # within cap — ok
check(f"a rule within MAX_RULE_DEPTH={MAX_RULE_DEPTH} validates", True)
expect_raise("a rule nested PAST the depth cap FAILS LOUD (renderability — no text-wall, C3.3)",
             lambda: validate_ast(deep_ast(MAX_RULE_DEPTH + 3)))

# =================================================================================================
# C3.4 — new/changed rules ride the normal change path (the static walk IS the commit gate)
# =================================================================================================
print("\nC3.4 — rides the normal change path (static walk = commit gate; no special gate)")
# validate_role_rules is the role-discovery hook: a role's AST-shaped rules are statically walked at
# load (the commit gate); descriptive (non-AST) rules pass through unchanged (schema-additive).
good_role_rules = [
    {"id": "ast-rule", "when": {"op": "field", "path": "recall.relevant"}, "destination": "inject"},
    {"id": "descriptive", "reads": "recall.relevant", "effect": "inject", "kind": "inject"},  # G2 shape
]
built = validate_role_rules("recall", good_role_rules)
check("validate_role_rules builds AST rules + passes descriptive rules through (schema-additive)",
      len(built) == 1 and built[0].id == "ast-rule")
expect_raise("a role declaring a MALFORMED AST rule FAILS LOUD at discovery (the commit gate)",
             lambda: validate_role_rules("bad", [{"id": "b", "when": {"op": "now", "args": []},
                                                  "destination": "inject"}]))
# the COMMIT GATE is wired into role DISCOVERY (roles._build_role → validate_role_rules): dropping a
# roles/*.py with a malformed AST rule FAILS LOUD at discovery — not just at Rule() construction.
from runtime.roles import RoleRegistry, _build_role
reg = RoleRegistry().discover([os.path.join(ROOT, "roles")])
check("ALL discovered G2 role files load (their declared rules pass the static walk at discovery)",
      len(list(reg)) >= 6)
for rid in reg:                                   # catch-all: every discovered role, not a hardcoded subset
    validate_role_rules(rid, reg[rid].spec.get("rules"))  # must not raise
check("EVERY discovered role's declared rules pass the static walk (catch-all, existing files unchanged)", True)
# a role declared with a malformed AST rule FAILS LOUD at _build_role (the discovery path itself).
expect_raise("a role with a malformed AST rule FAILS LOUD at discovery (_build_role wires the gate)",
             lambda: _build_role("evilrole", {"id": "evilrole",
                                              "rules": [{"id": "x", "when": {"op": "now", "args": []},
                                                         "destination": "inject"}]}))

# =================================================================================================
# DRIFT HOME (C9.4 / R2-FOLD H5) — RULE_OPS + DESTINATION_KINDS reflected in runtime/AGENTS.md
# =================================================================================================
print("\nDRIFT HOME — runtime/AGENTS.md reflects both net-new registries")
constitution = open(os.path.join(ROOT, "runtime", "AGENTS.md")).read()
missing_ops = [op for op in RULE_OPS if op not in constitution]
check(f"every RULE_OPS entry is reflected in runtime/AGENTS.md (drift: {missing_ops})", not missing_ops)
missing_dest = [d for d in DESTINATION_KINDS if d not in constitution]
check(f"every DESTINATION_KINDS entry is reflected in runtime/AGENTS.md (drift: {missing_dest})", not missing_dest)
check("RULE_OPS is named in its drift home", "RULE_OPS" in constitution)
check("DESTINATION_KINDS is named in its drift home", "DESTINATION_KINDS" in constitution)

print(f"\nALL {PASS} CHECKS PASS — G3 rule engine: declared-AST · deterministic · 5 destinations · "
      f"surface!=resolve · renderable+addressable · rides the change path · drift home")
