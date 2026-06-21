"""runtime/decision_registry.py — the file-discovered DECISION registry + the state-composer (decision-surface).

A DECISION is an addressed, typed thing the system needs an owner (Tim) to decide ON — the first content type
of the resolution-first decision-surface, and the RECONCILE vessel of the Face Pipeline. This module is the
COMPANY-SIDE resolver-target the `decision://` scheme dispatches to (runtime/cognition.py:resolve_address):

  • `DecisionRegistry`  — file-discovered (`decisions/<id>.py` each declaring a module-level `DECISION` dict).
                          Adding a decision = dropping a file; it self-registers. Mirrors the MECHANISM of
                          `runtime/lifter_registry.py:LifterRegistry` / `runtime/mark_types.py` (os.listdir →
                          spec_from_file_location by PATH → validate → register). registry-is-truth.
  • `compose_state`     — the PURE fold: a decision row + its `decision_take` mark thread → the RESOLVED
                          decision (row + composed state). STATE is NOT an authored field — it RESOLVES from
                          the LATEST decision_take mark by ts (the take IS the artifact; the row never mutates).

## Why a RESOLVER-TARGET, not a COG_SOURCES registry
This is reached like cc_board/cc_clone/vi_vision — a record/registry the `resolve_address` DISPATCH resolves
TO — NOT a registry CONSUMED by cognition compute (run_role/capture/create_*) the way mark_types/lifters are.
So (like its resolver-siblings) it is NOT enrolled in tests/cognition_governance_acceptance.py's COG_SOURCES /
C9.4 HOMES; the floor obligation lives in the resolver's OWN branch in cognition.py (which IS scanned — and
stays `.resolve(`-free: this registry exposes `.get(`, a read, never a resolve/dispatch).

## Why a NAME-SHADOW-SAFE registry module
Named `decision_registry.py` (NOT `runtime/decisions.py`) + discovered by PATH (spec_from_file_location), so the
`decisions/` rows-dir is never package-imported — the lifters lesson (runtime/lifters.py shadowed the lifters/
namespace package). No code does `import decisions`; the rows-dir is read off disk, never bound as a module.

## The DECISION schema (schemas/vi-vision/v1/decision.schema.json — composition's contract, in-tree mirror)
Each `decisions/<id>.py` declares a module-level `DECISION` dict — the PENDING DEFINITION only:
  - `id`                 — required; MUST equal the file stem (addressable as decision://<frame>/<id>).
  - `meaning`            — required; the decision in HUMAN terms (Tim's words) — the question. Never a machine name.
  - `options`            — required; a NON-EMPTY list of option dicts: {label (required, the decided_value),
                           description?, implication?, recommended?:bool}. label is the choice in human terms.
  - `address`            — optional; the addressed thing this decides ON (NOT the decision's identity).
  - `explanation_source` — optional; an address the RHM resolves to EXPLAIN this decision (live, not stored).
  - `scope`              — optional; global|project|user|session (default global; denormalised, also the frame).
  - `legibility`         — optional; {name (required), is (required), fills?, why?} — the meaning-fields.
A malformed entry FAILS LOUD at discovery (mirrors _build_lifter) — never a silent skip (a non-DECISION /
`_`-file is the one that skips). registry-is-truth.

LAWS honoured: no-hardcoding (decisions are FILE-DISCOVERED) · reuse-don't-parallel (ONE registry mechanism —
mirrors LifterRegistry/MarkTypeRegistry; NOT a fork) · fail loud (malformed RAISES at discovery; unknown id →
.get returns None → the resolver RAISES) · the floor (a registry read + a pure fold — no resolve/dispatch).
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass


# The DECISION schema field names a row MAY declare. id+meaning+options required; rest optional.
DECISION_FIELDS = ("id", "address", "meaning", "options", "explanation_source", "scope", "legibility")
DECISION_REQUIRED = ("id", "meaning", "options")
DECISION_SCOPES = ("global", "project", "user", "session")
OPTION_FIELDS = ("label", "description", "implication", "recommended")
LEGIBILITY_FIELDS = ("name", "is", "fills", "why")
LEGIBILITY_REQUIRED = ("name", "is")


class DecisionError(ValueError):
    """A malformed DECISION row (fail-loud at discovery) — never a silent malformed decision."""


@dataclass
class Decision:
    """A discovered decision — the declared dict (`spec`) verbatim + typed accessors. The PENDING DEFINITION
    only; STATE resolves from the decision_take mark thread (compose_state), never from here."""
    id: str
    spec: dict

    @property
    def meaning(self) -> str:
        return self.spec["meaning"]

    @property
    def options(self) -> list:
        return self.spec["options"]

    @property
    def scope(self) -> str:
        return self.spec.get("scope") or "global"

    @property
    def explanation_source(self):
        return self.spec.get("explanation_source")

    @property
    def legibility(self):
        return self.spec.get("legibility")


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_decision_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


def _build_decision(name: str, decl: dict) -> Decision:
    """Validate + build a Decision from a module's declared dict. FAIL LOUD on a malformed entry (mirrors
    _build_lifter's RAISE-on-declared-but-malformed): a declared DECISION with a bad shape RAISES — never
    silently skipped (a non-DECISION file is the one that skips). registry-is-truth. A LIGHT structural gate
    (the required fields + shapes the resolver/render rely on) — not a full JSON-schema validator."""
    if not isinstance(decl, dict):
        raise DecisionError(
            f"decision module {name!r}: DECISION must be a dict (the declared decision schema), got "
            f"{type(decl).__name__} — fail loud, never a silent malformed decision.")
    did = decl.get("id")
    if not did or not isinstance(did, str):
        raise DecisionError(
            f"decision module {name!r}: DECISION declares no string `id` — every decision declares its id "
            f"(fail loud; author from the registry, never an unnamed decision).")
    if did != name:
        raise DecisionError(
            f"decision module {name!r}: DECISION id {did!r} != module name {name!r} — the id must equal the "
            f"file name (so a decision is addressable by file as decision://<frame>/<id>). Fail loud.")
    unknown = [k for k in decl if k not in DECISION_FIELDS]
    if unknown:
        raise DecisionError(
            f"decision {did!r}: unknown decision-schema field(s) {unknown} — the schema is "
            f"{list(DECISION_FIELDS)}. Fail loud (never a silent typo'd field no consumer reads).")
    missing = [k for k in DECISION_REQUIRED if not decl.get(k)]
    if missing:
        raise DecisionError(
            f"decision {did!r}: missing required field(s) {missing} — required: {list(DECISION_REQUIRED)} "
            f"(id+meaning+options). Fail loud.")
    if not isinstance(decl.get("meaning"), str) or not decl["meaning"].strip():
        raise DecisionError(
            f"decision {did!r}: `meaning` must be a non-empty string (the decision in human terms). Fail loud.")
    opts = decl.get("options")
    if not isinstance(opts, list) or not opts:
        raise DecisionError(
            f"decision {did!r}: `options` must be a non-empty list of choices (option dicts). Fail loud.")
    for i, o in enumerate(opts):
        if not isinstance(o, dict):
            raise DecisionError(f"decision {did!r}: option[{i}] must be a dict, got {type(o).__name__}. Fail loud.")
        ounknown = [k for k in o if k not in OPTION_FIELDS]
        if ounknown:
            raise DecisionError(
                f"decision {did!r}: option[{i}] unknown field(s) {ounknown} — the option schema is "
                f"{list(OPTION_FIELDS)}. Fail loud.")
        if not isinstance(o.get("label"), str) or not o["label"].strip():
            raise DecisionError(
                f"decision {did!r}: option[{i}] needs a non-empty string `label` (the choice in human terms, "
                f"= the decided_value the take records). Fail loud.")
        if "recommended" in o and not isinstance(o["recommended"], bool):
            raise DecisionError(
                f"decision {did!r}: option[{i}] `recommended` must be a bool. Fail loud.")
    scope = decl.get("scope")
    if scope is not None and scope not in DECISION_SCOPES:
        raise DecisionError(
            f"decision {did!r}: `scope` {scope!r} not in {list(DECISION_SCOPES)}. Fail loud.")
    leg = decl.get("legibility")
    if leg is not None:
        if not isinstance(leg, dict):
            raise DecisionError(f"decision {did!r}: `legibility` must be a dict. Fail loud.")
        lunknown = [k for k in leg if k not in LEGIBILITY_FIELDS]
        if lunknown:
            raise DecisionError(
                f"decision {did!r}: legibility unknown field(s) {lunknown} — schema {list(LEGIBILITY_FIELDS)}. "
                f"Fail loud.")
        for k in LEGIBILITY_REQUIRED:
            if not isinstance(leg.get(k), str) or not leg[k].strip():
                raise DecisionError(
                    f"decision {did!r}: legibility.{k} must be a non-empty string (name=which one, is=what "
                    f"kind — the meaning-fields). Fail loud.")
    return Decision(id=did, spec=dict(decl))


def compose_state(row: dict, marks: list) -> dict:
    """PURE: fold a decision row + its mark thread → the RESOLVED decision (row + composed state). State
    RESOLVES from the LATEST `decision_take` mark by ts (registry-is-truth: the take IS the artifact; the row
    NEVER mutates). No decision_take ⇒ pending. decided_value = the chosen option label (the take's `value`);
    decided_by / decided_at from the mark's `by` / `ts`. Unit-testable without a store. The returned dict is the
    RESOLVED VIEW (the row's fields + state/decided_value/decided_by/decided_at) — NOT a stored row (the stored
    decision schema is the DEFINITION only; state is never authored). `marks` are already keyed to the canonical
    address by the caller (store.marks_for(decision_address(...))) — this fold selects the take/retract events.

    RETRACT (the operator-undo / 'Change' primitive + the safe append-only way to neutralise a mistaken/test
    take without deleting the audit trail): a `decision_retract` mark appended AFTER a take (newer ts) wins →
    pending; a later take re-decides. The LATEST decision EVENT by ts decides; no events ⇒ pending."""
    events = [m for m in (marks or []) if isinstance(m, dict)
              and m.get("mark_type") in ("decision_take", "decision_retract")]
    resolved = dict(row) if isinstance(row, dict) else {"row": row}
    # DERIVED `recommended_label` (the recommended option's label) — added to the RESOLVED VIEW so the
    # decision /api/territory record (identity = resolve_address → compose_state) carries it FLAT, which is
    # what projection's host row_fields read (`identity.recommended_label`). Same derivation decision_inbox
    # uses (single logic, registry-is-truth: it's row.options-derived, not authored). Present in every return
    # path (it's static, not state-dependent). A row without options/recommended → None (honest absent).
    if isinstance(row, dict):
        resolved["recommended_label"] = next(
            (o.get("label") for o in (row.get("options") or [])
             if isinstance(o, dict) and o.get("recommended") and o.get("label")), None)
    if not events:
        resolved.update(state="pending", decided_value=None, decided_by=None, decided_at=None)
        return resolved
    latest = max(events, key=lambda m: str(m.get("ts") or ""))
    if latest.get("mark_type") == "decision_retract":               # the most recent action un-decided it → pending
        resolved.update(state="pending", decided_value=None, decided_by=None, decided_at=None)
        return resolved
    resolved.update(state="decided", decided_value=latest.get("value"),
                    decided_by=latest.get("by"), decided_at=latest.get("ts"))
    return resolved


def decision_inbox(registry, store) -> list:
    """The decisions INBOX list (the operator's see-all-pending entry, beyond the deep-link): one
    {id, type, address, name, state, recommended_label} per discovered decision. registry-is-truth — the
    discovered set. `type` = the STACK-ITEM-TYPE ("decision-sequence") so the host DERIVES its StackItemType from
    the feed (registry-is-truth; projection's union-derive dep — the stack envelope is {id,type,address,name,
    state}). state = the FAST mark-composed state (compose_state — NOT the recall-grounded resolve; the inbox only
    needs open-vs-decided, so this stays GPU-free + fast: marks_for + the fold, no recall/embed). name =
    legibility.name (operator-law: never the raw id — humanise the id as the floor). address = the CANONICAL
    decision://global/<id> (file-discovered registry decisions are global; the take writes + the resolver reads
    marks off this same canonical). recommended_label = the recommended option's label (a hint; optional)."""
    out = []
    for did in sorted(registry):
        row = registry.get(did)
        if not isinstance(row, dict):
            continue
        addr = f"decision://global/{did}"
        marks = store.marks_for(addr) if (store is not None and hasattr(store, "marks_for")) else []
        st = compose_state(row, marks)
        leg = row.get("legibility") if isinstance(row.get("legibility"), dict) else {}
        name = (leg.get("name") or "").strip() or did.replace("-", " ").replace("_", " ").strip() or did
        rec = next((o.get("label") for o in (row.get("options") or [])
                    if isinstance(o, dict) and o.get("recommended") and o.get("label")), None)
        out.append({"id": did, "type": "decision-sequence", "address": addr, "name": name,
                    "state": st.get("state"), "recommended_label": rec})
    return out


class DecisionRegistry:
    """The file-discovered DECISION registry — mirrors `runtime/lifter_registry.py:LifterRegistry` /
    `runtime/mark_types.py:MarkTypeRegistry` (the ONE registry mechanism; not a fork). Dict-like
    (`reg[id] -> Decision`, `id in reg`, `.get(id)`, iterate). Adding a decision = dropping a
    `decisions/<id>.py` declaring `DECISION = {...}`; it self-registers.

    The `decision://` resolver reads `.get(id)` to find the pending definition; `as_records()` projects the set
    for a surface. NOTE: `.get` returns the DECLARED ROW (the definition) — STATE is composed separately by
    `compose_state` from the decision_take mark thread (the resolver does both)."""

    def __init__(self):
        self.decisions: dict[str, Decision] = {}

    def discover(self, dirs: list[str]) -> "DecisionRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "DECISION", None)
                if decl is None:               # not a decision module (mirrors NodeRegistry's `run` check)
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "DecisionRegistry":
        """Rebuild from the filesystem (clear + discover) — a REMOVED decision file un-registers.
        Mirrors LifterRegistry/MarkTypeRegistry.rediscover."""
        self.decisions.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> None:
        self.decisions[name] = _build_decision(name, decl)

    def get(self, did: str, default=None):
        """The DECLARED decision row (the spec dict) for an id, or `default` if no such file (the resolver
        RAISES on None — registry-is-truth). Returns the spec dict (not the Decision wrapper), so the resolver
        + compose_state work on the row shape directly."""
        d = self.decisions.get(did)
        return dict(d.spec) if d is not None else default

    def as_records(self) -> list[dict]:
        """The decision set as plain dicts (the declared definitions) for a surface — registry-is-truth: the
        discovered set, never a hand-listed one."""
        return [dict(self.decisions[k].spec) for k in sorted(self.decisions)]

    # --- dict-like (mirrors LifterRegistry) ---
    def __getitem__(self, did: str) -> Decision:
        return self.decisions[did]

    def __contains__(self, did: str) -> bool:
        return did in self.decisions

    def __iter__(self):
        return iter(self.decisions)

    def __len__(self) -> int:
        return len(self.decisions)


if __name__ == "__main__":
    # OPERATIONAL self-test — discover · validate · malformed-fail-loud · compose_state (pending→decided,
    # latest-by-ts) · canonical-address (bare≡global). The END-TO-END resolver+normalization adversarial
    # proof (write a take via the bare form, resolve via the global form) lives in tests/decisions_acceptance.py
    # (it needs the cognition resolver + a store). This self-test mirrors vi_vision's __main__ bar.
    import os as _os
    import sys as _sys
    _here = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    _sys.path.insert(0, _here)                         # repo root on path (run directly: python runtime/decision_registry.py)
    from contracts.address import parse_decision_address, decision_address

    reg = DecisionRegistry().discover([_os.path.join(_here, "decisions")])
    assert "merge-sa-authorize" in reg, f"bootstrap decision not discovered: {list(reg)}"
    row = reg.get("merge-sa-authorize")
    assert row["meaning"] and len(row["options"]) >= 2, row
    assert any(o.get("recommended") for o in row["options"]), "bootstrap should mark a recommended option"

    # canonical address: bare ≡ global (the normalization that keeps the mark key ONE).
    a_bare = decision_address(parse_decision_address("decision://merge-sa-authorize"))
    a_glob = decision_address(parse_decision_address("decision://global/merge-sa-authorize"))
    assert a_bare == a_glob == "decision://global/merge-sa-authorize", (a_bare, a_glob)
    # project frame canonical
    assert decision_address(parse_decision_address("decision://project/p1/x")) == "decision://project/p1/x"

    # compose_state: no take → pending.
    s0 = compose_state(row, [])
    assert s0["state"] == "pending" and s0["decided_value"] is None, s0
    # one take → decided, value = the option label, by/at from the mark.
    s1 = compose_state(row, [{"mark_type": "decision_take", "value": "Stay read-only for now",
                              "by": "operator", "ts": "2026-06-18T00:00:00+00:00"}])
    assert s1["state"] == "decided" and s1["decided_value"] == "Stay read-only for now" \
        and s1["decided_by"] == "operator", s1
    # latest-by-ts wins (out-of-order marks; a non-take mark is ignored).
    s2 = compose_state(row, [
        {"mark_type": "comment", "value": "noise"},
        {"mark_type": "decision_take", "value": "Stay read-only for now", "ts": "2026-06-18T00:00:00+00:00"},
        {"mark_type": "decision_take", "value": "Give it write access", "ts": "2026-06-18T09:00:00+00:00"},
        {"mark_type": "decision_take", "value": "Stay read-only for now", "ts": "2026-06-18T03:00:00+00:00"},
    ])
    assert s2["state"] == "decided" and s2["decided_value"] == "Give it write access", s2

    # malformed rows FAIL LOUD at build.
    _bads = [
        {"id": "x", "options": [{"label": "a"}]},                       # no meaning
        {"id": "x", "meaning": "m", "options": []},                     # empty options
        {"id": "x", "meaning": "m", "options": [{"implication": "no label"}]},  # option no label
        {"id": "x", "meaning": "m", "options": [{"label": "a"}], "scope": "bogus"},  # bad scope
        {"id": "x", "meaning": "m", "options": [{"label": "a"}], "legibility": {"name": "n"}},  # legibility no `is`
        {"id": "y", "meaning": "m", "options": [{"label": "a"}]},       # id != module name
    ]
    for b in _bads:
        try:
            _build_decision("x", b)
            raise SystemExit(f"FAIL: malformed decision did not raise: {b}")
        except DecisionError:
            pass
    print("decision_registry OPERATIONAL self-test: ALL PASS "
          "(discover·validate·malformed-fail-loud·compose_state[pending→decided·latest-by-ts]·canonical-addr)")
