# THE FULL INTERACTIVE APPLICATION FACE — Phase A synthesis (DNA, 2026-06-16)

*Tim's directive: the first slice proved the mechanism on ONE unit (render + annotate + talk); now make EVERY Application demo into the REAL interactive thing — click an element → annotate / talk to the inbuilt AI / direct it → re-render — as ONE new project holding the whole application face. Approach: A (explore) → B (prove-on-one) → scale to 19, gated on Tim's v9 verdict. This is Phase A's structure+model synthesis (my demo-file reads + my session-history scan + recollection's recall-per-demo, incoming; the kimi era-clones go deep on the targeted sessions — lead-sequenced).*

## ★ RECOVERED INTENT (session-history scan + recollection's recall)
- recollection surfaced Tim's ORIGINAL directive (exchange://104a58a7…): *"Build an INTERACTIVE standalone HTML mockup of the Company's PROPOSED MOBILE information architecture so Tim can DRIVE it."* Locked decisions: **4 tabs — BOARD / TALK / QUEUE / TUNE**, principle **"SURFACE EVERYTHING"**, aesthetic = **SCENARIO-PLAYER** (gold / warm-charcoal). ← the application's IA + the drive-it intent, recovered.
- The face = the Gallery (DNA's look entirely). Two mechanisms: the visual interface surface + the embedded-AI interaction layer (the AI sees the surface + acts live). Every screen has NATIVE desktop AND mobile (two archetypes, not one responsive). (GALLERY_AS_FACE.md.)

## THE ARCHETYPE STRUCTURE MAP (demo files read)
- **HOME** (scr-home "Morning, Keeper") — dashboard: stat-band (gold star + figures), Today/Season plates, a work-timeline of `.p-row`s (dot · title · sub · time), one gold action ("Enter Today's Cut"), the glass nav rail (house active).
- **COMPOSE** (scr-compose "Grow It from the Root") — the LADDER (root✓→role✓→frame[now]→slots→voice), archetype choices (stack/duo/trio/field, selectable), live DIALS (warmth/density/register), the SLOTS filling (checkboxes, 4 of 6), gold action ("Grow the Next Stage"), rail. ← the generative compose flow.
- **PIECE** (scr-piece "One piece, in hand") — preview with PINS on the work, take-switching pills (earlier/this-take/compare), the dials, PIN-rows (name · quote · verdict), gold action ("Pin a Note"), rail. ← the annotate+review surface.
- **CANVAS/HUB** (scr-canvas/app-canvas "the world is the screen") — immersive warm-radial ground, a frosted card carrying the words, dark-glass MENU + icon rail, HOTSPOTS ("where the world answers"), the hatch. ← the immersive field.
- **FLOW** (app-flow-full "Five Screens, One Arc") — multi-phone DECK, screens joined by the plug, warmth swinging per screen (the journey/transition logic).
- **SHEET/LEDGER** (app-sheet) — the working sheet (stat-band + plates) + the ledger (filter pills by season + dense `.row`s) — "dense where it works, gold only where it acts." ⚠️ DRIFT: uses `vars.css` + LOCAL .phone classes, not shared phone.css.
- **COMPONENTS** (app-comp-controls/cards) — ★ THE INTERACTION-VOCAB CATALOG: the gold action (rest/pressed/held), the quiet second + destructive, the DIALS, the SEARCH + segmented filter, the glass rail + MENU, the HOTSPOTS. (app-comp-cards = the card/row/chip/person/frosted components.)
- **STATES** (app-states/states-2) — empty / loading / done / error / offline (the resilience UX).
- **DASHBOARD** (scr-dashboard) — the dark analytics stage (gold data, hero figure, small multiples).

## THE INTERACTION MODEL — ONE self-build circuit across all screens
`click an element → direct (annotate / react / talk to the brain) → the brain generates/mutates → write to the addressed registry → re-render`
The primitives all exist (component bench + the first slice):
- **NAVIGATE** — the glass rail (4 stations; = Tim's BOARD/TALK/QUEUE/TUNE tabs).
- **SELECT / DRILL** — rows→piece, archetypes, pieces, constellation nodes (re-drill via address).
- **DRIVE** — the dials (warmth/density/register) live-driving the look (DNA.injectVars).
- **ACT** — the one gold action per screen.
- **ANNOTATE** — pins + the comment/reaction vocab (taxonomies.json) → write-back at the element's address (`[data-anchorable]`, proven in the first slice).
- **TALK** — the loadable CC brain bound to the element (proven: hook-1, by use).
- **COMPOSE/GENERATE** — the ladder; the AI generates content/assets to the registry (the content-half, the unbuilt rung).
- **HOTSPOTS** — "where the world answers" = the AI-answer points on imagery.

## FOR THE BUILD (Phase B = prove-on-ONE app screen, then scale to 19)
- v9 (the unit-face) is the TEMPLATE — must finish to top-tier first (overlap fix DONE; composition's editorial-VOICE transform is the remaining template-critical piece) so all 19 inherit the best pattern.
- UNIFY the 4 drift pieces (app-canvas/app-flow/app-sheet/app-states) onto shared phone.css (49-PIECES-MAP).
- Each screen becomes: the DNA-look render + the interaction layer (navigate/select/drive/act/annotate/talk) bound by ADDRESS — the same `projection:select → renderGallery → gallery:rendered → bind brain + annotate → route-back` circuit, retargeted per screen.
- PENDING: the clones' deep per-demo intent (lead-sequenced on recollection's map) · the v9 voice transform (composition) · Tim's v9 verdict (gates B).
