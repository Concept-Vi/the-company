// _demo/verify_entry.js — proof harness for index.js, the U4 packaging entry
// (node-runnable, loud). Proves: (a) getDS()/getRegistry() throw LOUDLY when
// the bundle-global / a registry global isn't on `window` yet — never a
// silent undefined; (b) both resolve correctly once the (faked) globals are
// present; (c) getRegistry() rejects unknown ids; (d) listRegistries() never
// throws and reports load state honestly.
//
// index.js is an ES module (`export {}`) — required so a browser
// `<script type="module">` can import it directly (see index.js's header and
// package.json's "_type_field_note" for why package.json has no top-level
// "type" field). This harness therefore uses dynamic import() rather than
// the eval(fs.readFileSync(...)) pattern the other _demo/verify_*.js scripts
// use for plain (non-module) scripts under core/ etc.
'use strict';
const path = require('path');

let pass = 0, total = 0;
function check(label, ok) { total++; if (ok) pass++; console.log((ok ? 'OK ' : 'XX ') + label); }
function threw(fn) { try { fn(); return null; } catch (e) { return e; } }

async function main() {
  global.window = global; // fake a browser window for the node harness

  const indexUrl = 'file://' + path.resolve(__dirname, '../index.js');
  const mod = await import(indexUrl);
  const { getDS, getRegistry, listRegistries, BUNDLE_GLOBAL, REGISTRY_GLOBALS } = mod;

  // 1 · loud-fail: bundle global absent → getDS() throws, never returns undefined
  check('BUNDLE_GLOBAL matches the real bundle namespace',
    BUNDLE_GLOBAL === 'ConceptVDesignSystem_c8f43c');

  let e = threw(() => getDS());
  check('getDS() throws when bundle not loaded', !!e);
  check('getDS() throw message names the missing global', !!e && e.message.includes(BUNDLE_GLOBAL));

  // 2 · loud-fail: registry absent → getRegistry() throws, never returns undefined/null
  e = threw(() => getRegistry('CV_AI'));
  check('getRegistry("CV_AI") throws when not loaded', !!e);
  check('getRegistry throw message names the registry', !!e && e.message.includes('CV_AI'));

  // 3 · loud-fail: unknown registry id → throws with the known-list in the message
  e = threw(() => getRegistry('CV_NOT_A_REAL_REGISTRY'));
  check('getRegistry() throws on unknown id', !!e);
  check('unknown-id throw lists the real registries', !!e && REGISTRY_GLOBALS.every(id => e.message.includes(id)));

  // 4 · listRegistries() never throws, and reports everything unloaded so far
  const before = listRegistries();
  check('listRegistries() returns one entry per REGISTRY_GLOBALS', before.length === REGISTRY_GLOBALS.length);
  check('listRegistries() reports all unloaded before stubbing', before.every(r => r.loaded === false));

  // 5 · stub the bundle global + one registry global — resolution should now succeed
  const fakeBundle = { Button: function FakeButton() {}, RenderType: function FakeRenderType() {} };
  const fakeAI = { execute: () => 'fake-executed', complete: () => 'fake-completed' };
  global.window[BUNDLE_GLOBAL] = fakeBundle;
  global.window.CV_AI = fakeAI;

  const ds = getDS();
  check('getDS() resolves the stubbed bundle once present', ds === fakeBundle);
  check('resolved bundle exposes the expected shape', typeof ds.Button === 'function' && typeof ds.RenderType === 'function');

  const ai = getRegistry('CV_AI');
  check('getRegistry("CV_AI") resolves the stubbed registry once present', ai === fakeAI);
  check('resolved registry is actually callable', ai.execute() === 'fake-executed');

  // 6 · the other registries are still correctly reported unloaded (no cross-talk / no silent success)
  e = threw(() => getRegistry('CV_REGISTRY'));
  check('an UNstubbed registry (CV_REGISTRY) still throws after a sibling was stubbed', !!e);

  const after = listRegistries();
  const aiEntry = after.find(r => r.id === 'CV_AI');
  const regEntry = after.find(r => r.id === 'CV_REGISTRY');
  check('listRegistries() reflects the stub (CV_AI loaded)', !!aiEntry && aiEntry.loaded === true);
  check('listRegistries() reflects the gap (CV_REGISTRY still unloaded)', !!regEntry && regEntry.loaded === false);

  console.log(`\n${pass}/${total} pass`);
  if (pass !== total) process.exit(1);
}

main().catch((err) => {
  console.error('HARNESS ERROR:', err);
  process.exit(1);
});
