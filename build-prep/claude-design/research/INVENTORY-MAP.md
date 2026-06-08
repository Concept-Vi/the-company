# Layer 1 consolidated — the terrain + the Layer 2 deep-read plan (2026-06-08)

> Merges the five Haiku coverage reports (`research/inventory/inv-{A..E}.md`). The application is large
> but **coherent and self-describing** — which is the best possible news for making it visible to Claude
> Design. Below: the terrain at a glance, the angle map, and the proposed smart deep-read clusters
> (Layer 2), prioritised by what the application-structure pack actually needs. For Tim to steer before
> the expensive layer fires.

## The terrain (≈600 source files, coherent)

| Region | Files | The spine (what matters for the pack) |
|---|---|---|
| **Backend core** (runtime/store/fabric/contracts) | ~75 | `suite.py` (the heart — chat, annotate, address_help, resolve_scope, up_translate, ui_target), `bridge.py` (API+SSE), `fs_store.py` (addressable, locked), `contracts/address.py` (the `run://`·`cas://`·`ui://` grammar), governance, registry, fabric guards |
| **FE + design** (canvas/design/panels) | 106 | F0-modular FE: `App.tsx`, `useAppController.ts`, `api.ts`, 19 `regions/`, `kit.tsx`, `NodeShape`; design substrate: `tokens.json`, `addresses.json`, `blueprint`, `register.json`; structural tools: `check.py`(lint)/`refcheck`/`symbols`/`codeedges` |
| **nodes/roles/voice** | 68 | 19 node-types (7 live), 9 cognition roles, MCP face, voice stack — all self-registering by file presence |
| **self-desc/tests/ops** | ~185 | 16 modules each with `AGENTS.md` (no orphans), `MAP.md`+`STATE.md`, **130 acceptance suites**, drift-check that fails loud, ops command-center (`services.json`, `company` CLI, `gpu.py`, `capabilities.py`) |

**Two facts that make this tractable for Claude Design:** (1) it **self-describes** — 16 AGENTS.md + MAP + STATE + a drift-check that fails if a capability lacks a suite or a module lacks a constitution; (2) it's **registry-not-hardcoding** + **schema-additive** everywhere. The structure is already disciplined; my job is to surface it as the thing Claude Design designs into.

## The angle map (where things live — the "many angles")

```
main ─────────── the built application (backend spine, FE, the address/organ system, ops)
│
├ concurrent-cognition ── BUILT cognition organ (~74 files); the live merge counterpart
├ interactive-surface-build ── Operable Composition Surface, X1–X17 staged
├ operable-interface-build ── THIS worktree: the visual redesign + studio mockups + the prep
├ night-build / overnight-20260605 ── older streams (mostly folded)
│
└ THE VAULT build-prep (252 files) ── the DESIGN INTENT narrative, three triads + the
     "Sequences as universal substrate" primitive + the "Composable Concurrency Surface"
```
The design intent is disproportionately in the **vault** (252 files) — the angle a shallow pass misses.

## Layer 2 — proposed deep-read clusters (smart models, keyed off the priority flags)

Prioritised by what the **application-structure pack** needs (the structure Claude Design designs into).

**MUST-HAVE (the pack's core):**
1. **FE structure + conventions** (Sonnet) — `App.tsx`, `useAppController.ts`, `api.ts`, the 19 regions, `kit.tsx`, `NodeShape`, `canvas/AGENTS.md`. → surface skeletons + component contracts + the FE where-things-go (layers ①②⑤). *The keystone's FE half.*
2. **The address/organ seams** (Sonnet) — `suite.py` (chat/annotate/address_help/resolve_scope/up_translate/ui_target), `bridge.py` API+SSE, `contracts/address.py`. → the integration seams (layer ③). *Overlaps cognition's seam-pack ownership — coordinate.*
3. **Design substrate + token-slots** (Sonnet) — `tokens.json`, `addresses.json`, `register.json`, `blueprint`, `design/conventions.md`+`CLAUDE.md`, the structural tools. → the token-slot contract + addressability + where-design-goes (layer ④, structure only — not aesthetic).
4. **The surface design-intent** (Opus) — the vault triad **Interactive Addressed Surface** (the studio's spec) + the IA proposal + the per-surface mockups. → the per-surface skeletons + intent (the §3E pack at full scope). *Large; scope to surface-relevant docs.*

**CONTEXT (informs the pack, lighter):**
5. **Contracts + registry + governance** (Sonnet) — `contracts/` C1–C8, `registry.py`, `governance.py`, `implement.py`/the wire. → how types/UI-components register + the act/governance seams (I4, L1).
6. **Self-description + ops shape** (Sonnet) — the 16 AGENTS.md, the 130-suite grouping, the ops command-center. → the conventions/laws (layer ⑤) + the real operational structure.
7. **The angles/merge delta** (Sonnet) — the `concurrent-cognition` delta + the X1–X17 chain + the other branches. → so the pack accounts for in-flight + divergent structure. *Coordinate with the merge.*

**LOWER (probably not needed for the pack now):** voice internals, the node-type skeletons — inventoried, deep-read only if a surface needs them.

## Coverage guarantee
Every PRIORITY-flagged place from Layer 1 maps to a cluster above (1–7) or the explicit "lower" defer.
Layer 3 (Opus synthesis) runs a completeness critic — "what place/angle/claim did we not cover?" —
and tops up if not dry. The vault's 252 files are the main volume risk → cluster 4 scopes to the
surface/interface/address docs, not the whole narrative, and the critic flags anything left.
