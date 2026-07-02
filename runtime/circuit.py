"""runtime/circuit.py — the CIRCUIT's state fold + lifecycle writers (④ L5-CIRCUIT, stages 2+4).

THE REBUILT ONE (build-prep/the-one-system/organ-studies/CIRCUIT.md §4): every circuit object is an
immutable, addressed row; every state transition a typed, attributed, timestamped MARK; every "status" a
FOLD over marks — INCLUDING OVER THE CLOCK. A mutated status column can lie forever; a composed state
cannot.

  compose_state(target, marks, now) → pending | running | suspended | lapsed | terminal
    · no claim (and no suspend)                        → pending
    · claim with now <= effective lease                → running   (heartbeats EXTEND the lease)
    · suspend newer than the latest claim              → suspended (deliberately parked; no lapse while parked)
    · terminal                                         → terminal  (WINS over everything, incl. the clock)
    · claim with now > effective lease and NO terminal → LAPSED    — DERIVED. There is NO reaper process:
      the zombie-killer is the clock IN the fold. The 73 historical stuck-"running" rows compose to LAPSED
      the instant they land, with zero destructive edits (C5.2/C5.3).

Writers (claim_intent / heartbeat / suspend_intent / terminate) write marks through the ONE API
(FsStore.append_mark → store/pg_marks.py → container.mark, migration 0021) and FAIL LOUD on grammar:
claim-on-terminal, claim-over-a-live-lease held by another, heartbeat-without-running, double-terminal,
unknown outcome — each refusal names what it expected (breadcrumbs, never a silent no-op).

Stage 4 (C5.4/C5.5/C5.6) rides the SAME module:
  · take/retract on a proposal address — retractable UNTIL an intent_claim `references_take`s it (C5.4);
  · release(inbox, sid) — READS the operator's resolve, never writes it (the executor's lane cannot
    release its own gate — C5.5);
  · sweep_deadlines(store, now) — SURFACE-class past deadline proceeds-by-default with a recorded note;
    CONFIRM-class escalates, resolved stays None until the operator (C5.6).

REUSE-NEVER-FORK: marks ride the ONE mark API; proposals are surfaced items in the ONE inbox
(runtime/governance.Inbox — no parallel queue); takes are `decision_take` marks (mark_types/decision_take
— the approvals table survives only as a VIEW over take marks); retract reuses `decision_retract`.
The vocabulary is files (mark_types/intent_claim|intent_heartbeat|intent_suspend|intent_terminal); the
data is DB (container.mark).
"""
from __future__ import annotations

from datetime import datetime, timezone

INTENT_MARKS = ("intent_claim", "intent_heartbeat", "intent_suspend", "intent_terminal")
TERMINAL_OUTCOMES = ("succeeded", "failed", "cancelled")
STATES = ("pending", "running", "suspended", "lapsed", "terminal")


class CircuitError(RuntimeError):
    """A circuit grammar violation (claim-on-terminal, heartbeat-without-claim, double-terminal, …) —
    fail loud with the breadcrumb; never a silent no-op that lets a status lie."""


# ── time ─────────────────────────────────────────────────────────────────────────────────────────────


def _now(now=None) -> datetime:
    """Normalize `now` (None → the wall clock; ISO string or datetime accepted) to an aware UTC datetime.
    THE CLOCK IN THE FOLD is a parameter, so every state is reproducible at any instant (and testable)."""
    if now is None:
        return datetime.now(timezone.utc)
    if isinstance(now, datetime):
        return now if now.tzinfo else now.replace(tzinfo=timezone.utc)
    if isinstance(now, str):
        return _parse_ts(now, field="now")
    raise CircuitError(f"circuit: `now` must be None, datetime, or ISO string — got {type(now).__name__}. "
                       "Fail loud, never guess the clock.")


def _parse_ts(v, *, field: str) -> datetime:
    """Parse an ISO timestamp FAIL-LOUD (a malformed lease/ts would make the fold silently wrong —
    the exact lie the circuit exists to kill)."""
    if isinstance(v, datetime):
        return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
    if not isinstance(v, str) or not v.strip():
        raise CircuitError(f"circuit: `{field}` must be an ISO timestamp string, got {v!r} — fail loud "
                           f"(a mark with an unreadable {field} would compose to a silent lie).")
    try:
        d = datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError as e:
        raise CircuitError(f"circuit: `{field}` {v!r} is not ISO-parseable ({e}) — fail loud.") from e
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _iso(d: datetime) -> str:
    return d.astimezone(timezone.utc).isoformat()


# ── THE FOLD (C5.2) ──────────────────────────────────────────────────────────────────────────────────


def compose_state(target: str, marks: list, now=None) -> dict:
    """PURE: fold an intent's lifecycle marks + THE CLOCK → the composed state. No store, no side
    effects, NO reaper — "lapsed" is what an expired lease with no terminal IS, not what a process
    stamped. Returns a legible dict:
      {target, state, outcome?, result?, claim?, lease_until?, suspended?{at_step, awaiting}, at, events}
    Mechanics (CIRCUIT.md §4):
      terminal → terminal (wins over everything) · no claim/suspend → pending · suspend newer than the
      latest claim → suspended · else claim: now <= effective lease (claim's lease_until extended by the
      max heartbeat lease after it) → running, past it → LAPSED. Non-lifecycle marks are ignored (the
      thread may carry comments etc. — additive)."""
    nw = _now(now)
    events = sorted([m for m in (marks or []) if isinstance(m, dict) and m.get("mark_type") in INTENT_MARKS],
                    key=lambda m: str(m.get("ts") or ""))
    base = {"target": target, "at": _iso(nw), "events": len(events)}

    terminals = [m for m in events if m["mark_type"] == "intent_terminal"]
    if terminals:
        t = terminals[-1]
        return {**base, "state": "terminal", "outcome": t.get("outcome") or t.get("value"),
                "result": t.get("result"), "terminal_ts": t.get("ts")}

    claims = [m for m in events if m["mark_type"] == "intent_claim"]
    suspends = [m for m in events if m["mark_type"] == "intent_suspend"]
    if not claims and not suspends:
        return {**base, "state": "pending"}

    last_claim = claims[-1] if claims else None
    last_suspend = suspends[-1] if suspends else None
    if last_suspend is not None and (last_claim is None
                                     or str(last_suspend.get("ts")) > str(last_claim.get("ts"))):
        return {**base, "state": "suspended",
                "suspended": {"at_step": last_suspend.get("at_step"),
                              "awaiting": last_suspend.get("awaiting")},
                "suspend_ts": last_suspend.get("ts")}

    # the live claim: effective lease = the claim's lease, extended by heartbeats written AFTER it.
    lease = _parse_ts(last_claim.get("lease_until"), field="lease_until")
    for hb in (m for m in events if m["mark_type"] == "intent_heartbeat"
               and str(m.get("ts")) >= str(last_claim.get("ts"))):
        hb_lease = _parse_ts(hb.get("lease_until"), field="lease_until")
        if hb_lease > lease:
            lease = hb_lease
    claim_view = {"by": last_claim.get("by"), "session": last_claim.get("session"),
                  "ts": last_claim.get("ts")}
    if last_claim.get("references_take"):
        claim_view["references_take"] = last_claim.get("references_take")
    state = "running" if nw <= lease else "lapsed"        # THE CLOCK IN THE FOLD — no reaper, ever
    return {**base, "state": state, "claim": claim_view, "lease_until": _iso(lease)}


def compose_from_store(store, target: str, now=None) -> dict:
    """compose_state over the target's live mark thread (the ONE API read)."""
    return compose_state(target, store.marks_for(target), now=now)


# ── writers (C5.2) — marks through the ONE API, fail-loud grammar ────────────────────────────────────


def _require_intent_target(target) -> str:
    if not isinstance(target, str) or not target.startswith("intent://"):
        raise CircuitError(f"circuit: target must be an intent:// address, got {target!r} — the circuit's "
                           "lifecycle marks live on intent addresses (CIRCUIT.md §4). Fail loud.")
    return target


def claim_intent(store, target: str, *, by: str, session: str, lease_until=None, lease_seconds=None,
                 now=None, references_take: str | None = None, ts=None, **extra) -> dict:
    """CLAIM an intent to run: write the intent_claim mark {by, session, lease_until[, references_take]}.
    Grammar (fail-loud): target is intent:// · by/session non-empty · exactly one of lease_until /
    lease_seconds · REFUSED on a terminal intent (ends end once) · REFUSED while another live claim runs
    (now <= its lease; a LAPSED intent is re-claimable — that IS the recovery path, no reaper needed).
    `ts` (pour only) back-dates the mark; `references_take` records the authorizing take's proposal
    address (C5.4 — freezes that take's retract window)."""
    _require_intent_target(target)
    if not isinstance(by, str) or not by.strip():
        raise CircuitError("circuit.claim_intent: `by` (the claiming principal) must be a non-empty "
                           "string — an unattributed claim is a liveness assertion nobody made. Fail loud.")
    if not isinstance(session, str) or not session.strip():
        raise CircuitError("circuit.claim_intent: `session` (the live execution handle — session:// or "
                           "run://) must be a non-empty string — a claim with no handle can't be found "
                           "alive or dead. Fail loud.")
    nw = _now(now)
    if (lease_until is None) == (lease_seconds is None):
        raise CircuitError("circuit.claim_intent: give exactly ONE of `lease_until` (ISO) or "
                           "`lease_seconds` — the lease is the whole zombie-killer; a claim without one "
                           "(or with two) is malformed. Fail loud.")
    lu = _parse_ts(lease_until, field="lease_until") if lease_until is not None else \
        datetime.fromtimestamp(nw.timestamp() + float(lease_seconds), tz=timezone.utc)

    cur = compose_state(target, store.marks_for(target), now=nw)
    if cur["state"] == "terminal":
        raise CircuitError(f"circuit.claim_intent: {target} is TERMINAL ({cur.get('outcome')}) — a "
                           "terminal intent is never re-claimed (fork a NEW intent instead; REWIND = "
                           "fork + fresh claim, CIRCUIT.md §4). Fail loud.")
    if cur["state"] == "running":
        c = cur.get("claim") or {}
        raise CircuitError(f"circuit.claim_intent: {target} is RUNNING under a live lease "
                           f"(by={c.get('by')!r} session={c.get('session')!r} lease_until="
                           f"{cur.get('lease_until')}) — wait for the lease to lapse or for a terminal; "
                           "a second live claim would double-execute. Fail loud.")
    rec = {"target": target, "mark_type": "intent_claim", "by": by, "session": session,
           "lease_until": _iso(lu), **extra}
    if references_take:
        rec["references_take"] = references_take
    if ts is not None:                                   # the pour back-dates; live writes never pass ts
        rec["ts"] = ts if isinstance(ts, str) else _iso(_parse_ts(ts, field="ts"))
    return store.append_mark(rec)


def heartbeat(store, target: str, *, lease_until, now=None, **extra) -> dict:
    """EXTEND the live claim's lease (liveness re-asserted). REFUSED unless the intent currently composes
    to RUNNING — a lapsed/unclaimed/suspended/terminal intent cannot be heartbeat back to life (the
    lapsed executor RE-CLAIMS; that refusal is what makes a dead executor unable to lie)."""
    _require_intent_target(target)
    nw = _now(now)
    lu = _parse_ts(lease_until, field="lease_until")
    cur = compose_state(target, store.marks_for(target), now=nw)
    if cur["state"] != "running":
        raise CircuitError(f"circuit.heartbeat: {target} composes to {cur['state'].upper()} at {_iso(nw)} "
                           "— a heartbeat is only legal on a RUNNING intent (lapsed? re-claim it; "
                           "no claim? claim it; terminal? it ended). Fail loud, never silently resurrect.")
    return store.append_mark({"target": target, "mark_type": "intent_heartbeat",
                              "lease_until": _iso(lu), **extra})


def suspend_intent(store, target: str, *, at_step, awaiting: str, now=None, ts=None, **extra) -> dict:
    """PARK the walk at a step, awaiting something (the wizard seam, generalized). REFUSED on a terminal
    intent; legal from running (the executor parks its own walk) and — for the historical pour — from
    pending (a wizard that suspended before any claim was recorded)."""
    _require_intent_target(target)
    if not isinstance(awaiting, str) or not awaiting.strip():
        raise CircuitError("circuit.suspend_intent: `awaiting` must say WHAT the walk waits on (a "
                           "non-empty string, in words) — a suspend nobody can read is a parked zombie. "
                           "Fail loud.")
    nw = _now(now)
    cur = compose_state(target, store.marks_for(target), now=nw)
    if cur["state"] == "terminal":
        raise CircuitError(f"circuit.suspend_intent: {target} is TERMINAL — nothing left to park. Fail loud.")
    rec = {"target": target, "mark_type": "intent_suspend", "at_step": at_step, "awaiting": awaiting,
           **extra}
    if ts is not None:
        rec["ts"] = ts if isinstance(ts, str) else _iso(_parse_ts(ts, field="ts"))
    return store.append_mark(rec)


def terminate(store, target: str, *, outcome: str, result=None, now=None, ts=None, **extra) -> dict:
    """END the walk: outcome ∈ succeeded|failed|cancelled (closed vocab — fail loud on anything else).
    REFUSED if already terminal (ends end once). Legal from every non-terminal state — cancelling a
    pending intent, failing a lapsed one, succeeding a running one are all real ends."""
    _require_intent_target(target)
    if outcome not in TERMINAL_OUTCOMES:
        raise CircuitError(f"circuit.terminate: unknown outcome {outcome!r} — the closed vocabulary is "
                           f"{list(TERMINAL_OUTCOMES)} (CIRCUIT.md §4). Fail loud, never invent a state.")
    cur = compose_state(target, store.marks_for(target), now=_now(now))
    if cur["state"] == "terminal":
        raise CircuitError(f"circuit.terminate: {target} is ALREADY terminal ({cur.get('outcome')} at "
                           f"{cur.get('terminal_ts')}) — ends end once; a second terminal would rewrite "
                           "history. Fail loud.")
    rec = {"target": target, "mark_type": "intent_terminal", "outcome": outcome, "value": outcome,
           "result": result, **extra}
    if ts is not None:
        rec["ts"] = ts if isinstance(ts, str) else _iso(_parse_ts(ts, field="ts"))
    return store.append_mark(rec)


# ── the take window (C5.4): approval take-marks retractable UNTIL a claim references them ────────────


def take_on_proposal(store, proposal_addr: str, *, value: str = "approve", by: str, ts=None,
                     **extra) -> dict:
    """An APPROVAL = a decision_take mark on the proposal address (CIRCUIT.md §4: "Approval = a
    decision_take mark … {by, ts, value, edited_params?, reason?}"; the approvals table survives only as
    a VIEW over these). Reuses the registered decision_take vocabulary — no new mark kind."""
    if not isinstance(proposal_addr, str) or not proposal_addr.startswith("proposal://"):
        raise CircuitError(f"circuit.take_on_proposal: expected a proposal:// address, got "
                           f"{proposal_addr!r}. Fail loud.")
    if not isinstance(by, str) or not by.strip():
        raise CircuitError("circuit.take_on_proposal: `by` must name the deciding principal — an "
                           "unattributed approval is exactly the audit hole the circuit closes. Fail loud.")
    rec = {"target": proposal_addr, "mark_type": "decision_take", "value": value, "by": by, **extra}
    if ts is not None:
        rec["ts"] = ts if isinstance(ts, str) else _iso(_parse_ts(ts, field="ts"))
    return store.append_mark(rec)


def claims_referencing(store, proposal_addr: str) -> list[dict]:
    """Every intent_claim whose `references_take` names this proposal address — the take's freeze set."""
    return [m for m in store.marks_by_type("intent_claim")
            if m.get("references_take") == proposal_addr]


def retract_take(store, proposal_addr: str, *, by: str, note: str = "", now=None) -> dict:
    """RETRACT a take on a proposal — legal ONLY while no intent_claim references it (C5.4: "retractable
    until an intent_claim references the take", refused after — once execution started on the approval's
    strength, un-approving would orphan a running effect). Appends a decision_retract (the registered
    un-decide vocabulary — audit-preserving, never a delete). Fail-loud if there is no take to retract."""
    takes = [m for m in store.marks_for(proposal_addr) if m.get("mark_type") == "decision_take"]
    if not takes:
        raise CircuitError(f"circuit.retract_take: no decision_take mark on {proposal_addr} — nothing to "
                           "retract. Fail loud, never a silent no-op.")
    refs = claims_referencing(store, proposal_addr)
    if refs:
        r = refs[0]
        raise CircuitError(f"circuit.retract_take: REFUSED — intent_claim on {r.get('target')!r} "
                           f"(by={r.get('by')!r}, ts={r.get('ts')}) references this take; the "
                           "approval-retract window closed when execution claimed it (CIRCUIT.md §4 — "
                           "retractable until an intent_claim references the take). Fail loud.")
    rec = {"target": proposal_addr, "mark_type": "decision_retract", "by": by}
    if note:
        rec["note"] = note
    return store.append_mark(rec)


# ── release (C5.5): the executor READS the operator's resolve — it can never write it ───────────────


def release(inbox, sid: str) -> dict:
    """The executor-side gate on a CONFIRM-class surfaced item: returns the item ONLY if the OPERATOR
    resolved it 'approve' (Inbox.resolve — the operator channel; kept off the executor's lane). This
    function READS `resolved`; it never writes it — the write-path split C5.5 demands (two-lane safe:
    the executor writes claim/heartbeat/terminal marks, only the operator's channel writes resolves)."""
    d = inbox.get(sid)
    if not d:
        raise CircuitError(f"circuit.release: no surfaced item {sid!r} — nothing to release. Fail loud.")
    if d.get("resolved") != "approve":
        raise CircuitError(f"circuit.release: {sid} is NOT released — resolved={d.get('resolved')!r} "
                           "(only the operator's resolve releases a CONFIRM gate; the executor's lane "
                           "cannot write it — C5.5). Fail loud, keep waiting or lapse the deadline.")
    return d


# ── deadlines (C5.6): SURFACE proceeds-by-default with a note; CONFIRM escalates ─────────────────────


def sweep_deadlines(store, now=None) -> dict:
    """Walk the ONE inbox for unresolved items carrying a `deadline` (top-level or in payload) that has
    passed, and apply the CIRCUIT's deadline law (CIRCUIT.md §4 "default+deadline"):
      · SURFACE-class (default == 'proceed') → resolved = 'proceed' + a RECORDED deadline_note (the one
        sanctioned non-operator resolve: the DECLARED default acting at its declared deadline — the
        operator set the default when the class was postured; nothing new was decided here).
      · CONFIRM-class (default == 'reject') → NEVER touches `resolved` (only the operator releases —
        C5.5); stamps escalated=True + deadline_note + status 'presented' so it lands in front of the
        operator (auto-escalates past threshold).
    Idempotent: an already-noted item is skipped. Returns {checked, proceeded, escalated, skipped}."""
    nw = _now(now)
    from runtime.governance import posture, SURFACE, CONFIRM  # the ONE policy — never a local copy
    out = {"checked": 0, "proceeded": [], "escalated": [], "skipped": 0}
    with store.surfaced_lock():
        for d in store.list_surfaced():
            payload = d.get("payload") if isinstance(d.get("payload"), dict) else {}
            dl = d.get("deadline") or payload.get("deadline")
            if not dl:
                continue
            out["checked"] += 1
            if d.get("deadline_note"):                    # already swept — idempotent
                out["skipped"] += 1
                continue
            if _parse_ts(dl, field="deadline") > nw:      # not yet due
                continue
            p = posture(d.get("action") or "")
            default = d.get("default")
            if d.get("resolved") is None and (p == SURFACE or (p != CONFIRM and default == "proceed")):
                d["resolved"] = "proceed"
                d["deadline_note"] = (f"deadline {dl} passed at {_iso(nw)} — proceeded by the DECLARED "
                                      "default (SURFACE-class: default=proceed at deadline, CIRCUIT.md §4)")
                store.save_surfaced(d)
                out["proceeded"].append(d["id"])
            elif d.get("resolved") is None:
                d["escalated"] = True
                d["status"] = "presented"
                d["deadline_note"] = (f"deadline {dl} passed at {_iso(nw)} — CONFIRM-class NEVER proceeds "
                                      "by default; ESCALATED to the operator (resolved stays None until "
                                      "the operator's resolve — C5.5/C5.6)")
                store.save_surfaced(d)
                out["escalated"].append(d["id"])
            else:
                out["skipped"] += 1                       # already resolved before the deadline
    return out
