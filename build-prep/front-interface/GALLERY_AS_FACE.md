# THE GALLERY IS THE FACE — the interface plan (Tim 2026-06-16)

*Tim's direction: the interface (the face) is designed INTO DNA's gallery. The gallery already holds the real look/feel; it needs a bit more attention + the interaction layer, then the interface is designed into its FORMAT. First real use of the ollama-clone + local-scan capability. Provisional — DNA owns the gallery + confirms/corrects specifics; nothing built on assumption. The face needs to be FOR the face.*

## THE FRAME
- **The Gallery (DNA) IS the interface surface — the FACE.** The look/feel is DNA's, full stop (the company mockups' frontend is throwaway; only the mockup-system's architecture + address-systems are kept underneath).
- **It's close — not many upgrades.** The interface mockups can be DESIGNED IN the gallery without building everything first.
- **Gallery state (Tim, DNA confirms):** already has a MOBILE version · NO desktop yet (can be added) · ★ a SLIDE-FORM exists — the mobile UI mockups in slides — and those are **the only versions Tim really liked the look of** (the target look). + an ALMANAC (content) + more.
- **The gallery + its CONTENT both need attention** — the gallery interface AND what's in the galleries.

## STEP 1 — FULL PICTURE (the deep look-through; FINDING, first real capability-use)
Get everything about the gallery on the table, into the channel:
- **DNA — launch KIMI ERA-CLONES of yourself** (the new ollama-clone capability — `clone_at(provider='ollama', model='kimi-k2.7-code:cloud')`) to do a LARGE look-through of: the SLIDE-FORM mobile UI mockups (the liked look — find it + all about it), the ALMANAC content, and everything else in the gallery → a FULL PICTURE posted to the channel. (Or a local-concurrent `mcp__company__ingest` dir-scan of the gallery repo — free, whole-dir. Either/both.) Clone-boots are lead-sequenced (cloud kimi = no local-GPU contention). VERIFY the capability with ONE live boot first (fork's proof), then scale.
- **wildcard — ✅ DONE (GPU-free, by reading — no clone needed, litellm-lesson applied):** the interaction layer is ALREADY a closed typed contract in `contracts/taxonomies.json` — 4 categories (comment·reaction·highlight·favour) · 5 reaction stamps (good·wrong·explain·remember_this·do_this) · 10 comment types · 3 navigation · the response-envelope `{element_id, category, type, text, reaction, favour}` write-back contract. Binding pattern = `makeAnnotatable(element)` (one element-walker serves ANY rendered surface — F13c). ★ So the gallery does NOT build an interaction system — it INHERITS one by being WALKED. Tim's real use (snapshot data): make comment(direction/question/correction) + reaction(good/wrong) + favour + highlight prominent = ~all of it. (F15.)

## STEP 2 — UPGRADE THE GALLERY (light; DNA-owned, after the picture)
- Add a **DESKTOP** form (it has mobile + the slide-form).
- **The gallery INHERITS the interaction system by being WALKED** (DE-SCOPED, wildcard F15): not a build — run `makeAnnotatable` over the rendered gallery elements + use the `taxonomies.json` vocabulary + the response-envelope write-back. The interaction layer is portable/built; the gallery just gets walked. (Make comment/reaction/favour/highlight prominent.)
- Write a **"HOW TO ADD THINGS INTO THE GALLERY"** guide → channel content (so the whole fabric can put designs into the gallery).

## STEP 3 — DESIGN THE INTERFACE INTO THE GALLERY FORMAT (the face, for the face)
Once the full picture + the interaction layer are on the table, everyone lays out everything → the interface is designed into the gallery's FORMAT (DNA's layout-archetypes/tokens/the slide-form look) so it can be put IN the gallery. The face built for the face — on-principle, in DNA's real look, with the company architecture/address-system underneath.

## SEAMS (each member's part; meet at the address)
- **DNA** — owns the gallery + its look/content; runs the deep-look clones; the desktop form; the how-to-add guide; the gallery as the render format.
- **wildcard** — the interaction/annotation ways → the gallery's interaction layer (clones or a workflow).
- **fork** — the loadable-brain at element-addresses (so a gallery element is clickable→talk-to-CC) + the live clone-on-kimi proof first.
- **projection** — the Instrument as the field you zoom out to; drill into a unit → the gallery render.
- **composition** — the resolver feeds the gallery render; slots/sockets as the gallery's data substrate (its catalog).
- **recollection** — the index/recall under it (continues its pilot in parallel — cloud-clone deep-look ≠ local-card pilot, no conflict).

## DISCIPLINE
- Company mockups' visual frontend = throwaway, don't even look; architecture+address-system = kept underneath; the LOOK = DNA's gallery entirely.
- Investigate the actual gallery code before upgrading (the litellm lesson).
- Clone-boots: lead-sequenced (resource awareness); cloud kimi = no local-GPU load (parallel-safe with recollection's local pilot); local-model scans GPU-sequence with the steward.
- Verify-by-use before scaling (one live kimi-clone boot proven before DNA launches several).
- The face needs to be FOR the face — on-principle, the real look, not a quick throwaway.
