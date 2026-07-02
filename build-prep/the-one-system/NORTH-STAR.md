# THE ONE SYSTEM — north star (Tim, 2026-07-02) — READ THIS BEFORE BUILDING

*Written into the record because Tim's only interface to the whole system is this chat until the UI exists. This is the direction everything serves. It doesn't all get built now — but it must be understood and honoured in every build decision. Board: filed alongside; docs: the durable copy.*

## What the ledger actually IS (not "a search index")
The ledger is **the common world the entire AI system works through** — and it is a **multi-axis, multidimensional coordinate space**, not a search box. Every unit of data can be located along, and related across, shared axes:
- **Graph** — typed nodes + edges (calls/imports/contains/serves-endpoint/subscribes/generated-by/…).
- **Vectors** — semantic position, MULTIPLE embedders + configs (nomic-code 3584, pplx 2560, bge 1024, more coming), each a lens.
- **Directory / paths** — the physical containment tree.
- **Scale** — file ↕ symbol ↕ clustered pyramid rungs (`scale:<space>:k<N>`); zoom changes which rung resolves.
- **Time** — created/changed/extracted; the temporal axis.
- **Transcript provenance** — **there is NO data in any repo/project that wasn't generated from an AI Claude-Code transcript.** Every unit traces to the `exchange://<sid>/<i>` that produced it (the `generated-by` edges). The transcripts are the ROOT; everything else is a projection of them.
- **Address systems + registries** — one grammar (`contracts/address.py`: code:// cap:// exchange:// board:// ui:// image:// …), shared across all axes, resolved through ONE resolver.

Everything **shares addresses** and can be **identified relative to these common axes**. That is the coordinate space.

## What we're really building (the bigger frame)
The long process of this session is a **reusable, compositional generation chain to create and maintain PROJECT UNIVERSES** — where **AI and UI share ONE interface, the data being the origin for both.** Capabilities are **projected to MCP and to UI from the SAME functions** (write the capability once; both faces get it). **Multi-project is simple: each project is just an address at the project level.** The ledger is the seed; this is the substrate the whole unified system grows from.

## HOW TIM WORKS — the development style (critical; changes how you build)
- **There are no developers. Tim is not a domain expert** in Supabase, SQL, schemas, pgvector, TypeScript, edge functions, extensions, UI/front-end, MCP, tool design, or software/AI-tool design styles. He knows **how systems work** — the relational/architectural shape — not the technical layer.
- **Everything already built was a best-guess by an AI** implementing what Tim described at the time. **None of it is intentionally as-is** — there was no educated design intent behind the specifics. So current code/schema/structure is *scaffolding, not spec* — never treat it as the intended bar.
- **Tim cannot give technical specs, instructions, or requests at the level of things he doesn't know** — and cannot even *ask* for a design in domains he can't see. **Therefore the AI must PROACTIVELY identify better-known/standard ways to do things and factor them into every build** — every time. If there's a better-known approach (e.g. how vector search is properly done in Supabase, whether there are multiple ways to do an operation, standard schema/index patterns), identify it, explain the trade-off in plain terms, and build the better one. Don't wait to be asked; Tim can't ask.
- Tim guides by **describing how the system should work**; the AI supplies the technical realization + surfaces the choices as recognizable options.

## STANDING DIRECTIVES (apply to every build from here)
1. **Proactively bring best-practice.** Before building anything technical, identify the standard/better-known way (and whether there are several), and choose/justify — because Tim can't request what he can't see.
2. **Tools are GENERATIVE + shared.** The tools that interact with the ledger will be updated/worked on constantly, and the **UI and the tools share** — so build capabilities as functions that project to BOTH MCP and UI (one function → two faces). Not one-off scripts.
3. **The ledger's interaction tools are IN SCOPE.** The ledger is the common world; the tools to query/generate/maintain it are part of what we build, not a side concern.
4. **Everything ends up in Supabase — but not all at once.** Vectors now; the rest (objects/events/chat/graphs/sessions) later, deliberately.
5. **Everything fails loud with resolution breadcrumbs** — errors give the path/address it expects now AND where it used to point + the fix command, because **no human is ever involved in the code** — only agents resolve issues, and they need the trail.
6. **No-confidence framing, addressed, provenance-stamped** — the existing laws still hold.

---

# ① THE VECTOR READ-PATH CUTOVER — walkthrough + decisions

## Plain-language: what it is
All ~7 features that ask "find the most semantically-similar things" (RHM chat corpus, R2/consult semantic, canvas forager search `/api/corpus-query`, neighbours, the agent `corpus`/`find_relations` MCP tools, the scale pyramid) funnel through **ONE seam**: `space_matrix` / `_vector_records` in `store/fs_store.py`. That one function is the only place vectors are actually read. **Change that one function to read Supabase → all 7 features follow; none of them change.** (Replace the water main, every tap switches source.)

## What moves / what doesn't
- **Moves now:** ONLY the `vectors/` namespace — already copied to `ledger.embedding` (76,039 rows). This step just switches the READER's source.
- **Does NOT move now:** the rest of FsStore (~630MB: objects/events/chat/graphs/sessions). That's the eventual "everything in Supabase," later.

## What changes
`space_matrix`/`_vector_records` runs a **pgvector cosine query** on `ledger.embedding` (HNSW index) instead of loading disk files. Readers above it are untouched.

## PROACTIVE IMPROVEMENTS to fold in (per the standing directive — these are better-known ways Tim couldn't ask for)
- **Expose search as a shared FUNCTION, not inline SQL** — a Postgres RPC (or a thin `ledger_search(space, emb, query_vec, k)` function) that BOTH the MCP tools and the UI call. This directly serves "capabilities projected to MCP + UI from the same functions." (Best-practice for Supabase + matches the vision.)
- **Reconsider the schema against best-practice** — my current design is one table with per-dim halfvec columns. Standard pgvector patterns also include one-table-per-model or `vecs`-style collections; I'll evaluate which is cleanest for multi-embedder + multi-scale + query ergonomics and justify the choice rather than inherit my first guess.
- **HNSW tuning** (m / ef_construction / ef_search) — set deliberately for recall vs speed, not defaults, and document why.
- **The query should carry the coordinate axes** — filter/return by space + emb + scale + project + time, so search is a coordinate query, not just cosine (serves the multi-axis vision).

## DECISIONS (Tim, 2026-07-02)
- **No fallback = COMMENT IT OUT**, not delete. The FsStore read path stays in the code but disabled/inert, with comments explaining it's the pre-Supabase path, why it's off, and how to restore — so it has no influence but is recoverable and legible to a resolving agent.
- **Loud-fail breadcrumbs** on every read miss: "expected (space, emb, address) in ledger.embedding :15432; previously FsStore .data/store/vectors/<key>; fix: ops/migrate_vectors_to_supabase.py --space <s>".
- **Order + scope of actual implementation: DECIDED LATER** — after ② and ③ are also written out. Nothing built until then.

# ② THE ADDRESS SURFACE CHANGE — walkthrough + decisions

## Plain-language: what it is
The S3 surface answers *"what code powers this UI element?"* — it maps `ui://<region>/<element>` → `code://` symbols → the files. Today `resolve_scope` (in `suite.py`, live operator-surface code) reads a **separate sidecar file** — `design/_system/code-symbols.json` (26KB, generated by `design/_system/symbols.py`) — keyed by the LOSSY **`code://<file-stem>/<symbol>`** form. Meanwhile the LEDGER holds the RICH canonical **`code://<project>/<path>::<symbol>`**. That's the "two grammars" split: a parallel, older, lossy code:// source powering the live surface, beside the canonical one in the ledger.

## What changes (same shape as ①)
Point `resolve_scope` + the S3 surface at the **LEDGER as the single source** (canonical addresses), retiring the sidecar `code-symbols.json` + its `symbols.py` generator. A reader → the unified source, exactly like ①.

## The dependency (honest — makes ② a touch bigger than ①)
`resolve_scope` needs the `ui://→code://` join (the "referenced_by" reverse index). The ledger has **551 `ui://` reference edges** already, but whether that's the FULL join the surface needs must be verified — if not, the extractor/ingest must capture the complete `ui://→code://` edges into the ledger FIRST, then repoint. So ② = (a) ensure the ledger holds the full ui→code join, (b) repoint resolve_scope at it, (c) canonical addresses throughout.

## PROACTIVE IMPROVEMENTS to fold in (best-known / vision-aligned)
- **One resolver-function, shared** — expose ui→code→scope resolution as a shared ledger-backed function that BOTH the S3 UI surface and the MCP tools call (the "same function → both faces" vision), instead of surface-only code reading a json.
- **Single source kills the staleness** — the docstring itself flags that `code-symbols.json` is regenerated-not-live ("a future rung could regenerate-then-read"). Resolving against the ledger (which IS the maintained source) removes that whole stale-sidecar class.
- **The ui:// address space** (addresses.json, 354KB) should also be ledger-resident nodes so ui:// is a first-class coordinate (Glyphic's design side lands here too — the CONNECTION-CONTRACT ui://↔code:// record becomes ledger edges).

## Why it needs us together (supervision)
`resolve_scope` is LIVE operator-surface code — the only real test is a live `ui://→code` resolve + a chat/surface turn. Silent breakage = the surface stops resolving until morning. So: I make the change, you drive a live turn, we confirm, then flip.

## DECISIONS (Tim's standing rules applied)
- **No-fallback = COMMENT OUT** the sidecar (`code-symbols.json`) read path — inert, commented, recoverable — not deleted.
- **Loud-fail breadcrumbs**: "resolve_scope expected ui→code join in ledger (ledger.edge kind=references, ui://→code://); previously design/_system/code-symbols.json; regenerate via <cmd>."
- **Technical approach: I propose it** (per north-star — Tim can't spec what he can't see): repoint to the ledger, ensure the ui→code join is complete first, expose as a shared function.
- **Order/scope: decided after ③ is written.**

# ③ THE FORK — the UI you can SEE through (direction, not just a cutover)

## Plain-language: what it is
This is your window — the interface that lets you SEE and DIRECT the whole system (right now this chat is your ONLY interface). It is NOT a separate app and NOT from scratch. Already built to grow on:
- **`runtime/projection.py`** — a projection ENGINE that maps ledger records into a polar COORDINATE space by data-driven "bindings" (θ = a categorical division e.g. kind; r = distance e.g. time-from-now). Its own principle: *"meaning lives in the DATA, never in the instrument"* — i.e. generative by design (add a binding/lens as data, not code). This is literally a coordinate-space renderer already.
- **`canvas/app` LatticeView.tsx** — renders that polar projection interactively on an HTML5 canvas (fetches `/api/projection`).
- **`surface/app`** — the form-factor-aware React surface + the RightHand/RHM.
Today it projects mostly EVENTS (θ=kind, r=time). The ledger's other axes (vectors/graph/scale/provenance/paths) aren't rendered yet.

## Why this is THE fork (why it needs your direction, not my mechanics)
①②  are cutovers I can largely propose+build. ③ is a DIRECTION call — how much, in what order, what you most need to SEE first — and only you can set that, because it's about what makes the system legible to YOU.

## The choices
- **A — build the full multi-axis view now:** extend projection+LatticeView to render the ledger's coordinate space (vectors/graph/scale/provenance/paths), navigable + zoomable, as the shared face. Biggest; the whole window.
- **B — harden the substrate first:** verify embedding quality across spaces, improve the descriptions, before building the visible layer on it.
- **C — one narrow, powerful slice first:** e.g. "click a file → see the conversation that generated it" (provenance), OR a semantic-search view over the store. Proves the shared-function pattern + gives you something to SEE fast, then expand to A.

## The vision this serves (why it's the payoff)
UI + MCP tools **share functions** — a coordinate query / projection / search written ONCE, projected to BOTH faces (the north-star's core). So building the UI = defining the coordinate-space functions once (the ① search-function + the projection engine are the shared core) → both the agent tools and your visible surface get them. Generative (bindings/lenses are data), multi-project (project = a top-level address), built on the design system (the FORM bar).

## DECISIONS
- **Direction (A / B / C): TIM'S CALL** — this is the one that's genuinely yours. My lean: **C → A** (a narrow, powerful slice first — fastest path to you SEEING something real + it proves the shared-function pattern — then grow into the full multi-axis window).
- **Order/scope across ①②③: decided now that all three are written** (below / next).

---
# NOW ALL THREE ARE WRITTEN → decide order + scope, then build.
- ① vector cutover — mostly mechanical, I propose+build (supervised flip).
- ② address surface — mechanical + a ledger-join dependency, supervised live-check.
- ③ UI — YOUR direction call (A/B/C).
Interlock: ①+② make the ledger THE live substrate; ③ is the window onto it. Natural sequence ①→②→③, but ③-C (a slice) could come early to give Tim sight fast. Tim sets it.
