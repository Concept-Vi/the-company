# AREA: canvases + app — `/home/tim/company/design/claude-ds/app/` (excl. `app/registry`, `app/ai`)

Reader scope: `app/index.html` (Studio boot shell), `app/App.jsx`, `app/canvases/**` (19 top-level
canvases + `workshop/` 9 sub-files), `app/services/**`, `app/components/**` (14 shared UI pieces).
~21,100 lines across 40 files, read in full via 7 parallel sub-readers plus targeted grep verification
against `core/`, `atomicity/`, `analysis/FINDINGS-LOG.md`. Register: provisional — Observed/Inferred/
Verified tagged throughout. This is NOT confirming the anchor — several findings below complicate or
falsify parts of it (see §B-flagged contradictions).

**This is the product surface layer.** Every finding below is about the layer end-users/Vi actually
touch — nav, canvases, builders, services — not the generative engine underneath it (`core/`,
`axes/`), which is only visible here as whatever these files *do or don't* consume from it.

---

## §A · What's here (dense account, by cluster)

**1. The boot shell (`index.html` + `App.jsx` + `components/`).** `index.html` is a long,
non-bundled, hand-ordered chain of ~50 `<script>` tags (Observed, `index.html:100-254`): core
solvers (`core/{DiagramSolver,ContainmentTree,Slide,RenderType}.jsx`, fetched as text, Babel-transformed,
`new Function`-eval'd, "no fallback: any load/parse error throws loudly" per its own comment) → icon/
shape/edge/axis registries → `CV_REGISTRY` (10-file Type-registry build-up) → `CV_AI` → `CV_HOST` →
`services/company.js` → 14 shared components → 25 canvas files → `App.jsx` last (self-mounts,
`App.jsx:281-282`). Dependency order is encoded ONLY as comment prose + physical script position — no
machine-checked manifest. `App.jsx` is one ~280-line component: ~20 `usePersisted`/`useState` hooks,
global-wiring `useEffect`s (`window.cvNav`, Cmd+K, registry-tick re-render), and an if/else-if chain
keyed on a bare `active` string (`App.jsx:222-239`) that selects the rendered canvas — no canvas type,
kind, or registry entry involved anywhere.

**2. Registry-facing canvases (Registry.jsx, RegistryInspector.jsx, TypeBuilder.jsx/TypeBuilder2.jsx,
Overview.jsx, StubCanvases.jsx, Templates.jsx, Bridge.jsx, Settings.jsx).** Registry.jsx is a curated,
hand-authored front door (`WORKSTATIONS` static array → `CV_REGISTRY.query()`) onto the Type registry.
RegistryInspector.jsx is the real detail surface (`TypeInspector` slide-in with lineage breadcrumbs,
`AIRegistryPanel` — a live `CV_AI` projection explicitly commented "the interface and the AI read one
source," `RegistryInspector.jsx:527-529`). TypeBuilder.jsx/TypeBuilder2.jsx are ONE module split
across two files for size (TypeBuilder2 defines sub-components attached to `window`, consumed as
globals — not a fork, see §C). Templates.jsx groups saved Build/Workshop runs by parent Type via
`CV_REGISTRY` (correct: one registry, no parallel list). Bridge.jsx is the `CV_HOST` canvas: runtimes,
a handoff-mode setting, a `Changes` queue of proposed disk writes — flat, id-keyed records, no
ancestry anywhere. Settings.jsx is a scalar OpenAI-credentials/image-defaults form, no compositional
concerns.

**3. Content canvases (Icons, Colors, Imagery, Patterns, Components, Architecture, Inbox, Voice).**
All eight organize their domain as a **flat name-keyed JS object/array** — `BASE_PALETTE`,
`ICON_CATEGORIES`, `COMPONENT_GROUPS`, `CATEGORIES` (Inbox) — none use parent/child ancestry or a
partition function. **Patterns.jsx (847 lines) does NOT contain texture/fill/grid logic** — contrary
to what its name and the brainwave's framing would suggest, it's four flat token arrays (spacing/
radii/shadow/motion). The real texture-pattern enum lives in `axes/texture/texture-axis.js` (a name
catalogue over `hatch/lines/vert/cross/grid/dense/dots`, itself deferring "the actual pattern geometry"
to `CV_SHAPES.markSVG` — neither file was read this pass). Architecture.jsx documents `CV_REGISTRY`'s
own Type-inheritance system (7 layers, slot composition, single-inheritance `extends`) — a real, live,
consumed ancestry mechanism, but a **different one** from the brainwave's spatial-address ancestry
(see §B-4).

**4. AIStudio.jsx / Build.jsx / services.** Build.jsx (1552 lines) is a **task-orchestration wizard**,
not a spatial layout canvas: Brief→Plan→Generate→Compose, an LLM decomposes a brief into 2-4 named
subtasks run in parallel, a composer assembles a preview, "Refine with Vi" triages which subtasks to
re-run. AIStudio.jsx (1035 lines) is the GPT-Image-2 control surface (Generate/Edit/Compose/Mask/Chat).
`services/company.js` registers `'company-http'` as a `CV_HOST` runtime kind — a mature, wired,
loud-fail example of registry-resolved AI-provider identity. `services/openai.js` (645 lines) is the
raw image-API client with a static `MODEL_REGISTRY`. `ai-presets.js`/`image-store.js` are flat
localStorage CRUD stores, opaque random ids, zero ancestry.

**5. Workshop.jsx shell + Section/Polish/Library/Export.** Workshop is a real multi-doc-type page/
deck/brochure builder with a **fixed 2-tier schema**: `doc.pages[]` → `page.sections[]`, every mutator
taking hardcoded `pageIdx`+`secIdx` coordinates — no third level, no self-similar recursion (directly
contrasts §9's "same partition law at every scale"). `type:'widget'/'wizard'` docs bypass this model
entirely, handed off to separate editors. Selection is single-index only (`selectedIdx`, no group
concept). Export produces three independent, unconnected layout implementations for the same content
(live-edit CSS flow / HTML-export CSS flow / PPTX absolute-inch imperative placement).

**6. Layouts.jsx + WidgetBuilder.jsx.** Layouts.jsx (775 lines) is a **template + naming registry**,
not a geometry engine: `WS_LAYOUTS` is ~30 named entries, each a fixed literal array of blocks —
insertion order IS section order. It DOES carry a genuine identity-by-registration instance
(`WS_LAYOUT_ARCHETYPE` stamps `surface.deck-slide.<key>` dot-path ids, consumed by
`core/archetype-catalog.js`). WidgetBuilder.jsx (823 lines) has a flat, un-addressed data model
(`kpis`/`rows` as plain arrays, array index = identity) but its *rendering* is fully unified — it calls
`window.__cvTypeToNode`/`window.__cvContainmentTree`/`window.__cvDiagramSolver` (the shared engine),
loud-failing if either global is missing.

**7. Blocks.jsx, WizardBuilder.jsx, AIEngine.jsx.** Blocks.jsx (1139 lines) is `WS_BLOCKS`, a flat
content-template registry (hero/quote/stats/timeline/…) keyed by semantic kind — **"block" here is a
different concept from the brainwave's "block address"** (resolved naming collision, see §B-2).
WizardBuilder.jsx (871 lines) is a multi-step flow builder, 3 hardcoded flow templates, step order =
array position, branching = a flat `{label: targetIndex}` jump table. AIEngine.jsx (1830 lines, the
largest single file in the territory) is the shared generation engine for all three Workshop doc
types: a pure, fully-invertible diff system (`applyDiff`/`invertDiff`), per-target-kind generation
functions, and a `CV_AI` capability-registration layer so dispatch is resolution-first (id ==
capability id, zero hand-kept switch) — but every diff addresses its target by raw array index
(`pageIdx`/`secIdx`/`stepIdx`), not by an address.

**8. AtomiCity — confirmed structurally separate, not absorbed.** `atomicity/` is a sibling top-level
app with its own `index.html`, entirely apart from `app/` (Studio) — confirmed both by the project's
own record (`analysis/FINDINGS-LOG.md:1909`: *"Lives in `atomicity/` — entirely separate from `app/`
(Studio)"*) and independently by direct boot-sequence comparison: `atomicity/index.html` re-loads a
**subset** of the same `CV_REGISTRY` chain (skips `types-hooks/types-vi/types-adapter/glyphic-type/
components-type/kinds-type/relationships-seed`), the same `CV_AI`/`CV_HOST` pair, then additionally
loads the compiled bundle `../_ds_bundle.js` (which `app/`'s boot never loads) and runs its own private
icon-name alias shim patching `CV_ICONS.data` post-hoc. **Two independently-maintained, divergent
bootstraps of overlapping globals** — not a fork of Studio, a genuinely separate consumer of the same
registries, kept in sync by hand where they overlap.

---

## §B · Joins to the one-math (concrete, file:line, with contradictions flagged)

**B1 — Canvas identity has NO address (§7), and this is the single highest-value, most-corroborated
join in the territory.** Seven independent hand-maintained lists stand in for one registered canvas
identity: `App.jsx:222-239` (if/else on `active`), `Sidebar.jsx:4-48` (`NAV_SECTIONS`),
`CommandPalette.jsx:15-28` (`canvases` — already a stale SUBSET, missing `workshop`/`registry`/
`architecture`/`bridge`/`settings`), `CommandPalette.jsx:53-64` (`baseColors`, a 4th hardcoded token
mirror), `ChatRail.jsx:4-17` (`SUGGESTED`), `ChatRail.jsx:19-33` (`SCOPE_LABEL`). Verified: no
`kind.canvas`/`kind.page` Type exists in `registry/kinds-type.js` despite `kind.graph`/
`kind.slide-system` already existing as the template for exactly this pattern. Under §5/§7 each canvas
should be a registry row; every list above becomes a NAMED VIEW computed from it. CommandPalette's
list is live, present-day proof that hand-sync already fails (`workshop` etc. are unreachable via
Cmd+K today).

**B2 — "Block" is a resolved naming collision, not a shared mechanism.** `WS_BLOCKS` (Blocks.jsx:66) is
a content-template vocabulary (hero/quote/stats), rendered via hand-written JSX per kind — it carries
no x/n partition, no span, no address, no ancestry. It is NOT the brainwave's §1 "a square divided x/n
→ a grid of cells, each cell a block address." Course-correction #7 says the block system lives
upstream at claude.ai/design — consistent with this: Workshop's "block" and the brainwave's "block"
are the same English noun over two unrelated concepts, zero code-level relationship (grep-confirmed,
zero `cv-address`/`CV_ADDRESS` references in Blocks.jsx, WizardBuilder.jsx, AIEngine.jsx).

**B3 — `core/cv-address.js` (the square-half algebra) has zero production consumers, independently
reconfirmed by every one of the 7 sub-reads via separate greps across their own file sets AND
repo-wide.** `span(k,n,parent)`, `encode/decode`, `lca/lcaAll`, `zones(parts,axisPx)`, `slotFor(index,
capacity)` all exist, are documented, and are called by nothing in `app/` or its transitive
dependencies (`RenderType.jsx`, `ContainmentTree.jsx`, `archetype-catalog.js`, `Blocks.jsx`, `Slide.jsx`
all checked). The ONE place a developer's mental model gestured at it: `core/DiagramSolver.jsx:74-75`,
a **comment**, not a call — *"The address IS the CV_ADDRESS shape — row/slot as a frozen path"* —
worth flagging as a low-friction first integration point (the author already thinks in these terms).

**B4 — Two ancestry mechanisms exist side by side, unreconciled — a genuine complication the anchor
doesn't address.** (a) `CV_REGISTRY`'s Type-inheritance (`resolve/lineage/children/query`, a stored
`extends` parent-pointer walked via `Set`-guarded `while`-loop) is LIVE and consumed everywhere in
this territory: RegistryInspector's breadcrumbs, Templates.jsx's parent-Type grouping, Architecture.jsx's
`LineageExample`, Layouts.jsx's `WS_LAYOUT_ARCHETYPE` dot-path stamping. (b) `cv-address.js`'s
mixed-radix spatial-address ancestry (dormant, per B3). Both implement "ancestry gives me things for
free" — different mechanism, same conceptual slot. **Open question, not resolved in this pass**: does
one-math's address ancestry replace CV_REGISTRY's Type ancestry, sit beside it as a second axis, or
does `extends`/`slots` become addressable under the same identity law (§7)? Flagged Inferred/unresolved
— needs a direct answer from whoever owns `core/`.

**B5 — Order is universally array-position, the single most-repeated violation of §3 in the whole
territory.** Every ordered list examined across all 7 sub-areas orders by insertion/splice/index, with
several ids literally encoding position at creation time:
- Build.jsx:86 — `id: 'st-' + i` (subtask id = its array index).
- Workshop.jsx:394-405,462-470 — `moveSection`/`movePage`, imperative splice; the SAME "track drag
  index, splice on drop" scaffolding independently reimplemented 3× (`SectionDraggable`, `SlideStrip`,
  `OutlineList`), each with its own off-by-one arithmetic (Workshop.jsx:1215-1224).
- WizardBuilder.jsx:184-189 — `moveStep`, splice; branching (`gotoOnChoice`, :307-318) is a flat
  `{label: targetIndex}` jump table, unrelated to "reading order over mixed square/circle divisions"
  (§10's open socket) — a clean but currently-unconnected candidate for what that socket replaces.
- Layouts.jsx:604-606 — `id: 'sec-' + Date.now() + '-' + idx + '-' + j` freezes creation-time array
  position INTO the id string — if reordered later, the id silently goes stale. This is the exact
  failure `cv-address.js`'s own header warns against ("an address is a view, never a stored fact that
  can stale," `core/cv-address.js:5-6`).
- AIEngine.jsx:55-124 — every diff (`block.insert/replace/update/remove`, `wizard.step.*`) operates by
  raw `pageIdx`/`secIdx`/`stepIdx`. **This is a live correctness risk, not just a law violation**:
  `BRIDGE.selectedIdx` (AIEngine.jsx:817,822) and `WizardBuilder`'s `activeStep` are never re-derived
  after a splice — WizardBuilder's own `useEffect` (:143-145) defensively clamps `activeStep` post-hoc,
  evidence the codebase is *aware* of the fragility without a general fix. `cv-address.js`'s
  `slotFor(index, capacity)` (:83-88) exists specifically to prevent this and is unused everywhere.

**B6 — The ramp (`--ramp-1..4`) directly contradicts §2's "cell k of n → ramp position k/n."**
Colors.jsx:12-16 defines 4 fixed `{name,hex,role}` swatches with fixed hex values, mirrored as literal
CSS custom properties (`colors_and_type.css:76-79`, commented "APPLIED/working stops" — authored
constants, not derived). Both live consumers (`core/ContainmentTree.jsx:267`,
`core/DiagramSolver.jsx:152`) index into this fixed 4-element array via a hand-set integer field
`node.ramp` (0-3, capped). **Concrete counter-evidence**: today's ramp is a hardcoded 4-stop palette
indexed by assignment, not an addressed ordinal run — exactly the target the ordinal-axis correction
(R4) already names, now with a minimal, ready repro site.

**B7 — Grid math (x/n) already exists as unconnected "folk knowledge" in the CSS engine, in at least
four independent places, none touching `cv-address.js`.** Build.jsx:807,985 —
`gridTemplateColumns: repeat(n,1fr)` (n = array length). `core/containers.css:132` —
`grid-template-columns: var(--split, 46fr 54fr)`, reachable from WidgetBuilder.jsx's cluster/split
flow. Blocks.jsx:980 — a hand-rolled percentage-of-parent placement formula for timeline ticks
(`top = ((tick+offset*0.45)/(total-0.6))*100`). **And the wrong-way version, the sharpest single
finding of the whole wave for this law**: Layouts.jsx:767-770 hardcodes a literal 53×30 line grid —
fixed 24px cell size, fixed 1280×720 extent (itself duplicated from `Workshop.jsx:1059,1079,1085,1291`
rather than defined once) — reinventing `cv-address.zones(parts, axisPx)` (`core/cv-address.js:71-75`)
by hand, with zero per-cell identity/token/order. This is the "blueprint" motif — a texture grid drawn
exactly the way §1 says texture-IS-address-math should NOT be drawn.

**B8 — A small, real 2π/n circle-division already exists, twice, both ad hoc and discarded.**
WizardBuilder.jsx:730-732 (`ShapeGlyph` hexagon icon): `a = π/6 + i·π/3` for i in 0..5 — a literal 6-way
angular partition, computed purely to plot decorative SVG points, discarded immediately after use, no
token/identity/order attached. Pano360.jsx's hotspot placement (raycaster hit → spherical lon/lat) is
genuine angle-addressing for pin drop, but hotspots are plain array entries (no minted identity, §8).
Both independently confirm the brainwave's own footnote: "radial layouts — 2π/n partitions already
drawn once, ad hoc" — the circle-address primitive (once it lands per §10) has real, waiting consumers
beyond the System Map's sunburst.

**B9 — Groups-as-identities (§8) is a total, consistent absence — not a migration target, new
construction.** Checked across all 8 registry/content canvases, Build.jsx, AIStudio.jsx, Workshop.jsx,
WidgetBuilder.jsx: zero multi-select/group/batch-as-one patterns except (a) Inbox.jsx's transient
`useState(new Set())` bulk-select, (b) Build.jsx's per-kind "apply to all icons" (a fixed category, not
an arbitrary group), (c) AIEngine.jsx's `{kind:'batch', diffs:[...]}` — functionally "one op over many
targets" but the group is a transient array of `{pageIdx,secIdx}` coordinates built fresh per AI call,
never registered/addressable afterward, no LCA computed. §8's law has no existing structure to migrate
— it needs building from nothing at this layer, with AIEngine's `batch` diff as the closest available
scaffold (same *shape*, missing the *identity* half).

**B10 — Placement: genuinely mixed evidence, both for and against the course-correction's relative-
placement law.** FOR: `ImageEditor.jsx` crop state is `{x,y,w,h}` all `0..1` — resolution-independent,
survives any transform. Workshop's `SlideFrame` fit-to-container (`Workshop.jsx:1059`,
`scale = w/1280`) is a genuine ratio. AGAINST: `Resizable.jsx:25-33,58-63` persists/computes column
widths in raw px, no `ResizeObserver` on the container (contrast `Pano360.jsx:184-185`, which has one)
— a persisted 240px column on a narrower viewport simply doesn't reflow. `Pano360.jsx:99-100`'s drag-
sensitivity is a hardcoded `0.2` constant, not derived from `fov`/viewport (inconsistent look-speed as
zoom varies). Export.jsx's PPTX path (`:216-316`) is a THIRD independent layout engine using absolute-
inch coordinates, alongside the live-editor's CSS flow and the HTML-exporter's CSS flow — "one layout
concern, three engines," none derived from a shared ratio/address function. **Scope correction**:
neither Build.jsx nor AIStudio.jsx (the two files most likely to be the placement-law's test target)
actually do spatial content-placement at all — recommend routing the absolute-vs-relative audit to
wherever elements ARE freely positioned (WidgetRender/ContainmentTree/DiagramSolver, none in this
territory).

**B11 — `company.js`/`CV_HOST` is a mature template for what the address union should eventually look
like — but confirmed to be a SEPARATE, more mature unification effort, not the same spine.** Verified
end-to-end: `ai-seed.js:38-44` registers provider `'company'`; `services/company.js:119`
(`HOST.registerKind('company-http', makeRuntime)`) resolves it; loud-fails on any non-2xx/malformed
response. **Also verified**: `grep -rn "resolve_address"` across all of `claude-ds` returns zero hits —
the brainwave's §7 "Company's one-resolver spine" has no browser-side leg anywhere in this codebase; if
it exists it's server-side in `~/company`, unconnected to anything in `app/`. Two unification efforts,
two maturity levels, in the same repo: copy the AI-provider `registerKind` pattern as the template for
address unification, don't build address-resolution from scratch.

**B12 — Movement: FRAME axis has two live instances (Workshop's `SlideFrame` scale, Pano360's camera);
CONTENT axis (split/merge/reform, §6) has ZERO instances anywhere in this territory.** The closest
positive alignment: WidgetBuilder.jsx:375-383's mocked-data resolve (620ms skeleton → real value),
explicitly citing "resolve, never pop (states.css §10)" — correctly disciplined per Slice 70's
"geometry authoritative + instant, animation is decoration," but this is VALUE resolution, not
structural split/merge. `WidgetVariationsPanel` (WidgetBuilder.jsx:658-696) swaps `system`/`widgetKind`
wholesale with NO transition at all — the clearest available, currently-unbuilt test case for a future
"reform" verb, re-resolving through the same `T2N`/`ContainmentTree` path on every render already.
**Scope note**: R3 (named by the anchor as the brainwave's first consumer) is confirmed absent from
this entire territory — it lives elsewhere in the corpus.

---

## §C · Disconnected / unused / stale (roundup across all 7 clusters)

- **`core/cv-address.js`, the whole file** — zero consumers, re-verified independently 7 times across
  every sub-territory (see B3). The single most-corroborated dead-but-built asset in the whole wave.
- **TypeBuilder2.jsx — NOT a fork, ruled out explicitly.** Purely a size-split; its exports are
  consumed as `window.*` globals by TypeBuilder.jsx. The brief flagged this pairing as a suspected
  duplicate; the evidence says otherwise.
- **StubCanvases.jsx — 4 of 6 defined stubs (`templates`/`voice`/`components`/`imagery`) are
  unreachable and their copy is stale/false** ("scaffolded but not fully built out yet" —
  StubCanvases.jsx:80) because `App.jsx`'s if/else chain matches the real, built canvases first. Only
  `type` (typography) and `logos` are live, reachable stubs (no real canvas exists for those two ids).
- **`WS_coreArchetypes()` (Layouts.jsx:585-593) has zero callers** — but explicitly staged, not drift:
  its own comment names the pending bridge as "weld W3."
- **Workshop.jsx: `WSErrorBoundary` never mounted** despite being fully implemented
  (Polish.jsx:179-201) and hoisted (Workshop.jsx:39) — render errors are not actually caught.
  **`Section.jsx`'s `Section` component unused** (only its sibling export `AddDivider` is live;
  Workshop.jsx reimplements the same toolbar inline in `SectionDraggable`, duplicating the badge/lock/
  refine/vary/remove UI). **`BlockMenuButton`** (Workshop.jsx:1788-1814) defined, never rendered.
  **Diff-based undo wired to nothing**: `invertDiff`'s result is computed then discarded
  (Workshop.jsx:220-223, `// Future:` comment) — undo/redo instead uses full-doc JSON snapshots,
  directly contradicting the LCA-bounded-change law the diff system was clearly designed for.
- **AIEngine.jsx: `MiniBlockPreview`/`MiniPagePreview` (1027-1065) are dead**, superseded by the
  generic `RenderedBlockPreview`/`RenderedPagePreview` (1526-1555) which are the ones actually wired
  into the UI — scaffolding left behind after a real generalization shipped. **`window.DOC_TRANSFORMS`**
  (a frozen module-load-time snapshot, :1198,1704) has zero consumers; the live/reactive version
  (`docTransforms()` called fresh per render) is what's actually used. **`WS_BLOCK_CORE`/`_atomRole`**
  (Blocks.jsx:1114-1139) is write-only — computed and stored, read by nothing.
- **Small dead/stale items**: `ChatRail.jsx`'s `onAction` prop (declared, never used, never passed);
  `ImageEditor.jsx:196`'s `onLoad` no-op stub; `Voice.jsx:337-366`, a byte-for-byte duplicate
  `VOICE_RULES` render hidden behind `display:none`, superseded by the live audited version below it;
  `Imagery.jsx:9`'s unused `useMemo` import; `Colors.jsx:136-148`'s dead branch (both `if`/`else` paths
  do the same thing despite comments implying divergent logic was intended).
- **Fixed shape-tables (course-correction #2's explicitly-retired anti-pattern) are STILL LIVE, found
  in 3 independent places post-correction**: WizardBuilder.jsx:11-49,83 (`WIZARD_KINDS` +
  `viDraftWizard`'s prompt literally states *"Canonical shapes: Property Wizard → hexagon, Virtual Hub
  → octagon, Vi → diamond, User Portal → circle"* to the AI as fact on every draft); Blocks.jsx:835
  (`orgDiagram` default hardcodes `shape:'octagon'` for "Virtual Hubs"); ChatRail.jsx:37
  (`SYSTEM_CONTEXT` hardcodes the same circle/diamond assignments inline). The correction has not
  propagated into this territory.
- **The diamond "Vi mark" is duplicated as raw inline SVG polygon coordinates 3 times** — the canonical
  `ui_kits/vi/ViMark.jsx:14-15`, a string-template mirror in `Export.jsx:92-93` (needed there for
  static HTML export), and inlined twice more in `Layouts.jsx:707-716` (`WSMotifLayer`) — instead of
  calling the registered, token-driven `CV_SHAPES.markSVG('vi', {...})`.
- **Token/hygiene drift**: `Build.jsx:788-798`'s `SUBTASK_META` hardcodes 5 raw hex values with no
  token-registry home; `Bridge.jsx`/`Settings.jsx` are dense with raw px in inline `style={{}}` objects
  rather than `var(--space-*)` tokens (flagged as hygiene, not a core one-math violation).
- **AtomiCity's private icon-alias shim** (`atomicity/index.html:69-83`, ~30 hand-typed name→name
  aliases patched onto `CV_ICONS.data` at boot) — a standing runtime patch that should be a registry
  fix or a call-site fix, not silent boot-time monkey-patching duplicated nowhere else in the corpus.

---

## §D · Law-candidates (recurring principles worth naming)

1. **"Navigation/identity is drift-prone precisely where it isn't addressed."** Seven parallel
   hand-maintained lists over the same canvas-id space (B1); one of them (CommandPalette) is already
   provably stale. Not hypothetical — live, present-day evidence.
2. **"Order is array position until an equation says otherwise."** The single most-repeated pattern in
   the whole territory (B5) — present in Build.jsx, Workshop.jsx (×3 independently-implemented reorder
   scaffolds), WizardBuilder.jsx, Layouts.jsx (id-freezes-position), and AIEngine.jsx's diff system
   (where it's a live correctness risk, not just a style violation).
3. **"Ratio-space components stay correct; pixel-space components silently degrade."** `ImageEditor`'s
   0..1 crop needs no defensive code across transforms; `Resizable`'s persisted px and `Pano360`'s
   `0.2` drag constant both needed extra clamping to paper over the absence of a container-relative
   unit. A clean, in-code before/after pair already exists to demonstrate the law.
4. **"A registered/derived list and a hand-typed list are visually indistinguishable in a diff, but
   only one degrades gracefully."** `CommandPalette.jsx` itself contains both side by side: icons
   (`Object.keys(CV_ICONS.data)`, complete-by-construction) vs. colors/canvases/voice-rules (hand-typed,
   already stale). A ready-made teaching example and a fast structural smell-test for future review
   ("is this array a `.map`/`.keys()` over a registry, or a literal?").
5. **"Types are registered; instances are not — extend registration to selections and instances."**
   CV_REGISTRY Types, Workshop's doc-types/block-kinds/layouts/themes/motifs are ALL registry-resolved.
   A live section/page/widget/step/selection never becomes a registry row anywhere. This is precisely
   the seam §8 names — and it's the same seam in every sub-territory examined, not one canvas's quirk.
6. **"Two ancestry mechanisms exist side by side, unreconciled"** (B4) — needs a direct architectural
   answer before one-math work touches `core/`: does address-ancestry replace, sit beside, or subsume
   Type-inheritance ancestry?
7. **"Fixed shape/kind-property tables are a recurring category of mistake, not a single retired
   instance."** Course-correction #2 retired one instance (octagon=Gateway); three more of the identical
   shape (`{kind → fixed visual property}`) were found live in this territory alone, one of them
   actively taught to the AI as canonical fact. A `grep 'shape:\s*[\'"]'` across `app/canvases` would
   likely surface more — recommended as a standing check, not a one-time fix.
8. **"A diff addresses a span, never an index."** AIEngine's `applyDiff`/`invertDiff` system is fully
   built, pure, bidirectional — structurally identical to §6's "movement = choreography over the
   address diff" — except every diff references a positional coordinate. Swap the coordinate fields for
   `CV_ADDRESS`-encoded paths and the entire diff/undo/redo/candidate-preview machinery keeps working
   unchanged while gaining insert/remove stability for free — the single cleanest, lowest-risk migration
   target found in the whole territory.
9. **"One layout concern, three engines."** Workshop's live-edit CSS flow, HTML-export CSS flow, and
   PPTX absolute-inch export are three unconnected implementations of "how do sections occupy space" —
   the sharpest concrete instance of "everything is ratios" being unaddressed, because Workshop IS a
   page-builder and this is exactly its placement seam.
10. **"A shape/value duplicated across files is the tell, not the shape itself."** The Vi-mark 3-way
    copy and the from-scratch blueprint grid (B7) are Tim's own "Design For The Class" pattern applied
    to geometry: don't patch the instance, dissolve the class (route every mark through
    `CV_SHAPES.markSVG`, every generated grid through `cv-address.zones()`).
11. **"Comment gestures at the mechanism, code never calls it"** (`DiagramSolver.jsx:74-75`) — worth
    naming as its own smell-class: a low-friction first integration point precisely because the
    author's mental model already includes the algebra, but no code path wires it in.
12. **"Placement passes the relative-not-absolute law by omission, not by design" (Layouts.jsx/
    WidgetBuilder.jsx specifically).** Neither file has a freeform placement UI today — the law isn't
    violated only because nothing yet needs placing. The moment either grows drag/resize (WidgetBuilder's
    own UI tooltip already promises "drag-drop" with zero backing code, B-flag), it should adopt
    `cv-address` spans from day one — the cheapest possible place in the whole app to do it right first,
    since there's no legacy absolute system to migrate away from.
13. **"Generic renders supersede special-cased ones — and the special-cased ones are never deleted."**
    `RenderedBlockPreview` superseding `MiniBlockPreview` fits a repeated evolutionary pattern in this
    codebase (hand-listed per-kind logic → calling the real renderer generically). A standing rule —
    delete the superseded sibling in the same commit — would be a cheap, mechanical lint check.

---

## §E · Scope additions (open questions / follow-ups for the wave)

- **B4's open question needs a direct owner-of-`core/` answer**: is CV_REGISTRY's Type-inheritance
  ancestry meant to unify with, sit beside, or be subsumed by `cv-address.js`'s spatial ancestry? Not
  resolved by reading `app/` alone.
- **`CV_SHAPES.markSVG` and `axes/texture/texture-axis.js`** were repeatedly gestured at across this
  territory as the REAL texture-pattern renderer (B7, Patterns.jsx's actual subject) but neither was
  read this pass — whichever reader owns `core/`/`assets/icons/` should read them directly; they're
  load-bearing for §1/§2 of the anchor.
- **`resolve_address` does not exist anywhere in `claude-ds`** (verified, B11) — if the Company's
  one-resolver spine (brainwave §7) exists, it's server-side in `~/company`, entirely unconnected to
  this frontend today. Worth a separate reader confirming where it lives, if it exists at all.
- **A `grep 'shape:\s*[\'"]'` across all of `app/canvases`** was suggested by one sub-reader as likely
  to surface more fixed-shape-table instances beyond the 3 found here (D7) — cheap, mechanical,
  worth running as a standing check rather than treating this list as exhaustive.
- **Route the placement absolute-vs-relative audit away from Build.jsx/AIStudio.jsx** (neither does
  spatial content-placement, B10) **toward wherever elements ARE freely positioned** — `WidgetRender`,
  `ContainmentTree`, `DiagramSolver` — none of which are in this territory.
- **AtomiCity's divergent, subset boot** (§A-8) is itself a drift risk independent of one-math (two
  hand-synced bootstraps of overlapping registries) — worth flagging to whoever eventually audits or
  merges AtomiCity against Studio, even though the two apps are correctly, deliberately separate today.
