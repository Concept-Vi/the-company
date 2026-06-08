# Design Substrate — Deep Read
**Scope:** `/home/tim/company/design/` — token-slot contract, address system, blueprint schema, conventions + tooling  
**Date:** 2026-06-08  
**Mode:** READ-ONLY comprehension pass. No edits made.

---

## Critical framing

The task is to extract the **STRUCTURE** — the slot names, categories, and conventions that a design fills — not the current values. Everything in `tokens.json` is wrapped in aesthetic rationale (gold-primary, warm charcoal, persona pastels, vivid/muted signal splits). That prose describes the current fill. Claude Design's lane is to supply new values for the same slot names. The slots are the contract; the values are provisional.

---

## 1. The Token-Slot Contract

**Source:** `design/_system/tokens.json`  
**Generated output:** `design/design-system.css` (via `emit.py` — never edit the CSS directly)

### How tokens are structured

```
tokens.json
  primitives: { name: hex }           ← single values referenced by other tokens
  groups: [
    { name, note, tokens: { slot-name: {v: value} | {ref: primitive-name} } }
  ]
```

A `{ref: primitive}` token changes automatically when its primitive changes. A primitive is changed once and every ref follows — the law-2 mechanism (change data, not generated files).

---

### The slot categories (the groups — what Claude Design fills)

#### Group 1 — Surface tiers
The depth stack of the UI. Seven named levels from deepest background to foreground.

| Slot | Role |
|------|------|
| `--bg` | The deepest surface (behind everything) |
| `--s0` | First elevation surface |
| `--s1` | Second elevation surface |
| `--s2` | Third elevation surface |
| `--s3` | Fourth elevation surface |
| `--line` | Primary separator/border |
| `--line-2` | Secondary separator/border |
| `--tx` | Primary text |
| `--tx-2` | Secondary/muted text |
| `--tx-3` | Tertiary/faint text |

#### Group 2 — Signal + semantic
The alive/status/identity colours. Not decorative — each carries a specific meaning that the system reads visually.

| Slot | Role |
|------|------|
| `--acc` | Primary identity/accent (alive, done, value signal) |
| `--acc-dim` | Dimmed accent (supporting tone) |
| `--acc-glow` | Glow / scrim (the ambient halo — semi-transparent fill) |
| `--acc-deep` | Deep/grounded end of the accent range |
| `--await` | Awaiting-input signal (distinct from acc by hue direction) |
| `--fail` | Failure / error signal |
| `--cache` | Cached/neutral signal |
| `--ok` | Resolved/success signal |

The current fill uses a two-vivid + one-muted split to keep `acc` / `await` / the wire-structural tone apart visually. That's a fill decision, not a constraint on the slot names.

#### Group 3 — Ink on bright surfaces
Text colours that sit ON coloured fills (accent chips, badges, primary buttons) — legibility layer, not ambient text.

| Slot | Role |
|------|------|
| `--ink-accent` | Text ON the accent fill |
| `--ink-await` | Text ON the await fill |
| `--ink-fail` | Text ON the fail fill |

#### Group 4 — Node-type visual language
The kind-coding system. Node kinds get distinct colours so the canvas is scannable by sight.

| Slot | Role |
|------|------|
| `--kind-process` | Process-kind node foreground |
| `--kind-content` | Content-kind node foreground |
| `--kind-present` | Present-kind node foreground (contract-allowed, no live node yet) |
| `--kind-model` | Model-config accent (NOT a node kind — a config-slot signal) |
| `--kind-process-bg` | Process-kind node background fill (semi-transparent) |
| `--kind-content-bg` | Content-kind node background fill |
| `--kind-present-bg` | Present-kind node background fill |
| `--kind-model-bg` | Model-config background fill |

Note: the registry records only TWO live kinds (process, content). `kind-present` is contract-allowed but has no live node. `kind-model` is a config accent, not a kind.

#### Group 5 — Typography
The type system. Slots for font families AND a modular scale named by role (not by px number), so a region picks intent.

| Slot | Role |
|------|------|
| `--font-display` | Display / heading / serif authority face |
| `--font-mono` | Monospace instrument body (precision reads) |
| `--font-body` | Base body font (aliased to mono in current fill — the instrument defaults) |
| `--font-sans` | Sans-serif face (available; not the instrument default) |
| `--fs-micro` | Micro-scale text (tags/badges at extreme small) |
| `--fs-tag` | Tag-level text |
| `--fs-meta` | Metadata-level text |
| `--fs-body` | Body text |
| `--fs-lg` | Large body |
| `--fs-title` | Title/label text |
| `--fs-display` | Display/heading text |
| `--lh-tight` | Tight line-height (headings) |
| `--lh-body` | Body line-height |
| `--tr-tag` | Letter-spacing for tags |
| `--tr-label` | Letter-spacing for labels |

The scale uses role-names so the intent is expressed, not an arbitrary px number.

#### Group 6 — Living instrument (presence, glow, persona)
The depth + motion + presence layer. The ambient glow flow and per-persona colour families.

| Slot | Role |
|------|------|
| `--gold-hi` | Light end of the primary accent range |
| `--gold-mid` | Mid of the primary accent range (ref to `gold` primitive) |
| `--gold-deep` | Deep/grounded end of the primary accent range |
| `--acc-flow` | Gradient fill (orb, run strip, alive flow — the animated alive surface) |
| `--orb-hi` | Specular highlight on the presence orb |
| `--persona-atlas` | Atlas persona accent |
| `--persona-atlas-deep` | Atlas persona deep accent |
| `--persona-atlas-glow` | Atlas persona glow |
| `--persona-atlas-flow` | Atlas persona gradient flow |
| `--persona-nova` | Nova persona accent |
| `--persona-nova-deep` | Nova persona deep accent |
| `--persona-nova-glow` | Nova persona glow |
| `--persona-nova-flow` | Nova persona gradient flow |

Note: Vi-persona = the canonical primary fill. Atlas and Nova are DEFINED as tokens but are NOT-LIVE in the running app (App.tsx does not set `data-persona`). A future persona switcher would activate them via `[data-persona=atlas]` CSS scoping. They are slot-ready, not yet wired.

#### Group 7 — Shape (space + radius + elevation)
The spatial rhythm. A modular base-4 space ramp, a 3-step radius ladder, and two elevation levels.

| Slot | Role |
|------|------|
| `--sp-1` through `--sp-6` | Space ramp: 4 · 8 · 12 · 16 · 24 · 32 px |
| `--sp` | Base-8 alias (legacy default; kept so existing `var(--sp)` refs continue resolving) |
| `--r-sm` | Small radius |
| `--r` | Standard radius |
| `--r-lg` | Large radius |
| `--r-pill` | Pill/full-round radius |
| `--shadow-color` | Drop-shadow colour (fills box-shadow declarations) |
| `--shadow` | Standard shadow |
| `--elev-1` | Elevation tier 1 (rail/panel depth) |
| `--elev-2` | Elevation tier 2 (floating card/sheet depth) |

---

### Gaps (slots-to-add — identified by prior pass and structural analysis)

These categories are referenced in the corpus but have no registered token group yet. They represent the slots Claude Design would need to fill to complete the contract:

1. **Motion / animation** — no duration, easing, or transition slots anywhere in `tokens.json`. The living-instrument group implies animated presence (orb, acc-flow gradient), but durations like `--duration-fast / --duration-med / --easing-spring` do not exist as tokens. Current values are scattered as literals in CSS. This is the most significant gap — motion is a visible design dimension that should assemble from the registry.

2. **Breakpoints / responsive** — no `--bp-mobile / --bp-tablet / --bp-desktop` tokens. Responsive behaviour is currently expressed as literal `min-width` values in CSS.

3. **Z-index layer stack** — no `--z-canvas / --z-chrome / --z-overlay / --z-modal` tokens. Stacking context is managed per-region with literals.

4. **Opacity scale** — `--acc-glow` is the one semi-transparent token, but there is no general opacity ramp (e.g. `--op-muted / --op-dim / --op-ghost`) for when regions dim un-focused content.

5. **Icon sizing** — no `--icon-sm / --icon-md / --icon-lg` tokens. Icon sizes are expressed as px literals today.

---

## 2. The Addresses Registry

**Source:** `design/_system/addresses.json`  
**Generated output:** `design/_system/element-map.json` (via `parse.py`)

### The scheme

```
ui://<region>/<element>[/<sub>][@<state>]   ← chrome / panels
run://<graph>/<node>[#<port>]               ← canvas nodes (pattern-based, not enumerated)
code://<file-stem>/<symbol>                 ← code symbols (symbols.py / codeedges.py)
```

### How an entry is shaped

```json
"ui://inbox/build-intent": {
  "region":       "inbox",
  "capabilities": ["pointable", "presentable", "spotlit"],
  "represents":   "WIRE-intent",
  "code":         "runtime/suite.py:surface_build_intent / runtime/bridge.py:do_POST",
  "howto":        "plain-language: WHAT / WHAT YOU CAN DO / HOW TO CHANGE IT"
}
```

**Fields:**

- `region` — which React region component renders this element (toolbar, canvas, inspector, inbox, chat, activity, walkthrough, workshop, models, settings, grow, cognition, tabbar)
- `capabilities` — what the element can do as a pointed target:
  - `pointable` — can receive a click / tap to become the indicated locus
  - `spotlit` — can be spotlit (the view navigates to and highlights it)
  - `presentable` — surfaces as a review/walkthrough item
  - `openable` — can be opened/expanded as a panel
  - `driven` — live-driven by backend state (reactive)
  - `driven-read-only` — driven by backend but operator cannot write (e.g. portal-window, versions)
- `represents` — the feature-id from `register.json` that this element exposes
- `code` — the file:symbol or /api/endpoint that backs it (the traceability link)
- `howto` — the address-help text the guide tour / AddressHelp panel shows (plain language at Tim's altitude)

### How `data-ui-ref` ties DOM to address

Every meaningful element in a mockup or in the real React app carries:
```html
<div data-ui-ref="ui://inbox/build-intent">…</div>
```

This attribute is the join key. `parse.py` reads all `data-ui-ref` values across all mockup HTML files and joins them against `addresses.json`, producing `element-map.json`. The map is bidirectional:

- **Used-but-unregistered** orphans: a `data-ui-ref` in a mockup that has no entry in `addresses.json` — fiction or cruft (or an unregistered `run://` node address, which is pattern-based)
- **Registered-but-unused** orphans: an address in `addresses.json` that no mockup carries yet — the addressing backlog

The `run://` scheme is deliberately pattern-based, not enumerated: every graph node gets its own `run://<graph>/<node>` address at runtime, derived from its node-id. These are not registered individually in `addresses.json` because they are infinite-cardinality — the scheme is the contract, not an enumeration.

### Current address inventory

**45 registered ui:// addresses** across 15 regions:

| Region | Addresses |
|--------|-----------|
| toolbar | toolbar, toolbar/run, toolbar/presence, toolbar/wire, toolbar/portal, toolbar/delete, toolbar/layers, toolbar/fit, toolbar/reload, toolbar/point, toolbar/guide, toolbar/teach |
| rail | rail/palette |
| canvas | canvas, canvas/node, canvas/portal-window, canvas/wire-request |
| inspector | inspector, inspector/model-field, inspector/act, inspector/workshop, inspector/surface, inspector/build, inspector/history, inspector/versions, inspector/freshness, inspector/help |
| inbox | inbox, inbox/build-review, inbox/build-intent, inbox/context-bundle, inbox/context-pin, inbox/coa, inbox/target, inbox/walk |
| chat | chat, chat/input, chat/send, chat/mic, chat/minimize, chat/new-conversation, chat/threads, chat/record, chat/debrief |
| activity | activity, activity/replay |
| walkthrough | walkthrough, walkthrough/verdict, walkthrough/voice, walkthrough/next, walkthrough/reason, walkthrough/show-again |
| workshop | workshop, workshop/self-changes |
| models | models |
| twin | twin |
| grow | grow, grow/dispatch, grow/approve, grow/reject |
| settings | settings, settings/close, settings/brain, settings/modes, settings/voice, settings/roles, settings/composition |
| cognition | cognition, cognition/pulse, cognition/river |
| tabbar | tabbar |

**Component status (from `component-inventory.json`):**
- Built (have a React file): activity, canvas (App.tsx), chat (RhmChat.tsx), inbox, inspector, rail, settings, toolbar, walkthrough, workshop
- Planned (address registered, no component file yet): cognition, grow, models (Fleet.tsx exists but not mapped), tabbar, twin

---

## 3. The Blueprint — importable build-spec

**Source:** `design/blueprint/README.md`, `design/blueprint/surfaces/`, `design/blueprint/component-inventory.json`  
**Generator:** `design/_system/blueprint_emit.py`

### What the blueprint is

The blueprint is the **build-to-schema contract** — the importable specification a fresh Claude Code session reads to build the front-end deterministically, without interpreting prose. "Build-to-schema, not build-from-docs."

It hands the builder five things:

1. **The look** — `tokens.json` → `design-system.css` (never edit the CSS). Every off-token hex/px is a lint failure.
2. **The addresses** — `addresses.json` (the ui:// registry) + `element-map.json`. The builder carries `data-ui-ref` from this; never invents an address.
3. **The state registry** — 7 NODE_STATES each with a render (token + icon + shape), served live via `GET /api/capabilities → node_states`. The FE reads the served registry, not a hardcoded enum.
4. **The component specs** — `component-inventory.json` (every region → its React component, built|planned) + the surface schemas in `surfaces/`.
5. **The connection contract** — `CONNECTION-CONTRACT.md` (what the FE sends on a command, what it reads for state, how an element declares its address, the governance-by-tier rule).

### Surface schema shape

Each surface spec is a JSON file at `surfaces/<home-journey>/<view-id>.json`:

```json
{
  "_what": "GENERATED surface-spec for view C1. …",
  "id": "C1",
  "area": "C",
  "title": "Inbox — three lanes, clean",
  "platforms": ["desktop", "mobile"],
  "represents": ["INB-lanes", "EVT-now"],
  "status": "planned",
  "home_journey": "J3",
  "journeys": ["J3", "J5", "J7"],
  "cross_journeys": ["J5", "J7"],
  "addresses": ["ui://activity", "ui://inbox"],
  "build_to": {
    "components": ["activity", "inbox"],
    "design_lint": "check.py --target canvas/app/src --fail-on  (the FORM gate)",
    "tokens": "design/_system/tokens.json → design-system.css (the only look-source)"
  }
}
```

Key fields:
- `home_journey` — which journey's directory the file lives under (the tree gives each view exactly one home)
- `journeys` — ALL journeys this view belongs to (the web; the full set including home)
- `cross_journeys` — the journeys BEYOND the home (the address-refs that give the web its non-tree connections)
- `addresses` — the registered `ui://` addresses this view carries
- `address_gap` — present when the view represents features that have no registered address yet (honest signal, not a failure to hide). Example from A7:
  ```json
  "address_gap": "view A7 represents ['CAN-drag', 'NODE-ports'] but no registered ui:// address joins by feature-id"
  ```

### The tree/web tension

The `surfaces/` directory is organized by journey (J1–J9 + `_unrouted/`). A directory tree can place each view in exactly one home. But many views belong to multiple journeys (e.g. C1 ∈ J3·J5·J7) and the nav graph has cycles. Resolution: **tree carries structure** (one home per view), **cross_journeys[] carries the web** (the address-references). `navgraph.py` reads both and reconstructs the full journey graph, proving it matches `register.json sequences`. The `_unrouted/` directory holds views not yet assigned to a journey home.

### The 16 address-gap views

The README flags 16 views with features that have no registered `ui://` address — the address backlog. Examples: A7/CAN-drag, A8/CAN-zoom, B2/VOICE, D4/INB-idea, D5/SM-*, G1-G3/responsive. The surface specs flag these honestly as `address_gap`. The builder structures the view, registers the address when it lands. Do not invent an address to fill the gap.

---

## 4. Where-design-goes conventions

**Source:** `design/conventions.md`, `design/CLAUDE.md`

### The law (one sentence)

Edit data not generated files; extend by registration; the machinery picks it up.

### The canonical data sources

| Source | What it controls | Generator | Output |
|--------|------------------|-----------|--------|
| `_system/tokens.json` | All visual values (the look) | `emit.py` | `design-system.css` |
| `_system/addresses.json` | All ui:// addresses | `parse.py` | `element-map.json` |
| `register.json` | All views + features + journeys + coverage | `gallery.py` | `index.html` |

Generated files (`design-system.css`, `element-map.json`, `index.html`, `check-report.json`, `refcheck-report.json`, `code-symbols.json`, `code-edges.json`) are NEVER hand-edited. Editing them is a violation — changes are lost on next regeneration and introduce drift.

### The mockup rules

1. Every mockup links `../design-system.css` — no inline styles that belong in the system
2. No view is grounded until its `features[]` are real (sourced from the actual app)
3. Responsive + mobile-native are mandatory where `platforms` includes `mobile`
4. `register.json` is updated and `gallery.py` re-run whenever a mockup is added/changed
5. Every meaningful element carries `data-ui-ref="ui://…"` from the address registry

### The status ladder

`planned → drafting → drafted → quality-passed → approved(Tim)`

A view-variant counts DONE for the loop at `quality-passed`. The `produced` list in `register.json` is a build-log reconciled DOWN to `views[].status` — never an independent quality claim.

---

## 5. The Lint / Drift Tooling

### check.py — two modes

**Mode A (default, no args) — mockup scan:**
```
python3 design/_system/check.py
```
Reports:
- Hardcoded literals in mockups: matches an existing token → should use `var(--x)`; matches nothing → candidate new token
- Coverage gaps: registered features with no view
- Orphan addresses (both directions: used-but-unregistered, registered-but-unused)
- Hygiene: mockups missing the CSS link or any `data-ui-ref`
- Writes `check-report.json`

**Mode B (additive, with `--target`) — design lint:**
```
python3 design/_system/check.py --target canvas/app/src --fail-on
```
Scans `.tsx`/`.css` under `<target>` for hardcoded off-token literals (hex, rgba — and optionally px with `--include-px`). Flags a SINGLE occurrence (not recurrence). With `--fail-on`: exits non-zero when any finding. This is the FORM gate.

Bespoke-element detection is a documented STUB (stub comment at line 97): it returns `[]` today and graduates with F4/F1. It is wired into `--fail-on` to count, but injects no spurious findings in the current build.

### Confirmed: the design-lint fires only through the build wire

**Observed** (grep across entire `~/company` codebase):

- The live invocation is `Suite._design_critic()` in `runtime/suite.py` (lines 7036–7114). It calls `check.py --target <changed-canvas-file> --fail-on` via `subprocess.run()` for each `.tsx`/`.css` the build changed.
- `tests/design_gate_acceptance.py` tests the gate end-to-end but does NOT invoke it in normal operation.
- **No CI workflow:** `/home/tim/company/.github` does not exist.
- **No pre-commit hook:** All hooks in `.git/hooks/` are `.sample` files — none are activated.
- **No npm script:** `canvas/app/package.json` scripts are `dev` (vite dev server) and `build` (vite build). No lint script.
- **No Makefile** at the repo root.

Conclusion (observed, not inferred): the design-lint (`check.py --target … --fail-on`) fires **exclusively inside `Suite._design_critic()`**, which is called during the build dispatch path in `runtime/suite.py`. It runs **per-changed-file** (only the files the build modified, not the whole `canvas/app/src`). A pure-backend build (no canvas change) skips it entirely. The gate is build-wire-only — there is no standing CI/pre-commit enforcement.

The fail-safe design: if the lint cannot run (corpus missing, file not found, subprocess crash), `_design_critic()` returns `(False, reason)` — unverifiable is treated as not-passed, never silent True.

### refcheck.py — code-ref drift validator

```
python3 design/_system/refcheck.py
```
Reads every `code:` field in `register.json` (`features[].code`) and `addresses.json` (`addresses.*.code`). Resolves each ref against `~/company` (READ-ONLY). Reports where a ref no longer lands on the symbol it claims, with a repair target where findable. Writes `refcheck-report.json`. **Does not repair** — emits the lead's repair worklist. `views[].represents[]` are feature-ids (referential pointers) not code refs; only `features[].code` is validated.

### symbols.py — reverse index

```
python3 design/_system/symbols.py
```
The REVERSE to refcheck's forward pass. Reads the same code refs, resolves each, and builds `code-symbols.json` keyed by `code://<file-stem>/<symbol>`. Each entry: `{ file, symbol, kind(def|class|route|const|file-only), resolves, referenced_by[] }`. `resolves:false` = drift; `referenced_by` 2+ = a shared symbol (change ripples to multiple features/addresses). With embedder `:8001` live, each entry also gains `semantically_nearest[]` (top-K conceptually-related symbols with no code link, the semantic sibling of the structural call-graph). Degrades-with-warning when the embedder is down.

### codeedges.py — structural code-dependency graph

```
python3 design/_system/codeedges.py
```
The symbol→symbol branch. Parses Python source under `~/company` via stdlib `ast` (READ-ONLY). Emits `code-edges.json` keyed by the same `code://` ids: `{ depends_on[], depended_by[], resolves }`. Only direct edges stored; transitive reach is a bounded query capped at `DEPTH` (default 2, max 3, configurable via `CODEEDGES_DEPTH` env). Capped reaches are reported, never silently truncated. Unparseable files → `stale[]` (fail-loud). Used by the blast-radius calculation for self-builds.

### mechanisms.json — the analysis registry

`_system/mechanisms.json` is the extend-by-registration registry for all corpus-analysis checks. Three mechanisms currently registered: `code-ref-validator` (refcheck.py), `code-symbol-registry` (symbols.py), `code-dependency-graph` (codeedges.py). Adding a check = add an entry to this registry + drop the script + a `test_<x>.py`. The registry generalises the check.py pattern into an extendable set.

---

## Summary

### Token-slot contract (Claude Design's styling interface)

Seven categories of slots, in dependency order:

1. **Surface tiers** — bg/s0–s3/line/line-2/tx/tx-2/tx-3 (the depth stack)
2. **Signal + semantic** — acc/acc-dim/acc-glow/acc-deep/await/fail/cache/ok (status vocabulary)
3. **Ink on bright** — ink-accent/ink-await/ink-fail (legibility on coloured fills)
4. **Node-type visual** — kind-process/kind-content/kind-present/kind-model + -bg variants
5. **Typography** — font-display/font-mono/font-body/font-sans + fs-micro through fs-display + lh/tr scale
6. **Living instrument** — gold-hi/gold-mid/gold-deep/acc-flow/orb-hi + persona-atlas/nova families (glow/flow/deep per persona)
7. **Shape** — sp-1 through sp-6 + sp alias + r-sm/r/r-lg/r-pill + shadow-color/shadow/elev-1/elev-2

**Slot gaps** (not yet tokenised — slots-to-add): motion (duration/easing), breakpoints, z-index layer stack, opacity scale, icon sizing.

### How UI elements get addresses

Every meaningful DOM element carries `data-ui-ref="ui://<region>/<element>"`. The address is registered in `addresses.json` with its region, capabilities (pointable/spotlit/presentable/openable/driven), the feature it represents, and the code that backs it. `parse.py` joins DOM refs to registry entries and flags orphans both ways. The `run://` node scheme is pattern-based (infinite cardinality) and is not enumerated — the scheme is the contract.

### Design conventions

Edit `tokens.json` / `addresses.json` / `register.json` — never the generated CSS. Extend by registration. The design-lint (`check.py --target … --fail-on`) is the FORM gate, fires exclusively inside `Suite._design_critic()` during the build dispatch path — not standing CI, not pre-commit. Bespoke-element detection is a wired stub (returns [], no live findings) graduating with F4/F1.
