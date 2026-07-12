# B — Resolved-Context: the architecture (grounded on A)

> A dynamic context-management layer: hooks + local AI judges RESOLVE an agent's context each turn from a
> durable, addressed substrate — instead of the append-only accumulate + lossy black-box compaction we have now.
> Tentative; assumptions marked [assume]; grounded in A's experiments (V1–V3, B1) + the live local Supabase.
> Store = LOCAL Supabase/Postgres (:15432, pgvector), beside the embedding session's `ledger.*`.

## 0 · Thesis
**Accumulated context** (today): history is append-only; when it overflows, an opaque compaction decides what
survives — the user has no say (this is literally the "old version" failure we hit). **Resolved context**
(this): every turn, context is *computed* from a substrate by cheap local judges — the same law as the rest of
the system (resolve-from-source, deep-link, registry-is-truth), now turned onto the agent's own working memory.
*Context-is-the-asset, made operational.*

## 1 · The circuit (one unbroken flow)
```
transcript/turn ─▶ HOOK (UserPromptSubmit / SessionStart:compact)
                     │  emits {session, prompt, transcript_path, source}
                     ▼
                 BRIDGE  (same-origin/local :8770)
                     │  embed(prompt) ─▶ MATCH vector spaces + the context-ledger
                     │  run_role(judge)  ─▶ typed VERDICT (structured output)
                     ▼
              VERDICT  {resolve:[spans], inject:[context], prune:[ids], pin:[ids], recall:[hits]}
                     │
                     ▼
             DISPATCH (registered, fail-loud — never hardcoded ifs)
                     │  stdout(resolved context)  ← the sanctioned injection seam (A/V1 proven)
                     ▼
             the model's turn runs on RESOLVED context
```
Everything is addressed; nothing hardcoded; the judge EXTRACTS + a decision layer JUDGES (extraction-vs-judgment).

## 2 · Two channels (both grounded in A)
- **Turn-resolution — LIVE, works today [A/V1 Verified].** `UserPromptSubmit` hook → bridge → resolved context
  on **stdout (exit 0)** → enters the turn as a system-reminder. This is the whole live loop; the spine
  (embed@:8007 + run_role 0.72s) is already proven. First to build.
- **Boundary-recomposition — supported paths [A/B1 Blocked in-place].** In-place rewrite of a live CLI session's
  `.jsonl` is guarded by the harness ("Session Transcript Tampering") — so recomposition is done by:
  (a) **`SessionStart matcher:"compact"`** re-injecting the resolved salient context AFTER the built-in
      compaction (the depth-preserving fix to the exact failure we lived); and
  (b) **the agent-SDK loop** — where the Company runs its own sessions and OWNS the messages array outright: full
      prune/replace/pin with no CLI transcript guard. This is the no-limits path for total recomposition. [assume:
      the Company's cognition loop can host the wrapped session; verify at build.]
  PreCompact is observe-only (cannot steer the summarizer) — so steer via SessionStart:compact, not PreCompact.

## 3 · The substrate — LOCAL Supabase/Postgres (:15432, pgvector)
Beside `ledger.*` (convergence — one local Postgres). Proposed schema `ctx.*` [assume names]:
- **`ctx.span`** — one row per addressable conversation unit: `{id, session_id, uuid (the jsonl node), parent_uuid,
  role, ts, text, token_est, address}`. The transcript tree (A/V3) mirrored into queryable rows.
- **`ctx.verdict`** — the JUDGE's typed tags on a span (the "context ledger"): `{span_id, kind (decision|fact|
  preference|scaffold|noise|superseded), salience 0-1, supersedes[], lod (full|gloss|omit), gloss_text, judged_at,
  model}`. This is what makes the history a **typed graph** — the conversation becomes a glyphgraph.
- **`ctx.embedding`** — `{span_id, space='ctx', emb='pplx', vec_2560}` — a space on the SHARED store (no fork; same
  pattern as glyph_meaning rides ledger.embedding). Powers semantic recall.
- **`ctx.rule`** — standing resolved-context rules (project/session-scoped): what must always be present.
Reads = live truth; the store is the single home for "what the agent should be holding."

## 4 · The judges (cheap, local, concurrent — burst per turn)
Drop-in `run_role` roles (file-discovered, like the glyph roles), each schema-constrained:
- **`ctx_recall`** — embed the incoming prompt → nearest spans across ctx.embedding + ledger spaces → the
  relevant past (recall becomes the FABRIC of context, not a tool the agent calls — the grounded-chain law).
- **`ctx_salience`** — judge a span/turn: `{kind, salience, supersedes[], lod}` → writes ctx.verdict.
- **`ctx_compose`** — given the turn + the ledger, decide the resolved injection: pin the critical, gloss the
  stale, omit the dead, recall the relevant → the stdout payload.
Extraction (many small models) feeds judgment (one composer) — never let extractors decide.

## 5 · The viewport / LOD (your spatial theorem, on conversation)
The full history is an infinite, addressed space; each span renders at a **zoom level** the resolver chooses:
full-text → gloss → **absence-with-an-address** (the span still exists at its id, just not rendered). The 200k
window is the current LOD, not the limit. Semantic zoom over the agent's own past. [assume: realised by WHAT the
resolver injects (§4 ctx_compose choosing lod per span), NOT by editing the raw transcript — per B1.]

## 6 · Honest constraints + the total-control path
- Live CLI sessions: resolve-and-INJECT (add), plus boundary re-injection — the harness guards in-place history
  edits (A/B1). Good enough for turn-resolution + compaction-survival.
- Full recomposition (prune/replace the actual working set mid-run): the **agent-SDK loop** (Company-owned
  messages array). That's where "replace/alter/manipulate the history" fully lives, safely, by design.
- So: CLI gets *resolved injection*; SDK-hosted sessions get *resolved composition*. Same substrate, two depths.

## 7 · Build path (walking-skeleton first — the spine's proven)
- **S1 · live turn-resolution skeleton:** one `UserPromptSubmit` hook → bridge → embed+`ctx_recall` → inject
  resolved context on stdout, in one real session. (Hours — V1 proves the seam.)
- **S2 · the substrate:** `ctx.*` in local Supabase; mirror a session's tree into `ctx.span`; embed → `ctx.embedding`.
- **S3 · the judges:** `ctx_salience` + `ctx_compose` roles → the context-ledger fills; injection becomes *composed*.
- **S4 · compaction-survival:** SessionStart:compact re-injection (kills the "old version" failure).
- **S5 · SDK composition:** the total-control path for Company-hosted sessions (prune/replace/pin the messages array).
- Each verified by USE (feel it in a live session) + against the substrate; commit small; loud-fail.

## 8 · Why it's one system
Resolve-from-source on working memory · recall becomes the fabric (the recall-substrate mission's live face) ·
the conversation becomes a typed graph = a glyphgraph (same language, another altitude) · the window becomes a
viewport (the spatial theorem). And it dissolves the failure we just lived: context stops being an accumulate-
then-lose pile and becomes a resolved, addressed, judged, zoomable substrate.
