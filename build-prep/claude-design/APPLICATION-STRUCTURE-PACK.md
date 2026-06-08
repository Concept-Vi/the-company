# The Application-Structure Pack — the keystone (what Claude Design plugs into)

> **The correction this embodies (Tim, 2026-06-08):** I do NOT build a design system — that would freeze
> *my* aesthetic and make Claude Design produce variations of *my* designs. **The design is Tim's, done
> in Claude Design. Tim owns the design system (he has half; he handles it).** My job is to give Claude
> Design **the application** it currently lacks: the real architecture, structure, component contracts,
> and plug-points that any design plugs INTO — so that everything Tim designs there comes back **in the
> right shape** and integrates easily. I build the sockets; Tim's designs are the plugs.
>
> This is the canonical keystone. It supersedes the earlier worktree version at
> `company-interface/claude-design/APPLICATION-STRUCTURE-PACK.md`. **One home, one-source
> (with BACKEND-SEAM-PACK.md for the backend contract).**

---

## 0 · The framing

**My role is to make the application's architecture VISIBLE and UNDERSTANDABLE so Claude Design can do
the design — not to consume or align to a design system.** Tim owns the design system; it is handled *in*
Claude Design and drops into the token-slots this pack exposes. I never set the aesthetic. I build the
sockets; Tim's designs are the plugs.

**Sockets vs plugs.** This pack exposes a set of named structural primitives (component contracts), surface
skeletons (composition shapes), integration seams (the live backend wiring already declared), and
token-slots (the CSS-variable interface the design system fills). Everything a design plugs into. The
design is the plug; this pack is the socket.

**The two-context seam.** The work divides cleanly across two Claude sessions:

```
JOB A — Claude Design session
  reads:  a scoped repo subdirectory  +  the published design system (Tim's half)
  does:   Tim indicates elements, talks, Claude Design proposes designs
  yields: a BUNDLE — design intent + component structure + styling tokens

JOB B — Claude Code session (me)
  reads:  the BUNDLE from Job A
  does:   merges styling/layout; the seams to ui:// + organ + /api are already declared
  yields: the design in the running app, integrated cleanly
```

Job A reads and designs well because every named part has a declared structure and declared seams. Job B
integrates cleanly because it was born in the application's structure — no re-plumbing required.

**Cognition authoring.** The cognition AUTHORING surface has its own dedicated pair of docs:
- `AUTHORING-FE-HANDOFF.md` at `/home/tim/company/build-prep/concurrent-cognition/` — the integration
  handoff for the frontend (component contracts, seam wiring, backend shapes).
- `AUTHORING-UI-BRIEF.md` (same directory as this pack) — the full Claude-Design-ready brief: role
  authoring, rule authoring, preview-a-turn, the approval loop, and all UX/design laws.

Do not restate those docs here. Cross-reference them for the cognition authoring surface.

---

## 1 · The five layers (what Claude Design plugs into)

```
THE APPLICATION STRUCTURE  (what I expose · what Tim designs into)
│
├─ ① SURFACE SKELETONS ── how parts compose into each surface (the layout shape)
│      studio  = [ Rail │ Stage │ RhmPanel ]
│      canvas  = [ Palette │ Board │ Inspector+AddressHelp+Queue ] + docked RhmPane
│      inbox   = [ three lanes ] …  (one skeleton per surface, from the IA)
│
├─ ② COMPONENT CONTRACTS ── named primitives · STRUCTURE not style
│      Card{ binds:data · emits:events · slots:token-vars }   Rail{…}   Stage{…}
│      RhmPanel{ organ: chat@locus · address_help · up_translate }   Composer{…}
│
├─ ③ INTEGRATION SEAMS ── each part's plug-points to the live backend
│      the ui:// address it carries · the organ calls · the /api + SSE data it binds
│
├─ ④ TOKEN-SLOTS ── the empty styling interface YOUR design system fills
│      --color-* --type-* --space-* --motion-* …  (the contract; not the values)
│
└─ ⑤ CONVENTIONS + LAWS ── where-things-go · click-indicates-consents · reflects-never-owns
```

**Layer ①** — surface skeletons and per-surface designed intent: see §03 below (pasted in full).
FE placement, where Claude Design output lands in the component tree, and the full file-structure map:
see **BACKEND-SEAM-PACK §6** ("Where Claude Design output lands").

**Layer ②** — component contracts (named primitives, bindings, events, token-slots): see §05 Part B
below (component contracts brief reference). The studio's five `StudioKit.tsx` components with full
seam tables: see §05 Part C.

**Layer ③** — integration seams: the full HTTP route table is **BACKEND-SEAM-PACK §1** (all `/api/*`
grouped by subsystem). The SSE event contract (`GET /api/stream`, gapless resume, address-stamped
events): **BACKEND-SEAM-PACK §2**. The address + resolution substrate (`ui://`, `run://`, `code://`,
`indicate()`, `resolveUiTarget`, `element-map.json`): **BACKEND-SEAM-PACK §3**. The
projections (registry-as-data, the generic-renderer pattern): **BACKEND-SEAM-PACK §4**.

**Layer ④** — token-slot contract: see §04 below (pasted in full). The seam-pack does not own this
layer; it lives here.

**Layer ⑤** — conventions + laws: the full 9-law set the FE must honor is **BACKEND-SEAM-PACK §5**
("The LAWS the FE must honor"). The interaction law baked into every surface (click = indicate +
consent, never execute) is restated briefly in §03 §1 below because it is the governing invariant for
all surface design decisions.

---

## ④ Token-Slot Contract — The Styling Interface a Design Fills

### The contract in one sentence

The structure exposes a set of CSS custom-property names (slots). Tim's design system fills the values. Reskinning the interface means changing token values; the structure, markup, and component logic never move.

**Slot = name I own. Value = aesthetic Tim owns.**

Every visual attribute in the running app resolves from `var(--<slot>)`. Hardcoding a hex or px literal directly in a component is a contract violation — `check.py --target … --fail-on` will catch it (see §Lint below). The single source of truth for all slot values is `company/design/_system/tokens.json`. The compiled output `company/design/design-system.css` is generated by `emit.py` and must never be edited by hand. Change `tokens.json`, regenerate, done.

---

### The 7 token groups — what each slot governs

#### Group 1 — Surface tiers

The depth stack of the UI. Every layer of chrome, panel, and canvas maps to one of these surfaces in z-order, deepest to foreground.

| Slot | Governs |
|------|---------|
| `--bg` | Deepest surface — behind everything |
| `--s0` | First elevation surface |
| `--s1` | Second elevation surface |
| `--s2` | Third elevation surface |
| `--s3` | Fourth elevation surface |
| `--line` | Primary separator / border |
| `--line-2` | Secondary separator / border |
| `--tx` | Primary text colour |
| `--tx-2` | Secondary / muted text |
| `--tx-3` | Tertiary / faint text |

A design supplies 10 values and the entire layered-panel hierarchy resolves from them. No per-component colour decisions needed.

---

#### Group 2 — Signal + semantic

The alive/status/identity colours. Each carries a specific meaning the system communicates visually — these are not decorative. The contract is that each slot name IS the semantic; the value expresses it in the current theme.

| Slot | Semantic |
|------|----------|
| `--acc` | Primary identity / accent — the alive, done, value signal |
| `--acc-dim` | Dimmed accent — supporting tone (less prominent alive state) |
| `--acc-glow` | Glow / scrim fill — the ambient halo; semi-transparent |
| `--acc-deep` | Deep / grounded end of the accent range |
| `--await` | Awaiting-input signal — must be hue-distinct from `--acc` |
| `--fail` | Failure / error signal |
| `--cache` | Cached / neutral signal |
| `--ok` | Resolved / success signal |

Important: `--acc` and `--await` must be visually distinguishable at a glance. The current fill achieves this via a two-vivid split (gold-lean vs orange-lean). Whatever values Claude Design supplies, the two-vivid constraint holds — it is a functional requirement of the status vocabulary, not an aesthetic preference.

---

#### Group 3 — Ink on bright surfaces

Text that sits on coloured fills (accent chips, badges, primary buttons). These exist because legibility on a saturated background requires a dedicated near-black ink, not a reuse of `--tx`.

| Slot | Governs |
|------|---------|
| `--ink-accent` | Text on the `--acc` fill |
| `--ink-await` | Text on the `--await` fill |
| `--ink-fail` | Text on the `--fail` fill |

Three slots. Each is set independently so the hue of each ink can be tuned to its background without cross-contamination.

---

#### Group 4 — Node-type visual language

Node kinds get distinct colours so the canvas is scannable by sight. The kind-coding scheme requires that process / content / present / model read as clearly different at a glance. Background (`-bg`) variants are semi-transparent fills; foreground slots are the strong accent used on icons and labels.

| Slot | Governs |
|------|---------|
| `--kind-process` | Process-kind node foreground |
| `--kind-process-bg` | Process-kind node background fill (semi-transparent) |
| `--kind-content` | Content-kind node foreground |
| `--kind-content-bg` | Content-kind node background fill |
| `--kind-present` | Present-kind node foreground (contract-registered; no live node yet) |
| `--kind-present-bg` | Present-kind node background fill |
| `--kind-model` | Model-config accent (config-slot signal, not a node kind) |
| `--kind-model-bg` | Model-config background fill |

**Registry status:** only two live kinds exist (`process`, `content`). `kind-present` is contract-defined and carries a value but has no live node rendering it yet. `kind-model` is not a node kind — it is a config-slot signal that borrows the kind-colour pattern for visual consistency. Source: `company/design/_system/tokens.json`, node-type group notes.

---

#### Group 5 — Typography

The type system. Font-family slots decouple the typeface choices from component code. Size and spacing slots use role names (not px numbers) so a component declares intent (`--fs-title`) rather than a literal that becomes meaningless when the scale is adjusted.

**Font-family slots**

| Slot | Role |
|------|------|
| `--font-display` | Display / heading / serif authority face |
| `--font-mono` | Monospace instrument body — precision reads, controls, values |
| `--font-body` | Base body font (currently aliased to `--font-mono` — the instrument default) |
| `--font-sans` | Sans-serif face (available in the registry; not the instrument default) |

**Size scale** (role-named, not px-named)

| Slot | Role |
|------|------|
| `--fs-micro` | Extreme-small: tags, badges, overflow indicators |
| `--fs-tag` | Tag-level |
| `--fs-meta` | Metadata / timestamp / secondary annotation |
| `--fs-body` | Body text |
| `--fs-lg` | Large body |
| `--fs-title` | Title / label |
| `--fs-display` | Display / heading |

**Rhythm slots**

| Slot | Governs |
|------|---------|
| `--lh-tight` | Line-height for headings |
| `--lh-body` | Line-height for body text |
| `--tr-tag` | Letter-spacing for tags |
| `--tr-label` | Letter-spacing for labels |

---

#### Group 6 — Living instrument (presence, glow, persona)

The depth + motion + presence layer. The ambient glow, orb, and gradient fills that make the interface feel alive. Also houses the per-persona colour families, which are slot-ready for a future persona switcher.

**Primary accent range**

| Slot | Governs |
|------|---------|
| `--gold-hi` | Light end of the primary accent range |
| `--gold-mid` | Mid of the primary accent range |
| `--gold-deep` | Deep / grounded end of the primary accent range |
| `--acc-flow` | Gradient fill — the animated alive surface (orb conic, run strip, active step, send button) |
| `--orb-hi` | Specular highlight on the presence orb |

**Persona families** — two additional personas defined, not yet live

Each persona gets four slots: the accent, the deep accent, the glow scrim, and the gradient flow. The Vi persona uses `--acc` / `--acc-deep` / `--acc-glow` / `--acc-flow` directly (it is the default). Atlas and Nova get dedicated slots so `[data-persona=atlas]` and `[data-persona=nova]` CSS scoping can swap them in without touching any component logic.

| Slot | Persona / Role |
|------|---------------|
| `--persona-atlas` | Atlas accent |
| `--persona-atlas-deep` | Atlas deep accent |
| `--persona-atlas-glow` | Atlas glow scrim |
| `--persona-atlas-flow` | Atlas gradient flow |
| `--persona-nova` | Nova accent |
| `--persona-nova-deep` | Nova deep accent |
| `--persona-nova-glow` | Nova glow scrim |
| `--persona-nova-flow` | Nova gradient flow |

**Atlas and Nova are defined-not-live.** `App.tsx` does not currently set `data-persona`; no persona switcher exists in the running app. The slot contract is ready; the activation wire is future work.

---

#### Group 7 — Shape (space, radius, elevation)

The spatial rhythm. A single modular base-4 ramp governs all spacing; a 3-step radius ladder governs all corner curves; two elevation tokens govern all shadow depth.

**Space ramp** (base-4, 4 · 8 · 12 · 16 · 24 · 32 px)

| Slot | px value | Use |
|------|----------|-----|
| `--sp-1` | 4 px | Tight inset, icon gap |
| `--sp-2` | 8 px | Standard gap (also `--sp`, the legacy alias) |
| `--sp-3` | 12 px | Medium gap |
| `--sp-4` | 16 px | Section inset |
| `--sp-5` | 24 px | Panel padding |
| `--sp-6` | 32 px | Large section gap |
| `--sp` | 8 px | Legacy alias — kept so existing `var(--sp)` refs resolve; maps to `--sp-2` |

The `--sp` alias exists for backward compatibility. New component work should use the numbered slots.

**Radius ladder** (sits on the 4-grid)

| Slot | Governs |
|------|---------|
| `--r-sm` | Small radius — tight controls, tags |
| `--r` | Standard radius — panels, nodes |
| `--r-lg` | Large radius — sheets, cards |
| `--r-pill` | Full round — pill badges, circular elements |

**Elevation + shadow**

| Slot | Governs |
|------|---------|
| `--shadow-color` | Drop-shadow colour base (parameterises all `box-shadow` declarations) |
| `--shadow` | Standard shadow |
| `--elev-1` | Elevation tier 1 — rail / panel depth |
| `--elev-2` | Elevation tier 2 — floating card / sheet depth |

---

### Slots to add — the design gaps Claude Design fills

Five categories exist in the rendered interface but have no registered token group yet. They represent the completion work for this contract. Values here are currently scattered as literals in component code — each category below is a gap Claude Design's first pass should close.

**1. Motion / animation**

No duration, easing, or transition slots anywhere in `tokens.json`. The living-instrument group implies animated presence (`--acc-flow` gradient, the orb glow), but the timing is hardcoded as CSS literals. Proposed slots:

```
--duration-fast    (snap transitions: hover, focus ring)
--duration-med     (UI transitions: panel open, state change)
--duration-slow    (presence: orb breathe, run-strip flow)
--easing-spring    (elastic / overshoot curves)
--easing-smooth    (standard ease-in-out)
```

This is the most visible gap — motion is a design dimension as legible as colour, and it should flow from the registry like everything else.

**2. Breakpoints / responsive**

No `--bp-mobile` / `--bp-tablet` / `--bp-desktop` tokens. Responsive behaviour is expressed as literal `min-width` values in CSS. CSS custom properties cannot be used directly in `@media` queries, but a registered breakpoint set (even as documentation tokens or via `env()` / `@custom-media` via PostCSS) establishes one canonical source rather than scattered literals.

**3. Z-index layer stack**

No `--z-canvas` / `--z-chrome` / `--z-overlay` / `--z-modal` tokens. Stacking context is managed per-region with integer literals. A registered z-index ladder prevents accidental overlap collisions as new regions are added.

**4. Opacity scale**

`--acc-glow` is the one semi-transparent token (rgba at 0.16). There is no general opacity ramp for regions that dim un-focused content. Proposed:

```
--op-muted    (partial-fade: inactive panel, background content)
--op-dim      (stronger fade: ghosted state)
--op-ghost    (near-transparent: placeholder, behind-modal scrim)
```

**5. Icon sizing**

No `--icon-sm` / `--icon-md` / `--icon-lg` tokens. Icon render sizes are px literals today. Icon sizing belongs on the same rhythm as the space ramp.

---

### How a UI element gets an address

Every meaningful DOM element in a mockup or the real React app carries a `data-ui-ref` attribute:

```html
<div data-ui-ref="ui://inbox/build-intent">…</div>
```

This attribute is the join key between the rendered DOM and the address registry at `company/design/_system/addresses.json`. The address scheme has three URI forms:

```
ui://<region>/<element>[/<sub>][@<state>]   ← chrome and panels
run://<graph>/<node>[#<port>]               ← canvas nodes (pattern-based, not enumerated)
code://<file-stem>/<symbol>                 ← code symbols
```

Each `ui://` entry in `addresses.json` declares:

- `region` — which React region renders this element
- `capabilities` — what the element can do as a pointed target: `pointable`, `spotlit`, `presentable`, `openable`, `driven`, `driven-read-only`
- `represents` — the feature-id from `register.json` that this element exposes
- `code` — the file:symbol or `/api/endpoint` that backs it (traceability)
- `howto` — plain-language help text shown in the guide tour / AddressHelp panel

`parse.py` reads all `data-ui-ref` values across all mockup HTML files and joins them against `addresses.json`, producing `element-map.json`. The map flags orphans bidirectionally: used-but-unregistered (fiction or cruft) and registered-but-unused (the addressing backlog).

The `run://` scheme is deliberately **pattern-based, not enumerated** — every graph node receives a `run://<graph>/<node>` address at runtime derived from its node-id. They are infinite-cardinality and are not registered individually; the scheme is the contract.

Current inventory: **45 registered `ui://` addresses** across 15 regions (toolbar, rail, canvas, inspector, inbox, chat, activity, walkthrough, workshop, models, twin, grow, settings, cognition, tabbar). 16 views carry an `address_gap` field where features are represented but no `ui://` address has been registered yet — these are honest signals in the surface specs, not failures to hide.

---

### Design-lint coverage gap

`check.py --target <path> --fail-on` is the FORM gate: it scans `.tsx` / `.css` files under `<target>` for hardcoded off-token literals (hex, rgba, px) and exits non-zero on any finding.

**Observed:** the design-lint fires exclusively inside `Suite._design_critic()` in `company/runtime/suite.py` (lines 7036–7114). It is called per-changed-file during the build dispatch path — only files the current build modified, not the whole `canvas/app/src`. It is:

- not wired to CI (no `.github/` workflows directory exists in `~/company`)
- not a pre-commit hook (all hooks in `.git/hooks/` are `.sample` files — none activated)
- not an npm script (`canvas/app/package.json` scripts: `dev` and `build` only)

**Consequence:** any `.tsx` or `.css` file written directly to `canvas/app/src` — bypassing the build wire — is entirely unguarded against token violations. The contract can be broken silently with no feedback until the next build-wire run hits that file. This is a legibility gap that Claude Design should flag when scoping its first surface work. Closing it requires either a pre-commit hook, a CI step, or an npm lint script that invokes `check.py --target canvas/app/src --fail-on` on every commit.

The bespoke-element detection inside `check.py` is a documented stub (line 97 of `check.py`) that currently returns `[]` — it is wired into `--fail-on` but injects no findings. It graduates with the F4/F1 milestones.

---

## 03 · Surface Layer — per-surface skeletons, relationships, and design intent

> **Sources.** This section is distilled from two bounded reads:
> `claude-design/research/deep/surface-intent.md` (Parts 1–5; the full depth scan) and
> `claude-design/findings/intent-studio.md` (§0–8; designed-vs-built reconstruction for the studio).
> Upstream code-truth cross-refs (`suite.py` function bodies, `IA-desktop.html` structure, `Interactive
> Addressed Surface — Completion Criteria.md`) are passed through from those sources as cited; they were
> not read directly in this pass. Tags are carried from the source: **BUILT** = function body confirmed on
> `main`; **DESIGNED-☐** = named in a Completion Criteria, not yet on main; **DESIGNED** = intent from chat
> or vault; **INFERRED** = synthesis across sources.

---

### 1 · The Interaction Law (baked into every surface)

> **"Click INDICATES + CONSENTS; the RHM proposes in chat; action goes through governance + see-and-approve
> — NOT click=execute."**
> — Tim, 2026-06-04 (surface-intent §1.1; baked into the Interactive Addressed Surface Criteria header)

A click is *attention + consent to consider*, not actuation. Every surface carries this law. The nuance is
in how tier is resolved: the tier comes from the **address's union record** (its governance posture), NOT
from the verb (surface-intent §1.2 / I4). An **AUTO**-tiered address (a bare run/build) acts immediately
— the already-fixed canvas RUN is preserved (surface-intent §1.2/I4/U1). A **CONFIRM** or **LOCKED**
address proposes → see-and-approve → then acts. The law routes on **declared type + consequence + posture,
never on a confidence value or a generic judgement** — mirrored in the Collective Cognition triage (§2.5)
and in governance.py's existing `guard()` + postures (BUILT — the verb-keyed mislabelling is the net-new
bind to fix, not the posture structure).

This is the single architectural invariant that separates click-as-indicate from click-as-execute. Every
surface design must preserve it: the affordance signals which tier the click is in; the RHM does the
proposing; the operator approves. The visible mode signal for the annotate/operate fork (I5) is a
**reserved Tim design call** — build a reasonable default, flag it for him.

---

### 2 · The Information Architecture as Parent — the Commander's Bridge

> Source: surface-intent §§2.2, 4.1–4.5; intent-studio §6; upstream `IA-desktop.html` (structural read via
> surface-intent §4.1).

**The Information Architecture (the commander's bridge) is the one parent surface that PLACES every other
surface as a zone, panel, or progressively-disclosed affordance.** It is not a navigation shell that
switches between screens; it is a **co-resolution surface** where all zones resolve to the *same locus
simultaneously* (surface-intent §4.2).

The IA's reason-to-exist is **simultaneity / the threaded address**: the same `ui://canvas/node/ask` is
visible on the BOARD (selected, gold ring), in the INSPECTOR (config + output + addressed strata), and in
the RHM PANE (a conversation about it) all at once — the operator's eye threads the three. This is Part 1's
R1/R2 (current locus auto-resolving context) **rendered as spatial layout**. Setting the locus by
indicating on the board (I1, DESIGNED-☐) causes every zone to re-resolve to that address. That coherence
IS the demonstration.

**Layout skeleton (BUILT-as-mockup — `IA-desktop.html`, per surface-intent §2.2):**

```
┌──────────────────────────── TOOLBAR (grouped verbs · presence dial · teach) ────────────────────────────┐
│  Run(primary) · layers · fit          [presence: mode·listening]              ☆teach        ⚙settings    │
├──────────┬─────────────────────────────────────────────┬─────────────────────────────────────────────────┤
│  RAIL    │              BOARD (canvas §2.3)             │   INSPECTOR (canvas §2.3 / workshop §2.5)        │
│ (palette │   tldraw · nodes · status-by-light          │   selected node config + output                   │
│  of node │   scenario-player aesthetic (§2.6)          │   ⌖ what can I do here  (address_help · BUILT)    │
│  types)  │   show-me overlay (walkthrough §2.7)        │   💬 comments & chat here  (I6/I7 · BUILT)        │
│          │   portals (§2.4)                            │   ⧗ history at this address  (L3 substrate BUILT) │
│          │                                             │   ⎘ versions of this output  (L6 · DESIGNED-☐)   │
│          │                                             │   ⟲ self-changes here  (L5 substrate BUILT)       │
│          │                                             │   ⟢ code behind this  (S3 / resolve_scope BUILT)  │
│          ├─────────────────────────────────────────────┴─────────────────────────────────────────────────┤
│          │   RHM PANE — scoped to the selected ui:// locus                  │   QUEUE · review (inbox/     │
│          │   "I see the ask node you've selected" · listening               │   build review / wire states) │
└──────────┴───────────────────────────────────────────────────────────────────┴───────────────────────────┘
   ┌ surfaced-everything strip (collapsed affordances — no fiction, named by real route):
     /api/knobs · run-stats · R2-composition · panel/extend · annotations/chats readback ·
     self-change-log · voice-trial debrief                                                 ┘
```

**Every LATENT capability gets a desktop home as a recognisable collapsed affordance** (chip / count /
sparkline / one-row ledger with chevron) — progressively disclosed, not an 8-deep junk-drawer. Named by
real route, no fiction (surface-intent §2.2, DESIGNED).

The studio (§2.1 below) is a **CHILD PAGE** of the IA app in its end-state — not a sibling, not a separate
tool. The rebuild lands the studio as a page of the main app reusing the real RHM organ (intent-studio §3.3,
`MERGE-COORDINATION.md:143`).

**Assembly law (Operable Interface G1/G2, per surface-intent §4.3):** every placed surface is assembled
from the registries, not authored against them. The rail palette from the node-type registry; the look from
`tokens.json`; the addresses from `addresses.json`; the actions through the wire; the modes from the
mode-registry; the context from the spine. A surface that bolt-ons against a bespoke store or a hardcoded
list is *wrong by this law* — which is exactly why the standalone studio is being superseded.

**Surface relationship graph (surface-intent §4.4):**

```
                          IA (commander's bridge) — the parent container
                                          │ places
        ┌──────────────┬─────────────────┼──────────────────┬───────────────┐
     TOOLBAR         BOARD            INSPECTOR            RHM PANE          QUEUE
    (verbs+modes)   (canvas §2.3)   (addressed strata)     (§2.6)          (inbox §2.10)
        │            │  └ portals(§2.4) │                     │              ├ build review(§2.11)
   settings(§2.17)   │  └ walkthrough  ├ I6/I7 comments      │ scoped to    └ wire states(§2.13)
   presence dial     │    (§2.7)        ├ L3 history          │ the locus          │
   (§2.8 modes)      │  └ workshop     ├ L5/§2.14 self-mod   │ (R1/R2)            │ deposits
        │            │    (§2.5)        ├ L6 versions         │                    ▼
        ▼            │                 └ S3 code-behind      └────────────► twin (§2.9) ◄── learning
   mode-registry     ▼                        │                                  │
   (substrate)   model fleet(§2.15)    address_help/up_translate            replay(§2.12)
                 activity/SSE(§2.16)    (BUILT substrate)                   (persist read-back)

  The studio (§2.1) = a CHILD page of the IA app (the rebuild target).
  The Sequences primitive (§3 below) = the loop EVERY zone runs on.
```

**Mobile (INFERRED — surface-intent §4.5):** the phone is not a shrunk desktop but the same interaction
(point · talk · see · approve) thumb-first / voice-first. Simultaneity gives way to single-locus-at-a-time
(one zone foregrounded, others a swipe or voice-call away). Co-presence survives because any device is a
view onto the one server-authoritative session (reflects-never-owns).

---

### 3 · The Sequences Primitive — the one relational loop

> Source: surface-intent §§3.1–3.3; upstream `RHM Walkthrough Organ — Sequenced Systems`, `context-05:150`,
> `Collective Cognition §4`, `Operable Composition` (passed through via surface-intent §3).

**The Sequences primitive is one relational loop — `resolve → present/work → persist → next/trigger` —
that the Company runs at every scale, pointed at different content.** It is not a feature; it is the
**mechanic**. A new capability is a new station on the loop, not a new pipeline (surface-intent §3.2,
INFERRED).

```
   SURFACE             PRESENT              RESPOND               ACT
   (needs-Tim  →  RHM drives the  →  verdict + WHY  →  system acts  →  resolved │ requeue→new work
    → inbox)      UI to it,           recorded,          (governed,       (no-repeat)
                  voice-first          operator-gated)    verdict-derived)
```

> "Read it as a circuit, not a checklist. A break anywhere breaks the organ." — Sequenced-Systems
> (via surface-intent §3.1)

**Why it earns "universal substrate" — three recurring instances (surface-intent §3.2):**

1. **The engine** — graph nodes: `resolve → work → persist → trigger`. A node fires when its inputs
   resolve; output persists to CAS; trigger cascades to fixpoint. (Operable Composition D1; Collective
   Cognition §2)
2. **The walkthrough / review organ** — review-items = nodes, the session = a graph-run, cursor =
   operator-paced readiness, Next = fire. `context-05:150` names the equivalence explicitly. The
   architecture-session proved the scheduler needs zero core change — human-paced readiness is just a
   `go`-gate input on each review-node.
3. **The collective cognition** — the context cascade runs the *same* `resolve → work → persist → trigger`;
   the write-half does four things at once (Collective Cognition §4): context assembly · memory forming ·
   learning (gold-grade grows the twin) · skill development. "One cascade, four functions — which is what
   makes it *cognition*, not a pipeline."

**INFERRED:** because the same loop is the engine, the human-interaction organ, AND cognition, "interact
with any part of the UI" becomes structurally true once every UI thing is a registered, addressed node on
the loop (the spine of §4). The walkthrough-is-a-graph unification *shrinks* the build (reuse the
scheduler, human-paced) rather than adding to it.

**How surfaces use the loop:**
- **Inbox (§4.10)** = the SURFACE station — one queue, one lifecycle, `origin` polarity.
- **Walkthrough (§4.7)** = the full circuit made operable for the human — the sequencer turns the inbox
  pile into a walk.
- **Build review (§4.11) + wire (§4.13)** = the RESPOND/ACT stations — verdict becomes next system action,
  governed, verdict-derived.
- **Twin (§4.9)** = fed by the write-half's learning function on every pass.
- **Replay (§4.12)** = reads the *persist* station back as trajectory.
- **Canvas (§4.3)** = the loop's original instance — every other surface is the same loop pointed at
  different content.

---

### 4 · Per-Surface Skeletons (~17 surfaces)

> Source: surface-intent §2.1–2.17; intent-studio §6 (the surface list); upstream mockup corpus
> `design/mockups/*.html` (structural references passed through). Some surfaces (§2.4/2.5/2.9/2.11–2.16)
> are DESIGNED from the GROUPS list and narratives; IA-desktop was read structurally; studio was read in
> full.

All surfaces compose the same primitives: assembled from the registries (`register.json`, `tokens.json`,
`addresses.json`), carry `ui://` addresses, thread the RHM, and run on the Sequences primitive. The table
compresses; §§1–3 above hold the relational depth.

| # | Surface | Mockup file(s) | One-line designed intent | Composes from | Status |
|---|---|---|---|---|---|
| **2.1** | **Mockup Studio** | `STUDIO.html` (worktree) | Tim's design-review portal: VIEW mockup → indicate element → RHM captures located comment → feedback surfaces as a build-intent | I1+I5+I6+R2+L1 on the mockup corpus; RHM organ reused as right panel | BUILT-standalone (worktree, superseded); end-state = in-app rebuild |
| **2.2** | **Information Architecture** | `IA-desktop.html`, `IA-mobile.html` | The commander's bridge — simultaneity: the same locus threaded across BOARD + INSPECTOR + RHM PANE at once; the parent that places every other surface | All surfaces as zones; the full spine (I1/R1/R2/S3) as spatial layout | BUILT-as-mockup; the parent container |
| **2.3** | **Canvas / operating surface** | `A1-canvas-empty`, `A2-canvas-desktop+mobile`, `A3-inspector` | Core operating surface: compose nodes, wire chains, run, configure, see outputs; the Sequences loop at node scale | Node-type registry; tldraw board; inspector; the loop's original instance | BUILT on `operable-surface` branch (A–G verified by use); needs-tim: drag-to-connect gesture |
| **2.4** | **Portals / transclusion** | `A11-portals-desktop` | Present-in-place: a portal is a resolved-reference window onto another address's output — what the RHM uses to drive the shared surface during walkthrough | `ui_target` locus carrier (BUILT); prior-version window (L6, DESIGNED-☐) | DESIGNED |
| **2.5** | **Workshop** | `A12-workshop-desktop` | Full-detail node view: the deep-inspect surface; the chrome region where self-changes + revert live (`ui://workshop/self-changes` / L5) | Address strata at full depth — history, versions, self-changes, code-behind | DESIGNED + BUILT-substrate (revert, self_changes_at) |
| **2.6** | **RHM presence / scenario player** | `SCENARIO-PLAYER.html`, `A2-rhm-mobile-elevated` | The aesthetic + presence reference — the living-instrument layer (aurora, orb, gold range, status-by-light); the RHM as felt co-presence; sets the visual language for the whole product | Collective Cognition §8 voice-as-conscious-surface; the one design language (Operable Interface H2) | DESIGNED (aesthetic reference; the visual-language substrate) |
| **2.7** | **Walkthrough** | `B3-walkthrough-desktop` | The RHM drives the shared surface step-by-step to direct Tim's attention — system-initiated step-sequences; walkthrough IS a graph: review-items = nodes, cursor = operator-paced readiness, Next = fire | The Sequences primitive (§3); the existing scheduler (zero core change); the camera/spotlight drive | BUILT-forward-drive (present_current / resolveUiTarget); net-new: sequencer/pacing, element-level show, reverse journey (L9) |
| **2.8** | **Presence dial** | `B4-presence-dial-desktop+mobile` | The dial of how much the RHM presents vs. acts — modes as a hierarchical type-registry (≤8 top-level with sub-types), each mode-type carrying context-resolution declarations; modes and context-resolution ARE one system | Mode-registry + per-mode context-resolution declarations; the off/suggest/auto toggle | BUILT-backend (mode-registry + GC3/GC6 runtime setter); deferred: FE mode surface, consent wiring, auto-detector |
| **2.9** | **The twin / model-of-Tim** | `B6-twin-desktop` | The RHM's predictive core — the model-of-Tim that makes `decide-for-me` real and shrinks what reaches Tim over time; fed by located-gold (L4) from every addressed surface | `model_of_tim.py`; `ingest_comment` (BUILT); escalation ladder; the write-half's learning function | BUILT-cold-start (corpus-pending; reasons from explicit principles, doesn't yet predict) |
| **2.10** | **Inbox** | `C1-inbox-desktop` | ONE place where anything needing Tim lands with ONE lifecycle (build flag / decision / verification / idea) — the chief-of-staff; three triage lanes: just-remember · inject-quietly · escalate-now | Sequences SURFACE station; `origin: responsive|generative` polarity; `ui://` target on each item (L8) | BUILT (inbox + COA + surface-output→inbox wired); net-new: three-lane typed triage, L8 target, live-conversation-on-revisit |
| **2.11** | **Build review** | `C3-build-review-desktop` | Where a self-build result is reviewed demonstrate-first before acceptance — the see-and-approve face of the decision→implementation wire; diff-ready, git-reversible, accept/send-back | Sequences RESPOND/ACT stations; L1 (build-intent entry, BUILT-front-door) + L2 (wire trigger, DESIGNED-☐🔒) | DESIGNED (front-door BUILT; trigger unarmed) |
| **2.12** | **Replay / decision trajectory** | `C5-replay-desktop` | The decision-trajectory surface — replaying what happened; the addressed history at scale (L3 generalised); the `coa` decision-compiler records WHY going down, replay reads it back | `address_view` / `decision_view` (BUILT substrate); the trajectory faculty of the context spine | DESIGNED + BUILT-substrate |
| **2.13** | **Wire states / lifecycle** | `D6-wire-states-desktop` | The decision→implementation wire's lifecycle made legible: surface_build_intent → [operator approve] → dispatch_decision → implement.launch (claude -p) → verify → guarded close → surface-for-review | L1 (entry BUILT) + L2 (trigger DESIGNED-☐🔒) + build review (the review face) | BUILT-front-door; trigger deliberately unarmed (🔒) |
| **2.14** | **Self-mod / revert** | `D7-selfmod-desktop` | The ledger of what the system changed about itself with revert at the address (`ui://workshop/self-changes`); "what changed here?" filtered by S3 address→code join | `self_change_log` / `self_changes_at` / `revert_self_change` (BUILT substrate); element-level addressing net-new | BUILT-substrate; net-new: element-level addressing + corpus-side join + the revert-at-address affordance |
| **2.15** | **Model fleet** | `E1-fleet-desktop` | Live chat+embed model fleet (model · kind · alive), registry-fed from `/api/ui_info` and `list_models` — never a baked list (the path-of-least-resistance correctness rule); the latent-gold knobs/run-stats land here | Native model layer; `/api/knobs`; `run-stats`; the "awake subconscious" VRAM working-set view (Collective Cognition §5) | DESIGNED (fleet backend BUILT; the fleet-as-surface, `ui://models` panel = DESIGNED-☐ F8) |
| **2.16** | **Activity / now + events** | `F4-activity-desktop` | The live event stream surface — the engine pushes (SSE `/api/stream`, gapless via `Last-Event-ID`); cross-process co-presence; the substrate S2 stamps addresses onto | SSE + `mergeEvents` seq-dedup + gapless resume (BUILT); addressed events (S2, DESIGNED-☐) | BUILT (SSE solid); net-new: address stamps on events (S2) |
| **2.17** | **Settings** | `A3-settings-elevated` | One consolidated settings surface — config-lab, modes, models, voice, personas — NOT scattered; the two-tier model config (load-time capability vs live per-request knobs) | Mode-registry (E1/E2); model fleet; voice trial; folds the mode surface (GC3) | DESIGNED |

---

### 5 · The Studio's End-State Spec — built vs net-new cut

> Source: surface-intent §§1.0, 1.2–1.3, 1.1; intent-studio §§5, 4, 7.

**The studio's correct end-state (DESIGNED — surface-intent §1.0; intent-studio §5.5, §7):**
> "the studio surface implementing **I1+I5+I6+R2+L1** on the mockup corpus"

That is: click-to-indicate the element's `ui://` address (I1) + the annotate-vs-operate mode signal (I5) +
attach a comment to that address via `annotate` (I6) + auto-resolve context at the locus for the RHM (R2)
+ promote the addressed comment to a build-intent via `surface_build_intent` (L1). The right panel is the
real `chat` organ, not a static textarea.

**BUILT on `main` right now — no build work needed for these (surface-intent §1.3; intent-studio §5.1–5.2):**

| ID | What's BUILT | Location (`suite.py` line) |
|---|---|---|
| I6 | `annotate(address, text, source)` / `annotations_at(address)` — comment thread at a `ui://` address, addressed event emitted | `suite.py:3967` / `4030` |
| I7 | `attach_chat(address, text, role)` / `chats_at(address)` — chat thread at a `ui://` address | `suite.py:4191` / `4223` |
| F1-pres. | `set_presentation_pref(address, pref)` / `presentation_pref_at(address)` — how Tim wants *this* presented, per-address, pin-persistent; up-translate organs consult + apply | `suite.py:4095` / `4133` |
| S3 | `resolve_scope(ui_addr)` — `ui://` → `code://` → file `scope[]`; empty scope → DENY-ALL (fail-safe) | `suite.py:6929` |
| L4 | `ingest_comment(address, text, source)` — annotate + `append_chat` → located gold for the twin, provenance-graded | `suite.py:3995` |
| L3/L5 sub. | `address_view(address)` / `self_changes_at(ui_addr)` / `revert_self_change(sha)` | `suite.py:8199` / `7622` |
| address_help | The 3-leg composed resolver (what_this_is · how_to_change w/ blast_radius · how_to_use) | `suite.py:1959` |
| up_translate | The altitude transformation layer (down/up between Tim's level and technical depths) | `suite.py:5100` |
| `_registry_ui_target` | Stamps a registry-valid `ui_target` into payloads — the locus carrier | `suite.py:5405` |
| Bridge routes | `/api/ui_info`, `/api/scope`, `/api/address-help`, `/api/annotations`, `/api/chats`, `/api/presentation-pref`, `/api/self-changes-at`, `/api/address-history` + POST counterparts | `bridge.py` route table ~199-285 |

**DESIGNED-☐ (net-new — not yet on `main`):**

| ID | What needs building | Shape note |
|---|---|---|
| I1 | Persistent backend locus widen — clicking ships the element's `ui://` as the current locus; `focus` vocabulary widened beyond canvas node-ids | Substrate exists (`_registry_ui_target`); persistent current-locus is the net-new bind |
| I2 | `/api/act` — `{verb, address, args}` → `_dispatch_rhm_action` directly (bypass prose-parse); inherits the 7-verb whitelist + no-self-apply | `_dispatch_rhm_action(dict)` BUILT (`suite.py:1205`); the endpoint is net-new |
| I3 | RHM proposes an approvable affordance in chat (verb + address rendered); approve fires `/api/act`; action runs only on approve | No path today constructs an uncommitted `{verb,address}` affordance (intent-studio §4 G gap) |
| I4 | Address→tier governance bind — tier resolved from the address union record's posture field, NOT the verb; bare run/build stays AUTO | `guard()` + postures BUILT (`governance.py:10-48`); they are verb-keyed today — address-keyed is the bind |
| I5 | Visible mode signal: annotate-vs-operate per click (Tim design call on the visible signal) | Reserved Tim decision; build a reasonable default |
| R1 | Persistent current-locus stored server-side, set on indicate (I1), readable by the RHM | `_registry_ui_target` is the carrier; a stored current-locus is net-new |
| R2 | `/api/context?address=` — single auto-resolver: info at the address (I6 annotations + I7 chats) auto-resolves into RHM context at the locus; relevance/recency decay bounds it | `annotate` docstring says it *feeds* R2; the resolver is net-new (intent-studio §5.4) |
| L1 | Address→intent bind — a comment-at-address becomes a build-intent (`surface_build_intent`) with `scope[]` via S3, surfaced for approval at that address | `surface_build_intent` BUILT on main (wire's production entry seam); the address→intent leg is net-new |
| L2 🔒 | Wire trigger — approve→`dispatch_decision`→`drive_dispatchable`→`claude -p`; `COMPANY_WIRE_PERMISSION=acceptEdits` as a flag; proven once on a throwaway build-intent, then locked | `resolve_surfaced` approve EMITS the resolve event but does NOT call `dispatch_decision`; no production caller exists; `PERMISSION_MODE` default = `plan`. This is built-not-armed by deliberate design |

**INFERRED summary of the gap (surface-intent §1.3):** The *attach-context primitives* (I6/I7/F1/L4) and
the *resolution substrate* (S3/address_help/up_translate/`_registry_ui_target`) are BUILT. What is missing
is the spine that addresses every element (S0/S1/S2/F4), the FORM rebuild that renders on it (F0–F9), and
the interaction loop that makes a click a governed proposal (I1–I4) auto-resolving context (R1/R2) and
closing the build loop (L1/L2). The studio's whole disconnect is that it reinvented the already-built
primitives instead of composing on them (intent-studio §0, §4).

The `CONNECTION-CONTRACT.md` in the worktree is **stale** — its IS/SHOULD-BE tags predate the main build.
Verify every claim about what's live against `suite.py` directly (intent-studio §5.4).

---

*Cross-refs: `BACKEND-SEAM-PACK.md` owns the seam detail for S0/S4/S2/I2/R2 binds.
`AUTHORING-UI-BRIEF.md` owns the FE rebuild approach (F0–F9). This section owns the designed intent,
surface relationships, and the built/net-new cut.*

---

## 05 · How to Add a Region — The Recipe + Studio Per-Surface Brief

*Sources: `company-interface/claude-design/research/deep/fe-structure.md` (direct read, 2026-06-08) · `company-interface/.build/interface/lanes/studio-scaffold.report.json` (direct read, 2026-06-08) · `BACKEND-SEAM-PACK.md` headers only (cross-reference map at §6).*

---

### Part A — The Recipe: How to Add a Region

A region is a carved presentational surface. It holds no domain state, fires no fetch calls, and owns nothing. It reads from `useApp()` and calls controller handlers. The recipe is six steps.

---

#### Step 1 · Create `regions/MyRegion.tsx` from kit primitives + `useApp()`

```tsx
// canvas/app/src/regions/MyRegion.tsx
import { SectionHead, LaneHead, Badge, Surface, EmptyState } from '../components/kit'
import { useApp } from '../AppContext'

export function MyRegion() {
  const { myData, myHandler } = useApp()
  return (
    <div data-ui-ref="ui://myregion" className="myrgn">
      <SectionHead tag="MY-KICKER">my region</SectionHead>
      {myData.length === 0
        ? <EmptyState>Nothing here yet.</EmptyState>
        : myData.map(item =>
            <Surface key={item.id} dataUiRef={`ui://myregion/${item.id}`} onClick={() => myHandler(item.id)}>
              <Badge tone="sig">{item.label}</Badge>
            </Surface>
          )
      }
    </div>
  )
}
```

**Hard rules for the file:**

- No `useState` or `useEffect` for domain state. Local UI-only toggles (open/closed) are the only exception.
- No `fetch` calls. No `import api` in a region file. All I/O is the controller's job.
- No inline styles. No hardcoded hex or pixel values. Token classes only (`.kit-*` and the system classes in `app.css` / `design-system.css`).
- Kit-first: compose from the five primitives — `Surface`, `SectionHead`, `Badge`, `EmptyState`, `LaneHead`. Do not re-invent equivalent markup.
- Root element carries `data-ui-ref="ui://myregion"`. Sub-elements carry `data-ui-ref="ui://myregion/element-id"`. The `Surface` primitive accepts `dataUiRef` prop and forwards it to the DOM — use that prop rather than setting `data-ui-ref` manually on a `<Surface>`.

The reference region (the kit exemplar) is `regions/Inbox.tsx`.

---

#### Step 2 · Mount in a grid cell wrapped in `PanelErrorBoundary`

Import and place inside the `AppContext.Provider` tree in `App.tsx` (`Hud`'s return). Choose the correct cell:

**Right rail** (`.as-panel` — the 330 px right scroll column; stacks below Fleet):

```tsx
<div className="as-panel as-sheet hud panel" data-ui-ref="inspector">
  {/* … existing regions … */}
  <PanelErrorBoundary name="my-region">
    <MyRegion />
  </PanelErrorBoundary>
</div>
```

**In-canvas overlay** (`.as-canvas` — transparent passthrough; re-enable pointer-events on the region's root element):

```tsx
<div className="as-canvas">
  {/* … existing overlays … */}
  <PanelErrorBoundary name="my-region">
    <MyRegion />
  </PanelErrorBoundary>
</div>
```

**Full-viewport modal** (outside `.app-shell`, sibling of `Workshop` / `Settings`; uses `position:fixed` internally, opened/closed by controller state):

```tsx
{showMyModal && (
  <PanelErrorBoundary name="my-region">
    <MyRegion />
  </PanelErrorBoundary>
)}
```

`PanelErrorBoundary` is not optional. Every region that can throw must be wrapped. A panel error renders a contained `"⚠ panel failed"` card; the canvas stays live. The shell-level `name="surface"` boundary is the backstop; per-panel boundaries keep failures isolated.

For the file-structure map of each grid area (class → area → pointer-events → which regions belong) see **BACKEND-SEAM-PACK §6**.

---

#### Step 3 · Add state and handlers to `useAppController.ts`

`AppController` is `ReturnType<typeof useAppController>`. Adding a field to the return object automatically extends the type — no separate interface to maintain.

```ts
// canvas/app/src/useAppController.ts — inside the function body:
const [myData, setMyData] = useState<MyItem[]>([])

async function myHandler(id: string) {
  const r = await api.someEndpoint(id)
  if (r.error) { setNotice('✕ ' + r.error); return }
  setMyData(r.result)
}

// add to the return object (line ~2271):
return { …existingFields, myData, setMyData, myHandler }
```

All regions in the tree can now destructure `{ myData, myHandler }` from `useApp()`. Zero prop-drilling.

---

#### Step 4 · Register `data-ui-ref` addresses in `addresses.json` + run `parse.py`

For every `data-ui-ref` on the region's DOM elements:

```json
// design/_system/addresses.json
{
  "ui://myregion": {
    "region": "myregion",
    "element": "root",
    "capabilities": ["pointable", "spotlit"],
    "represents": "<feature-id from design/register.json>",
    "code": "regions/MyRegion.tsx:12",
    "howto": "Plain-language description of what this element does."
  },
  "ui://myregion/item-id": {
    "region": "myregion",
    "element": "item-id",
    "capabilities": ["pointable"],
    "represents": "<feature-id>",
    "code": "regions/MyRegion.tsx:18"
  }
}
```

Then run:

```bash
python3 design/_system/parse.py
```

This refreshes `element-map.json` (element ↔ address ↔ feature ↔ code). An address in the code but absent from `addresses.json` is flagged as an orphan — the region works at runtime, but `show-me` / `address-help` / `history` cannot resolve it. Short-term orphans are tolerated (Inbox.tsx documents one explicitly); all must be registered before the corpus degrades.

The full relationship between `data-ui-ref`, the `indicate()` keystone, and the `resolveUiTarget` show-me path is documented at **BACKEND-SEAM-PACK §3**.

---

#### Step 5 · Run the FORM gate (`check.py`)

```bash
python3 design/_system/check.py --target canvas/app/src --fail-on
```

Scans source for off-token literals: hardcoded hex values, bespoke `px` sizes not mapped to tokens. Exits non-zero on violation. A new region using only kit classes and token variables passes clean. This is the design-lint gate (AGENTS.md rule 9). **Do not merge a region that fails this gate.**

---

#### Step 6 · If the region has a mockup: register in `register.json` + run `gallery.py`

Place the mockup HTML at `design/mockups/MY-surface.html`. Register the view in `design/register.json` under the appropriate journey, with the `data-ui-ref` address linking the mockup to the live element. Then run:

```bash
python3 design/_system/gallery.py
```

`design/index.html` is **generated** — never edit it directly. For the full corpus → gallery → annotation → RHM-locus pipeline see **BACKEND-SEAM-PACK §6**.

---

### Part B — Component Contracts (brief reference)

These are the structural constraints every new region inherits. For the full placement map see **BACKEND-SEAM-PACK §6**.

**`kit.tsx` — the five primitives** (`canvas/app/src/components/kit.tsx`):

| Primitive | Purpose | Key prop |
|---|---|---|
| `Surface` | Row / card interaction wrapper | `dataUiRef` forwards to DOM `data-ui-ref`; `tone` drives edge tint |
| `SectionHead` | Titled heading with optional kicker + aside slot | `tag` = uppercase kicker; `aside` = right-aligned action/count |
| `LaneHead` | Collapsible lane header | `tone`, `count`, `onToggle`, `open` |
| `Badge` | Read-state label | `tone` drives colour; the five tones are the signal vocabulary |
| `EmptyState` | Honest rest state | Never leave a blank gap |

**Tone vocabulary** — `'sig'` (done/ok, mint green) · `'await'` (needs action, amber) · `'fail'` (error, red) · `'wire'` (building/in-flight, blue) · `'dim'` (neutral/background). Tone is meaning, not decoration.

**`api.ts`** (`canvas/app/src/api.ts`) — the sole I/O boundary. All `fetch('/api/…')` calls live here. The controller calls `api.*`; regions never import or call it. Error normalization via `jr`: non-2xx returns `{ error: msg }` as a value (callers branch on `if (r.error)`); never a throw in normal operation.

**`useAppController` + `AppContext`** (`canvas/app/src/useAppController.ts`, `AppContext.ts`) — `useAppController(editor)` is called exactly once in `Hud`. The controller's return object is the `AppController` type (`ReturnType<typeof useAppController>`). All regions read it via `useApp()`. The one-hook pattern and the inferred type are both load-bearing — do not split the controller or declare the interface separately.

**`registryStore.ts`** (`canvas/app/src/registryStore.ts`) — external store readable by `useSyncExternalStore` (and by imperative `getOINFO()` / `getMODEL_OPTIONS()` calls inside tldraw, which cannot reach React context). Holds: `OINFO` (type → ports/schema/kind), `MODEL_OPTIONS` (kind → name list), `UI_INFO` (address → title/meta), `NODE_STATES` (stateId → label/render). Regions read `NODE_STATES` and `UI_INFO` through the controller; they never call `registryStore` directly.

---

### Part C — Studio Per-Surface Brief

The studio is the `Review.tsx` region — a **view-level switch** that covers the canvas entirely when `view === 'review'` (`.app-shell` becomes `display:none`). It is not a grid cell inside the normal layout; it is a full-screen `position:fixed` surface that co-exists with the tldraw board running silently underneath.

Its declared status is **STRUCTURE-BUILT / LOOK-PENDING**. The wiring is complete and verified by use. The deliberate aesthetic is what Claude Design delivers into it. The surface itself says at its root: *"This is the surface skeleton. The structure the look plugs into. The deliberate aesthetic is Claude Design's; this is the socket."*

---

#### Structure: three regions

```
┌─────────────────────────────────────────────────────┐
│  STUDIO (Review.tsx — view==='review', full-screen) │
│  ┌─────────┬───────────────────┬───────────────────┐ │
│  │  Rail   │      Stage        │    RhmPanel       │ │
│  │         │                   │  ┌─────────────┐  │ │
│  │ corpus  │  sandboxed iframe │  │  AddressHelp│  │ │
│  │ gallery │  device stage     │  │  RhmChat    │  │ │
│  │ (Cards) │  (phone/desktop)  │  │  Composer   │  │ │
│  └─────────┴───────────────────┴──┴─────────────┴──┘ │
└─────────────────────────────────────────────────────┘
```

Named primitives live in `canvas/app/src/components/StudioKit.tsx`. Seam descriptors live in `canvas/app/src/components/StudioSeams.ts` (pending seams THROW a labelled error — never a silent no-op).

---

#### The five `StudioKit.tsx` components

**`Rail`** — the corpus gallery. Binds `corpus[]` from `/api/corpus` (registry-is-truth: mockup files on disk joined to curated meta; never a hardcoded list). Renders `Card` items grouped by kind. `EmptyState` on corpus error — fail-loud. Emits `onSelect(file, address)`.

**`Card`** — one gallery item. Binds `{ file, title, platform, group, address }`. Emits `onSelect(file, address)` — this INDICATES the locus (`indicate(address)`) and loads the mockup into Stage. A card click never executes anything. Carries `data-ui-ref={address}` on its root. Composes kit `Surface` + `Badge`. Token-slots: `--studio-card-*`.

**`Stage`** — the device stage. Binds `reviewMockup` (filename) + `reviewAddress` (locus). Renders a sandboxed `<iframe>` served same-origin from `/mockups/<file>`. Phone / desktop toggle. Token-slots: `--studio-stage-*`. Current constraint: element deixis inside the iframe is pending (in-frame clicks cannot propagate `data-ui-ref` to the parent via the sandbox boundary; the locus is the whole reviewed surface until that seam lands).

**`Composer`** — addressed-feedback surface. Binds the current `locus` + the `annotations` thread for that locus (shared store, keyed by address). Two emitters:
- `onComment` → `POST /api/annotate` → into the shared address-keyed annotation store (not a parallel jsonl).
- `onRequest` → `POST /api/intent-at` → the build-intent door from a locus (plan-mode; the `I3` approval path is wired).
Token-slots: `--studio-composer-*`. `onDocClick` is excluded so a click on the composer itself never re-indicates the locus.

**`RhmPanel`** — mounts the REAL `RhmChat` organ at the current mockup locus. `sendChat` ships `focus={ selected: [mockup://<file>, ui://<address>] }` so every chat turn is grounded at the locus. Also mounts `AddressHelp` (what-this-is + what-a-change-touches, from `GET /api/address-help?address=`). Token-slots: `--studio-rhm-*`.

---

#### Seams the studio uses

| Seam | Direction | Route | What it does |
|---|---|---|---|
| Corpus read | → FE | `GET /api/corpus` | Registry-is-truth index of mockup surfaces; gallery binds it |
| Locus indication | FE → | `indicate(address)` (controller) | Card click sets the locus; RhmPanel + AddressHelp track it |
| Chat at locus | → BE | `POST /api/chat` with `focus.selected=[mockup://…, ui://…]` | R1 locus context — reply grounded at the indicated surface |
| Annotate | → BE | `POST /api/annotate` | Comment written to shared address-keyed store |
| Annotation read | → FE | `GET /api/annotations?address=` | Comment thread read-back for current locus |
| Address help | → FE | `GET /api/address-help?address=` | What-this-is + change-scope for the locus |
| Build intent | → BE | `POST /api/intent-at` | Explicit change-request from the locus (the `I3` approve→`/api/act` path is wired) |
| Act / approve | → BE | `POST /api/act` | Approve a proposed action from the RHM (I2 dispatch path) |

Pending seams (net-new, not yet wired): persistent server-side current-locus (`R1` standing locus beyond per-chat `focus.selected`); address→governance tier resolution (`I4`); auto comment→build-intent promotion (`L1`); in-frame element deixis inside the sandboxed iframe. All are declared with THROW-labelled descriptors in `StudioSeams.ts`.

---

#### Token-slots — `--studio-*`

All studio look-values read from CSS custom properties declared on `.studio-shell` with neutral structural defaults mapped to system tokens. Claude Design redefines these variables; the structure never moves. This is the layer-4 membrane.

```
--studio-card-*        Rail gallery card appearance
--studio-stage-*       Device frame + iframe surround
--studio-composer-*    Composer panel
--studio-rhm-*         RhmPanel surround
```

The system token layer underneath (`design-system.css` → `tokens.json`) provides the upstream values the `--studio-*` slots initially alias. Redefining a `--studio-*` variable overrides the structural default without touching any underlying system token.

---

#### Laws the studio honors

**Click indicates + consents, never click = execute.** A `Card` click indicates the locus and loads the mockup. Nothing runs. The RHM proposes; the operator sees and approves. Action flows through the `I3` consent path (`POST /api/act`).

**Reflects-never-owns.** The studio shows backend truth — corpus via `/api/corpus`, comments via `/api/annotations`, address context via `/api/address-help`. The locus is the one `indicate()` sink. No parallel store, no authoritative local state.

**Fail-loud.** Corpus error → visible `EmptyState`. Annotate or intent POST failure → visible notice from controller. Pending seams THROW a labelled error (never a silent no-op or a fake success). StudioSeams.ts defines `callPendingSeam()` which always throws.

**Registry-is-truth.** The gallery is driven by `/api/corpus` (disk truth). Comments go to the shared annotation store (not a bespoke parallel jsonl). Addresses are authored in `addresses.json`.

**Unstyled structural scaffold.** The studio is deliberately the one surface in the FE built as an empty socket. Everything else in the FE (all 18 regions except Review.tsx) already has the gold look applied. The studio's look is not a gap — it is the deliverable. Claude Design fills the token-slots; the structure stays.

---

*This section complements BACKEND-SEAM-PACK §6 (the placement map, route-to-region grid, and full file-structure map). Cross-reference §3 for the address + resolution substrate, §5 for the full law set, and §1.2 for the address-keyed API routes used by the studio seams.*

---

## STATUS — what exists, what is net-new to build

### What this pack establishes (as of 2026-06-08)

- The full canonical framing (§0): architecture-visible / sockets-vs-plugs / Job A + Job B / cognition cross-refs.
- The five-layer skeleton (§1) with tight cross-refs to BACKEND-SEAM-PACK (not restated here).
- The complete token-slot contract (§04): all 7 groups, the 5 gap categories, addressing scheme, lint coverage.
- The complete surface layer (§03): the interaction law, IA skeleton, Sequences primitive, all 17 surface skeletons, studio end-state spec with built/net-new cut.
- The region recipe and studio per-surface brief (§05): the 6-step recipe, component contracts, studio three-region structure, StudioKit components, seam table, studio laws.

### Net-new backend work (the tiny genuine gaps — see also BACKEND-SEAM-PACK §7)

| ID | What | Shape |
|----|------|-------|
| R2 | `/api/context?address=` | Single auto-resolver: I6 annotations + I7 chats → RHM context at locus; relevance/recency decay |
| I1/R1 | Persistent server-side current-locus | `_registry_ui_target` carrier exists; stored + gettable locus is net-new |
| per-address tier | Address union record posture field | Governance bind: tier resolved from address record, not verb |
| L1 | Auto comment→intent promotion | `surface_build_intent` + S3 scope[] already exist; address→intent leg is the bind |
| I2 | `/api/act` endpoint | `_dispatch_rhm_action(dict)` BUILT; the HTTP endpoint is net-new |
| In-frame deixis | Element-level addressing inside sandboxed iframe | Sandbox boundary makes propagation non-trivial; seam declared, solution open |

### One-source note

**BACKEND-SEAM-PACK.md** is the canonical one-source for: HTTP routes, SSE contract, address substrate, projections, the 9 FE laws, FE placement map. This pack does not restate those — it cross-references them. Changes to the backend contract go in the seam pack; the structure pack stays current with surface + design-into-it framing.

**AUTHORING-FE-HANDOFF.md** + **AUTHORING-UI-BRIEF.md** own the cognition authoring surface entirely. Cross-reference only.
