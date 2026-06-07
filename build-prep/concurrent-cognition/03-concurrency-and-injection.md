# 03 — Concurrent Execution & Injection (resident 4B swarm)

**Scope.** A concurrent-cognition layer over the **resident** small model (Qwen3.5-4B-AWQ on vLLM at `:8000`), best concurrency ~32 per the benchmark sheet. Two linked questions:

1. **Concurrent execution** — fire up to ~32 concurrent generation requests against the one resident endpoint, and budget the 32 slots so a turn never starves.
2. **Injection** — vLLM can't inject into a running generation, so the main reply is generated as **sequential PARTS** (each a fresh fast request), the swarm runs **between** parts, each role writes structured JSON to an address, and the next part's prompt **resolves** that address.

This is READ-ONLY research + design. No code was modified. All file:line evidence is from `~/company` as of 2026-06-07.

---

## A. What exists today — the call path, mapped (evidence)

### A.1 The transport is synchronous, one-at-a-time, stdlib `urllib`
`fabric/transport.py` has three transport builders, all blocking:

- `openai_transport` (`transport.py:28-51`) — `(model, messages, **opts) -> content_str`. The HTTP call is `with urllib.request.urlopen(req, timeout=timeout) as r:` (`transport.py:47`). **Blocking. One request per call. No pooling, no async.**
- `openai_tools_transport` (`transport.py:54-86`) — native tool-calling sibling, returns the whole message dict `{content, tool_calls}` (`transport.py:85`). Same blocking `urlopen` (`transport.py:81`). This is the one `chat()` uses.
- `openai_embeddings_transport` (`transport.py:173-195`) — embeddings sibling, same blocking shape.

`list_models` (`transport.py:15-25`) reads the real `/v1/models` at an endpoint — the registry-is-truth source (rule 8).

### A.2 The client wraps a transport with guards — still synchronous
`fabric/client.py`:
- `complete(transport, messages, model, schema=None, retries=4, ...)` (`client.py:54-89`) — retry/backoff loop, fail-loud. Calls `content = transport(model, messages, **opts)` (`client.py:66`).
- `complete_with_tools(...)` (`client.py:92-127`) — tool-aware: a tool_call with empty content is SUCCESS (`client.py:119-122`). This is `chat()`'s call.
- `complete_embeddings(...)` (`client.py:130-172`) — vector guards.
- `_backoff` (`client.py:21-25`) already has **jitter** "so concurrent cloud callers don't thunder-herd" — the codebase already anticipates concurrent callers at the retry layer.

**Key structural fact:** a transport is a plain callable `(model, messages, **opts) -> str|dict`. Nothing in `client`/`transport` holds shared mutable state across a call. So **N transports called from N threads are independent** — concurrency is a *caller* concern, not a transport rewrite.

### A.3 Everything that calls the model calls it ONE AT A TIME
- **`nodes/llm.py:run`** (`nodes/llm.py:30-41`) builds one transport, calls `client.complete` once. Synchronous.
- **The scheduler fires nodes sequentially.** `runtime/scheduler.py:run` (`scheduler.py:37`) is a single-threaded `while len(processed) < len(execs) and progress:` loop (`scheduler.py:59`) iterating `for nid, ex in by_id.items():` (`scheduler.py:61`), calling each ready node's `run()` in turn (`scheduler.py:~95-107`). Even a graph of 30 AI nodes runs them **one after another**, never concurrently.
- **`Suite.chat()`** (`suite.py:3333`) makes exactly **one** `complete_with_tools` call per turn (`suite.py:3424-3426`), then loops over the returned `tool_calls`.
- **The judge** (`is_finished_thought`, `suite.py:3253-3294`) makes one `client.complete` call (`suite.py:3283`).

**Verification (read-only):** `grep -rn "asyncio|httpx|aiohttp|ThreadPoolExecutor|concurrent.futures" fabric/ runtime/ nodes/` → **zero hits.** There is no concurrent generation mechanism anywhere in the model path today.

### A.4 The bridge IS already multi-threaded (but not for the model)
`runtime/bridge.py:972` runs `ThreadingHTTPServer` (`bridge.py:14`). Concurrent HTTP requests to `/api/*` already run in separate threads (`suite.py:188-209` documents per-session/per-graph locks added precisely because of this). So the **process can already run multiple Python threads**; what's missing is firing many *model* calls from them at once.

---

## B. The endpoint binding — the resident 4B is REGISTERED (prerequisite, resolved)

Per rule 8 the swarm must bind to a **registered** endpoint/model — never an invented one. It is registered:

- **`ops/services.json`** — service `chat-4b`, **port 8000**, group `brain`, model `cyankiwi/Qwen3.5-4B-AWQ-4bit` (`services.json:46-57`), titled *"a local WORKER (not the RHM brain; the RHM main is a cloud model)"*. `vram_mb: 8000` (`services.json:309`).
- **`ops/systemd/vllm-chat.service`** — *"vLLM Chat Server (Qwen3.5-4B-AWQ) on port 8000"*.
- **`runtime/suite.py:940-941`** — the **`judge` role** already declares `recommended_model: "cyankiwi/Qwen3.5-4B-AWQ-4bit"`, `recommended_base_url: "http://localhost:8000/v1"`, with the note *"Bind when the 4B is resident."* (`suite.py:944`).

**The binding this layer establishes (load-bearing — read carefully):** today the *default brain* is a **cloud reasoning model** — `DEFAULT_BRAIN = "deepseek-v4-pro:cloud"` at ollama `:11434` (`fabric/config.py:18,21`) — and `chat()`'s conversational reply runs on that cloud brain (`rhm_config()` resolves it). **The concurrent-cognition layer MOVES the main conversational reply onto the RESIDENT 4B at `:8000`, generated as sequential parts** (§E). This is a deliberate change of binding for *this mode* — it is what makes the rest of the design coherent:

- The task budgets the 32 slots "between the main conversation stream and the role swarm" on **the one resident endpoint** — i.e. the main stream is counted *inside* the resident 32 (see §C.3). That only holds if the main reply is on `:8000`, not on cloud `:11434`.
- "Each part a fresh **fast** request" + the prefix-caching evidence (§E.3, sheet §4) are **measurements of the 4B at `:8000`** — they do NOT transfer to a cloud reasoning model. The evidence is only valid because the main reply is resident.

So: main reply, judge, AND swarm all bind the resident 4B at `:8000`, exactly as the judge role's `recommended_*` already declares. The 4B's residency is owned by the **VRAM resource-manager** (`ops/cli/gpu.py`); any of these must **fail loud** if the 4B isn't loaded — never silently fall back to the slow cloud brain (that defeats the whole "fast resident, sequential-parts" architecture; rule 4). *(Whether the cloud brain remains an explicit operator-selectable mode — at the cost of losing the concurrent-cognition layer for that turn — is a Tim decision, flagged in §F.)*

> **Design rule (binding):** each swarm role resolves its model+endpoint the way the judge does — via the `ROLE_REGISTRY` + `resolve_role()` precedence (binding > env > declared default), defaulting to the resident 4B at `:8000`. See §D.

---

## C. CONCURRENT EXECUTION — firing ~32 at once

### C.1 Recommended: `ThreadPoolExecutor` (the path-of-least-resistance option)

**Why threads, not async.** The transport is already a clean blocking callable `(model, messages, **opts) -> str|dict`, and Python releases the GIL during the blocking socket I/O of `urllib.request.urlopen`. So firing the SAME existing transport from N threads gives **true concurrent in-flight HTTP requests with ZERO transport changes**. vLLM does **continuous batching server-side** — the benchmark's 2,241 tok/s aggregate at concurrency 32 (sheet §1) IS the server batching 32 independent HTTP requests. **No client-side batching is needed or wanted** — just issue N concurrent calls and let vLLM batch them.

```
from concurrent.futures import ThreadPoolExecutor, as_completed

# one shared transport instance is fine — it's a pure closure, no per-call state
t = transport.openai_tools_transport(base_url="http://localhost:8000/v1", timeout=...)

def role_run(role_prompt, schema):
    return client.complete(t, role_prompt, model=QWEN_4B, schema=schema)  # guarded, fail-loud

with ThreadPoolExecutor(max_workers=32) as pool:
    futs = {pool.submit(role_run, p, s): rid for rid, (p, s) in roles.items()}
    for f in as_completed(futs):
        rid = futs[f]; result = f.result()   # FabricError propagates → fail loud per role
```

This reuses `fabric.client.complete` / `complete_with_tools` **unchanged** — the guards (non-empty, JSON-repair, schema-validate, jittered backoff) apply per role, and a role that exhausts retries raises `FabricError` loud (rule 4) without taking down its siblings (catch per-future, surface the failing role).

**Tradeoffs:**
| | ThreadPool (recommended) | asyncio + httpx (rejected) | true server batch (n/a) |
|---|---|---|---|
| Transport change | **none** — reuses existing callable | rewrites all 3 transports to `async def`; breaks the 12+ string-callers of `openai_transport` | vLLM already batches server-side; a client `/v1/.../batch` shim adds nothing |
| Caller change | a small pool helper | every caller becomes `await` or needs an event-loop bridge | — |
| GIL | released during socket I/O → real concurrency | same, but +event-loop overhead | — |
| Fits repo law | **yes** (additive, sibling, no churn) | violates "additive, don't rewrite working callers" | — |
| Verdict | **adopt** | reject (heavy, no upside on this hot path) | not applicable |

The async option is documented only to show it was considered and rejected: it would force `openai_transport`'s 12+ existing string-callers (`nodes/llm.py`, judge, react, consult, embeddings…) to change, for no throughput gain over threads on I/O-bound HTTP.

### C.2 Where the pool lives
A new helper on the Suite (or a tiny `fabric/swarm.py` sibling) — e.g. `Suite._run_swarm(roles, budget) -> {role_id: result}`. It is **a sibling of the judge call path, not a rewrite of it.** It does NOT touch `chat()`'s single-call path except where §E wires the part-loop. Keep it off the MCP face (it's an internal cognition mechanism, not an operator verb), consistent with how `dispatch_decision` stays off the agent face.

### C.3 BUDGETING the 32 slots — never starve the turn

The failure mode the task names precisely: if the swarm grabs all 32 slots, the next **main part** queues behind 32 in-flight decodes (~1-2s each at the c=32 latency, sheet §1 p50 1.80s) — the operator's turn stalls. Two layers:

**Layer 1 — temporal separation (primary).** The architecture already separates them in time: the swarm fires **between** parts, the main part generates **alone**. So in the common case they don't overlap and there's nothing to contend. This is the structural answer and it carries most of the weight.

**Layer 2 — two distinct mechanisms, not one (a global ceiling + a swarm reservation).** These are easy to conflate; they are different:

- **The global ceiling — a shared `threading.Semaphore(32)`** sized at the **vLLM knee** (sheet §1: aggregate tok/s plateaus at 32; collapses past 128 → TTFT 3.7s). EVERY model call in the process — main part, judge, each swarm role, and any concurrent `/api/chat` turn or node run (the bridge is `ThreadingHTTPServer`, one process) — acquires one permit before calling and releases after. This guarantees the process never collectively exceeds the knee. A plain `Semaphore(32)` has **no partitions** — it cannot by itself "reserve" anything; it only caps the total.
- **The reservation — `max_workers = 32 − R` on the swarm pool.** THIS is what keeps R slots free for the main stream + judge. With the swarm's `ThreadPoolExecutor` capped at `32−R` (e.g. R=4 → swarm ≤ 28), the swarm can hold at most 28 permits at once, so ≥4 of the global 32 are always available for a main part / judge call to acquire immediately — even mid-swarm-wave. The main part and judge are NOT pooled (they're the single foreground call) but DO acquire the same global semaphore, finding a free permit because the swarm self-limited.

In short: **the swarm cap (`32−R`) is the reservation; the shared `Semaphore(32)` is the total ceiling.** Both are needed — the cap alone wouldn't stop concurrent bridge turns + node runs from collectively blowing the knee; the semaphore alone wouldn't stop the swarm from grabbing all 32.

**Tradeoff to surface for Tim:** a larger swarm (smaller R) = richer per-gap cognition but higher main-latency risk on overlap; a smaller swarm (larger R) = guaranteed-snappy turns but fewer concurrent roles. The number is a config slot (like the judge's knobs), measured by use, not guessed. Default proposal: **R = 4, swarm ≤ 28**, single shared semaphore at 32. The semaphore must be ONE instance shared across the whole process (the bridge is `ThreadingHTTPServer`, so concurrent `/api/chat` turns + the swarm all live in one process) — hold it on the Suite singleton.

**Evidence the 32 ceiling is right:** sheet §1 — c=32 → 2,241 tok/s, TTFT 153ms, p99 1.89s (the sweet spot); c=64 → 2,124 tok/s but p99 4.05s; c=128 → TTFT collapses to 3,736ms. Never exceed 32 concurrent for interactive feel.

---

## D. The swarm roles — bind like the judge (reuse `resolve_role`)

The judge (`suite.py:3172-3196` `resolve_role`, `suite.py:929-957` `ROLE_REGISTRY`) is the **exact precedent**: a role is a registry entry declaring `default_model / base_url / knobs / thinking / output / tools / context`, resolved live with precedence **binding > env > declared-default** (`resolve_role`, `suite.py:3184-3192`), so swapping a role's model is a config change, never a code change.

**Design:** each concurrent-cognition role is a `ROLE_REGISTRY` entry whose `recommended_*` (and, once the 4B is reliably resident, `default_*`) point at `cyankiwi/Qwen3.5-4B-AWQ-4bit` @ `http://localhost:8000/v1`. The swarm helper calls `resolve_role(rid)` per role to get `{model, base_url, knobs, output}`, builds the transport at that base_url, and fires. This means:
- adding a role TYPE is a registry row + its consuming prompt — it appears as a configurable slot in the config lab automatically (`suite.py:917-919`).
- a role's structured output is declared in `output` and enforced by `complete(..., schema=...)` → vLLM `response_format: json_object` (`transport.py:37,67`). The sheet (§5) confirms json_schema-constrained output is **production-reliable** on this model — so "each role writes structured JSON" is evidenced, not hoped.
- `thinking: False` + a small `max_tokens` per role keeps each role on the fast no-think path (the judge's measured lesson: a reasoner stalls the hot path, `suite.py:942-944`).

---

## E. INJECTION — sequential parts, swarm between, address-resolution into the next part

### E.1 Where the prompt/context is assembled today (the injection seam)
`Suite.chat()` (`suite.py:3333`) builds its messages at **`suite.py:3409`**:
```
msgs = [{"role": "system", "content": sys_p + "\n\n" + self._chat_context(graph_id, focus)}]
```
- `sys_p` (`suite.py:3386-3402`) is the persona / ground-truth / mode-directive head.
- **`_chat_context(graph_id, focus, intent)`** (`suite.py:1322-1462`) builds the **LIVE SYSTEM STATE block** (`suite.py:1385-1404`): graph/nodes/models/modes/verbs/inbox/panels/recent-activity — every value from the live registry, never fabricated.
- Crucially, `_chat_context` ENDS by APPENDING address-resolved context: **`suite.py:1461`**
  ```
  ctx += self._resolve_context_at(self.current_locus(), graph_id=graph_id, intent=intent)
  ```
  `_resolve_context_at` (`suite.py:1943-1982`) resolves info attached to the operator's **address** (locus) + ancestors into a bounded, ready-to-inject block (`CONTEXT RESOLVED AT YOUR LOCUS …`, `suite.py:1974-1976`), fail-loud-legible, returns `''` when nothing's attached.

**This is the exact, already-built injection mechanism.** Role-outputs become *more addressed context resolved into the next part's `_chat_context`* — the same append point at `:1461`, the same pattern as `_resolve_context_at`. No new injection machinery is invented; the design REUSES the address-resolution path the system already trusts.

### E.2 The two distinct "resolves" — keep them separate
1. **Model binding resolve** — `resolve_role()` (`suite.py:3172`), the judge pattern: binds each swarm role to the resident 4B endpoint. (Section D.)
2. **Address/content resolve** — `store.head(logical) -> cas` (`fs_store.py:277-279`) + `get_content(cas)`, and the higher-level `_resolve_context_at` (`suite.py:1943`): resolves a role-output ADDRESS into the next part's context. (This section.)

A role WRITES its structured JSON to an address via the store's content-addressed put + `set_ref` (`fs_store.py:184 put_content`, `:215 set_ref`); the next part READS it via `head`→`get_content` (or, for the bounded/decayed injection, through the `_resolve_context_at` machinery keyed at a swarm-output address namespace).

### E.3 The delta to `chat()` — one call becomes a part-loop
Today `chat()` is a **single** `complete_with_tools` (`suite.py:3424`). The design makes it a loop:

```
PART 0:  assemble msgs (sys_p + _chat_context)  →  generate part 0 (fresh fast request)
         ↓  (between parts — fire the swarm against :8000)
SWARM:   _run_swarm(roles)  →  each role writes structured JSON to an address  (store.put_content + set_ref)
         ↓
PART 1:  RE-assemble msgs — _chat_context now RESOLVES the swarm-output addresses
         (via _resolve_context_at at the swarm namespace) → generate part 1
         ↓ (swarm again, if more parts) …
ASSEMBLE the full reply from the parts; persist; return.
```

Each part is a fresh request → **prefix caching makes this cheap**: sheet §4 shows TTFT 40-110ms across 8 growing-context turns because each turn reuses the cached prior context instead of re-prefilling. So "main reply as sequential fresh requests" is not wasteful — the shared prefix (sys_p + stable LIVE STATE) is cached; only the newly-injected resolved-role block + the next part's generation are new work. This is the benchmark fact that converts the part-loop from "should work" to "evidenced".

### E.4 Concrete injection design options (tradeoffs)

| Option | How role-output reaches the next part | Pros | Cons |
|---|---|---|---|
| **(a) Address-resolution via `_resolve_context_at` (recommended)** | roles write to a `swarm://<turn>/<role>` address namespace; the next part's `_chat_context` resolves it at `:1461` through the existing decayed/bounded `_resolve_context_at` | reuses the trusted, BOUNDED injection path (can't flood the window — the §21 tension it already solves); fail-loud-legible; one-source | needs a small gather branch in `_r2_gather` that knows the swarm namespace |
| **(b) Direct `head`→`get_content` block** | the part-loop reads each role's address directly and concatenates a `SWARM FINDINGS` block into `msgs` before `_chat_context` | simplest; explicit; no decay machinery to touch | a second, parallel injection point (drifts from the address-resolution law); must hand-roll the bound/cap |
| **(c) Tool-result round-trip** | feed role outputs back as `role: tool` messages | matches native tool-calling shape | conflates cognition-roles with operator-facing tool_calls; heavier; not what the roles are |

**Recommendation: (a)** — it reuses the bounded address-resolution path (`_resolve_context_at`) the system already relies on, so the swarm output is injected the SAME governed, decayed, fail-loud-legible way the locus context is. (b) is the fast prototype to prove the loop end-to-end, then converge onto (a) so there's ONE injection law (rule 3, one-source). Avoid (c).

### E.5 Structured output is the contract between a role and the next part
A role's `output` is a JSON schema (declared in its `ROLE_REGISTRY` row); `complete(..., schema=RoleOut)` validates it (`client.py:75-87`) and the transport sets `response_format: json_object` (`transport.py:37,67`). Sheet §5: json_schema-constrained output is production-reliable on this model. So the address a role writes holds a VALIDATED structured object — the next part resolves a known shape, not free text. A role that can't produce valid JSON after retries raises `FabricError` (fail loud), surfaced per-role; it never silently injects garbage.

---

## F. Open questions to surface for Tim (don't build unasked)
- **R (reserved slots) and swarm cap** — proposed R=4 / swarm≤28 at a 32 semaphore; the real number is measured by use (config slot). Which way to bias: snappier turns (larger R) vs. richer per-gap cognition (smaller R)?
- **How many parts per reply, and what triggers a part boundary** — fixed N, or a judge-like model deciding "this part is a complete sub-thought, run the swarm now"? (The finished-thought judge is the obvious precedent for a part-boundary judge.)
- **Which roles populate the first swarm** — the role TYPES are a registry-driven, extensible set (like `judge`); the initial cast is a Tim/design call, informed by files `01`/`02` of this folder (not yet written).
- **Residency policy** — the swarm REQUIRES the 4B loaded at `:8000` (owned by the VRAM resource-manager). If it's not resident when a turn needs the swarm: fail loud + surface (the judge's stance), or have the turn request a load via `company up`/the manager? This is a resource-arbitration decision, not a cognition one.
- **Namespace + GC** — `swarm://<turn>/<role>` addresses accumulate; do they persist (introspective-data-building: the swarm's own run-records) or get reaped per turn?
- **Cloud-brain escape hatch** — moving the main reply to the resident 4B (§B) means a turn that wants the cloud reasoning brain loses the concurrent-cognition layer. Keep cloud as an explicit operator-selectable mode (no swarm that turn), or is the resident-4B-with-swarm the only conversational path going forward?
- **Tools array across parts** — today `chat()` is a `complete_with_tools` (native tool-calling) path (`suite.py:3424`). In the part-loop: do all parts carry the offered tools array, or only the final part (so intermediate parts are pure generation and only the last part can emit operator-facing `tool_calls`)? This is an open seam, not an oversight — flag it for the implementer.

---

## G. Summary of the build (what's net-new vs. reused)
- **Reused unchanged:** `fabric.client.complete` / `complete_with_tools` (the guards), `fabric.transport.*` (the blocking callables — threads make them concurrent), `resolve_role` + `ROLE_REGISTRY` (model binding), `store.head`/`put_content`/`set_ref` + `_resolve_context_at` (address resolution / injection), the `_chat_context` append seam at `suite.py:1461`.
- **Net-new (additive):** a `_run_swarm` helper using `ThreadPoolExecutor(max_workers=32−R)`; one shared `threading.Semaphore(32)` on the Suite with R reserved permits; concurrent-cognition role rows in `ROLE_REGISTRY`; a `swarm://` address namespace + a gather branch in `_r2_gather`; the part-loop in `chat()` replacing the single `complete_with_tools` call at `suite.py:3424`.
- **Laws honoured:** registry-is-truth (roles + the `:8000` binding are registered, not invented — rule 8); fail loud, no silent fallback to the cloud brain (rule 4); additive, no rewrite of the 12+ string-callers (rules 2/3); off the agent face (cognition is internal, not an operator verb).
