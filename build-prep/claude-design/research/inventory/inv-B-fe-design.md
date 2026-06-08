# FE + Design Substrate Inventory (canvas/, design/, panels/)

**Scope:** Fast mapping of the front-end region (canvas/), the design substrate (design/), and the declarative panels (panels/). Read-only coverage pass — location + apparent purpose, no deep synthesis.

**Date:** 2026-06-08  
**File Count:** 106 files (non-node_modules)

---

## Directory Tree (compressed structure)

```
canvas/
  AGENTS.md                         ← module constitution
  app/
    README.md
    package.json
    vite.config.ts
    tsconfig.json
    dist/
      assets/index-*.css            ← built output
    src/
      main.tsx                       ← React entry point
      App.tsx                        ← F0 shell restructure (carved from 1659-line Hud)
      AppContext.ts                  ← controller exposure
      api.ts                         ← F0 API client (carved, F5 adds error normalization)
      registryStore.ts               ← module globals (6 globals → 1 external store)
      NodeShape.tsx                  ← generic node shape + Edges + loadGraph
      useAppController.ts            ← F0 state container (all former Hud state + handlers)
      app.css                        ← regional styles
      components/                    ← reusable presentational blocks
        kit.tsx                      ← WAVE-2 DESIGN: shared vocabulary (SectionHead, LaneHead, Badge, Surface)
        ShapeHow.tsx
        BlastRadiusReach.tsx
        BuildIntentCard.tsx
        ContextBundle.tsx
        NodeConfigForm.tsx
        PanelErrorBoundary.tsx       ← per-panel error boundary
        PanelView.tsx
        WireRequest.tsx
      regions/                       ← carved presentational surfaces (F0 deliverable: CSS grid shell)
        Toolbar.tsx                  ← F0 command strip (run·wire·portal·delete·layers·fit·reload)
        Palette.tsx                  ← layer palette
        Inspector.tsx                ← node inspector
        Inbox.tsx                    ← decision/build queue (exemplar for kit adoption)
        Grow.tsx                     ← growth surface
        OpPanels.tsx                 ← operational panels
        Activity.tsx                 ← activity log
        RhmChat.tsx                  ← RHM chat interface
        Walkthrough.tsx              ← guided walkthrough
        Workshop.tsx                 ← workshop mode
        Settings.tsx                 ← settings panel
        History.tsx                  ← operation history
        Fleet.tsx                    ← fleet/swarm view
        CognitionView.tsx            ← cognition layers view
        SelfChanges.tsx              ← self-modification tracker
        Versions.tsx                 ← version management
        AddressHelp.tsx              ← ui:// address help
        ProposeAffordance.tsx        ← proposal interface
      extensions/
        AGENTS.md                    ← extensions constitution (LIVE docs)
        live_clock_widget.tsx        ← example extension

design/
  CLAUDE.md                         ← folder's keeper charter + boot sequence
  README.md
  conventions.md                    ← mockup corpus org + token/address systems
  design-system.css                ← GENERATED (never edit): tokens.json → emit.py → this
  register.json                     ← production contract (views·variants·features·journeys·coverage)
  CONNECTION-CONTRACT.md            ← ui://<region> ↔ code seam specs
  _system/
    emit.py                         ← tokens.json + components.css → design-system.css
    parse.py                        ← mockups + addresses.json → element-map.json
    check.py                        ← structural coherence + design-lint (free, no models)
    refcheck.py                     ← code-ref drift validator (resolves code: refs against live source)
    symbols.py                      ← reverse index of code: refs → code-symbols.json
    codeedges.py                    ← structural code dependency graph → code-edges.json (sym→sym)
    components.css                  ← template (reference var(--x))
    tokens.json                     ← THE source of truth for the look (WARM gold theme, GOLD-PRIMARY)
    addresses.json                  ← THE ui:// address registry (every ui://<region>/<element> → caps/code)
    mechanisms.json                 ← Layer-0: corpus-analysis mechanisms (extend-by-registration)
    element-map.json                ← GENERATED: element ⇄ address ⇄ feature ⇄ code + orphans (bidirectional)
    check-report.json               ← GENERATED: hardcoded→token candidates, coverage gaps, orphans
    refcheck-report.json            ← GENERATED: code: ref drift (refs that no longer resolve)
    code-symbols.json               ← GENERATED: code://<file>/<symbol> reverse-index (resolves/drift/refcount)
    code-edges.json                 ← GENERATED: code://<sym> dependencies (direct + bounded transitive)
    [test_*.py files for refcheck, symbols, codeedges]
  blueprint/
    README.md                       ← B1: importable build-spec intro
    component-inventory.json        ← registered components + state shape
    examples/
      C1-inbox.annotated.md        ← Inbox exemplar (kit adoption walkthrough)
    surfaces/                       ← addressable surface specs (J-groups, per-journey)
      J1/A1.json, A3.json, A4.json, A5.json, A6.json, A7.json, D3.json, F3.json
      J2/E1.json, E2.json, E3.json
      J3/C1.json, C2.json, C3.json, D1.json, D2.json, D6.json
      J4/B2.json, B3.json, B5.json, B7.json
      J5/C4.json
      J6/D4.json
      J7/B1.json
      J8/D5.json, D7.json
      J9/A10.json, B4.json
      _unrouted/A11.json, A12.json, A2.json, A8.json, A9.json, B6.json, B8.json, C5.json, F1.json, F2.json, F4.json, F5.json, G1.json, G2.json, G3.json
  mockups/                         ← grounded screens (each links design-system.css, carries data-ui-ref)
  index.html                        ← GENERATED by gallery.py (navigable gallery, status derived, can't drift)
  _archive/                         ← superseded concepts (retired manifest.json merged into register.json)

panels/
  AGENTS.md                         ← module constitution
  settings.json                     ← declarative config panel (pure data, no code)
```

---

## File Inventory Table

| File | Appears to be | PRIORITY | Note |
|------|---------------|----------|------|
| **canvas/AGENTS.md** | Module constitution (S5/D3 governs) | YES | FE layer contract; reads registers/bridge; renders C3/nodes generically; one ai-node shape. |
| **canvas/app/src/App.tsx** | F0 shell restructure; tldraw + React + Tauri entry | YES | Former 1659-line Hud split into carved modules; CSS grid layout (.app-shell, grid-based chrome); pointer-events layering. |
| **canvas/app/src/AppContext.ts** | Provider exposing useAppController state | YES | Surfaces controller to regions via React Context; no prop-drilling. |
| **canvas/app/src/api.ts** | F0 API client + helpers | YES | Proxied to bridge; F5 adds error-normalization (jr/json-or-error); chat/set/connect/tts routes; PRESERVED verbatim. |
| **canvas/app/src/useAppController.ts** | F0 state container (all editor state + handlers) | YES | Single hook holding ~37 useState + refs + effects from former Hud (line 578–1269); loadGraph/SSE/doRun/voice/wire logic. |
| **canvas/app/src/registryStore.ts** | Module globals (shape-reachable half) | YES | 6 globals → 1 external store; getMODEL_OPTIONS/getUI_INFO; setConnect/setForceRun. |
| **canvas/app/src/NodeShape.tsx** | Generic tldraw shape + Edges + loadGraph | YES | Data-driven from /object_info; renders any node-type; Edges + drag-to-wire. |
| **canvas/app/src/main.tsx** | React entry point | MAYBE | Mounts App into #app; standard Vite entry. |
| **canvas/app/src/app.css** | Regional styles (token-only) | YES | Token references (design-system.css); design-lint clean. |
| **canvas/app/src/components/kit.tsx** | WAVE-2 DESIGN: shared vocabulary | YES | SectionHead·LaneHead·Badge·Surface primitives; token-only; recognition-by-shape+tint (not text); one language for whole product. |
| **canvas/app/src/components/kit.tsx** siblings | Presentational components | MAYBE | ShapeHow, BlastRadiusReach, BuildIntentCard, ContextBundle, NodeConfigForm, PanelErrorBoundary, PanelView, WireRequest — carve-preserving extractons. |
| **canvas/app/src/regions/*.tsx** (15 files) | Carved presentational surfaces | YES | Toolbar·Palette·Inspector·Inbox·Grow·OpPanels·Activity·RhmChat·Walkthrough·Workshop·Settings·History·Fleet·CognitionView·SelfChanges·Versions·AddressHelp·ProposeAffordance (19 total). F0 deliverable: CSS grid shell over tldraw. |
| **canvas/app/src/extensions/** | Extension slots | MAYBE | live_clock_widget.tsx exemplar; extensions constitution in AGENTS.md. |
| **canvas/app/package.json** | Vite + React + tldraw + deps | MAYBE | Build config; pnpm workspace. |
| **canvas/app/vite.config.ts** | Vite build config | MAYBE | Entry point, dev server, build output. |
| **canvas/app/tsconfig.json** | TypeScript config | MAYBE | Path aliases, lib, module settings. |
| **canvas/app/dist/assets/index-*.css** | Built output | NO | Generated; do not read. |
| **design/CLAUDE.md** | Keeper charter + boot sequence | YES | Design corpus charter: "registry-as-truth"; read-first chain (Possibility Space → register.json → inventory → conventions). Keeper role + FORM gate. |
| **design/conventions.md** | Mockup corpus org + token/address systems | YES | Folder layout·token system·address scheme·operations (change look, address+map). Registry extend-by-registration pattern. |
| **design/register.json** | Production contract (views/variants/features/journeys) | YES | The machine-readable backbone; every view tagged; coverage map; produced status. |
| **design/_system/tokens.json** | THE design token registry (source of truth) | YES | WARM GOLD theme (Tim, 2026-06-07): gold #e6ab5c primary; sig·await·wire·fail split (vivid+muted); every mockup token-driven. Extend by adding entry. |
| **design/_system/addresses.json** | THE ui:// address registry | YES | Every valid ui://<region>/<element>[@state] address; capabilities (pointable·spotlit·presentable·openable·driven); represents real feature; code location. Extend by registration. |
| **design/_system/components.css** | Template for component styles | MAYBE | Reference var(--x); fed into emit.py. |
| **design/_system/emit.py** | tokens.json + components.css → design-system.css | YES | Generator; run: `python3 emit.py`; every mockup auto-reflows. |
| **design/_system/parse.py** | mockups + addresses.json → element-map.json | YES | Generator; run: `python3 parse.py`; element ⇄ address ⇄ feature ⇄ code mapping. |
| **design/_system/check.py** | Structural coherence + design-lint (free) | YES | Coherence: hardcoded→token candidates, coverage gaps, orphans. LINT: `--target <dir> --fail-on` scans app source for off-token literals; exits non-zero (FORM gate, AGENTS rule 9). |
| **design/_system/refcheck.py** | Code-ref drift validator (free) | YES | Reads code: refs in register.json/addresses.json; resolves against ~/company (READ-ONLY); reports drift → refcheck-report.json. |
| **design/_system/symbols.py** | Reverse index of code: refs → code-symbols.json | YES | Resolves code://<file>/<symbol>; reports resolves/drift/refcount (single occurrence flags, unlike recurrence). |
| **design/_system/codeedges.py** | Structural code dependency graph → code-edges.json | YES | sym→sym dependencies (direct + bounded transitive, depth 2–3 capped, configurable CODEEDGES_DEPTH); parses ~/company via ast (READ-ONLY); stale[] on unparseable. |
| **design/_system/mechanisms.json** | Layer-0 corpus-analysis mechanisms | MAYBE | Extend-by-registration; registry of analysis machinery. |
| **design/_system/element-map.json** | GENERATED: element ⇄ address ⇄ feature ⇄ code mapping | NO | Generated by parse.py; do not edit. |
| **design/_system/check-report.json** | GENERATED: coherence findings | NO | Generated by check.py; do not edit. |
| **design/_system/refcheck-report.json** | GENERATED: code-ref drift findings | NO | Generated by refcheck.py; do not edit. |
| **design/_system/code-symbols.json** | GENERATED: code://<file>/<symbol> reverse-index | NO | Generated by symbols.py; do not edit. |
| **design/_system/code-edges.json** | GENERATED: code dependencies (sym→sym) | NO | Generated by codeedges.py; do not edit. |
| **design/blueprint/README.md** | B1 build-spec intro | YES | "Build-TO-schema, not from-docs"; import → build → connects to system (ONE address grammar). Five things: look, addresses, state, components, address-location. |
| **design/blueprint/component-inventory.json** | Registered components + state shape | YES | Schema for the build; every component's state/shape registered. |
| **design/blueprint/examples/C1-inbox.annotated.md** | Inbox exemplar (kit adoption walkthrough) | MAYBE | Shows how regions adopt kit primitives. |
| **design/blueprint/surfaces/J*/**.json** | Addressable surface specs (J-journeys) | YES | J1–J9 + _unrouted; each surface a schema; state/shape/capabilities; journey-routed. |
| **design/mockups/** | Grounded screens | NO | Not inventoried here; each links design-system.css, carries data-ui-ref. Hundreds exist. |
| **design/index.html** | GENERATED gallery | NO | Generated by gallery.py; status derived (can't drift). |
| **design/_archive/** | Superseded concepts | NO | Retired manifest.json merged into register.json. |
| **design/CONNECTION-CONTRACT.md** | ui://<region> ↔ code seam specs | YES | Defines how ui:// addresses wire to React regions; capabilities contract. |
| **panels/AGENTS.md** | Module constitution | YES | Declarative UI panels (JSON fields edit real config); git-reversible; proposed via RHM. |
| **panels/settings.json** | Declarative config panel | YES | Pure data, no code; fields bind to real config; registry overrides guessed options. |

---

## Key Findings

### FE Structure (canvas/)
- **Carved from monolith:** F0 restructure split 1659-line App.tsx (Hud) into coherent modules: api.ts, registryStore.ts, NodeShape.tsx, useAppController.ts, AppContext.ts, and 19 region components.
- **Controller pattern:** Single useAppController hook holds all editor state (~37 useState) + refs (concurrency guards) + handlers/effects. Exposed via AppContext.
- **CSS grid shell (F0 deliverable):** Grid layout (.app-shell) layered OVER tldraw board; canvas cell is pointer-events:none (board interactive); chrome cells (top/rail/panel/foot) re-enable it.
- **Regions:** Toolbar, Palette, Inspector, Inbox, Grow, OpPanels, Activity, RhmChat, Walkthrough, Workshop, Settings, History, Fleet, CognitionView, SelfChanges, Versions, AddressHelp, ProposeAffordance.
- **One generic node shape:** NodeShape.tsx renders data-driven from /object_info; no per-type code.
- **Shared kit (WAVE-2):** kit.tsx provides SectionHead, LaneHead, Badge, Surface — one vocabulary for whole product (recognition-by-shape+tint, not text).
- **API error handling (F5):** jr/json-or-error normalizes HTTP errors; existing callers branch on if(r.error) without throwing; Blob-typed responses (tts) bypass jr.

### Design Substrate (design/)
- **Keeper charter:** CLAUDE.md defines the role; folder = "registry-as-truth" + thinking-substrate; boot order: Possibility Space → register.json → inventory → conventions.
- **Extend-by-registration pattern:** Tokens, addresses, components, surfaces all registered (not hardcoded); new thing = add entry + carry in mockup/code.
- **Token system:** tokens.json = edit point → emit.py → design-system.css (GENERATED, never edit). WARM GOLD theme (Tim, 2026-06-07): sig·await·wire·fail split (vivid+muted to hold 4 signals apart).
- **Address system:** addresses.json = ui://<region>/<element>[@state]; capabilities (pointable·spotlit·presentable·openable·driven); every address maps to code location + feature.
- **Free structural tools:** check.py (coherence + design-lint with --target/--fail-on for build gate), refcheck.py (code-ref drift), symbols.py (reverse-index), codeedges.py (sym→sym deps, depth 2–3).
- **Blueprint (B1):** Importable build-spec; surfaces/J*/**.json = schema; build-to-schema, deterministic, design-lint gates build (FORM gate, AGENTS rule 9).

### Declarative Panels (panels/)
- **Pure data:** panels/settings.json is declarative; fields bind to real config; no code.
- **Git-reversible:** Proposals via RHM propose_panel; operator approves; apply_panel writes JSON here.
- **Registry overrides:** Field options auto-populated from running registry (path-of-least-resistance).

---

## Top 10 PRIORITY Files (FE structure + design substrate)

1. **canvas/app/src/App.tsx** — F0 shell restructure; grid layout seam; entry point architecture
2. **canvas/app/src/useAppController.ts** — State container; all editor logic; centerpiece of controller
3. **design/CLAUDE.md** — Keeper charter + boot sequence; essential context for the design folder
4. **design/conventions.md** — Token/address systems + folder org; how to extend + operations
5. **design/_system/tokens.json** — Source of truth for look; WARM GOLD theme; every mockup's reference
6. **design/_system/addresses.json** — Source of truth for ui:// registry; FE-design seam contract
7. **design/register.json** — Production contract (views/variants/features/coverage); machine-readable backbone
8. **design/blueprint/README.md** — B1 intro; build-to-schema philosophy; design-lint gate
9. **canvas/app/src/NodeShape.tsx** — Generic node rendering (data-driven from /object_info); central to one-shape approach
10. **canvas/app/src/components/kit.tsx** — WAVE-2 shared vocabulary; recognition-by-shape+tint; language of the product

---

## Design Conventions & Extend Points

**Token Extension:** Edit design/_system/tokens.json (add entry with {v: value} or {ref: primitive}), run `python3 emit.py`, every mockup reflows.

**Address Extension:** Add entry to design/_system/addresses.json (ui://<region>/<element>, capabilities, code location), run `python3 parse.py`, element-map updates.

**Component Extension:** Propose via RHM; blueprint/component-inventory.json is schema source.

**Panel Extension:** RHM proposes → operator approves → apply_panel writes JSON to panels/.

**Design Lint Gate:** `python3 design/_system/check.py --target canvas/app/src --fail-on` (scans source for off-token literals; exits non-zero; blocks build per AGENTS rule 9).

---

## Notes on Duplicates / Legacy

- No legacy duplicates found in this region.
- Design folder has _archive/ (retired concepts); not inventoried.
- All generated files (_system/*.json) are marked GENERATED; do not edit.

