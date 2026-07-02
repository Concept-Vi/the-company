# AREA-18 — UI-Kits Version Catalogue (to fuse, not to choose)

**Wave-3 coverage+unification companion.** Territory: `/home/tim/company/design/claude-ds/ui_kits/` — three parallel product-UI versions (`vi/`, `platform/`, `virtual-hub/`). **The lens (Tim's):** these are MANY UIs, NONE canonical/in-use/final; each carries unique qualities; the job is to **identify them all and fuse the best parts into one conversational-glyphgraph surface** — never "pick the good one." I have read every `.jsx`, every `.css`, every `index.html` and `README.md` in all three kits (line counts below). Evidence is marked **Observed (file:line)** / **Inferred** / **My-idea**.

**Coverage:** `vi/` 8 files read whole (ViKitApp 240, vi.css 343, ChatPanel 108, OutputPreview 91, TaskTree 35, ViMark 23, ViStatusPill 23, index.html 24). `platform/` 12 files read whole (platform.css 396 full, PlatformApp 44, PlatformSidebar 77, ActionToolbar 43, TopBar 15, Chats 11, screens/HubSettings 95, Calendar 96, Gallery 51; `BrandKit.jsx`, `Stub.jsx` **skimmed via README only** — settings-form + placeholder, not load-bearing here). `virtual-hub/` 11 files read whole (hub.css 379 full, HubApp 78, CaptureComment 94, InfoPanel 37, SharePanel 38, FloorplanOverlay 43, QuickMenu 25, HubBug 22, MenuButton skimmed — 10-line pill). All three link `../../colors_and_type.css` then a local kit CSS — **one shared token base, three layout grammars on top** (Observed: each `index.html:7-8`).

---

## 0 · The headline recognitions (the "yes, but actually the code does X")

Three pieces of latent machinery that the ANCHOR's talk→graph pipeline needs and that **already exist in these kits under other names** — bank them as inherited, do not reinvent:

1. **`FloorplanOverlay.jsx` IS a latent glyphgraph canvas.** *(Observed: `virtual-hub/FloorplanOverlay.jsx:4-17`)* Rooms are objects positioned by **percent** (`{left, top, w, h}`), nav-dots positioned by **percent** (`{x, y}`) with an **`active` pulse state** (`hub.css:255-265` `.vh-fp-dot.active::after` dashed-ring pulse), and **click-to-pick** (`onPick?.(d.id)`). That is *nodes on a 2-D canvas with positional layout + per-node active state + node interaction* — the **manual/static ancestor of reactflow auto-place**. The glyphgraph canvas is this pattern with (a) data-driven nodes instead of a hardcoded `rooms[]`, and (b) an auto-layout engine writing the percents instead of a designer.

2. **`CaptureComment.jsx` IS a latent node-detail popup, fully built.** *(Observed: `virtual-hub/CaptureComment.jsx:13-19` + `hub.css:267-377`)* Click a point on the stage → popup anchored at **clamped `{x,y}`** (`Math.min(Math.max(x-160,16), innerWidth-336)`) + a **tap-marker at the exact click point** (`.vh-tap-marker`). That is *exactly* "click a glyph-node → detail card anchored to it, clamped inside the viewport." It even ships a **4-state status pill that cycles** (pending/approved/resolved/rejected, `CaptureComment.jsx:6-11,73-81`) and a **rich rich-text composer toolbar** (B/I/S/code/list/Aa/@/emoji/attach, `:55-66`). Direct reuse for the glyphgraph node-detail + node-annotation.

3. **The "live / streaming" visual grammar already exists end-to-end in `vi/`.** The talk→graph loop needs to show *reading, generating, arriving, narrating, blocking*. vi/ already has the whole vocabulary: **`ReadCard`** Reading→Read with an animated mark (`ChatPanel.jsx:17-25`), **`ViStatusPill` live-pulse** (`ViStatusPill.jsx` + `vi.css:101-105` `@keyframes vi-pulse-pill`), **`OutputPreview` section-states** done/pending/gap + **skeleton shimmer** (`OutputPreview.jsx:2-13`, `vi.css:312-323` `@keyframes vi-skel`), and **`vi-node` four states** idle/active/done/blocked with a **pulsing dot** + **layer-connector** (`vi.css:249-271`, `@keyframes vi-dot`). This is the streaming/narration palette for "watch the graph build itself."

---

## 1 · What EACH kit IS + its unique qualities

### A · `vi/` — the AI-workspace three-pane (the closest ancestor of the glyphgraph surface)

**What it is** *(Observed: `vi/README.md:5-15`, `ViKitApp.jsx`)*: "Vi Workspace" — a 240px nav rail + a **three-pane workspace** (`vi.css:46-51`: `grid-template-columns: 380px 1fr 420px`):

| Pane | Content | File |
|---|---|---|
| **Left · Conversation** | user↔Vi chat; Vi shows its work (entity-read cards, missing-field prompts, approvals); composer at the bottom | `ChatPanel.jsx` |
| **Centre · Task tree** | Vi's 3-layer agent architecture, live (plan → spawn clones → execute) | `TaskTree.jsx` |
| **Right · Output preview** | the asset being built, fills in real time | `OutputPreview.jsx` |

**Interaction model** *(Observed: `ViKitApp.jsx:45-93`)*: a **stepped state machine** (`step` 0→4). One `send()` advances; `setTimeout` auto-advances reading; submitting a missing field advances. Each step is a **snapshot tuple** of `{chat messages, task-layer states, filled-fields, composer hint, status-pill}` (`:80-93`). Derived-state-driven render: `layers`, `filled`, `messages`, `statusPill` all computed from `step`. **This is the single most glyphgraph-relevant structure in the territory** — it is already "a conversation that drives a live-building structure and a live-filling output," which is exactly the talk→graph→narrate loop, only with a *fixed script* instead of a model pipeline.

**Unique qualities to harvest:**
- **The three-zone talk+work+result frame itself** *(Observed: `vi.css:46-71`)* — separate scroll regions, `min-height:0` flex panes, pane-headers with a title + a live sub-pill. This is the load-bearing shape for the glyphgraph instrument (talk-zone / graph-zone / detail-zone). **(My-idea:** rename centre from "task tree" to "the glyphgraph canvas"; see the tension in §3.)
- **The live-work vocabulary** (§0.3) — `ReadCard`, `ViStatusPill`, `OutputPreview` states, `vi-node` states. The richest "AI is doing something right now" palette of the three kits.
- **`MissingPrompt`** *(Observed: `ChatPanel.jsx:27-44`)* — a dashed-border "Missing · <source>" card with an inline input that resolves in place to a ✓. This is the **gap-resolution-in-conversation** primitive — directly the glyphgraph's "no, the buyer's gone cold / what's the price?" correction loop (ANCHOR §2 "you correct it by voice").
- **`ViMark`** *(Observed: `ViMark.jsx:2-22`)* — a diamond avatar with an SVG **line-fill `<pattern>`** that animates (`<animate>` on stripe opacity) when `animated`. A self-contained, no-dependency "thinking" indicator. **(Inferred:** the glyphgraph's nodes are themselves glyphs; ViMark's pattern-fill-as-state idea generalises — a node's *fill* can encode "being computed" exactly as ANCHOR §3 says fill/colour encode state.)
- **`OutputPreview` as a structured live-fill artifact** *(Observed: `OutputPreview.jsx:16-88`)* — sectioned (`Brand & palette` / `Feature stats` / `Description` / `Starting price` / `Agent contact`), each with done/pending/gap and a footer of output formats (PDF/DOC/HTML) that light up on finalize. This is a **second, non-graph rendering of the same underlying data** — relevant to ANCHOR §8 "how does a bound glyphic co-exist with a talk-generated one": the detail-zone can show the *structured read-out* of the selected node alongside the graph.

### B · `platform/` — the creator dashboard (the chrome + the catalogue surfaces)

**What it is** *(Observed: `platform/README.md`, `PlatformApp.jsx`)*: the creator-side dashboard. A **two-zone shell** (`platform.css:14-19`: `grid-template-columns: 280px 1fr`) — a left rail + a scrolling content column — with screen routing (`PlatformApp.jsx:16-21`). Default screen: Gallery.

**Unique qualities to harvest:**
- **The richest, most complete component/token layer of the three** *(Observed: `platform.css:143-166`)* — a full **button system** (`--primary/--outline/--dashed/--ghost/--dark`), a baked-in search input (`:168-179`), a gold-fill checkbox with a CSS-drawn tick (`:256-275`), a dropzone (`:278-294`), a soft-gold `cv-panel` settings container (`:220-236`). These are the **form/control vocabulary** the glyphgraph's settings/inspector affordances will reuse.
- **`ActionToolbar`** *(Observed: `ActionToolbar.jsx:24-41`)* — Select / Filter / Sort / Search / Clear / Create / Upload, all with hand-rolled inline-SVG icons (`:14-22`). A reusable **operate-on-a-collection toolbar**. **(My-idea:** a glyphgraph view of many nodes wants exactly this — filter/sort/search the graph; Create = add-node; the toolbar transfers.)
- **`Calendar`** *(Observed: `Calendar.jsx`, `platform.css:322-390`)* — a genuinely distinct surface: a 7-col month grid, multi-coloured **`CalChip` task-chips with status dots** (`green/yellow/orange/red/blue/purple/gray`, each with a tinted bg + dot colour), plus a "Top Tasks" row. The **chip+dot+colour-coded-status grammar** is a strong precedent for the glyphgraph legend (a node's state→colour mapping is exactly the chip's `kind→{bg,dot}` map).
- **`Gallery`** *(Observed: `Gallery.jsx`, `platform.css:196-218`)* — a media-tile grid with **multi-select** (`useState(new Set)`, `:13-19`), a ✓ selection badge, and a grid/list **view-toggle** (`:26-33`). The select-set + view-toggle pattern transfers to "select multiple glyph-nodes."
- **`Chats` floating pill** *(Observed: `Chats.jsx`, `platform.css:296-315`)* — an always-visible bottom-right `position:fixed` conversation entry-point with an unread count badge. A **third, minimal form of "messaging"** (see overlap §2).
- **`HubSettings`** *(Observed: `HubSettings.jsx`)* — the densest **config surface**: two-col fields, three-col checkbox groups, URL-preview with monospace + accented segments, a live-toggle state object (`s`, `toggle(k)`). The **everything-is-a-toggle config grammar** for the glyphgraph's options panel.

### C · `virtual-hub/` — the immersive viewer (the canvas-with-floating-overlays version)

**What it is** *(Observed: `virtual-hub/README.md`, `HubApp.jsx`, `hub.css`)*: the buyer-facing immersive viewer. **Photo-first / canvas-first**: a full-bleed background fills the viewport (`hub.css:12-39` `.vh-stage`), and **all UI floats on dark translucent surfaces over it** (`backdrop-filter: blur`, `rgba(31,26,18,.7)` throughout). This is the **opposite layout philosophy to vi/platform** (which are panelled grids): here the *canvas is the whole screen* and panels are overlays.

**Unique qualities to harvest — this is the most directly canvas-relevant kit:**
- **Canvas-first stage with floating overlays** *(Observed: `HubApp.jsx:33-73`, `hub.css:12-45`)* — a single `relative` stage; everything (`HubBug`, `MenuButton`, `QuickMenu`, panels, capture) is `position:absolute` with `z-index` layering. **This is the glyphgraph instrument's most likely base layout** *(My-idea)*: the reactflow canvas IS the stage; talk-zone, detail-card, legend float over it — closer to the ANCHOR's "interactive canvas you watch build itself" than vi/'s rigid 3-column grid.
- **Click-anywhere-on-canvas → anchored detail** (§0.2) — `CaptureComment` clamped popup + tap-marker. The node-detail + annotation primitive, built.
- **`FloorplanOverlay` = the latent node-graph** (§0.1) — percent-positioned nodes + active-dot + pick. The static ancestor of the live canvas.
- **`HubBug` + hub-switcher** *(Observed: `HubBug.jsx`, `hub.css:64-83`)* — a top-left brand bug + a **pill of tabs** to switch which "stage" (Entry / Apt A / Apt B / Rooftop) you're viewing. **(My-idea:** the glyphgraph wants exactly this — switch between *projects/conversations/graph-snapshots*; the tab-pill transfers as the graph-switcher.)
- **`QuickMenu`** *(Observed: `QuickMenu.jsx`, `hub.css:102-129`)* — a dark popup column of tools (Info / Floorplan / Share / Gyro / CLOSE) with an `active` state and a `muted` (unavailable) state. A **compact floating tool-menu** for a canvas — transfers as the glyphgraph's canvas action menu (add-node / re-layout / narrate / focus).
- **`InfoPanel` / `SharePanel`** *(Observed: `InfoPanel.jsx`, `SharePanel.jsx`, `hub.css:131-211`)* — right-docked 360px overlay cards (they share the `.vh-info-panel` class — `SharePanel.jsx:8` reuses it). A **docked detail/share panel** that floats over the canvas rather than sitting in a grid column. Note: this is a *third* way of doing the right-side detail zone (see overlap §2).

---

## 2 · The OVERLAPS / duplications — and the fused best-of-all (the matrix)

Each row: the concern | how `vi/` does it | how `platform/` does it | how `virtual-hub/` does it | **what the FUSED surface takes from which.**

### Overlap 1 — **Left navigation rail** (done twice, near-identically)
| | vi/ | platform/ | virtual-hub/ |
|---|---|---|---|
| Evidence | `vi.css:20-43` `.vi-side` **240px**, glyph + label nav, active = dashed border (`:42`) | `platform.css:26-103` `.cv-sidebar` **280px**, glyph + label nav, active = dashed border (`:76`), **+ collapsible sections** (Tools/Integrations/Support, `PlatformSidebar.jsx:19-29`) + dashed "slot" placeholders | (none — canvas-first, no rail) |
**Fused takes:** platform's rail is a **superset** of vi's (same glyph-nav + active-dashed idiom, plus the collapsing `Section` and `cv-slot`). → **One nav rail**, platform's structure, with vi's lighter 240px option as a density variant. The active-state idiom (`background:bg-surface; border:dashed border-dashed`) is *already identical across both* — that's the one home; collapse to it.

### Overlap 2 — **Messaging / conversation** (done THREE ways — the richest overlap)
| | vi/ | platform/ | virtual-hub/ |
|---|---|---|---|
| Form | **Full conversation panel** — `ChatPanel.jsx`: messages, avatars, entity-read cards, missing-prompts, approvals, a composer with hint + Send | **Floating pill** — `Chats.jsx`: `position:fixed` bottom-right, unread count, opens elsewhere | **Anchored comment thread** — `CaptureComment.jsx`: a thread popup with comments-list, attachments, status-pill, and the **richest composer toolbar** (B/I/S/code/list/Aa/@/emoji/attach, `:55-66`) |
**Fused takes:** the glyphgraph's **talk-zone = vi's conversation structure** (`ChatPanel` messages + `MissingPrompt` gap-resolution + `ApproveCard`) — it already models user↔AI turns with inline work-cards. **+ virtual-hub's composer richness** (`CaptureComment`'s formatting toolbar + attachments) for when the user types rather than speaks. **+ platform's `Chats` floating-pill** as the *collapsed* form of the talk-zone on a canvas-first layout (so the conversation can dock or float). **(My-idea:** voice (ANCHOR §6 STT) feeds the *same* message stream — a transcribed turn is just a `Message from="user"`.)

### Overlap 3 — **Status pill** (done twice)
| | vi/ | virtual-hub/ |
|---|---|---|
| Evidence | `ViStatusPill.jsx` + `vi.css:93-107` — pill + mini-mark + **live-pulse** ring animation; text-driven ("Vi is reading 4 entities…") | `hub.css:343-355` `.vh-status-pill` — pill + **coloured dot**, cycling **4-state** (pending/approved/resolved/rejected, `CaptureComment.jsx:6-11`) |
**Fused takes:** **one pill** = vi's live-pulse (for "AI is working now") **+** vh's coloured-dot 4-state cycle (for a node/item's discrete status). They're complementary: vi encodes *activity*, vh encodes *state*. The glyphgraph node-status legend = vh's `{state→color}` map; the "extract layer is running" indicator = vi's pulse.

### Overlap 4 — **Detail / inspector zone** (done THREE ways)
| | vi/ | platform/ | virtual-hub/ |
|---|---|---|---|
| Form | **Docked right pane** — `OutputPreview` live-filling structured artifact (`vi.css:273-343`) | **In-flow panel** — `cv-panel` soft-gold settings container in the content column (`platform.css:220-236`) | **Floating/anchored** — `InfoPanel`/`SharePanel` right-docked overlay cards (`hub.css:131-211`) **+** `CaptureComment` node-anchored popup |
**Fused takes:** the glyphgraph detail-zone must be **either docked OR node-anchored** — so take **vh's two modes** (docked `vh-info-panel` for "selected node detail"; anchored `vh-capture` for "click a node in place") **+ vi's `OutputPreview` structured-section render** as *what goes inside* the detail (the node's facets/read-out, ANCHOR §1 "reads a glyph out as a sentence") **+ platform's `cv-panel`/field/checkbox** for the editable-properties form when you author a node. One detail component, two anchor-modes, three content-kinds.

### Overlap 5 — **Canvas / positioned-nodes layer** (only one kit has it — but it's the keystone)
| | vi/ | platform/ | virtual-hub/ |
|---|---|---|---|
| Form | centre pane is a **fixed-tier task tree** (hierarchy, NOT a free graph — see §3) | none (grids only) | **`FloorplanOverlay`** percent-positioned nodes + active-dot + pick (§0.1) — the only true 2-D positioned-node canvas |
**Fused takes:** the live glyphgraph canvas = **vh's `FloorplanOverlay` positioning model** (percent/absolute nodes, per-node active+pulse, click-to-pick) **generalised** — data-driven nodes + an auto-layout engine + edges (which vh lacks; ANCHOR §3 edges-from-relations). The reactflow surface (ANCHOR §4 my-idea) is this pattern made dynamic. **vi's centre tree does NOT transfer as the layout** (it's a waterfall, not a graph) — see §3.

### Overlap 6 — **Copy-pasted user-avatar SVG** (literal drift, the kind this design system exists to kill)
**Evidence:** the **identical** `<path d="M12 12 a4 4 0 1 0 0-8 a4 4 0 0 0 0 8 Z M4 22 a8 8 0 0 1 16 0 Z"/>` appears in `vi/ChatPanel.jsx:60` (Message user avatar) **and** `platform/TopBar.jsx:10` (avatar). **Fused takes:** this is exactly the second-home drift the design-system CLAUDE.md §0 forbids — one `Avatar` component / one icon entry, referenced from both. Trivial, but emblematic: even these "version" kits already duplicate primitives that want a single home.

### Overlap 7 — **Toolbar/menu of canvas actions** (two idioms)
| | platform/ | virtual-hub/ |
|---|---|---|
| Form | `ActionToolbar` horizontal row (Select/Filter/Sort/Search/Create/Upload, `ActionToolbar.jsx`) | `QuickMenu` dark floating column (Info/Floorplan/Share/CLOSE, `QuickMenu.jsx`) |
**Fused takes:** the glyphgraph wants both — platform's **horizontal toolbar** for collection-level operations (filter/search/add-node) when docked, vh's **floating column** for canvas-context actions (re-layout/narrate/focus). Same action-set, two presentations chosen by layout mode.

---

## 3 · The one tension to NOT smooth over — vi's frame YES, vi's centre NO

The strong temptation is to crown `vi/` "the design" because its three-pane *is* talk+graph+detail. **Resist exactly there.** Sharper, evidence-grounded claim:

- **vi's three-pane FRAME transfers** *(Observed: `vi.css:46-71`)* — talk-zone | work-zone | detail-zone is the right skeleton.
- **vi's centre pane does NOT transfer as the canvas.** `TaskTree` is a **fixed 3-tier agent-layer waterfall** *(Observed: `TaskTree.jsx:14-33`, `vi.css:229-271`)*: `layer-1` is `1fr` (one node), `layer-2` is `repeat(2,1fr)`, `layer-3` is `repeat(4,1fr)`, joined by a **vertical connector** (`:262-271`). That is a **hierarchy / dataflow waterfall**, not an edge-driven relational graph. The glyphgraph (ANCHOR §3, §7) is **reactflow freeform with edges-derived-from-relations + incremental auto-place** — arbitrary topology, not three fixed tiers.

→ **The fused canvas takes vi's frame + vi's node-state vocabulary** (idle/active/done/blocked + pulsing dot, `vi.css:249-260`) **but its layout model comes from virtual-hub's canvas-with-anchored-detail + reactflow**, not from vi's tree. *(Inferred from comparing `TaskTree` topology against ANCHOR §3-4.)* This is the precise "yes, but actually the code does X" the wave is paying for: the most-glyphgraph-looking kit has the *least*-glyphgraph layout engine in its centre.

**A second tension (layout philosophy):** vi/ and platform/ are **panelled grids** (fixed columns); virtual-hub/ is **canvas-first overlays**. The glyphgraph is fundamentally canvas-first (you watch a graph fill a space) — so *(My-idea)* the base layout is closer to **virtual-hub's stage-with-floating-overlays** than to vi's rigid 3-column grid, with vi's panes becoming *dockable overlays* (talk-zone can dock-left or collapse to a `Chats`-style pill; detail can dock-right or anchor-to-node). This reconciles all three: **vh's canvas-first stage** as the base, hosting **vi's conversation+state-vocabulary** and **platform's control/form vocabulary** as floating/dockable panels.

---

## 4 · Relevance to the conversational-glyphgraph surface (direct mappings)

| Glyphgraph need (ANCHOR) | Already-built precedent to fuse from | Evidence |
|---|---|---|
| **Three-zone talk + graph + detail** | vi's 3-pane frame (frame only) | `vi.css:46-71` |
| **Live canvas you watch build** | vh stage-first + FloorplanOverlay positioned nodes | `hub.css:12-45`, `FloorplanOverlay.jsx:4-17` |
| **Node = a glyph, with state in its fill** | ViMark pattern-fill-as-state; vi-node 4-state; CalChip colour-state | `ViMark.jsx:7-16`, `vi.css:249-260`, `platform.css:375-390` |
| **Click a node → detail anchored to it** | CaptureComment clamped popup + tap-marker | `CaptureComment.jsx:13-19`, `hub.css:267-377` |
| **Read the graph/node out as a sentence** | OutputPreview structured-section read-out | `OutputPreview.jsx:16-88` |
| **Voice/typed correction loop ("buyer's gone cold")** | MissingPrompt in-conversation gap-resolution; CaptureComment rich composer | `ChatPanel.jsx:27-44`, `CaptureComment.jsx:53-66` |
| **"Extract layer is running" live indicator** | ViStatusPill live-pulse + ReadCard | `ViStatusPill.jsx`, `vi.css:101-105`, `ChatPanel.jsx:17-25` |
| **Switch between graphs/conversations** | HubBug stage-switcher tab-pill | `HubBug.jsx`, `hub.css:64-83` |
| **Canvas action menu (add/re-layout/narrate)** | QuickMenu floating column + ActionToolbar row | `QuickMenu.jsx`, `ActionToolbar.jsx` |
| **Author/edit a node's properties** | platform cv-panel + field + checkbox + HubSettings toggle-grammar | `platform.css:220-275`, `HubSettings.jsx` |
| **Status legend (state→colour)** | CalChip `{kind→{bg,dot}}` + vh-status 4-state | `platform.css:384-390`, `CaptureComment.jsx:6-11` |

### The no-staleness watch (ANCHOR §5) — where these kits would violate it
**(Observed, and this matters for the fuse):** every kit hardcodes its data and its branches —
- `FloorplanOverlay` has a literal `rooms[]`/`dots[]` (`:4-17`); `HubApp` a literal `HUBS[]` (`:4-9`); `ViKitApp` literal step-snapshots (`:80-93`); `Calendar` hardcoded chips; `vi-node` state is a per-tier hand-set string.
- The avatar SVG is copy-pasted (§2.6); status-colour maps are inlined in two places (`CaptureComment.jsx:6-11` and `platform.css:384-390`).

These are **mockup-grade scaffolding, not the model** — but the fuse must **invert every one of them**: nodes come from the resolve-pipeline (not `rooms[]`), node-state-colour comes from `CV_MEANING.encodings` (the existing data→channel home, ANCHOR §7), the avatar/icon from one registry entry. *(Inferred:* the kits are honest about being demos — the lesson is **which patterns to keep and which literals to dissolve** when they become the real instrument.)*

---

## 5 · Three-line summary

1. **Three parallel UI versions, one shared token base, three layout grammars** — `vi/` (AI three-pane workspace), `platform/` (panelled creator dashboard), `virtual-hub/` (canvas-first immersive viewer); none canonical, each with unique harvestable qualities, to be fused into one conversational-glyphgraph surface.
2. **The keystone recognitions:** `FloorplanOverlay` is a latent node-on-canvas graph, `CaptureComment` is a built node-anchored detail/annotation popup, and `vi/` already ships the entire live/streaming/gap-resolution vocabulary — but **vi's three-pane FRAME transfers while its centre `TaskTree` does NOT** (it's a fixed 3-tier waterfall, not an edge-driven graph; the canvas layout-model comes from vh + reactflow). The fused base is **vh's canvas-first stage hosting vi's conversation+state vocabulary and platform's control/form vocabulary as dockable overlays.**
3. **Path:** `/home/tim/company/design/claude-ds/analysis/glyphic-language/live-instrument/findings/AREA-18-uikits-version-catalogue.md`
