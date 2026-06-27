"""runtime/guides.py — the file-discovered GUIDE registry (the narrative-guide face).

Tim (2026-06-28): the Company needs skills/guides on how to USE it — and he settled the shape as
"one entry, two faces." A SKILL (`runtime/skills.py`) is the dense instruction-unit a ROLE reads
mid-task; a GUIDE is the narrative how-to a human/agent reads to LEARN a part of the system. The
3-review verdict (architecture + grounding + security, 2026-06-27) was sharp: a guide is NOT a
field on the SKILL row — the skill schema is a strict closed-set (`runtime/skills.py:ENTRY_FIELDS`)
and co-locating two authored bodies in one file would be TWO HOMES sharing a filename (drift, the
exact failure one-home exists to prevent). So a guide is its OWN file-discovered registry, keyed by
the TARGET address it documents, holding only REFERENCES to its sources (`grounded_from`) — never a
copy. one-home satisfied: the guide references the target's source, it does not duplicate it.

## Why a registry, not a literal (embodies ~/.vi/rules/no-hardcoding.md)
A guide is the same KIND of thing roles, node-types, skills, and contexts are: a declared,
discoverable unit of vocabulary. So it is NOT a literal — it is a FILE-DISCOVERED registry, mirroring
the ONE registry pattern (`runtime/skills.py:SkillRegistry` / `runtime/roles.py:RoleRegistry` /
`runtime/registry.py:NodeRegistry`). Adding a guide = dropping a `guides/<id>.py` file; it
self-registers + is addressable as `guide://<id>`; a removed file un-registers on `rediscover`.
reuse-don't-parallel: this REUSES skills.py's `_load_module` importlib helper (the same discovery
mechanism), and mirrors the dict-like surface EXACTLY — it does NOT fork a new globbing/markdown
mechanism. It carries its OWN richer schema (a guide row ≠ a skill row), exactly as roles/nodes each
have their own builder while sharing the mechanism.

## The schema (a guide ROW — richer than a skill row, by design)
Each `guides/<id>.py` declares a module-level `GUIDE` dict:
  - `id`            — required; MUST equal the module name (addressable by file — fail-loud otherwise).
  - `content`       — required; the resolvable VALUE: the narrative how-to (markdown) a learner reads.
                      This is what `guide://<id>` resolves TO (a read — the floor: no resolve/dispatch).
  - `target`        — required; the ADDRESS this guide documents (e.g. `skill://summarize`, a `cap://`,
                      a domain). A guide is ABOUT something — keyed by what it teaches. fail-loud if absent.
  - `grounded_from` — required, NON-EMPTY list of source addresses the guide was authored FROM (the
                      MANDATORY-GROUNDING gate from the review: a guide with no grounding FAILS LOUD —
                      "abort on cold". This is what makes a guide true-by-construction, not invented).
  - `source_hash`   — optional; a content hash of the grounded_from sources at authoring time. Drives
                      FRESHNESS: when the sources change, the hash differs → the guide is STALE and a
                      re-author is due. (Reuses the hash-diff IDEA, not the embedding-reconcile fn.)
  - `label`         — operator-facing short name (optional; like roles/skills have).
  - `description`   — operator-facing one-liner (optional).
Every field except `id`+`content`+`target`+`grounded_from` is OPTIONAL. A malformed entry (no string
id / id≠filename / empty content / no target / empty grounded_from / unknown field) FAILS LOUD at
discovery — never a silent skip (a non-entry/`_`-file is the one that skips, mirroring SkillRegistry).

## Drift home
`guides/AGENTS.md` is the constitution (drift home). `tests/guides_acceptance.py` asserts every
discovered guide is reflected there (mirrors `tests/skills_contexts_acceptance.py`).

## Seam
discovered by `GuideRegistry` (mirrors `SkillRegistry`); resolved via
`runtime/cognition.py:resolve_address` (the `guide://` dispatch branch); the scheme is declared
additively in `contracts/address.py:SCHEMES`.

LAWS honoured: no-hardcoding (guides are FILE-DISCOVERED DATA, never a literal list) · reuse-don't-
parallel (REUSES `_load_module`, mirrors the dict-like registry surface; own schema like roles/nodes) ·
fail loud (a malformed entry RAISES at discovery; an unknown id RAISES on lookup — registry-is-truth,
never fabricate) · the floor (resolving a guide is a READ — return its content, no resolve/dispatch) ·
grounding-mandatory (an ungrounded guide RAISES — a guide is true-by-construction or it does not exist).
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from runtime.skills import _load_module  # REUSE the schema-agnostic importlib helper (don't-parallel)


# the schema field names a guide entry MAY declare. id+content+target+grounded_from required; rest optional.
GUIDE_FIELDS = ("id", "content", "target", "grounded_from", "source_hash", "label", "description")


@dataclass
class GuideEntry:
    """A discovered guide row — the narrative how-to for a target address. `content` is what the
    address resolves TO (a read — the floor). Carries the declared dict (`spec`) verbatim + typed
    accessors."""
    id: str
    content: str
    target: str
    grounded_from: list
    spec: dict
    kind: str = "guide"

    @property
    def source_hash(self) -> str | None:
        return self.spec.get("source_hash")

    @property
    def label(self) -> str:
        return self.spec.get("label") or self.id

    @property
    def description(self) -> str | None:
        return self.spec.get("description")


def _build_guide(name: str, decl: dict) -> GuideEntry:
    """Validate + build a GuideEntry from a module's declared `GUIDE` dict. FAIL LOUD on a malformed
    entry (mirrors SkillRegistry._build_entry): a declared entry with a bad shape RAISES — it is NOT
    silently skipped (a non-entry file is the one that skips). registry-is-truth: never register a
    fabricated/unnamed/ungrounded guide."""
    if not isinstance(decl, dict):
        raise TypeError(
            f"guide module {name!r}: GUIDE must be a dict (the declared guide schema), got "
            f"{type(decl).__name__} — fail loud, never a silent malformed guide.")
    gid = decl.get("id")
    if not gid or not isinstance(gid, str):
        raise ValueError(
            f"guide module {name!r}: GUIDE declares no string `id` — every guide declares its id "
            f"(fail loud; author from the registry, never an unnamed guide).")
    if gid != name:
        raise ValueError(
            f"guide module {name!r}: GUIDE id {gid!r} != module name {name!r} — the id must equal the "
            f"file name (so a guide is addressable by file, mirroring skills/roles). Fail loud.")
    unknown = [k for k in decl if k not in GUIDE_FIELDS]
    if unknown:
        raise ValueError(
            f"guide {gid!r}: unknown guide-schema field(s) {unknown} — the schema is "
            f"{list(GUIDE_FIELDS)}. Fail loud (never a silent typo'd field no consumer reads).")
    content = decl.get("content")
    if not isinstance(content, str) or not content:
        raise ValueError(
            f"guide {gid!r}: must declare non-empty string `content` (what guide://{gid} resolves TO "
            f"— the narrative a learner reads). Got {content!r} — fail loud (never resolve to empty).")
    target = decl.get("target")
    if not isinstance(target, str) or not target:
        raise ValueError(
            f"guide {gid!r}: must declare non-empty string `target` (the address this guide documents "
            f"— a guide is ABOUT something). Got {target!r} — fail loud.")
    grounded = decl.get("grounded_from")
    if not isinstance(grounded, list) or not grounded or not all(isinstance(x, str) and x for x in grounded):
        raise ValueError(
            f"guide {gid!r}: must declare a NON-EMPTY list `grounded_from` of source addresses (the "
            f"mandatory-grounding gate — a guide is authored FROM real sources or it does not exist; "
            f"abort-on-cold). Got {grounded!r} — fail loud (never an ungrounded/invented guide).")
    return GuideEntry(id=gid, content=content, target=target, grounded_from=list(grounded), spec=dict(decl))


class GuideRegistry:
    """The file-discovered GUIDE registry — a `guides/<id>.py` declares a module-level `GUIDE` dict;
    `guide://<id>` resolves to its `content` (the narrative how-to a learner reads). Mirrors the
    dict-like surface of `runtime/skills.py:SkillRegistry` (reuse-don't-parallel — same mechanism,
    own schema). Dict-like (`reg[id] -> GuideEntry`, `id in reg`, `.get(id)`); adding a guide = dropping
    a `guides/<id>.py` file."""

    def __init__(self):
        self.entries: dict[str, GuideEntry] = {}

    def discover(self, dirs: list[str]) -> "GuideRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "GUIDE", None)
                if decl is None:                  # not a guide module (mirrors SkillRegistry's ATTR check)
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "GuideRegistry":
        """Rebuild from the filesystem (clear + discover) — so a REMOVED guide file actually
        un-registers (discover() only adds). Mirrors SkillRegistry.rediscover."""
        self.entries.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> None:
        self.entries[name] = _build_guide(name, decl)

    def read(self, guide_id: str) -> str:
        """Read an id → its declared `content` (the READ the address scheme answers — the floor: no
        resolve/dispatch, just return the declared value). NAMED `read` (not `resolve`) on purpose —
        reading a guide IS a read, and the cognition layer keeps a dotted-resolve a forbidden-only
        token (the C9.2 source-invariant; same reasoning as SkillRegistry.read). FAIL LOUD on an
        unknown id (registry-is-truth — NEVER fabricate a missing guide)."""
        if guide_id not in self.entries:
            raise ValueError(
                f"unknown guide {guide_id!r} — registered guides: {sorted(self.entries)} "
                f"(registry-is-truth: a guide://{guide_id} that is not a discovered file does not "
                f"resolve — fail loud, never fabricate).")
        return self.entries[guide_id].content

    # --- dict-like (mirrors SkillRegistry) ---
    def __getitem__(self, guide_id: str) -> GuideEntry:
        return self.entries[guide_id]

    def __contains__(self, guide_id: str) -> bool:
        return guide_id in self.entries

    def __iter__(self):
        return iter(self.entries)

    def get(self, guide_id: str, default=None):
        return self.entries.get(guide_id, default)
