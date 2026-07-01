# GUIDE — how to run a folder analysis (for any session)

Follow this to analyse the next `ingest/` folder consistently. The first
baseline (`pitch-deck`) is done; read `pitch-deck.md` as a worked example and
`SYSTEM-GAPS.md` for what's already been found. **Do not skip the diff step** —
the whole point is separating universal rules from per-folder dialect.

## Golden rules
1. **Analysis before building.** This folder changes nothing in the design system. Synthesis happens only after a rule is confirmed across ≥2 folders.
2. **Content-agnostic.** Record the *grammar*, not the subject. Translate every domain noun to a generic role ("property" → "subject", "Virtual Hub" → "interactive panel", "$430B" → "hero metric"). The languages must apply universally.
3. **Ratios, not pixels.** Every position/size as **% of frame** (or ratio between type steps). This is what lets a native presentation ratio recompute to desktop/mobile/portrait/landscape.
4. **Subtlety is the signal.** Sample real pixels — never eyeball — for zoning/colour. Deltas of 1–3% matter and are the whole point of the zone language.

## Step-by-step

### 1. Ingest
- `local_copy_to_project` the folder's images → `_ingest/<folder>/`.
- `image_metadata` a couple to record dimensions/ratio.

### 2. Look at everything
- `view_image` every page (batch 4 per call). Note each page's role + density as you go — sequence matters as much as individual pages.

### 3. Sample real values (`run_script` + canvas)
- **Flat washes/zoning:** average an 11×11 window at fractional coords; report hex + spread. Low spread (<10) = trustworthy flat region; high spread = you hit text/an edge (discard).
- **Brand palette:** don't guess coordinates for thin elements. Instead **hue-cluster**: sample every ~7th pixel across several pages, keep chromatic pixels (sat>0.25, 0.18<lum<0.78), bin by 12° hue, report dominant buckets' average hex. This reliably extracts the gold/bronze ramp + chart palette.
- **Structure:** scan rows/columns for margins (first dark pixel in a band), dividers (darkest column), title top (first dark row). Report as %.
- (Reusable sampling/measuring snippets are in `pitch-deck`'s session — copy and adjust coords.)

### 4. Fill the template
- Copy `_TEMPLATE.md` → `analysis/<folder>.md`. Complete all 9 levels with sampled values + measured ratios. Catalogue atoms and layout archetypes. Capture the sequence/density rhythm and the responsive intent per archetype.

### 5. Diff against the system
- Tag every rule: ✅ confirms · ➕ new · ✏️ generalises · ⚠️ contradicts (vs current tokens AND vs prior folders' findings). Contradictions are the most valuable — they reveal where a "rule" was actually dialect.

### 6. Log gaps + progress
- Append confirmed, evidence-backed findings to `SYSTEM-GAPS.md` (with hexes/ratios + proposed home in the system).
- Tick the folder in `PROGRESS.md` and add a one-line session-log entry with the headline findings + recommended next folder.

### 7. Synthesise (only when ready)
- A finding graduates from `SYSTEM-GAPS.md` into the design system once confirmed across ≥2 folders. Order: **recalibrate tokens → pattern primitives → components → templates (the 13 archetypes)**. Recalibrate token *values* freely; deprecate rather than rename to avoid breaking consumers.

## Recommended folder order
`pitch-deck` ✓ → `deck1-2026` (confirm/extend baseline) → `recent-pitches` (dense 3:2 dialect — stress-tests density & ratio) → `company-info` / `presentation-15p` → `vt-*` family (print one-pagers) → `landing-mockups` (web surface) → `vi-onepager`.

## Watch for (open questions to resolve across folders)
- Does the **zoning ladder** hold at higher density (does the warm/neutral pairing stay the only semantic, or do real hues appear)?
- Is the **gold ramp** consistent, or does each deck tune it?
- Which **archetypes recur** across folders (→ strongest template candidates) vs one-offs?
- How do the **3:2 and A4 ratios** change the margin/grid ratios vs 16:9?
- The exact **display + body typefaces** (identify the families; sampling can't name them — judge by letterforms, confirm with user if needed).
