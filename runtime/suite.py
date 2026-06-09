"""runtime/suite.py — the shared brain (the composition suite's core operations).

ONE brain, two faces: the UI bridge and the MCP server both call this. Graphs live in
the addressed store (S3 graphs registry), so the faces operate the SAME substrate even in
separate processes. Operations are the C7 generic verbs — generic over node-type
(they consult the registry), never one-per-type.
"""
from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Callable

from contracts.node_record import NodeInstance, Edge, Graph, XY, WH
from runtime import scheduler
from runtime.governance import Inbox, GovernanceError, guard, posture, AUTO
from runtime.registry import NodeRegistry
from runtime.roles import RoleRegistry, resolve_binding
from runtime.projections import ProjectionRegistry
from store.fs_store import FsStore

CONTENT_KINDS = ("constant", "document", "code", "file", "image", "source", "portal")


def _tag_system_origin(code: str) -> str:
    """Tag a brain-written node module with its provenance layer. Idempotent — the canvas
    reads ORIGIN to show "what a role changed" (context-13 layers)."""
    if "ORIGIN" in code:
        return code
    return "ORIGIN = 'system'  # brain-written (self-grown) — provenance layer\n" + code


def _load_corpus_element_addresses() -> list[tuple]:
    """S1 — project the 24+ element-level addresses from the design corpus (design/_system/addresses.json)
    into live UI_REGISTRY rows, so the live registry carries ELEMENT addresses (ui://inbox/build-review),
    not just the 7 region handles. ONE SOURCE (rule 8): the rows are READ from the corpus, never
    hand-transcribed/invented — addresses.json is the design-time superset the mockups carry.

    Each row is the registry's 6-tuple shape `(ref, kind, title, handle, caps, union-extras)`:
      • ref          — the FULL canonical corpus string `ui://<region>/<element>` (region-first grammar).
                       It is the DICT KEY in build_ui_info AND the value the corpus/mockup carries as
                       data-ui-ref (full-string carrier, the baked-in decision) — so an orphan check
                       (every used data-ui-ref is registered) passes by construction for the corpus form.
      • kind         — DERIVED by UnionAddressRecord.from_corpus (region 'canvas' → 'canvas', else
                       'chrome' = the DOM-resolved default). The live resolver dispatches on kind.
      • handle       — for kind=canvas → camera_ref='*' (the whole canvas, reusing the existing camera
                       path); else dom_handle = the FULL ui:// string (the corpus full-string carrier).
      • caps         — the corpus list-capabilities NORMALIZED to the canonical bool-object via
                       UnionAddressRecord (driven/driven-read-only → drivenReadOnly; unknown → fail loud).
      • union-extras — the S0 union-record join fields (region/represents/code) — carried for the
                       element rows because the corpus join IS known for them (unlike the 7 live regions).

    PRESERVE: this is ADDITIVE. The 7 hand-authored bare-ref rows (UI_REGISTRY below) keep their bare keys
    ('inbox' → ui://chrome/inbox), so show's handle_map, _registry_ui_target, and the walkthrough drive
    keep resolving exactly as before — they read those bare entries, which are untouched. The element rows
    use DISTINCT full-string keys (no collision with the bare keys; build_ui_info's duplicate-ref guard
    stays satisfied). FAIL LOUD (rule 4): a missing/malformed corpus file raises — the registry never
    silently ships region-only.
    """
    import json as _json
    from contracts.ui_info import UnionAddressRecord
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(here)
    path = os.path.join(repo_root, "design", "_system", "addresses.json")
    with open(path, encoding="utf-8") as f:
        data = _json.load(f)
    addresses = data.get("addresses", data)   # tolerate {addresses:{...}} or a bare map
    rows: list[tuple] = []
    for addr, rec in addresses.items():
        ur = UnionAddressRecord.from_corpus(addr, rec)   # validates grammar + normalizes caps (fail loud)
        if ur.kind == "canvas":
            handle = {"camera_ref": "*"}                  # reuse the whole-canvas camera path
        else:
            handle = {"dom_handle": addr}                 # full-string carrier (the baked-in decision)
        # I4: carry the union-record `tier` (governance action_class for COMMANDS at this address)
        # into the registry row's union-extras. ADDITIVE + OPTIONAL — None when the corpus entry
        # carries no tier (the default), so an untiered address falls back to the verb's own class.
        # D1: carry the union-record `howto` (the foundational affordance / how-to-use text) into the
        # registry row's union-extras alongside region/represents/code/tier. ADDITIVE + OPTIONAL — None
        # when the corpus entry authors no help (the default). The how-to stratum (`_r2_howto_at`) and
        # `address_help` read it from row[5] GENERICALLY (mirroring how `_describe_ui_address` reads
        # `represents`), never a per-element branch — Tim's not-hardwired correction.
        extras = {"region": ur.region, "represents": ur.represents, "code": ur.code,
                  "tier": ur.tier, "howto": ur.howto}
        rows.append((addr, ur.kind, (ur.title or addr), handle, dict(ur.capabilities), extras))
    return rows


def _strip_fences(code: str) -> str:
    c = code.strip()
    if c.startswith("```"):
        inner = c[3:]
        c = inner.split("```", 1)[0] if "```" in inner else inner.strip("`")
        if c.lstrip().startswith("python"):
            c = c.lstrip()[len("python"):]
    return c.strip()


# ── F1 up-translate: the code-enforced SHAPE of a commander-altitude framing ──────────────────────
# coa() up-translates a raw technical decision into a Commander-altitude VALUE choice. The brief's bar
# splits STRUCTURE (prove model-free) from WORDING-QUALITY (live-model-dependent). That split only
# holds if the SHAPE is code-enforced — otherwise a test degenerates to "framing is a non-empty
# string". So the framing is a SCHEMA (`fabric.client.complete(..., schema=CoaFraming)` retries+raises
# on a shape miss): a plain-language meaning, 2-3 options each with a trade-off, and a recommendation.
# The struct is PROJECTED to a `framing` TEXT string for FE compat (Grow.tsx renders surf.coa as text)
# and also exposed verbatim as `framing_struct`. A live model that can't satisfy the schema degrades
# (framed=False + raw) rather than emitting malformed prose — MORE honest, not less. (pydantic is a
# hard dep of fabric/client.py — already imported there; importing it here adds no new dependency.)
from pydantic import BaseModel, Field


class CoaOption(BaseModel):
    """One value-option the operator could choose, at their altitude — never the raw code fork."""
    label: str = Field(description="the option in plain commander terms (a value choice, not code)")
    tradeoff: str = Field(description="what you gain / give up by choosing this option")


class CoaFraming(BaseModel):
    """The CODE-ENFORCED shape of an up-translated decision (the structural bar coa must hit).
    SHAPE is proven model-free (an injected canned response validates against this); the WORDING
    quality is the live-model-dependent half (flagged for a model-up check)."""
    meaning: str = Field(description="what this decision means for the system, in plain terms")
    options: list[CoaOption] = Field(description="2-3 value options the operator could choose")
    recommendation: str = Field(description="a clear recommendation + a one-line why")

    def to_text(self) -> str:
        """Project the struct to the plain-language `framing` string the FE (Grow.tsx) renders.
        The struct is the proven shape; this is the human-legible lead the operator reads."""
        lines = [self.meaning, ""]
        for i, o in enumerate(self.options, 1):
            lines.append(f"{i}. {o.label} — {o.tradeoff}")
        lines += ["", f"Recommendation: {self.recommendation}"]
        return "\n".join(lines)


@dataclass(frozen=True)
class VerbSpec:
    """ONE source for a single RHM verb (replaces the 3 parallel tables RHM_VERBS / RHM_VERB_DESC /
    RHM_VERB_CLASS — which could drift). Each verb carries: its operator-facing gloss (desc), its
    GOVERNANCE action-class (the deterministic decide-for-me router input), the set of presence MODES
    in which it is OFFERED (mode-primary), and a PREDICATE over the live affordance context that
    further refines whether it makes sense RIGHT NOW (context-refines). The three legacy dicts are
    DERIVED from the registry below so there is no second copy to fall out of sync.

    The `modes`/`predicate` pair governs only what is OFFERED to the model (the tools array +
    the rendered verb list). The ONE whitelist that ENFORCES safety still lives in
    `_dispatch_rhm_action` (it keys on RHM_VERBS), so even a verb the model emits unprompted —
    or a forbidden verb — is refused there: narrowing the offer never weakens the gate (E6)."""
    desc: str                       # one-line operator-facing gloss (the old RHM_VERB_DESC value)
    action_class: str               # governance action-class (the old RHM_VERB_CLASS value)
    modes: frozenset                # the presence modes in which this verb is OFFERED
    predicate: Callable             # ctx(dict) -> bool — does this verb make sense in the current context


@dataclass(frozen=True)
class ModeSpec:
    """ONE source for a single TOP-LEVEL presence mode (E1 — the mode type-registry). Replaces the two
    parallel literals `MODES` (the tuple) and `MODE_DIRECTIVES` (the prose map), which could drift: both
    are now DERIVED from `MODE_SPECS` below (the same one-source move `VerbSpec`/`RHM_VERB_SPECS` made).

    A mode-type is NOT just a behavioural label — per Tim's load-bearing correction (direction §6,
    2026-06-06) **modes and context-resolution are ONE system**: a mode-type CARRIES its
    context-resolution declarations, so editing a mode-type changes BOTH behaviour (the directive) AND
    how context resolves under it (the `resolution` block). That is why `resolution` lives on the spec
    next to `directive` — one edit, one place, both change (§6.5).

    Fields:
      label      — short operator-facing name (the surface renders it).
      directive  — the behavioural prose injected into the RHM prompt (the OLD MODE_DIRECTIVES value).
      resolution — the CONTEXT-RESOLUTION DECLARATION: a dict the resolver consumes AS DATA (never a
                   mode-name branch — registry-is-truth). Keys (all optional; absent → today's default):
                     • strata        — frozenset of gather-stratum kinds this lens admits
                                       ({'annotation','chat','event','howto','run'}). None → admit all
                                       (byte-for-byte today). A lens can DROP a stratum (e.g. a terse
                                       lens that excludes 'howto').
                     • howto_detail  — 'full' (today) | 'terse' (truncate howto harder) | 'none'
                                       (suppress the how-to/affordance leg entirely).
                     • budget        — int char-cap OVERRIDE for this lens (None → the instance R2_BUDGET).
                                       A tight-attention mode (focus) resolves a SMALLER window.
                   This is the §6.3 unification made concrete: R2 becomes mode-parameterized — the
                   active mode-type's declarations choose which strata / how much / how, the instance
                   parameters (sub-type + rhm_mode-node overrides) supply the specifics, over the ONE
                   shared store.
      subtypes   — the HIERARCHY (§6.5: '≤8 top-level, each with sub-types'). A dict {subtype-id: {...}}
                   where each sub-type may OVERRIDE any `resolution` key for an INSTANCE. The mode-type
                   is the lens; the sub-type (an instance parameter) refines it. None/{} → no sub-types.
      consent    — the consent-interaction style this mode favours (§6B — descriptive declaration the
                   later rich consent layer reads; not yet wired into dispatch, captured as data)."""
    label: str
    directive: str
    resolution: dict | None = None
    subtypes: dict | None = None
    consent: str = "offer"


class Suite:
    # The STATE-TYPE REGISTRY (Possibility Space Block 19) — node "state" is a REGISTERED, single-source
    # set, NOT a hardcoded enum. `state()` reads its status-id strings from HERE (one source), and
    # `capabilities().node_states` exposes the set so the surface renders the vocabulary from the
    # registry (registry-is-truth) instead of hardcoding it. Each entry:
    #   id          — the status string `state()` reports for a node
    #   label       — short human label for the surface
    #   means       — what the status means (the surface shows this; descriptive, not executable)
    #   applies_to  — which RESOLVE-MODE this status can apply to ('compute' = executing nodes;
    #                 'reference' = reference-resolved nodes i.e. portals). This SCOPES the vocabulary:
    #                 executing nodes keep idle/ran/cached/stuck; reference nodes get live/empty.
    #   derived_when— the condition under which `state()` derives this status (descriptive metadata for
    #                 the surface; the derivation logic lives in `state()`, this is not an interpreter).
    # Step A: the four EXISTING statuses are lifted here UNCHANGED (compute-scoped) — their derivation in
    # state() is byte-for-byte as before, proven by the existing suites staying green.
    # Step B: two ADDITIVE states for reference-resolved nodes (portals): `live` (ref resolves to content)
    # and `empty` (ref is None/dangling/unresolved) — so a portal stops mis-reporting idle/cached on
    # reload. Executing nodes are UNAFFECTED (scoped by applies_to).
    #
    # S5 (Interactive Addressed Surface) — each state additionally carries a `render` block so the surface
    # paints the status vocabulary FROM the registry (one-source, rule 3) instead of the FE hardcoding a
    # state→token switch (the thing F3 must avoid). Each render = {token, icon, shape}:
    #   token — the CORPUS design-token (CSS custom property) the dot/badge colours from. Registry-is-truth
    #           (rule 8): every token here REFERENCES an EXISTING corpus token in design/_system/tokens.json
    #           → design-system.css (none invented). The four executing statuses bind to the corpus's existing
    #           node-status classes (.s-idle/.s-ran/.s-cache/.s-stuck, design-system.css:92-93 →
    #           --tx-3/--ok/--cache/--fail). The three with NO dedicated corpus CSS binding yet
    #           (failed/live/empty — design-substrate §3) bind to the closest existing semantic token:
    #           failed→--fail (it is an error state, shares stuck's error colour), live→--acc (the live/active
    #           accent), empty→--tx-3 (the muted/idle tone). FLAGGED: failed/live/empty have no DISTINCT corpus
    #           class today — adding .s-failed/.s-live/.s-empty CSS bindings is a FORM/corpus-lane follow-up
    #           (the corpus keeper / F3), out of this backend lane (do NOT hand-edit the generated CSS).
    #   icon  — a provisional glyph hint for the surface. FLAGGED: there is NO icon registry in the corpus
    #           today; these are sensible provisional values the FE/design-critic may revise (F3).
    #   shape — the dot shape hint ('dot' default; 'ring' marks the reference-window states). Provisional;
    #           the corpus "shape" token group is border-radii, not a state-shape vocabulary — also a
    #           FORM-lane follow-up. The design-critic (separate stage, rule 9) grades aesthetics, not this.
    NODE_STATES = (
        {"id": "idle", "label": "Idle", "applies_to": ("compute",),
         "means": "has never produced a result and holds none",
         "derived_when": "no fresh run result and the node's output address does not resolve",
         "render": {"token": "--tx-3", "icon": "circle", "shape": "dot"}},
        {"id": "ran", "label": "Ran", "applies_to": ("compute",),
         "means": "fired on the most recent run and produced a fresh result",
         "derived_when": "the node id is in the run result's `ran` set",
         "render": {"token": "--ok", "icon": "check", "shape": "dot"}},
        {"id": "cached", "label": "Cached", "applies_to": ("compute",),
         "means": "output already existed, so the memo gate skipped re-running it (the GPU/clock guard)",
         "derived_when": "the node id is in the run result's `skipped` set, OR (on reload) its output "
                         "address resolves to a stored result",
         "render": {"token": "--cache", "icon": "layers", "shape": "dot"}},
        {"id": "stuck", "label": "Stuck", "applies_to": ("compute",),
         "means": "could not fire because a required input never resolved (not a pruned branch)",
         "derived_when": "the node id is in the run result's `stuck` set, OR (on reload) the most recent "
                         "run event for the graph listed it stuck and it still holds no result",
         "render": {"token": "--fail", "icon": "pause", "shape": "dot"}},
        {"id": "failed", "label": "Failed", "applies_to": ("compute",),
         "means": "fired but RAISED — it threw an error during run (the scheduler contained it; downstream "
                  "stays unresolved). Distinct from stuck (an input never arrived) — here the node ran and "
                  "errored. The error message is carried on the node where the shape allows.",
         "derived_when": "the node id is a key in the run result's `failed` map (scheduler containment)",
         "render": {"token": "--fail", "icon": "alert", "shape": "dot"}},
        {"id": "live", "label": "Live", "applies_to": ("reference",),
         "means": "a live window onto its reference address, currently resolving to content",
         "derived_when": "RESOLVE='reference' and head(config.ref) resolves to a stored content hash",
         "render": {"token": "--acc", "icon": "broadcast", "shape": "ring"}},
        {"id": "empty", "label": "Empty", "applies_to": ("reference",),
         "means": "a live window whose reference is unset, dangling, or not yet resolvable",
         "derived_when": "RESOLVE='reference' and config.ref is empty/None or head(ref) does not resolve",
         "render": {"token": "--tx-3", "icon": "circle-dashed", "shape": "ring"}},
    )

    def __init__(self, store: FsStore, registry: NodeRegistry, nodes_dir: str | None = None,
                 role_registry: "RoleRegistry | None" = None):
        self.store = store
        self.registry = registry
        self.inbox = Inbox(store)
        self.nodes_dir = nodes_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes")
        self.panels_dir = os.path.join(os.path.dirname(self.nodes_dir), "panels")  # UI extension point
        # G2 (C2.1) — the FILE-DISCOVERED role registry. Derived from the repo root like nodes_dir (the
        # `roles/` sibling of `nodes/`), discovered INTERNALLY so the required Suite(store, reg, nodes_dir)
        # signature every test uses is unchanged (an optional injection param at most). `ROLE_REGISTRY` is
        # built as {role_id: role.spec} so resolve_role/roles() read the SAME dict-view they read from the
        # old class constant — the judge's effective binding is byte-identical (C2.2).
        self.roles_dir = os.path.join(os.path.dirname(self.nodes_dir), "roles")
        # #56/#58 — the skill/context registry dirs (siblings of roles/, mirroring how cognition.py
        # derives them). Suite-instance-relative so a test Suite over a throwaway repo writes + reads
        # its OWN skills/contexts (not the live tree); in production these coincide with
        # cognition._SKILLS_DIR/_CONTEXTS_DIR (the global readers — list_skills_contexts/resolve_address).
        self.skills_dir = os.path.join(os.path.dirname(self.nodes_dir), "skills")
        self.contexts_dir = os.path.join(os.path.dirname(self.nodes_dir), "contexts")
        # Cognition Engine K1/P1 — the FILE-DISCOVERED PROJECTION registry (the corpus-pillar lens set).
        # Discovered exactly like role_registry above (the `projections/` sibling of `nodes/`), so the
        # cognition SELECTS (cognition_info / available_inputs) PROJECT the live discovered lens set
        # rather than a hardcoded list: drop a `projections/<id>.py`, restart the bridge, and the lens
        # appears in the select with NO code change (the PART 4.3 add-a-row=a-FILE bar). The capture-role
        # output_schema (model_projections()) + the Group-L spaces (embeddable()) are consumed by the
        # ENGINE/SURFACE lanes; this SUITE lane only PROJECTS the registry into the selects. As the other
        # 6 file-discovered registries (lifters/mark-types/ai-tics/relation-types/generation-policies/
        # forms) land, they instantiate here the SAME way and the selects project them too.
        self.projections_dir = os.path.join(os.path.dirname(self.nodes_dir), "projections")
        self.projection_registry = ProjectionRegistry().discover([self.projections_dir])
        # The OTHER 6 file-discovered corpus/cognition registries (719f82d) — discovered the SAME way
        # as projection_registry (the ONE registry mechanism, reuse-don't-parallel). Each is a sibling
        # `<name>/` dir of `nodes/`. They feed the authoring selects (available_inputs) + the create_*
        # tools (the shared `_write_registry_file` helper writes a `<name>/<id>.py` through the registry's
        # OWN gate). `_REGISTRIES` is the single-source table the create_* helper + the selects read, so
        # adding a registry = one row here (registry-is-truth, no per-registry branch). Each tuple is
        # (dir-attr, registry-instance-attr, RegistryClass, module-const, friendly-kind).
        from runtime.lifters import LifterRegistry
        from runtime.mark_types import MarkTypeRegistry
        from runtime.generation_policies import GenerationPolicyRegistry
        from runtime.relation_types import RelationTypeRegistry
        from runtime.ai_tics import AiTicRegistry
        from runtime.forms import FormRegistry
        _base = os.path.dirname(self.nodes_dir)
        self.lifters_dir = os.path.join(_base, "lifters")
        self.mark_types_dir = os.path.join(_base, "mark_types")
        self.generation_policies_dir = os.path.join(_base, "generation_policies")
        self.relation_types_dir = os.path.join(_base, "relation_types")
        self.ai_tics_dir = os.path.join(_base, "ai_tics")
        self.forms_dir = os.path.join(_base, "forms")
        self.lifter_registry = LifterRegistry().discover([self.lifters_dir])
        self.mark_type_registry = MarkTypeRegistry().discover([self.mark_types_dir])
        self.generation_policy_registry = GenerationPolicyRegistry().discover([self.generation_policies_dir])
        self.relation_type_registry = RelationTypeRegistry().discover([self.relation_types_dir])
        self.ai_tic_registry = AiTicRegistry().discover([self.ai_tics_dir])
        self.form_registry = FormRegistry().discover([self.forms_dir])
        # The single-source create_*-authorable table: (kind, dir-attr, registry-attr, RegistryClass,
        # module-const-name). The create_* methods derive from this — never a per-registry literal. A bad
        # spec is REFUSED via the registry's OWN discover() gate (mirrors create_projection).
        #   SCOPED TO THE 4 PURE-DATA REGISTRIES ON PURPOSE: declarative-direct authoring renders a DATA
        #   dict (pprint → a PYTHON-literal `<CONST> = {...}`) and arrives over MCP as JSON. So ONLY the
        #   registries whose ROW is pure data are create_*-authorable here: mark_type · generation_policy ·
        #   relation_type · ai_tic. The OTHER TWO discovered registries — `lifter` (an `extract` CALLABLE)
        #   and `form` (a `match` CALLABLE) — carry EXECUTABLE CODE in their row; pprint cannot serialize a
        #   function and MCP-JSON cannot carry one, so a data-create would ALWAYS fail-loud at the gate (a
        #   broken affordance). That is exactly the FLOOR's "executable-code create stays GATED" line: a
        #   lifter/form needs a CODE-render+gate authoring contract (create_role-style render of a `def`, or
        #   the gated propose→apply path), which is net-new + unspecified → FLAGGED for the operator, NOT
        #   invented here. lifter/form stay fully LISTABLE (selects) + GOVERNED (floor) — only data-CREATE
        #   excludes them. (build-against-the-contracts: the floor wins over the brief's "data registries"
        #   premise, which is false for these 2.)
        self._CORPUS_REGISTRIES = {
            "mark_type":         ("mark_types_dir",          "mark_type_registry",         MarkTypeRegistry,         "MARK_TYPE"),
            "generation_policy": ("generation_policies_dir", "generation_policy_registry", GenerationPolicyRegistry, "GENERATION_POLICY"),
            "relation_type":     ("relation_types_dir",      "relation_type_registry",     RelationTypeRegistry,     "RELATION_TYPE"),
            "ai_tic":            ("ai_tics_dir",             "ai_tic_registry",            AiTicRegistry,            "AI_TIC"),
        }
        self.role_registry = role_registry or RoleRegistry().discover([self.roles_dir])
        self.ROLE_REGISTRY = {rid: self.role_registry[rid].spec for rid in self.role_registry}
        # B-FIX (P3) — PROTECTED_ROLES DERIVED, not a second-copy literal. The spike subset comes from its
        # SOURCE (cognition.SPIKE_ROLES — the roles cognition.py imports by name); the suite-owned config
        # roles stay declared on the class (suite.py's own by-name dependencies; no other source-of-truth).
        # The union is the full protected set. A fail-loud drift guard: cognition's spike set must be a
        # subset of what we protect (if cognition adds a spike role, the assert FAILS until it's reflected —
        # never a silent gap). Imported here (not at class-body) to avoid the class/cognition import cycle.
        from runtime import cognition as _cog_pr
        _spike = tuple(sorted(_cog_pr.SPIKE_ROLES))            # focus/recall/ground (registry-derived)
        self.PROTECTED_ROLES = tuple(dict.fromkeys(_spike + self._SUITE_OWNED_PROTECTED_ROLES))
        assert set(_cog_pr.SPIKE_ROLES) <= set(self.PROTECTED_ROLES), (
            f"PROTECTED_ROLES drift: cognition.SPIKE_ROLES {sorted(_cog_pr.SPIKE_ROLES)} is not fully "
            f"protected by {sorted(self.PROTECTED_ROLES)} — a cognition-imported spike role would be "
            f"deletable, which bricks import. Fail loud (rules 3+4).")
        # Cognition Engine GROUP N — the SAVED-CASCADE registry (a saved cascade = a declared ActionRegistry
        # row). REUSE coherence_actions.ActionRegistry (the one-door validator+store EXISTS — never a 2nd
        # registry); persisted to a json file UNDER THE STORE ROOT (ext4 — never /mnt/c), so a reload sees
        # saved cascades (persistence-survives-reload). save_cascade validates via build_action + saves here;
        # run_cascade loads from here + fires the GROUP-N runner (cognition.run_cascade). Drift home: the
        # cascade-runner section in runtime/AGENTS.md.
        from runtime.coherence_actions import ActionRegistry as _ActionRegistry
        self.cascade_registry = _ActionRegistry(str(self.store.root / "cascades.json"))
        # E2 — the INCREMENTAL run-index cache (#54 efficiency). `list_runs`/`find_runs` are a READ-TIME
        # PROJECTION over the `op.run` event log; the naive form re-reads + re-filters the WHOLE log on
        # EVERY call (O(events)) — caught at scale. The op.run log is append-only with monotonic-unique
        # seqs (store.append_event T1-SEQ), so the projection is cheaply INCREMENTAL: hold the projected
        # rows + a high-water seq; each call reads ONLY `events_since(high_water)` (the delta), projects
        # the new op.run events, appends, advances the high-water. This is NOT a parallel store/index — the
        # op.run log STAYS the source of truth (registry-is-truth); the cache is a pure derived projection
        # that a fresh Suite rebuilds from the log (no persistence, no fs_store edit). Cross-PROCESS safe:
        # each process reads the disk tail past ITS OWN high-water and appends are immutable, so two Suites
        # over one store dir each converge on the same rows (a Suite never sees another's in-RAM cache, it
        # re-reads the shared log delta). Guarded by a lock — the bridge is a ThreadingHTTPServer (concurrent
        # list_runs across threads of one process would race the read-modify-write of the cache).
        import threading as _t
        self._run_index_lock = _t.Lock()
        self._run_index_rows: list[dict] = []   # projected ENGINE_RUN_OPS rows, oldest-first (one per concrete addr)
        self._run_index_hw: int = -1            # high-water: the largest event seq folded into _run_index_rows
        # The bridge is a ThreadingHTTPServer → concurrent POST /api/review/next run in separate threads of
        # ONE process over this one Suite. The session-cursor advance is a read-modify-write (load→run→save)
        # with no lock → concurrent calls dropped advances (lost update). A per-session in-process lock
        # serializes that critical section. Guarded so a CAS re-read still protects across processes/restart.
        import threading as _t
        self._session_locks_guard = _t.Lock()
        self._session_locks: dict = {}
        # WIRE exactly-once: the dispatch CHECK (read the event log for a prior decision.dispatch) →
        # CLAIM (emit decision.dispatch) is a read-modify-write critical section. The bridge is a
        # ThreadingHTTPServer over ONE Suite, so two concurrent dispatch_decision calls on the same
        # approved seq would BOTH clear the check before either claims → double-launch. A per-seq
        # in-process lock serializes that section (mirrors the per-session lock pattern above); the
        # durable decision.dispatch event remains the cross-process/restart guarantee.
        self._dispatch_locks_guard = _t.Lock()
        self._dispatch_locks: dict = {}
        # WIRE-ASYNC — the resolve→dispatch trigger must NOT run the build INSIDE the approving HTTP
        # request. `drive_dispatchable` → `dispatch_decision` → `launch` runs a BLOCKING `claude -p`
        # subprocess (up to DEFAULT_TIMEOUT_S=900s); doing that synchronously means the whole build
        # ran inside POST /api/resolve, so a dropped client connection (curl timeout, UI fetch timeout,
        # phone backgrounding) abandoned the request thread → the build orphaned as a 'crashed' dispatch
        # (a decision.dispatch claim with no terminal event), never re-launched (exactly-once). The fix:
        # resolve_surfaced writes the operator verdict SYNCHRONOUSLY (the consent record is durable
        # immediately), then hands the build EXECUTION to a BACKGROUND daemon thread owned HERE, and
        # returns a prompt ack. The background thread completes + emits its terminal event + commits +
        # surfaces via the SAME event log/SSE stream INDEPENDENTLY of the approving client connection.
        # We TRACK the live threads so tests can join them (wire_wait_for_dispatch) and so a caller can
        # see they exist; daemon=True so a never-finished thread can't block process shutdown.
        self._wire_threads_guard = _t.Lock()
        self._wire_threads: list = []
        # R1 — the BACKEND-HELD current `ui://` locus (seams-rhm Seam 4: "there is no stored
        # current-locus anywhere in suite/store" — this is the net-new piece). Today the operator's
        # locus exists ONLY FE-side, shipped per-request as `focus.selected`; nothing is remembered
        # between calls. R1 holds the most-recent INDICATED `ui://` address (set in the chat path when
        # I1's widened `focus` carries one — see _chat_context) so the RHM can READ where the operator
        # IS across turns. PERSISTENCE = in-memory on this long-lived Suite instance (DELIBERATE,
        # per the guide): single live operator; R2's auto-resolve reads it LIVE off the same Suite in
        # the same process; the FE re-ships `focus` every request so a restart re-establishes it
        # instantly (restart-survival buys nothing); store-backing would be a schema/contract addition
        # with no consumer. It PERSISTS ALONGSIDE the per-request `focus` path — never replacing it.
        # Exposed via current_locus() for R2 to consume (R2 is NOT wired here — held + set + readable).
        self._current_locus: str | None = None

        # X17 (Convergence, D2) — THE COMPOSITION IS CONFIGURABLE. The R2 ranking WEIGHTS (recency λ ·
        # proximity · pin · semantic), the window BUDGET cap, and the run-versions bound were hardcoded
        # CLASS constants (still defined on the class above, as the DEFAULT FLOOR). Here we RESOLVE each
        # from the env (the fabric.config `os.environ.get(default)` pattern — NO parallel config system,
        # consistent with CODEEDGES_DEPTH / COMPANY_WIRE_PERMISSION) INTO INSTANCE attributes that shadow
        # the class defaults. So retuning the context composition needs NO code change: a FRESH Suite (a
        # restart re-reads) picks up the env. The default is the OLD constant → byte-for-behaviour when
        # unset (every R2 preserve suite stays green). Reading into INSTANCE attrs (not re-binding the
        # class) keeps BOTH `Suite.R2_BUDGET` class-access (sibling suites) AND `su.R2_BUDGET = …`
        # per-instance override (conv_semantic_rank) working. FAIL LOUD on a malformed value (rule 4):
        # _cfg_float/_cfg_int raise a clear, knob-NAMED error — never a silent wrong/zero value. Exposed
        # in capabilities().composition_config so the surface/fleet can READ them (registry-is-truth).
        self.R2_LAMBDA = self._cfg_float("COMPANY_R2_LAMBDA", type(self).R2_LAMBDA)
        self.R2_PROXIMITY_WEIGHT = self._cfg_float("COMPANY_R2_PROXIMITY_WEIGHT", type(self).R2_PROXIMITY_WEIGHT)
        self.R2_PIN_WEIGHT = self._cfg_float("COMPANY_R2_PIN_WEIGHT", type(self).R2_PIN_WEIGHT)
        self.R2_SEMANTIC_WEIGHT = self._cfg_float("COMPANY_R2_SEMANTIC_WEIGHT", type(self).R2_SEMANTIC_WEIGHT)
        self.R2_BUDGET = self._cfg_int("COMPANY_R2_BUDGET", type(self).R2_BUDGET)
        self.R2_RUN_VERSIONS = self._cfg_int("COMPANY_R2_RUN_VERSIONS", type(self).R2_RUN_VERSIONS)
        self.R2_HOWTO_MAX = self._cfg_int("COMPANY_R2_HOWTO_MAX", type(self).R2_HOWTO_MAX)   # D1 flood guard
        self.R2_HOWTO_TERSE = self._cfg_int("COMPANY_R2_HOWTO_TERSE", type(self).R2_HOWTO_TERSE)  # E1 terse cap
        self.R2_COGNITION_TURNS = self._cfg_int("COMPANY_R2_COGNITION_TURNS", type(self).R2_COGNITION_TURNS)  # GROUP J
        self.R2_COGNITION_PER_ROLE = self._cfg_int("COMPANY_R2_COGNITION_PER_ROLE", type(self).R2_COGNITION_PER_ROLE)  # GROUP J
        # E2 (mode auto-detect as a CONFIG TOGGLE, not hardcoded — direction §6.5) — resolve the toggle
        # from the env into an instance attr (the SAME X17 pattern). VALUES (fail-loud-validated by
        # _cfg_choice): 'off' (manual only — the default, byte-for-byte today's operator-selected modes),
        # 'suggest' (auto-detection PROPOSES a mode, never switches), 'auto' (auto-detection SWITCHES).
        # Exposed in capabilities().composition_config so the surface reads + SETS it. The DETECTOR
        # that produces a candidate is a deferred seam (§11: zero detector exists today) — `autodetect_mode`
        # honours the toggle over a SUPPLIED candidate; it never fabricates detection (rule 4/8).
        # GC6 (E2-live) — MODE_AUTODETECT is now a RUNTIME-SETTABLE slot (set_rhm_config), so it must
        # SURVIVE a reload like every other config slot. PRECEDENCE on a fresh Suite: the PERSISTED store
        # value (MODE_NODE config, written by set_rhm_config) wins → else the env (_cfg_choice, X17) → else
        # the class default. So a value set through the surface is honoured by a fresh Suite re-running
        # __init__ (the reload test), while an unset slot still byte-for-byte resolves the env/class default
        # (every preserve suite stays green). The persisted value is fail-loud-validated by set_rhm_config
        # before it lands, so reading it here needs no re-validation; _rhm_cfg() returns {} safely at first
        # boot (no rhm node yet) → the env/class path. self.store is assigned above (line 229), so the
        # _rhm_cfg() read here is safe.
        _persisted_autodetect = self._rhm_cfg().get("mode_autodetect")
        self.MODE_AUTODETECT = (_persisted_autodetect if _persisted_autodetect in self.MODE_AUTODETECT_OPTIONS
                                else self._cfg_choice("COMPANY_MODE_AUTODETECT",
                                                      type(self).MODE_AUTODETECT, self.MODE_AUTODETECT_OPTIONS))

    @staticmethod
    def _cfg_float(env_name: str, default: float) -> float:
        """X17 — resolve a float knob from the env (default = the class constant). FAIL LOUD on a
        malformed value with a knob-NAMED error (rule 4 — never a silent wrong/zero value). The default
        is passed as the NUMERIC value (never round-tripped through a string) so the precision of e.g.
        R2_LAMBDA = 1/(3·24·3600) is preserved byte-for-behaviour when the env is unset."""
        raw = os.environ.get(env_name)
        if raw is None:
            return default
        try:
            return float(raw)
        except (TypeError, ValueError):
            raise ValueError(f"{env_name}={raw!r} is not a valid float — fix the env value "
                             f"(X17 composition knob; default {default!r})")

    @staticmethod
    def _cfg_int(env_name: str, default: int) -> int:
        """X17 — resolve an int knob from the env (default = the class constant). FAIL LOUD on a
        malformed value with a knob-NAMED error (rule 4 — never a silent wrong/zero value)."""
        raw = os.environ.get(env_name)
        if raw is None:
            return default
        try:
            return int(raw)
        except (TypeError, ValueError):
            raise ValueError(f"{env_name}={raw!r} is not a valid int — fix the env value "
                             f"(X17 composition knob; default {default!r})")

    @staticmethod
    def _cfg_choice(env_name: str, default: str, options) -> str:
        """E2 — resolve a STRING-ENUM knob from the env (default = the class constant). FAIL LOUD on a
        value outside `options` (rule 4 — never a silent wrong/default). Mirrors _cfg_int/_cfg_float."""
        raw = os.environ.get(env_name)
        if raw is None:
            return default
        if raw not in options:
            raise ValueError(f"{env_name}={raw!r} is not one of {tuple(options)} — fix the env value "
                             f"(config toggle; default {default!r})")
        return raw

    def _session_lock(self, session_id: str):
        """One reentrant-safe lock per session, created on demand (threadsafe)."""
        import threading as _t
        with self._session_locks_guard:
            lk = self._session_locks.get(session_id)
            if lk is None:
                lk = _t.Lock()
                self._session_locks[session_id] = lk
            return lk

    def _dispatch_lock(self, derived_from: int):
        """One lock per resolve `seq`, created on demand (threadsafe) — serializes the
        exactly-once CHECK→CLAIM critical section in dispatch_decision so a true race
        (two threads, one Suite) cannot double-launch the same approved decision."""
        import threading as _t
        with self._dispatch_locks_guard:
            lk = self._dispatch_locks.get(derived_from)
            if lk is None:
                lk = _t.Lock()
                self._dispatch_locks[derived_from] = lk
            return lk

    # ── WIRE-ASYNC · background dispatch (decouple the build from the approving request) ──────────
    def _drive_dispatchable_bg(self, *, sid: str | None, launcher=None, verifier=None,
                               suite_runner=None, critic=None, cap: int | None = None,
                               repo: str | None = None, committer=None):
        """Spawn a BACKGROUND daemon thread that runs ONE `drive_dispatchable` watcher pass, decoupled
        from whatever request triggered it. The thread:
          • runs the full GOVERNED path (drive_dispatchable → dispatch_decision: the per-seq lock + the
            durable decision.dispatch CLAIM + the AUTO-posture gate + launch + verify + the [self-build]
            commit + the guarded close + surface-for-review) — REUSED byte-for-byte, never re-implemented,
            so EXACTLY-ONCE, the gates, and git-safety are preserved (the claim is emitted under the
            SAME locks INSIDE dispatch_decision regardless of which thread runs it);
          • emits its terminal event (decision.implemented / decision.verify) + surfaces the review via
            the SAME store/event log → the SSE stream delivers it to the UI, INDEPENDENT of the
            approving client connection (a dropped connection no longer orphans the build);
          • is daemon=True so a long/never-finishing build can't block process shutdown;
          • CATCHES every exception and emits a FAIL-LOUD decision.verify terminal (rule 4 — a silently
            dead thread = an orphaned dispatch, exactly the bug this lane closes). resurface_crashed
            still covers a thread that genuinely dies (e.g. the interpreter is torn down), because the
            claim event with no terminal is its signal — but the normal-exception path fails loud HERE.

        Returns the spawned threading.Thread (tracked in self._wire_threads). The injectables
        (launcher/verifier/committer/cap/repo) are threaded through so tests inject a fake runner +
        a no-op committer (never a real `claude -p`, never a live commit)."""
        import threading as _t

        def _run():
            try:
                implement = __import__("runtime.implement", fromlist=["drive_dispatchable"])
                implement.drive_dispatchable(
                    self, launcher=launcher, verifier=verifier, suite_runner=suite_runner,
                    critic=critic, cap=cap, repo=repo, committer=committer)
            except Exception as e:   # noqa: BLE001 — fail loud, never a silent thread death
                # A silently-dead background thread would re-create the orphan bug (a claim with no
                # terminal). Emit a loud terminal so now()'s last-event surfaces it and the SSE stream
                # delivers it to the UI. The operator's resolve already committed (resolve_surfaced),
                # so operator-only resolve holds; only the build EXECUTION failed.
                try:
                    self._emit("decision.verify",
                               f"WIRE-ASYNC background dispatch thread errored (build not driven): {e}",
                               surfaced=sid, derived_from=None, verify_passed=False,
                               address="ui://chrome/inbox")
                except Exception:
                    pass   # the emit itself failing must not crash the daemon thread teardown
            finally:
                # drop ourselves from the live-thread registry (best-effort; the GC handles the rest)
                with self._wire_threads_guard:
                    me = _t.current_thread()
                    if me in self._wire_threads:
                        self._wire_threads.remove(me)

        th = _t.Thread(target=_run, name=f"wire-dispatch-{sid or '?'}", daemon=True)
        with self._wire_threads_guard:
            self._wire_threads.append(th)
        th.start()
        return th

    def wire_wait_for_dispatch(self, timeout: float | None = None) -> bool:
        """TEST/OPS helper — join every live WIRE-ASYNC background dispatch thread (a SNAPSHOT taken
        under the guard, so a thread that finishes + removes itself mid-join is fine). Returns True if
        all joined within `timeout`, False if any is still alive. NOT used in the production request
        path (the whole point is that the request does NOT wait) — it exists so a by-use test can prove
        the build COMPLETES in the background after the resolve returned, and so ops can drain on demand."""
        with self._wire_threads_guard:
            snapshot = list(self._wire_threads)
        for th in snapshot:
            th.join(timeout)
            if th.is_alive():
                return False
        return True

    def _emit(self, kind: str, summary: str, **meta) -> None:
        """Append one TELEMETRY event to the captured trajectory (I2). Lenient by design: a telemetry
        emit must never break the action it records, so a store hiccup is swallowed here. This is the
        RIGHT posture for narration/visibility events — but it is the WRONG posture for a DURABLE CLAIM
        whose absence changes behavior (e.g. the exactly-once decision.dispatch claim): for those use
        _emit_durable, which fails loud (T1-EMIT). Never route a safety-critical claim through _emit."""
        try:
            self.store.append_event({"kind": kind, "summary": summary, **meta})
        except Exception:
            pass

    def emit_run_record(self, op: str, duration_ms: int, **conditions) -> None:
        """G7 / Introspective Data Building (Tim's law) — FIRST INSTANCE, the voice/model layer learning
        by use. A typed run-record: an operation + HOW LONG IT TOOK + the CONDITIONS it happened under,
        into the EXISTING event log (kind='op.run') — NOT a new analytics store. A datum without its
        conditions is noise, so callers pass model/ear/engine/mode/ok/etc. Lenient-emit (telemetry must
        never break the op it records; the raw record is cheap + append-only). Rollups (n·median·p95) are
        DERIVED off the hot path from these — never computed here. 'How long it TOOK' lands here; 'how
        long it TAKES' (the prior/estimate) lives in the declared specs (role knobs, services.json
        vram/wake) — the measured refines the estimate. Generalises Company-wide past voice (cognition,
        RHM verbs, surface, errors) — same emit→substrate→rollup loop, per-type."""
        self._emit("op.run", f"{op} · {duration_ms}ms", op=op, duration_ms=duration_ms, **conditions)

    def run_stats(self, op: str | None = None, since: int = -1) -> dict:
        """G7 ROLLUP — raw op.run run-records → DISTRIBUTIONS (n · median · p95 · min · max), grouped by
        (op, model/engine). The read-half of introspective-data-building: the trace becomes KNOWLEDGE.
        Read-time aggregation over the event log — NEVER on the hot path (callers hit this on demand /
        a cadence). Feeds the Manifest's measured cells + the resource manager's pre-warm decisions.
        `op` filters to one operation; `since` is an event seq (default -1 = all)."""
        import statistics
        evs = [e for e in self.events_since(since) if e.get("kind") == "op.run"]
        if op:
            evs = [e for e in evs if e.get("op") == op]

        def dist(vals):
            vals = sorted(v for v in vals if isinstance(v, (int, float)))
            if not vals:
                return None
            n = len(vals)
            return {"n": n, "median": round(statistics.median(vals), 1),
                    "p95": vals[min(n - 1, int(round(0.95 * (n - 1))))],
                    "min": vals[0], "max": vals[-1]}

        groups: dict = {}
        for e in evs:
            key = (e.get("op"), e.get("model") or e.get("engine") or "")
            groups.setdefault(key, []).append(e)
        out = []
        for (o, who), es in groups.items():
            rec = {"op": o, "who": who, "n": len(es), "duration_ms": dist([e.get("duration_ms") for e in es])}
            for f in ("stt_ms", "think_ms", "tts_ms", "queue_ms", "chunks", "chunks_done", "chunks_total"):  # extra timing/condition fields
                d = dist([e.get(f) for e in es if e.get(f) is not None])
                if d:
                    rec[f] = d
            out.append(rec)
        return {"ops": sorted(out, key=lambda r: -r["n"]), "total_records": len(evs)}

    # the closed op-set of the ENGINE runs that emit the op.run RUN INDEX (#54 storage-discovery). A
    # run-projection lists ONLY these (NOT every op.run telemetry record — voice.client, voice.turn, etc.
    # also ride op.run). registry-is-truth: the emit sites (run_items/run_reduce in cognition.py, run_role
    # in the MCP wrapper) and this filter both name the SAME closed set; a new engine run-op is added here.
    ENGINE_RUN_OPS = ("cognition.run_role", "cognition.run_items", "cognition.run_reduce")

    @staticmethod
    def _project_run_event(e: dict) -> list[dict]:
        """#54 — project ONE `op.run` ENGINE_RUN_OP event into its discovered ROW(s). One event carries the
        per-fan `addresses` list (the C1.6 one-emit-per-fan discipline) → one row PER concrete run:// address
        (run://<turn>/<role>[/<i>]). A reduce records with no address → one row with address=None. SINGLE
        SOURCE of the row shape, shared by the cold rebuild + the incremental fold (so a fold + a full scan
        produce byte-identical rows)."""
        addrs = e.get("addresses") or [None]                  # a reduce records with no feedable address
        return [{
            "address": addr, "op": e.get("op"), "run_op": e.get("run_op"),
            "turn_id": e.get("turn_id"), "role": e.get("role"),
            "duration_ms": e.get("duration_ms"), "seq": e.get("seq"), "ts": e.get("ts"),
            # O3 (introspective-data-building) — WHY the run stopped, carried onto the discovered row so
            # find_runs surfaces it (present-only: None when the emit carried no finish_reason — embed ops,
            # older records — never fabricated).
            "finish_reason": e.get("finish_reason"),
        } for addr in addrs]

    def _run_index_fold(self) -> list[dict]:
        """E2 — the INCREMENTAL run-index. Return the projected ENGINE_RUN_OPS rows (oldest-first), folding
        ONLY the events appended since the held high-water seq (NOT a full re-read of the op.run log).

        Why this is correct + cheap: the event log is append-only with monotonic-unique seqs (T1-SEQ), so a
        row, once projected, never changes; `events_since(hw)` returns exactly the events with seq > hw,
        oldest-first. We read the tail delta ONCE, advance the high-water over the WHOLE delta (so the next
        call's events_since never re-yields an event we've seen — the last delta event may itself be a
        non-ENGINE_RUN_OP, so the cursor must move past it too), and project the ENGINE_RUN_OP subset into
        rows. The FIRST call (hw=-1) folds the whole log ONCE (the unavoidable cold read — same cost as
        before); EVERY subsequent call reads only the new tail. Cross-process safe: a sibling process's
        appends land on the shared disk log and this process picks them up on its next call (it reads past
        its OWN high-water).

        Held under `_run_index_lock` — the read-modify-write of (rows, hw) would otherwise race across the
        bridge's threads. Returns a SNAPSHOT COPY so the caller can filter/slice without holding the lock."""
        with self._run_index_lock:
            delta = self.events_since(self._run_index_hw)     # the tail past our high-water (read ONCE)
            if delta:
                self._run_index_hw = delta[-1].get("seq", self._run_index_hw)
            for e in delta:
                if e.get("kind") == "op.run" and e.get("op") in self.ENGINE_RUN_OPS:
                    self._run_index_rows.extend(self._project_run_event(e))
            # SNAPSHOT — a shallow copy of the row list; the rows themselves are never mutated after projection.
            return list(self._run_index_rows)

    def list_runs(self, op: str | None = None, run_op: str | None = None,
                  since: int = -1, limit: int = 50) -> dict:
        """#54 STORAGE-DISCOVERY — the RUN INDEX: make past engine runs DISCOVERABLE as inputs (not just
        known-by-address). A READ-TIME projection over the `op.run` event log (the run_stats pattern — no
        maintained index, no new store; reuse-don't-parallel — the op.run log IS the index). The discovery:
        an agent/FE can now LIST past runs + their run:// addresses → feed one as an input (resolve_address)
        or re-run, instead of only reading a run it already KNOWS the address of.

        E2 EFFICIENCY — the projection is INCREMENTAL (`_run_index_fold`): it no longer re-reads the WHOLE
        op.run log on every call (the O(events) cost caught at scale). It holds the projected rows + a
        high-water seq and folds only the events_since(high_water) delta. The op.run log STAYS the source of
        truth (registry-is-truth, no parallel store, no fs_store edit) — the cache is a pure derived
        projection a fresh Suite rebuilds from the log. `since`/`op`/`run_op`/`limit` are applied as filters
        on the cached rows (each row carries its `seq`).

        Filters to the closed ENGINE_RUN_OPS (the engine runs — NOT the voice/etc. op.run telemetry). One
        op.run event carries the per-fan `addresses` list (the C1.6 one-emit-per-fan discipline); this
        EXPANDS it into one discovered ROW PER concrete run:// address (run://<turn>/<role>[/<i>]), each a
        RESOLVABLE address (the prefix is never set_ref'd, only the per-unit address is). A reduce records
        with no address (its joined output is not landed) → one row with address=None.

        Each row: {address, op, run_op, turn_id, role, duration_ms, seq, ts}. Newest-first. `op` filters to
        one ENGINE_RUN_OP; `run_op` filters by the operation (generate|embed|role|rule|cluster); `since` is
        an event seq (-1 = all); `limit` caps the returned rows. Returns {runs:[...], total_records:int}."""
        if op is not None and op not in self.ENGINE_RUN_OPS:
            raise ValueError(
                f"list_runs: unknown engine run-op {op!r} — the run index covers {list(self.ENGINE_RUN_OPS)} "
                f"(the engine runs that emit the op.run index). Fail loud (never project a fabricated op).")
        rows = self._run_index_fold()                         # incremental: only the new tail is projected
        if since is not None and since != -1:
            rows = [r for r in rows if (r.get("seq") or 0) > since]   # `since` is an exclusive event-seq cursor
        if op:
            rows = [r for r in rows if r.get("op") == op]
        if run_op:
            rows = [r for r in rows if r.get("run_op") == run_op]
        # total_records = the count of underlying op.run EVENTS (after the same filters), NOT expanded rows
        # — a fan event projects to N rows but is ONE record (preserves the pre-E2 `len(evs)` semantics).
        total = len({r.get("seq") for r in rows})
        rows = list(reversed(rows))                           # newest-first (the cache holds oldest-first)
        return {"runs": rows[:limit], "total_records": total}

    def find_runs(self, role: str | None = None, op: str | None = None,
                  run_op: str | None = None, since: int = -1, limit: int = 50) -> dict:
        """#54 — the FILTERED run index (the discovery's query face): list_runs narrowed by `role` (the
        discovered runs OF a given role) and/or `op`/`run_op`. Thin reuse of list_runs (no second
        projection). Returns the same {runs, total_records} shape."""
        res = self.list_runs(op=op, run_op=run_op, since=since, limit=10_000)
        runs = res["runs"]
        if role:
            runs = [r for r in runs if r.get("role") == role]
        return {"runs": runs[:limit], "total_records": len(runs)}

    def route_run_output(self, run_address: str, destination: str, *, turn_id: str | None = None,
                         params: dict | None = None) -> dict:
        """E4 (chain save/re-run + output-DESTINATION) — direct a DISCOVERED run's output to a named
        destination/lane. The chain SAVE + RE-RUN half of E4 is the SAVED-CASCADE (save_cascade/run_cascade,
        GROUP N — a declared re-runnable pipeline); this is the remaining bit: route a DIRECT run's output to
        a named address/lane WITHOUT a saved cascade (the "I ran something, now land/surface/forward it"
        convenience).

        REUSE-don't-parallel (the lane law): the output is READ via `resolve_address` (the canonical
        scheme-dispatching resolver — the SAME path the inject edge + the run-index discovery use), and the
        effect is performed by `rules.route` over the SAME `DESTINATION_KINDS` (`address`/`lane`/`surface`/
        `inject`/`chain`). NO second router, NO destination logic re-implemented here.

        THE FLOOR HOLDS BY CONSTRUCTION (C9.2 / the lane law): `rules.route` can ONLY do the five
        non-consequential `DESTINATION_KINDS` — `FORBIDDEN_DESTINATION_VERBS` (resolve/approve/dispatch) are
        rejected at `Rule` construction AND absent from `DESTINATION_KINDS`, so routing a run output can
        NEVER forge an operator approve or launch a build. `surface` rides `surface_review` → an `ask`
        (resolved=None), never a resolve.

        Args:
          run_address — the run:// (or cas://) address of the output to route (a DISCOVERED address from
                        list_runs/find_runs, or any resolvable address).
          destination — one of `DESTINATION_KINDS` (address|lane|surface|inject|chain). An unknown kind
                        fails loud (the route's own validation), never a silent no-op.
          turn_id     — the turn key the landed address is namespaced under (defaults to a fresh `route-…`
                        so a standalone route still lands at a unique, discoverable address).
          params      — destination params (e.g. {lane: "<name>"} for lane, {title: …} for surface,
                        {chain_role: …} for chain) — passed through to `rules.route` verbatim.

        Returns the `route()` outcome record ({rule, destination, fired, acted, address?/lane?/surfaced?}).
        Fail-loud on an unresolvable address (resolve_address raises) — never route a None/empty output."""
        from runtime import cognition as _cog
        from runtime import rules as _rules
        import time as _time
        if destination not in _rules.DESTINATION_KINDS:
            raise ValueError(
                f"route_run_output: unknown destination {destination!r} — the routable kinds are "
                f"{list(_rules.DESTINATION_KINDS)} (registry-is-truth; never a fabricated destination). "
                f"NONE may be resolve/approve/dispatch (the build-dispatch floor is unforgeable).")
        tid = turn_id or "route-" + _time.strftime("%Y%m%d-%H%M%S-") + str(int(_time.monotonic() * 1000) % 100000)
        # READ the run output via the canonical resolver (run:///cas:// → head→get_content). Fail loud on an
        # unresolvable address (on_missing='raise' — never route an empty/None output as if it were content).
        value = _cog.resolve_address(self.store, run_address, turn_id=tid, on_missing="raise")
        # Build the routing DECISION the way a fired G3 rule would, and let rules.route perform the effect.
        decision = {"fire": True, "destination": destination, "value": value,
                    "rule": f"run-output:{run_address}", "params": params or {},
                    "reason": f"route_run_output({run_address} → {destination})"}
        # the emit adapter mirrors save_cascade's (route emits `emit(kind, {dict})`; _emit is (kind, summary,
        # **meta)) — reuse the SAME shape, no parallel emit.
        return _rules.route(decision, store=self.store, suite=self, turn_id=tid,
                            emit=lambda k, p: self._emit(k, p.get("summary", k),
                                                         **{kk: vv for kk, vv in p.items() if kk != "summary"}))

    # =================================================================================================
    # SAVED CASCADES (Cognition Engine GROUP N · the saving + running FACE over the runner)
    #
    # A saved cascade = a declared, named, RE-RUNNABLE pipeline. REUSE-don't-parallel:
    #   * the DECL is validated + persisted by coherence_actions.build_action / ActionRegistry (EXISTS) —
    #     save_cascade is the ONE validation door, the registry survives reload.
    #   * the EXECUTOR is cognition.run_cascade (the GROUP-N runner) riding run_role/run_items/run_reduce —
    #     NO 2nd engine.
    # registry-is-truth: a step's `model` must be a member of the LIVE model registry (chat ∪ embed) —
    # build_action FAILS LOUD on a hardcoded literal. A step's `role` must be a registered role at RUN time
    # (resolved via role_registry) — fail loud on an unknown role. THE FLOOR: a cascade is run:// COMPUTATION
    # — run_cascade emits only op.run telemetry, NEVER resolve/approve/dispatch, launches NO claude -p.
    # Drift home: the cascade-runner section in runtime/AGENTS.md.
    # =================================================================================================
    # The NAMED deterministic reduce-rules a cascade reduce-step (mode="rule") may select BY NAME (a Python
    # callable can't cross a saved decl). SINGLE SOURCE here; mirrors the MCP run_reduce _REDUCE_RULES seam.
    _CASCADE_REDUCE_RULES = {
        "count":  lambda values: {"count": len(values)},
        "concat": lambda values: {"concat": list(values)},
        "first":  lambda values: {"first": (values[0] if values else None)},
    }

    def _cascade_models(self) -> set:
        """The model REGISTRY build_action validates a cascade's per-step models against — the LIVE chat ∪
        embed models (registry-is-truth; a step naming anything outside this FAILS LOUD as a hardcoding
        violation). chat = available_models(); embed = models_at('embed') (best-effort — a down embed
        endpoint is tolerated so a generate-only cascade still validates; a missing embed model on an embed
        step then fails loud in build_action, never silently)."""
        models = set(self.available_models() or [])
        try:
            models |= set(self.models_at("embed") or [])
        except Exception:
            pass
        return models

    def save_cascade(self, decl: dict) -> dict:
        """SAVE a proven pipeline as a re-runnable cascade (GROUP N · N1). The decl is the ActionRegistry
        shape `{name, steps:[{op, model?, role, kind?, ...}], output_schema?}`. VALIDATED through the ONE
        existing door (coherence_actions.build_action — registry-is-truth on each step's model; fail-loud on
        no-name/no-steps/unknown-op/non-registry-model) then PERSISTED to the cascade_registry (survives
        reload). The execution fields (`role`/`kind`/`reduce_mode`/`fan`/...) ride through verbatim (the
        validator copies steps as-is — they are the runner's axis, the constrained `op` is the OPERATION
        axis). Returns {ok, action} or {ok:False, error} (build_action's shape — fail-loud, never written
        on invalid)."""
        from runtime import coherence_actions as _act
        built = _act.build_action(decl, models=self._cascade_models())
        if not built.get("ok"):
            return built
        self.cascade_registry.save(built["action"])
        self._emit("cascade.save", f"saved cascade {built['action']['name']!r} "
                   f"({len(built['action']['steps'])} steps)", cascade=built["action"]["name"])
        return built

    def list_cascades(self) -> list:
        """The saved cascades (registry-is-truth — the discoverable re-runnable pipelines, AK4). Each is the
        full decl row; an agent reads it to know the steps/ops/models before run_cascade."""
        return self.cascade_registry.all()

    def get_cascade(self, name: str) -> dict | None:
        """One saved cascade decl by name (None if absent — honest, not a fabricated row)."""
        return self.cascade_registry.get(name)

    def run_cascade(self, name: str, inputs=None, *, max_tokens: int = 256) -> dict:
        """RUN a saved cascade END-TO-END (GROUP N · N3 — the largest net-new). Loads the saved decl
        (fail-loud if unknown — never a fabricated cascade), then fires cognition.run_cascade (the runner
        riding run_role/run_items/run_reduce): each step's output threads → the next step's input via the
        run:// resolver, each step is PERSISTED + op.run-INDEXED (so find_runs sees every step), the final
        addressed output is returned. `inputs` is the first step's argument (a run://·cas:// address is
        resolved; a literal used as-is). A missing/unresolvable step input FAILS LOUD (the engine raises).

        DELEGATE: cognition.run_cascade. The role resolver is injected (self.role_registry lookup — the SAME
        registry the swarm uses; fail-loud on an unknown role) so the engine stays Suite-free. THE FLOOR:
        run:// computation only — no resolve/approve/dispatch, no claude -p."""
        action = self.cascade_registry.get(name)
        if action is None:
            raise ValueError(
                f"run_cascade: no saved cascade {name!r} — saved cascades are {[a['name'] for a in self.cascade_registry.all()]} "
                f"(save one via save_cascade first; registry-is-truth, never a fabricated cascade).")
        import time as _time
        from runtime import cognition as _cog
        turn_id = "cascade-" + _time.strftime("%Y%m%d-%H%M%S") + f"-{int(_time.monotonic()*1000) % 100000}"

        def _resolve_role(role_id: str):
            if role_id not in self.role_registry:
                raise ValueError(
                    f"run_cascade: cascade {name!r} references role {role_id!r} which is not registered — "
                    f"registered roles: {sorted(self.role_registry)} (author from the registry, never invent).")
            return self.role_registry[role_id]

        return _cog.run_cascade(action, self.store, turn_id=turn_id, inputs=inputs,
                                resolve_role=_resolve_role,
                                reduce_rules=self._CASCADE_REDUCE_RULES,
                                emit=lambda k, p: self._emit(k, p.get("summary", k),
                                                             **{kk: vv for kk, vv in p.items() if kk != "summary"}),
                                max_tokens=max_tokens)

    def voice_log(self, event: str, **data) -> None:
        """Client-side voice trace (Tim 2026-06-07: "store the process to a proper log so you can
        investigate"). The browser owns half the live voice loop — VAD pause detection, recording
        start/stop, the finished-thought judge calls, chunk playback (iOS), errors — none of which the
        server sees. The FE reports those steps here so the WHOLE process is reconstructable from the ONE
        event log alongside the server-side voice.stream/voice.turn/judge records (NOT a parallel log —
        introspective-data-building, op='voice.client'). Lenient: a trace write must never break a turn.
        `data` carries turn_id (correlate to the server turn), ms, and event-specific fields."""
        ms = data.pop("ms", 0)
        try:
            self.emit_run_record("voice.client", int(ms or 0), event=str(event), **data)
        except Exception:
            pass

    def _emit_durable(self, kind: str, summary: str, **meta) -> dict:
        """Append a DURABLE CLAIM event — FAIL LOUD (T1-EMIT). Unlike _emit (lenient telemetry), this
        does NOT swallow a failure: it returns the written record, and lets any append_event exception
        PROPAGATE. The exactly-once dispatch guarantee rides on the `decision.dispatch` claim being
        actually written — if that write silently failed (the old try/except: pass), _already_dispatched
        would return False on a retry → DOUBLE-LAUNCH of a real `claude -p` build. So the claim write
        must raise on failure (the caller is inside the dispatch lock, BEFORE launch — a raise here means
        nothing launches, exactly the safe outcome). Direct enforcement of rule 4 (fail loud) on the
        safety-critical path. Use ONLY for writes whose loss changes behavior; narration stays on _emit."""
        return self.store.append_event({"kind": kind, "summary": summary, **meta})

    # --- the capability registry: the source of truth the brain authors FROM (never invents) ---
    _models_cache: list | None = None
    _models_cache_at: float = 0.0                             # monotonic stamp of the last live fetch
    _models_cache_degraded: bool = False                      # the cached list is the fallback, not the live list
    MODELS_CACHE_TTL = 60.0                                    # seconds — a model that comes up later becomes
    #                                                            visible without a process restart (was: pinned
    #                                                            process-lifetime → the fleet went stale). A
    #                                                            DEGRADED cache (endpoint was down) is NOT held for
    #                                                            the TTL — it expires immediately so the next call
    #                                                            re-probes and the fleet recovers the moment the
    #                                                            endpoint returns. Manual refresh_models() forces it.

    def available_models(self, force_refresh: bool = False) -> list:
        """The REAL models registered at the fabric endpoint — so the brain picks from what exists
        instead of inventing names. Cached with a short TTL (MODELS_CACHE_TTL) so a model that comes up
        LATER is visible without a restart; a degraded (fallback) cache is never held — it re-probes next
        call so the fleet recovers the instant the endpoint returns. Falls back FAIL-LOUD-LEGIBLE to the
        configured brain if the endpoint is down (a warning event, never silent). force_refresh bypasses
        the cache (the manual-refresh path)."""
        import time as _t
        fresh = (self._models_cache is not None
                 and not self._models_cache_degraded                      # never serve a stale degraded list
                 and (_t.monotonic() - self._models_cache_at) < self.MODELS_CACHE_TTL)
        if fresh and not force_refresh:
            return self._models_cache
        from fabric import transport, config as fcfg
        degraded = False
        try:
            models = transport.list_models(fcfg.DEFAULT_BASE_URL)
        except Exception as e:
            models = None
            self._emit("warning", f"model registry unreachable ({type(e).__name__}) — "
                       f"falling back to [{fcfg.DEFAULT_BRAIN}]; the source-of-truth list is degraded")
        if not models:                                        # surface the degraded fallback, never silent (F6)
            if models is not None:
                self._emit("warning", "model registry returned empty — falling back to the default brain")
            models = [fcfg.DEFAULT_BRAIN]
            degraded = True
        self._models_cache = models
        self._models_cache_at = _t.monotonic()
        self._models_cache_degraded = degraded
        return self._models_cache

    def refresh_models(self) -> list:
        """Manual cache invalidation — re-probe the fabric endpoint NOW (no restart). The fleet stays
        current: a model brought up after process start becomes visible the moment this is called (or
        within MODELS_CACHE_TTL automatically). Returns the fresh list."""
        return self.available_models(force_refresh=True)

    def models_at(self, kind: str = "chat", base_url: str | None = None) -> list:
        """List the REAL models registered at a GIVEN endpoint (B) — so the UI can fill chat-model
        AND embed-model dropdowns from what is ACTUALLY running, not a hand-typed list. BYPASSES the
        chat-only available_models() cache (which only ever hits DEFAULT_BASE_URL → would fill an
        embed dropdown with chat models, the B3 bug). forbid_gemini is preserved (transport.list_models
        filters it). Fail loud: if the embed endpoint isn't configured by the fabric, raise rather than
        silently fall back to the chat endpoint (a silent fallback is the exact rot the laws forbid)."""
        from fabric import transport, config as fcfg
        if base_url is None:
            if kind == "embed":
                base_url = getattr(fcfg, "DEFAULT_EMBED_URL", None)
                if not base_url:
                    raise RuntimeError(
                        "no embedding endpoint configured (fabric.config.DEFAULT_EMBED_URL absent) — "
                        "cannot list embed models without inventing a fallback (fail loud, no silent "
                        "fallback to the chat endpoint). Configure the embed endpoint first.")
            else:
                base_url = fcfg.DEFAULT_BASE_URL
        return transport.list_models(base_url)               # live, uncached; Gemini filtered in transport

    def chat_models_detailed(self) -> list:
        """S1 — the chat models the PICKER should show: the live models at the default (ollama/cloud)
        endpoint PLUS the company-managed vLLM chat services (each on its OWN base_url), so the local
        4b/2b/0.8b are selectable. Each row: {model, base_url, service?, loadable, up}. Picking a
        service-backed model sets model+base_url and can load the service on demand (/api/model/load)."""
        import json as _j, os as _os, socket as _sock
        from fabric import transport, config as fcfg
        out, seen = [], set()
        try:                                                  # 1. the default endpoint's live models
            for m in transport.list_models(fcfg.DEFAULT_BASE_URL):
                out.append({"model": m, "base_url": fcfg.DEFAULT_BASE_URL, "service": None, "loadable": False, "up": True})
                seen.add((m, fcfg.DEFAULT_BASE_URL))
        except Exception:
            pass
        try:                                                  # 2. the company vLLM chat services (own base_urls)
            repo = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
            svcs = _j.load(open(_os.path.join(repo, "ops", "services.json")))["services"]
            for sid, spec in svcs.items():
                c = spec.get("config") or {}
                model, port = c.get("model"), spec.get("port")
                if not (model and port) or "chat" not in sid or spec.get("group") not in ("brain", "models"):
                    continue
                base = f"http://localhost:{port}/v1"
                if (model, base) in seen:
                    continue
                up = False
                try:
                    s = _sock.socket(); s.settimeout(0.3); up = s.connect_ex(("127.0.0.1", int(port))) == 0; s.close()
                except Exception:
                    pass
                out.append({"model": model, "base_url": base, "service": sid, "loadable": True, "up": up})
        except Exception:
            pass
        return out

    def capabilities(self) -> dict:
        """One snapshot of WHAT EXISTS — fed into every authoring prompt + every registered select,
        so the correct values are the easy path and nothing is guessed. The reflective fold."""
        return {
            "node_types": sorted(self.registry.types),
            "models": self.available_models(),
            "modes": list(self.MODES),
            # T3-MODE (COMPLETE): expose the mode DIRECTIVES (the prose behind each mode) from the one
            # source (MODE_DIRECTIVES) so the surface reads them instead of hand-copying. Backend half
            # (this line) + FE half (App.tsx deletes its MODE_DESC copy and reads capabilities().
            # mode_directives) are now BOTH merged — registry-is-truth, PoLR honoured. Additive map
            # {mode: directive}; an older FE that ignores it is unaffected.
            "mode_directives": dict(self.MODE_DIRECTIVES),
            # E1 — THE MODE TYPE-REGISTRY (registry-is-truth): the full HIERARCHICAL spec the surface reads
            # so the modes-and-context-resolution-are-ONE-system is visible end-to-end. Each entry carries
            # ALL declared mode axes from the ONE source — the resolution/context half (label/directive/
            # resolution/subtypes/consent), the thought-shape/staging half (grain/shape/stage), AND the
            # activation/budget half (live/reserve_r/per_role_ctx/main_ctx_tokens/brain_config). Editing a
            # mode in this registry changes ALL of them — one edit, one place.
            #
            # SEAM 1 (A · mode reach-extension, 2026-06-09): this block used to be hand-built from
            # MODE_SPECS and served only ~5 axes (label/directive/resolution/subtypes/consent), DROPPING the
            # cognition half (grain/shape/stage/live/reserve_r/per_role_ctx/main_ctx_tokens/brain_config) —
            # so the FE could not see or tune the cognition half of each mode (lost-opportunity #2). It now
            # serves the WHOLE declaration via the unified `mode_registry()` accessor (lost-opportunity #1 —
            # that accessor had ZERO callers). Registry-is-truth: serve what `mode_registry()` returns, never
            # a hand-picked subset — a 14th axis added to MODE_REGISTRY rides to the FE for free, no edit here.
            #
            # `capabilities()` is `json.dumps`'d raw by the bridge (bridge.py:529 — no `default=` set-handler),
            # so the served value MUST be JSON-safe. `mode_registry()` returns frozensets nested in
            # `resolution.strata` and `subtypes.*.strata` (focus/background/watch-and-react/off declare them) —
            # `_mode_axes_jsonsafe` recursively coerces every set/frozenset → a sorted list (the SAME
            # frozenset→sorted-list conversion the old hand-built block did for `strata`, now applied
            # whole-tree so no axis can leak a non-serializable value). None stays None (admit-all). This
            # preserves the exact serialized SHAPE of the 5 keys the FE already reads + adds the 8 missing.
            "mode_registry": {
                # FE/settings contract: `subtypes` is ALWAYS a JSON-safe dict (the old MODE_SPECS serve gave
                # {} for a no-subtypes mode; mode_registry() keeps None for byte-for-byte MODE_SPECS parity, so
                # coerce None→{} HERE at the serve only — never in mode_registry()). settings_surface A5.
                m: {**(_r := self._mode_axes_jsonsafe(self.mode_registry(m))),
                    "subtypes": _r.get("subtypes") or {}}
                for m in self.MODES
            },
            "rhm_verbs": list(self.RHM_VERBS),
            # The STATE-TYPE REGISTRY exposed (registry-is-truth): WHAT node-states exist + their meaning
            # + which resolve-mode each applies to, so the surface renders the status vocabulary from
            # here instead of hardcoding idle/ran/cached/stuck/live/empty. Additive key; an older FE that
            # ignores it is unaffected (the four executing statuses derive exactly as before).
            "node_states": [dict(s, applies_to=list(s["applies_to"])) for s in self.NODE_STATES],
            "panels": [p.get("id") for p in self.list_panels()],
            # the STT (ear) registry — WHAT speech-to-text providers exist + are usable (the slot mirrors
            # the brain model). From voice/stt.py's source of truth (guarded — {} if voice is absent), so
            # the surface fills the ear dropdown from what's real, never a hand-typed list. The stt lane
            # may not have shipped its richer available_stt() yet → degrades to available() (rule 4: no
            # crash, no fabrication). Schema-additive key; an older surface ignoring it is unaffected.
            "stt": self.available_stt(),
            "panel_field_targets": list(self.PANEL_TARGETS),
            # G2 (C2.1/C2.3) — the file-discovered COGNITION role registry as a status read: WHAT roles
            # exist + each role's facet (fireable/jury/mode_scope/requires) + the cast per mode + the
            # juries. Registry-is-truth: the surface/RHM read the cast from here, never a hardcoded list.
            # Additive key; an older reader that ignores it is unaffected (rule 2). The roles' drift home
            # is roles/AGENTS.md (asserted by tests/roles_acceptance.py), NOT the MAP REGISTRY block.
            "cognition": self.cognition_capabilities(),
            # X17 (Convergence, D2) — THE COMPOSITION IS CONFIGURABLE. The R2 ranking knobs (the recency
            # λ · proximity · pin · semantic WEIGHTS, the window BUDGET cap, the run-versions bound) read
            # from the env (resolved in __init__; defaults = the class constants), so retuning the context
            # composition needs NO code change. Exposed here (registry-is-truth) as the LIVE instance
            # values so the surface/fleet can READ them — and later a config panel can SET them via the
            # env. Additive key; an older reader that ignores it is unaffected (rule 2).
            "composition_config": {
                "R2_LAMBDA": self.R2_LAMBDA,
                "R2_PROXIMITY_WEIGHT": self.R2_PROXIMITY_WEIGHT,
                "R2_PIN_WEIGHT": self.R2_PIN_WEIGHT,
                "R2_SEMANTIC_WEIGHT": self.R2_SEMANTIC_WEIGHT,
                "R2_BUDGET": self.R2_BUDGET,
                "R2_RUN_VERSIONS": self.R2_RUN_VERSIONS,
                "R2_HOWTO_MAX": self.R2_HOWTO_MAX,
                "R2_HOWTO_TERSE": self.R2_HOWTO_TERSE,   # E1 — the terse-lens per-howto cap
                # E2 — the mode AUTO-DETECT toggle (off/suggest/auto), a CONFIG item not hardcoded. The
                # live resolved value + the valid options, so the surface renders + (later) sets it.
                "MODE_AUTODETECT": self.MODE_AUTODETECT,
                "MODE_AUTODETECT_OPTIONS": list(self.MODE_AUTODETECT_OPTIONS),
            },
            "api_verbs": ["/api/run", "/api/now", "/api/chat", "/api/graph", "/api/graphs",
                          "/api/types", "/api/object_info", "/api/cognition_info", "/api/events", "/api/inbox",
                          "/api/panels", "/api/models", "/api/stream", "/api/move",
                          "/api/ui_info", "/api/surface-review", "/api/capture-idea",
                          "/api/build-intent",
                          "/api/review/start", "/api/review/current", "/api/review/next",
                          "/api/review/status"],
        }

    def _authoring_preamble(self) -> str:
        """Put the registry on the brain's easy path so the correct values are effortless and nothing
        is invented — and make ASKING the easy path when something needed isn't registered."""
        cap = self.capabilities()
        return ("REGISTERED VALUES — author using ONLY these; do NOT invent anything not listed:\n"
                f"- models: {cap['models']}\n- modes: {cap['modes']}\n- node-types: {cap['node_types']}\n"
                f"- api verbs (for fetch): {cap['api_verbs']}\n"
                "If doing this correctly REQUIRES a value or capability NOT in these lists, do NOT make one "
                "up — output EXACTLY one line and nothing else: NEEDS: <what you need, and why>.")

    @staticmethod
    def _slug(name: str) -> str:
        """Normalize the brain's natural name ('Model Selector' → 'model_selector') so the correct
        path is easy. But a PATH-like name (/, .., \\) is a traversal attempt, not a name — reject it
        rather than silently sanitizing an attack into a node. (_safe_node_name guards again after.)"""
        import re
        if name and ("/" in name or "\\" in name or ".." in name):
            raise ValueError(f"unsafe name {name!r} — looks like a path, not a name")
        s = re.sub(r"[^a-z0-9]+", "_", (name or "").lower()).strip("_")
        if not s or s[0].isdigit():
            s = "x_" + s
        return s

    @staticmethod
    def _needs(text: str):
        t = (text or "").strip()
        return t[len("NEEDS:"):].strip() if t.upper().startswith("NEEDS:") else None

    def _ask_operator(self, question: str, context: str = "") -> str:
        """The brain hit unregistered ground → ASK the operator (surfaced question) instead of
        fabricating. Confabulation is as bad as failing (Tim) — this makes asking the easy path."""
        sid = self.inbox.surface("question", {"question": question, "context": context}, default="reject")
        self._emit("ask", f"the system needs input: {question[:60]}", surfaced=sid,
                   address="ui://chrome/inbox")   # S2: the question lands in the inbox for the operator
        return sid

    def _acceptance_suites(self) -> list:
        import glob
        return sorted(os.path.basename(p)[:-3]
                      for p in glob.glob(os.path.join(self._repo_root, "tests", "*.py")))

    def _write_doc_block(self, filename: str, marker: str, body: str) -> None:
        """Replace the <!--MARKER:START-->…<!--MARKER:END--> block of a self-description file
        with freshly-generated content. The factual parts of the docs thus maintain themselves."""
        import re
        path = os.path.join(self._repo_root, filename)
        if not os.path.exists(path):
            return
        full = f"<!--{marker}:START-->{body}<!--{marker}:END-->"
        text = open(path, encoding="utf-8").read()
        new = re.sub(rf"<!--{marker}:START-->.*?<!--{marker}:END-->", lambda _m: full, text, flags=re.S)
        if new != text:
            open(path, "w", encoding="utf-8").write(new)

    def refresh_self_description(self) -> None:
        """The reflective fold: regenerate the auto-maintained factual blocks of the orientation files
        — MAP.md (the live registry) + STATE.md (the acceptance-suite index) — from the system itself,
        so the self-description stays current as the app grows (Tim's 'maintains'). Called on every
        apply/revert. The PROSE is integration-maintained; doc_drift fails loud if anything falls behind."""
        cap = self.capabilities()
        self._write_doc_block("MAP.md", "REGISTRY",
            " (auto-maintained by Suite.refresh_self_description on every apply — do not hand-edit)\n"
            f"- **node-types** ({len(cap['node_types'])}): {', '.join(cap['node_types'])}\n"
            f"- **RHM verbs**: {', '.join(cap['rhm_verbs'])}\n"
            f"- **modes**: {', '.join(cap['modes'])}\n"
            f"- **panels**: {', '.join(cap['panels']) or '(none)'}\n"
            f"- **models** (from the fabric registry): {', '.join(cap['models'])}\n")
        suites = self._acceptance_suites()
        self._write_doc_block("STATE.md", "SUITES",
            " (auto-maintained by Suite.refresh_self_description — do not hand-edit)\n"
            f"- {len(suites)} acceptance suites: {', '.join(suites)}\n")

    # back-compat alias (older callers / external agents may know this name)
    refresh_map = refresh_self_description

    def _doc_block(self, filename: str, marker: str) -> str:
        """The text INSIDE a file's <!--MARKER--> block (lowercased) — so drift is checked against the
        maintained registry block, NOT the whole prose file (red-team F3: prose substrings → false negatives)."""
        import re
        path = os.path.join(self._repo_root, filename)
        if not os.path.exists(path):
            return ""
        m = re.search(rf"<!--{marker}:START-->(.*?)<!--{marker}:END-->",
                      open(path, encoding="utf-8").read(), re.S)
        return (m.group(1) if m else "").lower()

    def doc_drift(self) -> dict:
        """What the system has that the SELF-DESCRIPTION files don't yet reflect — so they can't
        silently rot (Tim: 'updates to the system → updates to whatever relevant files like this').
        Checked INSIDE the maintained blocks (not whole-file substrings), covering every capability
        category (node-types, verbs, modes, panels) + the suite index. A failing check is the enforcement."""
        reg = self._doc_block("MAP.md", "REGISTRY")
        suites_block = self._doc_block("STATE.md", "SUITES")
        cap = self.capabilities()
        return {
            "map_node_types": [t for t in cap["node_types"] if t.lower() not in reg],
            "map_rhm_verbs": [v for v in cap["rhm_verbs"] if v.lower() not in reg],
            "map_modes": [m for m in cap["modes"] if m.lower() not in reg],
            "map_panels": [p for p in cap["panels"] if p.lower() not in reg],
            "state_missing_suites": [s for s in self._acceptance_suites() if s.lower() not in suites_block],
        }

    map_drift = doc_drift  # back-compat alias

    # --- introspection (reads) ---
    def list_types(self) -> list[str]:
        return sorted(self.registry.types)

    def object_info(self) -> dict:
        return self.registry.object_info()

    def list_by_type(self, output_type: str) -> list[str]:
        return self.registry.produces(output_type)

    def list_graphs(self) -> list[str]:
        return self.store.list_graphs()

    # --- graph building (generic over node-type) ---
    def _load(self, graph_id: str) -> Graph:
        return self.store.load_graph(graph_id) or Graph(id=graph_id)

    def _last_run_stuck(self, graph_id: str) -> list:
        """T3-STATUS — the `stuck` node-ids from the MOST RECENT `run` event for `graph_id` (the run
        emit records `stuck=[...]` with `graph=<id>`). Backend-authoritative source for the persisted
        (no-fresh-result) status path, so `stuck` survives a reload without a client-side overlay. Reads
        events newest-first; the first matching run event wins. Empty when the graph never ran / no
        stuck nodes. Tolerant: a malformed/absent field reads as no-stuck (never raises in a status read)."""
        for ev in self.store.recent_events(200):
            if ev.get("kind") == "run" and ev.get("graph") == graph_id:
                st = ev.get("stuck")
                return list(st) if isinstance(st, list) else []
        return []

    def _last_run_failed(self, graph_id: str) -> dict:
        """The `failed` {nid: "ErrType: msg"} map from the MOST RECENT `run` event for `graph_id` (the
        run emit records `failed=dict(failed)` with `graph=<id>`). Mirror of `_last_run_stuck` so a
        FAILED node survives a reload (status=`failed`, not re-defaulting to idle) — closing the same
        silent-regression shape on the no-fresh-result path (rule 4). Newest run wins; tolerant (a
        malformed/absent field reads as no-failures; never raises in a status read). A node that since
        resolved (its output address now holds content) is no longer reported failed (checked at the
        call site, after cas)."""
        for ev in self.store.recent_events(200):
            if ev.get("kind") == "run" and ev.get("graph") == graph_id:
                fl = ev.get("failed")
                return dict(fl) if isinstance(fl, dict) else {}
        return {}

    @staticmethod
    def _schema_defaults(schema: dict) -> dict:
        """Flatten a node-type's nested config_schema {key:{...,default}} → {key:default} (A).
        Guarded so it survives a still-flat CONFIG ({key:value}, mid-migration) and skips entries
        with no/None default — so a freshly-added node is seeded with its type's defaults (not blank
        and inert) WITHOUT clobbering a run()-fallback (None default) or fabricating keys."""
        out = {}
        for k, v in (schema or {}).items():
            if isinstance(v, dict) and "default" in v and v["default"] is not None:
                out[k] = v["default"]
        return out

    def create_node(self, graph_id: str, type: str, config: dict | None = None,
                    node_id: str | None = None, position: dict | None = None) -> str:
        if type not in self.registry:
            raise KeyError(f"unknown node-type {type!r} (have: {self.list_types()})")
        def _do():                                                       # G1: AUTO → guard runs it straight through
            # T1-RACE: hold the per-graph lock around the WHOLE load→mutate→save so a concurrent
            # mutation on the same graph (another create/move/connect on the threading server, or the
            # MCP face racing a UI move) can't load the same version and last-writer-wins (lost update).
            with self.store.graph_lock(graph_id):
                g = self._load(graph_id)
                nid = node_id or f"{type}-{len(g.nodes) + 1}"
                nt = self.registry.types.get(type)
                seeded = self._schema_defaults(nt.config_schema if nt else {})   # type defaults first…
                seeded.update(config or {})                                      # …caller config WINS (merge)
                pos = XY(**position) if position else XY()                       # optional initial placement (C5)
                g.nodes.append(NodeInstance(id=nid, type=type, config=seeded, position=pos))
                self.store.save_graph(g)
                self._emit("create", f"+ {type} node ({nid})", graph=graph_id, node=nid, type=type,
                           address=f"run://{graph_id}/{nid}")   # S2: addressed at the node acted on
                return nid
        return guard("compose", do=_do)                                  # AUTO → identical behavior; POLICY is the router

    def connect(self, graph_id: str, from_node: str, from_port: str,
                to_node: str, to_port: str) -> None:
        # T1-RACE: per-graph lock around the whole load→mutate→save (lost-update across both faces).
        with self.store.graph_lock(graph_id):
            g = self._load(graph_id)
            byid = {n.id: n for n in g.nodes}
            if from_node not in byid or to_node not in byid:
                raise KeyError(f"connect: unknown node ({from_node!r} -> {to_node!r})")
            ft = self.registry.types.get(byid[from_node].type)
            tt = self.registry.types.get(byid[to_node].type)
            out_t = ft.ports.outputs.get(from_port) if ft else None
            in_t = tt.ports.inputs.get(to_port) if tt else None
            if out_t and in_t and "Any" not in (out_t, in_t) and out_t != in_t:   # type-check, fail loud
                raise ValueError(
                    f"type mismatch: {from_node}.{from_port}:{out_t} → {to_node}.{to_port}:{in_t}")
            g.edges.append(Edge(from_node=from_node, from_port=from_port,
                                to_node=to_node, to_port=to_port))
            self.store.save_graph(g)
            self._emit("connect", f"wired {from_node}.{from_port} → {to_node}.{to_port}",
                       graph=graph_id, from_node=from_node, to_node=to_node,
                       address=f"run://{graph_id}/{to_node}")   # S2: addressed at the wired-into (downstream) node

    def delete_node(self, graph_id: str, node_id: str) -> None:
        # T1-RACE: per-graph lock around the whole load→mutate→save (lost-update across both faces).
        with self.store.graph_lock(graph_id):
            g = self._load(graph_id)
            g.nodes = [n for n in g.nodes if n.id != node_id]
            g.edges = [e for e in g.edges if e.from_node != node_id and e.to_node != node_id]
            self.store.save_graph(g)
            self._emit("delete", f"removed node {node_id}", graph=graph_id, node=node_id,
                       address=f"run://{graph_id}/{node_id}")   # S2: addressed at the deleted node

    def set_config(self, graph_id: str, node_id: str, config: dict) -> None:
        def _do():                                                       # G1: AUTO → guard runs it straight through
            # T1-RACE: per-graph lock around the whole load→mutate→save (lost-update across both faces).
            with self.store.graph_lock(graph_id):
                g = self._load(graph_id)
                for n in g.nodes:
                    if n.id == node_id:
                        n.config.update(config)
                        self.store.save_graph(g)
                        return
                raise KeyError(f"no node {node_id!r} in graph {graph_id!r}")
        return guard("configure", do=_do)                               # AUTO → identical; POLICY is the router

    def set_position(self, graph_id: str, node_id: str, x: float, y: float,
                     w: float | None = None, h: float | None = None) -> None:
        """Write a node's SIBLING position (and optional size) — NOT its config (C5). The canvas
        reflects, never owns: a drag-end round-trips here so the backend stays the source of truth
        for layout. A clone of set_config but targeting position/size, the NodeInstance fields that
        already round-trip to disk. Raises KeyError if the node is absent (fail loud)."""
        # T1-RACE: per-graph lock around the whole load→mutate→save. /api/move is the highest-frequency
        # mutation path; without the lock two concurrent moves on DISTINCT nodes both load version V →
        # last-writer-wins → the other node's move silently lost (the exact bug T1-RACE names).
        with self.store.graph_lock(graph_id):
            g = self._load(graph_id)
            for n in g.nodes:
                if n.id == node_id:
                    n.position = XY(x=x, y=y)
                    if w is not None and h is not None:
                        n.size = WH(w=w, h=h)
                    self.store.save_graph(g)
                    self._emit("move", f"moved {node_id} → ({x:.0f},{y:.0f})",
                               graph=graph_id, node=node_id,
                               address=f"run://{graph_id}/{node_id}")   # S2: addressed at the moved node
                    return
            raise KeyError(f"no node {node_id!r} in graph {graph_id!r}")

    def save_graph(self, graph: Graph) -> None:
        self.store.save_graph(graph)

    # --- run + read ---
    def run(self, graph_id: str, branch: str = "main", pause=None, force=None) -> dict:
        def _do():                                                       # G1: AUTO → guard runs it straight through
            r = scheduler.run(self._load(graph_id), self.store, self.registry,
                              branch=branch, pause=pause, force=force)
            failed = r.get("failed") or {}
            self._emit("run", f"ran {len(r['ran'])}, cached {len(r['skipped'])}"
                       + (f", stuck {len(r['stuck'])}" if r.get("stuck") else "")
                       + (f", failed {len(failed)}" if failed else ""),
                       graph=graph_id, ran=sorted(r["ran"]), cached=sorted(r["skipped"]),
                       stuck=sorted(r.get("stuck", [])), failed=dict(failed),
                       address=f"run://{graph_id}")   # S2: graph-level run (ran N / cached M / …)
            # FAIL LOUD at the surface (engine handoff, rule 4): the run COMPLETES (containment, no raise),
            # but a failed node must be SEEN — a node-error is not a silent no-op. A distinct `warning`
            # event (not just the count folded into the run line) so now()'s last_event surfaces it and the
            # operator/now-view can't miss it. Names the nodes + their errors.
            if failed:
                detail = "; ".join(f"{nid}: {err}" for nid, err in sorted(failed.items()))
                self._emit("warning", f"{len(failed)} node(s) FAILED this run — {detail}",
                           graph=graph_id, failed=dict(failed),
                           address=f"run://{graph_id}")   # S2: this warning is locus-bound to the run graph
                                                          # (distinct from the locus-LESS system-health warnings)
            return r
        return guard("run", do=_do)                                     # AUTO → identical; POLICY is the router

    def state(self, graph_id: str, result: dict | None = None, branch: str = "main") -> dict:
        g = self._load(graph_id)
        nodes = []
        for n in g.nodes:
            logical = f"run://{g.id}/{n.id}" if branch == "main" else f"run://{g.id}/{n.id}@{branch}"
            mod = self.registry.get(n.type)
            node_error = None                                  # the run error for a `failed` node (else None)
            if getattr(mod, "RESOLVE", "compute") == "reference":
                # REFERENCE-RESOLVED (portals): a live window onto another address, never computed and
                # never fired (the scheduler SKIPS it). Resolve config.ref NOW (window, not a copy) and
                # derive its state from the STATE-TYPE REGISTRY's reference-scoped vocabulary
                # (NODE_STATES, applies_to='reference') — `live` if the ref resolves to content, `empty`
                # otherwise. This is hoisted ABOVE the result/reload split on purpose: a portal never
                # legitimately gets a run-status (it has no run), so routing it through ONE branch makes
                # the fresh-result path and the reload path AGREE by construction — which is exactly why
                # the old idle↔cached flip-on-reload (idle on the result path, cached on reload) is gone.
                # Executing nodes (RESOLVE='compute') are UNAFFECTED — they fall through to the original
                # four-status derivation below, byte-for-byte (Step A, no behaviour change).
                ref = n.config.get("ref") or ""
                cas = self.store.head(ref) if ref else None
                status = "live" if cas else "empty"
            else:
                cas = self.store.head(logical)
                if result:
                    # T3-STATUS: `stuck` is a REAL backend node status (one source of truth), not a
                    # client-only overlay. The scheduler already reports which nodes could not fire because
                    # an input never resolved (scheduler result['stuck']); surface it here so the FE reads
                    # it from the backend instead of maintaining a parallel client-side `stuck` re-applied
                    # from events after every reload. Checked BEFORE ran/cached/idle so a stuck node is
                    # never mislabeled idle. (be-half → at most needs-tim until the FE drops its overlay.)
                    # FAILED (engine handoff): the scheduler now CONTAINS a node that RAISED into a
                    # result['failed'] {nid: "ErrType: msg"} map. Without consuming it, a failed node fell
                    # through to `idle` — a SILENT regression (the operator saw "nothing happened" for a
                    # node that actually errored, violating rule 4). Branch on `failed` BEFORE the idle
                    # fallthrough (the sets are disjoint) and carry the error message onto the node dict.
                    failed_map = result.get("failed") or {}
                    if n.id in failed_map:
                        status = "failed"
                        node_error = failed_map[n.id]
                    else:
                        status = ("stuck" if n.id in result.get("stuck", [])
                                  else "ran" if n.id in result["ran"]
                                  else "cached" if n.id in result["skipped"] else "idle")
                else:
                    # D5-be (persisted run-status, in-territory): with no fresh run result, DERIVE status
                    # from the store — a node whose output address resolves has a cached result, so report
                    # 'cached' instead of resetting to 'idle' on reload. Fail-loud-legible: the surface
                    # never claims "nothing happened" for a node that actually holds a result. T3-STATUS:
                    # `stuck` is run-relative (an input that never resolved on the LAST run), so without a
                    # fresh result we derive from the most recent run event for THIS graph that listed the
                    # node as stuck — keeping `stuck` backend-authoritative across a reload (what the FE used
                    # to re-derive client-side). A node that since resolved (cas present) is never stuck.
                    if cas:
                        status = "cached"
                    elif n.id in self._last_run_failed(g.id):
                        # FAILED survives a reload too (rule 4): the most recent run recorded this node as
                        # failed and it still holds no result, so it is NOT idle. Mirror of the stuck path;
                        # checked before stuck/idle. Carry the persisted error message.
                        status = "failed"
                        node_error = self._last_run_failed(g.id).get(n.id)
                    elif n.id in self._last_run_stuck(g.id):
                        status = "stuck"
                    else:
                        status = "idle"
            nt = self.registry.types.get(n.type)
            node = {
                "id": n.id, "type": n.type, "config": n.config,
                "kind": nt.kind if nt else ("content" if n.type in CONTENT_KINDS else "process"),
                "layer": getattr(mod, "ORIGIN", "authored"),   # provenance layer (authored vs system)
                "status": status, "address": logical, "content_hash": cas,
                "output": self.store.get_content(cas) if cas else None,
                "position": n.position.model_dump(),           # C5: layout is backend-authoritative
                "size": n.size.model_dump(),
            }
            if node_error is not None:                         # carry the run error for a `failed` node (fail-loud)
                node["error"] = node_error
            nodes.append(node)
        return {"id": g.id, "nodes": nodes,
                # C2/C3: carry per-port identity so the UI draws per-port wires + feeds multi-input
                # nodes correctly. {from,to} kept for back-compat; from_port/to_port are additive.
                "edges": [{"from": e.from_node, "to": e.to_node,
                           "from_port": e.from_port, "to_port": e.to_port} for e in g.edges]}

    def results(self, graph_id: str) -> dict:
        st = self.state(graph_id)
        return {n["id"]: n["output"] for n in st["nodes"]}

    # --- the operator surfaces (I2): now-view · presence · event log ---
    def events(self, limit: int = 60) -> list:
        return self.store.recent_events(limit)

    def events_since(self, seq: int) -> list:
        """Events with seq > given, oldest-first — the SSE cursor read (G). Thin pass-through to the
        store's file-tail (mirrors events()); captures BOTH faces since it tails the shared log."""
        return self.store.events_since(seq)

    def now(self, graph_id: str) -> dict:
        """The now-view + presence snapshot — derived live from state, the inbox, and the log."""
        st = self.state(graph_id)
        nodes = st["nodes"]
        resolved = [n for n in nodes if n["content_hash"]]
        pending = [d for d in self.inbox.list() if d.get("resolved") is None]
        recent = self.store.recent_events(1)
        if pending:
            presence = "awaiting your approval"
        elif nodes and len(resolved) == len(nodes):
            presence = "ready · all resolved"
        elif nodes:
            presence = "ready · work unresolved"
        else:
            presence = "empty"
        mode = self.get_mode()
        return {
            "graph": st["id"],
            "nodes_total": len(nodes),
            "nodes_resolved": len(resolved),
            "surfaced_pending": len(pending),
            "presence": "off" if mode == "off" else presence,
            "mode": mode,
            "last_event": recent[0] if recent else None,
        }

    # --- modes / the presence dial: the mode IS a node (context-05, D1-D3) ---
    # E1 — THE MODE TYPE-REGISTRY (the modes-and-context-resolution-are-ONE-system criterion, direction
    # §6/§6.5). Each entry is a `ModeSpec` carrying its directive (behaviour) AND its `resolution`
    # declaration (how context resolves under it) AND its sub-types (the hierarchy). `MODES` (the 8-tuple,
    # ORDER-CONTRACTED — modes_acceptance asserts len==8) and `MODE_DIRECTIVES` (the prose map) are now
    # DERIVED from this ONE source (no parallel literal to drift — the same move RHM_VERB_SPECS made).
    # The 8 top-level modes are UNCHANGED in NAME and ORDER (listening … off) — schema-additive: the new
    # `resolution`/`subtypes`/`consent` data is added, no mode renamed/removed/reordered.
    #
    # The `resolution` blocks are the LOAD-BEARING half. They are consumed AS DATA by `resolution_spec_for`
    # → `_resolve_context_at` (there is NO `if mode ==` anywhere in the resolution path — registry-is-truth).
    # The seed `listening` resolution = today's full gather (strata=None admit-all, howto full, no budget
    # override) so the DEFAULT path is byte-for-byte unchanged (every existing R2 suite stays green). The
    # OTHER modes declare GENUINE differences over the SAME store/locus: focus resolves a tight, terse,
    # howto-suppressed window (deep work — minimal context); background/watch drop the chatty strata; off
    # resolves nothing (the RHM is asleep). Editing any one of these entries changes BOTH the mode's
    # behaviour AND how context resolves under it — one edit, one place (§6.5, proven by use).
    # ============================================================================================
    # MODE_REGISTRY — THE MODE DIAL, ONE SOURCE (the mode-dial join, 2026-06-08). Two AI sessions built
    # the dial in two halves; this is the unified declaration. ONE entry per mode carries ALL of its axes:
    #   • the RESOLUTION/CONTEXT half (was MODE_SPECS/ModeSpec — the interface session's):
    #       label · directive · resolution · subtypes · consent
    #   • the THOUGHT-SHAPE/STAGING half (was PART_GRAIN — cognition's): grain · shape · stage
    #   • the ACTIVATION/BUDGET half (was ACTIVATION_ALLOCATION — cognition's):
    #       live · reserve_r · per_role_ctx · main_ctx_tokens · brain_config
    # The 3 OLD NAMES (MODE_SPECS, PART_GRAIN, ACTIVATION_ALLOCATION) are now DERIVED VIEWS of this one
    # source (immediately below + at their original sites) — NO parallel tables (the law). Every consumer
    # + the `ModeSpec` interface + the `mode_registry()` accessor read the SAME values, value-for-value.
    # The 8 top-level modes are UNCHANGED in NAME and ORDER (listening … off) — modes_acceptance asserts
    # len==8 + this exact order; MODES = tuple(MODE_REGISTRY) so insertion order here IS the contract.
    #
    # PER-AXIS NOTES (moved here from the 3 old tables):
    #   resolution — the CONTEXT-RESOLUTION DECLARATION the resolver consumes AS DATA (never a mode-name
    #     branch — registry-is-truth). Keys (all optional; absent → today's default): strata (frozenset of
    #     admitted gather-stratum kinds, None → admit all) · howto_detail ('full'|'terse'|'none') · budget
    #     (int char-cap override, None → instance R2_BUDGET). The seed `listening` resolution = today's
    #     full gather → the DEFAULT path is byte-for-byte unchanged (every R2 suite stays green).
    #   subtypes — the HIERARCHY (§6.5: each mode-type may have sub-types that OVERRIDE a resolution key
    #     for an INSTANCE). A mode WITHOUT sub-types omits the key (→ ModeSpec.subtypes default None today).
    #   consent — the consent-interaction style this mode favours (§6B descriptive declaration).
    #   grain — the unit a reply part spans (line/beat/paragraph); the staged reply is chunked at this grain.
    #   shape — names the THOUGHT_SHAPE archetype (THOUGHT_SHAPES below, the shape-definition catalog —
    #     keyed by archetype, NOT per-mode; modes reference a shape by id, it stays as-is).
    #   stage — whether this mode STAGES a multi-part reply at all (focus/background/off NEVER stage, C4.3).
    #   live — which ACTIVATION CONTEXTS are live (C5.5); `per-turn` is always the spine.
    #   reserve_r — the per-turn live-stream reservation (sacred FLOOR, C5.5 — activation.py fails loud
    #     below FLOOR_RESERVE_R). per_role_ctx — per-role context tokens (the SlotBudget is COMPUTED from
    #     these against the live registry, never a literal). main_ctx_tokens — assumed main-conversation
    #     depth (the C0.5 deep-main KV bind). brain_config — the declared brain loadout (mode→loadout
    #     registry, H8; a swarm-heavy mode wants the higher-util swarm-brain ~16K/0.63, a voice-depth mode
    #     the 64K brain — DECLARED here, NOT swapped by this build).
    # ============================================================================================
    MODE_REGISTRY = {
        "listening": {
            "label": "Listening",
            "directive": "Conversational and present; respond fully.",
            # SEED = today's full gather: admit every stratum, full howto, no budget override.
            "resolution": {"strata": None, "howto_detail": "full", "budget": None},
            "subtypes": {
                "general": {},   # the default sub-type (no override) — identical to the mode-type lens
                # an instance can ask for a deeper, semantically-weighted read (e.g. when co-present at a
                # node): a sub-type is an INSTANCE PARAMETER that refines the SAME mode-type lens (§6.2).
                "deep": {"budget": 8000},
            },
            "consent": "offer",
            # thought-shape/staging half (was PART_GRAIN):
            "grain": "beat", "shape": "linear-stream", "stage": True,
            # activation/budget half (was ACTIVATION_ALLOCATION) — voice-depth conversational: 64K brain,
            # shallow background activity, R reserved.
            "live": ["per-turn", "background", "sense", "rollup"], "reserve_r": 2,
            "per_role_ctx": 1500, "main_ctx_tokens": 0, "brain_config": "voice-64k",
        },
        "text-only": {
            "label": "Text-only",
            "directive": "Respond in text, concisely, only to what is addressed.",
            "resolution": {"strata": None, "howto_detail": "full", "budget": None},
            "consent": "offer",
            "grain": "paragraph", "shape": "linear-stream", "stage": True,
            "live": ["per-turn", "rollup"], "reserve_r": 2,
            "per_role_ctx": 1500, "main_ctx_tokens": 0, "brain_config": "voice-64k",
        },
        "background": {
            "label": "Background",
            "directive": "Be minimal — surface only what genuinely needs the operator; otherwise a one-line acknowledgement.",
            # background = low-noise: drop the chatty annotation/chat strata, keep the stable howto +
            # presentation_pref (F1 — a learned pref is address-truth, a sibling of howto) + events.
            "resolution": {"strata": frozenset({"howto", "presentation_pref", "event", "run"}),
                           "howto_detail": "terse", "budget": 1500},
            "consent": "act",
            "grain": "line", "shape": "scatter-write", "stage": False,   # NEVER stage (C4.3) — minimal surface
            # BACKGROUND presence mode = the swarm-heavy loadout: the higher-util swarm-brain, a deeper
            # assumed main (the deep-main KV bind is why this mode wants the 0.63 brain).
            "live": ["per-turn", "background", "sense", "rollup"], "reserve_r": 2,
            "per_role_ctx": 1500, "main_ctx_tokens": 40000, "brain_config": "swarm-16k",
        },
        "focus": {
            "label": "Focus",
            "directive": "The operator is in deep work. Be extremely brief (one or two lines); do not elaborate unless asked.",
            # focus = TIGHT ATTENTION: a small window, terse, NO how-to/affordance leg (it would flood deep work).
            "resolution": {"strata": frozenset({"annotation", "chat", "event", "run"}), "howto_detail": "none", "budget": 800},
            "subtypes": {
                "default": {},
                # a focus instance that still wants the structural run-trail but nothing chatty:
                "structural": {"strata": frozenset({"event", "run"}), "budget": 600},
            },
            "consent": "act",
            "grain": "line", "shape": "linear-stream", "stage": False,   # NEVER stage (C4.3) — deep work, one/two lines
            "live": ["per-turn", "background"], "reserve_r": 2,
            "per_role_ctx": 1500, "main_ctx_tokens": 0, "brain_config": "voice-64k",
        },
        "walkthrough": {
            "label": "Walkthrough",
            "directive": "Actively guide: narrate what you are doing and direct the operator's attention step by step.",
            # GUIDED/show-me lens (§5): the howto/affordance leg is the POINT (narrate what-this-is /
            # what-you-can-do), full strata so the narration has the whole picture. A wider window.
            "resolution": {"strata": None, "howto_detail": "full", "budget": 6000},
            "subtypes": {
                "guided": {},                       # the operator drives, the RHM narrates each step
                "show-me": {"budget": 8000},        # the RHM drives the sequence (a richer read per step)
            },
            "consent": "offer",
            "grain": "paragraph", "shape": "linear-stream", "stage": True,
            "live": ["per-turn"], "reserve_r": 2,
            "per_role_ctx": 1500, "main_ctx_tokens": 0, "brain_config": "voice-64k",
        },
        "watch-and-react": {
            "label": "Watch & react",
            "directive": "Observe; comment only when relevant, and briefly.",
            # observe lens: events + run-trail are what matters (what's HAPPENING), terse, no flood; keep
            # the stable howto + presentation_pref (F1 — address-truth, a sibling of howto).
            "resolution": {"strata": frozenset({"event", "run", "howto", "presentation_pref"}),
                           "howto_detail": "terse", "budget": 1500},
            "consent": "act",
            "grain": "line", "shape": "linear-stream", "stage": True,
            "live": ["per-turn", "sense"], "reserve_r": 2,
            "per_role_ctx": 1500, "main_ctx_tokens": 0, "brain_config": "voice-64k",
        },
        "decide-for-me": {
            "label": "Decide for me",
            "directive": "Act on what the governance posture lets you act on (the AUTO/reversible classes — propose a node, run the graph) rather than asking; surface the rest for the operator. The routing is deterministic (the action's posture decides), not a judgement call. You still cannot self-approve; anything that needs approval is surfaced.",
            "resolution": {"strata": None, "howto_detail": "full", "budget": None},
            "consent": "act",
            "grain": "paragraph", "shape": "linear-stream", "stage": True,
            "live": ["per-turn", "background", "rollup"], "reserve_r": 2,
            "per_role_ctx": 1500, "main_ctx_tokens": 0, "brain_config": "voice-64k",
        },
        # D13: 'off' carries a one-line DESCRIPTION (was empty). chat() short-circuits on mode=='off'
        # BEFORE any directive is used, so this is purely descriptive for the surface — it does NOT
        # re-enable the RHM. modes_acceptance asserts non-empty directives only for m != 'off'.
        # resolution = the EMPTY lens: the RHM is asleep, nothing resolves (strata=empty set).
        "off": {
            "label": "Off",
            "directive": "The right-hand-man is asleep — no conversation, no actions. Switch any other mode on the presence dial to wake it.",
            "resolution": {"strata": frozenset(), "howto_detail": "none", "budget": 0},
            "consent": "none",
            "grain": "line", "shape": "linear-stream", "stage": False,   # NEVER stage (C4.3) — the dial is off
            # off: nothing fires (the dial is off) — only the spine is nominally live (chat() short-circuits).
            "live": ["per-turn"], "reserve_r": 2,
            "per_role_ctx": 1500, "main_ctx_tokens": 0, "brain_config": "voice-64k",
        },
    }
    # --- the 3 OLD NAMES, now DERIVED VIEWS of MODE_REGISTRY (no parallel tables — the join's law) ------
    # MODE_SPECS: the ModeSpec interface every resolution-half consumer + MODES/MODE_DIRECTIVES read. Each
    # ModeSpec is built from the registry entry's resolution-half fields → the SAME frozen objects as before
    # (subtypes absent → r.get("subtypes") is None → ModeSpec.subtypes default None, byte-for-byte today).
    MODE_SPECS = {
        m: ModeSpec(label=r["label"], directive=r["directive"], resolution=r["resolution"],
                    subtypes=r.get("subtypes"), consent=r["consent"])
        for m, r in MODE_REGISTRY.items()
    }
    # MODES: the 8-tuple in registry-insertion order (ORDER-CONTRACTED — modes_acceptance len==8 + the
    # _M_* mode-sets below frozenset over it). MODE_DIRECTIVES: the {mode: directive} prose map the
    # grounding context + capabilities() read. Both DERIVE from the one source — no copy to fall out of sync.
    MODES = tuple(MODE_REGISTRY)
    MODE_DIRECTIVES = {m: r["directive"] for m, r in MODE_REGISTRY.items()}
    DEFAULT_MODE = "listening"
    SYSTEM_GRAPH = "system"
    MODE_NODE = "rhm"
    # E2 — mode AUTO-DETECTION is a positionable CONFIG TOGGLE (direction §6.5: "the system CAN auto-detect
    # the mode, but whether/how is configured" — NOT hardcoded). The class constant is the DEFAULT FLOOR;
    # __init__ resolves the live value from COMPANY_MODE_AUTODETECT into self.MODE_AUTODETECT (X17 pattern).
    #   'off'     — manual only (operator-selected modes — TODAY's behaviour, the safe default).
    #   'suggest' — auto-detection PROPOSES a mode (a surfaced suggestion); never switches on its own.
    #   'auto'    — auto-detection SWITCHES the mode (set_mode the detected candidate).
    MODE_AUTODETECT_OPTIONS = ("off", "suggest", "auto")
    MODE_AUTODETECT = "off"

    # --- the MODEL-ROLE REGISTRY (registry-is-truth; mirrors STT_PROVIDERS / the node registry) -------
    # A ROLE is a named model-FUNCTION of the collective cognition: a specific job done by a model that
    # is NOT the conversational brain. The brain (rhm_config.model) is the primary/conscious role and
    # stays its OWN slot (widely read; the model-registry session owns it) — these are the AUXILIARY
    # roles. `judge` is the first (the voice circuit's finished-thought endpoint). Add a role TYPE here
    # (+ the code that consumes it) → it appears as a configurable slot in the UI automatically; you
    # never edit the config whitelist (bindings live in ONE `roles` dict).
    #
    # Each role DECLARES its full contract — Tim's "triggers, configs like outputs/tools, contexts, and
    # whatever else": the fields below are the role's self-description the config lab renders + binds.
    # WIRED-NOW fields (flow into the model call): default_model/base_url (None → the brain), knobs
    # (max_tokens/temperature/…), thinking, output, tools. DECLARED-design fields (captured + designable,
    # the growth path — NOT a faked general engine): `trigger` is descriptive today (judge's concrete
    # trigger is the voice circuit calling /api/voice/finished-thought); a general event→role trigger
    # engine, and per-role arbitrary tool-binding, come as their consuming code is built. `env_*` give
    # the resolution precedence: a config binding > env override > the declared default.
    # G2 (C2.1/C2.2): ROLE_REGISTRY is no longer a HARDCODED class dict — it is now a FILE-DISCOVERED
    # registry (runtime/roles.py + roles/*.py), mirroring how node-types self-register (registry.py).
    # The judge moved to roles/judge.py (role #0) UNCHANGED IN BEHAVIOUR: `self.ROLE_REGISTRY` is built
    # in __init__ as `{role_id: role.spec}` from the discovered registry — so resolve_role/roles() read
    # the SAME judge dict, only from the registry instead of this constant. Adding a role = adding a
    # roles/*.py file (the self-extending path). The `roles` rhm_config slot stays the per-binding
    # override. See roles/AGENTS.md (the drift home) + tests/roles_acceptance.py.

    # --- the MODEL KNOB CATALOG (G8.1 — dynamic knob resolution; mirrors STT_PROVIDERS/ROLE_REGISTRY) --
    # "all the configurable knobs for whatever is loaded" (Tim): a declarative catalog of the per-request
    # knobs a chat model exposes. knobs_for(model) resolves it DYNAMICALLY — tool-capability is PROBED
    # live (the existing _model_supports_tools, endpoint-aware), the rest are DECLARED-by-capability
    # (thinking/structured-output can't be universally probed; marked source='declared'). Emitted in the
    # NODE CONFIG SHAPE ({type,label,default,min?,max?,options?}) so the UI renders model-knobs with the
    # SAME NodeConfigForm it renders node config — one resolution, two faces (the RHM tools + the UI).
    # Load-time knobs (gpu-util/ctx) are per-service launch DATA (services.json load.env, the A mechanism),
    # not per-request — kept separate. Adding a knob = a row here; no dispatch edit.
    # S5 — the per-TTS-engine knob catalog (the comprehensive inventory the settings window renders). Each
    # engine row: knobs[] = {key, type, default, min/max/options?, scope: 'runtime'|'serve', note}. RUNTIME
    # knobs ride the /tts call (voice/speed) or the tts_voice override; SERVE knobs (exaggeration/cfg/ctx/
    # gpu_util) are env/service config — changing them restarts the engine. Sourced from each engine's code
    # (chatterbox.py/xtts.py/qwen3tts.py/cosyvoice.py/orpheus.py/tts_service.py), 2026-06-07.
    VOICE_ENGINE_KNOBS = {
        "kokoro":     [{"key": "voice", "type": "text", "default": "af_heart", "scope": "runtime", "note": "a Kokoro voice id (GET /voices)"},
                       {"key": "speed", "type": "number", "default": 1.0, "min": 0.5, "max": 2.0, "scope": "runtime", "note": "applied"}],
        "chatterbox": [{"key": "voice", "type": "text", "default": "(COMPANY_VOICE_REF clip)", "scope": "runtime", "note": "reference clip path to clone"},
                       {"key": "exaggeration", "type": "number", "default": 0.5, "min": 0.0, "max": 1.0, "scope": "serve", "note": "emotion intensity (COMPANY_CHATTERBOX_EXAGGERATION)"},
                       {"key": "cfg_weight", "type": "number", "default": 0.5, "min": 0.0, "max": 1.0, "scope": "serve", "note": "guidance (COMPANY_CHATTERBOX_CFG)"}],
        "xtts":       [{"key": "voice", "type": "text", "default": "(COMPANY_VOICE_REF clip)", "scope": "serve", "note": "speaker clip"},
                       {"key": "speed", "type": "number", "default": 1.0, "min": 0.5, "max": 2.0, "scope": "runtime", "note": "applied"},
                       {"key": "language", "type": "text", "default": "en", "scope": "serve", "note": "COMPANY_XTTS_LANG"}],
        "qwen3tts":   [{"key": "voice", "type": "text", "default": "(designed Australian woman)", "scope": "runtime", "note": "a VOICE DESCRIPTION — VoiceDesign instruct"}],
        "cosyvoice":  [{"key": "voice", "type": "text", "default": "(refined Australian woman instruct)", "scope": "runtime", "note": "an instruction (inference_instruct2)"}],
        "orpheus":    [{"key": "voice", "type": "text", "default": "tara", "scope": "runtime", "note": "a named Orpheus voice"},
                       {"key": "max_model_len", "type": "number", "default": 8192, "scope": "serve", "note": "vLLM ctx (COMPANY_ORPHEUS_MAXLEN)"},
                       {"key": "gpu_util", "type": "number", "default": 0.6, "min": 0.1, "max": 0.95, "scope": "serve", "note": "vLLM (COMPANY_ORPHEUS_GPU_UTIL)"}],
    }

    def voice_engine_knobs(self, engine: str | None = None) -> dict:
        """The TTS-engine knob catalog (S5) — all engines, or one. The settings window renders this so the
        operator sees every engine's real knobs (runtime vs serve-time)."""
        if engine:
            return {engine: self.VOICE_ENGINE_KNOBS.get(engine, [])}
        return dict(self.VOICE_ENGINE_KNOBS)

    MODEL_KNOBS = {
        "temperature":       {"type": "number", "label": "Temperature", "default": 0.7, "min": 0.0, "max": 2.0,
                              "applies": "always", "note": "sampling randomness"},
        "max_tokens":        {"type": "number", "label": "Max output tokens", "default": 1024, "min": 1, "max": 32768,
                              "applies": "always"},
        "top_p":             {"type": "number", "label": "Top-p", "default": 1.0, "min": 0.0, "max": 1.0,
                              "applies": "always"},
        "tools":             {"type": "boolean", "label": "Native tool-calling", "default": True,
                              "applies": "capability", "note": "PROBED live per the endpoint (vllm/ollama/litellm)"},
        "thinking":          {"type": "boolean", "label": "Reasoning / thinking", "default": False,
                              "applies": "declared", "note": "reasoning models (ollama think / a reasoning-parser)"},
        "structured_output": {"type": "choice", "label": "Structured output", "default": "none",
                              "options": ["none", "json", "json_schema"], "applies": "declared",
                              "note": "vLLM guided-decoding / ollama format=json"},
    }

    # --- VOICE PATHS (Tier 4 — the SWAPPABLE voice architecture; registry-is-truth) ------------------
    # Tim: "that [S2S] should be a swappable thing." Two ways the RHM can voice:
    #   pipeline — STT → brain → TTS (3 models, full control, BUILT, the default)
    #   s2s      — one fused audio→audio model (Qwen3-Omni/Moshi/GLM-Voice/mini-omni): sub-second,
    #              full-duplex, but the brain+voice are fused (less control). NO such model is on disk
    #              yet (only STT+TTS components + canary/granite which are speech→TEXT, not s2s) — so
    #              the s2s path is available:false until one is downloaded (mirrors a down-ear). The
    #              SWAPPABILITY is built now (a voice_path slot); the s2s runner is a fail-loud stub.
    VOICE_PATHS = {
        "pipeline": {"label": "Pipeline (STT → brain → TTS)", "built": True,
                     "note": "3 models, full per-stage control + config; the default. Tier 1 streaming."},
        "s2s":      {"label": "Speech-to-speech (one fused model)", "built": False,
                     "note": "sub-second + full-duplex; brain+voice fused. Needs an S2S model downloaded "
                             "(candidates: Qwen3-Omni, Moshi, GLM-Voice, mini-omni). No runner until then."},
    }
    # HF-cache name fragments that would indicate an s2s/omni model is present (probed by voice_paths()).
    _S2S_HINTS = ("omni", "moshi", "glm-voice", "glm4-voice", "mini-omni", "miniomni", "qwen2.5-omni",
                  "qwen3-omni", "ultravox", "llama-omni", "csm", "sesame")

    # MODE_DIRECTIVES is now DERIVED from MODE_SPECS above (one-source; the literal here was removed when
    # E1 folded the directive INTO the spec — see the MODE_SPECS block + `MODE_DIRECTIVES = {...}` derive).

    # ============================================================================================
    # CONCURRENT COGNITION G4 — the staged-response queue (the reply as PARTS).
    #
    # Two net-new registries, both L1 DATA (not control-flow), with their DRIFT HOME declared in
    # runtime/AGENTS.md (alongside RULE_OPS/DESTINATION_KINDS — the rule-engine registries) and a
    # drift assertion in tests/chat_parts_acceptance.py (mirrors EDGE_KINDS→contracts/AGENTS.md,
    # RULE_OPS→runtime/AGENTS.md). No net-new registry ships without its drift home (C9.4 / R2-FOLD H5).
    #
    # THOUGHT_SHAPES = the ~5 archetypes (E1 / E0-EXPLORE-SYNTHESIS), built ONCE. A shape declares HOW
    # a turn's cognition is shaped — net-new fields: `archetype` · `fanout` (the wave width policy) ·
    # `join` (the barrier-dep role, run://<turn>/<role>/* — None = no reduce) · `render_from` (which
    # role's output G7 draws the reply from). shape_for(mode) maps a presence mode → its shape.
    # ============================================================================================
    THOUGHT_SHAPES = {
        # linear-stream (voice): a sequence of parts, each enriched by the prior + the role wave; no
        # reduce/join. The DEFAULT conversational shape (listening/text-only/walkthrough/decide-for-me).
        "linear-stream": {"archetype": "linear-stream", "fanout": "cast",  "join": None,
                          "render_from": None,
                          "desc": "a sequence of reply parts, each enriched by the role wave (voice's shape)"},
        # reduce-tree (codebase map-reduce): fan-out → a `join` role reduces → ONE answer part.
        "reduce-tree":   {"archetype": "reduce-tree",   "fanout": "cast",  "join": "reduce",
                          "render_from": "reduce",
                          "desc": "fan-out the cast → a join role reduces their outputs → one answer"},
        # jury-select (altitude-translation): N candidate draws → score → winner (the C2.4 jury).
        "jury-select":   {"archetype": "jury-select",   "fanout": "draws", "join": "verdict",
                          "render_from": "verdict",
                          "desc": "N candidate draws → a deterministic verdict picks the winner"},
        # scatter-route (typed-triage): N classifications → own lanes, NO reduce, NO reply part.
        "scatter-route": {"archetype": "scatter-route", "fanout": "cast",  "join": None,
                          "render_from": None,
                          "desc": "N classifications routed to their own lanes (no reduce, no reply)"},
        # scatter-write (background): N consolidations → sinks (address/lane), NO spoken reply.
        "scatter-write": {"archetype": "scatter-write", "fanout": "cast",  "join": None,
                          "render_from": None,
                          "desc": "N consolidations written to sinks (background; no reply)"},
    }

    # PART-GRAIN view (C4.1): a per-MODE {grain, shape, stage} — `grain` is the unit a reply part spans
    # (line / beat / paragraph; the staged reply is chunked at this grain so the part follows the mode),
    # `shape` names the THOUGHT_SHAPE, `stage` = whether this mode STAGES at all (focus/background/off
    # NEVER stage — C4.3; a non-staging mode falls through to the one-part path). L1 DATA: switching mode
    # changes the grain by reading THIS view, never a branch per mode. Now a DERIVED VIEW of MODE_REGISTRY
    # (the mode-dial join — these axes live on the one source above; no parallel table).
    PART_GRAIN = {m: {"grain": r["grain"], "shape": r["shape"], "stage": r["stage"]}
                  for m, r in MODE_REGISTRY.items()}

    # ============================================================================================
    # CONCURRENT COGNITION G5 — ACTIVATION-CONTEXT ALLOCATION (C5.5 · the dial generalised).
    #
    # A MODE allocates (L1 declared data): which activation contexts are LIVE, the slot BUDGET (reserve_r
    # + per-role context — the SlotBudget is COMPUTED from these against the live registry, never a
    # literal), AND the brain CONFIG (R2-FOLD H1: a swarm-heavy mode wants the higher-util swarm-brain
    # ~16K/0.63; a voice-depth mode the 64K brain). The brain config is DECLARED here (the mode→loadout
    # registry, H8) — it is NOT swapped by this build (driving `company up/swap` is the always-on
    # GPU-loadout concern, needs-tim). The registry of contexts themselves lives in runtime/activation.py
    # (ACTIVATION_CONTEXTS, the drift home in runtime/AGENTS.md). `per-turn` is ALWAYS live (the spine).
    #
    # THE RESERVE FLOOR (sacred, C5.5): reserve_r is the per-turn live-stream reservation; activation.py
    # FAILS LOUD if a mode declares it below FLOOR_RESERVE_R. A non-turn cast runs under swarm_slots =
    # max_num_seqs − reserve_r, bounded by the SAME process-wide VRAM gate → R permits always stay free.
    # main_ctx_tokens models how deep the main conversation is assumed to be (the C0.5 deep-main KV bind).
    # ============================================================================================
    # Now a DERIVED VIEW of MODE_REGISTRY (the mode-dial join — these axes live on the one source above;
    # no parallel table). Each entry = the activation/budget axes of the registry row: which contexts are
    # LIVE, the slot budget params (reserve_r/per_role_ctx/main_ctx_tokens), and the declared brain config.
    ACTIVATION_ALLOCATION = {
        m: {k: r[k] for k in ("live", "reserve_r", "per_role_ctx", "main_ctx_tokens", "brain_config")}
        for m, r in MODE_REGISTRY.items()
    }

    def activation_allocation(self, mode: str) -> dict:
        """C5.5 — the activation-context allocation for a mode: the LIVE contexts, the slot budget
        params (reserve_r/per_role_ctx/main_ctx_tokens — the SlotBudget is COMPUTED from these), and
        the declared brain config (the mode→loadout registry, H8). Fail loud on an unknown mode (rule
        8 — never a fabricated allocation). `per-turn` is always present (the spine)."""
        alloc = self.ACTIVATION_ALLOCATION.get(mode)
        if alloc is None:
            raise ValueError(f"activation_allocation: unknown mode {mode!r} — registered: "
                             f"{sorted(self.ACTIVATION_ALLOCATION)} (fail loud, never a fabricated allocation).")
        out = {k: (list(v) if isinstance(v, list) else v) for k, v in alloc.items()}
        if "per-turn" not in out["live"]:                  # the spine is always live (defensive)
            out["live"] = ["per-turn"] + out["live"]
        return out

    def mode_registry(self, mode: str) -> dict:
        """The mode-dial join's SINGLE QUERY: ALL axes of a mode in one read — the resolution/context half
        (label/directive/resolution/subtypes/consent), the thought-shape/staging half (grain/shape/stage),
        and the activation/budget half (live/reserve_r/per_role_ctx/main_ctx_tokens/brain_config). The 3
        old views (MODE_SPECS/PART_GRAIN/ACTIVATION_ALLOCATION) DERIVE from this same source, so the FE /
        cognition can read the whole mode declaration from ONE place. Returns a COPY (the caller cannot
        mutate the class constant). Fail loud on an unknown mode (rule 8 — never a fabricated declaration)."""
        row = self.MODE_REGISTRY.get(mode)
        if row is None:
            raise ValueError(f"mode_registry: unknown mode {mode!r} — registered: "
                             f"{sorted(self.MODE_REGISTRY)} (fail loud, never a fabricated declaration).")
        return {k: (list(v) if isinstance(v, list) else dict(v) if isinstance(v, dict) else v)
                for k, v in row.items()}

    @staticmethod
    def _mode_axes_jsonsafe(axes):
        """SEAM 1 helper (A · mode reach-extension): recursively coerce a `mode_registry()` declaration into
        a JSON-safe form so `capabilities()` can serve the WHOLE row (capabilities() is `json.dumps`'d raw by
        the bridge with no set-handler). The ONLY non-serializable values in a mode row are sets/frozensets —
        `resolution.strata` and `subtypes.*.strata` (a frozenset of gather-strata; None → admit-all). Every
        set/frozenset → a sorted list (deterministic order); dicts/lists recurse; everything else passes
        through unchanged. None stays None. This applies the SAME frozenset→sorted-list conversion the old
        hand-built capabilities block did, but whole-tree — so adding a future set-valued axis to
        MODE_REGISTRY can never leak a non-serializable value to the bridge (registry-is-truth, fail-safe)."""
        if isinstance(axes, (set, frozenset)):
            return sorted(axes)
        if isinstance(axes, dict):
            return {k: Suite._mode_axes_jsonsafe(v) for k, v in axes.items()}
        if isinstance(axes, (list, tuple)):
            return [Suite._mode_axes_jsonsafe(v) for v in axes]
        return axes

    def fire_activation(self, context: str, *, mode: str | None = None,
                        sense_event: dict | None = None, turn_id: str | None = None):
        """C5.2/C5.3 — fire a non-turn activation context (background/sense): the mode's cast fires via
        run_swarm under the mode-allocated budget; outputs route over the non-consequential
        DESTINATION_KINDS (surface/address/lane — NO reply, NO resolve). Thin delegate to
        runtime/activation.py (reuse-don't-parallel — the driver lives by run_swarm)."""
        from runtime import activation as _act
        return _act.fire_activation(self, context, mode=mode, sense_event=sense_event, turn_id=turn_id)

    def consolidate_rollup(self, *, since: int = -1, mode: str | None = None,
                           turn_id: str | None = None, gc: bool = False):
        """C5.4 — the rollup trigger: consolidate the swarm's OWN run-records (cognition.wave telemetry)
        into ONE rollup distribution at a run:// address (introspective-data-building, read-half — fires
        no swarm). Thin delegate to runtime/activation.py."""
        from runtime import activation as _act
        return _act.consolidate_rollup(self, since=since, mode=mode, turn_id=turn_id, gc=gc)

    def shape_for(self, mode: str) -> dict:
        """The THOUGHT_SHAPE for a mode (C4.1/G4): read the per-mode grain row → its shape. Fail loud on
        an unknown mode (rule 8 — never default-fire a fabricated shape). Returns the shape dict (the
        archetype + fanout/join/render_from + desc)."""
        row = self.PART_GRAIN.get(mode)
        if row is None:
            raise ValueError(f"shape_for: unknown mode {mode!r} — registered modes: {sorted(self.PART_GRAIN)}")
        sid = row["shape"]
        shape = self.THOUGHT_SHAPES.get(sid)
        if shape is None:
            raise ValueError(f"shape_for: mode {mode!r} names unknown shape {sid!r} — registered shapes: "
                             f"{sorted(self.THOUGHT_SHAPES)} (fail loud, never a fabricated shape).")
        return dict(shape)

    def grain_for(self, mode: str) -> str:
        """The part GRAIN for a mode (C4.1) — line / beat / paragraph. Fail loud on an unknown mode."""
        row = self.PART_GRAIN.get(mode)
        if row is None:
            raise ValueError(f"grain_for: unknown mode {mode!r} — registered modes: {sorted(self.PART_GRAIN)}")
        return row["grain"]

    def mode_stages(self, mode: str) -> bool:
        """Whether `mode` STAGES a multi-part reply at all (C4.3): focus/background/off never stage."""
        row = self.PART_GRAIN.get(mode)
        return bool(row and row.get("stage"))

    def _rhm_cfg(self) -> dict:
        """The RHM's config node (system graph) — holds mode + model + base_url + persona."""
        g = self.store.load_graph(self.SYSTEM_GRAPH)
        if g:
            for n in g.nodes:
                if n.id == self.MODE_NODE:
                    return dict(n.config)
        return {}

    def _ensure_rhm_node(self) -> None:
        g = self.store.load_graph(self.SYSTEM_GRAPH)
        if not g or not any(n.id == self.MODE_NODE for n in g.nodes):
            self.create_node(self.SYSTEM_GRAPH, "rhm_mode",
                             config={"mode": self.DEFAULT_MODE}, node_id=self.MODE_NODE)

    def get_mode(self) -> str:
        return self._rhm_cfg().get("mode", self.DEFAULT_MODE)

    def set_mode(self, mode: str) -> str:
        if mode not in self.MODES:
            raise ValueError(f"unknown mode {mode!r} — one of {self.MODES}")
        self._ensure_rhm_node()
        self.set_config(self.SYSTEM_GRAPH, self.MODE_NODE, {"mode": mode})   # editing a parameter (same verb)
        self._emit("mode", f"presence → {mode}", address="ui://chrome/toolbar")   # S2: presence dial lives in the toolbar
        return mode

    def _mode_directive(self, mode: str) -> str:
        return self.MODE_DIRECTIVES.get(mode, "")

    # --- E1: the mode SUB-TYPE (the instance parameter in §6.2's (mode-type) × (instance) factoring) ---
    # The sub-type is a SECOND rhm_mode-node config key ('submode'), edited by the SAME verb as the mode
    # (set_config). Schema-additive: an rhm_mode node WITHOUT a 'submode' key reads as None → the
    # mode-type's bare lens (no instance override). So old graphs keep working byte-for-byte.
    def get_submode(self) -> str | None:
        return self._rhm_cfg().get("submode")

    def set_submode(self, submode: str | None) -> str | None:
        """Set the instance sub-type for the CURRENT mode-type. FAIL LOUD (rule 4) if the sub-type isn't
        declared on the current mode-type's spec — never a silent wrong value. None clears it (bare lens)."""
        mode = self.get_mode()
        spec = self.MODE_SPECS.get(mode)
        valid = set((spec.subtypes or {})) if spec else set()
        if submode is not None and submode not in valid:
            raise ValueError(f"unknown sub-type {submode!r} for mode {mode!r} — one of {sorted(valid) or '(none declared)'}")
        self._ensure_rhm_node()
        self.set_config(self.SYSTEM_GRAPH, self.MODE_NODE, {"submode": submode})
        self._emit("mode", f"sub-type → {mode}/{submode}", address="ui://chrome/toolbar")
        return submode

    def resolution_spec_for(self, mode: str | None = None, submode: str | None = None) -> dict:
        """E1 — the LOAD-BEARING resolver: (mode-type declarations) × (instance parameters) → the
        context-resolution spec the R2 path consumes AS DATA. This is the §6.2 relational primitive made
        a function: `resolved context = (mode-type) × (instance) over ONE shared store`.

        It is called ONCE at the resolution caller (`_chat_context`) and the resulting DICT is threaded
        down the R2 path — so NO mode-NAME ever appears in `_resolve_context_at`/`_r2_gather`/`_r2_howto_at`
        (registry-is-truth: the resolution shape is DATA from the spec, never an `if mode ==` branch).

        Resolution order (mode-type lens, then instance override — §6.2):
          1. start from the mode-type's `resolution` declaration (the LENS — what/how it admits);
          2. overlay the sub-type's overrides (the INSTANCE — what specifically, this time).
        With mode=None → the current live mode (read from the rhm_mode node); submode=None → the current
        live sub-type. Returns {'strata','howto_detail','budget'} — every key always present (the lens'
        default fills any the sub-type didn't override). An UNKNOWN mode degrades to the listening lens
        with a warning (fail-loud-legible — never crash the resolver, mirroring _resolve_context_at)."""
        if mode is None:
            mode = self.get_mode()
        spec = self.MODE_SPECS.get(mode)
        if spec is None:
            # locus-bound: the mode lives on the presence dial (ui://chrome/toolbar — same locus set_mode
            # stamps), so this config-resolution warning is honestly addressed, not locus-less.
            self._emit("warning", f"resolution_spec_for: unknown mode {mode!r} — defaulting to listening lens",
                       address="ui://chrome/toolbar")
            spec = self.MODE_SPECS["listening"]
        base = dict(spec.resolution or {})
        out = {"strata": base.get("strata"),
               "howto_detail": base.get("howto_detail", "full"),
               "budget": base.get("budget")}
        # INSTANCE overlay: the sub-type (an instance parameter) refines the SAME mode-type lens.
        if submode is None:
            submode = self.get_submode()
        if submode is not None:
            sub = (spec.subtypes or {}).get(submode)
            if sub is None:
                # honest: a sub-type set on the node that isn't declared on THIS mode-type (e.g. the mode
                # was switched after a sub-type was set) — ignore it with a warning, never a wrong read.
                # locus-bound to the presence dial (the mode/sub-type live there).
                self._emit("warning", f"resolution_spec_for: sub-type {submode!r} not declared on mode {mode!r} — using bare lens",
                           address="ui://chrome/toolbar")
            else:
                for k in ("strata", "howto_detail", "budget"):
                    if k in sub:
                        out[k] = sub[k]
        return out

    def autodetect_mode(self, candidate: str) -> dict:
        """E2-BACKEND — honour the mode AUTO-DETECT toggle (self.MODE_AUTODETECT) over a SUPPLIED candidate
        mode. The toggle (a config item, NOT hardcoded — direction §6.5) decides what auto-detection DOES:
          • 'off'     — NO-OP: auto-detection is disabled; the operator's mode is untouched (today's default).
          • 'suggest' — PROPOSE the candidate (emit a surfaced 'mode' suggestion event); never switch.
          • 'auto'    — SWITCH to the candidate via the SAME `set_mode` (no parallel path).
        FAIL LOUD (rule 4/8): the candidate must be a real registered mode — never a fabricated/unknown one.
        The DETECTOR that PRODUCES the candidate is a deferred seam (§11 — zero detector in the repo today);
        this method honours the toggle over whatever candidate it's GIVEN, and never invents a detection.
        Returns a legible {toggle, candidate, applied, action} so the caller/surface sees exactly what
        happened (no silent no-op — rule 4)."""
        if candidate not in self.MODES:
            raise ValueError(f"autodetect_mode: unknown candidate {candidate!r} — one of {self.MODES} "
                             f"(rule 8: never fabricate a mode)")
        toggle = self.MODE_AUTODETECT
        if toggle == "off":
            return {"toggle": toggle, "candidate": candidate, "applied": None, "action": "noop"}
        if toggle == "suggest":
            self._emit("mode", f"auto-detect SUGGESTS presence → {candidate} (toggle=suggest; not switched)",
                       address="ui://chrome/toolbar")
            return {"toggle": toggle, "candidate": candidate, "applied": None, "action": "suggested"}
        # 'auto' — switch via the one set_mode (validated above; the toggle was env-validated by _cfg_choice).
        self.set_mode(candidate)
        return {"toggle": toggle, "candidate": candidate, "applied": candidate, "action": "switched"}

    # --- the STT (ear) slot: a SWAPPABLE speech-to-text provider, mirroring the brain-model slot ---
    # The RHM's ear is a config slot just like its brain model — so the operator can swap providers
    # without code. The stt lane (voice/stt.py) is the source of truth for WHAT ears exist; this slot
    # records WHICH one is selected. Because the stt lane DEPENDS on this lane and may not have shipped
    # its richer registry (STT_PROVIDERS / available_stt()) yet, we GUARD the import and degrade
    # gracefully: prefer the new registry when present, else fall back to the current `available()` dict
    # + `DEFAULT_PROVIDER`. Never fabricate a provider id (rule 8) — the valid ids come from voice/stt.py.
    @staticmethod
    def _stt_module():
        """The voice STT module, or None if voice isn't importable here (a status read must never
        crash a turn). Namespace import (no voice/__init__.py) — mirrors bridge.py's usage."""
        try:
            from voice import stt as voice_stt
            return voice_stt
        except Exception:
            return None

    def available_stt(self) -> dict:
        """Which STT providers exist + are usable right now — the registry the UI/RHM reads (never
        guess). Prefers the stt lane's richer `available_stt()` (status read, never raises) when it has
        shipped; else the current `available()` {id: usable}. {} when voice isn't importable."""
        m = self._stt_module()
        if m is None:
            return {}
        fn = getattr(m, "available_stt", None) or getattr(m, "available", None)
        try:
            return fn() if fn else {}
        except Exception:
            return {}

    def _stt_provider_ids(self) -> list:
        """The valid STT provider IDS to validate a selection against — from voice/stt.py's source of
        truth (STT_PROVIDERS when present, else the keys of available()). Empty when voice is absent."""
        m = self._stt_module()
        if m is None:
            return []
        providers = getattr(m, "STT_PROVIDERS", None)
        if isinstance(providers, dict):
            return list(providers.keys())
        try:
            return list((getattr(m, "available", lambda: {})() or {}).keys())
        except Exception:
            return []

    def _stt_default(self) -> str:
        """The default ear id — the stt lane's STT_DEFAULT/DEFAULT_PROVIDER when present, else ''."""
        m = self._stt_module()
        if m is None:
            return ""
        return getattr(m, "STT_DEFAULT", None) or getattr(m, "DEFAULT_PROVIDER", "") or ""

    # --- RHM configs (E1-E2): model/provider + persona, all configurable + persistent ---
    def rhm_config(self) -> dict:
        from fabric import config as fcfg
        c = self._rhm_cfg()
        return {"mode": c.get("mode", self.DEFAULT_MODE),
                "model": c.get("model") or fcfg.DEFAULT_BRAIN,
                "base_url": c.get("base_url") or fcfg.DEFAULT_BASE_URL,
                "persona": c.get("persona", ""),
                # call-site timeout (D2): the interactive RHM model calls (chat reply, react) inherit
                # THIS, so the RHM never hangs minutes on a slow endpoint. Default DEFAULT_TIMEOUT (the
                # moderate 180s); configurable + persistent like the rest. Schema-additive (absent → default).
                # consult() + the self-coding calls deliberately use the longer DEFAULT_CLOUD_TIMEOUT
                # directly (they can wait) — see those call sites; this slot governs the INTERACTIVE calls.
                "timeout": int(c.get("timeout") or fcfg.DEFAULT_TIMEOUT),
                # voice-trial lane H: surface the per-mode voice toggle in the config the FE reads.
                # Default 'on' so a node with no field is voice-enabled (schema-additive).
                "voice_enabled": c.get("voice_enabled", "on"),
                # the STT (ear) slot — WHICH speech-to-text provider the RHM listens through. A config
                # slot mirroring `model` (the brain). Default = the stt lane's default ear when present
                # (else ''); the operator swaps providers without code. Schema-additive (absent → default).
                "stt": c.get("stt") or self._stt_default(),
                # the TTS slots (G4.2): an OPTIONAL active-engine + voice-arg OVERRIDE. Default '' →
                # the circuit uses the PERSONA's engine (personas.py) — so qwen3tts stays Sable's default,
                # nothing changes unless the operator explicitly picks an engine. Lets the config lab swap
                # the voice engine + voice-arg live without touching the persona. Schema-additive.
                "tts_engine": c.get("tts_engine", ""),
                "tts_voice": c.get("tts_voice", ""),
                # the VOICE PATH slot (Tier 4): 'pipeline' (default, built) or 's2s' (needs a model).
                "voice_path": c.get("voice_path", "pipeline"),
                # the VOICE INPUT MODE slot (V1.3): how the mic finalises a turn — 'push_to_talk' (tap to
                # start, tap to stop — the default) or 'auto_listen' (speak; on a pause the finished-thought
                # judge decides whether to fire the turn — "reply on a finished thought, not a silence
                # timer"). Two DISTINCT capabilities the operator switches between. Schema-additive.
                "voice_input_mode": c.get("voice_input_mode", "push_to_talk"),
                # the ROLE BINDINGS — {role_id: {model?, base_url?, knobs?, ...}} per the ROLE_REGISTRY.
                # n model-FUNCTION roles (judge first; more to come) each bind a model + config from the
                # live registry. Stored as ONE dict so adding a role never touches the config whitelist.
                # Schema-additive (absent → {}); the brain stays its OWN slot (`model`) — NOT a role here.
                "roles": c.get("roles", {}),
                # S5 — the brain's runtime knobs (temperature/max_tokens/top_p), set from the settings
                # window; reach the chat call. Absent → endpoint defaults. Schema-additive.
                "brain_knobs": c.get("brain_knobs", {})}

    def voice_enabled(self) -> bool:
        """Lane H — is voice on for the current presence? Reads the rhm node's `voice_enabled`
        CONFIG (the per-mode voice toggle), defaulting to True when absent (schema-additive: an old
        node with no field is voice-on). The conversation loop / a voice-gated path consults THIS
        rather than assuming voice; 'off' here means the mode runs text-only even with engines up.
        Also gated by the presence dial: mode 'off' (the RHM disabled) is never voice-on."""
        if self.get_mode() == "off":
            return False
        return str(self._rhm_cfg().get("voice_enabled", "on")).lower() != "off"

    def set_rhm_config(self, updates: dict) -> dict:
        allowed = {k: v for k, v in (updates or {}).items()
                   if k in ("model", "base_url", "persona", "mode", "voice_enabled", "timeout", "stt",
                            "roles", "tts_engine", "tts_voice", "voice_path", "voice_input_mode", "brain_knobs", "MODE_AUTODETECT")}
        if "brain_knobs" in allowed:                          # S5 — temperature/max_tokens/top_p (numeric, fail-loud)
            bk = allowed["brain_knobs"]
            if not isinstance(bk, dict):
                raise ValueError("brain_knobs must be a dict {temperature?,max_tokens?,top_p?}")
            clean = {}
            for k, v in bk.items():
                if k not in ("temperature", "max_tokens", "top_p"):
                    raise ValueError(f"unknown brain knob {k!r} — one of (temperature,max_tokens,top_p)")
                if v is not None:
                    try:
                        clean[k] = int(v) if k == "max_tokens" else float(v)
                    except (TypeError, ValueError):
                        raise ValueError(f"brain knob {k!r} must be numeric, got {v!r}")
            existing = dict(self.rhm_config().get("brain_knobs", {})); existing.update(clean)
            allowed["brain_knobs"] = existing                 # merge (set one knob without resetting another)
        if "voice_input_mode" in allowed:                     # V1.3 — push_to_talk | auto_listen (fail-loud)
            vim = str(allowed["voice_input_mode"]).strip()
            if vim not in ("push_to_talk", "auto_listen"):
                raise ValueError(f"unknown voice_input_mode {vim!r} — one of ('push_to_talk','auto_listen')")
            allowed["voice_input_mode"] = vim
        if "voice_path" in allowed:                           # the voice-path slot (registry-is-truth)
            vp = str(allowed["voice_path"]).strip()
            if vp not in self.VOICE_PATHS:
                raise ValueError(f"unknown voice_path {vp!r} — one of {sorted(self.VOICE_PATHS)}")
            allowed["voice_path"] = vp
        if "tts_engine" in allowed and str(allowed["tts_engine"]).strip():
            # validate against the engine port map (registry-is-truth; '' clears → persona default)
            from voice import loop as _vl
            eng = str(allowed["tts_engine"]).strip()
            if eng not in _vl.ENGINE_PORTS and eng != "kokoro":
                raise ValueError(f"unknown TTS engine {eng!r} — one of {['kokoro'] + sorted(_vl.ENGINE_PORTS)}")
            allowed["tts_engine"] = eng
        if "roles" in allowed:                                # the role-binding registry slot (n roles)
            incoming = allowed["roles"]
            if not isinstance(incoming, dict):
                raise ValueError("roles must be a dict {role_id: {model?, base_url?, knobs?, ...}}")
            for rid, binding in incoming.items():
                if rid not in self.ROLE_REGISTRY:             # registry-is-truth: fail loud on an unknown role
                    raise ValueError(f"unknown role {rid!r} — registered roles: {sorted(self.ROLE_REGISTRY)}. "
                                     f"Author from the registry, never invent (add a role TYPE in code first).")
                if not isinstance(binding, dict):
                    raise ValueError(f"role {rid!r} binding must be a dict (model?/base_url?/knobs?/…)")
            # MERGE with the existing bindings (set_config does a shallow top-level update, which would
            # REPLACE the whole roles dict — so we deep-merge here). THREE levels so a partial update is
            # non-destructive: (1) binding one role never wipes a SIBLING role; (2) within a role,
            # incoming keys override, others preserved; (3) the `knobs` SUB-dict deep-merges too, so
            # setting one knob (e.g. temperature) never resets another (e.g. max_tokens). Verified: a
            # partial knob update used to drop the other knob to its default — this keeps both.
            existing = dict(self.rhm_config().get("roles", {}))
            for rid, binding in incoming.items():
                merged = dict(existing.get(rid, {}))
                inc = dict(binding)
                if "knobs" in inc and isinstance(merged.get("knobs"), dict):
                    knobs = dict(merged["knobs"]); knobs.update(inc["knobs"] or {})
                    inc["knobs"] = knobs                      # deep-merge the knobs sub-dict
                merged.update(inc)
                existing[rid] = merged
            allowed["roles"] = existing
        if "mode" in allowed and allowed["mode"] not in self.MODES:
            raise ValueError(f"unknown mode {allowed['mode']!r}")
        if "MODE_AUTODETECT" in allowed:                      # GC6 (E2-live): the auto-detect toggle slot
            # The FE writes the SAME key composition_config exposes (`MODE_AUTODETECT`); we persist it
            # under the node-config slot `mode_autodetect` (lowercase, matching the slot convention so
            # _rhm_cfg/__init__ read it back). FAIL LOUD (rule 4/8) on a value outside the registered
            # options — mirrors _cfg_choice's validation discipline (off/suggest/auto only; never invent).
            ad = str(allowed.pop("MODE_AUTODETECT")).strip()
            if ad not in self.MODE_AUTODETECT_OPTIONS:
                raise ValueError(f"MODE_AUTODETECT must be one of {tuple(self.MODE_AUTODETECT_OPTIONS)}, "
                                 f"got {ad!r} (rule 8: never fabricate a value)")
            allowed["mode_autodetect"] = ad                   # persist under the lowercase slot key
            # X17 re-resolve — set the LIVE instance attr so autodetect_mode() + capabilities() honour
            # the new value IMMEDIATELY (this turn), without waiting for a reload. Persistence (below,
            # via set_config) carries it across a reload; __init__ re-seeds self.MODE_AUTODETECT from it.
            self.MODE_AUTODETECT = ad
        if "stt" in allowed:                                  # the ear slot — validate against voice/stt.py's
            # source of truth (never fabricate a provider id, rule 8). When the stt lane's registry has
            # shipped we validate ∈ its ids; until then (registry absent → no ids) we accept any non-empty
            # str (TODO: tighten once voice/stt.py exports STT_PROVIDERS/available_stt — coordinated with
            # the stt lane, which depends on THIS slot existing; do not block on it).
            ids = self._stt_provider_ids()
            val = str(allowed["stt"]).strip()
            if not val:
                raise ValueError("stt provider must be a non-empty id")
            if ids and val not in ids:
                raise ValueError(f"unknown STT provider {val!r} — one of {ids}")
            allowed["stt"] = val
        if "voice_enabled" in allowed and str(allowed["voice_enabled"]).lower() not in ("on", "off"):
            raise ValueError(f"voice_enabled must be 'on' or 'off', got {allowed['voice_enabled']!r}")
        if "timeout" in allowed:                              # the interactive call-site timeout — positive int
            try:
                t = int(allowed["timeout"])
            except (TypeError, ValueError):
                raise ValueError(f"timeout must be a positive integer (seconds), got {allowed['timeout']!r}")
            if t <= 0:
                raise ValueError(f"timeout must be a positive integer (seconds), got {allowed['timeout']!r}")
            allowed["timeout"] = t
        if not allowed:
            return self.rhm_config()
        self._ensure_rhm_node()
        self.set_config(self.SYSTEM_GRAPH, self.MODE_NODE, allowed)
        self._emit("config", "RHM config → " + ", ".join(f"{k}={v}" for k, v in allowed.items()),
                   address="ui://chrome/chat")   # S2: RHM config is the chat organ's settings
        return self.rhm_config()

    # --- the twin (B1, B3): the explicit model-of-Tim + provenance grading ---
    @staticmethod
    def _provenance_grade(role: str) -> str:
        """Tim's own words are GOLD (the only thing that trains the twin); the twin's output is
        WORKING-grade inference and must never masquerade as ground truth (prevents model-collapse)."""
        return "gold" if role == "user" else "working"

    @staticmethod
    def _provenance_source(role: str) -> str:
        """The SOURCE of a turn — operator (Tim) vs twin (the system). Grade alone is role-derived
        and launderable; the source travels with the turn so the twin's own output can never count
        as training signal even if its text is resubmitted as a 'user' turn (red-team F4)."""
        return "operator" if role == "user" else "twin"

    def _model_of_tim_digest(self, max_chars: int = 2600) -> str:
        """A COMPACT extract of the EXPLICIT model of Tim (principle headers + their statements) for
        the twin's context. The full text is drillable via the model_of_tim node. '' if unavailable."""
        import os
        from nodes import model_of_tim as mot
        path = os.environ.get("COMPANY_MODEL_OF_TIM", mot.DEFAULT_PATH)
        try:
            text = open(path, encoding="utf-8").read()
        except Exception:
            return ""
        lines, out = text.splitlines(), []
        for i, ln in enumerate(lines):
            s = ln.strip()
            if s.startswith("## "):                                   # a principle/law title
                out.append("• " + s[3:].strip())
            elif s.startswith("**") and "**" in s[2:]:                # its bold one-line statement
                out.append("  " + s.strip("*").split("**")[0].strip())
        digest = "\n".join(out)
        return digest[:max_chars]

    def training_signal(self) -> list:
        """Only operator-sourced GOLD turns train the twin — NEVER the twin's own output, even if it
        was laundered back in as a 'user' turn. Two guards (red-team F4): source must be 'operator'
        (not 'twin'), and the text must not echo any twin/assistant turn in history (echo-guard)."""
        history = self.store.chat_history(999)
        twin_texts = {(t.get("text") or "").strip()
                      for t in history if t.get("role") == "assistant" or t.get("source") == "twin"}
        return [t for t in history
                if t.get("grade") == "gold"
                and t.get("source", "operator") != "twin"
                and (t.get("text") or "").strip() not in twin_texts]

    # --- the right-hand-man: the coherent voice of the Company about ITSELF (I2) ---
    def _chat_context(self, graph_id: str, focus: dict | None = None, intent: str | None = None) -> str:
        """Compact GROUND TRUTH — live system state, not the codebase (context-05 rung 1).
        With `focus` (the operator's current canvas selection), the RHM gains CO-PRESENCE:
        the focused nodes' full detail (output/config) — the shared perceptual field where
        'context is a consequence of what I'm doing' (two planes, one state).

        X13 (Convergence) — `intent` (the operator's current chat MESSAGE, passed by `chat()`) is the
        SEMANTIC ranking query for R2: the locus context is ranked by RELEVANCE to what the operator is
        actually asking, not just location+age. Optional (default None) so every existing caller is
        unchanged (pre-X13 recency·proximity·pin ranking)."""
        nowv = self.now(graph_id)
        st = self.state(graph_id)
        by = {n["id"]: n for n in st["nodes"]}
        nodes = "; ".join(
            f"{n['id']}({n['type']}, {'resolved' if n['content_hash'] else 'unresolved'})"
            for n in st["nodes"]) or "(none)"
        evs = "; ".join(f"{e['kind']}: {e['summary']}" for e in self.store.recent_events(6)) or "(none)"

        # --- WHOLE-INTERFACE grounding (Tim: "everything it needs to be aware of in the whole
        # interface") — every value below comes from the LIVE registry/state, never fabricated. The
        # model reads are fail-loud-LEGIBLE (rule 4): a down endpoint renders a marker + emits a
        # warning, never a silent omission and never a crash (a raise here would break every turn).
        try:
            chat_models = self.available_models()             # chat — cached; warns on a down endpoint
        except Exception as e:                                 # defensive: never let grounding crash a turn
            self._emit("warning", f"chat model registry unreachable in RHM context ({type(e).__name__})")
            chat_models = None
        try:
            embed_models = self.models_at("embed")            # embed — its OWN endpoint; may be down
        except Exception as e:
            self._emit("warning", f"embed model registry unreachable in RHM context ({type(e).__name__})")
            embed_models = None
        chat_s = ", ".join(chat_models) if chat_models else "(endpoint unreachable)"
        embed_s = ", ".join(embed_models) if embed_models else "(endpoint unreachable)"

        mode = nowv["mode"]
        modes_s = ", ".join(self.MODES)
        # render ONLY the verbs AVAILABLE in this mode×context (mode-primary, context-refines), from
        # the SAME available_verbs() the tools array is built from — so the two channels (what the
        # prompt says it can do + what the native tools array offers) AGREE by construction. (Was: all
        # 7 unconditionally, which told the RHM it could `run` an empty graph or `build` in watch mode.)
        ctx = self._affordance_context(graph_id, focus)
        avail = self.available_verbs(mode, ctx)
        verbs_s = ("; ".join(f"{v} ({self.RHM_VERB_DESC.get(v, '')})" for v in avail)
                   if avail else "(none in this mode/context)")
        lanes = self.inbox_lanes()
        n_esc = lanes["counts"]["escalations"]
        # count AND what's awaiting — so the RHM can answer "what's awaiting", not just "how many".
        esc_titles = []
        for d in lanes["live_escalations"][:6]:
            pl = d.get("payload") or {}
            esc_titles.append(str(pl.get("title") or pl.get("name") or d.get("action") or d.get("id"))[:48])
        awaiting_s = ("; ".join(esc_titles) + ("…" if n_esc > 6 else "")) if esc_titles else "(nothing)"
        all_graphs = self.list_graphs()                       # keep COMPACT: count + the current graph
        others = [x for x in all_graphs if x != nowv["graph"]]
        graphs_s = (f"{len(all_graphs)} total — current: {nowv['graph']}"
                    + (f"; others incl. {', '.join(others[:5])}" + ("…" if len(others) > 5 else "") if others else ""))
        panels_s = ", ".join(p.get("id", "?") for p in self.list_panels()) or "(none)"
        # the valid ui:// show-targets, from the UI_REGISTRY (single-source). MUST mirror
        # _describe_ui_address's served-form logic (S1's TWO key conventions): the corpus ELEMENT rows are
        # ALREADY full-keyed (`ref="ui://inbox/build-review"`) → emit `ref` AS-IS; only the bare-keyed REGION
        # rows (`ref="inbox"`) get the `ui://{kind}/{ref}` served form (canvas-kind → `ui://canvas/*`). The
        # OLD builder applied the served form UNCONDITIONALLY, producing the malformed double-prefix
        # `ui://chrome/ui://inbox/build-review` (the exact bug _describe_ui_address's docstring warns against)
        # for every element row — fabricated, non-resolvable grounding the RHM was told were valid targets.
        # G-61-class drift: waves added ~60 full-keyed element rows to UI_REGISTRY but this builder was never
        # lifted past the bare-region vocabulary it was written for. De-malforming it also collapses the
        # repeated `ui://canvas/*` (dedupe, order-preserving) — together this dropped the line 2262→~1487
        # chars (the whole RHM-grounding budget overflow, len 4039>4000). One-source/never-fabricated (rule 8).
        _seen_targets: set[str] = set()
        _targets = []
        for row in self.UI_REGISTRY:
            ref, kind = row[0], row[1]
            t = ref if ref.startswith("ui://") else ("ui://canvas/*" if kind == "canvas" else f"ui://{kind}/{ref}")
            if t not in _seen_targets:
                _seen_targets.add(t)
                _targets.append(t)
        show_targets_s = ", ".join(_targets) or "(none)"

        ctx = (
            "LIVE SYSTEM STATE (ground truth — answer only from this):\n"
            f"- graph: {nowv['graph']} · {nowv['nodes_total']} nodes, {nowv['nodes_resolved']} resolved"
            f", {len(self._last_run_stuck(nowv['graph']))} stuck"
            f" · {nowv['surfaced_pending']} awaiting approval · presence: {nowv['presence']}\n"
            f"- nodes: {nodes}\n"
            f"- available node-types: {', '.join(self.list_types())}\n"
            f"- chat models: {chat_s}\n"
            f"- embed models: {embed_s}\n"
            f"- presence modes: {modes_s} (current: {mode})\n"
            f"- RHM verbs you can perform: {verbs_s}\n"
            # show-targets vocabulary (grounding for the `show` verb): enumerate the valid ui:// chrome
            # refs from the UI_REGISTRY (single-source) + note node-ids are valid targets, so the RHM
            # GROUNDS `show` in real handles instead of guessing. A bare handle resolves leniently.
            f"- show targets (ui:// regions): {show_targets_s}; plus any node-id above is a valid show target\n"
            f"- inbox: {n_esc} item(s) awaiting you — {awaiting_s}\n"
            f"- graphs (multigraph): {graphs_s}\n"
            f"- panels: {panels_s}\n"
            f"- recent activity: {evs}\n"
        )
        # I1 — the operator's focus is now a WIDENED vocabulary (seams-rhm Seam 4: widen the EXISTING
        # `focus` plug-in point, never a new mechanism). A `focus.selected` value is EITHER a canvas
        # node-id (the existing co-presence path — UNCHANGED) OR a `ui://` address (a clicked addressed
        # element — the new "indicating" path). We BRANCH on the value, additively:
        #   • s.startswith("ui://")  → resolve via the S1 UI registry → an INDICATING block (NEW)
        #   • elif s in by           → the canvas-node co-presence block (PRESERVED byte-for-byte)
        #   • else                   → a stale node-id: dropped, exactly as before (NOT fail-loud — a
        #                              vanished selection is normal; only an UNRESOLVED ui:// fails loud)
        # The ui:// check comes FIRST so a clicked address can never be silently swallowed by the
        # `s in by` node-id filter (rule 4). An unregistered ui:// is injected AS the address with an
        # "(unregistered)" marker — surfaced honestly, never dropped.
        raw_selected = (focus or {}).get("selected", [])
        indicated = [s for s in raw_selected if isinstance(s, str) and s.startswith("ui://")]
        # REVIEW WORKSPACE (the mockup-studio organ): a `mockup://<file>` value rides in the SAME
        # `focus.selected` list as a ui:// address (the WIDENED focus vocabulary, seams-rhm Seam 4 — never a
        # new mechanism). It means "the operator is REVIEWING this mockup; its content IS ground truth for
        # this turn". The mockups are static developer-authored HTML the operator (Tim) does NOT read — the
        # right-hand-man reads it FOR him and explains at his altitude. So the mockup's actual content must be
        # in the LIVE-STATE block (the grounding rule REFUSES to answer about anything not in that block — a
        # filename alone would correctly draw "I can't see that"). Path-safe (bare <file>.html basename only,
        # realpath-contained) so a junk value can never read outside design/mockups/ (mirrors the bridge's
        # _safe_mockup_path). Checked BEFORE the node-id filter so it's never swallowed as a (non-existent) node.
        mockups = [s for s in raw_selected if isinstance(s, str) and s.startswith("mockup://")]
        selected = [s for s in raw_selected if s not in indicated and s not in mockups and s in by]
        if mockups:
            import re as _re
            for mk in mockups:
                name = mk[len("mockup://"):]
                if not _re.fullmatch(r"[A-Za-z0-9._-]+\.html", name):
                    ctx += (f"\nMOCKUP UNDER REVIEW: {name!r} — (refused: not a bare <file>.html name; "
                            f"cannot read it)\n")
                    continue
                _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # repo root (single-source w/ codebase node)
                fp = os.path.realpath(os.path.join(_root, "design", "mockups", name))
                mroot = os.path.realpath(os.path.join(_root, "design", "mockups"))
                if os.path.commonpath([fp, mroot]) != mroot or not os.path.isfile(fp):
                    ctx += (f"\nMOCKUP UNDER REVIEW: {name!r} — (cannot see it: no such mockup file)\n")
                    continue
                with open(fp, "r", encoding="utf-8", errors="replace") as _f:
                    html = _f.read()
                # Inject the RAW content (advisor: don't pre-build an extraction pipeline — the model reading
                # raw HTML may be fine; only add cleaning IF a real test comes back truncated/junk). Cap the
                # bytes so one large mockup can't blow the window; the cap is generous and fail-loud-legible
                # (the model is TOLD it was truncated, never silently fed a partial as if whole — rule 4).
                CAP = 14000
                body = html if len(html) <= CAP else (html[:CAP] + f"\n…[truncated — mockup is {len(html)} chars, "
                                                                   f"showing first {CAP}]")
                ctx += ("\nMOCKUP UNDER REVIEW (the operator is looking at this design mockup RIGHT NOW; it is "
                        "a static HTML design artifact, NOT the live running app. The operator does not read "
                        "code — read this FOR them and explain, at a plain-language altitude, what this screen "
                        "IS, what they are looking at, and what they could do here. When they ask 'what am I "
                        "looking at', ground your answer in THIS content):\n"
                        f"  file: {name}\n  ---\n{body}\n  ---\n")
        if indicated:
            ilines = []
            for addr in indicated:
                ilines.append("  · " + self._describe_ui_address(addr))
            ctx += ("\nOPERATOR IS INDICATING (they clicked these addressed UI element(s) RIGHT NOW — "
                    "this is the locus their message is about; answer with respect to the indicated "
                    "thing):\n" + "\n".join(ilines) + "\n")
            # R1 — SET the backend-held current `ui://` locus from the indicated address. This is the
            # spec's named set-point (old suite.py:855): reuse I1's exact `startswith("ui://")`
            # extraction above (`indicated`), never a parallel mechanism (rule 3, one-source). It runs
            # AFTER the describe loop on purpose — _describe_ui_address calls parse_ui_address (the S0
            # grammar gate), so a MALFORMED `ui://` RAISES before this line and we NEVER remember an
            # unvalidated locus (fail-loud, consistent with I1). Most-recent wins on a multi-select
            # (indicated[-1] = last-wins). The write is guarded by `if indicated:` so a turn carrying
            # ONLY a canvas node-id (or no focus) leaves the prior locus INTACT (no clobber) — the
            # locus PERSISTS ALONGSIDE the per-request co-presence path, never replacing it.
            self._current_locus = indicated[-1]
        if selected:
            lines = []
            for nid in selected:
                n = by[nid]
                out = n.get("output")
                detail = (str(out)[:280] if out is not None else "(unresolved)")
                cfg = n.get("config") or {}
                lines.append(f"  · {nid} ({n['type']}, {n['status']}) — config={cfg} — output: {detail}")
            ctx += ("\nOPERATOR'S CURRENT FOCUS (co-presence — they have these selected on the canvas RIGHT "
                    "NOW; you may reference their full detail, including values):\n" + "\n".join(lines) + "\n")
        # R2 — address-keyed context resolution. AFTER every existing block (they stay byte-for-byte;
        # this only APPENDS). The retrieval key is now the ADDRESS THE OPERATOR IS AT — read via the
        # getter `current_locus()` (R1's read seam; R2 is its first PRODUCTION caller, the I7-left-it-
        # unwired precedent now closed) so info attached to the locus + its ancestors (I6 annotations,
        # I7 chats, addressed events) auto-resolves here, BOUNDED by the relevance/recency decay so it
        # cannot flood the window (the §21.10 tension R2 exists to kill). No locus / nothing attached →
        # _resolve_context_at returns '' and nothing is injected (the keyword consult path stays the
        # fallback). Fail-loud-LEGIBLE inside the helper (a warn + '' on error), never crash-the-turn.
        # X6 (Convergence) — pass `graph_id` (held here as ground truth) so the gather can BRIDGE a
        # `ui://canvas/<node>` locus to its `run://<graph_id>/<node>` counterpart (version-history L6 +
        # node events). The bridge is guarded (only a canvas-node in THIS graph maps); a non-canvas locus
        # or a node absent from graph_id skips the run:// step, leaving the ui:// resolution unchanged.
        # X13 (Convergence) — pass `intent` (the operator's current chat message) so the locus context is
        # SEMANTICALLY ranked (relevance to what they're asking), not just recency·proximity·pin. With no
        # intent the ranking is the pre-X13 ordering; a down embedder degrades the term to 0 with a warning.
        # E1 (mode-and-context-resolution-are-ONE-system) — resolve the LENS once here (mode-type × instance
        # sub-type, read live from the rhm_mode node), then thread the resulting DATA spec into R2 so the
        # active mode parameterizes WHAT/HOW context resolves. The mode is already in scope above (`mode`).
        # No mode-name reaches the R2 path — the shape is the spec dict (registry-is-truth).
        _res = self.resolution_spec_for(mode)
        ctx += self._resolve_context_at(self.current_locus(), graph_id=graph_id, intent=intent,
                                        resolution=_res)
        # GROUP J — the cognition↔resolution feedback loop: the PRIOR turns' swarm cognition (the system's
        # OWN thinking, the roles' run://<turn>/<role> outputs) resolves into THIS turn's context. A SECOND,
        # DEDICATED R2 call anchored at the FIXED `R2_COGNITION_ANCHOR` (a stable ui:// address, parses like
        # the per-turn ui://cognition/<turn> the staged path emits) — so it fires WITH OR WITHOUT a canvas
        # locus (the locus call above returns '' on a plain chat with no selection; this one does not depend
        # on it). It supplies the ONLY resolution spec that admits the 'cognition' stratum (the explicit
        # opt-in `_r2_gather` gates on) — every OTHER R2 caller's strata omits it, so the address-attached
        # reads (`context_at`/`surface_intent_at`) are byte-for-byte unchanged (no global-cognition leak).
        # The in-flight turn is excluded by construction (its `cognition.turn.done` fires later, in the
        # epilogue, AFTER this context is assembled — so only PRIOR completed turns resolve). Suppressed in
        # `off` mode (the presence dial off resolves nothing — consistent with the off lens admitting none).
        # REUSE: `_resolve_context_at` → `_r2_gather` → `_r2_score_and_cap` (the same scorer/cap), the run
        # INDEX (#54, E2-incremental), and `resolve_address` (the canonical resolver). No second system.
        if mode != "off":
            _cog_res = {"strata": frozenset({"cognition"}), "howto_detail": "none",
                        "framing": ("YOUR OWN PRIOR THINKING (the swarm of roles you ran on RECENT turns "
                                    "produced this — your cognition fed back as context; treat it as what "
                                    "you were already reasoning, and build on it, don't repeat it)")}
            ctx += self._resolve_context_at(self.R2_COGNITION_ANCHOR, graph_id=None, intent=intent,
                                            resolution=_cog_res)
        return ctx

    def _describe_ui_address(self, address: str) -> str:
        """I1 — resolve a clicked `ui://` address → a human-meaningful description for the RHM context,
        from the S1 UI registry (UI_REGISTRY, served as /api/ui_info → build_ui_info). ONE-SOURCE
        (rule 3/8): the description comes from the registry row's own `title`, never invented.

        The registry carries TWO key conventions (both legitimate, S1):
          • the 9 hand-authored REGION rows are bare-keyed (`ref="inbox"`, kind="chrome") and are SERVED
            as the full address `ui://chrome/inbox` (canvas-kind serves as `ui://canvas/*`);
          • the corpus ELEMENT rows are full-string-keyed (`ref="ui://inbox/build-review"`).
        So we match an incoming full address against EITHER form (a region row's served form OR an
        element row's full key) — never the naive `ui://{kind}/{ref}` builder (it produces the malformed
        `ui://chrome/ui://inbox/build-review` for element rows; that builder is for the bare-region
        show-targets vocabulary only).

        FAIL LOUD (rule 4 — HARD CONSTRAINT): a malformed address raises (S0 grammar gate); a well-formed
        but UNREGISTERED address returns the address tagged "(unregistered)" — surfaced in the context,
        NEVER silently dropped, so the RHM (and the operator) sees the gap honestly."""
        from contracts.ui_info import parse_ui_address
        parse_ui_address(address)                              # S0 grammar gate — raises on malformed
        for row in self.UI_REGISTRY:
            ref, kind, title = row[0], row[1], row[2]
            served = "ui://canvas/*" if kind == "canvas" else f"ui://{kind}/{ref}"
            if ref == address or served == address:           # element full-key OR region served-form
                # Build the human description from the registry row (ONE-SOURCE): the `title` for the
                # hand-authored region rows ("Inbox", "Toolbar"); the corpus `represents` (the feature-id,
                # e.g. "RUN-run") for the element rows whose title falls back to the address. The address
                # is always shown so the locus is exact.
                extras = row[5] if len(row) > 5 else {}
                represents = (extras or {}).get("represents")
                if title and title != address:                # region rows carry a real human title
                    return f"{title} ({address})"
                if represents:                                # element rows carry the feature-id
                    return f"{address} — represents {represents}"
                return address                                 # registered, no extra descriptor available
        return f"{address} (unregistered)"                    # fail-loud-legible: gap surfaced, not dropped

    def address_help(self, ui_addr: str) -> dict:
        """D1 — the COMPOSED affordance resolver: join the THREE legs of "what can I do here?" at one
        `ui://` address into ONE bundle, REUSING the existing resolvers (no parallel system, rule 3):

          • what_this_is   — the WHAT (`_describe_ui_address`): the registry row's human title /
                             `represents` feature-id (one-source, never invented).
          • how_to_change  — the HOW-TO-CHANGE (`resolve_scope` → `blast_radius`): the `code://` scope this
                             address powers + the BLAST RADIUS a change here would reach (co-reference /
                             structural dependents+dependencies / semantic neighbours). This is the
                             "if you change this, here's what it touches" leg — the same X1/X2/X14 join the
                             consent/mint path uses.
          • how_to_use     — the HOW-TO-USE (`_registry_howto_for`): the authored affordance/how-to text
                             (the NEW D1 `howto` field). None when the address authors no help.

        DEGRADE-CLEAN IF A LEG IS ABSENT (rule 4, fail-loud-LEGIBLE, never crash): each leg is resolved in
        its own guard. `resolve_scope`/`blast_radius` ALREADY return graceful-empty + a `note` for an
        address with no code symbol / a stale corpus join (they do not raise on absence — only a malformed
        address raises the S0 gate). The how-to-use leg is None when unauthored. So a bare/region address
        with no code and no howto returns a bundle with what_this_is populated and the other two legs
        honestly empty (each carrying its own note / None) — a clean partial, never a half-crash. A
        MALFORMED address propagates the S0 grammar raise (fail loud — an unparseable locus is a real
        error, not a missing leg).

        Returns {address, what_this_is, how_to_change:{scope, blast_radius, note}, how_to_use,
        legs_present:{...}} — `legs_present` makes the degrade explicit so a caller (or the D2 UI later)
        can see WHICH legs resolved without re-deriving it. GENERIC over any address (mode-parameterizable
        later, E1); no per-element branch (Tim's not-hardwired correction)."""
        from contracts.ui_info import parse_ui_address
        parse_ui_address(ui_addr)                              # S0 grammar gate — a malformed locus IS an error

        # LEG 1 — WHAT THIS IS (always resolvable for a well-formed address; '(unregistered)' if unknown).
        what_this_is = self._describe_ui_address(ui_addr)

        # LEG 2 — HOW TO CHANGE: scope (resolve_scope) + blast_radius. Both degrade graceful-empty (note),
        # never raise on absence. Guarded so even an unexpected internal failure becomes a legible note,
        # not a crash of the whole bundle (the leg is then honestly marked absent).
        how_to_change = {"scope": [], "blast_radius": None, "note": None}
        try:
            scoped = self.resolve_scope(ui_addr)               # {address, symbols, scope, stale, note}
            radius = self.blast_radius(ui_addr)                # {address, symbols, co_reference, …, note}
            how_to_change = {"scope": scoped.get("scope", []),
                             "blast_radius": radius,
                             "note": scoped.get("note") or radius.get("note")}
        except (ValueError, TypeError):
            raise                                              # malformed address already raised above; re-raise
        except Exception as e:                                 # any other internal failure → legible absent leg
            how_to_change = {"scope": [], "blast_radius": None,
                             "note": f"how-to-change leg unresolved ({type(e).__name__})"}

        # LEG 3 — HOW TO USE: the authored affordance text (None when unauthored — a clean absent leg).
        how_to_use = self._registry_howto_for(ui_addr)

        def _howto_change_has_content(htc: dict) -> bool:
            """The how-to-change leg has REAL content iff there is a code `scope` OR the blast_radius
            carries at least one edge (co_reference / structural dependents+dependencies / semantic
            neighbours). A well-formed no-code-symbol address yields an all-empty radius dict — that is an
            ABSENT change-leg (the operator can't change code that doesn't resolve), so we report it
            absent rather than reading the bare dict as 'present'."""
            if htc.get("scope"):
                return True
            br = htc.get("blast_radius")
            if not isinstance(br, dict):
                return False
            return bool(br.get("co_reference") or br.get("structural_dependents")
                        or br.get("structural_dependencies") or br.get("semantic_neighbours")
                        or br.get("symbols"))

        bundle = {
            "address": ui_addr,
            "what_this_is": what_this_is,
            "how_to_change": how_to_change,
            "how_to_use": how_to_use,
            "legs_present": {
                # what-this-is is "present" only when the address is REGISTERED (an '(unregistered)'
                # descriptor is the honest gap, not a resolved leg).
                "what_this_is": bool(what_this_is) and "(unregistered)" not in what_this_is,
                # how-to-change is "present" only when it resolved REAL content — a code `scope` OR a
                # blast_radius carrying at least one neighbour/dependent. blast_radius returns a dict for
                # ANY well-formed address (often all-empty for a no-code-symbol address), so testing
                # `is not None` would mark the leg present even when there is nothing to change. We check
                # for actual edges, so the D2 UI can detect a genuinely-empty change-leg (degrade signal).
                "how_to_change": _howto_change_has_content(how_to_change),
                # how-to-use is "present" only when the address authored a howto.
                "how_to_use": how_to_use is not None,
            },
        }
        # F1 LEARNING LOOP — the ADAPT step: CONSULT the learned presentation pref at this address and
        # APPLY it (model-free) so address_help (and up_translate('address'), which composes it) REFLECTS
        # how Tim has shaped this. No pref → the bundle is returned byte-for-byte (the clean default — no
        # error, no fabrication; every existing address_help caller + acceptance is preserved). A stored
        # junk pref RAISES (fail loud) via the consult-read's re-validation.
        return self._apply_presentation_pref(bundle, self.presentation_pref_at(ui_addr))

    def _resolve_named_target(self, target: str | None) -> dict | None:
        """Resolve a MODEL-SUPPLIED change target → a confident ui:// address, or an ASK. Returns None
        when no target was supplied at all (so the caller falls back to the indicated locus). REUSES the
        existing address machinery (parse_ui_address + _describe_ui_address + the UI_REGISTRY) — this is
        a CUSTOM confident-single-match-else-ASK resolver (there is no existing name→address resolver to
        reuse: `show`'s handle_map is handle→address, not name→address), deliberately conservative:
          • a ui:// address → accepted iff grammar-valid AND REGISTERED (an unregistered/malformed ui://
            is NOT silently accepted — it would mint a DENY-ALL or raise — it returns an ASK).
          • a plain name ("the run button") → token-matched against the registry's OWN titles/refs
            (registry-truth, never a fabricated address). CONFIDENT iff exactly ONE registry row matches;
            ZERO or AMBIGUOUS (>1) → ASK, never pick one (rule 8 — a wrong scope = a wrong build).
        Returns {address, source:'named'} on a confident match, {address:None, source:'ask', ask, candidates}
        on an unconfident one, or None when target is empty."""
        from contracts.ui_info import parse_ui_address
        t = (target or "").strip()
        if not t:
            return None                                        # no target supplied → caller uses the locus
        if t.startswith("ui://"):
            try:
                parse_ui_address(t)
                if "(unregistered)" not in self._describe_ui_address(t):
                    return {"address": t, "source": "named", "ask": None, "candidates": []}
            except Exception:
                pass                                           # malformed/unregistered ui:// → ASK below
            return {"address": None, "source": "ask", "candidates": [],
                    "ask": (f"I can't confidently resolve {t!r} to a known UI element. Point at the "
                            f"element (click it) or name one of the registered elements so I scope the "
                            f"change correctly — I won't guess a scope.")}
        # plain name → token-match against the registry's OWN titles + refs. Tokenise both sides; a row
        # matches when every salient query token is a substring of the row's title-or-ref token bag.
        import re
        stop = {"the", "a", "an", "this", "that", "button", "panel", "field", "area", "element",
                "section", "view", "to", "in", "on", "of", "for"}
        q_tokens = [w for w in re.findall(r"[a-z0-9]+", t.lower()) if w not in stop and len(w) >= 2]
        matches = []                                           # (served_address, label)
        if q_tokens:
            for row in self.UI_REGISTRY:
                ref, kind, title = row[0], row[1], row[2]
                served = "ui://canvas/*" if kind == "canvas" else (
                    ref if str(ref).startswith("ui://") else f"ui://{kind}/{ref}")
                hay = (str(title or "") + " " + str(ref or "")).lower()
                hay_tokens = set(re.findall(r"[a-z0-9]+", hay))
                if all(any(qt in ht for ht in hay_tokens) or qt in hay for qt in q_tokens):
                    matches.append((served, str(title or ref)))
        seen, uniq = set(), []                                 # de-dup by address (a region may surface once)
        for addr, label in matches:
            if addr not in seen:
                seen.add(addr); uniq.append((addr, label))
        if len(uniq) == 1:
            return {"address": uniq[0][0], "source": "named", "ask": None, "candidates": []}
        if len(uniq) > 1:                                      # AMBIGUOUS → ASK, never pick one
            cand = [f"{label} ({addr})" for addr, label in uniq[:8]]
            return {"address": None, "source": "ask", "candidates": cand,
                    "ask": (f"{t!r} could mean more than one element: " + "; ".join(cand) +
                            ". Which one should I scope the change to? (Or click the element.)")}
        return {"address": None, "source": "ask", "candidates": [],   # zero matches → ASK
                "ask": (f"I couldn't match {t!r} to a known UI element. Click the element you mean, "
                        f"or name a registered one, so I scope the change correctly — I won't guess.")}

    def resolve_change_target(self, target: str | None, indicated: str | None = None) -> dict:
        """CONVO→SELF-BUILD BRIDGE — resolve WHICH ui:// element/scope a conversational change-request
        is about (rule 8 — never guess a scope; a wrong scope = a wrong/over-broad build). REUSES the
        EXISTING address machinery (UI_REGISTRY + parse_ui_address + _describe_ui_address) via the
        custom `_resolve_named_target` resolver above.

        PRECEDENCE (the correctness-critical order):
          1. EXPLICIT RESOLVABLE TARGET WINS. If the model supplied a `target` that resolves CONFIDENTLY
             (a registered ui:// OR an unambiguous named element), use it — even if an indicated locus is
             also present. Rationale: `indicated` is the backend-held `current_locus()`, which is the
             most-recent indication ACROSS THE SESSION (set `if indicated:` in _chat_context, never
             cleared — locus_acceptance proves a no-focus turn does NOT clobber it). It is therefore NOT
             reliably "this turn." A stale earlier click must NEVER silently override a target the operator
             named THIS turn (that is the exact wrong-scope failure the task warns against). An explicit,
             resolvable target is itself evidence the operator is not leaning on a click this turn.
          2. INDICATED LOCUS. Else, if the operator has a held ui:// locus (they pointed at an element)
             and it is grammar-valid + REGISTERED, use it — this is the "operator pointed and didn't
             restate the address" case (mirrors the wire-door using the pointed element).
          3. ASK. Else fail loud: return an ASK message and resolve NO address (no fiction, no guessed
             scope). If the model supplied a target that did NOT resolve confidently, the ASK carries
             that named-target failure reason (its candidate list / no-match), which is more useful than
             a generic prompt — but ONLY after step 2 declined (so a stale locus can't suppress a useful
             ASK either, and a present locus is preferred over an unresolvable named target).

        Returns {address, source:'named'|'indicated'|'ask', ask:str|None, candidates:[...]}.
        `address` is None exactly when `source=='ask'`."""
        from contracts.ui_info import parse_ui_address
        # 1. EXPLICIT RESOLVABLE TARGET WINS (never let a stale session locus override a named target).
        named = self._resolve_named_target(target)
        if named is not None and named["source"] == "named":
            return named
        # 2. INDICATED LOCUS — the operator pointed at an element; use it if registered + valid.
        if indicated and isinstance(indicated, str) and indicated.startswith("ui://"):
            try:
                parse_ui_address(indicated)                    # grammar gate (an indicated address should be valid)
                if "(unregistered)" not in self._describe_ui_address(indicated):
                    return {"address": indicated, "source": "indicated", "ask": None, "candidates": []}
            except Exception:
                pass                                           # a malformed held locus → fall through to ASK
        # 3. ASK — no resolvable target, no usable locus. Prefer the named-target failure reason (its
        #    candidate list is more useful than a generic prompt) when the model DID supply a target.
        if named is not None:                                  # named was supplied but unconfident → its ASK
            return named
        return {"address": None, "source": "ask", "candidates": [],   # no target + no usable locus → generic ASK
                "ask": ("Which UI element should this change apply to? Click the element (so I use that "
                        "exact locus) or name it — I won't guess a scope, because a wrong scope is a "
                        "wrong build.")}

    def current_locus(self) -> str | None:
        """R1 — READ the backend-held current `ui://` locus (the most-recent indicated address).

        This is the net-new backend notion of "where the operator IS" (seams-rhm Seam 4: there was
        none before — locus lived only FE-side, per-request). It is SET in the chat path when I1's
        widened `focus.selected` carries a `ui://` address (see _chat_context). Returns the address
        string, or None if the operator has not indicated a `ui://` element this session.

        EXPOSED for R2's address-keyed context resolution to consume (it will key retrieval by this
        locus). R2 is NOT built here — R1 makes the locus HELD + SETTABLE + READABLE only; this getter
        has no production caller yet (the I7-left-R2-unwired precedent), it is the read seam R2 hangs
        off."""
        return self._current_locus

    # ============================================================================================
    # R2 — address-keyed context resolution (the keystone of the RESOLUTION group)
    # ============================================================================================
    # IS (today): retrieval is KEYWORD-keyed — `_consult_terms` extracts salient terms,
    # `_retrieve_for_consult` scans the repo by term-hit count, bounded only by CONSULT_CAP=40000
    # (the consult context-flood is the RHM's worst wound — §21.4#3 / seams-rhm Seam 4).
    # SHOULD-BE: the ADDRESS the operator is AT (R1's `current_locus()`) becomes the retrieval key.
    # Info attached to the locus (I6 annotations + I7 chats + addressed events) — and its ancestors in
    # the address tree — auto-resolves into the RHM context at that locus. A relevance/recency DECAY
    # bounds it so it CANNOT flood the window (the §21.10 context-flood tension — without decay,
    # auto-resolve recreates the 396k-char stuffing R2 exists to KILL). The keyword scan REMAINS as a
    # fallback (no locus / no addressed match) — it is just no longer the PRIMARY key.
    #
    # The decay weights + the window budget are NAMED config constants (D2-configurable, never bare
    # literals — the guide's "name the weights: recency · proximity · pin"). X17 (Convergence): these
    # class constants are now the DEFAULT FLOOR — __init__ RESOLVES each from the env (COMPANY_R2_*) into
    # an INSTANCE attribute that shadows the class default, so the composition is retunable with NO code
    # change (a fresh Suite/restart re-reads). Unset env → the class default → behaviour byte-for-behaviour
    # unchanged. Exposed via capabilities().composition_config (registry-is-truth). See __init__ + _cfg_*.
    R2_LAMBDA = 1.0 / (3 * 24 * 3600)   # recency decay rate (per second). exp(-LAMBDA*Δt): the score
    #                                     halves at ~ln2/LAMBDA ≈ 2 days; an item ~3 days old decays to
    #                                     1/e. Tuned so "recent" wins inside a working session/few days
    #                                     while week-old chatter fades — without a pin it can still drop.
    R2_PROXIMITY_WEIGHT = 1.0           # coefficient on tree-distance in 1/(1+W*proximity). The bare
    #                                     pseudocode is 1/(1+proximity); W makes the proximity term's
    #                                     STRENGTH explicit + tunable (W>1 punishes distance harder).
    R2_PIN_WEIGHT = 1.0                 # additive bonus for an explicitly pinned item. ≥ the max
    #                                     recency*proximity term (1.0 at exact+now) so a PIN always
    #                                     outranks an unpinned item regardless of age/distance — pinning
    #                                     is the operator's explicit "keep this in view" override.
    R2_SEMANTIC_WEIGHT = 1.0            # X13 (Convergence) — coefficient on the SEMANTIC term:
    #                                     + R2_SEMANTIC_WEIGHT * cosine(intent, item) in _r2_score. R2 ranked
    #                                     attached context by recency·proximity·pin — by LOCATION + AGE, not
    #                                     by RELEVANCE to what the operator is actually ASKING. This term ranks
    #                                     the gathered context by relevance to the operator's intent (Tim's
    #                                     "gather by relevance"). Default 1.0 → it sits at parity with the
    #                                     recency·proximity term (max 1.0 at exact+now) and at parity with a
    #                                     pin: a perfectly-on-topic item (cosine→1) gets the same lift a pin
    #                                     does, so RELEVANCE is a first-class dimension beside the others.
    #                                     A NAMED config knob (D2/X17 will env-wire it — a sane default here,
    #                                     never a bare literal). DEGRADE-WITH-WARNING: when the embedder
    #                                     (:8001) is unreachable the term degrades to 0 + a loud warning and
    #                                     R2 falls back to the proven recency·proximity·pin ranking (the term
    #                                     is ADDED — set it to 0 and the pre-X13 ordering is byte-for-byte).
    R2_RUN_VERSIONS = 3                 # X6 (Convergence) — max run://-keyed L6 versions the bridge
    #                                     contributes per locus. The bridged versions score at proximity 0
    #                                     (same node as the ui:// locus) — so without a bound a freshly-run
    #                                     LLM/content node's 25 full-preview versions (~200 chars each ≈
    #                                     5000 > R2_BUDGET) would dominate the window by recency and EVICT
    #                                     the operator's ui:// comments/chats at the same locus. This caps
    #                                     the run:// contribution to the FEW most-recent versions (newest-
    #                                     first from ref_versions), so BOTH schemes coexist in the bounded
    #                                     window rather than one starving the other. A named config knob
    #                                     (D2/X17-configurable), not a bare literal; the per-turn R2_BUDGET
    #                                     cap still applies on top.
    R2_BUDGET = 4000                    # max chars of resolved addressed context injected into the RHM
    #                                     window (~1k tokens). attention = BUDGET; the cap is ENFORCED —
    #                                     never stuffed. Far below CONSULT_CAP: this is the always-on
    #                                     locus slice that rides EVERY turn, not a one-shot consult read.
    R2_HOWTO_MAX = 2000                 # D1 — max CHARS of the how-to/affordance stratum that may enter the
    #                                     gather per locus (the FLOOD GUARD, mirroring R2_RUN_VERSIONS). The
    #                                     howto stratum is PIN-PERSISTENT (pinned=True + ts=now each gather →
    #                                     recency never decays), so it scores at or above the operator's own
    #                                     comments and, unbounded, a long help text could EVICT them from the
    #                                     bounded window (the same starvation _r2_run_strata caps against). So
    #                                     a howto longer than this is TRUNCATED-with-marker at the data seam
    #                                     (legible, not silent) BEFORE scoring; the per-turn R2_BUDGET cap
    #                                     still applies on top. A named knob (D2/X17 will env-wire it), not a
    #                                     bare literal — the affordance grounds, it never floods.
    R2_HOWTO_TERSE = 240                # E1 — the per-howto cap a mode-type's `howto_detail='terse'` lens
    #                                     applies (a one-liner affordance for low-noise modes — background /
    #                                     watch-and-react — that still want the help leg but not a paragraph).
    #                                     A named knob (env-wired below), not a bare literal; ≤ R2_HOWTO_MAX.
    R2_COGNITION_TURNS = 2              # GROUP J (the cognition↔resolution loop) — how many PRIOR COMPLETED
    #                                     turns' cognition (the swarm's run://<turn>/<role> outputs) feed the
    #                                     NEXT turn's R2 resolution (the system's OWN thinking becomes its
    #                                     context). Bounded like R2_RUN_VERSIONS: the cognition items score at
    #                                     the cognition anchor (proximity 0), so without a bound many prior
    #                                     turns × many roles would flood the window. A few most-recent turns is
    #                                     the working-memory horizon (the per-turn R2_BUDGET cap still applies).
    R2_COGNITION_PER_ROLE = 360        # GROUP J — max CHARS of ONE role's cognition output admitted into the
    #                                     gather (a role's structured JSON can be long; this keeps each
    #                                     contribution a legible snippet so no single role evicts the others —
    #                                     truncated-with-marker at the data seam, never silent). A named knob,
    #                                     not a bare literal; the R2_BUDGET cap bounds the whole stratum on top.

    @staticmethod
    def address_tree_distance(a: str, b: str) -> int:
        """Tree-distance between two `ui://` addresses — closer in the address tree = smaller.
        Strip the `ui://` scheme, split the remainder on `/`, take the common-prefix length, then
        distance = (len(a)-common) + (len(b)-common). Exact match → 0; parent/child → 1; sibling → 2.
        A non-`ui://` or empty operand degrades to its raw segments (no crash — distance is still a
        well-defined non-negative int). Pure + deterministic (proven directly in the R2 test)."""
        def segs(x: str) -> list:
            x = x or ""
            if x.startswith("ui://"):
                x = x[len("ui://"):]
            return [s for s in x.split("/") if s != ""]
        sa, sb = segs(a), segs(b)
        common = 0
        for x, y in zip(sa, sb):
            if x == y:
                common += 1
            else:
                break
        return (len(sa) - common) + (len(sb) - common)

    def _r2_score(self, item: dict, locus: str, now, semantic: float = 0.0) -> float:
        """Score ONE gathered item by the relevance/recency decay (the guide pseudocode):
            recency   = exp(-R2_LAMBDA * (now - ts))                 # newer = heavier
            proximity = address_tree_distance(locus, item.address)   # closer in the tree = heavier
            pin_bonus = R2_PIN_WEIGHT if item.pinned else 0.0
            score     = recency * (1/(1 + R2_PROXIMITY_WEIGHT*proximity)) + pin_bonus
                        + R2_SEMANTIC_WEIGHT * semantic                 # X13 — RELEVANCE to the intent
        `now` is a tz-aware datetime (injected for deterministic tests); `ts` is the store's
        ISO-8601 UTC string (`datetime.now(timezone.utc).isoformat()` → `+00:00`, fromisoformat-safe).
        A missing/unparseable ts → recency 0 (treated as infinitely old, never a crash).

        X13 (Convergence) — the SEMANTIC term. `semantic` is the PRECOMPUTED cosine(intent_vec, item_vec)
        in [-1, 1], supplied by `_r2_score_and_cap` (which embeds the operator's intent + each item's text
        ONCE per turn — never per `_r2_score` call, so the sort stays cheap and the embed cost is O(items),
        not O(items·log items)). KEEPING the cosine OUT of `_r2_score` is what keeps this method
        per-turn-safe + crash-free: it does NO I/O, exactly as before; an embedder failure is handled at
        the score+cap layer (degrade-to-0-with-warning), never here.
        BACKWARD-COMPATIBLE: `semantic` defaults to 0.0, so the pre-X13 3-arg call
        `_r2_score(item, locus, now)` is byte-for-byte the old recency·proximity·pin score — this is what
        preserves addr_context_acceptance (every existing call passes no `semantic`)."""
        import math
        from datetime import datetime
        ts_raw = item.get("ts")
        try:
            ts = datetime.fromisoformat(ts_raw)
            delta = (now - ts).total_seconds()
            recency = math.exp(-self.R2_LAMBDA * max(0.0, delta))
        except Exception:
            recency = 0.0
        proximity = self.address_tree_distance(locus, item.get("address", ""))
        pin_bonus = self.R2_PIN_WEIGHT if item.get("pinned") else 0.0
        return (recency * (1.0 / (1.0 + self.R2_PROXIMITY_WEIGHT * proximity)) + pin_bonus
                + self.R2_SEMANTIC_WEIGHT * semantic)

    def _r2_ancestors(self, locus: str) -> list:
        """The locus address + each ANCESTOR up the `ui://` tree (so proximity is a LIVE dimension,
        not a dead term — a locus-exact item outranks a parent-address item end-to-end; faithful to
        the guide's "addresses/types/screens"). Each candidate is validated against the S0 grammar
        (`parse_ui_address`); an ancestor that doesn't parse is SKIPPED (never a crash, never a junk
        key). Walks up to the region root (the first segment after the scheme), inclusive of locus."""
        from contracts.ui_info import parse_ui_address
        out, seen = [], set()
        if not (isinstance(locus, str) and locus.startswith("ui://")):
            return out
        rest = locus[len("ui://"):]
        parts = [p for p in rest.split("/") if p != ""]
        # locus first (exact), then each shorter prefix down to the region root (1 segment).
        for n in range(len(parts), 0, -1):
            cand = "ui://" + "/".join(parts[:n])
            if cand in seen:
                continue
            try:
                parse_ui_address(cand)                # S0 grammar gate — skip anything malformed
            except Exception:
                continue
            seen.add(cand); out.append(cand)
        return out

    def _r2_events_at(self, address: str) -> list:
        """Addressed EVENTS at `address` — the 3rd gather source (I6 annotations + I7 chats +
        addressed events, per the guide). Events ride the open `append_event` record with an additive
        `address` field (annotate/attach_chat already emit them; suite.py:1773/1816). Filter the
        shared events.jsonl by that field; newest-first. Reads disk every call (no in-memory cache),
        so a reload sees prior writes. NOTE these partly RE-NARRATE the annotations/chats already
        gathered (they are the S2 visibility echoes) — included because the guide names them; they are
        narration, not new substance, and the budget cap absorbs the overlap."""
        out = []
        for e in self.store.recent_events(500):
            if e.get("address") == address:
                out.append({"kind": "event", "address": address, "ts": e.get("ts"),
                            "text": f"[event] {e.get('kind', '')}: {e.get('summary', '')}",
                            "pinned": False})
        return out

    def _registry_howto_for(self, address: str) -> str | None:
        """D1 — read the authored HOW-TO / affordance text for `address` from the live UI_REGISTRY,
        GENERICALLY (rule 8 — from the registry, never invented; mode-parameterizable later, NEVER a
        per-element branch — Tim's not-hardwired correction). The howto rides the registry row's
        union-extras (row[5]['howto'], plumbed from the corpus `howto` field via
        UnionAddressRecord.from_corpus → _load_corpus_element_addresses), so this resolves it with the
        SAME two-key matching `_describe_ui_address` uses (the bare-region served-form OR the corpus
        element full-key) — one source, one match rule.

        Returns the howto string, or None when the address is unregistered OR registered-without-howto
        (both honest absences — the caller treats a None as 'no how-to-use leg' and degrades cleanly).
        FAIL-LOUD (rule 4): a malformed address raises (S0 grammar gate) — never a silent empty parse."""
        from contracts.ui_info import parse_ui_address
        parse_ui_address(address)                              # S0 grammar gate — raises on malformed
        for row in self.UI_REGISTRY:
            ref, kind = row[0], row[1]
            served = "ui://canvas/*" if kind == "canvas" else f"ui://{kind}/{ref}"
            if ref == address or served == address:
                extras = row[5] if len(row) > 5 else {}
                howto = (extras or {}).get("howto")
                return howto if (howto and str(howto).strip()) else None
        return None

    def _r2_howto_at(self, address: str, now=None, detail: str = "full") -> list:
        """D1 — the HOW-TO / AFFORDANCE stratum at `address`: the FOUNDATIONAL layer that resolves the
        what-this-is / what-you-can-do / how-to-change-it help INTO the locus context, as a NEW R2 gather
        source mirroring `_r2_events_at`. It is the data half of the foundational affordance stratum (the
        composed three-leg join lives in `address_help`).

        PIN-PERSISTENT (the keystone of this stratum — no recency decay): unlike a comment/chat/event whose
        relevance fades, an address's how-to text is ALWAYS true at that address, so it must not decay out
        of the window over a long session. Achieved WITHOUT touching `_r2_score` (which would risk the
        addr_context_acceptance byte-for-byte assertion): the item is emitted with `pinned=True` (the
        R2_PIN_WEIGHT bonus, the same mechanism a pinned comment uses) AND `ts=now` re-stamped EVERY gather
        (recency = exp(-LAMBDA·0) = 1 — the maximum, never decaying). So the howto holds its rank turn over
        turn through the EXISTING scorer — a pure-data persistence, not a scorer special-case.

        FLOOD-PROOF (mirrors `_r2_run_strata`'s R2_RUN_VERSIONS bound): because it is pin-persistent it
        scores at/above the operator's own locus comments; an unbounded long help text could EVICT them
        from the R2_BUDGET window (the same starvation the run:// versions cap guards against). So the text
        is TRUNCATED-with-marker at R2_HOWTO_MAX here (legible, never silent), BEFORE it reaches the
        score+cap; the per-turn R2_BUDGET cap still applies on top.

        MODE-PARAMETERIZABLE, NOT HARDWIRED (Tim's correction): the resolution is generic over ANY address
        via `_registry_howto_for` (one match rule, registry-is-truth) — there is NO per-element branch and
        NO help text embedded in code. E1 (NOW WIRED): the `detail` arg (the mode-type's `howto_detail`
        declaration, threaded from `resolution_spec_for` via `_r2_gather`) parameterizes WHAT/HOW the
        how-to resolves — the seam this docstring advertised is now closed:
          • 'full'  — today's behaviour byte-for-byte (truncate only at R2_HOWTO_MAX).
          • 'terse' — a tighter per-howto cap (R2_HOWTO_TERSE) so a low-noise mode (background/watch)
                      still GETS the affordance but as a one-liner, not a paragraph.
          • 'none'  — SUPPRESS the leg entirely (focus/off — deep work / asleep: no how-to flood).
        `detail` is DATA from the spec (a string compare on a declared value), NOT a mode-name branch.

        Returns a list of 0-or-1 R2 items in the common gather shape `{kind, address, ts, text, pinned}`.
        `kind='howto'` (NOT 'event' — so `_r2_dedup`'s pass-2 echo logic never mangles it) and NO `_raw`
        key (so dedup pass-1 keeps it unconditionally — it is never a comment double-count). Empty list
        when the address has no authored howto (clean degrade) OR when `detail=='none'` (the lens suppresses it)."""
        from datetime import datetime, timezone
        if now is None:
            now = datetime.now(timezone.utc)
        if detail == "none":                                  # E1: the lens suppresses the how-to leg entirely
            return []
        howto = self._registry_howto_for(address)             # generic registry read (raises on malformed addr)
        if not howto:
            return []
        text = str(howto)
        cap = self.R2_HOWTO_TERSE if detail == "terse" else self.R2_HOWTO_MAX   # E1: the lens' per-howto cap
        if len(text) > cap:                                   # FLOOD GUARD — truncate-with-marker (legible)
            text = text[: cap] + " …[howto truncated]"
        return [{"kind": "howto", "address": address,
                 "ts": now.isoformat(),                        # PIN-PERSISTENT: re-stamped now → recency = 1
                 "text": f"[how-to @ {address}] {text}",
                 "pinned": True}]                              # PIN-PERSISTENT: the R2_PIN_WEIGHT bonus

    def _r2_pref_at(self, address: str, now=None) -> list:
        """F1 LEARNING LOOP — the PRESENTATION-PREFERENCE stratum at `address`: the learned "how Tim wants
        <this> presented" resolved INTO the locus context as a NEW R2 gather source, MIRRORING `_r2_howto_at`
        (the affordance stratum it is a sibling of — both are pin-persistent address-truth that must not
        decay out of the bounded window).

        PIN-PERSISTENT (the keystone): a learned pref is ALWAYS true at its address until Tim re-shapes it,
        so it must not decay like a comment. Achieved WITHOUT touching `_r2_score` (same as `_r2_howto_at`):
        emitted `pinned=True` (the R2_PIN_WEIGHT bonus) AND `ts=now` re-stamped EVERY gather (recency =
        exp(-LAMBDA·0) = 1 — the max, never decaying). So the pref holds its rank turn-over-turn through the
        EXISTING scorer — pure-data persistence, not a scorer special-case.

        LATEST-WINS: reads the ACTIVE pref via `presentation_pref_at` (the same consult the adapt step uses,
        one-source) — the most-recent shaping, so the context reflects Tim's CURRENT preference, not the
        whole pref history. None / no pref → empty list (clean degrade — the RHM just gets the default
        framing context). NO `_raw` key (so `_r2_dedup` keeps it unconditionally — it is never a comment
        double-count). `kind='presentation_pref'` (distinct from 'annotation' so the comment-skip in
        `_r2_gather` + the dedup echo logic never touch it). Generic over any address (registry-is-truth) —
        the SAME 'read context at address → structured signal' shape a future mode auto-detect detector
        reuses (the sibling seam, left clean)."""
        from datetime import datetime, timezone
        if now is None:
            now = datetime.now(timezone.utc)
        # AMBIENT-GATHER POSTURE (mirrors `_r2_run_strata`, NOT the explicit-consult posture): this runs on
        # EVERY chat turn via `_r2_gather`. `presentation_pref_at` RAISES on a stored junk pref (the F6
        # explicit-consult fail-loud) — but a single junk pref at the locus/an ancestor must NOT collapse
        # the WHOLE locus gather to '' (the silent-degrade `_resolve_context_at`'s catch-all would cause).
        # So here we CATCH it, WARN loudly (address-stamped — fail-loud-LEGIBLE), and SKIP this one stratum,
        # never crashing/nuking the per-turn slice. The EXPLICIT up-translate consult (address_help/coa/
        # up_translate) keeps raising — an operator asking to up-translate THAT address wants it loud.
        try:
            pref = self.presentation_pref_at(address)         # latest-wins; raises on a stored junk pref
        except Exception as e:
            self._emit("warning",
                       f"F1 learning loop: malformed stored presentation pref at {address} "
                       f"({type(e).__name__}) — skipped (the pref leg degraded; other context unaffected)",
                       address=address)
            return []
        if not pref:
            return []
        directive = self.PRESENTATION_PREFS[pref["kind"]].format(arg=pref.get("arg"))
        return [{"kind": "presentation_pref", "address": address,
                 "ts": now.isoformat(),                        # PIN-PERSISTENT: re-stamped now → recency = 1
                 "text": f"[presentation pref @ {address}] {directive}",
                 "pinned": True}]                              # PIN-PERSISTENT: the R2_PIN_WEIGHT bonus

    def _r2_run_counterpart(self, locus: str, graph_id: str | None) -> str | None:
        """X6 (Convergence) — the ui://↔run:// BRIDGE: map a `ui://canvas/<node>` locus to its
        `run://<graph_id>/<node>` counterpart, the address where the SAME node's output-versions (L6,
        `set_ref`) and node-instance events accrue. Returns the run:// address, or None when the bridge
        does NOT apply (so the caller cleanly skips the run:// step and the ui:// path is unchanged).

        THE SPLIT THIS CLOSES (suite.py:1136): `_r2_ancestors` returns [] for any non-`ui://` locus, so
        run://-keyed memory can never inherit. But the operator's live locus is ALWAYS ui:// (R1's
        `current_locus()` holds a ui:// only; `ingest_comment`/`annotate` RAISE on run://). A canvas node
        carries TWO addresses for the SAME thing — `ui://canvas/<node>` (the UI target) and
        `run://<graph>/<node>` (where the scheduler writes versions/events). So the bridge fires from the
        ui:// locus and resolves the run:// counterpart (approach (b)); it never walks a run:// locus
        (which nothing reaches in production → would be dead code).

        WHY graph_id IS THREADED (not held / not enumerated): the Suite holds NO current graph (every
        verb takes graph_id as a param) and node-ids are NOT globally unique (`u`/`llm-1` recur across
        graphs). The production caller (`_chat_context(graph_id, …)`) HOLDS graph_id as ground truth, so
        it is THREADED in. With no graph_id we CANNOT recover the graph without enumerating (ambiguous,
        fabrication) → we return None (the ui:// path stays byte-for-byte).

        NODE-MEMBERSHIP GUARD (rule 4, no silent wrong value): `current_locus()` can hold a STALE locus
        from a prior turn on a DIFFERENT graph; mapping a same-id node into the current graph could pull
        the WRONG node's history. So we only bridge when the node ACTUALLY EXISTS in graph_id; otherwise
        None (skip — never a silent wrong-node trail). Fail-loud-legible: a malformed locus is SKIPPED
        (the ui:// gather already validated/ignored it), never a crash."""
        from contracts.ui_info import parse_ui_address
        if not graph_id or not isinstance(locus, str) or not locus.startswith("ui://"):
            return None
        try:
            segs = parse_ui_address(locus)["segments"]    # S0 grammar gate (ignored on raise → no bridge)
        except Exception:
            return None
        # the canvas-node form is `ui://canvas/<node>` — region 'canvas', the node id its 2nd segment.
        if len(segs) < 2 or segs[0] != "canvas":
            return None
        node_id = segs[1]
        # MEMBERSHIP: the node must exist in graph_id (else a same-id node in another graph could be
        # silently mapped). Reuse the loaded graph (no new substrate) — never enumerate other graphs.
        try:
            g = self._load(graph_id)
            if not any(n.id == node_id for n in g.nodes):
                return None
        except Exception:
            return None
        return f"run://{graph_id}/{node_id}"

    def _r2_run_strata(self, run_addr: str, ui_locus: str) -> list:
        """X6 — gather the run://-keyed strata at `run_addr`, NORMALISED into the R2 item shape so the
        existing decay/cap/dedup score them uniformly with the ui:// items. Two strata, REUSING the
        EXISTING retrievals (no new store):
          • L6 version-history — `ref_versions(run_addr)` (the temporal trail of the node's output).
          • node-instance events — `_r2_events_at(run_addr)` (the SAME addressed-event reader the ui://
            path uses; it matches by exact address, so it works for run:// unchanged).

        CROSS-SCHEME PROXIMITY (the load-bearing decision): a run:// address shares NO prefix with the
        ui:// locus under `address_tree_distance` → it would score maximally-FAR and almost always lose
        the R2_BUDGET cap (a present-but-inert bridge). But these strata ARE the SAME node as the ui://
        locus — so each item's SCORING `address` is set to `ui_locus` (proximity 0 — the honest
        cross-scheme distance: same node), while the `text` LABELS it [version]/run-event so it stays
        legible. The scoring formula itself is UNCHANGED.

        FAIL-LOUD-LEGIBLE (rule 4): a malformed/unresolvable run:// address makes `ref_versions` RAISE —
        we WARN (address-stamped) and SKIP this stratum, never crash the per-turn gather (losing the
        whole locus slice over one bad sub-read is the worse failure). The events stratum is independent
        (its own try) so one failure never poisons the other."""
        items = []
        try:
            # BOUND the run:// version contribution (R2_RUN_VERSIONS, newest-first): without it a
            # freshly-run node's 25 full-preview versions all score at proximity 0 (same node as the
            # locus) and, being recent, dominate the budget — EVICTING the operator's ui:// comments at
            # the same locus. Capping here keeps BOTH schemes in the bounded window (the per-turn
            # R2_BUDGET cap still applies on top). ref_versions returns newest-first, so `limit` keeps
            # the most recent.
            rv = self.ref_versions(run_addr, limit=self.R2_RUN_VERSIONS)
            for v in rv.get("versions", []):
                marker = " (current)" if v.get("is_current") else ""
                items.append({"kind": "version", "address": ui_locus, "ts": v.get("ts"),
                              "text": f"[version of {run_addr}{marker}] {v.get('preview', '')}",
                              "_raw": (v.get("preview", "") or ""),   # X8 dedup identity (the version preview)
                              "pinned": False})
        except Exception as e:
            self._emit("warning",
                       f"X6 bridge: version-history unresolvable at {run_addr} ({type(e).__name__}) — skipped",
                       address=ui_locus)
        try:
            for ev in self._r2_events_at(run_addr):
                ev = dict(ev)
                ev["address"] = ui_locus       # cross-scheme proximity: the event is AT this node (dist 0)
                items.append(ev)
        except Exception as e:
            self._emit("warning",
                       f"X6 bridge: node-instance events unresolvable at {run_addr} ({type(e).__name__}) — skipped",
                       address=ui_locus)
        return items

    # GROUP J — the cognition anchor. A FIXED, stable ui:// address the cognition-resolution call hangs off,
    # so the system's own thinking resolves into the chat context EVEN WHEN there is no canvas locus (a plain
    # chat turn). It parses identically to the per-turn `ui://cognition/<turn>` the staged path already emits
    # (so it is a registered-shape address, not a fabricated one). The cognition items are scored AT this
    # anchor (X6's cross-scheme trick — uniform proximity 0 → recency+intent rank them), never at the canvas
    # locus (which would be the wrong frame: cognition is conversation-global, not address-attached).
    R2_COGNITION_ANCHOR = "ui://cognition/recent"

    def _r2_cognition_strata(self, now=None, intent: str | None = None) -> list:
        """GROUP J (the cognition↔resolution feedback loop — the system SEES ITS OWN THINKING) — gather the
        PRIOR COMPLETED turns' swarm cognition (the roles' `run://<turn>/<role>` outputs) as R2 items, so the
        NEXT turn's resolution reads back what the system itself just thought.

        The wire reuses the EXISTING seams (no parallel resolver, no second system — Group J's law):
          • COMPLETED turns are the `cognition.turn.done` events on the ONE event log (the staged path emits
            ONE per turn in its EPILOGUE, AFTER both parts). Reading those EXCLUDES the IN-FLIGHT turn by
            construction: `_chat_context` (this method's caller) runs DURING the current turn's part-core (at
            BOTH part-1 AND part-2), BEFORE that turn emits its own `turn.done` — so the current turn's
            cognition is NEVER resolved into its own context (which would conflate J1 with the intra-turn
            inject edge + double-count, even though the current turn's `role.ran` events have fired by part-2).
          • the roles + their `run://` addresses of each completed turn come from that turn's
            **`cognition.role.ran`** lifecycle events (each carries `turn_id`, `role`, `ok`, `address=
            run://<turn>/<role>`, emitted by `chat_parts` post-join). This is the SWARM's per-turn discovery
            surface — NOT the #54 run-index (`list_runs`/`find_runs`): the run-index deliberately does NOT
            cover the per-cast swarm (emitting one op.run per cast-role "would flood the index" — runtime/
            AGENTS.md #54). VERIFIED BY USE: a live staged turn fires 6 roles that resolve at run://<turn>/
            <role> yet `find_runs` returns 0 — so the run-index is the WRONG producer surface for swarm
            cognition; `cognition.role.ran` is the right one (same intent the criterion names, correct source).
            Only `ok=True` roles are read (a failed role's address may be unwritten/garbage).
          • each role output is read by `resolve_address` (the canonical scheme-dispatching resolver) — the
            SAME path the intra-turn inject + the outputs→inputs discovery use (the "no parallel resolver" law
            is untouched: role.ran is DISCOVERY, resolve_address is RESOLUTION).

        Bounded (R2_COGNITION_TURNS most-recent completed turns; R2_COGNITION_PER_ROLE chars per role) so the
        cognition stratum can't flood the R2 window (mirrors R2_RUN_VERSIONS / R2_HOWTO_MAX). Each item is
        normalised to the R2 item shape `{kind, address, ts, text, pinned}` with `address = the cognition
        ANCHOR` (X6 cross-scheme proximity — same conversation, distance 0) so the EXISTING decay/score/cap
        rank them uniformly with everything else; the SCORING formula is untouched.

        FAIL-LOUD-LEGIBLE (rule 4): a single unresolvable run:// address (a pruned ref) WARNs (address-
        stamped) and is SKIPPED — losing one role's snippet must never crash the per-turn gather. An empty
        history (no completed turns yet) is a clean empty list (no error, no fabrication)."""
        from datetime import datetime as _dt, timezone as _tz
        from runtime import cognition as _cog
        import json as _json
        if now is None:
            now = _dt.now(_tz.utc)
        evs = self.events_since(-1)
        # the COMPLETED turns, newest-first, capped — read off the cognition.turn.done lifecycle events.
        done = [e for e in evs if e.get("kind") == "cognition.turn.done"]
        seen, turn_ids = set(), []
        for e in reversed(done):                                  # newest-first
            tid = e.get("turn_id")
            if tid and tid not in seen:
                seen.add(tid)
                turn_ids.append(tid)
            if len(turn_ids) >= self.R2_COGNITION_TURNS:
                break
        if not turn_ids:
            return []
        # the per-role run:// addresses of those completed turns — from the cognition.role.ran events (the
        # SWARM's discovery surface; ok-only). Group by turn_id so the bound is per-turn.
        ran_by_turn: dict = {}
        for e in evs:
            if e.get("kind") == "cognition.role.ran" and e.get("ok") and e.get("turn_id") in seen \
               and e.get("address"):
                ran_by_turn.setdefault(e["turn_id"], []).append(e)
        items = []
        for tid in turn_ids:                                      # newest-first
            for e in ran_by_turn.get(tid, []):
                addr = e["address"]
                try:
                    val = _cog.resolve_address(self.store, addr, turn_id=tid, on_missing="skip")
                except Exception as ex:
                    self._emit("warning",
                               f"GROUP J: prior-turn cognition unresolvable at {addr} ({type(ex).__name__}) — skipped",
                               address=self.R2_COGNITION_ANCHOR)
                    continue
                if val is None:                                   # a pruned/unresolved ref (on_missing=skip)
                    continue
                snippet = val if isinstance(val, str) else _json.dumps(val, default=str)
                if len(snippet) > self.R2_COGNITION_PER_ROLE:     # bound one role's contribution (legible)
                    snippet = snippet[:self.R2_COGNITION_PER_ROLE] + "…"
                role = e.get("role") or "?"
                items.append({
                    "kind": "cognition", "address": self.R2_COGNITION_ANCHOR, "ts": e.get("ts"),
                    "text": f"[my prior thinking · role {role} @ {addr}] {snippet}",
                    "_raw": snippet,                              # X8 dedup identity (the role output text)
                    "pinned": False})
        return items

    def _r2_gather(self, locus: str, graph_id: str | None = None, now=None,
                   resolution: dict | None = None) -> list:
        """GATHER every item attached to the locus AND its ancestors (I6 annotations via
        `annotations_at`, I7 chats via `chats_at`, addressed events). Each item is normalised to a
        common shape `{kind, address, ts, text, pinned}` so the decay scores them uniformly. The
        `pinned` flag rides free off the open annotation/chat record (schema-additive — an old record
        with no `pinned` field reads as unpinned). REUSES R1's locus consumers (annotations_at /
        chats_at — never duplicated). Address validation lives in those helpers (S0 gate); the
        ancestors are pre-validated by `_r2_ancestors`.

        X6 (Convergence) — the ui://↔run:// BRIDGE: when `graph_id` is supplied AND the locus is a
        `ui://canvas/<node>` whose node exists in that graph, ALSO gather the node's run://-keyed strata
        (L6 version-history + node-instance events) via `_r2_run_strata`, so at the locus BOTH schemes'
        memory resolves into one bounded window. `graph_id` is OPTIONAL (default None): with no graph_id
        the run:// step does NOT fire and the ui:// gather is byte-for-byte unchanged (preserving every
        existing caller + addr_context_acceptance). The run:// items go through the SAME dedup/score/cap.

        E1 (mode-and-context-resolution-are-ONE-system) — `resolution` (optional, default None) is the
        per-mode-type×instance lens spec from `resolution_spec_for`. `strata` (a frozenset of admitted
        gather-kinds, or None = admit all) FILTERS which sources contribute — so a mode-type resolves a
        DIFFERENT context SHAPE over the SAME store+locus (background drops annotation/chat; off admits
        nothing). `howto_detail` (full/terse/none) is threaded into `_r2_howto_at`. resolution=None →
        admit-all + full howto = byte-for-byte today (every R2 caller preserved). The filter is a DATA
        membership test, never a mode-name branch (registry-is-truth — Tim's not-hardwired correction)."""
        # E1: derive the admitted-strata set + howto detail FROM the resolution spec (data, no mode-name).
        admit = None            # None = admit every stratum (today's behaviour)
        howto_detail = "full"
        if resolution is not None:
            admit = resolution.get("strata")
            howto_detail = resolution.get("howto_detail", "full")
        def _ok(kind: str) -> bool:
            return admit is None or kind in admit       # DATA membership test, NOT an `if mode ==` branch
        items = []
        for addr in self._r2_ancestors(locus):
            if _ok("annotation"):
                for a in self.annotations_at(addr):
                    # F1 LEARNING LOOP — a presentation pref rides the SAME annotations.jsonl leaf (no
                    # parallel store) but is NOT a comment: skip it in the comment stratum so it is not
                    # double-counted (the howto-stratum class of double-count `_r2_dedup` guards) — it is
                    # gathered as its OWN distinct `presentation_pref` stratum below, pin-persistent.
                    if a.get("kind") == "presentation_pref":
                        continue
                    items.append({"kind": "annotation", "address": addr, "ts": a.get("ts"),
                                  "text": f"[comment @ {addr}] {a.get('text', '')}",
                                  "_raw": (a.get("text", "") or ""),   # X8: underlying text, for dedup identity
                                  "pinned": bool(a.get("pinned"))})
            # F1 LEARNING LOOP — the learned presentation pref at this ancestor rides R2 resolve-at-locus
            # as its OWN distinct stratum (so a learned "present this terser" reaches the RHM's context the
            # SAME way everything else does). Pin-persistent like the howto leg (a pref doesn't decay) and
            # NO `_raw` key (so `_r2_dedup`'s "no _raw → never dropped" rule keeps it — it is never a
            # comment double-count). Admitted under its own gather-kind so a lens can drop it.
            if _ok("presentation_pref"):
                items.extend(self._r2_pref_at(addr, now=now))
            if _ok("chat"):
                for c in self.chats_at(addr):
                    items.append({"kind": "chat", "address": addr, "ts": c.get("ts"),
                                  "text": f"[chat @ {addr}] {c.get('role', '')}: {c.get('text', '')}",
                                  "_raw": (c.get("text", "") or ""),   # X8: underlying text, for dedup identity
                                  "pinned": bool(c.get("pinned"))})
            if _ok("event"):
                items.extend(self._r2_events_at(addr))
            # D1: the FOUNDATIONAL HOW-TO / AFFORDANCE stratum at this ancestor — pin-persistent (no recency
            # decay), flood-bounded (R2_HOWTO_MAX), through the SAME dedup/score/cap as every other item.
            # `now` is threaded so the pin-persistent ts matches the scorer's `now` (deterministic in tests);
            # generic over any address (registry-is-truth), never a per-element branch (Tim's correction).
            # E1: `howto_detail` (the lens) parameterizes it — the seam _r2_howto_at's docstring advertised.
            if _ok("howto"):
                items.extend(self._r2_howto_at(addr, now=now, detail=howto_detail))
        # X6: bridge the ui:// locus to its run:// counterpart (guarded; None when the bridge doesn't apply).
        # E1: the run:// stratum is admitted under the 'run' kind (so a lens can drop the version-trail too).
        run_addr = self._r2_run_counterpart(locus, graph_id)
        if run_addr is not None and _ok("run"):
            items.extend(self._r2_run_strata(run_addr, locus))
        # GROUP J — the cognition↔resolution loop (the system sees its own thinking). The prior turns' swarm
        # cognition is NOT address-attached + NOT locus-walked — it is conversation-global. So it is gated as
        # an EXPLICIT POSITIVE OPT-IN (`"cognition" in admit`), NOT via `_ok` (which is True for the default
        # admit-all `resolution=None` — that would SILENTLY leak global cognition into the address-attached
        # reads `context_at`/`surface_intent_at`, violating their "locus-attached context only" contract with
        # NO test failure). ONLY the dedicated cognition-resolution call in `_chat_context` supplies a spec
        # whose `strata` admits 'cognition' (at the fixed anchor); every other caller's frozenset omits it, so
        # this stratum is byte-for-byte invisible to them. The items already carry their own anchor address.
        if admit is not None and "cognition" in admit:
            items.extend(self._r2_cognition_strata(now=now))
        deduped = self._r2_dedup(items)
        # `_raw` is dedup-INTERNAL identity (added above for X8); strip it before returning so the gather's
        # output shape stays {kind,address,ts,text,pinned} — X3 persists this bundle into the payload, and
        # a leaked `_raw` would duplicate `text` on disk. Removing it cannot affect scoring/cap (they read
        # `text` only). Pre-X8 callers see exactly the old shape.
        for it in deduped:
            it.pop("_raw", None)
        return deduped

    def _r2_dedup(self, items: list) -> list:
        """X8 (Convergence) — collapse the SAME comment to ONE item BEFORE the budget cap.

        WHY: a single clicked comment lands through `ingest_comment` as THREE strata at the same
        address — an annotation (its `annotations.jsonl` branch, full text), the located-gold chat turn
        (`append_chat`, full text), AND one addressed event echo (`_emit("annotation", …)` at
        suite.py:2032, whose summary is the text TRUNCATED to 40 chars). So the gather sees it 2–3× and
        it would consume 2–3× the bounded R2 window — a double-count, not three distinct notebook items.

        IDENTITY (the crux, robust to the 40-char truncation): items are the same comment when they share
        an `(address, underlying-text)` identity. But the event echo's text is a 40-char PREFIX of the
        full text, so an exact full-text key would match annotation↔chat yet MISS the event (it would
        still count 2×). The model that actually collapses all three:
          • annotation ↔ chat: exact `(address, full _raw text)` — collapse to one. (No false-collapse:
            two genuinely-different comments differ in _raw.)
          • the event echo: dropped IFF its (possibly truncated) `_raw` is a PREFIX of some
            annotation/chat `_raw` AT THE SAME ADDRESS. This kills the narration echo WITHOUT flat-keying
            on a 40-char prefix (which would wrongly merge two distinct comments that happen to share a
            40-char opening — the "never drop legitimately-distinct items" clause).
        SURVIVOR = the full-text annotation/chat item, NEVER the truncated event (X4 later composes the
        prompt from this bundle; keeping the truncated echo would silently lose content).

        PRESERVE: this ONLY removes double-counting. It does NOT touch `_r2_score`/the recency·proximity·
        pin ranking or the `R2_BUDGET` cap — dropping echoes can only FREE budget, never reorder distinct
        items, so the ranking is preserved by construction. An item without `_raw` (e.g. a non-comment
        event, or any future stratum) is NEVER dropped — dedup is conservative."""
        full_keys = set()        # (address, full _raw) of annotation/chat items already kept
        full_by_addr: dict = {}  # address -> list of full _raw texts kept (for the event prefix test)
        out = []
        # PASS 1: keep annotation/chat, collapsing exact (address, _raw) duplicates (e.g. annotation↔chat).
        events = []
        for it in items:
            if it.get("kind") == "event":
                events.append(it)
                continue
            raw = it.get("_raw")
            if raw is None:
                out.append(it)               # no identity → never dropped (conservative)
                continue
            key = (it.get("address", ""), raw)
            if key in full_keys:
                continue                     # exact duplicate of an already-kept full-text item
            full_keys.add(key)
            full_by_addr.setdefault(it.get("address", ""), []).append(raw)
            out.append(it)
        # PASS 2: keep an event ONLY if it is NOT the truncated echo of a kept annotation/chat at its addr.
        for ev in events:
            raw = ev.get("_raw")
            if raw is None:
                # the standard comment echo carries no _raw; recover its underlying text from the summary
                # so the prefix test can run. Format: "[event] <kind>: comment at <addr>: <text[:40]>".
                txt = ev.get("text", "") or ""
                marker = f": comment at {ev.get('address', '')}: "
                raw = txt.split(marker, 1)[1] if marker in txt else None
            if raw is not None and any(full.startswith(raw)
                                       for full in full_by_addr.get(ev.get("address", ""), [])):
                continue                     # truncated echo of a kept comment → drop the double-count
            out.append(ev)
        return out

    def _r2_semantic_map(self, intent: str | None, items: list) -> dict:
        """X13 (Convergence) — embed the operator's `intent` and each gathered item's `text` ONCE per
        turn, return `{id(item): cosine(intent_vec, item_vec)}` so `_r2_score_and_cap` can add a weighted
        RELEVANCE term. Keyed by `id(item)` (not the text) so two items with identical text still get
        their own entry and nothing collides.

        REUSES THE EMBED FABRIC suite.py already reaches (NO new transport): the embeddings endpoint is
        its OWN base_url (BGE-M3 @ :8001), called via `fabric.transport.openai_embeddings_transport`
        + `fabric.client.complete_embeddings` — the exact path `nodes/embed.py` uses. Everything is
        embedded in ONE call (intent + every item text) so the per-turn embed cost is a single round-trip.
        The cosine MIRRORS `nodes/similarity.py` (dot/(‖a‖·‖b‖), inlined — no cross-module import of
        design/_system or the node; a zero-magnitude vector degrades that one pair to 0, never a crash).

        DEGRADE-WITH-WARNING (HARD CONSTRAINT — mirror suite.py:906 'embed model registry unreachable'):
        if there is no intent, or the embedder is unreachable / the call errors, return `{}` (every item's
        semantic term is 0) + emit a LOUD warning — so R2 FALLS BACK to the proven recency·proximity·pin
        ranking. NEVER a silent zero-vector, NEVER a wrong cosine, NEVER a crash of the per-turn gather.
        The empty-intent case is silent (no embedder fault — just no query this turn); only an embedder
        FAILURE warns."""
        intent = (intent or "").strip()
        if not intent or not items:
            return {}                                          # no query → no semantic term (not a fault)
        import math
        from fabric import client, transport, config as fcfg
        texts = [(it.get("text", "") or "") for it in items]
        try:
            t = transport.openai_embeddings_transport(base_url=fcfg.DEFAULT_EMBED_URL)
            # ONE round-trip: index 0 = the intent, 1..N = each item text (aligned to `items`).
            vecs = client.complete_embeddings(t, [intent] + texts,
                                              model=fcfg.DEFAULT_EMBED_MODEL, dim=fcfg.DEFAULT_EMBED_DIM)
        except Exception as e:
            # FAIL-LOUD-LEGIBLE, never crash the per-turn slice: warn (locus-less system-health warning,
            # exactly like suite.py:906's embed-registry guard) and degrade — caller sees {} → all 0.
            self._emit("warning",
                       f"X13: embed endpoint unreachable for R2 semantic ranking ({type(e).__name__}) — "
                       "semantic term degraded to 0; falling back to recency·proximity·pin")
            return {}
        intent_vec = vecs[0]
        ni = math.sqrt(sum(x * x for x in intent_vec))
        out = {}
        for it, v in zip(items, vecs[1:]):
            nv = math.sqrt(sum(x * x for x in v))
            if ni == 0.0 or nv == 0.0:                         # zero-magnitude → undefined cosine → 0 (no crash)
                out[id(it)] = 0.0
                continue
            dot = sum(x * y for x, y in zip(intent_vec, v))
            out[id(it)] = dot / (ni * nv)                      # cosine, mirror nodes/similarity.py
        return out

    def _r2_score_and_cap(self, items: list, locus: str, now, intent: str | None = None,
                          budget: int | None = None) -> list:
        """Score each item by the decay, sort DESC, then `budget_cap` — accumulate text until R2_BUDGET
        is reached and STOP (cap the window, NEVER stuff). Returns the surviving items in score order.
        The cap is the keystone (the guide's THE-critical requirement): with more items than the budget,
        only the highest-scoring (recent + proximate + pinned + RELEVANT) survive; the rest are DROPPED,
        so R2 can never recreate the context-flood it exists to kill.

        X13 (Convergence) — `intent` (the operator's current chat MESSAGE / locus comment — "what the
        operator is actually asking") adds the SEMANTIC term: embed the intent + each item ONCE here
        (`_r2_semantic_map`), then score = recency·proximity·pin + R2_SEMANTIC_WEIGHT·cosine. The cosine
        is PRECOMPUTED here and passed INTO `_r2_score` so the per-item score stays I/O-free and
        crash-free. With `intent=None` (the default — every pre-X13 caller) the map is empty and every
        item's semantic term is 0, so the ranking is byte-for-byte the pre-X13 recency·proximity·pin
        ordering (preserves addr_context_acceptance). When the embedder is DOWN the map is empty too
        (degrade-with-warning in `_r2_semantic_map`) — the SAME proven fallback."""
        sem = self._r2_semantic_map(intent, items)             # X13: {id(item): cosine}; {} if no intent / down
        scored = sorted(items,
                        key=lambda it: self._r2_score(it, locus, now, semantic=sem.get(id(it), 0.0)),
                        reverse=True)
        # E1: the resolution lens may OVERRIDE the window cap (focus resolves a tighter window; walkthrough
        # a wider one). `budget=None` (every pre-E1 caller) → the instance R2_BUDGET, byte-for-byte today.
        cap = self.R2_BUDGET if budget is None else budget
        out, total = [], 0
        for it in scored:
            t = it.get("text", "") or ""
            if total + len(t) > cap and out:                  # cap is hard once we have at least one item
                break
            out.append(it); total += len(t)
            if total >= cap:
                break
        return out

    def _resolve_context_at(self, locus: str | None, now=None, graph_id: str | None = None,
                            intent: str | None = None, resolution: dict | None = None) -> str:
        """The R2 entry point: resolve the BOUNDED, address-keyed context slice at the operator's locus.
        Returns a ready-to-inject block string, or '' when there is no locus / nothing attached (so the
        caller skips injection cleanly). FAIL-LOUD-LEGIBLE, never crash-the-turn (mirrors _chat_context's
        own model-registry guard — a raise here would break EVERY turn): a gather/score error warns +
        returns '' rather than propagating.

        X6 (Convergence) — `graph_id` is threaded through (optional, default None) so the gather can BRIDGE
        a `ui://canvas/<node>` locus to its `run://<graph_id>/<node>` counterpart (version-history L6 +
        node events). The production caller (`_chat_context`) HOLDS graph_id as ground truth and passes it;
        with no graph_id the gather's run:// step does not fire (the ui:// path is unchanged).

        X13 (Convergence) — `intent` (the operator's current chat MESSAGE / locus comment) is threaded to
        `_r2_score_and_cap`, which adds the SEMANTIC ranking term (R2_SEMANTIC_WEIGHT·cosine(intent,item)).
        Optional (default None): with no intent the ranking is the pre-X13 recency·proximity·pin (byte-for-
        byte). When the embedder is DOWN the semantic term degrades to 0 with a warning (handled in
        `_r2_semantic_map`) — the score+cap still runs, never crashing the turn.

        E1 (the mode-and-context-resolution-are-ONE-system criterion) — `resolution` (optional, default
        None) is the CONTEXT-RESOLUTION SPEC produced by `resolution_spec_for` (mode-type × instance). It
        parameterizes the R2 gather+cap WITHOUT any mode-name branch (registry-is-truth, the shape is
        DATA): `strata` filters which gather-stratum kinds are admitted, `howto_detail` tunes/suppresses
        the how-to leg, `budget` overrides the per-turn window cap. With resolution=None the gather +
        budget are EXACTLY today's (byte-for-byte — every existing R2 caller/suite stays green). This is
        §6.3 made real: ONE spine, the active mode-type's declarations choose the shape."""
        from datetime import datetime, timezone
        if not locus:
            return ""
        if now is None:
            now = datetime.now(timezone.utc)
        try:
            items = self._r2_gather(locus, graph_id=graph_id, now=now, resolution=resolution)
            if not items:
                return ""
            budget = None
            if resolution is not None:
                budget = resolution.get("budget")   # E1: the lens may resolve a tighter/wider window
            capped = self._r2_score_and_cap(items, locus, now, intent=intent, budget=budget)
            if not capped:
                return ""
            lines = "\n".join("  · " + (it.get("text", "") or "") for it in capped)
            # GROUP J — the framing is spec-driven: a resolution spec MAY supply its own `framing` header
            # (the cognition-resolution call does — "this is your OWN prior thinking", not "info at the
            # operator's locus", which would mislabel the conversation-global cognition anchor). Absent a
            # `framing` key (every pre-J caller: resolution=None, or a spec without it) the default locus
            # header is byte-for-byte unchanged.
            framing = resolution.get("framing") if resolution is not None else None
            if framing:
                return "\n" + framing + ":\n" + lines + "\n"
            return ("\nCONTEXT RESOLVED AT YOUR LOCUS (info attached to the address the operator is at — "
                    f"{locus} — and its ancestors, bounded by relevance/recency decay; this is what's "
                    "relevant HERE, answer with respect to it):\n" + lines + "\n")
        except Exception as e:
            # locus-BOUND warning (not a locus-less system-health one) — the failure happened AT this
            # address, so it carries `address=locus` (event_address_acceptance: every _emit is stamped
            # or a documented locus-less exclusion; this one is honestly locus-bound).
            self._emit("warning", f"R2 context resolution failed ({type(e).__name__})", address=locus)
            return ""

    def context_at(self, address: str) -> dict:
        """R2 STANDALONE READ — the addressed-context inspector. EXPOSES the SAME R2 engine the chat
        runs inside `_resolve_context_at`, but for an ARBITRARY ui:// address (not just the live locus)
        and as a STRUCTURED bundle (not the inject-string). It is the read-face of "what context is
        resolved AT this address?" — annotations + chats + addressed events at the locus AND its
        ancestors, scored + budget-capped by the recency·proximity·pin decay.

        REUSES, never reimplements (rule 3 — one scoring source): `_r2_gather` (the address-keyed
        gather, ancestors walked, deduped by X8, `_raw` stripped → JSON-clean {kind,address,ts,text,
        pinned}) → `_r2_score_and_cap` (the SAME decay + the SAME `R2_BUDGET` cap the chat gets — this
        is the BYTE-FOR-BYTE pattern `surface_intent_at` uses at mint-time, suite.py:6831). The scoring
        is NOT touched here; this method only calls it for a given address.

        FAIL-LOUD on a malformed address (S0 grammar gate): we validate the address EXPLICITLY here
        (`parse_ui_address` RAISES on a malformed ui:// like 'not-a-ui-address'), mirroring how
        `annotations_at` / `_registry_howto_for` / `resolve_scope` all front their reads with the gate.
        WHY explicit and not relied-on-from-the-gather: `_r2_gather` walks `_r2_ancestors`, which is
        deliberately SILENT-SKIP on a malformed candidate (suite.py:2573 — it must never crash the live
        turn), so the gather would return [] for a malformed address — an empty-200 that LIES "no
        context here" instead of "that is not an address". The standalone READ-face wants the raise to
        surface as a 400 (mirroring `/api/scope` + `/api/address-help`), so we gate up-front. A
        missing-address is the bridge's KeyError (also a 400).

        DENY-ALL / honest-empty on a well-formed-but-UNREGISTERED address: `annotations_at` /
        `chats_at` are address-keyed STORAGE (not registry-gated) — an unattached well-formed address
        returns `[]` (nothing was ever attached there), so the bundle is honestly empty. We NEVER
        fabricate context for an address that has none (the no-confabulation law).

        Returns {address, items:[{kind,address,ts,text,pinned}], count, budget} — `items` is the
        scored+capped slice (highest-relevance first, bounded by R2_BUDGET), `count` its length,
        `budget` the cap that bounded it (so the reader can see the window was applied)."""
        from datetime import datetime as _dt, timezone as _tz
        from contracts.ui_info import parse_ui_address
        # S0 grammar gate FIRST — a malformed address MUST raise (→ the route's 400), because the gather
        # below silent-skips it (via `_r2_ancestors`) and would otherwise return a lying empty-200. NO
        # try/except around the gather: a well-formed-but-empty address flows through cleanly
        # (gather → [] → cap → []), the honest-empty DENY-ALL bundle.
        parse_ui_address(address)
        items = self._r2_score_and_cap(self._r2_gather(address), address, _dt.now(_tz.utc))
        return {"address": address, "items": list(items), "count": len(items),
                "budget": self.R2_BUDGET}

    # ════════════════════════════════════════════════════════════════════════════════════════════
    # THE SINGLE-SOURCE RHM VERB REGISTRY (replaces the old 3 parallel tables RHM_VERBS /
    # RHM_VERB_DESC / RHM_VERB_CLASS, which could drift). ONE VerbSpec per verb carries everything:
    # the gloss, the governance class, the modes it is OFFERED in (mode-primary), and a predicate over
    # the live affordance context (context-refines). The three legacy names are DERIVED below — there
    # is no second copy to fall out of sync (AGENTS.md rule 3, one-source).
    #
    # MODE SETS (per the Change-Maps §suite, mode-primary / context-refines):
    #   run    → {focus, background, listening, text-only, decide-for-me}
    #            pred = graph_nonempty (no point recomputing an empty graph)
    #            NOT walkthrough / watch-and-react: those are GUIDE / OBSERVE modes (show+consult only) —
    #            they do not RECOMPUTE the graph (spec-aligned). (whether walkthrough should offer run is
    #            a Tim mode-design call — flagged needs_tim; shipping the spec-aligned version now.)
    #   show   → all modes BUT 'off'
    #   consult→ {walkthrough, watch-and-react, listening, text-only, decide-for-me}
    #   build/propose/panel/extend → {listening, text-only, decide-for-me}
    #   off    → no verb is offered (the RHM is disabled; chat() short-circuits before this anyway)
    #   text-only MIRRORS listening for the ACTION set (its style differs via the mode directive, not
    #            the affordances) — so wherever 'listening' appears above, 'text-only' appears too.
    # The dict insertion ORDER (run, propose, build, consult, show, panel, extend) defines RHM_VERBS'
    # tuple order — kept identical to the prior literal so RHM_VERBS == the same 7-tuple (a contract
    # rhm_completion_acceptance asserts exactly).
    # ════════════════════════════════════════════════════════════════════════════════════════════
    _M_BUILDISH = frozenset({"listening", "text-only", "decide-for-me"})
    _M_RUN = frozenset({"focus", "background", "listening", "text-only", "decide-for-me"})
    _M_CONSULT = frozenset({"walkthrough", "watch-and-react", "listening", "text-only", "decide-for-me"})
    _M_ALL_BUT_OFF = frozenset(MODES) - {"off"}

    RHM_VERB_SPECS = {
        "run":     VerbSpec("recompute the current graph", "run",
                            _M_RUN, lambda ctx: ctx.get("graph_nonempty", False)),
        "propose": VerbSpec("draft a new node-type for approval", "register_type",
                            _M_BUILDISH, lambda ctx: True),
        "build":   VerbSpec("compose a pipeline on the canvas", "compose",
                            _M_BUILDISH, lambda ctx: True),
        "consult": VerbSpec("read the system's own code+design", "inspect",
                            _M_CONSULT, lambda ctx: True),
        "show":    VerbSpec("move the operator's view to node(s)/UI", "inspect",
                            _M_ALL_BUT_OFF, lambda ctx: True),
        "panel":   VerbSpec("add a declarative settings panel", "ui_panel",
                            _M_BUILDISH, lambda ctx: True),
        "extend":  VerbSpec("write a new UI component (build-gated)", "ui_extension",
                            _M_BUILDISH, lambda ctx: True),
        # G8.2 — config-as-tools: the RHM operates its OWN config by voice, not only the UI. All AUTO
        # (governance class 'configure') — operator-directed + reversible; the lifecycle fail-louds on
        # VRAM. configure sets any rhm_config slot (model/persona/mode/stt/tts_engine/voice_enabled/roles
        # — so "use the fast judge" or "switch to xtts" works); load/unload_voice drive the lifecycle.
        "configure":    VerbSpec("set RHM config (model/persona/mode/voice/ear/role bindings)", "configure",
                                 _M_BUILDISH, lambda ctx: True),
        "load_voice":   VerbSpec("load a voice service (STT ear / TTS engine) into VRAM", "configure",
                                 _M_BUILDISH, lambda ctx: True),
        "unload_voice": VerbSpec("unload a voice service to free VRAM", "configure",
                                 _M_BUILDISH, lambda ctx: True),
        # CONVO→SELF-BUILD BRIDGE — the conversational entry to the claude -p self-build wire. The
        # wire's dispatcher only acts on payload intent=="build" items (is_build_intent), which until
        # now were minted ONLY by the wire-DOOR (/api/build-intent, /api/intent-at). The RHM's existing
        # consequential verbs (propose/panel/extend) create NET-NEW components via /api/apply — they do
        # NOT reach the edit-existing-code wire. `request_change` closes that gap: it routes a
        # conversational change-request ("make the run button confirm before recomputing", "this panel
        # is too cramped, fix it") into the EXISTING `surface_intent_at` producer, which mints an
        # intent=="build" item that surfaces for approval through the SAME inbox/build-intent card +
        # /api/resolve approve the wire-door uses. CONSEQUENCE CLASS = the same SURFACE-then-approve
        # consent shape the wire-door has: it SURFACES a build-intent for the operator's approval —
        # NOTHING builds until the operator approves it (the wire only dispatches an approved
        # decision_build, and resolve_surfaced stays operator-only + off the MCP face). So the safe,
        # consent-respecting action this verb performs IS the surfacing (action_class register_type =
        # CONFIRM/SURFACE posture, like propose — it surfaces a draft for the operator, never auto-acts).
        "request_change": VerbSpec("surface a build-intent to CHANGE existing code at a ui:// element "
                                   "(routes a conversational change-request to the self-build wire; "
                                   "nothing builds until the operator approves)", "register_type",
                                   _M_BUILDISH, lambda ctx: True),
    }

    # --- the three legacy names, DERIVED from the one registry (no drift) ---
    # The dispatcher's WHITELIST: a verb the RHM may perform. apply/delete/file-write are NOT here, so
    # the conversational surface can never reach them (E6). Tuple in registry-insertion order.
    RHM_VERBS = tuple(RHM_VERB_SPECS)
    # one-line gloss per verb — so the grounding context can tell the RHM its OWN capabilities.
    RHM_VERB_DESC = {v: s.desc for v, s in RHM_VERB_SPECS.items()}
    # G3: each verb's GOVERNANCE action-class — the deterministic decide-for-me router input. AUTO
    # classes (run/compose/inspect) run; CONFIRM classes (register_type/ui_panel/ui_extension) surface.
    RHM_VERB_CLASS = {v: s.action_class for v, s in RHM_VERB_SPECS.items()}

    # the OpenAI-tool parameter schema per verb — built FROM the registry (single-source). The shapes
    # MIRROR exactly what _json_obj_to_action consumes (so a native tool_call round-trips to an action
    # dict with no shape drift): run{} · consult{query} · show{targets[]} · build{steps[]} ·
    # propose/panel/extend{name,spec}.
    _VERB_PARAMS = {
        "run":     {"type": "object", "properties": {}},
        "consult": {"type": "object",
                    "properties": {"query": {"type": "string",
                                             "description": "the question about this system's own design/code"}},
                    "required": ["query"]},
        "show":    {"type": "object",
                    "properties": {"targets": {"type": "array", "items": {"type": "string"},
                                               "description": "node-ids and/or ui:// regions to move the view to"}},
                    "required": ["targets"]},
        "build":   {"type": "object",
                    "properties": {"steps": {"type": "array", "items": {"type": "object"},
                                             "description": "pipeline steps: a node {as,type,config} or a wire {wire:'a.port -> b.port'}"}},
                    "required": ["steps"]},
        "propose": {"type": "object",
                    "properties": {"name": {"type": "string"}, "spec": {"type": "string"}},
                    "required": ["name", "spec"]},
        "panel":   {"type": "object",
                    "properties": {"name": {"type": "string"}, "spec": {"type": "string"}},
                    "required": ["name", "spec"]},
        "extend":  {"type": "object",
                    "properties": {"name": {"type": "string"}, "spec": {"type": "string"}},
                    "required": ["name", "spec"]},
        "configure":    {"type": "object",
                         "properties": {"updates": {"type": "object",
                             "description": "rhm_config slots to set: any of model, base_url, persona, mode, "
                                            "stt, tts_engine, tts_voice, voice_enabled, timeout, roles "
                                            "({role_id:{model,base_url,knobs}})"}},
                         "required": ["updates"]},
        "load_voice":   {"type": "object",
                         "properties": {"service": {"type": "string",
                             "description": "a loadable voice-service id (e.g. tts-qwen3tts, stt-parakeet)"}},
                         "required": ["service"]},
        "unload_voice": {"type": "object",
                         "properties": {"service": {"type": "string"}}, "required": ["service"]},
        # CONVO→SELF-BUILD BRIDGE: the change description is REQUIRED; the target is the ui:// element/scope
        # the change is about. The target is OPTIONAL in the schema because address resolution has THREE
        # tiers in the dispatcher (indicated locus → named-element lookup → ASK) — if the operator has
        # pointed at an element this turn, the dispatcher uses that indicated locus and the model need not
        # restate the address. When neither an indicated locus nor a resolvable named target exists, the
        # verb ASKS which element rather than guessing a scope (a wrong scope = a wrong/over-broad build).
        "request_change": {"type": "object",
                           "properties": {
                               "change": {"type": "string",
                                          "description": "what to change, in plain words (becomes the "
                                                         "build-intent's spec) — e.g. 'make the run button "
                                                         "confirm before recomputing'"},
                               "target": {"type": "string",
                                          "description": "the ui:// element/scope the change is about "
                                                         "(e.g. ui://toolbar/run), OR a recognizable element "
                                                         "name ('the run button'). OMIT if the operator has "
                                                         "pointed at the element this turn (the indicated "
                                                         "locus is used)."}},
                           "required": ["change"]},
    }

    def _affordance_context(self, graph_id: str, focus: dict | None = None) -> dict:
        """The live AFFORDANCE CONTEXT a verb's predicate is evaluated against — all derived from
        EXISTING reads (state() / now() / the operator's focus), nothing fabricated:
          - graph_nonempty : the current graph has at least one node (a `run` makes sense)
          - inbox_pending  : there is at least one item awaiting the operator
          - node_selected  : the operator currently has a node selected on the canvas (co-presence)
        Tolerant: a read hiccup degrades a flag to False rather than crashing a turn (the affordance
        layer narrows the OFFER; the dispatcher's whitelist is the real gate, so a conservative-False
        here only offers fewer verbs, never weakens safety)."""
        try:
            st = self.state(graph_id)
            graph_nonempty = len(st.get("nodes", [])) > 0
        except Exception:
            graph_nonempty = False
        try:
            inbox_pending = any(d.get("resolved") is None for d in self.inbox.list())
        except Exception:
            inbox_pending = False
        node_selected = bool((focus or {}).get("selected"))
        return {"graph_nonempty": graph_nonempty,
                "inbox_pending": inbox_pending,
                "node_selected": node_selected}

    def available_verbs(self, mode: str, ctx: dict) -> list:
        """The verbs OFFERED right now = those whose spec lists this `mode` AND whose predicate holds
        for the live affordance context. Mode-primary, context-refines. Order follows the registry
        (run, propose, build, …) so the rendered list + the tools array are deterministic. This is the
        ONE source both channels (the rendered verb list in _chat_context and the _rhm_tools array)
        read, so the two never disagree about what the RHM may do."""
        return [v for v, s in self.RHM_VERB_SPECS.items()
                if mode in s.modes and s.predicate(ctx)]

    def _rhm_tools(self, mode: str, ctx: dict) -> list:
        """The OpenAI tools array for THIS turn — built FROM available_verbs() + the single-source
        RHM_VERB_DESC (description) + _VERB_PARAMS (schema). So the model is offered exactly the verbs
        that are mode-appropriate + context-sensible, each as a native function tool. Empty list when
        no verb is available (off, or an empty graph with only `run` eligible) — the caller then passes
        no tools (tool_choice auto over zero tools = a plain reply)."""
        tools = []
        verbs = self.available_verbs(mode, ctx)
        for v in verbs:
            tools.append({
                "type": "function",
                "function": {
                    "name": v,
                    "description": self.RHM_VERB_DESC.get(v, ""),
                    "parameters": self._VERB_PARAMS.get(v, {"type": "object", "properties": {}}),
                },
            })
        # OFFER-WITH-OPTIONS (the consent affordance): if the RHM can ACT in this mode, it can also OFFER
        # — call `suggest` to surface a "shall I?" card (sees-then-approves, ANY offered verb) INSTEAD of
        # acting now. This is the convergence's propose-affordance, unified into native tool-calling (no
        # retired AFFORD: text directive).
        #
        # B2 · ON-SCREEN INTERACTIVE BUILD (the rich layer, multi-option): `suggest` accepts EITHER a single
        # `verb`/`address`/`args` (B1, the "shall I?" offer — UNCHANGED) OR an `options[]` array of two or
        # more ALTERNATIVES the operator chooses between on a comparison surface (e.g. several panel designs,
        # several build approaches). Each option carries a `label` + a `summary` (the DISTINGUISHING content —
        # what makes this option different, the thing the operator reads to choose) + the verb's `args`. For
        # the CONSEQUENTIAL verbs (build/panel/extend) the offer should come on-screen interactive (options to
        # weigh + chat-until-approve), NOT a silent inbox-drop — that is exactly what `options[]` is for. The
        # options are carried FAITHFULLY from the model's own tool-call (rule 8 — never fabricated here); a
        # one-option offer renders as B1's single card, two+ render the comparison surface (the FE branches on
        # the interactive marker derived from the verb class, never invents alternatives).
        if verbs:
            _consequential = sorted({"build", "panel", "extend"} & set(verbs))
            tools.append({
                "type": "function",
                "function": {
                    "name": "suggest",
                    "description": ("OFFER an action the operator SEES and approves (the 'shall I?' affordance) "
                                    "INSTEAD of doing it now. Use when proposing rather than acting, or when the "
                                    "operator should choose/steer first. For a CONSEQUENTIAL verb "
                                    f"({', '.join(_consequential) or 'build/panel/extend'}) prefer `options`: offer "
                                    "TWO OR THREE real ALTERNATIVES (e.g. different panel designs / build approaches), "
                                    "each with a distinguishing `summary`, so the operator compares + chooses + "
                                    "discusses on screen — never a silent queue."),
                    "parameters": {"type": "object", "properties": {
                        # B1 single-offer shape (unchanged) — used when there is one obvious action to confirm.
                        "verb": {"type": "string", "enum": list(verbs),
                                 "description": "the single action being offered (a real RHM verb); omit if using `options`"},
                        "address": {"type": "string", "description": "the ui:// locus the action targets, if any"},
                        "args": {"type": "object", "description": "the offered verb's arguments"},
                        "label": {"type": "string", "description": "a short human label for the offer"},
                        # B2 multi-option shape — used to offer alternatives on a comparison surface.
                        "options": {"type": "array",
                            "description": ("TWO OR THREE alternative actions the operator chooses between on a "
                                            "comparison surface. Use for consequential verbs (build/panel/extend) so the "
                                            "operator weighs real options + chats before approving. Nothing runs until approved."),
                            "items": {"type": "object", "properties": {
                                "verb": {"type": "string", "enum": list(verbs)},
                                "address": {"type": "string"},
                                "args": {"type": "object", "description": "the verb's arguments (the panel spec / the build steps)"},
                                "label": {"type": "string", "description": "a short name for this alternative"},
                                "summary": {"type": "string", "description": "what makes THIS option different — the line the operator reads to choose"},
                            }, "required": ["verb"]}},
                    }},
                },
            })
        return tools

    # tool-capability gate: a short-TTL cache (mirrors available_models) so the RHM doesn't re-probe
    # /api/show on every turn, while a model brought up later still becomes usable without a restart.
    _tools_cap_cache: dict = {}                               # (model, base_url) -> (bool, monotonic_stamp)
    TOOLS_CAP_TTL = 60.0

    def _model_supports_tools(self, model: str, base_url: str | None = None) -> bool:
        """Endpoint-aware, FAIL-LOUD tool-capability gate (rule 4 — no silent assume-capable). Delegates
        to the fabric helper (transport.model_supports_tools), which RAISES if it cannot determine the
        answer (endpoint down / no capabilities field / unknown endpoint kind). Here we translate a
        cannot-determine RAISE into FALSE — the RHM treats 'can't prove it supports tools' as 'does NOT',
        the safe refusal (a non-tool model must never silently be called with tools). Cached short-TTL
        (TOOLS_CAP_TTL) keyed on (model, base_url); a model that comes up later becomes usable without a
        restart. A POSITIVE (True) result is cached; a False from an unreachable endpoint is NOT cached
        (so recovery is immediate, mirroring the degraded-models policy)."""
        import time as _t
        from fabric import config as fcfg, transport as ftrans
        base = base_url or fcfg.DEFAULT_BASE_URL
        key = (model, base)
        hit = self._tools_cap_cache.get(key)
        if hit is not None and (_t.monotonic() - hit[1]) < self.TOOLS_CAP_TTL:
            return hit[0]
        # Classify the endpoint so the tool-cap detector probes the RIGHT way (was: everything-not-4100
        # = ollama, which mis-routed a raw vLLM endpoint to ollama's /api/show → false refusal). ollama
        # is :11434; litellm proxy :4100; a raw vLLM OpenAI server (the local model workers, :8000+) is
        # its own kind (probed by a forced tool-call). Default base (config) stays ollama.
        from fabric import config as _fc
        if "4100" in base:
            endpoint = "litellm"
        elif "11434" in base or base.rstrip("/") == _fc.DEFAULT_BASE_URL.rstrip("/"):
            endpoint = "ollama"
        else:
            endpoint = "vllm"                                  # raw OpenAI-compatible vLLM (local workers)
        try:
            ok = bool(ftrans.model_supports_tools(model, base_url=base, endpoint=endpoint))
        except Exception:
            return False                                       # cannot determine → False (safe), NOT cached
        self._tools_cap_cache[key] = (ok, _t.monotonic())
        return ok

    # consult retrieval: the WHOLE repo (~400k chars ≈ 100k tokens) into one model call overflowed /
    # ran slow / "didn't return". So consult RETRIEVES a query-relevant slice instead of stuffing the
    # repo — keyword scan over the SAME file set the codebase node reads (single-source the corpus), no
    # embed-service dependency (retrieval-proper/embed is still future). Cap the fed source so it stays
    # bounded; cite which files were used; on no match fall back to a small curated set (never the whole
    # repo). The "answer strictly from source, cite the file, abstain if absent" contract is preserved.
    CONSULT_CAP = 40000                                       # max chars of source fed to the model (~10k tok)
    CONSULT_PER_FILE_CAP = 8000                               # max chars any ONE file contributes — so a single
    #                                                            huge file (suite.py ≈140k) can't monopolize the
    #                                                            budget and crowd out the actually-relevant smaller
    #                                                            file (scheduler.py). ~CAP/5 → ≥5 distinct files of
    #                                                            headroom. Big files get a relevance-WINDOWED slice
    #                                                            (around the first term hit — the brief's "sections"),
    #                                                            small files come in whole.
    CONSULT_CURATED = ("AGENTS.md", "MAP.md", "STATE.md")     # the orientation fallback when nothing matches
    _CONSULT_STOPWORDS = frozenset((
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being", "of", "to", "in", "on",
        "for", "and", "or", "but", "with", "as", "by", "at", "from", "how", "what", "why", "where",
        "when", "which", "who", "does", "do", "did", "this", "that", "these", "those", "it", "its",
        "system", "work", "works", "i", "you", "me", "my", "can", "could", "would", "should", "tell",
        "about", "explain", "describe", "show", "get", "use", "used", "have", "has", "into", "out"))

    @classmethod
    def _consult_terms(cls, query: str) -> list:
        """Salient lowercase terms from a query — words ≥3 chars, minus stopwords. The retrieval keys."""
        import re
        words = re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", (query or "").lower())
        seen, out = set(), []
        for w in words:
            if w in cls._CONSULT_STOPWORDS or w in seen:
                continue
            seen.add(w); out.append(w)
        return out

    def _retrieve_for_consult(self, query: str) -> tuple:
        """Keyword retrieval over the repo — returns (context, sources, file_list). Feeds ONLY the
        query-relevant files/sections (bounded by CONSULT_CAP), not the whole repo. file_list is a short
        repo orientation (every candidate file's relpath). sources is the files actually fed (for the
        citation + the test). On no keyword match, falls back to the curated orientation set — NEVER the
        whole repo. No embed-service dependency: a plain term scan (relevance = term-hit count)."""
        import os, glob
        from nodes import codebase as cb
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # ~/company (single-source w/ codebase node)
        files = []                                            # (relpath, text) for every candidate file
        for g in cb.DEFAULT_GLOBS:
            for p in sorted(glob.glob(os.path.join(root, g))):
                try:
                    text = open(p, encoding="utf-8").read()
                except Exception:
                    continue
                files.append((os.path.relpath(p, root), text))
        file_list = [rel for rel, _ in files]
        terms = self._consult_terms(query)
        scored = []
        for rel, text in files:
            low = text.lower(); rel_low = rel.lower()
            score = sum(low.count(t) + (3 if t in rel_low else 0) for t in terms)   # filename match weighted
            if score > 0:
                scored.append((score, rel, text))
        scored.sort(key=lambda x: (-x[0], x[1]))
        if not scored:                                        # no match → curated orientation set, never the whole repo
            picked = []                                       # read the curated files DIRECTLY (not all are in the
            for rel in self.CONSULT_CURATED:                  # codebase globs — STATE.md isn't — so don't depend on it)
                try:
                    picked.append((rel, open(os.path.join(root, rel), encoding="utf-8").read(), []))
                except Exception:
                    continue
        else:
            picked = [(rel, text, [t for t in terms if t in text.lower()]) for _, rel, text in scored]
        context, sources = self._fill_consult_budget(picked)
        return context, sources, file_list

    def _fill_consult_budget(self, picked: list) -> tuple:
        """Fill the CONSULT_CAP budget ACROSS the top-ranked (rel, text, hits) files in the given order,
        capping each file's contribution to CONSULT_PER_FILE_CAP so no single huge file monopolizes the
        budget. A small file comes in WHOLE; a big file gets a relevance-WINDOWED slice (centred on its
        first matching term — the brief's "files/SECTIONS"), so the slice carries the relevant code, not
        the header/imports. SHARED by both the keyword path (_retrieve_for_consult) and the semantic path
        (_retrieve_for_consult_semantic) — one bounding discipline, never two. Returns (context, sources)."""
        parts, sources, total = [], [], 0
        for rel, text, hits in picked:
            if total >= self.CONSULT_CAP:
                break
            budget = min(self.CONSULT_PER_FILE_CAP, self.CONSULT_CAP - total)
            if len(text) <= budget:                           # small file → whole
                chunk = f"\n===== {rel} =====\n{text}\n"
            else:                                             # big file → windowed slice around the first hit
                low = text.lower()
                pos = min((low.find(t) for t in hits if low.find(t) >= 0), default=0)
                start = max(0, pos - 1000)
                excerpt = text[start:start + budget]
                tag = rel if start == 0 and len(excerpt) >= len(text) else f"{rel} (excerpt)"
                chunk = f"\n===== {tag} =====\n{excerpt}\n"
            if total + len(chunk) > self.CONSULT_CAP and parts:
                break                                         # keep the overall cap hard once we have something
            parts.append(chunk); sources.append(rel); total += len(chunk)
        return "".join(parts), sources

    # ============================================================================================
    # CONSULT-MIGRATION — semantic retrieval against the LIVE X12 vector index (retiring the stuff path)
    # ============================================================================================
    # WHY: the `codebase` node STUFFS the whole repo into one context and FAILS LOUD past max_chars (now
    # 600k; the repo is 865k). STATE.md:47 named the fix: "embed-based (semantic) retrieval — the next
    # rung." That rung is now BUILT + LIVE: the embedder (BGE-M3 @ :8001) is up, and the X12 persisted
    # vector index (store/vector_index.py over the store `vectors/` namespace) is populated with `code://`
    # symbol addresses. So consult RETRIEVES the query-relevant slice from the index instead of stuffing
    # the whole repo. This AUGMENTS the proven keyword scan — it does NOT replace it: the keyword path
    # (_retrieve_for_consult) REMAINS the fallback for no-match / no-index / embedder-down.
    #
    # NO PARALLEL SYSTEM: the embed call reuses the EXACT fabric path nodes/embed.py uses (mirrors
    # _semantic_for_r2's X13 reuse), and the ranking reuses store/vector_index.query_index (which itself
    # reuses nodes/retrieve's cosine). NO new retriever, NO new embedding transport, NO new whole-repo
    # stuffing. DEGRADE-WITH-WARNING: an unreachable :8001 or an empty index → a LOUD warning + the
    # keyword fallback (never a silent zero-vector, never a wrong cosine).
    def _embed_consult_query(self, query: str):
        """Embed ONE consult query through the EXACT fabric path nodes/embed.py + _semantic_for_r2 use
        (NO new transport): BGE-M3 @ DEFAULT_EMBED_URL, with the SAME model/dim the X12 index was built
        with so the cosine is dim-consistent (a mismatch is already fail-loud at retrieve._cosine). Returns
        the query vector, or None on an unreachable endpoint — DEGRADE-WITH-WARNING (mirrors suite.py's
        _semantic_for_r2 :8001-down guard): a LOUD warning + None so the caller falls back to keyword. NEVER
        a fabricated/zero vector."""
        from fabric import client, transport, config as fcfg
        try:
            t = transport.openai_embeddings_transport(base_url=fcfg.DEFAULT_EMBED_URL)
            return client.complete_embeddings(t, [query], model=fcfg.DEFAULT_EMBED_MODEL,
                                              dim=fcfg.DEFAULT_EMBED_DIM)[0]
        except Exception as e:
            self._emit("warning",
                       f"consult: embed endpoint unreachable for semantic retrieval ({type(e).__name__}) — "
                       "falling back to the keyword scan")
            return None

    @staticmethod
    def _code_addr_parts(address: str) -> tuple:
        """Split a `code://<file-stem>/<symbol>` index address into (file_stem, symbol). A file-only
        `code://<file-stem>` → (stem, None). A non-code:// address → (None, None) so the caller skips it
        (the index also holds `ui://` addresses, which have no source file to read)."""
        if not isinstance(address, str) or not address.startswith("code://"):
            return None, None
        rest = address[len("code://"):]
        if "/" in rest:
            stem, sym = rest.split("/", 1)
            return stem, (sym or None)
        return rest, None

    def _retrieve_for_consult_semantic(self, query: str) -> tuple | None:
        """SEMANTIC retrieval against the LIVE X12 index (the migration path). Embeds the query → ranks the
        persisted index by cosine (store/vector_index.query_index, reusing nodes/retrieve) → resolves the
        top-K ranked `code://` addresses back to their SOURCE files (the SAME worktree file set the keyword
        path reads — single-source the corpus, no runtime design/ dependency) → builds the SAME bounded
        slice (_fill_consult_budget). Returns (context, sources, file_list) on a usable result, or None to
        signal the caller to FALL BACK to the keyword scan. DEGRADE-WITH-WARNING (HARD CONSTRAINT):
          • embedder :8001 unreachable  → _embed_consult_query warns + returns None → here returns None
          • index EMPTY (embedder was down at build) → query_index's honest note → warn + return None
          • ranked but NO code:// address resolves to a readable file → return None (keyword fallback)
        NEVER a silent zero-vector, NEVER a fabricated nearest, NEVER a wrong cosine."""
        import os, glob
        from nodes import codebase as cb
        from store import vector_index as vx
        qvec = self._embed_consult_query(query)
        if qvec is None:                                      # :8001 down — warned already
            return None
        result = vx.query_index(self.store, qvec, k=8, with_note=True)
        ranked = result.get("ranked", [])
        if not ranked:                                        # EMPTY index (embedder down at build) or no rank
            self._emit("warning",
                       f"consult: the vector index returned no ranking ({result.get('note', 'empty')}) — "
                       "falling back to the keyword scan")
            return None
        # Resolve the ranked code:// addresses back to source files in the worktree (the SAME globs the
        # keyword path + the codebase node read — one corpus). Read each candidate file ONCE.
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # ~/company (this worktree)
        files = {}                                            # stem -> [(relpath, text), ...] (stem can collide)
        rel_text = {}                                         # relpath -> text
        for g in cb.DEFAULT_GLOBS:
            for p in sorted(glob.glob(os.path.join(root, g))):
                rel = os.path.relpath(p, root)
                if rel in rel_text:
                    continue
                try:
                    text = open(p, encoding="utf-8").read()
                except Exception:
                    continue
                rel_text[rel] = text
                stem = os.path.splitext(os.path.basename(rel))[0]
                files.setdefault(stem, []).append(rel)
        file_list = sorted(rel_text.keys())
        picked, seen = [], set()                              # (rel, text, hits) in cosine-rank order, de-duped
        for r in ranked:
            stem, sym = self._code_addr_parts(r.get("id", ""))
            if stem is None or stem not in files:             # ui:// address or a stem with no source file
                continue
            cands = files[stem]
            # Disambiguate a stem collision by the symbol actually appearing in the file; else the first.
            rel = None
            if sym:
                for c in cands:
                    if sym in rel_text[c]:
                        rel = c; break
            rel = rel or cands[0]
            if rel in seen:
                continue
            seen.add(rel)
            # hits = the symbol (so the windowing centres on the relevant region for a big file)
            picked.append((rel, rel_text[rel], [sym] if sym else []))
        if not picked:                                        # nothing in the index resolved to a readable file
            self._emit("warning",
                       "consult: the index ranked addresses but none resolved to a source file — "
                       "falling back to the keyword scan")
            return None
        context, sources = self._fill_consult_budget(picked)
        return context, sources, file_list

    def _retrieve_for_consult_best(self, query: str) -> tuple:
        """The consult retrieval ENTRY: SEMANTIC-first (the live X12 index), KEYWORD-fallback (the proven
        scan). Tries _retrieve_for_consult_semantic; on its None signal (embedder down / empty index / no
        resolvable match — each already warned) returns the keyword _retrieve_for_consult. The keyword path
        is UNCHANGED + still directly tested; this wrapper only chooses which one grounds a real consult."""
        sem = self._retrieve_for_consult_semantic(query)
        if sem is not None:
            return sem
        return self._retrieve_for_consult(query)

    def consult(self, query: str) -> dict:
        """The RHM reads the system's OWN code+design (the first-purpose Q&A, as a callable) and
        answers — so it knows how it is built. Grounded in a RETRIEVED, query-relevant slice
        (SEMANTIC-first against the live X12 vector index, KEYWORD-fallback — bounded by CONSULT_CAP,
        NEVER the whole repo, which overflowed/stalled); cites the files used; abstains if the answer
        isn't there. DEGRADE-WITH-WARNING: an unreachable embedder / empty index falls back to the proven
        keyword scan with a loud warning. A read (AUTO). Uses DEFAULT_CLOUD_TIMEOUT (a consult can wait)."""
        from fabric import client, transport, config as fcfg
        cfg = self.rhm_config()
        context, sources, file_list = self._retrieve_for_consult_best(query)
        orient = ", ".join(file_list)
        sys_p = ("You answer questions about THIS system's own design and code, STRICTLY from the SOURCE "
                 "below (a RETRIEVED slice of the repo selected for this question, not the whole repo). "
                 "Cite the relevant file(s). If the answer is not in the source provided, say so plainly "
                 "(it may live in a file that wasn't retrieved — name what you'd need). Concise.\n"
                 f"REPO FILE-LIST (for orientation — these files exist): {orient}")
        ans = client.complete(transport.openai_transport(base_url=cfg["base_url"], timeout=fcfg.DEFAULT_CLOUD_TIMEOUT),
                              [{"role": "system", "content": sys_p},
                               {"role": "user", "content": f"SOURCE:\n{context}\n\nQUESTION: {query}"}],
                              model=cfg["model"])
        return {"answer": ans, "sources": sources}

    # --- model-/provider-AGNOSTIC action mapping -------------------------------------------------
    # The requirement (Tim): the RHM must ACT regardless of which model/provider is selected, and a
    # NEW model must "just work". The RHM now acts through NATIVE TOOL-CALLING — chat() feeds each
    # tool_call's {name, arguments} through `_json_obj_to_action` (below) to the SAME dispatcher dict
    # the gate already takes. There is no prose-parsing step: the old `ACTION:`-line / `<invoke>` /
    # fenced-json / bare-json TEXT-shape parser cluster (_parse_rhm_action + _normalise_rhm_action +
    # _strip_provider_delims + _PROVIDER_DELIMS) has been RETIRED — chat() never used it once it moved
    # to native tools. The mapper is shape-recognition ONLY: it does NOT whitelist (that would be a
    # second whitelist that drifts from the dispatcher's — AGENTS.md rule 3). The ONE whitelist lives
    # in `_dispatch_rhm_action` (RHM_VERBS), so a forbidden verb mapped here is REFUSED there (the E6
    # no-bypass guarantee, proven end-to-end via chat() in rhm_action_parse_acceptance.py).

    @classmethod
    def _json_obj_to_action(cls, obj: dict, verb: str):
        """Normalise a JSON tool-call object → the dispatcher dict. The args may be a nested
        `arguments`/`args`/`input` dict (OpenAI/Anthropic style) OR fields on the object itself
        (the fenced `{"verb":..,"targets":..}` style). Either way it routes through the ONE
        normaliser, so the same intent yields the same action across shapes."""
        import json as _j
        verb = (verb or "").strip().lower()
        a = obj.get("arguments") or obj.get("args") or obj.get("input") or {}
        if isinstance(a, str):                                 # arguments serialised as a JSON string
            try:
                a = _j.loads(a)
            except Exception:
                a = {}
        merged = {**({k: v for k, v in obj.items() if k not in ("verb", "name", "tool")}), **(a if isinstance(a, dict) else {})}
        if verb == "build":
            steps = merged.get("steps") or merged.get("pipeline") or merged.get("json")
            return {"verb": "build", "steps": steps if isinstance(steps, list) else None}
        if verb == "consult":
            return {"verb": "consult", "query": str(merged.get("query") or merged.get("question") or "").strip()}
        if verb == "show":
            t = merged.get("targets") or merged.get("target") or []
            t = [t] if isinstance(t, str) else list(t or [])
            return {"verb": "show", "targets": [str(x) for x in t]}
        if verb in ("propose", "panel", "extend"):
            return {"verb": verb, "name": str(merged.get("name") or "").strip(),
                    "spec": str(merged.get("spec") or merged.get("description") or "").strip()}
        if verb == "run":
            return {"verb": "run"}
        if verb == "request_change":
            # the change description (accept a few synonyms a model might emit) + the optional target
            # (the ui:// element/scope, or a named element). Both normalised to clean strings; the
            # address-resolution tiers + the ASK live in the dispatcher (not here — this is shape-only).
            return {"verb": "request_change",
                    "change": str(merged.get("change") or merged.get("description")
                                  or merged.get("spec") or merged.get("text") or "").strip(),
                    "target": str(merged.get("target") or merged.get("address")
                                  or merged.get("element") or "").strip() or None}
        return {"verb": verb}

    # --- I3: propose-affordance — the CONSENT gate (click #2 of the two-click model) ----------
    # NET-NEW (seams-rhm Seam 2 REFUTE): today the system is EXECUTE-then-render — a verb runs inside
    # chat() and the FE renders the OUTCOME (App.tsx r.action.did). There is no "proposed action
    # awaiting a click" affordance. I3 adds one WITHOUT touching that executed path: the RHM may emit a
    # propose-affordance directive — `AFFORD: <verb> <address> [<args-json>]` — which chat() recognises
    # and returns as a structured `proposal` field, and which DOES NOT DISPATCH. The action runs ONLY
    # when the operator approves the rendered card → /api/act (Suite.act, the I2 endpoint). This is the
    # whole point: proposing must not execute (the see-and-approve consent gate, criteria line 99/107).
    #
    # WHY A SEPARATE KEYWORD (`AFFORD:`), not `PROPOSE:` — `propose` is already an RHM verb meaning
    # "draft a NEW node-type → inbox" (the propose/panel/extend inbox path the task warns NOT to confuse
    # this with). `AFFORD:` is the propose-affordance directive; its `<verb>` may itself be ANY RHM verb
    # (incl. `propose`), so a muddled keyword would be a real bug.
    #
    # WHY A SEPARATE PARSER (not folded into _parse_rhm_action) — _parse_rhm_action feeds the
    # EXECUTE-then-render dispatch; widening it would risk auto-running a proposal (consent-gate failure)
    # and would entangle the preserved path. This parser is recognition-only and returns a proposal the
    # caller hands BACK to the FE, never to the dispatcher.
    #
    # WHY NO SECOND WHITELIST HERE — AGENTS.md rule 3 (one source): the verb is NOT filtered at parse
    # time (that would be a second list drifting from the dispatcher's RHM_VERBS). The ONE governance
    # gate is /api/act → _dispatch_rhm_action's refuse-tail (the 7-verb whitelist + no-self-apply), which
    # the approve click reuses unchanged. The model is fed the real RHM_VERBS + the ui:// vocabulary in
    # _chat_context, so it proposes from truth; a bad verb is refused loudly at the click, not silently
    # dropped here. We DO grammar-validate the address (parse_ui_address, the S0 gate `annotate` uses) so
    # a malformed locus fails fast rather than rendering an un-resolvable card — but a NON-ui:// locus
    # (e.g. a bare canvas node-id, which `show`/`act` accept) is carried through untouched.
    _AFFORD_RE = None   # compiled lazily (see _parse_rhm_proposal)

    @classmethod
    def _parse_rhm_proposal(cls, reply: str):
        """Split a reply into (shown_text, proposal|None). A proposal is the propose-affordance directive
        `AFFORD: <verb> <address> [<args-json>]` (anchored to the start of a line, found anywhere —
        same anchoring discipline as the ACTION: handler so prose merely MENTIONING 'AFFORD:' mid-
        sentence does not over-trigger). On a match it RETURNS a structured `{verb, address, args}`
        proposal AND strips the directive from the shown prose (so the raw directive never leaks to the
        operator). On no match → (reply, None). This NEVER dispatches — it only recognises.

        The proposal dict mirrors Suite.act's signature ({verb, address, args}) so an approve→/api/act
        fires faithfully for ANY verb, not just `show` (act() is verb-shaped: show→targets, consult→
        query, build→steps — _act_dict adapts; the args travel here to feed it)."""
        import re, json as _j
        if not reply or not reply.strip():
            return reply, None
        if cls._AFFORD_RE is None:
            cls._AFFORD_RE = re.compile(r"^[ \t]*AFFORD:\s*(.+)$", re.MULTILINE | re.IGNORECASE)
        m = cls._AFFORD_RE.search(reply)
        if not m:
            return reply, None
        body = m.group(1).strip()
        shown = (reply[:m.start()] + reply[m.end():]).strip()
        # body = "<verb> <address> [<args-json>]". Split off the verb, then the address; whatever
        # remains (if it parses as a JSON object) is the args. Address is the first whitespace token
        # after the verb; if it begins a JSON object, there is no address (verb-only proposal, e.g. run).
        verb, _, rest = body.partition(" ")
        verb = verb.strip().lower()
        rest = rest.strip()
        address = None
        args: dict = {}
        if rest.startswith("{"):
            # no address — the remainder is args-json (e.g. `AFFORD: build {"steps":[...]}`)
            try:
                parsed = _j.loads(rest)
                if isinstance(parsed, dict):
                    args = parsed
            except Exception:
                args = {}
        elif rest:
            address, _, tail = rest.partition(" ")
            address = address.strip() or None
            tail = tail.strip()
            if tail.startswith("{"):
                try:
                    parsed = _j.loads(tail)
                    if isinstance(parsed, dict):
                        args = parsed
                except Exception:
                    args = {}
        # A ui:// address is grammar-CHECKED, but consistent with the verb philosophy above (a bad verb
        # rides through and is refused LOUDLY AT THE CLICK, not silently dropped here), a malformed
        # model-emitted address must NOT kill the whole turn (which would 400 it and lose the prose
        # answer — model output is unreliable, unlike `annotate`'s operator-supplied address). So a
        # grammatically-malformed ui:// → DROP the proposal and keep the prose (no card to approve);
        # a well-formed-but-unregistered address rides through and fails loud at the click
        # (resolveUiTarget / the dispatcher validate at act-time). A non-ui:// locus (bare canvas
        # node-id) passes through untouched — show/act accept both.
        if address and address.startswith("ui://"):
            from contracts.ui_info import parse_ui_address
            try:
                parse_ui_address(address)                      # grammar check only (S0)
            except Exception:
                # malformed locus → no card, but STILL strip the directive from the shown prose (the
                # operator must never see a raw `AFFORD:` line). Return the stripped text + no proposal;
                # chat() then renders the prose answer alone (the turn is not killed).
                return shown, None
        proposal = {"verb": verb, "address": address, "args": args}
        return shown, proposal

    @staticmethod
    def _confirmation_for(outcome: dict) -> str:
        """Fold a dispatched verb's outcome dict → ONE concise operator-facing confirmation line, for
        EVERY verb (run/build/show/propose/panel/extend/consult/ask + refused). Before this, only
        consult/ask folded an outcome; run/build/show/propose/panel/extend executed but returned a BLANK
        reply — worst for native-tool-call models that emit no prose. The operator must ALWAYS see what
        happened (rule 4: no silent success). Returns '' only for a None/empty outcome (nothing dispatched).
        consult's full answer is folded by the caller (it carries the looked-up text); here we don't
        duplicate it — '' so the caller's answer-fold stands alone."""
        if not outcome:
            return ""
        did = outcome.get("did")
        if did == "run":
            return f"▶ ran: {len(outcome.get('ran', []))} ran, {len(outcome.get('cached', []))} cached"
        if did == "build":
            if outcome.get("error"):
                return (f"build failed: {outcome['error']}"
                        + (f" (made {len(outcome.get('nodes', []))} before failing)" if outcome.get("nodes") else ""))
            nodes, edges = outcome.get("nodes", []), outcome.get("edges", [])
            wired = (" (" + ", ".join(edges) + ")") if edges else ""
            return f"＋ built {len(nodes)} node(s){wired}"
        if did == "show":
            return "→ moved your view to " + ", ".join(outcome.get("targets", []))
        if did == "propose":
            return f"drafted node '{outcome.get('name')}' — awaiting your approval in the inbox"
        if did == "panel":
            return f"drafted panel '{outcome.get('name')}' — awaiting your approval in the inbox"
        if did == "extend":
            return f"authored UI component '{outcome.get('name')}' (build-gated) — awaiting your approval"
        if did == "request_change":
            # CONVO→SELF-BUILD BRIDGE: a build-intent was SURFACED for approval — nothing built yet.
            scope = outcome.get("scope") or []
            scope_note = (" (scope: " + ", ".join(scope) + ")") if scope else \
                         " (no resolvable code scope yet — DENY-ALL until the address maps to code)"
            return (f"I've surfaced a build-intent to change {outcome.get('address')}{scope_note} — "
                    f"approve it in the inbox to build; nothing runs until you do.")
        if did == "ask_target":
            # the change could NOT be confidently scoped → the verb ASKED rather than guessing (rule 8).
            return outcome.get("ask") or ("Which element should this change apply to? I won't guess a scope.")
        if did == "surfaced_for_approval":
            # I4: the click hit an address whose governance tier is CONFIRM/LOCKED — the command was
            # SURFACED for see-and-approve and did NOT act (no silent success, rule 4).
            return (f"⏸ '{outcome.get('verb')}' at {outcome.get('address')} needs approval "
                    f"(tier: {outcome.get('tier')}) — surfaced for you in the inbox, not yet acted")
        if did == "consult":
            return ""                                         # the caller folds the full answer text
        if did == "ask":
            return ""                                         # the caller folds the ❓-needs line
        if did == "none":
            return "show refused: " + outcome["refused"] if "show" in str(outcome.get("refused", "")) \
                   else "couldn't do that: " + str(outcome.get("refused", "no effect"))
        return ""                                             # unknown did → nothing to confirm

    def _dispatch_rhm_action(self, action: dict, graph_id: str) -> dict:
        """Execute ONLY whitelisted verbs. Anything else is refused with no effect — this is the
        no-bypass guarantee: the RHM cannot apply/delete/write, only propose (surfaces) or run (AUTO)."""
        verb = (action or {}).get("verb")
        if verb == "run":
            r = self.run(graph_id)
            return {"did": "run", "ran": sorted(r["ran"]), "cached": sorted(r["skipped"])}
        if verb == "propose":
            name, spec = action.get("name"), action.get("spec")
            if name and spec:
                p = self.propose_node(name, spec)        # surfaces for OPERATOR approval (CONFIRM)
                if p.get("needs"):
                    return {"did": "ask", "surfaced": p["id"], "needs": p["needs"]}
                return {"did": "propose", "surfaced": p["id"], "name": name}
            return {"did": "none", "refused": "propose needs '<name> :: <spec>'"}
        if verb == "consult":
            q = action.get("query") or ""
            if not q:
                return {"did": "none", "refused": "consult needs a query"}
            return {"did": "consult", "answer": self.consult(q)["answer"]}
        if verb == "show":
            # attention-direction (magic-camera): a VIEW directive — moves the operator's view,
            # mutates NOTHING (view-only — preserved). Three target forms, all validated so we never
            # point at nothing; validated targets pass through UNCHANGED for the UI lane's resolver:
            #   • bare node-id            → live node on the canvas (existing behavior, kept)
            #   • ui://canvas/<id|*>      → camera path (a node-id, or '*' = the whole canvas)
            #   • ui://<chrome|field|panel|ext>/<ref> → a UI-component in the registry (build_ui_info)
            ids = {n.id for n in self._load(graph_id).nodes}
            reg = None                                          # the ui:// registry, lazily built once
            # LENIENT bare-target grounding: the RHM is told the vocabulary (in _chat_context) but a
            # native-tool-call model still often emits a bare handle ("inbox") rather than the full
            # ui://chrome/inbox. So a bare word that matches a UI_REGISTRY handle resolves to its FULL
            # ref USING THE REGISTRY ENTRY'S OWN KIND (not assumed) — never hardcoded. We refuse ONLY on
            # a genuine no-match (fail-loud preserved). Built from UI_REGISTRY so it can't drift.
            handle_map = {ref: kind for ref, kind, *_ in self.UI_REGISTRY}   # 'inbox'→'chrome', '*'→'canvas'
            targets = []
            for t in action.get("targets", []):
                if t.startswith("ui://"):
                    kind, _, ref = t[len("ui://"):].partition("/")
                    if kind == "canvas":
                        # camera-resolved: a live node-id, or '*' = the whole canvas (registry entry). This
                        # gate is LIVE-NODE-scoped on PURPOSE (the FE can only drive the camera to a node
                        # actually on the loaded graph) — it must stay so. NOTE a corpus element row like
                        # ui://canvas/node IS a build_ui_info key, so it must NOT be matched by the
                        # full-string element check below (that would bypass this live-node gate and emit a
                        # target the FE can't drive). Keeping the element check INSIDE the else branch
                        # ensures canvas addresses ALWAYS pass through this gate (preserved).
                        if ref == "*" or ref in ids:
                            targets.append(t)
                    else:
                        # registry-resolved (chrome/field/panel/ext + the S1 ELEMENT addresses):
                        # build_ui_info() keys BOTH the bare region handles ('inbox') AND the full-string
                        # element rows (ui://toolbar/run, ui://inbox/build-review — see
                        # _load_corpus_element_addresses). Match EITHER:
                        #   • t in reg   — C3 FIX: an ELEMENT-level (S1) address keyed by its FULL canonical
                        #     string. Before this, the parse below keyed on the <element> SEGMENT ('run'),
                        #     which is NOT a registry key, so element addresses were silently refused even
                        #     though they ARE registered + drivable. A full-string match passes through
                        #     UNCHANGED for the FE's resolveUiTarget (validates against /api/ui_info = the
                        #     same build_ui_info). The canonical dual-grammar (live kind-form
                        #     ui://chrome/inbox AND corpus region-form ui://inbox/build-review) both conform (S0).
                        #   • ref in reg — the EXISTING region kind-form (ui://chrome/inbox → ref 'inbox' is
                        #     a bare registry key). Kept exactly as before.
                        # Fail-loud preserved: neither key present → not appended → the refuse-tail fires.
                        if reg is None:
                            reg = self.build_ui_info()
                        if t in reg or ref in reg:
                            targets.append(t)
                elif t in ids:
                    targets.append(t)                           # bare node-id (kept)
                elif t in handle_map:
                    # LENIENT: a bare UI handle ('inbox') → its full ref via the registry's own kind.
                    # 'canvas' kind is the whole-canvas '*' camera ref; chrome/etc become ui://<kind>/<ref>.
                    k = handle_map[t]
                    targets.append("ui://canvas/*" if (k == "canvas" or t == "*") else f"ui://{k}/{t}")
            if not targets:
                return {"did": "none", "refused": "show: no matching target (node-id or ui:// component)"}
            return {"did": "show", "targets": targets}
        if verb == "panel":
            # update the interface through the interface: author a DECLARATIVE panel → surfaced
            # (CONFIRM, operator approves → git-committed). Not arbitrary code; not self-applied.
            name, spec = action.get("name"), action.get("spec")
            if name and spec:
                p = self.propose_panel(name, spec)
                if p.get("needs"):
                    return {"did": "ask", "surfaced": p["id"], "needs": p["needs"]}
                return {"did": "panel", "surfaced": p["id"], "name": name}
            return {"did": "none", "refused": "panel needs '<name> :: <spec>'"}
        if verb == "extend":
            name, spec = action.get("name"), action.get("spec")
            if name and spec:
                p = self.propose_extension(name, spec)       # arbitrary code → build-gate → operator approves
                if p.get("needs"):
                    return {"did": "ask", "surfaced": p["id"], "needs": p["needs"]}
                return {"did": "extend", "surfaced": p["id"], "name": name}
            return {"did": "none", "refused": "extend needs '<name> :: <spec>'"}
        if verb == "build":
            # symmetric agency / NL→graph: compose a pipeline on the canvas. Only create_node +
            # connect (AUTO, reversible — exactly what the operator can do), never apply/delete.
            steps = action.get("steps")
            if not isinstance(steps, list):
                return {"did": "none", "refused": "build needs a JSON list of steps"}
            local, made, edges = {}, [], []
            try:
                for step in steps:
                    if "type" in step:
                        nid = self.create_node(graph_id, step["type"], config=step.get("config", {}))
                        local[step.get("as", nid)] = nid
                        made.append(nid)
                    elif "wire" in step:
                        lhs, _, rhs = step["wire"].partition("->")
                        fa, _, fp = lhs.strip().partition("."); ta, _, tp = rhs.strip().partition(".")
                        self.connect(graph_id, local.get(fa, fa), fp, local.get(ta, ta), tp)
                        edges.append(step["wire"])
            except Exception as e:                        # bad type/port → fail the build loudly, no half-claim
                return {"did": "build", "error": f"{type(e).__name__}: {e}", "nodes": made, "edges": edges}
            return {"did": "build", "nodes": made, "edges": edges}
        if verb == "configure":                              # G8.2: the RHM sets its own config (AUTO)
            updates = action.get("updates") or {}
            if not isinstance(updates, dict) or not updates:
                return {"did": "none", "refused": "configure needs a non-empty 'updates' object"}
            cfg = self.set_rhm_config(updates)               # fail-loud on unknown slot/model/role/engine
            return {"did": "configure", "set": sorted(updates.keys()), "config": cfg}
        if verb in ("load_voice", "unload_voice"):           # G8.2: the RHM drives the voice lifecycle (AUTO)
            from voice import lifecycle as _vlc
            svc = action.get("service")
            if not svc:
                return {"did": "none", "refused": f"{verb} needs a 'service' id"}
            try:
                r = _vlc.load(svc) if verb == "load_voice" else _vlc.unload(svc)
            except Exception as e:                           # the lifecycle fail-loud (unknown/won't-fit) → structured, not a crash
                return {"did": verb, "error": f"{type(e).__name__}: {e}"}
            return {"did": verb, **r}
        if verb == "request_change":
            # CONVO→SELF-BUILD BRIDGE: route a conversational change-request into the EXISTING
            # surface_intent_at producer (which mints an intent=="build" item via the wire's UNCHANGED
            # surface_build_intent front door, deriving the code scope from the address per S3). This is
            # the ONLY conversational path to the claude -p self-build wire; the wire-door (/api/build-intent,
            # /api/intent-at) is unchanged, and NOTHING builds until the operator approves the surfaced item
            # via /api/resolve (operator-only, off the MCP face — resolve_surfaced + the approve→dispatch
            # trigger are untouched). REUSE, never reinvent: surface_intent_at composes ingest_comment +
            # resolve_scope + surface_build_intent — we add no parallel intent path.
            change = (action.get("change") or "").strip()
            if not change:
                return {"did": "none", "refused": "request_change needs a 'change' description"}
            # ADDRESS RESOLUTION (the one real design point): (a) the indicated locus the operator
            # pointed at this turn (held backend-side by current_locus(), SET in _chat_context from the
            # widened focus.selected), else (b) the model-supplied target (a ui:// address or a named
            # element matched against the registry), else (c) ASK. resolve_change_target is fail-loud:
            # an unresolvable target NEVER mints a build-intent (rule 8 — no guessed scope).
            resolved = self.resolve_change_target(action.get("target"), indicated=self.current_locus())
            if resolved["source"] == "ask" or not resolved.get("address"):
                # fail-loud, NO fiction: surface NO build-intent; return the ASK so the model voices it.
                return {"did": "ask_target", "ask": resolved["ask"],
                        "candidates": resolved.get("candidates", [])}
            address = resolved["address"]
            # MINT via the EXISTING producer (reused exactly; consequence_class=decision_build — the
            # one AUTO-posture class the wire dispatches on the operator's approve; surface_intent_at
            # derives the scope from the address per S3, empty scope = DENY-ALL). It only SURFACES
            # (resolved=None) — the operator approves via /api/resolve; this method NEVER dispatches.
            try:
                out = self.surface_intent_at(address, change, source="operator",
                                             consequence_class="decision_build")
            except Exception as e:                           # malformed address / corpus error → fail loud, no half-claim
                return {"did": "none", "refused": f"request_change could not surface a build-intent: "
                                                   f"{type(e).__name__}: {e}"}
            return {"did": "request_change", "surfaced": out["id"], "address": address,
                    "scope": out.get("scope", []), "source": resolved["source"],
                    "stale": out.get("stale"), "note": out.get("note") or ""}
        return {"did": "none",
                "refused": f"verb {verb!r} is not permitted from the RHM — only {self.RHM_VERBS} "
                           "(apply/delete/file-write are operator-gated)"}

    # --- G3: the decide-for-me deterministic dispatcher (NO confidence — posture decides) ---
    def autonomous_dispatch(self, action_class: str, do, payload: dict | None = None) -> dict:
        """G3: route an intended action by GOVERNANCE POSTURE alone — the deterministic decide-for-me
        router. `posture(action_class)` (governance.py POLICY) is the ONLY input: there is no
        confidence value, no score, no judgement call. It routes the ACT-vs-SURFACE decision; the
        `do` callable performs it.

          posture == AUTO  → guard(action_class, do)  → ACT (reversible/cheap/internal; run it now)
          else (SURFACE/CONFIRM, incl. every unknown class → CONFIRM, and every LOCKED class which
                posture() can NEVER return AUTO for) → run `do()` — but for an action whose posture is
                CONFIRM, `do` is a GOVERNED verb body whose own action is to SURFACE a consumable draft
                for the operator (propose→code_build, panel→ui_panel, extend→ui_extension; each surfaces
                the GENERATED payload that apply_node/apply_panel/apply_extension consume on approve). So
                the surface is the verb's real, applyable draft — NOT a generic intent-record that
                nothing could later build (that would be silent success — AGENTS.md rule 4).

        WHY running `do()` on CONFIRM does NOT bypass governance: this router is only ever called with
        RHM verbs (run/propose/build/consult/show/panel/extend — the RHM_VERBS whitelist). NONE of them
        apply/delete/write; the CONFIRM ones SURFACE (never apply). apply still requires the operator's
        `is_approved`. So no-self-approve is preserved STRUCTURALLY by the whitelist: no raw-mutation verb
        can reach this path, so `do()` here can only ever surface or run a reversible AUTO op — never
        approve, apply, or mutate real source. A LOCKED class → posture() CONFIRM → the else branch,
        never AUTO (D4/D7 forever-confirm).

        Returns the verb's own outcome dict, tagged `routed_posture` (auto|surface|confirm) for audit."""
        p = posture(action_class)
        out = guard(action_class, do) if p == AUTO else do()
        out = dict(out) if isinstance(out, dict) else {"result": out}
        out["routed_posture"] = p                              # deterministic record: which posture routed it
        return out

    # --- I2: the /api/act emission seam — a DETERMINISTIC human click replaces the model's
    #     unreliable prose-emission for the interactive path (the emission RELOCATION, §21.4#1) ---
    @staticmethod
    def _act_dict(verb: str, address: str | None, args: dict) -> dict:
        """The thin per-verb ADAPTER: turn a click's `{verb, address, args}` into the verb-shaped
        dispatcher dict `_dispatch_rhm_action` expects (it is verb-shaped, NOT uniform-`address`:
        show→targets, propose/panel/extend→name+spec, build→steps, run/consult→query — seams-rhm
        Seam 1). The `address` (the clicked locus, I1) maps onto the verb's natural address slot
        (show's `targets[]`, the existing ui:// vocabulary). UNKNOWN verbs are NOT filtered here —
        the dict is built and handed to the dispatcher, whose refuse-tail (suite.py:1386) enforces
        the 7-verb whitelist + no-self-apply STRUCTURALLY (the no-bypass guarantee rides along for
        free; I2 never widens authority)."""
        action: dict = {"verb": verb}
        if verb == "show":
            # the click's address IS the target; also accept explicit targets[] (multi-select clicks)
            targets = list(args.get("targets") or [])
            if address and address not in targets:
                targets.insert(0, address)
            action["targets"] = targets
        elif verb in ("run",):
            pass                                              # run takes the current graph — no extra args
        elif verb == "consult":
            action["query"] = args.get("query") or args.get("question") or ""
        elif verb in ("propose", "panel", "extend"):
            action["name"] = args.get("name")
            action["spec"] = args.get("spec")
        elif verb == "build":
            action["steps"] = args.get("steps")
        else:
            # unknown/non-whitelisted verb: pass the raw args through; the dispatcher refuses it.
            action.update({k: v for k, v in args.items() if k not in ("verb", "address")})
        if address is not None:
            action.setdefault("address", address)             # carry the locus through for audit (I1)
        return action

    def _tier_for_address(self, address: str | None) -> str | None:
        """I4 — resolve a clicked address → its governance `tier` (an action_class string) from the
        union-record `tier` field carried in the registry row's union-extras (the 6th tuple element).

        ADDRESS-KEYED, not verb-keyed. Returns:
          • the tier action_class string  — if the address is registered AND carries a non-empty `tier`
            (e.g. 'source_data', 'code_build' — a CONFIRM/LOCKED class). The caller routes the click
            through governance by THIS class instead of the verb's own.
          • None — if the address is None, unregistered, or registered-but-untiered. The caller then
            FALLS BACK to the verb's own governance class — so a bare run/build on an untiered (or
            unknown) address stays AUTO and ACTS IMMEDIATELY (U1 preserved, criteria line 153). The
            ABSENCE of a tier is the verb-class fallback; it is NOT the unknown→CONFIRM fail-safe (that
            fail-safe applies to an unknown tier VALUE inside posture(), never to a missing tier).

        Reads the live UI_REGISTRY rows (single source). A row is
        (ref, kind, title, handle, caps[, union-extras]); the 6th element (if present) is the
        union-extras dict carrying `tier`. The 9 bare-region rows have no 6th element → None."""
        if not address:
            return None
        for row in self.UI_REGISTRY:
            if row[0] != address:
                continue
            extras = row[5] if len(row) > 5 else {}
            tier = (extras or {}).get("tier")
            return tier or None                                 # empty-string tier reads as untiered
        return None                                             # address not registered → verb-class fallback

    def act(self, verb: str, graph_id: str, address: str | None = None,
            args: dict | None = None) -> dict:
        """I2 — the operator-face emission seam (the parallel-to-chat() entry to the SAME dispatcher).

        A human click ships a STRUCTURED `{verb, address, args}` — never prose — and this constructs
        the final dispatcher dict directly, BYPASSING the unreliable model-prose parse
        (`_parse_rhm_action`, the narration-prone step this exists to relocate, suite.py:1140). It
        then drives `_dispatch_rhm_action` (suite.py:1287) through the SAME governance posture routing
        chat()'s decide-for-me path uses (`autonomous_dispatch`), and re-folds the SAME operator
        confirmation chat() folds — so the operator always sees "did X" (rule 4: no silent success),
        and consult/ask get their richer folds too (not just the else-branch).

        Re-fold #1 — GOVERNANCE: the verb's action-class routes through `autonomous_dispatch`
          (suite.py:1391): AUTO verbs (run/build/show/consult) act now; CONFIRM verbs
          (propose/panel/extend) run their body whose action is to SURFACE a draft for operator
          approval — they NEVER self-apply. The 7-verb whitelist + no-self-apply ride along INSIDE
          the dispatcher (RHM_VERBS suite.py:952; refuse-tail suite.py:1386). I2 inherits exactly the
          RHM's permitted set — a click cannot widen authority.
          (NOTE: I4 will key the tier by ADDRESS on top of this; I2 folds the verb-class posture that
          already lives in chat(), not I4's address→tier lookup.)
        Re-fold #2 — CONFIRMATION: `_confirmation_for` (suite.py:1250) returns "" for consult/ask by
          design (chat() folds those separately at suite.py:1501); so act() replicates chat()'s FULL
          fold, not the else-branch alone — else a consult/ask click is a silent success.

        Returns the same `{reply, action}` shape /api/chat returns."""
        args = dict(args or {})
        action = self._act_dict(verb, address, args)
        # I4 — ADDRESS-KEYED governance gate (FIRST, before the verb-class posture). A click resolves
        # to (verb, address); the CLICKED ADDRESS — not the verb — decides the tier. If the address
        # carries a CONFIRM/LOCKED tier in its union record, the click PROPOSES (surfaces for see-and-
        # approve) and does NOT act; absent an address tier it falls through to the verb's own class
        # below — so a bare run/build (no address, or an untiered/AUTO address) stays AUTO and ACTS
        # IMMEDIATELY (U1 preserved, criteria line 153).
        addr_tier = self._tier_for_address(address)
        if addr_tier is not None and posture(addr_tier) != AUTO:
            # The address's tier is CONFIRM/SURFACE/LOCKED → SURFACE the command for the operator and
            # RETURN WITHOUT dispatching. We MUST NOT route this through autonomous_dispatch: its
            # non-AUTO branch calls do() directly (suite.py autonomous_dispatch), and for a `run` verb
            # do() EXECUTES the graph — that would be the inverse U1 regression (a CONFIRM-tier run
            # running). Surfacing here keeps the dispatcher (and thus any execution) untouched until
            # the operator approves (the approve→re-dispatch wire is I3, not this unit).
            # L8 (§21.7#9): this surfaced approval IS the canonical click-to-thing case — it concerns
            # the very address the operator clicked (gated CONFIRM/LOCKED). The GUIDE: "if the item
            # already has an address/locus, USE it." So carry that address as the navigable ui:// target
            # inside payload (the open bag — seams-engine Seam 2), so clicking the inbox item drives the
            # view back to the element awaiting approval via the preserved resolveUiTarget keystone. The
            # address reached here only by matching a registered UI_REGISTRY row in _tier_for_address, so
            # it is ALWAYS a ui:// form (navigable); we still gate on the ui:// prefix (mirror the resolver
            # grammar — a non-ui:// string would fail driveCanvas) so a malformed/absent locus simply
            # carries no target and the item behaves exactly as today (no navigation, not an error).
            i4_payload = {"verb": verb, "address": address, "args": args, "graph_id": graph_id}
            if isinstance(address, str) and address.startswith("ui://"):
                i4_payload["ui_target"] = address
            sid = self.inbox.surface(addr_tier, i4_payload, default="reject", resolved=None)
            outcome = {"did": "surfaced_for_approval", "verb": verb, "address": address,
                       "tier": addr_tier, "surfaced": sid, "routed_posture": posture(addr_tier)}
            return {"reply": self._confirmation_for(outcome), "action": outcome, "graph_id": graph_id}
        # GOVERNANCE re-fold (verb-class fallback — the address is untiered/AUTO/None): route by the
        # verb's action-class (the same posture routing chat()'s decide-for-me path uses). Not
        # mode-gated — a deterministic click is not subject to the RHM presence dial; and it is safe
        # regardless, since every RHM verb is AUTO or a CONFIRM that only SURFACES (autonomous_dispatch
        # never calls guard() for a non-AUTO class, so nothing raises and propose/panel/extend still
        # only surface). Unknown verb → safest class (CONFIRM).
        cls = self.RHM_VERB_CLASS.get(verb, "register_type")
        outcome = self.autonomous_dispatch(cls, do=lambda: self._dispatch_rhm_action(action, graph_id),
                                           payload=action)
        # CONFIRMATION re-fold (mirror chat() suite.py:1501–1509): consult folds its full answer; ask
        # folds its needs-line; every other verb (incl. refused → did=="none") folds _confirmation_for.
        if outcome and outcome.get("did") == "consult":
            reply = "📖 " + outcome["answer"]
        elif outcome and outcome.get("did") == "ask":
            reply = ("❓ That needs something not in the registry, so I'm asking rather than guessing: "
                     + outcome["needs"] + " — surfaced for you in the inbox.")
        else:
            reply = self._confirmation_for(outcome)
        return {"reply": reply, "action": outcome, "graph_id": graph_id}

    def route_click(self, address: str | None, graph_id: str, verb: str | None = None,
                    text: str | None = None, args: dict | None = None,
                    source: str = "operator") -> dict:
        """I5 — the annotate-vs-operate ROUTER: ONE classifier that decides, per click, whether the
        click attaches a COMMENT (annotate, I6) or proposes/runs an OPERATION (operate, I2/I4/I3) —
        and NEVER blurs the two. It COMPOSES `act` (which carries I4's address→tier gate inside) and
        `annotate` (I6); it does NOT re-implement or weaken either.

        THE ROUTING DISTINCTION (criteria line 109; Implementation Guide I5):
          • the SCHEME is a ROUTING HINT, not the safety gate (design-substrate CONTRACT.2, Verified):
              - `ui://`  = a DESIGN/UI element.  A `ui://` click with NO consequential verb → ANNOTATE.
              - `run://` = a LIVE graph-node instance.  A `run://` click → OPERATE (always).
          • a consequential VERB at ANY address → OPERATE (a verb makes it an operation regardless of
            scheme — e.g. the camera-driving `show` on a `ui://` element stays on the operate face).
          • what GATES a mutating command is NOT the scheme — it is the address's governance TIER
            (`_tier_for_address` → CONFIRM/LOCKED) + `guard()`, REUSED unchanged inside `act`. So:
              - bare / untiered / unknown address + an immediate verb → ACTS IMMEDIATELY (U1 preserved).
              - a CONFIRM/LOCKED-tier address + a consequential verb → PROPOSES (surfaces), never runs.
              - a `ui://` element that resolves to a read-only-driveable target keeps working read-only
                via the live `show` path (`show` is AUTO → operate → drives the camera; not blocked).

        FAIL-LOUD over silent (rule 4): an annotate route with empty text RAISES (never a silent no-op
        and never a silent dispatch); `annotate` itself raises on a non-`ui://` (run://) address, so a
        live instance is STRUCTURALLY incapable of being commented — half of "never blur" for free.

        Returns a tagged dict:
          • annotate face → {"face": "annotate", "annotation": <rec>, "action": None, "graph_id": …}
          • operate  face → {"face": "operate",  **act(...)}  (the same {reply, action, graph_id} shape)
        The `face` tag is the never-blur marker: an annotate route never carries an `action`; an operate
        route never carries an `annotation`."""
        args = dict(args or {})
        has_verb = bool(verb and str(verb).strip())
        is_run_scheme = isinstance(address, str) and address.startswith("run://")
        # OPERATE if there is a consequential verb OR the address is a live graph-node instance.
        # ANNOTATE only when there is NO verb AND the address is a UI/design element (the ui:// hint).
        if has_verb or is_run_scheme:
            # OPERATE — hand to act(), which applies I4's ADDRESS→TIER gate FIRST (CONFIRM/LOCKED →
            # propose/surface; bare/untiered/AUTO → act immediately, U1 preserved), then the verb-class
            # governance posture. The 7-verb whitelist + no-self-apply ride along inside the dispatcher.
            # A run:// click with no verb defaults to `run` (the natural verb for a live instance).
            v = str(verb).strip() if has_verb else "run"
            out = self.act(v, graph_id, address=address, args=args)
            out["face"] = "operate"
            return out
        # ANNOTATE — a ui:// element click with no verb attaches a comment at the address (I6). FAIL
        # LOUD if there is no text: never silently dispatch and never a silent no-op (rule 4). `annotate`
        # validates the address against the S0 grammar and RAISES on a non-ui:// (run://) address.
        if not text or not str(text).strip():
            raise ValueError(
                "I5 annotate route needs non-empty text (a ui:// element click with no verb attaches a "
                "comment — supply text, or pass a verb to OPERATE). Fail loud — no silent no-op, no "
                "silent dispatch.")
        # L4 — compose the COMMENT-INGEST entry (`ingest_comment`): the pure I6 `annotate()` PLUS the
        # one additive located-gold `append_chat` (§21.7#7, seams-rhm Seam 5). The same wired entry the
        # FE's `/api/annotate` route uses — single-source, so a clicked comment IS the twin's located
        # gold label whether it arrives via the I5 classifier (here) or the direct annotate API.
        rec = self.ingest_comment(address, str(text), source=source)
        return {"face": "annotate", "annotation": rec, "action": None, "graph_id": graph_id}

    def annotate(self, address: str, text: str, source: str = "operator") -> dict:
        """I6 — attach a comment / annotation to a `ui://` address (the `annotation://` content branch).

        NET-NEW and SEPARATE from `/api/resolve`'s comment choice (which annotates a surfaced item by
        `id`, not an arbitrary address — suite.py:3045) and from the I2 act path. Nothing else attaches
        by ADDRESS today.

        S0 GATE FIRST: `parse_ui_address` validates the address against the ONE canonical grammar and
        RAISES on a malformed `ui://` (fail-loud, rule 4) — so the store never persists a junk key, and
        the bridge's try/except turns the raise into a 400 for free. Validation lives HERE (the Suite
        semantic layer), matching where `act` does its work; the store leaf stays dumb.

        Then persist via the open-record store leaf (`append_annotation`), keyed by `address`. The
        annotation is retrievable by `annotations_at(address)`. This feeds R2 (address-keyed context
        resolution): info attached to an address auto-resolves into the RHM context at that locus, and
        the `ts` stamped by the store leaf gives R2's relevance/recency decay its clock.

        Fail loud on empty text (no silent no-op — rule 4)."""
        from contracts.ui_info import parse_ui_address
        parse_ui_address(address)                            # S0 grammar gate (raises on malformed)
        if not text or not str(text).strip():
            raise ValueError("annotate needs non-empty text (fail loud — no silent no-op)")
        rec = self.store.append_annotation(
            {"kind": "annotation", "address": address, "text": str(text).strip(), "source": source})
        # S2: emit an addressed event so the comment is visible on the live stream at its locus.
        self._emit("annotation", f"comment at {address}: {rec['text'][:40]}", address=address)
        return rec

    def ingest_comment(self, address: str, text: str, source: str = "operator") -> dict:
        """L4 — the COMMENT-INGEST entry point (§21.7#7, seams-rhm Seam 5): an addressed comment IS the
        twin's *located* gold label. This is the ONE wired entry a clicked comment flows through (the
        FE's `/api/annotate` route → `bridge.py` → here; and the I5 router's annotate branch composes it
        too). It does TWO things, in order:

          1. the pure I6 `annotate()` (records the comment on its OWN `annotations.jsonl` branch — that
             leaf stays byte-for-byte pure so I6's SEPARATION preserve holds: `annotate()` itself NEVER
             writes chat — `annotation_acceptance.py` asserts `chat_history()==[]` after a bare annotate);
          2. ONE additive `append_chat` (the located gold label): the existing OPEN `{ts, **turn}` record
             (`fs_store.py:357`) carries the `address` verbatim, so the comment flows the EXISTING
             `append_chat → training_signal` pipe — NO new training pipeline, NO parallel store — and
             surfaces in `training_signal` as a LOCATED gold label automatically (echo-guarded).

        WHY a separate ingest method (not folded into `annotate`): the default lean (make `annotate()`
        itself emit the gold turn) is impossible — `annotation_acceptance.py:131-132` asserts a bare
        `annotate()` writes NO chat (the I6 SEPARATION preserve), an un-editable hard constraint. So
        `annotate()` stays the PURE annotation leaf and the located-gold emit lives ONE layer up, here,
        on the WIRED comment-ingest path — exactly the "comment-ingest entry point that grades as
        operator-gold and stamps the address" seams-rhm:170 named.

        PROVENANCE / F4 (no second grading scheme): the chat turn's role is TIED to `source` via the same
        `_provenance_source`/`_provenance_grade` helpers `attach_chat`/`chat` use — an operator comment
        lands user/gold/operator (trains the twin, LOCATED); ANY non-operator source lands
        assistant/working/twin (NEVER trains, even laundered back — the F4 guard). We write through the
        store leaf DIRECTLY (not `attach_chat`) so we do NOT emit a SECOND addressed event at this locus
        (`annotate` already emitted the addressed `annotation` event for the live stream) — avoids
        double-stamping the addressed history (L3)."""
        rec = self.annotate(address, text, source=source)        # the pure I6 leaf (S0-gated, fail-loud)
        role = "user" if source == "operator" else "assistant"  # role-tied provenance (F4)
        self.store.append_chat({"role": role, "text": str(text).strip(), "address": address,
                                "source": self._provenance_source(role),
                                "grade": self._provenance_grade(role)})
        return rec

    def annotations_at(self, address: str) -> list:
        """I6 — every annotation attached to `address`, oldest-first (the comment thread at that locus).

        The address is VALIDATED first (same S0 gate as `annotate`) so a retrieval on a malformed
        address fails loud rather than silently returning [] (which a caller could read as 'no
        comments'). Reads through the store leaf, which reads disk every call — so this returns a prior
        Suite's writes on the same store root (persistence-survives-reload)."""
        from contracts.ui_info import parse_ui_address
        parse_ui_address(address)                            # S0 grammar gate (raises on malformed)
        return self._overlay_pins(address, self.store.annotations_for(address))

    # ============================================================================================
    # F1 LEARNING LOOP — "how Tim wants <this> presented" (the presentation-preference store + adapt)
    # ============================================================================================
    # Tim's F1 expansion: he must be able to SHAPE how the system presents to him FROM INSIDE the system
    # ("show me this differently / more / less / lead with X"), by voice OR typing, and it must ADAPT +
    # REMEMBER — "how it presents to him is LEARNED." This is the net-new piece of F1. It REUSES, never
    # rebuilds:
    #   • the addressed-feedback substrate — a presentation pref is "a comment at an address" with a
    #     presentation INTENT, so it rides the EXISTING `annotations.jsonl` store leaf (`append_annotation`)
    #     with one additive structured marker (`kind:"presentation_pref"`). NO parallel store (rule 3).
    #     It deliberately rides the PURE `annotate` leaf-shape (S0-gate + fail-loud guards mirrored here),
    #     NOT `ingest_comment` — a presentation pref is a CONTROL signal, not twin gold-training data, so it
    #     stays OUT of the located-gold `append_chat` pipe + the R2 [comment @ addr] framing noise (the
    #     twin's gold corpus + the RHM's framing context stay clean).
    #   • R2 resolve-at-locus — the pref is gathered as its OWN distinct `presentation_pref` stratum (NOT
    #     collapsed into the comment stratum) so a learned pref rides the SAME machinery as everything else,
    #     pin-persistent like the howto leg (a pref doesn't decay).
    #   • the up-translate organs (up_translate / coa / address_help) CONSULT the pref at the address and
    #     APPLY it (the adapt step) — model-free for the structural part (the pref REACHES the framing
    #     input/shape), model-dependent only in the actual WORDING the model emits when honoring it.
    # The chat path (voice OR typing) is the input — that rides the EXISTING `chat()` + `/api/chat`; the
    # capture seam below is what a "present this differently" message records.
    #
    # The pref VOCABULARY (registry-is-truth, rule 8 — a pref-kind not in this set FAILS LOUD, never a
    # silent ignore that the operator would read as "it remembered"). Each is a deterministic presentation
    # intent the adapt step can apply structurally and/or thread into the framing prompt:
    PRESENTATION_PREFS = {
        "terser":    "Present this more tersely — fewer words, the essentials only.",
        "more":      "Present this in more detail — expand, give me the fuller picture.",
        "lead_with": "Lead with {arg} — put that first when presenting this.",
        "shape":     "Present this as {arg} (the shape/form Tim recognises it by).",
    }

    def _validate_presentation_pref(self, pref: dict) -> dict:
        """FAIL LOUD on a malformed preference (rule 4/8 — a junk pref must RAISE, never be silently
        ignored or read as 'no pref', which the operator would misread as 'it remembered'). A valid pref is
        `{kind: <one of PRESENTATION_PREFS>, arg?: <str, REQUIRED for the arg-taking kinds>}`. The
        arg-taking kinds (`lead_with`/`shape`) carry a non-empty `arg`; the bare kinds (`terser`/`more`)
        must NOT carry a meaningful arg-dependence (an arg is tolerated-but-ignored). Returns the
        normalized pref dict (kind + arg-or-None)."""
        if not isinstance(pref, dict):
            raise ValueError(f"presentation pref must be a dict, got {type(pref).__name__} (fail loud)")
        kind = pref.get("kind")
        if kind not in self.PRESENTATION_PREFS:
            raise ValueError(
                f"unknown presentation pref kind {kind!r} — one of {tuple(self.PRESENTATION_PREFS)} "
                "(rule 8: never fabricate/silently-accept a pref kind)")
        arg = pref.get("arg")
        if "{arg}" in self.PRESENTATION_PREFS[kind]:                  # an arg-taking kind
            if not (isinstance(arg, str) and arg.strip()):
                raise ValueError(f"presentation pref {kind!r} needs a non-empty 'arg' (fail loud)")
            return {"kind": kind, "arg": arg.strip()}
        return {"kind": kind, "arg": None}

    def set_presentation_pref(self, address: str, pref: dict, text: str | None = None,
                              source: str = "operator") -> dict:
        """F1 LEARNING LOOP — the CAPTURE seam: record "how Tim wants <this> presented" at `address`.

        Mirrors `annotate`'s GUARDS (it IS the annotate-branch of the addressed-feedback channel, with a
        presentation intent) but carries a STRUCTURED pref so the adapt step is MODEL-FREE:
          • S0 grammar gate FIRST (`parse_ui_address` RAISES on a malformed `ui://` — fail loud, so the
            store never persists a junk key; the bridge's try/except turns the raise into a 400 for free).
          • the pref is VALIDATED (`_validate_presentation_pref` RAISES on an unknown kind / a missing
            required arg — the third distinct fail-loud guard the loop names, beside malformed-address and
            empty-text).
          • persist through the SAME `append_annotation` store leaf (one-source, no parallel store) with
            the additive `kind:"presentation_pref"` marker + the structured `pref` + the human `text`. The
            store is APPEND-ONLY, so an address accrues a pref HISTORY; the consult-read takes the LATEST
            (latest-wins = "remembers the most recent shaping"). Persistence-survives-reload comes free
            (the leaf reads disk every call — a FRESH Suite over the same store root reads Tim's learned
            prefs).
          • emit an addressed `presentation_pref` event so the shaping is visible on the live stream at its
            locus (S2), distinct from the `annotation` event so it is never mistaken for a plain comment.

        `text` defaults to the human form of the pref (so a bare structured capture still records a legible
        comment line). DELIBERATELY does NOT call `ingest_comment` (no gold `append_chat`): a presentation
        pref is a control signal, not twin training gold — keeping it out preserves the twin's gold corpus
        and R2's [comment] framing context (the I6 SEPARATION spirit). `annotate`/`ingest_comment` are
        UNTOUCHED (their contract + `annotation_acceptance` hold)."""
        from contracts.ui_info import parse_ui_address
        parse_ui_address(address)                                    # S0 grammar gate — raises on malformed
        norm = self._validate_presentation_pref(pref)                # fail loud on a malformed pref
        human = self.PRESENTATION_PREFS[norm["kind"]].format(arg=norm.get("arg"))
        rec_text = (text.strip() if (text and text.strip()) else human)
        rec = self.store.append_annotation({
            "kind": "presentation_pref", "address": address,
            "pref": norm, "text": rec_text, "source": source})
        self._emit("presentation_pref",
                   f"present @ {address}: {norm['kind']}" + (f" {norm['arg']}" if norm.get("arg") else ""),
                   address=address)
        return rec

    def presentation_pref_at(self, address: str) -> dict | None:
        """F1 LEARNING LOOP — the CONSULT seam: the ACTIVE presentation pref at `address` (latest-wins), or
        None when none is recorded (a CLEAN absence the adapt step degrades to the DEFAULT framing — never
        an error, never a fabricated pref).

        S0-gated (raises on a malformed address — same gate as the capture/read siblings). Reads the SAME
        `annotations.jsonl` leaf the capture wrote (so a FRESH Suite over the same store root reads it —
        reload-survival), filters for the `presentation_pref` marker, and returns the LAST (most-recent)
        one's structured pref — RE-VALIDATED on read (`_validate_presentation_pref` RAISES on a stored junk
        pref, so a corrupted record fails loud rather than silently degrading to 'no pref'). Generic over
        any address (registry-is-truth) — the SAME 'read context at an address → structured signal' shape a
        future mode auto-detect detector could call (the sibling seam; left clean, not built here)."""
        from contracts.ui_info import parse_ui_address
        parse_ui_address(address)                                    # S0 grammar gate — raises on malformed
        active = None
        for rec in self.store.annotations_for(address):              # oldest-first → last loop = latest-wins
            if rec.get("kind") == "presentation_pref":
                active = rec
        if active is None:
            return None
        return self._validate_presentation_pref(active.get("pref"))  # fail loud on a stored junk pref

    def _apply_presentation_pref(self, bundle: dict, pref: dict | None) -> dict:
        """F1 LEARNING LOOP — the ADAPT step (deterministic / MODEL-FREE) for the address path: thread a
        consulted pref INTO an `address_help`/`up_translate('address')` envelope so the presentation
        REFLECTS Tim's recorded shaping. Returns a NEW dict (never mutates the input — the un-adapted
        bundle stays available; reflects-never-owns).

        No pref → the bundle is returned UNCHANGED (the clean default — no error, no fabrication). With a
        pref it:
          • ATTACHES the structured pref to the envelope (`presentation_pref`) so any surface (the FE F1
            lane — NEXT lane) can render it + a 'learned' marker WITHOUT re-deriving it;
          • applies the pref STRUCTURALLY where the shape allows it model-free (the strongest model-free
            proof): `lead_with:how_to_change` REORDERS the legs so the change-leg leads (a deterministic
            re-shape the operator can SEE in the envelope); `terser`/`more`/`shape` are carried as a
            framing DIRECTIVE on the envelope (`presentation_directive`) that the model honors in WORDING
            (the model-dependent half — flagged) while the MECHANISM (pref recorded → consulted → reached
            the envelope) is proven model-free.
        The DIRECTIVE string is the human form of the pref (the same `PRESENTATION_PREFS` text the prompt
        consumes) — single-source between the FE marker, the prompt thread, and the live stream event."""
        if not pref:
            return bundle
        out = dict(bundle)
        out["presentation_pref"] = pref
        out["presentation_directive"] = self.PRESENTATION_PREFS[pref["kind"]].format(arg=pref.get("arg"))
        # STRUCTURAL adapt (model-free, SEE-able in the envelope): lead_with reorders the address legs.
        if pref["kind"] == "lead_with" and isinstance(out.get("lead"), str):
            arg = (pref.get("arg") or "").lower()
            # the address envelope's drillable MECHANISM is how-to-change; "lead with the change" surfaces
            # a one-line change-lead AHEAD of the what-this-is lead (a deterministic, observable re-shape).
            if arg in ("how_to_change", "how-to-change", "change", "mechanism"):
                htc = out.get("mechanism") or {}
                scope = htc.get("scope") if isinstance(htc, dict) else None
                if scope:
                    out["lead"] = f"[changes: {', '.join(str(s) for s in scope)}]  " + out["lead"]
                    out["led_with"] = "how_to_change"
        return out

    def attach_chat(self, address: str, text: str, role: str = "user", source: str | None = None) -> dict:
        """I7 — attach a chat turn to a `ui://` address (the dropped 4th attach-type, §21.1: the
        `chat://` content branch). The INVERSE of I6: I6 (`annotate`) writes its OWN annotations.jsonl;
        I7 RIDES the EXISTING open `append_chat` record (`rec = {"ts", **turn}`, fs_store.py:357) with
        ONE additive `address` field — NO separate chat store (that would violate one-source; the
        existing chat.jsonl open-record handles it additively — store constitution).

        S0 GATE FIRST: `parse_ui_address` validates the address against the ONE canonical grammar and
        RAISES on a malformed `ui://` (fail-loud, rule 4) — so the store never persists a junk key, and
        the bridge's try/except turns the raise into a 400 for free. Validation lives HERE (the Suite
        semantic layer), matching where `annotate`/`act` do their work; the store leaf stays dumb.

        ECHO-GUARD TAGS (store constitution 'Never write a chat turn without a source'): the turn is
        stamped with `source` + `grade` derived from `role` via `_provenance_source`/`_provenance_grade`
        — so an operator turn lands operator/gold (trains the twin) and an assistant/twin turn lands
        twin/working (NEVER trains, even laundered back). The turn is an ORDINARY chat turn that ALSO
        carries an `address`: it appears in chat_history, flows through training_signal UNCHANGED (the
        `address` rides free — seams-rhm Seam 5), and is retrievable by `chats_at(address)`. The `ts`
        stamped by the store leaf gives R2's relevance/recency decay its clock.

        Fail loud on empty text (no silent no-op — rule 4)."""
        from contracts.ui_info import parse_ui_address
        parse_ui_address(address)                            # S0 grammar gate (raises on malformed)
        if not text or not str(text).strip():
            raise ValueError("attach_chat needs non-empty text (fail loud — no silent no-op)")
        src = source if source is not None else self._provenance_source(role)
        rec = self.store.append_chat({"role": role, "text": str(text).strip(), "address": address,
                                      "source": src, "grade": self._provenance_grade(role)})
        # S2: emit an addressed event so the attached chat is visible on the live stream at its locus.
        self._emit("chat", f"chat at {address}: {rec['text'][:40]}", address=address)
        return rec

    def chats_at(self, address: str) -> list:
        """I7 — every chat turn attached to `address`, oldest-first (the `chat://` thread at that locus).

        The address is VALIDATED first (same S0 gate as `attach_chat`/`annotate`) so a retrieval on a
        malformed address fails loud rather than silently returning [] (which a caller could read as 'no
        chat'). Reads through the store leaf (`chats_for`), which filters the open chat.jsonl by the
        additive `address` field and reads disk every call — so this returns a prior Suite's writes on
        the same store root (persistence-survives-reload). This is what R2 will gather at the operator's
        locus (address-keyed context resolution) — the retrieval R2 consumes; I7 does NOT wire R2."""
        from contracts.ui_info import parse_ui_address
        parse_ui_address(address)                            # S0 grammar gate (raises on malformed)
        return self._overlay_pins(address, self.store.chats_for(address))

    def _overlay_pins(self, address: str, records: list) -> list:
        """X7 — overlay the resolved pin-state onto the records `annotations_at`/`chats_at` return.

        The annotation/chat stores are APPEND-ONLY immutable logs, so the operator's pin override can't
        be written ONTO the existing line; it lives as additive control-state in `pins.jsonl`, keyed by
        the item's `(address, ts)` handle, and is RESOLVED here on read (`pin_state_for`, last-wins). The
        returned records keep their SAME count + text (the overlay only flips an additive `pinned` field —
        annotation_acceptance's count/text assertions stay green); an item with no pin record reads as
        unpinned (schema-additive default). This is the SET-path completion of the dead pin term: the
        gather (`_r2_gather`) already reads `bool(a.get('pinned'))` / `bool(c.get('pinned'))`, so feeding
        the real flag here makes `_r2_score`'s `pin_bonus` reachable — the scoring formula is UNCHANGED.

        Non-mutating to the stored bytes (a shallow per-record copy carries the resolved flag) — the
        store stays immutable. An item whose `ts` has no pin record is returned unchanged-but-for the
        explicit `pinned` default, so every reader sees a uniform shape."""
        pin_state = self.store.pin_state_for(address)
        out = []
        for r in records:
            rr = dict(r)                                     # don't mutate the store's record bytes
            rr["pinned"] = bool(pin_state.get(r.get("ts"), r.get("pinned", False)))
            out.append(rr)
        return out

    def pin(self, address: str, target_ts: str, pinned: bool = True) -> dict:
        """X7 (Convergence) — the SET path for the operator's "keep this in view" override.

        THE DEAD TERM THIS COMPLETES (Research Synthesis, Round 4): `_r2_score` already adds
        `R2_PIN_WEIGHT` when `item.get('pinned')`, and `_r2_gather` already surfaces `bool(a.get('pinned'))`
        — but NOTHING ever set `pinned` True (only the `pinned:False` literals). So the pin_bonus existed
        in the math but was unreachable. `pin` wires the missing set-path: it records a pin/unpin of the
        attached item at (`address`, `target_ts`) so the gather's already-present read picks up the real
        flag → a pinned item holds in the bounded R2 window even when older/farther. The scoring FORMULA
        and `R2_PIN_WEIGHT` are UNCHANGED — only the flag becomes settable.

        OPERATOR-ONLY, OFF the MCP face: this is an operator action (mirrors `annotate`/`attach_chat`,
        surfaced via the operator-face `/api/pin` route). It is NOT in `RHM_VERBS` — the RHM/MCP face
        gains no pin tool (no-bypass preserved).

        IDENTITY: an attached item is addressed by its `(address, ts)` — the `ts` the store stamps and
        `annotations_at`/`chats_at` return is the stable per-record handle. Pin-state persists as an
        additive overlay in `pins.jsonl` (append-only; the annotation/chat logs are immutable, and we
        must not write into `chat.jsonl` — that would pollute the twin training pipe / echo-guard).

        FAIL LOUD (rule 4 — no silent no-op): the address is S0-gated (raises on malformed), and the
        `target_ts` MUST match an existing attached item (annotation OR chat) at that address — pinning a
        non-existent item RAISES rather than silently recording a pin nothing will ever read."""
        from contracts.ui_info import parse_ui_address
        parse_ui_address(address)                            # S0 grammar gate (raises on malformed)
        if not target_ts or not str(target_ts).strip():
            raise ValueError("pin needs a target_ts (the item's handle) — fail loud, no silent no-op")
        # existence guard: the (address, ts) must name a real attached item (annotation or chat).
        existing_ts = {r.get("ts") for r in self.store.annotations_for(address)}
        existing_ts |= {r.get("ts") for r in self.store.chats_for(address)}
        if target_ts not in existing_ts:
            raise ValueError(
                f"pin: no attached item at {address} with ts={target_ts} (fail loud — nothing to pin)")
        rec = self.store.append_pin(address, target_ts, bool(pinned))
        # S2: emit an addressed event so the pin/unpin is visible on the live stream at its locus.
        self._emit("pin", f"{'pinned' if pinned else 'unpinned'} item at {address}", address=address)
        return rec
    def roles(self) -> dict:
        """The MODEL-ROLE registry as a STATUS read — the config lab's source (it NEVER hardcodes the
        role list). For each registered role: its declared contract (label/description/trigger/output/
        tools/context/thinking/knobs) + the current binding + the EFFECTIVE resolution (what would
        actually be used right now). Mirrors available_stt()'s registry-as-status shape."""
        bindings = self.rhm_config().get("roles", {})
        # JSON-safe coercion (this is a STATUS read the bridge json.dumps for /api/roles + the FE config
        # lab consumes): a file-discovered cognition role (G2) carries `output_schema` (a Pydantic model
        # CLASS) + `mode_scope` (a set) — neither is JSON-serializable, so a raw copy 400s the endpoint.
        # Coerce to the FE-USEFUL form: the schema → its renderable json-schema (what an authoring/config
        # surface draws the output fields from); the set → a sorted list. Everything else passes through.
        import json as _json
        def _json_safe(k, v):
            if k == "output_schema" and v is not None and hasattr(v, "model_json_schema"):
                try:
                    return v.model_json_schema()        # the FE-renderable output-field schema
                except Exception:
                    return getattr(v, "__name__", str(v))
            if isinstance(v, (set, frozenset)):
                return sorted(v)                        # mode_scope
            if callable(v):
                return getattr(v, "__name__", str(v))   # verdict_rule (a jury's verdict fn) → its name
            try:
                _json.dumps(v)                          # defensive: a future non-JSON field never 400s
                return v                                #   the status endpoint — it degrades to a string
            except (TypeError, ValueError):
                return str(v)
        out = {}
        for rid, spec in self.ROLE_REGISTRY.items():
            out[rid] = {"id": rid, **{k: _json_safe(k, spec[k]) for k in spec
                                      if k not in ("env_model", "env_url", "env_knobs")},
                        "binding": bindings.get(rid, {}),
                        "effective": self.resolve_role(rid)}
        return out

    def resolve_role(self, role_id: str) -> dict:
        """Resolve a role to the EFFECTIVE {model, base_url, knobs, thinking, output, tools, context}
        actually used when the role fires. Precedence (advisor-set): config BINDING > env override >
        declared default; a None default_model falls to the RHM brain (rhm_config.model). Fail loud on
        an unknown role (registry-is-truth). The role's consuming code (e.g. is_finished_thought) calls
        THIS — so swapping a role's model is a config change, never a code change."""
        import os
        if role_id not in self.ROLE_REGISTRY:
            raise ValueError(f"unknown role {role_id!r} — registered: {sorted(self.ROLE_REGISTRY)}")
        spec = self.ROLE_REGISTRY[role_id]
        cfg = self.rhm_config()
        binding = cfg.get("roles", {}).get(role_id, {})
        model = (binding.get("model") or os.environ.get(spec.get("env_model", ""))
                 or spec.get("default_model") or cfg["model"])               # None default → the brain
        base_url = (binding.get("base_url") or os.environ.get(spec.get("env_url", ""))
                    or spec.get("default_base_url") or cfg["base_url"])
        knobs = dict(spec.get("knobs", {}))                                  # declared defaults
        for k, env_name in (spec.get("env_knobs") or {}).items():           # env override
            if os.environ.get(env_name):
                knobs[k] = type(knobs.get(k, 0))(os.environ[env_name]) if isinstance(knobs.get(k), int) else os.environ[env_name]
        knobs.update(binding.get("knobs", {}))                              # binding wins
        return {"role": role_id, "model": model, "base_url": base_url, "knobs": knobs,
                "thinking": binding.get("thinking", spec.get("thinking")),
                "output": spec.get("output"), "tools": spec.get("tools", []),
                "context": spec.get("context")}

    # --- G2 · C2.3: the mode-scoped CAST + C2.5: the capability-query binding ----------------------
    def cast_for_mode(self, mode: str) -> list:
        """The CAST for a mode (C2.3) — every file-discovered role whose mode_scope includes `mode`.
        An UNKNOWN mode yields an EMPTY cast (never a crash, never a default-fire). The active cast is a
        function of mode (DECISIONS Q2: roles are mode-scoped registry data)."""
        return self.role_registry.cast_for_mode(mode)

    def capability_providers(self) -> dict:
        """C2.5 — the thin capability-registry SEAM a role binds against (role.requires ⊆ provider.provides).

        Returns {provider_id: {model, base_url, provides:[caps]}}. TODAY the Company's only live provider is
        the RESIDENT model read from ops/services.json (the `chat-4b` service) — so the binding resolves
        against ONE provider. The SHAPE is the query (NOT hand-written prose); G8/L-model will POPULATE this
        with the full capability catalog (the model registry by type) — that catalog is the DOWNSTREAM DEP
        (flagged for the lead). The `provides` set here is derived from the resident service's known traits
        (a chat model that serves JSON + tool-calling + is the fast no-think judge pick), registry-grounded.
        """
        import json as _json
        providers = {}
        try:
            with open(self.cognition_services_path()) as f:
                reg = _json.load(f)
            svcs = reg.get("services", reg)
            svc = svcs.get("chat-4b") or {}
            cfg = svc.get("config") or {}
            model = cfg.get("model")
            if model:
                # G8 WIRE (single source): the `provides` set comes from the L-model capability catalog
                # (ops/cli/capabilities.py:provides_for — keyed by model-id, provenance declared/probed/served).
                # ops/cli is stdlib-only with BARE imports + no __init__.py (do NOT add one — it breaks the
                # siblings), so we read the catalog by inserting ops/cli on sys.path for the import only.
                # Fail-soft to the registry-grounded resident traits if the catalog can't be read (never a
                # silent WRONG set — the fallback is the same attested resident traits, documented).
                provides = None
                try:
                    import sys as _sys
                    _opscli = os.path.join(self._repo_root, "ops", "cli")
                    if _opscli not in _sys.path:
                        _sys.path.insert(0, _opscli)
                    import capabilities as _caps  # ops/cli/capabilities.py (bare import)
                    provides = list(_caps.provides_for(model))
                except Exception:
                    provides = None
                if not provides:
                    # fallback = the resident vLLM config's attested traits (registry-grounded, not invented):
                    # chat + json (response_format) + tool-calling (--enable-auto-tool-choice) + fast/no-think.
                    provides = ["chat", "json", "tools", "fast", "no-think"]
                providers[f"resident:chat-4b"] = {
                    "model": model, "base_url": f"http://127.0.0.1:{cfg.get('port', 8000)}/v1",
                    "provides": provides}
        except (OSError, ValueError, KeyError):
            pass
        return providers

    def cognition_services_path(self) -> str:
        return os.path.join(self._repo_root, "ops", "services.json")

    def resolve_role_binding(self, role_id: str) -> dict:
        """C2.5 — resolve a role's model BINDING via the capability QUERY (role.requires ⊆ provider.provides)
        against the live providers. The SHAPE is the query, not hardcoded prose. Fail loud on an unknown
        role; a role whose requires no provider satisfies falls to its declared hard default (the judge's
        None→brain floor) or RAISES. Distinct from resolve_role (which resolves the EFFECTIVE config binding
        incl. the operator's rhm_config override) — this is the capability-derived suitability."""
        if role_id not in self.role_registry:
            raise ValueError(f"unknown role {role_id!r} — registered: {sorted(self.role_registry)}")
        return resolve_binding(self.role_registry[role_id], self.capability_providers())

    def cognition_capabilities(self) -> dict:
        """The cognition registries as a STATUS read (registry-is-truth, exposed in capabilities()): the
        file-discovered roles + each role's facet (fireable/jury/mode_scope/requires), the cast per mode,
        and the juries. So the surface/RHM read WHAT roles exist + which fire in which mode from the
        registry, never a hardcoded list.

        REUSE-DON'T-PARALLEL (L-fe-be): the per-role serialization is the SAME projection
        build_cognition_info uses — both go through contracts.cognition_info._serialize_role, so the
        capabilities() block and the /cognition_info view can NEVER drift into two role serializers
        (Tim's "built like the rest of the system"). This block is the compact STATUS subset; the full
        render-truth (rules/render_hint/thought-shapes/edge-kinds/event-contract) is cognition_info()."""
        from contracts.cognition_info import _serialize_role
        roles = {}
        for rid in sorted(self.role_registry):
            full = _serialize_role(rid, self.role_registry[rid])   # the ONE role serializer (no fork)
            roles[rid] = {k: full[k] for k in
                          ("id", "label", "can_fire", "is_jury", "draws", "mode_scope", "requires")}
        casts = {m: [r.id for r in self.role_registry.cast_for_mode(m)] for m in self.MODES}
        return {"roles": roles, "casts": casts,
                "juries": [r.id for r in self.role_registry.juries()],
                "fireable": [r.id for r in self.role_registry.fireable()]}

    def cognition_info(self) -> dict:
        """C5 (sibling) — SERIALIZE the cognition registries for the live cognition VIEW (the SIBLING of
        object_info(); 06-rendering.md §F#1 names it exactly). Mirrors object_info()/ui_info(): a thin
        method that hands the live registries to the contract serializer (build_cognition_info), which is
        GENERATED FROM the registries — never hand-written — and FAILS LOUD on a key/id disagreement
        (mirrors build_object_info). Served at /api/cognition_info (sibling of /api/object_info).

        DYNAMIC + REUSABLE (Tim's directive): the projection reads the LIVE registries — a role file
        dropped in roles/*.py, a declared rule, an edge-kind, an activation context all appear in the
        projection with no FE code (the ComfyUI generic-renderer pattern, rule 3). The cognition.*
        event-kind EMIT-CONTRACT (what the staged turn emits on /api/stream) ships in the projection so
        the FE (L-fe) binds to a real contract, not an invented one (06 §F#3)."""
        from contracts.cognition_info import build_cognition_info
        from contracts.node_record import EDGE_KINDS
        from runtime import rules as _rules
        from runtime import activation as _act
        # The declared rules registry: the canonical cognition INJECTION_RULE + any AST-shaped rules the
        # cast roles declare (the SAME G3 engine chat_parts/activation use — never a second evaluator).
        from runtime import cognition as _cog
        rules_map: dict = {}
        canon = getattr(_cog, "INJECTION_RULE", None)
        if canon is not None:
            rules_map[canon.id] = canon
        for rid in self.role_registry:
            role = self.role_registry[rid]
            for rspec in (role.spec.get("rules") or []):
                rule = self._rule_from_spec(rspec)               # reuse the Suite's G3 builder (one engine)
                if rule is not None and rule.id not in rules_map:
                    rules_map[rule.id] = rule
        casts = {m: [r.id for r in self.role_registry.cast_for_mode(m)] for m in self.MODES}
        # Cognition Engine WIRING (SUITE-3) — the 6 file-discovered corpus registries + the projection
        # registry now ride the ONE uniform kwarg home the contract serializer (build_cognition_info, the
        # SURFACE/contracts lane) opened for them (each projects the registry's OWN `as_records()` — rule 3,
        # one source, no hand-built list). The contract derives `spaces` from `projections.embeddable()`.
        # Passing them HERE is what makes /api/cognition_info + the MCP cognition_info tool show the 6
        # registries NON-EMPTY (they were [] because the caller didn't pass them — the COGNITION-INFO lane's
        # flagged hand-off). The previous in-lane `info["projections"]`/`info["spaces"]` AUGMENT is now
        # REDUNDANT and removed — the projections= kwarg produces both, collapsing two mechanisms into one.
        info = build_cognition_info(
            roles=self.role_registry,                            # the file-discovered RoleRegistry (dict-like)
            rules=rules_map,
            edge_kinds=EDGE_KINDS,
            thought_shapes=self.THOUGHT_SHAPES,
            activation_contexts=_act.ACTIVATION_CONTEXTS,
            rule_ops=_rules.RULE_OPS,
            destination_kinds=_rules.DESTINATION_KINDS,
            casts=casts,
            node_states=[dict(s, applies_to=list(s["applies_to"])) for s in self.NODE_STATES],
            projections=self.projection_registry,                # → info["projections"] + info["spaces"]
            lifters=self.lifter_registry,
            mark_types=self.mark_type_registry,
            generation_policies=self.generation_policy_registry,
            relation_types=self.relation_type_registry,
            ai_tics=self.ai_tic_registry,
            forms=self.form_registry,
        )
        return info

    def knobs_for(self, model: str | None = None, base_url: str | None = None) -> dict:
        """G8.1 — DYNAMIC knob resolution: the configurable per-request surface for a (loaded) model,
        in the node config_schema SHAPE so the UI renders it with NodeConfigForm + the RHM can read it
        as a tool. `always` knobs always apply; the `tools` knob is PROBED LIVE (endpoint-aware) — its
        default + availability reflect what the model actually supports right now; `declared` knobs
        (thinking/structured-output, not universally probeable) are offered with source='declared'.
        None model/base_url → the current brain. Reuses MODEL_KNOBS (registry-is-truth) — no hardcoding
        in the UI; adding a knob is a catalog row."""
        cfg = self.rhm_config()
        model = model or cfg["model"]
        base_url = base_url or cfg["base_url"]
        out = {}
        for kid, spec in self.MODEL_KNOBS.items():
            entry = {k: v for k, v in spec.items() if k != "applies"}
            applies = spec.get("applies")
            if applies == "always":
                entry.update(available=True, source="always")
            elif applies == "capability" and kid == "tools":
                ok = self._model_supports_tools(model, base_url)     # PROBED live (vllm/ollama/litellm)
                entry.update(default=ok, available=ok, source="probed")
            else:                                                    # declared (can't universally probe)
                entry.update(available=True, source="declared")
            out[kid] = entry
        return {"model": model, "base_url": base_url, "knobs": out}

    def _s2s_models(self) -> list:
        """Probe the HF cache for any downloaded s2s/omni model (the _S2S_HINTS). Returns matching dir
        names — empty = no s2s model present (so the s2s path stays available:false)."""
        import os
        hub = os.path.expanduser("~/.cache/huggingface/hub")
        try:
            return [d for d in os.listdir(hub) if any(h in d.lower() for h in self._S2S_HINTS)]
        except OSError:
            return []

    def voice_paths(self) -> dict:
        """Tier 4 — the swappable voice-path registry as a STATUS read (the config lab's source). Each
        path + whether it's AVAILABLE right now: pipeline always (built); s2s only if an S2S model is on
        disk (probed). `active` = the rhm_config.voice_path slot (default pipeline). Mirrors the
        available_stt()/roles() registry-as-status shape — the UI never hardcodes the path list."""
        s2s_models = self._s2s_models()
        active = self.rhm_config().get("voice_path", "pipeline")
        out = {}
        for pid, spec in self.VOICE_PATHS.items():
            avail = spec["built"] or (pid == "s2s" and bool(s2s_models))
            entry = {"id": pid, "label": spec["label"], "built": spec["built"], "available": avail,
                     "note": spec["note"], "active": pid == active}
            if pid == "s2s":
                entry["models"] = s2s_models
                entry["detail"] = (f"s2s model present: {s2s_models}" if s2s_models
                                   else "no S2S model on disk — download one (Qwen3-Omni/Moshi/GLM-Voice) to enable")
            out[pid] = entry
        return {"paths": out, "active": active}

    def is_finished_thought(self, text: str) -> dict:
        """The voice circuit's SEMANTIC endpoint judge (G1.3): given the utterance heard so far (after a
        VAD pause), is it a FINISHED THOUGHT — fire the turn — or is the operator mid-ramble — keep
        listening? This is the "not a dumb silence timer" lever: a pause alone does NOT end a turn; a
        MODEL judges completeness.

        JUDGE = the 'judge' ROLE in the ROLE_REGISTRY (resolve_role('judge')) — a separate, configurable,
        fast model, NOT the conversational brain. The judge is a utility classifier on the LIVE turn
        path, so a reasoning brain is the WRONG tool: measured 2026-06-05, deepseek-v4-pro (a reasoner)
        needs ~256 tokens to surface a 1-word answer and takes ~6.5s — unusable per pause. The role's
        model/knobs resolve binding > env (COMPANY_JUDGE_*) > declared default (default_model None → the
        brain, which WORKS but is slow until rebound to a fast no-think model). Verdict parses 'finish'
        anywhere (robust to a little thinking).

        Empty/blank text → trivially not finished (no model call). Returns {finished, verdict, text,
        judge_model}. Brain/transport errors PROPAGATE (FabricError) → fail loud; the circuit's explicit
        fallback is the manual push-to-talk toggle SURFACED to the operator, NEVER a silent degrade to a
        silence timer (the rejected design)."""
        from fabric import client, transport
        t = (text or "").strip()
        if not t:
            return {"finished": False, "verdict": "MORE", "text": t, "note": "empty — nothing to end"}
        import time
        r = self.resolve_role("judge")                        # the role registry resolves model+knobs
        cfg = self.rhm_config()
        sys_p = ("You judge ONLY whether a spoken utterance is a COMPLETE THOUGHT the listener should now "
                 "respond to, or whether the speaker is mid-sentence / mid-ramble and likely to continue. "
                 "Answer with EXACTLY one word: FINISHED or MORE. No punctuation, no explanation.")
        msgs = [{"role": "system", "content": sys_p},
                {"role": "user", "content": f'Utterance so far: "{t}"\nFINISHED or MORE?'}]
        t0 = time.monotonic()
        out = client.complete(
            transport.openai_transport(base_url=r["base_url"], timeout=cfg["timeout"]),
            msgs, model=r["model"], max_tokens=r["knobs"].get("max_tokens", 2048),
            temperature=r["knobs"].get("temperature", 0))
        ms = int((time.monotonic() - t0) * 1000)
        verdict = "FINISHED" if "finish" in (out or "").strip().lower() else "MORE"
        # G7 run-record: the judge is on the LIVE turn path — how long it took, on which model, the
        # verdict (the condition that matters for tuning the always-listen feel). Rollups reveal whether
        # the bound judge model is fast enough live (the deepseek-6.5s lesson, measured per use).
        self.emit_run_record("judge", ms, model=r["model"], verdict=verdict, text=t[:240])
        return {"finished": verdict == "FINISHED", "verdict": verdict, "text": t,
                "judge_model": r["model"], "ms": ms}

    # --- conversation threads (S2): new / list / reopen. A thread is a pure CONVERSATION (independent of
    # the canvas graph). The CURRENT thread is held in-memory (single operator, like _current_locus); chat()
    # + the voice paths tag their turns with it. Persisted via the store's chat_threads + the additive
    # thread_id on chat.jsonl turns — one source, back-compatible (no thread = the legacy global stream). ---
    def new_conversation(self, title: str = "") -> dict:
        """Start a fresh conversation: mint + persist a thread record, make it current. Subsequent chat/voice
        turns thread into it. Returns the thread record."""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        tid = "conv-" + now.strftime("%Y%m%d-%H%M%S-%f")     # microsecond → collision-safe id (no uuid dep)
        rec = {"id": tid, "title": (title or "").strip(), "created": now.isoformat(), "last_msg": None}
        self.store.save_chat_thread(rec)
        self._current_thread = tid
        return {"thread_id": tid, **rec}

    def list_conversations(self, limit: int = 30) -> list:
        """The previous conversations, newest-active first — for the reopen list."""
        cur = getattr(self, "_current_thread", None)
        out = []
        for tid in self.store.list_chat_threads():
            t = self.store.load_chat_thread(tid) or {"id": tid}
            out.append({"id": tid, "title": t.get("title", ""), "created": t.get("created"),
                        "last_msg": t.get("last_msg"), "current": tid == cur})
        out.sort(key=lambda r: (r.get("last_msg") or r.get("created") or ""), reverse=True)
        return out[:limit]

    def load_conversation(self, thread_id: str) -> dict:
        """Reopen a conversation: make it current + return its history (the turns that carry its thread_id)."""
        t = self.store.load_chat_thread(thread_id)
        if not t:
            raise ValueError(f"unknown conversation {thread_id!r} — registered: {self.store.list_chat_threads()}")
        self._current_thread = thread_id
        return {"id": thread_id, "title": t.get("title", ""), "history": self.store.chats_in_thread(thread_id)}

    def current_conversation(self) -> str | None:
        return getattr(self, "_current_thread", None)

    # ============================================================================================
    # CONCURRENT COGNITION G4 — chat() refactored into prologue + parameterized part-core + epilogue.
    #
    # R1-FOLD F4 / R2-FOLD H3 (BINDING): chat_parts() can neither LOOP chat() (re-runs the gate, emits
    # N chat events) nor COPY it (forks the brain). So chat()'s body is EXTRACTED into a shared core that
    # BOTH chat() (one part) and chat_parts() (N parts) call:
    #   • _chat_prologue  — ONCE: mode=='off' early-return (4-key) + the fail-loud capability-gate
    #                       refusal (5-key). Both keep their OWN append+emit; neither reaches the
    #                       epilogue. The THREE return shapes stay DISTINCT (off=4 · refusal=5 · normal=7)
    #                       with the provenance asymmetry preserved (off/refusal hardcode gold/twin;
    #                       normal uses _provenance_grade/_source). DON'T normalize.
    #   • _chat_part_core — PER PART, parameterized: assembles _chat_context (ONCE PER PART — it is NOT
    #                       side-effect-free; emits a `warning` on a down endpoint), builds msgs (prior
    #                       parts prefilled for coherence, C4.4), calls client.complete_with_tools VIA
    #                       THE MODULE REF (the monkeypatch seam — never `from fabric.client import
    #                       complete_with_tools`), and runs the tool block ONLY when is_final (C4.5).
    #                       ALL parts route through complete_with_tools (intermediate → tools=[]) so the
    #                       capability-gate/seam check has teeth on every part. Does NOT append history,
    #                       does NOT emit `chat` — the epilogue owns those (once).
    #   • the epilogue    — ONCE (in chat()/chat_parts()): action_field shaping · the SINGLE user+
    #                       assistant append · thread bump · the SINGLE _emit("chat").
    #
    # THE SILENT KILLER (R2-FOLD H3 pt 5): an off/refusal short-circuit must NEVER leak into the core —
    # they are PROLOGUE early-returns, verified independently (tests/chat_parts_acceptance.py patches the
    # seams and asserts BOTH chat() and chat_parts() honor them — no listed rhm_* test catches a leak).
    # react() (a separate client.complete path) is NOT entangled.
    # ============================================================================================

    def _chat_prologue(self, message: str, mode: str, cfg: dict, *, persist: bool = True) -> dict | None:
        """The ONCE-only prologue both chat() and chat_parts() run BEFORE the part-core. Returns an
        EARLY-RETURN dict (and does its own append+emit) when the turn must short-circuit, else None
        (proceed to the part-core). The two short-circuits keep their EXACT distinct return shapes +
        provenance asymmetry — preserving them here is the gate (R2-FOLD H3 pt 2).

        `persist` (default True — every existing caller is UNCHANGED): when False (preview_turn, the
        non-mutating test path) the short-circuit does NOT append to chat.jsonl / emit `chat` — a preview
        must not inject phantom turns into the live conversation + training_signal pipe (AGENTS.md rule 4:
        a 'read-only' affordance that secretly writes is a silent failure)."""
        if mode == "off":                                     # the dial disables the RHM entirely (4-key)
            off = "The right-hand-man is off. Switch a mode on the presence dial to wake me."
            if persist:
                self.store.append_chat({"role": "user", "text": message, "grade": "gold", "source": "operator"})
                self.store.append_chat({"role": "assistant", "text": off, "grade": "working", "source": "twin"})
                self._emit("chat", f"you: {message[:40]} (RHM off)", address="ui://chrome/chat")   # S2: chat organ
            return {"reply": off, "action": None, "mode": mode, "history": self.store.chat_history(40)}
        # CAPABILITY-GATE (before any model call): the RHM acts through NATIVE tools, so the selected
        # model MUST support tool-calling. A non-tool model is a CONFIGURATION error — refuse it FAIL
        # LOUD (rule 4). The gate is an INSTANCE-METHOD CALL ON self (`self._model_supports_tools`) — the
        # rhm_* tests monkeypatch `suite._model_supports_tools`; keep it an instance call or the gate goes
        # green on a forked brain. _model_supports_tools translates cannot-determine (endpoint down) → False.
        if not self._model_supports_tools(cfg["model"], cfg["base_url"]):    # 5-key refusal
            refusal = (f"I can't act right now: the selected model '{cfg['model']}' does not report "
                       f"native tool-calling support (or its endpoint is unreachable), and I act ONLY "
                       f"through governed tools — I won't silently fall back to a non-acting path. "
                       f"Select a tool-capable chat model in the RHM config.")
            if persist:
                self.store.append_chat({"role": "user", "text": message, "grade": "gold", "source": "operator"})
                self.store.append_chat({"role": "assistant", "text": refusal, "grade": "working", "source": "twin"})
                self._emit("warning", f"RHM model '{cfg['model']}' is not tool-capable — refused (no model "
                           f"call, no fallback); select a tool-capable model", address="ui://chrome/chat")  # S2: chat-path locus
            return {"reply": refusal, "action": None, "mode": mode,
                    "model": cfg["model"], "history": self.store.chat_history(40)}
        return None                                           # gate passed → proceed to the part-core

    def _persona_text(self, persona: str | None) -> str | None:
        """Expand a known persona id to its FULL character prose (the IDENTITY hookup, Tim 2026-06-07).
        Free-text / unknown persona falls through verbatim (never crash a reply over an unknown string)."""
        persona_text = persona
        if persona:
            try:
                from voice import personas as _vp
                persona_text = _vp.get_persona(persona).get("brain") or persona
            except (KeyError, ImportError):
                persona_text = persona
        return persona_text

    def _chat_sys_head(self, mode: str, persona: str | None, persona_text: str | None,
                       extra: str = "") -> str:
        """The PERSONA / GROUND-TRUTH / MODE-DIRECTIVE system head (shared by one-part + staged parts).
        `extra` carries a per-part coherence directive (the prior parts + 'continue naturally', C4.4)."""
        return (
            "You are the right-hand-man — the coherent voice of the Company, speaking to its operator "
            "about the system ITSELF. Answer ONLY from the LIVE SYSTEM STATE below; it is ground truth. "
            "If something is not in that state, say you cannot see it — NEVER invent counts, names, or "
            "facts. Be concise and concrete.\n\n"
            + (f"VOICE / PERSONA (hold this consistently): {persona_text}\n\n" if persona else "")
            + ("THE EXPLICIT MODEL OF TIM (the principles the Company holds itself to — reason from these "
               "for judgment/value questions, but mark such answers as YOUR inference (working-grade), "
               "never as Tim's actual words; when genuinely uncertain, say so and defer to Tim):\n"
               f"{self._model_of_tim_digest()}\n\n" if self._model_of_tim_digest() else "")
            + f"CURRENT MODE — {mode}: {self._mode_directive(mode)}\n\n"
            + (extra + "\n\n" if extra else "")
            + "You can ACT on the system, but ONLY by CALLING one of the governed tools provided to you "
            "(they are the verbs you are permitted in this mode/context). Call a tool ONLY when the "
            "operator actually asks you to act — otherwise just answer in text. Describing an action in "
            "prose does NOTHING; to act you must CALL the tool. You CANNOT apply, delete, or write files "
            "(those are operator-gated and are not offered as tools)."
        )

    def _chat_part_core(self, message: str, graph_id: str, focus: dict | None, mode: str, cfg: dict,
                        persona: str | None, persona_text: str | None, *, is_final: bool = True,
                        prior_parts: list | None = None, inject: str | None = None) -> dict:
        """The PER-PART core (R2-FOLD H3): one model generation + (on the FINAL part only) the tool block.
        Returns {text, outcomes, proposals} — it NEVER appends history nor emits `chat` (the epilogue
        owns those, ONCE). Both chat() (one part, is_final=True) and chat_parts() (N parts) call this.

        Preservation invariants:
          • client.complete_with_tools is called VIA THE MODULE REF (`client.` — the monkeypatch seam).
          • _chat_context is assembled HERE, so it runs ONCE PER PART (it emits a `warning` on a down
            endpoint — per-part is the documented, tested behavior; R2-FOLD H3 pt 3).
          • ALL parts route through complete_with_tools; an intermediate part passes tools=[] (C4.5 —
            pure generation, no tool block) so the seam check has teeth on every part.
        `prior_parts` (C4.4 coherence) prefills the parts already emitted this turn; `inject` is the
        run:// role value (C4.2) folded into THIS part's user content."""
        from fabric import client, transport
        prior_parts = prior_parts or []

        # COHERENCE (C4.4): a staged later part carries the prior parts + a 'continue naturally' directive
        # so the reply reads as ONE voice. The one-part path (chat()) passes no prior_parts → no extra.
        coherence = ""
        if prior_parts:
            joined = "\n".join(f"  [part {i+1}] {p}" for i, p in enumerate(prior_parts))
            coherence = ("CONTINUE THE SAME REPLY — you have already said the parts below to the operator. "
                         "Continue NATURALLY from them as ONE coherent voice; do NOT repeat them, do NOT "
                         "re-greet, do NOT restate. Add the NEXT part only.\n" + joined)
        sys_p = self._chat_sys_head(mode, persona, persona_text, extra=coherence)

        # the affordance context for THIS turn → the native tools array (mode-primary, context-refines).
        # INTERMEDIATE parts (not is_final) are PURE GENERATION (C4.5): no tools offered (tools=[]) and
        # the tool block below is skipped — but they STILL route through complete_with_tools (the seam).
        actx = self._affordance_context(graph_id, focus)
        tools = self._rhm_tools(mode, actx) if is_final else []

        # S2 (main's fresh-conversation fix, folded into the per-part core) — the history that FEEDS THE MODEL
        # must be the CURRENT conversation's, not the global stream. `_current_thread` is set by
        # new_conversation/load_conversation; read it HERE (before building msgs) so a freshly-started
        # conversation feeds an EMPTY history (it carries no prior thread's turns) and a reopened one feeds
        # exactly its own turns. With no thread (None) this is the legacy global stream (chat_history),
        # byte-for-byte the prior behaviour — back-compat. (The bug it fixes: chat_history(20) here ignored
        # the thread, so the model saw the PRIOR conversation's last 20 turns even right after "new
        # conversation" → the first reply "defaulted to the same original one". The turns were already
        # PERSISTED + RETURNED thread-scoped below; only this model-input read leaked. Limit matched (20) for
        # context-window parity.) NOTE: this read runs ONCE PER PART (the per-part core) — the same thread is
        # current across a turn's parts, so every part feeds the correct conversation.
        _tid = getattr(self, "_current_thread", None)
        prior = self.store.chats_in_thread(_tid, 20) if _tid else self.store.chat_history(20)
        # _chat_context ONCE PER PART (NOT side-effect-free — emits a warning on a down endpoint).
        msgs = [{"role": "system", "content": sys_p + "\n\n" + self._chat_context(graph_id, focus)}]
        for t in prior:
            msgs.append({"role": t["role"], "content": t["text"]})
        user_content = message
        if inject:                                            # C4.2 — the resolved run:// role value, folded in
            user_content = (f"{message}\n\n[CONTEXT recalled this turn (use it if relevant): {inject}]")
        msgs.append({"role": "user", "content": user_content})

        # NATIVE tool-calling: complete_with_tools returns the whole message dict {content, tool_calls}.
        # FAIL LOUD on exhaustion (FabricError propagates, no fallback). S5 — the brain's runtime knobs.
        _bk = cfg.get("brain_knobs") or {}
        _bkargs = {k: _bk[k] for k in ("temperature", "max_tokens", "top_p") if k in _bk and _bk[k] is not None}
        msg = client.complete_with_tools(
            transport.openai_tools_transport(base_url=cfg["base_url"], timeout=cfg["timeout"]),
            msgs, model=cfg["model"], tools=tools, tool_choice="auto", timeout=cfg["timeout"], **_bkargs)
        reply = msg.get("content") or ""                      # may be empty (the model called a tool)

        outcomes = []
        proposals = []                                        # OFFER-WITH-OPTIONS: suggest-then-confirm cards (no dispatch)
        # THE TOOL BLOCK — FINAL PART ONLY (C4.5). Intermediate parts are pure generation: skip entirely
        # (and they were offered no tools above, so a well-behaved model emits none regardless). `outcomes`
        # and `proposals` are method-level (above) so the non-final return shape still carries empty lists.
        if is_final:
            offered = set(self.available_verbs(mode, actx))
            for tc in (msg.get("tool_calls") or []):
                fn = tc.get("function") or {}
                verb = fn.get("name")
                if not verb:
                    continue
                if verb == "suggest":
                    # OFFER-WITH-OPTIONS (the consent affordance): build a PROPOSAL, do NOT dispatch. The
                    # operator sees a card for ANY offered verb and approves (→ /api/act) or steers — nothing
                    # runs until then. Each option's verb is validated against the ONE whitelist (RHM_VERBS); a
                    # non-verb option is dropped (refused-loud-at-the-click philosophy, never a silent bad card).
                    #
                    # B2 · the suggest call carries EITHER a single {verb,address,args} (B1) OR an `options[]`
                    # array of alternatives (the comparison surface). We normalise BOTH into one option list,
                    # carried FAITHFULLY from the model (rule 8 — we never invent an alternative). A consequential
                    # verb (build/panel/extend) among the options marks the offer INTERACTIVE so the FE renders the
                    # on-screen comparison + chat-until-approve surface; everything else stays B1's single card.
                    import json as _json
                    try:
                        sargs = _json.loads(fn.get("arguments") or "{}")
                    except Exception:
                        sargs = {}
                    raw_opts = sargs.get("options")
                    if not isinstance(raw_opts, list) or not raw_opts:
                        # B1 shape (or a malformed options) → the single top-level offer is the only option.
                        raw_opts = [{"verb": sargs.get("verb"), "address": sargs.get("address"),
                                     "args": sargs.get("args"), "label": sargs.get("label")}]
                    norm_opts = []
                    for o in raw_opts:
                        if not isinstance(o, dict):
                            continue
                        ov = str(o.get("verb") or "").strip().lower()
                        if ov not in self.RHM_VERBS:                  # drop a non-whitelisted option (never a bad card)
                            continue
                        norm_opts.append({"verb": ov, "address": o.get("address"),
                                          "args": o.get("args") or {},
                                          "label": o.get("label") or ov,
                                          "summary": (str(o.get("summary")).strip() or None) if o.get("summary") else None})
                    if not norm_opts:
                        continue                                       # no valid option survived → no card
                    primary = norm_opts[0]
                    # interactive when ANY offered option is a consequential verb (build/panel/extend) — the
                    # registry-truth marker the FE branches the comparison surface on (NOT options.length, so a
                    # single consequential offer still presents the interactive frame, and a multi-`show` offer
                    # stays the lighter B1 list). consequential = a verb whose body composes/authors, vs read/run.
                    _CONSEQUENTIAL = {"build", "panel", "extend"}
                    interactive = any(o["verb"] in _CONSEQUENTIAL for o in norm_opts)
                    proposals.append({**{k: primary[k] for k in ("verb", "address", "args")},
                                      "options": norm_opts,
                                      "direction": True,
                                      "interactive": interactive})
                    continue
                if verb not in offered:
                    # not offered in THIS mode → refuse without dispatching (mode-discipline gate). Legible
                    # reason; same {did:none, refused} shape _confirmation_for folds into the reply.
                    outcomes.append({"did": "none",
                                     "refused": f"{verb} not available in mode {mode}"})
                    continue
                action = self._json_obj_to_action({"name": verb, "arguments": fn.get("arguments")}, verb)
                # SEAM 2 (A · mode reach-extension, 2026-06-09): route the ACT-vs-SURFACE decision off the
                # DECLARED `consent` axis (registry-is-truth) instead of the hardcoded `if mode=="decide-for-me"`
                # name-branch (lost-opportunity #4 — `consent` was captured as data but unwired). The mode
                # declares consent ∈ {offer, act, none}; consent=="act" → route through autonomous_dispatch.
                #   • BEHAVIOUR-PRESERVING for decide-for-me: it declares consent="act" → routes EXACTLY as the
                #     name-branch did.
                #   • THE GENERALIZATION (intended, FLAGGED): background/focus/watch-and-react ALSO declare
                #     consent="act" (MODE_REGISTRY) → they NOW auto-route too — consent becomes operative. A
                #     mode that should NOT auto-act has its consent VALUE changed in MODE_REGISTRY (a separate
                #     registry data-call), never a branch here.
                #   • THE FLOOR IS UNTOUCHED: autonomous_dispatch routes by posture — AUTO-class → run
                #     (reversible/whitelisted RHM verbs only); CONFIRM-class → the verb body SURFACES a draft.
                #     It NEVER self-approves (apply still needs operator is_approved; resolve_surfaced stays
                #     operator-only). consent=="offer"/"none" (listening/text-only/walkthrough/off) route the
                #     normal dispatch, unchanged.
                if self.mode_registry(mode)["consent"] == "act":
                    # G3 wiring: route the ACT-vs-SURFACE decision DETERMINISTICALLY by the verb's governance
                    # action-class (no confidence) through autonomous_dispatch. The verb BODY performs it
                    # either way — AUTO verbs run; CONFIRM verbs run their body whose action is to SURFACE a
                    # consumable applyable draft. Outcome carries routed_posture for audit.
                    cls = self.RHM_VERB_CLASS.get(verb, "register_type")   # unknown verb → safest (CONFIRM)
                    outcome = self.autonomous_dispatch(
                        cls, do=lambda a=action: self._dispatch_rhm_action(a, graph_id), payload=action)
                else:
                    outcome = self._dispatch_rhm_action(action, graph_id)
                outcomes.append(outcome)

            # ACTION-CONFIRMATION: fold a concise confirmation into reply for EVERY dispatched verb.
            for outcome in outcomes:
                if outcome and outcome.get("did") == "consult":
                    reply = (reply + "\n\n📖 " + outcome["answer"]).strip()
                elif outcome and outcome.get("did") == "ask":
                    reply = (reply + "\n\n❓ That needs something not in the registry, so I'm asking rather "
                             "than guessing: " + outcome["needs"] + " — surfaced for you in the inbox.").strip()
                else:
                    confirm = self._confirmation_for(outcome)
                    if confirm:
                        reply = (reply + "\n\n" + confirm).strip() if reply.strip() else confirm

        return {"text": reply, "outcomes": outcomes, "proposals": proposals}

    def _chat_epilogue(self, message: str, mode: str, cfg: dict, reply: str, outcomes: list,
                       proposals: list, *, persist: bool = True) -> dict:
        """The ONCE-only epilogue both paths run AFTER the part-core(s): action_field shaping · the SINGLE
        user+assistant append · the thread bump · the SINGLE _emit('chat'). Returns the normal 7-key shape.
        For chat_parts() `reply` is the JOINED parts; `outcomes` are the final part's (tools-on-final, C4.5).

        `persist` (default True — every existing caller is UNCHANGED): when False (preview_turn, the
        non-mutating test path) the append + thread-bump + `_emit('chat')` are SKIPPED — a preview fires a
        real staged turn but must NOT persist phantom turns into the live chat history / training_signal pipe
        (AGENTS.md rule 4). The cognition.* lifecycle telemetry is NARRATION and still fires (it is what the
        preview returns)."""
        if not outcomes:
            action_field = None
        elif len(outcomes) == 1:
            action_field = outcomes[0]
        else:
            action_field = outcomes
        # `_tid` re-read here (the epilogue is its own method in the G4 refactor — it does NOT share the
        # part-core's local scope, so the current-thread must be read again). It is the SAME in-memory
        # current-thread that scoped the model input in _chat_part_core, so the turns are PERSISTED under the
        # same thread they were REASONED in — input and storage agree by construction (main's S2 invariant).
        _tid = getattr(self, "_current_thread", None)
        if persist:
            # provenance grading (B3): Tim's words are gold (train the twin); the twin's are working.
            # S2 — thread the turn into the CURRENT conversation (the additive thread_id; None = the
            # global/legacy stream, back-compat).
            self.store.append_chat({"role": "user", "text": message, "grade": self._provenance_grade("user"), "source": self._provenance_source("user"), **({"thread_id": _tid} if _tid else {})})
            self.store.append_chat({"role": "assistant", "text": reply, "action": action_field,
                                    "grade": self._provenance_grade("assistant"), "source": self._provenance_source("assistant"), **({"thread_id": _tid} if _tid else {})})
            if _tid:                                           # bump the thread's last_msg for the list ordering
                try:
                    _t = self.store.load_chat_thread(_tid)
                    if _t:
                        from datetime import datetime, timezone
                        _t["last_msg"] = datetime.now(timezone.utc).isoformat()
                        if not _t.get("title"):
                            _t["title"] = message.strip()[:48]     # title from the first turn if unnamed
                        self.store.save_chat_thread(_t)
                except Exception:
                    pass                                       # thread metadata is best-effort, never break a turn
            self._emit("chat", f"you: {message[:48]}", address="ui://chrome/chat")   # S2: chat organ event carries its locus
        # OFFER-WITH-OPTIONS: a `suggest` tool_call rides back as a `proposal` (the FE renders the one-click
        # card; approve → /api/act). Additive + back-compat: None when the turn dispatched/spoke instead of
        # offering; the existing single-`proposal` FE consumer (useAppController r.proposal) reads it unchanged.
        proposal = proposals[0] if proposals else None
        return {"reply": reply, "action": action_field, "proposal": proposal, "mode": mode,
                "model": cfg["model"], "thread_id": _tid,
                "history": self.store.chats_in_thread(_tid) if _tid else self.store.chat_history(40)}

    def chat(self, message: str, graph_id: str, focus: dict | None = None) -> dict:
        """Grounded conversation with the operator via NATIVE TOOL-CALLING. Answers from compact
        ground truth; never confabulates system facts. It ACTS only through the governed verbs offered
        as native function-tools for this mode×context — and the dispatcher's whitelist still REFUSES
        anything off it (E6). The RHM model MUST support native tools: a non-tool model is refused
        FAIL-LOUD (no model call, no fallback, rule 4).

        G4 REFACTOR: chat() is now prologue → ONE part-core (is_final=True) → epilogue — the SAME shared
        core chat_parts() runs N times. The contract + the three return shapes are byte-identical to the
        pre-refactor chat() (the rhm_* guard suites are the gate). chat() does NOT stage (one part)."""
        mode = self.get_mode()
        cfg = self.rhm_config()
        early = self._chat_prologue(message, mode, cfg)        # ONCE: off (4-key) / refusal (5-key)
        if early is not None:
            return early
        persona = cfg["persona"]
        persona_text = self._persona_text(persona)
        part = self._chat_part_core(message, graph_id, focus, mode, cfg, persona, persona_text,
                                    is_final=True)             # the ONE part (one-part path)
        return self._chat_epilogue(message, mode, cfg, part["text"], part["outcomes"], part["proposals"])

    # --- C4.3: the brevity bypass (a trivial turn does NOT spin the swarm) ---------------------------
    def _should_stage(self, message: str, mode: str) -> dict:
        """Decide whether THIS turn stages a multi-part reply (C4.3 — conditional staging is MANDATORY).
        A trivial one-liner BYPASSES the whole machine; focus/background/off modes NEVER stage. Returns
        {stage: bool, reason: str}. PURE/cheap — it must NOT fire the swarm (proof: no cognition.wave
        emit when stage is False). The brevity check is a deterministic length/shape heuristic (a
        'brevity_judge' role-style check, mode-biased) — NOT a model call, so a trivial turn costs nothing."""
        if not self.mode_stages(mode):                        # focus/background/off never stage (mode-biased)
            return {"stage": False, "reason": f"mode {mode!r} does not stage (PART_GRAIN.stage=False)"}
        t = (message or "").strip()
        # a trivial turn: short AND not multi-sentence AND not an obvious deep ask. Cheap heuristic — no
        # model call (the swarm must not spin for a one-liner). A long / multi-clause / question-laden
        # message is worth staging; a greeting / yes-no / one-liner is not.
        words = t.split()
        sentences = [s for s in t.replace("!", ".").replace("?", ".").split(".") if s.strip()]
        trivial = (len(words) <= 6 and len(sentences) <= 1)
        if trivial:
            return {"stage": False, "reason": f"trivial turn ({len(words)} words, {len(sentences)} sentence) — brevity bypass"}
        return {"stage": True, "reason": f"substantive turn ({len(words)} words, {len(sentences)} sentences)"}

    def chat_parts(self, message: str, graph_id: str, focus: dict | None = None,
                   *, turn_id: str | None = None, persist: bool = True):
        """CONCURRENT COGNITION G4 — the STAGED reply: a generator yielding the reply as PARTS, each a
        node whose inputs resolve at a run:// address (the reactive-scheduler relationship applied
        INTRA-TURN). It shares chat()'s prologue + part-core + epilogue (R1-FOLD F4 — never loops/copies
        chat()).

        The flow:
          • PROLOGUE ONCE (off/refusal short-circuit — same as chat(); yields the one early text, runs no
            epilogue). The capability-gate is the SAME instance-method seam → patching it refuses BOTH paths.
          • C4.3 brevity/never-stage check — a trivial turn / focus·background·off mode BYPASSES the swarm
            entirely (NO cognition.wave fires) and degrades to the ONE-part path (chat()'s core, is_final).
          • STAGED: grain + shape from shape_for(mode)/PART_GRAIN (C4.1). Part 1 fires from BASE context
            INSTANTLY (is_final=False; pure generation). The mode's CAST fires CONCURRENTLY via run_swarm
            (G1) writing run://<turn>/<role>; the roles' DECLARED G3 rules decide what injects (C4.2 — the
            net-new ref-read, NOT _chat_context/_resolve_context_at). Part 2 (FINAL) reads the injected
            run:// value + carries the prior parts (C4.4) + runs the tool block (C4.5 — tools on final only).
          • EPILOGUE ONCE — the SINGLE user+assistant append (the joined reply) · thread bump · the SINGLE
            _emit('chat'). Runs at end-of-stream (so G6 can adopt this generator without re-refactoring).

        Yields each part's text as it is produced; the final yield completes the epilogue. The caller
        (G6 voice stream / a test) consumes the generator and reads the joined turn from the store."""
        import time as _time
        from runtime import cognition as _cog
        mode = self.get_mode()
        cfg = self.rhm_config()
        turn_id = turn_id or "turn-" + _time.strftime("%Y%m%d-%H%M%S-") + str(int(_time.monotonic() * 1000) % 100000)

        early = self._chat_prologue(message, mode, cfg, persist=persist)   # ONCE: off (4-key) / refusal (5-key)
        if early is not None:
            # an early-return short-circuit: yield its one text + STOP (the prologue did its own append+emit
            # unless persist=False; the epilogue does NOT run — the off/refusal shape is the prologue's).
            yield {"part": 1, "text": early["reply"], "final": True, "staged": False,
                   "early_return": early}
            return

        persona = cfg["persona"]
        persona_text = self._persona_text(persona)
        decision = self._should_stage(message, mode)

        # ---- the BYPASS path (C4.3): NOT staging → the ONE-part path (chat()'s core). NO swarm fires. ----
        if not decision["stage"]:
            part = self._chat_part_core(message, graph_id, focus, mode, cfg, persona, persona_text,
                                        is_final=True)
            res = self._chat_epilogue(message, mode, cfg, part["text"], part["outcomes"], part["proposals"],
                                      persist=persist)
            yield {"part": 1, "text": part["text"], "final": True, "staged": False,
                   "stage_reason": decision["reason"], "result": res}
            return

        # ---- the STAGED path: grain/shape (C4.1) → Part 1 instant → wave → run:// inject → Part 2 ----
        shape = self.shape_for(mode)
        grain = self.grain_for(mode)
        parts_emitted: list[str] = []
        # L-fe-be — the live cognition view (06-rendering.md §F#3) lights up from per-turn cognition.*
        # LIFECYCLE events on /api/stream (the existing cognition.wave is a per-WAVE ROLLUP, kept intact).
        # These are NARRATION (lenient _emit telemetry — reflects-never-owns; never a resolve/approve/
        # dispatch — the claude -p floor holds, C9.2). Each carries a TOP-LEVEL `address` (the locus, C7.2)
        # so the view is addressable: ui://cognition/<turn> for the turn frame, run://<turn>/<role> for a
        # role instance (run:// reuse, NOT a net-new cog:// scheme — §H default lean). The contract is
        # declared in contracts/cognition_info.COGNITION_EVENT_KINDS (the FE binds to it). EMITTED
        # SYNCHRONOUSLY at TRUE points (not from the wave threads) so the causal order is honest:
        # turn.start → role.fire×N (pre-wave) → part(1) (early, before join) → role.ran×N (post-join) →
        # inject → part(2) → turn.done. (A flat fire/ran/part order would MISREPRESENT the concurrency.)
        _cog_addr = f"ui://cognition/{turn_id}"
        _turn_t0 = _time.monotonic()

        # PART 1 — from BASE context, INSTANTLY (is_final=False → pure generation, no tools). Emitted
        # before the wave completes (the wave fires concurrently below).
        cast = self.cast_for_mode(mode)
        # fire the cast CONCURRENTLY (G1 run_swarm) — but only the FIREABLE roles (a prompt+schema), and
        # only those that read just the utterance (independent ready-set). The declared rules on those
        # roles (G3) decide what injects into the FINAL part.
        fireable = [r for r in cast if getattr(r, "can_fire", False) and not getattr(r, "is_jury", False)]

        # cognition.turn.start — the view opens a turn frame (carries the mode + shape + the cast).
        self._emit("cognition.turn.start", f"turn {turn_id} · {mode} · {len(fireable)} roles",
                   turn_id=turn_id, mode=mode, shape=shape["archetype"], grain=grain,
                   cast=[r.id for r in fireable], address=_cog_addr)
        # cognition.role.fire ×N — emitted SYNCHRONOUSLY before the wave starts (deterministic, one per
        # fireable role); the role dot goes 'firing'. Address = the role's run:// instance locus.
        for r in fireable:
            self._emit("cognition.role.fire", f"role {r.id} fires",
                       turn_id=turn_id, role=r.id, model=cfg["model"],
                       address=f"run://{turn_id}/{r.id}")

        wave_holder: dict = {}
        wave_err: dict = {}
        import threading as _thr
        def _fire_wave():
            try:
                wave_holder["wave"] = _cog.run_swarm(
                    fireable, {"utterance": message}, self.store, turn_id=turn_id,
                    emit=self._emit)                          # C1.6 ONE cognition.wave rollup per wave
            except BaseException as e:                        # captured; surfaced after Part 1 (fail loud)
                wave_err["err"] = e
        wave_thread = None
        if fireable:
            wave_thread = _thr.Thread(target=_fire_wave, name=f"chat_parts-wave-{turn_id}", daemon=True)
            wave_thread.start()

        part1 = self._chat_part_core(message, graph_id, focus, mode, cfg, persona, persona_text,
                                     is_final=False)           # Part 1: base context, no tools
        parts_emitted.append(part1["text"])
        # cognition.part part=1 — the instant base part (the river fills); genuinely early (before join).
        self._emit("cognition.part", f"turn {turn_id} part 1 (base)",
                   turn_id=turn_id, part=1, final=False, staged=True, address=_cog_addr)
        yield {"part": 1, "text": part1["text"], "final": False, "staged": True,
               "grain": grain, "shape": shape["archetype"]}

        # JOIN the wave; the DECLARED G3 RULES on the cast roles decide what injects (C4.2). We read the
        # roles' resolved outputs at run://<turn>/<role> via resolve_run_ref (the canonical resolver, the
        # net-new ref-read — NOT _chat_context/_resolve_context_at, which read operator-notebook strata).
        inject_text = None
        inject_provenance = []
        if wave_thread is not None:
            wave_thread.join(timeout=_cog.ROLE_TIMEOUT + 5)
            if wave_err.get("err") is not None:
                raise wave_err["err"]                         # fail loud — a wave failure is not swallowed
            wave = wave_holder.get("wave")
            resolved = dict(wave.resolved) if wave else {}
            # cognition.role.ran ×N — read off the wave's RoleRun records AFTER the barrier (the honest
            # point: roles finished concurrently, so we narrate completion post-join). Each carries its
            # run:// address + ok + ms (straight off RoleRun). A failed role narrates loud (carries error).
            for rr in (wave.runs if wave else []):
                self._emit("cognition.role.ran",
                           f"role {rr.role_id} {'ok' if rr.ok else 'FAILED'} · {rr.ms}ms",
                           turn_id=turn_id, role=rr.role_id, ok=rr.ok, ms=rr.ms,
                           address=rr.address, **({"error": rr.error} if rr.error else {}))
            # The G3 DECLARED RULES decide what injects (C4.2 — the G4 job the spike deferred). We gather
            # the buildable AST rules from TWO sources (reuse-don't-parallel — both are the SAME G3 engine):
            #   (a) the canonical declared rule(s) the cognition driver already built (cognition.INJECTION_RULE
            #       — the spike's recall.relevant AND ground.in_scope, generalized to a declared AST in G3);
            #   (b) any AST-shaped `rules` a cast role declares (the general path — descriptive {id,reads,
            #       effect,kind} role entries are NOT AST rules → skipped; when a role adds a `when` rule it
            #       wires automatically).
            from runtime import cognition as _cog2
            candidate_rules = []
            if getattr(_cog2, "INJECTION_RULE", None) is not None:
                candidate_rules.append((None, _cog2.INJECTION_RULE))
            for role in fireable:
                rspecs = (role.spec.get("rules") if hasattr(role, "spec") else None) or []
                for rspec in rspecs:
                    rule = self._rule_from_spec(rspec)
                    if rule is not None:
                        candidate_rules.append((role.id, rule))
            for role_id, rule in candidate_rules:
                # PER-RULE READINESS (R2-FOLD H2 / G3): a rule fires only when EVERY declared input is
                # SETTLED. A rule referencing a role NOT in this turn's wave is "not ready this turn" —
                # skip it cleanly (the readiness contract, NOT a violation). When all inputs ARE present
                # we call decide() and let it FAIL LOUD (never swallow a genuine rule error — the law).
                if not (rule.inputs <= set(resolved)):
                    continue
                decision_r = rule.decide(resolved)             # fail loud on a real error (no broad except)
                if decision_r.get("fire") and rule.destination == "inject" and decision_r.get("value"):
                    inject_text = str(decision_r["value"])
                    inject_provenance.append({"role": role_id, "rule": getattr(rule, "id", "?")})
                    # cognition.inject — a declared rule injected a role's output into the FINAL part (the
                    # injection edge SOURCE→brain lights up — 06 §C/§D). The source role is recoverable from
                    # the rule even when role_id is None (the canonical INJECTION_RULE is appended with
                    # role_id=None): the value_path's FIRST segment names the source role (e.g.
                    # "recall.snippet" → "recall"). So the injection edge always identifies its source.
                    src = role_id or ((getattr(rule, "params", {}) or {}).get("value_path") or "").split(".")[0] or None
                    self._emit("cognition.inject",
                               f"rule {getattr(rule, 'id', '?')} injects {src} → part 2",
                               turn_id=turn_id, rule=getattr(rule, "id", "?"),
                               source=src, role=src,                 # `source` = the 06 §F field name; `role` kept for back-compat
                               into=2, chars=len(inject_text),
                               address=(f"run://{turn_id}/{src}" if src else _cog_addr))

        # PART 2 (FINAL) — reads the injected run:// value (C4.2), carries the prior parts (C4.4), runs
        # the tool block (C4.5 — tools on the FINAL part only).
        part2 = self._chat_part_core(message, graph_id, focus, mode, cfg, persona, persona_text,
                                     is_final=True, prior_parts=parts_emitted, inject=inject_text)
        parts_emitted.append(part2["text"])

        # cognition.part part=2 — the FINAL enriched part (the river completes). final=True.
        self._emit("cognition.part", f"turn {turn_id} part 2 (final)",
                   turn_id=turn_id, part=2, final=True, staged=True, address=_cog_addr)

        # EPILOGUE ONCE — the joined reply (one coherent voice), the SINGLE append + emit.
        joined = "\n\n".join(p for p in parts_emitted if p.strip())
        res = self._chat_epilogue(message, mode, cfg, joined, part2["outcomes"], part2["proposals"],
                                  persist=persist)
        # cognition.turn.done — the view closes the turn frame + shows the total.
        self._emit("cognition.turn.done",
                   f"turn {turn_id} done · {int((_time.monotonic() - _turn_t0) * 1000)}ms",
                   turn_id=turn_id, total_ms=int((_time.monotonic() - _turn_t0) * 1000),
                   n_parts=len(parts_emitted), n_roles=len(fireable), address=_cog_addr)
        yield {"part": 2, "text": part2["text"], "final": True, "staged": True,
               "grain": grain, "shape": shape["archetype"], "joined": joined,
               "injected": inject_text, "inject_provenance": inject_provenance,
               "turn_id": turn_id, "result": res}

    def _rule_from_spec(self, rspec):
        """Build a G3 Rule from a role's declared `rules` entry, for the G4 part-assembly (C4.2). Only an
        AST-shaped rule (has a `when` op-tree) is buildable here; a descriptive (non-AST) rule entry
        returns None (skipped — not a routing rule). Reuses the G3 rule engine (runtime/rules.py); never
        a parallel evaluator. A malformed rule fails loud at ROLE DISCOVERY (validate_role_rules), so by
        the time we see it here it is already grammar-valid."""
        from runtime import rules as _rules
        if not isinstance(rspec, dict):
            return None
        if not _rules.is_ast_rule(rspec):                     # descriptive {id,reads,effect,kind} → not a routing rule
            return None
        try:
            return _rules.build_rule(rspec)
        except Exception:
            return None

    def chat_history(self, limit: int = 40) -> list:
        return self.store.chat_history(limit)

    def react(self, graph_id: str) -> dict:
        """watch-and-react mode: a brief AMBIENT comment on the latest activity — unprompted, but
        only in that mode (real mode-gated behavior) and only when something is worth remarking."""
        if self.get_mode() != "watch-and-react":
            return {"comment": ""}                         # mode-gated: silent otherwise
        recent = self.store.recent_events(1)
        if not recent:
            return {"comment": ""}
        from fabric import client, transport
        cfg = self.rhm_config()
        last = recent[0]
        sys_p = ("You are the right-hand-man in watch-and-react mode, watching over the operator's shoulder. "
                 "Given the latest activity, offer ONE short, useful observation or suggestion about it "
                 "(e.g. a node left unwired, an obvious next step, a result worth noting). Only if there is "
                 "truly nothing useful to say, reply with exactly: NOTHING. Keep it to one sentence.")
        user = f"Latest activity: {last['kind']} — {last['summary']}.\n{self._chat_context(graph_id)[:700]}"
        out = client.complete(transport.openai_transport(base_url=cfg["base_url"], timeout=cfg["timeout"]),
                              [{"role": "system", "content": sys_p},
                               {"role": "user", "content": user}], model=cfg["model"]).strip()
        if not out or out.upper().startswith("NOTHING"):
            return {"comment": ""}
        self.store.append_chat({"role": "assistant", "text": out, "grade": "working", "ambient": True, "source": "twin"})
        self._emit("react", f"(watching) {out[:44]}", address="ui://chrome/chat")   # S2: watch-and-react is the chat organ
        return {"comment": out}

    # ============================================================================================
    # The Voice Trial — recording (Group E) + debrief (Group F). REUSE-DON'T-PARALLEL: every
    # artifact rides an EXISTING seam — the append-only event log (durable claims via
    # _emit_durable), the content-addressed store (put_content/set_ref at trial://<session>/
    # transcript), the session store (save_session/load_session), the inbox (surface_review), and
    # the walkthrough organ (start_session/present_current/next/respond). No second event log, no
    # second store, no second brain. Each spoken session is recorded so the debrief can read it
    # back FAITHFULLY (no confabulation — the debrief item carries the REAL transcript).
    # ============================================================================================

    TRIAL_KINDS = ("trial.turn", "trial.feedback", "trial.reflection")

    @staticmethod
    def _trial_transcript_addr(session_id: str) -> str:
        """The CAS-pointer (run://-style mutable ref) for a trial session's full transcript — the
        address the debrief reads back. Namespaced trial:// so it can never collide with a node's
        run:// output address or a review session's go-gate addresses."""
        return f"trial://{session_id}/transcript"

    def _trial_turn_events(self, session_id: str) -> list:
        """Every recorded trial event (turn/feedback/reflection) for ONE session, OLDEST-first —
        the single source the transcript is DERIVED from (so events + CAS never disagree). Reads
        events_since(-1) (the whole file-tail) filtered to the trial kinds + this session id."""
        return [e for e in self.store.events_since(-1)
                if e.get("kind") in self.TRIAL_KINDS and e.get("trial_session") == session_id]

    def _rebuild_trial_transcript(self, session_id: str) -> dict:
        """Re-derive the FULL transcript for a session FROM its recorded events, write it to CAS,
        and (re)point the trial://<session>/transcript ref at the new content. Re-derived on every
        turn so the three artifacts (events · CAS transcript · session record) agree BY
        CONSTRUCTION — there is no parallel transcript write that could drift from the event log.
        Returns {address, cas, turns:[...]} (the materialised transcript)."""
        turns = []
        for ev in self._trial_turn_events(session_id):
            turns.append({"kind": ev.get("kind"), "seq": ev.get("seq"), "ts": ev.get("ts"),
                          "role": ev.get("role"), "character": ev.get("character"),
                          "text": ev.get("text", "")})
        transcript = {"session": session_id, "turns": turns, "n": len(turns)}
        cas = self.store.put_content(transcript)
        addr = self._trial_transcript_addr(session_id)
        self.store.set_ref(addr, cas)
        return {"address": addr, "cas": cas, "transcript": transcript}

    def _trial_session_record(self, session_id: str, character: str | None = None) -> dict:
        """Load this trial session's record, or seed a fresh one. The record carries the cast
        member and the running turn/feedback/reflection counts so the debrief can list sessions
        without re-scanning the whole event log. Namespaced id so it never collides with a review
        session record (_load_session expects review keys: graph/cursor/items)."""
        s = self.store.load_session(session_id)
        if not s:
            s = {"id": session_id, "kind": "trial", "character": character,
                 "turns": 0, "feedback": 0, "reflections": 0, "done": False}
        if character and not s.get("character"):
            s["character"] = character
        return s

    def trial_record_turn(self, session_id: str, role: str, text: str,
                          character: str | None = None) -> dict:
        """Record ONE spoken turn of a trial conversation (role='operator'|'character'). Emits a
        DURABLE trial.turn event (_emit_durable — the record IS the behavior here; a silently
        dropped turn would make the debrief misrepresent the session, so loss must FAIL LOUD, not
        be swallowed like lenient telemetry), re-materialises the CAS transcript from the events,
        and advances the trial session record. Fail loud on empty text (no silent no-op)."""
        sid = (session_id or "").strip()
        if not sid:
            raise ValueError("trial_record_turn needs a session id (fail loud)")
        if not (text or "").strip():
            raise ValueError("trial_record_turn needs non-empty text (fail loud)")
        self._emit_durable("trial.turn", f"[{character or role}] {text[:60]}",
                           trial_session=sid, role=role, character=character, text=text,
                           address="ui://chrome/chat")   # S2: a trial turn plays out in the chat organ
                                                         # (additive meta; fail-loud posture unchanged)
        s = self._trial_session_record(sid, character)
        s["turns"] = s.get("turns", 0) + 1
        self.store.save_session(s)
        built = self._rebuild_trial_transcript(sid)
        return {"session": sid, "role": role, "turns": s["turns"],
                "transcript_addr": built["address"], "transcript_cas": built["cas"]}

    def trial_record_feedback(self, session_id: str, text: str,
                              character: str | None = None) -> dict:
        """Record Tim's SPOKEN feedback during a trial session (his verdict-in-flight on a voice/
        character). DURABLE (_emit_durable) + folded into the same transcript so the debrief reads
        his feedback alongside the turns. Fail loud on empty text."""
        sid = (session_id or "").strip()
        if not sid:
            raise ValueError("trial_record_feedback needs a session id (fail loud)")
        if not (text or "").strip():
            raise ValueError("trial_record_feedback needs non-empty text (fail loud)")
        self._emit_durable("trial.feedback", f"feedback: {text[:60]}",
                           trial_session=sid, role="operator", character=character, text=text,
                           address="ui://chrome/chat")   # S2: trial feedback plays out in the chat organ
        s = self._trial_session_record(sid, character)
        s["feedback"] = s.get("feedback", 0) + 1
        self.store.save_session(s)
        built = self._rebuild_trial_transcript(sid)
        return {"session": sid, "feedback": s["feedback"], "transcript_addr": built["address"]}

    def trial_record_reflection(self, session_id: str, text: str,
                                character: str | None = None) -> dict:
        """Record the CHARACTER's own reflection-note on the exchange (the cast member's read of
        how it went). DURABLE + in the same transcript. Fail loud on empty text."""
        sid = (session_id or "").strip()
        if not sid:
            raise ValueError("trial_record_reflection needs a session id (fail loud)")
        if not (text or "").strip():
            raise ValueError("trial_record_reflection needs non-empty text (fail loud)")
        self._emit_durable("trial.reflection", f"[{character}] reflects: {text[:50]}",
                           trial_session=sid, role="character", character=character, text=text,
                           address="ui://chrome/chat")   # S2: trial reflection plays out in the chat organ
        s = self._trial_session_record(sid, character)
        s["reflections"] = s.get("reflections", 0) + 1
        self.store.save_session(s)
        built = self._rebuild_trial_transcript(sid)
        return {"session": sid, "reflections": s["reflections"], "transcript_addr": built["address"]}

    def trial_transcript(self, session_id: str) -> dict:
        """Read back a trial session's FULL transcript from CAS (the debrief's ground truth). Reads
        the trial://<session>/transcript ref → CAS content. Fail loud if the session was never
        recorded (no ref) — the debrief MUST NOT confabulate from an absent transcript."""
        addr = self._trial_transcript_addr(session_id)
        cas = self.store.head(addr)
        if not cas:
            raise KeyError(
                f"no recorded transcript for trial session {session_id!r} (no ref at {addr}) — "
                f"record turns first; the debrief reads only real transcripts (fail loud).")
        return self.store.get_content(cas)

    def trial_sessions(self) -> list:
        """Every recorded trial session record (the cast walked, with counts) — what the debrief
        loads as its review set. Reads the session store + filters to kind=='trial' so it never
        picks up a review session record."""
        out = []
        for sid in self.store.list_sessions():
            s = self.store.load_session(sid)
            if s and s.get("kind") == "trial":
                out.append(s)
        return out

    def start_debrief(self, session_ids: list, host_persona: str | None = None,
                      mode: str = "walkthrough") -> dict:
        """Group F — the trial DEBRIEF, built ON the walkthrough organ (specialise, don't rebuild).
        A debrief is a review session whose items are the recorded trial sessions; a host character
        walks Tim back through each, conversationally, and his verdicts are captured via the SAME
        resolve_surfaced path the walkthrough uses.

        CRITICAL (the parallel-path trap): start_session / present_current / respond all key on
        INBOX item ids (coa→inbox.get, resolve_surfaced→inbox.get raise KeyError on a non-surfaced
        id). So we CANNOT feed raw trial-session ids into start_session. We first SURFACE each trial
        session as a review item — carrying the REAL transcript pulled from CAS — and collect the
        returned surfaced ids; coa() dumps the whole payload into the framing prompt, so embedding
        the transcript is what lets the host read it back FAITHFULLY instead of confabulating from a
        bare character name. THEN we hand those surfaced ids to start_session.

        The debrief-host persona is set GLOBALLY via set_rhm_config (coa reads rhm_config().persona;
        there is no per-session persona slot) — deliberate for the trial: one host voice frames all
        five. Returns start_session's first presentation (the host's framing of the first session)."""
        ids = list(session_ids or [])
        if not ids:
            raise ValueError("start_debrief needs at least one trial session id (fail loud)")
        if host_persona:
            self.set_rhm_config({"persona": host_persona})   # the debrief-host voice (global, deliberate)
        surfaced = []
        for sid in ids:
            transcript = self.trial_transcript(sid)          # FAIL LOUD if a session was never recorded
            rec = self._trial_session_record(sid)
            item = {"title": f"debrief · {rec.get('character') or sid}",
                    "kind": "trial_debrief", "trial_session": sid,
                    "character": rec.get("character"),
                    "turns": rec.get("turns", 0), "feedback": rec.get("feedback", 0),
                    "reflections": rec.get("reflections", 0),
                    "transcript": transcript}              # the REAL transcript — coa frames from THIS
            r = self.surface_review(item, origin="generative")  # a debrief = Tim revisiting his own trial
            surfaced.append(r["id"])
        self._emit("trial.debrief.start",
                   f"debrief started — {len(surfaced)} trial session(s) to walk",
                   sessions=ids, surfaced=surfaced,
                   address="ui://chrome/inbox")   # S2: debrief items surface to the review queue (inbox)
        return self.start_session(surfaced, mode=mode)

    # ============================================================================================

    # --- the inbox: chief-of-staff triage (F1-F2) + the decision-compiler UP (C2-C3) ---
    def inbox_lanes(self) -> dict:
        """Three lanes (context-05): live escalations (pending, need the operator), resolved-for-you
        (already handled — audit), and batched walkthroughs (pending grouped by theme).

        T3-HYGIENE (filter-at-source): items tagged `test_origin` at creation (a run under
        COMPANY_TEST_RUN) are EXCLUDED from the operator's lanes — that pollution is what buried the
        real items. The exclusion is NOT silent: `counts.test_origin_excluded` reports how many were
        filtered, so a test run can still see/verify them and nothing is hidden by sleight of hand
        (fail-loud-legible). A real operator run sets no flag → no items tagged → identical to before."""
        items = self.inbox.list()
        real = [d for d in items if not d.get("test_origin")]
        excluded = len(items) - len(real)
        escalations = [d for d in real if d.get("resolved") is None]
        resolved = [d for d in real if d.get("resolved") is not None]
        batched: dict = {}
        for d in escalations:
            batched.setdefault(d["action"], []).append(d["id"])
        return {
            "live_escalations": escalations,                       # the irreducible — brought as COA
            "resolved_for_you": resolved,                          # logged for audit; needn't be worked
            "batched": {k: v for k, v in batched.items() if len(v) > 1},  # themes to handle in one sitting
            "counts": {"escalations": len(escalations), "resolved": len(resolved),
                       "test_origin_excluded": excluded},
        }

    # COA framing — the system prompt is module-level so the grounding guard, the live path, and the
    # acceptance suite all reference the SAME contract (one source). It hard-instructs grounding: frame
    # ONLY from the supplied payload, never invent — the prompt half of the guard (the code half below
    # is the real enforcement: abstain-on-empty + degrade-on-model-absent, neither prompt-dependent).
    # SCHEMA-AWARE: the live path is `client.complete(schema=CoaFraming)`, which retrieves the model's
    # CONTENT and validates it against CoaFraming — it does NOT auto-emit JSON for us (the schema kwarg is
    # not threaded into the transport's response_format; `json=True` in _live_complete sets the endpoint's
    # json_object mode, and THIS prompt names the exact shape). So the prompt MUST instruct the model to
    # return ONLY the CoaFraming JSON — otherwise prose comes back, _parse fails, and coa degrades on a
    # healthy model. The shape named here is the CoaFraming contract (one source — keep in sync if it
    # changes; the schema validation is the backstop that fails loud if it drifts).
    _COA_SYS = (
        "You are the right-hand-man's decision-compiler. Translate the raw technical decision BELOW into a "
        "COMMANDER-ALTITUDE value choice for the operator. Ground EVERY part STRICTLY in the supplied "
        "payload — never invent a decision the payload does not contain. Never make raw code the choice — "
        "the operator decides on value, not implementation.\n\n"
        "Respond with ONLY a JSON object of this exact shape (no prose, no markdown fences):\n"
        '{"meaning": "<what this decision means for the system, in plain terms>", '
        '"options": [{"label": "<a value option in plain commander terms>", '
        '"tradeoff": "<what you gain / give up choosing it>"}, ... 2-3 options], '
        '"recommendation": "<a clear recommendation + a one-line why>"}')

    def coa(self, surfaced_id: str, _complete=None) -> dict:
        """Decision-compiler UP (F1's core up-translate organ): translate a raw technical decision into a
        Commander-altitude VALUE choice — what it means, 2-3 options with trade-offs, + a recommendation.
        The raw payload stays DRILLABLE (F2); the operator decides on value, never the raw fork (C2).

        SHAPE is CODE-ENFORCED via the `CoaFraming` schema (proven model-free by an injected canned
        response); the WORDING quality is the live-model-dependent half (flagged for a model-up check).

        GROUNDING GUARD (soft-spot #5, code-enforced — NOT prompt-only):
          • ABSTAIN-ON-EMPTY — if the surfaced item carries no real payload there is nothing true to
            frame, so coa does NOT call the model (a model given no payload would CONFABULATE a decision).
            It returns an honest "can't frame this — here's the raw" with grounded=False, raw still
            attached. No silent fabrication from emptiness.
          • DEGRADE-ON-MODEL-ABSENT — the live model call is wrapped: a FabricError (model down /
            unreachable / a shape it could not satisfy) is NOT swallowed and is NOT faked into a story.
            `framing` becomes a LEGIBLE "model unavailable" line, the raw stays drillable, degraded=True,
            and a loud warning is emitted (fail-loud-legible, rule 4). The operator never sees an invented
            framing in place of a real one.
          • RAW ALWAYS ATTACHED — every return path keeps `raw` (the structural drill-to-ground), so the
            operator can always reach the true payload behind the altitude lead.

        FE CONTRACT (additive-only — Grow.tsx + useAppController.ts:272 read these, canvas/** is out of
        this lane's file set): `id`, `raw` (the payload dict — .name/.code read off it), and `framing` (a
        STRING rendered in the grow-coa div). NEW alongside: `framing_struct` (the CoaFraming dict or
        None), `grounded` (bool), `degraded` (bool) — unknown keys the FE ignores.

        `_complete` is the test injection seam (default None → the real fabric path): a callable
        (sys_prompt, user_prompt, model, base_url) -> CoaFraming, so the structure/guard/degrade can all
        be driven deterministically with NO live model."""
        d = self.inbox.get(surfaced_id)
        if not d:                                              # asked to frame a thing that doesn't exist → RAISE
            raise KeyError(f"no surfaced decision {surfaced_id!r}")

        payload = d.get("payload")
        # GROUNDING GUARD (a) — ABSTAIN-ON-EMPTY: no real payload → do not call the model (it would
        # confabulate). Honest "can't frame, here's the raw", grounded=False, raw still attached.
        if not payload or (isinstance(payload, (dict, list, str)) and len(payload) == 0):
            self._emit("warning", f"coa: surfaced {surfaced_id!r} has no payload to frame — abstaining "
                       "(no confabulation)", surfaced=surfaced_id, address="ui://chrome/inbox")
            return {"id": surfaced_id, "class": d.get("action"),
                    "framing": "Can't frame this at your altitude — the decision carries no payload to "
                               "ground a framing in. The raw is attached for inspection.",
                    "framing_struct": None, "raw": payload, "grounded": False, "degraded": False}

        cfg = self.rhm_config()
        user = f"Decision class: {d.get('action')}. Default if ignored: {d.get('default')}. Payload: {payload}"

        # F1 LEARNING LOOP — the ADAPT step for coa: if the surfaced item carries a `ui://` address (e.g. a
        # build-intent minted at a locus), CONSULT the learned presentation pref there and THREAD its
        # directive into the user prompt so the model honors how Tim wants this framed. The MECHANISM (pref
        # recorded → consulted → reached the framing prompt) is proven MODEL-FREE (the `_complete` injection
        # seam receives the directive in its prompt args); the WORDING the model actually emits honoring it
        # is the model-dependent half (flagged). No address / no pref → the prompt is byte-for-byte the
        # default (the clean default — no error, no fabricated directive). A stored junk pref RAISES (fail
        # loud) via the consult-read's re-validation.
        _pref_addr = payload.get("address") if isinstance(payload, dict) else None
        _pref = None
        if isinstance(_pref_addr, str) and _pref_addr.startswith("ui://"):
            _pref = self.presentation_pref_at(_pref_addr)            # raises on a stored junk pref (fail loud)
        presentation_directive = None
        if _pref:
            presentation_directive = self.PRESENTATION_PREFS[_pref["kind"]].format(arg=_pref.get("arg"))
            user += (f"\n\nPRESENTATION PREFERENCE (Tim has shaped how he wants things at {_pref_addr} "
                     f"presented — honor it in your framing): {presentation_directive}")

        def _live_complete(sys_p, usr, model, base_url) -> CoaFraming:
            from fabric import client, transport
            # `json=True` → the transport sets response_format={type:json_object} (transport.py:37) so the
            # endpoint emits a JSON object; `schema=CoaFraming` → complete() validates the content against
            # the schema (retries+raises on a shape miss). The prompt (_COA_SYS) names the exact shape. All
            # three together make the LIVE path emit + validate the struct — WITHOUT the prompt+json the
            # schema kwarg alone does NOT request JSON from the endpoint, so a healthy model would return
            # prose and coa would always degrade (the regression this guards against).
            return client.complete(transport.openai_transport(base_url=base_url),
                                   [{"role": "system", "content": sys_p},
                                    {"role": "user", "content": usr}],
                                   model=model, schema=CoaFraming, json=True)

        run = _complete or _live_complete
        # GROUNDING GUARD (b) — DEGRADE-ON-MODEL-ABSENT: wrap the model call. FabricError (down /
        # unreachable / schema-unsatisfiable) → legible degrade, raw kept, NEVER a fabricated framing.
        try:
            struct: CoaFraming = run(self._COA_SYS, user, cfg["model"], cfg["base_url"])
        except Exception as e:
            self._emit("warning", f"coa: framing model unavailable ({type(e).__name__}) — degrading "
                       "to raw-only, no fabricated framing", surfaced=surfaced_id, address="ui://chrome/inbox")
            return {"id": surfaced_id, "class": d.get("action"),
                    "framing": (f"Can't up-translate this right now — the framing model is unavailable "
                                f"({type(e).__name__}). The raw decision is attached so you can still act on it."),
                    "framing_struct": None, "raw": payload, "grounded": True, "degraded": True}

        # SHAPE is code-enforced (the schema validated); project to the FE text + expose the struct.
        out = {"id": surfaced_id, "class": d.get("action"),
               "framing": struct.to_text(), "framing_struct": struct.model_dump(),
               "raw": payload, "grounded": True, "degraded": False}
        if _pref:                                                    # F1: the consulted pref reached the framing
            out["presentation_pref"] = _pref
            out["presentation_directive"] = presentation_directive
        return out

    # ============================================================================================
    # F1 — the GENERALIZED up-translate move: "present-this-at-Tim's-altitude" for ANY artifact
    # ============================================================================================
    # address_help up-translates ONE address (3 legs); coa up-translates ONE surfaced decision. The
    # foundation "up-translate everywhere" needs the SAME move callable on ANY system artifact — an
    # address, a surfaced decision, a drift/coherence finding, an event — returning its Tim-altitude
    # framing (a plain-language LEAD + a drillable MECHANISM). This is the reusable resolver F1's
    # surface + G2 (detectors-as-RHM-signal) will CONSUME.
    #
    # It is a THIN COMPOSER, never a rebuild (rule 3, one-source): each kind DISPATCHES to the existing
    # proven organ and the result is NORMALIZED to one envelope. It REUSES:
    #   • address_help (D2) — already returns the altitude shape (legs + legs_present + degrade-clean);
    #   • coa — the value-framing + grounding guard + model-degrade (above);
    #   • the surfaced/inbox store — the same artifacts coa/the inbox read (no parallel store);
    #   • resolution_spec_for (modes E1) — the active mode's lens tunes verbosity where it helps.
    # The ONE envelope every kind returns:
    #   {kind, ref, lead, mechanism, legs_present, grounded, degraded, note}
    #   • lead       — the plain-language altitude line (what this IS / MEANS at Tim's level).
    #   • mechanism  — the drillable ground (the raw payload / the address legs / the finding detail).
    #   • legs_present — which parts resolved (the address_help degrade pattern, generalized).
    #   • grounded   — framed ONLY from real resolved content (the grounding guard, generalized).
    #   • degraded   — a leg/the model was unavailable (legible, never fabricated).
    UPTRANSLATE_KINDS = ("address", "decision", "finding", "event")

    def up_translate(self, kind: str, ref, _complete=None) -> dict:
        """F1 — up-translate ANY system artifact to Tim's altitude (plain-language LEAD + drillable
        MECHANISM), composing the existing organs. `kind` ∈ UPTRANSLATE_KINDS; `ref` is the artifact
        handle (a ui:// address string for 'address'; a surfaced_id for 'decision'; a finding dict for
        'finding'; an event dict for 'event'). FAIL LOUD on an unknown kind (rule 8 — never guess). The
        grounding guard is generalized: every kind frames ONLY from real resolved content and marks
        degraded/grounded honestly rather than confabulating. `_complete` is threaded to coa for the
        model-free decision proof."""
        if kind not in self.UPTRANSLATE_KINDS:
            raise ValueError(f"up_translate: unknown kind {kind!r} — one of {self.UPTRANSLATE_KINDS} "
                             "(rule 8: never fabricate a kind)")

        if kind == "address":
            # REUSE address_help (D2) — it already IS the altitude shape. Normalize its 3 legs into the
            # one envelope: the lead is the plain-language what-this-is + how-to-use (the altitude lead);
            # the mechanism is how-to-change (the code scope + blast radius — the drill-to-ground).
            # A MALFORMED address propagates address_help's S0 raise (fail loud); an UNREGISTERED /
            # no-code / unauthored address degrades clean (the legs_present flags carry which legs landed).
            b = self.address_help(ref)                          # raises on malformed (S0) — fail loud
            lp = b.get("legs_present") or {}
            wti = b.get("what_this_is")
            htu = b.get("how_to_use")
            lead_parts = []
            if lp.get("what_this_is"):
                lead_parts.append(wti)
            if lp.get("how_to_use") and htu:
                lead_parts.append(htu)
            lead = "  ".join(lead_parts) if lead_parts else (wti or f"{ref} (not registered)")
            grounded = bool(lp.get("what_this_is"))             # framed from a REAL registry row, not invented
            degraded = not (lp.get("what_this_is") and lp.get("how_to_use") and lp.get("how_to_change"))
            env = {"kind": "address", "ref": ref, "lead": lead,
                   "mechanism": b.get("how_to_change"), "legs_present": lp,
                   "grounded": grounded, "degraded": degraded,
                   "note": (b.get("how_to_change") or {}).get("note")}
            # F1 LEARNING LOOP — the ADAPT step on the COMPOSED envelope: address_help already consulted
            # the pref (it rides `b["presentation_pref"]`); apply it to the up_translate `lead`/`mechanism`
            # shape so the F1 envelope REFLECTS Tim's shaping (model-free: the pref reaches the envelope +
            # reorders the lead). No pref → byte-for-byte the pre-loop envelope (the clean default).
            return self._apply_presentation_pref(env, b.get("presentation_pref"))

        if kind == "decision":
            # REUSE coa — the value-framing + grounding guard + model-degrade already live there. Map its
            # return into the one envelope: lead = the framing (the altitude value-choice text), mechanism
            # = raw (the drillable payload). coa's grounded/degraded carry straight through. A missing
            # surfaced_id propagates coa's KeyError (fail loud — asked to frame a thing that isn't there).
            c = self.coa(ref, _complete=_complete)              # raises KeyError on a missing item — fail loud
            return {"kind": "decision", "ref": ref, "lead": c.get("framing"),
                    "mechanism": c.get("raw"),
                    "legs_present": {"meaning": c.get("framing_struct") is not None,
                                     "raw": c.get("raw") is not None},
                    "grounded": bool(c.get("grounded")), "degraded": bool(c.get("degraded")),
                    "note": None, "framing_struct": c.get("framing_struct")}

        if kind == "finding":
            # A drift/coherence finding (the shape G2 will feed — NOT wired here, that's a later lane). We
            # up-translate a finding DICT the caller already holds (e.g. {address, what, detail, touches}).
            # GROUNDING GUARD: frame ONLY from the supplied finding — an empty/non-dict finding abstains
            # rather than inventing one. If the finding names a ui:// address, ENRICH the mechanism with
            # that address's blast-radius (REUSE resolve_scope/blast_radius — the same "what it touches"
            # join address_help uses), so a drift lead can drill to what a fix would reach. Best-effort:
            # an unreachable/absent address degrades the enrichment, never fabricates it.
            if not isinstance(ref, dict) or not (ref.get("what") or ref.get("detail")):
                return {"kind": "finding", "ref": ref, "grounded": False, "degraded": False,
                        "lead": "Can't frame this finding — it carries no content to ground a framing in.",
                        "mechanism": ref, "legs_present": {"finding": False, "touches": False},
                        "note": "empty/malformed finding — abstained (no confabulation)"}
            what = ref.get("what") or ref.get("detail")
            addr = ref.get("address")
            lead = (f"{what}" + (f" (at {addr})" if addr else ""))
            mechanism = {"detail": ref.get("detail"), "address": addr, "touches": None}
            degraded = False
            note = None
            if isinstance(addr, str) and addr.startswith("ui://"):
                try:
                    mechanism["touches"] = self.blast_radius(addr)   # REUSE — what a fix here would reach
                except Exception as e:                               # best-effort enrichment, never fabricate
                    degraded = True
                    note = f"could not resolve what this touches ({type(e).__name__})"
            return {"kind": "finding", "ref": ref, "lead": lead, "mechanism": mechanism,
                    "legs_present": {"finding": True, "touches": mechanism["touches"] is not None},
                    "grounded": True, "degraded": degraded, "note": note}

        # kind == "event" — up-translate one recorded event (kind/summary/address/ts) to a plain line.
        # GROUNDING GUARD: an event with no summary has nothing true to frame → abstain. The mechanism is
        # the raw event dict (drillable); if it carries a ui:// address, that's the locus to drill to.
        if not isinstance(ref, dict) or not ref.get("summary"):
            return {"kind": "event", "ref": ref, "grounded": False, "degraded": False,
                    "lead": "Can't frame this event — it carries no summary to ground a framing in.",
                    "mechanism": ref, "legs_present": {"event": False},
                    "note": "empty/malformed event — abstained (no confabulation)"}
        ek = ref.get("kind", "event")
        lead = f"[{ek}] {ref.get('summary')}" + (f"  (at {ref['address']})" if ref.get("address") else "")
        return {"kind": "event", "ref": ref, "lead": lead, "mechanism": ref,
                "legs_present": {"event": True}, "grounded": True, "degraded": False, "note": None}

    def surface_output(self, graph_id: str, node_id: str) -> dict:
        """F2: route a node's RESULT to the decision surface. Composes the EXISTING surfaced/inbox
        path (no new mechanism): read the node's output from live state (the backend is truth — the
        client passes only {node, graph_id}, never the output itself; canvas reflects-never-owns),
        then surface it as a 'result' decision so it lands in `live_escalations` and is drillable via
        `coa` like any other surfaced item. Fail loud if the node is absent or has no output yet."""
        st = self.state(graph_id)
        node = next((n for n in st["nodes"] if n["id"] == node_id), None)
        if node is None:
            raise KeyError(f"no node {node_id!r} in graph {graph_id!r}")
        out = node.get("output")
        if out is None or str(out) == "":
            raise ValueError(f"node {node_id!r} has no output to surface yet — run it first (fail loud)")
        sid = self.inbox.surface("result",
                                 {"name": f"output · {node_id}", "node": node_id,
                                  "graph_id": graph_id, "output": str(out),
                                  # L8 (§21.7#9): the surfaced item CARRIES its navigable ui:// target so
                                  # clicking it in the inbox drives the operator's view to the thing it is
                                  # about (the node), via the preserved resolveUiTarget keystone. Derived
                                  # by the EXISTING _registry_ui_target (node → ui://canvas/<node>) —
                                  # registry-valid by construction, never fabricated. It lands inside
                                  # `payload` (the open bag every consumer reads via .get — seams-engine
                                  # Seam 2), so all surfaced-item consumers (inbox_lanes/escalation/wire)
                                  # ignore it cleanly. present_current's transient stamp (2662-2664) sees
                                  # it already present and skips re-stamping — same value, no conflict.
                                  "ui_target": self._registry_ui_target({"node": node_id})},
                                 default="reject")
        # emit as 'ask' so the live SSE inbox-refresh path (App.tsx kinds: ask|reject|resolve|…) lights
        # up; the operator's button also poll()s for instant local feedback regardless of the stream.
        self._emit("ask", f"a result was surfaced for your decision: {node_id}", surfaced=sid,
                   address=self._registry_ui_target({"node": node_id}))   # S2: registry-valid locus (the node)
        return {"id": sid, "node": node_id, "name": f"output · {node_id}"}

    # --- A: the review queue (one inbox, all sources; SEPARATE status lifecycle) ---
    def surface_review(self, item: dict, origin: str = "responsive") -> dict:
        """Surface a `review` decision into the SAME surfaced/inbox store (no parallel queue, A).
        `origin`: 'responsive' (a need raised by the build loop / a result) or 'generative' (an idea
        Tim threw in). The item carries a SEPARATE `status` (starts 'inbox') so the walk-lifecycle never
        overloads `resolved` — the predicate `resolved is None` keeps it a live escalation until Tim
        resolves it. Fail loud on a non-dict item. (E1's build loop calls this in place of WALKTHROUGH.md.)"""
        if not isinstance(item, dict):
            raise TypeError(f"surface_review needs a dict item, got {type(item).__name__}")
        sid = self.inbox.surface_review(item, origin=origin)
        # emit 'ask' so the SSE inbox-refresh lights up (same kind surface_output uses).
        self._emit("ask", f"a review item was surfaced ({origin}): {item.get('title', item.get('name', sid))}",
                   surfaced=sid, origin=origin,
                   address=self._registry_ui_target(item))   # S2: registry-valid locus (the node, or the inbox)
        return {"id": sid, "origin": origin, "status": "inbox"}

    def idea_capture(self, text: str) -> dict:
        """A4 — capture a fleeting idea as a GENERATIVE review item (the idea-capture organ). It lands
        in the same queue; the operator triages it later. Fail loud on empty text (no silent no-op)."""
        t = (text or "").strip()
        if not t:
            raise ValueError("idea_capture needs non-empty text (fail loud)")
        return self.surface_review({"title": t[:80], "idea": t, "kind": "idea"}, origin="generative")

    # --- B3: the configurable interactive-inbox — defer a LIVE offer into the one queue, revivable ---
    # §6B mode #4 (QUEUE, configurable): the operator can defer ANY offer/build (the B1/B2 propose-affordance
    # — its verb/address/args/options[]/interactive/direction) into the inbox AS A REAL QUEUED ITEM (not the
    # earlier FE-only "set aside" no-op). It lands in the SAME surfaced/inbox store every other lane uses
    # (registry-is-truth, NO parallel queue) so a fresh process reads it back. The whole proposal shape is
    # persisted under payload.proposal — ENOUGH TO REVIVE the interactive RHM offer (the ProposeAffordance
    # card with its options + steer channel + approve), so revisiting RE-OPENS the live conversation, never a
    # dead queue card. NOTHING runs here: resolved=None (a live escalation until the operator acts), no
    # /api/act, no dispatch — the B1/B2 consent invariants (select≠approve, nothing-runs-until-approved) are
    # preserved because reviving simply re-renders the SAME card whose approve is the only dispatch.
    #
    # DISTINCT action_class `deferred_offer` (NOT surface_review — that forces action="review" and would make
    # this indistinguishable from a real review item; the Inbox splits it into its OWN resume lane by class).
    # Schema-additive: the surfaced record gains an optional payload shape; no schema_ver bump (payload is the
    # open bag every consumer reads via .get — an unknown class is ignored cleanly by inbox_lanes/escalation).
    def defer_offer(self, proposal: dict, note: str = "") -> dict:
        """Defer a live RHM offer into the inbox as a REAL queued, revivable item (§6B QUEUE mode).
        `proposal` is the B1/B2 offer shape ({verb, address, args, options[], interactive, direction}) — the
        revival state. Fail loud on a non-dict or a proposal carrying no verb AND no options (nothing to
        revive). The item lands in `live_escalations` (resolved=None) until the operator revives+approves it
        or dismisses it; only the operator-face resolve ever clears it (reflects-never-owns)."""
        if not isinstance(proposal, dict):
            raise TypeError(f"defer_offer needs a dict proposal, got {type(proposal).__name__} (fail loud)")
        opts = proposal.get("options") or []
        if not proposal.get("verb") and not opts:
            raise ValueError("defer_offer needs a proposal carrying a verb or options[] to revive (fail loud)")
        # the human-legible name for the queued card (the primary offer's label/verb at its address).
        primary = (opts[0] if opts else proposal)
        label = primary.get("label") or primary.get("verb") or "offer"
        addr = proposal.get("address") or primary.get("address")
        name = f"deferred offer · {label}" + (f" @ {addr}" if addr else "")
        payload = {
            "name": name,
            "note": (note or "").strip(),
            # the FULL revival state — exactly what ProposeAffordance + approveProposal need to re-open the
            # live offer. Stored verbatim (the open bag), so a fresh Suite reads it back unchanged.
            "proposal": {
                "verb": proposal.get("verb"),
                "address": proposal.get("address"),
                "args": proposal.get("args"),
                "options": opts,
                "interactive": bool(proposal.get("interactive")),
                "direction": proposal.get("direction") is not False,
            },
            # L8 (§21.7#9): if the offer points at a ui:// address, carry it as the click-to-thing target so
            # the queued card can drive the operator's view to the locus the offer is about (registry-valid by
            # construction — derived from the offer's own address, never fabricated).
            **({"ui_target": addr} if (isinstance(addr, str) and addr.startswith("ui://")) else {}),
        }
        sid = self.inbox.surface("deferred_offer", payload, default="reject", resolved=None)
        # emit 'ask' so the live SSE inbox-refresh path lights up (same kind surface_output/surface_review use).
        self._emit("ask", f"an offer was deferred to your inbox: {name}", surfaced=sid,
                   address=addr if (isinstance(addr, str) and addr.startswith("ui://")) else None)
        return {"id": sid, "name": name, "proposal": payload["proposal"]}

    def revive_offer(self, sid: str) -> dict:
        """B3 — read a deferred offer back out of the inbox to RE-OPEN the live interactive conversation
        (the ProposeAffordance card). Returns the stored revival state ({verb,address,args,options,
        interactive,direction}) so the operator resumes discussing/steering/approving from where they left
        off. Fail loud if the id is missing or is not a deferred_offer (never a wrong-card revive)."""
        d = self.inbox.get(sid)
        if not d:
            raise KeyError(f"no surfaced item {sid!r} to revive (fail loud)")
        if d.get("action") != "deferred_offer":
            raise ValueError(f"surfaced {sid!r} is a {d.get('action')!r}, not a deferred_offer — cannot revive as an offer (fail loud)")
        return {"id": sid, "proposal": (d.get("payload") or {}).get("proposal") or {},
                "note": (d.get("payload") or {}).get("note", ""),
                "resolved": d.get("resolved")}

    # --- B: the walkthrough engine — a review session IS a Graph, run by the existing scheduler ---
    # No bespoke iterator + no scheduler change: a review-item = a STEP node whose readiness waits on a
    # human-writable `go` input (the scheduler already waits on an unwired/unresolved declared port,
    # scheduler.py:62-67). Each step has its OWN unresolved go-gate, so a fixpoint run() can't overrun
    # one step into the next (guide B). `next()` OPENS the current gate by writing the go-address.
    #
    # CARRIER node-type: any registered process node with a single declared input port works purely as a
    # resolution gate (the body is irrelevant — we read state, not the step's output). `uppercase` has
    # PORTS_IN={'text':'Text'}. Named once so swapping to a dedicated step/gate type later is one line.
    # CROSS-LANE SEAM (B-backend ↔ SCHED): SCHED owns nodes/gate.py + per-port emit for B5 BRANCHING;
    # this linear pacing deliberately does NOT depend on it (territory + don't couple to an unbuilt lane).
    STEP_CARRIER = "uppercase"
    GATE_CARRIER = "constant"     # the per-step go-SOURCE: a node whose output we write directly via next()

    @staticmethod
    def _session_graph_id(session_id: str) -> str:
        return f"review-{session_id}"

    def _go_addr(self, session_id: str, position: int) -> str:
        """The go-gate address for step `position` — the source node's logical output (compile.py form)."""
        return f"run://{self._session_graph_id(session_id)}/go{position}"

    def start_session(self, item_ids: list, mode: str = "walkthrough",
                      teach: list | None = None, indicate: list | None = None) -> dict:
        """Compile a review-session into a Graph the existing scheduler runs, operator-paced (B).
        For each item i: a go-SOURCE node `go{i}` (constant, unwired → never auto-fires → its address
        stays unresolved = the gate) wired into a STEP node `step{i}` (carrier) on its `text` port. The
        step thus waits until next() writes `go{i}`'s address. Persists the session record atomically
        (save_session) + the graph. The session is server-authoritative; the canvas reflects it.

        C2 (schema-additive side-channels, both optional): `teach` is a per-step list of flow-level
        narration (the bootstrap's own teaching voice, composed WITH the corpus how-to in present_current's
        guide branch), `indicate` is a per-step list of FE mount-hints (a ui:// address the FE indicates so
        a hard-gated element mounts before its spotlight). Both POSITIONALLY ALIGNED to `item_ids`; None
        (the default — every existing caller) leaves the session record C1-shaped (no teach/indicate keys),
        so the guide/review narration is byte-identical. A length mismatch fails loud (no silent misalign)."""
        items = list(item_ids or [])
        if not items:
            raise ValueError("start_session needs at least one item id (fail loud)")
        if mode not in self.MODES:
            raise ValueError(f"unknown session mode {mode!r} — one of {self.MODES}")
        if teach is not None and len(teach) != len(items):
            raise ValueError(f"start_session teach length {len(teach)} != items length {len(items)} (fail loud — no silent misalign)")
        if indicate is not None and len(indicate) != len(items):
            raise ValueError(f"start_session indicate length {len(indicate)} != items length {len(items)} (fail loud — no silent misalign)")
        import time as _t
        session_id = f"{int(_t.time())}-{len(items)}"
        gid = self._session_graph_id(session_id)
        nodes, edges = [], []
        for i, _item in enumerate(items):
            # go-SOURCE `go{i}` (constant, PORTS_IN={}) wired into STEP `step{i}` (carrier) on `text`.
            # The step waits until go{i}'s OUTPUT ADDRESS resolves (scheduler readiness, scheduler.py:62-67).
            nodes.append(NodeInstance(id=f"go{i}", type=self.GATE_CARRIER, config={"value": ""}))
            nodes.append(NodeInstance(id=f"step{i}", type=self.STEP_CARRIER, config={}))
            edges.append(Edge(from_node=f"go{i}", from_port="value", to_node=f"step{i}", to_port="text"))
        g = Graph(id=gid, nodes=nodes, edges=edges)
        self.store.save_graph(g)
        # THE GATE INVARIANT (load-bearing — do not break): a `constant` go-source has PORTS_IN={} so it
        # WOULD auto-fire on a plain run() and open EVERY gate at once. What actually holds the gates closed
        # is that next() runs the session graph with ALL `go*` nodes in `pause` (so none auto-fire), and
        # opens ONLY the current step's gate by WRITING that go-source's output address directly
        # (set_ref+put_content). => The session graph MUST NEVER be run un-paused over its go-sources; the
        # human-paced "go" signal is the hand-written address, not the source firing. (Removing the pause
        # silently breaks pacing — every step would fire on the first Next; no test would catch it.)
        session = {"id": session_id, "graph": gid, "mode": mode, "items": items,
                   "cursor": 0, "opened": [], "done": False}
        # C2 side-channels (schema-additive): only set when provided, so a plain review/guide session record
        # stays C1-shaped (no extra keys → byte-identical). present_current's guide branch reads these by cursor.
        if teach is not None:
            session["teach"] = list(teach)
        if indicate is not None:
            session["indicate"] = list(indicate)
        self.store.save_session(session)
        self._emit("review.start", f"review session {session_id} started — {len(items)} item(s), mode={mode}",
                   session=session_id, items=items, mode=mode,
                   address="ui://chrome/chat")   # S2: the review session walks in the chat/walkthrough organ
        return self.present_current(session_id)

    def _load_session(self, session_id: str) -> dict:
        s = self.store.load_session(session_id)
        if not s:
            raise KeyError(f"no review session {session_id!r}")
        return s

    def _registry_ui_target(self, payload: dict) -> str:
        """T0-KEYSTONE (backend half) — derive a REGISTRY-VALID `ui://` target for a review item's
        payload, so the walkthrough's view-drive (FE `resolveUiTarget(session.raw.ui_target)`) actually
        moves the operator's view to the thing the step concerns. The FE validates the ref against the
        live UI registry (`/api/ui_info` → build_ui_info) and FAILS LOUD on an unknown ref — so this
        MUST emit a ref the registry knows. The registry (UI_REGISTRY) contains:
          • ui://canvas/<node-id>  (camera path — the FE only drives if that node is on the loaded graph)
          • ui://canvas/*          (the whole canvas)
          • ui://chrome/{toolbar,inspector,inbox,activity,chat,workshop}  (DOM-resolved chrome regions)
        Mapping (deterministic, never invents): if the payload references a specific NODE (a result
        surfaced from a node, or a build_result_review tied to a node) → ui://canvas/<node-id> (point at
        the node). Otherwise the item is about the review queue itself → ui://chrome/inbox (a node-less
        build/idea/review item — the safe, always-registered target). Registry-is-truth: every branch
        returns a ref present in UI_REGISTRY (no fabrication). This stamps INTO the payload (what `raw`
        carries) — the additive field the FE reads — WITHOUT removing the top-level ui://review/<id>."""
        p = payload or {}
        # G-43 (C1 guided-sequence seam) — a payload may ALREADY carry an explicit registry-valid `ui://`
        # element address (a guided-step item is an `ui://<region>/<element>` address, NOT a node-backed
        # review payload). Honour it FIRST, validated against the live UI registry (registry-is-truth,
        # rule 8 — never pass through a fabricated ref the FE resolveUiTarget would then fail-loud on).
        # Before this, payload-less / synthetic / address-keyed items fell straight to the inbox region
        # (G-43: "per-step ui_target not stamped for payload-less items") so the FE spotlight no-op'd.
        # `payload['ui_target']` (a guided step stamps it) OR `payload['guide_address']` (the C1 marker) —
        # whichever is a registered element address wins. A NODE-backed payload still maps node→canvas.
        for key in ("ui_target", "guide_address"):
            cand = p.get(key)
            if isinstance(cand, str) and cand.startswith("ui://"):
                try:
                    if cand in self.build_ui_info():           # registered element address → drive to it
                        return cand
                except Exception:
                    pass                                       # registry unavailable → fall through (fail-safe)
        node = p.get("node")                               # surface_output result items carry the node id
        if isinstance(node, str) and node.strip():
            return f"ui://canvas/{node.strip()}"
        return "ui://chrome/inbox"                          # node-less items → the inbox chrome region

    def present_current(self, session_id: str) -> dict:
        """B: the node at the cursor — the next unresolved go-gate — with its `coa` framing + `ui://`
        target. Fail-safe: if `coa` errors (LLM down), present the RAW payload, NEVER block the walk (D)."""
        s = self._load_session(session_id)
        cur = s["cursor"]
        if s.get("done") or cur >= len(s["items"]):
            return {"session": session_id, "done": True, "cursor": cur, "total": len(s["items"])}
        item_id = s["items"][cur]
        framing, raw = None, None
        # ── C1 · GUIDED-SEQUENCE branch (system-initiated show-me) ───────────────────────────────────
        # A guided sequence is a review session whose ITEMS are `ui://<region>/<element>` ADDRESSES (not
        # inbox review-ids). Reuse-only: it rides the SAME start_session/present_current/next organ + the
        # SAME FE per-step view-drive (resolveUiTarget) + spotlight — NO parallel stepper. The ONLY divergence
        # is HERE: a step that IS a ui:// address frames from the CORPUS how-to (address_help, D1) and returns
        # BEFORE the coa() call — so the guided walk is MODEL-FREE BY CONSTRUCTION (coa is what makes the
        # review walk model-dependent, G-41; the tour reads its narration from the registry/corpus, never a
        # model). The prefix check works on cursor 0 too (present_current(0) runs inside start_session before
        # any session flag could be set, so we sniff the item, not a session field).
        if isinstance(item_id, str) and item_id.startswith("ui://"):
            try:
                bundle = self.address_help(item_id)         # the THREE-leg D1 affordance bundle (corpus)
            except Exception as e:                          # malformed address → fail loud, never a silent skip
                raise ValueError(f"guided step {cur} carries an unresolvable address {item_id!r}: {e}")
            # NARRATION: prefer the authored how-to-use; fall back to what-this-is; NEVER empty, NEVER
            # fabricated (registry-is-truth). This lands in `framing` so the EXISTING voice narration effect
            # (useAppController ~1113 reads session.framing) speaks the how-to FOR FREE — we drive the visual
            # sequence + supply the narration TEXT, we never call speakReply (G-8 voice functions untouched).
            corpus_narration = bundle.get("how_to_use") or bundle.get("what_this_is") \
                or f"This is {item_id} — a part of the interface."
            # C2 — COMPOSE the bootstrap's flow-level TEACH (the side-channel, by cursor) WITH the corpus
            # how-to (rule 3: teach is the FLOW framing, not a second source of element how-to). Teach LEADS
            # (it carries the point→ask→surface→approve step), the element's corpus how-to/what-this-is
            # FOLLOWS where it exists — so the narration auto-enriches when the corpus fills the per-element
            # howtos (no drift). When the topic carries no teach (the default tour), narration == the corpus
            # narration BYTE-FOR-BYTE (C1 unchanged). Read defensively (the side-channel may be shorter/absent).
            teach_list = s.get("teach") or []
            teach_text = teach_list[cur] if (isinstance(teach_list, list) and cur < len(teach_list)) else None
            if teach_text:
                # the element's WHAT-THIS-IS as a brief tail (skip the verbose how_to_use leg here — teach is
                # already the teaching voice; what_this_is grounds the element by name without doubling text).
                what = bundle.get("what_this_is")
                narration = f"{teach_text}\n\n({what})" if what else teach_text
            else:
                narration = corpus_narration
            # the FE mount-hint for this step (the side-channel, by cursor): a ui:// address the FE indicates
            # so a hard-gated element (the wire-door) MOUNTS before resolveUiTarget spotlights it. None = no
            # indication for this step. The FE per-step effect calls the EXISTING indicate(addr) (we supply
            # the hint; we never touch the indicate machinery here — fail-loud-safe, registry-validated FE-side).
            indicate_list = s.get("indicate") or []
            indicate_hint = indicate_list[cur] if (isinstance(indicate_list, list) and cur < len(indicate_list)) else None
            # raw carries: a registry-valid per-step ui_target (G-43 — _registry_ui_target honours
            # guide_address) so the FE per-step drive spotlights the REAL element; guide_address as the C1
            # marker the FE branches on (tour vs review card); the full how-to bundle for a richer surface;
            # teach (the step's flow narration) + indicate (the mount-hint) for the C2 teach-to-self-modify tour.
            raw = {"guide_address": item_id, "ui_target": self._registry_ui_target({"guide_address": item_id}),
                   "how_to": bundle, "kind": "guide", "teach": teach_text, "indicate": indicate_hint}
            return {"session": session_id, "cursor": cur, "total": len(s["items"]),
                    "item": item_id, "framing": narration, "raw": raw,
                    "ui_target": item_id,                   # the step's present target IS the element address
                    "done": False, "guide": True}
        try:
            c = self.coa(item_id)                          # decision-compiler UP (D1, reuse)
            framing, raw = c.get("framing"), c.get("raw")
        except Exception as e:                             # FAIL-SAFE: raw payload, never block (guide D)
            d = self.inbox.get(item_id)
            raw = d.get("payload") if d else None
            framing = None
            self._emit("warning", f"coa failed for {item_id} ({type(e).__name__}) — presenting raw payload")
        # T0-KEYSTONE (backend half): STAMP a registry-valid `ui_target` INTO the payload the FE reads as
        # `session.raw.ui_target`. Before this fix nothing wrote a payload-level ui_target, so the FE's
        # per-step view-drive (resolveUiTarget(session.raw?.ui_target)) was ~always undefined → the
        # keystone "the RHM moves your view to the thing it asks about" silently no-op'd. We stamp it
        # onto the presented `raw` (additively — never removing the top-level ui://review/<id>). It is
        # NOT persisted back to the surfaced item (this is a presentation projection — reflects-never-
        # owns), only carried on the response the walkthrough card reads. (FE proof is a separate lane —
        # this is the backend half; at most needs-tim until the FE drive is verified by use.)
        if isinstance(raw, dict) and "ui_target" not in raw:
            raw = dict(raw)
            raw["ui_target"] = self._registry_ui_target(raw)
        # mark presented (lifecycle status only — never touches `resolved`, so it stays a live escalation).
        try:
            self.inbox.set_status(item_id, "presented")
        except (KeyError, ValueError):
            pass
        return {"session": session_id, "cursor": cur, "total": len(s["items"]),
                "item": item_id, "framing": framing, "raw": raw,
                "ui_target": f"ui://review/{item_id}",      # the step's present target (C1 addressing)
                "done": False}

    def start_walkthrough(self, item_ids: list | None = None) -> dict:
        """C4 — the mode-selection → ORGAN-start seam (backend half). Resolves the long-standing
        walkthrough NAMING TRAP: there is a cosmetic presence-DIAL 'walkthrough' MODE (MODE_DIRECTIVES,
        a narration directive only) AND a separate, real walkthrough ORGAN (start_session — the
        screen-driving review engine). Selecting the dial-mode set ONLY the cosmetic directive; it never
        bound to / started the organ. This method UNIFIES the seam: SELECTING the guided/walkthrough
        experience now (a) sets the presence dial to 'walkthrough' (the cosmetic mode — kept, so the RHM
        speaks in guide register) AND (b) actually STARTS the organ over the pending review items.

        REUSE-ONLY (no parallel system): it composes the EXISTING set_mode (the dial) + the EXISTING
        pending-item gather (the same `resolved is None` predicate `_affordance_context`/`now` use) +
        the EXISTING start_session organ (which compiles a review-session graph the scheduler runs).
        `set_mode` stays PURE (its widely-called contract is untouched); this is the higher-level
        COMPOSER that binds dial→organ, so callers that want only the cosmetic mode are unaffected.

          • item_ids given  → walk exactly those (operator pre-selected a set).
          • item_ids None   → walk every PENDING unresolved inbox item (the natural "guide me through
                              what needs me" set). The gather mirrors the affordance-context predicate
                              (registry-is-truth: the one definition of 'pending').

        FAIL LOUD, never a silent no-op (rule 4): if there is NOTHING to walk, this does NOT crash and
        does NOT pretend success — it returns {organ_started:False, reason:'…', mode:'walkthrough'} so
        the dial is set (the operator IS in guide mode) but the surface is told plainly there is nothing
        to step through. A populated walk returns start_session's first presentation (present_current of
        cursor 0), tagged organ_started:True + the session id, so the FE can drive the organ view.

        DEFERRED (the FE show-me lane — noted, NOT built here): the FE wiring that CALLS this when the
        operator picks the walkthrough mode on the presence dial, and then DRIVES the organ view per
        step (resolveUiTarget over the per-step ui_target). This is the backend binding + a reachable
        entry; the view-drive is the FE half (would collide with the concurrent canvas/region lane)."""
        mode = self.set_mode("walkthrough")                      # (a) the cosmetic dial — kept, pure reuse
        if item_ids is None:
            # (b) the pending set — the SAME 'resolved is None' predicate the affordance layer uses
            # (one definition of 'pending', registry-is-truth — never a second notion).
            try:
                item_ids = [d.get("id") for d in self.inbox.list()
                            if d.get("resolved") is None and d.get("id")]
            except Exception:
                item_ids = []
        items = [i for i in (item_ids or []) if i]
        if not items:
            # FAIL LOUD (no silent no-op): the dial IS set, but there is nothing to walk — say so plainly.
            self._emit("mode", "walkthrough selected — nothing pending to walk through",
                       address="ui://chrome/chat")
            return {"organ_started": False, "mode": mode,
                    "reason": "no pending review items to walk through "
                              "(surface or capture an item first, then start the walkthrough)"}
        started = self.start_session(items, mode="walkthrough")   # the REAL organ — screen-driving engine
        # carry the session id + the organ_started flag so the surface can drive the organ view.
        return {**started, "organ_started": True,
                "session": started.get("session"), "mode": mode}

    # --- C1 · SYSTEM-INITIATED GUIDED SEQUENCES (the "show me how" tour) ---
    # A guided sequence is the SAME walkthrough organ (start_session/present_current/next) walking
    # `ui://` ELEMENT ADDRESSES instead of inbox review-items. It is SYSTEM-INITIATED: start_guide is
    # directly callable (no operator click needed — the test calls it bare; the RHM/bridge can call it
    # too), distinct from the review-organ's pending-item walk which is operator/dial-triggered. Each step
    # resolves the element's HOW-TO from the corpus (address_help, D1) as narration, drives the view to it,
    # and spotlights it (the FE per-step resolveUiTarget over the registry-valid ui_target, G-43). MODEL-FREE
    # by construction (present_current's guide branch returns before coa) — the tour reads the corpus, never
    # a model, so a model-down can't brick it (the FE still bounds the start, G-41/G-44 reuse).

    # The DEFAULT guided sequence — a registry-true ordered tour of the cockpit's primary affordances.
    # registry-is-truth (rule 8): every address here MUST be a live UI_REGISTRY key (validated in
    # _guide_sequence), never invented. Ordered as a first-run orientation: run → presence-dial → inbox.
    # ui://toolbar/run carries an AUTHORED howto (the seeded D1 text), so the tour opens on real how-to
    # narration; the others narrate their what-this-is leg. Named GUIDE_SEQUENCES so topic-keyed tours
    # extend by adding a key (each filtered to registered addresses at resolve time — registry-is-truth).
    GUIDE_SEQUENCES: dict = {
        "default": ["ui://toolbar/run", "ui://toolbar/presence", "ui://inbox/build-review"],
        # C2 — the BOOTSTRAP tour: teach the operator HOW TO REQUEST A CHANGE AND APPROVE IT FROM INSIDE
        # (point → ask → surface → approve). Every address here is a LIVE registry key (registry-is-truth,
        # filtered in _guide_sequence); the teach-narration (GUIDE_TEACH) + the indicate-hint (GUIDE_INDICATE)
        # ride PARALLEL side-channels keyed by position (the session items stay address STRINGS — the organ
        # keys on a ui:// string; teach/indicate are NOT folded into the items, so C1 stays byte-identical).
        #   • point   ui://toolbar/run        — point at an element (also the indicate-target that MOUNTS the door)
        #   • ask     ui://canvas/wire-request — the request-a-change door (appears because step 1 indicated an element)
        #   • surface ui://inbox              — the build-intent surfaces in the inbox, awaiting you (always-mounted region)
        #   • approve ui://inbox              — you approve it; only then does it dispatch (same region, distinct teach)
        "request-a-change": ["ui://toolbar/run", "ui://canvas/wire-request", "ui://inbox", "ui://inbox"],
        # alias — same bootstrap tour under the self-modify name (both resolve to the request-a-change spine).
        "self-modify": ["ui://toolbar/run", "ui://canvas/wire-request", "ui://inbox", "ui://inbox"],
    }

    # C2 — the flow-level TEACH narration, POSITIONALLY ALIGNED to each topic's GUIDE_SEQUENCES list. This is
    # the BOOTSTRAP's own teaching voice (not per-element how-to — that lives in the corpus, rule 3): each
    # string frames its STEP in the point→ask→surface→approve flow. It is COMPOSED WITH the corpus how-to in
    # present_current (teach leads; the element's authored how_to_use/what_this_is follows where present), so
    # the narration auto-enriches when the corpus fills the per-element howtos (no drift, no second source of
    # element how-to). Model-free (read here, never generated). Topics without a TEACH entry (e.g. 'default')
    # narrate purely from the corpus exactly as C1 did — teach is None → byte-identical C1 behaviour.
    GUIDE_TEACH: dict = {
        "request-a-change": [
            "The first thing to learn here is that you can change the Company from inside it — by sight. "
            "Start by POINTING at any element. Here it's the Run button; it could be any part of the "
            "interface. The element you point at becomes the place you request a change.",
            "With an element pointed at, the request-a-change door appears right here. You describe the "
            "change in plain words — what you want different. Your description becomes a scoped build-intent: "
            "the system works out which code it reaches (the blast radius), you don't have to.",
            "A minted build-intent surfaces here, in the inbox's decision-to-build lane, awaiting you. It "
            "shows what the change is and how far it reaches. Nothing has run yet — minting a build-intent "
            "composes a plan, it does not modify anything.",
            "Approval is yours alone — and it is safe by default. You approve the build-intent; that records "
            "your verdict, but nothing modifies the Company yet. The wire stays in plan-mode (inert) until it "
            "is deliberately armed, so an approved change is a plan awaiting that final go — you can always "
            "ask first ('shall I?'). This is the loop that lets you grow the Company by sight: point, ask, "
            "approve — with no change ever made behind your back.",
        ],
    }
    GUIDE_TEACH["self-modify"] = GUIDE_TEACH["request-a-change"]

    # C2 — the per-step INDICATE hint (the FE reads raw.indicate and calls the EXISTING indicate(addr) so a
    # hard-gated element MOUNTS before the spotlight). POSITIONALLY ALIGNED. The wire-door (ui://canvas/wire-
    # request) renders ONLY when a ui:// element is indicated (clickMode==='annotate'); so the 'point' step
    # indicates ui://toolbar/run, which MOUNTS the door for the 'ask' step's spotlight. The later inbox steps
    # carry no indicate (the door may stay up — harmless; the spotlight moves to the inbox region). A None per
    # position = no FE indication for that step. Topics without an entry (default) = no indication anywhere.
    GUIDE_INDICATE: dict = {
        "request-a-change": ["ui://toolbar/run", None, None, None],
    }
    GUIDE_INDICATE["self-modify"] = GUIDE_INDICATE["request-a-change"]

    def _guide_sequence(self, topic: str | None = None) -> list:
        """Resolve a topic → an ORDERED list of registry-valid `ui://` addresses for the guided walk.
        registry-is-truth (rule 8): a candidate address is kept ONLY if it is a live UI_REGISTRY key
        (build_ui_info) — an unregistered/typo address is DROPPED (never drives the FE to a dead ref).
        An unknown topic falls back to 'default' (the orientation tour). Fail loud at the CALLER
        (start_guide) if the resolved list is empty after the registry filter."""
        return [a for a, _t, _i in self._guide_steps(topic)]

    def _guide_steps(self, topic: str | None = None) -> list:
        """C2 — resolve a topic → ORDERED (address, teach, indicate) triples, PAIRED so the registry filter
        keeps teach/indicate aligned to the surviving addresses (filtering by address alone would misalign a
        positional teach list). registry-is-truth: an address is kept ONLY if it is a live UI_REGISTRY key
        (build_ui_info) — a dropped address takes its teach+indicate with it. teach is the flow-level
        narration (GUIDE_TEACH, None when the topic authors none → C1-identical corpus-only narration);
        indicate is the FE mount-hint (GUIDE_INDICATE, None when none). An unknown topic falls back to
        'default'. The CALLER (start_guide) fail-louds if the resolved list is empty after the filter."""
        key = (topic or "default").strip().lower()
        addresses = self.GUIDE_SEQUENCES.get(key) or self.GUIDE_SEQUENCES["default"]
        teach = self.GUIDE_TEACH.get(key) or []
        indicate = self.GUIDE_INDICATE.get(key) or []
        try:
            reg = self.build_ui_info()
        except Exception:
            reg = {}
        out = []
        for idx, a in enumerate(addresses):
            if reg and a not in reg:
                continue                                    # registry-is-truth — drop unregistered, with its teach+indicate
            out.append((a,
                        teach[idx] if idx < len(teach) else None,
                        indicate[idx] if idx < len(indicate) else None))
        return out

    def start_guide(self, topic: str | None = None) -> dict:
        """C1 — start a SYSTEM-INITIATED guided sequence (the "show me how" tour). Composes the EXISTING
        walkthrough organ over `ui://` element ADDRESSES (REUSE-ONLY, no parallel stepper): set the
        presence dial to 'walkthrough' (so the RHM speaks in guide register — same as start_walkthrough)
        + start_session over the resolved address sequence. Each step narrates the element's corpus
        how-to (address_help) and spotlights the real element (present_current's guide branch + G-43).

        SYSTEM-INITIATED: callable directly (no operator click) — the bridge route + the RHM can invoke
        it. DISTINCT from start_walkthrough (which walks pending INBOX items): a guide walks the
        INTERFACE's own addressed elements, teaching what each is + how to use it, model-free.

        FAIL LOUD (rule 4 — no silent no-op): if the topic resolves to NO registered addresses, this
        does NOT crash and does NOT pretend success — it returns {organ_started:False, reason:'…',
        mode:'walkthrough', topic} so the dial is set but the surface is told plainly there is nothing to
        tour. A populated guide returns start_session's first presentation (cursor 0) tagged
        organ_started:True + guide:True + the session id, so the FE drives the tour view per step."""
        steps = self._guide_steps(topic)                        # (address, teach, indicate) triples (registry-filtered, paired)
        addresses = [a for a, _t, _i in steps]
        teach = [t for _a, t, _i in steps]                       # the flow-level teach narration, aligned to the kept addresses
        indicate = [i for _a, _t, i in steps]                    # the FE mount-hints, aligned to the kept addresses
        mode = self.set_mode("walkthrough")                      # the cosmetic dial — kept, pure reuse
        if not addresses:
            # FAIL LOUD: the dial IS set, but there is nothing to tour — say so plainly (no silent no-op).
            self._emit("mode", f"guide selected (topic={topic or 'default'}) — no registered addresses to tour",
                       address="ui://chrome/chat")
            return {"organ_started": False, "mode": mode, "topic": topic or "default", "guide": True,
                    "reason": "no registered UI addresses resolved for this guide topic "
                              "(the sequence is registry-filtered — nothing to tour)"}
        # teach/indicate ride PARALLEL side-channels onto the session record (the items stay address STRINGS,
        # so the organ + C1 are unchanged); present_current's guide branch reads them by cursor. Pass None
        # when the topic carries no teach/indicate (the default tour) so the session record stays C1-shaped.
        started = self.start_session(addresses, mode="walkthrough",
                                     teach=teach if any(teach) else None,
                                     indicate=indicate if any(indicate) else None)   # the REAL organ — model-free guide branch
        self._emit("guide.start", f"guided sequence started — {len(addresses)} step(s), topic={topic or 'default'}",
                   session=started.get("session"), topic=topic or "default", address="ui://chrome/chat")
        return {**started, "organ_started": True, "guide": True,
                "session": started.get("session"), "mode": mode, "topic": topic or "default",
                "steps": addresses}

    def respond(self, session_id: str, choice: str, reason: str = "") -> dict:
        """B→D: record the operator's verdict for the CURRENT step, tagged with the session + position
        (the reuse of resolve_surfaced — no parallel record path). Does NOT advance; `next()` does (B)."""
        s = self._load_session(session_id)
        cur = s["cursor"]
        if cur >= len(s["items"]):
            raise ValueError(f"session {session_id!r} has no current item to respond to (fail loud)")
        item_id = s["items"][cur]
        return self.resolve_surfaced(item_id, choice, reason, session_id=session_id, position=cur)

    def next(self, session_id: str) -> dict:
        """B: the Next page-turn. WRITES the current step's go-address (so the scheduler fires that step;
        the cascade stalls at the NEXT step's still-unresolved gate), advances the cursor, emits
        `review.advance`, returns the next presentation. Idempotent past the end (done).

        ATOMIC cursor advance (concurrency): the load→run→save is a read-modify-write; under the threading
        bridge two concurrent next() calls would both read cursor=N and one advance is LOST. We take the
        per-session lock AND re-load the session FRESH inside it (compare-and-set against the substrate),
        so each next() advances by exactly one distinct step — N concurrent calls = N distinct advances."""
        with self._session_lock(session_id):
            s = self._load_session(session_id)             # re-read INSIDE the lock — the authoritative cursor
            cur = s["cursor"]
            if cur >= len(s["items"]):
                if not s.get("done"):
                    s["done"] = True
                    self.store.save_session(s)
                return {"session": session_id, "done": True, "cursor": cur, "total": len(s["items"])}
            # OPEN this step's gate: write the go-source's logical output address directly (set_ref+
            # put_content — we don't FIRE the source, we resolve its address by hand; the human "go" signal).
            go = self._go_addr(session_id, cur)
            cas = self.store.put_content(f"go:{session_id}:{cur}")
            self.store.set_ref(go, cas)
            if cur not in s.setdefault("opened", []):
                s["opened"].append(cur)
            # run the session graph: only the now-opened step(s) become ready; later steps wait on gates.
            # Pause every go-source so a PORTS_IN={} constant can't auto-fire and open all gates at once.
            gid = s["graph"]
            g = self.store.load_graph(gid)
            pause = [n.id for n in g.nodes if n.id.startswith("go")] if g else []
            self.run(gid, pause=pause)                      # AUTO via guard; fires the opened step(s)
            s["cursor"] = cur + 1
            if s["cursor"] >= len(s["items"]):
                s["done"] = True
            self.store.save_session(s)                      # commit the advance BEFORE releasing the lock
            cursor_now, done_now, total = s["cursor"], s["done"], len(s["items"])
        self._emit("review.advance", f"review session {session_id} → step {cursor_now}",
                   session=session_id, cursor=cursor_now, total=total,
                   address="ui://chrome/chat")   # S2: the review walk presents in the chat/walkthrough organ
        if done_now:
            return {"session": session_id, "done": True, "cursor": cursor_now, "total": total}
        return self.present_current(session_id)

    def session_status(self, session_id: str) -> dict:
        """B: the session's live status — cursor, total, mode, which steps are opened, done."""
        s = self._load_session(session_id)
        return {"session": session_id, "cursor": s["cursor"], "total": len(s["items"]),
                "mode": s.get("mode"), "items": s["items"], "opened": s.get("opened", []),
                "done": bool(s.get("done"))}

    # --- L9: reverse journey-recording (§21.7#2-reverse, fidelity ISSUE-5) -------------------------------
    #
    # The FORWARD direction is done: present_current + resolveUiTarget drive the view TO an address (seam
    # 3 CONFIRM forward). The REVERSE was dropped — no code captured a free click-path through addresses
    # as an ordered journey. The review-session organ above (start_session/present_current/next) records
    # a REVIEW (item-ids walked with a cursor), NOT navigation; a journey is a DISTINCT object that records
    # an addressed PATH. So these methods are a PARALLEL record + capture wire — they do NOT repurpose or
    # overload the review organ (which stays byte-for-byte unchanged), and they REUSE the existing forward
    # resolver for replay (replay_journey hands the FE the ordered addresses; the FE steps through them via
    # the preserved resolveUiTarget — no second navigation mechanism).
    #
    # CAPTURE-TRIGGER decision (the task asks to DECIDE + state): EXPLICIT start/stop journey-recording
    # (the default lean). start_journey() opens a record → each subsequent append_journey_step appends one
    # addressed step → stop_journey() finalizes; replay by id. WHY explicit over auto-capture-of-every-
    # indicate: auto-capture would silently fold ordinary indicate-to-comment clicks (I1) into a journey
    # the operator never asked to record — surprising, and it would couple two unrelated gestures. Explicit
    # start/stop makes recording a deliberate operator act (a journey is a thing you choose to make), and
    # the FE wire only appends while recording is ON — clicks outside a recording are pure indication.
    #
    # STORAGE decision: a NEW journeys open-record in the store (store.save_journey/load_journey), a
    # DISTINCT directory from sessions/ — so a journey id and a session id can never collide (the journey
    # is genuinely a different object, not a session in disguise). It mirrors save_session/load_session
    # (the atomic tmp+replace whole-record write) rather than the append_*.jsonl logs, because a journey is
    # RETRIEVED-WHOLE-BY-ID exactly like a session — that is the truer structural parallel. The record and
    # each step stay OPEN dicts ({id, ts, steps:[{address, ts}], done}) per the append_* {ts,**} additive
    # convention (store constitution: schema-additive). Each step's address is S0-validated by the SAME
    # parse_ui_address gate every other addressed write uses (annotate/attach-chat/address-history) —
    # registry-truth, fail-loud, no fabrication.
    def start_journey(self) -> dict:
        """L9: open a new journey-record (the REVERSE capture). Returns the fresh open record; the FE then
        appends a step per indicated ui:// address while recording is ON, and stops to finalize."""
        import time as _t
        from datetime import datetime, timezone
        journey_id = f"j{int(_t.time()*1000)}-{len(self.store.list_journeys())}"
        journey = {"id": journey_id, "ts": datetime.now(timezone.utc).isoformat(), "steps": [], "done": False}
        self.store.save_journey(journey)
        self._emit("journey.start", f"journey {journey_id} recording started",
                   journey=journey_id, address="ui://chrome/chat")
        return journey

    def append_journey_step(self, journey_id: str, address: str) -> dict:
        """L9: append one addressed step to an OPEN journey. The address is S0-validated (parse_ui_address,
        the SAME grammar gate annotate/attach-chat use) — a malformed address RAISES (fail loud, never a
        junk step). Appending to a finalized/absent journey RAISES (no silent no-op, rule 4). Atomic under
        the per-id lock (concurrent appends each land a distinct step). Returns the updated record."""
        from datetime import datetime, timezone
        from contracts.ui_info import parse_ui_address
        parse_ui_address(address)                              # S0 grammar gate — raises on malformed (BEFORE any mutation)
        with self._session_lock(f"journey:{journey_id}"):     # per-id lock; namespaced so it never aliases a session lock
            j = self.store.load_journey(journey_id)            # re-read INSIDE the lock (compare-and-set against the substrate)
            if not j:
                raise KeyError(f"no journey {journey_id!r} (fail loud)")
            if j.get("done"):
                raise ValueError(f"journey {journey_id!r} is finalized — cannot append (fail loud)")
            j["steps"].append({"address": address, "ts": datetime.now(timezone.utc).isoformat()})
            self.store.save_journey(j)
        self._emit("journey.step", f"journey {journey_id} → {address}",
                   journey=journey_id, address=address)        # the step's OWN address (so the trajectory is addressed too)
        return j

    def stop_journey(self, journey_id: str) -> dict:
        """L9: finalize an open journey (done=True), so it becomes a replayable walkthrough. Idempotent
        past done. Fail loud on an absent journey (no silent no-op)."""
        with self._session_lock(f"journey:{journey_id}"):
            j = self.store.load_journey(journey_id)
            if not j:
                raise KeyError(f"no journey {journey_id!r} (fail loud)")
            if not j.get("done"):
                j["done"] = True
                self.store.save_journey(j)
        self._emit("journey.stop", f"journey {journey_id} finalized — {len(j['steps'])} step(s)",
                   journey=journey_id, address="ui://chrome/chat")
        return j

    def get_journey(self, journey_id: str) -> dict:
        """L9: retrieve a journey-record whole, by id (reflects-never-owns: the store is authoritative)."""
        j = self.store.load_journey(journey_id)
        if not j:
            raise KeyError(f"no journey {journey_id!r} (fail loud)")
        return j

    def replay_journey(self, journey_id: str) -> dict:
        """L9: the REPLAY — hand the FE the ordered ui:// addresses so it can step the view through them
        via the PRESERVED forward resolveUiTarget (no second navigation mechanism; this is the reverse of
        present_current's view-drive). Returns {journey, addresses[], done}; the FE walks `addresses` one
        resolveUiTarget at a time. Each address was S0-validated at capture, so the replay vocabulary is
        the same registry-valid address vocabulary the forward resolver already drives (S0/S1)."""
        j = self.get_journey(journey_id)
        return {"journey": journey_id,
                "addresses": [s["address"] for s in j.get("steps", [])],
                "done": bool(j.get("done"))}

    def list_journeys_meta(self) -> list:
        """L9: the recorded journeys (id · step-count · done), newest-first — the picker the FE replays from."""
        out = []
        for jid in self.store.list_journeys():
            j = self.store.load_journey(jid) or {}
            out.append({"id": jid, "ts": j.get("ts"), "steps": len(j.get("steps", [])), "done": bool(j.get("done"))})
        return sorted(out, key=lambda m: m.get("ts") or "", reverse=True)

    # --- E: the channel back — the system acts, provably from a recorded verdict (the derived-from gate) ---
    def review_verdicts(self, since: int = -1) -> list:
        """E: the recorded verdicts the build loop reads from the STORE (not from Claude Code). Reads
        events_since(cursor) filtered to kind=='resolve' & choice=='approve' (the resolve event carries
        seq·surfaced·choice·reason). Cross-session/crash-safe by construction (it tails the shared log)."""
        return [e for e in self.store.events_since(since)
                if e.get("kind") == "resolve" and e.get("choice") == "approve"]

    def commit_criterion(self, criterion_id: str, sid: str, derived_from: int) -> dict:
        """E: write a criterion as a GOVERNED action whose authorization is READ FROM THE SUBSTRATE —
        REQUIRES `derived_from` = a resolve event's unique `seq`, and verifies the THREE-PART BIND:
        that event is kind=resolve · choice=approve · surfaced==sid, else raise GovernanceError (mirrors
        apply_node→is_approved). Bound to the event `seq` (unique), NOT `sid` (repeats on re-resolve).
        Emits the write WITH `derived_from` for audit. (The loop that CALLS this is lane X.)"""
        if not isinstance(derived_from, int):
            raise GovernanceError(f"commit_criterion requires derived_from = a resolve event seq (int), "
                                  f"got {type(derived_from).__name__} — refused (no ungoverned criterion write)")
        ev = next((e for e in self.store.events_since(-1) if e.get("seq") == derived_from), None)
        if ev is None:
            raise GovernanceError(f"commit_criterion: no event with seq={derived_from} — cannot derive a "
                                  f"criterion from a verdict that doesn't exist (fail loud)")
        if not (ev.get("kind") == "resolve" and ev.get("choice") == "approve" and ev.get("surfaced") == sid):
            raise GovernanceError(
                f"commit_criterion: event seq={derived_from} does not satisfy the three-part bind "
                f"(kind=resolve·choice=approve·surfaced=={sid!r}) — got "
                f"kind={ev.get('kind')!r} choice={ev.get('choice')!r} surfaced={ev.get('surfaced')!r}. Refused.")
        self._emit("criterion.commit", f"criterion {criterion_id} committed (derived from verdict seq={derived_from})",
                   criterion=criterion_id, surfaced=sid, derived_from=derived_from,
                   address="ui://chrome/inbox")   # S2: a criterion commit closes an inbox/review item
        return {"criterion": criterion_id, "surfaced": sid, "derived_from": derived_from, "committed": True}

    def resolve_verdicts_since(self, since: int = -1) -> list:
        """E3: ALL resolve verdicts since the cursor — approve AND reject/needs-change/decide — so the
        build loop can route each. `review_verdicts` (above) is the APPROVE-only slice the commit path
        reads; this is its sibling that also surfaces the negative verdicts the REQUEUE path needs (they
        are invisible to review_verdicts by design). Same shared event log → same crash/cross-session
        safety. Each event carries seq·surfaced·choice·reason (suite.py resolve event)."""
        return [e for e in self.store.events_since(since) if e.get("kind") == "resolve"]

    def requeue_from_verdict(self, sid: str, derived_from: int, note: str = "") -> dict:
        """E3: turn a NEGATIVE verdict (reject / needs-change / actionable-WHY) into a NEW review item —
        the reuse-not-parallel requeue path (it surfaces through the SAME inbox via `surface_review`, no
        second queue). GOVERNED like commit_criterion: REQUIRES `derived_from` = the resolve event's
        unique `seq`, and verifies the bind (kind=resolve · surfaced==sid · choice != approve) so a
        requeue can only be derived from a real, non-approving verdict. The WHY (reason/note) rides along
        — the actionable signal that generalises (I1). The new item starts `inbox`/responsive (it came
        from a build need). Operator-only resolve is untouched: this WRITES a derived item, it never
        resolves anything."""
        if not isinstance(derived_from, int):
            raise GovernanceError(f"requeue_from_verdict requires derived_from = a resolve event seq (int), "
                                  f"got {type(derived_from).__name__} — refused (no ungoverned requeue)")
        ev = next((e for e in self.store.events_since(-1) if e.get("seq") == derived_from), None)
        if ev is None:
            raise GovernanceError(f"requeue_from_verdict: no event with seq={derived_from} — cannot requeue "
                                  f"from a verdict that doesn't exist (fail loud)")
        if not (ev.get("kind") == "resolve" and ev.get("surfaced") == sid and ev.get("choice") != "approve"):
            raise GovernanceError(
                f"requeue_from_verdict: event seq={derived_from} is not a non-approving resolve of {sid!r} "
                f"(kind=resolve · surfaced=={sid!r} · choice!=approve) — got kind={ev.get('kind')!r} "
                f"choice={ev.get('choice')!r} surfaced={ev.get('surfaced')!r}. Refused.")
        item = {"requeued_from": sid, "verdict": ev.get("choice"),
                "why": note or ev.get("reason", ""), "derived_from": derived_from}
        new_sid = self.inbox.surface_review(item, origin="responsive")
        self._emit("review.requeue",
                   f"requeued {sid} ({ev.get('choice')}) → {new_sid} (derived from verdict seq={derived_from})",
                   surfaced=new_sid, requeued_from=sid, derived_from=derived_from, verdict=ev.get("choice"),
                   address="ui://chrome/inbox")   # S2: requeue surfaces a new inbox/review item
        return {"requeued_from": sid, "new_item": new_sid, "verdict": ev.get("choice"),
                "derived_from": derived_from}

    # ============================================================================================
    # The Decision→Implementation Wire (Group W) — recorded decision → governed dispatch to Claude
    # Code → verify → result back → terminal status. No new gate, no confidence value, no second
    # queue: it REUSES the derived_from three-part bind (commit_criterion), the append-only event
    # log (exactly-once + visibility), POLICY (auto-vs-surface), and the separate `status` lane
    # (closes without writing the operator `resolved` field). Kept OFF the MCP face (not in
    # RHM_VERBS) — the RHM proposes/surfaces; it never dispatches a build of its own authority.
    # ============================================================================================

    def _verify_resolve_bind(self, sid: str, derived_from: int, *, require_approve: bool = True):
        """The shared three-part-bind verifier (factored from commit_criterion, suite.py:1114).
        REQUIRES `derived_from` = a resolve event's unique `seq`; verifies kind=resolve · surfaced==sid
        · (choice==approve when require_approve). Returns the bound event, or raises GovernanceError
        (fail loud). The bind is per-unique-seq (not per-sid), the anti-double-action guarantee."""
        # bool is a subclass of int (isinstance(True, int) is True) and True == 1, so a plain
        # isinstance check would let derived_from=True bind to seq 1 — a truthy caller FLAG
        # authorizing the first item's build. Reject bool explicitly: a seq is a genuine int.
        if type(derived_from) is not int:
            raise GovernanceError(
                f"dispatch requires derived_from = a resolve event seq (a genuine int, not bool), got "
                f"{type(derived_from).__name__} — refused (no ungoverned dispatch; authorization is the "
                f"substrate seq-bind, never a caller flag)")
        ev = next((e for e in self.store.events_since(-1) if e.get("seq") == derived_from), None)
        if ev is None:
            raise GovernanceError(
                f"dispatch: no event with seq={derived_from} — cannot derive a build from a verdict that "
                f"doesn't exist (fail loud)")
        ok = ev.get("kind") == "resolve" and ev.get("surfaced") == sid
        if require_approve:
            ok = ok and ev.get("choice") == "approve"
        if not ok:
            raise GovernanceError(
                f"dispatch: event seq={derived_from} does not satisfy the three-part bind "
                f"(kind=resolve·surfaced=={sid!r}" + ("·choice=approve" if require_approve else "") +
                f") — got kind={ev.get('kind')!r} choice={ev.get('choice')!r} "
                f"surfaced={ev.get('surfaced')!r}. Refused.")
        return ev

    def surface_build_intent(self, spec: str, scope: list[str] | None = None,
                             consequence_class: str = "decision_build", why: str = "",
                             address: str | None = None, symbols: list[str] | None = None,
                             context: list[dict] | None = None,
                             blast_radius: dict | None = None) -> dict:
        """W4 PRODUCER: mint a build-intent item — a decision that, once the operator approves it,
        AUTHORIZES an autonomous build of a DECLARED scope. It is distinguished from a plain
        criterion/review by `intent="build"` (the discriminator §W2 — `action` is the governance
        class, so the intent rides the payload) and carries its declared `scope` (the paths it may
        touch) + `consequence_class` (the POLICY class the pre-dispatch gate keys on). The operator's
        `approve` is therefore approve OF THIS SCOPE (legible consent), not a bare agree.

        Surfaced through the SAME inbox (no parallel queue). `resolved` stays None → a live escalation
        until the operator resolves it via /api/resolve (operator-only preserved). Returns {id, ...}.

        Scope entries are normalized (blank entries dropped). An EMPTY declared scope is NOT a soft
        allow-all: the dispatch-time scope-diff treats empty scope as DENY-ALL (_in_any_scope returns
        False for every path), so a build with no declared scope can NEVER close `implemented` — every
        changed path reads as an overrun and surfaces back. This is the durable enforcement (the
        vacuous-enforcement hole closed at the gate that runs, not only at surface time).

        X1/X2 (Convergence) — the PERSISTED payload widens, schema-ADDITIVELY, with the launch-context
        truth so the build composes from disk (not a return-dict mutated AFTER persist, the old bug):
          • `address` (X1) — the `ui://` locus the comment/build derives from. Optional; persisted into
            the OPEN payload record (`inbox.surface` splats it) so the reloaded rec carries it. The 5
            existing fields (intent/spec/scope/consequence_class/why) are untouched; readers that
            `.get(...)` the old fields are unaffected (an absent `address` reads as None, as before).
          • `symbols` (X2) — the `code://` symbol-neighbours `resolve_scope` ALREADY computed for this
            address (the code relationships behind the locus). Reused, never recomputed here; the caller
            (`surface_intent_at`) passes the value it already has. Optional; same additive treatment.
          • `context` (X3) — the ATTACHED-STRATA bundle (comments/chats/history at the address + ancestors)
            that R2's EXISTING `_r2_gather` + `_r2_score_and_cap` assembled at MINT time, bounded by the
            same recency·proximity·pin decay + the `R2_BUDGET` cap the chat gets, deduped (X8), JSON-clean
            ({kind,address,ts,text,pinned} only — `_r2_gather` strips its internal `_raw`). NOT gathered
            here (this method stays a pure persister, X1/X2 character) — the caller (`surface_intent_at`)
            resolves it at mint and passes the bounded list, so the SURFACED record == what the build's
            prompt later composes from (the consent-time trust property, X5). Reused, never a second
            gather; the budget cap stays. Optional; same additive treatment.
        No `schema_ver` exists on the surfaced payload/rec (verified), so none is bumped — these are
        purely additive optional keys on an open `.get`-read record (rule 2, schema-additive)."""
        scope = [s for s in (scope or []) if isinstance(s, str) and s.strip()]
        payload = {"intent": "build", "spec": spec, "scope": scope,
                   "consequence_class": consequence_class, "why": why or spec}
        # X1/X2: thread the launch-context truth INTO the payload BEFORE persist (the old `out["address"]`
        # set AFTER persist never reached disk). Additive + optional — only present when supplied.
        if address is not None:
            payload["address"] = address
        if symbols is not None:
            payload["symbols"] = list(symbols)
        if context is not None:                       # X3: the bounded, deduped attached-strata bundle
            payload["context"] = list(context)        # (resolved at mint by the caller; persister-only here)
        if blast_radius is not None:                  # X16: the BLAST RADIUS (X14) the operator sees at
            payload["blast_radius"] = dict(blast_radius)  # consent time — what the change could REACH. Persisted
            # so (a) the FE surfaces it for reach-approval AND (b) `approve_reach` validates an approved
            # member against the EXACT radius the operator saw (consent-time, not a fresh recompute that
            # could disagree). Persister-only here (the caller resolves it at mint, X1/X2/X3 character).
        # action="review" so it walks the same review lifecycle/UI; the build-intent discriminator is
        # payload["intent"]=="build" (action is the governance class, which surface_review hardcodes).
        sid = self.inbox.surface("review", payload, default="reject", resolved=None,
                                 status="inbox", origin="responsive")
        self._emit("decision.intent",
                   f"build-intent surfaced ({consequence_class}, scope={scope or '∅'}) — awaiting operator approval",
                   surfaced=sid, intent="build", consequence_class=consequence_class, scope=scope,
                   address="ui://chrome/inbox")   # S2: a build-intent surfaces in the inbox (live-registry-valid;
                                                  # finer ui://inbox/build-review awaits S0's grammar unification)
        return {"id": sid, "intent": "build", "scope": scope, "consequence_class": consequence_class}

    def surface_intent_at(self, ui_addr: str, text: str, source: str = "operator",
                          consequence_class: str = "decision_build", why: str = "") -> dict:
        """L1 (§21.4#2) — a COMMENT-AT-AN-ADDRESS becomes a build-intent that surfaces for approval AT
        that address. The addressed-feedback → wire entry seam: "this run button is too loud" on
        `ui://chat/input` becomes a build-intent scoped to the code behind that address, awaiting the
        operator's approve.

        COMPOSES three EXISTING pieces (rule 3 — one source; never a parallel intent path):
          1. `ingest_comment` (I6) — RECORD the comment at the address (its `annotation://` branch +
             the located-gold chat turn). The comment IS the located gold label; it persists at the
             locus AND becomes the build's spec. This is the SAME wired comment-ingest path the FE's
             /api/annotate uses — L1 does not duplicate it.
          2. `resolve_scope` (S3) — JOIN `ui://` → `code://` symbol(s) → repo-relative `scope[]`. The
             SAME corpus-side resolver L5 used (`self_changes_at`); never re-derived. So the build
             "lands at the address you touched" — its declared scope IS the code behind that address.
          3. `surface_build_intent` (the wire's production FRONT DOOR, suite.py:2962) — mint the
             build-intent with that scope. REUSED UNCHANGED: empty-scope=DENY-ALL + `resolved=None`
             (a live escalation until the operator resolves) hold exactly as they do for /api/build-intent.

        EMPTY / STALE SCOPE = DENY-ALL (the headline safety property, rule 8): S3's scope is passed
        STRAIGHT THROUGH to `surface_build_intent`. If the address has no referencing code symbol
        (orphan / CSS-selector ref) or the corpus is unreadable (stale), S3 returns an EMPTY scope —
        which `surface_build_intent`'s dispatch-time scope-diff treats as DENY-ALL (`_in_any_scope`
        False for EVERY path), so the build can NEVER close `implemented`. We NEVER fabricate a broad
        scope to "make it buildable" (= confabulation, the same failure as not acting). We mirror L5's
        propagate-`stale`/`note`-straight-through: the gap is fail-loud-LEGIBLE in the return + folded
        into the build-intent `why`, never a silent empty that lies "buildable anywhere."

        OPERATOR-ONLY APPROVAL (no-bypass, server.py:158): the build-intent is SURFACED here
        (`resolved=None`) but APPROVED by the OPERATOR via `/api/resolve` (operator-only, off the MCP
        face). L1 STOPS at surfacing for approval. Dispatch-on-approve is L2 — a separate, deliberate
        switch (this method NEVER calls dispatch_decision).

        S0 GATE: `ingest_comment`/`resolve_scope` both validate the address (parse_ui_address RAISES on
        a malformed ui://), and `ingest_comment` fails loud on empty text — so a junk comment can never
        mint a build-intent. Returns {id, intent, scope, consequence_class, address, stale, note}."""
        # 1. RECORD the comment at the address (I6 — fails loud on malformed address / empty text).
        self.ingest_comment(ui_addr, text, source=source)
        # 2. RESOLVE the code scope (S3 — reused, never duplicated). Empty/stale ⇒ DENY-ALL, carried legibly.
        scoped = self.resolve_scope(ui_addr)
        scope = scoped.get("scope") or []
        symbols = scoped.get("symbols") or []   # X2: the code:// neighbours, REUSED (never recomputed)
        stale, note = bool(scoped.get("stale")), (scoped.get("note") or "")
        # X3: gather the ATTACHED-STRATA bundle at the address — at MINT/consent time, so the surfaced
        # record == what the build later composes from (the consent-time trust property, X5). REUSE R2's
        # EXISTING machinery (NO second gather): `_r2_gather` (annotations + chats + addressed events at
        # the locus AND its ancestors, deduped by X8, `_raw` stripped → JSON-clean {kind,address,ts,text,
        # pinned}) then `_r2_score_and_cap` (the recency·proximity·pin decay + the SAME `R2_BUDGET` cap the
        # chat gets — the persisted bundle is the SAME bounded slice, never an unbounded dump). The mint
        # comment was just recorded by `ingest_comment` above, so the gather picks it up (counted ONCE via
        # X8). FAIL-LOUD-LEGIBLE, mirroring `_resolve_context_at`'s posture: an error WARNS (address-stamped)
        # + omits the key (never persist a half-bundle silently); we must NOT crash the mint (losing the
        # operator's build-intent over a context hiccup is the worse failure). Empty (nothing attached) →
        # `[]` persisted (honest, parallels orphan symbols=[]); gather errored → key omitted (distinct signal).
        from datetime import datetime as _dt, timezone as _tz
        context = None
        try:
            context = self._r2_score_and_cap(self._r2_gather(ui_addr), ui_addr, _dt.now(_tz.utc))
        except Exception as e:
            self._emit("warning", f"X3 mint-time context gather failed ({type(e).__name__})", address=ui_addr)
            context = None   # omit the key — never persist a partial bundle (fail-loud, not silent-partial)
        # X16: compute the BLAST RADIUS (X14) at MINT/consent time and persist it, so the operator
        # sees WHAT THE CHANGE COULD REACH (co-reference + structural dependents-to-verify /
        # dependencies-to-respect + semantic) BEFORE approving, and so `approve_reach` validates an
        # approved member against the EXACT radius surfaced (consent-time, never a fresh recompute that
        # could disagree). REUSE `blast_radius` (X9+X14) — no parallel system, no new substrate. The
        # method is already graceful-empty + fail-loud-legible (orphan/stale → empty kinds + a note,
        # never a crash), so an orphan address yields an empty radius (nothing to expand → DENY-ALL
        # stays DENY-ALL). FAIL-LOUD-LEGIBLE, mirroring the context gather above: a hiccup WARNS
        # (address-stamped) + omits the key (never persist a half-radius silently) — never crash the
        # mint (losing the operator's build-intent over a radius hiccup is the worse failure).
        radius = None
        try:
            radius = self.blast_radius(ui_addr)
        except Exception as e:
            self._emit("warning", f"X16 mint-time blast_radius failed ({type(e).__name__})", address=ui_addr)
            radius = None   # omit the key — never persist a partial radius (fail-loud, not silent-partial)
        # legible consent (I1): the build derives from THIS address + comment. Fold the scope gap into
        # `why` so the operator's approve sees WHY it's empty (fail-loud-legible, never a silent empty).
        reason = why or f"comment at {ui_addr}: {str(text).strip()[:200]}"
        if not scope:
            reason += f" — [no resolvable code scope: {note or 'orphan/CSS-selector address'} — DENY-ALL]"
        # 3. MINT through the wire's UNCHANGED front door (empty-scope=DENY-ALL + resolved=None reused).
        #    X1/X2/X3: the address + the already-computed symbols + the mint-time R2 context bundle are
        #    threaded INTO the payload here, so the PERSISTED record carries the launch-context truth
        #    (consent-time: the surfaced record == what the build later composes from). The old
        #    `out["address"]=ui_addr` AFTER surface_build_intent only mutated the return dict — never
        #    reached disk; the payload threading is the durable fix.
        out = self.surface_build_intent(str(text).strip(), scope=scope,
                                        consequence_class=consequence_class, why=reason,
                                        address=ui_addr, symbols=symbols, context=context,
                                        blast_radius=radius)
        out["address"] = ui_addr   # kept on the RETURN dict too (callers/return-readers unaffected)
        out["stale"] = stale
        out["note"] = note
        return out

    @staticmethod
    def is_build_intent(decision: dict) -> bool:
        """The loop's discriminator (§W2): distinguish a 'go build this' decision from a 'mark a
        criterion done' approve. True only when the payload carries intent=='build'."""
        return bool(decision) and (decision.get("payload") or {}).get("intent") == "build"

    def _already_dispatched(self, derived_from: int) -> bool:
        """EXACTLY-ONCE (Round 2 Hole 1): the durable claim lives in the append-only crash-safe event
        log, NOT a cursor/lock. A prior `decision.dispatch` keyed on this resolve `seq` means this work
        already launched — refuse the second (checked BEFORE we emit our own claim, so emit-then-check
        can't find its own emission)."""
        return any(e.get("kind") == "decision.dispatch" and e.get("derived_from") == derived_from
                   for e in self.store.events_since(-1))

    # ============================================================================================
    # WIRE-HARDEN (H1–H8) — the wire's definition-of-done == the HUMAN BUILD LOOP's discipline.
    # ------------------------------------------------------------------------------------------
    # The wire is an autonomous build engine; its old "verified" was essentially "claude -p exited
    # and a file changed" — far weaker than the loop, which runs the suites + drift + a separate
    # review. That gap let the reverse incident through (a node-type built but the self-description
    # NOT refreshed → drift went red, silently). These helpers make the wire's verify REAL,
    # fail-loud, and surface-back-on-miss: the build re-discovers into the LIVE system (H3),
    # regenerates the factual self-description (H2), runs the affected acceptance suites + drift
    # (H1/H2), runs an adversarial CRITIC (H5), and refuses to auto-close anything that touches an
    # operator-facing surface (H4 — form can't be machine-verified until the design system exists).
    # ANY miss → fail loud → surface back, never a silent close (H6). All steps are INJECTABLE so
    # tests prove them deterministically without burning a real `claude -p` or a slow suite run.
    # ============================================================================================

    # the self-description files a build may always touch (H8) — H7 instructs the build to update them,
    # so they are upkeep, not out-of-scope wandering. The overrun check (H8) treats these as in-scope.
    _SELF_DESC_FILES = ("AGENTS.md", "MAP.md", "STATE.md")
    # operator-facing surface (H4): a build that changes anything under these CANNOT auto-close — its
    # FORM is unverifiable until the design system + design-critic/design-lint are wired. It surfaces.
    _SURFACE_PREFIXES = ("canvas/",)

    def _affected_suites(self, changed_files: list[str], scope: list[str]) -> list[str]:
        """H1 — which acceptance suites COULD this build break. The deterministic gate (no confidence):
        a change under `runtime/` or `store/` etc. can break the suites that exercise that module, and
        a node-type change can break node/registry/drift suites — so we always include `drift_acceptance`
        (H2) + the wire suites (this verify path itself), and add any suite whose name shares a module
        token with a changed/scoped path. The default verifier runs THESE (not all tests/*.py — several
        burn live models / are slow); the task allows 'at least the suites the change could affect + drift'.
        A node-type build (`nodes/`) → node/registry/drift/wire suites must stay green."""
        all_suites = set(self._acceptance_suites())
        affected = set()
        # ALWAYS: drift (the reverse incident) + the wire's own suites (this path must keep holding).
        for must in ("drift_acceptance", "wire_acceptance", "wire_loop_acceptance", "wire_adversarial"):
            if must in all_suites:
                affected.add(must)
        # module tokens touched by the change (changed paths + declared scope dirs).
        tokens = set()
        for p in list(changed_files or []) + list(scope or []):
            head = (p or "").strip().lstrip("./").split("/")[0]
            if head and head.endswith(".py"):           # a top-level file like 'MAP.md' has no module token
                continue
            if head:
                tokens.add(head.lower())
        # a node-type change can break the registry/drift/compose proofs — pull those in by token too.
        for s in all_suites:
            sl = s.lower()
            if any(tok and tok in sl for tok in tokens):
                affected.add(s)
            # a nodes/ change is a registry change — the registry/type suites guard it.
            if "nodes" in tokens and any(k in sl for k in ("registry", "e4", "compose", "walking", "polr")):
                affected.add(s)
        return sorted(affected)

    def _run_suites(self, suites: list[str], *, runner=None) -> tuple[bool, str]:
        """H1 — run the given acceptance suites as the loop does (`./.venv/bin/python tests/<s>.py`) and
        return (all_green, reason). FAIL LOUD: a non-zero exit = that suite broke → not green. `runner`
        is INJECTABLE (tests supply a deterministic pass/fail map so no slow/real suite is burned); the
        DEFAULT runner is the real subprocess so a live build is gated for real. A suite that ERRORS to
        run (missing interpreter, crash) is treated as RED (a build that breaks the harness is not done)."""
        if not suites:
            return True, "no affected suites to run"
        run = runner or self._default_suite_runner
        failed = []
        for s in suites:
            try:
                ok, detail = run(s)
            except Exception as e:                          # a runner crash is a RED suite, never a silent pass
                ok, detail = False, f"runner crashed on {s}: {type(e).__name__}: {e}"
            if not ok:
                failed.append(f"{s} ({detail})" if detail else s)
        if failed:
            return False, "acceptance suite(s) FAILED: " + "; ".join(failed)
        return True, f"all {len(suites)} affected suite(s) green: {', '.join(suites)}"

    def _default_suite_runner(self, suite: str) -> tuple[bool, str]:
        """The REAL suite runner (default): spawn the suite as the convergence record prescribes. A
        non-zero exit = RED (fail loud). Uses the repo's venv python if present, else the running one."""
        import subprocess, sys as _sys
        venv_py = os.path.join(self._repo_root, ".venv", "bin", "python")
        py = venv_py if os.path.exists(venv_py) else _sys.executable
        path = os.path.join(self._repo_root, "tests", suite + ".py")
        if not os.path.exists(path):
            return False, f"suite file missing: {path}"
        proc = subprocess.run([py, path], cwd=self._repo_root, capture_output=True, text=True,
                              timeout=600)
        if proc.returncode != 0:
            tail = (proc.stdout or "")[-400:] + (proc.stderr or "")[-400:]
            return False, f"exit={proc.returncode}; tail={tail!r}"
        return True, "exit=0"

    # ── the live-dependency REGISTRY: suites KNOWN to need an external service to pass ──────────────
    # This is the gate's safeguard against BOTH false alarms AND masked reds. A suite NOT in this map is
    # NEVER auto-excused — ANY failure = red (loud), so a genuinely-new broken suite always surfaces. A
    # suite IN this map is excused ONLY when its failure output shows a down-signal — so a REAL assertion
    # bug inside a live-dep suite (no down-signal) still surfaces as red, never masked. The map GROWS
    # DELIBERATELY (a new live-integration suite is added here on purpose), never silently — so it doubles
    # as the documentation of which suites have external deps + what each needs.
    _LIVE_DEP_SUITES = {
        "embeddings_acceptance":     "the embed server (:8001)",
        "stt_models_acceptance":     "an STT model endpoint",
        "stt_whispercpp_acceptance": "whisper.cpp + Kokoro TTS (:4123) to synth a clip to transcribe",
        "voice_circuit_acceptance":  "a running bridge (:8771) for the live STT→chat→TTS hops",
    }
    # the signals (anywhere in a suite's FULL output) that mean 'a live dependency is down' — the
    # deliberate `SKIP (LOUD)` / `unreachable` convention + the connection-error shapes. A real
    # AssertionError matches none of these, so an in-registry suite that fails for a REAL reason is red.
    _DOWN_SIGNALS = ("skip (loud)", "unreachable", "connection refused", "max retries", "newconnectionerror",
                     "econnrefused", "server-down", "skipped-server-down", "selected-but-down",
                     ":8001", ":8002", ":4123", ":4125", ":8771", "11434", "no module named 'torch'")

    def _full_suite_runner(self, suite: str) -> tuple[bool, str]:
        """Like _default_suite_runner but returns the FULL output (not a 400-char tail) so the down-signal
        classification sees a `SKIP (LOUD)` line wherever it occurs in the run, not only at the end."""
        import subprocess, sys as _sys
        venv_py = os.path.join(self._repo_root, ".venv", "bin", "python")
        py = venv_py if os.path.exists(venv_py) else _sys.executable
        path = os.path.join(self._repo_root, "tests", suite + ".py")
        if not os.path.exists(path):
            return False, f"suite file missing: {path}"
        proc = subprocess.run([py, path], cwd=self._repo_root, capture_output=True, text=True, timeout=600)
        return proc.returncode == 0, (proc.stdout or "") + (proc.stderr or "")

    def suite_health(self, *, runner=None, exclude=("suite_health_acceptance",)) -> dict:
        """THE STANDING ALL-GREEN GATE (added 2026-06-08, after the cross-session unification proved this
        catch missing: 3 reds slipped the gate layer — conv_reach + event_address sat RED undetected, and
        json_schema_transport false-greened by INVOCATION [passed with PYTHONPATH, failed standalone]).

        WHY the old gates missed them: `doc_drift` checks every suite is LISTED in STATE — not that it
        PASSES; `_affected_suites`/`_run_suites` (the wire's per-build gate) runs ONLY the suites a build
        touches — so a red in an untouched suite accumulates silently forever; and nothing ran suites
        STANDALONE, so an invocation-dependent false-green was invisible.

        This runs EVERY acceptance suite STANDALONE (the same fail-loud subprocess pattern, so
        invocation-dependent false-greens are caught too) and CLASSIFIES each: green / needs-live-dep
        (a DOCUMENTED external-service skip via `_LIVE_DEP_SUITES` — NOT a code red) / red. The registry
        bounds the excuse: only listed suites can be excused, and only when their output shows a
        down-signal, so neither a false alarm NOR a masked real red gets through. Fail-loud source of
        truth for 'is the whole suite green'. SLOW (spawns every suite) → a PRE-MERGE / PRE-DEPLOY /
        periodic standing gate, not a per-build one. EXCLUDES itself (recursion guard). `runner` injectable.
        Returns {green, needs_dep, red:[(suite, detail)], all_green, counts}."""
        run = runner or self._full_suite_runner
        suites = [s for s in self._acceptance_suites()
                  if s.endswith("_acceptance") and s not in exclude]
        green, needs_dep, red = [], [], []
        for s in suites:
            try:
                ok, out = run(s)
            except Exception as e:                          # a runner crash is RED, never a silent pass
                ok, out = False, f"runner crashed: {type(e).__name__}: {e}"
            out = out or ""
            if ok:
                green.append(s)
            elif s in self._LIVE_DEP_SUITES and any(sig in out.lower() for sig in self._DOWN_SIGNALS):
                needs_dep.append(s)                         # KNOWN live-dep + down-signal → documented skip
            else:
                red.append((s, out.strip()[-300:]))         # everything else = red (loud), never excused
        return {"green": sorted(green), "needs_dep": sorted(needs_dep),
                "red": sorted(red), "all_green": not red,
                "counts": {"green": len(green), "needs_dep": len(needs_dep), "red": len(red),
                           "total": len(suites)}}

    # ── the REACHABILITY registry: /api routes that reach NO front-end or test caller (built-but-unwired) ──
    # The disconnection class the all-green gate CANNOT catch: a route that works fine but nothing calls it
    # has no failing test — it just sits there invisible (the X16 seam was a cousin; the latent gold + the
    # cognition authoring endpoints are live instances). This CATALOGUES every current orphan with a tag, so
    # the orphan set is ACCOUNTED-FOR (the gate passes) but the registry doubles as the connect-it BACKLOG;
    # a NEW orphan not listed here = the gate FAILS (a fresh built-but-unwired disconnection, caught the
    # moment it appears). Tags: to_build_ui (needs a screen — a Claude Design target) · to_wire (built,
    # should have an FE caller — a real connect-it item) · voice_owned (the concurrent voice session's lane)
    # · backend_only (legitimately no FE — an agent/operator/internal entry point).
    # The orphan-route disposition catalogue is NO LONGER a hardcoded dict (it was — flagged by the
    # no-hardcoding rule + round 1 as "right shape, wrong form"). It is a DECLARED registry read from
    # design/_system/orphan-routes.json (registry-is-truth) via _orphan_routes(). This is the first
    # concrete finding-store step: a persisted, declared disposition catalogue the gate reads from one
    # source, generalising later into the dispositioned finding-store.
    def _orphan_routes(self) -> dict:
        """Load the declared orphan-route disposition catalogue {route: (tag, note)} from the registry
        file. FAIL LOUD if the file is missing/malformed (rule 4 — never silently treat every orphan as
        new). Cached per-instance."""
        cached = getattr(self, "_orphan_routes_cache", None)
        if cached is not None:
            return cached
        import json
        path = os.path.join(self._repo_root, "design", "_system", "orphan-routes.json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        cat = {r: (e["tag"], e.get("note", "")) for r, e in data["routes"].items()}
        self._orphan_routes_cache = cat
        return cat

    def reachability(self) -> dict:
        """THE REACHABILITY GATE (added 2026-06-08). Catches the disconnection class the all-green gate
        cannot: a built `/api` route that reaches NO front-end or test caller — it works, so no test fails,
        but nothing uses it (built-but-unwired). Extraction is AST-grounded (a route literal in a real
        `self.path ==`/`in` routing decision, NOT one mentioned in a comment/docstring) and the consumer
        check is call-marker-based on the COMMENT-STRIPPED corpus (a real fetch/EventSource/HTTP call, NOT a
        mere mention/existence-assertion/prose-in-a-string) — both in `runtime/coherence_detect.py`. This
        fixes the measured false-WIRE bug (a dead route reading as 'wired' because its name appears in a
        comment/assertion/label — the dangerous silent direction). The disposition catalogue is the DECLARED
        registry (`_orphan_routes()`, from design/_system/orphan-routes.json): a catalogued orphan is
        ACCOUNTED-FOR (the backlog); an orphan NOT listed is a NEW disconnection → the gate fails; a
        catalogued route now wired/removed is STALE → self-corrects. Returns {wired, documented:[(route,tag,
        note)], new_orphans, stale, all_accounted, counts, backlog}."""
        from runtime import coherence_detect as _cd
        catalogue = self._orphan_routes()
        routes_set, wired_map = _cd.route_reachability(self._repo_root)
        routes = sorted(routes_set)
        wired = [r for r in routes if wired_map.get(r)]
        orphan = [r for r in routes if not wired_map.get(r)]
        documented = [(r, *catalogue[r]) for r in orphan if r in catalogue]
        new_orphans = [r for r in orphan if r not in catalogue]
        stale = [r for r in catalogue if r not in orphan]   # listed but now wired/removed
        backlog = {tag: sorted(r for r, t, _ in documented if t == tag)
                   for tag in ("to_build_ui", "to_wire", "voice_owned", "backend_only")}
        return {"wired": sorted(wired), "documented": sorted(documented),
                "new_orphans": sorted(new_orphans), "stale": sorted(stale),
                "all_accounted": not new_orphans, "backlog": backlog,
                "counts": {"routes": len(routes), "wired": len(wired), "orphan": len(orphan),
                           "new": len(new_orphans), "stale": len(stale)}}

    def _make_live_and_refresh(self) -> tuple[bool, str]:
        """H3 + H2a — re-discover into the RUNNING system so a new node-type is LIVE (in self.registry,
        not just on disk), THEN regenerate the factual self-description blocks FROM the now-current
        registry. This is the exact fix for the reverse incident: rediscover → refresh BEFORE the drift
        check, so MAP/STATE reflect the new capability and drift reads GREEN. Uses rediscover() (clear +
        discover) so a removed/renamed node un-registers too (the wire can do anything, unlike apply_node
        which only adds). FAIL LOUD: a syntactically broken node makes exec_module raise during
        rediscover — that is a legitimate verify MISS (the build broke the registry), returned as a
        reason, never crashing dispatch_decision."""
        try:
            self.registry.rediscover([self.nodes_dir])
        except Exception as e:
            return False, (f"re-discovery FAILED ({type(e).__name__}: {e}) — the build left the node "
                           f"registry un-loadable (a broken node-type). Not live; surfaced back.")
        try:
            self.refresh_self_description()                 # H2a: factual MAP/STATE blocks, from the live registry
        except Exception as e:
            return False, f"self-description refresh FAILED ({type(e).__name__}: {e}) — surfaced back."
        return True, "re-discovered into the live registry + refreshed the factual self-description"

    def _touches_surface(self, changed_files: list[str]) -> list[str]:
        """H4 — did the build change an operator-facing surface (anything under canvas/)? Such a change
        CANNOT auto-close: its FORM (design-system components + tokens, coherent layout — AGENTS.md
        rule 9) is the product bar, and there is NO design system wired to machine-check it yet. So a
        surface-touching build surfaces for review instead of closing. Returns the offending paths."""
        out = []
        for p in (changed_files or []):
            q = (p or "").strip().lstrip("./")
            if any(q == pre.rstrip("/") or q.startswith(pre) for pre in self._SURFACE_PREFIXES):
                out.append(p)
        return out

    # F9 — where the corpus FORM lint lives. `design/_system/check.py` is a fixed part of THIS codebase
    # (it ships beside suite.py), NOT in the build's _repo_root sandbox — so it is located off suite.py's
    # own location, while the CHANGED files are resolved against _repo_root (the build's tree).
    def _design_lint_corpus(self) -> str:
        """The in-repo corpus design-lint script (design/_system/check.py). suite.py lives in
        runtime/, the corpus in design/_system/ — both under the same source root, so derive it from
        THIS file's location (the sandbox _repo_root has no corpus)."""
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "design", "_system", "check.py")

    def _design_critic(self, changed_files: list[str]) -> tuple[bool, str]:
        """F9 — the LIVE in-repo FORM gate (graduated from the stub, review-executability V-1).

        THE MACHINE HALF of FORM lives here: it runs the corpus design-lint (design/_system/check.py
        --target <changed canvas file> --fail-on) over the surface files this build CHANGED.
          • A clean, token-only surface change → lint exits 0 → (True, …): the UI self-build may
            AUTO-CLOSE (no second manual gate — approval already happened at the build-intent guard).
          • A surface change introducing an off-token literal (raw hex/rgba instead of var(--x)) or a
            bespoke element → lint exits non-zero → (False, reason): the build is GATED, surfaces back.
          • FAIL-SAFE: if the lint cannot run AT ALL — corpus missing, interpreter/script error, a
            changed file that doesn't resolve to a real file on disk, ANY exception — this returns
            (False, reason). Unverifiable is NOT-passed; it NEVER silently returns True (rule 4).
        A pure-backend build (no canvas/ change) has no form to grade → (True, …); it proceeds.

        THE HUMAN-JUDGMENT HALF (the design-critic AGENT — browser + screenshots, the design rubric
        its only lens) is NOT run in-process: a headless dispatch can't drive a browser, and the
        implementer can't grade its own form (AGENTS.md rule 9). The loop dispatches that agent
        SEPARATELY at verify time. Subjective taste it can't machine-settle → flagged for Tim, never
        green-painted. This method is the deterministic in-repo gate; the agent is the loop's stage."""
        surface = self._touches_surface(changed_files)
        if not surface:
            return True, "no operator-facing surface touched → no FORM gate (backend build may proceed)"

        script = self._design_lint_corpus()
        if not os.path.exists(script):
            # FAIL-SAFE: the corpus lint is absent → FORM is unverifiable → not-passed (never silent True).
            return (False, f"FORM unverifiable (fail-safe): the corpus design-lint {script} is missing — "
                           f"cannot machine-check the surface change {surface}. Surfaced for design review.")

        # Lint only the surface files THIS build changed (a clean change must not be gated by pre-existing
        # dirt elsewhere). Resolve each against _repo_root (the build's tree). The design-lint grades FORM,
        # which lives in .tsx/.css (the styled markup) — a .ts logic file, an image, etc. carry NO
        # lintable form (NO-FORM rule). So:
        #   • a .tsx/.css that EXISTS → a lint target.
        #   • a .tsx/.css the change names but that is NOT on disk → genuine can't-run → FAIL-SAFE (a
        #     surface file that should exist but doesn't is unverifiable, never a silent pass).
        #   • a non-.tsx/.css canvas file (.ts logic, asset) → no form to grade → skipped (not a target,
        #     not a fail-safe miss) — so a pure-logic FE build can still auto-close, and a .tsx+.ts change
        #     agrees with a .ts-alone change (the .ts never flips the verdict).
        # If the change has NO lintable .tsx/.css at all (pure-logic surface) → no form to grade → PASS.
        import subprocess, sys as _sys
        targets, missing_form_files = [], []
        for p in surface:
            q = (p or "").strip().lstrip("./")
            full = os.path.join(self._repo_root, q)
            if q.endswith((".tsx", ".css")):
                if os.path.exists(full):
                    targets.append(full)
                else:
                    missing_form_files.append(q)        # a styled file that should exist but doesn't
            # else: a non-form canvas file (.ts / asset) — NO-FORM, skipped (neither target nor miss).
        if missing_form_files:
            return (False, f"FORM unverifiable (fail-safe): surface change names .tsx/.css file(s) "
                           f"{missing_form_files} not present under {self._repo_root} — cannot lint a "
                           f"styled file that should exist. Surfaced for design review.")
        if not targets:
            # the changed surface carried NO lintable .tsx/.css (a pure-logic .ts / asset FE change) →
            # there is no form to machine-grade → it may proceed (the human design-critic agent, run
            # separately at verify time, still covers any judgment call).
            return (True, f"no lintable .tsx/.css in the changed surface {surface} (pure-logic / asset "
                          f"FE change) → no machine FORM to grade; the human design-critic agent covers "
                          f"any judgment at verify time.")

        py = _sys.executable
        offenders = []
        for full in targets:
            try:
                proc = subprocess.run([py, script, "--target", full, "--fail-on"],
                                      capture_output=True, text=True, timeout=120)
            except Exception as e:
                # FAIL-SAFE: the lint could not run (interpreter/script crash, timeout) → not-passed.
                return (False, f"FORM unverifiable (fail-safe): the corpus design-lint failed to run on "
                               f"{full} ({type(e).__name__}: {e}) — cannot confirm FORM. Surfaced for review.")
            if proc.returncode != 0:
                tail = (proc.stdout or "")[-300:] + (proc.stderr or "")[-300:]
                offenders.append(f"{os.path.relpath(full, self._repo_root)} (exit={proc.returncode}: {tail.strip()})")
        if offenders:
            return (False, f"FORM gate FAILED (design-lint): off-token/bespoke finding(s) in the changed "
                           f"surface — {'; '.join(offenders)}. The surface must use corpus tokens "
                           f"(var(--x)) + components (AGENTS.md rule 9), so it CANNOT auto-close.")
        return (True, f"FORM gate PASSED (design-lint clean on changed surface: "
                      f"{', '.join(os.path.relpath(t, self._repo_root) for t in targets)}) — "
                      f"token-only; the in-repo machine half is satisfied (the human design-critic agent "
                      f"runs separately at verify time).")

    def _critic_recheck(self, decision: dict, result: dict, *, critic=None) -> tuple[bool, str]:
        """H5 — an ADVERSARIAL re-check, SEPARATE from the builder's self-report (the builder defaults
        to function + grades itself generously — exactly why correctness gets its own adversary). A
        first-class part of the verify, not optional. The DEFAULT critic is deterministic + structural
        (no confidence value): a consequential build must actually have changed something and reported
        success; a launch that claims success with an empty change-set is a no-op masquerading as done.
        INJECTABLE so a stronger critic (or a test) can supply its own verdict."""
        run = critic or self._default_critic
        return run(decision, result)

    @staticmethod
    def _default_critic(decision: dict, result: dict) -> tuple[bool, str]:
        """The default adversarial critic (deterministic): re-derive the verdict from the result rather
        than trust the builder's narration. A 'success' with no change-set is not an implementation; a
        reported failure is a failure regardless of narration."""
        if not result.get("success"):
            return False, f"critic: builder reported failure (exit={result.get('exit_code')})"
        if not result.get("changed_files"):
            return False, "critic: success claimed with an EMPTY change-set — a no-op is not a build"
        return True, "critic: build is consequential (success + non-empty change-set)"

    def _wire_verify(self, decision: dict, result: dict, scope: list[str], *,
                     suite_runner=None, critic=None) -> tuple[bool, str]:
        """The wire's DEFINITION-OF-DONE — the loop's discipline, as ONE fail-loud gate (H1·H2b·H4·H5).
        Order matters (the reverse-incident fix): the build is ALREADY made LIVE + the factual
        self-description ALREADY refreshed (H3/H2a, hoisted to run unconditionally in dispatch_decision
        BEFORE any verifier — so a loop's injected scenario verifier can't lose the refresh). This gate
        then runs the affected suites + drift (H1/H2b) against the now-current state, the adversarial
        critic (H5), and the FORM gate (H4). ANY miss → (False, reason) → the caller surfaces back,
        never closes (H6). All steps injectable for deterministic tests. Returns (passed, reason)."""
        changed = result.get("changed_files", [])
        # NOTE: H3 + H2a (make-it-live + refresh-self-description) is hoisted OUT of here to run
        # UNCONDITIONALLY in dispatch_decision BEFORE the verifier branch — so even a loop that injects
        # its own scenario `verifier` (which bypasses this heavy default) cannot silently lose the
        # refresh (the exact reverse-incident class this lane kills). By the time _wire_verify runs, the
        # registry is already live + the self-description already refreshed. We re-assert it here ONLY
        # as a defensive no-op is unnecessary (it already ran); we go straight to the gates below.
        # H1 + H2b — the affected acceptance suites + drift must be GREEN (this is where the reverse
        # incident would now be CAUGHT: drift_acceptance is always in the affected set and runs AFTER
        # the refresh, so a build that didn't leave drift green does not close).
        suites = self._affected_suites(changed, scope)
        ok, why = self._run_suites(suites, runner=suite_runner)
        if not ok:
            return False, why
        # H5 — the adversarial critic, separate from the builder's self-report.
        ok, why = self._critic_recheck(decision, result, critic=critic)
        if not ok:
            return False, why
        # NOTE: H4 (the FORM gate — a surface-touching build cannot auto-close) is NOT here. It is a
        # STRUCTURAL gate, like the refresh + the scope-diff, so it runs UNCONDITIONALLY in
        # dispatch_decision — NOT only on this default path. Otherwise a loop that injects its own
        # scenario `verifier` (which bypasses this heavy default) could close a surface build with an
        # unverifiable FORM. The partition: structural gates (refresh · FORM · scope-diff) =
        # unconditional; verification-QUALITY (the affected suites + the critic) = replaceable by an
        # injected verifier. So _wire_verify proves only suites + critic.
        return True, ("wire verify PASSED: live+refreshed · affected suites + drift green · critic ok — "
                      + why)

    def dispatch_decision(self, sid: str, derived_from: int, *, launcher=None,
                          verifier=None, suite_runner=None, critic=None, repo: str | None = None,
                          committer=None) -> dict:
        """W2·W4·W1·W3·W5 — the governed dispatch verb. Run an implementation job ONLY when bound to
        a real operator approve via `derived_from` = the resolve event's unique `seq`, and ONLY once.

        Sequence (CHECK → CLAIM → GATE → LAUNCH → VERIFY → CLOSE-or-SURFACE):
          1. verify the three-part bind (kind=resolve·surfaced==sid·choice=approve) — else GovernanceError.
          2. require it IS a build-intent item (the discriminator) — else refuse.
          3. EXACTLY-ONCE: refuse if a `decision.dispatch` already exists for this `seq` (fail loud).
          4. W4 PRE-DISPATCH gate on the DECLARED consequence class, keyed on POLICY POSTURE: ONLY an
             AUTO-posture class auto-dispatches. CONFIRM/SURFACE/LOCKED all surface for the operator
             BEFORE building (refuse to auto-run a non-AUTO build). AUTO means auto-DISPATCH on the
             operator's approve (no second gate before building) — it does NOT mean auto-CLOSE without
             review. decision_build is the AUTO class; CONFIRM/SURFACE/LOCKED classes surface here.
          5. emit `decision.dispatch` (the durable exactly-once claim) BEFORE launching — so a crash
             after launch refuses re-launch on restart.
          6. launch (W1, runtime/implement.launch — injectable for tests).
          7. verify by USE (W3, injectable). On FAIL → surface_review directly with the reason; the
             item does NOT close (no `implemented`). Do NOT reuse requeue_from_verdict (it needs
             choice!=approve; a build follows an approve).
          8. W4 scope-diff: changed paths outside the declared scope → surface back, do NOT close.
          8b. GIT CHECKPOINT (Tim's safety mandate): commit EXACTLY the build's changed_delta paths as a
             single `[self-build] <sid>: <intent>` commit so the accepted build is REVERTIBLE
             (`git revert <sha>`, the same operator path as a self-apply). Path-scoped, so the
             concurrent writer's unstaged dirty files are NEVER swept in. FAIL LOUD: a commit failure
             (or an empty delta at this point) surfaces the build BACK as a retryable build-intent —
             it does NOT mark implemented (a build that can't be checkpointed is not safe-closed). The
             resulting sha is threaded into the close (the `decision.implemented` event + the review
             item) so the operator/a revert path can `git revert <sha>`.
          9. CLOSE + SURFACE-FOR-REVIEW (guarded): write status='implemented' AND surface a review item
             through guard("code_build",…, confirmed=verify_passed) — an unverified close RAISES
             (mirrors apply_node). `implemented` means "done AND surfaced for review", NEVER a silent
             terminal — AI-operated is NOT review-free. The review (a distinct `build_result_review`
             item, inert to the dispatcher) reuses the existing surface_review inbox + a
             `decision.surfaced_for_review` event; it is part of THIS single dispatch, not a second one.
             Code NEVER writes `resolved` (operator-only) — it writes the `status` lane + surfaces.
        """
        from runtime import implement as _impl
        repo = repo or self._repo_root
        d = self.inbox.get(sid)
        if not d:
            raise KeyError(f"no surfaced decision {sid!r}")

        # 1 + 2 — the bind, then the discriminator (a forged/mismatched/non-build item refuses).
        self._verify_resolve_bind(sid, derived_from, require_approve=True)
        if not self.is_build_intent(d):
            raise GovernanceError(
                f"dispatch_decision: {sid!r} is not a build-intent item (payload.intent != 'build') — "
                f"refusing to auto-build from a non-build approve (the discriminator §W2). Mint it via "
                f"surface_build_intent.")

        payload = d.get("payload") or {}
        declared = payload.get("consequence_class", "decision_build")
        scope = list(payload.get("scope") or [])

        # 4 — W4 PRE-DISPATCH gate on the DECLARED class (deterministic, no confidence, no LOCKED-set
        # special-case). ONLY an AUTO-posture declared class may auto-dispatch; CONFIRM/SURFACE/LOCKED
        # all surface for the operator (do NOT auto-run). This keys on POLICY posture, so a CONFIRM
        # class absent from the hardcoded LOCKED set (e.g. 'destructive') can no longer slip through.
        # (decision_build is SURFACE → surfaces by default = the safe default; an AUTO-classed build is
        # the only thing that auto-runs.)
        if posture(declared) != AUTO:
            raise GovernanceError(
                f"dispatch_decision: declared consequence class {declared!r} has posture "
                f"{posture(declared)!r} (not AUTO) — it does NOT auto-dispatch; it surfaces for the "
                f"operator (CONFIRM/SURFACE/LOCKED never auto-run; surfacing a result after the act is "
                f"too late). The operator launches a non-AUTO build; refused.")

        # 3 + 5 — EXACTLY-ONCE check→claim, ATOMIC under TWO nested locks. The bridge is a
        # ThreadingHTTPServer over one Suite; without a lock two concurrent fires both clear the check
        # before either claims → double-launch. The thread lock (_dispatch_lock) serializes in-PROCESS
        # threads; nested INSIDE it the store's cross-PROCESS graph_lock (keyed dispatch-claim:<seq>,
        # backed by fcntl.flock — the primitive the store lane built) serializes across SEPARATE
        # PROCESSES too (Tim runs multiple sessions). So the check→emit critical section is atomic
        # whether the race is two threads or two processes; the durable decision.dispatch event remains
        # the restart guarantee. Re-entrant, so a nested locked call on the same key won't self-deadlock.
        with self._dispatch_lock(derived_from), self.store.graph_lock(f"dispatch-claim:{derived_from}"):
            if self._already_dispatched(derived_from):
                raise GovernanceError(
                    f"dispatch_decision: a decision.dispatch already exists for resolve seq={derived_from} — "
                    f"this build already launched; refusing a second (exactly-once, fail loud).")
            # emit the durable exactly-once claim BEFORE launch (and inside the lock). T1-EMIT: this is
            # the SAFETY-CRITICAL claim the exactly-once guarantee rides on — it MUST fail loud. Routed
            # through _emit_durable (raises on an append failure) NOT _emit (which swallows). A swallowed
            # claim-write would let _already_dispatched return False on a retry → DOUBLE-LAUNCH of a real
            # `claude -p`. Because this raises BEFORE launch (below) + inside the lock, a failed claim
            # means NOTHING launches — the safe outcome — and the caller (drive_dispatchable) sees the
            # raise rather than a phantom success.
            self._emit_durable("decision.dispatch",
                               f"dispatching build for {sid} (class={declared}, scope={scope or '∅'}, "
                               f"derived from verdict seq={derived_from})",
                               surfaced=sid, derived_from=derived_from,
                               consequence_class=declared, scope=scope,
                               address="ui://chrome/inbox")   # S2: the dispatched build-intent's inbox item
                                                              # (additive meta; durable fail-loud posture unchanged)
            self.inbox.set_status(sid, "presented")

        # 6 — launch (W1). Loud on a bad round-trip (LaunchError) — caller (W7/loop) re-queues loud.
        launch = launcher or _impl.launch
        try:
            result = launch(d, repo=repo)
        except _impl.LaunchError as e:
            # loud re-queue as a responsive review item — never a silent no-op (W7).
            req = dict(payload); req.update({"requeued_from": sid, "why": f"dispatch failed: {e}",
                                             "derived_from": derived_from, "intent": "build"})
            new_sid = self.inbox.surface_review(req, origin="responsive")
            self._emit("decision.verify",
                       f"dispatch for {sid} FAILED to launch → re-queued {new_sid} — {e}",
                       surfaced=new_sid, requeued_from=sid, derived_from=derived_from, verify_passed=False,
                       address="ui://chrome/inbox")   # S2: re-queued build-intent inbox item
            return {"surfaced": sid, "dispatched": True, "launched": False, "verified": False,
                    "requeued": new_sid, "error": str(e)}

        # store the result summary on the item (W5) — visible after the fact. T1-RACE: re-read under the
        # surfaced lock and mutate the FRESH copy, so a concurrent set_status (presented→…) write can't
        # lose-update the build_result (or vice-versa). The lock is the store-level one both writers reach.
        with self.store.surfaced_lock():
            d = self.inbox.get(sid) or d
            d["build_result"] = {"success": result.get("success"), "summary": result.get("summary", "")[:2000],
                                 "changed_files": result.get("changed_files", []),
                                 "permission_mode": result.get("permission_mode")}
            self.store.save_surfaced(d)

        # 6b — WIRE-HARDEN H3 + H2a, UNCONDITIONAL (the reverse-incident fix): re-discover into the LIVE
        # system (a new node-type becomes live in self.registry, not just on disk) + regenerate the
        # factual self-description blocks (MAP/STATE) FROM the now-current registry — BEFORE any verify,
        # so the drift check reads the refreshed truth. Run here (not only inside _wire_verify) so even a
        # loop that injects its OWN scenario `verifier` (which bypasses the heavy default) can NEVER
        # silently lose the refresh — the exact class of bug (a node built but the self-description not
        # refreshed → drift red) this lane exists to kill. Spawns NOTHING (no fork-bomb risk) and is
        # idempotent on an unchanged registry (_write_doc_block no-ops when content matches). A broken
        # node makes rediscover raise → returned here as a MISS reason → surfaces back (a build that
        # breaks the registry is not done), never a silent close (H6).
        live_ok, live_reason = self._make_live_and_refresh()

        # 7 — VERIFY by use (W3 + WIRE-HARDEN H1·H2b·H5 — verification QUALITY). The wire's
        # definition-of-done is now the HUMAN BUILD LOOP's discipline: run the affected acceptance suites
        # + drift (against the now-refreshed state) + an adversarial critic. This is the DEFAULT verify.
        # An INJECTED `verifier` is the fast deterministic bypass the loop/tests use (a specific scenario
        # check) — it runs INSTEAD of the heavy default so existing suites stay fast + green, exactly as
        # before WIRE-HARDEN. Either way a miss surfaces back, never a silent close (H6). (The STRUCTURAL
        # gates — refresh, FORM, scope-diff — are UNCONDITIONAL, below + above; they are NOT replaceable
        # by an injected verifier, so a loop's scenario verifier can never close a surface build.)
        if not live_ok:
            verify_passed, verify_reason = False, live_reason     # broken-registry build → surface back
        elif verifier is not None:
            verify_passed, verify_reason = verifier(result)
        else:
            verify_passed, verify_reason = self._wire_verify(
                d, result, scope, suite_runner=suite_runner, critic=critic)

        if not verify_passed:
            # H6 — a verification miss (test fail / drift red / critic veto / broken registry / launch)
            # surfaces back as a RETRY-able build-intent (the operator may re-approve after a fix). Call
            # surface_review DIRECTLY (NOT requeue_from_verdict; a build follows an approve, no reject seq).
            fail_item = dict(payload)
            fail_item.update({"requeued_from": sid, "why": f"verification failed: {verify_reason}",
                              "derived_from": derived_from, "intent": "build",
                              "build_result": d.get("build_result")})
            new_sid = self.inbox.surface_review(fail_item, origin="responsive")
            self._emit("decision.verify",
                       f"build for {sid} did NOT verify ({verify_reason}) → re-queued {new_sid}; not closed",
                       surfaced=new_sid, requeued_from=sid, derived_from=derived_from,
                       verify_passed=False,
                       address="ui://chrome/inbox")   # S2: re-queued build-intent inbox item
            return {"surfaced": sid, "dispatched": True, "launched": True, "verified": False,
                    "requeued": new_sid, "reason": verify_reason}

        # 7b — H4/F9 FORM GATE (UNCONDITIONAL — a structural gate, like the scope-diff, NOT inside the
        # replaceable verifier). A build that touched an operator-facing surface (canvas/) is run through
        # the LIVE machine FORM gate (_design_critic, graduated by F9): the corpus design-lint
        # (design/_system/check.py --fail-on) over the CHANGED surface files. A clean token-only surface
        # PASSES → the UI self-build AUTO-CLOSES (approval already happened at the build-intent guard; F9
        # adds no second manual gate). An off-token/bespoke change, or an unrunnable lint (fail-safe),
        # FAILS → it surfaces for review REGARDLESS of how verify_passed was reached (incl. an injected
        # scenario verifier — the WIRE-LOOP path; the gate runs unconditionally here, NOT in the
        # bypassable verifier). The surfaced item is DELIBERATELY DISPATCHER-INERT (a `build_form_review`,
        # NOT a build-intent): re-approving it must NOT re-dispatch into a can't-verify-form loop (it
        # would satisfy _is_dispatchable under a NEW seq, and exactly-once is keyed on the OLD seq).
        # _design_critic is the in-repo MACHINE half; the human-judgment design-critic AGENT (browser +
        # screenshots) is dispatched SEPARATELY by the loop at verify time (it can't run headless here).
        form_ok, form_reason = self._design_critic(result.get("changed_files", []))
        if not form_ok:
            form_item = {"kind": "build_form_review", "review_of": sid, "derived_from": derived_from,
                         "why": f"not auto-closed: {form_reason}", "scope": scope,
                         "consequence_class": declared, "build_result": d.get("build_result"),
                         "changed_files": result.get("changed_files", [])}
            new_sid = self.inbox.surface_review(form_item, origin="responsive")
            self._emit("decision.verify",
                       f"build for {sid} touched an operator-facing surface → cannot auto-close (FORM "
                       f"unverifiable) → surfaced {new_sid} for design review; not closed",
                       surfaced=new_sid, review_of=sid, derived_from=derived_from, verify_passed=False,
                       address="ui://chrome/inbox")   # S2: surfaced design-review inbox item
            return {"surfaced": sid, "dispatched": True, "launched": True, "verified": True,
                    "closed": False, "requeued": new_sid, "reason": form_reason,
                    "form_unverifiable": True}

        # 8 — W4 SCOPE-DIFF (fail loud): changed paths outside the declared scope → surface back, no
        # close. Runs ALWAYS (no `if scope:` skip) — _within_scope treats an empty scope as DENY-ALL,
        # so a build with no/empty declared scope can NEVER close (vacuous-enforcement hole closed).
        # H8 — the self-description files (AGENTS.md / MAP.md / STATE.md) are ALWAYS allowed: H7 INSTRUCTS
        # the build to update them as part of the change, and the close itself regenerates the factual
        # blocks (the system's write, not the build's). So they are upkeep, NOT out-of-scope wandering —
        # the overrun check must not flag them, or every well-behaved build would surface as a false
        # overrun. (The regen's writes aren't in `changed_files` anyway — that was snapshotted inside
        # launch() before the close ran — but the BUILD's own H7 prose edits to these files ARE, and
        # those are legitimate.) The declared scope still binds every OTHER path.
        changed = result.get("changed_files", [])
        if True:
            overrun = [p for p in changed
                       if not self._is_self_description(p) and not self._in_any_scope(p, scope)]
            if overrun:
                over_item = dict(payload)
                over_item.update({"requeued_from": sid, "intent": "build", "derived_from": derived_from,
                                  "why": f"scope overrun: changed {overrun} outside declared scope {scope}",
                                  "overrun": overrun, "build_result": d.get("build_result")})
                new_sid = self.inbox.surface_review(over_item, origin="responsive")
                self._emit("decision.verify",
                           f"build for {sid} OVERRAN declared scope ({overrun}) → re-queued {new_sid}; not closed",
                           surfaced=new_sid, requeued_from=sid, derived_from=derived_from,
                           verify_passed=False, overrun=overrun,
                           address="ui://chrome/inbox")   # S2: re-queued build-intent inbox item
                return {"surfaced": sid, "dispatched": True, "launched": True, "verified": True,
                        "closed": False, "requeued": new_sid, "overrun": overrun}

        # 8b — GIT CHECKPOINT (Tim's safety mandate before arming the wire): commit EXACTLY the build's
        # changed_delta paths as a SINGLE revertible commit, BEFORE the close marks it implemented. This
        # turns each accepted autonomous build into a `git revert <sha>` away from undone — the property
        # that makes arming the wire acceptable. It runs ONLY here, on the verified + in-scope + FORM-ok
        # success branch (every earlier gate already surfaced its own failures back), so a
        # failed/denied/out-of-scope/plan-mode build NEVER reaches a commit.
        #
        # PROPERTIES, each load-bearing:
        #  • PATH-SCOPED: we commit `changed` (= the build's changed_delta — git ground truth, isolated
        #    by launch()'s baseline_snapshot from any pre-existing dirty files). `_self_build_commit` →
        #    `_git_self_commit` does `git add <changed>` (named paths only), so the concurrent writer's
        #    UNSTAGED dirty files (design/blueprint/*.json) are NEVER swept in.
        #  • EMPTY-DELTA GUARD: a verified build with an EMPTY change-set is a no-op (the default critic
        #    already vetoes it; a plan-mode run yields an empty delta and fails verify upstream). If we
        #    still arrive here with nothing to commit (only reachable via an injected verifier that
        #    passes on empty), we DO NOT create an empty commit — we surface back, fail loud.
        #  • FAIL LOUD: a commit failure (sha is None) surfaces the build BACK as a RETRYABLE build-intent
        #    (the same shape as the verify/scope-overrun re-queues, a `decision.verify`/verify_passed=False
        #    terminal event so the watcher does NOT read it as a crashed mid-flight dispatch) and returns
        #    closed=False. It must NOT mark `implemented` — a build that can't be checkpointed is NOT
        #    safe-closed (Tim's mandate). The sha is threaded into the close so the close can record it.
        #  • INJECTABLE: `committer(paths, msg) -> sha|None` defaults to the real `_self_build_commit`;
        #    a test injects a stub so no real commit hits the live repo and the exact staged paths can be
        #    asserted. (NOT `_commit_or_rollback` — that os.remove()s its path on failure, which would
        #    DELETE the build's own work across a multi-file delta.)
        commit = committer or self._self_build_commit
        if not changed:
            # a verified, in-scope build that changed NOTHING — no-op masquerading as done. Surface back
            # (do not create an empty checkpoint commit). (Unreachable on the default path: the critic
            # vetoes an empty change-set; reachable only via an injected verifier that passes on empty.)
            empty_item = dict(payload)
            empty_item.update({"requeued_from": sid, "intent": "build", "derived_from": derived_from,
                               "why": "git checkpoint: nothing to commit (empty change-set) — a build with "
                                      "no changed files cannot be checkpointed/closed (no-op is not a build)",
                               "build_result": d.get("build_result")})
            new_sid = self.inbox.surface_review(empty_item, origin="responsive")
            self._emit("decision.verify",
                       f"build for {sid} had an EMPTY change-set at checkpoint → re-queued {new_sid}; not closed",
                       surfaced=new_sid, requeued_from=sid, derived_from=derived_from, verify_passed=False,
                       address="ui://chrome/inbox")
            return {"surfaced": sid, "dispatched": True, "launched": True, "verified": True,
                    "closed": False, "requeued": new_sid, "reason": "empty change-set at checkpoint"}
        intent_summary = (payload.get("spec") or payload.get("instruction") or payload.get("why") or "").strip()
        intent_summary = " ".join(intent_summary.split())[:120] or "(no intent summary)"
        commit_msg = f"{sid}: {intent_summary}"
        commit_sha = commit(changed, commit_msg)
        if not commit_sha:
            # FAIL LOUD: the checkpoint did not commit → the build is NOT git-revertible → it is NOT
            # safe-closed. Surface back as a retryable build-intent (the operator may re-approve after the
            # tree is sorted); emit a recognized terminal kind (decision.verify) so resurface_crashed does
            # NOT later read this dispatch as crashed-mid-flight and double-surface it.
            fail_item = dict(payload)
            fail_item.update({"requeued_from": sid, "intent": "build", "derived_from": derived_from,
                              "why": (f"git checkpoint FAILED: could not commit the build's changed files "
                                      f"{changed} — the build is NOT git-revertible, so it is NOT safe to "
                                      f"close (Tim's safety mandate). Re-surfaced for the operator."),
                              "checkpoint_failed": True, "build_result": d.get("build_result")})
            new_sid = self.inbox.surface_review(fail_item, origin="responsive")
            self._emit("decision.verify",
                       f"build for {sid} could NOT be git-checkpointed (commit failed) → re-queued "
                       f"{new_sid}; not closed (a build that can't be checkpointed is not safe-closed)",
                       surfaced=new_sid, requeued_from=sid, derived_from=derived_from, verify_passed=False,
                       checkpoint_failed=True,
                       address="ui://chrome/inbox")
            return {"surfaced": sid, "dispatched": True, "launched": True, "verified": True,
                    "closed": False, "requeued": new_sid, "reason": "git checkpoint failed",
                    "checkpoint_failed": True}

        # 9 — CLOSE + SURFACE-FOR-REVIEW (the conceptual correction). guarded on the verification
        # verdict (W4 Hole 4). guard("code_build", …, confirmed=verify_passed): code_build is
        # CONFIRM-posture, so an unverified close (confirmed False) RAISES instead of silently writing
        # `implemented` (mirrors apply_node). inbox=None so the blocked path just raises (it must NOT
        # re-surface). Code writes ONLY the `status` lane — never the operator `resolved` field.
        #
        # AI-operated is NOT review-free: `implemented` means "done AND surfaced for review", NEVER a
        # silent terminal. So the SAME guarded close ALSO surfaces a review item (via the existing
        # `surface_review` inbox + a `decision.surfaced_for_review` event) carrying the result summary,
        # the changed-files manifest (git ground truth = the diff), and `derived_from` — so the operator
        # SEES it in the RHM walkthrough. This is part of the ONE dispatch (the decision.dispatch claim
        # already made it exactly-once); surfacing the review is NOT a second dispatch.
        #
        # The review item is DELIBERATELY NOT a build-intent (no `intent="build"`). The failure/overrun
        # re-queue paths above keep `intent="build"` on purpose — they are RETRIES the operator may
        # re-approve. A SUCCESS review must not be re-approvable into a REBUILD: if it carried
        # intent="build"+decision_build(AUTO), the operator's "looks good" approve would satisfy
        # drive_dispatchable._is_dispatchable (approve + build-intent + posture==AUTO) under a NEW seq,
        # and exactly-once (keyed on the OLD seq) would not stop it. So the review payload is a distinct
        # `build_result_review` kind — inert to the dispatcher.
        review_holder = {}
        def _close():
            self.inbox.set_status(sid, "implemented")
            # record the checkpoint sha on the item so the operator (or a revert path) can find it
            # without re-deriving it from the log. T1-RACE: re-read + mutate under the surfaced lock.
            with self.store.surfaced_lock():
                _it = self.inbox.get(sid) or d
                _it["commit"] = commit_sha
                self.store.save_surfaced(_it)
            self._emit("decision.implemented",
                       f"build for {sid} verified + within scope → checkpointed [self-build] "
                       f"{commit_sha[:8]} → status=implemented "
                       f"(changed {len(changed)} files; derived from seq={derived_from})",
                       surfaced=sid, derived_from=derived_from, verify_passed=True, changed_files=changed,
                       commit=commit_sha,                 # the revertible checkpoint sha (`git revert <sha>`)
                       address="ui://chrome/inbox")   # S2: the implemented build-intent's inbox item
            # surface the result for the MANDATORY review (reversible/AUTO builds are non-blocking —
            # the change is made + git-reversible — but the review is ALWAYS surfaced). Reuses the
            # existing surface_review inbox + event log; no parallel review system. surface_review
            # emits "ask" too, so the live SSE inbox-refresh lights up for the operator.
            br = d.get("build_result") or {}
            review_payload = {
                "kind": "build_result_review",          # NOT a build-intent → inert to the dispatcher
                "title": f"Review implemented build: {sid}",
                "review_of": sid,
                "derived_from": derived_from,
                "summary": br.get("summary", ""),
                "changed_files": changed,                # git ground truth = the diff manifest
                "commit": commit_sha,                    # the revertible checkpoint sha (`git revert <sha>`)
                "consequence_class": declared,
                "scope": scope,
                "why": (f"a build for {sid} was implemented (verified + in scope) and is surfaced for "
                        f"MANDATORY review — AI-operated is NOT review-free. The change was checkpointed "
                        f"as [self-build] commit {commit_sha[:8]} and is git-reversible "
                        f"(`git revert {commit_sha}`); review it in the RHM walkthrough."),
            }
            rev = self.surface_review(review_payload, origin="responsive")
            review_holder["id"] = rev["id"]
            self._emit("decision.surfaced_for_review",
                       f"build for {sid} surfaced for review → {rev['id']} "
                       f"(changed {len(changed)} files; review is mandatory, not silent close)",
                       surfaced=rev["id"], review_of=sid, derived_from=derived_from,
                       changed_files=changed,
                       address="ui://chrome/inbox")   # S2: the surfaced-for-review inbox item
            return True
        guard("code_build", do=_close, confirmed=verify_passed, inbox=None)
        return {"surfaced": sid, "dispatched": True, "launched": True, "verified": True,
                "closed": True, "status": "implemented", "changed_files": changed,
                "commit": commit_sha,                    # the revertible [self-build] checkpoint sha
                "derived_from": derived_from, "review_surfaced": review_holder.get("id")}

    @classmethod
    def _is_self_description(cls, path: str) -> bool:
        """H8 — is this changed path a ROOT self-description file (AGENTS.md / MAP.md / STATE.md)? H7
        instructs the build to update the self-description as part of the change, and the close itself
        regenerates the factual blocks — so a change to one of these is the SYSTEM's upkeep, never an
        out-of-scope edit. The overrun check (H8) treats it as in-scope without it being declared.
        Matched at the REPO ROOT only (normalized): a module's own AGENTS.md (e.g. 'nodes/AGENTS.md')
        is covered by that module's declared scope dir, not by this blanket allow."""
        import os as _os
        p = _os.path.normpath((path or "").strip().lstrip("./"))
        return p in cls._SELF_DESC_FILES

    @staticmethod
    def _in_any_scope(path: str, scope: list[str]) -> bool:
        """A changed path is authorized iff it falls under AT LEAST ONE declared scope entry. An
        EMPTY scope is DENY-ALL (returns False for every path) — never allow-all — so a build with
        no declared scope can never pass the overrun check (closes the vacuous-enforcement hole)."""
        return any(Suite._within_scope(path, s) for s in (scope or []))

    @staticmethod
    def _within_scope(path: str, scope_entry: str) -> bool:
        """A changed path is in scope if it equals or is under a declared scope entry (a file or a
        dir prefix). Both sides are NORMALIZED with os.path.normpath, which collapses '..' — so a
        traversal path like 'runtime/../nodes/evil.py' resolves to 'nodes/evil.py' and CANNOT match
        'runtime/' (the guard can't be fooled by '..'). An absolute path (e.g. '/etc/passwd') never
        matches a repo-relative scope entry. 'runtime/' still covers 'runtime/implement.py'."""
        import os as _os
        p = _os.path.normpath(path.strip().lstrip("./"))
        s = _os.path.normpath(scope_entry.strip().lstrip("./").rstrip("/"))
        if not s or s == ".":
            return False                                     # empty/degenerate scope entry → deny
        return p == s or p.startswith(s + _os.sep)

    # --- C1: the UI-component registry serialization (sibling of object_info) ---
    # Seeds the known chrome regions (DOM-resolved via data-ui-ref handles the UI lane adds) + the node
    # canvas (camera-resolved). ref = the <ref> in ui://<kind>/<ref>; dom_handle = the data-ui-ref value.
    # (ref, kind, title, dom_handle|camera_ref, caps-dict[, union-extras-dict]). caps keys are the
    # Capabilities fields.
    # S0 (Interactive Addressed Surface) — the ONE canonical grammar:
    #   The optional 6TH tuple element is the S0 union-extras dict (additive — defaults to {} via
    #   row[5:] slicing in every consumer), carrying the union-record join fields (represents/code/
    #   tier/states) for entries where a 1:1 corpus join is known. The 7 live entries leave it ABSENT
    #   (rule 8 — joining from the corpus is optional, not S0's bar; S1 grows the element-level set).
    #   Both this live registry AND design/_system/addresses.json validate against the ONE canonical
    #   `ui://<region>/<element>[/<sub>][/@state]` grammar via contracts.ui_info.conform_live /
    #   conform_corpus (proven by tests/address_grammar_acceptance.py). The grammar is purely
    #   STRUCTURAL; kind/region are RECORD fields — so the live kind-form `ui://chrome/inbox` and the
    #   corpus region-form `ui://inbox/build-review` both conform WITHOUT migrating the live strings
    #   (that migration is S1, not S0).
    UI_REGISTRY = [
        ("toolbar",   "chrome", "Toolbar",      {"dom_handle": "toolbar"},
         {"pointable": True, "spotlit": True}),
        ("inspector", "chrome", "Inspector",    {"dom_handle": "inspector"},
         {"pointable": True, "spotlit": True, "openable": True}),
        ("inbox",     "chrome", "Inbox",        {"dom_handle": "inbox"},
         {"pointable": True, "spotlit": True, "openable": True}),
        ("activity",  "chrome", "Activity log", {"dom_handle": "activity"},
         {"pointable": True, "spotlit": True, "openable": True, "drivenReadOnly": True}),
        ("chat",      "chrome", "RHM chat",     {"dom_handle": "chat"},
         {"pointable": True, "spotlit": True, "openable": True}),
        ("workshop",  "chrome", "Workshop",     {"dom_handle": "workshop"},
         {"pointable": True, "spotlit": True, "openable": True}),
        # S1: the two app-carried bare handles that had a DOM data-ui-ref but were NOT served (fe-map §8
        # internal inconsistency — the FE pointed at them, the registry didn't know them). Registering them
        # as bare-key chrome regions (the same shape as the 6 above) closes the orphan: every app
        # data-ui-ref now has a registry entry. walkthrough = the per-step review card region
        # (regions/Walkthrough.tsx); deferred-queue = the inbox deferred lane (regions/Inbox.tsx).
        ("walkthrough",    "chrome", "Walkthrough",    {"dom_handle": "walkthrough"},
         {"pointable": True, "spotlit": True, "presentable": True}),
        ("deferred-queue", "chrome", "Deferred queue", {"dom_handle": "deferred-queue"},
         {"pointable": True, "spotlit": True, "openable": True}),
        # the node canvas itself (camera_ref="*" = the whole canvas; individual nodes are addressed live
        # as ui://canvas/<node-id> by show's canvas branch — reuse of the existing camera path).
        ("*", "canvas", "Node canvas", {"camera_ref": "*"},
         {"pointable": True, "spotlit": True, "presentable": True}),
    ]
    # S1: GROW the registry to the 24+ ELEMENT-level addresses from the design corpus (additive — the 7
    # bare-ref region rows above are UNCHANGED, so every existing consumer keeps resolving). The element
    # rows are keyed by their FULL canonical string (ui://inbox/build-review), read from the corpus (never
    # invented — rule 8). See _load_corpus_element_addresses for the projection + the preserve rationale.
    # Built at class-definition time so /api/ui_info serves them with no per-call cost; fail-loud if the
    # corpus file is missing/malformed (the registry never silently ships region-only).
    UI_REGISTRY = UI_REGISTRY + _load_corpus_element_addresses()

    def build_ui_info(self) -> dict:
        """C1: serialize the UI-component registry for the frontend (a SIBLING of object_info — which is
        NodeType-hardwired, so this is its own build, not a reuse). Built against
        contracts.ui_info.UiComponentEntry/Capabilities + build_ui_info (the CONTRACTS lane provides them).
        FUNCTION-LOCAL import so suite.py loads even before that contract lands; fails loud only when
        ui_info is actually called. The UI lane adds the matching data-ui-ref handles to the DOM."""
        from contracts.ui_info import UiComponentEntry, Capabilities, build_ui_info as _build
        entries = []
        for row in self.UI_REGISTRY:
            # S0-additive: a registry row is (ref, kind, title, handle, caps[, union-extras]). The
            # 6th element (union-extras for the canonical grammar) is IGNORED by this v1 /ui_info
            # serializer — it preserves the existing served shape (an older FE reads exactly what it
            # did before). Slice the first five so a 6-tuple row does not break the unpack.
            ref, kind, title, handle, caps = row[0], row[1], row[2], row[3], row[4]
            entries.append(UiComponentEntry(ref=ref, kind=kind, title=title,
                                            capabilities=Capabilities(**caps), **handle))
        return _build(entries)

    def ui_info(self) -> dict:
        return self.build_ui_info()

    # --- S3: the backend ui://→code://→scope[] resolver (Interactive Addressed Surface) ---
    # Establishes `code://` in the BACKEND (it was corpus-only). A resolver mapping a `ui://` address →
    # its `code://` symbol(s) → a file `scope[]`. This is the pivot L1 (comment→build-intent needs the
    # code scope) and L5 (self-change→element needs the file→ui join) both lean on. It READS the corpus
    # join data on disk (design/_system/{addresses.json, code-symbols.json}); FRESHNESS coupling: that
    # JSON is REGENERATED (by design/_system/symbols.py), not live — a stale code-symbols.json returns a
    # stale scope. Surfaced, never pretended-live (seams-engine risk #4).

    def _corpus_dir(self) -> str:
        """The corpus _system dir holding the join data (addresses.json, code-symbols.json)."""
        return os.path.join(self._repo_root, "design", "_system")

    def resolve_scope(self, ui_addr: str) -> dict:
        """S3 — map a `ui://` address → its `code://` symbol(s) → a file `scope[]`.

        ONE-SOURCE (rule 3): the code:// ids AND the scope files come FROM the corpus code-symbol
        registry (design/_system/code-symbols.json), NOT re-derived from the raw `addresses.json`
        `code` string. The registry is the canonical `code://` index — keyed by the SAME
        code://<file-stem>/<symbol> ids it mints (design/_system/symbols.py), carrying each symbol's
        RESOLVED repo-relative file (e.g. canvas/app/src/App.tsx, not the corpus's shorthand 'App.tsx')
        and a `referenced_by[]` listing the ui:// addresses that point at it. S3 INVERTS that
        `referenced_by` into the forward map ui://addr → [symbols] (the guide's `files_for` design),
        so a resolved id is a real registry key and a resolved path is the registry's resolved path —
        BY CONSTRUCTION, never a parallel/disagreeing `code://` scheme (the two-grammars failure S0
        exists to kill, kept out of code:// too).

        Returns {address, symbols:[code://…], scope:[file,…], stale, note}:
          • symbols — the code:// ids referencing this address (registry keys; canonical).
          • scope   — the DISTINCT, sorted RESOLVED files those symbols live in. EMPTY ⇒ DENY-ALL
                      downstream (matches surface_build_intent empty-scope=deny, suite.py — fail-safe,
                      NEVER allow-all; rule 8 — an unmapped address is never a license to build anywhere).
          • stale   — True if the corpus join data couldn't be read (regenerate it); fail-loud-legible.
          • note    — a human-legible explanation when scope is empty / the join is stale.

        The address MUST conform to the canonical grammar (S0) — a malformed ui:// raises (fail loud).
        An address with NO referencing symbol in the registry (a CSS-selector ref like ui://tabbar, an
        orphan, or one absent from the corpus) returns empty scope (DENY-ALL) WITHOUT raising — the gap
        is surfaced via `note`, never fabricated.

        FRESHNESS (seams-engine risk #4): code-symbols.json is REGENERATED by design/_system/symbols.py,
        not live — a stale index returns a stale scope. The resolver reads it as-is; it does not pretend
        the data is live. (A future rung could regenerate-then-read; for now the coupling is surfaced.)"""
        import json as _j
        from contracts.ui_info import parse_ui_address
        parse_ui_address(ui_addr)                            # S0 grammar gate (raises on malformed)

        symbols_path = os.path.join(self._corpus_dir(), "code-symbols.json")
        try:
            with open(symbols_path, encoding="utf-8") as f:
                index = _j.load(f).get("symbols", {})
        except (OSError, ValueError) as e:
            return {"address": ui_addr, "symbols": [], "scope": [], "stale": True,
                    "note": f"corpus code-symbols.json unreadable ({type(e).__name__}: {e}) — "
                            f"regenerate design/_system (symbols.py); DENY-ALL until then"}

        # INVERT referenced_by: collect every registry symbol that names this ui:// address.
        symbols, scope = set(), set()
        for sid, entry in index.items():
            if ui_addr in (entry.get("referenced_by") or []):
                symbols.add(sid)
                f = entry.get("file")
                if f:
                    scope.add(f)                             # the RESOLVED repo-relative path

        note = ""
        if not symbols:
            note = (f"{ui_addr!r} has no referencing code symbol in the corpus registry "
                    f"(a CSS-selector/prose ref, an orphan, or absent) — DENY-ALL "
                    f"(never fabricated — rule 8)")
        return {"address": ui_addr, "symbols": sorted(symbols), "scope": sorted(scope),
                "stale": False, "note": note}

    # --- X9 (Convergence, Seam 2): blast_radius — the nearly-FREE co-reference ripple ---
    # The corpus reverse index (design/_system/code-symbols.json) already encodes "which
    # addresses/features touch the same code symbol" in each symbol's `referenced_by[]` — but
    # NOTHING read it for this purpose (zero runtime consumers). X9 is the FREE half: invert that
    # ALREADY-LOADED index into the sibling set. NO new substrate, NO re-parsing source.
    #
    # --- X14 (Convergence, Seam 3): blast_radius spans BOTH edge kinds ---
    # X9 gives co-reference (what shares this code). X14 WIDENS the SAME method to ALSO return, all
    # DISTINGUISHED by kind: the TRUE STRUCTURAL dependents/dependencies (X10's code-edges.json —
    # `depended_by` = dependents-to-VERIFY, `depends_on` = dependencies-to-RESPECT, bounded by X10's
    # DEPTH-capped reach query) AND the SEMANTIC neighbours (X11's `semantically_nearest[]`). REUSE,
    # never reimplement: resolve_scope for addr→symbols (S0 gate + stale), codeedges.reach_report for
    # the bounded structural walk (the dependents side reuses the SAME walk over a transposed edge
    # view — no new BFS), and semantically_nearest[] read straight off the same code-symbols.json.
    # Graceful-empty + fail-loud-legible: a missing/absent layer → that kind empty + a note, NEVER a
    # crash, NEVER a fabricated edge (registry-truth, rule 4 + rule 8).

    def _structural_radius(self, symbols: list[str]) -> dict:
        """X14 structural layer — for the resolved `code://` symbols, the bounded structural
        dependents (X10 `depended_by`, dependents-to-VERIFY) + dependencies (X10 `depends_on`,
        dependencies-to-RESPECT) from design/_system/code-edges.json.

        REUSE, NOT reimplement (rule 3): the bounded transitive walk is X10's
        `codeedges.reach_report` (capped at its DEPTH knob; a reach that hits the bound is reported
        `capped`, no silent truncation). Dependencies = reach over `depends_on`. Dependents = the
        SAME reach over a TRANSPOSED edge view (depends_on↔depended_by swapped) — so the algorithm
        is X10's bounded BFS, not a new graph computation. Bounded by X10's DEPTH (do NOT unbound).

        Graceful (rule 4): code-edges.json absent/unreadable → empty dependents/dependencies + a
        legible `note` (regenerate it), never a crash, never a fabricated edge. Returns
        {dependents, dependencies, dependents_capped, dependencies_capped, depth, note}."""
        import json as _j
        empty = {"dependents": [], "dependencies": [], "dependents_capped": False,
                 "dependencies_capped": False, "depth": None}
        edges_path = os.path.join(self._corpus_dir(), "code-edges.json")
        try:
            with open(edges_path, encoding="utf-8") as f:
                edges = _j.load(f).get("edges", {})
        except (OSError, ValueError) as e:
            # fail-loud-legible: the structural graph isn't there → empty structural + a note.
            return {**empty, "note": (
                f"structural graph unavailable (design/_system/code-edges.json: "
                f"{type(e).__name__}: {e}) — regenerate it (design/_system/codeedges.py); "
                f"structural dependents/dependencies EMPTY until then (never fabricated — rule 8)")}

        # REUSE X10's bounded reach query (and its DEPTH cap) — import the SAME module, do not
        # reimplement the BFS. A transposed view (swap the two edge lists) lets the SAME forward
        # `reach_report` (which walks depends_on) compute the DEPENDENTS side. The module itself
        # lives at the REAL design/_system path (the engine code, not the join-DATA dir which a test
        # may shadow via _corpus_dir); code-edges.json above is read from _corpus_dir (the data).
        import importlib.util, sys as _sys
        ce_dir = os.path.join(self._repo_root, "design", "_system")
        ce_path = os.path.join(ce_dir, "codeedges.py")
        # codeedges.py does top-level `import refcheck`/`import symbols` (its sibling modules), so its
        # own dir must be importable. Add it for the exec (idempotent) — do NOT pollute permanently.
        added = ce_dir not in _sys.path
        if added:
            _sys.path.insert(0, ce_dir)
        try:
            spec = importlib.util.spec_from_file_location("_company_codeedges", ce_path)
            if spec is None or spec.loader is None:
                return {**empty, "note": (
                    f"structural reach module design/_system/codeedges.py unavailable — "
                    f"structural dependents/dependencies EMPTY (never fabricated — rule 8)")}
            ce = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ce)
        except Exception as e:  # noqa: BLE001 — a broken module must not crash the radius
            return {**empty, "note": (
                f"structural reach module design/_system/codeedges.py failed to load "
                f"({type(e).__name__}: {e}) — structural EMPTY (never fabricated — rule 8)")}
        finally:
            if added and ce_dir in _sys.path:
                _sys.path.remove(ce_dir)
        depth = ce.DEPTH                                    # X10's DEPTH cap (2–3) — the bound
        # transposed edges: depends_on ⇄ depended_by, so reach_report (forward over depends_on)
        # walks DEPENDENTS over the same bounded algorithm.
        transposed = {k: {"depends_on": v.get("depended_by", []),
                          "depended_by": v.get("depends_on", [])} for k, v in edges.items()}

        dependents, dependencies = set(), set()
        dep_capped = dee_capped = False
        for sid in symbols:
            deps = ce.reach_report(sid, edges, depth=depth)          # dependencies (depends_on)
            ddts = ce.reach_report(sid, transposed, depth=depth)     # dependents (depended_by)
            dependencies.update(deps["reached"]); dep_capped = dep_capped or deps["capped"]
            dependents.update(ddts["reached"]); dee_capped = dee_capped or ddts["capped"]
        # never report the queried symbols themselves as their own dependents/dependencies.
        sset = set(symbols)
        return {"dependents": sorted(dependents - sset),
                "dependencies": sorted(dependencies - sset),
                "dependents_capped": dee_capped, "dependencies_capped": dep_capped,
                "depth": depth, "note": ""}

    def _semantic_radius(self, symbols: list[str], index: dict) -> dict:
        """X14 semantic layer — the conceptually-related symbols from X11's `semantically_nearest[]`
        (read straight off the SAME already-loaded code-symbols.json index — no recompute, no
        embedder call here). Each entry's `semantically_nearest[]` is `[{id, score}, …]`.

        Graceful (rule 4): when the field is ABSENT on the entries (the embedder :8001 was down at
        regen — its CURRENT real state), semantic_neighbours is EMPTY + a legible note; never a
        crash, never a fabricated nearest. Returns {neighbours, note}."""
        neighbours: set[str] = set()
        any_field = False
        for sid in symbols:
            entry = index.get(sid) or {}
            near = entry.get("semantically_nearest")
            if near is None:
                continue                                    # field absent for this symbol
            any_field = True
            for item in near:
                nid = item.get("id") if isinstance(item, dict) else item
                if nid and nid not in symbols:              # exclude the queried symbols themselves
                    neighbours.add(nid)
        note = ""
        if not any_field:
            note = ("no semantically_nearest[] in the corpus index (X11) — the embedder (BGE-M3 "
                    "@ :8001) was down at the last regen, so the semantic edges were skipped "
                    "(degrade-with-warning); semantic_neighbours EMPTY until design/_system "
                    "(symbols.py) is regenerated with :8001 up (never fabricated — rule 8)")
        return {"neighbours": sorted(neighbours), "note": note}

    def blast_radius(self, ui_addr: str, shared_only: bool = False) -> dict:
        """X9+X14 — the BLAST RADIUS of a `ui://` address, spanning BOTH edge kinds, distinguished:
          • co_reference[]           — (X9) the OTHER addresses/features that share a `code://`
                                       symbol (what else touches this code). Also surfaced under the
                                       legacy `neighbours` key (X9 preserved byte-for-byte).
          • structural_dependents[]  — (X10) the symbols that DEPEND ON the resolved symbol(s) =
                                       dependents-to-VERIFY (what would break). Bounded by X10's reach.
          • structural_dependencies[]— (X10) the symbols the resolved symbol(s) DEPEND ON =
                                       dependencies-to-RESPECT (what it relies on). Bounded by reach.
          • semantic_neighbours[]    — (X11) the conceptually-related symbols (`semantically_nearest`).

        REUSES (rule 3 — no parallel system, no recomputed graph):
          1. resolve_scope(addr) → its `code://` symbols (S0 grammar gate raises on a malformed
             address; surfaces `stale` if the corpus join is unreadable). The SAME forward step X9 used.
          2. co_reference: invert each symbol's `referenced_by[]` from the SAME code-symbols.json,
             MINUS `addr` itself. `referenced_by[]` carries BOTH ui:// addresses AND feature-ids
             (ENG-*/NODE-*/WIRE-*) — both are legitimate neighbours (no ui-only filter).
          3. structural: `_structural_radius` → X10's `codeedges.reach_report` (bounded at DEPTH;
             dependents via a transposed edge view, the SAME bounded walk — no new BFS).
          4. semantic: `_semantic_radius` → X11's `semantically_nearest[]` read off the same index.

        Returns {address, symbols, co_reference, neighbours, structural_dependents,
        structural_dependencies, structural_dependents_capped, structural_dependencies_capped,
        structural_depth, semantic_neighbours, stale, note, structural_note, semantic_note}:
          • symbols      — the code:// ids this address resolves to (same as resolve_scope.symbols).
          • stale        — True if the CO-REFERENCE corpus index couldn't be read (mirrors
                           resolve_scope; fail-loud-legible — every kind empty + a regenerate note).
          • note         — the co-reference note (distinguishes the two co-reference empty cases:
                           (a) the address resolves to NO symbol, vs (b) symbols but no co-referrers).
          • *_capped     — True when a structural reach hit X10's DEPTH bound (no silent truncation).
          • structural_note / semantic_note — legible per-layer notes when a layer is absent/empty.

        GRACEFUL-EMPTY + fail-loud-legible (rule 4): a missing/stale layer → that KIND empty + its own
        note, never a crash, never a fabricated edge. code-edges.json absent → structural empty + a
        note; semantically_nearest[] absent (embedder :8001 down) → semantic empty + a note. The
        co-reference stale short-circuit (the corpus index itself unreadable) returns ALL kinds empty.

        X17 knob (`shared_only`, default False): restricts the co_reference contribution to symbols
        in the corpus's top-level `shared` set (a near-no-op on the result — a neighbour-bearing
        symbol is already shared by construction). A thin method param, NOT a config substrate.

        FRESHNESS: code-symbols.json + code-edges.json are REGENERATED (symbols.py / codeedges.py),
        not live; a stale index returns a stale (honestly-flagged) radius — never pretended live."""
        import json as _j
        # 1 — the forward step, REUSED from resolve_scope (S0 gate + stale + canonical symbols).
        forward = self.resolve_scope(ui_addr)
        symbols = forward["symbols"]
        if forward["stale"]:
            # fail-loud-legible: the corpus join is unreadable — ALL kinds empty + the regenerate note.
            return {"address": ui_addr, "symbols": symbols, "co_reference": [], "neighbours": [],
                    "structural_dependents": [], "structural_dependencies": [],
                    "structural_dependents_capped": False, "structural_dependencies_capped": False,
                    "structural_depth": None, "semantic_neighbours": [], "stale": True,
                    "note": forward["note"], "structural_note": forward["note"],
                    "semantic_note": forward["note"]}
        if not symbols:
            # this address resolves to NO referencing symbol (CSS-selector/orphan/absent) → no shared
            # code, no structural anchor, no semantic anchor. Honest empty across every kind.
            none_note = (f"{ui_addr!r} resolves to no code symbol "
                         f"(a CSS-selector/prose ref, an orphan, or absent from the corpus) — "
                         f"no shared code, so an EMPTY blast radius across all kinds (not an error)")
            return {"address": ui_addr, "symbols": [], "co_reference": [], "neighbours": [],
                    "structural_dependents": [], "structural_dependencies": [],
                    "structural_dependents_capped": False, "structural_dependencies_capped": False,
                    "structural_depth": None, "semantic_neighbours": [], "stale": False,
                    "note": none_note, "structural_note": none_note, "semantic_note": none_note}

        # 2 — CO-REFERENCE (X9, preserved). Read each resolved symbol's referenced_by[] from the
        # SAME already-loaded index, MINUS this address itself. Also reused below for X11's
        # semantically_nearest[] (one read of the index for both the co-reference + semantic layers).
        symbols_path = os.path.join(self._corpus_dir(), "code-symbols.json")
        with open(symbols_path, encoding="utf-8") as f:
            doc = _j.load(f)
        index = doc.get("symbols", {})
        shared = set(doc.get("shared") or [])               # X17: the symbols referenced by 2+ owners

        co_reference: set[str] = set()
        for sid in symbols:
            if shared_only and sid not in shared:
                continue                                    # X17 knob — restrict to shared symbols
            entry = index.get(sid) or {}
            for ref in (entry.get("referenced_by") or []):
                if ref != ui_addr:                          # MINUS self — the load-bearing exclusion
                    co_reference.add(ref)

        note = ""
        if not co_reference:
            # case (b): symbols resolved, but none are referenced by anything else → honest empty.
            note = (f"{ui_addr!r} resolves to {len(symbols)} code symbol(s) but none are referenced "
                    f"by any OTHER address/feature — an EMPTY co-reference blast radius "
                    f"(it touches code nothing else touches; not an error)")
        co_ref_sorted = sorted(co_reference)

        # 3 — STRUCTURAL (X10) + 4 — SEMANTIC (X11), each DISTINGUISHED, each graceful-empty.
        struct = self._structural_radius(symbols)
        sem = self._semantic_radius(symbols, index)

        return {"address": ui_addr, "symbols": symbols,
                # X9 (preserved): co_reference == the legacy `neighbours` field, byte-for-byte set.
                "co_reference": co_ref_sorted, "neighbours": co_ref_sorted,
                # X10 (bounded): dependents-to-VERIFY + dependencies-to-RESPECT, capped reported.
                "structural_dependents": struct["dependents"],
                "structural_dependencies": struct["dependencies"],
                "structural_dependents_capped": struct["dependents_capped"],
                "structural_dependencies_capped": struct["dependencies_capped"],
                "structural_depth": struct["depth"],
                # X11: conceptually-related (empty + note when the embedder was down at regen).
                "semantic_neighbours": sem["neighbours"],
                "stale": False, "note": note,
                "structural_note": struct["note"], "semantic_note": sem["note"]}

    # --- self-growth: build-dispatch (the "direct its growth" half of the first purpose) ---
    @staticmethod
    def _safe_node_name(name: str) -> str:
        if not isinstance(name, str) or not name.isidentifier() or name.startswith("_"):
            raise ValueError(f"unsafe node name {name!r} — must be a plain identifier (no paths, no '_'-prefix)")
        return name

    def propose_node(self, name: str, spec: str, model: str | None = None) -> dict:
        """The agent asks the brain to WRITE a new node module, then SURFACES it as a CONFIRM
        decision for the operator. It is NOT applied here. Returns {id, name, code}.
        (Proposing is safe — a model call + a surfaced gate; applying needs operator approval.)"""
        name = self._slug(name)                             # natural name -> safe identifier (PoLR)
        self._safe_node_name(name)                          # reject path-traversal after
        from fabric import client, transport, config as fcfg
        sys_p = ("You write ONE Python node module for the 'company' composition engine. "
                 "Output ONLY raw Python — no prose, no markdown fences.")
        user_p = (
            "Contract: a module with VERSION='1', KIND ('process'|'content'), PORTS_IN dict, "
            "PORTS_OUT dict, and def run(inputs: dict, config: dict) returning the output value.\n\n"
            "Example:\nVERSION='1'\nKIND='process'\nPORTS_IN={'text':'Text'}\nPORTS_OUT={'text':'Text'}\n"
            "def run(inputs, config):\n    return str(inputs.get('text','')).upper()\n\n"
            "LIVE-STATE RULE: the scheduler memo-caches a node's output by the hash of its inputs, so a "
            "node that READS MUTABLE TRUTH whose inputs don't change every run (the repo on disk, a model "
            "of someone, a clock, a corpus index, anything that drifts under a fixed address) MUST declare "
            "VOLATILE=True at module top-level, or it will serve a STALE frozen result forever. A pure "
            "transform of its inputs (uppercase, join, wordcount) must NOT set it. When unsure: does the "
            "same input ever need to produce a fresh output? If yes -> VOLATILE=True.\n\n"
            f"Write a node named '{name}' that: {spec}\n"
            "Use PORTS_IN={'text':'Text'} and PORTS_OUT={'text':'Text'} unless the spec needs otherwise. "
            "Output ONLY the code.")
        t = transport.openai_transport(base_url=fcfg.DEFAULT_BASE_URL, timeout=fcfg.DEFAULT_CLOUD_TIMEOUT)
        raw = _strip_fences(client.complete(
            t, [{"role": "system", "content": sys_p + "\n\n" + self._authoring_preamble()},
                {"role": "user", "content": user_p}], model=model or fcfg.DEFAULT_BRAIN))
        need = self._needs(raw)
        if need:
            return {"needs": need, "id": self._ask_operator(need, f"while building node '{name}': {spec}")}
        code = _tag_system_origin(raw)
        sid = self.inbox.surface("code_build", {"name": name, "code": code}, default="reject")
        self._emit("grow", f"brain wrote a '{name}' node — surfaced for approval", node_name=name, surfaced=sid,
                   address="ui://chrome/inbox")   # S2: a proposed node-type surfaces for approval in the inbox
        return {"id": sid, "name": name, "code": code}

    def apply_node(self, surfaced_id: str) -> str:
        """Apply a proposed node — ONLY if the OPERATOR approved its surfaced decision.
        Authorization is READ from the inbox (resolved=='approve'), never a caller flag, so the
        agent that proposed it cannot self-approve. Writes atomically + re-discovers. (code_build, D7)."""
        d = self.inbox.get(surfaced_id)
        if not d:
            raise KeyError(f"no surfaced decision {surfaced_id!r}")
        def _do():                                          # the consequential body — runs ONLY if approved
            name = self._safe_node_name(d["payload"]["name"])   # re-validate at apply
            code = d["payload"]["code"]
            path = os.path.join(self.nodes_dir, name + ".py")
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(code if code.endswith("\n") else code + "\n")
            os.replace(tmp, path)                           # atomic; no partial file
            sha = self._commit_or_rollback(path, f"add node-type '{name}'")  # fail loud if not git-revertible
            self.registry.discover([self.nodes_dir])        # committed -> NOW make it live
            self._emit("apply", f"approved + applied '{name}' — now a live node-type · {sha[:8]}",
                       node_name=name, commit=sha,
                       address="ui://chrome/workshop")   # S2: a self-change shows at the workshop self-changes surface
            self.refresh_map()
            return path
        # G1: POLICY is the single router. code_build → CONFIRM → runs only if the OPERATOR approved
        # the surfaced item (authorization READ from the substrate, never a caller flag). inbox=None so
        # the blocked path just raises GovernanceError — it must NOT re-surface (the item already exists).
        return guard("code_build", do=_do, confirmed=self.inbox.is_approved(surfaced_id))

    # =============================================================================================
    # AUTHORING BACKEND — Concurrent Cognition C7.4/C7.5 (the write-side of the cognition layer).
    # GENERALIZES propose_node/apply_node to ROLES + RULES: the operator authors a role/rule on the
    # surface → it SURFACES for approval (propose-not-apply) → apply writes the file ONLY on the
    # operator's `resolved=='approve'` (authorization READ from the inbox, never a caller flag) → the
    # RoleRegistry re-discovers → it appears in /api/cognition_info live (DYNAMIC).
    #
    # THE FLOOR (C9.2): NO authoring method emits resolve/approve/dispatch. Authoring SURFACES; the
    # OPERATOR approves (via the existing operator-only resolve_surfaced). None of these go in RHM_VERBS
    # — they are OPERATOR-face (like /api/build-intent), off the agent face (no self-author-and-approve).
    # =============================================================================================

    # Roles the runtime depends on BY NAME — deleting/renaming one bricks the system. We REFUSE to delete
    # these even on operator approve (a brick is never an acceptable approve outcome — advisor E).
    #
    # B-FIX (P3 — derive, don't second-copy): PROTECTED_ROLES had TWO classes of role conflated in one
    # hardcoded literal. They have DIFFERENT sources of truth, so the de-hardcode derives each from ITS
    # source rather than re-listing:
    #   (a) the SPIKE roles cognition.py imports by name at module load (focus/recall/ground —
    #       cognition.py:118-120, exposed as `cognition.SPIKE_ROLES`): a SECOND COPY of that set. We DERIVE
    #       it from cognition.SPIKE_ROLES in __init__ (registry-is-truth) — add a spike role there and it
    #       protects here with NO edit. A fail-loud drift guard asserts the derived superset still covers it.
    #   (b) the load-bearing CONFIG roles suite.py's OWN machinery binds by name (judge — the finished-thought
    #       endpoint, suite.py:5124/5188; voice — the voice circuit, ~1690s; connect — the NL→graph verb,
    #       ~1262; check; verify_jury — the jury verdict): these are suite-OWNED dependencies with no other
    #       source-of-truth to derive from (no role-file `protected` marker exists, and that file is not this
    #       lane's to add — surfaced, not faked). They stay declared HERE, the honest single source for "the
    #       roles suite.py itself depends on by name". The full PROTECTED_ROLES is the union, built in __init__.
    _SUITE_OWNED_PROTECTED_ROLES = ("judge", "verify_jury", "voice", "check", "connect")

    def _roles_dir_path(self, rid: str) -> str:
        from runtime.authoring import _safe_role_id
        return os.path.join(self.roles_dir, _safe_role_id(rid) + ".py")

    def _rediscover_roles(self) -> None:
        """Rebuild the live role registry from the FS so a written/removed role file reflects immediately
        (rediscover clears+discovers — a removed file actually un-registers, mirroring revert_self_change's
        registry.rediscover). Also refresh ROLE_REGISTRY (the dict-view suite consumers read)."""
        self.role_registry.rediscover([self.roles_dir])
        self.ROLE_REGISTRY = {rid: self.role_registry[rid].spec for rid in self.role_registry}

    def propose_role(self, spec: dict, *, model: str | None = None) -> dict:
        """C7.4 — AUTHOR a role: either the operator supplies the field-set (`spec` carries
        output_fields/prompt_template/…) OR the brain drafts from a natural-language `spec['brief']`.
        RENDER the role module source (runtime.authoring — the ONE renderer), GATE it (import in a temp
        dir — a bad role can NEVER brick RoleRegistry.discover, the #1 constraint), then SURFACE it for
        the operator (propose-not-apply, mirrors propose_node). It is NOT applied here. Returns
        {id, source, role_id} or {needs, id} if the brain hit unregistered ground (asks, never invents).

        Distinct action class `role_build` (CONFIRM) so apply routes to apply_role, NOT the generic
        apply_node (a role is a roles/<id>.py file, never a node-type)."""
        from runtime import authoring as _auth
        if not isinstance(spec, dict):
            raise TypeError(f"propose_role needs a dict spec, got {type(spec).__name__}")
        spec = dict(spec)
        # Brain-draft path: a free-text brief → the brain proposes a field-set (asks if it needs an
        # unregistered value). Reuses the propose_node authoring discipline (registry preamble + NEEDS:).
        if "brief" in spec and not spec.get("output_fields") and not spec.get("prompt_template"):
            drafted = self._draft_role_fields(spec["brief"], spec.get("id"), model=model)
            if "needs" in drafted:
                return drafted
            spec.update(drafted)
        rid = _auth._safe_role_id(spec.get("id"))
        if rid in self.role_registry:
            raise ValueError(
                f"role {rid!r} already exists — use edit_role to re-propose it (propose_role is for a NEW "
                f"role; editing an existing one re-surfaces a replacement). Fail loud.")
        source = _auth.render_role_source(spec)             # the ONE renderer (fields → BaseModel module)
        err = _auth.gate_role_source(rid, source)           # THE GATE — validate OUTSIDE the live tree
        if err:
            raise ValueError(
                f"propose_role({rid!r}): the rendered role module would NOT discover cleanly — {err}. "
                f"Refused to surface a broken role (a bad approve must never brick RoleRegistry.discover). "
                f"Fail loud.")
        sid = self.inbox.surface("role_build", {"id": rid, "source": source, "spec": spec},
                                 default="reject")
        self._emit("grow", f"a '{rid}' cognition role was authored — surfaced for approval",
                   node_name=rid, surfaced=sid, address="ui://chrome/inbox")
        return {"id": sid, "role_id": rid, "source": source}

    def _draft_role_fields(self, brief: str, rid: str | None = None, *, model: str | None = None) -> dict:
        """Brain-draft a role field-set from a natural-language brief (the optional brain-author path of
        propose_role). Reuses propose_node's authoring discipline: the registry preamble on the easy path
        + NEEDS: → ask, never fabricate. Returns a field-spec dict OR {needs, id}."""
        from fabric import client, transport, config as fcfg
        from runtime import authoring as _auth
        sys_p = (
            "You design ONE cognition ROLE for the 'company' collective-cognition layer. A role is a small "
            "model-function: it reads the utterance and emits a STRUCTURED output. Output ONLY a JSON object "
            "with keys: id (a plain lower identifier), label, description, prompt_template (the system "
            "prompt), output_fields (a list of {name, type, description}; type ∈ "
            f"{sorted(_auth.FIELD_TYPES)}), and optionally mode_scope (a list of modes), requires "
            "(capability tags). No prose, no fences.\n\n"
            + self._authoring_preamble())
        user_p = "Design a role" + (f" named '{rid}'" if rid else "") + f" that: {brief}"
        t = transport.openai_transport(base_url=fcfg.DEFAULT_BASE_URL, timeout=fcfg.DEFAULT_CLOUD_TIMEOUT)
        raw = _strip_fences(client.complete(
            t, [{"role": "system", "content": sys_p}, {"role": "user", "content": user_p}],
            model=model or fcfg.DEFAULT_BRAIN))
        need = self._needs(raw)
        if need:
            return {"needs": need, "id": self._ask_operator(need, f"while drafting a role: {brief}")}
        import json as _json
        try:
            drafted = _json.loads(raw)
        except Exception as e:
            raise ValueError(f"_draft_role_fields: the brain did not return valid JSON ({e}). Fail loud.")
        if rid:
            drafted["id"] = rid
        return drafted

    def apply_role(self, surfaced_id: str) -> str:
        """Apply a proposed role — ONLY if the OPERATOR approved its surfaced decision (authorization
        READ from the inbox, resolved=='approve', never a caller flag — the agent that proposed it cannot
        self-approve). RE-GATES the module (import in a temp dir) BEFORE the write — a bad role NEVER
        reaches the live roles/ tree (the #1 constraint: discovery fail-loud would brick the cognition
        layer). Writes atomically + git-commits (revert-able) + re-discovers → it appears in
        /api/cognition_info live. (role_build → CONFIRM.) Returns the written path."""
        d = self.inbox.get(surfaced_id)
        if not d:
            raise KeyError(f"no surfaced decision {surfaced_id!r}")
        if d.get("action") != "role_build":
            raise ValueError(
                f"apply_role: surfaced {surfaced_id!r} is a {d.get('action')!r}, not a role_build. Fail loud.")
        from runtime import authoring as _auth
        def _do():                                          # consequential body — runs ONLY if approved
            rid = _auth._safe_role_id(d["payload"]["id"])   # re-validate at apply
            source = d["payload"]["source"]
            # REUSE the shared write-half (gate → atomic write → commit → rediscover → emit), the SAME
            # body create_role uses (reuse-don't-parallel: ONE write path; this is "minus the approve").
            return self._write_role_file(
                rid, source, f"add cognition role '{rid}'",
                emit_msg=f"approved + applied role '{rid}' — now a live cognition role")
        return guard("role_build", do=_do, confirmed=self.inbox.is_approved(surfaced_id))

    def _write_role_file(self, rid: str, source: str, commit_msg: str, *, emit_msg: str) -> str:
        """The shared CONSEQUENTIAL write-half of role authoring — the factored body BOTH the
        approval-gated `apply_role` AND the DIRECT `create_role` (#58) call. RE-GATES the rendered
        module (import in a temp dir — defense-in-depth: a bad role NEVER reaches the live roles/ tree,
        the #1 constraint that a malformed roles/*.py would brick RoleRegistry.discover and the whole
        cognition layer), writes atomically, git-commits (revert-able via _commit_or_rollback), then
        re-discovers so the role goes LIVE in /api/cognition_info. Returns the written path.

        This factoring IS the #58 law made structural: create_role reuses apply_role's exact write+gate
        path MINUS the inbox `resolved=='approve'` check — not a parallel author path."""
        from runtime import authoring as _auth
        err = _auth.gate_role_source(rid, source)           # THE CORRECTNESS GATE — non-negotiable
        if err:
            raise RuntimeError(
                f"_write_role_file({rid!r}): the role module failed the gate ({err}) — REFUSED to write "
                f"it to roles/ (a bad role would brick RoleRegistry.discover). Fail loud.")
        path = self._roles_dir_path(rid)
        os.makedirs(self.roles_dir, exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(source if source.endswith("\n") else source + "\n")
        os.replace(tmp, path)                               # atomic; no partial file
        sha = self._commit_or_rollback(path, commit_msg)    # fail loud if not git-revertible
        self._rediscover_roles()                            # committed → NOW make it live
        self._emit("apply", f"{emit_msg} · {sha[:8]}",
                   node_name=rid, commit=sha, address="ui://chrome/workshop")
        self.refresh_map()
        return path

    def create_role(self, spec: dict, *, model: str | None = None) -> dict:
        """#58 DIRECT autonomous create — the agent CREATES a role LIVE, with NO operator approval.
        Tim's correction: the propose→surface→approve gate on CREATE was the AI's default, NOT his
        constraint. So this is `apply_role`'s render+GATE+write+commit+rediscover path MINUS the
        `resolved=='approve'` inbox check (reuse-don't-parallel — the SAME `_write_role_file`, no
        parallel author path; `propose_role` STAYS available for when an operator wants surfacing).

        EXPOSES THE FULL ROLE SCHEMA (`render_role_source` now emits every ROLE_FIELDS the spec sets:
        prompt_template · output_fields/output_schema · op · thinking · tools · knobs · model_binding ·
        input_addresses · mode_scope · rules · context · render_hint · …). The CORRECTNESS GATE is KEPT
        (a malformed/un-importable spec is REFUSED fail-loud, never written). The build-dispatch floor
        is UNTOUCHED — this writes a roles/ file (authoring), it never dispatches `claude -p`.

        Returns {role_id, path, live: True, source}. Fail loud on a malformed spec / an existing id."""
        from runtime import authoring as _auth
        if not isinstance(spec, dict):
            raise TypeError(f"create_role needs a dict spec, got {type(spec).__name__}")
        spec = dict(spec)
        # Brain-draft path (same as propose_role): a free-text brief → the brain drafts a field-set.
        if "brief" in spec and not spec.get("output_fields") and not spec.get("prompt_template"):
            drafted = self._draft_role_fields(spec["brief"], spec.get("id"), model=model)
            if "needs" in drafted:
                return drafted
            spec.update(drafted)
        rid = _auth._safe_role_id(spec.get("id"))
        if rid in self.role_registry:
            raise ValueError(
                f"role {rid!r} already exists — create_role is for a NEW role (use edit_role to replace "
                f"an existing one). Fail loud.")
        source = _auth.render_role_source(spec)             # the ONE renderer — the FULL schema
        path = self._write_role_file(                       # gate + write + commit + rediscover (DIRECT)
            rid, source, f"create cognition role '{rid}' (direct)",
            emit_msg=f"created role '{rid}' DIRECTLY — now a live cognition role")
        return {"role_id": rid, "path": path, "live": rid in self.role_registry, "source": source}

    def _entry_dir(self, kind: str) -> str:
        return self.skills_dir if kind == "skill" else self.contexts_dir

    def _entry_registry(self, kind: str):
        """Discover the skill/context registry over THIS Suite's dir (registry-is-truth, instance-local
        — so the live check + the create read the SAME dir the write targets; production dirs coincide
        with cognition._SKILLS_DIR/_CONTEXTS_DIR, so the global readers see it too)."""
        from runtime.skills import SkillRegistry, ContextRegistry
        Reg = SkillRegistry if kind == "skill" else ContextRegistry
        return Reg().discover([self._entry_dir(kind)])

    def _write_entry_file(self, kind: str, eid: str, source: str, commit_msg: str, *, emit_msg: str) -> str:
        """The shared CONSEQUENTIAL write-half of skill/context authoring (#56 write-half, #58 DIRECT).
        Mirrors `_write_role_file`: RE-GATE the rendered entry module (import in a temp dir — a bad
        entry NEVER reaches the live skills/contexts dir, which would brick the registry's discover),
        write atomically, git-commit (revert-able), then the entry goes LIVE (skill_registry()/
        context_registry() re-discover fresh each call, so no in-memory rediscover is needed). Returns
        the written path."""
        from runtime import authoring as _auth
        err = _auth.gate_entry_source(eid, source, kind=kind)   # THE CORRECTNESS GATE — non-negotiable
        if err:
            raise RuntimeError(
                f"_write_entry_file({kind} {eid!r}): the module failed the gate ({err}) — REFUSED to "
                f"write it (a bad {kind} would brick the registry's discover). Fail loud.")
        base = self._entry_dir(kind)
        os.makedirs(base, exist_ok=True)
        path = os.path.join(base, _auth._safe_entry_id(eid, kind) + ".py")
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(source if source.endswith("\n") else source + "\n")
        os.replace(tmp, path)                               # atomic; no partial file
        sha = self._commit_or_rollback(path, commit_msg)    # fail loud if not git-revertible
        self._emit("apply", f"{emit_msg} · {sha[:8]}",
                   node_name=eid, commit=sha, address="ui://chrome/workshop")
        self.refresh_map()
        return path

    def create_skill(self, spec: dict) -> dict:
        """#56 write-half · #58 DIRECT — the agent CREATES a skill LIVE, no operator approval (the
        skill-writing-skill, direct). Renders `skills/<id>.py` (id + content + label/description) →
        the CORRECTNESS GATE (import in a temp dir; a bad entry refused fail-loud) → write → commit →
        live (readable via skill://<id> + list_skills_contexts). reuse-don't-parallel: the SAME
        gate+write+commit path as create_role, over the skill registry. Returns {skill_id, path, live}."""
        from runtime import authoring as _auth
        if not isinstance(spec, dict):
            raise TypeError(f"create_skill needs a dict spec, got {type(spec).__name__}")
        eid = _auth._safe_entry_id(spec.get("id"), "skill")
        if eid in self._entry_registry("skill"):
            raise ValueError(f"skill {eid!r} already exists — create_skill is for a NEW skill. Fail loud.")
        source = _auth.render_entry_source(spec, kind="skill")
        path = self._write_entry_file("skill", eid, source, f"create skill '{eid}' (direct)",
                                      emit_msg=f"created skill '{eid}' DIRECTLY — now a live skill")
        return {"skill_id": eid, "path": path, "live": eid in self._entry_registry("skill")}

    def create_context(self, spec: dict) -> dict:
        """#56 write-half · #58 DIRECT — the agent CREATES a context LIVE, no operator approval. Mirrors
        create_skill over the context registry (context://<id>). Returns {context_id, path, live}."""
        from runtime import authoring as _auth
        if not isinstance(spec, dict):
            raise TypeError(f"create_context needs a dict spec, got {type(spec).__name__}")
        eid = _auth._safe_entry_id(spec.get("id"), "context")
        if eid in self._entry_registry("context"):
            raise ValueError(f"context {eid!r} already exists — create_context is for a NEW context. Fail loud.")
        source = _auth.render_entry_source(spec, kind="context")
        path = self._write_entry_file("context", eid, source, f"create context '{eid}' (direct)",
                                      emit_msg=f"created context '{eid}' DIRECTLY — now a live context")
        return {"context_id": eid, "path": path, "live": eid in self._entry_registry("context")}

    # === DECLARATIVE-DIRECT authoring of the 4 PURE-DATA corpus/cognition registries =================
    # (mark_type/generation_policy/relation_type/ai_tic) — #58 DIRECT, no approval. These are DATA
    # registries (a `<name>/<id>.py` declaring `<CONST> = {...}`), NOT executable-code/node-types — so the
    # FLOOR distinguishes them: declarative-direct authoring is DIRECT (render→the registry's OWN gate→
    # write→commit→rediscover; no operator-approval, NO resolve/approve/dispatch/claude-p). It MIRRORS
    # create_projection (the precedent) EXACTLY, but factored into ONE shared helper over the
    # _CORPUS_REGISTRIES table (reuse-don't-parallel — NO copy-pasted per-registry body, NO 2nd author path).
    # NOT here: lifter/form — their row carries a CALLABLE (extract/match), executable code that pprint can't
    # serialize + MCP-JSON can't carry → GATED code-authoring, flagged for the operator (see _CORPUS_REGISTRIES).
    def _write_registry_file(self, kind: str, spec: dict) -> dict:
        """The SHARED declarative-direct write-half for the 6 corpus/cognition registries (the proper
        long-term home create_projection's BAR2 seam wished for — `Suite.create_*` over a shared helper).
        Mirrors create_projection's mechanism, parametrized by the `_CORPUS_REGISTRIES` row:
          render `<CONST> = {...}` source (the declared row verbatim, pprint — PYTHON literal, not json) →
          THE CORRECTNESS GATE: import-in-tempdir via the registry's OWN `discover()` (a malformed spec
          RAISES in the registry's `_build_*`, BEFORE any write to the live dir — registry-is-truth, a bad
          row never goes live) → atomic write into the live `<name>/<id>.py` → git-commit via the shared
          `_commit_or_rollback` (path-scoped, revertible) → rediscover the live registry (go live in-process).
        Returns {id, kind, path, live, spec}. Fail loud on a non-dict spec / illegal id / existing id.
        THE FLOOR: this writes a DATA file (declarative authoring) — it NEVER dispatches claude -p; a
        node-type / executable-code create stays GATED, off this path."""
        import tempfile as _tempfile
        import pprint as _pprint
        if kind not in self._CORPUS_REGISTRIES:
            raise ValueError(f"_write_registry_file: unknown registry kind {kind!r} — known: "
                             f"{sorted(self._CORPUS_REGISTRIES)} (registry-is-truth; fail loud).")
        dir_attr, reg_attr, RegClass, const = self._CORPUS_REGISTRIES[kind]
        if not isinstance(spec, dict):
            raise TypeError(f"create_{kind} needs a dict spec (the registry ROW), got {type(spec).__name__}")
        rid = spec.get("id")
        if not rid or not isinstance(rid, str) or not rid.isidentifier():
            raise ValueError(
                f"create_{kind}: `id` must be a valid python identifier (it becomes {kind}/<id>.py — "
                f"addressable by file, like a role/skill/projection). Got {rid!r} — fail loud, never unnamed.")
        reg = getattr(self, reg_attr)
        if rid in reg:
            raise ValueError(
                f"{kind} {rid!r} already exists — create_{kind} is for a NEW entry. Fail loud "
                f"(registry-is-truth; existing: {sorted(reg)}).")
        # RENDER the row module source: `<CONST> = {...}` (the declared row verbatim). Filter to the
        # registry's OWN known FIELDS (the `<CONST>_FIELDS` tuple on the module) so a typo'd field is
        # dropped before the gate sees it — but the gate ALSO catches an unknown field fail-loud, so this
        # is belt-and-suspenders, not the gate. Trivial pprint serialization (PYTHON literal; bool/None
        # round-trip — NOT json.dumps which would emit true/null). NO logic, NO behaviour — DATA.
        _modname = RegClass.__module__               # e.g. "runtime.lifters"
        import importlib as _importlib
        _mod = _importlib.import_module(_modname)
        _fields = getattr(_mod, f"{const}_FIELDS", None)
        row = {k: v for k, v in spec.items() if (_fields is None or k in _fields)}
        row["id"] = rid
        # DEFENSE-IN-DEPTH (the table is the real gate, but be explicit): a value that is not a plain
        # data literal (e.g. a CALLABLE — a lifter's extract / a form's match) CANNOT round-trip through
        # the pprint DATA render. Such a registry is CODE-authoring, GATED, not data-create. Fail loud with
        # a legible message rather than emit a non-importable module. (lifter/form aren't in the table, so
        # this is a guard against a future row, not the live path.)
        for k, v in row.items():
            if callable(v):
                raise ValueError(
                    f"create_{kind}: field {k!r} is a CALLABLE — declarative-direct data-create cannot "
                    f"author executable code (pprint can't serialize a function). This registry needs a "
                    f"CODE-render+gate authoring contract (flagged for the operator). Fail loud.")
        source = (f'"""{kind}/{rid}.py — an agent-authored {kind} (create_{kind}, #58 declarative-direct).\n'
                  f'A declared registry ROW. See runtime/{kind}.py + {kind}/AGENTS.md.\n'
                  f'Its `id` MUST equal the file stem ({rid!r})."""\n\n'
                  f"{const} = {_pprint.pformat(row, indent=4, sort_dicts=True)}\n")
        # THE CORRECTNESS GATE — import-in-tempdir via the registry's OWN discover(). A malformed row
        # (bad id / missing required / unknown field / bad type) RAISES in the registry's _build_*, BEFORE
        # any write to the live dir. Mirrors create_projection's gate-in-tempdir (reuse the gate).
        with _tempfile.TemporaryDirectory() as _td:
            with open(os.path.join(_td, f"{rid}.py"), "w", encoding="utf-8") as _f:
                _f.write(source)
            gated = RegClass().discover([_td])       # RAISES on a malformed row (the gate)
            if rid not in gated:
                raise RuntimeError(
                    f"create_{kind}: rendered module for {rid!r} did not discover as a {const} — refused "
                    f"to write it (fail loud; a non-discovering row is a bug in the render).")
        # WRITE atomically into the LIVE dir, git-commit (path-scoped, revertible), rediscover → go live.
        base = getattr(self, dir_attr)
        os.makedirs(base, exist_ok=True)
        path = os.path.join(base, f"{rid}.py")
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as _f:
            _f.write(source)
        os.replace(tmp, path)                        # atomic; no partial file
        sha = self._commit_or_rollback(path, f"create {kind} '{rid}' (direct)")
        setattr(self, reg_attr, RegClass().discover([base]))   # rediscover → live in this process
        self._emit("apply", f"created {kind} '{rid}' DIRECTLY — now a live {kind} · {sha[:8]}",
                   node_name=rid, commit=sha)
        self.refresh_map()
        return {"id": rid, "kind": kind, "path": path,
                "live": rid in getattr(self, reg_attr), "spec": row}

    def create_mark_type(self, spec: dict) -> dict:
        """#58 DIRECT — create a MARK_TYPE (the type vocabulary a mark carries: gold_likelihood/
        ai_fingerprint/contradiction; value_shape + direction) LIVE, no approval. See runtime/mark_types.py."""
        return self._write_registry_file("mark_type", spec)

    def create_generation_policy(self, spec: dict) -> dict:
        """#58 DIRECT — create a GENERATION_POLICY (the rep_penalty LADDER regime run_role reads; NOTHING
        static) LIVE, no approval. See runtime/generation_policies.py."""
        return self._write_registry_file("generation_policy", spec)

    def create_relation_type(self, spec: dict) -> dict:
        """#58 DIRECT — create a RELATION_TYPE (typed/directional corpus relation: principle_beneath/
        fragment_of/contradicts/sibling) LIVE, no approval. See runtime/relation_types.py."""
        return self._write_registry_file("relation_type", spec)

    def create_ai_tic(self, spec: dict) -> dict:
        """#58 DIRECT — create an AI_TIC (the fingerprint marker vocabulary: framework_imposition/
        versioning/false_finality/…) LIVE, no approval. See runtime/ai_tics.py."""
        return self._write_registry_file("ai_tic", spec)

    # === MARKS — the suite-side API over STORE-2's append_mark/marks_for/marks_by_type ================
    # A MARK targets a CLAIM or SPAN (the `target` string), carries a REGISTERED mark_type (from the
    # mark_types registry — the type VOCABULARY), and round-trips by target AND by mark_type. The Suite
    # owns the mark_type GATE (fail-loud on an unknown type — rule 8, registry-is-truth); store.append_mark
    # stays DUMB on purpose (its docstring: it won't import the registry — the Suite is the gate). REUSE
    # STORE-2's append_mark/marks_for/marks_by_type — NO parallel mark store. The FLOOR holds: a mark is a
    # store append (telemetry-class write), never a resolve/approve/dispatch.
    def mark(self, target: str, mark_type: str, **fields) -> dict:
        """Append a MARK on a claim/span `target`, of a REGISTERED `mark_type`. The mark_type GATE bites
        here (fail-loud on an unknown type — never a fabricated mark_type; the type vocabulary is the
        mark_types registry, registry-is-truth). Extra `fields` (value/confidence/source_pass/evidence/…)
        splat through to the open mark record. Returns the persisted record. Reuses store.append_mark
        (the dumb store leaf) — the Suite is the only gate."""
        if not isinstance(target, str) or not target.strip():
            raise ValueError(f"mark: `target` must be a non-empty string (the claim/span it marks). "
                             f"Got {target!r} — fail loud.")
        if mark_type not in self.mark_type_registry:
            raise ValueError(
                f"mark: unknown mark_type {mark_type!r} — registered: {sorted(self.mark_type_registry)} "
                f"(registry-is-truth: a mark_type that is not a discovered file does not exist; author one "
                f"via create_mark_type. Fail loud — never a fabricated mark_type).")
        rec = {"target": target, "mark_type": mark_type, **fields}
        return self.store.append_mark(rec)

    def marks_for(self, target: str) -> list[dict]:
        """Every mark on `target`, oldest-first (the mark thread at that claim/span). Reuses
        store.marks_for (persistence-survives-reload; an unmarked target → [])."""
        return self.store.marks_for(target)

    def marks_by_type(self, mark_type: str) -> list[dict]:
        """Every mark of `mark_type` across targets, oldest-first (the cross-target view of one mark kind).
        Reuses store.marks_by_type. FAIL LOUD on an unknown mark_type (registry-is-truth) — a typo'd type
        would silently return [] and look like 'no marks', masking the error."""
        if mark_type not in self.mark_type_registry:
            raise ValueError(
                f"marks_by_type: unknown mark_type {mark_type!r} — registered: "
                f"{sorted(self.mark_type_registry)} (fail loud; a typo'd type silently returns []).")
        return self.store.marks_by_type(mark_type)

    def edit_role(self, rid: str, spec: dict, *, model: str | None = None) -> dict:
        """C7.4 — RE-PROPOSE an existing role (edit = author a replacement that surfaces for approval).
        A PROTECTED role (one the runtime imports by name) is REFUSED — surfaced as a needs-tim question
        rather than risk a brick. Otherwise renders+gates the replacement source and surfaces role_build."""
        from runtime import authoring as _auth
        rid = _auth._safe_role_id(rid)
        if rid not in self.role_registry:
            raise ValueError(f"edit_role: unknown role {rid!r} — registered: {sorted(self.role_registry)}")
        if rid in self.PROTECTED_ROLES:
            q = (f"role {rid!r} is imported by name by the runtime (cognition.py / config) — editing its "
                 f"shape could break system import. This needs your eyes before any change.")
            return {"protected": True, "needs": q, "id": self._ask_operator(q, f"edit_role({rid})")}
        spec = dict(spec); spec["id"] = rid
        source = _auth.render_role_source(spec)
        err = _auth.gate_role_source(rid, source)
        if err:
            raise ValueError(f"edit_role({rid!r}): the replacement would not discover — {err}. Fail loud.")
        sid = self.inbox.surface("role_build", {"id": rid, "source": source, "spec": spec, "edit": True},
                                 default="reject")
        self._emit("grow", f"a replacement for role '{rid}' was authored — surfaced for approval",
                   node_name=rid, surfaced=sid, address="ui://chrome/inbox")
        return {"id": sid, "role_id": rid, "source": source, "edit": True}

    def delete_role(self, rid: str) -> dict:
        """C7.4 — SURFACE the removal of a role for the operator's approval (propose-not-apply applies to
        deletes too). A PROTECTED role is REFUSED (a brick is never an acceptable approve outcome).
        apply_role_delete performs the removal ONLY on operator approve. Returns the surfaced id."""
        from runtime import authoring as _auth
        rid = _auth._safe_role_id(rid)
        if rid not in self.role_registry:
            raise ValueError(f"delete_role: unknown role {rid!r} — registered: {sorted(self.role_registry)}")
        if rid in self.PROTECTED_ROLES:
            q = (f"role {rid!r} is imported by name by the runtime — DELETING it would break system import. "
                 f"Refused to surface a brick. This needs your eyes (a code-level migration, not a delete).")
            return {"protected": True, "needs": q, "id": self._ask_operator(q, f"delete_role({rid})")}
        sid = self.inbox.surface("role_delete", {"id": rid}, default="reject")
        self._emit("grow", f"removal of role '{rid}' was requested — surfaced for approval",
                   node_name=rid, surfaced=sid, address="ui://chrome/inbox")
        return {"id": sid, "role_id": rid, "delete": True}

    def apply_role_delete(self, surfaced_id: str) -> dict:
        """Remove a role file — ONLY on the OPERATOR's approve (authorization READ from the inbox).
        Re-checks PROTECTED (defense-in-depth), removes the file, git-commits the removal (revert-able),
        re-discovers (the role un-registers). (role_delete → CONFIRM.)"""
        d = self.inbox.get(surfaced_id)
        if not d:
            raise KeyError(f"no surfaced decision {surfaced_id!r}")
        if d.get("action") != "role_delete":
            raise ValueError(f"apply_role_delete: {surfaced_id!r} is not a role_delete. Fail loud.")
        from runtime import authoring as _auth
        def _do():
            rid = _auth._safe_role_id(d["payload"]["id"])
            if rid in self.PROTECTED_ROLES:
                raise RuntimeError(f"apply_role_delete: role {rid!r} is PROTECTED (runtime imports it). Refused.")
            path = self._roles_dir_path(rid)
            if not os.path.exists(path):
                raise FileNotFoundError(f"apply_role_delete: role file {path} does not exist. Fail loud.")
            os.remove(path)
            sha = self._git_self_commit([path], f"remove cognition role '{rid}'")
            self._rediscover_roles()
            self._emit("apply", f"approved + removed role '{rid}' · {(sha or '?')[:8]}",
                       node_name=rid, commit=sha, address="ui://chrome/workshop")
            self.refresh_map()
            return {"removed": rid, "commit": sha}
        return guard("role_delete", do=_do, confirmed=self.inbox.is_approved(surfaced_id))

    # --- RULE authoring (expose the runtime/rules.py primitives — never a parallel evaluator) ---
    def validate_rule(self, ast: dict, *, destination: str | None = None) -> dict:
        """C7.4 — VALIDATE a rule's condition AST + (optionally) its destination for the FE rule-builder.
        Wraps runtime/rules.py's static whitelist-walk (validate_ast) + the destination check, so the FE
        gets LIVE validation: is this AST legal/deterministic, what role-inputs does it reference, is the
        destination one of the 5 kinds (never a forbidden resolve/approve/dispatch), is it renderable
        (depth-capped)? Returns {ok, errors[], references[], destination_ok, renderable, when_text, depth}.
        PURE — no write, no approval (read-only)."""
        from runtime import rules as _rules
        out = {"ok": True, "errors": [], "references": [], "destination": destination,
               "destination_ok": None, "renderable": True, "when_text": None, "depth": None}
        try:
            _rules.validate_ast(ast)                        # the static grammar walk (fail loud on bad op/arity/depth)
            out["references"] = sorted(_rules.declared_inputs(ast))
            out["when_text"] = _rules._render_ast(ast)
            out["depth"] = _rules._ast_depth(ast)
            out["renderable"] = out["depth"] <= _rules.MAX_RULE_DEPTH
        except _rules.RuleError as e:
            out["ok"] = False
            out["errors"].append(str(e))
        if destination is not None:
            ok_dest = destination in _rules.DESTINATION_KINDS and \
                destination not in _rules.FORBIDDEN_DESTINATION_VERBS
            out["destination_ok"] = ok_dest
            if not ok_dest:
                out["ok"] = False
                out["errors"].append(
                    f"destination {destination!r} must be one of {sorted(_rules.DESTINATION_KINDS)} and "
                    f"NEVER one of {_rules.FORBIDDEN_DESTINATION_VERBS} (the claude -p floor is lead-only).")
        return out

    def dry_run_rule(self, ast: dict, sample_resolved: dict, *, destination: str = "inject",
                     params: dict | None = None, on_missing: str = "raise") -> dict:
        """C7.4 — DRY-RUN a rule over SAMPLE resolved values → the routing DECISION (no effect). Builds a
        Rule (validated at construction) and calls its PURE decide() over the sample — so the FE can show
        'with these inputs → this fires → routes to <dest>'. Wraps rules.Rule.decide; never executes the
        destination effect (no route()). Returns the decision {fire, destination, value, reason} (or an
        {error} on a malformed AST / missing sample input — fail loud, surfaced as data for the builder)."""
        from runtime import rules as _rules
        try:
            rule = _rules.build_rule({"id": "dry-run", "when": ast, "destination": destination,
                                      "params": params or {}, "on_missing": on_missing})
            decision = rule.decide(sample_resolved)
            return {"ok": True, "decision": decision, "when_text": rule._render_when()}
        except _rules.RuleError as e:
            return {"ok": False, "error": str(e)}

    def attach_rule(self, role_id: str, rule: dict) -> dict:
        """C7.4 — ATTACH a declared rule onto a role (a constrained edit_role that appends to ROLE['rules']).
        Validates the rule (build_rule — fail loud on a bad AST/destination) THEN re-proposes the role with
        the rule added (propose-not-apply: surfaces role_build for the operator). Reuses edit_role (one
        writer; never a parallel role-file mutator). A PROTECTED role is refused (via edit_role)."""
        from runtime import rules as _rules
        from runtime import authoring as _auth
        role_id = _auth._safe_role_id(role_id)
        if role_id not in self.role_registry:
            raise ValueError(f"attach_rule: unknown role {role_id!r}. Fail loud.")
        _rules.build_rule(rule)                             # VALIDATE the rule (fail loud) BEFORE attaching
        spec = self._role_spec_to_authoring_fields(dict(self.role_registry[role_id].spec))
        existing = list(spec.get("rules") or [])
        existing = [r for r in existing if r.get("id") != rule.get("id")] + [rule]   # replace-or-add by id
        spec["rules"] = existing
        return self.edit_role(role_id, spec)

    def detach_rule(self, role_id: str, rule_id: str) -> dict:
        """C7.4 — DETACH a rule from a role (constrained edit_role removing it from ROLE['rules']).
        Re-proposes the role without the rule (propose-not-apply). PROTECTED role refused via edit_role."""
        from runtime import authoring as _auth
        role_id = _auth._safe_role_id(role_id)
        if role_id not in self.role_registry:
            raise ValueError(f"detach_rule: unknown role {role_id!r}. Fail loud.")
        spec = self._role_spec_to_authoring_fields(dict(self.role_registry[role_id].spec))
        spec["rules"] = [r for r in (spec.get("rules") or []) if r.get("id") != rule_id]
        return self.edit_role(role_id, spec)

    @staticmethod
    def _role_spec_to_authoring_fields(spec: dict) -> dict:
        """Project a discovered role's `spec` dict back into the AUTHORING field-shape render_role_source
        expects (output_schema CLASS → output_fields LIST). So an edit/attach round-trips through the ONE
        renderer (never hand-editing the file). Reads the Pydantic model's fields back to field-defs."""
        out = {k: spec[k] for k in
               ("id", "label", "description", "prompt_template", "input_addresses", "trigger", "rules")
               if k in spec}
        if spec.get("mode_scope"):
            out["mode_scope"] = list(spec["mode_scope"])
        mb = spec.get("model_binding") or {}
        if mb.get("requires"):
            out["requires"] = list(mb["requires"])
        osch = spec.get("output_schema")
        fields = []
        if osch is not None and hasattr(osch, "model_fields"):
            _known = {"str", "int", "float", "bool", "list[str]", "list[int]"}
            for fname, finfo in osch.model_fields.items():
                # str(annotation) yields EXACTLY 'list[int]'/'list[str]'/'<class 'int'>' — match the list
                # forms verbatim (so list[int] does NOT silently become list[str] on an edit round-trip),
                # else fall back to the scalar __name__. Any unknown annotation → 'str' (never invent a type).
                sann = str(finfo.annotation)
                if sann in _known:
                    ftype = sann
                else:
                    nm = getattr(finfo.annotation, "__name__", None) or sann
                    ftype = nm if nm in _known else "str"
                fd = {"name": fname, "type": ftype}
                if finfo.description:
                    fd["description"] = finfo.description
                fields.append(fd)
        if fields:
            out["output_fields"] = fields
        return out

    # --- TEST / preview (so the FE can test a draft before saving) ---
    def dry_run_role(self, role_or_fields, utterance: str, *, model: str | None = None,
                     base_url: str | None = None) -> dict:
        """C7.4 — FIRE one role with `utterance` → the validated structured output (test a role in
        isolation, no full turn). `role_or_fields` is EITHER a registered role id (str) OR a draft
        field-spec (dict — render + load from a temp module, the never-yet-written case). Reuses
        cognition.run_role (the SAME fire path run_swarm uses — a dry-run behaves identically to live).
        Fires the resident 4B by default (read-only USE). Returns {role_id, output} or fail-loud error."""
        from runtime import cognition as _cog
        from runtime import authoring as _auth
        if isinstance(role_or_fields, str):
            rid = _auth._safe_role_id(role_or_fields)
            if rid not in self.role_registry:
                raise ValueError(f"dry_run_role: unknown role {rid!r} — registered: {sorted(self.role_registry)}")
            role = self.role_registry[rid]
        elif isinstance(role_or_fields, dict):
            rid = _auth._safe_role_id(role_or_fields.get("id"))
            source = _auth.render_role_source(role_or_fields)
            role = _auth.load_role_from_source(rid, source)   # the SAME RoleRegistry discovery (no fork)
        else:
            raise TypeError("dry_run_role needs a role id (str) or a draft field-spec (dict)")
        if not role.can_fire:
            raise ValueError(f"dry_run_role: role {rid!r} cannot fire (no prompt_template/output_schema).")
        kw = {}
        if base_url:
            kw["base_url"] = base_url
        if model:
            kw["model"] = model
        output = _cog.run_role(role, {"utterance": utterance}, **kw)
        return {"role_id": rid, "output": output}

    def preview_turn(self, utterance: str, mode: str | None = None, *, graph_id: str | None = None) -> dict:
        """C7.4 — PREVIEW a full STAGED turn for a draft config: fire chat_parts and return the parts +
        the per-turn cognition.* lifecycle (the cast that fired, the injections, the staging). Reuses
        chat_parts (the G4 staged-turn path — never a parallel turn engine) with persist=False, so the
        preview FIRES A REAL STAGED TURN but does NOT append phantom turns to the live chat history /
        training_signal pipe / thread (the non-mutating test path — AGENTS.md rule 4: a 'read-only'
        affordance that secretly wrote would be a silent failure). The cognition.* lifecycle telemetry is
        narration and still fires (it is what the preview returns). If `mode` is given it is set for the
        preview then RESTORED (a preview never leaves the dial moved). Returns {parts[], mode,
        cognition_events[], n_parts}. Non-mutating USE of the resident swarm."""
        # default to the first live graph (registry-driven — never a hardcoded literal); fail loud if
        # there are none (a preview needs SOME graph for context; chat_parts reads it like chat() does).
        if not graph_id:
            graphs = self.list_graphs()
            if not graphs:
                raise ValueError("preview_turn: no graph exists to provide context — create one first (fail loud).")
            graph_id = graphs[0]
        gid = graph_id
        prev_mode = self.get_mode()
        restore = False
        if mode is not None and mode != prev_mode:
            if mode not in self.MODES:
                raise ValueError(f"preview_turn: unknown mode {mode!r} — one of {self.MODES}")
            self.set_mode(mode)
            restore = True
        try:
            since = self.store.events_since(-1)
            cursor = since[-1]["seq"] if since else -1
            parts = []
            for p in self.chat_parts(utterance, gid, persist=False):   # non-mutating: no chat-history append
                parts.append({k: p.get(k) for k in ("part", "text", "final", "staged")})
            # event records carry the kind on the `kind` field (store.append_event schema), NOT `op`.
            new_events = [e for e in self.store.events_since(cursor)
                          if str(e.get("kind", "")).startswith("cognition.")]
            return {"utterance": utterance, "mode": (mode or prev_mode), "parts": parts,
                    "cognition_events": new_events, "n_parts": len(parts)}
        finally:
            if restore:
                self.set_mode(prev_mode)

    # --- the SELECT queries (so the FE populates every dropdown from truth, never hardcoded) ---
    def models_for_role(self, requires) -> dict:
        """C7.4 — the MODEL-SELECT: the model-ids whose `provides` ⊇ `requires` (wraps
        capabilities.suitable_models — registry-is-truth; a NEW model with the right provides is
        automatically a candidate). Plus the live providers the swarm actually binds against. Returns
        {requires, models[], providers{}}. Read-only."""
        reqs = list(requires) if isinstance(requires, (list, tuple, set)) else \
            ([r.strip() for r in str(requires).split(",") if r.strip()] if requires else [])
        providers = self.capability_providers()
        try:
            import sys as _sys
            _opscli = os.path.join(self._repo_root, "ops", "cli")
            if _opscli not in _sys.path:
                _sys.path.insert(0, _opscli)
            import capabilities as _caps
            models = _caps.suitable_models(reqs)
        except Exception:
            # fail-soft to the live providers (never a silent WRONG set — the resident is the truth that
            # always holds; the full catalog is the ops/cli capability registry, flagged if unreadable).
            models = [p["model"] for p in providers.values() if set(reqs) <= set(p.get("provides", []))]
        return {"requires": reqs, "models": sorted(set(models)), "providers": providers}

    def available_inputs(self, turn_context: dict | None = None) -> dict:
        """C7.4 — the INPUT-WIRING SELECT: the addresses a role/rule can READ. The utterance (always),
        the OTHER roles' run:// outputs (a rule reads run://<turn>/<role>, declared as the role id), and
        the notebook strata (the C6 context variables) — so the FE rule-builder/role-editor populates the
        'reads' dropdown from truth, not a hardcoded list. Returns {utterance, roles[], role_addresses[],
        context_variables[]}. Read-only."""
        roles = sorted(rid for rid in self.role_registry if self.role_registry[rid].can_fire)
        ctx_vars = []
        try:
            from runtime import context_variables as _cv
            ctx_vars = sorted(getattr(_cv, "REGISTRY", {}).keys())
        except Exception:
            ctx_vars = []
        # Cognition Engine K1/L — PROJECT the file-discovered PROJECTION registry into the input space.
        # The embeddable lenses (Group L) are vector SPACES (vec://<item>#space=<id>) a corpus-reading
        # role/rule can READ as an input (RAG-over-the-corpus, D3), so the 'reads' select advertises them
        # from truth, never a hardcoded list: drop a `projections/<id>.py` with embeds:true → restart →
        # it appears here. `projections` is every lens id (the discovery vocabulary); `projection_spaces`
        # is the templated read-address per embeddable lens (the per-item space the corpus capture writes).
        # ADDITIVE — every prior key (utterance/roles/role_addresses/context_variables) is unchanged.
        projections = sorted(self.projection_registry)
        spaces = [p.id for p in self.projection_registry.embeddable()]
        # The 6 OTHER file-discovered corpus/cognition registries (719f82d) — ADVERTISE their ids in the
        # composition select so the agent can SEE + USE them where it composes (registry-is-truth: drop a
        # `<name>/<id>.py` → restart → it appears here with NO code change). These are the discovery/
        # capture vocabulary a corpus-reading role/rule/cascade composes with: lifters (code extractors) ·
        # mark_types (the type vocab for marks) · generation_policies (the rep_penalty regimes run_role
        # reads — NOTHING static) · relation_types · ai_tics · forms (effort-routing). ADDITIVE — every
        # prior key is unchanged.
        return {"utterance": "utterance", "roles": roles,
                "role_addresses": [f"run://<turn>/{r}" for r in roles],
                "context_variables": ctx_vars,
                "projections": projections,
                "projection_spaces": [f"vec://<item>#space={s}" for s in spaces],
                "lifters": sorted(self.lifter_registry),
                "mark_types": sorted(self.mark_type_registry),
                "generation_policies": sorted(self.generation_policy_registry),
                "relation_types": sorted(self.relation_type_registry),
                "ai_tics": sorted(self.ai_tic_registry),
                "forms": sorted(self.form_registry)}

    def field_types(self) -> dict:
        """C7.5 — the closed field-type registry the FE schema-editor reads (registry-is-truth — the
        output_schema field-type dropdown comes from here, never a hardcoded FE list)."""
        from runtime import authoring as _auth
        return _auth.field_types()

    # ============================================================================================
    # Cognition Engine GROUP D — the CORPUS SINK + the inversion-finder (thin Suite methods)
    # --------------------------------------------------------------------------------------------
    # These are the SUITE-lane FACE over runtime/corpus.py (D1) + store/vector_index.query_index's
    # space filter (Group L / L2). They are THIN — they REUSE corpus.py + query_index, never
    # reimplement the record gate, the dedup-on-read, or the cosine ranking (reuse-don't-parallel).
    # THE FLOOR (C9.2): every one of these is a READ or a corpus.record telemetry write — NONE emits
    # resolve/approve/dispatch, and NONE is in RHM_VERBS or on the MCP face (the SURFACE/BRIDGE lanes
    # expose them as tools/routes; this lane only provides the methods).
    # ============================================================================================
    def write_corpus_record(self, *, source_address: str, output, kind: str, lineage: dict,
                            model: str | None = None, projection: str | None = None, **extra) -> dict:
        """D1 — persist ONE corpus record (durable cas:// + a deterministic run:// pointer + a
        `corpus.record` index event) via runtime/corpus.write_record over THIS Suite's store. The LINEAGE
        GATE bites here (session/round/project REQUIRED — fail-loud CorpusError, never a silent default):
        a record without lineage is uncorroboratable cross-session (M3) and unplaceable by the
        inversion-finder (L2). Thin reuse — corpus.py owns the gate + the resume-safe deterministic
        address; this just supplies self.store."""
        from runtime import corpus as _corpus
        return _corpus.write_record(self.store, source_address=source_address, output=output, kind=kind,
                                    lineage=lineage, model=model, projection=projection, **extra)

    def read_corpus_record(self, address: str) -> dict | None:
        """D1 — read a corpus record back by its run:// address (head→get_content, the canonical resolver
        path). An HONEST None if never written — never a crash, never a fabricated record. Thin reuse of
        corpus.read_record."""
        from runtime import corpus as _corpus
        return _corpus.read_record(self.store, address)

    def list_corpus(self, *, project: str | None = None) -> list[dict]:
        """D5 — the DISCOVERED corpus records: a READ-TIME PROJECTION over the ONE event log (the
        run-index sibling, filtered to `corpus.record`), dedup-on-read (resume-safe, latest-seq wins),
        newest-first, optionally narrowed to a lineage `project`. No maintained index, no parallel DB
        (reuse-don't-parallel — the log IS the index). Thin reuse of corpus.list_corpus."""
        from runtime import corpus as _corpus
        return _corpus.list_corpus(self.store, project=project)

    def find_corpus(self, *, project: str | None = None, kind: str | None = None,
                    projection: str | None = None, source_address: str | None = None) -> list[dict]:
        """D5 — the FILTERED corpus projection (the query face): list_corpus narrowed by any of the
        lineage/record axes (project · record kind · projection lens · source_address). Thin reuse of
        corpus.find_corpus (registry-is-truth: filters the discovered set, never a hand-listed one)."""
        from runtime import corpus as _corpus
        return _corpus.find_corpus(self.store, project=project, kind=kind, projection=projection,
                                   source_address=source_address)

    def find_relations(self, item: str, *, near_space: str, far_space: str, k: int = 10,
                       min_score: float = 0.5) -> dict:
        """GROUP L2 — THE INVERSION-FINDER: the cross-space relation query "same principle, different
        subject." Over the SPACE-KEYED persisted vector index (store/vector_index.query_index with the
        `space=` filter), it returns the items NEAR `item` in `near_space` but NOT near it in `far_space`
        (a near∩¬far set difference): e.g. units sharing a PRINCIPLE (near=principles) yet diverging in
        TOPIC (far=topics) — the inversion the discovery loop surfaces.

        MECHANISM (reuse-don't-parallel — NO cosine reimplemented):
          • the QUERY VECTOR is the item's OWN persisted per-space vector (store.get_vector over
            store.space_address(item, near_space)) — the same vector the capture/embed pass wrote. So the
            ranking is item-anchored, not a re-embed (NO :8001 dependency on the query side — the persisted
            vectors are enough; matters because the embedder is DOWN right now).
          • near = the items in `near_space` whose cosine to the item's near-vector ≥ `min_score`.
          • far  = the items in `far_space` whose cosine to the item's far-vector ≥ `min_score`.
          • relations = near.ids − far.ids − {item} : near in near_space, NOT near in far_space.

        WHY A THRESHOLD, not the raw ranked list (the correctness pivot): query_index/nodes.retrieve
        returns EVERY indexed item ranked by cosine — including score≈0 items (a k larger than the corpus
        returns the whole space). "In the far ranked list" therefore ≠ "is a far-NEIGHBOUR" — using mere
        presence would put EVERY item in `far_ids` and the difference would always be empty (the bug this
        guards). So a NEIGHBOUR is an item whose cosine ≥ `min_score` (DEFAULT 0.5; a cluster_threshold is
        a per-projection RELATION/GENERATION POLICY — the relation-type/generation-policy registries, a
        later NEWMOD pass — so it is a tunable PARAM here, not a hardcoded global, and becomes
        registry-projected when those land). The k-NN is still computed via query_index (reuse — no cosine
        reimplemented); the threshold is applied to its returned scores.

        FAIL LOUD (rule 4): if `item` has no persisted vector in EITHER named space, raise — the inversion
        is undefined without both anchors (never a silent empty that reads as 'no relations'). An
        unpopulated space (the embedder was down at build) yields no neighbours (a true empty difference),
        DISTINCT from the missing-anchor fail-loud.

        Returns {item, near_space, far_space, min_score, relations[], near[], far[]} — relations is the
        inversion result (source ids); near/far carry the THRESHOLDED neighbour rows (id+score) for the
        surface to render the WHY. Read-only; no model call; not on the MCP face / not in RHM_VERBS."""
        from store import vector_index as _vx
        near_key = self.store.space_address(item, near_space)
        far_key = self.store.space_address(item, far_space)
        near_rec = self.store.get_vector(near_key)
        far_rec = self.store.get_vector(far_key)
        if near_rec is None or near_rec.get("vector") is None:
            raise ValueError(
                f"find_relations: item {item!r} has no persisted vector in near_space {near_space!r} "
                f"(address {near_key!r}) — the inversion is anchored on the item's OWN per-space vector, "
                f"so it must be embedded in both spaces first (run the capture+embed pass). Fail loud, "
                f"never a silent empty result that looks like 'no relations'.")
        if far_rec is None or far_rec.get("vector") is None:
            raise ValueError(
                f"find_relations: item {item!r} has no persisted vector in far_space {far_space!r} "
                f"(address {far_key!r}) — both anchors are required for a near∩¬far inversion. Fail loud.")
        # k-NN within each space (reuse query_index — never a reimplemented cosine), then THRESHOLD to a
        # true neighbour set (score ≥ min_score) so a score≈0 item is NOT counted as 'near' (see WHY above).
        near = [r for r in _vx.query_index(self.store, near_rec["vector"], k=k, space=near_space)
                if r.get("score", 0.0) >= min_score]
        far = [r for r in _vx.query_index(self.store, far_rec["vector"], k=k, space=far_space)
               if r.get("score", 0.0) >= min_score]
        far_ids = {r["id"] for r in far}
        relations = [r["id"] for r in near if r["id"] not in far_ids and r["id"] != item]
        return {"item": item, "near_space": near_space, "far_space": far_space, "min_score": min_score,
                "relations": relations, "near": near, "far": far}

    # --- self-modification safety net (slice 13): additive + git-reversible ---
    @property
    def _repo_root(self) -> str:
        return os.path.dirname(self.nodes_dir)

    def _git_self_commit(self, paths: list[str], msg: str, *, prefix: str = "[self-apply]") -> str | None:
        """Commit a self-authored change so it is ALWAYS one `git revert` away (the real safety
        net — not the operator gate). Path-scoped; tagged with `prefix` (default `[self-apply]` for
        the self-mod streams; the wire's accepted-build close passes `[self-build]` so the two
        revertible-commit streams stay DISTINCT in the log without a parallel git path). None if the
        commit fails. `revert_self_change(sha)` is prefix-agnostic (it just `git revert`s a sha), so a
        `[self-build]` commit reverts via the SAME operator path as a `[self-apply]` one.

        Path-scoped (`git add <paths>`): only the named paths are staged here, so a concurrent
        writer's unstaged dirty files are NEVER swept in — this is the concurrent-writer isolation the
        wire's checkpoint rests on (the wire passes EXACTLY the build's `changed_delta`)."""
        import subprocess
        try:
            subprocess.run(["git", "-C", self._repo_root, "add", *paths], check=True, capture_output=True)
            # PATHSPEC-SCOPED commit (`commit -- <paths>`): commit ONLY the named paths, NOT whatever
            # else happens to be in the shared index. The bridge is ONE process; apply_node's
            # `[self-apply]` path also does an unlocked add+commit on the SAME index, and the wire's
            # commit runs outside the per-seq dispatch lock — so without the pathspec a concurrent
            # `[self-apply]` add could be swept into THIS commit (wrong attribution + lost update +
            # the other path's os.remove-on-fail deleting a just-committed file). The pathspec makes the
            # "concurrent writer's files are NEVER swept in" guarantee UNCONDITIONAL (not just "they're
            # usually unstaged"). Strictly safe for the [self-apply] caller too (it writes one file then
            # commits exactly it — a partial commit of a just-added new/modified path works).
            subprocess.run(["git", "-C", self._repo_root, "commit", "-m", f"{prefix} {msg}", "--", *paths],
                           check=True, capture_output=True)
            out = subprocess.run(["git", "-C", self._repo_root, "rev-parse", "HEAD"],
                                 check=True, capture_output=True, text=True)
            return out.stdout.strip()
        except Exception:
            return None

    def _self_build_commit(self, paths: list[str], msg: str) -> str | None:
        """The wire's accepted-build CHECKPOINT — commit EXACTLY the build's changed_delta paths so
        each autonomous build the wire accepts is a single revertible git commit (`git revert <sha>`,
        the SAME operator path as a self-apply). Tagged `[self-build]` (DISTINCT from `[self-apply]`
        self-mod), path-scoped (so a concurrent writer's unstaged dirty files — design/blueprint/*.json
        — are NEVER swept in). Returns the resulting sha, or None if the commit fails (the caller then
        surfaces the build back, never marking it implemented — a build that can't be checkpointed is
        not safe-closed). This is a thin reuse of `_git_self_commit` with the wire prefix — NOT a
        parallel git path — and is the default `committer` injected into dispatch_decision (a test
        supplies a stub so no real commit hits the live repo)."""
        return self._git_self_commit(list(paths), msg, prefix="[self-build]")

    def _commit_or_rollback(self, path: str, msg: str) -> str:
        """Commit a just-written self-change; if the commit FAILS, roll the file back and raise —
        never leave a live self-change without its revert safety net (red-team F2: fail loud, not
        silent success). Returns the sha on success."""
        sha = self._git_self_commit([path], msg)
        if not sha:
            try:
                os.remove(path)
            except OSError:
                pass
            raise RuntimeError(
                f"git commit failed for {os.path.basename(path)} — rolled back the write and refused "
                "to apply: a self-change must be git-revertible (the safety net), or it does not go live.")
        return sha

    @staticmethod
    def _is_revert_subject(subject: str) -> bool:
        """A `git revert` of a self-change produces subject `Revert "<prefix> ..."` — which STILL
        contains the prefix, so the coarse `--grep` matches the REVERT itself. So an undo is NOT a
        change: distinguish it by subject prefix, for EITHER reversible stream (`[self-apply]` AND
        `[self-build]`). (Finding #2: prevents 'revert the revert' — and a revert's --invert-grep can't
        be expressed alongside the positive grep, so we tag in Python.)"""
        s = subject or ""
        return any(s.startswith(f'Revert "{prefix}') for _, prefix in Suite._SELF_CHANGE_STREAMS)

    def _self_change_changed_files(self, sha: str) -> list[str]:
        """The files a self-apply commit touched — git ground truth (`git show --name-only`), so the
        record surfaces WHICH files it changed (Finding #4; mirrors the wire's `changed_files` manifest
        and the very call selfmod_acceptance asserts at HEAD). Tolerant: an unreadable commit reads as
        no files (a manifest read must never break the audit log it feeds)."""
        import subprocess
        try:
            out = subprocess.run(
                ["git", "-C", self._repo_root, "show", "--name-only", "--format=", sha],
                check=True, capture_output=True, text=True).stdout
        except Exception:
            return []
        return [ln.strip() for ln in out.splitlines() if ln.strip()]

    SELF_APPLY_PREFIX = "[self-apply]"
    SELF_BUILD_PREFIX = "[self-build]"
    CHECKPOINT_PREFIX = "[checkpoint]"
    # The reversible autonomous-change STREAMS (label · subject-prefix). ALL are git-committed by
    # `_git_self_commit` — `[self-apply]` for the self-mod streams (panels/extensions/nodes),
    # `[self-build]` for the decision→implementation wire's accepted-build checkpoint, and
    # `[checkpoint]` for an OPERATOR-initiated restore point (`checkpoint()`) — and ALL undo through the
    # ONE prefix-agnostic `revert_self_change(sha)`. The audit ledger reads them ALL so every reversible
    # autonomous change is visible AND one-click revertible from one place. This tuple is the SINGLE
    # SOURCE for the family: `_change_stream`, `_is_revert_subject`, AND the `_self_change_records`
    # `--grep` net all derive from it (so adding a stream here can't silently drop its commits from the
    # ledger — a fail-loud/one-source obligation, AGENTS.md rules 3+4). (Was: self-apply + self-build
    # ONLY — and before that self-apply ONLY, with a self-build revertible-by-sha but INVISIBLE to the
    # ledger; the operator had no single list of what's reversible, and no way to stamp their own.)
    _SELF_CHANGE_STREAMS = (("self-apply", SELF_APPLY_PREFIX), ("self-build", SELF_BUILD_PREFIX),
                            ("checkpoint", CHECKPOINT_PREFIX))

    @staticmethod
    def _change_stream(subject: str) -> str | None:
        """Which reversible STREAM a commit belongs to — `'self-apply'` | `'self-build'` |
        `'checkpoint'` — by SUBJECT prefix, for BOTH a genuine change (`<prefix> …`) and a revert of one
        (`Revert "<prefix> …`). `None` if the subject is none of them: a plain commit whose BODY merely
        MENTIONS a prefix is NOT a self-change and must not pollute the ledger (it would make
        `last_self_change` point at a non-self-change commit). This is the single classifier the audit
        reader keys on — classify by SUBJECT, never by the `--grep`-matched body. Iterates
        `_SELF_CHANGE_STREAMS` (the one source), so a new stream needs no edit here."""
        s = subject or ""
        for label, prefix in Suite._SELF_CHANGE_STREAMS:
            if s.startswith(prefix) or s.startswith(f'Revert "{prefix}'):
                return label
        return None

    def _self_change_records(self, limit: int = 50) -> list[dict]:
        """The shared reader behind the audit log + last_self_change (Finding #1/#2/#4). Reads the
        reversible-change commits of BOTH streams (`[self-apply]` self-mod AND `[self-build]` wire
        builds) newest-first and tags each: {sha, subject, ts (committer ISO date), stream
        ('self-apply'|'self-build'), is_revert (Finding #2), changed_files (Finding #4)}. Reverts are
        INCLUDED but MARKED — the log shows the full undo history; `last_self_change` filters them out.
        Empty list on any git failure (a read, not a mutation — degrade to empty, never raise here).

        CLASSIFY BY SUBJECT, not by message body: `--grep` matches the whole message (subject AND
        body), but a genuine self-change is SUBJECT-prefixed (`[self-apply]`/`[self-build]` — exactly
        what `_git_self_commit` writes), and a revert is subject `Revert "<prefix> ...`. A plain commit
        whose BODY merely MENTIONS a prefix (e.g. a feature/doc commit describing self-change work) is
        NOT a self-change and must NOT pollute the ledger — it would make `last_self_change` point at a
        non-self-change commit. So the two `--grep`s (OR'd by git) stay the cheap coarse net (they never
        drop a genuine or a revert — both contain a prefix), and we KEEP a record only if `_change_stream`
        classes its SUBJECT into a stream; everything else (body-only mention) is dropped. To request more
        than `limit` genuine records, the coarse net is widened (×4 + 20) before the subject filter, so
        body-mentions interleaved in history don't starve the requested count."""
        import subprocess
        n = max(1, int(limit))
        # The coarse `--grep` net is DERIVED from `_SELF_CHANGE_STREAMS` (the one source) — one
        # `--grep=<prefix>` per stream — so a stream added to that tuple is matched here too and its
        # commits can never be silently dropped from the ledger (the failure mode if this stayed a
        # hardcoded two-prefix literal; AGENTS.md rules 3+4). `--fixed-strings` keeps the bracketed
        # prefixes literal; the subject-classifier (`_change_stream`) below is the precise filter.
        grep_net = [arg for _, prefix in self._SELF_CHANGE_STREAMS for arg in ("--grep", prefix)]
        try:
            out = subprocess.run(
                ["git", "-C", self._repo_root, "log", *grep_net, "--fixed-strings",
                 "-n", str(n * 4 + 20), "--format=%H%x00%cI%x00%s"],
                check=True, capture_output=True, text=True).stdout.strip()
        except Exception:
            return []
        records = []
        for line in out.splitlines():
            if not line:
                continue
            sha, _, rest = line.partition("\x00")
            ts, _, subject = rest.partition("\x00")
            stream = self._change_stream(subject)   # 'self-apply' | 'self-build' | 'checkpoint' | None
            if stream is None:                      # body-only mention → NOT a self-change, drop it
                continue
            records.append({
                "sha": sha, "subject": subject, "ts": ts,
                "stream": stream,                   # which reversible stream this change belongs to
                "is_revert": self._is_revert_subject(subject),
                "changed_files": self._self_change_changed_files(sha),
            })
            if len(records) >= n:
                break
        return records

    def self_change_log(self, limit: int = 50) -> list[dict]:
        """The multi-entry self-modification audit ledger (Finding #1): the reversible-change commit
        history newest-first across BOTH streams — `[self-apply]` self-mod AND `[self-build]` wire
        builds — each entry carrying sha · subject · timestamp · stream ('self-apply'|'self-build') ·
        changed_files (Finding #4) · is_revert (Finding #2 — a revert is surfaced DISTINCTLY, not hidden
        and not mistaken for a change). Reachable through a real face (`GET /api/self-change-log`). Was:
        only the single latest (`last_self_change`) existed — then the ledger, but `[self-apply]` ONLY
        (a `[self-build]` was revertible-by-sha yet invisible here); now every reversible autonomous
        change is listed AND one-click revertible from the one place."""
        return self._self_change_records(limit)

    @staticmethod
    def _reverted_target_sha(body: str) -> str | None:
        """The ORIGINAL commit a revert undid — `git revert --no-edit` writes `This reverts commit
        <40-hex-sha>.` in the commit BODY. So the revert names its target unambiguously by full sha
        (subject-matching would be fragile — two changes can share a subject). Returns the full sha, or
        None if the body has no such line. Read from the body, NOT the line-split %s parser of
        _self_change_records (which would corrupt on a multi-line body)."""
        import re
        m = re.search(r"This reverts commit ([0-9a-f]{40})", body or "")
        return m.group(1) if m else None

    def _reverted_shas(self, records: list) -> set:
        """The set of ORIGINAL-change shas that a revert (in `records`) has UNDONE — so a change that
        no longer STANDS (it was reverted) can be skipped. For each revert record, read its body once
        (`git show -s --format=%b`, surgical — NOT through the shared %s parser) and extract the target
        sha. D9: 'still-standing' means not only 'not itself a revert' but also 'not the target of a
        later revert'. Tolerant: an unreadable body contributes no sha (degrade, never raise in a read).
        Minimal-correct: we do NOT model revert-of-revert restoration (a once-reverted change stays
        skipped) — only build that if a test demands it (no gold-plating)."""
        import subprocess
        out = set()
        for rec in records:
            if not rec.get("is_revert"):
                continue
            try:
                body = subprocess.run(
                    ["git", "-C", self._repo_root, "show", "-s", "--format=%b", rec["sha"]],
                    check=True, capture_output=True, text=True).stdout
            except Exception:
                continue
            tgt = self._reverted_target_sha(body)
            if tgt:
                out.add(tgt)
        return out

    def last_self_change(self) -> dict | None:
        """The most recent STILL-STANDING autonomous CHANGE of EITHER reversible stream — a
        `[self-apply]` self-mod OR a `[self-build]` wire build (the record carries `stream`) — for
        one-click rollback + audit. D9: a change still STANDS only if (a) it is not itself a revert
        (Finding #2 — a `git revert` of a self-change still matches the coarse `--grep`, so the naive
        `-1` returned the revert itself, and the UI offered to 'revert the revert'), AND (b) it has not
        since been UNDONE by a later revert. Without (b), `last_self_change` would still point at a change the operator already
        reverted — offering to roll back something that no longer exists in the working tree. So we read
        the tagged log, compute the set of shas reverted by any revert in it, and return the newest
        record that is neither a revert NOR in that reverted set. Keeps the {sha, subject} keys callers/
        the bridge read; ts + changed_files are additive."""
        records = self._self_change_records(50)
        reverted = self._reverted_shas(records)
        for rec in records:
            if not rec["is_revert"] and rec["sha"] not in reverted:
                return rec
        return None

    def checkpoint(self, paths: list, label: str = "") -> dict:
        """OPERATOR-only: mint a REVERSIBLE restore point of named paths — the operator-initiated third
        reversible autonomous-change stream (`[checkpoint]`), beside `[self-apply]` (self-mod) and
        `[self-build]` (the wire's accepted builds). The operator stamps "checkpoint THESE files so I
        can experiment, and revert if it goes wrong." It then shows in the SAME audit ledger
        (`self_change_log`/`last_self_change`, stream-tagged `checkpoint`) and undoes through the SAME
        prefix-agnostic `revert_self_change(sha)`. No parallel git path, no parallel ledger, no new
        revert route — a thin reuse of `_git_self_commit` with the `[checkpoint]` prefix.

        PATH-SCOPED ON PURPOSE (AGENTS.md rule 10 — Tim runs MULTIPLE sessions on `main`): it commits
        EXACTLY the named paths via `_git_self_commit` (pathspec `commit -- <paths>`), so a CONCURRENT
        session's unstaged in-flight work is NEVER swept into the checkpoint — and therefore a `git
        revert` of the checkpoint can never destroy another session's work. Blanket-committing the dirty
        tree would be a footgun, not a reversible thing; so an unnamed/whole-tree checkpoint is REFUSED.

        FAIL LOUD (rule 4), three guards: (a) an empty / non-list / blank-entry `paths` is refused
        (no whole-tree checkpoint); (b) a path that escapes the repo root (`..` / an absolute path
        outside) is refused (rule 8 — a wrong scope is a wrong checkpoint); (c) an EMPTY delta (none of
        the named paths has changes → nothing to commit → `_git_self_commit` returns None) RAISES — a
        checkpoint that commits nothing is not a restore point (mirrors `_commit_or_rollback`'s
        fail-loud). Returns {sha, subject, stream, paths}. Operator-only by design: like
        `revert_self_change`, it is OFF the MCP/agent face and NOT in `RHM_VERBS` (the RHM proposes /
        surfaces, it never commits of its own authority) — reachable only through `POST /api/checkpoint`
        on the operator face."""
        if not isinstance(paths, (list, tuple)) or not paths:
            raise ValueError(
                "checkpoint: name the paths to checkpoint — a whole-tree checkpoint is refused "
                "(AGENTS.md rule 10: parallel sessions on main; a blanket commit would sweep in — and a "
                "revert would then destroy — another session's in-flight work).")
        root = os.path.realpath(self._repo_root)
        rel_paths = []
        for p in paths:
            if not isinstance(p, str) or not p.strip():
                raise ValueError("checkpoint: each path must be a non-empty string.")
            ap = os.path.realpath(os.path.join(root, p))
            if ap != root and not ap.startswith(root + os.sep):
                raise ValueError(
                    f"checkpoint: path {p!r} escapes the repo root — refused (rule 8: a wrong scope is "
                    "a wrong checkpoint).")
            rel_paths.append(os.path.relpath(ap, root))
        msg = label.strip() or f"operator checkpoint of {len(rel_paths)} path(s)"
        sha = self._git_self_commit(rel_paths, msg, prefix=self.CHECKPOINT_PREFIX)
        if not sha:
            raise RuntimeError(
                "checkpoint: nothing to commit for the named paths (no changes there) — a checkpoint "
                "that commits nothing is not a restore point. Name paths that have pending changes, or "
                "there is nothing to make reversible. (fail loud — AGENTS.md rule 4.)")
        # Visibility (S2): a self-change shows at the workshop self-changes surface, on the live stream.
        # Lenient `_emit` (telemetry) — the durable record IS the git commit, already written above; the
        # event is narration, so a store hiccup must never undo a committed (and now reversible) change.
        self._emit("checkpoint", f"operator checkpoint · {msg} · {sha[:8]}",
                   commit=sha, paths=rel_paths, address="ui://chrome/workshop")
        return {"sha": sha, "subject": f"{self.CHECKPOINT_PREFIX} {msg}",
                "stream": "checkpoint", "paths": rel_paths}

    def revert_self_change(self, sha: str) -> dict:
        """RECOVERY: roll back a self-applied change via git (itself reversible). OPERATOR-only.
        Re-discovers so the capability change reflects immediately. The property that makes
        self-modification acceptable — a bad self-edit is bounded, never bricking.

        Finding #3 — CONFLICT-AWARE: reverting a NON-TIP commit can conflict (e.g. a later commit
        touched the same file). The old `check=True` raised mid-revert, leaving the repo in a dirty,
        half-reverted state. Now: run the revert WITHOUT check, and on a non-zero exit (conflict or
        other failure) `git revert --abort` to leave the repo CLEAN, then raise a LEGIBLE fail-loud
        error naming the sha — never a silent swallow, never a repo left mid-revert."""
        import subprocess
        proc = subprocess.run(["git", "-C", self._repo_root, "revert", "--no-edit", sha],
                              capture_output=True, text=True)
        if proc.returncode != 0:
            # leave the repo CLEAN — abort the half-applied revert (best-effort; a fresh repo with
            # nothing to abort just no-ops). Then fail loud with a legible reason (no silent swallow).
            subprocess.run(["git", "-C", self._repo_root, "revert", "--abort"],
                           capture_output=True, text=True)
            detail = (proc.stderr.strip() or proc.stdout.strip())[:400]
            raise RuntimeError(
                f"revert of self-change {sha[:8]} FAILED (likely a conflict — a later commit touched "
                f"the same files, so this non-tip revert cannot apply cleanly). Aborted the revert; the "
                f"repo is left CLEAN at its prior HEAD (no mid-revert state). git said: {detail}")
        self.registry.rediscover([self.nodes_dir])          # rebuild from FS so a removed file un-registers
        head = subprocess.run(["git", "-C", self._repo_root, "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
        self._emit("revert", f"rolled back self-change {sha[:8]}", reverted=sha, commit=head,
                   address="ui://chrome/workshop")   # S2: a revert shows at the workshop self-changes surface
        self.refresh_map()
        return {"reverted": sha, "head": head}

    # --- L5: self-change LOCATING (§21.7#5) — "what changed HERE?" -------------------------------
    # ADDITIVE on top of the existing audit log: filter `self_change_log` by the ADDRESS the operator
    # is at, then revert from there. The address→code join is S3's `resolve_scope` (corpus-side) — L5
    # does NOT duplicate it and does NOT modify the log/revert methods (they stay byte-for-byte). The
    # join is: address --resolve_scope--> scope[] (repo-relative files) ∩ each record's `changed_files`.
    # FRESHNESS COUPLING (seams-engine risk #4): resolve_scope reads the REGENERATED code-symbols.json —
    # a stale corpus returns a stale scope, hence a stale change list. We PROPAGATE `stale`/`note` from
    # resolve_scope straight through (fail-loud-legible, rule 4) rather than collapsing to a silent empty
    # that would falsely read "nothing changed here."

    def self_changes_at(self, ui_addr: str, limit: int = 50) -> dict:
        """"What did the system change HERE?" — the self-change audit log FILTERED to the code scope
        the address resolves to (S3). Returns:
          {address, scope:[file,…], stale, note, changes:[ <self_change_log record> + matched_files ]}

        THE JOIN (no new revert path, no duplicated resolver):
          1. `resolve_scope(ui_addr)` (S3) → the address's `code://` symbol(s) → repo-relative `scope[]`.
          2. Keep each `self_change_log` record whose `changed_files` INTERSECT that scope; annotate the
             record with `matched_files` (the subset that touched here — the operator sees WHY it matched).

        STALE TRICHOTOMY (rule 4 — fail loud, never a silent-success lie):
          • scope resolves        → filter; an empty `changes` is a legitimate "no self-changes here."
          • scope empty, NOT stale (orphan / CSS-selector / DENY-ALL address) → `changes:[]` WITH `note`
                                     ("this element maps to no code") — surfaced, not fabricated.
          • corpus unreadable     → `stale:True` PROPAGATED WITH `note` ("regenerate the corpus") AND
                                     `changes:[]` — NEVER pretended-live. A stale corpus that read
                                     "nothing changed here" would be a silent failure (rule 4); the
                                     surface MUST distinguish "stale" from "nothing here."

        The address MUST conform to the canonical grammar (S0) — resolve_scope raises on a malformed
        ui:// (fail loud). The audit log itself is unchanged (this calls `self_change_log`, never edits
        it); a git failure there degrades to `[]` as documented."""
        scoped = self.resolve_scope(ui_addr)                 # S3 — reused, never duplicated (rule 3)
        scope = set(scoped.get("scope") or [])
        out = {
            "address": ui_addr,
            "scope": scoped.get("scope") or [],
            "stale": bool(scoped.get("stale")),
            "note": scoped.get("note") or "",
            "changes": [],
        }
        # stale OR empty scope ⇒ no scope to filter against → DENY-ALL change list, but the REASON is
        # carried (stale vs orphan) via `stale`/`note` so the surface never reads a lie. (Matches the
        # surface_build_intent empty-scope=deny posture — an unmapped/stale address is never a license.)
        if scoped.get("stale") or not scope:
            if not out["note"]:
                out["note"] = (f"{ui_addr!r} maps to no code scope — no self-change can be located here "
                               f"(DENY-ALL; never fabricated — rule 8)")
            return out
        for rec in self.self_change_log(limit):              # the EXISTING ledger, unchanged
            touched = sorted(scope.intersection(rec.get("changed_files") or []))
            if touched:
                out["changes"].append(dict(rec, matched_files=touched))
        return out

    def revert_self_change_at(self, ui_addr: str, sha: str) -> dict:
        """Revert a self-change FROM the address you're at (§21.7#5). The file→ui→sha chain resolves
        through `self_changes_at` (the address-filtered list), then this composes the EXISTING
        `revert_self_change(sha)` — the SAME operator-only rollback (the `/api/revert` gate is the one
        that guards it; this adds NO new revert path and does NOT weaken the gate).

        WIRING NOTE (so the next agent isn't misled): this is a TESTED backend primitive that is
        deliberately NOT on a face — adding a `/api/revert-at` route would be the "new revert path" the
        L5 spec forbids. The LIVE operator drive path is FE `revertSelfChangeAt` → `api.revert(sha)` →
        POST `/api/revert` → `revert_self_change(sha)` (the existing operator-only gate), and per-address
        SCOPING on that path is UI-level (only the address-filtered rows are clickable). This method's
        server-side scoped-refusal is the additional belt the loop can wire to a face later if desired;
        for now it documents + proves the composition without weakening or duplicating the live gate.

        SCOPED + FAIL LOUD: you may only revert a change that actually touched THIS element. A `sha`
        absent from the address's filtered list RAISES (never silently revert something that didn't
        change here, never silently no-op) — rule 4. The leaf is the unchanged `revert_self_change`."""
        located = self.self_changes_at(ui_addr)
        if located.get("stale"):
            raise ValueError(
                f"cannot locate self-changes at {ui_addr!r}: the corpus join is STALE "
                f"({located.get('note')}) — regenerate design/_system before reverting from an address.")
        shas = {c["sha"] for c in located["changes"]}
        if sha not in shas:
            raise KeyError(
                f"self-change {sha!r} did not change anything at {ui_addr!r} "
                f"(scope {located['scope']}); refusing to revert it from here — you can only revert "
                f"what changed at this element (the address-located changes are {sorted(shas)}).")
        return self.revert_self_change(sha)                  # the EXISTING operator-only rollback, reused

    # --- UI extension point (slice 14): brain-authored DECLARATIVE panels added through the UI ---
    # Bounded by construction: the brain authors a panel DEFINITION (a generic renderer displays it),
    # NOT arbitrary interface code. Additive + git-reversible. Fields edit only real config.
    PANEL_TARGETS = ("mode", "model", "persona")
    PANEL_FIELD_TYPES = ("select", "text")

    def _registered_options(self, target: str) -> list:
        """The authoritative options for a registered target — from the registry, never invented."""
        if target == "mode":
            return list(self.MODES)
        if target == "model":
            return self.available_models()
        return []                                            # persona = free text

    def list_panels(self) -> list:
        import json as _j
        if not os.path.isdir(self.panels_dir):
            return []
        out = []
        for fn in sorted(os.listdir(self.panels_dir)):
            if fn.endswith(".json"):
                try:
                    out.append(_j.loads(open(os.path.join(self.panels_dir, fn), encoding="utf-8").read()))
                except Exception as e:
                    # a malformed file doesn't break the list — but SURFACE it, never drop silently (F6)
                    self._emit("warning", f"panel file {fn} is malformed and was skipped: {e}")
        return out

    def propose_panel(self, name: str, spec: str, model: str | None = None) -> dict:
        """The brain AUTHORS a declarative panel definition (it chooses the fields + wiring), surfaced
        as a ui_panel CONFIRM. NOT arbitrary code — a definition a generic renderer displays."""
        name = self._slug(name)
        self._safe_node_name(name)
        import json as _j
        from fabric import client, transport, config as fcfg
        sys_p = ('You author ONE declarative UI panel definition for the operator interface. Output ONLY '
                 'JSON, no prose. Shape: {"title": str, "fields": [{"key": str, "label": str, '
                 '"type": "select"|"text", "target": "mode"|"model"|"persona", "options": [str] (select only)}]}. '
                 'Each field\'s target is the REAL config it edits: mode (presence mode), model (the RHM model), '
                 'persona (the RHM voice). Choose the fields that fit the request.')
        cap = self.capabilities()
        user = (f"Panel name: {name}. Request: {spec}.\nUse ONLY these REGISTERED values — do not invent any:\n"
                f"- modes (for target 'mode'): {cap['modes']}\n"
                f"- models (for target 'model'): {cap['models']}\n"
                "For select fields you may omit 'options' — the system fills them from the registry.")
        raw = client.complete(transport.openai_transport(base_url=fcfg.DEFAULT_BASE_URL, timeout=fcfg.DEFAULT_CLOUD_TIMEOUT),
                              [{"role": "system", "content": sys_p + "\n\n" + self._authoring_preamble()},
                               {"role": "user", "content": user}],
                              model=model or fcfg.DEFAULT_BRAIN)
        need = self._needs(raw)
        if need:
            return {"needs": need, "id": self._ask_operator(need, f"while building panel '{name}': {spec}")}
        try:
            deftn = _j.loads(_strip_fences(raw))
        except Exception as e:
            # don't surface a success-shaped empty panel (F6) — ASK, the model didn't produce a valid def
            q = f"the '{name}' panel definition didn't parse as JSON ({e}); the model output was malformed"
            return {"needs": q, "id": self._ask_operator(q, f"panel '{name}': {spec}")}
        sid = self.inbox.surface("ui_panel", {"name": name, "panel": deftn}, default="reject")
        self._emit("grow", f"brain authored a '{name}' UI panel — surfaced for approval",
                   node_name=name, surfaced=sid,
                   address="ui://chrome/inbox")   # S2: a proposed panel surfaces for approval in the inbox
        return {"id": sid, "name": name, "panel": deftn}

    def apply_panel(self, surfaced_id: str) -> str:
        """Apply a proposed panel — only if OPERATOR-approved. VALIDATES the def to declarative
        fields with allowed types/targets (never arbitrary code), writes panels/<name>.json
        additively + git-commits (reversible)."""
        d = self.inbox.get(surfaced_id)
        if not d:
            raise KeyError(f"no surfaced decision {surfaced_id!r}")
        def _do():                                           # the consequential body — runs ONLY if approved
            name = self._safe_node_name(d["payload"]["name"])
            deftn = d["payload"]["panel"]
            fields, dropped = [], []
            for f in (deftn.get("fields") or []):
                if f.get("type") in self.PANEL_FIELD_TYPES and f.get("target") in self.PANEL_TARGETS:
                    # registered-target options come from the REGISTRY (authoritative) — never the brain's
                    # guess. So a 'model' picker always lists the REAL models, not invented names.
                    reg_opts = self._registered_options(f["target"])
                    opts = reg_opts if (f["type"] == "select" and reg_opts) \
                        else ([str(o) for o in f.get("options", [])] if f["type"] == "select" else [])
                    fields.append({"key": str(f.get("key", f.get("target"))), "label": str(f.get("label", "")),
                                   "type": f["type"], "target": f["target"], "options": opts})
                else:
                    dropped.append(f"{f.get('key', '?')}({f.get('type')}/{f.get('target')})")
            if dropped:                                      # surface dropped fields, never silent (F6)
                self._emit("warning", f"panel '{name}': dropped {len(dropped)} field(s) with unsupported "
                           f"type/target: {', '.join(dropped)}")
            clean = {"id": name, "title": str(deftn.get("title", name)), "fields": fields}
            import json as _j
            os.makedirs(self.panels_dir, exist_ok=True)
            path = os.path.join(self.panels_dir, name + ".json")
            tmp = path + ".tmp"
            open(tmp, "w", encoding="utf-8").write(_j.dumps(clean, indent=2))
            os.replace(tmp, path)
            sha = self._commit_or_rollback(path, f"add UI panel '{name}'")
            self._emit("apply", f"approved + applied '{name}' UI panel · {sha[:8]}", node_name=name, commit=sha,
                       address="ui://chrome/workshop")   # S2: a self-change shows at the workshop self-changes surface
            self.refresh_map()
            return path
        # G1: ui_panel → CONFIRM (now explicit in POLICY) → runs only if operator-approved. inbox=None
        # → the blocked path raises GovernanceError without re-surfacing (item already exists).
        return guard("ui_panel", do=_do, confirmed=self.inbox.is_approved(surfaced_id))

    def apply_surfaced(self, surfaced_id: str) -> dict:
        """Dispatch apply by the decision's class — ui_panel → panel, ui_extension → code-gated
        extension, else code_build → node-type."""
        d = self.inbox.get(surfaced_id)
        if not d:
            raise KeyError(f"no surfaced decision {surfaced_id!r}")
        if d.get("action") == "ui_panel":
            return {"applied": self.apply_panel(surfaced_id), "kind": "ui_panel"}
        if d.get("action") == "ui_extension":
            r = self.apply_extension(surfaced_id)
            r["kind"] = "ui_extension"
            return r
        # AUTHORING (C7.4): a role is a roles/<id>.py file — route to apply_role, NEVER the generic
        # apply_node (which would mis-write it to nodes/). The distinct action class is the router.
        if d.get("action") == "role_build":
            return {"applied": self.apply_role(surfaced_id), "kind": "role_build"}
        if d.get("action") == "role_delete":
            r = self.apply_role_delete(surfaced_id)
            return {"applied": r.get("removed"), "kind": "role_delete", "commit": r.get("commit")}
        return {"applied": self.apply_node(surfaced_id), "kind": "code_build"}

    # --- the self-coding subsystem (slice 15): arbitrary brain-authored extensions, BUILD-GATED ---
    # The object of safety is the LOOP, not the code: a broken change is caught by the build-gate
    # and NEVER goes live; runtime throws are contained by the error boundary; every promote is a
    # git commit (revert recovers). Operator-only. Reliability of the code is the MODEL's.
    def propose_extension(self, name: str, spec: str, model: str | None = None) -> dict:
        """The brain authors a real .tsx React component (arbitrary UI), surfaced as ui_extension
        CONFIRM (operator-only). Constrained: import only from 'react' (so the build-gate can keep
        unresolved-module breaks out); may call fetch('/api/...')."""
        name = self._slug(name)
        self._safe_node_name(name)
        from fabric import client, transport, config as fcfg
        sys_p = ("You write ONE React component (TSX) that extends the operator interface. Output ONLY the "
                 "code — no prose, no markdown fences. Contract: `export default function " + name +
                 "() { ... }`. You MAY `import { useState, useEffect } from 'react'` — but import from NO "
                 "other module. You MAY call fetch('/api/...') against the bridge to read or act on the "
                 "system.\n\n" + self._authoring_preamble())
        code = _strip_fences(client.complete(
            transport.openai_transport(base_url=fcfg.DEFAULT_BASE_URL, timeout=fcfg.DEFAULT_CLOUD_TIMEOUT),
            [{"role": "system", "content": sys_p}, {"role": "user", "content": f"Build: {spec}"}],
            model=model or fcfg.DEFAULT_BRAIN))
        need = self._needs(code)
        if need:                                              # asked instead of fabricating
            return {"needs": need, "id": self._ask_operator(need, f"while building extension '{name}': {spec}")}
        sid = self.inbox.surface("ui_extension", {"name": name, "code": code}, default="reject")
        self._emit("grow", f"brain authored a '{name}' UI extension — surfaced for approval",
                   node_name=name, surfaced=sid,
                   address="ui://chrome/inbox")   # S2: a proposed extension surfaces for approval in the inbox
        return {"id": sid, "name": name, "code": code}

    def _gate_extension(self, code: str) -> str | None:
        """Build-gate: returns an error string if the candidate would break the build or do something
        forbidden, else None. AST-checked via canvas/app/syntax-gate.cjs (red-team B1): syntax +
        import-allowlist (react only) + no dynamic import() + no require() + no external-URL literals.
        Runs on a TEMP file OUTSIDE the live tree."""
        import subprocess
        import tempfile
        appdir = os.path.join(self._repo_root, "canvas", "app")
        fd, tmp = tempfile.mkstemp(suffix=".tsx")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(code)
            r = subprocess.run(["node", "syntax-gate.cjs", tmp], cwd=appdir,
                               capture_output=True, text=True, timeout=60)
            if r.returncode != 0:
                return "build-gate rejected: " + (r.stderr.strip() or r.stdout.strip())[:400]
        finally:
            os.unlink(tmp)
        return None

    def apply_extension(self, surfaced_id: str) -> dict:
        """Operator-approved. Build-GATE the candidate OUTSIDE the live tree; promote into
        src/extensions/ + git-commit ONLY on pass. A failed gate NEVER writes to the live tree."""
        d = self.inbox.get(surfaced_id)
        if not d:
            raise KeyError(f"no surfaced decision {surfaced_id!r}")
        def _do():                                            # the consequential body — runs ONLY if approved
            name = self._safe_node_name(d["payload"]["name"])
            code = d["payload"]["code"]
            err = self._gate_extension(code)                  # gate runs on a temp file, NOT in src
            if err:
                self._emit("reject", f"extension '{name}' REJECTED by build-gate (never went live)", node_name=name,
                           address="ui://chrome/workshop")   # S2: a self-mod outcome shows at the workshop surface
                return {"applied": None, "rejected": True, "error": err}
            extdir = os.path.join(self._repo_root, "canvas", "app", "src", "extensions")
            os.makedirs(extdir, exist_ok=True)
            path = os.path.join(extdir, name + ".tsx")
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(code if code.endswith("\n") else code + "\n")
            os.replace(tmp, path)                             # promote (gate passed) — now Vite loads it
            sha = self._commit_or_rollback(path, f"add extension '{name}'")   # fail loud if not git-revertible
            self._emit("apply", f"approved + applied '{name}' extension (gate passed) · {sha[:8]}",
                       node_name=name, commit=sha,
                       address="ui://chrome/workshop")   # S2: a self-change shows at the workshop self-changes surface
            self.refresh_map()
            return {"applied": path, "rejected": False, "commit": sha}
        # G1: ui_extension → CONFIRM (now explicit in POLICY) → runs only if operator-approved. inbox=None
        # → the blocked path raises GovernanceError without re-surfacing (item already exists).
        return guard("ui_extension", do=_do, confirmed=self.inbox.is_approved(surfaced_id))

    # --- surfaced-decision inbox (D4/D7) ---
    def list_surfaced(self) -> list:
        return self.inbox.list()

    # the operator's response vocabulary (D): approve/reject/decide RESOLVE; comment annotates without
    # resolving; skip defers — back to the inbox, NOT resolved (a skipped item still needs Tim).
    RESOLVING_VERBS = ("approve", "reject", "decide")

    def resolve_surfaced(self, sid: str, choice: str, reason: str = "",
                         session_id: str | None = None, position: int | None = None) -> dict:
        """OPERATOR-only (UI channel) — NOT exposed on the MCP face, so the agent can't self-approve.
        Captures the WHY (the generalising signal, I1) and — additively (D) — the session id + position
        the response came from, plus the comment/skip/decide vocabulary:
          • approve/reject/decide → RESOLVE (writes `resolved`; status → resolved).
          • comment → annotate only (records the reason; status → responded; NOT resolved).
          • skip → defer (status back to 'inbox'; NOT resolved — a skipped item still needs Tim).
        Returns the verbose verdict. Existing two-arg callers are unchanged (the new args default)."""
        d = self.inbox.get(sid)
        if not d:
            raise KeyError(f"no surfaced decision {sid!r}")
        # session-position tagging (record on the surfaced item + the resolve event for audit/replay).
        # T1-RACE: re-read under the surfaced lock and mutate the fresh copy so a concurrent set_status
        # write can't lose-update the session tag (and the tag can't clobber a status advance).
        if session_id is not None:
            with self.store.surfaced_lock():
                d = self.inbox.get(sid) or d
                d.setdefault("session_id", session_id)
                if position is not None:
                    d["position"] = position
                self.store.save_surfaced(d)

        if choice == "skip":
            self.inbox.set_status(sid, "inbox")            # defer — still a live escalation; NOT resolved
            self._emit("review.skip", f"operator skipped {sid}" + (f" — {reason}" if reason else ""),
                       surfaced=sid, choice="skip", reason=reason, session=session_id, position=position,
                       address=self._registry_ui_target(d.get("payload") or {}))   # S2: the item's locus (node or inbox)
            return {"id": sid, "choice": "skip", "status": "inbox", "resolved": False}
        if choice == "comment":
            if reason:                                     # annotate the WHY without resolving
                d["reason"] = reason
                self.store.save_surfaced(d)
            self.inbox.set_status(sid, "responded")
            self._emit("review.comment", f"operator commented on {sid}" + (f" — {reason}" if reason else ""),
                       surfaced=sid, choice="comment", reason=reason, session=session_id, position=position,
                       address=self._registry_ui_target(d.get("payload") or {}))   # S2: the item's locus (node or inbox)
            return {"id": sid, "choice": "comment", "status": "responded", "resolved": False}

        # approve / reject / decide (or any other verb) → RESOLVE (TERMINAL). resolve() writes `resolved` +
        # reason; mark the lifecycle status resolved (additive) and emit the resolve event (seq·surfaced·
        # choice·reason — the verdict E reads, suite.py resolve event).
        #
        # IDEMPOTENT-PER-ITEM (integrity, fail-loud): a recorded decision CANNOT be contradicted. Once an
        # item has a TERMINAL verdict (resolved == approve|reject|decide), a SECOND terminal resolve REFUSES
        # — else one item could be both committed-as-approved AND requeued-as-rejected (the three-part bind
        # is per-verdict-seq, so it can't catch the contradiction). skip→inbox and comment→responded never
        # write `resolved`, so they stay non-terminal + re-presentable; only these three are terminal.
        prior = d.get("resolved")
        if prior in self.RESOLVING_VERBS:
            raise GovernanceError(
                f"surfaced {sid!r} already has a terminal verdict ({prior!r}) — a recorded decision "
                f"cannot be contradicted; refusing the second {choice!r} (one item → one final verdict). "
                f"Re-open it with skip/comment first if it genuinely needs revisiting.")
        self.inbox.resolve(sid, choice, reason)
        try:
            self.inbox.set_status(sid, "resolved")
        except KeyError:
            pass
        self._emit("resolve", f"operator {choice}d {sid}" + (f" — {reason}" if reason else ""),
                   surfaced=sid, choice=choice, reason=reason, session=session_id, position=position,
                   address=self._registry_ui_target(d.get("payload") or {}))   # S2: the item's locus (node or inbox)
        verdict = {"id": sid, "choice": choice, "status": "resolved", "resolved": True}

        # ── L2 · the resolve→dispatch PRODUCTION TRIGGER (INERT BY DEFAULT — 🔒 built-not-armed) ──
        # This is the seam where the LIVE loop used to STOP: resolve_surfaced wrote the verdict but
        # nothing READ it to fire dispatch_decision, and drive_dispatchable (the watcher that does) had
        # NO production caller — only tests. L2 adds the missing trigger: an operator approve of a
        # build-intent, WHEN the live loop is deliberately ARMED, drives the watcher pass — which is the
        # production caller for drive_dispatchable AND the resolve→dispatch link (both collapse into the
        # ONE existing mechanism: the watcher reads the just-written verdict and calls dispatch_decision).
        #
        # SAFE-BY-DEFAULT (the headline L2 property — wire-bridge §3, AGENTS.md rule 4): this fires ONLY
        # when implement.wire_armed() — i.e. COMPANY_WIRE_PERMISSION=acceptEdits, the deliberate opt-in.
        # The DEFAULT posture is "plan": wire_armed() is False → this block is a no-op → resolve_surfaced
        # behaves EXACTLY as before (the system does NOT self-modify; the lead fires the one-shot proof
        # under the deliberate flag). Even if it DID fire under `plan`, a plan-mode `claude -p` is
        # read-only → empty change-delta → the build can never close `implemented` (a second safety layer).
        #
        # NO-BYPASS PRESERVED: this is the OPERATOR face (resolve_surfaced is off the MCP face,
        # server.py:158) — the RHM can never reach it, so dispatch stays operator-authorized only. The
        # GOVERNED PATH IS UNCHANGED: we call drive_dispatchable, which calls dispatch_decision, which
        # still does the full three-part bind + exactly-once decision.dispatch claim under the per-seq
        # lock + the AUTO-posture pre-gate + the guarded close + the DENY-ALL scope-diff + surfaced-for-
        # review. We REUSE it (the watcher also enforces the §W7 concurrency cap + re-surfaces crashed
        # dispatches); we never re-implement or weaken it. A non-AUTO / non-build-intent approve is NOT
        # dispatched (drive_dispatchable._is_dispatchable filters it) — it surfaces for the operator.
        #
        # WIRE-ASYNC — the build EXECUTION is DECOUPLED from this request. The synchronous bug: this
        # block used to call drive_dispatchable INLINE, so the blocking `claude -p` subprocess (up to
        # 900s) ran INSIDE POST /api/resolve — if the approving client connection dropped, the request
        # thread's result-handling was lost and the build orphaned as a 'crashed' dispatch. NOW the
        # operator verdict above is the ONLY thing written synchronously (the consent record is durable
        # immediately); the build is handed to a BACKGROUND daemon thread (_drive_dispatchable_bg) that
        # runs the SAME governed drive_dispatchable → dispatch_decision path (per-seq lock + durable
        # claim + gates + [self-build] commit + guarded close + surface-for-review, all UNCHANGED), and
        # this method RETURNS PROMPTLY with an ack. The build completes + emits its terminal event +
        # commits + surfaces via the SAME event log → the SSE stream delivers the result to the UI
        # INDEPENDENT of this connection. EXACTLY-ONCE is preserved: the decision.dispatch claim is
        # emitted under the locks INSIDE dispatch_decision regardless of which thread runs it, so two
        # concurrent approves of the same seq → two threads → one claim wins, the other is refused.
        from runtime import implement      # local import (mirrors dispatch_decision) — avoid import cycle
        if choice == "approve" and implement.wire_armed() and self.is_build_intent(d):
            try:
                self._drive_dispatchable_bg(sid=sid)
                # the ACK — HONEST (rule 4, no pretending): the bg pass only DISPATCHES a build-intent
                # whose DECLARED class has posture==AUTO (drive_dispatchable._is_dispatchable filters
                # CONFIRM/SURFACE/LOCKED classes OUT — they surface for the operator, never auto-build).
                # So we report THIS sid as dispatched ONLY when it is genuinely auto-dispatchable; a
                # non-AUTO build-intent reports status="surfaced" with an EMPTY dispatched list (it was
                # NOT dispatched — claiming it was would be the exact "pretend success" rule 4 forbids).
                # The authoritative result (implemented / verify / surfaced-for-review) arrives via the
                # SSE event stream, NOT this ack — the ack only says what the bg pass WILL attempt.
                from runtime.governance import posture as _posture, AUTO as _AUTO
                _declared = (d.get("payload") or {}).get("consequence_class", "decision_build")
                if _posture(_declared) == _AUTO:
                    verdict["wire_drive"] = {"dispatched": [sid], "status": "running"}
                else:
                    verdict["wire_drive"] = {"dispatched": [], "status": "surfaced",
                                             "reason": f"declared class {_declared!r} is not AUTO — "
                                                       f"surfaced for the operator, not auto-dispatched"}
            except Exception as e:
                # FAIL LOUD (rule 4): failing to even SPAWN the background dispatch (e.g. thread start)
                # must NOT pretend the approve silently did nothing — surface it on the verdict + a
                # terminal event. The operator's resolve itself already committed (above) — operator-only
                # resolve holds; only the build EXECUTION couldn't start.
                self._emit("decision.verify",
                           f"resolve→dispatch trigger for {sid} could not start: {e}",
                           surfaced=sid, derived_from=None, verify_passed=False,
                           address="ui://chrome/inbox")
                verdict["wire_drive_error"] = str(e)
        return verdict

    # ── X16 · operator-approves-the-reach (the propagation decision) ───────────────────────────
    # A consequential build surfaces its BLAST RADIUS (X14, persisted at mint into payload —
    # surface_intent_at). The OPERATOR authorizes HOW FAR the edit propagates. The build's editable
    # scope IS payload["scope"] (dispatch_decision reads it; the scope-diff close gates on it). So:
    #   • DEFAULT-NARROW: with NO reach-approval, payload["scope"] stays the pointed address's scope —
    #     unchanged from today, never auto-expanded.
    #   • EXPLICIT EXPANSION: approve_reach widens payload["scope"] to the UNION of the original scope
    #     and the files the APPROVED blast-radius members live in. The approved members are recorded
    #     (payload["reach_approved"]) for audit + legibility.
    # Mutating payload["scope"] (not a separate merge-at-dispatch field) means the wire's governed path
    # is REUSED BYTE-FOR-BYTE — dispatch_decision/_in_any_scope are untouched; an EXPANDED scope
    # authorizes the expanded files, a NARROW one does not, by the SAME scope-diff gate. Empty-scope =
    # DENY-ALL is preserved (an orphan address has an empty radius → nothing to expand → scope stays []).
    def _member_to_files(self, member: str) -> list[str]:
        """Resolve a BLAST-RADIUS MEMBER to its repo-relative file(s) — the editable-scope grain.
        Members come in three grammars (the X14 return shape): a `code://` symbol id (structural
        dependents/dependencies, semantic neighbours), a `ui://` address (co-reference), or a feature-id
        (co-reference: ENG-*/NODE-*/WIRE-*). REUSE the existing resolvers, never re-derive:
          • code://<stem>/<symbol> → its `file` field in code-symbols.json (the same registry
            resolve_scope reads; the canonical resolved repo-relative path).
          • ui://…                 → resolve_scope(addr).scope (the SAME S3 forward map).
          • a feature-id (no scheme) → resolves to NO file here (it isn't a code locus) → []; the
            caller treats an all-empty resolution as a no-op for that member (legible, never a silent
            broadening). We NEVER fabricate a file (rule 8 — confabulation is a failure)."""
        import json as _j
        m = (member or "").strip()
        if not m:
            return []
        if m.startswith("code://"):
            symbols_path = os.path.join(self._corpus_dir(), "code-symbols.json")
            try:
                with open(symbols_path, encoding="utf-8") as f:
                    index = _j.load(f).get("symbols", {})
            except (OSError, ValueError):
                return []                              # unreadable index → no file (fail-safe, not fabricated)
            entry = index.get(m) or {}
            f = entry.get("file")
            return [f] if f else []
        if m.startswith("ui://"):
            try:
                return list(self.resolve_scope(m).get("scope") or [])
            except Exception:
                return []                              # malformed/orphan → no file (never fabricated)
        return []                                      # a feature-id (or anything else) maps to no file

    def approve_reach(self, sid: str, members: list[str], reason: str = "") -> dict:
        """X16 — the OPERATOR authorizes HOW FAR a build's edit propagates. Default is the pointed
        address only (payload["scope"] unchanged); this widens it to include the files the APPROVED
        blast-radius members live in. The classic case: a rename whose ripples reach the structural
        dependents — the operator approves expanding the editable scope to that relational cluster.

        OPERATOR-ONLY, OFF the MCP face: this is an operator action (mirrors resolve_surfaced / pin) —
        NOT in RHM_VERBS, so the RHM/MCP face gains no reach-expansion (no-bypass + the 7-verb
        whitelist + no-self-apply preserved).

        THE SAFETY GATE (the load-bearing invariant): each requested member MUST be a member of the
        PERSISTED blast_radius the operator saw at mint (consent-time — NOT a fresh recompute that could
        disagree). A member that is not in that radius RAISES (fail loud) — so approve_reach can only
        RATIFY what the operator actually saw; it is NEVER a scope-injection path that could defeat
        empty-scope=DENY-ALL or smuggle in an arbitrary file. A raw repo path is not a radius member
        either → rejected.

        ORDERING / IDEMPOTENCY: valid ONLY while the item is a live, UNRESOLVED build-intent. After a
        terminal resolve (approve/reject/decide) it RAISES — you cannot widen the reach of a build that
        has already been decided/launched (mirrors resolve_surfaced's idempotent-per-item refusal).

        DEFAULT-NARROW + NEVER-SILENT: only the NAMED members widen the scope; an un-named member is
        never pulled in. The new scope is the UNION of the original declared scope and the approved
        members' files (the original is never dropped). EMPTY-SCOPE=DENY-ALL is preserved: an orphan
        address has an empty radius, so every requested member is rejected and the scope stays []
        (never widened into allow-all).

        ATOMIC: the scope widen is a re-read-then-mutate-fresh-copy under the surfaced_lock (the T1-RACE
        pattern resolve_surfaced uses), so a concurrent set_status / build_result write can't lose-update
        the widened scope, nor it them. Returns the verbose verdict.

        FAIL LOUD on a missing item / non-build-intent / a member not in the radius / a terminal item —
        never a silent no-op (rule 4)."""
        d = self.inbox.get(sid)
        if not d:
            raise KeyError(f"no surfaced decision {sid!r}")
        if not self.is_build_intent(d):
            raise GovernanceError(
                f"approve_reach: {sid!r} is not a build-intent item (payload.intent != 'build') — "
                f"the reach is the editable scope of a BUILD; there is nothing to widen on a "
                f"non-build review item. Refused (fail loud).")
        # ORDERING: a terminal verdict means the build is decided/launched — too late to widen its reach.
        prior = d.get("resolved")
        if prior in self.RESOLVING_VERBS:
            raise GovernanceError(
                f"approve_reach: {sid!r} already has a terminal verdict ({prior!r}) — its reach is "
                f"locked; you cannot widen the editable scope of a decided/launched build. Refused.")
        members = [m for m in (members or []) if isinstance(m, str) and m.strip()]
        if not members:
            raise ValueError(
                "approve_reach needs a non-empty list of blast-radius members to approve — "
                "fail loud, no silent no-op (the default reach is the pointed address; widen explicitly).")
        payload = d.get("payload") or {}
        radius = payload.get("blast_radius") or {}
        # THE SAFETY GATE: build the SET of members the operator actually saw, across all kinds, from the
        # PERSISTED radius (consent-time). A requested member outside it RAISES — no scope injection.
        seen = set(radius.get("co_reference") or [])
        seen |= set(radius.get("structural_dependents") or [])
        seen |= set(radius.get("structural_dependencies") or [])
        seen |= set(radius.get("semantic_neighbours") or [])
        bad = [m for m in members if m not in seen]
        if bad:
            raise GovernanceError(
                f"approve_reach: {bad!r} is/are NOT in the surfaced blast radius of {sid!r} — the reach "
                f"can only RATIFY members the operator actually saw (consent-time, fail loud). Approving "
                f"an un-surfaced member would be a scope-injection path that defeats empty-scope=DENY-ALL; "
                f"refused. (Surfaced members: {sorted(seen) or '∅ — empty radius, nothing to expand'}.)")
        # resolve the approved members → their repo-relative files (REUSE the existing resolvers).
        add_files: set[str] = set()
        for m in members:
            for f in self._member_to_files(m):
                if f:
                    add_files.add(f)
        # ATOMIC widen: re-read the fresh record under the lock, UNION the scope, record the approval.
        with self.store.surfaced_lock():
            d = self.inbox.get(sid) or d
            payload = d.get("payload") or {}
            scope = list(payload.get("scope") or [])
            new_scope = sorted(set(scope) | add_files)
            payload["scope"] = new_scope
            approved = list(payload.get("reach_approved") or [])
            for m in members:                          # record WHAT was approved (legible consent / audit)
                if m not in approved:
                    approved.append(m)
            payload["reach_approved"] = approved
            d["payload"] = payload
            self.store.save_surfaced(d)
        # S2: emit an addressed event so the reach-expansion is visible on the live stream + audit log.
        self._emit("decision.reach",
                   f"operator approved a wider reach for {sid}: +{sorted(add_files) or '∅'} "
                   f"(members {members})" + (f" — {reason}" if reason else ""),
                   surfaced=sid, reach_approved=members, added_scope=sorted(add_files),
                   address="ui://chrome/inbox")        # S2: the build-intent's inbox item
        return {"id": sid, "reach_approved": members, "added_scope": sorted(add_files),
                "scope": new_scope}

    def decision_view(self, sid: str) -> dict:
        """A decision as a VIEW derived from the event log (I2): its full trajectory — proposed →
        framed → resolved (with the why) — reconstructed in order. Auditable + replayable.
        Reads the WHOLE event tail (events_since(-1)) and filters on `surfaced`, mirroring
        session_view: an audit must NOT silently truncate (fail-loud). A long-lived decision whose
        lineage spans more than the old 999-event window is now returned WHOLE, not clipped."""
        d = self.inbox.get(sid)
        evs = sorted((e for e in self.store.events_since(-1) if e.get("surfaced") == sid),
                     key=lambda e: e.get("seq", 0))                # chronological path, not endpoint
        return {"id": sid, "decision": d, "trajectory": evs}

    def session_view(self, session_id: str) -> dict:
        """D: the full trajectory of a review SESSION — every event tagged with this session id, in
        order. Clones decision_view but WIDENS past the 999-event window: reads from the start via
        events_since(-1) (the file-tail) and filters on `session`, so a long walk is never truncated."""
        evs = [e for e in self.store.events_since(-1) if e.get("session") == session_id]
        evs.sort(key=lambda e: e.get("seq", 0))
        g = self.store.load_graph(self._session_graph_id(session_id))
        return {"session": session_id, "trajectory": evs,
                "graph": g.model_dump(mode="json") if g else None}

    def address_view(self, address: str) -> dict:
        """L3 (§21.7#1): everything that happened AT an element's address — its addressed history.

        Clicking an element shows its full trajectory. This is the addressed ANALOGUE of
        `decision_view`: where `decision_view` filters `events_since(-1)` on `e.get("surfaced")==sid`,
        this filters the SAME whole tail on `e.get("address")==address`. It is a SIBLING (mirroring how
        `session_view` clones decision_view but filters on `session`) so `decision_view`'s `sid` path is
        LITERALLY untouched — L3 WIDENS the audit-view machinery to an address key, it does not replace
        the sid one. The store side is free: S2 already stamped the ~20 emit sites, so events carry an
        additive `address` (event_address_acceptance.py); readers `.get()` it, so this is non-breaking.

        S0 GATE FIRST: the QUERY address is validated by `parse_ui_address` (the same canonical-grammar
        gate `annotate`/`annotations_at`/`chats_at` use) and RAISES on a malformed / non-`ui://` string
        (fail-loud, rule 4) — so a junk query never silently returns [] (which a caller could read as 'no
        history'), and the bridge's try/except turns the raise into a 400 for free. SCOPE: `ui://` queries
        only — "clicking an element" is a `ui://` locus (the FE indicate flow fires only for `ui://`); the
        stored events themselves may carry `run://` (a node-instance locus), but a `run://` event simply
        won't equal a `ui://` query, so it is filtered out correctly — nothing to special-case.

        Reads the WHOLE event tail (`events_since(-1)`), like `decision_view`/`session_view`: an audit must
        NOT silently truncate (fail-loud). Returns the matching events in chronological (seq) order."""
        from contracts.ui_info import parse_ui_address
        parse_ui_address(address)                              # S0 grammar gate — raises on malformed / non-ui://
        evs = sorted((e for e in self.store.events_since(-1) if e.get("address") == address),
                     key=lambda e: e.get("seq", 0))            # chronological path, not endpoint
        return {"address": address, "trajectory": evs}

    def ref_versions(self, address: str, limit: int = 25) -> dict:
        """L6 (§21.7#6): the PRIOR VERSIONS of an addressed output — its temporal trail.

        A portal shows the CURRENT ref live (`state()` reads `head(ref)`, the live window). This is the
        OTHER half: every value the address has HELD over time. It reads the store's ref→version-history
        index (`ref_history`, appended on each `set_ref`) — the cas bytes already survive (put_content is
        write-once), so each entry's PRIOR bytes are fetched by its `cas` through `get_content` (no bytes
        are copied; the index only MAPS the ref to its prior cas hashes). Returns NEWEST-FIRST (the FE
        leads with the most recent), each entry carrying a short `preview` of the version's content + an
        `is_current` flag (the cas == `head(address)`), so the operator scans the trail by sight.

        THE ADDRESS THIS QUERIES (the load-bearing point):
          versions accrue at the address a `set_ref` WROTE — a compute node's own `run://<graph>/<node>`
          (it gets a `set_ref` every fire). A PORTAL never calls `set_ref` (RESOLVE='reference', the
          scheduler skips it), so a portal's OWN address has NO history — the FE must query the address the
          portal POINTS AT (its `config.ref`), which is what gets the versions. This method takes whatever
          `run://` address is asked and returns that address's trail; the FE chooses the right one.

        S0/SCOPE GATE: a versioned output is a `run://` address (mirrors how `cached` + `stale_at_address`
        are served). Malformed / non-`run://` RAISES (fail-loud, rule 4 — the bridge turns it into a 400 so
        a junk query never silently reads as 'no versions'). An address with NO history returns an HONEST
        empty list (`versions: []`) — distinct from a malformed query (which raises), never a silent wrong
        value. `lineage()` (provenance INPUTS) is a different axis and is untouched — this is the temporal
        trail of one address, not what it was made from.

        Returns {address, current, count, versions:[{cas, ts, is_current, preview}]} newest-first."""
        import json as _json
        from contracts.address import scheme as _scheme
        if _scheme(address) != "run":
            raise ValueError(
                f"ref_versions expects a run:// output address (e.g. run://<graph>/<node>); got "
                f"{address!r}. 'Versions at an address' is a stored-output trail — a ui:// element (or any "
                f"non-run scheme) has no set_ref history. For a PORTAL, query the address its config.ref "
                f"points at (the portal itself is a live window, it never writes a version).")
        current = self.store.head(address)                       # the live current value (UNCHANGED resolve)
        trail = self.store.ref_history(address, limit=limit)     # oldest-first {ts, cas} from the index
        versions = []
        for e in reversed(trail):                                # NEWEST-FIRST for the surface
            cas = e.get("cas")
            preview = None
            try:
                val = self.store.get_content(cas)                # the PRIOR bytes, fetched by cas (survive)
                s = val if isinstance(val, str) else _json.dumps(val)
                preview = s if len(s) <= 160 else s[:157] + "…"
            except Exception:
                # the index references a cas whose object is missing/unreadable — SURFACE it, do NOT pretend
                # an empty value (rule 4: fail-loud-legible; the operator sees the version is unfetchable).
                preview = "⚠ version bytes unavailable at this cas"
            versions.append({"cas": cas, "ts": e.get("ts"),
                             "is_current": (cas == current), "preview": preview})
        return {"address": address, "current": current, "count": len(versions), "versions": versions}

    def stale_at_address(self, address: str) -> dict:
        """L10 (§21.7#10): is the cached result AT this node's address out of date vs its CURRENT inputs?

        A surface shows "cached / stale at this address." **"cached" is ALREADY served** — the
        `cached` node-state derives on reload when the output address resolves (`state()`, S5/F3).
        **"stale" is NOT a served field, and it is NOT a free read.** Deriving it is a COSTED
        DERIVATION (seams-engine Seam 8a): recompile the node → resolve its current input
        content-hashes → compute the NEW `_memo_sig` → `memo_get`-compare against the STORED output
        cas at the node's `run://` address. So this is a method the surface CALLS when it wants the
        verdict — never an always-on key on the node dict (that would pretend staleness is free).

        It LEANS ON THE EXISTING MEMO GATE — it does not add a new cache. It REUSES the scheduler's
        `_memo_sig` (the exact formula the gate computes, port→content-hash) and `compile` (the exact
        execution face the scheduler runs), reads `memo_get` + `head`, and COMPARES. It writes
        nothing: NO `mod.run`, NO `put_content`, NO `memo_set`, NO `set_ref`. The memo gate
        (scheduler.py) is UNCHANGED — L10 reads a derived comparison from it, never mutates it.

        THE LOAD-BEARING RULE (one rule; both verdict cases fall out of it):
            fresh  ⟺  memo_get(sig_now) is not None  AND  memo_get(sig_now) == head(address)
            everything else (INCLUDING a memo miss) → stale.
        The compare to `head(address)` (not just "does sig_now exist in memo") is essential: current
        inputs could map to a DIFFERENT memoized output than the one written at the ref — that is
        stale too. A memo miss (sig never computed for these inputs) is stale, NOT fresh, NOT unknown.

        FAIL LOUD (rule 4) — the verdict is "unknown" (with a reason), NEVER a silent "fresh", when
        the node CANNOT be meaningfully compared:
          • malformed / non-`run://` address → RAISES (the bridge turns it into a 400);
          • the node isn't in the graph → unknown;
          • a VOLATILE node → the gate re-runs it EVERY pass by design (its output is not a pure
            function of its inputs), so a memo comparison is misleading → flag `volatile=True`;
          • a reference node (portal, RESOLVE='reference') → never computed/memoized → unknown;
          • a DECLARED input port unresolved → can't form a valid sig → unknown;
          • NO stored output at the address yet → a distinct "no cached result" (never a silent fresh).

        Returns {address, graph, node, stale, unknown, reason, volatile, sig?, stored_cas?, memo_cas?}.
        `stale` is True/False ONLY when a real comparison was made; otherwise it is None and
        `unknown` is True (a silent `stale=False` for an unevaluable node would be a lie — rule 4)."""
        from contracts.address import scheme as _scheme

        # --- SCOPE GATE: a node-instance locus is a run:// address (matching how `cached` is served).
        # Do NOT reuse the ui:// grammar gate (parse_ui_address) — that RAISES on non-ui:// and this
        # key is run://<graph>/<node>. We parse the run grammar ourselves (the address module exposes
        # the builder `run_address`/`scheme`, not a structured parser). The node-level logical form the
        # scheduler + compile use is `run://<graph>/<node>` (main) or `run://<graph>/<node>@<branch>`
        # (compile._addr / suite.state). Malformed / non-run:// RAISES (fail-loud; the bridge's
        # try/except → 400 — a junk query must never silently read as a node verdict).
        if _scheme(address) != "run":
            raise ValueError(
                f"stale_at_address expects a run:// node address (e.g. run://<graph>/<node>); "
                f"got {address!r}. 'Stale at this address' is a NODE-instance verdict — a ui:// element "
                f"(or any non-run scheme) has no memo/run semantics.")
        rest = address[len("run://"):]
        rest = rest.split("#", 1)[0]                       # drop a #run=<id> fragment if present
        branch = "main"
        if "@" in rest:
            rest, branch = rest.rsplit("@", 1)             # run://<graph>/<node>@<branch>
        parts = rest.split("/")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError(
                f"stale_at_address: {address!r} does not name a node (need run://<graph>/<node>"
                f"[@<branch>]).")
        graph_id, node_id = parts[0], parts[1]

        def _unknown(reason: str, **extra) -> dict:
            # fail-loud-legible: stale is None (NOT False) when we could not compare — never a silent fresh.
            base = {"address": address, "graph": graph_id, "node": node_id,
                    "stale": None, "unknown": True, "reason": reason}
            base.update(extra)
            return base

        # --- recompile (the SAME execution face the scheduler runs). A dangling edge raises in
        # compile → unknown (we don't let it crash a status read; rule 4 legibility).
        from runtime.compile import compile as _compile
        try:
            execs = _compile(self._load(graph_id), branch=branch, node_types=self.registry)
        except Exception as e:
            return _unknown(f"could not recompile graph {graph_id!r}: {type(e).__name__}: {e}")
        ex = next((e for e in execs if e.id == node_id), None)
        if ex is None:
            return _unknown(f"no node {node_id!r} in graph {graph_id!r}")

        mod = self.registry.get(ex.type)
        if mod is None:
            return _unknown(f"node-type {ex.type!r} is not registered")

        # --- reference nodes (portals) are never computed/memoized — a live window, not a run.
        if getattr(mod, "RESOLVE", "compute") == "reference":
            return _unknown(
                f"node {node_id!r} is a reference node ({ex.type!r}, RESOLVE='reference') — it is a "
                f"live window onto another address, never computed or memoized, so 'stale vs inputs' "
                f"does not apply.")

        # --- VOLATILE nodes: the gate re-runs them EVERY pass by design (output is not a pure
        # function of inputs — they read external truth: repo/index/clock). A memo comparison would
        # be misleading (their sig can be constant while their true output changes), so flag it.
        if getattr(mod, "VOLATILE", False):
            return _unknown(
                f"node {node_id!r} ({ex.type!r}) is VOLATILE — the memo gate re-runs it every pass by "
                f"design (it reads mutable external truth), so a memo-signature comparison cannot tell "
                f"fresh from stale; it is always re-derived on run.", volatile=True)

        # --- resolve CURRENT input content-hashes EXACTLY as the scheduler does (scheduler.py:80).
        # A declared input port that is unwired or unresolved → we cannot form the sig the gate
        # would → unknown (never a silent fresh).
        declared = set(getattr(mod, "PORTS_IN", {}).keys())
        if not declared <= set(ex.inputs.keys()):
            missing = sorted(declared - set(ex.inputs.keys()))
            return _unknown(f"node {node_id!r} has unwired input port(s) {missing} — cannot form its "
                            f"memo signature (it would not be READY to run).")
        input_map = {}
        for port, a in ex.inputs.items():
            cas = self.store.head(a)
            if cas is None:
                return _unknown(f"input port {port!r} of {node_id!r} is unresolved (address {a!r} holds "
                                f"no content) — cannot form its current memo signature.")
            input_map[port] = cas                           # port -> content-hash (the gate's form)

        # --- compute the NEW signature via the scheduler's OWN formula (no reimplementation — one source).
        from runtime.scheduler import _memo_sig
        version = getattr(mod, "VERSION", "1")
        sig_now = _memo_sig(ex, version, input_map)

        # --- MULTI-OUTPUT nodes (gate/join/pair: >=2 declared PORTS_OUT) write to per-port FRAGMENT
        # addresses (run://<g>/<n>#<port>, compile.py), so NOTHING is stored at the bare node address —
        # yet the memo cas is the WHOLE multi-port result, not a single cas comparable to one output
        # address. A bare head(address)==None here would emit a misleading "run it first" even for a node
        # that HAS run. Flag it honestly (unknown + the real reason) rather than mis-report — fail-loud
        # legibility (rule 4). Single-output staleness is the served contract (the FREE 'cached' half is
        # also a single bare-address read).
        if len(ex.outputs) > 1:
            return _unknown(
                f"node {node_id!r} has {len(ex.outputs)} output ports {sorted(ex.outputs)} — its memo "
                f"entry is the WHOLE multi-port result, not a single cas comparable to one output "
                f"address (each port writes its own run://…#<port> fragment); single-output staleness only.")

        # --- the stored output cas at the node's address (the FREE 'cached' half reads this same ref).
        stored_cas = self.store.head(address)
        if stored_cas is None:
            return _unknown(f"node {node_id!r} has no stored output at {address!r} yet — there is no "
                            f"cached result to be stale (run it first).")

        # --- THE COMPARISON (read-only). memo_get(sig_now) is the cas the gate WOULD reuse for the
        # current inputs; fresh iff it exists AND equals the stored output. A miss (None) or a
        # mismatch → stale. NO write of any kind happens here (the gate is untouched).
        memo_cas = self.store.memo_get(sig_now)
        fresh = (memo_cas is not None) and (memo_cas == stored_cas)
        return {"address": address, "graph": graph_id, "node": node_id,
                "stale": (not fresh), "unknown": False, "reason": "",
                "volatile": False, "sig": sig_now, "stored_cas": stored_cas, "memo_cas": memo_cas}

    def replay(self, limit: int = 200) -> list:
        """The whole captured path, oldest-first — the trajectory that trains the twin (I1)."""
        return list(reversed(self.store.recent_events(limit)))
