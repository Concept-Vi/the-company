---
type: deep-research
scope: contracts + registry + governance — addressability/component backbone + act/wire seams
date: 2026-06-08
sources:
  - contracts/address.py (C1)
  - contracts/node_type.py (C2)
  - contracts/node_record.py (C3)
  - contracts/resolver.py (C4)
  - contracts/object_info.py (C5)
  - contracts/cognition_info.py (C5 sibling)
  - contracts/ui_info.py (C1 UI registry)
  - contracts/bridge_msgs.py (C8)
  - contracts/tools.py (C7)
  - contracts/shapes.py (C3 shim)
  - runtime/registry.py (lines 1–112, full file)
  - runtime/governance.py (lines 1–100 + grep clusters)
  - runtime/implement.py (lines 1–80 + grep clusters)
  - runtime/suite.py (targeted ranges: UI_REGISTRY 7618–7760, surface_build_intent 6596–6760, act/I4 3990–4070, route_click 4051–4070, request_change 3841–3880, autonomous_dispatch 3882–3910, _tier_for_address 3947–3970, governance grep clusters)
status: BUILD=built+proven; PARTIAL=built-but-gaps; DESIGNED=spec-exists-not-fully-implemented
---

# Contracts + Governance Deep Read

## 1. The Spine: What "contracts/" Is

`contracts/` is the **import-nothing layer** — every other module imports from it; it imports from nothing above it. It is the seam set the entire system composes against. Changes here have the widest blast radius of anything in the repo; a contract change requires CONFIRM governance, never an off-the-cuff edit.

The contracts constitution (`contracts/AGENTS.md`) states the invariant explicitly: shapes carry a `schema_ver` or `version` marker; growth is **additive only** (new optional fields with defaults). A breaking change is a new versioned shape side-by-side, never an edit-in-place. No backend types leak into contracts — they are storage-agnostic.

---

## 2. The Address Grammar (C1 — `contracts/address.py`) — **BUILD**

The coordinate system for the entire system. Six address schemes:

```
run://<domain>/<intent>/<node>@<branch>#run=<id>    mutable pointer (the live node locus)
cas://<algo>:<hash>                                  immutable content (integrity + dedup)
blob://<algo>:<hash>                                 large binary (addressed, not inlined)
vec://<source-address>#emb=<model>                   embedding of a source
ui://<kind>/<ref>                                    a UI component (resolved by ui_info, not the store)
code://<file-stem>/<symbol>                          a code symbol (resolved by Suite.resolve_scope)
```

`address.py:32`: `SCHEMES = ("run", "cas", "blob", "vec", "ui", "code")`

The `ui://` and `code://` schemes are **label-only** in the address grammar — the store does not resolve them. `ui://` is resolved by the UI-component registry (`contracts.ui_info`). `code://` is resolved by the backend `ui://→code://→scope[]` resolver (`Suite.resolve_scope`), reading `design/_system/{addresses.json, code-symbols.json}`. Both are purely additive to SCHEMES (no record shape or schema_ver change).

`address.py:35` — the `Provenance` model: `address` (run://), `content_hash` (cas://), `type`, `produced_by`, `inputs` (lineage list), `agent`, `created_at`, `schema_ver=1`. This is the per-write integrity + lineage record carried into the store.

---

## 3. The Node-Type Contract (C2 — `contracts/node_type.py`) — **BUILD**

`NodeType` is the **single definition of what a node IS**. Three kinds: `process · content · presentation`. Every node-type is one `NodeType` instance; UI, runtime, and tools all project from this one shape.

Key fields per NodeType:

| Field | Role |
|-------|------|
| `name` | Unique id (e.g. "extract") — the registry key |
| `kind` | process / content / presentation |
| `extends` | Type-graph relation (S4 — the inheritance/composition chain) |
| `ports` | Inputs + outputs, each `{port_name: port_type_name}` |
| `config_schema` | The inspector's editable fields (what the operator sets) |
| `output_schema` | The structured thing the node produces (C1.4 — used by cognition driver to validate role output) |
| `render_set` | Which render modes this type supports (collapsed/expanded/full/workshop) |
| `inspector_schema` | Extended inspector shape |
| `actions` | Verbs this type supports (defaults to `["run"]`) |
| `version` | Per-type version marker (additive growth) |

`model_post_init` derives `title` from `name.title()` if not set — so a bare `name` is a fully-valid NodeType with a sensible display label.

The C3 record (`contracts/node_record.py`, `SCHEMA_VER=2`) carries the runtime shapes: `NodeInstance` (workflow face — id, type, config, position, size, render_state, layer, status, outputs), `Edge` (from_node/from_port/to_node/to_port + `kind: EdgeKind`, default "data"), `Graph` (id, nodes, edges), `ExecNode` (execution face — compiled, no pixels). `EDGE_KINDS` registry (`node_record.py:30`) is single-source: "data" / "injection" / "gate" / "fan_in" — declared once, never invented off-registry.

---

## 4. How Node-Types Register (C2/C5 — `runtime/registry.py`) — **BUILD**

**The declare-by-registration pattern:** dropping a `.py` file in `nodes/` (or any discovered directory) is ALL it takes to add a new node type. No hardcoding, no manual registration call, no frontend code.

`NodeRegistry.discover(dirs)` (`registry.py:55`) scans each directory, loads every non-underscore `.py` file, and calls `register_module(name, mod)` for any module that has a `run` attribute.

`register_module` (`registry.py:75`) builds a `NodeType` from module-level declarations:

```python
self.types[name] = NodeType(
    name=name,
    kind=getattr(mod, "KIND", _infer_kind(name)),          # process or content (inferred or declared)
    ports=Ports(inputs=dict(getattr(mod, "PORTS_IN", {})),
                outputs=dict(getattr(mod, "PORTS_OUT", {}))),
    config_schema=dict(getattr(mod, "CONFIG", {})),
    output_schema=_read_output_schema(mod),                  # C1.4: dict or Pydantic model → json-schema
    version=int(getattr(mod, "VERSION", "1")),
)
```

The module declares `KIND`, `PORTS_IN`, `PORTS_OUT`, `CONFIG`, `OUTPUT_SCHEMA`, `VERSION` as module-level attributes. The registry reads them and synthesises a `NodeType`. The module itself (`mod`) is stored at `self._modules[name]` and is invoked as the execution callable (its `run` function).

`_read_output_schema(mod)` (`registry.py:22`): accepts a plain dict (JSON-shape spec) OR a Pydantic BaseModel subclass (serialized via `.model_json_schema()`). Anything else declared but malformed → fail loud (never a silent wrong schema). Absent → `{}` (additive default, every existing node-type unchanged).

**Schema each registry entry carries:**
- The `NodeType` fields above (the shape the frontend sees via `/object_info`)
- The `mod` itself (the runtime callable — `mod.run`)
- Both keyed by `name` — key/name mismatch raises in `build_object_info` (`object_info.py:79`)

`NodeRegistry.object_info()` (`registry.py:100`) delegates to `build_object_info(self.types)` — the C5 serialization function — and produces the `/object_info` map the frontend renders its entire palette and inspector from. Add a node → registers → `/object_info` gains an entry → frontend re-merges → new type appears live, no frontend code written.

`rediscover(dirs)` (`registry.py:68`) clears and rebuilds from the filesystem — so a removed file (e.g. a reverted self-applied node) actually un-registers. `discover()` only adds; `rediscover()` is the clean rebuild.

**Type-graph queries** (`registry.py:93`): `produces(port_type)` and `consumes(port_type)` return which registered node-types produce or consume a given port type — the S4 queryable type-graph, traversed live from the registry without a separate index.

---

## 5. The UI-Component Registry (C1 UI — `contracts/ui_info.py`) — **BUILD**

A **parallel registry, distinct from NodeType**. UI components are not node-types. `ui_info` is the declaration of what UI elements exist and what the RHM may do to them — the addressing layer behind `ui://<kind>/<ref>`.

**`UiComponentEntry`** (`ui_info.py:58`) is the per-component schema:

| Field | Meaning |
|-------|---------|
| `ref` | The `<ref>` in `ui://<kind>/<ref>` — the stable address key |
| `kind` | chrome / field / canvas / panel / ext |
| `title` | Human label |
| `capabilities` | `Capabilities` model — what the RHM may DO to it (opt-in booleans) |
| `dom_handle` | The `data-ui-ref` value the FE resolves via querySelector (for chrome/field/panel/ext) |
| `camera_ref` | A node-id the FE zooms the camera to (for canvas kind) |
| `version` | Per-entry version marker |

**Capabilities** (`ui_info.py:43`) are all `False` by default — opt-in:
- `pointable` — show can point a cursor/arrow at it
- `spotlit` — show can highlight it
- `presentable` — content can be presented in-place
- `openable` — can be opened/expanded
- `drivenReadOnly` — RHM may drive it read-only (demonstrate, not mutate)

**`build_ui_info(entries)`** (`ui_info.py:88`) serializes the registry for the frontend: `{"<ref>": {...fields...}}` — mirroring `build_object_info`'s `{"<name>": {...}}`. Fail-loud on non-UiComponentEntry or duplicate ref (one-source rule enforced with explicit raise).

**The canonical `ui://` grammar** (`ui_info.py:158+`): S0 established that TWO non-interoperable grammars existed — the corpus (`ui://inbox/build-review`, element-level, region-keyed) and the live app (`ui://chrome/inbox`, kind-keyed). The reconciliation: the grammar is **purely structural** (segment shape), permissive on purpose. Semantics (kind vs region) live in the **record**, not the string.

The `UnionAddressRecord` (`ui_info.py:262`) is the ONE canonical per-address record that both sides project to:

```
address       — the full ui://… string (the stable key + carrier)
kind          — chrome|field|canvas|panel|ext  (REQUIRED — the live resolver dispatches on this)
region        — the coarse grouping (REQUIRED non-empty)
capabilities  — canonical bool-object (normalize_capabilities)
represents    — feature-id → inventory (corpus, optional)
code          — powering code ref → code:// symbol (corpus, optional — S3 resolves to scope)
states        — applicable NODE_STATES for @state addressing (optional)
tier          — governance posture for COMMANDS at this address (optional — feeds I4)
title         — human label (optional)
howto         — foundational affordance/help text for this address (D1 stratum, optional)
```

`from_corpus` and `from_live` classmethod projectors (`ui_info.py:313,337`) normalize each side into the union record. Two row-forms coexist in the live registry after S1: bare-ref rows (region/chrome handles + canvas '*') whose canonical address is `ui://<kind>/<ref>`, and full-string rows (S1's 24 corpus element addresses) where `ref` IS already the full canonical string — `from_live` handles both (`ui_info.py:354`).

`conform_corpus` / `conform_live` (`ui_info.py:402,421`) validate entire registries, enumerating every failing address (fail-loud at the surface, not on the first one).

**Schema-additive rule** (`ui_info.py:22`): new serialized fields carry defaults; an older frontend ignores unknown fields. A breaking change is a new versioned shape side-by-side, never edit-in-place.

---

## 6. The Live UI_REGISTRY in suite.py — **BUILD**

`Suite.UI_REGISTRY` (`suite.py:7618`) is the live declaration of all known UI components. It is a class-level list of tuples, built at class-definition time. Structure: `(ref, kind, title, handle_dict, caps_dict[, union-extras_dict])`.

The 9 bare-region rows (toolbar, inspector, inbox, activity, chat, workshop, walkthrough, deferred-queue) plus the canvas whole-canvas row (`"*", "canvas"`).

```python
UI_REGISTRY = [
    ("toolbar",   "chrome", "Toolbar",      {"dom_handle": "toolbar"},   {"pointable": True, "spotlit": True}),
    ("inbox",     "chrome", "Inbox",        {"dom_handle": "inbox"},     {"pointable": True, "spotlit": True, "openable": True}),
    # ... 7 more bare-region rows ...
    ("*", "canvas", "Node canvas", {"camera_ref": "*"},  {"pointable": True, "spotlit": True, "presentable": True}),
]
UI_REGISTRY = UI_REGISTRY + _load_corpus_element_addresses()  # suite.py:7651
```

`_load_corpus_element_addresses()` (`suite.py:31`) projects the 24+ element-level addresses from `design/_system/addresses.json` into the registry — reads, never hand-transcribes. Each corpus entry produces a 6-tuple with `union-extras` carrying `region, represents, code, tier, howto` from the `UnionAddressRecord`. This is what feeds I4's `_tier_for_address` with the per-address governance tier.

The 6th union-extras element is ADDITIVE: the 9 bare-region rows have NO 6th element (their handles were hand-authored before the corpus load); only the corpus-derived element rows carry it. `_tier_for_address` guards against a missing 6th element (`suite.py:3963`: `extras = (row[5] if len(row) > 5 else None)`).

`Suite.build_ui_info()` (`suite.py:7653`) iterates `UI_REGISTRY`, builds `UiComponentEntry` instances, and delegates to `contracts.ui_info.build_ui_info` — the contracts module provides the shape, the runtime provides the data.

---

## 7. The C5 Serializations: Object Info and Cognition Info

### 7a. `/object_info` (`contracts/object_info.py`) — **BUILD**

`build_object_info(node_types: dict[str, NodeType])` serializes the C2 type library into `{"<name>": {...C2 fields...}}`. Generated from the registry — never hand-written. Fail-loud on a non-`NodeType` value or a key that disagrees with `NodeType.name` (`object_info.py:79`). The frontend is a **generic renderer** — it holds no per-node-type code; it renders from this map.

### 7b. `/cognition_info` (`contracts/cognition_info.py`) — **BUILD** (backend registries), **PARTIAL** (live FE rendering)

The sibling of `object_info` for the concurrent-cognition layer. `build_cognition_info(roles, rules, edge_kinds, thought_shapes, activation_contexts, ...)` produces a JSON map the live cognition view renders from — roles as nodes, chains/injections as edges, status vocabulary, rule badges, edge-kind labels. Generated from the registries (file-discovered roles, declared rules), never hand-written.

The `COGNITION_EVENT_KINDS` dict (`cognition_info.py:52`) is the **emit-contract the FE binds to** — declared here as DATA so the FE doesn't bind to events nothing emits. Six event kinds: `cognition.turn.start`, `cognition.role.fire`, `cognition.role.ran`, `cognition.inject`, `cognition.part`, `cognition.turn.done`. Each carries an `address` field (a `ui://` or `run://` locus) — making cognition events addressable in the same coordinate system as UI elements and live nodes.

---

## 8. Schema Discipline — "Extend by Registration"

The invariant is consistent across every contract:

**Pydantic throughout**: every contract shape is a `BaseModel`. Validation happens at the seam — a malformed value raises at construction, never at use.

**Schema-additive**: every growth move adds a new **optional** field with a default. Old serialized data deserializes unchanged; old frontends ignore unknown fields. `schema_ver` (or `version`) is bumped when the serialization shape changes.

**Extend by registration** means concretely:

1. **Node-types**: drop a `.py` file with `run`, optional `KIND/PORTS_IN/PORTS_OUT/CONFIG/OUTPUT_SCHEMA/VERSION`. The `NodeRegistry` discovers it. `/object_info` gains an entry. The frontend sees a new palette item. Zero code written outside the one file.
2. **UI components**: add a tuple to `UI_REGISTRY` (bare-ref row) or add an entry to `design/_system/addresses.json` (corpus-driven element row). `build_ui_info` serves it. The corpus grammar validator (`conform_live`) validates it against the ONE canonical grammar.
3. **Cognition roles**: drop a `roles/<id>.py` file (gated by `role_build` — CONFIRM posture; module-gated import before any write). `RoleRegistry.discover()` picks it up. `/cognition_info` gains a new role card. The live cognition view renders it.
4. **Tool verbs**: add a `ToolSpec` entry to `TOOLS` in `contracts/tools.py`. The MCP server projects from this map — zero new server code.

**One-source enforcement** (`object_info.py:79`, `ui_info.py:110`, `cognition_info.py:112`): every serializer checks key = declared id. A mismatch is a loud raise, never a silently-wrong projection.

---

## 9. The C7 Tool Surface (`contracts/tools.py`) — **BUILD**

The tool surface is a **small fixed set of generic verbs** — NOT one tool per node-type. The set is the kernel:

- **Introspection**: GetTypeGraph, ListByType, ObjectInfo, Search (pure reads)
- **Sources**: ListSources, RegisterSource, SurveySource
- **Graphs/compositions**: ListGraphs, CreateNode, Connect, SetConfig, DeleteNode, ValidateGraph
- **Runs**: RunGraph, WatchRun, PauseRun, Retry, BranchRun, Reprioritise
- **Results**: GetResults, GetTrace, Feedback
- **Surfaced decisions**: ListSurfaced, ResolveSurfaced

Adding a node-type adds **zero tools**. The agent uses introspection verbs to LEARN a type (`GetTypeGraph`, `ObjectInfo`), then the generic verbs to USE it — the same surface the canvas drives (symmetric agency). `CreateNode`'s `type` parameter is a plain `str` — the GENERIC parameter, not a typed enum (proven in the self-check at `tools.py:546`: any type invented tomorrow works with the same verb).

`ToolAnnotations` (`tools.py:322`): `readonly`, `destructive`, `idempotent`. `readonly AND destructive` is incoherent and raises at construction. `DeleteNode` is `destructive=True`; all reads are `readonly=True`. Annotations feed governance (S7/D4) so an agent is told the truth about each verb.

---

## 10. Governance (`runtime/governance.py`) — **BUILD**

The act-unwatched policy. Every action has a posture on the axes **reversibility · cost · externality**:

```
AUTO    — cheap, reversible, internal
          inspect, compose, configure, run, write_own_layer, decision_build

SURFACE — meaningful but recoverable; proceeds on default + deadline
          promote, spend

CONFIRM — irreversible / expensive / external
          destructive, code_build, register_type, external, source_data,
          frozen_contract, ui_panel, ui_extension, review, role_build, role_delete
```

`posture(action_class)` (`governance.py:56`) returns the POLICY posture; **unknown class → CONFIRM** (the safest default, not a silent allow).

`LOCKED = {"source_data", "external", "frozen_contract"}` (`governance.py:49`) — these never graduate to AUTO, regardless of earned trust. D4/D7 forever-confirm.

`guard(action_class, do, *, confirmed, inbox, payload)` (`governance.py:60`) is the enforcement seam:
- AUTO: run `do()` immediately
- SURFACE: run `do()`, record a surfaced note (default = proceed, deadline-based)
- CONFIRM: run ONLY if `confirmed=True`; otherwise surface a gate item and raise `GovernanceError` — fail loud, never a silent refuse

The `decision_build` class is **deliberately AUTO** (`governance.py:27`). AUTO here means auto-DISPATCH on the operator's approve (no second gate before building) — it does NOT mean auto-CLOSE without review. The ONE class the wire may auto-dispatch: the operator's approve of the declared-scope build-intent IS the authorization. After every build, the result is surfaced for review (`decision.surfaced_for_review` event + inbox review item) — AI-operated is NOT review-free. The CLOSE routes through `guard("code_build")` (CONFIRM), so an unverified build can never reach `implemented`.

The `Inbox` (`governance.py:78`) is the **surfaced-decisions store** — the same inbox both the UI face and the MCP face see. `surface()` holds `surfaced_lock` across the full allocate→mint→save so no two concurrent surfacers can collide on the same id (T1-RACE closed). Lifecycle statuses (`governance.py:151`): `inbox → presented → responded → resolved | requeue | implemented`. The `status` lane tracks the walk; `resolved` is the operator-only terminal verdict.

---

## 11. The I4 Address→Tier Governance — **BUILD** (gate) / **PARTIAL** (per-address data)

I4 is the **address-keyed governance gate** — the clicked address, not the verb, decides the governance tier for a click.

`_tier_for_address(address)` (`suite.py:3947`) reads the live `UI_REGISTRY` rows. A row is `(ref, kind, title, handle, caps[, union-extras])`; the 6th element (if present) is the union-extras dict carrying `tier`. The 9 bare-region rows have no 6th element → returns None.

```python
def _tier_for_address(self, address):
    for row in self.UI_REGISTRY:
        ref = row[0]
        if ref == address or address.endswith("/" + ref):  # match full-string OR bare-ref suffix
            extras = (row[5] if len(row) > 5 else None)
            tier = (extras or {}).get("tier")
            return tier or None   # empty-string tier reads as untiered
    return None
```

If the address carries a CONFIRM/LOCKED tier → the click is **surfaced for approval** and NOT dispatched (`suite.py:4008–4030`). If untiered or AUTO → falls through to the verb's own governance class.

**The click-indicates-consent enforcement** (`suite.py:4001–4030`): when `posture(addr_tier) != AUTO`, the click PROPOSES (surfaces for see-and-approve) and does NOT act. The surfaced item carries `ui_target = address` (L8) so the operator can navigate back to the element awaiting approval. It is NEVER routed through `autonomous_dispatch` — that would execute `do()` directly, bypassing consent. (`suite.py:4010`: "We MUST NOT route this through autonomous_dispatch: its non-AUTO branch calls do() directly ... for a `run` verb do() EXECUTES the graph — that would be the inverse U1 regression.")

The `UnionAddressRecord.tier` field (`ui_info.py:308`): optional, an action_class string (e.g. `"source_data"`, `"code_build"`). Populated from the corpus `addresses.json` `tier` key. The `from_corpus` projector (`ui_info.py:332`) passes it through.

**Status breakdown:**
- The tier gate in `act()` — **BUILT and proven**
- The union-extras 6th-tuple mechanism to carry tier into live registry rows — **BUILT**
- Per-address `tier` assignments in corpus `addresses.json` — **PARTIAL** (the infrastructure is built; the data authoring for each address is incomplete)

---

## 12. The RHM Verb Set and Governance Routing — **BUILD**

`RHM_VERB_SPECS` (`suite.py:~2960`) declares every conversational verb available to the RHM, each as a `VerbSpec(desc, action_class, mode_mask, mode_guard)`:

- `run`, `compose`/`build`, `show`, `consult`, `configure`, `load_voice`, `unload_voice` — **AUTO** (posture from POLICY)
- `propose` (new node-type draft), `panel` (new UI panel draft), `extend` (new extension draft) — **CONFIRM** via `register_type`/`ui_panel`/`ui_extension`
- `request_change` — **CONFIRM** via `register_type` (surfaces a build-intent for approval; NOTHING builds until operator approves)

`RHM_VERB_CLASS = {v: s.action_class for v, s in RHM_VERB_SPECS.items()}` (`suite.py:3058`) — the deterministic governance router input, derived from the single registry.

**`request_change`** is the conversational→wire bridge verb (`suite.py:3044`): "surface a build-intent to CHANGE existing code at a ui:// element." It routes through `surface_intent_at` (which composes I6 + S3 + `surface_build_intent`) — the ONLY conversational path to the `claude -p` self-build wire; the wire-door (`/api/build-intent`, `/api/intent-at`) is unchanged. Address resolution uses `resolve_change_target` (`suite.py:3858`): (a) the operator's held locus (`current_locus()`), else (b) the model-supplied target matched against the registry, else (c) ASK — an unresolvable target NEVER mints a build-intent (rule 8, no guessed scope).

`autonomous_dispatch` (`suite.py:3882`) is the G3 decide-for-me deterministic dispatcher: `posture(action_class)` is the ONLY input (no confidence value, no score, no judgement call). AUTO → `guard(action_class, do)` → ACT. Non-AUTO → `do()` is called directly, but for an RHM CONFIRM verb `do` is a GOVERNED body that SURFACES a draft (never applies). `do()` here can only ever surface or run a reversible AUTO op — never approve, apply, or mutate source (the RHM_VERBS whitelist excludes apply/delete/file-write structurally).

`route_click` (`suite.py:4051`) is **I5 — the annotate-vs-operate router**: ONE classifier that decides per click whether the click attaches a COMMENT (annotate, I6) or proposes/runs an OPERATION (operate, I2/I4/I3). The scheme is a routing HINT, not the safety gate: a `ui://` click with no consequential verb → ANNOTATE; a `run://` click → OPERATE always; a consequential VERB at ANY address → OPERATE. What GATES a mutating command is the address's governance TIER (`_tier_for_address` → CONFIRM/LOCKED) + `guard()`, not the scheme.

---

## 13. The Decision→Implementation Wire — **BUILT** (end-to-end), **PARTIAL** (L1 FE wiring + per-address data)

The full circuit: **addressed-feedback → build-intent → operator approve → dispatch → build → verify → close + surface-for-review**

### A. `surface_build_intent` (`suite.py:6596`) — the production front door — **BUILD**

Mints a build-intent item into the inbox. Distinguishes by `payload.intent = "build"` (the W2 discriminator). Carries:
- `spec` — the what-to-build text (the operator sees this)
- `scope` — the declared paths the build MAY touch (empty = DENY-ALL at dispatch)
- `consequence_class` — the POLICY class the pre-dispatch gate keys on (default `"decision_build"`, an AUTO class)
- `why` — the operator-legible reason
- `address` (X1, optional) — the `ui://` locus the build derives from (threaded INTO the payload before persist — the old `out["address"]=ui_addr` set AFTER persist never reached disk; X1 fixed this)
- `symbols` (X2, optional) — `code://` symbol-neighbours of the locus (resolved by S3, reused not recomputed)
- `context` (X3, optional) — bounded accumulated strata at the locus (gathered at mint time, consent-time trust property X5 — the surfaced record == what the build later composes from)
- `blast_radius` (X16, optional) — what the change could reach, shown to operator at consent time; persisted so `approve_reach` validates against the EXACT radius the operator saw (consent-time, never a fresh recompute that could disagree)

`resolved=None` on surfacing → a live escalation until the operator resolves it via `/api/resolve` (operator-only, off the MCP face). Empty scope = DENY-ALL: the dispatch-time scope-diff treats empty scope as DENY-ALL (`_in_any_scope` returns False for every path), so a build with no declared scope can NEVER close `implemented`. Durable enforcement at the gate that runs, not only at surface time.

### B. `surface_intent_at` (`suite.py:6663`) — the L1 address→intent seam — **BUILD**

The "addressed-feedback → wire entry" seam. A comment placed at a `ui://` address becomes a build-intent scoped to the code behind that address. Composes three EXISTING pieces (rule 3 — one source; never a parallel intent path):

1. `ingest_comment` (I6) — record the comment at the address (fails loud on malformed address / empty text)
2. `resolve_scope` (S3, `suite.py:7686`) — join `ui://` → `code://` symbol(s) → repo-relative `scope[]`. Reads `design/_system/code-symbols.json` (the code:// registry, NOT re-derived from raw addresses.json). INVERTS `referenced_by` into the forward map ui://addr → [symbols]. Empty/stale corpus → empty scope, carried legibly (note + stale flag), NEVER fabricated broad scope.
3. `surface_build_intent` — mint the build-intent with that scope (REUSED UNCHANGED)

**EMPTY / STALE SCOPE = DENY-ALL** is the headline safety property. S3 returns empty scope for orphan addresses, CSS-selector refs, stale corpus → passes straight through → DENY-ALL at dispatch. Never allow-all for an unmapped address.

L1 STOPS at surfacing for approval. Dispatch-on-approve is L2 — a separate, deliberate switch. `surface_intent_at` NEVER calls `dispatch_decision`.

### C. `request_change` verb → `surface_intent_at` — **BUILD**

The conversational bridge (`suite.py:3841–3876`): when the RHM fires `request_change`, the dispatch path calls `surface_intent_at(address, change, source="operator", consequence_class="decision_build")`. `address` is resolved via `resolve_change_target` (current_locus → named target → ASK). On ASK (unresolvable target): returns `{"did": "ask_target", ...}`, NO build-intent minted. On success: returns `{"did": "request_change", "surfaced": sid, "address": address, "scope": [...], "source": resolved["source"], "stale": ..., "note": ...}`.

### D. `resolve_surfaced` (`suite.py:9069+`) — the operator verdict seam — **BUILD**

OPERATOR-ONLY — off the MCP face. The agent cannot self-approve.

Vocabulary: `approve/reject/decide` → TERMINAL (writes `resolved`, status → resolved); `comment` → annotate only (status → responded, NOT resolved); `skip` → defer (status back to inbox, NOT resolved).

**L2 resolve→dispatch production trigger** (`suite.py:9196`): when `choice == "approve"` AND `wire_armed()` (i.e. `COMPANY_WIRE_PERMISSION=acceptEdits`) AND `is_build_intent(d)` → fires `_drive_dispatchable_bg(sid=sid)`. The background thread runs `drive_dispatchable → dispatch_decision` — the SAME governed path. **INERT BY DEFAULT** (`plan` posture = read-only, no self-modify). Two deliberate graduation switches: (1) the production trigger itself (L2), (2) the `COMPANY_WIRE_PERMISSION=acceptEdits` env var (implement.py `wire_armed()`, `implement.py:56`). Either absent → no self-modification.

### E. `dispatch_decision` (`suite.py:7179+`) — the governed dispatch verb — **BUILD**

The full sequence: CHECK → CLAIM → GATE → LAUNCH → VERIFY → CLOSE-or-SURFACE.

1. **Three-part bind verification**: kind=resolve · surfaced==sid · choice=approve. A forged/mismatched bind raises `GovernanceError`.
2. **Build-intent discriminator**: the item must have `payload.intent == "build"` (`is_build_intent`, `suite.py:6761`).
3. **EXACTLY-ONCE**: refuses if a `decision.dispatch` already exists for this `seq` (the durable event-log guarantee). Two threads or two processes — the check→emit is atomic under both `_dispatch_lock` (in-process RLock) and `store.graph_lock(f"dispatch-claim:{derived_from}")` (cross-process fcntl).
4. **W4 pre-dispatch gate on declared consequence_class**: ONLY an AUTO-posture declared class auto-dispatches. `decision_build` is AUTO; any CONFIRM/SURFACE/LOCKED class surfaces for the operator before building.
5. **Emit `decision.dispatch`** before launching (durable exactly-once claim via `_emit_durable` — raises on failure, never a swallowed claim).
6. **Launch** (`implement.launch`, `implement.py:352`) — injectable for tests, real `claude -p --output-format json --permission-mode <PERMISSION_MODE>` by default. DEFAULT permission mode is `"plan"` (read-only, changes nothing). `acceptEdits` is OPT-IN via `COMPANY_WIRE_PERMISSION=acceptEdits`.
7. **Verify** (W3 — run affected acceptance suites + drift check + adversarial critic). A verification miss surfaces back as a retryable build-intent, does NOT close.
8. **W4 scope-diff**: `changed_delta` (git ground truth, not the model's self-report via `_git_dirty_paths`) identifies every changed path. Any path outside the declared scope → surfaces back, NEVER closes `implemented`.
9. **GIT CHECKPOINT** (H8/Tim's safety mandate): commit exactly the build's `changed_delta` as a `[self-build] <sid>: <intent>` commit — making the build revertible via `git revert <sha>`. Commit failure → surfaces the build BACK, never closes it.
10. **CLOSE + SURFACE-FOR-REVIEW**: `guard("code_build", ..., confirmed=verify_passed)` — an unverified close RAISES. `implemented` means "done AND surfaced for review", never a silent terminal. AI-operated is NOT review-free.

---

## 14. The Wire's L1 Readiness Summary

**BUILT and proven:**
- `surface_build_intent` — the production front door (mints, persists, emits; scope=DENY-ALL when empty; X1/X2/X3/X16 payload fields threaded into persist before disk write)
- `surface_intent_at` — the L1 comment→build-intent seam (composes I6 + S3 + surface_build_intent)
- `request_change` RHM verb → `surface_intent_at` — the conversational→wire bridge (the ONLY conversational path to the build wire)
- `dispatch_decision` — the full governed sequence (bind · exactly-once · gate · launch · verify · scope-diff · git-checkpoint · close+surface)
- `resolve_surfaced` — the operator verdict seam (OPERATOR-ONLY, off MCP face)
- L2 trigger — the resolve→dispatch production trigger (built, INERT BY DEFAULT — `plan` mode; `acceptEdits` is the deliberate opt-in)
- Governance POLICY + `guard()` — enforcement at every action class
- I4 address→tier gate — address-keyed governance on clicks (built in `act()`, `suite.py:4001–4030`)
- `route_click` (I5) — the annotate-vs-operate router (built, `suite.py:4051`)

**PARTIAL (infrastructure built, wiring or data incomplete):**
- The FE surface sending comments with `address` payloads to `/api/build-intent` (the FE side of L1 is the net-new leg the interface pack builds)
- Per-address `tier` assignments in corpus `addresses.json` (the gate machinery is built; the per-address declarations are incomplete — most addresses lack a `tier` value, so they fall back to the verb's own class)
- The blast-radius (X16) display in the operator consent surface (the field is persisted at `surface_build_intent`; FE rendering is net-new)

**DESIGNED (spec exists, not yet implemented):**
- The operator's inbox UI surface walking items with `address` + `howto` context (D1 stratum — `howto` field is in `UnionAddressRecord` and persisted in corpus; the FE rendering of it at consent time is designed but not built)
- The `howto` field rendering in the inbox (the foundational affordance text per address)

---

## 15. Key Register-by-Declaration Pattern — Summary

The pattern is uniform across node-types, UI components, cognition roles, and tool verbs:

1. **Declare the thing as data** (a Python module / a registry tuple / a Pydantic model) — the declaration carries the schema, identity, capabilities, and governance posture
2. **The registry discovers / loads it** — no registration call; the registry scans, discovers, and builds the contract shape
3. **Serializers project it to consumers** — `build_object_info` → frontend palette; `build_ui_info` → RHM address targets; `build_cognition_info` → live cognition view; `TOOLS` → MCP server
4. **One-source enforced** — a key/name mismatch raises at serialization time, never silently emits a wrong projection
5. **Schema-additive always** — growth adds optional fields with defaults; old consumers continue working unchanged

The governance posture (`tier` on a UI address, `ToolAnnotations` on a verb, `consequence_class` on a build-intent, `POLICY` on an action class) rides in the same declaration — so the CORRECT action at every address is the AI's easiest path (the AI path-of-least-resistance law, the constitution's core design principle).
