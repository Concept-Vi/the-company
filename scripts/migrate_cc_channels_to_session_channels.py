#!/usr/bin/env python3
"""scripts/migrate_cc_channels_to_session_channels.py — ONE-SHOT migration: fold the retired
cc_channels named-channel store (.data/channels/_channels/<id>.json) into the ONE named-channel store
(session_channels — <COMPANY_STORE>/agent_sessions/channels.jsonl).

Each cc record {id, name, purpose, coordinator, members[], status, shared?, created} becomes a
session_channels channel via create_channel(cid=<slug-id>, shared=…) + add_member for each handle +
archive_channel if it was archived. Members are stored VERBATIM (handles, not agent-session uuids —
registry=None: the named-channel surface, member-kind extension is a later field).

IDEMPOTENT: a channel whose id already exists on the leaf is SKIPPED (create_channel fails loud on
dup; we catch + report "exists"). The source _channels/*.json files are NOT deleted (rollback).

Run:  COMPANY_STORE=<store> .venv/bin/python scripts/migrate_cc_channels_to_session_channels.py [--apply]
Without --apply it is a DRY RUN (reports what it WOULD do, writes nothing).
"""
from __future__ import annotations
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
import fabric.config as fcfg
from runtime import session_channels as sc

CC_CHANNELS_DIR = os.path.join(ROOT, ".data", "channels", "_channels")


def _load_cc_records() -> list[dict]:
    out = []
    if not os.path.isdir(CC_CHANNELS_DIR):
        return out
    for fn in sorted(os.listdir(CC_CHANNELS_DIR)):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(CC_CHANNELS_DIR, fn), encoding="utf-8") as f:
                rec = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(rec, dict) and rec.get("id"):
            out.append(rec)
    return out


def migrate(store, *, apply: bool) -> dict:
    existing = set(sc.fold_channels(store).keys())
    report = {"created": [], "skipped_exists": [], "errors": []}
    for rec in _load_cc_records():
        cid = rec["id"]
        if cid in existing:
            report["skipped_exists"].append(cid)
            continue
        members = rec.get("members", []) or []
        shared = bool(rec.get("shared"))
        coord = (rec.get("coordinator") or "").strip() or None
        archived = rec.get("status") == "archived"
        plan = {"id": cid, "name": rec.get("name") or cid, "shared": shared,
                "members": members, "coordinator": coord, "archived": archived}
        if not apply:
            report["created"].append(plan)
            continue
        try:
            # mode stays 'direct'. sc.create_channel stores `coordinator` verbatim in direct mode (the
            # member-must-be-coordinator rule applies ONLY to conducted mode), so the cc coordinator
            # HANDLE is preserved FAITHFULLY on the coordinator field — NOT folded into the roster.
            row = sc.create_channel(store, name=rec.get("name") or cid,
                                    purpose=rec.get("purpose") or "",
                                    members=[], mode="direct", coordinator=coord,
                                    cid=cid, shared=shared, registry=None)
            for h in members:
                if h and h not in row.get("members", {}):
                    try:
                        sc.add_member(store, cid, h, registry=None)
                    except Exception as e:  # noqa: BLE001
                        report["errors"].append(f"{cid} add_member {h}: {e}")
            if archived:
                sc.archive_channel(store, cid)
            report["created"].append(plan)
            existing.add(cid)
        except Exception as e:  # noqa: BLE001
            report["errors"].append(f"{cid}: {type(e).__name__}: {e}")
    return report


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    store = FsStore(fcfg.STORE_DIR)
    print(f"store: {fcfg.STORE_DIR}  ({'APPLY' if apply else 'DRY RUN'})")
    print(f"source: {CC_CHANNELS_DIR}  ({len(_load_cc_records())} records)")
    rep = migrate(store, apply=apply)
    print(f"\ncreated ({len(rep['created'])}):")
    for c in rep["created"]:
        print(f"  {c['id']:<24} shared={c['shared']!s:<5} archived={c['archived']!s:<5} "
              f"members={len(c['members'])} coord={c['coordinator']}")
    if rep["skipped_exists"]:
        print(f"\nskipped (already on leaf): {rep['skipped_exists']}")
    if rep["errors"]:
        print(f"\nERRORS ({len(rep['errors'])}):")
        for e in rep["errors"]:
            print(f"  {e}")
        sys.exit(1)
    print("\nOK")
