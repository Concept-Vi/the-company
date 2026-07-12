"""runtime/door.py — THE DOOR: the resolved join-time top card (Tim, 2026-06-29 — the generalisation).

The card every session receives at the door (SessionStart) is NEVER hardcoded prose — it is COMPOSED
LIVE from the registries at injection time, so any registry change (a new message verb, a new door
entry, a renamed guide) automatically appears on the next card with zero code edits. Tim's check:
"any modification automatically results with the current set" — this module is that guarantee.

Two halves:
1. `door/<id>.py` rows — WHAT'S ON THE CARD. Each row = one line at Tim's altitude + a DEPTH address
   pointing one level deeper (the depth-layered knowledge pattern: the card is the map; detail is a
   resolve away). A capability earns a door-line by dropping a row — the card grows by LINES, not pages.
   Row schema: {id, line (required), depth (required — an address), order (optional int, low first)}.
2. `compose_card(reg)` — folds the LIVE state: the member's identity (from their registration), the
   verb table (folded from message_types/ — kinds+obligations, never a baked list), and the door rows.

Mirrors the ONE registry mechanism (message_types/item_types): file-discovered, fail-loud, id==stem.
"""
from __future__ import annotations

import importlib.util
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOOR_DIR = os.path.join(REPO, "door")
DOOR_FIELDS = ("id", "line", "depth", "order")
REQUIRED = ("id", "line", "depth")


def _load(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"door.{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return name, mod


def door_rows(door_dir: str | None = None) -> list[dict]:
    """The discovered door entries, order-sorted. Fail-loud on malformed rows (never a silent skip)."""
    d = door_dir or DOOR_DIR
    rows = []
    if not os.path.isdir(d):
        return rows
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".py") or fn.startswith("_"):
            continue
        name, mod = _load(os.path.join(d, fn))
        decl = getattr(mod, "DOOR", None)
        if decl is None:
            continue
        if not isinstance(decl, dict):
            raise ValueError(f"door/{name}.py: DOOR must be a dict. Fail loud.")
        unknown = [k for k in decl if k not in DOOR_FIELDS]
        if unknown:
            raise ValueError(f"door/{name}.py: unknown fields {unknown} — valid {list(DOOR_FIELDS)}. Fail loud.")
        missing = [k for k in REQUIRED if not decl.get(k)]
        if missing:
            raise ValueError(f"door/{name}.py: missing required {missing}. Fail loud.")
        if decl["id"] != name:
            raise ValueError(f"door/{name}.py: id {decl['id']!r} != filename {name!r}. Fail loud.")
        rows.append(decl)
    return sorted(rows, key=lambda r: (r.get("order", 100), r["id"]))


def verb_table(message_types_dir: str | None = None) -> str:
    """The verb line, FOLDED from the live message_types registry — a new verb row appears here
    automatically (grouped by obligation, e.g. 'mention/ask→reply · review_request→verdict ·
    handoff→ack · fyi→none')."""
    from runtime.message_types import MessageTypeRegistry
    reg = MessageTypeRegistry().discover([message_types_dir or os.path.join(REPO, "message_types")])
    by_ob: dict[str, list[str]] = {}
    for k in sorted(reg):
        by_ob.setdefault(reg[k].obligation, []).append(k)
    order = ("reply", "verdict", "ack", "none")
    parts = [f"{'/'.join(ks)}→{ob}" for ob in order if (ks := by_ob.get(ob))]
    parts += [f"{'/'.join(ks)}→{ob}" for ob, ks in sorted(by_ob.items()) if ob not in order]
    return " · ".join(parts)


def compose_card(reg: dict, *, door_dir: str | None = None, message_types_dir: str | None = None) -> str:
    """The RESOLVED top card for a just-registered member `reg` ({handle, name, ...}). Every section is
    live-folded: identity from the registration, verbs from message_types/, entries from door/. Nothing
    here is baked — a registry edit IS a card edit."""
    who = reg.get("name") or reg.get("handle", "?")
    lines = [f'<fabric-membership handle="{reg.get("handle","?")}" name="{reg.get("name","")}">',
             f"You are a registered member of the company fabric ({who}). The board is the shared "
             "workspace across all sessions — none of us holds the full picture; the board does.",
             "",
             f"THE VERBS (typed messages; the obligation is enforced until your reply lands on the board): {verb_table(message_types_dir)}",
             "  reply: cc_board.reply_to_mention('text'[, comment_addr='<ID>' when several are open])",
             "  name yourself once so others can @you: cc_channels.register_self(name='<your-role>')",
             "",
             "DEPTH (each line is one resolve away — read when needed, never all at once):"]
    for r in door_rows(door_dir):
        lines.append(f"- {r['line']} → {r['depth']}")
    lines.append("</fabric-membership>")
    return "\n".join(lines)
