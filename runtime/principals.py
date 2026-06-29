"""runtime/principals.py — the ONE PRINCIPAL REGISTRY (identity fusion, additive + behavior-preserving).

WHAT THIS IS (and is NOT): a thin RESOLVER VIEW over the registry that already half-holds both kinds
— the per-handle reg files under `.data/channels/<handle>.json` (cc_channels' transport regs:
`tim.json`/`operator.json` sit beside the `ch-*.json` agent sessions). It is NOT a new parallel store
and NOT a directory reader of its own: it reads the SAME files cc_channels reads (CHAN_DIR), and adds
ONE thing — an explicit `kind` discriminator so a principal is legibly AGENT or VIEWER.

WHY (the keystone, verified live): humans and AI sessions already cohabit one directory. `tim.json`
(`handle:"tim"`, "operator surface", no `claude_pid`) is a VIEWER; `ch-cr4p7uxj.json` (has `pid`/
`claude_pid`/`port`) is an AGENT. The fusion formalizes the kind that fold_channels half-derives from
`claude_pid` presence (S-3 in the fusion doc), making it explicit + fail-loud rather than implicit.

THE TWO KINDS (open axis — a third kind, e.g. service/persona, is additive later; persona stays a
NOTED future sub-kind here, NOT carried as a grant-holder yet — fusion S-6 left open WITH Tim):
  • AGENT  — an AI member (a live Claude Code session: ch-* reg + self-authored profile blob).
  • VIEWER — a human who is looking (today: tim.json; outside humans via OWUI auth, later).

ALIGN WITH inc.3 (do NOT fork): session_channels.MEMBER_KINDS = (human, live-session, model) is the
per-CHANNEL membership kind (HOW a member is present in a room). This module's principal-kind is the
IDENTITY kind (WHAT a principal IS). The mapping is explicit + total:
    human                  → VIEWER
    live-session | model   → AGENT
So a channel member's kind resolves to a principal kind by the same vocabulary — one notion, two
granularities, never two parallel kind-axes.

RESOLUTION RULE (fail-loud, never silent-guess):
  1. an explicit `principal_kind` field on the reg WINS (forward-compat: a reg can declare itself).
  2. else: an AGENT signal present (`claude_pid`, or a `ch-`/`ga-` handle, or transport=="supervised"
     with a supervisor_session) → AGENT.
  3. else, a clear VIEWER signal (a human-surface reg: has a `port`+`transport=="channel"` but NO
     `claude_pid`/`pid`, e.g. the operator surface tim.json) → VIEWER.
  4. else AMBIGUOUS → returned as kind="ambiguous" with the evidence, NEVER silently bucketed.
     (operator.json — a supervised session acting FOR Tim — is the deliberately-flagged ambiguous case;
      the brief asked to flag, not silently classify it.)

This is a READ. It does not prune, write, or mutate any reg (cc_channels.live_sessions prunes dead
pids; principal resolution must be non-destructive — it answers "what kind is this principal" for
identity, not "is this session live" for transport).
"""
from __future__ import annotations

import os
import json

from runtime import cc_channels as _cc   # reuse the SAME CHAN_DIR + _read_reg (one registry, no fork)

# the principal-kind axis (open vocabulary — extends by adding values, the OWUI principal_type pattern).
KIND_AGENT = "agent"
KIND_VIEWER = "viewer"
KIND_AMBIGUOUS = "ambiguous"          # flagged, never silently bucketed (S-3 / operator.json)
PRINCIPAL_KINDS = (KIND_AGENT, KIND_VIEWER)

# inc.3 MEMBER_KINDS → principal kind (total map; the SAME vocabulary, never a parallel axis).
_MEMBER_KIND_TO_PRINCIPAL = {
    "human": KIND_VIEWER,
    "live-session": KIND_AGENT,
    "model": KIND_AGENT,
}


def member_kind_to_principal_kind(member_kind: str) -> str:
    """Map an inc.3 channel MEMBER_KIND (human|live-session|model) to a PRINCIPAL kind (viewer|agent).
    Fail-loud on an unknown member kind — never silently default (a new member kind must declare its
    principal mapping here, registry-is-truth)."""
    k = _MEMBER_KIND_TO_PRINCIPAL.get(member_kind)
    if k is None:
        raise ValueError(
            f"member_kind_to_principal_kind: unknown member kind {member_kind!r} — the inc.3 vocabulary "
            f"is {list(_MEMBER_KIND_TO_PRINCIPAL)} (session_channels.MEMBER_KINDS). A new member kind "
            f"must declare its principal mapping HERE (one notion, not a parallel kind-axis).")
    return k


def resolve_kind(reg: dict) -> dict:
    """Resolve ONE reg dict to its principal kind + the evidence. Returns
    {handle, kind, kind_source, evidence}. NEVER raises on a well-formed reg (an ambiguous reg is
    answered kind='ambiguous', not an error — the caller decides; honest, never silent)."""
    if not isinstance(reg, dict):
        raise ValueError("resolve_kind: reg must be a dict (a per-handle .data/channels reg).")
    handle = reg.get("handle")
    # (1) explicit declaration wins (forward-compat).
    explicit = reg.get("principal_kind")
    if explicit in PRINCIPAL_KINDS:
        return {"handle": handle, "kind": explicit, "kind_source": "explicit",
                "evidence": {"principal_kind": explicit}}
    if explicit is not None:
        raise ValueError(
            f"resolve_kind: reg {handle!r} declares principal_kind={explicit!r}, not in "
            f"{list(PRINCIPAL_KINDS)} — fail loud (a typo'd kind must not silently fall through).")
    # (2) AGENT signals.
    has_claude_pid = reg.get("claude_pid") is not None
    h = handle or ""
    handle_is_session = isinstance(h, str) and (h.startswith("ch-") or h.startswith("ga-"))
    supervised_session = (reg.get("transport") == "supervised") and bool(reg.get("supervisor_session"))
    agent_signals = {"claude_pid": has_claude_pid, "session_handle": handle_is_session,
                     "supervised_session": supervised_session}
    # (3) VIEWER signal: a human surface — channel transport with a port but no claude_pid and not a
    #     session-shaped handle (tim.json: handle="tim", port set, transport=="channel", no claude_pid).
    transport = _cc._transport_of(reg)   # back-compat "channel" default — the SAME rule cc_channels uses
    viewer_signal = (not has_claude_pid and not handle_is_session and transport == "channel"
                     and ("port" in reg))

    if has_claude_pid or handle_is_session:
        return {"handle": handle, "kind": KIND_AGENT, "kind_source": "derived",
                "evidence": agent_signals}
    if supervised_session:
        # a supervised session acting FOR a human (operator.json) — AGENT-ish in mechanism but standing
        # in for a viewer. DELIBERATELY AMBIGUOUS (the brief: flag operator.json, don't classify it).
        return {"handle": handle, "kind": KIND_AMBIGUOUS, "kind_source": "flagged",
                "evidence": {**agent_signals,
                             "note": "supervised session acting for a human — viewer-vs-agent is the "
                                     "open S-3/S-6 relation; declare principal_kind to resolve."}}
    if viewer_signal:
        return {"handle": handle, "kind": KIND_VIEWER, "kind_source": "derived",
                "evidence": {"human_surface": True, "transport": transport,
                             "no_claude_pid": True}}
    # (4) nothing decisive — honest ambiguity, never a silent bucket.
    return {"handle": handle, "kind": KIND_AMBIGUOUS, "kind_source": "undetermined",
            "evidence": {**agent_signals, "transport": transport,
                         "note": "no decisive AGENT or VIEWER signal — declare principal_kind to resolve."}}


def resolve_handle(handle: str, *, chan_dir: str | None = None) -> dict:
    """Resolve the principal kind for a handle by reading its reg file from CHAN_DIR (non-destructive;
    uses cc_channels._read_reg — the SAME loader, one registry). Fail-loud on a missing reg (never
    fabricate a principal). `chan_dir` overridable for tests."""
    d = chan_dir or _cc.CHAN_DIR
    path = os.path.join(d, f"{handle}.json")
    reg = _cc._read_reg(path)
    if reg is None:
        raise ValueError(
            f"resolve_handle: no reg for {handle!r} at {path!r} — not in the channel registry "
            f"(.data/channels). list via principals.list_principals(); fail loud, never fabricate.")
    return resolve_kind(reg)


def list_principals(*, chan_dir: str | None = None) -> list[dict]:
    """Every principal in the registry, with its resolved kind — a READ-ONLY fold over the per-handle
    reg files (NON-DESTRUCTIVE: unlike cc_channels.live_sessions it never prunes a dead pid; identity
    resolution must not delete transport state). `_`-prefixed files (mail/threads leaves) are skipped,
    mirroring cc_channels' own scan."""
    d = chan_dir or _cc.CHAN_DIR
    out = []
    if not os.path.isdir(d):
        return out
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".json") or fn.startswith("_"):
            continue
        reg = _cc._read_reg(os.path.join(d, fn))
        if not reg:
            continue
        out.append(resolve_kind(reg))
    return out
