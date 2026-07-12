# STUDIO — the conversational + compositional editor (master scope)

> Written at Info/Tim's Studio steer (slice 93). The durable home for the plan so it isn't lost
> across the build. Companion: `system/glyphic-system.html` §11 (concept + live proof),
> `system/studio.html` (working concept demo). Mirror key moves in `FINDINGS-LOG.md`.

## The principle (what we're building)

A **Studio**: one surface where you build the system *both* by assembling from a library/tools onto a
live interactive viewer/editor *and* by talking to it (chat, and two-way voice). The thesis that makes
this not-two-things:

> **The single node system projects, through ONE mechanism, to BOTH the UI and the AI.** A node already
> declares everything about itself (kind · value-slots = axis subscriptions · sockets · parts ·
> decorators · conditions). Add **actions** (what can be DONE to it). Then one projection emits the
> inspector you click AND the tool schema the AI calls — from the same declaration. Clicking and
> talking are two inputs to **one action layer**; the viewer re-projects after either. Voice is just a
> provider feeding the same loop.

`design = f(content, axis)` and `ai = f(capability, context, params)` converge: **`ui = project(node)`
and `tools = project(node)` are the same `project`.**

## The registries it adds / extends (one home each)

| Concern | Home | Status |
|---|---|---|
| **Variable resolution** (one mechanism for params/context/conditions/projection) | `app/registry/vars.js` → `CV_VARS` | BUILT |
| **Actions** (verbs/tools/functions; actionType + variable params + per-action Skill + targets + run) | `app/registry/actions.js` → `CV_ACTIONS` | BUILT (6 seed verbs) |
| **Projection** (node → UI inspector + AI tool schema + shared context) | `app/registry/project.js` → `CV_PROJECT` | BUILT |
| **Providers** incl. voice + user-connectable local/remote | `CV_AI` provider layer (resolveProvider → `CV_HOST`) | EXTENDED (`ai-studio.js`: `voice.openai`, `provider.local`) |
| **Context sharing** (selection/screen/clicks → Vi's context, same var mechanism) | `CV_AI` context layer (`context.studio`) | BUILT |
| **Command loop** (instruction → one action call from the live tool schema) | `CV_AI` capability `studio.command` | BUILT |

All reference the existing node/axis/decorator/AI registries; nothing is a parallel store.

## How the loop works (one action layer, many inputs)

```
            ┌──────── CV_PROJECT.toInspector(node) ──────► UI controls (click)
 a NODE ────┤                                                      │
 (CV_NODE)  └──────── CV_PROJECT.toToolSchema(node) ─► AI tools ──►│  (chat / voice)
                                                                   ▼
   voice provider ─transcript─► CV_AI.execute('studio.command') ─► {action, args}
                                                                   ▼
                          CV_ACTIONS.invoke(action, args, ctx)  ── args resolved by CV_VARS
                                                                   ▼  (mutates the node)
                          CV_PROJECT.toContext(state) ◄──────── re-project ► viewer + inspector + tools
```

- **Context sharing** is the same variable mechanism: `CV_PROJECT.toContext(studioState)` produces the
  one context blob (`selection · node · hover · clicks · screen`); the AI prompt reads it via the
  `context.studio` resolver, and `CV_ACTIONS`/`CV_COND` read it via `CV_VARS` — one set of paths.
- **Providers**: `CV_AI.resolveProvider` already delegates unknown runtime kinds to `CV_HOST`, so a
  local model or a different voice engine is registered exactly like `voice.openai` and bound by
  `CV_HOST`. Loud (throws) until connected — never a silent fallback.

## Build order (each step independently usable; check between)

1. **CV_VARS** — one variable mechanism; `CV_COND.getField` delegates to it. ✅
2. **CV_ACTIONS** — verbs with actionType, variable params, per-action Skill, targets, run;
   `applicable(node)` + `invoke()`; seed select/set-value/fill-socket/open/generate/remove. ✅
3. **CV_PROJECT** — `toInspector` + `toToolSchema` + `toContext`; `coherent()` proves the UI action
   set === the AI tool set (one source). ✅
4. **ai-studio.js** — voice + local providers, `context.studio`, `studio.command`. ✅
5. **The concept Studio** (`system/studio.html`) — viewer + projected inspector + AI-schema panel +
   shared-context panel + chat→action loop (local interpreter standing in for the model). ✅
6. **Live model + voice** — wire `studio.command` to a connected provider; wire `voice.openai` through
   `CV_HOST` (mic in / TTS out) onto the same loop. PENDING (needs a connected runtime).
7. **The real editor** — replace the single-glyphic demo with the full canvas: a tree of nodes
   (slides/panels/glyphics), drag-from-library into sockets (`CV_NODE.candidates`), multi-select,
   undo (actions are the diff units), keyboard. PENDING.
8. **The library + tools rail** — every registry projected as a palette (Types, axis values/tokens,
   actions, decorators); drag onto the canvas = `fill-socket`/`set-value`. PENDING.

## DO-NOT-LOSE — carried scope

- **The one inspector** (from the §10 decorators work): reads `applicable(node)` for empty slots +
  `decoratorsOf(node)` for present ones — the Studio inspector IS this, generalised beyond glyphics.
- **Generalised foundry**: "fill any socket" — `generate` action already routes to the generatable
  capability for any kind; the foundry UI (propose → feedback → save) plugs in as a generate surface.
- **Undo/redo as action inverses** — each `CV_ACTIONS` verb should declare (or compute) its inverse so
  history is free and single-sourced. (New: add `invert(args, ctx)` to the action schema.)
- **Selection as a node too** — a multi-selection is itself a node (kind `selection`) so actions apply
  to it uniformly. (Idea — keeps "everything is a node" honest at the interaction layer.)
- **Macros / recorded skills** — a sequence of action invocations is itself a registrable action
  (an actionType `macro`), so "a Skill" can be a recorded chain, not just a prompt. (New idea.)

## Anti-drift notes (learned this slice)

- **Dissolved a hardcode**: the `generatable` decorator had a static `kind→capability` map; it now
  QUERIES `CV_AI` (a capability declares `generates: [classifications]` as its single source). The rule
  Info gave: a hardcode is a class problem to dissolve or a capability to build — applied.
- **One path-reader**: `CV_VARS.getPath` is the single dotted-path mechanism; `CV_COND` delegates to it
  so "a.b.c" means the same everywhere (conditions, actions, context, projection).
- **Part slots flatten for projection**: a glyphic's form/symbol/fill live on its parts; `CV_NODE.
  flatValueSlots` merges them so the inspector + the tool schema see one editable facet set (no second
  list).

## Autonomy note

Info/Tim steer by reacting to the built thing (the DS tab + this plan). Add to scope anything found
that needs merging into this foundation, else it becomes "a part of the system that is not part of the
system." Use the questions tool only to batch genuinely-blocking choices.

## Update — slice 94: the self-building layer (Root Unity)

The system is now named **Root Unity** (√unit) and can grow itself through its own verbs:
- **`CV_QUERY`** (`app/registry/query.js`) — derive-by-query. The generalised form of the generatable
  fix: a relationship is computed by querying the single source that owns the fact, never a stored map.
  `relations(node,{from,field})` / `relation(...)`; also a `{query}` value-spec in `CV_VARS`.
- **`CV_EVENTS`** (`app/registry/events.js`, 9th registry) — triggers `{on,when,do,args}` + an `emit`
  bus. The AI emits where it's looking (`ai.focus`) and a declared rule highlights it — attention as a
  rule, not an intentional call. Seeded: ai-focus/ai-blur/selection-change → highlight.
- **Meta-actions** in `CV_ACTIONS` — `define-kind · add-field · relate · define-rule · define-axis ·
  define-decorator · define-trigger · define-action · define-macro`. Each writes to the one home for
  what it defines, so the backend is built through the interface.
- **Undo-as-inverse** (`CV_ACTIONS.inverse` + per-verb `invert`) and **macros-as-actions**
  (`actionType:'macro'`, replayed steps) — both built. `highlight` is a `ui` action fired by triggers.
- **Studio** (`system/studio.html`) gained: Undo, AI-focus auto-highlight, a live "build the backend"
  panel (define a kind, watch it appear). Mark: `system/root-unity-mark.html`.
- Proof: `_qa/meta-test.html` 19/19. Carried-scope additions: **selection-as-node**, the full
  node-tree editor, the library/tools rail (every registry as a palette), live model + voice.
