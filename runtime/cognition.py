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
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator

from pydantic import BaseModel, Field

from contracts.address import scheme as _scheme
from fabric import client, transport
from fabric.vram import VramGate

# --- spike constants: the resident 4B pool that is UP (task-given; NOT invented) ----------------
RESIDENT_BASE_URL = "http://127.0.0.1:8000/v1"
RESIDENT_MODEL = "cyankiwi/Qwen3.5-4B-AWQ-4bit"
ROLE_TIMEOUT = 60


# --- the ROLE notion + the spike roles are now FILE-DISCOVERED (G2 · C2.1) ----------------------
# The G0 spike defined `Role` + FocusOut/RecallOut/GroundOut + FOCUS/RECALL/GROUND_ROLE INLINE here.
# G2 promotes roles into a FILE-DISCOVERED registry (runtime/roles.py + roles/*.py) — ONE role notion,
# not two. The CANONICAL definitions now live in roles/focus.py · roles/recall.py · roles/ground.py;
# cognition.py imports them FROM the registry (no duplicate definition). `Role` is re-exported from
# roles.py (the superset dataclass) so existing `run_role(role, ...)` / type hints are unchanged —
# roles.Role exposes the SAME .id/.prompt_template/.output_schema the spike's dataclass did.
from runtime.roles import Role, RoleRegistry  # noqa: E402  (the ONE role notion, file-discovered)

_ROLES_DIR = os.path.join(_REPO_ROOT, "roles") if "_REPO_ROOT" in dir() else os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "roles")


def role_registry() -> RoleRegistry:
    """Discover the file-based role registry (roles/*.py). The cognition driver + the Suite share this
    ONE registry (reuse-don't-parallel). Re-discovered fresh so a removed/added role file is picked up."""
    return RoleRegistry().discover([_ROLES_DIR])


# C 3b — skills + contexts as addressable, file-discovered registries (registry-is-truth). The TWO
# registries the `skill://`/`context://` schemes resolve through (the FIRST real extension of the C 3/4
# resolve_address seam). Reached EXACTLY like roles (a fresh discovered registry, reuse-don't-parallel).
from runtime.skills import SkillRegistry, ContextRegistry  # noqa: E402  (the C 3b registries)

_SKILLS_DIR = os.path.join(os.path.dirname(_ROLES_DIR), "skills")
_CONTEXTS_DIR = os.path.join(os.path.dirname(_ROLES_DIR), "contexts")


def skill_registry() -> SkillRegistry:
    """Discover the file-based skill registry (skills/*.py) — fresh each call, so an added/removed
    skill file is picked up (mirrors role_registry()). `skill://<id>` resolves through this."""
    return SkillRegistry().discover([_SKILLS_DIR])


def context_registry() -> ContextRegistry:
    """Discover the file-based context registry (contexts/*.py) — fresh each call (mirrors
    role_registry()). `context://<id>` resolves through this."""
    return ContextRegistry().discover([_CONTEXTS_DIR])


# O2 — the GENERATION-POLICY registry (file-discovered, `generation_policies/*.py`). `run_role` reads
# the SELECTED policy's repetition_penalty LADDER from HERE (registry-is-truth — the rep_penalty is DATA,
# NOTHING static), never a hardcoded constant. Discovered fresh each call (mirrors role_registry()), so a
# dropped-in `generation_policies/<id>.py` is picked up. The default `policy=None` keeps run_role
# BYTE-IDENTICAL to before (no ladder, no penalty, no meta read) — the ladder is OPT-IN by id.
from runtime.generation_policies import GenerationPolicyRegistry  # noqa: E402

_GENERATION_POLICIES_DIR = os.path.join(os.path.dirname(_ROLES_DIR), "generation_policies")


def generation_policy_registry() -> GenerationPolicyRegistry:
    """Discover the file-based generation-policy registry (generation_policies/*.py) — fresh each call
    (mirrors role_registry()). `run_role(policy=<id>)` reads the selected regime's rep_penalty ladder."""
    return GenerationPolicyRegistry().discover([_GENERATION_POLICIES_DIR])


# The spike's three roles, sourced FROM the file-discovered registry (canonical defs in roles/*.py).
# Built at import so the spike's chat_parts_spike/concurrency_probe keep working UNCHANGED, and so a
# missing role file FAILS LOUD at import (never a silently-absent spike role).
_SPIKE_REG = role_registry()
FOCUS_ROLE: Role = _SPIKE_REG["focus"]
RECALL_ROLE: Role = _SPIKE_REG["recall"]
GROUND_ROLE: Role = _SPIKE_REG["ground"]
# the output schema classes, re-exported from the role files for any caller that referenced them.
FocusOut = FOCUS_ROLE.output_schema
RecallOut = RECALL_ROLE.output_schema
GroundOut = GROUND_ROLE.output_schema

SPIKE_ROLES: dict[str, Role] = {FOCUS_ROLE.id: FOCUS_ROLE, RECALL_ROLE.id: RECALL_ROLE,
                                GROUND_ROLE.id: GROUND_ROLE}


# --- the INPUT axis (C): a role's input is DECLARED (input_addresses), resolved through the run:// resolver.
# DEFAULT = today: an absent input_addresses OR exactly ("utterance",) resolves to ctx["utterance"], and the
# GENERATE path frames it BYTE-IDENTICALLY as f"Utterance: {utterance}". Any OTHER declared inputs are resolved
# per-name from ctx (a run:// value resolves via the canonical resolver IF a store is passed) and composed.
def _declared_inputs(role: "Role") -> list:
    """The role's declared input addresses, normalized to a list. Read from role.spec (input_addresses
    lives in the declared dict, not on the dataclass). Absent/empty ⇒ [] (⇒ the default utterance path)."""
    ia = role.spec.get("input_addresses") if hasattr(role, "spec") else None
    return list(ia) if ia else []


def _supplied_extra(role: "Role", ctx: dict, store) -> list:
    """The role's DECLARED non-utterance inputs that the CALLER ACTUALLY SUPPLIED this call — either
    present in `ctx`, or a run:// address resolvable because a `store` was passed. This is the
    behaviour-preservation discriminator: `input_addresses` is DESCRIPTIVE today (roles.py docstring),
    and every CURRENT caller passes only {"utterance": …} — so for them this is [] → the default
    byte-identical path. The compose path is reached ONLY when a future caller supplies the richer
    ctx/store (the run_items usage, deferred). Keying on SUPPLIED (not the descriptive field) is what
    keeps recall/ground/check — which DECLARE extra inputs but are CALLED utterance-only — byte-identical."""
    extras = [a for a in _declared_inputs(role) if a != "utterance"]
    return [a for a in extras
            if (a in ctx) or (isinstance(a, str) and a.startswith("run://") and store is not None)]


def _is_default_input(role: "Role", ctx: dict, store) -> bool:
    """TRUE ⇔ this CALL uses today's default input axis: no SUPPLIED extra declared inputs. The default
    path MUST stay byte-identical to before the op/input axes existed (f"Utterance: {ctx['utterance']}")."""
    return not _supplied_extra(role, ctx, store)


def _resolve_input_value(name: str, ctx: dict, store) -> Any:
    """Resolve ONE declared input by name. A run:// name resolves through the CANONICAL resolver
    (resolve_run_ref — head→get_content; reuse-don't-parallel). Any other name reads ctx[name]
    (bracket access — a missing declared input KeyErrors = fail loud, never a silent empty). A run://
    input with no store RAISES (fail loud — never silently skip a declared addressed input)."""
    if isinstance(name, str) and name.startswith("run://"):
        if store is None:
            raise ValueError(
                f"run_role: declared input {name!r} is a run:// address but no store was passed — "
                f"cannot resolve the addressed input (fail loud, never skip a declared input).")
        return resolve_run_ref(store, name)
    return ctx[name]


def _embed_text_for(role: "Role", ctx: dict, store) -> str:
    """The RAW text an embed role embeds. Default (no SUPPLIED extra inputs) = ctx["utterance"] itself
    (NOT the "Utterance: …" generate-framing — that prefix is a chat artifact, wrong for a vector).
    When extra inputs ARE supplied, the supplied declared inputs are concatenated as "name: value"
    lines (the labelled compose)."""
    if _is_default_input(role, ctx, store):
        return str(ctx["utterance"])
    parts = [f"{name}: {_resolve_input_value(name, ctx, store)}"
             for name in _declared_inputs(role) if name in _supplied_extra(role, ctx, store) or name == "utterance"]
    return "\n".join(parts)


# --- run_role: fire ONE request at the resident 4B (mirrors is_finished_thought's fabric path) ---
def _ensure_embedder_resident(*, evict: bool = False) -> dict:
    """#50 consumer wiring — the OPT-IN deliberate load for an embed role (the embed-op's
    load-on-demand). DELEGATES to the ONE gated capability (ops/cli/capabilities.ensure_resident) —
    no parallel resource-manager here. ops/cli is a bare-import package, so add it to sys.path then
    import (the same way the CLI loads it). Resolves the embedder by its model-id (DEFAULT_EMBED_MODEL)
    so it JOINs to whatever service serves BGE-M3. Raises (EnsureResidentError) if it can't be made
    resident — fail-loud, never a silent half-load. Returns the structured result dict."""
    import sys as _sys
    _ops_cli = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ops", "cli")
    if _ops_cli not in _sys.path:
        _sys.path.insert(0, _ops_cli)
    import capabilities as _cap          # the gated actuator (reuses gpu.py — the one resource-manager)
    from fabric import config as _fcfg
    return _cap.ensure_resident(_fcfg.DEFAULT_EMBED_MODEL, evict=evict)


def run_role(role: Role, ctx: dict, *, base_url: str = RESIDENT_BASE_URL,
             model: str = RESIDENT_MODEL, timeout: int = ROLE_TIMEOUT,
             max_tokens: int = 256, temperature: float = 0.0, store=None,
             ensure: bool = False, ensure_evict: bool = False,
             policy: str | None = None, meta: dict | None = None) -> dict:
    """Fire ONE request at the resident 4B for `role`, returning VALIDATED JSON (a dict).

    Mirrors `Suite.is_finished_thought`/the judge EXACTLY: `client.complete(openai_transport(...))`.
    `json=True` makes the transport set `response_format: {"type": "json_object"}` (verified the
    resident vLLM honours it); `schema=` makes `complete()` parse + validate + retry on a malformed
    role output (client-side enforcement — C1.4/F9). temperature defaults to 0 for routing-stable
    outputs; a JURY's draws (C2.4) pass temperature>0 to get VARIED draws (the draws are intentionally
    varied — C0.2/R2-FOLD H7 scope: it's the VERDICT over them that is deterministic, not the draws).

    `role` is a roles.Role (file-discovered, G2) OR the cognition dataclass Role — both expose
    `.prompt_template`/`.output_schema`/`.id` (duck-compatible; ONE role notion, the G2 superset).

    THE TWO AXES (C — behaviour-preserving):
      * INPUT axis — the role's input is DECLARED (`role.input_addresses`). DEFAULT (absent, or exactly
        `["utterance"]`) is BYTE-IDENTICAL to before: `ctx["utterance"]` framed as `f"Utterance: {…}"`.
        Other declared inputs are resolved per-name from `ctx` (a `run://` name via the canonical
        resolver, IF a `store=` is passed) and composed as labelled lines.
      * OP axis — `role.op` selects the OPERATION. DEFAULT `"generate"` (today's every role) → the exact
        `complete` + `output_schema` + `json=True` path. `"embed"` → the EXISTING `complete_embeddings`
        vector path (reuse — zero new plumbing), returning `{"vector", "dim", "model"}` (LOCAL embedder
        only, no cloud). An embed role needs NO prompt_template/output_schema (it embeds, doesn't generate).

    #50 CONSUMER WIRING (opt-in, behaviour-preserving): `ensure=False` (DEFAULT) keeps the embed-op
    fail-loud-when-down — a down embedder PROPAGATES FabricError, exactly as before (no auto-load, no
    silent degrade). A DELIBERATE caller may pass `ensure=True` to first request the GATED actuator
    (capabilities.ensure_resident — the ONE resource-manager) to make the embedder resident before the
    embed; `ensure_evict=True` additionally authorizes largest-first eviction to make room. ensure only
    affects op="embed". This makes the load a DECLARED, authorized request — never an implicit one.

    GENERATION POLICY (O2 — opt-in, the rep_penalty LADDER from the registry, NOTHING static):
      * `policy=None` (DEFAULT, every current caller) → BYTE-IDENTICAL to before: no repetition_penalty,
        no finish_reason read, ONE complete() call. The ladder is opt-in by id.
      * `policy="<id>"` → look the regime up in the file-discovered GENERATION_POLICY registry
        (generation_policies/<id>.py — registry-is-truth, fail-loud on an unknown id) and run its
        repetition_penalty LADDER: start at `default_rep_penalty`; pass `repetition_penalty=<rung>` into the
        call + read `finish_reason` back via the transport's `meta={}` out-param (O3). On
        `finish_reason=="length"` (a TRUNCATED / degenerate-loop signal), re-call at `next_rep_penalty` (the
        next rung up); EXHAUSTING the ladder → raise FabricError("degenerate-loop …") (fail-loud — never a
        silent give-up; the regime's own contract). The penalty VALUE comes from the registry ladder, never
        a code constant.
      **KNOWN, FLAGGED (cross-lane — `fabric/transport.py` is out of this lane):** the transport's body-build
      copies ONLY `temperature/max_tokens/top_p` into the request (transport.py:92/122) — it does NOT yet
      forward `repetition_penalty`, so the penalty does not reach vLLM until that one-line passthrough lands
      (the coordinate-with-owner follow-up flagged in the lane report). The LADDER LOGIC + the registry-sourced
      value + the finish=length escalation + the fail-loud exhaustion are all real and verifiable here; the
      penalty's EFFECT on the model is gated on that transport edit. `diff_against_source` is read off the
      policy but the output-vs-source diff (catching legitimate-enumeration under-capture) is NOT implemented
      in this pass — flagged NOT-done, never silently ignored.

    O3 — finish_reason / token-count OUT-PARAM (additive, behaviour-preserving): a caller may pass a
    `meta={}` dict to read the completion's `finish_reason` (+ `usage`) back WITHOUT changing the
    returned shape. The transport's `_fill_meta` (fabric/transport.py) populates it on every call when
    `meta` is supplied; the policy-ladder path already used this seam internally (it reads
    `finish_reason=="length"` to escalate). `meta=None` (DEFAULT, every current caller) is BYTE-IDENTICAL
    to before — no meta dict reaches the transport, the request body is untouched, and the return is the
    same `model_dump()` (run_swarm/dry_run_role/run_cascade/the MCP wrapper all depend on that exact
    shape — finish_reason is an OUT-PARAM, NEVER folded into the returned dict). This makes the O3 value
    AVAILABLE at the engine seam; PERSISTING it into the agent-facing `op.run` run-record is the MCP
    wrapper's emit (`mcp_face/server.py` — a different lane; flagged for that owner, not edited here).
    `meta` is read on the DEFAULT (policy=None) path; the policy-LADDER path manages its own finish_reason
    internally (a local `meta` per rung to drive escalation) and does NOT surface it to a `meta=` caller.
    embed-op ignores meta (no completion to read a finish_reason from).

    `ctx` must carry `utterance` for the default input axis. Fail loud: a transport/empty/parse/schema
    failure PROPAGATES as FabricError after retries (never a silent empty dict); a missing/unresolvable
    declared input RAISES (never a silent skip)."""
    op = getattr(role, "op", "generate")

    if op == "embed":
        # The EMBED op (C op-axis) — reuse the EXISTING embed plumbing (suite.py:2980-2983 / nodes/embed.py):
        # openai_embeddings_transport + complete_embeddings, LOCAL resident embedder only (no cloud branch).
        # complete_embeddings is the fail-loud guarded path: a down/empty/dim-mismatch embedder RAISES
        # FabricError after retries — NEVER a silent [] (C law: an embed with no embedder RAISES).
        from fabric import config as _fcfg
        if ensure:
            # OPT-IN deliberate load (#50): make the embedder resident via the gated capability BEFORE
            # the embed. Default (ensure=False) skips this entirely → the existing fail-loud-when-down.
            _ensure_embedder_resident(evict=ensure_evict)
        text = _embed_text_for(role, ctx, store)
        et = transport.openai_embeddings_transport(base_url=_fcfg.DEFAULT_EMBED_URL)
        vecs = client.complete_embeddings(
            et, [text], model=_fcfg.DEFAULT_EMBED_MODEL, dim=_fcfg.DEFAULT_EMBED_DIM)
        vec = vecs[0]
        return {"vector": vec, "dim": len(vec), "model": _fcfg.DEFAULT_EMBED_MODEL}

    # The GENERATE op (default) — BYTE-IDENTICAL to before for a default-input CALL (every current caller).
    if _is_default_input(role, ctx, store):
        user_content = f"Utterance: {ctx['utterance']}"   # identical framing + bracket access (fail-loud)
    else:
        # NET-NEW (never the current callers' path): compose the SUPPLIED declared inputs as labelled
        # lines (utterance included if declared). Reached only when a future caller supplies richer ctx/store.
        compose = [a for a in _declared_inputs(role)
                   if a == "utterance" or a in _supplied_extra(role, ctx, store)]
        user_content = "\n".join(
            f"{name}: {_resolve_input_value(name, ctx, store)}" for name in compose)
    msgs = [
        {"role": "system", "content": role.prompt_template},
        {"role": "user", "content": user_content},
    ]
    t = transport.openai_transport(base_url=base_url, timeout=timeout)
    if policy is None:
        # DEFAULT path — BYTE-IDENTICAL to before for a meta=None caller (ONE complete() call, the same
        # return). Every current caller (run_swarm/dry_run_role/run_cascade/the MCP run_role) passes no
        # meta, so `_complete_kw` carries nothing extra and the request body is untouched. O3: a caller
        # that passes `meta={}` gets finish_reason/usage filled by the transport's _fill_meta — the value
        # rides `**opts` straight through; the body only reads response_format + temperature/max_tokens/
        # top_p, so a stray `meta` key can't pollute the request. OUT-PARAM only — NEVER in the return.
        _complete_kw = {} if meta is None else {"meta": meta}
        validated = client.complete(
            t, msgs, model=model, schema=role.output_schema, json=True,
            temperature=temperature, max_tokens=max_tokens, **_complete_kw,
        )
        return validated.model_dump()

    # O2 LADDER path (opt-in) — the repetition_penalty regime is DATA, read from the file-discovered
    # GENERATION_POLICY registry (NOTHING static). Fail-loud on an unknown id (registry-is-truth).
    pol = generation_policy_registry().policy_for(policy)
    rung = pol.default_rep_penalty                              # the first ladder rung (e.g. 1.1)
    pol_temp = pol.temperature if pol.temperature is not None else temperature
    while True:
        meta: dict = {}                                        # the O3 transport out-param (finish_reason)
        validated = client.complete(
            t, msgs, model=model, schema=role.output_schema, json=True,
            temperature=pol_temp, max_tokens=max_tokens,
            repetition_penalty=rung,                           # FROM the registry ladder — never a constant
            meta=meta,                                         # read finish_reason back to drive escalation
        )
        if meta.get("finish_reason") != "length":
            # clean finish (or an honest None the transport passed through) — accept this draw.
            return validated.model_dump()
        # finish=length → TRUNCATED / degenerate-loop signal: escalate to the next rung.
        nxt = pol.next_rep_penalty(rung)
        if nxt is None:
            # the ladder is EXHAUSTED — fail loud (the regime's own contract; never a silent give-up).
            raise client.FabricError(
                f"degenerate-loop: role {getattr(role, 'id', '?')!r} hit finish_reason=length at the TOP "
                f"of generation-policy {policy!r}'s rep_penalty ladder {pol.rep_penalty_ladder} — the "
                f"output is truncated/looping and the ladder is exhausted. Fail loud (never a silent give-up).")
        rung = nxt                                             # climb the ladder, re-call


# --- SPACE-EMBED (Cognition Engine GROUP L · L1/D2): the corpus capture path PERSISTS embeddings ---
# THE END-TO-END GAP (the SURFACE flagged): run_role(op=embed) PRODUCES a 1024-dim vector but the result
# is never put_vector'd into a SPACE — so the corpus's embedded records never populate a queryable space
# and find_relations (suite.py:9222, the cross-space inversion-finder) has nothing to read end-to-end (its
# own docstring says the item "must be embedded in both spaces first (run the capture+embed pass)" — that
# pass did not exist). This is that pass.
#
# REUSE-DON'T-PARALLEL (the lane law — NO 2nd vector path): the persist is `vector_index.build_index(store,
# corpus, space=<projection>)` — which ALREADY does embed→space-keyed put_vector (vector_index.py:64-139).
# It embeds via `client.complete_embeddings` (the EXACT plumbing run_role(op=embed) uses, cognition.py:274
# ≡ vector_index.py:60-61 — the ONE embed path, not a paralleled one), keys by `store.space_address(item,
# space)` (the SAME key find_relations reads — `space_address(item, near_space)` → get_vector → lines up by
# construction), carries the explicit `space`/`source` fields put_vector requires for the per-space query,
# and gives the content-hash incremental diff + the ONE-round-trip batch + the degrade-with-warning FOR
# FREE. A per-item run_role(op=embed)→put_vector path would REIMPLEMENT all of that (= the parallel path
# the law forbids). The OR-clause in the lane brief ("run_role(op=embed) OR a thin engine path the corpus
# capture uses") sanctions exactly this — and persistence does not belong INSIDE run_role anyway (like
# generate's run_role returns the validated dict and the CALLER persists, embed returns the vector and the
# CAPTURE PATH persists — the run_role(op=embed) return shape stays {vector,dim,model}, untouched).
#
# EMBEDDER-DOWN SEMANTICS (deliberate): build_index's degrade-with-warning IS fail-loud — a down :8001
# emits a LOUD durable `warning` event, writes NOTHING (no silent fabricated/zero vector, never a silent
# []), and returns degraded=True WITHOUT crashing the capture run. This is the sanctioned degrade (chosen
# knowingly): a multi-record/multi-space capture pass should not be aborted whole by a transient embedder
# outage — the loud durable warning is the detectable channel + the records can be re-embedded when :8001
# is up. (The HARD-raise fail-loud lives at the single-embed seam — run_role(op=embed)/complete_embeddings
# — for a deliberate one-shot embed; the capture pass uses the batch path's degrade.)
def embed_corpus_to_spaces(store, records, projections, *, embed_fn=None, dim=None,
                           model=None, base_url=None) -> dict:
    """Embed corpus RECORDS into their PROJECTION SPACES so find_relations / query_index(space=) read them
    end-to-end. THE thin engine path the corpus capture uses (L1/D2) — a pure delegate to STORE's existing
    space-keyed `vector_index.build_index(space=)`, NOT a second vector path.

    `records` = `[{source_address, text, projection}, ...]` — each is one corpus capture under ONE lens
    (`projection`) describing one `source_address` (the item), with the `text` to embed (the lens output).
    `projections` = the EMBEDDABLE projection set (`projection_registry.embeddable()` — registry-is-truth;
    a record whose `projection` is NOT in this set is REFUSED fail-loud, never silently dropped — only a
    lens DECLARED to become a space (`embeds==True`, GROUP L) may be embedded into one).

    Groups the records BY projection (one build_index call per space — the batch the incremental diff +
    one-round-trip cost is O(changed) over), and for each space calls
    `vector_index.build_index(store, [{address: source_address, text}], space=projection)`. The persisted
    key is `store.space_address(source_address, projection)` (build_index owns that — the SAME key
    find_relations reads), carrying `space`/`source` as explicit fields.

    `embed_fn`/`dim`/`model`/`base_url` are the SAME injection seams build_index exposes — a test injects
    SEEDED vectors (embedder-down / deterministic) exactly as conv_index_space_acceptance does; the live
    default is `complete_embeddings`.

    FAIL LOUD: a record missing `source_address`/`text`/`projection`, or naming a non-embeddable projection,
    RAISES before any write (rule 4 — an unembeddable record is a misconfiguration, never a silent skip).
    A DOWN embedder degrades-with-warning per space (build_index's sanctioned loud degrade — see the module
    note above), reflected in the per-space result.

    Returns `{spaces: {<projection>: {embedded, skipped, degraded}}, records: N, degraded: bool}` — the
    per-space build result + an aggregate `degraded` (True iff ANY space degraded). The FLOOR holds:
    put_vector is a store WRITE, never a resolve/approve/dispatch; this emits no engine run-record."""
    from store import vector_index as _vx              # the EXISTING space-keyed embed→put_vector (reuse)

    embeddable_ids = {p.id for p in projections}        # registry-is-truth (the declared space set)
    by_space: dict[str, list] = {}
    for rec in records:
        src = rec.get("source_address")
        text = rec.get("text")
        proj = rec.get("projection")
        if not src or not isinstance(src, str):
            raise ValueError(
                f"embed_corpus_to_spaces: a record needs a string `source_address` (the item the vector is "
                f"keyed to — what find_relations queries). Got {src!r} in {rec!r} — fail loud.")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(
                f"embed_corpus_to_spaces: a record needs non-empty `text` to embed (the lens output). "
                f"Got {text!r} for source_address {src!r} — fail loud (never embed an empty string).")
        if not proj or proj not in embeddable_ids:
            raise ValueError(
                f"embed_corpus_to_spaces: record for {src!r} names projection {proj!r}, which is not an "
                f"EMBEDDABLE space (the embeddable set is {sorted(embeddable_ids)} — embeds==True, GROUP L). "
                f"Only a lens declared to become a space may be embedded into one — fail loud, never a "
                f"silent drop. (registry-is-truth, AGENTS.md rule 8.)")
        by_space.setdefault(proj, []).append({"address": src, "text": text})

    # build_index defaults embed_fn=_default_embed (the live complete_embeddings); only pass embed_fn when
    # a caller INJECTS one (seeded/embedder-down) — passing None would override that default with None.
    bi_kw = {"dim": dim, "model": model, "base_url": base_url}
    if embed_fn is not None:
        bi_kw["embed_fn"] = embed_fn
    spaces: dict[str, dict] = {}
    any_degraded = False
    for proj in sorted(by_space):                       # deterministic per-space order
        res = _vx.build_index(store, by_space[proj], space=proj, **bi_kw)
        spaces[proj] = res
        any_degraded = any_degraded or bool(res.get("degraded"))
    return {"spaces": spaces, "records": len(records), "degraded": any_degraded}


# --- the DECLARED RULE (L2): a NON-TRIVIAL pure function of resolved values (C0.2 / R1-FOLD F5) ---
# DECLARED inputs of this rule (the referenceable-input whitelist): the resolved `recall` AND `ground`
# role outputs — TWO roles that fire CONCURRENTLY and finish in NONDETERMINISTIC order. The rule reads
# MULTIPLE fields across BOTH (recall.relevant, ground.in_scope, recall.snippet, ground.note) — not a
# one-liner — and is the exact case F5 hardens: it must NOT depend on which sibling finished first.
RULE_INPUTS = ("recall", "ground")


# G3 GENERALIZATION (the L2 core): the spike's hand-written `injection_rule` Python is now a DECLARED
# DATA-AST rule interpreted by the restricted evaluator in runtime/rules.py (NEVER eval/exec). The
# condition `recall.relevant AND ground.in_scope` is the declared op-tree below; the spike's behaviour
# is preserved by DELEGATION (reuse-don't-parallel) — `injection_rule` now calls the rule engine, and
# tests/rules_acceptance.py proves the declared rule evaluates IDENTICALLY to the old hand-written one.
# The G0 spike's chat_parts_spike/C0.2 replay-identical stay green (the rule reads the same two resolved
# fields, deterministically). This is C3.1: the hand-written rule becomes the first DECLARED rule.
from runtime import rules as _rules  # noqa: E402  (the G3 rule engine — the declared-AST evaluator)

# The declared condition AST for the spike injection rule (recall.relevant AND ground.in_scope):
INJECTION_RULE_AST: dict = {
    "op": "and",
    "args": [
        {"op": "field", "path": "recall.relevant"},
        {"op": "field", "path": "ground.in_scope"},
    ],
}
# The declared Rule (validated at build — the commit-time static walk). destination=inject (C3.2);
# params.value_path names the routed value (the recalled snippet). on_missing=raise (fail loud — a
# missing declared input never routes; never gate.py's implicit-truthy).
INJECTION_RULE = _rules.build_rule({
    "id": "recall-injects",
    "label": "recall.relevant AND ground.in_scope",
    "when": INJECTION_RULE_AST,
    "destination": "inject",
    "params": {"value_path": "recall.snippet"},
    "on_missing": "raise",
})


def injection_rule(resolved: dict) -> dict:
    """The routing RULE for Part 2 — now a DECLARED DATA-AST rule (G3), evaluated by the restricted
    rule engine (runtime/rules.py). PURE function of the RESOLVED `recall` AND `ground` values.

    LOGIC (multi-field, F5): INJECT the recalled snippet iff `recall.relevant AND ground.in_scope`.
    Reads multiple fields across BOTH roles' resolved outputs. Generalized from hand-written Python
    into the declared AST `INJECTION_RULE` (C3.1) — proven identical in tests/rules_acceptance.py.

    DETERMINISM (C0.2 / R1-FOLD F5): the evaluator reads ONLY fully-resolved address values from the
    declared whitelist — NO now()/random/wave-completion-order/partial-results/model-call (those ops
    are not in the grammar). So identical resolved inputs route identically regardless of finish order.

    FAIL LOUD (C0.4 / R2-FOLD H2): a missing declared input RAISES (rules.RuleError) — never implicit-
    truthy-on-missing. (KeyError-compatible: RuleError is raised, the spike's callers treat any raise
    as fail-loud.)

    Returns the spike's routing-decision shape: {inject: bool, snippet: str|None, reason: str} —
    derived from the rule engine's decision (so the spike's chat_parts_spike is UNCHANGED)."""
    # the engine raises RuleError on a missing declared input (fail loud, on_missing=raise)
    decision = INJECTION_RULE.decide(resolved)
    fire = bool(decision["fire"])
    if fire:
        return {"inject": True, "snippet": decision["value"],
                "reason": "recall.relevant AND ground.in_scope"}
    rec = resolved["recall"]
    grd = resolved["ground"]
    return {"inject": False, "snippet": None,
            "reason": f"recall.relevant={bool(rec.get('relevant'))} ground.in_scope={bool(grd.get('in_scope'))}"}


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


# =================================================================================================
# G1 — THE NODE-MECHANISM SUBSTRATE (productionizes the G0 spike mechanism above).
#
# The spike PROVED the mechanism (run_role · run:// injection · pure rules). G1 productionizes it
# into the real concurrent substrate — but it is STILL the COGNITION DRIVER, not the shared
# scheduler (R1-FOLD F2, CRITICAL): all parallelism lives HERE, leaving runtime/scheduler.py:run()
# strictly serial so the app's Suite.run behaviour is UNCHANGED ("one substrate, two drivers").
#
#   C1.1  concurrent dispatch in the DRIVER: materialize a ready-set → dispatch the wave via a
#         ThreadPoolExecutor → barrier per wave → serialize store writes behind the barrier.
#   C1.2  slot budget from REAL registry values: min(max_num_seqs − R, free_KV / per_role_ctx),
#         read from ops/services.json (NEVER a hardcoded 32). A global VramGate semaphore + a
#         swarm sub-pool of (knee − R) keeps R slots for the main stream/judge.
#   C1.3  the injection ref-read: a part reads a role's resolved output at run://<turn>/<role> via
#         the store's canonical head→get_content resolver (NO parallel resolver). run:// only.
#   C1.4  output_schema enforced: run_role already passes schema= into complete()'s validate/retry.
#   C1.6  telemetry batched: ONE rollup per wave (containing each role's run-record), not one
#         store write per role-fire — does NOT fsync-flood append_event.
# =================================================================================================


# --- C1.2: the slot budget, derived from the LIVE registry (never a hardcoded 32) ---------------
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SERVICES_JSON = os.path.join(_REPO_ROOT, "ops", "services.json")

# Defaults are the C0.5-MEASURED reality of the resident config (2026-06-07), used ONLY as a
# fail-loud-avoiding fallback if a registry field is genuinely absent — NOT a hardcoded budget.
# The budget is COMPUTED from these registry values; nothing here assumes 32.
DEFAULT_RESERVE_R = 2            # R: slots reserved for the main stream/judge (R2-FOLD H1)
DEFAULT_ROLE_CTX_TOKENS = 1500   # per-role context budget ~1–2K (R2-FOLD H1)
# KV pool tokens by util (C0.5 measured); read live if the registry exposes it, else this map.
_MEASURED_KV_BY_UTIL = {0.49: 66036, 0.63: 135574}


@dataclass
class SlotBudget:
    """The request-concurrency budget for a swarm wave, COMPUTED from registry values (C1.2 / F1).

    knee          = min(max_num_seqs − R, free_KV // per_role_ctx)   — the swarm concurrency cap.
    swarm_slots   = max(1, knee)                                     — the swarm sub-pool width.
    reserve_r     = R                                                — kept for the main stream/judge.
    Everything is DERIVED from the live `chat-4b` service config (max_num_seqs, gpu_util) — NEVER a
    literal 32 (R1-FOLD F1). Fail loud only on a corrupt registry; an absent optional field falls
    back to the C0.5-measured value, labelled in `source`."""
    max_num_seqs: int
    reserve_r: int
    per_role_ctx: int
    kv_pool_tokens: int
    main_ctx_tokens: int          # how much KV the main conversation is assumed to hold this turn
    swarm_slots: int
    source: dict

    @classmethod
    def from_registry(cls, *, service_id: str = "chat-4b", reserve_r: int = DEFAULT_RESERVE_R,
                      per_role_ctx: int = DEFAULT_ROLE_CTX_TOKENS, main_ctx_tokens: int = 0,
                      services_path: str = _SERVICES_JSON) -> "SlotBudget":
        """Read the LIVE registry (ops/services.json) and COMPUTE the slot budget. `main_ctx_tokens`
        is how deep the main conversation is THIS turn (it eats the shared KV pool — the deep-main
        bind C0.5 found); 0 = shallow main. Fail loud (FileNotFoundError/KeyError) on a corrupt
        registry — never a silent guessed budget."""
        with open(services_path) as f:
            reg = json.load(f)
        svcs = reg["services"] if "services" in reg else reg
        if service_id not in svcs:
            raise KeyError(
                f"SlotBudget.from_registry: no service {service_id!r} in {services_path} — "
                f"cannot derive the slot budget from the registry (fail loud, never assume 32).")
        cfg = svcs[service_id].get("config") or {}
        if "max_num_seqs" not in cfg:
            raise KeyError(
                f"SlotBudget.from_registry: service {service_id!r} declares no max_num_seqs — "
                f"the seq-cap bind is unknown (fail loud).")
        max_num_seqs = int(cfg["max_num_seqs"])
        util = float(cfg.get("gpu_util", 0.49))
        # KV pool: prefer a registry-declared measured value, else the C0.5 map, else derive from the
        # _profile (kv_kb_per_token) if present — all REGISTRY-grounded, never invented.
        kv_pool = None
        prof = cfg.get("_profile") or {}
        if "kv_pool_tokens" in cfg:
            kv_pool = int(cfg["kv_pool_tokens"])
            kv_src = "registry.config.kv_pool_tokens"
        elif round(util, 2) in _MEASURED_KV_BY_UTIL:
            kv_pool = _MEASURED_KV_BY_UTIL[round(util, 2)]
            kv_src = f"C0.5-measured @util {round(util, 2)}"
        else:
            # last resort: a coarse estimate from the profile, clearly labelled. Never silent.
            kv_pool = _MEASURED_KV_BY_UTIL[0.49]
            kv_src = "fallback C0.5 @0.49 (util not in measured map)"
        free_kv = max(0, kv_pool - max(0, int(main_ctx_tokens)))
        kv_bound = free_kv // max(1, int(per_role_ctx))
        seq_bound = max_num_seqs - reserve_r
        knee = min(seq_bound, kv_bound)
        swarm_slots = max(1, knee)
        return cls(
            max_num_seqs=max_num_seqs, reserve_r=reserve_r, per_role_ctx=per_role_ctx,
            kv_pool_tokens=kv_pool, main_ctx_tokens=int(main_ctx_tokens), swarm_slots=swarm_slots,
            source={"service": service_id, "gpu_util": util, "kv_source": kv_src,
                    "seq_bound": seq_bound, "kv_bound": kv_bound, "knee": knee,
                    "services_path": services_path},
        )


# A PROCESS-WIDE VRAM gate (C1.2): the global semaphore that bounds concurrent LOCAL model calls so
# the swarm can never starve the main stream of the shared resident pool. It is a singleton (created
# ONCE, module-level) — a per-call VramGate would cap nothing (advisor flag). The swarm acquires its
# OWN sub-pool (knee − R) so R slots ALWAYS remain free for a main-stream/judge call to acquire
# immediately. Both bound the SAME resident pool. fabric/vram.py:VramGate was unwired before G1.
_GLOBAL_VRAM_GATE: VramGate | None = None
_GLOBAL_VRAM_LOCK = threading.Lock()


def global_vram_gate(limit: int) -> VramGate:
    """The process-wide VramGate singleton sized to the registry knee. Created once; subsequent
    calls return the same gate (the limit is fixed at first creation — the resident config is fixed
    while up). This is the ONE gate every local model call passes (main stream + swarm both)."""
    global _GLOBAL_VRAM_GATE
    with _GLOBAL_VRAM_LOCK:
        if _GLOBAL_VRAM_GATE is None:
            _GLOBAL_VRAM_GATE = VramGate(limit=max(1, limit))
        return _GLOBAL_VRAM_GATE


# --- C1.3: the injection ref-read (the store's canonical resolver — NO parallel resolver) --------
def resolve_run_ref(store, addr: str, *, on_missing: str = "raise") -> Any:
    """Read the RESOLVED value at a role's run:// address — the net-new injection ref-read (C1.3).

    This is the canonical store resolution path (head → get_content), NOT a second resolver: the
    store's head→get_content IS the system's resolver (R1-FOLD F3 retracted "promote
    context_variables.py" — that module is test-only/dead and reads operator-notebook strata, not
    fresh role refs). A later reply part calls this to inject a role's output into its context.

    Addressing is run:// ONLY (never swarm:// — not a registered scheme, contracts/address.py).
    Fail loud (C9.3 / R2-FOLD H2): a missing/unresolved ref RAISES unless a declared on_missing
    handler is given — NEVER implicit-truthy-on-missing (that would couple routing to timing)."""
    if not addr.startswith("run://"):
        raise ValueError(
            f"resolve_run_ref: address {addr!r} is not a run:// address — the injection edge reads "
            f"run://<turn>/<role> ONLY (never swarm://; contracts/address.py SCHEMES).")
    cas = store.head(addr)
    if cas is None:
        if on_missing == "raise":
            raise RuntimeError(
                f"resolve_run_ref: {addr} did not resolve (head() is None) — fail loud, never route "
                f"or inject on an unresolved ref. (Declare on_missing to handle a pruned ref.)")
        return None
    return store.get_content(cas)


# --- C 3/4: the SCHEME-DISPATCHING address resolver (the input-address INTENT — Tim, 2026-06-08) --
# A SENTINEL the dispatcher returns for a BARE NAME (no "://" — e.g. "utterance", "notes"): a bare name
# is NOT an address, it is a ctx KEY the caller reads from the supplied context. Distinct object (an
# `is`-comparison, never a falsy/None confusion) so a caller can tell "this is a ctx-key, go read ctx"
# apart from a legitimately-resolved None.
class _BareName:
    __slots__ = ()
    def __repr__(self): return "<BARE_NAME: read from ctx>"
BARE_NAME = _BareName()


def resolve_address(store, addr: str, *, turn_id: str | None = None,
                    on_missing: str = "raise") -> Any:
    """Resolve CONTENT FROM ANY ADDRESS — the scheme-dispatching resolver (C 3/4, the input-address
    INTENT: a role's input can be "any skill, any context, or the output of anything else, set by
    address"). This is the EXTENSIBLE SEAM: it DISPATCHES by address scheme to the existing per-scheme
    resolvers — it does NOT build a parallel resolver (reuse-don't-parallel).

    Resolution path:
      1. MATERIALIZE templates first — substitute `<turn>` → `turn_id` in `addr` (so a declared
         `run://<turn>/part-1` becomes `run://<turn_id>/part-1` BEFORE any scheme dispatch). A `<turn>`
         template with no `turn_id` RAISES (fail loud — never dispatch an unmaterialized template, which
         would resolve the literal "<turn>" path and miss).
      2. DISPATCH by `contracts.address.scheme(addr)`:
           run://     → the EXISTING canonical resolver `resolve_run_ref` (head→get_content; REUSE).
           cas://     → the EXISTING immutable-content read `store.get_content(addr)` (cas:// IS get_content).
           skill://   → `runtime/skills.py:SkillRegistry.read(id)` — the skill's declared instructions
                        content (C 3b — file-discovered, registry-is-truth). An UNKNOWN id RAISES fail-loud.
           context:// → `runtime/skills.py:ContextRegistry.read(id)` — the context's declared content
                        blob (C 3b). An UNKNOWN id RAISES fail-loud (never fabricate a missing context).
      3. A BARE NAME (no "://" at all — e.g. "utterance", "notes") is NOT an address: return the
         `BARE_NAME` sentinel so the CALLER reads it from the supplied ctx (bare names are ctx keys).
      4. ANY OTHER scheme — a REGISTERED scheme with no content-resolver yet (blob:// vec:// ui:// code://)
         OR an UNREGISTERED scheme (foo://) — RAISES fail-loud: there is no content-resolver for it TODAY.
         NEVER a silent empty. This RAISE is the extensible seam: when a resolver exists, add a dispatch
         branch here (and that scheme stops raising) — exactly as skill://+context:// just did (C 3b).

    SCOPE (C 3b — the seam's FIRST real extension): skills + contexts ARE addressed now —
    `resolve_address` resolves `run://` (an upstream output) + `cas://` (a content blob) + `skill://`
    (a reusable instructions unit) + `context://` (a reusable context blob). It remains the ONE place
    the next resolver (a `vec://` k-NN read, a `blob://` binary read) plugs in LATER; until then those
    schemes fail loud here — the seam is declared, not faked. The input-address INTENT (a role's input
    = any skill, any context, or any upstream output, set by address) is now fully realised.

    `on_missing` is passed through to `resolve_run_ref` for run:// (a declared "skip" returns None on a
    pruned ref; default "raise" fail-louds). Fail loud everywhere else."""
    if not isinstance(addr, str):
        raise TypeError(f"resolve_address: address must be a str, got {type(addr).__name__} — fail loud.")
    # 1. MATERIALIZE the <turn> template FIRST (before any scheme dispatch).
    if "<turn>" in addr:
        if not turn_id:
            raise ValueError(
                f"resolve_address: address {addr!r} carries a <turn> template but no turn_id was "
                f"passed — cannot materialize the address (fail loud, never dispatch an unmaterialized "
                f"template that would resolve the literal '<turn>' path and miss).")
        addr = addr.replace("<turn>", turn_id)
    # 2/3/4. DISPATCH by scheme. NOTE: scheme() returns None for BOTH a bare name AND an unregistered
    # scheme (skill:// — not in SCHEMES) — so we MUST discriminate on "://", not on scheme()==None
    # (else skill://foo would wrongly return the ctx-read sentinel instead of failing loud).
    sch = _scheme(addr)
    if sch == "run":
        return resolve_run_ref(store, addr, on_missing=on_missing)        # REUSE the canonical resolver
    if sch == "cas":
        return store.get_content(addr)                                    # REUSE: cas:// IS get_content
    if sch == "skill":
        # C 3b — skill://<id> → the skill's declared instructions content (file-discovered registry).
        # read() FAIL-LOUDs on an unknown id (registry-is-truth — never fabricate a missing skill).
        # NAMED .read (not .resolve): a registry read is the floor, and the cognition layer keeps
        # `.resolve(` a forbidden-only token (the C9.2 source-invariant).
        return skill_registry().read(addr[len("skill://"):])
    if sch == "context":
        # C 3b — context://<id> → the context's declared content blob (file-discovered registry).
        return context_registry().read(addr[len("context://"):])
    if sch is not None:
        # a REGISTERED scheme (blob/vec/ui/code) with no content-resolver wired into this dispatcher yet.
        raise ValueError(
            f"resolve_address: scheme {sch!r} not content-resolvable yet (address {addr!r}) — "
            f"run:// + cas:// + skill:// + context:// resolve to content today (extensible: add a "
            f"{sch}:// resolver branch here). Fail loud, NEVER a silent empty.")
    if "://" in addr:
        # an UNREGISTERED scheme (foo://) — not in contracts.address.SCHEMES, no resolver. The seam's
        # future home for a new declared scheme (skill://+context:// graduated from here in C 3b).
        bad = addr.split("://", 1)[0]
        raise ValueError(
            f"resolve_address: scheme {bad!r} not content-resolvable yet (address {addr!r}) — it is not "
            f"a registered scheme (contracts.address.SCHEMES) and has no resolver. run:// + cas:// + "
            f"skill:// + context:// resolve now; this is the EXTENSIBLE seam where a {bad}:// resolver "
            f"plugs in when the scheme exists. Fail loud, NEVER a silent empty.")
    # a BARE NAME (no "://") — not an address; the caller reads it from the supplied ctx.
    return BARE_NAME


# --- C1.1 + C1.2 + C1.6: the concurrent swarm wave -----------------------------------------------
@dataclass
class RoleRun:
    """One role's run-record in a wave — the unit the C1.6 batched rollup contains (G7 will render)."""
    role_id: str
    address: str
    ok: bool
    ms: int
    error: str | None = None


@dataclass
class WaveResult:
    """The captured artifact of one concurrent wave (the proof C1.1/C1.6 read)."""
    turn_id: str
    resolved: dict = field(default_factory=dict)        # role_id -> resolved value (read BACK via run://)
    addresses: dict = field(default_factory=dict)       # role_id -> run:// address
    runs: list = field(default_factory=list)            # list[RoleRun] (per-role records)
    finish_order: list = field(default_factory=list)    # the order roles FINISHED (nondeterministic)
    wall_s: float = 0.0
    sum_role_s: float = 0.0                              # sum of role latencies (for the max-vs-sum proof)
    budget: dict = field(default_factory=dict)


def run_swarm(roles: list, ctx: dict, store, *, turn_id: str,
              budget: "SlotBudget | None" = None,
              emit: Callable[[str, dict], None] | None = None,
              base_url: str = RESIDENT_BASE_URL, model: str = RESIDENT_MODEL,
              max_tokens: int = 256) -> WaveResult:
    """Dispatch a WAVE of independent role-runs CONCURRENTLY (C1.1), bounded by the registry slot
    budget (C1.2), each writing its validated JSON to its own run://<turn>/<role> address; JOIN at
    the wave barrier; read every role's resolved value BACK via the canonical resolver (C1.3); emit
    ONE batched rollup containing every role's run-record (C1.6).

    This is the cognition DRIVER — the concurrency lives HERE, not in scheduler.py (F2). It fires the
    EXISTING blocking transport on pool threads (the GIL releases on socket I/O; vLLM batches
    server-side) — NO async/httpx. Store writes (put_content/set_ref per role) are individually
    atomic AND each role writes a DISTINCT address (no shared key) → no write race; the rollup +
    the read-back happen AFTER the barrier (serialized). N independent roles finish in ~max(role)
    not ~sum(role).

    `roles` = list[Role] (declared data). `ctx` carries `utterance`. `budget` = SlotBudget (the
    swarm sub-pool width = budget.swarm_slots; if None, derived from the live registry). `emit` =
    an optional ONE-arg-per-call sink (kind, payload) — the Suite's _emit/append_event seam.
    Fail loud: a role's failure is captured per-RoleRun AND re-raised after the barrier (the wave
    cannot silently lose a role)."""
    if budget is None:
        budget = SlotBudget.from_registry()
    # The GLOBAL gate is sized to the FULL resident seq-cap (max_num_seqs) — NOT seq-cap−R. The
    # reservation comes from the SWARM POOL being capped at swarm_slots (= max_num_seqs − R) below:
    # the swarm can hold at most swarm_slots gate permits, so R permits ALWAYS remain free for a
    # concurrent main-stream/judge call to acquire immediately (it never queues behind the swarm).
    # (Sizing the gate to seq-cap−R AND the pool to swarm_slots would leave ZERO headroom — the bug
    # the C1.2 reserved-slot invariant forbids.)
    gate = global_vram_gate(budget.max_num_seqs)
    # C1.1 — MATERIALIZE THE READY-SET (the scheduler is a re-scanning loop with no ready-set; the
    # driver builds one). A role is "ready" iff its declared inputs are available — here every role
    # in `roles` reads only `ctx.utterance` (independent), so the whole list is the ready-set. (When
    # roles gain inter-role deps, ready-set = roles whose run:// deps already resolved — same shape.)
    ready_set = list(roles)
    addresses = {r.id: f"run://{turn_id}/{r.id}" for r in ready_set}
    result = WaveResult(turn_id=turn_id, addresses=addresses,
                        budget={"swarm_slots": budget.swarm_slots, "reserve_r": budget.reserve_r,
                                "knee": budget.source.get("knee"), "source": budget.source})
    runs: dict = {}
    finish_lock = threading.Lock()

    def _one(role: Role) -> RoleRun:
        t0 = time.monotonic()
        # The swarm acquires the GLOBAL gate but is itself bounded to swarm_slots by the pool's
        # max_workers (knee − R) — so R slots of the gate stay free for a main-stream call.
        with gate.slot():
            out = run_role(role, ctx, base_url=base_url, model=model, max_tokens=max_tokens)
            cas = store.put_content(out)              # immutable content (write-once)
            store.set_ref(addresses[role.id], cas)    # the run:// pointer (atomic set_ref)
        ms = int((time.monotonic() - t0) * 1000)
        rr = RoleRun(role_id=role.id, address=addresses[role.id], ok=True, ms=ms)
        with finish_lock:
            result.finish_order.append(role.id)
        return rr

    wall0 = time.monotonic()
    errors: list[BaseException] = []
    # C1.1/C1.2 — dispatch the wave via a ThreadPoolExecutor sized to the SWARM SUB-POOL (knee − R).
    # max_workers caps in-flight role-runs at the budget; the global gate is the cross-driver bound.
    if ready_set:
        with ThreadPoolExecutor(max_workers=budget.swarm_slots,
                                thread_name_prefix=f"swarm-{turn_id}") as pool:
            futs = {pool.submit(_one, r): r for r in ready_set}
            for fut in as_completed(futs):            # the BARRIER: every role joined before we proceed
                role = futs[fut]
                try:
                    runs[role.id] = fut.result()
                except BaseException as e:            # capture per-role; re-raise after the barrier
                    runs[role.id] = RoleRun(role_id=role.id, address=addresses[role.id],
                                            ok=False, ms=0, error=f"{type(e).__name__}: {e}")
                    errors.append(e)
    result.wall_s = round(time.monotonic() - wall0, 3)
    result.runs = [runs[r.id] for r in ready_set]
    result.sum_role_s = round(sum(rr.ms for rr in result.runs) / 1000.0, 3)

    # C1.6 — ONE BATCHED ROLLUP per wave (NOT one append_event per role-fire). Contains EVERY role's
    # run-record (so G7's render still has them) — batch the fsync, never drop the data (advisor flag).
    if emit is not None:
        emit("cognition.wave", {
            "turn_id": turn_id, "n_roles": len(result.runs),
            "wall_s": result.wall_s, "sum_role_s": result.sum_role_s,
            "finish_order": result.finish_order,
            "budget": result.budget,
            "roles": [{"role": rr.role_id, "address": rr.address, "ok": rr.ok,
                       "ms": rr.ms, **({"error": rr.error} if rr.error else {})}
                      for rr in result.runs],
        })

    # Fail loud AFTER the rollup (so the failure is recorded) — the wave cannot silently lose a role.
    if errors:
        raise errors[0]

    # C1.3 — read every role's resolved value BACK via the canonical resolver (head→get_content),
    # AFTER the barrier (serialized). This is the value a later part injects. Fail loud on a missing ref.
    for rid, addr in addresses.items():
        result.resolved[rid] = resolve_run_ref(store, addr)
    return result


# =================================================================================================
# C 3/4 — run_items: the AXIS-INVERSION (1 role × N units) — makes input_addresses OPERATIONAL.
#
# run_swarm fans N DIFFERENT roles over 1 shared ctx (N roles × 1 ctx). run_items INVERTS the axis: it
# fans ONE role over N input-UNITS (1 role × N units) — each unit becomes that role's primary input
# (CORPUS-CHAIN §MAP: "run_swarm fans N roles × 1 ctx; the map needs 1 role × N units"). This is the
# map half of the corpus-chain, and the operational form of the input-address INTENT: a unit is either a
# LITERAL value OR an ADDRESS (resolved via resolve_address — run:// an upstream output, cas:// a blob).
#
# It MIRRORS run_swarm's fan (reuse-don't-fork): the SAME global VramGate, the SAME swarm sub-pool width
# (budget.swarm_slots), the SAME per-unit fail-loud + barrier re-raise, the SAME ONE batched emit rollup.
# It is a DRIVER (the model runs only in the role, via run_role); it emits NO resolve/approve/dispatch
# (the operator-only floor). It does NOT fire any reduce — it only MAPs (the cross-unit JOIN is run_reduce).
#
# Additive: nothing calls run_items yet; run_swarm/run_jury/run_role/the cast/chat_parts are byte-identical.
# =================================================================================================
@dataclass
class ItemsResult:
    """The captured artifact of one run_items fan (1 role × N units) — mirrors WaveResult.

    addresses    {i: run://<turn>/<role>/<i>}  — the per-unit output address (positional index).
    resolved     {i: value}                    — each OK unit's role output, read BACK via the resolver.
    runs         list[RoleRun]                 — the per-unit OK run-records (the batched-rollup unit).
    finish_order list[int]                     — the order units FINISHED (nondeterministic — the fan).
    skipped      list[(i, reason)]             — units DECLARED-skipped (on_missing="skip" — never silent).
    failed       list[(i, error)]              — units that ERRORED in run_role (F2 per-unit resilience):
                                                 a poison unit lands HERE (never a silent drop), and the
                                                 GOOD units' outputs STILL return in .runs/.resolved. A
                                                 failed unit's address was never set_ref'd, so it is kept
                                                 OUT of .runs/.resolved (the read-back reads OK addresses
                                                 only). NOTE: this is a PROCESSING failure (run_role raised
                                                 on a resolved unit) — distinct from a RESOLUTION failure
                                                 (an unresolvable run:// address under on_missing="raise"),
                                                 which STILL fails the whole fan loud (the address contract).
    """
    turn_id: str
    role_id: str
    addresses: dict = field(default_factory=dict)
    resolved: dict = field(default_factory=dict)
    runs: list = field(default_factory=list)
    finish_order: list = field(default_factory=list)
    skipped: list = field(default_factory=list)
    failed: list = field(default_factory=list)
    wall_s: float = 0.0
    sum_unit_s: float = 0.0


def run_items(role: "Role", items: list, store, *, turn_id: str,
              ctx: dict | None = None,
              budget: "SlotBudget | None" = None,
              on_missing: str = "raise",
              emit: "Callable[[str, dict], None] | None" = None,
              base_url: str = RESIDENT_BASE_URL, model: str = RESIDENT_MODEL,
              max_tokens: int = 256, temperature: float = 0.0) -> ItemsResult:
    """Fan ONE `role` over N input-UNITS (1 role × N units) — the AXIS-INVERSION of run_swarm (C 3/4).

    `items` = the N input-units. Each unit is EITHER:
      * an ADDRESS (a str containing "://": run:// an upstream output, cas:// a content blob) — RESOLVED
        via `resolve_address` (which materializes the `<turn>` template against `turn_id` + fail-louds on
        a not-content-resolvable scheme), OR
      * a LITERAL value (anything else — a plain string / dict) — used as-is.
    The resolved/literal unit becomes the role's PRIMARY input: it is placed at `ctx["utterance"]`, so a
    "utterance"-reading role (today's every fireable role) takes run_role's DEFAULT byte-identical path.

    `ctx` (optional) is a SHARED context for the role's DECLARED EXTRA inputs (the bare-name input_addresses
    beyond "utterance" — e.g. a role declaring input_addresses=("utterance","memory") reads ctx["memory"]).
    Mirrors run_swarm's single shared ctx (not per-unit dicts — no plumbing the proof doesn't exercise).
    NOTE: run_items does NOT point at a role's TEMPLATED run:// input_addresses (e.g. check.py's
    "run://<turn>/part-1") — that forming-answer chaining is the G3/G4 chainer's job; run_items materializes
    the <turn> template on the ITEMS axis (the units), the addressed axis it owns.

    For EACH unit (CONCURRENTLY — the SAME bounded pool + global VramGate + barrier as run_swarm): resolve
    the unit → build the per-unit ctx (the unit at "utterance" + the shared ctx's extra inputs) → fire
    run_role(role, ctx, store=store, ...) → write the validated output to `run://<turn>/<role>/<i>`
    (put_content → set_ref, exactly like run_swarm). JOIN at the barrier; read every unit's output BACK
    via the canonical resolver; emit ONE batched `cognition.items` rollup.

    F2 — PER-UNIT RESILIENCE (the batch is not all-or-nothing). Two DISTINCT failure points, handled
    differently (the address contract vs. processing resilience):
      * RESOLUTION failure — a unit that is a run:// address which does NOT resolve. Under the default
        on_missing="raise" this RAISES (via resolve_address) and FAILS THE WHOLE FAN LOUD — the address
        contract is unchanged (an unresolvable declared input is a fatal misconfiguration, not a flaky
        unit). A DECLARED on_missing="skip" instead RECORDS it in .skipped (returned so the caller sees
        what was dropped), NEVER a silent drop.
      * PROCESSING failure — a unit that RESOLVED fine but whose run_role RAISED (e.g. an over-context
        file → a 400, a transient model error). This unit goes to .failed (recorded, never silent) and
        the GOOD units' outputs STILL return in .runs/.resolved. The fan no longer discards the whole
        batch for one poison unit. A failed unit's address was never set_ref'd, so it is kept OUT of
        .runs/.resolved (the after-barrier read-back reads OK addresses only — never an unset address).

    A DRIVER, not an agent: the model runs only inside the role; run_items emits no resolve/approve/dispatch
    (the operator-only floor). Returns an ItemsResult (the by-use artifact)."""
    if not role.can_fire:
        raise ValueError(
            f"run_items: role {role.id!r} cannot fire (no prompt_template/output_schema, and not op=embed) "
            f"— run_items maps a FIREABLE role over N units. Fail loud.")
    if budget is None:
        budget = SlotBudget.from_registry()
    shared_ctx = dict(ctx or {})
    gate = global_vram_gate(budget.max_num_seqs)

    # the per-unit OUTPUT addresses are POSITIONAL — run://<turn>/<role>/<i> (a distinct address per unit,
    # like run_swarm's per-role addresses → no shared key → no write race).
    addresses = {i: f"run://{turn_id}/{role.id}/{i}" for i in range(len(items))}
    result = ItemsResult(turn_id=turn_id, role_id=role.id, addresses=dict(addresses))
    runs: dict = {}
    finish_lock = threading.Lock()
    skipped: dict = {}                                       # i -> reason (declared skip, never silent)
    failed: dict = {}                                        # i -> error (F2 processing failure, never silent)

    class _ResolutionError(Exception):
        """Marks a RESOLUTION failure (an unresolvable run:// unit under on_missing="raise") — distinct
        from a PROCESSING failure (run_role raised on a resolved unit). A resolution failure is FATAL to
        the whole fan (the address contract: an unresolvable declared input is a misconfiguration, not a
        flaky unit), so it is re-raised after the barrier; a processing failure goes to .failed and the
        good units still return (F2). Carries the original cause so the re-raise preserves it."""
        def __init__(self, cause: BaseException):
            self.cause = cause
            super().__init__(str(cause))

    def _resolve_unit(unit: Any) -> Any:
        """Resolve ONE unit to the role's primary input.

        F1 — ://-CLASSIFICATION (starts-with-registered-scheme): a unit is an ADDRESS only if it STARTS
        WITH a REGISTERED scheme — `contracts.address.scheme(unit) is not None`, i.e. it begins with one
        of `run://`/`cas://`/`blob://`/`vec://`/`ui://`/`code://`/`skill://`/`context://`. It is NOT an
        address merely because the string CONTAINS "://" somewhere in its body. This is the fix for the
        whole-repo map: 16% of repo files contain "run://"/"ui://" MID-TEXT (in prose/code), and the old
        `"://" in unit` check sent every such file to resolve_address — which then fail-louds on a
        not-content-resolvable scheme and aborted the map. With starts-with classification, those files
        are LITERALS (used as-is — the unit IS the text to fan the role over), exactly as intended.

        An ADDRESS resolves via resolve_address (materialize <turn> + dispatch by scheme + fail-loud on an
        unknown/unresolvable scheme). Anything else is a LITERAL, used as-is. (A non-address str — one that
        does not START with a registered scheme — is a literal, not a ctx-key: the BARE_NAME sentinel
        belongs to a role's bare input_addresses, not to a unit.) A templated `run://<turn>/x` still
        classifies as an address (it STARTS with `run://`), so the address/template path is preserved."""
        if isinstance(unit, str) and _scheme(unit) is not None:
            return resolve_address(store, unit, turn_id=turn_id, on_missing=on_missing)
        return unit

    def _one(i: int, unit: Any) -> "RoleRun | None":
        t0 = time.monotonic()
        with gate.slot():                                    # the SAME global gate as run_swarm/run_jury
            # RESOLUTION (the address contract) — a failure here is FATAL to the fan (re-raised at the
            # barrier). Wrapped in _ResolutionError so the barrier can tell it apart from a PROCESSING
            # failure (which goes to .failed; F2). on_missing="skip" handles a pruned ref WITHOUT raising.
            try:
                resolved_unit = _resolve_unit(unit)
            except BaseException as e:
                raise _ResolutionError(e) from e
            if resolved_unit is None and on_missing == "skip":
                # a DECLARED skip (a pruned run:// ref under on_missing="skip") — recorded, never silent.
                with finish_lock:
                    skipped[i] = f"unit {i} ({unit!r}) resolved to None (declared on_missing=skip)"
                return None
            # PROCESSING (run_role + the store write) — a failure here is PER-UNIT resilient (F2): it goes
            # to .failed and the good units still return. The exception propagates to the barrier as a
            # PLAIN exception (NOT a _ResolutionError) so the barrier routes it to .failed, not the re-raise.
            # build the per-unit ctx: the resolved unit at "utterance" (the role's primary input → the
            # default byte-identical run_role path) + the shared ctx's declared extra inputs.
            unit_ctx = dict(shared_ctx)
            unit_ctx["utterance"] = resolved_unit
            out = run_role(role, unit_ctx, base_url=base_url, model=model,
                           max_tokens=max_tokens, temperature=temperature, store=store)
            cas = store.put_content(out)                     # immutable content (write-once)
            store.set_ref(addresses[i], cas)                 # the run:// pointer (atomic set_ref)
        ms = int((time.monotonic() - t0) * 1000)
        rr = RoleRun(role_id=f"{role.id}/{i}", address=addresses[i], ok=True, ms=ms)
        with finish_lock:
            result.finish_order.append(i)
        return rr

    wall0 = time.monotonic()
    fatal: list[BaseException] = []                          # RESOLUTION failures — re-raised after barrier
    if items:
        with ThreadPoolExecutor(max_workers=budget.swarm_slots,
                                thread_name_prefix=f"items-{turn_id}") as pool:
            futs = {pool.submit(_one, i, u): i for i, u in enumerate(items)}
            for fut in as_completed(futs):                   # the BARRIER — every unit joined before we proceed
                i = futs[fut]
                try:
                    rr = fut.result()
                    if rr is not None:
                        runs[i] = rr
                except _ResolutionError as re_:              # RESOLUTION failure — FATAL to the fan (address
                    fatal.append(re_.cause)                  # contract: re-raise after the barrier, unchanged.
                except BaseException as e:                   # PROCESSING failure — PER-UNIT resilient (F2):
                    # the poison unit goes to .failed (recorded, never silent); the unit's address was never
                    # set_ref'd, so it is kept OUT of runs/resolved (the read-back reads OK addresses only).
                    # The GOOD units' outputs STILL return — the fan does NOT discard the whole batch.
                    failed[i] = f"{type(e).__name__}: {e}"
    result.wall_s = round(time.monotonic() - wall0, 3)
    result.skipped = [(i, skipped[i]) for i in sorted(skipped)]
    result.failed = [(i, failed[i]) for i in sorted(failed)]
    # ordered OK run-records (positional, excluding declared-skipped AND failed units — runs is ok-only,
    # so the after-barrier read-back never touches an address that was never set_ref'd).
    result.runs = [runs[i] for i in sorted(runs)]
    result.sum_unit_s = round(sum(rr.ms for rr in result.runs) / 1000.0, 3)

    # ONE BATCHED ROLLUP per fan (C1.6 discipline — NOT one append_event per unit-fire). Carries every
    # unit's run-record. NO resolve/approve/dispatch verb (the operator-only floor — driver, not agent).
    if emit is not None:
        emit("cognition.items", {
            "turn_id": turn_id, "role": role.id, "n_units": len(items),
            "n_run": len(result.runs), "skipped": [i for (i, _r) in result.skipped],
            # F2 — the FAILED units are recorded in the rollup too (fail-loud VISIBILITY: a poison unit is
            # never silently dropped; the run-record carries which units failed + why), distinct from the
            # declared-skipped units. The good units still ran (in `units` below).
            "failed": [{"i": i, "error": err} for (i, err) in result.failed],
            "wall_s": result.wall_s, "sum_unit_s": result.sum_unit_s,
            "finish_order": result.finish_order,
            "units": [{"i": rr.role_id.split("/")[-1], "address": rr.address, "ok": rr.ok,
                       "ms": rr.ms, **({"error": rr.error} if rr.error else {})}
                      for rr in result.runs],
        })
        # #54 STORAGE-DISCOVERY — the op.run RUN INDEX (introspective-data law: a run self-instruments).
        # ONE op.run per FAN (the C1.6 fsync discipline — never one append_event per unit), carrying the
        # per-unit run:// `addresses` (the discoverable inputs). list_runs EXPANDS this into one discovered
        # row per address at READ time. `duration_ms` reuses the introspective-data field-convention on the
        # SHARED op.run kind (run_stats rolls it up for free); op=cognition.run_items keys the run-projection.
        # Telemetry — additive, behaviour-preserving (the fan's outputs persist to run:// exactly as before);
        # NO resolve/approve/dispatch verb (the operator-only floor — a run record narrates, never governs).
        emit("op.run", {
            "summary": f"cognition.run_items · {role.id} · {len(result.runs)} units · {int(result.wall_s*1000)}ms",
            "op": "cognition.run_items", "run_op": getattr(role, "op", "generate"),
            "turn_id": turn_id, "role": role.id,
            "duration_ms": int(result.wall_s * 1000),
            # ONLY the OK units' addresses — a failed unit's address was never set_ref'd, so listing it would
            # break the run-index contract ("list an address you can FEED"). The fan re-raises below, but the
            # op.run is emitted first (telemetry records the attempt); index only the resolvable outputs.
            "addresses": [rr.address for rr in result.runs if rr.ok],
        })

    # Fail loud AFTER the rollup (so the failure is recorded) on a RESOLUTION failure ONLY — an
    # unresolvable run:// unit under on_missing="raise" is a fatal misconfiguration (the address contract),
    # so the whole fan re-raises (unchanged behaviour; tests/run_items_acceptance.py §3 locks this). A
    # PROCESSING failure (F2) does NOT raise — it is recorded in .failed and the good units still return.
    if fatal:
        raise fatal[0]

    # read every OK unit's output BACK via the canonical resolver (head→get_content), AFTER the barrier.
    # `runs` is ok-only (failed/skipped units are excluded), so a never-set_ref'd address is never read —
    # the F2 read-back does NOT relocate the whole-batch failure here (advisor flag).
    for i in sorted(runs):
        result.resolved[i] = resolve_run_ref(store, addresses[i])
    return result


# --- C2.4: the JURY/ensemble primitive (first-class) --------------------------------------------
@dataclass
class JuryResult:
    """The captured artifact of one jury run (the proof C2.4/C1.5 read)."""
    turn_id: str
    role_id: str
    draws: list = field(default_factory=list)           # the N resolved draw values (read back via run://)
    addresses: list = field(default_factory=list)       # the N distinct per-draw run:// addresses
    signatures: list = field(default_factory=list)       # the N content signatures (prove they're DISTINCT)
    verdict: dict = field(default_factory=dict)          # the deterministic verdict over the draws
    wall_s: float = 0.0


def run_jury(role: "Role", ctx: dict, store, *, turn_id: str,
             base_url: str = RESIDENT_BASE_URL, model: str = RESIDENT_MODEL,
             max_tokens: int = 256, temperature: float = 1.0,
             emit: Callable[[str, dict], None] | None = None) -> JuryResult:
    """Run a JURY role's N VARIED draws → a deterministic verdict (C2.4, building on C1.5).

    `role` MUST be a jury (role.is_jury — draws > 1) declaring a callable verdict_rule. Each of the N
    draws fires the SAME role at temperature>0 (so the draws VARY) and writes its validated JSON to a
    DISTINCT per-draw address `run://<turn>/<role>#<i>` (C1.5's per-draw key — they do NOT collapse at
    one ref). After the barrier, the draws are read BACK via the canonical resolver and the role's PURE
    verdict_rule (a deterministic function over the draws — quorum/vote; L2, no model call) decides.

    E4 caveat (documented in roles/verify_jury.py): N draws on ONE model are CORRELATED — variance, not
    independent error. The verdict_rule call shape (list[draw dict] → verdict dict) accepts a future
    2nd-model/cloud tiebreak slotting in. v1 = single-model with the limit documented.

    Fail loud: a non-jury role, an absent verdict_rule, or a missing draw ref RAISES. Returns a
    JuryResult capturing the N draws, their distinct addresses + signatures (proving variation), and
    the verdict. The draws fire concurrently (a wave of N) bounded by the global VRAM gate."""
    if not role.is_jury:
        raise ValueError(
            f"run_jury: role {role.id!r} is not a jury (draws={role.draws}) — declare draws>1 + a "
            f"verdict_rule to make it a jury (C2.4). Fail loud.")
    vrule = role.verdict_rule
    if not callable(vrule):
        raise ValueError(
            f"run_jury: jury role {role.id!r} has no callable verdict_rule — a jury's verdict MUST be "
            f"a PURE declared function over the draws (L2). Fail loud.")
    n = role.draws
    budget = SlotBudget.from_registry()
    gate = global_vram_gate(budget.max_num_seqs)
    addresses = [f"run://{turn_id}/{role.id}#{i}" for i in range(n)]
    result = JuryResult(turn_id=turn_id, role_id=role.id, addresses=addresses)
    draws: dict = {}
    errors: list[BaseException] = []

    def _draw(i: int):
        # C1.5 — each draw is a DISTINCT run:// address (#i) so the N draws don't collapse at one ref;
        # temperature>0 makes them VARY (the draws are intentionally varied — the verdict is deterministic).
        with gate.slot():
            out = run_role(role, ctx, base_url=base_url, model=model, max_tokens=max_tokens,
                           temperature=temperature)
            cas = store.put_content(out)
            store.set_ref(addresses[i], cas)
        return i, out

    wall0 = time.monotonic()
    with ThreadPoolExecutor(max_workers=max(1, min(n, budget.swarm_slots)),
                            thread_name_prefix=f"jury-{turn_id}") as pool:
        futs = {pool.submit(_draw, i): i for i in range(n)}
        for fut in as_completed(futs):                    # the BARRIER — all draws joined before verdict
            try:
                i, out = fut.result()
                draws[i] = out
            except BaseException as e:
                errors.append(e)
    result.wall_s = round(time.monotonic() - wall0, 3)
    if errors:                                            # fail loud — a jury cannot silently lose a draw
        raise errors[0]

    # read every draw BACK via the canonical resolver (proving the distinct per-draw addresses resolve),
    # capture content signatures to PROVE the draws are distinct, then apply the PURE verdict rule.
    import hashlib
    ordered = []
    for i, addr in enumerate(addresses):
        val = resolve_run_ref(store, addr)
        ordered.append(val)
        result.signatures.append(hashlib.sha256(
            json.dumps(val, sort_keys=True).encode()).hexdigest()[:12])
    result.draws = ordered
    result.verdict = vrule(ordered)                       # the deterministic verdict OVER the draws (L2)

    if emit is not None:                                  # ONE batched rollup (C1.6 discipline)
        emit("cognition.jury", {
            "turn_id": turn_id, "role": role.id, "n_draws": n, "wall_s": result.wall_s,
            "distinct_signatures": len(set(result.signatures)), "verdict": result.verdict,
            "addresses": addresses,
        })
    return result


# =================================================================================================
# C 2/4 — THE CROSS-UNIT REDUCE (run_reduce): the net-new JOIN engine.
#
# `run_swarm` is MAP-ONLY (fan-out + barrier + resolve-each-individually); the only joins that exist
# are run_role's two-input rule and run_jury's N-draws-of-ONE-role verdict. There is NO mechanism to
# JOIN N DIFFERENT units' outputs (COGNITION-REVIEW §3 "the smart REDUCE"; CORPUS-CHAIN §2-REDUCE:
# join / adjudicate / compose / decide-next). This wires the declared-but-dead `reduce-tree` shape
# (suite.py THOUGHT_SHAPES: join="reduce") LIVE.
#
# run_reduce is a DRIVER, not an agent (not-agent-by-default): it READS the N map outputs back via the
# canonical resolver (the run_jury read-back pattern, factored into _read_back) and applies ONE declared
# JOIN MODE. The model runs ONLY in the reduce-ROLE variant (a real role, fired via run_role); the rule
# and cluster variants are PURE L2 (no model call), mirroring run_jury's deterministic verdict_rule.
# A reduce emits NO resolve/approve/dispatch (the operator-only floor). It does NOT fire the MAP — the
# caller produces the addresses (via run_swarm or seeded) and passes them in; run_reduce only JOINS.
#
# Fail loud: a missing/unresolvable map address RAISES via resolve_run_ref (never a silent drop) UNLESS
# an explicit on_missing="skip" is declared (a DECLARED skip, not a silent one) — mirroring run_swarm's
# per-unit fail-loud + barrier re-raise.
# =================================================================================================


def _read_back(store, addresses, *, on_missing: str = "raise") -> "list[tuple[str, str, Any]]":
    """Read the N map-output run:// addresses BACK via the canonical resolver, in a STABLE order
    (the run_jury / run_swarm read-back pattern, factored to ONE place so the reduce + the jury share
    it — reuse-don't-fork). `addresses` is either a {unit_id: addr} mapping (e.g. WaveResult.addresses)
    or a list of addr strings; in both forms the unit_id is the mapping key or the address string.

    Returns a list of (unit_id, addr, value) tuples, ORDERED by unit_id (deterministic — the reduce's
    determinism, like the jury's, must not depend on which map unit finished first).

    Fail loud (C0.4 / the run_swarm barrier discipline): a missing/unresolved address RAISES through
    resolve_run_ref (head() is None → RuntimeError) — UNLESS on_missing="skip" is DECLARED, in which
    case a missing unit is omitted (a DECLARED skip, returned so the caller can see what was dropped —
    NEVER a silent drop)."""
    if isinstance(addresses, dict):
        items = sorted(addresses.items())                 # stable order by unit_id
    else:
        items = sorted((a, a) for a in addresses)         # a list of addrs: unit_id == addr
    out: list = []
    for unit_id, addr in items:
        # resolve_run_ref already fail-louds on a missing ref (on_missing="raise" default); pass the
        # declared on_missing through (so a declared skip returns None, never an implicit-truthy miss).
        val = resolve_run_ref(store, addr, on_missing=on_missing)
        if val is None and on_missing == "skip":
            continue                                       # a DECLARED skip (never a silent drop)
        out.append((unit_id, addr, val))
    return out


@dataclass
class ReduceResult:
    """The captured artifact of one cross-unit reduce (the by-use proof) — mirrors WaveResult/JuryResult.

    `joined` is the reduce's ONE output, its shape following the join mode:
      - reduce-role    → the synthesized role output dict (e.g. {"summary": ...}).
      - reduce-rule    → the pure verdict over the N values (whatever the rule returns).
      - reduce-cluster → {"clusters": [[unit_id, ...], ...], "k": N} (groups of near-duplicate units).
    """
    turn_id: str
    mode: str                                              # "role" | "rule" | "cluster"
    inputs: list = field(default_factory=list)             # [(unit_id, addr), ...] — what was read back (stable)
    skipped: list = field(default_factory=list)            # [(unit_id, addr), ...] declared-skipped (on_missing=skip)
    joined: Any = None                                     # the ONE reduce output (shape per mode, above)
    wall_s: float = 0.0
    detail: dict = field(default_factory=dict)             # mode-specific provenance (the by-use evidence)


def run_reduce(addresses, store, *, turn_id: str, mode: str,
               role: "Role | None" = None,
               reduce_rule: "Callable[[list], Any] | None" = None,
               cluster_threshold: float = 0.85,
               on_missing: str = "raise",
               embed_fn: "Callable | None" = None,
               base_url: str = RESIDENT_BASE_URL, model: str = RESIDENT_MODEL,
               max_tokens: int = 512,
               emit: "Callable[[str, dict], None] | None" = None) -> ReduceResult:
    """The CROSS-UNIT REDUCE — JOIN a set of map-output run:// addresses into ONE output (C 2/4).

    `addresses` = the map outputs to join: a {unit_id: run://addr} mapping (e.g. WaveResult.addresses)
    OR a list of run:// addr strings. run_reduce READS THEM ALL BACK via the canonical resolver (the
    run_jury read-back pattern, _read_back — stable order, fail-loud-on-missing), then applies ONE
    declared JOIN `mode`:

      mode="role"    — the reduce-ROLE / synthesize join (op=generate). Composes the N read-back outputs
                       into ONE input and fires `role` (a reduce-role, e.g. roles/reduce_synth.py) via
                       run_role → ONE synthesized output (the reduce-tree "join role"). The N→1 compose
                       is run_reduce's job (the N addresses are DYNAMIC — they cannot be statically
                       declared on the role); the role declares input_addresses=("notes",) and run_reduce
                       passes ctx={"notes": <composed>} (exercising the 1/4 input-axis compose path).
      mode="rule"    — the deterministic L2 join (no model). Applies the PURE `reduce_rule` (a callable
                       over the list of read-back values — vote / merge / select) → its result. MIRRORS
                       run_jury's verdict_rule EXACTLY (deterministic; identical on replay; no model call).
      mode="cluster" — the embed-cluster join (the built-twice DISCOVERY primitive). Embeds each unit's
                       read-back text (op=embed / complete_embeddings via embed_fn) then GROUPS by cosine-
                       nearness (reuse nodes/retrieve._cosine — dim-mismatch fail-loud by reuse) → clusters
                       of near-duplicates (the cross-unit "which of these are the same" join). Deterministic
                       given vectors (greedy union over SORTED units → replay-identical). `embed_fn` lets a
                       caller inject seeded vectors when the live embedder (:8001) is down (mirrors
                       vector_index.build_index's embed_fn seam); default = the live complete_embeddings.

    A DRIVER, not an agent: the model runs ONLY in the reduce-role; rule + cluster are pure L2. No
    resolve/approve/dispatch is emitted (operator-only floor). It does NOT fire the map (the caller
    passes the addresses). Fail loud: a missing address RAISES (or a DECLARED on_missing="skip" omits it,
    recorded in ReduceResult.skipped — never a silent drop), mirroring run_swarm's barrier discipline.

    Returns a ReduceResult (the by-use artifact)."""
    if mode not in ("role", "rule", "cluster"):
        raise ValueError(
            f"run_reduce: unknown join mode {mode!r} — declared modes are 'role' | 'rule' | 'cluster' "
            f"(COGNITION-REVIEW 'the smart REDUCE'). Fail loud (an unknown mode has no join branch).")

    wall0 = time.monotonic()
    # SHARED FRONT-HALF (the run_jury read-back, factored): read the N map outputs back, stable order.
    # A missing address fail-louds here (on_missing="raise") — the cross-unit barrier discipline.
    read = _read_back(store, addresses, on_missing=on_missing)
    values = [v for (_uid, _addr, v) in read]
    inputs = [(uid, addr) for (uid, addr, _v) in read]
    # which declared inputs were skipped (only populated when on_missing="skip")
    if isinstance(addresses, dict):
        all_items = sorted(addresses.items())
    else:
        all_items = sorted((a, a) for a in addresses)
    kept = {uid for (uid, _a) in inputs}
    skipped = [(uid, addr) for (uid, addr) in all_items if uid not in kept]

    result = ReduceResult(turn_id=turn_id, mode=mode, inputs=inputs, skipped=skipped)

    if mode == "role":
        # The reduce-ROLE / synthesize join (op=generate). The N→1 compose is run_reduce's job.
        if role is None:
            raise ValueError("run_reduce(mode='role'): a reduce-role must be passed (the join role, "
                             "e.g. roles/reduce_synth.py). Fail loud.")
        if not role.can_fire:
            raise ValueError(f"run_reduce(mode='role'): role {role.id!r} cannot fire (no prompt_template/"
                             f"output_schema) — a synthesize join needs a generate role. Fail loud.")
        # COMPOSE the N read-back outputs into ONE labelled input (deterministic order). Each unit is
        # rendered as "[unit_id] <json>" so the role sees which output came from which map unit.
        composed = "\n".join(f"[{uid}] {json.dumps(v, sort_keys=True)}" for (uid, _addr, v) in read)
        # Fire the reduce-role via run_role, exercising the 1/4 INPUT-AXIS compose path: the role
        # declares input_addresses=("notes",) and we SUPPLY ctx={"notes": composed} (a declared
        # non-utterance input present in ctx → _is_default_input is False → the labelled compose path).
        synth = run_role(role, {"notes": composed}, base_url=base_url, model=model,
                         max_tokens=max_tokens, temperature=0.0, store=store)
        result.joined = synth
        result.detail = {"n_units": len(values), "role": role.id, "composed_chars": len(composed)}

    elif mode == "rule":
        # The DETERMINISTIC L2 join (no model) — MIRRORS run_jury's verdict_rule (a PURE callable over
        # the list of read-back values; deterministic; identical on replay). No model call.
        if not callable(reduce_rule):
            raise ValueError("run_reduce(mode='rule'): a callable reduce_rule must be passed (a PURE "
                             "deterministic function over the N read-back values — vote/merge/select; "
                             "L2, no model call). Mirrors run_jury's verdict_rule. Fail loud.")
        result.joined = reduce_rule(values)               # the deterministic verdict over the N values
        result.detail = {"n_units": len(values), "rule": getattr(reduce_rule, "__name__", "rule")}

    else:  # mode == "cluster"
        # The EMBED-CLUSTER join — the built-twice DISCOVERY primitive ("which of these are the same").
        # Embed each unit's read-back text, then GROUP by cosine-nearness (reuse nodes/retrieve._cosine).
        clusters, vecs = _cluster_units(read, threshold=cluster_threshold, embed_fn=embed_fn,
                                        base_url=base_url)
        result.joined = {"clusters": clusters, "k": len(clusters)}
        result.detail = {"n_units": len(values), "threshold": cluster_threshold,
                         "dims": [len(v) for v in vecs]}

    result.wall_s = round(time.monotonic() - wall0, 3)

    if emit is not None:                                  # ONE batched rollup (C1.6 discipline)
        emit("cognition.reduce", {
            "turn_id": turn_id, "mode": mode, "n_units": len(values),
            "skipped": [uid for (uid, _a) in skipped], "wall_s": result.wall_s,
            "detail": result.detail,
        })
        # #54 STORAGE-DISCOVERY — the op.run RUN INDEX (see run_items). The reduce's joined output is NOT
        # persisted to a run:// address (the caller decides whether to land it), so this records THAT a
        # reduce happened (mode/inputs/turn_id) with an EMPTY `addresses` — list_runs lists it as a run
        # with no feedable output (flagged: a reduce output is not addressed today). Telemetry — additive,
        # behaviour-preserving; NO resolve/approve/dispatch (the operator-only floor — narrates, never governs).
        emit("op.run", {
            "summary": f"cognition.run_reduce · {mode} · {len(values)} units · {int(result.wall_s*1000)}ms",
            "op": "cognition.run_reduce", "run_op": mode,
            "turn_id": turn_id, "role": (role.id if role is not None else mode),
            "duration_ms": int(result.wall_s * 1000),
            "addresses": [],
        })
    return result


def _reduce_embed_text(value: Any) -> str:
    """The RAW text a cluster embeds for ONE read-back unit. A dict output is rendered to a stable JSON
    string (sort_keys — deterministic); a plain string is embedded as-is. (The same 'embed the unit's
    text' contract vector_index.build_index uses.)"""
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True)


def _cluster_units(read, *, threshold: float, embed_fn=None, base_url: str = RESIDENT_BASE_URL):
    """Embed the N read-back units + GROUP by cosine-nearness → clusters of near-duplicates (the
    cross-unit DISCOVERY join). Returns (clusters, vectors) where clusters is a list of lists of
    unit_ids (each group is a set of near-duplicate units) and vectors is the per-unit embedding list.

    REUSE (no parallel machinery): the cosine is nodes/retrieve._cosine (dim-mismatch FAIL-LOUD by
    reuse — never a wrong-but-plausible cosine); the live embed path is the EXISTING complete_embeddings
    (op=embed / vector_index.build_index's fabric path). `embed_fn(texts) -> [vector,...]` lets a caller
    inject SEEDED vectors when the embedder (:8001) is down (mirrors vector_index's embed_fn seam) — the
    cosine-grouping is deterministic given vectors, so the cluster LOGIC is proven on seeded vectors and
    the live-embed run is its first consumer when the launch-capability loads BGE-M3.

    DETERMINISTIC: units are processed in SORTED unit_id order and grouped greedily (a unit joins the
    FIRST existing cluster whose representative is within `threshold` cosine, else starts a new cluster)
    → replay-identical regardless of input order (mirrors the jury's order-independence)."""
    from nodes.retrieve import _cosine                     # reuse the cosine (dim-mismatch fail-loud)
    ordered = sorted(read, key=lambda t: t[0])             # stable: sort by unit_id
    unit_ids = [uid for (uid, _addr, _v) in ordered]
    texts = [_reduce_embed_text(v) for (_uid, _addr, v) in ordered]

    if embed_fn is not None:
        vectors = list(embed_fn(texts))                    # SEEDED / injected vectors (embedder-down path)
    else:
        # LIVE embed via the EXISTING fabric path (complete_embeddings — local resident embedder only).
        from fabric import client, transport, config as _fcfg
        et = transport.openai_embeddings_transport(base_url=_fcfg.DEFAULT_EMBED_URL)
        vectors = client.complete_embeddings(
            et, texts, model=_fcfg.DEFAULT_EMBED_MODEL, dim=_fcfg.DEFAULT_EMBED_DIM)

    if len(vectors) != len(unit_ids):                      # fail loud — every unit must get a vector
        raise ValueError(
            f"_cluster_units: embedder returned {len(vectors)} vectors for {len(unit_ids)} units — "
            f"a unit cannot be silently dropped from the cluster join (fail loud).")

    # GREEDY cosine grouping (deterministic): a unit joins the first cluster whose REPRESENTATIVE (its
    # first member's vector) is within `threshold`, else opens a new cluster. _cosine raises on a dim
    # mismatch (fail-loud by reuse). Replay-identical because units are processed in sorted order.
    clusters: list[list[str]] = []
    reps: list = []                                        # the representative vector per cluster
    for uid, vec in zip(unit_ids, vectors):
        placed = False
        for ci, rep in enumerate(reps):
            if _cosine(vec, rep) >= threshold:
                clusters[ci].append(uid)
                placed = True
                break
        if not placed:
            clusters.append([uid])
            reps.append(vec)
    return clusters, vectors


# =====================================================================================================
# THE CASCADE RUNNER (Cognition Engine GROUP N · N1-N3 · the LARGEST net-new of the corpus pillar)
#
# A saved cascade is a DECLARED chain — the ActionRegistry decl `{name, steps:[{op, model, ...}],
# output_schema}` validated + persisted by `runtime/coherence_actions.py:build_action`/`ActionRegistry`
# (the validator EXISTS — REUSED, never re-built). This is the EXECUTOR that runs such a saved decl
# end-to-end: for each step it fires the right ENGINE PRIMITIVE (`run_role`/`run_items`/`run_reduce`),
# THREADS each step's output → the next step's input (via the run:// resolver), PERSISTS + op.run-INDEXES
# each step (so `find_runs` sees every step), and returns the final step's addressed output.
#
# WHY net-new (RESEARCH-SYNTHESIS §4.1, coherence_actions.py:5-8 in-code): `build_action`/`ActionRegistry`
# only VALIDATE + SAVE a declaration; the multi-hop output→input EXECUTOR (per-step primitive dispatch,
# threading, persist, index) was never built. This is it — riding the existing primitives, NOT a 2nd engine.
#
# ── THE TWO TRAPS THIS DESIGN HANDLES (the seams an agent updating this MUST preserve) ──
#  TRAP 1 — the decl `op` is CONSTRAINED. `build_action._VALID_OPS` =
#    (generate, embed, similarity, retrieve, detect, reduce); a step's `op` CANNOT be a primitive name
#    (run_role/run_items/run_reduce). So the PRIMITIVE is selected from ADDITIVE step fields the validator
#    copies through verbatim (it never inspects them): the `kind` selector below. NEVER edit
#    coherence_actions.py to widen `op` — the primitive is a separate axis (op = the OPERATION the role
#    performs; kind = HOW it fans).
#  TRAP 2 — `run_reduce` does NOT persist its joined output to a run:// address (cognition.py ~1375-1386:
#    its op.run carries EMPTY addresses by design — the caller decides whether to land it). So THE RUNNER
#    OWNS PERSIST + INDEX UNIFORMLY for EVERY step: it calls the primitives with `emit=None` (suppressing
#    their self-op.run, which would otherwise double-record run_items/run_reduce AND give the reduce an
#    addressless row), then persists each step's output to a STEP-KEYED address and emits exactly ONE
#    op.run per step under the matching ENGINE_RUN_OP. This is what makes a reduce step FEEDABLE-by-address
#    and discoverable by find_runs — closing the "reduce not addressed today" gap for cascades.
#
# THE FLOOR (AGENTS.md rule + C9.2): a cascade step is a role-run (run:// COMPUTATION). The runner emits
# only op.run telemetry — NO resolve/approve/dispatch, launches NO claude -p. A cascade is computation,
# never a code-build. (Source-invariant-scanned by cognition_governance_acceptance.)
# =====================================================================================================

CASCADE_KINDS = ("role", "items", "reduce")   # the closed primitive selectors (drift home: runtime/AGENTS.md)


def _cascade_step_kind(step: dict) -> str:
    """Select the ENGINE PRIMITIVE for a cascade step from the DECL (registry-is-truth — never guessed).

    The decl `op` is constrained to coherence_actions._VALID_OPS (TRAP 1), so the primitive rides an
    ADDITIVE `kind` field the validator copies through verbatim. DERIVATION (fail-loud, no silent default):
      * explicit `kind` ∈ CASCADE_KINDS wins (the author said so);
      * else `op=="reduce"` → "reduce" (the JOIN op maps to the JOIN primitive);
      * else (op generate/embed) → "items" if the step is a FAN (`fan:true` OR `items` supplied), else "role".
    An explicit `kind` outside CASCADE_KINDS FAILS LOUD (rule 8 — never a fabricated primitive)."""
    kind = step.get("kind")
    if kind is not None:
        if kind not in CASCADE_KINDS:
            raise ValueError(
                f"cascade step kind {kind!r} is not a known primitive selector — declared kinds are "
                f"{CASCADE_KINDS} (role=run_role · items=run_items · reduce=run_reduce). Fail loud (rule 8).")
        return kind
    if step.get("op") == "reduce":
        return "reduce"
    if step.get("fan") or step.get("items") is not None:
        return "items"
    return "role"


def run_cascade(action: dict, store, *, turn_id: str,
                inputs: Any = None,
                resolve_role: "Callable[[str], Role]",
                reduce_rules: "dict[str, Callable] | None" = None,
                emit: "Callable[[str, dict], None] | None" = None,
                base_url: str = RESIDENT_BASE_URL, model: str = RESIDENT_MODEL,
                max_tokens: int = 256) -> dict:
    """EXECUTE a saved cascade (a validated ActionRegistry decl) END-TO-END (the GROUP N runner).

    `action` — the saved decl `{name, steps:[{op, model?, role, kind?, ...}], output_schema}` (already
        validated by `coherence_actions.build_action`; this runner does NOT re-validate the decl shape —
        save_cascade is the one validation door, REUSED). The runner reads the EXECUTION fields off each
        step: `role` (the role id — REQUIRED, resolved via `resolve_role`), `kind`/`op`/`fan` (the
        primitive selector — see `_cascade_step_kind`), `model` (per-step model override; None → the
        resident default — NO cloud router here, that is N2 in fabric/, needs-tim), and for reduce steps
        `reduce_mode`("role"|"rule"|"cluster", default "role") + `reduce_rule` (a NAMED rule via
        `reduce_rules`, for mode="rule").
    `inputs` — the FIRST step's input (the cascade's argument). A run://·cas:// address is resolved; a
        literal is used as-is. None → the role's default "Utterance:" framing.
    `resolve_role(role_id) -> Role` — the caller's role resolver (Suite.role_registry / mcp _resolve_role).
        Injected (not imported) so the runner stays engine-pure — no Suite/authoring import cycle.
    `reduce_rules` — the NAMED deterministic reduce-rules (for a reduce step with mode="rule"); a callable
        can't cross a decl, so it is selected BY NAME (mirrors the MCP run_reduce _REDUCE_RULES seam).

    ── THE SEAM (output→input threading — the heart of the runner) ──
      * step 0 reads `inputs` (the cascade argument).
      * step N (N>0) reads step N-1's output ADDRESS(es) — the run:// address(es) the prior step landed at.
      * CARDINALITY (per-primitive, explicit — never inferred by magic):
          - role   : consumes ONE value (the prior single address resolved, or `inputs`) → produces ONE
                     address run://<turn>/<i>-<role>.
          - items  : consumes a LIST (the prior step's address LIST, or `inputs` as a 1-list) → produces a
                     LIST run://<turn>/<i>-<role>/<j>.
          - reduce : consumes a LIST of addresses (the prior step's address list — the run_reduce input) →
                     produces ONE address run://<turn>/<i>-<role> (THE RUNNER persists it — TRAP 2).
      * a step's outputs are keyed by STEP INDEX (`<i>-<role>`), NOT bare `run://<turn>/<role>` — so two
        steps sharing a role never overwrite (the MCP run_role wrapper uses the bare form; the runner
        can't — a chain re-uses roles).

    FAIL LOUD (no silent fallback, rule 4): a missing/unresolvable step input RAISES (via the engine's
    `resolve_address`/`resolve_run_ref`, on_missing="raise" — the runner adds NO own check, the engine
    already raises); a step naming no `role`, an unknown `kind`, or a reduce mode/rule that doesn't
    resolve RAISES. A step never silently skips.

    Returns {action, turn_id, steps:[{step, role, kind, address|addresses, op}...], final_address,
             final_output}. THE FLOOR: emits only op.run telemetry (per step) — never resolve/approve/dispatch."""
    name = action.get("name", "<unnamed>")
    steps = action.get("steps") or []
    if not steps:
        raise ValueError(f"run_cascade: action {name!r} has no steps — nothing to execute (fail loud).")
    reduce_rules = reduce_rules or {}

    step_records: list[dict] = []
    prev_addresses: list[str] | None = None   # the prior step's output address(es) — the thread

    for i, step in enumerate(steps):
        role_id = step.get("role")
        if not role_id:
            raise ValueError(
                f"run_cascade: step {i} of {name!r} declares no `role` — a cascade step IS a role-run "
                f"(the model runs in the role; rule = pure decision, no role). Fail loud (rule 8).")
        role = resolve_role(role_id)
        kind = _cascade_step_kind(step)
        # A per-step `model` override is honoured on the RESIDENT endpoint (the engine pins RESIDENT_BASE_URL).
        # CLOUD-tier routing is N2 net-new transport in fabric/, NOT this lane — a cloud model id here FAILS
        # LOUD downstream in the client (no silent fallback). needs-tim: a multi-endpoint per-step router (N2).
        step_model = step.get("model") or model
        kw_common = {"max_tokens": max_tokens}

        if kind == "reduce":
            # ── REDUCE step: consume the prior step's address LIST → ONE joined output the RUNNER persists.
            reduce_mode = step.get("reduce_mode", "role")
            if prev_addresses is None:
                raise ValueError(
                    f"run_cascade: step {i} ({role_id!r}, reduce) is the FIRST step but a reduce JOINS the "
                    f"outputs of a prior MAP step — there is no prior step to reduce. Fail loud (a reduce "
                    f"needs upstream addresses; put a map/items step before it).")
            rkw = {"turn_id": turn_id, "mode": reduce_mode, "emit": None,
                   "base_url": base_url, "model": step_model, "max_tokens": max_tokens}
            if reduce_mode == "role":
                rkw["role"] = role
            elif reduce_mode == "rule":
                rname = step.get("reduce_rule")
                if rname not in reduce_rules:
                    raise ValueError(
                        f"run_cascade: step {i} reduce_mode='rule' names reduce_rule {rname!r} which is not "
                        f"a known named rule {sorted(reduce_rules)} — a callable can't cross a decl, select "
                        f"by name; fail loud (rule 8, never a fabricated rule).")
                rkw["reduce_rule"] = reduce_rules[rname]
            elif reduce_mode == "cluster":
                rkw["cluster_threshold"] = step.get("cluster_threshold", 0.85)
            else:
                raise ValueError(
                    f"run_cascade: step {i} reduce_mode {reduce_mode!r} unknown — declared modes are "
                    f"role|rule|cluster. Fail loud.")
            t0 = time.monotonic()
            res = run_reduce(list(prev_addresses), store, **rkw)
            ms = int((time.monotonic() - t0) * 1000)
            # TRAP 2 — THE RUNNER persists the joined output to a step-keyed run:// address (run_reduce
            # does NOT). This makes the reduce step FEEDABLE-by-address + discoverable by find_runs.
            address = f"run://{turn_id}/{i}-{role.id}"
            cas = store.put_content(res.joined)
            store.set_ref(address, cas)
            out_addresses = [address]
            final_output = res.joined
            run_op, op_kind = reduce_mode, "cognition.run_reduce"
            items_visibility = {}

        elif kind == "items":
            # ── ITEMS step (the MAP): fan the role over the prior step's address LIST (or `inputs` as a
            # 1-list on step 0). run_items persists each unit independently of emit; we suppress its
            # self-op.run (emit=None) and emit ONE uniform op.run for the fan below.
            if prev_addresses is not None:
                units: list = list(prev_addresses)            # the prior step's per-unit run:// addresses
            elif step.get("items") is not None:
                units = list(step["items"])                   # an EXPLICIT unit list declared on the step
            elif inputs is not None:
                units = inputs if isinstance(inputs, list) else [inputs]
            else:
                raise ValueError(
                    f"run_cascade: step {i} ({role_id!r}, items) has no units — pass `inputs`, declare "
                    f"`items` on the step, or place it after a map step. Fail loud.")
            t0 = time.monotonic()
            res = run_items(role, units, store, turn_id=f"{turn_id}-s{i}", emit=None,
                            base_url=base_url, model=step_model, **kw_common)
            ms = int((time.monotonic() - t0) * 1000)
            # FAIL LOUD ON A PROCESSING FAILURE (the lane law: "a missing step input / DOWN MODEL → fail
            # loud, never skip"; Tim's no-silent-failures rule). run_items is PER-UNIT RESILIENT by design
            # (F2 — a poison unit goes to .failed and the good units still return), and we suppressed its
            # `cognition.items` rollup (emit=None) which is where .failed is normally surfaced. In a CASCADE
            # that resilience is the WRONG posture: the downstream reduce consumes the SET, so a silently
            # SHRUNK input set silently changes the result (a confident answer built from fewer inputs than
            # supplied). So a cascade items step RAISES if ANY unit failed processing — the failed units are
            # named so the failure is legible, never an invisible shorter address list. (A resolution failure
            # already re-raised inside run_items regardless of emit — this covers the F2 processing path.)
            if res.failed:
                raise RuntimeError(
                    f"run_cascade: step {i} ({role_id!r}, items) had {len(res.failed)} unit(s) FAIL "
                    f"processing — a cascade reduce consumes the SET, so a silently shrunk input set is "
                    f"not acceptable (fail loud, no silent skip). Failed units: "
                    f"{[{'i': fi, 'error': err} for (fi, err) in res.failed]}")
            # run_items keys its outputs run://<turn>-s<i>/<role>/<j> (its own turn_id). Those ARE the
            # step-keyed addresses (the s<i> suffix makes them step-unique). Use the OK addresses.
            out_addresses = [rr.address for rr in res.runs if rr.ok]
            final_output = res.resolved
            run_op, op_kind = getattr(role, "op", "generate"), "cognition.run_items"
            address = None
            # carry the run_items visibility (skipped — only populated under a declared on_missing=skip; a
            # processing failure already raised above) onto the step record so it is never invisible.
            items_visibility = {"skipped": [fi for (fi, _r) in res.skipped]} if res.skipped else {}

        else:  # kind == "role" — ONE value in, ONE value out
            # ── ROLE step: consume ONE input (the prior single address resolved, or `inputs` on step 0).
            if prev_addresses is not None:
                if len(prev_addresses) != 1:
                    raise ValueError(
                        f"run_cascade: step {i} ({role_id!r}, role) consumes ONE value but the prior step "
                        f"produced {len(prev_addresses)} addresses — wire a `reduce`/`items` step (a role "
                        f"step is single-cardinality). Fail loud (the cardinality rule).")
                primary = resolve_address(store, prev_addresses[0], turn_id=turn_id)
            elif inputs is not None:
                primary = (resolve_address(store, inputs, turn_id=turn_id)
                           if isinstance(inputs, str) and _scheme(inputs) is not None else inputs)
            else:
                primary = ""   # the role's default "Utterance:" framing (run_role default-input path)
            ctx = {"utterance": primary}
            t0 = time.monotonic()
            out = run_role(role, ctx, base_url=base_url, model=step_model, store=store, **kw_common)
            ms = int((time.monotonic() - t0) * 1000)
            address = f"run://{turn_id}/{i}-{role.id}"
            cas = store.put_content(out)
            store.set_ref(address, cas)
            out_addresses = [address]
            final_output = out
            run_op, op_kind = getattr(role, "op", "generate"), "cognition.run_role"
            items_visibility = {}

        # #54 STORAGE-DISCOVERY — ONE uniform op.run per step (THE RUNNER OWNS INDEX — TRAP 2). op keys
        # the ENGINE_RUN_OP so find_runs/list_runs see every cascade step; addresses are the step's REAL
        # output address(es). Telemetry only — NO resolve/approve/dispatch (the floor).
        if emit is not None:
            emit("op.run", {
                "summary": f"{op_kind} · cascade {name} step {i} · {role.id} · {ms}ms",
                "op": op_kind, "run_op": run_op, "turn_id": turn_id, "role": role.id,
                "duration_ms": ms, "addresses": out_addresses,
                "cascade": name, "step": i, "step_kind": kind, **items_visibility,
            })

        step_records.append({"step": i, "role": role.id, "kind": kind, "op": op_kind,
                             "addresses": out_addresses, **items_visibility,
                             **({"address": address} if address else {})})
        prev_addresses = out_addresses

    final_address = prev_addresses[0] if (prev_addresses and len(prev_addresses) == 1) else None
    return {"action": name, "turn_id": turn_id, "steps": step_records,
            "final_address": final_address, "final_output": final_output,
            "final_addresses": prev_addresses}
