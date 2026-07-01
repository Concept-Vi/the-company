export const meta = {
  name: 'ledger-interpret-wave',
  description: 'Opus interpretive pass over one ledger wave — one agent per batch reads original files in full and emits one neutral interpretive JSON per file (file-local; contribution-not-ranking). Agents never touch the DB.',
  phases: [{ title: 'Interpret', detail: 'one Opus agent per batch' }],
}
const WAVE = "build-prep/the-one-system/interpret/wave-005"   // EDIT per wave
const N = 40                                                   // EDIT per wave (batch count)
const ids = Array.from({ length: N }, (_, i) => String(i + 1).padStart(3, '0'))

const prompt = (id) => `You add the INTERPRETIVE layer for a ledger of code/design substrates. NEUTRAL, file-local, NO ranking.

Your batch: read /home/tim/company/${WAVE}/alloc/batch-${id}.json — a JSON array of {project, path, root}.
For EACH entry, ATOMICALLY (one file in → one file out, then next):
  1. Read the ORIGINAL file in full at <root>/<path>. If it's a generated/minified/oversized blob, say so briefly and keep it short.
  2. Write ONE JSON to /home/tim/company/${WAVE}/out/<project>/<path>.json (create parent dirs) with EXACTLY these keys:
     { "project","path","model":"opus",
       "what_it_does": "<plain factual: what THIS file does, as the content shows>",
       "observations": ["<notable things actually in this file>"],
       "standouts": ["<the few most signal things, or []>"],
       "conventions": ["<patterns it follows or breaks>"],
       "concerns": ["<file-local smells only; or []>"],
       "notes": "<one-line 'if briefing someone on this file' remark>",
       "questions": ["<unclear FROM THIS FILE ALONE, as questions; or []>"],
       "purpose_vs_actual": "<does stated purpose match what it does? or 'n/a'>",
       "apparent_themes": ["<themes/principles it embodies>"],
       "intention_signals": "<what it seems to be TRYING to do / the idea behind it — inferred>",
       "novelty": "<what's distinct/unusual here, or 'n/a'>",
       "contribution": "<NEUTRAL: what this file UNIQUELY brings that a fused system would KEEP. Fusion has no winner — describe the contribution, never rank.>",
       "summary_for_embedding": "<one dense factual sentence — 'what is this'>",
       "intention_for_embedding": "<one sentence — 'what was this for'>" }

RULES: Describe only what's in the file. NO cross-file claims (duplication/which-wins/clusters are computed later by query). NEVER use ranking words (canonical/basis/thin/better/winner) — only 'contributes'. Tight arrays. Valid JSON only.
Final message: 'interp ${id} — <count> files'.`

const res = await parallel(ids.map(id => () => agent(prompt(id), { label: `interp:${id}`, model: 'opus', phase: 'Interpret' })))
return { wave: WAVE, batches: N, agents_done: res.filter(Boolean).length }
