# AREA 1 — CV_AI + its provider layer: making it a multi-provider registry resolved by role/id

> Companion to `../ANCHOR.md`. My territory: `app/ai/` (the `CV_AI` registry + provider resolution)
> and what it takes to register **openai · google · and PRIMARILY the Company-local fleet** as
> providers *resolved by role/id*, without hardcoding call-sites — the governing no-staleness law.
> Marks: **Observed (file:line)** / **Inferred** / **External** / **My-idea**. Expansion-ratio > 1.

---

## 0 · TL;DR (the contradiction, held in both halves)

The anchor (§4, §7) says *"currently `CV_AI` assumes a single `claude` provider."* That is **half
true, and the wrong half to lead with.** Precisely:

- **The PLUMBING is already multi-provider.** `CV_AI` is a layered registry with a `provider`
  layer, a `resolveProvider(id)` that binds a record to a *live runtime*, and a **delegation seam**
  (`CV_HOST.resolveProviderRuntime`) for runtime kinds `CV_AI` itself doesn't know how to reach.
  Six provider records are already seeded: `claude`, `openai-image`, `vision`, `host-fs`,
  `native-model`, `mcp-tools`. **Observed** (`app/ai/ai-seed.js:21-43`, `app/ai/host-serializer.js:132-154`).
- **The RESOLUTION is a `claude` monoculture.** Every *text* generation path is pinned to the
  literal string `'claude'` — at ~30 capability registrations + 2 fallbacks. That pin, not the
  registry shape, is what §5 (the no-staleness law) is actually about. **Observed** (enumerated in §2).

So the work is **not** "add a provider layer" (it exists) and **not** "add provider records"
(trivial). The work is a **role-resolution layer** so a capability declares a *role* (`compose-graph`,
`extract-entities`, `chat`) that resolves to a provider from one config map — exactly the anchor's
`cognition-is-role-resolved` law and exactly what the Company already does (`run_role` /
`models_for_role`). Flip the whole DS from claude→Company-local with **one edit**; add openai/google
text with **a row + a binding**, zero call-site edits.

And the browser↔server boundary (§4, the `(d)` question) resolves to: **call the Company bridge at
`:8770` over HTTP** (the vLLM model ports have *no CORS*) — a new direct-`fetch` runtime kind modelled
on the existing `openai.js` direct-to-OpenAI shape. The `native-model`/`CV_HOST_NATIVE` path the seed
*names* is **export-host vaporware** — nothing in-repo injects it — so it is NOT the recommended path.

---

## 1 · (a) The EXACT shape of a provider record + how a capability resolves one

### 1.1 A provider record (the data shape)

A provider is just a `CV_AI` entry with `layer:'provider'`. `normalize()` is the canonical schema.
The provider-relevant fields: **Observed** (`app/ai/ai-registry.js:159-191`):

```js
{
  id, name, layer:'provider', family,           // identity + grouping
  description, icon, provenance, tags,
  runtime: { kind: '…', model?: '…' },           // ai-registry.js:183 — HOW to reach the live endpoint
  modality: ['text'] | ['text','stream'] | ['image'] | ['fs'] | ['tool'],  // :184
  caps: { stream, json, maxPromptChars, … },     // :185 — declared capabilities
}
```

The seeded records (the real corpus today): **Observed**
- `claude` — `runtime:{kind:'claude'}`, `modality:['text','stream']`, `caps:{stream,json,maxPromptChars:200000}` (`ai-seed.js:21-27`)
- `openai-image` — `runtime:{kind:'openai-image'}`, `modality:['image']` (`ai-seed.js:29-35`)
- `vision` — `runtime:{kind:'vision'}`, `modality:['image','text']`, `caps.exportOnly:true` (`ai-seed.js:37-43`)
- `host-fs` — `runtime:{kind:'host-fs'}`, `modality:['fs']` (`host-serializer.js:132-137`)
- `native-model` — `runtime:{kind:'native-model'}`, `modality:['text']`, `caps.json:true`, tag `export-only` (`host-serializer.js:143-148`)
- `mcp-tools` — `runtime:{kind:'mcp-model'}`, `modality:['tool']` (`host-serializer.js:149-154`)

**The `runtime.kind` is the dispatch key.** It is the one field that says "how do I become a live,
callable thing." `caps`/`modality` are *declared* metadata (no resolver enforces them yet — see §5.4).

### 1.2 How a capability resolves a provider — the call chain

`execute(capabilityId, …)` is the one generative path. **Observed** (`ai-registry.js:278-317`):

1. `resolve(capabilityId)` flattens the capability with its `extends` ancestors (`:279`, `:135-148`).
2. If it's a `skill`, delegate to its `target.capability`, threading the instruction as the brief (`:283-291`).
3. `mergedParams` = capability defaults ⊕ call params ⊕ brief (`:294`).
4. `resolveContext({surface, doc, ctx})` projects the active screen into a context object (`:295`).
5. **Provider resolution (the hinge):** `const provider = cap.provider ? resolveProvider(cap.provider) : null;` (`:299`).
   - A *pure-`run`* capability (`provider:null`, no LLM — e.g. `glyphic.save`, `glyphic.author`) gets `null` and never touches a runtime. This is the recent change the anchor §7 mentions. **Observed** (`ai-glyphic.js:74` `provider:null`; `ai-registry.js:296-299` comment + code).
6. **Two execution shapes:**
   - **`run()` path** (`:304-307`) — the capability owns build→complete→parse; it receives the resolved `provider` (or `null`), context, behaviour preamble, brief. Most capabilities use this.
   - **`build`/`parse` path** (`:309-316`) — pure-data capability; the registry calls `(provider || resolveProvider('claude')).complete(...)`. **← the first hardcoded `claude` fallback.**

`resolveProvider(id)` (`ai-registry.js:198-238`) is the **runtime binder**. It:
- looks the record up; throws loud if missing / not a provider (`:200-201`),
- branches on `runtime.kind`:
  - `'claude'` → binds `window.claude.complete` (throws if absent — `:203-214`),
  - `'openai-image'` → binds `window.cvOpenAI` image methods (`:215-228`),
  - **anything else** → delegates to `window.CV_HOST.resolveProviderRuntime(p)`; if `CV_HOST` returns a bound runtime, use it; else **throw** unknown-kind (`:229-237`).

`CV_HOST.resolveProviderRuntime(p)` (`host-runtime.js:155-170`) handles:
- `'host-fs'` → file ops (`:158-159`),
- `'native-model'` | `'mcp-model'` → bind `window.CV_HOST_NATIVE.complete(model, prompt, opts)`; **throws if `CV_HOST_NATIVE` absent** (`:162-167`),
- else `return null` → CV_AI throws its own unknown-kind error (`:169`).

> **The seam is already cut.** `CV_AI` resolves a provider it doesn't understand by *asking
> `CV_HOST`*. This is the exact extension point for Company-local models — but the only runtime-kind
> `CV_HOST` knows for models is `native-model`/`mcp-model`, both gated on `CV_HOST_NATIVE` (vaporware,
> §3). A **new HTTP runtime kind** plugs in here without touching `CV_AI` at all.

---

## 2 · (b) What already supports multiple providers vs what assumes `claude`

### 2.1 Already provider-agnostic (the shape)

- **`resolveProvider`** dispatches on `runtime.kind`, not on a fixed list. **Observed** (`ai-registry.js:202`).
- **The delegation seam** means new runtime kinds register *without editing `CV_AI`*. **Observed** (`ai-registry.js:233-236`).
- **Capabilities CAN declare any provider** via `provider: '<id>'`; `execute` resolves whatever they name. **Observed** (`ai-registry.js:299`).
- **The registry inspector / surfaces are projections** of `query({layer:'provider'})` — register a provider and it appears, no UI edit. **Observed** (`ai-seed.js` records all surface in the AI panel; charter §2).

### 2.2 Assumes `claude` (the monoculture — the real target)

Every *text* path is pinned to the literal `'claude'`. **Observed** (grep `app/ai/`):

| Site | file:line | What it pins |
|---|---|---|
| `CV_AI.complete()` one-off | `ai-registry.js:343` | `resolveProvider('claude').complete(...)` — the path `glyphic.generate` rides via `AI.complete` (`ai-glyphic.js:66`) |
| build/parse fallback | `ai-registry.js:315` | `(provider \|\| resolveProvider('claude'))` |
| all ~27 canvas TEXT caps | `ai-capabilities-canvas.js:84` | `provider:'claude'` (applied across the 30-row `TEXT` table at `:34-74`; ~27 are text moves) |
| `deck.titlechain` | `ai-capabilities-canvas.js:105` | `provider:'claude'` |
| `glyphic.generate` | `ai-glyphic.js:61` | `provider:'claude'` |

So: **the registry admits many providers; the resolution is hardcoded-claude at ~30 capability
rows + 2 registry fallbacks.** A live-instrument extract/compose pipeline that wants Company-local
models would, today, have to either (i) hand-set `provider:'<company-id>'` on every new capability
(re-hardcoding, the anti-pattern), or (ii) the system needs a role-resolution layer (§3).

### 2.3 The `claude` runtime itself is **External / ambient** (a hidden assumption)

**`window.claude.complete` is defined NOWHERE in this repo.** **Observed** (grep: the only hits are
*comments* saying "never raw window.claude" — `system/glyphic-foundry.html:24,193`; the only *binder*
is `ai-registry.js:204-211` which *consumes* it). It is an **ambient global injected by the editor /
sandbox host** (the Claude.ai artifact / Claude Code preview runtime) — **External / Inferred**. The
seed's `native-model` description confirms the mental model: a model runtime "activates when you
export this app" (`host-serializer.js:145`).

> **Consequence for the live instrument:** the `claude` provider only resolves *inside that host*.
> A standalone/exported browser tab has **no text model at all** today (openai is image-only, §2.4).
> This is a strong argument that the live-instrument's real text engine should be the **Company
> bridge over HTTP** (§4) — browser-native, no host injection, no vendor key, and it's the local
> fleet Tim wants primary anyway.

### 2.4 openai is **image-only**; google is **absent**

- `window.cvOpenAI` exposes `generateImage / editImage / responsesImage / variateImage / listImageModels / getModelCapabilities` — **no text-completion method**. **Observed** (`app/services/openai.js:621-644`). It talks directly to `api.openai.com` (or a proxy) via `fetch` with the user's key (`openai.js:210-218, 253, 382`).
- There is **no google provider, record, or service** anywhere. **Observed** (no match for google/gemini in `app/ai/` or `app/services/`).

So "register openai/google as **text** providers" needs a **real browser-side text runtime**, not
just a registry row. The OpenAI *image* path is the precedent for *how* (direct `fetch` + a service
object); the text equivalent must be built (§4 — the same direct-fetch runtime supplies it).

---

## 3 · (c) Precisely what to change — a **role-resolution layer**, no hardcoded call-sites

This is the make-or-break against §5. The fix is NOT "more provider records" — it's **one config map
+ one resolver function** that every pinned site routes through, so the catalogue stays the dispatch
and the *binding* of role→provider is single-sourced.

### 3.1 The design — `defaultProvider(role)` (My-idea, grounded in the existing API)

Today a capability says `provider:'claude'` (an *id*). The change: a capability declares a **role**,
and a single config resolves role→provider-id. Add to `CV_AI`:

```js
// one home for "which provider serves which role" — the ONLY place an id is pinned.
// LS-overridable + Vi-authorable (ds.propose), like everything else in the system.
const ROLE_PROVIDERS = {                 // role  → provider id (the single binding)
  'text':            'claude',           // the default text role (was the implicit ~30 pins)
  'compose-graph':   'claude',           // the live-instrument JUDGE role
  'extract-entities':'company-chat',     // the live-instrument EXTRACT role → Company-local
  'embed':           'company-embed',    // semantic icon-lookup → pplx embedder
  'image':           'openai-image',
};
function defaultProvider(role) {          // resolves a role to a provider id (config-driven)
  const id = ROLE_PROVIDERS[role] || ROLE_PROVIDERS['text'];
  return id;                              // resolveProvider(id) binds it to its live runtime
}
```

Then:
- **Capabilities declare a `role`, not a literal provider** — `normalize()` already carries arbitrary
  fields; add `role` to the schema (`ai-registry.js:159-191`). `execute()` changes one line:
  `const providerId = cap.provider || defaultProvider(cap.role || 'text');` then
  `const provider = providerId ? resolveProvider(providerId) : null;` (replaces `ai-registry.js:299`).
  *(`cap.provider` still honoured as an explicit override — e.g. image caps keep `provider:'openai-image'`.)*
- **The two fallbacks** (`:315`, `:343`) become `resolveProvider(defaultProvider('text'))` instead of
  `resolveProvider('claude')`. **Now there is no literal `'claude'` in a code path** — flipping the
  whole DS to Company-local is editing `ROLE_PROVIDERS['text']` in one place.
- **The ~27 canvas caps + `deck.titlechain` + `glyphic.generate`** drop `provider:'claude'` and (if
  needed) gain `role:'text'` (or just inherit the `'text'` default). One edit to the loop at
  `ai-capabilities-canvas.js:84`.

**No staleness, by construction:** a new capability references a *role* (a concept), never an
endpoint; the role→provider map is the one home; adding google text = register the `google` provider
record + bind a role to it (or set `ROLE_PROVIDERS['some-role']='google'`). Zero call-site edits. This
*is* `cognition-is-role-resolved` realised in `CV_AI`, mirroring the Company's `run_role`/`models_for_role`.

### 3.2 The provider records to add (the easy half)

Three new `provider` entries in `ai-seed.js` (data, not code):
- **`company-chat`** — `runtime:{kind:'company-http', endpoint:'chat', model:'chat-4b'}`, `modality:['text','stream']`, `caps:{stream:true, json:true}`. (Company FP8-4B brain; §4.)
- **`company-embed`** — `runtime:{kind:'company-http', endpoint:'embed', model:'embed-pplx'}`, `modality:['embedding']`, `caps:{dims:2560}`. (the pplx embedder for semantic icon-lookup; §4, anchor §4.)
- **`openai-text`** *(optional, later)* — `runtime:{kind:'openai-text'}`, needs a text method added to `cvOpenAI` (`/v1/chat/completions`) — out of scope for the local-first instrument but the role layer makes it a drop-in.
- **`google`** *(optional, later)* — a future record; same drop-in.

### 3.3 The no-staleness checklist (where hardcoding would sneak back in)

- ✅ **Provider binding** — role→id map is the single home (§3.1). *Trap:* a future capability author
  writing `provider:'company-chat'` directly re-pins; convention + a lint should prefer `role:`.
- ⚠️ **Model id inside a runtime** — `runtime.model:'chat-4b'` pins a *model*. Better: have the
  Company side resolve `chat-4b` by role too (it already does — `models_for_role`), so the DS passes a
  *role* to the bridge and the Company picks the model. Keeps the DS from caring which checkpoint is hot.
- ⚠️ **`caps`/`modality` are declared-not-enforced** — nothing checks them before calling. The
  live-instrument should add a `requireCap(provider, 'json')` guard (loud) so a non-JSON provider
  can't be silently asked for structured output. (Mirrors the Company's fail-loud json_schema check —
  §4.6.)
- ✅ **Icon tags / renderer** — out of my area (Areas 3/4), but the same principle: derive, don't list.

---

## 4 · (d) How a browser-side `CV_AI` provider reaches the server-side Company models

> Verified by a parallel Explore agent against `/home/tim/company` (Observed file:line below;
> agent-relayed — **Inferred** where I didn't re-read the line myself).

### 4.1 The hard constraint: vLLM model ports have **no CORS**

The Company serves OpenAI-compatible vLLM on `:8000` (AWQ chat), `:8001` (FP8-4B brain), `:8002` (9B),
`:8007` (pplx embed, 2560-dim INT8 unnormalized cosine). **Observed** (`ops/services.json` ~`:151-211,
:513-530`; `runtime/cognition.py:58` `RESIDENT_BASE_URL="http://127.0.0.1:8000/v1"`). **A browser
CANNOT `fetch` these directly** — no CORS headers on the vLLM ports. **Inferred** (agent: no CORS
middleware seen; `runtime/page_face.py:163` sets `Cross-Origin-Resource-Policy: same-origin`).

> So the anchor's option "`CV_AI` (browser) calling the Company over HTTP" is right **only via the
> bridge**, not via the raw model ports.

### 4.2 The real door: the **bridge HTTP API at `:8770`**

`runtime/bridge.py` is a plain HTTP server exposing browser-shaped routes. **Observed** (agent, `bridge.py`):
- `POST /api/chat` → `SUITE.chat(message, graph_id)` (`bridge.py:~3001`) — grounded RHM chat reply.
- `POST /api/cognition/run_role` (+ `/embed`, `/run_items`, `/run_reduce`, `/preview_turn`) (`bridge.py:~84-86`) — **the role-resolved cognition surface** the DS should target: pass a *role*, the Company picks the model.
- `POST /api/chat/stream` — NDJSON incremental parts → `{type:done, …}` (`bridge.py:~2153-2236`).
- `POST /api/voice/stream?persona=…` — NDJSON: `{type:transcript}` → `{type:part}` → `{type:chunk,wav_b64}` → `{type:reply}` → `{type:done}` (`bridge.py:~2338-2510`) — **the whole voice circuit in one stream** (relevant to LISTEN/NARRATE, Areas 5/6).
- `POST /api/stt` (raw audio → transcript), `POST /api/say` (TTS out) (`bridge.py:~2799, 3007`).
- `GET /api/stream` — SSE event feed (`bridge.py:~2120-2151`).

**Open question I could NOT close:** whether `:8770` sets permissive **CORS** (`Access-Control-Allow-Origin`)
for a cross-origin browser. The agent confirmed the *vLLM* ports don't; it did **not** confirm the
bridge does. **This gates the recommendation** — see §4.5. If the DS is *served from the same origin*
as the bridge (or via a same-origin proxy/path), CORS is moot.

### 4.3 The runtime kind to build — `company-http` (My-idea, modelled on `openai.js`)

A new browser-side runtime that does a direct `fetch` to the bridge — structurally identical to how
`openai.js` already `fetch`es `api.openai.com` (`openai.js:382` etc.). It belongs **either**:
- **in `CV_HOST`** as a new `runtime.kind` branch in `resolveProviderRuntime` (sibling to `host-fs`)
  — cleanest, since `CV_HOST` already owns "reaching the world"; OR
- **as its own service** `app/services/company.js` exposing `window.cvCompany.{complete, stream, embed}`,
  with a thin `CV_HOST` (or `CV_AI`) branch binding it — mirrors the `cvOpenAI` split exactly.

Recommended: **a `cvCompany` service + a `company-http` kind**, so the HTTP/shape knowledge lives in
one file (like `openai.js`), and `CV_AI`/`CV_HOST` only *bind* it. Shape:

```js
// app/services/company.js  (My-idea — mirrors openai.js's single-source-of-HTTP pattern)
window.cvCompany = {
  base: localStorage.getItem('cv:company:base') || 'http://127.0.0.1:8770',  // configurable, one home
  async complete(prompt, opts) {                       // role-resolved text
    const r = await fetch(this.base + '/api/cognition/run_role', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ role: opts?.role || 'text', utterance: prompt,
                             schema: opts?.schema /* → json_schema, §4.6 */ }) });
    if (!r.ok) throw new Error('[cvCompany] '+r.status+' '+await r.text());  // loud
    return (await r.json()).reply;                     // shape per run_role response
  },
  async embed(texts) { /* POST /api/cognition/embed → 2560-dim int8 vectors */ },
  stream(prompt, onPart) { /* POST /api/chat/stream, read NDJSON, call onPart per {type:part} */ },
};
```

Then `CV_HOST.resolveProviderRuntime` gains:
```js
if (kind === 'company-http') {
  const c = window.cvCompany;
  if (!c) throw new Error('[CV_HOST] provider "'+p.id+'" needs app/services/company.js + a reachable bridge at '+(c&&c.base));
  return { ...p, complete:(pr,o)=>c.complete(pr,{...o, role:p.runtime.role||p.runtime.model}),
                  embed:(t)=>c.embed(t), stream:(pr,cb)=>c.stream(pr,cb) };
}
```

**Result:** `resolveProvider('company-chat')` returns a live, callable provider; a capability with
`role:'extract-entities'` → `defaultProvider` → `'company-chat'` → this runtime → the bridge → the
FP8-4B brain. No call-site knows an endpoint. The whole chain is role-resolved end to end.

### 4.4 The other door (NOT recommended as primary): `native-model` / `CV_HOST_NATIVE`

The seed *names* `native-model` and `mcp-tools` and the resolver binds `CV_HOST_NATIVE.complete`
(`host-runtime.js:162-167`). **But nothing in this repo (or an export harness that exists today) sets
`window.CV_HOST_NATIVE`.** **Observed** (grep: zero `CV_HOST_NATIVE =` assignments; only the consumer
+ docstrings). It is a **forward-declared seam for a future export shell**, not a live path. Using it
would require building+shipping that native bridge first. The `company-http` direct-fetch path needs
*no host injection* and is therefore the realistic primary. (Keep `native-model` as the documented
path for a future packaged/desktop build.)

### 4.5 The recommendation, gated

- **If the DS app is (or can be) served same-origin with the bridge** (or behind a path proxy):
  build `cvCompany` + `company-http`, point it at `/api/cognition/run_role`. **This is the path.**
- **If it must be truly cross-origin and the bridge does NOT send CORS headers:** either (i) add a
  permissive-CORS option to the bridge's `:8770` routes (a Company-side one-liner — out of *this*
  repo, flag to that team), or (ii) fall back to the export `CV_HOST_NATIVE` bridge (heavier). **The
  headline pick can't be finalized until the bridge's CORS posture on `:8770` is confirmed** — that's
  the one open fact between here and a working demo.

### 4.6 Structured outputs — the EXTRACT layer's lifeblood works

The Company's vLLM honours **json_schema structured outputs** (not just `json_object`): `run_role(…,
schema=<model>)` forwards `response_format.json_schema`, and both 4B residents declare
`json_schema=true` with a **fail-loud** guard if a model can't do it. **Observed** (agent,
`runtime/cognition.py:303-380, 492-515`; `runtime/generation_policies.py:35,97-98`). So the
extract-vs-judgment pipeline (anchor §3) can demand structured entities/relations per concern from the
local fleet — *passing the schema through `cvCompany.complete(prompt,{schema})`*. (One caveat the agent
flagged: a `transport.py` passthrough for some params "not yet complete" — verify the json_schema
field actually forwards end-to-end before relying on it; **Inferred-incomplete**.)

---

## 5 · Cross-cutting: how this serves the live instrument (the pipeline, anchor §3)

- **LISTEN** → `POST /api/voice/stream` already returns `{type:transcript}` then brain parts + audio —
  a browser can subscribe to live transcripts *and* the narration in one NDJSON stream (Areas 5/6 own
  this; noting the door exists). **Observed** (`bridge.py:~2338-2510`).
- **EXTRACT** (concurrent small local models, structured outputs) → capabilities with
  `role:'extract-entities'` resolving to `company-chat` via `defaultProvider`, each calling
  `run_role` with a per-concern `schema`. The "fleet of small models" = multiple roles, each bound to
  the same `company-chat` provider (the Company multiplexes). **My-idea**, grounded in §3 + §4.6.
- **JUDGE/compose** → a `role:'compose-graph'` capability (stronger model, possibly the 9B at `:8002`
  or `claude` while local) — the binding is one config row, swappable. Realises *extraction-vs-judgment*.
- **RESOLVE → semantic icon-lookup** → `role:'embed'` → `company-embed` → pplx 2560-dim vectors;
  nearest tagged icon; below threshold → `glyphic.generate` (already a capability, `ai-glyphic.js:59`).
  **The pplx ~0.6b embedder the anchor referenced is actually a 4B (`pplx-embed-context-v1-4b`,
  2560-dim) on `:8007`** — anchor's "~0.6b" is wrong; the real one is bigger. **Observed** (agent,
  `ops/services.json:513-530`).
- **GENERATE-ON-MISS / SAVE** → `glyphic.generate` (role:`text`/`compose-graph`) + `glyphic.save`
  (pure-run, `provider:null`) already exist and write live to `CV_ICONS`. **Observed** (`ai-glyphic.js`).

So the registry already has the *moves*; what's missing is the **role layer** (§3) + the **`company-http`
runtime** (§4) so those moves run on the local fleet instead of the ambient sandbox `claude`.

---

## 6 · Honest gaps / what I did NOT verify

- **Bridge `:8770` CORS** for cross-origin browser calls — **unconfirmed**, gates §4.5. The single
  most important open fact for a working demo.
- **`run_role` HTTP response shape** — I assumed `{reply}`; the agent confirmed the *route* exists
  (`bridge.py:~84-86`) but I did not read the exact JSON keys. Verify before wiring `cvCompany`.
- **json_schema end-to-end forward** — vLLM honours it; a `transport.py` passthrough was flagged
  "not yet complete" by the agent — **verify** the schema field actually reaches vLLM (§4.6).
- **`window.claude` host contract** — I infer it's the sandbox/editor ambient (no in-repo definition);
  the exact `complete()` signature is whatever that host provides (`ai-registry.js:209-211` accepts
  string or `{messages}`).
- **`caps`/`modality` enforcement** — declared, not checked anywhere today; a guard is a §3.3 to-do.
- Anchor's `app/ai/services/…` paths are wrong: the services live at **`app/services/openai.js` +
  `app/services/ai-presets.js`**, and there is **no `services/openai.js` under `app/ai/`**. (Minor,
  but corrects the anchor's file map.)

---

## 3-line summary
1. **Contradiction held both ways:** `CV_AI`'s *plumbing* is already multi-provider (6 records, a `runtime.kind` dispatch, a `CV_HOST` delegation seam), but its *text resolution* is a `claude` monoculture pinned at ~30 capability rows + 2 registry fallbacks — and `window.claude` itself is an **ambient sandbox-host global defined nowhere in-repo**; openai is image-only, google absent.
2. **The fix is a role-resolution layer, not more records:** one config `ROLE_PROVIDERS` + `defaultProvider(role)` that `execute()`'s line 299 and the two `'claude'` fallbacks (315, 343) route through, so capabilities declare a *role* and flipping the whole DS to Company-local is one edit — `cognition-is-role-resolved` realised, no call-site staleness.
3. **Browser→Company is via the bridge `:8770` over HTTP** (vLLM model ports have no CORS), through a new `company-http` runtime modelled on `openai.js`'s direct-fetch, hitting `/api/cognition/run_role` (role-resolved, json_schema structured outputs confirmed) — NOT the `CV_HOST_NATIVE` path (export vaporware, never injected in-repo); the one open gate is whether `:8770` sends CORS for cross-origin.

Path: `/home/tim/company/design/claude-ds/analysis/glyphic-language/live-instrument/findings/AREA-1-cv-ai-providers.md`
