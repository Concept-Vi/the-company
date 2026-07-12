/* ============================================================
   ConceptV Design System — index.js
   ------------------------------------------------------------
   THIS is the sanctioned import surface.

   `_adherence.oxlintrc.json`'s `no-restricted-imports` rule blocks
   deep imports of component/registry internals (`components/**`,
   `core/**`, `app/registry/**`, `axes/**`, …) with the message
   "Import design-system components from 'index.js', not component
   internals." — but until this file existed, nothing actually sat
   at that door: the only working consumption path was the compiled
   `_ds_bundle.js`, which mounts everything onto a hash-suffixed
   global (`window.ConceptVDesignSystem_c8f43c`) that no consumer
   could be expected to know or type. This file is the honest,
   minimal door the lint has been presuming all along.

   It does NOT re-implement or duplicate anything — `core/`,
   `components/`, and the four registries (`CV_REGISTRY`, `CV_AI`,
   `CV_AXES`, `CV_NODE`/`CV_ACTIONS`/`CV_HOST`) remain their single
   homes (see design/claude-ds/CLAUDE.md §1). This module is a THIN,
   LOUD-FAIL accessor layer in front of the two doors that already
   exist:

     1. `getDS()`        — the compiled bundle's component/core
                            exports (Avatar, Button, RenderType,
                            ContainmentTree, DiagramSolver, Slide, …)
     2. `getRegistry(id)` — the named global registries
                            (CV_REGISTRY, CV_AI, CV_AXES, CV_NODE,
                            CV_ACTIONS, CV_HOST, CV_ICONS, CV_GLYPHIC,
                            CV_MEANING, CV_BLOCK, CV_LAYOUT_GRAMMAR)

   Both throw LOUDLY (never return undefined/null/a stub) if the
   thing consumers asked for isn't loaded yet — per CLAUDE.md §3
   ("Loud fail, never silent").

   CONSUMPTION MODEL — this DS has no bundler-level module build.
   `_ds_bundle.js` is compiled output (CLAUDE.md §5: never hand-edit,
   and it mounts itself onto `window` as a side effect — it is not
   an ES module and exports nothing via `export`). So the real
   sequence in an HTML surface is:

       <script src="_ds_bundle.js"></script>   <!-- mounts window.ConceptVDesignSystem_c8f43c + registries -->
       <script type="module">
         import { getDS, getRegistry } from './index.js';
         const { Button, RenderType } = getDS();
         const CV_AI = getRegistry('CV_AI');
       </script>

   index.js itself has ZERO runtime dependencies and does no work at
   import time — it only reaches for `window.*` lazily, inside the
   accessor calls, so importing this file before the bundle has
   loaded is safe (the throw happens on CALL, not on import).
   ============================================================ */

/** The bundle's namespace-mangled global. Never reference this
 * hash-suffixed name directly from a consumer — go through getDS(). */
const BUNDLE_GLOBAL = 'ConceptVDesignSystem_c8f43c';

/** Every registry global this DS exposes (design/claude-ds/CLAUDE.md
 * §1's four single-sources-of-truth, plus the sibling registries the
 * bundle also mounts: icons, glyphic language, meaning, block types,
 * layout grammar). One list — extend it here when a new `window.CV_*`
 * registry is registered, never let a consumer discover it by typo. */
const REGISTRY_GLOBALS = [
  'CV_REGISTRY',       // Types: token→atom→block→system→surface→doc→template
  'CV_AI',              // AI: providers · behaviours · skills · capabilities · context
  'CV_AXES',            // the generative axes (color/density/depth/motion/…) dial registry
  'CV_NODE',            // the shared cv-node type / graph node model
  'CV_ACTIONS',         // the action registry (composed behaviors)
  'CV_HOST',            // host-runtime bindings (where a provider's runtime actually lives)
  'CV_ICONS',           // icon registry
  'CV_GLYPHIC',         // the glyphic-language composer
  'CV_MEANING',         // the meaning-field registry (glyphic language's semantics)
  'CV_BLOCK',           // block-type registry (ContainmentTree's vocabulary)
  'CV_LAYOUT_GRAMMAR',  // layout-grammar registry
];

/**
 * getDS() — the sanctioned door onto the compiled bundle.
 *
 * Returns the bundle's export object (its components + core:
 * Avatar, Badge, Button, Card, Glyphic, Input, Modal, Popover,
 * Segmented, Select, Stepper, Switch, Tabs, Tooltip,
 * ContainmentTree, DiagramSolver, RenderType, CoreTypes, Slide,
 * Archetypes — see `_ds_bundle.js`'s `@ds-bundle` header comment for
 * the authoritative, generated list).
 *
 * THROWS if `_ds_bundle.js` has not been loaded (script tag missing,
 * loaded after this call, or failed) — never returns undefined so a
 * consumer silently renders nothing (CLAUDE.md §3: loud fail).
 *
 * @returns {object} the bundle's namespace object
 */
function getDS() {
  if (typeof window === 'undefined') {
    throw new Error('[conceptv-design-system] getDS(): no `window` — this DS is browser-only (the bundle mounts onto window at script-load time). Not usable in a non-browser/SSR context without a DOM shim.');
  }
  const ns = window[BUNDLE_GLOBAL];
  if (!ns || typeof ns !== 'object') {
    throw new Error('[conceptv-design-system] getDS(): window.' + BUNDLE_GLOBAL + ' is not loaded. Load _ds_bundle.js via a <script> tag BEFORE importing/calling this module\'s consumers (see index.js header for the load order). Never silently falls back to an empty object.');
  }
  return ns;
}

/**
 * getRegistry(id) — the sanctioned door onto a named registry global
 * (one of REGISTRY_GLOBALS).
 *
 * THROWS if `id` is not a known registry name, or if the registry
 * hasn't mounted onto `window` yet (script load order — see
 * CLAUDE.md §5: `ai-registry.js` → `ai-seed.js` →
 * `ai-capabilities-canvas.js` → consumers).
 *
 * @param {string} id one of REGISTRY_GLOBALS, e.g. 'CV_AI'
 * @returns {object} the live registry
 */
function getRegistry(id) {
  if (!REGISTRY_GLOBALS.includes(id)) {
    throw new Error('[conceptv-design-system] getRegistry("' + id + '"): unknown registry. Known registries: ' + REGISTRY_GLOBALS.join(', ') + '. If you just registered a new window.CV_* global, add it to REGISTRY_GLOBALS in index.js.');
  }
  if (typeof window === 'undefined') {
    throw new Error('[conceptv-design-system] getRegistry("' + id + '"): no `window` — registries mount onto window at script-load time; this DS is browser-only.');
  }
  const reg = window[id];
  if (!reg) {
    throw new Error('[conceptv-design-system] getRegistry("' + id + '"): window.' + id + ' is not loaded yet. Load _ds_bundle.js (or the registry\'s source script, in its documented load order) BEFORE calling getRegistry(). Never silently falls back to an empty registry.');
  }
  return reg;
}

/**
 * listRegistries() — introspection helper: the known registry ids,
 * annotated with whether each is currently mounted. Never throws —
 * this one is meant for tooling/diagnostics (e.g. "why is getRegistry
 * throwing?"), not for driving app logic.
 *
 * @returns {{id: string, loaded: boolean}[]}
 */
function listRegistries() {
  const w = typeof window === 'undefined' ? {} : window;
  return REGISTRY_GLOBALS.map((id) => ({ id, loaded: !!w[id] }));
}

export { getDS, getRegistry, listRegistries, BUNDLE_GLOBAL, REGISTRY_GLOBALS };
