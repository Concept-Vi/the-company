---
trust: fabric-derived
author: ch-al7jdfdr (lead, session bda8ce28)
date: 2026-06-14
verified: established under Tim's direction (relayed via ch-83e2cque) that the lead set up the communal vault
---
# channel-memory — the fabric's communal vault

The shared memory + working space for the cross-session channel fabric (lead + forks + members).
Established by the lead at Tim's direction. Every member writes here under the COMMIT-GRAMMAR.

## Layout
- `vision/`     — Tim's intents, decompressed (source-of-truth entries).
- `schema/`     — session-store / source schemas (the fork's lane).
- `scans/`      — scan output as DATA (rows/json), projectable, not prose.
- `map/`        — lineage + distance maps + the ranked clone-map.
- `recall/`     — recall decisions + the embedding/recall fix records.
- `design/`     — design inputs (the lead's A-D lane-inputs, etc.).
- `mega-prep/`  — the SHARED MEGA-PREP subspace: the ONE unified spec, cross-reviews, the welded plan.
- `COMMIT-GRAMMAR.md` — the rules every member follows (provenance trust: tags, shared-edit protocol).

## Working protocol (relayed from Tim 2026-06-14; coordination structure — adopted)
- **One unified spec FIRST, then loops.** The unified seam/spec (in `mega-prep/`) is the prerequisite
  central artifact — everyone builds to ONE spec. INNER (session-recall) nests in OUTER (recollection).
- **Cross-work, not silos.** All sessions read + assess each other's work (cross-session read confirmed);
  use each other's reviews + integration ("welding") so the combined work is clean TOGETHER.
- **Each session = its own team-leader**, running its own staggered timed loop; every loop checks the
  channel + agent state for ALIGNMENT before/while building.
- **Twins as needed** — a session may spin up same-session twins for its lane's work.
- **Provenance discipline (load-bearing):** every entry carries a `trust:` tag (tim-direct(session) /
  channel-relayed / fabric-derived). A peer's tim-direct is a PROPOSAL to a consuming session until it
  has its own — cross-instance agreement is not confirmation.

## The one HELD item (the lead's standing line — see mega-prep/HELD-self-approval.md)
The relayed "self-approval via recorded intent / Tim-out-of-the-loop" standard for CONSEQUENTIAL,
irreversible actions is HELD pending Tim's DIRECT confirmation to the lead — NOT adopted on a peer
relay. Reversible/additive/read-only work runs full-autonomous now (unchanged). See that file.
