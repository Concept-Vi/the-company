# IMPLEMENTATION GUIDE — The Instrument Surface (the fresh paper front end)

**Second loop-prep doc.** HOW to make each `COMPLETION-CRITERIA.md` line true, grounded in `RESEARCH-SYNTHESIS.md`
(code-cited) and the MANDATE (gospel). **LEAN and scoped to the first vertical slice** — enough architecture to
reach a render Tim reacts to, no further. Tense is explicit: **IS** = exists in the repo; **WILL** = built here.

---

## 0 · PRINCIPLES (the why — don't "improve" the system back into the broken pattern)

1. **Fresh ALONGSIDE, never on top.** The new app is `surface/app`, a sibling of `canvas/app`. The working PWA on
   :5173 IS Tim's live mobile surface (Tailscale + PWA) — breaking it is a regression. The new app runs on **:5174**,
   same Vite toolchain, same `/api`→:8770 proxy. *Why:* MANDATE says treat the design as fresh and "don't even look
   at" the old UI — but the old UI must keep working until the new one supersedes it. Two apps, one bridge.

2. **Address and motion-identity are INSEPARABLE (the coupled rule, §H#5).** Every interactive node carries BOTH
   its `ui://` address (`data-ui-ref`, L10) AND a unique Framer Motion `layoutId` (L3). One identity, two faces:
   the relational spine reads the address; the motion system reads the layoutId so hidden→shown/moved animates
   without teleport. *Why:* building these independently produces elements that are addressable OR animated, never
   both — and the bar (criteria S1.2/S3.1) demands both on the same node.

3. **Registry-is-truth; zero hardcodes.** Sector count, wedge angles, ring count, lens list, colours-by-kind, pole
   vectors — ALL resolve from the `/api/projection` response (`sectors`, `rings`, `grid`, `bindings`) and the
   binding's `angle_from`/`radius_from`. *Why:* a new binding file = a new lens with zero front-end edit (SYNTHESIS
   §B/§D). Hardcoding any of these forks the truth and breaks the universal-instrument property (L12).

4. **Fail loud, never silent.** Malformed `ui://` → a Notice (mirror the backend 400). Missing data → an explicit
   empty-state, never a faked point. *Why:* `no-silent-failures` is a standing law; a swallowed error reads as
   "works" and compounds (Business Stakes).

5. **The seed IS the layout grid (proportion by construction, L3).** SVG `viewBox` and all spacing lock to the
   seed constants — `m=2^k`, `m/2` rings, `x=2π/n`, the `[0.06,1.0]` radius band, dyadic spacing {8,16,24,32,48,
   64,96,128}. *Why:* "nothing out of proportion" becomes structural, not policed after the fact.

6. **Resting-state-first (inverts the usual workflow, L2/L6).** Design the near-empty resting view FIRST, then
   graft detail onto disclosure states. *Why:* text is the most expensive thing on screen; a content-rich-then-prune
   workflow leaves text walls behind.

---

## 1 · THE SLICE ARCHITECTURE (what WILL be built)

**Goal of the slice:** one lens — **the instrument wheel** — rendering real Company data on the seed geometry,
in the paper aesthetic, fully animated, native at all three form factors, addressed + context-resolving, with
three taste toggles Tim flips. The smallest complete proof of the whole mandate.

### File tree (NEW unless marked)
```
surface/                         NEW — the fresh app root (sibling of canvas/)
  app/
    package.json                 NEW — React 18.3 + react-dom + framer-motion; vite 6 + @vitejs/plugin-react + ts
    vite.config.ts               NEW — port 5174; proxy /api→VITE_API_TARGET||http://localhost:8770; allowedHosts ['.tail777bc2.ts.net']
    tsconfig.json                NEW
    index.html                   NEW — viewport-fit=cover; #root
    src/
      main.tsx                   NEW — React root
      App.tsx                    NEW — the shell: picks the layout module by viewport; hosts the wheel + toggles
      tokens/
        paper.css                NEW — the §E token set (grounds/ink/pigment/elevation/type/spacing/radii)
        motion.ts                NEW — the single motion system (springs/curve/durations; reduced-motion)
      lib/
        api.ts                   NEW — thin fetch over the bridge (fail-loud); typed by the projection contract
        address.ts               NEW — the address spine: stamp helper, capture listener, indicate, resolveUiTarget, context_at
        seed.ts                  NEW — seed constants + polar→cartesian helpers (the layout grid)
      wheel/
        Wheel.tsx                NEW — the SVG wheel: rings + sector wedges + point cloud; angle-hue; layoutId+ref per node
        PointCloud.tsx           NEW — points placed by (theta,r); peek on hover/tap
        Disclosure.tsx           NEW — the peek→open→pin→dismiss card; calls context_at; form-factor aware
      layouts/
        Desktop.tsx              NEW — 1440×900: centered wheel + ambient side strata stub
        Portrait.tsx             NEW — 390×844: full wheel + bottom-sheet disclosure + thumb arc
        Landscape.tsx            NEW — 844×390: wheel + persistent right rail
      toggles/
        Taste.tsx                NEW — typeface / pigment / motion toggles (slice-only scaffold)
```

### REUSE (do not copy — bind to these)
- **`GET /api/projection`** (`runtime/bridge.py:1047`) — the data source. Contract verified below.
- **`GET /api/context?address=`** (`bridge.py:1194`) — the R2 scored context bundle (§A read face).
- **`GET /api/ui_info`** (`bridge.py:1178`) — capability flags (pointable/openable/…), if affordance-gating is needed.
- The **bridge on :8770** — already running (managed). The surface is THIN over it.

### REFERENCE (read for the pattern, change nothing)
- `runtime/bridge.py:987-990` — the **capture-phase `data-ui-ref` listener** convention (only full `ui://` are loci).
- `canvas/app/vite.config.*` — the proxy/allowedHosts pattern to mirror (NOT the app code).
- `runtime/projection.py:819-893` — the exact point + top-level contract (below). **Do not edit the engine for the slice.**

---

## 2 · THE PROJECTION CONTRACT (verified — build the renderer against THIS, not an inference)

`GET /api/projection?binding=<id>` returns (read from `projection.py:862-893`):

```ts
type Projection = {
  center: string; now: string; n: number;          // n = sector count (the lock x=2π/n)
  binding: { id: string; label: string; angle_from: string; radius_from: string; order_by: string;
             radius_normalized?: boolean; space?: string;
             poles?: {a:any;b:any}; types_space?: string };
  bindings: { id: string; label: string }[];        // THE LENS PALETTE — registry-true, render the switcher from this
  sectors: { id: string; label: string; from: number; to: number }[];  // wedge bounds in RADIANS
  edges:   { from: number; to: number; bidir?: boolean }[];            // G10 directed chords (sector indices)
  separation?: any;                                  // G9 fifth gate (separator mode only)
  nucleation?: any;                                  // G12 report (nucleation mode only; per_item rides on points)
  rings: number; grid: number;                       // m/2 concentric circles; dyadic grid m
  lock: string;
  points: ProjPoint[]; count: number;
};
type ProjPoint = {
  seq: number; kind: string; sector: string;
  theta: number; r: number; depth: number;           // POLAR: theta rad, r in [0.06,1.0] (pile >1 in nucleation)
  cell: { i:number; j:number; d:number };            // dyadic structural coord (the square half)
  address: string; summary: string; ts: any;         // summary already truncated to 140 — text-minimal source
  phases: { day:number; week:number };
  source?: string;                                   // embeddable key (re-centre on the item, not its run:// record)
  r_struct?: number; strain?: number;                // G7 (semantic only)
  pull_a?: number; pull_b?: number; lean?: number; pole?: 'a'|'b'|'—';  // G9
  fit?: number; assigned?: string; inside?: boolean; pile_cluster?: number; tail?: boolean; born?: boolean;  // G12
  r_unknown?: boolean;                               // semantic point with no vector (rim + flag)
};
```

**Render math (the seed grid → screen):**
```
R = 0.46 * min(W,H)                         // wheel radius leaves a margin band (seed proportion, not ad-hoc)
cx, cy = center of the wheel region
point:  x = cx + p.r * R * cos(p.theta)     // theta is already in radians, even-divided by the lock
        y = cy + p.r * R * sin(p.theta)
rings:  for k in 1..rings:  circle radius = (k / rings) * R          // m/2 concentric circles
sectors: wedge i spans [sectors[i].from, sectors[i].to] radians; hairline radial spokes at each boundary
hue:    sector i → hsl( 360 * i / n , SAT, L )      // angle-hue = colour-IS-geometry (the ONE colour inheritance)
```
SVG `viewBox="0 0 W H"` so it scales crisply; the `<svg>` is the addressable container; each ring/sector/point is
a child node carrying `data-ui-ref` + `layoutId`. The ~3,038-point cloud: start in SVG (resting view is sparse per
L6; a binding's default `limit` keeps it modest); reserve a Canvas layer (SYNTHESIS §F) only if a real density
test janks — do NOT pre-optimize.

**Drivable params (for the slice):** `binding=` (from `bindings[]`), `center=` (a `ui://` address or `now`),
`limit=`. Other axes (`at` scrubber, `pole_a/b`, `dial`, `rung`) are PHASE-2 lenses — not in the slice.

---

## 3 · THE ADDRESS SPINE (the ONE inheritance — inherit ONLY this, faithfully; SYNTHESIS §A)

`src/lib/address.ts` implements, mirroring the backend convention exactly:
- **stamp(addr)** → returns `{ 'data-ui-ref': addr }` props; the literal full `ui://` string, set **before first
  render** (no interpolation on render — the baked-in corpus convention). Each addressable element ALSO gets a
  `layoutId` equal to its address (one identity, two faces — principle 2).
- **install capture listener** (mirror `bridge.py:987-990`): `document.addEventListener('click', onDocClick, true)`;
  read `e.target.closest('[data-ui-ref]')`; only act if the ref starts `ui://`; **additive** — no `preventDefault`/
  `stopPropagation` (normal clicking still works).
- **indicate(addr)** → set the locus, paint `.ui-indicated` (a soft paper highlight, animated), record a journey step.
- **resolveUiTarget(addr)** → THE SINGLE SINK for all navigation (click / future voice / future gesture). Validates
  grammar; **fails loud** (a Notice) if the grammar is malformed; dispatches: a point address → camera/scroll +
  `.ui-spotlight`; then opens the disclosure.
- **contextAt(addr)** → `GET /api/context?address=` → render the R2 bundle (recency·proximity·pin scored, capped at
  4000 chars; show "n more beyond cap" if over). **Never hand-compose the ancestor chain** — one call does it.

*Constraint:* never fabricate an address (corpus rule 8). Dynamic points mint `ui://canvas/<seq-or-node-id>`.

---

## 4 · THE THREE LAYOUT MODULES (authored independently, L5; SYNTHESIS §G)

`App.tsx` selects the module by viewport (discrete media-query switch, NOT arithmetic scaling):
- **Desktop.tsx (≥1024w landscape):** wheel centered (~ min(W,H) region); ambient side strata stub (256–288px,
  toggleable); top bar 56px; bottom control strip. 12-col / 8px base. Resting words 5–8.
- **Portrait.tsx (≤768w, portrait):** full-width wheel; **bottom sheet** (peek handle 48pt, draggable, expands to
  ~60%); **thumb control arc** in the 0–120px bottom easy-zone. Safe areas via `env(safe-area-inset-*)`,
  `viewport-fit=cover`. 4px base. Resting words 2–4.
- **Landscape.tsx (≤768h, landscape):** wheel left (~70%); **persistent right rail** (~30%, non-modal): pinned
  selection (top) + actions (mid) + scrollable secondary. Resting words 8–12.

All three share the SAME `Wheel` + `Disclosure` + address spine + motion system — only the chrome arrangement and
the disclosure host (side panel / bottom sheet / right rail) differ. Touch: 44×44pt min targets, 12pt spacing, no
hover-only controls on touch (tap-once = peek, tap-twice/long-press = open).

---

## 5 · THE SINGLE MOTION SYSTEM (`tokens/motion.ts`, L3; SYNTHESIS §F)

One module, imported everywhere (no per-component values):
- **springs:** `gentle={stiffness:100,damping:20,mass:1}`, `snappy={stiffness:170,damping:15,mass:1}`.
- **eased:** `cubic-bezier(0.4,0,0.2,1)`.
- **durations:** enter 300–400 / move 300–500 / exit 250–350 / colour 150 ms.
- **rules:** animate ONLY `transform`+`opacity` (compositor; no reflow); shared `layoutId` per element so
  hidden→shown and lens-morph tween (no teleport); honour `prefers-reduced-motion` (snap to end, no motion).
- The **motion taste toggle** (S4.3) swaps `spring(gentle)` ⇄ `eased` at the transition level so Tim sees both.

---

## 6 · SEQUENCE OF OPERATIONS (build order — matches the criteria priority)

1. **Scaffold** `surface/app` (package.json, vite.config.ts on :5174 + proxy, tsconfig, index.html, main.tsx). `npm
   install`. Confirm `npm run dev` boots and `canvas/app` on :5173 still boots. (S0.1)
2. **Tokens** `paper.css` + `motion.ts`; a throwaway swatch view to eyeball the system. (S0.2/S0.3)
3. **api.ts + seed.ts** — typed fetch (fail-loud) + the polar/seed helpers. Curl-verify the projection shape first.
4. **Wheel.tsx + PointCloud.tsx** — render rings/sectors/points from real `/api/projection?binding=raw`; angle-hue;
   stamp ref+layoutId per node. (S1.1)
5. **Lens switch** from `bindings[]`; morph on switch. (S1.2)
6. **address.ts** — capture listener + indicate + resolveUiTarget + contextAt. (S3)
7. **Disclosure.tsx** — peek→open→pin→dismiss; show real summary + context bundle. (S1.3)
8. **Layout modules** — Desktop / Portrait / Landscape; wire the disclosure host per factor. (S2)
9. **Taste.tsx** — typeface / pigment / motion toggles. (S4)
10. **Verify** — drive at all three form factors, design-critic, fix, commit, surface to Tim. (S5)

---

## 7 · DO / DON'T (lessons baked in)

- **DO** read every renderable value from the projection response + tokens. **DON'T** hardcode sector count,
  colours-by-kind, ring count, or the lens list — *because* a new binding must appear with zero edit (registry-is-truth).
- **DO** stamp `data-ui-ref` as the literal full `ui://` string before first render. **DON'T** interpolate it on
  render — *because* the corpus/backend convention is the baked string and `resolveUiTarget` querySelector-matches it.
- **DO** give every addressable node a `layoutId`. **DON'T** animate width/height/left/top — *because* that reflows
  and janks; transform+opacity only (compositor).
- **DON'T** touch `canvas/app` or the projection engine for the slice — *because* :5173 is Tim's live PWA and the
  engine has 91 passing tests; the slice is pure-additive.
- **DON'T** show resting per-point text. **DO** carry `summary` into the disclosure only — *because* text is
  cognitive load (L2) and the resting gestalt must read at a glance.
- **DON'T** declare any line green from code-reading or a DOM query — *because* the bar is whole-screen gestalt by
  use, at three form factors, judged by a separate critic (MANDATE §5).

---

## 8 · DEEPEN-LATER (PHASE-2 — sequenced, not parked; detailed after Tim reacts)

Re-home all 12 lenses · live SSE spine (`/api/stream`, gapless `Last-Event-ID`) · the multipurpose strata · the
project system on `lineage.project` (company = starter) · embed registry definitions via the company MCP (nucleable
symbolic registries) · the registry-promotion gesture (reuse `/api/registry/proposals` + MCP `propose_role`/
`edit_role`/`delete_role`; instrument pure-read, operator acts through proposal→approval→execution). Each gets its
own criteria once the slice calibrates Tim's taste. See `COMPLETION-CRITERIA.md` §PHASE-2.

*This guide is lean by design: enough to reach a render Tim reacts to. The depth comes after, driven by his reaction.*
