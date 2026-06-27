---
type: terrain-entry
name: company
register: descriptive
aliases: ["company"]
path: /home/tim/company
relation: company
kind:
status: unconfirmed
created: 2026-05-27
last_active: 2026-06-26
size: 5.6G
coverage: { files_read: 1, files_total: many, last_read: 2026-06-26 }
git_remote: git@github.com:Concept-Vi/the-company.git
purpose: the Company spine — composition engine + decisions/flows/runtime/RHM + MCP face
contains: ["[[foundation]]", "[[company-cli]]"]
launched-by: ["[[company-systemd]]"]
relates-to: ["[[corpora]]", "[[cache-company]]", "[[recollection]]", "[[dot-recollection]]", "[[dot-vi]]", "[[config-company]]"]
secrets: false
move_intent: none
tags: [fabric, mcp, control]
---

# company

## What it is
The `~/company` folder itself — the Company spine. Plain-meaning: this is the one entity everything else in this ledger either IS-but-lives-outside, connects to, or is a candidate to join. It is a typed compositional dataflow system (code + AI nodes wired by structured-output contracts) plus its decisions/flows/runtime/RHM layers and an MCP face.

Evidence (Observed): `git remote -v` → `git@github.com:Concept-Vi/the-company.git` (remote `Concept-Vi/the-company`). `du -sh` = 5.6G. Most recent commit `2026-06-26 15:29:05 +1000`. Top-level shows the engine's registry-folders (`decisions`, `flows`, `contexts`, `contracts`, `bindings`, `dials`, `axes`, `kinds`, `lifters`, `minds`, `nodes`, `runtime`, `mcp_face`, `canvas`, `design`, `fabric`, `channels`, `foundation`, …) alongside handoff/state markdown (`STATE.md`, `MAP.md`, `HANDOFF.md`, `AGENTS.md`).

## How it works
Per design intent (E1–E6 composition engine + first self-purpose). This entry is deliberately HIGH-LEVEL: per `orienteering/CLAUDE.md`, the Company's internals get their own dedicated future pass. The property system here will hold whatever hierarchy that pass needs. Running pieces that live OUTSIDE the folder (services, venvs, caches, config) are catalogued as their own `external` entries — see connects_to.

## What it connects to
Everything in this ledger orbits this folder. Directly:
- `[[foundation]]` — now lives INSIDE at `/home/tim/company/foundation` (moved in 2026-06-26).
- `[[corpora]]` (source library), `[[cache-company]]` (its vector index) — the session-recall substrate.
- `[[recollection]]` + `[[dot-recollection]]` — recall tool + its data; `dot-recollection/self/` is written by code in `company/ops/`.
- `[[company-systemd]]` — the ~20 user services that boot/run it; source copies at `/home/tim/company/ops/systemd/`.
- `[[config-company]]` (TLS), `[[dot-vi]]` (cross-session frame that names the Company as the substrate layer).

## When / where
Created 2026-05-27 (earliest founding-conversation evidence, mirrored in `foundation/exchanges/01-questions.md`). Last active 2026-06-26 (latest commit). Path `/home/tim/company`, 5.6G. File count not enumerated — out of scope for this high-level entry.

## Notes / evidence
Read: top-level `ls`, `git remote -v`, `git log -1`, `du -sh`. NOT read: the folder's internals (by design — a separate pass owns them). The 5.6G figure is `du`-measured; the README/INDEX brief quoted 5.7G — within rounding of the same tree.
