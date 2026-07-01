// verify_g10.js — G10 MULTI-TARGET transglyphing, verified BY RUNNING the real engine
// (node window-shim), NOT by reading code. The bar (CRITERIA G10 + LAWS):
//   (a) readGraph(graph,{target:'english'}) and readGraph(graph,{target:'triples'}) run on the
//       SAME graphs and each produce a real projection — proving the meaning is the GRAPH and
//       English is ONE projection (the read-out generalises past English).
//   (b) the 'triples' target is STRUCTURAL — it emits node ids + edge kinds + (and …)/(if …)/
//       (not …), and NEVER an English noun phrase (no referent() leak).
//   (c) coverage parity: relation, coordination, subordination, negation, conditional all
//       project in BOTH targets.
//   (d) LOUD-FAIL: an unknown target THROWS; absent target → the 'english' default (existing
//       callers pass none and must keep working — the colorForValue absent-vs-present pattern).
//   (e) English is unchanged (this file does NOT re-prove that — verify_readgraph.js does; here
//       we only assert the english target still equals the known sentences).
const fs = require('fs'); global.window = global;
const load = p => { eval(fs.readFileSync(p, 'utf8')); };
['assets/icons/cv-icons.js','assets/icons/cv-vi-glyph.js','assets/icons/cv-shapes.js',
 'assets/icons/cv-edges.js','assets/icons/cv-meaning.js','assets/icons/cv-glyphics.js',
 'app/registry/conditions.js'].forEach(load);   // conditions.js → window.CV_COND (G2.4 + the if/then triple)
const M = window.CV_MEANING;
// the SAME live-authoring glosses the other read-out harnesses use — so English reads as words.
[['browser','web page'],['file','file'],['folder','project'],['gear','engine'],['person','person'],
 ['team','team'],['house','home']].forEach(g => M.author.setGloss(g[0], g[1]));

let pass = 0, fail = 0;
function ok(cond, label, detail) { console.log((cond?'  ✓ ':'  ✗ ')+label+(detail?'  '+detail:'')); cond?pass++:fail++; }

// ---- the graphs (the SAME object handed to BOTH targets) ----
const G = {
  single:  { nodes:[{id:'h',form:'square',symbol:'house',fill:'paper'}], edges:[] },
  relation:{ nodes:[{id:'pg',form:'square',symbol:'browser',fill:'wash'},{id:'h',form:'square',symbol:'house',fill:'paper'}],
             edges:[{from:'pg',to:'h',line:'solid',kind:'face'}] },
  branch:  { nodes:[{id:'p',form:'square',symbol:'person',fill:'paper'},{id:'t',form:'circle',symbol:'team',fill:'none'},{id:'pr',form:'circle',symbol:'folder',fill:'none'}],
             edges:[{from:'p',to:'t',line:'solid',kind:'part-of'},{from:'p',to:'pr',line:'solid',kind:'part-of'}] },
  chain:   { nodes:[{id:'f',form:'square',symbol:'file',fill:'paper'},{id:'pr',form:'circle',symbol:'folder',fill:'none'},{id:'e',form:'circle',symbol:'gear',fill:'none'}],
             edges:[{from:'f',to:'pr',line:'solid',kind:'part-of'},{from:'pr',to:'e',line:'solid',kind:'part-of'}] },
  negation:{ nodes:[{id:'f',form:'square',symbol:'file',fill:'paper'},{id:'p',form:'square',symbol:'person',fill:'paper'}],
             edges:[{from:'f',to:'p',line:'solid',kind:'face',negate:true}] },
  // the OTHER negation form — the kind IS the negation operator (its field carries .negates).
  // English suppresses the relation word here ("is not", not "is not not"); triples must NOT
  // double-wrap ("(not (face …))", not "(not (not face …))").
  notOp:   { nodes:[{id:'f',form:'square',symbol:'file',fill:'paper'},{id:'p',form:'square',symbol:'person',fill:'paper'}],
             edges:[{from:'f',to:'p',line:'solid',kind:'not'}] },
  conditional:{ nodes:[{id:'pg',form:'square',symbol:'browser',fill:'wash'},{id:'h',form:'square',symbol:'house',fill:'paper'}],
                edges:[{from:'pg',to:'h',line:'solid',kind:'face',conditions:{field:'status',op:'==',value:'approved'}}] }
};

function read(g, target) { return M.readGraph(g, target ? {target} : undefined); }

console.log('=== G10 · BOTH targets on the SAME graph (meaning is the graph; English is one projection) ===\n');
Object.keys(G).forEach(name => {
  const en = read(G[name], 'english');
  const tr = read(G[name], 'triples');
  console.log(name+':');
  console.log('   english : '+en.sentence+'   ['+en.kind+']');
  console.log('   triples : '+tr.sentence+'   ['+tr.kind+']');
  ok(en.target === 'english' && typeof en.sentence === 'string' && en.sentence.length, name+' · english projects', '');
  ok(tr.target === 'triples' && typeof tr.sentence === 'string' && tr.sentence.length, name+' · triples projects', '');
});

console.log('\n=== Triples is STRUCTURAL — node ids + edge kinds, NEVER English words (no referent leak) ===');
{
  const tr = read(G.relation, 'triples').sentence;
  ok(tr === '(face pg h)', 'relation → (face pg h)', '"'+tr+'"');
  ok(!/web page|home|the |this /.test(tr), 'relation triples carries NO English noun phrase', '"'+tr+'"');
}
{
  const tr = read(G.branch, 'triples').sentence;
  ok(/^\(and /.test(tr) && /\(part-of p t\)/.test(tr) && /\(part-of p pr\)/.test(tr),
     'branch → coordination (and (part-of p t) (part-of p pr))', '"'+tr+'"');
}
{
  const tr = read(G.chain, 'triples').sentence;
  ok(/\(part-of pr e\)/.test(tr) && /\(part-of f /.test(tr),
     'chain → subordination nests (part-of pr e) inside f\'s relation', '"'+tr+'"');
}
{
  const tr = read(G.negation, 'triples').sentence;
  ok(/^\(not /.test(tr) && /\(face f p\)/.test(tr), 'negation → (not (face f p))', '"'+tr+'"');
}
{
  const tr = read(G.notOp, 'triples').sentence;
  ok(tr === '(not (rel f p))', 'kind:not → (not (rel f p)) — wrapped ONCE, no double-negate', '"'+tr+'"');
}
{
  const tr = read(G.conditional, 'triples').sentence;
  ok(tr === '(if (== status approved) (face pg h))',
     'conditional → (if (== status approved) (face pg h)) — wrapped exactly ONCE', '"'+tr+'"');
}

console.log('\n=== English target STILL equals the known sentences (the G4.5-DONE projection unchanged) ===');
ok(read(G.single,'english').sentence === 'This home.', 'single node → "This home."', read(G.single,'english').sentence);
ok(read(G.relation,'english').sentence === 'This web page is the face of this home.', 'relation → known sentence', read(G.relation,'english').sentence);
ok(read(G.branch,'english').sentence === 'This person is part of the team, and is part of the project.', 'branch → known sentence', read(G.branch,'english').sentence);

console.log('\n=== ABSENT target → english default (existing callers pass no opts) ===');
ok(read(G.relation, null).target === 'english', 'no opts → defaults to english', '');
ok(M.readGraph(G.relation, {}).target === 'english', 'empty opts → defaults to english', '');
ok(M.readGraph(G.relation, {focus:'pg'}).target === 'english', 'opts without target → english', '');

console.log('\n=== LOUD-FAIL — a PRESENT-but-unknown target THROWS (no silent fallback) ===');
try { M.readGraph(G.relation, {target:'klingon'}); ok(false, 'unknown target did NOT throw', ''); }
catch(e){ ok(/unknown target "klingon"/.test(e.message), 'unknown target throws, naming it', e.message.split(' (')[0]); }
try { M.readGraph(G.relation, {target:'code'}); ok(false, 'unbuilt target "code" did NOT throw', ''); }
catch(e){ ok(/unknown target "code"/.test(e.message), 'unbuilt target "code" throws (not silently empty)', ''); }

console.log('\n=== LOUD-FAIL holds inside triples too — a present-unknown edge kind/line THROWS ===');
try { M.readGraph({ nodes:[{id:'a',form:'square',symbol:'house',fill:'paper'},{id:'b',form:'square',symbol:'house',fill:'paper'}],
        edges:[{from:'a',to:'b',line:'solid',kind:'NOPE'}] }, {target:'triples'});
      ok(false, 'unknown kind did NOT throw in triples', ''); }
catch(e){ ok(/NOPE|unknown/i.test(e.message), 'present-unknown edge kind throws in triples target', e.message.split(' (')[0]); }

console.log('\n===== '+pass+' passed, '+fail+' failed =====');
process.exit(fail ? 1 : 0);
