"""runtime/cc_gate.py — Heart R15: per-step GATE / ABORT / REWIND, as an OBSERVER on the native
mechanism (NOT a reimplementation, NOT a hot-path edit).

Scoped with the lead after a stop-and-flag (the scouts proved a true pre-execution pause lives in
claude's OWN CLI loop — the hot path — not here). So this is the FAITHFUL, file-disjoint cut:
  • GATE — a record that a declared step is gated. The PAUSE rides the NATIVE `blocks_execution`
    declaration (the same mechanism AskUserQuestion uses; claude's CLI enforces it). This module
    OBSERVES + records gate-state in its OWN store; it never edits session_supervisor._reader.
  • ABORT — the supervisor's existing /interrupt + /teardown (the no-orphan law). Reuse, not rebuild.
  • REWIND — session_pointintime.materialize_at_point (the native fork transform; proven via cc_clone).
    Surface-don't-rebuild.
  • The step is referenced by an OPAQUE step-ADDRESS (session://<sid>/step/<tool_use_id>) — stored
    verbatim, NEVER parsed (the board://<id> pattern). The lead's cognition.py resolver makes it
    resolve + round-trip (H1.1/H1.2); this module only needs the FORMAT. `session` is a SEPARATE
    operational field (the abort/rewind handle) — so we never parse the address for the session.

HONEST LIMIT (documented, not faked): an arbitrary enforced pre-execution pause AT ANY step is claude's
internal loop, not file-disjoint, not ours. We surface the native gate + give operator ABORT/REWIND/
record-resume around it. The full live round-trip (a real claude process gating on blocks_execution →
operator resumes → completes) needs a LIVE gated session (see ops/ probe) — the deterministic lifecycle
(gate→resume, gate→abort→interrupt+teardown, gate→rewind→materialize) is unit-verified here.

Control-types (gate/abort/rewind) are NOT frozen — a future registry row can add a 4th (annotate/branch);
the door is left open (everything-is-registry), but the registry is not built now (don't over-build).
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
import uuid as _uuid
from pathlib import Path

from store.fs_store import _atomic_write_fsync
from lifters.frontmatter import _extract as _fm_extract
from contracts.address import is_step_address, is_composition_step_address  # SHARED grammar (one parser, lead's 4b87aee/bar4)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATES_DIR = os.path.join(REPO, ".data", "gates")
SUPERVISOR = os.environ.get("COMPANY_SUPERVISOR_BASE", "http://127.0.0.1:8771")
# step-address validation rides the SHARED grammar (contracts.address.is_step_address) — ONE parser,
# not a local regex (retired STEP_ADDR_RE per f1ade750's two-parsers-one-shape flag; verified byte-
# equivalent before the swap). The grammar declares the shape; this module validates through it.
GATE_STATES = ("gated", "resumed", "aborted", "rewound")
FRONTMATTER_KEYS = ("id", "step_address", "session", "state", "control", "by", "note",
                    "rewound_to", "interrupt_http", "created", "updated", "history")


class GateError(RuntimeError):
    """A gate op could not run — raised TEACHING-loud (never a silent no-op). Mirrors BoardError/CloneError."""


# ── the gate-event emitter (P0.4 — mirrors cc_board's injected-emitter pattern) ────────────────────────
# Gate transitions — ESPECIALLY the destructive abort (interrupt+teardown kills a live session) — were
# invisible to the fabric: _transition wrote only the private .data/gates/<id>.md file, so an abort left
# no trace on events.jsonl (the review's audit-gap finding). Now every transition emits `gate.<control>`
# on the shared event layer. cc_gate stays standalone (no suite import — no cycle); the MCP face injects
# suite.emit_run_record at register() time; UNSET falls back to the durable bus directly. Lenient like
# every telemetry emit: a failure is SURFACED on the returned record (emit_error), never breaks the write.
_UNSET_EMITTER = object()   # sentinel: "never configured" ≠ "explicitly off (None)"
_GATE_EMITTER = _UNSET_EMITTER
_BUS_CACHE: dict = {}       # {store_path: FsStore} — the default emitter's lazy store handle


def set_gate_emitter(fn) -> None:
    """Install the process's gate-event emitter — a callable emit(control: str, fields: dict). Wired by
    the MCP face (suite.emit_run_record) or a test subscriber. None = EXPLICITLY off; UNSET (default) =
    the durable-bus fallback (gate activity lands on the shared events.jsonl whichever face acted)."""
    global _GATE_EMITTER
    _GATE_EMITTER = fn


def _default_bus_emitter(event: str, fields: dict) -> None:
    path = os.environ.get("COMPANY_STORE") or os.path.join(REPO, ".data", "store")
    store = _BUS_CACHE.get(path)
    if store is None:
        from store.fs_store import FsStore
        store = _BUS_CACHE[path] = FsStore(path)
    store.append_event({"kind": f"gate.{event}",
                        "summary": f"{event}: {fields.get('step_address') or fields.get('id') or ''}",
                        **fields})


def _emit_gate_event(event: str, fields: dict) -> str | None:
    """Emit a gate event leniently. Returns an error string on failure (surfaced on the record, never
    raised) or None on success/emitter-off."""
    fn = _default_bus_emitter if _GATE_EMITTER is _UNSET_EMITTER else _GATE_EMITTER
    if fn is None:
        return None
    try:
        fn(event, fields)
        return None
    except Exception as e:                       # VISIBILITY best-effort — never break the file write
        return f"{type(e).__name__}: {e}"


def _sup(path: str, body=None, method: str = "POST", timeout: float = 30):
    """POST/GET the operator-controlled supervisor (reused pattern from cc_clone)."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{SUPERVISOR}{path}", data=data, method=method,
                                 headers={"Content-Type": "application/json"} if data else {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode()[:300]}
    except (urllib.error.URLError, OSError) as e:
        raise GateError(f"supervisor unreachable at {SUPERVISOR}{path} ({type(e).__name__}: {e}) — "
                        f"is it up? No silent no-op.")


# ── helpers ──────────────────────────────────────────────────────────────────────────────────────────
def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def _validate_step_address(step_address: str) -> None:
    """FAIL-LOUD on a malformed step address (bar 3: never a silent no-op / guessed-nearest). We check the
    FORMAT only (opaque — the lead's resolver gives it meaning + the resolve/round-trip verification).
    TWO legal step forms (R13 bar 4): a native session tool-step (session://<sid>/step/<tool_use_id>) OR a
    composition-step — a run_composition leg's run:// address (run://<turn>/<member>[/<index>]). The gate
    treats both opaquely; a composition-step is the harness payoff (run_composition is OUR driver → a
    pre-leg pause is enforceable, unlike the native-loop HONEST-LIMIT for session-steps)."""
    if not (is_step_address(step_address) or is_composition_step_address(step_address)):
        raise GateError(
            f"invalid step address {step_address!r} — expected either a session tool-step "
            f"'session://<sid>/step/<tool_use_id>' or a composition-step 'run://<turn>/<member>[/<index>]'. "
            f"Fail loud (never gate a guessed-nearest / silent address). (format-validated here; the "
            f"cognition.py resolver gives it meaning + the H1.1/H1.2 round-trip.)")


def _path(gates_dir: str | None, gid: str) -> str:
    return os.path.join(gates_dir or GATES_DIR, f"{gid}.md")


def _render(rec: dict) -> str:
    import yaml
    fm = {k: rec[k] for k in FRONTMATTER_KEYS if k in rec}
    return "---\n" + yaml.dump(fm, sort_keys=False, allow_unicode=True) + "---\n"


def _read(path: str) -> dict | None:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return _fm_extract(f.read()) or None


def _write(gates_dir: str | None, rec: dict) -> None:
    d = gates_dir or GATES_DIR
    os.makedirs(d, exist_ok=True)
    _atomic_write_fsync(Path(_path(gates_dir, rec["id"])), _render(rec))


def _find(gate_id_or_step: str, *, gates_dir: str | None = None) -> dict:
    """Resolve a gate by its id OR by the step_address it gates. Fail-loud if absent."""
    direct = _read(_path(gates_dir, gate_id_or_step))
    if direct is not None:
        return direct
    for rec in list_gates(gates_dir=gates_dir):
        if rec.get("step_address") == gate_id_or_step:
            return rec
    raise GateError(f"no gate {gate_id_or_step!r} (by id or step_address) — nothing to act on. Fail loud.")


def _transition(rec: dict, to_state: str, control: str, by: str, note: str, *,
                gates_dir: str | None, extra: dict | None = None) -> dict:
    if to_state not in GATE_STATES:
        raise GateError(f"unknown gate state {to_state!r} — one of {list(GATE_STATES)}. Fail loud.")
    rec = dict(rec)
    rec["history"] = list(rec.get("history") or []) + [
        {"from": rec.get("state"), "to": to_state, "control": control, "by": by or "", "ts": _now(),
         "note": note or ""}]
    rec["state"] = to_state
    rec["control"] = control
    rec["by"] = by or ""
    rec["note"] = note or ""
    rec["updated"] = _now()
    if extra:
        rec.update(extra)
    _write(gates_dir, rec)
    # P0.4 — every lifecycle transition is a fabric event (the abort audit-gap fix); lenient, post-write.
    err = _emit_gate_event(control, {"id": rec.get("id"), "step_address": rec.get("step_address"),
                                     "session": rec.get("session"), "from": rec["history"][-1]["from"],
                                     "to": to_state, "by": by or "", "note": note or ""})
    if err:
        rec = dict(rec); rec["emit_error"] = err          # surfaced on the return, not persisted
    return rec


# ── the ops ──────────────────────────────────────────────────────────────────────────────────────────
def gate(step_address: str, session: str, *, note: str = "", by: str = "", gates_dir: str | None = None) -> dict:
    """REGISTER a gate on a declared step (state=gated). The PAUSE itself rides the NATIVE blocks_execution
    declaration (claude's CLI enforces it — we observe + record, never enforce a pre-pause ourselves).
    `step_address` is stored OPAQUE (format-validated, never parsed); `session` is the separate abort/rewind
    handle. Fail-loud on a malformed address (bar 3)."""
    _validate_step_address(step_address)
    if not session:
        raise GateError("gate() needs a `session` (the operational handle for abort/rewind) — separate from "
                        "the opaque step_address. Fail loud.")
    rec = {"id": "gate-" + _uuid.uuid4().hex[:8], "step_address": step_address, "session": session,
           "state": "gated", "control": "gate", "by": by or "", "note": note or "",
           "created": _now(), "updated": _now(),
           "history": [{"from": None, "to": "gated", "control": "gate", "by": by or "", "ts": _now(),
                        "note": note or ""}]}
    _write(gates_dir, rec)
    # P0.4 — the registration itself is a fabric event too (gate() writes directly, not via _transition).
    err = _emit_gate_event("gate", {"id": rec["id"], "step_address": step_address, "session": session,
                                    "from": None, "to": "gated", "by": by or "", "note": note or ""})
    if err:
        rec = dict(rec); rec["emit_error"] = err
    return rec


def resume(gate_id_or_step: str, *, by: str = "", note: str = "", gates_dir: str | None = None) -> dict:
    """RESUME a gated step (state=resumed). In the observer model the native pause is released by the
    operator's normal action (e.g. answering the blocking step); this RECORDS the decision (no hot-path
    enforcement). Bar 4's 'resumes + completes correctly' is the native continuation; we record it."""
    rec = _find(gate_id_or_step, gates_dir=gates_dir)
    if rec.get("state") != "gated":
        raise GateError(f"gate {rec['id']} is {rec.get('state')!r}, not 'gated' — cannot resume. Fail loud.")
    return _transition(rec, "resumed", "resume", by, note, gates_dir=gates_dir)


def abort(gate_id_or_step: str, *, by: str = "", note: str = "", gates_dir: str | None = None) -> dict:
    """ABORT a gated step's session (state=aborted): supervisor /interrupt then /teardown — the existing
    NO-ORPHAN law (bar 4). Reuse, not rebuild. Fail-loud if the supervisor refuses."""
    rec = _find(gate_id_or_step, gates_dir=gates_dir)
    session = rec.get("session")
    if not session:
        raise GateError(f"gate {rec['id']} has no session — cannot abort. Fail loud.")
    # P0.4 — capture the /interrupt result instead of discarding it. A failed interrupt does NOT block the
    # abort (teardown is the no-orphan backstop either way) but it is RECORDED, never silently swallowed.
    icode, ir = _sup("/interrupt", {"session": session})          # stop the in-flight turn
    code, r = _sup("/teardown", {"session": session})  # no-orphan: tear the session down
    if code != 200:
        raise GateError(f"abort: supervisor /teardown for {session} failed (HTTP {code}): {r}. Fail loud.")
    inote = "" if icode == 200 else f" [interrupt FAILED (HTTP {icode}): {ir} — teardown was the backstop]"
    return _transition(rec, "aborted", "abort", by,
                       (note or f"interrupt+teardown {session} (no-orphan)") + inote,
                       gates_dir=gates_dir, extra={"interrupt_http": icode})


def rewind(gate_id_or_step: str, source_jsonl: str, at: str, *, by: str = "", note: str = "",
           dest_dir: str | None = None, gates_dir: str | None = None) -> dict:
    """REWIND via the NATIVE fork transform (materialize_at_point) — surface-don't-rebuild (bar 2). Cuts
    the session's transcript at `at` ('compact:N'|'uuid:..'|'ts:..') into a NEW materialized session
    (source byte-untouched); records the new sid. NOT a reimplemented restore."""
    from runtime.session_pointintime import materialize_at_point
    rec = _find(gate_id_or_step, gates_dir=gates_dir)
    if not os.path.exists(source_jsonl):
        raise GateError(f"rewind: source transcript not found: {source_jsonl}. Fail loud.")
    out_dir = dest_dir or os.path.dirname(os.path.abspath(source_jsonl))
    mat = materialize_at_point(source_jsonl, at, dest_dir=out_dir)
    if not mat.get("source_untouched"):
        raise GateError(f"rewind: source changed during materialization of {source_jsonl} — abort (non-destructive law).")
    return _transition(rec, "rewound", "rewind", by, note or f"materialized @ {at}",
                       gates_dir=gates_dir, extra={"rewound_to": mat["new_sid"]})


def get_gate(gate_id_or_step: str, *, gates_dir: str | None = None) -> dict:
    return _find(gate_id_or_step, gates_dir=gates_dir)


def list_gates(*, state: str | None = None, session: str | None = None, gates_dir: str | None = None) -> list[dict]:
    """All gate records (file-discovered), optionally filtered by state/session. Sorted by created."""
    d = gates_dir or GATES_DIR
    out = []
    if os.path.isdir(d):
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".md") or fn.startswith("_"):
                continue
            rec = _read(os.path.join(d, fn))
            if rec is None:
                continue
            if state is not None and rec.get("state") != state:
                continue
            if session is not None and rec.get("session") != session:
                continue
            out.append(rec)
    return sorted(out, key=lambda r: r.get("created") or "")
