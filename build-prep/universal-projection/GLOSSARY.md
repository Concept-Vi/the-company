# Glossary — terms of the Universal Projection (the instrument)

*Living, provisional. Names the terms the instrument's docs reuse so they don't drift. Some entries are
Tim's broader framework still being formalized — flagged as such, never frozen into false precision.*

---

## "axis" / "axes" — ⚠ AN OVERLOADED TERM (read this before using it)

The word **axes** carries (at least) two distinct meanings in these docs. Be explicit about which you mean.

### Meaning A — the instrument's DRIVABLE axes (the local, concrete sense)
The dimensions the operator/agent can drive a projection along — what the pickers + query params expose:
- **angle** (`angle_from`) — which lens lays out the sectors (kind · a registry · a graph · directional edges).
- **radius** (`radius_from`) — what distance-from-centre means (time/age · structural tree-distance ·
  semantic cosine · separator lean · nucleation fit).
- **the SCALE axis** (`?rung=`) — unit items ↔ coarse theme/cluster centroids (the pyramid). "Zoom which
  rung RESOLVES."
- **the RESOLUTION axis** (`?dim=`, MRL) — truncate the read vectors to N dims before the cosine: a
  continuous coarse↔fine MEANING zoom, orthogonal to the rung (together "the 2-D scale: rung × dim").
- **the embedder LAYER** (`?emb=`) — which embedding the meaning is read through (the multi-layer model).
- **time** (`?at=`, the scrubber) · **the relative centre** (`?center=`) · **the two poles** (`?pole_a/_b=`).

These are the "axes" the instrument code + the embedder-pplx HOWTO mean by default.

### Meaning B — Tim's FOUR ROOT AXES (the broader framework — NOT yet formalized)
In Tim's broader architecture / system theory there are **four ROOT axes — "the axes of all axes" (master
axes)**. Their precise definitions are **still being walked down** (Tim, 2026-06-15) — do not pin them.

The crucial relationship: **the axes named in Meaning A (and the G17 family — hierarchy · type-graph ·
scale · sequence · temporal · semantic · structural) are almost certainly TYPES along those four root axes —
i.e. sub-types, not roots themselves.** Tim's feeling (explicitly held as a feeling, not a claim): there are
**probably ~four sub-types per root axis**. So the structure is roughly:

```
4 ROOT AXES  (the master "axes of all axes" — definitions pending)
   └─ each with ~4 sub-types   ← the axes WE list (scale, resolution, hierarchy, type-graph, sequence, …)
                                  are sub-types living UNDER the roots, not the roots.
```

**Why this matters / how to apply:** when these docs say "axis," they mean **Meaning A** (a drivable sub-type)
unless they say "root axis." Treat our axis list as **provisional sub-types of a four-root structure that is
still being defined** — never assert our list IS the axis taxonomy. This connects to **G17 — "the AXES family,
beyond temporal"** (`build-prep/cognition-self-improvement/SYSTEM-GAPS.md`), which is the grounded research
workflow that will help formalize the roots. (See also [[the-seed-geometric-substrate]] — the geometric SEED.)

*Status: Meaning A is built + verified. Meaning B is Tim's open framework — captured here so the term isn't
used loosely, to be refined when Tim's definitions of the four roots crystallize.*
