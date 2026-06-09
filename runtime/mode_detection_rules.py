"""runtime/mode_detection_rules.py — the FILE-DISCOVERED mode-detection-rule registry (Concurrent
Cognition Group I · the signal→candidate vocabulary of the mode auto-detector).

A MODE-DETECTION-RULE is a declared row that maps a SIGNAL CONDITION → a candidate presence mode.
The detector (`activation.detect_mode_candidate`) reads the live `activity_signal()` snapshot, walks
the discovered rules in PRIORITY order (first-match-wins), and produces a candidate mode — which feeds
the existing off/suggest/auto toggle (`Suite.autodetect_mode`). The detector NEVER switches the mode of
its own authority; the toggle owns the posture (off=ignore · suggest=surface · auto=switch).

## Why a FILE-DISCOVERED registry, not a python list (the registry-is-truth law — same BAR as projections)
The detection rules USED to be a hardcoded `MODE_DETECTION_RULES = [ {..., "when": lambda s: ...} ]`
literal in `activation.py`. That violated two laws at once:
  1. **NOTHING static / registry-is-truth** — add-a-rule meant a CODE EDIT, not a dropped FILE. The real
     test of "registry-driven" (the PART 4.3 bar the projection/role/skill registries meet) is
     **add-a-row = a FILE, no code edit.**
  2. **A `lambda` is CODE, not authorable DATA** — a closure can't be validated at discovery, can't be
     serialized to a surface, and is a SECOND predicate mechanism beside the G3 rule-engine's declared
     data-AST. reuse-don't-parallel says use the ONE predicate language the system already has.

So a rule's condition is a **`rules.RULE_OPS` data-AST** (the EXACT grammar the G3 cognition rules use —
boolean/comparison/arithmetic/field-access/membership over a resolved snapshot, NEVER `eval`/`exec`/a
lambda). It is VALIDATED at discovery (`rules.validate_ast` — fail-loud on a malformed/out-of-grammar
AST) and EVALUATED by `rules.evaluate` against the `activity_signal()` snapshot. Authored AS DATA, so a
rule is file-droppable, validatable, surfaceable, and deterministic.

## Why SELF-CONTAINED (mirrors projections.py / roles.py — the ONE registry mechanism, not a fork)
This mirrors the MECHANISM of `runtime/projections.py:ProjectionRegistry` /
`runtime/roles.py:RoleRegistry` (both of which mirror `runtime/registry.py:NodeRegistry`) — `os.listdir`
→ `importlib` a directory, fail-loud on a malformed entry, id==filename, dict-like, `rediscover` for
removal. It is a STANDALONE copy of that pattern (exactly as roles.py / projections.py are standalone
copies — they don't import each other's base either). The ROW SHAPE differs (a detection rule declares
`candidate`/`why`/`when`/`priority`, no `level`/`embeds`), so the validator is detection-specific
(`_build_rule`) — mirroring the mechanism, not copying projection's field check.

## The ORDERING trap (the load-bearing difference from projections/roles)
projections/roles are KEYED dicts with NO order — order doesn't matter for a lens or a cast member. But
mode-detection is **first-match-wins — ORDER-BEARING.** `sorted(os.listdir)` would couple the detection
SEMANTICS to filenames (drop `aaa_rule.py` and it jumps to the front). So each rule declares an EXPLICIT
integer `priority` (lower fires first) and the detector sorts by `(priority, id)` — NEVER by listdir
order. Authoring order is decoupled from filename order.

## The None-handling discipline (a real startup correctness point)
At startup / with no operator activity, `activity_signal()["idle_seconds"]` is **None**. A naive
`{ge: [idle_seconds, 600]}` would be `None >= 600` → a TypeError, not False. So an idle-threshold rule
MUST guard the not-None FIRST inside an `and` so the comparison short-circuits:
  `{and: [ {ne: [idle_seconds, lit None]}, {ge: [idle_seconds, 600]} ]}`
(`rules.evaluate`'s `and` is `all(... for a in args)` — it short-circuits, verified by use; and
`validate_ast` accepts a `lit` whose value is None.)

## The mode-detection-rule schema
Each `mode_detection_rules/<id>.py` declares a module-level `MODE_DETECTION_RULE` dict — a registry ROW:
  - `id`        — required; MUST equal the module name (addressable by file, like a role/lens/node-type —
                  fail-loud otherwise).
  - `candidate` — required; the presence-mode id this rule proposes (e.g. "background"/"focus"/
                  "listening"). VALIDATED ∈ `suite.MODES` at DETECT time (the registry can't see the live
                  mode set at discovery; the detector fail-louds — rule 8, never propose a fabricated mode).
  - `why`       — required; a one-line legible rationale that SURFACES with the suggestion (FORM: legible).
  - `when`      — required; the condition data-AST (a `rules.RULE_OPS` tree) over the `activity_signal()`
                  snapshot. Validated at discovery (`rules.validate_ast`). `field` paths read the snapshot
                  keys (idle_seconds · last_activity · mode · inbox · recent_kinds).
  - `priority`  — required int; lower fires first (first-match-wins is by ascending priority, then id).

A malformed entry (no string id / id≠filename / missing required / unknown field / bad type / a `when`
that fails `validate_ast`) FAILS LOUD at discovery — never a silent skip (a non-MODE_DETECTION_RULE /
`_`-file is the one that skips, mirroring the role/projection non-entry skip).

## Drift home (mirrors projections/AGENTS.md · roles/AGENTS.md)
`mode_detection_rules/AGENTS.md` is this registry's constitution (the drift home). The runtime
constitution (`runtime/AGENTS.md`) names this registry under the Group-I detector section.
`tests/mode_autodetect_acceptance.py` asserts the discovered rules + the registry are reflected.

## The floor (C9.2)
A detection rule is DECLARED DATA — it PRODUCES a candidate, it performs NO effect. The detector READS
the registry + the signal (no resolve/dispatch/approve), produces a candidate, and feeds the existing
TOGGLE — which `surface`s (suggest) or `set_mode`s (auto). A rule can NEVER forge an operator approve or
launch a build. `rules.evaluate` is PURE (no IO, no model, no clock — deterministic).

LAWS honoured: no-hardcoding (rules are FILE-DISCOVERED DATA, never a literal list — the add-a-row=a-FILE
bar) · reuse-don't-parallel (the ONE registry mechanism + the ONE predicate language `rules.RULE_OPS`,
not a fork, not a lambda) · fail loud (a malformed rule RAISES at discovery; an unregistered candidate
RAISES at detect) · the floor (the detector produces a candidate + feeds the toggle — never a resolve/
dispatch) · suggest-not-silently-switch (the detector never calls set_mode — the toggle owns the posture).
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass

from runtime import rules as _rules


# The schema field names a detection rule MAY declare. ALL of these are REQUIRED (a rule with no
# candidate/why/when/priority is meaningless to the detector). An unknown field FAILS LOUD (never a
# silent typo'd field no consumer reads — mirrors projection's unknown-field check).
RULE_FIELDS = ("id", "candidate", "why", "when", "priority")
REQUIRED_FIELDS = ("id", "candidate", "why", "when", "priority")


@dataclass
class ModeDetectionRule:
    """A discovered detection rule — the declared dict (`spec`) verbatim + typed accessors. `when` is a
    `rules.RULE_OPS` data-AST (validated at build); `priority` orders first-match-wins (ascending)."""
    id: str
    candidate: str
    why: str
    when: dict
    priority: int
    spec: dict

    def matches(self, signal: dict) -> bool:
        """Evaluate this rule's `when` AST against an `activity_signal()` snapshot. PURE
        (rules.evaluate is IO-free + deterministic). Pre-validated at build → no re-validate."""
        return bool(_rules.evaluate(self.when, signal, _validated=True))

    def as_record(self) -> dict:
        """The rule as a plain dict (the declared spec verbatim) — for a surface/projection to serialize.
        registry-is-truth: this is the discovered row, never a hand-listed one."""
        return dict(self.spec)


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_mdr_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


def _build_rule(name: str, decl: dict) -> ModeDetectionRule:
    """Validate + build a ModeDetectionRule from a module's declared dict. FAIL LOUD on a malformed entry
    (mirrors projections._build_projection / roles._build_role's RAISE-on-declared-but-malformed): a
    declared MODE_DETECTION_RULE with a bad shape RAISES — it is NOT silently skipped (a non-rule file is
    the one that skips). registry-is-truth: never register a fabricated/unnamed/under-declared rule.

    NOTE — `candidate` is NOT validated against the mode set here: the registry is discovered at Suite
    construction and can't see the live `MODES` (which itself derives from the discovered rhm_mode nodes).
    The candidate-∈-MODES check lives in `activation.detect_mode_candidate` (fail-loud at DETECT time,
    rule 8) — the same place the old literal validated it."""
    if not isinstance(decl, dict):
        raise TypeError(
            f"mode-detection-rule module {name!r}: MODE_DETECTION_RULE must be a dict (the declared rule "
            f"schema), got {type(decl).__name__} — fail loud, never a silent malformed rule.")
    rid = decl.get("id")
    if not rid or not isinstance(rid, str):
        raise ValueError(
            f"mode-detection-rule module {name!r}: declares no string `id` — every rule declares its id "
            f"(fail loud; author from the registry, never an unnamed rule).")
    if rid != name:
        raise ValueError(
            f"mode-detection-rule module {name!r}: id {rid!r} != module name {name!r} — the id must equal "
            f"the file name (so a rule is addressable by file, mirroring roles/projections/node-types). "
            f"Fail loud.")
    unknown = [k for k in decl if k not in RULE_FIELDS]
    if unknown:
        raise ValueError(
            f"mode-detection-rule {rid!r}: unknown field(s) {unknown} — the schema is "
            f"{list(RULE_FIELDS)}. Fail loud (never a silent typo'd field that no consumer reads).")
    missing = [k for k in REQUIRED_FIELDS if k not in decl]
    if missing:
        raise ValueError(
            f"mode-detection-rule {rid!r}: missing required field(s) {missing} — a rule MUST declare "
            f"{list(REQUIRED_FIELDS)} (candidate=the proposed mode · why=the legible rationale · "
            f"when=the condition data-AST · priority=the first-match-wins order). Fail loud.")
    candidate = decl.get("candidate")
    if not isinstance(candidate, str) or not candidate:
        raise ValueError(
            f"mode-detection-rule {rid!r}: `candidate` must be a non-empty string (the proposed presence "
            f"mode id). Got {candidate!r} — fail loud (validated ∈ MODES at detect time, rule 8).")
    why = decl.get("why")
    if not isinstance(why, str) or not why:
        raise ValueError(
            f"mode-detection-rule {rid!r}: `why` must be a non-empty string (the legible rationale that "
            f"surfaces with the suggestion — FORM: legible). Got {why!r} — fail loud.")
    priority = decl.get("priority")
    # bool is an int subclass — reject it so a `True`/`False` can't masquerade as a priority (mirrors the
    # wire's derived_from int-not-bool guard).
    if not isinstance(priority, int) or isinstance(priority, bool):
        raise ValueError(
            f"mode-detection-rule {rid!r}: `priority` must be an int (lower fires first; first-match-wins "
            f"is by ascending priority, NOT listdir/filename order). Got {priority!r} — fail loud.")
    when = decl.get("when")
    if not isinstance(when, dict):
        raise ValueError(
            f"mode-detection-rule {rid!r}: `when` must be a dict (a rules.RULE_OPS condition data-AST over "
            f"the activity_signal snapshot — NEVER a lambda/string/eval). Got {type(when).__name__} — "
            f"fail loud.")
    # Validate the condition AGAINST THE ONE GRAMMAR at discovery (reuse-don't-parallel: the same
    # whitelist-walk the G3 rules ride). A malformed/out-of-grammar/over-nested AST RAISES here — it never
    # ships (mirrors Rule.__post_init__'s commit-time gate).
    try:
        _rules.validate_ast(when)
    except Exception as exc:
        raise ValueError(
            f"mode-detection-rule {rid!r}: `when` is not a valid rules.RULE_OPS AST ({exc}). The grammar "
            f"is {sorted(_rules.RULE_OPS)} over the activity_signal keys (idle_seconds/last_activity/mode/"
            f"inbox/recent_kinds). Fail loud — a rule out of the grammar never ships.") from exc
    return ModeDetectionRule(id=rid, candidate=candidate, why=why, when=when, priority=priority,
                             spec=dict(decl))


class ModeDetectionRuleRegistry:
    """The file-discovered MODE-DETECTION-RULE registry — mirrors `runtime/projections.py:
    ProjectionRegistry` / `runtime/roles.py:RoleRegistry` / `runtime/registry.py:NodeRegistry` (the ONE
    registry mechanism; not a fork). Dict-like (`reg[id] -> ModeDetectionRule`, `id in reg`, `.get(id)`,
    iterate). Adding a rule = dropping a `mode_detection_rules/<id>.py` declaring `MODE_DETECTION_RULE =
    {...}`; it self-registers.

    The KEY difference from projections/roles: `ordered()` returns the rules in FIRST-MATCH-WINS order
    (ascending `priority`, then id) — detection is order-bearing, so ordering is by the declared integer,
    NEVER by listdir/filename order. The detector (`activation.detect_mode_candidate`) walks `ordered()`."""

    def __init__(self):
        self.rules: dict[str, ModeDetectionRule] = {}

    def discover(self, dirs: list[str]) -> "ModeDetectionRuleRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "MODE_DETECTION_RULE", None)
                if decl is None:        # not a rule module (mirrors NodeRegistry's `run` check)
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "ModeDetectionRuleRegistry":
        """Rebuild from the filesystem (clear + discover) — so a REMOVED rule file actually un-registers
        (discover() only adds). Mirrors RoleRegistry/ProjectionRegistry.rediscover."""
        self.rules.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> None:
        self.rules[name] = _build_rule(name, decl)

    def ordered(self) -> list[ModeDetectionRule]:
        """The rules in FIRST-MATCH-WINS order — ascending `priority`, then id (a deterministic tiebreak).
        THIS is the order the detector walks; never `sorted(os.listdir)` (which would couple detection
        semantics to filenames — the ordering trap)."""
        return sorted(self.rules.values(), key=lambda r: (r.priority, r.id))

    def as_records(self) -> list[dict]:
        """The whole rule set as plain dicts (the declared spec verbatim, in firing order) — for a
        surface/projection to serialize to both faces. registry-is-truth: the discovered set, in the
        order it fires."""
        return [r.as_record() for r in self.ordered()]

    # --- dict-like (mirrors RoleRegistry / ProjectionRegistry) ---
    def __getitem__(self, rid: str) -> ModeDetectionRule:
        return self.rules[rid]

    def __contains__(self, rid: str) -> bool:
        return rid in self.rules

    def __iter__(self):
        return iter(self.rules)

    def __len__(self) -> int:
        return len(self.rules)

    def get(self, rid: str, default=None):
        return self.rules.get(rid, default)
