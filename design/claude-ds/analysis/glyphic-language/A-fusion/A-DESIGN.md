# A — the AI/Company Fusion · grounded design

> Synthesis of the 6-read wave (`reads/READ-1..6`), all first-hand where it matters, cross-corroborated.
> A = make the design-system `CV_AI` a multi-provider registry resolved by role, **Company-default**, reaching
> the Company's local models + embedder; fuse the two overlapping AI systems into one; and let the AI consume
> the shared-selection substrate (`window.CV_GLYPHGRAPH_SESSION`) so you and it co-edit the glyphgraph.
> Home = `claude-ds` (decided). Everything here rests on read source, not memory. Status: DESIGN (not built).

## 0 · The make-or-break (front, because it's invisible without both codebases)
`CV_AI` is a **dumb-endpoint consumer** — it builds its own prompt (`cap.build`/`composeBehaviours`) and parses the
reply (`cap.parse`) [READ-3/6, ai-registry.js:278-317]. Every live Company brain route (`run_role`) is a **smart
endpoint** — the *role* owns the prompt/framing [READ-4/6, cognition.py:313]. **So the obvious fusion — point the
Company provider at `run_role` — DOUBLE-PROMPTS and fails on exactly the structured outputs the writer needs, while
looking fine on short prompts.** The word "role" collides (our "provider *role*-layer" ≠ Company's `run_role`),
which is what leads a builder into the trap. **The rule: `company-http` points at a NEW *dumb* `/api/complete`
(raw `client.complete`, no role framing); the Company's *smart* roles stay server-side as the extract-swarm.** This
single fact reshapes A and is why the read-wave was worth it.

## 1 · Transport — SAME-ORIGIN (the CORS gate, settled) [READ-5, first-hand]
The bridge (`:8770`) sends **zero CORS headers**, no `do_OPTIONS` (preflight → 501), binds 127.0.0.1 only. So a
static `:8775` `@dsCard` page **cannot** call it cross-origin. Resolution needs **zero `~/company` changes**: serve
the writer surface **same-origin**, two proven doors —
- **Door A — behind a vite `/api`→`:8770` proxy** (exactly how the live canvas + the Tailscale phone reach it;
  `canvas/app/vite.config.js:17-20`). → the writer surface becomes a vite app (aligns with the "surface/app" home).
- **Door B — bridge-served page** (the bridge's `do_GET` already serves `/`, `/studio`, `/mockups/`, `/design-system.css`).
**Consequence for the generator:** the current static specimen is a demo shell; the *real* writer surface must run
same-origin. **Decision for Tim:** Door A (vite app) vs Door B (bridge-served) — A is the canvas precedent, more flexible.

## 2 · The provider fusion — registerKind + role-indirection [READ-3/6]
Provider resolution today is a hardcoded kind-dispatch in **two homes** (`ai-registry.js:203-228`;
`host-runtime.js:158-168`) and `'claude'` is pinned across **~33 sites**. Design-for-the-class fix (both, not either):
1. **`CV_HOST.registerKind(kind, resolverFn)`** — a registry that dissolves both hardcoded `if`-ladders; a new
   provider kind = one registration, no call-site edits.
2. **Role indirection** — capabilities declare a *provider-role* (`text` / `embed`), one `ROLE_PROVIDERS` config
   maps role→provider id; the ~33 `'claude'` pins collapse to **one binding**. Flip to Company-local = one edit.
3. **`company-http` runtime kind** (modelled on `services/openai.js` direct-fetch) → same-origin `/api/…`.
   Routed through `CV_HOST`, so `ai-registry.js` stays untouched (the seam is the point).
The loud-fail law is currently *violated* by the `'claude'` fallbacks (`ai-registry.js:315/343`) — A removes them.

## 3 · The three real integration paths (do NOT conflate — the whole trap)
- **Path DUMB — `CV_AI` capabilities that build their own prompts** (e.g. `glyphic.generate`) → `company-http` →
  **NEW dumb `/api/complete`** (over `client.complete`, no framing). *(This is the one genuinely-new `~/company`
  route — see §6.)* `glyphic.generate` also currently ignores its resolved provider [READ-3, ai-glyphic.js:66] — fix that.
- **Path SMART — the extract/compose swarm** = **file-discovered Company roles** `roles/glyph_extract.py` /
  `glyph_compose.py` (mirror `element_fit_lens`/`embed` shape), fired via `run_role` / `run_items`×`run_reduce`
  (the map→reduce concurrency primitive) [READ-4]. These are **server-side, NOT CV_AI providers** — they own their
  prompts + `output_schema` (validated JSON). This is the real NL→graph meaning engine (Tim's extraction-vs-judgment).
- **Path EMBED — meaning→glyph resolution** → `/api/cognition/embed` (live **pplx-embed @ :8007, 2560-dim**;
  the BGE/:8001/1024 comments are STALE [READ-4]). `CV_AI` has no embed analog today → add an `embed` role/provider.

## 4 · Meaning-resolution + generate-on-miss (the writer's engine, embedding-backed)
Replaces the starter parser: describe → embed the phrase → nearest glyphic entry in a **`glyph_meaning` projection
space** (none exists yet — zero grep hits [READ-4]) → below threshold → the foundry generates one (Path DUMB) →
`glyphic.save` → freshness-reindex so it's instantly resolvable. Needs: (a) the `glyph_meaning` space + a
populate/embed pass over the glyphic library's tags/descriptions (fixes the live hand-typed-tag staleness), (b)
re-run on `CV_ICONS.add`. Deep-linked (embeddings reference entries, never copy). All **registry/data drops, no
engine work** [READ-4].

## 5 · Collaborative AI — consume the shared selection [READ-1, from C]
`window.CV_GLYPHGRAPH_SESSION {graph, selection, subscribers}` (built in C) is A's concrete contract: an AI
capability reads `.selection` + `.graph` as context (so "make these blocked" acts on what you selected) and can
push graph-ops back (the same typed ops C's mouse editing uses) — two hands on one graph. One-IR law holds: the AI
edits the one `CVGraph`, never a parallel model.

## 6 · What A adds to `~/company` (the charter nod) [READ-4/5/6]
Minimal, additive, registry/data-shaped — **only ONE is real code**:
- **NEW `/api/complete`** bridge route over `client.complete` (dumb completion, no role framing) — *the one new
  engine surface* (Path DUMB needs it; `run_role` must not be used). Small, additive to `bridge.py`.
- **`roles/glyph_extract.py` + `glyph_compose.py`** — file-discovered role drops (data-shaped, no engine edit).
- **A `glyph_meaning` projection space** + populate/embed/reindex (data/config).
This is the "unify INTO the Company" convergence — touching `~/company` with care. **Needs Tim's explicit nod**
(the design/CLAUDE.md "never modify ~/company" charter edit rides here).

## 7 · Guardrails — the silent-failures A must not ship [READ-4/6]
- **Assert `satisfied == True`**, never truthiness — a role silently floors to the resident 4B otherwise
  (`roles.py:424`); and the fire path does NOT apply `model_binding.requires` → **pass `model=` explicitly** [READ-4].
- **Treat `ok:false` as an error** — the bridge returns it inside HTTP-200 (`bridge.py:2594`).
- **Read `maxPromptChars` from the live `max_model_len`** — hardcoded 200000 chars (~50k tok) silently overflows
  the 32k local brain [READ-6].
- **Embed fails loud if the embedder is down** unless `ensure:true` [READ-5] — surface a Notice, never a silent null.
- **Hardware honesty:** one 16GB card, one resident brain, measured knee ≈ **2-wide** [READ-4]; schema fires
  `think=False`. The extract-swarm = short schema-constrained roles in **bursts at pauses**, not an always-on fleet.

## 8 · The one-law frame
The fleet enters as **`CV_AI` providers** — a *fifth consumer* of the registries, **never a second model client or
a fifth registry** [READ-2/6]. CV_MODE (browser click-dial) and Company `modes_registry` (server presence) are two
axes on one mechanism — **reconcile, don't merge** [READ-2]. Everything resolves; nothing hardcodes.

## 9 · Build sequence (folds into the plan; grounded, sequenced, no "later")
- **A1 · registerKind + role-indirection** in `CV_HOST`/`CV_AI` (dissolve the 33 pins; `ROLE_PROVIDERS`; loud-fail restored).
- **A2 · `company-http` runtime + `/api/complete`** (the dumb route) + same-origin transport (Door A vite proxy) — verify end-to-end with a real `client.complete` round-trip.
- **A3 · `embed` role/provider** → `/api/cognition/embed`; the `glyph_meaning` space + populate/embed/reindex.
- **A4 · meaning-resolution + generate-on-miss** in the writer (replace the starter parser with embed-nearest + foundry-on-miss).
- **A5 · the extract/compose Company roles** (`roles/glyph_*.py`) + the map→reduce pipeline — the real NL→graph.
- **A6 · collaborative AI** — consume `CV_GLYPHGRAPH_SESSION`; AI acts on selection + pushes graph-ops.
Each verified by USE; guardrails (§7) are acceptance criteria, not polish.

## 10 · Honest opens for Tim
- **Door A (vite app) vs Door B (bridge-served)** for the same-origin surface. *(rec: A)*
- **The `~/company` additions (§6) — the charter nod** (the `/api/complete` route especially).
- Where the writer surface lives given home=claude-ds + the counterpart/design convergence.
- `/api/stream` carrying graph-deltas is **inferred, not yet verified** [READ-5] — confirm the `_emit` sites before relying on it for live delta-flow.
