"""runtime/model_routing.py — resolve_model(intent): the ONE model-selection resolver (#71).

WHY (#71 model-routing unification): model selection was SCATTERED across three seams —
  • roles.resolve_binding(role, providers)   — role  → provider (capability match, runtime/roles.py:307)
  • Suite.capability_providers()              — capability → provider (services.json + provides_for)
  • cc_clone._pick_ollama_model(path, model)  — clone → the TIM-RULE context-size pick (kimi ≤256K else 1M)
resolve_model UNIFIES the ENTRY POINT (registry-is-truth): one call, an `intent` in →
`{model, base_url, provider, why, satisfied, ...}` out. It does NOT fork a second router — it WRAPS and
REUSES the three existing seams (reuse-don't-parallel; the context-pick is the SAME function the clone
path calls, cc_clone.pick_ollama_model_for_context). base_urls are config DATA (fabric.config), never
hardcoded literals.

PHASE (#71): Phase 1 (this module) = the resolver + the registry data EXIST and are verifiable; NOTHING is
routed through it yet. Phase 2 wires the live firing paths (run_swarm / cognition) through it BYTE-IDENTICALLY
(the resolver returns the same model the scattered logic does today). So Phase 1 changes NO behaviour.

INTENT shapes:
  {kind:"clone",      context_tokens:int, model?:str}   → the TIM-RULE context-size pick (ollama clones)
  {kind:"role",       role_id:str}                       → Suite.resolve_role_binding (effective role binding)
  {kind:"capability", capability:str|list[str]}          → Suite.capability_providers (first provider by capability)

★ THE FLOOR / NO-GREEN-PAINT (advisor-caught false-pass trap): the role seam (roles.resolve_binding) does
NOT raise when no provider matches a role that declares a `default_model` — it returns the DEFAULT
(provider="default", satisfied=False): the brain FLOOR. So a role re-tier can "look resolved" because it
silently floored to the resident 4B while the intended cloud brain (e.g. kimi) was never a live provider.
resolve_model SURFACES `satisfied` VERBATIM so a caller (and the verify) asserts a REAL capability match
(satisfied=True, the intended provider) — NOT merely a non-empty `model`. Assert satisfied, not truthiness.
"""

from __future__ import annotations


class ModelRoutingError(Exception):
    """A model-routing intent could not be resolved — fail loud (never a silent wrong/floor model)."""


def _clone_branch(intent: dict) -> dict:
    # REUSE the shared TIM-RULE context-pick (no second context-router) + the config-canonical ollama base.
    from runtime.cc_clone import pick_ollama_model_for_context
    from fabric.config import OLLAMA_DIRECT
    ctx = intent.get("context_tokens")
    if ctx is None:
        raise ModelRoutingError("clone intent needs context_tokens (int) for the TIM-RULE context-size pick")
    if not isinstance(ctx, int) or isinstance(ctx, bool) or ctx < 0:
        raise ModelRoutingError(f"clone context_tokens must be a non-negative int, got {ctx!r}")
    requested = intent.get("model")
    model, reason = pick_ollama_model_for_context(ctx, requested)
    return {
        "model": model,
        # Informational: a clone LAUNCHES via `ollama launch claude --model <tag>` (ollama-NATIVE, Anthropic
        # format) — it does NOT consume this base_url. OLLAMA_DIRECT is the config-canonical ollama endpoint
        # (the ollama-OpenAI surface on the same host); kept here so the contract shape is uniform + truthful.
        "base_url": OLLAMA_DIRECT,
        "provider": "ollama",
        "why": f"clone context-pick — {reason}",
        "satisfied": True,            # the pick always yields a concrete model (kimi · the 1M fallback · explicit)
        "kind": "clone",
    }


def _role_branch(intent: dict, suite) -> dict:
    if suite is None:
        raise ModelRoutingError("role intent needs suite= (reads the effective role binding + capability providers)")
    role_id = intent.get("role_id")
    if not role_id:
        raise ModelRoutingError("role intent needs role_id")
    b = suite.resolve_role_binding(role_id)   # REUSE: roles.resolve_binding(role, capability_providers())
    satisfied = b.get("satisfied")
    prov = b.get("provider")
    if satisfied:
        why = (f"role {role_id!r}: requires={b.get('requires')} → provider {prov!r} "
               f"provides {b.get('provides')} (capability match → {b.get('model')!r})")
    else:
        why = (f"role {role_id!r}: requires={b.get('requires')} → NO provider matched; FLOOR to "
               f"default_model {b.get('model')!r} (satisfied=False — a re-tier that lands HERE looks "
               f"resolved but isn't; the intended provider is not live)")
    return {
        "model": b.get("model"), "base_url": b.get("base_url"), "provider": prov,
        "why": why, "satisfied": satisfied, "requires": b.get("requires"),
        "provides": b.get("provides"), "candidates": b.get("candidates"), "kind": "role",
    }


def _capability_branch(intent: dict, suite) -> dict:
    if suite is None:
        raise ModelRoutingError("capability intent needs suite= (reads capability_providers)")
    cap = intent.get("capability")
    if not cap:
        raise ModelRoutingError("capability intent needs capability (a tag or list of tags)")
    needed = [cap] if isinstance(cap, str) else list(cap)
    providers = suite.capability_providers()   # {provider_id: {model, base_url, provides}}
    matches = [(pid, p) for pid, p in providers.items()
               if set(needed) <= set(p.get("provides") or [])]
    if not matches:
        avail = {pid: p.get("provides") for pid, p in providers.items()}
        raise ModelRoutingError(f"no provider provides all of {needed} (available providers: {avail})")
    pid, p = matches[0]
    return {
        "model": p.get("model"), "base_url": p.get("base_url"), "provider": pid,
        "why": f"capability {needed}: provider {pid!r} provides {p.get('provides')} → {p.get('model')!r}",
        "satisfied": True, "candidates": [m[0] for m in matches], "kind": "capability",
    }


def resolve_model(intent: dict, *, suite=None) -> dict:
    """Resolve a model-selection INTENT to {model, base_url, provider, why, satisfied, ...}. The ONE entry
    point (#71). Wraps + reuses the three existing seams; fail-loud on an unknown/under-specified intent.
    `suite` is required for kind in {role, capability} (they read the live registry); kind=clone is pure."""
    if not isinstance(intent, dict):
        raise ModelRoutingError(f"intent must be a dict, got {type(intent).__name__}")
    kind = intent.get("kind")
    if kind == "clone":
        return _clone_branch(intent)
    if kind == "role":
        return _role_branch(intent, suite)
    if kind == "capability":
        return _capability_branch(intent, suite)
    raise ModelRoutingError(f"unknown intent kind {kind!r} (expected one of: clone, role, capability)")
