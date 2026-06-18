# DECISION CARD — HOST INTEGRATION CONTRACT (for DNA's render)

The flagship prove-on-one is one render away: every non-visual leg is built + verified across all streams;
the last mile is DNA's decision-card render. This is the consolidated checklist of **exactly what the card
must emit/do to plug into the live machinery** — each seam with the SILENT-FAILURE if it's missed (these are
the union-seam traps the session's work guards against) and projection's VERIFIED status. Built so the card
plugs in cleanly in ONE pass. (Companion to DECISION-SURFACE-BUILD.md, which is the vision/build-order.)

The chain, once the card renders: `decision:// resolve → DNA renders the variant → host opens → in-card Ask
+ pre-filled explanation → operator picks an option → take writes → state flips → host re-renders decided`.

## What the card MUST do (each = a seam; the silent-failure if missed)

1. **RENDER FROM the resolved decision** — fetch/receive `/api/territory?address=decision://<frame>/<id>` →
   `{id, meaning, options:[{label, implication?, description?, recommended?}], explanation_source, scope,
   legibility:{name,is,why}}` + composed `{state, decided_value, decided_by, decided_at}` (+ `subtype` once
   composition lands it). Render the variant by `subtype` (registry-true) and `render_kind`.
   ✅ projection-verified: /api/territory returns this exact shape on the bootstrap row.
   ⚠ if you render from anything but the resolved row → drift from the registry-is-truth source.

2. **MOUNT through the host** — render INTO `#gallery-mount` via `window.DNA.renderGallery(addr,{container})`.
   ✅ projection-verified: GalleryMount hosts it; the host is VARIANT-AGNOSTIC (any variant plugs in, zero host change).

3. **EMIT `decision:rendered`** after mounting — `detail = { element:<the card ROOT node>, address:"decision://<frame>/<id>" }`.
   `address` = the BARE CANONICAL decision address (NOT a `#elem`); `element` = the node the Ask binds to.
   ✅ projection-verified: host OPENS + HOLDS (wheel-deselect can't kill the walk) on this; fork's HOOK 1b Ask mounts on `element`.
   ⚠ SILENT-FAILURE if missed: the host never opens (no decision-mode) AND no in-card Ask mounts. If `address`
   is wrong-keyed → host doesn't open. If `element` absent → no Ask.

4. **THE TAKE — stamp + wire the option control** — on each decide-control: `data-decision = the BARE CANONICAL
   decision://<frame>/<id>` (the decision's identity, NOT `#elem`); `onClick → window.galleryBinder.decide(<that
   canonical addr>, <the option LABEL>)`.
   ✅ projection-verified: decide() → gallery:verb → projection's dispatch → territory_write → state flips
   pending→decided (decided_value = the label); latest-take-wins.
   ⚠ SILENT-FAILURE guarded: wildcard's decide() now REFUSES a non-canonical address (fail-LOUD guard, TEST9) —
   a bad/`#elem` stamp SCREAMS at the emit point instead of the old silent "decided reads pending". Missing
   onClick = no take. value MUST be the option LABEL (= decided_value).

5. **THE ASK (interactive follow-up)** — AUTOMATIC, no DNA action beyond passing `element` in (3): fork's HOOK
   1b binds the same in-card Ask on `decision:rendered`, keyed to the decision's canonical address; talk()
   grounds on the decision (meaning/options/state). ✅ verified (composite). The pre-filled explanation slot
   (`resolve:explanation_source`) is the one-shot explanation; the Ask is the walk-through Q&A.

6. **THE REFRESH after a take** — AUTOMATIC: the take's write fires `gallery:rerender` → projection's host
   re-fires `decision:rendered` → your card re-renders with `state=decided`. ✅ projection-verified.
   REPLACEABLE: if you'd rather refresh IN PLACE (finer than the host's full re-mount), yours supersedes.

7. **THE WRITE-ERROR display — YOUR lane (the one seam projection can't cover)** — listen for
   `gallery:write-error{element_id}` matching the card → show a "couldn't save" state ON the card. The surface
   chrome (Notice z-50, V z-45) is COVERED by the card overlay (z-60), so projection can't surface it. ⚠ if
   missed: a failed take/annotation is silent to the operator (no-silent-failure violated).

## What's already done for you (zero DNA action)

Host (open/hold/advance/close, variant-agnostic, slide+sequence lifecycle) · the take dispatch · the
rerender refresh · the in-card Ask · the resolve (/api/territory) · the explain (forkBrainCore.talk) ·
wildcard's canonical guard. All composite-proven end-to-end both viewports on a throwaway decision.

## The whole loop, once your card lands

`render the variant → emit decision:rendered{element,address} → host opens + Ask mounts → operator reads the
explanation, asks follow-ups, picks an option → decide() → take writes → state flips → host re-renders
decided`. Ping projection (ch-projection) when the card renders → I run the real per-variant on-card
prove-on-one (390 then 1440) + the fresh-eyes stranger test, both viewports.

## ★ READY HARNESS — run the prove-on-one SAME-SECOND the card renders

`surface/app/scripts/prove-decision-harness.js` — a self-contained `proveDecision(addr, opts)` that drives
the FULL loop and asserts EVERY leg (resolve · host-open · in-card-ask · take-flips-state · rerender-refresh),
returning `{pass, mode, legs}`. Verified known-good (all 5 legs green, both viewports). The moment your card
renders a decision, run in the live surface (chrome-devtools/console):

```
await proveDecision('decision://global/<id>')                                  // SHOW legs — safe, no take
await proveDecision('decision://global/<THROWAWAY-id>', { decide: '<label>' })  // FULL loop incl. the take
```

It auto-detects REAL-CARD (your render mounted in #gallery-mount → asserts it) vs SYNTHETIC (drives a stub so
host+ask are exercised pre-card). ★ Pass `decide` ONLY on a throwaway — it flips real state; on a REAL
decision, run without `decide` and let the operator make the actual choice (that IS the prove-on-one). So the
seam is proven the instant your card paints, not hours later.
