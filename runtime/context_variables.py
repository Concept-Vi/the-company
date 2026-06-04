"""C6 — the context-variable interface (the RHM's *seeing* half). See build-prep/contracts/C6.

The right-hand-man's context is NOT a fixed prompt. It RESOLVES, per turn, by the
same operation the runtime uses to fire nodes:

    runtime:  a node runs when its INPUT addresses resolve     -> acts on that data
    RHM:      a turn runs when its CONTEXT variables resolve    -> the brain acts on that context

So this module is the resolution engine again, pointed at context-variables instead of
node-inputs. A ContextVariable is a name + a `resolve(ctx)` + a `cost` (so assembly can
budget). The REGISTRY holds variable TYPES, not per-provider hardcoding (Tim's Vi Chat
"universal variable registry" principle) — register once, every turn/provider gains it.

Stdlib + pydantic only. Fail loud (no silent fallbacks). Schema-additive.
"""
from __future__ import annotations

from typing import Any, Literal, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from contracts.node_record import Graph, NodeInstance

# --- the cost budget vocabulary (so context-assembly can budget a turn) ---
Cost = Literal["cheap", "loads-model", "loads-corpus"]


class TurnContext(BaseModel):
    """What a single RHM turn has available — the substrate it resolves against.

    This is the live situation: the document (graph), where things live (store),
    what's selected, and the recent path. Each ContextVariable reads what it needs
    from here. `store` is the FsStore/Resolver (not a pydantic type) so it's typed
    `Any` + arbitrary_types_allowed and defaults to None — cheap variables don't need it.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    graph: Graph                                   # the live document (the canvas)
    selection: list[str] = Field(default_factory=list)   # node ids selected on the canvas
    recent: list[Any] = Field(default_factory=list)      # the recent path (event log slice)
    store: Any = None                              # the Resolver (C4) — None until needed
    # voice-trial (lane E): scope the trial_* context variables to ONE recorded session. Optional +
    # schema-additive — a turn that doesn't set it gets the most-recent trial session (trial_* read
    # the store). None means "no session selected".
    trial_session: str | None = None


@runtime_checkable
class ContextVariable(Protocol):
    """A context-variable TYPE: a name, a resolve, a cost. Mirrors the Resolver Protocol
    pattern (contracts/resolver.py) so `register()` can validate structurally."""

    name: str
    cost: Cost

    def resolve(self, ctx: TurnContext) -> Any:
        """Read the substrate, return exactly what this turn needs for this variable."""
        ...


# --- the universal registry of variable TYPES ---
REGISTRY: dict[str, ContextVariable] = {}


def register(var: ContextVariable) -> ContextVariable:
    """Register one context-variable type. One place; everything that assembles context
    gains it. Fail loud on a malformed variable or a duplicate name (no silent overwrite)."""
    if not isinstance(var, ContextVariable):
        raise TypeError(
            f"register: {var!r} is not a ContextVariable "
            "(needs `name: str`, `cost`, and `resolve(self, ctx)`)."
        )
    if var.name in REGISTRY and REGISTRY[var.name] is not var:
        raise ValueError(
            f"register: a different context-variable named {var.name!r} is already "
            "registered. A variable type is defined once (no silent overwrite)."
        )
    REGISTRY[var.name] = var
    return var


def resolve_context(ctx: TurnContext, names: list[str]) -> dict[str, Any]:
    """Resolve the named variables against the substrate — the per-turn bundle the brain
    receives. Fail loud on an unknown name (AGENTS.md rule 4: no silent fallbacks)."""
    bundle: dict[str, Any] = {}
    for name in names:
        var = REGISTRY.get(name)
        if var is None:
            raise KeyError(
                f"resolve_context: no context-variable registered as {name!r}. "
                f"Registered: {sorted(REGISTRY)}."
            )
        bundle[name] = var.resolve(ctx)
    return bundle


# --- concrete variable types -------------------------------------------------
# Each is a real ContextVariable: a name, a cost, and a resolve() that reads the
# substrate. They mirror the table in C6 / "The right-hand-man" deep-dive.


class Selection:
    """`selection` -> the node records currently selected on the canvas.

    Resolves from the live document (ctx.graph) by node id. Fail loud if a selected id
    isn't in the graph — that's a substrate inconsistency, not an empty result."""

    name: str = "selection"
    cost: Cost = "cheap"

    def resolve(self, ctx: TurnContext) -> list[NodeInstance]:
        by_id = {n.id: n for n in ctx.graph.nodes}
        out: list[NodeInstance] = []
        for nid in ctx.selection:
            node = by_id.get(nid)
            if node is None:
                raise KeyError(
                    f"selection: node id {nid!r} is selected but not in graph "
                    f"{ctx.graph.id!r}."
                )
            out.append(node)
        return out


class RunState:
    """`run-state` -> running / failed / idle, derived from node statuses.

    Resolves from the runtime's view living in the document (each node's `status`,
    a C3 Status literal). Returns the buckets plus a one-line summary."""

    name: str = "run_state"
    cost: Cost = "cheap"

    def resolve(self, ctx: TurnContext) -> dict[str, list[str]]:
        running, failed, idle = [], [], []
        for n in ctx.graph.nodes:
            if n.status in ("running",):
                running.append(n.id)
            elif n.status in ("failed",):
                failed.append(n.id)
            elif n.status in ("idle", "ready"):
                idle.append(n.id)
            # ran/cached/done/surfaced are terminal-ish; not running/failed/idle
        return {"running": running, "failed": failed, "idle": idle}


class Rules:
    """`rules` -> the governing rules that apply here (the constitution/registry, S7).

    Placeholder: returns [] until the governance engine (S7) exists. Schema-additive —
    when S7 lands, this resolve reads it; the shape (a list) stays."""

    name: str = "rules"
    cost: Cost = "cheap"

    def resolve(self, ctx: TurnContext) -> list[Any]:
        return []   # placeholder — no governance registry wired yet (S7)


class Trajectory:
    """`trajectory` -> the recent path: what you just did / decided (the event log)."""

    name: str = "trajectory"
    cost: Cost = "cheap"

    def resolve(self, ctx: TurnContext) -> list[Any]:
        return ctx.recent


class RecallSlice:
    """`recall-slice` -> the relevant slice of your past work (the corpus).

    Resolves EMPTY for now: there is no corpus yet. Per C6/§5, until recall exists this
    variable returns "nothing yet" and the brain leans on explicit context. When the
    corpus exists, this resolve queries it (cost becomes "loads-corpus" in practice)."""

    name: str = "recall_slice"
    cost: Cost = "loads-corpus"

    def resolve(self, ctx: TurnContext) -> list[Any]:
        return []   # nothing yet until the corpus exists


# --- voice-trial context variables (lane E) ------------------------------------------------
# The trial is the first real build of the memory loop, so its recordings become RESOLVABLE
# context: a turn can pull the recorded transcript / cast / Tim's spoken feedback as ground truth.
# These read ctx.store (the FsStore) directly — the SAME substrate suite.py writes via
# trial_record_*; no parallel store. They are registered into the C6 universal registry so any
# future context-assembly (and any provider) gains them once. cost="loads-corpus": reading a
# recorded session is a corpus read, not a cheap graph field. Fail loud on a missing store (a
# trial variable was requested with no resolver — a substrate inconsistency, not an empty result).


def _trial_transcript_addr(session_id: str) -> str:
    """Mirror of Suite._trial_transcript_addr — the trial://<session>/transcript ref. Kept in sync
    by the shared string form; both point at the one CAS-backed transcript (no parallel store)."""
    return f"trial://{session_id}/transcript"


def _resolve_trial_session(ctx: "TurnContext") -> str | None:
    """The session a trial_* variable resolves against: ctx.trial_session if set, else the
    most-recent recorded trial session in the store. None when there are no trial sessions yet."""
    if ctx.trial_session:
        return ctx.trial_session
    store = ctx.store
    if store is None:
        return None
    latest = None
    for sid in store.list_sessions():                       # ids are "trial-<ts>-..." → lexically sortable by ts
        s = store.load_session(sid)
        if s and s.get("kind") == "trial":
            if latest is None or sid > latest:
                latest = sid
    return latest


class TrialTranscript:
    """`trial_transcript` -> the full recorded transcript of a trial session (turns + Tim's
    feedback + the character's reflections), read from CAS via the trial://<session>/transcript
    ref. The debrief's ground truth as a context variable. Empty dict when no session / no
    recording (nothing yet) — but fail loud if a store is present and the named session has no ref
    is left to Suite.trial_transcript; the cheap context read returns {} so assembly never breaks."""

    name: str = "trial_transcript"
    cost: Cost = "loads-corpus"

    def resolve(self, ctx: "TurnContext") -> dict:
        sid = _resolve_trial_session(ctx)
        if sid is None or ctx.store is None:
            return {}
        cas = ctx.store.head(_trial_transcript_addr(sid))
        return ctx.store.get_content(cas) if cas else {}


class TrialCharacter:
    """`trial_character` -> which cast member a trial session was with (from the session record)."""

    name: str = "trial_character"
    cost: Cost = "cheap"

    def resolve(self, ctx: "TurnContext") -> str | None:
        sid = _resolve_trial_session(ctx)
        if sid is None or ctx.store is None:
            return None
        s = ctx.store.load_session(sid)
        return (s or {}).get("character")


class TrialFeedback:
    """`trial_feedback` -> just Tim's SPOKEN feedback turns from the resolved trial session (the
    operator's verdict-in-flight) — the slice of the transcript that is gold training signal."""

    name: str = "trial_feedback"
    cost: Cost = "loads-corpus"

    def resolve(self, ctx: "TurnContext") -> list[Any]:
        sid = _resolve_trial_session(ctx)
        if sid is None or ctx.store is None:
            return []
        cas = ctx.store.head(_trial_transcript_addr(sid))
        if not cas:
            return []
        transcript = ctx.store.get_content(cas) or {}
        return [t for t in transcript.get("turns", []) if t.get("kind") == "trial.feedback"]


# --- register the built-in variable types (one place) ---
register(Selection())
register(RunState())
register(Rules())
register(Trajectory())
register(RecallSlice())
register(TrialTranscript())
register(TrialCharacter())
register(TrialFeedback())


# --- self-check --------------------------------------------------------------
if __name__ == "__main__":
    # A tiny 2-node graph; "up" feeds "down". Selection points at "up".
    g = Graph(
        id="selfcheck",
        nodes=[
            NodeInstance(id="up", type="source", status="failed"),
            NodeInstance(id="down", type="sink", status="running"),
        ],
        edges=[],
    )
    ctx = TurnContext(graph=g, selection=["up"], recent=["opened canvas", "selected up"])

    bundle = resolve_context(ctx, ["selection", "run_state", "recall_slice"])

    # keys present
    assert set(bundle) == {"selection", "run_state", "recall_slice"}, bundle.keys()
    # selection -> the node record for "up"
    assert [n.id for n in bundle["selection"]] == ["up"], bundle["selection"]
    # run_state -> "up" failed, "down" running
    assert bundle["run_state"]["failed"] == ["up"], bundle["run_state"]
    assert bundle["run_state"]["running"] == ["down"], bundle["run_state"]
    # recall_slice -> empty (no corpus yet)
    assert bundle["recall_slice"] == [], bundle["recall_slice"]

    # fail loud on an unknown variable name
    try:
        resolve_context(ctx, ["does_not_exist"])
    except KeyError:
        pass
    else:
        raise AssertionError("resolve_context did not fail loud on an unknown name")

    # trial_* variables register + resolve to empty with no store (nothing recorded yet)
    assert {"trial_transcript", "trial_character", "trial_feedback"} <= set(REGISTRY), sorted(REGISTRY)
    tb = resolve_context(ctx, ["trial_transcript", "trial_character", "trial_feedback"])
    assert tb["trial_transcript"] == {}, tb["trial_transcript"]   # no store on ctx → empty, not a crash
    assert tb["trial_character"] is None, tb["trial_character"]
    assert tb["trial_feedback"] == [], tb["trial_feedback"]

    print("OK context_variables self-check")
    print("  registered:", sorted(REGISTRY))
    print("  selection :", [n.id for n in bundle["selection"]])
    print("  run_state :", bundle["run_state"])
    print("  recall    :", bundle["recall_slice"], "(nothing yet until the corpus exists)")
