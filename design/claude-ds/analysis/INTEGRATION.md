# INTEGRATION — how it all wires together without drift

> The risk: adding new capability as a *parallel* system that drifts from the existing one. The
> defence is one rule, applied to **every** subsystem: **one home per concept; everything else
> references it.** Then a change to the home propagates everywhere instead of forking. This doc is
> the wiring contract — it covers all four single-source registries (tokens, types, the engine, AI).

## 0. The four registries (one home each — change the home, it propagates)
| Registry | Home | Consumers reference it via |
|---|---|---|
| **Tokens** | `styles.css` → `colors_and_type.css` + `tokens/*.css` | `var(--token)`, `data-*` axis knobs |
| **Types** | `window.CV_REGISTRY` (`app/registry/types-core.js`) + `core/archetype-catalog.js` | `CV_REGISTRY.resolve(id)` → `RenderType`/`Slide`/solvers |
| **Engine** | `core/` solvers on `cv-nodes.d.ts` | `window.__cvRenderType`, DS bundle exports |
| **AI** | `window.CV_AI` (`app/ai/ai-registry.js` + `ai-seed.js` + `ai-capabilities-canvas.js`) | `CV_AI.execute(id)` / `.complete` / `.resolveProvider` |

All four share the same API shape (`register`/`resolve`/`lineage`/`query`/`subscribe`, layers +
single-inheritance) on purpose. The sections below detail tokens (the original contract); §6 covers
types + AI with the same discipline.

## 1. One source of truth, layered (new things enter at the right layer)
```
styles.css  ──imports──▶  colors_and_type.css + tokens/*.css      ← THE source of truth
        │
        ├─ L0 PRIMITIVES     pigments, --ramp-*, --zone-ground, raw scales   ← new COLOURS enter here
        ├─ L1 SEMANTIC ROLES --zone-*-surface, colour-role (ink/gold/bronze), status set  ← derived via color-mix
        ├─ L2 COMPONENT TOKENS  --dgm-*, --icon-*, --elev-*, control sizes    ← reference L1, never literals
        └─ consumers: components / templates / block+graph solvers  ← reference L0–L2 ONLY, never raw hex/px
```
**Rule:** a value is defined **once**, at its lowest valid layer. Higher layers reference it with
`var(...)`. Recalibrating L0/L1 (e.g. the real zone ladder, softened gold) **auto-updates every
consumer** — that is the anti-drift guarantee.

## 2. How each kind of NEW thing connects in
- **New colours** → add as **L0 primitives** (a pigment / a `--ramp-*` stop / a status hue) in `colors_and_type.css`. Then give them **L1 semantic roles** (mix toward `--zone-ground` like the rest). Components consume the role, never the raw colour. *Never* add a colour straight into a component.
- **New atoms** (hatch, frame-signature, stepper, bullet-kinds) → tokens in the **existing** `tokens/*.css` they belong to (texture→`depth.css`, bullets→a list token, stepper→`diagram.css`/a component). Extend, don't create parallel files.
- **New axes** (LOD, surface paged↔scroll↔print) → follow the **established knob pattern**: a `data-*` attribute + CSS vars (exactly how `data-theme`/`--density` already work). No new mechanism.
- **The generative core** (block + graph solvers, container model) → built as components that **consume L0–L2 tokens only**, so generated output inherits the DNA *by construction* — a generated diagram or block can't drift because it has no literals to drift with.

## 3. Reconcile, don't duplicate (the recalibration discipline)
- When a finding **corrects** an existing token (zone ladder too saturated, gold too acidic): **edit the value in place; keep the name.** All consumers update. Keep the old as `--x-legacy` only if something external depends on it.
- When a finding is **genuinely new**: add it to the correct existing layer/file. Search first (`grep`) to avoid a near-duplicate token.
- **One concept = one token.** If two tokens mean the same thing, merge (alias one to the other).

## 4. Guardrails that catch drift automatically
- **The compiler** (`check_design_system`) reads tokens + components every turn → run after each change; it flags untyped tokens, orphans, duplicate component names, stale manifest.
- **Adherence lint** (`_adherence.oxlintrc.json`, compiler-generated) → can flag hardcoded hex/px in consumers ("use a token"). The ABSENT-list (REQUIREMENTS A7) becomes lint rules (no pure black, no left-accent-border, etc.).
- **Specimen cards + DESIGN-LANGUAGE.md** → every new token/role gets a card so the visible DS tab stays in sync with the code (docs can't silently drift from values).
- **Deprecate, don't delete/rename** → protects any consuming project bound to the system.

## 5. Order of operations (so nothing is built on sand)
1. Recalibrate/extend **L0–L1 tokens** (colours, ramp, zone ladder, new frames) + refresh specimen cards → `check_design_system` clean.
2. Add **L2 component tokens** for new atoms.
3. Build the **generative core** (container model + block/graph solvers) consuming L0–L2.
4. Build **components/templates** on the core.
5. Each step ends with `check_design_system` + a specimen/card so the DS tab reflects it.

> Net: new parts don't *attach* to the system — they're **defined inside its token graph**, and
> everything downstream references that graph. There's no second place for a value to live, so
> there's nothing to drift from.

## 6. The same contract for Types and AI (not just tokens)

The token rule generalises: **one registry home per concept; consumers hold references, never copies.**

### Types (`CV_REGISTRY`) — the composition graph
- **One catalogue.** Every composable definition (token→atom→block→system→surface→doc→template) is a
  registered Type. Core archetypes/atoms are seeded from `core/archetype-catalog.js` into the same
  registry — there is no parallel "built-in list" beside it.
- **Add by registering, extend by `extends`.** A variant is a child Type that inherits defaults +
  slots + variables (leaf wins). Editing a parent propagates to children. Never fork a Type by copy.
- **Rendered by the one engine.** A Type renders through `RenderType`/`Slide` + the two solvers under
  the axis-dials, so it inherits the DNA by construction (it has no literals). Don't hand-lay-out.
- **New axis = a `data-*` knob threaded through `RenderType`→`ContainmentTree`**, exactly like tokens'
  `data-theme`/`--density`. Every surface gets it for free.

### AI (`CV_AI`) — every model touch
- **One catalogue of moves.** Each generative operation is a registered **capability** (`id` ==
  the move name, so the catalogue IS the dispatch). 43 today across 14 families. Add a move =
  `CV_AI.register({layer:'capability', …, run})`; never a bespoke function with an inline prompt.
- **Providers are the only model binding.** `resolveProvider(id)` binds to the live runtime
  (`window.claude` / `window.cvOpenAI`) and throws if absent. Swap models in one place. Consumers
  call `CV_AI.execute(id)` or `CV_AI.complete(prompt)` — **never** `window.claude.complete` or
  `window.cvOpenAI.generateImage` directly.
- **Voice + angle are behaviours, composed into prompts.** The voice lives once at `voice.conceptv`;
  every prompt sources it (`CV_AI.get('voice.conceptv').text`) — never inline the voice string.
- **Skills + context are projections.** The transform menu is a projection of `skill` entries; the
  prompt context is a projection of the active surface via `context` resolvers. Register data → the
  interface and the prompts update; the registry inspector's `AIRegistryPanel` shows the whole
  catalogue. Interface and AI read one source.
- **Loud, never silent.** Missing capability/provider/runtime → throw. Don't swallow in a `catch` and
  return a degraded default.

### Guardrails for Types + AI (mirror §4)
- `check_design_system` validates the type catalogue + manifest every turn.
- The registry inspector (`AIRegistryPanel` + the Type inspector) is the visible projection — if a
  move/Type isn't in the catalogue, it isn't real. Keep the catalogue comprehensive.
- When registering an entry with a function member (`render`/`run`/`build`/`resolveCtx`), confirm
  `normalize()` carries that field — a dropped field = a silently inert entry.

> Net (all four registries): there is exactly one home for every value, type, archetype, move,
> provider, and the voice. Everything else references it. Change the home → it propagates everywhere.
> That is the whole system: **`design = f(content, axisPosition)` and `ai = f(capability, context, params)`,
> both computed from registries that have no duplicated literals to drift from.**
