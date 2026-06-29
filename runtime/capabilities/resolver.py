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


# --- USE-side · family_sampling: the per-request sampling BASE a family recommends ----------------
def family_sampling(family, thinking=False):
    """The family's recommended SAMPLING profile — the USE-side base layer UNDER per-role knobs +
    per-call kwargs (override wins). `thinking` selects the family's reasoning-on (`thinking`) vs
    reasoning-off (`default`) profile (Qwen3.5 tunes them differently). Returns the knob dict (annotation
    keys + None values stripped), or {} when the family is unknown OR declares no `sampling`.

    DELIBERATELY NON-RAISING on absence (unlike serve_flags): sampling is an ADDITIVE enhancement, not a
    launch flag — an unknown/cloud model or a family with no profile simply falls back to the caller's
    explicit knobs / historical defaults (the call still runs). The `sampling_profile` capability-type is
    declared use-only (no serve order) — this is its resolver. Reads the live FAMILIES registry."""
    fam = FAMILIES.get(family)
    if not isinstance(fam, dict):
        return {}
    samp = fam.get("sampling")
    if not isinstance(samp, dict):
        return {}
    profile = samp.get("thinking" if thinking else "default") or {}
    return {k: v for k, v in _strip_annotations(profile).items() if v is not None}


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

    # --- per-model capability INJECTION via capability-type-keyed overrides (dissolves BUG 2) ----------
    # A `capability_overrides` key that NAMES a capability-type row (e.g. `vision: 'lm-only'`) — and is
    # NOT one of the structural keys handled above — is a per-model capability injection, driven by the
    # capability-type's `value_shape` (registry-is-truth, not a code literal):
    #   value_shape bool  -> inject-when-truthy (the flat stack serve fragment);
    #   value_shape enum  -> SELECT the serve fragment by value via the row's `serve_values` map
    #                        (a value mapping to null = a declared NO-OP, no flag emitted — e.g.
    #                         vision.full loads the vision tower, so NO --language-model-only).
    # An injected capability is placed into the ordered `capabilities` list at its registry `order` rank
    # (the family's own list is already in rank order). serve_ref_overrides carries the enum-selected
    # serve_ref so serve_flags emits the right fragment. Fail-loud on an unknown enum value or a missing
    # value_shape — never silently drop or mis-emit a flag.
    _STRUCTURAL = {"stack", "provides", "capabilities", "serve_params", "fields"}
    serve_ref_overrides = {}
    injected = []                                      # (order_rank, cap_id)
    for key, val in ov.items():
        if key in _STRUCTURAL:
            continue
        ctype = CAPABILITY_TYPES.get(key)
        if ctype is None:
            raise CapabilityResolutionError(
                f"resolve_capabilities: capability_override {key!r}={val!r} names no capability-type row "
                f"(and is not a structural key). Register it in capability_types.json before a model "
                f"declares it (registry-is-truth, rule 8). Known capability-types: {sorted(CAPABILITY_TYPES)}.")
        shape = ctype.get("value_shape")
        emit_id = None
        if shape == "bool":
            if val:                                    # inject only when truthy; falsy = declared OFF, no flag
                emit_id = key
        elif shape == "enum":
            serve_values = ctype.get("serve_values")
            if not isinstance(serve_values, dict) or val not in serve_values:
                raise CapabilityResolutionError(
                    f"resolve_capabilities: enum capability_override {key!r}={val!r} is not a declared "
                    f"value — the capability-type {key!r} must carry a `serve_values` map listing every "
                    f"valid enum value (have: {sorted(serve_values) if isinstance(serve_values, dict) else serve_values!r}). "
                    f"Fail-loud — refusing to guess a serve fragment for an undeclared enum value.")
                # NOTE: serve_values[value] == null is a VALID declared NO-OP (no flag), distinct from an unknown value above.
            mapped = serve_values[val]
            if mapped is not None:                     # null = declared no-op (e.g. vision.full -> no flag)
                emit_id = key
                serve_ref_overrides[key] = mapped      # the value-selected serve_ref for serve_flags
        else:
            raise CapabilityResolutionError(
                f"resolve_capabilities: capability_override {key!r} has value_shape {shape!r}, which is not "
                f"injectable as a serve flag (only `bool` and `enum` capabilities inject via override). "
                f"Fail-loud rather than silently ignore the declaration.")
        if emit_id is not None and emit_id not in capabilities:
            order_rank = ctype.get("order")
            if order_rank is None:
                raise CapabilityResolutionError(
                    f"resolve_capabilities: capability-type {key!r} has no `order` rank — cannot place it "
                    f"in the canonical launch order. Add an `order` to its capability_types.json row "
                    f"(registry-is-truth).")
            injected.append((order_rank, emit_id))
    # Insert each injected capability at its order rank relative to the family-listed caps' ranks.
    for order_rank, cap_id in sorted(injected):
        pos = len(capabilities)
        for i, existing in enumerate(capabilities):
            ex_ct = CAPABILITY_TYPES.get(existing)
            ex_rank = ex_ct.get("order") if isinstance(ex_ct, dict) else None
            if ex_rank is not None and ex_rank > order_rank:
                pos = i
                break
        capabilities.insert(pos, cap_id)

    return {
        "family": family,
        "stack": stack,
        "provides": provides,
        "capabilities": capabilities,
        "serve_params": serve_params,
        "fields": fields,
        "serve_ref_overrides": serve_ref_overrides,
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
    serve_ref_overrides = resolved.get("serve_ref_overrides", {})

    flags = []
    # Map a capability id (from the family's ordered list) -> its serve_ref. Priority:
    #   1. an enum-selected serve_ref from resolve_capabilities (serve_ref_overrides — e.g. vision
    #      'lm-only' selected the `vision` fragment; a different enum value could select a different one);
    #   2. the capability-type row's default serve_ref;
    #   3. the cap_id itself (a capability with no type row — the family lists serve_ref keys directly,
    #      so this is identity in practice, but the indirection is kept as the design specifies).
    for cap_id in resolved["capabilities"]:
        ctype = CAPABILITY_TYPES.get(cap_id)
        if cap_id in serve_ref_overrides:
            serve_ref = serve_ref_overrides[cap_id]
        else:
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
