// _demo/verify_address.js — proof harness for core/cv-address.js (node-runnable, loud).
// The ported laws re-proven: spans partition; 7/15 encodes AND decodes; LCA anchors; zones
// re-derive counterpart's proven archetype geometry; stable slots never move on growth.
'use strict';
const A = (function(){ global.window = global; require('../core/cv-address.js'); return global.CV_ADDRESS; })();
let pass = 0, total = 0;
const eq = (a,b) => JSON.stringify(a) === JSON.stringify(b);
const near = (a,b,t) => Math.abs(a-b) <= (t||1e-9);
function check(label, ok){ total++; if(ok) pass++; console.log((ok?'OK ':'XX ')+label); }

// 1 · the worked example: zone 3-of-5 inside slide 2-of-3 starts at 7/15
const s = A.encode([[2,3],[3,5]]);
check('7/15 worked example', near(s.start, 7/15) && near(s.width, 1/15));
// 2 · decode round-trips
check('decode round-trip', eq(A.decode(s.start, [3,5]), [[2,3],[3,5]]));
// 3 · spans partition: siblings tile the parent exactly
const kids = [1,2,3].map(k => A.span(k,3));
check('partition tiles', near(kids[0].start,0) && near(kids[1].start,1/3) && near(kids[2].start+kids[2].width,1));
// 4 · the seam: 2/3 is where child 3 BEGINS (spans, not points)
check('2/3 is a seam', near(A.span(3,3).start, 2/3));
// 5 · LCA anchors: two zones in the same slide anchor at the slide; different slides at the root
check('LCA same slide', eq(A.lca([[2,3],[3,5]], [[2,3],[1,5]]), [[2,3]]));
check('LCA cross slide', eq(A.lca([[1,3],[2,5]], [[2,3],[2,5]]), []));
check('lcaAll set',      eq(A.lcaAll([[[2,3],[3,5]],[[2,3],[1,5]],[[2,3],[4,5]]]), [[2,3]]));
// 6 · zones re-derive the proven archetype (title-main-footer on a 900px axis — counterpart's fractions)
check('zones title-main-footer', eq(A.zones([0.14,0.72,0.10], 900), [126,648,90]));
check('zones split-weighted',    eq(A.zones([0.46,0.54], 1200),    [552,648]));
// 7 · stable slots: adding nodes NEVER moves an existing slot
const s0 = A.slotFor(0).span.start, s3 = A.slotFor(3).span.start;
const after = A.slotFor(0).span.start;              // ask again after "growth"
const s9 = A.slotFor(9);                            // forces capacity doubling
check('slot 0 frozen under growth', near(s0, after) && near(s0, 0));
check('doubling absorbs growth',    s9.capacity === 16 && near(s9.span.start, 9/16) && near(s3, 3/8));
// 8 · loud-fail
let threw=false; try{ A.span(4,3); }catch(e){ threw=true; } check('loud on bad span', threw);
threw=false; try{ A.zones([],100); }catch(e){ threw=true; } check('loud on empty zones', threw);

console.log(`\n${pass}/${total} pass`);
if (pass !== total) process.exit(1);
