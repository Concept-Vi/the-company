// Build-gate for self-coded extensions — AST-checked, not regex (red-team B1).
// Catches what regex missed: dynamic import(), export … from, spaced require(, external-URL literals.
// Two layers: (1) syntax/transpile check (ts.transpileModule), (2) an AST walk that REJECTS:
//   - any import/export whose module specifier isn't 'react' / 'react/…'  (unresolved-module → build break)
//   - any dynamic import(…)                                               (remote-code RCE vector)
//   - any require(…)                                                      (not browser-safe; build break)
//   - any string literal that is an external URL (http(s):// or //)       (exfil / remote fetch)
// Exit 0 = safe to promote; non-zero + stderr = rejected with the reason. Run from canvas/app.
const ts = require('typescript');
const fs = require('fs');

const src = fs.readFileSync(process.argv[2], 'utf8');

// (1) syntax — transpileModule reports parse errors fast (no project/type load)
const out = ts.transpileModule(src, {
  compilerOptions: { jsx: ts.JsxEmit.ReactJSX, module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020 },
  reportDiagnostics: true,
});
const synErrs = (out.diagnostics || []).filter(d => d.category === ts.DiagnosticCategory.Error);
if (synErrs.length) {
  console.error('syntax: ' + synErrs.map(d => ts.flattenDiagnosticMessageText(d.messageText, '\n')).join('\n'));
  process.exit(1);
}

// (2) AST walk — structural denylist
const sf = ts.createSourceFile(process.argv[2], src, ts.ScriptTarget.ES2020, true, ts.ScriptKind.TSX);
const ALLOWED = m => m === 'react' || m.startsWith('react/');
const violations = [];

function isExternalUrl(s) { return /^(https?:)?\/\//i.test(s); }

function walk(node) {
  // static import / export … from '<mod>'
  if ((ts.isImportDeclaration(node) || ts.isExportDeclaration(node)) && node.moduleSpecifier &&
      ts.isStringLiteral(node.moduleSpecifier)) {
    const m = node.moduleSpecifier.text;
    if (!ALLOWED(m)) violations.push(`import/export from '${m}' — only 'react' is allowed`);
  }
  // dynamic import(...)
  if (ts.isCallExpression(node) && node.expression.kind === ts.SyntaxKind.ImportKeyword) {
    violations.push('dynamic import() is not allowed (remote-code vector)');
  }
  // require(...)
  if (ts.isCallExpression(node) && ts.isIdentifier(node.expression) && node.expression.text === 'require') {
    violations.push('require() is not allowed');
  }
  // external-URL string literals (exfil / remote fetch)
  if ((ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node)) && isExternalUrl(node.text)) {
    violations.push(`external URL literal '${node.text}' — extensions may only call same-origin /api/…`);
  }
  ts.forEachChild(node, walk);
}
walk(sf);

if (violations.length) {
  console.error('forbidden: ' + [...new Set(violations)].join('; '));
  process.exit(1);
}
process.exit(0);
