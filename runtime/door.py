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
# The generalised row (Tim 2026-06-29: moments × scopes × conditions — "nothing that isn't structurally
# known at join/create/registration exists"):
#   moment   — WHICH mechanical moment shows this line: register (default) | channel-join |
#              channel-create | project-join | project-create | all.
#   scope    — WHERE it applies: global (default — the "+default" every card carries) |
#              channel:<name> | project:<id> (the per-channel/per-project MODIFICATION rows).
#   audience — WHO sees it (role-dependent): omitted = everyone; else a comma list matched against the
#              member's name/handle.
#   until    — WHEN it stops (temporal/open items): ISO date/datetime; an expired row silently leaves
#              the card (the LIVE resolution — no stale standing orders). Standing rows omit it.
DOOR_FIELDS = ("id", "line", "depth", "order", "moment", "scope", "audience", "until")
REQUIRED = ("id", "line", "depth")
MOMENTS = ("register", "channel-join", "channel-create", "project-join", "project-create", "all")


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
        if decl.get("moment", "register") not in MOMENTS:
            raise ValueError(f"door/{name}.py: unknown moment {decl['moment']!r} — valid {list(MOMENTS)}. Fail loud.")
        rows.append(decl)
    return sorted(rows, key=lambda r: (r.get("order", 100), r["id"]))


def _row_applies(r: dict, *, moment: str, channel: str | None, project: str | None,
                 reg: dict, now: str | None = None) -> bool:
    """The LIVE condition resolution — evaluated at compose time, so the card is always the current set:
    moment gate · scope gate (global rows everywhere; channel:/project: rows only in their scope) ·
    audience gate (role-dependent) · until gate (temporal — expired rows leave the card)."""
    m = r.get("moment", "register")
    if m != "all" and m != moment:
        return False
    scope = r.get("scope", "global")
    if scope.startswith("channel:") and scope.split(":", 1)[1] != (channel or ""):
        return False
    if scope.startswith("project:") and scope.split(":", 1)[1] != (project or ""):
        return False
    aud = r.get("audience")
    if aud:
        who = {(reg.get("name") or "").lower(), (reg.get("handle") or "").lower()}
        if not ({a.strip().lower() for a in aud.split(",")} & who):
            return False
    until = r.get("until")
    if until:
        from datetime import datetime, timezone
        ts = now or datetime.now(timezone.utc).isoformat()
        if ts[:len(until)] > until:                    # ISO prefix compare — date or datetime both work
            return False
    return True


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


def compose_card(reg: dict, *, moment: str = "register", channel: str | None = None,
                 project: str | None = None, door_dir: str | None = None,
                 message_types_dir: str | None = None, now: str | None = None,
                 room: dict | None = None) -> str:
    """The RESOLVED card for a mechanical MOMENT (register · channel-join · channel-create ·
    project-join/create). Every section is live-folded at compose time: identity from the registration,
    verbs from message_types/, entries from door/ filtered by moment × scope × audience × until — so a
    channel card = the global default rows + that channel's modification rows, temporal rows expire out,
    role rows show only to their audience. Nothing is baked — a registry edit IS a card edit; a card can
    never show anything but the current set (the anti-drift property, Tim 2026-06-29).

    `room` (2026-07-13, the join-orientation extension): the LIVE state of the room being entered,
    supplied by the caller who holds it (session_channels — the door renders, it does not fetch):
    {purpose, members: int, posts: int, open_board: [(id, title), …], board_open_count: int,
     recent: [(from, text), …]} — every key optional; only present keys render (conditioned, like
    the rows). Joining a room mid-conversation should FEEL like being handed the room's state."""
    if moment not in MOMENTS:
        raise ValueError(f"compose_card: unknown moment {moment!r} — valid {list(MOMENTS)}. Fail loud.")
    who = reg.get("name") or reg.get("handle", "?")
    at = f' channel="{channel}"' if channel else (f' project="{project}"' if project else "")
    head = {"register": f"You are a registered member of the company fabric ({who}).",
            "channel-join": f"You ({who}) just JOINED channel '{channel}'.",
            "channel-create": f"You ({who}) just CREATED channel '{channel}' — you are its steward: "
                              f"seed its board, set its purpose, and add its door rows "
                              f"(scope 'channel:{channel}') so joiners get YOUR channel's card.",
            "project-join": f"You ({who}) just joined project '{project}'.",
            "project-create": f"You ({who}) just created project '{project}'.",
            }[moment if moment != "all" else "register"]
    lines = [f'<fabric-card moment="{moment}" handle="{reg.get("handle","?")}" name="{reg.get("name","")}"{at}>',
             head + " The board is the shared workspace across all sessions — none of us holds the "
                    "full picture; the board does.",
             "",
             f"THE VERBS (typed messages; the obligation is enforced until your reply lands on the board): {verb_table(message_types_dir)}",
             "  reply: cc_board.reply_to_mention('text'[, comment_addr='<ID>' when several are open])",
             "  name yourself once so others can @you: cc_channels.register_self(name='<your-role>')",
             "",
             "DEPTH (each line is one resolve away — read when needed, never all at once):"]
    for r in door_rows(door_dir):
        if _row_applies(r, moment=moment, channel=channel, project=project, reg=reg, now=now):
            lines.append(f"- {r['line']} → {r['depth']}")
    if room:
        lines.append("")
        lines.append("THE ROOM (live state at this moment — resolved, never baked):")
        if room.get("purpose"):
            lines.append(f"  purpose: {room['purpose']}")
        counts = []
        if room.get("members") is not None:
            counts.append(f"{room['members']} members")
        if room.get("posts") is not None:
            counts.append(f"{room['posts']} posts")
        if counts:
            lines.append("  " + " · ".join(counts))
        if room.get("board_open_count"):
            lines.append(f"  board — {room['board_open_count']} item(s) awaiting attention "
                         f"(cc_board list, scope channel://{channel}):")
            for bid, title in (room.get("open_board") or [])[:3]:
                lines.append(f"    - {bid} · {title}")
        for frm, txt in (room.get("recent") or [])[:3]:
            lines.append(f"  recent · {frm}: {txt}")
    lines.append("</fabric-card>")
    return "\n".join(lines)
