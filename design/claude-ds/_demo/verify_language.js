const fs=require('fs'); global.window=global;
const load=p=>{ eval(fs.readFileSync(p,'utf8')); };
['assets/icons/cv-icons.js','assets/icons/cv-vi-glyph.js','assets/icons/cv-shapes.js','assets/icons/cv-edges.js','assets/icons/cv-meaning.js','assets/icons/cv-glyphics.js'].forEach(load);

console.log('=== a single glyphic SAYS ITSELF (the screenshot mark) ===');
const r = window.CV_GLYPHIC.describe({ form:'octagon', symbol:'house', fill:'wash', motion:'none' });
console.log('  →', r.sentence);
console.log('  meaning-set types:', r.meaningSet.map(m=>m.type).join(' · '));

console.log('\n=== the SAME mark, different fill values → different mode (combinatorial) ===');
['none','paper','wash'].forEach(fl=>{
  console.log('  fill='+fl+':', window.CV_GLYPHIC.describe({form:'octagon',symbol:'house',fill:fl,motion:'none'}).sentence);
});

console.log('\n=== a RELATION says itself (2 nodes + edge) — value of each changes meaning ===');
const base = { source:{form:'square',symbol:'house',fill:'paper'}, target:{form:'octagon',symbol:'browser',fill:'wash'} };
console.log('  dashed/face:', window.CV_GLYPHIC.composeRelation(Object.assign({},base,{edge:{line:'dashed',kind:'face'}})).sentence);
console.log('  solid/face: ', window.CV_GLYPHIC.composeRelation(Object.assign({},base,{edge:{line:'solid',kind:'face'}})).sentence);

console.log('\n=== LOUD-FAIL proof (no silent defaults) ===');
const mustThrow=(label,fn)=>{ try{ fn(); console.log('  ✗ DID NOT THROW:',label);}catch(e){ console.log('  ✓ threw:',label,'—',e.message.slice(0,60));} };
mustThrow('unknown form', ()=>window.CV_MEANING.describe({form:'pentagram',symbol:'house'}));
mustThrow('unknown fill', ()=>window.CV_MEANING.describe({form:'octagon',fill:'rainbow'}));
mustThrow('unknown symbol', ()=>window.CV_MEANING.describe({form:'octagon',symbol:'unicorn',fill:'paper'}));
mustThrow('unknown texture', ()=>window.CV_MEANING.describe({form:'octagon',fill:'paper',texture:'plaid'}));
mustThrow('relation w/o edge.line', ()=>window.CV_MEANING.describeRelation({source:{form:'square'},target:{form:'octagon'}}));
mustThrow('unknown edge line', ()=>window.CV_GLYPHIC.composeRelation({source:{form:'square',fill:'paper'},target:{form:'octagon',fill:'paper'},edge:{line:'zigzag'}}));

console.log('\n=== edges folded into the meaning system (line-types incl right-angled/curved/free) ===');
console.log('  line facet values:', Object.keys(window.CV_MEANING.valuesFor('line')).join(' · '));
console.log('  field(line,right-angled):', JSON.stringify(window.CV_MEANING.field('line','right-angled')));
