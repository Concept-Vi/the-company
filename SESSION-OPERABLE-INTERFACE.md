---
type: session-handoff
module: root
aliases: ["Operable Interface Session", "SESSION-OPERABLE-INTERFACE"]
tags: [company, session, interface, ui, ux, merge, unify, cross-session-awareness]
status: living
---

# SESSION — Operable Interface (the UI/UX build + merge + wide-unify)

> **Cross-session awareness doc.** Written 2026-06-07 so the parallel **concurrent-cognition**
> session (and any other) knows EXACTLY what this session built, what it is about to land on
> `main`, and WHICH regions of the shared hot files it touches — so when our two big bodies of
> work meet, the merge is mostly clean. This is the mirror of main's `HANDOFF*.md`. If this
> disagrees with `STATE.md` + the tests, those win — fix this.
>
> **Worktree:** `/home/tim/company-interface` · **branch:** `operable-interface-build` ·
> **bridge:** `:8771` (NOT the live `:8770`) · **vite:** `:5174`. We share ONE repo
> (`/home/tim/company/.git`); `main` is checked out in the **live `~/company`**.

---

## 1. Who I am / what this session is

The **operable interface** session: the Company's self-modifying, recognition-by-sight UI/UX —
built so the Commander operates and *reshapes* the system from inside it. 28 commits ahead of the
`c7ea69b05` merge-base, every criterion **verified BY USE** (both desktop 1440 + phone 390),
gaps logged in `.build/interface/GAPS-REGISTER.md`. The full record is `.build/interface/state.json`.

## 2. What I built (all verified by use, on `operable-interface-build`)

| Group | What it is | Key surface |
|---|---|---|
| **A / H** | The cockpit — Palette/Inspector/Grow/Activity/Fleet/Workshop/History/Versions/SelfChanges regions, all in one design language (kit + tokens), phone-parity, **consolidated Settings (A3) control-room** (5 sections: brain/modes/voice/roles/composition) | `canvas/app/src/regions/*`, `App.tsx`, `app.css`, kit |
| **B** | The **consent** model — offer-with-options (B1), on-screen interactive multi-option select≠approve (B2), configurable defer-to-inbox as a live revivable offer (B3) | `ProposeAffordance.tsx`, `Inbox.tsx`, suite verbs |
| **C** | The **show-me** bootstrap — model-free guided tour (C1), teach-to-self-modify (C2), spotlight/walkthrough organ (C3/C4) | `Walkthrough.tsx`, `.ui-spotlight` |
| **D** | The **altitude help** surface — address_help composed (what-this-is + how-to-change + how-to-use) behind a drill-down | `AddressHelp.tsx` |
| **E** | **Modes-as-context-resolution** — a mode-type's declarations DRIVE what context resolves; live off/suggest/auto autodetect toggle | `MODE_SPECS`/`resolution_spec_for` in suite.py |
| **F1** | The **altitude transformation layer** + **learning loop** — up-translate the system's reality to the Commander's level + drill-down to machinery; he shapes HOW things present FROM INSIDE (voice/typing) → it adapts + remembers | `coa`, `up_translate`, `set_presentation_pref`, `ShapeHow.tsx` |
| **G1/G3** | Corpus-true registry — every UI element registered, ref'd, resolves, has a how-to (zero-orphan gate) | `design/_system/*` |

## 3. ⚠️ MY TERRITORY in the shared HOT FILES — read this if you touch them

These three files are edited by BOTH this session and (per your landscape) the concurrent-cognition
session. Here is WHERE I am, so you can stay disjoint or anticipate the merge:

### `runtime/suite.py`
- **My new defs (24), mostly in the RHM-verb / altitude / R2-howto area:** `address_help`,
  `up_translate`, `coa` (framing), `start_guide`, `start_walkthrough`, `set_presentation_pref`,
  `presentation_pref_at`, `autodetect_mode`, `resolution_spec_for`, `get_submode`/`set_submode`,
  `defer_offer`, `revive_offer`, `_r2_howto_at`, `_r2_pref_at`, `_apply_presentation_pref`,
  `_validate_presentation_pref`, `_registry_howto_for`, `_guide_sequence`/`_guide_steps`,
  `_live_complete`, `_cfg_choice`, `_ok`, `to_text`.
- **`MODE_SPECS` / `MODES` / `MODE_DIRECTIVES`** are now derived from one source (`MODE_SPECS`),
  and a mode-type's declarations parameterise **`_resolve_context_at`** (E1).
- **`set_rhm_config`** `allowed` whitelist: I added `MODE_AUTODETECT`.
- 🔴 **COLLISION ZONE with cognition:** you plan to generalise **`ROLE_REGISTRY`** (~929),
  add `_run_swarm`/`chat_parts`/`THOUGHT_SHAPES`, edit **`chat()`** (~3172/3369), and promote
  injection in **`_chat_context`** (~1322) + **`_resolve_context_at`** (~1461). I ALSO edited
  `_chat_context` (a show-targets grounding fix, G-63) and `_resolve_context_at` (mode-driven
  resolution, E1). **`chat()` is doubly hot** — main's voice session already edited it (~3369,
  persona-prose expansion) and you'll edit it (~3172, role binding). Expect a real `chat()` /
  context-resolution reconcile. My edits are additive *around* the resolution call; yours change
  *what gets resolved/injected*. We should keep the resolution path ONE coherent function.

### `runtime/bridge.py`
- **My 7 new routes:** `/api/address-help`, `/api/defer-offer`, `/api/guide/start`,
  `/api/presentation-pref`, `/api/revive-offer`, `/api/up-translate`, `/api/walkthrough/start`.
  (All verified disjoint from main's 9 voice/settings routes.)
- 🔴 **COLLISION ZONE:** you'll add a **`cognition.*` SSE branch** to `/api/stream` + a cognition
  serializer (sibling of `build_object_info`). My routes don't touch `/api/stream`, but if your
  serializer or stream emitter refactors the shared emit path, flag it.

### `canvas/app/src/useAppController.ts`
- **My handlers (disjoint names):** `startGuide`, `mintBuildIntent`, `setPresentationPrefAt`,
  `steerProposal`, `deferProposal`, `reviveOffer`, `openSettings`, `loadSettingsData`, `setCfgSlot`,
  plus A3 settings state (`settingsTab`, `roles`, `modeRegistry`, `autodetect`, `compositionCfg`…).
- 🔴 **COLLISION ZONE:** you'll add a **`cognition.*` case to the `openStream` dispatch (~355–403)**.
  My branch touches `openStream` for guide/walkthrough events. The SSE dispatch switch is the shared
  spot — add your `cognition.*` case as a NEW branch, don't refactor the switch shape, and we merge clean.

### Lower-risk shared files
- `canvas/app/src/api.ts` — I only **append** client methods (disjoint from your cognition fetchers).
- `canvas/app/src/regions/NodeShape.tsx` — you'll add role/cognition states. I did NOT touch NodeShape
  (I work in the region panels, not the canvas shapes). **Clean for you.**
- `nodes/llm.py`, `runtime/scheduler.py`, `fabric/transport.py`, `fabric/vram.py` — **I do not touch
  any of these.** All yours, clean.

## 4. What I am about to do (the next stages — so you can time your own merge)

**Stage 1 — MERGE (Tim-sanctioned: land `operable-interface-build`'s work on `main`).**
Approach chosen for SAFETY given you're live in parallel: I merge **`main` INTO my branch** first
(in my isolated worktree — off the live system, off your base), resolve the 9 conflict files
(per `.build/interface/MERGE-PLAN.md`), then update `main` by **fast-forward** at the very end.
That means **`main` only ever sees the final, green, unified tree** — you are never stranded on a
broken base. The 9 reconcile files: `Settings.tsx` is the one real fold (main's S1/S3/S5 config
bench folds INTO my A3 control-room, nothing dropped); the other 8 are additive unions.

**Stage 2 — WIDE-UNIFY (agents liberally).** Bring main's voice/persona/settings UI under the same
tokens/registries/kit; register main's ~8 unregistered `ui://` elements; re-tokenise its literal-px
CSS; retire the scattered RhmChat config gear (A3 supersedes); resolve coherence decisions (the
indicate-on-click model, the `voiceStatus` shape, one home for conversation threads, one voice on/off).

**Stage 3 — verify by use both faces → WALKTHROUGH for Tim.**

**MERGE-ORDER COORDINATION (proposal):** I am merge-ready now (28 verified commits); you just
branched (0 commits). Cleanest is **I land on `main` first** (green, via the fast-forward above),
then you `git merge main` into `concurrent-cognition` ONCE to pick up the unified base — rather than
both of us absorbing each other's large diffs in a tangle later. If you'd rather land your cognition
spine first, tell me (via Tim or a note here) and I'll merge main into my branch after you. Either
way: **whoever lands second does one `git merge main`**, and the collision zones above (§3) are where
to look first. The `chat()` + `_resolve_context_at` reconcile is the one that needs a human-aware
merge, not a blind `-X`.

## 5. Pointers
- Merge reconciliation detail: `/home/tim/company-interface/.build/interface/MERGE-PLAN.md`
- RHM ability map: `/home/tim/company-interface/.build/interface/RHM-LANDSCAPE.md`
- Build log + every wave: `/home/tim/company-interface/.build/interface/state.json`
- Gaps found anywhere (incl. beyond UI): `/home/tim/company-interface/.build/interface/GAPS-REGISTER.md`

— the operable-interface session, 2026-06-07.
