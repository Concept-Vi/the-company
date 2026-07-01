# AREA 5 — Resolution / Deep-link / No-staleness discipline (the rigor area)

> I am the skeptic. My job: try to BREAK §5's governing law — *everything generative / deep-linked /
> resolved from a single source, NO hardcoded backfill, NO hardcoded provider, NO per-type render
> branch* — by finding exactly where the live layer (icon-tag backfill · provider wiring · reactflow
> renderer · meaning lookup · extract→resolve pipeline) **would** hardcode/stale, and naming the
> resolution pattern that holds the line. Marks: **Observed (file:line)** = read in code · **Inferred**
> = a naive build's predicted behaviour (not yet written) · **External** · **My-idea**.
> Two repos: design system `/home/tim/company/design/claude-ds/`, machinery `/home/tim/company/design/_system/`,
> Company `/home/tim/company/`.

---

## 0 · TL;DR — the three legs of §5, scored against the real code

§5 names three hardcode-legs. Here is where each ALREADY stands and where the live build breaks it:

| §5 leg | Live-layer part | Current code reality | Verdict |
|---|---|---|---|
| **no hardcoded backfill** | icon-tag backfill | tags are a **frozen per-icon literal** (`CV_ICONS.facets`, cv-icons.js:273-418) + **lexical** substring search (cv-icons.js:430). The §5 "embed→derive, re-runs as icons grow" pass **does not exist.** | **ALREADY VIOLATED** — the staleness bug is in the code today, not hypothetical |
| **no hardcoded provider** | provider wiring | `resolveProvider('claude')` literal at **ai-registry.js:315 & :343**; `provider:'claude'` at **ai-glyphic.js:61**. The registry is right; the *default* is a literal. | **ONE literal to dissolve** — the un-stale seam (`CV_HOST`) already exists |
| **no per-type render branch** | reactflow renderer | nothing built yet; the precedent to copy is `NodeShape.tsx` = "**the one generic node shape**" + Palette "**fills itself from the live registry**" (addresses.json `ui://canvas`, `ui://rail/palette`) | **NOT YET BUILT** — name the trap before it lands |
| (within "resolved from a single source") | meaning lookup | `CV_MEANING.encodings` is a clean register/resolve registry (cv-meaning.js:211-215, fail-loud) — the GOOD precedent | follow it |
| (within "resolved from a single source") | extract→resolve roles | the Company already resolves cognition **by role, never a pinned model** (`run_role`, cognition.py:303; `role_registry()`, cognition.py:114) | follow it; the trap is the browser side pinning a model |

**The honest gate finding (the task asked explicitly):** `check.py --target … --fail-on` (the design-lint
gate, check.py:101-167) scans `.tsx/.css` for **hex/rgba/px only** (check.py:28-30, 114-120). It would
**NOT** catch `resolveProvider('claude')`, the `CV_ICONS.facets` literal, or a `switch(node.type)` render
branch. **As-is the gate does not cover any of the live-layer staleness risks.** Holding the line means
*registering new mechanisms* in `mechanisms.json` — detailed in §7. (Observed: check.py:28-30, 101-167.)

---

## 1 · The resolution patterns the live layer MUST copy (inventory, with evidence)

These are the system's existing anti-staleness machinery. Each is a *shape* the live layer reuses.

### P1 · The ONE resolver, scheme-dispatched, fail-loud on unknown — `resolve_address`
**Observed** (`runtime/cognition.py:1100-1218`, `contracts/address.py:145-186`). `resolve_address(store, addr)`
dispatches by `contracts.address.scheme(addr)` to per-scheme resolvers. The law, verbatim in the docstring
(cognition.py:1127-1130): *"ANY OTHER scheme … RAISES fail-loud … NEVER a silent empty. This RAISE is the
extensible seam: when a resolver exists, add a dispatch branch here."* The `SCHEMES`
set (address.py:145 — 21 entries at this revision and growing) registers each scheme; each new one (`skill://`, `context://`, `board://`, `clone://`, `decision://`,
`vi-vision://` …) was added **purely additively** — a new dispatch branch, never a parallel resolver. The
key property: an address is a *pointer to a single home*; the resolver follows it live; an unresolvable
address fails loud instead of returning a stale/fabricated value. **The live layer's glyphic resolution
(noun → glyphic) must be one such resolver, not a lookup table.**

### P2 · File-discovered registries — *add a row = drop a file, zero code edit*
**Observed** (`runtime/relation_types.py:11-16, 136-196`). The relation-type registry is `os.listdir →
importlib`, `id == filename` (fail-loud otherwise, line 114-117), unknown field → RAISE (118-122). Its own
docstring states the law (lines 11-16): *"add-a-row = a FILE, no code edit … NOT `RELATION_TYPES={...}`."*
It explicitly mirrors `RoleRegistry/ProjectionRegistry/NodeRegistry` — **the ONE registry mechanism**, copied
standalone. **This is the antidote to every hardcoded list in the live layer** (the icon taxonomy, the
provider list, the relation→edge vocabulary): the set is discovered, never a literal.

### P3 · Deep-link to source + fail-loud on drift — `refcheck.py` / `symbols.py` / `codeedges.py`
**Observed.** The corpus never copies code; it holds `code:` **refs** that resolve READ-ONLY against
`~/company` and report DRIFT:
- `refcheck.py` (forward: ref → does it still land on its symbol?) — resolves every `code:` in
  `register.json` + `addresses.json`, fail-loud on a malformed registry (refcheck.py:273-286), emits a
  repair worklist (refcheck.py:446-515).
- `symbols.py` (reverse: symbol → who references it) — `code://<file-stem>/<symbol>` ids
  (symbols.py:96-100); `resolves:false` IS the drift signal (symbols.py:171-173).
- `codeedges.py` — symbol→symbol dependency graph, same `code://` ids (mechanisms.json:22-29).

The property: meaning is **deep-linked, not copied**, so when the source moves the link drifts *loudly*
and the keeper repairs the **one** ref. **The live layer's icon tags + glyphic meaning must be deep-linked
/ re-derived this way — not snapshotted at author time** (see §2, §5).

### P4 · Render-from-data, ONE generic renderer — the `ui://` registry + NodeShape
**Observed** (`design/_system/addresses.json`). `ui://canvas` code = `canvas/app/src/NodeShape.tsx:NodeShapeUtil`,
howto: *"the board is tldraw driven by **NodeShape.tsx (the one generic node shape)**."* `ui://rail/palette`
howto: *"the rack **fills itself from the live registry (/object_info)** — adding a node-type
(`nodes/<name>.py`) makes a new block appear here automatically, **no palette code**."* This is the
render-from-data law made concrete: **one generic node component reads facets from data; new types light up
with zero render edits.** **The reactflow renderer must be exactly this** (see §4).

### P5 · Recognise-and-derive over hardcode — `check.py` + the embed/retrieve reuse in `symbols.py`
**Observed.** `check.py` finds hardcoded literals and proposes the token they should reference
(check.py:38-57: `matches_token` → use `var(--x)`; recurring + no token → candidate new token). And
`symbols.py` X11 (symbols.py:235-309) shows the **embed→derive** pattern done right: each symbol's
representative text is embedded via `nodes/embed` (BGE-M3 @ :8001) and ranked via `nodes/retrieve` — *reused,
never reimplemented* (symbols.py:252-262) — **degrade-with-warning** when the embedder is down (symbols.py:283-302),
never a fabricated nearest. **This is the exact mechanism the icon-tag backfill needs** (§2): embed the noun,
rank the icons, re-run as icons grow — not a frozen tag list.

---

## 2 · LIVE PART A — the icon-tag backfill (the headline §5 example — ALREADY VIOLATED)

§5 (verbatim): *"icon tags are NOT a typed list — they're a generative pass [embed → derive] that re-runs
as icons are added, with meaning deep-linked to its source, not copied."*

### Where it hardcodes / stales — and the proof it's the CURRENT code, not a hypothetical
**Observed.** `CV_ICONS.facets` (cv-icons.js:273-418) is **a hand-written literal map**
`name → {domain, kind, tags[]}` — e.g. `'house':{domain:'property',kind:'object',tags:['home','listing','residence']}`.
This IS "a typed list" — exactly what §5 forbids. Three concrete staleness facts:

1. **Tags are authored ONCE and frozen.** Trace the write path (verified): `glyphic.save` (ai-glyphic.js:80)
   → `CV_ICONS.add` (cv-icons.js:498). `add` writes `data[rec.id]=rec.svg` (line 506) and
   `facets[rec.id]={domain,kind,tags,...}` from `rec.facets` (lines 507-515). Those `tags` come from the
   **LLM at generation time** (ai-glyphic.js:41 puts `"tags":["..."]` in the prompt). **So an icon's tags
   are whatever words the model happened to write at save time — never re-derived.** *(Good news, also
   verified: `add` writes into the SAME `data`/`facets` the readers use — there is NO parallel store; a saved
   icon IS immediately in the registry. The single-source write/read is correct. The defect is that the
   meaning is a frozen snapshot, not a derivation.)*

2. **Lookup is LEXICAL, not semantic.** `CV_ICONS.search` (cv-icons.js:430-439) is `String.includes`
   substring matching over name/domain/kind/tags. There is **no embedder, no `embed→derive`, no
   "re-runs as icons are added".** The anchor §4 *(my-idea)* "embed the noun → nearest tagged icon" and §5's
   generative pass **do not exist in the code.** So the live pipeline's RESOLVE step (noun → symbol) has no
   semantic path today.

3. **The taxonomy is a closed literal + silent coercion.** `taxonomy` (cv-icons.js:246) is a hardcoded
   category list; `add` defaults a missing facet to `domain:'feature', kind:'object'` (cv-icons.js:509-510)
   — a **silent coercion to a hardcoded default**, which also breaks §3's loud-fail law (it should surface
   "this icon's domain couldn't be derived", not quietly stamp `feature`).

**Why this is the make-or-break:** add 50 nouns from a conversation, 30 trigger `glyphic.generate`, each
saves tags the LLM wrote in isolation. At 500 icons the lookup is captive to inconsistent author-time word
choices, with no pass that re-derives tags against the whole grown set. **This is the precise "un-hardcoding
a grown system later is brutal" Tim warned about — and it's already growing.** (Inferred: the scaling
consequence; Observed: the frozen-literal mechanism.)

### The resolution pattern that holds the line (My-idea, grounded in P3 + P5)
Make icon tags a **derived projection**, exactly like `symbols.py:semantically_nearest[]`:
- **Embed-and-derive (P5).** A generative pass embeds each icon's representative text (svg-domain + name +
  description) via the **existing `nodes/embed`** path — *reuse, do not reimplement* (the symbols.py:252-262
  precedent). Tags/nearest are a *computed field*, re-runnable. Adding an icon re-runs the pass; the meaning
  is never a frozen hand-string.
- **Resolve noun→glyphic by cosine (P1+P5).** The RESOLVE step embeds the noun and ranks icons via the
  existing `nodes/retrieve` cosine path (symbols.py:304-308). Below threshold → `glyphic.generate` (the
  foundry). This is "embed → nearest → generate-on-miss" — the anchor §3/§4 move, built on machinery that
  exists.
- **Deep-link, don't copy (P3).** An icon's `domain/kind` should *resolve* from its facets via the taxonomy
  registry, and the taxonomy itself should be **file-discovered (P2)**, not the closed literal at line 246 —
  so a new domain is a registered row, not a code edit. Missing domain → fail loud (kill the silent `'feature'`
  default at line 509).
- **Degrade-with-warning, never fabricate (Observed precedent, symbols.py:283-302).** :8001 down → skip the
  semantic field with a loud warning, never a fabricated nearest. The live layer must inherit this exactly,
  because it runs against the same embedder.

---

## 3 · LIVE PART B — the provider wiring (ONE literal to dissolve; the seam already exists)

§5 (verbatim): *"NO hardcoded provider."*

### Where it hardcodes / stales
**Observed.** The CV_AI registry is *structurally* right — providers are registered entries, resolved by id
(`resolveProvider`, ai-registry.js:198-238), fail-loud if a named runtime is absent (lines 200, 205, 237 —
honours §3 loud-fail). The break is the **default**:
- `ai-registry.js:315` — `(provider || resolveProvider('claude')).complete(...)` — the build/parse path
  resolves the **literal `'claude'`** when a capability declares no provider.
- `ai-registry.js:343` — `complete(promptOrOpts){ return resolveProvider('claude').complete(...) }` — the
  one-off completion endpoint hardcodes `'claude'`.
- `ai-glyphic.js:61` — `glyphic.generate` declares `provider:'claude'` literally.

**Why it stales:** §3 already mandates routing through CV_AI, so the *plumbing* won't stale — but the
**identity of the default brain is pinned to a string**. The live layer's whole premise (anchor §3, §7) is
the Company's **local fleet** (chat-4b-fp8, etc.) as the concurrent extract layer. With `'claude'` hardwired
as the fallback, every capability that doesn't *explicitly* name a provider silently routes to claude — so
"swap the default brain" becomes a hunt-and-replace across consumers, the exact anti-pattern. (Inferred:
the consequence; Observed: the three literals.)

### The resolution pattern that holds the line — resolve the DEFAULT by ROLE (My-idea + Observed seam)
The fix is small and the seam already exists — frame it as *resolve the default*, **not** "build a provider
abstraction" (that would misread the code):
- **The plug is already there.** `resolveProvider` already delegates any unknown runtime kind to
  `window.CV_HOST.resolveProviderRuntime(p)` (ai-registry.js:229-237) — *"native/MCP model endpoints …
  the AI catalogue can name providers it doesn't itself know how to reach."* **The Company local fleet
  registers as providers whose runtime CV_HOST binds over HTTP.** No new mechanism — just registered rows
  (P2) + the existing host delegation.
- **Kill the literal: a `default-brain` ROLE, not `'claude'`.** Mirror the Company's
  **cognition-is-role-resolved** law: `run_role` (cognition.py:303) and `role_registry()` (cognition.py:114)
  resolve a *role* (extract-entities, compose-graph) to a model from its needs — *"NOTHING static … never a
  hardcoded constant"* (cognition.py:188). On the browser side, the two `resolveProvider('claude')` calls
  (ai-registry.js:315,343) and `provider:'claude'` (ai-glyphic.js:61) should resolve a **registered default**
  (e.g. a `provider.default` alias / a `behaviour`-style role lookup) — one home, swap once. (The anchor's
  *(my-idea)* "providers resolved by role/id" is exactly this; I'm grounding it on the role precedent.)
- **Fail loud if the default is unset** (§3) — never silently fall back to claude. If no default-brain is
  registered, throw with the registered-provider list (the existing pattern at ai-registry.js:200).

---

## 4 · LIVE PART C — the reactflow renderer (the "no per-type render branch" leg)

§5 (verbatim): *"NO per-type render branch."*

### Where it WOULD hardcode (Inferred — not yet built)
The naive reactflow custom-node will branch on the thing's type:
```js
// NAIVE (the trap) — Inferred prediction of an un-disciplined build
function GlyphicNode({ data }) {
  switch (data.kind) {                       // ← per-type branch = §5 violation
    case 'person': return <PersonGlyph .../>;
    case 'property': return <HouseGlyph .../>;
    default: return <GenericGlyph/>;         // ← silent default = §3 violation
  }
}
```
Every new noun-type/domain then needs a render edit — the system stales as it grows. A second trap: a
**hardcoded nodeTypes map** (`{ glyphic: GlyphicNode, edgeLabel: ... }`) that grows by code edit.

### The resolution pattern that holds the line — ONE generic node, facets resolved from data (P4)
**Observed precedent to copy verbatim:** `addresses.json` `ui://canvas` → `NodeShape.tsx:NodeShapeUtil` is
*"the one generic node shape"* and `ui://rail/palette` *"fills itself from the live registry … no palette
code."* The reactflow node must be the same:
- **One `GlyphicNode` component** that takes a glyphic spec (form/fill/colour/texture/symbol/edges) and
  renders it via the engine's `CV_GLYPHIC.render` — **no `switch`**. A new domain is new *data* (a facet
  combination), not a new branch. This IS the engine's own design law (CLAUDE.md §1: *"renders through the
  one engine under the axis-dials … inherits the DNA by construction because it has no literals"*).
- **`nodeTypes` is a projection of the registry, not a literal** (mirrors §3 "the interface is a projection
  of the registries"). The custom-node kinds resolve from CV_GLYPHIC/CV_REGISTRY, so registering a glyphic
  archetype makes it renderable with no reactflow edit — the Palette precedent (P4).
- **Edges from relation-types, file-discovered (P2).** The graph's edges must resolve their kind from a
  registry like `relation_types.py` (file-discovered, directed/symmetric per the row — relation_types.py:62),
  NOT a hardcoded edge-style switch. A new edge kind = a dropped file.
- **No silent default node** (§3) — an unrenderable spec fails loud / surfaces a notice, never a quiet
  generic fallback that hides drift.

*(Honest hard-part flagged for the synthesis: reactflow-in-CSP/bundle — the no-script SVG page-face render
[`runtime/page_render.py`] vs the interactive reactflow surface is a real boundary; that's AREA-2/4's
domain, not mine. My claim is only about the render-from-data discipline, which holds regardless of the
bundler.)*

---

## 5 · LIVE PART D — the meaning lookup (follow the good precedent; one drift risk)

### Where it could stale — and the good precedent
**Observed.** `CV_MEANING.encodings` (cv-meaning.js:211-215) is **already a clean register/resolve registry**:
`register(surface, profile)`, `resolve(surface)` fail-loud (`fail('no encoding profile for surface …')`),
`has`, `list`. The data-field→visual-channel grammar is data, not code — the anchor §7 correctly calls it
*"the EXISTING precedent for data-binding."* `CV_MEANING.author` (cv-meaning.js:414+) is fail-loud throughout
(no empty meaning, no unknown facet — lines 416-423). **This is the shape the icon-tag pass (§2) should
have had.** Follow it.

The one drift risk (Inferred): if the live pipeline's RESOLVE step (state → fill/colour, anchor §3) reads
meaning by **copying** an encoding profile into the node spec rather than holding a **reference** to the
encoding surface, the node stales when the profile changes. The pattern: a live glyphic node should carry a
*reference* to its encoding (`resolve(surface)` at render time), not a snapshot — the CLAUDE.md §0 prime
directive ("consumers hold references, never copies").

---

## 6 · LIVE PART E — the extract→resolve pipeline (resolve-by-role, never a pinned model)

### Where it would hardcode (Inferred) — and the law it must honour
The anchor §3 names the *extraction-vs-judgment* + *cognition-is-role-resolved* laws. The naive break: the
browser-side pipeline pins a model (`chat-4b`, `pplx-embed-context-v1-4b`) by string into the extract/compose
calls. Then the loadout changes (the Company hot-swaps brains — `services.json` declares the FP8/AWQ/9B ladder,
Observed-in-registry) and the pinned strings stale.

### The resolution pattern that holds the line (Observed law)
**Observed.** The Company already does this right: `run_role(role, ctx, …)` (cognition.py:303) resolves a
**role** to a model; `role_registry()` (cognition.py:114) is file-discovered (mirrors the P2 mechanism);
the spike-policy comment states the law outright — *"NOTHING static … never a hardcoded constant. Discovered
fresh each call"* (cognition.py:188). The extract layer's concerns (entities / relations / states /
placement-hints — anchor §3) are **roles**, each resolving to a model from its needs — never a pinned id.
The pplx embedder is **registered (Observed in services.json — not executed by me)**: `embed-pplx` =
`pplx-embed-context-v1-4b`, the combos' notes claim 2560-dim, context-aware, replacing legacy BGE-M3
(services.json combos `xsession`/`instrument`/`fabric`). The anchor §7 asked to verify it exists — it is
declared in the service registry; I did not run it. The live layer must
reach it **by role**, not by hardwiring its name. The browser→Company boundary is HTTP via the `company` MCP
(`run_role`, `models_for_role`); the role resolution stays server-side where the loadout truth lives.

---

## 7 · Can the design-system's OWN hardcode-detector gate this? (the task's direct question)

**Observed — honest answer: NO, not as-is.** `check.py` design-lint (`--target … --fail-on`, check.py:101-167)
scans `.tsx/.css` for **hex/rgba** colour literals (+px with `--include-px`) — check.py:28-30, 114-120. It is
a *token*-drift gate. It will **not** flag:
- `resolveProvider('claude')` / `provider:'claude'` (a string literal, not a colour),
- the `CV_ICONS.facets` typed list (a data literal),
- a `switch(node.type)` render branch (a control-flow literal).

`refcheck.py`/`symbols.py` catch *code-ref* drift, not *provider/render* hardcoding. So **the existing
machine gate is blind to every live-layer staleness risk.**

### Holding the line = register NEW mechanisms (My-idea, grounded in mechanisms.json:1-31, the extend-by-registration law)
`mechanisms.json` is explicitly *"extend-by-registration: add a mechanism = add an entry keyed by id."* The
disciplined move is three new structural mechanisms (each a `_system/<x>.py` + `test_<x>.py`, same shape as
`refcheck.py`):
1. **`provider-literal-detector`** — scan `app/**/*.js` for a string literal `'claude'`/`'openai'`/any
   provider id passed to `resolveProvider(...)` or a `provider:` field; the legal form is a registered-id /
   role reference. Fail-on gates the build. (Catches §3-leg.)
2. **`typed-list-detector`** — flag a large hand-written object-literal map that should be a derived/discovered
   registry (the `CV_ICONS.facets` shape: `name → {domain,kind,tags}`); route it to "make this a generative
   pass / file-discovered." (Catches the icon-backfill leg.)
3. **`render-branch-detector`** — flag a `switch`/`if` on `.type`/`.kind`/`.domain` inside a render function
   (the per-type branch §5 forbids), routing to "render-from-data via the one generic node." (Catches the
   render leg.)

These are **Layer-0 structural** (exact, free); the model layer augments later (mechanisms.json:2 pattern) —
e.g. a local model judging "is this default actually role-resolved or a disguised pin." The point: the gate
that holds §5 for the live layer does not exist yet; it is *registered*, exactly as every other check was.

---

## 8 · Summary — the disciplined alternatives, one line each

| Part | Hardcode trap | Resolution pattern (deep-link / file-discovery / embed-derive / resolve-by-role / render-from-data) | Evidence |
|---|---|---|---|
| A · icon tags | frozen per-icon `facets` literal + lexical search (**already live**) | **embed-and-derive** re-runnable pass (reuse `nodes/embed`+`retrieve`); taxonomy **file-discovered**; deep-link domain | cv-icons.js:273-439,498-518; symbols.py:235-309 |
| B · provider | `resolveProvider('claude')` ×2 + `provider:'claude'` | **resolve-by-role** default via existing `CV_HOST` host-delegation seam; fail-loud if unset | ai-registry.js:198-238,315,343; ai-glyphic.js:61; cognition.py:114,188,303 |
| C · reactflow | `switch(node.type)` + hardcoded `nodeTypes` map | **one generic node, facets from data** (the NodeShape/Palette precedent); edges from file-discovered relation-types | addresses.json `ui://canvas`,`ui://rail/palette`; relation_types.py:62 |
| D · meaning | copying an encoding profile into a node (snapshot) | hold a **reference** to `encodings.resolve(surface)` at render time | cv-meaning.js:211-215,414+ |
| E · extract→resolve | pinning `chat-4b`/`pplx…` model strings in the browser | **resolve-by-role** server-side (`run_role`/`role_registry`); reach the fleet by role over the `company` MCP | cognition.py:114,188,303; services.json combos |
| GATE | check.py design-lint catches **colour only** — blind to all five | **register 3 new mechanisms** (provider-literal / typed-list / render-branch detectors), extend-by-registration | check.py:28-30,101-167; mechanisms.json:1-31 |

**The make-or-break, stated plainly:** §5's law is not aspirational for this system — the system is already
resolution-native (P1-P5 are real, verified machinery). The live layer's risk is concentrated in **two
places that already lean the wrong way** (icon tags = a live frozen-literal staleness bug; the `'claude'`
default = a pin) and **two not-yet-built places** (the render branch; browser-side model pinning) where the
disciplined alternative is a *copy of an existing pattern*, not new invention. The gate to enforce it does
not exist yet and must be *registered*, not assumed.
