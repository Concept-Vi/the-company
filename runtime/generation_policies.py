"""runtime/generation_policies.py — the file-discovered GENERATION-POLICY registry (Cognition Engine
NEWMOD · O2 · P1).

A GENERATION-POLICY is the declared, per-content GENERATION REGIME a `run_role` call uses — NOT static
knobs in code. The cognition engine WILL hit a generation pathology: greedy temp0 + grammar-constrained
long arrays → a degenerate repetition loop (~20% of real files; input-size does NOT predict it;
`frequency_penalty` is WRONG — it penalises JSON structure). The cure is a **repetition_penalty LADDER**
declared as DATA: `1.1` default → `1.2` on `finish=length` → **fail-loud `degenerate-loop`**. This must be
a POLICY ENTRY with the ladder + the `diff_against_source` flag, tool-configurable — NEVER a hardcoded
constant. (Tim-decision OPEN→leaned: rep_penalty can silently under-capture LEGITIMATE enumeration → a
`diff_against_source` check, NEVER a silent penalty.)

## Why a FILE-DISCOVERED registry, not a python dict (the law made concrete — PART 4.3 + "NOTHING static")
This is THE entry the brief singles out for "NOTHING static": the rep_penalty regime is a registry ROW
with a ladder + a diff-against-source flag, **add-a-row = a FILE**, no code edit — EXACTLY like
roles/skills/projections. NOT `GENERATION_POLICIES = {...}`, and NOT `REP_PENALTY = 1.1` in code.
Dropping a `generation_policies/<id>.py` makes that regime selectable with ZERO code change.

## Why SELF-CONTAINED (mirrors projections.py — NOT a shared base)
Mirrors the MECHANISM of ProjectionRegistry/RoleRegistry/NodeRegistry (`os.listdir`→`importlib`,
fail-loud, id==filename, dict-like, `rediscover`). A STANDALONE copy. The POLICY row shape is its own
(the ladder + flags), so the validator is policy-specific (`_build_policy`).

## The generation-policy schema
Each `generation_policies/<id>.py` declares a module-level `GENERATION_POLICY` dict — a registry ROW:
  - `id`                  — required; MUST equal the module name (addressable by file — fail-loud).
  - `rep_penalty_ladder`  — required; a NON-EMPTY list of floats — the repetition_penalty LADDER
                            (e.g. [1.1, 1.2]): the first value is the default; each next is the
                            escalation on `finish=length`; EXHAUSTING the ladder → fail-loud
                            `degenerate-loop`. DATA, never a code constant. (>=2 entries = a real ladder
                            with an escalation step; a single-entry ladder is allowed = a fixed penalty.)
  - `diff_against_source` — required bool — does this regime DIFF the output against the source on
                            enumerative content (to catch rep_penalty silently under-capturing
                            LEGITIMATE enumeration)? The Tim-decision lean: never a silent penalty.
  - `json_schema`         — optional bool — structured-outputs (json_schema, NOT json_object) for this
                            regime (the capture path). DATA.
  - `temperature`         — optional float — the sampling temperature for this regime (e.g. 0.0 greedy).
  - `budget`              — optional int — a max-tokens budget hint (per-content, not a global constant).
  - `desc`                — optional; operator-facing one-liner.
Every field except `id`+`rep_penalty_ladder`+`diff_against_source` is OPTIONAL. A malformed entry
(no string id / id≠filename / empty-or-non-float ladder / non-bool diff_against_source / unknown field)
FAILS LOUD at discovery — never a silent skip (a non-GENERATION_POLICY / `_`-file is the one that skips).

## The floor
A generation-policy is DECLARED DATA — a regime, not an action. Reading the registry is a READ (the
method is `policy_for` / `as_records`, NEVER a dotted-resolve method — keeping this file clean of the
C9.2 forbidden resolve-call token so it stays floor-safe if/when enrolled in COG_SOURCES).

## Drift home (SD2) + create_*-authorable + the WIRING seam
`generation_policies/AGENTS.md` is the drift home; `tests/generation_policies_acceptance.py` asserts
reflection. The `_build_policy` gate + clean `discover` make it create_*-authorable (a future
`create_generation_policy` reusing this gate — a SEPARATE coordinated wiring pass, NOT built here). The
ENGINE lane wires `run_role` to read the selected policy's ladder; that is also the next pass.

LAWS honoured: no-hardcoding (the rep_penalty regime is FILE-DISCOVERED DATA — never a code constant;
"NOTHING static" made concrete) · reuse-don't-parallel (mirrors ProjectionRegistry/RoleRegistry) · fail
loud (malformed RAISES; exhausting the ladder → fail-loud degenerate-loop is the regime's own contract) ·
the floor (reading a policy is a READ; never resolve/dispatch).
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass


GENERATION_POLICY_FIELDS = (
    "id", "rep_penalty_ladder", "diff_against_source", "json_schema", "temperature", "budget", "desc")
REQUIRED_FIELDS = ("id", "rep_penalty_ladder", "diff_against_source")


@dataclass
class GenerationPolicy:
    """A discovered generation regime — the declared dict (`spec`) verbatim + typed accessors. The
    `rep_penalty_ladder` is the escalation DATA (default → escalate-on-length → fail-loud); the
    `diff_against_source` flag is the never-silently-lossy guard for legitimate enumeration."""
    id: str
    rep_penalty_ladder: list
    diff_against_source: bool
    spec: dict

    @property
    def default_rep_penalty(self) -> float:
        """The first rung — the regime's default repetition_penalty."""
        return float(self.rep_penalty_ladder[0])

    def next_rep_penalty(self, current: float) -> float | None:
        """The NEXT rung above `current` (the escalation on finish=length), or None if the ladder is
        EXHAUSTED — which the engine treats as fail-loud `degenerate-loop` (never a silent give-up).
        A pure READ over the declared ladder (no resolve/dispatch — the floor)."""
        for rung in self.rep_penalty_ladder:
            if float(rung) > float(current):
                return float(rung)
        return None

    @property
    def json_schema(self) -> bool:
        return bool(self.spec.get("json_schema", False))

    @property
    def temperature(self) -> float | None:
        t = self.spec.get("temperature")
        return None if t is None else float(t)

    @property
    def budget(self) -> int | None:
        b = self.spec.get("budget")
        return None if b is None else int(b)

    @property
    def desc(self) -> str | None:
        return self.spec.get("desc")


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_gp_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


def _build_policy(name: str, decl: dict) -> GenerationPolicy:
    """Validate + build a GenerationPolicy. FAIL LOUD on a malformed entry (mirrors _build_projection)."""
    if not isinstance(decl, dict):
        raise TypeError(
            f"generation-policy module {name!r}: GENERATION_POLICY must be a dict, got "
            f"{type(decl).__name__} — fail loud, never a silent malformed policy.")
    pid = decl.get("id")
    if not pid or not isinstance(pid, str):
        raise ValueError(
            f"generation-policy module {name!r}: declares no string `id` — fail loud (never unnamed).")
    if pid != name:
        raise ValueError(
            f"generation-policy module {name!r}: id {pid!r} != module name {name!r} — the id must equal "
            f"the file name (addressable by file). Fail loud.")
    unknown = [k for k in decl if k not in GENERATION_POLICY_FIELDS]
    if unknown:
        raise ValueError(
            f"generation-policy {pid!r}: unknown field(s) {unknown} — the schema is "
            f"{list(GENERATION_POLICY_FIELDS)}. Fail loud (never a silent typo'd field).")
    missing = [k for k in REQUIRED_FIELDS if k not in decl]
    if missing:
        raise ValueError(
            f"generation-policy {pid!r}: missing required field(s) {missing} — a regime MUST declare "
            f"{list(REQUIRED_FIELDS)} (the rep_penalty LADDER as DATA + the diff-against-source guard; "
            f"NOTHING static). Fail loud.")
    ladder = decl.get("rep_penalty_ladder")
    if not isinstance(ladder, (list, tuple)) or not ladder:
        raise ValueError(
            f"generation-policy {pid!r}: `rep_penalty_ladder` must be a NON-EMPTY list of floats (the "
            f"escalation DATA — default → escalate-on-length → fail-loud). Got {ladder!r} — fail loud "
            f"(the rep_penalty regime is DATA, never a code constant).")
    if not all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in ladder):
        raise ValueError(
            f"generation-policy {pid!r}: every rung of `rep_penalty_ladder` must be a number. Got "
            f"{ladder!r} — fail loud.")
    if list(ladder) != sorted(ladder):
        raise ValueError(
            f"generation-policy {pid!r}: `rep_penalty_ladder` must be ASCENDING (each rung escalates "
            f"the penalty). Got {ladder!r} — fail loud (a non-ascending ladder can't escalate).")
    diff = decl.get("diff_against_source")
    if not isinstance(diff, bool):
        raise ValueError(
            f"generation-policy {pid!r}: `diff_against_source` must be a bool (does this regime diff "
            f"output-vs-source to catch silently-lossy enumeration — the never-silent guard). Got "
            f"{diff!r} — fail loud.")
    return GenerationPolicy(id=pid, rep_penalty_ladder=list(ladder), diff_against_source=diff,
                            spec=dict(decl))


class GenerationPolicyRegistry:
    """The file-discovered GENERATION-POLICY registry — mirrors ProjectionRegistry/RoleRegistry/
    NodeRegistry (the ONE registry mechanism). Dict-like. Adding a regime = dropping a
    `generation_policies/<id>.py` declaring `GENERATION_POLICY = {...}`. `run_role` reads the selected
    policy's ladder (registry-is-truth — the rep_penalty regime is DATA, never a code constant)."""

    def __init__(self):
        self.policies: dict[str, GenerationPolicy] = {}

    def discover(self, dirs: list[str]) -> "GenerationPolicyRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "GENERATION_POLICY", None)
                if decl is None:
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "GenerationPolicyRegistry":
        self.policies.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> None:
        self.policies[name] = _build_policy(name, decl)

    # --- the consumer reads (pure reads — the floor; NOTE: `policy_for`, never `resolve`) ---
    def policy_for(self, pid: str) -> GenerationPolicy:
        """The regime for a given content/policy id (the run_role read). FAIL LOUD on an unknown id
        (registry-is-truth — never fabricate a generation regime)."""
        if pid not in self.policies:
            raise ValueError(
                f"unknown generation-policy {pid!r} — registered: {sorted(self.policies)} "
                f"(registry-is-truth: a regime that is not a discovered file does not exist — fail loud).")
        return self.policies[pid]

    def as_records(self) -> list[dict]:
        """The whole policy set as plain dicts (the declared spec verbatim) — for cognition_info."""
        return [dict(self.policies[k].spec) for k in sorted(self.policies)]

    # --- dict-like ---
    def __getitem__(self, pid: str) -> GenerationPolicy:
        return self.policies[pid]

    def __contains__(self, pid: str) -> bool:
        return pid in self.policies

    def __iter__(self):
        return iter(self.policies)

    def __len__(self) -> int:
        return len(self.policies)

    def get(self, pid: str, default=None):
        return self.policies.get(pid, default)
