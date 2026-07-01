const fs = require('fs'); global.window = global;
['cv-icons','cv-vi-glyph','cv-shapes','cv-edges','cv-meaning','cv-glyphics'].forEach(f => eval(fs.readFileSync('assets/icons/'+f+'.js','utf8')));
const M = window.CV_MEANING;
// author a few symbol glosses so the words read as words (this is exactly the live-authoring path)
[['browser','web page'],['file','file'],['folder','project'],['gear','engine'],['person','person'],['team','team'],['color-swatches','colour set'],['star','palette']].forEach(g => M.author.setGloss(g[0], g[1]));

const G = (nodes, edges) => M.readGraph({ nodes, edges }).sentence;

console.log('1 · single node (a noun phrase, not a sentence):');
console.log('   ', G([{id:'a',form:'square',symbol:'house',fill:'paper'}], []));

console.log('2 · a relation (page is the face of the thing):');
console.log('   ', G([{id:'pg',form:'square',symbol:'browser',fill:'wash'},{id:'h',form:'square',symbol:'house',fill:'paper'}],
                     [{from:'pg',to:'h',line:'solid',kind:'face'}]));

console.log('3 · potential (dashed edge + dashed-outline node = the "could-be" question you flagged):');
console.log('   ', G([{id:'pg',form:'square',symbol:'browser',fill:'wash'},{id:'h',form:'square',symbol:'house',outline:'dashed'}],
                     [{from:'pg',to:'h',line:'dashed',kind:'face'}]));

console.log('4 · a branch (coordination — one thing, two relations):');
console.log('   ', G([{id:'p',form:'square',symbol:'person',fill:'paper'},{id:'t',form:'circle',symbol:'team',fill:'none'},{id:'pr',form:'circle',symbol:'folder',fill:'none'}],
                     [{from:'p',to:'t',line:'solid',kind:'part-of'},{from:'p',to:'pr',line:'solid',kind:'part-of'}]));

console.log('5 · a chain (subordination — "which …"):');
console.log('   ', G([{id:'f',form:'square',symbol:'file',fill:'paper'},{id:'pr',form:'circle',symbol:'folder',fill:'none'},{id:'e',form:'circle',symbol:'gear',fill:'none'}],
                     [{from:'f',to:'pr',line:'solid',kind:'part-of'},{from:'pr',to:'e',line:'solid',kind:'part-of'}]));

console.log('6 · circle vs square (the SOFT CELL — kind vs instance — your ear most needed here):');
console.log('    square+house+present →', M.referent({form:'square',symbol:'house',fill:'paper'}));
console.log('    circle+house+concept →', M.referent({form:'circle',symbol:'house',fill:'none'}));

console.log('\n(verb-composition note: noun-ish relations [face/part-of] read clean; verb-ish [navigates/becomes] need mood-folding — flagged)');
