"""runtime/needs_me.py — the NEEDS-ME INBOX fold (I1): every registered `inbox_sources/*` row folded into
ONE card list for the operator's Inbox view.

`needs_me_inbox()` is the WHOLE contract: discover the file-registered sources (`runtime.inbox_sources`,
mirrors `runtime.item_types`), call each source's `fetch()`, lift its raw items into the uniform CARD
SHAPE via the row's declared `card_shape` field-name hints, and fold every source's cards into one
newest-first list.

FAIL-SOFT PER SOURCE, LOUD IN THE PAYLOAD (the I1 spec's non-negotiable): a broken source (a bad `fetch`
reference, an exception fetching, a raw item missing a hinted field) must never blank Tim's whole inbox —
its exception is CAUGHT at the per-source boundary and recorded into `errors[]` (source id + the real
exception message), and every OTHER source's cards still render. This is fail-soft only at that one
boundary — inside a source, a genuinely malformed raw item (no id) still raises, but that raise is scoped
to its OWN source's try/except, never propagating past it. Nothing is ever silently dropped without a
trace in `errors[]` — a silent narrowing of the inbox would be a silent failure (rule 4).

CARD SHAPE (the contract `operator/app/src/views/Inbox.tsx` reads):
    {source, id, address, title, why, verbs: [{id, label, door}], created}
`source` = the inbox-source's id (the badge). `verbs[].door` has already had `{id}`/`{address}` tokens
substituted for THIS card (the registry row declares one templated verb list; every card gets its own
resolved doors)."""
from __future__ import annotations

import os

from runtime.inbox_source_registry import InboxSourceRegistry, resolve_fetch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INBOX_SOURCES_DIR = os.path.join(ROOT, "inbox_sources")


def _substitute_verb(verb: dict, card_id: str, address: str) -> dict:
    door = verb["door"].replace("{id}", str(card_id)).replace("{address}", str(address))
    return {"id": verb["id"], "label": verb["label"], "door": door}


def _build_card(source_id: str, card_shape: dict, verbs: list, raw: dict) -> dict:
    cid = raw.get(card_shape["id_field"])
    if cid is None or cid == "":
        raise ValueError(
            f"inbox source {source_id!r}: a raw item is missing {card_shape['id_field']!r} — a card "
            f"needs an id. Fail loud (never a card with no address to act on).")
    address = raw.get(card_shape["address_field"]) or ""
    title = raw.get(card_shape["title_field"]) or f"{source_id} item"
    why = raw.get(card_shape["why_field"]) or ""
    created = raw.get(card_shape["created_field"]) or ""
    return {
        "source": source_id,
        "id": str(cid),
        "address": str(address),
        "title": str(title),
        "why": str(why),
        "verbs": [_substitute_verb(v, cid, address) for v in verbs],
        "created": str(created) if created else "",
    }


def needs_me_inbox(*, dirs: list | None = None) -> dict:
    """Fold every registered `inbox_sources/*` row into ONE card list. Returns
    {cards, count, sources, errors} — `errors` is the fail-soft side-channel (never silent; see module
    docstring). `cards` is sorted newest-first by `created` where determinable (items with no discoverable
    timestamp — e.g. decision rows, which the registry carries no `created` for — sort after every timed
    card, in their source's own discovery order; never crashes, never pretends a false precision)."""
    reg = InboxSourceRegistry().discover(dirs or [INBOX_SOURCES_DIR])
    cards: list[dict] = []
    errors: list[dict] = []
    for sid in sorted(reg):
        row = reg[sid]
        try:
            fn = resolve_fetch(row.fetch)
            raw_items = fn()
            if not isinstance(raw_items, list):
                raise TypeError(
                    f"inbox source {sid!r}: fetch() must return a list, got {type(raw_items).__name__}")
            for raw in raw_items:
                if not isinstance(raw, dict):
                    raise TypeError(
                        f"inbox source {sid!r}: fetch() returned a non-dict item ({type(raw).__name__})")
                cards.append(_build_card(sid, row.card_shape, row.verbs, raw))
        except Exception as e:               # PER-SOURCE fail-soft — one broken feed never blanks the rest
            errors.append({"source": sid, "error": f"{type(e).__name__}: {e}"})

    cards.sort(key=lambda c: c["created"], reverse=True)   # stable: undated cards keep discovery order
    return {"cards": cards, "count": len(cards), "sources": sorted(reg), "errors": errors}
