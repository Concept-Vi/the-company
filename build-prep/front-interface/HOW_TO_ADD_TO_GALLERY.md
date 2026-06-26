# How to add things into the gallery

This is **channel content**: the whole fabric uses this to put designs into DNA's gallery
(the company's face — `counterpart/design`). It is written from the **actual code**, not
from memory. Every claim cites a file + line and is labelled in Tim's evidence scheme:
**Observed** = read directly in the source (a structural fact, incl. deductions from
control flow) · **Inferred** = pattern-matched, NOT confirmed (flagged as such) ·
**Verified** = confirmed by actually running it. *Pattern-matching and code-tracing are
**not** Verification — they prove structure exists, not that execution works.* This doc was
written by reading the code, not by running the gallery, so almost everything here is
**Observed**; "Verified" is used only where noted that the behaviour was actually exercised.

The gallery today holds **49 pieces** across `mockups/` (one directory each) registered in
**`mockups/manifest.json`** (categories: *The Slides*, *The Application*, *Further Out*).

---

## 0. The one primitive (read this first)

**Every gallery piece is the SAME two things:**

1. **A file** at `mockups/<id>/v1.html` — a self-contained HTML page.
2. **One entry** in `mockups/manifest.json` → `mockups[]` pointing at that file.

That's it. The rail lists the manifest entries; the stage loads the entry's file into an
`<iframe>`; the gallery live-injects the DNA tokens into that iframe. **Observed:**
`stage.js:31` (`mockups=manifest.mockups`), `stage.js:188-193` (the iframe mount),
`drawer-tokens.js:35-42` (the token injection on the iframe's `onload`).

The **two paths** in this guide — (A) a static hand-laid piece, (B) a data-driven unit —
**differ only in how the body of that one HTML file is produced.** The manifest entry, the
two CSS links, the canvas rule, the token discipline, and the dials are **identical** for
both. One primitive, two ways to fill it.

> **Serve over HTTP, not `file://`.** The stage fetches `mockups/manifest.json`
> (`stage.js:23`) and the data-driven path fetches `/api/...`. On `file://` those fail.
> **Observed:** `stage.js:26-29` prints *"Serve the folder over http (e.g.
> http://localhost:8090/)"* on a failed manifest fetch; `told-almanac/v1.html`'s catch
> writes *"content unavailable — serve over http"*. **Observed** (both strings are in the
> source).

---

## 1. The manifest entry (shared by both paths)

A piece is registered by appending one object to `mockups[]` in `mockups/manifest.json`.

**Observed** — the real schema, copied from the live entries (`manifest.json`, e.g.
`var-15-currentsolution` at lines 20-60 and `scr-home` at 1231-1253):

```jsonc
{
  "id": "my-piece",                       // REQUIRED. = the folder name (mockups/my-piece/)
  "title": "A Short Human Title",         // REQUIRED. shown on the stage + rail card
  "group": "New content types",           // REQUIRED. must be a known group — see §2
  "canvas": { "w": 390, "h": 844 },       // OPTIONAL. omit for a 1600×900 .view slide;
                                          //   declare it for a .screen piece — see §4
  "dials": { "warmth": 45, "register": "explanatory" },  // metadata label — see §5
  "note": "One plain sentence describing what the piece is.",  // rail card + read-aloud
  "versions": [
    {
      "v": 1,                             // REQUIRED. integer version
      "file": "mockups/my-piece/v1.html", // REQUIRED. path FROM the repo root (not relative)
      "date": "2026-06-16",
      "changes": [ "first take" ]         // shown in the stage's info strip (renderStage)
    }
  ]
}
```

Field-by-field, traced through the code:

- **`id`** — the stable handle. `select()` shows it as the meta line
  (`stage.js:72` → `$('meta').textContent=m.id`). **Convention (Observed):** matches the
  folder name for every one of the 49 pieces.
- **`title`** — `stage.js:71` (`$('title')`), rail card `rail.js:36` (`<h3>`),
  skim strip `rail.js:118`. **Observed.**
- **`group`** — decides whether the piece is **visible at all**. See §2. **Observed.**
- **`canvas`** — read by `canvasOf(m)` = `m.canvas || {w:1600,h:900}` (`stage.js:186`).
  See §4. **Observed.**
- **`dials`** — `renderStage` prints `warmth <b>…</b> · register <b>…</b>`
  (`stage.js:211`); rail card prints them too (`rail.js:38`). **Label only** — §5.
- **`note`** — rail card `rail.js:37`. **Observed.**
- **`versions[]`** — the version tabs (`buildVTabs`, `stage.js:127-134`), the compare
  before/after selectors (`buildCompareSelects`, `stage.js:156-164`), and `verFile()`
  which resolves `{v,file}` → the iframe `src` (`stage.js:184`). **Observed.**
  `select()` defaults to the **latest** version: `curV = m.versions[last].v`
  (`stage.js:73`). The rail thumbnail and Open-full also point at the last version
  (`rail.js:29`, `stage.js:205-206`). **Observed.**

> `render` (a PNG path) appears on older entries (e.g. `manifest.json:33`). It is **not
> required** — newer entries (`scr-home`, `told-almanac`) render live from the HTML and
> many omit it. The stage never reads `render`. **Observed** (no `render` reference in
> `stage.js`/`rail.js`).

---

## 2. Make the piece VISIBLE — the group ↔ category coupling (blocking)

A new manifest entry can be **silently invisible**. This is the one trap.

**Observed trace** (`rail.js:41-87`, `buildList`):

1. `buildList` walks `manifest.categories[]` (`rail.js:44`).
2. For each category it renders only its `cat.groups` (`rail.js:52`).
3. A piece appears **only if its `group` string is in some `categories[].groups`** — OR,
   as a safety net, in the top-level `manifest.groups` (those orphan groups get bundled
   under a synthetic *"Unsorted"* category, `rail.js:47-49`).
4. A `group` that is in **neither** list → the piece **never renders, with no error**.
   (**Observed** from the code path above — not exercised in a running gallery.)

So:

- **Easiest path:** set `group` to one that already exists. It just appears. The existing
  groups are listed in `manifest.json:2-18` and inside each `categories[].groups`
  (`manifest.json:1490-1531`). Example known-good groups: `"New content types"`,
  `"The wider language"`, `"Application · screens, full size"`, `"From the corpus"`.
- **A genuinely new group:** add the group string to **both** the top-level
  `manifest.groups` array **and** the `groups` array of the category it belongs to
  (`slides`, `application`, or `further`). Then pieces in that group appear under that
  category.

**Inferred (NOT verified):** the top-level `manifest.groups` array (lines 2-18) is the
master list and largely redundant with the per-category lists; the code's actual gate is
the per-category `groups` (step 3). I have not run the gallery to confirm the top-level
list is otherwise unused — to be safe, **add a new group to both.**

---

## 3. The look you build in — the PHONE ARCHETYPE + DNA tokens

Both paths render in **one design system**. Do not invent a look. Build on:

- **`ui/piece.css`** — the **1600×900 page scaffold** (`.view`): warm radial ground,
  blueprint corner (`.bp.tr`/`.bp.tl`), `.title`/`.superhead`, the `.phones` row, the
  goldwash hatch `.foot`, the `.mark`. **Observed:** `piece.css:10-28`.
- **`ui/phone.css`** — the **product chrome** components: the phones
  (`.phone` 300×600, `.phone.lg` 330×660, `.phone.sm` 240×480 — `phone.css:9-12`), the
  standalone **`.screen` (390×844)** root (`phone.css:98`), and the component vocabulary:
  `.p-hd`/`.p-sup`/`.p-h` (header), `.p-band`/`.p-bs` (stat band), `.p-rows`/`.p-row`
  (ledger), `.p-plate`/`.p-inset` (plates), `.p-act`/`.p-ghost` (the one gold action +
  the quiet second), `.p-rail`/`.p-glass`/`.p-frost`/`.p-spot` (glass chrome on imagery),
  `.p-hatch` (the page's closure), `.p-pills` (ordinal filters), `.unit`/`.role`/`.joint`
  (a captioned phone + the transport plug between screens). **Observed:** `phone.css:16-126`.
- **`:root` DNA tokens** — defined in `piece.css:32-49` between the `DNA:VARS` markers.
  Colours (`--page --warm --cool --nested --gold --ochre --bronze --bronze-line
  --charcoal --body --secondary --faint --goldwash --line ...`), the **space scale**
  (`--dna-space-3 … --dna-space-130`), radii (`--dna-radius-*`), type (`--dna-type-*`).
  **Use these via `var(--dna-...)` and `var(--gold)` etc. — never raw hex/px for
  colour/space/type/radius.**
- **`ui/organisms.js`** — the live furniture, included with
  `<script src="../../ui/organisms.js"></script>`. Returns coloured SVG/HTML strings:
  `DNA.org.icon(name,size,color)`, `iconStrip`, `mesh`, `hubNetwork`, `consequencesBox`,
  `cascade`, `detailStrip`, `phaseStrip`, `testimonial`, `checkMatrix`, `donut`, `bars`,
  `ordinalVar`. **Observed:** the export list at `organisms.js:230`; the available icons
  at `organisms.js:_icons`. Real usage: `scr-home/v1.html:29,35`
  (`DNA.org.icon('scale',18)`, the bottom rail of icons).

### Why token discipline matters (the mechanism, not taste)

A bespoke hex or px value is **dead to the dials.** The gallery re-tints every piece live:

- **Warmth dial** → `applyTokens(iframe)` → `DNA.injectVars(doc, TOK, curWarmth())`
  rewrites the colour vars on the iframe's `<html>`. **Observed:** `drawer-tokens.js:39`,
  `surface.js:74` (`injectVars`).
- **Density dial** → the spatial twin rewrites `--dna-space-*` via `injectSpace`.
  **Observed:** `surface.js:331-334`, hooked at `drawer-tokens.js:40` (`applySpaceFrame`).

So a value written as `var(--warm)` **moves with the warmth dial**; `#FEFBF6` stays frozen
while everything around it shifts. A `var(--dna-space-20)` gap **breathes with the density
dial**; `20px` does not. This is the reason — not aesthetics.

**Honest exception (Observed):** real pieces do scope a little bespoke geometry in their
own `<style>` block when the scale doesn't carry it — e.g. `app-flow-full/v1.html:8`
overrides the phone to `228×466px` to fit five phones in one slide. The real rule:

> **Ride `var(--dna-*)` (and the palette vars) for every colour, space, type and radius.
> Bespoke px is allowed only for per-piece geometry the scale genuinely doesn't carry, and
> only scoped inside the piece's own `<style>`.** Never reach for a raw colour hex — colour
> is always an address.

---

## 4. Where the canvas comes from — and why it's a hard pair with the root class

**Observed:** `canvasOf(m)` returns `m.canvas` if present, else `{w:1600,h:900}`
(`stage.js:186`). This single number drives:

- `fit()` — scaling the iframe to the stage (`stage.js:348-384`, reads `cv.w`/`cv.h`).
- the rail thumbnail's aspect — `s = 46/cv.h` (`rail.js:28`).
- comment hit-testing — `el = doc.elementFromPoint(xFrac*cv.w, yFrac*cv.h)`
  (`stage.js:293`).

So the canvas **must match the root element you build:**

| You build | Root class | manifest `canvas` |
|---|---|---|
| A page-scale slide | `.view` (1600×900, from `piece.css:10`) | **omit** `canvas` (defaults to 1600×900) |
| A standalone phone screen | `.screen` (390×844, from `phone.css:98`) | **REQUIRED:** `"canvas":{"w":390,"h":844}` |

A `.screen` piece with no `canvas` is scaled as if it were 1600×900 → it renders wrong and
its thumbnail/comment hit-testing are off. **Observed** (the three call-sites above all read
`canvasOf`; the visible mis-scale is the deduction, not run). Every `scr-*` entry declares
the 390×844 canvas (e.g. `scr-home`, `manifest.json:1239-1242`).

---

## 5. How the dials work

Two distinct things share the word "dial":

1. **`manifest.dials` (per piece) = a metadata LABEL.** `{warmth: 45, register: "..."}`.
   `renderStage` only **prints** them (`stage.js:211`); the rail card prints them
   (`rail.js:38`). **Observed: nothing in `select()` or `renderStage()` applies
   `m.dials.warmth` to the render.** A piece tagged `warmth:75` does **not** render warmer.
2. **The gallery's LIVE warmth/density dials = what actually re-tints.** Read from the
   gallery's own control (`curWarmth()` reads `#tk-warmth`, **Observed** `drawer-tokens.js:32`)
   and pushed into every shown iframe by `applyTokens` (§3). Every piece renders at the
   gallery's *current* dial position, regardless of its `manifest.dials`.

So set `manifest.dials` to honestly describe the piece's intent; just know it labels, it
doesn't drive. **`register`** values seen in the corpus (**Observed**, an open vocabulary —
no validating schema found): `explanatory`, `credible`, `precise`, `immersive`, `tension`.

---

## PATH A — add a STATIC (hand-laid) piece

This is how **48 of the 49** pieces are built. You write the HTML body yourself, on the
scaffold.

### A.1 — Create the file

`mockups/my-piece/v1.html`. The non-negotiable head:

```html
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>My Piece (v1)</title>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../ui/piece.css"><link rel="stylesheet" href="../../ui/phone.css">
```

**Observed:** this exact head is in `app-flow-full/v1.html:1-4` and `scr-home/v1.html:1-4`.
The `../../` is because the file lives two levels down (`mockups/<id>/`). **Do not** link
`ui/vars.css` and redraw `.view` yourself — that is the OLD pre-scaffold pattern (e.g.
`var-9-truetone/v1.html:4`, which hand-rolls bespoke `.card`/`.box` classes). The current
system is `piece.css` + `phone.css`.

### A.2a — A screen piece (`.screen`, 390×844) — REAL minimal skeleton

Trimmed from the real `scr-home/v1.html` (verbatim classes):

```html
</head><body>
<div class="screen">
  <div class="sbar"><span>9:41</span><span>●●●</span></div>
  <div class="p-hd"><div class="p-sup">THE WORKSHOP · WINTER</div><div class="p-h">Morning, Keeper</div></div>
  <div class="p-band">
    <div class="p-bs star"><div class="n">365</div><div class="l">days in order</div></div>
    <div class="p-bs"><div class="n">9</div><div class="l">seams open</div></div>
  </div>
  <div class="p-plate"><div class="ph2"><span id="i1"></span>Today</div>
    <div class="p-inset"><div class="iv">4</div><div class="il">cuts to enter<br>before the tide</div></div></div>
  <div class="p-rows" id="rows"></div>
  <div class="p-act">Enter Today's Cut</div>
  <div class="p-rail" id="rail"></div>
</div>
<script src="../../ui/organisms.js"></script>
<script>
  document.getElementById('i1').innerHTML = DNA.org.icon('scale', 18);
  document.getElementById('rows').innerHTML = [
    ['Seam nine, east face', 'cut and drawn', '08:12'],
    ['Seam four, west bench', 'set by weight', '09:01'],
  ].map(([t, s, v], i) =>
    `<div class="p-row"><span class="dot" style="background:${['var(--gold)','var(--ochre)'][i]}"></span>` +
    `<span class="t">${t}<span class="sub">${s}</span></span><span class="v">${v}</span></div>`).join('');
  document.getElementById('rail').innerHTML =
    ['house','ledger','chart'].map((n,i)=>DNA.org.icon(n,19,i===0?'var(--gold)':'var(--page)')).join('');
</script>
</body></html>
```

Manifest entry must include `"canvas": {"w":390,"h":844}` (§4). **Source:**
`scr-home/v1.html` (full file is 37 lines).

### A.2b — A slide piece (`.view`, 1600×900) — REAL minimal skeleton

The scaffold the page provides (from `piece.css:10-28`) wrapped around a `.phones` row of
phone archetypes. Adapted from `app-flow-full/v1.html:28-76` (simplified to two phones;
`.p-act` → `.p-act.inline` so the action sits in flow, which is real — `phone.css:58`):

```html
</head><body>
<div class="view">
  <div class="bp tr"></div>                                  <!-- blueprint corner -->
  <div class="title"><div class="superhead">My Super Heading</div><h1>My Piece Title</h1></div>
  <div class="phones">
    <div class="unit"><div class="phone sm">
      <div class="sbar"><span>9:41</span></div>
      <div class="p-hd"><div class="p-sup">CHOOSE</div><div class="p-h">The Seam</div></div>
      <div class="p-rows" id="r1"></div>
    </div><div class="role">choose · 50</div></div>
    <div class="joint"><span class="sock"></span><span class="dash"></span><span class="plug"></span></div>
    <div class="unit"><div class="phone sm">
      <div class="sbar"><span>9:41</span></div>
      <div class="p-hd"><div class="p-sup">THE BENCH</div><div class="p-h">The Cut</div></div>
      <div class="p-act inline">Enter the Cut</div>
    </div><div class="role">work · 35</div></div>
  </div>
  <div class="mark">V</div>
  <div class="foot"></div>
</div>
<script src="../../ui/organisms.js"></script>
<script>
  document.getElementById('r1').innerHTML = [['Seam nine, east face'],['Seam four, west bench']]
    .map(([t],i)=>`<div class="p-row"><span class="dot" style="background:${['var(--gold)','var(--ochre)'][i]}"></span><span class="t">${t}</span></div>`).join('');
</script>
</body></html>
```

For a slide that is a single composition (not a row of phones), use `.title` + your own
content laid out with token-driven CSS in a scoped `<style>` — but still inside `.view`,
still on the palette/space vars. Omit `canvas` from the manifest (defaults to 1600×900).

### A.3 — Register it

Append the §1 entry to `manifest.json` → `mockups[]`, with the right `group` (§2) and the
right `canvas` (§4). Reload the gallery over HTTP. The rail card and stage appear; the
warmth/density dials re-tint it live because you built on the vars.

---

## PATH B — the DATA-DRIVEN path (a normalised unit + a `unitFrom<source>` adapter)

This is the **live-compose presentation rung**: `DNA.renderUnit` (`ui/unit-view.js`) — *one
renderer, many sources.* You don't hand-lay markup; you resolve **data** into a normalised
**unit** and let the one renderer build the phone/screen look.

### B.0 — Honest status (read before using)

**This path is NOT yet wired as a turnkey gallery piece type** — three concrete proofs:

- `unit-view.js` says so itself: `renderUnit` is *"Increment 1 verifies it standalone"*;
  *"the address→data resolve + same-page hosting are the integration rung (Increment 2),
  kept out of here on purpose."* **Observed:** `unit-view.js:12-14`.
- **`index.html` never loads `ui/unit-view.js`.** Its script list (`index.html:951-959`)
  loads `surface.js`, `organisms.js`, the gallery modules and the rooms — not
  `unit-view.js`. So the gallery chrome doesn't even have `renderUnit`; a data-driven
  piece's own iframe must load it. **Verified:** `grep -n "unit-view" index.html` returns
  nothing (ran it).
- **No `mockups/*/v1.html` calls `renderUnit`.** **Verified** by `grep -rn "renderUnit"
  mockups/ index.html` (ran it) → the only hits are the *definition* in `ui/unit-view.js`
  (lines 23, 122). Line 122 is inside `DNA.renderGallery` (Increment-2's own helper),
  not a piece.
- The one genuinely live, data-driven gallery piece — **`told-almanac/v1.html`** — does
  **not** use `renderUnit`. It calls `DNA.story.node(tree,'B3')` and hand-writes its own
  `.slab` body (**Observed:** `told-almanac/v1.html` script block). It is the working
  *template* for "a piece whose words come from data."

So Path B today = **the pure renderer + the adapter pattern that exist**, composed inside
**your own piece's `<script>`** the way `told-almanac` composes its source. The general
gallery integration is not built yet.

### B.1 — The normalised unit shape (the contract)

**Observed** — `unit-view.js:20-22, 23-53`. `DNA.renderUnit(u, opts)` takes:

```js
u = {
  super,        // eyebrow → .p-sup
  title,        // → .p-h
  corner,       // status-bar left (default "9:41")
  kindLabel,    // status-bar right
  stat,         // { n, label } → the gold .p-band star figure
  prose,        // → .p-prose, under a .sec label
  proseLabel,   // the .sec label (default "What this is")
  points,       // [string]  → .p-rows of single-cell .p-row
  meta,         // [{k,v}]    → .p-rows of key/value .p-row
  close,        // truthy → adds the warm "closebg" background
}
opts = { root: 'screen' | 'phone' | 'phone sm' | 'phone lg' }   // default 'screen'
```

It returns a DOM element built entirely from **`phone.css` classes + tokens** — **Observed**
(read the `el.innerHTML` template, `unit-view.js:28-52`: only `.sbar`, `.p-hd`, `.p-sup`,
`.p-h`, `.p-band`, `.p-bs.star`, `.sec`, `.p-prose`, `.p-rows`, `.p-row`, `.p-hatch`). It is
**pure** — no fetch, no framework (`unit-view.js:11-14`).

### B.2 — A `unitFrom<source>` adapter (the pattern)

An adapter maps **one source's record** → the normalised `u`. Two ship in `unit-view.js` as
the pattern to copy:

- **`DNA.unitFromCorpus(rec)`** — a corpus `common_knowledge` record →
  `{super, title, kindLabel, prose, meta}`. **Observed:** `unit-view.js:57-77`. It reads
  `rec.output.digest` → `prose`, `rec.projection` → `super`, `rec.source_address` →
  `title`, and folds `rec.lineage` (`project/round/session`) into `meta`.
- **`DNA.unitFromStory(node)`** — an authored story-tree node →
  `{super, title, kindLabel, prose, points, stat, meta}`. **Observed:** `unit-view.js:82-97`.
  It reads `node.line` → `prose`, `node.bullets` → `points`, `node.figure` → `stat`.

These two over the **same** `renderUnit` are the proof of "one renderer, many sources"
(`unit-view.js:80-81`).

> **Do NOT edit `ui/unit-view.js`** to add your adapter — that file is DNA's. To support a
> new source, write your own `unitFrom<X>` function **inside your piece's `<script>`**,
> matching the shape above, and call `DNA.renderUnit(yourUnit, {root:'screen'})`.

### B.3 — A data-driven piece, end to end (modelled on the working `told-almanac`)

`mockups/my-told-piece/v1.html`:

```html
<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../ui/piece.css"><link rel="stylesheet" href="../../ui/phone.css">
</head><body>
<div id="mount"></div>
<script src="../../ui/surface.js"></script>      <!-- DNA.story, DNA.esc, DNA.api -->
<script src="../../ui/unit-view.js"></script>    <!-- DNA.renderUnit + the adapters -->
<script>
(async () => {
  try {
    // resolve DATA from a source. told-almanac uses the story tree (Observed, told-almanac/v1.html):
    const tree = await (await fetch('/api/content/workshop', { cache: 'no-store' })).json();
    const node = DNA.story.node(tree, 'B3');                 // the walk (surface.js:219)
    const unit = DNA.unitFromStory(node);                    // adapter → normalised unit
    document.getElementById('mount').appendChild(DNA.renderUnit(unit, { root: 'screen' }));
  } catch (e) {
    // honest degrade — a legible fallback, never a crash
    document.getElementById('mount').appendChild(
      DNA.renderUnit({ super: 'UNRESOLVED', title: '(content unavailable — serve over http)' }));
  }
})();
</script>
</body></html>
```

**Observed facts behind this:** `DNA.story.node(tree,id)` walks the tree for a node by id
(`surface.js:219-225`); `DNA.api` / `surface.js` is the only script you need for
`story`/`esc`/`injectVars` (`surface.js:508` export list); `told-almanac` fetches its source
with exactly this `/api/content/<id>` shape and degrades to a legible string on failure
(**Observed**, `told-almanac/v1.html` script). The canvas is `.screen` so the manifest entry
needs `"canvas":{"w":390,"h":844}` (§4). Register it with §1/§2 exactly like a static piece —
**the manifest doesn't care that the body was composed from data.**

**For a corpus-backed unit**, swap the resolve for the corpus shape that `unitFromCorpus`
expects (`unit-view.js:56` documents it: `{source_address, output:{digest,kind},
lineage:{project,round,session}, projection, kind}`) and call `DNA.unitFromCorpus(record)`.

---

## Checklist (both paths)

- [ ] File at `mockups/<id>/v1.html`, head links **`../../ui/piece.css` + `../../ui/phone.css`**
      (not `vars.css`). — §A.1 / §B.3
- [ ] Root element matches the canvas: `.view` ↔ no `canvas`; `.screen` ↔
      `"canvas":{"w":390,"h":844}`. — §4
- [ ] Every colour/space/type/radius is a `var(--dna-*)` / palette var. Bespoke px only for
      per-piece geometry, scoped to the piece's `<style>`. No raw colour hex, ever. — §3
- [ ] Manifest entry appended to `mockups[]` with `id`, `title`, `group`, `note`, `dials`,
      `versions[0].file`. — §1
- [ ] `group` is in a `categories[].groups` (existing group = appears; new group = add it to
      the category **and** top-level `groups`). — §2
- [ ] `dials` describes intent honestly (it labels; the live gallery dial drives the
      render). — §5
- [ ] Served over HTTP (manifest + `/api/*` fetches fail on `file://`).
- [ ] (Path B) Adapter `unitFrom<X>` written in **your piece's `<script>`**, never in
      `ui/unit-view.js`. — §B.2

---

### Provenance

All citations are from `counterpart/design` (commit at time of writing, branch `master`):
`mockups/manifest.json`, `ui/gallery/{core,stage,rail}.js`,
`ui/gallery/drawer-tokens.js`, `ui/{phone,piece}.css`, `ui/organisms.js`,
`ui/surface.js`, `ui/unit-view.js`, `index.html`, and the pieces
`mockups/{app-flow-full,scr-home,told-almanac,var-9-truetone}/v1.html`. Labels:
**Observed** = read directly in source (incl. deductions from control flow); **Inferred** =
pattern-matched, flagged as such; **Verified** = confirmed by actually running it (here, only
the three `grep`s in §B.0). Do-not-edit (DNA's, build by sight):
`ui/unit-view.js`, `ui/phone.css`, `ui/piece.css`, `ui/gallery/*`. You add your **own** new
piece file + one manifest entry.
