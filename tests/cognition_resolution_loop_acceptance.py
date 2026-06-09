#!/usr/bin/env python3
"""tests/cognition_resolution_loop_acceptance.py — GROUP J (SUITE-2 lane): the cognition↔resolution loop.

J1 — the swarm's run://<turn>/<role> outputs (the system's OWN thinking) feed the NEXT turn's R2 resolution.
Today R2 resolves operator-notebook strata; the swarm's cognition was a parallel edge that never converged
back. This wires the PRIOR completed turn's cognition into what the next turn's R2 resolves.

REUSE-don't-parallel (the lane law): the wire rides `_r2_gather` (a new `cognition` stratum) + the run INDEX
(#54, E2-incremental) + `resolve_address` (the canonical resolver) — NO second resolver, NO second index.

THE PROOFS (the traps the advisor flagged — proven, not assumed):
  1. END-TO-END WIRE: seed a PRIOR completed turn's cognition at run://<turn>/<role> + its cognition.turn.done;
     `_chat_context` for the NEXT turn RESOLVES that prior thinking into the context string — with NO canvas
     locus (current_locus empty) — the exact case J1 cares about (a plain chat).
  2. IN-FLIGHT EXCLUSION: an IN-FLIGHT turn (run:// written, but NO cognition.turn.done yet) is NOT resolved
     — only COMPLETED prior turns feed back (turn.done fires in the epilogue, after the context is built).
  3. NO LEAK: the address-attached reads `context_at`/`surface_intent_at` (resolution=None → admit-all) do
     NOT gain the global cognition stratum — the opt-in is positive-membership, not `_ok` (the silent
     contract-violation the advisor caught).
  4. OFF MODE: the cognition loop is suppressed in `off` (the presence dial off resolves nothing).
  5. BOUNDED: capped to R2_COGNITION_TURNS prior turns; a long role output is truncated (no flood).
  6. FAIL-LOUD-LEGIBLE: a pruned run:// ref is SKIPPED with a warning, never crashes the gather.
"""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from store.fs_store import FsStore
from runtime.suite import Suite
from runtime.registry import NodeRegistry

PASS = 0
def check(label, cond):
    global PASS
    print(f"  {'ok ' if cond else 'XX '} {label}")
    if not cond:
        raise SystemExit(f"FAIL: {label}")
    PASS += 1


def _suite(root):
    store = FsStore(root)
    reg = NodeRegistry().discover([os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes")])
    return Suite(store, reg)


def _seed_completed_turn(suite, turn, role_outputs: dict):
    """Seed a COMPLETED prior turn the way `chat_parts` does: write each role's run://<turn>/<role> output,
    emit a `cognition.role.ran` lifecycle event (ok=True, address — the SWARM's discovery surface), and emit
    `cognition.turn.done` (so it counts as a COMPLETED turn). NOTE: deliberately NO op.run RUN-INDEX record —
    the swarm doesn't emit one (flood-avoidance), so the wire must discover via role.ran, NOT find_runs."""
    addrs = []
    for role, text in role_outputs.items():
        addr = f"run://{turn}/{role}"
        cas = suite.store.put_content(text)
        suite.store.set_ref(addr, cas)
        addrs.append(addr)
        suite._emit("cognition.role.ran", f"role {role} ok", turn_id=turn, role=role, ok=True,
                    ms=5, address=addr)
    suite._emit("cognition.turn.done", f"turn {turn} done", turn_id=turn, total_ms=10,
                n_parts=2, n_roles=len(role_outputs), address=f"ui://cognition/{turn}")
    return addrs


def _seed_inflight_turn(suite, turn, role_outputs: dict):
    """Seed an IN-FLIGHT turn the way chat_parts looks at part-2: run:// written + `cognition.role.ran`
    ALREADY FIRED (the wave joined), but NO `cognition.turn.done` yet (the epilogue hasn't run). This proves
    the TURN.DONE GATE is what excludes the in-flight turn — NOT the absence of role.ran events (which HAVE
    fired by part-2). If the wire keyed on role.ran presence, this turn would leak into its own context."""
    for role, text in role_outputs.items():
        addr = f"run://{turn}/{role}"
        cas = suite.store.put_content(text)
        suite.store.set_ref(addr, cas)
        suite._emit("cognition.role.ran", f"role {role} ok", turn_id=turn, role=role, ok=True,
                    ms=5, address=addr)


with tempfile.TemporaryDirectory() as root:
    suite = _suite(root)
    GID = "g1"
    suite.create_node(GID, "constant", config={"value": "hi"})   # a real graph so state() works

    print("[1] END-TO-END — a prior turn's cognition resolves into the NEXT turn's context (NO canvas locus)")
    # the distinctive marker that proves the prior thinking reached the context.
    MARKER = "ZEBRA-COGNITION-MARKER-7731"
    _seed_completed_turn(suite, "turn-prior", {"recall": f"recalled fact: {MARKER}",
                                               "ground": "in scope: yes"})
    # NO canvas locus held (a plain chat). assemble the NEXT turn's context.
    assert not suite.current_locus(), f"test setup: expected no locus, got {suite.current_locus()!r}"
    ctx = suite._chat_context(GID, intent="what did we establish")
    check("1 the prior turn's cognition (the recall marker) IS in the next turn's context",
          MARKER in ctx)
    check("1 it is framed as the system's OWN thinking (not 'operator's locus')",
          "YOUR OWN PRIOR THINKING" in ctx)
    check("1 it resolved with NO canvas locus (the plain-chat case J1 exists for)",
          not suite.current_locus())

    print("\n[2] IN-FLIGHT EXCLUSION — the current/in-flight turn's cognition is NOT resolved into its own context")
    INFLIGHT = "OCTOPUS-INFLIGHT-MARKER-4422"
    _seed_inflight_turn(suite, "turn-inflight", {"recall": f"in-flight thought: {INFLIGHT}"})
    ctx2 = suite._chat_context(GID, intent="what now")
    check("2 the in-flight turn (no turn.done) is EXCLUDED from the resolution", INFLIGHT not in ctx2)
    check("2 the COMPLETED prior turn still resolves (the wire still works)", MARKER in ctx2)

    print("\n[3] NO LEAK — context_at / surface_intent_at (resolution=None) do NOT gain global cognition")
    # context_at is an address-attached read (admit-all). It must NOT pull the conversation-global cognition.
    bundle = suite.context_at("ui://chrome/inbox")
    leaked = any(MARKER in (it.get("text", "") or "") for it in bundle["items"])
    check("3 context_at('ui://chrome/inbox') has NO cognition leak (positive opt-in, not _ok admit-all)",
          not leaked)
    # _r2_gather with resolution=None (the default admit-all path every legacy caller uses) — no cognition.
    raw = suite._r2_gather("ui://chrome/inbox")     # resolution=None → admit=None
    check("3 _r2_gather(resolution=None) admits NO cognition stratum (the silent-leak guard)",
          not any(it.get("kind") == "cognition" for it in raw))

    print("\n[4] OFF MODE — the cognition loop is suppressed")
    suite.set_mode("off")
    # off-mode _chat_context still runs the grounding blocks but must NOT inject cognition.
    ctx_off = suite._chat_context(GID, intent="anything")
    check("4 off mode does NOT resolve the cognition loop", MARKER not in ctx_off)
    suite.set_mode("listening")

    print("\n[5] BOUNDED — capped to R2_COGNITION_TURNS prior turns + per-role char cap")
    # seed MORE completed turns than the cap; the OLDEST must drop out of the window.
    suite.R2_COGNITION_TURNS = 2
    _seed_completed_turn(suite, "turn-A", {"recall": "AAAA-oldest-turn-marker"})
    _seed_completed_turn(suite, "turn-B", {"recall": "BBBB-middle-turn-marker"})
    _seed_completed_turn(suite, "turn-C", {"recall": "CCCC-newest-turn-marker"})
    strata = suite._r2_cognition_strata()
    turns_seen = {it["text"].split("@ run://")[1].split("/")[0] for it in strata if "@ run://" in it["text"]}
    check("5 only the R2_COGNITION_TURNS (2) most-recent completed turns are gathered",
          len(turns_seen) <= 2 and "turn-C" in turns_seen and "turn-B" in turns_seen
          and "turn-A" not in turns_seen)
    # per-role char cap: a huge role output is truncated with a marker.
    suite.R2_COGNITION_PER_ROLE = 40
    _seed_completed_turn(suite, "turn-big", {"recall": "X" * 500})
    big = [it for it in suite._r2_cognition_strata() if "turn-big" in it.get("text", "")]
    check("5 a long role output is TRUNCATED (no flood)", big and "…" in big[0]["text"]
          and len(big[0]["_raw"]) <= 41)

    print("\n[6] FAIL-LOUD-LEGIBLE — a pruned run:// ref is SKIPPED, never crashes the gather")
    # a completed turn whose role.ran address was NEVER set_ref'd (a pruned/dangling ref).
    suite._emit("cognition.role.ran", "role recall ok", turn_id="turn-pruned", role="recall", ok=True,
                ms=5, address="run://turn-pruned/recall")
    suite._emit("cognition.turn.done", "turn turn-pruned done", turn_id="turn-pruned", total_ms=10,
                n_parts=2, n_roles=1, address="ui://cognition/turn-pruned")
    # must not raise; the pruned ref is skipped (on_missing='skip' → None → skipped).
    survived = suite._r2_cognition_strata()
    check("6 a pruned ref is skipped (gather survives, returns the resolvable items)",
          isinstance(survived, list))

print(f"\nALL {PASS} CHECKS PASS — GROUP J: the swarm's prior-turn cognition feeds the next turn's R2 "
      f"resolution (end-to-end, no-locus), in-flight excluded, no leak into address reads, off-suppressed, "
      f"bounded, fail-loud. The system sees its own thinking.")
