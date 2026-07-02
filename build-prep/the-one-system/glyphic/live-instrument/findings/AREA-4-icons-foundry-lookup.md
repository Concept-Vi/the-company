# AREA 4 — The Icon System + Foundry + Semantic-Lookup Loop

> Companion to `../ANCHOR.md`. My area: how icons are stored + tagged today, how a **generative**
> tag/meaning backfill would work, the exact wiring for **semantic icon-lookup → generate-on-miss →
> use live**, and how an icon's **meaning should deep-link to its source** rather than be copied.
> Every claim is marked **Observed (file:line)** / **Inferred** / **External-prior-art** / **My-idea**.
> Two repos in scope: the design system `claude-ds/` and the Company `~/company/`.

---

## 0 · The headline reframe (read this first — it rewrites the anchor's premise)

The anchor (§7, §5) says the icon **taxonomy is under-populated** and points at `_ingest/ICON-AUDIT.md`
as the tagging-gap evidence. **Both are stale.** What's actually there:

- **Observed (live, ran a node script over `cv-icons.js`):** `CV_ICONS.data` has **132 symbols**;
  `CV_ICONS.facets` covers **131** of them; **0** faceted symbols have empty `tags`. The *only*
  untagged symbol is `sun-moon`. The taxonomy is **dense**, not sparse. **BUT (Observed, ran):**
  **0 of the 131 built-in facets carry a `name` or `description`** — those fields are written only by
  `CV_ICONS.add` (`:508–514`), i.e. for **vi/user-minted icons only**. A built-in facet is exactly
  `{domain, kind, tags}` (e.g. `building-tall:{domain:'property',kind:'object',tags:['tower',
  'apartment','commercial']}`). **So the authored seed for the 131 built-ins is `id + domain + kind +
  tags` — there is no `name`/`description` to draw on for them.** This matters for §3.3/§4 below.
- **Observed:** `_ingest/ICON-AUDIT.md` **does not exist** in `claude-ds/` (no `_ingest/` dir at all).
  The only surviving trace is one line in `analysis/glyphic-language/SYNTHESIS.md:105` — *"symbol
  taxonomy is a flat list, needs domain/kind/tags facets (ICON-AUDIT flagged)"* — which has **already
  been done** (the facets exist; see `cv-icons.js:273–418`). The audit's recommendation landed; the
  audit file is gone.

So the real gap is **not coverage** — it's **provenance**. Every tag, every domain/kind assignment,
and the symbol→word gloss is a **hand-typed literal** in source. That is precisely the failure mode
the governing law (§5) names: *"icon tags are NOT a typed list — they're a generative pass [embed →
derive] that re-runs as icons are added."* Today they ARE a typed list. The law is violated **by
construction**, not by being incomplete. **That is the gold of this area.** And the infrastructure to
make it generative — an embedder reachable from the design system — **does not exist in `claude-ds/`
at all** (proven below). This area is therefore a *build*, not a *backfill*.

---

## 1 · How icons are stored + tagged today (Observed)

### 1.1 The single source: `CV_ICONS`
**Observed — `assets/icons/cv-icons.js`:**

- `CV_ICONS.data` (`:30`) — `{ id → svgBody }`. The body is a raw 24×24 SVG path string (no
  `<svg>` wrapper). 132 entries.
- `CV_ICONS.aliases` (`:198`) — 25 alias→canonical hops (`'price' → 'dollar-circle'`); resolved by
  `CV_ICONS.resolve()` (`:442`), one hop, alias never shadows a real key.
- `CV_ICONS.taxonomy` (`:246`) — the **two-facet classification**: `domains` (13: people, property,
  visualization, document, communication, interface, media, data, commerce, place, action, system,
  feature) and `kinds` (4: object, action, state, concept). Each has `{label, desc}`. This is the
  *category vocabulary*; it is the single source the explorer + `CV_GLYPHIC` read (the comment at
  `:238–243` asserts neither keeps its own list).
- `CV_ICONS.facets` (`:273`) — **the one home for each symbol's meaning**: `id → { domain, kind,
  tags[], (name, description, provenance) }`. `brand:true` flags the customer-facing set. This is
  what `search()` and the Glyphic registry read.
- `CV_ICONS.search(q)` (`:430`) — substring match across name, domain id, domain label, kind, and
  tags. **Purely lexical** — no embedding, no fuzzy, no synonyms beyond hand-listed `tags`/`aliases`.
- `CV_ICONS.add(rec)` (`:498`) — **the write path.** Validates against `CV_GLYPHIC.validateSymbol`
  (loud throw on invalid), writes `data[id] = svg` and `facets[id] = {domain, kind, tags, name,
  description, provenance}`, defaults `domain:'feature'`/`kind:'object'`/`tags:[]` when absent
  (`:509–511`), persists vi/user symbols to `localStorage` (`:516`, `:520`).
- `CV_ICONS._loadPersisted()` (`:533`, called at `:540`) — re-hydrates vi/user symbols on load.

**The record shape** is `CV_GLYPHIC.schema.symbol` (**Observed — `assets/icons/cv-glyphics.js:118`**):
`{ id (kebab, required), svg (required), name (required), description?, facets:{domain (enum from
taxonomy), kind (enum object|action|state), tags:string[]}, provenance (built-in|user|vi|imported) }`.
`validateSymbol` (`:144`) checks the three required keys, kebab id, and a valid `kind` — **it does NOT
validate that `tags` are sensible or that `domain` is a real domain** (Observed: the loop at `:149`
only guards `kind`). So tags are entirely unconstrained free text.

### 1.2 The TWO meaning layers (this matters for deep-linking — §4)
The system **deliberately splits** a symbol's meaning into intrinsic vs contextual
(**Observed — `cv-glyphics.js:9–14`, `cv-meaning.js:9–11`**):

| Layer | Home | What it holds | Per-symbol? |
|---|---|---|---|
| **Intrinsic** (a house is always a house) | `CV_ICONS.facets` | `domain · kind · tags · name · description` | yes |
| **Gloss → plain word** (for the read-out) | the active meaning profile's `symbolGloss` | `symbol-id → word` (e.g. `house → home`) | yes, but contextual/loadable |
| **Contextual** (what a *form/colour/texture* means here) | `CV_MEANING` profile bindings | form/color/fill/texture/depth/motion → meaning | **no — symbols deliberately excluded** |

- **Observed — `cv-meaning.js:9–11`:** *"The ONE exception is SYMBOLS … a symbol's denotation is
  intrinsic and lives in CV_ICONS.facets, never here."* `MEANING_FACETS` (`:34`) is
  `['form','color','fill','texture','depth','motion']` — **symbol is not a meaning facet.**
- **Observed — `cv-meaning.js:407`:** `symbolGloss` is seeded with **exactly one entry**:
  `Object.assign({ house: 'home' }, …)`. `CV_MEANING.referent(spec)` (`:602`) reads it at `:618`:
  `thing = (P.symbolGloss && P.symbolGloss[spec.symbol]) || spec.symbol` — i.e. **with no gloss it
  falls back to the raw kebab id** as the noun. So 131 of 132 symbols read out as their id string,
  not an English word. This is SYNTHESIS item 9 (*"symbolGloss has ONE entry (house→home) — backfill
  ~110 + auto-gloss in the foundry"*). **The "backfill ~110" instinct IS the hand-written
  anti-pattern** — see §4.

### 1.3 The foundry (the live write loop) — Observed `app/ai/ai-glyphic.js`
Two capabilities are registered into `CV_AI`:

- **`glyphic.generate`** (`:59`) — `provider:'claude'`, `behaviours:['voice.conceptv']`.
  `buildPrompt` (`:26`) threads prior turns + the **live taxonomy** (`Object.keys(tax.domains)` /
  `tax.kinds`, `:31–32`) into the prompt, so Claude proposes on-system records (kebab id, Title-Case
  name, one-line description, 24×24 svg body, `facets:{domain,kind,tags}`). `run` (`:64`) calls
  `AI.complete(prompt)` → `parseCandidates` (`:47`) extracts a JSON array and validates each against
  `CV_GLYPHIC.validateSymbol` (`:54`), returning `{record, valid, problems}[]`.
- **`glyphic.save`** (`:72`) — `provider:null` (pure function, no LLM). `run` (`:77`) calls
  `CV_ICONS.add({provenance:'vi', …record})` → returns `{saved:id}`. **Instantly live** to the
  explorer, `CV_GLYPHIC`, and the registry (the comment at `:75`).

**Inferred:** the foundry is the existing, working precedent for "AI authors the icon set live, as
data." The *generate→save* shape is exactly the spine the semantic-lookup loop (§3) plugs into — the
loop's only addition is **deciding when to call it** (the below-threshold gate) and **deriving the
new icon's metadata from one source** (§4). The foundry already produces `tags`/`domain`/`kind` from
Claude at birth — so the system **already has a generative origin for an icon's metadata**; what it
lacks is a *re-runnable index* over those, and a *deep-linked gloss*.

### 1.4 The language-authoring sibling — Observed `app/ai/ai-glyphic-language.js`
This file registers `glyphic.author` / `author-relation` / `author-gloss` / `read` / `describe` /
`context.glyphic` — the **dual user+AI authoring of CONTEXTUAL meaning** (`CV_MEANING`), explicitly a
**sibling not an extension** of `ai-glyphic.js` (`:9–12`): *"ai-glyphic.js operates on CV_ICONS
(symbols — intrinsic); THIS operates on CV_MEANING (contextual meaning)."* Note `glyphic.author-gloss`
(`:45`) wraps `CV_MEANING.author.setGloss(symbol, word)` — **the manual write path for the symbol→word
gloss.** A generative gloss pass (§4) would *call this same API*, not invent a second one. Note also
`glyphic.transglyph` is **reserved/unbuilt** (`:79`) — the real referent-based read-out waits on Tim's
ear; relevant because the gloss it consumes is what §4 fixes.

---

## 2 · The governing-law violation, stated exactly

**The chain that should be generative, link by link, and where each link is hand-set today:**

```
icon SVG  →  domain/kind/tags  →  symbol→word gloss  →  noun-to-icon lookup
 (drawn)      (hand-typed in       (hand-typed in        (lexical substring
              cv-icons.js:273)      profile, 1 of 132)     search, cv-icons.js:430)
```

- **Observed:** `tags` are literals in `cv-icons.js:275–417`. Adding a synonym for an existing icon =
  editing source. (Law §5: "NOT a typed list".)
- **Observed:** the gloss is a literal in `cv-meaning.js:407` (1 entry). Backfilling 110 by hand =
  110 more literals.
- **Observed:** lookup is `String.includes` (`cv-icons.js:436`). "dwelling" finds nothing because the
  tag says "home"; "buyer" finds nothing because no icon's tags say "buyer". **No semantic reach.**
- **Observed (proven, §3.1):** there is **no embedder, no embed provider, no cosine, no fetch-to-
  Company** anywhere in `claude-ds/`. The generative machinery the law assumes simply isn't here yet.

**The precise design-for-the-class statement (My-idea, grounded):** the four hand-set links are
**one class** — *"derive an icon's searchable/speakable meaning from its single source, and re-run as
icons are added."* Dissolve the class with **one generative pass over one source** (`CV_ICONS.facets`,
which the foundry already fills from Claude at birth), producing a **re-runnable index + derived
gloss**, both **deep-linked** back to the facets (never copied). The pass re-runs whenever
`CV_ICONS.add` fires — so it can never go stale.

**Coherence guard (from review — keep this precise):** "generative / not hand-written" does **not**
mean *zero authored meaning*. Something must still ground the semantics — and it does, but the ground
**differs by provenance** (Observed §0):
- **Built-in icons (131):** the authored seed is **`tags` (+ id + domain/kind)** — there is no
  `name`/`description`. So the index embeds the tags + id + domain/kind text.
- **Foundry-minted icons (vi/user):** the seed is richer — the `name` + `description` Claude writes at
  birth (`ai-glyphic.js:38–41`) **plus** tags (`CV_ICONS.add` writes all of them, `:508–514`).

**Stated tension (be honest):** the index therefore derives, for built-ins, **from the same
hand-written tags §2 calls the anti-pattern.** That is not circular once you name the boundary: **the
tags are the authored SEED; the generative / re-runnable / deep-linked layer is the index + gloss +
lookup built ON them.** The anchor's law text (§5) is literally stronger — it wants the *tags
themselves* generative. **This area does NOT deliver that, and shouldn't:** an embedding cannot read an
SVG and emit "buyer"; it embeds the *text we already have*. Truly-generative tags would be a separate
LLM/**vision**-caption pass — fuzzier, and for built-ins it would have to caption the *rendered glyph*
since there is no name/description to draw from. The **lookup loop (§3) needs only the index, not
generative tags.** Honest beats glossed.

---

## 3 · The semantic icon-lookup loop — what exists, what's missing, the exact wiring

> **Separate the two things the anchor conflates** (review's sharpest point). The **lookup loop** needs
> only a **semantic INDEX** (embed representative text → cosine-rank). It does **not** need *derived
> tag strings*. Tag/gloss derivation (§4) is a different, fuzzier move (LLM caption / borrow-from-
> neighbours). Below is the index + loop; §4 is the derivation.

### 3.1 What EXISTS vs MISSING (Observed)

| Piece | Status | Evidence |
|---|---|---|
| Lexical search | EXISTS | `CV_ICONS.search` lexical, `cv-icons.js:430` |
| Foundry generate-on-demand | EXISTS | `glyphic.generate`, `ai-glyphic.js:59` |
| Live save into the single source | EXISTS | `glyphic.save` → `CV_ICONS.add`, `ai-glyphic.js:72` |
| Schema validation of a candidate | EXISTS | `CV_GLYPHIC.validateSymbol`, `cv-glyphics.js:144` |
| **An embedder reachable from the DS** | **MISSING** | `CV_AI.complete` resolves ONLY `claude` (`ai-registry.js:343`); `resolveProvider` knows kinds `claude`/`openai-image`/host-delegated (`:203–237`); **no embed kind**. `ai-seed.js` providers = `claude`, `openai-image`, `vision` (`:22,30,38`) — **no embed provider.** Grep for `embed`/`cosine`/`nearest` in `app/`,`_system/` → none in the icon/AI path. |
| **A semantic INDEX over icons** | **MISSING** | nothing builds or stores `icon → vector` / `icon → nearest[]` |
| **A noun→icon resolve step** | **MISSING** | no caller embeds a noun and ranks icons |
| **The below-threshold gate → foundry** | **MISSING** | nothing decides "no close icon, generate one" |
| **The browser↔Company HTTP transport** | **MISSING in DS** | no `fetch`/`:8770`/`:8001` in `app/ai/` or `host-runtime.js` |

So **the entire (b) loop is unbuilt**; only its two endpoints (lexical search, the foundry) exist.

### 3.2 The embedder that the index would resolve to (Observed — Company)
**Observed — `~/company/ops/services.json`:**
- `embed-pplx` (`:472`-adjacent; combo notes `:27,:32,:37,:43,:52`) = **pplx-embed-context-v1-4b**,
  **port 8007**, 2560-dim, 32K ctx, context-aware/late-chunking — the combo notes call it *"the
  strongest, replacing legacy BGE-M3."* This is the **pplx ~0.6b** Tim referenced (anchor §4) — it's
  actually a **4b** context embedder; the "0.6b" in the anchor is **mis-remembered** (no 0.6b embedder
  exists in services.json; verify-the-rosier-claim per anchor §0).
- `embed-bge` = **BGE-M3**, **port 8001**, `/v1/models` health (`:472,478,486`).
- **External-prior-art (Company runtime):** `nodes/embed` + `nodes/retrieve` exist in
  `~/company/runtime/{cognition.py,projection.py,suite.py}` (grep-confirmed) — the embed+cosine-rank
  primitives the design-folder charter's "X11 semantic edge" reuses. **NB:** the X11 mechanism the
  *parent* `~/company/design/CLAUDE.md` describes lives in **that** sibling folder's `_system/`, which
  **does not exist in `claude-ds/`** (`_system/symbols.py` is MISSING here). So X11 is **prior-art to
  copy the shape of**, realized in the sibling repo + Company runtime — not present in our repo.

### 3.3 The wiring (My-idea, grounded in the existing seams) — the icon-specific loop

**Stay-in-lane note (review):** the *provider abstraction / multi-provider CV_AI* mechanics
(anchor my-idea #1) are likely another agent's synthesis area. I specify the **seam** precisely and the
**icon-specific loop**; I hand the deep transport/provider plumbing to synthesis.

**The seam (one new provider + one runtime kind):**
1. **Register an `embed` provider in `CV_AI`** (mirrors `ai-seed.js:22`): `{ id:'embed-pplx',
   layer:'provider', family:'embed', runtime:{ kind:'native-model'|'mcp-model', model:'embed-pplx' },
   modality:['embed'] }`. — Observed seam: `resolveProvider` already **delegates unknown kinds to
   `CV_HOST.resolveProviderRuntime(p)`** (`ai-registry.js:233–237`), and `host-runtime.js:155–169`
   already handles `native-model`/`mcp-model` by calling `window.CV_HOST_NATIVE.complete(...)` and
   **throws a precise "needs the bridge" error in the sandbox** (`:165`). So an `embed` kind slots in
   the **same place**, adding an `embed(text)→vector` op alongside `complete`.
2. **Honesty guard (review):** that runtime resolves **only in the exported/bridged context** — in the
   browser sandbox it **throws loud** (by design, `host-runtime.js:165`). **In-browser semantic lookup
   does not work today** and must not be implied to. The live-instrument layer runs where the bridge to
   the Company (`embed-pplx` @ :8007) is reachable. This is the **browser↔Company boundary** the anchor
   §6 flags, made concrete for icons.

**The index (the re-runnable pass — this is all the loop needs):**
3. For each icon, build **representative text** from whatever the facet authored seed carries —
   `tags.join(" ") + " " + domain-label + " " + kind + " " + humanize(id)`, **plus `name` +
   `description` when present** (foundry-minted icons only — for the 131 built-ins those are absent,
   §0, so the text is tags+domain+kind+id). *All read from `CV_ICONS.facets`* (the one source). Embed it →
   `vector`. Store `CV_ICONS.index = { id → vector }` (in-memory; optionally persisted beside the
   localStorage symbols). **Re-run on every `CV_ICONS.add`** (hook the write path at `cv-icons.js:498`)
   so a newly-minted icon is immediately rankable. — This is the **X11 shape** (embed representative
   text → cosine), applied to `CV_ICONS` instead of code symbols.
4. **Degrade-with-warning** when the embedder is down (the X11 discipline): skip the index with a loud
   console warning + a surfaced Notice; **lexical `search()` still works** as the floor. Never fabricate
   a nearest.

**The resolve + generate-on-miss loop (the live pipeline's RESOLVE→GENERATE-ON-MISS steps, anchor §3):**
```
noun (from the extract layer, e.g. "buyer")
  → embed(noun)                                    [CV_AI.execute('embed', …) → :8007]
  → cosine vs CV_ICONS.index → ranked [{id, score}]
  → best.score ≥ THRESHOLD ?
        YES → use CV_ICONS.get(best.id) as the glyphic's symbol facet      (no LLM, instant)
        NO  → CV_AI.execute('glyphic.generate', {brief: noun, count: …})    (ai-glyphic.js:59)
              → pick/validate a candidate
              → CV_AI.execute('glyphic.save', {record})  → CV_ICONS.add     (ai-glyphic.js:72)
              → index pass re-runs (step 3) → the new icon is now rankable
              → use it live on the canvas
```
5. **THRESHOLD is a calibration parameter, not a guessed number** (review). It's tuned against the
   2560-dim pplx space on real nouns; expose it as a config knob, default set during a calibration pass
   (e.g. log scores for a noun corpus, pick the knee). **Do not hardcode a literal** — that would be the
   same anti-pattern one layer up.
6. This loop is **registry-native**: it's three `CV_AI.execute` calls + one cosine op. No new mechanism,
   no per-type branch — exactly the law's shape. The only genuinely new code is the embed op behind the
   seam and the cosine ranker (a dozen lines, reusing `nodes/retrieve`'s math, not reimplementing it).

---

## 4 · How meaning should DEEP-LINK to its source (not be copied) — (a) and (c) are ONE pass

**Review's key unification:** (a) the generative **tag/meaning backfill** and (c) the **gloss
deep-link** are *the same pass over the same source*. Make that explicit — it's the design-for-the-class
move.

### 4.1 The deep-link rule (Observed precedent + My-idea applied)
The system **already deep-links meaning rather than copying it**, in three places — *follow this exact
pattern*:
- **Observed — `cv-meaning.js:39–47`:** the default profile's **form bindings are seeded by reference
  from `CV_SHAPES.shapeTypes`**, with the comment *"reference, not a copy — the geometry source stays
  the home."*
- **Observed — `cv-glyphics.js:37–39`:** the glyphic `symbol` facet's value-space **resolves live** via
  `function(){ return Object.keys(need('CV_ICONS').data); }` — never a frozen list.
- **Observed — `cv-glyphics.js:196–206`:** `CV_GLYPHIC.meaningOf` **delegates to `CV_MEANING`** rather
  than holding meanings; the comment: *"Meaning is CONTEXTUAL → resolved through the active meaning
  profile … NOT hardcoded here."*

**So the rule the icon meaning must obey:** an icon's *searchable text* and its *spoken gloss* are
**derived views of `CV_ICONS.facets`** (the intrinsic single source), computed on demand / on-add, and
**keyed back to the facet id** — exactly like form-meaning keys back to `CV_SHAPES`. Nothing is copied
into a second list.

### 4.2 The ONE generative pass (My-idea, grounded)
On `CV_ICONS.add` (and an initial full run), for each icon, in one pass over `CV_ICONS.facets[id]`:

- **(index)** embed representative text → `CV_ICONS.index[id]` (§3.3). *Derived, deep-linked: the text
  is composed from the facets at run time; the vector is keyed by `id`; re-run on change.*
- **(gloss, replacing the hand-backfill of SYNTHESIS item 9)** derive the plain word from the facets.
  Since built-ins have **no `name`** (§0), the deep-link source is **`tags[0]` (or a humanized `id`)** —
  e.g. `building-tall → "tower"` from `tags[0]`; foundry-minted icons can prefer their authored `name`.
  Where a richer/contextual word is wanted, the **auto-gloss** move (LLM, the foundry already has the
  surface) captions from `tags + domain + kind` (+ `name`/`description` when present) → calls the
  **existing** `CV_MEANING.author.setGloss(id, word)`
  (`ai-glyphic-language.js:45`, `cv-meaning.js:439`). **Key point:** the gloss is *written through the
  one gloss API*, derived from the one facet source, and **re-derivable** — so adding 110 glosses is a
  *re-runnable pass*, not 110 source literals. (The contextual nature is preserved: a profile can still
  override a gloss; the derivation only fills the default that today is the raw kebab id at
  `cv-meaning.js:618`.)

**Why this honours "intrinsic vs contextual" (Observed `cv-meaning.js:9–11`):** the **embedding/index**
is intrinsic-derived (lives with `CV_ICONS`, the intrinsic home) and is profile-independent. The
**gloss** is contextual (lives in `CV_MEANING` profiles, loadable/swappable) — so the derivation seeds
the *default* profile's gloss but never freezes it. The two layers stay correctly separated; the
generative pass respects the boundary instead of collapsing it.

### 4.3 The meaning surfaced at lookup is a deep link, not a copy
When the resolve step (§3.3) picks `best.id`, the glyphic it builds **references** the icon by id —
`CV_GLYPHIC.compose({ symbol: best.id, … })` reads `CV_ICONS.get(best.id)` (`cv-glyphics.js:253`) and
the read-out reads `symbolGloss[best.id]` (`cv-meaning.js:618`). **At no point is the tag text or the
gloss copied into the graph node** — the node holds the **id** (the address); every consumer resolves
through the single source. This is the anchor's deep-link discipline (§5) realized: *meaning lives once,
referenced everywhere.*

---

## 5 · Honest hard parts + where hardcoding would sneak in (the rigor area, anchor §6)

1. **The threshold literal** — the single most likely place a magic number creeps in. Must be a tuned,
   surfaced config knob, calibrated against the real pplx space, never a guessed constant. (§3.3 step 5.)
2. **The browser↔Company boundary** — in-browser lookup throws in the sandbox by design
   (`host-runtime.js:165`); the loop only lives where the bridge to `embed-pplx`@:8007 is up. Don't claim
   it works in the plain design-system browser. (§3.3 step 2.)
3. **Index staleness** — if the embed pass is *not* hooked into `CV_ICONS.add`, a vi-minted icon is
   invisible to lookup → people re-generate duplicates. The re-run-on-add hook (§3.3 step 3) is the
   anti-staleness guarantee; it is the law, not an optimisation.
4. **`validateSymbol` doesn't validate tags/domain** (`cv-glyphics.js:149`) — a Claude-generated record
   can carry a junk domain or empty tags and still save. The index *derives from* whatever's there, so
   garbage-in propagates. A light validation tightening (domain ∈ taxonomy, tags non-empty) belongs with
   the foundry, loud. (Folds with SYNTHESIS item 8/9.)
5. **Lexical-vs-semantic both, not either** — keep `CV_ICONS.search` as the deterministic floor (it
   works with the embedder down); the semantic index is the reach on top. (Mirrors the Company's own
   *"company NOT cosine-only — session_search lexical mode"* finding in MEMORY.) **Both-plus-others**, not
   a replacement.
6. **The anchor's "0.6b embedder" is wrong** — it's a **4b** (pplx-embed-context-v1-4b, :8007). Cheaper
   alternative is BGE-M3 (:8001). A genuinely small/local embedder for sub-second per-noun latency during
   live speech is a real open question — verify latency before claiming "live". (Anchor §6 latency.)

---

## 6 · The minimum real demo for this area (anchor §8)
Bridge up with `embed-pplx`. Run the index pass over the 132 icons once. Then, by voice/text: say a noun
that **has** a close icon ("a house") → it resolves to `house` instantly (no LLM); say one that **has
none** ("a notary") → score below threshold → `glyphic.generate` draws a candidate → `glyphic.save` adds
it → the index re-runs → say "notary" again → it now resolves to the new icon. That round-trip —
**resolve-hit, generate-on-miss, re-index, resolve-hit-again** — proves the whole (a)+(b)+(c) loop and
that it can't stale.

---

## 7 · Evidence ledger (what's Observed vs Inferred vs External vs My-idea)

- **Observed (ran/read):** 131/132 faceted, 0 tagless, only `sun-moon` untagged; **0 of 131 built-in
  facets carry `name`/`description`** (those are written only by `CV_ICONS.add`, `:508–514`, for
  vi/user icons) — built-in seed = `id+domain+kind+tags`; `_ingest/ICON-AUDIT.md`
  absent; `symbolGloss` = 1 entry (`cv-meaning.js:407`); symbols excluded from meaning facets
  (`cv-meaning.js:34`); `CV_ICONS.search` lexical (`:430`); foundry generate/save (`ai-glyphic.js:59,72`);
  `CV_AI.complete` resolves only claude (`ai-registry.js:343`); no embed provider (`ai-seed.js`);
  `CV_HOST` native/mcp seam (`host-runtime.js:155–169`); deep-link precedents (`cv-meaning.js:39`,
  `cv-glyphics.js:37,196`); embed-pplx@:8007 / embed-bge@:8001 (`services.json`); `nodes/embed`+`retrieve`
  in Company runtime.
- **Inferred:** the foundry's generate→save shape is the loop's reusable spine; the index re-run on add
  is the no-staleness guarantee.
- **External-prior-art:** the "X11 semantic-edge" (embed representative text → cosine top-K, reuse the
  embed service, degrade-with-warning) — described in the **sibling** `~/company/design/CLAUDE.md`,
  realized via Company `nodes/embed`/`retrieve`; **not present in `claude-ds/`** (no `_system/symbols.py`
  here). Copy the *shape*, applied to `CV_ICONS`.
- **My-idea (marked):** the embed-provider seam + index + threshold-gated generate-on-miss loop; the
  one-pass unification of index + gloss derivation; deriving gloss from `facets.name` via the existing
  `setGloss` API; the demo.
