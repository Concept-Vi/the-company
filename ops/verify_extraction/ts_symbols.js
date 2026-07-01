// ts_symbols.js — ground-truth symbol extractor for JS/JSX/TS/TSX via the real TypeScript compiler API.
// Part of the repeatable extraction-verifier (see verify.py). Reads newline-separated file paths on stdin,
// emits one JSON line per file: {file, names:[...]}. `names` = declared functions / arrow-or-fn-expr consts /
// methods / classes — the symbols the deterministic ledger extractor is expected to capture, so verify.py can
// set-diff them against ledger.symbol and find genuine misses (as opposed to the audit-model's noise).
//
// Usage:  node ts_symbols.js <path-to-node_modules-containing-typescript>  < filelist
// The typescript install is only used as a parser; any project's node_modules/typescript works for any file.
const ts = require(process.argv[2] + '/typescript');
const fs = require('fs');
const files = fs.readFileSync(0, 'utf8').trim().split('\n').filter(Boolean);
const KIND = { '.ts': ts.ScriptKind.TS, '.tsx': ts.ScriptKind.TSX, '.js': ts.ScriptKind.JS, '.jsx': ts.ScriptKind.JSX };
for (const file of files) {
  let text;
  try { text = fs.readFileSync(file, 'utf8'); } catch (e) { console.log(JSON.stringify({ file, names: [], err: 'read' })); continue; }
  const ext = file.slice(file.lastIndexOf('.'));
  const sf = ts.createSourceFile(file, text, ts.ScriptTarget.Latest, true, KIND[ext] || ts.ScriptKind.TSX);
  const names = [];
  (function walk(n) {
    if (ts.isFunctionDeclaration(n) && n.name) names.push(n.name.text);
    else if (ts.isClassDeclaration(n) && n.name) names.push(n.name.text);
    else if (ts.isMethodDeclaration(n) && n.name) names.push(n.name.getText(sf));
    else if (ts.isVariableDeclaration(n) && n.name && n.initializer &&
             (ts.isArrowFunction(n.initializer) || ts.isFunctionExpression(n.initializer)))
      names.push(n.name.getText(sf));
    ts.forEachChild(n, walk);
  })(sf);
  console.log(JSON.stringify({ file, names }));
}
