# TOKEN-HOMES — the three-way census (derived; rerun via this file's generator block in _system/substrate-map.py docs)
_generated 2026-07-12T21:33:56Z · spine=design/_system/tokens.json · ds=claude-ds tokens css · dna=counterpart vars/piece.css_

## Counts
- company spine: 84 emitted names · claude-ds css: 618 names · counterpart dna: 159 names
- spine∩ds shared names: 26 — 11 SAME value, 15 DIFFERENT value
- spine∩dna: 1 name (--line) · ds∩dna: 3 names (--body/--bronze/--gold) · zero shared hex either way — the DNA is a DISJOINT identity

## THE COLLISION SURFACE — same name, different value (load-order decides the look)
| token | spine | claude-ds |
|---|---|---|
| `--d-1` | `calc(4px * var(--density))` | `calc(4px  * var(--density))` |
| `--d-2` | `calc(8px * var(--density))` | `calc(8px  * var(--density))` |
| `--elev-1` | `0 1px 0 rgba(255,255,255,.02), 0 8px 24px -16px var(--shadow` | `0 1px 2px   color-mix(in srgb, var(--shadow-c) 8%,  transpar` |
| `--elev-2` | `0 1px 0 rgba(255,255,255,.03), 0 24px 60px -28px var(--shado` | `0 2px 6px   color-mix(in srgb, var(--shadow-c) 10%, transpar` |
| `--font-body` | `'IBM Plex Mono', ui-monospace, 'SF Mono', monospace` | `'DM Sans', ui-sans-serif, system-ui, sans-serif` |
| `--font-display` | `'Fraunces', Georgia, serif` | `'Sora', ui-sans-serif, system-ui, sans-serif` |
| `--font-mono` | `'IBM Plex Mono', ui-monospace, 'SF Mono', monospace` | `'JetBrains Mono', ui-monospace, 'SFMono-Regular', monospace` |
| `--fs-body` | `12px` | `clamp(14px, 0.86rem + 0.25vw, 16px)` |
| `--fs-display` | `19px` | `clamp(38px, 1.40rem + 6.00vw, 92px)` |
| `--fs-meta` | `10.5px` | `clamp(12px, 0.78rem + 0.15vw, 14px)` |
| `--fs-micro` | `8.5px` | `clamp(10px, 0.66rem + 0.12vw, 11px)` |
| `--lh-body` | `1.5` | `1.55` |
| `--lh-tight` | `1.3` | `1.04` |
| `--r-pill` | `99px` | `999px` |
| `--r-sm` | `5px` | `6px` |

## Shared names, same value (benign today, unguarded tomorrow)
`--control-h`, `--control-h-sm`, `--d-12`, `--d-3`, `--d-4`, `--d-6`, `--d-8`, `--density`, `--r-lg`, `--row-h`, `--touch-min`

## Reading
The font stack (--font-body/display/mono) and the whole type scale (--fs-*) DIVERGE between the spine and the DS.
Any page loading both chains inherits whichever wins the cascade — the look is load-order-dependent today.
The DNA (counterpart) is not a token-collision problem; it is a separate identity needing a declared relationship (board://item-62514a68).