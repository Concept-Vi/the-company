# AREA 1 — Guided show-me walkthrough + comprehension-at-altitude

> Make-up companion, authored by the lead from bounded direct reads + the 5 sibling companions (the prior
> two agent runs overflowed on the vault docs). Scope: the unique slice the siblings left — the
> comprehension-at-the-user's-altitude depth + the show-me state. Evidence: Observed(file:line)/Inferred/
> Anchor-idea. Cross-refs AREA-2/3/5/6.

## 1 · Comprehension-at-altitude — the path BIFURCATES (the A5↔A6 tension resolved)

**Observed (`suite.py:2213` `address_help`):** the "what can I do / what is this here" resolver joins THREE
legs at a `ui://` address — `what_this_is` (`_describe_ui_address`: the registry row's title / `represents`
feature-id, returns **"(unregistered)"** when unknown), `how_to_change` (`resolve_scope` + `blast_radius`:
the code scope + what a change touches), `how_to_use` (authored howto text, `None` if unauthored). It
degrades clean per leg; a malformed address raises the S0 gate.

**Observed (`suite.py:2102-2120`, in `_chat_context`):** when the chat focus carries a `mockup://<file>`,
the RHM context gets a `MOCKUP UNDER REVIEW` block with the mockup's **raw HTML injected** (path-safe,
**`CAP = 14000` chars**), explicitly told "the operator does not read code — read this FOR them and explain
at a plain-language altitude what this screen IS."

**The reconciliation (Inferred, decisive):** comprehension runs on **two different paths**:
- **Registered live elements** → `address_help` (the 3 legs, grounded in the registry). Solid.
- **Proposed mockup screens** (the redesign corpus — NOT in the live registry) → `address_help` returns
  "(unregistered)" + empty legs, so it **cannot** explain them; the **`mockup://` HTML injection** is the
  only path that can. So the very screens the studio exists to review are comprehended *only* via the raw-HTML
  injection — and that path carries the risk (below).

This is the literal root of the original failure: the detached studio gave the user a mockup with **neither**
path active (no RHM focus → no HTML injection; unregistered → no address_help) → he saw a screen with no
explanation. The fix is structural: the guided surface must put the mockup into RHM focus at every stop so the
HTML-injection comprehension path is always live.

## 2 · The risks on the mockup comprehension path (Inferred — verify live)

- **The 14KB cap truncates real mockups.** The corpus mockups (IA-desktop, the elevated views) exceed 14000
  chars; a truncated mockup → a partial explanation. Either raise/relax the cap, or pre-digest the mockup
  (extract structure/sections) rather than inject raw HTML. **Net-new refinement.**
- **4B explanation quality is UNVERIFIED.** Whether the resident Qwen3.5-4B actually produces a *good*
  plain-language "what you're looking at" from raw mockup HTML is the single most central unproven claim
  (A5 flagged this; the bridge/model were down for it). **Must verify live** (one chat call with a mockup
  focus) before trusting the comprehension story.
- **`up_translate` (`suite.py:5856`) is the present-at-altitude layer** — A6 flagged the altitude organ
  (`coa`) as possibly unwired. Confirm the explanation actually passes through altitude-shaping, not just
  raw model output.

## 3 · The show-me state (cross-ref AREA-3/5 — confirmed, with the one new gap)

- **The walkthrough/guide ENGINE is built and view-driving** (AREA-3/5 Observed: `start_guide` /
  `start_walkthrough` / `present_current` / `next`; `_registry_ui_target` + the FE `resolveUiTarget` move/
  spotlight the surface to a stop). So "the RHM drives the view stop-by-stop, next/back" is **largely built**
  — better than the anchor feared.
- **NEW GAP (decisive for the studio):** `present_current` **RAISES on an unregistered address** (AREA-2
  Observed). The redesign mockups are unregistered → **the built guided tour cannot tour the proposed
  mockups** without either (a) the engine tolerating unregistered/`mockup://` stops, or (b) lightweight
  per-mockup registration. This connects directly to A5's make-or-break: the guided experience's engine works
  for the live app but **not for the mockup corpus the studio reviews.** Net-new: a mockup-aware guided stop.
- **The FE show-me lane is deferred** (AREA-3/5): the user doesn't yet *see himself* walked through (the
  view-driving exists backend-side; the front-end guided overlay / next-back-dwell controls are unbuilt).
  Net-new FE.
- **"Narrate each stop at altitude"** = at each stop, run the comprehension path (§1) + `up_translate`. The
  pieces exist; the *loop* (advance → narrate → await next) is the net-new join (mirrors A2's "compose
  walkthrough↔chat" + A4's accumulate-layer).

## 4 · Contradiction of the anchor

The anchor framed *comprehension* as the make-or-break. Corrected: registered-element comprehension is solid;
mockup comprehension has a working mechanism (HTML injection) with **two real risks** (the cap + unverified
4B quality) AND a **structural blocker** the anchor missed — the guided ENGINE raises on the unregistered
mockup addresses it would tour. So the make-or-break for the *guided* experience specifically is **"can the
built tour engine + comprehension run on the unregistered mockup corpus"** — which, with A5's "generate
doesn't edit mockups," makes **the mockups (not the live app) the consistent frontier across the whole wave.**

## 5 · Honest status of THIS slice
- **Observed-built:** address_help 3-leg resolver; mockup:// HTML-injection comprehension; the walkthrough/
  guide view-driving engine; ui_target spotlighting.
- **Net-new:** mockup-aware guided stops (engine tolerates unregistered/`mockup://`); the FE show-me lane;
  the advance→narrate→next loop; cap/pre-digest refinement.
- **Unverified (live test needed):** 4B explanation quality from mockup HTML; up_translate/altitude wiring.
