"""roles/register_element.py — the REGISTER_ELEMENT role (Registry-Generation chain · RG3 · the MAP step).

The net-new role of the V-A loop (the swarm reads the surface → grows the address registry). It maps ONE
candidate element (a meaningful mockup element the EXTRACT pass, RG1, emitted) → a PROPOSED registry dossier
— the same `{represents, capabilities, howto, …}` shape the 82 existing `ui://` entries in
`design/_system/addresses.json` carry, so a clicked element can explain itself at the operator's altitude.
This is the engine-depth half cognition owns; it MIRRORS `roles/screen_reader.py` exactly (a Pydantic
output class + a self-registering module-level `ROLE` dict), and is fired over N units by `run_items`
(cognition.py — the 1-role × N-units axis-inversion, the chain's MAP), reduced/deduped by `run_reduce`
(RG5), confirmed by the jury + refcheck (RG6), surfaced to the operator (RG8), and only then written back
(RG9). It NEVER auto-writes the registry (operator-only floor) — it PROPOSES.

────────────────────────────────────────────────────────────────────────────────────────────────────────
NO-FICTION IS THE MAKE-OR-BREAK (the one truth must not be corrupted). A registration is only as good as
the CONTEXT it sees: a model with thin context invents capabilities + feature ids, which poisons the
registry. So this role is GROUNDED — and grounding must reach the MODEL, not just be declared.

THE SEAM (input_addresses — the run:// output→input wiring, the engine-real grounding path):

  run_role (runtime/cognition.py) builds the prompt as
      system = role.prompt_template
      user   = the unit at ctx["utterance"]  +  the DECLARED extra input_addresses (composed as
               labelled lines, each resolved per-name from ctx / a run:// store)
  Nothing auto-injects the role-spec `context` field into the prompt (verified: run_role only reads
  `context` for the per-role token-budget math, never into `msgs`). So ALL grounding the model must SEE
  is routed through `input_addresses` (the real vehicle), NOT the `context` field. The split:

    (a) PER-UNIT (varies every fire) → rides the UNIT at ctx["utterance"].
        run_items places each unit at ctx["utterance"]; the EXTRACT pass (RG1) emits the unit as the
        candidate's snippet — element outerHTML (bounded) + visible_text + tag/role + selector + the
        nearest registered ANCESTOR address + ITS dossier (so the child nests under + inherits the
        parent's framing). The unit IS the per-unit-varying context. (RG1 freezes the unit schema.)

    (b) PER-MOCKUP (the GROUND step's output feeds the MAP step) → a `run://` input_address.
        The screen_reader GROUND pass (RG2) produced an at-altitude summary of THIS element's mockup at
        `run://<turn>/screen_reader/<mockup-i>`. Declared here as a templated run:// input
        (`run://<turn>/screen_reader/{mockup}`), MIRRORING check.py's `("run://<turn>/part-1", "ground")`:
        the dependency is declared as DATA; the per-unit chaining executor that materializes <mockup>
        against THIS element's mockup is the CASCADE (RG7) / the chainer — flagged downstream, NOT built
        in this file (exactly as check.py declares its forming-answer ref but defers the chainer to G3/G4).

    (c) SHARED across all N units (identical every fire — the context-efficiency win) → bare-name
        input_addresses delivered through run_items' SHARED `ctx` (its documented "ctx is a SHARED
        context for the role's DECLARED EXTRA inputs" path — the engine's REAL resolve-once vehicle):
          · `exemplars`  — 3-5 real addresses.json entries (voice/shape few-shot)
          · `inventory`  — the Feature & Function Inventory (design/register.json `features`: 58 real
                           ids like ENG-resolve) + the closed capability vocabulary (the 5 ui_info caps:
                           pointable · spotlit · presentable · openable · driven). The no-fiction anchor.
        These are RESOLVED ONCE by the caller and passed in run_items' shared `ctx` (NOT re-inlined per
        unit → no N× token bloat). The cascade (RG7) supplies them; this file DECLARES the contract.

CONTEXT-EFFICIENCY NOTE (engine depth, honest status): the role-spec `context` field below names the same
shared exemplars+inventory as a FORWARD CONTRACT (the way judge.py declares its `context` as prose). But
auto-resolution of the role-spec `context` field into the prompt is NOT wired in run_role today — so the
"resolve-once, shared, addressed" efficiency is realised through run_items' shared `ctx` (the bare-name
input_addresses above), which the engine DOES deliver. The `context` field is declarative/forward, not a
proven prompt-injection path. Flagged, not fictionalised.

DEFER, don't duplicate (LAW 0 — unification): a candidate whose selector already maps to a registered
`ui://` is NOT a new address — the role RECOGNISES it and DEFERS (sets grounding="defer" + represents
"already registered — defer to <existing ui://>" + maps_to_feature the existing one or "proposed"), it
must NEVER re-propose a duplicate address. (The cross-unit dedup is run_reduce's cluster mode, RG5; this
is the per-unit recognition that keeps the role from minting a collision in the first place.)

Op:generate. mode_scope={"registration"} — a registration cast, so the cast-beyond-listening seam
(56d42f4, the same seam screen_reader rides) can fire it. Fireable.
"""
from pydantic import BaseModel
from typing import Literal


class HowTo(BaseModel):
    """The nested howto sub-model — the 82 entries' three-part voice (WHAT / WHAT YOU CAN DO / HOW TO
    CHANGE IT), at the operator's altitude. A real sub-BaseModel (kind:object in B2's richer field-type
    grammar — the nested object the flat-scalar draft lacked), NOT a flat dict."""
    what: str               # plain language: what this element IS (NOT HTML/tags/code)
    what_you_can_do: str    # what the operator can DO with it, at his altitude
    how_to_change: str      # how the element is changed (which region/code/wire — the 82's "HOW TO CHANGE IT")


class RegisterElementOut(BaseModel):
    """register_element reads a candidate element (+ its grounded context) → a PROPOSED registry dossier,
    the same junction shape addresses.json entries carry. PROPOSED — never auto-written (operator-only floor).

    Richer field-type grammar (B2 — nested/optional, not flat scalars): `howto` is a nested sub-model
    (HowTo); the rest are scalars/lists + a closed-vocabulary TAG (`grounding` — the no-confidence law,
    G16: tags+counts, never a fabricated float). Mirrors how ScreenReaderOut is a real class."""
    address: str            # the PROPOSED ui:// — nested UNDER the parent's address (parent + "/" + element)
    represents: str         # short, the 82's "RUN-run" voice — what real thing this element represents
    howto: HowTo            # the nested at-altitude dossier (what / what_you_can_do / how_to_change)
    capabilities: list[str] # ⊆ the REAL capability vocabulary (pointable·spotlit·presentable·openable·driven) — NEVER invented
    maps_to_feature: str    # a Feature & Function Inventory id (e.g. "ENG-resolve") OR the literal "proposed" if un-built
    grounding: Literal["built", "proposed", "uncertain", "defer"]   # the NO-CONFIDENCE tag (G16) — a discrete
    #   grounding STATE, not a float (the float was empirically flat noise — all 0.85; the tag carries the
    #   routing signal the operator triages on). built=a real built addressable feature (maps_to_feature a
    #   real inventory id); proposed=mockup-only/un-built (maps_to_feature="proposed"); uncertain=ambiguous,
    #   surface for extra operator scrutiny; defer=selector already maps to a registered ui:// (don't duplicate).


ROLE = {
    "id": "register_element",
    "label": "Register element (propose a registry dossier)",
    "description": (
        "Maps a candidate mockup element + its grounded context (parent dossier · mockup summary · "
        "exemplars · feature inventory) → a PROPOSED registry dossier (address · represents · howto · "
        "capabilities · maps_to_feature · grounding tag), at the 82 existing entries' altitude. Proposes "
        "— never writes (operator-only floor). Defers an already-registered selector, never duplicates it."
    ),
    "prompt_template": (
        "You are the REGISTER_ELEMENT role. You read ONE candidate element from a design mockup and propose "
        "a REGISTRY DOSSIER for it — the entry that lets the system explain that element, at altitude, to a "
        "NON-DEVELOPER operator who reads no code. You PROPOSE; you never write anything. Match the voice of "
        "the existing registry entries you are shown (the exemplars).\n"
        "\n"
        "You are given (as labelled inputs):\n"
        "  - the ELEMENT (its visible text, tag/role, a bounded HTML snippet, its selector, and its parent's "
        "registered address + that parent's dossier) — read it as a person SEES the screen, not as code;\n"
        "  - the MOCKUP SUMMARY (what screen this element lives on + its purpose) for framing;\n"
        "  - EXEMPLARS (3-5 real registry entries) — copy their voice + shape;\n"
        "  - the INVENTORY: the allowed CAPABILITY vocabulary and the allowed FEATURE ids.\n"
        "\n"
        "GROUNDING RULES — these are absolute (a fabricated entry corrupts the one registry):\n"
        "  - capabilities: choose ONLY from the capability vocabulary you are given "
        "(pointable, spotlit, presentable, openable, driven). NEVER invent a capability. Pick the ones that "
        "honestly fit what the element does; an inert label gets few or none.\n"
        "  - maps_to_feature: use a feature id from the INVENTORY only if this element clearly depicts that "
        "real, built feature. If the element is mockup-only / not yet built / you are unsure, set it to the "
        "literal \"proposed\" and set grounding to \"proposed\"/\"uncertain\" — do NOT guess a feature id.\n"
        "  - address: nest the proposed ui:// UNDER the parent's address (parent + '/' + a short element "
        "slug). If the element's selector ALREADY corresponds to the parent address or a registered address "
        "you were shown, DEFER: do not mint a new address — set grounding to \"defer\", set represents to "
        "\"already registered — defer to <that ui://>\", and reuse that address. Never duplicate an address.\n"
        "  - grounding: a discrete TAG (NOT a number) reporting how grounded the dossier is — "
        "\"built\" ONLY when the element is clearly a real, built, addressable thing AND maps_to_feature is a "
        "real inventory id; \"proposed\" for a mockup-only / un-built element (maps_to_feature must be "
        "\"proposed\"); \"uncertain\" when the element's function is ambiguous (surface for operator scrutiny); "
        "\"defer\" when the selector already maps to a registered ui://.\n"
        "\n"
        "Return ONLY JSON:\n"
        '  "address": the proposed ui:// (nested under the parent),\n'
        '  "represents": a short phrase naming what real thing this element represents (the exemplars\' voice),\n'
        '  "howto": an object { "what": plain language what this element IS (not HTML), '
        '"what_you_can_do": what the operator can do with it, '
        '"how_to_change": how it is changed (which region/code/wire) },\n'
        '  "capabilities": a list from the allowed vocabulary only,\n'
        '  "maps_to_feature": a feature id COPIED VERBATIM from the inventory list, OR the literal '
        '"proposed". NEVER invent or adapt an id — if no inventory id matches the element\'s function '
        'EXACTLY, use "proposed" (a wrong/coined id corrupts the registry worse than an honest "proposed"),\n'
        '  "grounding": one of "built" | "proposed" | "uncertain" | "defer" (the tag described above).\n'
        "Example A (a clear, built feature — grounding \"built\"): {\"address\": \"ui://inbox/triage\", "
        "\"represents\": \"INB-lanes\", "
        "\"howto\": {\"what\": \"The triage control on the inbox.\", "
        "\"what_you_can_do\": \"Sort the awaiting decisions into lanes.\", "
        "\"how_to_change\": \"It lives in the inbox region (Inbox.tsx); changing it is a code change there.\"}, "
        "\"capabilities\": [\"pointable\", \"openable\"], \"maps_to_feature\": \"INB-lanes\", \"grounding\": \"built\"}\n"
        "Example B (NO inventory feature honestly fits — ABSTAIN, do NOT stretch onto a loosely-related id): "
        "for a generic chrome control like a 'Settings' nav item or an account/export button whose function "
        "matches NONE of the inventory feature labels — {\"address\": \"ui://chrome/settings\", "
        "\"represents\": \"Settings entry\", "
        "\"howto\": {\"what\": \"A settings entry point in the app chrome.\", "
        "\"what_you_can_do\": \"Open the settings (mockup-only — not a built feature here).\", "
        "\"how_to_change\": \"Mockup-only; no built code path maps to it yet.\"}, "
        "\"capabilities\": [\"pointable\"], \"maps_to_feature\": \"proposed\", \"grounding\": \"proposed\"}\n"
        "RULE OF THUMB for maps_to_feature: only return an inventory id when the element's function MATCHES "
        "that feature's label closely. If you find yourself reaching for an id that is merely RELATED (same "
        "area, similar word) but not the same function, that is the signal to return \"proposed\" with "
        "grounding \"proposed\"/\"uncertain\" instead. A wrong id corrupts the registry worse than an honest \"proposed\"."
    ),
    "output_schema": RegisterElementOut,
    # THE SEAM — the engine-real grounding path (run_role composes utterance + these declared inputs into
    # the user message; the role-spec `context` field is NOT auto-injected, so grounding rides HERE):
    #   "utterance"                          → (a) the per-unit candidate element (run_items places the
    #                                            unit here: snippet/text/tag/selector + parent addr+dossier).
    #   "run://<turn>/screen_reader/{mockup}"→ (b) the GROUND step's per-mockup summary (RG2 feeds MAP). The
    #                                            <mockup> materialization per element is the CASCADE/chainer's
    #                                            job (RG7) — declared as DATA here, mirroring check.py's
    #                                            run://<turn>/part-1 (the chainer is downstream, not here).
    #   "exemplars", "inventory"             → (c) SHARED across all N units, delivered ONCE via run_items'
    #                                            shared ctx (the bare-name extra-input path) — the
    #                                            context-efficiency win (no N× re-inline).
    # G3·S1 RESOLVED (2026-06-10): the per-mockup ground was declared as a TEMPLATED run:// address
    # ("run://<turn>/screen_reader/{mockup}") as a FORWARD CONTRACT — the {mockup} chainer never
    # existed in run_role (the docstring above flagged it). The engine now delivers per-unit ground
    # FOR REAL via run_items' unit_ctx ({field} templates over unit dicts) under the BARE NAME
    # `ground` — so the declaration becomes the real mechanism (the cascade's items step declares
    # unit_ctx={"ground": "run://rg-ground/{mockup}"}). One contract, one vehicle.
    "input_addresses": ("utterance", "ground", "exemplars", "inventory"),
    # FORWARD CONTRACT (declarative, like judge.py's prose `context`): the shared resolve-once grounding.
    # NOT a proven prompt-injection path — run_role does not auto-resolve the role-spec `context` field into
    # the prompt today (it is delivered via run_items' shared ctx, the bare-name input_addresses above).
    # Names the addressed, shared, resolve-once units so the cascade (RG7) knows what to provision once.
    "context": (
        "SHARED (resolve once, identical every unit — provisioned by the cascade via run_items' shared ctx): "
        "exemplars = 3-5 real entries from design/_system/addresses.json (voice/shape few-shot); "
        "inventory = the Feature & Function Inventory (design/register.json `features`, 58 ids) + the closed "
        "capability vocabulary (contracts/ui_info.py: pointable·spotlit·presentable·openable·driven). "
        "PER-UNIT (the unit at utterance): the element snippet/text/tag/selector + nearest registered "
        "ancestor address + its dossier (RG1's candidate schema). PER-MOCKUP: the screen_reader summary at "
        "run://<turn>/screen_reader/<mockup-i> (RG2's GROUND output)."
    ),
    "trigger": (
        "fires in the registration cast — run_items(register_element, candidates) maps it over the N "
        "EXTRACT units (RG4); reduced/deduped by run_reduce (RG5), confirmed by the jury+refcheck (RG6), "
        "declared as a step of the registry-generation cascade (RG7). It PROPOSES; the operator approves (RG8)."
    ),
    "model_binding": {"requires": ["chat", "json"], "default_model": None, "default_base_url": None},
    "mode_scope": {"registration"},
    "rules": [],
    "render_hint": {"shape": "dossier", "lane": "register_element"},
}
