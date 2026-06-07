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
assertion lives in tests/model_capabilities_acceptance.py (asserts every catalog entry has
the required fields + provenance, and that the resident's `provides` matches the capability
fields it derives from). No net-new registry ships without its drift home.

REGISTRY-IS-TRUTH (rule 8): entries are SEEDED only from what is KNOWN — services.json, the
C0.5 measurement, and L-transport's proven json_schema fact. Cloud/ollama json_schema is
recorded UNKNOWN (declared, value None) — recording that gap is exactly this registry's job.
An unknown model-id returns an explicit "unknown — ASK" result, never a fabricated row.
"""
import json
import os
import urllib.request

import registry
import gpu

# Provenance vocabulary (reuses MODEL_KNOBS' applies-vocab + B4's additions). LIVE wins over declared.
#   declared — asserted from a doc / known trait, not verified by execution
#   probed   — determined by a live capability probe at call time (endpoint-aware, e.g. tool-calling)
#   measured — a benchmark/measurement datum (the C0.5 KV measurement, decode tok/s)
#   served   — verified by a live USE call against the actually-served endpoint (the strongest)
PROVENANCE = ("declared", "probed", "measured", "served")

# The controlled capability-TAG vocabulary (the `provides`/`requires` axis). MATCHES the live
# suite.py capability_providers() set exactly (chat·json·tools·fast·no-think) + the negative
# (vision) the verify-by-use exercises — so the lead's wire is a thin read, not a re-spelling.
# NOTE: json_schema is a structured-output CAPABILITY FIELD (with provenance), NOT a provides-tag —
# no role in the cast requires it as a tag, and adding it to `provides` would diverge from the seam.
CAPABILITY_TAGS = ("chat", "json", "tools", "fast", "no-think", "vision", "thinking", "reasoning")

# --- THE CATALOG — keyed by MODEL-ID (the HF/cloud string), the intrinsic half ------------------
# Seeded ONLY from services.json + the C0.5 measurement + L-transport's proven json_schema fact.
# Every field carries {value, source}. concurrency_knee is DATA (the C0.5 loadout numbers), never
# the stale literal 32. context_ceiling is the model's real ceiling (max_model_len_ceiling), read
# via the JOIN where served. Cloud rows record UNKNOWNs honestly (value None, source declared).
MODEL_CAPABILITIES = {
    "cyankiwi/Qwen3.5-4B-AWQ-4bit": {
        # --- intrinsic capabilities (what the weights can do) ---
        # tools + json_schema were LIVE-PROVEN served against the resident vLLM :8000 (read-only USE):
        #   tools  — forced tool_choice='required' returned a real tool_call (get_weather Paris)
        #   json_schema — L-transport's negative control: a no-JSON prompt STILL returned conformant
        #                 JSON, so xgrammar CONSTRAINS the decode (not just accepts). provenance=served.
        "tools":           {"value": True,  "source": "served",
                            "note": "live probe :8000 forced tool_choice → tool_call emitted; also "
                                    "--enable-auto-tool-choice + qwen3_xml parser in services.json"},
        "json_schema":     {"value": True,  "source": "served",
                            "note": "L-transport PROVED resident vLLM 0.21 CONSTRAINS the decode "
                                    "(neg-control: no-JSON prompt still conformant). Re-probed live."},
        "thinking":        {"value": False, "source": "declared",
                            "note": "no-think model — chat_template_nothink.jinja (services.json); the "
                                    "day-one judge pick was chosen for exactly this"},
        # context ceiling: the model's REAL capacity, not the currently-set max_model_len (65536).
        # Read via the JOIN from the backing service's max_model_len_ceiling where served.
        "context_ceiling": {"value": 262144, "source": "served",
                            "note": "services.json chat-4b config.max_model_len_ceiling (reachable solo)"},
        # --- performance profile (the MEASURED numbers the swarm budget + fit-surface read) ---
        # concurrency-knee is DATA derived from max_num_seqs + KV (the C0.5 formula), NOT the literal 32.
        # See G0.C0.5-measurement.json: the bind FLIPS on main-context depth.
        "concurrency_knee": {
            "value": {
                "max_num_seqs": 16,                       # services.json chat-4b config.max_num_seqs
                "kv_kb_per_token": 31.7,                  # services.json config._profile (measured)
                "formula": "min(max_num_seqs - R, free_KV_tokens / per_role_ctx)",
                # the two MEASURED loadout points (G0.C0.5-measurement.json authoritative_vllm_kv):
                "loadout_points": {
                    "voice_coresident_u0.49": {"kv_pool_tokens": 66036, "kv_gib": 2.14,
                                               "roles_at_deep_main": "~1-2",
                                               "note": "0.49 util + Orpheus co-resident; KV~one 64K conv "
                                                       "→ deep main collapses swarm to ~1-2"},
                    "swarm_mode_u0.63":       {"kv_pool_tokens": 135574, "kv_gib": 4.38,
                                               "roles_at_deep_main": "~16",
                                               "note": "0.63 util + NO Orpheus; 64K main leaves ~71K → "
                                                       "seq-cap(16) is the sole bind → ~16 roles"},
                },
            },
            "source": "measured",
            "note": "C0.5 (2026-06-07, lead-supervised). NOT the stale literal 32 — bind flips on main "
                    "context depth; the swarm Semaphore reads this, sized per the resident loadout.",
        },
        "speed_profile":   {"value": {"decode_tok_s": 100},  # ~100 tok/s decode (the resident worker)
                            "source": "measured",
                            "note": "approximate decode speed of the resident 4B-AWQ worker"},
        # --- role-suitability: a CAPABILITY SET (provides), not a list of role names (B4 C3) ---
        # MATCHES suite.py capability_providers() exactly so role.requires ⊆ provides is the same query.
        "provides":        ["chat", "json", "tools", "fast", "no-think"],
    },
    # Cloud / ollama brain options carry capabilities but NO local VRAM (B4 "two populations" trap).
    # json_schema is UNKNOWN for these — L-transport flagged they MAY 400 on response_format:json_schema;
    # recording that gap honestly (value None, source declared) is exactly this registry's job (C8.3).
    "deepseek-v4-pro:cloud": {
        "tools":           {"value": True,  "source": "declared",
                            "note": "ollama /api/show capabilities — verify by probe before binding"},
        "json_schema":     {"value": None,  "source": "declared",
                            "note": "UNKNOWN for cloud (L-transport: may 400). ASK / probe, never assume."},
        "thinking":        {"value": True,  "source": "declared", "note": "a reasoner"},
        "context_ceiling": {"value": None,  "source": "declared", "note": "cloud — no local ceiling/VRAM"},
        "concurrency_knee": {"value": None, "source": "declared",
                             "note": "cloud-throttled, not a local KV knee"},
        "speed_profile":   {"value": None,  "source": "declared"},
        "provides":        ["chat", "json", "tools", "thinking", "reasoning"],  # NOT 'fast', NOT 'no-think'
    },
}


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
