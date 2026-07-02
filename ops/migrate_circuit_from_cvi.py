#!/usr/bin/env python3
"""ops/migrate_circuit_from_cvi.py — ④ L5-CIRCUIT stage 3 (C5.3): the historical POUR.

107 intents / 31 proposals / 18 approvals land from cvi_mine (the IMMUTABLE source-of-record — read-only
SELECTs only; row-count fingerprint asserted identical before/after) into the circuit's mark-composed
world (CIRCUIT.md §4 "Data landing … translation into synthesized marks, healing on arrival"):

  · 107 intents → intent://global/<uuid> addresses; each row lands as marks through the ONE API
    (container.mark, per-root ns='' — the canonical store):
      – the row itself        → an `intent_created` mark (ts = created_at; the immutable row-of-record;
                                status_at_pour carries what the mutated column CLAIMED — provenance,
                                never authority).
      – started_at (84)       → a SYNTHESIZED `intent_claim` with a ZERO-LENGTH lease
                                (lease_until == started_at): honest — liveness was never proven, so
                                every un-terminated claim composes to LAPSED the instant it lands.
                                **The 73 stuck-"running" rows land exactly this way and are VERIFIED to
                                compose to LAPSED on arrival — history stops lying with zero destructive
                                edits, and NO reaper process exists.**
      – terminal statuses (16)→ `intent_terminal` marks (outcome = succeeded|failed; ts = completed_at,
                                or fallback started_at/created_at WITH an honesty note — 5 rows).
      – wizard_state (6)      → `intent_suspend` marks (at_step = current_step, awaiting names the wizard
                                template) — pendings stay re-claimable.
  · 31 proposals → SURFACED ITEMS in the ONE inbox (runtime/governance.Inbox's shape, store.save_surfaced
    — NO parallel queue): id = prop-<uuid> (identity preserved), action = the verbatim proposal_type
    (posture() maps an undeclared class to CONFIRM — safest, honest), payload carries A's full envelope
    (preview / bounded_effects / execution_intent / idempotency_key / correlation_id / delivery_style),
    default = 'reject' (CONFIRM default), delivered_at → status='presented', approved → resolved='approve'
    (the audit lane), pending → resolved=None (live escalations, surfaced as a batch — the deadline law
    C5.6 governs them from here).
  · 18 approvals → `decision_take` marks on their proposal://global/<uuid> addresses ({by, ts, value,
    edited_params?, reason?}) — the approvals table survives as a VIEW over take marks; the 1:1 join is
    verified to reproduce (18 takes on 18 distinct proposal addresses). The 1 proposal approved in the
    mutated column with NO approvals row gets NO take (never fabricate an approval) — noted with reason.

RECONCILIATION WITH DENOMINATORS (source → landed → excluded-with-reason, sums must CLOSE or the pour
RAISES) printed AND folded into .build-container/lanes/L5-CIRCUIT.report.json (the ④ lane-report shape).

LAWS: cvi_mine NEVER mutated (this file contains no INSERT/UPDATE/DELETE against it; fingerprint asserted)
· idempotent (an already-landed uuid is skipped, counted, never re-appended) · fail-loud with breadcrumbs
· reuse-never-fork (marks ride the ONE API; proposals ride the ONE inbox shape; takes ride the registered
decision_take vocabulary) · vocabulary=files (mark_types/), data=DB (container.mark).

Run:  .venv/bin/python ops/migrate_circuit_from_cvi.py            # pour + verify + reconcile + report
      .venv/bin/python ops/migrate_circuit_from_cvi.py --verify   # re-compose + reconcile only (no writes)
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from store.fs_store import FsStore                                     # noqa: E402
from runtime import circuit                                            # noqa: E402

# one convention with ops/migrate_board_from_cvi.py / migrate_container_from_cvi.py (env-overridable)
PGCONF = {"host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
          "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
          "user": os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"),
          "db": os.environ.get("COMPANY_LEDGER_PGDB", "postgres"),
          "pw": os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres")}
CVI_DB = os.environ.get("COMPANY_CVI_DB", "cvi_mine")     # the immutable source-of-record (READ-ONLY)
REPORT = os.path.join(REPO, ".build-container", "lanes", "L5-CIRCUIT.report.json")


def _psql(db: str, sql: str) -> str:
    env = {**os.environ, "PGPASSWORD": PGCONF["pw"]}
    r = subprocess.run(["psql", "-h", PGCONF["host"], "-p", PGCONF["port"], "-U", PGCONF["user"],
                        "-d", db, "-v", "ON_ERROR_STOP=1", "-tA", "-c", sql],
                       capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"psql({db}) failed: {r.stderr.strip()[:400]}\nSQL head: {sql[:160]}")
    return r.stdout


def _json_rows(db: str, sql: str) -> list[dict]:
    out = _psql(db, f"select coalesce(json_agg(t), '[]'::json) from ({sql}) t")
    return json.loads(out.strip() or "[]")


def _fingerprint() -> str:
    """cvi_mine's circuit-table row counts — the immutability witness."""
    return _psql(CVI_DB, "select (select count(*) from intents) || '|' || "
                         "(select count(*) from proposals) || '|' || (select count(*) from approvals)"
                 ).strip()


# ── the pour ─────────────────────────────────────────────────────────────────────────────────────────


def pour_intents(store) -> dict:
    """107 intents → intent://global/<uuid> mark threads. Idempotent by intent_created/source_uuid."""
    rows = _json_rows(CVI_DB, "select intent_id, intent_type, user_id, actor_id, space_id, source, "
                              "correlation_id, run_id, thread_id, status, required_autonomy, "
                              "input_params, result, error, created_at, started_at, completed_at, "
                              "wizard_state from intents order by created_at")
    rep = {"source": len(rows), "landed_new": 0, "landed_already": 0, "excluded": [],
           "marks": {"intent_created": 0, "intent_claim": 0, "intent_terminal": 0, "intent_suspend": 0},
           "terminal_ts_fallback": 0}
    for r in rows:
        target = f"intent://global/{r['intent_id']}"
        existing = store.marks_for(target)
        if any(m.get("mark_type") == "intent_created" and m.get("source_uuid") == r["intent_id"]
               for m in existing):
            rep["landed_already"] += 1
            # count the ALREADY-LANDED cvi marks so a re-run's report still states the landed reality
            # (idempotency must not erase the denominators).
            for m in existing:
                mt = m.get("mark_type")
                if m.get("source_system") == "cvi_mine" and mt in rep["marks"]:
                    rep["marks"][mt] += 1
                    if mt == "intent_terminal" and m.get("ts_note"):
                        rep["terminal_ts_fallback"] += 1
            continue
        # 1 · the immutable row-of-record (birth mark; ts = created_at)
        store.append_mark({
            "target": target, "mark_type": "intent_created", "ts": r["created_at"],
            "intent_type": r["intent_type"], "by": r["actor_id"], "user_id": r["user_id"],
            "space_id": r.get("space_id"), "required_autonomy": r["required_autonomy"],
            "input_params": r.get("input_params"), "correlation_id": r.get("correlation_id"),
            "thread": f"thread://{r['correlation_id']}" if r.get("correlation_id") else None,
            "source": r.get("source"), "status_at_pour": r["status"],
            "source_system": "cvi_mine", "source_uuid": r["intent_id"]})
        rep["marks"]["intent_created"] += 1
        # 2 · started_at → SYNTHESIZED claim, ZERO-LENGTH lease (liveness never proven)
        if r.get("started_at"):
            session = (r.get("thread_id") or (f"run://{r['run_id']}" if r.get("run_id")
                                              else "run://cvi/unrecorded"))
            circuit.claim_intent(
                store, target, by=r["actor_id"], session=session,
                lease_until=r["started_at"], ts=r["started_at"],
                synthesized=True, note="zero-length lease — liveness never proven (the pour's honesty)",
                source_system="cvi_mine", source_uuid=r["intent_id"])
            rep["marks"]["intent_claim"] += 1
        # 3 · wizard_state → suspend (pendings stay re-claimable)
        if r.get("wizard_state"):
            w = r["wizard_state"] if isinstance(r["wizard_state"], dict) else {}
            circuit.suspend_intent(
                store, target, at_step=w.get("current_step"),
                awaiting=f"wizard input (template {w.get('template_name') or 'unrecorded'}, "
                         f"step {w.get('current_step')})",
                ts=r["created_at"], synthesized=True,
                source_system="cvi_mine", source_uuid=r["intent_id"])
            rep["marks"]["intent_suspend"] += 1
        # 4 · terminal statuses → terminal marks (ts = completed_at, honest fallback if absent)
        if r["status"] in circuit.TERMINAL_OUTCOMES:
            ts = r.get("completed_at")
            extra = {}
            if not ts:
                ts = r.get("started_at") or r["created_at"]
                extra["ts_note"] = ("completed_at was NULL in cvi_mine — ts falls back to "
                                    + ("started_at" if r.get("started_at") else "created_at")
                                    + " (honest approximation, flagged)")
                rep["terminal_ts_fallback"] += 1
            circuit.terminate(store, target, outcome=r["status"],
                              result=r.get("result") or r.get("error"), ts=ts,
                              source_system="cvi_mine", source_uuid=r["intent_id"], **extra)
            rep["marks"]["intent_terminal"] += 1
        rep["landed_new"] += 1
    return rep


def pour_proposals(store) -> dict:
    """31 proposals → surfaced items in the ONE inbox (identity preserved: id = prop-<uuid>)."""
    rows = _json_rows(CVI_DB, "select proposal_id, intent_id, proposal_type, preview, bounded_effects, "
                              "execution_intent, idempotency_key, delivery_style, status, approved_by, "
                              "approved_at, denied_reason, expires_at, correlation_id, created_at, "
                              "edited_params, delivered_at from proposals order by created_at")
    rep = {"source": len(rows), "landed_new": 0, "landed_already": 0, "excluded": [],
           "resolved_approve": 0, "live_pending": 0, "presented": 0,
           "approved_without_approval_row": []}
    for r in rows:
        sid = f"prop-{r['proposal_id']}"
        if store.get_surfaced(sid) is not None:
            rep["landed_already"] += 1
            continue
        addr = f"proposal://global/{r['proposal_id']}"
        rec = {
            "id": sid,
            "action": r["proposal_type"],          # verbatim source vocabulary; posture(unknown)→CONFIRM
            "payload": {"address": addr, "preview": r.get("preview"),
                        "bounded_effects": r.get("bounded_effects"),
                        "execution_intent": r.get("execution_intent"),
                        "idempotency_key": r.get("idempotency_key"),
                        "correlation_id": r.get("correlation_id"),
                        "intent": f"intent://global/{r['intent_id']}" if r.get("intent_id") else None,
                        "delivery_style": r.get("delivery_style"),
                        "created_at": r.get("created_at"),
                        "edited_params": r.get("edited_params"),
                        "denied_reason": r.get("denied_reason")},
            "default": "reject",                   # CONFIRM-class default (deny-by-default; C5.6's law)
            "resolved": "approve" if r["status"] == "approved" else None,
            "status": "presented" if r.get("delivered_at") else "inbox",
            "origin": "responsive",
            "source_system": "cvi_mine",
        }
        if r.get("expires_at"):
            rec["deadline"] = r["expires_at"]      # none in the historical data (verified 0) — kept for shape
        with store.surfaced_lock():
            store.save_surfaced(rec)
        rep["landed_new"] += 1
    # the lane split is counted over the LANDED reality (all prop-* items), so a re-run's report
    # still states the truth instead of zeros (idempotency must not erase the denominators).
    for d in store.list_surfaced():
        if not str(d.get("id", "")).startswith("prop-") or d.get("source_system") != "cvi_mine":
            continue
        if d.get("resolved") == "approve":
            rep["resolved_approve"] += 1
        else:
            rep["live_pending"] += 1
        if d.get("status") == "presented":
            rep["presented"] += 1
    return rep


def pour_approvals(store) -> dict:
    """18 approvals → decision_take marks on their proposal addresses (the table becomes the VIEW)."""
    rows = _json_rows(CVI_DB, "select approval_id, proposal_id, decision, decided_by, decided_at, "
                              "decision_note, edited_params, correlation_id from approvals "
                              "order by decided_at")
    rep = {"source": len(rows), "landed_new": 0, "landed_already": 0, "excluded": []}
    for r in rows:
        addr = f"proposal://global/{r['proposal_id']}"
        if any(m.get("mark_type") == "decision_take" and m.get("source_uuid") == r["approval_id"]
               for m in store.marks_for(addr)):
            rep["landed_already"] += 1
            continue
        circuit.take_on_proposal(
            store, addr, value=r["decision"], by=r["decided_by"], ts=r["decided_at"],
            reason=r.get("decision_note"), edited_params=r.get("edited_params"),
            correlation_id=r.get("correlation_id"),
            source_system="cvi_mine", source_uuid=r["approval_id"])
        rep["landed_new"] += 1
    return rep


# ── verify on arrival + reconcile ────────────────────────────────────────────────────────────────────


def verify(store) -> dict:
    """Compose EVERY poured intent's state on arrival + reproduce the take-mark view. The healing proof:
    every source-'running' row must compose to LAPSED (no reaper is running — the state is derived)."""
    intents = _json_rows(CVI_DB, "select intent_id, status from intents")
    now = datetime.now(timezone.utc)
    composed: dict[str, list] = {}
    mismatch = []
    for r in intents:
        target = f"intent://global/{r['intent_id']}"
        st = circuit.compose_from_store(store, target, now=now)["state"]
        composed.setdefault(st, []).append(r["intent_id"])
        if r["status"] == "running" and st != "lapsed":
            mismatch.append((r["intent_id"], r["status"], st))
    if mismatch:
        raise RuntimeError(f"HEALING FAILED: {len(mismatch)} source-'running' intents did NOT compose to "
                           f"LAPSED: {mismatch[:5]} — the zombie-killer bar (C5.2/C5.3) is broken. Fail loud.")
    running_src = sum(1 for r in intents if r["status"] == "running")

    # the take-mark VIEW: one take per approved proposal (the 1:1 join reproduced)
    props = _json_rows(CVI_DB, "select proposal_id, status from proposals")
    take_view = []
    approved_no_take = []
    for p in props:
        addr = f"proposal://global/{p['proposal_id']}"
        takes = [m for m in store.marks_for(addr)
                 if m.get("mark_type") == "decision_take" and m.get("source_system") == "cvi_mine"]
        if takes:
            take_view.append({"proposal": addr, "takes": len(takes)})
        elif p["status"] == "approved":
            approved_no_take.append(p["proposal_id"])
    return {"composed_counts": {k: len(v) for k, v in sorted(composed.items())},
            "running_in_source": running_src,
            "lapsed_composed": len(composed.get("lapsed", [])),
            "zombies_healed": f"{running_src} source-'running' → {running_src} LAPSED on arrival "
                              "(derived; no reaper process)",
            "take_view_proposals": len(take_view),
            "takes_are_1to1": all(t["takes"] == 1 for t in take_view),
            "approved_without_approval_row": approved_no_take}


def reconcile(rep_i: dict, rep_p: dict, rep_a: dict, ver: dict, fp_before: str, fp_after: str) -> dict:
    """Denominators that CLOSE, or raise."""
    for name, rep in (("intents", rep_i), ("proposals", rep_p), ("approvals", rep_a)):
        landed = rep["landed_new"] + rep["landed_already"]
        if rep["source"] != landed + len(rep["excluded"]):
            raise RuntimeError(f"RECONCILIATION does not close for {name}: source {rep['source']} != "
                               f"landed {landed} + excluded {len(rep['excluded'])}. Fail loud.")
    if fp_before != fp_after:
        raise RuntimeError(f"cvi_mine MUTATED ({fp_before} → {fp_after}) — INVARIANT BROKEN. Fail loud.")
    return {
        "intents": f"{rep_i['source']} = {rep_i['landed_new'] + rep_i['landed_already']} landed "
                   f"({rep_i['landed_already']} already) + {len(rep_i['excluded'])} excluded",
        "intent_marks": rep_i["marks"],
        "terminal_ts_fallback": f"{rep_i['terminal_ts_fallback']} terminal marks carry a ts fallback note "
                                "(completed_at NULL in source — honest approximation, flagged on the mark)",
        "proposals": f"{rep_p['source']} = {rep_p['landed_new'] + rep_p['landed_already']} landed "
                     f"({rep_p['landed_already']} already) + {len(rep_p['excluded'])} excluded "
                     f"[{rep_p['resolved_approve']} resolved-approve (audit lane) + "
                     f"{rep_p['live_pending']} live-pending; {rep_p['presented']} presented "
                     "(delivered_at → status)]",
        "approvals": f"{rep_a['source']} = {rep_a['landed_new'] + rep_a['landed_already']} landed "
                     f"({rep_a['landed_already']} already) + {len(rep_a['excluded'])} excluded",
        "composed_on_arrival": ver["composed_counts"],
        "zombies": ver["zombies_healed"],
        "take_view": f"{ver['take_view_proposals']} proposals carry exactly-one cvi take mark "
                     f"(1:1 join reproduced: {ver['takes_are_1to1']}); "
                     f"approved-without-approvals-row: {ver['approved_without_approval_row']} "
                     "(no take synthesized — never fabricate an approval; resolved='approve' carried "
                     "from the proposal row itself, provenance-only)",
        "cvi_mine_fingerprint": f"{fp_before} == {fp_after} (immutable — never mutated)",
    }


def write_report(recon: dict, verify_only: bool) -> None:
    """Fold the reconciliation into the ④ lane report (create-or-update, the L1/L6 shape)."""
    rep = {}
    if os.path.exists(REPORT):
        with open(REPORT) as f:
            rep = json.load(f)
    rep.setdefault("lane", "L5-CIRCUIT")
    rep.setdefault("criteria", {})
    rep["criteria"].setdefault("C5.2", "compose_state + lifecycle mark rows — tests/circuit_compose_acceptance.py 41 checks green")
    rep["criteria"]["C5.3"] = ("historical pour 107/31/18 landed + reconciled with denominators; the "
                               "source-'running' rows compose to LAPSED on arrival (verified by the pour "
                               "itself — it RAISES otherwise)")
    rep["reconciliation"] = recon
    rep["pour"] = {"script": "ops/migrate_circuit_from_cvi.py",
                   "ran_at": datetime.now(timezone.utc).isoformat(),
                   "mode": "verify-only" if verify_only else "pour+verify",
                   "idempotent": "re-run lands 0 new (already-landed uuids skipped, counted)"}
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w") as f:
        json.dump(rep, f, indent=2)
    print(f"report → {REPORT}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true", help="re-compose + reconcile only (no writes)")
    args = ap.parse_args()

    if os.environ.get("COMPANY_TEST_RUN"):
        raise RuntimeError("COMPANY_TEST_RUN is set — the pour writes REAL history into the canonical "
                           "store; a test-tagged pour would be filtered out of the operator's lanes. "
                           "Unset it (tests use their own temp roots). Fail loud.")
    store = FsStore(os.path.join(REPO, ".data", "store"))   # the canonical root (ns='')
    fp_before = _fingerprint()

    if args.verify:
        ver = verify(store)
        print(json.dumps(ver, indent=2))
        fp_after = _fingerprint()
        if fp_before != fp_after:
            raise RuntimeError(f"cvi_mine MUTATED during verify ({fp_before} → {fp_after}). Fail loud.")
        return

    rep_i = pour_intents(store)
    rep_p = pour_proposals(store)
    rep_a = pour_approvals(store)
    ver = verify(store)
    fp_after = _fingerprint()
    recon = reconcile(rep_i, rep_p, rep_a, ver, fp_before, fp_after)

    print("LANDING RECONCILIATION (cvi_mine → the circuit: marks + the ONE inbox)")
    for k, v in recon.items():
        print(f"  {k}: {json.dumps(v) if isinstance(v, (dict, list)) else v}")
    write_report(recon, verify_only=False)


if __name__ == "__main__":
    main()
