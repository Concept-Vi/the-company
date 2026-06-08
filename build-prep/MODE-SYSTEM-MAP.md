# The Mode System — full reach map (`/home/tim/company` @ c614761)

> Built from a 3-reader deep sweep of the unified repo (2026-06-08), after the mode-dial join. Read as a **circuit**, not a list. The dial = `MODE_REGISTRY[mode]` (suite.py:1220, ONE source, 13 axes). The risk this doc beats is under-reading — every claim is file:line-traced. **The headline: the join unified the SOURCE; the REACH downstream was never extended — that gap IS the drift.**

## The shape: one dial → five arms

```
   set_mode (/api/mode ← the presence dial + the mode cards)  →  the `rhm` node in the `system` graph
        │  get_mode() reads it every turn
        ▼
   MODE_REGISTRY[mode]  (13 axes, one source; MODE_SPECS/PART_GRAIN/ACTIVATION_ALLOCATION/MODES/MODE_DIRECTIVES derive)
        │
        ├─ ARM 1 · directive ──────────▶ the system prompt (every turn)            [WIRED · live]
        ├─ ARM 2 · _M_* verb-sets ──────▶ WHICH governed verbs exist this turn      [WIRED · live · most load-bearing]
        ├─ ARM 3 · decide-for-me ───────▶ act-vs-surface (the AUTO/CONFIRM split)    [WIRED · live · 1 hardcoded branch]
        ├─ ARM 4 · grain/shape/stage/cast ▶ the staged reply + which roles fire     [WIRED · live · voice path]
        └─ ARM 5 · live/reserve_r/budget ▶ activation contexts + SlotBudget         [WIRED in code · NO DRIVER]
        ·  brain_config ──────────────────▶ (nothing reads it)                      [DECLARED · reaches nothing]
        ·  consent ───────────────────────▶ (only a UI badge)                       [DECLARED · reaches nothing]
```

## The five arms (what each controls)

- **ARM 1 · directive → the prompt** (WIRED). `_mode_directive` (1621) → `_chat_sys_head` (4928): `"CURRENT MODE — {mode}: {directive}"` rides into every generation. The prose is what makes the model behave differently per mode.
- **ARM 2 · the `_M_*` mode-sets → the action surface** (WIRED, the sharpest gate). `_M_BUILDISH/_M_RUN/_M_CONSULT/_M_ALL_BUT_OFF` (3072-75); each `RHM_VERB_SPECS` verb carries a `.modes` set; `available_verbs(mode,ctx)` (3215, the `mode in s.modes` test) → `_rhm_tools` → the tools array handed to the model. **A mode that doesn't list `build` literally cannot offer it.** Mode = which governed verbs exist this turn.
- **ARM 3 · decide-for-me → governance routing** (WIRED). `if mode=="decide-for-me"` (5067) routes tool-calls through `autonomous_dispatch` (AUTO runs / CONFIRM surfaces) instead of the normal dispatch. *(The one hardcoded mode-name branch in the dispatch path — see lost-opportunity #4.)*
- **ARM 4 · grain/shape/stage/cast → the staged reply + the swarm** (WIRED, voice path). `mode_stages` (1590) → `_should_stage` → focus/background/off collapse to one-shot, never spin the swarm. `shape_for`/`grain_for` shape the staged parts (emitted on `cognition.turn.start`). `cast_for_mode` (4573 → roles.py:210) fires the concurrent `run_swarm`. **Mode = which cognition roles fire + how the reply is shaped.**
- **ARM 5 · live/reserve_r/per_role_ctx/main_ctx_tokens → activation + budget** (WIRED in code, **NO DRIVER**). `activation_allocation` (1524) → `runtime/activation.py`: `live` gates non-turn contexts, `reserve_r` the sacred floor, the rest compute `SlotBudget.from_registry`. **But `fire_activation`/`consolidate_rollup` have no HTTP route + no timer — nothing calls them.** Built, undriven.

## The 8 modes — what each actually does today

| mode | context (resolution lens) | reply | swarm | verbs offered | essence |
|---|---|---|---|---|---|
| **listening** | all strata · full how-to · 4000 | beat · stage | **YES** (6 roles, voice) | full set | full presence + cognition |
| **text-only** | all strata · full · 4000 | paragraph · stage | none (empty cast) | full set | listening's twin, terser typed |
| **background** | events/run/terse-howto/prefs · 1500 | line · **never stages** | none | run/show | low-noise, one-liners |
| **focus** | annotation/chat/event/run · **no how-to** · 800 | line · never stages | none | run/show | don't-disturb deep work |
| **walkthrough** | all strata · full how-to · 6000 | paragraph · stage | none | consult/show | guide me step-by-step |
| **watch-and-react** | event/run/howto/pref · terse · 1500 | line · stage | none | consult/show | silent observer, event-keyed |
| **decide-for-me** | all strata · full · 4000 | paragraph · stage | none | full set | act on the safe things, surface rest |
| **off** | empty — *short-circuits before resolving* | "switch a mode to wake me" | none | none | the RHM is asleep |

**Two findings that condition all of it:** (1) **the swarm fires ONLY for `listening`, ONLY on the voice path** — every role's `mode_scope` is `{"listening"}`; `chat()` (typed/MCP) is always one-shot in every mode; only `chat_parts()` (voice) stages. Concurrent cognition is, today, listening-on-voice-only. (2) **`consent` (offer/act/none) is unwired** — the governance gate (AUTO/CONFIRM via `posture()`) is global + mode-blind; decide-for-me differs from listening only by directive prose, not a distinct dispatch path.

## The substrate underneath (context-resolution + addresses)

- **Context resolution = R2** (suite.py): `current_locus()` (where you clicked, a `ui://` address, persists across the session) → `_r2_gather` collects strata (annotation/chat/event/howto/presentation_pref/run) at the locus **+ its ancestors** → `_r2_score` ranks by **recency · proximity · pin · semantic-cosine(your message)** → `_r2_score_and_cap` keeps the top slice under `R2_BUDGET` (4000 chars). **The budget cap is the keystone** — the cure for the old 396k context-flood. *Attention = budget.*
- **The mode IS the context dial** (WIRED, no `if mode==` in the resolution path): `resolution_spec_for(mode)` → `{strata, howto_detail, budget}` threaded as DATA into `_r2_gather`; the filter is a membership test. Registry-is-truth, structural.
- **Addresses = the shared language:** `run://` (mutable node/role output), `cas://` (immutable content), `ui://` (a screen element, `data-ui-ref`), `code://` (a code symbol → build-scope). The store resolves run/cas (`head→get_content`); the FE drives `ui://`; the swarm writes `run://<turn>/<role>`. **`vec://` IS wired** (CORRECTED 2026-06-08): `store/fs_store.py:put_vector/get_vector` + `store/vector_index.py:query_index` (k-NN) — and it's LIVE-used: R2 (`_r2_score_and_cap:2982`) embeds the intent + each candidate via `complete_embeddings` and cosines them every turn. Embeddings are a first-class, consumed capability everywhere EXCEPT the cognition engine (`run_role` is generate-only — the C op-axis fixes that). **`blob://` remains declared-only.** *(My earlier "vec:// declared-only" was wrong — a propagating-fact error, the coherence problem in miniature.)*
- **The non-loop seam:** R2's bridge resolves a *canvas node's* `run://<graph>/<node>` history; the swarm writes a *role's* `run://<turn>/<role>` — **two parallel addressed edges into the turn, never converging.** The system's own cognition does not yet feed back into what it resolves next turn.

## ★ THE LOST-OPPORTUNITY MAP — where the unified source should reach but doesn't

*The join completed the SOURCE (one MODE_REGISTRY); the REACH was never extended to consume it. Each is a candidate connection, file:line, not a fix:*

1. **The unified `mode_registry()` accessor (1538) has ZERO callers.** The 13-axis single-query the join built is itself unconsumed — every reader still goes through one of the 3 derived half-views. *The most precise statement of the drift.*
2. **The FE sees only 5 of 13 axes.** `capabilities()["mode_registry"]` (702) is built from `MODE_SPECS` — serves label/directive/resolution/subtypes/consent, **drops** grain/shape/stage/live/budget/brain_config. The operator can't see or tune the *cognition half* of each mode. → serve `mode_registry()` instead.
3. **`brain_config` reaches nothing.** Each mode declares which brain it wants (swarm-16k / voice-64k); no code reads it. → the activation/chat path could hand it to the resource-manager (`company up/swap --evict`) so switching presence actually reconfigures VRAM. Today `background` declares "swarm-16k" and nothing changes.
4. **`consent` should drive governance but the posture is hardcoded.** 5 modes "act", 2 "offer", 1 "none" — but the only act-vs-surface routing is `if mode=="decide-for-me"`. → route off the `consent` axis, dissolving the name-branch (registry-is-truth).
5. **Activation is built but undriven.** `live`/`reserve_r`/budget are honoured *if* `fire_activation`/`consolidate_rollup` are called — but no route/timer calls them. → a background/rollup timer (the explicit needs-tim seam, activation.py:264) turns the between-turns cognition the modes allocate into live behaviour.
6. **Auto-detect has the toggle but no detector.** `autodetect_mode` (1690) honours off/suggest/auto over a *supplied* candidate; nothing *produces* one. → the detector is a deferred seam.
7. **The swarm is listening-only.** Only listening's roles declare `mode_scope`; other modes fire no cognition even on voice. → if other modes want cognition, their casts need declaring. And `chat()` (typed) never stages at all — cognition is voice-only.
8. **The cognition↔resolution non-loop (substrate #seam):** the swarm's `run://` outputs don't feed back into R2's next-turn resolution. → the cleanest place a "the system sees its own thinking" wire attaches.

## Bottom line
**The mode dial is a true pillar — and more declared than driven.** Four arms are live (prompt · action-surface · governance-routing · staged-reply/swarm); the context lens is genuinely mode-driven (the keystone, wired). But the activation/budget arm has no driver, two axes (brain_config, consent) reach nothing, the unified accessor has no callers, the FE sees half the axes, and cognition is listening-on-voice-only. The join made the source whole; extending the reach is the next pillar-work — and it's "needed in a lot of places," exactly as suspected.
