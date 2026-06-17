# RESEARCH — wildcard (ch-piffgfxv) · for the FULL V-SURFACE

*Research-first (Tim: "have the research done from all sides AND BEYOND"). My domain: the direction circuit / verbs / slide-format / modes. What EXISTS in vi-visual-bridge (verified in code), HOW it works, and a BEYOND lens. Verification-state honest; nothing final. Feeds the lead's assembled synthesis.*

---

## 1. MODE→COLOUR + MODE→SURFACE — THE "FIND IT" TARGET (it exists in vi-visual, verified)
Tim: "setting a mode sets the PRIMARY colour token → the WHOLE UI resolves to the active mode's colour … there's an existing DNA/composition system — FIND it." vi-visual HAS one (its own version):

- **MODE→COLOUR (server.py ~3874, verified):** `body[data-mode="X"] { --mode-primary: <hex> }` — slide_mode=#c8943a (gold), document_mode/document_channel_split=#4a90d9 (blue), graph_mode=#b85e3e (terracotta). The WHOLE UI resolves against it: `color-mix(in srgb, var(--mode-primary) N%, transparent)` throughout (borders, backgrounds, active states ~6107–6184). Set the body's data-mode → one CSS var → the whole surface re-colours. This IS Tim's mode→colour, built — at the CSS-var resolution level.
- **MODE→SURFACE (MODE_CHROME registry, @vi:mode-chrome-registry ~12699, verified):** a DECLARATIVE map `{mode → {panels:[], chrome:[]}}`; `applyModeChrome(modeName)` reads the registry, shows/hides all tracked elements. Modes: slide/document/graph/document_channel_split/waiting_slide. Mode transition = look up the row, resolve which panels+chrome are visible. This is RESOLUTION-FIRST in shape already (a registry, not scattered display toggles — the code comment says exactly that: "instead of scattered individual style.display assignments").
- **HOW it maps to the V-surface ask:** the V-as-modes-setter sets data-mode → --mode-primary resolves the colour + applyModeChrome resolves the surface composition. vi-visual's version is a hardcoded {mode→hex} + {mode→chrome-list}; the resolution-first version = those become TYPE ROWS (mode-type with a colour-token field + a surface-composition field) resolved by the one resolver. The MECHANISM exists; promoting the maps to typed rows is the compositional upgrade.
- **CONVERGENCE FLAG:** Tim said "DNA/composition system" — vi-visual's is the bridge's local one. There are likely THREE (vi-visual --mode-primary, DNA's palette/tokens, composition's palette). Union dedup: ONE mode-type registry, colour-token resolved through DNA's palette. (composition/DNA: this is your find too; mine is the bridge's proven mechanism.)

## 2. SLIDE FORMAT — decisions render as slides (my territory's deepest-built piece)
Tim: "decisions render in a SLIDE format." vi-visual's slide system IS this, built + live:
- show_slide → content (markdown string) → 15-step render pipeline → sectioned, every element addressable (the element-walker, F13c) → directive system (:::options/:::input/:::form/:::ranking/:::approval/:::multigen) → response envelope.
- ★ `:::options` directive ALREADY renders option-cards with {label, implication, recommended} + captures the pick — that IS the decision-card's options mechanism, built. A decision = a slide with an options directive + an explanation section.
- HOW it maps: decision-card archetype RESOLVES to a slide-format render; the slide pipeline is the renderer; options-directive = the option-type rows resolved. The slide format Tim wants for decisions is vi-visual's slide pipeline, resolution-promoted.
- BUILT vs needed: pipeline + directives BUILT (live); the decision-card as a resolved TYPE (not a hand-authored slide) is the compositional upgrade — the archetype reads decision-rows → emits the slide-format render.

## 3. THE V AS MODES-SETTER + SUB-SURFACES (modes-as-projections, my finding)
- The V-as-modes-setter = my genesis finding "modes are projections of one system" made the control: the V sets the mode → the same content resolves to a different projection (slide/graph/document/decision). One V, one mechanism, mode-parameterized. (= L-ONEOP/L-NOSINGLE.)
- The slot/socket + sub-surfaces/windows-nested-in-expansions: vi-visual's channel/inbox system is a partial precedent (channels = nested addressable sub-contexts); the supabase slot/socket Tim names is composition's — mine is the verbs that operate IN each sub-surface (the affordance resolves per sub-surface).
- Direction in every sub-surface = the gallery:verb envelope (already unified) dispatched per aim — one verb-grammar across all sub-surfaces/windows. That's how the V stays ONE mechanism across infinite nesting.

## 4. BEYOND (Tim: "not limited to what I specify")
- **The V-surface is the self-build surface applied to ITSELF.** If the V sets modes + modes are type rows + the surface resolves from rows, then the V can RETARGET the MAKE verb at its OWN mode-rows → Tim directs the V to add/change a mode IN the V, live (add a mode = add a row = a generate-write-back at a mode:// address). The interface builds its own modes through the same circuit. That's beyond "decision surface" — it's the surface editing the surface.
- **Decisions are one type; the chain resolves ANY type.** Once decision-card proves address→type→archetype→render→take→write-back, the SAME chain renders a code-unit, a DNA-token, a factory-archetype, a session-mind — each a type row + an archetype. The V-surface is not N surfaces; it's ONE resolver over a growing type-registry. The "whole interface by adding type rows, zero screen-code" (lead) — vi-visual's MODE_CHROME registry is a tiny proof it works (modes added as rows already).
- **Mode-colour as a SEMANTIC signal, not decoration:** mode→colour means Tim's whole visual field tells him WHICH projection he's in at a glance (recognition, not reading). Beyond: the colour could resolve from the DECISION'S state/urgency too (a pending high-stakes decision tints the field) — colour as a resolved meaning-field, not a fixed per-mode hex.

## 5. SEAMS (research-level)
- composition: the mode-type / option-type / decision-type / direction-affordance SCHEMAS (type-builder); the V slot/socket supabase; the palette the colour-token resolves through.
- DNA: archetypes (decision-card, direction-affordance), the token-merge, the mode-colour palette, slide-format look, legibility meaning-fields.
- fork: the RHM explanation resolve (address→territory_prose→brain), keystone write-back, channels integration.
- recollection: common memory under the surface (explanation context, decision history).
- projection: host the V on every page; /api/territory + /api/cognition behind.
- wildcard (me): the VERB layer (gallery:verb, resolve-from-rows), the slide-format render of decisions, the modes-as-projections mechanism, the mode→surface resolution (MODE_CHROME pattern), the take→write-back.

## VERIFICATION-STATE
§1 MODE_CHROME + --mode-primary: Observed in code (verified grep + read, server.py ~3874/~12699). §2 slide pipeline + :::options: Observed (live, used by Tim). §3-4: synthesis/BEYOND (my reasoning from the finds, [T3]). Nothing built from this doc — research only.
