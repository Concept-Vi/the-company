# A — CONTINUATION RECORD (start here after a resume / time-travel)

> **Purpose:** the durable "you are here, continue from here" for the Glyphic AI/Company FUSION build (A).
> Written 2026-07-02 by the opus session (0e68d462-…) so a resumed/time-travelled session continues with zero
> guesswork. If this doc has MOVED (the reorg fork is relocating plans/process docs onto the board + build-prep),
> follow the pointer the fork leaves; the canonical A-design is `A-DESIGN.md` beside this, the sequence is `../ROADMAP.md`,
> and the always-loaded running record is memory `project-glyphic-language.md`. Read those three + this.

## The one-line state
**A0 (spine) DONE. A1 (the fusion seam) DONE + acceptance-verified. NEXT = A2 (point the seam at the Company) → A3
(the glyph_meaning space on the shared vector store) → A4 meaning-resolution → A5 extract/compose roles → A6 collaborative AI.**

## Ground truth (verified live 2026-07-02 — don't re-discover)
- Services UP: bridge `:8770` · embedder pplx-embed-context @ `:8007` (2560-dim) · `run_role` route live.
- SPINE PROVEN in-browser same-origin: `POST /api/cognition/run_role {role,utterance}` WITH an output_schema → validated JSON in ~0.7s; `POST /api/cognition/embed {text}` → 2560-dim vector. (Probe: `~/company/surface/app/public/glyph-skeleton.html`, served by the instrument-surface vite dev server on `:5174`, `/api`→:8770 proxy.)
- `~/company` on `main` @ `c9ed303b` (the embedding session's ledger+embedding+Supabase build landed). My commits ride main.
- The SHARED vector store is BUILT: `ledger.embedding` @ `:15432` (pgvector, 26 spaces, halfvec multi-dim incl. vec_2560 for pplx, HNSW, ~76k vectors). Embed primitive = `~/company/ops/build_embeddings.py`; migrate = `~/company/ops/migrate_vectors_to_supabase.py`; schema = `~/company/build-prep/the-one-system/SUPABASE-VECTOR-SCHEMA.md`.

## What A1 actually did (the seam — all in claude-ds, its OWN git repo)
Commits: `75f2202` baseline → `4f64d89` seam → `89df4f3` migrate-41 → `f96d6d0` remove-fallback/loud-fail → `a1c1a30` AtomiCity sweep. All synced to canonical (DNA Studio c8f43c46-…).
- **`app/ai/ai-registry.js`**: added `ROLE_PROVIDERS = { text:'claude', image:'openai-image' }` + `providerForRole(role)` + `providerIdFor(cap)`; `execute()` resolves `cap.provider || role→provider`; `normalize()` carries `role`; `complete()` routes via `providerForRole('text')`; build/parse path THROWS if no provider (loud-fail, no silent claude).
- **`app/ai/host-runtime.js`**: added `CV_HOST.registerKind(kind, resolverFn)` + `KINDS` map checked FIRST in `resolveProviderRuntime` (beside the built-in kind dispatch — the seam A2 plugs `company-http` into).
- **All 55 caps migrated**: 41 text-caps declare `role:'text'` (via the 3 factory templates + glyphic.generate + AtomiCity's 7); the 8 non-text keep explicit `provider` (host-fs/openai-image/vision); 6 pure-fn unchanged.
- **ACCEPTANCE (grep whole tree):** ZERO `provider:'claude'` literals, ZERO direct `window.claude.complete` calls. 'claude' lives in exactly TWO homes: the `ROLE_PROVIDERS` binding + the `kind==='claude'` dispatch it names. **Flip-to-Company = ONE edit (`ROLE_PROVIDERS.text`).**
- **Verified by USE:** Studio boot-check (55 caps, resolved-kind == `baseline-resolution-map.json`, 0 broken) POSITIVE + unbound-cap-THROWS NEGATIVE (loud-fail proven). The oracle to re-verify against is `baseline-resolution-map.json` (its `_reverify_check` field has the eval).

## A2 — point the seam at the Company (NEXT). Design-side + first real ~/company reach.
Goal: text/embed roles resolve to the Company over the bridge, so flipping `ROLE_PROVIDERS.text` → the Company actually reaches your models.
1. Build a **`company-http` runtime kind**, registered via `CV_HOST.registerKind('company-http', fn)` (the seam is already there). Model it on `app/ai/services/openai.js`'s direct-fetch. It calls the bridge same-origin (`/api/cognition/...`).
2. Register a Company **provider** record `{ id:'company', runtime:{ kind:'company-http', ... } }` in `ai-seed.js`.
3. Add an **`embed`** role + `embed` support (the writer's meaning-resolution needs `POST /api/cognition/embed`).
4. **THE TRAP (from READ-6 — do not forget):** CV_AI capabilities that build their own prompt must NOT be double-prompted by a smart `run_role`. The union reframe (A-DESIGN §1): a model-using capability BECOMES a role that owns its prompt+schema, fired via `run_role`; the browser stops hand-building that prompt. For the plain `complete()`/text path, resolve to a completion that does NOT re-inject role framing. Re-read A-DESIGN §0-3 before wiring — this is the make-or-break.
5. **Transport:** the surface must be SAME-ORIGIN to :8770 (bridge has no CORS). Use the vite `/api` proxy (surface/app on :5174) OR bridge-served. Static :8775 pages CANNOT reach the bridge — that's why the A0 probe lives in surface/app.
6. Verify by USE: flip `ROLE_PROVIDERS.text` to `company` in a served surface, confirm a real `run_role`/`complete` round-trips + the boot-check still holds. Keep `claude` as the default binding until proven.

## A3 — the glyph_meaning space (needs ~/company write → ADVISOR GATE first)
Converged with embedding session (see below). NO fork — my A3 = ONE space on their store:
1. **advisor() BEFORE the first substantive ~/company write.**
2. VERIFY `ledger.embedding` @ :15432 + `ops/migrate_vectors_to_supabase.py` BY USE first (not-a-replacement law — run it, don't assume).
3. Register `glyph_meaning` as ONE SPACES row in `ops/build_embeddings.py`: `kind='fabric', emb='pplx', dim=2560`.
4. Write `corpus_for_glyph()` → `[{address, text}]` — each glyphic-library entry's tags/description as text, keyed by glyphic address + content_hash.
5. Migrate: `ops/migrate_vectors_to_supabase.py --space glyph_meaning`. Verify vectors landed (query nearest-neighbor).
6. Commit to `~/company` **main** (small commits; repo law — no feature branch, no co-author trailer).

## A4-A6 (after A3)
- A4: meaning-resolution + generate-on-miss in the generator — replace the starter `M.parse` with embed-nearest over glyph_meaning; below-threshold → glyphic.generate (foundry) → save → reindex.
- A5: `roles/glyph_extract.py` + `glyph_compose.py` (file-discovered drop-ins on ~/company) — the NL→graph extract/judge pipeline via run_role / run_items×run_reduce.
- A6: a capability reads `window.CV_GLYPHGRAPH_SESSION` (selection+graph, built in generator step C) + pushes graph-ops → collaborative co-edit.

## Coordination state (the fabric — cross-session convergence)
- My session `0e68d462-5d0d-465e-977a-7b6b92911b77` is REGISTERED (ran ops/agent_sessions_importer.py) + joined `channel://provider-registry` + `channel://design-fusion`. Profile set (company-channel).
- Converged with the EMBEDDING session (`ch-5wog4hmx`) on **thread `t-1782921350-ch-518m76r0`** (company-channel `reply` pushes to it; their loop polls it): SAME pplx-2560 embedder, SUPABASE backend, my glyph_meaning = space #27 on their store, no fork. Their branch LANDED to main. They're drafting `CODE-ADDRESS-RECONCILIATION.md` (canonical `code://<project>/<path>::<symbol>` — TOUCHES my design-side stem-form in `_system/symbols.py`+refcheck+addresses.json; I agreed to align → ONE address scheme, glyph://+code://+file://).
- The REORG FORK is separately moving the plan/process/research/coordination docs OUT of claude-ds onto the board + `build-prep/the-one-system/`. KEEP in claude-ds: the engine, surfaces, registries, LANGUAGE.md, the language-arc/meaning docs. If docs moved, the board/build-prep is their home now.

## Laws every step (do not drop)
loud-fail (guard: assert `satisfied==True`, pass `model=` explicitly, treat `ok:false`-in-HTTP-200 as error, prompt-cap from live `max_model_len` not 200k, embed fails-loud) · nothing hardcoded (resolve via registry/context; write howtos) · verify by USE + practically-useful (technical success is half) · git commit per verified step (claude-ds repo for design-side, ~/company main for A3+) · sync diff-first to canonical after design-side · one-IR / unions-not-bridges / one-address-scheme · advisor() before A3's first ~/company write + any unplanned destructive change · NEVER break a running ~/company service.
