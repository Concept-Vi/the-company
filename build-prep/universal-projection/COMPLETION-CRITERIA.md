# Universal Projection — Completion Criteria

**Originated by Tim Geldard; all derived work attributed to him.** A truth-table for the
instrument→ability buildout — each item a verifiable statement about the system, not a task. Built on
RESEARCH-SYNTHESIS.md; HOW lives in IMPLEMENTATION-GUIDE.md.

## Verification rules (the loop follows exactly what's written here)

**FUNCTION bar:** verified BY USE — run it, curl it, drive it in the browser. Never by reading code,
never by a DOM/JS query alone, never "the code looks right." The instrument's invariants verify
against the COMMITTED acceptance suite (Group 1) — NOT `tests/projections_acceptance.py`, which tests
the unrelated LENS registry (the name collision; see synthesis Round 4).

**FORM bar (the design rubric, run on every operator-facing surface by a SEPARATE design-critic, not
the implementer):** built on the design system's components (`components/kit.tsx`) + corpus tokens
(`design/design-system.css`), NO hardcoded values, NO bespoke one-offs · no overlaps · responsive at
desktop AND 390×844 · consistent scale/type/spacing · settings consolidated · a navigable
visual/spatial surface, not a text-wall · empty/loading/error states · the outcome demonstrable.
Machine-gated by `design/_system/check.py` (design-lint) against BOTH the .tsx AND app.css. THE ONE
EXCEPTION: the per-point hue = angle (colour IS geometry) is a deliberate non-token colour — preserve
it; it is not a lint target.

**Status:** ✅ verified-by-use · 🟡 designed/stubbed (intent, not fact) · 🔴 broken/absent.
**The floor (CORRECTED by Tim 2026-06-15):** the instrument **AUTHORS** — it is NOT read-only. Tim: *"everything
in it is variables, nothing static, it absolutely definitely needs to author… the data is loadable + filterable…
the consent fixation didn't come from me."* The old "PURE READ" line was a misencoding of "everything is a
VARIABLE" (= everything authorable, the opposite of static). The real floor: (a) *reading never silently mutates*
(authoring is an explicit verb, never a side-effect of viewing — "no surprise writes", NOT "no writes"); (b) the
instrument never fires autonomous self-modifying BUILDS (`claude -p`/acceptEdits — the autonomous-spawn law,
about build-dispatch, not data-authoring); safety for writes = git-revert, not consent-gating. The lens/projection
*computations below* remain pure functions; the instrument *around* them loads/embeds/overrides/stores/filters.
See [[feedback-instrument-authors-not-readonly]] + build-prep/embedder-pplx/INSTRUMENT-DUAL-INTERFACE-AND-LAYERS.md §5.
**Registry-is-truth:** lenses/bindings/sectors are declared rows, never hardcoded ("no first binding
ruins the system"). **Expand-before-harden:** the brain docs are captured design, NOT ratified.

---

## SPACE IS A VARIABLE + FABRIC SEAM — ✅ 2026-06-16 (caught verifying the recall→project() seam)

The fleet (lead `ch-al7jdfdr` + recollection/fork/composition) is building the **recall→project()→resolve()**
spine — recollection MOVES an address, my project() RENDERS it. Verifying my side against the live MCP door
surfaced a real **parametric gap**: `_semantic_projection` + `_separator_projection` IGNORED `?space=` (used
only the binding's declared default — topics), while nucleation honored it. A lens locked to a static
binding-space violates "nothing static, everything is a variable" AND capped the seam (an address could only
render in topics). FIXED (`1dbb201`): both honor `space = q.get("space") or binding.get("space")` (absent →
binding, byte-identical) + the `binding.space` echo now reports the ACTIVE space. Verified live: semantic
`space=repo` renders repo (was topics); acceptance multilayer 25 (+3 space-as-variable). So `project(space=,
center=<contracts.address>)` renders any address in ANY embedded space — the recall→project() handoff is
seam-ready (verified my side; integration Q to recollection: what address grammar navigate() emits). Tim made
the lead's channel authorizations carry his authority (2026-06-16, fleet-wide) — [[feedback-channel-relayed-is-proposal]].
- **SEAM RESOLVED + SPACE REGISTERED (✅ `6648660`):** recollection (Index Chief) chose Option A (publish into
  a company space, reuse-don't-parallel) and named it. Registered `projections/common_knowledge.py` (embeds:True,
  level=meaning, produced_by=code, pplx/dim-2560) — the home recollection's comprehended-knowledge index
  publishes into (`projection="common_knowledge"`), that `project(space=common_knowledge, center=<addr>)`
  renders as the overlord interface's field. projections_acceptance 35. Exact publish contract pinned to recollection. Per the INTERFACE
  BRIEF (2026-06-16, Tim-direct): projection is the SEED the front interface extends from — the Instrument's
  tri-form-factor project()→resolve() surface = the overlord render-field; my brief contribution at `3ade584`.
  - **RENDER PROOF ✅ CLOSED + VERIFIED-BY-USE 2026-06-16 (`d53a38e`):** recollection's pilot PUBLISHED (102
    pplx units, dim 2560, `backfill.ts` semantically verified by them). The recall→project()→resolve() spine is
    DEMONSTRATED live through the MCP `project` door: `project(space=common_knowledge,
    center=code:///home/tim/recollection/test/sync.test.ts, emb=pplx)` → centre **r=0.0** (self), nearest
    `sync-error-sentinel.test.ts` **r=0.06**, farthest `version-consistency.test.ts` **r=1.0**. Radius = cosine
    meaning-distance over the comprehended index. Layer discipline proven: common_knowledge is pplx-ONLY → the
    centre must be `emb=pplx`; a wrong-layer/wrong-address centre **fails loud** (no silent fallback) — verified
    both the success and the fail-loud. No longer "honest-empty / pending its data" — the circuit is closed.
- **FIRST_SLICE seam 3 — the DRILL-IN HANDOFF ✅ BUILT + verified live (`7852acb`):** the build-HOLD was lifted
  for the first slice (Tim "scope it"); my assigned seam = wheel-point → the gallery render of that addressed
  unit. Built the projection-side (engine, not look — the look is DNA's): selecting a wheel-point emits the
  unit's contracts.address on a transport-neutral `projection:select` window event {address, source, record,
  seq, kind, space} + a `drillAddress` in SurfaceState. Consumers (DNA gallery render · fork loadable-brain)
  hook it; we meet at the address. Verified live BOTH viewports (1440×900 → code://contracts/resolver.py,
  390/portrait → code://ops/cli/serveconfig.py; null on address-less points — fail-honest). design-lint 0
  literals. Reversible transport (simple-consent). The full overlord-surface assembly stays held (finding phase).
  - **ADDRESS-FIELD BUG FIXED + VERIFIED END-TO-END 2026-06-16 (`4f1b50c`):** caught verifying the lead's keystone
    (renderGallery resolves THROUGH `resolve_address`). The `address` field was source-FIRST → for corpus points
    that is the `code://` source, which `resolve_address` **fails loud** on ('scheme code not content-resolvable
    yet') → would have BROKEN DNA's renderGallery at my seam. The resolvable `run://` record was misfiled into
    `record`. FIX: `address` = `selected.address || selected.source` (run:// record first → resolve_address reads
    it today); `source` kept as the canonical `code://·board://` unit address (fork's brain target + wildcard's
    route-back mutation-at-address). VERIFIED LIVE (not code-looks-right): clicked a real wheel-point in the
    semantic 'topics' view → emitted `address=run://corpus/company/code://ops/cli/serveconfig.py/topics` →
    `inspect_address` resolves it to `{output:[topics...], source_address}`. click→emit→resolve proven end-to-end;
    typecheck clean; no other consumer (DNA hadn't built renderGallery). Corrected seam contract handed to DNA+lead.
  - **SPACE AXIS NOW DRIVABLE — SpaceChip + visual first-slice path VERIFIED 2026-06-16 (`f28afee`):** caught via
    advisor before holding — the Instrument could only reach each binding's DEFAULT space; no operator control
    drove the wheel to common_knowledge (the backend honored `space`, the frontend lacked the chip). That blocked
    "Tim can drive the first slice visually" = THE BAR. Built `toggles/SpaceChip.tsx` (registry-true, reads
    /api/layers — common_knowledge appears with zero hardcoding; shows only when the lens self-reports
    `binding.space`, hidden on raw/time-of-day). Wired `space` state (clears cross-space-stale centre/selected/
    poles) into the query + all 3 layouts. VERIFIED LIVE end-to-end: SpaceChip→common_knowledge → wheel
    re-projects to 112 units → click → emit `run://…/src/sync.ts/common_knowledge` → `inspect_address` resolves
    to `{output.digest:'core synchronization logic…'}`. Drive→drill→content proven. FORM ✅ all 3 form factors
    (Desktop bar-left; Portrait chips wrap clean 2 rows, no orphan; Landscape rail vertical stack). The universal
    projection now points at ANY embedded space from the operator's seat — the visual first-slice entry is real.
  - **DOM-MOUNT SEAM ✅ BUILT + VERIFIED-BY-USE 2026-06-16 (`0507e64`) — the first-slice RENDER half is live:**
    the lead/DNA/fork converged ask (the one same-page blocker). projection owns surface/app, so projection
    HOSTS DNA's gallery render at a stable container. Architecture (copy-on-build, advisor-blessed):
    `scripts/sync-gallery.mjs` copies DNA's `unit-view.js`+`phone.css` → `public/gallery/` on predev/prebuild
    (DNA stays OWNER; dev==prod; FAILS LOUD if her repo absent; gitignored — no committed stale snapshot;
    proven by re-syncing over her live edit). `index.html` loads the module as a CLASSIC script (window.DNA
    ready pre-React → no StrictMode double-bind). `GalleryMount.tsx` = a stable `<div id=gallery-mount>` React
    never reconciles (DNA's innerHTML + fork/wildcard element refs stay valid), binds the drill ONCE (guarded).
    DNA's relative `/api/cognition/corpus` fetch is now SAME-ORIGIN (surface proxies /api → :8770 — the CORS
    block is gone). COHERENCE (FORM): the FACE is a drill-in modal (scrim+dismiss+Esc); App owns `galleryOpen`
    so all 3 layouts SUPPRESS the redundant Disclosure inspector → ONE drilled-unit surface, not two competing.
    VERIFIED BY USE both viewports: Desktop 1440×900 (drive→click→DNA renders the real unit's digest in
    #gallery-mount→overlay opens→Disclosure suppressed) + Mobile 390×844 TRUE (face edge-to-edge, no clip —
    fixed the 390-screen-in-358-frame squeeze). design-lint 0/0; instrument acceptance 91/0. SCOPE: this is the
    RENDER half (drive→select→render, same-origin, stable container). The talk-to-brain (fork) + annotate
    (wildcard) halves attach to the hosted element via `gallery:rendered` — THEIR pieces; not marked done here.
  - **FACE FORM-CLEAN — design-critic fixes + token-starvation seam ✅ 2026-06-16 (`02813c1`):** a SEPARATE
    design-critic on whole-screen screenshots (no green-paint) found real FORM defects in MY overlay — all fixed:
    (1) HEADER COLLISION (desktop, load-bearing) — the centred card's top band overlapped the global header
    (DNA's "9:41" punched through "default"); a scrim can't fix a spatial collision over dark text, so
    GalleryMount toggles `body.gallery-modal-open` and CSS RECEDES the competing chrome (.bar/.strata/.rail/
    .legend/.scrubber) when the FACE is open — the wheel stays dimmed for drill-from context. (2) SCRIM 30%→54%
    + chrome-recede → the single drilled-unit surface. (3) ✕ moved to MODAL level (overlay top-right, clears the
    card + DNA's sbar); overlay z 45→60 above all chrome. (4) ★ TOKEN-STARVATION (DNA's diagnosis): phone.css is
    token-based but its `--dna-*` :root tokens live in piece.css (which carries a global *-reset + body rule —
    unsafe to load whole), so the host was starving the render → it looked flat (collapsed padding, run-together
    chips, no warm ground). FIX: sync-gallery.mjs EXTRACTS ONLY piece.css's :root → dna-tokens.css (no globals),
    loaded before phone.css → DNA's real immersive face renders (warm ground, frosted card, gold pill, spaced
    glass pills, address bar, hatch). VERIFIED BY USE both viewports (Desktop 1440×900 + Mobile 390×844 true);
    design-lint 0/0; instrument 91/0. Render half is now FORM-clean. (DNA's content look — the immersive
    typography/imagery — is being raised through her own adversarial FORM critique loop; separate from this mount.)
  - **LANE-B TALK ROUND-TRIP ✅ FUNCTION VERIFIED-BY-USE BOTH VIEWPORTS 2026-06-16 — the loadable-brain (fork)**
    **half attaches; the annotate (wildcard) half is mounted-but-blocked on a DNA contract (honest split):** the
    two fork-authored bridge diffs + the hook mount the prior entry deferred to "THEIR pieces" are now landed and
    DRIVEN. (a) `runtime/bridge.py` `_claude_stream` context composer: ui://-only `SUITE.address_help` →
    scheme-agnostic `territory_prose`. PROVEN DETERMINISTICALLY (run_turn-independent, both vs the old composer on
    4 real addresses): a run:// drill target went `"help bundle unavailable: ValueError"` (151ch, useless) →
    **1309ch of real content** (kind + run.record + digest); code:// likewise; ui:// is a strict SUPERSET (693→
    1445ch); a bad address NEVER raises (degrade-clean preserved). (b) NEW `POST /api/territory/write` →
    `territory_write`→`suite.mark`: PROVEN by HTTP round-trip (`{ok,written:2,marks:[…]}` — comment/reaction/favour
    persist + read back via `marks_for`) AND fail-loud (a typeless item → **HTTP 400**, not a silent swallow).
    py_compile + bridge_routes_acceptance (the drift teeth) both green; the bridge restart was announced on the
    fabric first (~10s :8770 blip); /api/projection + /api/territory/write + /api/claude/turn all health-checked
    post-restart (lazy imports surface at request-time — hit, not assumed). (c) THE HOOK MOUNT: `sync-gallery.mjs`
    now copies fork-gallery-brain-hooks.js + wildcard-gallery-binder.js into public/gallery/ (same copy-on-build
    discipline; owners hold the build-prep/ source) + index.html loads them as classic IIFEs — they were AUTHORED
    BUT UNMOUNTED (nothing loaded them; the silent no-op the advisor flagged). (d) BY-USE caught a REAL fork bug
    (no green-paint): the brain button didn't appear → console `TypeError: …reading 'brainBound'` → fork's
    gallery:rendered listener read `d.root || document` but DNA's CONFIRMED emit is `{element,…}` (wildcard already
    adapted; fork hadn't), so it bound to `document` (no `.dataset`) and crashed. FIXED: bind at `d.element || d.root`,
    element-guard, never `document`. (e) **hook-1 (loadable brain / talk leg) VERIFIED BY USE:** Desktop 1440×900 —
    drove Meaning→common_knowledge→clicked a wheel-point → DNA rendered the CHANGELOG.md unit → "Ask Claude Code
    about this" bound to the unit root → clicked → typed → `POST /api/claude/turn` streamed a **content-correct**
    answer ("a comprehended capture of the CHANGELOG.md from your 'recollection' project … sync workers, MCP plugin
    support, recall skills") into the panel (num_turns=1, no tools — proving territory_prose fed the unit's real
    content; before the diff this address gave "unavailable" → the brain had nothing). Mobile 390×844 — same drill,
    brain-ask binds, overlay edge-to-edge (x:0 w:390), 0 console errors. **SCOPE (lead's framing — NOT form-done):**
    this proves the TECHNICAL layer only. fork's brain panel is UNSKINNED (`.brain-ask/.brain-panel/.brain-reply`
    are DNA's RE-SKIN, pending) — FUNCTION ✅, FORM is DNA's parallel raise. The sbar (9:41) was NOT suppressed
    (DNA holds that call; the lead's "it goes" was conditioned on her confirm, which she declined). **hook-2
    route-back — fork's WIRE ✅ by-use; wildcard's SELECTOR → DNA contract 🔴 (the precise split):** the write
    BACKEND is proven (HTTP round-trip + 400). fork's HOOK 2 BROWSER wire is ALSO proven by-use — a synthetic
    `gallery:direction` (bypassing wildcard's selector) → batched → `POST /api/territory/write` HTTP **200** →
    `gallery:rerender` emitted, no write-error (verified in-browser after the advisor flagged HOOK 2 was
    authored-but-unexercised in exactly the state HOOK 1 was when it crashed — symmetric-risk caught, not shipped
    blind). 🔴 The ONE remaining gap is wildcard's binder SELECTOR: it bound 0 strips by-use because it targets
    semantic HTML (`p,h1..h6,li,…`) while DNA renders pure divs (`.screen.uv > .uv-words > .p-frost`,
    anchorableCount=0). Needs the DNA↔wildcard anchorable contract: DNA tags blocks `[data-anchorable]` (already in
    wildcard's selector — drop-in) OR wildcard adds DNA's content-block classes. SURFACED to fork/wildcard/DNA with
    evidence — not guessed at DNA's markup (her render is hers).
  - **HOST-SYNC organisms.js + hook-2 annotate CLOSED + constellation DATA-PATH live 2026-06-16 (`11d64bd` + peer**
    **`ff98143` + my restart):** the in-host first-slice FACE advanced on three fronts. (a) **organisms.js HOSTED**
    (my `11d64bd`): DNA's renderUnit now calls `DNA.org.hubNetwork` (the unit→neighbour constellation), so
    sync-gallery.mjs copies `organisms.js` into public/gallery/ + index.html loads it BEFORE unit-view.js (DNA's
    host-wiring note). Pure generator module, 0 global side-effects → safe as a classic script (verified:
    `window.DNA.org.hubNetwork === function` in-host). (b) **hook-2 annotate write-back ✅ CLOSED BY-USE** — the
    prior entry's 🔴 wildcard-selector gap is RESOLVED: DNA tagged content blocks `[data-anchorable]` (+ data-address)
    + wildcard committed a rot-proof 3-tier selector; my re-sync picked up DNA's updated unit-view.js → drill
    CHANGELOG.md → wildcard binds **3 annotation strips (0→N)** → clicked a `good` reaction → `gallery:direction` at
    the unit sub-address → `POST /api/territory/write` **[200]** → `gallery:rerender`, no write-error. The full
    first-slice round-trip (talk + annotate) is closed in-browser; hook-1 brain still binds (no regression); 0
    console errors. (c) **constellation DATA-PATH live** — `GET /api/cognition/neighbours` (peer `ff98143`, HTTP twin
    of MCP corpus op='neighbours', reuses `runtime/corpus_neighbours`) brought online by my bridge restart (it 404'd
    pre-restart). Curl + same-origin browser fetch both 200: harness.ts → **5 real neighbours** (index.ts 0.75 …
    extractor 0.55 — the distill-module constellation), shape `{source,score}`. ★ ADDRESS CONTRACT probed
    deterministically (advisor's blocking item — wrong form = silent-empty constellation): the **code:// SOURCE**
    address has the vector; the run:// record form returns honest-EMPTY. Coverage 60/60 sampled common_knowledge
    units have neighbours (CHANGELOG.md is a rare unembedded anomaly → degrade-clean card-only). 🔴 **OPEN — the
    constellation RENDER** is DNA's last half: renderGallery fetches only `/api/cognition/corpus`; it needs a parallel
    `/api/cognition/neighbours` fetch (keyed on `opts.source` = code://) to set `unit.neighbours` → hubNetwork draws.
    Exact contract (URL + the code:// address-form gotcha + {source,score} shape) SURFACED to DNA; her file, not
    clobbered (actively raised). Once she wires it + re-syncs, the constellation renders in-host = full first-slice FORM.
  - **CONSTELLATION RENDERS LIVE IN-HOST ✅ VERIFIED BY USE BOTH VIEWPORTS 2026-06-16 — the prior 🔴 closed; the**
    **first-slice FACE is FUNCTION-complete in-host (FORM polish is DNA's/composition's):** DNA wired renderGallery's
    neighbours fetch (`?address=<opts.source code://>` — the code:// gotcha handled) + a `neighboursToNodes` mapper;
    I RE-SYNCED her updated unit-view.js (9069→11145B) into public/gallery/ and verified IN THE HOST (not on DNA's
    stub). Drilled an embedded unit (`backfill.ts`) at 1440 AND 390: the corpus-fetch + the **neighbours-fetch** both
    fire → the constellation SVG renders **7 REAL neighbour nodes** (backfill.test.ts 0.70 · sync.ts 0.56 · db.ts
    0.55 · integration.test 0.52 · crossings 0.51 …), labeled by **editorial ROLE** (cli/indexer/crossings/test/sync/
    db — DNA's roleOf, not filenames), score-weighted, the hub `{ }` kind-glyph at centre, each node a drillable
    code:// address; "7 linked" chip shows the count. Host frame is the correct 390px phone width (`.screen.uv` fills
    it exactly — my sizing faithful). 0 console errors both viewports; overlay edge-to-edge at 390. So the in-host
    FACE is now: real CARD + real CONSTELLATION + talk (hook-1) + annotate (hook-2) — ALL real-data, same-origin,
    drivable, interactive. The recall-under-unit lane is closed end-to-end (corpus_neighbours → MCP op 8a77a2e →
    HTTP route ff98143 → DNA's fetch → in-host render). 🟡 **FORM polish remaining (NOT mine — surfaced):** (1) on a
    long-digest unit the `.uv-words` card (h≈603) overlaps the `.uv-field` constellation (overlapX=206) — DNA's render
    LAYOUT at varying content lengths (the frame is correctly 390px; not a host bug). (2) the live render shows RAW
    editorial voice (filename title + full digest) — composition's digest→title/telegraphic-card transform pending
    (DNA noted). Both are DNA's/composition's parallel raise; the host integration + data are complete + faithful.

## PROJECTION LANE — BUILD COMPLETE (in-host) + SHIP-READY · 2026-06-16 · the two remaining gaps are Tim-INPUT-blocked

Honest stand-down status (the loop's no-churn clause: the projection lane meets THE BAR in-host; the gaps left are
not buildable without a Tim INPUT, so I note + hold rather than churn or drift into others' lanes).
- **DONE + VERIFIED (this session):** G10 (directional typed edges) + G9 (two-gravity separator) BUILD COMPLETE, re-verified
  live both viewports post-restart (211/0 acceptance battery). First-slice FACE function-complete IN-HOST: real card +
  real constellation (7 live neighbours, role-labeled, drillable) + talk (hook-1) + annotate (hook-2 round-trip 200) —
  all real-data, drivable, interactive, 0 console errors at 1440 AND 390.
- **SHIP-READY (verified this fire):** `surface/app` production build is CLEAN — `npm run build` → 459 modules, dist/
  (js 326kB/gz 104kB, css 23kB), prebuild copies DNA's render + organisms + the fabric hooks. The live instrument can
  be built+served; it had only ever run as a dev server before — now confirmed buildable.
- **DURABLE FACT for whoever sequences access (NOT a crisis-time ping):** `surface/app` is dev-only on **127.0.0.1:5174**
  — it is NOT served on the tailnet (vite `allowedHosts: ['.tail777bc2.ts.net']` is set, but allowedHosts ≠ served; a
  `tailscale serve`/proxy onto it is required to reach it from Tim's phone). This is SEPARATE from DNA's :8090 gallery
  (which IS served on the tailnet IP, cert-broken on the .ts.net URL). Serving the live instrument is a config action I
  am NOT taking unilaterally (lead owns access coordination + it needs Tim's firewall authorize; no thrash).
- 🔴 **THE BAR #3 (Tim can DRIVE it) — gap, Tim-INPUT-blocked:** Tim cannot access the surface on his phone. Root =
  the lead-owned access work (cert + the netfilter/connmark firewall fix needing **Tim's iptables-legacy authorize**).
  Outside the projection lane; SKIP + noted (the law), not churned.
- 🔴 **FULL APP-FACE scale-up (the ~19 screens) — gap, Tim-gated:** DNA-led next build; the lead gates Phase B on Tim's
  v9 verdict (itself gated on access) + holds the clone fleet. When greenlit, `surface/app` is the host (my lane) — I'm
  ready to host it then. Not front-run.
- **STANCE:** no further projection changes until the loop has real projection work — i.e. Tim's verdict greenlights the
  app-face host, OR access unblocks (so Tim can drive + judge). Standing down to avoid churn/drift, per the law.

## #1 BINARY QUANTIZATION — ✅ BUILT + VERIFIED LIVE 2026-06-15 (the REPRESENTATION axis)

Tim's 4-item program (1 BQ · 2 Postgres · 3 cron · 4 reconnect): #4 ✅ closed; #1 ✅ BUILT + FORM-passed; #3
his timer; **#2 Postgres — 🟡 BLOCKED on infra + Tim's "how" (evidence 2026-06-15):** NO Postgres server
running (only the `psql` client), NO pgvector / Python pg-driver / Supabase creds present, and 30 live
sessions are reading+writing the `FsStore` right now — a store-backend swap would endanger the running fleet,
and the cloud(Supabase)-vs-local fork is the "how" Tim reserved. Not autonomously buildable-to-THE-BAR
(needs infra provisioning + Tim's go); SKIP-not-stall. When unblocked: additive `PgStore` behind the SAME
`FsStore` interface (the one `FsStore(STORE_DIR)` injection point), one-time import, flag-flip cutover on a
quiescent fleet — the projection engine is untouched (one engine, new store). BQ = the third representation
axis beside `?emb=` (◫ layer) and `?dim=` (◎ resolution): `?quant=binary` signs each read dim to ±1 → the SAME
cosine becomes a faithful Hamming similarity (`cos(sign a, sign b) = 1 − 2·Hamming/d`), folded into the `_mrl`
seam so it composes with `?dim=`. Compute-on-read (pure-read; no stored variant — a LAW-forced call). Fidelity
proven BEFORE building (not green-paint): NN@10 binary-vs-full 0.81 (pplx 2560d) / 0.70 (BGE 1024d).
- **FUNCTION ✅** — `quant` threaded through all 3 vector handlers + echoed (`binding.quant`); verified live:
  nucleation full→1born/3cand/11sec vs binary→1born/2cand/10sec; composes with dim (binary+dim512). The
  `QuantChip ▦` (full·float / binary·Hamming) drives `?quant=binary` (network-traced), shows only on vector
  lenses. Acceptance projection_multilayer 18 (+5 BQ), instrument 91, bridge_routes 8.
- **FORM ✅** (design-critic PASS) — QuantChip mirrors LayerChip/ResChip + the useChipMenu collision seam;
  0 off-token literals; glyph family ◫/◎/▦ coherent + legible, menu collision-flip holds for the 4th chip.
  One HIGH finding (portrait binary-state widened the label → 4th chip orphaned to its own row) FIXED
  (`a690358`): portrait optics-cluster gap+padding tightened (~56px) → all 4 hold one row in the binary
  state (verified one-row at the tool's 500px floor; true-390 unrenderable by the tool but the clawback holds).
- MCP `project`/`layers` gain `quant` automatically on the next reconnect (same engine — no separate door).
- **SCOPE-HONESTY (measured 2026-06-16, overclaim corrected):** BQ delivers the binary GEOMETRY only, NOT a
  perf/size win — the impl runs ±1 FLOATS through the float cosine, so binary nucleation ≈ full (~21s). The
  "32×-compact / whole-corpus" framing was vapor for this impl; corrected in the QuantChip tooltip + HOWTO §9
  (no green-paint). The real interactive SPEED lever is the resolution picker (`?dim=128` → ~1.5s vs 21s full,
  dim=512 → ~4.6s — measured). The true 32× perf needs bit-packed vectors + popcount-Hamming (a future beat).

## G10 EDGE-COVERAGE AUDIT — 2026-06-15 (falsification: is G10 a "toy slice"? → NO, ✅ is honest)

The cron names `relation_types` + `cascade precedes` as directional-edge sources G10 must connect to. Audited
whether the Connections lens (node-type type-flow) is only a slice of the realized directional edges. Evidence
(over the LIVE store, not assumption):
- **relation_types: 5 declared directed (contradicts·depends_on·fragment_of·precedes·principle_beneath; +
  `sibling` symmetric, correctly excludable per "only directional relations type"), each with near→far + an
  `inverse` (Tim's equal-opposite) — but ZERO realized instances**: 0 of 6287 events carry a relation_type
  field; no relation/mark event kinds exist. relation_types realize as unit→unit marks ("A contradicts B"),
  none stamped yet.
- **cascades: NONE exist** (no cascade store).
- → At audit time the ONLY realized directional edges were **node-type type-flow** (Connections lens ✅) and
  **graph connect wires** (graph lens ✅). relation_types (0 realized) + cascades (0 saved) were a data-gated
  GROWTH FRONT — surfacing them then would have been green-paint over empty data.
- **UPDATE 2026-06-15 — the cascade half of the gate OPENED (✅ BUILT, `79ba937`):** the live fleet has now
  saved **6 cascades** (was 0). So `by_cascade` — "cascade precedes", the directional source the cron named —
  is BUILT with real data: reads `SUITE.list_cascades`, each cascade's ordered steps → DIRECTIONAL precedence
  edges (step i → step i+1; node = role else op-verb), registry-true, cycles-as-cycles, reusing the
  by_node_type sector+chord seam. Verified live both viewports (14 sectors + 9 edges) + acceptance (multilayer
  22, +4 guarded). G10 now connects to node-type-flow + graph + cascade-precedence.
- **relation_types — still un-buildable both ways (evidence 2026-06-15, sharpened):** (a) as realized MARKS:
  0 stamped (`relation_type` events 0/6291); (b) as DECLARED structure: too sparse — only 1/6 directed relations
  has both near+far (`contradicts: principles→principles`, a lone self-loop), the rest `far=None`; the 3 declared
  inverses (unlocks/has_fragment/follows) aren't registered relation_types (dangling). Either rendering = a
  degenerate ~empty wheel = green-paint (fails THE BAR's "real data, never a toy slice"). GATED on EITHER marks
  being stamped OR the rows gaining near+far+registered-inverses — then it lights up like cascade did. Not a G10 gap.

## RE-VERIFICATION — 2026-06-16 · BUILD COMPLETE re-confirmed (post-bridge-restart, full pass)

**2026-06-16 — G10 + G9 (the cron's literal targets) RE-VERIFIED LIVE after the front-interface beat restarted
`company-bridge.service`** (the territory_prose composer + `/api/territory/write` landed in `_claude_stream`/
do_POST — NOT in `build_projection`, so the projection engine is untouched; this pass PROVES no regression, not
"code looks right"):
- **Acceptance battery GREEN — 211 checks / 6 suites** (projection_instrument 91 · semantic 23 · scale 29 ·
  projections 35 · bridge_routes 8 · multilayer 25). Up from 198; more teeth, 0 failures.
- **G10 `by_node_type` — curl: 16 node-type sectors + 49 REAL directional typed edges (output-type→input-type),
  0 reciprocal pairs in current data (honest — cycles rendered WHEN present, never forced acyclic). LIVE both
  viewports 1440×900 + 390×844 — the directed-chord web (arrowheads = direction), coherent FORM, 0 console errors.**
- **G9 `by_separator` — curl: 162 REAL items, variable poles (worldview/conceptual ↔ sessions/runtime, real
  `cluster://topics/k8/*` refs). LIVE both viewports — two spatial basins, the `separates` fifth-gate verdict +
  47/115 balance bar, pole/space/layer/resolution pickers drivable. 0 console errors.**
- **THE BAR — MET (re-confirmed):** (1) live both viewports + curl ✓ (2) all real data — 16 node-types + 49
  edges; 162 items + real cluster poles, the whole topics space ✓ (3) drivable (lens/pole/space/layer/res/
  scrubber/centre) ✓ (4) interactive ✓. **NO CHURN** — zero code change to G10/G9 this fire (the build meets THE
  BAR; the law forbids re-building a done thing — verification only).

The 2026-06-15 deepening (prior session) extracted `bridge.build_projection` as the ONE engine under BOTH faces
— which sits beneath G10 + G9. That pass proved the refactor preserved THE BAR (not "code looks right"):
- **Acceptance battery GREEN — 198 checks / 6 suites:** projection_instrument 91 · semantic 23 · scale 29 ·
  projections 34 · bridge_routes 8 · projection_multilayer 13 (the new live-store teeth, incl. the cwd-regression guard).
- **G10 (Connections — directional typed edges) — ✅ RE-VERIFIED LIVE both viewports** (1440×900 + 390): 16
  node-type sectors, real directional type-flow chords (output-type feeds input-type), cycles rendered as cycles.
- **G9 (Two gravities — separator) — ✅ RE-VERIFIED LIVE both viewports:** variable poles (worldview/conceptual
  ← → sessions/runtime), signed lean, the `separates` fifth-gate balance bar (47/115).
- **Deepening — ✅** multi-layer · MRL-on-all-lenses · LayerChip · ResChip · optics-cluster FORM (design-critic
  PASS, all 4 findings) · MCP `layers` door (live ✓).
- **THE BAR — MET:** (1) verified live both viewports ✓ (2) all real data — 16 node-types + real edges, 162
  items + real pole regions, the whole 5994-pt event corpus, every registry ✓ (3) Tim can DRIVE (lens/layer/
  resolution/pole/scrubber/centre pickers) ✓ (4) interactive ✓.
- **MCP `project` live-verify — ✅ CLOSED 2026-06-15** (Tim reconnected the company MCP; the stdio server
  re-spawned with the fix). LIVE-verified through the tool face: `mcp__company__layers` returns `{space:{emb:dim}}`
  (the dims door); `mcp__company__project(by_nucleation, operators, repo, pplx, rung=8)` returns the TRUE keystone
  — `binding.id=by_nucleation`, all 8 bindings discovered, `emb=pplx` echoed, and the full nucleation report:
  657 items × 8 operator roles → 2 BORN candidate-operators (✦0 the `*_acceptance.py` test-cluster size 36
  margin 0.354 distinct+born = "test-verifier"; ✦2 `fabric/vram.py` infra size 30 born) + dissolution candidate.
  THE DUAL INTERFACE IS PROVEN: the agent (MCP) sees byte-identically what the operator (UI) sees. No open
  items remain reconnect-gated.

## BUILD STATUS — 2026-06-14 · BUILD COMPLETE — verified live, all real data, drivable, interactive

Groups 1–12 are all ✅, both faces, to THE BAR. The last item (#12 — the 20/80 water-law / TYPE-NUCLEATION)
is now BUILT, not gated: Tim unblocked it 2026-06-14 by giving the operational law directly ("scan content →
typed units → fall into the registry's types; what doesn't fit piles up OUTSIDE the square; past a threshold a
DISTINCT pile becomes a new type; the inverse — a type thinning below — is context-dependent, not a hard rule;
the laws underneath are the invariant; nothing is for a specific purpose — choosing one is automatic failure").
The old "Tim-gated on the forbidden-definition / the second axis" framing was MY inversion of his delegation,
now corrected. Built as a PURE READ, registry-true, NO tuned cosine floor, with the structural honesty the
fifth gate established. This IS a completion claim — see the TYPE-NUCLEATION entry under GENUINELY REMAINING.

- **THE LIVE FRONTIER (2026-06-15) — the front-end surface + the EQUATION-DESCRIPTIONS AUDIT.** The engine
  (Groups 1–12, incl. the cron's G10/G9 targets) is ✅ COMPLETE — re-verified this fire: acceptance suite
  91/91 PASS (pure read, no regression) + the ✅ markers below. Per Tim's direct 2026-06-14 corrections the
  work moved to the fresh React surface (`surface/app`, port 5174/5175) and then to expressing the SEED
  equation's full DESCRIPTIONS. That frontier is tracked in **build-prep/instrument-surface/STATUS.md** and
  **EQUATION-AUDIT.md** (the §-by-§ gap list). Done so far: all 12 lenses re-homed; gap #1 the coincidence
  spine (`ce04fcf`); gap #2 the corner reading (residue → grow the box, `ec1ba61`); signed strain (`615b66a`);
  the **selection tether** (point→detail-card on all lenses, `817a2f1`, both viewports + critic). **The
  registry-promotion KEYSTONE (§7) is PROVEN** (2026-06-15): typing real content against the 29 OPERATORS
  (roles) nucleates a defensible candidate new operator (a born `*_acceptance.py` cluster = "test-verifier"),
  validated in-process against the resident pplx embedder (no eviction); the noise pile is correctly rejected
  by the permutation null. NOT Tim-blocked (Tim: "no blocks on Tim" — the embedder/loadout is mine). The
  integrated SHIP needs operators + an items space in ONE embedding model persisted with pyramids — a real
  fork: pplx-forward (Tim's chosen embedder; the migration seed) vs BGE-restore (the corpus's current embedder
  on :8001, currently DOWN → a GPU eviction the harness guards). That fork is a dedicated migration, not a
  piecemeal loop beat. Next unblocked surface beats: axes-as-variables, edges-as-canonical-moves (engine),
  desktop framing / de-knot (polish). See STATUS.md "✅ KEYSTONE L14 — PROVEN".
- **INSTRUMENT half — ✅ COMPLETE.** Group 1 (the variable-engine floor / acceptance suite), Group 5 (the
  FORM face on the corpus design system), Group 3 (time-freed/relative centre + scrubber), Group 4
  (real-time SSE pub-sub), Group 2 (the square/dyadic-grid half). All ✅, both faces, design-critic-passed.
- **ABILITY half — ✅ COMPLETE.** Group 8 (embedding substrate live), Group 6 (the circle / semantic radius),
  Group 7 (strain / structure↔meaning gap), Group 11 (the multi-scale SCALE axis) — all ✅. Group 10 (the
  connections in the registries) — ✅ 2026-06-14 (Tim unblocked; my prior "needs an acyclic backbone" was a
  self-imposed constraint — nonsequential IS valid): the directional typed edges render as an INTERACTIVE
  directed-chord web (drive-to-explore), verified to THE BAR, critic RESOLVED both viewports. Group 9 (the
  two-gravity separator) — ✅ 2026-06-14 (Tim unblocked; general variable-two-pole read, AI supplies its own
  pole): the fifth gate + the two-basin drivable FORM (balance bar, pole-picker, reset), verified to THE BAR,
  critic PASS both viewports. Both faces each.
- **#12 — small registries + gate surface + 20/80 water-law (TYPE-NUCLEATION) — ✅ DONE (2026-06-14, both faces, to THE BAR).**
  Tim gave the law directly (it was never really Tim-gated — I'd inverted his delegation). Built as a PURE-READ
  nucleation reading: type the items of a content store against a REGISTRY OF TYPES (scale-pyramid centroids);
  membership = each type's OWN admission extent (truthful — cross-store → empty square, same-store → populated +
  outliers; NOT a tuned floor); the misfits pile up OUTSIDE the box; a pile-cluster is a CANDIDATE NEW TYPE when
  its silhouette margin (members bind to each other more than to any existing type) BEATS a permutation-null (no
  magic constant); the 20/80 DIAL is the BIRTH threshold (mass to be born), surfaced + drivable; a thinning type
  is a context-dependent dissolution candidate. See the TYPE-NUCLEATION entry under GENUINELY REMAINING.
- **GENUINELY REMAINING (all honestly gated — the loop must NOT churn on these):**
  · **Group 9** (two-gravity separator) — ✅ DONE (2026-06-14, both faces, to THE BAR). SUPERSEDED the AI-tells
    gate: Tim "there is no single purpose" → general variable-two-pole read, AI supplies its own pole. FUNCTION:
    a PURE two-pole read over the persisted vectors (no embed-lens) + the fifth gate (separation_report:
    distinctness · both spreads · ρ≠+1 · a pole must attract somebody) + the AI plants its own AI-corner anchor;
    proven live on a real NON-centroid balanced pair (worldview.py vs sessions.py: separates, ρ −0.41, 57/105).
    FORM: the two gravities as two spatial BASINS (left/right), radius=|lean|, a diverging BALANCE bar so the
    skew is seen, a pole-PICKER (drive the two gravities live); design-critic PASS at 1440×900 AND 390×844.
    Pollution instance = named DEFERRED application (lens-mismatch 162/0 → correctly refused, honest).
  · **Group 10** (the connections in the registries) — ✅ DONE (2026-06-14, both faces, to THE BAR). The
    directional-typed-edge wheel + the connection web (directed chords, cycles rendered AS cycles, drive-to-
    explore) shipped; design-critic RESOLVED both viewports. The prior "needs an acyclic backbone, three data
    sources fail" was my self-imposed total-order constraint — retired by Tim's "nonsequential IS valid / only
    directional edges type." (The relation_types vocabulary has no instances yet — a growth front, not a gap.)
  · **The small registries + gate surface + 20/80 water-law (TYPE-NUCLEATION)** — ✅ DONE (2026-06-14, both faces,
    to THE BAR). Tim UNBLOCKED it by giving the law directly (verbatim intent): "scan content → typed units →
    fall into the registry's types; what doesn't fit the registered types won't fit inside the square, so they
    pile up OUTSIDE; past a THRESHOLD a DISTINCT pile becomes a new type (a heap of leftovers is NOT enough — it
    must be a distinct type); the inverse — a registered type that falls below — is context-dependent, not a hard
    rule; the laws underneath are the invariant; NOTHING is for a specific purpose — choosing one is automatic
    failure." So my prior "Tim-gated on the forbidden-definition / the second axis" was an INVERSION of his
    delegation (now corrected below). Built (commit this beat):
      · FUNCTION — `projection.nucleation_report()` + `radius_from='nucleation'`: fit each item to the nearest
        registered type; MEMBERSHIP = the type's OWN admission extent (truthful, NOT a tuned global floor — the
        all-pile/all-fit degeneracy the data forced me away from); cluster the bounded pile; a candidate is
        DISTINCT when its silhouette margin (mean member→own-centroid cos − mean member→nearest-type cos) BEATS a
        PERMUTATION-NULL over the pile (parameter-free, the no-magic-constant discipline the fifth gate set); BORN
        when distinct AND its mass passes the 20/80 dial; thinning types → context-dependent dissolution
        candidates. `bridge._nucleation_projection` resolves the registry centroids + item vectors (cross-instance:
        types from one store, items from another → non-circular); `bindings/by_nucleation.py`; project() stays pure.
      · FORM — the registry is the SQUARE; fits sit inside, misfits pile in a RING OUTSIDE the box, distinct piles
        bloom as CANDIDATE NEW TYPES at the rim (✦ born / ◦ forming / · pile), a readout card (membership · the
        candidates with margin-strength · dissolution), and DRIVE controls: the registry picker, the store picker,
        the rung, and the 20/80 dial (visibly moves the born line). design-critic + design-lint (0 lattice literals).
      · VERIFIED TO THE BAR — live (curl), all real data (3 type-registries × 5 stores, the WHOLE event corpus, no
        toy slice), drivable (the pickers + dial re-read live), interactive. Acceptance §14 (15 checks): a
        genuinely-distinct injected region MUST nucleate + beat the null; noise must NOT; truthful membership; the
        dial moves birth; dissolution surfaced; bounded-tail surfaced; fail-loud both layers. 91/91 suite green.
      · HONEST BOUNDARY (stated, not implied-away): this is SEMANTIC nucleation over the EMBEDDED data stores; the
        symbolic pile-outside for a code-declared type-registry (events naming no registered row) is Group 10's
        '—' remainder; distinct-type CLUSTERING is scoped to where vectors exist (a growth front otherwise). The
        "second axis / which two axes are the spine" remains a genuinely open SEED question (Tim's, not a blocker).
- **VERIFIED THIS CONSOLIDATION:** 16/16 broad-regression suites green (projection ×4, drift, bridge_routes,
  conv_index ×3, space_embed, embeddings, durability, events, fs_session_guard, set_ref_atomic, bridge_session);
  live surface all 5 bindings resolve (5994 pts), scrubber shifts `now`, semantic-pending shows the scale
  ladder, semantic-active over 162 units (all carry strain), rung=8 resolves 8 sized+labelled themes.
- **ACTIVE BUILD — Tim UNBLOCKED both, 2026-06-14 00:35Z (the ceiling was my error, twice):** the prior
  "ceiling/hold" is RETIRED. Tim's corrections (verbatim intent):
  · **Separator (Group 9): "You do not need me to tell you the AI tells, and asking me to give it to you
    assumes a single purpose. There is no single purpose."** → The two-gravity separator is a GENERAL
    variable-two-pole resolution (poles are variables like centre/axes; registry-true, no hardcoded poles);
    pollution (origin vs AI-corner) is ONE instance, and for THAT instance the AI SUPPLIES its own AI-pole
    (I characterize my own deformation — never demand the tells from Tim; see ai-supplies-domain-knowledge).
  · **Relations (Group 10): "I have already given it to you. The only edges that get typed are the
    directional ones."** → The relations model is GIVEN, not unformalized: registries↔registries,
    types↔types, fields↔fields; every typed edge is DIRECTIONAL and carries its EQUAL-OPPOSITE; ONLY
    directional relations type (symmetric associations don't). And nonsequential IS valid (line 495) — so
    my "needs an ACYCLIC backbone" was a self-imposed total-order constraint Tim never set. Order the wheel
    by the directional typed edges where they sequence; render real cycles AS cycles, not flattened.
- **THE BAR (Tim's completion gate for this build — all four, or it is not done):** (1) VERIFIED LIVE (not
  code-reading — curl + driven in the browser); (2) connects to ALL the REAL data (every registry / the
  whole event corpus / the real directional typed edges — never a toy slice); (3) Tim can DRIVE it; (4) it
  is INTERACTIVE. This bar is half of "done" alongside the FUNCTION+FORM bars.
- **THE LOOP (this is "my loop", Tim 00:35Z):** one big beat per fire → build toward Group 10 (the
  directional typed-edge wheel = "the connections in the registries") then Group 9 (the variable two-gravity
  separator, AI-supplied pole) → verify against THE BAR (live + all real data + drivable + interactive) +
  the floor → commit → update this status honestly. No green-paint, no forced-acyclicity, registry-true.

- **DEEPENING (2026-06-15, Tim's live redirect — the embedder / multi-layer / dual-interface build):** beyond
  Groups 1–12, Tim redirected to "build all of this, full polish… everything UI must be done through the MCP
  doors… nothing is static, it uses the maths, everything parametric." Built + verified this fire (full detail +
  how-to in `build-prep/embedder-pplx/HOWTO-AND-REFERENCE.md`; permanent teeth in
  `tests/projection_multilayer_acceptance.py` 13/13):
  · **MULTI-LAYER embedding model — ✅** one item carries MANY embeddings keyed by C1 `#emb=`; the whole store
    write+read path layer-aware; whole corpus dual-layered (BGE + pplx) + pyramids; self-describing
    (`/api/layers`, `/api/layer-dims`). Non-destructive (emb=None byte-identical).
  · **LayerChip `◫` (the UI layer picker) — ✅ VERIFIED LIVE** (1440×900 + 390×844 + 844×390): registry-true
    (reads `/api/layers`), switching default↔pplx visibly re-projects the keystone.
  · **OPTICS CLUSTER FORM — ✅ design-critic PASS** (all four findings resolved + re-verified live across
    desktop/portrait/landscape): the cluster (lens · layer · resolution · centre) reads as one coherent
    family — landscape vertical stack (was a shattered rail), centre chip in the family treatment, atomic
    wrap in portrait, and popover-collision (`useChipMenu`) so menus never clip a mobile edge. 0 off-token
    literals. See commit `8a93b3f`.
  · **MRL resolution axis (`?dim=`) on ALL vector lenses — ✅** nucleation + semantic + separator (consistent
    truncation; `binding.res` echoed); the **ResChip `◎`** (UI resolution picker) ✅ VERIFIED LIVE — ladder
    DERIVED from the active layer's full dim (never hardcoded). The 2-D scale (rung × dim) is now drivable.
  · **ONE ENGINE, TWO FACES — ✅** `bridge.build_projection` extracted; the bridge HTTP face AND the MCP door
    (`mcp_face/tools/instrument.py`: `project` + `layers`, via `Suite.project`/`Suite.layer_dims`) call the
    SAME resolver (reuse-don't-parallel). `layers` (live ✓) returns `{space:{emb:dim}}` — the MCP twin of both
    UI pickers. Fix `3b57981`: bindings discovered by ABSOLUTE path (the cwd-relative default silently fell
    back to raw for every binding in the MCP process — the permanent regression guard is check #1 of the suite).
  · 🟡 **MCP `project` live-verify — pending ONE MCP reconnect** (a Tim INPUT; SKIP-not-stall per the loop): the
    fix is proven by execution (all 8 bindings resolve from a wrong cwd) but the running MCP process holds the
    pre-fix module; `mcp__company__project` returns raw until the next reconnect, then returns the true keystone.

---

## GROUP 1 · INSTRUMENT — THE FLOOR (the variable engine) ✅ (suite committed 6615e53)
`runtime/projection.py:project` + `BindingRegistry` + `bindings/` resolve a frame from a swappable
lens; sectors data-driven; lock x=2π/n re-divides evenly.
- **FUNCTION** — the angle/depth/now/binding floor is a pure read over the store; no hardcoded
  sectors; a COMMITTED acceptance suite proves the invariants (r∈[0,1], θ inside its sector wedge,
  even re-division at every n, lock holds, kind-group '*' remainder catches everything). ✅ by use —
  `tests/projection_instrument_acceptance.py`, 26 passed 0 failed; deliberately does NOT pin the
  stubs (rings:4, time-radius) that G2/G6 replace.
- **FORM** — n/a (backend). The suite IS the form of "done" here. ✅

## GROUP 2 · INSTRUMENT — THE SQUARE/STRUCTURE HALF (the grid) ✅ (ebbfb89; critic-passed both faces)
The seed's m/2 concentric circles + dyadic (i,j) grid — built. Both stubs (rings:4, depth scalar) gone.
- **FUNCTION** — ✅ by use: `_grid_cell(address)`→(i,j,d) the dyadic quadtree coord (MSB-first → a parent
  cell contains its children; scheme-agnostic — NOT parse_ui_address, which is ui://-only fail-loud);
  per-point `cell`; `grid` m = 2^(deepest path, cap 4); `rings` = m/2 (the rings:4 hardcode gone).
  Proven: live payload rings 8 / grid 16 / per-point cell; suite 35→41 (power-of-2, rings==m/2, cell
  bounds, depth-tracks-nesting, determinism+scheme-strip, CONTAINMENT).
- **FORM** — ✅ (design-critic PASS both viewports): the box frames the wheel (the outer circle inscribed,
  corners past it at the diagonals);
  the dyadic grid fades by level (coarse anchors, fine recedes); the picked point's CELL lights up gold
  (its square home — the circle/square duality, seen); the card shows 'cell i,j · depth d'. On tokens
  (box/grid --tx-3, cell --acc), angle-hue preserved. The first design-critic FAILED it (grid
  under-contrast, imperceptible at native viewing — measured delta 5–19); contrast RAISED per its
  prescription (box 0.85, grid by-level 0.50→0.14). ✅ by rubric — the SEPARATE design-critic re-confirmed
  PASS at 1440×900 AND 390×844 (measured: box frame Δlum ~66-113, coarse grid ~14-43, fine ~5-7 with the
  level-graded fade intact, subordinate to the wheel; the picked cell reads as a located cell, not floating).

## GROUP 3 · INSTRUMENT — TIME-FREED / RELATIVE CENTRE ✅ (backend dabf952; FE 9be11cc + 3f65f70)
The centre is freed — both in the engine (`project(now=, center=)` + bridge `?at=`/`?center=`) and in the
surface (the scrubber + re-centre + animation).
- **FUNCTION** — `?at=` parsed in bridge, `project(now=)` filters events ts≤now (the scrubber); AND a
  non-now ADDRESS centre re-projects radius as STRUCTURAL tree-distance from that address
  (`_tree_distance`, mirrors `address_tree_distance`, kept in projection.py so the floor has no suite
  dep). ✅ by use — suite 26→35 green; live curl: `?at=-2h` shifts `now` 2h back, `?center=` flips
  `radius_from`→'address' with the centre event at r=0, all r∈[0,1]. FE driven at both faces: scrub
  (5470→2105 pts, '◷ 125h ago'), live→'◷ past'→return-to-now, re-centre (chip + distance-shells),
  clear, lens, frames, zoom, mobile bottom-sheet 'centre on this'. The cosine/semantic relevance ring
  (a SEMANTIC centre-radius) was stubbed here pending Group 6 — now DELIVERED by Group 6 ✅
  (`radius_from='semantic'`: pick any embedded item → "◎ meaning-field from here"); the old 🔴 is retired.
- **FORM** — ✅ by rubric: the scrubber (⏱, gold = the privileged time axis) + zoom (⌕, dim) are
  distinct controls; a 'centre on this' affordance + a '⊙ <name> ✕' chip; re-centring/reframe ANIMATES
  (easeOutCubic rAF, identity survives, off the live-refresh path). All on corpus tokens; pointer-events
  fixed so foot controls are real-tappable; foot wraps (no phone overflow); design-lint clean
  (LatticeView 0 / lattice app.css 0). A SEPARATE design-critic passed all 6 dimensions at 1440×900
  AND 390×844 (slider-distinctness defect found + fixed + re-confirmed).

## GROUP 4 · INSTRUMENT — REAL-TIME PUB-SUB ✅ (528704a; Tim's explicit ask)
The lattice subscribes to `/api/stream` (SSE over the shared events.jsonl tap); the 15s poll is retired.
- **FUNCTION** — ✅ by use: an EventSource on `/api/stream?since=<latest seq>` (only future events stream);
  on a new event, a 220ms-coalesced re-projection (server stays the projection authority — no parallel
  client math); `setInterval(15000)` removed; `now` advances on a continuous ~22fps client-clock rAF
  (the centre breathes smoothly, stops when frozen/scrubbed). Proven: network `GET /api/stream?since=`
  [200]; appended a real event → live count 5493→5494 in <2s with NO reload (and it minted a new
  kind-sector 50→51 — the data-driven engine, live). Suite 35/35.
- **FORM** — ✅ by rubric: updates are setProj + canvas REPAINT (the `<canvas>` is never remounted —
  verified same DOM node across re-projection → not a flicker/reload); new arrivals DRIFT IN (markNew →
  the easeOutCubic fade-in tween) while placed points hold. A SEPARATE design-critic: PASS, no FORM
  regression at 1440×900 AND 390×844.
- **ROBUSTNESS (carry-forward, found in G5 review)** — ✅ FIXED (2026-06-14, verified by use). The error
  view used to return early with NO controls → a failed pull was a dead-end until reload (worse than the
  note said: the 15s poll was retired for SSE, which only subscribes after a SUCCESSFUL fetch, so there was
  no auto-recovery at all). FIX: a `retry` nonce in the fetch deps + the error view now renders ↻ retry
  (re-fires the same params) AND ← default lens (escape a bad binding/pole, clearing bind/center/poles/at).
  VERIFIED LIVE: monkeypatched /api/projection → 503 → error view shows both buttons (no dead-end) → restore
  + ↻ retry → recovered (lattice + HUD back). Token-only; the error view re-centred as a tight column. ✅ by use

## GROUP 5 · INSTRUMENT — THE FORM FACE (the lattice on the design system) ✅ (committed dc3378a)
LatticeView.tsx WAS the LONE region still on the dead GitHub-dark palette (undefined --accent/--ink-dim
→ hardcoded fallbacks; 37 CSS + 6 tsx literals). Repaid.
- **FUNCTION** — unchanged behaviour through the rebuild (lens switch, frames, forager seam,
  live/frozen, zoom, pick→card, select→set-bar→hand-to-builder all still work). ✅ by use — every
  interaction driven at 1440×900 AND 390×844; builder-context fires; mobile card docks bottom-sheet.
- **FORM** — chrome rebuilt on kit primitives (Badge pills, EmptyState error) + corpus tokens;
  the draw() palette resolved from --acc/--tx/--bg/--line/--tx-3 (no hex), live-dot off-palette
  green → gold, box-shadows → --shadow, ls-go text → --ink-accent; design-lint CLEAN on
  LatticeView.tsx (0) and the lattice's app.css contribution (37→0); the angle-hue PRESERVED;
  a SEPARATE design-critic passed the WHOLE screen at desktop AND 390×844 (pixel-verified). ✅ by rubric
  NOTE (out of scope): 2 pre-existing #fff remain in app.css (.review-frame/.studio-frame) — deliberate
  white 'paper' for rendering mockup HTML, not the lattice; left intentionally. CONSEQUENCE: a
  FILE-LEVEL gate (`check.py --target canvas/app/src --fail-on`, rule 9) stays RED from those two —
  "Group 5 lattice-clean" is NOT "the app.css gate is green". A white token (or a lint allowlist) is a
  design-folder concern (generated CSS, another session), not the app's to hand-edit.

## GROUP 6 · ABILITY — THE CIRCLE / SEMANTIC RADIUS ✅ (2026-06-14; both faces verified by use, design-critic PASS)
Built on Group 8's live spaces. commits 078eb6a (FUNCTION) + 53b4baf (FORM + empty-core fix) + 7d231a0/this (criteria).
- **FUNCTION** ✅ by use — `project(..., radius_from=='semantic')` resolves r = MEANING-distance from the
  centre = 1 - cosine, read off the persisted per-space vectors (project stays PURE — vectors ride in via
  `vectors=`, keyed by `_addr_of`; the store I/O is the bridge's: `store.get_vector` over the binding's
  space). `bindings/semantic.py` (space='topics'). `vector_index._cosine` replicated in the floor.
  Verified by use (live bridge, center=suite.py over topics): 162 points, centre at r=0, nearest
  neighbours small r, claimed_status.py at the rim; no-centre → legible 400; raw/time bindings unchanged
  (41/41 instrument regression). `tests/projection_semantic_acceptance.py` (15 checks).
- **FORM** ✅ by rubric — the lattice renders the meaning-field: pick any embedded point → "◎ meaning-field
  from here" (sets the semantic lens + centre together — no chicken-egg); radius reads off p.r (temporal
  frames hidden), axis "farther in meaning →", a normalized note + a pick-a-centre banner; r_unknown points
  faint at the rim. design-lint contribution 0. EMPTY-CORE FIX: the centre's cosine=1.0 was an outlier that
  compressed neighbours into the outer band (design-critic caught it, nearest at r~0.39); now the centre is
  EXCLUDED from the normalization band → centre at 0, nearest at 0.06, full radius. SEPARATE design-critic
  re-verified at BOTH viewports (1440×900 + 390×844): inner core populated, smooth gradient from near-origin
  (~4-6% of max) to rim, near-vs-far readable by distance — PASS on both (was a hollow-core FAIL).

## GROUP 7 · ABILITY — STRAIN / FORBIDDEN ZONES ✅ (2026-06-14; both faces verified by use, design-critic PASS)
The structure↔meaning gap (SEED §111). Built on Groups 2 (the square) + 6 (the circle). commits f00aa25 + this.
- **FUNCTION** ✅ by use — per-point STRAIN = |r_struct − r_semantic|: where it's FILED (structural radius
  = tree-distance from the centre over the SOURCE address, normalized like r) vs where it MEANS to be (the
  semantic radius). NOT a 2D cell↔wheel distance (the one-sector angle is hash-jitter → the centre, the
  MOST coherent point, would read max-strain — the advisor caught this); compared like-for-like as radii at
  a shared angle, so the centre is 0/0 → strain 0. Computed in `project()` semantic-mode-only (the circle
  must be MEANING); a vectorless point carries NO strain (no fabricated coherence). `mark_types/strain.py`
  registered (score · surface — so strain can be MARKED + surfaced; render, never auto-correct). Verified by
  use (live bridge, center=suite.py): 162 points carry strain, centre strain 0.0, divergences real
  (flows.py means-like-suite-but-filed-far → 0.80; coherence_calibrate.py filed-near-but-means-differently
  → 0.73). `tests/projection_semantic_acceptance.py` extended (23 checks incl. the centre≈0 dispositive
  guard + coherent≈0 + divergence-high + far+far-is-coherent).
- **FORM** ✅ by rubric — a "⊿ strain" toggle on the meaning-field draws the RADIAL tension segment from
  r_struct to r at each point's angle (SEED §111's literal "line between where it's filed and where it means
  to be"); alpha+width ∝ strain so coherent points vanish and only divergence reads as tension; the picked
  card shows "⊿ strain · filed ↔ means". design-lint contribution 0. SEPARATE design-critic PASS at BOTH
  viewports (1440×900 + 390×844): lines appear, toggle ON/OFF clean, card math exact (e.g. 0.69 filed ↔ 1.00
  means → 0.31), geometry proven (distinct radii, not a spoke artifact), gradation self-thins (not a
  hairball — eye drawn to real divergences), gold-on-warm-dark tokens. Honest caveat: a busy CENTRE (one
  with many near-in-meaning-but-filed-far neighbours) reads denser near the origin — a centre-choice, not a
  width artifact; still legible. (forbidden-zone = a high-strain threshold marker — a later refinement.)

## GROUP 8 · ABILITY — EMBEDDING SUBSTRATE LIVE ✅ (2026-06-14; verified by use, unblocks 6,7,9,11)
CORRECTION of the prior "mechanism complete" premise: the mechanism was NOT complete. The single-lens
`repo` path existed (ingest_paths → repo_digest → repo space) and `history` was populated, but the
embeddable lenses topics/principles/worldview had NO producer — declared spaces, EMPTY on disk (0 each).
The capture-schema builder the architecture NAMED (projections.py:5 / suite.py:292 "output_schema built
FROM model_projections()") was never built. So Group 8 was a BUILD, not a bring-up. Built it.
- **FUNCTION** ✅ by use —
  · embed-bge UP via `company up embed-bge` (no --evict; co-fits chat-4b on the 16GB card — needs ~4.9G,
    7.0G free); HEALTHY on :8001 (BGE-M3, verified `/health`→200).
  · `Suite.capture_corpus_lenses` (runtime/suite.py) — the MULTI-LENS capture lane: builds ONE dynamic
    output_schema FROM the registry (model_projections ∩ requested lenses), fans it over file units
    (run_items @ chat-4b :8000), captures+embeds each lens field into its space (capture_corpus →
    embed_corpus_to_spaces → build_index(space=)). REUSE: walk_files + run_items + capture_corpus, no
    parallel vector path. Fail-loud: a non-registry / non-model / non-embeddable lens RAISES. Incremental
    (resume-safe; bounded batches compose to full coverage).
  · POPULATED: topics/principles/worldview = 162 each (full backend corpus: runtime/store/contracts/ops/
    roles/projections/fabric/nodes/mcp_face), real BGE-M3 1024-dim vectors, 0 failures; content is
    meaningful + render-not-judge (verified: topics.py → topics=["content lens","vector space",…]);
    queryable via `query_corpus(space=…)` (live :8001 cosine). repo=644, history=1464 pre-existing.
  · index freshness CONFIRMED via `vector_index.index_staleness` (extended with `space=` param):
    topics/principles/worldview fresh=True (162 corpus==162 indexed, 0 missing/changed/extra), repo
    fresh=True (644==644). The 20-check staleness regression still passes (space=None byte-identical).
  · acceptance suite `tests/capture_lenses_acceptance.py` (18 checks) + drift green; commits ea10f24
    (lane + index_staleness space=) + 30e8356 (suite + STATE reflection).
  · COVERAGE: backend 162/repo-644 (partial — the substrate IS live; "populates" met). NOT self-driving:
    `capture_corpus_lenses` extends ONLY when RE-INVOKED with broader roots (frontend .tsx / docs) — the
    incremental lane is resume-safe, but nothing auto-calls it yet (a routine/later beat must re-invoke).
  · query_corpus(space='topics') ranks items by cosine, returning the source address as `id` (verified —
    e.g. "subjects a file covers" → what.py/projections.py nearest); this IS Group 6's semantic-radius input.
- **FORM** — n/a (substrate). ✅

## GROUP 9 · ABILITY — TWO-GRAVITY SEPARATOR ✅ (2026-06-14; both faces, design-critic PASS both viewports, to THE BAR)
> SUPERSEDES the old plan (a "steerable embedder" threaded through transport→client→embed→build_index +
> Tim's AI-tells). Tim 2026-06-14: "There is no single purpose" → the separator is a GENERAL variable-two-pole
> resolution; the AI supplies its OWN AI-pole (never demand the tells from Tim). And the PURE-READ law: the
> instrument never re-embeds — it READS the per-space vectors that already exist. So the built mechanism is a
> pure two-pole read over the persisted vectors, NOT an embed-lens. Poles are VARIABLES (any address with a
> vector in the lens — a corpus item, a cluster:// theme centroid, or a planted anchur://), registry-true
> (declared in a binding ROW, overridable per request) — no hardcoded poles.
>
> **BUILT this beat (FUNCTION, commit pending):**
> · `runtime/projection.py` — `radius_from='separator'`: per item pull_a=cos(item,A), pull_b=cos(item,B),
>   signed lean=pull_b−pull_a; radius=|lean| min-max (NEUTRAL→centre, BOTH poles→rim — the two gravities as
>   equals, no centre-pile); BOTH raw pulls + the lean carried per point (no signal thrown away). Vectorless
>   point → rim + r_unknown (flagged, never dropped). Missing poles → fail loud.
> · **THE FIFTH GATE** — `separation_report()` (raw cosines, the witness the field actually SEPARATES, since a
>   normalized radius gradients over noise): FOUR degeneracies ALL refused → pole_distinctness ≥ floor · spread_a
>   AND spread_b ≥ floor (kills a dead/constant pole) · Spearman(pulls_a,pulls_b) NOT ≈ +1 (kills a redundant
>   pole; opposed poles ρ→−1 PASS — the false-negative the earlier gap-rank draft would have had is gone) · AND
>   min(lean_a,lean_b) ≥ 1 (kills a ONE-SIDED field — a pole attracting NOBODY collapses to a one-pole distance;
>   a hard count-of-zero, not a tuned threshold). The BALANCE (lean_a/lean_b/minority_frac) is also surfaced for
>   the DEGREE of skew among fields that do separate.
> · `runtime/bridge.py` `_separator_projection` — resolves the two pole vectors (unit item / cluster centroid /
>   planted anchor) + the item vectors from the store; project() stays pure; poles drivable via ?pole_a=&pole_b=.
> · `bindings/by_separator.py` — the general lens (default poles = the two MOST-distinct topics clusters).
> · `runtime/anchors.py` — the AI plants its OWN AI-corner pole: characterizes AI-deformation, embeds it through
>   the SAME BGE-M3 lens, persists anchor://ai-corner. The named pollution-instance mechanism.
> · `tests/…acceptance.py §13` — 75 pass: hermetic two-blob SEPARATES (flat=bug), identical-poles REFUSED,
>   dead-pole REFUSED, pole-agnostic 2nd config, balance, opposed-poles PASS, vectorless→rim, missing-poles fail-loud.
>
> **VERIFIED LIVE — the real-data ✅ gate (the honest, non-circular one):** the separator, driven over ALL 162
> real topics items through the bridge. The PRIMARY evidence is a NON-CENTROID pair (two real corpus ITEMS from
> different regions, NOT means of the corpus, so non-circular): pole_a=code://projections/worldview.py vs
> pole_b=code://mcp_face/tools/sessions.py → `separates:True`, distinctness 0.40, **Spearman −0.41** (strongly
> opposed gravities), balance **57/105 (minority 0.35 — a genuinely two-sided field)**, and the leaders (DIFFERENT
> items than the poles) spot-check region-clean: toward worldview ← topics.py, what.py, lineage.py, principles.py;
> toward sessions ← introspection.py, channels.py, ui_claude_session.py, rule.py. The default centroid pair (c6
> vs c4) corroborates (separates, balance 47/115) but is partly circular (centroids are means of the items), so
> the NON-centroid pair carries the claim. The general two-gravity separator is demonstrated on real data.
>
> **HONEST — the pollution instance is the NAMED DEFERRED application, correctly REFUSED today:** probed origin
> (worldview centroid, a §17 corpus sample standing in for the deferred true Tim-pole) vs anchor://ai-corner →
> balance **162/0** (every code-topic item leans to the code centroid; the free-text AI-corner attracts nobody).
> This is the lens-mismatch the design anticipated (a free-text prose pole vs a code-topic corpus). The hardened
> fifth gate now reports **separates:False** for it (the one-sided degeneracy) — so the pollution probe is not
> faked-green; it is honestly refused. DEFERRED: the true Tim-pole (§17, not a corpus sample) + a text-lens where
> the AI-corner is comparable. The ✅ rests on the balanced non-centroid real pair, never on this probe.
- **FUNCTION** — the general two-pole read + the fifth gate, verified live on a real balanced pair. ✅ by use
- **FORM** — ✅ (2026-06-14, both viewports, design-critic PASS). The two gravities render as two spatial BASINS
  (advisor's (b), chosen over recolouring): pole A fans LEFT / pole B fans RIGHT, radius = |lean| (neutral at the
  centre, strong lean at the rim), colour reinforces the side (cool A / warm B); the two poles are marked + named
  at the rims; a NEUTRAL divide bisects; the centre is a quiet neutral marker (NOT the breathing-NOW dot, which
  would lie). The readout card carries the FIFTH GATE made visible — both pole names (full, stacked), a diverging
  BALANCE bar (the advisor's mandate: separates:True can still be lopsided → Tim must SEE the 47/115 skew), and
  the verdict (separates · distinct · ρ). DRIVE-TO-EXPLORE: tap a point → its pulls + lean; ◀ set pole A / set
  pole B ▶ re-drives the field keeping the other pole (proven live — driving channels.py as pole A re-drove to
  2/160), and ↺ default poles resets to the binding's declared pair (added 2026-06-14, verified live: drive →
  reset → back to 47/115). Time controls suppressed (radius is lean, not time), like the semantic lens.
  > BUILT (commit pending): canvas/app/src/regions/LatticeView.tsx (the basin layout sepTheta used identically by
  > draw + pick; pole hues; readout + balance bar; pole picker; the controls/centre-dot separator branches) +
  > app.css (lc-sep, token-only; pole hues via inline computed hsl, the colour-IS-pole exception). VERIFIED:
  > driven LIVE in chrome-devtools at 1440×900 AND 390×844 on the real 162-item field; the pole-picker re-drives;
  > a SEPARATE design-critic PASSED all 4 criteria on BOTH viewports (caught + I fixed: a full-height card burying
  > the mobile wheel, rim labels colliding at centre, ellipsis-truncated names; and a bridge label bug — an
  > overridden pole kept the stale default label). design-lint: LatticeView 0 off-token literals (the 2 #fff in
  > app.css are the pre-existing white-paper, out of scope; the separator CSS added zero literals). 76 acceptance
  > checks still green.

## GROUP 10 · ABILITY — ORDER-FROM-EDGES + ANGLE-FROM-A-REGISTRY + THE CONNECTIONS ✅ (2026-06-14; Tim-unblocked, both faces, design-critic RESOLVED, to THE BAR)
> DONE 2026-06-14 (Tim unblocked — see ACTIVE BUILD up top): the old "edge-order needs an ACYCLIC backbone /
> three sources all fail" finding is SUPERSEDED — Tim: "the only edges that get typed are the directional
> ones" + nonsequential IS valid (no acyclic requirement I'd invented). BUILT, both beats:
> · BEAT 1 — the connections DATA (commit 85df987): project() SURFACES the directional typed edges (edges =
>   directed sector-index pairs; bidir = a real mutual cycle, rendered AS a cycle); whole_set renders a
>   registry's WHOLE structure; the bridge resolves node-types → all 16 rows + 49 DIRECTIONAL-only type-flow
>   edges; bindings/by_node_type.py; +6 floor invariants.
> · BEAT 2 — the interactive FORM (commit b136d17): the directional typed edges render as directed CHORDS
>   (bow to centre, arrowhead at target, bidir = head both ends); DRIVE-TO-EXPLORE — tap a row → its OUT
>   edges blaze gold, IN ink, the rest fade, readout card lists feeds-to/fed-by; tap centre to clear; the
>   whole-registry labelled; a backend point-drop fix (no event-dump into the last sector). SEPARATE
>   design-critic RESOLVED at BOTH viewports (drive-to-explore lights the wheel — 26,392 px change vs the
>   prior 177-px FAIL; direction readable; phone labels staggered, no collision). floor 59→60; design-lint 0.
> VERIFIED TO THE BAR: live (curl + driven in-browser) · all real data (the live node registry + its real
> type-flow) · Tim can drive it (tap rows) · interactive. The edge-order/connections FORM 🟡 is now ✅.
> NOTE: the directional typed-edge VOCABULARY (relation_types: precedes/depends_on/…) has no INSTANCES yet;
> as real typed relations are instantiated between items they render in this same view (registry-true).
> NEXT: Group 9 — the variable two-gravity separator (AI supplies its own pole).
The keystone. commits (this beat). The advisor stopped a fake "derived precedence" (order_by=time in a
costume) — only REAL persisted directed edges order sectors; registries have none yet (growth front).
- **FUNCTION** ✅ by use — (1) THE EVENT→ROW EDGE formalized: `_row_of(event, angle_from)` — a registry's
  SINGULAR-field convention (op.run→`role`, corpus.record→`projection`; `_singular` depluralizes, one rule)
  + a graph's node-ref (connect→`from_node`). (2) `_resolve_sectors` gains the angle_from=<registry/graph>
  branch (sectors = the entity-set's PRESENT rows via the edge; an event naming no row → an honest '—'
  remainder). (3) `order_by='edge'` = `_toposort` over the passed REAL directed edges (Kahn, STABLE
  tie-break, cycle-safe) — the alphabetical default RETIRED (count). Verified by use: `by_lens` (live
  bridge) divides the wheel by the projection registry (history/repo/principles/topics/worldview/what + '—');
  order_by=edge topologically orders a real graph (review-1780773666-26: 52 nodes/26 edges, 0 edge
  violations, stable). `tests/projection_instrument_acceptance.py` +12 invariants (53 total).
- **FORM** ✅ (2026-06-14, both viewports, design-critic RESOLVED — Tim-unblocked). Two faces, both shipped:
  · ANGLE-FROM-A-REGISTRY: `bindings/by_lens.py` renders the registry-divided wheel (sectors = the projection
    lenses + an honest '—' remainder), design-critic PASS at both viewports.
  · THE CONNECTIONS (the directional typed edges, drawn): the node registry's type-flow renders as directed
    CHORDS (bow toward centre, arrowhead at the target; a bidir pair = a real mutual cycle, rendered AS a
    cycle — never flattened); whole_set renders the registry's WHOLE structure; DRIVE-TO-EXPLORE — tap a row
    → its OUT edges blaze gold, IN ink, the rest fade, a readout lists feeds-to / fed-by. design-critic
    RESOLVED both 1440×900 + 390×844 (drive lights the wheel — 26,392-px change vs a prior 177-px FAIL).
  > SUPERSEDED — the prior long "needs an ACYCLIC edge-backbone / three data sources all fail / a connection-
  > web is a different feature for Tim" finding was retired by Tim 2026-06-14: "the only edges that get typed
  > are the directional ones" + "nonsequential IS valid." That made the directional-typed-edge connection web
  > the CORRECT face (cycles rendered as cycles, no acyclic order imposed), and it shipped (commits 85df987 +
  > b136d17). My "acyclic backbone" was a self-imposed total-order constraint Tim never set.
  > NOTE: the relation_types VOCABULARY (precedes/depends_on/…) has no INSTANCES yet; as real typed relations
  > are instantiated between items they render in this same view (registry-true) — not a gap, a growth front.

## GROUP 11 · ABILITY — MULTI-SCALE EMBEDDING PYRAMID ✅ (both faces verified; the SCALE axis)
THE REVERSAL (evidence-forced): the spec's "sentence/turn/session/project" rungs were CONVERSATION-shaped;
the corpus is code-digest-shaped + the per-space probe KILLED lineage as the rung axis — within ONE space
`session` is CAPTURE-BATCH provenance (ingest-flow/full-repo/g25/smoke-test — which ingest run wrote the unit,
NOT a semantic nest) and `project` is ONE point per space (company dominates). A centroid over a capture batch
is noise; a one-point project rung is degenerate. So the honest coarsening is over MEANING (the same circle
Group 6 built), not provenance: the coarse rung = fewer, larger meaning-regions = CLUSTERS of near points; a
coarse point = the cluster CENTROID. (Same plausible-but-wrong trap the advisor caught on 6/7/10; the
distinctness test below was locked BEFORE the render.)
- **FUNCTION** ✅ by use — `runtime/scale.py`: ONE agglomerative dendrogram (WARD linkage) cut at each rung →
  the rungs NEST (every fine cluster ⊂ exactly one coarse cluster — independent per-K k-means would NOT;
  ward not average — average CHAINED 129/162 & 525/644 into one giant, verified on the real topics space;
  ward gave balanced 9/19/31). Centroids persist via the SAME store.put_vector into `scale:<space>:k<K>` (no
  parallel index — `query_index` resolves them with the existing cosine); the nesting/membership/exemplar
  rides a `store.save_scale_pyramid` sidecar. Dependency-free (Lance-Williams, no numpy). `default_rungs`
  derives a DYADIC ladder from n (SEED §1 m=2^k; topics 162 → [32, 8]). The bridge's `/api/projection?rung=`
  feeds the rung's centroids to project() as pseudo-events (semantic radius unchanged) — "zoom changes which
  rung RESOLVES". Centre is PORTABLE across rungs (a theme centre resolves from its native rung; no 400 when
  stepping). Built LIVE over topics (40 centroids, real exemplars: scheduler/vector_index/README/worldview…);
  coarse query ≠ fine query proven on real data. `tests/projection_scale_acceptance.py` (29 invariants):
  nesting, ward-not-chaining, centroid=normed-mean, coarse≠fine over a real store, discriminative, persisted
  nesting, incremental, fail-loud, derived dyadic rungs.
- **FORM** ✅ by rubric — a SEGMENTED rung ladder (⊟ units|32|8), distinct from the radial ⌕ zoom (advisor's
  collision avoided); coarse points render as discs SIZED by member-count + labelled by exemplar (region halos);
  stepping rungs CROSSFADES (departing rung fades out as the incoming fades in — continuous scale move, not a
  mode switch); a theme card carries size/finer-count/exemplar + ⊕ zoom-into-theme (steps to the finer rung,
  centred on the exemplar). SEPARATE design-critic PASS at BOTH viewports (1440×900 + 390×844): scale
  legibility (8→32→units reads as a genuine grain progression), discs-as-regions, ladder-vs-zoom distinct,
  token-coherent, responsive. The critic's one FAIL (centre/dense-rung label overprint) was FIXED
  (collision-aware placement: reserve the centre marker, skip the centred theme's label, biggest-first
  non-colliding slot, drop-if-no-slot) and re-verified RESOLVED. design-lint: 0 off-token from this change.
- GROWTH FRONT (honest): raw-source sentence/turn chunking (the corpus is 1-sentence digests → chunking is a
  no-op here); a richer space (repo=644/history=1464) gets more/larger rungs automatically via default_rungs.
  The pyramid is RUNTIME data (.data, like every space) — rebuilt via the DISCOVERABLE route `POST
  /api/scale/build {space}` (registered in the bridge route table → api_verbs; fail-loud on empty/thin
  space), not a hidden script; so the ladder can't silently vanish with no recourse if .data is rebuilt.

## GROUP 12 · ABILITY — TYPE-NUCLEATION (the 20/80 water-law) ✅ (2026-06-14; both faces, to THE BAR)
Tim Geldard's growth law, given directly (his words): content is processed into typed UNITS; dropped into the
instrument they fall into the REGISTRY's types; what does NOT fit the registered types won't fit inside the
square, so they pile up OUTSIDE; when a DISTINCT pile accumulates past a threshold it becomes a NEW TYPE (a heap
of leftovers is not enough — it must be a distinct type); the inverse (a registered type that thins below) is
context-dependent, NOT a hard rule; the laws underneath are the invariant; NOTHING is for a specific purpose —
choosing one is automatic failure. A PURE READ — registry-true, every axis a variable.
commits: this beat. Built on Group 8 (the embedded spaces) + Group 11 (the scale-pyramid centroids = the
data-born registry of types) + the fifth-gate honesty discipline (Group 9).
- **FUNCTION** ✅ by use — `runtime/projection.py`:
  · `nucleation_report(item_vecs, refs, type_vecs, type_labels, type_radii, type_sizes, dial)` — the type-birth
    witness. MEMBERSHIP = each type's OWN admission extent (a low percentile of its members' cosines), so "fits"
    means actually within a type's empirical reach — NOT a tuned global cosine floor (the empirical data forced
    this: a global floor made every cross-store field 100% pile = the all-pile degeneracy; the per-type extent is
    truthful — cross-store → an honest empty square, same-store → populated + the natural outliers). DISTINCTNESS
    = the per-pile-cluster silhouette MARGIN (mean member→own-centroid cos − mean member→nearest-existing-type
    cos: members bind to each other more than to any existing type) — surfaced as STRENGTH; the binary
    distinct-vs-noise BEATS a PERMUTATION-NULL over the pile (parameter-free; dissolves the margin≈0 knife-edge a
    bare margin>0 would flap on). BIRTH = the 20/80 DIAL = a distinct cluster is BORN once its mass passes
    dial×(clustered pile) ("fills past ~20/80"); below it, FORMING. DISSOLUTION = low-tail types surfaced as
    context-dependent candidates, never auto-applied. Bounded (agglomerate is O(n³)) → clusters the worst-fitting
    `cap`; the tail is SURFACED, never silently dropped. `radius_from='nucleation'` lays the geometry (inside the
    box for fits, OUTSIDE for the pile, candidate ZONES for the blooms). `runtime/bridge.py:_nucleation_projection`
    resolves the registry centroids (scale.rung_points) + admission radii (from members) + the item vectors
    (CROSS-INSTANCE default: types from one store, items from another → non-circular) and rides them into the
    pure project(); drivable `?types_space=&space=&rung=&dial=`. `bindings/by_nucleation.py` (default topics-types
    × repo-items). Verified live: cross-store topics×repo → 0 fit / 657 pile → 2 born (wire_trigger m0.23,
    qwen3tts m0.25); same-store topics×topics → 149 fit / 13 pile (honest near-null); 3 type-registries
    (topics/principles/worldview) × 5 stores all resolve; the dial visibly moves born (0.1→2, 0.2→1, 0.3→0).
    `tests/projection_instrument_acceptance.py` §14 (15 checks, 91 total): a genuinely-distinct injected region
    MUST nucleate + beat the null; noise must NOT; truthful membership; the dial moves birth; dissolution
    surfaced; bounded-tail surfaced; fail-loud both layers; the geometry (inside r<1, pile r>1, sectors=types+zones).
- **FORM** ✅ by rubric — the registry is the SQUARE; fits sit inside it; misfits pile in a RING clearly OUTSIDE
  the box (beyond the corners — geometrically faithful to "piles up outside"); DISTINCT piles bloom as CANDIDATE
  NEW TYPES at the rim (✦ born = gold / ◦ forming = ink / · pile = dim, with an arc bracket + exemplar label). A
  readout card (membership: N fit / N piled + tail; the candidates with margin-strength + born/forming; the
  verdict; dissolution candidates). DRIVE-TO-EXPLORE: a registry picker, a store picker, the rung, and the 20/80
  DIAL (all registry-true — the bridge lists what's embedded / has a pyramid; new stores appear with no code
  edit); pick a point → its card. The empty-square cross-store case reads as intentional ("none of this fits —
  here are the types it wants"). design-lint: LatticeView contribution 0 off-token literals; app.css 0 added
  (the 2 #fff are the pre-existing white-paper). Verified by driving in chrome-devtools at 1440×900 AND 390×844
  (the card is a top banner, never the lc-sep full-height bug; pile clearly outside the box after a geometry fix).
  A SEPARATE design-critic (independent agent) drove both viewports and returned FAIL with 3 mobile/interaction
  defects (desktop strong) — ALL FIXED + re-verified (commit 3ef5f2b): (1) mobile candidate rim labels overflowed
  the screen edge (the born ✦ name unreadable) → edge-aware clamp + 15-char cap; (2) the 20/80 dial refetched the
  compute-heavy projection (~5s lag) → the dial is now CLIENT-SIDE (born recomputed in card + canvas, no refetch
  — instant); (3) mobile tap targets 16–19px → bumped to 34px. Re-driven: labels on-screen, born updates <150ms,
  controls 34px.
- **HONEST BOUNDARY** — this is SEMANTIC nucleation over the EMBEDDED data stores; the symbolic pile-outside for
  a code-declared type-registry (events naming no registered row) is Group 10's '—' remainder; distinct-type
  CLUSTERING is scoped to where vectors exist (a growth front for purely-symbolic registries). Unifying the
  symbolic remainder + the semantic pile as one "pressure" is Tim's "it's not either/or, it depends on context."

## MODEL CALLS — DISSOLVED (2026-06-13; Tim confirmed "your logic was actually all correct")
See SEED-SCALE-PRIMES-SEPARATOR.md §17. The gate is GONE — every "model call" was the lead trying to
freeze a variable Tim deliberately left free (the hardcoding reflex). Resolution:
- **Call 1 (register = prime/divisor lattice?) — INVALID.** Not a separate formalism; the equation
  recursing one scale up (corners = primes already). No ratification, no gate.
- **Call 3 (the two privileged axes) — INVALID.** Axes are variables; it is ONE-and-three — only TIME
  is privileged (settled); the three of space stay variable. Build the resolver, never fix them.
- **Call 2 (two-gravity anchors) — ANSWERED structurally.** Poles = the CENTRE (Tim's model/origin +
  the gradient field of his recognitions) and the CORNER (AI deformation). Nothing in the corpus is
  purely Tim, so the Tim-pole is the origin+gradient, NOT corpus samples. The ONLY input is Tim
  describing the AI-tells (volunteered). → Group 9 is UN-GATED.
- **Call 4 (harmonics) — ANSWERED.** "As one instance" — a lens, not the core; spectrum stays out.
- Genuinely-open growth fronts (not gates, not blockers): k (the dimension); prioritization-at-scale.
  RESOLVED (2026-06-14): the 20/80 / TYPE-NUCLEATION is now BUILT (Tim gave the law directly — see GROUP 12 and
  the TYPE-NUCLEATION entry). It is NOT a visual prioritization dial and NOT a green-paint density stub: it types
  content against a registry of types, piles the misfits OUTSIDE the square, and a DISTINCT pile (silhouette
  margin beats a permutation-null — no tuned floor) past the 20/80 birth-mass becomes a candidate new type. The
  earlier "gated on Tim's formalization" caveat is superseded by his direct statement of the law.
**Consequence: NO build item is blocked awaiting a Tim decision. The whole sequence is buildable now.**

---

## PRIORITY ORDER (dependency; instrument-first then ability — the loop walks this)

0. **Model calls DISSOLVED** (§17; Tim confirmed) — no gate; the whole sequence is buildable. (Group 9's old
   "AI-tells input" is also retired — Tim: "there is no single purpose"; the AI supplies its own AI-pole.)
1. **Group 1** — ✅ DONE (6615e53) — the acceptance suite (regression floor; 26 invariant teeth).
2. **Group 5** — ✅ DONE (dc3378a) — the FORM rebuild (lattice onto the corpus design system).
3. **Group 3** — ✅ DONE (backend dabf952 + FE 9be11cc/3f65f70: scrubber + re-centre + animation, both faces, critic-passed).
4. **Group 4** — ✅ DONE (528704a: SSE subscription, poll retired, smooth client clock, critic-passed).
5. **Group 2** — ✅ DONE (ebbfb89: dyadic grid + m/2 rings + picked-cell highlight; critic-passed both faces). The INSTRUMENT half is complete.
6. **Group 8** — ✅ DONE — embedding substrate live (embedder resident via the `company` CLI + capture+embed).
7. **Group 6** — ✅ DONE — semantic radius (the meaning-field, the first ability ring).
8. **Group 7** — ✅ DONE — strain / forbidden zones (per-point structure↔meaning incommensurability).
9. **Group 10** — ✅ DONE (2026-06-14, both faces) — the event→row edge + angle-from-a-registry + THE
   CONNECTIONS (the directional typed-edge web, cycles AS cycles, drive-to-explore). The keystone.
10. **Group 9** — ✅ DONE (2026-06-14, both faces) — the two-gravity separator (general variable-two-pole read
    + the fifth gate + the two-basin drivable FORM). Tim retired the old "Model Call 2 / AI-tells" gate.
11. **Group 11** — ✅ DONE — the multi-scale pyramid as the SCALE axis: ward-clustered meaning-rung centroids
    (NOT lineage — evidence-killed), nested rungs, a crossfading rung ladder, design-critic PASS both faces.
12. **The small registries + gate surface + 20/80 water-law (TYPE-NUCLEATION)** — ✅ DONE (2026-06-14, both faces,
    to THE BAR). Tim gave the law directly (the "Tim-gated on forbidden-definition / second axis" framing was MY
    inversion of his delegation, now corrected). Built as a PURE READ: type a content store against a registry of
    types; misfits pile OUTSIDE the square; a DISTINCT pile (silhouette margin beats a permutation-null — no tuned
    floor) past the 20/80 birth-mass becomes a candidate new type; thinning types → context-dependent dissolution.
    `nucleation_report` + `radius_from='nucleation'` + `_nucleation_projection` + `bindings/by_nucleation.py` +
    the FORM (square / pile-outside / candidate blooms / drive controls + dial) + §14 acceptance (15 checks).
    Verified live across 3 type-registries × 5 stores, both viewports. (The "second axis" stays a genuinely open
    SEED question — Tim's, not a blocker.)
