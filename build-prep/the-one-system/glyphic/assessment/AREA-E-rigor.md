# AREA-E — THE SKEPTIC (adversarial rigor over the gap-map)

> Assessment E of the wide-assessment wave. Stance: **default to WRONG, find why.** Every kill carries
> Observed(file:line) / measured evidence, not vibes. Confirmed-correct is also a finding (it de-risks a
> group). A doubt I can't land on a file:line is dropped, not written.
> Written 2026-07-03 against LIVE source (design repo `/home/tim/company/design/claude-ds`, company
> `/home/tim/company`), not against the maps. Author of all principles: Tim Geldard.

**The bottom line up front.** Three of the map's load-bearing claims are stale enough to move a build
group; one is HALF stale (the correction is precision, not reversal); several minor counts drifted. The
plan's spine holds — the fusion framing is right and the frontier (the voice-corrected loop) is honestly
new — but the sequencing hides a real rewrite in the token fusion and a real product-grade wall in the
read-out register + the CDN substrate. Citizenship is achievable for the *graph nodes* this phase but NOT
for the *instrument shell* (the writer/generator are bespoke pages); forcing it now strangles the maker.
Coordination: the collision the lead feared (④'s window on glyphGraphView) is **not tonight's risk** (the
window is Tim-gated), but the shared-stack collisions (bridge routes, services.json, ledger.query) ARE live.

---

## 1 · THE MAP'S STALENESS — highest-load-bearing claims, then-vs-now

Triaged by blast radius — I verified the ~6 claims a build group's *premise* rests on, and the counts a
reader would trust. Format: **claim (map file:line) → live check → verdict.**

### 1.1 · KILL — G1's premise is ~85% already built (the biggest one)
- **Map claims** (`LIVE-INSTRUMENT.md:220`, `:461-463`): ~5 literal `'claude'` sites + **~27 caps** carrying
  `provider:'claude'` + the **~16-site AIEngine `typeof provider` guard** (always falls to claude) + the
  **foundry `window.claude` liveness check** — all listed as **live fuse material**, and **G1** (`:509-512`)
  is scoped to *build* the role-layer + `company-http` runtime from that state.
- **Live check** (`grep` over the design repo, 2026-07-03):
  - `grep "provider: *'claude'"` excluding "was provider" comments → **0 caps** (Observed).
  - Every cap now carries `role: 'text'` with an inline `/* A1: role-indirection (was provider:'claude') */`
    breadcrumb (`ai-glyphic.js:61`, `ai-capabilities-canvas.js:84,105`, `AIEngine.jsx:1245`) (Observed).
  - The role-layer EXISTS: `ROLE_PROVIDERS = { text:'claude', image:'openai-image', embed:'company' }`
    (`ai-registry.js:247`), `providerForRole`/`setRoleProvider` live (`:249-263,370`) (Observed).
  - The `company-http` runtime EXISTS and is registered: `ai-seed.js:40` (`runtime:{kind:'company-http',
    api:'/api/cognition', completeRole:'complete_text'}`), `app/services/company.js:1,77,119`
    (`HOST.registerKind('company-http', makeRuntime)`, with a real `embed(text)` → `/embed`) (Observed).
  - The foundry `window.claude` probe is GONE, replaced by registry resolution: `glyphic-foundry.html:124`
    (`no direct window.claude probe; the badge follows the binding`), `:195` (`ROUTE THROUGH THE REGISTRY`)
    (Observed).
- **Verdict:** **STALE. G1's fuse-material inventory describes a pre-A-fusion state.** The A0–A6 commits
  (89df4f3 "migrate all 41 claude-pinned caps → role:'text'", a1c1a30 "zero provider:'claude' pins remain",
  d29d3c1 "company-http runtime built", f96d6d0 "flip = one edit") DID the work the map scopes as unbuilt.
- **What actually remains of G1** (the honest residual, NOT ~27 caps): exactly **ONE pin by design** —
  `ROLE_PROVIDERS.text: 'claude'` (`ai-registry.js:247`); flip-to-Company = one edit. Two `resolveProvider('claude')`
  call-sites survive as *runtime resolution* not pins (`AIEngine.jsx:188,1311`, `RegistryInspector.jsx:467`) —
  they resolve the id, they don't hardcode a model into a cap. And the `company-http` round-trip is
  script-verified (A2 acceptance, 651ms) but **NOT proven under a live extract burst** — that's the real
  open, and it's a *different* claim than "27 caps to migrate."
- **Consequence for the plan:** G1 should be re-scoped from "build the role-layer" to "**flip the binding +
  harden the company-http path under real load**." Its blast radius is the whole extract pipeline (G3/G4
  can't run on Company-local models until the flip holds), so getting this scope right matters — building a
  role-layer that already exists is the "narrow building = failure" trap in reverse (wasted motion on solved
  ground).

### 1.2 · CORRECTED (precision, not reversal) — the layout-jump is HALF solved, G6 still needed
- **Map claims** (`:146-148`, `:454`, echoed ANCHOR:42 "stable-slot/freeze law exists, UNWIRED"): the auto
  layout **re-ranks every render → a new node changes an existing node's longest-path rank → the graph jumps**;
  "the static render does NOT solve the live incremental case."
- **Live check** (`DiagramSolver.jsx:63-115`, read in full):
  - There IS a shipped fix — **"G11 · STABLE-SLOT placement"** (`:95-110`): each node sits at a slot whose
    coord is `FIXED slot index × FIXED pitch`, "**NEVER the live count**"; the comment records the exact bug
    it killed ("the old even-spread `ci*(VB-88)/(m-1)` re-centred the whole row on every addition — **a 116px
    jump on a 320 canvas, verified**"). So **same-rank sibling re-centering is FIXED and WIRED** (Observed).
  - BUT: `rank` is **recomputed inside `layout()` on every call** via the BFS relax (`:76-89`) — nothing
    persists rank or coords across renders (Observed: `const rank = {}` rebuilt each call, no cache/ref/store).
  - The authored-freeze branch (`:68` `const authored = nodes.every(nd => nd.x!=null && nd.y!=null)`) fires
    **only when every node already has x/y** — i.e. never during unfrozen live growth (Observed).
  - `LAY_ROW_PITCH = (VB - 2*margin)/max(1, nR-1)` is **nR-dependent** (`:110`) — the `:110` comment concedes
    "nR only grows when a NEW RANK appears," i.e. **a new depth level reflows every row vertically** (Observed).
- **Verdict:** **The map's *specific* mechanism (longest-path rank change → node moves) IS STILL LIVE.** G11
  fixed a *different* jump (horizontal within-row re-centering). During a real conversation, a new edge that
  lengthens a node's longest-path still re-ranks it; a new depth level still reflows all rows. The per-node
  **freeze-x/y-across-renders incremental placer (G6's actual job) is genuinely unbuilt.**
- **Correction to ANCHOR §4:** "stable-slot/freeze exists, unwired" collapses two things — **stable-slot is
  WIRED; per-node freeze-across-renders is NOT.** Don't read this as "the placer is done." G6 stays in scope,
  but its scope narrows to *rank/coord persistence*, since within-row stability is already handled.

### 1.3 · STALE COUNTS (note, don't dwell — they don't move a group)
- **"132 symbols" / "131 faceted"** (`:336`, ANCHOR:32 "132+12", REGROUNDING:100 "132 symbols"): live
  `cv-icons.js` has **143 faceted entries** (Observed: `grep "':{domain:"` → 143). The 03f18b0 "+12
  language-family" landed (frame/block/equation/window/seed/weave/judge/ring/corpus/room/territory/operator,
  `cv-icons.js:438-449`), so the true count is 132→143 (one short of a clean +12; a prior entry may have
  merged). **Stale by ~11.**
- **"131 facets carry no name/description"** (`:128`): **STILL TRUE for the old corpus** — live count is
  **131 entries WITHOUT `name:`, 12 WITH** (Observed). Only the 12 new language-family citizens got
  name+description (they ARE full citizens per 03f18b0). So the map's claim is *precisely still accurate for
  the 131*, and the §5-violation (hand-typed tags, no derived gloss/embed index) that G2 targets holds. The
  map is NOT stale here — I checked because the git log looked like it might be, and it isn't. De-risks G2.
- **Vector count drift** (203 vs 220): REGROUNDING:100 says 203, ANCHOR:32 says 220. 03f18b0 says "203→220,
  17 new vectors." Trivia — the embedding space is live either way; note only that the docs disagree with
  each other, which is a symptom of the fast-moving-repo problem, not a load-bearing error.

### 1.4 · CONFIRMED CORRECT (de-risks the group — the skeptic working the other side)
- **"reactflow / @xyflow absent from both repos"** (`:274`): **CONFIRMED** — no `package.json` entry, no
  `node_modules/reactflow` or `node_modules/@xyflow` in claude-ds (Observed, exit=2 on both). tldraw likewise
  absent from claude-ds (Observed) — it lives in `~/company/canvas/app` per the map's own reconciliation. So
  the renderer-substrate decision (Open Decision 1) genuinely starts from "reactflow is a forward choice, not
  a fact." **De-risks that decision.**
- **"6 Company roles live"** (ANCHOR:29): **CONFIRMED** — `roles/complete_text.py`, `glyph_extract.py`,
  `glyph_compose.py`, `glyph_assist.py`, `glyph_symbol_candidates.py` all exist as role files, dated
  2026-07-02 (Observed: `ls roles/glyph_*.py`). glyph_compose (the JUDGE) and glyph_assist (the collaborative
  hand) exist NOW. **De-risks G4.**
- **G3 transcript fan-out genuinely unbuilt**: `voice.transcript` does NOT appear in `bridge.py`; but
  `/api/cognition/run_role` and `/api/cognition/embed` DO (`bridge.py:84-85`) (Observed). So G3's premise
  (the transcript rides no bus yet, but the role/embed routes exist to fan out into) is **accurate**. Correct.

---

## 2 · WHAT "FUSE THE VERSIONS" HIDES — the 3 hardest rows (where fuse = secret rewrite)

For each: the map's fusion cell, what fusing ACTUALLY costs, and **the test that does not exist** to prove
the fusion lost no semantic. The pattern of the kill: "fuse best-of-all" is cheap when the versions share a
data model and expensive-to-rewrite when they don't.

### 2.1 · tokens α/β (`fusion map row 1`, `LIVE-INSTRUMENT:292`, `THE-GENERATIVE-LANGUAGE §2 row 1`)
- **The cell:** "lift α's derived-roles MODEL into β's emit+governance; keep β's dated GOLD palette; α's
  light/green becomes a theme variant."
- **What it hides:** α (`claude-ds`) is **hand-authored CSS with NO `_system/`, no emit.py, no GENERATED
  header** (map's own `:292`, Observed the repo has no `_system/` under claude-ds). β
  (`~/company/design/_system/tokens.json → emit.py`) is the machine single-source. "Lift α's model into β"
  is therefore **not a merge — it is authoring a NEW emit stage** that generates α's `color-mix`-derived L1/L2
  roles + the `data-*` knob layer + the typed `CV_AXES` view, PLUS reconciling the **three-colour-map drift**
  the map itself flags (`:299`: `gold→accent-gold` lives in color-axis + `CV_GLYPHIC.COLOR_TOKENS` +
  `CV_MEANING` seeds — and I found a **4th** literal home: the hex short-circuit `#E0C010` at
  `cv-meaning.js:232` per `:306`). That's four homes to collapse into one emit source.
- **The missing test:** there is **no round-trip proof** that β-emitted-from-α produces byte-identical
  resolved colours to today's hand-authored α across every `data-theme`/`data-ground`/`--density` combination.
  Without it, the "lift" silently changes rendered colour on some knob combo and nobody sees it until Tim's
  eye catches a wrong warmth. **This is a rewrite wearing "fusion" clothes** — scope it as one.

### 2.2 · the conversation surface (`fusion map`, `LIVE-INSTRUMENT:251-267`, `row: molecules/ChatRail`)
- **The cell (G5):** "one surface = ViConsole act-spine + ChatRail provider/routing + ChatPanel stage cards,
  through one message-kind renderer... the three originals retire into it."
- **What it hides:** the map's OWN evidence names **two bridges — CV_AI vs WS_AI** (`:257`, `:265`
  "one bridge, not WS_AI vs CV_AI") and **three layout grammars** (`:259`: vi 3-pane · platform dashboard ·
  virtual-hub canvas-first). The tell the advisor flagged: **do the three surfaces even share a `Message`
  shape?** The map never asserts they do — it says ViConsole returns `{say,actions,proposals,options}`
  (`vi-brain.js:132`), ChatRail routes intents inline, ChatPanel has `ReadCard`/`MissingPrompt`/`ApproveCard`.
  Three DIFFERENT structured shapes. "One message-kind renderer" therefore requires **first inventing a union
  Message type none of them currently emit**, then rewriting all three to emit it. That is the load-bearing
  hidden cost.
- **The missing test:** no fixture proves a ViConsole turn, a ChatRail turn, and a ChatPanel card all render
  identically through the proposed one renderer. Until that union type is defined and tested, "the three
  retire into it" is three rewrites, not a fusion. **Honest scope: define the Message union FIRST (a typed
  citizen), test all three project onto it, THEN retire.**

### 2.3 · shapes / forms (`fusion map row 6`, `THE-GENERATIVE-LANGUAGE §2`: "octagon once", cardinality)
- **The cell:** "ONE shape grammar: form + rarity/**cardinality** (octagon once) + minting policy" — fusing
  counterpart's `shapes.json` (`shape=f(entityType)`, CARDINALITY: octagon once) with `CV_MEANING` forms
  (circle=kind, square=specific, octagon=gateway).
- **What it hides:** cardinality ("octagon appears exactly once") is a **cross-graph INVARIANT**, and there is
  **no checker that enforces it.** `CV_GLYPHGRAPH.validateGlyphgraph` validates per-node `accepts`+`CV_COND`
  (Observed via map `:104`), which is *within-node* validation — it cannot see "this octagon is the second in
  the graph." Enforcing cardinality is a **new `checker: model`-or-`predicate` class law** (per
  THE-GENERATIVE-LANGUAGE law 10) that scans the whole graph. Counterpart *declared* the rule; claude-ds has
  no mechanism for it. Fusing the two doesn't merge two implementations — **it builds the one that's missing.**
- **The missing test:** no test asserts "a graph with two octagons fails to validate." Without it, the fused
  shape grammar *claims* cardinality but doesn't hold it — a green-paint risk exactly of the kind THE STANDARD
  forbids. Scope: cardinality is a new whole-graph invariant + its checker, not a data-file merge.

**The generalization (the class):** every fusion row where the two versions **do not already share a typed
data model** is a rewrite, and the honest deliverable per row is *the test that proves the fusion lost no
semantic* — which by definition doesn't exist yet, or the versions wouldn't be divergent. The map's
"fuse best-of-all, never pick a winner" is right as *stance* and hides *cost* wherever it's written as a
table cell instead of "define the shared type, then project both onto it."

---

## 3 · THE NEXT 80% — this build's blind spot, with evidence

The last two builds' gaps were "frames without furniture" then "placed not derived." My prediction for THIS
build's blind spot, ranked by evidence strength:

### 3.1 · PRIMARY BLIND SPOT — the read-out REGISTER is engine-correct but not Tim's ear
- **Evidence (the literal rendered output, from the shipped commits + the dictionary):** the read-out
  composes from a fixed relation dictionary (`cv-meaning.js:418-432`): `'face'→'the face of'`,
  `'resolves'→'the resolution of'`, `'projection-of'→'a projection of'`, `'seeds'→'the seed of'`,
  `'part-of'→'part of'`. The actual sentences it produced (git 71de607, 03f18b0):
  > "This reader is a projection of this one. This one system is the resolution of this one. This one system
  > could be the mirror of this reader."
  > "This conversation is the seed of this structure, which is the seed of this telling, which could be the
  > way back to this conversation."
- **The kill:** these are **grammatically correct and semantically faithful, but the register is stilted and
  demonstrative-heavy** — "This X is the Rel of this Y, this Y is the Rel of this Z" is a *template read
  aloud*, not prose a person would speak. Run it against Tim's OWN gate — **"can you hear the octagon?"**
  (REGROUNDING:69): can you hear a *voice*, or do you hear a form being filled? I hear the form. The pronoun
  soup ("this one... this one... this reader") is the tell.
- **Corroborating open flag (NOT green):** `FINDINGS-LOG.md` (the sentence-coverage flag, echoed
  LIVE-INSTRUMENT:181,474): the auto-focus walk can **drop a clause from the SENTENCE though the PICTURE shows
  the relation** — flagged FORM/Tim, explicitly "not green." So the read-out has BOTH a *coverage* gap
  (misses clauses) AND a *register* gap (the clauses it does say are stilted). The map treats coverage as the
  known-open; **register is the un-named one.** G7 ("close sentence-coverage") targets coverage and is silent
  on register.
- **Why it's THE 80%:** the whole product IS "the graph speaks itself." If it speaks in fill-the-template
  voice, it fails Tim's sight/sound-recognition bar (THE STANDARD: "Tim judges by recognition") the same way
  a bare-node void failed the visual bar. **Register is the read-out's furniture.** In-scope, product-grade,
  needs Tim's ear — mark it needs-tim, never green.

### 3.2 · SECONDARY — the CDN substrate (measured, not asserted)
- **Evidence (Observed):** BOTH the reference composition `system/the-whole-thing.html:318-320` AND the writer
  `system/glyphgraph-generator.html:138-140` load, at runtime, from **unpkg.com**:
  `react@18.3.1/umd/react.development.js` + `react-dom.development.js` + `@babel/standalone@7.29.0/babel.min.js`.
- **The kill (three edges):**
  1. **`react.development.js` is the DEV build** (unminified, with warnings/checks) — never ship it as a
     product surface; it's markedly slower and larger than production react.
  2. **`@babel/standalone` transpiles JSX in the browser on every load** — this is a dev-harness pattern, not
     product grade; first paint waits on a ~2MB+ transpiler downloading and running.
  3. **External CDN = a CSP + offline wall.** LIVE-INSTRUMENT's own hard laws lean on "token-pure, **CSP-clean**,
     no external lib" as a virtue of glyphGraphView (`:272`) and `.spatial` (`:275`) — yet the *pages that
     showcase the language* violate exactly that by pulling three scripts cross-origin from unpkg. An Artifact
     or any strict-CSP host **cannot load these pages at all** (the CSP blocks unpkg), and there's no offline
     path.
- **The map never flags this.** It celebrates the-whole-thing.html as "the live-engine composition reference"
  (ANCHOR:33) and the generator as the writer, without noting they're built on a dev-CDN scaffold that can't
  ship. **Honest finding: these are demo harnesses, and productizing the instrument means a real build step
  (bundled, minified, self-contained) — that's unscoped work, and it's the "placed not derived" pattern
  recurring as "prototyped not productized."** (I did not get a live load-time number — no browser session
  this run — so I state the substrate facts as Observed and the perf claim as Inferred from the dev-build +
  browser-babel pattern, not measured. If a number is wanted, load :5174 and read the network panel.)

### 3.3 · TERTIARY (named, lower confidence)
- **Embedding-margin trust:** the map makes top-k+judge law (thin margins), and glyph_compose is the judge
  role — but I found **no measured margin distribution** over the 143-symbol space. "The judge catches thin
  margins" is untested against real utterances. Worth a measured pass before trusting generate-on-miss
  thresholds (G2's "tuned not guessed threshold" — tuned against WHAT data?).
- **One-brain latency under live conversation:** the map is honest here (`:459`: knee collapses to ~1-5
  mid-deep-reply, burst-at-pause). This is *stated*, so not a blind spot — but it's also **unverified under a
  real voice reply + extract burst simultaneously**; the "burst-at-pause" operating point is a design
  assertion, not a measurement. Flag as prove-by-use, not settled.
- **132→143 symbol library vs a real domain's vocabulary breadth:** 143 symbols is a STARTER lexicon
  (the memory itself says "grows in use"). A real property-sale domain (buyers, offers, cooling-off,
  settlement, easements...) will miss constantly → generate-on-miss fires constantly → the foundry becomes the
  hot path, not the edge case. The map treats generate-on-miss as an edge trigger; at real domain breadth it's
  the main loop. Not a kill, but a scope-reframe: the foundry must be product-grade, not a fallback.

---

## 4 · CITIZENSHIP'S COST — achievable this phase, or honest sequencing?

**The finding: full citizenship is achievable for the graph NODES this phase, and NOT for the instrument
SHELL — and forcing the shell strangles the maker (law §1.13).**

- **Achievable now (the nodes):** a glyphgraph node already CAN be a full citizen — it's addressed
  (`glyph://symbol/<id>` + `glyph://field/<facet>/<value>`, A3), typed (`kind.graph` is a declared Type,
  `glyphic-type.js` sockets), derived (composed via `CV_AXES`, not placed), two-way (the read-out says it AND
  glyph_assist takes correction — A6 verified: "make these blocked"→set_state). The node-level citizenship
  bar is real and mostly met. **Push here.**
- **NOT achievable this phase, and shouldn't be forced (the shell):** the writer
  (`system/glyphgraph-generator.html`) and the-whole-thing.html are **bespoke HTML pages on a dev-CDN
  scaffold** (§3.2), NOT composed from the 11 token-clean React components, NOT in the gallery, NOT `@dsCard`'d
  as self-projecting citizens (REGROUNDING:113,115 already concedes "the generator is an orphan page"). To make
  the *shell* a full citizen this phase means: rebuild it from `components/` + place it in the gallery +
  productize the CDN substrate + make it a self-describing @dsCard — a large front-end build that is
  **orthogonal to proving the pipeline works.**
- **Why forcing it strangles the maker (law §1.13, "over-tokenize and you strangle the maker"; law §1.17,
  "never fix by subtraction"):** the shell is the *instance* (this particular writer page), the pipeline is
  the *identity* (the LISTEN→...→NARRATE→LOOP grammar). Law §1.13's split — "identity resolves; instance is
  authored" — says the instance page is legitimately *authored*, and demanding it resolve from the registry
  before the identity is proven inverts the order. You'd spend the phase gallery-fitting a page whose
  underlying loop isn't yet verified end-to-end.
- **Honest sequencing (the "yes, but actually"):** name the shell as **deliberately non-citizen this phase**,
  with the reason recorded (identity-before-instance; the loop must prove out on a working harness first), and
  put "shell → full citizen (rebuilt from components, gallered, @dsCard'd, CDN productized)" as a NAMED later
  phase — NOT a silent gap, NOT green-painted as done. This is the difference between honest sequencing and
  the "narrow building" failure: narrow = *ignoring* the shell; honest = *naming* it out-of-phase with a
  reason. The one thing that would be a real failure is shipping the bespoke CDN page AS the product and
  calling it integrated.

---

## 5 · COORDINATION RISK — the concrete collision surfaces

The lead named three risks (④'s window · ledger L9-L11 · shared stack). I resolved WHERE each actually bites.

### 5.1 · ④'s window is NOT tonight's collision (the lead's fear, refined not dismissed)
- **The lead's premise:** "④ builds the window on the same stack tonight; both touch what I depend on
  [glyphGraphView]."
- **Live check:** ④'s window is **L8**, and `COMPLETION-CRITERIA.md:65` states L8 is **"gated on L1–L7 green +
  Tim's go."** THE-CONTAINER.md:74 (Tim, 2026-07-02): *"the window arrives WHOLE... built once, on proven
  ground, to the FORM bar, **not iterated in front of him**... no slice-first."* ④'s LAST 7 commits are all
  **L2–L7 substrate** (principal table, ladder slot-kind, historical pour — Observed via git log), **zero
  L8/window**. ANCHOR:42 itself says ④ is "loop-**prepping** the WINDOW in parallel" — prep, not build.
- **Verdict:** **the glyphGraphView collision is not live tonight** — the window BUILD hasn't started and is
  Tim-gated. The lead's instinct (both sessions converge on the render surface) is *correct as a future risk*;
  it's just not this-session's. **Do NOT treat glyphGraphView as contested tonight.** But: when L8 fires, ④'s
  window and my G6 canvas WILL both project the one CVGraph IR onto a render surface — so the non-colliding
  requirement is that **whoever touches glyphGraphView first records the shared render contract on the board**,
  and G6's incremental placer serializes frozen x/y back to the SAME IR L8 reads. Name it now, collide never.

### 5.2 · Ledger L9-L11 — the real dependency is L11 QUERY, and it's clean IF I stay additive
- **Live check** (THE-CONTAINER.md:53-55, "Lanes owned by the ledger/substrate session ch-5wog4hmx"):
  - **L9 SUPERSESSION** = `ledger.interpretation` + `assertion` + `unit_latest`/`edge_unified` views;
    **migrations 0014–0016 reserved** for that session; numbering = next-free-at-write, **board-announced**.
  - **L10 JOBS** = `intent://` records, marks-lifecycle — no embedding surface.
  - **L11 QUERY** = `ledger.query(spec jsonb)`, "one fn both faces," and explicitly **"L8's biggest consumer."**
- **The collision surface (concrete):** my scope writes glyph_meaning as **additive rows in
  `ledger.embedding`** (a DIFFERENT table from L9's `ledger.interpretation`) — so on the SCHEMA I don't
  collide (I touch no `ledger` schema/migrations; §8 of REGROUNDING binds me to additive-only). **BUT L11
  QUERY is the shared read surface:** if the window (L8) consumes `ledger.query` and my glyph/meaning
  vectors are meant to be visible through that same window, then **the query spec is a shared contract** — I
  must NOT invent a parallel query path over `ledger.embedding`; I feed INTO / read THROUGH L11's `ledger.query`.
- **Non-colliding split requires:** (a) I never author migrations in the 0014–0016 range (reserved); if I need
  a migration, next-free + board-announce (the stated rule). (b) My glyph_meaning ingest stays additive rows,
  no schema change. (c) Any query I need over the vectors goes through L11's `ledger.query` contract, not a
  glyph-specific side path (one-resolver law). (d) I coordinate the query spec on `ch-5wog4hmx` (the ledger
  thread) before assuming a shape.

### 5.3 · Shared stack — the collisions that ARE live tonight (file-level)
These bite regardless of the window, because G1/G3/G9 all touch the running services:
- **`runtime/bridge.py` routes** — G1's `company-http` hits `/api/cognition/run_role` + `/embed` (**both already
  exist**, `bridge.py:84-85` — so G1 ADDS no route, it USES existing ones: low collision). G3's transcript
  fan-out needs a NEW emit at the STT-return point (`voice.transcript` — **absent today**, Observed). **Named
  owner needed per new route;** G3's new emit is the only genuinely-new bridge surface, so G3 owns it, announces it.
- **`ops/services.json`** (Observed at `ops/services.json`) — G9's `glyphgraph` combo (`extends: interaction`)
  edits the SAME file ④/loadout work touches for its combos. **This is a real file-level collision.**
  Non-colliding requires: G9 appends a combo, never edits an existing one; ideally the combo edit is a single
  additive block announced on the board before write (the loadout/④ sessions read this file).
- **`modes/glyphgraph.py`** — **absent today** (Observed: no `modes/glyphgraph.py` anywhere). New file,
  file-disjoint, no collision — clean to create.
- **`ledger.embedding`** — additive rows only (§5.2), no schema, no collision if the rule holds.

**The non-colliding split in one line:** additive-only on `ledger.embedding`; read through L11's `ledger.query`
never a side path; file-disjoint new files (`modes/glyphgraph.py`, `roles/glyph_*.py`); the ONLY shared-file
edits are `ops/services.json` (append a combo, board-announce) and bridge's new `voice.transcript` emit (G3
owns, announce) — and migrations only next-free + board-announced, never 0014–0016.

---

## Appendix · Evidence ledger (what I verified vs inferred vs stated)
- **Observed (grep/read of live source, 2026-07-03):** 0 pinned caps + ROLE_PROVIDERS + company-http built
  (§1.1); G11 stable-slot wired + rank recomputed-per-call + freeze-branch-never-fires-mid-growth (§1.2); 143
  symbols / 131-without-name / 12-with (§1.3); reactflow+tldraw absent from claude-ds, 6 role files exist,
  voice.transcript absent + run_role/embed present (§1.4); the read-out dictionary + CDN dev-scaffold in both
  showcase pages (§3); L8 Tim-gated + ④'s commits all L2-L7 + L9-L11 ownership/reserved-migrations (§5);
  services.json path + modes/glyphgraph.py absent (§5.3).
- **Inferred (labelled as such):** the CDN perf cost (dev-build + browser-babel → slow first paint) — stated
  from the pattern, NOT measured (no browser this run); embedding-margin fragility (no measured distribution).
- **Stated by others, unverified by me:** the company-http round-trip latency (651ms, A2 commit) and the
  burst-at-pause operating point — script-verified per the commits, but not proven under a live simultaneous
  voice-reply + extract-burst; flagged prove-by-use, not settled.
- **What a browser session would add next:** a real load-time number on the-whole-thing.html + a CSP-load test
  (§3.2), and a measured read-out register judgment against Tim's ear (§3.1) — both need Tim's eye/ear, marked
  needs-tim, never green.
