# AREA 7 — Data-Binding (glyphic facets ↔ live data) + Prior Art

> Research-wave companion, agent 7 of 7. Two halves: **(A) IN-SYSTEM** — how a glyphic facet binds to
> a live data value and resolves the *no-staleness* way, grounded in the real code; and **(B) EXTERNAL
> PRIOR-ART** — the proven NL→graph machinery that de-risks the extract→resolve→render→narrate loop.
> Every claim marked **Observed (file:line)** / **Inferred** / **External** / **My-idea**.
> Expansion ratio > 1: where the anchor is rosier than the code, I say so with evidence.

---

## TL;DR (the three load-bearing findings)

1. **The binding *delivery* mechanism already exists and is proven** — `runtime/channel_boundary.py` is a
   working Supabase **Realtime WebSocket** subscriber (postgres_changes, RLS-scoped via the principal JWT,
   daemon thread, reconnect-with-backoff) that injects DB INSERTs into a live consumer. A bound glyphic
   rides this exact channel: a row changes → a delta arrives → the glyphic re-resolves. **No polling, no
   copy, no staleness — by construction.** *(Observed: channel_boundary.py:119-160, 199-245)*

2. **The binding *grammar* exists but is surface-scoped, and the no-staleness chain has a flaw to fix.**
   `CV_MEANING.encodings` (data-facet → visual-channel, with value→appearance maps) is the existing
   precedent — but it short-circuits to **raw hex** (`axis:'#E0C010'`), whereas the glyphic `color`
   meaning resolves through **token names** (`{token:'gold'}` → `tokenForValue` → CSS var). A glyphic
   binding MUST resolve through the semantic/token layer, not copy hex like the System Map does — else
   it forks a second home for colour. *(Observed: cv-meaning.js:232 vs 334, 189-192)*

3. **There is NO business-domain data model yet (no project/property/buyer schema).** The live Supabase
   tables are *design-collaboration* (`dna_tokens`, `design_seeds`, `design_submissions`), *fabric*
   (`clients`, `channels`, `channel_posts`), and a *code-ledger* (`ledger.run/entry/symbol/edge`). A
   bound glyphic **today** can only bind to those rows. The "property sale" domain in the anchor's
   what-if is itself an **unbuilt gap to name** — but the *addressing spine* to reach it already exists
   (`project://`, the one resolver). *(Observed: 0004_collab_data.sql, 0011_ledger.sql, address.py:18)*

---

# PART A — IN-SYSTEM: how a bound glyphic resolves the no-staleness way

## A0 · The "one idea" this must obey
`claude-ds/CLAUDE.md`: *"consumers hold references, never copies… find the one home, edit there, reference
from everywhere else."* **No-staleness = the glyphic holds an ADDRESS, not a value, and re-resolves on
change.** This is not a new principle to invent — it is the system's prime directive, applied to live
data. The whole of Part A is: *what is the reference, what resolves it, what pushes the change.*
*(Observed: claude-ds/CLAUDE.md §0)*

## A1 · The existing binding grammar — `CV_MEANING.encodings` (the precedent to GENERALISE, not fork)

`CV_MEANING.encodings` is the **single home for "how a surface turns DATA into what you see."**
*(Observed: cv-meaning.js:210-255)*

- **Shape:** `encodings.register(surface, profile)`; a profile holds `channels` (the visual vocabulary:
  colour / size / texture / border / glow / opacity) and `sets`, where **each set binds ONE data facet to
  ONE visual channel**, either `kind:'discrete'` (a `values` map: data-value → appearance) or
  `kind:'scale'` (continuous interpolation, e.g. `stops`/`scale:'linear'`). *(Observed: cv-meaning.js:211-216, 218-255)*
- **Worked example** (`'system-map'` surface): `'role-colour'` binds the data facet `role` → channel
  `colour`, discrete; `'usedby-size'` binds `usedBy` → `size`, linear scale; draft sets bind `depth→border`,
  `roleGroup→texture`, `state→glow`. *(Observed: cv-meaning.js:230-253)*
- **It is surface-scoped today** — the only *runtime-JS* reference a grep for `CV_MEANING.encodings` /
  `.encodings.` finds is `cv-meaning.js` itself; per the file's own docstring it is ALSO projected into
  `system-map.json` by `build-system-map.js` (a build-step consumer, not a runtime one). So `encodings`
  is **surface-scoped**; the live layer GENERALISES it (a glyphic-binding profile is just another encoding
  profile), it does not invent a parallel mechanism. *(Observed: grep → cv-meaning.js only; cv-meaning.js:207-208 names build-system-map.js)*

**The flaw to fix (the "code does X but a binding must do Y" gold):** the System Map's encoding sets map
data-values straight to **raw hex** — `'role-colour'.values = { axis:'#E0C010', registry:'#6BA0E0', … }`.
*(Observed: cv-meaning.js:232)*. But the glyphic LANGUAGE layer maps `color` *state-values* to **token
names** — `seed('color','active', …, {token:'gold'})` — and `tokenForValue('active') → 'gold'`, which
`CV_GLYPHIC` then turns into a CSS `var()`. *(Observed: cv-meaning.js:334, 189-192)*. So there are **two
colour-resolution paths**: System-Map = data→hex (single-sourced to nothing — a literal), Glyphic =
data→meaning-value→token→var (single-sourced to the token registry). A **bound glyphic's colour facet must
take the second path** — resolve through the meaning value and its `token`, never a hex literal — or it
re-opens the drift the whole system exists to prevent. *(Inferred from the two observed paths.)*

## A2 · The missing piece — there is NO glyphic data-binding API yet (the anchor over-claims)

The anchor §1 says the parallel engine build "already includes… data-binding." **I cannot find it.** A grep
of `app/ai/ai-glyphic.js` and `assets/icons/cv-glyphics.js` for `bind` / live-data / `fromData` / `encoding`
resolution finds **nothing** — `ai-glyphic.js` is the *icon foundry* (generate/save symbols), not a data
binder. *(Observed: grep over ai-glyphic.js + cv-glyphics.js — no binding API.)* So:

- **What exists:** the appearance grammar (`CV_MEANING.encodings`), the meaning→token resolution
  (`tokenForValue`), the glyphic spec → render path (Area 2/3/5 own `CV_GLYPHIC.render`), and the meaning
  read-out (`describe` / `referent` / `readGraph`). *(Observed: cv-meaning.js:476-688)*
- **What is genuinely a GAP to design:** the function that takes `(address, encoding-profile)` and produces a
  *live* glyphic spec — `boundGlyphic(addr) = encode(profile, resolve(addr))`, re-run on every delta. This is
  the deliverable, not an existing API to wrap. *(My-idea, grounded in the precedent above.)*

## A3 · The addressing spine — what a glyphic binds TO (the reference, not the value)

For no-staleness the glyphic holds an **address** and re-resolves it. The system already has **one resolver
over a registry of schemes** — this is the spine the binding hangs on. *(Observed: cognition.py:1100 `resolve_address`)*

- **`contracts/address.py`** declares the scheme grammar (18+ schemes). Directly relevant:
  `project://<name>` (a project node), `file://<abs-path>`, `board://<id>`, `session://`, `run://`, `cas://`,
  `ui://`, `code://`, `skill://`, `context://`, `cap://`, `vec://`, `blob://`. *(Observed: address.py:4-71, 106-110)*
- **`runtime/cognition.py:resolve_address(store, addr, …)`** is the **scheme-dispatching, fail-loud, extensible
  seam**: it dispatches by `contracts.address.scheme(addr)` to the existing per-scheme resolver; a registered
  scheme with no resolver yet **RAISES** (never a silent empty); *"when a resolver exists, add a dispatch
  branch here and that scheme stops raising — exactly as skill://+context:// just did."* *(Observed:
  cognition.py:1100-1144)*. This is the EXACT shape the no-staleness law wants: one home, extend-by-registration,
  loud on the unbuilt.
- **`run_role` already composes ANY registered scheme as a role input** (the unify-exercise, 2026-06-26):
  a role declares `input_addresses`, and a `project://`/`board://`/`extraction://` address resolves through the
  ONE resolver, not just `run://`. *(Observed: cognition.py:238-268)*. **So the pipeline can already feed a
  live-resolved address into an extraction role.**

**`project://` is registered and HAS a working resolver — but in recollection's separate lane, NOT in the one
resolver yet.** The scheme is declared (address.py:18) and its resolver is recollection's *containment edges*
(address.py:108-110: *"their RESOLVERS are recollection's lane… wired"*). **But `resolve_address`'s own
docstring enumerates what it dispatches — run / cas / skill / context / session / cap — and says any other
registered scheme with no content-resolver RAISES fail-loud, naming `blob:// vec:// ui:// code://` as the ones
that currently raise.** A grep for `project://` in `cognition.py` hits **only the `def` line** — it appears
nowhere in the resolver body. *(Observed: cognition.py:1100-1144; address.py:18, 108-110; grep `project://`.)*
So the honest state: a glyphic for "the property-sale project" has a real *address* and a *lane resolver*
today, but **the one resolver does not yet dispatch `project://`** (it would fail-loud there, exactly like
`blob://`/`vec://`). Routing the binding chain through the single resolver = add the additive dispatch branch,
the way `skill://`+`context://` did (the seam below in A3, restated in the open threads). *(Inferred from the
two observed facts.)*

## A4 · The no-staleness binding chain (assembled, with the live-data hop proven)

```
  glyphic facet  ←  encoding(data-facet → channel)  ←  live state  ←  resolve_address(addr)  ←  Realtime push
  (color/fill/    (CV_MEANING.encodings,            (a row /        (the ONE resolver,        (channel_boundary
   texture/…)      generalised to glyphics)          a node)         18+ schemes)              postgres_changes)
```
*(Assembled from: cv-meaning.js:211-255 · cognition.py:1100 · channel_boundary.py:130-160.)*

**Hop-by-hop honesty (which are built vs seams):** hop-2 (encode) + hop-3 (meaning grammar) are **built**
(`CV_MEANING.encodings` + `tokenForValue`, just surface-scoped — A1); hop-5 (Realtime push) is **built and
proven** (channel_boundary, A4 below); **hop-4 (`resolve_address`) is the SEAM to extend** — the one resolver
dispatches run/cas/skill/context/session/cap today and fail-louds on any domain/`project://` address (A3), so
the live-state hop is *declared, not built* for a domain row until its dispatch branch is added the additive
way. The leftmost generalisation (encodings → glyphic-scoped) and a `boundGlyphic(addr)` are **My-idea**
grounded in the built pieces.

**Hop 5 — the live push — is the part I was most able to verify, and it is fully built:**
- `runtime/channel_boundary.py` opens a Supabase **Realtime WebSocket** (`wss://…/realtime/v1/websocket?apikey=…`),
  sends a **`phx_join`** subscribing to a table's INSERTs, and **carries the principal JWT as
  `payload.access_token`** so **Supabase applies RLS to postgres_changes and streams ONLY the rows the
  principal may see**. *(Observed: channel_boundary.py:119-135)*
- It runs in a **daemon thread**, **reconnects with backoff** on drop with a **fresh token each connect**, and
  fans each parsed INSERT out to an `on_insert` consumer. *(Observed: channel_boundary.py:199-245)*
- `parse_realtime_message` turns a raw frame into `(event, record)` — `postgres_changes` INSERT → the new row;
  join-ack / heartbeat / junk → `None`. *(Observed: channel_boundary.py:140-160)*

**This is the no-staleness delivery primitive, already proven against a real backend.** A bound glyphic does
not poll; it subscribes to the row(s) behind its address and re-resolves on the pushed delta. The same primitive
that injects `channel_posts` into a live session injects `design_submissions` / `dna_tokens` / a future
domain row into the live glyphgraph. *(Inferred — same mechanism, different table.)*

## A5 · The Supabase situation — the REAL state (correcting the anchor's "today local")

The anchor says Supabase is "the planned backend, today local." **The evidence is more nuanced and more built:**

- **A real hosted project is referenced and wired:** `gctunhsuwpaxeatwlmuv.supabase.co` appears across
  `supabase_principal.py`, `channel_boundary.py`, `vi_vision.py`. *(Observed: supabase_principal.py:152-155;
  channel_boundary.py:42, 314)*
- **A least-privilege auth primitive is built and offline-tested:** `runtime/supabase_principal.py` —
  `SupabasePrincipal(env_prefix)` does `grant_type=password|refresh_token` → cached/refreshed JWT →
  `auth_headers()` = `{apikey: anon, Authorization: Bearer <jwt>}` for PostgREST/Realtime; **fail-loud, never a
  silent unauthenticated call**; env-prefix parameterised so ONE class serves every internal principal (the
  channel boundary, `vi_vision`, a future glyphic binder). *(Observed: supabase_principal.py:50-138; self-test
  155-184)*. **This is the auth primitive a glyphic binder reuses — it does not write its own.**
- **There is also a LOCAL dev-stack config:** `build-prep/claude-design/supabase/supabase/config.toml` —
  `project_id="gctunhsuwpaxeatwlmuv"`, API port `15421`, db port `15432`, `"the local stack is http"`. So a
  **local Supabase stack mirrors the hosted project**. *(Observed: config.toml; channel_boundary.py:119 comment.)*
- **Honest status:** I **Observed wiring** to both a hosted URL and a local stack; I did **not Verify** that
  either is *running right now* (and Tim's memory notes recurring "company-down" states). The live/local question
  should not carry weight — the headline (A5 below) stands regardless.

**The data model (the real headline) — what a "project/property/buyer" thing would be and read:**
- **Design-collab tables** (`0004_collab_data.sql`): `dna_tokens` (id, group_id, value, note — the token library
  Claude Design snaps to), `design_seeds` (a partial description + DNA ref + status `open|designed|translated|
  registered`), `design_submissions` (the export bundle, status `ingested|…|registered`). **All three are
  published to `supabase_realtime`** — so they already push live deltas. *(Observed: 0004_collab_data.sql:16-65)*
- **Fabric tables** (`0002/0003`): `clients`, `channels`, `channel_posts` (the cross-session message rows
  `channel_boundary` subscribes to). *(Observed: 0002_clients.sql, 0003_channels.sql)*
- **Code-ledger** (`0011_ledger.sql`): a non-flat, run-scoped structural ledger — `ledger.run` (project, channel,
  purpose, layer, model, status), `ledger.entry` (per-file: path, node_type, imports, declares, what_it_does, …),
  `ledger.symbol`, `ledger.edge` (from_ref, kind, to_resolved). **This is a graph-of-the-codebase already in
  Postgres** — the closest existing thing to "a domain graph the glyphic could render." *(Observed: 0011_ledger.sql:13-126)*
- **There is NO `projects` / `properties` / `buyers` / `offers` table.** *(Observed: the migration set 0001-0012
  contains none; the only `project` is the *text column* in `ledger.run` and the `project://` *address scheme*.)*

**Conclusion (A5):** a bound glyphic can be demonstrated **today** against `design_seeds.status` or
`design_submissions.status` (real rows, real Realtime push, real state-machine values) — that is the honest
minimum live binding. The "property sale" domain is a **separate unbuilt schema**; naming it is in-scope, and
when built it plugs into the SAME spine: a `properties` row → addressed (`project://oak-st` or a new
`property://<id>` scheme registered the additive way) → resolved by `resolve_address` → pushed by
`channel_boundary` → encoded onto glyphic facets. *(Inferred from the observed seam + the no-staleness law.)*

## A6 · How a bound glyphic and a talk-generated glyphic co-exist (anchor §8 thread)
They are the **same spec with two provenances.** A talk-generated node's facets come from the EXTRACT→RESOLVE
pass (Area 1-6); a bound node's facets come from `encode(profile, resolve(addr))`. Both produce a `CV_GLYPHIC`
spec; both render through the one renderer; both narrate through `CV_MEANING.describe`. **The discriminator is
just whether the node carries an `addr`.** A bound node simply *also* subscribes for deltas. *(My-idea, grounded
in the shared spec shape at cv-meaning.js:476-541.)* This means "the buyer's gone cold" (a voice correction) and
the CRM flipping `status='cold'` (a live delta) **converge on the same facet mutation** — which is the
instrument's whole promise.

## A7 · The provider abstraction (anchor §4/§7 — partly already built)
The anchor's "my-idea" (wire Company-local models into `CV_AI` as providers) is **partly real**:
- `CV_AI.resolveProvider` binds a provider to its live runtime; `claude` → `window.claude.complete`,
  `openai-image` → `window.cvOpenAI`; **anything else is delegated to `CV_HOST`.** *(Observed: ai-registry.js:194-237)*
- `CV_HOST` (`host-runtime.js`) already has the delegation branch: a provider with `runtime.kind ===
  'native-model' || 'mcp-model'` is bound to `window.CV_HOST_NATIVE.complete(model, prompt, opts)`, with a
  loud error naming how to activate it ("…when you export this app and run it with the local bridge"). *(Observed:
  host-runtime.js:150-169)*. **So the seam for "a Company-local model as a CV_AI provider" exists** — what is
  missing is (a) the seeded provider entries (ai-seed.js seeds only `claude` / `openai-image` / `vision`) and
  (b) a `CV_HOST_NATIVE` implementation that reaches the Company over HTTP (the `company` MCP `run_role` /
  `models_for_role`). *(Observed: ai-seed.js:19-44.)* This is the un-hardcoding the governing law (§5) demands:
  register the local providers, don't branch the resolver. **It half-exists; finish it by registration.**

## A8 · The embedder reality (anchor §4 — correcting "pplx ~0.6b")
The anchor's "**pplx ~0.6b** embedder" is **wrong on size.** The real model is **`pplx-embed-context-v1-4b`** —
a **4B**, **2560-dim**, **32K-ctx**, context-aware/late-chunking embedder (~5.4G at 8-bit, ~8.2G otherwise),
the designated *strongest* embedder replacing legacy BGE-M3. *(Observed: ops/services.json:32, 39, 78)*. It is
resident in the `interaction` / `instrument` / `xsession` loadouts alongside `chat-4b-fp8` (the everyday brain),
`rerank-jina`, an STT ear (Moonshine/whisper/parakeet — `nvidia/parakeet-tdt-0.6b-v3`), and `tts-kokoro`.
*(Observed: ops/services.json:32-58, 296)*. **So semantic icon-lookup (anchor §4) uses the 4B context embedder,
not a 0.6B one** — more capable, but heavier; the latency budget must account for that. The "0.6b" Tim referenced
is most likely the **parakeet-0.6b STT model**, not the embedder. *(Inferred from the two 0.6b-bearing entries.)*

## A9 · The CSP / browser↔server boundary (anchor §6/§7 — the real constraint)
The design system's no-script page-face renders server-side (`runtime/page_render.py`), but the *interactive*
canvas (`app/`, CV_AI, CV_GLYPHIC) runs **in a browser**. The local models + Supabase principal + Realtime
subscriber are **server-side Python** (`channel_boundary.py`, `supabase_principal.py`, `cognition.py`). *(Observed:
those files are `runtime/*.py`.)* So the live-instrument has a **boundary**: either (a) the browser opens its OWN
Supabase Realtime WS (anon + a browser-side principal JWT) and resolves addresses client-side, or (b) the Company
drives the pipeline server-side and **pushes graph-deltas to the browser** (the `channel_boundary` shape, but
INTO the canvas). Option (b) reuses the proven primitive and keeps the local-model + extract work server-side
where it belongs; the browser becomes a thin render+narrate surface. **(b) is the lower-risk path** because it
reuses `channel_boundary` wholesale and never exposes the box. *(Inferred from the file locations + the
channel_boundary "nothing connects IN — no box exposure" comment, line 161.)*

---

# PART B — EXTERNAL PRIOR-ART (de-risking the NL→graph pipeline)

> *(Filled from the prior-art research pass — see below. The discriminating question for each item is the same:
> does it give a **streaming / incremental** extract target? A batch-only formalism de-risks nothing for the
> realtime honest-hard-part, §6 of the anchor.)*

**Cross-cutting headline (External):** the pipeline maps onto **mature** prior art at every stage; the
**only genuinely novel/unproven part is the full integrated voice-correction loop.** Discriminator applied
throughout: *does this give a streaming/incremental extract target?* (batch-only ⇒ de-risks nothing here).

### B1 · Abstract Meaning Representation (AMR)
- **What it is:** a sentence → a single **rooted directed-acyclic graph**; nodes = concepts (PropBank
  predicates + entities), edges = typed semantic roles (`:ARG0`, `:location`). Abstracts away surface syntax
  (3 paraphrases → 1 graph). *(External; cutoff)*
- **What's proven:** strong **sentence-level** parsers — SPRING / AMRBART (BART/T5 seq2seq, Smatch low-80s),
  transition-based parsers; AMR-to-text generation likewise solved. *(External, fact)*
- **The realtime catch:** **not incremental** — built to consume one *complete, clean written sentence* and
  emit one complete graph; full autoregressive decode per sentence; out-of-distribution on disfluent speech.
  **Do NOT put a real AMR parser in the live loop.** *(External, inference)*
- **Borrow:** the **target SHAPE, not the toolchain** — concepts-as-nodes / roles-as-typed-edges validates the
  glyph-graph; **reentrancy** (reuse one node when an entity recurs) = your "resolve to ONE node" requirement;
  **abstraction** (normalise paraphrases before placing) so "wants to go / desires going" don't double-node.
  Let small LLMs emit something *AMR-shaped but lighter*.

### B2 · Conceptual Graphs (Sowa)
- **What it is:** a **bipartite** graph — **concept nodes** + **relation nodes** (edges only run
  concept↔relation, never directly between concepts); maps to first-order logic; CGIF serialization. *(External)*
- **Status:** conceptually influential (fed ISO Common Logic); **tooling effectively dead** (no maintained,
  performant JS/Python lib). *(External, inference)*
- **Borrow (high value):** **relations as FIRST-CLASS nodes.** This is the precedent for Tim's "edges≠verbs /
  glyphic=address" — it lets a *relationship itself* be addressable, renderable, glyph-bearing, narratable
  (a state/confidence/glyph attached to the edge, not just the edge). Also the **type lattice** for resolving
  a mention → a glyph *type*. Take the structure; leave the FOL + tooling.

### B3 · RDF / triples / property graphs
- **What it is:** the **(subject, predicate, object)** triple is the atomic unit; RDF = W3C standard (URIs +
  SPARQL); **LPG** (Neo4j/Cypher) = nodes+edges each carrying key-value property bags + labels. *(External)*
- **What's proven:** triples are the **universal extract target** — lowest-common-denominator decomposition,
  trivially mergeable (incremental accumulation = **set union**), and "head/relation/tail" maps perfectly onto
  a fill-in-the-blanks JSON schema a small LLM emits reliably. *(External, fact)*
- **RDF vs LPG:** RDF = standard + globally addressable but a property *on a relationship* needs awkward
  reification; LPG = properties-on-edges native, ergonomic for "this edge has a state/glyph." *(External, fact)*
- **Borrow (the storage decision):** **extract AS triples, store/render AS a property graph.** Triples give
  free stable incremental accumulation + dedup-is-entity-resolution; LPG gives states-on-nodes AND
  glyphs-on-relations (which B2 demands). **This directly answers the open thread "typed domain table vs
  generic triple store":** a generic `{subject, predicate, object, state}` triple store IS the proven extract
  target — it can back a glyphgraph without a per-noun table, and the address spine (`project://`, a new
  scheme) sits on top. *(External + my-idea joining it to A3/A5.)*

### B4 · LLM knowledge-graph construction (the 2024-2026 dominant pattern) — the heart of EXTRACT
- **What it is:** prompt an LLM → emit `(entity, relation, entity)` triples as **structured JSON**,
  **schema-guided** (closed list of entity + relation types); build the KG incrementally by streaming chunks
  and merging. *(External, fact)*
- **Real systems:** **Microsoft GraphRAG** (LLM extracts entities+relations per chunk → graph → community
  summaries); **LangChain `LLMGraphTransformer`** (docs → schema-constrained nodes/relationships → Neo4j);
  **REBEL** (BART-class **~400M** seq2seq, purpose-built end-to-end relation extractor — the *small/fast*
  option directly relevant to "concurrent small LLMs"); **`instructor`/constrained-decoding/vLLM JSON-schema**
  (the plumbing that makes triple-emission reliable); **Graphiti/Zep** (temporal KG ingesting **conversational
  episodes**, LLM-extract, bi-temporal — the closest to *conversational incremental* building). *(External, fetched)*
- **Small-model reality (honest):** constrained decoding makes the **format** reliable (schema-valid JSON
  nearly always); the **content** is the weak point — missed relations (recall), hallucinated edges
  (precision), and **inconsistent entity canonicalisation** ("Tim" vs "the founder") which directly threatens
  resolve-to-one-node. Latency for a small (≤8B) model emitting a few triples per utterance is fine for a
  conversational loop; running several **concurrently** over utterance windows is a sound standard pattern.
  *(External, inference — consistent field-reported failure mode.)*
- **Borrow (4 concrete):** (1) **schema-guided extraction is non-negotiable** — closed entity/relation-type
  vocab is the biggest reliability lever AND makes resolve-to-glyph deterministic (type → glyph type);
  (2) **split extract from judge** — small models EXTRACT candidate triples, a **central** step does
  canonicalisation/merge (embedding-match + smarter judge), never the fan-out workers — **this is exactly
  Tim's `extraction-vs-judgment` law, independently the field's answer**; (3) **staged incremental ingest**
  (per-utterance extract → merge into the running graph, not re-parse the transcript); (4) consider a
  **REBEL-class** purpose-built extractor as a fast first pass, prompted-LLM as smarter fallback.

### B5 · Realtime "talk → diagram/graph" systems
- **Honest headline:** **no dominant production system does the FULL loop** (live speech → auto-extracted
  growing graph → auto-layout → narrate → voice-correct). Closest = research prototypes + commercial tools
  doing *pieces*. The integrated loop is **genuinely novel space.** *(External, fetched/inference)*
- **Closest prototype — MeetMap (arXiv 2502.01564, 2025):** STT → speaker-turn detection (**splits long
  monologues at ~50-word checkpoints** to avoid lag) → GPT-4 categorises each turn (IBIS schema) → emits
  **node summaries into a "Temporary Node Palette"** → placed on canvas. Variants: Human-Map (users drag/link)
  vs AI-Map (auto-generated at topic boundaries). **Findings:** (a) **staged outputs win** — show the atomic
  node *immediately* per turn, defer relationship/map generation async; this *feels* more real-time than
  periodic full summaries; (b) users have **low tolerance for AI errors on output they "own"** and **full
  auto-layout reduced perceived understanding** vs self-placement. *(External, fetched)*
- **Commercial pieces:** **tldraw** (infinite-canvas TS/React SDK with first-class **AI starter kits** —
  custom shapes, bindings, agent/workflow kits, multiplayer; the strongest *substrate*); **Excalidraw**
  text-to-diagram (one-shot, not streaming); **Graphiti** (the backend accumulate-analogue, no canvas/voice).
- **Borrow:** (1) **staged-reveal is the most important steal** — place the *node* the instant an utterance
  resolves; run relation-inference + re-layout async (makes it *feel* live, empirically validated); (2) the
  **checkpoint-long-monologues** chunking (pairs with the Company's existing VAD/finished-thought judge);
  (3) the **error-ownership finding cuts against full automation — BUT Tim's voice-correction channel is the
  mitigation:** full auto-layout is fine *if correcting it by voice is trivial*; make the correction loop
  cheap and the "humans must place" finding stops applying. **(4) ⚠ Tension with the anchor:** the anchor
  fixes **reactflow**; the prior art points to **tldraw** for the AI/freeform-on-canvas feel (anchor §8's own
  open what-if). Worth surfacing to Tim — reactflow needs dagre/elkjs bolted on and isn't incrementally stable
  (see B6), tldraw ships the AI/shape/binding substrate. *(External — flag, don't decide.)*

### B6 · Incremental / stable graph layout (the "graph that grows without jumping")
- **The problem:** naive re-layout re-solves everything → all nodes jump → spatial memory destroyed. *(External)*
- **What's proven, in priority order:** (1) **position-seeding** — drop the new node *at/near its connecting
  node's coords* before any layout runs (never starts at origin + flies across); (2) **pinning** — fix existing
  nodes (`fx`/`fy` in d3-force, or high mass/low alpha), relax only the newcomer + local neighbourhood;
  (3) **constraint-based incremental solve — cola.js / WebCola** — layout as constraint optimisation re-run with
  existing positions as start + soft constraints, so additions perturb **locally**; this is **the** library
  purpose-built for stable incremental layout. ELK/elkjs has `INTERACTIVE` modes (weaker incrementality);
  **reactflow does NOT auto-layout** — the ecosystem bolts on **dagre** (fast layered) or **elkjs** (richer,
  slower), neither incrementally stable OOTB. *(External, fact)*
- **Borrow (the actual answer to anchor §6's honest-hard-part):** default to **cola.js/WebCola**; always
  **seed-then-relax** (resolve → drop at parent's coords → short, locally-scoped relaxation with existing nodes
  pinned; never a full global re-layout per utterance); this **pairs with B5's staged reveal** — appear
  instantly at seed position, then async-settle → reads as "alive," not "jumpy."

---

## Open threads handed forward (for the synthesis layer)
- **Name the domain schema** (`properties`/`buyers`/`offers` or a generic `entities`+`relations`+`states` triple
  store) — it's the one unbuilt thing between "demo on design_seeds.status" and "talk a property sale into being."
  Decide: a typed domain table per noun, or a generic triple store the extract layer writes to (see Part B/RDF).
- **Generalise `CV_MEANING.encodings` from surface-scoped to glyphic-scoped** + add `boundGlyphic(addr, profile)`
  that resolves-through-token (never hex) and re-runs on delta.
- **Register a `property://` / reuse `project://` scheme** + its `resolve_address` dispatch branch (additive, the
  skill://+context:// way) so a domain row is addressable the one-resolver way.
- **Seed Company-local CV_AI providers** + implement `CV_HOST_NATIVE.complete` over the `company` MCP — finish the
  half-built provider seam by registration, not a resolver branch.
- **Pick boundary (b):** Company drives the pipeline, pushes graph-deltas to the browser via the `channel_boundary`
  Realtime primitive — reuse, don't reinvent, don't expose the box.
