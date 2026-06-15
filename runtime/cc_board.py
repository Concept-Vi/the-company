"""runtime/cc_board.py — the Company NOTICEBOARD / board runtime (Tim's "inward-facing half", 2026-06-15).

The outward half (channels, clones, recall, the capability/registry engine) builds the product. THIS is
where the Company talks ABOUT ITSELF: agents (and Tim) file typed items — request · issue · tip · guide ·
idea — about the Company / MCP / CLI / CI / app; a channel (the lead first, a routine later) picks them
up and moves them along their lifecycle. The board is realized THROUGH the channel system (an item lives
in a channel, has a thread), but its records are a DISTINCT resource, so its tool is `cc_board` (its own
op-multiplexed surface) — exactly as `cc_clone` is its own tool beside `cc_channel`.

## The locked design (synthesized with the fabric, 2026-06-15 — see channel-memory/vision/...noticeboard...)
  • type / state / source / edge-kind are REGISTRY REFERENCES, validated fail-loud — never inline enums.
    (item_types/, source_types/, board_edges/ — file-discovered, add-a-row-not-code.)
  • the per-type LIFECYCLE lives ON the item-type row; `transition` moves along the registry-declared
    legal states — there is NO hardcoded pickup/resolve op.
  • storage is id-keyed FLAT: channel-memory/noticeboard/<id>.md (md+frontmatter, git-tracked). `type`
    is frontmatter, never the path — so a type can CHANGE (idea->request promotion) without re-homing.
  • the canonical address is `board://<id>` — FLAT, because identity must hold nothing mutable.
  • `links` are TYPED EDGES [{kind, target}] — `kind` validated against the relation/edge registry; this
    is the Company's cross-registry edge layer (a board row pointing at a session:// / channel / source /
    board:// row), exercised here for the first time. A new edge-kind is a board_edges/<kind>.py — a
    ROW-ADD, no code.

## Reuse (no parallel machinery — scouted before building, per the fabric norm)
  • frontmatter read  -> lifters.frontmatter._extract (the canonical PyYAML-backed parser).
  • durable write     -> store.fs_store._atomic_write_fsync (tmp+fsync+os.replace+dir-fsync).
  • registries        -> ItemTypeRegistry / SourceTypeRegistry (this build) + RelationTypeRegistry (reused
                         verbatim for the board edge vocabulary — the ONE registry mechanism).

## NOT recall-able yet (honest ledger — confirmed by recollection ch-83e2cque, 2026-06-15)
Items are git-tracked + addressed (board://<id>) but NOT in any recall index today. The recall<->board
wire (a "noticeboard" capture-source sweeping these .md into the embedding axis) is recollection's
follow-up unit, landing ON the board:// addresses + `source` field this module emits.

LAWS honoured: no-hardcoding · reuse-don't-parallel · fail loud (every bad registry ref / illegal
transition / missing item RAISES BoardError — never a silent no-op) · registry-is-truth.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml

from lifters.frontmatter import _extract as _fm_extract
from store.fs_store import _atomic_write_fsync
from runtime.item_types import ItemTypeRegistry
from runtime.source_types import SourceTypeRegistry
from runtime.relation_types import RelationTypeRegistry

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEM_TYPES_DIR = os.path.join(REPO, "item_types")
SOURCE_TYPES_DIR = os.path.join(REPO, "source_types")
BOARD_EDGES_DIR = os.path.join(REPO, "board_edges")
NOTICEBOARD_DIR = os.path.join(REPO, "channel-memory", "noticeboard")

DEFAULT_SOURCE = "claude_code"

# The frontmatter keys (the structured row); `body` is the markdown AFTER the frontmatter, not a key.
FRONTMATTER_KEYS = ("id", "address", "type", "source", "state", "title", "author_session",
                    "channel", "thread", "links", "created", "updated", "history")


class BoardError(RuntimeError):
    """A board op could not run — raised TEACHING-loud (never a silent no-op). Mirrors cc_channels.ChannelError."""


# ── registries (lazy module singletons; reset_registries re-reads the dirs — proves add-a-row-is-live) ──
_ITEMS: ItemTypeRegistry | None = None
_SOURCES: SourceTypeRegistry | None = None
_EDGES: RelationTypeRegistry | None = None


def _items_reg() -> ItemTypeRegistry:
    global _ITEMS
    if _ITEMS is None:
        _ITEMS = ItemTypeRegistry().discover([ITEM_TYPES_DIR])
    return _ITEMS


def _sources_reg() -> SourceTypeRegistry:
    global _SOURCES
    if _SOURCES is None:
        _SOURCES = SourceTypeRegistry().discover([SOURCE_TYPES_DIR])
    return _SOURCES


def _edges_reg() -> RelationTypeRegistry:
    global _EDGES
    if _EDGES is None:
        _EDGES = RelationTypeRegistry().discover([BOARD_EDGES_DIR])
    return _EDGES


def reset_registries() -> None:
    """Drop the cached registries so the NEXT access re-reads the directories. Proves the registries are
    real (a freshly-dropped board_edges/<kind>.py becomes live with no code change)."""
    global _ITEMS, _SOURCES, _EDGES
    _ITEMS = _SOURCES = _EDGES = None
    _items_reg()
    _sources_reg()
    _edges_reg()


def item_types() -> list[str]:
    """The registered story-types (sorted ids)."""
    return sorted(_items_reg())


def source_types() -> list[str]:
    """The registered source-types (sorted ids)."""
    return sorted(_sources_reg())


def edge_kinds() -> list[str]:
    """The registered board edge-kinds (sorted ids) — the cross-registry link vocabulary."""
    return sorted(_edges_reg())


def initial_state(item_type: str) -> str:
    """The registry-declared initial state for an item type. Fail-loud on an unknown type."""
    reg = _items_reg()
    if item_type not in reg:
        raise BoardError(
            f"unknown item type {item_type!r} — valid types: {item_types()}. "
            f"(type is a registry ref; add an item_types/<id>.py to extend.)")
    return reg[item_type].initial


def legal_transitions(item_type: str, state: str) -> list[str]:
    """The states an item of `item_type` may legally move to FROM `state` (registry-declared lifecycle)."""
    reg = _items_reg()
    if item_type not in reg:
        raise BoardError(
            f"unknown item type {item_type!r} — valid types: {item_types()}. (type is a registry ref.)")
    return reg[item_type].legal_from(state)


# ── helpers ──────────────────────────────────────────────────────────────────────────────────────────
def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return "item-" + uuid.uuid4().hex[:8]


def _dir(board_dir: str | None) -> str:
    return board_dir or NOTICEBOARD_DIR


def _path(board_dir: str | None, iid: str) -> str:
    return os.path.join(_dir(board_dir), f"{iid}.md")


def _validate_links(links) -> list[dict]:
    """Each link is a TYPED EDGE {kind, target}; `kind` validated fail-loud against the edge registry."""
    reg = _edges_reg()
    out = []
    for ln in (links or []):
        if not isinstance(ln, dict) or "kind" not in ln or "target" not in ln:
            raise BoardError(f"each link must be a dict with `kind` and `target`. Got {ln!r} — fail loud.")
        kind = ln["kind"]
        if kind not in reg:
            raise BoardError(
                f"unknown edge kind {kind!r} — valid edge kinds: {edge_kinds()}. "
                f"(a link's kind is a registry ref; add a board_edges/<kind>.py to extend.)")
        out.append({"kind": kind, "target": ln["target"]})
    return out


def _render(record: dict) -> str:
    """The on-disk form: a `---`-fenced YAML frontmatter (the structured row) + the markdown body after."""
    fm = {k: record[k] for k in FRONTMATTER_KEYS if k in record}
    return "---\n" + yaml.dump(fm, sort_keys=False, allow_unicode=True) + "---\n\n" + (record.get("body") or "") + "\n"


def _split_frontmatter(text: str) -> tuple[dict, str]:
    """Parse the record: frontmatter via the canonical lifters parser; body = everything after the fence."""
    meta = _fm_extract(text) or {}
    body = ""
    s = text.lstrip("\n")
    if s.startswith("---"):
        rest = s[3:]
        idx = rest.find("\n---")
        if idx != -1:
            after = rest[idx + 4:]            # skip the closing "\n---"
            nl = after.find("\n")
            body = after[nl + 1:] if nl != -1 else ""
    return meta, body.strip("\n")


def _write(board_dir: str | None, record: dict) -> None:
    d = _dir(board_dir)
    os.makedirs(d, exist_ok=True)
    _atomic_write_fsync(Path(_path(board_dir, record["id"])), _render(record))


# ── the ops (cc_board file / list / get / transition ride on these) ────────────────────────────────────
def file_item(item_type: str, title: str, body: str, author_session: str, *,
              source: str = DEFAULT_SOURCE, channel: str = "", thread: str = "",
              links=None, board_dir: str | None = None) -> dict:
    """FILE a typed item onto the board. Validates type/source/edge-kinds against their registries
    (fail-loud), starts the item in its type's registry-declared initial state, stamps provenance +
    history, and persists it id-keyed FLAT at <board>/<id>.md. Returns the item record."""
    reg = _items_reg()
    if item_type not in reg:
        raise BoardError(
            f"unknown item type {item_type!r} — valid types: {item_types()}. "
            f"(type is a registry ref, not an enum; add an item_types/<id>.py to extend.)")
    if source not in _sources_reg():
        raise BoardError(
            f"unknown source {source!r} — valid sources: {source_types()}. "
            f"(source is a registry ref; add a source_types/<id>.py to extend.)")
    edges = _validate_links(links)
    d = _dir(board_dir)
    os.makedirs(d, exist_ok=True)
    iid = _new_id()
    while os.path.exists(_path(board_dir, iid)):       # collision-guard (uuid hex8)
        iid = _new_id()
    ts = _now()
    state = reg[item_type].initial
    record = {
        "id": iid,
        "address": f"board://{iid}",
        "type": item_type,
        "source": source,
        "state": state,
        "title": title,
        "author_session": author_session,
        "channel": channel,
        "thread": thread,
        "links": edges,
        "created": ts,
        "updated": ts,
        "history": [{"from": None, "to": state, "by": author_session, "ts": ts, "note": "filed"}],
        "body": body,
    }
    _write(board_dir, record)
    return record


def get_item(item_id: str, *, board_dir: str | None = None) -> dict:
    """READ one item by id. Fail-loud if it does not exist or is unparseable."""
    p = _path(board_dir, item_id)
    if not os.path.exists(p):
        raise BoardError(f"no board item {item_id!r} at {p} — get/transition on a missing item fails loud.")
    with open(p, encoding="utf-8") as f:
        text = f.read()
    meta, body = _split_frontmatter(text)
    if not meta.get("id"):
        raise BoardError(f"board item {item_id!r} at {p} has no parseable frontmatter — malformed record, fail loud.")
    rec = dict(meta)
    rec["body"] = body
    rec.setdefault("links", [])
    rec.setdefault("history", [])
    return rec


def list_items(*, type: str | None = None, state: str | None = None, source: str | None = None,
               author_session: str | None = None, board_dir: str | None = None) -> list[dict]:
    """LIST items on the board (the pick-up read), optionally filtered. 'Browse by type' is a PROJECTION
    over the flat store (a filter), never a directory layout. (`type` shadows the builtin only in this
    read-filter scope — the on-disk field this matches is the item's registry-ref `type`.)"""
    d = _dir(board_dir)
    if not os.path.isdir(d):
        return []
    out = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".md") or fn.startswith("_"):
            continue
        try:
            rec = get_item(fn[:-3], board_dir=board_dir)
        except BoardError:
            continue
        if type is not None and rec.get("type") != type:
            continue
        if state is not None and rec.get("state") != state:
            continue
        if source is not None and rec.get("source") != source:
            continue
        if author_session is not None and rec.get("author_session") != author_session:
            continue
        out.append(rec)
    return out


def traverse(item_id: str, kind: str | None = None, *, store=None, board_dir: str | None = None) -> list[dict]:
    """Heart H1.1 — FOLLOW a board item's typed edges ACROSS registries, through the ONE resolver.

    Reads the item's typed links (optionally filtered to `kind`, validated fail-loud against the edge
    registry), resolves each edge's `target` THROUGH cognition.resolve_address — so a board:// target
    lands in the board registry, session:// in the agent-session registry, skill:// in the skill
    registry: one addressed graph, one resolver. Returns one hop per edge: {kind, target, resolved}.

    COMPOSES the resolver + the edge registry — NOT a parallel query engine (this is the seed the H1.2
    query traversal + find_relations generalize). `store` is passed through to resolve_address (needed
    for session://run:// targets; board:///skill:// targets ignore it). Fail-loud both ends: a missing
    source item RAISES (get_item); an unregistered `kind` RAISES naming the valid kinds; an unresolvable
    target propagates resolve_address's loud raise (never a silent empty)."""
    rec = get_item(item_id, board_dir=board_dir)          # raises if the source item is missing
    if kind is not None and kind not in _edges_reg():
        raise BoardError(
            f"unknown edge kind {kind!r} — valid edge kinds: {edge_kinds()}. "
            f"(traverse filters by a registry edge-kind; add a board_edges/<kind>.py to extend.)")
    from runtime.cognition import resolve_address          # lazy: avoid module-load coupling / any cycle
    hops = []
    for ln in (rec.get("links") or []):
        if kind is not None and ln.get("kind") != kind:
            continue
        target = ln.get("target")
        hops.append({"kind": ln.get("kind"), "target": target,
                     "resolved": resolve_address(store, target)})
    return hops


def transition(item_id: str, to_state: str, *, by: str = "", note: str = "",
               board_dir: str | None = None) -> dict:
    """MOVE an item along its type's registry-declared lifecycle. Fail-loud if the move is not a declared
    legal transition (the lifecycle on the item-type row is the only truth). Appends to history + persists."""
    rec = get_item(item_id, board_dir=board_dir)          # raises if missing
    itype = rec.get("type")
    reg = _items_reg()
    if itype not in reg:
        raise BoardError(f"board item {item_id!r} has unknown type {itype!r} — cannot transition. Fail loud.")
    cur = rec.get("state")
    legal = reg[itype].legal_from(cur)
    if to_state not in legal:
        raise BoardError(
            f"illegal transition {cur!r}->{to_state!r} for item type {itype!r}. Legal from {cur!r}: {legal}. "
            f"(the registry-declared lifecycle is the only truth — no hardcoded transition op.)")
    ts = _now()
    rec["state"] = to_state
    rec["updated"] = ts
    rec.setdefault("history", []).append({"from": cur, "to": to_state, "by": by, "ts": ts, "note": note})
    _write(board_dir, rec)
    return rec
