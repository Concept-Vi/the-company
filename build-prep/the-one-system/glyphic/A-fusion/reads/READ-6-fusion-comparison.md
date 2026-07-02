# READ-6 — Fusion Comparison + Stress-Test (the make-or-break read)

> Role: total-comparison / skeptic. Both AI systems read FIRST-HAND with file:line on both sides.
> The worst outcome (Tim) is designing on less than total comparison. This read exists to find where
> the fusion HARDCODES, STALES, or BREAKS — before "A" is designed on a wrong seam.
>
> Verdict up front: the fusion is sound in SHAPE (the two registries are near-isomorphic), but the
> naive seam ("point the `claude` provider at the bridge") **breaks on a real architectural collision**
> — CV_AI is a *dumb-endpoint* consumer, and every live Company brain route is a *smart* endpoint.
> The disciplined fusion requires a **new dumb-completion route** on the bridge. Details below.

---

## 0. What each side IS (one breath each, so the comparison is grounded)

**DESIGN side — `window.CV_AI`** (`app/ai/ai-registry.js` + `ai-seed.js` + `host-runtime.js`):
a browser-side registry of parametric, inheritable entries across five layers
(`provider · behaviour · skill · capability · context`), where the running interface is a *projection*
of the registry. **CV_AI owns ALL the intelligence**: a capability builds its own prompt
(`cap.build`), composes behaviour fragments (`composeBehaviours`), dispatches to a provider, and parses
candidates (`cap.parse`) — `execute()` at ai-registry.js:278-317. The provider is a **dumb**
model-endpoint: prompt in, text out (`window.claude.complete`, ai-registry.js:203-214).

**COMPANY side — `runtime/cognition.py`**: a Python engine where **the role owns the intelligence**.
`run_role(role, ctx)` (cognition.py:313) reads the role's `prompt_template`/`prompt_slot`,
`output_schema`/`schema_slot`, sampling `knobs`, and the O2 rep-penalty policy ladder — all
registry-is-truth (file-discovered `roles/*.py`, `skills/*.py`, `contexts/*.py`,
`generation_policies/*.py`). `run_role` is a **smart** endpoint: role-id + inputs in, validated JSON
out. It resolves the live brain itself (`active_brain()`, cognition.py:69) and the embedder itself
(op=embed, cognition.py:408-427).

That asymmetry — **dumb consumer vs smart engine** — is the spine of the entire comparison. Hold it.

---

## (a) EXACT overlap — where CV_AI and Company-cognition do the SAME job

The two systems are a **layer-for-layer near-isomorphism**, not a loose analogy. Same job, both sides:

| Job | CV_AI (browser) | Company cognition (server) | Overlap? |
|---|---|---|---|
| **provider / model resolution** | `resolveProvider(id)` binds a provider record → live runtime, loud if absent (ai-registry.js:198-238) | `active_brain()` sentinel→live loaded brain (cognition.py:69-108); `resolve_binding(role, providers)` role→provider by capability match (roles.py:398-431); `resolve_model(intent)` the declared unifier (model_routing.py:105) | **YES — direct** |
| **capability / operation dispatch** | `execute(capabilityId, …)` resolves + runs a capability (ai-registry.js:278) | `run_role(role, ctx)` resolves + fires a role (cognition.py:313) | **YES — same shape, opposite intelligence-ownership** |
| **skill (named parametric intent)** | `skill` layer → binds capability + instruction (ai-seed.js:86-112); `execute` delegates skill→capability (ai-registry.js:283-291) | `skill_registry()` / `skill://<id>` (cognition.py:141-144) | **YES** |
| **context (surface → prompt context)** | `context` layer + `resolveContext({surface,doc,ctx})` (ai-registry.js:246-257) | `context_registry()` / `context://<id>` (cognition.py:153-156); the `coordinate`→`prompt_slot` resolve (cognition.py:445-448) | **YES** |
| **behaviour (instruction fragment)** | `behaviour` layer + `composeBehaviours` (ai-registry.js:263-270; voice/angle/diversity in ai-seed.js:50-79) | closest analog = the resolved `prompt_slot` framing + role prompt_template; no separate first-class "fragment" registry | **PARTIAL** |
| **registry API** | `register/update/get/all/query/resolve/lineage/subscribe` (ai-registry.js:75-154) | file-discovered registries (`role_registry()`, `skill_registry()`, …) discovered fresh per call | **YES — same registry-is-truth idea** |

**What each UNIQUELY has:**

- **CV_AI unique:** the **browser boundary** itself — `caps.maxPromptChars` (ai-seed.js:25), surface-keyed
  context resolvers reading a live DOM `doc` (ai-seed.js:135-185), `image.generate/edit` via
  `window.cvOpenAI` (ai-seed.js:192-205), and the whole `execute()` **build→parse** machinery that turns a
  reply into typed candidates. CV_AI is where *product-shaped* generative moves live.
- **Company unique — the real muscle:** REAL local models (services.json: chat-4b-AWQ :8000, chat-4b-FP8
  :8001, chat-9b-FP8 :8002, plus 2B/0.8B/nemotron); a **real embedder** (`op=embed` →
  `complete_embeddings`, BGE-M3/pplx; cognition.py:408-427) — **CV_AI has NO embed analog at all**
  (its three providers are claude-text, openai-image, vision — ai-seed.js:21-43; this is *no overlap*,
  a clean Company-only capability); **live loadout resolution** (`active_brain` follows the running
  service, cognition.py:91-108); **concurrency** (ThreadPoolExecutor swarm — the whole point of the
  Concurrent Cognition build); **structured output enforcement** (schema-constrained decode + client-side
  validate/retry, cognition.py:519-534); the **O2 rep-penalty policy ladder** (cognition.py:618-646);
  **think-control routing** per stack (cognition.py:491-508).

**The overlap in one line:** both are a *registry of what-the-AI-can-do that resolves an entry into a
model call*. The difference is WHERE the prompt/parse intelligence lives — and that is what breaks the
naive seam.

---

## (b) The FUSED design — the exact seam (function · record · route)

**Goal:** CV_AI capabilities keep declaring their provider by a role-layer indirection; that role resolves
to ONE config; a `company-http` runtime hits the bridge — so the ~5 claude-pins and the dead
`window.claude` guard dissolve into a single repointed provider record.

### The seam, spelled out

> **⚠ WORD COLLISION (name it before it bites the builder):** the task calls the fused layer a "provider
> role-layer," but Company's `run_role` uses "role" to mean *a smart entry that owns a prompt_template*.
> These are DIFFERENT things. If the DS provider record carries a field named `role:` and a builder wires
> it to a Company `run_role` role, that is the EXACT double-prompt failure this read exists to prevent
> (R1). So this design uses **NO `role` field** on the provider record — the record names a *dumb route*,
> nothing more. "provider role-layer" here means only "the provider is the indirection layer the
> capabilities reference," never a `run_role` role.

**1. The provider RECORD (one edit, ai-seed.js:21-27).** Today:
```
runtime: { kind: 'claude' }          // → window.claude.complete
```
Becomes:
```
runtime: { kind: 'company-http', base: 'http://127.0.0.1:8770', route: '/api/complete' }
```
(No `role`, no model — the route binds the LIVE brain server-side; see below.) Everything downstream that
says `provider:'claude'` (ai-glyphic.js:61, ai-capabilities-canvas.js:84/105) is **unchanged** — they
reference the record by id; only the record's `runtime` changed. That is the one-home discipline paying
off: 3 capability pins + the seed = one edit.

**2. The FUNCTION seam — route it through CV_HOST, leave ai-registry.js UNTOUCHED (the tighter dissolve).**
CV_AI already delegates unknown runtime kinds to `CV_HOST.resolveProviderRuntime` (the fall-through at
ai-registry.js:233-236), and host-runtime.js:155-170 already has the `native-model`/`mcp-model` pattern to
copy. So `kind:'company-http'` is resolved by a NEW branch in **CV_HOST** (host-runtime.js), whose bound
runtime's `.complete(prompt, opts)` does the HTTP POST to the bridge and returns text. Consequence: the
only CV_AI edit is the seed record's `runtime` (step 1). The `if (kind === 'claude')` branch
(ai-registry.js:203-214) + its dead guard (line 205) become **removable dead code** — no record references
`kind:'claude'` anymore. This is CV_HOST's literal charter ("what can Vi reach in the world it runs in"),
and it keeps the AI registry itself pristine. The `execute()` fallback `resolveProvider('claude')`
(ai-registry.js:315) and `CV_AI.complete` (:343) resolve the SAME repointed record for free.

**3. The ROUTE (the required new bridge route — see the crux in (d)).** The `company-http` runtime MUST
target a **dumb completion route** `POST /api/complete {prompt, schema?} → {text}` (or `{json}`). This
route does NOT exist today and MUST be built. It is a thin wrapper over the DUMB engine primitive
`client.complete(transport, msgs, model, …)` (the same primitive `run_role` calls under the hood at
cognition.py:612/626) — NOT over `run_role` itself. Rationale is the crux below.

### How "one config → the live brain" lands (no `run_role` role involved)

The `/api/complete` handler binds the completion to `active_brain()` (cognition.py:69) server-side, so the
DS gets the SAME live loaded brain the RHM uses — a loadout swap (interaction-fp8 → quality-9b) moves the
DS's model with zero DS edits. That is the fusion's real prize: **the DS stops carrying a pinned model and
inherits the Company's live loadout** — WITHOUT routing through a `run_role` role. (Why not a "passthrough
role" with an empty template? Because `run_role` is never truly dumb: it injects `f"Utterance: {…}"`
framing at cognition.py:431 and always sends a system prompt (the role's `prompt_template`, cognition.py:450) —
so even an "empty" role re-frames the DS's already-built prompt. The dumb `client.complete` primitive is
the only clean target.)

---

## (c) STRESS-TEST — where this fusion HARDCODES, STALES, or BREAKS

Each risk is named with file:line + the disciplined alternative. The skeptic's job.

### R1 — THE CRUX: dumb consumer vs smart endpoint (would break silently)
CV_AI already built the prompt (`composeBehaviours` + `cap.build`, ai-registry.js:305/313) before it calls
`provider.complete(prompt)`. Every LIVE Company brain route is a **smart** endpoint:
- `/api/claude/turn` (bridge.py:2949) spawns a **stateful streaming Claude Code session** — wrong shape entirely.
- `/api/brain/ask` (bridge.py:2535) is RHM-composed + source-routed (fleet/recall/model) — adds its own cognition.
- `run_role` tool via `/api/tools/invoke` (bridge.py:3483; tool at mcp_face/server.py:690) requires a
  **registered role id**, wraps the input in the role's `prompt_template`, and returns `{output, address,
  turn_id}` — **not** a bare string.

If `company-http` targets any of these, CV_AI's already-built prompt gets **wrapped a second time** by a
role template (double-prompt), OR CV_AI must abandon its own `build`/`parse` machinery and become thin
role-references — which **dissolves CV_AI's one-IR law** (CLAUDE.md §1: "capability carries a `run` (or
`build`/`parse`) co-located with its prompt helpers").
**Disciplined alternative:** build a NEW **dumb** route `/api/complete` over `client.complete` (the raw
transport primitive). Both one-IR laws survive: CV_AI owns prompt+parse; the Company just lends its brain.
This is a **required-new-route**, not a detail — it is what makes A possible at all.

### R2 — CORS gate (would break 100%, immediately)
`grep -i cors runtime/bridge.py` → **zero matches.** The server sets no `Access-Control-Allow-Origin` and
has **no `do_OPTIONS`** handler. It binds **`127.0.0.1` only** (bridge.py:3725: `ThreadingHTTPServer(("127.0.0.1", port), H)`).
The canvas dev server is a **different origin** (`localhost:5173`, services.json canvas). A browser
`fetch('http://127.0.0.1:8770/api/complete')` from `:5173` is **blocked by CORS preflight** before the
request lands. Every DS AI call fails in the browser.
**Disciplined alternative:** add a CORS allowlist + `do_OPTIONS` on the bridge (localhost origins only —
NOT `*`, because `/api/tools/invoke` is a consequential door, bridge.py:3483), OR same-origin proxy the DS
through the bridge's own static serving (bridge.py:1485 already serves mockups same-origin). The
same-origin path is safer: it keeps the control plane un-CORSed.

### R3 — the `satisfied` floor trap (would STALE silently — the exact class Tim named)
`resolve_binding` (roles.py:398) returns `satisfied:False, provider:"default"` and **floors to
`default_model`** when no live provider matches (roles.py:424-427); `resolve_model` surfaces that
verbatim (model_routing.py:68-80, and the file's own warning at :22-27). If the DS binds `ds_completion`
through a role and the intended brain isn't live, it **silently floors to the resident 4B** and *looks*
resolved. A DS capability tuned for a big model then runs on a 4B with nobody the wiser.
**Disciplined alternative:** the `/api/complete` handler must return `satisfied` in its response, and the
`company-http` runtime must **throw on `satisfied:false`** (CV_AI loud-fail, CLAUDE.md §3) unless the
capability explicitly opts into the floor. Assert `satisfied`, never mere truthiness of `model`.

### R4 — sync vs async (would break the call shape)
CV_AI's provider `.complete` is `async` and awaited (ai-registry.js:209-315). The bridge is a **synchronous
`ThreadingHTTPServer`** (bridge.py:14/3725) — fine, HTTP is naturally async from the browser's side
(`fetch`). The real hazard is the **timeout mismatch**: `run_role`/`client.complete` server-side default is
`ROLE_TIMEOUT=600s` (cognition.py:66) — a heavy structured call can legitimately take minutes. A browser
`fetch` with no timeout will hang the UI; the DS composer expects fast candidate turnaround.
**Disciplined alternative:** the `/api/complete` route should support the streaming SSE shape the bridge
already uses (bridge.py:2133-2135) so the DS can render tokens as they arrive, and the `company-http`
runtime sets an explicit fetch timeout + AbortController. Don't inherit the 600s server default as a
browser hang.

### R5 — structured-output format mismatch (would break `cap.parse`)
CV_AI capabilities `parse(reply, …)` expecting **text** they can slice into candidates (ai-registry.js:316).
The Company enforces **schema-constrained JSON** (cognition.py:519-534) and the MCP face returns
`{output, address}` NESTING (cognition.py:322-324: "the `{output…}` nesting exists ONLY on the MCP face").
If `/api/complete` returns the MCP-nested shape, `cap.parse` chokes. Worse: the Company disables `<think>`
under schema decode (cognition.py:482-490 — "GUIDED-JSON ⊥ THINKING") — a subtle behaviour the DS never sees.
**Disciplined alternative:** `/api/complete` returns a **flat** `{text}` (or `{json}` when the DS passes a
`schema`), never the MCP `{output, address}` envelope. Match `cap.parse`'s expectation exactly; the DS
decides text-vs-json per capability.

### R6 — the browser↔server boundary + loud-fail translation (would create SILENT failures)
Several bridge routes return **HTTP 200 with `ok:false`/`degraded:true`** rather than an error status
(e.g. `/api/decision/explain` degrade at bridge.py:2594; `/api/tools/invoke` 403-refused at :3513;
`/api/say` 500 at :3022). CV_AI's law is **loud-fail = throw** (CLAUDE.md §3: "silently returning
[]/null/a fallback is not [ok]"). A `company-http` runtime that treats HTTP-200 as success and hands the
`ok:false` body to `cap.parse` produces a **silent failure** — exactly the class this whole system exists
to prevent.
**Disciplined alternative:** the `company-http` runtime inspects the body: `ok:false` / `degraded:true` /
`satisfied:false` → **throw** a `[CV_AI] company-http:` error naming the cause. HTTP status alone is not
the success signal across this boundary.

### R7 — the one-IR law for the AI layer (would violate BOTH registries' constitution)
CV_AI's charter: one catalogue, capability owns its prompt (CLAUDE.md §1-2). Company's charter:
registry-is-truth, role owns its prompt (AGENTS.md rule 8, roles/*.py). A fusion that lets the Company
role RE-wrap CV_AI's prompt puts prompt-authorship in TWO homes — drift by construction, the failure mode
both systems were built to kill.
**Disciplined alternative:** the boundary is the contract — CV_AI owns prompt+parse, Company owns
model+sampling+concurrency. `/api/complete` is a DUMB pipe. Neither registry reaches across it to author
the other's content. (This is R1's alternative, restated as a law.)

### R8 — provider-record shape mismatch (would break capability matching)
CV_AI caps are **booleans** `{stream, json, maxPromptChars}` (ai-registry.js:183-186). Company `provides`
is a **capability-tag list** matched against `role.requires` via `model_satisfies` (roles.py:415). "One
config" in (b) has to bridge two different shapes: a DS boolean-cap record vs a Company tag-set. If the
`/api/complete` route naively maps one to the other, a capability that "declares json" on the DS side
won't line up with a role that "requires ['json_schema']" on the Company side.
**Disciplined alternative:** keep them SEPARATE — the DS provider record stays boolean-cap (its own truth);
the bridge route resolves Company capability tags server-side (via `capabilities_for(model)`,
cognition.py:526). Don't try to unify the two cap vocabularies through the pipe; translate at the route.

### R9 — context-window HARDCODE/STALE (would break silently on long prompts)
CV_AI's `claude` provider advertises `caps.maxPromptChars: 200000` (ai-seed.js:25) — **chars**, sized for
Claude's window. The local brains are `max_model_len` **32768–65536 TOKENS** (services.json chat-4b:168,
chat-4b-fp8:199). 200k chars ≈ **~50k tokens** — which OVERFLOWS the 32k brain and only just fits the 64k
one. A DS capability that builds a prompt to its 200k-char assumption **overflows the local brain
silently** — vLLM truncates or refuses, and the DS never knows its assumption is stale.
**Disciplined alternative:** the `company-http` runtime must read the LIVE brain's `max_model_len` (the
`/api/complete` response, or a `/api/cognition_info` read, bridge.py:2090) and set `maxPromptChars`
DYNAMICALLY from the loaded model — never the hardcoded 200000. Follows the live loadout, same as the model.

---

## (d) What must be TRUE for A to work end-to-end

A checklist the build must satisfy — each is a concrete, verifiable gate, not a hope:

1. **A dumb completion route exists.** `POST /api/complete {prompt, schema?, role?} → {text|json, model, satisfied}`
   wrapping `client.complete` (NOT `run_role`). *(Does not exist today — REQUIRED NEW WORK. Verified: the
   only completion-shaped routes are the smart ones — `/api/claude/turn`, `/api/brain/ask`,
   `/api/cognition/run_role`, `/api/tools/invoke`→run_role.)*
2. **CORS or same-origin is solved.** Either a localhost CORS allowlist + `do_OPTIONS` on the bridge, or the
   DS is served same-origin through the bridge. *(Today: zero CORS, 127.0.0.1-bound, `:5173`≠`:8770` → hard block.)*
3. **The `company-http` runtime throws on `ok:false`/`degraded`/`satisfied:false`.** Loud-fail is honored
   ACROSS the HTTP boundary, not just within JS.
4. **Response shape is FLAT** (`{text}`/`{json}`), never the MCP `{output,address}` envelope — so `cap.parse` works.
5. **The one-IR boundary holds:** CV_AI owns prompt+parse+behaviours; Company owns model+sampling+concurrency+embed.
   Neither authors the other's content across the pipe. *(Verifies R1/R7.)*
6. **`maxPromptChars` is derived from the live brain's `max_model_len`,** not the hardcoded 200000.
7. **The model follows the live loadout** — `/api/complete` binds through `active_brain()` so a loadout swap
   moves the DS's brain with zero DS edits. *(This is the prize; verify by swapping loadout and re-firing a DS capability.)*
8. **Embedding, if the DS ever needs it, is a NEW CV_AI provider** (`kind:'company-embed'` → `op=embed`),
   not a retrofit of the text pipe. *(CV_AI has no embed layer today — clean Company-only addition.)*
9. **The claude pins dissolve to ONE record.** After the fusion, `grep "kind: 'claude'"` returns the single
   repointed seed record; `window.claude.complete` appears nowhere live (only in the deleted guard's history).

**The single highest-risk item:** #1 + the R1 crux. If the build points `company-http` at `run_role`
(the obvious-looking target — it's the "one cognition engine") instead of building the dumb `/api/complete`,
the fusion will double-prompt or gut CV_AI's IR, and it will *look* like it works on short prompts before
failing on structured ones. That is the make-or-break decision this read exists to flag.

---

### Evidence classification (per Tim's non-negotiable)
- **Observed (read first-hand, file:line above):** CV_AI dumb-provider shape; Company smart `run_role`;
  zero CORS; 127.0.0.1 bind; `satisfied` floor; MCP `{output,address}` nesting; maxPromptChars 200000 vs
  max_model_len 32768-65536; no embed analog in CV_AI; the 5 claude pins.
- **Inferred (not executed):** that a browser fetch from :5173→:8770 is CORS-blocked (standard browser
  behaviour given no ACAO header + cross-origin; NOT run against a live bridge here); that double-prompting
  degrades output (logical from the two prompt-owners, not measured).
- **Verified by execution:** none in this read — this is a source comparison, not a live test. The build
  must verify #7 (loadout-follow) and #1 (route shape) by USE.

---
**Summary (3 lines):**
1. CV_AI and Company-cognition are near-isomorphic registries (provider≈brain, capability≈role, skill≈skill, context≈context), but CV_AI is a DUMB-endpoint consumer (owns prompt+parse) while every live Company brain route is a SMART endpoint (role owns prompt) — that asymmetry is the whole game.
2. The fusion is one provider-record edit (ai-seed.js:22 `kind:'claude'`→`'company-http'`) that dissolves all 5 claude-pins, BUT it BREAKS unless a NEW dumb `/api/complete` route (over `client.complete`, not `run_role`) is built, CORS/same-origin is solved (bridge has ZERO CORS, 127.0.0.1-bound), and the runtime throws on the `satisfied` floor + `ok:false` 200s + reads `maxPromptChars` from the live `max_model_len` (the hardcoded 200000 CHARS ≈ ~50k tokens overflows the 32k local brain, only just fits the 64k one — silently).
3. What must be TRUE: dumb route exists · CORS solved · loud-fail across HTTP · flat `{text}` shape · one-IR boundary held · model follows `active_brain()` live loadout — the one make-or-break is NOT pointing `company-http` at `run_role`.

Path: `/home/tim/company/design/claude-ds/analysis/glyphic-language/A-fusion/reads/READ-6-fusion-comparison.md`
