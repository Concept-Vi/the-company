# The Glyphic Language — founding spec + howto

> A glyphic is not an icon — it is a **sign in a visual language**. Its meaning is a
> **field** (a feeling + a cluster of senses), composed across its facets. The English
> sentence is a **read-out** — one projection for humans; the meaning lives in the facets,
> never borrowed from another language. (Tim, 2026-06-29.)

## The one law
**Meaning is a field, not a single thing.** A facet value carries a *feeling* and a cluster
of *senses*; context and combination resolve it to a sense. A thing that means one fixed
thing is a lookup, not a language. And meaning is **combinatorial**: the combination of facet
values means, not each facet alone.

## The home
The meaning registry (`assets/icons/cv-meaning.js`, `window.CV_MEANING`) is the **one home**
of meaning. The language layer lives there — fields, types, the combinatorial read, and the
read-out. Nothing else stores meaning; consumers read from here. **Loud-fail law:** an unknown
facet / value / required lookup THROWS — no fallback, no silent default.

## The four layers
1. **Fields** — every `(facet, value)` → `{ feeling, senses[], type }` (+ `token`/`phrase`).
   `CV_MEANING.field(facet, value)` returns it (throws if unseeded).
2. **Types** — the *kind* of meaning each facet contributes; a glyph carries several at once:
   form=`kind` · symbol=`thing` · fill/outline=`mode` · color=`state` · texture=`material` ·
   depth=`prominence` · motion=`liveness` · line=`relation-mood` · edge=`relation` · direction=`role`.
3. **Combination** — `mode` is read from fill + outline + icon-presence *together* (the clearest
   case of meaning that depends on a combination). More combination rules grow here.
4. **Read-out** — `CV_MEANING.describe(spec)` → `{ sentence, parts, meaningSet }` for one glyphic;
   `CV_MEANING.describeRelation({source, edge, target})` for a relation (nests the node meanings).
   `CV_GLYPHIC.describe(spec)` delegates here so any glyphic, anywhere, says itself.

## The parts of speech (the seed dictionary — grows in use)
- **FORM = what kind of thing.** circle = *the kind itself* · square = *a specific one* ·
  triangle = *an operation on it* · diamond = *interacting with it (deciding is one kind)* ·
  pentagon = *a feature* · hex = *a system* · heptagon = *a special case* · octagon = *a gateway*.
- **SYMBOL = which thing** (intrinsic; a small `symbolGloss` maps icon→word, e.g. house→home).
- **FILL+OUTLINE = mode.** dashed = *potential* · none = *held as a concept* · paper = *here, in
  context* (+ icon → *present*) · wash = *featured* · solid = *full/set* *(needs a solid-colour
  fill value in CV_GLYPHIC — flagged)*.
- **COLOR = state, on common connotation.** active/gold · positive/sage · error/clay ·
  warning/amber · info/blue · neutral/bronze · muted.
- **TEXTURE = material.** grid = *structured/engineered/mathematical* · hatch = *worked-on* ·
  lines = *directional* (NOT "AI-generated") · dots = *partial* · cross = *crossed-out*.
- **DEPTH = prominence · MOTION = liveness.**
- **EDGE (the relation-carrier, not a "verb").** line = the relation's mood (solid=*is*,
  dashed=*could*, dotted=*tentative*, lines=*ongoing*, **right-angled=*routed*, curved=*organic*,
  free=*loose*** — Tim's additions) · edge = the specific relation (face/higher-order/navigates) ·
  direction = role (subject→object).

## The levels (the same subject·relation·object shape, fractal, no ceiling)
facet (morpheme) → glyphic (word; and a micro-clause via the ring holding the icon) →
edge (the relation) → node·edge·node (a clause) → a container's three slots (the simplest
complete sentence) → nested containers (paragraph → page). Containment is itself a relation,
not merely a size.

## Glyphic = address
Addresses are the **nouns**, edges the **verbs**: the Company's address/registry world and a
glyphic are the **same language at two heights**. The read-out is the universal interface —
anything, at any level, can be made to say itself.

## Status (honest)
- Verified by running (`_demo/verify_language.js`): the read-out composes from facets
  (octagon+house+wash → *"a gateway holding the home, featured, at rest"*), the combinatorial
  mode changes with fill, relations say themselves, and every loud-fail case throws.
- Page: `system/language.html` (marks saying themselves, the mode trio, the relation) — renders
  via the live engine; visual layout pending an on-device look.
- **Starter, grows in use** — the dictionary is meant to be authored as meanings come, via the
  registry + Vi. Soft cells flagged: the fine grain of FORM vs FILL at the lower layers; the
  solid-colour fill value + dashed-outline render (the "missing parts" still to build in
  CV_GLYPHIC); kind+thing composition (square+house → "this home").
