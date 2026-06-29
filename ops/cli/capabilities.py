"""capabilities — the model-TYPE capability registry, keyed by MODEL-ID (G8 / C8.1–C8.4).

The THIRD keying in the model machinery (B4): intrinsic capability (by model-id, HERE)
⨝ service deployment (by service-key, services.json, EXISTS) ⨝ telemetry (EXISTS). This
module owns ONLY the intrinsic half — what the WEIGHTS can do (tool-calling · json_schema ·
thinking · context-ceiling · concurrency-knee · speed) — each with explicit PROVENANCE
(declared|probed|measured|served). It NEVER stores gpu_util/vram (rule 3 — that is the
service layer's job); for those it JOINS to ops/cli/gpu.py (the ONE VRAM authority — reused,
never duplicated). It COMPLEMENTS suite.py's MODEL_KNOBS (per-REQUEST knobs, also keyed by
model-id) — knobs say "what dials a request can turn"; this says "what the model can do."

WHY in ops/ and not suite.py (the B4 draft put it on the Suite): ops/ already owns the
deployment registry (services.json) + the VRAM authority (gpu.py), so the capability layer
sits with the resource machinery it JOINS to (rule: where things go — the resource view).
It is stdlib-only with BARE imports (matching the ops/cli package), so it loads in the 3.14
bridge and the CLI alike. The DOWNSTREAM consumer is suite.py's `capability_providers()`
(C2.5) — that seam today hand-derives the resident's `provides`; the lead wires it to read
THIS catalog (the wire is flagged in the lane report; see `provides_for`).

SELF-DESCRIPTION / DRIFT HOME (C9.4 / R2-FOLD H5): this registry's self-description home is
this module docstring + the ops/AGENTS.md "models/VRAM" type-view section; its drift
assertion lives in tests/model_capabilities_acceptance.py (the resident-4b row's exact values
+ the JOIN + fail-loud residency — the no-regression base) AND tests/model_catalog_acceptance.py
(C2.5 — the WIDTH: the full declared set, the capability-discrimination query, the data-driven
'add a row → it appears, no code edit' bar, the fail-loud loader). No net-new registry ships
without its drift home.

THE CATALOG IS FILE-DISCOVERED DECLARED DATA (C2.5, the original G8/L-model widened): the catalog
lives in ops/model_capabilities.json — the SINGLE source ops + cognition both read (registry-is-
truth) — NOT a hardcoded python dict that omits non-resident models. `_load_catalog` reads it into
MODEL_CAPABILITIES at import (FAIL LOUD if missing/malformed/empty — never a silently-empty catalog);
the name + shape + every consumer fn are UNCHANGED (the data MOVED, the values did not). Adding a
model's capabilities = adding ONE entry to that FILE (no code edit). The catalog now spans the FULL
declared model set keyed by model-id (the resident 4B · the local chat workers 2B/0.8B/nemotron ·
the embedders bge/jina/qwen3 · the model-id voice engines orpheus/qwen3tts · the cloud reasoner) —
so the role↔model query (suitable_models/role_can_bind/provides_for) projects REAL capabilities
across ALL models (an embed role → the embedders; a vision role → [] fail-loud-by-empty; a tts role
→ the voice engines), not just the resident's. Keyless services (clone-TTS engines + STT ears with
no config.model) cannot be model-id-keyed and are deliberately NOT invented here.

REGISTRY-IS-TRUTH (rule 8): every row is GROUNDED in a hard services.json signal — never fabricated
(--runner pooling → embed · --tool-call-parser qwen3_xml → tools · chat_template_nothink → no-think ·
a chat model → chat,json). Genuine unknowns are recorded honestly (value None/null, source declared):
cloud/ollama json_schema (L-transport: cloud may 400) and the not-yet-live-probed local workers'
tools/json_schema. An unknown model-id returns an explicit "unknown — ASK" result, never a row.
"""
import json
import os
import time
import urllib.request

import registry
import gpu
import systemd

# Provenance vocabulary (reuses MODEL_KNOBS' applies-vocab + B4's additions). LIVE wins over declared.
#   declared — asserted from a doc / known trait, not verified by execution
#   probed   — determined by a live capability probe at call time (endpoint-aware, e.g. tool-calling)
#   measured — a benchmark/measurement datum (the C0.5 KV measurement, decode tok/s)
#   served   — verified by a live USE call against the actually-served endpoint (the strongest)
PROVENANCE = ("declared", "probed", "measured", "served")

# The controlled capability-TAG vocabulary (the `provides`/`requires` axis). MATCHES the live
# suite.py capability_providers() set (chat·json·tools·fast·no-think) — so the lead's wire is a thin
# read, not a re-spelling — WIDENED (C2.5) with the catalog's other model TYPES so the FULL declared
# set has somewhere true to land:
#   embed   — an embedding model's provide (services.json `--runner pooling`); a MULTIMODAL embedder
#             provides both embed AND vision (e.g. Qwen3-VL-Embedding, jina-embeddings-v4).
#   rerank  — a cross-encoder / late-interaction-scoring model that re-orders a candidate set
#             (NOT an embedder — emits a relevance score, not a stored vector). A VISUAL reranker
#             (Qwen3-VL-Reranker) provides rerank AND vision. Added 2026-06-12 when the on-disk
#             reranker fleet (ms-marco · jina-reranker-v3 · Qwen3-VL-Reranker) was cataloged.
#   vision  — a model that ingests images/screenshots (the VL embedder + reranker now provide it;
#             it was a negative-only tag until 2026-06-12 — "no cataloged model provides it yet" is
#             no longer true). A vision-requiring role now resolves to the VL models.
#   tts/stt — a model-id-bearing voice engine / speech recognizer (forward-looking: no role REQUIRES
#             them yet; stt has no cataloged provider, so it is the current fail-loud-by-empty demo).
# NOTE: json_schema is a structured-output CAPABILITY FIELD (with provenance), NOT a provides-tag —
# no role in the cast requires it as a tag, and adding it to `provides` would diverge from the seam.
CAPABILITY_TAGS = ("chat", "json", "tools", "fast", "no-think", "vision", "thinking", "reasoning",
                   "embed", "rerank", "tts", "stt")

# --- THE CATALOG — keyed by MODEL-ID (the HF/cloud string), the intrinsic half ------------------
# DECLARED DATA, file-discovered (C2.5): the catalog is `ops/model_capabilities.json` — the SINGLE
# source ops + cognition both read (registry-is-truth, AGENTS.md rule 8) — NOT a hardcoded python
# dict that omits non-resident models. Adding a model's capabilities = adding ONE entry to that FILE
# (no code edit) — mirroring how services.json declares what RUNS. This module LOADS it into the
# `MODEL_CAPABILITIES` name (UNCHANGED name + shape: every field {value, source}; `provides` a TAG
# set ⊆ CAPABILITY_TAGS) so every consumer (provides_for/suitable_models/capabilities_for/role_can_bind)
# is unchanged — the data MOVED, the values + behaviour did not (the resident-4b row is preserved
# exactly; proven by tests/model_capabilities_acceptance.py asserting its literal values).
#
# WIDTH (C2.5): the file catalogs the FULL declared model set keyed by model-id — the resident 4B,
# the local chat workers (2B/0.8B/nemotron), the embedders (bge/jina/qwen3), the model-id-bearing
# voice engines (orpheus/qwen3tts), and the cloud reasoner — each with `provides` GROUNDED in a hard
# services.json signal (never fabricated). VRAM is NOT stored here (rule 3) — `capabilities_for`'s
# JOIN to gpu.py supplies it. Keyless services (the clone-TTS engines + STT ears with no
# config.model) cannot be model-id-keyed and are deliberately NOT invented here (a model-id is
# required to key a row); they remain service-only.

_CATALOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "model_capabilities.json")


def _load_catalog(path=None):
    """Load the declared catalog from ops/model_capabilities.json into the MODEL_CAPABILITIES shape.
    FAIL LOUD (raise) if the file is missing or malformed — NEVER a silently-empty catalog (a silent
    empty would make every role unbindable + every model 'unknown', the opposite of registry-is-truth).
    Strips `_doc`/`_note` annotation keys (they document the file, they are not model rows)."""
    path = path or _CATALOG_PATH
    try:
        with open(path) as f:
            raw = json.load(f)
    except FileNotFoundError as e:
        raise RuntimeError(
            f"model capability catalog MISSING at {path!r} — the declared catalog is the single source "
            f"of truth (registry-is-truth, rule 8); a missing catalog is fail-loud, never an empty dict."
        ) from e
    except (ValueError, OSError) as e:
        raise RuntimeError(
            f"model capability catalog at {path!r} is MALFORMED ({e}) — fail-loud; refusing a partial "
            f"or empty catalog (a wrong catalog mis-binds every role)."
        ) from e
    if not isinstance(raw, dict):
        raise RuntimeError(f"model capability catalog at {path!r} is not a JSON object — fail-loud.")
    # model rows only — drop the file-level `_doc`; within each row strip `_`-prefixed annotation keys
    # (`_note`) so a row is PURELY capability fields ({value, source} dicts) + `provides` — the exact
    # shape the consumers + the drift test (model_capabilities_acceptance) assert (iterate-all-fields).
    catalog = {
        mid: {k: v for k, v in row.items() if not (isinstance(k, str) and k.startswith("_"))}
        for mid, row in raw.items()
        if not (isinstance(mid, str) and mid.startswith("_"))
        if isinstance(row, dict)
    }
    if not catalog:
        raise RuntimeError(f"model capability catalog at {path!r} has NO model rows — fail-loud.")
    return catalog


# Loaded at import — the live catalog (same name/shape as the old inline dict). reload_catalog()
# re-reads the file (used by the acceptance test to prove 'add a row → it appears, no code edit').
MODEL_CAPABILITIES = _load_catalog()


def reload_catalog(path=None):
    """Re-read the declared catalog from disk INTO the live MODEL_CAPABILITIES (in place, so importers
    holding the name see the update). Returns it. This is the seam that proves the verify-by-use bar:
    add a row to ops/model_capabilities.json → reload_catalog() → it appears via every query, NO code
    edit. Fail-loud like the import-time load."""
    global MODEL_CAPABILITIES
    fresh = _load_catalog(path)
    MODEL_CAPABILITIES.clear()
    MODEL_CAPABILITIES.update(fresh)
    return MODEL_CAPABILITIES


# --- the model-id ↔ service-key JOIN (generalises bridge.py:_local_brain_key — NOT imported) -----
def service_key_for(reg, model_id):
    """The JOIN: the locally-served service-key whose config.model == model_id, or None (cloud/ollama).
    Local scan of services.json (reg) — the general form of bridge.py's `_local_brain_key`, implemented
    HERE so the lane stays file-disjoint (bridge.py is off-limits + being edited)."""
    for key, svc in reg["services"].items():
        cfg = svc.get("config") or {}
        if cfg.get("model") == model_id:
            return key
    return None


def _endpoint_for(reg, key):
    """The local OpenAI-compatible endpoint of a served service-key (for the live probe)."""
    cfg = reg["services"][key].get("config") or {}
    port = cfg.get("port") or reg["services"][key].get("port")
    return f"http://127.0.0.1:{port}/v1" if port else None


def family_for(reg, model_id):
    """The model's declared `family` (services.json config.family via the model↔service JOIN), or None
    when the model isn't locally served (a cloud/ollama model has no local family)."""
    key = service_key_for(reg, model_id)
    if not key:
        return None
    return (reg["services"][key].get("config") or {}).get("family")


def sampling_profile_for(model_id, *, thinking=False, reg=None):
    """The family-default SAMPLING profile for a model-id (think-aware) — the per-request BASE the chat path
    + run_role lay UNDER the explicit per-role/per-call knobs (override wins). Resolves model→family
    (services.json) → resolver.family_sampling (the family registry). Returns {} when the model is
    cloud/unknown OR its family declares no `sampling` — additive, never blocks a call. ONE join, both
    callers (suite._chat_part_core + cognition.run_role) use this — no parallel lookup."""
    reg = reg if reg is not None else registry.load()
    fam = family_for(reg, model_id)
    if not fam:
        return {}
    from runtime.capabilities import resolver
    return resolver.family_sampling(fam, thinking=bool(thinking))


def _probe_tools(endpoint, model_id, timeout=20):
    """Live tool-calling probe — forced tool_choice must emit a tool_call. Returns True/False/None
    (None = endpoint unreachable, do NOT assume). Read-only USE; never raises into the caller."""
    body = {
        "model": model_id,
        "messages": [{"role": "user", "content": "What is the weather in Paris?"}],
        "tools": [{"type": "function", "function": {
            "name": "get_weather", "description": "get weather",
            "parameters": {"type": "object", "properties": {"city": {"type": "string"}},
                           "required": ["city"]}}}],
        "tool_choice": "required", "max_tokens": 64, "temperature": 0.0,
    }
    try:
        req = urllib.request.Request(endpoint + "/chat/completions",
                                     data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        out = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
        return bool(out["choices"][0]["message"].get("tool_calls"))
    except Exception:
        return None


# --- C8.1 + C8.2 · capabilities_for(model_id): the catalog row + THE JOIN -----------------------
def capabilities_for(model_id, reg=None, live_probe=False):
    """C8.1/C8.2 — the capability fields for a model-id, JOINED to the deployment/VRAM layer.

    Returns a dict the role-binder / fit-surface / RHM reads directly:
      - the intrinsic fields (each {value, source}) from MODEL_CAPABILITIES;
      - `provides` (the capability TAG set);
      - the JOIN: if locally served (service_key_for hits), attaches `served_by` + reads
        `context_ceiling` from services.json + `vram_budget_mb` via gpu.budget_vram (REUSED, not
        re-stored) + DERIVED `resident_capable` (budget ≤ card ceiling, via gpu.py) + `is_resident`
        (gpu.py's live view of what's active);
      - if cloud/ollama-only: served_by=None, no VRAM (the 'two populations' trap, B4).
    An UNKNOWN model-id returns {"known": False, "model_id":..., "action":"ASK", ...} — never a
    fabricated row (rule 8). `live_probe=True` upgrades the `tools` field to source='served' from a
    read-only call to the served endpoint (probe wins over declared)."""
    reg = reg or registry.load()
    spec = MODEL_CAPABILITIES.get(model_id)
    if spec is None:
        return {
            "known": False, "model_id": model_id, "action": "ASK",
            "message": (f"model-id {model_id!r} is NOT in MODEL_CAPABILITIES — capabilities unknown. "
                        f"Register it (intrinsic facts) before a role binds it; never assume "
                        f"(registry-is-truth, rule 8). Known: {sorted(MODEL_CAPABILITIES)}"),
        }
    caps = {"known": True, "model_id": model_id}
    # deep-ish copy of the intrinsic fields (don't mutate the catalog)
    for k, v in spec.items():
        caps[k] = list(v) if isinstance(v, list) else (dict(v) if isinstance(v, dict) else v)

    key = service_key_for(reg, model_id)
    caps["served_by"] = key
    if key:
        svc_cfg = reg["services"][key].get("config") or {}
        ceiling = svc_cfg.get("max_model_len_ceiling")
        if ceiling:                                              # the JOIN refreshes context_ceiling
            caps["context_ceiling"] = {"value": ceiling, "source": "served", "from": key}
        caps["vram_budget_mb"] = gpu.budget_vram(reg, key)       # REUSE gpu.py — never re-store
        caps["resident_capable"] = caps["vram_budget_mb"] <= registry.ceiling_mb(reg)  # DERIVED via gpu
        caps["is_resident"] = is_resident(model_id, reg)         # live view of what's active
        caps["endpoint"] = _endpoint_for(reg, key)
        if live_probe and caps.get("endpoint"):                  # probe wins over declared (A6)
            probed = _probe_tools(caps["endpoint"], model_id)
            if probed is not None:
                caps["tools"] = {"value": probed, "source": "served",
                                 "note": "live forced-tool-choice probe at " + caps["endpoint"]}
    else:
        caps["vram_budget_mb"] = None
        caps["resident_capable"] = False
        caps["is_resident"] = False
    return caps


def catalog(reg=None):
    """The whole capability catalog as a status read (mirrors knobs_for()/roles()) — every model-id
    JOINED. Surfaced so the UI/RHM/brain read it the way they read node-types/verbs/models."""
    reg = reg or registry.load()
    return {mid: capabilities_for(mid, reg) for mid in MODEL_CAPABILITIES}


# --- C8.2 · provides_for + role_can_bind: the query the lead wires into capability_providers() ----
def provides_for(model_id):
    """The capability TAG set a model-id provides (the `provides` list), or [] if unknown.
    This is the exact value suite.py's capability_providers() hand-derives today for the resident —
    the lead's wire reads THIS instead of the literal list (the one suite-side wire, flagged)."""
    spec = MODEL_CAPABILITIES.get(model_id)
    return list(spec["provides"]) if spec else []


def role_can_bind(requires, model_id):
    """C8.2 — the binding query: can a role whose `requires` is this set bind to this model-id?
    True iff requires ⊆ provides. The SAME shape suite.py's resolve_role_binding uses (role.requires
    ⊆ provider.provides). Unknown model-id → False (never bind to an unknown — fail-loud-by-empty)."""
    return set(requires) <= set(provides_for(model_id))


def suitable_models(requires, reg=None):
    """All catalog model-ids whose provides ⊇ requires (the computed match — B4 C3). A NEW model that
    declares the right provides is automatically a candidate (path-of-least-resistance)."""
    return [mid for mid in MODEL_CAPABILITIES if role_can_bind(requires, mid)]


# --- C8.3 · cloud-decoupling POLICY as DATA (not control-flow) -----------------------------------
# The swarm ALWAYS runs resident; the main brain is SEPARATELY selectable (resident OR cloud); a mode
# MAY auto-pick cloud; cloud MAY run background roles. The swarm is NEVER lost by a cloud brain choice.
# Recorded as registry/policy DATA + a query (C8.3) — the actual control-flow wiring is downstream.
COGNITION_PLACEMENT_POLICY = {
    "swarm":      {"placement": "resident-always",
                   "why": "the swarm = concurrent requests to ONE resident vLLM model, batched; it is "
                          "never moved to cloud and never lost by a cloud BRAIN choice"},
    "main_brain": {"placement": "selectable",  "options": ["resident", "cloud"],
                   "why": "the foreground reply brain is independently selectable; a mode may auto-pick "
                          "cloud (C8.3) — that does NOT touch the resident swarm"},
    "background": {"placement": "cloud-allowed",
                   "why": "cloud MAY run background roles (between-turn consolidation); the resident "
                          "swarm stays the live per-turn cast regardless"},
}


def placement_for(track):
    """C8.3 — query the placement policy for a cognition track ('swarm'|'main_brain'|'background').
    Fail loud (KeyError) on an unknown track — never a silent default."""
    return COGNITION_PLACEMENT_POLICY[track]


def swarm_survives_cloud_brain():
    """C8.3 — the invariant as a query: choosing a cloud MAIN brain NEVER removes the resident swarm.
    True by construction (swarm placement is 'resident-always', independent of main_brain)."""
    return COGNITION_PLACEMENT_POLICY["swarm"]["placement"] == "resident-always"


# --- C8.4 · residency, FAIL-LOUD (reuse gpu.py's view of what's active; never auto-load) ----------
def is_resident(model_id, reg=None):
    """Is model_id currently LOADED (its backing service active)? Reuses gpu.py's running view
    (running_gpu_services → the per-unit is-active signal). Cloud/unbacked → False (not resident)."""
    reg = reg or registry.load()
    key = service_key_for(reg, model_id)
    if key is None:
        return False
    return key in {k for k, _ in gpu.running_gpu_services(reg)}


def require_resident(model_id, reg=None):
    """C8.4 — assert a needed model is resident; return a LOUD STRUCTURED result on miss (NO silent
    degrade, NO auto-load). The caller surfaces this + OFFERS to load via `company up`. Shape mirrors
    the fail-loud surfaces elsewhere: {resident:bool, ...}."""
    reg = reg or registry.load()
    key = service_key_for(reg, model_id)
    if key is None:
        return {
            "resident": False, "model_id": model_id, "served_by": None, "action": "ASK",
            "message": (f"model {model_id!r} has NO local service (cloud/ollama or unregistered) — it "
                        f"cannot be made resident on this card. If it must run locally, register a "
                        f"service for it; otherwise route via the cloud brain (C8.3)."),
        }
    if is_resident(model_id, reg):
        return {"resident": True, "model_id": model_id, "served_by": key,
                "message": f"{model_id} is resident (service {key} active)."}
    return {
        "resident": False, "model_id": model_id, "served_by": key, "action": "OFFER_LOAD",
        "load_command": f"company up {key}",
        "vram_budget_mb": gpu.budget_vram(reg, key),
        "message": (f"model {model_id!r} (service {key}) is NOT resident — needed but not loaded. "
                    f"Offer to load via `company up {key}` (~{gpu.budget_vram(reg, key)/1000:.1f} GB). "
                    f"NOT auto-loaded (no silent degrade; the operator/lead decides)."),
    }


# --- #50 · ensure_resident: THE GATED LAUNCH/SELECT/EVICT ACTUATOR ---------------------------------
# The deliberate ACTUATOR sibling of require_resident (the fail-loud surface above). require_resident
# SURFACES + OFFERS; ensure_resident ACTS (loads, evicting largest-first if asked). ONE gated capability
# the cognition engine + the CLI both call, UNIFYING the three load-on-demand consumers (the embed-op
# load · B brain_config · the mode-loadout swap) — see COGNITION-REVIEW.md "TIM CORRECTIONS" §2.
#
# REUSE-DON'T-PARALLEL (the GPU-shared law): it reuses the EXISTING ONE resource-manager primitives —
#   gpu.check_fit (the fit math) · gpu.plan_eviction (the largest-first, models→brain→voice eviction
#   plan, identical to `company up --evict`) · gpu.teardown (orphan-safe stop) · systemd.control(...,
#   "start") (the SAME start path `_act` uses) · gpu.budget_vram (the reservation).
# It does NOT call app.py:_act (that `print`s + `sys.exit(2)`s on refuse — it is the CLI front, not a
# library; calling it from the engine would crash the process). It reuses _act's PRIMITIVES, not _act —
# so there is exactly ONE resource-manager (gpu.py), no second start path, no duplicated fit math.
#
# GATED / operator-AUTO class: loading a model is reversible/internal (an AUTO-class action) — it does
# NOT bypass the operator-only governance floor (it never resolves/approves/dispatches a Tim decision).
# It is the explicit, deliberate actuator: callable when a run/operator GATES it (evict=True is an
# explicit authorization to make room), never auto-fired on every mode-switch.
#
# FAIL-LOUD: if it cannot fit even after the full eviction plan, it RAISES EnsureResidentError — never
# a silent half-load, never a blind over-budget --force stomp (that stays a separate CLI-only override).
#
# G14 — THE SWAP-APPROVAL RESPONSE (Tim's design, 2026-06-09): a load that NEEDS eviction without
# pre-authorization (evict=False) is NOT a hard-block and NOT a silent evict — the actuator RETURNS a
# structured swap-approval ASK ({swap_needed, would_load, would_evict, free_gb, needed_gb, approve})
# carrying the REAL largest-first plan it would execute, so the agent/operator approves AT CALL TIME
# (re-call with the authorization). The raise is reserved for the genuinely impossible (no service /
# can't fit even after the FULL plan / start failed) — an ask whose approve would fail is a false offer.

class EnsureResidentError(RuntimeError):
    """Raised when a model CANNOT be made resident (no local service, or won't fit even after the full
    largest-first eviction plan). Fail-loud: the caller never sees a silent half-load."""


def _resolve_service_key(reg, model_or_service):
    """Disambiguate the arg → a local service-key (the thing the resource-manager loads).
    A service-key (in services.json) is used directly; otherwise treat it as a model-id and JOIN via
    service_key_for. Returns the key, or None (cloud/ollama/unregistered — no local card slot)."""
    if model_or_service in reg["services"]:
        return model_or_service
    return service_key_for(reg, model_or_service)


def _wait_until_serving(svc, timeout=420):
    """Block until the service's port serves (reuses systemd.port_open / is_active — the SAME poll
    `company up --wait` uses, app.py:_wait_and_record:56-63). Returns True if it came up, False on
    timeout/unit-failure. WHY this matters: an embedder cold-loads; returning before :8001 serves makes
    the very next complete_embeddings fail-loud RAISE on a not-yet-ready endpoint (misread as a load
    failure). So ensure_resident is not 'done' until the port answers."""
    port = svc.get("port")
    if not port:
        return True  # no port to wait on (non-serving) — control() success is the signal
    t0 = time.time()
    while time.time() - t0 < timeout:
        if systemd.port_open(port) is True:
            return True
        if systemd.is_active(svc) == "failed":
            return False
        time.sleep(3)
    return systemd.port_open(port) is True


def ensure_resident(model_or_service, *, evict=False, reg=None, wait=True, timeout=420):
    """#50 — THE GATED LAUNCH/SELECT/EVICT ACTUATOR. Make a model/service RESIDENT on demand.

    Args:
      model_or_service — a service-key (services.json) OR a model-id (JOINed via service_key_for).
      evict            — if True AND the start doesn't fit, make room via the EXISTING largest-first
                         eviction plan (gpu.plan_eviction — models→brain→voice, identical to
                         `company up --evict`), then load. If False and it doesn't fit → the G14
                         SWAP-APPROVAL ASK is RETURNED (see below) — not a raise, not a silent evict.
      reg              — the registry (loaded if None).
      wait/timeout     — block until the service's port serves before returning (default True).

    Returns a structured dict (mirrors require_resident's shape) describing what happened:
      {resident, model_or_service, served_by, action, evicted, vram_budget_mb, message}
        action ∈ {"already-resident", "loaded", "evicted-and-loaded", "swap-approval-needed"}.
      G14 — THE SWAP-APPROVAL ASK (Tim's design, 2026-06-09): when the load NEEDS eviction and
      eviction was NOT pre-authorized (evict=False), the actuator RETURNS the structured ask —
        {swap_needed: True, would_load: <svc>, would_evict: [<svcs> — the REAL largest-first plan],
         free_gb, needed_gb, approve: "re-call with ensure_evict=true", resident: False, ...}
      — never a hard-block, never a silent evict; the agent (or operator) decides and re-calls with
      the authorization. Callers MUST check `swap_needed`/`resident` before treating the result as
      a successful load (the run_role(ensure=) seam surfaces this dict to the agent).

    RAISES EnsureResidentError on: no local service (cloud/unregistered); won't fit even after the
    full eviction plan (an ask whose approve would fail is a false offer — this raises under EITHER
    authorization); the start command failed; or (when wait=True) the service never came up. NEVER
    a silent half-load (fail-loud law)."""
    reg = reg or registry.load()
    key = _resolve_service_key(reg, model_or_service)
    if key is None:
        raise EnsureResidentError(
            f"ensure_resident: {model_or_service!r} has NO local service (cloud/ollama or unregistered) "
            f"— it cannot be made resident on this card. Register a service for it to run locally, or "
            f"route via the cloud brain (C8.3). Known services: {sorted(reg['services'])}.")
    svc = reg["services"][key]
    budget = gpu.budget_vram(reg, key)

    # 1. ALREADY RESIDENT → no-op (idempotent).
    if key in {k for k, _ in gpu.running_gpu_services(reg)}:
        return {"resident": True, "model_or_service": model_or_service, "served_by": key,
                "action": "already-resident", "evicted": [], "vram_budget_mb": budget,
                "message": f"{key} is already resident (~{budget/1000:.1f} GB) — no-op."}

    # 2. FIT? — reuse gpu.check_fit (the ONE fit math: measured free vs the budget sum).
    ok, need, free, _present = gpu.check_fit(reg, [key])
    evicted = []
    if not ok:
        # The load needs ROOM. Compute the largest-first plan EITHER WAY (gpu.plan_eviction — the ONE
        # planner, sparing the to-start key): authorized (evict=True) EXECUTES it; unauthorized RETURNS
        # it as the G14 swap-approval ASK so the agent/operator decides at call time.
        plan, projected = gpu.plan_eviction(reg, [key], need, free)
        if not plan or projected < need:
            # No swap CAN fit this load — an ASK whose approve would then fail is a false offer; this
            # stays the genuine fail-loud case regardless of authorization.
            raise EnsureResidentError(
                f"ensure_resident: CANNOT fit {key} (need ~{need/1000:.1f} GB, free ~{free/1000:.1f} GB) "
                f"even after evicting {plan or 'nothing evictable'} (frees only ~{projected/1000:.1f} GB). "
                f"Fail-loud — the card cannot hold this model alongside what must stay. No half-load.")
        if not evict:
            # G14 — THE SWAP-APPROVAL ASK (Tim's design, 2026-06-09): a load that needs eviction and
            # wasn't pre-authorized RETURNS "swap needed — approve?" — NEVER a hard-block (the old
            # raise), NEVER a silent evict. The agent (or operator) decides and re-calls with the
            # authorization. Structured + complete: what would load, what would be evicted (the REAL
            # largest-first plan the authorized path would execute), the measured numbers, and the
            # approve hint at every seam (run_role/MCP `ensure_evict=true` · this fn `evict=True` ·
            # CLI `--evict`). Nothing is loaded or evicted on this branch.
            return {
                "resident": False, "swap_needed": True,
                "model_or_service": model_or_service, "served_by": key,
                "would_load": key, "would_evict": plan,
                "free_gb": round(free / 1000, 2), "needed_gb": round(need / 1000, 2),
                "vram_budget_mb": budget, "action": "swap-approval-needed", "evicted": [],
                "approve": "re-call with ensure_evict=true",
                "message": (f"SWAP NEEDED — loading {key} needs ~{need/1000:.1f} GB but only "
                            f"~{free/1000:.1f} GB is free. Approving would evict "
                            f"{', '.join(plan)} (largest-first). Approve: re-call with "
                            f"ensure_evict=true (run_role/MCP) / evict=True "
                            f"(capabilities.ensure_resident) / `company ensure {key} --evict` (CLI). "
                            f"Nothing was loaded or evicted."),
            }
        # 3. EVICT — the AUTHORIZED path (evict=True): execute the SAME plan (behaviour unchanged).
        for k in plan:
            okk, msg = gpu.teardown(svc=reg["services"][k])   # orphan-safe stop (cgroup teardown)
            if not okk:
                raise EnsureResidentError(
                    f"ensure_resident: eviction of {k} FAILED ({msg}) while making room for {key} — "
                    f"aborting before any load (fail-loud; never a partial-evict half-state).")
            evicted.append(k)
        time.sleep(2)  # let VRAM release (matches _act's post-stop settle)

    # 3b. WS-R — the SYSTEM-RAM leg (the check_fit above is VRAM-only). A CPU-resident service costs 0
    # VRAM (stt-granite fp32 ~9 GB, the ONNX ears, whisper.cpp) so the VRAM gate passes it (need 0) —
    # yet host-RAM overcommit is the kernel OOM-killer. gpu.ram_fit reads LIVE /proc/meminfo MemAvailable
    # (counts ALL processes on the box, not just services), so this is the gate that makes the actuator —
    # and therefore the mode→loadout swap that rides it (WS1 apply_loadout) — unable to OOM. Checked AFTER
    # any VRAM eviction above (which also freed that service's RAM); ram_fit re-reads live, so it reflects
    # the freed memory. RAM overflow is not VRAM-evictable, so this fails loud (no --evict/--force bypass).
    ram = gpu.ram_fit(reg, [key])
    if ram["present"] and not ram["ok"]:
        raise EnsureResidentError(
            f"ensure_resident: CANNOT fit {key} in SYSTEM RAM — needs ~{ram['need']/1000:.1f} GB, only "
            f"~{ram['free']/1000:.1f} GB available (live MemAvailable − headroom). RAM overflow is "
            f"kernel-fatal and not VRAM-evictable; free memory first (close other RAM users / "
            f"`company down <service>`). Fail-loud — never an OOM-inducing load. evicted={evicted}.")

    # 4. LOAD — the SAME start path `_act` uses (systemd.control(svc, "start")). One start mechanism.
    okk, msg = systemd.control(svc, "start")
    if not okk:
        raise EnsureResidentError(
            f"ensure_resident: starting {key} FAILED ({msg}). evicted={evicted}. See `company logs {key}`. "
            f"Fail-loud (never report resident when the start did not take).")

    # 5. WAIT until it actually serves (so a downstream embed/chat call hits a ready endpoint).
    if wait and not _wait_until_serving(svc, timeout=timeout):
        raise EnsureResidentError(
            f"ensure_resident: {key} was started but its port did not serve within {timeout}s "
            f"(evicted={evicted}). See `company logs {key}`. Fail-loud — not a half-load to ignore.")

    action = "evicted-and-loaded" if evicted else "loaded"
    return {
        "resident": True, "model_or_service": model_or_service, "served_by": key, "action": action,
        "evicted": evicted, "vram_budget_mb": budget,
        "message": (f"{key} loaded (~{budget/1000:.1f} GB)"
                    + (f" after evicting {', '.join(evicted)} (largest-first)" if evicted else "")
                    + (" and serving." if wait else ".")),
    }


# --- #50 · the B / mode-loadout consumer (lightweight) — the deliberate mode→loadout actuator --------
def ensure_loadout_for_mode(mode, *, evict=False, reg=None, mode_registry=None):
    """B / mode-loadout consumer: read a mode's declared `brain_config` (the mode→loadout name, e.g.
    'swarm-16k' | 'voice-64k') and ensure_resident the brain SERVICE it wants — the deliberate
    mode→loadout actuator. GATED: NOT auto-fired on a mode switch; an explicit, authorized call.

    `mode_registry` is the callable `Suite.mode_registry` (passed in to keep this lane file-disjoint
    from suite.py — registry-is-truth, read the declared row, never a parallel mode table here). If
    omitted it is imported from runtime.suite.

    THE HONEST GAP (surfaced, never silently bridged — anti-hardcoding law): a `brain_config` value is
    a LOADOUT NAME that encodes a gpu_util VARIANT of the brain (swarm-16k @ 0.63 vs voice-64k @ 0.49),
    NOT a service-key. suite.py:1513 already declares the gpu_util-variant SWAP out-of-scope / needs-tim.
    So this consumer ensures the brain SERVICE is resident and RETURNS the requested variant + a loud
    `variant_applied=False` flag — it does NOT silently drop a hardcoded {name→service} map (that would
    break registry-is-truth). The brain service is resolved from the registry (the `brain` group), never
    a literal. Applying the gpu_util variant (a `company config`/`swap` + restart) stays the needs-tim
    deeper action."""
    reg = reg or registry.load()
    if mode_registry is None:
        from runtime.suite import Suite          # lazy — keeps the import off the stdlib CLI path
        mode_registry = Suite.__new__(Suite).mode_registry
    row = mode_registry(mode)                     # the declared mode row (fail-loud on unknown mode)
    wanted = row.get("brain_config")
    if not wanted:
        raise EnsureResidentError(
            f"ensure_loadout_for_mode: mode {mode!r} declares no brain_config — nothing to ensure "
            f"(fail-loud; a mode that wants a loadout must declare it).")
    # Resolve the brain SERVICE from the registry (the `brain` group member) — never a hardcoded map.
    brain_keys = [k for k, s in reg["services"].items() if s.get("group") == "brain"]
    if not brain_keys:
        raise EnsureResidentError(
            "ensure_loadout_for_mode: no service in the `brain` group to make resident (registry has "
            "no brain service). Fail-loud.")
    brain_key = brain_keys[0]
    res = ensure_resident(brain_key, evict=evict, reg=reg)
    # Surface the variant gap loudly — the gpu_util variant is NOT applied here (needs-tim, suite.py:1513).
    cur_util = (reg["services"][brain_key].get("config") or {}).get("gpu_util")
    res["loadout_requested"] = wanted
    res["variant_applied"] = False
    res["variant_note"] = (
        f"brain service {brain_key} is resident; the loadout VARIANT {wanted!r} (a gpu_util change, "
        f"current gpu_util={cur_util}) is NOT applied by ensure (a `company config {brain_key} gpu_util "
        f"<v>` + restart — flagged needs-tim at suite.py:1513). Residency ensured; variant surfaced.")
    return res
