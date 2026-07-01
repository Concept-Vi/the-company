const fs = require('fs'); global.window = global;
const load = p => { eval(fs.readFileSync(p, 'utf8')); };
['assets/icons/cv-icons.js', 'assets/icons/cv-vi-glyph.js', 'assets/icons/cv-shapes.js',
 'assets/icons/cv-edges.js', 'assets/icons/cv-meaning.js', 'assets/icons/cv-glyphics.js'].forEach(load);
const M = window.CV_MEANING;

console.log('=== operators seeded AS DATA (the = ≠ + → ⊂ sign-class) ===');
['equals','not','and','becomes','part-of'].forEach(id => {
  const f = M.field('edge', id);
  console.log('  ' + id.padEnd(9), JSON.stringify({ feeling: f.feeling, symbol: M.activeProfile().bindings.edge[id].symbol }));
});

console.log('\n=== operators transglyph in a relation ===');
const rel = { source:{form:'square',symbol:'color-swatches',fill:'paper'}, target:{form:'circle',symbol:'star',fill:'none'}, edge:{line:'solid', kind:'equals'} };
console.log('  ', window.CV_GLYPHIC.composeRelation(rel).sentence);

console.log('\n=== the AUTHORING API — the language is DATA, written live (G0.2) ===');
console.log('  setField returns the field:', JSON.stringify(M.author.setField('texture','wave','rippling',['undulating','organic'])));
console.log('  field() now sees it:', M.field('texture','wave').feeling);
console.log('  setGloss:', M.author.setGloss('palette','colour set'));
console.log('  removeField:', M.author.removeField('texture','wave'));
try { M.field('texture','wave'); console.log('  XX still there'); } catch(e){ console.log('  ok removed (field now throws)'); }

console.log('\n=== G0.5 — author a BRAND-NEW operator at runtime → the language USES it ===');
M.author.setOperator('contradicts', 'contradicts', ['conflicts with','is at odds with'], '⊥');
const rel2 = { source:{form:'square',symbol:'file',fill:'paper'}, target:{form:'square',symbol:'file',fill:'paper'}, edge:{line:'solid', kind:'contradicts'} };
console.log('  new operator transglyphs:', window.CV_GLYPHIC.composeRelation(rel2).sentence);

console.log('\n=== persistence round-trip (export → load) ===');
const json = M.author.save();
console.log('  profile serializes to JSON:', json.length + ' chars, includes "contradicts":', json.includes('contradicts'));

console.log('\n=== LOUD-FAIL: authoring a field with no feeling throws ===');
try { M.author.setField('texture','bad'); console.log('  XX did not throw'); } catch(e){ console.log('  ok threw:', e.message.slice(0,52)); }
try { M.author.setField('not-a-facet','x','y'); console.log('  XX did not throw'); } catch(e){ console.log('  ok threw:', e.message.slice(0,52)); }
