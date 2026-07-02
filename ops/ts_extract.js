// ts_extract.js — real-AST extractor for JS/JSX/TS/TSX via the TypeScript compiler API.
// The reliable frontend extractor for the ledger (tree-sitter's py3.14 binding is broken here).
// Reads SOURCE on stdin; argv[2]=filename (for ScriptKind), argv[3]=node_modules dir containing `typescript`.
// Emits one JSON object: {symbols:[{name,kind,line,exported,async}], imports:[{target,relative,line}],
// calls:[{name,line}], endpoints:[{method,url,line}], events:[...]}. Walks the AST for every function/
// component/class/method/interface/type/enum/module-constant + object-literal methods + window.* assigns
// (the expression-embedded definitions regex was structurally blind to) + imports + the JS call-graph.
const ts = require(process.argv[3] + '/typescript');
const fs = require('fs');
const file = process.argv[2] || 'anon.tsx';
const text = fs.readFileSync(0, 'utf8');
const isTsx = file.endsWith('.tsx') || file.endsWith('.jsx');
const KIND = file.endsWith('.tsx') || file.endsWith('.jsx') ? ts.ScriptKind.TSX
          : file.endsWith('.ts') || file.endsWith('.mts') || file.endsWith('.cts') ? ts.ScriptKind.TS
          : ts.ScriptKind.JS;
const sf = ts.createSourceFile(file, text, ts.ScriptTarget.Latest, true, KIND);
const symbols = [], imports = [], calls = [], endpoints = [], events = [], uiBinds = [];
const line = n => sf.getLineAndCharacterOfPosition(n.getStart(sf)).line + 1;
const ENDPOINT_METHODS = new Set(['get', 'post', 'put', 'delete', 'patch']);

// UI-BINDING capture — the ui://→code join's DERIVED half (universal mechanism, not curated data):
// any FE file that carries a ui:// address is bound to it. Three deterministic sources:
//   attr     — <div data-ui-ref="ui://…">        (the canvas convention)
//   literal  — 'ui://…' string literal            (the surface/pointables stamp catalog)
//   template — `ui://…/${x}` template family      (dynamic addresses; recorded as prefix + '*')
function addUiBind(addr, src, node) {
  if (addr && addr.startsWith('ui://') && addr.length > 5) uiBinds.push({ addr, src, line: line(node) });
}

function isFn(n) { return n && (ts.isArrowFunction(n) || ts.isFunctionExpression(n)); }
function addSym(name, kind, node, exported = false, isAsync = false) {
  if (!name) return;
  if (isTsx && /^[A-Z]/.test(name) && (kind === 'function' || kind === 'method')) kind = 'component';
  symbols.push({ name, kind, line: line(node), exported, async: isAsync });
}
function isExported(node) {
  const mods = ts.canHaveModifiers(node) ? ts.getModifiers(node) : undefined;
  return !!(mods && mods.some(m => m.kind === ts.SyntaxKind.ExportKeyword));
}
function calleeName(expr) {
  if (ts.isIdentifier(expr)) return expr.text;
  if (ts.isPropertyAccessExpression(expr)) return expr.name.text;
  return null;
}
function firstStringArg(callNode) {
  const a = callNode.arguments && callNode.arguments[0];
  if (a && (ts.isStringLiteral(a) || ts.isNoSubstitutionTemplateLiteral(a))) return a.text;
  return null;
}

function walk(node, inFunc) {
  // ui:// bindings (see addUiBind) — attr wins over literal for the same address occurrence
  if (ts.isJsxAttribute(node) && node.name && node.name.getText(sf) === 'data-ui-ref' && node.initializer) {
    if (ts.isStringLiteral(node.initializer)) addUiBind(node.initializer.text, 'attr', node);
    else if (ts.isJsxExpression(node.initializer) && node.initializer.expression) {
      const e = node.initializer.expression;
      if (ts.isStringLiteral(e) || ts.isNoSubstitutionTemplateLiteral(e)) addUiBind(e.text, 'attr', node);
      else if (ts.isTemplateExpression(e) && e.head.text.startsWith('ui://')) addUiBind(e.head.text + '*', 'template', node);
    }
  } else if ((ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node)) && node.text.startsWith('ui://')) {
    addUiBind(node.text, 'literal', node);
  } else if (ts.isTemplateExpression(node) && node.head.text.startsWith('ui://')) {
    addUiBind(node.head.text + '*', 'template', node);
  }
  if (ts.isFunctionDeclaration(node) && node.name) {
    addSym(node.name.text, 'function', node, isExported(node),
           !!(ts.getModifiers(node) || []).some?.(m => m.kind === ts.SyntaxKind.AsyncKeyword));
    ts.forEachChild(node, c => walk(c, true)); return;
  }
  if (ts.isClassDeclaration(node) && node.name) {
    addSym(node.name.text, 'class', node, isExported(node));
    ts.forEachChild(node, c => walk(c, inFunc)); return;
  }
  if (ts.isMethodDeclaration(node) && node.name) { addSym(node.name.getText(sf), 'method', node); ts.forEachChild(node, c => walk(c, true)); return; }
  if (ts.isInterfaceDeclaration(node)) { addSym(node.name.text, 'interface', node, isExported(node)); return; }
  if (ts.isTypeAliasDeclaration(node)) { addSym(node.name.text, 'type', node, isExported(node)); return; }
  if (ts.isEnumDeclaration(node)) { addSym(node.name.text, 'enum', node, isExported(node)); return; }
  if (ts.isVariableStatement(node)) {
    const exp = isExported(node);
    for (const d of node.declarationList.declarations) {
      const nm = d.name.getText(sf);
      const wrapped = d.initializer && ts.isCallExpression(d.initializer) && d.initializer.arguments.some(isFn);
      if (isFn(d.initializer) || wrapped) addSym(nm, 'function', d, exp);
      else if (!inFunc && /^[A-Za-z]/.test(nm)) addSym(nm, 'constant', d, exp);
      if (d.initializer) walk(d.initializer, inFunc);
    }
    return;
  }
  if (ts.isPropertyAssignment(node) && isFn(node.initializer)) {          // { open: () => {} }
    addSym(node.name.getText(sf).replace(/['"`]/g, ''), 'method', node);
  }
  if (ts.isBinaryExpression(node) && node.operatorToken.kind === ts.SyntaxKind.EqualsToken && isFn(node.right)) {
    const nm = (ts.isPropertyAccessExpression(node.left) ? node.left.name.text : node.left.getText(sf)).split('.').pop();
    addSym(nm, 'function', node);                                          // window.X = () => {}
  }
  if (ts.isImportDeclaration(node) && node.moduleSpecifier && ts.isStringLiteral(node.moduleSpecifier)) {
    const t = node.moduleSpecifier.text;
    imports.push({ target: t, relative: t.startsWith('.'), line: line(node) });
  }
  if (ts.isCallExpression(node)) {
    const nm = calleeName(node.expression);
    const s = firstStringArg(node);
    if ((nm === 'require' || node.expression.kind === ts.SyntaxKind.ImportKeyword) && s) imports.push({ target: s, relative: s.startsWith('.'), line: line(node) });
    else if (nm === 'fetch' && s) endpoints.push({ method: 'FETCH', url: s, line: line(node) });
    else if (nm && ENDPOINT_METHODS.has(nm) && s && (s.includes('/') || s.startsWith('http'))) endpoints.push({ method: nm.toUpperCase(), url: s, line: line(node) });
    else if (['addEventListener', 'dispatchEvent', 'CustomEvent', 'on', 'emit'].includes(nm) && s) events.push(s);
    else if (nm) calls.push({ name: nm, line: line(node) });
  }
  ts.forEachChild(node, c => walk(c, inFunc));
}
try { ts.forEachChild(sf, c => walk(c, false)); }
catch (e) { console.log(JSON.stringify({ error: String(e) })); process.exit(0); }
console.log(JSON.stringify({ symbols, imports, calls, endpoints, events, ui_binds: uiBinds }));
