// verify_g2_4.js — G2.4 CONDITIONALS + NEGATION in the read-out, verified BY RUNNING
// the real engine (not by reading code). Bar (CRITERIA G2.4 + LAWS):
//   (a) NEGATION reads with not/never — the 'not' operator (negates:true) AND an explicit
//       negate:true marker both negate; the relation word SURVIVES ("is NOT the face of").
//   (b) CONDITIONAL reads "if … then …" via CV_COND (reused, not reinvented).
//   (c) BOTH read-outs (readGraph AND describeRelation) carry both features.
//   (d) LOUD-FAIL still holds under the new branches (present-unknown line/kind/lineColor
//       on a negated/conditional edge THROWS); absent contributes nothing.
const fs = require('fs'); global.window = global;
const load = p => { eval(fs.readFileSync(p, 'utf8')); };
['assets/icons/cv-icons.js','assets/icons/cv-vi-glyph.js','assets/icons/cv-shapes.js',
 'assets/icons/cv-edges.js','assets/icons/cv-meaning.js','assets/icons/cv-glyphics.js',
 'app/registry/conditions.js'].forEach(load);
const M = window.CV_MEANING, G = window.CV_GLYPHIC, C = window.CV_COND;
let pass = 0, fail = 0;
const ok = (label, cond, extra) => { if (cond) { pass++; console.log('  ✓', label, extra ? '— ' + extra : ''); } else { fail++; console.log('  ✗ FAIL:', label, extra ? '— ' + extra : ''); } };
const threw = (label, fn) => { try { fn(); fail++; console.log('  ✗ DID NOT THROW:', label); } catch (e) { pass++; console.log('  ✓ threw:', label, '—', e.message.slice(0, 56)); } };

console.log('=== (pre) CV_COND loaded into the harness (required for conditionals) ===');
ok('window.CV_COND.normalize is available', !!(C && C.normalize));
ok("the 'not' operator carries negates:true (single home of negation)", M.field('edge','not').negates === true);

console.log('\n=== (a) NEGATION — describeRelation ===');
const baseSrc = { form:'square', symbol:'file', fill:'paper' };
const baseTgt = { form:'octagon', symbol:'browser', fill:'wash' };
// explicit marker on a real relation kind → the relation word SURVIVES.
const negFace = M.describeRelation({ source: baseSrc, edge:{ line:'solid', kind:'face', negate:true }, target: baseTgt });
ok('negate marker reads "is not" AND keeps the relation word "the face of"',
   /is not the face of/.test(negFace.sentence), negFace.sentence);
ok('describeRelation flags edge.negated', negFace.edge.negated === true);
// the 'not' operator itself (negates:true) — standalone negation, no surviving relation word.
const negOp = M.describeRelation({ source: baseSrc, edge:{ line:'solid', kind:'not' }, target: baseTgt });
ok("the 'not' operator reads single negation (no double 'not'; detected via .negates)",
   /\bis not\b/.test(negOp.sentence) && !/not not/.test(negOp.sentence), negOp.sentence);
// a positive control: without negation the same edge stays positive.
const posFace = M.describeRelation({ source: baseSrc, edge:{ line:'solid', kind:'face' }, target: baseTgt });
ok('without negation the clause stays positive ("is the face of", no "not")',
   /is the face of/.test(posFace.sentence) && !/not/.test(posFace.sentence), posFace.sentence);
// dashed mood negates as "could not be"
const negDashed = M.describeRelation({ source: baseSrc, edge:{ line:'dashed', kind:'face', negate:true }, target: baseTgt });
ok('dashed (could) negates as "could not be"', /could not be the face of/.test(negDashed.sentence), negDashed.sentence);

console.log('\n=== (a) NEGATION — readGraph (the same shared helper) ===');
const graphNeg = { nodes:[ Object.assign({id:'a'}, baseSrc), Object.assign({id:'b'}, baseTgt) ],
                   edges:[ { from:'a', to:'b', line:'solid', kind:'face', negate:true } ] };
const rgNeg = M.readGraph(graphNeg);
ok('readGraph negates with the relation word surviving', /is not the face of/.test(rgNeg.sentence), rgNeg.sentence);
const graphNegOp = { nodes:[ Object.assign({id:'a'}, baseSrc), Object.assign({id:'b'}, baseTgt) ],
                     edges:[ { from:'a', to:'b', line:'solid', kind:'not' } ] };
const rgNegOp = M.readGraph(graphNegOp);
ok("readGraph reads the 'not' operator as single negation (no double 'not')", /\bis not\b/.test(rgNegOp.sentence) && !/not not/.test(rgNegOp.sentence), rgNegOp.sentence);

console.log('\n=== (b) CONDITIONAL — describeRelation reads "if … then …" (via CV_COND) ===');
const condRel = M.describeRelation({ source: baseSrc, edge:{ line:'solid', kind:'becomes', conditions:'status == approved' }, target: baseTgt });
ok('conditional reads "if … then …"', /^if .+ then .+/.test(condRel.sentence), condRel.sentence);
ok('the antecedent verbalizes the condition field/op/value', /status is approved/.test(condRel.sentence), condRel.sentence);
ok('describeRelation flags edge.conditional', condRel.edge.conditional === true);
// a boolean-tree condition (CV_COND.normalize handles all/any/not) verbalizes too.
const condTree = M.describeRelation({ source: baseSrc, edge:{ line:'solid', kind:'becomes', conditions:'status == approved and finance != pending' }, target: baseTgt });
ok('an "and" condition tree reads as a joined antecedent', /if status is approved and finance is not pending then/.test(condTree.sentence), condTree.sentence);

console.log('\n=== (b) CONDITIONAL — readGraph reads "if … then …" ===');
const graphCond = { nodes:[ Object.assign({id:'a'}, baseSrc), Object.assign({id:'b'}, baseTgt) ],
                    edges:[ { from:'a', to:'b', line:'solid', kind:'becomes', conditions:'status == approved' } ] };
const rgCond = M.readGraph(graphCond);
ok('readGraph wraps the clause as "if … then …"', /if status is approved then/i.test(rgCond.sentence), rgCond.sentence);

console.log('\n=== (a+b) NEGATION + CONDITIONAL together ===');
const both = M.describeRelation({ source: baseSrc, edge:{ line:'solid', kind:'face', negate:true, conditions:'visible == false' }, target: baseTgt });
ok('a negated conditional reads "if … then … is not …"', /^if .+ then .+ is not the face of/.test(both.sentence), both.sentence);

console.log('\n=== (c) composeRelation forwards negate + conditions to the read-out ===');
const compNeg = G.composeRelation({ source: baseSrc, edge:{ line:'solid', kind:'face', negate:true }, target: baseTgt });
ok('composeRelation read-out negates (negate forwarded through EDGES.resolve drop)', /is not the face of/.test(compNeg.sentence), compNeg.sentence);
const compCond = G.composeRelation({ source: baseSrc, edge:{ line:'solid', kind:'becomes', conditions:'status == approved' }, target: baseTgt });
ok('composeRelation read-out reads conditional', /if status is approved then/.test(compCond.sentence), compCond.sentence);

console.log('\n=== (d) LOUD-FAIL still holds under the new branches ===');
// present-unknown line on a NEGATED edge → throws (field('line',…) is still the gate).
threw('present-unknown line, negated (describeRelation)', () => M.describeRelation({ source: baseSrc, edge:{ line:'zigzag', kind:'face', negate:true }, target: baseTgt }));
// present-unknown kind on a negated edge → isNegated resolves field('edge',kind) which throws.
threw('present-unknown kind, negate marker (describeRelation)', () => M.describeRelation({ source: baseSrc, edge:{ line:'solid', kind:'flibber', negate:true }, target: baseTgt }));
// present-unknown lineColor on a conditional edge → throws.
threw('present-unknown lineColor, conditional (describeRelation)', () => M.describeRelation({ source: baseSrc, edge:{ line:'solid', kind:'becomes', lineColor:'ultraviolet', conditions:'x == 1' }, target: baseTgt }));
// present-unknown kind on a conditional edge in readGraph → throws.
threw('present-unknown kind, conditional (readGraph)', () => M.readGraph({ nodes:[ Object.assign({id:'a'}, baseSrc), Object.assign({id:'b'}, baseTgt) ], edges:[ { from:'a', to:'b', line:'solid', kind:'flibber', conditions:'x == 1' } ] }));
// ABSENT negate/conditions contribute nothing — no throw, plain positive reading.
ok('ABSENT negate + conditions → plain positive clause (no throw, no "if"/"not")',
   !/not|^if/.test(posFace.sentence) && !!posFace.sentence, posFace.sentence);

console.log('\n----------------------------------------');
console.log('G2.4 verify:  ' + pass + ' passed, ' + fail + ' failed');
if (fail) process.exit(1);
