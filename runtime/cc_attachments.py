"""runtime/cc_attachments.py — CHANNEL-ATTACHMENT bindings: bind a target (a board item, a session, a
doc, a recall scope, the cloning capability) to a channel, as a file-discovered REGISTRY OF BINDINGS.

Tim 2026-06-15: "channels can have things attached… so the channel set-up can be parametrically
generated, things added and removed as the channel evolves." Built per the fork's scout-surfaced
refinement (board://item-e523b30d), CONFIRMED by the lead:
  • channel-attachment is its OWN registry of BINDING ROWS — {id, channel, attachment_type, target, added}
    — NOT a mutable `attachments` field on the channel record (so we never edit cc_channels.py; a future
    consumer mutating the channel record can't desync the bindings, and add/remove = add/remove a row).
  • the §3 MANIFEST ({sessions, docs, recall_scope, …}) is a PROJECTION of the rows grouped by type,
    a VIEW computed on read — not stored. (The Heart: the manifest is a projection of the registry.)
  • `target` is an OPAQUE ref (e.g. board://<id>, session://<id>) — stored verbatim, resolved by the
    address scheme; never parsed here.
  • channel existence is validated by IMPORTING cc_channels._read_channel READ-ONLY — file-disjoint
    (this module never writes cc_channels' records).

Storage mirrors cc_board: id-keyed FLAT at channel-memory/channel_attachments/<id>.md (frontmatter row +
empty body), durable via store.fs_store._atomic_write_fsync, parsed via lifters.frontmatter.

attachment_type is a registry ref → validated fail-loud against runtime/attachment_types (no hardcoding).
FOLLOW-UP (lead's suite.py lane, NOT done here to avoid concurrent suite.py edits / the committer-collision
hazard): promote attachment_type to a first-class _CORPUS_REGISTRIES kind so create_*/cognition_info see it.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml

from lifters.frontmatter import _extract as _fm_extract
from store.fs_store import _atomic_write_fsync
from runtime.attachment_types import AttachmentTypeRegistry

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATTACHMENT_TYPES_DIR = os.path.join(REPO, "attachment_types")
ATTACHMENTS_DIR = os.path.join(REPO, "channel-memory", "channel_attachments")
FRONTMATTER_KEYS = ("id", "channel", "attachment_type", "target", "added")


class AttachmentError(RuntimeError):
    """An attachment op could not run — raised TEACHING-loud (never a silent no-op). Mirrors BoardError."""


# ── the attachment-TYPE registry (lazy singleton; reset re-reads the dir — proves add-a-row-is-live) ──
_TYPES: AttachmentTypeRegistry | None = None


def _types_reg() -> AttachmentTypeRegistry:
    global _TYPES
    if _TYPES is None:
        _TYPES = AttachmentTypeRegistry().discover([ATTACHMENT_TYPES_DIR])
    return _TYPES


def reset_registry() -> None:
    """Drop the cached type registry so the NEXT access re-reads attachment_types/ (a fresh kind is live)."""
    global _TYPES
    _TYPES = None
    _types_reg()


def attachment_types() -> list[str]:
    """The registered attachment kinds (sorted ids)."""
    return sorted(_types_reg())


# ── channel existence (READ-ONLY import of cc_channels — file-disjoint) ──
def _channel_exists(channel: str) -> bool:
    """Does the named channel exist? Reads the channel record via cc_channels._read_channel READ-ONLY.
    This module NEVER writes a channel record (file-disjoint from cc_channels.py)."""
    try:
        from runtime.cc_channels import _read_channel
    except Exception:
        return False
    return _read_channel(channel) is not None


# ── helpers (mirror cc_board) ──────────────────────────────────────────────────────────────────────────
def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return "att-" + uuid.uuid4().hex[:8]


def _dir(attachments_dir: str | None) -> str:
    return attachments_dir or ATTACHMENTS_DIR


def _path(attachments_dir: str | None, aid: str) -> str:
    return os.path.join(_dir(attachments_dir), f"{aid}.md")


def _render(record: dict) -> str:
    fm = {k: record[k] for k in FRONTMATTER_KEYS if k in record}
    return "---\n" + yaml.dump(fm, sort_keys=False, allow_unicode=True) + "---\n"


def _read_record(path: str) -> dict | None:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        meta = _fm_extract(f.read()) or {}
    return meta or None


def _write(attachments_dir: str | None, record: dict) -> None:
    d = _dir(attachments_dir)
    os.makedirs(d, exist_ok=True)
    _atomic_write_fsync(Path(_path(attachments_dir, record["id"])), _render(record))


# ── the ops ──────────────────────────────────────────────────────────────────────────────────────────
def attach(channel: str, attachment_type: str, target: str, *,
           require_channel: bool = True, attachments_dir: str | None = None) -> dict:
    """BIND `target` to `channel` as an attachment of `attachment_type`. Validates the type against the
    registry (fail-loud), validates the channel exists (read-only), enforces `multi` (a non-multi type
    may bind to a channel only once), and persists an id-keyed binding row. Returns the binding record.
    `target` is stored VERBATIM (opaque ref — board://<id>, session://<id>, a path, a scope)."""
    reg = _types_reg()
    if attachment_type not in reg:
        raise AttachmentError(
            f"unknown attachment_type {attachment_type!r} — valid: {attachment_types()}. "
            f"(attachment_type is a registry ref; add an attachment_types/<id>.py to extend.)")
    if not channel:
        raise AttachmentError("attach() needs a `channel`.")
    if not target:
        raise AttachmentError("attach() needs a `target` (the opaque ref to bind — e.g. board://<id>).")
    if require_channel and not _channel_exists(channel):
        raise AttachmentError(
            f"channel {channel!r} not found (no record via cc_channels._read_channel) — create it first, "
            f"or pass require_channel=False for a forward binding. Fail loud, never a dangling attach.")
    if not reg[attachment_type].multi:
        existing = [a for a in list_attachments(channel=channel, attachments_dir=attachments_dir)
                    if a.get("attachment_type") == attachment_type]
        if existing:
            raise AttachmentError(
                f"attachment_type {attachment_type!r} is non-multi (multi=false) and channel {channel!r} "
                f"already has one ({existing[0]['id']} → {existing[0].get('target')}). Detach it first.")
    record = {"id": _new_id(), "channel": channel, "attachment_type": attachment_type,
              "target": target, "added": _now()}
    _write(attachments_dir, record)
    return record


def detach(attachment_id: str, *, attachments_dir: str | None = None) -> dict:
    """Remove a binding (presence=truth). Fail-loud if it doesn't exist."""
    p = _path(attachments_dir, attachment_id)
    rec = _read_record(p)
    if rec is None:
        raise AttachmentError(f"attachment {attachment_id!r} not found at {p} — nothing to detach. Fail loud.")
    os.unlink(p)
    return {"detached": attachment_id, "channel": rec.get("channel"),
            "attachment_type": rec.get("attachment_type"), "target": rec.get("target")}


def get_attachment(attachment_id: str, *, attachments_dir: str | None = None) -> dict:
    rec = _read_record(_path(attachments_dir, attachment_id))
    if rec is None:
        raise AttachmentError(f"attachment {attachment_id!r} not found. Fail loud.")
    return rec


def list_attachments(*, channel: str | None = None, attachment_type: str | None = None,
                     attachments_dir: str | None = None) -> list[dict]:
    """All binding rows (file-discovered), optionally filtered by channel and/or type. Sorted by `added`."""
    d = _dir(attachments_dir)
    out = []
    if os.path.isdir(d):
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".md") or fn.startswith("_"):
                continue
            rec = _read_record(os.path.join(d, fn))
            if rec is None:
                continue
            if channel is not None and rec.get("channel") != channel:
                continue
            if attachment_type is not None and rec.get("attachment_type") != attachment_type:
                continue
            out.append(rec)
    return sorted(out, key=lambda r: r.get("added") or "")


def manifest(channel: str, *, attachments_dir: str | None = None) -> dict:
    """The §3 attachments MANIFEST for a channel — a PROJECTION of the binding rows grouped by type
    (a VIEW, not stored). {<attachment_type>: [target, …]} for each type bound to the channel; e.g.
    {sessions:[session://…], docs:[path…], recall:[scope], board_items:[board://…]}. This is exactly
    'manifest = projection of the rows' — the Heart's projection-of-the-registry."""
    rows = list_attachments(channel=channel, attachments_dir=attachments_dir)
    grouped: dict[str, list] = {}
    for r in rows:
        grouped.setdefault(r.get("attachment_type"), []).append(r.get("target"))
    return {"channel": channel, "attachments": grouped, "count": len(rows)}
