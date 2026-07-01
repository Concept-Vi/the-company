# CLAUDE.md — how to work in this project

> This file is injected into every conversation. It is the operating manual for the **ConceptV
> Design System** — a *unified generative system*, not a pile of components. Read it before
> touching anything, and keep it true as the system grows.

## 0. The one idea

**Everything is defined once and referenced everywhere.** Change a value, a type, an archetype, a
prompt, or the voice in its *single home* and it propagates to every consumer — because consumers
hold references, never copies. Your prime directive when adding or changing anything: **find the one
home, edit there, reference from everywhere else. Never create a second place for a thing to live.**
If you catch yourself copy-pasting a value, a prompt, a shape, or a rule — stop: that is drift, and
drift is the failure mode this whole system exists to prevent.

Companion docs (read when relevant): `analysis/HANDOFF.md` (master briefing), `analysis/AXES.md`
(the generative model), `analysis/INTEGRATION.md` (the wiring/anti-drift contract — now covers all
four registries), `analysis/UNIFICATION.md` (how the halves were welded), `analysis/FINDINGS-LOG.md`
(running build memory — **append every slice, newest first**), `DESIGN-LANGUAGE.md` + `README.md` v2
(the codified rules — keep in lockstep with the code).

## 1. The four single sources of truth

Everything in the system lives in one of four registries. Each has ONE home; everything else
references it. To change behaviour anywhere, change the home.

| System | Single home | Consumed via | Add/extend by |
|---|---|---|---|
| **Design tokens** (colour, type, space, depth, motion, zoning, states…) | `styles.css` → `colors_and_type.css` + `tokens/*.css` (L0 primitives → L1 roles → L2 component tokens) | `var(--token)` in CSS; `data-*` knobs for axes | Add at the lowest valid layer; higher layers `var()` it. Never a raw hex/px in a consumer. |
| **Types** (token→atom→block→system→surface→doc→template) | `window.CV_REGISTRY` (`app/registry/types-core.js`); core archetypes/atoms seeded from `core/archetype-catalog.js` | `CV_REGISTRY.resolve(id)`; rendered by `RenderType`/`Slide`/the two solvers | `CV_REGISTRY.register(type)` (single-inheritance via `extends`, slots, variables). One catalogue — never a parallel list. |
| **The generative engine** (design = f(content, axis)) | `core/` — `ContainmentTree` (block solver), `DiagramSolver` (graph solver), `RenderType`/`Slide` (the bridge), on the shared `cv-nodes.d.ts` node type | `window.__cvRenderType` / the DS bundle exports | Grow the solver (a new atom `role`, a new diagram `type`) — as data/registry, not a new code branch where avoidable. |
| **AI** (providers · behaviours · skills · capabilities · context) | `window.CV_AI` (`app/ai/ai-registry.js` + `ai-seed.js` + `ai-capabilities-canvas.js`) | `CV_AI.execute(capabilityId, …)` · `CV_AI.complete(prompt)` · `CV_AI.resolveProvider(id)` | `CV_AI.register(entry)`. One catalogue of every model touch. |

These mirror each other deliberately (same `register/resolve/lineage/query/subscribe` API, same
layer/inheritance idea) so learning one teaches the others.

## 2. How to add or change things (the propagation rules)

**Colour / type / spacing / any design value** → edit the token at its lowest layer in
`colors_and_type.css` / `tokens/*.css`. Every component, solver output, template, and card that
`var()`s it updates automatically. New colour = new L0 primitive + an L1 role (mixed toward
`--zone-ground`); consumers reference the *role*. (Full layer rules: `analysis/INTEGRATION.md`.)

**A new component / block / atom / archetype** → register a Type in `CV_REGISTRY` (or add an
archetype to `core/archetype-catalog.js`, which seeds the registry). It renders through the one
engine under the axis-dials — it inherits the DNA by construction because it has no literals. Do
**not** hand-lay-out a layout or fork a parallel component list.

**A new axis / dial** (surface, LOD, density, theme, motion, register, loading, focus…) → follow
the established knob pattern: a `data-*` attribute + CSS vars, exactly like `data-theme` /
`--density` already work. Thread it through `RenderType`→`ContainmentTree` so every surface gets it.
No new mechanism.

**Anything AI** (a model provider, a tone/behaviour, a one-click skill, a generative move, a
screen's context) → register it in `CV_AI`:
- **provider** — a model endpoint. `resolveProvider` binds it to its live runtime and throws if
  absent. Swap models in one place.
- **behaviour** — an instruction fragment composed into prompts (the **voice** is `voice.conceptv`;
  the regeneration **angle** is parametric). Source the voice from here — never inline it.
- **skill** — a named parametric intent a user invokes (the transforms). The composer's transform
  menu is a *projection* of these — register a skill and it appears, no UI edit.
- **capability** — a generative move (id == the target/move name, so the catalogue IS the dispatch).
  Declares surfaces, behaviours, provider, params; carries a `run` (or `build`/`parse`) co-located
  with its prompt helpers. 43 today across 14 families.
- **context** — a surface-keyed resolver that projects "what screen Vi is on" into the prompt
  context. `execute()` resolves it from `CV_AI.active` (pushed by the bridge) automatically.

To make Vi do something new: `CV_AI.register({layer:'capability', …, run})` then call
`CV_AI.execute('<id>', {…})`. To call a model directly for a one-off, use `CV_AI.complete(prompt)`
(string or `{messages}`) — never `window.claude.complete` and never `window.cvOpenAI.generateImage`
directly (route image work through `CV_AI.resolveProvider('openai-image')`).

## 3. Non-negotiables

- **No second home for any value.** No raw hex/px in consumers; no inlined prompts or voice strings;
  no parallel type/atom/archetype/capability lists. One concept = one entry.
- **Loud fail, never silent.** Missing provider/runtime/capability/type → `throw`, don't degrade to a
  default or swallow in a `catch`. (User-facing toasts are fine; silently returning `[]`/`null`/a
  fallback is not.)
- **The interface is a projection of the registries**, not a parallel structure. UI reads from
  `CV_REGISTRY` / `CV_AI` (menus, galleries, the registry inspector's `AIRegistryPanel`) so the
  interface and the engine are synchronised by construction.
- **Audit before you touch.** `grep` for the existing home before adding anything — the system is
  mature; reconcile/extend, don't duplicate. Most "hardcoded" values in `app/`/kits are legitimate
  token *definitions*, not drift — check before "fixing".
- **Vigilance against mere technical success.** "It compiles / renders / passes check" ≠ "it is
  computed from the rules." Always ask: is this *referenced from the one source*, or did I just
  hand-set a copy?

## 4. After every change

1. `check_design_system` — reports components, cards, tokens, AI/type registries, and ISSUES
   (untyped tokens, orphans, duplicate names, raw `.jsx` in cards, stale manifest). Fix what it
   flags; re-run until clean. ("MANIFEST STALE" mid-turn is expected — it rebuilds at end of turn.)
2. Append a slice to `analysis/FINDINGS-LOG.md` (what you audited, changed, why; open items).
3. Keep `DESIGN-LANGUAGE.md` + `README.md` v2 in lockstep when you add a *rule the system makes*.
4. `ready_for_verification({path:'app/index.html'})` — surfaces it, checks the load, forks the verifier.

## 5. Traps (learned the hard way)

- `_ds_bundle.js` / `_ds_manifest.json` / `_adherence.oxlintrc.json` are **compiled output — never
  hand-edit.** The bundle is stale mid-turn; to verify a compiled component the same turn use the
  Babel-harness pattern (`_qa/core-test.html`), else end the turn and let the verifier check.
- Script **load order** matters: `ai-registry.js` → `ai-seed.js` → `ai-capabilities-canvas.js` →
  consumers; the registry must exist before anything resolves through it. `CV_AI` capabilities that
  need the composer's prompt helpers are registered from `AIEngine.jsx` (where the helpers live).
- Self-mounting `.jsx` (`createRoot(getElementById('app'))` at top level) poison the shared bundle —
  DOM-guard them (`if (document.getElementById('app'))`).
- When registering a registry entry with a function member (`render`/`run`/`build`/`resolveCtx`),
  make sure `normalize()` carries that field through — a dropped field = a silently inert entry.

> The mandate: keep building the **one unified system**. Every new thing is *defined inside a
> registry and referenced from everywhere*, so there is no second place for it to drift from. If
> something feels flat, copied, or hand-set — it's wrong; make it computed, single-sourced, deep.
