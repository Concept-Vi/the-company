"""runtime/conversations.py — THE CONVERSATION-CONTENT RECORD the company was missing.

THE GAP THIS FILLS (verified live 2026-06-28, build-prep/openwebui-company-fusion/
fusion-conversations-sessions.md §0): the company had NO message-content store with parent/child
structure. `agent_sessions/<uuid>.json` is metadata + a `jsonl_path` POINTER at a foreign
Claude-Code transcript; `events.jsonl` `agent_sessions.turn` rows carry a summary string, no body;
`session_recall` reads message text DIRECTLY from the foreign CC `.jsonl` and stores nothing of its
own; `chat.jsonl` is a degenerate operator-console twin (a flat log, no thread/conversation id).
So conversation CONTENT lived only in foreign CC transcripts the company merely points at.

WHAT THIS IS — one record, branchable, that ANY FACE is a view onto. A single conversation is an
append-only leaf of message EVENTS; a read-time fold reconstructs the branching message DAG and the
`current` displayed path. OpenWebUI's chat shape (parentId / childrenIds / currentId) is the DONOR
SHAPE — expressed here in company grammar (parent_id; children COMPUTED by the fold; current = the
folded leaf path). OWUI contributes the SHAPE, not a second database: the OWUI chat UI, the company
chat surfaces, voice — each becomes a VIEW that reads/writes THIS record through this API. No
parallel store, no JSON-blob rewrite, no half-finished ChatMessage table — the migration OWUI never
finished is resolved here by keeping only the normalized append-only form.

TOPOLOGY (deliberately NOT session_channels' one-leaf-many-rows). A conversation is its OWN leaf —
`<store>/store/conversations/<conversation_id>.jsonl` — append-only, graph-locked PER CONVERSATION
(so two conversations never serialize against each other), fsync'd. `fold_conversation(cid)` folds
ONE file into ONE message tree + current path; `list_conversations` is a DIRECTORY SCAN. The append/
seq/fsync/fail-loud IDIOMS mirror runtime/session_channels.append_channel_event exactly (reuse, not
parallel); only the topology differs because the record's grain differs (one conversation ≠ a
registry of many channels).

THE BRANCHING MODEL (the donor shape, natively).
  · A MESSAGE event: {seq, ts, conversation_id, message_id, parent_id, role, content, model_id?,
    files?, sources?, attribution, edited_of?, regen_of?, kind:"message"}.
  · parent_id → the DAG edge. The fold inverts parent_id into each node's `children` (OWUI's
    childrenIds, computed not stored — log-IS-the-index). A root message has parent_id=None.
  · BRANCHING = two messages sharing one parent_id (a regen or an edit re-run). Both survive on the
    leaf; the fold keeps both retrievable under the parent's `children`.
  · EDIT / REGEN = a new message event carrying edited_of / regen_of (provenance) under the same
    parent_id as the message it supersedes — OWUI's edit/regen UX expressed as append-only events.
  · CURRENT (OWUI's currentId) = the displayed leaf. Default rule: LAST-APPENDED message wins (each
    new/regen node becomes current, exactly as OWUI advances currentId). A face MAY override the
    displayed branch by appending a `select` event (kind:"select", message_id=<the chosen leaf>) —
    branch navigation as a non-message event (the channel.mode_set analogue), so picking which
    branch a view shows is itself a recorded, foldable act. `current` = the path from the selected
    (or last-appended) leaf back to its root via parent_id.

THE FLOOR (same side as session_channels / the MCP face). This module NEVER spawns, never resumes a
session, never imports the supervisor. Writes are store appends. It emits NO `agent_sessions.*`
events on events.jsonl — the single-writer law (audit C6) stays intact: conversation content lives
on its OWN per-conversation leaf.

SCOPE (increment 1 — build-prep brief). The store + shape + API ONLY: correct + inert-but-usable.
The live supervisor's `_reader()` is NOT wired to write here yet (increment 2 — it touches core);
no existing data is migrated; `session_recall` is not re-pointed yet (one-line source swap, §3.4 of
the proposal, once content is born here). Consumers to come: the supervisor reader (agent turns),
the OWUI/operator chat surface (human turns), session_recall + recollection (index THIS, not foreign
files).
"""
from __future__ import annotations

import json
import os
import uuid as _uuid
from datetime import datetime, timezone

# ── the closed vocabulary (registry-is-truth: defined ONCE, here) ──────────────────────────────
# Event kinds on a conversation leaf. A new kind is added HERE and folded in _apply_event — nowhere
# else. "message" is the DAG node; "select" is branch-navigation (which leaf a view displays).
EVENT_KINDS = ("message", "select")
ROLES = ("user", "assistant", "system", "tool")   # the speakers a turn may carry (open as needed)

DIR = "conversations"                              # <store>/conversations/<cid>.jsonl
LOCK_PREFIX = "conversations:"                     # per-conversation append lock (NOT one global lock)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _conv_addr(cid: str) -> str:
    cid = cid.strip()
    return cid if cid.startswith("conversation://") else f"conversation://{cid}"


def _conv_bare(ref: str) -> str:
    ref = (ref or "").strip()
    return ref[len("conversation://"):] if ref.startswith("conversation://") else ref


def _safe_cid(cid: str) -> str:
    """A conversation id is a filename leaf — reject path-escaping ids loud (a black hole, store rule
    4). Bare ids only (slashes/.. would write outside the conversations dir)."""
    bare = _conv_bare(cid)
    if not bare:
        raise ValueError("conversations: empty conversation id — give a real id (or use new_conversation()).")
    if "/" in bare or "\\" in bare or bare in (".", "..") or bare.startswith("."):
        raise ValueError(
            f"conversations: unsafe conversation id {bare!r} — ids are bare leaf names (no path "
            f"separators, no dot-prefix). Mint one with new_conversation().")
    return bare


def _dir(store):
    return store.root / DIR


def _leaf_path(store, cid: str):
    return _dir(store) / f"{_safe_cid(cid)}.jsonl"


# ── the leaf (append + read — the append_channel_event discipline, per-conversation file) ──────
def _append_event(store, cid: str, rec: dict) -> dict:
    """Persist ONE event to a conversation's append-only leaf. STRUCTURAL fail-loud: `kind` in the
    closed EVENT_KINDS vocabulary. Owns `seq`/`ts`/`conversation_id` (never caller-overridable).
    Cross-process-unique monotonic per-conversation seq under a PER-CONVERSATION graph_lock (every
    Claude Code session runs its own MCP-face process over this one store — the append_event landmine,
    closed here exactly as for mail/channels). Fsync'd before return: an event you were told persisted
    survives a crash."""
    bare = _safe_cid(cid)
    kind = rec.get("kind")
    if kind not in EVENT_KINDS:
        raise ValueError(
            f"conversations._append_event: unknown kind {kind!r} — the closed vocabulary is "
            f"{list(EVENT_KINDS)} (registry-is-truth; a new event kind is added to "
            f"runtime/conversations.EVENT_KINDS + its fold, never ad-hoc).")
    d = _dir(store)
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{bare}.jsonl"
    with store.graph_lock(LOCK_PREFIX + bare):
        seq = 0
        if path.exists():
            with path.open("rb") as f:
                try:
                    f.seek(-2, 2)
                    while f.read(1) != b"\n":
                        f.seek(-2, 1)
                except OSError:
                    f.seek(0)
                last = f.readline().decode().strip()
            if last:
                seq = json.loads(last).get("seq", -1) + 1
        out = {**rec, "kind": kind, "conversation_id": bare, "seq": seq, "ts": _now()}
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(out) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return out


def conversation_events_since(store, cid: str, seq: int = -1, *, limit: int | None = None) -> list[dict]:
    """A conversation's events with seq STRICTLY greater than `seq`, OLDEST-first (the events_since
    semantics — a fresh consumer passes -1). Reads disk every call (a sibling process's appends are
    seen next call). Honest empty list when the conversation has no leaf yet."""
    path = _leaf_path(store, cid)
    if not path.exists():
        return []
    out = []
    for l in path.read_text(encoding="utf-8").splitlines():
        if not l.strip():
            continue
        rec = json.loads(l)
        if rec.get("seq", -1) <= seq:
            continue
        out.append(rec)
        if limit is not None and len(out) >= limit:
            break
    return out


# ── the API ────────────────────────────────────────────────────────────────────────────────────
def new_conversation(store, *, title: str | None = None, cid: str | None = None,
                     source: str | None = None) -> str:
    """Mint a conversation id (used verbatim if supplied, else a fresh `conv-<hex>`). A conversation
    is born on its FIRST appended message — this only resolves the id (no empty-leaf write), mirroring
    how OWUI mints a chat id before the first turn. `source` (e.g. "supervisor"/"owui"/"operator") and
    `title` are not stored by this call; pass them on the first append_message's attribution/extra."""
    if cid is not None:
        return _safe_cid(cid)
    return f"conv-{_uuid.uuid4().hex[:12]}"


def append_message(store, cid: str, *, role: str, content, parent_id: str | None = None,
                   message_id: str | None = None, model_id: str | None = None,
                   files=None, sources=None, attribution: dict | None = None,
                   edited_of: str | None = None, regen_of: str | None = None,
                   extra: dict | None = None) -> dict:
    """Append ONE message event (the DAG node — donor shape from OWUI, named in company grammar).

    `role` ∈ ROLES. `parent_id` = the DAG edge (None for a root). `message_id` is minted (`msg-<hex>`)
    when not supplied. BRANCHING: append two messages with the SAME `parent_id` (a regen/edit re-run)
    — both survive; the fold keeps both retrievable under the parent's children, and (default rule)
    the LAST-appended becomes `current` (OWUI's currentId advance). `edited_of`/`regen_of` record
    provenance of an edit/regen variant. Returns the stored event (with its minted message_id + seq)."""
    if role not in ROLES:
        raise ValueError(f"append_message: unknown role {role!r} — the speaker vocabulary is "
                         f"{list(ROLES)} (extend runtime/conversations.ROLES, never ad-hoc).")
    if content is None:
        raise ValueError("append_message: `content` is None — a message with no body is unfoldable. "
                         "Pass a string (or a structured content value); empty string is allowed.")
    mid = (message_id or "").strip() or f"msg-{_uuid.uuid4().hex[:12]}"
    rec = {"kind": "message", "message_id": mid, "parent_id": parent_id, "role": role,
           "content": content}
    if model_id is not None:
        rec["model_id"] = model_id
    if files is not None:
        rec["files"] = files
    if sources is not None:
        rec["sources"] = sources
    if attribution is not None:
        rec["attribution"] = attribution
    if edited_of is not None:
        rec["edited_of"] = edited_of
    if regen_of is not None:
        rec["regen_of"] = regen_of
    if extra:
        rec.update({k: v for k, v in extra.items() if k not in rec and k not in (
            "kind", "seq", "ts", "conversation_id")})
    return _append_event(store, cid, rec)


def select_branch(store, cid: str, message_id: str) -> dict:
    """Set the DISPLAYED leaf (OWUI's currentId) to `message_id` — branch navigation a face does when
    it walks siblings. A recorded, foldable act (the channel.mode_set analogue): the fold's `current`
    path then runs from this selected leaf, overriding the last-appended default. Fail-loud if the id
    is not in the conversation (a view cannot select a leaf that was never said)."""
    bare = _safe_cid(cid)
    ids = {e.get("message_id") for e in conversation_events_since(store, bare, -1)
           if e.get("kind") == "message"}
    if message_id not in ids:
        raise ValueError(
            f"select_branch: message {message_id!r} is not in conversation://{bare} — selectable "
            f"leaves are the messages on its leaf ({sorted(i for i in ids if i)}). Fail loud, never "
            f"select a phantom leaf.")
    return _append_event(store, bare, {"kind": "select", "message_id": message_id})


def fold_conversation(store, cid: str) -> dict:
    """Project the conversation's branching DAG + the current displayed path from its leaf. Read-time
    fold, no parallel store: a fresh process rebuilds everything from shared disk. Mirrors fold_channels'
    log-IS-the-index discipline, on a single conversation's file.

    Returns: {id, conversation_id, messages:{mid→node}, roots:[mid], current:[mid…], current_leaf,
    selected, count, seq}. Each node = {message_id, parent_id, role, content, model_id?, files?,
    sources?, attribution?, edited_of?, regen_of?, children:[mid], seq, ts} — `children` is the
    COMPUTED inverse of parent_id (OWUI's childrenIds). `current` is the linear path from the current
    leaf (the last `select`ed message, else the LAST-appended message) back to root via parent_id."""
    bare = _safe_cid(cid)
    events = conversation_events_since(store, bare, -1)
    messages: dict[str, dict] = {}
    roots: list[str] = []
    order: list[str] = []          # message_ids in append order (last = default current leaf)
    selected: str | None = None    # the last branch-selection event's message_id (informational)
    # current leaf = the leaf set by the LATEST navigation, where BOTH a message-append (OWUI advances
    # currentId on every new message) AND a `select` (explicit branch nav) are navigations. The event
    # file is oldest-first, so iterating in order and overwriting current_leaf gives latest-action-wins:
    # a select sticks only UNTIL the next append (honouring the documented "if its select is the latest
    # navigation"). The earlier code took any prior select unconditionally, freezing current_leaf so a
    # reply appended after a branch-nav was invisible — fixed here (verified by use).
    current_leaf: str | None = None
    for e in events:
        k = e.get("kind")
        if k == "message":
            mid = e.get("message_id")
            node = {kk: e[kk] for kk in (
                "message_id", "parent_id", "role", "content", "model_id", "files", "sources",
                "attribution", "edited_of", "regen_of", "seq", "ts") if kk in e}
            node["children"] = []
            messages[mid] = node
            order.append(mid)
            current_leaf = mid                 # a new message advances the displayed leaf (OWUI currentId)
        elif k == "select":
            selected = e.get("message_id")
            if selected in messages:           # navigate the displayed leaf to an existing message
                current_leaf = selected
    # invert parent_id → children (OWUI childrenIds, computed), collect roots
    for mid, node in messages.items():
        pid = node.get("parent_id")
        if pid is None:
            roots.append(mid)
        elif pid in messages:
            messages[pid]["children"].append(mid)
        else:
            roots.append(mid)      # an orphan (parent unseen) — a root by construction, never dropped
    current: list[str] = []
    walk = current_leaf
    guard = set()
    while walk is not None and walk in messages and walk not in guard:
        guard.add(walk)
        current.append(walk)
        walk = messages[walk].get("parent_id")
    current.reverse()
    return {"id": _conv_addr(bare), "conversation_id": bare, "messages": messages,
            "roots": roots, "current": current, "current_leaf": current_leaf,
            "selected": selected, "count": len(messages),
            "seq": (events[-1]["seq"] if events else -1)}


def get_conversation(store, cid: str) -> dict:
    """One conversation's folded DAG, fail-loud on unknown (never fabricate a conversation). A
    conversation with no leaf (nothing ever appended) is unknown — mirror get_channel."""
    bare = _safe_cid(cid)
    if not _leaf_path(store, bare).exists():
        raise ValueError(
            f"get_conversation: unknown conversation {bare!r} — no leaf at conversations/{bare}.jsonl. "
            f"list via list_conversations; start one with append_message (new_conversation mints an "
            f"id). Fail loud, never fabricate.")
    return fold_conversation(store, bare)


def list_conversations(store) -> list[dict]:
    """Every conversation — a DIRECTORY SCAN of conversations/*.jsonl (NOT a fold of one leaf; the
    topology differs from channels by design). One lightweight summary row per conversation, newest
    activity first: {id, conversation_id, count, current_leaf, last_ts}. Honest empty list when the
    dir doesn't exist yet."""
    d = _dir(store)
    if not d.exists():
        return []
    rows = []
    for p in d.glob("*.jsonl"):
        bare = p.stem
        try:
            folded = fold_conversation(store, bare)
        except ValueError:
            continue                # an unsafe-named file someone dropped in — skip, don't crash the list
        last_ts = None
        cl = folded.get("current_leaf")
        if cl and cl in folded["messages"]:
            last_ts = folded["messages"][cl].get("ts")
        rows.append({"id": _conv_addr(bare), "conversation_id": bare, "count": folded["count"],
                     "current_leaf": cl, "last_ts": last_ts})
    rows.sort(key=lambda r: r.get("last_ts") or "", reverse=True)
    return rows
