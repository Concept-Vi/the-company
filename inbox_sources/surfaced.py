"""inbox_sources/surfaced.py — surfaced INTENTS awaiting approve/reject (the operator inbox, `Suite.inbox`).

Rides `Suite.list_surfaced()` (the SAME store the bridge's `/api/surfaced` and `/api/inbox` read) — no
parallel surfaced read. T3-HYGIENE mirrors `Suite.inbox_lanes()`: `test_origin`-tagged items (a run under
COMPANY_TEST_RUN) are excluded — that pollution is exactly what buried the real items there. Only items
with `resolved is None` are "needs me" (a resolved item is already handled — audit-only, not a card).

The verbs POST straight to `/api/resolve` (`SUITE.resolve_surfaced`) with `{id, choice, reason}` — the
verb's OWN `id` ("approve"/"reject") IS the `choice` the front end sends (one declared verb list, no
per-card special-casing needed client-side)."""


def fetch() -> list:
    import os
    from fabric import config as fcfg
    from runtime.suite import Suite
    from store.fs_store import FsStore
    from runtime.registry import NodeRegistry

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    suite = Suite(FsStore(fcfg.STORE_DIR), NodeRegistry().discover([os.path.join(root, "nodes")]))

    out = []
    for d in suite.list_surfaced():
        if d.get("test_origin"):                    # T3-HYGIENE: never a real operator item
            continue
        if d.get("resolved") is not None:            # already handled — not "needs me"
            continue
        payload = d.get("payload") or {}
        title = (payload.get("title") or payload.get("intent") or payload.get("name")
                  or d.get("action") or d.get("id"))
        why = f"Surfaced ‘{d.get('action')}’ needs your approve/reject"
        if d.get("default"):
            why += f" — default if ignored: {d.get('default')}"
        out.append({
            **d,
            "address": f"surfaced://{d.get('id')}",
            "title": str(title),
            "why": why,
            "created": payload.get("created") or payload.get("ts") or "",
        })
    return out


INBOX_SOURCE = {
    "id": "surfaced",
    "label": "Surfaced",
    "fetch": "inbox_sources.surfaced:fetch",
    "card_shape": {
        "id_field": "id", "address_field": "address", "title_field": "title",
        "why_field": "why", "created_field": "created",
    },
    "verbs": [
        {"id": "approve", "label": "Approve", "door": "/api/resolve"},
        {"id": "reject", "label": "Reject", "door": "/api/resolve"},
    ],
}
