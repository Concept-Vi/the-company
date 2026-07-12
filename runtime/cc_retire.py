"""runtime/cc_retire.py — the reusable RETIREMENT component (member-retire + channel-retire).

Tim 2026-06-22: the harvest "is probably good practice for member retirement and channel retirement, worth
building in as a reusable component for channels along with all that image stuff." This makes the wind-down
HARVEST a repeatable VERB — so when a member (session) or a channel retires, its perspective/totality is
crystallized into the ONE corpus (structured, attributed, linked, honest-state, coverage-checked) BEFORE it
closes, instead of being lost.

Two retirements, both reusing existing seams (no parallel machinery):
  • MEMBER retire — a session crystallizes its OWN perspective: the agent recollects its past (session_recall)
    and produces structured CLAIMS; harvest_member() ENFORCES the discipline (every claim honest-state-tagged
    verified|attempted|broken|abandoned — no self-certified "done" into permanent memory), ingests it into the
    corpus, and files an attributed, linked board record. The intelligence (the perspective) is the agent's;
    the component guarantees structure + honest-tags + provenance + linking + ingest.
  • CHANNEL retire — crystallizes a channel's TOTALITY: its members, their member-harvests, its attachments
    (images/docs/board), and its board items → ONE channel-retirement corpus record that LINKS them all, with
    a coverage check (are all members harvested?). Archiving the channel is an EXPLICIT opt-in (never auto —
    a live coordination channel is not closed as a side effect).

Reuses: session_recall (recollect-own-past — recollection's verified backbone) · corpus.write_record (into the
corpus) · cc_board (the linked record + typed edges) · cc_attachments (the manifest) · cc_channels (members +
archive). Honest-state is the non-negotiable (the keystone-poisoning lesson: a fake "done" in permanent memory
is the worst outcome).
"""
from __future__ import annotations

import os

from runtime import corpus as _corpus
from runtime import cc_board as _board
from runtime import cc_attachments as _att
from runtime import session_channels as _sc   # channel_members/archive_channel live here (moved 2026-06-29)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARVEST_DIR = os.path.join(REPO, "build-prep", "the-one-application", "harvest")

VALID_STATUS = ("verified", "attempted-unverified", "broken", "abandoned")


class RetireError(RuntimeError):
    """A retirement op could not run — raised TEACHING-loud (never a silent no-op)."""


def _harvest_files() -> list[str]:
    if not os.path.isdir(HARVEST_DIR):
        return []
    return [f for f in os.listdir(HARVEST_DIR) if f.endswith(".md")]


def harvest_status(store, channel: str) -> dict:
    """COVERAGE LEDGER for a channel's retirement: each member → has it crystallized a harvest? A member is
    'harvested' if a harvest file names its handle OR a board item carries author_session==handle. Returns
    {members, harvested, missing, complete} — the fail-loud coverage proof before a channel closes."""
    members = _sc.channel_members(store, channel)
    files = _harvest_files()
    harvested, missing = [], []
    for m in members:
        in_file = any(m in f for f in files)
        in_board = bool(_board.reverse_traverse(f"session://{m}", "authored_by")) if not in_file else False
        (harvested if (in_file or in_board) else missing).append(m)
    return {"channel": channel, "members": members, "harvested": harvested,
            "missing": missing, "complete": not missing}


def harvest_member(store, session_id: str, *, claims: list, summary: str = "",
                   open_questions: list | None = None, dead_ends: list | None = None,
                   links: list | None = None, project: str = "company") -> dict:
    """MEMBER retire: crystallize a session's perspective into the corpus, ENFORCING honest-state. `claims` =
    [{text, status, ...}] — every one MUST carry a status in VALID_STATUS (fail-loud: no self-certified
    'done'). Ingests a structured record into the corpus (attributed to the session) + files a linked board
    item. Returns {corpus, board, address}."""
    if not session_id:
        raise RetireError("harvest_member needs `session_id` (the retiring member — provenance).")
    if not claims:
        raise RetireError("harvest_member needs `claims` (the perspective) — an empty harvest is not honest.")
    bad = [c for c in claims if not isinstance(c, dict) or c.get("status") not in VALID_STATUS]
    if bad:
        raise RetireError(
            f"{len(bad)} claim(s) missing an honest-state tag — every claim MUST be tagged one of "
            f"{list(VALID_STATUS)} (+ why). No self-certified 'done' into the permanent corpus (the "
            f"keystone-poisoning). First offender: {bad[0]!r}")
    record = {"session": session_id, "summary": summary, "claims": claims,
              "open_questions": list(open_questions or []), "dead_ends": list(dead_ends or [])}
    src = f"retire/member/{session_id}"
    ev = _corpus.write_record(store, source_address=src, output=record, kind="retirement-member",
                              lineage={"session": session_id, "round": "retire", "project": project})
    item = _board.file_item("note", f"Member retirement — {session_id}",
                            summary or f"{len(claims)} claims, honest-state-tagged.", session_id,
                            links=(links or []) + [{"kind": "sourced_from", "target": ev["address"]}])
    return {"corpus": ev["address"], "board": item["address"], "session": session_id,
            "claim_count": len(claims)}


def retire_channel(store, channel: str, *, author_session: str, summary: str = "",
                   archive: bool = False, project: str = "company") -> dict:
    """CHANNEL retire: crystallize a channel's TOTALITY into the corpus + a linked board record, with a
    coverage check. Gathers members + their harvests + attachments + board items, writes ONE findable
    channel-retirement corpus record linking them, and (only if `archive=True`, explicit) archives the
    channel. Returns {corpus, board, coverage, archived}. Fail-loud surfaces coverage gaps — does NOT block
    (an honest 'these members did not harvest' is recorded), and NEVER auto-archives a live channel."""
    if not author_session:
        raise RetireError("retire_channel needs `author_session` (who is performing the retirement).")
    cov = harvest_status(store, channel)
    manifest = _att.manifest(channel).get("attachments", {})
    board_items = [i for i in _board.list_items() if i.get("channel") == channel]
    harvest_files = [f for f in _harvest_files()]
    record = {
        "channel": channel, "retired_by": author_session, "summary": summary,
        "members": cov["members"], "harvested": cov["harvested"], "missing_harvest": cov["missing"],
        "coverage_complete": cov["complete"],
        "attachments": {k: len(v) for k, v in manifest.items()},
        "board_item_count": len(board_items),
        "member_harvests": [f for f in harvest_files
                            if any(m in f for m in cov["members"])],
    }
    src = f"retire/channel/{channel}"
    ev = _corpus.write_record(store, source_address=src, output=record, kind="retirement-channel",
                              lineage={"session": author_session, "round": "retire", "project": project})
    # the linked board record — references the channel's attachments + (the corpus record carries the harvests)
    links = [{"kind": "sourced_from", "target": ev["address"]}]
    for typ, targets in manifest.items():
        for t in targets[:50]:                      # cap the edge fan-out per type (logged in the record's counts)
            links.append({"kind": "references", "target": t})
    item = _board.file_item("note", f"Channel retirement — {channel}",
                            (summary or "Channel totality crystallized into the corpus.") +
                            (f"\n\n⚠ coverage gap: members without a harvest: {cov['missing']}" if cov["missing"] else
                             "\n\ncoverage: complete (all members harvested)."),
                            author_session, channel=channel, links=links)
    archived = False
    if archive:
        _row = _sc.get_channel(store, channel)
        if (_row or {}).get("kind") == "gathering":
            raise RetireError(
                f"retire_channel: {channel!r} is a GATHERING — gatherings DISPERSE, they do not archive "
                f"(archive_channel refuses a non-channel). The totality is crystallized above; call "
                f"channel_act(action='disperse', channel=…) to close it.")
        _sc.archive_channel(store, channel)         # EXPLICIT opt-in only — never a side effect
        archived = True
    return {"corpus": ev["address"], "board": item["address"], "coverage": cov,
            "archived": archived, "attachments": record["attachments"]}
