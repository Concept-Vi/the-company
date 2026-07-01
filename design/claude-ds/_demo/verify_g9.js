/**
 * G9 — THE REVERSE: parse(text → glyphgraph). Verified BY RUNNING (node window-shim),
 * mirroring verify_readgraph.js. The contract is the TEXT round-trip (forward is lossy,
 * so graph==graph' is NOT recoverable): readGraph(parse(S)).sentence ≈ S.
 */
const fs = require('fs'); global.window = global;
['cv-icons','cv-vi-glyph','cv-shapes','cv-edges','cv-meaning','cv-glyphics'].forEach(f => eval(fs.readFileSync('assets/icons/'+f+'.js','utf8')));
const M = window.CV_MEANING;
// the SAME live-authoring path verify_readgraph.js uses — glosses so words read as words.
[['browser','web page'],['file','file'],['folder','project'],['gear','engine'],['person','person'],['team','team'],['color-swatches','colour set'],['star','palette']].forEach(g => M.author.setGloss(g[0], g[1]));

let pass = 0, fail = 0;
function norm(s){ return s.toLowerCase().replace(/[.,]/g,'').replace(/\s+/g,' ').trim(); }
function check(label, sentence){
  let out;
  try { out = M.parse(sentence); }
  catch(e){ console.log('  ✗ '+label+'  PARSE THREW: '+e.message); fail++; return; }
  let back;
  try { back = M.readGraph(out.graph).sentence; }
  catch(e){ console.log('  ✗ '+label+'  readGraph THREW: '+e.message); fail++; return; }
  const ok = norm(back) === norm(sentence);
  console.log((ok?'  ✓ ':'  ✗ ')+label);
  console.log('      in : '+sentence);
  console.log('      out: '+back);
  console.log('      graph: '+JSON.stringify(out.graph));
  if (out.notes && out.notes.length) console.log('      notes: '+out.notes.join(' | '));
  ok ? pass++ : fail++;
}

console.log('=== ROUND-TRIP: readGraph(parse(S)).sentence ≈ S ===');
console.log('(the EXACT sentences readGraph emits in verify_readgraph.js are the parser target)\n');

// These are the literal outputs of verify_readgraph.js examples 1,2,4,5 (re-derived live below
// so the target can never drift from what readGraph actually says today).
const ex1 = M.readGraph({ nodes:[{id:'a',form:'square',symbol:'house',fill:'paper'}], edges:[] }).sentence;
console.log('1 · single node (a noun phrase):');           check('single-node', ex1);

const ex2 = M.readGraph({ nodes:[{id:'pg',form:'square',symbol:'browser',fill:'wash'},{id:'h',form:'square',symbol:'house',fill:'paper'}],
  edges:[{from:'pg',to:'h',line:'solid',kind:'face'}] }).sentence;
console.log('\n2 · a relation (page is the face of the home):'); check('relation-face', ex2);

const ex4 = M.readGraph({ nodes:[{id:'p',form:'square',symbol:'person',fill:'paper'},{id:'t',form:'circle',symbol:'team',fill:'none'},{id:'pr',form:'circle',symbol:'folder',fill:'none'}],
  edges:[{from:'p',to:'t',line:'solid',kind:'part-of'},{from:'p',to:'pr',line:'solid',kind:'part-of'}] }).sentence;
console.log('\n4 · a branch (coordination — "A and B"):');   check('coordination', ex4);

console.log('\n=== HAND-WRITTEN SENTENCES (parse a sentence a person would type) ===');
check('typed-relation', 'this web page is the face of this home');
check('typed-concept',  'the engine');

console.log('\n=== G0.5 — author a NEW word, parse picks it up for free ===');
M.author.setGloss('lock', 'safety door');
const g05 = M.parse('this safety door is part of the project');
console.log('  parsed "this safety door is part of the project" →', JSON.stringify(g05.graph));
const sym = g05.graph.nodes.find(n=>n.symbol==='lock');
if (sym) { console.log('  ✓ a just-authored gloss ("safety door"→lock) parsed without any code change'); pass++; }
else { console.log('  ✗ just-authored gloss did NOT parse'); fail++; }

console.log('\n=== LOUD-FAIL — an unknown content token must THROW (no fabricated node) ===');
try { M.parse('this wizard is the face of this home'); console.log('  ✗ did NOT throw on unknown token "wizard"'); fail++; }
catch(e){ if (/wizard/.test(e.message)) { console.log('  ✓ threw, naming the token: '+e.message.split(' — ')[0]); pass++; } else { console.log('  ✗ threw but did not name the token: '+e.message); fail++; } }

console.log('\n=== STARTER GAPS loud-fail with the HONEST reason (never a misattributed token) ===');
try {
  M.parse('this file is part of the project, which is part of the engine');
  console.log('  ✗ subordination did NOT throw'); fail++;
} catch(e){
  if (/subordination/i.test(e.message) && /STARTER GAP/.test(e.message)) {
    console.log('  ✓ subordination throws naming the real cause: '+e.message.split('—')[0].trim()); pass++;
  } else { console.log('  ✗ threw but misattributed the cause: '+e.message); fail++; }
}
try {
  M.parse('if this offer is approved then this file becomes the project');
  console.log('  ✗ conditional did NOT throw'); fail++;
} catch(e){
  if (/conditional/i.test(e.message) && /STARTER GAP/.test(e.message)) {
    console.log('  ✓ conditional throws naming the real cause'); pass++;
  } else { console.log('  ✗ threw but misattributed: '+e.message); fail++; }
}

console.log('\n===== '+pass+' passed, '+fail+' failed =====');
process.exit(fail ? 1 : 0);
