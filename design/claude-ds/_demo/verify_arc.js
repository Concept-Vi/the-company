// _demo/verify_arc.js — proof harness for core/cv-arc.js on the ported seed (node-runnable, loud).
// The ported proof re-run: plan('pitch',16) must re-derive the source deck's exact structure.
'use strict';
global.window = global;
require('../core/cv-arc.js');
const SEED = require('../assets/icons/glyph-arc-seed.json');
const beats = global.CV_ARC.plan('pitch', 16, SEED);
let pass = 0, total = 0;
function check(l, ok){ total++; if(ok) pass++; console.log((ok?'OK ':'XX ')+l); }

const runs = [];
beats.forEach(b => { const last = runs[runs.length-1];
  if (last && last.role === b.role) last.len++; else runs.push({role:b.role, len:1}); });
const DECK = [['open',1],['argue',2],['show',5],['prove',3],['plan',1],['people',3],['close',1]];
check('16 beats', beats.length === 16);
check('run lengths reproduce the deck', JSON.stringify(runs.map(r=>[r.role,r.len])) === JSON.stringify(DECK));
check('immersive bookends', beats[0].archetype === 'immersive' && beats[15].archetype === 'immersive');
let boundary = true;
for (let i=1;i<beats.length;i++)
  if (beats[i].role !== beats[i-1].role && beats[i].archetype === beats[i-1].archetype) boundary = false;
check('archetype changes at role boundaries', boundary);
const mid = beats.slice(1,-1);
check('warmth choreography (bookends>=70, middle<=60)',
  beats[0].dials.warmth >= 70 && beats[15].dials.warmth >= 70 && mid.every(b => b.dials.warmth <= 60));
check('deterministic', JSON.stringify(global.CV_ARC.plan('pitch',16,SEED)) === JSON.stringify(beats));
let threw = false; try { global.CV_ARC.plan('pitch', 99, SEED); } catch(e){ threw = true; }
check('loud on unreachable count', threw);

console.log(`\n${pass}/${total} pass`);
if (pass !== total) process.exit(1);
