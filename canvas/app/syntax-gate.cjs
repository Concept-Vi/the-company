// Build-gate for self-coded extensions: a FAST syntax/transpile check (ts.transpileModule —
// no project/type load, unlike full tsc which is too slow on tldraw). Catches what actually
// breaks the Vite build (syntax/parse errors); type errors don't break esbuild's transpile.
// Exit 0 = safe to promote; non-zero + stderr = rejected with the error. Run from canvas/app.
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const out = ts.transpileModule(src, {
  compilerOptions: { jsx: ts.JsxEmit.ReactJSX, module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020 },
  reportDiagnostics: true,
});
const errs = (out.diagnostics || []).filter(d => d.category === ts.DiagnosticCategory.Error);
if (errs.length) {
  console.error(errs.map(d => ts.flattenDiagnosticMessageText(d.messageText, '\n')).join('\n'));
  process.exit(1);
}
process.exit(0);
