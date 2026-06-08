# claude-design — reading order + doc ownership

## Canonical reading order

1. **`BACKEND-SEAM-PACK.md`** — start here. The one-source for the backend contract: all HTTP routes, the SSE event contract, the address + resolution substrate (`ui://` / `run://` / `code://`), the projections (registry-as-data), the 9 FE laws the interface must honor, and the FE placement map (where Claude Design output lands in the component tree). If a question concerns what the backend exposes, this doc answers it.

2. **`../concurrent-cognition/AUTHORING-FE-HANDOFF.md`** + **`AUTHORING-UI-BRIEF.md`** — the cognition authoring surface. The handoff owns the frontend component contracts and seam wiring for role/rule authoring. The brief is the full Claude-Design-ready brief: surfaces, backend contract, UX flow, design bar, laws, open questions. Read both before designing or building anything in the cognition authoring surface.

3. **`APPLICATION-STRUCTURE-PACK.md`** — this directory's keystone. Adds what the seam pack does not own: the FE-structure and design-into-it framing (§0 sockets-vs-plugs, Job A/B), the token-slot contract (§04), the surface layer (§03: IA skeleton, Sequences primitive, 17 surface skeletons, studio end-state spec), and the region recipe + studio per-surface brief (§05). Read after the seam pack, not instead of it.

---

## What each doc owns

| Doc | Owns | Does NOT own |
|-----|------|-------------|
| `BACKEND-SEAM-PACK.md` | HTTP routes, SSE contract, address substrate, projections, 9 FE laws, FE placement map | Token-slot contract, surface skeletons, region recipe |
| `AUTHORING-FE-HANDOFF.md` | Cognition authoring FE component contracts + seam wiring | Everything else |
| `AUTHORING-UI-BRIEF.md` | Cognition authoring Claude-Design brief (surfaces, UX, laws) | Everything else |
| `APPLICATION-STRUCTURE-PACK.md` | Framing, token-slot contract, surface layer, region recipe, studio brief | Backend contract (cross-refs seam pack); cognition authoring (cross-refs above two) |

---

## One-source note

**BACKEND-SEAM-PACK.md is canonical for the backend contract.** The structure pack cross-references it — it does not restate route tables, the SSE spec, the address substrate, or law text. If you find the same content in both docs, the seam pack is the source of truth.

**The division by session type:**
- Cognition session (backend + integration focus): `BACKEND-SEAM-PACK` + `AUTHORING-FE-HANDOFF` + `AUTHORING-UI-BRIEF`
- Interface session (FE structure + design-into-it focus): `APPLICATION-STRUCTURE-PACK` (which cross-refs the seam pack for layer ③ + ⑤)

---

## Evidence base

`research/` — the bounded-read corpus that produced the seam pack and structure pack. Contains:

- `deep/` — six deep-read distillations: `fe-structure.md`, `surface-intent.md`, `seams.md`, `contracts-governance.md`, `design-substrate.md`, `selfdesc-ops.md`, `angles-delta.md`
- `inventory/` — five inventory reads: `inv-A` through `inv-E`
- `INVENTORY-MAP.md`, `RESEARCH-METHOD.md`, `scout-studio-extract.md`

**`research/README.md`** notes where the seam pack supersedes the deep-reads' findings.

---

## Studio reconcile material

The two studio patches in this directory are the studio-reconcile material — applied during the interface session to wire the studio's real seams and align its structure to the kit primitives and token contract:

- `studio-fe-wiring.patch`
- `studio-suite-mockup-focus.patch`
