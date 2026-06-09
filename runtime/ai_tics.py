"""runtime/ai_tics.py — the file-discovered AI-TIC registry (Cognition Engine NEWMOD · M4 · P1).

An AI-TIC is a declared, CATALOGUED generic-AI fingerprint — a recurring tell of machine-generated
(not Tim-meaning) content: framework-imposition · versioning · false-finality · silent-fallback ·
agent-arch · closure-form · MVP. The fingerprint pass (M4, the inversion) matches the coined-vocab
projection against THIS registry → `ai-fingerprint` marks (`mark_types/ai_fingerprint`, direction
`subtract`): generic+recurring = a tic to SUBTRACT (denoising = surfacing, opposite direction);
idiosyncratic+recurring = gold. The catalogue is EXTENSIBLE (a new tic = a new file) — Tim's own
named frustrations seed it.

## Why a FILE-DISCOVERED registry, not a python dict (PART 4.3)
**add-a-row = a FILE, no code edit.** The tic catalogue must be directory-discovered, file-per-entry
+ create_*-authorable, EXACTLY like roles/skills/projections — NOT `AI_TICS={...}`. Dropping an
`ai_tics/<id>.py` adds that fingerprint to the subtraction pass with ZERO code change.

## Why SELF-CONTAINED (mirrors projections.py)
Mirrors the MECHANISM of ProjectionRegistry/RoleRegistry/NodeRegistry. A STANDALONE copy. The AI-TIC
row shape is its own (the markers/cue list), so the validator is tic-specific (`_build_tic`).

## The AI-tic schema
Each `ai_tics/<id>.py` declares a module-level `AI_TIC` dict — a registry ROW:
  - `id`       — required; MUST equal the module name (addressable by file — fail-loud otherwise).
                 The tic name (e.g. `versioning`, `false_finality`).
  - `markers`  — required; a NON-EMPTY list of strings — the textual/structural CUES the fingerprint
                 pass matches against the coined-vocab projection (e.g. for `versioning`: "v2", "round 2",
                 "-final"). DATA — the catalogue, not a code branch. (The matcher is a later pass; this is
                 the vocabulary it reads.)
  - `label`    — optional; operator-facing short name.
  - `desc`     — optional; operator-facing one-liner — what the tic IS + why it's a generic tell.
Every field except `id`+`markers` is OPTIONAL. A malformed entry (no string id / id≠filename / empty-or-
non-string-list markers / unknown field) FAILS LOUD at discovery — never a silent skip.

## The floor
An AI-tic is DECLARED DATA — a catalogue entry, not an action. Reading is a READ (`get`/`as_records`,
never `resolve`). The fingerprint pass appends a finding (a mark), never resolves — the floor holds.

## Drift home (SD2) + create_*-authorable + WIRING seam
`ai_tics/AGENTS.md` is the drift home; `tests/ai_tics_acceptance.py` asserts reflection. The
`_build_tic` gate + clean `discover` make it create_*-authorable (a future `create_ai_tic` reusing this
gate — a SEPARATE coordinated wiring pass, NOT built here). The fingerprint mark-pass (Group M, SUITE
lane) reads this registry; that is the next pass.

LAWS honoured: no-hardcoding (the tic catalogue FILE-DISCOVERED, never a literal) · reuse-don't-parallel
(mirrors ProjectionRegistry/RoleRegistry) · fail loud (malformed RAISES; unknown id RAISES) · the floor
(reading a tic is a READ).
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass


AI_TIC_FIELDS = ("id", "markers", "label", "desc")


@dataclass
class AiTic:
    """A discovered AI-fingerprint catalogue entry — the declared dict (`spec`) verbatim + typed
    accessors. `markers` is the cue vocabulary the fingerprint pass matches (the subtraction set)."""
    id: str
    markers: list
    spec: dict

    @property
    def label(self) -> str:
        return self.spec.get("label") or self.id

    @property
    def desc(self) -> str | None:
        return self.spec.get("desc")


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_tic_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


def _build_tic(name: str, decl: dict) -> AiTic:
    """Validate + build an AiTic. FAIL LOUD on a malformed entry (mirrors _build_projection)."""
    if not isinstance(decl, dict):
        raise TypeError(
            f"ai-tic module {name!r}: AI_TIC must be a dict, got {type(decl).__name__} — fail loud, "
            f"never a silent malformed tic.")
    tid = decl.get("id")
    if not tid or not isinstance(tid, str):
        raise ValueError(
            f"ai-tic module {name!r}: declares no string `id` — fail loud (never unnamed).")
    if tid != name:
        raise ValueError(
            f"ai-tic module {name!r}: id {tid!r} != module name {name!r} — the id must equal the file "
            f"name (addressable by file). Fail loud.")
    unknown = [k for k in decl if k not in AI_TIC_FIELDS]
    if unknown:
        raise ValueError(
            f"ai-tic {tid!r}: unknown field(s) {unknown} — the schema is {list(AI_TIC_FIELDS)}. "
            f"Fail loud (never a silent typo'd field).")
    markers = decl.get("markers")
    if not isinstance(markers, (list, tuple)) or not markers:
        raise ValueError(
            f"ai-tic {tid!r}: `markers` must be a NON-EMPTY list of strings (the cues the fingerprint "
            f"pass matches — the catalogue, not a code branch). Got {markers!r} — fail loud.")
    if not all(isinstance(m, str) and m for m in markers):
        raise ValueError(
            f"ai-tic {tid!r}: every marker must be a non-empty string. Got {markers!r} — fail loud.")
    return AiTic(id=tid, markers=list(markers), spec=dict(decl))


class AiTicRegistry:
    """The file-discovered AI-TIC registry — mirrors ProjectionRegistry/RoleRegistry/NodeRegistry (the
    ONE registry mechanism). Dict-like. Adding a tic = dropping an `ai_tics/<id>.py` declaring
    `AI_TIC = {...}`. The fingerprint pass reads `as_records()` (registry-is-truth — the subtraction
    catalogue is the discovered set, never a hand-listed one)."""

    def __init__(self):
        self.tics: dict[str, AiTic] = {}

    def discover(self, dirs: list[str]) -> "AiTicRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "AI_TIC", None)
                if decl is None:
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "AiTicRegistry":
        self.tics.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> None:
        self.tics[name] = _build_tic(name, decl)

    # --- the consumer reads (pure reads — the floor) ---
    def all_markers(self) -> list[str]:
        """The flat, deduped cue set across every tic — the fingerprint pass's match vocabulary.
        Sorted for determinism."""
        seen: list[str] = []
        for k in sorted(self.tics):
            for m in self.tics[k].markers:
                if m not in seen:
                    seen.append(m)
        return sorted(seen)

    def as_records(self) -> list[dict]:
        """The whole tic catalogue as plain dicts (the declared spec verbatim) — for cognition_info."""
        return [dict(self.tics[k].spec) for k in sorted(self.tics)]

    # --- dict-like ---
    def __getitem__(self, tid: str) -> AiTic:
        return self.tics[tid]

    def __contains__(self, tid: str) -> bool:
        return tid in self.tics

    def __iter__(self):
        return iter(self.tics)

    def __len__(self) -> int:
        return len(self.tics)

    def get(self, tid: str, default=None):
        return self.tics.get(tid, default)
