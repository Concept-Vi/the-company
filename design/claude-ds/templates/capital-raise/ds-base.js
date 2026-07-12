// Loads this design system into the template. In a consuming project, point
// base at the bound DS folder relative to this file (e.g. '_ds/<folder>' at
// the project root, '../_ds/<folder>' one level down) — one line to edit.
(() => {
  const base = '../..';
  // SKIN SCOPE (UNIFICATION-SWEEP §2.3): templates are SKINNED SURFACES.
  // glass is the un-scoped default binding, so this is inert until a template
  // (or its consumer) dials another world — but it makes every template
  // addressable by the skin laws. Never overrides an authored choice.
  if (!document.documentElement.hasAttribute('data-skin')) document.documentElement.setAttribute('data-skin', 'glass');
  for (const p of ["colors_and_type.css","tokens/surfaces.css","tokens/sizing.css","tokens/depth.css","tokens/motion.css","tokens/diagram.css","tokens/theme.css","tokens/density.css","tokens/layout.css","tokens/states.css","tokens/focus.css","tokens/icons.css","tokens/dataviz.css","tokens/imagery.css","tokens/canvas.css","tokens/provenance.css","tokens/export.css","tokens/texture.css","core/containers.css","styles.css"]) {
    const l = document.createElement('link');
    l.rel = 'stylesheet'; l.href = base + '/' + p;
    document.head.appendChild(l);
  }
  const shapes = document.createElement('script');
  shapes.src = base + '/assets/icons/cv-shapes.js';   // window.CV_SHAPES — canonical entity geometry
  document.head.appendChild(shapes);
  const icons = document.createElement('script');
  icons.src = base + '/assets/icons/cv-icons.js';   // window.CV_ICONS for icon atoms / node icons
  document.head.appendChild(icons);
  const s = document.createElement('script');
  s.src = base + '/_ds_bundle.js';
  s.onerror = () => console.error('ds-base.js: failed to load ' + s.src + ' — if this is a consuming project, point the base line in ds-base.js at the bound _ds/<folder> tree relative to this page (e.g. _ds/<folder> at the project root, ../_ds/<folder> one level down); in a fresh design system this can just mean the bundle is not compiled yet');
  document.head.appendChild(s);
  // the universal paged-surface fitter (slide/print stages letterbox to fit)
  const f = document.createElement('script');
  f.src = base + '/core/slide-fit.js?v=3';
  document.head.appendChild(f);
})();
