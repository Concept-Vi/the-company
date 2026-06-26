# SPEC — "The One Wire": direction → generate (self-build surface, extension 1)

**Authors:** wildcard (ch-piffgfxv, direction-capture + retarget-by-address) ⊕ fork (ch-8djrpmsl, run_turn + territory_write) — fork to confirm/correct the fork-side pieces.
**Status:** SPEC ONLY — Tim steers whether/when it's built. Nothing built from this doc.
**What it is:** the single unbuilt rung between the live first-slice round-trip and Tim's full self-build surface. The pieces are built; this names the ONE join.

> **RECONCILED with composition's V VERB CONTRACT (ch-2mnxl9j0, 2026-06-17):** this wire IS the
> **MAKE** verb. composition owns the verb contract (6 polymorphic verbs over the aim's TYPE: ASK ·
> ANNOTATE · GO-TO · DRIVE · SOURCE · MAKE); this spec is MAKE's mechanism. NOT a parallel spec —
> MAKE = this direction→generate wire, governed by the verb contract. Key refinement composition
> adds (folded in below): MAKE is **aim-type-gated** — enabled only on a WRITABLE address
> (vi-vision asset / real data node), DISABLED on a synthetic `ui://`instrument-sector (you can't
> "make" a projection artifact). And ANNOTATE (the record half) is the already-live route-back; MAKE
> is its generative escalation. Verb order to build (composition's): GO-TO + SOURCE first (work on a
> sector aim today), DRIVE next, MAKE last (gated, needs the write path live). So this wire is the
> LAST verb to build, and only on writable aims.

---

## The mechanism Tim named
click an element → talk to the inbuilt brain → direct it at source → it **GENERATES/mutates** → written to an **addressed registry** → re-render. Retargetable at any addressed surface (gallery / DNA-system / mockup-content / composition factory) because the target is an address, not a hardcoded place.

## What is ALREADY BUILT (verified) — the wire joins these, doesn't make them
| Piece | Owner | State | Evidence |
|---|---|---|---|
| direction capture at an address | wildcard | use-verified (unit) | `wildcard-gallery-binder.js`: click → `gallery:direction {element_id=<address#elem>, type, annotation_type, text, reaction, score}`. `direction`/`do_this` are existing comment/reaction types (taxonomies.json). |
| retarget-by-address | wildcard | built-by-construction | element_id IS an address; route-out is an EVENT not a fixed target → any addressed surface works. |
| loadable brain | fork | built (default host-Claude) | `run_turn` (bridge `_claude_stream` / `POST /api/claude/turn`) — real CC subprocess, `--resume` continuity, address-context folds into the prompt. *(per fork's reports — fork confirm.)* |
| scheme-agnostic address→context | fork | built (g-1781604207) | `_claude_stream` composer now `territory_prose` (run://·code://·ui:// resolve, never raises). |
| write-to-addressed-registry | fork | built (g-1781604207) | `POST /api/territory/write` → `suite.mark` (3 mark_types round-trip, bad→400). |
| address resolver (read side) | composition/core | built | `resolve_address` (cognition.py, 16-scheme). |

## THE ONE NEW CONNECTION (all the wire is)
Today a `do_this`/`direction` item routes to `territory_write → suite.mark` = a **recorded** direction. The wire re-routes the *generative* items through the brain first:

```
gallery:direction { element_id=<address>, type, text }            ← BUILT (wildcard emit)
    │
    │  IF type/annotation_type ∈ {do_this, direction}  ← generate-intent (else: mark, as today)
    ▼
run_turn(                                                          ← BUILT (fork brain)
   context = territory_prose(element_id),   ← the address's resolved territory  ← BUILT
   instruction = item.text                  ← the direction text IS the instruction
)
    │  brain output (asset/content/mutation)
    ▼
POST /api/territory/write(address=element_id, payload=brain_output, kind=<generated|mutation>)  ← BUILT endpoint, NEW payload kind
    │
    ▼
re-render at address  → shimmer→solid (collapse)                   ← BUILT (re-render + render-state)
```

**The ONE new thing:** a router step — `if item is generative → run_turn → write the OUTPUT; else → mark (as today)`. Everything it calls already exists. It is a ~1-function join, not infrastructure.

**AIM-TYPE GATE (composition's verb contract — folded in):** before the router fires, check the aim's TYPE: MAKE is enabled ONLY when `element_id` resolves to a WRITABLE address (a `vi-vision://` asset or a real data node). On a synthetic `ui://`instrument-sector the MAKE path is DISABLED (you can't make a projection artifact) — ANNOTATE/ASK still work on it. So the router's first guard is `isWritable(resolve_address(element_id))`, not just `is generative`.

Sub-decisions RESOLVED by the lead (Entry 46) + composition (verb contract): (a) generate ALSO leaves a provenance mark (don't replace) ✅; (b) ASYNC — "generating…" shimmer→solid ✅; (c) START `do_this` only ✅. Composition adds: (d) MAKE gated on writable-aim-type ✅; (e) write is lead-governed, never brain-unilateral ✅. All five now resolved; the wire is fully specified, gated on Tim's build-go.

## Per-surface write-target (each an addressed registry; same wire, different address)
| Surface | Address scheme | Write-target registry | Note |
|---|---|---|---|
| gallery unit | `common_knowledge://` / `code://` | territory_write → corpus/registry at address | the first-slice surface |
| DNA-system | (DNA's) | DNA's `feedback_server` / addressed DNA registry | DNA confirms the scheme + target |
| mockup-content | mockup address | the mockup's addressed store | makes mockups self-editable |
| composition factory | `vi-vision://` | composition's slot/catalog registry | generate INTO the component registry |

The wire is identical for all; only `resolve_address(element_id)` differs. That IS Tim's universal composition — one mechanism, retargeted by address.

## VERIFY-BY-USE (the proof Tim's map wants — when/if built)
1. At a real address (e.g. a gallery `code://` unit), Tim adds a `do_this` direction: "summarize this file's exports as a card."
2. The wire fires: `run_turn(context=that address's territory, instruction="summarize…")`.
3. The brain output is WRITTEN to the registry AT that address (territory_write, kind=generated).
4. Re-render shows the new/changed asset at the address — collapse shimmer→solid.
5. PROOF = the registry CHANGED by Tim's directed generation (not a mark) + the surface reflects it. Retarget proof: same steps at a DNA-system address mutate the DNA registry.

## Ownership at the seam
- wildcard: the generative-item detection + emit shape (already carries type+text+address); the retarget-by-address property.
- fork: `run_turn` invocation + the territory_write payload-kind for generated output; the router placement (bridge-side, fork's file).
- DNA / composition: expose their surfaces as addressed write-targets (their registries) + emit `gallery:rendered` so the binder walks them.

**This is the keystone:** with this one router step, "Tim directs → the system builds itself at the address" is live, retargetable across every addressed surface. It is the shortest path from the round-trip to the self-build surface — and it is a JOIN of built pieces, gated on Tim's go.
