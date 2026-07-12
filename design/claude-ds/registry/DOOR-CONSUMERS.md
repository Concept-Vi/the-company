# DOOR-CONSUMERS — who walks which render door TODAY (v2, corrected patterns; for the U13 reconciliation)
_v1's narrow patterns missed the `window.__cvRenderType` consumption shape — caught by refutation pass._

## THE HEADLINE: the doors are ALREADY JOINED in code
`core/cv-node.js:351-352` — CV_NODE's block/surface/doc solver DELEGATES to `window.__cvRenderType`
(the RenderType component). `system/glyphic-system.html:554` documents it as the design: "CV_NODE
invents no renderer: the solvers re-point at the homes that already draw (glyphic → CV_GLYPHIC.compose,
token → the axis's resolveCSS, block/surface/doc → __cvRenderType)". So U13's reconciliation is NOT a
build — CV_NODE = the universal resolve mechanism; RenderType = its block-family render delegate.
What's missing is DOCTRINE: the DS's own CLAUDE.md render-door table names RenderType alone and never
states the delegation — that's the doc fix.

## RenderType/Slide — direct or via window.__cvRenderType — 10 consumer file(s)
- `_demo/verify_entry.js`
- `app/canvases/Workshop.jsx`
- `app/index.html`
- `app/registry/types-thumb.jsx`
- `core/RenderType.d.ts`
- `core/RenderType.jsx`
- `core/Slide.jsx`
- `core/cv-node.js`
- `core/slide-archetypes.html`
- `system/glyphic-system.html`

## CV_NODE — resolve/render/lens/candidates — 5 consumer file(s)
- `app/registry/actions.js`
- `system/block-system.html`
- `system/glyphic-system.html`
- `system/inspector.html`
- `system/studio-ng.html`

## CV_NODE — solver registration — 2 consumer file(s)
- `app/registry/block-type.js`
- `app/registry/text-type.js`

## CV_BLOCK.chrome/walk (container solver) — 4 consumer file(s)
- `app/ai/ai-block.js`
- `app/ai/ai-layout.js`
- `system/block-system.html`
- `system/skin-system.html`

## ContainmentTree (react tree renderer) — 6 consumer file(s)
- `app/canvases/workshop/WidgetBuilder.jsx`
- `app/index.html`
- `core/ContainmentTree.d.ts`
- `core/ContainmentTree.jsx`
- `core/RenderType.jsx`
- `core/generative-core.html`

## DiagramSolver — 13 consumer file(s)
- `_demo/verify_g11.js`
- `app/canvases/workshop/WidgetBuilder.jsx`
- `app/index.html`
- `app/registry/kinds-type.js`
- `core/ContainmentTree.d.ts`
- `core/ContainmentTree.jsx`
- `core/DiagramSolver.d.ts`
- `core/DiagramSolver.jsx`
- `core/RenderType.jsx`
- `core/generative-core.html`
- `system/glyphgraph-generator.html`
- `system/language.html`
- `system/the-whole-thing.html`

## CV_GLYPHIC (mark composition) — 5 consumer file(s)
- `app/registry/inspector.js`
- `system/glyphic-parts.html`
- `system/glyphic-system.html`
- `system/skin-system.html`
- `system/system-map.html`

## Files touching BOTH (1)
- `system/glyphic-system.html`