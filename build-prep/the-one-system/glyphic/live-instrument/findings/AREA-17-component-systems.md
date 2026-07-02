# AREA-17 — Component systems, the conversation-surface lineage, and the FUSION map (wave-3)

> Wave-3 **coverage + unification** agent. My lens (Tim): **nothing is final/canonical**; **duplications
> are expected and valuable** — for each parallel version I catalogue its **unique qualities** and the
> **FUSION direction** (fuse-best-of-all, never pick one), and the fusion is **governed by the
> single-source law** (ANCHOR §5: everything resolved from one home), *not* by feature-union. Evidence
> marked **Observed (file:line)** / **Inferred** / **My-idea**. I **reconcile with AREA-13** (the wave-2
> component/registry/kit map) rather than re-walk it, and I **deepen + correct** it where my coverage
> went further. Two repos in scope; this area is mostly `claude-ds/` with one cross-repo flag at the end.

---

## 0 · Where this sits relative to AREA-13 (reconcile, don't repeat)

AREA-13 mapped the **static** layer well and I take its findings as read:
- The **11 token-class components** (`Avatar/Badge/Button/Card/Input/Modal/Segmented/Stepper/Switch/Tabs`
  + `Glyphic`) are design-system-grade thin `cv-*`-class wrappers with zero literals — reuse them as the
  instrument's chrome. (AREA-13 §1.1.)
- `Glyphic.jsx` is the React socket around the one `CV_GLYPHIC.compose` renderer (incl. an edge path) —
  never write a second glyph drawer. (AREA-13 §1.3; I re-confirm at `components/Glyphic.jsx:53`.)
- `components-type.js` is a **catalogue-only** projection: AREA-13 *verified* no renderer dispatches its
  `runtime.kind:'react-component'` — a latent staleness seam. (AREA-13 §2.6.) I do not re-derive this.
- The registry is deep/resolution-native (`kind.graph`, filled `relationship.*`, `CV_COND`,
  `CV_REGISTRY.accepts`, `CV_TYPES_VI.proposeType`). (AREA-13 §2.)

**Where I go past AREA-13 (my net-new territory):**
1. AREA-13 saw **two** conversation surfaces (`ChatRail`, `ChatPanel`). **There are three.** The third —
   **`atomicity/ViConsole.jsx`** — is *outside* AREA-13's stated territory and is **the most advanced
   act-on-the-surface conversation loop in the repo**, the closest existing thing to "talk → the surface
   mutates." It is the single most important find in my area and AREA-13 never saw it. (Observed; §2.)
2. AREA-13 named the `vi/` kit's `ViMark` as a "directly reusable pattern." I show there are **three Vi-mark
   drawers** (`ViShape`, `ViMark`, and the Glyphic `form:"diamond"`) and the single-source law says there
   should be **one**. (§1.)
3. AREA-13's stance on kits + chat was effectively **pick-one** ("rebuild on the real components, mine the
   kit for UX"). My deliverable is the **fusion map**: each surface's unique contribution to **one** thing.
   (§2, §4.)

---

## 1 · DUPLICATION SET A — the Vi mark is drawn in THREE places (the canonical fusion example)

This is the cleanest illustration of "duplication → fuse-best-of-all under the single-source law."

| Version | Where | Unique qualities (Observed) | The drift |
|---|---|---|---|
| **`ViShape`** | `app/components/ViShape.jsx:2` | Token-clean: `color = 'var(--accent-gold)'` default; hatch-pattern fill via inline `<pattern>`; `animated` toggles a `<animate>` opacity pulse (the "thinking" tell, `:9-11`). Small (logo/chip/button glyph). | none — this is the clean one |
| **`ViMark`** | `ui_kits/vi/ViMark.jsx:2` | Adds **`showGlyph`** (the literal "Vi" wordmark inside the diamond, `:17-19`) and a larger 100×100 viewBox. The richest. | **hardcodes `#E0C010` and `#fff`** (`:9,14`) — a raw-hex copy of the gold/paper tokens. This IS the drift the whole system exists to prevent. |
| **Glyphic `form:"diamond"`** | the DNA itself | Per the system: *Vi → diamond* is a glyphic form, not a bespoke SVG. (Observed: `ChatRail.jsx:37` "Vi → diamond"; `Glyphic.d.ts:19` `form` enum includes `"diamond"`.) The mark composes through `CV_GLYPHIC.compose` like every other glyph. | n/a — but it means **two of the three drawers shouldn't exist** |

**FUSION DIRECTION (collapse-to-one-home, not feature-union):**
The naive "best-of-all" would merge ViShape's tokens + ViMark's `showGlyph` + the animation into one
SVG component. **The law forbids that** — there should not be three diamond drawers at all. The Vi mark
**is a Glyphic** (`form:"diamond"`, a symbol/fill/motion spec). The fusion:
- The one home is `CV_GLYPHIC.compose` (via `<Glyphic form="diamond" …/>`). (My-idea, grounded in the DNA.)
- ViMark's good features become **options on that one home**: `showGlyph` → a symbol/overlay slot;
  the pulse animation → the existing Glyphic **`motion`** axis (`Glyphic.d.ts:31` already has
  `breathe/pulse/glow` — the "thinking" state is `motion:"pulse"`, not a hand-rolled `<animate>`).
- ViMark's `#E0C010`/`#fff` **die** — they resolve to `ringColor:"gold"` / `fill:"paper"` token names.
- `ViStatusPill` (`ui_kits/vi/ViStatusPill.jsx`) stays as a *wrapper* (pill chrome + label) but its inner
  mark becomes `<Glyphic form="diamond" motion={live?'pulse':'none'} />`. (Observed it already just wraps
  `ViMark size=18 showGlyph={false}`, `:5` — a thin re-skin, trivially repointed.)

**Why this matters for the live instrument:** the instrument's live-state indicators ("listening",
"extracting", "composing") are exactly the `ViStatusPill` + animated-mark pattern. If they're built on
the one Glyphic renderer with a `motion` option, every state themes for free and there's no fourth
diamond drawer. (My-idea; grounded.)

> Note (Observed, not in scope to fix here): `polygon points` also appears in `types-thumb.jsx`,
> `CvIcon.jsx`, and several `workshop/*` files — those are *thumbnails/icon geometry*, not Vi-mark
> copies. The three above are the genuine Vi-mark duplication set.

---

## 2 · DUPLICATION SET B — THREE conversation surfaces (the heart of this area)

There is no single "chat component." There are three independent implementations, each grown for its own
surface, with **non-overlapping strengths**. AREA-13 saw two; the third is the prize. The live instrument's
conversation pane should be **one** surface that is the *fusion of all three under the single-source law*.

### 2.1 `app/components/ChatRail.jsx` — the PRODUCTION-WIRED rail (Observed)
The only one wired into the real app and the real registries.
- **Real `CV_AI` wiring**: `window.CV_AI.complete({messages})` with a composed system prompt + 6-turn
  history window (`ChatRail.jsx:124-138`). This is the live single-source AI call. (Observed.)
- **Intent routing** baked in: an **image-intent route** (`cvOpenAI.classifyIntent` → `resolveProvider
  ('openai-image').generateImage`, `:67-99`) and a **workshop edit-intent route** (`WS_AI.classifyIntent`
  → `generateEdit` → inline **diff card** the user applies/discards, `:104-159`). (Observed.)
- **Scope-awareness**: `SCOPE_LABEL` + `SUGGESTED[scope]` (`:4-33`) make the rail context-aware per canvas.
- **Message-kind renderer**: text · `kind:'image'` (with Adopt/Open/Download actions) · `kind:'diff'`
  (the `WSDiffCard`). (`:186-211`.) **This is the union-renderer seed.**
- Composer = textarea + send button, Enter-to-send / Shift+Enter (`:232-251`), auto-scroll (`:52-54`).
- **Unique contribution to the fusion:** the *real provider call*, the *intent-routing spine*
  (talk → classify → either-answer-or-act), and the **apply/discard inline-proposal** pattern.

### 2.2 `ui_kits/vi/ChatPanel.jsx` — the DEMO with the richest NODE-AFFORDANCE vocabulary (Observed)
Self-mounting kit demo (not imported anywhere), but it has interaction *cards* the others lack:
- **`ReadCard`** ("Reading/Read `<entity>`", with a spinner→✓, `:17-25`) — the *extraction-in-progress*
  affordance. This is **literally the live-instrument's EXTRACT stage** ("reading the buyer… resolved").
- **`MissingPrompt`** (inline gap-fill question + input + submitted state, `:27-44`) — the
  *resolve-on-miss / ask-for-the-missing-field* affordance. Directly the pipeline's GENERATE-ON-MISS UX.
- **`ApproveCard`** (`:46-53`) — approve-a-result, the confirm-before-mutate gate.
- **`Message`** carries a **timestamp** + a **`vi-live`** animated state (`:55-78`).
- **Drift / disposable bits:** **emoji** entity icons (`EntityIcon`, `:4-15` — `🎨📋📷…`) and **inline
  styles** (`:33-39`). These are demo shortcuts, NOT the glyphic system. (Observed.)
- **Unique contribution to the fusion:** the **card vocabulary** — `ReadCard` / `MissingPrompt` /
  `ApproveCard` — which maps 1:1 onto the EXTRACT → RESOLVE-ON-MISS → CONFIRM stages of the pipeline.

### 2.3 `atomicity/ViConsole.jsx` — the ACT-ON-THE-SURFACE loop (Observed — the net-new prize)
The most advanced surface; the closest prior art to "talk → the surface live-mutates." AREA-13 didn't see it.
- **Structured interpret-and-act**: `VI_BRAIN.interpret(text, ctx, history)` returns
  **`{say, actions, proposals, followup, options}`** (`ViConsole.jsx:57-59`) — exactly the structured-output
  shape the ANCHOR's RESOLVE/compose stage wants (and the same idiom as `CV_TYPES_VI.proposeType`).
- **Auto-runs actions on the surface**: it loops `res.actions` and *executes* them — `open`/`search`/
  `expand`/`highlight`/`connect`/`ingest`/`explore` go straight to handlers; `restyle` runs through a
  **before/after visual-diff** path with real `CV_OVERRIDE.apply` + `CV_SHOT.snapshot` (`:62-92`). This is
  **talk → the canvas changes**, the instrument's core loop, already prototyped on the studio surface.
- **Element selection (`picked`)**: a selected element drives **element-anchored asks** ("Explain this",
  "Restyle this", "Make a component", `:204-210`) and shows a selection chip (`:195-202`). This is the
  **node-selection → contextual-action** pattern a glyphgraph node needs (see §3).
- **Modes** Chat · Teach · Memory (`:212-215`): **Teach** folds a stated preference back into `CV_AI`
  live (`VI_BRAIN.learn`, `:39-51`) and **Memory** lists/forgets them — the two-way *learning* loop.
- **Screenshot memory** the user AND Vi tune (`CV_SHOT` FIFO, `:216-221`) — adjustable perception window.
- **Message-kind renderer**: text · **action-chips** · **proposal-chips** (staged/applied) · **before/after
  image pair** · followup · **`OptionRow`** (`:147-177`). The richest renderer of the three.
- **Unique contribution to the fusion:** the **structured `{say,actions,proposals,options}` interpret-spine**,
  the **auto-run-actions-on-the-surface** mechanism, **element-selection + anchored asks**, and the
  **Teach/learn** two-way authoring.

### 2.4 THE FUSION — one conversation surface (not three components)
The single-source law says the instrument doesn't get a fourth chat component; it gets **one** surface that
is the union *of capabilities*, each sourced from its one home:

| Concern | Sourced from | Built on |
|---|---|---|
| The AI call | ChatRail's real `CV_AI.complete` / `CV_AI.execute` | the AI registry (single home) |
| The interpret-spine (talk → structure) | ViConsole's `{say, actions, proposals, options}` | the `CV_TYPES_VI.proposeType` idiom (AREA-13 §2.5) |
| Auto-act on the canvas | ViConsole's action loop (`:62-92`) | a glyphgraph action-set (open node, add edge, recolour) instead of restyle |
| The card vocabulary | ChatPanel's `ReadCard`/`MissingPrompt`/`ApproveCard` + ChatRail's image/diff cards + ViConsole's action/proposal/before-after | **one message-kind renderer** with the union of kinds |
| Entity icons | **`<Glyphic/>`** — *killing ChatPanel's emoji* and ViConsole's mixed `CvIcon`/`ViShape` | `CV_GLYPHIC.compose` (single home) |
| Composer | `Input` (`as="textarea"`) + `Button` | the 11 token-class components (AREA-13 §1.1) |
| The scrolling list | **a new `.cv-feed` list/scroller primitive** (all three hand-roll `scrollTop=scrollHeight`: `ChatRail:53`, `ChatPanel:82`, `ViConsole:25`) | AREA-13 §1.2 already flagged this absence — fuse the three hand-rolls into one primitive |
| Mode toggle (listen ⇄ push-to-talk; Chat/Teach) | ViConsole's `ac-vi-modes` → rebuilt on **`Segmented`** | the token-class component |

**Net:** the instrument's conversation pane = **ViConsole's act-on-surface spine** + **ChatRail's real
provider/intent routing** + **ChatPanel's pipeline-stage card vocabulary**, rendered through **one
message-kind renderer**, on **Input/Button/Segmented + a new feed primitive**, with **Glyphic entity
icons** — and the three originals retire into it (the islands join the mainland; no parallel chat survives).
(My-idea; every part grounded in a real file above.)

---

## 3 · (c) The interaction / selection / persistence patterns a glyphic NODE needs (synthesis)

The brief asks what handlers/selection/persistence a live glyphic node needs. The parts already exist
across my territory and the registry — assembled here as one answer:

- **SELECT** — a node-selection model already exists as ViConsole's **`picked`** (a selected element with
  `role`, `text`, `_el`, a screenshot, style snapshot — `ViConsole.jsx:73-83,195-211`). A glyphgraph node's
  "selected" state is this same shape (the node id + its resolved glyphic-spec). (Observed → My-idea map.)
- **ACT (contextual)** — two complementary affordances:
  - **Action-chips** that auto-run (ViConsole `:147-156`) — "add a relation", "recolour by state",
    "ask why this glyph" become chips on a selected node.
  - **`RefinePop`** (`app/components/RefinePop.jsx`) — the per-item "tell it to change this one" popover
    (a ↻ dot on a tile → type a change → refine, `:7-78`). This is **the voice-correction-by-node UX**
    Tim's loop wants ("no, the buyer's gone cold") rendered as a per-node control. **Reuse it.** (Observed.)
- **HANDLE (the declared event)** — the registry already models a node's click-action as a typed
  **event-socket** (`kind:'event'`, `event:'click'`, `onPick:'open'|'insert'`, an `address` to the
  occupant — AREA-13 §0/§2.4, `types-core.js:292 socketInfo()`). So a node's handler is a **registry
  declaration**, not bespoke code — the no-staleness shape. (Observed via AREA-13; I cite, don't re-walk.)
- **PERSIST** — two homes, both already here:
  - **`usePersisted`** (`app/components/usePersisted.js`) — namespaced (`cvstudio:`) localStorage React
    hook + a `cvStudioStorage.getAll/clear` (export/wipe everything at once, `:25-37`). The graph's
    transient state (open node, last layout, draft edges) persists through this. (Observed.)
  - **`Resizable`'s** per-key localStorage (`cvstudio:resizable:<key>`, `Resizable.jsx:26-38`) — the
    *layout* persistence (the three-zone split sizes). (Observed.)
- **The canonical (durable) home** is Supabase per the ANCHOR; `usePersisted` is the *session/transient*
  layer, not the graph's source of truth. (Inferred from ANCHOR §7 data-binding note.)

---

## 4 · Layout + supporting interaction components (reuse-as-is, Observed)

These are not duplicated — they're single, clean, and directly serviceable for the instrument's shell:

- **`Resizable.jsx`** — a horizontal split with draggable, **persisted** gutters; exactly one `flex` column
  (`:21-107`). This **IS the three-zone instrument shell** (talk · watch-it-build · the graph). Reuse
  verbatim with `storageKey:"live-instrument-cols"`. (Observed + My-idea.)
- **`CommandPalette.jsx`** — a ⌘K overlay that builds a **unified searchable index FROM the registries**
  (canvases + every `CV_ICONS` glyph + colors + voice rules + actions), with fuzzy scoring + full keyboard
  nav (`:9-117`). Two uses for the instrument: (a) the **"what can I place / find an icon" palette** (it
  already indexes `CV_ICONS.data`, `:42-50` — the seed of the semantic-icon-lookup UX); (b) a
  jump-to-node/run-a-capability command bar over the live graph. **A genuinely reusable pattern.** (Observed.)
- **`Toast.jsx`** — a single shared global notifier (`window.dsaToast`, one instance, `:4-22`). The
  loud-but-light surface for "new icon drawn", "node added". Reuse. (Observed.)
- **`Sidebar.jsx`** — data-driven nav from a `NAV_SECTIONS` literal (`:4-48`); product chrome, reference for
  *where the instrument lives*, not instrument-internal. (Observed.)
- **`CanvasHeader.jsx`** — a 9-line `{title, sub, actions}` shared header (`:2-12`). Trivially reusable as the
  instrument canvas's header. Token-clean. (Observed.)

### 4.1 Coverage of the remaining named files (classified, Observed)
Closing the territory map so nothing is silently omitted:
- **`ExportPatch.jsx`** — a modal that emits **copy-paste code patches** for generated icons/colors/patterns
  back into `cv-icons.js` etc. (`:4-12`). *Relevant pattern, not chrome:* it's the "an AI-generated artifact
  becomes a saved registry entry" flow — analogous to the foundry's `glyphic.save`. Reference for the
  generate-on-miss → persist step, not a reused component. (Observed.)
- **`KitPreviews.jsx`** — mini live-token thumbnails of the three kits, rendering **from CSS custom
  properties so token edits cascade** (`:1-37`). Confirms the kits are *previewable surfaces*; the
  token-cascade-into-a-thumbnail trick could preview a glyphgraph node under palette edits. Mostly
  Colors-canvas-specific. (Observed.)
- **`ImageEditor.jsx`** (crop/filter/AI-edit modal), **`MaskEditor.jsx`** (brush-mask for OpenAI edits),
  **`Pano360.jsx`** (three.js equirectangular viewer) — **disposable for the live instrument.** These are
  the imagery/virtual-hub domain (editing photos, viewing 360° tours), not conversation/graph/glyphic
  machinery. They are the *content the graph narrates about* (a property's images/tour), not instrument
  chrome. Note `Pano360` lazy-loads `three.js` from a CDN (`:5-13`) — a **CSP flag** if the instrument's
  bundle inherits the no-script/CSP constraints the ANCHOR §6 raised (a precedent that external libs are
  loaded on-demand here, relevant to the reactflow-in-CSP question). (Observed.)

---

## 5 · The no-staleness watch (where hardcoding would sneak into MY territory)

- **The Vi mark** — `ViMark`'s raw `#E0C010`/`#fff` (`ViMark.jsx:9,14`) is live drift today; the fusion
  (§1) kills it by collapsing to the Glyphic renderer. *Don't carry it forward.*
- **Emoji + inline styles in the kit chat** — `ChatPanel`'s `EntityIcon` emoji (`:4-15`) and inline-style
  cards are demo shortcuts. The fused surface must render entity icons through **`<Glyphic/>`** and cards
  through `cv-*` classes, never copy the emoji/inline literals. (§2.2.)
- **CommandPalette's `baseColors` literal** — it hand-lists hex (`CommandPalette.jsx:53-57`) instead of
  reading the token registry. If the instrument reuses the palette, **derive the color list from the token
  source**, don't copy this literal. (Observed gap.)
- **Three hand-rolled scrollers** (`ChatRail:53`, `ChatPanel:82`, `ViConsole:25`) — fuse into **one** feed
  primitive, don't perpetuate the copy. (AREA-13 §1.2 + my confirmation.)
- **CanvasHeader / Sidebar literals** are *data definitions* (nav structure), not drift — leave them.

---

## 6 · Cross-repo flag (the unification law spans both repos)

The ANCHOR (§7) and the recall mission both reference a **Company-side operator/console surface** (the
"Operator Surface build", phone+desktop console fusing into the bridge) and the Company's own voice/STT
loop. **There is therefore a likely FOURTH conversation surface in `~/company/` (the operator console)**
that this design-system trio must eventually fuse with — the live instrument's voice path is server-side
(Company) while these three surfaces are browser-side (design system). I did not read the Company surface
(outside my file-territory and AREA-3/AREA-8 cover the voice/RHM/operator side). **Flagging it as the
cross-repo seam:** the fusion in §2.4 is the *browser half*; it must be designed to receive graph-deltas
from / send transcribed-intent to the Company operator surface, not as a closed browser-only chat.
(Inferred from ANCHOR §7 + MEMORY operator-surface mission; verify against AREA-3/AREA-8.)

---

## 3-line summary

1. **Two clean duplication sets define this area.** The **Vi mark** is drawn 3× (`ViShape` token-clean ·
   `ViMark` richer-but-hardcodes-`#E0C010` · the Glyphic `form:"diamond"`) — the law says collapse to the
   **one** `CV_GLYPHIC` renderer with `showGlyph`/`motion:"pulse"` as options, killing the hex drift.
2. **There are THREE conversation surfaces, not two** (AREA-13 saw two): `ChatRail` (production `CV_AI` +
   intent-routing + apply/discard diffs) · `ChatPanel` (the `ReadCard`/`MissingPrompt`/`ApproveCard`
   pipeline-stage card vocabulary, but emoji) · **`atomicity/ViConsole`** (the prize — structured
   `{say,actions,proposals,options}` interpret-spine that **auto-acts on the surface**, element-selection,
   Teach/learn). The fusion is **one** surface uniting all three under single-source: ViConsole's act-spine
   + ChatRail's real provider/routing + ChatPanel's cards, one message-kind renderer, Glyphic entity icons,
   built on `Input`/`Button`/`Segmented` + a new feed primitive.
3. **The node's select/act/persist parts already exist** (`ViConsole.picked` = selection · action-chips +
   `RefinePop` = correction · the registry **event-socket `onPick`** = the declared handler ·
   `usePersisted` + `Resizable` localStorage = persistence); **`Resizable`/`CommandPalette`/`Toast`/
   `CanvasHeader` reuse as-is** for the shell; the image/mask/pano editors are **disposable** (Pano360's
   CDN `three.js` load is a CSP precedent to note). Cross-repo seam flagged: a likely **4th** (Company
   operator) surface to fuse with server-side.

Path: `/home/tim/company/design/claude-ds/analysis/glyphic-language/live-instrument/findings/AREA-17-component-systems.md`
