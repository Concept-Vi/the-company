---
type: constitution
module: tests
aliases: ["tests — constitution"]
tags: [company, constitution, tests, proofs]
governs: []
relates-to: ["[[Company Map]]", "[[Company State]]", "[[Concepts and Principles]]"]
status: living
---

# tests/ — module constitution

**Is:** the acceptance suites — the **convergence record**. Each `tests/*.py` proves one capability by execution (`for t in tests/*.py; do ./.venv/bin/python "$t"; done`).
**Guarantees:** "done" is proven, not asserted — a capability isn't real until its suite is green; beyond tests, the standard is **prove by USE** — operate the live system, don't just assert.
**Where new things go:** a new capability = a new `tests/<name>_acceptance.py` that proves it; the live index of suites is [[Company State]] (auto-maintained — do not duplicate the list here).
**To extend:** add a suite that **fails before** the capability exists and **passes after** — it self-joins the run-all loop, so the proof and the run are never out of step.
**Seam:** exercises [[runtime — constitution]], [[nodes — constitution]], [[store — constitution]] etc. **through their real interfaces** — not against stand-ins.
**Never:** claim something works without a green suite or fresh use-evidence · let a suite drift from the capability it names · test against mocks where the real system can run.

## What's in here

The acceptance suites (`tests/*.py`) — one per capability, each a runnable proof rather than
a description of one. They are the **proof record**: a capability is real exactly when its
suite is green, and the system's own claims about what is built trace back here. The **live,
complete index of suites is the single source of truth** — the auto-maintained block in
[[Company State]] (do not duplicate it here; that's the rule in [[Vault Conventions]]). The
suites span the same arc the system does — engine, fabric, registries, the two faces +
governance, the first purpose, the interface, the RHM, self-modification — each capability
named by the suite that converges on it.

## Relates to

- **Proves the capabilities of** [[runtime — constitution]] (the scheduler + memo gate that
  actually runs), [[nodes — constitution]] (each node-type doing what it declares), and
  [[store — constitution]] (content-addressing + provenance hold) — by driving their **real
  interfaces**, end to end.
- **Guards the self-mod gates** — the build-gate, governance, and revertibility of
  self-modification each have a suite that holds the line; a regression there fails loud.
- **Indexed by** [[Company State]] — the convergence record lists every suite and the
  capability it proves, and a drift-check fails loud if a registered capability isn't backed
  by one.

## Read next
[[Company State]] (the live suite index + what each proves) · [[Company Map]] (the whole picture) · [[Concepts and Principles]] (why "prove by use" is the standard).
