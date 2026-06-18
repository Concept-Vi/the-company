// sync-gallery.mjs — the DOM-MOUNT SEAM's copy-on-build step (runs as predev + prebuild).
//
// The first-slice FACE is DNA's render module (ONE renderer, MANY sources). DNA OWNS it — it lives in
// DNA's repo (counterpart/design/ui/). The surface HOSTS it (so DNA's /api/cognition/corpus fetch is
// same-origin + fork/wildcard get stable element refs). To host without taking custody (no silent
// drift, no stale hand-copy), we COPY DNA's canonical files into public/gallery/ on every dev/build —
// fresh every time, identical in dev and prod, and FAIL LOUD if DNA's source is missing (never serve a
// silently-stale or absent module). DNA edits her source; the next dev/build picks it up. Registry-of-
// truth for the module = DNA's repo, not this copy.
import { existsSync, mkdirSync, copyFileSync, statSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const PUBLIC_GALLERY = join(HERE, '..', 'public', 'gallery')

// DNA's render module is MID-REORG: her repo is moving `ui/` → `surface/runtime/` (DNA's own
// docs/dev/REORGANISATION-PROPOSAL.md, target tree — organisms.js/unit-view.js/phone.css/piece.css all
// land in surface/runtime/). To dissolve the move-RACE — so the reorg can land on ANY beat without a
// paired edit here AND without ever serving a silently-stale copy — we resolve EACH source file across a
// PRIORITISED list of candidate homes and FAIL LOUD if it's in none:
//   1. an explicit DNA_UI_DIR override (a relocated checkout / manual pin) — honoured first of all;
//   2. <repo>/surface/runtime/ — the reorg TARGET, tried before today's home so the instant DNA's move
//      lands we pick up the new canonical home (and never prefer a lingering stale ui/ copy after it);
//   3. <repo>/ui/ — today's home, the fallback until the move lands.
// The per-file log prints the ACTUAL resolved path, so which home a file came from is VISIBLE, not silent.
const DNA_REPO = process.env.DNA_REPO_DIR || '/home/tim/repos/counterpart/design'
const DNA_DIRS = [
  process.env.DNA_UI_DIR, // explicit override (legacy var / relocated checkout) — first
  join(DNA_REPO, 'surface', 'runtime'), // the reorg target (ui/ → surface/runtime/) — preferred
  join(DNA_REPO, 'ui'), // today's home — fallback until the move lands
].filter(Boolean)

// resolve a DNA source file across the candidate homes; returns the first existing path, or null (the
// caller FAILS LOUD — never a silent empty/stale gallery).
function resolveDna(file) {
  for (const dir of DNA_DIRS) {
    const p = join(dir, file)
    if (existsSync(p)) return p
  }
  return null
}

// the files the host needs to render the gallery face: DNA's organism generators (DNA.org.* — renderUnit
// calls DNA.org.hubNetwork for the unit→neighbour constellation; MUST load before unit-view.js), her renderer,
// and its look. organisms.js is a pure generator module (no global *-reset / body rule), safe to host whole.
const FILES = ['organisms.js', 'unit-view.js', 'phone.css']

const resolved = FILES.map((f) => ({ f, src: resolveDna(f) }))
const missing = resolved.filter((r) => !r.src)
if (missing.length) {
  // FAIL LOUD (no silent fallback) — a missing DNA source means the gallery face can't be hosted; say so,
  // and list every home we searched so the fix (checkout / DNA_REPO_DIR / DNA_UI_DIR) is obvious.
  console.error(
    `\n[sync-gallery] FAIL LOUD — DNA's render module file(s) not found in ANY known home:\n` +
      missing.map((r) => `  - ${r.f}`).join('\n') +
      `\nSearched (in priority order):\n` +
      DNA_DIRS.map((d) => `  · ${d}`).join('\n') +
      `\nThe gallery first-slice FACE is hosted FROM DNA's repo (she owns it; mid-reorg ui/ → surface/runtime/).\n` +
      `Fix: ensure counterpart/design is checked out, or set DNA_REPO_DIR (repo root) / DNA_UI_DIR (exact dir).\n`,
  )
  process.exit(1)
}

mkdirSync(PUBLIC_GALLERY, { recursive: true })
for (const { f, src } of resolved) {
  const dst = join(PUBLIC_GALLERY, f)
  copyFileSync(src, dst)
  console.log(`[sync-gallery] ${f}  (${statSync(src).size}B)  ← ${src}`)
}

// DNA's TOKEN VOCABULARY (:root --dna-space-*/--dna-radius-*/--warmpole-* etc.) lives in piece.css — but
// piece.css ALSO carries a global `*{margin:0;padding:0}` reset + a `body{display:flex;background}` rule that
// would WRECK the host surface if loaded whole. phone.css's values are token-based, so without these tokens
// every padding/radius collapses (DNA's diagnosis: .uv-chips render run-together). So we EXTRACT ONLY the
// :root token blocks into a standalone dna-tokens.css — the tokens phone.css needs, none of the dangerous
// globals. FAIL LOUD if piece.css or its :root is absent (the face's look depends on these tokens).
const PIECE = resolveDna('piece.css') // same prioritised homes (piece.css also moves ui/ → surface/runtime/)
if (!PIECE) {
  console.error(`\n[sync-gallery] FAIL LOUD — DNA's token source piece.css not found in ANY known home:\n` +
    DNA_DIRS.map((d) => `  · ${join(d, 'piece.css')}`).join('\n') + `\n` +
    `phone.css is token-based; without :root tokens the face's spacing/radius/warmth collapse.\n`)
  process.exit(1)
}
const pieceCss = readFileSync(PIECE, 'utf8')
// :root blocks are flat var-declaration lists (no nested braces) → a non-greedy {…} match is exact.
const rootBlocks = pieceCss.match(/:root\s*\{[^}]*\}/g)
if (!rootBlocks || !rootBlocks.length) {
  console.error(`\n[sync-gallery] FAIL LOUD — no :root token block found in ${PIECE} (DNA restructured?).\n` +
    `The gallery face's tokens cannot be hosted; aborting rather than serving a token-starved render.\n`)
  process.exit(1)
}
const tokensCss =
  `/* GENERATED by scripts/sync-gallery.mjs — DNA's :root token vocabulary EXTRACTED from piece.css.\n` +
  `   ONLY the :root blocks (no piece.css global *-reset / body rule, which would wreck the host surface).\n` +
  `   phone.css is token-based; these make its spacing/radius/warmth resolve in the host. DNA owns the source. */\n` +
  rootBlocks.join('\n\n') + '\n'
writeFileSync(join(PUBLIC_GALLERY, 'dna-tokens.css'), tokensCss)
console.log(`[sync-gallery] dna-tokens.css  (${rootBlocks.length} :root block(s), ${tokensCss.length}B)  ← extracted from piece.css`)

// THE FABRIC HOOKS (fork's loadable-brain wire + wildcard's interaction binder). Same copy-on-build
// discipline as DNA's module, but the registry-of-truth is the COMPANY repo (build-prep/front-interface/),
// NOT DNA's repo — fork (ch-8djrpmsl) + wildcard (ch-piffgfxv) own them. They are self-wiring classic-script
// IIFEs: loaded as <script> in index.html, they register their gallery:rendered / gallery:direction listeners
// before any user drill. Copied fresh each dev/build (so an owner's edit is picked up); FAIL LOUD if absent.
const HOOKS_DIR = process.env.FRONT_INTERFACE_DIR ||
  join(HERE, '..', '..', '..', 'build-prep', 'front-interface')
// fork-brain-core.js (the ONE brain-turn engine) must load BEFORE any mount; fork-v-brain.js is the V/RHM
// every-page brain mount the overlay host attaches; fork-gallery-brain-hooks.js is the per-unit mount (both
// now ride the core). wildcard's binder is the interaction wire.
const HOOK_FILES = ['wildcard-gallery-binder.js', 'fork-brain-core.js', 'fork-v-brain.js', 'fork-gallery-brain-hooks.js']
const missingHooks = HOOK_FILES.filter((f) => !existsSync(join(HOOKS_DIR, f)))
if (missingHooks.length) {
  console.error(
    `\n[sync-gallery] FAIL LOUD — fabric gallery hooks missing at ${HOOKS_DIR}:\n` +
      missingHooks.map((f) => `  - ${f}`).join('\n') +
      `\nThese are the loadable-brain (fork) + interaction (wildcard) wires the gallery face needs.\n` +
      `Fix: ensure build-prep/front-interface/ is present, or set FRONT_INTERFACE_DIR to its path.\n`,
  )
  process.exit(1)
}
for (const f of HOOK_FILES) {
  const src = join(HOOKS_DIR, f)
  copyFileSync(src, join(PUBLIC_GALLERY, f))
  console.log(`[sync-gallery] ${f}  (${statSync(src).size}B)  ← ${src}`)
}

console.log(`[sync-gallery] hosted DNA's gallery face + fabric hooks at public/gallery/ (owners hold the sources; these are fresh copies).`)
