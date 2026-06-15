"""runtime/attachment_types.py — the file-discovered ATTACHMENT-TYPE registry for channels.

An ATTACHMENT-TYPE is a declared KIND of thing that can be bound to a channel (Tim 2026-06-15:
"channels can have things attached, like documentation, the recall system, the cloning system, as
attachments… so the channel set-up can be parametrically generated, things added and removed as the
channel evolves"). The set of kinds is a REGISTRY — add a kind = drop an `attachment_types/<id>.py`
declaring `ATTACHMENT_TYPE = {...}`; no code change (the no-hardcoding / Heart law).

This is the TYPE registry (the kinds). The BINDINGS (a channel actually attached to a target) are
runtime records in runtime/cc_attachments.py — id-keyed flat files, the cc_board precedent — because
bindings are added/removed dynamically as a channel evolves (data), not deliberately-authored type defs.

## The attachment-type schema — each `attachment_types/<id>.py` declares a module-level dict:
  - id          — required; MUST equal the module name.
  - label       — optional; human label.
  - target_kind — optional; what a binding's `target` field holds + how to read it:
                  "address" (an addr like board://<id> or session://<id> — opaque, resolve by scheme),
                  "path" (a filesystem path, e.g. a doc), "scope" (a selector, e.g. a recall scope).
                  Default "address".
  - multi       — optional bool; may a channel hold MANY of this type? Default True.
  - desc        — optional; operator-facing one-liner.
A malformed entry FAILS LOUD at discovery.

LAWS honoured: no-hardcoding · reuse-don't-parallel (mirrors SourceTypeRegistry) · fail loud · the floor.
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass


ATTACHMENT_TYPE_FIELDS = ("id", "label", "target_kind", "multi", "desc")
REQUIRED_FIELDS = ("id",)
TARGET_KINDS = ("address", "path", "scope")


@dataclass
class AttachmentType:
    id: str
    spec: dict

    @property
    def label(self) -> str:
        return self.spec.get("label") or self.id

    @property
    def target_kind(self) -> str:
        return self.spec.get("target_kind") or "address"

    @property
    def multi(self) -> bool:
        return self.spec.get("multi", True)

    @property
    def desc(self):
        return self.spec.get("desc")


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_at_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


def _build_attachment_type(name: str, decl: dict) -> AttachmentType:
    """Validate + build an AttachmentType. FAIL LOUD on a malformed entry."""
    if not isinstance(decl, dict):
        raise TypeError(
            f"attachment-type module {name!r}: ATTACHMENT_TYPE must be a dict, got {type(decl).__name__} — fail loud.")
    rid = decl.get("id")
    if not rid or not isinstance(rid, str):
        raise ValueError(f"attachment-type module {name!r}: declares no string `id` — fail loud (never unnamed).")
    if rid != name:
        raise ValueError(
            f"attachment-type module {name!r}: id {rid!r} != module name {name!r} — the id must equal the "
            f"file name. Fail loud.")
    unknown = [k for k in decl if k not in ATTACHMENT_TYPE_FIELDS]
    if unknown:
        raise ValueError(
            f"attachment-type {rid!r}: unknown field(s) {unknown} — schema is {list(ATTACHMENT_TYPE_FIELDS)}. Fail loud.")
    tk = decl.get("target_kind")
    if tk is not None and tk not in TARGET_KINDS:
        raise ValueError(
            f"attachment-type {rid!r}: target_kind {tk!r} not in {list(TARGET_KINDS)} — fail loud.")
    return AttachmentType(id=rid, spec=dict(decl))


class AttachmentTypeRegistry:
    """The file-discovered ATTACHMENT-TYPE registry — mirrors SourceTypeRegistry. Dict-like. Adding a
    kind = dropping an `attachment_types/<id>.py` declaring `ATTACHMENT_TYPE = {...}` (no code change)."""

    def __init__(self):
        self.attachment_types: dict[str, AttachmentType] = {}

    def discover(self, dirs: list[str]) -> "AttachmentTypeRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "ATTACHMENT_TYPE", None)
                if decl is None:
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "AttachmentTypeRegistry":
        self.attachment_types.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> None:
        self.attachment_types[name] = _build_attachment_type(name, decl)

    def as_records(self) -> list[dict]:
        return [dict(self.attachment_types[k].spec) for k in sorted(self.attachment_types)]

    # --- dict-like ---
    def __getitem__(self, rid: str) -> AttachmentType:
        return self.attachment_types[rid]

    def __contains__(self, rid: str) -> bool:
        return rid in self.attachment_types

    def __iter__(self):
        return iter(self.attachment_types)

    def __len__(self) -> int:
        return len(self.attachment_types)

    def get(self, rid: str, default=None):
        return self.attachment_types.get(rid, default)
