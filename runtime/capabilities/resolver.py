"""resolver — the capability resolver (C2 of the capability-resolution architecture).

CAPABILITY-RESOLUTION-DESIGN-CORRECTED.md §5. The net-new LOGIC that turns the three
file-discovered DATA registries (capability_types.json · stack_capabilities.json ·
family_capabilities.json, all in this directory) into:

  resolve_capabilities(family, overrides=None)  -> the model's EFFECTIVE capability set
                                                   (family defaults ⊕ per-model overrides; override wins)
  serve_flags(config)                            -> the vLLM launch-arg flag list, GENERATED from
                                                   {resolved family, stack} and appended with
                                                   config.extra_flags verbatim

THE PROOF (tests/capability_resolver_acceptance.py): for the EXISTING config-driven services
(chat-4b/chat-2b/chat-08b · embed-bge/embed-jina-v5/embed-qwen3), serve_flags() of the
would-be-migrated declaration (`{family, stack, extra_flags}`, NO hand-typed flags[]) REPRODUCES
the current `config.flags` list BYTE-FOR-BYTE. That is the correctness proof WITHOUT wiring
anything — nothing live imports this module yet (the wiring into serveconfig.args_for is the
later LIVE phase, deliberately out of scope).

DESIGN STANCE — EXTEND, don't rebuild + reproduce-TODAY-exactly (SAFE half):
  - The functions take the family/stack/overrides as INPUT (a config dict), they do NOT read
    `config.family`/`config.stack` out of services.json — those optional fields don't exist there
    yet (and services.json is a forbidden-to-edit file). The caller (today the test; later the
    LIVE-phase serveconfig wiring) supplies the migrated declaration.
  - The SAFE half reproduces what launches TODAY. The qwen3.5 family's `reasoning` capability emits
    the EXISTING chat_template_nothink.jinja (the design's swap to a thinking-capable template is the
    LIVE phase). The `~`-path is emitted VERBATIM (literal `~`) — serveconfig.args_for's existing
    expanduser applies identically at launch, so behaviour is byte-preserved.

FAIL-LOUD, file-discovered (mirrors ops/cli/capabilities.py:_load_catalog / reload_catalog):
each registry loads at import; a missing/malformed/empty file RAISES (never a silently-empty
registry); reload_registries() re-reads from disk into the live names (the seam that proves
'add a row -> it appears, no code edit'). An unknown stack/capability that a stack can't express
RAISES (CapabilityResolutionError) rather than silently dropping a flag (on_unexpressible=fail_loud).
"""
import json
import os

_DIR = os.path.dirname(os.path.abspath(__file__))
_CAPABILITY_TYPES_PATH = os.path.join(_DIR, "capability_types.json")
_STACK_PATH = os.path.join(_DIR, "stack_capabilities.json")
_FAMILY_PATH = os.path.join(_DIR, "family_capabilities.json")


class CapabilityResolutionError(RuntimeError):
    """Raised when a capability cannot be resolved/expressed (unknown family/stack/capability, or a
    stack that cannot express an owned capability -> on_unexpressible=fail_loud). Fail-loud: the
    caller never sees a silently-dropped launch flag."""


def _load_json_registry(path, what):
    """Load a file-discovered registry, stripping `_`-prefixed annotation keys (`_doc`/`_note`).
    FAIL LOUD (raise) on missing/malformed/empty — never a silently-empty registry (a silent empty
    would make every model unresolvable, the opposite of registry-is-truth, AGENTS.md rule 8)."""
    try:
        with open(path) as f:
            raw = json.load(f)
    except FileNotFoundError as e:
        raise CapabilityResolutionError(
            f"{what} registry MISSING at {path!r} — the declared registry is the single source of "
            f"truth (registry-is-truth, rule 8); a missing registry is fail-loud, never an empty dict."
        ) from e
    except (ValueError, OSError) as e:
        raise CapabilityResolutionError(
            f"{what} registry at {path!r} is MALFORMED ({e}) — fail-loud; refusing a partial/empty "
            f"registry (a wrong registry mis-generates every launch)."
        ) from e
    if not isinstance(raw, dict):
        raise CapabilityResolutionError(f"{what} registry at {path!r} is not a JSON object — fail-loud.")
    rows = {
        k: v for k, v in raw.items()
        if not (isinstance(k, str) and k.startswith("_"))
    }
    if not rows:
        raise CapabilityResolutionError(f"{what} registry at {path!r} has NO rows — fail-loud.")
    return rows


def _strip_annotations(d):
    """Drop `_`-prefixed annotation keys from a single row's dict (so a row is pure data)."""
    if not isinstance(d, dict):
        return d
    return {k: v for k, v in d.items() if not (isinstance(k, str) and k.startswith("_"))}


# Loaded at import — the live registries (same fail-loud discipline as the model catalog).
CAPABILITY_TYPES = _load_json_registry(_CAPABILITY_TYPES_PATH, "capability-type")
STACKS = _load_json_registry(_STACK_PATH, "stack-expression")
FAMILIES = _load_json_registry(_FAMILY_PATH, "family")


def reload_registries(capability_types_path=None, stack_path=None, family_path=None):
    """Re-read the three registries from disk INTO the live names (in place, so importers holding the
    names see the update). Returns (CAPABILITY_TYPES, STACKS, FAMILIES). This is the seam that proves
    the verify-by-use bar: add a row to any registry FILE -> reload_registries() -> it appears via
    every query, NO code edit. Fail-loud like the import-time load. Each path independently overridable
    (the test points one at a temp file to prove add-a-row)."""
    global CAPABILITY_TYPES, STACKS, FAMILIES
    ct = _load_json_registry(capability_types_path or _CAPABILITY_TYPES_PATH, "capability-type")
    st = _load_json_registry(stack_path or _STACK_PATH, "stack-expression")
    fa = _load_json_registry(family_path or _FAMILY_PATH, "family")
    CAPABILITY_TYPES.clear(); CAPABILITY_TYPES.update(ct)
    STACKS.clear(); STACKS.update(st)
    FAMILIES.clear(); FAMILIES.update(fa)
    return CAPABILITY_TYPES, STACKS, FAMILIES


# --- C2 · resolve_capabilities: family defaults ⊕ overrides ---------------------------------------
def resolve_capabilities(family, overrides=None):
    """resolve_capabilities — the model's EFFECTIVE capability set: the family's declared defaults,
    with a per-model `capability_overrides` merged ON TOP (override wins). REUSES the family registry;
    fail-loud (CapabilityResolutionError) on an unknown family — never a silent default.

    Returns a dict:
      {
        family:       <name>,
        stack:        <the family's expression stack>,
        provides:     [<capability TAGS the model declares>],   # family.provides ⊕ overrides.provides
        capabilities: [<ORDERED serve_ref keys serve_flags emits>],  # family.capabilities ⊕ overrides
        serve_params: {<{placeholder} values the stack templates fill>},  # family ⊕ overrides (override wins)
        fields:       {<Layer-B field defaults>},                # family.fields ⊕ overrides.fields
      }

    The ⊕ merge: list-valued keys (provides/capabilities) take the override value when present
    (a model that overrides its capability set replaces it wholesale — the explicit per-model
    exception); dict-valued keys (serve_params/fields) shallow-merge with the override winning
    per key. This is the 'family defaults ⊕ overrides' of the design (§5)."""
    fam = FAMILIES.get(family)
    if fam is None:
        raise CapabilityResolutionError(
            f"resolve_capabilities: unknown family {family!r} — not in the family registry. "
            f"Register the family (one row in family_capabilities.json) before a model declares it; "
            f"never assume a default (registry-is-truth, rule 8). Known: {sorted(FAMILIES)}.")
    fam = _strip_annotations(fam)
    ov = _strip_annotations(overrides or {})

    stack = ov.get("stack", fam.get("stack"))
    provides = list(ov["provides"]) if "provides" in ov else list(fam.get("provides", []))
    capabilities = list(ov["capabilities"]) if "capabilities" in ov else list(fam.get("capabilities", []))

    serve_params = dict(fam.get("serve_params", {}))
    serve_params.update(ov.get("serve_params", {}))   # override wins per key

    fields = dict(fam.get("fields", {}))
    fields.update(ov.get("fields", {}))               # override wins per key

    return {
        "family": family,
        "stack": stack,
        "provides": provides,
        "capabilities": capabilities,
        "serve_params": serve_params,
        "fields": fields,
    }


# --- C2 · serve_flags: generate launch args from resolved capabilities × stack -------------------
def _fill_template(token, serve_params):
    """Fill a single serve-fragment token: a `{placeholder}` token is replaced by serve_params[name];
    any other token is emitted verbatim. A `{placeholder}` with no value -> fail-loud (a missing
    parser/template would silently drop a flag, the exact bug this architecture kills)."""
    if isinstance(token, str) and token.startswith("{") and token.endswith("}"):
        name = token[1:-1]
        if name not in serve_params or serve_params[name] is None:
            raise CapabilityResolutionError(
                f"serve_flags: serve-template needs {token} but the resolved serve_params has no "
                f"value for {name!r} (have: {sorted(serve_params)}). Fail-loud — refusing to emit a "
                f"flag with a missing parameter (a silently-dropped parser/template loses the capability).")
        return str(serve_params[name])
    return token


def serve_flags(config):
    """serve_flags — generate the vLLM launch-arg FLAG list from a model's would-be-migrated
    declaration, GENERATED from {resolved family, stack} and appended with config.extra_flags verbatim.

    `config` is the migrated declaration dict (the LIVE-phase serveconfig would read this from
    services.json; the SAFE-half caller/test constructs it in memory):
      {
        family:         <name>,                 # required to generate
        stack:          <name>,                 # optional — defaults to the family's stack
        capability_overrides: {...},            # optional per-model ⊕
        extra_flags:    [...],                  # optional — appended VERBATIM after the generated flags
                                                #            (the OLD flags[] escape-hatch role)
      }

    Returns the flag list (the part of serveconfig.args_for AFTER the model/port/host/gpu-util/
    max-model-len/max-num-seqs runtime params). For the EXISTING config-driven services this
    REPRODUCES config.flags byte-for-byte (the proof). A custom-server stack returns only
    extra_flags (its launch is a bespoke script — not flag-generated).

    Generation: for each capability in the resolved (ORDERED) `capabilities` list, look up the
    stack's serve-fragment for that capability's serve_ref, fill its {placeholders} from serve_params,
    and concatenate IN THAT ORDER. The order IS the canonical launch order (it matches today's
    hand-authored flag sequence). Then append extra_flags verbatim.

    FAIL-LOUD (on_unexpressible=fail_loud): an owned capability whose stack has no expression entry
    RAISES (CapabilityResolutionError) — never a silently-dropped flag."""
    family = config.get("family")
    if not family:
        raise CapabilityResolutionError(
            "serve_flags: config has no `family` — cannot generate flags (a service without a family "
            "declaration is the LIVE-phase flags[] pass-through path, handled by serveconfig, not here).")
    resolved = resolve_capabilities(family, config.get("capability_overrides"))
    stack = config.get("stack", resolved["stack"])
    stack_caps = STACKS.get(stack)
    if stack_caps is None:
        raise CapabilityResolutionError(
            f"serve_flags: unknown stack {stack!r} — not in the stack-expression registry. "
            f"Known: {sorted(STACKS)}.")
    stack_caps = _strip_annotations(stack_caps)
    serve_params = resolved["serve_params"]

    flags = []
    # Map a capability id (from the family's ordered list) -> its serve_ref via the capability-type
    # registry; a capability with no type row falls back to using its own id as the serve_ref (the
    # family lists serve_ref keys directly, so this is identity in practice — but the type-registry
    # lookup keeps the indirection the design specifies).
    for cap_id in resolved["capabilities"]:
        ctype = CAPABILITY_TYPES.get(cap_id)
        serve_ref = (ctype or {}).get("serve_ref", cap_id) if isinstance(ctype, dict) else cap_id
        expr = stack_caps.get(serve_ref)
        if expr is None:
            raise CapabilityResolutionError(
                f"serve_flags: stack {stack!r} cannot express capability {cap_id!r} "
                f"(serve_ref={serve_ref!r}) — on_unexpressible=fail_loud (a surfaced Gap, never a "
                f"silent drop). The stack registry has no entry for it. Known caps for {stack!r}: "
                f"{sorted(stack_caps)}.")
        for token in (expr.get("serve") or []):
            flags.append(_fill_template(token, serve_params))

    for f in config.get("extra_flags", []):
        flags.append(str(f))
    return flags
