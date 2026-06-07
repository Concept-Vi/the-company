---
type: design
module: build-prep
series: concurrent-cognition
seq: "04"
aliases: ["Staged Multi-Part Response", "Staged Response Queue", "Thought-Shapes"]
tags: [company, design, concurrent-cognition, rhm, staged-response, thought-shapes]
status: proposal
relates-to: ["[[Company — read first]]", "[[Company Map]]", "[[runtime — constitution]]"]
---

# 04 — The Staged Multi-Part Response (thought-shapes + the intra-turn queue)

> First doc in `build-prep/concurrent-cognition/` (the folder was empty when written — no 01–03 to extend; this file establishes the vocabulary the later docs in the series should build on, not contradict). Provisional / open. Written against codebase evidence in `~/company` as of 2026-06-07. Nothing here is built yet.

## What this is (the one relationship)

One user-facing reply that **one brain model** produces in **sequential parts** that read as one unbroken stream. **Part 1 fires instantly** (it depends on nothing but the operator's message). **Later parts are enriched** by **concurrent auxiliary-role outputs** that were resolving in the background while Part 1 played. To the operator it is one voice, one thought, arriving the way a person speaks — an opening beat lands immediately, the substance follows as it's gathered.

The spine, stated as a relationship (not a component list):

```
message → [shape selected by mode] → Part 1 (instant, no deps)
                                       │
        roles resolve concurrently ───┤ (their OUTPUTS are ADDRESSES)
                                       ▼
                              Part 2 … N (each fires when its
                              role-output addresses resolve)
                                       ▼
                              [offer] (the existing suggest/proposal card)
```

**The deepest connection (Universal Composition):** a **part is a node**, a **role-output is an address**, and **a part fires when its input addresses resolve** — this is the repo's *existing reactive scheduler primitive* (`MAP.md` "How a run flows": *a node fires when its input addresses resolve in store*) applied **intra-turn**, to one reply, instead of across a canvas graph. We are not inventing a second scheduler concept. We are re-using the system's defining relationship at a smaller scale (see [§ Queue/scheduler](#the-queuescheduler--a-part-is-a-node-a-role-output-is-an-address)).

---

## Part A — How a reply is produced TODAY (evidence)

### `Suite.chat()` — one call → one full reply
`runtime/suite.py:3333` `def chat(self, message, graph_id, focus=None) -> dict`.

The current shape is **single-shot**:

1. **`mode = self.get_mode()`** (`:3339`); if `off` (`:3340`) it short-circuits with a fixed line and returns — *the mode already gates whether the RHM acts at all*.
2. **Capability-gate** (`:3357`): `_model_supports_tools(...)` — a non-tool model is refused **fail-loud**, no model call, no fallback.
3. **System-prompt assembly** (`:3386–3402`): a head that states WHO it is + "answer ONLY from LIVE SYSTEM STATE" + optional `VOICE / PERSONA` block (`:3391`, persona id expanded to full character prose via `voice.personas.get_persona(...).get("brain")`, `:3376–3381`) + the model-of-Tim digest (`:3392`) + **`CURRENT MODE — {mode}: {self._mode_directive(mode)}`** (`:3396`) + the "act only by CALLING a governed tool" clause (`:3397–3401`).
4. **Tools array** (`:3406–3407`): `actx = self._affordance_context(...)`; `tools = self._rhm_tools(mode, actx)` — the verbs offered THIS turn.
5. **Message list** (`:3409–3412`): `system` = `sys_p + "\n\n" + self._chat_context(graph_id, focus)`, then up to 20 turns of history (`store.chat_history(20)`), then the user message.
6. **ONE model call** (`:3424–3426`): `client.complete_with_tools(transport, msgs, model, tools, tool_choice="auto", **brain_knobs)`. Returns `{content, tool_calls}`. **There is no streaming here** — the whole reply is produced before return.
7. **Tool-call loop** (`:3445–3486`): each `tool_call` → `_json_obj_to_action` → `_dispatch_rhm_action` (the ONE whitelist, E6). A `suggest` call becomes a **proposal** (no dispatch, `:3450–3468`). A not-offered verb is refused (`:3469–3474`).
8. **Confirmation fold** (`:3493–3502`): a concise confirmation of each dispatched verb is folded INTO `reply` (critical because a tool-only turn has empty content).
9. **Return shape** (`:3537–3540`):
   ```python
   {"reply": str, "action": None|dict|list, "proposal": dict|None,
    "mode": str, "model": str, "thread_id": str|None, "history": list}
   ```

> **The staged design is ADDITIVE to this (rule 2).** `chat()` and its return shape stay byte-for-byte. The staged path is a NEW Suite method + a NEW streaming endpoint. Every existing caller (the MCP face, `/api/chat`, the voice circuit at `bridge.py:431` which calls `SUITE.chat(...)` for the full reply) is unchanged.

### The MODE system (the gate)
- **Registry:** `MODES = ("listening","text-only","background","focus","walkthrough","watch-and-react","decide-for-me","off")` (`runtime/suite.py:907`). The mode **IS a node** (`rhm_mode`, the `rhm` node in the `system` graph): `set_mode` (`:1066`) writes the node config via `set_config`; `get_mode` (`:1063`) reads it.
- **Directives** (`MODE_DIRECTIVES`, `:1032–1046`) — behaviour comes from the directive string, single-source, exposed in `capabilities().mode_directives` (`:469`). Note the **brevity gradient already encoded**:
  - `focus` → "extremely brief (one or two lines); do not elaborate unless asked"
  - `background` → "minimal — surface only what genuinely needs the operator; otherwise a one-line acknowledgement"
  - `walkthrough` → "Actively guide: narrate what you are doing and direct the operator's attention step by step" (the staging-WANTS-IT mode)
  - `decide-for-me` → act on AUTO-class verbs, surface the rest
  - `off` → short-circuits before any directive (`:3340`)
- **`_mode_directive(mode)`** (`:1074`) is the single read.

**Why mode is the gate for staging:** the mode already says *how much to say and how to behave*. So **mode decides whether to stage at all** (focus/background → never stage, the answer is one line; walkthrough/listening → stage by default), **and** mode biases the short-response judge (below), **and** mode selects the **thought-shape** and **role-set** (below). The mode is the single dial that the whole staging machine reads — consistent with "the mode IS a node, behavior comes from the directive" (`AGENTS.md` "where things go").

### The auxiliary-role registry (the concurrent enrichers)
`ROLE_REGISTRY` (`runtime/suite.py:929`). A **ROLE** is "a named model-FUNCTION of the collective cognition: a specific job done by a model that is NOT the conversational brain." The brain stays its own slot (`rhm_config.model`); roles are auxiliary. First/only role today is **`judge`** (the voice circuit's finished-thought endpoint, `:930–957`). Each role DECLARES its full contract: `label`, `description`, `trigger`, `default_model` (None → falls to the brain), `recommended_model`, `thinking`, `output`, `tools`, `context`, `knobs`, `env_*`. Bindings live in ONE `rhm_config.roles` dict (`:1166`), schema-additive, validated fail-loud against the registry (`:1217–1242`).

> **This is exactly the substrate the staged response needs.** The concurrent enrichers (retrieval, a fact-checker, a tone/affect pass, etc.) are NEW ROLES added to `ROLE_REGISTRY`. The short-response judge is ALSO a new role (mirrors `judge`). Adding a role TYPE = a row in the registry + the code that consumes it (`AGENTS.md` rule for "a new model/provider" style single-source); no config-whitelist edit.

### The existing streaming + "multi-part feel" precedent
There is **no token-streamed chat** today, but there IS a **sentence-chunked NDJSON stream** in the voice circuit — the closest existing pattern to "parts that feel like one stream":

`bridge.py:357` `_voice_stream` (`POST /api/voice/stream`):
- `Content-Type: application/x-ndjson`, `Connection: close` (`:377–379`); **emits newline-delimited JSON events** as work completes: `{type:transcript}` (`:428`) → `{type:reply}` (`:434`) → per-sentence `{type:chunk, idx, text, wav_b64, ms}` (`:452–454`) → `{type:done}` (`:463`). Fail-loud is a `{type:error}` event then close (`:464–468`).
- The whole reply is produced by ONE `SUITE.chat(transcript, gid)` call (`:431`), THEN split into sentences (`:444`) and each synthesised + streamed AS IT'S READY (`:447–455`) — "so the first words play at ~(silence+STT+brain+TTS-of-one-short-sentence), and the rest flows behind."
- **Client-disconnect cancellation** (`client_gone()`, `:391–404`, select+`MSG_PEEK`): a cancelled turn stops before the next expensive synth.

And the canonical SSE pattern: `GET /api/stream` (`bridge.py:325–354`) — `text/event-stream`, durable cursor (`?since=`/`Last-Event-ID`), 15s heartbeat, replays the event log (`events_since`, `suite.py:875`).

**The staged-response transport mirrors `_voice_stream` exactly:** a new NDJSON endpoint that emits `{type:part, ...}` events as each part is produced. Same shape, same fail-loud-as-event, same disconnect-cancel.

### The "offer" stage already exists — OFFER-WITH-OPTIONS
The `acknowledge→retrieve→synthesise→**offer**` shape's final beat is NOT a new primitive. `chat()` already has it: a `suggest` tool_call (`:3450–3468`) becomes a **proposal** — `{verb, address, args, options[], direction}` — that rides back in the return as `proposal` (`:3536`); the FE renders a one-click card; approve → `/api/act`; nothing runs until then. The staged "offer" part emits this same proposal as its content.

### The declarative-template prior art — `panels/`
The repo's existing **registry-driven template** pattern is brain-authored **declarative panel definitions** (`propose_panel`→`apply_panel`, `suite.py:5764`; JSON field-defs in `panels/`; "NOT arbitrary code — a definition a generic renderer displays", `:5766`). The thought-shape registry should follow the same philosophy: a **declarative shape definition a generic runner executes**, single-source, schema-additive — mirroring the existing in-code dict registries (`MODE_DIRECTIVES`, `RHM_VERB_SPECS`, `ROLE_REGISTRY`).

---

## Part B — DESIGN

### (a) Thought-shape templates — the registry + schema

A **thought-shape** is the *shape of a multi-part answer*: an ordered list of **parts**, each part declaring what it depends on (which role-outputs must resolve before it can be generated) and what it's for. It is **declarative data**, executed by one generic runner — exactly like `panels/` are declarative defs a generic renderer displays.

**Single-source registry on the Suite** (mirrors `MODE_DIRECTIVES` / `RHM_VERB_SPECS` / `ROLE_REGISTRY`):

```python
# runtime/suite.py — proposed, schema-additive, registry-is-truth
THOUGHT_SHAPES = {
    "acknowledge_retrieve_synthesise_offer": {
        "label": "Acknowledge → retrieve → synthesise → offer",
        "description": "The default conversational shape: land an instant opening beat, "
                       "pull what's needed, deliver the substance, then offer a next step.",
        "modes": ("listening", "walkthrough"),       # which presence modes SELECT this shape
        "parts": [
            {"id": "acknowledge",
             "deps": [],                              # NOTHING → fires INSTANTLY (Part 1)
             "intent": "A brief, warm opening beat that shows you heard the operator. "
                       "Do not answer yet; set up the answer. One or two sentences.",
             "may_act": False},                       # this part cannot call governed verbs
            {"id": "synthesise",
             "deps": ["role:retriever"],              # waits for the retriever role-output address
             "intent": "Answer the operator's message grounded in the retrieved material "
                       "and the live system state. This is the substance.",
             "may_act": True},                        # this part MAY call governed verbs (see Part C)
            {"id": "offer",
             "deps": [],                              # depends only on prior parts (coherence carry)
             "intent": "Offer ONE concrete next step as a suggest-proposal if (and only if) "
                       "one is genuinely useful; otherwise emit nothing.",
             "may_act": False, "offer": True},        # routes through the existing suggest/proposal path
        ],
    },
    "direct": {                                       # the degenerate 1-part shape = today's chat()
        "label": "Direct (single part)",
        "description": "One part, no roles, no staging — what plain chat() does.",
        "modes": ("text-only", "background", "focus", "watch-and-react", "decide-for-me"),
        "parts": [{"id": "answer", "deps": [], "intent": "Answer directly.", "may_act": True}],
    },
}
```

**Part schema (one row):**
| field | type | meaning |
|---|---|---|
| `id` | str | the part's name (also its address segment) |
| `deps` | list[str] | the **addresses** this part waits on. `"role:<role_id>"` = an auxiliary-role output; `"part:<id>"` = a prior part (usually implicit — all prior parts are always carried for coherence). Empty `[]` → fires immediately. |
| `intent` | str | the per-part instruction folded into that part's prompt (the "what this beat is for") |
| `may_act` | bool | whether this part is allowed to call governed verbs (default False; see Part C) |
| `offer` | bool (opt) | this part routes through the existing OFFER-WITH-OPTIONS `suggest`/proposal mechanism rather than emitting prose |

**Shape selection** is mode-driven: `shape_for(mode)` returns the registered shape whose `modes` contains the current mode (single read, mirrors `_mode_directive`). `focus`/`background` map to `direct` → **they never stage** (the answer is one line, by directive). Selection is registry-driven and configurable: a `rhm_config` slot could later override the per-mode shape binding (open question).

**Why declarative, not hardcoded:** the same reasons `panels/` are declarative — the system can later **author its own shapes** (a `propose_shape`→`apply_shape` path mirroring panels: governed, additive, git-reversible), and the surface renders the shape vocabulary from the registry (`capabilities().thought_shapes`) instead of hand-copying. Registry-is-truth (AGENTS.md rule 8).

### (b) The queue/scheduler — *a part is a node, a role-output is an address*

This is the **same reactive relationship the canvas scheduler already embodies**, applied intra-turn. A part fires when its `deps` (addresses) resolve. The question of whether to **reuse `runtime/`'s scheduler verbatim or build a lightweight in-turn analogue** is a real open question (below) — the design INTENT is concurrent, the relationship is identical, the implementation is most cleanly a small in-turn runner that speaks the same "fires-when-deps-resolve" language.

**The flow of one staged turn** (proposed `Suite.chat_staged(message, graph_id, focus) -> generator of part-events`):

```
t0  message arrives
    ├─ select shape = shape_for(mode)                        (mode is the gate)
    ├─ short-response judge?  → if SHORT: yield ONE part = plain chat(), DONE   (see (c))
    │
    ├─ KICK OFF every auxiliary role the shape's deps name, CONCURRENTLY
    │     each role:<id> runs in its own thread (ThreadPoolExecutor), calling
    │     fabric.client.complete(...) with the role's bound model/knobs/context.
    │     its result is written to an intra-turn address  role://<turn>/<role_id>
    │     (mirrors how a node's result persists to store by address).
    │
    ├─ PART 1 (deps=[]) fires IMMEDIATELY — one brain call, streamed back as
    │     {type:part, id:"acknowledge", idx:0, text:...}      (instant)
    │
    ├─ for each later part in shape order:
    │     WAIT until all its deps' addresses resolve (a role future completes,
    │       or fail-loud as {type:part_error, role:<id>, error:...})
    │     build that part's prompt = system-head + prior parts + role-outputs
    │       resolved for its deps + the part's `intent` + "continue naturally"
    │     ONE brain call → {type:part, id:..., idx:n, text:...}
    │     (if part.may_act: its tool_calls dispatch via _dispatch_rhm_action;
    │      if part.offer:   its suggest call → a {type:proposal} event)
    │
    └─ {type:done, reply: <all parts joined>, action, proposal, mode, model}
```

**Concurrency is NET-NEW and must be flagged.** Today every model call is sequential (`chat()` makes exactly one; `_voice_stream` chunks AFTER the reply). Staging introduces **concurrent model calls** — the role threads run WHILE Part 1's brain call runs. Design choices:
- A bounded `ThreadPoolExecutor` (one future per role in the shape's dep-set). Roles are independent — no shared mutable state beyond reads of live ground truth.
- **Fail-loud per role** (rule 4), mirroring `_voice_stream`'s `{type:error}`: a role that raises emits `{type:part_error, role, error}` and the dependent part either (i) proceeds WITHOUT that enrichment with an honest in-text marker, or (ii) the whole part fails loud — **open question which, per-role-declared** (`on_fail: "degrade" | "fail"` in the role row). NO silent drop.
- **Disconnect-cancel**: reuse `_voice_stream`'s `client_gone()` (`bridge.py:391`) — a cancelled turn stops kicking off / awaiting further role work and never burns a brain call on a dead socket.
- **Why concurrent, not sequential-with-prefetch:** "Part 1 instant, later parts enriched" REQUIRES the roles to be resolving during Part 1. Sequential prefetch (resolve all roles, then Part 1) would delay Part 1 to the slowest role — defeating the whole point. (The cost: thread management + concurrent VRAM/endpoint pressure — see Open Questions.)

**Ordering** is the shape's `parts` order; a part is emitted only after its predecessors (so the stream stays linear and coherent) AND its `deps` resolve. Part 1 always has `deps=[]` so it never waits.

**The intra-turn address space** `role://<turn_id>/<role_id>` and `part://<turn_id>/<part_id>` is the relationship made literal: it MIRRORS the store's content-addressing without necessarily persisting to the durable store (an open question — persisting would make turns inspectable/replayable like a run; not persisting keeps a turn ephemeral). Either way the *grammar* is the same one the system already speaks.

### (c) Short-response detection — the cheap bypass judge

A one-liner ("yes", "thanks", "what mode am I in?") must NOT spin up the whole machine. A **cheap judge bypasses staging** and routes to plain `chat()`.

**It is a NEW ROLE in `ROLE_REGISTRY`** (mirrors `judge` exactly — fast, no-think, the local 4B):

```python
# ROLE_REGISTRY addition (proposed)
"brevity_judge": {
    "label": "Short-response judge",
    "description": "Decides whether the operator's message warrants a STAGED multi-part "
                   "answer or a single direct line — the staging hot-path gate.",
    "trigger": "chat_staged entry, before any role kickoff",
    "default_model": None,                      # → falls to the brain; PREFERS the local 4B
    "recommended_model": "cyankiwi/Qwen3.5-4B-AWQ-4bit",   # same measured fast pick as `judge`
    "recommended_base_url": "http://localhost:8000/v1",
    "thinking": False,                          # a reasoner stalls the hot path (the judge lesson)
    "output": "one word: STAGE | DIRECT",
    "tools": [], "context": "the operator message + the current mode only",
    "knobs": {"max_tokens": 2048, "temperature": 0},   # 2048 so a thinking-default brain can finish
    "env_model": "COMPANY_BREVITY_MODEL", "env_url": "COMPANY_BREVITY_URL",
},
```

**Mode-biased** (the requirement) — falls out of the mode system for free, layered cheapest-first:
1. **Mode hard-gate (no model call):** if `shape_for(mode) == "direct"` (focus, background, text-only, watch-and-react, decide-for-me) → **always DIRECT, judge never runs.** The directive already says "be extremely brief" / "minimal". Free.
2. **Trivial-message hard-gate (no model call):** a message under N chars / pure acknowledgement → DIRECT. Free.
3. **The judge** only adjudicates the **ambiguous middle** in staging-eligible modes (listening, walkthrough). It returns STAGE|DIRECT. The mode is passed in its context so it can be biased (walkthrough leans STAGE; listening neutral).

So the expensive judge call happens rarely, and the whole staging machine is bypassed for the common one-liner — Part 1 of a `direct` shape IS just `chat()`.

### (d) Coherence across parts — one voice, one thought

Each later part's prompt is assembled so the model continues the SAME utterance, not starts a new one:

```
system = [the EXACT chat() head, :3386–3402 — persona, ground-truth-only,
          model-of-Tim digest, CURRENT MODE directive]      (reused verbatim — rule 3, one source)
       + _chat_context(graph_id, focus, intent=message)      (live ground truth; intent ranks R2)
       + "RETRIEVED FOR THIS PART:\n" + <role outputs resolved for this part's deps>
user   = <the operator message>
assistant (prefill) = <Part 1 text> + <Part 2 text> + …      (all prior parts, verbatim)
system-tail = part.intent + "Continue the SAME reply naturally from where it left off. "
              "Do NOT repeat or re-greet; do NOT restate what you already said. "
              "This is one continuous thought to the operator."
```

Carrying **prior parts as an assistant prefill** + an explicit "continue naturally / don't repeat" instruction is what makes the seams invisible. The persona/voice block is identical across parts (one voice). The FE concatenates `{type:part}` events into one growing bubble so the operator never sees a boundary — the parts are a *production* detail, not a presentation one.

**Verb dispatch across parts (the real open question the shape implies):** staging still goes through the EXISTING `_dispatch_rhm_action` (the ONE whitelist, E6 — non-negotiable). The shape's `may_act` flag declares WHICH part may call verbs (default: only the `synthesise` part; `acknowledge` and `offer` may not — `offer` uses the `suggest`/proposal path, which dispatches nothing). The mode-discipline gate (`chat():3442–3474`) and decide-for-me routing (`:3476–3483`) apply per-part unchanged. **A part calling a verb does NOT bypass any governance** — the staged path reuses the identical dispatch + whitelist + confirmation-fold machinery; it only changes WHEN (which part) a call can originate. This must be stated loudly so the staged path can never become a governance side-door.

---

## How it connects to the mode system (the binding relationship)

The **mode is the single dial** the whole machine reads, FIVE ways from one source (`MODE_DIRECTIVES` + the new per-mode shape/budget binding):
1. **Whether to stage at all** — `shape_for(mode)`: focus/background/text-only/watch/decide-for-me → `direct` (never stage); listening/walkthrough → a staged shape.
2. **Which thought-shape** — the shape's `modes` field selects it (walkthrough → narrate-heavy shape; listening → the default).
3. **Which roles run** — only the roles named in the selected shape's part `deps` kick off (so a leaner mode runs fewer/no enrichers).
4. **The brevity-judge bias** — the mode rides in the judge's context.
5. **The SLOT BUDGET** — see below. The mode caps how much cognition a turn may spend.

### The slot budget (budget = attention — the per-mode cap)

The task names a fifth lever: mode selects a **slot budget**. This is Tim's **budget = attention** frame (Collective Cognition) made concrete at the turn level — a per-mode *ceiling on how much a single reply may cost*: how many parts, how many concurrent enrichers, and a token allotment. It is DISTINCT from shape selection (the shape is the *intended* form; the budget is the *cap* that can trim it).

Proposed as a single-source per-mode cap read ALONGSIDE `_mode_directive` (mirrors it):

```python
# runtime/suite.py — proposed, schema-additive
MODE_BUDGETS = {
    "listening":  {"max_parts": 4, "max_concurrent_roles": 3, "max_tokens_total": 1200},
    "walkthrough":{"max_parts": 6, "max_concurrent_roles": 3, "max_tokens_total": 2000},
    "focus":      {"max_parts": 1, "max_concurrent_roles": 0, "max_tokens_total": 200},   # never stages anyway
    "background": {"max_parts": 1, "max_concurrent_roles": 0, "max_tokens_total": 120},
    # text-only / watch-and-react / decide-for-me → direct shape, budget enforces the 1-part floor
}
def _mode_budget(self, mode): return self.MODE_BUDGETS.get(mode, self.MODE_BUDGETS["listening"])
```

**How the budget binds the queue:** the runner reads `_mode_budget(mode)` at turn start and (i) caps the role threads it kicks off to `max_concurrent_roles` (a shape naming more enrichers than the budget allows → only the highest-priority N run; the rest are skipped with an honest in-stream marker, never silently); (ii) stops emitting parts at `max_parts` (a long shape is trimmed from the tail — the `offer` part is droppable, the `synthesise` part is not); (iii) passes `max_tokens_total` down as the brain-knob ceiling across parts. A `focus`/`background` budget of `max_parts:1, max_concurrent_roles:0` is a SECOND enforcement of "never stage" (belt-and-braces with shape selection) — the cap makes staging structurally impossible there even if a shape were mis-bound. The budget is the attention economy: a deep-work mode spends almost nothing; walkthrough is allowed to spend the most.

This is the same principle the repo already states: *"a new presence mode → behavior comes from the directive; the mode IS a node"* (`AGENTS.md`). Staging extends that — the directive already governed *how much to say*; now it also governs *the shape of how it's said*. No new mode dial; the existing one gains reach.

## Configurable / registry-driven (rule 8)
- **Thought-shapes** = a single-source dict (`THOUGHT_SHAPES`), exposed in `capabilities().thought_shapes`, future-authorable via a `propose_shape`/`apply_shape` path (mirrors panels: governed, additive, git-reversible). Never invent a shape; add a registry row.
- **Roles** (enrichers + the brevity judge) = rows in the existing `ROLE_REGISTRY`, bound via `rhm_config.roles`, validated fail-loud against the registry.
- **Per-mode shape binding** = a `rhm_config` slot (open question: default to the shape's `modes` field; allow override).
- A drift-check should fail loud if a shape names a `role:<id>` not in `ROLE_REGISTRY` (mirrors `drift_acceptance`) — a shape can't reference a role that doesn't exist.

## FORM is half of done (rule 9 — a SEPARATE required lane)
The backend (staged generation + the NDJSON endpoint + the registries) is the FUNCTION half. The **FORM half is a separate, mandatory lane**: the FE must render the part-events as **one unbroken growing bubble** (no visible seams, no per-part chrome), built on the design system's components + tokens, with the offer-card rendered from the existing proposal path. The "feels like one stream" claim is FE-verified, by a separate design-critic — backend-only is **not done**.

---

## Open questions (flagged, not silently decided)

1. **Concurrency implementation — AND the binding-distinct-model CONDITION.** Design intent = genuinely concurrent (ThreadPoolExecutor, roles resolve during Part 1). **A hard precondition for real parallelism, from the registry's own evidence:** `ROLE_REGISTRY` roles default `default_model: None` → *falls to the brain* (`suite.py:935`). An enricher that falls to the brain calls the SAME model on the SAME endpoint as Part 1's brain call — so they contend, there is no real parallelism, and Part 1 is NOT actually instant. **Therefore the staging enrichers MUST bind a DISTINCT model/endpoint** (e.g. the local 4B, exactly as `judge`'s `recommended_model` does, `:940`) for the "Part 1 instant, roles resolving behind it" premise to hold. With both Part 1 (the brain) and the enrichers (the 4B) resident, they genuinely run in parallel; the VRAM cost is N resident models, arbitrated by `ops/cli/gpu.py`. This is a CONFIG condition, not just a nice-to-have. Separately: reuse `runtime/`'s scheduler, or a lightweight in-turn runner that speaks the same fires-when-deps-resolve language? Lean: in-turn runner (the canvas scheduler is graph-oriented + persistent; a turn is ephemeral + tiny).
2. **Per-role on-fail policy.** `degrade` (proceed without the enrichment, honest marker) vs `fail` (the part fails loud). Declare it per-role. Default lean: `degrade` for enrichers (a missing fact-check shouldn't kill the answer), `fail` for a retriever the synthesis genuinely needs.
3. **Persist the intra-turn addresses?** `role://<turn>/<id>` / `part://<turn>/<id>` to the durable store (turns become inspectable/replayable like a run, feeds introspective-data-building) vs ephemeral (cheaper, a turn is not a graph). Lean: emit run-records (`emit_run_record`, already used by `_voice_stream`) for timing, keep the part bodies ephemeral unless replay is wanted.
4. **Brevity-judge cost vs benefit.** The judge adds a hot-path model call in staging-eligible modes. Is the mode hard-gate + trivial hard-gate enough on their own (skip the model judge entirely)? Measure before binding a model — same discipline as `judge`'s measured pick.
5. **Voice circuit integration.** `_voice_stream` (`bridge.py:357`) currently calls `SUITE.chat()` for the full reply, THEN sentence-chunks. A staged turn already produces parts incrementally — could the voice path consume `chat_staged`'s parts directly (Part 1 → speak immediately, later parts → speak as they arrive), collapsing two streaming layers into one? Likely yes, and a strong simplification — but it's a second consumer, design after the text path is proven.
6. **Shape authoring by the brain.** A `propose_shape`/`apply_shape` governed path (mirrors panels). Future; the registry-of-shapes is the seam that makes it possible.
7. **What happens to `action`/`proposal` in the return** when the turn is multi-part — the `done` event should carry the same back-compat shape `chat()` returns (None|dict|list for action; the single proposal), so non-streaming consumers still work.

## Acceptance (how it'd be proven — by USE, not assertion)
- A new `staged_response_acceptance.py`: a staged turn in `listening` mode emits Part 1 before any role future completes (timing assertion — Part 1's emit timestamp < the slowest role's completion); later parts carry the role outputs; the joined reply reads coherently (no re-greet/repeat); `focus`/`background` modes bypass staging (one part, no role calls); a forced role failure surfaces fail-loud per its policy (never silent); a verb called from a part dispatches through the SAME whitelist (E6 holds — a forbidden verb refused end-to-end). Plus the FORM lane: the FE renders one unbroken bubble (design-critic + by-use in the browser).
