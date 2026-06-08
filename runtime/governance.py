"""runtime/governance.py — the act-unwatched policy + surfaced-decision gate (S7/D4/D7).

Per-action-class posture on the axes reversibility · cost · externality:
  reversible+cheap+internal -> AUTO; meaningful-but-recoverable -> SURFACE (default+deadline);
  irreversible/expensive/external -> CONFIRM. Some classes are locked-to-CONFIRM forever
  (Tim: real source data, external publishing). See decisions/D4 + D7.
"""
from __future__ import annotations

AUTO, SURFACE, CONFIRM = "auto", "surface", "confirm"

POLICY = {
    # AUTO — cheap, reversible, internal
    "inspect": AUTO, "compose": AUTO, "configure": AUTO, "run": AUTO, "write_own_layer": AUTO,
    # AUTO — the decision→implementation wire (Group W). AUTO here means auto-DISPATCH on the
    # operator's approve (no second gate BEFORE building) — it does NOT mean auto-CLOSE without review.
    # A DECLARED-SCOPE, reversible (git-committed, build-gated, scope-diffed) build is the ONE class the
    # wire may auto-dispatch: the operator's approve of the declared-scope build-intent IS the
    # authorization, so the dispatch proceeds without a second gate. The pre-dispatch gate keys on
    # posture==AUTO, so ONLY this class auto-runs; ANY CONFIRM/SURFACE/LOCKED declared class surfaces
    # for the operator instead (never auto-acts — a CONFIRM class like 'destructive' that is absent from
    # LOCKED can no longer slip through a LOCKED-membership check). After the build, EVERY implemented
    # result is SURFACED FOR REVIEW (a `decision.surfaced_for_review` event + a review inbox item) —
    # AI-operated is NOT review-free; `implemented` means "done AND surfaced for review", never a silent
    # terminal. The CLOSE routes through guard("code_build") (CONFIRM), so an unverified build can never
    # reach `implemented`, and the review item is ALWAYS surfaced in the same guarded close.
    "decision_build": AUTO,
    # SURFACE — meaningful but recoverable (proceeds on default + deadline)
    "promote": SURFACE, "spend": SURFACE,
    # CONFIRM — irreversible / expensive / external
    "destructive": CONFIRM, "code_build": CONFIRM, "register_type": CONFIRM,
    "external": CONFIRM, "source_data": CONFIRM, "frozen_contract": CONFIRM,
    # CONFIRM — UI self-mod + the review queue. They already routed to CONFIRM via the
    # unknown-class default (posture() → CONFIRM); declaring them here changes NO behavior,
    # it makes the intent explicit + single-source (G1). `review` = a surfaced item the
    # operator walks/decides; only Tim resolves it (no-bypass), so CONFIRM is its posture.
    "ui_panel": CONFIRM, "ui_extension": CONFIRM, "review": CONFIRM,
}
# never graduate to AUTO, no matter the earned trust (D4/D7 forever-confirm)
LOCKED = {"source_data", "external", "frozen_contract"}


class GovernanceError(RuntimeError):
    """Raised when a CONFIRM action is attempted without confirmation (fail loud)."""


def posture(action_class: str) -> str:
    return POLICY.get(action_class, CONFIRM)        # unknown class -> safest


def guard(action_class: str, do, *, confirmed: bool = False, inbox=None, payload: dict | None = None):
    """Run `do()` per policy. AUTO: run. SURFACE: run, record a surfaced note (default = proceed).
    CONFIRM: run only if `confirmed`; else surface a gate and raise (fail loud)."""
    p = posture(action_class)
    if p == AUTO:
        return do()
    if p == SURFACE:
        if inbox is not None:
            inbox.surface(action_class, payload or {}, default="proceed", resolved="proceed")
        return do()
    # CONFIRM
    if confirmed:
        return do()
    if inbox is not None:
        inbox.surface(action_class, payload or {}, default="reject", resolved=None)
    raise GovernanceError(f"action '{action_class}' requires confirmation (CONFIRM); surfaced for the operator")


class Inbox:
    """Surfaced decisions live in the store, so both faces (UI + MCP) see the same inbox."""
    def __init__(self, store):
        self.store = store
        self._n = 0

    def _next_index(self) -> int:
        """Next id index, computed from PERSISTED decisions (not just an in-memory counter) so a
        process restart can never reuse an id and overwrite an unresolved decision (gate integrity)."""
        import re
        mx = self._n
        for d in self.store.list_surfaced():
            m = re.match(r"s(\d+)-", d.get("id", ""))
            if m:
                mx = max(mx, int(m.group(1)))
        return mx + 1

    def surface(self, action_class: str, payload: dict, default: str, resolved=None,
                status: str | None = None, origin: str | None = None) -> str:
        # T1-RACE (the CREATE path — the missing twin of set_status/resolve below): minting a surfaced
        # item is a read-modify-write on the shared surfaced store — `_next_index()` READS the persisted
        # max index, surface() MINTS `sid` from it, then `save_surfaced` WRITES the new file. Left
        # unserialized, two concurrent surfacers race it. The threaded bridge is the real source: e.g.
        # `/api/build-intent` (→ surface_build_intent → surface) racing the wire's `surface_review`
        # during a build close, or two build-intents arriving together. Both call `_next_index()`, both
        # read the same persisted max N (neither has saved yet), both mint index N+1 → (a) SAME
        # action_class collapses to ONE `sid` and the second `save_surfaced` silently OVERWRITES the
        # first — an operator-facing decision is LOST (rule 4: a silent loss is a silent failure); (b) a
        # DIFFERENT class reuses index N+1 across two distinct decisions, breaking the very id-integrity
        # `_next_index`'s docstring promises ("can never reuse an id and overwrite an unresolved
        # decision"). FIX: hold `surfaced_lock` across the whole allocate→mint→save so it is ATOMIC
        # against every other surfaced writer — the SAME store-level lock `set_status`/`resolve` already
        # take for the MUTATE path (T1-RACE was closed there but not here). Safe: `surfaced_lock` is a
        # re-entrant RLock, so callers that ALREADY hold it (the build-close RMWs in suite.py) re-acquire
        # without self-deadlock; and it is a LEAF lock (no graph_lock/dispatch_lock is ever taken under
        # it), so wrapping surface() adds no lock-ordering cycle. SCOPE of the guarantee: IN-PROCESS,
        # exactly matching set_status/resolve (no fcntl) — the threaded bridge is the dominant real
        # concurrency. Cross-process surfaced-create stays as unprotected as cross-process
        # set_status/resolve: a pre-existing store-level gap (the surfaced lock is in-process only), not
        # this fix's scope.
        with self.store.surfaced_lock():
            self._n = self._next_index()
            sid = f"s{self._n}-{action_class}"
            rec = {"id": sid, "action": action_class, "payload": payload,
                   "default": default, "resolved": resolved}
            # T3-HYGIENE (tag-at-source): the OPERATOR inbox was ~90% test/adversarial pollution because
            # test- and red-team-created surfaced items were indistinguishable from real ones, and the FE
            # filter pattern-matched titles (brittle, missed most). The DURABLE fix is a tag set AT CREATION:
            # when a run sets COMPANY_TEST_RUN, every item this surfaces carries `test_origin=True`, so the
            # inbox lanes / FE filter exclude it by a real field instead of a fragile title regex. A real
            # operator run never sets the flag, so real items are never tagged. Additive + optional: an
            # untagged item reads exactly as before. (Cross-lane: the TESTS lane / adversarial harness sets
            # COMPANY_TEST_RUN; the FE filters on `test_origin`; the verifier drives a clean operator run.)
            import os as _os
            if _os.environ.get("COMPANY_TEST_RUN"):
                rec["test_origin"] = True
            # SEPARATE lifecycle field (A): inbox→presented→responded→resolved|requeue. NEVER
            # overload `resolved` (inbox_lanes/now/is_approved key on `resolved is None`); the
            # status tracks the walk WITHOUT touching the live/escalation predicate. Additive +
            # optional, so every existing surfaced item (no status) reads exactly as before.
            if status is not None:
                rec["status"] = status
            if origin is not None:                   # responsive (came from a build need) | generative (an idea)
                rec["origin"] = origin
            self.store.save_surfaced(rec)
        return sid

    # --- the review queue (A): a review item is the SAME inbox, a new decision class ---
    # `implemented` (W4) is the code-written terminal of the decision→implementation wire: it lives
    # on the SEPARATE `status` lane (NOT the operator `resolved` field), so a build can close without
    # breaking operator-only resolve. set_status RAISES on an unknown value, so it MUST be listed here
    # before the wire can write it. The wire only writes it through a guard()ed close on the
    # verification verdict — an unverified build that reaches the close raises (W4).
    REVIEW_STATUSES = ("inbox", "presented", "responded", "resolved", "requeue", "implemented")

    def surface_review(self, item: dict, origin: str = "responsive") -> str:
        """Surface a `review` decision into the SAME inbox/surfaced store (no parallel queue).
        Carries a SEPARATE `status` (starts `inbox`) + `origin` (responsive|generative). `resolved`
        stays None so it lands in `live_escalations` until Tim resolves it — only `resolve_surfaced`
        ever writes `resolved`, so a presented/responded item is still a live escalation (A)."""
        if origin not in ("responsive", "generative"):
            raise ValueError(f"unknown review origin {origin!r} — responsive|generative")
        return self.surface("review", dict(item), default="reject",
                            resolved=None, status="inbox", origin=origin)

    def set_status(self, sid: str, status: str) -> None:
        """Advance a surfaced item's lifecycle status WITHOUT touching `resolved` (A). Fail loud
        on an unknown status or a missing item — never silently no-op."""
        if status not in self.REVIEW_STATUSES:
            raise ValueError(f"unknown review status {status!r} — one of {self.REVIEW_STATUSES}")
        # T1-RACE: serialize the whole get→mutate→save against every other surfaced writer (the
        # Suite's resolve/build_result writes, Inbox.resolve) so a status advance can't lose-update a
        # concurrently-written field (e.g. `resolved`). The store-level lock is the one both reach.
        with self.store.surfaced_lock():
            d = self.store.get_surfaced(sid)
            if not d:
                raise KeyError(sid)
            d["status"] = status
            self.store.save_surfaced(d)

    def list(self) -> list:
        return self.store.list_surfaced()

    def get(self, sid: str) -> dict | None:
        return self.store.get_surfaced(sid)

    def resolve(self, sid: str, choice: str, reason: str = "") -> None:
        """OPERATOR-only: approve/reject a surfaced decision. (Must NOT be reachable by the
        agent it gates — kept off the MCP face; only the UI/operator channel calls this.)
        `reason` captures the WHY — the trajectory that generalises, not just the endpoint (I1)."""
        # T1-RACE: serialize the whole get→mutate→save (resolved is the operator-only field; a
        # concurrent set_status must not lose-update it, nor it the status). Store-level lock.
        with self.store.surfaced_lock():
            d = self.store.get_surfaced(sid)
            if not d:
                raise KeyError(sid)
            d["resolved"] = choice
            if reason:
                d["reason"] = reason
            self.store.save_surfaced(d)

    def is_approved(self, sid: str) -> bool:
        d = self.store.get_surfaced(sid)
        return bool(d and d.get("resolved") == "approve")


# --- self-check ---------------------------------------------------------------
# In-scope durable proof of the T1-RACE create-path fix (Inbox.surface). The acceptance suites live
# under tests/ — a runtime/-scoped wire build may not touch them (the scope-diff would read it as an
# overrun) — so the teeth live here, the same convention context_variables.py uses. Inert on import;
# runs only as `./.venv/bin/python runtime/governance.py`. Proves: N threads, released together on a
# barrier, all minting surfaced items concurrently → EVERY item persists (no lost-update via an
# overwritten id) AND every index is UNIQUE (no id reuse). Before the fix (surface() unserialized) the
# shared _next_index read-modify-write races: same action_class collapses ids → fewer than N files;
# mixed classes reuse an index → a duplicate. With surfaced_lock wrapping allocate→mint→save, both hold.
if __name__ == "__main__":
    import os
    import re
    import sys
    import shutil
    import tempfile
    import threading

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from store.fs_store import FsStore

    def _hammer(n_threads: int, same_class: bool) -> tuple[int, list[int]]:
        """Fire n_threads concurrent surface() calls (released together) and return
        (distinct persisted items, the list of parsed indices)."""
        work = tempfile.mkdtemp(prefix="surface-race-")
        try:
            store = FsStore(os.path.join(work, "store"))
            inbox = Inbox(store)
            start = threading.Barrier(n_threads)
            errors: list[str] = []

            def one(k: int):
                cls = "decision_build" if same_class else f"cls{k}"
                try:
                    start.wait()                      # release all threads at the same instant → max contention
                    inbox.surface(cls, {"i": k}, default="reject")
                except Exception as e:                # a surface() must never raise under contention
                    errors.append(f"{type(e).__name__}: {e}")

            ts = [threading.Thread(target=one, args=(k,)) for k in range(n_threads)]
            for t in ts:
                t.start()
            for t in ts:
                t.join()
            assert not errors, f"surface() raised under contention: {errors[:3]}"
            items = store.list_surfaced()
            idxs = []
            for d in items:
                m = re.match(r"s(\d+)-", d.get("id", ""))
                assert m, f"malformed surfaced id {d.get('id')!r}"
                idxs.append(int(m.group(1)))
            return len(items), idxs
        finally:
            shutil.rmtree(work, ignore_errors=True)

    N = 48
    P = 0

    def ck(label, cond):
        global P
        assert cond, "FAIL: " + label
        P += 1
        print("  ok  " + label)

    # 1) SAME action_class: a lost-update would overwrite a colliding id → fewer than N files.
    count, idxs = _hammer(N, same_class=True)
    ck(f"same-class: all {N} concurrent surfaces persisted (no lost-update overwrite)", count == N)
    ck("same-class: every index unique (no id reuse)", len(set(idxs)) == N)
    ck(f"same-class: indices are exactly 1..{N}", sorted(idxs) == list(range(1, N + 1)))

    # 2) MIXED action_class: distinct filenames, so a race shows as a REUSED index, not an overwrite.
    count2, idxs2 = _hammer(N, same_class=False)
    ck(f"mixed-class: all {N} items persisted", count2 == N)
    ck("mixed-class: every index unique (no id reuse across distinct decisions)",
       len(set(idxs2)) == N)

    print(f"OK governance self-check — {P} checks; surface() create-path race closed "
          f"(in-process, matching set_status/resolve)")
