"""runtime/forms.py — the file-discovered FORM registry (Cognition Engine NEWMOD · P1 · effort-routing).

A FORM is a declared FILE-SHAPE → ROUTING rule: it recognises a kind of corpus unit by its shape
(a log · a registry/index · a decision note · free prose · a stub) and routes it to an EFFORT BAND
(the restored effort-routing-by-form discipline: ~half a corpus is bookkeeping — DON'T burn full
capture depth on logs). The capture pass reads a unit's form to TIER the work (legibility = the cheap
broad pass · deep = the heavier pass) and may pick a generation-policy by form. "Effort-routing by
form" made DATA, not a hardcoded if-ladder.

## Why a FILE-DISCOVERED registry, not a python dict (PART 4.3)
**add-a-row = a FILE, no code edit.** The form→routing vocabulary must be directory-discovered,
file-per-entry + create_*-authorable, EXACTLY like roles/skills/projections — NOT `FORMS={...}`.
Dropping a `forms/<id>.py` adds that shape→routing rule with ZERO code change.

## Why SELF-CONTAINED (mirrors projections.py)
Mirrors the MECHANISM of ProjectionRegistry/RoleRegistry/NodeRegistry. A STANDALONE copy. The FORM row
shape is its own (a `match` callable + a stage band), so the validator is form-specific (`_build_form`).

## The form schema
Each `forms/<id>.py` declares a module-level `FORM` dict — a registry ROW:
  - `id`        — required; MUST equal the module name (addressable by file — fail-loud otherwise).
                  The form name (`log`, `registry`, `decision`, `prose`, `stub`).
  - `match`     — required; a CALLABLE `(text:str, *, meta:dict|None=None) -> bool` — does this unit
                  HAVE this shape? Deterministic recogniser (a READ — never a resolve/dispatch). The
                  router reads the FIRST form whose match() is True (declaration order by id; an
                  explicit fallthrough form is the `prose` default).
  - `stage`     — required; the effort BAND this form routes to — open vocab ("legibility" the cheap
                  broad pass · "deep" the heavier pass · "skip" bookkeeping not worth capture). DATA.
  - `policy`    — optional; the generation-policy id this form selects (e.g. a log → a cheap regime).
                  Ties forms → generation_policies (the per-content regime by shape). DATA.
  - `fallthrough`— optional bool (default False); is this the CATCH-ALL form (matches broadly, the last
                  resort)? `route()` checks all non-fallthrough forms FIRST (so a narrow form claims a
                  unit before the catch-all), then the fallthrough forms — DATA-driven ordering, no
                  hardcoded form name. Exactly one `prose`-style fallthrough is the norm.
  - `desc`      — optional; operator-facing one-liner.
Every field except `id`+`match`+`stage` is OPTIONAL. A malformed entry (no string id / id≠filename /
non-callable match / empty stage / unknown field) FAILS LOUD at discovery — never a silent skip.

## The floor
A form is DECLARED DATA + a deterministic recogniser (a READ). Reading the registry / running a `match`
is a READ (the method is `route` / `as_records`, never `resolve`). The router PICKS an effort band; it
never resolves/dispatches — the floor holds.

## Drift home (SD2) + create_*-authorable + WIRING seam
`forms/AGENTS.md` is the drift home; `tests/forms_acceptance.py` asserts reflection. The `_build_form`
gate + clean `discover` make it create_*-authorable (a future `create_form` reusing this gate — a
SEPARATE coordinated wiring pass, NOT built here). The capture lane reads `route()` to tier the work;
that is the next pass.

LAWS honoured: no-hardcoding (form→routing FILE-DISCOVERED, never a literal if-ladder) · reuse-don't-parallel
(mirrors ProjectionRegistry/RoleRegistry) · fail loud (malformed RAISES; an empty registry route RAISES —
never a silent un-routed unit) · the floor (a form match is a READ).
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass


FORM_FIELDS = ("id", "match", "stage", "policy", "fallthrough", "desc")
REQUIRED_FIELDS = ("id", "match", "stage")


@dataclass
class Form:
    """A discovered file-shape→routing rule — the declared dict (`spec`) verbatim + typed accessors. The
    `match` callable recognises the shape (a READ); `stage` is the effort band the router assigns."""
    id: str
    stage: str
    spec: dict

    @property
    def match(self):
        return self.spec["match"]

    @property
    def policy(self) -> str | None:
        return self.spec.get("policy")

    @property
    def fallthrough(self) -> bool:
        return bool(self.spec.get("fallthrough", False))

    @property
    def desc(self) -> str | None:
        return self.spec.get("desc")


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_form_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


def _build_form(name: str, decl: dict) -> Form:
    """Validate + build a Form. FAIL LOUD on a malformed entry (mirrors _build_projection)."""
    if not isinstance(decl, dict):
        raise TypeError(
            f"form module {name!r}: FORM must be a dict, got {type(decl).__name__} — fail loud, never "
            f"a silent malformed form.")
    fid = decl.get("id")
    if not fid or not isinstance(fid, str):
        raise ValueError(
            f"form module {name!r}: declares no string `id` — fail loud (never unnamed).")
    if fid != name:
        raise ValueError(
            f"form module {name!r}: id {fid!r} != module name {name!r} — the id must equal the file "
            f"name (addressable by file). Fail loud.")
    unknown = [k for k in decl if k not in FORM_FIELDS]
    if unknown:
        raise ValueError(
            f"form {fid!r}: unknown field(s) {unknown} — the schema is {list(FORM_FIELDS)}. Fail loud "
            f"(never a silent typo'd field).")
    missing = [k for k in REQUIRED_FIELDS if k not in decl]
    if missing:
        raise ValueError(
            f"form {fid!r}: missing required field(s) {missing} — a form MUST declare "
            f"{list(REQUIRED_FIELDS)} (match=the recogniser · stage=the effort band). Fail loud.")
    match = decl.get("match")
    if not callable(match):
        raise ValueError(
            f"form {fid!r}: `match` must be a callable (text, *, meta=None) -> bool — the deterministic "
            f"shape recogniser. Got {type(match).__name__} — fail loud.")
    stage = decl.get("stage")
    if not isinstance(stage, str) or not stage:
        raise ValueError(
            f"form {fid!r}: `stage` must be a non-empty string (the effort band — legibility/deep/skip). "
            f"Got {stage!r} — fail loud.")
    ft = decl.get("fallthrough")
    if ft is not None and not isinstance(ft, bool):
        raise ValueError(
            f"form {fid!r}: `fallthrough` (when present) must be a bool (is this the catch-all checked "
            f"last). Got {ft!r} — fail loud.")
    return Form(id=fid, stage=stage, spec=dict(decl))


class FormRegistry:
    """The file-discovered FORM registry — mirrors ProjectionRegistry/RoleRegistry/NodeRegistry (the ONE
    registry mechanism). Dict-like. Adding a form = dropping a `forms/<id>.py` declaring `FORM = {...}`.
    The capture lane reads `route()` to tier the work by shape (registry-is-truth — effort-routing is
    DATA, never a hardcoded if-ladder)."""

    def __init__(self):
        self.forms: dict[str, Form] = {}

    def discover(self, dirs: list[str]) -> "FormRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "FORM", None)
                if decl is None:
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "FormRegistry":
        self.forms.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> None:
        self.forms[name] = _build_form(name, decl)

    # --- the consumer reads (pure reads — the floor; NOTE: `route`, never `resolve`) ---
    def route(self, text: str, *, meta: dict | None = None) -> Form:
        """The FIRST matching form for this unit — the effort-routing read. NON-fallthrough forms are
        checked FIRST (a narrow form claims a unit before the catch-all), THEN fallthrough forms — a
        DATA-driven ordering (the `fallthrough` flag), no hardcoded form name. Within each group, id
        order (deterministic). A deterministic match is a READ (the floor). FAIL LOUD if NO form matches
        (never a silently un-routed unit — declare a `fallthrough` form that matches anything)."""
        if not self.forms:
            raise ValueError("FormRegistry is empty — no form to route to (fail loud; discover() first).")

        def _matches(form: Form) -> bool:
            try:
                return bool(form.match(text, meta=meta))
            except TypeError:
                return bool(form.match(text))    # tolerate a 1-arg matcher

        specific = [k for k in sorted(self.forms) if not self.forms[k].fallthrough]
        catchall = [k for k in sorted(self.forms) if self.forms[k].fallthrough]
        for k in specific + catchall:
            if _matches(self.forms[k]):
                return self.forms[k]
        raise ValueError(
            f"no form matched the unit (registered: {sorted(self.forms)}) — fail loud (declare a "
            f"fallthrough form that matches anything, never a silently un-routed unit).")

    def as_records(self) -> list[dict]:
        """The whole form set as plain dicts — the `match` callable is replaced by its qualname (a
        callable can't serialize to a face). For cognition_info (SURFACE lane)."""
        out = []
        for k in sorted(self.forms):
            spec = dict(self.forms[k].spec)
            fn = spec.get("match")
            spec["match"] = getattr(fn, "__qualname__", repr(fn))
            out.append(spec)
        return out

    # --- dict-like ---
    def __getitem__(self, fid: str) -> Form:
        return self.forms[fid]

    def __contains__(self, fid: str) -> bool:
        return fid in self.forms

    def __iter__(self):
        return iter(self.forms)

    def __len__(self) -> int:
        return len(self.forms)

    def get(self, fid: str, default=None):
        return self.forms.get(fid, default)
