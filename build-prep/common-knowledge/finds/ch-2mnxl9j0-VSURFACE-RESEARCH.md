# composition (ch-2mnxl9j0) — V-SURFACE research (what exists · HOW · gaps · BEYOND)

Lane: the V slot/socket Supabase system · the mode→colour system · the type-builder / archetype layer.
Method: 4 code-grounded research agents across vi-visual-dev (overlay) + /home/tim/company + counterpart/design.
Date 2026-06-17. Feeds the lead's assembled synthesis for the resolution-first full V-surface.

NET HEADLINE: **the full V-surface is ~70% structurally present in composition's lane.** The connection model
already nests a full organism-in-an-expansion with per-binding settings; the mode→colour rails are all built;
the keystone is composition-generic. The frontier is RECURSION + RESOLUTION + PERSISTENCE, not new grammar:
(1) make expansion-dispatch recursive (nested windows), (2) route the mode signal through the ONE cascade onto
`color.primary` (whole-UI re-resolve), (3) add an optional `archetype` render-layer above the keystone, (4) move
the source of truth from localStorage to the Supabase typed registry. All are continuations of existing laws.

---

## 1 · The 4-layer placement (composition = the TYPE-BUILDER)
THE_FACTORY.md:458-470 (Tim, canonical): DNA=IDENTITY → **FACTORY (vi-visual-dev)=TYPE-BUILDER (registries/types)**
→ GALLERY=where CONTENT+SCENES are made → COMPANY(~/company)=ADDRESS-RESOLUTION+models+substrate. Composition
owns the type-builder + the V's slot/socket grammar + the 6-verb V-corner contract; we author TYPES that RESOLVE,
DNA renders them, the company resolves the addresses.

---

## 2 · V SLOT / SOCKET + SUPABASE  (the surface spine)
THREE distinct composition primitives (do not conflate):
- **SLOTS / composedOf / zones** = child COMPONENT composition, accepts-validated (renderer/slots.js;
  registry.js validate()/register(); atomic ladder atom→[]・molecule→[atom]・organism→[atom,molecule]・
  template→[organism], definition-renderer.js:462).
- **SOCKETS** = addressable VALUE inputs, cascade-resolved, materialised to DOM (v-symbol-sockets.js V_SYMBOL:46
  — 8 sockets; socket-resolver.js resolveSockets:33 → cascade.js resolveCascade:58, scopes global<project<user<
  session<runtime, strategies first-found/merge-deep/append; renderer/socket-materials.js classifyMaterial:62 +
  applySocketMaterials:98 — classifies by address KIND not socket name; JUST SHIPPED + verified by use & sight).
- **CONNECTIONS** = a socket binding holding a CHILD COMPONENT revealed as an emerging sub-surface — **the spine
  of the V-surface vision.** connection-mount.js mountConnection:71 renders binding.child through the keystone,
  anchors it on the parent, applies emerge/collapse choreography + effect tokens, owns teardown. Bindings live on
  the V's sockets (factory-mount.js:91 radial_menu.connection, :106 orchestration_panel.connection). Registered
  connection children already exist: radial-organism.js RADIAL_WHEEL_DEF, agent-orchestration-panel.js AGENT_ORCH_DEF.

THE KEYSTONE: definition-renderer.js renderDefinition:595 — composition-generic (dispatches only on
`definition.component`, the leaf primitive; never on id/screen-name), recurses composedOf/slots/zones, resolves
sockets, applies state-machine + socket-materials, owns the reactive rerender (:705) that makes write-back→
re-resolve a live loop.

PERSISTENCE — **source of truth TODAY = localStorage, NOT Supabase** (the key gap). Table
`visual_dev_component_registry` (migration 20260609_…:8; RLS read scope='global' OR user_id=auth.uid(), write
own-rows; in supabase_realtime publication) is the DESIGNED home — full adapter on both ends + setDurableStore
hook (factory-ops.js:478) — but boot seeds from the bundled V_ROW + hydrateRegistry() reads localStorage
(factory-ops.js:455/545); every save call passes {registry} with NO supabase client → writes only memory+
localStorage. Company-side runtime/vi_vision.py resolve/catalog/write DOES read/write the table for real
(SA-auth, RLS, same scope-cascade as cascade.js). So the loop is plumbed but the overlay's live durability is
localStorage; threading a client through setDurableStore closes it (and joins the AI-side resolver — same row).

GAPS for sub-surfaces/windows/expansions (precise + mechanical):
1. **Trigger-dispatch is V-specific, not recursive — THE gap.** openConnectionFor (factory-mount.js:381) reads
   the V's OWN sockets only → depth ≥ 2 (a window inside an expansion) is unsupported. Lift dispatch into the
   keystone/controller driven by ANY element's def → recursion unlocks (keystone already has a depth guard :606).
2. **Connection binding is not cascade/Supabase-resolved** → per-expansion SETTINGS can't override per scope.
   Make `connection` a structured socket value flowing through resolveSockets+socketOverrides; add a `connection`
   kind to classifyMaterial so it's no longer inert.
3. **Connection STATE not persisted** — binding.selection mutates in memory; visual_dev_ui_state (user-scoped,
   Realtime) exists for exactly this. Persist {openConnections, selections, arrangement}.
4. **One window per anchor** — OPEN WeakMap keyed per-anchor (connection-mount.js:47); key by (anchor,socket) →
   multiple coexisting windows.

---

## 3 · MODE → COLOUR  (the modes-setter; the rails are ALL built, the wire is wrong)
EXISTS: palette.js THEMES (19 themes; classic-gold = company gold #E3C421/#BD922B :20), STATE_MAP (state→theme),
resolveStateColor:62. theme-stage.js dual dark/light + glow vars. tokens.js tokenToCssVar/generateCssVariables;
defaultTokens. **served-cascade.js createServedCascade — the PROVEN whole-UI live re-resolve engine**: setToken/
setTokens → resolveDesignSystem → emit() inline custom-props on .vi-app with diff-removal → all 68 `--color-
primary` consumers re-skin with no re-render; `color.primary` is already in EDITABLE_TOKENS. design-system.js
resolveDesignSystem folds palette→tokens per scope; dna-import.js synthesizeDnaPalette builds a palette from the
DNA accent axis (#E3C421/#BD922B); role-map.js DNA_ROLE_MAP:92 maps `color.primary → color.accent.bronze` so an
external identity re-skins the existing 68 consumers + the V with no per-component edits.

HOW IT WORKS TODAY (the crux): the V's processing-STATE fires tint() (factory-mount.js:637-654) which writes
`--vi-mode-primary`/`--vi-mode-accent` (**2 consumers only**: app-shell.css.js:66 top-edge, :348 mobile tab) +
`--vi-ck-accent` (cockpit). **It does NOT write `color.primary`** → the 68-consumer body of the UI is untouched.
It's an additive parallel layer, outside the resolution-first cascade. The working-MODE organism (pilot/inspect/
dev, organisms.js MODE_SELECTOR) declares colours but is wired to nothing global; the pack modes carry NO colour
(the `mode` cascade rule only gates action availability, providers.js:53).

GAPS: (a) "normal = company gold" is UNMET — the seeded Vi DS has brand_tokens:{} so `color.primary` =
foundation default **#0066ff (legacy blue)**, not #E3C421. (b) mode tint dead-ends at --vi-mode-primary instead
of `color.primary` via served-cascade. (c) the pilot/inspect/dev axis is colour-inert. (d) two writers (tint +
served-cascade) both write inline on .vi-app, unreconciled.

BEYOND (recommendation, all rails exist): route mode selection through `cascade.setTokens('color.primary', …)`
at the runtime scope (merges OVER the DS identity, reverts cleanly) → whole-UI resolves for free; seed the Vi DS
default primary to #E3C421 so normal=gold holds at the source; give each mode a `primary` palette-name field
(composition DATA, derived not hardcoded); unify the STATE tint + the working-MODE organism onto the SAME setter
(the V becomes the visible handle on color.primary). This is "re-point the mode signal onto the proven whole-UI
path + seed the default to gold" — no new engine.

---

## 4 · TYPE-BUILDER / ARCHETYPE / SLIDE  (the resolution-first render layer — the prize)
EXISTS: only the **4 atomic types** (atom/molecule/organism/template; registry.js:331/337). The keystone is
composition-generic (dispatches on definition.component = a leaf primitive; a new decision/option/decision-card
def whose component is Panel mounts TODAY with zero screen-code) — **but there is ONE presentation model (nested
boxes + leaf primitives) and NO render-archetype concept.** Company has TWO per-archetype renderers
(surface/app/public/gallery/unit-view.js renderUnit:24, renderPiece:70) selected by the caller — no
renderArchetype(type,data) dispatcher, no archetype registry. THOUGHT_SHAPES (suite.py:2380) are a cognition
axis, NOT render — do not conflate.

THE RESOLUTION CHAIN (address→type→archetype→render→RHM-explain→decide→write-back→re-resolve, named verbatim in
DECISION-SURFACE-BUILD.md:31): address LIVE for 10/17 schemes (decision:// NOT yet in contracts/address.py:129 —
~15 LOC, identical to vi-vision://); type LIVE; **archetype = the SPLIT seam, no archetype field/registry yet**;
render = JS keystone LIVE + company 2/8 archetype renderers; RHM-explain = decision_memory.recall_for_decision
LIVE; decide = reuse resolve_surfaced/Inbox verdict (the consent record IS the artifact — no new mark);
write-back = write_vi_vision / territory_write LIVE; re-resolve = needs decision://.

LEGIBILITY (legibility.js — composition's meaning lane, built): SEED_LEGIBILITY_FIELDS {name, is, fills, why},
DECLARED-first then inferred-fallback (resolveLegibility:60), so Tim sees MEANING off the row's meta/context,
never machine-names. validateLegibility:84 drafted to wire into registry.validate (a row lacking required meaning
fails loud at birth).

SLIDE/SEQUENCE/STORY: **no slide/deck/carousel renderer exists** in either repo. Closest precedents are
design-only (DNA.story walker referenced not-in-tree; ARCHETYPE_DATA_MAP.md:34 "flows = a sequence LAYER that
ORDERS archetypes"). The liked look (counterpart/design/mockups) is portrait-phone screens in slide layouts: the
DECK (app-flow-full, 5 screens one arc joined by .joint plug) + the EXPLAINER (app-canvas, screen + principles).

BEYOND (the cleanest extend-don't-fork): add an optional **`archetype` field** to a def + an **archetype-renderer
registry** that registers like extra primitives do — `component` names a leaf primitive, `archetype` names a
SURFACE-shaper; absence = today's pure-composition (backward-compatible). Adopt render_declaration.py's proven
**exact→family→bare→UNDECLARED-LOUD** lookup law (:167-188) so an unknown archetype renders loud + records a gap,
never blank. The decision-card archetype reads its labels THROUGH resolveLegibility (meaning, not ids). Model the
SLIDE as a `sequence`/`flow` archetype over an ordered list of addresses, each resolving to a decision-card
instance (renderer built once, slides cheap — renderUnit economics). One keystone, one dispatch model, lifted one
level → decision/option/decision-card/slide become TYPE ROWS that resolve to surfaces.

---

## 5 · THE GALLERY FACE + the 6-VERB CONTRACT (composition-owned)
The FACE = counterpart/design/ (DNA's gallery: ui/gallery/stage.js slide-form, ui/rooms/shell.js rooms-over-one-
canvas, the V-corner, mockups/manifest.json 49+ pieces) + the hosted subset company/surface/app/public/gallery/.
The 6 verbs (THE_FACTORY.md:539-560, composition-owned, ONE `gallery:verb` event {verb,aim_address,payload},
polymorphic over aim type): navigate=move the VIEW to the aim (re-centre); drive=RE-PROJECT (adjust the dial/lens/
MODE → re-resolve — this IS the mode-cascade); open-source=reveal source/def/provenance; ask=talk to the brain;
annotate=leave a mark; generate=the GATED keystone write (enabled only on a WRITABLE address). projection has the
dispatcher live (commit 8e8ef8d); I've confirmed the per-verb semantics to projection + flagged the face-vs-V
z-order seam (point-aim needs DNA's face which sits above the V) as a 3-way design seam.

---

## 6 · THE BEYOND FRONTIER (what's genuinely unbuilt)
- **Nested addressed windows with per-window frame-scoped settings** (the signature element, NOT built): a
  window/sub-surface as an addressed asset (type=surface/window) with its own slots (chrome/content) + sockets
  (nested windows); per-expansion settings = a FRAME sub-scope per window resolved through the cascade (the
  cascade already supports it; the gallery resolves one global frame today). Window-manager = composed assets
  (z-order/focus/dock/float), teardown via the keystone's dispose-cascade, open/close via the existing
  emerge/collapse choreography.
- **Typed decision/story SEQUENCES rendered as slides**: a sequence as an addressed asset on the order/time axis;
  a decision = {pending slide → memory-context slides (RHM) → verdict slide}, all renderUnit-composed, annotatable,
  re-drillable; the .joint plug = the live transition.
- **Channel-native join** (backend built: decision_memory.recall_for_decision, rhm.py, cc_channels.py): the FACE
  has no channel identity yet → bootstrap a v-handle (role:modes-setter); render the recall bundle AS a slide-
  sequence with {source,space,score} provenance; a common-memory feed ROOM beside bench/map/almanac.

---

## 7 · SEAMS (what composition needs / provides)
- ← DNA (ch-ovxwz8k8): the decision-card + slide ARCHETYPE VISUAL (the render), the archetype catalog shape, the
  token-merge (zones/iconography/proportions/layouts/rules). I provide the TYPE + legibility meaning-fields + the
  archetype-field mechanism; DNA provides the look. Meet at the data (no cross-repo import).
- ← fork (ch-8djrpmsl): decision:// scheme + resolve_address branch; the RHM run_turn explain leg; the keystone
  write wire. I co-own the keystone retarget.
- ← projection (ch-piffgfxv): host the surface + the gallery:verb dispatcher (LIVE); resolve the face-vs-V seam.
- ← recollection (ch-83e2cque): common memory INTO the channels as the recall bundle the decision slides render.

---

## 8 · SMALLEST PATH to the prove-on-one (composition's buildable-NOW half)
1. Author `decision` / `option` types + the `decision-card` archetype as TYPE ROWS + schemas (resolution-first).
2. Add the optional `archetype` field + a loud-lookup archetype registry above the keystone (render_declaration
   pattern); wire legibility as the field feeder.
3. Compose ONE real decision-card by hand → render through the keystone → (TAKE = write-back rides GOAL·4's gate:
   lead-restart anon window + Tim SA-authorize).
Parallel low-risk wins that also serve the whole surface: seed default `color.primary=#E3C421` (normal=gold) +
route mode→served-cascade.setToken('color.primary'); thread a Supabase client through setDurableStore (truth →
the typed registry). Build only after the lead assembles + we design; this is research.
