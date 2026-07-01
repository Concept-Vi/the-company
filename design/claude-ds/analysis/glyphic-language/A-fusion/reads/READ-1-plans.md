# READ-1 · The Plans — what already constrains "A" (the AI/Company fusion)

> **Lane.** This is the PLANS stream of the A-fusion reads. It consolidates every DECISION, LAW, quoted
> plan-statement, and open-question the existing plan-triad + map + thinking-doc hold **that A touches** —
> so the A design is built on TOTAL knowledge, not a partial re-derivation. It does NOT do the code
> inventory (that is another read) nor the A design itself.
>
> **What A is (the mandate being designed):** make the design-system `CV_AI` a **multi-provider registry
> resolved by ROLE**, **Company-default**, reaching the Company **embedder + local models**; and **fuse the
> overlapping design-system-AI ↔ Company-cognition-AI** into one. In the plan-vocabulary A = **build group
> G-L1** (LIVE-INSTRUMENT's "Provider role-layer + `company-http` runtime") PLUS its **dual-authoring face**
> (CRITERIA G0.4 + G8.3, already seeded by C).
>
> **Sources read in full:** `live-instrument/LIVE-INSTRUMENT.md`, `CRITERIA.md`, `GUIDE.md`, `SYNTHESIS.md`,
> `UNDERSTANDING/00-the-thinking.md`, `live-instrument/catalogue/README.md`, `analysis/LANGUAGE.md`,
> `live-instrument/ANCHOR.md`; design-system charters (`claude-ds/CLAUDE.md`, `design/CLAUDE.md`). Code
> anchors read directly: `system/glyphgraph-generator.html:174-176`, `app/ai/ai-registry.js:198-343`,
> `app/ai/ai-glyphic-language.js`.

---

## ⚠️ Read this first — TWO colliding G-numberings (do not conflate)

There are two independent "G" sequences in these docs. **A downstream A-designer who conflates them builds
the wrong thing.** This brief always qualifies.

- **CRITERIA-G / GUIDE-G (the ENGINE build):** G0…G11. Here **G0** = the one-mechanism spine, **G1** =
  universal-operator lexicon, **G8.3** = register authoring in `CV_AI`. (`CRITERIA.md`, `GUIDE.md`.)
- **LIVE-INSTRUMENT-G / "G-L" (the INSTRUMENT build groups):** G1…G11. Here **G-L1** = the provider
  role-layer = **A itself**, **G-L2** = the semantic icon index + embedder. (`LIVE-INSTRUMENT.md §Build groups`.)

**"G-L1" in the task = LIVE-INSTRUMENT-G1 (the provider role-layer), NOT CRITERIA-G1 (the lexicon).**
A therefore lives across BOTH sequences: G-L1/G-L2 (provider + embedder side) AND CRITERIA-G0.4/G8.3
(dual-authoring side).

---

## (a) DECISIONS already made that constrain A

Each is **settled** in the plans (not an open question). Marked with its doc:section ref and the doc's own
evidence tag where present.

### A-1 · Home = `claude-ds/` (the design system), reaching INTO the Company
- The provider role-layer is built **in `CV_AI`** — inside `claude-ds/` — and the Company fleet enters it as a
  runtime. `LIVE-INSTRUMENT.md §1 fused-direction` (223–232): *"a **role-resolution layer** in `CV_AI`."*
- The design↔Company boundary is a **SEAM, not a wall** — touching `~/company` (with care) is part of the
  convergence. `LIVE-INSTRUMENT.md §lens 6` (31–32); `00-the-thinking.md §1` (46–47, `[Tim's word]`).
- G-L1 is tagged **"Design-side + cross-into-company"** (`LIVE-INSTRUMENT.md §Build groups G-L1`, 509–512).

### A-2 · Role-resolution, never a pinned model (the core of A)
- **Hard law 6** (`LIVE-INSTRUMENT.md §hard-laws`, 428): *"**Role-resolution, never a pinned model.**
  Capabilities declare a role; one config maps role→provider; the Company fleet resolves the model. Assert
  `satisfied`, not a non-empty model."*
- Mechanism (`§1 fused-direction`, 223–226): capabilities declare a *role* (`extract-entities`,
  `compose-graph`, `embed`, `text`); one **`ROLE_PROVIDERS`** config maps role→provider id — *"the single
  place an id is pinned."* `execute()`'s line 299 + the two fallbacks route through it; the ~27 caps drop
  `provider:'claude'`.
- This realises the standing rule **cognition-is-role-resolved** in `CV_AI`, mirroring Company
  `run_role`/`models_for_role` (`§1 table` row 3, 219; `§1 fused-direction`, 230).
- **Assert `satisfied`** — the honest-status flag, NOT truthiness of the model string (the `satisfied` FLOOR
  trap: a role silently floors to the resident 4B). `§1 table` row 3 (219); `§7 fused-direction` (330).

### A-3 · Company-default (not just "role-resolvable")
- The role→provider config **defaults to the Company fleet**, and the flip is atomic: *"Flipping the whole DS
  to Company-local = **one edit**."* `LIVE-INSTRUMENT.md §1 fused-direction` (226). This is a direction-of-
  default decision, not only a mechanism — A must make Company the default resolution target.

### A-4 · The Company enters as a `company-http` runtime — NOT `CV_HOST_NATIVE` (settled)
- *"The Company fleet enters as a **`company-http` runtime** (modelled on `openai.js` direct-fetch) hitting the
  bridge `/api/cognition/run_role` (role-resolved, json_schema structured outputs) — **NOT** the
  `CV_HOST_NATIVE` export path (**vaporware, never injected**)."* `LIVE-INSTRUMENT.md §1 fused-direction`
  (227–229). This closes the "how does the browser reach the fleet" question: direct-fetch HTTP runtime to the
  bridge, structured outputs via json_schema.
- The design-system charter confirms the runtime-registration pattern this rides: `resolveProvider` delegates
  unknown kinds to `CV_HOST.resolveProviderRuntime` — *"Add a way to reach the world = register a runtime, not
  edit every caller."* `LIVE-INSTRUMENT.md §1 table` rows 1–2 (217–218); `claude-ds/CLAUDE.md §1` (AI row) +
  observed `ai-registry.js:198,233-234`.

### A-5 · One-IR law (constrains what A's output feeds)
- **Hard law 1** (`LIVE-INSTRUMENT.md §hard-laws`, 416–418; §lens 4, 24–26): there is ONE `CVGraph` IR
  (`core/cv-nodes.d.ts`); every render surface is a *projection*. A surface with its own node model = the
  "fifth parallel strand" (`UNIFICATION.md §4`). A's extract/compose output must emit a
  `CVGraph{type:'glyphgraph'}`, not a parallel structure. (`CRITERIA.md §G-L4` maps to this; G3.1/G3.2 in the
  CRITERIA-engine sense.)

### A-6 · Loud-fail everywhere (governs A's failure behaviour)
- **Hard law 4** (`LIVE-INSTRUMENT.md §hard-laws`, 424): unknown facet/value/**provider**/runtime/type →
  **throw**; a resolve-miss → foundry-or-Notice + a recorded Gap; *"never a silent fallback to claude."*
- Design-system non-negotiable: *"**Loud fail, never silent.** Missing provider/runtime/capability/type →
  `throw`, don't degrade to a default."* `claude-ds/CLAUDE.md §3`.
- **Currently VIOLATED** — A must fix: `ai-registry.js:315` falls back to `resolveProvider('claude')`;
  `:343` `complete()` hardpins `'claude'`; the AIEngine dead `typeof provider` guard (~16 sites, always falls
  to claude); the foundry `window.claude` liveness check. `LIVE-INSTRUMENT.md §1 table` row 4 (220), §honest-
  gaps (461–463), §Build-groups G-L1 (510–511) [A1/A5/A16 Observed]. Observed directly this read at
  `ai-registry.js:299,315,343`.

### A-7 · Deep-linked / single-source (governs A's config + any index A builds)
- **Hard law 2 + lens 5** (`LIVE-INSTRUMENT.md` 420–421, 27–30): stored things *reference* their source, never
  copy, so growth never stales. The semantic icon index A's `embed` role feeds (G-L2) must be **keyed by icon
  id, deep-linked to `CV_ICONS.facets` (never copied)**, re-run on `CV_ICONS.add`. `§8 fused-direction`
  (341–345); `§Build-groups G-L2` (513–516).
- Design-system's one idea: *"Everything is defined once and referenced everywhere… find the one home, edit
  there, reference from everywhere else."* `claude-ds/CLAUDE.md §0`.

### A-8 · Nothing canonical / fuse-not-choose (the governing stance over A)
- **Lens 1–2** (`LIVE-INSTRUMENT.md`, 13–21): nothing is final/canonical/done; duplications are expected and
  valuable; *"find every version of each capability and fuse the best parts of all into one. Never pick a
  winner."* A must **fuse** the several AI touch-points (see below), not pick one.
- `00-the-thinking.md §1` (37–40, `[Tim's word]`): *"Nothing is canonical; the job is fusion… identify every
  version and fuse the best of all into one; never pick a winner."*

### A-9 · The AI touch-points A must FUSE (all "already the AI layer under another name")
The plans name the parallel AI/cognition surfaces that A converges to one `CV_AI.execute()`-driven path:
- `CV_AI` registry (6 providers, `resolveProvider` + `CV_HOST` delegation) — the plumbing. `§1 table` (217).
- Company `run_role`/`models_for_role`/`resolve_model` (built-but-dormant) — the true role-resolver A mirrors.
  `§1 table` (219) [A2/A8].
- Browser fan-out idioms — `Build.jsx` plan→specialists→composer, `generateCandidatesStream`, ViConsole's
  `interpret`→`{say,actions,proposals,options}`, `CV_TYPES_VI.proposeType`. *"converge on one
  `CV_AI.execute()` structured-output path resolving to those roles."* `§2` (238–249).
- The two-bridge split **CV_AI vs WS_AI** must collapse to one: *"Everything routes through `CV_AI.execute()`
  (one bridge, not WS_AI vs CV_AI)."* `§3 fused-direction` (265).

### A-10 · The dual-authoring face of A — ALREADY SEEDED by C (existing, not hypothetical)
This is A's second half: the AI has **equal tools to the user** to read AND author the language, through the
**same** API, registered in `CV_AI`.
- **CRITERIA-G0.4** (`CRITERIA.md`, 39–40): *"the SAME `author` API is reachable by BOTH the user (interface
  panel, G7) and the integrated AI (a Company authoring capability) — one API, two faces."*
- **CRITERIA-G8.3** (`CRITERIA.md`, 149–150): *"the authoring + read-out are registered in the AI registry
  (`CV_AI`) as capabilities, so the integrated AI can read the language in-context AND configure it — the same
  `CV_MEANING.author` (G0.4), exposed as an AI capability + a user panel (the DUAL surface)."*
- **GUIDE-G0** (`GUIDE.md`, 51–53): *"Expose authoring two ways from the ONE API… so the AI can read the
  language in-context AND configure it. Both call the same `CV_MEANING.author`."*
- **Already built (C):** `app/ai/ai-glyphic-language.js` registers `glyphic.author`, `glyphic.author-relation`,
  `glyphic.author-gloss`, `glyphic.read` as `CV_AI` capabilities (family `language`, `provider:null`, wrapping
  the loud-fail `CV_MEANING.author.*`). Its header: *"the integrated AI has EQUAL tools to the user… One
  capability = a DUAL surface by construction."* Observed `ai-glyphic-language.js` (head). **A extends this
  embryo — it does not invent the dual surface.**

### A-11 · The `CV_GLYPHGRAPH_SESSION` shared-selection substrate — the substrate C built for A to consume
This is A's **most concrete integration contract** — the collaborative surface the AI reads/acts on.
- Built in `system/glyphgraph-generator.html:173-176` (Observed, read directly):
  ```js
  // C · the SHARED-SELECTION SUBSTRATE — the collaborative surface the AI reads/acts on (wired in A).
  // The generator owns it; a future AI capability reads window.CV_GLYPHGRAPH_SESSION.selection + .graph.
  window.CV_GLYPHGRAPH_SESSION = { graph, selection: [], get selected(){…}, subscribers: [] };
  function syncSession(){ var S=window.CV_GLYPHGRAPH_SESSION; S.graph=graph; S.selection=selArr();
                          S.subscribers.forEach(fn => fn(S)); }
  ```
- Contract for A: read `.graph` (the live `CVGraph{type:'glyphgraph'}`), `.selection` (ids) / `.selected`
  (resolved nodes), and **subscribe** by pushing to `.subscribers[]` (called on every redraw via `syncSession`).
  The comment **names A as the consumer** ("wired in A"). C also implemented the spatial-theorem pin (a
  manual drag/insert writes a frozen x/y; auto-placement never overrides — `glyphgraph-generator.html:179`),
  which A's mutation ops must honour.

### A-12 · mode / app / panel is NON-EXCLUSIVE (how A composes at the presence layer)
- **Hard law 8 + lens 8** (`LIVE-INSTRUMENT.md`, 431–432, 36): build as a MODE (`modes/glyphgraph.py`),
  runnable as an APP, embeddable as a PANEL in the RHM surface — hold all three, force none. A's role-resolution
  ties into the mode/loadout spine: `§7 fused-direction` (324–330) — glyphgraph is a presence MODE with
  `consent:'act'`, a `services.json glyphgraph` combo (`extends: interaction`), the extract role files loaded
  by `set_mode('glyphgraph')`.

---

## (b) The LAWS A must obey

The 8 hard laws (`LIVE-INSTRUMENT.md §hard-laws`, 414–439), the design-system non-negotiables
(`claude-ds/CLAUDE.md §3`), and the three new machine-enforceable gate detectors. A is directly bound by all;
the starred ones are A's own.

1. **One IR** — every render surface projects the one `CVGraph` IR; no fifth parallel strand (`UNIFICATION.md §4`).
2. **Deep-linked storage** — reference type/facets/meaning/sockets, never copy; triples at most the extract
   wire-format; the stored/rendered unit is a full typed glyphic.
3. **Colour via `CV_AXES → var(--token)`, never hex** — kill the three-colour-map drift + the encodings hex
   short-circuit.
4. ⭐ **Loud-fail** — unknown facet/value/**provider**/runtime/type → throw; resolve-miss → foundry-or-Notice
   + recorded Gap; **never a silent fallback to claude** (A's exact anti-pattern to remove).
5. **Render-from-data, no per-type branch** — one generic node-type + one generic edge-type via
   `CV_GLYPHIC.render`; a new entity type just renders.
6. ⭐ **Role-resolution, never a pinned model** — capabilities declare a role; one config maps role→provider;
   the Company fleet resolves the model; assert `satisfied`. **(This law IS A.)**
7. **A node is a full typed glyphic** (slots/sockets/triggers/values/tags/state/click-actions per
   `glyphic-type.js`), validated by `CV_GLYPHGRAPH.validateGlyphgraph` before render.
8. **mode/app/panel non-exclusive.**

**Design-system non-negotiables** (`claude-ds/CLAUDE.md §3`, reinforcing the above for A specifically):
- **No second home for any value** — no parallel type/atom/archetype/**capability** lists; one concept = one
  entry. (A must not spawn a parallel provider/role list; extend `CV_AI`.)
- **The interface is a projection of the registries** — UI reads from `CV_REGISTRY`/`CV_AI`; not a parallel
  structure. (A's dual authoring panel is a projection of the `CV_AI` capabilities.)
- **Audit before you touch** — grep the existing home first; reconcile/extend, don't duplicate.
- **Route model calls through `CV_AI`** — *"never `window.claude.complete` and never
  `window.cvOpenAI.generateImage` directly."* `claude-ds/CLAUDE.md §2`.

**The three new gate detectors** (`LIVE-INSTRUMENT.md §hard-laws`, 434–439) — machine-enforcement A partly
triggers/benefits from:
- ⭐ **provider-literal** — a `'claude'`/provider-id string passed to `resolveProvider`/`provider:` → flag.
  (This detector exists **for A** — it catches the pins A must dissolve, and prevents regression.)
- **typed-list** — a large hand-written `name→{…}` map that should be a generative/file-discovered registry.
- **render-branch** — a `switch`/`if` on `.type`/`.kind` in a render fn.
- Note: today's design-lint catches **colour only** — blind to all three ([A5/A11]). Registering these is
  build-group **G-L10**.

**Method laws** (`00-the-thinking.md §1`) A's build must follow: trust-nothing/structure-the-catch (verify by
use, coverage-diff, adversarial reader); source→atoms→views; deep-linked single-source incl. storage; unify
INTO the Company; nothing canonical / fuse.

---

## (c) What the plans already SAY about A / G-L1 / the fusion (quoted, with refs)

### On the provider role-layer (G-L1 = A)
> **Fused direction** — *"a **role-resolution layer** in `CV_AI` — capabilities declare a *role*
> (`extract-entities`, `compose-graph`, `embed`, `text`), one `ROLE_PROVIDERS` config maps role→provider id,
> the single place an id is pinned. `execute()`'s line 299 + the two fallbacks route through it; the ~27 caps
> drop `provider:'claude'`. Flipping the whole DS to Company-local = one edit. The Company fleet enters as a
> `company-http` runtime (modelled on `openai.js` direct-fetch) hitting the bridge `/api/cognition/run_role`
> (role-resolved, json_schema structured outputs) — **NOT** the `CV_HOST_NATIVE` export path (vaporware, never
> injected)… Assert `satisfied`. This realises `cognition-is-role-resolved` in `CV_AI`, mirroring
> `run_role`/`models_for_role`."* — `LIVE-INSTRUMENT.md §1 fused-direction` (223–232).

> **G-L1 · Provider role-layer + `company-http` runtime.** *Design-side + cross-into-company.* `ROLE_PROVIDERS`
> + `defaultProvider(role)` in `CV_AI`; route the ~5 literal sites + ~27 caps + the dead `typeof provider`
> guard + the foundry `window.claude` check through it; add `cvCompany`/`company-http` reaching the bridge
> `/api/cognition/run_role`. Verify the CORS fact." — `LIVE-INSTRUMENT.md §Build groups` (509–512).

> **Hard law 6** — *"Role-resolution, never a pinned model. Capabilities declare a role; one config maps
> role→provider; the Company fleet resolves the model. Assert `satisfied`, not a non-empty model."* — 428.

### On the embedder / embed role (G-L2, the provider A also lights up)
> *"an `embed` provider (role-resolved) → a re-runnable cosine index keyed by icon id, deep-linked to
> `CV_ICONS.facets` (never copied), re-run on `CV_ICONS.add`… a tuned threshold gates generate-on-miss; lexical
> stays the floor."* — `LIVE-INSTRUMENT.md §8 fused-direction` (341–345).

> **G-L2 · Semantic icon index + generate-on-miss.** *Design-side + cross-into-company (embedder).* An `embed`
> provider + a re-runnable cosine index keyed by icon id…" — `§Build groups` (513–516).

### On the dual-authoring fusion (CRITERIA-G0.4 / G8.3, GUIDE-G0)
> *"Equal tools for user AND AI. Expose authoring two ways from the ONE API: an interface panel… AND an AI path
> (a Company MCP capability / the existing config-dials mechanism) so the AI can read the language in-context
> AND configure it. Both call the same `CV_MEANING.author`."* — `GUIDE.md §G0` (51–53).

> *"the SAME `author` API is reachable by BOTH the user… and the integrated AI (a Company authoring
> capability) — one API, two faces; the AI can read the language in-context AND configure it."* —
> `CRITERIA.md §G0.4` (39–40).

### On the relational whole (why A sits where it does)
> *"→ which the system can **build/describe/explain by talking** (the conversational glyphgraph) → driven by
> **local models** resolved by **role**, entered as a **mode/loadout** →…"* — `00-the-thinking.md §2` (52–57).

### On the extract fleet reality (constrains A's role-serving assumptions)
> *"the realistic operating point is a burst of ~10-14 short, think-off, schema-constrained roles at each pause
> — NOT an always-on fleet… the brain-KV is shared with the main reply; the knee collapses to ~1-5
> mid-deep-reply. Per-utterance bursts, vLLM continuous-batches them."* — `LIVE-INSTRUMENT.md §EXTRACT honest-gap`
> (90–93) [A2]. A's role-resolution must serve *burst-at-pause*, not a standing swarm; a higher-util swarm-brain
> config is a **GPU-reconfig lever (needs-tim)**, not free (§honest-gaps, 458–460).

### ⚠️ ANCHOR is SUPERSEDED — do not treat its specifics as decisions
`LIVE-INSTRUMENT.md` (4–7) explicitly supersedes the earlier framing. `ANCHOR.md §4` items are marked
`(my-idea)`/`verify`, not decisions: the **reactflow** canvas pick and the **pplx ~0.6b** embedder are
"my-idea"; treat them as candidates, not settled. The role-resolution idea in `ANCHOR.md §4/§7` (72–74) is
grounded and carries forward; the specific library/embedder choices do NOT.

---

## (d) Open decisions the plans FLAG that A touches (surfaced, not resolved)

These are the plans' own open questions where A intersects. A must carry them as open (fuse-not-choose /
verify-first), not silently pick.

### D-1 ⚠️ (verify-first, gates the whole browser→Company wire) — the CORS fact
> *"One fact to verify (not a design choice): does bridge `:8770` send cross-origin CORS to a Vite surface, or
> is the surface served same-origin (the canvas/app way)? Gates the browser→Company wire."* —
> `LIVE-INSTRUMENT.md §open-decisions #5` (499–500); also §1 fused-direction "single open fact" (231–232) and
> G-L1 "Verify the CORS fact" (512). **Note the port discrepancy in the plans: `§1` says the bridge is `:8770`;
> `§open-decisions #5` and §honest-gaps also say `:8770`; the design-charter/services reference `:8774`
> (page-face). A must confirm the actual bridge origin/port + CORS empirically before wiring `company-http`.**

### D-2 — the embedder endpoint for the `embed` role (three candidates, unresolved)
The plans reference **three** embedder endpoints; A's `embed` role must resolve to one, but the plans do not
pick:
- **pplx-embed-v1-0.6b** — 1024-dim, INT8-native, MIT, *on disk NOT served* — "the *right* small icon-lookup
  embedder but needs serving." `LIVE-INSTRUMENT.md §8 table` (338) [A2/A4].
- **pplx-embed-context-v1-4b @ :8007** — 2560-dim, *served* — "does it now." Same row (338).
- **BGE-M3 @ :8001** — already used by `symbols.py`'s `semantically_nearest[]` via `nodes/embed`+`nodes/retrieve`
  ("degrades-with-warning when :8001 is down"). `design/CLAUDE.md` (symbols.py X11 description). *(Cross-doc:
  this endpoint is not in LIVE-INSTRUMENT's embedder row but is the live embedder the design corpus already
  reaches — surface it as a fusion candidate, don't drop it.)*
A touches this as the `embed` provider record; **open decision** = which endpoint the role defaults to
(serve the 0.6b · use the served 4b · reuse the BGE-M3 the corpus already uses). Fuse-not-choose until decided.

### D-3 — how the fused conversation surface talks to the Company (cross-repo seam)
> *"it must send transcribed-intent to / receive graph-deltas from the Company surface, not be a closed
> browser-only chat."* — `LIVE-INSTRUMENT.md §3 fused-direction` (266–267). A's `company-http` runtime is the
> plumbing; whether the Company **drives and pushes graph-deltas** vs the **browser polls/requests** is an open
> shape (`ANCHOR.md §8`, 100–102, superseded framing but the question stands).

### D-4 — mode/app/panel composition (A ties into the mode/loadout spine)
> *"How the glyphgraph composes as a MODE (with loadouts), an APP, and a PANEL in the RHM surface —
> non-exclusive (lens 8). The `consent` axis governs whether the loop acts vs surfaces."* —
> `LIVE-INSTRUMENT.md §open-decisions #4` (497–498). A's role-serving is entered via `set_mode('glyphgraph')`;
> the wrinkles for Tim (`§7 fused-direction`, 329–330): use `loadout_class` not the partial `brain_config`;
> `resolve_model` is dormant (live resolution still flows through `roles.resolve_binding`); assert `satisfied`.

### D-5 — CV_MODE vs modes_registry (reconcile, never merge)
> *"CV_MODE (canvas click-dial) and modes_registry (RHM presence) are different axes sharing one registry
> mechanism — reconcile, the instrument needs BOTH, never merge."* — `LIVE-INSTRUMENT.md §7 fused-direction`
> (327–329). A touches this only where role-loadout entry meets the canvas interaction-dial; hold both.

**Decisions the plans have RESOLVED that A does NOT reopen** (so A treats as fixed): `company-http` not
`CV_HOST_NATIVE` (A-4); Company-default direction (A-3); role-resolution over pins (A-2); the GOLD-PRIMARY WARM
palette as centre (`§open-decisions #3`, 494–496 — not an A concern but a standing centre); deep-linked storage
model shape as "bring-background not binary" (`§open-decisions #2`, 489–493 — A's `embed` index obeys the
deep-link half).

---

## Cross-cutting notes for the A designer (carried tags)

- **Trust-map** (`00-the-thinking.md §4`): findings (AREA-1..20) are closest-to-source; `LIVE-INSTRUMENT.md` is
  a **lossy synthesis/view** over them; ANCHOR is superseded. Where a claim matters, this brief cites the doc's
  own Observed/Inferred tag. A design that depends on a specific fact should re-verify against source (the
  READ-2 code-inventory stream will do this for the code side).
- **A is stated in BOTH plan-views** — provider/role side (LIVE-INSTRUMENT + hard-law 6 + G-L1/G-L2) AND
  dual-authoring side (CRITERIA-G0.4/G8.3 + GUIDE-G0, already seeded by C). Design A to satisfy both faces.
- **A's most concrete existing contract** is `window.CV_GLYPHGRAPH_SESSION` (`glyphgraph-generator.html:174-176`)
  — the read/subscribe/act surface C named "wired in A." Start the integration there.

---

### 3-line summary
A (the AI/Company fusion, = build-group **G-L1** + its dual-authoring face **CRITERIA-G0.4/G8.3**) is heavily
pre-constrained: a **role-resolution layer in `CV_AI`, Company-default, one `ROLE_PROVIDERS` config**, the fleet
entering as a **`company-http` runtime → bridge `/api/cognition/run_role`** (NOT `CV_HOST_NATIVE`), obeying the
8 hard laws (esp. **loud-fail / role-not-pin**) + the design-system non-negotiables, with the dual authoring
**already seeded by C** in `ai-glyphic-language.js` and the collaborative substrate **`CV_GLYPHGRAPH_SESSION`**
built for A to consume. Open where A must NOT pick: the **CORS/bridge-origin fact** (verify-first, note the
:8770/:8774 discrepancy), the **embed-role endpoint** (0.6b-unserved · 4b@:8007 · BGE-M3@:8001), the
**cross-repo delta-flow shape**, and **mode/app/panel + CV_MODE-vs-modes_registry reconcile**. The task's "G-L1"
is **LIVE-INSTRUMENT-G1 (provider role-layer), NOT CRITERIA-G1 (lexicon)** — the two G-sequences collide and are
kept distinct throughout.

Path: `/home/tim/company/design/claude-ds/analysis/glyphic-language/A-fusion/reads/READ-1-plans.md`
