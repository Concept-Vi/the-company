"""runtime/rules.py — the RULE ENGINE (Concurrent Cognition G3 · the L2 core · the spine).

A RULE is the deterministic routing primitive of the collective cognition. L2: a model runs ONLY
inside a *role*; a *rule* is **declared, deterministic logic over resolved values** that decides what
happens to a role's structured output — route it, inject it, chain it, land it, surface it. *"That is
the main mechanism that all of this application is aimed at."* (Tim, L2, DECISIONS.md.)

This file GENERALIZES the G0 spike's hand-written `cognition.injection_rule` (a Python function) into
DECLARED DATA: a rule is a **declared AST interpreted by a RESTRICTED evaluator — NEVER eval/exec/
compile**. The spike's `recall.relevant AND ground.in_scope` becomes the first DECLARED rule, proven to
evaluate IDENTICALLY (see tests/rules_acceptance.py + cognition.injection_rule which now delegates here).

## Why a data-AST, not a parsed string (the load-bearing decision — R2-FOLD H2 · advisor)
The grammar is a **dict tree with a CLOSED op-set** (RULE_OPS) — e.g.
    {"op": "and", "args": [{"op": "field", "path": "recall.relevant"},
                           {"op": "field", "path": "ground.in_scope"}]}
authored AS DATA, never a string we parse. This makes the whitelist STRUCTURAL (C3.1):
  - `now`/`random`/`call`/IO/wave-completion-order/partial-results CANNOT be expressed — there is no
    such op in the language. (A parsed Python expression would force *blacklisting* dangerous nodes —
    the eval-sandbox arms race the design rejects. `ast.parse` itself calls compile(); banned too.)
  - field-access = DICT-KEY traversal on the resolved JSON values ONLY — never getattr/dunder reach.
  - comparison/membership operands = a sub-expression OR a static literal — never a free name.
  - renderability + addressability + the depth-cap all fall out for free (C3.3).

## Rule = pure DECISION (data); the DRIVER = effect (mirrors gate.py — R1-FOLD purity discipline)
`evaluate()` is handed ONLY the fully-resolved address values (the gate.py discipline: the scheduler
hands a node resolved inputs; the rule evaluator is handed resolved role outputs) and returns a pure
value/decision. It NEVER calls run_role / set_ref / surface_review / emits an event / does IO. The
DRIVER (cognition.py / suite.py) acts on the returned decision — exactly as gate.py returns {port:value}
and the *scheduler* does the set_ref. This is how the `claude -p`/build-dispatch floor (C9.2) and the
surface-cannot-forge-a-resolve law (C3.2) hold BY CONSTRUCTION: there is no op and no destination-kind
by which a rule produces a `resolve`/`approve`/`dispatch` — structural, not a runtime check.

## Determinism + readiness (R1-FOLD F5 · R2-FOLD H2 · DECISIONS Batch 5)
A rule is a PURE function of fully-resolved address values from its DECLARED referenceable-input
whitelist. PER-RULE READINESS (the scheduler has NO global barrier): the DRIVER evaluates a rule only
when EVERY declared input is SETTLED (resolved OR provably pruned/failed) — never on a timeout
(a timeout re-admits wall-clock = nondeterminism). A missing/pruned/failed reference FAILS LOUD or hits
the rule's declared `on_missing` — NEVER gate.py's implicit truthy-on-missing (that couples routing to
resolution-timing). Heavier-than-a-predicate computation → a role/node (composition — the gate pattern),
NOT a richer rule (the rule-vs-role classifier, E3).

## The two net-new registries + their drift homes (C9.4 / R2-FOLD H5)
- RULE_OPS         — the closed grammar (the ops a rule AST may use). Drift home: runtime/AGENTS.md.
- DESTINATION_KINDS — the five routing destinations (C3.2). Drift home: runtime/AGENTS.md.
tests/rules_acceptance.py asserts both stay reflected (mirrors edge_kinds_acceptance → contracts/AGENTS.md).

LAWS honoured: L1 registry-driven (rules + ops + destinations are DECLARED DATA) · L2 a model never runs
inside a rule · run:// addressing only · fail loud (missing ref → raise/declared on_missing; never a
timeout) · schema-additive · reflects-never-owns (rules + firings are addressable data the view draws) ·
reuse-don't-parallel (surface destination = surface_review; mirrors gate.py + edge_kinds registry) ·
the claude -p floor is lead-only (no destination emits resolve/approve/dispatch).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable


# =================================================================================================
# 1 · RULE_OPS — the closed grammar (a rule AST may use ONLY these; whitelist BY CONSTRUCTION).
#     Drift home: runtime/AGENTS.md. Each op is one node-kind in the data-AST.
# =================================================================================================
RULE_OPS: dict[str, str] = {
    # --- leaves ---
    "field":  "read a field by DOT-PATH from the resolved inputs (dict-key traversal only; e.g. "
              "'recall.relevant'). The FIRST path segment is a declared input id (the whitelist).",
    "lit":    "a STATIC literal value (str/int/float/bool/None/list of literals) — frozen at declare time.",
    # --- boolean ---
    "and":    "boolean AND over >=1 sub-expressions (all truthy).",
    "or":     "boolean OR over >=1 sub-expressions (any truthy).",
    "not":    "boolean NOT of one sub-expression.",
    # --- comparison ---
    "eq":     "equality of two sub-expressions.",
    "ne":     "inequality of two sub-expressions.",
    "lt":     "less-than (numeric/comparable) of two sub-expressions.",
    "le":     "less-than-or-equal of two sub-expressions.",
    "gt":     "greater-than of two sub-expressions.",
    "ge":     "greater-than-or-equal of two sub-expressions.",
    # --- arithmetic (over resolved numeric values; renders as a small badge) ---
    "add":    "numeric addition of two sub-expressions.",
    "sub":    "numeric subtraction of two sub-expressions.",
    "mul":    "numeric multiplication of two sub-expressions.",
    "div":    "numeric division arg[0]/arg[1] (fail-loud on divide-by-zero — never a silent inf/NaN).",
    "min":    "the smaller of two sub-expressions.",
    "max":    "the larger of two sub-expressions.",
    "clamp":  "constrain arg[0] to [arg[1], arg[2]] (= max(lo, min(x, hi))) — the layout-allocation primitive: "
              "an axis-derived dimension held within available space (relationship, not a breakpoint).",
    # --- membership ---
    "in":     "membership: arg[0] is a member of arg[1] (a resolved list/str/collection).",
    "contains": "membership (reversed): arg[0] (a collection) contains arg[1].",
}

# Renderability cap (C3.3): the cognition view (G7) draws a rule as a SHORT edge-badge. Arbitrary
# nesting degrades to a text-wall (violates rule 9 — no-text-wall). A rule deeper than this FAILS LOUD
# at validate (commit-time) — heavier logic must decompose into an upstream role/node (composition).
MAX_RULE_DEPTH = 6

# Arity by op (validated structurally at commit-time; an out-of-arity AST RAISES).
_ARITY = {
    "field": None, "lit": None,            # leaves: validated by their own shape, not args
    "not": 1,
    "eq": 2, "ne": 2, "lt": 2, "le": 2, "gt": 2, "ge": 2,
    "add": 2, "sub": 2, "mul": 2, "div": 2, "min": 2, "max": 2, "clamp": 3,
    "in": 2, "contains": 2,
    "and": -1, "or": -1,                   # -1 = variadic (>=1)
}


# =================================================================================================
# 2 · DESTINATION_KINDS — the five routing destinations a rule may route to (C3.2 · DECISIONS B3 Q4).
#     Drift home: runtime/AGENTS.md. CRITICAL LAW: NONE of these is resolve/approve/dispatch — a rule
#     SURFACES for the operator; it can NEVER forge an operator approve (the claude -p floor is
#     lead-only, C9.2). The `surface` kind routes through the EXISTING surface_review (emits an `ask`
#     event with resolved=None — NOT a `resolve` event); only the operator-only resolve_surfaced ever
#     emits `resolve`. So the floor holds BY CONSTRUCTION.
# =================================================================================================
DESTINATION_KINDS: dict[str, str] = {
    "inject":  "inject the routed value into a later reply part (write→address, resolved by the C1.3 "
               "run:// read at part-assembly). The G0 spike's recall-injection is this kind.",
    "chain":   "chain/trigger a dependent role (the rule names the next role; a thin executor fires "
               "run_role on it — the model runs in the ROLE, never the rule). The `check` case.",
    "address": "land the routed value at a run:// address for later (a durable write, no reply impact).",
    "surface": "surface to the inbox/decisions for the operator — REUSES Suite.surface_review (an `ask` "
               "event, resolved=None; a live escalation until the operator resolves). NEVER a resolve.",
    "lane":    "write the routed value to a named TYPED LANE/CHANNEL — a typed run-record on the ONE "
               "event log (kind='cognition.lane', a named stream), distinct from `address` by being a "
               "named stream rather than a single overwrite point. (Minimal seam — R2-FOLD H6 flagged "
               "typed-lane under-specified; built on the existing event log, NOT a parallel channel.)",
}

# The unforgeable-floor invariant, declared as DATA so the test can assert it structurally (C9.2/C3.2):
# no destination kind is — and none may ever be — one of these dispatch-trigger verbs.
FORBIDDEN_DESTINATION_VERBS = ("resolve", "approve", "dispatch")


# =================================================================================================
# 3 · THE EVALUATOR — a restricted recursive interpreter over the data-AST. NEVER eval/exec/compile.
# =================================================================================================
class RuleError(Exception):
    """A rule that is malformed, out-of-grammar, over-nested, or reads a missing input. Fail loud."""


def _is_literal_value(v: Any) -> bool:
    """A static literal allowed in a `lit` node: a JSON scalar or a list of such (frozen at declare)."""
    if v is None or isinstance(v, (bool, int, float, str)):
        return True
    if isinstance(v, list):
        return all(_is_literal_value(x) for x in v)
    return False


def validate_ast(node: Any, *, depth: int = 0, _path: str = "$") -> None:
    """STATIC AST WHITELIST-WALK (C3.1 · the commit-time gate that rides C3.4). Walk the data-AST and
    FAIL LOUD on anything outside the grammar: an unknown op, a bad arity, a non-literal `lit`, a
    non-string field path, or nesting past MAX_RULE_DEPTH. This is the structural whitelist — it does
    not (cannot) need a blacklist, because the grammar simply has no IO/time/random/call op.

    Called at role-discovery / commit (see attach_to_role_discovery) so a bad rule never ships."""
    if depth > MAX_RULE_DEPTH:
        raise RuleError(
            f"rule AST at {_path}: nesting depth {depth} > MAX_RULE_DEPTH={MAX_RULE_DEPTH} — a rule "
            f"must stay a SHORT renderable badge (C3.3). Heavier logic decomposes into an upstream "
            f"role/node (composition — the rule-vs-role classifier), not a deeper rule. Fail loud.")
    if not isinstance(node, dict):
        raise RuleError(
            f"rule AST at {_path}: every node must be a dict with an 'op', got {type(node).__name__} "
            f"({node!r}). The grammar is a declared data-AST, never a string/expression. Fail loud.")
    op = node.get("op")
    if op not in RULE_OPS:
        raise RuleError(
            f"rule AST at {_path}: unknown op {op!r} — NOT in the RULE_OPS grammar {sorted(RULE_OPS)}. "
            f"(now/random/call/io are NOT ops — they cannot appear by construction. Whitelist-by-"
            f"construction, C3.1.) Fail loud.")
    if op == "field":
        path = node.get("path")
        if not isinstance(path, str) or not path:
            raise RuleError(f"rule AST at {_path}: 'field' needs a non-empty string 'path', got {path!r}.")
        # dot-path segments must be plain identifiers (no dunder reach, no getattr-shaped tricks)
        for seg in path.split("."):
            if not seg or seg.startswith("__"):
                raise RuleError(
                    f"rule AST at {_path}: field path segment {seg!r} invalid — dict-key traversal only "
                    f"(no empty/dunder segments; never getattr). Fail loud.")
        return
    if op == "lit":
        if "value" not in node:
            raise RuleError(f"rule AST at {_path}: 'lit' needs a 'value' key. Fail loud.")
        if not _is_literal_value(node["value"]):
            raise RuleError(
                f"rule AST at {_path}: 'lit' value {node['value']!r} is not a static literal "
                f"(scalar or list of scalars, frozen at declare). Fail loud.")
        return
    # operator nodes: validate arity + recurse into args
    args = node.get("args")
    if not isinstance(args, list) or not args:
        raise RuleError(f"rule AST at {_path}: op {op!r} needs a non-empty 'args' list. Fail loud.")
    want = _ARITY[op]
    if want == -1:
        if len(args) < 1:
            raise RuleError(f"rule AST at {_path}: op {op!r} needs >=1 args, got {len(args)}.")
    elif want is not None and len(args) != want:
        raise RuleError(
            f"rule AST at {_path}: op {op!r} needs exactly {want} args, got {len(args)}. Fail loud.")
    for i, a in enumerate(args):
        validate_ast(a, depth=depth + 1, _path=f"{_path}.{op}[{i}]")


def declared_inputs(node: Any) -> set[str]:
    """The referenceable-input WHITELIST a rule AST declares: the FIRST segment of every field path
    (the role/input id the rule reads). The DRIVER uses this to know which run:// addresses must be
    SETTLED before evaluating the rule (per-rule readiness). Pure structural walk."""
    out: set[str] = set()
    if isinstance(node, dict):
        if node.get("op") == "field" and isinstance(node.get("path"), str):
            out.add(node["path"].split(".")[0])
        for a in node.get("args", []) or []:
            out |= declared_inputs(a)
    return out


def _get_path(resolved: dict, path: str) -> Any:
    """Dict-key traversal of a dot-path over the RESOLVED inputs (never getattr). Fail loud if any
    segment is missing — a rule reading an absent field is a malformed-input error (C9.3), never a
    silent None (that would couple routing to which fields a model happened to emit)."""
    cur: Any = resolved
    walked: list[str] = []
    for seg in path.split("."):
        walked.append(seg)
        if not isinstance(cur, dict) or seg not in cur:
            raise RuleError(
                f"rule eval: field path {path!r} did not resolve at {'.'.join(walked)!r} — the value "
                f"is {('absent' if isinstance(cur, dict) else 'not a dict (' + type(cur).__name__ + ')')}. "
                f"Fail loud (never route on a missing field — the rule's declared inputs must all be "
                f"present + resolved). Available at this level: "
                f"{sorted(cur) if isinstance(cur, dict) else '—'}.")
        cur = cur[seg]
    return cur


def _truthy(v: Any) -> bool:
    return bool(v)


def evaluate(node: Any, resolved: dict, *, _validated: bool = False) -> Any:
    """Interpret the data-AST against the RESOLVED inputs and return the value (PURE — no IO/effects).

    `resolved` is the dict of fully-resolved role outputs the DRIVER hands in (e.g.
    {"recall": {...}, "ground": {...}}) — the gate.py discipline (handed resolved values only). The
    evaluator NEVER reads time/random/order, never calls a model, never writes. Deterministic: identical
    `resolved` → identical result, regardless of the order the roles finished (R1-FOLD F5 / C0.2).

    Validates the AST first (unless told it's pre-validated) so a runtime call is also fail-loud."""
    if not _validated:
        validate_ast(node)
        _validated = True
    op = node["op"]
    if op == "field":
        return _get_path(resolved, node["path"])
    if op == "lit":
        return node["value"]
    args = node["args"]

    def ev(a):
        return evaluate(a, resolved, _validated=True)

    if op == "and":
        return all(_truthy(ev(a)) for a in args)
    if op == "or":
        return any(_truthy(ev(a)) for a in args)
    if op == "not":
        return not _truthy(ev(args[0]))
    if op == "eq":
        return ev(args[0]) == ev(args[1])
    if op == "ne":
        return ev(args[0]) != ev(args[1])
    if op == "lt":
        return ev(args[0]) < ev(args[1])
    if op == "le":
        return ev(args[0]) <= ev(args[1])
    if op == "gt":
        return ev(args[0]) > ev(args[1])
    if op == "ge":
        return ev(args[0]) >= ev(args[1])
    if op == "add":
        return ev(args[0]) + ev(args[1])
    if op == "sub":
        return ev(args[0]) - ev(args[1])
    if op == "mul":
        return ev(args[0]) * ev(args[1])
    if op == "div":
        num, den = ev(args[0]), ev(args[1])
        if den == 0:
            raise RuleError("rule eval: div by zero — fail loud (never a silent inf/NaN).")
        return num / den
    if op == "min":
        return min(ev(args[0]), ev(args[1]))
    if op == "max":
        return max(ev(args[0]), ev(args[1]))
    if op == "clamp":
        x, lo, hi = ev(args[0]), ev(args[1]), ev(args[2])
        return max(lo, min(x, hi))                          # the layout-allocation primitive
    if op == "in":
        return ev(args[0]) in ev(args[1])
    if op == "contains":
        return ev(args[1]) in ev(args[0])
    # unreachable — validate_ast already rejected any op not in RULE_OPS. Fail loud regardless.
    raise RuleError(f"rule eval: op {op!r} not implemented (should have failed validate). Fail loud.")


# =================================================================================================
# 4 · THE RULE — a declared, addressable, renderable record (C3.1/C3.3). Pure DECISION; no effect.
# =================================================================================================
@dataclass
class Rule:
    """A declared routing rule: an id, a condition (the data-AST), a destination kind (C3.2), and the
    destination params. PURE DATA — the DRIVER acts on `decide()`'s returned decision. Addressable +
    renderable (C3.3): `as_record()` is the data the live view (G7) draws; `firing_record()` is one
    firing. `on_missing` ('raise'|'skip') governs a missing declared input (never implicit truthy)."""
    id: str
    when: dict                                   # the condition data-AST (a RULE_OPS tree)
    destination: str                             # a DESTINATION_KINDS key
    params: dict = field(default_factory=dict)   # destination-specific (e.g. {"value_path": "recall.snippet"})
    on_missing: str = "raise"                     # 'raise' (fail loud) | 'skip' (declared no-op)
    label: str | None = None

    def __post_init__(self):
        # Validate at construction (commit-time gate, rides C3.4): a malformed/out-of-grammar/over-nested
        # rule RAISES — it never ships. Mirrors roles._build_role's fail-loud-on-malformed discipline.
        if self.destination not in DESTINATION_KINDS:
            raise RuleError(
                f"rule {self.id!r}: unknown destination {self.destination!r} — one of "
                f"{sorted(DESTINATION_KINDS)} (C3.2). And NEVER one of {FORBIDDEN_DESTINATION_VERBS} "
                f"(the claude -p floor is lead-only, C9.2). Fail loud.")
        if self.destination in FORBIDDEN_DESTINATION_VERBS:
            raise RuleError(
                f"rule {self.id!r}: destination {self.destination!r} is a FORBIDDEN dispatch-trigger "
                f"verb — a rule SURFACES, it can never forge a resolve/approve/dispatch (C9.2). Fail loud.")
        if self.on_missing not in ("raise", "skip"):
            raise RuleError(f"rule {self.id!r}: on_missing must be 'raise' or 'skip', got {self.on_missing!r}.")
        validate_ast(self.when)

    @property
    def inputs(self) -> set[str]:
        """The declared referenceable-input whitelist (per-rule readiness uses this)."""
        return declared_inputs(self.when)

    def ready(self, settled: dict) -> bool:
        """PER-RULE READINESS (R1-FOLD F5 / R2-FOLD H2 — no global barrier, never a timeout). The rule
        is ready iff EVERY declared input is SETTLED. `settled` maps input-id → status string; an input
        is settled when it is 'resolved' (value available) OR provably 'pruned'/'failed' (never coming).
        A 'pending' (still in-flight) input means NOT ready. This is the scheduler's readiness law applied
        to a rule; the DRIVER calls this before evaluate(), so a rule never fires on partial results."""
        for inp in self.inputs:
            st = settled.get(inp)
            if st not in ("resolved", "pruned", "failed"):
                return False
        return True

    def decide(self, resolved: dict) -> dict:
        """Evaluate the condition against the RESOLVED inputs → a PURE routing decision (no effect).

        Fail loud on a missing declared input UNLESS on_missing='skip' (then the decision is a declared
        no-op: fire=False, reason names the skip). The DRIVER acts on the returned decision; this never
        writes/emits/calls a model. Returns:
          {rule, fire: bool, destination, value: Any, params, reason}
        `fire` = the condition is truthy. `value` = the routed value (resolved from params.value_path if
        the rule declares one, else the boolean condition result)."""
        # ORDER-INDEPENDENT fail-loud (R1-FOLD F5 / R2-FOLD H2 sub-call 1): assert EVERY declared input
        # root is present BEFORE evaluating. Without this, `and`/`or` short-circuit (all()/any() stop at
        # the first falsy) would SKIP a missing input that sits behind a falsy earlier arg → a silent
        # fire=False instead of a raise — coupling routing to which refs happened to resolve/prune (the
        # exact implicit-on-missing the laws forbid). A pruned/failed role is absent from `resolved`, so
        # this is where a pruned dep fails loud / hits on_missing (the readiness contract's other half).
        missing = self.inputs - set(resolved)
        if missing:
            if self.on_missing == "skip":
                return {"rule": self.id, "fire": False, "destination": self.destination,
                        "value": None, "params": dict(self.params),
                        "reason": f"on_missing=skip: declared inputs {sorted(missing)} not resolved/pruned"}
            raise RuleError(
                f"rule {self.id!r}: declared input(s) {sorted(missing)} not resolved (absent from the "
                f"resolved values — missing/pruned/failed). Fail loud (never route on a missing ref; "
                f"never implicit-on-missing — F5/H2). Declare on_missing='skip' to handle a pruned ref.")
        try:
            fire = _truthy(evaluate(self.when, resolved, _validated=True))
        except RuleError as e:
            # a deeper field error (e.g. a nested path absent within a present root) — still fail loud
            # / honor on_missing, never silently no-fire.
            if self.on_missing == "skip":
                return {"rule": self.id, "fire": False, "destination": self.destination,
                        "value": None, "params": dict(self.params),
                        "reason": f"on_missing=skip: {e}"}
            raise
        value: Any = fire
        vpath = self.params.get("value_path")
        if fire and vpath:
            value = _get_path(resolved, vpath)   # fail loud if the routed value path is absent
        return {"rule": self.id, "fire": fire, "destination": self.destination,
                "value": value, "params": dict(self.params),
                "reason": self._reason(resolved, fire)}

    def _reason(self, resolved: dict, fire: bool) -> str:
        """A short human-legible reason (renderable — the badge text). Pure."""
        return (self.label or f"{self.id}: {self._render_when()}") + (" → FIRE" if fire else " → no")

    def _render_when(self) -> str:
        """Render the condition AST as a SHORT infix string for the edge-badge (C3.3). Depth-capped by
        construction. Pure formatter — NOT a re-parse."""
        return _render_ast(self.when)

    # --- addressable data (C3.3 · reflects-never-owns) ---
    def as_record(self) -> dict:
        """The rule AS ADDRESSABLE DATA the live view (G7) draws (C3.3). Pure serialization."""
        return {"id": self.id, "label": self.label, "when": self.when, "when_text": self._render_when(),
                "destination": self.destination, "params": dict(self.params),
                "inputs": sorted(self.inputs), "on_missing": self.on_missing,
                "depth": _ast_depth(self.when)}

    def firing_record(self, decision: dict, *, turn_id: str) -> dict:
        """ONE firing AS ADDRESSABLE DATA (C3.3) — the record the view draws for a rule that evaluated
        this turn (lives at run://<turn>/rules/<rule-id>). Pure."""
        return {"turn_id": turn_id, "rule": self.id, "when_text": self._render_when(),
                "fired": bool(decision.get("fire")), "destination": decision.get("destination"),
                "reason": decision.get("reason"), "address": f"run://{turn_id}/rules/{self.id}"}


def _render_ast(node: Any) -> str:
    """Render a data-AST as a short infix string (the edge-badge — C3.3). Pure."""
    if not isinstance(node, dict):
        return repr(node)
    op = node.get("op")
    if op == "field":
        return node["path"]
    if op == "lit":
        return repr(node["value"])
    args = node.get("args", [])
    infix = {"and": " AND ", "or": " OR ", "eq": " == ", "ne": " != ", "lt": " < ", "le": " <= ",
             "gt": " > ", "ge": " >= ", "add": " + ", "sub": " - ", "mul": " * ", "div": " / ", "in": " in ",
             "contains": " contains "}                       # min/max/clamp render via the f"{op}(…)" fallback (safe, no KeyError)
    if op == "not":
        return f"NOT {_render_ast(args[0])}"
    if op in infix:
        return "(" + infix[op].join(_render_ast(a) for a in args) + ")"
    return f"{op}(…)"


def _ast_depth(node: Any) -> int:
    if not isinstance(node, dict) or node.get("op") in ("field", "lit"):
        return 1
    return 1 + max((_ast_depth(a) for a in node.get("args", [])), default=0)


# =================================================================================================
# 5 · build_rule + the role-discovery hook (the commit-time static walk — C3.4 rides this)
# =================================================================================================
def build_rule(decl: dict) -> Rule:
    """Build + VALIDATE a Rule from a declared dict (the commit-time gate, C3.1/C3.4). Fail loud on a
    malformed rule. The declared shape:
        {"id": str, "when": <data-AST>, "destination": <DESTINATION_KINDS key>,
         "params": {...}, "on_missing": "raise"|"skip", "label": str?}
    Backward-compatible: a role's EXISTING `rules` declarations (the descriptive {id,reads,effect,kind}
    shape in roles/*.py) are NOT data-AST rules — they describe intent. `is_ast_rule()` distinguishes
    them; only AST-shaped rules are built/validated here (so G2's role files still load unchanged)."""
    if not isinstance(decl, dict):
        raise RuleError(f"rule decl must be a dict, got {type(decl).__name__}. Fail loud.")
    if "id" not in decl or not isinstance(decl["id"], str) or not decl["id"]:
        raise RuleError(f"rule decl needs a non-empty string 'id'. Fail loud.")
    if "when" not in decl:
        raise RuleError(f"rule {decl['id']!r}: needs a 'when' condition AST. Fail loud.")
    if "destination" not in decl:
        raise RuleError(f"rule {decl['id']!r}: needs a 'destination' (one of {sorted(DESTINATION_KINDS)}).")
    return Rule(
        id=decl["id"], when=decl["when"], destination=decl["destination"],
        params=dict(decl.get("params") or {}), on_missing=decl.get("on_missing", "raise"),
        label=decl.get("label"),
    )


def is_ast_rule(decl: dict) -> bool:
    """Distinguish a G3 data-AST rule (has a 'when' op-tree + a 'destination') from the older descriptive
    rule shape ({id,reads,effect,kind}) the G2 role files already declare. Only AST rules are validated
    by the static walk (so the existing role files load unchanged — schema-additive)."""
    return isinstance(decl, dict) and isinstance(decl.get("when"), dict) and "destination" in decl


def validate_role_rules(role_id: str, rules_decl: Any) -> list[Rule]:
    """The role-discovery hook: STATIC WHITELIST-WALK every AST-shaped rule a role declares, at load
    (C3.1) — so a bad rule never ships (rides the normal commit path, C3.4). Returns the built Rules.
    A descriptive (non-AST) rule is passed through un-built (still valid G2 data). Fail loud on a
    malformed AST rule (mirrors roles._build_role's fail-loud-on-malformed)."""
    built: list[Rule] = []
    for decl in (rules_decl or []):
        if is_ast_rule(decl):
            try:
                built.append(build_rule(decl))
            except RuleError as e:
                raise RuleError(f"role {role_id!r}: malformed declared rule — {e}") from e
    return built


# =================================================================================================
# 6 · route() — the DRIVER seam: given a fired decision + the live Suite, perform the destination
#     EFFECT. This is the ONLY place a rule's decision becomes an action. The rule itself never acts.
#     CRITICAL: no branch here emits resolve/approve/dispatch (C9.2/C3.2 — the floor is lead-only).
# =================================================================================================
def route(decision: dict, *, store=None, suite=None, turn_id: str,
          emit: Callable[[str, dict], None] | None = None,
          chain_executor: Callable[[str], Any] | None = None) -> dict:
    """Perform the EFFECT of a fired routing decision (the DRIVER's job — never the rule's). Dispatches
    on `decision['destination']` over the FIVE DESTINATION_KINDS. Returns an outcome record (addressable).

    DESTINATION SEAMS (reuse-don't-parallel):
      inject  — returns the value for a later part to inject (the part-assembly does the run:// read;
                G4 wires it). For G3 we LAND the value at run://<turn>/inject/<rule> so the part can read
                it back via the canonical resolver (C1.3) — the spike's exact inject mechanism.
      chain   — TRIGGER the dependent role (params.chain_role). The DRIVER supplies a `chain_executor`
                (role_id → fired role output) — the model runs INSIDE the role (run_role), NEVER in the
                rule (L2). route() lands the chained output at run://<turn>/chain/<rule> and returns it,
                so the chained role's result is addressable like any role output. If no executor is
                supplied, route() returns the chain DECISION (chain_role named) for the driver to honor.
      address — store.set_ref(run://<turn>/addr/<rule>, value) — a durable landing (no reply impact).
      surface — suite.surface_review({...}) — the EXISTING inbox/decisions path (emits `ask`, resolved=
                None; a live escalation). NEVER a resolve event. (Asserted adversarially.)
      lane    — emit('cognition.lane', {...}) — a named typed stream on the ONE event log (NOT a parallel
                channel; R2-FOLD H6 minimal seam).

    Only acts when decision['fire'] is True (a non-firing rule is a no-op outcome). Fail loud on a
    destination that needs a missing collaborator (e.g. surface with no suite) — never silently skip."""
    out = {"rule": decision.get("rule"), "destination": decision.get("destination"),
           "fired": bool(decision.get("fire")), "acted": False}
    if not decision.get("fire"):
        out["reason"] = "rule did not fire (no-op)"
        return out
    dest = decision["destination"]
    value = decision.get("value")
    rid = decision.get("rule")

    if dest == "inject":
        # land the value at a run:// inject address so a later part reads it back (C1.3 canonical read)
        if store is None:
            raise RuleError(f"route(inject): needs a store to land the injected value. Fail loud.")
        addr = f"run://{turn_id}/inject/{rid}"
        cas = store.put_content(value)
        store.set_ref(addr, cas)
        out.update(acted=True, address=addr, value=value)
        return out

    if dest == "chain":
        # TRIGGER the dependent role. The model runs INSIDE the role (via the executor's run_role),
        # NEVER in the rule (L2). The executor is the DRIVER's run_role seam, kept OUT of the pure rule.
        chain_role = decision.get("params", {}).get("chain_role")
        if not chain_role:
            raise RuleError(f"route(chain): rule {rid!r} declares no params.chain_role to chain. Fail loud.")
        if chain_executor is not None:
            chained_out = chain_executor(chain_role)          # the DRIVER fires run_role(chain_role)
            if store is not None:                              # land the chained output at run:// (addressable)
                addr = f"run://{turn_id}/chain/{rid}"
                store.set_ref(addr, store.put_content(chained_out))
                out.update(acted=True, chain_role=chain_role, chained_output=chained_out, address=addr)
            else:
                out.update(acted=True, chain_role=chain_role, chained_output=chained_out)
            return out
        # no executor supplied → return the chain DECISION for the driver to honor (still a valid route)
        out.update(acted=True, chain_role=chain_role,
                   note="DRIVER fires run_role(chain_role) — the model runs in the ROLE (L2), not the rule")
        return out

    if dest == "address":
        if store is None:
            raise RuleError(f"route(address): needs a store to land the value. Fail loud.")
        addr = f"run://{turn_id}/addr/{rid}"
        cas = store.put_content(value)
        store.set_ref(addr, cas)
        out.update(acted=True, address=addr, value=value)
        return out

    if dest == "surface":
        # REUSE the existing surface_review (no parallel inbox). It emits an `ask` event (resolved=None) —
        # NEVER a `resolve`. A rule can surface for the operator; it can NEVER forge an approve (C9.2/C3.2).
        if suite is None or not hasattr(suite, "surface_review"):
            raise RuleError(f"route(surface): needs a Suite with surface_review (no parallel inbox). Fail loud.")
        item = {"title": decision.get("params", {}).get("title") or f"rule {rid} fired",
                "kind": "cognition-rule", "rule": rid, "turn_id": turn_id, "value": value,
                "reason": decision.get("reason")}
        res = suite.surface_review(item, origin="responsive")
        out.update(acted=True, surfaced=res.get("id"), surfaced_status=res.get("status"))
        return out

    if dest == "lane":
        lane = decision.get("params", {}).get("lane")
        if not lane:
            raise RuleError(f"route(lane): rule {rid!r} declares no params.lane (the named stream). Fail loud.")
        if emit is None:
            raise RuleError(f"route(lane): needs an emit sink (the ONE event log). Fail loud.")
        emit("cognition.lane", {"turn_id": turn_id, "rule": rid, "lane": lane, "value": value,
                                "reason": decision.get("reason")})
        out.update(acted=True, lane=lane, value=value)
        return out

    # unreachable — Rule.__post_init__ already rejected any non-DESTINATION_KINDS dest. Fail loud.
    raise RuleError(f"route: unknown destination {dest!r} (should have failed at build). Fail loud.")
