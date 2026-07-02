# AREA-8 — the MODE / RHM / LOADOUT / model-routing config-and-switching spine

> Wave-2 COVERAGE agent. Wave 1 narrowed to "browser-side CV_AI wiring" (LIVE-INSTRUMENT.md G-L1…G-L8)
> and **never read the Company's presence-mode / loadout / RHM-repoint spine** — the exact mechanism
> Tim's insight names: *"the live instrument should be a MODE/LOADOUT the system SWITCHES INTO."*
> This file grounds + corrects that. **The headline: the entry mechanism Tim described ALREADY EXISTS,
> end-to-end, and is verified by acceptance tests.** Glyphgraph is not a parallel app and not (only) a
> browser wiring job — it is **`modes/glyphgraph.py` + a `services.json` combo + extract-role files**,
> entered by `set_mode('glyphgraph')`. Every claim marked **Observed (file:line)** / **Inferred** / **My-idea**.

---

## 0 · The correction to the layer-1 plan (read this first)

LIVE-INSTRUMENT.md frames the build as eight browser-centric wiring groups around `CV_AI` (the design
system's JS AI registry) calling the Company over HTTP. That framing is **not wrong, but it is the wrong
altitude for the ENTRY.** The Company already has a first-class, registry-driven, governed machine for
*"switch the whole presence + load the right models + repoint the brain"* — the **presence-MODE spine**.
The live instrument should ride it as **one more mode**, not be assembled ad hoc in the browser. Concretely:

- **Wave 1's anchor "my-idea" #44** (wire local models into `CV_AI` as providers) is real but **downstream**.
  The *upstream* truth is: the model loadout is selected by **entering a mode**, server-side, through
  `Suite.set_mode` → loadout-swap confirm → `apply_loadout` → `ensure_resident` + **RHM repoint**. The
  browser doesn't pick the models; the **mode** does. *(My-idea / correction)*
- **The LIVE-INSTRUMENT catalogue row "live canvas pattern — REUSE tldraw OR build reactflow — DECISION"**
  is downstream of a missing row: **"the live instrument is a MODE (`modes/glyphgraph.py`) + a LOADOUT
  combo (`services.json`)."** That row is the spine wave 1 omitted.
- **The extract-swarm** ("concurrent small local models, one per concern") is not new infrastructure —
  it is `runtime/cognition.run_swarm` firing **role files** (`roles/<id>.py`), exactly like the existing
  `dragnet_coarse/fine/design` extract roles. **Observed** (`roles/`, `runtime/cognition.py:1413`).

---

## 1 · (a) What a MODE is + how the system enters / switches one

### A MODE is a file-discovered registry row (the lone hardcode, now dissolved)
**Observed** (`runtime/modes_registry.py:1-91`): presence modes were "the system's ONE remaining hardcoded
dict (a `MODE_REGISTRY = {...}` literal in suite.py)". They are now an **open, file-discovered registry**:
one `modes/<id>.py` per mode declaring a module-level `MODE` dict; `discover_modes(dirs)` does
`os.listdir → importlib`, fail-loud on a malformed/duplicate entry, **id == filename stem verbatim**
(hyphens kept — `text-only`, `decide-for-me` are real ids). **Add a mode = drop a file. No code edit.**
This mirrors `runtime/roles.py` and `runtime/mode_detection_rules.py` — the ONE registry mechanism.

**The mode schema** (`modes_registry.py:30-32`):
- `_REQUIRED = ("label", "directive", "resolution", "consent", "grain", "shape", "stage", "live",
  "reserve_r", "per_role_ctx", "main_ctx_tokens", "brain_config")`
- `_OPTIONAL = ("subtypes", "loadout_class", "voice")`
- plus a discovery-only integer `order` (modes are **order-bearing**; stripped from the returned decl so
  each row is byte-for-byte the literal it replaced). **Observed** (`modes_registry.py:43-58`).

Field meanings (**Observed**, `modes/AGENTS.md:18-24` + the mode files):
- `directive` — the behavioural prose injected into the RHM prompt (e.g. walkthrough: *"Actively guide:
  narrate what you are doing and direct the operator's attention step by step."* — `modes/walkthrough.py:7`).
- `resolution` `{strata, howto_detail, budget}` — the context-gather depth for a turn.
- `consent` ∈ `offer | act | none` — the act-vs-surface governance axis (§(e)/§4 below).
- `grain` / `shape` / `stage` — reply shaping (beat/line/paragraph; linear-stream; whether to stage).
- `live` — which live-cognition lanes run (`per-turn`/`background`/`sense`/`rollup`).
- `reserve_r` / `per_role_ctx` / `main_ctx_tokens` — the activation/slot budget (the `SlotBudget` is
  COMPUTED from these — `modes_registry.py` + `suite.py:2406`).
- `brain_config` — a **brain loadout NAME** (e.g. `voice-64k`, `swarm-16k`) — the gpu_util variant the
  mode wants. **(See §2 for how this differs from `loadout_class` — a wrinkle for Tim.)**
- `loadout_class` (optional) — a **services.json combo name** (e.g. `interaction`) — the multi-service
  loadout the mode wants resident.
- `voice` ∈ `on | off` — the mode's voice default (`text-only`/`off` declare off).
- `subtypes` — partial axis-overrides for named sub-postures (e.g. listening `general`/`deep`).

**The 8 shipped modes** (`modes/`): `listening` (order 0), `text-only`, `background`, `watch-and-react`,
`focus` (30), `walkthrough` (40), `decide-for-me` (60), `off`. **They are explicitly a STARTER SET —
"none final"** (`modes/AGENTS.md:30`); Tim 2026-06-28: *"modes are a starter set, open, all in registries,
adjustable."* **This is the open door glyphgraph walks through.**

### Entering / switching a mode — `Suite.set_mode`
**Observed** (`runtime/suite.py:2626-2641`): `set_mode(mode)` →
1. validate `mode ∈ self.MODES` (fail loud);
2. write `{"mode": mode, "overlays": []}` to the system graph's MODE_NODE (one `set_config`; **switching a
   mode CLEARS overlays** — a switch is a fresh presence gesture);
3. emit `presence → {mode}` to `ui://chrome/toolbar` (the dial lives in the toolbar);
4. **`_maybe_surface_loadout_swap(mode)`** — if the new mode binds a `loadout_class` whose services aren't
   all resident, **SURFACE a loadout_swap confirm** (never auto-actuate).

> **The switch is FREE** (a config write); **changing the resident loadout is expensive + service-affecting
> → CONFIRM** (governance). The mode switch ALWAYS succeeds; the model swap waits for operator approval.
> **The autonomous loop can RAISE the confirm but can NEVER self-approve it.** (`suite.py:2635-2640`)

### Mode auto-detection (the suggest/auto toggle) — file-discovered rules
**Observed** (`runtime/mode_detection_rules.py`): a **MODE-DETECTION-RULE** is a file-discovered row
(`mode_detection_rules/<id>.py`) mapping a **signal condition → a candidate mode**. The condition is a
`rules.RULE_OPS` **data-AST** (NOT a lambda/eval), validated at discovery, evaluated against the live
`activity_signal()` snapshot. Rules are **first-match-wins, ordered by an explicit integer `priority`**
(never listdir order). The detector (`activation.detect_mode_candidate`) produces a candidate and feeds
the off/suggest/auto toggle — it **never calls `set_mode` of its own authority** (the toggle owns the
posture). **The floor**: a rule PRODUCES a candidate, performs NO effect; it can never forge an approve or
launch a build. *(Relevance to glyphgraph in §5.)*

### Mode STACKING (base + overlays) — the per-turn refinement layer
**Observed** (`tests/mode_stacking_acceptance.py` + `suite.py:2485-2583`): a mode can be STACKED as a base
+ a list of **overlays** (partial axis-override dicts). `resolve_mode_stack(mode)` folds base+overlays into
ONE resolved row that every per-mode consumer reads. **Depth-1 (no overlays) is byte-identical to pre-stacking**
(the golden-master gate: all 8 modes × 7 consumers equal the precomputed oracle). An overlay can refine ANY
axis; an unknown axis **fails loud** (`suite.py`, test T7). `push_overlay/pop_overlay/clear_overlays/get_overlays`
is the API. **Inferred**: glyphgraph could use an overlay to temporarily deepen its extract budget mid-session
("show-me" vs "guided") without defining a second mode — exactly how `walkthrough` declares its subtypes.

---

## 2 · (b) What a LOADOUT is + the atomic-switch mechanism

### Two overlapping "loadout" concepts on one mode row — A WRINKLE FOR TIM
There are **two distinct loadout fields** on a mode, and they are not the same thing — this duplication is
worth surfacing:

| Field | What it names | What it loads | Variant applied? |
|---|---|---|---|
| `loadout_class` | a **services.json combo** (`interaction`) | **N services together** via `apply_loadout`→`ensure_resident` each + RHM repoint | yes (full atomic switch) |
| `brain_config` | a **brain loadout NAME** (`voice-64k`) — a gpu_util variant of the brain | **ONE brain service** resident; `variant_applied=False` | **NO — needs-tim** |

**Observed** (`ops/cli/capabilities.py:558-602`): `ensure_loadout_for_mode` reads a mode's `brain_config`,
resolves the `brain`-group service from the registry, makes it resident — but **explicitly does NOT apply
the gpu_util variant** (`variant_applied=False`, `variant_note=...`), because a `brain_config` value
"encodes a gpu_util VARIANT … NOT a service-key" and applying it is a `company config <svc> gpu_util <v>`
+ restart, **flagged needs-tim at `suite.py:1513`**. So `brain_config` is the *weaker, partial* loadout
concept; `loadout_class` is the *real* multi-service one.

> **For glyphgraph the answer is unambiguous: use `loadout_class`.** It is the ONLY mechanism that loads
> *several* services together (the extract brain + embedder + ear + voice) — exactly the layer-1 pipeline's
> service list. `brain_config` only ensures one brain. *(My-idea / decision, grounded in the two fields above.)*

### A LOADOUT (combo) is a services.json entry with class-variants
**Observed** (`ops/services.json` `combos`): a combo is a "named set of services meant to run TOGETHER."
The **loadout-CLASS mechanism** (2026-06-28): a combo can `extends: <base>` to inherit a base's service list
and override the difference (`swap`/`add`/`remove`). `registry.combos()` resolves this centrally, fail-loud
on a missing base / bad swap target / unknown service / extends-cycle. Real examples:
- `interaction` (the everyday-default class base): `['embed-pplx', 'chat-4b-fp8', 'rerank-jina', 'stt-moonshine', 'tts-kokoro']` — realtime conversation + Speech-To-Action with the local brain.
- `interaction-fp8` (`extends: interaction`, `remove: ['rerank-jina']`) — the FP8-4B everyday that FITS the 16GB card.
- `interaction-parakeet` (`extends: interaction`, `swap: {stt-moonshine: stt-parakeet-onnx}`) — same loadout, different ear.
- `quality-9b` — the larger 9B brain SOLO (fills the card; runs alone).
- `instrument` — `['bridge', 'embed-pplx']` (the surface API + its embedder).

**This is exactly the shape glyphgraph's combo takes** (§5).

### The ATOMIC-SWITCH mechanism — `apply_loadout` → ensure_resident → RHM repoint
**Observed** (`runtime/suite.py:2726-2837`). This is the load-bearing machine the layer-1 plan never named:

1. **`apply_loadout(sid)`** (`:2726`) — ACTUATE a surfaced loadout_swap, **on operator APPROVE only**.
   Approval is **READ FROM THE INBOX** (`inbox.is_approved(sid)`), never a caller flag → the loop can raise
   the confirm but can't self-approve. Fail loud on unknown/unapproved sid.
2. It captures the **prior brain pointer** (the revert anchor), then for each service in the loadout calls
   **`ensure_resident(s, evict=True, wait=True)`** — the ONE gated actuator, which rides the RAM+VRAM
   invariant (fail-loud, evict-on-authorize), **so an approved swap can never OOM** (`:2750-2755`).
3. **`_repoint_rhm_for_loadout(services, reg, prior=...)`** (`:2772-2822`) — **completes the atomic switch**:
   - find the **brain-group service NAMED IN THIS LOADOUT** (`_brain_in_loadout`, `:2765` — registry-is-truth:
     the loadout's own brain, NOT `brain_keys[0]`; >1 brain = fail loud; 0 = tool-only, no repoint);
   - read its model + endpoint from the registry;
   - **VERIFY BY USE** — a real inference probe (`_cap._probe_tools`), not a port poll;
   - if the new brain won't answer → **REVERT** (bring the prior brain back, repoint to it) and **raise**
     (`EnsureResidentError`) — *"no silent broken brain."* This **dissolves the broken-brain class**: after a
     switch, *"what is resident"* and *"what the RHM points at"* can never diverge.
4. **`repoint_rhm_to_loadout(services)`** (`:2824`) — the PUBLIC repoint for the bare CLI door (`company up
   @loadout` → bridge `/api/loadout/repoint` → here). **ONE repoint logic, two callers** (the confirm-gated
   `apply_loadout` AND the CLI door) — either door dissolves the broken-brain class.

> **This is precisely Tim's "atomic-switch actuator" from the Loadout-Resolution mission** (the repoint-RHM
> fix). It is BUILT and verified. The layer-1 plan's "G-L1 provider role-layer / verify CORS" treats model
> selection as a browser concern; **it is actually this server-side, governed, OOM-safe, verify-by-probe
> machine.** *(Correction.)*

### The WORK-layer twin — `_gate_work_requires`
**Observed** (`suite.py:2665-2697`): a unit of *work* (a cascade/action) can declare `requires: <loadout_class>`.
The gate resolves the loadout; if resident → proceed; if any service is **missing** → SURFACE a loadout_swap
confirm and **`raise GovernanceError`** so the work does NOT run against the wrong loadout (no-silent-degrade).
Same `_resolve_loadout` + `inbox.surface`. **Relevance**: a glyphgraph cascade (NL→graph) could `requires:
'glyphgraph'` so it refuses to run unless the extract-swarm is resident. *(My-idea, grounded.)*

### Loadout governance posture
**Observed** (`tests/mode_loadout_acceptance.py` T2): `governance.POLICY['loadout_swap'] == CONFIRM`
(single-source gate). `_resolve_loadout(class)` → `(services, missing)`; unknown class → fail loud (T3).
An UNAPPROVED `apply_loadout` raises `GovernanceError` (T6); `apply_surfaced` routes a loadout_swap to
`apply_loadout` and the gate still holds (T8).

---

## 3 · (c) What the RHM is + how it drives the conversation / brain

**The RHM ("Right-Hand-Man") is not a single module — it is a CONFIG SLOT + the conversation engine +
a source-router**, all on `Suite`. There is no `rhm_*.py`; the RHM lives in `suite.py` + `brain_router.py`.

### The RHM config — `rhm_config()` / `set_rhm_config()`
**Observed** (`suite.py:3084-3140`): `rhm_config()` is a pure getter (~50 callers; **never raises** — returns
`model: None` when unconfigured; the loud failure lives at the chat chokepoint `require_brain`, not here —
*no silent `-pro` fallback, cognition-is-role-resolved*). The slots that matter for glyphgraph:
- `model` / `base_url` — **the brain pointer** (what `_repoint_rhm_for_loadout` sets).
- `persona`, `voice_enabled`, `voice_out` (`browser|server|both`), `tts_engine`/`tts_voice`, `voice_path`
  (`pipeline|s2s`), **`voice_input_mode` (`push_to_talk|auto_listen`)**, `stt` (the ear).
- **`roles`** — `{role_id: {model?, base_url?, knobs?}}` per the ROLE_REGISTRY (the per-role model bindings;
  the brain stays its OWN slot, NOT a role).
- `think` (default **False** — snappy realtime chat; True surfaces the reasoning trace) and `brain_knobs`
  (the vLLM sampling family).

`set_rhm_config(updates)` (`:3160`) whitelists the writable slots, fail-loud-validates each
(`voice_input_mode`/`voice_path`/`brain_knobs`/`think`). **This is the single seam the atomic switch writes
the brain pointer through.**

### `voice_enabled()` precedence (`suite.py:3142-3158`)
mode `off` → never voice; else an explicit operator override wins; else the **mode's declared `voice`
default** (registry-is-truth). So a glyphgraph mode declaring `voice: 'on'` is voice-enabled by construction.

### The RHM mind — the SUPERVISOR-AS-LOADABLE-BRAIN source router
**Observed** (`runtime/brain_router.py`): the RHM's mind "RESOLVES which cognition-SOURCE answers a question"
— it is **the resolver, one altitude up** (a discrete `resolve_slot` select, the same primitive a surface
uses). `route_source(question)` → `'fleet' | 'recall' | 'model'` via a **declared keyword→source table**
(axes-are-registries: a new source = a row, not a code branch). `'model'` is the default conversational mind
(`Suite.chat` — today's whole RHM mind). **The floor**: it READs + runs a model + PROPOSEs; it emits NO
resolve_address/approve/dispatch/spawn — a 'fleet' answer implying an action returns a **proposal** the
operator/lead fires. Fail-soft: an unroutable/down source degrades to `'model'`, never a crash.
**Inferred**: glyphgraph's "compose the graph" judge could be a new source-row, or simply the `'model'` leg
with the glyphgraph directive in the prompt.

### The conversation chokepoint — `Suite.chat`
**Observed** (`suite.py:7070`): `chat(message, graph_id, focus, …)` is the RHM turn. The mode's `directive`
is injected via `_mode_directive(mode)` (`:2839` — reads the folded stack when overlays are active, else the
precomputed source). The consent axis routes the turn's verbs (§4).

---

## 4 · (d) How model_routing resolves a role → model

### `resolve_model` — the unified entry point (BUILT, but DORMANT — accuracy correction)
**Observed** (`runtime/model_routing.py:13-15`): its own docstring says **"PHASE 1 … NOTHING is routed
through it yet … Phase 1 changes NO behaviour."** It is the *unified entry point* (one `intent` in →
`{model, base_url, provider, why, satisfied}` out) that **WRAPS + REUSES three existing seams** — it does
NOT fork a second router. **Do not read this as the live production path.** The intents:
- `{kind:"clone", context_tokens, model?}` → the TIM-RULE context-size pick (kimi ≤256K else 1M;
  `cc_clone.pick_ollama_model_for_context`).
- `{kind:"role", role_id}` → **`Suite.resolve_role_binding`** → `roles.resolve_binding`.
- `{kind:"capability", capability}` → `Suite.capability_providers` (first provider providing the tags).

### The LIVE role→model resolution is `roles.resolve_binding` — with the `satisfied` FLOOR trap
**Observed** (`model_routing.py:22-28`, `_role_branch:61-81`): the role seam does **NOT raise** when no
provider matches a role that declares a `default_model` — it returns the DEFAULT (`provider="default",
satisfied=False`): **the brain FLOOR**. So a role can "look resolved" because it silently floored to the
resident 4B while the intended cloud brain was never live. **`resolve_model` surfaces `satisfied` VERBATIM
so a caller asserts a REAL capability match — assert `satisfied`, not a non-empty `model`.** **This is the
exact `cognition-is-role-resolved` law from Tim's memory; the floor is the no-green-paint trap.**

**Role files are the unit** (**Observed**, `roles/judge.py`): a role declares `id/label/default_model/
recommended_model/recommended_base_url/thinking/output/tools/model_binding(requires)`. `default_model: None`
→ falls to the RHM brain (always available). The `judge` role is the model for the **finished-thought
endpoint** and the **template for extract-roles** (fast, `thinking:False`, no tools, schema-constrained).

---

## 5 · (e) EXACTLY how "enter glyphgraph mode" rides this spine — the artifacts

This is the payoff. The layer-1 pipeline (LISTEN→EXTRACT→RESOLVE→ICON→PLACE→RENDER→NARRATE→LOOP) is **a
mode + a combo + role files**. Below are the concrete, real-schema artifacts. *(My-idea / proposed — built
against the verified schemas above; tentative, for Tim to correct.)*

### 5.1 · `modes/glyphgraph.py` — the new presence mode (against the real `_REQUIRED` schema)
```python
# modes/glyphgraph.py — presence mode «glyphgraph» (the live-instrument mode). PROPOSED.
MODE = {
    'order': 50,
    'label': 'Glyphgraph',
    'directive': ("You are co-authoring a LIVING glyphgraph from the conversation. As the operator "
                  "speaks a project, extract the things/relations/states, resolve each to a glyphic, "
                  "place them on the canvas, and narrate the graph back. When the operator corrects "
                  "('no, the buyer's gone cold'), re-extract and mutate the graph."),
    'resolution': {'strata': None, 'howto_detail': 'full', 'budget': 6000},
    'subtypes': {'guided': {}, 'free': {'budget': 8000}},   # like walkthrough's guided/show-me
    'consent': 'act',          # the AI mutates the graph autonomously (reversible) — see 5.4
    'grain': 'paragraph',
    'shape': 'linear-stream',
    'stage': True,
    'live': ['per-turn', 'background', 'sense'],   # 'sense' = the standing extract perception lane
    'reserve_r': 2,
    'per_role_ctx': 1500,
    'main_ctx_tokens': 0,
    'brain_config': 'voice-64k',     # the brain gpu_util variant (partial; see the wrinkle in §2)
    'loadout_class': 'glyphgraph',   # ← THE REAL LOADOUT: the combo in 5.2 (the multi-service one)
    'voice': 'on',
}
```

### 5.2 · `services.json` combo `glyphgraph` — the loadout (the pipeline's service list)
```jsonc
// ops/services.json → combos.glyphgraph  (PROPOSED — extends the proven `interaction` class)
"glyphgraph": {
  "extends": "interaction",          // inherit embed-pplx + brain + ear + tts (the proven base)
  "note": "The LIVE-INSTRUMENT loadout: NL→glyphgraph. Extract-swarm brain + embed-pplx (semantic icon lookup) + ear (stt) + tts-kokoro (narrate).",
  // base interaction already supplies: embed-pplx, chat-4b-fp8 (brain), rerank-jina, stt-moonshine, tts-kokoro
  // optionally swap the brain for the composer/judge tier, or add the 9B for the JUDGE leg:
  // "add": ["chat-4b-fp8"]   // the extract workers + the strong composer share the resident brain via run_swarm
}
```
> The pipeline's stages **ARE this combo's service list**: `embed-pplx` = stage-4 semantic icon lookup;
> `chat-4b-fp8` = the EXTRACT workers + JUDGE/composer (one resident brain with concurrency — see §5.3);
> `stt-moonshine` = LISTEN; `tts-kokoro` = NARRATE. The icon foundry (`glyphic.generate`) is an LLM call
> on the same brain. **No new service type — a new combination.** *(My-idea, grounded in §2's combo shape.)*

### 5.3 · The EXTRACT roles — `roles/glyph_entities.py` etc., fired via `run_swarm`
The extract layer is **role files**, fired concurrently by `runtime/cognition.run_swarm` (`:1413`) — the
SAME machine the existing `dragnet_coarse/fine/design` extract roles use. Each role models on `judge`
(**`thinking:False`, schema-constrained, short-context, no tools** — fast on the hot path):
```python
# roles/glyph_entities.py — extract THINGS from the utterance (PROPOSED). Mirrors roles/dragnet_fine.py.
ROLE = {
    "id": "glyph_entities",
    "label": "Glyphgraph entity extractor",
    "default_model": None,             # → the resident loadout brain (chat-4b-fp8); fast
    "thinking": False,                 # hot path — no reasoning stall (the judge-role discipline)
    "prompt_template": "...",          # one concern: list the entities + their type
    "schema": {...},                   # json_schema guided-decode (cognition.run_role:492 — vLLM honours it)
    "tools": [],
}
# siblings: roles/glyph_relations.py, roles/glyph_states.py, roles/glyph_placement.py
# the JUDGE/composer: roles/glyph_compose.py — the STRONG role that folds the swarm into one graph delta.
```
**Observed** (`cognition.py:1413-1482`): `run_swarm(roles, ctx, store, turn_id=..., budget=SlotBudget)`
dispatches the wave CONCURRENTLY (a `ThreadPoolExecutor` sized to `budget.swarm_slots = max_num_seqs − R`),
each role writing its validated JSON to `run://<turn>/<role>`, joining at the barrier, reading every value
back via the canonical resolver, one batched rollup. **Fail loud** — a role failure is captured per-run AND
re-raised after the barrier (the wave can't silently lose a role). **Tim's extraction-vs-judgment law IS the
field's own mechanism**: many small role-runs EXTRACT in parallel (`run_swarm`), one strong `glyph_compose`
JUDGES. *(Grounded — this is the system's existing answer, not a new build.)*

**Schema-constrained decode is real** (**Observed**, `cognition.py:492-515`): `run_role` derives
`response_format.json_schema` from `schema=`; the resident vLLM honours it; a role declaring a schema against
a model that declares `json_schema=false` **fails loud** (no silent downgrade). Both residents (AWQ + FP8)
declare `json_schema=true`.

### 5.4 · The ENTRY PATH — the exact call sequence
```
operator/auto-detect → Suite.set_mode('glyphgraph')           # suite.py:2626
  → writes mode + clears overlays (free; always succeeds)
  → _maybe_surface_loadout_swap('glyphgraph')                 # suite.py:2699
      → _resolve_loadout('glyphgraph') → (services, missing)  # reads combos.glyphgraph
      → if missing: inbox.surface('loadout_swap', …)          # CONFIRM (governance) — NOT actuated
  → emit 'presence → glyphgraph' to ui://chrome/toolbar
operator APPROVES the loadout_swap in the inbox               # the loop can raise, never self-approve
  → Suite.apply_loadout(sid)                                  # suite.py:2726 (reads is_approved)
      → ensure_resident(each service, evict=True, wait=True)  # RAM+VRAM-gated; cannot OOM
      → _repoint_rhm_for_loadout(services)                    # point RHM brain at glyphgraph's brain
          → _probe_tools(endpoint, model)                     # VERIFY BY USE; revert+raise on regression
  → RHM now: resident extract-swarm + composer, brain repointed, voice on, directive injected
```
Now a turn (`Suite.chat`) injects the glyphgraph `directive`, the EXTRACT roles fire at pauses via
`run_swarm`, the composer judges, the resolve/icon/place/render/narrate stages run, and **consent='act'**
routes the graph-mutation verbs.

### 5.5 · The CONSENT axis governs the voice-correction LOOP (the novel frontier's safety)
**Observed** (`tests/mode_consent_registry_acceptance.py`, `suite.py:6986`): the act-vs-surface routing of a
dispatched RHM verb keys off the **mode's declared `consent`** — `if self.mode_registry(mode)["consent"] ==
"act"` (registry-is-truth, **NOT** a `mode == "decide-for-me"` name-branch). consent='act' routes through
`autonomous_dispatch` (`suite.py:5696`), which **routes by the verb's POSTURE** — AUTO-class verbs (reversible)
run; CONFIRM-class verbs SURFACE a draft; **it NEVER self-approves**. So a glyphgraph mode with `consent: 'act'`
means: *"add/mutate a node" is reversible → the AI does it live; anything destructive/irreversible surfaces.*
**This is exactly the governance the layer-1 plan's "voice-correction loop … build last, verify by use" needs
and never named.** If glyphgraph should ASK before mutating, declare `consent: 'offer'` — a one-field change,
no code. *(Correction — the LOOP's safety already has a registry-driven home.)*

### 5.6 · Two doors to the loadout — and why the MODE door is preferred
**Observed** (`suite.py:2824` + `bridge.py:95-98`): a loadout can be entered two ways —
1. **the MODE door**: `set_mode('glyphgraph')` → confirm → `apply_loadout` (carries the **whole presence
   posture**: directive, consent, voice, grain, live-lanes, brain-config);
2. **the bare CLI door**: `company up @glyphgraph` → bridge `/api/loadout/repoint` → `repoint_rhm_to_loadout`
   (services only; same verify-by-probe + revert, but **no presence posture**).

> **Prefer the mode door for glyphgraph**: it sets not just the models but the *behaviour* (the directive
> that tells the brain to co-author a graph, the consent that lets it act, voice on, the extract live-lanes).
> The CLI door is the "I already started the services, just follow them" path. *(My-idea / recommendation.)*

---

## 6 · Where the no-staleness GOVERNING LAW is honoured (and where to watch)

**Honoured (Observed):** modes, detection-rules, roles, combos are ALL file-discovered registries (add-a-file,
no code edit); `_resolve_loadout` reads the ONE combos table (no parallel map); `_brain_in_loadout` reads the
loadout's own brain from the registry (not `brain_keys[0]`); `set_rhm_config` whitelists + fail-loud-validates;
`run_role` fails loud on a schema/model capability mismatch (no silent downgrade); the loadout swap rides the
OOM-safe `ensure_resident`; the repoint verifies-by-probe and reverts. **The spine is already resolution-native.**

**Watch (the wrinkles to surface for Tim):**
- **`brain_config` vs `loadout_class` duplication** (§2) — two loadout concepts on one row; `brain_config`'s
  gpu_util variant is `variant_applied=False`/needs-tim. Glyphgraph should rely on `loadout_class`; the
  `brain_config` partiality is a pre-existing gap, not glyphgraph's to fix, but it's in the row glyphgraph fills.
- **`resolve_model` is dormant** (§4) — the unified router is built but nothing routes through it; live
  resolution still flows through the three seams it wraps. Don't build glyphgraph assuming it's the live path.
- **The `satisfied` floor** (§4) — if glyphgraph binds a role to a non-resident cloud brain, it silently floors
  to the resident 4B (`satisfied=False`). Assert `satisfied`, never truthiness, when verifying glyphgraph's roles.

---

## 7 · The catalogue — what the layer-1 plan should ADD (mode/loadout spine rows)

| Piece | Verdict | Where (Observed) |
|---|---|---|
| presence-mode registry | **REUSE — drop `modes/glyphgraph.py`** | `runtime/modes_registry.py`; `modes/` |
| mode entry/switch | **REUSE** `set_mode` (+ loadout-swap confirm) | `suite.py:2626` |
| mode auto-detection | **EXTEND** (optional `mode_detection_rules/<id>.py` to suggest glyphgraph) | `runtime/mode_detection_rules.py` |
| mode stacking/overlays | **REUSE** (guided/free as overlays or subtypes) | `suite.py:2485`; `tests/mode_stacking_acceptance.py` |
| loadout combo | **BUILD** `combos.glyphgraph` (extends `interaction`) | `ops/services.json` |
| atomic loadout switch | **REUSE** `apply_loadout`→`ensure_resident`→`_repoint_rhm_for_loadout` (OOM-safe, verify-by-probe, revert) | `suite.py:2726-2837` |
| work-layer loadout gate | **REUSE** `_gate_work_requires` (a glyphgraph cascade `requires:'glyphgraph'`) | `suite.py:2665` |
| RHM brain pointer | **REUSE** `rhm_config`/`set_rhm_config` (the switch writes here) | `suite.py:3084-3196` |
| RHM source router | **REUSE/EXTEND** `brain_router.route_source` (a glyphgraph source-row, or the `model` leg) | `runtime/brain_router.py` |
| extract-swarm | **BUILD** `roles/glyph_*.py`, fire via `run_swarm` (modeled on dragnet/judge) | `runtime/cognition.py:1413`; `roles/` |
| schema-constrained decode | **REUSE** (`schema=` → json_schema guided-decode, fail-loud) | `runtime/cognition.py:492` |
| extract JUDGE/composer | **BUILD** `roles/glyph_compose.py` (the strong role) | `roles/` |
| consent governance of the loop | **REUSE** the `consent` axis (act→`autonomous_dispatch` by posture) | `suite.py:6986`, `5696` |
| role→model resolution | **REUSE** `resolve_role_binding`/`roles.resolve_binding` (assert `satisfied`) | `runtime/model_routing.py`; `runtime/roles.py` |

---

## 3-line summary
The entry mechanism Tim named — *"a MODE/LOADOUT the system SWITCHES INTO"* — **already exists end-to-end
and is acceptance-verified**: a file-discovered presence-MODE registry (`modes/<id>.py`), `set_mode` →
governed loadout-swap confirm → `apply_loadout` → `ensure_resident` (OOM-safe) → `_repoint_rhm_for_loadout`
(verify-by-probe + revert), with the extract-swarm being `run_swarm` over role files and the voice-correction
loop's safety being the mode's `consent` axis. Glyphgraph is therefore **`modes/glyphgraph.py` + a
`services.json` `glyphgraph` combo (extends `interaction`) + `roles/glyph_*.py` extract roles + a
`glyph_compose` judge** — entered by `set_mode('glyphgraph')`, NOT a parallel app or a browser-only wiring job.
Wrinkles for Tim: `brain_config` vs `loadout_class` are two loadout concepts on one row (use `loadout_class`);
`resolve_model` is built-but-dormant (live resolution still flows through `roles.resolve_binding`, with the
`satisfied`-floor trap); the mode door is preferred over the bare CLI door because it carries the whole presence posture.

Path: `/home/tim/company/design/claude-ds/analysis/glyphic-language/live-instrument/findings/AREA-8-mode-rhm-loadout-spine.md`
