"""runtime/cc_images.py — IMAGES as first-class, HIERARCHICALLY-ADDRESSED fabric artifacts.

An image is its OWN typed record addressed image://<channel>/<path> — STRUCTURED + DEEP, never a flat
global id (Tim 2026-06-22: "the address space needs more structure and depth than just a dump at a global
root level"). The CHANNEL is the hierarchical root (images live IN channels); <path> is a nestable
collection/sub/name path, so the address is NAVIGABLE AT EACH DEPTH (image://<channel> = the channel's whole
image tree · image://<channel>/<collection> = that group · …/<name> = one image). The binary bytes live in
the content-addressed BLOB store (blob://b2:<hash>); the record points at them. (Mirrors decision://<frame>/<id>
+ code://<project>/<rel_path> — a structured address, parsed by contracts.address.parse_image_address.)

What this gives — all by REUSE, no parallel machinery:
  • STORE/SAVE / GENERATE-INTO → save_image(store, bytes, channel=…, path=…) → put_blob + the record.
  • READ        → get_image(addr) · image_bytes(store, addr) · the /api/image/<channel>/<path> route serves them.
  • NAVIGATE    → list_images(prefix=image://<channel>[/<collection>]) — browse the tree at any depth.
  • ATTACH      → cc_attachments `images` type targets image://<channel>/<path> (the channel's image tree).
  • COMMENT     → a board item linked `commented_on` → the image address (cc_board polymorphic edges).
  • LINK/REF    → board `references` edges between image addresses (output ↔ source compare links).

Storage: the hierarchical ADDRESS is the identity; the on-disk file is keyed by _safe(address) (flat filename,
hierarchical address — storage ≠ address). image:// resolves through the ONE resolve_address seam, fail-loud.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import yaml

from lifters.frontmatter import _extract as _fm_extract
from store.fs_store import _atomic_write_fsync, FsStore
from contracts.address import parse_image_address, image_address

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(REPO, "channel-memory", "images")

FRONTMATTER_KEYS = ("id", "address", "channel", "path", "blob", "mime", "name", "w", "h",
                    "source", "author_session", "created", "links")

_MIME_EXT = {
    "image/png": "png", "image/jpeg": "jpg", "image/webp": "webp",
    "image/gif": "gif", "image/svg+xml": "svg", "image/avif": "avif",
}


class ImageError(RuntimeError):
    """An image op could not run — raised TEACHING-loud (never a silent no-op)."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _file_for(addr: str) -> str:
    return os.path.join(IMAGES_DIR, FsStore._safe(addr) + ".md")


def _render(record: dict) -> str:
    fm = {k: record[k] for k in FRONTMATTER_KEYS if k in record}
    return "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n" + (record.get("body", "") or "") + "\n"


def _split_frontmatter(text: str) -> tuple[dict, str]:
    meta = _fm_extract(text) or {}
    body = ""
    s = text.lstrip("\n")
    if s.startswith("---"):
        rest = s[3:]
        idx = rest.find("\n---")
        if idx != -1:
            after = rest[idx + 4:]
            nl = after.find("\n")
            body = after[nl + 1:] if nl != -1 else ""
    return meta, body.strip("\n")


def _norm(addr_or_parts: str) -> str:
    """Normalise an input to a full image:// address. Accepts a full address, or 'channel/path'."""
    s = (addr_or_parts or "").strip("/")
    if s.startswith("image://"):
        return "image://" + s[len("image://"):].strip("/")
    return "image://" + s


def _sniff_mime(data: bytes, declared: str = "") -> str:
    sniffed = ""
    if data[:8].startswith(b"\x89PNG\r\n\x1a\n"):
        sniffed = "image/png"
    elif data[:3] == b"\xff\xd8\xff":
        sniffed = "image/jpeg"
    elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        sniffed = "image/webp"
    elif data[:6] in (b"GIF87a", b"GIF89a"):
        sniffed = "image/gif"
    elif b"<svg" in data[:512].lower() or data[:5] == b"<?xml":
        sniffed = "image/svg+xml"
    if declared:
        if sniffed and declared != sniffed:
            raise ImageError(
                f"declared mime {declared!r} does not match the actual bytes ({sniffed!r}) — refusing a "
                f"mislabeled image.")
        if declared not in _MIME_EXT:
            raise ImageError(f"unsupported mime {declared!r} — valid: {sorted(_MIME_EXT)}.")
        return declared
    if not sniffed:
        raise ImageError("could not recognise the image type from its bytes (not PNG/JPEG/WebP/GIF/SVG).")
    return sniffed


# ── the ops ─────────────────────────────────────────────────────────────────────────────────────────────
def save_image(store, data: bytes, *, channel: str, path: str, mime: str = "", name: str = "",
               source: str = "claude_code", alt: str = "", w: int = 0, h: int = 0,
               author_session: str, links=None) -> dict:
    """STORE an image at the HIERARCHICAL address image://<channel>/<path> (path = the in-channel tree
    location, e.g. 'deck1-2026/p-05' or 'generated/my-output'). Bytes → the content-addressed blob store
    (write-once, dedup). Idempotent: re-saving the same address UPDATES the record (re-ingest is safe).
    Fail-loud on a non-image / a missing channel|path|author_session (no flat/rootless image)."""
    if not isinstance(data, (bytes, bytearray)):
        raise ImageError(f"save_image expects image bytes, got {type(data).__name__}.")
    if not author_session:
        raise ImageError("save_image needs `author_session` (provenance).")
    addr = image_address(channel, path)                      # FAIL-LOUD if channel/path missing (no flat dump)
    parsed = parse_image_address(addr)
    data = bytes(data)
    mime = _sniff_mime(data, mime)
    blob = store.put_blob(data)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    record = {
        "id": parsed["path"], "address": addr,
        "channel": parsed["channel"], "path": parsed["path"],
        "blob": blob, "mime": mime, "name": name or parsed["name"],
        "w": int(w), "h": int(h), "source": source,
        "author_session": author_session, "created": _now(),
        "links": list(links or []), "body": alt,
    }
    _atomic_write_fsync(Path(_file_for(addr)), _render(record))
    return record


def get_image(addr_or_parts: str) -> dict:
    """READ one image record by its address (image://<channel>/<path>) or 'channel/path'. Fail-loud if
    missing/unparseable/not-a-leaf."""
    addr = _norm(addr_or_parts)
    parsed = parse_image_address(addr)
    if not parsed["is_leaf"]:
        raise ImageError(f"{addr!r} is a channel/group PREFIX, not one image — use list_images(prefix=…) to "
                         f"browse it. get_image needs a leaf image://<channel>/<path>.")
    p = _file_for(addr)
    if not os.path.exists(p):
        raise ImageError(f"no image at {addr!r} ({p}) — get on a missing image fails loud (never a silent empty).")
    with open(p, encoding="utf-8") as f:
        meta, body = _split_frontmatter(f.read())
    if not meta.get("address"):
        raise ImageError(f"image {addr!r} at {p} has no parseable frontmatter — malformed record, fail loud.")
    rec = dict(meta)
    rec["body"] = body
    rec.setdefault("links", [])
    return rec


def image_bytes(store, addr_or_parts: str) -> tuple[bytes, str]:
    """The image BYTES + mime (resolve record → blob → bytes). For the serve route."""
    rec = get_image(addr_or_parts)
    return store.get_blob(rec["blob"]), rec.get("mime", "application/octet-stream")


def list_images(prefix: str | None = None) -> list[dict]:
    """NAVIGATE the image tree at ANY depth. prefix = a channel (image://<channel>) or a group
    (image://<channel>/<collection>) or 'channel[/collection]' — returns every image whose address is
    UNDER it, newest-first. No prefix = all. Empty is HONEST (never fabricated)."""
    if not os.path.isdir(IMAGES_DIR):
        return []
    want = None
    if prefix:
        want = _norm(prefix).rstrip("/")
    out = []
    for fn in os.listdir(IMAGES_DIR):
        if not fn.endswith(".md"):
            continue
        try:
            with open(os.path.join(IMAGES_DIR, fn), encoding="utf-8") as f:
                meta, body = _split_frontmatter(f.read())
        except OSError:
            continue
        addr = meta.get("address")
        if not addr:
            continue
        if want and not (addr == want or addr.startswith(want + "/")):
            continue
        meta["body"] = body
        meta.setdefault("links", [])
        out.append(meta)
    out.sort(key=lambda r: r.get("created", ""), reverse=True)
    return out


def list_groups(channel: str) -> dict:
    """The channel's image tree as GROUPS (the immediate sub-paths under image://<channel>) → counts.
    Renders the hierarchy as a navigable index (the depth Tim asked for, surfaced)."""
    from collections import Counter
    ch = _norm(channel).rstrip("/")
    groups: Counter = Counter()
    leaves = 0
    for rec in list_images(ch):
        segs = rec.get("path", "").split("/")
        if len(segs) >= 2:
            groups[segs[0]] += 1
        else:
            leaves += 1
    return {"channel": ch, "groups": dict(groups), "ungrouped": leaves, "total": sum(groups.values()) + leaves}
