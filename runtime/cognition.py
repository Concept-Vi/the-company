"""runtime/cognition.py — Concurrent Cognition G0 PROVING SPIKE.

This is the GATE spike (G0) for the Concurrent Cognition build (build-prep/concurrent-cognition/).
It is deliberately MINIMAL — it proves the MECHANISM, not the full substrate (that is G1–G9).
It is ADDITIVE: it does NOT touch `chat()`/`suite.py`/`scheduler.py`. It fires at the EXISTING
resident 4B pool via the SAME fabric path the judge (`Suite.is_finished_thought`) uses, and it
round-trips a concurrent role's output through the addressed store at a `run://` address — the
net-new injection ref-read the criteria (C0.1/C4.2 · R1-FOLD F3) call for.

What it proves (G0):
  C0.1  a 2-PART staged turn: Part 1 emits from base context immediately; `recall` fires
        CONCURRENTLY (a thread); its validated JSON is written to `run://<turn>/recall`; a
        DECLARED RULE reads that RESOLVED ADDRESS BACK (head→get_content, never the thread's
        in-memory return) and decides whether to inject; Part 2 emits enriched.
  C0.2  ROUTING is rule-based + DETERMINISTIC — the rule is a PURE function of fully-resolved
        address values (no now()/random/wave-order/partials), so identical resolved inputs route
        identically regardless of the order roles finished in (R1-FOLD F5 / R2-FOLD H7).
  C0.4  fail loud: a missing/unresolved recall ref RAISES — never implicit-truthy-on-missing
        (R2-FOLD H2 sub-call 1). A down resident model PROPAGATES FabricError (fail loud).
  C0.5  concurrency probe helper (`concurrency_probe`) fires N concurrent role-runs at the
        resident pool and measures how many complete + latency distribution.

LAWS honoured:
  L1 registry-driven — the spike roles are DECLARED DATA ({id, prompt_template, output_schema}),
     not hardcoded control-flow. (Full file-discovered ROLE_REGISTRY is G2 — flagged.)
  L2 rule-routing — a model runs ONLY inside a ROLE (`run_role`); ROUTING is a declared RULE
     (`recall_injection_rule`), a pure function — never a model call.
  run:// addressing throughout — NEVER swarm:// (not a registered scheme).
  fail loud · additive · reflects-never-owns (the spike only READS resolved store values to route).

SPIKE CONSTANTS (NOT a fabricated registry row — rule 8): the resident endpoint + model-id are
TASK-GIVEN facts about what is UP right now. Proper registration of these as a role's model
binding from the capability registry is G1/G8, not G0. They are passed as params with these
documented defaults.
"""
from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator

from pydantic import BaseModel, Field

from fabric import client, transport

# --- spike constants: the resident 4B pool that is UP (task-given; NOT invented) ----------------
RESIDENT_BASE_URL = "http://127.0.0.1:8000/v1"
RESIDENT_MODEL = "cyankiwi/Qwen3.5-4B-AWQ-4bit"
ROLE_TIMEOUT = 60


# --- output schemas (a role declares its output_schema; complete() validate/retries against it) --
class FocusOut(BaseModel):
    """`focus` reads the utterance → the turn's intent + which auxiliary roles to run."""
    intent: str
    which_roles: list[str] = Field(default_factory=list)


class RecallOut(BaseModel):
    """`recall` reads the utterance → a memory snippet + whether it is relevant enough to inject."""
    snippet: str
    relevant: bool


class GroundOut(BaseModel):
    """`ground` reads the utterance → whether it is IN SCOPE for this system + a one-line grounding note.
    (The second concurrent role — so the C0.2 rule reads TWO roles' resolved outputs.)"""
    in_scope: bool
    note: str


# --- a ROLE is declared data (L1) ---------------------------------------------------------------
@dataclass
class Role:
    """A declared role: {id, prompt_template, output_schema}. A model runs ONLY inside a role (L2).
    `prompt_template` is a system prompt; the utterance is the user message. `output_schema` is the
    Pydantic model the role's JSON is validated against (client-side validate/retry — C1.4/F9)."""
    id: str
    prompt_template: str
    output_schema: type[BaseModel]


FOCUS_ROLE = Role(
    id="focus",
    prompt_template=(
        "You are the FOCUS role. Read the operator's utterance and return ONLY JSON with two fields:\n"
        '  "intent": a short phrase naming what the operator wants,\n'
        '  "which_roles": a JSON array of auxiliary role names to run for this turn.\n'
        'Available auxiliary roles: ["recall"]. Include "recall" when the utterance refers to past '
        "decisions, prior context, or memory; otherwise return an empty array.\n"
        'Example: {"intent": "recall a past decision", "which_roles": ["recall"]}'
    ),
    output_schema=FocusOut,
)

RECALL_ROLE = Role(
    id="recall",
    prompt_template=(
        "You are the RECALL role — the cognition's memory. Read the operator's utterance and return "
        "ONLY JSON with two fields:\n"
        '  "snippet": a short (one or two sentence) recalled note that would help answer the utterance,\n'
        '  "relevant": a boolean — true if the snippet is genuinely useful for THIS utterance, false if not.\n'
        'Example: {"snippet": "We decided the storage layer stays content-addressed on ext4.", "relevant": true}'
    ),
    output_schema=RecallOut,
)

GROUND_ROLE = Role(
    id="ground",
    prompt_template=(
        "You are the GROUND role — you check whether the operator's utterance is IN SCOPE for the "
        "Company system (a composition/cognition suite the operator builds with AI). Return ONLY JSON "
        "with two fields:\n"
        '  "in_scope": a boolean — true if answering this is a legitimate task for the system,\n'
        '  "note": a one-line grounding note.\n'
        'Example: {"in_scope": true, "note": "A question about a past architecture decision is in scope."}'
    ),
    output_schema=GroundOut,
)

SPIKE_ROLES: dict[str, Role] = {FOCUS_ROLE.id: FOCUS_ROLE, RECALL_ROLE.id: RECALL_ROLE,
                                GROUND_ROLE.id: GROUND_ROLE}


# --- run_role: fire ONE request at the resident 4B (mirrors is_finished_thought's fabric path) ---
def run_role(role: Role, ctx: dict, *, base_url: str = RESIDENT_BASE_URL,
             model: str = RESIDENT_MODEL, timeout: int = ROLE_TIMEOUT,
             max_tokens: int = 256) -> dict:
    """Fire ONE request at the resident 4B for `role`, returning VALIDATED JSON (a dict).

    Mirrors `Suite.is_finished_thought`/the judge EXACTLY: `client.complete(openai_transport(...))`.
    `json=True` makes the transport set `response_format: {"type": "json_object"}` (verified the
    resident vLLM honours it); `schema=` makes `complete()` parse + validate + retry on a malformed
    role output (client-side enforcement — C1.4/F9). temperature=0 for routing-stable outputs.

    `ctx` must carry `utterance`. Fail loud: a transport/empty/parse/schema failure PROPAGATES as
    FabricError after retries (never a silent empty dict)."""
    utterance = ctx["utterance"]
    msgs = [
        {"role": "system", "content": role.prompt_template},
        {"role": "user", "content": f"Utterance: {utterance}"},
    ]
    t = transport.openai_transport(base_url=base_url, timeout=timeout)
    validated = client.complete(
        t, msgs, model=model, schema=role.output_schema, json=True,
        temperature=0, max_tokens=max_tokens,
    )
    return validated.model_dump()


# --- the DECLARED RULE (L2): a NON-TRIVIAL pure function of resolved values (C0.2 / R1-FOLD F5) ---
# DECLARED inputs of this rule (the referenceable-input whitelist): the resolved `recall` AND `ground`
# role outputs — TWO roles that fire CONCURRENTLY and finish in NONDETERMINISTIC order. The rule reads
# MULTIPLE fields across BOTH (recall.relevant, ground.in_scope, recall.snippet, ground.note) — not a
# one-liner — and is the exact case F5 hardens: it must NOT depend on which sibling finished first.
RULE_INPUTS = ("recall", "ground")


def injection_rule(resolved: dict) -> dict:
    """The routing RULE for Part 2. PURE function of the RESOLVED `recall` AND `ground` values.

    LOGIC (multi-field, F5): INJECT the recalled snippet iff `recall.relevant AND ground.in_scope`.
    Reads multiple fields across BOTH roles' resolved outputs.

    DETERMINISM (C0.2 / R1-FOLD F5): reads ONLY fully-resolved address values from the declared
    whitelist (RULE_INPUTS) — NO now()/random/wave-completion-order/partial-results/model-call. So
    identical resolved inputs route identically regardless of the order recall vs ground finished in.

    FAIL LOUD (C0.4 / R2-FOLD H2): a missing declared input RAISES — never implicit-truthy-on-missing.

    Returns the routing decision: {inject: bool, snippet: str|None, reason: str}."""
    for key in RULE_INPUTS:
        if key not in resolved:                  # a declared input did not resolve → fail loud
            raise KeyError(
                f"injection_rule: no resolved {key!r} value — its ref did not resolve. "
                f"Fail loud (never implicit-skip): a routing rule must see ALL its declared inputs "
                f"({list(RULE_INPUTS)}).")
    rec = resolved["recall"]
    grd = resolved["ground"]
    relevant = bool(rec.get("relevant"))
    in_scope = bool(grd.get("in_scope"))
    if relevant and in_scope:
        return {"inject": True, "snippet": rec["snippet"],
                "reason": "recall.relevant AND ground.in_scope"}
    return {"inject": False, "snippet": None,
            "reason": f"recall.relevant={relevant} ground.in_scope={in_scope}"}


# --- the staged 2-part turn (C0.1) --------------------------------------------------------------
@dataclass
class StagedTurn:
    """The captured artifact of one staged turn — the proof the criteria read."""
    turn_id: str
    utterance: str
    focus: dict
    parts: list[str] = field(default_factory=list)
    part1_ts: float = 0.0
    wave_done_ts: float = 0.0
    role_finish_order: list[str] = field(default_factory=list)  # the ORDER the wave's roles finished
    routing: dict = field(default_factory=dict)
    addresses: dict = field(default_factory=dict)               # role_id -> run:// address
    resolved: dict = field(default_factory=dict)                # role_id -> resolved value (read back)


def chat_parts_spike(utterance: str, store, *, turn_id: str | None = None,
                     base_url: str = RESIDENT_BASE_URL, model: str = RESIDENT_MODEL,
                     ) -> tuple[Iterator[str], StagedTurn]:
    """Emit a 2-PART staged reply for `utterance` (C0.1). Returns (parts_stream, turn_record).

    The flow (the mechanism G0 proves):
      1. focus fires → {intent, which_roles}.
      2. Part 1 emits from BASE context IMMEDIATELY (timestamped before the wave completes).
      3. recall AND ground fire CONCURRENTLY (a WAVE of two threads, finishing in nondeterministic
         order); each writes its VALIDATED JSON to its own `run://<turn>/<role>` address
         (put_content → set_ref) — the addressed write.
      4. We JOIN the wave, then the RULE reads BOTH RESOLVED ADDRESSES BACK (head → get_content,
         NOT the threads' in-memory returns — proving the addressed ref-read, C4.2/F3) and decides
         from a multi-field predicate over both (the F5 non-trivial-rule case).
      5. Part 2 emits — enriched with the injected snippet iff the rule said inject.

    `store` is an FsStore (the same store the app uses). run:// addressing throughout.
    The parts are yielded as a generator (staging is visible: part1 is yielded before part2 exists).
    """
    turn_id = turn_id or "spike-" + time.strftime("%Y%m%d-%H%M%S")
    rec = StagedTurn(turn_id=turn_id, utterance=utterance, focus={})

    # 1. focus fires first (C0.1 says focus fires — it is REAL, gating which_roles).
    rec.focus = run_role(FOCUS_ROLE, {"utterance": utterance}, base_url=base_url, model=model)
    which = set(rec.focus.get("which_roles") or [])
    # The C0.2 wave runs recall+ground together when focus routes recall (a memory turn). ground is
    # blessed by C0.1/C2.3; it always co-fires with recall here so the rule has two concurrent inputs.
    run_wave = "recall" in which

    rec.addresses = {"recall": f"run://{turn_id}/recall", "ground": f"run://{turn_id}/ground"}

    # 3 (kick off). The WAVE: recall + ground fire CONCURRENTLY; each thread WRITES its run:// address.
    wave_errors: list[BaseException] = []
    order_lock = threading.Lock()

    def _role_worker(role: Role):
        try:
            out = run_role(role, {"utterance": utterance}, base_url=base_url, model=model)
            cas = store.put_content(out)              # immutable content
            store.set_ref(rec.addresses[role.id], cas)  # mutable run:// pointer (atomic set_ref)
            with order_lock:                          # capture the REAL finish order (nondeterministic)
                rec.role_finish_order.append(role.id)
        except BaseException as e:                    # capture; re-raised after join (fail loud)
            with order_lock:
                wave_errors.append(e)

    wave: list[threading.Thread] = []
    if run_wave:
        for role in (RECALL_ROLE, GROUND_ROLE):
            th = threading.Thread(target=_role_worker, args=(role,), name=f"spike-{role.id}",
                                  daemon=True)
            wave.append(th)
            th.start()

    def _stream() -> Iterator[str]:
        # 2. Part 1 from BASE context — emitted IMMEDIATELY, before the wave completes.
        part1 = f"[Part 1 · base context] On {rec.focus.get('intent', 'your message')}: let me check."
        rec.part1_ts = time.monotonic()
        rec.parts.append(part1)
        yield part1

        # 4. JOIN the wave, then the RULE reads BOTH RESOLVED ADDRESSES BACK (not the in-memory returns).
        if wave:
            for th in wave:
                th.join(timeout=ROLE_TIMEOUT + 5)
            if wave_errors:                           # fail loud — propagate a role's failure
                raise wave_errors[0]
            resolved = {}
            for rid, addr in rec.addresses.items():
                cas = store.head(addr)                # resolve the run:// address
                if cas is None:                       # fail loud — the ref did NOT resolve
                    raise RuntimeError(
                        f"chat_parts_spike: address {addr} did not resolve (head() is None) — "
                        f"fail loud, never route on an unresolved ref.")
                resolved[rid] = store.get_content(cas)  # read the RESOLVED value back
            rec.resolved = resolved
            rec.wave_done_ts = time.monotonic()
            rec.routing = injection_rule(resolved)    # the PURE multi-field rule decides routing
        else:
            # focus routed recall OFF — no injection this turn (deterministic on focus.which_roles).
            rec.routing = {"inject": False, "snippet": None, "reason": "focus did not route recall"}

        # 5. Part 2 — enriched iff the rule injected.
        if rec.routing["inject"]:
            part2 = (f"[Part 2 · enriched] Recalled: \"{rec.routing['snippet']}\" "
                     f"— using it to answer.")
        else:
            part2 = f"[Part 2 · base] (no relevant recall: {rec.routing['reason']}) Here is my answer."
        rec.parts.append(part2)
        yield part2

    return _stream(), rec


# --- C0.5 concurrency probe: fire N concurrent run_role calls at the resident pool ---------------
def concurrency_probe(n: int, *, role: Role = RECALL_ROLE,
                      utterance: str = "What did we decide about the storage layer?",
                      base_url: str = RESIDENT_BASE_URL, model: str = RESIDENT_MODEL,
                      max_tokens: int = 128) -> dict:
    """Fire `n` concurrent `run_role` calls at the EXISTING resident pool (no new load — task floor).
    Measures how many complete + the latency distribution at the CURRENT resident config. A first
    datapoint for C0.5; the full swarm-mode-config measurement (GPU reconfig) is the LEAD's."""
    latencies: list[float] = []
    errors: list[str] = []
    lock = threading.Lock()

    def _one(_i):
        t0 = time.monotonic()
        try:
            run_role(role, {"utterance": utterance}, base_url=base_url, model=model,
                     max_tokens=max_tokens)
            dt = time.monotonic() - t0
            with lock:
                latencies.append(dt)
        except BaseException as e:
            with lock:
                errors.append(repr(e))

    threads = [threading.Thread(target=_one, args=(i,)) for i in range(n)]
    wall0 = time.monotonic()
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    wall = time.monotonic() - wall0

    lat = sorted(latencies)

    def _pct(p):
        if not lat:
            return None
        k = max(0, min(len(lat) - 1, int(round((p / 100) * (len(lat) - 1)))))
        return round(lat[k], 3)

    return {
        "n": n,
        "completed": len(latencies),
        "failed": len(errors),
        "errors": errors[:5],
        "wall_s": round(wall, 3),
        "latency_s": {"p50": _pct(50), "p95": _pct(95), "max": round(max(lat), 3) if lat else None,
                      "min": round(min(lat), 3) if lat else None},
    }
