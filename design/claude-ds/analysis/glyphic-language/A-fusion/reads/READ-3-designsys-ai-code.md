# READ-3 · The Design-System AI code, first-hand — the exact contract "A" must extend

**Stream:** the DESIGN side of the AI/Company fusion ("A").
**Method:** every file below read IN FULL + grepped, not summarised. Statements are tagged **Observed** (in the code, no execution) / **Inferred** (pattern-match, unverified) / **Verified** (ran it). Nothing here was executed in a browser, so runtime behaviour is Observed-from-source or Inferred, never Verified — flagged where it matters.

**Files read (file · lines):**
`app/ai/ai-registry.js` (351) · `app/ai/ai-seed.js` (213) · `app/ai/ai-glyphic.js` (85) · `app/ai/ai-glyphic-language.js` (102) · `app/ai/ai-capabilities-canvas.js` (120) · `app/ai/host-runtime.js` (441) · `app/ai/host-serializer.js` (198) · `app/services/ai-presets.js` (167) · `app/services/openai.js` (646) · load order `app/index.html:180–200`.

---

## 0. The one-paragraph shape (so the rest reads relationally)

`window.CV_AI` is one hierarchical registry of five layers — **provider · behaviour · skill · capability · context** — mirroring `CV_REGISTRY` verbatim (`register/resolve/lineage/query/subscribe`). A **capability** is the unit of "a thing Vi can do"; it *declares* which `provider` it runs on, which `behaviours` it composes, its `params`, and either a `run()` (owns build→complete→parse) or a `build()`/`parse()` pair. `execute()` is the single generative path: resolve capability (+inheritance) → resolve context from the active surface → compose behaviour preamble → **resolve the provider** → dispatch. A **provider** is a data record whose `runtime.kind` names *how to reach the live endpoint*; `resolveProvider(id)` turns that record into a bound object with a live `complete()` (text) / `generateImage()` (image). Runtime kinds `CV_AI` doesn't itself know are delegated to `CV_HOST.resolveProviderRuntime` — the host/environment registry. **This delegation seam is where the Company plugs in.**

---

## (a) The EXACT provider-resolution path + EVERY place a provider/model id is pinned

### The resolution path — `execute()` → `resolveProvider()` → (kind-dispatch)

**`ai-registry.js:278–317` — `execute()`** (Observed):

- `299`: `const provider = cap.provider ? resolveProvider(cap.provider) : null;`
  This IS the "recent `cap.provider ? resolveProvider : null` fix" the brief names. A capability with `provider:null` (e.g. `glyphic.save`, `glyphic.author`, `glyphic.read`) resolves **no** provider — a pure-function `run()` no longer requires a live LLM. **Verified by read:** the ternary is present and is the only provider-resolution in `execute()`.
- `304–307`: **run() path.** The resolved provider (or `null`) is passed into `cap.run({…, provider, preamble, brief})`. The capability owns its own build→complete→parse.
- `311–316`: **build/parse path** (pure-data capabilities, no `run()`). Line `315`:
  `const reply = await (provider || resolveProvider('claude')).complete(…);`
  → **hardcoded default #1**: if a build-capability declares no provider, `execute` falls back to the literal `'claude'`.

**`ai-registry.js:198–238` — `resolveProvider(id)`** (Observed) — the kind-dispatch:

- `203–214`: `if (kind === 'claude')` → checks `window.claude.complete` is a function (loud throw at `205` if absent), returns a bound `{…p, complete}` wrapping `window.claude.complete` (string or `{messages}`, `211`).
- `215–228`: `if (kind === 'openai-image')` → binds `window.cvOpenAI` (loud throw at `218`), returns generate/edit/responses/getModelCapabilities.
- `233–237`: **the delegation seam** — any *other* kind:
  ```
  if (… window.CV_HOST && typeof window.CV_HOST.resolveProviderRuntime === 'function') {
    const bound = window.CV_HOST.resolveProviderRuntime(p);
    if (bound) return bound;
  }
  ```
  else throws `unknown runtime kind "<kind>" (no CV_HOST runtime claimed it)` at `237`.

**On the "dead typeof-provider guard" the brief names:** *it is not present in the current code.* A case-insensitive grep for `typeof … provider` returns exactly ONE hit — `ai-registry.js:233`, `typeof window.CV_HOST.resolveProviderRuntime === 'function'` — which is a **live** guard on the delegation seam, not a dead provider-type guard. **Inference:** the dead guard was removed by the same fix that introduced the `cap.provider ? …` ternary; the brief's memory of it is stale. Flagged so "A" extends the real contract, not the remembered one. (Not mine to change — noting.)

### EVERY place a provider/model id is pinned (the fusion change-surface)

**The literal `'claude'` (grep-confirmed, `app/ai`):**

| file:line | pin | role |
|---|---|---|
| `ai-registry.js:203` | `kind === 'claude'` | the branch that binds `window.claude` |
| `ai-registry.js:315` | `resolveProvider('claude')` | **default #1** — build/parse fallback |
| `ai-registry.js:343` | `resolveProvider('claude')` | **default #2** — `CV_AI.complete()`, the one-off endpoint every surface calls |
| `ai-seed.js:22,24` | provider record `id:'claude'` + `runtime:{kind:'claude'}` | the seed |

**`window.claude` (the live text runtime):** referenced ONLY inside the `claude` branch — `ai-registry.js:204, 205, 211` (and comment `342`). It is the browser-sandbox Anthropic endpoint the whole text surface funnels through. **Observed:** it is an ambient global, not a registered runtime — `resolveProvider` reaches for it directly.

**Capability records that pin `provider:'claude'`** (Observed) — these are the ~31 text moves whose default brain is Claude:
- `ai-capabilities-canvas.js:84` — the whole `TEXT[]` loop (27 canvas capabilities: colour, icon, voice, pattern, component, build.*, deck.*, block.*, slide.compose, widget/wizard draft, type.*, inbox.classify, chat.respond).
- `ai-capabilities-canvas.js:105` — `deck.titlechain`.
- `ai-glyphic.js:61` — `glyphic.generate`.

**Net change-surface for a claude↔company swap:** 2 literal defaults (`:315`, `:343`) + 1 seed record + ~29 capability `provider:'claude'` strings = **~33 edit sites.** This is the number the design should collapse (see §e).

---

## (b) The provider RECORD shape + how a NEW runtime kind registers/resolves WITHOUT editing call-sites

**Record shape** — `normalize()` at `ai-registry.js:159–191` (Observed). Provider-relevant fields:
- `runtime` (`183`): `{ kind }` — *the dispatch key*. This is what `resolveProvider` switches on.
- `modality` (`184`): `['text']` | `['text','stream']` | `['image']` | `['fs']` | `['tool']`.
- `caps` (`185`): `{ stream, json, maxPromptChars, … }`.
- plus the common `id/name/layer/family/description/tags/provenance/icon`.

A provider is **pure data** — no functions. All behaviour is supplied at resolve-time by the kind-branch that binds it.

**How a new kind registers/resolves without touching call-sites** — *partially true today.* Two registration steps exist, but dispatch is NOT registry-driven:

1. **Register the data** — `CV_AI.register({layer:'provider', runtime:{kind:'<new>'}, …})`. Call-sites (`execute`, every `run()`) never change: they only ever call `resolveProvider(cap.provider)`.
2. **Teach something to bind the kind** — and *this* is the constraint: **there is no `kind → resolver` registry.** Dispatch is hardcoded in TWO homes:
   - `CV_AI.resolveProvider` — inline `if (kind==='claude')` (`203`), `if (kind==='openai-image')` (`215`), else delegate.
   - `CV_HOST.resolveProviderRuntime` (`host-runtime.js:155–170`) — inline `if (kind==='host-fs')` (`158`), `if (kind==='native-model' || kind==='mcp-model')` (`162`), else `return null` (`169`).

So a new kind lights up **without editing call-sites**, but **only if it is `native-model`/`mcp-model`/`host-fs`** (already-branched) — otherwise you must add a code branch to one of the two dispatchers. **This is the seam "A" must design against:** the record is data-extensible; the *resolver* is not yet.

---

## (c) The CV_HOST seam — plug the Company here, or a new provider runtime?

**The code answers itself.** `ai-registry.js:229–237` comment: *"Any other runtime kind is owned by the Host/Environment layer (CV_HOST): filesystem providers, native/MCP model endpoints. Delegate to it so the AI catalogue can name providers it doesn't itself know how to reach."* CV_HOST **is** the designated extension seam for provider kinds `CV_AI` proper shouldn't hardcode.

`CV_HOST.resolveProviderRuntime(p)` (`host-runtime.js:155–170`, Observed):
- `host-fs` (`158`) → binds `{read, list, write, capabilities, commit}` (the repo.* capabilities).
- `native-model` | `mcp-model` (`162–167`) → requires `window.CV_HOST_NATIVE.complete`; loud throw at `165` if absent; else returns `{…p, complete(prompt,opts){ return n.complete(p.runtime.model || p.id, prompt, opts); }}`.
- else `return null` (`169`) → hands back to `CV_AI` to throw its own unknown-kind error.

**Recommendation — plug the Company as a runtime KIND, not a parallel registry. Three sub-paths, ranked:**

- **(i) Zero-code (works TODAY, export-mode only).** Have the Company bridge expose `window.CV_HOST_NATIVE.complete(model, prompt, opts)` and register a data-only provider `{layer:'provider', id:'company', runtime:{kind:'native-model', model:'<role/model>'}}`. It resolves through `host-runtime.js:162–167` **untouched** — the intended path for "another model the host exposes." Constraint (Observed): `native-model` is `caps:{stream:false}` and `tags:['export-only']` (`host-serializer.js:143–148`); it throws in the browser sandbox (`165`), so this path is real only when the app is exported with the bridge.

- **(ii) First-class kind (one branch, the intended extension point).** Add one `if (kind === 'company-http')` branch to `CV_HOST.resolveProviderRuntime` that binds a `complete()` hitting the Company's HTTP surface directly (the same pattern `services/openai.js` uses for direct fetch — see §f). This makes the Company reachable **in the sandbox too**, not only on export, and lets it declare its own `caps` (streaming, role-resolution, json). This is the seam behaving exactly as designed: *add a way to reach the world = register a runtime, not edit every caller* (`host-runtime.js:19–21`).

- **(iii) A brand-new top-level runtime registry — NOT cleaner.** It would duplicate the seam `CV_HOST` already is (`host-runtime.js` is literally "the pluggable ways to reach the world"). Reject per *unions-not-bridges*.

**The "design-for-the-class" move (recommended alongside ii):** the real defect is that **kind-dispatch is hardcoded in two functions**. Dissolve the class: introduce `CV_HOST.registerKind(kind, resolverFn)` (and/or the same on `CV_AI`) so `claude`, `openai-image`, `host-fs`, `native-model`, `mcp-model`, and `company-http` are all *registered resolvers*, and the two `if`-ladders (`ai-registry.js:203–228`, `host-runtime.js:158–168`) collapse into one registry lookup. Then "add a provider = register data + register its kind-resolver once" becomes the whole law, with zero call-site edits ever. This is the extend-by-registration discipline the rest of the system already lives by, applied to the one place it isn't yet.

---

## (d) How a capability reaches a provider in execute() — pure-run vs build/parse

**Two dispatch paths in `execute()` (Observed), + a THIRD hidden variance inside run():**

**Path 1 — `run()` capability** (`ai-registry.js:304–307`). The resolved `provider` (or `null`) is handed to `cap.run(...)`; the capability decides how to use it. **But run()-capabilities are not uniform in how they reach the model:**
- **Canvas caps** (`ai-capabilities-canvas.js:28`): `runText = (a) => a.provider.complete(…)` — uses the **passed, resolved** provider. Correct.
- **`glyphic.generate`** (`ai-glyphic.js:64–68`): **ignores** `a.provider` and re-routes through `AI.complete` (`66`: `AI.complete ? AI.complete.bind(AI) : (a.provider && a.provider.complete)`). So it dispatches via the `CV_AI.complete()` default (`ai-registry.js:343` → `resolveProvider('claude')`), NOT via its declared `provider:'claude'` (`:61`). **Consequence for the fusion:** repointing the default text brain must cover *both* routes — a capability's declared provider AND the `AI.complete` fallback — or glyphic.generate silently keeps using the old default. Easy to miss.

**Path 2 — build/parse capability** (`ai-registry.js:311–316`). No `run()`. `cap.build(...)` produces a prompt; then `315`: `(provider || resolveProvider('claude')).complete(...)`; then `cap.parse(...)`. **This path has its own `'claude'` fallback** (`:315`) distinct from `AI.complete`'s (`:343`).

**So there are THREE places the "default text brain" is decided, all pinned to `'claude'`:**
`ai-registry.js:315` (build/parse fallback) · `ai-registry.js:343` (`CV_AI.complete`) · and each capability's `provider:'claude'` field. A fusion that makes the Company the default must repoint all three surfaces — which argues directly for §e.

---

## (e) The design lever — role-resolution over 33 pins (recommended framing)

Per memory *cognition-is-role-resolved* and *design-for-the-class*: a brain is a **role** that resolves to a model from its needs, never a pinned literal. Today the "default text brain" is the literal `'claude'` in ~33 sites. **Proposed primitive:** a role indirection — e.g. a registered provider alias `text.default` (or `CV_AI` resolving `provider:'text'` through a role table) — so:
- capabilities declare `provider:'text'` (the role), not `'claude'` (the model);
- `execute`'s two fallbacks (`:315`, `:343`) resolve the same role;
- swapping claude↔company (or A/B, or per-surface) is **one edit to the role binding**, not 33.

This is the exact shape the token/type/AI registries already use (define once, reference everywhere) — the AI provider layer is the one spot still holding copies. "A" is the occasion to close it.

---

## Real gaps surfaced (map, not fix)

1. **No `kind → resolver` registry** — dispatch hardcoded in `ai-registry.js:203–228` AND `host-runtime.js:158–168`; every new kind needs a code branch. (§b, §c)
2. **`'claude'` pinned ~33×** — 3 dispatch defaults + ~29 capability records + 1 seed; no role indirection. (§a, §e)
3. **`glyphic.generate` ignores its resolved provider** — routes through `AI.complete` (`ai-glyphic.js:66`) instead of `a.provider`; inconsistent with canvas caps. (§d)
4. **No caller of `glyphic.generate`** in `app/` — grep found the capability registered (`ai-glyphic.js:60`) but no `execute('glyphic.generate')` invocation anywhere; the generation surface is registered-but-unwired. (Observed)
5. **No "live/demo" branch in glyphic** — the brief names one; `glyphic.generate.run` (`ai-glyphic.js:64–68`) has no demo/offline/no-key fallback (unlike `services/openai.js`, which is key-gated). The brief's memory is stale here too.

---

## (f) The direct-fetch provider pattern (the template for a `company-http` kind)

`services/openai.js` (Observed) is the reference for a provider that reaches a live HTTP endpoint from the browser: `endpoint(path)` honours an optional `proxyUrl` (`210–213`, the CORS escape hatch), `authHeaders()` (`214–218`), key-gating via `isConfigured()` (`219`), typed loud errors via `fail(msg, code)` (`220`), SSE streaming (`streamSSE`, `462–495`), and a static-registry-with-inference capability model (`getModelCapabilities`, `49–177`). A `company-http` runtime kind would follow this shape: a bound `complete()` that fetches the Company surface, proxy-aware, streaming-capable, loud on failure — and could declare real `caps` (stream/json/role-resolution) instead of `native-model`'s conservative `{stream:false}`. `services/ai-presets.js` is orthogonal (image-preset store); noted read, not load-bearing for text fusion.

---

### Load order (Observed, `index.html:180–200`) — the contract A must not break
`services/openai.js` → `ai-presets.js` → **`ai-registry.js` → `ai-seed.js` → `ai-capabilities-canvas.js` → `ai-glyphic.js` → `ai-glyphic-language.js`** → `host-runtime.js` → `host-serializer.js`. CV_AI exists before anything resolves through it; **CV_HOST loads AFTER CV_AI** (so its `host-fs`/`native-model`/`mcp-tools` providers register into the one catalogue, and the `resolveProviderRuntime` delegation target exists by the time any non-claude/non-image kind is resolved). Any `company-http` wiring lands in this window, after CV_AI, alongside CV_HOST.
