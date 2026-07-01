# A — the AI FUSION (union, not bridge) · grounded design

> Synthesis of the 6-read wave (`reads/READ-1..6`), first-hand + cross-corroborated, reframed after Tim: this is a
> **UNION, not a bridge.** The design-system `CV_AI` and the Company's cognition are the *same AI, built twice*
> (near-isomorphic [READ-6]). A collapses them into **ONE AI registry with ONE home, of which the browser is a
> projection** — the same law as everything else in the system (registry-is-truth · resolve-from-one-source ·
> unions-not-bridges · islands-join-mainland). Home(design system)=claude-ds (decided); **home(the AI)=the Company**
> (it holds the substance: the models, the embedder, the concurrency, the corpus, the file-discovered roles).
> Status: DESIGN. (Supersedes the earlier bridge-framed draft, which left two registries standing.)

## 0 · The thesis — collapse two into one
Today there are **two registries of "how the system uses AI"** with a near-perfect overlap [READ-6]:

| CV_AI (browser, claude-ds) | Company cognition (server) | → fused concept |
|---|---|---|
| provider (model endpoint) | brain / model | **MODEL** |
| capability (a move: build·run·parse) | role (owns prompt + `output_schema` + model-binding) | **CAPABILITY** (= a role) |
| behaviour (voice/angle fragment) | behaviour | **BEHAVIOUR** |
| context (surface→prompt-context) | context | **CONTEXT** |
| skill (named user intent) | skill | **SKILL** |
| — (none) | the embedder, run_swarm concurrency, corpus | **(Company-only substance)** |

That overlap **is the duplication to dissolve.** The fusion: **one registry of these typed entries, one home, and
`CV_AI` becomes the browser *face* of it** — it defines no AI of its own; it resolves the one registry, runs the
pure-function entries locally, and fires the model entries through the Company. No second home → no drift.

## 1 · The move that makes it a union, not a bridge (and removes the trap)
READ-6 caught that pointing a browser "provider" at `run_role` **double-prompts** (CV_AI builds a prompt *and* the
role injects its own). My earlier draft "fixed" that by adding a *dumb* `/api/complete` to accommodate CV_AI's
prompt-building — **that's the bridge: it keeps CV_AI a separate prompt-owner.** The **union heals it instead**:
**a model-using capability *becomes a role*** — a typed entry that **owns its prompt + `output_schema`** (the
single-source, smart convention the Company already uses [READ-4, cognition.py:313]). So:
- The browser **stops hand-building prompts in JS** (which drift from the Python roles). A capability *is* a role.
- Model capabilities **fire through the existing `run_role`** — no dumb endpoint, no double-prompt, no new engine
  surface for completion. The asymmetry (dumb-consumer vs smart-endpoint) **dissolves** because there's one convention.
- Pure-function capabilities (`glyphic.author`, `read`, `describe`, `transglyph` — no model) **stay browser-resolved.**
So the registry's resolver decides *where an entry runs*: **pure-fn → in the browser; model-role → through the Company.**
One registry, one definition per thing, execution resolved to where it belongs. *That* is the fusion.

## 2 · One home, one registry (what lives where)
- **Home of the AI registry = the Company** — models (`services.json` + the model/brain registry), the file-discovered
  **roles** (`roles/*.py`, drop-in [READ-4]), behaviours, contexts, the embedder (**pplx-embed @ :8007, 2560-dim**),
  the map→reduce concurrency, the corpus. The design-system's ~43 CV_AI capabilities/behaviours/contexts **fold IN**
  as entries (islands-join-mainland) — the model-using ones become roles; the pure-fn ones register as browser-run entries.
- **`CV_AI` (claude-ds, browser) = the projection** — it *resolves* the one registry (over the same-origin wire),
  exposes the entries relevant to the active surface, runs pure-fn entries locally, and fires model-role entries via
  the Company. It keeps its good shape — the **surface/context projection model + the capability UX** — but as a
  *view of the one registry*, not a second registry. (This is the same pattern as the design system's UI being "a
  projection of the registries," now across the browser/server line.)
- **Best of both, kept:** Company's real models/roles/embedder/concurrency/corpus + CV_AI's clean
  registry-projection + surface-context + capability-UX. Neither is discarded; they become one.

## 3 · The transport is just the wire the projection crosses (plumbing, not the fusion)
The browser and the models sit on different sides (JS vs Python), so the projection reaches the one registry over
HTTP — **this is plumbing under the union, not the union itself** [the mistake in the earlier draft was calling it
the fusion]. Grounded facts [READ-4/5]:
- **Same-origin required** — the bridge (`:8770`) sends zero CORS, binds 127.0.0.1 (preflight→501). So the browser
  face is served **same-origin**, zero `~/company` change: **Door A** = a vite `/api`→`:8770` proxy (the canvas +
  phone precedent) or **Door B** = bridge-served. *(Decision for Tim; rec: A.)*
- The projection uses the **existing** routes: `POST /api/cognition/run_role` (fire a capability-role → validated
  JSON against its schema), `POST /api/cognition/embed` (meaning→glyph resolution; pplx@:8007), `GET
  /api/corpus-query`, `GET /api/stream` (SSE — live deltas). **No new completion route needed** (the union removed it).

## 4 · What the fused AI then powers (the writer, for real)
- **Meaning→glyph resolution** (replaces the starter parser): describe → embed → nearest glyphic in a **`glyph_meaning`
  projection space** (build it; none exists [READ-4]) → below threshold → generate-on-miss (a *generate* capability-role)
  → save → reindex. Fixes the live hand-typed-tag staleness. Registry/data drops, no engine work.
- **NL→graph** = the **extract + compose capability-roles** (`roles/glyph_extract.py`, `glyph_compose.py`), fired
  via `run_role` / `run_items`×`run_reduce` (Tim's extraction-vs-judgment = the concurrency primitive). These are
  entries in the ONE registry, resolved server-side.
- **Collaborative co-edit**: an AI capability reads `window.CV_GLYPHGRAPH_SESSION` (your selection, from C) as context
  and pushes graph-ops back — two hands on one `CVGraph`. One-IR holds.

## 5 · Guardrails (the silent-failures the reads found — acceptance criteria, not polish)
Assert `satisfied==True` + pass `model=` explicitly (the fire path doesn't apply `model_binding`; roles.py:424 floor
trap) [READ-4] · treat `ok:false` as an error (it rides inside HTTP-200; bridge.py:2594) [READ-6] · `maxPromptChars`
from the live `max_model_len`, not hardcoded 200k (overflows the 32k brain) [READ-6] · embed fails loud unless
`ensure:true` [READ-5] · one 16GB card, knee ≈ 2-wide, `think=False` for schema, **burst-at-pause not always-on** [READ-4].

## 6 · What A adds to `~/company` (the charter nod) — smaller than the bridge version
Because model-capabilities-become-roles fire through the *existing* `run_role`, A adds **no new completion engine**.
The `~/company` additions are **registry/data-shaped**: the folded-in capability **roles** (`roles/glyph_*.py`,
drop-in), the **`glyph_meaning` projection space** + populate/embed/reindex, and the design-system capabilities' entries
migrating to the one registry. This is "unify INTO the Company," done as data, not engine surgery — **needs Tim's
explicit nod** (the design/CLAUDE.md "never modify ~/company" charter edit rides here).

## 7 · The structural fix that makes CV_AI a projection [READ-3]
`CV_HOST.registerKind(kind, resolverFn)` (dissolve the two hardcoded dispatch homes) + a **role-indirection** so
capabilities declare a provider-role and one binding maps it → collapses the ~33 `'claude'` pins to **one** and
restores loud-fail (the `'claude'` fallbacks at ai-registry.js:315/343 currently violate it). The one binding points
the whole projection at the Company.

## 8 · Build sequence (the union, sequenced — folds into the plan)
- **A1 · One registry, projection seam** — `registerKind` + role-indirection; `CV_AI` resolves entries from the one
  home instead of self-defining; collapse the 33 pins; restore loud-fail. Same-origin transport (Door A).
- **A2 · Model-capabilities → roles** — migrate the model-using CV_AI capabilities to typed roles (own prompt+schema),
  fired via `run_role`; pure-fn capabilities stay browser-run. (This *is* the fusion; verify the double-prompt trap is gone.)
- **A3 · Embed + `glyph_meaning` space** — the `embed` path + the projection space + populate/reindex.
- **A4 · Meaning-resolution + generate-on-miss** in the writer (embed-nearest + generate-role-on-miss; retire the starter parser).
- **A5 · Extract/compose roles** — the NL→graph pipeline (`glyph_extract`/`glyph_compose` + map→reduce).
- **A6 · Collaborative AI** — consume `CV_GLYPHGRAPH_SESSION`; act on selection + push graph-ops.
Each verified by USE; §5 guardrails are acceptance criteria.

## 9 · Decisions for Tim
- **Home of the AI = the Company** (my grounded call — it holds the substance; CV_AI folds in as projection). Confirm or redirect.
- **Door A (vite app) vs Door B (bridge-served)** for the same-origin face. *(rec: A.)*
- **The `~/company` additions (§6) — the charter nod.**
- Confirm `/api/stream` carries graph-deltas before relying on it (inferred [READ-5]).
