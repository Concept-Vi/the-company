# AREA-design — Design System Landscape Dragnet

> **Extractor role.** This is a read-only exhaustive capture of `/home/tim/company/design/` (121 files).
> No filtering, no omission of stale/dead/surprising. Evidence = file paths throughout.

---

## 0 · What this folder IS (one breath)

`design/` is the Company's **front-end design corpus and living model**. It is NOT documentation — it is:
- Two working **registries** (`tokens.json` → the look; `addresses.json` → the `ui://` address system)
- A grounded **mockup corpus** (HTML screens each linked to real features and code refs)
- A **self-describing substrate**: the Company's own registry/address architecture turned onto its own face
- A **build-spec**: the `blueprint/` subtree and `CONNECTION-CONTRACT.md` are machine-readable build contracts a fresh Claude Code session can build to directly

**Sync note (README.md):** `~/company/design/` is a **synced read-copy**. The canonical source lives at
`build-prep/design/` (Windows-side: `/mnt/c/Users/Workstation001/Documents/Claude/Projects/counterpart/the Company/build-prep/design/`). A hand-edit here is silently overwritten on next sync. This file (`AREA-design.md`) is being written into `build-prep/company-landscape/` per task instruction — not into the synced read-copy.

---

## 1 · The Design Token System

**Source of truth:** `design/_system/tokens.json`
**Generated output:** `design/design-system.css` (GENERATED — never hand-edit)

### 1.1 Token counts

| Group | Count | Purpose |
|---|---|---|
| surface tiers | 10 | Warm charcoal base palette (`bg`, `s0`–`s3`, `line`, `line-2`, `tx`, `tx-2`, `tx-3`) |
| signal + semantic | 8 | `acc` (gold), `acc-dim`, `acc-glow`, `acc-deep`, `await`, `fail`, `cache`, `ok` |
| ink on bright surfaces | 3 | `ink-accent`, `ink-await`, `ink-fail` — near-black on coloured fills |
| node-type visual language | 8 | `kind-process`, `kind-content`, `kind-present`, `kind-model` + their `-bg` variants |
| typography | 15 | `font-display`, `font-mono`, `font-body`, `font-sans`; `fs-micro`..`fs-display`; `lh-*`; `tr-*` |
| living instrument | 13 | `gold-hi/mid/deep`, `acc-flow` gradient, `orb-hi`, `persona-atlas-*`, `persona-nova-*` |
| shape | 15 | `sp-1..sp-6`, `sp`, `r-sm`, `r`, `r-lg`, `r-pill`, `shadow-color`, `shadow`, `elev-1`, `elev-2` |
| **TOTAL** | **72** | — |

**Primitive:** 1 (`gold`: `#e6ab5c`) — feeds `acc`, `ok`, `kind-process`, `kind-present`, `gold-mid`

**Imports (fonts):** Fraunces (display/serif), Bricolage Grotesque, IBM Plex Mono (instrument body), IBM Plex Sans — the "commander's-bridge" type system established 2026-06-07.

### 1.2 Colour direction (gold-primary warm theme, locked 2026-06-07)

- **Base:** warm charcoal (`#0c0a08`) — NOT cold blue-black
- **Primary accent:** gold (`#e6ab5c`) — THE identity colour; also `acc`, `ok`, `kind-process`
- **Status signal split (TWO VIVID + ONE MUTED):** `sig`=gold (vivid), `await`=orange-amber (vivid, leans away from gold toward orange), `wire`/`kind-content`=desaturated bronze/taupe (MUTED — structural reads muted beside vivid signals)
- **Fail:** coral (`#ec6a5e`)
- **Cache:** warm taupe-grey neutral (`#9c8f78`) — the one near-cool
- **Personas defined-not-live:** Vi=canonical gold; Atlas=soft apricot pastel; Nova=soft rose-gold pastel. Tokens exist but the app doesn't set `data-persona` yet — the switch is a future controller change.

### 1.3 Typography direction

- `font-display` = Fraunces serif (authority: titles, RHM voice, panel headings)
- `font-mono` = IBM Plex Mono (instrument body: every control, label, value, address)
- `font-body` aliases `font-mono` — base font IS mono
- Scale: named by role (`fs-micro` 8.5px → `fs-display` 19px) — no scattered px literals

### 1.4 Known token issues (from check-report.json)

- **31 literals should use `var(--…)`** — existing tokens exist but not used
- **27 candidate new colour tokens** — recurrent hex values not yet in registry (940 element candidates scanned across 23 mockups)
- **3 mockups missing design-system CSS link**
- **3 mockups missing any address**

---

## 2 · The Address System

**Source of truth:** `design/_system/addresses.json`
**Total registered addresses:** 504 (across 31 regions)
**Generated output:** `design/_system/element-map.json` (via `parse.py`)

### 2.1 Regions by address count

| Region | Addresses | Component Status |
|---|---|---|
| inbox | 86 | BUILT (`Inbox.tsx`) |
| canvas | 79 | BUILT (`App.tsx` + `NodeShape.tsx`) |
| chat | 46 | BUILT (`RhmChat.tsx`) |
| inspector | 42 | BUILT (`Inspector.tsx`) |
| activity | 33 | BUILT (`Activity.tsx`) |
| board | 31 | PLANNED (no component) |
| toolbar | 27 | BUILT (`Toolbar.tsx`) |
| settings | 25 | PLANNED (no component) |
| chrome | 20 | PLANNED (no component) |
| workshop | 15 | BUILT (`Workshop.tsx`) |
| walkthrough | 14 | BUILT (`Walkthrough.tsx`) |
| studio | 13 | PLANNED (no component) |
| twin | 11 | PLANNED (B6 mockup exists, no carved component) |
| address-help | 8 | PLANNED |
| tune | 7 | PLANNED |
| tabbar | 6 | PLANNED (mobile-nav inline in App.tsx shell) |
| grow | 5 | PLANNED |
| forager | 5 | PLANNED |
| registry | 5 | PLANNED |
| rail | 4 | BUILT (`Palette.tsx`) |
| rhm | 4 | PLANNED |
| cognition | 3 | PLANNED |
| mockup | 3 | PLANNED |
| run | 3 | PLANNED |
| scenario-player | 2 | PLANNED |
| scenario | 2 | PLANNED |
| models | 1 | PLANNED (fleet surface F8, no dedicated component) |
| mockup-studio | 1 | PLANNED |
| palette | 1 | PLANNED |
| queue | 1 | PLANNED |
| system | 1 | PLANNED |

**Address grammar:** `ui://<region>/<element>[/<sub>][/@state]`
**Second scheme:** `run://<graph>/<node>` for live graph-node instances (pattern-based, not enumerated)

### 2.2 Address orphan status (check-report.json)

- **Unregistered (in mockups but not in registry):** 2 — `run://demo/ask` and `run://system/model_of_tim` (these are `run://` pattern-based, expected)
- **Unused (registered but no mockup carries them):** 45 addresses registered but not yet placed in any mockup — the addressing backlog

### 2.3 Address record shape (per entry)

Each address carries: `region` · `capabilities` (string list: `pointable|spotlit|presentable|openable|drivenReadOnly`) · `represents` (feature-id) · `code` (file:line or route) · `howto` (human description: WHAT it is, WHAT YOU CAN DO, HOW TO CHANGE IT)

**Reconciliation note (CONNECTION-CONTRACT.md §1):** corpus stores capabilities as string-list; the live Pydantic model uses bool-object with `drivenReadOnly` only. The S0 projection converts. `kind` field (chrome|field|canvas|panel|ext) absent from corpus compact rows — the live resolver dispatches on it; S0 projection adds it.

---

## 3 · The Blueprint / J-Surface Structure

**Path:** `design/blueprint/`
**GENERATED by:** `_system/blueprint_emit.py`

### 3.1 Blueprint directory map

```
blueprint/
  README.md                  builder onboarding + build-spec (the 5 things it hands you)
  component-inventory.json   GENERATED: every region → React component (built|planned)
  examples/
    C1-inbox.annotated.md    annotated walkthrough: how to build ONE view to schema
  surfaces/
    J1/  A1 A3 A4 A5 A6 A7 D3 F3    (Compose & run a process — spine)
    J2/  E1 E2 E3                    (Leverage models & embeddings)
    J3/  C1 C2 C3 D1 D2 D6           (Direct a self-build — spine)
    J4/  B2 B3 B5 B7                 (Be walked through a decision — spine)
    J5/  C4                          (Triage the inbox)
    J6/  D4                          (Capture an idea)
    J7/  B1                          (Operate from mobile — spine)
    J8/  D5 D7                       (Grow the system)
    J9/  A10 B4                      (Set posture)
    _unrouted/  A2 A8 A9 A11 A12 B6 B8 F1 F2 F4 F5 G1 G2 G3
```

**_unrouted/ note:** Views not assigned a home journey. These are mostly views with no journey `spine` or views with `journeys:[]`. Cross-reachable views (C1, C3) ARE routed to their home journey (J3) but have `cross_journeys[]` refs.

### 3.2 Per-surface spec fields (all GENERATED)

Each `.json` contains: `id` · `area` · `title` · `platforms[]` · `represents[]` · `status` · `home_journey` · `journeys[]` · `cross_journeys[]` · `addresses[]` (the registered addresses this view MUST carry) · `build_to` (components, design_lint command, tokens path)

The **directory = journey spine** (tree holds structure); **address-refs = web** (cross_journeys reconstructed by `navgraph.py`).

---

## 4 · The View Inventory (register.json)

### 4.1 Views summary

| Status | Count |
|---|---|
| planned | 33 |
| quality-passed | 9 |
| redo-pre-audit | 1 |
| **Total** | **43** |

**quality-passed views** (FORM-grounded, design-critic vetted):
- A11 — Portals (portal node live transclusion treatment)
- A12 — Workshop (full-detail node surface)
- B4 — Presence dial, desktop + mobile (8 real modes, dial treatment of dropdown)
- B6 — The twin (provenance grading gold/working; NO confidence scores)
- C5 — Replay / decision trajectory audit
- D6 — Wire failure & lifecycle states (6 real dispatch returns)
- D7 — Self-mod revert (single latest only; multi-entry labelled proposed)
- E1 — Live model fleet (real model registry data; screen is build-required/proposed)
- F4 — Activity / now + live event stream

**redo-pre-audit:** A2 (Canvas — running chain) — existing file carries fiction (4 kinds, await status); must regenerate grounded.

### 4.2 Features by area (76 total)

| Area | Count | Notes |
|---|---|---|
| rhm | 17 | Most features — includes proposed (RHM-identity, RHM-presence, etc.) |
| inbox | 9 | Mix of built, proposed, and standard |
| nodes | 8 | 2 live kinds only (process, content) |
| engine | 7 | Scheduler core |
| wire | 7 | Mix of built and build_required |
| selfmod | 5 | propose/apply node/panel/extension + revert |
| walk | 4 | walkthrough organ |
| events | 3 | SSE, now-view, log |
| canvas | 6 | compose, drag, zoom, layers, multigraph |
| models | 2 | registry, embedding chain |
| run | 2 | run/state + status dots |
| gov | 2 | consequence tiers + operator-only resolve |
| intro | 1 | capabilities() |
| frame | 1 | legacy skeleton (build_required) |
| voice | 1 | two-way voice |
| workshop | 1 | full-detail node surface |

**build_required features** (FE not yet built): `ENG-branches-pause`, `CAN-multigraph`, `WIRE-intent`, `FRM-divergence`

**proposed features** (proposed, not-yet-built, labelled in register): `CAN-brand`, `RHM-identity`, `RHM-presence`, `RHM-process`, `RHM-status`, `RHM-thinking`, `WIRE-layers`, `WIRE-trail`

### 4.3 Journey sequences

| ID | Goal | Spine | Steps |
|---|---|---|---|
| J1 | Compose & run a process | YES | A1 F3 A3 A4 A7 A5 A6 D3 |
| J2 | Leverage models & embeddings | no | E1 A7 E2 E3 |
| J3 | Direct a self-build (the wire) | YES | D1 C1 C2 D2 C3 D6 |
| J4 | Be walked through a decision | YES | B3 B7 B2 B5 |
| J5 | Triage the inbox | no | C1 C4 C2 |
| J6 | Capture an idea mid-flow | no | D4 |
| J7 | Operate from mobile | YES | C1 C3 B1 B2 A5 |
| J8 | Grow the system | no | D5 D7 |
| J9 | Set posture (presence + context) | no | B4 A10 |

**4 spine journeys** (J1, J3, J4, J7). All 9 storyboard statuses are `planned`.

### 4.4 Coverage gaps (features with no view)

From check-report.json, 6 features have no mockup coverage:
1. `ENG-branch` — per-port branching + pruning (gate)
2. `ENG-branches-pause` — branches/pause (engine-only, no FE) — also build_required
3. `ENG-volatile` — VOLATILE bypass
4. `FRM-divergence` — legacy skeleton served at / — also build_required
5. `INB-target` — click-to-thing navigation
6. `WALK-session` — review session as a graph

### 4.5 Area definitions

| Area | Description |
|---|---|
| A | The operating surface (canvas) |
| B | Right-hand-man + review/walkthrough organ |
| C | Inbox + decisions (chief-of-staff) |
| D | Self-build / the wire (act on outputs) |
| E | Models + embeddings |
| F | Frame, settings, system |
| G | Responsive system |

---

## 5 · The Mockup Corpus (23 HTML files)

**Path:** `design/mockups/`
**Total:** 23 HTML files (20 view-registered, 3 extra special-purpose)

### 5.1 Registered mockups (from corpus-meta.json + register.json produced[])

| File | View | Platform | Status | Notes |
|---|---|---|---|---|
| A1-canvas-empty-desktop.html | A1 | desktop | planned | D-1 reconcile: was over-claimed quality-passed |
| A2-canvas-desktop.html | A2 | desktop | redo-pre-audit | pre-audit fiction; regenerate grounded |
| A2-canvas-mobile.html | A2 | mobile | redo-pre-audit | same |
| A3-inspector-desktop.html | A3 | desktop | planned | D-1 reconcile: was over-claimed |
| A11-portals-desktop.html | A11 | desktop | quality-passed | grounded, critic-passed 2026-06-05 |
| A12-workshop-desktop.html | A12 | desktop | quality-passed | grounded, critic-passed 2026-06-05 |
| B3-walkthrough-desktop.html | B3 | desktop | planned | D-1 reconcile: was over-claimed |
| B4-presence-dial-desktop.html | B4 | desktop | quality-passed | grounded, critic-passed 2026-06-05 |
| B4-presence-dial-mobile.html | B4 | mobile | quality-passed | native mobile, critic-passed |
| B6-twin-desktop.html | B6 | desktop | quality-passed | grounded (gold/working provenance, no confidence) |
| C1-inbox-desktop.html | C1 | desktop | planned | D-1 reconcile: was over-claimed |
| C3-build-review-desktop.html | C3 | desktop | planned | D-1 reconcile: was over-claimed |
| C5-replay-desktop.html | C5 | desktop | quality-passed | grounded, critic-passed 2026-06-05 |
| D6-wire-states-desktop.html | D6 | desktop | quality-passed | grounded (6 real dispatch returns) |
| D7-selfmod-desktop.html | D7 | desktop | quality-passed | grounded (one real revert; multi-entry proposed) |
| E1-fleet-desktop.html | E1 | desktop | quality-passed | grounded (real model registry data) |
| F4-activity-desktop.html | F4 | desktop | quality-passed | grounded (now-view + real event kinds) |

### 5.2 Special-purpose mockups (not in register.json views[])

| File | Title | Purpose |
|---|---|---|
| IA-desktop.html | The Company — Desktop IA · the commander's bridge (proposed) | Information architecture proposal — desktop |
| IA-mobile.html | The Company — Mobile IA · Board/Talk/Queue/Tune | Information architecture proposal — mobile |
| SCENARIO-PLAYER.html | The Company — Scenario Player · the living instrument IN USE | The gold-primary theme reference source; living instrument demo |
| A2-rhm-mobile-elevated.html | RHM mobile — elevated (390px) | Elevated RHM treatment for mobile |
| A3-settings-elevated.html | Settings — elevated · less form / more instrument | Elevated settings redesign proposal |
| STUDIO.html | Mockup Studio — the design-review portal | The design-review portal tool itself |

**SCENARIO-PLAYER.html is architecturally significant:** It is the source that was used to derive the gold-primary warm theme. The tokens were realised to match it.

### 5.3 Mockup quality bar (7 criteria from register.json)

1. GROUNDED — depicts only real features (no fiction)
2. LINKED — represents[] filled + reachable in coverage{}
3. ON-SYSTEM — links design-system.css; uses tokens + component classes; no bespoke inline
4. RESPONSIVE — reflows; native mobile variant where platforms includes 'mobile'
5. JOURNEY-MOMENT — states which journey-step it is + when it surfaces
6. UX — attention-protecting, recognise-by-sight, RHM-as-thread
7. SELF-DESCRIBING — opens with metadata comment block listing represents[] + code refs

---

## 6 · The _system Machinery

**Path:** `design/_system/`

### 6.1 The scripts (with their generated outputs)

| Script | Input | Output | Purpose |
|---|---|---|---|
| `emit.py` | `tokens.json` + `components.css` | `../design-system.css` | Compiles token registry → CSS |
| `parse.py` | mockups + `addresses.json` | `element-map.json` | Element ⇄ address ⇄ feature ⇄ code map |
| `gallery.py` | `register.json` + mockup files | `../index.html` | Navigable gallery |
| `check.py` | mockups (default) or `--target` app src | `check-report.json` | Structural coherence + design-lint (FORM gate) |
| `refcheck.py` | `code:` refs in register + addresses | `refcheck-report.json` | Forward drift validator (ref → does it resolve?) |
| `symbols.py` | same `code:` refs | `code-symbols.json` | Reverse code index (symbol → who references it) + semantic nearest (X11) |
| `codeedges.py` | `~/company` source (READ-ONLY) | `code-edges.json` | Structural symbol→symbol dependency graph (X10) |
| `blueprint_emit.py` | `register.json` + `addresses.json` | `blueprint/` subtree | GENERATES the machine-readable build-spec |
| `navgraph.py` | `blueprint/surfaces/` + `register.json` | (query) | Reconstructs journey graph; proves it matches register |

### 6.2 Regression tests

One test file per script: `test_emit.py`, `test_parse.py`, `test_check.py`, `test_gallery.py`, `test_refcheck.py`, `test_symbols.py`, `test_codeedges.py`. `.pytest_cache/` present (tests have been run).

### 6.3 State of generated files

- `design-system.css` — present, GENERATED
- `element-map.json` — present, GENERATED
- `index.html` — present, GENERATED (the gallery)
- `check-report.json` — present, last run found 31 should-use-var, 27 candidates, 6 coverage gaps, 2 unregistered orphans, 45 unused addresses, 3 missing CSS, 3 missing address
- `refcheck-report.json` — present; 210 ok, **1 drift**, 4 unverifiable; drift on `suite.py:349` (NODE-ports, points at `__init__` line 267, +82 lines deep in body — review-severity)
- `code-symbols.json` — present; 94 symbols indexed, 4 not-indexable
- `code-edges.json` — present (not interrogated in detail this pass)
- `candidates.json` — 940 element candidates across 23 mockups (the address-candidate pool for future registration)
- `corpus-meta.json` — maps filename → [title, platform, category, base_address] for all 23 mockups
- `generate-config.json` — the guided mockup-edit loop's config (model, mode, instruction_template, routing)
- `orphan-routes.json` — registry of built-but-unwired `/api` routes with `to_wire`/`to_build_ui`/`voice_owned`/`backend_only` disposition tags
- `mechanisms.json` — THE mechanisms registry (Layer-0 analysis floor)

### 6.4 Mechanisms registry (mechanisms.json — 3 registered)

| ID | Tool | What it builds |
|---|---|---|
| `code-ref-validator` | `refcheck.py` | Forward: code ref → does it still resolve? (drift detection) |
| `code-symbol-registry` | `symbols.py` | Reverse: symbol → who references it; + semantic nearest (X11, BGE-M3 `:8001`, degrades-with-warning when down) |
| `code-dependency-graph` | `codeedges.py` | Structural symbol→symbol call/import graph (X10); bounded transitive reach (DEPTH 2-3 hops); `stale[]` for unparseable files |

### 6.5 Extend-by-registration discipline

All three registries (tokens, addresses, mechanisms) use the same pattern: **add an entry → run the script → machinery picks it up**. No surgery. The same discipline as the Company's fractal registry architecture turned onto its own design corpus.

---

## 7 · The CONNECTION-CONTRACT (FE ⇄ Backend ⇄ Corpus)

**Path:** `design/CONNECTION-CONTRACT.md`

The importable spec tagged IS vs SHOULD-BE:

| Concern | IS (live today) | SHOULD-BE (target to build to) |
|---|---|---|
| Grammar | `ui://region/element` full-string grammar (S0 closed) | — |
| State read | `GET /api/capabilities → node_states[*].render` (S5 served) | — |
| Address element | `data-ui-ref="<full string>"` (corpus already full-string; live app migrating from bare refs) | F4 lane: migrate live bare refs to full strings |
| Capabilities record | corpus stores string-list; S0 projection converts to bool-object | — |
| Command | per-verb route table today (not address-keyed) | `POST /api/act` {verb+address+args} (I2 — net-new) |
| Governance | per-route posture today | address → tier (AUTO/SURFACE/CONFIRM/LOCKED) via `tier` field (I4 — SHOULD-BE) |
| Context read | keyword-keyed today | `GET /api/context?address=…` decay-bounded (R2 — net-new) |
| Locus tracking | none today | R1: backend holds operator's current locus |

**7 NODE_STATES:** `idle`, `ran`, `cached`, `stuck`, `failed`, `live`, `empty` (live/empty are portal-only)

**7 whitelisted verbs (IS, E6 enforced):** `run`, `propose`, `build`, `consult`, `show`, `panel`, `extend`

**Click principle (IS):** click INDICATES + CONSENTS — does NOT execute. RHM proposes; consequential action goes through governance + see-and-approve. Canvas RUN stays AUTO (immediate; must not regress).

---

## 8 · The Generate-for-Mockup Loop

**Path:** `design/_system/generate-config.json`

A reconfigurable guided-review loop:
- Model: `default` (dispatcher's configured default; future: pin to model id)
- Mode: `plan` (safe/read-only by default; `apply` graduates to git-revertible change-making)
- Route: `mockup_edit` — authorised to change ONLY one mockup file (scope-enforced)
- `live` route DECLARED but not implemented (raises `NotImplementedError`) — the seam for future mockup→build-intent wire

This is itself a REGISTERED DECLARED CONFIG — all configuration is data, no hardcoded literals in the engine code.

---

## 9 · Notable Gaps, Stale Content, Surprises

### 9.1 STALE / TO-REDO
- **A2 (Canvas — running chain):** marked `redo-pre-audit` — the files exist but contain fiction (4 node kinds, `await` status). Must regenerate grounded before any build uses them.
- **1 refcheck drift:** `suite.py:349` (NODE-ports) — the ref points 82 lines past the intended symbol into the body of `__init__`. Review-severity, not critical, but the worklist entry exists.
- **4 unverifiable refcheck refs** — cannot be confirmed against source (stale or pattern-based)

### 9.2 PLANNED REGIONS WITH NO COMPONENT YET (16 regions)

The majority of the 31 address regions have no React component yet: `board`, `settings`, `chrome`, `studio`, `twin`, `address-help`, `tune`, `grow`, `forager`, `registry`, `rhm`, `cognition`, `mockup`, `run`, `scenario-player`, `scenario`, `models`, `mockup-studio`, `palette`, `queue`, `system`. These are real design surfaces with registered addresses but no FE implementation.

### 9.3 IMPORTANT ARCHITECTURAL DECISION (D-1, 2026-06-07)

`produced[].status` was blanket `quality-passed` in wave-1, but `views[].status` is the **authority**. 7 wave-1 entries were reconciled DOWN: A1, A2 (desktop+mobile), A3, C1, C3, B3 all back to `planned`/`redo-pre-audit`. **gallery.py trusts `produced`** — so these two must stay in sync. A claim of "quality-passed" on a view is only valid when both entries agree.

### 9.4 MOCKUP STATUS: 9/43 views quality-passed

Only 9 of 43 views (21%) are at `quality-passed`. 33 are `planned`, 1 is `redo-pre-audit`. The ~41 views × variants remaining is the wave-2+ backlog. The spine storyboards (J1, J3, J4, J7) are ALL `planned`.

### 9.5 PROPOSED FEATURES MIXED INTO REGISTER

8 features carry `status: "proposed"` — they are design proposals for things not yet in the app. These are: `CAN-brand`, `RHM-identity`, `RHM-presence`, `RHM-process`, `RHM-status`, `RHM-thinking`, `WIRE-layers`, `WIRE-trail`. They are correctly labelled. No mockup should depict them as existing.

### 9.6 PERSONA TOKENS DEFINED-NOT-LIVE

`persona-atlas-*` and `persona-nova-*` tokens are fully defined in the token registry but the live app doesn't set `data-persona` on any element. Switching Atlas/Nova requires controller markup changes — out of the styling lane. These are ready-to-activate but not current.

### 9.7 SPECIAL MOCKUPS NOT IN REGISTER

4 mockups are in `corpus-meta.json` but not in `register.json views[]`: IA-desktop, IA-mobile, SCENARIO-PLAYER, STUDIO, A2-rhm-mobile-elevated, A3-settings-elevated. They are tracked in `corpus-meta.json` under categories "IA proposals" and "Elevated / living instrument". These are exploratory/tool mockups, not build targets.

### 9.8 CANDIDATES.JSON: 940 ELEMENT CANDIDATES

The `candidates.json` holds 940 parsed DOM elements from 23 mockups with their ancestor addresses and whether they are self-registered. This is the raw pool for the address-registration pass — a large backlog of unaddressed elements.

### 9.9 ORPHAN-ROUTES.JSON: BUILT-BUT-UNWIRED API ROUTES

`orphan-routes.json` is a coherence-disposition catalogue of `/api` routes that exist on the backend but have no FE caller. Routes tagged `to_build_ui` include the full `/api/cognition/role|rule|*` authoring surface (propose/edit/delete/dry_run roles, validate/dry_run/attach/detach rules, preview_turn, models_for_role, inputs, field_types) — these have NO FE UI yet. Routes tagged `to_wire` include `/api/knobs` and `/api/run-stats`.

### 9.10 CORPUS IS A READ-COPY (CRITICAL)

`design/README.md` is explicit: `~/company/design/` is a **synced read-copy** of the canonical `build-prep/design/`. Any edit here is silently overwritten. Canonical edits happen at the Windows-side `build-prep/design/` path. This AREA file is being written to `build-prep/company-landscape/` as directed — not into the read-copy.

---

## 10 · Cross-References

- **Gallery:** `design/index.html` (GENERATED) — the navigable view of the whole corpus
- **Canonical source:** `build-prep/design/` (Windows-side)
- **FE app counterpart:** `canvas/app/src/` — the live React app this corpus is the spec for
- **Backend counterpart:** `runtime/suite.py`, `runtime/bridge.py`, `runtime/scheduler.py`, `runtime/governance.py`, `nodes/*.py` — the code refs in the corpus trace to here
- **FORM gate command:** `python3 design/_system/check.py --target canvas/app/src --fail-on` (exits non-zero on off-token literals; the machine half of the FORM gate, AGENTS.md rule 9)
- **Bespoke-element detection:** documented stub in `check.py` for C0 — returns `[]` until the app carries `data-ui-ref` (F4 lane) and the component inventory is reconciled
