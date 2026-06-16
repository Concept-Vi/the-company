// sync-gallery.mjs — the DOM-MOUNT SEAM's copy-on-build step (runs as predev + prebuild).
//
// The first-slice FACE is DNA's render module (ONE renderer, MANY sources). DNA OWNS it — it lives in
// DNA's repo (counterpart/design/ui/). The surface HOSTS it (so DNA's /api/cognition/corpus fetch is
// same-origin + fork/wildcard get stable element refs). To host without taking custody (no silent
// drift, no stale hand-copy), we COPY DNA's canonical files into public/gallery/ on every dev/build —
// fresh every time, identical in dev and prod, and FAIL LOUD if DNA's source is missing (never serve a
// silently-stale or absent module). DNA edits her source; the next dev/build picks it up. Registry-of-
// truth for the module = DNA's repo, not this copy.
import { existsSync, mkdirSync, copyFileSync, statSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const PUBLIC_GALLERY = join(HERE, '..', 'public', 'gallery')

// DNA's canonical source (env-overridable so a relocated checkout still resolves; default = the fleet path).
const DNA_UI = process.env.DNA_UI_DIR || '/home/tim/repos/counterpart/design/ui'

// the files the host needs to render the gallery face: DNA's renderer + its look.
const FILES = ['unit-view.js', 'phone.css']

const missing = FILES.filter((f) => !existsSync(join(DNA_UI, f)))
if (missing.length) {
  // FAIL LOUD (no silent fallback) — a missing DNA source means the gallery face can't be hosted; say so.
  console.error(
    `\n[sync-gallery] FAIL LOUD — DNA's render module is missing at ${DNA_UI}:\n` +
      missing.map((f) => `  - ${f}`).join('\n') +
      `\nThe gallery first-slice FACE is hosted FROM DNA's repo (she owns it).\n` +
      `Fix: ensure counterpart/design is checked out, or set DNA_UI_DIR to its ui/ path.\n`,
  )
  process.exit(1)
}

mkdirSync(PUBLIC_GALLERY, { recursive: true })
for (const f of FILES) {
  const src = join(DNA_UI, f)
  const dst = join(PUBLIC_GALLERY, f)
  copyFileSync(src, dst)
  console.log(`[sync-gallery] ${f}  (${statSync(src).size}B)  ← ${src}`)
}
console.log(`[sync-gallery] hosted DNA's gallery face at public/gallery/ (DNA owns the source; this is a fresh copy).`)
