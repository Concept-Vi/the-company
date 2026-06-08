# Build Address Map — the coordinate system for the guided-review-surface unification

> Tim's method (2026-06-08): give ADDRESSES to the loop-prep docs + findings AND to AREAS of the
> directory (full coverage, areas-not-queries), then sweep the areas for everything that RELATES to the
> guided-review-surface — so the build loop is significant and unifies a whole lot at once. This map is
> that coordinate system + the anchor for the coverage rounds.
>
> **Dogfood note (a unification thread itself):** the live address grammar (`contracts/address.py`
> SCHEMES = run·cas·blob·vec·ui·code) has no scheme for DOCS or DIRECTORY-AREAS. Giving the build's own
> artefacts + the directory addresses is a proposed grammar extension (`doc://`, `area://`) — captured
> here as the working coordinate system AND flagged as a candidate unification (addresses-for-everything,
> the address system reaching its own build). Whether to formalize the schemes is a build decision.

## The artefact addresses (the build's own docs, now coordinates)
- `doc://grs/anchor`              → build-prep/guided-review-surface/ANCHOR.md
- `doc://grs/synthesis`           → build-prep/guided-review-surface/GUIDED-REVIEW-SURFACE.md (the grounded research)
- `doc://grs/criteria`            → build-prep/guided-review-surface/Completion Criteria.md
- `doc://grs/guide`               → build-prep/guided-review-surface/Implementation Guide.md
- `doc://grs/findings/area-1..6`  → build-prep/guided-review-surface/findings/AREA-{1..6}-*.md
- `doc://grs/address-map`         → this file

## The directory-area addresses (FULL coverage — every region a coordinate)
- `area://runtime`       → runtime/ (the RHM organ, the wire, the modes/dial, R2 context-resolution, governance, scheduler, cognition, activation, registry)
- `area://canvas`        → canvas/app/src/ (the whole front end — App, controller, api, regions, components, the studio Review surface)
- `area://substrate`     → contracts/ + store/ + fabric/ (the ui:///run:// address grammar, the registries, the resolver protocol, persistence, the model guards)
- `area://cognition`     → nodes/ + roles/ (node-types + the cognition roles/casts that fire in a mode)
- `area://voice`         → voice/ (STT/TTS, the voice circuit, the turn/stream routes — voice-in for the live dialogue)
- `area://design`        → design/ + panels/ (tokens, the design system, addresses.json, the mockup corpus + register, blueprint)
- `area://ops`           → ops/ + tests/ (the mode/resource manager, the CLI, capabilities, the gating acceptance suites)
- `area://design-corpus` → build-prep/ (repo) + the VAULT build-prep (the designed-but-maybe-unbuilt corpus — other surfaces/organs that relate or could unify)

## The coverage anchor (what each area sweep is FOR)
For its area, each round finds — by AREA, not by query, full coverage — everything that:
1. the guided-review-surface would **use** (a faculty/seam it composes — context-resolution, the organ, the wire, voice, the registry…),
2. it would **touch / be touched by** (a shared hot file, a contract it changes, a mode axis),
3. it could **UNIFY or improve** as it lands (a half-built thing, a duplicated pattern, a latent capability the surface would activate, an inconsistency it would resolve),
4. or that **relates conceptually** (the Sequences primitive, the addressed substrate, the cognition modes — the same shape recurring).
Anchored to `doc://grs/synthesis` + `doc://grs/criteria`. Findings APPEND to the criteria (never filter — Tim's grow-scope law). Companions land at `build-prep/guided-review-surface/findings/coverage/AREA-<name>.md`.
