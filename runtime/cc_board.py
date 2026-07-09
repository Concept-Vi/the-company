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

import json
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
# The DERIVED authored_by index (④ L6 BOARD, C6.1): a regenerable reverse-lookup map author-address ->
# [item ids], rebuilt from a full scan and read O(1) — so "which items did this author file?" costs one
# dict access, never an O(n) reverse_traverse scan of every file. `_`-prefixed so list_items skips it.
AUTHORED_BY_INDEX = "_authored_by_index.json"

DEFAULT_SOURCE = "claude_code"

# The frontmatter keys (the structured row); `body` is the markdown AFTER the frontmatter, not a key.
# `scope` + `author` are ADDRESSES (④ L6 BOARD): scope = project://<key> | channel://<name> | global;
# author = operator://tim | session://<id> | agent://<name>. Both derived-with-a-default from the legacy
# channel/author_session fields (see _scope_of / _author_of) so the 690 pre-existing items carry them on
# read even before the durable backfill sweep.
FRONTMATTER_KEYS = ("id", "address", "type", "source", "state", "scope", "author", "title", "author_session",
                    "channel", "thread", "links", "order", "created", "updated", "history")
# `order` (optional) — an ordered list of child addresses for a CONTAINER item (e.g. a document's blocks in
# sequence). Membership is the part_of edge; SEQUENCE is this list. Written only when present (see _render).


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


# ── scope + author AS ADDRESSES (④ L6 BOARD, C6.1) ─────────────────────────────────────────────────────
# The BOARD study: "scope is an address · author is an address". author_type dissolves — you know it's an
# agent because the address RESOLVES to one. These derive a canonical address from the legacy fields, so a
# pre-address item (the 690) still yields a scope/author on read (get_item setdefault), and the migration
# stamps the SAME derivation durably. Never fabricate — an unrecognised author stays as a session:// of its
# raw handle (source provenance; L2's principal model formalises the operator/agent split).
_OPERATOR_HANDLES = {"tim", "operator", "operator://tim"}


def _scope_of(channel: str | None) -> str:
    """channel -> scope address. '' / None -> the explicit global root; a named channel -> channel://<name>.
    (A project:// scope is passed explicitly by a caller filing into a project; never guessed from a channel.)"""
    ch = (channel or "").strip()
    if not ch:
        return "global"
    if "://" in ch:                 # already an address (project://… / channel://…) — pass through
        return ch
    return f"channel://{ch}"


def _author_of(author_session: str | None) -> str:
    """author_session (a legacy untyped handle) -> author ADDRESS. tim/operator -> operator://tim; an
    already-addressed value passes through; a session handle (ch-…) -> session://<id>; any other named role
    -> agent://<slug>. This is the derivation the authored_by edge + index compose from."""
    a = (author_session or "").strip()
    if not a:
        return "agent://unknown"
    if "://" in a:                  # already an address
        return a
    if a.lower() in _OPERATOR_HANDLES:
        return "operator://tim"
    if a.startswith("ch-") or a.startswith("as-"):   # a Claude Code / agent-session handle (EPHEMERAL)
        # DURABLE-IDENTITY LAW (contracts/address.py:93 — a provenance address must hold the STABLE id,
        # not the churning handle): resolve the handle -> its session UUID and record THAT, so authorship
        # survives a handle churn. Fast + probe-free (read the reg + the fast recovery rungs); fall back
        # to the handle only when the uuid can't be recovered (still addressable, honestly).
        try:
            import os as _os
            from runtime import cc_channels as _cc, identity as _identity
            reg = _cc._read_reg(_os.path.join(_cc.CHAN_DIR, f"{a}.json"))
            if reg:
                u, _how = _identity.recover_uuid(reg)     # deep=False — fast rungs, no probe/scan
                if u:
                    return f"session://{u}"
        except Exception:
            pass
        return f"session://{a}"
    return f"agent://{a}"


# ── the board-event emitter (④ L6 BOARD, C6.5) ─────────────────────────────────────────────────────────
# item.filed / item.transitioned emit on the CHANNEL/event layer so a gated lane is WOKEN BY the board
# (the study's "the board stays the thing agents are WOKEN BY"). cc_board is standalone (no suite import —
# avoids a cycle); the emitter is INJECTED. The MCP tool wires it to suite.emit_run_record at the
# register(mcp, suite) boundary (mirrors decision_decided_signal's floor-clean record emit). Lenient like
# every telemetry emit: a failure is SURFACED on the return (emit_error), never breaks the file write.
_BOARD_EMITTER = None


def set_board_emitter(fn) -> None:
    """Install the process's board-event emitter — a callable emit(event: str, fields: dict). Called by the
    MCP face (suite.emit_run_record) and by tests (a capturing subscriber). None = no emit (pure file I/O)."""
    global _BOARD_EMITTER
    _BOARD_EMITTER = fn


def _emit_board_event(event: str, fields: dict, *, emit=None) -> str | None:
    """Emit a board event leniently. `emit` (per-call) overrides the module emitter. Returns an error string
    on failure (surfaced on the record, never raised) or None on success/no-emitter."""
    fn = emit if emit is not None else _BOARD_EMITTER
    if fn is None:
        return None
    try:
        fn(event, fields)
        return None
    except Exception as e:                       # VISIBILITY best-effort — never break the file write
        return f"{type(e).__name__}: {e}"


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
    """The on-disk form: a `---`-fenced YAML frontmatter (the structured row) + the markdown body after.

    Frontmatter is NOT a closed allowlist (F3): the canonical FRONTMATTER_KEYS render FIRST in their fixed
    order (so existing items serialise byte-identically), then ANY OTHER record key is persisted too —
    except `body`, which is the post-fence content. A new typed field (e.g. `active` for block-versions, or
    any future registry-driven field) is therefore never silently dropped on write. Previously an unlisted
    key was discarded here, which was real data loss for new fields."""
    fm = {k: record[k] for k in FRONTMATTER_KEYS if k in record}
    for k, v in record.items():                      # then carry any extra field (open, not allowlisted)
        if k not in fm and k != "body":
            fm[k] = v
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
              scope: str | None = None, author: str | None = None,
              links=None, board_dir: str | None = None, item_id: str | None = None,
              state: str | None = None, extra: dict | None = None,
              created: str | None = None, updated: str | None = None,
              history: list | None = None, emit=None) -> dict:
    """FILE a typed item onto the board. Validates type/source/edge-kinds against their registries
    (fail-loud), starts the item in its type's registry-declared initial state, stamps provenance +
    history, and persists it id-keyed FLAT at <board>/<id>.md. Returns the item record.

    `scope` + `author` are ADDRESSES (④ L6 BOARD): scope defaults to the channel-derived scope (global for
    ''), author defaults to the author_session-derived address. `item_id` forces a specific id (the pour
    keeps the cloud uuids). Emits `item.filed` on the channel layer (C6.5) via the injected emitter.

    Pour-only additive kwargs (④ L6 BOARD data landing, C6.3): `state` LANDS a non-initial state directly
    (validated ∈ the type's declared states — fail-loud, honoring the legacy open/resolved/closed; the
    landing status is written into the file, NOT run through transition()); `extra` merges the long-tail
    content keys as OPEN frontmatter (nothing dropped); `created`/`updated` preserve the source timestamps;
    `history` replaces the default filed-history with synthesized provenance entries."""
    for _an, _av in (("scope", scope), ("author", author)):   # ④ L6 adversary DENT-1: addresses, fail-loud
        if _av is not None and _av != "global" and "://" not in _av:   # "global" = the board root sentinel
            raise BoardError(
                f"{_an}={_av!r} is not an address — {_an} is an ADDRESS (scheme://…, e.g. "
                f"project://the-fusion, operator://tim). A bare string never lands. Fail loud, never guess.")
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
    if item_id:
        iid = item_id
        if os.path.exists(_path(board_dir, iid)):
            raise BoardError(f"board item {iid!r} already exists — file with an explicit item_id refuses to "
                             f"overwrite (idempotent pour checks existence first). Fail loud.")
    else:
        iid = _new_id()
        while os.path.exists(_path(board_dir, iid)):       # collision-guard (uuid hex8)
            iid = _new_id()
    ts = _now()
    if state is not None and state not in reg[item_type].states:
        raise BoardError(
            f"cannot land state {state!r} on item type {item_type!r} — declared states: "
            f"{reg[item_type].states}. (a landing status must be in the type's vocabulary; add it to "
            f"item_types/{item_type}.py to honour a legacy status. Fail loud, never a silent bad record.)")
    landed = state or reg[item_type].initial
    record = {
        "id": iid,
        "address": f"board://{iid}",
        "type": item_type,
        "source": source,
        "state": landed,
        "scope": scope or _scope_of(channel),
        "author": author or _author_of(author_session),
        "title": title,
        "author_session": author_session,
        "channel": channel,
        "thread": thread,
        "links": edges,
        "created": created or ts,
        "updated": updated or ts,
        "history": history if history is not None else
                   [{"from": None, "to": landed, "by": author_session, "ts": created or ts, "note": "filed"}],
        "body": body,
    }
    for k, v in (extra or {}).items():                    # the open long-tail keys (never shadow a core key)
        if k not in record and k != "body":
            record[k] = v
    _write(board_dir, record)
    err = _emit_board_event("item.filed", {"id": iid, "address": record["address"], "type": item_type,
                                           "state": landed, "scope": record["scope"],
                                           "author": record["author"], "title": title,
                                           "channel": channel}, emit=emit)
    if err:
        record = dict(record); record["emit_error"] = err     # surfaced on the return, not persisted
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
    # scope/author are ADDRESSES (④ L6 BOARD) — the 690 pre-address items get them derived on read from
    # their legacy channel/author_session so a read never fails and list(scope=…) works pre-backfill.
    rec.setdefault("scope", _scope_of(rec.get("channel")))
    rec.setdefault("author", _author_of(rec.get("author_session")))
    return rec


def list_items(*, type: str | None = None, state: str | None = None, source: str | None = None,
               author_session: str | None = None, scope: str | None = None, author: str | None = None,
               board_dir: str | None = None) -> list[dict]:
    """LIST items on the board (the pick-up read), optionally filtered. 'Browse by type' is a PROJECTION
    over the flat store (a filter), never a directory layout. (`type` shadows the builtin only in this
    read-filter scope — the on-disk field this matches is the item's registry-ref `type`.)

    `scope` filters to one board (④ L6 BOARD): list(scope='project://the-fusion') is the projection that
    makes 'one store, many boards' — a board is a scope-filtered VIEW over the one item store. `author`
    filters by author address."""
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
        if scope is not None and rec.get("scope") != scope:
            continue
        if author is not None and rec.get("author") != author:
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


def reverse_traverse(target_addr: str, kind: str | None = None, *, hydrate: bool = False,
                     store=None, board_dir: str | None = None) -> list[dict]:
    """Heart H1.2 — the INVERSE of traverse: every board item that LINKS TO `target_addr`.

    Where traverse() follows a source item's edges OUT, this finds the edges IN: scan the board, return
    each item carrying a link {kind, target == target_addr} (optionally filtered to `kind`). The match is
    on the OPAQUE target STRING — no resolution needed to MATCH (a projection over the rows, exactly like
    manifest()/list_items — addresses are compared as identities, not dereferenced). e.g.
    reverse_traverse("session://ch-8djrpmsl", "authored_by") → the items that session authored;
    reverse_traverse("board://item-e523b30d", "promoted_from") → the items promoted from it.

    Returns one entry per matching edge: {source, kind, target, item} where `source` = the linking item's
    board:// address and `item` = its full record. `hydrate=True` ALSO resolves each `source` THROUGH
    cognition.resolve_address (string-match → resolved record) — proving the matched ids flow back through
    the ONE resolver (the round-trip H1.1 established). Fail-loud on an unregistered `kind` (mirrors
    traverse). COMPOSES list_items + the edge registry (+ resolve_address when hydrating) — NOT a parallel
    query engine; this is the find_relations 'edges-into' generalization."""
    if kind is not None and kind not in _edges_reg():
        raise BoardError(
            f"unknown edge kind {kind!r} — valid edge kinds: {edge_kinds()}. "
            f"(reverse_traverse filters by a registry edge-kind; add a board_edges/<kind>.py to extend.)")
    matches = []
    resolve = None
    if hydrate:
        from runtime.cognition import resolve_address          # lazy: avoid module-load coupling / any cycle
        resolve = resolve_address
    for rec in list_items(board_dir=board_dir):
        for ln in (rec.get("links") or []):
            if ln.get("target") != target_addr:
                continue
            if kind is not None and ln.get("kind") != kind:
                continue
            entry = {"source": rec.get("address"), "kind": ln.get("kind"), "target": target_addr,
                     "item": rec}
            if resolve is not None:
                entry["resolved"] = resolve(store, rec.get("address"))
            matches.append(entry)
    return matches


def _edges_out(item_id: str, kind: str | None, *, hydrate: bool, store, board_dir: str | None) -> list[dict]:
    """STRUCTURAL read of a board item's outgoing edges (its links, optionally filtered to `kind`) —
    the structural sibling of traverse(). Unlike traverse (H1.1) which ALWAYS resolves every target
    through the resolver (needs a live store), this matches/returns the edges WITHOUT resolving, and
    resolves only when `hydrate=True` — so the query surface works on the pure structural graph (no live
    store required). Same edge-registry fail-loud. (traverse stays the eager resolve-through forward.)"""
    rec = get_item(item_id, board_dir=board_dir)              # raises if the source item is missing
    resolve = None
    if hydrate:
        from runtime.cognition import resolve_address
        resolve = resolve_address
    edges = []
    for ln in (rec.get("links") or []):
        if kind is not None and ln.get("kind") != kind:
            continue
        e = {"kind": ln.get("kind"), "target": ln.get("target")}
        if resolve is not None:
            e["resolved"] = resolve(store, ln.get("target"))
        edges.append(e)
    return edges


def relations(addr: str, *, direction: str = "both", kind: str | None = None, hydrate: bool = False,
              store=None, board_dir: str | None = None) -> dict:
    """Heart H1.2 — ONE query surface over the typed-edge graph: edges-OUT of a source + edges-IN to a
    target, by address. The unification the seed find_relations generalizes into (the lattice's relation
    axis): give it any address + a direction. STRUCTURAL by default (matches on the opaque address — no
    live store needed); `hydrate=True` resolves results through the ONE resolver (the H1.1 round-trip).

      direction="out"  — edges FROM `addr` (only a board://<id> source CARRIES links; structural read).
      direction="in"   — edges INTO `addr` (any address; reverse_traverse).
      direction="both" — both (default).

    `out` on a non-board addr is empty + STATED (sessions/skills don't author board edges) — never a
    silent guess. Fail-loud on an unregistered `kind`. COMPOSES reverse_traverse + the structural edge
    read — NOT a new engine, and NOT coupled to a live store (that's traverse's job when you want it)."""
    if direction not in ("in", "out", "both"):
        raise BoardError(f"unknown direction {direction!r} — one of 'in' | 'out' | 'both'. Fail loud.")
    if kind is not None and kind not in _edges_reg():
        raise BoardError(
            f"unknown edge kind {kind!r} — valid edge kinds: {edge_kinds()}. "
            f"(relations filters by a registry edge-kind; add a board_edges/<kind>.py to extend.)")
    out: dict = {"addr": addr, "direction": direction}
    if direction in ("in", "both"):
        out["edges_in"] = reverse_traverse(addr, kind, hydrate=hydrate, store=store, board_dir=board_dir)
    if direction in ("out", "both"):
        if isinstance(addr, str) and addr.startswith("board://"):
            out["edges_out"] = _edges_out(addr[len("board://"):], kind, hydrate=hydrate,
                                          store=store, board_dir=board_dir)
        else:
            out["edges_out"] = []          # only board items carry outgoing board edges (stated, not silent)
            out["edges_out_note"] = f"{addr!r} is not a board:// address — only board items carry outgoing edges"
    return out


def transition(item_id: str, to_state: str, *, by: str = "", note: str = "",
               board_dir: str | None = None, emit=None) -> dict:
    """MOVE an item along its type's registry-declared lifecycle. Fail-loud if the move is not a declared
    legal transition (the lifecycle on the item-type row is the only truth). Appends to history + persists.
    Emits `item.transitioned` on the channel layer (C6.5) via the injected emitter."""
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
    err = _emit_board_event("item.transitioned", {"id": item_id, "address": rec.get("address"),
                                                  "type": itype, "from": cur, "to": to_state, "by": by,
                                                  "scope": rec.get("scope")}, emit=emit)
    if err:
        rec = dict(rec); rec["emit_error"] = err          # surfaced on the return, not persisted
    return rec


# ── edit-in-place (no-versioning: update the SAME record, append history — never a new file) ──────────────
def edit_item(item_id: str, *, title: str | None = None, body: str | None = None, order: list | None = None,
              add_links: list | None = None, by: str = "", note: str = "", board_dir: str | None = None) -> dict:
    """EDIT an item IN PLACE (the no-versioning law — same address, same file, updated). Any of `title` /
    `body` / `order` (the container's ordered child-address list) may be updated; `add_links` APPENDS typed
    edges (validated fail-loud). Stamps `updated` + appends an `edited` history entry. Returns the record.
    (state moves go through transition(); this is for content/structure, not lifecycle.)"""
    rec = get_item(item_id, board_dir=board_dir)              # raises if missing
    changed = []
    if title is not None:
        rec["title"] = title; changed.append("title")
    if body is not None:
        rec["body"] = body; changed.append("body")
    if order is not None:
        rec["order"] = list(order); changed.append("order")
    if add_links:
        rec["links"] = (rec.get("links") or []) + _validate_links(add_links); changed.append("links")
    if not changed:
        raise BoardError("edit_item: nothing to change — pass at least one of title/body/order/add_links. Fail loud.")
    ts = _now()
    rec["updated"] = ts
    rec.setdefault("history", []).append({"from": "edit", "to": ",".join(changed), "by": by, "ts": ts,
                                          "note": note or "edited in place"})
    _write(board_dir, rec)
    return rec


# ── general ANNOTATION on ANY address (comment / reply / thread) — the runtime the cc_images tool wrapped,
#    now first-class on the board so it works on a block://, a code:// card, a decision://, anything ─────────
def comment(target_addr: str, body: str, author_session: str, *, title: str = "Comment",
            channel: str = "", item_type: str = "note", board_dir: str | None = None,
            author: str | None = None) -> dict:
    """COMMENT on any address: files a board item linked `commented_on` → `target_addr`. The comment is
    itself addressed (board://<id>), so it can be replied to (threading) and commented on in turn."""
    if not target_addr or not body or not author_session:
        raise BoardError("comment needs `target_addr`, `body`, and `author_session`. Fail loud.")
    return file_item(item_type, title, body, author_session, channel=channel,
                     links=[{"kind": "commented_on", "target": target_addr}], board_dir=board_dir, author=author)


def reply(comment_addr: str, body: str, author_session: str, *, title: str = "Reply", channel: str = "",
          item_type: str = "note", board_dir: str | None = None) -> dict:
    """REPLY to a comment/note (threading): files a board item linked `reply_to` → the comment's address."""
    if not comment_addr or not body or not author_session:
        raise BoardError("reply needs `comment_addr`, `body`, and `author_session`. Fail loud.")
    return file_item(item_type, title, body, author_session, channel=channel,
                     links=[{"kind": "reply_to", "target": comment_addr}], board_dir=board_dir)


def thread(addr: str, *, board_dir: str | None = None) -> list[dict]:
    """The THREADED annotation tree ON an address: top-level comments (commented_on → addr), each with its
    nested replies (reply_to → the comment, recursive). The 'replied-to comments'. Reuses reverse_traverse."""
    def nest(item_addr: str) -> list[dict]:
        return [{"comment": e["item"], "replies": nest(e["item"]["address"])}
                for e in reverse_traverse(item_addr, "reply_to", board_dir=board_dir)]
    return [{"comment": e["item"], "replies": nest(e["item"]["address"])}
            for e in reverse_traverse(addr, "commented_on", board_dir=board_dir)]


# ── assemble a DOCUMENT for reading/review: ordered blocks, each with its comment thread ──────────────────
def assemble_document(doc_id: str, *, board_dir: str | None = None) -> dict:
    """READ a document as an ORDERED, ANNOTATED whole: the document record + its blocks IN SEQUENCE, each
    block carrying its body + its threaded comments. Sequence comes from the document's `order` field;
    if absent, falls back to the blocks that link `part_of` it, sorted by title (the title-prefix order).
    Composes get_item + reverse_traverse(part_of) + thread() — not a parallel engine. Fail-loud on a
    missing document; a block address in `order` that no longer resolves is reported, not silently dropped."""
    doc = get_item(doc_id, board_dir=board_dir)              # raises if missing
    order = list(doc.get("order") or [])
    if not order:                                            # fallback: membership edges, title-sorted
        contained = reverse_traverse(doc["address"], "part_of", board_dir=board_dir)
        order = [e["item"]["address"] for e in
                 sorted((e for e in contained), key=lambda e: e["item"].get("title", ""))]
    blocks, missing = [], []
    for addr in order:
        bid = addr.split("://", 1)[-1] if "://" in addr else addr
        try:
            brec = get_item(bid, board_dir=board_dir)
        except BoardError:
            missing.append(addr); continue
        blocks.append({"address": addr, "title": brec.get("title"), "state": brec.get("state"),
                       "body": brec.get("body"), "thread": thread(addr, board_dir=board_dir)})
    return {"document": doc, "blocks": blocks, "block_count": len(blocks),
            "missing": missing, "doc_thread": thread(doc["address"], board_dir=board_dir)}


# ── the DERIVED authored_by index (④ L6 BOARD, C6.1) — the equal-and-opposite, composed + indexed ─────────
# The BOARD study: "the authored_by edge becomes DERIVED from the author field (equal-and-opposite,
# indexed) — fixing both the 8-of-690 inconsistency and the O(n) reverse." The index is a regenerable
# projection (never hand-maintained): a full scan builds {author-address -> [item ids]}, and a reverse
# lookup ("which items did operator://tim file?") is then ONE dict access — not a reverse_traverse scan of
# every file. Rebuilt by the migration + on demand; the map is DERIVED, the files stay truth.
def rebuild_authored_by_index(board_dir: str | None = None) -> dict:
    """DERIVE the authored_by index from the item store (a full scan → {author: [ids]}), persist it to
    <board>/_authored_by_index.json, and return it. Regenerable — deleting the file and re-running
    reproduces it identically. This is the ONE place the reverse is composed; nothing hand-maintains it."""
    idx: dict[str, list[str]] = {}
    for rec in list_items(board_dir=board_dir):            # get_item derives `author` for pre-address items
        author = rec.get("author") or _author_of(rec.get("author_session"))
        idx.setdefault(author, []).append(rec["id"])
    _n = sum(len(v) for v in idx.values())
    payload = {"_derived": "authored_by index (④ L6 BOARD) — DERIVED from each item's author address; "
                           "regenerate with cc_board.rebuild_authored_by_index(). Do not hand-edit.",
               "count": _n, "item_count": _n, "authors": len(idx), "index": idx}
    d = _dir(board_dir)
    os.makedirs(d, exist_ok=True)
    _atomic_write_fsync(Path(os.path.join(d, AUTHORED_BY_INDEX)), json.dumps(payload, indent=1))
    return payload


def authored_by_index(board_dir: str | None = None, *, rebuild_if_missing: bool = True) -> dict:
    """LOAD the derived authored_by index (the map {author -> [ids]}). Rebuilds it if absent (derived data
    is always regenerable — never a fail-loud dead-end for a missing projection). Fail-loud if the on-disk
    index is corrupt (a malformed projection is a bug, not an empty answer)."""
    p = os.path.join(_dir(board_dir), AUTHORED_BY_INDEX)
    if not os.path.exists(p):
        if rebuild_if_missing:
            return rebuild_authored_by_index(board_dir)
        raise BoardError(f"no authored_by index at {p} — it is DERIVED; run "
                         f"cc_board.rebuild_authored_by_index() (or the L6 migration). Fail loud.")
    with open(p, encoding="utf-8") as f:
        try:
            payload = json.load(f)
        except Exception as e:
            raise BoardError(f"authored_by index at {p} is corrupt ({type(e).__name__}: {e}) — a derived "
                             f"projection went bad; rebuild it. Fail loud.")
    # ④ L6 adversary DENT-2: NEVER return a silently-stale index. The index is derived; if the live item
    # count no longer matches the fingerprint, an item was filed/removed since the last build → self-heal
    # by re-deriving (cheap name-scan, not a full parse). Derived data stays derived; staleness is loud.
    live = sum(1 for f in os.listdir(_dir(board_dir))
               if f.endswith(".md") and not f.startswith("_"))
    if payload.get("item_count") != live:
        return rebuild_authored_by_index(board_dir)
    return payload


def items_by_author(author: str, board_dir: str | None = None, *, rebuild_if_missing: bool = True) -> list[str]:
    """The REVERSE lookup, O(1): the item ids authored by `author` (an address), via the derived index —
    NOT an O(n) reverse_traverse scan. `author` may be an address or a legacy handle (derived to an
    address). Returns [] for an author with no items (the index answers, never a scan)."""
    addr = author if "://" in (author or "") else _author_of(author)
    return list(authored_by_index(board_dir, rebuild_if_missing=rebuild_if_missing).get("index", {}).get(addr, []))


# ── PIN as a VIEW-RECORD (④ L6 BOARD, C6.6) — salience belongs to the view, never the item ────────────────
# "One store, many boards": a board_view is itself an addressed item; a PIN is a typed `pinned` edge FROM
# the view TO an item. Pinning on one view therefore does not pin on another — the pin lives on the view.
def create_view(name: str, author_session: str, *, scope: str = "global", body: str = "",
                board_dir: str | None = None, emit=None) -> dict:
    """Create a BOARD-VIEW record (item_type board_view). A view is an addressed board item; pins hang off
    it as `pinned` edges. Returns the view record (with its board://<id> address)."""
    return file_item("board_view", name, body or f"Board view: {name}", author_session,
                     scope=scope, links=None, board_dir=board_dir, emit=emit)


def _board_target(item: str) -> str:
    """Normalise a board id or board:// address to a board:// target string."""
    return item if str(item).startswith("board://") else f"board://{item}"


def pin(view_id: str, item: str, *, by: str = "", board_dir: str | None = None) -> dict:
    """PIN an item ON a board-view: append a `pinned` edge FROM the view TO the item. Fail-loud if the view
    is not a board_view. Idempotent (a duplicate pin is a no-op). Returns the updated view record."""
    view = get_item(view_id, board_dir=board_dir)         # raises if missing
    if view.get("type") != "board_view":
        raise BoardError(f"pin target {view_id!r} is type {view.get('type')!r}, not 'board_view' — a pin is "
                         f"a VIEW-record edge (salience belongs to the view). Fail loud.")
    target = _board_target(item)
    for ln in (view.get("links") or []):                  # idempotent — don't double-pin
        if ln.get("kind") == "pinned" and ln.get("target") == target:
            return view
    return edit_item(view_id, add_links=[{"kind": "pinned", "target": target}], by=by,
                     note=f"pinned {target}", board_dir=board_dir)


def pinned_on_view(view_id: str, *, board_dir: str | None = None) -> list[str]:
    """The item addresses a board-view has PINNED (its `pinned` edge targets). Empty for a view with no
    pins. This is a per-VIEW read — the same item is pinned on one view and not another by construction."""
    view = get_item(view_id, board_dir=board_dir)
    return [ln.get("target") for ln in (view.get("links") or []) if ln.get("kind") == "pinned"]


def is_pinned(item: str, view_id: str, *, board_dir: str | None = None) -> bool:
    """Is `item` pinned ON `view_id`? (Salience is view-scoped — asks THIS view, never the item globally.)"""
    return _board_target(item) in pinned_on_view(view_id, board_dir=board_dir)
