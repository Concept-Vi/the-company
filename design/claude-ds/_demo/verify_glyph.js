// Headless verification of the relational-glyphic GENERATION: load the real engine files (window shim),
// call CV_GLYPHIC.composeRelation with the real face-index rel data, prove it composes valid SVG.
const fs = require('fs');
global.window = global;                       // the IIFEs assign to window
global.document = { getElementById: () => null, addEventListener(){}, createElement: () => ({}) };
const load = (p) => { try { eval(fs.readFileSync(p, 'utf8')); } catch (e) { console.log('LOAD ERR', p, e.message); } };
['assets/icons/cv-icons.js','assets/icons/cv-vi-glyph.js','assets/icons/cv-shapes.js',
 'assets/icons/cv-edges.js','assets/icons/cv-meaning.js','assets/icons/cv-glyphics.js'].forEach(load);
 // (cv-meaning.js is required: composeRelation reads CV_MEANING.describeRelation — the
 //  one home of meaning. It was missing from this harness's load list; the production
 //  index.html load order already includes it.)

console.log('CV_SHAPES.edgeSVG present:', typeof window.CV_SHAPES?.edgeSVG === 'function');
console.log('CV_EDGES kinds:', window.CV_EDGES ? window.CV_EDGES.ids() : 'MISSING');
console.log('CV_GLYPHIC.composeRelation present:', typeof window.CV_GLYPHIC?.composeRelation === 'function');

// the REAL rel from face-index.js (colors)
const faceIdx = fs.readFileSync('face-index.js','utf8');
eval(faceIdx);
const rel = window.CV_FACES.colors.rel;
console.log('\nrel from face-index:', JSON.stringify(rel));
const r = window.CV_GLYPHIC.composeRelation(rel, { nodeSize: 22, edgeLength: 26 });
const svgCount = (r.html.match(/<svg/g) || []).length;
const hasArrow = r.html.includes('<polygon');
const hasDash  = r.html.includes('stroke-dasharray');
console.log('\n=== GENERATED relational glyph ===');
console.log('edge resolved:', JSON.stringify(r.edge));
console.log('svg count (2 nodes + 1 edge = 3):', svgCount);
console.log('has arrowhead (polygon):', hasArrow, '| has textured line (dasharray):', hasDash);
console.log('html length:', r.html.length);
console.log('\n--- html (first 400) ---\n', r.html.slice(0, 400));
