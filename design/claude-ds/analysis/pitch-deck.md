# Analysis · `pitch-deck`

> Source: `ingest/pitch-deck/` · 17 pages · copied to `_ingest/pitch-deck/`
> Status: ☑ complete · baseline folder (sets the vocabulary all others are tested against)
>
> **Content-agnostic note:** the deck's subject (property / virtual hubs / capital raise)
> is incidental. Everything below is recorded as *universal structural grammar* — the
> property nouns are replaced with generic roles (e.g. "relationship diagram", "hero metric").

---

## 0 · Frame
- **1930×1085 px → 16:9** (1.778). Medium: on-screen **presentation**, but already carrying interactive affordances (see §5) — i.e. a deck intended to become a component.
- Coordinate basis: 100% = the slide; everything below is measured as **% of frame** so it survives re-rationing.

## 1 · Grid & spatial structure *(measured)*
- **Outer side margins ≈ 12%** each (symmetric), giving a **~76% content band**.
- **Title top ≈ 7.5%** of height; title is either centered (workhorse) or top-left (split layouts).
- **Footer zone** ≈ bottom 3–4%: a thin diagonal **gold hatch rule** (left ~60% width) + a circular **gold V mark** bottom-right. Present on nearly every analytical slide → a persistent "frame signature".
- Two macro-layouts:
  - **CENTERED** — title centered at ~7.5%, lede beneath, content fills the 76% band.
  - **SPLIT** — left **visual zone** (~0–46%, **bleeds off the left/top edges**), right **content zone** (~50–88%); on some slides a **hairline vertical divider** (~46%) with a thin **arrow crossing it** (visual → content). The off-edge bleed is the deck's "ghosted continuation".
- Cards/panels: large corner radius (~1% of width ≈ 16–20px here), very soft low shadow, generous internal padding (~3–4% of width).

## 2 · Tonal zoning *(sampled — THE key recalibration)*
The zoning is **near-imperceptible** and built from **undertone + texture + emboss, not hue**:

| Role | Sampled hex | Δ from white | Notes |
|---|---|---|---|
| Ground | `#fefefe`–`#ffffff` | — | pure white base |
| Warm ivory wash | `#fdfcf7` | ≈ −2G −7B | default soft panel/card |
| Warm cream | `#fcf9f4` | ≈ −5G −10B | slightly warmer panel |
| **Neutral grey wash** | `#f8f8f8` | equal RGB | the **"distinct/third"** surface — *neutral, not another warm* |
| Embossed panel | `#f6f8f7` | faint cool | hero-number boxes; subtle raised/inset |
| Hatch-ivory band | `#fdfcf5` (spread ~20) | warm + texture | full-width metric bands; faint diagonal gold hatch |
| Blueprint ghost | ~`#fefefe` | barely there | faint architectural linework, esp. top band |

**Rule:** large regions separate by ~1–3% warm-vs-neutral undertone, optionally a diagonal **hatch** texture or a soft **emboss**. In a set of sibling cards, the odd-one-out is rendered **neutral grey** while the rest are **warm ivory** — that warm/neutral pairing *is* the semantic signal, felt not seen. → The current `--zone-*` palette is far too saturated and too hue-coded; **recalibrate to this ladder** (see SYSTEM-GAPS).

## 3 · Type
- **Display/heading:** bold humanist sans (Source-Sans/Open-Sans family character), near-neutral ink `#191919`. Slide title ≈ **4.5–5% of frame height** (~48–52px here). Centered or top-left.
- **Lede/intro:** regular, warm-grey (`#3A3026`/`#5A4F38`), centered, ≈ 2%h (~22px), often `.measure`-capped to ~2 lines.
- **Body/bullets:** regular ≈ 1.8%h (~20px), dark; **bold** used inline for key terms.
- **Section header:** bold **bronze** `#c09d5d`, ≈ 2%h, centered over its panel.
- **Italic connective captions:** bronze italic — the "felt" voice that links panels / closes slides.
- **Hero metric:** bold **gold**, large (~3–4%h), paired with a small 1–2-line grey label to its right.
- **Special treatment:** the brand **V** substituted into a headline word (gold V in "**V**irtual Tours"); recurring circular **V mark**.

## 4 · Colour & brand *(sampled empirically by hue clustering)*
- **The brand is a RAMP, not one gold:** bright gold `#dad364` → **primary gold `#d6bf57`** → **bronze `#c09d5d`** → **tan/brown `#b98664`** → (deep brown). Used as: bullets/arrows/hero numbers (bright/primary), section headers (bronze), **diagram ring sequence** (full ramp top→bottom), hatch lines (gold).
- Current system `--accent-gold: #E0C010` is **more saturated/acidic** than the deck's working gold → soften toward `#d6bf57` and **add the ramp**. `--accent-bronze: #988058` reads **darker/greyer** than the deck's `#c09d5d` → warm/lighten.
- **Accent coral/terracotta `#d4907a`** — sparingly (photographic accents).
- **Chart/dataviz palette (multi-hue ONLY here):** gold + navy `#212d5b` + blue `#4c7bc8` + green `#8aae48`/`#35a550` + red `#d4726c` + orange.
- Title ink reads near-neutral `#191919` (deck) vs warm `#1F1A12` (system) — minor; keep warm.

## 5 · Atoms *(catalogue)*
- **Triangle/play bullet** — solid gold ▶, precedes each list item.
- **Soft stat panel** — rounded warm/neutral panel grouping KPIs.
- **Hairline gold OUTLINE callout** — outline (not fill) box for a headline stat (logo + big number + supporting line).
- **Hero-metric chip** — embossed light box holding a big gold number ($300k / $5.5M).
- **Big-number + label pair** — gold number, small 2-line grey label.
- **Outlined pill** — rounded-rect, gold/bronze border, label inside; used in rows where the **border colour gradates along the ramp** (gold→brown).
- **Icon-flow row** — thin single-weight line icons on a **dashed baseline** converging to a plug/browser node ("tools → platform" motif).
- **Checklist item** — gold/green check in a rounded square + label.
- **Badge** — hexagon + diamond brand badges, soft shadow, version label beneath.
- **Profile block** — circular photo + bold bronze name + role + stat triplet.
- **Logo strip** — partner logos in a muted row.
- **Hatch** — diagonal gold hatch as full-width band (behind metrics) and as the bottom baseline rule.
- **Connector** — thin line + arrowhead crossing the split divider; dashed connectors (with plug icon) between panels and in flow/timeline diagrams.
- **Interactive affordances (deck→component bridge):** hotspot dots (state-coloured ⊙ green/amber/red = approved/review/declined), **MENU** pill (dark, chevron), account icon (top-right), info "i" markers, embedded 2D dashboard/panel chrome.

## 6 · Layout patterns *(archetypes — candidate templates)*
1. **Full-bleed photographic cover** — logo lockup + bronze subtitle + hotspots + MENU + hatch baseline.
2. **Split visual/content** — bleeding diagram/collage left, title+bullets+icon-row+callout right, optional hairline divider + crossing arrow.
3. **Centered title + lede + body** — the workhorse.
4. **Two-panel compare** — soft panels side-by-side + dashed connector + italic footer.
5. **Mode columns** — parallel screenshot columns + centred badges.
6. **Triptych cards** — 3 columns, **2 warm + 1 neutral**, image + bullets.
7. **Metric band** — full-width hatch band of KPIs.
8. **Dual checklist + logo strip.**
9. **Timeline/flow diagram split** — axis + outlined nodes + dashed connectors.
10. **Profile / feature panel.**
11. **Terms panels** — multi soft-panel with hero-number chips + bullet lists.
12. **Gallery grid** — 2×3 screenshots + italic lede/footer.
13. **Contact / closing** — full-bleed + info card + action pills.

## 7 · Sequence & rhythm
- **Arc:** Cover → Problem (complexity → friction) → Solution → How it works (modes / adaptive UI / spans types) → Proof & science (journey metrics, field-testing) → Product & market → Readiness (threshold, partners) → GTM (timeline, advocacy, leader) → Ask (funds, terms) → Contact.
- **Density rhythm:** photographic **full-bleed covers bookend** and act as "breaths"; analytical white slides in the middle **alternate medium/high density**. Hatch metric bands and dense panels appear at density **peaks** (proof, terms). Italic bronze captions cushion transitions.

## 8 · Construction *(recipes — fixed vs fluid)*
- **Frame signature** (all analytical slides): top centred/▦ title at 7.5%, 12% side margins, bottom hatch rule + V mark. Fixed anchors; body fluid between.
- **Split:** left zone is a **bleed layer** (z-below, overflows frame); right zone is a `.stack` of title → bullets → icon-row → callout. Divider + arrow are an overlay aligned to the zone boundary.
- **Triptych:** `.grid-fit` of 3; surface roles = [warm, warm, neutral]; each card = media (ratio-locked) → bullet `.stack`.
- **Metric band:** full-bleed hatch surface; KPIs in an even `.cluster`/`.switcher`, each = hero-number + label pair.
- **Terms panels:** `.grid-fit` of soft panels; each = bronze header → hero-number chip → bullet list.

## 9 · Responsive rules *(native 16:9 → other surfaces)*
- **Desktop:** essentially native; hold the 76% band, scale type with `--fs-*` clamps, keep margins at 12% (cap max).
- **Mobile portrait:** **split → stack** (visual becomes a full-bleed media block on top, content below); **centered stays centered**; **triptych → 1-col**; **metric band → 2-col grid**; side margins **12% → 5–6%**; title size via clamp; **icon-flow row → wrap or scroll** (`.reel`).
- **Mobile landscape:** closest to native ratio — split can stay side-by-side but compresses; metric band stays a row.
- **Ratio rules:** margins scale but clamp to a min; the split ratio (~46/54) collapses below tablet; radial/hub diagrams keep their geometry, while **network/timeline diagrams reflow or simplify** (node positions are %-of-container, connectors re-route).

## Diff vs current system
- ⚠️ **Zoning** — current `--zone-*` too saturated/hue-coded → recalibrate to the §2 near-white ladder (warm-ivory / warm-cream / neutral-grey / emboss / hatch).
- ✏️ **Gold** — soften `--accent-gold` toward `#d6bf57`; **add a gold→bronze→tan ramp** (the diagram/sequence ramp `tokens/diagram.css` hinted at, now with real values).
- ✏️ **Bronze** — warm/lighten `--accent-bronze` toward `#c09d5d`.
- ➕ **New motifs** — diagonal hatch, blueprint ghost, embossed hero-number chip, hairline-outline callout, outlined pill w/ ramp border, icon-flow connector row, hex/diamond badge, profile block, interactive-affordance atoms, the bottom hatch+V "frame signature".
- ✅ **Confirms** — fluid type, `.grid-fit`/`.switcher`/`.stack` primitives, `.measure`, soft elevation, thin-line icon language, the "gold = decision/accent only" discipline.

## → Gaps logged
See `SYSTEM-GAPS.md` (updated this session).

---

# DEEP PASS — connection, constancy, texture, depth & the unnamed

## 10 · How the slides connect (narrative architecture)
The deck is not 17 independent slides — it's a **single argument** with connective machinery:

- **Visual rhyme as argument.** The *same six nodes* appear as a **chaotic network** (problem) and then re-form into an **ordered hexagonal hub** (solution). Same elements, chaos → order — the layout itself makes the pitch. Recurring diagrams are reused with changed *state*, not redrawn.
- **Leitmotifs that thread slides together.** The **icon-flow row** (industry tools on a dashed baseline → a hub node) recurs across the problem→solution run; the **hexagon (Property Wizard)** and **diamond (Vi)** badges recur wherever the system is named. These are shape-coded recurring characters.
- **Italic bronze captions = connective tissue.** Almost every analytical slide closes on an italic bronze line that *synthesises this slide and seeds the next*. They are the narration between scenes — a distinct register from the body copy.
- **The persistent frame signature** (bottom gold hatch rule + circular V mark, 12% margins, title at 7.5%) is the "binding" — it tells you every page belongs to one document, so content can change radically without the deck feeling fragmented.
- **Photographic full-bleeds bookend and breathe.** Cover and close are immersive renders; the analytical middle is white. The full-bleeds act as inhale/exhale around the dense argument.

## 11 · Reading order (within a slide)
A consistent eye-path is engineered:
- **Centered "statement" slides:** title (top) → lede (centred, measure-capped) → evidence panels → italic synthesis (bottom). Pure vertical descent.
- **Split "working" slides:** the **bleeding visual on the left** grabs first; a **literal arrow crosses the divider** pushing the eye rightward into the title+bullets — the arrow is both a reading-direction cue *and* the "translation / 2-way" metaphor (chaos left → clarity right).
- **Sequence is always made explicit:** numbered Steps, a months axis on the timeline, gold triangle bullets that point *into* the content. Order is never left to chance.
- **Alignment signals slide type:** centred = statement/breath; left-aligned = working/analytical. You can read the deck's rhythm from alignment alone.

## 12 · Constant vs variable (the system's "DNA vs expression")
- **Constant (the DNA):** 12% margins · title at 7.5% · bottom hatch+V signature · white ground · faint blueprint ghost · gold-as-accent-only discipline · triangle bullets · thin single-weight icons · soft rounded panels · the type roles · warm premium photography world · generous negative space (nothing ever crowds).
- **Variable (the expression):** layout archetype · density (low↔high) · full-bleed vs white · which diagram · which surface tints (warm vs neutral) · where on the gold→bronze→tan ramp an element sits · centred vs left alignment.
- **Subtle variation worth keeping:** the bronze of section headers drifts warm↔cool *along the ramp* by context; pill-row borders gradate across the ramp; surface warmth nudges by zone. None of it shouts.

## 13 · Texture & depth (was under-weighted first pass)
**Background textures (3, layered by opacity):**
1. **Blueprint ghost** — architectural линework, technical annotations, very faint, **top-weighted**, fading down. The "industry" substrate.
2. **Diagonal gold hatch** — as full-width **bands** behind metrics and as the **bottom baseline rule**. ~45° fine lines.
3. **Paper-fine grain / pure white** — dominant negative space.

**Depth is LAYERED and SOFT — never harsh.** A real z-stack runs through the whole deck:
`blueprint ghost → white ground → soft panels (low shadow) → cards → frosted-glass overlays → floating UI/hotspots → modal panels`.
Depth cues observed:
- **Frosted glass (glassmorphism)** — translucent blurred panels over photography (cover contact card, "More Information" action bar). Real backdrop-blur, hairline light border, soft shadow.
- **Translucent layered-panel stack** — the "user-relevant layers" idea shown as stacked semi-transparent UI panels with **coloured edge strokes receding in z**. Depth = the message.
- **Embossed number chips** — hero metrics in subtly raised/inset light boxes (inner highlight + soft drop).
- **Soft long shadows** under every card/badge — warm-tinted, low-opacity, large blur (matches `--elev-*` intent; values run softer/warmer than default).
- **Bleed & ghosting off-frame** — split visuals overflow the edges (spatial continuation); the network fades at the margins.
- **Floating affordances** — hotspot dots and the MENU pill sit *above* the photo plane with their own small shadow.

**Image / diagram / icon texture:**
- **Photography** is a defined art-direction world, not stock: warm coastal-luxury interiors, floor-to-ceiling glass, ocean light, neutral cream/taupe/timber with **sage plant** + occasional **rust/terracotta** accents (the coral in the palette). Rounded organic furniture — the UI's rounded geometry **rhymes with the furniture** (material harmony between interface and imagery).
- **Caption-over-image** = dark bottom gradient scrim + white text.
- **Diagrams** = hairline outlined nodes, **dashed** connectors, opacity-graded depth (foreground solid, background faded), ramp-coloured rings.
- **Icons** = single thin weight, rounded caps, 24-grid, two-tone (gold accent over neutral), industry-themed.

## 14 · Previously-unnamed observations (new — broaden the lens for next folders)
- **A traffic-light STATUS system exists** in the embedded product UI: **green = approved · amber = review/pending · red = declined**. This is a real semantic colour set, *separate from brand gold* — highly relevant to the app design system, and a likely cross-folder universal.
- **The embedded product UI is itself a consistent design system:** left nav menu, top tab bar, data tables with status pills, right comment/detail panel, account icon top-right, "MENU" pill, hotspot markers, "Hide Dashboard". The decks are quietly carrying the *real app's* component vocabulary — mine these slides for app patterns, not just deck patterns.
- **Connector / "2-way" language:** a **plug icon** + **dashed bidirectional connectors** recur to encode translation/overlay/sync. A genuine connector vocabulary, not decoration.
- **Number/label pairing is a hard convention:** number always **gold + tabular-nums**, label always **small grey, to the right** (or beneath). Never varies.
- **Gold underline emphasis:** key inline phrases underlined in gold (distinct from bold-ink emphasis) — a third emphasis level.
- **Shape-coded sub-brands:** hexagon vs diamond carry meaning (engine vs assistant). Shape is semantic.
- **Trust strip:** partner logos in a muted, native-colour row — a recurring credibility pattern.
- **Everything is rounded** (pills fully round; cards ~1% radius; photos rounded) — soft geometry is a rule, not a default.
- **Negative space is non-negotiable** even at peak density — generous gaps are part of the "premium/calm" signal.
- **Two-column "compare" carries a constant grammar:** left = current/problem (warm panel), right = ours/solution (neutral or gold-touched panel), dashed connector between, italic synthesis below.

## → Added to SYSTEM-GAPS this pass
Status traffic-light set · embedded product-UI component vocabulary · frosted-glass/glassmorphism depth · translucent layered-panel z-stack · connector/plug "2-way" language · number+label convention · gold-underline emphasis · shape-coded badges · trust strip · photography art-direction spec · warm-soft shadow recalibration · z-order depth stack.

---

# THIRD PASS — the rules *between* the elements

## 15 · Micro-typography & the modular scale
- **Titles use manual *balanced* line breaks** — broken into two near-equal lines (e.g. "Property Design and Construction / is a Complex Undertaking"), never ragged or widow'd. Tight leading (~1.05). → titles want `text-wrap: balance` + tight `--lh-tight`.
- **Bullets are hanging-indented** — the gold triangle sits in the margin and wrapped lines align to the *text* start, not under the triangle. ~3%-of-width marker→text gutter.
- **Number formatting is a system:** compact suffixes (`k / M / B / T`), `+` for "or more", unit attached with a slash (`/year`, `/wk`), `x` for multiples (`91x`), `%` inline. Numbers are **gold + tabular**, trailing label **grey**, set inline ("**$430B+/year** in rework") or as a left-aligned number→label row.
- **Curly punctuation** throughout ('We've', ''Property''). Typographic quotes, not straight.
- **Modular scale (measured, % frame-height):** title ~4.6% (~50px) · section-header ~2.4% (~26px) · body/bullet ~1.8% (~20px) · caption ~1.6% (~18px) · micro-label ~1.2% (~13px). Ratio ≈ **1.25 per step, with a ~1.9 display jump** title→section.
- **Caps reserved** for tiny eyebrow/label text only; body + headings sentence case.

## 16 · Colour-role logic (the *when*, not just the *what*)
- **Ink (warm near-black):** titles + body — the "content" voice, high contrast = loud.
- **Gold (bright/primary):** numbers, triangle bullets, emphasis, interactive affordances, V mark — the "active/decision" voice. **Never body text.**
- **Bronze (ramp's warm-mid):** section headers, italic connective captions, panel titles, "What's Next?" labels — the "structural/quiet" voice, deliberately lower contrast so it recedes.
- **Contrast is itself a hierarchy tool:** connective tissue (italic bronze on white) is intentionally low-contrast; content (ink) high-contrast; numbers earn attention through *size*, not saturation. This keeps the deck calm while dense.
- **Ramp position encodes loudness:** gold→bronze→tan = loud→quiet/structural.

## 17 · Grid at finer resolution
- **Panel padding** ≈ 2.5–3% of frame width; **inter-panel gutter** ≈ 2%; cards never touch.
- **Hanging-indent gutter** (marker→text) ≈ 3%.
- **Icon-flow rows** distribute icons evenly across the full content-zone width (space-between) on a shared dashed baseline.
- **Bottom hatch rule is asymmetric** — left margin to ~60% width, then stops; V mark anchors bottom-right; account icon top-right. These four corners form an **invisible frame** on every slide.
- Split divider ~46%; crossing arrow sits on it at the content's vertical center.

## 18 · Latent motion & directional-cue vocabulary
The deck is static but **encodes its own motion** (bridge to the motion language + interactivity):
- **Directional-cue set:** up-chevron (MENU = expand), down-triangle ▼ (reveal/continue), right-arrow → (flow/translate, crossing the divider). A small consistent indicator vocabulary.
- **Affordances imply interaction:** hotspot dots → hover/click reveal; MENU pill → slide-up panel; layered translucent panels → cycle/animate-in; dashed connectors → directional flow.
- **Implied entrance order = reading order** (title → lede → panels → caption) → a natural stagger when animated. Confirms "nothing teleports": arrows + bleed/ghosting are literally things moving on/off.

## 19 · What's deliberately ABSENT (restraint rules / anti-patterns avoided)
None of these appear in 17 slides — encode as guardrails:
- No **pure black**; no **hard/dark shadows** (all soft, warm, low-opacity).
- No **gradients** except in photography; no **saturated fills** outside charts.
- No **heavy rules** — hairlines only; no **left-accent-border cards** (AI cliché); no harsh borders.
- No **drop-caps**, no **all-caps body**; **italic only** for bronze captions; **underline only** for gold emphasis.
- **No emoji**; icons functional/industry, never ornamental.

## 20 · Production-system tells & copy content-model
- **Pixel-consistent** title baseline / margins / footer across all 17 ⇒ built from a **master template**. Componentising is faithful to intent.
- One icon family, one type system, one palette — single-source discipline.
- **Copy content-model** (content-agnostic, scaffoldable):
  - **Title** = bold *claim* ("We/Our + verb" or "[Subject] is …").
  - **Lede** = 1–2 sentence centred explanation (measure-capped).
  - **Section header** = 1–3 words, bronze.
  - **Caption** = italic bronze reassurance/synthesis bridging to the next slide.
  - **Bullet** = single claim, key term bolded inline.

## 21 · Responsive fragility flags (hard cases needing explicit rules)
- **6-across metric band** → regroup 3×2 / 2×3 → 1-col; labels must not truncate.
- **2×3 gallery** → 3→2→1 col; media holds ratio.
- **Timeline / network diagrams** (absolute node positions) → %-of-container coords + connector re-routing, or a simplified mobile variant.
- **Bleeding split visual** → full-bleed media block on top when stacked.
- **Balanced 2-line titles** → re-balance per width (don't preserve the desktop break).
- **Inline number+label runs** → wrap as units, never split number from label.

### → Added to SYSTEM-GAPS (third pass)
modular type scale (1.25 + display jump) · `text-wrap:balance` titles · hanging-indent bullet · number-formatting convention · colour-role logic (ink/gold/bronze = content/active/structural) · contrast-as-hierarchy · panel-padding & gutter ratios · invisible 4-corner frame · directional-cue set · latent-motion→entrance-stagger mapping · ABSENT-list as guardrails · master-template/single-source discipline · copy content-model · responsive-fragility rule list.
