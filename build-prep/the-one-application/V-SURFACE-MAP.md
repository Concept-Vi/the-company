The advisor caught a critical error: there are 8 reports, not 6. Let me recount: v-slot-socket, mode-colour, archetypes-atomic, sequences-stories-slides, gallery-app, channels-integration, resolution-spine, operator-surface-RHM. Yes, 8. The advisor's mechanical field-to-part mapping is sound. I'll synthesize directly from the reports' citations without re-reading files, preserve all status labels, surface the three conflicts, and capture BEYOND maximally. Here is the MAP.

---

# V-SURFACE RESEARCH MAP

**The build:** the full decision/command surface BUILT INTO THE V. Eight code-grounded dimensions, one resolution-first spine. Every named thing is a **type that resolves** — types + registries that resolve, never hand-placed markup, never restyle. This map carries each report's file:line citations verbatim and preserves its evidence tier (BUILT / observed-in-code / DESIGNED-not-built / claimed-not-verifiable).

---

## 1. The Resolution-First TYPE / REGISTRY Model (the spine)

**The universal "add a type" recipe** (from `resolution-spine.how_to_build`) — every named thing on the surface follows this one path, so the surface grows by adding rows, not by writing screen-code:

```
scheme label → contracts/address.py:129 SCHEMES  (additive, no schema_ver bump)
   + resolver branch → runtime/cognition.py:842 resolve_address()
   + Pydantic schema → contracts/<thing>.py
   + registry row → _CORPUS_REGISTRIES (suite.py:360) via _write_registry_file() (suite.py:9840)
   + first row file → <kind>/<id>.py
→ inherits territory_for, inspect_address, project(center=<new://...>) FOR FREE
```

The create gate `_write_registry_file(kind, spec)` (suite.py:9840): render spec as Python literal → import in tempdir via the registry's own `discover()` (gate-check) → atomic write → git commit → re-`discover()`. Fails loud on callable values.

| Named thing | Type / scheme | Resolver + Registry (file:line) | Schema (file:line) | Status |
|---|---|---|---|---|
| **mode** | `MODE_REGISTRY` (one dict, 8 entries, all axes) | `suite.py:2138`; all derived tables (MODE_SPECS, MODES, MODE_DIRECTIVES, PART_GRAIN, ACTIVATION_ALLOCATION) are VIEWS of it | `ModeSpec(BaseModel)` `suite.py:155` | **BUILT** — the most complete type-with-schema in the system; the exemplar |
| **V / slot / socket** | `component.organism.brand-icon` = shell with 8 named sockets | `V_ROW` `factory-mount.js:75-126` (authoritative runtime); `V_SYMBOL` `v-symbol-sockets.js:46-103` (predates `connection`); `setSocket()` `factory-ops.js:212-310` (write path, registry.has() gate at :233); `mountConnection()` `connection-mount.js:71-270` (turns a socket connection binding into a live child) | socket = `{accepts[], default, strategy, trigger, connection?}`; `connection` = `{child, trigger, choreography, collapse, effects[], selection, closeOnSelect, parentLeap}` | **BUILT** (runtime). **SCHEMA GAP:** `component.schema.json:74-103` declares sockets with `additionalProperties:false` + only 4 fields (accepts/default/strategy/trigger) — `connection` is NOT in schema, valid only because stored as free JSONB |
| **window** | `window://` (DESIGNED) — today a node mark-type state | mark-type registry rows `suite.py:257-264` (`"live"` = live window onto its reference; `"empty"` = dangling ref); resolution = `RESOLVE='reference'` mode → node resolves `config.ref` via `resolve_address` recursively | render hint `shape:"ring"` (vs `"dot"` for compute nodes) | **BUILT as resolution-mode** (live/empty states authored); `window://` scheme label is **net-new** |
| **expansion-setting** | `RenderMode = Literal["collapsed","expanded","full","workshop"]` | `contracts/node_type.py:10`; `NodeInstance.render_state="collapsed"` `node_record.py:58`; `NodeType.render_set: list[RenderMode]` `node_type.py:28`; affordance `Capabilities.openable:bool` `ui_info.py:54`; "workshop" meaning in `dials/stability.py` | Literal type (upgrade path: file-back the 4 values into `render_modes/<id>.py`) | **BUILT as Literal**; registry-promotion is an upgrade, not a ground-up build |
| **sub-surface** | `ui://` addressing grammar; `panel` kind = a sub-surface slot | `ADDRESS_KINDS=("chrome","field","canvas","panel","ext")` `ui_info.py:163`; `parse_ui_address()` `ui_info.py:194` accepts multi-segment paths (segments past first = sub-surface path); `UiComponentEntry` rows in `UI_REGISTRY`; served `/api/ui_info` | `UiComponentEntry` `ui_info.py:58` | **BUILT** (addressing). Formal sub-surface-as-typed-registry-row (`UiPanelSlot` w/ `slots[]`) is net-new |
| **decision** | `decision://` (DESIGNED) — today an inbox item typed by `action_class` | designed in `DECISION-SURFACE-BUILD.md:24`; today surfaced via `surface_review()` `suite.py:7230` / `defer_offer()` `suite.py:7261`; kind declared `kinds/raw.py:36` (`"decision"`), siblings `approve`:37, `resolve`:38; runtime surface shape `SurfacedItem={id,prompt,choices[]}` `contracts/tools.py:294-315`; verbs `ListSurfaced` `tools.py:460`, `ResolveSurfaced` `tools.py:464` | designed schema: `{id, address, meaning, options[], explanation_source, state(pending\|decided), decided_value/by/at, scope}` | **DESIGNED-not-built** — no `decision://` in SCHEMES, no `Decision(BaseModel)` in contracts/, no `DecisionRegistry` / `decisions/` dir, no `_CORPUS_REGISTRIES` entry |
| **option** | `option://` (DESIGNED) — `CoaOption` is the live model | `CoaOption(BaseModel)` `suite.py:111`; `CoaFraming` `suite.py:117`; vi-visual `:::options` directive renders the cards | live: `CoaOption={label, description, recommended}`; designed canonical: `{label, description, implication, recommended}` (`DECISION-SURFACE-BUILD.md:25`) | **Schema BUILT** (CoaOption); promotion to `option://` scheme + `options/<id>.py` registry is net-new |
| **decision-card** | `archetype://decision-card` (DESIGNED) — a RENDER-type | pattern proven in vi-visual `MODE_CHROME` (`{mode→{panels:[],chrome:[]}}`); `:::options` directive IS the renderer; **distinct from** `THOUGHT_SHAPES` `suite.py:2385` (5 cognitive archetypes — that governs how an agent wave fires, NOT surface render) | designed: `{type_match, render_kind, directive, fields_map}`, `render_kind="slide"` | **DESIGNED-not-built** — surface archetype registry (`archetypes/<id>.py`) is genuinely absent; the MODE_CHROME pattern exists but no formal registry |

**Provenance** every addressed item carries: `Provenance(BaseModel)` `address.py:132` = `address, content_hash, type, produced_by, inputs, agent, created_at, schema_ver`.
**Schema-additive law:** `SCHEMA_VER` on every contract (`ui_info.py:40`=v2, `node_record.py:19`=v2); new fields optional-with-defaults; breaking change = new versioned shape side-by-side, never edit-in-place.

**The single resolver** all of this flows through: `resolve_address(store, addr, *, turn_id, on_missing)` `cognition.py:842` → `contracts.address.scheme()` → dispatch. `SCHEMES` (16/17) `address.py:129`: run·cas·blob·vec·ui·code·skill·context·session·cap·board·clone·mind·exchange·file·project·(vi-vision). 9 resolvable today. Bare names → `BARE_NAME` sentinel. Unknown scheme → raises (fail-loud).

---

## 2. Per-Dimension: REUSE / EXPAND vs BUILD

### A. v-slot-socket (the V's expansion machinery)
**REUSE (extend in place):** `mountConnection()` `connection-mount.js:71` (teardown, `OPEN` WeakMap toggling :47, repositioning, MutationObserver orphan guard, choreography, selection contract — all verbatim); `renderDefinition()` (called `connection-mount.js:150` — the universal child renderer, zero changes for all 4 expansion modes); `setSocket()` `factory-ops.js:212` (composition/value classify + off-architecture guard :233; connection object survives merge at :295); full Supabase circuit `component-store.js` (`resolveComponent`/`saveComponent`/`subscribeComponents` — JSONB carries any connection shape, SELECT-then-UPDATE/INSERT handles the COALESCE index, Realtime broadcasts changes); `CONNECTION_CSS` `connection-mount.js:277` (token-only choreography); `describeParts()` `factory-mount.js:1181` (already returns `connection` per socket); `visual_dev_cascade_rules`+`cascade.js`.
**BUILD (net-new):** `expansion-handlers.js` (new, runtime/renderer/) — typed registry `'resting'|'radial'|'window'|'sub-surface'`; **`connection` property in `component.schema.json` sockets :77-103** (the ONLY required schema change — currently rejected by `additionalProperties:false`); CSS classes `vi-conn-window`, `vi-conn-sub-surface`, `vi-conn-resting`.

### B. mode-colour (whole-UI primary-token cascade)
**REUSE (wire only):** `palette.js` THEMES/STATE_MAP/`resolveStateColor`/`paletteCssVars` — complete registry+resolver, import don't rewrite; `DNA.injectVars` `surface.js:74-102` (root-var write mechanism — extend, don't replace); `setState()` `brand-icon.js:133-160` (already calls `resolveStateColor` :137 — one added `setProperty`); `paletteCssVars()` output `palette.js:69-75` (precomputed 19-theme registry).
**BUILD (net-new):** the CSS token **`--vi-mode-primary`** itself (does not exist anywhere); the event listener in `RightHand.tsx` (company V is a static `<img>` `:414` today — zero state); the gold unification decision (see §3).

### C. archetypes-atomic (DNA / archetypes / atomic-composition / token-merge)
**REUSE/EXPAND:** `engine/resolve.mjs` (zone/space/type px resolution, complete); `DNA.injectVars`+`DNA.injectSpace` `surface.js:74,339`; `DNA.resolve` `surface.js:370` (colour+type resolve now); `DNA.space` `surface.js:319`; `DNA.splitRatio` `surface.js:415`; `DNA.story` `surface.js:217`; `DNA.control` `surface.js:254`; `dna/layouts.json` (8 archetypes typed — consume as-is); `dna/molecules.json#slot_bindings`; `dna/types.json#edges` (18+ typed); `dna/organisms.json` (11 live generators on `DNA.org.*`); `sync-gallery.mjs`.
**BUILD (net-new):** **the generic archetype compositor** `composeArchetype(name, content, ctx)` (~150-200 lines, new `ui/archetype-view.js`) — the single most load-bearing piece; proven by `renderUnit`/`renderPiece` (`unit-view.js:64-67` explicitly names it the next step) but no generic compositor exists (confirmed by grep — no file reads `layouts.json` at runtime); Company `warmth_anchors` block in `design/_system/tokens.json`; space bond-count grounding in `grammar.json#scales.space.bonds.levels`; **6 null organism generators** (process_steps, stage_cards, branch_tree, time_tree, porthole_row, updown_duo — `generator:null` confirmed gaps); register-dial wiring to the compositor.

### D. sequences-stories-slides (sequences / stories / decisions-as-slides)
**REUSE (wire only):** `DNA.story.cut(tree,tier)` `surface.js:230-242` (the walk — zero changes); `dna/sequence.json` narrative_roles+dial_envelopes+`content_role_map`+`generation_ladder` (8 stages = "the progressive wizard's spine = Intent→Proposal→Approval→Execution"); `DNA.renderUnit` `unit-view.js:15` (accepts `{super,title,prose,meta}`, designed multi-source); `DNA.veeCorner`+`DNA.mark` `unit-view.js:131`/`surface.js:276` (verdict mark = approve/reject); `DNA.surfaces`+`injectVars`; `ListSurfaced`/`ResolveSurfaced` `tools.py:460-467`; `content/stories/workshop.json` (reference tree).
**BUILD (net-new, thin):** `decision_to_node(item:SurfacedItem)→StoryNode` normalizer (~30 lines, the ONLY new logic — field-rename + role-lookup via `content_role_map`); a `decision` arc in `sequence.json` arcs (data, not code: `argue(1)+show(1-3)+prove(0-1)+plan(1)+close(1)`); **the live slide renderer** (BACKLOG ★★ "missing rung" `docs/BACKLOG.md:115`, ~100-150 lines wiring — decision-slides RIDE this, not a parallel pipeline).

### E. gallery-app (the instrument shell)
**REUSE:** `DNA.gallery.register(id,{init(ctx){}})` `core.js:9-17`; `DNA.rooms.register({...})` `shell.js:13`+`CONTRACT.md` (Bench/Map/Almanac are copy-from instances); `feedback_server.py:38` (`DNA_FACES` derived from `os.listdir('dna/')` — drop a `dna/<name>.json`, it's served, no edit); `DNA.splitPane`+`DNA.pinchZoom` `surface.js`; `DNA.story.cut`+resolver+`drawer-layouts.js`+injectors (the composition parts); `dna/application.json#components`+`DNA.control`; `content/stories/*.json`+`content/index.json`; 7-proof engine `engine/rebuild.sh`.
**BUILD (net-new):** the live-composed work renderer (the project's own telos — "the work finally DERIVED not PLACED", static iframe today, verified byte-identical on archetype change `BACKLOG.md:113`); content trees for the 73 static pieces; the polarity face (`dna/polarity.json`+`inverts-to` edge+`{magnitude,sign}` tokens); field-field edges in the type system; bond-count authoring surface; the `~/.vi` fleet commons (designed, nothing written).

### F. channels-integration
**REUSE (no new infra):** full `cc_channels.py` runtime (handle registration, transport dispatch, presence, mail log, named registry `:459-549`); full `session_channels.py` runtime (`fold_channels`, `post_to_channel` `:468`, `member_statuses`, `channel_history` `:617`, `edges_for` `:642`); `cc_attachments` runtime+MCP (the channel context assembly point — sessions/docs/recall_scope); `corpus.py`+`mcp_face/tools/corpus.py` (embed `:8007` pplx-embed-context-v1-4b dim 2560 / rerank `:8008` jina-v3 CPU); `session_recall` (8 lenses); `operator_memory.py` (the one already-ambient memory); `BRIDGE_ROUTES` pattern `bridge.py:45-112`; `run_turn` `ui_claude_session.py`.
**BUILD (net-new):** `op="recall"` branch in `mcp_face/tools/cc_channel.py` (**the 5th wire** — contract fully written `CHANNEL-LAYER-SEAM.md §4`, code branch absent); corpus-capture hook in `post_to_channel` (intent declared `session_channels.py:20`, emit call not there); `_chat_context()` extension `suite.py:2975` (channel_state block + channel verb); routes `/api/channels`, `/api/channel/history`, `/api/channel/recall`; channel panel component; builder self-registration as a `cc_channels` member.

### G. resolution-spine
**REUSE:** `resolve_address()` `cognition.py:842` (THE dispatcher — never build parallel dispatch); `_CORPUS_REGISTRIES`+`_write_registry_file()` `suite.py:360/9840`; `CoaOption`/`CoaFraming` `suite.py:111-122`; `ModeSpec`+`MODE_REGISTRY` `suite.py:155/2138` (nothing to add for mode); `surface_review`/`defer_offer`/`revive_offer` `suite.py:7230/7261/7301`; `UiComponentEntry`+`parse_ui_address`+`ADDRESS_KINDS` `ui_info.py:58/194/163`; `RenderMode`+`render_state` `node_type.py:10`/`node_record.py:58`; `Provenance` `address.py:132`; mark-type live/empty `suite.py:257-264`; vi-visual `:::options`+slide pipeline; `MODE_CHROME` pattern.
**BUILD (net-new):** `"decision"` in SCHEMES + `decision://` resolver branch; `Decision(BaseModel)` in contracts/; `DecisionRegistry`+`decisions/` dir; `"archetype"`/`"decision-card"` scheme + `archetypes/<id>.py` dir (NOT THOUGHT_SHAPES); `"decision"` entry in `_CORPUS_REGISTRIES`; `window://` scheme label + resolver branch.

### H. operator-surface + RHM
**REUSE/EXTEND:** `runtime/projection.py:project`+`BindingRegistry` (9 live bindings — every new surface is a `bindings/` row); `runtime/projections.py:ProjectionRegistry` (every new space a `projections/` row); `cognition.py:resolve_address:842` (one branch per new kind); `RightHand.tsx` (V shell BUILT, commit `3ac24f3` — backends wire to existing `rhm:verb`); `territory.py:territory_for`+`territory_prose`; `ui_claude_session.py:run_turn`+`PANEL_BRIEFING`; `decision_memory.py:recall_for_decision`; `implement.py`+`suite.dispatch_decision` (Group W, proven `tests/wire_commit_acceptance.py`); `kinds/raw.py:KIND_META`+`nodes/_meta.py`; `surface/app/src/toggles/` (SpaceChip/LensChip pattern); `runtime/scale.py`; `bridge.py:_claude_stream`.
**BUILD (net-new):** **the MAKE keystone router** (~1 function: `gallery:direction{do_this} → isWritable → run_turn → POST /api/territory/write(kind=generated) → gallery:rerender` — joins 6 built pieces, spec `SPEC-direction-to-generate-wire.md`); the 5 V-verb backends (`/api/rhm/<verb>` routes — emit side `rhm:verb` already built); arrangement-template registry (`templates/` dir mirrors `bindings/` — "no modes, only resolution"); nucleation→axis ratification path; parallax binding (`bindings/parallax.py`); tutorial auto-open.

---

## 3. Mode-Colour → Primary-Token Cascade (FOUND, with files)

The mechanism exists in pieces across the stack; the missing piece is one named token. **This is resolution, not restyle** — no class toggled, no `!important`, no specificity war; every consumer resolves through one var.

**Built pieces:**
- **Palette registry (type + resolver — built):** `palette.js` — `THEMES` `:16-40` (19 themes, `classic-gold`=`#E3C421`/`#BD922B` `:20` = "THE company gold"); `STATE_MAP` `:46-53` (idle→slate-blue, tool-use→classic-gold, thinking→soft-mauve, error→soft-coral, success→sage-green, launching→warm-bronze); `resolveStateColor(state)` `:62-66` (**the mode→colour resolver**); `paletteCssVars()` `:69-75` (emits `--palette-<name>-primary/-accent` for all 19 — the preloaded registry).
- **V-icon tinting (built, narrow):** `brand-icon.js setState()` `:133-160` calls `resolveStateColor` `:137`, writes `--vi-icon-color`+`.color` `:141-142` — **icon-only** via currentColor.
- **DNA root cascade (built, gold-constant):** `DNA.injectVars(target,tokens,warmth,polarity)` `surface.js:74-102`; `:90` `s.setProperty("--gold", c.accent.gold)` — gold held FIXED, no mode concept.

**The cascade spine to build (6 steps):**
1. **Name `--vi-mode-primary`** — the single anchored CSS var for the active mode's primary; on `:root` (or `.vi-app`). idle/normal = `#E3C421`. All accent consumers using `var(--gold)`/`var(--acc)` reroute to it.
2. **Use `paletteCssVars()` as the preloaded registry** — mode change = single reassign `root.style.setProperty('--vi-mode-primary', getTheme(name).primary)`. No new hex.
3. **Extend `setState()` `brand-icon.js:133-160`** — add `document.documentElement.style.setProperty('--vi-mode-primary', colors.primary)`. The V becomes the modes-setter; icon stays icon-tinted AND whole surface cascades.
4. **`DNA.injectVars` reads it** — `surface.js:90` becomes `var(--vi-mode-primary, #E3C421)` so `injectVars` writes primary and `--gold` resolves from it (the `||#E3C421` fallback means nothing breaks without the mode system).
5. **Wire the company V `RightHand.tsx`** — add a `processingState` listener (via `window.forkVBrain` / `vi:state-change`): `resolveStateColor(state)` → write `--vi-mode-primary`. One `useEffect` + one listener (today the company V is a static `<img>` `:414`, zero colour logic).
6. **The cascade** — every CSS rule reading `var(--vi-mode-primary)` re-tints: buttons, chips, active states, V icon, axis gold-stop. Resolution not restyle.

**Two setters, one token:** AI processing state → `STATE_MAP` → `--vi-mode-primary`; manual operator choice → full `THEMES` (19) → `--vi-mode-primary`. (Tim: "Normal is gold, others from the palette of composition.")

**⚠ CONFLICT — GOLD DRIFT (must resolve):** "normal=gold" resolves to THREE hexes for one named role:
- `palette.js:20` = `#E3C421` — **registry-of-truth** (per its own docstring)
- `brand-icon.js:35` fallback = `#D4AF37`
- `company/design/_system/tokens.json:8` = `#e6ab5c` (warmer ochre)
**Resolution:** `#E3C421` is canonical. Update brand-icon fallback `:35`; either align company tokens `:8` to `#E3C421` OR consciously treat the company dark instrument's warmer ochre as a deliberate second identity — a design decision, but one consciously-chosen value, not three by accident. (Note: the company token world differs from DNA by **hue angle**, not lightness — NOT a polarity-dial inverse; merging is real work.)

**⚠ CLAIMED, NOT VERIFIABLE HERE:** Noticeboard `item-534ef183:29,42` states "the V IS the mode-token handle; `--vi-mode-primary` on `.vi-app`, verified" and "the mode-cascade dials — THIS IS BUILT." Exhaustive grep for `--vi-mode-primary` across all .js/.ts/.css/.html under `/home/tim` found ONLY the workflow research-target script; the composition runtime (`overlay/src/components/factory-mount.js`, `runtime/factory-ops.js`) and the `.vi-app` scope are **not present in the accessible filesystem**. Label: claimed by the composition session, composition runtime not accessible here — do not treat as built.

**BEYOND the cascade:** make mode-colour a 5th NAMED grammar dial (`grammar.json:396-404` already has `modality`/`polarity`; `DNA.dialsFor` `surface.js:297-299` would discover it); mode as a SCOPE not just global (override relation `grammar.json:232-240` — `injectVars(target,...)` `:76-77` already accepts any element, so a subtree in "thinking" while global is "idle"=gold is architecturally free); `paletteCssVars()` as a build artifact (`palette-vars.css`).

---

## 4. How the V Hosts Nested Sub-Surfaces / Windows (expanded slot/socket)

**Two views of the SAME thing** — the composition runtime (v-slot-socket) and the company backend (resolution-spine `window://` + `ui://` panels). They meet at the data (a socket's `connection` binding ≡ a `ui://panel` sub-surface address ≡ a `window://` reference node).

**The relational primitive (Tim's "identify once, reuse everywhere"):** `parentLeap` (boolean) is the embryo of an `expansion` type discriminant. Today it distinguishes exactly two behaviors — `radial_menu` (parentLeap omitted→true, the radial mode: parent gains `vi-conn-parent-open`, scale 1.35×) and `orchestration_panel` (`parentLeap:false`, parent NOT elevated, child covers origin). Replace it with a typed field:

```
socket.connection.expansion: 'resting' | 'radial' | 'window' | 'sub-surface'
```

dispatched in `mountConnection` (`connection-mount.js:~114`) to a handler registry keyed by the tag:
```
const handler = EXPANSION_HANDLERS[binding.expansion ||
   (binding.parentLeap === false ? 'window' : 'radial')];   // backward-compat fallback
```
- **resting** — child persists minimized near anchor, no leap/choreography until interaction
- **radial** — current behavior: `vi-conn-parent-open` 1.35×, child at `radius` (`connection-mount.js:93-107`, clamp(max(70, anchorSize×0.675+34))), arc configurable (`expansionParams.arc_start/arc_extent`)
- **window** — parentLeap:false, child fills viewport-anchored region (fixed-position, `expansionParams.size:'fullscreen'|'half'|'quarter'`), class `vi-conn-window`
- **sub-surface** — child embedded as a nested registry component inside the V's own DOM region (`expansionParams.slot` names the insertion zone), via `renderDefinition` into a named zone (not a floating layer)

**RECURSIVE NESTING IS ALREADY LATENT:** `mountConnection` renders the child via `renderDefinition()` `connection-mount.js:150` — the SAME universal renderer used everywhere. The child is a full registry organism with its own sockets and connections. A sub-surface child can itself have a socket whose `connection` mounts ITS child. **V → radial-wheel → nested-option-surface → detail-surface is structurally available today, with zero mechanism changes** — it is the composition law running recursively.

**Full expansion resolution circuit (how expansion-settings resolve from socket DATA):**
```
visual_dev_component_registry.definition (JSONB)
  → sockets.<name>.connection.expansion
  → resolveComponent(id,{supabase,userId,projectId})  [cascade: user→project→global, strategy from visual_dev_cascade_rules]
  → winning row's connection.expansion read by mountConnection
  → dispatched to typed handler
  → handler renders child via renderDefinition()  (same universal renderer)
```
Expansion mode is a DATA field travelling the same cascade as any other socket property — a user-scope row overrides HOW (window vs sub-surface) without touching WHAT (the child component address) and without touching the global V definition. `subscribeComponents()` Realtime means every open session sees a new expansion setting immediately on save.

**The backend twin (resolution-spine):** a `window://<node-id>` reference node resolves `config.ref` via `resolve_address` recursively (the two states already authored as mark-type rows `suite.py:257-264`). Sub-surfaces are `ui://chrome/inbox/build-review` multi-segment addresses (`parse_ui_address` `ui_info.py:194`), dispatched by `kind=panel`. The V's `gallery:verb` event (`App.tsx:190`) is ONE verb-envelope across ALL sub-surfaces — the verb's `address` field carries the `ui://` target; no per-surface verb wiring. The V stays ONE mechanism across nesting.

**The ONE required schema change:** add `connection` to `component.schema.json` sockets `:77-103` (relax `additionalProperties:false`). Without it, any validation pass strips/rejects the connection object. The connection schema formalized: `{child, trigger, choreography, collapse, effects[], selection, closeOnSelect, parentLeap, expansion, expansionParams?}`.

**BEYOND:** expansion as a separately-addressable registry type (`expansion_mode_registry` — change HOW the orchestration panel opens independent of WHAT opens); `expansionParams` as typed sub-schema keyed by kind (radial:`{arc_start,arc_extent,item_count}`, window:`{size,position,backdrop}`, sub-surface:`{zone,size_ratio}`); `accepts[]` extended to gate by expansion compat (`['component.organism.*','expansion:radial']`); choreography as cascade-resolvable address (`material://animation/window-slide-up`); `selection:'write-to-slot'` for sub-surfaces; expansion resolved FROM decision-state (a `decided` decision auto-expands its artifact, `pending` collapses to summary).

---

## 5. Channels-Integration + RHM + Common-Memory Shape

**⚠ THE PRIMARY ARCHITECTURAL GAP — two un-unified channel stacks:**
1. **cc_channels** (`cc_channels.py` + `mcp_face/tools/cc_channel.py`) — the LIVE-INJECTION transport. Handle-based members (`.data/channels/<handle>.json`), durable mail `_mail.jsonl`, thread map `_threads.json`, own named-channel registry `:459-549`. Two transports per-member: `transport="channel"` (HTTP POST to member port) and `transport="supervised"` (supervisor `/inject`, nonce-gated watcher `:173-267`). This is the hand-launched interactive CC session fabric (handle+port).
2. **session_channels** (`session_channels.py` + `mcp_face/tools/channels.py` + `channel_act.py`) — the FABRIC registry (Session Fabric R2.2-R2.5). `session://`-based, log-is-index fold over `agent_sessions/channels.jsonl`, CQRS split (channels reads / channel_act writes), two modes (direct|conducted), two postures (awake|listening). `post_to_channel` `:468-562`, `channel_history()` `:617`, `edges_for()` `:642`. Header `:20`: "exactly the rows a future heart ingests" — a design-intent declaration, NOT a built wire.

BOTH define create/add/remove/archive; serve different session models; **there is NO unification layer** (`cross-session-unified-transport.md` unifies channel|supervised WITHIN cc_channels, not cc_channels↔session_channels). This unresolved seam is the gap — do not smooth it.

**The unification the build proposes:** one TYPE, two transports, resolved per-member. `GET /api/channels` returns `{cc_channels:[...], session_channels:[...]}` differentiated by a `transport` field (`"live-injection"` | `"fabric"`).
```
Channel { id, transport, members[], attachments[], history[], recall_scope[] }
Member  { handle|session://, status(live|idle|absent), posture(awake|listening) }
```
Everything is a projection over existing append-only leaves — no new state, no new indexes.

**The 4 seams, built in dependency order:**
1. **5th wire — channel-scoped recall (memory wire):** add `op="recall"` to `cc_channel.py` (params `channel, query, k=8, rerank`). Resolve attached sessions via `cc_attachments(op=manifest)` → `session_recall(session=each, op="find", query)` (D-1 structural-axis filter — the session set IS the scoping axis) → merge+rank → optional jina-v3 rerank `:8008`. Fail-loud on no attached sessions. Contract fully written `CHANNEL-LAYER-SEAM.md §4`; no `op="recall"` branch exists today.
2. **Corpus capture on channel post (common-memory wire):** in `post_to_channel` `:468`, after delivery, `suite.put_corpus_record(source_address=f"channel://{cid}/{msg_id}", output=message, kind="channel.post", lineage={session,round,project})`. Emits `CORPUS_EVENT_KIND="corpus.record"` → posts embeddable within one sweep. This is the wire `session_channels.py:20` declared as intent. Adds `channel://<cid>/<seq>` as a first-class source scheme alongside `exchange://`.
3. **RHM channel awareness (surface brain wire):** extend `_chat_context()` `suite.py:2975` (assembles the RHM's ground truth per turn — today: graph nodes, recent events, model lists, presence, RHM verbs, inbox escalations, graphs, panels; **NO channel rosters/history/cross-session recall/corpus hits**) with a `channel_state` block (open channels via `fold_channels`, `member_statuses`, recent `channel_history`); add a channel verb to `RHM_VERBS`; add `/api/channel/history` + `/api/channel/recall` to `BRIDGE_ROUTES` (`bridge.py:45-112`, copy the `/api/corpus-query` `:91` shape). NOTE: `bridge.py` BRIDGE_ROUTES has ZERO channel routes today; only `/api/resolve` `:2643` (the OPERATOR approval sink, unrelated).
4. **Surface panel (operator surface wire):** channel list → roster w/ live statuses → history stream → recall input. The builder session (`run_turn` `ui_claude_session.py:101` — a real `claude -p --permission-mode plan --mcp-config` company-face subprocess) registers itself as a `cc_channels` `transport=channel` member on start, becoming a first-class participant (the recursion: the surface's own brain joins the fabric it displays).

**Common-memory stack (the shape):** `corpus.py` (lineage gate `(source_address, output, kind, lineage=(session,round,project))`, exchange identity `exchange://<sid>/<i>`; embed `:8007` pplx-embed-context-v1-4b dim 2560 cosine; rerank `:8008` jina-v3 CPU); `session_recall` (8 lenses, `session="self"` resolves own transcript — NOT a channel_history source today); `operator_memory.py` (`(id,rule,why,evidence,status)`, status=confirmed shared across RHM/crew/all MCP agents — the ONE already-ambient memory); `cc_attachments` (binding registry `channel-memory/channel_attachments/`, `op=manifest` projects sessions/docs/recall_scope — the CHANNEL CONTEXT ASSEMBLY POINT already built); `decision_memory.recall_for_decision` (cross-space semantic + jina-v3 rerank over DEFAULT_DECISION_SPACES = common_knowledge·principles·worldview·topics·history·repo). Today `channel_history` `:617` does `store.put_content(body)` CAS blob, NOT a corpus.record — channel exchange is NOT captured into the corpus (seam #2 fixes this).

**RHM ↔ surface:** the RHM brain `/api/chat` and the builder panel `/api/claude/turn`→`run_turn` are two DISTINCT surfaces. Enriching the V's "Ask" panel: thread `decision_memory.recall_for_decision(aim)` into `territory_for`'s `context_items` leg → every "Ask" gains TEMPORAL depth (prior conversations, principles, related sessions) — address stays the same, brain gains the corpus.

---

## 6. The BEYOND List (what's needed/possible past the spec — maximal, grouped)

**B1 — The surface edits/grows itself (self-build closure)**
- The MAKE keystone: retarget the MAKE verb at `mode://<id>` → Tim ADDS A MODE by speaking to the RHM; the interface builds its own modes via the SAME circuit it renders with (one `MODE_REGISTRY` row via `_write_registry_file`, zero screen-code).
- **Decisions are type row zero:** once `decision://` proves address→type→archetype→render→take→write-back, the SAME chain renders code-units, DNA-tokens, factory-archetypes, session-minds — "whole interface by adding type rows, zero new screen-code" becomes true for EVERY domain. The decision surface is the TEMPLATE that proves the engine.
- **Nucleation → axis-birth → learning:** `bindings/by_nucleation.py` (built — items pile out when they don't fit; 20/80 water-law surfaces candidates). When a `born` event fires, prompt Tim to RATIFY a new axis → gate-ratified row insertion → new angular geometry the next render uses. Tim's FOUR ROOT AXES formalized by forbidden-zone pressure, not manual declaration. Surface: a NUCLEATION LENS PANEL inside the V's "Make."
- **Decision-kinds beyond build:** the `implement.py` wire (AUTO/CONFIRM/SURFACE/LOCKED postures, exactly-once `decision.dispatch`, git-checkpoint, `build_result_review` item) generalizes to config-change, role-change, model-swap, schedule-change, annotation-policy-change. The V's "Drive" verb = governed propose→confirm→act for ANY system parameter. One circuit, every change-kind.

**B2 — One resolve, many surfaces (every future view = one binding/template row)**
- The Planning Surface (`center=future://goal/<id>`, `radius=semantic distance to goal` — "the distance between present and goal IS the plan").
- The Pollution-Hunt Surface (`center=AI-pole address`, every unit's lean reveals AI-contamination distance — a corpus cleaner AND real-time grader).
- The Graph-of-Minds Surface (D1: sessions-as-units, channel-membership as angle, last-activity as radius — NEAR-UNANIMOUS "FOLD IN", a `bindings/by_session_graph.py` row).
- The Remembering Surface (`project(center=cas://<past-commit>, at=ISO-past)` — the field AS IT WAS; the `?at=` time scrubber already exists).
- The Parallax/Triangulation Surface (`bindings/parallax.py` — two poles from any registry, every unit by its lean between them = multi-perspective reasoning made spatial; the separator math `?pole_a=`/`?pole_b=` exists).
- The Strain Surface (`bindings/strain.py` — `by_separator` with pole_a=where-it-IS-filed, pole_b=where-it-MEANS-to-be; renders the whole corpus's structural-vs-semantic divergence = coherence at a glance; gap-pressure made visible).
- **No-modes by construction:** `resolve(address × DNA-frame × mode-template) → surface`; a `templates/` registry (mirrors `bindings/`) makes any address renderable as slide/graph/document/dashboard by passing a different arrangement-template — not a mode flip.

**B3 — Bidirectional address / accumulation as memory**
- 256 real unanswered element-bound questions in the snapshot corpus, each an `exchange://` address carrying a "Why?" with no brain loaded = 256 pre-seeded, pre-aimed conversations. Annotation-as-conversation-seed: every annotated element becomes an `exchange://` address that pre-seeds a brain — direction IS a brain handle.
- **Option accumulation as a corpus:** every `option://` Tim ever encountered accumulates; the RHM resolves PAST options as context for NEW decisions — options don't die when a decision is made, they become reusable primitives. The corpus IS the institutional memory of what Tim considered.
- **Decision slides as corpus entries:** `kinds/raw.py:36` already declares `decision`; every rendered slide ingests back as a `corpus.record` with its verdict mark; the RHM recalls "decisions made about X" and resurfaces the slide sequence (introspective data building applied to decisions).
- **Cross-channel memory diffusion:** channel posts as corpus records (`channel://`) → `corpus(op=query)` searches ACROSS all channels — the common company memory IS the cross-channel search surface.

**B4 — Sequences / narrative applied to decisions**
- Decision sequences as traversable walks (`reading_axes`: DESCENT drills to evidence, TRAVERSE steps the decision queue; 3 invariants mean any slice is a valid artifact).
- A `decision` arc type in `sequence.json`; `measure` applied to decisions = partial approval (approve options 1+2, defer 3, multiple `ResolveSurfaced` against one id).
- The V corner as decision-action rail (drill=descend to evidence, mark=approve, ask=more context, source=trace to surfacing node — no new verbs).
- Progressive wizard via `generation_ladder` (8 stages = "Intent→Proposal→Approval→Execution applied to design"); each stage a Vi-Chat wizard step; converges with `plan-wizard-redesign.md`.

**B5 — DNA / composition completion**
- Complete dial closure (warmth re-tints, density re-spaces, register swaps eligible archetypes, polarity inverts grounds — all WITHOUT re-rendering the DOM, just re-injecting CSS vars).
- Scale-tier multiplier at compose time (`grammar.scale_tiers`: poster×2.0 … component×0.5 — same archetype record renders at any scale; "any part is a whole" becomes mechanically provable).
- The narrative walk as compositor content source (`DNA.story.cut(tree,tier)` → archetype names → `composeArchetype` → injectors → live-themed DOM; no bespoke render per story).
- Substrate-addressed organism injection (resolve organisms by generator key from the record — add to JSON registry, available to any accepting slot).
- The Company token bridge as a polarity proof (Company dark theme as a 2nd "identity" — same engine, different `warmth_anchors` — proves "derive-never-place" at the identity level).
- The 6 null organisms (process_steps, stage_cards, branch_tree, time_tree, porthole_row, updown_duo).

**B6 — Type-system / spine deepening**
- The polarity / signed-axis face (`{magnitude,sign}` depth tokens, `inverts-to` symmetric edge, magnitude-preservation invariant, twin-piece demo) — the equal-opposite law arrived 3× independently.
- Field-field edges (the type system has registries/types/17 edges; NOT YET field↔field — "fields with fields and so on" — makes the typed graph queryable at field resolution).
- Bond-count tuning (`grammar.scales.space.bonds.levels` `{0.5,1,2,3,5,11}` are seeded candidates; Tim retunes, every gap of that bond type re-resolves estate-wide — the authoring step that turns the spacing mirror into the real vocabulary).
- The `~/.vi` fleet commons (project registry, conventions-of-record, laws-commons port, letters/post-office, the Tim layer — designed in Packet 01, nothing written).
- Colour as resolved meaning-field (a pending high-stakes decision's `state`/`scope` resolves to a colour-token tinting the operator's whole visual field — colour as resolved signal, not decoration).
- The window as a time axis (`window://` resolving `run://<turn>` parameterized by `turn_id` → a time-axis slider over decision history; CAS already holds every prior state).

**B7 — V as a two-way dial / surface polish**
- The V becomes a two-way surface dial: "Drive" moves a warmth/density/register dial inside the V → `DNA.injectVars` re-tints the whole app, frame/grammar constant. The mode-token is the V's ARM on the four-axis state. V-as-navigation+ask+annotate AND V-as-live-drive = ONE object, two roles ("an overlord surface = sees AND drives").
- Work-as-hero recomposition / mobile (`DNA.splitPane`+`DNA.pinchZoom` exist; rooms need only compose them; perfect the work treatment then apply to other rooms).
- Atlas in the roombar (not floating — measured 67×12px overlap on mobile); changes-prose disclosure primitive; token-edit undo/redo over the registry with a revert-to-source path; built-in tutorial (Phase-0 pedagogy delivered by the RHM via first-open seeded "Ask" prompt + `PANEL_BRIEFING` extension).

---

## 7. The Seams (the union — the relationships ARE the content)

Each seam = a concrete function/file where two dimensions meet. This is the circuit.

| # | Seam (A ↔ B) | The exact join (file:line) |
|---|---|---|
| S1 | **socket → composition (recursive)** | `mountConnection` renders child via `renderDefinition()` `connection-mount.js:150` — the universal renderer; child is a full registry organism with its own sockets/connections → infinite nesting is the composition law recursing. V → wheel → sub-surface → detail, free. |
| S2 | **socket → Supabase cascade** | `connection.expansion` in `definition` JSONB (`visual_dev_component_registry`) resolves through user→project→global via `visual_dev_cascade_rules`; project-scope overrides expansion mode without touching global V. |
| S3 | **socket → registry validation** | `setSocket()` `factory-ops.js:212` enforces `registry.has(address)` `:233` before any composition write — the child must exist before a connection mounts it. |
| S4 | **socket / window → resolution-spine** | composition's `connection.expansion='window'` ≡ backend `window://<node>` (mark-type `suite.py:257-264`, resolves `config.ref` via `cognition.py:842`) ≡ `ui://panel` sub-surface (`parse_ui_address` `ui_info.py:194`). Same thing, two repos; meet at the address. |
| S5 | **mode-colour → V/RHM (the setter)** | The V IS the modes-setter; `RightHand.tsx` is the listener insertion point; the RHM "drive" verb (`RightHand.tsx:23`) = "the mode-cascade dials" → its handler writes `--vi-mode-primary`. |
| S6 | **mode-colour → DNA tokens (resolve target)** | `dna/tokens.json color.accent.gold #E3C421` is every gold consumer's anchor; aliasing `--gold` = `var(--vi-mode-primary, #E3C421)` (`surface.js:90`) makes every existing gold consumer mode-responsive without touching it. |
| S7 | **mode-colour → composition/palette (data source)** | `palette.js` is shared vocabulary; `brand-icon.js:26` already imports `resolveStateColor` — the data path exists, just not widened from icon-only to root-cascade. |
| S8 | **archetypes → address/substrate** | every `layouts.json` archetype is an addressable TYPE in `dna/types.json`; `composeArchetype(name, ...)` uses the name as a TYPE address routing through `registry-is-truth`. |
| S9 | **archetypes → application.json (screen face)** | `screen_archetype.layout` → `layouts.json` archetype name → compositor; application states (empty/loading/error/success) are REGISTERS that drive dial configs on the same archetype. |
| S10 | **archetypes ↔ sequences (content)** | `DNA.story.cut(tree,tier)` `surface.js:230` returns nodes carrying `archetype` fields → each looks up `layouts.json` → `composeArchetype(node.archetype, node, ctx)`. Stories drive archetype selection drives zone/slot population. |
| S11 | **archetypes → V corner / RHM** | `DNA.veeCorner` `unit-view.js:131` places 5 verb-sockets on every rendered unit; verbs map to `application.json` navigation verbs; the compositor composes the archetype DOM, `DNA.bindVee` mounts the V corner as its interaction layer. The RHM surface is the archetype hosting the V corner as focal slot. |
| S12 | **sequences → company-decisions** | `SurfacedItem {id,prompt,choices[]}` `tools.py:294` (input) + `ResolveSurfaced` `tools.py:464` (output); `decision_to_node` is the only cross-repo bridge — it sits at this seam. |
| S13 | **sequences → corpus/memory** | every rendered decision slide is a `corpus.record` kind `decision` (`kinds/raw.py:36`); the verdict `DNA.mark`(`kind:"verdict"`) attaches to the slide address; RHM retrieves past decisions by kind, resurfaces the sequence. |
| S14 | **sequences → Vi Chat wizard** | the `generation_ladder` (`sequence.json`) = "the progressive wizard's spine"; Vi Chat steps ≡ ladder stages; decision-slide build + wizard-redesign converge here. |
| S15 | **resolution-spine → decision surface build** | `DECISION-SURFACE-BUILD.md` (live commission, Tim 2026-06-17); every declared schema (`decision`/`option`/`decision-card`) maps to a SCHEMES entry + resolver branch — the surface IS the spine's first retarget at real content. |
| S16 | **resolution-spine → fork/keystone wire** | the write-back leg (`territory_write` at `decision://`, state→`decided`) flows through `cas://` → emits `run://` ref; the keystone generate→write→re-render circuit exists; retargeting at `decision://` is the seam. |
| S17 | **resolution-spine → DNA archetype registry** | DNA registers `archetypes/decision-card.py`; resolver reads `archetype://decision-card`; the slide pipeline renders it — DNA + spine share the archetype-registry contract. |
| S18 | **resolution-spine → recollection/common-memory** | `Decision.explanation_source` is an address (`cas://<hash>`) resolved by `resolve_address` through the RHM brain → corpus document → RHM generates explanation text. |
| S19 | **resolution-spine → composition/mode-type** | `MODE_REGISTRY` carries all mode axes; `brain_config` references model loadouts; `resolution` field declares how turns resolve — the mode IS a composition spec. |
| S20 | **resolution-spine → wildcard/verb layer** | the `gallery:verb` event `App.tsx:190` is ONE verb-envelope across ALL sub-surfaces; every new `ui://` sub-surface subscribes to it; the verb's `address` field carries the target. No per-surface verb wiring. |
| S21 | **channels → RHM brain** | `_chat_context()` `suite.py:2975` — injecting `channel_state` makes the surface brain and the channel fabric one cognition layer per turn. |
| S22 | **channels → common memory** | channel posts as `corpus.record` (`channel://` scheme) via the `post_to_channel` `:468` hook → Tim's semantic questions search across all channels (embed `:8007` / rerank `:8008`). |
| S23 | **channels → cc_attachments** | the binding registry IS the channel's memory declaration; the 5th wire's recall scope resolves through `op=manifest`; `attachments[type=session]` IS the D-1 axis filter. No new schema. |
| S24 | **channels → builder panel (recursion)** | `run_turn` `ui_claude_session.py` (a CC session with the company MCP face) self-registers as a `cc_channels` member → the surface's own brain is part of the fabric it displays. |
| S25 | **channels → Session Fabric edges** | `edges_for` `session_channels.py:642` projects the connection graph the Heart traverses; channel posts as corpus records add a message-co-participation edge type alongside mail-exchange edges. |
| S26 | **operator-surface → projection engine** | `runtime/projection.py:project` + `bindings/` + `projections/` + `/api/projection`; the MCP twin `mcp_face/tools/instrument.py:project` ensures agent + operator see byte-identical results. |
| S27 | **operator-surface → fork brain + territory_for** | `territory.py:territory_for` (9 schemes + graph) → `territory_prose` (never raises) → `run_turn` (PANEL brain) / `suite.chat_parts` (FOCUS brain at overlord altitude); scale/rung selects which; seam at `bridge.py:_claude_stream` (`:1691`) where `territory_prose` replaces the ui://-only composer. |
| S28 | **operator-surface → composition legibility + V component** | `bindings/<id>.py meta:{name,is,fills,why}` (seed shape composition validates via `legibility.js:resolveLegibility`); `v-icon.svg` container is the swap seam — the real V organism renders in, verbs emit `rhm:verb`; meet-at-the-data, no cross-repo import. `projection:select` CustomEvent + `GalleryMount.tsx` is the gallery DOM seam. |
| S29 | **operator-surface → address spine + decision/implement wire** | `contracts/address.py:SCHEMES` + `cognition.py:resolve_address:842` (one resolver); `implement.py:launch` + `suite.dispatch_decision` + `surface_build_intent` (one wire, gated, git-checkpoint, `[self-build]`, exactly-once). The MAKE verb routes through this when generative. |
| S30 | **operator-surface → common-memory + decision_memory** | `decision_memory.recall_for_decision` over DEFAULT_DECISION_SPACES + jina-v3 rerank; threading it into `territory_for`'s `context_items` leg gives "Ask" temporal depth; `common_knowledge` (102 pplx-2560 units, growing) is the shared memory every aim draws from. |
| S31 | **gallery → company / fleet commons** | counterpart's `manifest.json` ≡ company's `register.json` (sister machine-registries); `ui://` scheme (company `addresses.json`) + counterpart `dna/address.json` share the address-resolution model; `~/.vi` (`MAP.md §8`) is the cross-repo law-travel mechanism (portable `laws/` sector). |
| S32 | **gallery → Tim as resolver** | the authored half (the cut, the route, bond counts, scope on the live-composed work) is Tim's input, not derivable; the two-halves law is the structural seam; the feedback loop (pin → `POST /api/feedback` → `data/feedback.json`) captures his reactions as persistent state against the piece registry. |

---

**The one circuit (Tim's relational spine), end to end:**
```
Principal → aim (the V, at an address)
  → resolve_address (cognition.py:842, one resolver, 16 schemes)
  → type + registry row (decision·option·mode·window·sub-surface — all rows, not code)
  → archetype:// (decision-card render-type)
  → composeArchetype + DNA.injectVars(--vi-mode-primary cascade) + DNA.story.cut
  → V hosts it (socket.connection.expansion → mountConnection → renderDefinition, recursive)
  → take (verdict mark / MAKE verb)
  → ResolveSurfaced / territory_write(kind=generated) (dispatch_decision wire, git-checkpoint)
  → corpus.record (channel:// + decision kind → common memory)
  → recall_for_decision feeds the next aim
```
One unbroken loop. The relationships are the content; every node is a type that resolves; the surface grows by adding rows.