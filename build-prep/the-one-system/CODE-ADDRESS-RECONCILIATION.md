# code:// address reconciliation — the plan (needs Tim's eyes on the live-surface cutover)

*Tim AUTHORIZED the ledger form as canonical. This is the precise change-set. The DATA parts (corpus re-address, provenance join) are safe/additive and done or doable unattended; the LIVE-SURFACE part (`resolve_scope` / the S3 `ui://→code://` resolver in suite.py) is the ONE thing that can break live chat/the surface, so it is drafted here for Tim to run WITH him watching — not executed overnight (the "never break the live surface" law overrides even an authorized change when it's unattended).*

## The three forms (recap)
1. **Ledger + all embedding spaces + provenance edges (CANONICAL):** `code://<project>/<path>::<symbol>` — e.g. `code://company/runtime/suite.py::Suite.chat`. Unambiguous.
2. **Contract declaration + S3 surface / `resolve_scope`:** `code://<file-stem>/<symbol>` — e.g. `code://suite/review_verdicts`. Lossy (stem collisions, no project).
3. **Corpus `repo` space rows:** `code://<path>` (no project).

## What's ALREADY canonical (no work)
- The whole embedding layer (code/symbol/docs/desc) → `code://company/<path>[::<sym>]`. ✓
- The provenance `generated-by` edges → `code://company/<path>`. ✓
- The ledger itself (entry/symbol/edge) → canonical. ✓
So the *new* substrate is already on the canonical form. Only the OLDER corpus/repo space + the S3 surface diverge.

## The change-set

### Part A — corpus `repo` space (DATA, safe/additive, unattended-OK)
The `repo` space (1292 vectors) uses `code://<path>` / `code://<stem>`. It's now duplicated by the richer `code` space (`code://company/<path>`, nomic). **Recommendation: retire the legacy `repo` space** (the `code`+`symbol` spaces supersede it — real parser, canonical addresses, better model) rather than re-address it. Verify nothing queries `repo` exclusively first (grep `space=.repo`/`query_corpus.*repo`). If something does, alias its addresses to canonical. Additive → verify → retire.

### Part B — the S3 surface `resolve_scope` (LIVE CODE — Tim-supervised)
`runtime/suite.py::resolve_scope` + the `ui://→code://→scope[]` resolver read the corpus with `code://<file-stem>/<symbol>`. Contract: `contracts/address.py` line 9 declares the stem form.
**Additive-alias approach (the safe cutover):**
1. Teach the resolver to ACCEPT BOTH forms: try canonical `code://<project>/<path>::<sym>` first, fall back to the stem form (or normalize stem→canonical via a path lookup). Keep the stem alias working.
2. VERIFY by use: drive a real `ui://` resolve + a chat turn that hits `resolve_scope`; confirm the S3 surface still returns scope. (This is why it's Tim-supervised — the acceptance is a live chat/surface check.)
3. Only after both forms verified: update `contracts/address.py`'s `code://` declaration to canonical (+ note the stem alias), and migrate any stored stem-form addresses.
4. NEVER retire the stem path until a live surface check passes on canonical.
**Files:** `runtime/suite.py` (resolve_scope + the S3 resolver — MODIFY additively), `contracts/address.py` (the scheme doc — update after verify), `tests/*acceptance*` touching `resolve_scope`/`ui://` (run them as the gate).

### Part C — provenance path-join (DONE)
`file://<abs> ↔ code://company/<path>` join landed 1403 `generated-by` edges. ✓

## Why B is NEEDS-TIM (not done overnight)
`resolve_scope` is on the live chat/S3 surface path. An additive alias SHOULD be safe, but the only real verification is a live surface/chat check, and an unattended mistake here breaks the operator's surface silently until morning. Tim's law: never break the live surface. So: A + C done/doable unattended; **B waits for Tim** (a ~15-min supervised change: add the alias, drive a live resolve, confirm, then flip the contract).
