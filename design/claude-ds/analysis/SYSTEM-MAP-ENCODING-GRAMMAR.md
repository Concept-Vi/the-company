# System Map — Visual-Encoding Grammar

> Piece 4 of the living-codebase-canvas work. This is the **draft + handoff spec** for the System
> Map's visual encoding. The data lives in its single home — `CV_MEANING.encodings('system-map')`
> in `assets/icons/cv-meaning.js` — and is baked into `system/system-map.json` by
> `system/build-system-map.js`. The map (`system/system-map.html`) is a *projection* of it.
> Claude Code builds out the channels marked `draft:true` and extends the vocabulary from the
> registry — never by hardcoding a parallel list in the UI.

## The one idea

A file/folder has **facets** (metadata). The canvas turns facets into **channels** (what you see).
An **encoding set** is one binding: `facet → channel`, plus how each value looks. Recognition is
offloaded to spatial/visual cognition (colour, size, texture, border, glow) so reasoning stays free
for meaning. The vocabulary is single-sourced and loadable — exactly like a `CV_MEANING` profile,
because it *is* one (surface-scoped).

## Channels (the visual properties of a node)

| Channel | What it controls | Reserve for |
|---|---|---|
| `colour`  | fill / tint of the node | the primary recognition anchor (system, type, heat) |
| `size`    | area, **always relative to siblings within the same folder** | magnitude (bytes, links, used-by) |
| `texture` | surface pattern (hatch / dots / grid / lines / cross) | a second categorical facet without spending colour |
| `border`  | edge weight + tone | depth / state without changing fill |
| `glow`    | outer halo | **liveness only** — changed / attention / selected |
| `opacity` | fade | de-emphasis without removal |

One facet may drive several channels; one channel is driven by one *active* set at a time (the
selector picks it). Size and colour are independent selectors today; texture/border/glow are drafts.

## Facets (the metadata a set can bind)

`role` (system membership) · `ext` (file type) · `roleGroup` (broad kind: code/token/asset/doc/…)
· `links` (degree = in+out) · `usedBy` (how many depend on it) · `bytes` (size on disk)
· `depth` (nesting level) · `state` (derived: changed / unwired / selected). Add a facet by
computing it on the node in the generator (or deriving it in the map) and referencing it from a set.

## Set schema

```jsonc
"<set-id>": {
  "channel": "colour|size|texture|border|glow|opacity",
  "facet":   "role|ext|roleGroup|links|usedBy|bytes|depth|state",
  "label":   "Selector label",
  "kind":    "discrete | scale",
  "description": "Plain-language: what it shows and why it helps.",

  // discrete:
  "values":   { "<facetValue>": "<appearance>" },   // colour hex, texture id, etc.
  "fallback": "<appearance>",                         // when a value isn't listed
  "folderColour": "#3a342a",                          // optional: folders' colour for colour sets

  // scale (continuous):
  "scale": "linear",
  "stops": [[r,g,b],[r,g,b],[r,g,b]]                  // colour scales interpolate across stops
}
```

## Sets drafted today (in `CV_MEANING.encodings('system-map').sets`)

**Live now** (the map reads these):
- `role-colour` — colour ← role. The main spatial anchor (axes gold, registries blue, components
  green, tokens amber, ingest/inspo/upload muted). Drives `rc()` and the System colour mode.
- `type-colour` — colour ← ext. JS/CSS/MD/image mix.
- `link-heat` — colour ← links (scale, cool→gold→red). Finds hubs.
- `usedby-size`, `filesize-size`, `links-size` — size ← usedBy / bytes / links. (The map's Size
  selector currently implements these as `SIZERS`; they mirror these sets 1:1 and should resolve
  from here once Claude Code unifies them.)

**Draft — Claude Code to build live** (`draft:true`, data + intent only):
- `depth-border` — border ← depth. Deeper files → lighter/thinner border so shallow structure reads
  bolder.
- `kind-texture` — texture ← roleGroup. code=plain, token=grid, asset=dots, doc=lines, archive=cross,
  ingest=hatch. Lets kind read without spending colour.
- `state-glow` — glow ← state. changed=gold, unwired=clay, none. Glow = liveness only.

## How the map consumes it (the projection)

1. `build-system-map.js` is called with `encoding = CV_MEANING.encodings('system-map')` and writes it
   to `model.encoding`. `system-map.json` is the OUTPUT; the registry is the source.
2. `system-map.html` sets `ENC = DATA.encoding` on load. `encSet(id)` reads a set; `rc()` and the
   `COLORERS` (type, heat) resolve their values from `ENC`, falling back to the inline tables only if
   the profile is absent. **No second home** — change a colour in `cv-meaning.js`, rescan, the map
   updates.

## How Claude Code should extend it

- **New colour/size set** → add an entry under `sets` with `channel` + `facet` + values/scale; it
  appears in the matching selector (projection) with zero UI code.
- **A draft channel (texture/border/glow)** → implement the channel renderer in the map keyed off the
  set's `channel`, reading `values`/`scale` from `ENC` — never a hardcoded switch on facet values.
- **Per-context profiles** → register another encoding for a different surface, or a variant for the
  same surface, with `CV_MEANING.encodings.register(surface, profile)`; profiles round-trip to JSON
  so they’re authored/edited without code (same as meaning profiles).
- **A new facet** → compute it on the node (generator or map), document it in the Facets table, then
  reference it from a set.

## Principle gate

The encoding vocabulary is one registry (`CV_MEANING.encodings`) projected into the map's selectors
and legend. The map holds **references**, not copies. If you find yourself writing a colour/size/
texture value inside `system-map.html`, that's drift — move it into the encoding profile and read it.
