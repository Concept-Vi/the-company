#!/usr/bin/env python3
"""ops/hooks/auto_register.py — JOIN-TIME MECHANICS (Tim, 2026-06-29): membership + the handbook at the door.

A SessionStart hook. Two jobs, both mechanical (they happen for EVERY company session, unskippable):
1. AUTO-REGISTER — register_self(): this session becomes an addressable fabric member (idempotent per
   claude-ancestor PID; an existing registration is updated, never duplicated). `self`/`reply` resolve;
   @mentions reach it.
2. THE TOP CARD — inject the SMALL handbook card into the session's starting context: who you are, the
   few verbs, and ADDRESSES POINTING ONE LEVEL DEEPER (guide://channel_collaboration, the D0 protocol
   block). Depth-layered: the agent gets the map at the door; detail is a resolve away — never the full
   context. This is the mechanism that keeps the protocols from being lost: not docs someone might read,
   an event that always fires.

Fail-soft ALWAYS (exit 0, silent on any error) — a hook must never break a session.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
os.environ.setdefault("COMPANY_STORE", os.path.join(REPO, ".data", "store"))

try:
    from runtime import cc_channels as cc
    from runtime.door import compose_card
    reg = cc.register_self()
    print(compose_card(reg))     # RESOLVED live from the registries — never baked prose (Tim's check)
except Exception:  # noqa: BLE001 — fail-soft: never break a session
    pass
sys.exit(0)
