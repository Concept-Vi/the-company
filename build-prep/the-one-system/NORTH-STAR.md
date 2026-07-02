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

## STILL TO WRITE (same depth, next): ② the address surface change · ③ the fork (UI).
